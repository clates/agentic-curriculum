"""Utilities for generating Venn diagram worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet, normalize_entries


@dataclass(frozen=True)
class VennDiagramEntry:
    """A word or phrase to be sorted into the Venn diagram."""

    text: str
    category: str | None = None  # Optional hint: "left", "right", "both", or None for unsorted

    @classmethod
    def from_mapping(cls, payload: dict) -> "VennDiagramEntry":
        text = payload.get("text")
        if not text:
            raise ValueError("VennDiagramEntry requires a text field")
        return cls(text=text, category=payload.get("category"))


@dataclass
class VennDiagramWorksheet(BaseWorksheet):
    """Worksheet with two overlapping circles for classification activities."""

    title: str
    instructions: str
    left_label: str
    right_label: str
    both_label: str
    word_bank: List[VennDiagramEntry]
    left_items: List[str]  # Pre-filled items in left circle
    right_items: List[str]  # Pre-filled items in right circle
    both_items: List[str]  # Pre-filled items in overlap
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the Venn diagram worksheet."""
        lines = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
            f"## Diagram: {self.left_label} | {self.both_label} | {self.right_label}",
            "",
        ]

        # Show pre-filled items
        if self.left_items:
            lines.append(f"**{self.left_label} only:** {', '.join(self.left_items)}")
        if self.both_items:
            lines.append(f"**{self.both_label}:** {', '.join(self.both_items)}")
        if self.right_items:
            lines.append(f"**{self.right_label} only:** {', '.join(self.right_items)}")

        # Word bank section
        if self.word_bank:
            lines.extend(["", "## Word Bank", ""])
            words = [entry.text for entry in self.word_bank]
            lines.append(", ".join(words))

        return "\n".join(lines)


def generate_venn_diagram_worksheet(
    *,
    left_label: str,
    right_label: str,
    word_bank: Sequence[VennDiagramEntry | dict | str] | None = None,
    both_label: str = "Both",
    left_items: Sequence[str] | None = None,
    right_items: Sequence[str] | None = None,
    both_items: Sequence[str] | None = None,
    title: str = "Venn Diagram",
    instructions: str = "Sort the words from the word bank into the correct section of the Venn diagram.",
    metadata: dict | None = None,
) -> VennDiagramWorksheet:
    """Create a Venn diagram worksheet with two overlapping circles."""
    if not left_label.strip():
        raise ValueError("Left label is required")
    if not right_label.strip():
        raise ValueError("Right label is required")

    normalized_bank = normalize_entries(
        word_bank or [],
        VennDiagramEntry,
        "Word bank entries must be VennDiagramEntry, dict, or str",
        lambda text: VennDiagramEntry(text=text),
    )

    return VennDiagramWorksheet(
        title=title,
        instructions=instructions,
        left_label=left_label.strip(),
        right_label=right_label.strip(),
        both_label=both_label.strip() or "Both",
        word_bank=normalized_bank,
        left_items=list(left_items or []),
        right_items=list(right_items or []),
        both_items=list(both_items or []),
        metadata=metadata or {},
    )


__all__ = [
    "VennDiagramEntry",
    "VennDiagramWorksheet",
    "generate_venn_diagram_worksheet",
]
