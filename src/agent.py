"""
agent.py

LLM-based agent for generating lesson plans using OpenAI API.
"""

from datetime import datetime, timedelta
import os
import sys
import json
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, cast
from openai import OpenAI
from pydantic import ValidationError

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:  # Prefer package-relative imports when available
    from .db_utils import get_student_profile
    from .logic import get_filtered_standards
    from .resource_models import ResourceRequests
    from .worksheet_requests import build_worksheets_from_requests, WorksheetArtifactPlan
    from .worksheets import Worksheet, ReadingWorksheet
    from .packet_store import save_weekly_packet
    from .worksheet_renderer import (
        render_worksheet_to_image,
        render_worksheet_to_pdf,
        render_reading_worksheet_to_image,
        render_reading_worksheet_to_pdf,
    )
except ImportError:  # Fallback for direct script execution
    sys.path.insert(0, os.path.dirname(__file__))
    from db_utils import get_student_profile  # type: ignore
    from logic import get_filtered_standards  # type: ignore
    from resource_models import ResourceRequests  # type: ignore
    from worksheet_requests import build_worksheets_from_requests, WorksheetArtifactPlan  # type: ignore
    from worksheets import Worksheet, ReadingWorksheet  # type: ignore
    from worksheet_renderer import (  # type: ignore
        render_worksheet_to_image,
        render_worksheet_to_pdf,
        render_reading_worksheet_to_image,
        render_reading_worksheet_to_pdf,
    )
    from packet_store import save_weekly_packet  # type: ignore


# Maximum number of concurrent threads for generating daily lesson plans.
# Default is 5 (one per weekday). Raising this may reduce latency but
# increases OpenAI rate-limit pressure and local CPU usage.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAX_DAILY_PLAN_THREADS = int(os.environ.get("MAX_DAILY_PLAN_THREADS", "5"))
LOG_DIR = PROJECT_ROOT / "logs"
GENERATE_WEEKLY_DIR = LOG_DIR / "generate-weekly"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

RESOURCE_GUIDANCE = """If a printable worksheet would measurably help the lesson, include a `resources` object.

Supported worksheet payloads (summarized from docs/WORKSHEET_TYPES.md):
1. `mathWorksheet` (two-operand vertical math): requires `problems` (each item has `operand_one`, `operand_two`, `operator:+|-`). Optional `title`, `instructions`, `metadata`.
    Example: "mathWorksheet": {"title": "Repeated Addition", "problems": [{"operand_one": 3, "operand_two": 3, "operator": "+"}]}
2. `readingWorksheet` (reading comprehension passage): requires `passage_title`, `passage`, and `questions` (each question has `prompt` + optional `response_lines`). Optional `vocabulary`, `instructions`, `title`, `metadata`.
    Example: "readingWorksheet": {"passage_title": "Garden Story", "passage": "...", "questions": [{"prompt": "What happened first?", "response_lines": 2}]}
3. `vennDiagramWorksheet` (compare/contrast two sets): requires `left_label` and `right_label`. Optional `both_label`, `word_bank` entries, and pre-filled `left_items`/`right_items`/`both_items` arrays.
    Example: "vennDiagramWorksheet": {"left_label": "Mammals", "right_label": "Reptiles", "word_bank": ["cat", "snake"]}
4. `featureMatrixWorksheet` (items vs. properties grid): requires `items` and `properties`. Optional `show_answers`, `metadata`, and per-item `checked_properties` to pre-mark cells.
    Example: "featureMatrixWorksheet": {"items": ["Dog", "Fish"], "properties": ["Has Fur", "Lives in Water"]}
5. `oddOneOutWorksheet` (identify the item that doesn't belong): requires `rows` where each row has at least 3 `items`. Optional `odd_item`, `explanation`, `show_answers`, `reasoning_lines`.
    Example: "oddOneOutWorksheet": {"rows": [{"items": ["dog", "cat", "car", "bird"]}], "reasoning_lines": 2}
6. `treeMapWorksheet` (root + branches classification map): requires `root_label` and `branches`. Each branch supplies a `label` plus either explicit `slots` or a `slot_count`. Optional `word_bank`, `metadata`.
    Example: "treeMapWorksheet": {"root_label": "Food Groups", "branches": [{"label": "Fruits", "slot_count": 3}]}

Only emit the worksheet fields you need. Omit the `resources` key entirely when no worksheet is needed.
"""

