"""
main.py

FastAPI application for serving student data from curriculum.db
"""

from __future__ import annotations
from packet_store import (
    get_artifact_for_student,
    get_weekly_packet,
    list_packet_artifacts,
    list_weekly_packets,
)
from agent import generate_weekly_plan
from db_utils import get_student_profile

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
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))


logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]


app = FastAPI()


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
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
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


@app.get("/")
def read_root():
    """Root endpoint that returns a simple hello message."""
    return {"message": "Hello World"}


@app.get("/student/{student_id}")
def read_student(student_id: str):
    """
    Get student profile by student_id.

    Args:
        student_id: The unique identifier for the student

    Returns:
        Student profile data as JSON

    Raises:
        HTTPException: 404 if student not found
    """
    profile = get_student_profile(student_id)

    if profile is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return profile


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
    start_time = datetime.utcnow()
    log_context = {
        "timestamp_utc": start_time.isoformat(timespec="microseconds") + "Z",
        "request": request_payload,
        "status": "pending"
    }

    try:
        plan = generate_weekly_plan(
            student_id=request.student_id,
            grade_level=request.grade_level,
            subject=request.subject
        )
        log_context["response"] = plan
        log_context["status"] = "success"
        return plan
    except ValueError as e:
        log_context["error"] = {"type": type(e).__name__, "message": str(e)}
        log_context["status"] = "client_error"
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_context["error"] = {"type": type(e).__name__, "message": str(e)}
        log_context["status"] = "server_error"
        raise HTTPException(
            status_code=500, detail=f"Error generating plan: {str(e)}")
    finally:
        duration_ms = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000)
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
    response.headers["Last-Modified"] = formatdate(
        updated_dt.timestamp(), usegmt=True)
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
    except ValueError:
        raise HTTPException(status_code=404, detail="Artifact not found")
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
            created_dt = datetime.fromisoformat(
                created_at.replace("Z", "+00:00"))
        except ValueError:
            created_dt = datetime.now(UTC)
        headers["Last-Modified"] = formatdate(
            created_dt.timestamp(), usegmt=True)
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
            extra={"artifact_id": artifact_id,
                   "student_id": student_id, "path": str(file_path)},
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
