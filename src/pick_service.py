"""Pick one of three (M6.4) and fresh ideas (M6.6): the parent-facing side of the week plan.

Everything here acts for one family and one child (D2). The loop's state moves only through
``loop_state.advance``; this module decides WHEN to call it and what to tell the parent.

Pick:   awaiting_pick --pick_made--> authoring, then the ``request_authoring`` hook.
        The same pick twice is a no-op that succeeds; a different pick once authoring has
        started is a clear conflict (the choice is already made).
Fresh:  awaiting_pick | expired --outlines_regenerate--> outlining --outlines_ready-->
        awaiting_pick, with new outlines. At most ``max_regenerations`` per week plan. The
        model call happens BEFORE any state moves, so a failed call leaves the plan as it was and
        does not use up an allowance. The loop event key ``regen:<plan>:<n>`` makes the n-th
        regeneration happen once, even if two requests race.
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol

try:  # Prefer package-relative import when available
    from . import week_plan as wp  # type: ignore
    from .authoring_kickoff import request_authoring  # type: ignore
    from .candidate_selector import NoCandidates, load_candidate_inputs, select_week_standards  # type: ignore
    from .loop_state import Event, IllegalTransition, advance  # type: ignore
    from .model_context import ModelStudentContext, build_model_context  # type: ignore
    from .outline_generator import generate_outlines  # type: ignore
    from .outline_models import OutlineSet  # type: ignore
except ImportError:  # Fallback for direct script execution / top-level import
    import week_plan as wp  # type: ignore
    from authoring_kickoff import request_authoring  # type: ignore
    from candidate_selector import NoCandidates, load_candidate_inputs, select_week_standards  # type: ignore
    from loop_state import Event, IllegalTransition, advance  # type: ignore
    from model_context import ModelStudentContext, build_model_context  # type: ignore
    from outline_generator import generate_outlines  # type: ignore
    from outline_models import OutlineSet  # type: ignore

DEFAULT_MAX_REGENERATIONS = 2


class PickError(Exception):
    """A refusal the parent should read in plain words. ``code`` is stable; ``status`` is HTTP."""

    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


class RegenerationLimits(Protocol):
    """How many times a family may ask for fresh ideas for one week (M9 backs this by plan)."""

    def max_regenerations(self, family_id: str) -> int: ...


class EnvLimits:
    def max_regenerations(self, family_id: str) -> int:
        raw = os.environ.get("OUTLINE_MAX_REGENERATIONS")
        try:
            return max(0, int(raw)) if raw else DEFAULT_MAX_REGENERATIONS
        except ValueError:
            return DEFAULT_MAX_REGENERATIONS


DEFAULT_LIMITS: RegenerationLimits = EnvLimits()


@dataclass(frozen=True)
class StudentRow:
    student_id: str
    progress_blob: str | None
    plan_rules_blob: str | None
    metadata_blob: str | None


def get_student(conn: sqlite3.Connection, family_id: str, student_id: str) -> StudentRow:
    row = conn.execute(
        "SELECT student_id, progress_blob, plan_rules_blob, metadata_blob FROM student_profiles "
        "WHERE family_id=? AND student_id=?",
        (family_id, student_id),
    ).fetchone()
    if row is None:
        raise PickError(404, "unknown_child", "We couldn’t find that child.")
    return StudentRow(*row)


def regenerations_used(conn: sqlite3.Connection, plan_id: str) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM loop_event WHERE plan_id=? AND event_type='outlines_regenerate'",
        (plan_id,),
    ).fetchone()[0]


def _public_outline(o) -> dict[str, Any]:
    """What the parent's screen gets: no standard ids, no internals."""
    return {
        "option_id": o.option_id,
        "title": o.title,
        "hook": o.hook,
        "topic": o.topic,
        "activities": o.activities,
        "skills": list(o.skills),
        "effort": o.effort,
    }


