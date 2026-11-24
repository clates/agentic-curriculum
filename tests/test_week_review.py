"""Week review (console): facts and flags about an authored week, no model call."""

import json
from pathlib import Path

import week_review as wr

SIMPLE = "The cat sat. The dog ran. We had fun. It was a sunny day. We ate lunch. " * 4
HARD = (
    "Photosynthesis transforms electromagnetic radiation into chemical energy, enabling "
    "autotrophic organisms to synthesize carbohydrates through sophisticated biochemical "
    "pathways involving chlorophyll molecules and enzymatic catalysis. " * 3
)
SKILLS = {
    "S.SCI.1": {"subject": "Science", "description": "plants grow"},
    "S.MATH.1": {"subject": "Math", "description": "symmetry"},
    "S.HIST.1": {"subject": "History", "description": "explorers"},
    "S.CS.1": {"subject": "Computer Science", "description": "technology changes"},
}


def day(
    name, passage, standards, prompt="Read the story and answer the questions below.", extra=None
):
    data = {"passage": passage, "questions": [{"prompt": prompt, "answer": "x " * 400}]}
    data.update(extra or {})
    return {
        "day": name,
        "title": f"{name} lesson",
        "standards": standards,
        "worksheets": [{"id": f"{name[:3]}-1", "kind": "readingWorksheet", "data": data}],
    }


def week(days, guide="Read the passage aloud to your child, then talk about it.", narrator="Rex"):
    return {
        "title": "Test Week",
        "narrator": narrator,
        "days": days,
        "prep_checks": [{}] * 3,
        "teacher_guide": {
            "title": "Guide",
            "days": [{"day": "Monday", "title": "t", "blocks": [{"paragraphs": [guide]}]}],
        },
    }


def flags(review, level=None):
    return [f.message for f in review.flags if level is None or f.level == level]


def test_reading_grade_ranks_simple_below_hard_and_skips_tiny_text():
    assert wr.reading_grade(SIMPLE) < 2 < wr.reading_grade(HARD)
    assert wr.reading_grade("Too short.") is None


def test_a_clean_week_for_its_grade_looks_good():
    w = week([day("Monday", SIMPLE, ["S.SCI.1"]), day("Tuesday", SIMPLE, ["S.SCI.1"])])
    r = wr.review_week(w, grade=2, skills=SKILLS, planned=["S.SCI.1"])
    assert flags(r, "warn") == [] and r.to_dict()["verdict"] == "Looks good"
    assert [d.day for d in r.days] == ["Monday", "Tuesday"]
    assert r.skills == [
        {
            "id": "S.SCI.1",
            "subject": "Science",
            "description": "plants grow",
            "days": ["Monday", "Tuesday"],
        }
    ]
    assert r.prep_checks == 3


def test_answer_keys_are_not_counted_as_words_the_child_reads():
    r = wr.review_week(week([day("Monday", SIMPLE, ["S.SCI.1"])]), grade=2, skills=SKILLS)
    assert r.days[0].words < 200  # the 400-word answer key is left out


def test_a_passage_two_grades_too_hard_and_hard_questions_are_flagged():
    w = week([day("Monday", SIMPLE, ["S.SCI.1"]), day("Thursday", HARD, ["S.SCI.1"], prompt=HARD)])
    warns = flags(wr.review_week(w, grade=2, skills=SKILLS), "warn")
    assert any("Thursday's reading passage reads at about grade" in m for m in warns)
    assert any("Thursday's questions or instructions read at about grade" in m for m in warns)
    assert any("Reading level climbs" in m for m in flags(wr.review_week(w, grade=2)))


def test_too_many_words_for_the_grade_is_flagged():
    w = week([day("Monday", SIMPLE * 8, ["S.SCI.1"])])
    assert any("words on the page" in m for m in flags(wr.review_week(w, grade=0), "warn"))
    assert not any("words on the page" in m for m in flags(wr.review_week(w, grade=5), "warn"))


def test_read_aloud_guidance_is_recognised_however_it_is_phrased():
    for guide in (
        "Read the passage aloud to your child.",
        "Try reading it aloud together.",
        "A read-aloud day.",
        "Read this to your child slowly.",
    ):
        w = week([day("Monday", SIMPLE, ["S.SCI.1"])], guide=guide)
        assert not any("read aloud" in m for m in flags(wr.review_week(w, grade=1))), guide


def test_missing_read_aloud_guidance_matters_for_young_children_only():
    w = week([day("Monday", SIMPLE, ["S.SCI.1"])], guide="Have fun this week.")
    assert any("read aloud" in m for m in flags(wr.review_week(w, grade=2), "warn"))
    assert not any("read aloud" in m for m in flags(wr.review_week(w, grade=4), "warn"))


def test_skill_curation_planned_but_untaught_single_day_and_subject_spread():
    w = week(
        [
            day("Monday", SIMPLE, ["S.SCI.1"]),
            day("Tuesday", SIMPLE, ["S.SCI.1", "S.MATH.1"]),
            day("Wednesday", SIMPLE, ["S.HIST.1", "S.CS.1", "S.SCI.1"]),
        ]
    )
    r = wr.review_week(w, grade=2, skills=SKILLS, planned=["S.SCI.1", "S.MATH.1", "S.HIST.1",
                                                          "S.CS.1", "S.MISSING.1"])  # fmt: skip
    assert any("S.MISSING.1" in m and "no day teaches it" in m for m in flags(r, "warn"))
    infos = flags(r, "info")
    assert any("S.HIST.1 (History) is taught on Wednesday only" in m for m in infos)
    assert any("spans 4 subjects" in m for m in infos)
    assert any("Wednesday carries 3 skills" in m for m in infos)
    assert r.subjects == ["Computer Science", "History", "Math", "Science"]


def test_the_run_record_feeds_the_review():
    w = week([day("Monday", SIMPLE, ["S.SCI.1"])])
    run = {
        "status": "week_failed",
        "model": "m",
        "cost_usd": 0.1,
        "repairs": 2,
        "uncovered_standards": ["S.MATH.1"],
        "final_errors": ["e" * 500],
    }
    r = wr.review_week(w, grade=2, skills=SKILLS, run=run)
    warns = flags(r, "warn")
    assert any("Authoring ended as week_failed" in m for m in warns)
    assert any("left these skills out: S.MATH.1" in m for m in warns)
    assert any("2 rewrites" in m for m in flags(r, "info"))
    assert r.run["model"] == "m" and len(r.run["final_errors"][0]) == 200
    assert r.flags[0].level == "warn"  # worst first


def test_the_real_fixture_week_reviews_without_error():
    doc = json.loads(
        (Path(__file__).parent / "fixtures" / "weekdoc" / "weather_week.json").read_text()
    )
    r = wr.review_week(doc, grade=1).to_dict()
    assert len(r["days"]) == 5 and r["verdict"]
    assert all(isinstance(d["words"], int) for d in r["days"])
