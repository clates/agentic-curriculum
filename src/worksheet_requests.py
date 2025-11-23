"""Glue between worksheet request models and worksheet generators."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from pydantic import ValidationError

from .worksheets import (
    generate_reading_comprehension_worksheet,
    generate_two_operand_math_worksheet,
    ReadingWorksheet,
    Worksheet,
)
from .resource_models import (
    MathWorksheetRequest,
    ReadingWorksheetRequest,
    ResourceRequests,
)


@dataclass
class WorksheetArtifactPlan:
    """Represents a worksheet ready for rendering plus metadata."""

    kind: str
    worksheet: Worksheet | ReadingWorksheet
    filename_hint: str
    metadata: dict


class WorksheetRequestError(Exception):
    """Raised when a worksheet request fails to build."""

    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind
        self.message = message


def _derive_filename(kind: str, metadata: dict | None) -> str:
    label = (metadata or {}).get("artifact_label") or kind
    return f"{label}_{kind}"


def _build_math_worksheet(request: MathWorksheetRequest) -> WorksheetArtifactPlan:
    worksheet = generate_two_operand_math_worksheet(
        problems=[problem.model_dump() for problem in request.problems],
        title=request.title or "Two-Operand Practice",
        instructions=request.instructions or "Solve each problem. Show your work if needed.",
        metadata=request.metadata or {},
    )
    return WorksheetArtifactPlan(
        kind="mathWorksheet",
        worksheet=worksheet,
        filename_hint=_derive_filename("math", request.metadata),
        metadata=request.metadata or {},
    )


def _build_reading_worksheet(request: ReadingWorksheetRequest) -> WorksheetArtifactPlan:
    worksheet = generate_reading_comprehension_worksheet(
        passage_title=request.passage_title,
        passage=request.passage,
        questions=[question.model_dump() for question in request.questions],
        vocabulary=[entry.model_dump() for entry in request.vocabulary],
        instructions=request.instructions or "Read the passage carefully, then answer the questions and review the vocabulary.",
        title=request.title or "Reading Comprehension",
        metadata=request.metadata or {},
    )
    return WorksheetArtifactPlan(
        kind="readingWorksheet",
        worksheet=worksheet,
        filename_hint=_derive_filename("reading", request.metadata),
        metadata=request.metadata or {},
    )


def build_worksheets_from_requests(resources: ResourceRequests) -> tuple[List[WorksheetArtifactPlan], List[WorksheetRequestError]]:
    """Generate worksheet objects for the provided ResourceRequests."""

    plans: List[WorksheetArtifactPlan] = []
    errors: List[WorksheetRequestError] = []

    if resources.mathWorksheet:
        try:
            plans.append(_build_math_worksheet(resources.mathWorksheet))
        except (ValidationError, ValueError) as exc:
            errors.append(WorksheetRequestError("mathWorksheet", str(exc)))

    if resources.readingWorksheet:
        try:
            plans.append(_build_reading_worksheet(resources.readingWorksheet))
        except (ValidationError, ValueError) as exc:
            errors.append(WorksheetRequestError("readingWorksheet", str(exc)))

    return plans, errors


__all__ = [
    "WorksheetArtifactPlan",
    "WorksheetRequestError",
    "build_worksheets_from_requests",
]
