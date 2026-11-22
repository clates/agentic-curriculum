"""The outline shape: three short options a parent picks from (M6.2).

An outline is cheap: a topic, a short title, a one-line hook and the standards it carries. No
worksheets yet. The three options of a set differ by TOPIC only; they all carry the same
standards, which the curriculum engine chose. The model only frames them (topic, title, hook),
so validation here checks shape, not that ids exist in the DB (the validation gate does that).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

OPTION_IDS = ("a", "b", "c")  # stable, used in job keys such as author:{plan}:{option} (D6)


class Outline(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_id: Literal["a", "b", "c"]
    title: str = Field(min_length=1, max_length=80)
    hook: str = Field(min_length=1, max_length=200)
    topic: str | None = Field(default=None, max_length=60)  # what the week is about
    standard_ids: list[str] = Field(min_length=1)
    event_note: str | None = Field(default=None, max_length=200)
    # What the parent reads (M6.3). Optional so outlines stored before they existed still load.
    activities: str | None = Field(default=None, max_length=300)  # what the child will do
    skills: list[str] = Field(default_factory=list, max_length=6)  # plain-language skills covered
    effort: str | None = Field(default=None, max_length=60)  # time/effort hint

    @model_validator(mode="before")
    @classmethod
    def _drop_legacy(cls, data):
        """Outlines stored before options differed by topic carried a difficulty; ignore it."""
        if isinstance(data, dict) and "difficulty" in data:
            data = {k: v for k, v in data.items() if k != "difficulty"}
        return data

    @field_validator("standard_ids")
    @classmethod
    def _ids_clean(cls, ids: list[str]) -> list[str]:
        if any(not s.strip() for s in ids):
            raise ValueError("standard ids must be non-empty")
        if len(set(ids)) != len(ids):
            raise ValueError("standard ids must be unique within an outline")
        return ids


class OutlineSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    source: Literal["model", "template"] = "model"  # template: built from the vetted topic list
    options: list[Outline] = Field(min_length=3, max_length=3)

    @model_validator(mode="after")
    def _three_distinct_options(self) -> "OutlineSet":
        ids = [o.option_id for o in self.options]
        if sorted(ids) != list(OPTION_IDS):
            raise ValueError("an outline set has exactly options a, b and c")
        return self

    def get(self, option_id: str) -> Outline:
        for option in self.options:
            if option.option_id == option_id:
                return option
        raise KeyError(option_id)
