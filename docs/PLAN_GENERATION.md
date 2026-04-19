# Plan Generation

A **plan** (also called a **packet**) is a complete weekly lesson plan for one student in one subject. This document covers how plans are generated, stored, and surfaced in the UI.

---

## Concepts

### Packet
A packet is the atomic unit of a week's work. It contains:
- A **weekly overview** describing the arc of the week
- Five **daily lessons**, each targeting one or more curriculum standards
- **Worksheet artifacts** (PNG and PDF) for supported worksheet types
- **Feedback** submitted by the parent after the week is complete

One packet = one student × one subject × one week.

### Standards
Plans are built around educational standards pulled from the database. Standards are filtered by:
- **Grade level** — only standards for the requested grade are considered
- **Mastery** — already-mastered standards are excluded
- **Cooldown** — recently covered standards are skipped based on feedback history:
  - Mastered standards: 2–12 week cooldown (increases with consecutive mastery)
  - Benched standards: 8-week cooldown
  - Developing standards: 1-week cooldown
  - If all standards are in cooldown, they are used anyway with a logged warning

---

## Generation Flow

Generation is triggered via `POST /generate_weekly_plan` and is **synchronous** — the HTTP request blocks for 30–60 seconds while the plan is assembled.

### 1. Setup (`src/agent.py:547–645`)
- Validates `OPENAI_API_KEY` is set
- Loads the student profile (rules, progress, metadata)
- Fetches up to 10 eligible standards via `get_filtered_standards()`
- Applies cooldown filtering via `is_standard_eligible()`
- Calculates `activity_bias` from the student's `quantity_preferences` to adjust lesson length

### 2. Weekly Scaffold — LLM Call 1 (`src/agent.py:647–705`)
A single LLM call generates the week's structure: how standards are distributed across five days and what each day's focus is.

**Prompt inputs:** grade level, subject, first 5 available standards, allowed materials, parent notes, activity guidance  
**Response format:**
```json
{
  "weekly_overview": "Brief description of week progression",
  "daily_assignments": [
    { "day": "Monday", "standard_ids": ["std_id"], "focus": "Brief description" },
    ...
  ]
}
```
If the LLM response fails to parse, a default scaffold is created by distributing available standards evenly across 5 days.

### 3. Daily Lessons — LLM Calls 2–6 (`src/agent.py:728–770`)
Five daily lesson calls run **in parallel** via a `ThreadPoolExecutor` (default: 5 workers, configurable via `MAX_DAILY_PLAN_THREADS`).

Each call receives:
- The standard(s) assigned to that day
- Allowed materials and parent notes
- The day's focus from the scaffold

**Response format:**
```json
{
  "lesson_plan": {
    "objective": "Clear learning objective",
    "materials_needed": ["Material1"],
    "procedure": ["Step 1 (15 min)", "Step 2 (20 min)"]
  },
  "resources": {
    "mathWorksheet": { ... },
    "readingWorksheet": { ... }
  }
}
```
`resources` is optional. If present, worksheets are rendered to PNG and PDF and stored in `artifacts/`.

If a daily plan call fails, a fallback lesson is created from the standard's description and the student's allowed materials — generation does not abort.

### 4. Assembly & Persistence (`src/agent.py:772–791`)
The scaffold and five daily plans are assembled into a single weekly plan object and saved via `save_weekly_packet()` (`src/packet_store.py`). The full plan JSON is stored in the database and the artifact files remain on disk.

---

## LLM Configuration

| Setting | Env Var | Default |
|---|---|---|
| API key | `OPENAI_API_KEY` | *(required)* |
| Base URL | `OPENAI_BASE_URL` | OpenAI default |
| Model | `OPENAI_MODEL` | `gpt-3.5-turbo` |
| Parallel workers | `MAX_DAILY_PLAN_THREADS` | `5` |

The system prompt (`src/prompts.py:247–255`) instructs the LLM that it is building content for a **homeschool environment** with one parent and one student, emphasising hands-on, at-home activities.

Temperature is `0.7` for all calls. All calls use `response_format: {"type": "json_object"}` to enforce valid JSON output.

---

## Worksheet Artifacts

Supported worksheet types that render to files:
- `mathWorksheet` — vertical addition or subtraction problems
- `readingWorksheet` — reading passage with comprehension questions

