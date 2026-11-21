"""Ordered and gap kinds (M2.2d)."""

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

SEQ = {
    "title": "Water cycle",
    "activity_name": "Rain",
    "steps": [
        {"text": "Rain falls", "correct_order": 3},
        {"text": "Water evaporates", "correct_order": 1},
        {"text": "Clouds form", "correct_order": 2},
    ],
}
FIB = {
    "title": "Fill",
    "segments": [
        {"text": "The"},
        {"gap": 1},
        {"text": "heats the ground."},
        {"newline": True},
        {"text": "Then clouds make"},
        {"gap": 2},
    ],
    "word_bank": ["sun", "rain", "wind"],
}
CASES = {"sequencingWorksheet": SEQ, "fillInBlankWorksheet": FIB}


@pytest.mark.parametrize("kind", CASES)
def test_valid_data_parses_and_renders_with_the_real_renderer(kind):
    parse_data(kind, copy.deepcopy(CASES[kind]))
    html = render_worksheet_html(kind, CASES[kind], "Wednesday")
    assert html and CASES[kind]["title"] in html


def test_item_refs():
    assert [r.ref for r in item_refs("sequencingWorksheet", SEQ)] == [
        "steps.0",
        "steps.1",
        "steps.2",
    ]
    refs = item_refs("fillInBlankWorksheet", FIB)
    assert [r.ref for r in refs] == ["segments.1", "segments.5"]
    assert refs[1].prompt.startswith("gap 2")


def test_segment_union_picks_the_right_variant():
    from src.weekdoc.kinds_ordered import FillInBlankData, GapSeg, NewlineSeg, TextSeg

    d = FillInBlankData.model_validate(FIB)
    assert [type(s) for s in d.segments] == [TextSeg, GapSeg, TextSeg, NewlineSeg, TextSeg, GapSeg]


@pytest.mark.parametrize(
    "kind,mutate",
    [
        ("sequencingWorksheet", lambda d: d["steps"].pop()),
        ("sequencingWorksheet", lambda d: d["steps"][0].update(correct_order=1)),
        ("sequencingWorksheet", lambda d: d["steps"][0].pop("correct_order")),
        ("sequencingWorksheet", lambda d: d["steps"][0].update(image_path="x.png")),
        ("sequencingWorksheet", lambda d: d.update(activity_name="")),
        (
            "fillInBlankWorksheet",
            lambda d: d.update(segments=[{"text": "no gaps"}, {"newline": True}]),
        ),
        ("fillInBlankWorksheet", lambda d: d["segments"].__setitem__(5, {"gap": 3})),
        ("fillInBlankWorksheet", lambda d: d["segments"].__setitem__(1, {"text": "a", "gap": 1})),
        ("fillInBlankWorksheet", lambda d: d["segments"].__setitem__(1, {"oops": 1})),
        ("fillInBlankWorksheet", lambda d: d["segments"].__setitem__(3, {"newline": False})),
        ("fillInBlankWorksheet", lambda d: d.update(word_bank=["only"])),
        ("fillInBlankWorksheet", lambda d: d.update(word_bank=["a", "A", "b"])),
        ("fillInBlankWorksheet", lambda d: d.update(answers={"1": "sun"})),
    ],
)
def test_empty_or_malformed_worksheets_fail_loudly(kind, mutate):
    data = copy.deepcopy(CASES[kind])
    mutate(data)
    with pytest.raises(ValidationError):
        parse_data(kind, data)
