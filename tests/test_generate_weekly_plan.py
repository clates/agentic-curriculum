"""generate_weekly_plan, end to end, against an in-process fake OpenAI client.

The fake (tests/llm_fakes.py) serves the same canned fixtures as the Playwright stub, so a
"Stub Monday objective" means the same thing here and in the E2E journeys. No test in this file
can reach a real LLM: agent._make_client is replaced, and conftest pins the endpoint to a dead port.
"""

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import agent  # noqa: E402
from tests.llm_fakes import DAYS, FakeProvider, fake_client  # noqa: E402

FALLBACK_OVERVIEW = "Weekly plan using standard curriculum progression"
FALLBACK_PROCEDURE = [
    "Introduce the concept",
    "Practice with materials",
    "Review and assess understanding",
]


def _standards(subject: str = "Math", grade: int = 3) -> list[dict]:
    return [
        {
            "standard_id": f"T.{grade}.{i}",
            "subject": subject,
            "grade_level": grade,
            "description": f"Standard {i} description",
        }
        for i in range(1, 11)
    ]


@pytest.fixture
def run(tmp_path, monkeypatch):
    """Return run(fake, subject=..., standards=...) -> (plan, saved_packets)."""
    saved: list[dict] = []
    monkeypatch.setattr(agent, "GENERATE_WEEKLY_DIR", tmp_path / "logs")
    monkeypatch.setattr(agent, "ARTIFACTS_DIR", tmp_path / "artifacts")
    monkeypatch.setattr(agent, "save_weekly_packet", lambda plan, **_: saved.append(plan))
    monkeypatch.setattr(
        agent,
        "get_student_profile",
        lambda sid: {
            "student_id": sid,
            "plan_rules_blob": json.dumps({"parent_notes": "keep it short"}),
            "progress_blob": json.dumps({}),
        },
    )

    def _run(fake: FakeProvider, *, subject: str = "Math", standards: list | None = None):
        monkeypatch.setattr(agent, "_make_client", lambda: fake_client(fake))
        monkeypatch.setattr(
            agent,
            "get_filtered_standards",
            lambda *a, **k: standards if standards is not None else _standards(subject),
        )
        plan = agent.generate_weekly_plan("s1", 3, subject)
        return plan, saved

    return _run


def _objective(day: dict) -> str:
    return day["lesson_plan"]["objective"]


def test_happy_path_five_real_days_with_scaffold_overview(run):
    fake = FakeProvider()
    plan, saved = run(fake)

    assert plan["weekly_overview"].startswith("E2E STUB WEEK: Math")
    assert [d["day"] for d in plan["daily_plan"]] == DAYS
    for day in plan["daily_plan"]:
        assert day["focus"] == f"Stub {day['day']} focus"
        assert _objective(day).startswith(f"Stub {day['day']} objective")
        assert day["lesson_plan"]["procedure"][0].startswith(f"Stub {day['day']} step 1")
    assert len(fake.calls_of("scaffold")) == 1
    assert sorted(c["day"] for c in fake.calls_of("day")) == sorted(DAYS)
    assert saved == [plan]  # persisted exactly once


def test_each_day_gets_its_own_standard_from_the_scaffold(run):
    plan, _ = run(FakeProvider())
    ids = [d["standard"]["standard_id"] for d in plan["daily_plan"]]
    assert ids == [f"T.3.{i}" for i in range(1, 6)]


def test_invalid_scaffold_json_uses_fallback_scaffold(run):
    fake = FakeProvider(scaffold="this is not json {")
    plan, _ = run(fake)

    assert plan["weekly_overview"] == FALLBACK_OVERVIEW
    assert [d["focus"] for d in plan["daily_plan"]] == [f"Day {i} focus" for i in range(1, 6)]
    # The week is still five days, one standard each, and the lesson calls still ran.
    assert [d["standard"]["standard_id"] for d in plan["daily_plan"]] == [
        f"T.3.{i}" for i in range(1, 6)
    ]
    assert len(fake.calls_of("day")) == 5
    assert all(_objective(d).startswith("Stub ") for d in plan["daily_plan"])


def test_scaffold_call_failure_uses_fallback_scaffold(run):
    plan, _ = run(FakeProvider(fail_scaffold=True))
    assert plan["weekly_overview"] == FALLBACK_OVERVIEW
    assert len(plan["daily_plan"]) == 5


def test_short_scaffold_is_padded_to_five_days(run):
    short = json.dumps(
        {
            "weekly_overview": "Short week",
            "daily_assignments": [
                {"day": "Monday", "standard_ids": ["T.3.1"], "focus": "Stub Monday focus"}
            ],
        }
    )
    plan, _ = run(FakeProvider(scaffold=short))
    assert plan["weekly_overview"] == "Short week"
    assert len(plan["daily_plan"]) == 5
    assert [d["focus"] for d in plan["daily_plan"][1:]] == ["Additional practice"] * 4


