"""
main.py

FastAPI application for serving student data from curriculum.db
"""

from __future__ import annotations
from src.packet_store import (
    get_artifact_for_student,
    get_packet_feedback,
    get_weekly_packet,
    list_packet_artifacts,
    list_weekly_packets,
    save_packet_feedback,
)
from src.agent import generate_weekly_plan
from src.db_utils import (
    create_student,
    delete_student,
    get_student_profile,
    update_student,
    list_all_students,
)
from src.constants import EVALUATION_STATUSES, GRADE_LEVELS, SUBJECTS, get_worksheet_types
from src.feedback_processor import (
    process_mastery_feedback,
    process_quantity_feedback,
    validate_mastery_feedback,
    validate_quantity_feedback,
)
from src.feedback_models import FeedbackResponse, SubmitFeedbackRequest

import json
import logging
import os
import sys
from collections import OrderedDict
from datetime import UTC, datetime
from email.utils import formatdate
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))


logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _project_root_path() -> Path:
    return PROJECT_ROOT if isinstance(PROJECT_ROOT, Path) else Path(PROJECT_ROOT)


def _log_dir() -> Path:
    return _project_root_path() / "logs"


def _sanitize_for_filename(value: str) -> str:
    """Return a filesystem-friendly version of the provided string."""
    if not value:
        return "unknown"
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value)


def _write_weekly_plan_log(log_context: dict) -> None:
    """Persist the request/response payload for a weekly plan call."""
    log_dir = _log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    student_id = log_context.get("request", {}).get("student_id", "")
    safe_student_id = _sanitize_for_filename(student_id)
    log_id = uuid4().hex[:8]
    filename = f"weekly_plan_{safe_student_id}_{timestamp}_{log_id}.json"
    filepath = log_dir / filename
    with open(filepath, "w", encoding="utf-8") as log_file:
        json.dump(log_context, log_file, indent=2)


class PlanRequest(BaseModel):
    """Request model for generating weekly plans."""

    student_id: str
    grade_level: int
    subject: str


class PaginationMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    has_more: bool
    next_page: int | None = Field(default=None, ge=1)


class WeeklyPacketSummary(BaseModel):
    packet_id: str
    student_id: str
    week_of: str
    subject: str
    grade_level: int
    status: str
    worksheet_counts: dict[str, int] = Field(default_factory=dict)
    artifact_count: int = 0
    resource_days: int = 0
    daily_count: int = 0
    updated_at: str


class WeeklyPacketListResponse(BaseModel):
    items: list[WeeklyPacketSummary]
    pagination: PaginationMeta


class WeeklyPacketDetail(BaseModel):
    """Flexible representation of a stored weekly packet."""

    model_config = ConfigDict(extra="allow")


class WorksheetArtifactDownload(BaseModel):
    artifact_id: int
    format: str
    download_url: str
    checksum: str | None = None
    file_size_bytes: int | None = None
    metadata: dict[str, Any] | None = None
    created_at: str


class WorksheetArtifactGroup(BaseModel):
    day_label: str
    resource_kind: str
    artifacts: list[WorksheetArtifactDownload]


class WorksheetArtifactManifest(BaseModel):
    packet_id: str
    artifact_count: int
    items: list[WorksheetArtifactGroup]


class StudentMetadata(BaseModel):
    """Model containing student metadata."""

    name: str
    birthday: str
    avatar_url: str | None = None
    notes: str | None = None


class StudentMetadataPatch(BaseModel):
    """Model for partial updates to student metadata."""

    name: str | None = None
    birthday: str | None = None
    avatar_url: str | None = None
    notes: str | None = None


class CreateStudentRequest(BaseModel):
    """Request model for creating a new student."""

    student_id: str
    metadata: StudentMetadata
    plan_rules: dict[str, Any] = Field(default_factory=dict)


class UpdateStudentRequest(BaseModel):
    """Request model for updating a student."""

    metadata: StudentMetadataPatch | None = None
    plan_rules: dict[str, Any] | None = None


