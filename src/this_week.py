"""Read model for the parent's 'This week' home (M10.4): one card per child, one next action.

The next action is driven by the loop state on week_plan (see loop_state.py):
check_in, writing (we are working on it), pick, print, done. Raw status names never leave this
module's output as copy; the UI maps ``next_action`` to plain words.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import date, timedelta

try:  # Prefer package-relative import when available
    from . import week_plan as wp  # type: ignore
except ImportError:  # Fallback for direct script execution
    sys.path.insert(0, os.path.dirname(__file__))
    import week_plan as wp  # type: ignore

NEXT_ACTION = {
    "awaiting_feedback": "check_in",
    "outlining": "writing",
    "awaiting_pick": "pick",
    "expired": "pick",
    "authoring": "writing",
    "ready": "print",
    "printed": "done",
}


def upcoming_week_start(today: date) -> str:
    """Monday of the school week a brand-new plan is for (this week through Friday, else next)."""
    monday = today - timedelta(days=today.weekday())
    if today.weekday() >= 5:
        monday += timedelta(days=7)
    return monday.isoformat()


def _first_name(metadata_blob: str | None) -> str:
    try:
        name = (json.loads(metadata_blob or "{}").get("name") or "").strip()
    except (ValueError, AttributeError):
        name = ""
    return name.split(" ")[0] if name else "Your child"


def this_week_cards(conn: sqlite3.Connection, family_id: str, today: date) -> dict:
    """One card per child. A child with no plan yet gets one created (idempotent)."""
    conn.row_factory = sqlite3.Row
    kids = conn.execute(
        "SELECT student_id, metadata_blob FROM student_profiles WHERE family_id=? "
        "ORDER BY student_id",
        (family_id,),
    ).fetchall()
    cards = []
    for kid in kids:
        plan = wp.latest_plan_for_student(conn, family_id, kid["student_id"])
        if plan is None:
            plan = wp.create_plan(conn, family_id, kid["student_id"], upcoming_week_start(today))
        cards.append(
            {
                "student_id": kid["student_id"],
                "first_name": _first_name(kid["metadata_blob"]),
                "plan_id": plan.plan_id,
                "week_start": plan.week_start,
                "next_action": NEXT_ACTION[plan.status],
                "options_expired": plan.status == "expired",
                "needs_attention": plan.needs_attention,
                "pick_deadline": plan.pick_deadline,
                "print_deadline": plan.print_deadline,
                "packet_id": plan.packet_id,
            }
        )
    return {"children": cards}