@pytest.mark.parametrize("bad_day", DAYS)
def test_one_invalid_day_falls_back_and_the_others_do_not(run, bad_day):
    fake = FakeProvider(broken_days={bad_day})
    plan, _ = run(fake)

    by_day = {d["day"]: d for d in plan["daily_plan"]}
    broken = by_day[bad_day]
    assert _objective(broken).startswith("Learn about: Standard ")
    assert broken["lesson_plan"]["procedure"] == FALLBACK_PROCEDURE
    assert broken["focus"] == f"Stub {bad_day} focus"  # the scaffold's focus is kept
    for day, payload in by_day.items():
        if day != bad_day:
            assert _objective(payload).startswith(f"Stub {day} objective")
    assert plan["weekly_overview"].startswith("E2E STUB WEEK")


def test_a_lesson_call_that_raises_falls_back_only_that_day(run):
    plan, _ = run(FakeProvider(failing_days={"Monday"}))
    by_day = {d["day"]: d for d in plan["daily_plan"]}
    assert by_day["Monday"]["lesson_plan"]["procedure"] == FALLBACK_PROCEDURE
    assert all(
        _objective(by_day[d]).startswith(f"Stub {d} objective") for d in DAYS if d != "Monday"
    )


def test_llm_entirely_unavailable_still_returns_five_distinct_days(run):
    plan, saved = run(FakeProvider(fail_everything=True))
    assert len(plan["daily_plan"]) == 5
    objectives = [_objective(d) for d in plan["daily_plan"]]
    assert all(o.startswith("Learn about: Standard ") for o in objectives)
    assert len(set(objectives)) == 5  # each day names its own standard
    assert saved == [plan]


