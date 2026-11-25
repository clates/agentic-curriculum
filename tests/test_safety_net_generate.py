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
    conn.execute("""
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
            created_at TEXT,
            family_id TEXT NOT NULL DEFAULT 'fam_local'
        )
    """)
    conn.execute("""
        CREATE TABLE packet_feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            packet_id TEXT,
            student_id TEXT,
            mastery_feedback TEXT,
            quantity_feedback INTEGER,
            completed_at TEXT,
            family_id TEXT NOT NULL DEFAULT 'fam_local'
        )
    """)
    conn.commit()
    conn.close()
    return db


def test_finds_student_with_feedback_but_no_new_plan(tmp_path):
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO packet_feedback (feedback_id, packet_id, student_id,"
        " mastery_feedback, quantity_feedback, completed_at)"
        " VALUES (1, 'pkt1', 's1', NULL, NULL, '2026-06-06T20:00:00Z')"
    )
    # No new packet after the feedback timestamp
    conn.execute(
        "INSERT INTO weekly_packets (packet_id, student_id, grade_level, subject, week_of,"
        " status, payload_json, summary_json, updated_at, created_at)"
        " VALUES ('pkt1', 's1', 2, 'Math', '2026-06-01', 'active', '{}', '{}', '2026-06-01T00:00:00Z', '2026-06-01T00:00:00Z')"
    )
    conn.commit()
    conn.close()

    result = safety_net_generate.find_students_needing_plans(str(db))
    assert result == [("fam_local", "s1")]


def test_skips_student_who_already_has_new_plan(tmp_path):
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO packet_feedback (feedback_id, packet_id, student_id,"
        " mastery_feedback, quantity_feedback, completed_at)"
        " VALUES (1, 'pkt1', 's1', NULL, NULL, '2026-06-06T18:00:00Z')"
    )
    # New packet created AFTER feedback
    conn.execute(
        "INSERT INTO weekly_packets (packet_id, student_id, grade_level, subject, week_of,"
        " status, payload_json, summary_json, updated_at, created_at)"
        " VALUES ('pkt2', 's1', 2, 'Science', '2026-06-09', 'active', '{}', '{}', '2026-06-06T19:00:00Z', '2026-06-06T19:00:00Z')"
    )
    conn.commit()
    conn.close()

    result = safety_net_generate.find_students_needing_plans(str(db))
    assert result == []


def test_runs_trio_for_each_student(tmp_path):
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO packet_feedback (feedback_id, packet_id, student_id,"
        " mastery_feedback, quantity_feedback, completed_at)"
        " VALUES (1, 'pkt1', 's1', NULL, NULL, '2026-06-06T20:00:00Z')"
    )
    conn.execute(
        "INSERT INTO packet_feedback (feedback_id, packet_id, student_id,"
        " mastery_feedback, quantity_feedback, completed_at)"
        " VALUES (2, 'pkt2', 's2', NULL, NULL, '2026-06-06T20:00:00Z')"
    )
    conn.commit()
    conn.close()

    trio_calls = []
    with patch(
        "safety_net_generate.generate_trio_for_student",
        side_effect=lambda sid, fam: trio_calls.append((sid, fam)),
    ):
        safety_net_generate.run(str(db))

    assert set(trio_calls) == {("s1", "fam_local"), ("s2", "fam_local")}


def test_skips_student_with_no_feedback(tmp_path):
    """Student with a packet but no feedback row is excluded."""
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    # Insert a packet but NO feedback row
    conn.execute(
        "INSERT INTO weekly_packets (packet_id, student_id, grade_level, subject, week_of,"
        " status, payload_json, summary_json, updated_at, created_at)"
        " VALUES ('p1', 's1', 2, 'Math', '2026-06-01', 'active', '{}', '{}', '2026-06-01T10:00:00Z', '2026-06-01T10:00:00Z')"
    )
    conn.commit()
    conn.close()
    result = safety_net_generate.find_students_needing_plans(str(db))
    assert result == []


def test_error_in_one_student_does_not_block_others(tmp_path):
    """A RuntimeError for one student should not prevent processing of others."""
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO packet_feedback (feedback_id, packet_id, student_id,"
        " mastery_feedback, quantity_feedback, completed_at)"
        " VALUES (1, 'pkt1', 's1', NULL, NULL, '2026-06-06T20:00:00Z')"
    )
    conn.execute(
        "INSERT INTO packet_feedback (feedback_id, packet_id, student_id,"
        " mastery_feedback, quantity_feedback, completed_at)"
        " VALUES (2, 'pkt2', 's2', NULL, NULL, '2026-06-06T20:00:00Z')"
    )
    conn.commit()
    conn.close()

    calls = []

    def side_effect(student_id, family_id):
        if student_id == "s1":
            raise RuntimeError("s1 failed")
        calls.append(student_id)

    with patch("safety_net_generate.generate_trio_for_student", side_effect=side_effect):
        safety_net_generate.run(str(db))  # must not raise

    assert calls == ["s2"]


def test_created_family_is_matched_and_passed_through(tmp_path):
    """A created family's student is found by its own packets and generated in its own family;
    another family's newer packet for the same student id does not hide it."""
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO packet_feedback (feedback_id, packet_id, student_id, completed_at, family_id)"
        " VALUES (1, 'pkt1', 'stu_b', '2026-06-06T20:00:00Z', 'fam_b')"
    )
    conn.execute(
        "INSERT INTO weekly_packets (packet_id, student_id, created_at, family_id)"
        " VALUES ('pktA', 'stu_b', '2026-06-07T00:00:00Z', 'fam_local')"
    )
    conn.commit()
    conn.close()

    assert safety_net_generate.find_students_needing_plans(str(db)) == [("fam_b", "stu_b")]
    trio_calls = []
    with patch(
        "safety_net_generate.generate_trio_for_student",
        side_effect=lambda sid, fam: trio_calls.append((sid, fam)),
    ):
        safety_net_generate.run(str(db))
    assert trio_calls == [("stu_b", "fam_b")]

    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO weekly_packets (packet_id, student_id, created_at, family_id)"
        " VALUES ('pktB', 'stu_b', '2026-06-07T00:00:00Z', 'fam_b')"
    )
    conn.commit()
    conn.close()
    assert safety_net_generate.find_students_needing_plans(str(db)) == []
