"""Tests for the pluggable page-chrome layout system."""

from src.worksheet_html_renderer import build_print_packet_html, render_page
from src.worksheet_layouts import LAYOUT_NAMES, get_layout


# ============ Registry ============


def test_known_layouts_are_registered():
    assert "classic" in LAYOUT_NAMES
    assert "journal" in LAYOUT_NAMES


def test_unknown_layout_falls_back_to_classic():
    """A typo in a layout name degrades to classic rather than raising."""
    assert get_layout("does-not-exist").name == "classic"
    assert get_layout(None).name == "classic"
    assert get_layout("").name == "classic"


def test_classic_layout_adds_no_chrome():
    """Classic must pass content through untouched — existing weeks depend on it."""
    inner = "<p>hello</p>"
    assert get_layout("classic").render_page(inner, {}, "#000", "#fff") == inner


def test_classic_layout_contributes_no_css():
    assert get_layout("classic").css == ""


# ============ Journal chrome ============


def test_journal_page_renders_rail_masthead_and_pips():
    html = render_page(
        [("noteBox", {"text": "body content"})],
        {
            "day_label": "Monday",
            "title": "Scout Needs Help",
            "subtitle": "Equal parts",
            "day_index": 1,
            "total_days": 5,
        },
        layout="journal",
    )
    assert "jr-rail" in html
    assert "Scout Needs Help" in html
    assert "Equal parts" in html
    assert "Day 1 of 5" in html
    assert html.count('class="jr-pip"') == 5
    assert "body content" in html


def test_journal_pips_fill_up_to_day_index():
    """Filled pips carry the day colour; remaining pips are outline only."""
    html = render_page(
        [],
        {"day_label": "Wednesday", "day_index": 3, "total_days": 5},
        layout="journal",
    )
    primary = "#7c3aed"  # Wednesday
    filled = f'<div class="jr-pip" style="border-color:{primary};background:{primary};">'
    hollow = f'<div class="jr-pip" style="border-color:{primary};">'
    assert html.count(filled) == 3
    assert html.count(hollow) == 2


def test_journal_status_strip_marks_half_units():
    """filled_halves counts half-hearts, so an odd value half-fills one heart."""
    html = render_page(
        [],
        {
            "day_label": "Monday",
            "status": {
                "label": "Scout's health",
                "hearts": 5,
                "filled_halves": 5,
                "reading": "2.5 / 5",
            },
        },
        layout="journal",
    )
    assert html.count('class="on"') == 5
    assert "2.5 / 5" in html
    assert "Scout&#x27;s health" in html or "Scout's health" in html


def test_journal_name_date_can_be_suppressed():
    with_row = render_page([], {"day_label": "Monday"}, layout="journal")
    without = render_page([], {"day_label": "Monday", "show_name_date": False}, layout="journal")
    assert "jr-meta" in with_row
    assert "jr-meta" not in without


# ============ Packet assembly ============


def test_packet_includes_layout_css_only_when_requested():
    frag = "<p>x</p>"
    classic = build_print_packet_html([("Monday", frag)], "T", layout="classic")
    journal = build_print_packet_html([("Monday", frag)], "T", layout="journal")
    assert ".jr-rail" not in classic
    assert ".jr-rail" in journal


def test_packet_defaults_to_classic_layout():
    """Callers that predate the layout argument keep their original chrome."""
    html = build_print_packet_html([("Monday", "<p>x</p>")], "T")
    assert ".jr-rail" not in html


def test_block_css_is_namespaced_and_always_present():
    """Block CSS ships in every packet but cannot collide with legacy classes."""
    html = build_print_packet_html([("Monday", "<p>x</p>")], "T")
    assert ".fx-story" in html
    # Legacy worksheet classes are untouched by the fx- namespace.
    assert ".passage" in html
    assert ".fx-passage" not in html
