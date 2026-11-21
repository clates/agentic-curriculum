"""Persistence helpers for weekly packets, daily lessons, and worksheet artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:  # Prefer package-relative import when available
    from .db_utils import DB_FILE  # type: ignore
    from .migrations import apply_migrations  # type: ignore
except ImportError:  # Fallback for direct script execution
    sys.path.insert(0, os.path.dirname(__file__))
    from db_utils import DB_FILE  # type: ignore
    from migrations import apply_migrations  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
READY_STATUS = "ready"

_SCHEMA_INITIALIZED: str | None = None


def _utc_now() -> str:
    """Return a UTC timestamp suitable for SQLite text columns."""
    stamp = datetime.now(UTC).isoformat(timespec="seconds")
    if stamp.endswith("+00:00"):
        return stamp[:-6] + "Z"
    return stamp


def _get_connection() -> sqlite3.Connection:
    Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_schema() -> None:
    """Bring the database schema up to date (runs pending numbered migrations once)."""
    global _SCHEMA_INITIALIZED
    if _SCHEMA_INITIALIZED == DB_FILE:
        return

    apply_migrations(DB_FILE)
    _SCHEMA_INITIALIZED = DB_FILE


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _build_summary(weekly_plan: Mapping[str, Any]) -> dict[str, Any]:
    worksheet_counts: dict[str, int] = {}
    artifact_count = 0
    resource_days = 0

    for day in weekly_plan.get("daily_plan", []):
        resources = day.get("resources") or {}
        if resources:
            resource_days += 1
        for kind, payload in resources.items():
            artifacts = payload.get("artifacts") or []
            count = worksheet_counts.get(kind, 0) + len(artifacts)
            worksheet_counts[kind] = count
            artifact_count += len(artifacts)

    return {
        "daily_count": len(weekly_plan.get("daily_plan", [])),
        "resource_days": resource_days,
        "worksheet_counts": worksheet_counts,
        "artifact_count": artifact_count,
    }


def _insert_weekly_packet(
    conn: sqlite3.Connection,
    weekly_plan: Mapping[str, Any],
    status: str,
) -> None:
    now = _utc_now()
    summary = _build_summary(weekly_plan)
    payload_json = _json(weekly_plan)
    summary_json = _json(summary)

    conn.execute(
        """
        INSERT INTO weekly_packets (
            packet_id,
            student_id,
            grade_level,
            subject,
            week_of,
            status,
            weekly_overview,
            summary_json,
            payload_json,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(packet_id) DO UPDATE SET
            student_id = excluded.student_id,
            grade_level = excluded.grade_level,
            subject = excluded.subject,
            week_of = excluded.week_of,
            status = excluded.status,
            weekly_overview = excluded.weekly_overview,
            summary_json = excluded.summary_json,
            payload_json = excluded.payload_json,
            updated_at = excluded.updated_at
        """,
        (
            weekly_plan.get("plan_id"),
            weekly_plan.get("student_id"),
            weekly_plan.get("grade_level"),
            weekly_plan.get("subject"),
            weekly_plan.get("week_of"),
            status,
            weekly_plan.get("weekly_overview"),
            summary_json,
            payload_json,
            now,
            now,
        ),
    )


def _persist_daily_lessons(
    conn: sqlite3.Connection,
    packet_id: str,
    daily_plan: Iterable[Mapping[str, Any]],
) -> None:
    for day in daily_plan:
        day_label = day.get("day") or ""
        cursor = conn.execute(
            """
            INSERT INTO daily_lessons (
                packet_id,
                day_label,
                focus,
                standards_json,
                lesson_plan_json,
                resources_json,
                worksheet_plans_json,
                resource_errors_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                packet_id,
                day_label,
                day.get("focus"),
                _json(day.get("standards")),
                _json(day.get("lesson_plan")),
                _json(day.get("resources")),
                _json(day.get("worksheet_plans")),
                _json(day.get("resource_errors")),
                _utc_now(),
            ),
        )
        daily_lesson_id = cursor.lastrowid
        if daily_lesson_id is None:  # pragma: no cover - sqlite guarantees an id for inserts
            raise RuntimeError("Failed to persist daily lesson row")
        _persist_artifacts(conn, packet_id, daily_lesson_id, day_label, day.get("resources"))


