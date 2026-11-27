"""Per-subject coverage for the family dashboard: counts only, never a standard id or a skill name."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

try:
    from .candidate_selector import is_whole_skill
    from .model_context import build_model_context
    from .progress_summary import classify_progress
except ImportError:  # imported as a top-level module (src/ on sys.path)
    from candidate_selector import is_whole_skill
    from model_context import build_model_context
    from progress_summary import classify_progress

SUBJECT_ORDER = ("Math", "English", "Science", "History", "Computer Science")


def build_coverage(
    conn: sqlite3.Connection,
    metadata_blob: Any,
    plan_rules_blob: Any,
    progress_blob: Any,
    *,
    fallback_grade: int | None = None,
) -> list[dict[str, Any]]:
    """``[{subject, solid, shaky, to_come}]``, only subjects with a count.

    solid: mastered (a review coming due does not change it). shaky: still developing (shaky or
    needing more work). to_come: whole skills at the child's grade for the subject that are neither.
    """
    progress = json.loads(progress_blob or "{}")
    context = build_model_context(metadata_blob, plan_rules_blob, fallback_grade=fallback_grade)
    solid_ids, shaky_ids, needs_work_ids = classify_progress(progress)  # due ones stay solid
    solid, shaky = set(solid_ids), set(shaky_ids) | set(needs_work_ids)
    grades = {context.grade_for(subject) for subject in SUBJECT_ORDER}

    # Only rows that can count: the child's own skills (any grade) and their grades' to-come ones.
    try:
        rows = conn.execute(
            "SELECT standard_id, subject, grade_level, description FROM standards"
            " WHERE standard_id IN (SELECT value FROM json_each(?))"
            " OR grade_level IN (SELECT value FROM json_each(?))",
            (json.dumps(sorted(solid | shaky)), json.dumps(sorted(grades))),
        ).fetchall()
    except sqlite3.OperationalError:
        return []

    counts: dict[str, dict[str, int]] = {}
    for sid, subject, grade, description in rows:
        if not subject or not is_whole_skill(sid, description):
            continue
        row = counts.setdefault(subject, {"solid": 0, "shaky": 0, "to_come": 0})
        if sid in solid:
            row["solid"] += 1
        elif sid in shaky:
            row["shaky"] += 1
        elif grade == context.grade_for(subject):
            row["to_come"] += 1

    order = {name: i for i, name in enumerate(SUBJECT_ORDER)}
    return [
        {"subject": subject, **row}
        for subject, row in sorted(
            counts.items(), key=lambda kv: (order.get(kv[0], len(order)), kv[0])
        )
        if any(row.values())
    ]
