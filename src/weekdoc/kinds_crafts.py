"""Image-and-grid kinds: colorTask, cutCards, pixelCopyWorksheet (M2.9f).

How the server produces these deterministically, with no model-written code and no network:

* **pixelCopyWorksheet** is a validated color matrix (``colors``: n x n hex strings, n in
  4..32, at most 6 distinct colors, at least 2). The renderer turns the matrix into inline SVG
  (``_svg_pixel_grid``). The offline renderer's ``image_path`` (a server file read, sampled
  with Pillow) is NOT a hosted field: the model forbids it, so a hosted week can never make the
  server open a path. The renderer has one additive hook: a ``colors`` matrix in the data wins
  over ``image_path``. Offline callers never pass ``colors``, so their output is unchanged.
* **colorTask** pairs a figure with a color key. The renderer recurses into ``_render_block``
  for the figure, so the figure here is a closed, validated union of the five procedural
  figures (strips, circles, area, number line, hearts), each drawn by CSS/HTML from numbers.
  No arbitrary block kind, no image, no path can be nested.
* **cutCards** is validated card text (short strings in a grid). No images.

Shared rule for image-backed kinds (kept self-contained so it is easy to reconcile with
M2.9e): procedural SVG/CSS from validated numbers and colors; vetted bundled assets by id would
be the other allowed source, and none are needed here.

Color safety: the renderer writes hex values into ``style`` attributes unescaped, so every
color field is ``#rrggbb`` only (normalised to lowercase). That blocks CSS/HTML injection.
Numbers are bounded so a page cannot be made absurdly large or an index point off the figure.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import Field, StringConstraints, field_validator, model_validator

from .kinds import ItemRef, KindData, register
from .kinds_comprehension import Text

PIXEL_MIN, PIXEL_MAX = 4, 32
PIXEL_MAX_COLORS = 6  # the renderer's legend shows at most this many (_PC_LEGEND_MAX)

Hex = Annotated[str, StringConstraints(pattern=r"^#[0-9a-fA-F]{6}$")]
Caption = Annotated[str, StringConstraints(max_length=80)]
Inches = Annotated[float, Field(ge=0.5, le=7.5, allow_inf_nan=False)]
Denominator = Annotated[int, Field(ge=1, le=24)]


# ── cutCards ────────────────────────────────────────────────────────────────


class CutCardsData(KindData):
    cards: Annotated[
        list[Annotated[Text, StringConstraints(max_length=40)]], Field(min_length=1, max_length=40)
    ]
    columns: Annotated[int, Field(ge=1, le=8)] = 6


register(
    "cutCards",
    CutCardsData,
    waiver="Kit page: cards are cut out and used in later tasks; this page itself asks nothing.",
)

# ── colorTask figures ───────────────────────────────────────────────────────


class Strip(KindData):
    label: Caption = ""
    denominator: Denominator
    shade: list[Annotated[int, Field(ge=0, le=23)]] = Field(default_factory=list)
    color: Hex | Literal[""] = ""
    fill_all: bool = False
    piece_label: Annotated[str, StringConstraints(max_length=12)] | None = None

    @model_validator(mode="after")
    def _shade_in_range(self) -> "Strip":
        if any(i >= self.denominator for i in self.shade):
            raise ValueError(f"shade indexes must be below denominator {self.denominator}")
        return self


class StripsFigure(KindData):
    strips: Annotated[list[Strip], Field(min_length=1, max_length=8)]
    width_in: Inches = 6.0
    height_in: Annotated[float, Field(ge=0.2, le=1.5, allow_inf_nan=False)] = 0.44
    show_labels: bool = True


class Circle(KindData):
    parts: Denominator
    shaded: Annotated[int, Field(ge=0, le=24)] = 0
    shade_color: Hex = "#dbeafe"
    caption: Caption = ""

    @model_validator(mode="after")
    def _shaded_le_parts(self) -> "Circle":
        if self.shaded > self.parts:
            raise ValueError("shaded cannot exceed parts")
        return self


class CirclesFigure(KindData):
    circles: Annotated[list[Circle], Field(min_length=1, max_length=6)]
    size_in: Annotated[float, Field(ge=0.5, le=3.0, allow_inf_nan=False)] = 1.5


Weight = Annotated[float, Field(gt=0, le=20, allow_inf_nan=False)]


class AreaGrid(KindData):
    cols: Annotated[int, Field(ge=1, le=12)] = 2
    rows: Annotated[int, Field(ge=1, le=12)] = 2
    cols_spec: Annotated[list[Weight], Field(min_length=1, max_length=12)] | None = None
    rows_spec: Annotated[list[Weight], Field(min_length=1, max_length=12)] | None = None
    shaded: list[Annotated[int, Field(ge=0, le=143)]] = Field(default_factory=list)
    shade_color: Hex = "#ede9fe"
    caption: Caption = ""

    @model_validator(mode="after")
    def _shaded_in_range(self) -> "AreaGrid":
        cols = len(self.cols_spec) if self.cols_spec else self.cols
        rows = len(self.rows_spec) if self.rows_spec else self.rows
        if any(i >= cols * rows for i in self.shaded):
            raise ValueError(f"shaded indexes must be below {cols * rows} cells")
        return self


class AreaFigure(KindData):
    grids: Annotated[list[AreaGrid], Field(min_length=1, max_length=6)]
    size_in: Annotated[float, Field(ge=0.5, le=3.5, allow_inf_nan=False)] = 1.9


class NumberLine(KindData):
    denominator: Annotated[int, Field(ge=2, le=24)] = 2
    prompt: Caption = ""
    show_labels: bool = True
    start_label: Annotated[str, StringConstraints(max_length=8)] = "0"
    end_label: Annotated[str, StringConstraints(max_length=8)] = "1"


class NumberLineFigure(KindData):
    lines: Annotated[list[NumberLine], Field(min_length=1, max_length=6)]
    width_in: Inches = 6.0


class HeartsFigure(KindData):
    hearts: Annotated[int, Field(ge=1, le=10)] = 5
    filled_halves: Annotated[int, Field(ge=0, le=20)] = 0
    width_in: Inches = 5.0
    height_in: Annotated[float, Field(ge=0.2, le=1.5, allow_inf_nan=False)] = 0.4
    caption: Caption = ""

    @model_validator(mode="after")
    def _filled_in_range(self) -> "HeartsFigure":
        if self.filled_halves > self.hearts * 2:
            raise ValueError("filled_halves cannot exceed 2 x hearts")
        return self


class StripsBlock(KindData):
    kind: Literal["fractionStrips"]
    data: StripsFigure


class CirclesBlock(KindData):
    kind: Literal["fractionCircles"]
    data: CirclesFigure


class AreaBlock(KindData):
    kind: Literal["fractionArea"]
    data: AreaFigure


class NumberLineBlock(KindData):
    kind: Literal["fractionNumberLine"]
    data: NumberLineFigure


class HeartsBlock(KindData):
    kind: Literal["heartBar"]
    data: HeartsFigure


Figure = Annotated[
    Union[StripsBlock, CirclesBlock, AreaBlock, NumberLineBlock, HeartsBlock],
    Field(discriminator="kind"),
]

# ── colorTask ───────────────────────────────────────────────────────────────


class ColorEntry(KindData):
    fraction: Annotated[Text, StringConstraints(max_length=24)]
    color_name: Annotated[Text, StringConstraints(max_length=24)]
    hex: Hex

    @field_validator("hex")
    @classmethod
    def _norm(cls, v: str) -> str:
        return v.lower()


class ColorTaskData(KindData):
    figure: Figure
    entries: Annotated[list[ColorEntry], Field(min_length=1, max_length=8)]

    @model_validator(mode="after")
    def _distinct_colors(self) -> "ColorTaskData":
        hexes = [e.hex for e in self.entries]
        names = [e.color_name.casefold() for e in self.entries]
        if len(set(hexes)) != len(hexes) or len(set(names)) != len(names):
            raise ValueError("each key entry needs its own color (hex and name must be unique)")
        return self


def _color_task_items(d: ColorTaskData) -> list[ItemRef]:
    return [
        ItemRef(f"entries.{i}", f"colour {e.fraction} {e.color_name}")
        for i, e in enumerate(d.entries)
    ]


register("colorTask", ColorTaskData, _color_task_items)

# ── pixelCopyWorksheet ──────────────────────────────────────────────────────


class PixelCopyData(KindData):
    title: Text
    instructions: str | None = None
    grid_size: Annotated[int, Field(ge=PIXEL_MIN, le=PIXEL_MAX)]
    colors: list[list[Hex]]

    @field_validator("colors")
    @classmethod
    def _norm_colors(cls, v: list[list[str]]) -> list[list[str]]:
        return [[c.lower() for c in row] for row in v]

    @model_validator(mode="after")
    def _square_and_small_palette(self) -> "PixelCopyData":
        n = self.grid_size
        if len(self.colors) != n or any(len(row) != n for row in self.colors):
            raise ValueError(f"colors must be a {n} x {n} matrix to match grid_size")
        distinct = {c for row in self.colors for c in row}
        if len(distinct) < 2:
            raise ValueError("the picture needs at least 2 colors")
        if len(distinct) > PIXEL_MAX_COLORS:
            raise ValueError(
                f"the picture uses {len(distinct)} colors; the key shows at most {PIXEL_MAX_COLORS}"
            )
        return self


def _pixel_items(d: PixelCopyData) -> list[ItemRef]:
    return [
        ItemRef(f"colors.{r}", f"copy row {r + 1} of {d.grid_size}") for r in range(d.grid_size)
    ]


register("pixelCopyWorksheet", PixelCopyData, _pixel_items)
