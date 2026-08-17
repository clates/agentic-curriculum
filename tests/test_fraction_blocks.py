"""Tests for the fraction manipulative and practice content blocks."""

import re

from src.worksheet_html_renderer import HTML_SUPPORTED_KINDS, render_page, render_worksheet_html


def _render(kind, data):
    return render_worksheet_html(kind, data, "Monday")


# ============ Dispatch registration ============


def test_fraction_blocks_are_registered():
    for kind in (
        "fractionStrips",
        "fractionCircles",
        "fractionArea",
        "fractionNumberLine",
        "heartBar",
        "colorKey",
        "colorTask",
        "calibrationRuler",
        "cutCards",
        "comparePairs",
        "speedMath",
        "storyPanel",
        "doingCard",
        "taskList",
        "richText",
    ):
        assert kind in HTML_SUPPORTED_KINDS, kind


# ============ Fraction strips ============


def test_strip_divides_into_exactly_n_flex_cells():
    """Equal division is delegated to flex, so the cell count must match the denominator."""
    html = _render("fractionStrips", {"strips": [{"denominator": 7}]})
    cells = re.findall(r"<span[^>]*>", html)
    assert len(cells) == 7


def test_strip_width_is_emitted_in_physical_inches():
    """Manipulatives must print at real-world size, so width is in `in`, not px."""
    html = _render("fractionStrips", {"width_in": 6.0, "strips": [{"denominator": 4}]})
    assert "width:6.0in" in html


def test_strip_shading_marks_only_requested_cells():
    html = _render(
        "fractionStrips",
        {"strips": [{"denominator": 4, "shade": [0, 1], "color": "#ff0000"}]},
    )
    assert html.count("background:#ff0000;") == 2


# ============ Fraction circles ============


def test_circle_wedges_use_exact_degree_stops():
    """Six equal wedges means a 60-degree repeating stop."""
    html = _render("fractionCircles", {"circles": [{"parts": 6}]})
    assert "60deg" in html
    assert "border-radius: 50%" in html or "fx-circle" in html


def test_circle_shading_covers_the_right_arc():
    """3 of 8 shaded is 135 degrees of fill."""
    html = _render("fractionCircles", {"circles": [{"parts": 8, "shaded": 3}]})
    assert "135deg" in html


# ============ Area models ============


def test_area_grid_emits_one_cell_per_partition():
    html = _render("fractionArea", {"grids": [{"cols": 4, "rows": 2}]})
    assert html.count("<div></div>") == 8


def test_area_cols_spec_produces_unequal_parts():
    """cols_spec is what makes the 'four pieces but not fourths' distractor possible."""
    html = _render("fractionArea", {"grids": [{"cols_spec": [3, 1, 1, 1], "rows": 1}]})
    assert "grid-template-columns:3fr 1fr 1fr 1fr" in html
    # Still four pieces — that is the point of the distractor.
    assert html.count("<div></div>") == 4


def test_area_equal_and_unequal_render_same_piece_count():
    equal = _render("fractionArea", {"grids": [{"cols": 4, "rows": 1}]})
    unequal = _render("fractionArea", {"grids": [{"cols_spec": [3, 1, 1, 1], "rows": 1}]})
    assert equal.count("<div></div>") == unequal.count("<div></div>") == 4


# ============ Heart bar ============


def test_heart_bar_fills_half_units():
    """7 half-hearts = 3 full hearts plus one left half."""
    html = _render("heartBar", {"hearts": 5, "filled_halves": 7})
    assert html.count('class="on"') == 7


def test_heart_bar_blank_when_zero():
    html = _render("heartBar", {"hearts": 4, "filled_halves": 0})
    assert 'class="on"' not in html


# ============ Number line ============


def test_number_line_emits_one_tick_per_interval():
    html = _render("fractionNumberLine", {"lines": [{"denominator": 8}]})
    assert html.count("fx-nl-tick") == 8


def test_number_line_labels_can_be_suppressed():
    labelled = _render("fractionNumberLine", {"lines": [{"denominator": 4}]})
    bare = _render("fractionNumberLine", {"lines": [{"denominator": 4, "show_labels": False}]})
    assert "fx-nl-lab" in labelled
    assert "fx-nl-lab" not in bare


# ============ Comparison pairs ============


def test_compare_pairs_keeps_each_pair_separate():
    """Rendered as a grid because run-on text collapses whitespace into one blob."""
    html = _render(
        "comparePairs",
        {"pairs": [{"left": "1/2", "right": "1/4"}, {"left": "1/3", "right": "1/6"}]},
    )
    assert html.count("fx-cmp-box") == 2
    assert html.count('class="fx-cmp"') == 2


# ============ Speed math ============


def test_speed_math_numbers_every_problem():
    html = _render("speedMath", {"title": "Warm-Up", "problems": ["1+1", "2+2", "3+3"]})
    assert "1." in html and "2." in html and "3." in html
    assert "Warm-Up" in html


def test_speed_math_head_suppressed_when_unlabelled():
    """Allows reuse as a bare problem grid inside a numbered task."""
    bare = _render("speedMath", {"problems": ["1+1"]})
    titled = _render("speedMath", {"title": "Warm-Up", "problems": ["1+1"]})
    assert "fx-drill-head" not in bare
    assert "fx-drill-head" in titled


# ============ Task list ============


def test_task_list_numbers_from_start_number():
    html = _render(
        "taskList",
        {"start_number": 4, "tasks": [{"prompt": "first"}, {"prompt": "second"}]},
    )
    assert ">4</div>" in html
    assert ">5</div>" in html


def test_task_figure_is_rendered_inline():
    html = _render(
        "taskList",
        {
            "tasks": [
                {
                    "prompt": "Colour it",
                    "figure": {"kind": "fractionCircles", "data": {"circles": [{"parts": 4}]}},
                }
            ]
        },
    )
    assert "fx-circle" in html


def test_unknown_block_kind_is_skipped_not_fatal():
    """A typo should drop one block, not fail the whole week generation."""
    html = render_page(
        [("noteBox", {"text": "kept"}), ("nopeNotAKind", {})],
        {"day_label": "Monday"},
        layout="journal",
    )
    assert "kept" in html


# ============ Escaping ============


def test_block_text_is_html_escaped():
    html = _render("storyPanel", {"who": "Scout", "text": "5 < 8 & 2 > 1"})
    assert "&lt;" in html and "&amp;" in html
    assert "<script" not in html
