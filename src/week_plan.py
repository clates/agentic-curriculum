"""Data access for the week_plan table (M6.2). Every function takes the family it acts for.

The caller passes ``family_id`` explicitly until the Tenant object lands (D2); each query filters
on it, so one family can never read or change another family's plan. State transitions live in
``loop_state.advance`` (M8.1); this module only creates, reads and records outlines and the pick.
"""

from __future__ import annotations

import os
import secrets
import sqlite3
import sys
from dataclasses import dataclass
from datetime import UTC, datetime

try:  # Prefer package-relative import when available
    from .outline_models import OutlineSet  # type: ignore
except ImportError:  # Fallback for direct script execution
    sys.path.insert(0, os.path.dirname(__file__))
    from outline_models import OutlineSet  # type: ignore

STATUSES = (
    "awaiting_feedback",
    "outlining",
    "awaiting_pick",
    "authoring",
    "ready",
    "printed",
    "expired",
)


class PlanNotFound(LookupError):
    """No such plan for this family (also what another family's plan looks like)."""


@dataclass(frozen=True)
class WeekPlan:
    plan_id: str
    family_id: str
    student_id: str
    week_start: str
    status: str
    state_version: int
    needs_attention: bool
    attention_reason: str | None
    outlines: OutlineSet | None
    outlines_ready_at: str | None
    picked_option: str | None
    packet_id: str | None
    feedback_due_at: str | None
    pick_deadline: str | None
    print_deadline: str | None
    created_at: str
    updated_at: str


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def new_plan_id() -> str:
    return "wp_" + secrets.token_hex(8)


def row_to_plan(row: sqlite3.Row) -> WeekPlan:
    outlines = (
        OutlineSet.model_validate_json(row["outlines_json"]) if row["outlines_json"] else None
    )
    return WeekPlan(
        plan_id=row["plan_id"],
        family_id=row["family_id"],
        student_id=row["student_id"],
        week_start=row["week_start"],
        status=row["status"],
        state_version=row["state_version"],
        needs_attention=bool(row["needs_attention"]),
        attention_reason=row["attention_reason"],
        outlines=outlines,
        outlines_ready_at=row["outlines_ready_at"],
        picked_option=row["picked_option"],
        packet_id=row["packet_id"],
        feedback_due_at=row["feedback_due_at"],
        pick_deadline=row["pick_deadline"],
        print_deadline=row["print_deadline"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create_plan(
    conn: sqlite3.Connection,
    family_id: str,
    student_id: str,
    week_start: str,
    *,
    feedback_due_at: str | None = None,
    pick_deadline: str | None = None,
    print_deadline: str | None = None,
) -> WeekPlan:
    """Create the plan for a school week, or return the existing one (idempotent)."""
    conn.row_factory = sqlite3.Row
    now = utc_now()
    conn.execute(
        "INSERT OR IGNORE INTO week_plan (plan_id, family_id, student_id, week_start, "
        "feedback_due_at, pick_deadline, print_deadline, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (
            new_plan_id(),
            family_id,
            student_id,
            week_start,
            feedback_due_at,
            pick_deadline,
            print_deadline,
            now,
            now,
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM week_plan WHERE family_id=? AND student_id=? AND week_start=?",
        (family_id, student_id, week_start),
    ).fetchone()
    return row_to_plan(row)


def get_plan(conn: sqlite3.Connection, family_id: str, plan_id: str) -> WeekPlan:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM week_plan WHERE family_id=? AND plan_id=?", (family_id, plan_id)
    ).fetchone()
    if row is None:
        raise PlanNotFound(plan_id)
    return row_to_plan(row)


def current_plans(conn: sqlite3.Connection, family_id: str, week_start: str) -> list[WeekPlan]:
    """Every plan for one school week, one per child (what 'This week' reads)."""
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM week_plan WHERE family_id=? AND week_start=? ORDER BY student_id",
        (family_id, week_start),
    ).fetchall()
    return [row_to_plan(r) for r in rows]


def latest_plan_for_student(
    conn: sqlite3.Connection, family_id: str, student_id: str
) -> WeekPlan | None:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM week_plan WHERE family_id=? AND student_id=? "
        "ORDER BY week_start DESC LIMIT 1",
        (family_id, student_id),
    ).fetchone()
    return row_to_plan(row) if row else None


def store_outlines(
    conn: sqlite3.Connection, family_id: str, plan_id: str, outlines: OutlineSet
) -> None:
    """Record the generated outlines (does not change status: advance() does)."""
    now = utc_now()
    cur = conn.execute(
        "UPDATE week_plan SET outlines_json=?, outlines_ready_at=?, updated_at=? "
        "WHERE family_id=? AND plan_id=?",
        (outlines.model_dump_json(), now, now, family_id, plan_id),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise PlanNotFound(plan_id)
