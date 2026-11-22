"""M6.1: the deterministic candidate selector."""

import json

import pytest

from candidate_selector import (
    DIFFICULTIES,
    NoCandidates,
    StandardInfo,
    load_candidate_inputs,
    select_candidates,
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


def ids(cs):
    return {d: cs.ids_for(d) for d in DIFFICULTIES}


def test_same_inputs_same_answer_and_different_seed_differs():
    a = select_candidates(progress={}, standards=world(), grade=3, seed="s1", now=NOW)
    b = select_candidates(progress={}, standards=world(), grade=3, seed="s1", now=NOW)
    c = select_candidates(progress={}, standards=world(), grade=3, seed="s2", now=NOW)
    assert a == b
    assert ids(a) != ids(c)


def test_every_id_exists_and_pools_sit_at_their_grade():
    standards = world()
    known = {s.standard_id: s for s in standards}
    cs = select_candidates(progress={}, standards=standards, grade=3, seed="x", now=NOW)
    for d in DIFFICULTIES:
        pool = cs.for_difficulty(d)
        assert 1 <= len(pool) <= 3
        assert all(c.standard_id in known for c in pool)
    assert {c.grade for c in cs.easier} == {2}
    assert {c.grade for c in cs.on_level} == {3}
    assert {c.grade for c in cs.stretch} == {4}


def test_no_skill_appears_in_two_options_when_there_is_room():
    cs = select_candidates(progress={}, standards=world(), grade=3, seed="x", now=NOW)
    flat = [i for d in DIFFICULTIES for i in cs.ids_for(d)]
    assert len(flat) == len(set(flat))


def test_options_rotate_through_subjects():
    cs = select_candidates(progress={}, standards=world(), grade=3, seed="x", now=NOW)
    for d in DIFFICULTIES:
        assert len({c.subject for c in cs.for_difficulty(d)}) == 3


def test_mastered_skills_are_never_new_work():
    standards = world()
    mastered = [s.standard_id for s in standards if s.grade == 3]
    progress = {"mastered_standards": mastered, "developing_standards": []}
    cs = select_candidates(progress=progress, standards=standards, grade=3, seed="x", now=NOW)
    assert not (set(mastered) & cs.all_ids())


def test_working_on_skills_come_first_in_the_on_level_option():
    standards = world()
    target = "SC.3.2"
    progress = {"mastered_standards": [], "developing_standards": [target]}
    cs = select_candidates(progress=progress, standards=standards, grade=3, seed="x", now=NOW)
    assert cs.on_level[0].standard_id == target
    assert cs.on_level[0].reason == "working_on"


def test_due_review_leads_the_easier_option_and_cooldown_is_respected():
    standards = world()
    progress = {
        "mastered_standards": ["MA.3.1", "MA.3.2"],
        "developing_standards": [],
        "standard_metadata": {
            # missed last week: due now
            "MA.3.1": {"last_seen": "2026-02-20T00:00:00Z", "last_feedback": "STRUGGLING"},
            # mastered yesterday with a 4 week cooldown: left alone
            "MA.3.2": {
                "last_seen": "2026-02-28T00:00:00Z",
                "last_feedback": "MASTERED",
                "cooldown_weeks": 4,
            },
        },
    }
    cs = select_candidates(progress=progress, standards=standards, grade=3, seed="x", now=NOW)
    assert cs.easier[0].standard_id == "MA.3.1"
    assert cs.easier[0].reason == "review"
    assert "MA.3.2" not in cs.all_ids()


def test_a_skill_is_blocked_while_its_prerequisite_is_known_weak():
    standards = [std("A.3.1"), std("A.3.2"), std("A.3.3", "Science"), std("A.4.1", grade=4)]
    prereqs = {"A.3.2": {"A.3.1"}, "A.4.1": {"A.3.2"}}
    progress = {"mastered_standards": [], "developing_standards": ["A.3.1"]}
    cs = select_candidates(
        progress=progress, standards=standards, prereqs=prereqs, grade=3, seed="x", now=NOW
    )
    assert "A.3.2" not in cs.all_ids()  # its prerequisite is shaky: offer that first
    assert "A.3.1" in cs.all_ids()
    # once the prerequisite is mastered the next skill opens up
    progress = {"mastered_standards": ["A.3.1"], "developing_standards": []}
    cs = select_candidates(
        progress=progress, standards=standards, prereqs=prereqs, grade=3, seed="x", now=NOW
    )
    assert "A.3.2" in cs.all_ids()


def test_a_prerequisite_with_no_record_is_assumed_known():
    standards = [std("A.3.2"), std("A.3.1")]
    cs = select_candidates(
        progress={}, standards=standards, prereqs={"A.3.2": {"A.3.1"}}, grade=3, seed="x", now=NOW
    )
    assert "A.3.2" in cs.all_ids()


def test_avoid_pushes_already_seen_skills_to_the_back():
    standards = world()
    first = select_candidates(progress={}, standards=standards, grade=3, seed="x", now=NOW)
    seen = first.all_ids()
    fresh = select_candidates(
        progress={}, standards=standards, grade=3, seed="x2", now=NOW, avoid=seen
    )
    assert not (seen & fresh.all_ids())


def test_progress_can_be_a_json_string_and_unknown_ids_are_ignored():
    progress = json.dumps(
        {
            "mastered_standards": ["GONE.1"],
            "standard_metadata": {
                "GONE.2": {"last_seen": "2026-02-01T00:00:00Z", "last_feedback": "STRUGGLING"}
            },
        }
    )
    cs = select_candidates(progress=progress, standards=world(), grade=3, seed="x", now=NOW)
    assert "GONE.2" not in cs.all_ids()


def test_tiny_pools_still_give_every_option_something():
    cs = select_candidates(progress={}, standards=[std("ONLY.3.1")], grade=3, seed="x", now=NOW)
    assert all(cs.for_difficulty(d) for d in DIFFICULTIES)


def test_nothing_to_plan_from_is_a_clear_error():
    with pytest.raises(NoCandidates):
        select_candidates(progress={}, standards=[], grade=3, seed="x", now=NOW)
    with pytest.raises(NoCandidates):
        select_candidates(
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
