"""Tests for the Fraction Repair Shop (error_audit partitions art)."""
import pytest

from src.worksheets.error_audit import (
    ErrorAuditSpecimen,
    generate_error_audit_worksheet,
)
from src.worksheets.factory import WorksheetFactory


def _payload(**over):
    base = {
        "title": "Fractions: Halves, Thirds & Fourths",
        "theme_label": "Fraction Repair Shop",
        "instructions": "Circle the bug, diagnose it, redraw it fixed.",
        "legend": ["Unequal pieces", "Wrong count", "Shading slip"],
        "fix_mode": "redraw",
        "verify": True,
        "metadata": {
            "learner": "Dev",
            "grade": 3,
            "subject": "fractions",
            "strategy": "misconception-hunter",
            "source": "bank:dev_batch/fraction_repair_shop",
        },
        "specimens": [
            {
                "prompt": "Pip says this circle shows halves.",
                "lines": ["Study Pip's circle."],
                "art": {"kind": "partitions", "parts": 2, "broken": 0},
                "bug_location": "The two pieces are unequal.",
                "diagnosis": "Unequal pieces",
            },
            {
                "prompt": "Zoe says this circle shows thirds.",
                "lines": ["Study Zoe's circle."],
                "art": {"kind": "partitions", "parts": 4},
                "bug_location": "Four pieces, not three.",
                "diagnosis": "Wrong count",
            },
            {
                "prompt": "Milo says the shaded part is one fourth.",
                "lines": ["Study Milo's circle."],
                "art": {"kind": "partitions", "parts": 4, "shaded": [0, 1]},
                "bug_location": "Two pieces shaded, so one half.",
                "diagnosis": "Shading slip",
            },
        ],
    }
    base.update(over)
    return base


# ── data layer ──────────────────────────────────────────────────────────────


def test_partitions_art_passthrough():
    art = {"kind": "partitions", "parts": 3, "broken": 1}
    ws = WorksheetFactory.create("error_audit", {"specimens": [
        {"prompt": "p", "lines": ["l"], "art": art}
    ]})
    assert isinstance(ws.specimens[0], ErrorAuditSpecimen)
    assert ws.specimens[0].art == art


def test_partitions_validation_accepts_valid_specs():
    # broken=None, shaded as int or list, parts at both ends of the range.
    for art in (
        {"kind": "partitions", "parts": 2, "broken": 1},
        {"kind": "partitions", "parts": 12, "broken": 11},
        {"kind": "partitions", "parts": 4, "shaded": 2},
        {"kind": "partitions", "parts": 4, "shaded": [0, 3]},
    ):
        WorksheetFactory.create(
            "error_audit", {"specimens": [{"prompt": "p", "lines": [], "art": art}]}
        )


def test_partitions_validation_rejects_bad_parts():
    with pytest.raises(ValueError):
        generate_error_audit_worksheet(
            [{"prompt": "p", "lines": [],
              "art": {"kind": "partitions", "parts": 1, "broken": 0}}]
        )


def test_partitions_validation_rejects_bad_indices():
    with pytest.raises(ValueError):
        generate_error_audit_worksheet(
            [{"prompt": "p", "lines": [],
              "art": {"kind": "partitions", "parts": 3, "broken": 3}}]
        )
    with pytest.raises(ValueError):
        generate_error_audit_worksheet(
            [{"prompt": "p", "lines": [],
              "art": {"kind": "partitions", "parts": 3, "shaded": [0, 5]}}]
        )


def test_fraction_repair_worksheet_fields():
    ws = WorksheetFactory.create("error_audit", _payload())
    assert ws.fix_mode == "redraw"
    assert ws.verify is True
    assert ws.legend == ["Unequal pieces", "Wrong count", "Shading slip"]
    assert len(ws.specimens) == 3
    assert ws.metadata["learner"] == "Dev"
    assert ws.metadata["subject"] == "fractions"


# ── PIL renderer ───────────────────────────────────────────────────────────


def test_pil_renders_fraction_repair_png_pdf_key(tmp_path):
    import os

    from src.worksheet_renderer import (
        render_error_audit_to_image,
        render_error_audit_to_pdf,
        _render_error_audit_image,
    )

    ws = WorksheetFactory.create("error_audit", _payload())
    img = render_error_audit_to_image(ws, str(tmp_path / "sheet.png"))
    pdf = render_error_audit_to_pdf(ws, str(tmp_path / "sheet.pdf"))
    key_ws = WorksheetFactory.create("error_audit", _payload(show_answers=True))
    key = render_error_audit_to_image(key_ws, str(tmp_path / "key.png"))
    assert os.path.getsize(img) > 5000
    assert os.path.getsize(pdf) > 5000
    assert os.path.getsize(key) > 5000
    # Key mode drops the interactive stages, so the sheet is taller.
    assert _render_error_audit_image(ws).height > _render_error_audit_image(key_ws).height


def test_pil_redraw_starter_box_makes_sheet_taller():
    from src.worksheet_renderer import _render_error_audit_image

    ws_redraw = WorksheetFactory.create(
        "error_audit", _payload(fix_mode="redraw", verify=False)
    )
    ws_none = WorksheetFactory.create(
        "error_audit", _payload(fix_mode="none", verify=False)
    )
    taller = (
        _render_error_audit_image(ws_redraw).height
        - _render_error_audit_image(ws_none).height
    )
    # 3 redraw boxes with partition starter scaffolds (~230px each).
    assert taller > 600


# ── HTML renderer ──────────────────────────────────────────────────────────


def _html_frag(**data_over):
    from src.worksheet_html_renderer import render_worksheet_html

    payload = _payload(**data_over)
    frag = render_worksheet_html(
        "errorAuditWorksheet",
        {
            "title": payload["title"],
            "theme_label": payload["theme_label"],
            "instructions": payload["instructions"],
            "legend": payload["legend"],
            "fix_mode": payload["fix_mode"],
            "verify": payload["verify"],
            "adversarial": False,
            "specimens": payload["specimens"],
            **data_over,
        },
        "Thursday",
    )
    assert frag is not None
    return frag


def test_html_renders_partitions_svg():
    frag = _html_frag()
    assert "Fraction Repair Shop" in frag
    assert "<svg" in frag
    # 3 specimen-art SVGs + 3 starter-scaffold SVGs (redraw mode).
    assert frag.count("<svg") == 6
    # Cut lines: specimen art (2 + 4 + 4) + starters (2 + 4 + 4).
    assert frag.count('stroke-width="2"') == 20


def test_html_redraw_starter_present():
    frag = _html_frag()
    # Each redraw box carries a faint equal-partition starter scaffold.
    assert frag.count('class="ea-starter"') == 3
    assert frag.count("ea-redrawbox") == 3
    # Starter SVGs use the reduced-opacity gray stroke
    # (cut lines + circle outline per starter: 2+1, 4+1, 4+1).
    assert frag.count('stroke="#8a8a8a"') == 13


def test_html_shading_renders_filled_wedges():
    frag = _html_frag()
    # Milo's specimen shades two fourths.
    assert frag.count('<path d="M 80 80') == 2


def test_html_key_mode():
    frag = _html_frag(show_answers=True)
    assert "Bug:" in frag
    assert "Bug circled" not in frag
    assert "ea-starter" not in frag  # key mode has no redraw scaffolds
