"""Image-and-grid kinds: colorTask, cutCards, pixelCopyWorksheet (M2.9f)."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.weekdoc import item_refs
from src.weekdoc.kinds import parse_data

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import worksheet_html_renderer as R  # noqa: E402
from worksheet_html_renderer import render_worksheet_html  # noqa: E402

PALETTE = ["#ff0000", "#0000ff", "#ffff00"]
GRID = [[PALETTE[(r + c) % 3] for c in range(6)] for r in range(6)]

PIXEL = {"title": "Pixel Pup", "grid_size": 6, "colors": GRID}
CUT = {"cards": ["0", "1/4", "1/2", "Ada"], "columns": 4}
ENTRIES = [
    {"fraction": "1/2", "color_name": "red", "hex": "#FF0000"},
    {"fraction": "1/4", "color_name": "blue", "hex": "#0000ff"},
]
TASK = {
    "figure": {
        "kind": "fractionCircles",
        "data": {"size_in": 1.6, "circles": [{"parts": 4}]},
    },
    "entries": ENTRIES,
}
CASES = {"pixelCopyWorksheet": PIXEL, "cutCards": CUT, "colorTask": TASK}
MARK = {"pixelCopyWorksheet": "pc-grid", "cutCards": "fx-card", "colorTask": "fx-sw"}


@pytest.mark.parametrize("kind", CASES)
def test_valid_data_parses_and_renders(kind):
    parse_data(kind, copy.deepcopy(CASES[kind]))
    html = render_worksheet_html(kind, CASES[kind], "Monday")
    assert html and MARK[kind] in html


def test_pixel_grid_renders_the_matrix_not_the_placeholder():
    html = render_worksheet_html("pixelCopyWorksheet", PIXEL, "Monday")
    assert html.count("<rect") == 2 * 36
    assert 'fill="#ff0000"' in html and "Colour 3" in html


def test_pixel_render_is_deterministic():
    a = render_worksheet_html("pixelCopyWorksheet", PIXEL, "Monday")
    assert a == render_worksheet_html("pixelCopyWorksheet", copy.deepcopy(PIXEL), "Monday")


def test_pixel_legend_limit_matches_renderer():
    from src.weekdoc.kinds_visual import PIXEL_MAX_COLORS

    assert PIXEL_MAX_COLORS == R._PC_LEGEND_MAX


def test_color_task_hex_is_lowercased():
    d = parse_data("colorTask", TASK)
    assert d.entries[0].hex == "#ff0000"


def test_item_refs():
    assert [r.ref for r in item_refs("colorTask", TASK)] == ["entries.0", "entries.1"]
    assert [r.ref for r in item_refs("pixelCopyWorksheet", PIXEL)][:2] == ["colors.0", "colors.1"]
    assert item_refs("cutCards", CUT) == []


def _grid(n, fn=lambda r, c: PALETTE[(r + c) % 2]):
    return [[fn(r, c) for c in range(n)] for r in range(n)]


@pytest.mark.parametrize(
    "kind,mutate",
    [
        ("pixelCopyWorksheet", lambda d: d.update(colors=[])),
        ("pixelCopyWorksheet", lambda d: d.update(grid_size=5)),
        ("pixelCopyWorksheet", lambda d: d["colors"][2].pop()),
        ("pixelCopyWorksheet", lambda d: d.update(grid_size=3, colors=_grid(3))),
        ("pixelCopyWorksheet", lambda d: d.update(grid_size=33, colors=_grid(33))),
        ("pixelCopyWorksheet", lambda d: d.update(colors=_grid(6, lambda r, c: "#123456"))),
        (
            "pixelCopyWorksheet",
            lambda d: d.update(colors=_grid(6, lambda r, c: f"#00000{(r + c) % 7}")),
        ),
        ("pixelCopyWorksheet", lambda d: d["colors"][0].__setitem__(0, "red")),
        ("pixelCopyWorksheet", lambda d: d["colors"][0].__setitem__(0, 'red" onload="x')),
        ("pixelCopyWorksheet", lambda d: d["colors"][0].__setitem__(0, "#f00")),
        ("pixelCopyWorksheet", lambda d: d.update(image_path="/etc/passwd")),
        ("pixelCopyWorksheet", lambda d: d.update(title="")),
        ("cutCards", lambda d: d.update(cards=[])),
        ("cutCards", lambda d: d.update(cards=["ok", " "])),
        ("cutCards", lambda d: d.update(cards=["x" * 41])),
        ("cutCards", lambda d: d.update(cards=["a"] * 41)),
        ("cutCards", lambda d: d.update(columns=0)),
        ("cutCards", lambda d: d.update(columns=9)),
        ("cutCards", lambda d: d.update(cards=[{"html": "x"}])),
        ("colorTask", lambda d: d.update(entries=[])),
        ("colorTask", lambda d: d["entries"][0].update(hex="red; background:url(x)")),
        ("colorTask", lambda d: d["entries"][1].update(hex="#FF0000")),
        ("colorTask", lambda d: d["entries"][1].update(color_name="Red")),
        ("colorTask", lambda d: d["figure"].update(kind="pixelCopyWorksheet")),
        ("colorTask", lambda d: d["figure"].update(kind="richText")),
        ("colorTask", lambda d: d["figure"]["data"]["circles"][0].update(shaded=5)),
        ("colorTask", lambda d: d["figure"]["data"]["circles"][0].update(shade_color="blue")),
        ("colorTask", lambda d: d["figure"]["data"].update(circles=[])),
        ("colorTask", lambda d: d["figure"]["data"].update(size_in=float("inf"))),
        ("colorTask", lambda d: d["figure"]["data"].update(size_in=99)),
        ("colorTask", lambda d: d["figure"].pop("data")),
        ("colorTask", lambda d: d["figure"].update(extra=1)),
    ],
)
def test_empty_or_malformed_worksheets_fail_loudly(kind, mutate):
    data = copy.deepcopy(CASES[kind])
    mutate(data)
    with pytest.raises(ValidationError):
        parse_data(kind, data)


@pytest.mark.parametrize(
    "figure",
    [
        {"kind": "fractionStrips", "data": {"strips": [{"denominator": 4, "shade": [4]}]}},
        {"kind": "fractionArea", "data": {"grids": [{"cols": 2, "rows": 2, "shaded": [4]}]}},
        {"kind": "fractionArea", "data": {"grids": [{"cols_spec": [0, 1]}]}},
        {"kind": "fractionNumberLine", "data": {"lines": [{"denominator": 1}]}},
        {"kind": "heartBar", "data": {"hearts": 2, "filled_halves": 5}},
    ],
)
def test_color_task_figures_reject_out_of_range(figure):
    with pytest.raises(ValidationError):
        parse_data("colorTask", {"figure": figure, "entries": ENTRIES})


@pytest.mark.parametrize(
    "figure",
    [
        {
            "kind": "fractionStrips",
            "data": {"strips": [{"denominator": 4, "shade": [1], "color": "#ff0000"}]},
        },
        {
            "kind": "fractionArea",
            "data": {"grids": [{"cols_spec": [3, 1, 1, 1], "rows": 1, "shaded": [0]}]},
        },
        {"kind": "fractionNumberLine", "data": {"lines": [{"denominator": 4}]}},
        {"kind": "heartBar", "data": {"hearts": 3, "filled_halves": 3}},
    ],
)
def test_every_figure_kind_renders(figure):
    html = render_worksheet_html("colorTask", {"figure": figure, "entries": ENTRIES}, "Tuesday")
    assert "fx-row" in html and "fx-sw" in html


def test_card_text_is_escaped():
    html = render_worksheet_html("cutCards", {"cards": ["<b>x</b>"]}, "Monday")
    assert "<b>x</b>" not in html and "&lt;b&gt;" in html


def test_render_week_hosts_all_three(tmp_path):
    from src.weekdoc import WeekDoc
    from src.weekdoc.render import render_packet
    from tests.weekdoc_fixtures import minimal_week

    data = minimal_week()
    day = data["days"][0]
    for i, (kind, d) in enumerate(CASES.items()):
        day["worksheets"].append({"id": f"vis{i}", "kind": kind, "data": d})
    html = render_packet(WeekDoc.model_validate(data))
    for mark in MARK.values():
        assert mark in html
