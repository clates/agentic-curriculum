"""Weekly-loop scheduler (M8.4): ``tick(now, conn)`` on a timer, in each family's own timezone.

``python -m scheduler`` runs the tick loop alone; ``python -m worker --scheduler`` runs it beside
a worker. Every effect is idempotent (job idempotency keys, compare-and-set state moves, plan
create-if-missing), so ticking twice, or from two processes, changes nothing the second time.

Windows for the school week starting Monday M (all family-local wall-clock, DST-safe because the
local datetime is built first and only then converted to UTC):

    Fri M-3 15:00  CHECKIN   reminder:{family}:{M}   "do the Friday check-in" (families with a child
                             still awaiting_feedback)
    Sat M-2 10:00  NUDGE     nudge:{family}:{M}      "pick next week" (awaiting_pick), and the safety
                             net: a child still awaiting_feedback is moved on without a check-in
    Sun M-1 08:00  LASTCALL  lastcall:{family}:{M}   "pick today" (awaiting_pick)
    Sun M-1 12:00  pick deadline: awaiting_pick -> one of the three outlines is picked at random
                             and authored (or expired if there are no outlines)
    Sun M-1 20:00  print deadline (recorded on the plan; the author job must be done by then)

Notices catch up to the LATEST window only: after downtime on Sunday morning, a family gets the
last call, not Friday's reminder and Saturday's nudge as well. State-driven work (outlining ->
outline job, authoring -> author job, expiry) is always done. Plans for the coming week are
created from Friday 00:00 local. Missing family timezone (family_settings): SCHEDULER_DEFAULT_TZ (America/New_York).
"""

from __future__ import annotations

import logging
import os
import random
import sqlite3
import sys
import threading
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

try:
    from . import jobs, loop_state, week_plan as wp  # type: ignore
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import jobs  # type: ignore
    import loop_state  # type: ignore
    import week_plan as wp  # type: ignore

logger = logging.getLogger("scheduler")

DEFAULT_TZ = "America/New_York"
# (name, days after the target week's Monday (negative), local time)
CHECKIN = ("checkin", -3, time(15, 0))
NUDGE = ("nudge", -2, time(10, 0))
LASTCALL = ("lastcall", -1, time(8, 0))
PICK_DEADLINE = (-1, time(12, 0))
PRINT_DEADLINE = (-1, time(20, 0))
WINDOWS = (CHECKIN, NUDGE, LASTCALL)
NOTICE_KEY_PREFIX = {"checkin": "reminder", "nudge": "nudge", "lastcall": "lastcall"}
OPEN_STATES = ("awaiting_feedback", "outlining", "awaiting_pick", "authoring")


@dataclass
class TickReport:
    plans_created: list[str] = field(default_factory=list)
    safety_net: list[str] = field(default_factory=list)
    expired: list[str] = field(default_factory=list)
    auto_picked: list[str] = field(default_factory=list)
    jobs_enqueued: list[tuple[str, str]] = field(default_factory=list)  # (kind, key), new only
    errors: list[str] = field(default_factory=list)


def default_tz() -> str:
    return os.environ.get("SCHEDULER_DEFAULT_TZ") or DEFAULT_TZ


def local_at(monday: date, days: int, at: time, tz: ZoneInfo) -> datetime:
    """The wall-clock moment ``monday + days`` at ``at`` in ``tz`` (aware)."""
    return datetime.combine(monday + timedelta(days=days), at, tzinfo=tz)


def target_monday(local_now: datetime) -> date | None:
    """The Monday of the week being planned, or None when planning has not started this week.

    From Friday 00:00 local to Sunday midnight the coming Monday is the target."""
    d = local_now.date()
    if d.weekday() < 4:
        return None
    return d + timedelta(days=7 - d.weekday())


def current_window(local_now: datetime, monday: date, tz: ZoneInfo) -> str | None:
    """Name of the latest notice window that has opened and not passed the print deadline."""
    if local_now >= local_at(monday, *PRINT_DEADLINE, tz):
        return None
    latest = None
    for name, days, at in WINDOWS:
        if local_now >= local_at(monday, days, at, tz):
            latest = name
    return latest


