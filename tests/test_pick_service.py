"""M6.4 / M6.6: pick one of three, the authoring hook, fresh ideas and their cap."""

import json
import re
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import authoring_kickoff
import pick_service as ps
import week_plan as wp
from llm import LLMClient
from loop_state import Event, advance
from migrations import apply_migrations
from model_context import build_model_context, grade_from_birthday
from outline_models import OutlineSet
from tests.llm_provider_fakes import ScriptedProvider

FAM = "fam_local"
LONG = "The student will investigate and understand skill number {n} in {subject}"


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "t.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(path))
    apply_migrations(path)
    c = sqlite3.connect(path)
    c.execute("PRAGMA foreign_keys = ON")
    c.execute("INSERT INTO family (family_id, name, created_at) VALUES ('fam_b','B','x')")
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
    for fam, stu, name in ((FAM, "kid", "Mira Quillfeather"), ("fam_b", "other", "Zed")):
        c.execute(
            "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, "
            "metadata_blob, family_id) VALUES (?,'{}',?,?,?)",
            (
                stu,
                json.dumps({"parent_notes": "Likes short tasks", "interests": ["dinosaurs"]}),
                json.dumps({"name": name, "birthday": "2018-03-04", "grade_level": 3}),
                fam,
            ),
        )
    c.commit()
    yield c
    c.close()


@pytest.fixture(autouse=True)
def _hook():
    authoring_kickoff.clear_recorded()
    yield
    authoring_kickoff.set_authoring_requester(None)
    authoring_kickoff.clear_recorded()


def to_state(conn, status, student="kid", family=FAM):
    plan = wp.create_plan(conn, family, student, "2026-03-02")
    path = {
        "outlining": ["feedback_submitted"],
        "awaiting_pick": ["feedback_submitted", "outlines_ready"],
        "expired": ["feedback_submitted", "outlines_ready", "pick_expired"],
    }[status]
    for kind in path:
        if kind == "outlines_ready":
            wp.store_outlines(conn, family, plan.plan_id, old_outlines())
        advance(conn, family, plan.plan_id, Event(kind))
    return wp.get_plan(conn, family, plan.plan_id)


def old_outlines():
    def o(i, topic, sid):
        return {
            "option_id": i,
            "title": f"Old {i}",
            "hook": "An old idea",
            "topic": topic,
            "standard_ids": [sid],
            "activities": "Do things",
            "skills": ["A plain skill"],
            "effort": "About 20 minutes a day",
        }

    return OutlineSet.model_validate(
        {
            "options": [
                o("a", "Pirates", "VA.MATH.3.1"),
                o("b", "Music", "VA.MATH.3.1"),
                o("c", "Robots", "VA.MATH.3.1"),
            ]
        }
    )


SETS = [
    [
        ("Weather", "Weather Watchers", "tracks the sky and predicts tomorrow."),
        ("Baking", "Bakery Boss", "runs a bakery and tests recipes."),
        ("Space", "Mission to Mars", "plans a trip to another planet."),
    ],
    [
        ("Ocean animals", "Deep Sea Files", "dives down to meet sea creatures."),
        ("Castles", "Castle Under Siege", "defends a castle and its kingdom."),
        ("Music", "Band Practice Week", "puts a band together for a show."),
    ],
]


def reply_for(prompt):
    """A passing model answer; picks a set whose topics are not in the recent-topics line."""
    recent = json.loads(re.search(r"recent topics: (\[.*\])\.", prompt).group(1))
    text = " ".join(recent).lower()
    chosen = next(s for s in SETS if not any(t.lower() in text for t, _, _ in s))
    return json.dumps(
        {
            "options": [
                {
                    "option_id": letter,
                    "topic": topic,
                    "title": title,
                    "hook": f"Mira {hook}",
                    "activities": f"Hands-on work for {title}.",
                }
                for letter, (topic, title, hook) in zip("abc", chosen, strict=True)
            ]
        }
    )


