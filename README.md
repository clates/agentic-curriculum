# agentic-curriculum

A Python-based system for managing educational curriculum standards and student profiles using SQLite.

## Overview

This project provides tools to:
- Initialize and manage a SQLite database for educational standards
- Ingest curriculum standards from JSON files
- Track student profiles and learning progress

## Setup and Usage

### 1. Ingest Standards

Run the ingestion script to create the database and populate it with standards:

```bash
python3 ingest_standards.py
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
python3 validate_chunk1.py
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

## Files

- `ingest_standards.py` - Main script for database initialization and data ingestion
- `validate_chunk1.py` - Validation script to verify the setup
- `standards_data/` - Directory containing JSON files with curriculum standards
- `curriculum.db` - SQLite database (generated, not version controlled)
