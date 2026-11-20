"""Tests for migration 0002 (tenancy schema + backfill, M7.2)."""

import sqlite3

import pytest

from src.migrations import apply_migrations

NOW = "2026-01-01T00:00:00Z"


def _conn(path):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _seed_pre_tenancy(path):
    """Build a DB at version 0001 holding rows, as an existing install would."""
    d = path.parent / "only0001"
    d.mkdir(exist_ok=True)
    src = __import__("src.migrations", fromlist=["MIGRATIONS_DIR"]).MIGRATIONS_DIR
    (d / "0001_baseline.sql").write_text((src / "0001_baseline.sql").read_text())
    apply_migrations(path, d)
    conn = _conn(path)
    conn.execute("INSERT INTO student_profiles VALUES ('s1', '{}', '{}', '{}')")
    conn.execute(
        "INSERT INTO weekly_packets VALUES ('p1','s1',2,'Math','2026-01-05','ready',NULL,NULL,"
        "'{}',?,?)",
        (NOW, NOW),
    )
    conn.execute(
        "INSERT INTO daily_lessons (packet_id, day_label, lesson_plan_json, created_at) "
        "VALUES ('p1','Mon','{}',?)",
        (NOW,),
    )
    conn.execute(
        "INSERT INTO packet_feedback (packet_id, student_id, completed_at, quantity_feedback) "
        "VALUES ('p1','s1',?,1)",
        (NOW,),
    )
    conn.commit()
    conn.close()


def test_existing_rows_backfill_to_fam_local(tmp_path):
    db = tmp_path / "x.db"
    _seed_pre_tenancy(db)
    assert apply_migrations(db)[0] == 2  # later migrations (0004 week_documents...) follow
    conn = _conn(db)
    for table in (
        "student_profiles",
        "weekly_packets",
        "daily_lessons",
        "packet_feedback",
    ):
        rows = conn.execute(f"SELECT DISTINCT family_id FROM {table}").fetchall()
        assert rows == [("fam_local",)], table
    assert conn.execute("SELECT family_id FROM family").fetchall() == [("fam_local",)]
    assert conn.execute("SELECT quantity_feedback FROM packet_feedback").fetchall() == [(1,)]


def test_fresh_db_and_existing_db_have_same_tables(tmp_path):
    a, b = tmp_path / "a.db", tmp_path / "b.db"
    apply_migrations(a)
    _seed_pre_tenancy(b)
    apply_migrations(b)

    def shape(p):
        c = sqlite3.connect(p)
        return sorted(r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'"))

    assert shape(a) == shape(b)
    assert {
        "family",
        "parent_user",
        "auth_identity",
        "session",
        "auth_challenge",
        "audit_log",
    } <= set(shape(a))


def test_inserts_without_family_id_default_to_fam_local(tmp_path):
    db = tmp_path / "x.db"
    apply_migrations(db)
    conn = _conn(db)
    conn.execute("INSERT INTO student_profiles (student_id) VALUES ('s9')")
    assert conn.execute("SELECT family_id FROM student_profiles").fetchone() == ("fam_local",)


def test_foreign_keys_enforced(tmp_path):
    db = tmp_path / "x.db"
    apply_migrations(db)
    conn = _conn(db)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO student_profiles (student_id, family_id) VALUES ('s', 'fam_nope')"
        )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO parent_user (user_id, family_id, role, created_at) "
            "VALUES ('usr_1', 'fam_nope', 'owner', ?)",
            (NOW,),
        )


def test_family_with_many_users_and_identities(tmp_path):
    db = tmp_path / "x.db"
    apply_migrations(db)
    conn = _conn(db)
    conn.execute("INSERT INTO family VALUES ('fam_a', 'A', ?)", (NOW,))
    for uid, role in (("usr_1", "owner"), ("usr_2", "member")):
        conn.execute(
            "INSERT INTO parent_user (user_id, family_id, role, created_at) VALUES (?,?,?,?)",
            (uid, "fam_a", role, NOW),
        )
    for iid, prov, subj in (("i1", "email_code", "a@x"), ("i2", "google", "g-1")):
        conn.execute(
            "INSERT INTO auth_identity (identity_id, user_id, provider, subject, created_at) "
            "VALUES (?, 'usr_1', ?, ?, ?)",
            (iid, prov, subj, NOW),
        )
    with pytest.raises(sqlite3.IntegrityError):  # same provider+subject twice
        conn.execute(
            "INSERT INTO auth_identity (identity_id, user_id, provider, subject, created_at) "
            "VALUES ('i3', 'usr_2', 'google', 'g-1', ?)",
            (NOW,),
        )
    with pytest.raises(sqlite3.IntegrityError):  # bad role
        conn.execute(
            "INSERT INTO parent_user (user_id, family_id, role, created_at) "
            "VALUES ('usr_3','fam_a','admin',?)",
            (NOW,),
        )


def test_feedback_family_must_match_packet_family(tmp_path):
    db = tmp_path / "x.db"
    apply_migrations(db)
    conn = _conn(db)
    conn.execute("INSERT INTO family VALUES ('fam_b', 'B', ?)", (NOW,))
    conn.execute(
        "INSERT INTO weekly_packets (packet_id, student_id, grade_level, subject, week_of, status,"
        " payload_json, created_at, updated_at) VALUES ('p','s',1,'M','w','ready','{}',?,?)",
        (NOW, NOW),
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO packet_feedback (packet_id, student_id, completed_at, family_id) "
            "VALUES ('p','s',?, 'fam_b')",
            (NOW,),
        )
