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

---

## 🖥️ Frontend

The project includes a modern Next.js-based web interface for managing students and curriculum.

### Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
4.  Open [http://localhost:3000](http://localhost:3000) in your browser.

### Key Features
- **Dashboard**: High-level overview of active students and plan generation stats.
- **Student Profiles**: Detailed view of student metadata and standard mastery progress.
- **Plan Generation UI**: Intuitive modals to trigger new AI-generated weekly plans.
- **Progress Tracking**: Visual indicators for standard mastery and educational milestones.

---

## 🏗️ Worksheet Ecosystem

The system features a robust, extensible worksheet engine designed to generate high-quality, printable educational resources. Each worksheet is structured as a data model that can be rendered to multiple formats (Markdown, PDF, HTML).

### Core Capabilities
- **Pedagogical Structure**: Every worksheet includes clear titles, instructions, and logically grouped problems.
- **Automatic Formatting**: Math problems are vertically aligned for column-based arithmetic; reading passages are wrapped for readability.
- **Serialization**: Worksheets are stored as JSON in the database, allowing for easy retrieval and re-rendering.
- **Feedback Loop**: Generated worksheets are linked to specific standards, enabling automated progress tracking when completed.

### Available Worksheet Types
- **🧮 Math Practice**: Vertical arithmetic problems (addition, subtraction, multiplication) with operand validation.
- **📖 Reading Comprehension**: Passages paired with open-response questions and vocabulary builders.
- **⭕ Venn Diagrams**: Visual comparison structures for identifying similarities and differences between two concepts.
- **📊 Feature Matrices**: Grids for classifying items against multiple attributes (ideal for science and social studies).
- **🔎 Odd One Out**: Logical reasoning rows where students identify the item that doesn't fit the pattern.
- **🌳 Tree Maps**: Hierarchical classification tools for sorting information into categories.

---

## 📝 Feedback & Adaptive Learning

The system adapts to each student through a structured feedback loop. When a weekly packet is completed, feedback is submitted to the API to update the student's profile.

- **Mastery Feedback**: Mark specific standards as `mastered` or `developing`. The logic engine uses this to decide whether to introduce new concepts or provide remediation.
- **Quantity Feedback**: Adjust the "dosage" of activities. If a student is overwhelmed or finishing too quickly, the system adjusts the number of tasks in subsequent weeks.

---

## 🧹 Code Style & Linting

All Python files are auto-formatted with [Black](https://github.com/psf/black) and linted with [Ruff](https://docs.astral.sh/ruff/), enforced automatically via [pre-commit](https://pre-commit.com/) hooks.

### Setup

```bash
pip install -r requirements.txt
pre-commit install
```

`pre-commit install` adds a git `pre-commit` hook that runs Ruff (lint/fix) and then Black on staged Python files. Commits will fail until formatting or lint issues are resolved, ensuring a consistent style and catching mistakes like unused imports before they land.

---

## 🐳 Run with Docker

Prefer containers? The repo ships with a `Dockerfile` that bakes in dependencies, ingests standards, and starts Uvicorn automatically.

```bash
# Build the image (run from repo root)
docker build -t agentic-curriculum .

# Run the API (exposes port 8000 by default)
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY="your-api-key" \
  agentic-curriculum
```

Notes:

- `OPENAI_API_KEY` must be provided at runtime (and any other optional env vars such as `OPENAI_BASE_URL` or `OPENAI_MODEL`).
- The image executes `python src/ingest_standards.py` during build so `curriculum.db` is ready before the server boots.
- Container logs include the structured request logs written to `/app/logs` inside the image.

---

## API Reference

The FastAPI server exposes the following endpoints:

### Student Management
- `GET /student/{student_id}`: Retrieve a student's profile.
- `POST /students`: Create a new student profile.
- `PUT /student/{student_id}`: Update student metadata or learning rules.
- `DELETE /student/{student_id}`: Remove a student profile.

### Lesson Planning
- `POST /generate_weekly_plan`: Generate a 5-day AI lesson plan tailored to student progress.
- `GET /students/{id}/weekly-packets`: List history of generated packets.
- `GET /students/{id}/weekly-packets/{id}`: Retrieve full JSON payload for a specific packet.

### Resources & Feedback
- `GET /students/{id}/weekly-packets/{id}/worksheets`: Get a manifest of all worksheet artifacts for a packet.
- `GET /students/{id}/worksheet-artifacts/{id}`: Download a rendered PDF/PNG worksheet.
- `POST /students/{id}/weekly-packets/{id}/feedback`: Submit mastery and quantity feedback.
- `GET /system/options`: Retrieve valid subjects, grades, and worksheet types.

---

## 🧪 Running Tests

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
