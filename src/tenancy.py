"""Per-family ownership of students: the check every student-scoped route depends on."""

import base64
import secrets
import sqlite3

from fastapi import Depends, HTTPException

import db_utils
from auth.web import current_family


def student_in_family(conn: sqlite3.Connection, family_id: str, student_id: str) -> bool:
    """True when the family has a profile row, or any packet, for this student."""
    row = conn.execute(
        "SELECT 1 FROM student_profiles WHERE family_id = ? AND student_id = ? "
        "UNION ALL SELECT 1 FROM weekly_packets WHERE family_id = ? AND student_id = ? LIMIT 1",
        (family_id, student_id, family_id, student_id),
    ).fetchone()
    return row is not None


def owned_student_id(student_id: str, family: str = Depends(current_family)) -> str:
    """Path dependency: the student id, or 404 exactly as for a missing student."""
    conn = sqlite3.connect(db_utils.get_db_path())
    try:
        owned = student_in_family(conn, family, student_id)
    finally:
        conn.close()
    if not owned:
        raise HTTPException(status_code=404, detail="Student not found")
    return student_id


def new_student_id() -> str:
    """stu_ plus 10 lowercase base32 characters (50 random bits)."""
    return "stu_" + base64.b32encode(secrets.token_bytes(7)).decode().lower()[:10]
