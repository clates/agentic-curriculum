"""What the model may know about a child (D9): an explicit allowlist, built in one place.

The hosted app sends the child's FIRST NAME, grade, reading level, interests and the parent's
free-text notes to the model, and nothing else: never a last name, email, birthday, id or
avatar. ``build_model_context`` reads only the keys named here, so a new profile field can never
leak into a prompt by accident. Every prompt that mentions the child must be built from a
``ModelStudentContext``, not from the raw profile.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from typing import Any

MAX_NOTES_CHARS = 600
MAX_INTERESTS = 8
MAX_INTEREST_CHARS = 40
MAX_READING_CHARS = 200

GRADE_LABELS = {0: "Kindergarten"} | {n: f"Grade {n}" for n in range(1, 13)}


@dataclass(frozen=True)
class ModelStudentContext:
    first_name: str
    grade: int
    reading_level: str | None = None
    interests: tuple[str, ...] = field(default_factory=tuple)
    parent_notes: str | None = None

    @property
    def grade_label(self) -> str:
        return GRADE_LABELS.get(self.grade, f"Grade {self.grade}")

    def prompt_lines(self) -> str:
        """The child's facts as prompt text. This is the only text about the child that leaves."""
        lines = [f"First name: {self.first_name}", f"Grade: {self.grade_label}"]
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


def first_name(full_name: str | None) -> str:
    name = (full_name or "").strip()
    return name.split(" ")[0] if name else "Your child"


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
    )
