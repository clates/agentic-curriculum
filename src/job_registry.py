"""Handler registry for the job queue (M8.2): ``@handler("outline")`` maps a job kind to code.

A handler is ``fn(ctx: JobContext) -> None``. Returning means success; raising means "retry me"
(the worker applies backoff and eventually dead-letters). Handlers must be idempotent: a job can
run twice (a worker may die after the work but before it records success).

The shipped stubs (``job_handlers_stub``) register with ``stub=True``. A real handler registered
for the same kind replaces the stub silently; two real handlers for one kind is an error.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Callable

try:
    from .jobs import Job, connect  # type: ignore
except ImportError:
    from jobs import Job, connect  # type: ignore


@dataclass
class JobContext:
    job: Job
    db_path: str
    heartbeat: Callable[[], bool]  # extend the lease; False = lease lost, stop work

    def connect(self) -> sqlite3.Connection:
        """A fresh connection for the handler's own work (own it, close it)."""
        return connect(self.db_path)


Handler = Callable[[JobContext], None]
_HANDLERS: dict[str, tuple[Handler, bool]] = {}


class DuplicateHandler(RuntimeError):
    pass


def handler(kind: str, *, stub: bool = False) -> Callable[[Handler], Handler]:
    def deco(fn: Handler) -> Handler:
        existing = _HANDLERS.get(kind)
        if existing is not None:
            _, existing_is_stub = existing
            if stub:
                if not existing_is_stub:
                    return fn  # a real handler already won; the stub stays out of the way
            elif not existing_is_stub:
                raise DuplicateHandler(f"two real handlers registered for job kind {kind!r}")
        _HANDLERS[kind] = (fn, stub)
        return fn

    return deco


def get_handler(kind: str) -> Handler | None:
    entry = _HANDLERS.get(kind)
    return entry[0] if entry else None


def is_stub(kind: str) -> bool:
    entry = _HANDLERS.get(kind)
    return bool(entry and entry[1])


def kinds() -> list[str]:
    return sorted(_HANDLERS)


def clear() -> None:
    """Test helper."""
    _HANDLERS.clear()
