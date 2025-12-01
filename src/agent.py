"""
agent.py

LLM-based agent for generating lesson plans using OpenAI API.
"""

import hashlib
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, cast

from openai import OpenAI
from pydantic import ValidationError

from src.resource_models import ResourceRequests
from src.worksheet_requests import WorksheetArtifactPlan
from src.db_utils import get_student_profile
from src.logic import get_filtered_standards
from src.packet_store import save_weekly_packet
from src.worksheets.reading_comprehension import ReadingWorksheet
from src.worksheets.two_operand_math import Worksheet
from src.worksheet_renderer import (
    render_worksheet_to_image,
    render_worksheet_to_pdf,
    render_reading_worksheet_to_image,
    render_reading_worksheet_to_pdf,
)
from src.worksheet_requests import build_worksheets_from_requests
from src.prompts import (
    build_lesson_plan_prompt,
    build_weekly_scaffold_prompt,
    LLM_SYSTEM_MESSAGE,
)


# Configuration constants
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAX_DAILY_PLAN_THREADS = int(os.environ.get("MAX_DAILY_PLAN_THREADS", "5"))
LOG_DIR = PROJECT_ROOT / "logs"
GENERATE_WEEKLY_DIR = LOG_DIR / "generate-weekly"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

# Note: Resource guidance has been moved to src/prompts.py for easier editing.
# RESOURCE_GUIDANCE = """If a printable worksheet would measurably help the lesson, include a `resources` object.

# Supported worksheet payloads (summarized from docs/WORKSHEET_TYPES.md):
# 1. `mathWorksheet` (two-operand vertical math): requires `problems` (each item has `operand_one`, `operand_two`, `operator:+|-`). Optional `title`, `instructions`, `metadata`.
#     Example: "mathWorksheet": {"title": "Repeated Addition", "problems": [{"operand_one": 3, "operand_two": 3, "operator": "+"}]}
# 2. `readingWorksheet` (reading comprehension passage): requires `passage_title`, `passage`, and `questions` (each question has `prompt` + optional `response_lines`). Optional `vocabulary`, `instructions`, `title`, `metadata`.
#     Example: "readingWorksheet": {"passage_title": "Garden Story", "passage": "...", "questions": [{"prompt": "What happened first?", "response_lines": 2}]}
# 3. `vennDiagramWorksheet` (compare/contrast two sets): requires `left_label` and `right_label`. Optional `both_label`, `word_bank` entries, and pre-filled `left_items`/`right_items`/`both_items` arrays.
#     Example: "vennDiagramWorksheet": {"left_label": "Mammals", "right_label": "Reptiles", "word_bank": ["cat", "snake"]}
# 4. `featureMatrixWorksheet` (items vs. properties grid): requires `items` and `properties`. Optional `show_answers`, `metadata`, and per-item `checked_properties` to pre-mark cells.
#     Example: "featureMatrixWorksheet": {"items": ["Dog", "Fish"], "properties": ["Has Fur", "Lives in Water"]}
# 5. `oddOneOutWorksheet` (identify the item that doesn't belong): requires `rows` where each row has at least 3 `items`. Optional `odd_item`, `explanation`, `show_answers`, `reasoning_lines`.
#     Example: "oddOneOutWorksheet": {"rows": [{"items": ["dog", "cat", "car", "bird"]}], "reasoning_lines": 2}
# 6. `treeMapWorksheet` (root + branches classification map): requires `root_label` and `branches`. Each branch supplies a `label` plus either explicit `slots` or a `slot_count`. Optional `word_bank`, `metadata`.
#     Example: "treeMapWorksheet": {"root_label": "Food Groups", "branches": [{"label": "Fruits", "slot_count": 3}]}

# Only emit the worksheet fields you need. Omit the `resources` key entirely when no worksheet is needed.
# """

