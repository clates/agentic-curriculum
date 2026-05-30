#!/usr/bin/env python3
"""
CLI seed helper for Playwright E2E tests.

Usage:
  python scripts/e2e_seed.py create_packet <student_id> <packet_id>
  python scripts/e2e_seed.py backdate_feedback <packet_id> <iso_timestamp>

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
from ingest_standards import create_database  # noqa: E402


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
    """Reset the test DB to a clean state (delete file and recreate schema)."""
    db = _db_path()
    if os.path.exists(db):
        os.remove(db)
    create_database()
    from packet_store import ensure_schema  # noqa: E402

    ensure_schema()
    print(f"initialized DB at {db}")


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

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
