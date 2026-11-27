"""Plain-language progress summary read model (M5.5).

Answers "how is my child doing?" for a parent: no standard ids, no tree terms, no internal
mastery states. Pure functions; the endpoint in main.py supplies the data.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from typing import Any, Mapping

try:
    from .review_policy import REASON_MASTERED, REASON_MISSED, REASON_SHAKY, _parse, review_due
except ImportError:  # imported as a top-level module (src/ on sys.path)
    from review_policy import REASON_MASTERED, REASON_MISSED, REASON_SHAKY, _parse, review_due

FALLBACK_SKILL = "A skill we have been working on"
_LEAD_IN = re.compile(r"^(the )?(student|students|learner|child)s? (will|should|can)\s+", re.I)
_REVIEW_WORDS = {
    REASON_MISSED: "Was tricky last time, so it is worth another go",
    REASON_SHAKY: "Was shaky last time and is ready to revisit",
    REASON_MASTERED: "Solid before, time for a quick refresher",
}


def skill_label(description: str | None, max_len: int = 90) -> str:
    """Turn a curriculum description into a short, human skill name."""
    text = " ".join((description or "").split())
    if not text:
        return FALLBACK_SKILL
    text = _LEAD_IN.sub("", text)
    text = re.split(r"(?<=[.;])\s", text, maxsplit=1)[0].rstrip(".;")
    if len(text) > max_len:
        text = text[: max_len - 1].rsplit(" ", 1)[0].rstrip(",;: ") + "…"
    return text[:1].upper() + text[1:] if text else FALLBACK_SKILL


def _item(standards: Mapping[str, Mapping[str, Any]], sid: str, **extra: Any) -> dict[str, Any]:
    info = standards.get(sid) or {}
    item = {"skill": skill_label(info.get("description"))}
    if info.get("subject"):
        item["subject"] = info["subject"]
    item.update(extra)
    return item


def classify_progress(progress: Mapping[str, Any]) -> tuple[list[str], list[str], list[str]]:
    """Sorted standard ids: mastered, shaky, and needing more work.

    The one place these words are defined. Reviews coming due are not considered here.
    """
    meta = progress.get("standard_metadata") or {}
    solid = sorted(set(progress.get("mastered_standards", [])))
    shaky, needs_work = [], []
    for sid in sorted(set(progress.get("developing_standards", []))):
        last = meta.get(sid, {}).get("last_feedback")
        (needs_work if last in ("STRUGGLING", "NOT_STARTED") else shaky).append(sid)
    return solid, shaky, needs_work


def _sentence(first_name: str, solid: int, shaky: int, needs_work: int, due: int) -> str:
    who = first_name or "Your child"
    if not (solid or shaky or needs_work):
        return f"{who} has no progress recorded yet. Once you submit a Friday check, it shows here."
    bits = []
    if solid:
        bits.append(f"{solid} skill{'s' if solid != 1 else ''} going well")
    if shaky:
        bits.append(f"{shaky} still shaky")
    if needs_work:
        bits.append(f"{needs_work} needing more work")
    text = (
        f"{who} has " + ", ".join(bits[:-1]) + (" and " if len(bits) > 1 else "") + bits[-1] + "."
    )
    if due:
        text += f" {due} {'is' if due == 1 else 'are'} due for a review."
    return text


def build_progress_summary(
    student_name: str | None,
    progress: dict[str, Any] | str | None,
    standards: Mapping[str, Mapping[str, Any]],
    now: str | None = None,
) -> dict[str, Any]:
    """Build the parent-facing summary from a progress blob and a standards lookup."""
    if isinstance(progress, str):
        progress = json.loads(progress)
    progress = progress or {}
    meta = progress.get("standard_metadata") or {}
    ref = _parse(now) if now else datetime.now(UTC)
    first_name = (student_name or "").split(" ")[0]

    due_rows = review_due(progress, now)
    due_ids = {r["standard_id"] for r in due_rows}
    solid_ids, shaky_ids, needs_work_ids = classify_progress(progress)
    solid = [_item(standards, sid) for sid in solid_ids if sid not in due_ids]
    shaky = [_item(standards, sid) for sid in shaky_ids]
    needs_work = [_item(standards, sid) for sid in needs_work_ids]

    due = [
        _item(standards, r["standard_id"], why=_REVIEW_WORDS.get(r["reason"], "Time to revisit"))
        for r in due_rows
    ]

    cutoff = ref - timedelta(days=28)
    went_well, still_shaky, tricky = [], [], []
    for sid, m in sorted(meta.items()):
        recent = [
            e
            for e in m.get("feedback_history", [])
            if e.get("date") and cutoff <= _parse(e["date"]) <= ref
        ]
        if not recent:
            continue
        latest = max(recent, key=lambda e: e["date"])["rating"]
        bucket = {"MASTERED": went_well, "DEVELOPING": still_shaky}.get(latest)
        if latest in ("STRUGGLING", "NOT_STARTED"):
            bucket = tricky
        if bucket is not None:
            bucket.append(_item(standards, sid))

    return {
        "student_name": first_name or None,
        "summary": _sentence(first_name, len(solid), len(shaky), len(needs_work), len(due)),
        "solid": solid,
        "shaky": shaky,
        "needs_work": needs_work,
        "due_for_review": due,
        "last_four_weeks": {
            "skills_checked": len(went_well) + len(still_shaky) + len(tricky),
            "went_well": went_well,
            "still_shaky": still_shaky,
            "needs_work": tricky,
        },
    }
