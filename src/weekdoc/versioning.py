"""Schema versioning and migrate-on-read for stored weeks (M2.7).

Stored documents keep the ``schema_version`` they were written with. Reading goes through
``load_week()``, which upgrades old documents one version at a time with the functions in
``MIGRATIONS`` and rejects documents newer than this code (never guess at a future shape).

To change the schema: bump ``SCHEMA_VERSION`` in models.py and add ``MIGRATIONS[old] = fn``
where ``fn`` takes a version-``old`` dict and returns a version-``old + 1`` dict. Migrations
must not mutate their input.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Mapping

from .models import SCHEMA_VERSION, WeekDoc

Migration = Callable[[dict[str, Any]], dict[str, Any]]

#: from_version -> function producing from_version + 1. Empty: v1 is the first version.
MIGRATIONS: dict[int, Migration] = {}


class WeekVersionError(ValueError):
    """The stored document's schema_version cannot be loaded by this code."""


def migrate_week_data(
    raw: dict[str, Any],
    migrations: Mapping[int, Migration] | None = None,
    current: int | None = None,
) -> dict[str, Any]:
    """Return ``raw`` upgraded to ``current``. Raises WeekVersionError if it cannot be."""
    migrations = MIGRATIONS if migrations is None else migrations
    current = SCHEMA_VERSION if current is None else current  # read at call time
    version = raw.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise WeekVersionError(f"missing or invalid schema_version: {version!r}")
    if version > current:
        raise WeekVersionError(
            f"week schema_version {version} is newer than this code understands ({current}); "
            "upgrade the app before opening it"
        )
    data = dict(raw)
    while version < current:
        step = migrations.get(version)
        if step is None:
            raise WeekVersionError(f"no migration from schema_version {version} to {version + 1}")
        data = step(dict(data))
        version += 1
        if data.get("schema_version") != version:
            raise WeekVersionError(
                f"migration {version - 1}->{version} must set schema_version to {version}"
            )
    return data


def load_week(raw: dict[str, Any] | str | bytes) -> WeekDoc:
    """Parse a stored week (dict or JSON text), migrating older versions on read."""
    if isinstance(raw, (str, bytes)):
        raw = json.loads(raw)
    if not isinstance(raw, dict):
        raise WeekVersionError("a stored week must be a JSON object")
    return WeekDoc.model_validate(migrate_week_data(raw))
