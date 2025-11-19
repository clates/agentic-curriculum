"""
db_utils.py

Database utility functions for interacting with curriculum.db
"""

import os
import sqlite3


# Always resolve the DB path relative to the project root so uvicorn reloads
# or different working directories don't create duplicate SQLite files.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.environ.get("CURRICULUM_DB_PATH", os.path.join(PROJECT_ROOT, "curriculum.db"))


def get_student_profile(student_id: str) -> dict:
    """
    Query the student_profiles table for a given student_id.
    
    Args:
        student_id: The unique identifier for the student
        
    Returns:
        A dictionary with student data if found, None otherwise
        Dictionary format: {"student_id": "...", "progress_blob": "...", "plan_rules_blob": "..."}
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT student_id, progress_blob, plan_rules_blob FROM student_profiles WHERE student_id = ?",
            (student_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return {
                "student_id": result[0],
                "progress_blob": result[1],
                "plan_rules_blob": result[2]
            }
        return None
    finally:
        conn.close()
