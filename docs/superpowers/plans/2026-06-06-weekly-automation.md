# Weekly Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automate the weekly curriculum loop: Friday NTFY reminder → parent submits feedback → backend generates 3 lesson plans per student → NTFY confirmation push; with a Saturday safety-net cron and NTFY error alerts.

**Architecture:** A shared `ntfy.py` helper handles all pushes. `subject_picker.py` reads each student's `progress_blob` and ranks subjects by developing-standards count using the existing curriculum graph. `trio_generator.py` orchestrates parallel `generate_weekly_plan()` calls and fires NTFY on completion or failure. The feedback endpoint gains a `BackgroundTask` hook; two standalone cron scripts handle the reminder and safety net.

**Tech Stack:** Python 3.12, FastAPI `BackgroundTasks`, `ThreadPoolExecutor` (already used in `agent.py`), `requests`, pytest, `unittest.mock`, SQLite (direct via `sqlite3`).

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `src/ntfy.py` | Single `notify()` function; swallows network errors |
| Create | `src/subject_picker.py` | Ranks subjects by developing-standards gap; falls back to SUBJECTS rotation |
| Create | `src/trio_generator.py` | Resolves grade_level, picks 3 subjects, generates plans in parallel, fires NTFY |
| Create | `scripts/send_weekly_reminder.py` | Standalone Friday cron — fetches students, posts reminder push |
| Create | `scripts/safety_net_generate.py` | Standalone Saturday cron — finds students with feedback but no new plans |
| Create | `tests/test_ntfy.py` | Unit tests for ntfy helper |
| Create | `tests/test_subject_picker.py` | Unit tests for subject picker logic |
| Create | `tests/test_trio_generator.py` | Unit tests for trio generator |
| Create | `tests/test_weekly_automation_integration.py` | Integration test: feedback endpoint queues background task |
| Modify | `src/main.py` | Add `BackgroundTasks` param + `add_task` call to `submit_packet_feedback` |

---

## Task 1: NTFY Helper (`src/ntfy.py`)

**Files:**
- Create: `src/ntfy.py`
- Create: `tests/test_ntfy.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ntfy.py`:

```python
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ntfy


def test_notify_posts_to_correct_url():
    with patch("ntfy.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        ntfy.notify("Test Title", "Test message")
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert call_kwargs[0][0] == "http://100.97.236.69:2586/homeschool"
        assert call_kwargs[1]["headers"]["Title"] == "Test Title"
        assert call_kwargs[1]["data"] == "Test message"
        assert call_kwargs[1]["headers"]["Priority"] == "default"


def test_notify_uses_custom_priority():
    with patch("ntfy.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        ntfy.notify("Urgent", "Something broke", priority="high")
        assert mock_post.call_args[1]["headers"]["Priority"] == "high"


def test_notify_swallows_network_errors(caplog):
    import logging
    with patch("ntfy.requests.post", side_effect=Exception("timeout")):
        with caplog.at_level(logging.WARNING, logger="ntfy"):
            ntfy.notify("Fail", "This will fail silently")
    # Should not raise; warning should be logged
    assert any("timeout" in r.message for r in caplog.records)


def test_notify_swallows_bad_status(caplog):
    import logging
    with patch("ntfy.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=403)
        with caplog.at_level(logging.WARNING, logger="ntfy"):
            ntfy.notify("Fail", "403 from server")
    assert any("403" in r.message for r in caplog.records)
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
cd /home/clates/agentic-curriculum
venv/bin/python -m pytest tests/test_ntfy.py -v
```
Expected: `ModuleNotFoundError: No module named 'ntfy'`

- [ ] **Step 3: Write the implementation**

Create `src/ntfy.py`:

```python
import logging
import requests

logger = logging.getLogger(__name__)

NTFY_URL = "http://100.97.236.69:2586/homeschool"


def notify(title: str, message: str, priority: str = "default") -> None:
    """POST a push notification to the NTFY homeschool topic.

    Swallows all errors — a failed push must never crash the caller.
    """
    try:
        resp = requests.post(
            NTFY_URL,
            headers={"Title": title, "Priority": priority},
            data=message,
            timeout=5,
        )
        if resp.status_code >= 400:
            logger.warning("ntfy push returned %s for title=%r", resp.status_code, title)
    except Exception as exc:
        logger.warning("ntfy push failed for title=%r: %s", title, exc)
```