class StudentResponse(BaseModel):
    """Response model for student profile."""

    student_id: str
    progress_blob: str | None = None
    plan_rules_blob: str | None = None
    metadata_blob: str | None = None


class GradeLevelOption(BaseModel):
    """A grade level option with value and label."""

    value: int
    label: str


class SystemOptionsResponse(BaseModel):
    """Response model for system configuration options."""

    subjects: list[str]
    grades: list[GradeLevelOption]
    worksheet_types: list[str]
    statuses: list[str]


@app.get("/")
def read_root():
    """Root endpoint that returns a simple hello message."""
    return {"message": "Hello World"}


@app.get("/system/options", response_model=SystemOptionsResponse)
def get_system_options():
    """
    Return valid configuration options for the frontend.

    Returns a JSON object containing:
    - subjects: List of valid subject names
    - grades: List of grade level options with value and label
    - worksheet_types: List of supported worksheet type keys
    - statuses: List of evaluation status values
    """
    grades = [GradeLevelOption(value=k, label=v) for k, v in GRADE_LEVELS.items()]
    return SystemOptionsResponse(
        subjects=SUBJECTS,
        grades=grades,
        worksheet_types=get_worksheet_types(),
        statuses=EVALUATION_STATUSES,
    )


@app.get("/student/{student_id}")
def read_student(student_id: str):
    """
    Get student profile by student_id.

    Args:
        student_id: The unique identifier for the student

    Returns:
        Student profile data as JSON including metadata_blob

    Raises:
        HTTPException: 404 if student not found
    """
    profile = get_student_profile(student_id)

    if profile is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return profile


