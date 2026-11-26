"""POST /children: add a child (profile, first week, at most five per family)."""

from __future__ import annotations

import json
import sqlite3
import sys
import threading
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import loop_integration  # noqa: E402
import main  # noqa: E402
from auth import passwords, store  # noqa: E402
from migrations import apply_migrations  # noqa: E402

PASSWORD = "correct horse battery"
CHILD = {
    "name": "  Ada  ",
    "interests": [" owls ", "trains"],
    "math_grade": 3,
    "la_grade": 2,
    "notes": "Loves short tasks.",
}
# Wednesday 2026-11-25 15:00 UTC is 10:00 in New York: this week's Monday is 2026-11-23.
WEDNESDAY = datetime(2026, 11, 25, 15, 0, tzinfo=UTC)


def _at(now: datetime) -> None:
    main.app.dependency_overrides[main.utc_now] = lambda: now


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "children.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(path))
    monkeypatch.delenv("AUTH_REQUIRED", raising=False)
    monkeypatch.delenv("LOOP_JOBS_ENABLED", raising=False)
    monkeypatch.delenv("SCHEDULER_DEFAULT_TZ", raising=False)
    monkeypatch.setitem(main.list_students.__globals__, "DB_FILE", str(path))
    apply_migrations(path)
    _at(WEDNESDAY)
    yield path
    main.app.dependency_overrides.pop(main.utc_now, None)


def rows(db: Path, sql: str, params: tuple = ()) -> list[tuple]:
    conn = sqlite3.connect(db)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def kids(db: Path, family: str = "fam_local") -> list[str]:
    return [
        r[0]
        for r in rows(db, "SELECT student_id FROM student_profiles WHERE family_id=?", (family,))
    ]


def test_creates_the_child_with_the_stored_profile_shape(db):
    r = TestClient(main.app).post("/children", json=CHILD)
    assert r.status_code == 201, r.text
    body = r.json()
    assert set(body) == {"student_id", "week_start"}
    assert body["student_id"].startswith("stu_") and len(body["student_id"]) == 14
    [(family, meta, rules)] = rows(
        db,
        "SELECT family_id, metadata_blob, plan_rules_blob FROM student_profiles WHERE student_id=?",
        (body["student_id"],),
    )
    assert family == "fam_local"
    assert json.loads(meta) == {
        "name": "Ada",
        "interests": ["owls", "trains"],
        "math_grade": 3,
        "la_grade": 2,
        "notes": "Loves short tasks.",
        "grade_level": 2,
    }
    assert json.loads(rules) == {}


def test_starts_the_first_week(db):
    body = TestClient(main.app).post("/children", json=CHILD).json()
    assert body["week_start"] == "2026-11-23"
    assert rows(
        db, "SELECT week_start FROM week_plan WHERE student_id=?", (body["student_id"],)
    ) == [("2026-11-23",)]


def test_loop_off_makes_the_plan_but_queues_nothing(db):
    body = TestClient(main.app).post("/children", json=CHILD).json()
    [(status,)] = rows(db, "SELECT status FROM week_plan WHERE student_id=?", (body["student_id"],))
    assert status == "awaiting_feedback"
    assert rows(db, "SELECT * FROM jobs") == []


def test_loop_on_starts_the_week_and_queues_the_outlines(db, monkeypatch):
    monkeypatch.setenv("LOOP_JOBS_ENABLED", "1")
    body = TestClient(main.app).post("/children", json=CHILD).json()
    [(status,)] = rows(db, "SELECT status FROM week_plan WHERE student_id=?", (body["student_id"],))
    assert status == "outlining"
    assert rows(db, "SELECT kind FROM jobs") == [("outline",)]


