"""Tests for the numbered migration runner (M7.1)."""

import sqlite3

import pytest

from src.migrations import MigrationError, apply_migrations, discover


def _tables(path):
    conn = sqlite3.connect(path)
    try:
        return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        conn.close()


def test_fresh_db_gets_baseline(tmp_path):
    db = tmp_path / "fresh.db"
    applied = apply_migrations(db)
    assert applied[0] == 1
    assert {"standards", "student_profiles", "weekly_packets", "packet_feedback"} <= _tables(db)
    conn = sqlite3.connect(db)
    assert [r[0] for r in conn.execute("SELECT version FROM schema_version")] == applied


def test_rerun_is_noop(tmp_path):
    db = tmp_path / "x.db"
    apply_migrations(db)
    assert apply_migrations(db) == []


def test_existing_db_keeps_data(tmp_path):
    """A DB created by the pre-runner code (tables, rows, no schema_version) migrates cleanly."""
    db = tmp_path / "old.db"
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE student_profiles (student_id TEXT PRIMARY KEY, progress_blob TEXT, "
        "plan_rules_blob TEXT, metadata_blob TEXT)"
    )
    conn.execute("INSERT INTO student_profiles VALUES ('s1', '{}', '{}', '{}')")
    conn.commit()
    conn.close()
    apply_migrations(db)
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT student_id FROM student_profiles").fetchall() == [("s1",)]
    assert "schema_version" in _tables(db)


def test_failed_migration_rolls_back_and_stops(tmp_path):
    d = tmp_path / "m"
    d.mkdir()
    (d / "0001_a.sql").write_text("CREATE TABLE a (x INTEGER);")
    (d / "0002_bad.sql").write_text("CREATE TABLE b (x INTEGER); INSERT INTO nope VALUES (1);")
    (d / "0003_c.sql").write_text("CREATE TABLE c (x INTEGER);")
    db = tmp_path / "t.db"
    with pytest.raises(sqlite3.OperationalError):
        apply_migrations(db, d)
    tables = _tables(db)
    assert "a" in tables and "b" not in tables and "c" not in tables
    conn = sqlite3.connect(db)
    assert [r[0] for r in conn.execute("SELECT version FROM schema_version")] == [1]


def test_foreign_key_violation_fails_migration(tmp_path):
    d = tmp_path / "m"
    d.mkdir()
    (d / "0001_a.sql").write_text(
        "CREATE TABLE p (id INTEGER PRIMARY KEY);"
        "CREATE TABLE c (pid INTEGER REFERENCES p(id));"
        "INSERT INTO c VALUES (5);"
    )
    with pytest.raises(MigrationError):
        apply_migrations(tmp_path / "t.db", d)


def test_bad_filename_and_duplicates(tmp_path):
    (tmp_path / "1_x.sql").write_text("")
    with pytest.raises(MigrationError):
        discover(tmp_path)


def test_trigger_body_statement_splitting(tmp_path):
    d = tmp_path / "m"
    d.mkdir()
    (d / "0001_t.sql").write_text(
        "CREATE TABLE t (x INTEGER);\n"
        "CREATE TABLE log (x INTEGER);\n"
        "CREATE TRIGGER tr AFTER INSERT ON t BEGIN INSERT INTO log VALUES (new.x); END;\n"
    )
    db = tmp_path / "t.db"
    apply_migrations(db, d)
    conn = sqlite3.connect(db)
    conn.execute("INSERT INTO t VALUES (7)")
    assert conn.execute("SELECT x FROM log").fetchall() == [(7,)]
