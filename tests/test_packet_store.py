import importlib
import json
import sqlite3
import sys
from pathlib import Path

import pytest


def _reload_modules(db_path: Path):
    """Reload db_utils and packet_store to point at the temp database."""
    env_value = str(db_path)
    # Ensure env var is set before reloads
    import os

    os.environ["CURRICULUM_DB_PATH"] = env_value

    db_utils_module = importlib.import_module("src.db_utils")
    importlib.reload(db_utils_module)

    if "src.packet_store" in sys.modules:
        del sys.modules["src.packet_store"]
    packet_store = importlib.import_module("src.packet_store")
    importlib.reload(packet_store)
    return packet_store


def _sample_weekly_plan():
    return {
        "plan_id": "plan_student_2025-11-24",
        "student_id": "student-123",
        "grade_level": 4,
        "subject": "Mathematics",
        "week_of": "2025-11-24",
        "weekly_overview": "Focus on multiplying fractions.",
        "daily_plan": [
            {
                "day": "Monday",
                "focus": "Intro",
                "lesson_plan": {"objective": "Learn", "procedure": ["Do"]},
                "standards": [{"standard_id": "MATH.4.1"}],
                "resources": {
                    "mathWorksheet": {
                        "title": "Warmup",
                        "artifacts": [
                            {
                                "type": "pdf",
                                "path": "artifacts/plan_student_2025-11-24/monday.pdf",
                                "size_bytes": 1024,
                                "sha256": "abc123",
                            },
                            {
                                "type": "png",
                                "path": "artifacts/plan_student_2025-11-24/monday.png",
                                "size_bytes": 2048,
                                "sha256": "def456",
                            },
                        ],
                    }
                },
                "worksheet_plans": [{"kind": "mathWorksheet", "filename_hint": "warmup"}],
                "resource_errors": [],
            },
            {
                "day": "Tuesday",
                "focus": "Apply",
                "lesson_plan": {"objective": "Practice", "procedure": ["Explain"]},
                "standards": [{"standard_id": "MATH.4.2"}],
                "resources": {
                    "readingWorksheet": {
                        "title": "Story",
                        "artifacts": [
                            {
                                "type": "pdf",
                                "path": "artifacts/plan_student_2025-11-24/tuesday.pdf",
                                "size_bytes": 512,
                                "sha256": "ghi789",
                            }
                        ],
                    }
                },
                "worksheet_plans": [{"kind": "readingWorksheet", "filename_hint": "story"}],
                "resource_errors": [],
            },
        ],
    }


def test_save_weekly_packet_persists_rows(tmp_path):
    db_path = tmp_path / "packets.db"
    packet_store = _reload_modules(db_path)

    weekly_plan = _sample_weekly_plan()
    packet_store.save_weekly_packet(weekly_plan)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    weekly_row = conn.execute("SELECT * FROM weekly_packets").fetchone()
    assert weekly_row is not None

    stored_payload = json.loads(weekly_row["payload_json"])  # type: ignore[index]
    assert stored_payload["plan_id"] == weekly_plan["plan_id"]
    summary = json.loads(weekly_row["summary_json"])  # type: ignore[index]
    assert summary["artifact_count"] == 3
    assert summary["worksheet_counts"]["mathWorksheet"] == 2

    daily_count = conn.execute("SELECT COUNT(*) FROM daily_lessons").fetchone()[0]
    assert daily_count == len(weekly_plan["daily_plan"])

    artifact_rows = conn.execute("SELECT * FROM worksheet_artifacts ORDER BY id").fetchall()
    assert len(artifact_rows) == 3
    assert artifact_rows[0]["file_format"] == "pdf"  # type: ignore[index]
    assert artifact_rows[0]["file_size_bytes"] == 1024  # type: ignore[index]
    assert artifact_rows[1]["checksum"] == "def456"  # type: ignore[index]

    conn.close()


def test_save_weekly_packet_rolls_back_on_error(tmp_path):
    db_path = tmp_path / "packets.db"
    packet_store = _reload_modules(db_path)

    def boom(*_args, **_kwargs):
        raise RuntimeError("boom")

    weekly_plan = _sample_weekly_plan()
    # Patch helper so it raises inside the transaction.
    original = packet_store._persist_daily_lessons
    packet_store._persist_daily_lessons = boom  # type: ignore[attr-defined]

    with pytest.raises(RuntimeError):
        packet_store.save_weekly_packet(weekly_plan)

    # Restore helper and verify nothing was written.
    packet_store._persist_daily_lessons = original  # type: ignore[attr-defined]
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    count = conn.execute("SELECT COUNT(*) FROM weekly_packets").fetchone()[0]
    assert count == 0
    conn.close()