def plan_view(
    conn: sqlite3.Connection,
    family_id: str,
    plan: wp.WeekPlan,
    student: StudentRow,
    limits: RegenerationLimits = DEFAULT_LIMITS,
) -> dict[str, Any]:
    used = regenerations_used(conn, plan.plan_id)
    allowed = limits.max_regenerations(family_id)
    context = build_model_context(student.metadata_blob, student.plan_rules_blob)
    return {
        "plan_id": plan.plan_id,
        "student_id": plan.student_id,
        "first_name": context.first_name,
        "week_start": plan.week_start,
        "status": plan.status,
        "options_expired": plan.status == "expired",
        "pick_deadline": plan.pick_deadline,
        "picked_option": plan.picked_option,
        "outlines": [_public_outline(o) for o in plan.outlines.options] if plan.outlines else None,
        "regenerations_used": used,
        "regenerations_allowed": allowed,
        "regenerations_left": max(0, allowed - used),
    }


def current_plan(conn: sqlite3.Connection, family_id: str, student_id: str) -> wp.WeekPlan:
    get_student(conn, family_id, student_id)
    plan = wp.latest_plan_for_student(conn, family_id, student_id)
    if plan is None:
        raise PickError(404, "no_plan", "There is no plan for this child yet.")
    return plan


def get_current(
    conn: sqlite3.Connection,
    family_id: str,
    student_id: str,
    limits: RegenerationLimits = DEFAULT_LIMITS,
) -> dict[str, Any]:
    student = get_student(conn, family_id, student_id)
    plan = current_plan(conn, family_id, student_id)
    return plan_view(conn, family_id, plan, student, limits)


def _check_plan_id(plan: wp.WeekPlan, plan_id: str | None) -> None:
    if plan_id is not None and plan_id != plan.plan_id:
        raise PickError(
            409, "stale_plan", "These ideas are out of date. Please go back to This week."
        )


def pick(
    conn: sqlite3.Connection,
    family_id: str,
    student_id: str,
    option: str,
    plan_id: str | None = None,
    limits: RegenerationLimits = DEFAULT_LIMITS,
) -> dict[str, Any]:
    """Choose an option. Idempotent for an exact repeat; see the module docstring."""
    student = get_student(conn, family_id, student_id)
    plan = current_plan(conn, family_id, student_id)
    _check_plan_id(plan, plan_id)

    if plan.status in ("authoring", "ready", "printed"):
        if plan.picked_option != option:
            raise PickError(
                409,
                "already_picked",
                "You already chose this week’s idea, and we’re working on it. "
                "It can’t be changed now.",
            )
        if plan.status == "authoring":  # an exact repeat: heal a missed kickoff, change nothing
            request_authoring(family_id, student_id, plan.plan_id, option)
        return {**plan_view(conn, family_id, plan, student, limits), "already_picked": True}

    try:
        result = advance(
            conn, family_id, plan.plan_id, Event("pick_made", payload={"option_id": option})
        )
    except IllegalTransition as exc:
        if plan.status == "expired":
            raise PickError(
                409, "expired", "Those ideas ran out of time. Ask for fresh ones."
            ) from exc
        if plan.outlines is not None and option not in {o.option_id for o in plan.outlines.options}:
            raise PickError(422, "unknown_option", "That idea isn’t one of the three.") from exc
        raise PickError(409, "not_ready", "There’s nothing to pick yet.") from exc
    request_authoring(family_id, student_id, plan.plan_id, option)
    return {
        **plan_view(conn, family_id, result.plan, student, limits),
        "already_picked": not result.applied,
    }


def _db_path(conn: sqlite3.Connection) -> str:
    return conn.execute("PRAGMA database_list").fetchone()[2]


def _latest_packet_grade(conn: sqlite3.Connection, family_id: str, student_id: str) -> int | None:
    row = conn.execute(
        "SELECT grade_level FROM weekly_packets WHERE family_id=? AND student_id=? "
        "ORDER BY week_of DESC, created_at DESC LIMIT 1",
        (family_id, student_id),
    ).fetchone()
    return row[0] if row else None


def _topic_text(o) -> str:
    return o.topic or o.title


def recent_topics(
    conn: sqlite3.Connection, family_id: str, student: StudentRow, plan: wp.WeekPlan
) -> list[str]:
    """Topics to steer away from: what this child chose in recent weeks, and every topic already
    shown for this week (so fresh ideas are fresh)."""
    out: list[str] = []
    for past in wp.recent_plans_for_student(
        conn, family_id, student.student_id, before_week=plan.week_start
    ):
        if past.outlines and past.picked_option:
            out.append(_topic_text(past.outlines.get(past.picked_option)))
    if plan.outlines:
        out.extend(_topic_text(o) for o in plan.outlines.options)
    return out


