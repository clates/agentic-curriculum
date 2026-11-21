"""M5.6: API-level journey for the Friday form: submit, mastery, review-due, summary, edit."""

import importlib
import json
import re
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SRC = str(Path(__file__).resolve().parents[1] / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


PID = "plan_journey"
STANDARDS = {
    "VA.MATH.2.a": ("Math", "The student will add within 100."),
    "VA.SCI.2.b": ("Science", "The student will describe the water cycle."),
    "VA.ELA.2.c": ("Reading", "The student will retell a story."),
}
CHECKS = [
    {"id": "math-1", "standard_id": "VA.MATH.2.a"},
    {"id": "math-2", "standard_id": "VA.MATH.2.a"},
    {"id": "sci-1", "standard_id": "VA.SCI.2.b"},
    {"id": "ela-1", "standard_id": "VA.ELA.2.c"},
]
JARGON = re.compile(r"VA\.|MASTERED|STRUGGLING|DEVELOPING|standard|mastery", re.I)


def _week_with_checks(checks):
    from tests.weekdoc_fixtures import minimal_week

    week = minimal_week()
    week["prep_checks"] = [
        {
            "id": c["id"],
            "day": "Monday",
            "standard_id": c["standard_id"],
            "kind": "oral",
            "prompt": "Ask.",
            "pass_criteria": "Gets it.",
        }
        for c in checks
    ]
    return week


@pytest.fixture()
def api(tmp_path, monkeypatch):
    db = tmp_path / "journey.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    for name in (
        "packet_store",
        "db_utils",
        "agent",
        "main",
        "feedback_service",
        "week_store",
        "src.week_store",
        "src.packet_store",
        "src.db_utils",
        "src.agent",
        "src.main",
        "src.feedback_service",
    ):
        sys.modules.pop(name, None)
    sys.modules["db_utils"] = importlib.import_module("src.db_utils")
    sys.modules["packet_store"] = importlib.import_module("src.packet_store")
    main = importlib.import_module("src.main")
    store = sys.modules["packet_store"]
    store.ensure_schema()
    conn = sqlite3.connect(db)
    for sid, (subject, desc) in STANDARDS.items():
        conn.execute(
            "INSERT INTO standards (standard_id, subject, description) VALUES (?, ?, ?)",
            (sid, subject, desc),
        )
    conn.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob)"
        " VALUES ('stu_throwaway', ?, '{}', ?)",
        (
            json.dumps({"mastered_standards": [], "developing_standards": []}),
            json.dumps({"name": "Pat Throwaway"}),
        ),
    )
    conn.commit()
    conn.close()
    sys.modules["week_store"] = importlib.import_module("src.week_store")
    sys.modules["week_store"].save_week(
        "stu_throwaway", PID, _week_with_checks(CHECKS), grade_level=2, week_of="2026-01-05"
    )
    triggers = []
    monkeypatch.setattr(main, "generate_trio_for_student", lambda sid: triggers.append(sid))
    return TestClient(main.app), triggers


def test_friday_journey(api):
    client, triggers = api
    base = "/students/stu_throwaway"

    # 1. Nothing recorded yet.
    first = client.get(f"{base}/progress-summary").json()
    assert "no progress recorded yet" in first["summary"]

    # 2. Submit: math all Got it, science Shaky, reading Missed.
    results = {"math-1": "got_it", "math-2": "got_it", "sci-1": "shaky", "ela-1": "missed"}
    r = client.post(
        f"{base}/weekly-packets/{PID}/feedback",
        json={"check_results": results, "workload": 1},
    )
    assert r.status_code == 204

    # 3. Raw results are kept; mastery was derived ("missed wins", no over-crediting).
    fb = client.get(f"{base}/weekly-packets/{PID}/feedback").json()
    assert fb["check_results"] == results
    assert fb["derived_mastery"] == {
        "VA.MATH.2.a": "MASTERED",
        "VA.SCI.2.b": "DEVELOPING",
        "VA.ELA.2.c": "STRUGGLING",
    }

    # 4. Plain-language summary; the missed skill is due now, the shaky one is not yet.
    s = client.get(f"{base}/progress-summary").json()
    assert [i["skill"] for i in s["needs_work"]] == ["Retell a story"]
    assert [i["skill"] for i in s["shaky"]] == ["Describe the water cycle"]
    assert [i["skill"] for i in s["due_for_review"]] == ["Retell a story"]
    assert s["student_name"] == "Pat"
    assert not JARGON.search(json.dumps(s))

    # 5. Shaky returns after a week (review-due policy, read from the stored progress).
    from src.review_policy import review_due

    conn = sqlite3.connect(_db_path())
    progress = conn.execute("SELECT progress_blob FROM student_profiles").fetchone()[0]
    conn.close()
    later = (datetime.now(UTC) + timedelta(days=8)).isoformat()
    assert {d["standard_id"] for d in review_due(progress, later)} >= {
        "VA.SCI.2.b",
        "VA.ELA.2.c",
    }

    # 6. Edit: the missed check was actually fine. Reverted and re-applied, not double counted.
    results["ela-1"] = "got_it"
    client.post(f"{base}/weekly-packets/{PID}/feedback", json={"check_results": results})
    s = client.get(f"{base}/progress-summary").json()
    assert s["needs_work"] == []
    assert {i["skill"] for i in s["solid"]} == {"Add within 100", "Retell a story"}
    fb = client.get(f"{base}/weekly-packets/{PID}/feedback").json()
    assert fb["version"] == 2 and fb["quantity_feedback"] is None
    conn = sqlite3.connect(_db_path())
    progress = json.loads(conn.execute("SELECT progress_blob FROM student_profiles").fetchone()[0])
    plan_rules = json.loads(
        conn.execute("SELECT plan_rules_blob FROM student_profiles").fetchone()[0]
    )
    conn.close()
    assert len(progress["standard_metadata"]["VA.ELA.2.c"]["feedback_history"]) == 1
    assert plan_rules["quantity_preferences"]["activity_bias"] == 0.0  # workload edit reverted

    # 7. Pressing save again with the same answers changes nothing and queues nothing.
    count = len(triggers)
    client.post(f"{base}/weekly-packets/{PID}/feedback", json={"check_results": results})
    assert len(triggers) == count
    assert client.get(f"{base}/weekly-packets/{PID}/feedback").json()["version"] == 2


def _db_path():
    import os

    return os.environ["CURRICULUM_DB_PATH"]
