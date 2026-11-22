"""What the parent's print screen needs (M10.7): which documents a week has, and 'I've printed it'.

The loop state machine already owns the ``ready -> printed`` move (``marked_printed`` in
``loop_state``); this module only checks the plan belongs to the child and turns the machine's
refusals into plain results. ``GET /this-week`` reads the same ``week_plan.status``, so the card
turns into the 'all set' state as soon as the move is recorded.
"""

from __future__ import annotations

import os
import sqlite3
import sys
from typing import Any

try:  # Prefer package-relative import when available
    from . import week_plan as wp  # type: ignore
    from .loop_state import Event, IllegalTransition, advance  # type: ignore
except ImportError:  # Fallback for direct script execution
    sys.path.insert(0, os.path.dirname(__file__))
    import week_plan as wp  # type: ignore
    from loop_state import Event, IllegalTransition, advance  # type: ignore

STRUCTURED_DOCS = ["packet", "guide", "prep"]
LEGACY_DOCS = ["packet"]


class PlanNotReady(Exception):
    """The week is not at the printing step; ``status`` says where it is."""

    def __init__(self, status: str):
        self.status = status
        super().__init__(status)


def mark_printed(
    conn: sqlite3.Connection, family_id: str, student_id: str, plan_id: str
) -> dict[str, Any]:
    """Record that the parent printed the week. Safe to repeat. Raises ``wp.PlanNotFound`` when the
    plan is not this child's, ``PlanNotReady`` when the week is not ready to print."""
    plan = wp.get_plan(conn, family_id, plan_id)
    if plan.student_id != student_id:
        raise wp.PlanNotFound(plan_id)
    try:
        result = advance(conn, family_id, plan_id, Event("marked_printed"))
    except IllegalTransition as exc:
        raise PlanNotReady(exc.status) from exc
    return {"plan_id": plan_id, "status": result.plan.status, "already_printed": not result.applied}


def print_info(
    student_id: str, packet_id: str, packet: dict[str, Any], week: Any
) -> dict[str, Any]:
    """The title and the documents the week can print. Structured weeks have all three; a legacy
    packet has only the one printable packet."""
    if week is not None:
        return {"structured": True, "title": week.title, "documents": STRUCTURED_DOCS}
    payload = packet.get("payload") or {}
    subject = (payload.get("subject") or "").strip()
    return {"structured": False, "title": subject, "documents": LEGACY_DOCS}
