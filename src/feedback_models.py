"""
Pydantic models for packet feedback API requests and responses.
"""

from pydantic import BaseModel, model_validator


class SubmitFeedbackRequest(BaseModel):
    """Request model for submitting packet feedback."""

    mastery_feedback: dict[str, str] | None = None
    quantity_feedback: int | None = None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "SubmitFeedbackRequest":
        if self.mastery_feedback is None and self.quantity_feedback is None:
            raise ValueError(
                "At least one of mastery_feedback or quantity_feedback must be provided"
            )
        return self


class FeedbackResponse(BaseModel):
    """Response model for packet feedback."""

    packet_id: str
    student_id: str
    completed_at: str
    mastery_feedback: dict[str, str] | None = None
    quantity_feedback: int | None = None