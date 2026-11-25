"""
main.py

FastAPI application for serving student data from curriculum.db
"""

from __future__ import annotations

import sqlite3
import subprocess

from agent import generate_weekly_plan
from packet_store import (
    get_artifact_for_student,
    get_packet_feedback,
    get_weekly_packet,
    list_packet_artifacts,
    list_weekly_packets,
    save_packet_feedback,
)
from trio_generator import generate_trio_for_student
from db_utils import (
    get_db_path,
    create_student,
    delete_student,
    get_student_profile,
    list_students,
    update_student,
)
from constants import EVALUATION_STATUSES, GRADE_LEVELS, SUBJECTS, get_worksheet_types
from feedback_processor import (
    process_mastery_feedback,
    process_quantity_feedback,
    reverse_quantity_feedback,
    validate_mastery_feedback,
    validate_quantity_feedback,
)
from feedback_models import FeedbackResponse, SubmitFeedbackRequest
from feedback_service import FeedbackError, apply_feedback
from curriculum_graph import load_from_db
from migrations import apply_migrations
from auth.web import (
    AuthBodyLimit,
    auth_gate,
    auth_required,
    current_family,
    invalid_request_handler,
    router as auth_router,
)
from tenancy import new_student_id, owned_student_id, student_in_family
from this_week import this_week_cards, first_name_of
import pick_service
from prep_check_cards import check_cards
from progress_summary import build_progress_summary
from week_store import get_week
from print_week import PlanNotReady, mark_printed, print_info
from week_plan import PlanNotFound
import loop_integration
from admin_api import router as admin_api_router
from loop_admin import router as loop_admin_router
from weekdoc.render import render_packet, render_prep_sheet, render_teacher_guide
from worksheet_html_renderer import build_print_packet_html

import json
import logging
import os
import sys
from contextlib import asynccontextmanager, contextmanager
from functools import lru_cache
from datetime import UTC, datetime
from email.utils import formatdate
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, ConfigDict, Field

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))


logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    """Run pending schema migrations before serving requests."""
    apply_migrations(get_db_path())
    yield


# Login (see docs/how-to/turn-on-login.md). The gate protects every route except auth.web.PUBLIC_PATHS and
# does nothing unless AUTH_REQUIRED is on. The interactive docs are not routes the gate can see,
# so they are simply not served when login is required.
_docs_off = {"docs_url": None, "redoc_url": None, "openapi_url": None} if auth_required() else {}
app = FastAPI(lifespan=_lifespan, dependencies=[Depends(auth_gate)], **_docs_off)
app.include_router(auth_router)
app.include_router(loop_admin_router)
app.include_router(admin_api_router)
app.add_middleware(AuthBodyLimit)
app.add_exception_handler(RequestValidationError, invalid_request_handler)


@contextmanager
def _local_db():
    """A connection to the app DB with foreign keys on, closed afterwards."""
    conn = sqlite3.connect(get_db_path())
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    finally:
        conn.close()


def _log_dir() -> Path:
    return PROJECT_ROOT / "logs"


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
    has_feedback: bool = False
    feedback_completed_at: str | None = None


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
    interests: list[str] | None = None  # what the child likes; themes the week topics


class StudentMetadataPatch(BaseModel):
    """Model for partial updates to student metadata."""

    name: str | None = None
    birthday: str | None = None
    avatar_url: str | None = None
    notes: str | None = None
    interests: list[str] | None = None


class CreateStudentRequest(BaseModel):
    """Request model for creating a new student."""

    student_id: str | None = None  # honoured only with login off; otherwise server-generated
    metadata: StudentMetadata
    plan_rules: dict[str, Any] = Field(default_factory=dict)


class UpdateStudentRequest(BaseModel):
    """Request model for updating a student."""

    metadata: StudentMetadataPatch | None = None
    plan_rules: dict[str, Any] | None = None
    progress: dict[str, Any] | None = None


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


@app.get("/health")
def health_check():
    """Health check endpoint for container healthchecks and backend readiness polling."""
    return {"status": "ok"}