Types described in the prompt but **not yet rendered**: `vennDiagram`, `featureMatrix`, `oddOneOut`, `treeMap`. If the LLM requests one of these, the error is logged and the lesson continues without that worksheet.

### Artifact Storage
```
artifacts/
└── plan_{student_id}_{week_of}/
    ├── monday/
    │   ├── math.png
    │   ├── math.pdf
    │   └── reading_1.pdf
    ├── tuesday/
    │   └── math.png
    └── ...
```

Each artifact is tracked in the `worksheet_artifacts` table with its file path, SHA-256 checksum, and file size.

---

## Database Schema

### `weekly_packets`
| Column | Type | Description |
|---|---|---|
| `packet_id` | TEXT PK | `plan_{student_id}_{week_of}` |
| `student_id` | TEXT | Owning student |
| `grade_level` | INTEGER | 0 = Kindergarten, 1–12 = grades |
| `subject` | TEXT | Subject area |
| `week_of` | TEXT | `YYYY-MM-DD` (Monday of the week) |
| `status` | TEXT | `ready` or `complete` |
| `weekly_overview` | TEXT | Narrative summary of the week |
| `summary_json` | TEXT | `{daily_count, resource_days, worksheet_counts, artifact_count}` |
| `payload_json` | TEXT | Full plan JSON including all daily lessons |
| `created_at` / `updated_at` | TEXT | UTC timestamps |

### `daily_lessons`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `packet_id` | TEXT FK | References `weekly_packets` |
| `day_label` | TEXT | e.g. `Monday` |
| `focus` | TEXT | Day focus from scaffold |
| `standards_json` | TEXT | Array of standard objects |
| `lesson_plan_json` | TEXT | Objective, materials, procedure |
| `resources_json` | TEXT | Resource payloads with artifact metadata |
| `worksheet_plans_json` | TEXT | Worksheet planning metadata |
| `resource_errors_json` | TEXT | Rendering errors, if any |

### `worksheet_artifacts`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `packet_id` | TEXT FK | References `weekly_packets` |
| `daily_lesson_id` | INTEGER FK | References `daily_lessons` |
| `day_label` | TEXT | e.g. `Monday` |
| `kind` | TEXT | `mathWorksheet`, `readingWorksheet` |
| `file_format` | TEXT | `png` or `pdf` |
| `file_path` | TEXT | Relative path from project root |
| `checksum` | TEXT | SHA-256 hex digest |
| `file_size_bytes` | INTEGER | |
| `metadata_json` | TEXT | Worksheet-specific metadata |

### `packet_feedback`
| Column | Type | Description |
|---|---|---|
| `feedback_id` | INTEGER PK | Auto-increment |
| `packet_id` | TEXT FK | References `weekly_packets` |
| `student_id` | TEXT | |
| `completed_at` | TEXT | UTC timestamp |
| `mastery_feedback_blob` | TEXT | `{"overall": "STRUGGLING"\|"DEVELOPING"\|"MASTERED"}` |
| `quantity_feedback` | INTEGER | `-2` (too much) → `+2` (too little) |

---

## API Endpoints

### `POST /generate_weekly_plan`
Generate a new weekly plan. Blocks until complete (~30–60 seconds).

**Request:**
```json
{ "student_id": "string", "grade_level": 0, "subject": "Math" }
```
**Response:** Full weekly plan JSON  
**Errors:** `400` if student not found or no standards available; `500` on LLM/other failures

### `GET /students/{student_id}/weekly-packets`
List all packets for a student.

**Query params:** `page` (default 1), `page_size` (default 20, max 50), `week_of` (optional filter)  
**Response:** `{ items: [WeeklyPacketSummary], pagination: {...} }`

### `GET /students/{student_id}/weekly-packets/{packet_id}`
Fetch the full payload for a specific packet, including all daily lessons and artifact metadata.  
Responds with ETag for caching.

### `GET /students/{student_id}/weekly-packets/{packet_id}/worksheets`
List all worksheet artifacts for a packet, grouped by day and type.

**Response:** `{ packet_id, artifact_count, items: [{ day_label, resource_kind, artifacts: [...] }] }`

### `GET /students/{student_id}/worksheet-artifacts/{artifact_id}`
Download a worksheet file (PNG or PDF).  
Returns binary with `Content-Disposition: attachment`, `Cache-Control`, and `ETag` headers.  
Validates that the artifact belongs to the requested student.

