"""Storage for structured weeks (WeekDoc), M2.6.

``save_week`` writes, in one transaction: a legacy-shaped summary row in ``weekly_packets`` (so
the existing list/get endpoints keep working), the document in ``week_documents`` and the derived
``prep_checks`` index. ``get_week`` loads through ``load_week`` so older ``schema_version`` rows
are upgraded on read.

Tenancy (D2): every row carries ``family_id``. The Tenant type has not landed yet, so functions
take ``family_id`` (default ``fam_local``) as its stand-in; a week is only visible when both the
family and the student own it.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from typing import Any

try:
    from . import packet_store as _ps
    from .weekdoc import WeekDoc, load_week
except ImportError:  # script/uvicorn context: src/ is on sys.path
    sys.path.insert(0, os.path.dirname(__file__))
    import packet_store as _ps  # type: ignore
    from weekdoc import WeekDoc, load_week  # type: ignore

DEFAULT_FAMILY = "fam_local"


class PacketOwnershipError(ValueError):
    """The packet id already belongs to another family or student."""


def _legacy_payload(
    week: WeekDoc, packet_id: str, student_id: str, grade_level: int, week_of: str
) -> dict[str, Any]:
    """The payload shape the existing GET endpoint returns for a packet."""
    return {
        "plan_id": packet_id,
        "student_id": student_id,
        "grade_level": grade_level,
        "subject": week.subject or week.theme,
        "week_of": week_of,
        "weekly_overview": week.arc or week.title,
        "structured": True,
        "daily_plan": [
            {
                "day": d.day,
                "focus": d.title,
                "standards": [{"standard_id": s} for s in d.standards],
                "resources": {},
            }
            for d in week.days
        ],
    }


def _summary(week: WeekDoc) -> dict[str, Any]:
    counts = Counter(w.kind for d in week.days for w in d.worksheets)
    return {
        "daily_count": len(week.days),
        "resource_days": len(week.days),
        "worksheet_counts": dict(counts),
        "artifact_count": 0,  # structured weeks are rendered on demand, not stored as files
        "structured": True,
    }


def save_week(
    student_id: str,
    packet_id: str,
    week: WeekDoc | dict[str, Any],
    *,
    grade_level: int,
    week_of: str,
    family_id: str = DEFAULT_FAMILY,
    status: str = _ps.READY_STATUS,
) -> WeekDoc:
    """Validate and store a week. Re-saving the same packet replaces it. Returns the WeekDoc."""
    doc = week if isinstance(week, WeekDoc) else load_week(week)
    _ps.ensure_schema()
    now = _ps._utc_now()
    payload = _legacy_payload(doc, packet_id, student_id, grade_level, week_of)
    conn = _ps._get_connection()
    try:
        with conn:  # one transaction: all three writes or none
            cur = conn.execute(
                """
                INSERT INTO weekly_packets (packet_id, student_id, grade_level, subject, week_of,
                    status, weekly_overview, summary_json, payload_json, created_at, updated_at,
                    family_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(packet_id) DO UPDATE SET
                    grade_level = excluded.grade_level, subject = excluded.subject,
                    week_of = excluded.week_of, status = excluded.status,
                    weekly_overview = excluded.weekly_overview,
                    summary_json = excluded.summary_json, payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                WHERE weekly_packets.family_id = excluded.family_id
                  AND weekly_packets.student_id = excluded.student_id
                """,
                (
                    packet_id,
                    student_id,
                    grade_level,
                    payload["subject"],
                    week_of,
                    status,
                    payload["weekly_overview"],
                    _ps._json(_summary(doc)),
                    _ps._json(payload),
                    now,
                    now,
                    family_id,
                ),
            )
            if cur.rowcount == 0:
                raise PacketOwnershipError(f"packet {packet_id!r} belongs to another owner")
            conn.execute(
                "DELETE FROM week_documents WHERE family_id = ? AND packet_id = ?",
                (family_id, packet_id),
            )  # cascades to prep_checks
            conn.execute(
                "INSERT INTO week_documents (family_id, packet_id, schema_version, doc_json,"
                " created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (family_id, packet_id, doc.schema_version, doc.model_dump_json(), now, now),
            )
            conn.executemany(
                "INSERT INTO prep_checks (family_id, packet_id, check_id, position, day,"
                " standard_id, kind) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (family_id, packet_id, c.id, i, c.day, c.standard_id, c.kind)
                    for i, c in enumerate(doc.prep_checks)
                ],
            )
    finally:
        conn.close()
    return doc


def get_week(student_id: str, packet_id: str, *, family_id: str = DEFAULT_FAMILY) -> WeekDoc | None:
    """Load a stored week (migrating older schema versions on read), or None if not owned."""
    _ps.ensure_schema()
    conn = _ps._get_connection()
    try:
        row = conn.execute(
            """
            SELECT d.doc_json FROM week_documents d
            JOIN weekly_packets p ON p.family_id = d.family_id AND p.packet_id = d.packet_id
            WHERE d.family_id = ? AND d.packet_id = ? AND p.student_id = ?
            """,
            (family_id, packet_id, student_id),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return load_week(json.loads(row["doc_json"]))


def list_prep_checks(
    student_id: str, packet_id: str, *, family_id: str = DEFAULT_FAMILY
) -> list[dict[str, Any]]:
    """The derived check index for a packet, in document order (empty if none/not owned)."""
    _ps.ensure_schema()
    conn = _ps._get_connection()
    try:
        rows = conn.execute(
            """
            SELECT c.check_id, c.day, c.standard_id, c.kind FROM prep_checks c
            JOIN weekly_packets p ON p.family_id = c.family_id AND p.packet_id = c.packet_id
            WHERE c.family_id = ? AND c.packet_id = ? AND p.student_id = ?
            ORDER BY c.position
            """,
            (family_id, packet_id, student_id),
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]
