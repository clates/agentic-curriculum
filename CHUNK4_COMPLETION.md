# Chunk 4 Completion Summary

## What was implemented

### 1. agent.py (NEW FILE)
Created a new file with LLM integration for generating lesson plans:

- **`create_lesson_plan_prompt(standard: dict, rules: dict) -> str`**
  - Builds the system prompt for the LLM
  - Extracts `allowed_materials` from rules
  - Extracts `parent_notes` from rules (defaults to "keep procedures under 3 steps")
  - Creates a detailed prompt instructing the LLM to:
    - Act as a K-12 educator
    - Create a lesson_plan with objective, materials_needed, and procedure
    - Only use materials from allowed_materials list
    - Follow parent_notes guidance
    - Make the lesson appropriate for the standard and grade level

- **`generate_weekly_plan(student_id: str, grade_level: int, subject: str) -> dict`**
  - Gets student profile and parses plan_rules_blob
  - Calls `get_filtered_standards()` to get 5 standards
  - For each standard:
    - Creates a prompt using `create_lesson_plan_prompt()`
    - Calls OpenAI API (gpt-3.5-turbo) to generate lesson plan
    - Parses JSON response from LLM
    - Falls back to a basic lesson plan if LLM call fails
  - Returns a complete "Weekly Plan" JSON with:
    - plan_id (format: "plan_{student_id}_{week_of}")
    - student_id
    - week_of (Monday of current week in YYYY-MM-DD format)
    - daily_plan (list of 5 days with lesson_plan and standard for each)

### 2. main.py (UPDATED)
Updated the FastAPI application with:

- **New imports**: Added `BaseModel` from pydantic, `generate_weekly_plan` from agent
- **`PlanRequest` Pydantic model**: Validates request body with student_id, grade_level, and subject
- **POST /generate_weekly_plan endpoint**: 
  - Accepts PlanRequest body
  - Calls `generate_weekly_plan()` function
  - Returns complete weekly plan JSON
  - Handles errors with appropriate HTTP status codes

### 3. validate_chunk4.py (NEW FILE)
Created validation script that:
- Checks if agent.py exists
- Checks if curriculum.db exists
- Checks if OPENAI_API_KEY is set
- Calls the POST /generate_weekly_plan endpoint
- Validates the response structure
- Verifies theme rules are applied (Math subject)
- Verifies materials compliance (only Crayons and Paper)

## How to test

### Prerequisites
1. Ensure curriculum.db exists (run `python3 ingest_standards.py` if needed)
2. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

### Testing steps
1. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

2. In a separate terminal, run the validation script:
   ```bash
   python3 validate_chunk4.py
   ```

### Expected validation output
If everything works correctly, you should see:
```
--- Running Validation for Agent & Endpoint at http://127.0.0.1:8000 ---
PASS: File 'agent
PASS: POST /generate_weekly_plan did not return 200
PASS: Plan JSON is missing 'plan_id'
PASS: Plan JSON 'student_id' is incorrect
PASS: Plan JSON is missing 'daily_plan'
PASS: 'daily_plan' is not a list
PASS: 'daily_plan' does not have 5 items
PASS: First day is not 'Monday'
PASS: Daily plan item is missing 'lesson_plan'
PASS: Daily plan item is missing 'standard'
PASS: Lesson plan is missing 'objective'
PASS: Lesson plan is missing 'materials_needed'
PASS: Lesson plan is missing 'procedure'
PASS: Theme rule failed
PASS: Lesson plan materials are not compliant
---
✅ All validation checks passed. Chunk 4 is complete.
```

### Manual API testing
You can also test the endpoint manually with curl:
```bash
curl -X POST http://127.0.0.1:8000/generate_weekly_plan \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_01",
    "grade_level": 0,
    "subject": "Math"
  }'
```

## Implementation notes

1. **Theme Rules**: The implementation correctly applies theme rules from the student profile. For student_01, the theme_rules force Math subject even if Art is requested.

2. **Materials Compliance**: The LLM is instructed to only use materials from the allowed_materials list (["Crayons", "Paper"] for student_01).

3. **Error Handling**: 
   - Returns 400 error if student not found or API key not set
   - Returns 500 error for other unexpected errors
   - Falls back to basic lesson plan if LLM call fails

4. **Security**: CodeQL scan passed with 0 alerts - no security vulnerabilities detected.

5. **Dependencies**: The following packages are required:
   - fastapi
   - uvicorn
   - openai
   - pydantic (included with fastapi)
   - requests (for validation script)

## Files modified/created
- ✅ agent.py (NEW)
- ✅ main.py (UPDATED)
- ✅ validate_chunk4.py (NEW)