RESOURCE_FEW_SHOT = {
    "lesson_plan": {
        "objective": "Students practice repeated addition to prepare for multiplication.",
        "materials_needed": ["Counters", "Paper"],
        "procedure": [
            "Model repeated addition with counters.",
            "Have students solve two practice problems.",
            "Discuss how repeated addition relates to multiplication.",
        ],
    },
    "resources": {
        "mathWorksheet": {
            "title": "Repeated Addition Warm-Up",
            "problems": [
                {"operand_one": 2, "operand_two": 2, "operator": "+"},
                {"operand_one": 3, "operand_two": 3, "operator": "+"},
            ],
        }
    },
}
RESOURCE_FEW_SHOT_JSON = json.dumps(RESOURCE_FEW_SHOT, indent=2)


def _slugify(value: str) -> str:
    if not value:
        return "entry"
    return re.sub(r"[^a-zA-Z0-9_-]", "_", value)


class GenerationLogger:
    """Structured logger that tracks one weekly generation run."""

    def __init__(self, student_id: str, grade_level: int, subject: str) -> None:
        self.run_id = datetime.now().strftime("%Y%m%dT%H%M%S_%f")
        self.base_dir = GENERATE_WEEKLY_DIR / self.run_id
        self.daily_dir = self.base_dir / "daily_plans"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.daily_dir.mkdir(parents=True, exist_ok=True)
        self._day_slug_cache: dict[str, str] = {}
        self._day_slug_counts: dict[str, int] = {}
        self._write_json(
            self.base_dir / "run_metadata.json",
            {
                "run_id": self.run_id,
                "student_id": student_id,
                "grade_level": grade_level,
                "subject": subject,
                "created_at": self.run_id,
            },
        )

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

    def _day_slug(self, day_label: str) -> str:
        key = (day_label or "").strip().lower() or "day"
        if key in self._day_slug_cache:
            return self._day_slug_cache[key]
        base = _slugify(key) or "day"
        count = self._day_slug_counts.get(base, 0)
        slug = base if count == 0 else f"{base}_{count}"
        self._day_slug_counts[base] = count + 1
        self._day_slug_cache[key] = slug
        return slug

    def _daily_path(self, day_label: str, suffix: str = "") -> Path:
        slug = self._day_slug(day_label)
        filename = f"{slug}{suffix}.json"
        return self.daily_dir / filename

    def log_weekly_scaffold_exchange(
        self,
        request_payload: dict,
        response_payload: dict | None = None,
        error: str | None = None,
    ) -> None:
        payload: dict[str, Any] = {"request": request_payload}
        if response_payload is not None:
            payload["response"] = response_payload
        if error:
            payload["error"] = error
        self._write_json(self.base_dir / "weekly_scaffold_llm_exchange.json", payload)

    def log_weekly_scaffold_content(
        self,
        parsed_content: dict | None,
        raw_content: str,
        error: str | None = None,
    ) -> None:
        if parsed_content is not None:
            self._write_json(self.base_dir / "weekly_scaffold.json", parsed_content)
        else:
            self._write_json(
                self.base_dir / "weekly_scaffold.json",
                {"error": error or "parse_error", "raw_content": raw_content},
            )

    def log_weekly_plan(self, weekly_plan: dict) -> None:
        self._write_json(self.base_dir / "weekly_plan.json", weekly_plan)

    def log_daily_llm_exchange(
        self,
        day_label: str,
        request_payload: dict,
        response_payload: dict | None = None,
        error: str | None = None,
    ) -> None:
        payload: dict[str, Any] = {"request": request_payload}
        if response_payload is not None:
            payload["response"] = response_payload
        if error:
            payload["error"] = error
        self._write_json(self._daily_path(day_label, "_llm_exchange"), payload)

    def log_daily_response(
        self,
        day_label: str,
        parsed_content: dict | None,
        raw_content: str,
        error: str | None = None,
    ) -> None:
        if parsed_content is not None:
            self._write_json(self._daily_path(day_label, "_response"), parsed_content)
        else:
            self._write_json(
                self._daily_path(day_label, "_response"),
                {"error": error or "parse_error", "raw_content": raw_content},
            )

    def log_daily_plan(self, day_label: str, plan_payload: dict) -> None:
        self._write_json(self._daily_path(day_label), plan_payload)

    def log_daily_error(
        self,
        day_label: str,
        stage: str,
        message: str,
        request_payload: dict | None = None,
    ) -> None:
        payload: dict[str, Any] = {"stage": stage, "error": message}
        if request_payload is not None:
            payload["request"] = request_payload
        self._write_json(self._daily_path(day_label, "_error"), payload)


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
    allowed_materials = rules.get("allowed_materials", [])
    # Default to keeping procedures under 3 steps if parent_notes not provided
    parent_notes = rules.get("parent_notes", "keep procedures under 3 steps")

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
    - procedure: Step-by-step instructions for teaching the lesson (include approximate minutes for each step so the full lesson fits in about 60 minutes)

