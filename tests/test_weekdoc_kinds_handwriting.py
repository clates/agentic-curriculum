"""Handwriting and writing-practice kinds (M2.9c)."""

from __future__ import annotations

import re

import copy

import pytest
from pydantic import ValidationError

from src.weekdoc import WeekDoc, item_refs
from src.weekdoc.kinds import HOSTED_KINDS, parse_data
from src.weekdoc.render import render_packet
from tests.weekdoc_fixtures import minimal_week

SCAFFOLD = {
    "title": "My Pet",
    "topic": "A pet I would like",
    "sections": [
        {"label": "Beginning", "starter": "I would like a", "lines": 2},
        {"label": "Middle"},
        {"label": "End", "starter": "That is why", "lines": 3},
    ],
}
HANDWRITING = {
    "title": "Trace the words",
    "items": [{"text": "cat", "sub_label": "an animal"}, {"text": "dog"}, {"text": "sun"}],
    "rows": 2,
    "cols": 2,
}
ALPHABET = {
    "title": "The letter B",
    "letter": "b",
    "starting_words": ["bat", "ball"],
    "containing_words": ["crab", "tub"],
}
MIRROR_TRACE = {"title": "Secret", "phrase": "hi there", "reveal_note": "Hold it to a mirror!"}
MIRROR_INTRO = {"title": "Flip", "mode": "intro", "letters": ["b", "d", "p"]}
LETTER = {
    "title": "Dear Zara",
    "style": "parchment",
    "incoming": {"greeting": "Dear friend,", "body": "Come to tea.\n\nBring a hat.", "seal": "Z"},
    "reply": {
        "paragraphs": [{"starter": "Thank you for", "lines": 2}, {"lines": 3}],
        "closing_options": ["Sincerely,", "Your friend,"],
    },
    "word_bank": ["tea", "hat"],
    "checklist": ["I used a capital letter", "I signed my name"],
    "envelope": {"to": "Zara", "from": "Me"},
}
CASES = {
    "writingScaffoldWorksheet": SCAFFOLD,
    "handwritingWorksheet": HANDWRITING,
    "alphabetWorksheet": ALPHABET,
    "mirrorMessageWorksheet": MIRROR_TRACE,
    "letterWorksheet": LETTER,
}
MARKERS = {
    "writingScaffoldWorksheet": "scaffold-section",
    "handwritingWorksheet": "hw-grid",
    "alphabetWorksheet": "abc-centerpiece",
    "mirrorMessageWorksheet": "mm-trace-row",
    "letterWorksheet": "lt-card",
}


def _render(kind, data):
    week = minimal_week()
    week["days"][0]["worksheets"].append({"id": "ws-x", "kind": kind, "data": copy.deepcopy(data)})
    return render_packet(WeekDoc.model_validate(week), "Zara")


@pytest.mark.parametrize("kind", CASES)
def test_registered_and_renders_through_render_week(kind):
    assert kind in HOSTED_KINDS
    html = _render(kind, CASES[kind])
    assert MARKERS[kind] in html
    assert CASES[kind]["title"] in html


def test_mirror_intro_mode_renders():
    assert "mm-intro-pair" in _render("mirrorMessageWorksheet", MIRROR_INTRO)


def test_no_image_or_network_references_are_rendered():
    for kind, data in CASES.items():
        html = _render(kind, data)
        assert "<img" not in html and "http://" not in html.replace("http://www.w3.org", "")
        assert "@import" not in html
        # Fonts are allowed only when embedded: every url() is inline data or an in-page #ref.
        for url in re.findall(r"url\(\s*['\"]?([^)'\"]*)", html):
            assert url.startswith(("data:", "#")), url


def test_waivers_and_enumerators_split_as_designed():
    for kind in ("handwritingWorksheet", "alphabetWorksheet", "mirrorMessageWorksheet"):
        assert HOSTED_KINDS[kind].waiver and item_refs(kind, CASES[kind]) == []
    for kind in ("writingScaffoldWorksheet", "letterWorksheet"):
        assert HOSTED_KINDS[kind].enumerate is not None


def test_scaffold_prompts_are_enumerated():
    refs = item_refs("writingScaffoldWorksheet", SCAFFOLD)
    assert [r.ref for r in refs] == ["sections.0", "sections.1", "sections.2"]
    assert refs[0].prompt == "Beginning: I would like a"
    assert refs[1].prompt == "Middle"


