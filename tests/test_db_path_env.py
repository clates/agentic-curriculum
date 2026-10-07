"""Regression: every DB reader must honor CURRICULUM_DB_PATH (container volume), not
PROJECT_ROOT/curriculum.db."""

import importlib
import json
import logging
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = str(PROJECT_ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

MODULES = [
    "packet_store",
    "db_utils",
    "agent",
    "src.packet_store",
    "src.db_utils",
    "src.agent",
    "src.main",
    "main",
]


def _build_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE standards (standard_id TEXT PRIMARY KEY, source TEXT, subject TEXT,"
        " grade_level INTEGER, description TEXT, json_blob TEXT)"
    )
    conn.execute(
        "CREATE TABLE student_profiles (student_id TEXT PRIMARY KEY, progress_blob TEXT,"
        " plan_rules_blob TEXT, metadata_blob TEXT)"
    )
    for i in range(3):
        conn.execute(
            "INSERT INTO standards VALUES (?, 'SOL', 'Math', 1, ?, '{}')",
            (f"MA.1.{i}", f"Math standard {i}"),
        )
    conn.execute(
        "INSERT INTO student_profiles VALUES ('kid', ?, '{}', '{}')",
        (json.dumps({"mastered_standards": ["MA.1.0"], "developing_standards": ["MA.1.1"]}),),
    )
    conn.commit()
    conn.close()


@pytest.fixture
def env_db(tmp_path, monkeypatch):
    db = tmp_path / "volume" / "curriculum.db"
    db.parent.mkdir()
    _build_db(db)
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    for name in MODULES:
        sys.modules.pop(name, None)
    sys.modules["db_utils"] = importlib.import_module("src.db_utils")
    sys.modules["packet_store"] = importlib.import_module("src.packet_store")
    sys.modules["agent"] = importlib.import_module("src.agent")
    main = importlib.import_module("src.main")
    return main, db


def test_get_db_path_reads_env_at_call_time(monkeypatch, tmp_path):
    import db_utils

    monkeypatch.setenv("CURRICULUM_DB_PATH", str(tmp_path / "a.db"))
    assert db_utils.get_db_path() == str(tmp_path / "a.db")
    monkeypatch.delenv("CURRICULUM_DB_PATH")
    assert db_utils.get_db_path() == str(PROJECT_ROOT / "curriculum.db")


def test_curriculum_graph_endpoint_uses_env_db(env_db):
    main, _ = env_db
    data = TestClient(main.app).get("/curriculum/graph/Math").json()
    assert len(data["nodes"]) == 3


def test_progress_map_endpoint_uses_env_db(env_db):
    main, _ = env_db
    resp = TestClient(main.app).get("/students/kid/progress-map/Math?prune=false")
    assert resp.status_code == 200
    assert len(resp.json()["nodes"]) == 3


def test_subject_picker_uses_env_db(env_db, monkeypatch):
    subject_picker = importlib.reload(importlib.import_module("subject_picker"))

    seen = []
    real = subject_picker.load_from_db

    def spy(db_path, subject_keyword=None):
        seen.append(db_path)
        return real(db_path, subject_keyword=subject_keyword)

    monkeypatch.setattr(subject_picker, "load_from_db", spy)
    assert subject_picker.pick_subjects("kid")[0] == "Math"  # MA.1.1 developing
    assert seen and all(p == str(env_db[1]) for p in seen)


def test_load_from_db_does_not_create_missing_db(tmp_path):
    from curriculum_graph import load_from_db

    missing = tmp_path / "nope.db"
    with pytest.raises(FileNotFoundError):
        load_from_db(str(missing), "Math")
    assert not missing.exists()


def test_load_from_db_logs_error_when_no_standards(tmp_path, caplog):
    from curriculum_graph import load_from_db

    empty = tmp_path / "empty.db"
    sqlite3.connect(empty).close()
    with caplog.at_level(logging.ERROR):
        graph = load_from_db(str(empty), "Math")
    assert len(graph.graph.nodes) == 0
    assert "no standards found" in caplog.text
