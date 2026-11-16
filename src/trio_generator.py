import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(__file__))

from agent import generate_weekly_plan
from db_utils import get_student_profile
from ntfy import notify
from packet_store import list_weekly_packets
from subject_picker import pick_subjects

logger = logging.getLogger(__name__)


def _get_grade_level(student_id: str, metadata_fallback: dict | None = None) -> int:
    """Return grade_level from the student's most recent weekly packet.

    Falls back to metadata_fallback["grade_level"] if no packets exist, then to 0.
    """
    packets, _ = list_weekly_packets(student_id, limit=1, offset=0)
    if packets:
        return packets[0].get("grade_level", 0)
    if metadata_fallback is not None:
        return int(metadata_fallback.get("grade_level", 0))
    return 0


def generate_trio_for_student(student_id: str) -> None:
    """Generate 3 lesson plans for a student and push NTFY on completion or failure."""
    profile = get_student_profile(student_id)
    metadata = json.loads(profile.get("metadata_blob") or "{}") if profile else {}
    name = metadata.get("name", student_id)

    try:
        grade_level = _get_grade_level(student_id, metadata_fallback=metadata)
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

        notify(f"Plans ready for {name}!", "Math, Reading & more packets are in the queue.")
    except Exception as exc:
        logger.error("trio_generator: failed for %s: %s", student_id, exc)
        notify(f"Plan generation FAILED for {name}", str(exc), priority="high")
        raise
