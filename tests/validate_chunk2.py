# validate_chunk2.py
import requests
import os
import json

BASE_URL = "http://127.0.0.1:8000"
print(f"--- Running Validation for FastAPI App at {BASE_URL} ---")

errors = 0


def check(condition, error_message):
    global errors
    if not condition:
        print(f"FAIL: {error_message}")
        errors += 1
    else:
        print(f"PASS: {error_message.split('.')[0]}")


# Test 1: Check required files
check(os.path.exists("main.py"), "File 'main.py' was not created.")
check(os.path.exists("db_utils.py"), "File 'db_utils.py' was not created.")

if not os.path.exists("curriculum.db"):
    print("FATAL: 'curriculum.db' not found. Run Chunk 1 script first.")
    exit(1)

# Test 2: Check root endpoint
try:
    response = requests.get(f"{BASE_URL}/")
    check(response.status_code == 200, "Root GET / endpoint did not return 200.")
    try:
        data = response.json()
        check(
            data == {"message": "Hello World"}, "Root GET / endpoint did not return correct JSON."
        )
    except ValueError:
        check(False, "Root GET / endpoint did not return valid JSON.")
except requests.ConnectionError:
    print("\nFATAL: Could not connect to server.")
    print("Please ensure you are running 'uvicorn main:app --reload' in another terminal.")
    exit(1)
except Exception as e:
    check(False, f"Error testing root endpoint: {e}")


# Test 3: Check for existing student (student_01)
try:
    response = requests.get(f"{BASE_URL}/student/student_01")
    check(response.status_code == 200, "GET /student/student_01 did not return 200.")

    if response.status_code == 200:
        try:
            data = response.json()
            check(
                data["student_id"] == "student_01",
                "Student data does not contain correct 'student_id'.",
            )

            # Check if rules blob is correct
            rules = json.loads(data["plan_rules_blob"])
            check(
                rules["allowed_materials"] == ["Crayons", "Paper"],
                "Student 'plan_rules_blob' content is incorrect.",
            )

        except Exception as e:
            check(False, f"Could not parse JSON or validate data from /student/student_01: {e}")

except Exception as e:
    check(False, f"Error testing /student/student_01 endpoint: {e}")

# Test 4: Check for non-existent student
try:
    response = requests.get(f"{BASE_URL}/student/non_existent_student_id_12345")
    check(response.status_code == 404, "GET /student/non_existent... did not return 404 Not Found.")

    if response.status_code == 404:
        try:
            data = response.json()
            check(
                "detail" in data and "not found" in data["detail"].lower(),
                "404 response JSON missing 'detail' message.",
            )
        except ValueError:
            check(False, "404 response was not valid JSON.")

except Exception as e:
    check(False, f"Error testing non-existent student endpoint: {e}")


# Final Summary
print("---")
if errors == 0:
    print("✅ All validation checks passed. Chunk 2 is complete.")
else:
    print(f"❌ Found {errors} errors. Please review the FAIL messages.")
