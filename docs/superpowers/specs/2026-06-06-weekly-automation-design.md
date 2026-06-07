# Weekly Automation Design

**Date:** 2026-06-06  
**Status:** Approved

## Overview

End-to-end automation for the weekly curriculum loop:

1. Friday evening → NTFY push to both phones reminding parent to submit feedback
2. Parent submits feedback via existing UI → proficiency update runs (existing behavior)
3. Feedback endpoint fires a background task → subject gap analysis → 3 lesson plans generated in parallel → NTFY push confirming plans are ready
4. Saturday morning safety-net script catches any missed generations

## Architecture

```
Cron (system)
└── scripts/send_weekly_reminder.py   (Friday 7pm: 0 19 * * 5)
      └── POST /homeschool "Time to review this week's lessons"

FastAPI feedback endpoint (existing: POST /students/{id}/weekly-packets/{packet_id}/feedback)
└── after save_packet_feedback() + update_student() succeed
      └── BackgroundTask: generate_trio_for_student(student_id)
            ├── src/subject_picker.py  → pick 3 subjects from progress gaps
            ├── generate_weekly_plan() × 3  (ThreadPoolExecutor, parallel)
            ├── POST /homeschool "Plans ready for <name>!"   (on success)
            └── POST /homeschool "Plan generation FAILED for <name>"  (on error)

Cron (system)
└── scripts/safety_net_generate.py    (Saturday 9am: 0 9 * * 6)
      └── find packets: has_feedback=true AND no packet created after feedback_completed_at
            └── generate_trio_for_student() for each → same NTFY outcomes
```

## New Files

### `src/ntfy.py`
Shared helper. Single function used by all scripts and background tasks.

```python
NTFY_URL = "http://100.97.236.69:2586/homeschool"

def notify(title: str, message: str, priority: str = "default") -> None:
    """POST a push notification to the NTFY homeschool topic."""
```

Swallows network errors with a logged warning — a failed push must never crash the caller.

### `src/subject_picker.py`
Reads a student's `progress_blob` and maps `developing_standards` back to subjects via the curriculum graph. Returns the top 3 subjects ranked by count of developing (non-mastered) standards.

**Fallback:** if progress data is empty or fewer than 3 subjects have developing standards, fills remaining slots by rotating through all available subjects in constants.SUBJECTS order.

Note: this module is intentionally simple — a more intelligent AI-driven picker is planned for a future iteration.

### `src/trio_generator.py`
Orchestrates parallel plan generation for a single student.

- Reads student profile via `get_student_profile(student_id)` to extract `grade_level` from `metadata_blob`
- Calls `subject_picker.pick_subjects(student_id)` → list of 3 subject strings
- Calls `generate_weekly_plan(student_id, grade_level, subject)` × 3 via `ThreadPoolExecutor(max_workers=3)`
- On all 3 succeeding: `notify("Plans ready for {name}!", ...)`
- On any unrecoverable exception: `notify("Plan generation FAILED for {name}", priority="high")` and re-raises so the caller can log

### `scripts/send_weekly_reminder.py`
Standalone script (~30 lines). No FastAPI dependency.

- Reads all students from `curriculum.db` directly via `db_utils.list_students()`
- Finds any packets with `status != completed` (pending feedback)
- Builds a message listing student names and packet counts
- `notify("Time to review this week's lessons!", message)`
- Exits 0 always — a failed reminder is logged, not fatal

### `scripts/safety_net_generate.py`
Standalone script. Idempotent — safe to run repeatedly.

- Queries DB for packets where `has_feedback = true` AND no packet exists for that student with `created_at > feedback_completed_at`
- Calls `trio_generator.generate_trio_for_student(student_id)` for each match
- Logs each action; NTFY fires per-student via trio_generator

## Changes to Existing Files

### `src/main.py` — `submit_packet_feedback` endpoint

Add `background_tasks: BackgroundTasks` parameter and queue the trio generator after the existing save calls:

```python
from fastapi import BackgroundTasks
from trio_generator import generate_trio_for_student

@app.post("/students/{student_id}/weekly-packets/{packet_id}/feedback", status_code=204)
def submit_packet_feedback(
    student_id: str,
    packet_id: str,
    request: SubmitFeedbackRequest,
    background_tasks: BackgroundTasks,          # added
):
    # ... existing validation, update_student(), save_packet_feedback() ...
    background_tasks.add_task(generate_trio_for_student, student_id)  # added
```

## Scheduling (system crontab)

```cron
# Weekly curriculum reminder — Friday 7pm
0 19 * * 5 cd /home/clates/agentic-curriculum && venv/bin/python3 scripts/send_weekly_reminder.py >> logs/reminder.log 2>&1

# Safety-net plan generation — Saturday 9am
0 9  * * 6 cd /home/clates/agentic-curriculum && venv/bin/python3 scripts/safety_net_generate.py >> logs/safety_net.log 2>&1
```

## NTFY Notification Inventory

| Trigger | Title | Priority |
|---------|-------|----------|
| Friday cron | "Time to review this week's lessons!" | default |
| Trio generation success | "Plans ready for {name}!" | default |
| Trio generation failure | "Plan generation FAILED for {name}" | high |

## What Is NOT Changing

- Unused plans from prior weeks are left in the pending queue — parent dismisses manually
- Subject picker logic is intentionally simple now; AI-driven gap analysis is a future iteration
- No frontend changes required

## Future Work

- Replace `subject_picker.py` heuristic with LLM-based gap analysis using the full curriculum graph
- Per-student NTFY topics if multiple caregivers want different notification streams
