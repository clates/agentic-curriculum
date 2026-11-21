<<<<<<< HEAD
"""Diagram, map and picture kinds (M2.9e), including the hosted image rule."""
=======
"""Image-and-grid kinds: colorTask, cutCards, pixelCopyWorksheet (M2.9f)."""
>>>>>>> o/m2-9f

from __future__ import annotations

import copy
<<<<<<< HEAD
=======
import sys
from pathlib import Path
>>>>>>> o/m2-9f

import pytest
from pydantic import ValidationError

<<<<<<< HEAD
from src.weekdoc import WeekDoc, item_refs
from src.weekdoc.kinds import parse_data
from src.weekdoc.render import render_packet
from tests.weekdoc_fixtures import minimal_week

SHAPES = [{"type": "circle", "color": "#22d3ee"}, {"type": "square"}]

CASES = {
    "labeledDiagramWorksheet": (
        "Parts of a Plant",
        {
            "title": "Parts of a Plant",
            "word_bank": True,
            "labels": [
                {"number": 1, "answer": "root", "hint": "underground"},
                {"number": 2, "answer": "stem"},
            ],
        },
    ),
    "vennDiagramWorksheet": (
        "Frogs and Toads",
        {
            "title": "Frogs and Toads",
            "left_label": "Frog",
            "right_label": "Toad",
            "left_items": ["smooth skin"],
            "word_bank": ["bumpy skin", "lays eggs", "long legs"],
        },
    ),
    "storyMapWorksheet": (
        "Story Map",
        {
            "title": "Story Map",
            "fields": [
                {"label": "Characters"},
                {"label": "Setting", "prompt": "Where?", "lines": 3},
            ],
        },
    ),
    "pictureSequenceWorksheet": (
        "Plant a Seed",
        {
            "title": "Plant a Seed",
            "steps": [
                {"emoji": "🌱", "text": "It sprouts"},
                {"emoji": "🕳️", "text": "Dig a hole"},
                {"emoji": "🌻", "text": "It blooms"},
            ],
        },
    ),
    "errorAuditWorksheet": (
        "Clock Doctor",
        {
            "title": "Clock Doctor",
            "legend": ["Hands swapped", "Wrong number"],
            "fix_mode": "redraw",
            "specimens": [
                {
                    "prompt": "Rory says this is 3:30",
                    "art": {"kind": "clock", "hour": 3, "minute": 30},
                },
                {
                    "prompt": "Split into equal parts",
                    "art": {"kind": "partitions", "parts": 4, "broken": 1},
                    "starter_art": {"parts": 4},
                },
            ],
        },
    ),
}
SHAPE_CASES = {
    "gallery": {"shapes": SHAPES, "word_bank": ["circle", "square"]},
    "attributes": {"shapes": SHAPES},
    "pattern": {"shapes": SHAPES + [{"type": "circle"}, {"blank": True}]},
    "sort": {"shapes": SHAPES, "categories": ["Round", "Straight"]},
    "mirror_match": {
        "shapes": [
            {
                "type": "triangle",
                "options": [{"type": "triangle", "flipped": True}, {"type": "square"}],
            }
        ]
    },
}
for _mode, _body in SHAPE_CASES.items():
    CASES[f"shapeIdWorksheet:{_mode}"] = ("Shapes", {"title": "Shapes", "mode": _mode, **_body})


# One sample per kind (kind -> data), for the every-hosted-kind golden test.
SAMPLES = {
    _k.split(":")[0]: _v[1] for _k, _v in CASES.items() if ":" not in _k or _k.endswith(":gallery")
}


def _kind(key: str) -> str:
    return key.split(":")[0]


def _week(key: str, marker: str, data: dict) -> WeekDoc:
    w = minimal_week()
    w["days"][0]["worksheets"].append({"id": "ws-x", "kind": _kind(key), "data": data})
    return WeekDoc.model_validate(w)


@pytest.mark.parametrize("key", CASES)
def test_valid_data_renders_through_render_week(key):
    marker, data = CASES[key]
    parse_data(_kind(key), copy.deepcopy(data))
    html = render_packet(_week(key, marker, data), "Tobin")
    assert marker in html
    assert item_refs(_kind(key), data), "kind must address at least one item"