def auto_pick_option(plan) -> str:
    """The option chosen for a parent who did not pick. Random, but fixed per plan so a retry or a
    second scheduler picks the same one."""
    return random.Random(plan.plan_id).choice([o.option_id for o in plan.outlines.options])


def _enqueue(
    conn, report: TickReport, family_id: str, kind: str, key: str, payload: dict, now: datetime
) -> None:
    job, created = jobs.enqueue(conn, family_id, kind, key, payload, now=now)
    if created:
        report.jobs_enqueued.append((kind, key))


def _regen_suffix(conn: sqlite3.Connection, plan_id: str) -> str:
    n = conn.execute(
        "SELECT COUNT(*) FROM loop_event WHERE plan_id=? AND event_type='outlines_regenerate'",
        (plan_id,),
    ).fetchone()[0]
    return f":r{n}" if n else ""


def _family_tick(
    conn: sqlite3.Connection, family_id: str, tz_name: str | None, now: datetime, report: TickReport
) -> None:
    tz = ZoneInfo(tz_name or default_tz())
    local_now = now.astimezone(tz)
    now_iso = jobs.iso(now)
    monday = target_monday(local_now)
    window = current_window(local_now, monday, tz) if monday else None
    week = monday.isoformat() if monday else None

    kids = [
        r[0]
        for r in conn.execute(
            "SELECT student_id FROM student_profiles WHERE family_id=? ORDER BY student_id",
            (family_id,),
        )
    ]
    if monday:
        deadlines = dict(
            feedback_due_at=jobs.iso(local_at(monday, *CHECKIN[1:], tz)),
            pick_deadline=jobs.iso(local_at(monday, *PICK_DEADLINE, tz)),
            print_deadline=jobs.iso(local_at(monday, *PRINT_DEADLINE, tz)),
        )
        for sid in kids:
            existing = conn.execute(
                "SELECT plan_id FROM week_plan WHERE family_id=? AND student_id=? AND week_start=?",
                (family_id, sid, week),
            ).fetchone()
            if existing is None:
                plan = wp.create_plan(conn, family_id, sid, week, **deadlines)
                report.plans_created.append(plan.plan_id)
        # fill deadlines on a plan created elsewhere (e.g. by the This-week screen)
        conn.execute(
            "UPDATE week_plan SET feedback_due_at=COALESCE(feedback_due_at,?), "
            "pick_deadline=COALESCE(pick_deadline,?), print_deadline=COALESCE(print_deadline,?) "
            "WHERE family_id=? AND week_start=?",
            (
                deadlines["feedback_due_at"],
                deadlines["pick_deadline"],
                deadlines["print_deadline"],
                family_id,
                week,
            ),
        )
        conn.commit()

    conn.row_factory = sqlite3.Row
    plans = [
        wp.row_to_plan(r)
        for r in conn.execute(
            f"SELECT * FROM week_plan WHERE family_id=? AND status IN ({','.join('?' * len(OPEN_STATES))})"
            " ORDER BY week_start, student_id",
            (family_id, *OPEN_STATES),
        )
    ]

    for plan in plans:
        status = plan.status
        # 1. the pick deadline passed (any week; the deadline is on the plan). A parent who was too
        #    busy still gets a packet on Monday: one of the three outlines is chosen for them. With
        #    no outlines there is nothing to choose, so the week expires as before.
        if status == "awaiting_pick" and plan.pick_deadline and plan.pick_deadline <= now_iso:
            if plan.outlines is not None:
                res = loop_state.advance(
                    conn,
                    family_id,
                    plan.plan_id,
                    loop_state.Event(
                        "pick_made",
                        key=f"autopick:{plan.plan_id}",
                        payload={"option_id": auto_pick_option(plan), "source": "auto_pick"},
                    ),
                )
                if res.applied:
                    report.auto_picked.append(plan.plan_id)
                status = res.plan.status
            else:
                res = loop_state.advance(
                    conn,
                    family_id,
                    plan.plan_id,
                    loop_state.Event("pick_expired", key=f"expire:{plan.plan_id}"),
                )
                if res.applied:
                    report.expired.append(plan.plan_id)
                continue
        # 2. safety net: no check-in by Saturday 10:00 -> move on without it
        if (
            status == "awaiting_feedback"
            and plan.week_start == week
            and local_now >= local_at(monday, *NUDGE[1:], tz)
        ):
            res = loop_state.advance(
                conn,
                family_id,
                plan.plan_id,
                loop_state.Event(
                    "feedback_submitted",
                    key=f"safety_net:{plan.plan_id}",
                    payload={"source": "safety_net"},
                ),
            )
            if res.applied:
                report.safety_net.append(plan.plan_id)
            status = res.plan.status
        # 3. state-driven jobs (also repairs a feedback/pick endpoint that failed to enqueue)
        if status == "outlining":
            _enqueue(
                conn,
                report,
                family_id,
                "outline",
                f"outlines:{plan.plan_id}{_regen_suffix(conn, plan.plan_id)}",
                {"plan_id": plan.plan_id},
                now,
            )
        elif status == "authoring":
            fresh = wp.get_plan(conn, family_id, plan.plan_id)
            _enqueue(
                conn,
                report,
                family_id,
                "author",
                f"author:{plan.plan_id}:{fresh.picked_option}"
                f"{_regen_suffix(conn, plan.plan_id)}",
                {"plan_id": plan.plan_id, "option_id": fresh.picked_option},
                now,
            )

    # 4. notices: only the latest window, once per family per week
    if window and week:
        wanted = {
            "checkin": "awaiting_feedback",
            "nudge": "awaiting_pick",
            "lastcall": "awaiting_pick",
        }[window]
        ids = [
            r["plan_id"]
            for r in conn.execute(
                "SELECT plan_id FROM week_plan WHERE family_id=? AND week_start=? AND status=?"
                " ORDER BY plan_id",
                (family_id, week, wanted),
            )
        ]
        if ids:
            _enqueue(
                conn,
                report,
                family_id,
                "send_notice",
                f"{NOTICE_KEY_PREFIX[window]}:{family_id}:{week}",
                {"notice": window, "week_start": week, "plan_ids": ids},
                now,
            )


