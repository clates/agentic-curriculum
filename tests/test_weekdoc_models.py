"""WeekDoc v1 envelope (M2.1)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from pydantic import ValidationError

from src.weekdoc import WeekDoc, week_json_schema
from tests.weekdoc_fixtures import minimal_week

SCHEMA_FILE = Path(__file__).resolve().parents[1] / "src" / "weekdoc" / "week.v1.schema.json"


def test_minimal_week_validates_and_roundtrips():
    week = WeekDoc.model_validate(minimal_week())
    assert week.schema_version == 1
    again = WeekDoc.model_validate(json.loads(week.model_dump_json()))
    assert again == week


def test_valid_week_also_passes_the_exported_json_schema():
    schema = json.loads(SCHEMA_FILE.read_text())
    jsonschema.validate(minimal_week(), schema)


def test_exported_schema_file_is_current():
    expected = json.dumps(week_json_schema(), indent=2, sort_keys=True) + "\n"
    assert SCHEMA_FILE.read_text() == expected, "run scripts/export_week_schema.py"


def test_schema_rejects_what_the_models_reject():
    bad = minimal_week()
    bad["days"][0]["worksheets"] = []
    schema = json.loads(SCHEMA_FILE.read_text())
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def _mutated(fn):
    data = minimal_week()
    fn(data)
    return data


@pytest.mark.parametrize(
    "mutate,fragment",
    [
        (lambda d: d["days"][0]["worksheets"][0].update(data={}), "empty data"),
        (lambda d: d["days"][0].update(worksheets=[]), "at least 1"),
        (lambda d: d.update(days=[]), "at least 1"),
        (lambda d: d.update(prep_checks=[]), "at least 1"),
        (lambda d: d["prep_checks"][0].update(pass_criteria=" "), "at least 1"),
        (lambda d: d["prep_checks"][0].update(day="Tuesday"), "not in the week"),
        (lambda d: d["prep_checks"][0].update(standard_id="not an id"), "pattern"),
        (lambda d: d["prep_checks"].append(dict(d["prep_checks"][0])), "unique"),
        (lambda d: d["days"].append(dict(d["days"][0])), "duplicate day"),
        (lambda d: d.update(schema_version=2), "Input should be 1"),
        (lambda d: d.update(surprise=1), "Extra inputs"),
        (lambda d: d.update(packet_title="Hi {{kid}}"), "unknown"),
        (
            lambda d: d["teacher_guide"]["days"][0]["blocks"].append({"style": "answer"}),
            "at least one paragraph",
        ),
        (
            lambda d: d["teacher_guide"]["days"][0]["blocks"].append(
                {"heading": "H", "style": "answer", "paragraphs": ["x"]}
            ),
            "heading block",
        ),
        (lambda d: d["teacher_guide"]["days"][0].update(day="Friday"), "not in the week"),
    ],
)
def test_invalid_weeks_fail_loudly(mutate, fragment):
    with pytest.raises(ValidationError) as exc:
        WeekDoc.model_validate(_mutated(mutate))
    assert fragment in str(exc.value)


def test_student_name_token_and_literal_names_are_both_allowed():
    data = minimal_week()
    data["days"][0]["worksheets"][0]["data"]["text"] = "Hello Zoe and {{ student_name }}"
    WeekDoc.model_validate(data)
