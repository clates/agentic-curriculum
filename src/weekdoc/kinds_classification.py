"""Classification and grid kinds: word sort, tree map, T-chart, feature matrix, matching (M2.2c).

Cross-field validators catch the mistakes that otherwise print a broken page: a word bank that
does not match the blanks, mismatched matching columns, duplicate tiles.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, model_validator

from .kinds import ItemRef, KindData, register
from .kinds_comprehension import Text


def _unique(values: list[str], what: str) -> None:
    folded = [v.strip().casefold() for v in values]
    if len(set(folded)) != len(folded):
        raise ValueError(f"{what} must be unique")


# ── wordSortWorksheet ───────────────────────────────────────────────────────


class SortCategory(KindData):
    label: Text


class WordSortData(KindData):
    title: Text
    instructions: str | None = None
    categories: Annotated[list[SortCategory | Text], Field(min_length=2, max_length=4)]
    tiles: Annotated[list[Text], Field(min_length=2)]
    columns: Annotated[int, Field(ge=1, le=4)] | None = None

    @model_validator(mode="after")
    def _checks(self) -> "WordSortData":
        _unique(self.tiles, "tiles")
        _unique([c if isinstance(c, str) else c.label for c in self.categories], "categories")
        if len(self.tiles) < len(self.categories):
            raise ValueError("need at least one tile per category")
        return self


def _word_sort_items(d: WordSortData) -> list[ItemRef]:
    return [ItemRef(f"tiles.{i}", t) for i, t in enumerate(d.tiles)]


register("wordSortWorksheet", WordSortData, _word_sort_items)


# ── treeMapWorksheet ────────────────────────────────────────────────────────


class TreeBranch(KindData):
    # The renderer accepts name|label and blank_count|slot_count; exactly one of each pair.
    name: Text | None = None
    label: Text | None = None
    prefilled: list[Text] = Field(default_factory=list)
    blank_count: Annotated[int, Field(ge=0, le=12)] | None = None
    slot_count: Annotated[int, Field(ge=0, le=12)] | None = None

    @model_validator(mode="after")
    def _shape(self) -> "TreeBranch":
        if (self.name is None) == (self.label is None):
            raise ValueError("branch needs exactly one of name or label")
        if self.blank_count is not None and self.slot_count is not None:
            raise ValueError("give blank_count or slot_count, not both")
        if self.blanks + len(self.prefilled) < 1:
            raise ValueError("branch has no slots")
        return self

    @property
    def title(self) -> str:
        return self.name or self.label or ""

    @property
    def blanks(self) -> int:
        # renderer default is one blank when neither count is given
        for v in (self.blank_count, self.slot_count):
            if v is not None:
                return v
        return 1


class TreeMapData(KindData):
    title: Text
    instructions: str | None = None
    root_label: Text
    branches: Annotated[list[TreeBranch], Field(min_length=2, max_length=6)]
    columns: Annotated[int, Field(ge=1, le=6)] | None = None
    word_bank: list[Text] = Field(default_factory=list)

    @model_validator(mode="after")
    def _checks(self) -> "TreeMapData":
        _unique([b.title for b in self.branches], "branch names")
        if self.word_bank:
            _unique(self.word_bank, "word_bank")
            blanks = sum(b.blanks for b in self.branches)
            if len(self.word_bank) != blanks:
                raise ValueError(
                    f"word_bank has {len(self.word_bank)} words but branches have {blanks} blanks"
                )
        return self


def _tree_items(d: TreeMapData) -> list[ItemRef]:
    return [ItemRef(f"branches.{i}", b.title) for i, b in enumerate(d.branches) if b.blanks]


register("treeMapWorksheet", TreeMapData, _tree_items)


# ── tChartWorksheet ─────────────────────────────────────────────────────────


class TChartData(KindData):
    title: Text
    instructions: str | None = None
    columns: Annotated[list[Text], Field(min_length=2, max_length=3)]
    row_count: Annotated[int, Field(ge=1, le=12)] = 8
    word_bank: list[Text] = Field(default_factory=list)

    @model_validator(mode="after")
    def _checks(self) -> "TChartData":
        _unique(self.columns, "columns")
        if self.word_bank:
            _unique(self.word_bank, "word_bank")
        return self


def _t_chart_items(d: TChartData) -> list[ItemRef]:
    return [ItemRef(f"columns.{i}", c) for i, c in enumerate(d.columns)]


register("tChartWorksheet", TChartData, _t_chart_items)


# ── featureMatrixWorksheet ──────────────────────────────────────────────────


class FeatureMatrixData(KindData):
    """Items are plain strings here; the PIL path's dict items are not hosted (AGENTS.md)."""

    title: Text
    instructions: str | None = None
    items: Annotated[list[Text], Field(min_length=1, max_length=8)]
    properties: Annotated[list[Text], Field(min_length=1, max_length=8)]

    @model_validator(mode="after")
    def _checks(self) -> "FeatureMatrixData":
        _unique(self.items, "items")
        _unique(self.properties, "properties")
        return self


def _feature_items(d: FeatureMatrixData) -> list[ItemRef]:
    return [ItemRef(f"items.{i}", it) for i, it in enumerate(d.items)]


register("featureMatrixWorksheet", FeatureMatrixData, _feature_items)


# ── matchingWorksheet ───────────────────────────────────────────────────────


class MatchingData(KindData):
    """left_items[i] matches right_items[i]; the renderer prints the lists side by side."""

    title: Text
    instructions: str | None = None
    left_items: Annotated[list[Text], Field(min_length=2, max_length=10)]
    right_items: Annotated[list[Text], Field(min_length=2, max_length=10)]

    @model_validator(mode="after")
    def _checks(self) -> "MatchingData":
        if len(self.left_items) != len(self.right_items):
            raise ValueError("left_items and right_items must be the same length")
        _unique(self.left_items, "left_items")
        _unique(self.right_items, "right_items")
        return self


def _matching_items(d: MatchingData) -> list[ItemRef]:
    return [ItemRef(f"left_items.{i}", t) for i, t in enumerate(d.left_items)]


register("matchingWorksheet", MatchingData, _matching_items)
