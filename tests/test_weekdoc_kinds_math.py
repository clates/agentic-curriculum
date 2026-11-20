"""K-2 math kinds (M2.2e)."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.weekdoc import HOSTED_KINDS, item_refs
from src.weekdoc.kinds import parse_data

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from worksheet_html_renderer import render_worksheet_html  # noqa: E402

CASES = {
    "twoOperandWorksheet": {
        "title": "Add",
        "problems": [
            {"operand_one": 12, "operand_two": 7},
            {"operand_one": 20, "operand_two": 5, "operator": "-"},
        ],
    },
    "tenFrameWorksheet": {
        "title": "Ten",
        "problems": [{"addend_a": 8, "addend_b": 5, "fill_a": "red", "fill_b": "blue"}],
    },
    "numberLineWorksheet": {
        "title": "Line",
        "tasks": [
            {"prompt": "Fill in", "start": 0, "end": 10, "hidden_positions": [3, 7]},
            {
                "prompt": "Hop",
                "start": 0,
                "end": 20,
                "step": 5,
                "jumps": [{"from": 5, "to": 15, "label": "+10"}],
            },
        ],
    },
    "speedMath": {
        "title": "Warm up",
        "problems": [{"a": 3, "op": "+", "b": 4}, {"a": 9, "op": "-", "b": 2}],
        "columns": 2,
    },
}


@pytest.mark.parametrize("kind", CASES)
def test_valid_data_parses_and_renders_with_the_real_renderer(kind):
    parse_data(kind, copy.deepcopy(CASES[kind]))
    html = render_worksheet_html(kind, CASES[kind], "Monday")
    assert html


def test_speed_math_typed_problems_render_as_equations():
    html = render_worksheet_html("speedMath", CASES["speedMath"], "Monday")
    assert "3 + 4 =" in html and "9 - 2 =" in html


def test_speed_math_legacy_q_form_is_unchanged():
    html = render_worksheet_html("speedMath", {"problems": [{"q": "1/2 + 1/2"}, "3 x 3"]}, "Monday")
    assert "1/2 + 1/2" in html and "3 x 3" in html


def test_item_refs():
    assert len(item_refs("twoOperandWorksheet", CASES["twoOperandWorksheet"])) == 2
    assert item_refs("tenFrameWorksheet", CASES["tenFrameWorksheet"])[0].prompt == "8 + 5"
    assert [r.ref for r in item_refs("numberLineWorksheet", CASES["numberLineWorksheet"])] == [
        "tasks.0",
        "tasks.1",
    ]
    assert item_refs("speedMath", CASES["speedMath"])[1].prompt == "9 - 2"


def test_legacy_math_alias_is_not_hosted():
    assert "mathWorksheet" not in HOSTED_KINDS


@pytest.mark.parametrize(
    "kind,mutate",
    [
        ("twoOperandWorksheet", lambda d: d.update(problems=[])),
        ("twoOperandWorksheet", lambda d: d["problems"][0].update(operand_one=1000)),
        ("twoOperandWorksheet", lambda d: d["problems"][0].update(operand_one=-1)),
        ("twoOperandWorksheet", lambda d: d["problems"][0].update(operator="*")),
        ("twoOperandWorksheet", lambda d: d["problems"][1].update(operand_two=50)),
        ("tenFrameWorksheet", lambda d: d["problems"][0].update(addend_a=11)),
        ("tenFrameWorksheet", lambda d: d["problems"][0].update(fill_a="a-very-long-fill")),
        ("tenFrameWorksheet", lambda d: d.update(problems=[])),
        ("numberLineWorksheet", lambda d: d["tasks"][0].update(hidden_positions=[11])),
        ("numberLineWorksheet", lambda d: d["tasks"][0].update(hidden_positions=[])),
        ("numberLineWorksheet", lambda d: d["tasks"][0].update(step=3, end=9)),
        ("numberLineWorksheet", lambda d: d["tasks"][0].update(end=0)),
        ("numberLineWorksheet", lambda d: d["tasks"][0].update(end=120, step=1)),
        ("numberLineWorksheet", lambda d: d["tasks"][1]["jumps"][0].update(to=7)),
        ("numberLineWorksheet", lambda d: d.update(tasks=[])),
        ("speedMath", lambda d: d["problems"][0].update(a=21)),
        ("speedMath", lambda d: d["problems"][1].update(b=12)),
        ("speedMath", lambda d: d["problems"].append({"q": "free text"})),
        ("speedMath", lambda d: d.update(problems=[])),
        ("speedMath", lambda d: d.update(columns=9)),
    ],
)
def test_out_of_bounds_or_empty_worksheets_fail_loudly(kind, mutate):
    data = copy.deepcopy(CASES[kind])
    mutate(data)
    with pytest.raises(ValidationError):
        parse_data(kind, data)
