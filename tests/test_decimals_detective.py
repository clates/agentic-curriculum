"""Tests for the Decimals Detective error_audit theme (Priya, grade 5)."""
import pytest

from src.worksheets.base import BaseWorksheet
from src.worksheets.error_audit import (
    ErrorAuditSpecimen,
    generate_error_audit_worksheet,
)
from src.worksheets.factory import WorksheetFactory


def _spec(**over):
    base = {
        "prompt": "Case 1: Maya adds 0.5 + 0.25. Her answer: 0.30.",
        "lines": ["Maya's work: 0.5 + 0.25 = 0.30 (stacked flush right)."],
        "bug_location": "The 5 in 0.5 landed under the hundredths column.",
        "diagnosis": "Line-Up Slip",
        "fix_text": "Line up the decimal points: 0.50 + 0.25 = 0.75.",
    }
    base.update(over)
    return base


DECIMALS_META = {
    "learner": "Priya",
    "grade": 5,
    "subject": "decimals",
    "strategy": "misconception-hunter",
    "source": "bank:priya_decimals_batch/Decimals Detective",
}


def _decimals_payload(**over):
    payload = {
        "title": "Decimals: Find the Bug",
        "theme_label": "Decimals Detective",
        "instructions": "Circle the wrong step, check the suspect, rewrite it.",
        "legend": ["Line-Up Slip", "Trailing-Zero Myth", "Place Swap"],
        "fix_mode": "rewrite",
        "verify": True,
        "metadata": dict(DECIMALS_META),
        "specimens": [
            _spec(),
            {
                "prompt": "Case 2: Dev compares 1.2 and 1.20.",
                "lines": ['Dev\'s claim: "1.20 > 1.2."'],
                "bug_location": "Trailing zero changes nothing.",
                "diagnosis": "Trailing-Zero Myth",
                "fix_text": "1.20 = 1.2; they are equal.",
            },
            {
                "prompt": "Case 3: Sam labels the point at 0.7 as 0.07.",
                "lines": ["Sam's label: seven hundredths, 0.07."],
                "bug_location": "7 tenths written as 7 hundredths.",
                "diagnosis": "Place Swap",
                "fix_text": "The point is at 0.7, seven tenths.",
            },
        ],
    }
    payload.update(over)
    return payload


def test_factory_creates_decimals_detective():
    ws = WorksheetFactory.create("error_audit", _decimals_payload())
    assert isinstance(ws, BaseWorksheet)
    assert ws.theme_label == "Decimals Detective"
    assert ws.fix_mode == "rewrite"
    assert ws.verify is True
    assert len(ws.specimens) == 3
    assert all(isinstance(s, ErrorAuditSpecimen) for s in ws.specimens)


def test_legend_names_suspects():
    ws = WorksheetFactory.create("error_audit", _decimals_payload())
    assert ws.legend == ["Line-Up Slip", "Trailing-Zero Myth", "Place Swap"]
    md = ws.to_markdown()
    for name in ws.legend:
        assert name in md


def test_rewrite_mode_stages_in_markdown():
    ws = WorksheetFactory.create("error_audit", _decimals_payload())
    md = ws.to_markdown()
    assert "Bug circled" in md          # mark stage
    assert "Diagnosis:" in md           # diagnose stage
    assert "Fix:" in md                 # rewrite stage
    assert "Re-checked my fix" in md    # verify stage
    assert "redraw box" not in md       # not redraw mode


def test_show_answers_key_fills_fix_text():
    ws = WorksheetFactory.create(
        "error_audit", _decimals_payload(show_answers=True)
    )
    md = ws.to_markdown()
    assert "0.50 + 0.25 = 0.75" in md       # fix_text filled
    assert "Line-Up Slip" in md            # diagnosis filled
    assert "hundredths column" in md       # bug_location filled
    assert "Bug circled" not in md         # student scaffolding hidden
    assert "Re-checked" not in md


def test_fix_text_hidden_when_not_show_answers():
    ws = WorksheetFactory.create("error_audit", _decimals_payload())
    md = ws.to_markdown()
    assert "0.50 + 0.25 = 0.75" not in md


def test_each_specimen_maps_to_distinct_suspect():
    ws = WorksheetFactory.create("error_audit", _decimals_payload())
    diagnoses = {s.diagnosis for s in ws.specimens}
    assert diagnoses == set(ws.legend)


def test_metadata_round_trip():
    ws = WorksheetFactory.create("error_audit", _decimals_payload())
    assert ws.metadata["learner"] == "Priya"
    assert ws.metadata["grade"] == 5
    assert ws.metadata["subject"] == "decimals"
    assert ws.metadata["strategy"] == "misconception-hunter"
    assert ws.metadata["source"] == "bank:priya_decimals_batch/Decimals Detective"


def test_html_fragment_contains_stages():
    from src.worksheet_html_renderer import render_worksheet_html

    payload = _decimals_payload()
    frag = render_worksheet_html(
        "errorAuditWorksheet",
        {
            "title": payload["title"],
            "theme_label": payload["theme_label"],
            "instructions": payload["instructions"],
            "legend": payload["legend"],
            "fix_mode": payload["fix_mode"],
            "verify": payload["verify"],
            "fix_lines": 2,
            "specimens": payload["specimens"],
        },
        "Thursday",
    )
    assert frag
    assert "Decimals Detective" in frag
    for name in ["Line-Up Slip", "Trailing-Zero Myth", "Place Swap"]:
        assert name in frag          # diagnose stage checkboxes
    assert "Bug circled" in frag     # mark stage
    assert "Fix:" in frag            # rewrite stage
    assert "Re-check" in frag        # verify stage
    assert "0.5 + 0.25" in frag      # specimen text present
    assert "0.50 + 0.25 = 0.75" not in frag  # no answers on student sheet


def test_pil_render_smoke(tmp_path):
    from src.worksheet_renderer import (
        render_error_audit_to_image,
        render_error_audit_to_pdf,
    )

    payload = _decimals_payload()
    ws = WorksheetFactory.create("error_audit", payload)
    img = render_error_audit_to_image(ws, str(tmp_path / "sheet.png"))
    pdf = render_error_audit_to_pdf(ws, str(tmp_path / "sheet.pdf"))
    key = WorksheetFactory.create(
        "error_audit", {**payload, "show_answers": True}
    )
    kimg = render_error_audit_to_image(key, str(tmp_path / "key.png"))
    import os

    for path in (img, pdf, kimg):
        assert os.path.getsize(path) > 5000, path
