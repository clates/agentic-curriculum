"""Utilities for generating handwriting worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class HandwritingItem:
    """An item to practice writing (image + label)."""

    text: str
    image_path: str | None = None
    sub_label: str | None = None

    @classmethod
    def from_mapping(cls, payload: dict) -> "HandwritingItem":
        text = payload.get("text")
        if not text:
            raise ValueError("HandwritingItem requires text")
        image_path = payload.get("image_path")
        sub_label = payload.get("sub_label")
        return cls(text=text, image_path=image_path, sub_label=sub_label)


@dataclass
class HandwritingWorksheet(BaseWorksheet):
    """Worksheet for handwriting practice with images and dotted lines."""

    title: str
    instructions: str
    items: List[HandwritingItem]
    rows: int = 4
    cols: int = 2
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the handwriting worksheet."""
        lines = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
        ]

        for item in self.items:
            lines.append(f"## {item.text}")
            if item.sub_label:
                lines.append(f"({item.sub_label})")
            lines.append("Trace the word: " + " . ".join(list(item.text)))
            lines.append("Write the word: " + "_" * 20)
            lines.append("")

        return "\n".join(lines)


def _normalize_items(items: Sequence[HandwritingItem | dict]) -> List[HandwritingItem]:
    """Convert items to HandwritingItem objects."""
    normalized: List[HandwritingItem] = []
    for item in items:
        if isinstance(item, HandwritingItem):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(HandwritingItem.from_mapping(item))
        else:
            raise TypeError("Items must be HandwritingItem or dict entries")
    return normalized


def generate_handwriting_worksheet(
    *,
    items: Sequence[HandwritingItem | dict],
    title: str = "Handwriting Practice",
    instructions: str = "Look at the picture and practice writing the word on the lines.",
    rows: int = 4,
    cols: int = 2,
    metadata: dict | None = None,
) -> HandwritingWorksheet:
    """Create a handwriting worksheet.

    Args:
        items: List of items to practice.
        title: Worksheet title.
        instructions: Instructions for students.
        rows: Suggested number of rows for layout.
        cols: Suggested number of columns for layout.
        metadata: Optional metadata dictionary.

    Returns:
        HandwritingWorksheet instance.
    """
    normalized_items = _normalize_items(items)
    if not normalized_items:
        raise ValueError("At least one item is required")

    return HandwritingWorksheet(
        title=title,
        instructions=instructions,
        items=normalized_items,
        rows=rows,
        cols=cols,
        metadata=metadata or {},
    )


__all__ = [
    "HandwritingItem",
    "HandwritingWorksheet",
    "generate_handwriting_worksheet",
]
