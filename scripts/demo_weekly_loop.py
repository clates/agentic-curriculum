#!/usr/bin/env python3
"""Demo: two children move through the weekly loop on a simulated clock, on a throwaway DB.

Uses the real scheduler, queue and worker. The outline/author handlers registered here are DEMO
stand-ins that only advance the state machine (the real ones come from other streams); the
send_notice handler is the shipped stub. Run: venv/bin/python scripts/demo_weekly_loop.py
"""

import os
import sqlite3
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
os.environ["JOB_ALERTS_ENABLED"] = ""

import job_registry  # noqa: E402
import jobs  # noqa: E402
import loop_state as ls  # noqa: E402
import scheduler  # noqa: E402
import week_plan as wp  # noqa: E402
import worker as worker_mod  # noqa: E402
from migrations import apply_migrations  # noqa: E402
from outline_models import OutlineSet  # noqa: E402

FAM = "fam_local"
NY = ZoneInfo("America/New_York")


def _outlines() -> OutlineSet:
    def o(i, d):
        return {"option_id": i, "title": i, "hook": "h", "difficulty": d, "standard_ids": ["X.1"]}

    return OutlineSet.model_validate(
        {"options": [o("a", "easier"), o("b", "on_level"), o("c", "stretch")]}
    )


@job_registry.handler("outline")
def demo_outline(ctx):  # DEMO stand-in for the outline generator
    c = ctx.connect()
    pid = ctx.job.payload["plan_id"]
    wp.store_outlines(c, FAM, pid, _outlines())
    ls.advance(c, FAM, pid, ls.Event("outlines_ready", key=f"job:{ctx.job.id}"))


@job_registry.handler("author")
def demo_author(ctx):  # DEMO stand-in for the week author
    c = ctx.connect()
    pid = ctx.job.payload["plan_id"]
    ls.advance(
        c,
        FAM,
        pid,
        ls.Event("authoring_done", key=f"job:{ctx.job.id}", payload={"packet_id": "pk_demo"}),
    )


def main() -> None:
    tmp = tempfile.mkdtemp()
    db = os.path.join(tmp, "demo.db")
    apply_migrations(db)
    conn = jobs.connect(db)
    conn.execute(
        "INSERT INTO family_settings (family_id, timezone, updated_at) VALUES (?,?,?)",
        (FAM, "America/New_York", "2026-01-01T00:00:00Z"),
    )
    for sid in ("stu_a", "stu_b"):
        conn.execute(
            "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, "
            "metadata_blob, family_id) VALUES (?,'{}','{}','{}',?)",
            (sid, FAM),
        )
    conn.commit()
    w = worker_mod.Worker(db, poll_seconds=0.01)

    def snapshot(label: str, when: datetime) -> None:
        rep = scheduler.tick(when, conn)
        n = 0
        while w.run_once():
            n += 1
        rows = conn.execute(
            "SELECT student_id, status FROM week_plan ORDER BY student_id"
        ).fetchall()
        st = ", ".join(f"{r[0]}={r[1]}" for r in rows) or "(no plans yet)"
        new = [f"{k}:{key}" for k, key in rep.jobs_enqueued]
        print(f"{when.astimezone(NY):%a %Y-%m-%d %H:%M %Z} | {label}")
        print(f"    states: {st}")
        print(f"    enqueued: {new or '-'}  ran {n} job(s)  expired: {len(rep.expired)}")

    def plan(sid):
        r = conn.execute("SELECT plan_id FROM week_plan WHERE student_id=?", (sid,)).fetchone()
        return r[0]

    at = lambda d, h, m=0: datetime(2026, 3, d, h, m, tzinfo=NY)  # noqa: E731
    print("Week of Mon 2026-03-09 (the Sunday before is the US spring-forward day)\n")
    snapshot("Thursday: nothing yet", at(5, 12))
    snapshot("Friday 15:00: plans created, check-in reminder queued", at(6, 15))
    ls.advance(conn, FAM, plan("stu_a"), ls.Event("feedback_submitted", key="parent-checkin"))
    snapshot("Friday evening: stu_a checked in; outline job runs", at(6, 18))
    snapshot("Friday 18:01: tick again (idempotent)", at(6, 18, 1))
    snapshot("Saturday 10:00: stu_b has no check-in -> safety net; nudge for stu_a", at(7, 10))
    ls.advance(
        conn, FAM, plan("stu_a"), ls.Event("pick_made", key="pick-1", payload={"option_id": "b"})
    )
    snapshot("Saturday 10:30: stu_a picked option b; author job runs", at(7, 10, 30))
    snapshot("Sunday 08:00: last call (stu_b still has not picked)", at(8, 8))
    snapshot("Sunday 12:00 EDT: pick deadline; stu_b's options expire", at(8, 12))
    snapshot("Sunday 12:01: tick again (idempotent)", at(8, 12, 1))
    ls.advance(conn, FAM, plan("stu_a"), ls.Event("marked_printed", key="printed"))
    snapshot("Sunday 15:00: stu_a printed", at(8, 15))
    print("\nqueue:", jobs.status(conn)["counts"])
    print("jobs run:")
    for r in conn.execute("SELECT kind, idempotency_key, state, attempts FROM jobs ORDER BY id"):
        print("   ", tuple(r))
    _ = (UTC, sqlite3)


if __name__ == "__main__":
    main()
