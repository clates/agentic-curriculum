# validate_chunk1.py
import sqlite3
import os
import json

DB_FILE = "curriculum.db"
print(f"--- Running Validation for {DB_FILE} ---")

errors = 0


def check(condition, error_message):
    global errors
    if not condition:
        print(f"FAIL: {error_message}")
        errors += 1
    else:
        print(f"PASS: {error_message.split('.')[0]}")


# Test 1: Database file creation
check(os.path.exists(DB_FILE), "Database file 'curriculum.db' was not created.")
if errors > 0:
    print("Cannot continue tests, database file not found.")
    exit(1)

# Connect to the DB
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
except Exception as e:
    print(f"FATAL: Could not connect to database. {e}")
    exit(1)

# Test 2: Check 'standards' table schema
try:
    cursor.execute("SELECT * FROM standards LIMIT 1")
    cols = [desc[0] for desc in cursor.description]
    expected_cols = ["standard_id", "source", "subject", "grade_level", "description", "json_blob"]
    check(
        cols == expected_cols,
        f"'standards' table columns are incorrect. Expected {expected_cols}, Got {cols}",
    )
except sqlite3.OperationalError:
    check(False, "'standards' table does not exist or failed to query.")

# Test 3: Check 'student_profiles' table schema
try:
    cursor.execute("SELECT * FROM student_profiles LIMIT 1")
    cols = [desc[0] for desc in cursor.description]
    expected_cols = ["student_id", "progress_blob", "plan_rules_blob"]
    check(
        cols == expected_cols,
        f"'student_profiles' table columns are incorrect. Expected {expected_cols}, Got {cols}",
    )
except sqlite3.OperationalError:
    check(False, "'student_profiles' table does not exist or failed to query.")

# Test 4: Check for ingested data in 'standards'
try:
    cursor.execute("SELECT COUNT(*) FROM standards")
    count = cursor.fetchone()[0]
    check(count > 0, "'standards' table is empty. Ingestion script did not add data.")
except Exception as e:
    check(False, f"Failed to count 'standards': {e}")

# Test 5: Check for dummy student in 'student_profiles'
try:
    cursor.execute("SELECT * FROM student_profiles WHERE student_id = 'student_01'")
    student = cursor.fetchone()
    check(student is not None, "Dummy 'student_01' not found in 'student_profiles'.")

    # Test 5b: Validate dummy data content
    if student:
        student_id, progress, rules = student
        try:
            json.loads(progress)
            check(True, "progress_blob is valid JSON.")
        except json.JSONDecodeError:
            check(False, "progress_blob is NOT valid JSON.")

        try:
            rules_json = json.loads(rules)
        except json.JSONDecodeError:
            check(False, "plan_rules_blob is NOT valid JSON or content is wrong.")
        else:
            check(
                rules_json["allowed_materials"] == ["Crayons", "Paper"],
                "plan_rules_blob content is incorrect.",
            )

except Exception as e:
    check(False, f"Failed to query 'student_profiles': {e}")

conn.close()

# Final Summary
print("---")
if errors == 0:
    print("✅ All validation checks passed. Chunk 1 is complete.")
else:
    print(f"❌ Found {errors} errors. Please review the FAIL messages.")
