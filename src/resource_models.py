"""Pydantic models that mirror docs/WORKSHEET_REQUEST_SCHEMA.md."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

MAX_MATH_PROBLEMS = 20
MAX_READING_QUESTIONS = 10
MAX_VOCAB_ENTRIES = 12
MAX_RESPONSE_LINES = 8


class TwoOperandProblem(BaseModel):
    """Single vertical math problem (supports + / -)."""

    model_config = ConfigDict(extra="forbid")

    operand_one: int = Field(..., description="Top operand for the vertical problem")
    operand_two: int = Field(..., description="Bottom operand for the vertical problem")
    operator: str = Field(..., description="Operator symbol (+ or -)")

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, value: str) -> str:
        if value not in {"+", "-"}:
            raise ValueError("operator must be '+' or '-'")
        return value


class MathWorksheetRequest(BaseModel):
    """Request payload for generate_two_operand_math_worksheet."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    problems: List[TwoOperandProblem] = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default=None)

    @model_validator(mode="after")
    def check_problem_count(self) -> "MathWorksheetRequest":
        if len(self.problems) > MAX_MATH_PROBLEMS:
            raise ValueError(f"problems cannot exceed {MAX_MATH_PROBLEMS} entries")
        return self


class ReadingQuestion(BaseModel):
    """Free-response reading comprehension prompt."""

    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(..., description="Question text rendered on the worksheet")
    response_lines: int = Field(default=2, ge=1, le=MAX_RESPONSE_LINES)

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("prompt must be non-empty")
        return value


class VocabularyEntry(BaseModel):
    """Vocabulary drill line rendered at the bottom of the worksheet."""

    model_config = ConfigDict(extra="forbid")

    term: str = Field(..., description="Vocabulary word")
    definition: Optional[str] = Field(default=None, description="Optional definition text")
    response_lines: int = Field(default=1, ge=1, le=MAX_RESPONSE_LINES)

    @field_validator("term")
    @classmethod
    def validate_term(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("term must be non-empty")
        return value


class ReadingWorksheetRequest(BaseModel):
    """Request payload for generate_reading_comprehension_worksheet."""

    model_config = ConfigDict(extra="forbid")

    passage_title: str = Field(...)
    passage: str = Field(...)
    questions: List[ReadingQuestion] = Field(..., min_length=1)
    vocabulary: List[VocabularyEntry] = Field(default_factory=list)
    instructions: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)

    @field_validator("passage_title")
    @classmethod
    def validate_passage_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("passage_title must be non-empty")
        return value

    @field_validator("passage")
    @classmethod
    def validate_passage(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("passage must be non-empty")
        return value

    @model_validator(mode="after")
    def check_counts(self) -> "ReadingWorksheetRequest":
        if len(self.questions) > MAX_READING_QUESTIONS:
            raise ValueError(f"questions cannot exceed {MAX_READING_QUESTIONS} entries")
        if len(self.vocabulary) > MAX_VOCAB_ENTRIES:
            raise ValueError(f"vocabulary cannot exceed {MAX_VOCAB_ENTRIES} entries")
        return self


# ── HTML worksheet request models ──────────────────────────────────────────
# These models validate LLM output for worksheet types rendered via
# worksheet_html_renderer.py.  Each model's fields map directly to the
# dict keys consumed by the corresponding render function.


class FeatureMatrixWorksheetRequest(BaseModel):
    """Grid comparing items against a set of properties."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    items: List[str] = Field(..., min_length=1, description="Row labels (e.g. animal names)")
    properties: List[str] = Field(..., min_length=1, description="Column headers (e.g. 'Has Fur')")
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class TreeMapBranch(BaseModel):
    """One branch of a tree map."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Branch label")
    prefilled: List[str] = Field(default_factory=list, description="Pre-filled slot values")
    blank_count: int = Field(default=1, ge=0, description="Number of blank write-in slots")


class TreeMapWorksheetRequest(BaseModel):
    """Root + branches classification map."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    root_label: str = Field(..., description="Central root node label")
    branches: List[TreeMapBranch] = Field(..., min_length=1)
    columns: Optional[int] = Field(
        default=None, ge=1, description="Branches per row (auto if omitted)"
    )
    word_bank: List[str] = Field(default_factory=list, description="Optional word bank tiles")
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class OddOneOutRow(BaseModel):
    """One row in an odd-one-out worksheet."""

    model_config = ConfigDict(extra="forbid")

    items: List[str] = Field(
        ..., min_length=3, description="At least 3 items; one is the odd one out"
    )
    reasoning_lines: int = Field(default=1, ge=0)


class OddOneOutWorksheetRequest(BaseModel):
    """Circle the item that doesn't belong."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    rows: List[OddOneOutRow] = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class MatchingWorksheetRequest(BaseModel):
    """Two-column matching (draw a line) worksheet."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    left_items: List[str] = Field(..., min_length=2)
    right_items: List[str] = Field(
        ..., min_length=2, description="Same length as left_items, pre-shuffled"
    )
    metadata: Optional[Dict[str, Any]] = Field(default=None)

    @model_validator(mode="after")
    def check_equal_lengths(self) -> "MatchingWorksheetRequest":
        if len(self.left_items) != len(self.right_items):
            raise ValueError("left_items and right_items must have the same length")
        return self


class CauseEffectPair(BaseModel):
    """One cause → effect pair."""

    model_config = ConfigDict(extra="forbid")

    cause: str = Field(..., description="The cause (pre-filled)")
    effect: Optional[str] = Field(
        default=None, description="Pre-filled effect; omit to leave blank for student"
    )
    effect_lines: int = Field(
        default=2, ge=1, description="Blank answer lines when effect is omitted"
    )


class CauseEffectWorksheetRequest(BaseModel):
    """Cause and effect organizer."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    pairs: List[CauseEffectPair] = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class FrayerEntry(BaseModel):
    """One word entry in a Frayer Model."""

    model_config = ConfigDict(extra="forbid")

    word: str = Field(..., description="The vocabulary word in the centre")
    quadrants: Dict[str, Any] = Field(
        default_factory=dict,
        description="Map of quadrant label → content (str, list, or omit for blank)",
    )


