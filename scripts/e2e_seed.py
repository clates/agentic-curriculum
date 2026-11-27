#!/usr/bin/env python3
"""
CLI seed helper for Playwright E2E tests.

Usage:
  python scripts/e2e_seed.py create_packet <student_id> <packet_id>
  python scripts/e2e_seed.py set_progress <student_id>
  python scripts/e2e_seed.py backdate_feedback <packet_id> <iso_timestamp>
  python scripts/e2e_seed.py create_week <student_id> <packet_id>
  python scripts/e2e_seed.py check_in <student_id> <packet_id>
  python scripts/e2e_seed.py create_plan <student_id> <loop_status> [week_start]
  python scripts/e2e_seed.py expire_plan <student_id>
  python scripts/e2e_seed.py loop_events <student_id>

The DB path is controlled by CURRICULUM_DB_PATH (same env var the backend uses).
"""

import json
import os
import sqlite3
import sys
from pathlib import Path

# Allow importing from src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from packet_store import save_weekly_packet  # noqa: E402
from ingest_standards import (
    STANDARDS_DIR,
    create_database,
    ingest_standards_from_json,
)  # noqa: E402


def _db_path() -> str:
    return os.environ.get("CURRICULUM_DB_PATH", str(PROJECT_ROOT / "curriculum.db"))


def create_packet(student_id: str, packet_id: str) -> None:
    """Seed a minimal ready packet owned by student_id."""
    plan = {
        "plan_id": packet_id,
        "student_id": student_id,
        "grade_level": 3,
        "subject": "Mathematics",
        "week_of": "2026-01-06",
        "weekly_overview": "E2E test packet — multiplying fractions.",
        "daily_plan": [
            {
                "day": "Monday",
                "focus": "Introduction",
                "lesson_plan": {
                    "objective": "Understand fractions",
                    "procedure": ["Read introduction", "Do examples"],
                },
                "standards": [{"standard_id": "MATH.3.1"}],
                "resources": {
                    "mathWorksheet": {
                        "title": "Warmup",
                        "artifacts": [
                            {
                                "type": "pdf",
                                "path": f"artifacts/{packet_id}/monday.pdf",
                                "size_bytes": 1024,
                                "sha256": "abc123",
                            }
                        ],
                    }
                },
                "worksheet_plans": [{"kind": "mathWorksheet", "filename_hint": "warmup"}],
                "resource_errors": [],
            },
            {
                "day": "Tuesday",
                "focus": "Practice",
                "lesson_plan": {
                    "objective": "Apply fraction rules",
                    "procedure": ["Complete worksheet"],
                },
                "standards": [{"standard_id": "MATH.3.2"}],
                "resources": {
                    "readingWorksheet": {
                        "title": "Story Problems",
                        "artifacts": [
                            {
                                "type": "pdf",
                                "path": f"artifacts/{packet_id}/tuesday.pdf",
                                "size_bytes": 512,
                                "sha256": "def456",
                            }
                        ],
                    }
                },
                "worksheet_plans": [{"kind": "readingWorksheet", "filename_hint": "story"}],
                "resource_errors": [],
            },
        ],
    }
    save_weekly_packet(plan, status="ready")
    print(f"created packet {packet_id} for student {student_id}")


def create_week(student_id: str, packet_id: str, week_of: str = "2026-01-06") -> None:
    """Seed a ready structured week (the weather-week fixture, 10 prep checks)."""
    import week_store  # noqa: E402

    fixture = PROJECT_ROOT / "tests" / "fixtures" / "weekdoc" / "weather_week.json"
    week = json.loads(fixture.read_text(encoding="utf-8"))
    week_store.save_week(student_id, packet_id, week, grade_level=0, week_of=week_of)
    print(f"created structured week {packet_id} for student {student_id}")


def init_db() -> None:
    """Reset the test DB to a clean state: fresh schema plus the real standards data."""
    db = _db_path()
    if os.path.exists(db):
        os.remove(db)
    create_database()
    # Real standards, so the progress map and plan generation have a curriculum to work with.
    ingest_standards_from_json(STANDARDS_DIR)
    from packet_store import ensure_schema  # noqa: E402

    ensure_schema()
    print(f"initialized DB at {db}")


