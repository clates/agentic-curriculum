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


def get_db_path() -> str:
    """Single source of truth for the SQLite DB location.

    Reads CURRICULUM_DB_PATH at call time (the container sets it to a volume path),
    defaulting to <project root>/curriculum.db.
    """
    return os.environ.get("CURRICULUM_DB_PATH") or os.path.join(PROJECT_ROOT, "curriculum.db")


# Import-time snapshot kept for modules/tests that import DB_FILE directly.
DB_FILE = get_db_path()

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


def _query_profiles(where: str = "", params: tuple = ()) -> list[dict]:
    """Profile rows as dicts; ``metadata_blob`` is None on old DBs that lack the column."""
    has_metadata = _has_metadata_column(DB_FILE)
    columns = "student_id, progress_blob, plan_rules_blob" + (
        ", metadata_blob" if has_metadata else ""
    )
    conn = sqlite3.connect(DB_FILE)
    try:
        rows = conn.execute(f"SELECT {columns} FROM student_profiles{where}", params).fetchall()
    finally:
        conn.close()
    return [
        {
            "student_id": row[0],
            "progress_blob": row[1],
            "plan_rules_blob": row[2],
            "metadata_blob": row[3] if has_metadata else None,
        }
        for row in rows
    ]


def get_student_profile(student_id: str) -> dict | None:
    """The student's profile row as a dict, or None if there is no such student."""
    rows = _query_profiles(" WHERE student_id = ?", (student_id,))
    return rows[0] if rows else None


def list_students() -> list[dict]:
    """Every student profile, as dicts shaped like get_student_profile's."""
    return _query_profiles()


def create_student(student_id: str, metadata: dict, plan_rules: dict) -> dict:
    """Create a student profile with empty progress; ValueError if the id is taken."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
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
    """Update a profile (metadata is merged into the existing metadata; progress and plan_rules
    replace theirs). Returns the updated row, or None if the student does not exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT student_id, progress_blob, plan_rules_blob, metadata_blob FROM student_profiles WHERE student_id = ?",
            (student_id,),
        )
        result = cursor.fetchone()

        if not result:
            return None

        _, current_progress_blob, current_plan_rules_blob, current_metadata_blob = result

        if progress is not None:
            current_progress_blob = json.dumps(progress)

        if metadata is not None:
            existing_metadata = json.loads(current_metadata_blob) if current_metadata_blob else {}
            existing_metadata.update(metadata)
            current_metadata_blob = json.dumps(existing_metadata)

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


def ensure_student(family_id: str, student_id: str, conn: sqlite3.Connection | None = None) -> bool:
    """Make sure a (family_id, student_id) profile row exists; return True if it was created.

    Packets, feedback and plans carry a composite foreign key to student_profiles (migration
    0008, decision D2), so a packet can only be saved for a student that has a profile. The real
    save paths (packet_store.save_weekly_packet, week_store.save_week) call this first: when a
    packet is saved for a student the app has not seen, a minimal profile row (empty progress,
    empty plan rules and metadata) is created so the save succeeds, and the profile can be
    filled in later. An existing row is never modified.

    Pass ``conn`` to join the caller's transaction (the caller commits); without it a short
    transaction of its own is used. The family must already exist (foreign key); a student id
    that belongs to a different family is not stolen: student_id is the profile primary key, so
    the insert fails with sqlite3.IntegrityError.
    """
    own = conn is None
    if own:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA busy_timeout = 5000")
        conn.execute("PRAGMA foreign_keys = ON")
    try:
        cur = conn.execute(
            "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob,"
            " metadata_blob, family_id) SELECT ?, ?, '{}', '{}', ? WHERE NOT EXISTS ("
            "SELECT 1 FROM student_profiles WHERE family_id = ? AND student_id = ?)",
            (
                student_id,
                json.dumps({"mastered_standards": [], "developing_standards": []}),
                family_id,
                family_id,
                student_id,
            ),
        )
        if own:
            conn.commit()
        return cur.rowcount > 0
    finally:
        if own:
            conn.close()


def delete_student(student_id: str) -> bool:
    """Delete a student and their packets; False if not found. A locked DB raises
    sqlite3.OperationalError after the busy timeout."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA busy_timeout = 5000")  # 5s timeout instead of hanging forever
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        # Delete packets first — their FK cascade removes daily_lessons,
        # worksheet_artifacts, and packet_feedback automatically.
        # weekly_packets may not exist in minimal test DBs, so ignore if absent.
        try:
            cursor.execute(
                "DELETE FROM weekly_packets WHERE student_id = ?",
                (student_id,),
            )
        except sqlite3.OperationalError as e:
            if "no such table" not in str(e):
                raise
        cursor.execute(
            "DELETE FROM student_profiles WHERE student_id = ?",
            (student_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.OperationalError:
        conn.rollback()
        raise
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
        placeholders = ", ".join("?" * len(required_tables))
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name IN ({placeholders})",
            tuple(required_tables),
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
