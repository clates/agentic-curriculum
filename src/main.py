"""
main.py

FastAPI application for serving student data from curriculum.db
"""

import json
import os
import sys
from datetime import UTC, datetime
from email.utils import formatdate
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field, ConfigDict

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from db_utils import get_student_profile
from agent import generate_weekly_plan
from packet_store import get_weekly_packet, list_weekly_packets


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")


app = FastAPI()


def _sanitize_for_filename(value: str) -> str:
    """Return a filesystem-friendly version of the provided string."""
    if not value:
        return "unknown"
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value)


def _write_weekly_plan_log(log_context: dict) -> None:
    """Persist the request/response payload for a weekly plan call."""
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    student_id = log_context.get("request", {}).get("student_id", "")
    safe_student_id = _sanitize_for_filename(student_id)
    log_id = uuid4().hex[:8]
    filename = f"weekly_plan_{safe_student_id}_{timestamp}_{log_id}.json"
    filepath = os.path.join(LOG_DIR, filename)
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
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}")
    finally:
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
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
