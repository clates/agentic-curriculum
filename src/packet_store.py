"""Persistence helpers for weekly packets, daily lessons, and worksheet artifacts."""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

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