@app.get("/students", response_model=list[StudentResponse])
def list_students_endpoint():
    """
    List all student profiles.

    Returns:
        A list of all student profile data
    """
    try:
        students = list_all_students()
        return students
    except Exception as e:
        logger.error(f"Error listing students: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student_endpoint(request: CreateStudentRequest):
    """
    Create a new student profile.

    Args:
        request: CreateStudentRequest containing student_id, metadata, and plan_rules

    Returns:
        The created student profile data

    Raises:
        HTTPException: 400 if student already exists
    """
    try:
        student = create_student(
            student_id=request.student_id,
            metadata=request.metadata.model_dump(),
            plan_rules=request.plan_rules,
        )
        return student
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.put("/student/{student_id}", response_model=StudentResponse)
def update_student_endpoint(student_id: str, request: UpdateStudentRequest):
    """
    Update an existing student profile.

    Args:
        student_id: The unique identifier for the student
        request: UpdateStudentRequest containing optional metadata and plan_rules

    Returns:
        The updated student profile data

    Raises:
        HTTPException: 404 if student not found
    """
    metadata_dict = request.metadata.model_dump(exclude_unset=True) if request.metadata else None
    student = update_student(
        student_id=student_id,
        metadata=metadata_dict,
        plan_rules=request.plan_rules,
    )

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@app.delete("/student/{student_id}", status_code=204)
def delete_student_endpoint(student_id: str):
    """
    Delete a student profile.

    Args:
        student_id: The unique identifier for the student

    Raises:
        HTTPException: 404 if student not found
    """
    deleted = delete_student(student_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Student not found")


@app.post("/generate_weekly_plan")
def create_weekly_plan(request: PlanRequest):
    """
    Generate a weekly lesson plan for a student using LLM.

    Args:
        request: PlanRequest containing student_id, grade_level, and subject

    Returns:
        A complete weekly plan JSON with daily lesson plans

    Raises:
        HTTPException: 400 if there's an error generating the plan
    """
    request_payload = request.dict()
    start_time = datetime.now(UTC)
    log_context = {
        "timestamp_utc": start_time.isoformat(timespec="microseconds") + "Z",
        "request": request_payload,
        "status": "pending",
    }

    try:
        plan = generate_weekly_plan(
            student_id=request.student_id, grade_level=request.grade_level, subject=request.subject
        )
        log_context["response"] = plan
        log_context["status"] = "success"
        return plan
    except ValueError as e:
        log_context["error"] = {"type": type(e).__name__, "message": str(e)}
        log_context["status"] = "client_error"
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        log_context["error"] = {"type": type(e).__name__, "message": str(e)}
        log_context["status"] = "server_error"
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}") from e
    finally:
        duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
        log_context["duration_ms"] = duration_ms
        _write_weekly_plan_log(log_context)


@app.get(
    "/students/{student_id}/weekly-packets",
    response_model=WeeklyPacketListResponse,
)
def list_student_weekly_packets(
    student_id: str,
    week_of: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    """List weekly packets for a student with basic metadata."""

    offset = (page - 1) * page_size
    summaries, has_more = list_weekly_packets(
        student_id,
        limit=page_size,
        offset=offset,
        week_of=week_of,
    )
    next_page = page + 1 if has_more else None
    return {
        "items": summaries,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "has_more": has_more,
            "next_page": next_page,
        },
    }


@app.get(
    "/students/{student_id}/weekly-packets/{packet_id}",
    response_model=WeeklyPacketDetail,
)
def get_student_weekly_packet(
    student_id: str,
    packet_id: str,
    response: Response,
):
    """Return the stored weekly packet payload."""

    packet = get_weekly_packet(student_id, packet_id)
    if packet is None:
        raise HTTPException(status_code=404, detail="Weekly packet not found")

    etag = packet["etag"]
    response.headers["ETag"] = f'"{etag}"'

    updated_at = packet["updated_at"]
    try:
        updated_dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    except ValueError:
        updated_dt = datetime.now(UTC)
    response.headers["Last-Modified"] = formatdate(updated_dt.timestamp(), usegmt=True)
    return packet["payload"]


def _resolve_artifact_path(file_path: str) -> Path:
    root = _project_root_path()
    candidate = Path(file_path)
    if candidate.is_absolute():
        candidate = candidate.resolve()
    else:
        candidate = (root / candidate).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Artifact not found") from e
    return candidate


def _media_type(file_format: str | None) -> str:
    if not file_format:
        return "application/octet-stream"
    normalized = file_format.lower()
    if normalized == "pdf":
        return "application/pdf"
    if normalized in {"png", "image/png"}:
        return "image/png"
    return "application/octet-stream"


def _artifact_headers(artifact: dict[str, Any]) -> dict[str, str]:
    headers = {"Cache-Control": "private, max-age=86400"}
    checksum = artifact.get("checksum")
    etag_value = checksum or f"artifact-{artifact['artifact_id']}"
    headers["ETag"] = f'"{etag_value}"'
    created_at = artifact.get("created_at")
    if created_at:
        try:
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            created_dt = datetime.now(UTC)
        headers["Last-Modified"] = formatdate(created_dt.timestamp(), usegmt=True)
    return headers


@app.get(
    "/students/{student_id}/weekly-packets/{packet_id}/worksheets",
    response_model=WorksheetArtifactManifest,
)
def list_packet_worksheet_manifest(student_id: str, packet_id: str):
    """Return grouped worksheet artifact metadata for a packet."""

    artifacts = list_packet_artifacts(student_id, packet_id)
    if artifacts is None:
        raise HTTPException(status_code=404, detail="Weekly packet not found")

    grouped: OrderedDict[tuple[str, str], dict[str, Any]] = OrderedDict()
    for artifact in artifacts:
        key = (artifact["day_label"], artifact["kind"])
        group = grouped.get(key)
        if group is None:
            group = {
                "day_label": artifact["day_label"],
                "resource_kind": artifact["kind"],
                "artifacts": [],
            }
            grouped[key] = group

        download_url = app.url_path_for(
            "download_worksheet_artifact",
            student_id=student_id,
            artifact_id=str(artifact["artifact_id"]),
        )
        group["artifacts"].append(
            {
                "artifact_id": artifact["artifact_id"],
                "format": artifact["file_format"],
                "download_url": download_url,
                "checksum": artifact.get("checksum"),
                "file_size_bytes": artifact.get("file_size_bytes"),
                "metadata": artifact.get("metadata"),
                "created_at": artifact.get("created_at"),
            }
        )

    return {
        "packet_id": packet_id,
        "artifact_count": len(artifacts),
        "items": list(grouped.values()),
    }


@app.get(
    "/students/{student_id}/worksheet-artifacts/{artifact_id}",
    name="download_worksheet_artifact",
)
def download_worksheet_artifact(student_id: str, artifact_id: int):
    """Stream a worksheet artifact when the student owns it."""

    artifact = get_artifact_for_student(student_id, artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")

    file_path = _resolve_artifact_path(artifact["file_path"])
    if not file_path.exists():
        logger.warning(
            "Worksheet artifact missing",
            extra={"artifact_id": artifact_id, "student_id": student_id, "path": str(file_path)},
        )
        raise HTTPException(status_code=410, detail="Artifact unavailable")

    headers = _artifact_headers(artifact)
    headers["Content-Disposition"] = f'attachment; filename="{file_path.name}"'

    logger.info(
        "worksheet_artifact_download",
        extra={
            "artifact_id": artifact_id,
            "packet_id": artifact.get("packet_id"),
            "student_id": student_id,
            "format": artifact.get("file_format"),
        },
    )

    return FileResponse(
        file_path,
        media_type=_media_type(artifact.get("file_format")),
        filename=file_path.name,
        headers=headers,
    )


@app.post("/students/{student_id}/weekly-packets/{packet_id}/feedback", status_code=204)
def submit_packet_feedback(student_id: str, packet_id: str, request: SubmitFeedbackRequest):
    """
    Submit feedback for a completed weekly packet.

    Args:
        student_id: The student ID
        packet_id: The packet ID
        request: Feedback data with mastery_feedback and quantity_feedback

    Raises:
        HTTPException: 400 for validation errors, 404 if packet not found
    """
    mastery_feedback = request.mastery_feedback
    quantity_feedback = request.quantity_feedback

    # Validate feedback
    try:
        if mastery_feedback:
            validate_mastery_feedback(mastery_feedback)
        if quantity_feedback is not None:
            validate_quantity_feedback(quantity_feedback)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Get current student profile
    profile = get_student_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")

    # Process feedback and update blobs
    feedback_date = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    progress_blob = profile["progress_blob"] or json.dumps(
        {"mastered_standards": [], "developing_standards": []}
    )
    plan_rules_blob = profile["plan_rules_blob"] or json.dumps({})

    if mastery_feedback:
        progress_blob = process_mastery_feedback(progress_blob, mastery_feedback, feedback_date)

    if quantity_feedback is not None:
        plan_rules_blob = process_quantity_feedback(
            plan_rules_blob, quantity_feedback, feedback_date
        )

    plan_rules_payload = json.loads(plan_rules_blob) if quantity_feedback is not None else None
    progress_payload = json.loads(progress_blob) if mastery_feedback else None

    # Update student profile and store raw feedback in packet_feedback
    try:
        update_student(
            student_id=student_id,
            metadata=None,
            plan_rules=plan_rules_payload,
            progress=progress_payload,
        )
        save_packet_feedback(student_id, packet_id, mastery_feedback, quantity_feedback)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get(
    "/students/{student_id}/weekly-packets/{packet_id}/feedback",
    response_model=FeedbackResponse,
)
def get_packet_feedback_endpoint(student_id: str, packet_id: str):
    """
    Retrieve feedback for a weekly packet.

    Args:
        student_id: The student ID
        packet_id: The packet ID

    Returns:
        Feedback data if it exists

    Raises:
        HTTPException: 404 if feedback not found
    """
    feedback = get_packet_feedback(student_id, packet_id)

    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found for this packet")

    return FeedbackResponse(**feedback)
