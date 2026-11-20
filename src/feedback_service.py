"""Feedback API v2 service (M5.3b): one transactional apply for a packet's Friday feedback.

A submission carries EITHER ``check_results`` (per-check Got it / Shaky / Missed) OR a
``quick_rating`` (smooth / mixed / rough), never both, plus an optional ``workload`` (-2..2).
Saving always replaces the packet's previous submission: the old mastery and workload effects are
reverted and the new ones applied, inside one SQLite transaction together with the raw row.
An exact repeat changes nothing and reports ``changed=False`` (the caller must not re-trigger
plan generation).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, Callable

try:
    from . import packet_store
    from .check_mastery import map_check_results, normalize_result
    from .feedback_processor import (
        process_mastery_feedback,
        process_quantity_feedback,
        revert_mastery_feedback,
        reverse_quantity_feedback,
        validate_quantity_feedback,
    )
except ImportError:  # imported as a top-level module (src/ on sys.path)
    import packet_store
    from check_mastery import map_check_results, normalize_result
    from feedback_processor import (
        process_mastery_feedback,
        process_quantity_feedback,
        revert_mastery_feedback,
        reverse_quantity_feedback,
        validate_quantity_feedback,
    )

QUICK_RATINGS = ("smooth", "mixed", "rough")
# Without per-check evidence a quick rating can never CREDIT mastery. A rough week marks the
# packet's standards as needing work, a mixed week as shaky, a smooth week changes nothing.
_QUICK_TO_MASTERY = {"smooth": None, "mixed": "DEVELOPING", "rough": "STRUGGLING"}


class FeedbackError(ValueError):
    """Bad submission (maps to HTTP 400)."""


@dataclass
class FeedbackOutcome:
    changed: bool
    version: int
    derived_mastery: dict[str, str]


def _prep_checks_from_payload(payload: dict[str, Any]) -> list[Any]:
    return [SimpleNamespace(**c) for c in (payload.get("prep_checks") or [])]


def load_prep_checks(student_id: str, packet_id: str) -> list[Any]:
    """Prep checks (objects with ``id`` and ``standard_id``) for a stored packet.

    Interface for M2.6: once storage for structured weeks lands, ``packet_store`` exposes
    ``get_prep_checks(student_id, packet_id)`` backed by the derived prep_checks index and it is
    used here. Until then, fall back to a ``prep_checks`` list inside the stored payload.
    """
    getter: Callable[..., list[Any]] | None = getattr(packet_store, "get_prep_checks", None)
    if getter is not None:
        return list(getter(student_id, packet_id))
    packet = packet_store.get_weekly_packet(student_id, packet_id)
    return _prep_checks_from_payload((packet or {}).get("payload") or {})


def _packet_standard_ids(student_id: str, packet_id: str, checks: list[Any]) -> list[str]:
    ids = {c.standard_id for c in checks}
    if not ids:
        packet = packet_store.get_weekly_packet(student_id, packet_id) or {}
        for day in (packet.get("payload") or {}).get("daily_plan", []):
            for std in day.get("standards") or []:
                sid = std.get("standard_id") if isinstance(std, dict) else std
                if sid:
                    ids.add(sid)
    return sorted(ids)


def derive_mastery(
    student_id: str,
    packet_id: str,
    check_results: dict[str, str] | None,
    quick_rating: str | None,
) -> tuple[dict[str, str] | None, dict[str, str]]:
    """Return (normalized raw check_results or None, derived {standard_id: state})."""
    if check_results and quick_rating:
        raise FeedbackError("Send check_results or quick_rating, not both")
    checks = load_prep_checks(student_id, packet_id)
    if check_results:
        if not checks:
            raise FeedbackError("This packet has no checks to record results against")
        try:
            clean = {k: normalize_result(v) for k, v in check_results.items()}
            return clean, map_check_results(checks, clean)
        except ValueError as exc:
            raise FeedbackError(str(exc)) from exc
    if quick_rating:
        if quick_rating not in QUICK_RATINGS:
            raise FeedbackError(f"quick_rating must be one of {QUICK_RATINGS}")
        state = _QUICK_TO_MASTERY[quick_rating]
        if state is None:
            return None, {}
        return None, {sid: state for sid in _packet_standard_ids(student_id, packet_id, checks)}
    return None, {}


def apply_feedback(
    student_id: str,
    packet_id: str,
    *,
    check_results: dict[str, str] | None = None,
    quick_rating: str | None = None,
    workload: int | None = None,
) -> FeedbackOutcome:
    """Record (or edit) a packet's feedback atomically. Raises FeedbackError / ValueError."""
    if check_results is None and quick_rating is None and workload is None:
        raise FeedbackError("Nothing to record")
    if workload is not None:
        try:
            validate_quantity_feedback(workload)
        except ValueError as exc:
            raise FeedbackError(str(exc)) from exc
    packet_store.ensure_schema()
    raw_results, derived = derive_mastery(student_id, packet_id, check_results, quick_rating)
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    conn = packet_store._get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        if not packet_store._packet_exists(conn, student_id, packet_id):
            raise ValueError(f"Packet {packet_id} not found for student {student_id}")
        student = conn.execute(
            "SELECT progress_blob, plan_rules_blob FROM student_profiles WHERE student_id = ?",
            (student_id,),
        ).fetchone()
        if student is None:
            raise ValueError(f"Student {student_id} not found")
        old = conn.execute(
            "SELECT check_results_json, quick_rating, quantity_feedback, version "
            "FROM packet_feedback WHERE packet_id = ? AND student_id = ?",
            (packet_id, student_id),
        ).fetchone()

        if old is not None:
            same = (
                json.loads(old["check_results_json"] or "null") == raw_results
                and old["quick_rating"] == quick_rating
                and old["quantity_feedback"] == workload
            )
            if same:
                conn.execute("ROLLBACK")
                return FeedbackOutcome(False, old["version"], derived)

        progress = student["progress_blob"] or json.dumps(
            {"mastered_standards": [], "developing_standards": []}
        )
        plan_rules = student["plan_rules_blob"] or json.dumps({})
        old_workload = old["quantity_feedback"] if old is not None else None

        progress = revert_mastery_feedback(progress, packet_id)
        if derived:
            progress = process_mastery_feedback(progress, derived, now, packet_id=packet_id)
        if old_workload is not None:
            plan_rules = reverse_quantity_feedback(plan_rules, old_workload)
        if workload is not None:
            plan_rules = process_quantity_feedback(plan_rules, workload, now)

        conn.execute(
            "UPDATE student_profiles SET progress_blob = ?, plan_rules_blob = ? "
            "WHERE student_id = ?",
            (progress, plan_rules, student_id),
        )
        conn.execute(
            """
            INSERT INTO packet_feedback (
                packet_id, student_id, completed_at, mastery_feedback_blob, quantity_feedback,
                check_results_json, quick_rating, derived_mastery_json, version, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            ON CONFLICT(family_id, packet_id) DO UPDATE SET
                completed_at = excluded.completed_at,
                mastery_feedback_blob = excluded.mastery_feedback_blob,
                quantity_feedback = excluded.quantity_feedback,
                check_results_json = excluded.check_results_json,
                quick_rating = excluded.quick_rating,
                derived_mastery_json = excluded.derived_mastery_json,
                version = packet_feedback.version + 1,
                updated_at = excluded.updated_at
            """,
            (
                packet_id,
                student_id,
                now,
                json.dumps(derived) if derived else None,
                workload,
                json.dumps(raw_results) if raw_results else None,
                quick_rating,
                json.dumps(derived) if derived else None,
                now,
            ),
        )
        version = conn.execute(
            "SELECT version FROM packet_feedback WHERE packet_id = ? AND student_id = ?",
            (packet_id, student_id),
        ).fetchone()[0]
        conn.execute("COMMIT")
        return FeedbackOutcome(True, version, derived)
    except BaseException:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()
