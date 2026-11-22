"""Production week author: student context + topic + real standards -> a validated WeekDoc."""

from .context import ModelStudentContext, Tenant  # noqa: F401
from .pipeline import (  # noqa: F401
    AuthorResult,
    RunRecord,
    StepRecord,
    author_week,
)