def make_outlines(
    conn: sqlite3.Connection,
    family_id: str,
    student: StudentRow,
    plan: wp.WeekPlan,
    *,
    variant: int,
    client=None,
    today: date | None = None,
) -> OutlineSet:
    """Selector + one framing call. Nothing is stored. ``variant`` changes the topics (fresh ideas)."""
    from llm import UsageContext

    context: ModelStudentContext = build_model_context(
        student.metadata_blob,
        student.plan_rules_blob,
        today=today,
        fallback_grade=_latest_packet_grade(conn, family_id, student.student_id),
    )
    standards, prereqs = load_candidate_inputs(_db_path(conn), context.grade)
    # The engine alone picks the skills (mastery, review dates, grade). ``variant`` is not in the
    # seed: fresh ideas are new topics around the same skills.
    seed = f"{student.student_id}:{plan.week_start}"
    try:
        week_standards = select_week_standards(
            progress=student.progress_blob,
            standards=standards,
            prereqs=prereqs,
            grade=context.grade,
            seed=seed,
        )
    except NoCandidates as exc:
        raise PickError(
            422, "no_ideas", "We don’t have enough to plan from yet. Please check back soon."
        ) from exc
    generated = generate_outlines(
        context,
        week_standards,
        recent_topics=recent_topics(conn, family_id, student, plan),
        seed=f"{seed}:{variant}",
        client=client,
        usage=UsageContext(family_id=family_id, student_id=student.student_id),
    )
    return generated.outlines


def finish_outlining(
    conn: sqlite3.Connection,
    family_id: str,
    plan_id: str,
    *,
    client=None,
    today: date | None = None,
) -> wp.WeekPlan:
    """For the loop automation: write the first outlines of a plan that is ``outlining``."""
    plan = wp.get_plan(conn, family_id, plan_id)
    if plan.status != "outlining":
        return plan
    student = get_student(conn, family_id, plan.student_id)
    outlines = make_outlines(conn, family_id, student, plan, variant=0, client=client, today=today)
    wp.store_outlines(conn, family_id, plan_id, outlines)
    return advance(
        conn, family_id, plan_id, Event("outlines_ready", key=f"outlines:{plan_id}:0")
    ).plan


def regenerate(
    conn: sqlite3.Connection,
    family_id: str,
    student_id: str,
    plan_id: str | None = None,
    *,
    client=None,
    limits: RegenerationLimits = DEFAULT_LIMITS,
    today: date | None = None,
) -> dict[str, Any]:
    """Fresh ideas for an expired (or still open) set, within the weekly allowance."""
    student = get_student(conn, family_id, student_id)
    plan = current_plan(conn, family_id, student_id)
    _check_plan_id(plan, plan_id)

    if plan.status == "outlining":
        raise PickError(409, "busy", "We’re already writing fresh ideas. Give it a moment.")
    if plan.status not in ("awaiting_pick", "expired"):
        raise PickError(409, "not_ready", "There’s nothing to refresh right now.")

    used = regenerations_used(conn, plan.plan_id)
    if used >= limits.max_regenerations(family_id):
        raise PickError(
            409,
            "limit_reached",
            "You’ve used this week’s fresh ideas. We’ll have new ones after your next check-in.",
        )
    nth = used + 1
    outlines = make_outlines(
        conn, family_id, student, plan, variant=nth, client=client, today=today
    )

    started = advance(
        conn,
        family_id,
        plan.plan_id,
        Event("outlines_regenerate", key=f"regen:{plan.plan_id}:{nth}"),
    )
    if not started.applied:  # another request got there first
        raise PickError(409, "busy", "We’re already writing fresh ideas. Give it a moment.")
    wp.store_outlines(conn, family_id, plan.plan_id, outlines)
    done = advance(
        conn, family_id, plan.plan_id, Event("outlines_ready", key=f"outlines:{plan.plan_id}:{nth}")
    )
    return plan_view(conn, family_id, done.plan, student, limits)
