"""Utilities for generating tree map worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet, normalize_entries


@dataclass(frozen=True)
class TreeMapSlot:
    """A leaf-level slot in the tree map (optionally pre-filled)."""

    text: str | None = None  # Pre-filled text, or None for blank slot

    @classmethod
    def from_mapping(cls, payload: dict) -> "TreeMapSlot":
        return cls(text=payload.get("text"))


@dataclass(frozen=True)
class TreeMapBranch:
    """A branch in the tree map containing slots."""

    label: str
    slots: List[TreeMapSlot]
    slot_count: int = 3  # Default number of slots if none provided

    @classmethod
    def from_mapping(cls, payload: dict) -> "TreeMapBranch":
        label = payload.get("label")
        if not label:
            raise ValueError("TreeMapBranch requires a label")

        slots_data = payload.get("slots", [])
        slot_count = int(payload.get("slot_count", 3))

        if slots_data:
            slots: List[TreeMapSlot] = []
            for item in slots_data:
                if isinstance(item, TreeMapSlot):
                    slots.append(item)
                elif isinstance(item, dict):
                    slots.append(TreeMapSlot.from_mapping(item))
                elif isinstance(item, str):
                    slots.append(TreeMapSlot(text=item))
                elif item is None:
                    slots.append(TreeMapSlot())
                else:
                    raise TypeError("Slots must be TreeMapSlot, dict, str, or None")
        else:
            # Create empty slots based on slot_count
            slots = [TreeMapSlot() for _ in range(max(1, slot_count))]

        return cls(label=label, slots=slots, slot_count=len(slots))


@dataclass
class TreeMapWorksheet(BaseWorksheet):
    """Worksheet with hierarchical tree structure for classification."""

    title: str
    instructions: str
    root_label: str
    branches: List[TreeMapBranch]
    word_bank: List[str]  # Optional words to fill in slots
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the tree map worksheet."""
        lines = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
            f"## {self.root_label}",
            "",
        ]

        for branch in self.branches:
            lines.append(f"### {branch.label}")
            for idx, slot in enumerate(branch.slots, start=1):
                if slot.text:
                    lines.append(f"  {idx}. {slot.text}")
                else:
                    lines.append(f"  {idx}. ____________")
            lines.append("")

        if self.word_bank:
            lines.extend(["## Word Bank", "", ", ".join(self.word_bank)])

        return "\n".join(lines)


def generate_tree_map_worksheet(
    *,
    root_label: str,
    branches: Sequence[TreeMapBranch | dict],
    word_bank: Sequence[str] | None = None,
    title: str = "Tree Map",
    instructions: str = "Fill in the tree map by writing words from the word bank in the correct category.",
    metadata: dict | None = None,
) -> TreeMapWorksheet:
    """Create a tree map worksheet with hierarchical structure."""
    if not root_label.strip():
        raise ValueError("Root label is required")

    normalized_branches = normalize_entries(
        branches, TreeMapBranch, "Branches must be TreeMapBranch or dict entries"
    )
    if not normalized_branches:
        raise ValueError("At least one branch is required")

    return TreeMapWorksheet(
        title=title,
        instructions=instructions,
        root_label=root_label.strip(),
        branches=normalized_branches,
        word_bank=list(word_bank or []),
        metadata=metadata or {},
    )


__all__ = [
    "TreeMapSlot",
    "TreeMapBranch",
    "TreeMapWorksheet",
    "generate_tree_map_worksheet",
]
