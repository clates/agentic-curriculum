import importlib
import json
import os
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

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
    "main",
    "src.packet_store",
    "src.db_utils",
    "src.agent",
    "src.main",
    "trio_generator",
    "src.trio_generator",
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
            mastery_feedback_blob TEXT,
            quantity_feedback INTEGER,
            completed_at TEXT
        )
    """
    )
    conn.commit()
    conn.close()


@pytest.fixture()
def automation_client(tmp_path, monkeypatch):
    db_path = tmp_path / "auto.db"
    _bootstrap_db(db_path)
    os.environ["CURRICULUM_DB_PATH"] = str(db_path)

    for name in MODULE_NAMES_TO_CLEAR:
        sys.modules.pop(name, None)

    db_utils = importlib.import_module("src.db_utils")
    sys.modules["db_utils"] = db_utils
    packet_store = importlib.import_module("src.packet_store")
    sys.modules["packet_store"] = packet_store

    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO student_profiles VALUES (?, ?, ?, ?)",
        (
            "s1",
            json.dumps({"mastered_standards": [], "developing_standards": []}),
            json.dumps({}),
            json.dumps({"name": "Test Kid"}),
        ),
    )
    conn.execute(
        "INSERT INTO weekly_packets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "pkt1",
            "s1",
            2,
            "Math",
            "2026-06-01",
            "active",
            json.dumps({}),
            json.dumps({}),
            "2026-06-01T00:00:00Z",
            "2026-06-01T00:00:00Z",
        ),
    )
    conn.commit()
    conn.close()

    main_module = importlib.import_module("src.main")
    importlib.reload(main_module)
    yield TestClient(main_module.app)


def test_feedback_submission_queues_trio_generation(automation_client):
    trio_calls = []

    def fake_trio(student_id):
        trio_calls.append(student_id)

    with patch("src.main.generate_trio_for_student", fake_trio):
        resp = automation_client.post(
            "/students/s1/weekly-packets/pkt1/feedback",
            json={"mastery_feedback": {"MATH.1": "MASTERED"}, "quantity_feedback": 0},
        )

    assert resp.status_code == 204
    assert trio_calls == ["s1"]
