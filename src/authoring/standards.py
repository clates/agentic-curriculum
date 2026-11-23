"""Standards grounding (M3.2): the real standards for a topic, read from the standards DB.

The prompt lists these ids with their descriptions; the validators in ``gate`` and the plan
check reject any Day.standards or prep-check standard_id that is not on the list.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from db_utils import get_db_path


class UnknownStandardsError(ValueError):
    """Some requested standard ids are not in the standards DB."""

    def __init__(self, missing: list[str]) -> None:
        super().__init__(f"standard id(s) not in the standards database: {', '.join(missing)}")
        self.missing = missing


@dataclass(frozen=True)
class Standard:
    standard_id: str
    description: str
    subject: str | None = None
    grade_level: int | None = None


def _connect(db_path: str | None) -> sqlite3.Connection:
    return sqlite3.connect(db_path or get_db_path())


def load_standards(ids: list[str], db_path: str | None = None) -> list[Standard]:
    """Resolve ids (order kept, duplicates dropped); unknown ids raise UnknownStandardsError."""
    unique = list(dict.fromkeys(i.strip() for i in ids if i and i.strip()))
    conn = _connect(db_path)
    try:
        found: dict[str, Standard] = {}
        for sid in unique:
            row = conn.execute(
                "SELECT standard_id, description, subject, grade_level FROM standards "
                "WHERE standard_id = ?",
                (sid,),
            ).fetchone()
            if row:
                found[sid] = Standard(row[0], row[1] or "", row[2], row[3])
    finally:
        conn.close()
    missing = [s for s in unique if s not in found]
    if missing:
        raise UnknownStandardsError(missing)
    return [found[s] for s in unique]


def search_standards(
    *,
    grade: int,
    subject: str | None = None,
    keyword: str | None = None,
    db_path: str | None = None,
    limit: int = 40,
) -> list[Standard]:
    """Browse the DB for a grade (and optional subject / description keyword)."""
    sql = (
        "SELECT standard_id, description, subject, grade_level FROM standards WHERE grade_level = ?"
    )
    args: list[object] = [grade]
    if subject:
        sql += " AND lower(subject) = lower(?)"
        args.append(subject)
    if keyword:
        sql += " AND lower(description) LIKE ?"
        args.append(f"%{keyword.lower()}%")
    sql += " ORDER BY standard_id LIMIT ?"
    args.append(limit)
    conn = _connect(db_path)
    try:
        return [Standard(r[0], r[1] or "", r[2], r[3]) for r in conn.execute(sql, args)]
    finally:
        conn.close()