- [ ] **Step 4: Run the tests to confirm they pass**

```bash
venv/bin/python -m pytest tests/test_ntfy.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/ntfy.py tests/test_ntfy.py
git commit -m "feat: add ntfy push notification helper"
```

---

## Task 2: Subject Picker (`src/subject_picker.py`)

**Files:**
- Create: `src/subject_picker.py`
- Create: `tests/test_subject_picker.py`

**How it works:** For each subject in `SUBJECTS`, load the curriculum graph from `curriculum.db` and count how many of the student's `developing_standards` IDs appear as nodes in that graph. Subjects are ranked by count (descending). Return the top 3. If fewer than 3 subjects have any developing standards, fill remaining slots from `SUBJECTS` in order (skipping already-selected ones).

- [ ] **Step 1: Write the failing tests**

Create `tests/test_subject_picker.py`:

```python
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import subject_picker
from subject_picker import pick_subjects


def _make_profile(developing: list[str]) -> dict:
    return {
        "student_id": "test_student",
        "progress_blob": json.dumps({
            "mastered_standards": [],
            "developing_standards": developing,
        }),
        "plan_rules_blob": json.dumps({}),
        "metadata_blob": json.dumps({}),
    }


def _make_graph(node_ids: list[str]) -> MagicMock:
    g = MagicMock()
    g.graph.nodes.return_value = node_ids
    return g


def test_returns_three_subjects():
    profile = _make_profile(["MATH.1", "MATH.2", "ENG.1", "SCI.1", "SCI.2", "SCI.3", "HIST.1"])

    def fake_load(db_path, subject_keyword=None):
        mapping = {
            "Math": ["MATH.1", "MATH.2"],
            "English": ["ENG.1"],
            "Science": ["SCI.1", "SCI.2", "SCI.3"],
            "History": ["HIST.1"],
            "Computer Science": [],
        }
        return _make_graph(mapping.get(subject_keyword, []))

    with patch("subject_picker.get_student_profile", return_value=profile), \
         patch("subject_picker.load_from_db", side_effect=fake_load):
        result = pick_subjects("test_student")

    assert len(result) == 3
    assert result[0] == "Science"   # 3 developing
    assert result[1] == "Math"      # 2 developing
    assert result[2] == "English"   # 1 developing (History also has 1, tie broken by SUBJECTS order)


def test_falls_back_when_progress_sparse():
    profile = _make_profile([])  # no developing standards

    with patch("subject_picker.get_student_profile", return_value=profile), \
         patch("subject_picker.load_from_db", return_value=_make_graph([])):
        result = pick_subjects("test_student")

    assert len(result) == 3
    # Falls back to first 3 from SUBJECTS
    from constants import SUBJECTS
    assert result == SUBJECTS[:3]


def test_falls_back_when_only_one_subject_has_gap():
    profile = _make_profile(["MATH.1"])

    def fake_load(db_path, subject_keyword=None):
        return _make_graph(["MATH.1"] if subject_keyword == "Math" else [])

    with patch("subject_picker.get_student_profile", return_value=profile), \
         patch("subject_picker.load_from_db", side_effect=fake_load):
        result = pick_subjects("test_student")

    assert len(result) == 3
    assert "Math" in result


def test_raises_when_student_not_found():
    with patch("subject_picker.get_student_profile", return_value=None):
        import pytest
        with pytest.raises(ValueError, match="Student not found"):
            pick_subjects("ghost_student")
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
venv/bin/python -m pytest tests/test_subject_picker.py -v
```
Expected: `ModuleNotFoundError: No module named 'subject_picker'`

- [ ] **Step 3: Write the implementation**

Create `src/subject_picker.py`:

