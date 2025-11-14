"""
main.py

FastAPI application for serving student data from curriculum.db
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db_utils import get_student_profile
from agent import generate_weekly_plan


app = FastAPI()


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
    try:
        plan = generate_weekly_plan(
            student_id=request.student_id,
            grade_level=request.grade_level,
            subject=request.subject
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}")