class SmartProvider(ScriptedProvider):
    """Answers every outline call, avoiding the recent topics the prompt lists."""

    def __init__(self, fail=False):
        super().__init__()
        self.fail = fail

    def complete(self, request):
        if self.fail:
            self.requests.append(request)
            from llm import LLMBadRequest

            raise LLMBadRequest("boom")
        text = "\n".join(m["content"] for m in request.messages)
        self.script = [reply_for(text)]
        return super().complete(request)


def client(provider):
    return LLMClient(provider, env={}, sleep=lambda s: None)


# --- reading -----------------------------------------------------------------------------------


def test_the_view_has_first_name_three_ideas_and_no_ids_or_last_name(db):
    to_state(db, "awaiting_pick")
    view = ps.get_current(db, FAM, "kid")
    text = json.dumps(view)
    assert view["first_name"] == "Mira" and view["status"] == "awaiting_pick"
    assert [o["option_id"] for o in view["outlines"]] == ["a", "b", "c"]
    assert view["regenerations_left"] == 2
    assert "Quillfeather" not in text and "VA.MATH" not in text and "2018" not in text


def test_another_familys_child_is_not_found(db):
    to_state(db, "awaiting_pick", student="other", family="fam_b")
    with pytest.raises(ps.PickError) as info:
        ps.get_current(db, FAM, "other")
    assert info.value.status == 404


def test_no_plan_yet_is_a_404(db):
    with pytest.raises(ps.PickError) as info:
        ps.get_current(db, FAM, "kid")
    assert info.value.code == "no_plan"


# --- pick --------------------------------------------------------------------------------------


def test_pick_moves_to_authoring_records_the_choice_and_asks_for_the_week(db):
    plan = to_state(db, "awaiting_pick")
    calls = []
    authoring_kickoff.set_authoring_requester(lambda *a: calls.append(a))
    view = ps.pick(db, FAM, "kid", "b", plan.plan_id)
    assert (view["status"], view["picked_option"], view["already_picked"]) == (
        "authoring",
        "b",
        False,
    )
    assert calls == [(FAM, "kid", plan.plan_id, "b")]
    row = db.execute(
        "SELECT event_type, payload_json FROM loop_event WHERE plan_id=? AND event_type='pick_made'",
        (plan.plan_id,),
    ).fetchall()
    assert [tuple(r) for r in row] == [("pick_made", '{"option_id": "b"}')]


def test_the_same_pick_twice_changes_nothing(db):
    plan = to_state(db, "awaiting_pick")
    ps.pick(db, FAM, "kid", "a", plan.plan_id)
    again = ps.pick(db, FAM, "kid", "a", plan.plan_id)
    assert again["already_picked"] is True and again["status"] == "authoring"
    events = db.execute(
        "SELECT COUNT(*) FROM loop_event WHERE plan_id=? AND event_type='pick_made'",
        (plan.plan_id,),
    ).fetchone()[0]
    assert events == 1
    assert authoring_kickoff.recorded_requests() == [(FAM, "kid", plan.plan_id, "a")]  # once


def test_a_different_pick_after_writing_started_is_a_clear_conflict(db):
    plan = to_state(db, "awaiting_pick")
    ps.pick(db, FAM, "kid", "a", plan.plan_id)
    with pytest.raises(ps.PickError) as info:
        ps.pick(db, FAM, "kid", "c", plan.plan_id)
    assert (info.value.status, info.value.code) == (409, "already_picked")
    assert "already chose" in info.value.message
    assert wp.get_plan(db, FAM, plan.plan_id).picked_option == "a"


def test_a_missed_kickoff_heals_on_the_next_identical_pick(db):
    plan = to_state(db, "awaiting_pick")

    def broken(*_):
        raise RuntimeError("queue down")

    authoring_kickoff.set_authoring_requester(broken)
    with pytest.raises(RuntimeError):
        ps.pick(db, FAM, "kid", "b", plan.plan_id)
    assert wp.get_plan(db, FAM, plan.plan_id).status == "authoring"  # the choice itself is safe
    calls = []
    authoring_kickoff.set_authoring_requester(lambda *a: calls.append(a))
    ps.pick(db, FAM, "kid", "b", plan.plan_id)
    assert calls == [(FAM, "kid", plan.plan_id, "b")]