```python
import json
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from constants import SUBJECTS
from curriculum_graph import load_from_db
from db_utils import get_student_profile

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = str(PROJECT_ROOT / "curriculum.db")


def pick_subjects(student_id: str) -> list[str]:
    """Return 3 subjects ranked by count of developing standards.

    Falls back to rotating through SUBJECTS if progress data is sparse.
    """
    profile = get_student_profile(student_id)
    if profile is None:
        raise ValueError(f"Student not found: {student_id}")

    progress = json.loads(profile["progress_blob"] or "{}")
    developing = set(progress.get("developing_standards", []))

    scores: dict[str, int] = {}
    for subject in SUBJECTS:
        try:
            graph = load_from_db(DB_PATH, subject_keyword=subject)
            node_ids = set(graph.graph.nodes())
            scores[subject] = len(developing & node_ids)
        except Exception as exc:
            logger.warning("subject_picker: failed to load graph for %s: %s", subject, exc)
            scores[subject] = 0

    ranked = sorted(SUBJECTS, key=lambda s: scores.get(s, 0), reverse=True)

    # Take subjects with at least 1 developing standard first
    selected = [s for s in ranked if scores.get(s, 0) > 0][:3]

    # Fill remaining slots from SUBJECTS rotation (preserve order, skip already selected)
    if len(selected) < 3:
        for subject in SUBJECTS:
            if subject not in selected:
                selected.append(subject)
            if len(selected) == 3:
                break

    return selected
```

- [ ] **Step 4: Run the tests to confirm they pass**

```bash
venv/bin/python -m pytest tests/test_subject_picker.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/subject_picker.py tests/test_subject_picker.py
git commit -m "feat: add subject picker using developing-standards gap analysis"
```

---

## Task 3: Trio Generator (`src/trio_generator.py`)

**Files:**
- Create: `src/trio_generator.py`
- Create: `tests/test_trio_generator.py`

**How it works:** Reads grade_level from the student's most recent weekly packet (falls back to 0 if none). Calls `pick_subjects()` → 3 subjects. Generates all 3 plans in parallel via `ThreadPoolExecutor`. On all success: NTFY "Plans ready". On any failure: NTFY "FAILED" at high priority, then re-raises.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_trio_generator.py`:

```python
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trio_generator


def _make_profile(name: str = "Alice") -> dict:
    return {
        "student_id": "s1",
        "progress_blob": json.dumps({"mastered_standards": [], "developing_standards": []}),
        "plan_rules_blob": json.dumps({}),
        "metadata_blob": json.dumps({"name": name}),
    }


def test_generates_three_plans_and_notifies():
    with patch("trio_generator.get_student_profile", return_value=_make_profile("Alice")), \
         patch("trio_generator._get_grade_level", return_value=2), \
         patch("trio_generator.pick_subjects", return_value=["Math", "English", "Science"]), \
         patch("trio_generator.generate_weekly_plan", return_value={"ok": True}) as mock_gen, \
         patch("trio_generator.notify") as mock_notify:
        trio_generator.generate_trio_for_student("s1")

    assert mock_gen.call_count == 3
    subjects_called = {c.kwargs["subject"] for c in mock_gen.call_args_list}
    assert subjects_called == {"Math", "English", "Science"}
    mock_notify.assert_called_once()
    assert "Alice" in mock_notify.call_args[0][0]


def test_notifies_failure_on_exception():
    with patch("trio_generator.get_student_profile", return_value=_make_profile("Bob")), \
         patch("trio_generator._get_grade_level", return_value=0), \
         patch("trio_generator.pick_subjects", return_value=["Math", "English", "Science"]), \
         patch("trio_generator.generate_weekly_plan", side_effect=RuntimeError("openai down")), \
         patch("trio_generator.notify") as mock_notify:
        import pytest
        with pytest.raises(RuntimeError):
            trio_generator.generate_trio_for_student("s1")

    mock_notify.assert_called_once()
    title = mock_notify.call_args[0][0]
    assert "FAILED" in title
    priority = mock_notify.call_args[1].get("priority") or mock_notify.call_args[0][2]
    assert priority == "high"


def test_get_grade_level_from_most_recent_packet():
    packets = [{"grade_level": 3}, {"grade_level": 1}]
    with patch("trio_generator.list_weekly_packets", return_value=(packets, False)):
        assert trio_generator._get_grade_level("s1") == 3


def test_get_grade_level_defaults_to_zero_when_no_packets():
    with patch("trio_generator.list_weekly_packets", return_value=([], False)):
        assert trio_generator._get_grade_level("s1") == 0
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
venv/bin/python -m pytest tests/test_trio_generator.py -v
```
Expected: `ModuleNotFoundError: No module named 'trio_generator'`

