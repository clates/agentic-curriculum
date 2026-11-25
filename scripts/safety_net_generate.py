#!/usr/bin/env python3
"""Saturday cron script: generate plans for students who submitted feedback but got no new plans."""

import logging
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db_utils import get_db_path
from trio_generator import generate_trio_for_student

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def find_students_needing_plans(db_path: str) -> list[tuple[str, str]]:
    """Return (family_id, student_id) pairs with feedback but no weekly packet in that family
    created after that feedback."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("""
            -- A row in packet_feedback is equivalent to has_feedback=true in the API layer
            -- (has_feedback is a computed field derived from the existence of a packet_feedback row)
            SELECT DISTINCT pf.family_id, pf.student_id
            FROM packet_feedback pf
            WHERE NOT EXISTS (
                SELECT 1
                FROM weekly_packets wp
                WHERE wp.student_id = pf.student_id
                  AND wp.family_id = pf.family_id
                  AND wp.created_at > pf.completed_at
            )
        """).fetchall()
        return [(row["family_id"], row["student_id"]) for row in rows]
    finally:
        conn.close()


def run(db_path: str | None = None) -> None:
    students = find_students_needing_plans(db_path or get_db_path())
    logger.info("safety_net: found %d student(s) needing plans", len(students))
    for family_id, student_id in students:
        try:
            logger.info("safety_net: generating trio for %s", student_id)
            generate_trio_for_student(student_id, family_id)
        except Exception as exc:
            logger.error("safety_net: failed for %s: %s", student_id, exc)


if __name__ == "__main__":
    run()
