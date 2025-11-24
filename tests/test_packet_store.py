import importlib
import json
import sqlite3
import sys
from pathlib import Path

import pytest
from .factories import build_weekly_plan


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


def test_save_weekly_packet_persists_rows(tmp_path):
    db_path = tmp_path / "packets.db"
    packet_store = _reload_modules(db_path)

    weekly_plan = build_weekly_plan()
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

    weekly_plan = build_weekly_plan()
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


def test_list_weekly_packets_supports_pagination(tmp_path):
    db_path = tmp_path / "packets.db"
    packet_store = _reload_modules(db_path)

    newer = build_weekly_plan(plan_id="plan_newer", week_of="2025-12-01")
    older = build_weekly_plan(plan_id="plan_older", week_of="2025-11-17")
    packet_store.save_weekly_packet(newer)
    packet_store.save_weekly_packet(older)

    items, has_more = packet_store.list_weekly_packets("student-123", limit=1)
    assert has_more is True
    assert len(items) == 1
    assert items[0]["packet_id"] == "plan_newer"
    assert items[0]["worksheet_counts"]["mathWorksheet"] == 2

    items_page_2, has_more_second = packet_store.list_weekly_packets(
        "student-123",
        limit=1,
        offset=1,
    )
    assert has_more_second is False
    assert items_page_2[0]["packet_id"] == "plan_older"


def test_get_weekly_packet_returns_payload_and_etag(tmp_path):
    db_path = tmp_path / "packets.db"
    packet_store = _reload_modules(db_path)

    plan = build_weekly_plan(plan_id="plan_detail")
    packet_store.save_weekly_packet(plan)

    result = packet_store.get_weekly_packet("student-123", "plan_detail")
    assert result is not None
    assert result["payload"]["plan_id"] == "plan_detail"
    assert result["etag"]


def test_list_packet_artifacts_enforces_ownership(tmp_path):
    db_path = tmp_path / "packets.db"
    packet_store = _reload_modules(db_path)

    plan = build_weekly_plan(plan_id="plan_artifacts", student_id="student-xyz")
    packet_store.save_weekly_packet(plan)

    owned = packet_store.list_packet_artifacts("student-xyz", "plan_artifacts")
    assert owned is not None
    assert len(owned) == 3
    assert owned[0]["artifact_id"] > 0

    unauthorized = packet_store.list_packet_artifacts("student-123", "plan_artifacts")
    assert unauthorized is None


def test_get_artifact_for_student_returns_none_when_mismatch(tmp_path):
    db_path = tmp_path / "packets.db"
    packet_store = _reload_modules(db_path)

    plan = build_weekly_plan(plan_id="plan_artifacts", student_id="student-xyz")
    packet_store.save_weekly_packet(plan)

    artifacts = packet_store.list_packet_artifacts("student-xyz", "plan_artifacts")
    assert artifacts is not None
    first_id = artifacts[0]["artifact_id"]

    owned = packet_store.get_artifact_for_student("student-xyz", first_id)
    assert owned is not None
    assert owned["artifact_id"] == first_id

    mismatch = packet_store.get_artifact_for_student("student-123", first_id)
    assert mismatch is None