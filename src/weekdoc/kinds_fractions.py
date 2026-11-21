"""Fraction figure kinds: strips, circles, area models, number lines (M2.9b).

Field names are the renderer's own (``_render_fraction_*`` in worksheet_html_renderer). The
offline renderer draws these figures but has no answer field, so each item here also accepts
an optional typed answer that the renderer never reads (unknown keys are ignored, so the
offline output is byte-identical with or without it):

* ``answer`` (strips, circles, area): the fraction the figure should show or the child should
  shade, as ``"n/d"``. When the figure is already shaded, ``answer`` must match the shading.
* ``answers`` (number line): the fractions the child marks, each as ``"n/d"``; each must land
  on a tick of the line (``3/6`` on halves is fine, ``1/3`` on fourths is not).

Impossible fractions are rejected: zero denominators, numerators above the denominator,
shaded counts beyond the parts, shade indices outside the figure, and non-positive weights.
Colours are restricted to hex or a plain colour word because the renderer writes them into
a style attribute unescaped. Every item is addressable, so the answer key can point at it.
"""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from .kinds import ItemRef, KindData, register

MAX_PARTS = 12

Color = Annotated[
    str, StringConstraints(pattern=r"^(#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6}|[a-zA-Z]{3,20})$")
]
Parts = Annotated[int, Field(ge=1, le=MAX_PARTS)]
Inches = Annotated[float, Field(gt=0, le=8)]

_FRACTION = re.compile(r"^\s*(\d{1,3})\s*/\s*(\d{1,3})\s*$")


def parse_fraction(text: str) -> tuple[int, int]:
    """Parse ``"n/d"`` into ``(n, d)``; reject zero denominators and improper fractions."""
    m = _FRACTION.match(text)
    if not m:
        raise ValueError(f"answer {text!r} must look like '3/4'")
    n, d = int(m.group(1)), int(m.group(2))
    if d == 0:
        raise ValueError(f"answer {text!r} has a zero denominator")
    if n > d:
        raise ValueError(f"answer {text!r} is greater than 1; these figures show 0 to 1")
    return n, d


def _same_value(n: int, d: int, n2: int, d2: int) -> bool:
    return n * d2 == n2 * d


Fraction = Annotated[str, StringConstraints(strip_whitespace=True, max_length=8)]


def _check_answer(answer: str | None, shaded: int | None, parts: int | None) -> None:
    if answer is None:
        return
    n, d = parse_fraction(answer)
    if shaded is not None and parts is not None and not _same_value(n, d, shaded, parts):
        raise ValueError(f"answer {answer} does not match {shaded} of {parts} shaded")


# ── fractionStrips ──────────────────────────────────────────────────────────


class Strip(KindData):
    denominator: Parts
    label: str = ""
    shade: list[int] = Field(default_factory=list)
    color: Color = ""
    piece_label: str | None = None
    fill_all: bool = False
    answer: Fraction | None = None

    @model_validator(mode="after")
    def _bounds(self) -> "Strip":
        bad = [i for i in self.shade if not 0 <= i < self.denominator]
        if bad:
            raise ValueError(f"shade indices {bad} are outside 0..{self.denominator - 1}")
        if len(set(self.shade)) != len(self.shade):
            raise ValueError("shade indices repeat")
        if self.shade and not self.color:
            raise ValueError("a shaded strip needs a color or the shading is invisible")
        _check_answer(self.answer, len(self.shade) if self.shade else None, self.denominator)
        return self


class FractionStripsData(KindData):
    strips: Annotated[list[Strip], Field(min_length=1, max_length=8)]
    width_in: Inches = 6.0
    height_in: Inches = 0.44
    show_labels: bool = True


def _strip_items(d: FractionStripsData) -> list[ItemRef]:
    return [
        ItemRef(f"strips.{i}", s.label or f"strip cut into {s.denominator} parts")
        for i, s in enumerate(d.strips)
    ]


register("fractionStrips", FractionStripsData, _strip_items)


# ── fractionCircles ─────────────────────────────────────────────────────────


