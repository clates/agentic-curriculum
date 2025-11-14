# validate_chunk3.py
import sqlite3
import os
import json
import copy

# Import the function we want to test
try:
    from logic import get_filtered_standards
except ImportError:
    print("FATAL: Could not import 'get_filtered_standards' from 'logic.py'.")
    print("Please ensure 'logic.py' exists in the same directory.")
    exit(1)

DB_FILE = "curriculum.db"
print(f"--- Running Validation for logic.py ---")

errors = 0
student_id = "student_01"

# Utility to get/set student data for testing
def set_student_data(progress_blob, rules_blob):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE student_profiles SET progress_blob = ?, plan_rules_blob = ? WHERE student_id = ?",
        (json.dumps(progress_blob), json.dumps(rules_blob), student_id)
    )
    conn.commit()
    conn.close()

# Get the original data to restore it later
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("SELECT progress_blob, plan_rules_blob FROM student_profiles WHERE student_id = ?", (student_id,))
original_data = cursor.fetchone()
conn.close()

if not original_data:
    print(f"FATAL: Could not find '{student_id}' in database. Run Chunk 1 script first.")
    exit(1)

original_progress, original_rules = original_data

def check(condition, error_message):
    global errors
    if not condition:
        print(f"FAIL: {error_message}")
        errors += 1
    else:
        print(f"PASS: {error_message.split('.')[0]}")

# --- Test 1: Basic Filtering (No Mastery, Theme Rule) ---
print("\nTest 1: Basic filtering with theme rule...")
try:
    # Setup: No mastered standards, Theme is "Math"
    rules = json.loads(original_rules)
    rules["theme_rules"] = {"force_weekly_theme": True, "theme_subjects": ["Math", "Art"]}
    progress = {"mastered_standards": [], "developing_standards": []}
    set_student_data(progress, rules)
    
    standards = get_filtered_standards(student_id, 0, "Art", limit=3) # "Art" param should be ignored
    
    check(len(standards) == 3, f"Expected 3 standards, got {len(standards)}")
    check(all(s['subject'] == 'Math' for s in standards), "Theme rule failed. Did not get 'Math' standards.")
    check(all(s['grade_level'] == 0 for s in standards), "Did not get Grade 0 standards.")
except Exception as e:
    check(False, f"Test 1 crashed: {e}")

# --- Test 2: Mastered Standard Filtering ---
print("\nTest 2: Filtering mastered standards...")
try:
    # Setup: Mastered "VA.MATH.K.1a", Theme is "Math"
    rules = json.loads(original_rules)
    rules["theme_rules"] = {"force_weekly_theme": True, "theme_subjects": ["Math", "Art"]}
    progress = {"mastered_standards": ["VA.MATH.K.1a"], "developing_standards": []}
    set_student_data(progress, rules)

    standards = get_filtered_standards(student_id, 0, "Art", limit=5) # "Art" param ignored
    
    check(len(standards) == 5, f"Expected 5 standards, got {len(standards)}")
    check(all(s['subject'] == 'Math' for s in standards), "Theme rule failed. Did not get 'Math' standards.")
    mastered_found = any(s['standard_id'] == 'VA.MATH.K.1a' for s in standards)
    check(not mastered_found, "Mastered standard 'VA.MATH.K.1a' was returned. It should be filtered.")
    
except Exception as e:
    check(False, f"Test 2 crashed: {e}")

# --- Test 3: Theme Rotation (Picks first subject) ---
print("\nTest 3: Theme rule uses first subject in list...")
try:
    # Setup: No mastered standards, Theme is "Art" first
    rules = json.loads(original_rules)
    rules["theme_rules"] = {"force_weekly_theme": True, "theme_subjects": ["Art", "Math"]}
    progress = {"mastered_standards": [], "developing_standards": []}
    set_student_data(progress, rules)
    
    standards = get_filtered_standards(student_id, 0, "Math", limit=3) # "Math" param should be ignored
    
    check(len(standards) == 3, f"Expected 3 standards, got {len(standards)}")
    check(all(s['subject'] == 'Art' for s in standards), "Theme rule failed. Did not pick 'Art' from list.")
except Exception as e:
    check(False, f"Test 3 crashed: {e}")

# --- Test 4: No Theme Rule (Uses parameter) ---
print("\nTest 4: No theme rule, uses 'subject' parameter...")
try:
    # Setup: No mastered standards, Theme rule is OFF
    rules = json.loads(original_rules)
    rules["theme_rules"] = {"force_weekly_theme": False, "theme_subjects": ["Math", "Art"]}
    progress = {"mastered_standards": [], "developing_standards": []}
    set_student_data(progress, rules)
    
    standards = get_filtered_standards(student_id, 0, "Art", limit=3) # "Art" param should be USED
    
    check(len(standards) == 3, f"Expected 3 standards, got {len(standards)}")
    check(all(s['subject'] == 'Art' for s in standards), "Theme rule OFF failed. Did not use 'Art' parameter.")
except Exception as e:
    check(False, f"Test 4 crashed: {e}")

# --- Cleanup ---
print("\nRestoring original student data...")
set_student_data(json.loads(original_progress), json.loads(original_rules))

# Final Summary
print("---")
if errors == 0:
    print("✅ All validation checks passed. Chunk 3 is complete.")
else:
    print(f"❌ Found {errors} errors. Please review the FAIL messages.")
