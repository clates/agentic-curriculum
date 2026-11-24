"""The weekly loop end to end (M8 integration): check-in -> outlines -> pick or auto-pick -> week.

Real queue, real worker, real handlers, real scheduler; only the model is scripted.
"""

import importlib
import json
import sqlite3
import sys
from datetime import UTC, date, datetime

import pytest

import authoring_kickoff
import job_registry
import jobs
import loop_integration
import loop_state as ls
import pick_service
import scheduler
import week_plan as wp
import worker as worker_mod
from llm import LLMClient
from migrations import apply_migrations
from outline_models import OutlineSet
from tests.authoring_fixtures import STANDARDS, good_plan, good_week, text
from tests.llm_provider_fakes import ScriptedProvider
from tests.test_pick_service import SmartProvider

FAM = "fam_local"
LONG = "The student will investigate and understand skill number {n} in {subject}"
ENV = {"LLM_MODEL_AUTHOR": "z-ai/glm-5.3", "LLM_FALLBACK_MODEL_AUTHOR": ""}


def utc(y, m, d, h=0, mi=0):
    return datetime(y, m, d, h, mi, tzinfo=UTC)


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = str(tmp_path / "loop.db")
    monkeypatch.setenv("CURRICULUM_DB_PATH", path)
    monkeypatch.setenv("AUTHORING_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setenv("LOOP_JOBS_ENABLED", "1")
    # packet_store keeps an import-time snapshot of the DB path: reload it for this database
    for name in (
        "src.db_utils",
        "src.packet_store",
        "src.week_store",
        "db_utils",
        "packet_store",
        "week_store",
    ):
        sys.modules.pop(name, None)
    apply_migrations(path)
    c = sqlite3.connect(path)
    for g in (2, 3, 4):
        for subject in ("Math", "Science", "English"):
            for n in range(1, 6):
                c.execute(
                    "INSERT INTO standards (standard_id, subject, grade_level, description) "
                    "VALUES (?,?,?,?)",
                    (
                        f"VA.{subject.upper()}.{g}.{n}",
                        subject,
                        g,
                        LONG.format(n=n, subject=subject),
                    ),
                )
    c.executemany(
        "INSERT INTO standards (standard_id, subject, grade_level, description) VALUES (?,?,?,?)",
        [(s, "Science", 2, f"desc of {s}") for s in STANDARDS],
    )
    c.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, "
        "metadata_blob, family_id) VALUES ('kid','{}',?,?,?)",
        (
            json.dumps({"parent_notes": "Likes short tasks", "interests": ["dinosaurs"]}),
            json.dumps({"name": "Mira", "birthday": "2018-03-04", "grade_level": 2}),
            FAM,
        ),
    )
    c.commit()
    c.close()
    importlib.import_module("packet_store").ensure_schema()
    return path


@pytest.fixture
def conn(db_path):
    c = jobs.connect(db_path)
    yield c
    c.close()


@pytest.fixture
def real_handlers(monkeypatch):
    """Register the real handlers for one test, then put the registry back as it was."""
    saved = dict(job_registry._HANDLERS)
    sys.modules.pop("job_handlers_real", None)
    mod = importlib.import_module("job_handlers_real")
    yield mod
    job_registry._HANDLERS.clear()
    job_registry._HANDLERS.update(saved)
    sys.modules.pop("job_handlers_real", None)


@pytest.fixture(autouse=True)
def _hook():
    authoring_kickoff.clear_recorded()
    yield
    authoring_kickoff.set_authoring_requester(None)
    authoring_kickoff.clear_recorded()


def use_model(mod, monkeypatch, provider):
    monkeypatch.setattr(
        mod, "_llm_client", lambda: LLMClient(provider, env=ENV, sleep=lambda s: None)
    )


def ideas():
    def o(i, title):
        return {
            "option_id": i,
            "title": title,
            "hook": "A fun idea",
            "topic": title,
            "standard_ids": STANDARDS,
            "activities": "Do things",
            "skills": ["A plain skill"],
            "effort": "About 20 minutes a day",
        }

    return OutlineSet.model_validate(
        {"options": [o("a", "Weather Watchers"), o("b", "Bakery Boss"), o("c", "Band Week")]}
    )


def plan_at(conn, status, week="2026-01-12"):
    plan = wp.create_plan(conn, FAM, "kid", week)
    steps = {
        "awaiting_feedback": [],
        "outlining": ["feedback_submitted"],
        "awaiting_pick": ["feedback_submitted", "outlines_ready"],
    }[status]
    for kind in steps:
        if kind == "outlines_ready":
            wp.store_outlines(conn, FAM, plan.plan_id, ideas())
        ls.advance(conn, FAM, plan.plan_id, ls.Event(kind))
    return wp.get_plan(conn, FAM, plan.plan_id)