def test_missing_api_key_is_a_value_error(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY")
    monkeypatch.delenv("OPENAI_API_KEY")
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        agent.generate_weekly_plan("s1", 3, "Math")


# --------------------------------------------------------------------------------------------
# #134 "Day 1 shows generic fallback while days 2-5 have real content"
#
# Root cause (fixed by #139/#140, kept here as a regression test): the standards table holds one
# document-level row per subject and grade with an EMPTY description, and it is the first row
# inserted for the group. get_filtered_standards used to take the first N rows (SQL LIMIT), so
# standards[0] was that blank row. Day 1 is assigned standards[0], so whenever its lesson call
# failed, _create_fallback_lesson_plan rendered "Learn about: the assigned topic" for Day 1 only,
# while days 2-5 (real standards) rendered their own descriptions.
#
# It cannot be reproduced on main any more, so this is a plain regression test, not an xfail.
# --------------------------------------------------------------------------------------------


def _load_private(name: str):
    path = SRC / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_private_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def real_standards_db(tmp_path_factory):
    # Load private copies by path: other test modules leave mocks/reloaded copies of these
    # names in sys.modules, and this fixture must not depend on test order.
    ingest_standards = _load_private("ingest_standards")
    logic = _load_private("logic")

    db_path = tmp_path_factory.mktemp("standards") / "curriculum.db"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(ingest_standards, "DB_FILE", str(db_path))
        mp.setattr(logic, "DB_FILE", str(db_path))
        mp.setattr(
            logic,
            "get_student_profile",
            lambda sid: {"progress_blob": "{}", "plan_rules_blob": "{}"},
        )
        ingest_standards.create_database()
        ingest_standards.ingest_standards_from_json(ingest_standards.STANDARDS_DIR)
        yield db_path, logic


def test_134_root_cause_ingestion_no_longer_stores_blank_document_rows(real_standards_db):
    db_path, _ = real_standards_db
    conn = sqlite3.connect(db_path)
    try:
        blank_rows = conn.execute(
            "SELECT COUNT(*) FROM standards WHERE TRIM(COALESCE(description, '')) = ''"
        ).fetchone()[0]
    finally:
        conn.close()
    # M11.4a fixed ingestion; the picker-level guard below stays as defense in depth.
    assert blank_rows == 0


def test_134_no_subject_or_grade_starts_with_a_blank_standard(real_standards_db):
    from constants import GRADE_LEVELS, SUBJECTS

    _, logic = real_standards_db
    offenders = []
    for subject in SUBJECTS:
        for grade in GRADE_LEVELS:
            picked = logic.get_filtered_standards("s1", grade, subject, limit=10)
            for position, standard in enumerate(picked[:5]):
                if not (standard.get("description") or "").strip():
                    offenders.append((subject, grade, position, standard["standard_id"]))
    assert offenders == [], f"blank-description standards would give a generic day: {offenders}"


def test_134_llm_down_day_one_is_not_more_generic_than_the_rest(run, real_standards_db):
    _, logic = real_standards_db
    standards = logic.get_filtered_standards("s1", 3, "English", limit=10)
    plan, _ = run(FakeProvider(fail_everything=True), subject="English", standards=standards)
    objectives = [_objective(d) for d in plan["daily_plan"]]
    assert not any("the assigned topic" in o for o in objectives), objectives
    assert not any(o.strip() == "Learn about:" for o in objectives)


# --------------------------------------------------------------------------------------------
# M1.6a: generation goes through the src/llm provider; usage is billed, caps are not swallowed
# --------------------------------------------------------------------------------------------


def test_generation_records_usage_for_every_call(run, monkeypatch):
    from llm import InMemoryLedger

    ledger = InMemoryLedger()
    fake = FakeProvider()
    run(fake)  # installs the default fake client; replace it with one that has a ledger
    monkeypatch.setattr(agent, "_make_client", lambda: fake_client(fake, ledger=ledger))
    agent.generate_weekly_plan("s1", 3, "Math")
    assert sorted(r["task"] for r in ledger.rows) == ["lesson"] * 5 + ["scaffold"]
    assert {r["student_id"] for r in ledger.rows} == {"s1"}
    assert all(r["cost_usd"] == pytest.approx(0.0001) for r in ledger.rows)


def test_cost_cap_is_not_swallowed_into_fallback_content(run, monkeypatch):
    from llm import CostCapExceeded, CostCaps, InMemoryLedger, UsageContext, Usage

    ledger = InMemoryLedger()
    ledger.record(
        UsageContext(family_id="fam_x", student_id="s1"),
        task="lesson",
        model="m",
        usage=Usage(cost_usd=5.0),
        latency_s=0.0,
        status="ok",
    )
    run(FakeProvider())  # installs the DB/standards stubs
    caps = CostCaps(family_month_usd=1.0)
    fresh = FakeProvider()
    monkeypatch.setattr(agent, "_make_client", lambda: fake_client(fresh, ledger=ledger, caps=caps))
    with pytest.raises(CostCapExceeded):
        agent.generate_weekly_plan(
            "s1", 3, "Math", usage=UsageContext(family_id="fam_x", student_id="s1")
        )
    assert fresh.calls == []  # stopped before any model call


def test_family_id_alone_bills_the_family_and_enforces_its_cap(run, monkeypatch):
    """The route and the trio pass only family_id; that alone must reach the ledger and the cap."""
    from llm import CostCapExceeded, CostCaps, InMemoryLedger, UsageContext, Usage

    ledger = InMemoryLedger()
    fake = FakeProvider()
    run(fake)  # installs the DB/standards stubs
    monkeypatch.setattr(agent, "_make_client", lambda: fake_client(fake, ledger=ledger))
    agent.generate_weekly_plan("s1", 3, "Math", family_id="fam_b")
    assert ledger.rows and {r["family_id"] for r in ledger.rows} == {"fam_b"}

    capped = InMemoryLedger()
    capped.record(
        UsageContext(family_id="fam_b", student_id="s1"),
        task="lesson",
        model="m",
        usage=Usage(cost_usd=0.02),
        latency_s=0.0,
        status="ok",
    )
    caps = CostCaps(family_month_usd=0.01)
    fresh = FakeProvider()
    monkeypatch.setattr(agent, "_make_client", lambda: fake_client(fresh, ledger=capped, caps=caps))
    with pytest.raises(CostCapExceeded):
        agent.generate_weekly_plan("s1", 3, "Math", family_id="fam_b")
    assert fresh.calls == []  # refused before any model call


def test_legacy_openai_env_names_still_work(monkeypatch):
    """Self-hosters with only OPENAI_API_KEY / OPENAI_MODEL keep working (M1.6b)."""
    from llm import default_client

    monkeypatch.delenv("OPENROUTER_API_KEY")
    monkeypatch.delenv("LLM_BASE_URL")
    monkeypatch.delenv("LLM_MODEL")
    monkeypatch.setenv("OPENAI_MODEL", "legacy/model")
    client = default_client()
    assert client.provider.settings.api_key == "pytest-not-a-real-key"
    assert client.provider.settings.base_url.startswith("http://127.0.0.1:")
    assert client.config("lesson").model == "legacy/model"


def test_new_llm_names_override_legacy(monkeypatch):
    from llm import default_client

    monkeypatch.setenv("OPENROUTER_API_KEY", "new-key")
    monkeypatch.setenv("LLM_BASE_URL", "http://127.0.0.1:1/new")
    monkeypatch.setenv("OPENAI_MODEL", "legacy/model")
    monkeypatch.setenv("LLM_MODEL", "new/model")
    client = default_client()
    assert client.provider.settings.api_key == "new-key"
    assert client.provider.settings.base_url == "http://127.0.0.1:1/new"
    assert client.config("lesson").model == "new/model"