def test_a_failure_starting_the_week_keeps_the_child(db, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("loop down")

    monkeypatch.setattr(loop_integration.wp, "create_plan", boom)
    r = TestClient(main.app).post("/children", json=CHILD)
    assert r.status_code == 201, r.text
    assert kids(db) == [r.json()["student_id"]]


def test_a_timezone_that_does_not_load_keeps_the_child(db):
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO family_settings (family_id, timezone, updated_at) VALUES (?,?,?)",
        ("fam_local", "Not/AZone", "x"),
    )
    conn.commit()
    conn.close()
    r = TestClient(main.app).post("/children", json=CHILD)
    assert r.status_code == 201, r.text
    assert kids(db) == [r.json()["student_id"]]
    assert r.json()["week_start"] == "2026-11-23"  # the UTC date (a Wednesday)


def test_a_start_week_that_exits_keeps_the_child(db, monkeypatch):
    monkeypatch.setenv("LOOP_JOBS_ENABLED", "1")

    def exits(*args, **kwargs):
        raise SystemExit("no child")

    monkeypatch.setattr(loop_integration, "start_week", exits)
    r = TestClient(main.app).post("/children", json=CHILD)
    assert r.status_code == 201, r.text
    assert kids(db) == [r.json()["student_id"]]


def test_the_sixth_child_is_refused_and_nothing_is_written(db):
    c = TestClient(main.app)
    for _ in range(5):
        assert c.post("/children", json=CHILD).status_code == 201
    before = (rows(db, "SELECT * FROM student_profiles"), rows(db, "SELECT * FROM week_plan"))
    r = c.post("/children", json=CHILD)
    assert r.status_code == 409
    assert r.json() == {"detail": "too_many_children"}
    assert (rows(db, "SELECT * FROM student_profiles"), rows(db, "SELECT * FROM week_plan")) == (
        before
    )