def stored_week(packet_id):
    return importlib.import_module("week_store").get_week("kid", packet_id, family_id=FAM)


def kind_jobs(conn, kind):
    return [r["idempotency_key"] for r in conn.execute("SELECT * FROM jobs WHERE kind=?", (kind,))]


def run_worker(db_path, times=3):
    w = worker_mod.Worker(db_path, poll_seconds=0.01, backoff_base=0.001)
    for _ in range(times):
        w.run_once()
    w.conn.close()


def test_a_parent_who_never_picks_still_gets_a_ready_week(
    db_path, conn, real_handlers, monkeypatch
):
    plan = plan_at(conn, "awaiting_pick")
    provider = ScriptedProvider(text(good_plan()), text(good_week()))
    use_model(real_handlers, monkeypatch, provider)

    rep = scheduler.tick(utc(2026, 1, 11, 17, 0), conn)  # Sunday 12:00 in New York
    assert len(rep.auto_picked) == 1
    keys = kind_jobs(conn, "author")
    assert len(keys) == 1 and keys[0].startswith(f"author:{plan.plan_id}:")

    run_worker(db_path)
    done = wp.get_plan(conn, FAM, plan.plan_id)
    assert done.status == "ready" and done.packet_id == f"pk_{plan.plan_id}"
    stored = stored_week(done.packet_id)
    assert stored is not None and stored.title == "Weather Week"
    assert jobs.status(conn)["counts"]["succeeded"] == 1
    assert len(provider.requests) == 2  # plan + week, nothing more

    # nothing left to do: another tick and another worker pass spend no more model calls
    scheduler.tick(utc(2026, 1, 11, 17, 5), conn)
    run_worker(db_path)
    assert len(provider.requests) == 2 and kind_jobs(conn, "author") == keys


def test_a_parents_pick_and_the_auto_pick_share_one_author_job(conn, real_handlers):
    plan = plan_at(conn, "awaiting_pick")
    assert loop_integration.install()
    pick_service.pick(conn, FAM, "kid", "b", plan.plan_id)
    first = kind_jobs(conn, "author")
    assert first == [f"author:{plan.plan_id}:b"]
    pick_service.pick(conn, FAM, "kid", "b", plan.plan_id)  # a repeat tap
    scheduler.tick(utc(2026, 1, 11, 17, 30), conn)  # the scheduler's repair pass
    assert kind_jobs(conn, "author") == first
    job = conn.execute("SELECT max_attempts FROM jobs WHERE kind='author'").fetchone()
    assert job[0] == scheduler.AUTHOR_MAX_ATTEMPTS


def test_a_checkin_starts_outlines_at_once_and_the_scheduler_agrees(
    db_path, conn, real_handlers, monkeypatch
):
    plan = plan_at(conn, "awaiting_feedback")
    loop_integration.on_feedback(FAM, "kid")
    loop_integration.on_feedback(FAM, "kid")  # an exact repeat
    assert wp.get_plan(conn, FAM, plan.plan_id).status == "outlining"
    first = kind_jobs(conn, "outline")
    assert first == [f"outlines:{plan.plan_id}"]
    scheduler.tick(utc(2026, 1, 9, 22, 0), conn)  # Friday evening: nothing new to queue
    assert kind_jobs(conn, "outline") == first

    use_model(real_handlers, monkeypatch, SmartProvider())
    run_worker(db_path)
    after = wp.get_plan(conn, FAM, plan.plan_id)
    assert after.status == "awaiting_pick" and len(after.outlines.options) == 3


def test_a_checkin_with_the_loop_off_changes_nothing(conn, monkeypatch):
    monkeypatch.delenv("LOOP_JOBS_ENABLED")
    plan = plan_at(conn, "awaiting_feedback")
    loop_integration.on_feedback(FAM, "kid")
    assert wp.get_plan(conn, FAM, plan.plan_id).status == "awaiting_feedback"
    assert not kind_jobs(conn, "outline") and not loop_integration.install()


def test_a_week_that_fails_validation_is_retried_then_reported_by_status_only(
    db_path, conn, real_handlers, monkeypatch
):
    plan = plan_at(conn, "awaiting_pick")
    use_model(real_handlers, monkeypatch, ScriptedProvider(*["not json at all"] * 40))
    loop_integration.enqueue_author(conn, FAM, plan.plan_id, "a")
    ls.advance(conn, FAM, plan.plan_id, ls.Event("pick_made", payload={"option_id": "a"}))
    run_worker(db_path, times=2)
    row = conn.execute(
        "SELECT state, attempts, last_error FROM jobs WHERE kind='author'"
    ).fetchone()
    assert row["state"] == "queued" and row["attempts"] >= 1  # waiting to retry
    assert row["last_error"].startswith("AuthoringFailed")
    assert "Mira" not in row["last_error"] and "not json" not in row["last_error"]
    assert wp.get_plan(conn, FAM, plan.plan_id).status == "authoring"  # never half-ready