@pytest.mark.parametrize("status,code", [("expired", "expired"), ("outlining", "not_ready")])
def test_picking_is_refused_unless_the_ideas_are_open(db, status, code):
    plan = to_state(db, status)
    with pytest.raises(ps.PickError) as info:
        ps.pick(db, FAM, "kid", "a", plan.plan_id)
    assert (info.value.status, info.value.code) == (409, code)
    assert wp.get_plan(db, FAM, plan.plan_id).status == status


def test_a_stale_screen_cannot_pick(db):
    to_state(db, "awaiting_pick")
    with pytest.raises(ps.PickError) as info:
        ps.pick(db, FAM, "kid", "a", "wp_not_this_one")
    assert info.value.code == "stale_plan"


def test_the_default_hook_records_the_intent_once_with_the_job_key(db):
    plan = to_state(db, "awaiting_pick")
    ps.pick(db, FAM, "kid", "c", plan.plan_id)
    assert authoring_kickoff.recorded_requests() == [(FAM, "kid", plan.plan_id, "c")]
    assert authoring_kickoff.idempotency_key(plan.plan_id, "c") == f"author:{plan.plan_id}:c"


# --- fresh ideas -------------------------------------------------------------------------------


def test_expired_ideas_can_be_replaced_with_new_ones(db):
    plan = to_state(db, "expired")
    provider = SmartProvider()
    view = ps.regenerate(db, FAM, "kid", plan.plan_id, client=client(provider))
    assert view["status"] == "awaiting_pick" and view["regenerations_used"] == 1
    assert view["regenerations_left"] == 1
    assert [o["option_id"] for o in view["outlines"]] == ["a", "b", "c"]
    assert not any(o["title"].startswith("Old") for o in view["outlines"])
    assert len(provider.requests) == 1
    new = wp.get_plan(db, FAM, plan.plan_id).outlines
    # all three topics wrap the engine's one set; no parent input changed it
    assert len({tuple(o.standard_ids) for o in new.options}) == 1
    assert len({o.topic for o in new.options}) == 3


def test_fresh_ideas_keep_the_skills_and_change_the_topics(db):
    plan = to_state(db, "awaiting_pick")
    provider = SmartProvider()
    ps.regenerate(db, FAM, "kid", plan.plan_id, client=client(provider))
    first = wp.get_plan(db, FAM, plan.plan_id).outlines
    advance(db, FAM, plan.plan_id, Event("pick_expired"))
    ps.regenerate(db, FAM, "kid", plan.plan_id, client=client(provider))
    second = wp.get_plan(db, FAM, plan.plan_id).outlines
    assert first.options[0].standard_ids == second.options[0].standard_ids
    assert not ({o.topic for o in first.options} & {o.topic for o in second.options})


def test_last_weeks_chosen_topics_are_told_to_the_model(db):
    old = wp.create_plan(db, FAM, "kid", "2026-01-05")
    for kind in ("feedback_submitted", "outlines_ready", "pick_made"):
        if kind == "outlines_ready":
            wp.store_outlines(db, FAM, old.plan_id, old_outlines())
        advance(
            db,
            FAM,
            old.plan_id,
            Event(kind, payload={"option_id": "b"} if kind == "pick_made" else {}),
        )
    now = wp.create_plan(db, FAM, "kid", "2026-01-12")
    for kind in ("feedback_submitted", "outlines_ready"):
        if kind == "outlines_ready":
            wp.store_outlines(db, FAM, now.plan_id, old_outlines())
        advance(db, FAM, now.plan_id, Event(kind))
    provider = SmartProvider()
    ps.regenerate(db, FAM, "kid", now.plan_id, client=client(provider))
    prompt = "\n".join(m["content"] for m in provider.requests[0].messages)
    recent = re.search(r"recent topics: (\[.*\])\.", prompt).group(1)
    assert "Music" in recent  # the topic of the option picked last week
    assert "Pirates" in recent  # and what this week already showed


