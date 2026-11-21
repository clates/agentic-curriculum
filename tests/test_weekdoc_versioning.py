"""Schema versioning + migrate-on-read (M2.7)."""

from __future__ import annotations

import json

import pytest

from src.weekdoc import WeekDoc, WeekVersionError, load_week, migrate_week_data
from tests.weekdoc_fixtures import minimal_week


def test_load_current_version_from_dict_and_json_text():
    assert isinstance(load_week(minimal_week()), WeekDoc)
    assert load_week(json.dumps(minimal_week())).title == "Tiny Week"


def test_newer_than_code_is_rejected():
    data = minimal_week()
    data["schema_version"] = 99
    with pytest.raises(WeekVersionError, match="newer than this code"):
        load_week(data)


@pytest.mark.parametrize("bad", [None, 0, -1, "1", True, 1.5])
def test_missing_or_invalid_version_is_rejected(bad):
    data = minimal_week()
    data["schema_version"] = bad
    with pytest.raises(WeekVersionError, match="invalid schema_version"):
        load_week(data)
    data.pop("schema_version")
    with pytest.raises(WeekVersionError):
        load_week(data)


def test_older_version_is_upgraded_step_by_step_without_mutating_input():
    old = {"schema_version": 1, "name": "legacy"}
    seen = []

    def m1(d):
        seen.append(1)
        out = dict(d, schema_version=2)
        out["title"] = out.pop("name")
        return out

    def m2(d):
        seen.append(2)
        return dict(d, schema_version=3, theme="t")

    out = migrate_week_data(old, migrations={1: m1, 2: m2}, current=3)
    assert seen == [1, 2]
    assert out == {"schema_version": 3, "title": "legacy", "theme": "t"}
    assert old == {"schema_version": 1, "name": "legacy"}


def test_missing_migration_step_is_an_error():
    with pytest.raises(WeekVersionError, match="no migration from schema_version 1"):
        migrate_week_data({"schema_version": 1}, migrations={}, current=2)


def test_migration_must_bump_the_version():
    with pytest.raises(WeekVersionError, match="must set schema_version"):
        migrate_week_data({"schema_version": 1}, migrations={1: lambda d: d}, current=2)


def test_non_object_is_rejected():
    with pytest.raises(WeekVersionError, match="JSON object"):
        load_week("[1, 2]")