def test_an_author_job_for_a_plan_that_moved_on_does_nothing(
    db_path, conn, real_handlers, monkeypatch
):
    plan = plan_at(conn, "awaiting_pick")
    provider = ScriptedProvider()
    use_model(real_handlers, monkeypatch, provider)
    loop_integration.enqueue_author(conn, FAM, plan.plan_id, "a")  # nobody picked: stale job
    run_worker(db_path)
    assert provider.requests == []
    assert jobs.status(conn)["counts"]["succeeded"] == 1


def test_seed_demo_and_start_week_are_safe_to_repeat_and_carry_no_real_data(conn):
    cid = loop_integration.seed_demo(conn)
    loop_integration.seed_demo(conn)
    assert (
        conn.execute("SELECT COUNT(*) FROM student_profiles WHERE student_id=?", (cid,)).fetchone()[
            0
        ]
        == 1
    )
    plan = loop_integration.start_week(conn, cid, "2026-01-12")
    again = loop_integration.start_week(conn, cid, "2026-01-12")
    assert plan.plan_id == again.plan_id and again.status == "outlining"
    assert kind_jobs(conn, "outline") == [f"outlines:{plan.plan_id}"]
    assert loop_integration.next_monday(date(2026, 1, 8)) == "2026-01-12"  # Thursday
    assert loop_integration.next_monday(date(2026, 1, 12)) == "2026-01-19"  # Monday
    with pytest.raises(SystemExit):
        loop_integration.start_week(conn, "nobody", "2026-01-12")


# --- a job that dies flags the week; a retry or a success clears it ----------------------------


def _jobs(conn, kind):
    return conn.execute(
        "SELECT id, state, attempts, last_error FROM jobs WHERE kind=?", (kind,)
    ).fetchall()


def _card(conn):
    from datetime import date

    import this_week

    return this_week.this_week_cards(conn, FAM, date(2026, 1, 14))["children"][0]


def _picked_plan(conn):
    plan = plan_at(conn, "awaiting_pick")
    ls.advance(conn, FAM, plan.plan_id, ls.Event("pick_made", payload={"option_id": "a"}))
    loop_integration.enqueue_author(conn, FAM, plan.plan_id, "a")
    return plan


def test_a_rejected_key_kills_the_outline_job_at_once_and_flags_the_week(
    db_path, conn, real_handlers, monkeypatch
):
    from llm.errors import LLMAuthError

    plan = plan_at(conn, "outlining")
    loop_integration.enqueue_outline(conn, FAM, plan.plan_id)
    provider = ScriptedProvider(LLMAuthError("HTTP 401: User not found"))
    use_model(real_handlers, monkeypatch, provider)
    run_worker(db_path, times=4)

    (job,) = _jobs(conn, "outline")
    assert (job["state"], job["attempts"]) == ("dead", 1)
    assert job["last_error"].startswith("LLMAuthError")
    assert len(provider.requests) == 1  # no second try
    flagged = wp.get_plan(conn, FAM, plan.plan_id)
    assert flagged.status == "outlining"
    assert (flagged.needs_attention, flagged.attention_reason) == (True, "outline_failed")
    card = _card(conn)
    assert card["next_action"] == "writing" and card["needs_attention"] is True


def test_a_rate_limit_retries_and_does_not_flag_the_week(db_path, conn, real_handlers, monkeypatch):
    from llm.errors import LLMRateLimit

    plan = plan_at(conn, "outlining")
    loop_integration.enqueue_outline(conn, FAM, plan.plan_id)
    use_model(real_handlers, monkeypatch, ScriptedProvider(*[LLMRateLimit("429")] * 40))
    run_worker(db_path, times=1)
    (job,) = _jobs(conn, "outline")
    assert (job["state"], job["attempts"]) == ("queued", 1)
    assert job["last_error"].startswith("LLMRateLimit")
    assert wp.get_plan(conn, FAM, plan.plan_id).needs_attention is False


