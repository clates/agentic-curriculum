"""
agent.py

LLM-based agent for generating lesson plans using OpenAI API.
"""

import os
import sys
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from openai import OpenAI
from pydantic import ValidationError

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from db_utils import get_student_profile
from logic import get_filtered_standards
from resource_models import ResourceRequests
from worksheet_requests import build_worksheets_from_requests
from datetime import datetime, timedelta


# Maximum number of concurrent threads for generating daily lesson plans.
# Default is 5 (one per weekday). Raising this may reduce latency but
# increases OpenAI rate-limit pressure and local CPU usage.
MAX_DAILY_PLAN_THREADS = int(os.environ.get("MAX_DAILY_PLAN_THREADS", "5"))
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LLM_LOG_DIR = LOG_DIR / "llm_exchanges"

RESOURCE_GUIDANCE = """If a printable worksheet would measurably help the lesson, include a `resources` object.
- `mathWorksheet`: requires `problems` (array of {operand_one, operand_two, operator:+|-}) and optional `title`, `instructions`, `metadata`.
- `readingWorksheet`: requires `passage_title`, `passage`, and `questions` (prompt + optional response_lines). Optional `vocabulary`, `instructions`, `metadata`.
Only emit the worksheet fields you need. Omit the `resources` key entirely when no worksheet is needed.
"""

RESOURCE_FEW_SHOT = {
    "lesson_plan": {
        "objective": "Students practice repeated addition to prepare for multiplication.",
        "materials_needed": ["Counters", "Paper"],
        "procedure": [
            "Model repeated addition with counters.",
            "Have students solve two practice problems.",
            "Discuss how repeated addition relates to multiplication."
        ],
    },
    "resources": {
        "mathWorksheet": {
            "title": "Repeated Addition Warm-Up",
            "problems": [
                {"operand_one": 2, "operand_two": 2, "operator": "+"},
                {"operand_one": 3, "operand_two": 3, "operator": "+"}
            ]
        }
    }
}
RESOURCE_FEW_SHOT_JSON = json.dumps(RESOURCE_FEW_SHOT, indent=2)


def _slugify(value: str) -> str:
    if not value:
        return "entry"
    return re.sub(r"[^a-zA-Z0-9_-]", "_", value)


def _log_llm_exchange(
    phase: str,
    metadata: dict,
    request_payload: dict,
    response_payload: dict | None = None,
    error: str | None = None,
) -> None:
    """Persist the LLM request/response payloads under logs/llm_exchanges."""

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S_%f")
    label = metadata.get("day") or metadata.get("label") or phase
    filename = f"{timestamp}_{_slugify(label)}.json"
    phase_dir = LLM_LOG_DIR / phase
    phase_dir.mkdir(parents=True, exist_ok=True)
    logfile = phase_dir / filename

    log_payload = {
        "timestamp": timestamp,
        "phase": phase,
        "metadata": metadata,
        "request": request_payload,
    }
    if response_payload is not None:
        log_payload["response"] = response_payload
    if error is not None:
        log_payload["error"] = error

    with logfile.open("w", encoding="utf-8") as handle:
        json.dump(log_payload, handle, indent=2)


def create_lesson_plan_prompt(standard: dict, rules: dict) -> str:
    """
    Build the system prompt for the LLM to generate a lesson plan.
    
    Args:
        standard: Dictionary containing standard information (standard_id, subject, description, etc.)
        rules: Dictionary containing parent rules (allowed_materials, parent_notes, etc.)
        
    Returns:
        A string containing the formatted prompt for the LLM
    """
    # Extract allowed materials and parent notes from rules
    allowed_materials = rules.get('allowed_materials', [])
    # Default to keeping procedures under 3 steps if parent_notes not provided
    parent_notes = rules.get('parent_notes', 'keep procedures under 3 steps')
    
    # Build the prompt
    resource_guidance = f"""{RESOURCE_GUIDANCE}

Example (trim fields you do not need):
{RESOURCE_FEW_SHOT_JSON}
"""

    prompt = f"""You are an expert K-12 educator. Create a lesson plan for the following educational standard.

Standard: {standard.get('description', '')}
Subject: {standard.get('subject', '')}
Grade Level: {standard.get('grade_level', 0)}

Requirements:
1. Create a lesson_plan object with the following structure:
   - objective: A clear learning objective based on the standard
   - materials_needed: A list of materials (MUST only use items from: {allowed_materials})
   - procedure: Step-by-step instructions for teaching the lesson

2. Important constraints:
   - Materials MUST ONLY come from this list: {allowed_materials}
   - Follow this parent guidance: {parent_notes}
   - Keep the lesson age-appropriate for the grade level
   - The objective should directly address the standard

{resource_guidance}

Respond ONLY with valid JSON:
{{
    "lesson_plan": {{
        "objective": "Clear learning objective here",
        "materials_needed": ["Material1", "Material2"],
        "procedure": ["Step 1", "Step 2", "Step 3"]
    }},
    "resources": {{
        "mathWorksheet": {{ ... }},
        "readingWorksheet": {{ ... }}
    }} // omit this entire key when no worksheet is needed
}}"""
    
    return prompt


