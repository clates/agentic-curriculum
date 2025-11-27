"""Utilities for generating odd-one-out worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class OddOneOutRow:
    """A row of items with one odd item and optional explanation."""

    items: List[str]
    odd_item: str | None = None  # The correct answer (for answer key)
    explanation: str | None = None  # Why this item is the odd one

    @classmethod
    def from_mapping(cls, payload: dict) -> "OddOneOutRow":
        items = payload.get("items")
        if not items:
            raise ValueError("OddOneOutRow requires an items list")
        if not isinstance(items, list) or len(items) < 3:
            raise ValueError("OddOneOutRow requires at least 3 items")
        odd_item = payload.get("odd_item")
        explanation = payload.get("explanation")
        return cls(items=list(items), odd_item=odd_item, explanation=explanation)


@dataclass
class OddOneOutWorksheet(BaseWorksheet):
    """Worksheet with rows of items where students identify the odd one."""

    title: str
    instructions: str
    rows: List[OddOneOutRow]
    show_answers: bool
    reasoning_lines: int  # Number of lines for student reasoning
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the odd-one-out worksheet."""
        lines = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
        ]

        for idx, row in enumerate(self.rows, start=1):
            items_str = "   ".join(row.items)
            lines.append(f"{idx}. {items_str}")

            if self.show_answers and row.odd_item:
                lines.append(f"   **Answer:** {row.odd_item}")
                if row.explanation:
                    lines.append(f"   **Reason:** {row.explanation}")
            else:
                lines.append("   Circle the odd one out.")
                lines.append(f"   Why? {'_' * 40}")
                for _ in range(self.reasoning_lines - 1):
                    lines.append(f"   {'_' * 50}")

            lines.append("")

        return "\n".join(lines)


def _normalize_rows(rows: Sequence[OddOneOutRow | dict]) -> List[OddOneOutRow]:
    """Convert rows to OddOneOutRow objects."""
    normalized: List[OddOneOutRow] = []
    for item in rows:
        if isinstance(item, OddOneOutRow):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(OddOneOutRow.from_mapping(item))
        else:
            raise TypeError("Rows must be OddOneOutRow or dict entries")
    return normalized


def generate_odd_one_out_worksheet(
    *,
    rows: Sequence[OddOneOutRow | dict],
    title: str = "Odd One Out",
    instructions: str = "Look at each row. Circle the item that does not belong and explain why.",
    show_answers: bool = False,
    reasoning_lines: int = 2,
    metadata: dict | None = None,
) -> OddOneOutWorksheet:
    """Create an odd-one-out worksheet.

    Args:
        rows: List of rows, each containing items to compare.
        title: Worksheet title.
        instructions: Instructions for students.
        show_answers: Whether to show correct answers (for answer key).
        reasoning_lines: Number of blank lines for student reasoning (min 1).
        metadata: Optional metadata dictionary.

    Returns:
        OddOneOutWorksheet instance.

    Raises:
        ValueError: If no rows provided or rows have insufficient items.
    """
    normalized_rows = _normalize_rows(rows)
    if not normalized_rows:
        raise ValueError("At least one row is required")

    return OddOneOutWorksheet(
        title=title,
        instructions=instructions,
        rows=normalized_rows,
        show_answers=show_answers,
        reasoning_lines=max(1, reasoning_lines),
        metadata=metadata or {},
    )


__all__ = [
    "OddOneOutRow",
    "OddOneOutWorksheet",
    "generate_odd_one_out_worksheet",
]