@pytest.mark.parametrize("key", CASES)
def test_rendering_is_deterministic(key):
    marker, data = CASES[key]
    assert render_packet(_week(key, marker, data)) == render_packet(_week(key, marker, data))


def test_item_refs():
    refs = lambda k: [r.ref for r in item_refs(_kind(k), CASES[k][1])]  # noqa: E731
    assert refs("labeledDiagramWorksheet") == ["labels.0", "labels.1"]
    assert refs("vennDiagramWorksheet") == ["word_bank.0", "word_bank.1", "word_bank.2"]
    assert refs("storyMapWorksheet") == ["fields.0", "fields.1"]
    assert refs("pictureSequenceWorksheet") == ["steps.0", "steps.1", "steps.2"]
    assert refs("errorAuditWorksheet") == ["specimens.0", "specimens.1"]
    assert refs("shapeIdWorksheet:pattern") == ["shapes.3"]  # only the blank cell is asked


def test_answers_must_address_a_real_item():
    w = minimal_week()
    data = CASES["pictureSequenceWorksheet"][1]
    ok = {"id": "p", "kind": "pictureSequenceWorksheet", "data": data}
    w["days"][0]["worksheets"].append({**ok, "answers": [{"item_ref": "steps.1", "answer": "1"}]})
    WeekDoc.model_validate(w)
    w["days"][0]["worksheets"][-1]["answers"][0]["item_ref"] = "steps.9"
    with pytest.raises(ValidationError):
        WeekDoc.model_validate(w)


# ── the image rule ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "kind,patch",
    [
        ("labeledDiagramWorksheet", {"image_path": "https://example.com/x.png"}),
        ("labeledDiagramWorksheet", {"image_path": "/etc/passwd"}),
        ("storyMapWorksheet", {"image_path": "x.png"}),
        ("errorAuditWorksheet", {"show_answers": True}),
    ],
)
def test_no_image_paths_or_answer_mode_in_hosted_data(kind, patch):
    data = copy.deepcopy(CASES[kind][1])
    data.update(patch)
=======
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
>>>>>>> o/m2-9f
    with pytest.raises(ValidationError):
        parse_data(kind, data)


<<<<<<< HEAD
def test_labeled_diagram_prints_the_placeholder_box_with_no_img_tag():
    marker, data = CASES["labeledDiagramWorksheet"]
    html = render_packet(_week("labeledDiagramWorksheet", marker, data))
    assert "ld-diagram-placeholder" in html and "<img" not in html


@pytest.mark.parametrize("color", ['red" onload="x', "red", "#12", "url(http://x)", "#gggggg"])
def test_colors_must_be_hex_because_the_renderer_does_not_escape_them(color):
    data = {"title": "S", "mode": "attributes", "shapes": [{"type": "circle", "color": color}]}
    with pytest.raises(ValidationError):
        parse_data("shapeIdWorksheet", data)


def test_text_is_escaped_in_every_text_kind():
    evil = "<script>alert(1)</script>"
    for key in ("labeledDiagramWorksheet", "vennDiagramWorksheet", "storyMapWorksheet"):
        marker, data = CASES[key]
        data = copy.deepcopy(data)
        data["title"] = evil
        html = render_packet(_week(key, marker, data))
        assert evil not in html and "&lt;script&gt;" in html


# ── invalid variants fail loudly ────────────────────────────────────────────


def _bad(key, mutate):
    data = copy.deepcopy(CASES[key][1])
    mutate(data)
    with pytest.raises(ValidationError):
        parse_data(_kind(key), data)


L, V, S, P, E = (
    "labeledDiagramWorksheet",
    "vennDiagramWorksheet",
    "storyMapWorksheet",
    "pictureSequenceWorksheet",
    "errorAuditWorksheet",
)