def test_retrying_the_dead_outline_job_unflags_the_week_and_success_leaves_it_clear(
    db_path, conn, real_handlers, monkeypatch
):
    from llm.errors import LLMAuthError

    plan = plan_at(conn, "outlining")
    loop_integration.enqueue_outline(conn, FAM, plan.plan_id)
    use_model(real_handlers, monkeypatch, ScriptedProvider(LLMAuthError("HTTP 401")))
    run_worker(db_path, times=1)
    job_id = _jobs(conn, "outline")[0]["id"]
    assert wp.get_plan(conn, FAM, plan.plan_id).needs_attention

    assert loop_integration.retry_dead_job(conn, job_id)
    assert not wp.get_plan(conn, FAM, plan.plan_id).needs_attention
    assert not loop_integration.retry_dead_job(conn, job_id)  # no longer dead

    use_model(real_handlers, monkeypatch, SmartProvider())  # the key was replaced
    run_worker(db_path, times=1)
    done = wp.get_plan(conn, FAM, plan.plan_id)
    assert done.status == "awaiting_pick" and not done.needs_attention


def test_the_worker_retry_command_unflags_the_week(db_path, conn, real_handlers, monkeypatch):
    from llm.errors import LLMAuthError

    plan = plan_at(conn, "outlining")
    loop_integration.enqueue_outline(conn, FAM, plan.plan_id)
    use_model(real_handlers, monkeypatch, ScriptedProvider(LLMAuthError("HTTP 401")))
    run_worker(db_path, times=1)
    job_id = _jobs(conn, "outline")[0]["id"]
    assert wp.get_plan(conn, FAM, plan.plan_id).needs_attention
    assert worker_mod.main(["--db", db_path, "--retry", str(job_id)]) == 0
    assert not wp.get_plan(conn, FAM, plan.plan_id).needs_attention
    assert _jobs(conn, "outline")[0]["state"] == "queued"


def test_a_rejected_key_in_the_author_step_is_dead_at_once_and_leaks_no_lesson_text(
    db_path, conn, real_handlers, monkeypatch
):
    from llm.errors import LLMAuthError

    plan = _picked_plan(conn)
    use_model(
        real_handlers, monkeypatch, ScriptedProvider(LLMAuthError("HTTP 401: Weather Watchers"))
    )
    run_worker(db_path, times=3)
    (job,) = _jobs(conn, "author")
    assert (job["state"], job["attempts"]) == ("dead", 1)
    assert job["last_error"] == "LLMAuthError: provider_error"  # class and status only
    flagged = wp.get_plan(conn, FAM, plan.plan_id)
    assert flagged.status == "authoring" and flagged.attention_reason == "author_failed"
    assert _card(conn)["needs_attention"] is True

    # fixed key + retry: the flag comes off, and the finished week leaves it off
    assert loop_integration.retry_dead_job(conn, job["id"])
    assert not wp.get_plan(conn, FAM, plan.plan_id).needs_attention
    use_model(real_handlers, monkeypatch, ScriptedProvider(text(good_plan()), text(good_week())))
    run_worker(db_path, times=1)
    done = wp.get_plan(conn, FAM, plan.plan_id)
    assert done.status == "ready" and not done.needs_attention


def test_a_transient_provider_error_in_the_author_step_still_retries(
    db_path, conn, real_handlers, monkeypatch
):
    from llm.errors import LLMTimeout

    plan = _picked_plan(conn)
    use_model(real_handlers, monkeypatch, ScriptedProvider(*[LLMTimeout("slow")] * 40))
    run_worker(db_path, times=1)
    (job,) = _jobs(conn, "author")
    assert (job["state"], job["attempts"]) == ("queued", 1)
    assert job["last_error"] == "LLMTimeout: provider_error"
    assert not wp.get_plan(conn, FAM, plan.plan_id).needs_attention


def test_a_dead_job_that_is_not_the_plans_current_one_flags_nothing(conn):
    plan = plan_at(conn, "awaiting_pick")  # the outline step is long done
    job, _ = jobs.enqueue(conn, FAM, "outline", "stale", {"plan_id": plan.plan_id}, max_attempts=1)
    assert not loop_integration.flag_dead_job(conn, job)
    ls.advance(conn, FAM, plan.plan_id, ls.Event("pick_made", payload={"option_id": "b"}))
    other, _ = jobs.enqueue(
        conn, FAM, "author", "other", {"plan_id": plan.plan_id, "option_id": "a"}
    )
    assert not loop_integration.flag_dead_job(conn, other)  # an idea that was not the pick
    assert not wp.get_plan(conn, FAM, plan.plan_id).needs_attention


def test_the_plan_moving_on_clears_a_leftover_flag(conn):
    plan = plan_at(conn, "outlining")
    ls.advance(
        conn, FAM, plan.plan_id, ls.Event("flag_attention", payload={"reason": "outline_failed"})
    )
    wp.store_outlines(conn, FAM, plan.plan_id, ideas())
    ls.advance(conn, FAM, plan.plan_id, ls.Event("outlines_ready"))
    assert not wp.get_plan(conn, FAM, plan.plan_id).needs_attention
