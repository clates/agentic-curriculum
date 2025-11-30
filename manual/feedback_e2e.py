#!/usr/bin/env python3
"""
Manual end-to-end feedback workflow test.
Requires OPENAI_API_KEY and a running FastAPI server.
"""

import json
import requests
import sqlite3
import sys

BASE_URL = "http://localhost:8000"
DB_PATH = "curriculum.db"


def check_blobs(label: str) -> None:
    """Print current blob state from database for manual inspection."""
    print(f"\n--- {label} ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT progress_blob, plan_rules_blob FROM student_profiles WHERE student_id = 'student_01'"
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        print("❌ Student not found in database")
        return

    progress_blob = json.loads(row[0]) if row[0] else {}
    plan_rules_blob = json.loads(row[1]) if row[1] else {}

    print(f"Progress blob keys: {list(progress_blob.keys())}")
    if "standard_metadata" in progress_blob:
        print(f"  standard_metadata: {progress_blob['standard_metadata']}")

    print(f"Plan rules keys: {list(plan_rules_blob.keys())}")
    if "quantity_preferences" in plan_rules_blob:
        print(f"  quantity_preferences: {plan_rules_blob['quantity_preferences']}")


def main() -> bool:
    print("=== End-to-End Feedback Test ===\n")

    # Check initial state
    check_blobs("BEFORE: Initial State")

    # Step 1: Generate a weekly packet
    print("\n1. Generating weekly packet...")
    response = requests.post(
        f"{BASE_URL}/generate_weekly_plan",
        json={"student_id": "student_01", "grade_level": 0, "subject": "Math"},
    )

    if response.status_code != 200:
        print(f"❌ Failed to generate packet: {response.status_code}")
        print(f"   {response.text}")
        return False

    packet = response.json()
    packet_id = packet["plan_id"]
    print(f"✅ Generated packet: {packet_id}")
    print(f"   Standards used: {[d['standard']['standard_id'] for d in packet['daily_plan'][:2]]}")

    # Step 2: Submit feedback
    print(f"\n2. Submitting feedback for {packet_id}...")
    first_standard = packet["daily_plan"][0]["standard"]["standard_id"]
    second_standard = packet["daily_plan"][1]["standard"]["standard_id"]

    feedback_data = {
        "mastery_feedback": {first_standard: "MASTERED", second_standard: "DEVELOPING"},
        "quantity_feedback": -1,
    }

    response = requests.post(
        f"{BASE_URL}/students/student_01/weekly-packets/{packet_id}/feedback",
        json=feedback_data,
    )

    if response.status_code != 204:
        print(f"❌ Failed to submit feedback: {response.status_code}")
        print(f"   {response.text}")
        return False

    print("✅ Feedback submitted")

    # Check blob updates
    check_blobs("AFTER: Blobs After Feedback")

    # Step 3: Retrieve feedback via GET
    print("\n3. Retrieving feedback via GET...")
    response = requests.get(f"{BASE_URL}/students/student_01/weekly-packets/{packet_id}/feedback")

    if response.status_code != 200:
        print(f"❌ Failed to retrieve feedback: {response.status_code}")
        return False

    feedback = response.json()
    print("✅ Retrieved feedback:")
    print(f"   Mastery: {feedback['mastery_feedback']}")
    print(f"   Quantity: {feedback['quantity_feedback']}")

    # Step 4: Verify packet_feedback table
    print("\n4. Checking packet_feedback table...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT packet_id, mastery_feedback_blob, quantity_feedback FROM packet_feedback WHERE student_id = 'student_01'"
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        print("✅ Feedback stored in database:")
        print(f"   Packet ID: {row[0]}")
        print(f"   Quantity: {row[2]}")
    else:
        print("❌ No feedback found in database")
        return False

    print("\n✅ ALL TESTS PASSED")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as exc:  # pragma: no cover - manual script
        print(f"\n❌ Error: {exc}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
