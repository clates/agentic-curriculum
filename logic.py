"""
logic.py

Rules Engine for selecting educational standards based on student progress and parent-defined rules.
"""

import sqlite3
import json
from db_utils import get_student_profile


DB_FILE = "curriculum.db"


def _connect_db():
    """
    Private helper function to connect to curriculum.db.
    
    Returns:
        sqlite3.Connection: A connection object to the database
    """
    return sqlite3.connect(DB_FILE)


def get_filtered_standards(student_id: str, grade_level: int, subject: str, limit: int = 15) -> list:
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
    progress_blob = json.loads(student_profile['progress_blob'])
    plan_rules_blob = json.loads(student_profile['plan_rules_blob'])
    
    # Step d: Extract mastered standards
    mastered_standards = progress_blob.get('mastered_standards', [])
    
    # Step e: Extract theme rules
    theme_rules = plan_rules_blob.get('theme_rules', {})
    
    # Step f: Determine which subject to use
    force_weekly_theme = theme_rules.get('force_weekly_theme', False)
    if force_weekly_theme and 'theme_subjects' in theme_rules and theme_rules['theme_subjects']:
        # Use the first subject from theme_subjects list
        selected_subject = theme_rules['theme_subjects'][0]
    else:
        # Use the provided subject parameter
        selected_subject = subject
    
    # Step g: Build SQL query
    conn = _connect_db()
    cursor = conn.cursor()
    
    # Base query
    query = "SELECT * FROM standards WHERE grade_level = ? AND subject = ?"
    params = [grade_level, selected_subject]
    
    # Add filter for mastered standards if any exist
    if mastered_standards:
        # Create placeholders for the mastered standards
        placeholders = ','.join('?' * len(mastered_standards))
        query += f" AND standard_id NOT IN ({placeholders})"
        params.extend(mastered_standards)
    
    # Add limit
    query += " LIMIT ?"
    params.append(limit)
    
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
    
    # Step i: Return the list of standard dictionaries
    return results
