"""
main.py

FastAPI application for serving student data from curriculum.db
"""

import json
import os
import sys
from datetime import datetime
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from db_utils import get_student_profile
from agent import generate_weekly_plan


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
