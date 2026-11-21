"""M5.3a: raw check results stored as the source of truth, with a real upsert."""

import importlib
import sqlite3

import pytest

from tests.factories import build_weekly_plan


@pytest.fixture()
def store(tmp_path, monkeypatch):
    db = tmp_path / "fb.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    import src.db_utils as db_utils
    import src.packet_store as packet_store

    importlib.reload(db_utils)
    importlib.reload(packet_store)
    packet_store.ensure_schema()
    packet_store.save_weekly_packet(build_weekly_plan(student_id="s1"))
    yield packet_store, db


def _pid(store):
    return build_weekly_plan(student_id="s1")["plan_id"]


def test_raw_results_round_trip(store):
    ps, _ = store
    ps.save_packet_feedback(
        "s1",
        _pid(store),
        {"S.a": "MASTERED"},
        1,
        check_results={"c1": "got_it", "c2": "shaky"},
        derived_mastery={"S.a": "DEVELOPING"},
    )
    fb = ps.get_packet_feedback("s1", _pid(store))
    assert fb["check_results"] == {"c1": "got_it", "c2": "shaky"}
    assert fb["derived_mastery"] == {"S.a": "DEVELOPING"}
    assert fb["quantity_feedback"] == 1
    assert fb["quick_rating"] is None and fb["version"] == 1


def test_upsert_keeps_one_row_and_bumps_version(store):
    ps, db = store
    v1 = ps.save_packet_feedback("s1", _pid(store), None, 0, quick_rating="smooth")
    v2 = ps.save_packet_feedback("s1", _pid(store), None, -1, quick_rating="rough")
    assert (v1, v2) == (1, 2)
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM packet_feedback").fetchone()[0] == 1
    fb = ps.get_packet_feedback("s1", _pid(store))
    assert fb["quick_rating"] == "rough" and fb["quantity_feedback"] == -1


def test_edit_replaces_raw_results(store):
    ps, _ = store
    ps.save_packet_feedback("s1", _pid(store), None, None, check_results={"c1": "missed"})
    ps.save_packet_feedback("s1", _pid(store), None, None, quick_rating="mixed")
    fb = ps.get_packet_feedback("s1", _pid(store))
    assert fb["check_results"] is None and fb["quick_rating"] == "mixed"


def test_unknown_packet_rejected(store):
    ps, _ = store
    with pytest.raises(ValueError):
        ps.save_packet_feedback("s1", "nope", None, 1)


def test_migration_dedupes_old_duplicate_rows(tmp_path):
    from pathlib import Path

    from src.migrations import MIGRATIONS_DIR, apply_migrations

    d = tmp_path / "m"
    d.mkdir()
    for name in ("0001_baseline.sql", "0002_tenancy.sql"):
        (d / name).write_text((Path(MIGRATIONS_DIR) / name).read_text())
    db = tmp_path / "old.db"
    apply_migrations(db, d)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO weekly_packets (packet_id, student_id, grade_level, subject, week_of, status,"
        " payload_json, created_at, updated_at) VALUES ('p','s',1,'M','w','ready','{}','t','t')"
    )
    for q in (1, 2):
        conn.execute(
            "INSERT INTO packet_feedback (packet_id, student_id, completed_at, quantity_feedback)"
            " VALUES ('p','s','t',?)",
            (q,),
        )
    conn.commit()
    conn.close()
    (d / "0005_feedback.sql").write_text((Path(MIGRATIONS_DIR) / "0005_feedback.sql").read_text())
    apply_migrations(db, d)
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT quantity_feedback, version FROM packet_feedback").fetchall() == [
        (2, 1)
    ]