def test_letter_reply_and_checklist_are_enumerated():
    refs = item_refs("letterWorksheet", LETTER)
    assert [r.ref for r in refs] == [
        "reply.paragraphs.0",
        "reply.paragraphs.1",
        "checklist.0",
        "checklist.1",
    ]
    assert item_refs("letterWorksheet", {"title": "t", "incoming": {"body": "hi there"}}) == []


def test_letter_accepts_boolean_envelope_and_rejects_string_incoming_shortcut():
    parse_data("letterWorksheet", {**LETTER, "envelope": True})
    with pytest.raises(ValidationError):
        parse_data("letterWorksheet", {**LETTER, "incoming": "plain string"})


def test_free_text_is_escaped():
    data = {**SCAFFOLD, "title": "<script>x</script>"}
    html = _render("writingScaffoldWorksheet", data)
    assert "<script>x" not in html and "&lt;script&gt;" in html


def _del(key):
    return lambda d: d.pop(key)


@pytest.mark.parametrize(
    "kind,mutate",
    [
        ("writingScaffoldWorksheet", lambda d: d.update(sections=[])),
        ("writingScaffoldWorksheet", lambda d: d["sections"][0].update(lines=0)),
        ("writingScaffoldWorksheet", lambda d: d["sections"][0].update(label="")),
        ("writingScaffoldWorksheet", lambda d: d["sections"].__setitem__(0, "Beginning")),
        ("writingScaffoldWorksheet", lambda d: d.update(sections=[{"label": "x"}] * 9)),
        ("writingScaffoldWorksheet", _del("title")),
        ("handwritingWorksheet", lambda d: d.update(items=[])),
        ("handwritingWorksheet", lambda d: d["items"][0].update(image_path="http://x/y.png")),
        ("handwritingWorksheet", lambda d: d.update(rows=1, cols=1)),
        ("handwritingWorksheet", lambda d: d.update(cols=0)),
        ("handwritingWorksheet", lambda d: d["items"][0].update(text="")),
        ("handwritingWorksheet", lambda d: d["items"][0].update(text="two words")),
        ("alphabetWorksheet", lambda d: d.update(letter="bb")),
        ("alphabetWorksheet", lambda d: d.update(letter="")),
        ("alphabetWorksheet", lambda d: d.update(letter="7")),
        ("alphabetWorksheet", lambda d: d.update(starting_words=[])),
        ("alphabetWorksheet", lambda d: d.update(starting_words=["cat"])),
        ("alphabetWorksheet", lambda d: d.update(containing_words=["cat"])),
        ("alphabetWorksheet", lambda d: d.update(character_image_path="http://x/y.png")),
        ("mirrorMessageWorksheet", _del("phrase")),
        ("mirrorMessageWorksheet", lambda d: d.update(phrase="")),
        ("mirrorMessageWorksheet", lambda d: d.update(phrase="x" * 21)),
        ("mirrorMessageWorksheet", lambda d: d.update(phrase="<b>")),
        ("mirrorMessageWorksheet", lambda d: d.update(letters=["b"])),
        ("mirrorMessageWorksheet", lambda d: d.update(mode="spin")),
        ("mirrorMessageWorksheet", lambda d: d.update(mode="intro", letters=[], phrase=None)),
        ("mirrorMessageWorksheet", lambda d: d.update(mode="intro", letters=["bd"], phrase=None)),
        ("mirrorMessageWorksheet", lambda d: d.update(mode="intro", letters=["b"])),
        ("letterWorksheet", lambda d: (d.pop("incoming"), d.pop("reply"))),
        ("letterWorksheet", lambda d: d["incoming"].update(body="")),
        ("letterWorksheet", lambda d: d["incoming"].update(seal="ab")),
        ("letterWorksheet", lambda d: d["reply"].update(paragraphs=[])),
        ("letterWorksheet", lambda d: d["reply"]["paragraphs"][0].update(lines=0)),
        ("letterWorksheet", lambda d: d.update(style="neon")),
        ("letterWorksheet", lambda d: d.update(checklist=[""])),
        ("letterWorksheet", lambda d: d.update(envelope={"to": "Z", "cc": "x"})),
    ],
)
def test_empty_or_invalid_variants_fail_loudly(kind, mutate):
    data = copy.deepcopy(CASES[kind])
    mutate(data)
    with pytest.raises(ValidationError):
        parse_data(kind, data)
