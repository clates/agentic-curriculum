"""Fraction figure kinds (M2.9b)."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.weekdoc import HOSTED_KINDS, WeekDoc, item_refs
from src.weekdoc.kinds import parse_data
from src.weekdoc.render import render_packet
from tests.weekdoc_fixtures import minimal_week

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from worksheet_html_renderer import render_worksheet_html  # noqa: E402

CASES = {
    "fractionStrips": {
        "strips": [
            {"denominator": 4, "label": "shade 3/4", "answer": "3/4"},
            {"denominator": 2, "shade": [0], "color": "#93c5fd", "answer": "1/2"},
        ],
        "width_in": 4.5,
    },
    "fractionCircles": {
        "circles": [
            {"parts": 4, "shaded": 2, "caption": "A", "answer": "2/4"},
            {"parts": 3, "caption": "B"},
        ]
    },
    "fractionArea": {
        "grids": [
            {"cols": 2, "rows": 2, "shaded": [0], "caption": "A", "answer": "1/4"},
            {"cols_spec": [3, 1, 1, 1], "rows": 1, "caption": "C"},
        ],
        "size_in": 0.9,
    },
    "fractionNumberLine": {
        "lines": [
            {"denominator": 4, "prompt": "Mark 3/4", "answers": ["3/4"]},
            {"denominator": 6, "prompt": "Mark 1/2", "answers": ["1/2"], "show_labels": False},
        ],
        "width_in": 5.4,
    },
}
ITEM_REFS = {
    "fractionStrips": ["strips.0", "strips.1"],
    "fractionCircles": ["circles.0", "circles.1"],
    "fractionArea": ["grids.0", "grids.1"],
    "fractionNumberLine": ["lines.0", "lines.1"],
}
LIST_KEY = {
    "fractionStrips": "strips",
    "fractionCircles": "circles",
    "fractionArea": "grids",
    "fractionNumberLine": "lines",
}


@pytest.mark.parametrize("kind", CASES)
def test_valid_data_parses_enumerates_and_renders(kind):
    parse_data(kind, copy.deepcopy(CASES[kind]))
    assert [r.ref for r in item_refs(kind, CASES[kind])] == ITEM_REFS[kind]
    assert render_worksheet_html(kind, CASES[kind], "Monday")


@pytest.mark.parametrize("kind", CASES)
def test_answer_fields_do_not_change_offline_output(kind):
    plain = copy.deepcopy(CASES[kind])
    for item in plain[LIST_KEY[kind]]:
        item.pop("answer", None)
        item.pop("answers", None)
    assert render_worksheet_html(kind, plain, "Monday") == render_worksheet_html(
        kind, CASES[kind], "Monday"
    )


@pytest.mark.parametrize("kind", CASES)
def test_kinds_render_through_a_week_packet(kind):
    week = minimal_week()
    week["days"][0]["worksheets"].append({"id": "fx", "kind": kind, "data": CASES[kind]})
    html = render_packet(WeekDoc.model_validate(week), "Zara")
    assert {
        "fractionStrips": "fx-strips",
        "fractionCircles": "fx-circles",
        "fractionArea": "fx-areas",
        "fractionNumberLine": "fx-nl",
    }[kind] in html


@pytest.mark.parametrize("kind", CASES)
def test_registered_with_enumerator(kind):
    assert HOSTED_KINDS[kind].enumerate is not None


def _bad(kind, **patch):
    data = copy.deepcopy(CASES[kind])
    data[LIST_KEY[kind]][0].update(patch)
    return kind, data


INVALID = [
    _bad("fractionStrips", denominator=0),
    _bad("fractionStrips", denominator=13),
    _bad("fractionStrips", shade=[4], color="red"),
    _bad("fractionStrips", shade=[0], color=""),
    _bad("fractionStrips", answer="5/4"),
    _bad("fractionStrips", answer="1/0"),
    _bad("fractionStrips", answer="three quarters"),
    _bad("fractionStrips", shade=[0, 1], color="red", answer="3/4"),
    _bad("fractionStrips", color="red;background:url(x)"),
    _bad("fractionCircles", parts=0),
    _bad("fractionCircles", shaded=5),
    _bad("fractionCircles", shaded=1, answer="1/2"),
    _bad("fractionArea", shaded=[4]),
    _bad("fractionArea", cols=0),
    _bad("fractionArea", cols_spec=[1, 0]),
    _bad("fractionArea", cols=12, rows=12),
    _bad("fractionArea", answer="1/2"),
    _bad("fractionNumberLine", denominator=0),
    _bad("fractionNumberLine", denominator=1),
    _bad("fractionNumberLine", answers=["1/3"]),
    _bad("fractionNumberLine", answers=["5/4"]),
    _bad("fractionNumberLine", answers=["1/0"]),
]


@pytest.mark.parametrize("kind,data", INVALID)
def test_impossible_variants_fail_loudly(kind, data):
    with pytest.raises(ValidationError):
        parse_data(kind, data)


@pytest.mark.parametrize("kind", CASES)
def test_empty_list_and_extra_fields_fail(kind):
    with pytest.raises(ValidationError):
        parse_data(kind, {LIST_KEY[kind]: []})
    data = copy.deepcopy(CASES[kind])
    data["bogus"] = 1
    with pytest.raises(ValidationError):
        parse_data(kind, data)


def test_equivalent_fraction_answers_are_accepted():
    parse_data("fractionNumberLine", {"lines": [{"denominator": 8, "answers": ["2/8", "1/4"]}]})
    parse_data("fractionCircles", {"circles": [{"parts": 4, "shaded": 2, "answer": "1/2"}]})
