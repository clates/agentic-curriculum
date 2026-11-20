"""Parent Prep Sheet render block (M2.3)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from worksheet_html_renderer import (  # noqa: E402
    HTML_SUPPORTED_KINDS,
    build_print_packet_html,
    render_worksheet_html,
)

CHECKS = [
    {
        "id": "c1",
        "day": "Monday",
        "kind": "oral",
        "prompt": "Ask: what does the sun do to the ground?",
        "pass_criteria": "Says it warms the ground & air.",
        "standard_id": "VA.SCIENCE.K.k.6",
    },
    {
        "day": "Friday",
        "kind": "quiz",
        "prompt": "Name two weather tools.",
        "pass_criteria": "Any two of thermometer, rain gauge, anemometer.",
    },
]


def test_block_is_a_registered_kind():
    assert "prepCheckList" in HTML_SUPPORTED_KINDS


def test_one_card_per_check_with_all_the_fields_and_tick_boxes():
    html = render_worksheet_html("prepCheckList", {"checks": CHECKS}, "")
    assert html.count('class="pc-card"') == 2
    for text in (
        "Monday",
        "oral",
        "Friday",
        "quiz",
        "what does the sun do",
        "A good answer sounds like",
    ):
        assert text in html
    assert html.count("Got it") == 2 and html.count("Shaky") == 2 and html.count("Missed") == 2
    assert html.count('class="pc-box"') == 6
    assert "VA.SCIENCE" not in html  # standards ids are for stored results, not paper


def test_text_is_escaped():
    bad = [
        {"day": "Monday", "kind": "oral", "prompt": "<script>x</script>", "pass_criteria": "a & b"}
    ]
    html = render_worksheet_html("prepCheckList", {"checks": bad}, "")
    assert "<script>" not in html and "&lt;script&gt;" in html and "a &amp; b" in html


def test_title_and_instructions_and_packet_embedding():
    html = render_worksheet_html(
        "prepCheckList",
        {"title": "Prep: Weather", "instructions": "Tick one box.", "checks": CHECKS},
        "",
    )
    assert "Prep: Weather" in html and "Tick one box." in html
    doc = build_print_packet_html([("", html)], "Prep")
    assert doc.count('class="pc-card"') == 2


def test_empty_checks_render_only_the_title():
    html = render_worksheet_html("prepCheckList", {"checks": []}, "")
    assert 'pc-card"' not in html and "Parent Prep Sheet" in html
