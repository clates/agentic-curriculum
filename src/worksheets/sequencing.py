"""Utilities for generating sequencing (cut-and-order) worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class SequencingStep:
    """A single step in a sequencing activity."""

    text: str
    image_path: str | None = None
    # correct_order is the 1-based position this step should occupy (used in answer key)
    correct_order: int | None = None

    @classmethod
    def from_mapping(cls, payload: str | dict) -> "SequencingStep":
        if isinstance(payload, str):
            return cls(text=payload)
        return cls(
            text=payload.get("text", ""),
            image_path=payload.get("image_path"),
            correct_order=payload.get("correct_order"),
        )


@dataclass
class SequencingWorksheet(BaseWorksheet):
    """A cut-out sequencing worksheet where steps are shown out of order.

    Students cut out each step card and paste them back in the correct order.
    """

    title: str
    instructions: str
    activity_name: str  # e.g. "Making a Bowl of Cereal"
    steps: List[SequencingStep]  # Steps in shuffled (display) order
    show_answers: bool = False
    metadata: dict | None = None

    def to_markdown(self) -> str:
        lines = [
            f"# {self.title}",
            "",
            f"**Activity:** {self.activity_name}",
            "",
            self.instructions,
            "",
            "## Steps (cut out and put in order!)",
            "",
        ]
        for _idx, step in enumerate(self.steps, start=1):
            answer_hint = ""
            if self.show_answers and step.correct_order is not None:
                answer_hint = f"  *(correct position: {step.correct_order})*"
            lines.append(f"- {step.text}{answer_hint}")
        return "\n".join(lines)


def _normalize_steps(steps: Sequence[SequencingStep | dict | str]) -> List[SequencingStep]:
    normalized: List[SequencingStep] = []
    for item in steps:
        if isinstance(item, SequencingStep):
            normalized.append(item)
        elif isinstance(item, (dict, str)):
            normalized.append(SequencingStep.from_mapping(item))
        else:
            raise TypeError("Steps must be SequencingStep, dict, or str entries")
    return normalized


def generate_sequencing_worksheet(
    *,
    activity_name: str,
    steps: Sequence[SequencingStep | dict | str],
    title: str = "Put It in Order!",
    instructions: str = (
        "Cut out each step below. Paste them in the correct order on another sheet of paper."
    ),
    show_answers: bool = False,
    metadata: dict | None = None,
) -> SequencingWorksheet:
    """Create a cut-and-sequence worksheet.

    Args:
        activity_name: The name of the activity (e.g. "Brushing Teeth").
        steps: List of steps in the order they should be displayed (shuffled).
               Each step should have a ``correct_order`` field for answer key support.
        title: Worksheet title.
        instructions: Instructions for students.
        show_answers: Whether to show correct order numbers (answer key mode).
        metadata: Optional metadata dictionary.

    Returns:
        SequencingWorksheet instance.
    """
    normalized = _normalize_steps(steps)
    if len(normalized) < 2:
        raise ValueError("At least 2 steps are required for a sequencing worksheet")

    return SequencingWorksheet(
        title=title,
        instructions=instructions,
        activity_name=activity_name,
        steps=normalized,
        show_answers=show_answers,
        metadata=metadata or {},
    )


__all__ = [
    "SequencingStep",
    "SequencingWorksheet",
    "generate_sequencing_worksheet",
]
