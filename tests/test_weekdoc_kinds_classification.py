"""Classification and grid kinds (M2.2c)."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.weekdoc import item_refs
from src.weekdoc.kinds import parse_data

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from worksheet_html_renderer import render_worksheet_html  # noqa: E402

CASES = {
    "wordSortWorksheet": {
        "title": "Sort",
        "categories": [{"label": "Sunny"}, "Rainy"],
        "tiles": ["bright", "puddle", "warm"],
    },
    "treeMapWorksheet": {
        "title": "Tree",
        "root_label": "Weather",
        "branches": [{"label": "Tools", "slot_count": 2}, {"name": "Clouds", "blank_count": 1}],
        "word_bank": ["Rain gauge", "Barometer", "Cirrus"],
    },
    "tChartWorksheet": {"title": "T", "columns": ["Hot", "Cold"], "row_count": 4},
    "featureMatrixWorksheet": {
        "title": "FM",
        "items": ["Cumulus", "Cirrus"],
        "properties": ["Puffy", "Wispy"],
    },
    "matchingWorksheet": {
        "title": "Match",
        "left_items": ["Wind", "Rain"],
        "right_items": ["Moving air", "Falling water"],
    },
}


@pytest.mark.parametrize("kind", CASES)
def test_valid_data_parses_and_renders_with_the_real_renderer(kind):
    parse_data(kind, copy.deepcopy(CASES[kind]))
    html = render_worksheet_html(kind, CASES[kind], "Tuesday")
    assert html and CASES[kind]["title"] in html


def test_item_refs():
    refs = lambda k: [r.ref for r in item_refs(k, CASES[k])]  # noqa: E731
    assert refs("wordSortWorksheet") == ["tiles.0", "tiles.1", "tiles.2"]
    assert refs("treeMapWorksheet") == ["branches.0", "branches.1"]
    assert refs("tChartWorksheet") == ["columns.0", "columns.1"]
    assert refs("featureMatrixWorksheet") == ["items.0", "items.1"]
    assert refs("matchingWorksheet") == ["left_items.0", "left_items.1"]


@pytest.mark.parametrize(
    "kind,mutate",
    [
        ("wordSortWorksheet", lambda d: d.update(tiles=["only"])),
        ("wordSortWorksheet", lambda d: d.update(tiles=["a", "A"])),
        ("wordSortWorksheet", lambda d: d.update(categories=["one"])),
        ("wordSortWorksheet", lambda d: d.update(categories=["x", "y", "z"], tiles=["a", "b"])),
        ("treeMapWorksheet", lambda d: d.update(word_bank=["a", "b"])),
        ("treeMapWorksheet", lambda d: d["branches"][0].update(name="Both")),
        ("treeMapWorksheet", lambda d: d["branches"][0].update(blank_count=1)),
        ("treeMapWorksheet", lambda d: d["branches"][1].update(blank_count=0)),
        ("treeMapWorksheet", lambda d: d.update(branches=d["branches"][:1])),
        ("treeMapWorksheet", lambda d: d.update(root_label="")),
        ("tChartWorksheet", lambda d: d.update(columns=["only"])),
        ("tChartWorksheet", lambda d: d.update(row_count=0)),
        ("featureMatrixWorksheet", lambda d: d.update(items=[])),
        ("featureMatrixWorksheet", lambda d: d.update(properties=[])),
        ("featureMatrixWorksheet", lambda d: d.update(items=[{"name": "dict items are PIL-only"}])),
        ("matchingWorksheet", lambda d: d.update(right_items=["just one", "two", "three"])),
        ("matchingWorksheet", lambda d: d.update(right_items=["same", "same"])),
        ("matchingWorksheet", lambda d: d.update(left_items=[], right_items=[])),
    ],
)
def test_empty_or_malformed_worksheets_fail_loudly(kind, mutate):
    data = copy.deepcopy(CASES[kind])
    mutate(data)
    with pytest.raises(ValidationError):
        parse_data(kind, data)
