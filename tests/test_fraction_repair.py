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
                "starter_art": {"kind": "partitions", "parts": 3},
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





def _html_frag(**data_over):
    from src.worksheet_html_renderer import render_worksheet_html

    payload = _payload(**data_over)
    data = {
        "title": payload["title"],
        "theme_label": payload["theme_label"],
        "instructions": payload["instructions"],
        "legend": payload["legend"],
        "fix_mode": payload["fix_mode"],
        "verify": payload["verify"],
        "adversarial": False,
        "specimens": payload["specimens"],
    }
    data.update(data_over)
    frag = render_worksheet_html(
        "errorAuditWorksheet",
        data,
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
    # Cut lines: specimen art (2 + 4 + 4) + starters (2 + 3 + 4 —
    # thirds starter shows the correct 3-piece target).
    assert frag.count('stroke-width="2"') == 19


def test_html_redraw_starter_present():
    frag = _html_frag()
    # Each redraw box carries a faint equal-partition starter scaffold.
    assert frag.count('class="ea-starter"') == 3
    assert frag.count("ea-redrawbox") == 3
    # Starter SVGs use the reduced-opacity gray stroke
    # (cut lines + circle outline per starter: 2+1 halves, 3+1 thirds, 4+1
    # fourths — the thirds starter shows the CORRECT 3-piece target).
    assert frag.count('stroke="#8a8a8a"') == 12


def test_starter_art_override_and_validation():
    from src.worksheets.error_audit import ErrorAuditSpecimen

    spec = ErrorAuditSpecimen.from_mapping(
        {
            "prompt": "Zoe thirds",
            "lines": ["x"],
            "art": {"kind": "partitions", "parts": 4},
            "starter_art": {"kind": "partitions", "parts": 3},
        }
    )
    assert spec.starter_art == {"kind": "partitions", "parts": 3}
    with pytest.raises(ValueError):
        WorksheetFactory.create(
            "error_audit",
            {
                "specimens": [
                    {
                        "prompt": "bad",
                        "lines": ["x"],
                        "art": {"kind": "partitions", "parts": 4},
                        "starter_art": {"kind": "partitions", "parts": 13},
                    }
                ]
            },
        )


def test_html_shading_renders_filled_wedges():
    frag = _html_frag()
    # Milo's specimen shades two fourths.
    assert frag.count('<path d="M 80 80') == 2


def test_html_key_mode():
    frag = _html_frag(show_answers=True)
    assert "Bug:" in frag
    assert "Bug circled" not in frag
    assert "ea-starter" not in frag  # key mode has no redraw scaffolds


def _blank_payload(**over):
    payload = _payload()
    for spec in payload["specimens"]:
        spec["blank_fix_circle"] = True
    payload.update(over)
    return payload


def test_columns_validation():
    with pytest.raises(ValueError):
        generate_error_audit_worksheet(
            _blank_payload()["specimens"], columns=3
        )
    ws = generate_error_audit_worksheet(
        _blank_payload()["specimens"], columns=2, fix_mode="redraw"
    )
    assert ws.columns == 2
    assert generate_error_audit_worksheet(
        _blank_payload()["specimens"]).columns == 1


def test_blank_fix_circle_markdown():
    ws = generate_error_audit_worksheet(
        _blank_payload()["specimens"], fix_mode="redraw"
    )
    md = ws.to_markdown()
    assert md.count("blank circle") == 3
    assert "[redraw box]" not in md


def test_html_blank_circle_no_starter():
    frag = _html_frag(
        specimens=_blank_payload()["specimens"],
    )
    # 3 specimen-art SVGs + 3 bare-circle scaffold SVGs; no starters.
    assert frag.count("<svg") == 6
    assert frag.count('r="70" fill="white"') == 3  # one bare circle each
    assert "ea-starter" not in frag
    assert "ea-redrawbox" not in frag
    assert "draw the lines in the circle" in frag


def test_html_key_shows_fixed_shape():
    frag = _html_frag(
        specimens=_blank_payload()["specimens"], show_answers=True
    )
    assert "Fixed shape:" in frag


def test_html_two_up_wraps_cards():
    frag = _html_frag(
        specimens=_blank_payload()["specimens"], columns=2
    )
    assert 'class="ea-cards-2"' in frag
    single = _html_frag(specimens=_blank_payload()["specimens"])
    assert 'class="ea-cards-2"' not in single



