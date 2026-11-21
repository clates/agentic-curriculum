"""Diagram, map and picture kinds (M2.9e): labeled diagram, Venn, story map, shape ID,
picture sequence, error audit.

Image asset rule (hosted path)
------------------------------
A hosted week never carries a file path, URL or data URI for an image, and rendering never
reads a file or touches the network. Every picture on these kinds is one of:

* procedural inline SVG/HTML that the renderer draws from structured, bounded data
  (shapes by enum name, clocks from hour/minute, dot arrays from rows/cols, fraction wedges
  from a part count, Venn circles from labels); or
* text, including emoji characters, which are glyphs and not image files.

Colours are restricted to ``#rrggbb`` because the renderer writes them into SVG attributes
unescaped.

Hosted with a limit
    labeledDiagramWorksheet: the renderer's ``image_path`` is NOT a hosted field. The page
    prints the framed, numbered diagram box with its placeholder, and the child draws or glues
    the picture. A vetted bundled asset library (resolve an id to an inline SVG before render)
    is the extension point if the product wants pre-drawn diagrams; none ships today.

Not hosted
    Anything needing a raster image (PIL-made art, photos, logos, ``image_path`` on the
    handwriting/labeled kinds): it cannot be produced deterministically from structured data.

Answer keys: ``show_answers`` and the per-field answer slots that only print in answer mode
(story map ``value``, error audit ``bug_location``/``diagnosis``/``fix_text``) are not hosted
fields; those answers live in the worksheet's ``answers`` addressed by item_ref.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import Discriminator, Field, StringConstraints, Tag, model_validator

from .kinds import ItemRef, KindData, register
from .kinds_comprehension import Text

Color = Annotated[str, StringConstraints(pattern=r"^#[0-9a-fA-F]{6}$")]
Decimal = Annotated[str, StringConstraints(pattern=r"^\d{1,6}(\.\d{1,6})?$")]
ShapeName = Literal["circle", "square", "rectangle", "triangle"]


def _unique(values: list[str], what: str) -> None:
    folded = [v.strip().casefold() for v in values]
    if len(set(folded)) != len(folded):
        raise ValueError(f"{what} must be unique")


class VisualData(KindData):
    """An explicit null would print as the text "None", so nulls are rejected up front."""

    @model_validator(mode="before")
    @classmethod
    def _no_nulls(cls, values: Any) -> Any:
        if isinstance(values, dict):
            bad = [k for k, v in values.items() if v is None]
            if bad:
                raise ValueError(f"omit {', '.join(bad)} instead of setting it to null")
        return values


# ── labeledDiagramWorksheet ─────────────────────────────────────────────────


class DiagramLabel(VisualData):
    number: Annotated[int, Field(ge=1, le=20)]
    answer: Text
    hint: Text | None = None


class LabeledDiagramData(VisualData):
    title: Text
    instructions: Text | None = None
    word_bank: bool = False
    labels: Annotated[list[DiagramLabel], Field(min_length=2, max_length=12)]

    @model_validator(mode="after")
    def _checks(self) -> "LabeledDiagramData":
        nums = [lb.number for lb in self.labels]
        if len(set(nums)) != len(nums):
            raise ValueError("label numbers must be unique")
        _unique([lb.answer for lb in self.labels], "label answers")
        return self


def _labeled_items(d: LabeledDiagramData) -> list[ItemRef]:
    return [ItemRef(f"labels.{i}", f"Label {lb.number}") for i, lb in enumerate(d.labels)]


register("labeledDiagramWorksheet", LabeledDiagramData, _labeled_items)


# ── vennDiagramWorksheet ────────────────────────────────────────────────────

_VENN_ITEMS = Annotated[list[Text], Field(max_length=6)]


class VennData(VisualData):
    title: Text
    instructions: Text | None = None
    left_label: Text
    right_label: Text
    both_label: Text = "Both"
    left_items: _VENN_ITEMS = Field(default_factory=list)
    right_items: _VENN_ITEMS = Field(default_factory=list)
    both_items: _VENN_ITEMS = Field(default_factory=list)
    word_bank: Annotated[list[Text], Field(min_length=1, max_length=12)]

    @model_validator(mode="after")
    def _checks(self) -> "VennData":
        _unique([self.left_label, self.right_label], "circle labels")
        _unique(self.word_bank, "word_bank")
        placed = self.left_items + self.right_items + self.both_items
        _unique(placed, "pre-placed items")
        bank = {w.casefold() for w in self.word_bank}
        if any(p.strip().casefold() in bank for p in placed):
            raise ValueError("a pre-placed item must not also be in the word_bank")
        return self


def _venn_items(d: VennData) -> list[ItemRef]:
    return [ItemRef(f"word_bank.{i}", w) for i, w in enumerate(d.word_bank)]


register("vennDiagramWorksheet", VennData, _venn_items)


# ── storyMapWorksheet ───────────────────────────────────────────────────────


class StoryField(VisualData):
    label: Text
    prompt: Text | None = None
    lines: Annotated[int, Field(ge=1, le=8)] = 2


class StoryMapData(VisualData):
    title: Text
    instructions: Text | None = None
    story_title_field: bool = True
    fields: Annotated[list[StoryField], Field(min_length=1, max_length=8)]

    @model_validator(mode="after")
    def _checks(self) -> "StoryMapData":
        _unique([f.label for f in self.fields], "field labels")
        return self


def _story_map_items(d: StoryMapData) -> list[ItemRef]:
    return [ItemRef(f"fields.{i}", f.label) for i, f in enumerate(d.fields)]


register("storyMapWorksheet", StoryMapData, _story_map_items)


# ── shapeIdWorksheet ────────────────────────────────────────────────────────


class Shape(VisualData):
    type: ShapeName
    color: Color | None = None


class LabeledShape(Shape):
    label: Text | None = None


class PatternShape(VisualData):
    type: ShapeName | None = None
    color: Color | None = None
    blank: bool = False

    @model_validator(mode="after")
    def _blank_xor_type(self) -> "PatternShape":
        if self.blank == (self.type is not None):
            raise ValueError("a pattern cell is either blank:true or has a type, not both/neither")
        if self.blank and self.color is not None:
            raise ValueError("a blank cell has no color")
        return self


class MirrorOption(VisualData):
    type: ShapeName
    color: Color | None = None
    flipped: bool = False


class MirrorRow(VisualData):
    type: ShapeName
    color: Color | None = None
    options: Annotated[list[MirrorOption], Field(min_length=2, max_length=4)]

    @model_validator(mode="after")
    def _one_match(self) -> "MirrorRow":
        if not any(o.type == self.type for o in self.options):
            raise ValueError("one option must be the same shape as the reference")
        return self


class _ShapeBase(VisualData):
    title: Text
    instructions: Text | None = None


class ShapeGallery(_ShapeBase):
    mode: Literal["gallery"]
    shapes: Annotated[list[LabeledShape], Field(min_length=1, max_length=8)]
    word_bank: Annotated[list[Text], Field(min_length=1, max_length=8)] | None = None


class ShapeAttributes(_ShapeBase):
    mode: Literal["attributes"]
    shapes: Annotated[list[Shape], Field(min_length=1, max_length=8)]


class ShapePattern(_ShapeBase):
    mode: Literal["pattern"]
    shapes: Annotated[list[PatternShape], Field(min_length=3, max_length=10)]

    @model_validator(mode="after")
    def _has_blank(self) -> "ShapePattern":
        if not any(s.blank for s in self.shapes):
            raise ValueError("a pattern needs at least one blank cell to fill")
        if all(s.blank for s in self.shapes):
            raise ValueError("a pattern needs at least one shown shape")
        return self


class ShapeSort(_ShapeBase):
    mode: Literal["sort"]
    shapes: Annotated[list[Shape], Field(min_length=2, max_length=10)]  # lettered A-J
    categories: Annotated[list[Text], Field(min_length=2, max_length=4)]

    @model_validator(mode="after")
    def _checks(self) -> "ShapeSort":
        _unique(self.categories, "categories")
        return self


class ShapeMirror(_ShapeBase):
    mode: Literal["mirror_match"]
    shapes: Annotated[list[MirrorRow], Field(min_length=1, max_length=5)]


def _mode(v: Any) -> str | None:
    raw = v.get("mode") if isinstance(v, dict) else getattr(v, "mode", None)
    return raw if isinstance(raw, str) else None


ShapeIdData = Annotated[
    Union[
        Annotated[ShapeGallery, Tag("gallery")],
        Annotated[ShapeAttributes, Tag("attributes")],
        Annotated[ShapePattern, Tag("pattern")],
        Annotated[ShapeSort, Tag("sort")],
        Annotated[ShapeMirror, Tag("mirror_match")],
    ],
    Discriminator(_mode),
]


def _shape_items(d: Any) -> list[ItemRef]:
    if d.mode == "pattern":
        return [
            ItemRef(f"shapes.{i}", "Draw the next shape") for i, s in enumerate(d.shapes) if s.blank
        ]
    if d.mode == "mirror_match":
        return [ItemRef(f"shapes.{i}", f"Match the {s.type}") for i, s in enumerate(d.shapes)]
    ask = {
        "gallery": "Name this shape",
        "attributes": "Count sides and corners",
        "sort": "Which group?",
    }[d.mode]
    return [ItemRef(f"shapes.{i}", f"{ask} ({s.type})") for i, s in enumerate(d.shapes)]


class _ShapeIdModel(VisualData):
    """Wrapper so the registry (which wants a model class) can validate the mode union."""

    @model_validator(mode="wrap")
    @classmethod
    def _dispatch(cls, values: Any, handler: Any) -> Any:
        from pydantic import TypeAdapter

        return TypeAdapter(ShapeIdData).validate_python(values)


register("shapeIdWorksheet", _ShapeIdModel, _shape_items)


# ── pictureSequenceWorksheet ────────────────────────────────────────────────


def _glyph(value: str) -> str:
    # an emoji is a glyph, not an image file; ASCII letters would make it a word
    if any(c.isascii() and c.isalpha() for c in value):
        raise ValueError("emoji must be emoji characters, not words")
    return value


Emoji = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=12)]


class PictureStep(VisualData):
    emoji: Emoji
    text: Text

    @model_validator(mode="after")
    def _emoji(self) -> "PictureStep":
        _glyph(self.emoji)
        return self


class PictureSequenceData(VisualData):
    """steps are printed in the order given, so the author supplies them already shuffled.
    The correct order lives in ``answers`` (steps.N -> "1", "2", ...)."""

    title: Text
    instructions: Text | None = None
    steps: Annotated[list[PictureStep], Field(min_length=3, max_length=6)]

    @model_validator(mode="after")
    def _checks(self) -> "PictureSequenceData":
        _unique([s.text for s in self.steps], "step texts")
        return self


def _picture_items(d: PictureSequenceData) -> list[ItemRef]:
    return [ItemRef(f"steps.{i}", s.text) for i, s in enumerate(d.steps)]


register("pictureSequenceWorksheet", PictureSequenceData, _picture_items)


# ── errorAuditWorksheet ─────────────────────────────────────────────────────


class ClockArt(VisualData):
    kind: Literal["clock"]
    hour: Annotated[float, Field(ge=0, le=12)] = 12
    minute: Annotated[int, Field(ge=0, le=59)] = 0
    missing: Literal["hour", "minute", "both"] | None = None


class DotsArt(VisualData):
    kind: Literal["dots"]
    rows: Annotated[int, Field(ge=1, le=10)] = 2
    cols: Annotated[int, Field(ge=1, le=10)] = 2


class PartitionsArt(VisualData):
    kind: Literal["partitions"]
    parts: Annotated[int, Field(ge=2, le=12)] = 2
    broken: Annotated[int, Field(ge=0, le=11)] | None = None
    shaded: Annotated[int, Field(ge=0, le=11)] | list[Annotated[int, Field(ge=0, le=11)]] | None = (
        None
    )

    @model_validator(mode="after")
    def _in_range(self) -> "PartitionsArt":
        picked = (
            []
            if self.shaded is None
            else (self.shaded if isinstance(self.shaded, list) else [self.shaded])
        )
        if self.broken is not None:
            picked = picked + [self.broken]
        if any(p >= self.parts for p in picked):
            raise ValueError("broken/shaded wedge index must be less than parts")
        return self


Art = Annotated[Union[ClockArt, DotsArt, PartitionsArt], Field(discriminator="kind")]


class StarterArt(VisualData):
    parts: Annotated[int, Field(ge=2, le=12)]


class FixScaffold(VisualData):
    addends: Annotated[list[Decimal], Field(min_length=2, max_length=4)]
    answer: Decimal


class Specimen(VisualData):
    prompt: Text
    lines: Annotated[list[Text], Field(max_length=10)] = Field(default_factory=list)
    art: Art | None = None
    starter_art: StarterArt | None = None
    fix_scaffold: FixScaffold | None = None
    blank_fix_circle: bool = False

    @model_validator(mode="after")
    def _checks(self) -> "Specimen":
        if not self.lines and self.art is None:
            raise ValueError("a specimen needs lines or art to audit")
        partitions = isinstance(self.art, PartitionsArt)
        if (self.starter_art or self.blank_fix_circle) and not partitions:
            raise ValueError("starter_art and blank_fix_circle need partitions art")
        if self.fix_scaffold and self.art is not None:
            raise ValueError("fix_scaffold is for text specimens, not art")
        return self


class ErrorAuditData(VisualData):
    title: Text
    instructions: Text | None = None
    theme_label: Text | None = None
    legend: Annotated[list[Text], Field(max_length=8)] = Field(default_factory=list)
    specimens: Annotated[list[Specimen], Field(min_length=1, max_length=8)]
    fix_mode: Literal["rewrite", "redraw", "none"] = "rewrite"
    verify: bool = True
    adversarial: bool = False
    fix_lines: Annotated[int, Field(ge=1, le=8)] = 2
    columns: Literal[1, 2] = 1

    @model_validator(mode="after")
    def _checks(self) -> "ErrorAuditData":
        _unique(self.legend, "legend")
        for s in self.specimens:
            if s.fix_scaffold and self.fix_mode != "rewrite":
                raise ValueError("fix_scaffold needs fix_mode 'rewrite'")
            if (s.starter_art or s.blank_fix_circle) and self.fix_mode != "redraw":
                raise ValueError("starter_art and blank_fix_circle need fix_mode 'redraw'")
        return self


def _audit_items(d: ErrorAuditData) -> list[ItemRef]:
    return [ItemRef(f"specimens.{i}", s.prompt) for i, s in enumerate(d.specimens)]


register("errorAuditWorksheet", ErrorAuditData, _audit_items)