- [ ] **Step 3: Write the implementation**

Create `src/trio_generator.py`:

```python
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from agent import generate_weekly_plan
from db_utils import get_student_profile
from ntfy import notify
from packet_store import list_weekly_packets
from subject_picker import pick_subjects

logger = logging.getLogger(__name__)


def _get_grade_level(student_id: str) -> int:
    """Return grade_level from the student's most recent weekly packet, or 0."""
    packets, _ = list_weekly_packets(student_id, limit=1, offset=0)
    if packets:
        return packets[0].get("grade_level", 0)
    return 0


def generate_trio_for_student(student_id: str) -> None:
    """Generate 3 lesson plans for a student and push NTFY on completion or failure."""
    profile = get_student_profile(student_id)
    metadata = json.loads(profile.get("metadata_blob") or "{}") if profile else {}
    name = metadata.get("name", student_id)

    try:
        grade_level = _get_grade_level(student_id)
        subjects = pick_subjects(student_id)

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(
                    generate_weekly_plan,
                    student_id=student_id,
                    grade_level=grade_level,
                    subject=subject,
                ): subject
                for subject in subjects
            }
            for future in as_completed(futures):
                subject = futures[future]
                exc = future.exception()
                if exc:
                    raise exc
                logger.info("trio_generator: plan generated for %s / %s", student_id, subject)

        notify(f"Plans ready for {name}!", f"Math, Reading & more packets are in the queue.")
    except Exception as exc:
        logger.error("trio_generator: failed for %s: %s", student_id, exc)
        notify(f"Plan generation FAILED for {name}", str(exc), priority="high")
        raise
```

- [ ] **Step 4: Run the tests to confirm they pass**

```bash
venv/bin/python -m pytest tests/test_trio_generator.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/trio_generator.py tests/test_trio_generator.py
git commit -m "feat: add trio generator for parallel weekly plan generation"
```

---

## Task 4: Wire Feedback Endpoint (`src/main.py`)

**Files:**
- Modify: `src/main.py`
- Create: `tests/test_weekly_automation_integration.py`

- [ ] **Step 1: Write the failing integration test**

Create `tests/test_weekly_automation_integration.py`:

```python
import importlib
import json
import os
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = str(PROJECT_ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

MODULE_NAMES_TO_CLEAR = [
    "packet_store", "db_utils", "agent", "main",
    "src.packet_store", "src.db_utils", "src.agent", "src.main",
    "trio_generator", "src.trio_generator",
]


def _bootstrap_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE student_profiles (
            student_id TEXT PRIMARY KEY,
            progress_blob TEXT,
            plan_rules_blob TEXT,
            metadata_blob TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE weekly_packets (
            packet_id TEXT PRIMARY KEY,
            student_id TEXT,
            grade_level INTEGER,
            subject TEXT,
            week_of TEXT,
            status TEXT,
            payload_json TEXT,
            summary_json TEXT,
            updated_at TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE packet_feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            packet_id TEXT,
            student_id TEXT,
            mastery_feedback TEXT,
            quantity_feedback INTEGER,
            completed_at TEXT
        )
    """)
    conn.commit()
    conn.close()


@pytest.fixture()
def automation_client(tmp_path, monkeypatch):
    db_path = tmp_path / "auto.db"
    _bootstrap_db(db_path)
    os.environ["CURRICULUM_DB_PATH"] = str(db_path)

    for name in MODULE_NAMES_TO_CLEAR:
        sys.modules.pop(name, None)

    db_utils = importlib.import_module("src.db_utils")
    sys.modules["db_utils"] = db_utils
    packet_store = importlib.import_module("src.packet_store")
    sys.modules["packet_store"] = packet_store

    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO student_profiles VALUES (?, ?, ?, ?)",
        ("s1",
         json.dumps({"mastered_standards": [], "developing_standards": []}),
         json.dumps({}),
         json.dumps({"name": "Test Kid"})),
    )
    conn.execute(
        "INSERT INTO weekly_packets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("pkt1", "s1", 2, "Math", "2026-06-01", "active",
         json.dumps({}), json.dumps({}), "2026-06-01T00:00:00Z", "2026-06-01T00:00:00Z"),
    )
    conn.commit()
    conn.close()

    main_module = importlib.import_module("src.main")
    importlib.reload(main_module)
    yield TestClient(main_module.app)


def test_feedback_submission_queues_trio_generation(automation_client):
    trio_calls = []

    def fake_trio(student_id):
        trio_calls.append(student_id)

    with patch("src.main.generate_trio_for_student", fake_trio):
        resp = automation_client.post(
            "/students/s1/weekly-packets/pkt1/feedback",
            json={"mastery_feedback": {"MATH.1": "MASTERED"}, "quantity_feedback": 0},
        )

    assert resp.status_code == 204
    assert trio_calls == ["s1"]
```

