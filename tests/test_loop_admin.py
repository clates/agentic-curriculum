# ruff: noqa: F401, F811  (pytest fixtures are imported from the loop integration tests)
"""The loop console's API: every step can be pushed from here, through the loop's own code."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

import jobs
import loop_integration
import loop_state as ls
import scheduler
import week_plan as wp
from tests.test_loop_integration import (  # noqa: F401  (fixtures and helpers)
    FAM,
    SmartProvider,
    conn,
    db_path,
    ideas,
    kind_jobs,
    real_handlers,
    run_worker,
    use_model,
)

BASE = "/loop-admin"


@pytest.fixture
def api(db_path):
    from main import app

    with TestClient(app) as c:
        yield c


def act(api, action, student="kid", **body):
    return api.post(f"{BASE}/students/{student}/actions/{action}", json=body)


def children(overview):
    return [c for f in overview["families"] for c in f["children"]]


def child(api, student="kid"):
    return next(
        c for c in children(api.get(f"{BASE}/overview").json()) if c["student_id"] == student
    )


def enabled(c):
    return {a["id"] for a in c["actions"] if a["enabled"]}


def states(c):
    return {s["key"]: s["state"] for s in c["steps"]}


def test_overview_lists_the_child_with_no_week_and_only_a_new_week_allowed(api):
    c = child(api)
    assert c["name"] == "Mira" and c["plan"] is None
    assert enabled(c) == {"new_week"}
    assert [s["key"] for s in c["steps"]] == [
        "feedback", "feed_forward", "outlines", "pick", "author", "print",
    ]  # fmt: skip
    assert {s["actor"] for s in c["steps"]} == {"parent", "system"}
    assert all(a["why_not"] for a in c["actions"] if not a["enabled"])


def test_the_whole_loop_can_be_driven_from_the_console(
    api, db_path, conn, real_handlers, monkeypatch
):
    r = act(api, "new_week", week="2026-01-12")
    assert r.status_code == 200
    c = r.json()["child"]
    assert c["plan"]["status"] == "awaiting_feedback" and states(c)["feedback"] == "current"
    assert enabled(c) == {"new_week", "skip_checkin", "reset_weeks"}

    c = act(api, "skip_checkin").json()["child"]  # the parent's step, forced
    assert c["plan"]["status"] == "outlining" and states(c)["outlines"] == "current"
    assert [j["kind"] for j in c["plan"]["jobs"]] == ["outline"]
    assert "generate_ideas" in enabled(c)

    use_model(real_handlers, monkeypatch, SmartProvider())
    run_worker(db_path)  # the worker writes the three ideas
    c = child(api)
    assert c["plan"]["status"] == "awaiting_pick" and len(c["plan"]["outlines"]) == 3
    assert enabled(c) >= {"pick", "generate_ideas"} and states(c)["pick"] == "current"

    # fresh ideas on demand, with no cap
    import pick_service

    real = pick_service.generate_outlines
    from llm import LLMClient

    monkeypatch.setattr(
        pick_service, "generate_outlines",
        lambda *a, client=None, **k: real(*a, client=LLMClient(SmartProvider(), env={}, sleep=lambda s: None), **k),
    )  # fmt: skip
    for _ in range(3):
        assert act(api, "generate_ideas").status_code == 200
    assert child(api)["plan"]["status"] == "awaiting_pick"

    # the author needs ideas whose skills exist in the author's list: use the shared fixture ideas
    plan = wp.latest_plan_for_student(conn, FAM, "kid")
    wp.store_outlines(conn, FAM, plan.plan_id, ideas())
    assert act(api, "pick").status_code == 422  # which one?
    c = act(api, "pick", option="b").json()["child"]
    assert c["plan"]["status"] == "authoring" and c["plan"]["picked_option"] == "b"
    assert kind_jobs(conn, "author") == [scheduler.author_key(conn, plan.plan_id, "b")]

    from llm import LLMClient as _L  # noqa: F401
    from tests.authoring_fixtures import good_plan, good_week, text
    from tests.llm_provider_fakes import ScriptedProvider

    use_model(real_handlers, monkeypatch, ScriptedProvider(text(good_plan()), text(good_week())))
    run_worker(db_path)
    c = child(api)
    assert c["plan"]["status"] == "ready" and states(c)["author"] == "done"
    assert enabled(c) == {"new_week", "mark_printed", "reset_weeks"}

    c = act(api, "mark_printed").json()["child"]
    assert c["plan"]["status"] == "printed" and set(states(c).values()) == {"done"}

    # and the cycle repeats: the next Monday, one week later
    c = act(api, "new_week").json()["child"]  # no date: the next Monday after the last week
    assert c["plan"]["status"] == "awaiting_feedback" and c["plan"]["week_start"] > "2026-01-12"
    assert date.fromisoformat(c["plan"]["week_start"]).weekday() == 0


def test_an_action_that_is_not_possible_says_so_in_plain_words(api):
    assert act(api, "skip_checkin").status_code == 409  # no week yet
    assert "Start a new week" in act(api, "skip_checkin").json()["detail"]["message"]
    act(api, "new_week", week="2026-01-12")
    assert act(api, "new_week", week="2026-01-12").status_code == 409  # that week exists
    assert act(api, "new_week", week="2026-01-13").status_code == 422  # a Tuesday
    assert act(api, "new_week", week="soon").status_code == 422
    assert act(api, "pick", option="a").status_code == 409  # still waiting for the check-in
    assert act(api, "mark_printed").status_code == 409
    assert act(api, "author_now").status_code == 409
    assert act(api, "teleport").status_code == 404
    assert act(api, "skip_checkin", student="nobody").status_code == 404


def test_a_dead_job_is_revived_by_the_step_that_needs_it(api, conn):
    act(api, "new_week", week="2026-01-12")
    act(api, "skip_checkin")
    job = jobs.get_job(conn, conn.execute("SELECT id FROM jobs WHERE kind='outline'").fetchone()[0])
    conn.execute(
        "UPDATE jobs SET state='dead', attempts=5, last_error='X: no' WHERE id=?", (job.id,)
    )
    conn.commit()
    q = api.get(f"{BASE}/overview").json()["queue"]
    assert [d["id"] for d in q["dead"]] == [job.id]
    act(api, "generate_ideas")  # "Generate ideas" on an outlining week puts the dead job back
    assert jobs.get_job(conn, job.id).state == "queued"
    assert api.post(f"{BASE}/jobs/{job.id}/retry").status_code == 409  # no longer dead
    assert api.post(f"{BASE}/jobs/99999/retry").status_code == 404
    conn.execute("UPDATE jobs SET state='dead' WHERE id=?", (job.id,))
    conn.commit()
    assert api.post(f"{BASE}/jobs/{job.id}/retry").status_code == 200
    assert jobs.get_job(conn, job.id).state == "queued"


def test_reset_clears_the_weeks_and_their_jobs_but_keeps_the_child(api, conn):
    act(api, "new_week", week="2026-01-12")
    act(api, "skip_checkin")
    assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1
    c = act(api, "reset_weeks").json()["child"]
    assert c["plan"] is None and enabled(c) == {"new_week"}
    assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM loop_event").fetchone()[0] == 0
    assert (
        conn.execute("SELECT COUNT(*) FROM student_profiles WHERE student_id='kid'").fetchone()[0]
        == 1
    )
    assert act(api, "new_week", week="2026-01-12").status_code == 200  # a clean slate


def test_seed_demo_adds_a_made_up_child(api):
    c = api.post(f"{BASE}/seed-demo").json()["child"]
    assert c["student_id"] == loop_integration.DEMO_STUDENT and c["name"] == "Demo"
    assert api.post(f"{BASE}/seed-demo").status_code == 200  # repeatable


def test_feed_forward_previews_the_skills_without_a_model_call(api):
    r = api.get(f"{BASE}/students/kid/feed-forward", params={"week": "2026-01-12"})
    body = r.json()
    assert r.status_code == 200 and body["week_start"] == "2026-01-12" and body["grade"] == 2
    assert body["skills"] and all(
        s["reason"] in {"review", "working_on", "new", "next_step"} for s in body["skills"]
    )
    assert (
        api.get(f"{BASE}/students/kid/feed-forward", params={"week": "2026-01-12"}).json() == body
    )
    assert api.get(f"{BASE}/students/nobody/feed-forward").status_code == 404


def test_every_console_route_needs_a_login_when_login_is_on(db_path, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "1")
    from main import app

    with TestClient(app) as c:
        assert c.get(f"{BASE}/overview").status_code == 401
        assert c.post(f"{BASE}/students/kid/actions/new_week", json={}).status_code == 401
        assert c.post(f"{BASE}/seed-demo").status_code == 401
        assert c.post(f"{BASE}/jobs/1/retry").status_code == 401


def test_a_written_week_can_be_reviewed_with_its_run_record(api, conn, db_path, monkeypatch):
    import json as _json
    import os

    from tests.authoring_fixtures import STANDARDS, good_week

    act(api, "new_week", week="2026-01-12")
    act(api, "skip_checkin")
    plan = wp.latest_plan_for_student(conn, FAM, "kid")
    wp.store_outlines(conn, FAM, plan.plan_id, ideas())
    ls.advance(conn, FAM, plan.plan_id, ls.Event("outlines_ready"))
    act(api, "pick", option="a")
    packet = f"pk_{plan.plan_id}"
    __import__("importlib").import_module("week_store").save_week("kid", packet, good_week(), grade_level=2, week_of="2026-01-12",
                                   family_id=FAM)  # fmt: skip
    ls.advance(conn, FAM, plan.plan_id, ls.Event("authoring_done", payload={"packet_id": packet}))
    runs = os.environ["AUTHORING_RUNS_DIR"]
    os.makedirs(runs, exist_ok=True)
    with open(os.path.join(runs, f"{packet}.json"), "w") as f:
        _json.dump({"status": "success", "model": "z-ai/glm-5.3", "cost_usd": 0.11, "repairs": 1,
                    "wall_s": 400, "uncovered_standards": []}, f)  # fmt: skip

    c = child(api)
    assert c["weeks"][0]["packet_id"] == packet and c["weeks"][0]["status"] == "ready"
    assert [s["id"] for s in c["plan"]["outlines"][0]["skills"]] == STANDARDS
    assert c["plan"]["outlines"][0]["skills"][0]["subject"] == "Science"
    assert c["grade"] == 2 and c["demo"] is False

    r = api.get(f"{BASE}/students/kid/weeks/{plan.plan_id}/review")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Weather Week" and len(body["days"]) == 5 and body["grade"] == 2
    assert body["run"]["model"] == "z-ai/glm-5.3" and body["run"]["repairs"] == 1
    assert [d["doc"] for d in body["documents"]] == ["packet", "guide", "prep"]
    assert body["documents"][0]["url"].endswith(f"/weekly-packets/{packet}/print?doc=packet")
    assert any("1 rewrite" in f["message"] for f in body["flags"])
    assert {s["id"] for s in body["skills"]} >= set(STANDARDS)
    # the links point at the print route the parent's print screen already uses
    assert all(
        d["url"].startswith(f"/api/students/kid/weekly-packets/{packet}/print?doc=")
        for d in body["documents"]
    )

    assert api.get(f"{BASE}/students/kid/weeks/wp_nope/review").status_code == 404
    assert api.get(f"{BASE}/students/nobody/weeks/{plan.plan_id}/review").status_code == 404
    act(api, "new_week", week="2026-01-19")
    newer = wp.latest_plan_for_student(conn, FAM, "kid")
    assert api.get(f"{BASE}/students/kid/weeks/{newer.plan_id}/review").status_code == 409


# --- login on: admin only; an admin sees every family, and each look at another is audited ------

PASSWORD = "correct horse battery"


@pytest.fixture
def two_families(db_path, monkeypatch):
    """Family A owns the fixture's "kid", with a week and a dead job. Family B owns "b_kid" and has
    an admin and an ordinary parent. Both are created families, so nothing can lean on fam_local."""
    from auth import passwords, store

    monkeypatch.setenv("AUTH_REQUIRED", "1")
    monkeypatch.setattr(passwords, "CURRENT", passwords.ScryptParams(n=2**10, r=8, p=1))
    c = jobs.connect(db_path)
    fam_a, fam_b = store.create_family(c, "A"), store.create_family(c, "B")
    c.execute("UPDATE student_profiles SET family_id=? WHERE student_id='kid'", (fam_a,))
    add_child(c, "b_kid", "Bea", fam_b)
    users = {
        name: store.create_user(c, name, PASSWORD, fam).id
        for name, fam in (("parenta", fam_a), ("adminb", fam_b), ("parentb", fam_b))
    }
    store.grant(c, "adminb", "admin")
    c.commit()
    plan = wp.create_plan(c, fam_a, "kid", "2026-01-12")
    job = jobs.enqueue(c, fam_a, "outline", f"outlines:{plan.plan_id}", {"plan_id": plan.plan_id})[
        0
    ]
    c.execute("UPDATE jobs SET state='dead', last_error='A secret' WHERE id=?", (job.id,))
    c.commit()
    yield {
        "conn": c, "fam_a": fam_a, "fam_b": fam_b, "plan_id": plan.plan_id, "job_id": job.id,
        "users": users,
    }  # fmt: skip
    c.close()


def add_child(conn, student_id, name, family_id):
    conn.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob,"
        " family_id) VALUES (?, '{}', '{}', ?, ?)",
        (student_id, f'{{"name": "{name}", "grade_level": 2}}', family_id),
    )
    conn.commit()


def signed_in(username):
    from main import app

    c = TestClient(app)
    assert (
        c.post("/auth/login", json={"username": username, "password": PASSWORD}).status_code == 200
    )
    return c


def rows(conn):
    tables = ("week_plan", "jobs", "student_profiles", "audit_log")
    return {t: conn.execute(f"SELECT * FROM {t} ORDER BY 1").fetchall() for t in tables}


def audits(conn):
    return [
        tuple(r)
        for r in conn.execute(
            "SELECT family_id, user_id, action, target, detail_json FROM audit_log ORDER BY 1"
        )
    ]


def console_routes():
    from fastapi.routing import APIRoute

    from main import app
    from tests.test_auth import iter_routes

    return [
        (m, r.path)
        for r in iter_routes(app.routes)
        if isinstance(r, APIRoute) and r.path.startswith(BASE)
        for m in r.methods
    ]


def test_console_is_404_for_non_admins_with_login_on(two_families):
    b = signed_in("parentb")
    before = rows(two_families["conn"])
    routes = console_routes()
    assert len(routes) == 6
    for student in ("b_kid", "kid"):  # their own child, and another family's: the same refusal
        for method, path in routes:
            url = path.format(
                student_id=student, plan_id=two_families["plan_id"], action="new_week",
                job_id=two_families["job_id"],
            )  # fmt: skip
            r = b.request(method, url, json={} if method == "POST" else None)
            assert r.status_code == 404 and r.json() == {"detail": "Not Found"}, f"{method} {path}"
    assert rows(two_families["conn"]) == before  # nothing written, not even an audit row
    assert signed_in("adminb").get(f"{BASE}/overview").status_code == 200


def test_an_admin_acts_on_another_familys_child_and_each_request_is_audited(two_families):
    conn, fam_a, plan_id = two_families["conn"], two_families["fam_a"], two_families["plan_id"]
    admin = two_families["users"]["adminb"]
    b = signed_in("adminb")

    r = act(b, "new_week", student="kid", week="2026-01-19")
    assert r.status_code == 200 and r.json()["child"]["plan"]["week_start"] == "2026-01-19"
    assert wp.latest_plan_for_student(conn, fam_a, "kid").week_start == "2026-01-19"  # A's week
    assert audits(conn) == [(fam_a, admin, "console.new_week", "kid", None)]

    conn.execute("DELETE FROM audit_log")
    conn.commit()
    assert b.get(f"{BASE}/students/kid/feed-forward").status_code == 200
    assert b.get(f"{BASE}/students/kid/weeks/{plan_id}/review").status_code == 409  # not written
    assert b.post(f"{BASE}/jobs/{two_families['job_id']}/retry").status_code == 200
    assert jobs.get_job(conn, two_families["job_id"]).state == "queued"
    assert audits(conn) == [
        (fam_a, admin, "console.view", "kid", None),
        (fam_a, admin, "console.view", "kid", None),
        (fam_a, admin, "console.retry", f"job:{two_families['job_id']}", None),
    ]

    conn.execute("DELETE FROM audit_log")
    conn.commit()
    r = act(b, "new_week", student="nobody")  # a missing child or job: the same 404 as before
    assert r.status_code == 404 and r.json() == {"detail": "Student not found"}
    assert act(b, "teleport", student="kid").status_code == 404  # an unknown name is not recorded
    r = b.post(f"{BASE}/jobs/99999/retry")
    assert r.status_code == 404 and r.json() == {"detail": {"message": "No such job."}}
    assert b.get(f"{BASE}/students/b_kid/weeks/{plan_id}/review").status_code == 404  # A's plan
    assert audits(conn) == []


def test_the_overview_shows_every_family_own_first_with_one_audit_row(two_families):
    conn, fam_a, fam_b = two_families["conn"], two_families["fam_a"], two_families["fam_b"]
    from auth import store

    fam_c = store.create_family(conn, "Cedars")
    add_child(conn, "c_kid", "Cy", fam_c)
    overview = signed_in("adminb").get(f"{BASE}/overview").json()
    assert [(f["family_id"], f["name"], f["own"]) for f in overview["families"]] == [
        (fam_b, "B", True), (fam_a, "A", False), (fam_c, "Cedars", False),
    ]  # fmt: skip
    assert [[c["student_id"] for c in f["children"]] for f in overview["families"]] == [
        ["b_kid"], ["kid"], ["c_kid"],
    ]  # fmt: skip
    # the whole queue, but another family's error text is not shown (it can quote a child's data)
    assert [d["id"] for d in overview["queue"]["dead"]] == [two_families["job_id"]]
    assert "A secret" not in str(overview)
    admin = two_families["users"]["adminb"]
    assert audits(conn) == [(None, admin, "console.overview", None, '{"families": 2}')]


def test_another_familys_error_shows_only_its_type(two_families):
    conn, job_id = two_families["conn"], two_families["job_id"]
    conn.execute("UPDATE jobs SET last_error='ValueError: Ava wrote x' WHERE id=?", (job_id,))
    conn.commit()
    overview = signed_in("adminb").get(f"{BASE}/overview").json()
    assert [d["last_error"] for d in overview["queue"]["dead"]] == ["ValueError"]
    kid = next(c for f in overview["families"] for c in f["children"] if c["student_id"] == "kid")
    assert [j["last_error"] for j in kid["plan"]["jobs"]] == ["ValueError"]
    assert "Ava wrote" not in str(overview)
    # the colonless one in the fixture has no type to show
    conn.execute("UPDATE jobs SET last_error='A secret' WHERE id=?", (job_id,))
    conn.commit()
    overview = signed_in("adminb").get(f"{BASE}/overview").json()
    assert [d["last_error"] for d in overview["queue"]["dead"]] == [None]


def test_the_overview_is_audited_at_most_once_per_admin_per_ten_minutes(two_families):
    conn, fam_a = two_families["conn"], two_families["fam_a"]
    b = signed_in("adminb")
    for _ in range(3):  # the console polls the overview every few seconds
        assert b.get(f"{BASE}/overview").status_code == 200
    act(b, "new_week", student="kid", week="2026-01-19")
    act(b, "new_week", student="kid", week="2026-01-26")
    actions = [a for _, _, a, _, _ in audits(conn)]
    assert actions == ["console.overview", "console.new_week", "console.new_week"]
    conn.execute(
        "UPDATE audit_log SET created_at=? WHERE action='console.overview'",
        (jobs.iso(jobs.utcnow() - timedelta(seconds=601)),),
    )
    conn.commit()
    b.get(f"{BASE}/overview")
    assert [a for _, _, a, _, _ in audits(conn)].count("console.overview") == 2
    assert [f for f, _, a, _, _ in audits(conn) if a == "console.new_week"] == [fam_a, fam_a]


def test_an_admin_on_their_own_family_writes_no_audit_row(two_families):
    conn = two_families["conn"]
    conn.execute("DELETE FROM student_profiles WHERE student_id='kid'")
    conn.commit()
    b = signed_in("adminb")
    assert [f["own"] for f in b.get(f"{BASE}/overview").json()["families"]] == [True]
    assert act(b, "new_week", student="b_kid", week="2026-01-19").status_code == 200
    assert b.get(f"{BASE}/students/b_kid/feed-forward").status_code == 200
    assert (
        wp.latest_plan_for_student(conn, two_families["fam_b"], "b_kid").week_start == "2026-01-19"
    )
    assert audits(conn) == []


def test_seed_demo_lands_in_the_admins_family_and_never_collides(two_families):
    conn = two_families["conn"]
    assert loop_integration.seed_demo(conn) == loop_integration.DEMO_STUDENT  # the CLI: fam_local
    b = signed_in("adminb")
    r = b.post(f"{BASE}/seed-demo")
    assert r.status_code == 200 and r.json()["child"]["demo"] is True
    sid = r.json()["child"]["student_id"]
    assert sid != loop_integration.DEMO_STUDENT
    assert b.post(f"{BASE}/seed-demo").json()["child"]["student_id"] == sid  # repeatable
    owners = dict(conn.execute("SELECT student_id, family_id FROM student_profiles").fetchall())
    assert owners[sid] == two_families["fam_b"] and owners["demo_child"] == "fam_local"
    own = b.get(f"{BASE}/overview").json()["families"][0]
    assert own["own"] and [c["student_id"] for c in own["children"]] == sorted(["b_kid", sid])
