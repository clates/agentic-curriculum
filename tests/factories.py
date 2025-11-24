from __future__ import annotations

from copy import deepcopy


def build_weekly_plan(
    *,
    plan_id: str = "plan_student_2025-11-24",
    student_id: str = "student-123",
    grade_level: int = 4,
    subject: str = "Mathematics",
    week_of: str = "2025-11-24",
) -> dict:
    """Return a deterministic weekly plan payload for testing."""

    base_plan = {
        "plan_id": plan_id,
        "student_id": student_id,
        "grade_level": grade_level,
        "subject": subject,
        "week_of": week_of,
        "weekly_overview": "Focus on multiplying fractions.",
        "daily_plan": [
            {
                "day": "Monday",
                "focus": "Intro",
                "lesson_plan": {"objective": "Learn", "procedure": ["Do"]},
                "standards": [{"standard_id": "MATH.4.1"}],
                "resources": {
                    "mathWorksheet": {
                        "title": "Warmup",
                        "artifacts": [
                            {
                                "type": "pdf",
                                "path": f"artifacts/{plan_id}/monday.pdf",
                                "size_bytes": 1024,
                                "sha256": "abc123",
                            },
                            {
                                "type": "png",
                                "path": f"artifacts/{plan_id}/monday.png",
                                "size_bytes": 2048,
                                "sha256": "def456",
                            },
                        ],
                    }
                },
                "worksheet_plans": [{"kind": "mathWorksheet", "filename_hint": "warmup"}],
                "resource_errors": [],
            },
            {
                "day": "Tuesday",
                "focus": "Apply",
                "lesson_plan": {"objective": "Practice", "procedure": ["Explain"]},
                "standards": [{"standard_id": "MATH.4.2"}],
                "resources": {
                    "readingWorksheet": {
                        "title": "Story",
                        "artifacts": [
                            {
                                "type": "pdf",
                                "path": f"artifacts/{plan_id}/tuesday.pdf",
                                "size_bytes": 512,
                                "sha256": "ghi789",
                            }
                        ],
                    }
                },
                "worksheet_plans": [{"kind": "readingWorksheet", "filename_hint": "story"}],
                "resource_errors": [],
            },
        ],
    }

    return deepcopy(base_plan)
