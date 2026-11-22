"""M3.4: the completeness gate rejects each failure class and accepts a complete week."""

import pytest

from authoring.gate import completeness_problems, make_week_check
from tests.authoring_fixtures import STANDARDS, good_week, mutate
from weekdoc import WeekDoc

ALLOWED = set(STANDARDS)


def problems(week: dict, name="Ada"):
    return completeness_problems(
        WeekDoc.model_validate(week), student_first_name=name, allowed_standards=ALLOWED
    )


def test_a_complete_week_passes():
    assert problems(good_week()) == []
    assert make_week_check(student_first_name="Ada", allowed_standards=ALLOWED)(
        WeekDoc.model_validate(good_week())
    ) is None


def _drop_day(w):
    del w["days"][4]
    w["prep_checks"] = [c for c in w["prep_checks"] if c["day"] != "Friday"]
    del w["teacher_guide"]["days"][4]


def _one_ws(w):
    del w["days"][1]["worksheets"][1]


def _few_checks(w):
    w["prep_checks"] = w["prep_checks"][:6]


def _guide_day(w):
    del w["teacher_guide"]["days"][2]


def _no_extension(w):
    w["teacher_guide"]["days"][0]["blocks"] = [
        b for b in w["teacher_guide"]["days"][0]["blocks"] if b.get("style") != "extension"
    ]


def _name(w):
    w["days"][0]["worksheets"][0]["data"]["passage"] = "Ada looks at the sky."


def _missing_answer(w):
    del w["days"][0]["worksheets"][0]["answers"][1]


def _wrong_math(w):
    w["days"][0]["worksheets"][1]["answers"][0]["answer"] = "8"


def _match_unknown(w):
    w["days"][2]["worksheets"][2]["answers"][0]["answer"] = "A cloud"


def _match_identity(w):
    ws = w["days"][2]["worksheets"][2]
    ws["data"]["right_items"] = ["Moving air", "Falling water", "Warm light"]


def _match_dup(w):
    w["days"][2]["worksheets"][2]["answers"][1]["answer"] = "Moving air"


def _placeholder(w):
    w["days"][3]["worksheets"][0]["data"]["passage"] = "TBD later\n\nmore"


def _bad_standard(w):
    w["days"][0]["standards"] = ["VA.SCIENCE.9.9.9"]


def _bad_check_standard(w):
    w["prep_checks"][0]["standard_id"] = "VA.MATH.1.1.1"


def _no_check_friday(w):
    w["prep_checks"] = [c for c in w["prep_checks"] if c["day"] != "Friday"] + [
        dict(w["prep_checks"][0], id=f"x{i}") for i in range(2)
    ]


CASES = [
    (_drop_day, "exactly Monday"),
    (_one_ws, "need at least 2"),
    (_few_checks, "prep checks"),
    (_guide_day, "teacher_guide must have exactly one entry"),
    (_no_extension, "lacks a 'extension' callout"),
    (_name, "name appears literally"),
    (_missing_answer, "answers missing for item_refs questions.1"),
    (_wrong_math, "is wrong; the correct answer is 7"),
    (_match_unknown, "not one of right_items"),
    (_match_identity, "same order as left_items"),
    (_match_dup, "share one right item"),
    (_placeholder, "placeholder text"),
    (_bad_standard, "not in the STANDARDS list"),
    (_bad_check_standard, "not in the STANDARDS list"),
    (_no_check_friday, "no prep check on Friday"),
]


@pytest.mark.parametrize("fn,expect", CASES, ids=[c[0].__name__ for c in CASES])
def test_gate_rejects(fn, expect):
    try:
        week = mutate(fn)
    except Exception:  # pragma: no cover
        raise
    found = problems(week)
    assert any(expect in p for p in found), found


def test_token_is_fine_and_name_match_is_whole_word():
    week = good_week()
    week["days"][0]["worksheets"][0]["data"]["passage"] = "Adapt to {{student_name}}.\n\nOk"
    assert problems(week) == []


def test_speed_math_and_ten_frame_are_recomputed():
    from authoring.gate import _expected_arithmetic

    assert _expected_arithmetic("speedMath", {"problems": [{"a": 9, "op": "-", "b": 4}]}, 0) == 5
    assert _expected_arithmetic("tenFrameWorksheet", {"problems": [{"addend_a": 3, "addend_b": 4}]}, 0) == 7
    assert _expected_arithmetic("readingWorksheet", {}, 0) is None
