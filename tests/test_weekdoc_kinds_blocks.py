"""Layout and narration blocks (M2.9a)."""

from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from src.weekdoc import HOSTED_KINDS, WeekDoc, item_refs
from src.weekdoc.kinds import parse_data
from src.weekdoc.render import render_packet
from tests.weekdoc_fixtures import minimal_week

PNG = "data:image/png;base64,iVBORw0KGgo="
CASES = {
    "doingCard": {"label": "Outside", "text": "Find three leaves."},
    "noteBox": {"text": "Bring a pencil."},
    "heartBar": {"hearts": 3, "filled_halves": 4, "caption": "Health"},
    "colorKey": {"entries": [{"fraction": "1/2", "color_name": "red", "hex": "#ff0000"}]},
    "logoBadge": {"src": PNG, "alt": "logo", "caption": "Today's truck"},
    "calibrationRuler": {"inches": 6},
    "richText": {
        "sections": [
            {
                "heading": "Intro",
                "text": "Para one.\n\nPara two.",
                "bullets": ["a"],
                "rows": [{"k": "Key", "v": "Val"}],
            }
        ]
    },
    "taskList": {
        "tasks": [
            {"prompt": "Count them", "response_lines": 2},
            {"prompt": "Look", "figure": {"kind": "noteBox", "data": {"text": "hi"}}},
        ]
    },
}
MARKERS = {
    "doingCard": "fx-doing",
    "noteBox": "fx-note",
    "heartBar": "fx-hearts",
    "colorKey": "fx-key",
    "logoBadge": "fx-logo-badge",
    "calibrationRuler": "fx-ruler",
    "richText": "fx-rt",
    "taskList": "fx-task",
}


def _week(kind, data):
    w = minimal_week()
    w["days"][0]["worksheets"].append({"id": "x1", "kind": kind, "data": data})
    return WeekDoc.model_validate(w)


@pytest.mark.parametrize("kind", CASES)
def test_registered_and_rendered_through_render_week(kind):
    assert kind in HOSTED_KINDS
    parse_data(kind, copy.deepcopy(CASES[kind]))
    assert MARKERS[kind] in render_packet(_week(kind, CASES[kind]))


def test_waivers_and_task_list_enumerator():
    for k in CASES:
        e = HOSTED_KINDS[k]
        assert (e.enumerate is None) == (k != "taskList")
    assert [r.ref for r in item_refs("taskList", CASES["taskList"])] == ["tasks.0", "tasks.1"]
    assert item_refs("noteBox", CASES["noteBox"]) == []


def test_prep_check_list_and_cut_line_are_not_hosted_kinds():
    assert "prepCheckList" not in HOSTED_KINDS
    assert "cutLine" not in HOSTED_KINDS


def test_free_text_is_escaped():
    evil = "<script>alert(1)</script>"
    tl = {"tasks": [{"prompt": evil, "detail": evil}]}
    rt = {
        "sections": [
            {"heading": evil, "text": evil, "bullets": [evil], "rows": [{"k": evil, "v": evil}]}
        ]
    }
    for kind, data in (("taskList", tl), ("richText", rt)):
        html = render_packet(_week(kind, data))
        assert "<script>alert" not in html and "&lt;script&gt;" in html


BAD = [
    ("doingCard", lambda d: d.update(text="")),
    ("noteBox", lambda d: d.update(text="  ")),
    ("noteBox", lambda d: d.update(extra=1)),
    ("heartBar", lambda d: d.update(filled_halves=7)),
    ("heartBar", lambda d: d.update(hearts=0)),
    ("heartBar", lambda d: d.update(width_in=99)),
    ("colorKey", lambda d: d.update(entries=[])),
    ("colorKey", lambda d: d["entries"][0].update(hex="red;background:url(http://x)")),
    ("logoBadge", lambda d: d.update(src="https://example.com/a.png")),
    ("logoBadge", lambda d: d.update(src="data:image/svg+xml;base64,AAAA")),
    ("logoBadge", lambda d: d.update(src="")),
    ("calibrationRuler", lambda d: d.update(inches=0)),
    ("calibrationRuler", lambda d: d.update(inches=40)),
    ("richText", lambda d: d.update(sections=[])),
    ("richText", lambda d: d["sections"].append({"heading": "empty"})),
    ("taskList", lambda d: d.update(tasks=[])),
    ("taskList", lambda d: d["tasks"][0].update(prompt="")),
    ("taskList", lambda d: d["tasks"][0].update(response_lines=50)),
    ("taskList", lambda d: d["tasks"][1]["figure"].update(kind="nopeKind")),
    ("taskList", lambda d: d["tasks"][1]["figure"].update(data={"text": ""})),
    ("taskList", lambda d: d["tasks"][1]["figure"].update(kind="taskList", data=CASES["taskList"])),
]


@pytest.mark.parametrize("kind,mutate", BAD)
def test_invalid_variants_fail_loudly(kind, mutate):
    data = copy.deepcopy(CASES[kind])
    mutate(data)
    with pytest.raises(ValidationError):
        parse_data(kind, data)
