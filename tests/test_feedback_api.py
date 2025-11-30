import importlib
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = str(PROJECT_ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

MODULE_NAMES_TO_CLEAR = [
    "packet_store",
    "db_utils",
    "agent",
    "src.packet_store",
    "src.db_utils",
    "src.agent",
    "src.main",
    "main",
]


def _bootstrap_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE student_profiles (
            student_id TEXT PRIMARY KEY,
            progress_blob TEXT,
            plan_rules_blob TEXT,
            metadata_blob TEXT
        )
        """
    )
    conn.commit()
    conn.close()


@pytest.fixture()
def feedback_client(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "feedback.db"
    _bootstrap_db(db_path)

    os.environ["CURRICULUM_DB_PATH"] = str(db_path)
    for name in MODULE_NAMES_TO_CLEAR:
        sys.modules.pop(name, None)

    db_utils_module = importlib.import_module("src.db_utils")
    sys.modules["db_utils"] = db_utils_module
    packet_store = importlib.import_module("src.packet_store")
    sys.modules["packet_store"] = packet_store

    main_module = importlib.import_module("src.main")
    importlib.reload(main_module)

    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob) VALUES (?, ?, ?, ?)",
        (
            "student_01",
            json.dumps({"mastered_standards": [], "developing_standards": []}),
            json.dumps({}),
            json.dumps({}),
        ),
    )
    conn.commit()
    conn.close()

    packet_feedback_calls: list[tuple[str, str, dict[str, str] | None, int | None]] = []
    stored_feedback: dict[tuple[str, str], dict[str, Any]] = {}

    def fake_save(student_id: str, packet_id: str, mastery_feedback, quantity_feedback):
        packet_feedback_calls.append((student_id, packet_id, mastery_feedback, quantity_feedback))
        stored_feedback[(student_id, packet_id)] = {
            "packet_id": packet_id,
            "student_id": student_id,
            "completed_at": "2025-11-29T00:00:00Z",
            "mastery_feedback": mastery_feedback,
            "quantity_feedback": quantity_feedback,
        }

    def fake_get(student_id: str, packet_id: str):
        return stored_feedback.get((student_id, packet_id))

    monkeypatch.setattr(main_module, "save_packet_feedback", fake_save)
    monkeypatch.setattr(main_module, "get_packet_feedback", fake_get)

    client = TestClient(main_module.app)
    return client, packet_feedback_calls, stored_feedback, db_path


def test_submit_feedback_validates_mastery(feedback_client):
    client, _, _, _ = feedback_client

    response = client.post(
        "/students/student_01/weekly-packets/plan_123/feedback",
        json={"mastery_feedback": {"VA.MATH.K.1": "INVALID"}},
    )

    assert response.status_code == 400
    assert "Invalid mastery rating" in response.json()["detail"]


def test_submit_feedback_updates_blobs_and_calls_store(feedback_client):
    client, calls, _, db_path = feedback_client

    payload = {
        "mastery_feedback": {"VA.MATH.K.1": "MASTERED"},
        "quantity_feedback": 1,
    }
    response = client.post(
        "/students/student_01/weekly-packets/plan_abc/feedback",
        json=payload,
    )

    assert response.status_code == 204
    assert calls == [("student_01", "plan_abc", payload["mastery_feedback"], 1)]

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT progress_blob, plan_rules_blob FROM student_profiles WHERE student_id = ?",
        ("student_01",),
    ).fetchone()
    conn.close()
    progress = json.loads(row[0])
    plan_rules = json.loads(row[1])

    metadata = progress.get("standard_metadata", {}).get("VA.MATH.K.1")
    assert metadata is not None
    assert metadata["last_feedback"] == "MASTERED"
    assert "feedback_history" in metadata

    quantity_prefs = plan_rules.get("quantity_preferences")
    assert quantity_prefs is not None
    assert pytest.approx(quantity_prefs.get("activity_bias"), rel=1e-3) == 0.15


def test_get_feedback_returns_data(feedback_client):
    client, _, stored_feedback, _ = feedback_client
    stored_feedback[("student_01", "plan_xyz")] = {
        "packet_id": "plan_xyz",
        "student_id": "student_01",
        "completed_at": "2025-11-29T00:00:00Z",
        "mastery_feedback": {"VA.MATH.K.2": "DEVELOPING"},
        "quantity_feedback": -1,
    }

    response = client.get("/students/student_01/weekly-packets/plan_xyz/feedback")

    assert response.status_code == 200
    body = response.json()
    assert body["packet_id"] == "plan_xyz"
    assert body["quantity_feedback"] == -1


def test_get_feedback_404_when_missing(feedback_client):
    client, _, _, _ = feedback_client
    response = client.get("/students/student_01/weekly-packets/missing/feedback")
    assert response.status_code == 404
