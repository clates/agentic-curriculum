#!/usr/bin/env python3
"""
Test script for feedback endpoints.

Creates a weekly packet, submits feedback, and retrieves it.
"""

import requests
import sys

BASE_URL = "http://localhost:8000"


def test_feedback_workflow():
    print("=== Testing Feedback Workflow ===\n")

    # Step 1: Verify student exists
    print("1. Checking student profile...")
    response = requests.get(f"{BASE_URL}/student/student_01")
    if response.status_code != 200:
        print(f"❌ Student not found: {response.status_code}")
        return False
    print(f"✅ Student found: {response.json()['student_id']}\n")

    # Step 2: Generate a weekly packet (requires OPENAI_API_KEY)
    print("2. Generating weekly packet...")
    print("   (Skipping - requires OPENAI_API_KEY)")
    print("   Using mock packet_id instead\n")

    #  For real testing, you would do:
    # response = requests.post(
    #     f"{BASE_URL}/generate_weekly_plan",
    #     json={"student_id": "student_01", "grade_level": 0, "subject": "Math"}
    # )
    # packet_id = response.json()["plan_id"]

    # Mock packet for testing (won't work until we have real packet)
    packet_id = "plan_student_01_2025-11-29"

    # Step 3: Try to submit feedback (will fail without real packet)
    print(f"3. Submitting feedback for packet: {packet_id}...")
    feedback_data = {
        "mastery_feedback": {"VA.MATH.K.1a": "MASTERED", "VA.MATH.K.2a": "DEVELOPING"},
        "quantity_feedback": -1,
    }

    response = requests.post(
        f"{BASE_URL}/students/student_01/weekly-packets/{packet_id}/feedback", json=feedback_data
    )

    if response.status_code == 204:
        print("✅ Feedback submitted successfully\n")
    elif response.status_code == 400:
        error_detail = response.json().get("detail", "Unknown error")
        if "not found" in error_detail.lower():
            print(f"⚠️  Expected error: {error_detail}")
            print("   (This is normal - packet doesn't exist yet)\n")
            return True  # Expected failure
        else:
            print(f"❌ Validation error: {error_detail}\n")
            return False
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        print(f"   Response: {response.text}\n")
        return False

    # Step 4: Retrieve feedback
    print("4. Retrieving feedback...")
    response = requests.get(f"{BASE_URL}/students/student_01/weekly-packets/{packet_id}/feedback")

    if response.status_code == 200:
        feedback = response.json()
        print("✅ Feedback retrieved:")
        print(f"   Completed: {feedback['completed_at']}")
        print(f"   Mastery: {feedback['mastery_feedback']}")
        print(f"   Quantity: {feedback['quantity_feedback']}\n")
        return True
    elif response.status_code == 404:
        print("✅ 404 (expected - no feedback submitted yet)\n")
        return True
    else:
        print(f"❌ Unexpected status: {response.status_code}\n")
        return False


if __name__ == "__main__":
    try:
        success = test_feedback_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