- [ ] **Step 2: Run the test to confirm it fails**

```bash
venv/bin/python -m pytest tests/test_weekly_automation_integration.py -v
```
Expected: FAIL — background task not yet wired.

- [ ] **Step 3: Modify `src/main.py`**

Add the import at the top of `src/main.py`, alongside existing imports:

```python
from fastapi import FastAPI, HTTPException, Query, Response, BackgroundTasks
from trio_generator import generate_trio_for_student
```

Then update the `submit_packet_feedback` function signature and add the `add_task` call. Find this line:

```python
def submit_packet_feedback(student_id: str, packet_id: str, request: SubmitFeedbackRequest):
```

Replace with:

```python
def submit_packet_feedback(
    student_id: str,
    packet_id: str,
    request: SubmitFeedbackRequest,
    background_tasks: BackgroundTasks,
):
```

Then find the final `try` block's last line (the `save_packet_feedback` call) and add immediately after it, still inside the `try`:

```python
        background_tasks.add_task(generate_trio_for_student, student_id)
```

The end of the function body should look like:

```python
    try:
        update_student(
            student_id=student_id,
            metadata=None,
            plan_rules=plan_rules_payload,
            progress=progress_payload,
        )
        save_packet_feedback(student_id, packet_id, mastery_feedback, quantity_feedback)
        background_tasks.add_task(generate_trio_for_student, student_id)  # ← added
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
```

- [ ] **Step 4: Run the tests to confirm they pass**

```bash
venv/bin/python -m pytest tests/test_weekly_automation_integration.py tests/test_feedback_api.py -v
```
Expected: all pass. The existing feedback tests must not regress.

- [ ] **Step 5: Commit**

```bash
git add src/main.py tests/test_weekly_automation_integration.py
git commit -m "feat: trigger trio generation as background task after feedback submission"
```

---

## Task 5: Weekly Reminder Script (`scripts/send_weekly_reminder.py`)

**Files:**
- Create: `scripts/send_weekly_reminder.py`
- Create: `tests/test_send_weekly_reminder.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_send_weekly_reminder.py`:

```python
import json
import sys
from pathlib import Path
from unittest.mock import patch, call

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import send_weekly_reminder


def _make_student(sid: str, name: str) -> dict:
    return {
        "student_id": sid,
        "progress_blob": json.dumps({}),
        "plan_rules_blob": json.dumps({}),
        "metadata_blob": json.dumps({"name": name}),
    }


def test_sends_reminder_listing_student_names():
    students = [_make_student("s1", "Christopher"), _make_student("s2", "Theodore")]

    with patch("send_weekly_reminder.list_students", return_value=students), \
         patch("send_weekly_reminder.notify") as mock_notify:
        send_weekly_reminder.send_reminder()

    mock_notify.assert_called_once()
    message = mock_notify.call_args[0][1]
    assert "Christopher" in message
    assert "Theodore" in message


def test_sends_reminder_with_no_students():
    with patch("send_weekly_reminder.list_students", return_value=[]), \
         patch("send_weekly_reminder.notify") as mock_notify:
        send_weekly_reminder.send_reminder()

    mock_notify.assert_called_once()


def test_does_not_raise_on_ntfy_failure():
    with patch("send_weekly_reminder.list_students", return_value=[]), \
         patch("send_weekly_reminder.notify", side_effect=Exception("network down")):
        # Should not raise — reminder failure is non-fatal
        send_weekly_reminder.send_reminder()
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
venv/bin/python -m pytest tests/test_send_weekly_reminder.py -v
```
Expected: `ModuleNotFoundError: No module named 'send_weekly_reminder'`

