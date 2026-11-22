"""M3.3 / M3.5-M3.7: plan -> week pipeline, repair, typed failure, save, run record."""

import importlib
import json
import sqlite3
import sys

import pytest

from authoring import Tenant, author_week
from authoring.pipeline import (
    BUDGET_EXCEEDED, INVALID_INPUT, PLAN_FAILED, PROVIDER_ERROR, SUCCESS, WEEK_FAILED,
)
from llm import LLMClient
from llm.errors import LLMAuthError
from tests.authoring_fixtures import STANDARDS, good_plan, good_week, mutate, text
from tests.llm_provider_fakes import ScriptedProvider

STUDENT = {"first_name": "Ada", "grade": 2, "reading_level": "grade 2", "interests": ["space"],
           "parent_notes": "hands-on", "last_name": "Lovelace"}
TENANT = Tenant(family_id="fam_t")
ENV = {"LLM_MODEL_AUTHOR": "z-ai/glm-5.3", "LLM_FALLBACK_MODEL_AUTHOR": ""}


@pytest.fixture
def env(tmp_path, monkeypatch):
    db = tmp_path / "a.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    monkeypatch.setenv("AUTHORING_RUNS_DIR", str(tmp_path / "runs"))
    for name in ("src.db_utils", "src.packet_store", "src.week_store", "db_utils",
                 "packet_store", "week_store"):
        sys.modules.pop(name, None)
    importlib.import_module("packet_store").ensure_schema()
    con = sqlite3.connect(db)
    con.execute("INSERT OR IGNORE INTO family (family_id, created_at) VALUES ('fam_t', '2026-01-01')")
    con.executemany(
        "INSERT INTO standards (standard_id, subject, grade_level, description) VALUES (?,?,?,?)",
        [(s, "Science", 2, f"desc of {s}") for s in STANDARDS],
    )
    con.commit()
    con.close()
    return tmp_path


def go(provider, env, **kw):
    client = LLMClient(provider, env=ENV, sleep=lambda _s: None)
    args = dict(student_id="stu_1", client=client)
    args.update(kw)
    return author_week(TENANT, STUDENT, "Weather", STANDARDS, **args)


def test_success_path_plans_then_writes_validates_and_saves(env):
    provider = ScriptedProvider(text(good_plan()), text(good_week()))
    res = go(provider, env)
    assert res.ok and res.status == SUCCESS and res.saved and res.run.repairs == 0
    assert [s.name for s in res.run.steps] == ["plan", "week"]
    assert len(provider.requests) == 2
    plan_req, week_req = provider.requests
    assert "KIND MENU" in plan_req.messages[1]["content"]
    week_prompt = week_req.messages[1]["content"]
    assert "### readingWorksheet" in week_prompt and "### matchingWorksheet" not in week_prompt
    assert "desc of VA.SCIENCE.2.2.6.a" in week_prompt  # real standards in the brief
    assert "Lovelace" not in week_prompt
    assert res.run.prompt_version and res.run.prompt_hash and res.run.model == "z-ai/glm-5.3"
    assert res.run.cost_usd == pytest.approx(0.002) and res.run.completion_tokens == 10
    import week_store

    stored = week_store.get_week("stu_1", res.packet_id, family_id="fam_t")
    assert stored is not None and stored.title == "Weather Week"
    saved = json.loads(next((env / "runs").glob("*.json")).read_text())
    assert saved["status"] == "success" and saved["packet_id"] == res.packet_id
    assert "Ada" not in json.dumps(saved)  # no student name in the run record


def test_a_repair_fixes_a_schema_error_and_keeps_the_original_brief(env):
    broken = mutate(lambda w: w["days"][0].pop("title"))
    provider = ScriptedProvider(text(good_plan()), text(broken), text(good_week()))
    res = go(provider, env)
    assert res.ok and res.run.repairs == 1
    repair = provider.requests[2]
    brief = provider.requests[1].messages[1]["content"]
    assert repair.messages[1]["content"] == brief  # original brief is still there
    assert repair.messages[-2]["role"] == "assistant" and "title" in repair.messages[-1]["content"]
    assert repair.model == provider.requests[1].model == "z-ai/glm-5.3"
    assert (repair.temperature, repair.top_p) == (1.0, 0.95)  # same sampling as the author call
    assert res.run.steps[1].repairs == 1 and "title" in res.run.steps[1].errors[0]


