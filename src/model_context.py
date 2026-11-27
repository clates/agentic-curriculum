"""What the model may know about a child (D9): an explicit allowlist, built in one place.

The hosted app sends the child's FIRST NAME, grade, reading level, interests and the parent's
free-text notes to the model, and nothing else: never a last name, email, birthday, id or
avatar. ``build_model_context`` reads only the keys named here, so a new profile field can never
leak into a prompt by accident. Every prompt that mentions the child must be built from a
``ModelStudentContext``, not from the raw profile.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

MAX_NOTES_CHARS = 600
MAX_INTERESTS = 8
MAX_INTEREST_CHARS = 40
MAX_READING_CHARS = 200

GRADE_LABELS = {0: "Kindergarten"} | {n: f"Grade {n}" for n in range(1, 13)}


def _label(grade: int) -> str:
    return GRADE_LABELS.get(grade, f"Grade {grade}")


@dataclass(frozen=True)
class ModelStudentContext:
    first_name: str
    grade: int
    reading_level: str | None = None
    interests: tuple[str, ...] = field(default_factory=tuple)
    parent_notes: str | None = None
    math_grade: int | None = None
    la_grade: int | None = None

    @property
    def non_math_grade(self) -> int:
        """The grade every subject except math is planned at: the language arts grade, else the
        single grade."""
        return self.grade if self.la_grade is None else self.la_grade

    def grade_for(self, subject: str) -> int:
        """The grade the planner uses for a subject: math has its own, the rest follow language arts."""
        if subject != "Math":
            return self.non_math_grade
        return self.grade if self.math_grade is None else self.math_grade

    @property
    def has_subject_grades(self) -> bool:
        return self.math_grade is not None or self.la_grade is not None

    @property
    def grade_label(self) -> str:
        return _label(self.grade)

    def prompt_lines(self) -> str:
        """The child's facts as prompt text. This is the only text about the child that leaves."""
        lines = [f"First name: {self.first_name}"]
        if self.has_subject_grades:  # one line per subject grade, never a third "Grade:" line
            lines.append(f"Math grade: {_label(self.grade_for('Math'))}")
            lines.append(f"Language arts grade: {_label(self.non_math_grade)}")
        else:
            lines.append(f"Grade: {self.grade_label}")
        if self.reading_level:
            lines.append(f"Reading level: {self.reading_level}")
        if self.interests:
            lines.append("Interests: " + ", ".join(self.interests))
        if self.parent_notes:
            lines.append(f"Parent notes: {self.parent_notes}")
        return "\n".join(lines)


def _blob(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    try:
        loaded = json.loads(value or "{}")
    except (TypeError, ValueError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _subject_grade(raw: Any) -> int | None:
    ok = isinstance(raw, int) and not isinstance(raw, bool) and 0 <= raw <= 12
    return raw if ok else None


_SPACES = re.compile(r"[\s\x00-\x1f\x7f-\x9f]+")


def first_name(full_name: str | None) -> str:
    """The first word of a parent-typed name, at most 40 characters. Every run of whitespace or
    control characters counts as one space, so a name can't add lines to a prompt."""
    name = _SPACES.sub(" ", full_name or "").strip()
    return name.split(" ")[0][:40] if name else "Your child"


def grade_from_birthday(birthday: str | None, today: date) -> int | None:
    """US-style placement: age on 1 September of the current school year, minus 5 (5 = K)."""
    try:
        born = date.fromisoformat((birthday or "")[:10])
    except ValueError:
        return None
    start_year = today.year if today.month >= 8 else today.year - 1
    cutoff = date(start_year, 9, 1)
    age = cutoff.year - born.year - ((cutoff.month, cutoff.day) < (born.month, born.day))
    return max(0, min(12, age - 5))


def _interests(raw: Any) -> tuple[str, ...]:
    if isinstance(raw, str):
        raw = [part for part in raw.replace(";", ",").split(",")]
    if not isinstance(raw, (list, tuple)):
        return ()
    cleaned = [" ".join(str(x).split())[:MAX_INTEREST_CHARS] for x in raw]
    return tuple(x for x in cleaned if x)[:MAX_INTERESTS]


def build_model_context(
    metadata_blob: Any,
    plan_rules_blob: Any = None,
    *,
    today: date | None = None,
    fallback_grade: int | None = None,
) -> ModelStudentContext:
    """Allowlist the profile down to what the model may see.

    Grade: ``grade_level`` in the profile, else ``fallback_grade`` (the last finished week),
    else worked out from the birthday (the birthday itself is never copied).
    """
    meta, rules = _blob(metadata_blob), _blob(plan_rules_blob)
    today = today or date.today()
    grade = None
    for source in (meta, rules):
        if isinstance(source.get("grade_level"), int):
            grade = source["grade_level"]
            break
    if grade is None:
        grade = fallback_grade
    if grade is None:
        grade = grade_from_birthday(meta.get("birthday"), today)
    notes = " ".join(
        part
        for part in (
            " ".join(str(rules.get("parent_notes") or "").split()),
            " ".join(str(meta.get("notes") or "").split()),
        )
        if part
    )
    reading = " ".join(str(meta.get("reading_level") or rules.get("reading_level") or "").split())
    return ModelStudentContext(
        first_name=first_name(meta.get("name")),
        grade=max(0, min(12, grade if grade is not None else 0)),
        reading_level=reading[:MAX_READING_CHARS] or None,
        interests=_interests(meta.get("interests") or rules.get("interests")),
        parent_notes=notes[:MAX_NOTES_CHARS] or None,
        math_grade=_subject_grade(meta.get("math_grade")),
        la_grade=_subject_grade(meta.get("la_grade")),
    )
