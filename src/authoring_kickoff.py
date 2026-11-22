"""The hook between 'the parent picked' and 'the week gets written' (M6.4).

The real week author and the job queue (M8.2) are separate work. Until they land, picking an
option calls ``request_authoring``, whose default only RECORDS the intent (a log line plus a
bounded in-process list for tests and local debugging). Nothing here writes a week.

Wiring it to the job queue later is a one-function replacement, no change to the pick endpoint:

    def enqueue_author_week(family_id, student_id, plan_id, option):
        jobs.enqueue(
            kind="author_week",
            family_id=family_id,
            idempotency_key=f"author:{plan_id}:{option}",
            payload={"student_id": student_id, "plan_id": plan_id, "option": option},
        )

    set_authoring_requester(enqueue_author_week)

The pick endpoint calls the hook on the first pick AND on an exact repeat of it, so a crash
between "pick recorded" and "job enqueued" heals on the parent's next tap. That is only safe
because the hook must be idempotent: the job queue's unique idempotency key makes a repeat a
no-op, and the default recorder below de-duplicates on the same key.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable

logger = logging.getLogger(__name__)

AuthoringRequester = Callable[[str, str, str, str], None]

_lock = threading.Lock()
_recorded: dict[str, tuple[str, str, str, str]] = {}  # idempotency key -> the request
MAX_RECORDED = 500


def idempotency_key(plan_id: str, option: str) -> str:
    return f"author:{plan_id}:{option}"


def record_authoring_request(family_id: str, student_id: str, plan_id: str, option: str) -> None:
    """Default requester: remember that authoring was asked for, once per (plan, option)."""
    key = idempotency_key(plan_id, option)
    with _lock:
        if key in _recorded:
            return
        if len(_recorded) >= MAX_RECORDED:
            _recorded.pop(next(iter(_recorded)))
        _recorded[key] = (family_id, student_id, plan_id, option)
    logger.info("authoring requested key=%s family=%s", key, family_id)


_requester: AuthoringRequester = record_authoring_request


def set_authoring_requester(requester: AuthoringRequester | None) -> None:
    """Replace the hook (the job queue wiring); ``None`` restores the recording default."""
    global _requester
    _requester = requester or record_authoring_request


def request_authoring(family_id: str, student_id: str, plan_id: str, option: str) -> None:
    """Ask for the week to be written for this pick. Must be idempotent."""
    _requester(family_id, student_id, plan_id, option)


def recorded_requests() -> list[tuple[str, str, str, str]]:
    with _lock:
        return list(_recorded.values())


def clear_recorded() -> None:
    with _lock:
        _recorded.clear()