# RESOURCE_FEW_SHOT = {
#     "lesson_plan": {
#         "objective": "Students practice repeated addition to prepare for multiplication.",
#         "materials_needed": ["Counters", "Paper"],
#         "procedure": [
#             "Model repeated addition with counters.",
#             "Have students solve two practice problems.",
#             "Discuss how repeated addition relates to multiplication.",
#         ],
#     },
#     "resources": {
#         "mathWorksheet": {
#             "title": "Repeated Addition Warm-Up",
#             "problems": [
#                 {"operand_one": 2, "operand_one": 2, "operator": "+"},
#                 {"operand_one": 3, "operand_one": 3, "operator": "+"},
#             ],
#         }
#     },
# }
# RESOURCE_FEW_SHOT_JSON = json.dumps(RESOURCE_FEW_SHOT, indent=2)


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


# Note: Resource guidance has been moved to src/prompts.py for easier editing.
# Use build_lesson_plan_prompt() instead


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

    # Extract rules for prompt generation
    allowed_materials = rules.get("allowed_materials", [])
    parent_notes = rules.get("parent_notes", "keep procedures under 3 steps")

    # Build prompt for single or combined standards
    if len(day_standards) == 1:
        prompt = build_lesson_plan_prompt(
            day_standards[0], allowed_materials, parent_notes, day_focus
        )
    else:
        combined_descriptions = " AND ".join([s.get("description", "") for s in day_standards])
        combined_standard = {
            "description": combined_descriptions,
            "subject": day_standards[0].get("subject") if day_standards else "",
            "grade_level": day_standards[0].get("grade_level") if day_standards else 0,
        }
        prompt = build_lesson_plan_prompt(
            combined_standard, allowed_materials, parent_notes, day_focus
        )

    resources_model: ResourceRequests | None = None

    messages = [
        {"role": "system", "content": LLM_SYSTEM_MESSAGE},
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

    # Filter standards by cooldown (feedback mechanism)
    # Only include standards that have completed their cooldown period
    try:
        from feedback_processor import is_standard_eligible

        progress = json.loads(student_profile.get("progress_blob") or "{}")
        standard_metadata = progress.get("standard_metadata", {})
        current_time = datetime.now(UTC).isoformat().replace("+00:00", "Z")

        eligible_standards = [
            s
            for s in standards
            if is_standard_eligible(standard_metadata.get(s.get("standard_id"), {}), current_time)
        ]

        # If filtering removed all standards, log warning and use all standards
        if not eligible_standards:
            print(
                f"Warning: All standards in cooldown for {student_id}. Using all standards anyway."
            )
            eligible_standards = standards

        standards = eligible_standards
    except Exception as e:
        # If cooldown filtering fails, continue with all standards
        print(f"Warning: Failed to filter by cooldown: {e}. Using all standards.")

    generation_logger = GenerationLogger(student_id, grade_level, subject)

    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    week_of = monday.strftime("%Y-%m-%d")
    plan_id = f"plan_{student_id}_{week_of}"

    # Precompute a preview of the first few standards for the prompt
    available_standards_preview = [
        {"id": s.get("standard_id"), "description": s.get("description")} for s in standards[:5]
    ]

    # Get activity bias from quantity feedback
    quantity_prefs = rules.get("quantity_preferences", {})
    activity_bias = quantity_prefs.get("activity_bias", 0.0)

    # Calculate suggested base activity count (default ~3 per day)
    base_activities = 3
    adjusted_activities = int(base_activities * (1 + activity_bias * 0.5))
    adjusted_activities = max(1, min(adjusted_activities, 6))  # Clamp to [1, 6]

    # Build activity guidance based on bias
    if activity_bias < -0.1:
        activity_guidance = f"Each day should have approximately {adjusted_activities} activities (parent feedback indicates lessons should be shorter)."
    elif activity_bias > 0.1:
        activity_guidance = f"Each day should have approximately {adjusted_activities} activities (parent feedback indicates more content is desired)."
    else:
        activity_guidance = f"Each day should have approximately {adjusted_activities} activities."

    # Build weekly scaffold prompt using the prompts module
    scaffold_prompt = build_weekly_scaffold_prompt(
        grade_level=grade_level,
        subject=subject,
        available_standards=available_standards_preview,
        allowed_materials=rules.get("allowed_materials", []),
        parent_notes=rules.get("parent_notes", "keep procedures under 3 steps"),
        activity_guidance=activity_guidance,
    )

    scaffold_messages = [
        {"role": "system", "content": LLM_SYSTEM_MESSAGE},
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
