"""Utilities for generating feature matrix worksheet data structures."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class FeatureMatrixItem:
    """A row in the feature matrix (an item to classify)."""

    name: str
    checked_properties: List[str] | None = None  # Properties that are pre-checked (for answer key)

    @classmethod
    def from_mapping(cls, payload: dict) -> "FeatureMatrixItem":
        name = payload.get("name")
        if not name:
            raise ValueError("FeatureMatrixItem requires a name field")
        checked = payload.get("checked_properties")
        if checked is not None and not isinstance(checked, list):
            checked = [checked] if isinstance(checked, str) else list(checked)
        return cls(name=name, checked_properties=checked)


@dataclass
class FeatureMatrixWorksheet(BaseWorksheet):
    """Worksheet with a grid for classification activities."""

    title: str
    instructions: str
    items: List[FeatureMatrixItem]  # Rows
    properties: List[str]  # Columns
    show_answers: bool
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the feature matrix worksheet."""
        lines = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
        ]

        # Build table header
        header = "| Item | " + " | ".join(self.properties) + " |"
        separator = "|------|" + "|".join(["------"] * len(self.properties)) + "|"
        lines.extend([header, separator])

        # Build table rows
        for item in self.items:
            cells = [item.name]
            for prop in self.properties:
                if self.show_answers and item.checked_properties:
                    cells.append("✓" if prop in item.checked_properties else " ")
                else:
                    cells.append("☐")
            lines.append("| " + " | ".join(cells) + " |")

        return "\n".join(lines)


def _normalize_items(items: Sequence[FeatureMatrixItem | dict | str]) -> List[FeatureMatrixItem]:
    """Convert items to FeatureMatrixItem objects."""
    normalized: List[FeatureMatrixItem] = []
    for item in items:
        if isinstance(item, FeatureMatrixItem):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(FeatureMatrixItem.from_mapping(item))
        elif isinstance(item, str):
            normalized.append(FeatureMatrixItem(name=item))
        else:
            raise TypeError("Items must be FeatureMatrixItem, dict, or str")
    return normalized


def generate_feature_matrix_worksheet(
    *,
    items: Sequence[FeatureMatrixItem | dict | str],
    properties: Sequence[str],
    title: str = "Feature Matrix",
    instructions: str = "Check the boxes that apply to each item.",
    show_answers: bool = False,
    metadata: dict | None = None,
) -> FeatureMatrixWorksheet:
    """Create a feature matrix worksheet with items as rows and properties as columns.

    Args:
        items: List of items to classify (rows). Can be strings, dicts, or FeatureMatrixItem.
        properties: List of property names (columns).
        title: Worksheet title.
        instructions: Instructions for students.
        show_answers: Whether to show pre-checked answers (for answer key).
        metadata: Optional metadata dictionary.

    Returns:
        FeatureMatrixWorksheet instance.

    Raises:
        ValueError: If no items or properties provided.
    """
    normalized_items = _normalize_items(items)
    if not normalized_items:
        raise ValueError("At least one item is required")

    property_list = [p.strip() for p in properties if p.strip()]
    if not property_list:
        raise ValueError("At least one property is required")

    return FeatureMatrixWorksheet(
        title=title,
        instructions=instructions,
        items=normalized_items,
        properties=property_list,
        show_answers=show_answers,
        metadata=metadata or {},
    )


__all__ = [
    "FeatureMatrixItem",
    "FeatureMatrixWorksheet",
    "generate_feature_matrix_worksheet",
]
