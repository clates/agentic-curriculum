"""Graph, compare and math-alias kinds (M2.9d)."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.weekdoc import item_refs
from src.weekdoc.kinds import parse_data
from src.weekdoc.kinds_graphs import (
    compare_answer,
    graph_answer,
    graph_values,
    two_operand_answer,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from worksheet_html_renderer import render_worksheet_html  # noqa: E402

Q = [{"prompt": "Which has the most?"}, {"prompt": "How many in all?", "response_lines": 2}]
CASES = {
    "barGraphWorksheet": {
        "title": "Pets <b>",
        "categories": ["Dogs", "Cats", "Fish"],
        "values": [4, 7, 2],
        "y_max": 8,
        "y_step": 2,
        "questions": Q,
    },
    "pictographWorksheet": {
        "title": "Fruit",
        "symbol": "🍎",
        "per_symbol": 2,
        "rows": [{"label": "Apples", "symbols": 3}, {"label": "Pears", "symbols": 5}],
        "questions": Q,
    },
    "comparePairs": {
        "pairs": [{"left": "3/8", "right": "5/8"}, {"left": "0.5", "right": "1/2"}],
        "columns": 2,
    },
    "mathWorksheet": {
        "title": "Add",
        "problems": [{"operand_one": 12, "operand_two": 7}],
    },
}
MARKERS = {
    "barGraphWorksheet": "bg-bar",
    "pictographWorksheet": "pg-row",
    "comparePairs": "fx-cmp-grid",
    "mathWorksheet": "to-problem",
}


@pytest.mark.parametrize("kind", CASES)
def test_valid_data_parses_and_renders_with_the_real_renderer(kind):
    parse_data(kind, copy.deepcopy(CASES[kind]))
    html = render_worksheet_html(kind, CASES[kind], "Monday")
    assert html and MARKERS[kind] in html


def test_free_text_is_escaped():
    html = render_worksheet_html("barGraphWorksheet", CASES["barGraphWorksheet"], "Monday")
    assert "Pets <b>" not in html and "Pets &lt;b&gt;" in html


def test_item_refs():
    assert [r.ref for r in item_refs("barGraphWorksheet", CASES["barGraphWorksheet"])] == [
        "questions.0",
        "questions.1",
    ]
    assert len(item_refs("pictographWorksheet", CASES["pictographWorksheet"])) == 2
    assert item_refs("comparePairs", CASES["comparePairs"])[0].prompt == "3/8 ? 5/8"
    assert item_refs("mathWorksheet", CASES["mathWorksheet"])[0].ref == "problems.0"


def test_blank_graphs_enumerate_their_bars_and_rows():
    bar = {"title": "B", "categories": ["a", "b"]}
    assert [r.ref for r in item_refs("barGraphWorksheet", bar)] == ["categories.0", "categories.1"]
    pic = {"title": "P", "blank": True, "rows": [{"label": "x"}]}
    assert [r.ref for r in item_refs("pictographWorksheet", pic)] == ["rows.0"]
    assert render_worksheet_html("pictographWorksheet", pic, "Monday")


def test_graph_answers_are_computed():
    bar = parse_data("barGraphWorksheet", CASES["barGraphWorksheet"])
    assert graph_values(bar) == {"Dogs": 4, "Cats": 7, "Fish": 2}
    assert graph_answer(bar, "most") == "Cats"
    assert graph_answer(bar, "least") == "Fish"
    assert graph_answer(bar, "total") == 13
    assert graph_answer(bar, "difference", "Cats", "Dogs") == 3
    pic = parse_data("pictographWorksheet", CASES["pictographWorksheet"])
    assert graph_answer(pic, "value", "Pears") == 10  # 5 symbols x 2
    assert graph_answer(pic, "total") == 16


def test_graph_answer_edge_cases():
    tie = parse_data(
        "barGraphWorksheet",
        {"title": "T", "categories": ["a", "b"], "values": [3, 3], "questions": Q},
    )
    with pytest.raises(ValueError):
        graph_answer(tie, "most")
    with pytest.raises(KeyError):
        graph_answer(tie, "value", "zzz")
    with pytest.raises(ValueError):
        graph_values(parse_data("barGraphWorksheet", {"title": "T", "categories": ["a"]}))


def test_compare_and_two_operand_answers():
    assert compare_answer("3/8", "5/8") == "<"
    assert compare_answer("0.5", "1/2") == "="
    assert compare_answer("9", "2") == ">"
    assert compare_answer("cat", "2") is None
    assert compare_answer("1/0", "2") is None
    assert two_operand_answer(12, "+", 7) == 19
    assert two_operand_answer(20, "-", 5) == 15


@pytest.mark.parametrize(
    "kind,mutate",
    [
        ("barGraphWorksheet", lambda d: d.update(categories=[])),
        ("barGraphWorksheet", lambda d: d.update(values=[])),
        ("barGraphWorksheet", lambda d: d.update(values=[4, 7])),  # series shorter than labels
        ("barGraphWorksheet", lambda d: d.update(values=[4, 7, 2, 1])),
        ("barGraphWorksheet", lambda d: d.update(values=[4, 9, 2])),  # above y_max
        ("barGraphWorksheet", lambda d: d.update(values=[4, -1, 2])),
        ("barGraphWorksheet", lambda d: d.update(values=[4, None, 2])),
        ("barGraphWorksheet", lambda d: d.update(categories=["a", "a", "b"])),
        ("barGraphWorksheet", lambda d: d.update(y_max=0)),
        ("barGraphWorksheet", lambda d: d.update(y_step=3)),  # 8 is not a multiple of 3
        ("barGraphWorksheet", lambda d: d.update(y_max=1000, y_step=1)),  # 1000 steps
        ("barGraphWorksheet", lambda d: d.update(questions=[])),  # bars to read, nothing asked
        ("barGraphWorksheet", lambda d: d.update(bogus=1)),
        ("pictographWorksheet", lambda d: d.update(rows=[])),
        ("pictographWorksheet", lambda d: d["rows"][0].update(symbols=16)),
        ("pictographWorksheet", lambda d: d["rows"][0].update(symbols=-1)),
        ("pictographWorksheet", lambda d: d["rows"][0].pop("symbols")),
        ("pictographWorksheet", lambda d: d.update(per_symbol=0)),
        ("pictographWorksheet", lambda d: d["rows"][1].update(label="Apples")),
        ("pictographWorksheet", lambda d: d.update(questions=[])),
        ("pictographWorksheet", lambda d: d.update(blank=True)),  # blank with counts given
        ("comparePairs", lambda d: d.update(pairs=[])),
        ("comparePairs", lambda d: d["pairs"][0].update(left="")),
        ("comparePairs", lambda d: d["pairs"][0].update(right="x" * 21)),
        ("comparePairs", lambda d: d.update(columns=0)),
        ("comparePairs", lambda d: d["pairs"].append("3 4")),  # legacy string pair
        ("mathWorksheet", lambda d: d.update(problems=[])),
        ("mathWorksheet", lambda d: d["problems"][0].update(operand_one=1000)),
        ("mathWorksheet", lambda d: d["problems"][0].update(operator="-", operand_two=50)),
    ],
)
def test_empty_or_inconsistent_worksheets_fail_loudly(kind, mutate):
    data = copy.deepcopy(CASES[kind])
    mutate(data)
    with pytest.raises(ValidationError):
        parse_data(kind, data)