def _persist_artifacts(
    conn: sqlite3.Connection,
    packet_id: str,
    daily_lesson_id: int,
    day_label: str,
    resources: Mapping[str, Any] | None,
) -> None:
    if not resources:
        return

    for kind, payload in resources.items():
        artifacts = payload.get("artifacts") or []
        for artifact in artifacts:
            metadata = {
                key: value
                for key, value in artifact.items()
                if key not in {"type", "path", "sha256", "size_bytes"}
            }
            conn.execute(
                """
                INSERT INTO worksheet_artifacts (
                    packet_id,
                    daily_lesson_id,
                    day_label,
                    kind,
                    file_format,
                    file_path,
                    checksum,
                    file_size_bytes,
                    metadata_json,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    packet_id,
                    daily_lesson_id,
                    day_label,
                    kind,
                    artifact.get("type"),
                    artifact.get("path"),
                    artifact.get("sha256"),
                    artifact.get("size_bytes"),
                    _json(metadata or None),
                    _utc_now(),
                ),
            )


def save_weekly_packet(
    weekly_plan: Mapping[str, Any],
    status: str = READY_STATUS,
) -> None:
    """Persist a generated weekly packet and its related rows in one transaction."""
    ensure_schema()

    packet_id = weekly_plan.get("plan_id")
    if not packet_id:
        raise ValueError("weekly_plan must include plan_id")

    with _get_connection() as conn:
        _insert_weekly_packet(conn, weekly_plan, status)
        conn.execute("DELETE FROM daily_lessons WHERE packet_id = ?", (packet_id,))
        _persist_daily_lessons(conn, packet_id, weekly_plan.get("daily_plan", []))


def _compute_etag(packet_id: str, updated_at: str) -> str:
    """Return a deterministic etag string for a packet."""

    payload = f"{packet_id}:{updated_at}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _deserialize_summary(summary_json: str | None) -> dict[str, Any]:
    if not summary_json:
        return {}
    try:
        return json.loads(summary_json)
    except json.JSONDecodeError:  # pragma: no cover - defensive fallback
        return {}


def list_weekly_packets(
    student_id: str,
    *,
    limit: int,
    offset: int = 0,
    week_of: str | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """Return packet summaries for a student ordered by week desc."""

    ensure_schema()
    limit = max(1, limit)
    query = [
        "SELECT wp.packet_id, wp.student_id, wp.grade_level, wp.subject, wp.week_of, wp.status, wp.summary_json, wp.updated_at,",
        "    pf.completed_at AS feedback_completed_at",
        "FROM weekly_packets wp",
        "LEFT JOIN packet_feedback pf ON pf.packet_id = wp.packet_id AND pf.student_id = wp.student_id",
        "WHERE wp.student_id = ?",
    ]
    params: list[Any] = [student_id]
    if week_of:
        query.append("AND wp.week_of = ?")
        params.append(week_of)
    query.append("ORDER BY wp.week_of DESC, wp.updated_at DESC")
    query.append("LIMIT ? OFFSET ?")
    params.extend([limit + 1, offset])

    sql = "\n".join(query)
    conn = _get_connection()
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    has_more = len(rows) > limit
    rows_to_use: Sequence[sqlite3.Row] = rows[:limit]

    summaries: list[dict[str, Any]] = []
    for row in rows_to_use:
        summary = _deserialize_summary(row["summary_json"])
        feedback_completed_at = row["feedback_completed_at"]
        summaries.append(
            {
                "packet_id": row["packet_id"],
                "student_id": row["student_id"],
                "grade_level": row["grade_level"],
                "subject": row["subject"],
                "week_of": row["week_of"],
                "status": row["status"],
                "updated_at": row["updated_at"],
                "worksheet_counts": summary.get("worksheet_counts", {}),
                "artifact_count": summary.get("artifact_count", 0),
                "resource_days": summary.get("resource_days", 0),
                "daily_count": summary.get("daily_count", 0),
                "has_feedback": feedback_completed_at is not None,
                "feedback_completed_at": feedback_completed_at,
            }
        )

    return summaries, has_more


def get_weekly_packet(student_id: str, packet_id: str) -> dict[str, Any] | None:
    """Return persisted packet payload for a student or None when missing."""

    ensure_schema()
    conn = _get_connection()
    try:
        row = conn.execute(
            """
            SELECT payload_json, updated_at
            FROM weekly_packets
            WHERE packet_id = ? AND student_id = ?
            LIMIT 1
            """,
            (packet_id, student_id),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    try:
        payload = json.loads(row["payload_json"])
    except json.JSONDecodeError as exc:  # pragma: no cover - unexpected
        raise ValueError(f"Corrupted payload for packet {packet_id}: {exc}") from exc

    updated_at = row["updated_at"]
    return {
        "payload": payload,
        "updated_at": updated_at,
        "etag": _compute_etag(packet_id, updated_at),
    }


def _packet_exists(conn: sqlite3.Connection, student_id: str, packet_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM weekly_packets WHERE packet_id = ? AND student_id = ? LIMIT 1",
        (packet_id, student_id),
    ).fetchone()
    return row is not None


def list_packet_artifacts(student_id: str, packet_id: str) -> list[dict[str, Any]] | None:
    """Return artifacts for a packet when the student owns it."""

    ensure_schema()
    conn = _get_connection()
    try:
        if not _packet_exists(conn, student_id, packet_id):
            return None
        rows = conn.execute(
            """
            SELECT id, day_label, kind, file_format, file_path, checksum,
                   file_size_bytes, metadata_json, created_at
            FROM worksheet_artifacts
            WHERE packet_id = ?
            ORDER BY day_label, kind, id
            """,
            (packet_id,),
        ).fetchall()
    finally:
        conn.close()

    artifacts: list[dict[str, Any]] = []
    for row in rows:
        metadata_json = row["metadata_json"]
        metadata = json.loads(metadata_json) if metadata_json else None
        artifacts.append(
            {
                "artifact_id": row["id"],
                "packet_id": packet_id,
                "day_label": row["day_label"],
                "kind": row["kind"],
                "file_format": row["file_format"],
                "file_path": row["file_path"],
                "checksum": row["checksum"],
                "file_size_bytes": row["file_size_bytes"],
                "metadata": metadata,
                "created_at": row["created_at"],
            }
        )

    return artifacts


def get_artifact_for_student(student_id: str, artifact_id: int) -> dict[str, Any] | None:
    """Return artifact metadata + path when student owns it."""

    ensure_schema()
    conn = _get_connection()
    try:
        row = conn.execute(
            """
            SELECT wa.id, wa.packet_id, wa.day_label, wa.kind, wa.file_format,
                   wa.file_path, wa.checksum, wa.file_size_bytes, wa.metadata_json,
                   wa.created_at, wp.student_id
            FROM worksheet_artifacts wa
            JOIN weekly_packets wp ON wa.packet_id = wp.packet_id
            WHERE wa.id = ? AND wp.student_id = ?
            LIMIT 1
            """,
            (artifact_id, student_id),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    metadata_json = row["metadata_json"]
    metadata = json.loads(metadata_json) if metadata_json else None
    return {
        "artifact_id": row["id"],
        "packet_id": row["packet_id"],
        "day_label": row["day_label"],
        "kind": row["kind"],
        "file_format": row["file_format"],
        "file_path": row["file_path"],
        "checksum": row["checksum"],
        "file_size_bytes": row["file_size_bytes"],
        "metadata": metadata,
        "created_at": row["created_at"],
    }


def save_packet_feedback(
    student_id: str,
    packet_id: str,
    mastery_feedback: dict[str, str] | None,
    quantity_feedback: int | None,
    *,
    check_results: dict[str, str] | None = None,
    quick_rating: str | None = None,
    derived_mastery: dict[str, str] | None = None,
) -> int:
    """Save (insert or replace) the one feedback row for a packet; returns its version.

    ``check_results`` are the raw per-check ticks and stay the source of truth; ``mastery_feedback``
    is the per-standard rating that was derived and applied. Saving again bumps ``version``.
    """
    ensure_schema()

    conn = _get_connection()
    try:
        # Verify packet exists and belongs to student
        if not _packet_exists(conn, student_id, packet_id):
            raise ValueError(f"Packet {packet_id} not found for student {student_id}")

        now = _utc_now()
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
                _json(mastery_feedback) if mastery_feedback else None,
                quantity_feedback,
                _json(check_results) if check_results else None,
                quick_rating,
                _json(derived_mastery) if derived_mastery else None,
                now,
            ),
        )
        version = conn.execute(
            "SELECT version FROM packet_feedback WHERE packet_id = ? AND student_id = ?",
            (packet_id, student_id),
        ).fetchone()[0]
        conn.commit()
        return version
    finally:
        conn.close()


def get_packet_feedback(student_id: str, packet_id: str) -> dict[str, Any] | None:
    """Retrieve feedback for a weekly packet."""
    ensure_schema()

    conn = _get_connection()
    try:
        row = conn.execute(
            """
            SELECT packet_id, student_id, completed_at, mastery_feedback_blob, quantity_feedback,
                   check_results_json, quick_rating, derived_mastery_json, version
            FROM packet_feedback
            WHERE packet_id = ? AND student_id = ?
            LIMIT 1
            """,
            (packet_id, student_id),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    def _load(blob: str | None) -> Any:
        return json.loads(blob) if blob else None

    return {
        "packet_id": row["packet_id"],
        "student_id": row["student_id"],
        "completed_at": row["completed_at"],
        "mastery_feedback": _load(row["mastery_feedback_blob"]),
        "quantity_feedback": row["quantity_feedback"],
        "check_results": _load(row["check_results_json"]),
        "quick_rating": row["quick_rating"],
        "derived_mastery": _load(row["derived_mastery_json"]),
        "version": row["version"],
    }