def test_the_third_regeneration_stops_with_a_plain_message(db):
    plan = to_state(db, "expired")
    provider = SmartProvider()
    for _ in range(2):
        ps.regenerate(db, FAM, "kid", plan.plan_id, client=client(provider))
        advance(db, FAM, plan.plan_id, Event("pick_expired"))
    calls = len(provider.requests)
    with pytest.raises(ps.PickError) as info:
        ps.regenerate(db, FAM, "kid", plan.plan_id, client=client(provider))
    assert (info.value.status, info.value.code) == (409, "limit_reached")
    assert "used this week" in info.value.message
    assert len(provider.requests) == calls  # no model call is made past the cap
    assert wp.get_plan(db, FAM, plan.plan_id).status == "expired"


def test_the_limit_comes_from_a_replaceable_interface(db):
    plan = to_state(db, "awaiting_pick")

    class One:
        def max_regenerations(self, family_id):
            return 1

    ps.regenerate(db, FAM, "kid", plan.plan_id, client=client(SmartProvider()), limits=One())
    with pytest.raises(ps.PickError) as info:
        ps.regenerate(db, FAM, "kid", plan.plan_id, client=client(SmartProvider()), limits=One())
    assert info.value.code == "limit_reached"


def test_a_failed_model_call_changes_nothing_and_costs_no_allowance(db):
    plan = to_state(db, "expired")
    from llm import LLMError

    with pytest.raises(LLMError):
        ps.regenerate(db, FAM, "kid", plan.plan_id, client=client(SmartProvider(fail=True)))
    after = wp.get_plan(db, FAM, plan.plan_id)
    assert after.status == "expired" and after.outlines is not None
    assert ps.regenerations_used(db, plan.plan_id) == 0


def test_a_plan_already_being_written_is_busy(db):
    plan = to_state(db, "outlining")
    with pytest.raises(ps.PickError) as info:
        ps.regenerate(db, FAM, "kid", plan.plan_id, client=client(SmartProvider()))
    assert info.value.code == "busy"


def test_a_second_request_for_the_same_regeneration_number_does_not_run_twice(db):
    plan = to_state(db, "expired")
    # Another request already claimed regeneration number 1: its loop-event key exists.
    db.execute(
        "INSERT INTO loop_event (family_id, plan_id, event_key, event_type, from_status, "
        "to_status, created_at) VALUES (?,?,?,?,?,?,?)",
        (FAM, plan.plan_id, f"regen:{plan.plan_id}:1", "claimed", "expired", "expired", "x"),
    )
    db.commit()
    with pytest.raises(ps.PickError) as info:
        ps.regenerate(db, FAM, "kid", plan.plan_id, client=client(SmartProvider()))
    assert info.value.code == "busy"
    after = wp.get_plan(db, FAM, plan.plan_id)
    assert after.status == "expired" and after.outlines is not None


def test_finish_outlining_writes_the_first_ideas_and_opens_the_pick(db):
    plan = to_state(db, "outlining")
    done = ps.finish_outlining(db, FAM, plan.plan_id, client=client(SmartProvider()))
    assert done.status == "awaiting_pick" and len(done.outlines.options) == 3
    assert ps.regenerations_used(db, plan.plan_id) == 0  # the first set is not a regeneration


