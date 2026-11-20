"""The weekly loop state machine (M8.1): ``advance(conn, family_id, plan_id, event)``.

States live on ``week_plan.status``. Each transition is a compare-and-set on
``(status, state_version)``, so two workers racing on one plan cannot both win. Rules:

- An event that is not allowed from the current state raises ``IllegalTransition``.
- A replay is a no-op: the same event key seen before, or a transition event whose target is the
  state the plan is already in (with the same payload). ``AdvanceResult.applied`` says which.
- ``needs_attention`` is a flag, not a state: ``flag_attention`` / ``clear_attention`` work in
  every state and never move ``status``.

    awaiting_feedback --feedback_submitted--> outlining --outlines_ready--> awaiting_pick
    awaiting_pick --pick_made--> authoring --authoring_done--> ready --marked_printed--> printed
    awaiting_pick --pick_expired--> expired;  awaiting_pick|expired --outlines_regenerate--> outlining
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from dataclasses import dataclass, field
from typing import Any

try:  # Prefer package-relative import when available
    from .week_plan import PlanNotFound, WeekPlan, get_plan, utc_now  # type: ignore
except ImportError:  # Fallback for direct script execution
    sys.path.insert(0, os.path.dirname(__file__))
    from week_plan import PlanNotFound, WeekPlan, get_plan, utc_now  # type: ignore

# event type -> (allowed from states, to state)
TRANSITIONS: dict[str, tuple[frozenset[str], str]] = {
    "feedback_submitted": (frozenset({"awaiting_feedback"}), "outlining"),
    "outlines_ready": (frozenset({"outlining"}), "awaiting_pick"),
    "outlines_regenerate": (frozenset({"awaiting_pick", "expired"}), "outlining"),
    "pick_made": (frozenset({"awaiting_pick"}), "authoring"),
    "pick_expired": (frozenset({"awaiting_pick"}), "expired"),
    "authoring_done": (frozenset({"authoring"}), "ready"),
    "marked_printed": (frozenset({"ready"}), "printed"),
}
FLAG_EVENTS = ("flag_attention", "clear_attention")
EVENT_TYPES = tuple(TRANSITIONS) + FLAG_EVENTS
MAX_CAS_ATTEMPTS = 5


class IllegalTransition(Exception):
    """The event cannot be applied in the plan's current state."""

    def __init__(self, status: str, event_type: str, detail: str = ""):
        self.status, self.event_type = status, event_type
        super().__init__(
            f"{event_type!r} is not allowed while the plan is {status!r}. {detail}".strip()
        )


class ConcurrentUpdate(Exception):
    """The plan kept changing underneath us; the caller may retry."""


@dataclass(frozen=True)
class Event:
    type: str
    key: str | None = None  # idempotency key, e.g. a job id; replays with it are no-ops
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdvanceResult:
    plan: WeekPlan
    applied: bool  # False = replay / already there; nothing changed


def _is_replay(plan: WeekPlan, event: Event) -> bool:
    """True when this event has already had its effect on the plan (state-based replay)."""
    if event.type == "flag_attention":
        return plan.needs_attention and plan.attention_reason == event.payload.get("reason")
    if event.type == "clear_attention":
        return not plan.needs_attention
    _, target = TRANSITIONS[event.type]
    if plan.status != target:
        return False
    if event.type == "pick_made":
        return plan.picked_option == event.payload.get("option_id")
    if event.type == "authoring_done":
        return plan.packet_id == event.payload.get("packet_id")
    return True


def _key_seen(conn: sqlite3.Connection, plan_id: str, key: str | None) -> bool:
    if key is None:
        return False
    row = conn.execute(
        "SELECT 1 FROM loop_event WHERE plan_id=? AND event_key=?", (plan_id, key)
    ).fetchone()
    return row is not None


def _validate(plan: WeekPlan, event: Event) -> tuple[str, dict[str, Any]]:
    """Return (to_status, column updates) or raise IllegalTransition."""
    allowed, target = TRANSITIONS[event.type]
    if plan.status not in allowed:
        raise IllegalTransition(plan.status, event.type)
    updates: dict[str, Any] = {}
    if event.type == "pick_made":
        option = event.payload.get("option_id")
        if plan.outlines is None:
            raise IllegalTransition(plan.status, event.type, "No outlines to pick from.")
        try:
            plan.outlines.get(option)
        except KeyError:
            raise IllegalTransition(
                plan.status, event.type, f"Unknown option {option!r}."
            ) from None
        updates["picked_option"] = option
    elif event.type == "authoring_done":
        packet_id = event.payload.get("packet_id")
        if not packet_id:
            raise IllegalTransition(plan.status, event.type, "A packet_id is required.")
        updates["packet_id"] = packet_id
    elif event.type == "outlines_regenerate":
        updates.update(outlines_json=None, outlines_ready_at=None, picked_option=None)
    return target, updates


def advance(conn: sqlite3.Connection, family_id: str, plan_id: str, event: Event) -> AdvanceResult:
    """Apply ``event`` to the plan as a compare-and-set. See the module docstring for the rules."""
    if event.type not in EVENT_TYPES:
        raise IllegalTransition("?", event.type, "Unknown event.")
    for _ in range(MAX_CAS_ATTEMPTS):
        plan = get_plan(conn, family_id, plan_id)
        if _key_seen(conn, plan_id, event.key) or _is_replay(plan, event):
            return AdvanceResult(plan, applied=False)

        if event.type in FLAG_EVENTS:
            to_status = plan.status
            if event.type == "flag_attention":
                updates: dict[str, Any] = {
                    "needs_attention": 1,
                    "attention_reason": event.payload.get("reason") or "unspecified",
                }
            else:
                updates = {"needs_attention": 0, "attention_reason": None}
        else:
            to_status, updates = _validate(plan, event)

        sets = {"status": to_status, "updated_at": utc_now(), **updates}
        assignments = ", ".join(f"{col}=?" for col in sets)
        try:
            cur = conn.execute(
                f"UPDATE week_plan SET {assignments}, state_version=state_version+1 "  # noqa: S608
                "WHERE family_id=? AND plan_id=? AND status=? AND state_version=?",
                (*sets.values(), family_id, plan_id, plan.status, plan.state_version),
            )
            if cur.rowcount == 1:
                conn.execute(
                    "INSERT INTO loop_event (family_id, plan_id, event_key, event_type, "
                    "from_status, to_status, payload_json, created_at) VALUES (?,?,?,?,?,?,?,?)",
                    (
                        family_id,
                        plan_id,
                        event.key,
                        event.type,
                        plan.status,
                        to_status,
                        json.dumps(event.payload, sort_keys=True),
                        utc_now(),
                    ),
                )
        except sqlite3.IntegrityError:
            conn.rollback()  # same key committed by someone else between our check and insert
            continue
        if cur.rowcount == 1:
            conn.commit()
            return AdvanceResult(get_plan(conn, family_id, plan_id), applied=True)
        conn.rollback()  # lost the race; re-read and re-decide
    raise ConcurrentUpdate(plan_id)


__all__ = [
    "AdvanceResult",
    "ConcurrentUpdate",
    "Event",
    "IllegalTransition",
    "PlanNotFound",
    "TRANSITIONS",
    "advance",
]
