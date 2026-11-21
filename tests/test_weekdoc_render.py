"""render_week: packet, teacher guide, prep sheet, name substitution, CLI (M2.4)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.weekdoc import WeekDoc
from src.weekdoc.render import (
    RenderError,
    clean_name,
    render_packet,
    render_prep_sheet,
    render_teacher_guide,
    substitute_name,
)
from tests.weekdoc_fixtures import minimal_week

ROOT = Path(__file__).resolve().parents[1]


def _week(**patch) -> WeekDoc:
    data = minimal_week()
    data.update(patch)
    return WeekDoc.model_validate(data)


def _with_fill_in() -> WeekDoc:
    data = minimal_week()
    data["days"][0]["worksheets"].append(
        {
            "id": "mon-fib",
            "kind": "fillInBlankWorksheet",
            "data": {
                "title": "Fill",
                "segments": [{"text": "The"}, {"gap": 1}, {"text": "and"}, {"gap": 2}],
                "word_bank": ["sun", "rain", "wind", "snow", "hail", "fog"],
            },
        }
    )
    return WeekDoc.model_validate(data)


def test_name_token_is_substituted_everywhere():
    week = _week()
    for fn in (render_packet, render_teacher_guide, render_prep_sheet):
        html = fn(week, "Zoe")
        assert "{{student_name}}" not in html
    assert "Tiny Week for Zoe" in render_packet(week, "Zoe")
    assert "Hello Zoe" in render_packet(week, "Zoe")


def test_missing_name_falls_back_to_generic_phrase():
    assert "Tiny Week for your child" in render_packet(_week(), None)
    assert clean_name("   ") == "your child"


def test_name_is_escaped_not_injected():
    html = render_packet(_week(), "<b>Zoe</b>")
    assert "<b>Zoe</b>" not in html and "&lt;b&gt;Zoe&lt;/b&gt;" in html


def test_name_written_by_the_model_is_escaped_like_any_text():
    data = minimal_week()
    data["days"][0]["worksheets"][0]["data"]["text"] = "<img src=x onerror=alert(1)> Zoe"
    html = render_packet(WeekDoc.model_validate(data), "Zoe")
    assert "<img" not in html and "&lt;img" in html


@pytest.mark.parametrize("bad", ["x" * 41, "Zo\ne"])
def test_invalid_names_are_rejected(bad):
    with pytest.raises(RenderError):
        clean_name(bad)


def test_substitute_name_walks_nested_structures():
    out = substitute_name({"a": ["Hi {{ student_name }}", {"b": "{{student_name}}"}], "n": 3}, "Al")
    assert out == {"a": ["Hi Al", {"b": "Al"}], "n": 3}


def test_render_is_byte_identical_across_runs_even_with_shuffled_word_banks():
    week = _with_fill_in()
    assert render_packet(week, "Zoe") == render_packet(week, "Zoe")


def test_render_does_not_disturb_global_random_state():
    import random

    random.seed(5)
    expected = random.random()
    random.seed(5)
    render_packet(_with_fill_in(), "Zoe")
    assert random.random() == expected


def test_guide_markup_and_entities():
    html = render_teacher_guide(_week(), "Zoe")
    assert "<strong>Q1:</strong> warms it." in html
    data = minimal_week()
    data["teacher_guide"]["arc"] = "Sun &rarr; Rain & <script>"
    html = render_teacher_guide(WeekDoc.model_validate(data), "Zoe")
    assert "Sun &rarr; Rain &amp; &lt;script&gt;" in html


def test_prep_sheet_lists_every_check():
    html = render_prep_sheet(_week(), "Zoe")
    assert "Ask what the sun does." in html and "Says it warms the ground." in html
    assert html.count(chr(34).join(["class=", "pc-card", ""])) == 1


def test_a_week_with_a_kind_the_renderer_cannot_draw_fails_loudly(monkeypatch):
    import src.weekdoc.render as render

    monkeypatch.setattr(render._r, "render_worksheet_html", lambda *a, **k: None)
    with pytest.raises(RenderError, match="rendered nothing"):
        render_packet(_week(), "Zoe")


def test_cli_writes_three_files(tmp_path):
    src = tmp_path / "tiny.json"
    src.write_text(json.dumps(minimal_week()))
    out = tmp_path / "out"
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "render_week.py"),
            str(src),
            "--name",
            "Zoe",
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    assert sorted(p.name for p in out.iterdir()) == [
        "tiny_packet.html",
        "tiny_prep_sheet.html",
        "tiny_teacher_guide.html",
    ]
    assert "Tiny Week for Zoe" in (out / "tiny_packet.html").read_text()
