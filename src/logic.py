"""
logic.py

Rules Engine for selecting educational standards based on student progress and parent-defined rules.
"""

from db_utils import get_student_profile
import os
import sys
import sqlite3
import json
import random

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.environ.get("CURRICULUM_DB_PATH", os.path.join(PROJECT_ROOT, "curriculum.db"))


def _connect_db():
    """
    Private helper function to connect to curriculum.db.

    Returns:
        sqlite3.Connection: A connection object to the database
    """
    return sqlite3.connect(DB_FILE)


def get_filtered_standards(
    student_id: str, grade_level: int, subject: str | None, limit: int = 15
) -> list:
    """
    Get filtered standards for a student based on their progress and rules.

    This function:
    1. Retrieves the student's profile
    2. Parses their progress and rules
    3. Applies theme rules to determine the subject
    4. Filters out mastered standards
    5. Returns standards matching the criteria

    Args:
        student_id: The unique identifier for the student
        grade_level: The grade level to filter by
        subject: The subject to filter by (may be overridden by theme rules)
        limit: Maximum number of standards to return (default: 15)

    Returns:
        A list of dictionaries, where each dictionary represents a standard with keys:
        'standard_id', 'source', 'subject', 'grade_level', 'description', 'json_blob'

    Raises:
        ValueError: If the student is not found
    """
    # Step a: Get student profile
    student_profile = get_student_profile(student_id)

    # Step b: Validate student exists
    if student_profile is None:
        raise ValueError(f"Student with id '{student_id}' not found")

    # Step c: Parse the JSON blobs
    progress_blob = json.loads(student_profile["progress_blob"] or "{}")
    plan_rules_blob = json.loads(student_profile["plan_rules_blob"] or "{}")

    # Step d: Extract mastered standards
    mastered_standards = progress_blob.get("mastered_standards", [])

    # Step e: Extract theme rules
    theme_rules = plan_rules_blob.get("theme_rules", {})

    # Step f: Determine which subject to use
    force_weekly_theme = theme_rules.get("force_weekly_theme", False)
    theme_subjects = theme_rules.get("theme_subjects") or []
    if subject:
        # Caller explicitly requested a subject; honor it.
        selected_subject = subject
    elif force_weekly_theme and theme_subjects:
        # No subject provided, fall back to the scheduled theme rotation.
        selected_subject = theme_subjects[0]
    else:
        selected_subject = theme_subjects[0] if theme_subjects else subject

    if isinstance(selected_subject, str):
        selected_subject = selected_subject.strip()

    if not selected_subject:
        raise ValueError("Subject is required to retrieve standards.")

    normalized_subject = selected_subject.lower()

    # Step g: Build SQL query
    conn = _connect_db()
    cursor = conn.cursor()

    # Base query
    query = "SELECT * FROM standards WHERE grade_level = ? AND LOWER(subject) = ?"
    params = [grade_level, normalized_subject]

    # Add filter for mastered standards if any exist
    if mastered_standards:
        # Create placeholders for the mastered standards
        placeholders = ",".join("?" * len(mastered_standards))
        query += f" AND standard_id NOT IN ({placeholders})"
        params.extend(mastered_standards)

    # NOTE: no SQL LIMIT here on purpose. We fetch all matching rows so the
    # category-aware selection below can distribute picks across categories;
    # a SQL LIMIT would truncate to the first N rows (typically one category).

    # Step h: Execute query and fetch results
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Get column names from cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Convert rows to list of dictionaries
    results = []
    for row in rows:
        row_dict = {}
        for i, column_name in enumerate(column_names):
            row_dict[column_name] = row[i]
        results.append(row_dict)

    conn.close()

    # Step i: Expand and diversify across categories, then apply the limit
    expanded = _expand_standards(results)
    return _diversify_by_category(expanded, limit)


def _expand_standards(rows: list) -> list:
    """
    Expand raw standards rows into individual standards.

    Some sources (e.g. Virginia English SOLs) are ingested as one row per
    grade-level document, with the json_blob containing a list of
    ``categories`` each holding multiple standards. Expand those documents
    into one entry per standard, tagging each with its category title, so
    downstream consumers see individual standards. Rows that already
    represent a single standard are passed through unchanged.
    """
    expanded = []
    for row in rows:
        try:
            blob = json.loads(row.get("json_blob") or "{}")
        except (json.JSONDecodeError, TypeError):
            blob = {}

        categories = blob.get("categories")
        if not isinstance(categories, list):
            expanded.append(row)
            continue

        for category in categories:
            category_title = category.get("title") or category.get("id") or "General"
            for standard in category.get("standards", []) or []:
                description = standard.get("description")
                substandards = standard.get("substandards") or []
                if description is None and substandards:
                    description = " ".join(
                        str(s.get("description", "")).strip() for s in substandards
                    ).strip()
                expanded.append(
                    {
                        "standard_id": standard.get("id"),
                        "source": row.get("source"),
                        "subject": row.get("subject"),
                        "grade_level": row.get("grade_level"),
                        "description": description,
                        "json_blob": json.dumps(
                            {
                                "category": category_title,
                                "parent_id": blob.get("id"),
                                **{
                                    k: v
                                    for k, v in standard.items()
                                    if k not in ("id", "description")
                                },
                            }
                        ),
                    }
                )
    return expanded


def _category_of(row: dict) -> str:
    """Return the category label for a standard row (blank if unknown)."""
    try:
        blob = json.loads(row.get("json_blob") or "{}")
    except (json.JSONDecodeError, TypeError):
        return ""
    for key in ("category", "category_title", "strand", "domain"):
        value = blob.get(key)
        if value:
            return str(value)
    return ""


def _diversify_by_category(rows: list, limit: int) -> list:
    """
    Select up to ``limit`` standards spread across categories.

    Standards are grouped by category, shuffled within each group, then
    interleaved round-robin so consecutive picks come from different
    categories. Without this, the first N standards of a single category
    (e.g. 'Foundations for Reading') dominate every weekly plan.
    """
    if len(rows) <= limit:
        return rows

    groups: dict[str, list] = {}
    for row in rows:
        groups.setdefault(_category_of(row) or "General", []).append(row)

    for group in groups.values():
        random.shuffle(group)

    # Round-robin across categories; keep category order stable modulo the
    # shuffle above so results vary run to run within each category.
    selected = []
    queues = list(groups.values())
    while queues and len(selected) < limit:
        next_queues = []
        for queue in queues:
            if queue and len(selected) < limit:
                selected.append(queue.pop())
            if queue:
                next_queues.append(queue)
        queues = next_queues

    return selected
