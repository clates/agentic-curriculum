"""The one time source for auth. Tests replace ``now`` (see tests/test_auth_*.py)."""

from __future__ import annotations

import time
from collections.abc import Callable

_source: Callable[[], float] = time.time


def now() -> float:
    return _source()


def set_source(source: Callable[[], float] | None) -> None:
    global _source
    _source = source or time.time
