"""Family isolation (E0): with login on, a family reads and writes only its own children.

Families A and B are both created families (neither is fam_local), so a path that still assumes
fam_local fails here. A owns one child with a profile, a legacy packet (for its worksheet artifact), a
structured week with feedback, a ready week plan and an open one. B is signed in and asks for A's things by id.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import e2e_seed  # noqa: E402
import main  # noqa: E402
from auth import passwords, store  # noqa: E402
from migrations import apply_migrations  # noqa: E402
from tests.factories import build_weekly_plan  # noqa: E402
from tests.llm_fakes import FakeProvider, fake_client  # noqa: E402
from tests.test_auth import iter_routes  # noqa: E402
from tests.test_pick_service import SmartProvider, client as llm_client  # noqa: E402

PASSWORD = "correct horse battery"
KID = "a_kid"
PACKET = "plan_a_kid_legacy"
WEEK = "week_a_kid"
LONG = "The student will investigate and understand skill number {n} in {subject}"
TABLES = ("student_profiles", "weekly_packets", "packet_feedback", "week_plan", "jobs")


def _point_app_at(db: Path, monkeypatch) -> None:
    """Other test modules re-import db_utils/packet_store; patch the copies this app calls."""
    for fn in (
        main.get_student_profile,
        main.get_weekly_packet,
        main.get_week.__globals__["_ps"].ensure_schema,
        main.generate_weekly_plan.__globals__["save_weekly_packet"],
    ):
        if "DB_FILE" in fn.__globals__:
            monkeypatch.setitem(fn.__globals__, "DB_FILE", str(db))


def _seed_family_a(conn: sqlite3.Connection, fam: str) -> dict:
    conn.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob,"
        " family_id) VALUES (?, '{}', '{}', ?, ?)",
        (
            KID,
            json.dumps({"name": "Ada Lovelace", "birthday": "2018-03-04", "grade_level": 3}),
            fam,
        ),
    )
    for subject in ("Math", "Science", "English"):
        for n in range(1, 6):
            conn.execute(
                "INSERT INTO standards (standard_id, subject, grade_level, description)"
                " VALUES (?, ?, 3, ?)",
                (f"VA.{subject.upper()}.3.{n}", subject, LONG.format(n=n, subject=subject)),
            )
    conn.commit()
    main.get_weekly_packet.__globals__["save_weekly_packet"](
        build_weekly_plan(plan_id=PACKET, student_id=KID), family_id=fam
    )
    week = json.loads((ROOT / "tests/fixtures/weekdoc/weather_week.json").read_text("utf-8"))
    save_week = main.get_week.__globals__["save_week"]
    save_week(KID, WEEK, week, grade_level=3, week_of="2026-01-06", family_id=fam)
    main.save_packet_feedback(KID, WEEK, {"MATH.4.1": "MASTERED"}, 0, family_id=fam)
    e2e_seed.create_plan(KID, "ready", "2026-01-05", fam)
    e2e_seed.create_plan(KID, "awaiting_pick", "2026-01-12", fam)
    ready = conn.execute(
        "SELECT plan_id FROM week_plan WHERE student_id = ? AND status = 'ready'", (KID,)
    ).fetchone()[0]
    artifact = conn.execute(
        "SELECT id FROM worksheet_artifacts WHERE packet_id = ? LIMIT 1", (PACKET,)
    ).fetchone()[0]
    return {"student_id": KID, "packet_id": WEEK, "plan_id": ready, "artifact_id": artifact}


@pytest.fixture
def env(tmp_path, monkeypatch):
    db = tmp_path / "iso.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    monkeypatch.setenv("AUTH_REQUIRED", "1")
    monkeypatch.delenv("LOOP_JOBS_ENABLED", raising=False)
    monkeypatch.setattr(passwords, "CURRENT", passwords.ScryptParams(n=2**10, r=8, p=1))
    _point_app_at(db, monkeypatch)
    monkeypatch.setattr(main, "_log_dir", lambda: tmp_path / "logs")
    trio = []
    monkeypatch.setattr(main, "generate_trio_for_student", lambda *args: trio.append(args))
    agent = main.generate_weekly_plan.__globals__
    fake = FakeProvider()
    monkeypatch.setitem(agent, "_make_client", lambda: fake_client(fake))
    monkeypatch.setitem(agent, "GENERATE_WEEKLY_DIR", tmp_path / "gen")
    monkeypatch.setitem(agent, "ARTIFACTS_DIR", tmp_path / "artifacts")
    monkeypatch.setitem(
        agent,
        "get_filtered_standards",
        lambda *a, **k: [
            {"standard_id": f"T.3.{i}", "subject": "Math", "grade_level": 3, "description": "d"}
            for i in range(1, 11)
        ],
    )
    monkeypatch.setattr("llm.structured.default_client", lambda: llm_client(SmartProvider()))
    apply_migrations(db)
    conn = sqlite3.connect(db)
    family_a, family_b = store.create_family(conn, "A"), store.create_family(conn, "B")
    store.create_user(conn, "parenta", PASSWORD, family_a)
    store.create_user(conn, "parentb", PASSWORD, family_b)
    ids = _seed_family_a(conn, family_a)
    yield {"db": db, "conn": conn, "ids": ids, "fake": fake, "family_a": family_a, "trio": trio}
    conn.close()


def signed_in(username: str) -> TestClient:
    c = TestClient(main.app)
    r = c.post("/auth/login", json={"username": username, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return c


def snapshot(conn: sqlite3.Connection) -> dict:
    return {t: sorted(map(repr, conn.execute(f"SELECT * FROM {t}"))) for t in TABLES}  # noqa: S608


def student_get_paths(ids: dict) -> list[str]:
    """Every GET route with {student_id}, filled in with A's ids (the loop console is Task 5's)."""
    values = {**ids, "subject": "Math"}
    return [
        route.path.format(**values)
        for route in iter_routes(main.app.routes)
        if isinstance(route, APIRoute)
        and "GET" in route.methods
        and "{student_id}" in route.path
        and not route.path.startswith("/loop-admin")
    ]


def writes(ids: dict) -> list[tuple[str, str, dict | None]]:
    """A's write calls, in an order where each one can succeed for A."""
    kid, packet, plan = ids["student_id"], ids["packet_id"], ids["plan_id"]
    return [
        ("POST", f"/students/{kid}/weekly-packets/{packet}/feedback", {"quantity_feedback": 1}),
        ("POST", f"/students/{kid}/week-plan/regenerate", {}),
        ("POST", f"/students/{kid}/week-plan/pick", {"option": "a"}),
        ("POST", f"/students/{kid}/week-plans/{plan}/printed", None),
        (
            "POST",
            "/generate_weekly_plan",
            {"student_id": kid, "grade_level": 3, "subject": "Math"},
        ),
        ("PUT", f"/student/{kid}", {"metadata": {"notes": "likes owls"}}),
        ("DELETE", f"/student/{kid}", None),
    ]


