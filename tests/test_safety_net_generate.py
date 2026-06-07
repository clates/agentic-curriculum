import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import safety_net_generate


def _make_db(tmp_path) -> Path:
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute(
        """
        CREATE TABLE weekly_packets (
            packet_id TEXT PRIMARY KEY,
            student_id TEXT,
            grade_level INTEGER,
            subject TEXT,
            week_of TEXT,
            status TEXT,
            payload_json TEXT,
            summary_json TEXT,
            updated_at TEXT,
            created_at TEXT
        )
    """
    )
    conn.execute(
        """
        CREATE TABLE packet_feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            packet_id TEXT,
            student_id TEXT,
            mastery_feedback TEXT,
            quantity_feedback INTEGER,
            completed_at TEXT
        )
    """
    )
    conn.commit()
    conn.close()
    return db


def test_finds_student_with_feedback_but_no_new_plan(tmp_path):
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO packet_feedback VALUES (1, 'pkt1', 's1', NULL, NULL, '2026-06-06T20:00:00Z')"
    )
    # No new packet after the feedback timestamp
    conn.execute(
        "INSERT INTO weekly_packets VALUES ('pkt1', 's1', 2, 'Math', '2026-06-01', 'active', '{}', '{}', '2026-06-01T00:00:00Z', '2026-06-01T00:00:00Z')"
    )
    conn.commit()
    conn.close()

    result = safety_net_generate.find_students_needing_plans(str(db))
    assert result == ["s1"]


def test_skips_student_who_already_has_new_plan(tmp_path):
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO packet_feedback VALUES (1, 'pkt1', 's1', NULL, NULL, '2026-06-06T18:00:00Z')"
    )
    # New packet created AFTER feedback
    conn.execute(
        "INSERT INTO weekly_packets VALUES ('pkt2', 's1', 2, 'Science', '2026-06-09', 'active', '{}', '{}', '2026-06-06T19:00:00Z', '2026-06-06T19:00:00Z')"
    )
    conn.commit()
    conn.close()

    result = safety_net_generate.find_students_needing_plans(str(db))
    assert result == []


def test_runs_trio_for_each_student(tmp_path):
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO packet_feedback VALUES (1, 'pkt1', 's1', NULL, NULL, '2026-06-06T20:00:00Z')"
    )
    conn.execute(
        "INSERT INTO packet_feedback VALUES (2, 'pkt2', 's2', NULL, NULL, '2026-06-06T20:00:00Z')"
    )
    conn.commit()
    conn.close()

    trio_calls = []
    with patch("safety_net_generate.generate_trio_for_student", side_effect=trio_calls.append):
        safety_net_generate.run(str(db))

    assert set(trio_calls) == {"s1", "s2"}


def test_skips_student_with_no_feedback(tmp_path):
    """Student with a packet but no feedback row is excluded."""
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE weekly_packets (id TEXT, student_id TEXT, created_at TEXT)")
    conn.execute(
        "CREATE TABLE packet_feedback (id TEXT, student_id TEXT, packet_id TEXT, completed_at TEXT)"
    )
    # Insert a packet but NO feedback row
    conn.execute("INSERT INTO weekly_packets VALUES ('p1', 's1', '2026-06-01T10:00:00')")
    conn.commit()
    conn.close()
    result = safety_net_generate.find_students_needing_plans(db_path)
    assert result == []
