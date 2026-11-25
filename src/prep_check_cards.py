"""Parent-facing view of a week's prep checks for the Friday check-by-check form (M10.5b).

Reads the stored week (M2.6), swaps in the child's first name, and returns only what a parent
needs: an id to report back on, the day, what to ask or do, and what a good answer sounds like.
Standard ids stay on the server.
"""

from __future__ import annotations

import os
import sys

try:  # Prefer package-relative import when available
    from . import week_store  # type: ignore
    from .weekdoc.render import substitute_name  # type: ignore
except ImportError:  # Fallback for direct script execution
    sys.path.insert(0, os.path.dirname(__file__))
    import week_store  # type: ignore
    from weekdoc.render import substitute_name  # type: ignore


def check_cards(
    student_id: str,
    packet_id: str,
    first_name: str | None,
    family_id: str = week_store.DEFAULT_FAMILY,
) -> list[dict]:
    """The packet's checks in document order; empty for a week with no structured checks."""
    week = week_store.get_week(student_id, packet_id, family_id=family_id)
    if week is None:
        return []
    return [
        {
            "check_id": c.id,
            "day": c.day,
            "prompt": substitute_name(c.prompt, first_name),
            "pass_criteria": substitute_name(c.pass_criteria, first_name),
        }
        for c in week.prep_checks
    ]
