"""Utilities for generating labeled-diagram worksheet data structures."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class DiagramLabel:
    """A label/answer for one part of the diagram."""

    number: int  # callout number shown on diagram
    answer: str  # the correct label text
    hint: str | None = None  # optional hint shown in word bank

    @classmethod
    def from_mapping(cls, payload: dict) -> "DiagramLabel":
        number = payload.get("number")
        if number is None:
            raise ValueError("DiagramLabel requires a number")
        answer = payload.get("answer")
        if not answer:
            raise ValueError("DiagramLabel requires an answer")
        hint = payload.get("hint")
        return cls(number=int(number), answer=str(answer), hint=hint)


@dataclass
class LabeledDiagramWorksheet(BaseWorksheet):
    """Worksheet where students label parts of a diagram."""

    title: str
    instructions: str
    image_path: str | None  # path to diagram image, or None for placeholder box
    labels: List[DiagramLabel]
    show_answers: bool
    word_bank: bool  # whether to show a scrambled word bank
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the labeled diagram worksheet."""
        lines = [f"# {self.title}", "", self.instructions, ""]
        if self.image_path:
            lines.append(f"![Diagram]({self.image_path})")
        else:
            lines.append("[Diagram placeholder]")
        lines.append("")
        if self.word_bank:
            words = [lbl.answer for lbl in self.labels]
            shuffled = words[:]
            random.shuffle(shuffled)
            lines.append("**Word Bank:** " + "   ".join(shuffled))
            lines.append("")
        for lbl in self.labels:
            if self.show_answers:
                lines.append(f"{lbl.number}. {lbl.answer}")
            else:
                lines.append(f"{lbl.number}. {'_' * 20}")
        return "\n".join(lines)


def _normalize_labels(labels: Sequence[DiagramLabel | dict]) -> List[DiagramLabel]:
    """Convert labels to DiagramLabel objects."""
    normalized: List[DiagramLabel] = []
    for item in labels:
        if isinstance(item, DiagramLabel):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(DiagramLabel.from_mapping(item))
        else:
            raise TypeError("Labels must be DiagramLabel or dict entries")
    return normalized


def generate_labeled_diagram_worksheet(
    *,
    title: str = "Labeled Diagram",
    instructions: str = "Label each part of the diagram.",
    image_path: str | None = None,
    labels: Sequence[DiagramLabel | dict],
    show_answers: bool = False,
    word_bank: bool = True,
    metadata: dict | None = None,
) -> LabeledDiagramWorksheet:
    """Create a labeled diagram worksheet.

    Args:
        title: Worksheet title.
        instructions: Instructions for students.
        image_path: Path to diagram image file, or None for a placeholder box.
        labels: List of DiagramLabel objects or dicts with number/answer/hint keys.
        show_answers: If True, show the correct answers instead of blank lines.
        word_bank: If True, display a shuffled word bank of the answers.
        metadata: Optional metadata dictionary.

    Returns:
        LabeledDiagramWorksheet instance.

    Raises:
        ValueError: If no labels are provided.
    """
    normalized_labels = _normalize_labels(labels)
    if not normalized_labels:
        raise ValueError("At least one label is required")

    return LabeledDiagramWorksheet(
        title=title,
        instructions=instructions,
        image_path=image_path,
        labels=normalized_labels,
        show_answers=show_answers,
        word_bank=word_bank,
        metadata=metadata or {},
    )


__all__ = [
    "DiagramLabel",
    "LabeledDiagramWorksheet",
    "generate_labeled_diagram_worksheet",
]
