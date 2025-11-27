# validate_chunk4.py
import requests
import os
import json

BASE_URL = "http://127.0.0.1:8000"
print(f"--- Running Validation for Agent & Endpoint at {BASE_URL} ---")

errors = 0


def check(condition, error_message):
    global errors
    if not condition:
        print(f"FAIL: {error_message}")
        errors += 1
    else:
        print(f"PASS: {error_message.split('.')[0]}")


# Test 1: Check required files
check(os.path.exists("agent.py"), "File 'agent.py' was not created.")

if not os.path.exists("curriculum.db"):
    print("FATAL: 'curriculum.db' not found. Run Chunk 1 script first.")
    exit(1)
if "OPENAI_API_KEY" not in os.environ:
    print("FATAL: 'OPENAI_API_KEY' environment variable not set.")
    print('Please set it before running this test: export OPENAI_API_KEY="your_key_here"')
    exit(1)

# Test 2: Call the new POST /generate_weekly_plan endpoint
try:
    payload = {
        "student_id": "student_01",
        "grade_level": 0,
        "subject": "Math",  # This will be overridden by theme rules
    }
    print("\nCalling POST /generate_weekly_plan... (This may take a moment)")
    response = requests.post(f"{BASE_URL}/generate_weekly_plan", json=payload)

    check(
        response.status_code == 200,
        f"POST /generate_weekly_plan did not return 200. Got {response.status_code}.",
    )

    if response.status_code == 200:
        # Test 3: Validate the structure of the returned plan
        try:
            plan = response.json()

            check("plan_id" in plan, "Plan JSON is missing 'plan_id'.")
            check(plan.get("student_id") == "student_01", "Plan JSON 'student_id' is incorrect.")
            check("daily_plan" in plan, "Plan JSON is missing 'daily_plan'.")

            daily_plan = plan.get("daily_plan", [])
            check(isinstance(daily_plan, list), "'daily_plan' is not a list.")
            check(
                len(daily_plan) == 5, f"'daily_plan' does not have 5 items. Got {len(daily_plan)}."
            )

            if len(daily_plan) > 0:
                day_one = daily_plan[0]
                check(day_one.get("day") == "Monday", "First day is not 'Monday'.")
                check("lesson_plan" in day_one, "Daily plan item is missing 'lesson_plan'.")
                check("standard" in day_one, "Daily plan item is missing 'standard'.")

                # Test 4: Validate lesson_plan sub-structure
                lesson_plan = day_one.get("lesson_plan", {})
                check("objective" in lesson_plan, "Lesson plan is missing 'objective'.")
                check(
                    "materials_needed" in lesson_plan, "Lesson plan is missing 'materials_needed'."
                )
                check("procedure" in lesson_plan, "Lesson plan is missing 'procedure'.")

                # Test 5: Validate content adherence (Heuristic)
                standard = day_one.get("standard", {})
                check(
                    standard.get("subject") == "Math",
                    "Theme rule failed. Standard subject is not 'Math'.",
                )

                # Check if materials adhere to rules
                # The rule for student_01 is ["Crayons", "Paper"]
                materials = lesson_plan.get("materials_needed", [])
                is_compliant = all(m in ["Crayons", "Paper"] for m in materials)
                check(is_compliant, f"Lesson plan materials are not compliant. Found: {materials}.")

        except json.JSONDecodeError:
            check(False, "Response from /generate_weekly_plan was not valid JSON.")
        except Exception as e:
            check(False, f"Error validating JSON structure: {e}")

except requests.ConnectionError:
    print("\nFATAL: Could not connect to server.")
    print("Please ensure you are running 'uvicorn main:app --reload' in another terminal.")
    exit(1)
except Exception as e:
    check(False, f"Error testing /generate_weekly_plan endpoint: {e}")

# Final Summary
print("---")
if errors == 0:
    print("✅ All validation checks passed. Chunk 4 is complete.")
else:
    print(f"❌ Found {errors} errors. Please review the FAIL messages.")