def _resolve_git_sha() -> str:
    """Return GIT_SHA from the environment, else `git rev-parse HEAD`, else "unknown"."""
    sha = os.environ.get("GIT_SHA", "").strip()
    if sha and sha != "unknown":
        return sha
    return _git_head_sha()


@lru_cache(maxsize=1)
def _git_head_sha() -> str:
    """The `git rev-parse` fallback, run once (the public /version route must stay cheap)."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        candidate = out.stdout.strip()
        if out.returncode == 0 and len(candidate) == 40:
            return candidate
    except Exception:
        pass
    return "unknown"


@app.get("/version")
def get_version():
    """Report which build is running (set via GIT_SHA/BUILD_TIME/RELEASE_TAG at image build)."""
    sha = _resolve_git_sha()
    return {
        "sha": sha,
        "short_sha": sha[:7] if sha != "unknown" else "unknown",
        "build_time": os.environ.get("BUILD_TIME") or None,
        "release_tag": os.environ.get("RELEASE_TAG") or None,
    }


@app.get("/system/options", response_model=SystemOptionsResponse)
def get_system_options():
    """Return valid configuration options (subjects, grades, worksheet types, statuses)."""
    return SystemOptionsResponse(
        subjects=SUBJECTS,
        grades=[GradeLevelOption(value=k, label=v) for k, v in GRADE_LEVELS.items()],
        worksheet_types=get_worksheet_types(),
        statuses=EVALUATION_STATUSES,
    )


@app.get("/student/{student_id}")
def read_student(student_id: str = Depends(owned_student_id)):
    """Get student profile by student_id."""
    profile = get_student_profile(student_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return profile


@app.get("/this-week")
def read_this_week(family: str = Depends(current_family)):
    """One card per child with the single next step for the week (M10.4)."""
    with _local_db() as conn:
        return this_week_cards(conn, family, datetime.now(UTC).date())


@app.get("/students/{student_id}/weekly-packets/{packet_id}/checks")
def read_packet_checks(
    packet_id: str,
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
):
    """The parent's check-by-check list for a finished week (empty if it has no structured checks)."""
    profile = get_student_profile(student_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Student not found")
    if get_weekly_packet(student_id, packet_id, family_id=family) is None:
        raise HTTPException(status_code=404, detail="Packet not found")
    first = first_name_of(profile.get("metadata_blob"))
    return {"checks": check_cards(student_id, packet_id, first, family)}


@app.get("/students/{student_id}/weekly-packets/{packet_id}/print-info")
def read_print_info(
    packet_id: str,
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
):
    """Which documents this week can print (structured weeks: packet, guide, prep; legacy: packet)."""
    packet = get_weekly_packet(student_id, packet_id, family_id=family)
    if packet is None:
        raise HTTPException(status_code=404, detail="Packet not found")
    week = get_week(student_id, packet_id, family_id=family)
    return print_info(student_id, packet_id, packet, week)


@app.post("/students/{student_id}/week-plans/{plan_id}/printed")
def mark_week_printed(
    plan_id: str,
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
):
    """The parent says the week is printed: ready -> printed. Repeating it is harmless (M10.7)."""
    try:
        with _local_db() as conn:
            return mark_printed(conn, family, student_id, plan_id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Week not found") from None
    except PlanNotReady as exc:
        raise HTTPException(
            status_code=409,
            detail=f"This week is not ready to print yet (it is {exc.status}).",
        ) from None


@app.get("/students", response_model=list[StudentResponse])
def get_students(family: str = Depends(current_family)):
    """The family's student profiles."""
    return list_students(family)


@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student_endpoint(request: CreateStudentRequest, family: str = Depends(current_family)):
    """Create a new student profile. With login on (or no id given) the server picks the id."""
    client_id = None if auth_required() else request.student_id
    try:
        return create_student(
            student_id=client_id or new_student_id(),
            metadata=request.metadata.model_dump(),
            plan_rules=request.plan_rules,
            family_id=family,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.put("/student/{student_id}", response_model=StudentResponse)
def update_student_endpoint(
    request: UpdateStudentRequest, student_id: str = Depends(owned_student_id)
):
    """Update an existing student profile."""
    metadata_dict = request.metadata.model_dump(exclude_unset=True) if request.metadata else None
    student = update_student(
        student_id=student_id,
        metadata=metadata_dict,
        plan_rules=request.plan_rules,
        progress=request.progress,
    )

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@app.delete("/student/{student_id}", status_code=204)
def delete_student_endpoint(student_id: str = Depends(owned_student_id)):
    """Delete a student profile."""
    try:
        deleted = delete_student(student_id)
    except sqlite3.OperationalError as e:
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable — please retry",
        ) from e

    if not deleted:
        raise HTTPException(status_code=404, detail="Student not found")


@app.post("/generate_weekly_plan")
def create_weekly_plan(request: PlanRequest, family: str = Depends(current_family)):
    """Generate a weekly lesson plan for a student using LLM."""
    with _local_db() as conn:
        if not student_in_family(conn, family, request.student_id):
            raise HTTPException(status_code=404, detail="Student not found")
    request_payload = request.model_dump()
    start_time = datetime.now(UTC)
    log_context = {
        "timestamp_utc": start_time.isoformat(timespec="microseconds") + "Z",
        "request": request_payload,
        "status": "pending",
    }

    try:
        plan = generate_weekly_plan(
            student_id=request.student_id,
            grade_level=request.grade_level,
            subject=request.subject,
            family_id=family,
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
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
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
        family_id=family,
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
    packet_id: str,
    response: Response,
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
):
    """Return the stored weekly packet payload."""
    packet = get_weekly_packet(student_id, packet_id, family_id=family)
    if packet is None:
        raise HTTPException(status_code=404, detail="Weekly packet not found")
    response.headers["ETag"] = f'"{packet["etag"]}"'
    response.headers["Last-Modified"] = _http_date(packet["updated_at"])
    return packet["payload"]


def _http_date(iso_timestamp: str) -> str:
    """An HTTP date for a stored ISO timestamp (now, if it does not parse)."""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    except ValueError:
        dt = datetime.now(UTC)
    return formatdate(dt.timestamp(), usegmt=True)


def _resolve_artifact_path(file_path: str) -> Path:
    # An absolute file_path replaces PROJECT_ROOT in the join; either way it must stay inside.
    candidate = (PROJECT_ROOT / file_path).resolve()
    try:
        candidate.relative_to(PROJECT_ROOT)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Artifact not found") from e
    return candidate


_MEDIA_TYPES = {
    "pdf": "application/pdf",
    "png": "image/png",
    "image/png": "image/png",
    "html": "text/html",
    "text/html": "text/html",
}


def _media_type(file_format: str | None) -> str:
    return _MEDIA_TYPES.get((file_format or "").lower(), "application/octet-stream")


def _artifact_headers(artifact: dict[str, Any]) -> dict[str, str]:
    etag_value = artifact.get("checksum") or f"artifact-{artifact['artifact_id']}"
    headers = {"Cache-Control": "private, max-age=86400", "ETag": f'"{etag_value}"'}
    if artifact.get("created_at"):
        headers["Last-Modified"] = _http_date(artifact["created_at"])
    return headers


@app.get(
    "/students/{student_id}/weekly-packets/{packet_id}/worksheets",
    response_model=WorksheetArtifactManifest,
)
def list_packet_worksheet_manifest(
    packet_id: str,
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
):
    """Return grouped worksheet artifact metadata for a packet."""
    artifacts = list_packet_artifacts(student_id, packet_id, family_id=family)
    if artifacts is None:
        raise HTTPException(status_code=404, detail="Weekly packet not found")

    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for artifact in artifacts:
        group = grouped.setdefault(
            (artifact["day_label"], artifact["kind"]),
            {
                "day_label": artifact["day_label"],
                "resource_kind": artifact["kind"],
                "artifacts": [],
            },
        )
        group["artifacts"].append(
            {
                "artifact_id": artifact["artifact_id"],
                "format": artifact["file_format"],
                "download_url": app.url_path_for(
                    "download_worksheet_artifact",
                    student_id=student_id,
                    artifact_id=str(artifact["artifact_id"]),
                ),
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
def download_worksheet_artifact(
    artifact_id: int,
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
):
    """Stream a worksheet artifact when the student owns it."""
    artifact = get_artifact_for_student(student_id, artifact_id, family_id=family)
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
    is_html = (artifact.get("file_format") or "").lower() in {"html", "text/html"}
    disposition = "inline" if is_html else "attachment"
    headers["Content-Disposition"] = f'{disposition}; filename="{file_path.name}"'

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


def _student_first_name(student_id: str) -> str | None:
    """First name only (D9): the name is substituted into print output, nothing else is."""
    profile = get_student_profile(student_id)
    try:
        name = (json.loads(profile["metadata_blob"] or "{}").get("name") or "").strip()
    except (TypeError, ValueError, KeyError, AttributeError):
        return None
    return name.split()[0] if name else None


@app.get(
    "/students/{student_id}/weekly-packets/{packet_id}/print",
    response_class=HTMLResponse,
    name="print_weekly_packet",
)
def print_weekly_packet(
    packet_id: str,
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
    doc: Literal["packet", "guide", "prep"] | None = Query(
        None,
        description="Structured weeks only: packet (default), guide or prep, rendered on demand.",
    ),
):
    """
    Return a single printable HTML document containing all HTML worksheets for
    the packet, ordered Mon–Fri.  Opening this URL in a browser and hitting
    Ctrl+P (or the auto-triggered print dialog) produces a single PDF printout.

    Structured weeks (stored as a WeekDoc) are rendered on demand; ``?doc=`` picks the student
    packet, the teacher guide or the parent prep sheet. Legacy packets ignore nothing: asking
    them for ``guide`` or ``prep`` is a 404.
    """
    packet = get_weekly_packet(student_id, packet_id, family_id=family)
    if packet is None:
        raise HTTPException(status_code=404, detail="Packet not found")

    week = get_week(student_id, packet_id, family_id=family)
    if week is not None:
        renderers = {
            "packet": render_packet,
            "guide": render_teacher_guide,
            "prep": render_prep_sheet,
        }
        return HTMLResponse(
            content=renderers[doc or "packet"](week, _student_first_name(student_id))
        )
    if doc not in (None, "packet"):
        raise HTTPException(status_code=404, detail="This packet has no structured week")

    artifacts = list_packet_artifacts(student_id, packet_id, family_id=family)
    if artifacts is None:
        raise HTTPException(status_code=404, detail="Packet not found")

    import re as _re

    pages: list[tuple[str, str]] = []
    for artifact in artifacts:
        if (artifact.get("file_format") or "").lower() != "html":
            continue
        artifact_path = _resolve_artifact_path(artifact["file_path"])
        if not artifact_path.exists():
            continue
        try:
            fragment = artifact_path.read_text(encoding="utf-8")
            body_match = _re.search(
                r"<body[^>]*>(.*)</body>", fragment, _re.DOTALL | _re.IGNORECASE
            )
            if body_match:
                fragment = body_match.group(1)
            pages.append((artifact.get("day_label", ""), fragment))
        except OSError:
            pass

    if not pages:
        raise HTTPException(
            status_code=404,
            detail="No HTML worksheets found for this packet. Re-generate the plan to produce HTML worksheets.",
        )

    subject = packet.get("subject", "")
    week_of = packet.get("week_of", "")
    title = f"{subject} — Week of {week_of}" if subject and week_of else packet_id
    return HTMLResponse(content=build_print_packet_html(pages, title))


def _submit_feedback_v2(
    family: str,
    student_id: str,
    packet_id: str,
    request: SubmitFeedbackRequest,
    background_tasks: BackgroundTasks,
) -> None:
    """v2: check_results or quick_rating (+ workload), applied transactionally and idempotently."""
    if get_weekly_packet(student_id, packet_id, family_id=family) is None:
        raise HTTPException(status_code=404, detail="Packet not found")
    if not get_student_profile(student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    try:
        outcome = apply_feedback(
            student_id,
            packet_id,
            check_results=request.check_results,
            quick_rating=request.quick_rating,
            workload=request.workload,
            family_id=family,
        )
    except FeedbackError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    if outcome.changed:  # an exact repeat must not re-trigger plan generation
        background_tasks.add_task(generate_trio_for_student, student_id, family)
        background_tasks.add_task(loop_integration.on_feedback, family, student_id)


@app.post("/students/{student_id}/weekly-packets/{packet_id}/feedback", status_code=204)
def submit_packet_feedback(
    packet_id: str,
    request: SubmitFeedbackRequest,
    background_tasks: BackgroundTasks,
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
):
    """Submit feedback for a completed weekly packet."""
    if request.is_v2:
        _submit_feedback_v2(family, student_id, packet_id, request, background_tasks)
        return

    mastery_feedback = request.mastery_feedback
    quantity_feedback = request.quantity_feedback
    try:
        if mastery_feedback:
            validate_mastery_feedback(mastery_feedback)
        if quantity_feedback is not None:
            validate_quantity_feedback(quantity_feedback)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if get_weekly_packet(student_id, packet_id, family_id=family) is None:
        raise HTTPException(status_code=404, detail="Packet not found")
    profile = get_student_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")

    existing_feedback = get_packet_feedback(student_id, packet_id, family_id=family)
    feedback_date = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    progress_blob = profile["progress_blob"] or json.dumps(
        {"mastered_standards": [], "developing_standards": []}
    )
    plan_rules_blob = profile["plan_rules_blob"] or json.dumps({})

    # When updating, reverse the old quantity effect before applying the new one
    if existing_feedback and existing_feedback.get("quantity_feedback") is not None:
        plan_rules_blob = reverse_quantity_feedback(
            plan_rules_blob, existing_feedback["quantity_feedback"]
        )

    if mastery_feedback:
        progress_blob = process_mastery_feedback(
            progress_blob, mastery_feedback, feedback_date, packet_id=packet_id
        )

    if quantity_feedback is not None:
        plan_rules_blob = process_quantity_feedback(
            plan_rules_blob, quantity_feedback, feedback_date
        )

    plan_rules_payload = json.loads(plan_rules_blob) if quantity_feedback is not None else None
    progress_payload = json.loads(progress_blob) if mastery_feedback else None
    try:
        update_student(
            student_id=student_id,
            metadata=None,
            plan_rules=plan_rules_payload,
            progress=progress_payload,
        )
        save_packet_feedback(
            student_id, packet_id, mastery_feedback, quantity_feedback, family_id=family
        )
        background_tasks.add_task(generate_trio_for_student, student_id, family)
        background_tasks.add_task(loop_integration.on_feedback, family, student_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get(
    "/students/{student_id}/weekly-packets/{packet_id}/feedback",
    response_model=FeedbackResponse,
)
def get_packet_feedback_endpoint(
    packet_id: str,
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
):
    """Retrieve feedback for a weekly packet."""
    feedback = get_packet_feedback(student_id, packet_id, family_id=family)
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found for this packet")
    return FeedbackResponse(**feedback)


@app.get("/curriculum/graph/{subject}")
def get_curriculum_graph(subject: str, prune: bool = False):
    """Retrieve the full structural dependency graph for a subject."""
    return load_from_db(get_db_path(), subject).export_for_visualization(prune=prune)


@app.get("/students/{student_id}/progress-map/{subject}")
def get_student_progress_map(
    subject: str, student_id: str = Depends(owned_student_id), prune: bool = True
):
    """Retrieve the curriculum graph with student mastery data overlay."""
    profile = get_student_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    mastered = json.loads(profile["progress_blob"] or "{}").get("mastered_standards", [])
    return load_from_db(get_db_path(), subject).export_for_visualization(mastered, prune=prune)


def _standards_lookup(standard_ids: set[str]) -> dict[str, dict[str, Any]]:
    """Subject and description for the given standard ids (missing ids are simply absent)."""
    if not standard_ids:
        return {}
    ids = sorted(standard_ids)
    out: dict[str, dict[str, Any]] = {}
    conn = sqlite3.connect(get_db_path())
    try:
        for i in range(0, len(ids), 500):
            chunk = ids[i : i + 500]
            marks = ",".join("?" * len(chunk))
            for sid, subject, description in conn.execute(
                f"SELECT standard_id, subject, description FROM standards "  # noqa: S608
                f"WHERE standard_id IN ({marks})",
                chunk,
            ):
                out[sid] = {"subject": subject, "description": description}
    except sqlite3.OperationalError:
        return out  # no standards table (minimal DB): fall back to generic skill names
    finally:
        conn.close()
    return out


@app.get("/students/{student_id}/progress-summary")
def get_student_progress_summary(student_id: str = Depends(owned_student_id)):
    """How a child is doing, in plain words: solid, shaky, needs work, due for review."""
    profile = get_student_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    progress = json.loads(profile["progress_blob"] or "{}")
    metadata = json.loads(profile.get("metadata_blob") or "{}")
    ids = set(progress.get("mastered_standards", [])) | set(
        progress.get("developing_standards", [])
    )
    ids |= set((progress.get("standard_metadata") or {}).keys())
    return build_progress_summary(metadata.get("name"), progress, _standards_lookup(ids))


# --- Pick one of three (M6.4) and fresh ideas (M6.6) -------------------------------------------
loop_integration.install()  # LOOP_JOBS_ENABLED=1: a pick queues the author job


class PickRequest(BaseModel):
    """Choose one of the three ideas. ``plan_id`` (optional) guards against a stale screen."""

    option: Literal["a", "b", "c"]
    plan_id: str | None = None


class RegenerateRequest(BaseModel):
    plan_id: str | None = None


def _week_plan_call(action):
    """Run ``action(conn)``, turning refusals into plain-language errors."""
    from llm import LLMError

    try:
        with _local_db() as conn:
            conn.execute("PRAGMA busy_timeout = 5000")
            return action(conn)
    except pick_service.PickError as exc:
        raise HTTPException(
            status_code=exc.status, detail={"code": exc.code, "message": exc.message}
        ) from exc
    except LLMError as exc:
        logger.warning("outline generation failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=502,
            detail={
                "code": "outline_failed",
                "message": "We couldn’t write new ideas just now. Nothing was lost. "
                "Please try again.",
            },
        ) from exc


@app.get("/students/{student_id}/week-plan")
def get_week_plan(
    student_id: str = Depends(owned_student_id), family: str = Depends(current_family)
):
    """The child's current week plan with its three ideas (no standard ids)."""
    return _week_plan_call(lambda c: pick_service.get_current(c, family, student_id))


@app.post("/students/{student_id}/week-plan/pick")
def pick_week_idea(
    request: PickRequest,
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
):
    """Pick one idea: awaiting_pick -> authoring, and ask for the week to be written.

    The same pick twice is a no-op (200). A different pick once writing has started is 409.
    """
    return _week_plan_call(
        lambda c: pick_service.pick(c, family, student_id, request.option, request.plan_id)
    )


@app.post("/students/{student_id}/week-plan/regenerate")
def regenerate_week_ideas(
    request: RegenerateRequest | None = None,
    student_id: str = Depends(owned_student_id),
    family: str = Depends(current_family),
):
    """Fresh ideas (expired or open set), at most two per week plan; 409 at the cap."""
    plan_id = request.plan_id if request else None
    return _week_plan_call(lambda c: pick_service.regenerate(c, family, student_id, plan_id))
