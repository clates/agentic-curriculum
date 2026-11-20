#!/usr/bin/env python3
"""
CLI seed helper for Playwright E2E tests.

Usage:
  python scripts/e2e_seed.py create_packet <student_id> <packet_id>
  python scripts/e2e_seed.py backdate_feedback <packet_id> <iso_timestamp>
  python scripts/e2e_seed.py create_plan <student_id> <loop_status> [week_start]

The DB path is controlled by CURRICULUM_DB_PATH (same env var the backend uses).
"""

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


def create_plan(student_id: str, status: str, week_start: str = "2026-01-05") -> None:
    """Create the student's week plan and walk it to ``status`` with legal loop events."""
    import week_plan as wp  # noqa: E402
    from loop_state import Event, advance  # noqa: E402
    from outline_models import OutlineSet  # noqa: E402

    def outline(i, difficulty):
        return {
            "option_id": i,
            "title": f"Option {i}",
            "hook": "A week to explore",
            "difficulty": difficulty,
            "standard_ids": ["VA.MATH.2.1"],
        }

    conn = sqlite3.connect(_db_path())
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        plan = wp.create_plan(conn, "fam_local", student_id, week_start)
        for kind in _PLAN_PATH[status]:
            payload = {}
            if kind == "outlines_ready":
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
            elif kind == "pick_made":
                payload = {"option_id": "b"}
            elif kind == "authoring_done":
                payload = {"packet_id": f"e2e_{student_id}"}
            advance(conn, "fam_local", plan.plan_id, Event(kind, payload=payload))
    finally:
        conn.close()
    print(f"plan for {student_id} is {status}")


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

    elif cmd == "create_plan":
        if len(sys.argv) not in (4, 5):
            print("Usage: e2e_seed.py create_plan <student_id> <loop_status> [week_start]")
            sys.exit(1)
        create_plan(*sys.argv[2:])

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