### `POST /students/{student_id}/weekly-packets/{packet_id}/feedback`
Submit feedback after completing a week's plan.

**Request:**
```json
{
  "mastery_feedback": { "<standard_id>": "DEVELOPING", "<standard_id_2>": "MASTERED" },
  "quantity_feedback": 0
}
```
`mastery_feedback` is a map of standard IDs to ratings. Valid ratings: `NOT_STARTED`, `DEVELOPING`, `MASTERED`, `BENCHED`.

`quantity_feedback` values: `-2` too much, `-1` slightly too much, `0` just right, `1` slightly too little, `2` too little

**Side effects:**
- Updates `student_profiles.progress_blob` — moves standards into mastered/developing lists, sets cooldowns
- Updates `student_profiles.plan_rules_blob` — adjusts `activity_bias` (range: −1.0 to +1.0) to influence future lesson length

> **Known bug:** The frontend currently sends `{"overall": "STRUGGLING"|"DEVELOPING"|"MASTERED"}` — using the literal key `"overall"` rather than a real standard ID, and `STRUGGLING` is not a valid backend rating. Submitting `STRUGGLING` feedback will fail validation on the backend.

### `GET /students/{student_id}/weekly-packets/{packet_id}/feedback`
Retrieve previously submitted feedback for a packet.

---

## Feedback & Adaptive Planning

Submitting feedback after a week closes the loop for future plans:

**Mastery feedback** updates each standard's cooldown in `standard_metadata`:
- `MASTERED` → standard moved to mastered list, cooldown increases with each consecutive mastery (2–12 weeks)
- `DEVELOPING` → standard stays in developing list with 1-week cooldown
- `NOT_STARTED` → no list change, cooldown reset to 0
- `BENCHED` → standard removed from active consideration, 8-week cooldown

**Quantity feedback** adjusts `activity_bias` in the student's plan rules:
| Rating | Value sent | Adjustment |
|---|---|---|
| Too much | −2 | −0.30 |
| Slightly too much | −1 | −0.15 |
| Just right | 0 | ×0.9 (decays toward neutral) |
| Slightly too little | +1 | +0.15 |
| Too little | +2 | +0.30 |

`activity_bias` controls how many activities are generated per day. At 0.0, the default is 3 activities. Bias adjusts this between 1 and 6 activities per day.

---

## Logging

Every generation run writes structured logs to `logs/generate-weekly/{run_id}/`:

| File | Contents |
|---|---|
| `run_metadata.json` | run_id, student_id, grade_level, subject, created_at |
| `weekly_scaffold_llm_exchange.json` | Full LLM request and response for scaffold call |
| `weekly_scaffold.json` | Parsed scaffold (or error + raw response) |
| `weekly_plan.json` | Final assembled weekly plan |
| `daily_plans/{day}_llm_exchange.json` | Per-day LLM request and response |
| `daily_plans/{day}_response.json` | Parsed response (or error details) |
| `daily_plans/{day}.json` | Final assembled day plan |
| `daily_plans/{day}_error.json` | Error details if that day failed |

---

## Known Limitations

- **Grade level hardcoded in frontend** (`frontend/app/plans/page.tsx:161`): the student list passed to the Generate Plan modal always sets `grade: 0`. The user must manually select the correct grade level in the modal dropdown each time.
- **Feedback broken for `STRUGGLING`** (`frontend/app/plans/page.tsx:542`): the UI offers "Struggling" as a mastery option but the backend rejects it — `STRUGGLING` is not a valid rating. Valid backend ratings are `NOT_STARTED`, `DEVELOPING`, `MASTERED`, `BENCHED`.
- **Feedback key mismatch**: the frontend sends `mastery_feedback: { "overall": "<rating>" }` but the backend expects `{ "<standard_id>": "<rating>" }`. Feedback submitted through the UI does not update per-standard progress correctly.
- **Generation is synchronous**: the HTTP request blocks for the full generation duration. There is no progress indicator and no cancellation mechanism.
- **Unimplemented worksheet types**: `vennDiagram`, `featureMatrix`, `oddOneOut`, and `treeMap` are described in the LLM prompt but have no rendering code. Requests for these types fail silently.
- **One packet per student/week**: `packet_id` is `plan_{student_id}_{week_of}`. Regenerating a plan for the same student and week overwrites the previous packet and its artifacts.
