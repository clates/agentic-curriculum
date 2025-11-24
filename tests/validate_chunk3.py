# validate_chunk3.py
import sqlite3
import os
import sys
import json
import copy

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the function we want to test
try:
    from logic import get_filtered_standards
except ImportError:
    print("FATAL: Could not import 'get_filtered_standards' from 'logic.py'.")
    print("Please ensure 'logic.py' exists in the src directory.")
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

# --- Test 1: Explicit Subject Overrides Theme ---
print("\nTest 1: Explicit subject overrides theme...")
try:
    # Setup: No mastered standards, Theme is "Math"
    rules = json.loads(original_rules)
    rules["theme_rules"] = {"force_weekly_theme": True, "theme_subjects": ["Math", "Science"]}
    progress = {"mastered_standards": [], "developing_standards": []}
    set_student_data(progress, rules)
    
    standards = get_filtered_standards(student_id, 0, "Science", limit=3)
    
    check(len(standards) == 3, f"Expected 3 standards, got {len(standards)}")
    check(all(s['subject'] == 'Science' for s in standards), "Subject override failed; expected 'Science' standards.")
    check(all(s['grade_level'] == 0 for s in standards), "Did not get Grade 0 standards.")
except Exception as e:
    check(False, f"Test 1 crashed: {e}")

# --- Test 2: Mastered Filtering Still Applies With Subject Override ---
print("\nTest 2: Mastered filtering with explicit subject...")
try:
    # Setup: Mastered "VA.MATH.K.k.1", Theme is "Math"
    rules = json.loads(original_rules)
    rules["theme_rules"] = {"force_weekly_theme": True, "theme_subjects": ["Math", "Science"]}
    progress = {"mastered_standards": ["VA.MATH.K.k.1"], "developing_standards": []}
    set_student_data(progress, rules)

    standards = get_filtered_standards(student_id, 0, "Science", limit=5)
    
    check(len(standards) == 5, f"Expected 5 standards, got {len(standards)}")
    check(all(s['subject'] == 'Science' for s in standards), "Subject override failed; expected 'Science' standards.")
    mastered_found = any(s['standard_id'] == 'VA.MATH.K.k.1' for s in standards)
    check(not mastered_found, "Mastered standard 'VA.MATH.K.k.1' was returned. It should be filtered.")
    
except Exception as e:
    check(False, f"Test 2 crashed: {e}")

# --- Test 3: Theme Fallback When Subject Missing ---
print("\nTest 3: Theme rule used when subject omitted...")
try:
    # Setup: No mastered standards, Theme is "Science" first
    rules = json.loads(original_rules)
    rules["theme_rules"] = {"force_weekly_theme": True, "theme_subjects": ["Science", "Math"]}
    progress = {"mastered_standards": [], "developing_standards": []}
    set_student_data(progress, rules)
    
    standards = get_filtered_standards(student_id, 0, None, limit=3)
    
    check(len(standards) == 3, f"Expected 3 standards, got {len(standards)}")
    check(all(s['subject'] == 'Science' for s in standards), "Theme fallback failed. Did not pick 'Science' from rotation.")
except Exception as e:
    check(False, f"Test 3 crashed: {e}")

# --- Test 4: Theme Disabled Still Uses Provided Subject ---
print("\nTest 4: Theme disabled uses provided subject...")
try:
    # Setup: No mastered standards, Theme rule is OFF
    rules = json.loads(original_rules)
    rules["theme_rules"] = {"force_weekly_theme": False, "theme_subjects": ["Math", "Science"]}
    progress = {"mastered_standards": [], "developing_standards": []}
    set_student_data(progress, rules)
    
    standards = get_filtered_standards(student_id, 0, "Science", limit=3)
    
    check(len(standards) == 3, f"Expected 3 standards, got {len(standards)}")
    check(all(s['subject'] == 'Science' for s in standards), "Theme rule OFF failed. Did not use 'Science' parameter.")
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
