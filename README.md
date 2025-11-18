# agentic-curriculum

A Python-based system for managing educational curriculum standards and student profiles using SQLite. The system generates personalized weekly lesson plans using AI, tailored to each student's progress and learning preferences.

## 🚀 Quick Start (First Time Setup)

Get from clone to generating lessons in under 5 minutes!

### 1. Clone the Repository

```bash
git clone https://github.com/clates/agentic-curriculum.git
cd agentic-curriculum
```

### 2. Install Dependencies

```bash
# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Set Your OpenAI API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Required:** You must have a valid OpenAI API key to generate lesson plans.

### 4. Initialize the Database

```bash
python3 src/ingest_standards.py
```

This creates `curriculum.db` with educational standards and a sample student profile.

### 5. Start the API Server

```bash
cd src
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`

### 6. Generate Your First Weekly Lesson Plan!

In a new terminal:

```bash
curl -X POST "http://127.0.0.1:8000/generate_weekly_plan" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_01",
    "grade_level": 0,
    "subject": "Math"
  }'
```

You'll receive a complete 5-day lesson plan with objectives, materials, and procedures!

---

## Configuration

### Environment Variables

The system uses environment variables for configuration:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | **Yes** | None | Your OpenAI API key for generating lesson plans |
| `OPENAI_BASE_URL` | No | None | Custom API base URL (e.g., for Azure OpenAI or local models) |
| `OPENAI_MODEL` | No | `gpt-3.5-turbo` | The OpenAI model to use for generation |

**Setting environment variables:**

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-your-key-here"
export OPENAI_BASE_URL="https://custom.api.endpoint"  # Optional
export OPENAI_MODEL="gpt-4"  # Optional

# Windows (Command Prompt)
set OPENAI_API_KEY=sk-your-key-here
set OPENAI_BASE_URL=https://custom.api.endpoint
set OPENAI_MODEL=gpt-4

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-key-here"
$env:OPENAI_BASE_URL="https://custom.api.endpoint"
$env:OPENAI_MODEL="gpt-4"
```

**Using Azure OpenAI:**

```bash
export OPENAI_API_KEY="your-azure-api-key"
export OPENAI_BASE_URL="https://your-resource.openai.azure.com"
export OPENAI_MODEL="gpt-4"  # or your deployment name
```

---

## API Endpoints

The FastAPI server exposes the following endpoints:

### `GET /`

Health check endpoint.

**Response:**
```json
{
  "message": "Hello World"
}
```

### `GET /student/{student_id}`

Retrieve a student's profile including their progress and learning rules.

**Parameters:**
- `student_id` (path): Unique identifier for the student

**Response:**
```json
{
  "student_id": "student_01",
  "progress_blob": "{\"mastered_standards\": [], \"developing_standards\": []}",
  "plan_rules_blob": "{\"allowed_materials\": [\"Crayons\", \"Paper\"], ...}"
}
```

**Error Responses:**
- `404`: Student not found

### `POST /generate_weekly_plan`

Generate a complete weekly lesson plan for a student using AI.

**Request Body:**
```json
{
  "student_id": "string",
  "grade_level": 0,
  "subject": "string"
}
```

**Request Model (PlanRequest):**
- `student_id` (string, required): Unique identifier for the student
- `grade_level` (integer, required): Grade level (0 = Kindergarten, 1 = 1st grade, etc.)
- `subject` (string, required): Subject area (may be overridden by student's theme rules)

**Response Model (WeeklyPlan):**
```json
{
  "plan_id": "plan_student_01_2025-01-15",
  "student_id": "student_01",
  "week_of": "2025-01-15",
  "weekly_overview": "Brief description of the week's learning progression",
  "daily_plan": [
    {
      "day": "Monday",
      "lesson_plan": {
        "objective": "Learning objective for the day",
        "materials_needed": ["Crayons", "Paper"],
        "procedure": [
          "Step 1: Introduction",
          "Step 2: Practice",
          "Step 3: Review"
        ]
      },
      "standard": {
        "standard_id": "VA.MATH.K.1a",
        "source": "VA",
        "subject": "Math",
        "grade_level": 0,
        "description": "The student will count forward to 10.",
        "json_blob": "..."
      },
      "standards": [...],
      "focus": "Day-specific learning focus"
    }
    // ... Tuesday through Friday
  ]
}
```

**Error Responses:**
- `400`: Invalid request or error generating plan
- `500`: Server error

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/generate_weekly_plan" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_01",
    "grade_level": 0,
    "subject": "Math"
  }'
