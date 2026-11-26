"""The model-facing child context: allowlist, caps, and a grade per subject."""

import json

from model_context import MAX_INTERESTS, MAX_NOTES_CHARS, build_model_context


def test_subject_grades_are_read_and_the_prompt_mentions_both():
    ctx = build_model_context(
        {"name": "Ada Lovelace", "grade_level": 1, "math_grade": 3, "la_grade": 1}
    )
    assert (ctx.math_grade, ctx.la_grade) == (3, 1)
    assert ctx.grade_for("Math") == 3
    assert ctx.grade_for("English") == ctx.grade_for("Science") == 1
    text = ctx.prompt_lines()
    assert "Math grade: Grade 3" in text
    assert "Language arts grade: Grade 1" in text
    assert "Lovelace" not in text


def test_without_subject_grades_everything_follows_the_single_grade():
    ctx = build_model_context({"name": "Ada", "grade_level": 4})
    assert ctx.math_grade is None and ctx.la_grade is None
    assert ctx.grade_for("Math") == ctx.grade_for("English") == 4
    assert "Math grade" not in ctx.prompt_lines()


def test_bad_subject_grades_are_ignored():
    ctx = build_model_context({"grade_level": 2, "math_grade": "3", "la_grade": True})
    assert ctx.math_grade is None and ctx.la_grade is None


def test_interest_and_notes_caps_are_unchanged():
    blob = {"interests": [f"i{n}" for n in range(20)], "notes": "x" * 2000, "grade_level": 2}
    ctx = build_model_context(json.dumps(blob))
    assert len(ctx.interests) == MAX_INTERESTS == 8
    assert len(ctx.parent_notes) == MAX_NOTES_CHARS == 600
