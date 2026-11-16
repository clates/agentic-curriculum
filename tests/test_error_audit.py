"""Tests for the error_audit ("Bug Hunt") worksheet type."""
import pytest

from src.worksheets.base import BaseWorksheet
from src.worksheets.error_audit import (
    ErrorAuditSpecimen,
    generate_error_audit_worksheet,
)
from src.worksheets.factory import WorksheetFactory


def _spec(**over):
    base = {
        "prompt": "Rory says this clock shows 3:30.",
        "lines": ["Study Rory's clock."],
        "bug_location": "Hour hand on 3; should sit halfway to 4.",
        "diagnosis": "Hour-hand trap",
        "fix_text": "Hour hand halfway between 3 and 4.",
    }
    base.update(over)
    return base


def test_factory_registers_error_audit():
    assert "error_audit" in WorksheetFactory.get_supported_types()


def test_factory_create_minimal():
    ws = WorksheetFactory.create("error_audit", {"specimens": [_spec()]})
    assert isinstance(ws, BaseWorksheet)
    assert ws.title == "Bug Hunt"
    assert ws.fix_mode == "rewrite"
    assert ws.verify is True
    assert len(ws.specimens) == 1
    assert isinstance(ws.specimens[0], ErrorAuditSpecimen)


def test_empty_specimens_rejected():
    with pytest.raises(ValueError):
        generate_error_audit_worksheet([])


def test_bad_fix_mode_rejected():
    with pytest.raises(ValueError):
        WorksheetFactory.create(
            "error_audit", {"specimens": [_spec()], "fix_mode": "teleport"}
        )


def test_bad_fix_lines_rejected():
    with pytest.raises(ValueError):
        generate_error_audit_worksheet([_spec()], fix_lines=0)


def test_fix_none_and_no_verify():
    ws = WorksheetFactory.create(
        "error_audit",
        {
            "specimens": [_spec()],
            "fix_mode": "none",
            "verify": False,
            "legend": ["Hour-hand trap"],
        },
    )
    assert ws.fix_mode == "none"
    assert ws.verify is False
    md = ws.to_markdown()
    assert "Re-checked" not in md


def test_adversarial_and_redraw_modes():
    ws = WorksheetFactory.create(
        "error_audit",
        {
            "specimens": [_spec()],
            "adversarial": True,
            "fix_mode": "redraw",
            "legend": ["Plant a missing hand"],
        },
    )
    assert ws.adversarial is True
    md = ws.to_markdown()
    assert "ASSIGN SUSPECTS:" in md
    assert "Suspects:" not in md.replace("ASSIGN SUSPECTS:", "")


def test_show_answers_renders_key():
    ws = WorksheetFactory.create(
        "error_audit", {"specimens": [_spec()], "show_answers": True}
    )
    md = ws.to_markdown()
    assert "Hour-hand trap" in md
    assert "Bug circled" not in md


def test_specimen_art_passthrough():
    art = {"kind": "clock", "hour": 3.0, "minute": 30}
    ws = WorksheetFactory.create(
        "error_audit", {"specimens": [_spec(art=art)]}
    )
    assert ws.specimens[0].art == art


def test_metadata_round_trips_through_factory():
    ws = WorksheetFactory.create(
        "error_audit",
        {
            "specimens": [_spec()],
            "metadata": {"learner": "Maya", "strategy": "misconception-hunter"},
        },
    )
    assert ws.metadata["learner"] == "Maya"
    assert ws.metadata["strategy"] == "misconception-hunter"



def test_html_render_smoke():
    from src.worksheet_html_renderer import render_worksheet_html

    frag = render_worksheet_html(
        "errorAuditWorksheet",
        {
            "title": "Telling Time: Half Hour",
            "theme_label": "Clock Doctor",
            "instructions": "Circle the bug.",
            "legend": ["Hour-hand trap", "Missing hand"],
            "fix_mode": "redraw",
            "specimens": [
                {
                    "prompt": "Rory says 3:30.",
                    "lines": ["Study the clock."],
                    "art": {"kind": "clock", "hour": 3.0, "minute": 30},
                }
            ],
        },
        "Monday",
    )
    assert frag is not None
    assert "Clock Doctor" in frag
    assert "<svg" in frag
    assert "Hour-hand trap" in frag


def _scaffold_spec(**over):
    base = _spec(
        fix_scaffold={
            "kind": "decimal_stack",
            "addends": ["0.5", "0.25"],
            "answer": "0.75",
        }
    )
    base.update(over)
    return base


def test_fix_scaffold_decimal_stack_rows():
    from src.worksheets.error_audit import decimal_stack_rows

    grid = decimal_stack_rows(
        {"kind": "decimal_stack", "addends": ["0.5", "0.25"], "answer": "0.75"}
    )
    # Columns: 1 int + point + 2 frac = 4 per row; the short term pads.
    assert [c for _, c in grid["terms"][0]].count("pad") == 1
    assert [c for _, c in grid["terms"][1]].count("pad") == 0
    assert grid["has_pads"] is True
    points = [i for i, (_, k) in enumerate(grid["terms"][0]) if k == "point"]
    assert points == [i for i, (_, k) in enumerate(grid["terms"][1]) if k == "point"]
    assert points == [i for i, (_, k) in enumerate(grid["answer"]) if k == "point"]
    key = decimal_stack_rows(
        {"kind": "decimal_stack", "addends": ["0.5", "0.25"], "answer": "0.75"},
        filled=True,
    )
    assert "".join(c for c, k in key["answer"] if k == "given") == "075"


def test_fix_scaffold_validation():
    with pytest.raises(ValueError):
        generate_error_audit_worksheet([_scaffold_spec(
            fix_scaffold={"kind": "mystery_grid"})])
    with pytest.raises(ValueError):
        generate_error_audit_worksheet([_scaffold_spec(
            fix_scaffold={"kind": "decimal_stack", "addends": [], "answer": "0.75"})])
    with pytest.raises(ValueError):
        generate_error_audit_worksheet([_scaffold_spec(
            fix_scaffold={"kind": "decimal_stack",
                          "addends": ["0.5"], "answer": "3/4"})])


