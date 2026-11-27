"""GET /students/{id}/coverage: per-subject counts of solid, shaky and still-to-come skills."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import main  # noqa: E402
from auth import passwords, store  # noqa: E402
from migrations import apply_migrations  # noqa: E402

LONG = "The student will investigate and understand skill number {n} in {subject}"
KID = "kid_1"


def _progress(mastered=(), developing=(), last=None) -> str:
    meta = {sid: {"last_feedback": r} for sid, r in (last or {}).items()}
    return json.dumps(
        {
            "mastered_standards": list(mastered),
            "developing_standards": list(developing),
            "standard_metadata": meta,
        }
    )


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "coverage.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(path))
    monkeypatch.delenv("AUTH_REQUIRED", raising=False)
    monkeypatch.setitem(main.get_student_profile.__globals__, "DB_FILE", str(path))
    apply_migrations(path)
    conn = sqlite3.connect(path)
    # Math: 4 skills at grade 3, 2 at grade 2, plus a bullet sub-point at grade 3 (not a skill).
    # English: 3 skills at grade 2, 2 at grade 3. Science: 2 at grade 2 only.
    plan = [("Math", 3, 4), ("Math", 2, 2), ("English", 2, 3), ("English", 3, 2), ("Science", 2, 2)]
    for subject, grade, count in plan:
        for n in range(1, count + 1):
            conn.execute(
                "INSERT INTO standards (standard_id, subject, grade_level, description)"
                " VALUES (?, ?, ?, ?)",
                (f"{subject[:2]}.{grade}.{n}", subject, grade, LONG.format(n=n, subject=subject)),
            )
    conn.execute(
        "INSERT INTO standards (standard_id, subject, grade_level, description)"
        " VALUES ('Ma.3.1.a', 'Math', 3, ?)",
        (LONG.format(n=1, subject="Math"),),
    )
    conn.commit()
    yield conn
    conn.close()


def _child(conn, meta: dict, progress: str = "{}", family: str = "fam_local", sid: str = KID):
    conn.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob,"
        " family_id) VALUES (?, ?, '{}', ?, ?)",
        (sid, progress, json.dumps(meta), family),
    )
    conn.commit()


def _get(sid: str = KID):
    return TestClient(main.app).get(f"/students/{sid}/coverage")


def test_child_with_no_history_has_only_still_to_come(db):
    _child(db, {"grade_level": 3, "math_grade": 3, "la_grade": 2})
    r = _get()
    assert r.status_code == 200
    assert r.json() == [
        {"subject": "Math", "solid": 0, "shaky": 0, "to_come": 4},
        {"subject": "English", "solid": 0, "shaky": 0, "to_come": 3},
        {"subject": "Science", "solid": 0, "shaky": 0, "to_come": 2},
    ]


def test_per_subject_grade_rule_math_vs_language_arts(db):
    _child(db, {"grade_level": 3, "math_grade": 2, "la_grade": 3})
    got = {row["subject"]: row for row in _get().json()}
    assert got["Math"]["to_come"] == 2  # math grade 2
    assert got["English"]["to_come"] == 2  # la grade 3
    assert "Science" not in got  # no grade-3 Science skills, no progress: no row


def test_other_subjects_follow_the_language_arts_grade(db):
    _child(db, {"math_grade": 3, "la_grade": 2})
    got = {row["subject"]: row for row in _get().json()}
    assert got["Science"]["to_come"] == 2  # la grade 2


def test_grade_level_fallback_when_no_subject_grades(db):
    _child(db, {"grade_level": 3})
    got = {row["subject"]: row for row in _get().json()}
    assert got["Math"]["to_come"] == 4 and got["English"]["to_come"] == 2
    assert "Science" not in got


def test_solid_shaky_and_to_come_split(db):
    progress = _progress(
        mastered=["Ma.3.1"],
        developing=["Ma.3.2", "Ma.3.3"],
        last={"Ma.3.2": "DEVELOPING", "Ma.3.3": "STRUGGLING"},
    )
    _child(db, {"math_grade": 3, "la_grade": 2}, progress)
    math = next(r for r in _get().json() if r["subject"] == "Math")
    assert math == {"subject": "Math", "solid": 1, "shaky": 2, "to_come": 1}


def test_mastered_skill_due_for_review_still_counts_as_solid(db):
    progress = json.dumps(
        {
            "mastered_standards": ["Ma.3.1"],
            "developing_standards": [],
            "standard_metadata": {
                "Ma.3.1": {
                    "last_feedback": "MASTERED",
                    "last_seen": "2020-01-01T10:00:00Z",
                    "cooldown_weeks": 1,
                }
            },
        }
    )
    from review_policy import review_due

    assert [r["standard_id"] for r in review_due(progress)] == ["Ma.3.1"]  # it is due
    _child(db, {"math_grade": 3, "la_grade": 3}, progress)
    math = next(r for r in _get().json() if r["subject"] == "Math")
    assert math == {"subject": "Math", "solid": 1, "shaky": 0, "to_come": 3}


def test_progress_outside_the_grade_counts_without_breaking_to_come(db):
    # Science has no skills at grade 3, and a grade-2 Math skill is mastered at grade 3.
    progress = _progress(mastered=["Sc.2.1", "Ma.2.1"], developing=["Sc.2.2"])
    _child(db, {"math_grade": 3, "la_grade": 3}, progress)
    got = {row["subject"]: row for row in _get().json()}
    assert got["Science"] == {"subject": "Science", "solid": 1, "shaky": 1, "to_come": 0}
    assert got["Math"] == {"subject": "Math", "solid": 1, "shaky": 0, "to_come": 4}


def test_bullet_sub_points_and_unknown_ids_are_not_counted(db):
    progress = _progress(mastered=["Ma.3.1.a", "NOPE.1"])
    _child(db, {"math_grade": 3, "la_grade": 3}, progress)
    math = next(r for r in _get().json() if r["subject"] == "Math")
    assert math["solid"] == 0 and math["to_come"] == 4


def test_order_and_no_ids_in_the_response(db):
    _child(db, {"grade_level": 2}, _progress(mastered=["Sc.2.1"]))
    rows = _get().json()
    assert [r["subject"] for r in rows] == ["Math", "English", "Science"]
    assert all(set(r) == {"subject", "solid", "shaky", "to_come"} for r in rows)


def test_unknown_child_is_404(db):
    r = _get("nobody")
    assert r.status_code == 404 and r.json() == {"detail": "Student not found"}


def test_another_familys_child_is_404_with_login_on(db, tmp_path, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "1")
    monkeypatch.setattr(passwords, "CURRENT", passwords.ScryptParams(n=2**10, r=8, p=1))
    fam_a, fam_b = store.create_family(db, "A"), store.create_family(db, "B")
    store.create_user(db, "parenta", "correct horse battery", fam_a)
    store.create_user(db, "parentb", "correct horse battery", fam_b)
    _child(db, {"grade_level": 3}, family=fam_a)

    def login(name):
        c = TestClient(main.app)
        assert (
            c.post("/auth/login", json={"username": name, "password": "correct horse battery"})
        ).status_code == 200
        return c

    assert login("parenta").get(f"/students/{KID}/coverage").status_code == 200
    b = login("parentb")
    r = b.get(f"/students/{KID}/coverage")
    assert r.status_code == 404
    assert r.json() == b.get("/students/no_such/coverage").json() == {"detail": "Student not found"}


def test_empty_progress_blob_is_no_progress(db):
    _child(db, {"math_grade": 3, "la_grade": 2}, progress="")
    r = _get()
    assert r.status_code == 200
    assert next(row for row in r.json() if row["subject"] == "Math") == {
        "subject": "Math",
        "solid": 0,
        "shaky": 0,
        "to_come": 4,
    }
