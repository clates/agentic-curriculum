"""Structured weeks (WeekDoc): models, hosted-kind registry, storage, rendering."""

from .kinds import HOSTED_KINDS, ItemRef, UnknownKindError, item_refs  # noqa: F401
from . import kinds_comprehension  # noqa: F401  (registers kinds on import)
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
from .versioning import (
    MIGRATIONS,
    WeekVersionError,
    load_week,
    migrate_week_data,
)  # noqa: F401, E402