@pytest.mark.parametrize(
    "key,mutate",
    [
        (L, lambda d: d.update(labels=[])),
        (L, lambda d: d.update(labels=d["labels"][:1])),
        (L, lambda d: d["labels"][1].update(number=1)),
        (L, lambda d: d["labels"][1].update(answer="ROOT")),
        (L, lambda d: d.update(title="")),
        (L, lambda d: d.update(instructions=None)),
        (V, lambda d: d.update(word_bank=[])),
        (V, lambda d: d.update(left_label="frog", right_label="Frog")),
        (V, lambda d: d.update(word_bank=["bumpy", "Bumpy"])),
        (V, lambda d: d.update(word_bank=["smooth skin", "x"])),
        (V, lambda d: d.update(left_items=["a"] * 7)),
        (V, lambda d: d.update(right_label="")),
        (S, lambda d: d.update(fields=[])),
        (S, lambda d: d.update(fields=[{"label": "A"}, {"label": "a"}])),
        (S, lambda d: d["fields"][0].update(lines=0)),
        (S, lambda d: d["fields"][0].update(value="answer in data")),
        (P, lambda d: d.update(steps=d["steps"][:2])),
        (P, lambda d: d["steps"][0].update(emoji="sprout")),
        (P, lambda d: d["steps"][0].update(emoji="")),
        (P, lambda d: d["steps"][1].update(text="It sprouts")),
        (E, lambda d: d.update(specimens=[])),
        (E, lambda d: d["specimens"][0].pop("art")),  # no lines and no art
        (E, lambda d: d["specimens"][0]["art"].update(minute=75)),
        (E, lambda d: d["specimens"][1]["art"].update(broken=4)),
        (E, lambda d: d["specimens"][1]["art"].update(parts=99)),
        (E, lambda d: d["specimens"][0]["art"].update(kind="image")),
        (E, lambda d: d.update(fix_mode="rewrite")),  # starter_art needs redraw
        (E, lambda d: d.update(columns=3)),
        (E, lambda d: d["specimens"][0].update(bug_location="in data")),
    ],
)
def test_empty_or_malformed_worksheets_fail_loudly(key, mutate):
    _bad(key, mutate)


@pytest.mark.parametrize(
    "mode,mutate",
    [
        ("gallery", lambda d: d.update(shapes=[])),
        ("gallery", lambda d: d["shapes"][0].update(type="star")),
        ("gallery", lambda d: d.update(shapes=SHAPES * 5)),
        ("attributes", lambda d: d.update(shapes=[])),
        ("pattern", lambda d: d.update(shapes=SHAPES + [{"type": "circle"}])),  # no blank
        ("pattern", lambda d: d.update(shapes=[{"blank": True}] * 3)),  # nothing shown
        ("pattern", lambda d: d["shapes"][3].update(type="circle")),  # blank with a type
        ("sort", lambda d: d.update(categories=["one"])),
        ("sort", lambda d: d.update(categories=["a", "A"])),
        ("sort", lambda d: d.update(shapes=SHAPES * 6)),  # more than the 10 letters A-J
        ("sort", lambda d: d.pop("categories")),
        ("mirror_match", lambda d: d["shapes"][0].update(options=[{"type": "square"}] * 2)),
        ("mirror_match", lambda d: d["shapes"][0].update(options=[])),
        ("gallery", lambda d: d.update(image_path="x.png")),
    ],
)
def test_shape_id_invalid_variants_fail_loudly(mode, mutate):
    data = {"title": "Shapes", "mode": mode, **copy.deepcopy(SHAPE_CASES[mode])}
    if mode == "pattern":
        data["shapes"] = SHAPES + [{"type": "circle"}, {"blank": True}]
    mutate(data)
    with pytest.raises(ValidationError):
        parse_data("shapeIdWorksheet", data)


def test_shape_id_needs_a_known_mode():
    with pytest.raises(ValidationError):
        parse_data("shapeIdWorksheet", {"title": "S", "shapes": SHAPES})
    with pytest.raises(ValidationError):
        parse_data("shapeIdWorksheet", {"title": "S", "mode": "spin", "shapes": SHAPES})


def test_decimal_scaffold_rules():
    data = {
        "title": "Detective",
        "specimens": [
            {
                "prompt": "0.5 + 0.25 = 0.30",
                "lines": ["0.5 + 0.25 = 0.30"],
                "fix_scaffold": {"addends": ["0.5", "0.25"], "answer": "0.75"},
            }
        ],
    }
    html = render_packet(_week(E, "Detective", data))
    assert "ea-dec-grid" in html
    bad = copy.deepcopy(data)
    bad["specimens"][0]["fix_scaffold"]["answer"] = "x.y"
    with pytest.raises(ValidationError):
        parse_data(E, bad)
    bad = copy.deepcopy(data)
    bad["fix_mode"] = "redraw"
    with pytest.raises(ValidationError):
        parse_data(E, bad)
=======
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
>>>>>>> o/m2-9f
