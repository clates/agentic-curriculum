"""Hosted-kind registry (M2.2a)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.weekdoc import HOSTED_KINDS, UnknownKindError, WeekDoc, item_refs
from src.weekdoc.kinds import HostedKind, KindData, register
from tests.weekdoc_fixtures import minimal_week


def test_unknown_kind_raises_from_item_refs():
    with pytest.raises(UnknownKindError, match="notAKind"):
        item_refs("notAKind", {"x": 1})


def test_unknown_kind_fails_week_validation():
    data = minimal_week()
    data["days"][0]["worksheets"][0]["kind"] = "notAKind"
    with pytest.raises(ValidationError, match="unknown worksheet kind"):
        WeekDoc.model_validate(data)


def test_story_panel_is_registered_with_a_documented_waiver():
    entry = HOSTED_KINDS["storyPanel"]
    assert entry.waiver and entry.enumerate is None
    assert item_refs("storyPanel", {"text": "Once upon a time"}) == []


def test_typed_data_rejects_misspelled_fields():
    data = minimal_week()
    data["days"][0]["worksheets"][0]["data"] = {"txt": "oops"}
    with pytest.raises(ValidationError):
        WeekDoc.model_validate(data)
    # the envelope only checks structure; typing comes from the registry via item_refs
    data["days"][0]["worksheets"][0]["data"] = {"text": "ok"}
    WeekDoc.model_validate(data)


def test_answer_with_unknown_item_ref_is_rejected():
    data = minimal_week()
    data["days"][0]["worksheets"][0]["answers"] = [{"item_ref": "questions.0", "answer": "x"}]
    with pytest.raises(ValidationError, match="unknown item_ref"):
        WeekDoc.model_validate(data)


def test_every_registered_kind_has_an_enumerator_or_a_waiver():
    for name, entry in HOSTED_KINDS.items():
        assert isinstance(entry, HostedKind) and entry.kind == name
        assert (entry.enumerate is None) != (entry.waiver is None), name


def test_registration_requires_enumerator_or_waiver_and_rejects_duplicates():
    class D(KindData):
        x: int = 0

    with pytest.raises(ValueError, match="exactly one"):
        register("tmpKind", D)
    with pytest.raises(ValueError, match="already registered"):
        register("storyPanel", D, waiver="dup")
