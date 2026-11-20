"""M5.3b: feedback API v2 (check_results or quick_rating, plus workload)."""

import importlib
import json
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SRC = str(Path(__file__).resolve().parents[1] / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from tests.factories import build_weekly_plan  # noqa: E402

PID = "plan_v2"
CHECKS = [
    {"id": "c1", "standard_id": "VA.MATH.2.a"},
    {"id": "c2", "standard_id": "VA.MATH.2.a"},
    {"id": "c3", "standard_id": "VA.SCI.2.b"},
]


@pytest.fixture()
def env(tmp_path, monkeypatch):
    db = tmp_path / "v2.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    for name in list(sys.modules):
        if name in ("packet_store", "db_utils", "agent", "main", "feedback_service") or (
            name.startswith("src.") and name != "src.migrations"
        ):
            sys.modules.pop(name, None)
    sys.modules["db_utils"] = importlib.import_module("src.db_utils")
    sys.modules["packet_store"] = importlib.import_module("src.packet_store")
    main = importlib.import_module("src.main")
    store = sys.modules["packet_store"]
    store.ensure_schema()
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob)"
        " VALUES ('s1', ?, '{}', '{}')",
        (json.dumps({"mastered_standards": [], "developing_standards": []}),),
    )
    conn.commit()
    conn.close()
    plan = build_weekly_plan(plan_id=PID, student_id="s1")
    plan["prep_checks"] = CHECKS
    store.save_weekly_packet(plan)
    triggers = []
    monkeypatch.setattr(main, "generate_trio_for_student", lambda sid: triggers.append(sid))
    return TestClient(main.app), db, triggers


def _post(client, body):
    return client.post(f"/students/s1/weekly-packets/{PID}/feedback", json=body)


def _student(db):
    conn = sqlite3.connect(db)
    row = conn.execute("SELECT progress_blob, plan_rules_blob FROM student_profiles").fetchone()
    return json.loads(row[0]), json.loads(row[1])


def test_check_results_update_mastery_and_keep_raw(env):
    client, db, _ = env
    body = {"check_results": {"c1": "got_it", "c2": "got_it", "c3": "shaky"}}
    assert _post(client, body).status_code == 204
    progress, _ = _student(db)
    assert progress["mastered_standards"] == ["VA.MATH.2.a"]
    assert progress["developing_standards"] == ["VA.SCI.2.b"]
    fb = client.get(f"/students/s1/weekly-packets/{PID}/feedback").json()
    assert fb["check_results"] == body["check_results"]
    assert fb["derived_mastery"] == {"VA.MATH.2.a": "MASTERED", "VA.SCI.2.b": "DEVELOPING"}
    assert fb["version"] == 1


def test_exact_repeat_changes_nothing_and_does_not_retrigger(env):
    client, db, triggers = env
    body = {"check_results": {"c1": "got_it", "c3": "missed"}, "workload": 1}
    _post(client, body)
    before = _student(db)
    _post(client, body)
    assert _student(db) == before
    assert triggers == ["s1"]  # once, not twice
    assert client.get(f"/students/s1/weekly-packets/{PID}/feedback").json()["version"] == 1


def test_edit_reverts_then_applies_without_double_counting(env):
    client, db, triggers = env
    _post(
        client, {"check_results": {"c1": "got_it", "c2": "got_it", "c3": "got_it"}, "workload": 2}
    )
    _post(
        client, {"check_results": {"c1": "missed", "c2": "got_it", "c3": "got_it"}, "workload": 2}
    )
    progress, plan_rules = _student(db)
    assert progress["mastered_standards"] == ["VA.SCI.2.b"]
    assert progress["developing_standards"] == ["VA.MATH.2.a"]
    history = progress["standard_metadata"]["VA.MATH.2.a"]["feedback_history"]
    assert [h["rating"] for h in history] == ["STRUGGLING"]
    assert plan_rules["quantity_preferences"]["activity_bias"] == 0.3  # applied once
    assert len(triggers) == 2
    assert client.get(f"/students/s1/weekly-packets/{PID}/feedback").json()["version"] == 2


def test_edit_that_drops_workload_reverts_it(env):
    client, db, _ = env
    _post(client, {"quick_rating": "smooth", "workload": 2})
    _post(client, {"quick_rating": "smooth"})
    _, plan_rules = _student(db)
    assert plan_rules["quantity_preferences"]["activity_bias"] == 0.0


def test_quick_rating_never_credits_mastery(env):
    client, db, _ = env
    _post(client, {"quick_rating": "smooth"})
    progress, _ = _student(db)
    assert progress["mastered_standards"] == []
    _post(client, {"quick_rating": "rough"})
    progress, _ = _student(db)
    assert sorted(progress["developing_standards"]) == ["VA.MATH.2.a", "VA.SCI.2.b"]
    assert all(m["last_feedback"] == "STRUGGLING" for m in progress["standard_metadata"].values())


def test_both_evidence_kinds_rejected(env):
    client, db, _ = env
    r = _post(client, {"check_results": {"c1": "got_it"}, "quick_rating": "smooth"})
    assert r.status_code == 422
    r = _post(client, {"check_results": {"c1": "got_it"}, "mastery_feedback": {"X.1": "MASTERED"}})
    assert r.status_code == 422


@pytest.mark.parametrize(
    "body",
    [
        {"check_results": {"nope": "got_it"}},
        {"check_results": {"c1": "great"}},
        {"quick_rating": "amazing"},
        {"workload": 5},
    ],
)
def test_bad_values_are_400_and_change_nothing(env, body):
    client, db, triggers = env
    before = _student(db)
    assert _post(client, body).status_code == 400
    assert _student(db) == before and triggers == []


def test_unknown_packet_and_student(env):
    client, _, _ = env
    r = client.post("/students/s1/weekly-packets/nope/feedback", json={"quick_rating": "mixed"})
    assert r.status_code == 404
    r = client.post(f"/students/ghost/weekly-packets/{PID}/feedback", json={"workload": 0})
    assert r.status_code == 404


def test_failure_mid_apply_rolls_everything_back(env, monkeypatch):
    client, db, triggers = env
    _post(client, {"check_results": {"c1": "got_it", "c2": "got_it"}, "workload": 1})
    before = _student(db)
    svc = sys.modules["feedback_service"] if "feedback_service" in sys.modules else None
    svc = svc or importlib.import_module("src.feedback_service")

    def boom(*a, **k):
        raise RuntimeError("disk on fire")

    monkeypatch.setattr(svc, "process_quantity_feedback", boom)
    with pytest.raises(RuntimeError):
        _post(client, {"check_results": {"c1": "missed"}, "workload": -1})
    assert _student(db) == before
    fb = client.get(f"/students/s1/weekly-packets/{PID}/feedback").json()
    assert fb["check_results"] == {"c1": "got_it", "c2": "got_it"} and fb["version"] == 1
