"""Numbered SQL migration runner.

Migrations live next to this file as ``NNNN_name.sql`` and run in numeric order exactly once.
Applied versions are recorded in the ``schema_version`` table. A fresh database and an existing
one converge on the same schema: migration 0001 is the historical ``CREATE TABLE IF NOT EXISTS``
baseline, so it is a no-op on a database that already has those tables.

Each migration runs in its own transaction (a failure rolls the whole file back and stops the
run). Foreign keys are switched off while a migration runs, so a table can be rebuilt (the
standard SQLite 12-step recipe), and ``PRAGMA foreign_key_check`` must come back clean before the
migration commits.

Number ownership (see the build plan): 0001 baseline, 0002 tenancy, 0003 llm_usage,
0004 week_documents, 0005 feedback, 0006 week_plan, 0007 loop state, 0008 student FK,
0011 auth (0009 and 0010 are reserved; the runner applies by version, so gaps are fine).
"""

from __future__ import annotations

import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parent
_NAME_RE = re.compile(r"^(\d{4})_([a-z0-9_]+)\.sql$")


class MigrationError(RuntimeError):
    """A migration failed or the migration set is inconsistent."""


def discover(directory: Path | None = None) -> list[tuple[int, str, Path]]:
    """Return ``(version, name, path)`` for every migration file, sorted by version."""
    found: list[tuple[int, str, Path]] = []
    for path in sorted((directory or MIGRATIONS_DIR).glob("*.sql")):
        match = _NAME_RE.match(path.name)
        if not match:
            raise MigrationError(f"Bad migration file name: {path.name} (want NNNN_name.sql)")
        found.append((int(match.group(1)), match.group(2), path))
    versions = [v for v, _, _ in found]
    if len(versions) != len(set(versions)):
        raise MigrationError(f"Duplicate migration numbers in {directory or MIGRATIONS_DIR}")
    return sorted(found)


def _statements(sql: str) -> list[str]:
    """Split a script into complete statements (trigger bodies stay whole)."""
    out: list[str] = []
    start = 0
    for i, ch in enumerate(sql):
        if ch == ";" and sqlite3.complete_statement(sql[start : i + 1]):
            out.append(sql[start : i + 1].strip())
            start = i + 1
    tail = sql[start:]
    if any(ln.strip() and not ln.strip().startswith("--") for ln in tail.splitlines()):
        raise MigrationError(f"Incomplete SQL statement at end of migration: {tail.strip()[:80]}")
    return out


def applied_versions(conn: sqlite3.Connection) -> set[int]:
    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_version'"
    ).fetchone()
    if not exists:
        return set()
    return {row[0] for row in conn.execute("SELECT version FROM schema_version")}


def apply_migrations(db_path: str | Path, directory: Path | None = None) -> list[int]:
    """Apply every pending migration to ``db_path`` (created if missing).

    Returns the versions applied by this call (empty when already up to date). Safe to call
    from several processes at once: each migration takes the write lock and re-checks.
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    migrations = discover(directory)
    # isolation_level=None: we issue BEGIN/COMMIT ourselves.
    conn = sqlite3.connect(str(db_path), isolation_level=None, timeout=30)
    applied_now: list[int] = []
    try:
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_version ("
            "version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)"
        )
        for version, name, path in migrations:
            if version in applied_versions(conn):
                continue
            conn.execute("BEGIN IMMEDIATE")
            try:
                if version in applied_versions(conn):  # another process won the race
                    conn.execute("COMMIT")
                    continue
                for statement in _statements(path.read_text()):
                    conn.execute(statement)
                violations = conn.execute("PRAGMA foreign_key_check").fetchall()
                if violations:
                    raise MigrationError(
                        f"Migration {path.name} leaves {len(violations)} foreign key "
                        f"violation(s), first: {tuple(violations[0])}"
                    )
                conn.execute(
                    "INSERT INTO schema_version (version, name, applied_at) VALUES (?, ?, ?)",
                    (version, name, datetime.now(UTC).isoformat(timespec="seconds")),
                )
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
            applied_now.append(version)
    finally:
        conn.close()
    return applied_now
