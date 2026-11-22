#!/usr/bin/env python3
"""
ingest_standards.py

This script initializes a SQLite database (curriculum.db) with two tables:
- standards: for storing educational standards
- student_profiles: for storing student data

It also ingests JSON files from a specified directory into the standards table.
"""

import sqlite3
import json
import os
import glob
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.environ.get("CURRICULUM_DB_PATH", os.path.join(PROJECT_ROOT, "curriculum.db"))
STANDARDS_DIR = os.path.join(PROJECT_ROOT, "standards_data")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from migrations import apply_migrations  # noqa: E402


def create_database():
    """Create the SQLite database and bring its schema up to date via the migration runner."""
    apply_migrations(DB_FILE)
    print(f"Database '{DB_FILE}' created successfully with tables.")


def is_flat_standard(record) -> bool:
    """A real standard: a dict with a string id, subject and description, and an integer grade
    (K is 0). Container documents with nested ``categories`` fail this and are skipped."""
    if not isinstance(record, dict):
        return False
    return (
        all(
            isinstance(record.get(k), str) and record[k].strip()
            for k in ("id", "subject", "description")
        )
        and isinstance(record.get("grade"), int)
        and not isinstance(record.get("grade"), bool)
    )


def ingest_standards_from_json(directory):
    """Read all JSON files from the specified directory and ingest into standards table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Find all JSON files in the directory
    json_files = glob.glob(os.path.join(directory, "*.json"))

    if not json_files:
        print(f"No JSON files found in '{directory}'")
        conn.close()
        return

    # Earlier versions inserted grade-container documents (no description or source) as if they
    # were standards. Purge those leftovers so existing databases heal on re-ingest.
    cursor.execute("DELETE FROM standards WHERE description IS NULL AND source IS NULL")
    purged = cursor.rowcount

    total_inserted = 0
    skipped = 0
    for json_file in json_files:
        print(f"Processing: {json_file}")
        try:
            with open(json_file, "r") as f:
                standards = json.load(f)

            # Ingest each standard from the file
            for standard in standards:
                if not is_flat_standard(standard):
                    skipped += 1  # nested grade-container or malformed record, not a standard
                    continue
                standard_id = standard.get("id")
                source = standard.get("source")
                subject = standard.get("subject")
                grade = standard.get("grade")
                description = standard.get("description")
                json_blob = json.dumps(standard)

                # Insert into database
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO standards 
                    (standard_id, source, subject, grade_level, description, json_blob)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (standard_id, source, subject, grade, description, json_blob),
                )

                total_inserted += 1

        except Exception as e:
            print(f"Error processing {json_file}: {e}")

    conn.commit()
    conn.close()
    print(
        f"Ingested {total_inserted} standards into the database "
        f"({skipped} non-standard records skipped, {purged} stale rows purged)."
    )


def insert_dummy_student():
    """Insert a dummy student profile into the student_profiles table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    student_id = "student_01"
    progress_blob = json.dumps({"mastered_standards": [], "developing_standards": []})
    plan_rules_blob = json.dumps(
        {
            "allowed_materials": ["Crayons", "Paper"],
            "review_rules": {"no_review_mastered_for_weeks": 2},
            "theme_rules": {"force_weekly_theme": True, "theme_subjects": ["Math", "Art"]},
        }
    )
    metadata_blob = json.dumps(
        {
            "name": "Student One",
            "birthday": "2018-01-15",
        }
    )

    # Only insert if student doesn't already exist (avoid overwriting real data)
    cursor.execute("SELECT 1 FROM student_profiles WHERE student_id = ?", (student_id,))
    if cursor.fetchone() is None:
        cursor.execute(
            """
            INSERT OR REPLACE INTO student_profiles 
            (student_id, progress_blob, plan_rules_blob, metadata_blob)
            VALUES (?, ?, ?, ?)
        """,
            (student_id, progress_blob, plan_rules_blob, metadata_blob),
        )

    conn.commit()
    conn.close()
    print(f"Inserted dummy student profile: {student_id}")


def main():
    """Main function to orchestrate database creation and data ingestion."""
    print("Starting database initialization and data ingestion...")

    # Step 1: Create database and tables
    create_database()

    # Step 2: Ingest standards from JSON files
    ingest_standards_from_json(STANDARDS_DIR)

    # Step 3: Insert dummy student data
    insert_dummy_student()

    print("All operations completed successfully!")


if __name__ == "__main__":
    main()
