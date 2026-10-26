"""Tests for hop arcs (``jumps``) on the HTML number line renderer."""

from src.worksheet_html_renderer import render_worksheet_html


def _render(task: dict) -> str:
    html = render_worksheet_html("numberLineWorksheet", {"tasks": [task]}, "Monday")
    assert html is not None
    return html


def test_no_jumps_keeps_original_geometry():
    html = _render({"start": 0, "end": 10, "step": 1})
    assert 'viewBox="0 0 760 88"' in html
    assert 'class="nl-jump"' not in html


def test_jumps_draw_one_arc_and_label_each():
    html = _render(
        {
            "start": 0,
            "end": 20,
            "step": 1,
            "jumps": [
                {"from": 8, "to": 10, "label": "+2"},
                {"from": 10, "to": 13, "label": "+3"},
            ],
        }
    )
    assert html.count('class="nl-jump"') == 2
    assert ">+2</text>" in html and ">+3</text>" in html
    assert 'viewBox="0 0 760 124"' in html


def test_backward_jump_and_zero_length_jump():
    html = _render(
        {
            "start": 0,
            "end": 20,
            "step": 1,
            "jumps": [{"from": 15, "to": 9, "label": "-6"}, {"from": 4, "to": 4}],
        }
    )
    assert html.count('class="nl-jump"') == 1
    assert ">-6</text>" in html


def test_hop_space_reserves_headroom_without_arcs():
    html = _render({"start": 0, "end": 20, "step": 1, "hop_space": True})
    assert 'viewBox="0 0 760 124"' in html
    assert 'class="nl-jump"' not in html
