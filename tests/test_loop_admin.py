# ruff: noqa: F401, F811  (pytest fixtures are imported from the loop integration tests)
"""The loop console's API: every step can be pushed from here, through the loop's own code."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

import jobs
import loop_integration
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


def child(api, student="kid"):
    return next(
        c for c in api.get(f"{BASE}/overview").json()["children"] if c["student_id"] == student
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


def test_a_flagged_week_and_a_rejected_key_are_explained_in_the_console(
    api, db_path, conn, real_handlers, monkeypatch
):
    from llm.errors import LLMAuthError
    from tests.llm_provider_fakes import ScriptedProvider

    act(api, "new_week", week="2026-01-12")
    act(api, "skip_checkin")
    use_model(
        real_handlers, monkeypatch, ScriptedProvider(LLMAuthError("HTTP 401: User not found"))
    )
    run_worker(db_path, times=1)

    c = child(api)
    assert c["plan"]["needs_attention"] is True
    assert c["plan"]["attention_reason"] == "outline_failed"
    (job,) = c["plan"]["jobs"]
    assert (job["state"], job["attempts"]) == ("dead", 1)
    hint = (
        "The model key was rejected. Replace OPENROUTER_API_KEY in /srv/curriculum/.env "
        "and recreate the app and worker containers."
    )
    assert job["hint"] == hint
    assert api.get(f"{BASE}/overview").json()["queue"]["dead"][0]["hint"] == hint

    assert api.post(f"{BASE}/jobs/{job['id']}/retry").status_code == 200  # Retry button
    c = child(api)
    assert c["plan"]["needs_attention"] is False and c["plan"]["attention_reason"] is None
    assert c["plan"]["jobs"][0]["state"] == "queued"


def test_other_dead_jobs_get_no_key_hint_and_the_console_actions_unflag(api, conn):
    act(api, "new_week", week="2026-01-12")
    act(api, "skip_checkin")
    job_id = conn.execute("SELECT id FROM jobs WHERE kind='outline'").fetchone()[0]
    conn.execute("UPDATE jobs SET state='dead', last_error='RuntimeError: x' WHERE id=?", (job_id,))
    conn.commit()
    plan = wp.latest_plan_for_student(conn, FAM, "kid")
    import loop_state as ls

    ls.advance(
        conn, FAM, plan.plan_id, ls.Event("flag_attention", payload={"reason": "outline_failed"})
    )
    c = child(api)
    assert c["plan"]["needs_attention"] and c["plan"]["jobs"][0]["hint"] is None
    act(api, "generate_ideas")  # "Generate ideas" on the stuck week
    c = child(api)
    assert not c["plan"]["needs_attention"] and c["plan"]["jobs"][0]["state"] == "queued"

    # author side: Author now clears too
    ls.advance(
        conn, FAM, plan.plan_id, ls.Event("flag_attention", payload={"reason": "author_failed"})
    )
    assert child(api)["plan"]["needs_attention"]
    ls.advance(conn, FAM, plan.plan_id, ls.Event("flag_attention", payload={"reason": "x"}))