def _resolve_day_standards(assignment: dict, standards_by_id: dict, standards: list) -> list:
    """Return the ordered list of standards referenced by an assignment."""
    standard_ids = assignment.get('standard_ids', [])
    day_standards = [standards_by_id.get(sid) for sid in standard_ids if sid in standards_by_id]
    day_standards = [s for s in day_standards if s is not None]
    if not day_standards:
        day_standards = [standards[0]] if standards else []
    return day_standards


def _create_fallback_lesson_plan(day_standards: list, rules: dict) -> dict:
    """Return a deterministic lesson plan used when LLM calls fail."""
    description = day_standards[0].get('description', '') if day_standards else 'the assigned topic'
    return {
        "objective": f"Learn about: {description}",
        "materials_needed": rules.get('allowed_materials', [])[:2],
        "procedure": [
            "Introduce the concept",
            "Practice with materials",
            "Review and assess understanding"
        ]
    }


def _assemble_day_plan(
    day: str,
    day_standards: list,
    day_focus: str,
    lesson_plan: dict,
    resources: dict | None = None,
    worksheet_plans: list | None = None,
    worksheet_errors: list | None = None,
) -> dict:
    """Compose the day plan payload from provided components."""
    payload = {
        "day": day,
        "lesson_plan": lesson_plan,
        "standard": day_standards[0] if day_standards else {},
        "standards": day_standards,
        "focus": day_focus
    }
    if resources:
        payload["resources"] = resources
    if worksheet_plans:
        payload["worksheet_plans"] = worksheet_plans
    if worksheet_errors:
        payload.setdefault("resource_errors", []).extend(worksheet_errors)
    return payload


def _extract_lesson_and_resources(payload: dict, day_label: str) -> tuple[dict, ResourceRequests | None]:
    """Normalize LLM response into lesson plan + optional worksheet resources."""

    lesson_plan = payload.get("lesson_plan")
    if not isinstance(lesson_plan, dict):
        lesson_plan = payload

    raw_resources = payload.get("resources") if isinstance(payload, dict) else None
    resource_model: ResourceRequests | None = None
    if isinstance(raw_resources, dict) and raw_resources:
        try:
            resource_model = ResourceRequests.model_validate(raw_resources)
        except ValidationError as exc:
            print(f"Warning: Invalid worksheet resources for {day_label}: {exc}")
        else:
            if not resource_model.has_requests():
                resource_model = None

    return lesson_plan, resource_model


