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
        rows = conn.execute(
            """
            SELECT DISTINCT pf.student_id
            FROM packet_feedback pf
            WHERE NOT EXISTS (
                SELECT 1
                FROM weekly_packets wp
                WHERE wp.student_id = pf.student_id
                  AND wp.created_at > pf.completed_at
            )
        """
        ).fetchall()
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
