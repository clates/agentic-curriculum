"""Spaced re-surfacing policy (M5.4). Pure: reads a progress blob, returns what is due.

Policy, from each standard's most recent feedback:
  * Missed (STRUGGLING / NOT_STARTED): due now.
  * Shaky (DEVELOPING): comes back after 1 week; if it is still shaky when it returns the gap
    stretches to 2 weeks, then 4 weeks (the ladder is the number of shaky ratings in a row).
  * Mastered: keeps the cooldown it already earned (cooldown_weeks, set by feedback_processor).
  * Benched: returns after its bench cooldown, like the existing eligibility rule.

The self-hosted planner keeps using feedback_processor.is_standard_eligible unchanged; this
module is the hosted path's view of "what should come back".
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

SHAKY_LADDER_WEEKS = (1, 2, 4)

REASON_MISSED = "missed"
REASON_SHAKY = "shaky"
REASON_MASTERED = "mastered_refresh"
REASON_BENCHED = "benched_return"

_REASON_ORDER = {REASON_MISSED: 0, REASON_SHAKY: 1, REASON_MASTERED: 2, REASON_BENCHED: 3}


def _parse(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def _shaky_streak(history: list[dict[str, Any]]) -> int:
    streak = 0
    for entry in sorted(history, key=lambda e: e.get("date", "")):
        streak = streak + 1 if entry.get("rating") == "DEVELOPING" else 0
    return streak


def review_schedule(progress: dict[str, Any] | str | None) -> list[dict[str, Any]]:
    """Every standard with feedback, with when it is due and why (due or not)."""
    if isinstance(progress, str):
        progress = json.loads(progress)
    progress = progress or {}
    out: list[dict[str, Any]] = []
    for standard_id, meta in (progress.get("standard_metadata") or {}).items():
        last_seen = meta.get("last_seen")
        rating = meta.get("last_feedback")
        if not last_seen or not rating:
            continue
        seen = _parse(last_seen)
        if rating in ("STRUGGLING", "NOT_STARTED"):
            reason, due = REASON_MISSED, seen
        elif rating == "DEVELOPING":
            streak = max(_shaky_streak(meta.get("feedback_history") or []), 1)
            weeks = SHAKY_LADDER_WEEKS[min(streak, len(SHAKY_LADDER_WEEKS)) - 1]
            reason, due = REASON_SHAKY, seen + timedelta(weeks=weeks)
        elif rating == "MASTERED":
            reason = REASON_MASTERED
            due = seen + timedelta(weeks=meta.get("cooldown_weeks") or 0)
        elif rating == "BENCHED":
            reason = REASON_BENCHED
            due = seen + timedelta(weeks=meta.get("cooldown_weeks") or 0)
        else:
            continue
        out.append(
            {
                "standard_id": standard_id,
                "reason": reason,
                "last_seen": last_seen,
                "due_at": due.isoformat().replace("+00:00", "Z"),
            }
        )
    return out


def review_due(
    progress: dict[str, Any] | str | None, reference_date: str | None = None
) -> list[dict[str, Any]]:
    """Standards due on ``reference_date`` (default now), missed first, then oldest due first."""
    ref = _parse(reference_date) if reference_date else datetime.now(UTC)
    due = [r for r in review_schedule(progress) if _parse(r["due_at"]) <= ref]
    due.sort(key=lambda r: (_REASON_ORDER[r["reason"]], r["due_at"], r["standard_id"]))
    return due
