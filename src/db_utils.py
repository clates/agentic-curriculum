"""
db_utils.py

Database utility functions for interacting with curriculum.db
"""

import json
import os
import sqlite3


# Always resolve the DB path relative to the project root so uvicorn reloads
# or different working directories don't create duplicate SQLite files.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.environ.get("CURRICULUM_DB_PATH", os.path.join(PROJECT_ROOT, "curriculum.db"))

# Cache for column existence check to avoid repeated PRAGMA queries
_metadata_column_cache: dict[str, bool] = {}


def _has_metadata_column(db_file: str) -> bool:
    """Check if metadata_blob column exists in student_profiles table (cached)."""
    if db_file in _metadata_column_cache:
        return _metadata_column_cache[db_file]

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(student_profiles)")
        columns = {row[1] for row in cursor.fetchall()}
        has_metadata = "metadata_blob" in columns
        _metadata_column_cache[db_file] = has_metadata
        return has_metadata
    finally:
        conn.close()


def get_student_profile(student_id: str) -> dict | None:
    """
    Query the student_profiles table for a given student_id.

    Args:
        student_id: The unique identifier for the student

    Returns:
        A dictionary with student data if found, None otherwise
        Dictionary format: {"student_id": "...", "progress_blob": "...", "plan_rules_blob": "...", "metadata_blob": "..."}
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        has_metadata = _has_metadata_column(DB_FILE)

        if has_metadata:
            cursor.execute(
                "SELECT student_id, progress_blob, plan_rules_blob, metadata_blob FROM student_profiles WHERE student_id = ?",
                (student_id,),
            )
        else:
            cursor.execute(
                "SELECT student_id, progress_blob, plan_rules_blob FROM student_profiles WHERE student_id = ?",
                (student_id,),
            )
        result = cursor.fetchone()

        if result:
            profile = {
                "student_id": result[0],
                "progress_blob": result[1],
                "plan_rules_blob": result[2],
            }
            if has_metadata:
                profile["metadata_blob"] = result[3]
            else:
                profile["metadata_blob"] = None
            return profile
        return None
    finally:
        conn.close()


def list_all_students() -> list[dict]:
    """
    Query all student profiles from the database.

    Returns:
        A list of dictionaries with student data
        Each dictionary format: {"student_id": "...", "progress_blob": "...", "plan_rules_blob": "...", "metadata_blob": "..."}
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        has_metadata = _has_metadata_column(DB_FILE)

        if has_metadata:
            cursor.execute(
                "SELECT student_id, progress_blob, plan_rules_blob, metadata_blob FROM student_profiles"
            )
        else:
            cursor.execute(
                "SELECT student_id, progress_blob, plan_rules_blob FROM student_profiles"
            )
        results = cursor.fetchall()

        students = []
        for result in results:
            profile = {
                "student_id": result[0],
                "progress_blob": result[1],
                "plan_rules_blob": result[2],
            }
            if has_metadata:
                profile["metadata_blob"] = result[3]
            else:
                profile["metadata_blob"] = None
            students.append(profile)

        return students
    finally:
        conn.close()


def create_student(student_id: str, metadata: dict, plan_rules: dict) -> dict:
    """
    Create a new student profile in the database.

    Args:
        student_id: The unique identifier for the student
        metadata: Dictionary containing student metadata (name, birthday, etc.)
        plan_rules: Dictionary containing plan rules

    Returns:
        A dictionary with the created student data

    Raises:
        ValueError: If a student with the given ID already exists
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Check if student already exists
        cursor.execute(
            "SELECT student_id FROM student_profiles WHERE student_id = ?",
            (student_id,),
        )
        if cursor.fetchone():
            raise ValueError(f"Student with ID '{student_id}' already exists")

        progress_blob = json.dumps({"mastered_standards": [], "developing_standards": []})
        plan_rules_blob = json.dumps(plan_rules)
        metadata_blob = json.dumps(metadata)

        cursor.execute(
            """
            INSERT INTO student_profiles 
            (student_id, progress_blob, plan_rules_blob, metadata_blob)
            VALUES (?, ?, ?, ?)
            """,
            (student_id, progress_blob, plan_rules_blob, metadata_blob),
        )
        conn.commit()

        return {
            "student_id": student_id,
            "progress_blob": progress_blob,
            "plan_rules_blob": plan_rules_blob,
            "metadata_blob": metadata_blob,
        }
    finally:
        conn.close()


def update_student(
    student_id: str,
    metadata: dict | None = None,
    plan_rules: dict | None = None,
    progress: dict | None = None,
) -> dict | None:
    """
    Update an existing student profile in the database.

    Args:
        student_id: The unique identifier for the student
        metadata: Optional dictionary containing updated metadata (merged with existing)
        plan_rules: Optional dictionary containing updated plan rules

    Returns:
        A dictionary with the updated student data, or None if student not found
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Get existing student
        cursor.execute(
            "SELECT student_id, progress_blob, plan_rules_blob, metadata_blob FROM student_profiles WHERE student_id = ?",
            (student_id,),
        )
        result = cursor.fetchone()

        if not result:
            return None

        current_progress_blob = result[1]
        current_plan_rules_blob = result[2]
        current_metadata_blob = result[3]

        if progress is not None:
            current_progress_blob = json.dumps(progress)

        # Merge metadata if provided
        if metadata is not None:
            existing_metadata = json.loads(current_metadata_blob) if current_metadata_blob else {}
            existing_metadata.update(metadata)
            current_metadata_blob = json.dumps(existing_metadata)

        # Update plan_rules if provided
        if plan_rules is not None:
            current_plan_rules_blob = json.dumps(plan_rules)

        cursor.execute(
            """
            UPDATE student_profiles 
            SET progress_blob = ?, plan_rules_blob = ?, metadata_blob = ?
            WHERE student_id = ?
            """,
            (current_progress_blob, current_plan_rules_blob, current_metadata_blob, student_id),
        )
        conn.commit()

        return {
            "student_id": student_id,
            "progress_blob": current_progress_blob,
            "plan_rules_blob": current_plan_rules_blob,
            "metadata_blob": current_metadata_blob,
        }
    finally:
        conn.close()


def delete_student(student_id: str) -> bool:
    """
    Delete a student profile from the database.

    Args:
        student_id: The unique identifier for the student

    Returns:
        True if the student was deleted, False if not found
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM student_profiles WHERE student_id = ?",
            (student_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def ensure_database_initialized() -> None:
    """
    Check if the database has the required tables, and if not, initialize them.
    This handles cases where the DB file is missing or empty (e.g. volume mount).
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        required_tables = {"student_profiles", "standards", "packet_feedback"}
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('student_profiles', 'standards', 'packet_feedback')"
        )
        existing_tables = {row[0] for row in cursor.fetchall()}
        if not required_tables.issubset(existing_tables):
            print("Database missing required tables. Initializing...")
            # Import here to avoid circular imports if any
            from ingest_standards import main as ingest_main

            # Close our connection before calling ingest which manages its own connections
            conn.close()
            ingest_main()
            return
    finally:
        try:
            conn.close()
        except sqlite3.ProgrammingError:
            pass
