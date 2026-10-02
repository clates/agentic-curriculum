"""Tests for the ten_frame ("Make Ten") worksheet type."""
import pytest

from src.worksheets.base import BaseWorksheet
from src.worksheets.ten_frame import (
    TenFrameProblem,
    generate_ten_frame_worksheet,
)
from src.worksheets.factory import WorksheetFactory


def _prob(**over):
    base = {"addend_a": 8, "addend_b": 5, "label": "Sam has 8 blocks and 5 more."}
    base.update(over)
    return base


def test_factory_registers_ten_frame():
    assert "ten_frame" in WorksheetFactory.get_supported_types()


def test_factory_create_minimal():
    ws = WorksheetFactory.create("ten_frame", {"problems": [_prob()]})
    assert isinstance(ws, BaseWorksheet)
    assert ws.title == "Make Ten!"
    assert ws.equation_lines == 2
    assert len(ws.problems) == 1
    assert isinstance(ws.problems[0], TenFrameProblem)


def test_empty_problems_rejected():
    with pytest.raises(ValueError):
        generate_ten_frame_worksheet([])


def test_addend_bounds_enforced():
    with pytest.raises(ValueError):
        generate_ten_frame_worksheet([_prob(addend_a=11)])
    with pytest.raises(ValueError):
        WorksheetFactory.create("ten_frame", {"problems": [_prob(addend_b=-1)]})


def test_sum_over_20_rejected():
    with pytest.raises(ValueError):
        generate_ten_frame_worksheet([_prob(addend_a=10, addend_b=11)])


def test_bad_equation_lines_rejected():
    with pytest.raises(ValueError):
        generate_ten_frame_worksheet([_prob()], equation_lines=0)


def test_problem_derived_values():
    p = TenFrameProblem(addend_a=8, addend_b=5)
    assert p.total == 13
    assert p.carries is True
    assert p.make_ten_split == 2
    assert p.remainder == 3
    assert p.proof_equations() == ["8 + 2 = 10", "10 + 3 = 13"]
    nc = TenFrameProblem(addend_a=6, addend_b=3)
    assert nc.carries is False
    assert nc.proof_equations() == ["6 + 3 = 9"]
    exact = TenFrameProblem(addend_a=8, addend_b=2)
    assert exact.proof_equations() == ["8 + 2 = 10"]


def test_show_answers_renders_key():
    ws = WorksheetFactory.create(
        "ten_frame", {"problems": [_prob()], "show_answers": True}
    )
    md = ws.to_markdown()
    assert "8 + 2 = 10" in md
    assert "10 + 3 = 13" in md
    assert "Proof: _" not in md


def test_markdown_student_mode_blanks():
    ws = WorksheetFactory.create("ten_frame", {"problems": [_prob()]})
    md = ws.to_markdown()
    assert "## Problem 1: 8 + 5" in md
    assert "Proof:" in md
    assert "= 10" not in md


def test_metadata_round_trips_through_factory():
    ws = WorksheetFactory.create(
        "ten_frame",
        {
            "problems": [_prob()],
            "metadata": {
                "learner": "Sam",
                "grade": 1,
                "subject": "addition_make_ten",
                "strategy": "make-ten-bridge",
                "source": "bank:priya_sam_batch/ten_frame_make_ten",
            },
        },
    )
    assert ws.metadata["learner"] == "Sam"
    assert ws.metadata["grade"] == 1
    assert ws.metadata["subject"] == "addition_make_ten"
    assert ws.metadata["strategy"] == "make-ten-bridge"
    assert ws.metadata["source"].startswith("bank:")


def test_pil_render_smoke(tmp_path):
    from src.worksheet_renderer import (
        render_ten_frame_to_image,
        render_ten_frame_to_pdf,
    )

    ws = WorksheetFactory.create(
        "ten_frame",
        {
            "title": "Make Ten: Addition Within 20",
            "instructions": "Move counters to fill the first ten-frame to ten.",
            "problems": [_prob(), _prob(addend_a=6, addend_b=3)],
        },
    )
    img = render_ten_frame_to_image(ws, str(tmp_path / "smoke.png"))
    pdf = render_ten_frame_to_pdf(ws, str(tmp_path / "smoke.pdf"))
    import os

    assert os.path.getsize(img) > 5000
    assert os.path.getsize(pdf) > 5000


def test_html_render_smoke():
    from src.worksheet_html_renderer import render_worksheet_html

    frag = render_worksheet_html(
        "tenFrameWorksheet",
        {
            "title": "Make Ten: Addition Within 20",
            "instructions": "Move counters to fill the first ten-frame to ten.",
            "problems": [_prob()],
        },
        "Thursday",
    )
    assert frag is not None
    assert "Make Ten" in frag
    assert "<svg" in frag
    assert "Make ten:" in frag
    assert "tf-card" in frag


def test_html_render_answer_key():
    from src.worksheet_html_renderer import render_worksheet_html

    frag = render_worksheet_html(
        "tenFrameWorksheet",
        {
            "title": "Make Ten",
            "problems": [_prob()],
            "show_answers": True,
        },
        "",
    )
    assert frag is not None
    assert "8 + 2 = 10" in frag
    assert "10 + 3 = 13" in frag
    assert "answer-lines" not in frag


def test_fill_defaults_to_black():
    ws = generate_ten_frame_worksheet([_prob()])
    prob = ws.problems[0]
    assert prob.fill_a == "black"
    assert prob.fill_b == "black"


def test_fill_passthrough_and_validation():
    ws = generate_ten_frame_worksheet([_prob(fill_a="blue", fill_b="🦆")])
    prob = ws.problems[0]
    assert prob.fill_a == "blue"
    assert prob.fill_b == "🦆"
    md = ws.to_markdown()
    assert "(blue)" in md and "(🦆)" in md
    with pytest.raises(ValueError):
        generate_ten_frame_worksheet([_prob(fill_a=123)])  # type: ignore[dict-item]
    with pytest.raises(ValueError):
        generate_ten_frame_worksheet([_prob(fill_b="x" * 25)])


def test_html_renders_color_and_emoji_fills():
    from src.worksheet_html_renderer import render_worksheet_html

    frag = render_worksheet_html(
        "tenFrameWorksheet",
        {
            "title": "Make Ten",
            "problems": [
                _prob(fill_a="blue", fill_b="red"),
                _prob(fill_a="🦆", fill_b="🦆"),
            ],
        },
        "Thursday",
    )
    assert frag is not None
    assert 'fill="blue"' in frag
    assert 'fill="red"' in frag
    assert "🦆" in frag


def test_pil_render_with_fills_smoke(tmp_path):
    from src.worksheet_renderer import render_ten_frame_to_image

    ws = generate_ten_frame_worksheet([_prob(fill_a="blue", fill_b="🦆")])
    img = render_ten_frame_to_image(ws, str(tmp_path / "fills.png"))
    import os

    assert os.path.getsize(img) > 5000