def test_completeness_gate_failure_is_repaired(env):
    short = mutate(lambda w: w.__setitem__("prep_checks", w["prep_checks"][:6]))
    provider = ScriptedProvider(text(good_plan()), text(short), text(good_week()))
    res = go(provider, env)
    assert res.ok and "incomplete" in res.run.steps[1].errors[0]
    assert "prep checks" in provider.requests[2].messages[-1]["content"]


def test_bust_after_four_repairs_returns_typed_failure_with_the_errors(env):
    bad = text(mutate(lambda w: w["days"][0].pop("title")))
    provider = ScriptedProvider(text(good_plan()), *[bad] * 5)
    res = go(provider, env)
    assert not res.ok and res.status == WEEK_FAILED and res.week is None and res.plan is not None
    assert len(provider.requests) == 1 + 5  # plan, author call, 4 repairs
    assert len(res.errors) == 5 and all("schema validation failed" in e for e in res.errors)
    assert res.run.steps[1].repairs == 4 and not res.saved


def test_plan_failure_is_typed(env):
    provider = ScriptedProvider(*["{}"] * 5)
    res = go(provider, env)
    assert res.status == PLAN_FAILED and res.errors and len(provider.requests) == 5


def test_plan_with_unknown_standard_or_kind_is_repaired(env):
    bad = good_plan()
    bad["days"][0]["standards"] = ["VA.NOPE.1"]
    provider = ScriptedProvider(text(bad), text(good_plan()), text(good_week()))
    res = go(provider, env)
    assert res.ok and "not in the STANDARDS list" in res.run.steps[0].errors[0]
    kind = good_plan()
    kind["days"][0]["worksheets"][0]["kind"] = "madeUpKind"
    provider = ScriptedProvider(text(kind), text(good_plan()), text(good_week()))
    assert "not in the kind menu" in go(provider, env).run.steps[0].errors[0]


def test_standards_must_come_from_the_db_list(env):
    wrong = mutate(lambda w: w["prep_checks"][0].__setitem__("standard_id", "VA.MATH.1.1.1"))
    provider = ScriptedProvider(text(good_plan()), text(wrong), text(good_week()))
    res = go(provider, env)
    assert res.ok and "VA.MATH.1.1.1 is not in the STANDARDS list" in res.run.steps[1].errors[0]


def test_unknown_input_standard_is_invalid_input_not_an_exception(env):
    provider = ScriptedProvider()
    client = LLMClient(provider, env=ENV)
    res = author_week(TENANT, STUDENT, "Weather", ["VA.NOPE.1"], client=client)
    assert res.status == INVALID_INPUT and "VA.NOPE.1" in res.errors[0] and not provider.requests
    res = author_week(TENANT, STUDENT, "  ", STANDARDS, client=client)
    assert res.status == INVALID_INPUT


def test_run_cost_cap_halts_as_budget_exceeded(env):
    bad = text(mutate(lambda w: w["days"][0].pop("title")))
    provider = ScriptedProvider(text(good_plan()), bad, bad, bad, cost=0.01)
    res = go(provider, env, max_cost_usd=0.025)
    assert res.status == BUDGET_EXCEEDED and len(provider.requests) == 3


def test_provider_error_is_typed(env):
    res = go(ScriptedProvider(LLMAuthError("nope")), env)
    assert res.status == PROVIDER_ERROR and "LLMAuthError" in res.errors[0]


def test_without_student_id_nothing_is_saved(env):
    res = go(ScriptedProvider(text(good_plan()), text(good_week())), env, student_id=None)
    assert res.ok and not res.saved and res.packet_id is None
