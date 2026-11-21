"""Storage for structured weeks (M2.6)."""

from __future__ import annotations

import importlib
import json
import sqlite3
import sys
from pathlib import Path

import pytest

from tests.weekdoc_fixtures import minimal_week

FIXTURE = (
    Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "weekdoc" / "weather_week.json"
)


@pytest.fixture
def stores(tmp_path, monkeypatch):
    db = tmp_path / "w.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    for name in ("src.db_utils", "src.packet_store", "src.week_store"):
        sys.modules.pop(name, None)
    ps = importlib.import_module("src.packet_store")
    ws = importlib.import_module("src.week_store")
    return db, ps, ws


def _weather():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_save_writes_summary_document_and_check_index_together(stores):
    db, ps, ws = stores
    ws.save_week("stu_1", "pk1", _weather(), grade_level=0, week_of="2026-01-05")
    con = sqlite3.connect(db)
    assert con.execute("SELECT COUNT(*) FROM weekly_packets").fetchone()[0] == 1
    assert con.execute("SELECT COUNT(*) FROM week_documents").fetchone()[0] == 1
    assert con.execute("SELECT COUNT(*) FROM prep_checks").fetchone()[0] == 10
    fam, ver = con.execute("SELECT family_id, schema_version FROM week_documents").fetchone()
    assert (fam, ver) == ("fam_local", 1)
    assert {r[0] for r in con.execute("SELECT family_id FROM prep_checks")} == {"fam_local"}


def test_roundtrip_and_check_index_order(stores):
    _, _, ws = stores
    ws.save_week("stu_1", "pk1", _weather(), grade_level=0, week_of="2026-01-05")
    week = ws.get_week("stu_1", "pk1")
    assert week.title == "Weather Week" and len(week.days) == 5
    checks = ws.list_prep_checks("stu_1", "pk1")
    assert [c["check_id"] for c in checks][:3] == ["chk-1", "chk-2", "chk-3"]
    assert checks[0] == {
        "check_id": "chk-1",
        "day": "Monday",
        "standard_id": "VA.SCIENCE.K.k.8.a",
        "kind": "oral",
    }


def test_legacy_list_and_get_endpoints_see_the_week(stores):
    _, ps, ws = stores
    ws.save_week("stu_1", "pk1", _weather(), grade_level=0, week_of="2026-01-05")
    items, _ = ps.list_weekly_packets("stu_1", limit=10)
    assert items[0]["packet_id"] == "pk1" and items[0]["worksheet_counts"]["readingWorksheet"] == 6
    payload = ps.get_weekly_packet("stu_1", "pk1")["payload"]
    assert payload["plan_id"] == "pk1" and len(payload["daily_plan"]) == 5


def test_resave_replaces_document_and_checks(stores):
    db, _, ws = stores
    ws.save_week("stu_1", "pk1", _weather(), grade_level=0, week_of="2026-01-05")
    ws.save_week("stu_1", "pk1", minimal_week(), grade_level=0, week_of="2026-01-05")
    con = sqlite3.connect(db)
    assert con.execute("SELECT COUNT(*) FROM weekly_packets").fetchone()[0] == 1
    assert con.execute("SELECT COUNT(*) FROM prep_checks").fetchone()[0] == 1
    assert ws.get_week("stu_1", "pk1").title == "Tiny Week"


def test_invalid_week_writes_nothing(stores):
    db, ps, ws = stores
    ps.ensure_schema()
    bad = minimal_week()
    bad["days"][0]["worksheets"][0]["kind"] = "noSuchKind"
    with pytest.raises(ValueError):
        ws.save_week("stu_1", "pk1", bad, grade_level=0, week_of="2026-01-05")
    assert sqlite3.connect(db).execute("SELECT COUNT(*) FROM weekly_packets").fetchone()[0] == 0


def test_failure_mid_write_rolls_everything_back(stores, monkeypatch):
    db, ps, ws = stores
    real = ps._get_connection

    def exploding():
        conn = real()
        orig = conn.executemany
        conn_proxy = type(
            "C",
            (),
            {
                "__getattr__": lambda self, n: getattr(conn, n),
                "__enter__": lambda self: conn.__enter__(),
                "__exit__": lambda self, *a: conn.__exit__(*a),
                "executemany": lambda self, *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
            },
        )()
        return conn_proxy

    monkeypatch.setattr(ps, "_get_connection", exploding)
    with pytest.raises(RuntimeError, match="boom"):
        ws.save_week("stu_1", "pk1", minimal_week(), grade_level=0, week_of="2026-01-05")
    monkeypatch.setattr(ps, "_get_connection", real)
    con = sqlite3.connect(db)
    assert con.execute("SELECT COUNT(*) FROM weekly_packets").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM week_documents").fetchone()[0] == 0


def test_other_student_and_other_family_cannot_read_or_overwrite(stores):
    db, ps, ws = stores
    ws.save_week("stu_1", "pk1", minimal_week(), grade_level=0, week_of="2026-01-05")
    assert ws.get_week("stu_2", "pk1") is None
    assert ws.get_week("stu_1", "pk1", family_id="fam_other") is None
    assert ws.list_prep_checks("stu_2", "pk1") == []
    with pytest.raises(ws.PacketOwnershipError):
        ws.save_week("stu_2", "pk1", minimal_week(), grade_level=0, week_of="2026-01-05")
    assert ws.get_week("stu_1", "pk1").title == "Tiny Week"


def test_older_schema_version_is_upgraded_on_read(stores, monkeypatch):
    db, _, ws = stores
    ws.save_week("stu_1", "pk1", minimal_week(), grade_level=0, week_of="2026-01-05")
    # Pretend the code moved to v2 with a v1->v2 migration; the row on disk is still v1.
    import src.weekdoc.versioning as v

    real_model = v.WeekDoc

    class V2Stub:
        @staticmethod
        def model_validate(data):
            assert data["schema_version"] == 2 and data["migrated"] is True
            data = {k: x for k, x in data.items() if k != "migrated"}
            return real_model.model_validate({**data, "schema_version": 1})

    monkeypatch.setattr(v, "SCHEMA_VERSION", 2)
    monkeypatch.setattr(
        v, "MIGRATIONS", {1: lambda d: {**d, "schema_version": 2, "migrated": True}}
    )
    monkeypatch.setattr(v, "WeekDoc", V2Stub)
    stored = json.loads(
        sqlite3.connect(db).execute("SELECT doc_json FROM week_documents").fetchone()[0]
    )
    assert stored["schema_version"] == 1
    assert ws.get_week("stu_1", "pk1").title == "Tiny Week"


def test_newer_schema_version_on_disk_is_rejected(stores):
    db, _, ws = stores
    ws.save_week("stu_1", "pk1", minimal_week(), grade_level=0, week_of="2026-01-05")
    con = sqlite3.connect(db)
    doc = json.loads(con.execute("SELECT doc_json FROM week_documents").fetchone()[0])
    doc["schema_version"] = 99
    con.execute("UPDATE week_documents SET doc_json = ?", (json.dumps(doc),))
    con.commit()
    from src.weekdoc import WeekVersionError

    with pytest.raises(WeekVersionError, match="newer"):
        ws.get_week("stu_1", "pk1")


def test_migration_0004_is_registered():
    from src.migrations import discover

    assert 4 in [v for v, _, _ in discover()]
