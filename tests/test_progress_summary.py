"""M5.5: plain-language progress summary."""

import importlib
import json
import re
import sqlite3
import sys

import pytest
from fastapi.testclient import TestClient

from pathlib import Path

SRC = str(Path(__file__).resolve().parents[1] / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from src.feedback_processor import process_mastery_feedback  # noqa: E402
from src.progress_summary import build_progress_summary, skill_label  # noqa: E402

NOW = "2026-02-02T12:00:00Z"
STANDARDS = {
    "VA.MATH.2.a": {"subject": "Math", "description": "The student will add within 100."},
    "VA.MATH.2.b": {"subject": "Math", "description": "The student will subtract within 100."},
    "VA.SCI.2.c": {
        "subject": "Science",
        "description": "The student will describe the water cycle.",
    },
    "VA.ELA.2.d": {"subject": "Reading", "description": "The student will retell a story."},
}
BLANK = json.dumps({"mastered_standards": [], "developing_standards": []})
JARGON = re.compile(r"VA\.|MASTERED|STRUGGLING|DEVELOPING|standard|mastery|node|prereq", re.I)


def _progress():
    b = BLANK
    b = process_mastery_feedback(b, {"VA.MATH.2.a": "MASTERED"}, "2026-01-12T10:00:00Z", "p1")
    b = process_mastery_feedback(b, {"VA.MATH.2.b": "DEVELOPING"}, "2026-01-30T10:00:00Z", "p2")
    b = process_mastery_feedback(
        b, {"VA.SCI.2.c": "STRUGGLING", "VA.ELA.2.d": "MASTERED"}, "2026-02-01T10:00:00Z", "p3"
    )
    return b


def test_skill_label_is_human():
    assert skill_label("The student will add within 100.") == "Add within 100"
    assert skill_label("") == "A skill we have been working on"
    long = "The student will " + "explain the very long thing " * 10
    assert len(skill_label(long)) <= 91


def test_summary_groups_and_has_no_jargon():
    s = build_progress_summary("Maya Rivers", _progress(), STANDARDS, NOW)
    assert s["student_name"] == "Maya"
    assert [i["skill"] for i in s["solid"]] == ["Retell a story"]  # math.a is due for a refresher
    assert [i["skill"] for i in s["shaky"]] == ["Subtract within 100"]
    assert [i["skill"] for i in s["needs_work"]] == ["Describe the water cycle"]
    due = {i["skill"]: i["why"] for i in s["due_for_review"]}
    assert "Describe the water cycle" in due and "Add within 100" in due
    assert s["last_four_weeks"]["skills_checked"] == 4
    assert not JARGON.search(json.dumps(s)), json.dumps(s)
    assert "Maya has" in s["summary"]


def test_empty_progress_is_friendly():
    s = build_progress_summary("Maya", None, {}, NOW)
    assert "no progress recorded yet" in s["summary"]
    assert s["solid"] == s["shaky"] == s["needs_work"] == s["due_for_review"] == []


def test_unknown_standard_never_leaks_its_id():
    s = build_progress_summary("Maya", _progress(), {}, NOW)
    assert not JARGON.search(json.dumps(s))


def test_old_feedback_falls_out_of_last_four_weeks():
    s = build_progress_summary("Maya", _progress(), STANDARDS, "2026-04-01T00:00:00Z")
    assert s["last_four_weeks"]["skills_checked"] == 0


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db = tmp_path / "s.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    for name in (
        "packet_store",
        "db_utils",
        "agent",
        "src.packet_store",
        "src.db_utils",
        "src.agent",
        "src.main",
        "main",
    ):
        sys.modules.pop(name, None)
    sys.modules["db_utils"] = importlib.import_module("src.db_utils")
    main = importlib.import_module("src.main")
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE standards (standard_id TEXT PRIMARY KEY, source TEXT, subject TEXT,"
        " grade_level INTEGER, description TEXT, json_blob TEXT)"
    )
    conn.execute(
        "CREATE TABLE student_profiles (student_id TEXT PRIMARY KEY, progress_blob TEXT,"
        " plan_rules_blob TEXT, metadata_blob TEXT)"
    )
    for sid, info in STANDARDS.items():
        conn.execute(
            "INSERT INTO standards (standard_id, subject, description) VALUES (?,?,?)",
            (sid, info["subject"], info["description"]),
        )
    conn.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob)"
        " VALUES ('stu_1', ?, '{}', ?)",
        (_progress(), json.dumps({"name": "Maya Rivers"})),
    )
    conn.commit()
    conn.close()
    return TestClient(main.app)


def test_endpoint(client):
    r = client.get("/students/stu_1/progress-summary")
    assert r.status_code == 200
    body = r.json()
    assert body["student_name"] == "Maya"
    assert any(i["skill"] == "Describe the water cycle" for i in body["needs_work"])
    assert not JARGON.search(r.text)


def test_endpoint_404(client):
    assert client.get("/students/nope/progress-summary").status_code == 404
