# agentic-curriculum

A Python-based system for managing educational curriculum standards and student profiles using SQLite.

## Overview

This project provides tools to:
- Initialize and manage a SQLite database for educational standards
- Ingest curriculum standards from JSON files
- Track student profiles and learning progress

## Setup and Usage

### 0. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn for the web API
- OpenAI Python client for LLM integration
- Requests for API testing
- Pydantic for data validation

Alternatively, you can use a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1. Ingest Standards

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

### 2. Validate the Setup

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

## Project Structure

```
.
├── src/
│   ├── agent.py
│   ├── db_utils.py
│   ├── ingest_standards.py
│   ├── logic.py
│   └── main.py
├── tests/
│   ├── validate_chunk1.py
│   ├── validate_chunk2.py
│   ├── validate_chunk3.py
│   └── validate_chunk4.py
├── docs/
├── standards_data/
└── curriculum.db
