"""Comprehension kinds (M2.2b)."""

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

READING = {
    "title": "Mon",
    "passage": "Zara flies.\n\nShe sings.",
    "vocabulary": [{"term": "sun", "definition": "a star"}],
    "questions": [{"prompt": "Who flies?"}, {"prompt": "Who sings?", "response_lines": 3}],
}
CAUSE = {
    "title": "CE",
    "pairs": [{"cause": "Sun heats water"}, {"cause": "Cloud is full", "effect": "Rain falls"}],
}
ODD = {"title": "Odd", "rows": [{"items": ["cat", "dog", "rock"], "reasoning_lines": 2}]}
FRAYER = {
    "title": "Frayer",
    "entries": [
        {"word": "cloud", "quadrants": {"Definition": "water drops", "Examples": ["cumulus"]}}
    ],
}
CASES = {
    "readingWorksheet": READING,
    "causeEffectWorksheet": CAUSE,
    "oddOneOutWorksheet": ODD,
    "frayerModelWorksheet": FRAYER,
}


@pytest.mark.parametrize("kind", CASES)
def test_valid_data_parses_and_renders_with_the_real_renderer(kind):
    parse_data(kind, copy.deepcopy(CASES[kind]))
    html = render_worksheet_html(kind, CASES[kind], "Monday")
    assert html and CASES[kind]["title"] in html


def test_reading_items():
    assert [r.ref for r in item_refs("readingWorksheet", READING)] == ["questions.0", "questions.1"]


def test_cause_effect_only_blank_effects_are_answerable():
    refs = item_refs("causeEffectWorksheet", CAUSE)
    assert [(r.ref, r.prompt) for r in refs] == [("pairs.0.effect", "Sun heats water")]


def test_odd_one_out_items():
    assert [r.ref for r in item_refs("oddOneOutWorksheet", ODD)] == ["rows.0"]


def test_frayer_items_are_the_unfilled_quadrants():
    refs = [r.ref for r in item_refs("frayerModelWorksheet", FRAYER)]
    assert refs == ["entries.0.quadrants.Characteristics", "entries.0.quadrants.Non-Examples"]


@pytest.mark.parametrize(
    "kind,mutate",
    [
        ("readingWorksheet", lambda d: d.update(questions=[])),
        ("readingWorksheet", lambda d: d.update(passage="  ")),
        ("readingWorksheet", lambda d: d.update(title="")),
        ("readingWorksheet", lambda d: d["questions"][0].update(response_lines=-1)),
        ("readingWorksheet", lambda d: d.update(extra_field=1)),
        ("causeEffectWorksheet", lambda d: d.update(pairs=[])),
        ("causeEffectWorksheet", lambda d: d["pairs"][0].update(cause="")),
        ("oddOneOutWorksheet", lambda d: d.update(rows=[])),
        ("oddOneOutWorksheet", lambda d: d["rows"][0].update(items=["a", "b"])),
        ("frayerModelWorksheet", lambda d: d.update(entries=[])),
        ("frayerModelWorksheet", lambda d: d["entries"][0]["quadrants"].update(Bogus="x")),
        ("frayerModelWorksheet", lambda d: d.update(quadrant_labels=["A", "A"])),
    ],
)
def test_empty_or_malformed_worksheets_fail_loudly(kind, mutate):
    data = copy.deepcopy(CASES[kind])
    mutate(data)
    with pytest.raises(ValidationError):
        parse_data(kind, data)
