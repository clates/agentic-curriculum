"""Tests for GET /system/options endpoint."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import app
from worksheets.factory import WorksheetFactory


client = TestClient(app)


def test_system_options_returns_200():
    """Endpoint returns 200 OK status."""
    response = client.get("/system/options")
    assert response.status_code == 200


def test_system_options_contains_required_keys():
    """Response contains subjects, grades, worksheet_types, and statuses."""
    response = client.get("/system/options")
    data = response.json()

    assert "subjects" in data
    assert "grades" in data
    assert "worksheet_types" in data
    assert "statuses" in data


def test_system_options_subjects_are_list():
    """Subjects should be a list of strings."""
    response = client.get("/system/options")
    data = response.json()

    assert isinstance(data["subjects"], list)
    assert len(data["subjects"]) > 0
    assert all(isinstance(s, str) for s in data["subjects"])


def test_system_options_grades_structure():
    """Grades should be a list of objects with value and label."""
    response = client.get("/system/options")
    data = response.json()

    assert isinstance(data["grades"], list)
    assert len(data["grades"]) > 0

    for grade in data["grades"]:
        assert "value" in grade
        assert "label" in grade
        assert isinstance(grade["value"], int)
        assert isinstance(grade["label"], str)


def test_system_options_includes_kindergarten():
    """Grade 0 should be labeled as Kindergarten."""
    response = client.get("/system/options")
    data = response.json()

    kindergarten = next((g for g in data["grades"] if g["value"] == 0), None)
    assert kindergarten is not None
    assert kindergarten["label"] == "Kindergarten"


def test_system_options_worksheet_types_match_factory():
    """Worksheet types should match the WorksheetFactory registry."""
    response = client.get("/system/options")
    data = response.json()

    worksheet_types = data["worksheet_types"]
    expected_types = WorksheetFactory.get_supported_types()

    assert isinstance(worksheet_types, list)
    assert set(worksheet_types) == set(expected_types)


def test_system_options_statuses_contains_expected_values():
    """Statuses should contain MASTERED, DEVELOPING, and BENCHED."""
    response = client.get("/system/options")
    data = response.json()

    statuses = data["statuses"]
    assert isinstance(statuses, list)
    assert "MASTERED" in statuses
    assert "DEVELOPING" in statuses
    assert "BENCHED" in statuses
