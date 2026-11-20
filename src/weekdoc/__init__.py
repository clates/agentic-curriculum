"""Structured weeks (WeekDoc): models, hosted-kind registry, storage, rendering."""

from .models import (  # noqa: F401
    SCHEMA_VERSION,
    STUDENT_NAME_TOKEN,
    Answer,
    Day,
    GuideBlock,
    GuideDay,
    GuideSummary,
    PrepCheck,
    TeacherGuide,
    WeekDoc,
    Worksheet,
    week_json_schema,
)
