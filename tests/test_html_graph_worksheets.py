"""Tests for the HTML bar-graph and pictograph worksheet renderers."""

from src.worksheet_html_renderer import (
    HTML_SUPPORTED_KINDS,
    render_worksheet_html,
)


# ============ Dispatch registration ============


def test_new_graph_kinds_are_registered():
    """Both new kinds are dispatchable via the HTML renderer."""
    assert "barGraphWorksheet" in HTML_SUPPORTED_KINDS
    assert "pictographWorksheet" in HTML_SUPPORTED_KINDS


# ============ Bar graph ============


def test_bar_graph_prefilled_renders_bars_and_questions():
    """A pre-filled bar graph draws a bar per category plus interpretation questions."""
    html = render_worksheet_html(
        "barGraphWorksheet",
        {
            "title": "Favorite Fruit",
            "categories": ["Apple", "Banana", "Grape"],
            "values": [4, 7, 2],
            "y_max": 8,
            "y_step": 1,
            "x_label": "Fruit",
            "y_label": "Votes",
            "show_values": True,
            "questions": [
                {"prompt": "Which fruit got the most votes?", "response_lines": 1},
            ],
        },
        "Tuesday",
    )
    assert html is not None
    # One filled bar per category.
    assert html.count("bg-bar ") == 3 or html.count('class="bg-bar"') == 3
    # Tallest bar (Banana=7 of 8) is taller than the shortest (Grape=2 of 8).
    assert "height:87.5000%" in html  # 7/8
    assert "height:25.0000%" in html  # 2/8
    # Interpretation question rendered.
    assert "Which fruit got the most votes?" in html
    assert "Read the Graph" in html


def test_bar_graph_blank_has_no_bars():
    """With no values supplied the plot is a blank grid (no bar elements)."""
    html = render_worksheet_html(
        "barGraphWorksheet",
        {
            "title": "Count and Graph",
            "categories": ["Red", "Blue", "Green"],
            "y_max": 10,
            "y_step": 1,
        },
        "Monday",
    )
    assert html is not None
    assert 'class="bg-bar"' not in html
    # Lanes still present, one per category.
    assert html.count('class="bg-lane"') == 3
    # y_max=10, step=1 -> 11 gridlines (0..10 inclusive).
    assert html.count('class="bg-gridline"') == 11


def test_bar_graph_clamps_values_over_max():
    """A value above y_max is clamped to the top of the plot (100%)."""
    html = render_worksheet_html(
        "barGraphWorksheet",
        {"categories": ["A"], "values": [20], "y_max": 10, "y_step": 2},
        "Wednesday",
    )
    assert html is not None
    assert "height:100.0000%" in html


# ============ Pictograph ============


def test_pictograph_prefilled_draws_symbols_and_key():
    """A pre-filled pictograph repeats the symbol and shows a scaled key."""
    html = render_worksheet_html(
        "pictographWorksheet",
        {
            "title": "Bugs We Found",
            "symbol": "🐞",
            "per_symbol": 2,
            "unit_label": "bugs",
            "rows": [
                {"label": "Monday", "symbols": 3},
                {"label": "Tuesday", "symbols": 1},
            ],
            "questions": [{"prompt": "How many bugs on Monday?", "response_lines": 1}],
        },
        "Thursday",
    )
    assert html is not None
    # 3 + 1 = 4 symbol icons drawn.
    assert html.count("🐞") == 4 + 1  # +1 for the symbol in the key line
    assert "each 🐞 = 2 bugs" in html
    assert "How many bugs on Monday?" in html


def test_pictograph_blank_uses_empty_cells():
    """A blank pictograph renders empty draw cells instead of symbols."""
    html = render_worksheet_html(
        "pictographWorksheet",
        {
            "symbol": "⭐",
            "blank": True,
            "max_symbols": 6,
            "rows": [{"label": "Team A"}, {"label": "Team B"}],
        },
        "Friday",
    )
    assert html is not None
    # 2 rows * 6 cells each.
    assert html.count('class="pg-cell"') == 12