class FrayerModelWorksheetRequest(BaseModel):
    """Frayer Model vocabulary organizer (4-quadrant)."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    entries: List[FrayerEntry] = Field(..., min_length=1)
    quadrant_labels: List[str] = Field(
        default_factory=lambda: ["Definition", "Characteristics", "Examples", "Non-Examples"]
    )
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class WordSortCategory(BaseModel):
    """One category column in a word sort."""

    model_config = ConfigDict(extra="forbid")

    label: str


class WordSortWorksheetRequest(BaseModel):
    """Sort word tiles into labelled categories."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    categories: List[WordSortCategory] = Field(..., min_length=2)
    tiles: List[str] = Field(..., min_length=1, description="Word tiles the student sorts")
    columns: Optional[int] = Field(default=None, ge=1)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class WritingScaffoldSection(BaseModel):
    """One labelled section of a writing scaffold."""

    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., description="Section heading, e.g. 'Introduction'")
    starter: Optional[str] = Field(default=None, description="Optional sentence starter in italic")
    lines: int = Field(default=3, ge=1)


class WritingScaffoldWorksheetRequest(BaseModel):
    """Structured writing scaffold with labelled sections."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    topic: Optional[str] = Field(default=None, description="Topic displayed at top of worksheet")
    sections: List[WritingScaffoldSection] = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class TChartWorksheetRequest(BaseModel):
    """Two-column T-Chart comparison."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    columns: List[str] = Field(
        default_factory=lambda: ["Column A", "Column B"], min_length=2, max_length=4
    )
    row_count: int = Field(default=8, ge=2, le=20)
    word_bank: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class ResourceRequests(BaseModel):
    """Wrapper that mirrors daily_plan[n].resources."""

    model_config = ConfigDict(extra="forbid")

    # Pillow-rendered (fallback for types without HTML renderer)
    mathWorksheet: Optional[MathWorksheetRequest] = Field(default=None)

    # HTML-rendered worksheet types
    readingWorksheet: Optional[ReadingWorksheetRequest] = Field(default=None)
    featureMatrixWorksheet: Optional[FeatureMatrixWorksheetRequest] = Field(default=None)
    treeMapWorksheet: Optional[TreeMapWorksheetRequest] = Field(default=None)
    oddOneOutWorksheet: Optional[OddOneOutWorksheetRequest] = Field(default=None)
    matchingWorksheet: Optional[MatchingWorksheetRequest] = Field(default=None)
    causeEffectWorksheet: Optional[CauseEffectWorksheetRequest] = Field(default=None)
    frayerModelWorksheet: Optional[FrayerModelWorksheetRequest] = Field(default=None)
    wordSortWorksheet: Optional[WordSortWorksheetRequest] = Field(default=None)
    writingScaffoldWorksheet: Optional[WritingScaffoldWorksheetRequest] = Field(default=None)
    tChartWorksheet: Optional[TChartWorksheetRequest] = Field(default=None)

    def has_requests(self) -> bool:
        """True when at least one worksheet request is present."""
        return any(v is not None for v in self.model_dump().values())


__all__ = [
    "MAX_MATH_PROBLEMS",
    "MAX_READING_QUESTIONS",
    "MAX_VOCAB_ENTRIES",
    "MAX_RESPONSE_LINES",
    "TwoOperandProblem",
    "MathWorksheetRequest",
    "ReadingQuestion",
    "VocabularyEntry",
    "ReadingWorksheetRequest",
    "FeatureMatrixWorksheetRequest",
    "TreeMapBranch",
    "TreeMapWorksheetRequest",
    "OddOneOutRow",
    "OddOneOutWorksheetRequest",
    "MatchingWorksheetRequest",
    "CauseEffectPair",
    "CauseEffectWorksheetRequest",
    "FrayerEntry",
    "FrayerModelWorksheetRequest",
    "WordSortCategory",
    "WordSortWorksheetRequest",
    "WritingScaffoldSection",
    "WritingScaffoldWorksheetRequest",
    "TChartWorksheetRequest",
    "ResourceRequests",
]