def _build_day_plan(assignment: dict, standards_by_id: dict, standards: list, rules: dict, client: OpenAI, model: str) -> dict:
    """Generate one day's plan inside the thread pool with deterministic fallbacks.

    Args:
        assignment: Dict containing `day`, `standard_ids`, and optional `focus` keys.
        standards_by_id: Lookup of standard_id -> standard metadata.
        standards: List of candidate standards (used for fallback selection).
        rules: Parent preference metadata (materials, notes, etc.).
        client: Thread-safe OpenAI client instance.
        model: OpenAI model name.

    Returns:
        Dict with `day`, `lesson_plan`, `standard`, `standards`, and `focus` keys.
    """
    day = assignment.get('day') or ''
    day_focus = assignment.get('focus', '') or ''
    day_standards = _resolve_day_standards(assignment, standards_by_id, standards)

    if len(day_standards) == 1:
        prompt = create_lesson_plan_prompt(day_standards[0], rules)
    else:
        combined_descriptions = " AND ".join([s.get('description', '') for s in day_standards])
        combined_standard = {
            'description': combined_descriptions,
            'subject': day_standards[0].get('subject') if day_standards else '',
            'grade_level': day_standards[0].get('grade_level') if day_standards else 0
        }
        prompt = create_lesson_plan_prompt(combined_standard, rules)

    if day_focus:
        prompt += f"\n\nDay Focus: {day_focus}"

    resources_model: ResourceRequests | None = None

    messages = [
        {"role": "system", "content": "You are a helpful K-12 education assistant. Always respond with valid JSON only."},
        {"role": "user", "content": prompt}
    ]
    llm_request_payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    try:
        response = client.chat.completions.create(**llm_request_payload)
        _log_llm_exchange(
            phase="daily_plan",
            metadata={"day": day},
            request_payload=llm_request_payload,
            response_payload=response.model_dump(),
        )
        lesson_plan_json = response.choices[0].message.content or "{}"
        payload = json.loads(lesson_plan_json)
        lesson_plan, resources_model = _extract_lesson_and_resources(payload, day)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse lesson plan JSON for {day}: {e}")
        lesson_plan = _create_fallback_lesson_plan(day_standards, rules)
        resources_model = None
    except Exception as e:
        _log_llm_exchange(
            phase="daily_plan",
            metadata={"day": day},
            request_payload=llm_request_payload,
            error=str(e),
        )
        print(f"Warning: Failed to generate lesson plan for {day}: {e}")
        lesson_plan = _create_fallback_lesson_plan(day_standards, rules)
        resources_model = None

    worksheet_plans = []
    worksheet_errors = []
    resources_payload: dict | None = None

    if resources_model:
        plans, errors = build_worksheets_from_requests(resources_model)
        worksheet_plans = [
            {
                "kind": plan.kind,
                "filename_hint": plan.filename_hint,
                "metadata": plan.metadata,
            }
            for plan in plans
        ]
        worksheet_errors = [
            {"kind": err.kind, "message": err.message}
            for err in errors
        ]
        resources_payload = resources_model.model_dump(exclude_none=True)

    return _assemble_day_plan(
        day,
        day_standards,
        day_focus,
        lesson_plan,
        resources_payload,
        worksheet_plans or None,
        worksheet_errors or None,
    )


