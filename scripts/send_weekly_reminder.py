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