def tick(now: datetime, conn: sqlite3.Connection) -> TickReport:
    """Run one scheduler pass at the instant ``now`` (aware). Safe to call at any cadence."""
    if now.tzinfo is None:
        raise ValueError("tick(now): pass an aware datetime")
    report = TickReport()
    conn.row_factory = sqlite3.Row
    families = [
        (r["family_id"], r["timezone"])
        for r in conn.execute(
            "SELECT f.family_id, s.timezone FROM family f "
            "LEFT JOIN family_settings s ON s.family_id = f.family_id ORDER BY f.family_id"
        )
    ]
    for family_id, tz_name in families:
        try:
            _family_tick(conn, family_id, tz_name, now, report)
        except Exception as exc:  # one bad family must not stop the others
            if conn.in_transaction:
                conn.rollback()
            logger.exception("scheduler: family %s failed", family_id)
            report.errors.append(f"{family_id}: {type(exc).__name__}")
    return report


def run_forever(
    db_path: str, stop: threading.Event | None = None, interval: float | None = None
) -> None:
    stop = stop or threading.Event()
    interval = interval or float(os.environ.get("SCHEDULER_INTERVAL_SECONDS", "300"))
    conn = jobs.connect(db_path)
    logger.info("scheduler up: tick every %ss, default tz %s", interval, default_tz())
    while not stop.is_set():
        try:
            rep = tick(jobs.utcnow(), conn)
            if (
                rep.jobs_enqueued
                or rep.plans_created
                or rep.expired
                or rep.safety_net
                or rep.auto_picked
            ):
                logger.info("tick: %s", rep)
        except Exception:
            logger.exception("scheduler tick failed")
        stop.wait(interval)
    conn.close()


def main() -> int:
    import logging as _l
    import signal

    try:
        from .db_utils import get_db_path  # type: ignore
        from .migrations import apply_migrations  # type: ignore
    except ImportError:
        from db_utils import get_db_path  # type: ignore
        from migrations import apply_migrations  # type: ignore
    _l.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    db = get_db_path()
    apply_migrations(db)
    stop = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stop.set())
    run_forever(db, stop)
    return 0


if __name__ == "__main__":
    sys.exit(main())
