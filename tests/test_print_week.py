"""The print screen's backend (M10.7): print-info, and marking a week printed."""

from __future__ import annotations

import importlib
import json
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tests.factories import build_weekly_plan

ROOT = Path(__file__).resolve().parents[1]
WEATHER = json.loads(
    (ROOT / "tests/fixtures/weekdoc/weather_week.json").read_text(encoding="utf-8")
)
PATH = [
    ("feedback_submitted", {}),
    ("outlines_ready", {}),
    ("pick_made", {"option_id": "a"}),
    ("authoring_done", {"packet_id": "pk1"}),
]


@pytest.fixture
def env(tmp_path, monkeypatch):
    db = tmp_path / "p.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    monkeypatch.syspath_prepend(str(ROOT / "src"))
    saved = dict(sys.modules)
    for name in list(sys.modules):
        if name in {
            "main",
            "db_utils",
            "packet_store",
            "week_store",
            "migrations",
        } or name.startswith(("weekdoc", "src.")):
            sys.modules.pop(name, None)
    main = importlib.import_module("main")
    importlib.import_module("packet_store").ensure_schema()
    dbu = importlib.import_module("db_utils")
    dbu.create_student("stu_1", {"name": "Zoe Quillfeather", "birthday": "2019-01-01"}, {})
    dbu.create_student("stu_2", {"name": "Sam", "birthday": "2019-01-01"}, {})
    yield TestClient(main.app), db
    # Leave the import state as we found it, so later tests see the modules they imported.
    sys.modules.clear()
    sys.modules.update(saved)


def _plan(db, student="stu_1", upto=4, marked=False):
    """A plan walked ``upto`` steps along the loop (4 = ready), optionally already printed."""
    from loop_state import Event, advance
    from outline_models import OutlineSet
    import week_plan as wp

    def o(i, d):
        return {
            "option_id": i,
            "title": i,
            "hook": "h",
            "difficulty": d,
            "standard_ids": ["VA.MATH.2.1"],
        }

    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = ON")
    plan = wp.create_plan(conn, "fam_local", student, "2026-01-05")
    for kind, payload in PATH[:upto]:
        if kind == "outlines_ready":
            wp.store_outlines(
                conn,
                "fam_local",
                plan.plan_id,
                OutlineSet.model_validate(
                    {"options": [o("a", "easier"), o("b", "on_level"), o("c", "stretch")]}
                ),
            )
        advance(conn, "fam_local", plan.plan_id, Event(kind, payload=payload))
    if marked:
        advance(conn, "fam_local", plan.plan_id, Event("marked_printed"))
    conn.close()
    return plan.plan_id


def _action(client, student):
    cards = client.get("/this-week").json()["children"]
    return next(c["next_action"] for c in cards if c["student_id"] == student)


def test_marking_a_ready_week_printed_turns_the_card_into_all_set(env):
    client, db = env
    pid = _plan(db)
    assert _action(client, "stu_1") == "print"
    res = client.post(f"/students/stu_1/week-plans/{pid}/printed")
    assert res.status_code == 200
    assert res.json() == {"plan_id": pid, "status": "printed", "already_printed": False}
    assert _action(client, "stu_1") == "done"


def test_marking_twice_is_a_harmless_repeat_and_records_one_event(env):
    client, db = env
    pid = _plan(db)
    url = f"/students/stu_1/week-plans/{pid}/printed"
    assert client.post(url).json()["already_printed"] is False
    again = client.post(url)
    assert again.status_code == 200
    assert again.json() == {"plan_id": pid, "status": "printed", "already_printed": True}
    conn = sqlite3.connect(db)
    n = conn.execute(
        "SELECT COUNT(*) FROM loop_event WHERE plan_id=? AND event_type='marked_printed'", (pid,)
    ).fetchone()[0]
    conn.close()
    assert n == 1


@pytest.mark.parametrize("upto", [0, 1, 2, 3])
def test_a_week_that_is_not_ready_is_a_clear_409_and_stays_put(env, upto):
    client, db = env
    pid = _plan(db, upto=upto)
    res = client.post(f"/students/stu_1/week-plans/{pid}/printed")
    assert res.status_code == 409
    assert "not ready to print" in res.json()["detail"]
    conn = sqlite3.connect(db)
    status = conn.execute("SELECT status FROM week_plan WHERE plan_id=?", (pid,)).fetchone()[0]
    conn.close()
    assert status != "printed"


def test_unknown_plan_and_another_childs_plan_are_404(env):
    client, db = env
    pid = _plan(db)
    assert client.post("/students/stu_1/week-plans/wp_nope/printed").status_code == 404
    assert client.post(f"/students/stu_2/week-plans/{pid}/printed").status_code == 404
    assert _action(client, "stu_1") == "print"  # untouched


def test_print_info_for_a_structured_week_lists_all_three_documents(env):
    client, _ = env
    importlib.import_module("week_store").save_week(
        "stu_1", "pk1", WEATHER, grade_level=0, week_of="2026-01-05"
    )
    body = client.get("/students/stu_1/weekly-packets/pk1/print-info").json()
    assert body == {
        "structured": True,
        "title": "Weather Week",
        "documents": ["packet", "guide", "prep"],
    }


def test_print_info_for_a_legacy_packet_lists_only_the_packet(env):
    client, _ = env
    importlib.import_module("packet_store").save_weekly_packet(
        build_weekly_plan(plan_id="pk1", student_id="stu_1")
    )
    body = client.get("/students/stu_1/weekly-packets/pk1/print-info").json()
    assert body["structured"] is False and body["documents"] == ["packet"]


def test_print_info_unknown_or_foreign_packet_is_404(env):
    client, _ = env
    assert client.get("/students/stu_1/weekly-packets/none/print-info").status_code == 404
    importlib.import_module("week_store").save_week(
        "stu_1", "pk1", WEATHER, grade_level=0, week_of="2026-01-05"
    )
    assert client.get("/students/stu_2/weekly-packets/pk1/print-info").status_code == 404
