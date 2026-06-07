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
