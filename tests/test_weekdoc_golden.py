"""Weather-week golden: stored structured data renders byte-for-byte like the original script (M2.5).

The fixture holds the week with ``{{student_name}}`` in place of the child's first name. Rendering
it with the name the script hard-codes must reproduce the script's packet and teacher guide
exactly. The original script has no Parent Prep Sheet (it ended with a feedback page), so the prep
sheet is checked structurally.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

from src.weekdoc import HOSTED_KINDS, WeekDoc, load_week
from src.weekdoc.render import render_packet, render_prep_sheet, render_teacher_guide
from tests.test_weekdoc_kinds_blocks import CASES as BLOCKS
from tests.test_weekdoc_kinds_classification import CASES as CLASSIFICATION
from tests.test_weekdoc_kinds_comprehension import CASES as COMPREHENSION
    samples = {}
from tests.test_weekdoc_kinds_math import CASES as MATH
from tests.test_weekdoc_kinds_ordered import CASES as ORDERED

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "weekdoc" / "weather_week.json"
SCHEMA = ROOT / "src" / "weekdoc" / "week.v1.schema.json"
NAME = "Christopher"  # the name the original script hard-codes; the fixture itself has none


@pytest.fixture(scope="module")
def original(tmp_path_factory):
    out = ROOT / "weather_week_series"
    existed = out.exists()
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_weather_week_series.py")],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, r.stderr
    try:
        yield {
            "packet": (out / "weather_week.html").read_text(encoding="utf-8"),
            "guide": (out / "weather_week_teacher_guide.html").read_text(encoding="utf-8"),
        }
    finally:
        if not existed:
            shutil.rmtree(out, ignore_errors=True)


@pytest.fixture(scope="module")
def week() -> WeekDoc:
    return load_week(json.loads(FIXTURE.read_text(encoding="utf-8")))


def test_fixture_is_sanitized_and_valid(week):
    raw = FIXTURE.read_text(encoding="utf-8")
    assert NAME not in raw and "{{student_name}}" in raw
    jsonschema.validate(json.loads(raw), json.loads(SCHEMA.read_text()))
    assert [d.day for d in week.days] == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    assert len(week.prep_checks) >= 10


def test_packet_is_byte_identical_to_the_original_script(week, original):
    assert render_packet(week, NAME) == original["packet"]


def test_teacher_guide_is_byte_identical_to_the_original_script(week, original):
    assert render_teacher_guide(week, NAME) == original["guide"]


def test_prep_sheet_has_every_check_and_is_stable(week):
    html = render_prep_sheet(week, NAME)
    assert html == render_prep_sheet(week, NAME)
    assert html.count('class="pc-card"') == len(week.prep_checks)
    for check in week.prep_checks:
        assert check.pass_criteria.replace("{{student_name}}", NAME).split(".")[0][:20] in html
    assert "{{student_name}}" not in html


def test_without_a_name_nothing_leaks_the_token(week):
    for fn in (render_packet, render_teacher_guide, render_prep_sheet):
        assert "{{" not in fn(week, None)


def test_a_week_using_every_hosted_kind_validates_against_the_schema_and_renders():
    samples = {**COMPREHENSION, **CLASSIFICATION, **ORDERED, **MATH, **BLOCKS, **FRACTIONS, **HANDWRITING, **GRAPHS}
    samples["storyPanel"] = {"who": "Zara", "text": "A beat."}
    assert set(samples) == set(HOSTED_KINDS), set(HOSTED_KINDS) ^ set(samples)
    worksheets = [
        {"id": f"w{i}", "kind": kind, "data": data}
        for i, (kind, data) in enumerate(sorted(samples.items()))
    ]
    doc = {
        "schema_version": 1,
        "title": "All Kinds",
        "packet_title": "All kinds for {{student_name}}",
        "theme": "Kinds",
        "grade_band": "K-2",
        "days": [{"day": "Monday", "title": "Everything", "worksheets": worksheets}],
        "prep_checks": [
            {
                "id": "c1",
                "day": "Monday",
                "standard_id": "VA.MATH.K.k.1",
                "kind": "quiz",
                "prompt": "p",
                "pass_criteria": "c",
            }
        ],
        "teacher_guide": {
            "title": "G",
            "days": [
                {
                    "day": "Monday",
                    "title": "t",
                    "blocks": [{"style": "answer", "paragraphs": ["a"]}],
                }
            ],
        },
    }
    jsonschema.validate(doc, json.loads(SCHEMA.read_text()))
    week = WeekDoc.model_validate(doc)
    html = render_packet(week, "Zoe")
    assert html.count('class="page') == len(samples)