- [ ] **Step 3: Write the implementation**

Create `scripts/send_weekly_reminder.py`:

```python
#!/usr/bin/env python3
"""Friday cron script: send NTFY reminder to review weekly lesson feedback."""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db_utils import list_students
from ntfy import notify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_reminder() -> None:
    try:
        students = list_students()
        names = []
        for student in students:
            meta = json.loads(student.get("metadata_blob") or "{}")
            name = meta.get("name", student["student_id"])
            names.append(name)

        if names:
            name_list = ", ".join(names)
            message = f"Time to review this week's lessons for {name_list}. Open the app to submit feedback."
        else:
            message = "Time to review this week's lessons. Open the app to submit feedback."

        notify("Weekly Lesson Review", message)
        logger.info("Weekly reminder sent for students: %s", names)
    except Exception as exc:
        logger.error("send_weekly_reminder failed: %s", exc)


if __name__ == "__main__":
    send_reminder()
```

- [ ] **Step 4: Run the tests to confirm they pass**

```bash
venv/bin/python -m pytest tests/test_send_weekly_reminder.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/send_weekly_reminder.py tests/test_send_weekly_reminder.py
git commit -m "feat: add weekly NTFY reminder script for lesson feedback"
```

---

## Task 6: Safety-Net Script (`scripts/safety_net_generate.py`)

**Files:**
- Create: `scripts/safety_net_generate.py`
- Create: `tests/test_safety_net_generate.py`

The safety net queries SQLite directly for student IDs that have feedback but no weekly packet created after that feedback's `completed_at` timestamp.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_safety_net_generate.py`:

```python
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import safety_net_generate


def _make_db(tmp_path) -> Path:
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute("""
        CREATE TABLE weekly_packets (
            packet_id TEXT PRIMARY KEY,
            student_id TEXT,
            grade_level INTEGER,
            subject TEXT,
            week_of TEXT,
            status TEXT,
            payload_json TEXT,
            summary_json TEXT,
            updated_at TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE packet_feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            packet_id TEXT,
            student_id TEXT,
            mastery_feedback TEXT,
            quantity_feedback INTEGER,
            completed_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    return db


def test_finds_student_with_feedback_but_no_new_plan(tmp_path):
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO packet_feedback VALUES (1, 'pkt1', 's1', NULL, NULL, '2026-06-06T20:00:00Z')"
    )
    # No new packet after the feedback timestamp
    conn.execute(
        "INSERT INTO weekly_packets VALUES ('pkt1', 's1', 2, 'Math', '2026-06-01', 'active', '{}', '{}', '2026-06-01T00:00:00Z', '2026-06-01T00:00:00Z')"
    )
    conn.commit()
    conn.close()

    result = safety_net_generate.find_students_needing_plans(str(db))
    assert result == ["s1"]


def test_skips_student_who_already_has_new_plan(tmp_path):
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO packet_feedback VALUES (1, 'pkt1', 's1', NULL, NULL, '2026-06-06T18:00:00Z')"
    )
    # New packet created AFTER feedback
    conn.execute(
        "INSERT INTO weekly_packets VALUES ('pkt2', 's1', 2, 'Science', '2026-06-09', 'active', '{}', '{}', '2026-06-06T19:00:00Z', '2026-06-06T19:00:00Z')"
    )
    conn.commit()
    conn.close()

    result = safety_net_generate.find_students_needing_plans(str(db))
    assert result == []


def test_runs_trio_for_each_student(tmp_path):
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO packet_feedback VALUES (1, 'pkt1', 's1', NULL, NULL, '2026-06-06T20:00:00Z')"
    )
    conn.execute(
        "INSERT INTO packet_feedback VALUES (2, 'pkt2', 's2', NULL, NULL, '2026-06-06T20:00:00Z')"
    )
    conn.commit()
    conn.close()

    trio_calls = []
    with patch("safety_net_generate.generate_trio_for_student", side_effect=trio_calls.append):
        safety_net_generate.run(str(db))

    assert set(trio_calls) == {"s1", "s2"}
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
venv/bin/python -m pytest tests/test_safety_net_generate.py -v
```
Expected: `ModuleNotFoundError: No module named 'safety_net_generate'`

