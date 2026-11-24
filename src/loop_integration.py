"""Joins the weekly loop to the app (M8 integration): check-in -> outlines, pick -> author.

The job queue, scheduler and state machine exist; this module is the glue on the web side. It does
three things, all behind ``LOOP_JOBS_ENABLED`` so a self-hosted or dev install behaves as before:

* ``on_feedback``  a check-in moves the child's waiting week plan on and queues the outline job,
                   without waiting for the scheduler's next tick.
* the pick hook    ``authoring_kickoff`` queues the author job instead of only recording intent.
* the keys         come from ``scheduler.outline_key`` / ``author_key``, the same ones the
                   scheduler uses, so a parent's pick, the auto-pick and the repair pass all map to
                   ONE job. Handlers are idempotent on top of that.
"""

from __future__ import annotations

import logging
import os
import sqlite3

try:
    from . import authoring_kickoff, jobs, loop_state, scheduler, week_plan as wp  # type: ignore
    from .db_utils import get_db_path  # type: ignore
except ImportError:
    import authoring_kickoff  # type: ignore
    import jobs  # type: ignore
    import loop_state  # type: ignore
    import scheduler  # type: ignore
    import week_plan as wp  # type: ignore
    from db_utils import get_db_path  # type: ignore

logger = logging.getLogger(__name__)
LOCAL_FAMILY_ID = "fam_local"


def enabled() -> bool:
    return os.environ.get("LOOP_JOBS_ENABLED", "").strip().lower() in ("1", "true", "yes", "on")


def enqueue_outline(conn: sqlite3.Connection, family_id: str, plan_id: str) -> jobs.Job:
    return jobs.enqueue(
        conn, family_id, "outline", scheduler.outline_key(conn, plan_id), {"plan_id": plan_id}
    )[0]


def enqueue_author(conn: sqlite3.Connection, family_id: str, plan_id: str, option: str) -> jobs.Job:
    return jobs.enqueue(
        conn,
        family_id,
        "author",
        scheduler.author_key(conn, plan_id, option),
        {"plan_id": plan_id, "option_id": option},
        max_attempts=scheduler.AUTHOR_MAX_ATTEMPTS,
    )[0]


def _open() -> sqlite3.Connection:
    return jobs.connect(get_db_path())


def request_author_job(family_id: str, student_id: str, plan_id: str, option: str) -> None:
    """The pick hook. Idempotent: a repeat pick finds the job already there."""
    conn = _open()
    try:
        enqueue_author(conn, family_id, plan_id, option)
    finally:
        conn.close()


def on_feedback(family_id: str, student_id: str) -> None:
    """A check-in arrived: move this child's waiting week on and queue its outlines. Never raises
    (it runs after the parent's feedback was saved, and the scheduler repairs a miss)."""
    if not enabled():
        return
    try:
        conn = _open()
        try:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM week_plan WHERE family_id=? AND student_id=? "
                "AND status='awaiting_feedback' ORDER BY week_start DESC LIMIT 1",
                (family_id, student_id),
            ).fetchone()
            plan = wp.row_to_plan(row) if row else None
            if plan is None:
                return
            res = loop_state.advance(
                conn,
                family_id,
                plan.plan_id,
                loop_state.Event("feedback_submitted", key=f"feedback:{plan.plan_id}"),
            )
            if res.plan.status == "outlining":
                enqueue_outline(conn, family_id, plan.plan_id)
        finally:
            conn.close()
    except Exception:  # the scheduler's safety net and repair pass pick this up
        logger.exception("loop: could not advance the plan after a check-in")


def install() -> bool:
    """Point the pick hook at the job queue. Returns whether it did."""
    if not enabled():
        return False
    authoring_kickoff.set_authoring_requester(request_author_job)
    logger.info("loop jobs enabled: picks queue an author job")
    return True


# --- operator commands: python -m loop_integration seed-demo | start-week <student> ---------------

DEMO_STUDENT = "demo_child"


def seed_demo(conn: sqlite3.Connection) -> str:
    """Add a made-up child to the local family, to watch the loop with no real student data.
    Safe to repeat. Returns the student id."""
    import json

    conn.execute(
        "INSERT OR IGNORE INTO student_profiles (student_id, progress_blob, plan_rules_blob, "
        "metadata_blob, family_id) VALUES (?,?,?,?,?)",
        (
            DEMO_STUDENT,
            "{}",
            json.dumps(
                {"interests": ["dinosaurs", "space"], "parent_notes": "Short, hands-on tasks"}
            ),
            json.dumps({"name": "Demo", "grade_level": 2}),
            LOCAL_FAMILY_ID,
        ),
    )
    conn.commit()
    return DEMO_STUDENT


def next_monday(today) -> str:
    from datetime import timedelta

    return (today + timedelta(days=7 - today.weekday())).isoformat()


def start_week(
    conn: sqlite3.Connection, student_id: str, week_start: str, family_id: str = LOCAL_FAMILY_ID
) -> wp.WeekPlan:
    """Start this child's week now instead of waiting for Friday: make the plan if it is missing,
    skip the check-in, and queue the outlines. Safe to repeat."""
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT plan_id FROM week_plan WHERE family_id=? AND student_id=? AND week_start=?",
        (family_id, student_id, week_start),
    ).fetchone()
    if row is None:
        if not conn.execute(
            "SELECT 1 FROM student_profiles WHERE family_id=? AND student_id=?",
            (family_id, student_id),
        ).fetchone():
            raise SystemExit(f"no child {student_id!r} in family {family_id}")
        plan = wp.create_plan(conn, family_id, student_id, week_start)
    else:
        plan = wp.get_plan(conn, family_id, row["plan_id"])
    res = (
        loop_state.advance(
            conn,
            family_id,
            plan.plan_id,
            loop_state.Event("feedback_submitted", key=f"cli:{plan.plan_id}"),
        )
        if plan.status == "awaiting_feedback"
        else None
    )
    plan = res.plan if res else plan
    if plan.status == "outlining":
        enqueue_outline(conn, family_id, plan.plan_id)
    return plan


def main(argv: list[str] | None = None) -> int:
    import argparse
    from datetime import date

    ap = argparse.ArgumentParser(prog="python -m loop_integration")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed-demo", help="add a made-up child (no real data) to the local family")
    sw = sub.add_parser("start-week", help="start a child's week now: queue its outlines")
    sw.add_argument("student_id")
    sw.add_argument("--week", help="Monday of the week, YYYY-MM-DD (default: next Monday)")
    args = ap.parse_args(argv)
    try:
        from .migrations import apply_migrations  # type: ignore
    except ImportError:
        from migrations import apply_migrations  # type: ignore
    db = get_db_path()
    apply_migrations(db)
    conn = jobs.connect(db)
    try:
        if args.cmd == "seed-demo":
            print(f"child {seed_demo(conn)} is in the family. Next: start-week {DEMO_STUDENT}")
        else:
            plan = start_week(conn, args.student_id, args.week or next_monday(date.today()))
            print(f"plan {plan.plan_id} for week {plan.week_start}: {plan.status}")
            if plan.status == "outlining":
                print("outline job queued; the worker writes the three ideas (LOOP_JOBS_ENABLED=1)")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
