"""Utilities for generating word sort worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class WordSortTile:
    """A single word tile to be sorted into a category."""

    text: str
    category: str  # which box it belongs to (for show_answers and answer key)

    @classmethod
    def from_mapping(cls, payload: str | dict) -> "WordSortTile":
        if isinstance(payload, str):
            raise ValueError("WordSortTile requires both 'text' and 'category' keys")
        text = payload.get("text")
        category = payload.get("category")
        if not text:
            raise ValueError("WordSortTile requires 'text'")
        if not category:
            raise ValueError("WordSortTile requires 'category'")
        return cls(text=text, category=category)


@dataclass
class WordSortWorksheet(BaseWorksheet):
    """Worksheet where students cut out word tiles and sort them into category boxes."""

    title: str
    instructions: str
    categories: List[str]  # 2–4 category box labels
    tiles: List[WordSortTile]  # words to sort
    show_answers: bool  # True = render tiles inside correct category boxes
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the word sort worksheet."""
        lines = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
        ]

        for category in self.categories:
            lines.append(f"## {category}")
            if self.show_answers:
                cat_tiles = [t for t in self.tiles if t.category == category]
                for tile in cat_tiles:
                    lines.append(f"- {tile.text}")
            else:
                lines.append("____________")
                lines.append("____________")
                lines.append("____________")
            lines.append("")

        lines.append("## Cut-Out Tiles")
        lines.append("")
        for tile in self.tiles:
            lines.append(f"[ {tile.text} ]")

        return "\n".join(lines)


def _normalize_tiles(tiles: Sequence[WordSortTile | dict]) -> List[WordSortTile]:
    """Convert tiles to WordSortTile objects."""
    normalized: List[WordSortTile] = []
    for item in tiles:
        if isinstance(item, WordSortTile):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(WordSortTile.from_mapping(item))
        else:
            raise TypeError("Tiles must be WordSortTile or dict entries")
    return normalized


def generate_word_sort_worksheet(
    *,
    categories: Sequence[str],
    tiles: Sequence[WordSortTile | dict],
    title: str = "Word Sort",
    instructions: str = "Cut out the word tiles below. Sort them into the correct category boxes.",
    show_answers: bool = False,
    metadata: dict | None = None,
) -> WordSortWorksheet:
    """Create a word sort worksheet with category boxes and cut-out tiles.

    Args:
        categories: List of 2–4 category box labels.
        tiles: List of word tiles (each with text and category).
        title: Worksheet title.
        instructions: Instructions for students.
        show_answers: If True, tiles are rendered inside their correct boxes.
        metadata: Optional metadata dictionary.

    Returns:
        WordSortWorksheet instance.

    Raises:
        ValueError: If categories count is not 2–4, fewer than 2 tiles, or tile
                    categories don't match the listed categories.
    """
    categories_list = list(categories)
    if len(categories_list) < 2 or len(categories_list) > 4:
        raise ValueError("WordSortWorksheet requires 2–4 categories")

    normalized_tiles = _normalize_tiles(tiles)
    if len(normalized_tiles) < 2:
        raise ValueError("At least 2 tiles are required")

    category_set = set(categories_list)
    for tile in normalized_tiles:
        if tile.category not in category_set:
            raise ValueError(
                f"Tile '{tile.text}' has category '{tile.category}' which is not in "
                f"the listed categories: {categories_list}"
            )

    return WordSortWorksheet(
        title=title,
        instructions=instructions,
        categories=categories_list,
        tiles=normalized_tiles,
        show_answers=show_answers,
        metadata=metadata or {},
    )


__all__ = [
    "WordSortTile",
    "WordSortWorksheet",
    "generate_word_sort_worksheet",
]
