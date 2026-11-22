#!/usr/bin/env python3
"""Seed for the print screen E2E (M10.7): a child whose week plan is walked to a loop state with
its plan pointing at a REAL stored week, so the print documents have content to open.

Usage:
  python scripts/e2e_seed_print.py week <student_id> <packet_id> <structured|legacy> \
      [status=ready] [week_start=2026-01-05] [print_deadline=]

``structured`` stores the weather WeekDoc (10 prep checks); ``legacy`` stores a packet with no
structured week. Kept apart from e2e_seed.py (shared with other streams); the DB path comes from
CURRICULUM_DB_PATH like every seed.
"""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e2e_seed  # noqa: E402

PATH = e2e_seed._PLAN_PATH


def seed_week(
    student_id: str,
    packet_id: str,
    kind: str,
    status: str = "ready",
    week_start: str = "2026-01-05",
    print_deadline: str = "",
) -> None:
    import week_plan as wp  # noqa: E402
    from loop_state import Event, advance  # noqa: E402
    from outline_models import OutlineSet  # noqa: E402

    if kind == "structured":
        e2e_seed.create_week(student_id, packet_id)
    elif kind == "legacy":
        e2e_seed.create_packet(student_id, packet_id)
    else:
        raise SystemExit("kind must be structured or legacy")

    def outline(i, difficulty):
        return {
            "option_id": i,
            "title": f"Option {i}",
            "hook": "A week to explore",
            "difficulty": difficulty,
            "standard_ids": ["VA.MATH.2.1"],
        }

    conn = sqlite3.connect(e2e_seed._db_path())
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        plan = wp.create_plan(
            conn, "fam_local", student_id, week_start, print_deadline=print_deadline or None
        )
        for event in PATH[status]:
            payload = {}
            if event == "outlines_ready":
                wp.store_outlines(
                    conn,
                    "fam_local",
                    plan.plan_id,
                    OutlineSet.model_validate(
                        {
                            "options": [
                                outline("a", "easier"),
                                outline("b", "on_level"),
                                outline("c", "stretch"),
                            ]
                        }
                    ),
                )
            elif event == "pick_made":
                payload = {"option_id": "b"}
            elif event == "authoring_done":
                payload = {"packet_id": packet_id}
            advance(conn, "fam_local", plan.plan_id, Event(event, payload=payload))
        print(plan.plan_id)
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 5 or sys.argv[1] != "week":
        print(__doc__)
        sys.exit(1)
    seed_week(*sys.argv[2:])
