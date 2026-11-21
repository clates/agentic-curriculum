"""Hosted-kind registry: which worksheet kinds a hosted week may use (M2.2a).

Each registered kind has a typed data model (the renderer's exact field names) and an
enumerator that lists the addressable items on the page (questions, blanks, slots), so
answer keys and gates can refer to ``item_ref`` strings instead of guessing at positions.

A kind with no enumerator must carry a documented ``waiver`` saying why (for example a
narration block that asks nothing). The meta-test in tests/test_weekdoc_kinds.py fails if a
kind has neither.

Item refs are dotted paths into the worksheet's ``data`` (``questions.0``, ``pairs.2.effect``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict


class UnknownKindError(ValueError):
    """Raised for a worksheet kind that is not in HOSTED_KINDS. Never silently skipped."""


@dataclass(frozen=True)
class ItemRef:
    """One addressable item on a worksheet."""

    ref: str  # dotted path into data, e.g. "questions.0"
    prompt: str  # what is being asked, for gates and answer-key display


Enumerator = Callable[[BaseModel], list[ItemRef]]


class KindData(BaseModel):
    """Base for typed worksheet data: strict, so a misspelled field fails loudly."""

    model_config = ConfigDict(extra="forbid")


@dataclass(frozen=True)
class HostedKind:
    kind: str
    model: type[KindData]
    enumerate: Enumerator | None = None
    waiver: str | None = None

    def __post_init__(self) -> None:
        if (self.enumerate is None) == (self.waiver is None):
            raise ValueError(f"{self.kind}: provide exactly one of enumerate or waiver")


HOSTED_KINDS: dict[str, HostedKind] = {}


def register(
    kind: str,
    model: type[KindData],
    enumerate: Enumerator | None = None,  # noqa: A002 - mirrors the dataclass field
    waiver: str | None = None,
) -> HostedKind:
    if kind in HOSTED_KINDS:
        raise ValueError(f"kind {kind!r} is already registered")
    entry = HostedKind(kind, model, enumerate, waiver)
    HOSTED_KINDS[kind] = entry
    return entry


def get_kind(kind: str) -> HostedKind:
    try:
        return HOSTED_KINDS[kind]
    except KeyError:
        known = ", ".join(sorted(HOSTED_KINDS))
        raise UnknownKindError(f"unknown worksheet kind {kind!r}; hosted kinds: {known}") from None


def parse_data(kind: str, data: dict[str, Any]) -> BaseModel:
    """Validate ``data`` against the kind's model (raises UnknownKindError / ValidationError)."""
    return get_kind(kind).model.model_validate(data)


def item_refs(kind: str, data: dict[str, Any]) -> list[ItemRef]:
    """List the addressable items for a worksheet. Unknown kinds raise."""
    entry = get_kind(kind)
    parsed = entry.model.model_validate(data)  # typing is enforced even for waived kinds
    return [] if entry.enumerate is None else entry.enumerate(parsed)


# ── Narration blocks ────────────────────────────────────────────────────────


class StoryPanelData(KindData):
    who: str = ""
    text: str


register(
    "storyPanel",
    StoryPanelData,
    waiver="Narrator beat; it asks nothing and has no answer slot.",
)