def set_progress(student_id: str) -> None:
    """Give a student a believable progress record from real standards: two going well, one
    shaky and one needing work, all checked within the last four weeks."""
    import re
    from datetime import UTC, datetime, timedelta

    from feedback_processor import process_mastery_feedback  # noqa: E402

    conn = sqlite3.connect(_db_path())
    try:
        rows = conn.execute(
            "SELECT standard_id, description FROM standards WHERE grade_level = 2 "
            "AND subject IN ('Math', 'Mathematics', 'Science') ORDER BY standard_id"
        ).fetchall()
        # Short, plain descriptions only, so the seeded screen reads like real life.
        clean = [
            sid
            for sid, desc in rows
            if desc
            and 20 < len(desc) < 90
            and not re.search(r"standard|schema|api|json", desc, re.I)
        ]
        if len(clean) < 4:
            raise SystemExit("not enough standards to seed progress")
        a, b, c, d = clean[:4]
        now = datetime.now(UTC)

        def day(n):
            return (now - timedelta(days=n)).isoformat(timespec="seconds").replace("+00:00", "Z")

        blob = json.dumps({"mastered_standards": [], "developing_standards": []})
        blob = process_mastery_feedback(blob, {a: "MASTERED", b: "MASTERED"}, day(9), "e2e_p1")
        blob = process_mastery_feedback(blob, {c: "DEVELOPING"}, day(3), "e2e_p2")
        blob = process_mastery_feedback(blob, {d: "STRUGGLING"}, day(2), "e2e_p3")
        conn.execute(
            "UPDATE student_profiles SET progress_blob = ? WHERE student_id = ?", (blob, student_id)
        )
        conn.commit()
    finally:
        conn.close()
    print(f"progress seeded for {student_id}")


_PLAN_PATH = {
    "awaiting_feedback": [],
    "outlining": ["feedback_submitted"],
    "awaiting_pick": ["feedback_submitted", "outlines_ready"],
    "expired": ["feedback_submitted", "outlines_ready", "pick_expired"],
    "authoring": ["feedback_submitted", "outlines_ready", "pick_made"],
    "ready": ["feedback_submitted", "outlines_ready", "pick_made", "authoring_done"],
    "printed": [
        "feedback_submitted",
        "outlines_ready",
        "pick_made",
        "authoring_done",
        "marked_printed",
    ],
}


def create_plan(
    student_id: str, status: str, week_start: str = "2026-01-05", family_id: str = "fam_local"
) -> None:
    """Create the student's week plan and walk it to ``status`` with legal loop events."""
    import week_plan as wp  # noqa: E402
    from loop_state import Event, advance  # noqa: E402
    from outline_models import OutlineSet  # noqa: E402

    # Three different topics wrapping the SAME skills (the engine's set), like the real thing.
    seeded = {
        "a": (
            "Garden Planner Week",
            "Plant, count and sketch a tiny garden.",
            "Gardening",
        ),
        "b": (
            "Kitchen Math Lab",
            "Measure, mix and bake your way through real numbers.",
            "Baking",
        ),
        "c": (
            "Mountain Climb Diary",
            "Plan a trail to the very top and record the climb.",
            "Mountains",
        ),
    }

    def outline(i):
        title, hook, topic = seeded[i]
        return {
            "option_id": i,
            "title": title,
            "hook": hook,
            "topic": topic,
            "standard_ids": ["VA.MATH.2.1"],
            "activities": "Short hands-on tasks each day, with a little reading and writing.",
            "skills": ["Counting and measuring", "Reading short passages"],
        }

    conn = sqlite3.connect(_db_path())
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        plan = wp.create_plan(conn, family_id, student_id, week_start)
        for kind in _PLAN_PATH[status]:
            payload = {}
            if kind == "outlines_ready":
                wp.store_outlines(
                    conn,
                    family_id,
                    plan.plan_id,
                    OutlineSet.model_validate(
                        {
                            "options": [
                                outline("a"),
                                outline("b"),
                                outline("c"),
                            ]
                        }
                    ),
                )
            elif kind == "pick_made":
                payload = {"option_id": "b"}
            elif kind == "authoring_done":
                payload = {"packet_id": f"e2e_{student_id}"}
            advance(conn, family_id, plan.plan_id, Event(kind, payload=payload))
    finally:
        conn.close()
    print(f"plan for {student_id} is {status}")


