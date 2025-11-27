import importlib
import json
import os
import sqlite3
import sys
from pathlib import Path


MODULE_NAMES = [
    "logic",
    "db_utils",
    "src.logic",
    "src.db_utils",
]


def _bootstrap_db(db_path: Path) -> None:
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
            plan_rules_blob TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob) VALUES (?, ?, ?)",
        (
            "student_01",
            json.dumps({"mastered_standards": [], "developing_standards": []}),
            json.dumps({"theme_rules": {"force_weekly_theme": False, "theme_subjects": []}}),
        ),
    )
    conn.execute(
        "INSERT INTO standards (standard_id, source, subject, grade_level, description, json_blob) VALUES (?, ?, ?, ?, ?, ?)",
        (
            "VA.HISTORY.2.test",
            "VA",
            "History",
            2,
            "Sample grade 2 history standard",
            json.dumps({}),
        ),
    )
    conn.commit()
    conn.close()


def _reload_logic(db_path: Path):
    os.environ["CURRICULUM_DB_PATH"] = str(db_path)
    for name in MODULE_NAMES:
        sys.modules.pop(name, None)

    db_utils_module = importlib.import_module("src.db_utils")
    sys.modules["db_utils"] = db_utils_module
    logic_module = importlib.import_module("src.logic")
    sys.modules["logic"] = logic_module
    return logic_module


def test_get_filtered_standards_handles_subject_case(tmp_path):
    db_path = tmp_path / "logic.db"
    _bootstrap_db(db_path)
    logic_module = _reload_logic(db_path)

    standards = logic_module.get_filtered_standards(
        "student_01", grade_level=2, subject="history", limit=5
    )

    assert standards, "Expected history standards despite lowercase subject"
    assert all(s["subject"] == "History" for s in standards)
