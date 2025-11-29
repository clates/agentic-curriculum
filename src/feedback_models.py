"""
Pydantic models for packet feedback API requests and responses.
"""

from pydantic import BaseModel
from typing import Dict


class SubmitFeedbackRequest(BaseModel):
    """Request model for submitting packet feedback."""

    mastery_feedback: Dict[str, str] | None = None
    quantity_feedback: int | None = None


class FeedbackResponse(BaseModel):
    """Response model for packet feedback."""

    packet_id: str
    student_id: str
    completed_at: str
    mastery_feedback: Dict[str, str] | None = None
    quantity_feedback: int | None = None