- [ ] **Step 3: Write the implementation**

Create `scripts/safety_net_generate.py`:

```python
#!/usr/bin/env python3
"""Saturday cron script: generate plans for students who submitted feedback but got no new plans."""

import logging
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trio_generator import generate_trio_for_student

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = str(PROJECT_ROOT / "src" / "curriculum.db")


def find_students_needing_plans(db_path: str) -> list[str]:
    """Return student_ids with feedback but no weekly packet created after that feedback."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("""
            SELECT DISTINCT pf.student_id
            FROM packet_feedback pf
            WHERE NOT EXISTS (
                SELECT 1
                FROM weekly_packets wp
                WHERE wp.student_id = pf.student_id
                  AND wp.created_at > pf.completed_at
            )
        """).fetchall()
        return [row["student_id"] for row in rows]
    finally:
        conn.close()


def run(db_path: str = DEFAULT_DB) -> None:
    students = find_students_needing_plans(db_path)
    logger.info("safety_net: found %d student(s) needing plans", len(students))
    for student_id in students:
        try:
            logger.info("safety_net: generating trio for %s", student_id)
            generate_trio_for_student(student_id)
        except Exception as exc:
            logger.error("safety_net: failed for %s: %s", student_id, exc)


if __name__ == "__main__":
    run()
```

- [ ] **Step 4: Run the tests to confirm they pass**

```bash
venv/bin/python -m pytest tests/test_safety_net_generate.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/safety_net_generate.py tests/test_safety_net_generate.py
git commit -m "feat: add Saturday safety-net script for missed plan generation"
```

---

## Task 7: Crontab Setup (Manual Step)

**Files:** System crontab only — no source file changes.

- [ ] **Step 1: Add the two cron entries**

```bash
(crontab -l 2>/dev/null; cat <<'EOF'
# Weekly curriculum reminder — Friday 7pm
0 19 * * 5 cd /home/clates/agentic-curriculum && venv/bin/python3 scripts/send_weekly_reminder.py >> logs/reminder.log 2>&1
# Safety-net plan generation — Saturday 9am
0 9 * * 6 cd /home/clates/agentic-curriculum && venv/bin/python3 scripts/safety_net_generate.py >> logs/safety_net.log 2>&1
EOF
) | crontab -
```

- [ ] **Step 2: Verify the entries are present**

```bash
crontab -l
```
Expected output includes both lines above (plus any existing entries).

- [ ] **Step 3: Ensure log directory exists**

```bash
mkdir -p /home/clates/agentic-curriculum/logs
```

---

## Task 8: Full Test Suite Pass

- [ ] **Step 1: Run the complete test suite**

```bash
cd /home/clates/agentic-curriculum
venv/bin/python -m pytest tests/ -v --tb=short
```
Expected: all existing tests pass plus the 5 new test files.

- [ ] **Step 2: Commit if any fixups were needed**

```bash
git add -p
git commit -m "fix: test suite cleanup after automation wiring"
```

---

## Self-Review Checklist

**Spec coverage:**
- ✅ `src/ntfy.py` — Task 1
- ✅ `src/subject_picker.py` — Task 2 (heuristic gap analysis, SUBJECTS fallback)
- ✅ `src/trio_generator.py` — Task 3 (parallel, grade_level from last packet, NTFY success + NTFY error at high priority)
- ✅ `src/main.py` BackgroundTask hook — Task 4
- ✅ `scripts/send_weekly_reminder.py` — Task 5
- ✅ `scripts/safety_net_generate.py` — Task 6
- ✅ Crontab entries — Task 7
- ✅ NTFY as error channel — covered in Task 3 (`notify(..., priority="high")` on exception)

**Type consistency:**
- `pick_subjects(student_id: str) -> list[str]` used consistently in trio_generator tests and implementation
- `generate_trio_for_student(student_id: str) -> None` used consistently in main.py and safety_net tests
- `notify(title, message, priority="default")` signature consistent across all callers
- `find_students_needing_plans(db_path: str) -> list[str]` and `run(db_path)` consistent between test and impl

**No placeholders:** Confirmed — all steps have concrete code, exact commands, and expected output.
