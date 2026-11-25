"""Ownership check: a student belongs to a family by profile row or by packet row."""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

from fastapi import HTTPException
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import db_utils  # noqa: E402
from auth import store  # noqa: E402
import tenancy  # noqa: E402
from migrations import apply_migrations  # noqa: E402


@pytest.fixture
def conn(tmp_path, monkeypatch):
    db = tmp_path / "tenancy.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    monkeypatch.setattr(db_utils, "DB_FILE", str(db))
    apply_migrations(db)
    c = sqlite3.connect(db)
    yield c
    c.close()


@pytest.fixture
def families(conn):
    """(A, B): A owns profile student stu_prof and packet-only student stu_pack."""
    a, b = store.create_family(conn, "A"), store.create_family(conn, "B")
    conn.execute(
        "INSERT INTO student_profiles (student_id, family_id) VALUES ('stu_prof', ?)", (a,)
    )
    conn.execute(
        "INSERT INTO weekly_packets (packet_id, student_id, grade_level, subject, week_of,"
        " status, payload_json, created_at, updated_at, family_id)"
        " VALUES ('p1', 'stu_pack', 3, 'math', '2026-01-05', 'draft', '{}', 'n', 'n', ?)",
        (a,),
    )
    conn.commit()
    return a, b


def test_profile_student_belongs_to_its_family_only(conn, families):
    a, b = families
    assert tenancy.student_in_family(conn, a, "stu_prof")
    assert not tenancy.student_in_family(conn, b, "stu_prof")


def test_packet_only_student_belongs_to_packet_family(conn, families):
    a, b = families
    assert tenancy.student_in_family(conn, a, "stu_pack")
    assert not tenancy.student_in_family(conn, b, "stu_pack")


def test_unknown_student_belongs_to_nobody(conn, families):
    a, b = families
    assert not tenancy.student_in_family(conn, a, "stu_nope")
    assert not tenancy.student_in_family(conn, b, "stu_nope")


def test_owned_student_id_returns_id_or_404(conn, families):
    a, b = families
    assert tenancy.owned_student_id("stu_prof", a) == "stu_prof"
    with pytest.raises(HTTPException) as exc:
        tenancy.owned_student_id("stu_prof", b)
    assert (exc.value.status_code, exc.value.detail) == (404, "Student not found")


def test_new_student_id_shape_and_uniqueness():
    ids = [tenancy.new_student_id() for _ in range(1000)]
    assert all(re.fullmatch(r"stu_[a-z2-7]{10}", i) for i in ids)
    assert len(set(ids)) == 1000