def test_math_is_planned_at_the_math_grade_and_the_rest_at_the_language_arts_grade(
    tmp_path, monkeypatch
):
    """Through the real wiring: profile -> context -> loader (extra grades) -> selector."""
    path = tmp_path / "grades.db"
    apply_migrations(path)
    conn = sqlite3.connect(path)
    # Both subjects exist at both grades, so swapping the grades or loading only one of them
    # picks the wrong ones instead of the only ones there are.
    for subject in ("Math", "English"):
        for g in (1, 6):
            for n in range(1, 6):
                conn.execute(
                    "INSERT INTO standards (standard_id, subject, grade_level, description) "
                    "VALUES (?,?,?,?)",
                    (
                        f"VA.{subject.upper()}.{g}.{n}",
                        subject,
                        g,
                        LONG.format(n=n, subject=subject),
                    ),
                )
    meta = {"name": "Ada", "grade_level": 3, "math_grade": 6, "la_grade": 1}
    conn.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob, "
        "family_id) VALUES ('kid','{}','{}',?,?)",
        (json.dumps(meta), FAM),
    )
    conn.commit()
    plan = wp.create_plan(conn, FAM, "kid", "2026-03-02")
    seen = {}

    def fake_generate(context, week_standards, **_):
        seen["items"] = week_standards.items
        return type("Generated", (), {"outlines": old_outlines()})()

    monkeypatch.setattr(ps, "generate_outlines", fake_generate)
    ps.make_outlines(conn, FAM, ps.get_student(conn, FAM, "kid"), plan, variant=0)
    conn.close()

    picked = {(c.subject, c.grade) for c in seen["items"]}
    assert picked == {("Math", 6), ("English", 1)}


# --- context and the HTTP surface --------------------------------------------------------------


def test_grade_comes_from_the_profile_then_the_birthday_without_copying_it():
    from datetime import date

    assert grade_from_birthday("2018-03-04", date(2026, 11, 21)) == 3
    assert grade_from_birthday("2020-12-01", date(2026, 11, 21)) == 0
    assert grade_from_birthday("nonsense", date(2026, 11, 21)) is None
    ctx = build_model_context(
        {"name": "Mira Quillfeather", "birthday": "2018-03-04"}, {}, today=date(2026, 11, 21)
    )
    assert (ctx.first_name, ctx.grade) == ("Mira", 3)
    assert "2018" not in ctx.prompt_lines() and "Quillfeather" not in ctx.prompt_lines()


@pytest.fixture
def api(db, monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from main import app

    monkeypatch.setattr("llm.structured.default_client", lambda: client(SmartProvider()))
    with TestClient(app) as c:
        yield c


def test_http_pick_flow(db, api):
    plan = to_state(db, "awaiting_pick")
    got = api.get("/students/kid/week-plan").json()
    assert got["status"] == "awaiting_pick" and len(got["outlines"]) == 3
    first = api.post("/students/kid/week-plan/pick", json={"option": "b", "plan_id": plan.plan_id})
    assert first.status_code == 200 and first.json()["status"] == "authoring"
    repeat = api.post("/students/kid/week-plan/pick", json={"option": "b"})
    assert repeat.status_code == 200 and repeat.json()["already_picked"] is True
    clash = api.post("/students/kid/week-plan/pick", json={"option": "a"})
    assert clash.status_code == 409 and clash.json()["detail"]["code"] == "already_picked"
    assert api.post("/students/kid/week-plan/pick", json={"option": "z"}).status_code == 422
    assert api.get("/students/nobody/week-plan").status_code == 404


def test_http_fresh_ideas_and_the_cap(db, api):
    plan = to_state(db, "expired")
    for n in (1, 2):
        res = api.post("/students/kid/week-plan/regenerate", json={"plan_id": plan.plan_id})
        assert res.status_code == 200 and res.json()["regenerations_used"] == n
        advance(db, FAM, plan.plan_id, Event("pick_expired"))
    capped = api.post("/students/kid/week-plan/regenerate", json={})
    assert capped.status_code == 409
    assert capped.json()["detail"]["code"] == "limit_reached"


def test_http_model_failure_is_a_plain_502(db, api, monkeypatch):
    to_state(db, "expired")
    monkeypatch.setattr("llm.structured.default_client", lambda: client(SmartProvider(fail=True)))
    res = api.post("/students/kid/week-plan/regenerate", json={})
    assert res.status_code == 502
    detail = res.json()["detail"]
    assert detail["code"] == "outline_failed" and "try again" in detail["message"]
    assert "boom" not in json.dumps(detail)
