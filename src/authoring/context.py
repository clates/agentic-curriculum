"""Who the author may know about: the model-facing student allowlist, and the tenant (D2, D9).

``ModelStudentContext`` is the ONLY description of a child that ever reaches a prompt: first
name, grade, reading level, interests and the parent's free-text notes. It rejects every other
field, so a last name, email, birthday or id cannot be added by accident; ``from_profile`` picks
the allowlisted keys out of a larger record and ignores the rest.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

_NAME_RE = re.compile(r"^[^\W\d_][^\W\d_ '’.-]*(?:[ '’.-][^\W\d_]+)*$")
Short = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


@dataclass(frozen=True)
class Tenant:
    """Stand-in for the app's tenant object (D2): every row carries ``family_id``."""

    family_id: str


class ModelStudentContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)
    ]
    grade: int = Field(ge=0, le=12, description="0 = kindergarten")
    reading_level: Short
    interests: list[Short] = Field(default_factory=list, max_length=12)
    parent_notes: Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)] = ""

    @field_validator("grade", mode="before")
    @classmethod
    def _grade(cls, v: Any) -> Any:
        if isinstance(v, str) and v.strip().lower() in {"k", "kindergarten"}:
            return 0
        return int(v) if isinstance(v, str) and v.strip().isdigit() else v

    @field_validator("first_name")
    @classmethod
    def _first_name(cls, v: str) -> str:
        if not _NAME_RE.match(v) or "@" in v:
            raise ValueError("first_name must be a plain first name (letters only)")
        return v

    @property
    def grade_label(self) -> str:
        return "K" if self.grade == 0 else str(self.grade)

    @classmethod
    def from_profile(cls, profile: dict[str, Any]) -> "ModelStudentContext":
        """Pick the allowlisted keys from a larger record; everything else is dropped."""
        keys = ("first_name", "grade", "reading_level", "interests", "parent_notes")
        return cls(**{k: profile[k] for k in keys if k in profile})

    def prompt_json(self) -> dict[str, Any]:
        return {
            "first_name": self.first_name,
            "grade": self.grade_label,
            "reading_level": self.reading_level,
            "interests": self.interests,
            "parent_notes": self.parent_notes,
        }
