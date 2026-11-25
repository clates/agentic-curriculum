"""Glue between worksheet request models and worksheet generators."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Any, List

from pydantic import ValidationError

try:  # Package-relative imports when available
    from .worksheets import (
        generate_two_operand_math_worksheet,
        ReadingWorksheet,
        Worksheet,
    )
    from .resource_models import MathWorksheetRequest, ResourceRequests
except ImportError:  # Fallback for execution without package context
    CURRENT_DIR = os.path.dirname(__file__)
    if CURRENT_DIR not in sys.path:
        sys.path.insert(0, CURRENT_DIR)
    from worksheets import (  # type: ignore
        generate_two_operand_math_worksheet,
        ReadingWorksheet,
        Worksheet,
    )
    from resource_models import MathWorksheetRequest, ResourceRequests  # type: ignore


@dataclass
class WorksheetArtifactPlan:
    """Represents a worksheet ready for rendering plus metadata."""

    kind: str
    filename_hint: str
    metadata: dict
    # Set for Pillow-rendered types (mathWorksheet, readingWorksheet fallback)
    worksheet: Worksheet | ReadingWorksheet | None = None
    # Set for HTML-rendered types; passed directly to worksheet_html_renderer
    html_data: dict | None = None


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
        html_data=request.model_dump(),
        filename_hint=_derive_filename("math", request.metadata),
        metadata=request.metadata or {},
    )


def _build_html_plan(kind: str, request: Any) -> WorksheetArtifactPlan:
    """Plan for an HTML-rendered type: the request payload goes straight to the renderer."""
    data = request.model_dump()
    metadata = data.get("metadata") or {}
    short_name = kind.replace("Worksheet", "").lower()
    return WorksheetArtifactPlan(
        kind=kind,
        worksheet=None,
        html_data=data,
        filename_hint=_derive_filename(short_name, metadata),
        metadata=metadata,
    )


# Resource fields rendered via HTML, in build order.
_HTML_KINDS = (
    "readingWorksheet",
    "featureMatrixWorksheet",
    "treeMapWorksheet",
    "oddOneOutWorksheet",
    "matchingWorksheet",
    "causeEffectWorksheet",
    "frayerModelWorksheet",
    "wordSortWorksheet",
    "writingScaffoldWorksheet",
    "tChartWorksheet",
    # Ported from PIL → HTML (PR #113)
    "vennDiagramWorksheet",
    "handwritingWorksheet",
    "pixelCopyWorksheet",
    "alphabetWorksheet",
    "sequencingWorksheet",
    "fillInBlankWorksheet",
    "storyMapWorksheet",
    "numberLineWorksheet",
    "labeledDiagramWorksheet",
    "twoOperandWorksheet",
)


def build_worksheets_from_requests(
    resources: ResourceRequests,
) -> tuple[List[WorksheetArtifactPlan], List[WorksheetRequestError]]:
    """Generate worksheet artifact plans for the provided ResourceRequests."""

    plans: List[WorksheetArtifactPlan] = []
    errors: List[WorksheetRequestError] = []

    # Pillow-rendered
    if resources.mathWorksheet:
        try:
            plans.append(_build_math_worksheet(resources.mathWorksheet))
        except (ValidationError, ValueError) as exc:
            errors.append(WorksheetRequestError("mathWorksheet", str(exc)))

    for kind in _HTML_KINDS:
        request = getattr(resources, kind, None)
        if request is not None:
            try:
                plans.append(_build_html_plan(kind, request))
            except (ValidationError, ValueError) as exc:
                errors.append(WorksheetRequestError(kind, str(exc)))

    return plans, errors


__all__ = [
    "WorksheetArtifactPlan",
    "WorksheetRequestError",
    "build_worksheets_from_requests",
]
