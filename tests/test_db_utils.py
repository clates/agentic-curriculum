"""Tests for db_utils functions."""

import importlib
import os
import sqlite3
import sys
from pathlib import Path
from unittest.mock import MagicMock

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
    "ingest_standards",
]


def _clear_modules():
    """Clear cached modules for fresh imports."""
    for name in MODULE_NAMES_TO_CLEAR:
        sys.modules.pop(name, None)


class TestEnsureDatabaseInitialized:
    """Tests for ensure_database_initialized function."""

    def test_initializes_when_no_tables_exist(self, tmp_path):
        """Should call ingest_main when database has no tables."""
        db_path = tmp_path / "empty.db"
        # Create an empty database
        conn = sqlite3.connect(db_path)
        conn.close()

        os.environ["CURRICULUM_DB_PATH"] = str(db_path)
        _clear_modules()

        # Mock the ingest_standards module before importing db_utils
        mock_ingest_module = MagicMock()
        sys.modules["ingest_standards"] = mock_ingest_module

        db_utils = importlib.import_module("src.db_utils")
        db_utils.ensure_database_initialized()

        mock_ingest_module.main.assert_called_once()

    def test_initializes_when_only_student_profiles_exists(self, tmp_path):
        """Should call ingest_main when only student_profiles table exists (partial init)."""
        db_path = tmp_path / "partial.db"
        conn = sqlite3.connect(db_path)
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
        conn.commit()
        conn.close()

        os.environ["CURRICULUM_DB_PATH"] = str(db_path)
        _clear_modules()

        # Mock the ingest_standards module
        mock_ingest_module = MagicMock()
        sys.modules["ingest_standards"] = mock_ingest_module

        db_utils = importlib.import_module("src.db_utils")
        db_utils.ensure_database_initialized()

        mock_ingest_module.main.assert_called_once()

    def test_initializes_when_missing_packet_feedback(self, tmp_path):
        """Should call ingest_main when packet_feedback table is missing."""
        db_path = tmp_path / "partial2.db"
        conn = sqlite3.connect(db_path)
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
        conn.commit()
        conn.close()

        os.environ["CURRICULUM_DB_PATH"] = str(db_path)
        _clear_modules()

        # Mock the ingest_standards module
        mock_ingest_module = MagicMock()
        sys.modules["ingest_standards"] = mock_ingest_module

        db_utils = importlib.import_module("src.db_utils")
        db_utils.ensure_database_initialized()

        mock_ingest_module.main.assert_called_once()

    def test_no_init_when_all_tables_exist(self, tmp_path):
        """Should not call ingest_main when all required tables exist."""
        db_path = tmp_path / "complete.db"
        conn = sqlite3.connect(db_path)
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
            CREATE TABLE packet_feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                packet_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                mastery_feedback_blob TEXT,
                quantity_feedback INTEGER
            )
            """
        )
        conn.commit()
        conn.close()

        os.environ["CURRICULUM_DB_PATH"] = str(db_path)
        _clear_modules()

        # Mock the ingest_standards module
        mock_ingest_module = MagicMock()
        sys.modules["ingest_standards"] = mock_ingest_module

        db_utils = importlib.import_module("src.db_utils")
        db_utils.ensure_database_initialized()

        mock_ingest_module.main.assert_not_called()
