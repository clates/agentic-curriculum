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


class ResourceRequests(BaseModel):
    """Wrapper that mirrors daily_plan[n].resources."""

    model_config = ConfigDict(extra="forbid")

    mathWorksheet: Optional[MathWorksheetRequest] = Field(default=None)
    readingWorksheet: Optional[ReadingWorksheetRequest] = Field(default=None)

    def has_requests(self) -> bool:
        """True when at least one worksheet request is present."""
        return self.mathWorksheet is not None or self.readingWorksheet is not None


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
    "ResourceRequests",
]
