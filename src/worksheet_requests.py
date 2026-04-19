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
    from .resource_models import (
        MathWorksheetRequest,
        ReadingWorksheetRequest,
        ResourceRequests,
    )
except ImportError:  # Fallback for execution without package context
    CURRENT_DIR = os.path.dirname(__file__)
    if CURRENT_DIR not in sys.path:
        sys.path.insert(0, CURRENT_DIR)
    from worksheets import (  # type: ignore
        generate_two_operand_math_worksheet,
        ReadingWorksheet,
        Worksheet,
    )
    from resource_models import (  # type: ignore
        MathWorksheetRequest,
        ReadingWorksheetRequest,
        ResourceRequests,
    )


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
        filename_hint=_derive_filename("math", request.metadata),
        metadata=request.metadata or {},
    )


def _build_reading_worksheet(request: ReadingWorksheetRequest) -> WorksheetArtifactPlan:
    """Reading uses the HTML renderer; the Pillow worksheet object is not built."""
    data = request.model_dump()
    return WorksheetArtifactPlan(
        kind="readingWorksheet",
        worksheet=None,
        html_data=data,
        filename_hint=_derive_filename("reading", request.metadata),
        metadata=request.metadata or {},
    )


def _build_html_plan(kind: str, request: Any) -> WorksheetArtifactPlan:
    """Generic builder for any HTML-rendered worksheet type."""
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


# Map resource field name → builder function
_HTML_BUILDERS = {
    "featureMatrixWorksheet": _build_html_plan,
    "treeMapWorksheet": _build_html_plan,
    "oddOneOutWorksheet": _build_html_plan,
    "matchingWorksheet": _build_html_plan,
    "causeEffectWorksheet": _build_html_plan,
    "frayerModelWorksheet": _build_html_plan,
    "wordSortWorksheet": _build_html_plan,
    "writingScaffoldWorksheet": _build_html_plan,
    "tChartWorksheet": _build_html_plan,
}


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

    # HTML-rendered: reading
    if resources.readingWorksheet:
        try:
            plans.append(_build_reading_worksheet(resources.readingWorksheet))
        except (ValidationError, ValueError) as exc:
            errors.append(WorksheetRequestError("readingWorksheet", str(exc)))

    # HTML-rendered: all other types
    for field_name, builder in _HTML_BUILDERS.items():
        request = getattr(resources, field_name, None)
        if request is not None:
            try:
                plans.append(builder(field_name, request))
            except (ValidationError, ValueError) as exc:
                errors.append(WorksheetRequestError(field_name, str(exc)))

    return plans, errors


__all__ = [
    "WorksheetArtifactPlan",
    "WorksheetRequestError",
    "build_worksheets_from_requests",
]