```

---

## Overview

This project provides tools to:
- Initialize and manage a SQLite database for educational standards
- Ingest curriculum standards from JSON files
- Track student profiles and learning progress
- Generate AI-powered weekly lesson plans tailored to each student

## Detailed Setup Instructions

### Installing Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn for the web API
- OpenAI Python client for LLM integration
- Requests for API testing
- Pydantic for data validation

### Ingesting Standards

Run the ingestion script to create the database and populate it with standards:

```bash
python3 src/ingest_standards.py
```

This script will:
- Create `curriculum.db` SQLite database
- Create two tables: `standards` and `student_profiles`
- Read JSON files from `standards_data/` directory
- Insert standards data into the database
- Add a dummy student profile for testing

### Validating the Setup

Run the validation script to verify everything is working correctly:

```bash
python3 tests/validate_chunk1.py
```

## Database Schema

### `standards` Table

Stores educational standards and curriculum information.

| Column | Type | Description |
|--------|------|-------------|
| `standard_id` | TEXT | Primary key, unique identifier for the standard |
| `source` | TEXT | Source of the standard (e.g., "VA", "CommonCore") |
| `subject` | TEXT | Subject area (e.g., "Math", "Art") |
| `grade_level` | INTEGER | Grade level (0 = Kindergarten) |
| `description` | TEXT | Description of the standard |
| `json_blob` | TEXT | Original JSON object as string |

### `student_profiles` Table

Stores student information and learning progress.

| Column | Type | Description |
|--------|------|-------------|
| `student_id` | TEXT | Primary key, unique identifier for the student |
| `progress_blob` | TEXT | JSON blob tracking mastered and developing standards |
| `plan_rules_blob` | TEXT | JSON blob with parent rules and learning preferences |

## JSON Format for Standards

Place JSON files in the `standards_data/` directory with the following format:

```json
[
  {
    "id": "VA.MATH.K.1a",
    "source": "VA",
    "subject": "Math",
    "grade": 0,
    "description": "The student will count forward to 10."
  }
]
```

---

## Troubleshooting

### Common Issues

**"OPENAI_API_KEY environment variable not set"**
- Make sure you've exported the API key before starting the server
- Run: `export OPENAI_API_KEY="your-key-here"`

**"Could not connect to server"**
- Ensure the server is running with: `cd src && uvicorn main:app --reload`
- Check that the server is running on the expected port (default: 8000)

**"Student not found" (404 error)**
- Run the ingestion script to create the dummy student: `python3 src/ingest_standards.py`
- Use the correct student ID: `student_01`

**"No standards found for student"**
- Ensure the database has been populated: `python3 src/ingest_standards.py`
- Check that standards exist for the requested grade level and subject

**Connection refused or API errors**
- Verify your OpenAI API key is valid
- Check your internet connection
- If using a custom BASE_URL, ensure it's correct

---

## Project Structure

```
.
├── src/
│   ├── agent.py              # LLM integration for lesson plan generation
│   ├── db_utils.py           # Database utility functions
│   ├── ingest_standards.py   # Database initialization script
│   ├── logic.py              # Business logic for filtering standards
│   └── main.py               # FastAPI application and endpoints
├── tests/
│   ├── validate_chunk1.py    # Database validation tests
│   ├── validate_chunk2.py    # Student profile tests
│   ├── validate_chunk3.py    # Logic engine tests
│   └── validate_chunk4.py    # API endpoint tests
├── docs/                      # Documentation
├── standards_data/           # JSON files with educational standards
│   └── va_standards.json     # Virginia state standards
├── requirements.txt          # Python dependencies
└── curriculum.db             # SQLite database (generated)
```

---

## Advanced Usage

### Adding Custom Standards

To add your own educational standards:

1. Create a JSON file in the `standards_data/` directory
2. Format your standards according to the schema below
3. Run `python3 src/ingest_standards.py` to import them

### Creating Student Profiles

Students are stored in the `student_profiles` table with:
- **Progress tracking**: Lists of mastered and developing standards
- **Learning rules**: Parent preferences for materials, themes, and review schedules

Example student profile:
```json
{
  "student_id": "student_02",
  "progress_blob": {
    "mastered_standards": ["VA.MATH.K.1a"],
    "developing_standards": ["VA.MATH.K.2a"]
  },
  "plan_rules_blob": {
    "allowed_materials": ["Blocks", "Pencils", "Paper"],
    "parent_notes": "Student learns best with visual aids",
    "theme_rules": {
      "force_weekly_theme": true,
      "theme_subjects": ["Science", "Math"]
    },
    "review_rules": {
      "no_review_mastered_for_weeks": 3
    }
  }
}
```

### Running Tests

Validate each component of the system:

```bash
# Test database setup
python3 tests/validate_chunk1.py

# Test student profiles
python3 tests/validate_chunk2.py

# Test logic engine
python3 tests/validate_chunk3.py

# Test API endpoints (requires server running)
python3 tests/validate_chunk4.py
```

---