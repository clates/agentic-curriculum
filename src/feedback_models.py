"""
Pydantic models for packet feedback API requests and responses.
"""

from pydantic import BaseModel, model_validator


class SubmitFeedbackRequest(BaseModel):
    """Request model for submitting packet feedback.

    v2 (Friday form): ``check_results`` (per-check Got it / Shaky / Missed) or ``quick_rating``,
    never both, plus an optional ``workload`` (-2..2). The v1 fields ``mastery_feedback`` and
    ``quantity_feedback`` keep working and cannot be combined with the v2 evidence fields.
    """

    mastery_feedback: dict[str, str] | None = None
    quantity_feedback: int | None = None
    check_results: dict[str, str] | None = None
    quick_rating: str | None = None
    workload: int | None = None

    @model_validator(mode="after")
    def check_fields(self) -> "SubmitFeedbackRequest":
        if self.check_results is not None and self.quick_rating is not None:
            raise ValueError("Send check_results or quick_rating, not both")
        v2 = self.check_results is not None or self.quick_rating is not None
        if v2 and self.mastery_feedback is not None:
            raise ValueError("mastery_feedback cannot be combined with check_results/quick_rating")
        if self.workload is not None and self.quantity_feedback is not None:
            raise ValueError("Send workload or quantity_feedback, not both")
        if all(
            v is None
            for v in (
                self.mastery_feedback,
                self.quantity_feedback,
                self.check_results,
                self.quick_rating,
                self.workload,
            )
        ):
            raise ValueError(
                "At least one of mastery_feedback, quantity_feedback, check_results, "
                "quick_rating or workload must be provided"
            )
        return self

    @property
    def is_v2(self) -> bool:
        return (
            self.check_results is not None
            or self.quick_rating is not None
            or self.workload is not None
        )


class FeedbackResponse(BaseModel):
    """Response model for packet feedback."""

    packet_id: str
    student_id: str
    completed_at: str
    mastery_feedback: dict[str, str] | None = None
    quantity_feedback: int | None = None
    check_results: dict[str, str] | None = None
    quick_rating: str | None = None
    derived_mastery: dict[str, str] | None = None
    version: int | None = None