def test_family_b_cannot_read_family_a(env):
    b = signed_in("parentb")
    paths = student_get_paths(env["ids"])
    assert len(paths) >= 12 and f"/student/{KID}" in paths
    for path in paths:
        r = b.get(path)
        missing = b.get(path.replace(KID, "no_such_kid", 1))
        assert r.status_code == 404, f"{path} answered {r.status_code}"
        assert r.json() == missing.json() == {"detail": "Student not found"}, path
    assert KID not in b.get("/students").text
    week = b.get("/this-week")
    assert week.status_code == 200 and KID not in week.text and "Ada" not in week.text


def test_family_b_cannot_write_family_a(env):
    b = signed_in("parentb")
    before = snapshot(env["conn"])
    for method, path, body in writes(env["ids"]):
        r = b.request(method, path, json=body)
        assert r.status_code == 404, f"{method} {path} answered {r.status_code}"
        assert r.json() == {"detail": "Student not found"}, path
    assert snapshot(env["conn"]) == before
    assert env["fake"].calls == [] and env["trio"] == []  # no model call or trio for B


def test_family_a_still_works(env):
    a = signed_in("parenta")
    for path in student_get_paths(env["ids"]):
        gone = "/worksheet-artifacts/" in path  # 410: the seeded artifact has no file on disk
        assert a.get(path).status_code == (410 if gone else 200), path
    assert KID in a.get("/students").text
    assert KID in a.get("/this-week").text
    for method, path, body in writes(env["ids"]):
        r = a.request(method, path, json=body)
        assert r.status_code in (200, 201, 204), f"{method} {path}: {r.status_code} {r.text}"
        if path == "/generate_weekly_plan":  # the new packet is saved in A's family
            saved = env["conn"].execute(
                "SELECT family_id FROM weekly_packets WHERE packet_id = ?", (r.json()["plan_id"],)
            )
            assert saved.fetchall() == [(env["family_a"],)]
    assert env["trio"] == [(KID, env["family_a"])]  # the feedback hook runs for A's family


def test_new_ids_are_generated_with_login_on(env):
    b = signed_in("parentb")
    before = env["conn"].execute("SELECT * FROM student_profiles WHERE student_id = ?", (KID,))
    before = before.fetchall()
    child = {"name": "Bo", "birthday": "2019-05-06"}
    r = b.post("/students", json={"student_id": KID, "metadata": child})
    assert r.status_code == 201, r.text
    new_id = r.json()["student_id"]
    assert re.fullmatch(r"stu_[a-z2-7]{10}", new_id)
    after = env["conn"].execute("SELECT * FROM student_profiles WHERE student_id = ?", (KID,))
    assert after.fetchall() == before
    assert [s["student_id"] for s in b.get("/students").json()] == [new_id]
    assert b.get(f"/student/{new_id}").status_code == 200


def test_client_ids_still_work_with_login_off(env, monkeypatch):
    monkeypatch.delenv("AUTH_REQUIRED")
    c = TestClient(main.app)
    child = {"name": "Kid One", "birthday": "2019-05-06"}
    r = c.post("/students", json={"student_id": "kid1", "metadata": child})
    assert r.status_code == 201 and r.json()["student_id"] == "kid1"
    generated = c.post("/students", json={"metadata": child}).json()["student_id"]
    assert re.fullmatch(r"stu_[a-z2-7]{10}", generated)
    row = env["conn"].execute("SELECT family_id FROM student_profiles WHERE student_id = 'kid1'")
    assert row.fetchone() == ("fam_local",)
    assert {s["student_id"] for s in c.get("/students").json()} == {"kid1", generated}