def generate_weekly_plan(student_id: str, grade_level: int, subject: str) -> dict:
    """
    Generate a weekly lesson plan for a student using LLM.
    
    Args:
        student_id: Unique identifier for the student
        grade_level: Grade level for the standards
        subject: Subject area (may be overridden by theme rules)
        
    Returns:
        A dictionary containing the complete weekly plan with daily lesson plans
        
    Raises:
        ValueError: If student not found or API key not set
    """
    # Check for OpenAI API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Get base URL and model from environment variables with defaults
    base_url = os.environ.get('OPENAI_BASE_URL', None)
    model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Initialize OpenAI client. The official SDK client is stateless and thread-safe,
    # so we reuse a single instance across the executor workers below.
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # Get student profile and parse rules
    student_profile = get_student_profile(student_id)
    if student_profile is None:
        raise ValueError(f"Student with id '{student_id}' not found")
    
    # Parse plan_rules_blob to get rules
    rules = json.loads(student_profile['plan_rules_blob'])
    
    # Get standards for the student. We request more than 5 to have flexibility
    # in how they're distributed across the week. Some complex standards may need
    # multiple days, while simpler ones can be covered in a single day.
    standards = get_filtered_standards(student_id, grade_level, subject, limit=10)
    
    if len(standards) == 0:
        raise ValueError(f"No standards found for student {student_id}.")
    
    # Precompute a pretty JSON preview of the first few standards for the prompt
    available_standards_preview = [
        {"id": s.get("standard_id"), "description": s.get("description")}
        for s in standards[:5]
    ]
    available_standards_text = json.dumps(available_standards_preview, indent=2)

    # First pass: Create a weekly overview/scaffold
    # This helps ensure complex standards get multiple days if needed
    scaffold_prompt = f"""You are an expert K-12 educator creating a weekly lesson plan scaffold.

Grade Level: {grade_level}
Subject: {subject}

Available Standards (may use 1 or more):
{available_standards_text}

Parent Constraints:
- Allowed materials: {rules.get('allowed_materials', [])}
- Parent guidance: {rules.get('parent_notes', 'keep procedures under 3 steps')}

Create a weekly plan that:
1. Distributes standards across Monday-Friday appropriately
2. Complex standards should span multiple days with scaffolding
3. Simpler standards can be covered in a single day
4. Each day should build on previous days

Respond with a JSON object in this exact format:
{{
  "weekly_overview": "Brief description of how the week progresses",
  "daily_assignments": [
    {{
      "day": "Monday",
      "standard_ids": ["standard_id_1"],
      "focus": "Brief description of this day's focus"
    }},
    ...
  ]
}}"""

    scaffold_messages = [
        {"role": "system", "content": "You are a helpful K-12 education assistant. Always respond with valid JSON only."},
        {"role": "user", "content": scaffold_prompt}
    ]
    scaffold_request_payload = {
        "model": model,
        "messages": scaffold_messages,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    # Get the weekly scaffold from LLM
    try:
        scaffold_response = client.chat.completions.create(**scaffold_request_payload)
        _log_llm_exchange(
            phase="weekly_scaffold",
            metadata={"label": "weekly_scaffold"},
            request_payload=scaffold_request_payload,
            response_payload=scaffold_response.model_dump(),
        )
        
        scaffold_json = scaffold_response.choices[0].message.content or "{}"
        weekly_scaffold = json.loads(scaffold_json)
        daily_assignments = weekly_scaffold.get('daily_assignments', [])
        weekly_overview = weekly_scaffold.get('weekly_overview', '')
    except json.JSONDecodeError as e:
        # JSON parsing error from LLM - log and use fallback
        print(f"Warning: Failed to parse scaffold JSON: {e}")
        _log_llm_exchange(
            phase="weekly_scaffold",
            metadata={"label": "weekly_scaffold"},
            request_payload=scaffold_request_payload,
            error=str(e),
        )
        weekly_overview = "Weekly plan using standard curriculum progression"
        daily_assignments = [
            {"day": day, "standard_ids": [standards[i].get('standard_id')], "focus": f"Day {i+1} focus"}
            for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
            if i < len(standards)
        ]
    except Exception as e:
        # Other errors (API, network, etc.) - log and use fallback
        print(f"Warning: Failed to generate scaffold: {e}")
        weekly_overview = "Weekly plan using standard curriculum progression"
        daily_assignments = [
            {"day": day, "standard_ids": [standards[i].get('standard_id')], "focus": f"Day {i+1} focus"}
            for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
            if i < len(standards)
        ]
    
    # Ensure we have exactly 5 days
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    if len(daily_assignments) != 5:
        # Adjust to exactly 5 days
        while len(daily_assignments) < 5:
            daily_assignments.append({
                "day": days[len(daily_assignments)],
                "standard_ids": [standards[min(len(daily_assignments), len(standards)-1)].get('standard_id')],
                "focus": "Additional practice"
            })
        daily_assignments = daily_assignments[:5]
    
    # Create a lookup for standards by ID
    standards_by_id = {s.get('standard_id'): s for s in standards}

    # Build daily plan concurrently based on scaffold
    max_workers = max(1, min(len(daily_assignments), MAX_DAILY_PLAN_THREADS))
    daily_plan = [None] * len(daily_assignments)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(
                _build_day_plan,
                assignment,
                standards_by_id,
                standards,
                rules,
                client,
                model
            ): idx
            for idx, assignment in enumerate(daily_assignments)
        }

        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                daily_plan[idx] = future.result()
            except Exception as e:
                print(f"Warning: Daily plan generation failed for index {idx}: {e}")
                assignment = daily_assignments[idx]
                day_standards = _resolve_day_standards(assignment, standards_by_id, standards)
                fallback_plan = _create_fallback_lesson_plan(day_standards, rules)
                daily_plan[idx] = _assemble_day_plan(
                    assignment.get('day') or '',
                    day_standards,
                    assignment.get('focus', '') or '',
                    fallback_plan,
                    None,
                    None,
                    None,
                )
    
    # Calculate week_of date (Monday of current week)
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    week_of = monday.strftime("%Y-%m-%d")
    
    # Construct the final weekly plan
    weekly_plan = {
        "plan_id": f"plan_{student_id}_{week_of}",
        "student_id": student_id,
        "week_of": week_of,
        "weekly_overview": weekly_overview,
        "daily_plan": daily_plan
    }
    
    return weekly_plan