2. Important constraints:
   - Materials MUST ONLY come from this list: {allowed_materials}
   - Follow this parent guidance: {parent_notes}
    - Plan approximately one hour of focused work (45-60 minutes total) and keep procedure steps tightly scoped
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
    }}
}}
If no worksheet is needed, omit the entire `resources` key.
"""

    return prompt


def _resolve_day_standards(assignment: dict, standards_by_id: dict, standards: list) -> list:
    """Return the ordered list of standards referenced by an assignment."""
    standard_ids = assignment.get("standard_ids", [])
    day_standards = [standards_by_id.get(sid) for sid in standard_ids if sid in standards_by_id]
    day_standards = [s for s in day_standards if s is not None]
    if not day_standards:
        day_standards = [standards[0]] if standards else []
    return day_standards


def _create_fallback_lesson_plan(day_standards: list, rules: dict) -> dict:
    """Return a deterministic lesson plan used when LLM calls fail."""
    description = day_standards[0].get("description", "") if day_standards else "the assigned topic"
    return {
        "objective": f"Learn about: {description}",
        "materials_needed": rules.get("allowed_materials", [])[:2],
        "procedure": [
            "Introduce the concept",
            "Practice with materials",
            "Review and assess understanding",
        ],
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
        "focus": day_focus,
    }
    if resources:
        payload["resources"] = resources
    if worksheet_plans:
        payload["worksheet_plans"] = worksheet_plans
    if worksheet_errors:
        payload.setdefault("resource_errors", []).extend(worksheet_errors)
    return payload


def _artifact_day_dir(plan_id: str, day_label: str) -> Path:
    day_slug = _slugify(day_label.strip().lower()) if day_label else "day"
    return ARTIFACTS_DIR / plan_id / day_slug


def _relative_artifact_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _unique_artifact_path(directory: Path, filename_hint: str, extension: str) -> Path:
    safe_hint = _slugify(filename_hint or "worksheet")
    candidate = directory / f"{safe_hint}.{extension}"
    counter = 1
    while candidate.exists():
        candidate = directory / f"{safe_hint}_{counter}.{extension}"
        counter += 1
    return candidate


def _artifact_file_metadata(path: Path) -> tuple[int | None, str | None]:
    """Return (size_bytes, sha256) for the given artifact path."""

    try:
        size = path.stat().st_size
    except OSError:
        return None, None

    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
    except OSError:
        return size, None

    return size, digest.hexdigest()


def _render_worksheet_artifacts(
    plan_id: str,
    day_label: str,
    plans: list[WorksheetArtifactPlan],
    generation_logger: GenerationLogger | None = None,
) -> tuple[dict[str, list[dict]], list[dict]]:
    """Render worksheet artifacts and return payload + error metadata."""

    artifacts_by_kind: dict[str, list[dict]] = {}
    artifact_errors: list[dict] = []

    if not plans:
        return artifacts_by_kind, artifact_errors

    day_dir = _artifact_day_dir(plan_id, day_label)
    day_dir.mkdir(parents=True, exist_ok=True)

    for plan in plans:
        render_jobs: list[tuple[str, Callable[[Path], Path]]] = []
        if plan.kind == "mathWorksheet":
            worksheet = cast(Worksheet, plan.worksheet)
            render_jobs = [
                (
                    "png",
                    lambda output_path, worksheet=worksheet: render_worksheet_to_image(
                        worksheet, output_path
                    ),
                ),
                (
                    "pdf",
                    lambda output_path, worksheet=worksheet: render_worksheet_to_pdf(
                        worksheet, output_path
                    ),
                ),
            ]
        elif plan.kind == "readingWorksheet":
            worksheet = cast(ReadingWorksheet, plan.worksheet)
            render_jobs = [
                (
                    "png",
                    lambda output_path, worksheet=worksheet: render_reading_worksheet_to_image(
                        worksheet, output_path
                    ),
                ),
                (
                    "pdf",
                    lambda output_path, worksheet=worksheet: render_reading_worksheet_to_pdf(
                        worksheet, output_path
                    ),
                ),
            ]
        else:
            message = f"Unsupported worksheet kind '{plan.kind}'"
            artifact_errors.append({"kind": plan.kind, "message": message})
            if generation_logger:
                generation_logger.log_daily_error(day_label, "artifact_render", message)
            continue

        for fmt, renderer in render_jobs:
            output_path = _unique_artifact_path(day_dir, plan.filename_hint or plan.kind, fmt)
            try:
                rendered_path = renderer(output_path)
            except Exception as exc:  # pragma: no cover - exercised via unit tests
                message = str(exc)
                artifact_errors.append({"kind": plan.kind, "format": fmt, "message": message})
                if generation_logger:
                    generation_logger.log_daily_error(day_label, "artifact_render", message)
                continue

            rendered_file = Path(rendered_path)
            size_bytes, checksum = _artifact_file_metadata(rendered_file)
            artifacts_by_kind.setdefault(plan.kind, []).append(
                {
                    "type": fmt,
                    "path": _relative_artifact_path(rendered_file),
                    "size_bytes": size_bytes,
                    "sha256": checksum,
                }
            )

    return artifacts_by_kind, artifact_errors


def _extract_lesson_and_resources(
    payload: dict, day_label: str
) -> tuple[dict, ResourceRequests | None]:
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


def _build_day_plan(
    assignment: dict,
    standards_by_id: dict,
    standards: list,
    rules: dict,
    client: OpenAI,
    model: str,
    plan_id: str,
    generation_logger: GenerationLogger | None = None,
) -> dict:
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
    day = assignment.get("day") or ""
    day_focus = assignment.get("focus", "") or ""
    day_standards = _resolve_day_standards(assignment, standards_by_id, standards)

    if len(day_standards) == 1:
        prompt = create_lesson_plan_prompt(day_standards[0], rules)
    else:
        combined_descriptions = " AND ".join([s.get("description", "") for s in day_standards])
        combined_standard = {
            "description": combined_descriptions,
            "subject": day_standards[0].get("subject") if day_standards else "",
            "grade_level": day_standards[0].get("grade_level") if day_standards else 0,
        }
        prompt = create_lesson_plan_prompt(combined_standard, rules)

    if day_focus:
        prompt += f"\n\nDay Focus: {day_focus}"

    resources_model: ResourceRequests | None = None

    messages = [
        {
            "role": "system",
            "content": "You are a helpful K-12 education assistant. Always respond with valid JSON only.",
        },
        {"role": "user", "content": prompt},
    ]
    llm_request_payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    try:
        response = client.chat.completions.create(**llm_request_payload)
    except Exception as e:
        if generation_logger:
            generation_logger.log_daily_llm_exchange(day, llm_request_payload, error=str(e))
            generation_logger.log_daily_error(day, "request_failed", str(e), llm_request_payload)
        print(f"Warning: Failed to generate lesson plan for {day}: {e}")
        lesson_plan = _create_fallback_lesson_plan(day_standards, rules)
        resources_model = None
    else:
        if generation_logger:
            generation_logger.log_daily_llm_exchange(
                day, llm_request_payload, response.model_dump()
            )
        response_content = response.choices[0].message.content or "{}"
        try:
            payload = json.loads(response_content)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse lesson plan JSON for {day}: {e}")
            if generation_logger:
                generation_logger.log_daily_response(day, None, response_content, str(e))
            lesson_plan = _create_fallback_lesson_plan(day_standards, rules)
            resources_model = None
        else:
            lesson_plan, resources_model = _extract_lesson_and_resources(payload, day)
            if generation_logger:
                generation_logger.log_daily_response(day, payload, response_content)

    worksheet_plans: list[dict] = []
    worksheet_errors: list[dict] = []
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
        worksheet_errors = [{"kind": err.kind, "message": err.message} for err in errors]
        resources_payload = resources_model.model_dump(exclude_none=True)

        artifact_map, artifact_render_errors = _render_worksheet_artifacts(
            plan_id,
            day,
            plans,
            generation_logger,
        )
        if artifact_render_errors:
            worksheet_errors.extend(artifact_render_errors)
        if artifact_map:
            if resources_payload is None:
                resources_payload = {}
            for kind, entries in artifact_map.items():
                kind_payload = resources_payload.setdefault(kind, {})
                kind_payload["artifacts"] = entries

    day_payload = _assemble_day_plan(
        day,
        day_standards,
        day_focus,
        lesson_plan,
        resources_payload,
        worksheet_plans or None,
        worksheet_errors or None,
    )
    if generation_logger:
        generation_logger.log_daily_plan(day, day_payload)
    return day_payload


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
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    # Get base URL and model from environment variables with defaults
    base_url = os.environ.get("OPENAI_BASE_URL", None)
    model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

    # Initialize OpenAI client. The official SDK client is stateless and thread-safe,
    # so we reuse a single instance across the executor workers below.
    client = OpenAI(api_key=api_key, base_url=base_url)

    # Get student profile and parse rules
    student_profile = get_student_profile(student_id)
    if student_profile is None:
        raise ValueError(f"Student with id '{student_id}' not found")

    # Parse plan_rules_blob to get rules
    rules = json.loads(student_profile["plan_rules_blob"])

    # Get standards for the student. We request more than 5 to have flexibility
    # in how they're distributed across the week. Some complex standards may need
    # multiple days, while simpler ones can be covered in a single day.
    standards = get_filtered_standards(student_id, grade_level, subject, limit=10)

    if len(standards) == 0:
        raise ValueError(f"No standards found for student {student_id}.")

    generation_logger = GenerationLogger(student_id, grade_level, subject)

    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    week_of = monday.strftime("%Y-%m-%d")
    plan_id = f"plan_{student_id}_{week_of}"

    # Precompute a pretty JSON preview of the first few standards for the prompt
    available_standards_preview = [
        {"id": s.get("standard_id"), "description": s.get("description")} for s in standards[:5]
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
5. Each day's activities should represent roughly one hour of learning time (about 45-60 minutes of instruction, practice, and wrap-up)

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
        {
            "role": "system",
            "content": "You are a helpful K-12 education assistant. Always respond with valid JSON only.",
        },
        {"role": "user", "content": scaffold_prompt},
    ]
    scaffold_request_payload = {
        "model": model,
        "messages": scaffold_messages,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    scaffold_raw_content = ""
    try:
        scaffold_response = client.chat.completions.create(**scaffold_request_payload)
        scaffold_dump = scaffold_response.model_dump()
        scaffold_raw_content = scaffold_response.choices[0].message.content or "{}"
        generation_logger.log_weekly_scaffold_exchange(scaffold_request_payload, scaffold_dump)
        weekly_scaffold = json.loads(scaffold_raw_content)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse scaffold JSON: {e}")
        generation_logger.log_weekly_scaffold_content(None, scaffold_raw_content, str(e))
        weekly_overview = "Weekly plan using standard curriculum progression"
        daily_assignments = [
            {
                "day": day,
                "standard_ids": [standards[i].get("standard_id")],
                "focus": f"Day {i+1} focus",
            }
            for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
            if i < len(standards)
        ]
    except Exception as e:
        print(f"Warning: Failed to generate scaffold: {e}")
        generation_logger.log_weekly_scaffold_exchange(scaffold_request_payload, error=str(e))
        generation_logger.log_weekly_scaffold_content(None, scaffold_raw_content or "", str(e))
        weekly_overview = "Weekly plan using standard curriculum progression"
        daily_assignments = [
            {
                "day": day,
                "standard_ids": [standards[i].get("standard_id")],
                "focus": f"Day {i+1} focus",
            }
            for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
            if i < len(standards)
        ]
    else:
        generation_logger.log_weekly_scaffold_content(weekly_scaffold, scaffold_raw_content)
        daily_assignments = weekly_scaffold.get("daily_assignments", [])
        weekly_overview = weekly_scaffold.get("weekly_overview", "")

    # Ensure we have exactly 5 days
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    if len(daily_assignments) != 5:
        # Adjust to exactly 5 days
        while len(daily_assignments) < 5:
            daily_assignments.append(
                {
                    "day": days[len(daily_assignments)],
                    "standard_ids": [
                        standards[min(len(daily_assignments), len(standards) - 1)].get(
                            "standard_id"
                        )
                    ],
                    "focus": "Additional practice",
                }
            )
        daily_assignments = daily_assignments[:5]

    # Create a lookup for standards by ID
    standards_by_id = {s.get("standard_id"): s for s in standards}

    # Build daily plan concurrently based on scaffold
    max_workers = max(1, min(len(daily_assignments), MAX_DAILY_PLAN_THREADS))
    daily_plan: list[dict] = [{} for _ in daily_assignments]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(
                _build_day_plan,
                assignment,
                standards_by_id,
                standards,
                rules,
                client,
                model,
                plan_id,
                generation_logger,
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
                day_label = assignment.get("day") or f"day_{idx+1}"
                fallback_payload = _assemble_day_plan(
                    assignment.get("day") or "",
                    day_standards,
                    assignment.get("focus", "") or "",
                    fallback_plan,
                    None,
                    None,
                    None,
                )
                daily_plan[idx] = fallback_payload
                if generation_logger:
                    generation_logger.log_daily_error(day_label, "worker_exception", str(e))
                    generation_logger.log_daily_plan(day_label, fallback_payload)

    # Construct the final weekly plan
    weekly_plan = {
        "plan_id": plan_id,
        "student_id": student_id,
        "grade_level": grade_level,
        "subject": subject,
        "week_of": week_of,
        "weekly_overview": weekly_overview,
        "daily_plan": daily_plan,
    }

    generation_logger.log_weekly_plan(weekly_plan)

    try:
        save_weekly_packet(weekly_plan)
    except Exception as exc:  # pragma: no cover - relies on sqlite errors
        print(f"Error: Failed to persist weekly packet {plan_id}: {exc}")
        raise

    return weekly_plan