class Circle(KindData):
    parts: Parts = 1
    shaded: Annotated[int, Field(ge=0)] = 0
    caption: str = ""
    shade_color: Color = "#dbeafe"
    answer: Fraction | None = None

    @model_validator(mode="after")
    def _bounds(self) -> "Circle":
        if self.shaded > self.parts:
            raise ValueError(f"shaded {self.shaded} is more than the {self.parts} parts")
        _check_answer(self.answer, self.shaded if self.shaded else None, self.parts)
        return self


class FractionCirclesData(KindData):
    circles: Annotated[list[Circle], Field(min_length=1, max_length=8)]
    size_in: Inches = 1.5


def _circle_items(d: FractionCirclesData) -> list[ItemRef]:
    return [
        ItemRef(f"circles.{i}", c.caption or f"circle cut into {c.parts} parts")
        for i, c in enumerate(d.circles)
    ]


register("fractionCircles", FractionCirclesData, _circle_items)


# ── fractionArea ────────────────────────────────────────────────────────────

Weight = Annotated[float, Field(gt=0, le=20)]


class Grid(KindData):
    cols: Parts = 2
    rows: Parts = 2
    cols_spec: Annotated[list[Weight], Field(min_length=1, max_length=MAX_PARTS)] | None = None
    rows_spec: Annotated[list[Weight], Field(min_length=1, max_length=MAX_PARTS)] | None = None
    shaded: list[int] = Field(default_factory=list)
    shade_color: Color = "#ede9fe"
    caption: str = ""
    answer: Fraction | None = None

    @model_validator(mode="after")
    def _bounds(self) -> "Grid":
        n_cols = len(self.cols_spec) if self.cols_spec else self.cols
        n_rows = len(self.rows_spec) if self.rows_spec else self.rows
        cells = n_cols * n_rows
        if cells > 36:
            raise ValueError(f"{cells} cells is more than a child can read (max 36)")
        bad = [i for i in self.shaded if not 0 <= i < cells]
        if bad:
            raise ValueError(f"shaded indices {bad} are outside 0..{cells - 1}")
        if len(set(self.shaded)) != len(self.shaded):
            raise ValueError("shaded indices repeat")
        unequal = bool(self.cols_spec or self.rows_spec) and not (
            _equal(self.cols_spec) and _equal(self.rows_spec)
        )
        if self.answer is not None:
            n, d = parse_fraction(self.answer)
            if self.shaded and not unequal and not _same_value(n, d, len(self.shaded), cells):
                raise ValueError(
                    f"answer {self.answer} does not match {len(self.shaded)} of {cells} shaded"
                )
        return self


def _equal(spec: list[float] | None) -> bool:
    return spec is None or len(set(spec)) == 1


class FractionAreaData(KindData):
    grids: Annotated[list[Grid], Field(min_length=1, max_length=8)]
    size_in: Inches = 1.9


def _area_items(d: FractionAreaData) -> list[ItemRef]:
    return [ItemRef(f"grids.{i}", g.caption or f"shape {i + 1}") for i, g in enumerate(d.grids)]


register("fractionArea", FractionAreaData, _area_items)


# ── fractionNumberLine ──────────────────────────────────────────────────────


class FractionLine(KindData):
    denominator: Annotated[int, Field(ge=2, le=MAX_PARTS)] = 2
    prompt: str = ""
    show_labels: bool = True
    start_label: str = "0"
    end_label: str = "1"
    answers: Annotated[list[Fraction], Field(max_length=4)] = Field(default_factory=list)

    @model_validator(mode="after")
    def _on_a_tick(self) -> "FractionLine":
        for a in self.answers:
            n, d = parse_fraction(a)
            if (n * self.denominator) % d:
                raise ValueError(
                    f"answer {a} is not a tick on a line cut into {self.denominator} parts"
                )
        return self


class FractionNumberLineData(KindData):
    lines: Annotated[list[FractionLine], Field(min_length=1, max_length=6)]
    width_in: Inches = 6.0


def _line_items(d: FractionNumberLineData) -> list[ItemRef]:
    return [
        ItemRef(f"lines.{i}", ln.prompt or f"line cut into {ln.denominator} parts")
        for i, ln in enumerate(d.lines)
    ]


register("fractionNumberLine", FractionNumberLineData, _line_items)
