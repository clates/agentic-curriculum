"""generate_weekly_plan, end to end, against an in-process fake OpenAI client.

The fake (tests/llm_fakes.py) serves the same canned fixtures as the Playwright stub, so a
"Stub Monday objective" means the same thing here and in the E2E journeys. No test in this file
can reach a real LLM: agent.OpenAI is replaced, and conftest pins OPENAI_BASE_URL to a dead port.
"""

import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import agent  # noqa: E402
from tests.llm_fakes import DAYS, FakeOpenAI  # noqa: E402

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

    def _run(fake: FakeOpenAI, *, subject: str = "Math", standards: list | None = None):
        monkeypatch.setattr(agent, "OpenAI", lambda **_: fake)
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
    fake = FakeOpenAI()
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
    plan, _ = run(FakeOpenAI())
    ids = [d["standard"]["standard_id"] for d in plan["daily_plan"]]
    assert ids == [f"T.3.{i}" for i in range(1, 6)]


def test_invalid_scaffold_json_uses_fallback_scaffold(run):
    fake = FakeOpenAI(scaffold="this is not json {")
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
    plan, _ = run(FakeOpenAI(fail_scaffold=True))
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
    plan, _ = run(FakeOpenAI(scaffold=short))
    assert plan["weekly_overview"] == "Short week"
    assert len(plan["daily_plan"]) == 5
    assert [d["focus"] for d in plan["daily_plan"][1:]] == ["Additional practice"] * 4


@pytest.mark.parametrize("bad_day", DAYS)
def test_one_invalid_day_falls_back_and_the_others_do_not(run, bad_day):
    fake = FakeOpenAI(broken_days={bad_day})
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
    plan, _ = run(FakeOpenAI(failing_days={"Monday"}))
    by_day = {d["day"]: d for d in plan["daily_plan"]}
    assert by_day["Monday"]["lesson_plan"]["procedure"] == FALLBACK_PROCEDURE
    assert all(
        _objective(by_day[d]).startswith(f"Stub {d} objective") for d in DAYS if d != "Monday"
    )


def test_llm_entirely_unavailable_still_returns_five_distinct_days(run):
    plan, saved = run(FakeOpenAI(fail_everything=True))
    assert len(plan["daily_plan"]) == 5
    objectives = [_objective(d) for d in plan["daily_plan"]]
    assert all(o.startswith("Learn about: Standard ") for o in objectives)
    assert len(set(objectives)) == 5  # each day names its own standard
    assert saved == [plan]


def test_missing_api_key_is_a_value_error(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY")
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
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


@pytest.fixture(scope="module")
def real_standards_db(tmp_path_factory):
    import ingest_standards
    import logic

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


def test_134_precondition_blank_document_rows_exist_and_come_first(real_standards_db):
    db_path, _ = real_standards_db
    conn = sqlite3.connect(db_path)
    try:
        blank_first = conn.execute(
            """SELECT COUNT(*) FROM standards s
               WHERE TRIM(COALESCE(description, '')) = ''
                 AND rowid = (SELECT MIN(rowid) FROM standards s2
                              WHERE s2.subject = s.subject AND s2.grade_level = s.grade_level)"""
        ).fetchone()[0]
    finally:
        conn.close()
    assert blank_first > 0, "the data shape that caused #134 is no longer present; revisit"


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
    plan, _ = run(FakeOpenAI(fail_everything=True), subject="English", standards=standards)
    objectives = [_objective(d) for d in plan["daily_plan"]]
    assert not any("the assigned topic" in o for o in objectives), objectives
    assert not any(o.strip() == "Learn about:" for o in objectives)
