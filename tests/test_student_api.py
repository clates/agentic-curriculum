"""Tests for the Student Management API (CRUD) endpoints."""

import importlib
import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to path for imports (similar to main.py)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = str(PROJECT_ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

MODULE_NAMES_TO_CLEAR = [
    "packet_store",
    "db_utils",
    "agent",
    "src.packet_store",
    "src.db_utils",
    "src.agent",
    "src.main",
    "main",
]


def _bootstrap_db(db_path: Path) -> None:
    """Create a fresh test database with the new schema."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE standards (
            standard_id TEXT PRIMARY KEY,
            source TEXT,
            subject TEXT,
            grade_level INTEGER,
            description TEXT,
            json_blob TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE student_profiles (
            student_id TEXT PRIMARY KEY,
            progress_blob TEXT,
            plan_rules_blob TEXT,
            metadata_blob TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob) VALUES (?, ?, ?, ?)",
        (
            "existing_student",
            json.dumps({"mastered_standards": ["MA.1.1"], "developing_standards": []}),
            json.dumps({"allowed_materials": ["Crayons"]}),
            json.dumps({"name": "Existing Student", "birthday": "2018-05-15"}),
        ),
    )
    conn.commit()
    conn.close()


def _reload_app(db_path: Path):
    """Reload the application modules with a fresh database."""
    os.environ["CURRICULUM_DB_PATH"] = str(db_path)
    for name in MODULE_NAMES_TO_CLEAR:
        sys.modules.pop(name, None)

    db_utils_module = importlib.import_module("src.db_utils")
    sys.modules["db_utils"] = db_utils_module

    packet_store = importlib.import_module("src.packet_store")
    sys.modules["packet_store"] = packet_store

    agent_module = importlib.import_module("src.agent")
    sys.modules["agent"] = agent_module

    main_module = importlib.import_module("src.main")
    importlib.reload(main_module)
    return main_module


@pytest.fixture
def test_client(tmp_path):
    """Create a test client with a fresh database."""
    db_path = tmp_path / "test_students.db"
    _bootstrap_db(db_path)
    main_module = _reload_app(db_path)
    return TestClient(main_module.app)


class TestGetStudentEndpoint:
    """Tests for GET /student/{student_id}."""

    def test_get_student_returns_metadata(self, test_client):
        """GET /student/{id} returns the student's metadata_blob."""
        response = test_client.get("/student/existing_student")
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "existing_student"
        assert data["metadata_blob"] is not None
        metadata = json.loads(data["metadata_blob"])
        assert metadata["name"] == "Existing Student"
        assert metadata["birthday"] == "2018-05-15"

    def test_get_student_not_found(self, test_client):
        """GET /student/{id} returns 404 for non-existent student."""
        response = test_client.get("/student/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Student not found"


class TestCreateStudentEndpoint:
    """Tests for POST /students."""

    def test_create_student_with_metadata(self, test_client):
        """POST /students accepts metadata and persists it."""
        payload = {
            "student_id": "new_student",
            "metadata": {
                "name": "Alice",
                "birthday": "2019-05-01",
            },
            "plan_rules": {"allowed_materials": ["Paper"]},
        }
        response = test_client.post("/students", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["student_id"] == "new_student"
        metadata = json.loads(data["metadata_blob"])
        assert metadata["name"] == "Alice"
        assert metadata["birthday"] == "2019-05-01"

    def test_create_student_with_optional_metadata_fields(self, test_client):
        """POST /students accepts optional metadata fields."""
        payload = {
            "student_id": "student_with_avatar",
            "metadata": {
                "name": "Bob",
                "birthday": "2020-03-15",
                "avatar_url": "https://example.com/avatar.png",
                "notes": "Some notes about the student",
            },
            "plan_rules": {},
        }
        response = test_client.post("/students", json=payload)
        assert response.status_code == 201
        data = response.json()
        metadata = json.loads(data["metadata_blob"])
        assert metadata["name"] == "Bob"
        assert metadata["avatar_url"] == "https://example.com/avatar.png"
        assert metadata["notes"] == "Some notes about the student"

    def test_create_student_duplicate_fails(self, test_client):
        """POST /students returns 400 for duplicate student_id."""
        payload = {
            "student_id": "existing_student",
            "metadata": {"name": "Duplicate", "birthday": "2020-01-01"},
            "plan_rules": {},
        }
        response = test_client.post("/students", json=payload)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_student_initializes_progress(self, test_client):
        """POST /students initializes progress_blob with empty standards."""
        payload = {
            "student_id": "new_student_progress",
            "metadata": {"name": "Charlie", "birthday": "2019-01-01"},
            "plan_rules": {},
        }
        response = test_client.post("/students", json=payload)
        assert response.status_code == 201
        data = response.json()
        progress = json.loads(data["progress_blob"])
        assert progress["mastered_standards"] == []
        assert progress["developing_standards"] == []


class TestUpdateStudentEndpoint:
    """Tests for PUT /student/{student_id}."""

    def test_update_student_metadata_preserves_progress(self, test_client):
        """PUT /student/{id} updates metadata without affecting progress."""
        # First, verify existing data
        get_response = test_client.get("/student/existing_student")
        original_data = get_response.json()
        original_progress = json.loads(original_data["progress_blob"])
        assert original_progress["mastered_standards"] == ["MA.1.1"]

        # Update the name
        update_payload = {
            "metadata": {
                "name": "Updated Name",
                "birthday": "2018-05-15",
            }
        }
        response = test_client.put("/student/existing_student", json=update_payload)
        assert response.status_code == 200

        # Verify name is updated but progress is preserved
        data = response.json()
        metadata = json.loads(data["metadata_blob"])
        assert metadata["name"] == "Updated Name"

        progress = json.loads(data["progress_blob"])
        assert progress["mastered_standards"] == ["MA.1.1"]

    def test_update_student_merges_metadata(self, test_client):
        """PUT /student/{id} merges new metadata into existing blob."""
        # Update with partial metadata
        update_payload = {
            "metadata": {
                "name": "Existing Student",
                "birthday": "2018-05-15",
                "notes": "Added notes",
            }
        }
        response = test_client.put("/student/existing_student", json=update_payload)
        assert response.status_code == 200

        data = response.json()
        metadata = json.loads(data["metadata_blob"])
        assert metadata["name"] == "Existing Student"
        assert metadata["birthday"] == "2018-05-15"
        assert metadata["notes"] == "Added notes"

    def test_update_student_plan_rules(self, test_client):
        """PUT /student/{id} can update plan_rules_blob."""
        update_payload = {
            "plan_rules": {"allowed_materials": ["Markers", "Colored Pencils"]},
        }
        response = test_client.put("/student/existing_student", json=update_payload)
        assert response.status_code == 200

        data = response.json()
        plan_rules = json.loads(data["plan_rules_blob"])
        assert plan_rules["allowed_materials"] == ["Markers", "Colored Pencils"]

    def test_update_student_not_found(self, test_client):
        """PUT /student/{id} returns 404 for non-existent student."""
        update_payload = {
            "metadata": {"name": "Ghost", "birthday": "2020-01-01"},
        }
        response = test_client.put("/student/nonexistent", json=update_payload)
        assert response.status_code == 404


class TestDeleteStudentEndpoint:
    """Tests for DELETE /student/{student_id}."""

    def test_delete_student_removes_record(self, test_client):
        """DELETE /student/{id} removes the student record entirely."""
        # Verify student exists first
        get_response = test_client.get("/student/existing_student")
        assert get_response.status_code == 200

        # Delete the student
        delete_response = test_client.delete("/student/existing_student")
        assert delete_response.status_code == 204

        # Verify student is gone
        get_response = test_client.get("/student/existing_student")
        assert get_response.status_code == 404

    def test_delete_student_not_found(self, test_client):
        """DELETE /student/{id} returns 404 for non-existent student."""
        response = test_client.delete("/student/nonexistent")
        assert response.status_code == 404
