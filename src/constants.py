"""Constants for the agentic-curriculum system.

Provides centralized definitions for subjects, grade levels, worksheet types,
and evaluation statuses used throughout the application.
"""

from __future__ import annotations

from worksheets.factory import WorksheetFactory

# Subjects available in the curriculum
# NOTE: These must match the subjects in the standards database
SUBJECTS: list[str] = [
    "Computer Science",
    "English",
    "History",
    "Math",
    "Science",
]

# Grade levels mapped from integer to human-readable label
GRADE_LEVELS: dict[int, str] = {
    0: "Kindergarten",
    1: "1st Grade",
    2: "2nd Grade",
    3: "3rd Grade",
    4: "4th Grade",
    5: "5th Grade",
    6: "6th Grade",
    7: "7th Grade",
    8: "8th Grade",
    9: "9th Grade",
    10: "10th Grade",
    11: "11th Grade",
    12: "12th Grade",
}

# Evaluation statuses for student progress
EVALUATION_STATUSES: list[str] = [
    "NOT_STARTED",
    "DEVELOPING",
    "MASTERED",
    "BENCHED",
]


def get_worksheet_types() -> list[str]:
    """Return the list of supported worksheet types from the factory registry.

    This function dynamically retrieves the types from WorksheetFactory
    to ensure consistency with the actual implementation.
    """
    return WorksheetFactory.get_supported_types()


__all__ = [
    "SUBJECTS",
    "GRADE_LEVELS",
    "EVALUATION_STATUSES",
    "get_worksheet_types",
]
