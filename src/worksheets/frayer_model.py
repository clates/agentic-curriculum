"""Utilities for generating Frayer Model / Concept Definition Map worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class FrayerModelEntry:
    """One Frayer Model vocabulary concept."""

    concept: str  # the word/concept in the center
    definition: str | None = None  # student fills in if None
    characteristics: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    non_examples: List[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, payload: dict) -> "FrayerModelEntry":
        concept = payload.get("concept", "")
        if not concept:
            raise ValueError("FrayerModelEntry requires a concept")
        return cls(
            concept=str(concept),
            definition=payload.get("definition"),
            characteristics=list(payload.get("characteristics", [])),
            examples=list(payload.get("examples", [])),
            non_examples=list(payload.get("non_examples", [])),
        )


@dataclass
class FrayerModelWorksheet(BaseWorksheet):
    """Classic 4-quadrant vocabulary graphic organizer."""

    title: str
    instructions: str
    entries: List[FrayerModelEntry]
    show_answers: bool
    quadrant_labels: List[str] = field(
        default_factory=lambda: ["Definition", "Characteristics", "Examples", "Non-Examples"]
    )
    metadata: dict | None = None

    def to_markdown(self) -> str:
        ql = self.quadrant_labels
        lines = [f"# {self.title}", "", self.instructions, ""]
        for entry in self.entries:
            lines.append(f"## Concept: {entry.concept}")
            lines.append(
                f"**{ql[0]}:** "
                + (entry.definition if self.show_answers and entry.definition else "_" * 40)
            )
            chars = ", ".join(entry.characteristics) if entry.characteristics else "_" * 40
            lines.append(
                f"**{ql[1]}:** "
                + (chars if self.show_answers and entry.characteristics else "_" * 40)
            )
            exs = ", ".join(entry.examples) if entry.examples else "_" * 40
            lines.append(
                f"**{ql[2]}:** " + (exs if self.show_answers and entry.examples else "_" * 40)
            )
            non_exs = ", ".join(entry.non_examples) if entry.non_examples else "_" * 40
            lines.append(
                f"**{ql[3]}:** "
                + (non_exs if self.show_answers and entry.non_examples else "_" * 40)
            )
            lines.append("")
        return "\n".join(lines)


def _normalize_entries(
    entries: Sequence[FrayerModelEntry | dict],
) -> List[FrayerModelEntry]:
    normalized: List[FrayerModelEntry] = []
    for item in entries:
        if isinstance(item, FrayerModelEntry):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(FrayerModelEntry.from_mapping(item))
        else:
            raise TypeError("Entries must be FrayerModelEntry or dict entries")
    return normalized


def generate_frayer_model_worksheet(
    *,
    entries: Sequence[FrayerModelEntry | dict],
    title: str = "Frayer Model",
    instructions: str = "Fill in each section to show what you know about the word.",
    show_answers: bool = False,
    quadrant_labels: List[str] | None = None,
    metadata: dict | None = None,
) -> FrayerModelWorksheet:
    """Create a Frayer Model vocabulary organizer worksheet.

    Args:
        entries: List of concept entries (FrayerModelEntry or dict).
        title: Worksheet title.
        instructions: Instructions for students.
        show_answers: Whether to render pre-filled answers.
        quadrant_labels: Override for the 4 quadrant labels (default:
            ["Definition", "Characteristics", "Examples", "Non-Examples"]).
        metadata: Optional metadata dictionary.

    Returns:
        FrayerModelWorksheet instance.

    Raises:
        ValueError: If no entries provided or quadrant_labels wrong length.
    """
    normalized = _normalize_entries(entries)
    if not normalized:
        raise ValueError("At least one entry is required")
    labels = quadrant_labels or ["Definition", "Characteristics", "Examples", "Non-Examples"]
    if len(labels) != 4:
        raise ValueError(f"quadrant_labels must have exactly 4 entries, got {len(labels)}")
    return FrayerModelWorksheet(
        title=title,
        instructions=instructions,
        entries=normalized,
        show_answers=show_answers,
        quadrant_labels=labels,
        metadata=metadata or {},
    )


__all__ = [
    "FrayerModelEntry",
    "FrayerModelWorksheet",
    "generate_frayer_model_worksheet",
]
