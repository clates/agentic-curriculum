"""Graph and comparison kinds: bar graph, pictograph, compare pairs, math alias (M2.9d).

Chart data is bounds-checked so a hosted chart cannot be empty or inconsistent: series length
must match the labels, no gaps, and every value must sit inside the axis range.

Where the answer is computable (reading a graph, comparing numbers, solving a stack) this module
also offers pure, deterministic helpers (``graph_values``, ``graph_answer``, ``compare_answer``,
``two_operand_answer``) so an answer key can be checked without a model. No model-written code
runs; the helpers only do arithmetic on already validated data.

``mathWorksheet`` is the renderer's legacy alias for ``twoOperandWorksheet`` (same renderer, same
fields). It is hosted here with exactly the two-operand model and bounds; new weeks should still
prefer ``twoOperandWorksheet``.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, model_validator

from .kinds import ItemRef, KindData, register
from .kinds_comprehension import Text
from .kinds_math import TwoOperandData, _two_operand_items

Short = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]
Side = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]


class GraphQuestion(KindData):
    prompt: Text
    response_lines: Annotated[int, Field(ge=1, le=5)] = 1


# ── barGraphWorksheet ───────────────────────────────────────────────────────


class BarGraphData(KindData):
    title: Text
    instructions: str | None = None
    categories: Annotated[list[Short], Field(min_length=1, max_length=12)]
    # None = blank grid for the child to colour; a list = bars to read (one per category).
    values: list[Annotated[float, Field(ge=0)]] | None = None
    y_max: Annotated[float, Field(gt=0, le=1000)] = 10
    y_step: Annotated[float, Field(gt=0, le=1000)] = 1
    x_label: str = ""
    y_label: str = ""
    height_in: Annotated[float, Field(ge=1, le=6)] = 2.5
    show_values: bool = False
    questions: Annotated[list[GraphQuestion], Field(max_length=6)] = Field(default_factory=list)

    @model_validator(mode="after")
    def _consistent(self) -> "BarGraphData":
        if len(set(self.categories)) != len(self.categories):
            raise ValueError("categories must be unique")
        steps = self.y_max / self.y_step
        if abs(steps - round(steps)) > 1e-9:
            raise ValueError("y_max must be a whole number of y_step steps")
        if not 1 <= round(steps) <= 50:
            raise ValueError(f"the y axis needs 1-50 steps, got {round(steps)}")
        if self.values is not None:
            if len(self.values) != len(self.categories):
                raise ValueError(
                    f"values has {len(self.values)} entries for {len(self.categories)} categories"
                )
            over = [v for v in self.values if v > self.y_max]
            if over:
                raise ValueError(f"values {over} exceed y_max {self.y_max}")
            if not self.questions:
                raise ValueError("a graph with bars to read needs at least one question")
        return self


def _graph_items(d: "BarGraphData | PictographData") -> list[ItemRef]:
    if d.questions:
        return [ItemRef(f"questions.{i}", q.prompt) for i, q in enumerate(d.questions)]
    # Blank mode with no questions: the child's task is one bar/row per group.
    if isinstance(d, BarGraphData):
        return [ItemRef(f"categories.{i}", f"Bar for {c}") for i, c in enumerate(d.categories)]
    return [ItemRef(f"rows.{i}", f"Row for {r.label}") for i, r in enumerate(d.rows)]


register("barGraphWorksheet", BarGraphData, _graph_items)


# ── pictographWorksheet ─────────────────────────────────────────────────────


class PictographRow(KindData):
    label: Short
    symbols: Annotated[int, Field(ge=0, le=15)] | None = None


class PictographData(KindData):
    title: Text
    instructions: str | None = None
    symbol: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=8)] = (
        "⭐"
    )
    per_symbol: Annotated[int, Field(ge=1, le=100)] = 1
    unit_label: str = ""
    rows: Annotated[list[PictographRow], Field(min_length=1, max_length=10)]
    blank: bool = False
    max_symbols: Annotated[int, Field(ge=1, le=15)] = 10
    questions: Annotated[list[GraphQuestion], Field(max_length=6)] = Field(default_factory=list)

    @model_validator(mode="after")
    def _consistent(self) -> "PictographData":
        labels = [r.label for r in self.rows]
        if len(set(labels)) != len(labels):
            raise ValueError("row labels must be unique")
        if self.blank:
            if any(r.symbols is not None for r in self.rows):
                raise ValueError("a blank pictograph must not give symbol counts")
            return self
        missing = [r.label for r in self.rows if r.symbols is None]
        if missing:
            raise ValueError(
                f"rows {missing} have no symbol count (set blank=true for a blank one)"
            )
        if not self.questions:
            raise ValueError("a pictograph to read needs at least one question")
        return self


register("pictographWorksheet", PictographData, _graph_items)


# ── comparePairs ────────────────────────────────────────────────────────────


class ComparePair(KindData):
    left: Side
    right: Side


class ComparePairsData(KindData):
    pairs: Annotated[list[ComparePair], Field(min_length=1, max_length=24)]
    columns: Annotated[int, Field(ge=1, le=6)] = 3


def _pair_items(d: ComparePairsData) -> list[ItemRef]:
    return [ItemRef(f"pairs.{i}", f"{p.left} ? {p.right}") for i, p in enumerate(d.pairs)]


register("comparePairs", ComparePairsData, _pair_items)


# ── mathWorksheet (legacy alias of twoOperandWorksheet) ─────────────────────


class MathWorksheetData(TwoOperandData):
    """Same fields and K-2 bounds as ``twoOperandWorksheet``."""


register("mathWorksheet", MathWorksheetData, _two_operand_items)


# ── Deterministic answer helpers ────────────────────────────────────────────

_NUM = re.compile(r"^\s*(-?\d+)\s*(?:/\s*(\d+)|\.(\d+))?\s*$")


def _to_number(text: str) -> Fraction | None:
    """Parse ``7``, ``3/8`` or ``0.25`` exactly; anything else (words, mixed numbers) is None."""
    m = _NUM.match(text)
    if not m:
        return None
    whole, den, dec = m.groups()
    if den is not None:
        return Fraction(int(whole), int(den)) if int(den) else None
    if dec is not None:
        return Fraction(f"{whole}.{dec}")
    return Fraction(int(whole))


def compare_answer(left: str, right: str) -> Literal["<", ">", "="] | None:
    """The correct symbol for ``left ? right``, or None when either side is not a plain number."""
    a, b = _to_number(left), _to_number(right)
    if a is None or b is None:
        return None
    return "<" if a < b else ">" if a > b else "="


def graph_values(data: BarGraphData | PictographData) -> dict[str, float]:
    """Label -> value a child reads off the graph (pictograph = symbols x per_symbol).

    Raises ValueError for a blank graph, which has nothing to read.
    """
    if isinstance(data, BarGraphData):
        if data.values is None:
            raise ValueError("blank bar graph has no values to read")
        return dict(zip(data.categories, data.values, strict=True))
    if data.blank:
        raise ValueError("blank pictograph has no values to read")
    return {r.label: r.symbols * data.per_symbol for r in data.rows}  # type: ignore[operator]


def graph_answer(
    data: BarGraphData | PictographData,
    question: Literal["value", "total", "most", "least", "difference"],
    *labels: str,
) -> float | str:
    """Deterministic graph-reading answers.

    value(label), total(), most() / least() (label with the extreme value; a tie raises),
    difference(label_a, label_b) = value(a) - value(b).
    """
    vals = graph_values(data)

    def get(label: str) -> float:
        if label not in vals:
            raise KeyError(f"no such category {label!r}; have {sorted(vals)}")
        return vals[label]

    if question == "value":
        return get(labels[0])
    if question == "total":
        return sum(vals.values())
    if question == "difference":
        return get(labels[0]) - get(labels[1])
    pick = max if question == "most" else min
    target = pick(vals.values())
    winners = [k for k, v in vals.items() if v == target]
    if len(winners) != 1:
        raise ValueError(f"{question} is a tie between {winners}")
    return winners[0]


def two_operand_answer(operand_one: int, operator: str, operand_two: int) -> int:
    """Answer to one stacked problem (K-2: operator is + or -)."""
    if operator == "+":
        return operand_one + operand_two
    if operator == "-":
        return operand_one - operand_two
    raise ValueError(f"unsupported operator {operator!r}")
