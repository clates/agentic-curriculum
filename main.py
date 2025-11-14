"""
main.py

FastAPI application for serving student data from curriculum.db
"""

from fastapi import FastAPI, HTTPException
from db_utils import get_student_profile


app = FastAPI()


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
