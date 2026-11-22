"""M6.1: the deterministic standards selector (the engine decides; no parent input)."""

import inspect
import json

import pytest

from candidate_selector import (
    PER_SET,
    NoCandidates,
    StandardInfo,
    load_candidate_inputs,
    step_up_slots,
    select_week_standards,
)

NOW = "2026-03-01T00:00:00Z"


def std(sid, subject="Math", grade=3):
    return StandardInfo(sid, subject, grade, f"The student will do {sid} in plain words")


def world():
    out = []
    for g in (2, 3, 4):
        for subject in ("Math", "Science", "English"):
            for n in range(1, 5):
                out.append(std(f"{subject[:2].upper()}.{g}.{n}", subject, g))
    return out


def sel(progress=None, **kw):
    kw.setdefault("standards", world())
    return select_week_standards(progress=progress or {}, grade=3, seed="x", now=NOW, **kw)


def test_same_inputs_same_answer_and_the_seed_only_breaks_ties():
    a, b = sel(), sel()
    assert a == b
    assert len(a.ids()) == len(set(a.ids())) <= PER_SET


def test_the_selector_takes_no_parent_input_and_no_difficulty():
    params = set(inspect.signature(select_week_standards).parameters)
    assert params == {"progress", "standards", "prereqs", "grade", "seed", "now", "per_set"}


def test_a_new_child_gets_grade_level_skills_across_subjects_and_no_step_up():
    cs = sel()
    assert {c.grade for c in cs.items} == {3}
    assert len({c.subject for c in cs.items}) >= 3
    assert {c.reason for c in cs.items} == {"new"}


def test_every_id_exists():
    known = {s.standard_id for s in world()}
    assert set(sel().ids()) <= known


def test_mastered_skills_are_never_new_work():
    mastered = [s.standard_id for s in world() if s.grade == 3]
    cs = sel({"mastered_standards": mastered, "developing_standards": []})
    assert not (set(mastered) & set(cs.ids()))


def test_the_gap_comes_first_after_review():
    cs = sel({"mastered_standards": [], "developing_standards": ["SC.3.2"]})
    assert cs.items[0].standard_id == "SC.3.2" and cs.items[0].reason == "working_on"


def test_due_review_comes_first_and_cooldown_is_respected():
    progress = {
        "mastered_standards": ["MA.3.1", "MA.3.2"],
        "developing_standards": [],
        "standard_metadata": {
            "MA.3.1": {"last_seen": "2026-02-20T00:00:00Z", "last_feedback": "STRUGGLING"},
            "MA.3.2": {
                "last_seen": "2026-02-28T00:00:00Z",
                "last_feedback": "MASTERED",
                "cooldown_weeks": 4,
            },
        },
    }
    cs = sel(progress)
    assert cs.items[0].standard_id == "MA.3.1" and cs.items[0].reason == "review"
    assert "MA.3.2" not in cs.ids()


def test_the_step_up_share_comes_from_mastery_not_from_anyone_asking():
    assert step_up_slots(0, 0) == 0
    assert step_up_slots(2, 0) == 0
    assert step_up_slots(3, 0) == 1
    assert step_up_slots(10, 2) == 0  # shaky: consolidate first
    strong = {"mastered_standards": ["MA.3.1", "MA.3.2", "MA.3.3", "SC.3.1"]}
    cs = sel(strong)
    up = [c for c in cs.items if c.reason == "next_step"]
    assert len(up) == 1 and up[0].grade == 4
    shaky = {
        "mastered_standards": ["MA.3.1", "MA.3.2", "MA.3.3", "SC.3.1"],
        "developing_standards": ["SC.3.2", "EN.3.1"],
    }
    assert not [c for c in sel(shaky).items if c.reason == "next_step"]


def test_the_set_follows_mastery_so_different_children_get_different_weeks():
    fresh = sel()
    strong = sel({"mastered_standards": ["MA.3.1", "MA.3.2", "MA.3.3", "SC.3.1"]})
    assert fresh.ids() != strong.ids()


def test_a_skill_is_blocked_while_its_prerequisite_is_known_weak():
    standards = [std("A.3.1"), std("A.3.2"), std("A.3.3", "Science"), std("A.4.1", grade=4)]
    prereqs = {"A.3.2": {"A.3.1"}, "A.4.1": {"A.3.2"}}
    cs = sel(
        {"mastered_standards": [], "developing_standards": ["A.3.1"]},
        standards=standards,
        prereqs=prereqs,
    )
    assert "A.3.2" not in cs.ids() and "A.3.1" in cs.ids()
    cs = sel(
        {"mastered_standards": ["A.3.1"], "developing_standards": []},
        standards=standards,
        prereqs=prereqs,
    )
    assert "A.3.2" in cs.ids()


def test_a_prerequisite_with_no_record_is_assumed_known():
    cs = sel(standards=[std("A.3.2"), std("A.3.1")], prereqs={"A.3.2": {"A.3.1"}})
    assert "A.3.2" in cs.ids()


def test_progress_can_be_a_json_string_and_unknown_ids_are_ignored():
    progress = json.dumps(
        {
            "mastered_standards": ["GONE.1"],
            "standard_metadata": {
                "GONE.2": {"last_seen": "2026-02-01T00:00:00Z", "last_feedback": "STRUGGLING"}
            },
        }
    )
    cs = select_week_standards(progress=progress, standards=world(), grade=3, seed="x", now=NOW)
    assert "GONE.2" not in set(cs.ids())


def test_tiny_pools_still_give_a_week():
    cs = select_week_standards(progress={}, standards=[std("ONLY.3.1")], grade=3, seed="x", now=NOW)
    assert cs.ids() == ["ONLY.3.1"]


def test_nothing_to_plan_from_is_a_clear_error():
    with pytest.raises(NoCandidates):
        select_week_standards(progress={}, standards=[], grade=3, seed="x", now=NOW)
    with pytest.raises(NoCandidates):
        select_week_standards(
            progress={"mastered_standards": ["ONLY.3.1"]},
            standards=[std("ONLY.3.1")],
            grade=3,
            seed="x",
            now=NOW,
        )


def test_loader_reads_nearby_whole_skills_from_the_standards_table(tmp_path):
    import sqlite3

    db = tmp_path / "s.db"
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE standards (standard_id TEXT PRIMARY KEY, source TEXT, subject TEXT, "
        "grade_level INTEGER, description TEXT, json_blob TEXT)"
    )
    long = "The student will investigate and understand a whole skill"
    rows = [
        ("VA.MATH.3.1", "Math", 3, long),
        ("VA.MATH.3.1.a", "Math", 3, long),  # a bullet sub-point
        ("VA.MATH.3.2", "Math", 3, "Short heading"),  # a heading, not a skill
        ("VA.MATH.9.1", "Math", 9, long),  # too far from grade 3
    ]
    conn.executemany(
        "INSERT INTO standards VALUES (?, 'x', ?, ?, ?, NULL)",
        [(a, b, c, d) for a, b, c, d in rows],
    )
    conn.commit()
    conn.close()
    standards, _prereqs = load_candidate_inputs(str(db), 3)
    assert [s.standard_id for s in standards] == ["VA.MATH.3.1"]
