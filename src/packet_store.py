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
except ImportError:  # Fallback for direct script execution
    sys.path.insert(0, os.path.dirname(__file__))
    from db_utils import DB_FILE  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
READY_STATUS = "ready"

_SCHEMA_INITIALIZED = False


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
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_schema() -> None:
    """Create packet storage tables if they do not already exist."""
    global _SCHEMA_INITIALIZED
    if _SCHEMA_INITIALIZED:
        return

    statements = [
        """
        CREATE TABLE IF NOT EXISTS weekly_packets (
            packet_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            grade_level INTEGER NOT NULL,
            subject TEXT NOT NULL,
            week_of TEXT NOT NULL,
            status TEXT NOT NULL,
            weekly_overview TEXT,
            summary_json TEXT,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_weekly_packets_student_week
        ON weekly_packets(student_id, week_of)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_weekly_packets_status
        ON weekly_packets(status)
        """,
        """
        CREATE TABLE IF NOT EXISTS daily_lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            packet_id TEXT NOT NULL,
            day_label TEXT NOT NULL,
            focus TEXT,
            standards_json TEXT,
            lesson_plan_json TEXT NOT NULL,
            resources_json TEXT,
            worksheet_plans_json TEXT,
            resource_errors_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(packet_id) REFERENCES weekly_packets(packet_id) ON DELETE CASCADE,
            UNIQUE(packet_id, day_label)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS worksheet_artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            packet_id TEXT NOT NULL,
            daily_lesson_id INTEGER NOT NULL,
            day_label TEXT NOT NULL,
            kind TEXT NOT NULL,
            file_format TEXT NOT NULL,
            file_path TEXT NOT NULL,
            checksum TEXT,
            file_size_bytes INTEGER,
            metadata_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(packet_id) REFERENCES weekly_packets(packet_id) ON DELETE CASCADE,
            FOREIGN KEY(daily_lesson_id) REFERENCES daily_lessons(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_artifacts_packet_kind
        ON worksheet_artifacts(packet_id, kind)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_daily_lessons_packet
        ON daily_lessons(packet_id)
        """,
    ]

    conn = _get_connection()
    try:
        with conn:
            for statement in statements:
                conn.execute(statement)
    finally:
        conn.close()
    _SCHEMA_INITIALIZED = True


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


def _delete_existing_packet(conn: sqlite3.Connection, packet_id: str) -> None:
    conn.execute("DELETE FROM weekly_packets WHERE packet_id = ?", (packet_id,))


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
        _delete_existing_packet(conn, packet_id)
        _insert_weekly_packet(conn, weekly_plan, status)
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
        "SELECT packet_id, student_id, grade_level, subject, week_of, status, summary_json, updated_at",
        "FROM weekly_packets",
        "WHERE student_id = ?",
    ]
    params: list[Any] = [student_id]
    if week_of:
        query.append("AND week_of = ?")
        params.append(week_of)
    query.append("ORDER BY week_of DESC, updated_at DESC")
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
) -> None:
    """Save feedback for a weekly packet."""
    ensure_schema()

    conn = _get_connection()
    try:
        # Verify packet exists and belongs to student
        if not _packet_exists(conn, student_id, packet_id):
            raise ValueError(f"Packet {packet_id} not found for student {student_id}")

        # Check if feedback already exists
        existing = conn.execute(
            "SELECT feedback_id FROM packet_feedback WHERE packet_id = ? AND student_id = ?",
            (packet_id, student_id),
        ).fetchone()

        if existing:
            raise ValueError(f"Feedback already exists for packet {packet_id}")

        # Insert feedback
        mastery_blob = _json(mastery_feedback) if mastery_feedback else None
        conn.execute(
            """
            INSERT INTO packet_feedback (
                packet_id,
                student_id,
                completed_at,
                mastery_feedback_blob,
                quantity_feedback
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (packet_id, student_id, _utc_now(), mastery_blob, quantity_feedback),
        )
        conn.commit()
    finally:
        conn.close()


def get_packet_feedback(student_id: str, packet_id: str) -> dict[str, Any] | None:
    """Retrieve feedback for a weekly packet."""
    ensure_schema()

    conn = _get_connection()
    try:
        row = conn.execute(
            """
            SELECT packet_id, student_id, completed_at, mastery_feedback_blob, quantity_feedback
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

    mastery_blob = row["mastery_feedback_blob"]
    mastery_feedback = json.loads(mastery_blob) if mastery_blob else None

    return {
        "packet_id": row["packet_id"],
        "student_id": row["student_id"],
        "completed_at": row["completed_at"],
        "mastery_feedback": mastery_feedback,
        "quantity_feedback": row["quantity_feedback"],
    }