def test_simultaneous_requests_never_make_six(db):
    c = TestClient(main.app)
    for _ in range(4):
        assert c.post("/children", json=CHILD).status_code == 201
    go = threading.Barrier(6)
    codes: list[int] = []

    def add():
        client = TestClient(main.app)
        go.wait()
        codes.append(client.post("/children", json=CHILD).status_code)

    threads = [threading.Thread(target=add) for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(codes) == [201] + [409] * 5
    assert len(kids(db)) == 5


def test_the_limit_holds_under_a_race_at_the_db_level(db):
    """The count and the insert share one BEGIN IMMEDIATE: many writers at once still stop at 5."""
    import db_utils
    import jobs

    go = threading.Barrier(12)
    results: list[str] = []

    def add(i: int):
        conn = jobs.connect(str(db))
        try:
            go.wait()
            try:
                db_utils.add_child(conn, f"stu_race{i:06d}", {"name": "X"}, "fam_local", limit=5)
                results.append("ok")
            except db_utils.TooManyChildren:
                results.append("full")
        finally:
            conn.close()

    threads = [threading.Thread(target=add, args=(i,)) for i in range(12)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(results) == ["full"] * 7 + ["ok"] * 5
    assert len(kids(db)) == 5


@pytest.mark.parametrize(
    "change",
    [
        {"name": ""},
        {"name": "   "},
        {"name": "x" * 41},
        {"name": 5},
        {"interests": ["a"] * 9},
        {"interests": [""]},
        {"interests": ["  "]},
        {"interests": ["x" * 41]},
        {"interests": "owls"},
        {"math_grade": "3"},
        {"math_grade": 3.0},
        {"math_grade": True},
        {"math_grade": 9},
        {"math_grade": -1},
        {"math_grade": None},
        {"la_grade": "3"},
        {"la_grade": 3.0},
        {"la_grade": True},
        {"la_grade": 9},
        {"la_grade": -1},
        {"notes": "x" * 501},
        {"student_id": "stu_mine"},
    ],
)
def test_invalid_input_is_422_and_creates_nothing(db, change):
    r = TestClient(main.app).post("/children", json={**CHILD, **change})
    assert r.status_code == 422, r.text
    assert kids(db) == [] and rows(db, "SELECT * FROM week_plan") == []


@pytest.mark.parametrize("field", ["name", "math_grade", "la_grade"])
def test_required_fields(db, field):
    body = {k: v for k, v in CHILD.items() if k != field}
    assert TestClient(main.app).post("/children", json=body).status_code == 422


def test_edges_are_accepted(db):
    body = {"name": "x" * 40, "interests": ["y" * 40] * 8, "math_grade": 0, "la_grade": 8}
    r = TestClient(main.app).post("/children", json={**body, "notes": "z" * 500})
    assert r.status_code == 201, r.text
    r = TestClient(main.app).post("/children", json={"name": "Bo", "math_grade": 8, "la_grade": 0})
    assert r.status_code == 201, r.text
    [meta] = rows(
        db,
        "SELECT metadata_blob FROM student_profiles WHERE student_id=?",
        (r.json()["student_id"],),
    )
    assert json.loads(meta[0])["interests"] == [] and json.loads(meta[0])["notes"] == ""


@pytest.mark.parametrize(
    "local_day, expected",
    [
        (date(2026, 11, 23), "2026-11-23"),  # Monday: this week
        (date(2026, 11, 25), "2026-11-23"),  # Wednesday: this week
        (date(2026, 11, 26), "2026-11-30"),  # Thursday: next week
        (date(2026, 11, 29), "2026-11-30"),  # Sunday: next week
    ],
)
def test_first_week_rule(local_day, expected):
    assert loop_integration.first_week_start(local_day) == expected


@pytest.mark.parametrize(
    "now, tz, expected",
    [
        # 03:00 UTC Thursday is still Wednesday evening in New York: this week.
        (datetime(2026, 11, 26, 3, 0, tzinfo=UTC), None, "2026-11-23"),
        # ...but already Thursday in Tokyo: next week.
        (datetime(2026, 11, 26, 3, 0, tzinfo=UTC), "Asia/Tokyo", "2026-11-30"),
        # Monday 10:00 UTC; Sunday night in Honolulu: next week (which is tomorrow).
        (datetime(2026, 11, 30, 5, 0, tzinfo=UTC), "Pacific/Honolulu", "2026-11-30"),
        (datetime(2026, 11, 23, 12, 0, tzinfo=UTC), None, "2026-11-23"),
    ],
)
def test_first_week_uses_the_family_local_date(db, now, tz, expected):
    if tz:
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO family_settings (family_id, timezone, updated_at) VALUES (?,?,?)",
            ("fam_local", tz, "x"),
        )
        conn.commit()
        conn.close()
    _at(now)
    body = TestClient(main.app).post("/children", json=CHILD).json()
    assert body["week_start"] == expected
    assert rows(
        db, "SELECT week_start FROM week_plan WHERE student_id=?", (body["student_id"],)
    ) == [(expected,)]


def test_default_tz_from_the_environment(db, monkeypatch):
    monkeypatch.setenv("SCHEDULER_DEFAULT_TZ", "Asia/Tokyo")
    _at(datetime(2026, 11, 26, 3, 0, tzinfo=UTC))
    assert TestClient(main.app).post("/children", json=CHILD).json()["week_start"] == "2026-11-30"


# --- login on: two families -----------------------------------------------------------------


@pytest.fixture
def families(db, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "1")
    monkeypatch.setattr(passwords, "CURRENT", passwords.ScryptParams(n=2**10, r=8, p=1))
    conn = sqlite3.connect(db)
    a, b = store.create_family(conn, "A"), store.create_family(conn, "B")
    store.create_user(conn, "parenta", PASSWORD, a)
    store.create_user(conn, "parentb", PASSWORD, b)
    conn.commit()
    conn.close()
    return a, b


def signed_in(username: str) -> TestClient:
    c = TestClient(main.app)
    r = c.post("/auth/login", json={"username": username, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return c


def test_signed_out_is_refused(families, db):
    assert TestClient(main.app).post("/children", json=CHILD).status_code == 401
    assert kids(db) == []


def test_the_child_lands_in_the_callers_family_only(families, db):
    fam_a, fam_b = families
    a, b = signed_in("parenta"), signed_in("parentb")
    r = a.post("/children", json=CHILD)
    assert r.status_code == 201, r.text
    sid = r.json()["student_id"]
    assert kids(db, fam_a) == [sid] and kids(db, fam_b) == []
    assert rows(db, "SELECT family_id FROM week_plan WHERE student_id=?", (sid,)) == [(fam_a,)]
    assert sid in a.get("/students").text
    assert sid not in b.get("/students").text and "Ada" not in b.get("/students").text
    week = b.get("/this-week")
    assert week.status_code == 200 and sid not in week.text and "Ada" not in week.text
    assert sid in a.get("/this-week").text


def test_the_limit_is_per_family(families, db):
    fam_a, fam_b = families
    a, b = signed_in("parenta"), signed_in("parentb")
    for _ in range(5):
        assert a.post("/children", json=CHILD).status_code == 201
    assert a.post("/children", json=CHILD).status_code == 409
    assert b.post("/children", json=CHILD).status_code == 201
    assert len(kids(db, fam_a)) == 5 and len(kids(db, fam_b)) == 1


# --- the legacy POST /students obeys the same cap with login on ------------------------------

LEGACY = {"metadata": {"name": "Bo", "birthday": "2019-05-06"}}


def test_login_on_sixth_child_via_students_is_refused(families, db):
    fam_a, _ = families
    a = signed_in("parenta")
    for _ in range(5):
        r = a.post("/students", json=LEGACY)
        assert r.status_code == 201, r.text
    before = rows(db, "SELECT * FROM student_profiles")
    r = a.post("/students", json=LEGACY)
    assert r.status_code == 409
    assert r.json() == {"detail": "too_many_children"}
    assert rows(db, "SELECT * FROM student_profiles") == before
    assert len(kids(db, fam_a)) == 5


def test_login_on_students_keeps_its_response_and_plan_rules(families, db):
    fam_a, _ = families
    r = signed_in("parenta").post(
        "/students", json={**LEGACY, "student_id": "mine", "plan_rules": {"x": 1}}
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["student_id"].startswith("stu_")  # the client's id is ignored with login on
    assert json.loads(body["plan_rules_blob"]) == {"x": 1}
    assert kids(db, fam_a) == [body["student_id"]]


def test_login_on_a_mix_of_routes_cannot_exceed_five(families, db):
    fam_a, _ = families
    a = signed_in("parenta")
    for i in range(5):
        path, body = ("/children", CHILD) if i % 2 else ("/students", LEGACY)
        assert a.post(path, json=body).status_code == 201
    assert a.post("/children", json=CHILD).status_code == 409
    assert a.post("/students", json=LEGACY).status_code == 409
    assert len(kids(db, fam_a)) == 5


def test_login_on_simultaneous_mixed_requests_never_make_six(families, db):
    fam_a, _ = families
    clients = [signed_in("parenta") for _ in range(6)]
    for _ in range(4):
        assert clients[0].post("/students", json=LEGACY).status_code == 201
    go = threading.Barrier(6)
    codes: list[int] = []

    def add(i: int):
        go.wait()
        path, body = ("/children", CHILD) if i % 2 else ("/students", LEGACY)
        codes.append(clients[i].post(path, json=body).status_code)

    threads = [threading.Thread(target=add, args=(i,)) for i in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(codes) == [201] + [409] * 5
    assert len(kids(db, fam_a)) == 5


def test_login_off_students_is_unchanged(db):
    """Self-hosters: no cap on the legacy route, and the client's id is still honoured."""
    c = TestClient(main.app)
    for i in range(6):
        r = c.post("/students", json={**LEGACY, "student_id": f"kid_{i}"})
        assert r.status_code == 201, r.text
        assert r.json()["student_id"] == f"kid_{i}"
    assert c.post("/students", json=LEGACY).status_code == 201  # no id: server picks one
    assert c.post("/students", json={**LEGACY, "student_id": "kid_0"}).status_code == 400
    assert len(kids(db)) == 7
