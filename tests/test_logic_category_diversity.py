"""Regression tests for category diversity in get_filtered_standards().

Bug: the function took the first N rows matching grade/subject, which for
grade 3 English meant every weekly plan drew only from the first category
('Foundations for Reading') and ignored Reading Literary Text, Writing,
Research, etc. The fix expands doc-level standards rows and round-robins
across categories.
"""

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

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _bootstrap_db(db_path: Path, english_doc: dict | None = None) -> None:
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
            plan_rules_blob
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
    if english_doc is not None:
        conn.execute(
            "INSERT INTO standards (standard_id, source, subject, grade_level, description, json_blob) VALUES (?, ?, ?, ?, ?, ?)",
            (
                english_doc["id"],
                "VA",
                english_doc["subject"],
                3,
                None,
                json.dumps(english_doc),
            ),
        )
    else:
        # Flat, per-standard rows (no category info) across two "categories"
        # distinguished only by insertion order.
        for i in range(10):
            conn.execute(
                "INSERT INTO standards (standard_id, source, subject, grade_level, description, json_blob) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    f"flat-{i}",
                    "VA",
                    "English",
                    3,
                    f"Flat standard {i}",
                    json.dumps({"id": f"flat-{i}", "category": f"Cat {i % 2}"}),
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


def _grade3_english_doc() -> dict:
    data = json.loads(
        (PROJECT_ROOT / "standards_data" / "english_writing.json").read_text()
    )
    for doc in data:
        if str(doc.get("grade")) == "3":
            return doc
    raise AssertionError("grade 3 English doc not found in standards_data")


def test_grade3_english_standards_span_multiple_categories(tmp_path):
    db_path = tmp_path / "logic.db"
    _bootstrap_db(db_path, english_doc=_grade3_english_doc())
    logic_module = _reload_logic(db_path)

    standards = logic_module.get_filtered_standards(
        "student_01", grade_level=3, subject="English", limit=5
    )

    assert len(standards) == 5, "Expected exactly 5 standards"
    assert all(s.get("standard_id") for s in standards), "Expanded standards need ids"
    assert all(s.get("description") for s in standards), (
        "Expanded standards need descriptions"
    )

    categories = {
        json.loads(s["json_blob"]).get("category", "") for s in standards
    }
    assert len(categories) >= 4, (
        f"Expected standards from multiple categories, got: {sorted(categories)}"
    )
    assert len(categories) > 1
    # The historical failure mode: every pick from 'Foundations for Reading'.
    assert categories != {"Foundations for Reading"}


def test_diversity_round_robins_flat_rows(tmp_path):
    db_path = tmp_path / "logic.db"
    _bootstrap_db(db_path)
    logic_module = _reload_logic(db_path)

    standards = logic_module.get_filtered_standards(
        "student_01", grade_level=3, subject="English", limit=4
    )

    assert len(standards) == 4
    categories = {json.loads(s["json_blob"]).get("category", "") for s in standards}
    assert categories == {"Cat 0", "Cat 1"}, (
        f"Expected picks from both categories, got: {sorted(categories)}"
    )
