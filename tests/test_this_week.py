"""Tests for the 'This week' read model and endpoint (M10.4)."""

import json
import sqlite3
from datetime import date

import pytest
from fastapi.testclient import TestClient

from src import week_plan as wp
from src.loop_state import Event, advance
from src.migrations import apply_migrations
from src.this_week import NEXT_ACTION, this_week_cards, upcoming_week_start


@pytest.fixture
def conn(tmp_path):
    db = tmp_path / "t.db"
    apply_migrations(db)
    c = sqlite3.connect(db)
    c.execute("PRAGMA foreign_keys = ON")
    c.execute("INSERT INTO family (family_id, name, created_at) VALUES ('fam_b','B','x')")
    for fam, stu, name in (
        ("fam_local", "stu_1", "Ada Lovelace"),
        ("fam_local", "stu_2", "Sam"),
        ("fam_b", "stu_9", "Other"),
    ):
        c.execute(
            "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, "
            "metadata_blob, family_id) VALUES (?,'{}','{}',?,?)",
            (stu, json.dumps({"name": name, "birthday": "2018-01-01"}), fam),
        )
    c.commit()
    yield c
    c.close()


def test_upcoming_week_start():
    assert upcoming_week_start(date(2026, 1, 7)) == "2026-01-05"  # Wednesday
    assert upcoming_week_start(date(2026, 1, 9)) == "2026-01-05"  # Friday
    assert upcoming_week_start(date(2026, 1, 10)) == "2026-01-12"  # Saturday


def test_every_status_has_a_next_action():
    assert set(NEXT_ACTION) == set(wp.STATUSES)


def test_new_children_get_a_check_in_card_and_first_names_only(conn):
    cards = this_week_cards(conn, "fam_local", date(2026, 1, 7))["children"]
    assert [(c["first_name"], c["next_action"]) for c in cards] == [
        ("Ada", "check_in"),
        ("Sam", "check_in"),
    ]
    assert "Lovelace" not in json.dumps(cards) and "2018" not in json.dumps(cards)
    again = this_week_cards(conn, "fam_local", date(2026, 1, 7))["children"]
    assert [c["plan_id"] for c in again] == [c["plan_id"] for c in cards]  # idempotent


def test_card_follows_the_loop_state(conn):
    plan = wp.create_plan(conn, "fam_local", "stu_1", "2026-01-05")
    seen = []
    for kind, payload in [
        ("feedback_submitted", {}),
        ("outlines_ready", {}),
        ("pick_made", {"option_id": "a"}),
        ("authoring_done", {"packet_id": "pk"}),
        ("marked_printed", {}),
    ]:
        if kind == "outlines_ready":
            from src.outline_models import OutlineSet

            o = lambda i, d: {  # noqa: E731
                "option_id": i,
                "title": i,
                "hook": "h",
                "difficulty": d,
                "standard_ids": ["VA.MATH.2.1"],
            }
            wp.store_outlines(
                conn,
                "fam_local",
                plan.plan_id,
                OutlineSet.model_validate(
                    {"options": [o("a", "easier"), o("b", "on_level"), o("c", "stretch")]}
                ),
            )
        advance(conn, "fam_local", plan.plan_id, Event(kind, payload=payload))
        cards = this_week_cards(conn, "fam_local", date(2026, 1, 7))["children"]
        seen.append(next(c for c in cards if c["student_id"] == "stu_1")["next_action"])
    assert seen == ["writing", "pick", "writing", "print", "done"]


def test_attention_flag_is_surfaced_and_other_family_is_hidden(conn):
    plan = wp.create_plan(conn, "fam_local", "stu_1", "2026-01-05")
    advance(conn, "fam_local", plan.plan_id, Event("flag_attention", payload={"reason": "slow"}))
    cards = this_week_cards(conn, "fam_local", date(2026, 1, 7))["children"]
    assert cards[0]["needs_attention"] is True
    assert all(c["student_id"] != "stu_9" for c in cards)


def test_endpoint_returns_cards(tmp_path, monkeypatch):
    db = tmp_path / "api.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    apply_migrations(db)
    c = sqlite3.connect(db)
    c.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob) "
        "VALUES ('kid','{}','{}',?)",
        (json.dumps({"name": "Kit Smith"}),),
    )
    c.commit()
    c.close()
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from main import app

    with TestClient(app) as client:
        body = client.get("/this-week").json()
    assert body["children"][0]["first_name"] == "Kit"
    assert body["children"][0]["next_action"] == "check_in"


def test_check_in_points_at_the_latest_finished_week(conn):
    for pid, week in (("old", "2026-01-05"), ("new", "2026-01-12")):
        conn.execute(
            "INSERT INTO weekly_packets (packet_id, student_id, grade_level, subject, week_of, "
            "status, payload_json, created_at, updated_at, family_id) "
            "VALUES (?, 'stu_1', 2, 'Math', ?, 'ready', '{}', 'x', 'x', 'fam_local')",
            (pid, week),
        )
    conn.commit()
    cards = this_week_cards(conn, "fam_local", date(2026, 1, 20))["children"]
    by_id = {c["student_id"]: c for c in cards}
    assert by_id["stu_1"]["feedback_packet_id"] == "new"
    assert by_id["stu_2"]["feedback_packet_id"] is None


def test_check_cards_endpoint_uses_first_name_and_hides_standards(tmp_path, monkeypatch):
    import importlib
    import sys
    from pathlib import Path

    db = tmp_path / "c.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    src = str(Path(__file__).resolve().parents[1] / "src")
    sys.path.insert(0, src)
    for name in ("db_utils", "packet_store", "week_store", "main", "prep_check_cards", "this_week"):
        sys.modules.pop(name, None)
    importlib.import_module("db_utils")
    ws = importlib.import_module("week_store")
    fixture = Path(__file__).parent / "fixtures" / "weekdoc" / "weather_week.json"
    week = json.loads(fixture.read_text(encoding="utf-8"))
    week["prep_checks"][0]["prompt"] = "Ask {{student_name}}: where does weather energy come from?"
    apply_migrations(db)
    c = sqlite3.connect(db)
    c.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob) "
        "VALUES ('kid','{}','{}',?)",
        (json.dumps({"name": "Kit Smith"}),),
    )
    c.commit()
    c.close()
    ws.save_week("kid", "pk1", week, grade_level=0, week_of="2026-01-05")
    from main import app

    with TestClient(app) as client:
        body = client.get("/students/kid/weekly-packets/pk1/checks").json()
        assert client.get("/students/kid/weekly-packets/nope/checks").status_code == 404
        assert client.get("/students/ghost/weekly-packets/pk1/checks").status_code == 404
    assert len(body["checks"]) == 10
    first = body["checks"][0]
    assert first["prompt"].startswith("Ask Kit:") and "Smith" not in first["prompt"]
    assert set(first) == {"check_id", "day", "prompt", "pass_criteria"}
