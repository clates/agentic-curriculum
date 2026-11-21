"""Migration 0008 and ensure_student: packets carry a real (family_id, student_id) FK (D2)."""

import sqlite3

import pytest

import src.db_utils as db_utils
from src.db_utils import ensure_student
from src.migrations import MIGRATIONS_DIR, apply_migrations

NOW = "2026-01-01T00:00:00Z"

PACKET = (
    "INSERT INTO weekly_packets (packet_id, student_id, grade_level, subject, week_of, status,"
    " payload_json, created_at, updated_at, family_id) "
    "VALUES (?, ?, 1, 'Math', '2026-01-05', 'ready', '{}', ?, ?, ?)"
)
FEEDBACK = (
    "INSERT INTO packet_feedback (packet_id, student_id, completed_at, family_id) "
    "VALUES (?, ?, ?, ?)"
)


def _conn(path):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@pytest.fixture()
def conn(tmp_path):
    db = tmp_path / "fk.db"
    apply_migrations(db)
    c = _conn(db)
    c.execute("INSERT INTO family VALUES ('fam_a', 'A', ?)", (NOW,))
    c.execute("INSERT INTO family VALUES ('fam_b', 'B', ?)", (NOW,))
    yield c
    c.close()


def test_packet_for_unknown_student_fails_at_db_level(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(PACKET, ("p1", "stu_ghost", NOW, NOW, "fam_a"))


def test_student_in_family_a_cannot_be_used_by_family_b_packet(conn):
    ensure_student("fam_a", "stu_1", conn)
    conn.execute(PACKET, ("p_ok", "stu_1", NOW, NOW, "fam_a"))  # own family works
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(PACKET, ("p_bad", "stu_1", NOW, NOW, "fam_b"))


def test_feedback_cannot_reference_unknown_or_foreign_student(conn):
    ensure_student("fam_a", "stu_1", conn)
    conn.execute(PACKET, ("p1", "stu_1", NOW, NOW, "fam_a"))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(FEEDBACK, ("p1", "stu_ghost", NOW, "fam_a"))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(FEEDBACK, ("p1", "stu_1", NOW, "fam_b"))


def test_deleting_a_student_cascades_to_packets_and_feedback(conn):
    ensure_student("fam_a", "stu_1", conn)
    conn.execute(PACKET, ("p1", "stu_1", NOW, NOW, "fam_a"))
    conn.execute(FEEDBACK, ("p1", "stu_1", NOW, "fam_a"))
    conn.execute("DELETE FROM student_profiles WHERE student_id = 'stu_1'")
    assert conn.execute("SELECT COUNT(*) FROM weekly_packets").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM packet_feedback").fetchone()[0] == 0


def test_ensure_student_is_idempotent_and_never_overwrites(conn):
    assert ensure_student("fam_a", "stu_1", conn) is True
    conn.execute('UPDATE student_profiles SET metadata_blob = \'{"name": "Ada"}\'')
    assert ensure_student("fam_a", "stu_1", conn) is False
    row = conn.execute("SELECT metadata_blob FROM student_profiles").fetchone()
    assert row[0] == '{"name": "Ada"}'


def test_ensure_student_does_not_take_over_another_familys_student(conn):
    ensure_student("fam_a", "stu_1", conn)
    with pytest.raises(sqlite3.IntegrityError):
        ensure_student("fam_b", "stu_1", conn)


def test_ensure_student_requires_an_existing_family(conn):
    with pytest.raises(sqlite3.IntegrityError):
        ensure_student("fam_nope", "stu_1", conn)


def test_ensure_student_standalone_connection(tmp_path, monkeypatch):
    db = tmp_path / "solo.db"
    apply_migrations(db)
    monkeypatch.setattr(db_utils, "DB_FILE", str(db))
    assert ensure_student("fam_local", "stu_x") is True
    assert ensure_student("fam_local", "stu_x") is False


def test_save_paths_create_a_minimal_profile_for_an_unseen_student(tmp_path, monkeypatch):
    import src.packet_store as ps
    from tests.factories import build_weekly_plan

    db = tmp_path / "save.db"
    monkeypatch.setattr(ps, "DB_FILE", str(db))
    monkeypatch.setattr(ps, "_SCHEMA_INITIALIZED", None)
    monkeypatch.setattr(db_utils, "DB_FILE", str(db))
    ps.save_weekly_packet(build_weekly_plan(student_id="stu_new"))
    c = _conn(db)
    assert c.execute(
        "SELECT family_id, progress_blob FROM student_profiles WHERE student_id='stu_new'"
    ).fetchone() == ("fam_local", '{"mastered_standards": [], "developing_standards": []}')
    c.close()


def test_0008_drops_orphan_packets_and_children_and_keeps_valid_ones(tmp_path):
    """Upgrade a 0007 database holding a packet without a profile (the old tolerated state)."""
    import shutil

    db = tmp_path / "up.db"
    d = tmp_path / "upto7"
    d.mkdir()
    for f in MIGRATIONS_DIR.glob("000[1-7]_*.sql"):
        shutil.copy(f, d / f.name)
    apply_migrations(db, d)
    c = _conn(db)
    c.execute("INSERT INTO student_profiles (student_id, family_id) VALUES ('good', 'fam_local')")
    c.execute(PACKET, ("p_good", "good", NOW, NOW, "fam_local"))
    c.execute(PACKET, ("p_orphan", "nobody", NOW, NOW, "fam_local"))
    c.execute(FEEDBACK, ("p_orphan", "nobody", NOW, "fam_local"))
    c.execute(
        "INSERT INTO daily_lessons (packet_id, day_label, lesson_plan_json, created_at) "
        "VALUES ('p_orphan', 'Mon', '{}', ?)",
        (NOW,),
    )
    c.commit()
    c.close()

    assert apply_migrations(db) == [8]
    c = _conn(db)
    assert [r[0] for r in c.execute("SELECT packet_id FROM weekly_packets")] == ["p_good"]
    assert c.execute("SELECT COUNT(*) FROM packet_feedback").fetchone()[0] == 0
    assert c.execute("SELECT COUNT(*) FROM daily_lessons").fetchone()[0] == 0
    assert c.execute("PRAGMA foreign_key_check").fetchall() == []
    c.close()