def expire_plan(student_id: str) -> None:
    """Let the child's open ideas run out of time (awaiting_pick -> expired)."""
    import week_plan as wp  # noqa: E402
    from loop_state import Event, advance  # noqa: E402

    conn = sqlite3.connect(_db_path())
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        plan = wp.latest_plan_for_student(conn, "fam_local", student_id)
        advance(conn, "fam_local", plan.plan_id, Event("pick_expired"))
    finally:
        conn.close()
    print(f"plan for {student_id} expired")


def loop_events(student_id: str) -> None:
    """Print the loop events recorded for the child's latest plan as JSON."""
    import week_plan as wp  # noqa: E402

    conn = sqlite3.connect(_db_path())
    try:
        plan = wp.latest_plan_for_student(conn, "fam_local", student_id)
        rows = conn.execute(
            "SELECT event_type, from_status, to_status, payload_json, event_key FROM loop_event "
            "WHERE plan_id = ? ORDER BY event_id",
            (plan.plan_id,),
        ).fetchall()
    finally:
        conn.close()
    print(
        json.dumps(
            [
                {"type": t, "from": f, "to": to, "payload": json.loads(p or "{}"), "key": k}
                for t, f, to, p, k in rows
            ]
        )
    )


def backdate_feedback(packet_id: str, iso_timestamp: str) -> None:
    """Set completed_at on a packet's feedback row to iso_timestamp."""
    db = _db_path()
    conn = sqlite3.connect(db)
    try:
        conn.execute(
            "UPDATE packet_feedback SET completed_at = ? WHERE packet_id = ?",
            (iso_timestamp, packet_id),
        )
        conn.commit()
    finally:
        conn.close()
    print(f"backdated feedback for {packet_id} to {iso_timestamp}")


def check_in(student_id: str, packet_id: str) -> None:
    """Store a feedback row for the week, without the API's follow-on plan generation."""
    from packet_store import save_packet_feedback  # noqa: E402

    save_packet_feedback(student_id, packet_id, None, 0)
    print(f"checked in {packet_id} for student {student_id}")


def llm_usage(student_id: str) -> None:
    """Print the llm_usage ledger rows for a student as JSON."""
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT task, model, prompt_tokens, completion_tokens, cost_usd, status "
            "FROM llm_usage WHERE student_id = ? ORDER BY created_at",
            (student_id,),
        ).fetchall()
    finally:
        conn.close()
    print(json.dumps([dict(r) for r in rows]))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init_db":
        init_db()

    elif cmd == "create_packet":
        if len(sys.argv) != 4:
            print("Usage: e2e_seed.py create_packet <student_id> <packet_id>")
            sys.exit(1)
        create_packet(sys.argv[2], sys.argv[3])

    elif cmd == "backdate_feedback":
        if len(sys.argv) != 4:
            print("Usage: e2e_seed.py backdate_feedback <packet_id> <iso_timestamp>")
            sys.exit(1)
        backdate_feedback(sys.argv[2], sys.argv[3])

    elif cmd == "set_progress":
        if len(sys.argv) != 3:
            print("Usage: e2e_seed.py set_progress <student_id>")
            sys.exit(1)
        set_progress(sys.argv[2])

    elif cmd == "create_week":
        if len(sys.argv) not in (4, 5):
            print("Usage: e2e_seed.py create_week <student_id> <packet_id> [week_of]")
            sys.exit(1)
        create_week(*sys.argv[2:])

    elif cmd == "check_in":
        if len(sys.argv) != 4:
            print("Usage: e2e_seed.py check_in <student_id> <packet_id>")
            sys.exit(1)
        check_in(sys.argv[2], sys.argv[3])

    elif cmd == "expire_plan":
        expire_plan(sys.argv[2])

    elif cmd == "loop_events":
        loop_events(sys.argv[2])

    elif cmd == "create_plan":
        if len(sys.argv) not in (4, 5):
            print("Usage: e2e_seed.py create_plan <student_id> <loop_status> [week_start]")
            sys.exit(1)
        create_plan(*sys.argv[2:])

    elif cmd == "llm_usage":
        if len(sys.argv) != 3:
            print("Usage: e2e_seed.py llm_usage <student_id>")
            sys.exit(1)
        llm_usage(sys.argv[2])

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
