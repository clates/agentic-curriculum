"""Ingestion only stores real standards (M11.4a)."""

from __future__ import annotations

import json
import sqlite3

import pytest

import src.ingest_standards as ing


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "c.db"
    monkeypatch.setattr(ing, "DB_FILE", str(path))
    ing.create_database()
    return path


def test_real_data_has_no_junk_rows(db):
    ing.ingest_standards_from_json(ing.STANDARDS_DIR)
    con = sqlite3.connect(db)
    assert (
        con.execute("SELECT COUNT(*) FROM standards WHERE description IS NULL").fetchone()[0] == 0
    )
    assert con.execute("SELECT COUNT(*) FROM standards WHERE source IS NULL").fetchone()[0] == 0
    assert (
        con.execute("SELECT COUNT(*) FROM standards WHERE standard_id LIKE 'history-%'").fetchone()[
            0
        ]
        == 0
    )
    # every id follows the JURIS.SUBJECT.GRADE.code scheme
    bad = [r[0] for r in con.execute("SELECT standard_id FROM standards") if r[0].count(".") < 3]
    assert bad == []
    assert con.execute("SELECT COUNT(*) FROM standards").fetchone()[0] > 1400


def test_container_and_malformed_records_are_skipped(db, tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "a.json").write_text(
        json.dumps(
            [
                {
                    "id": "VA.MATH.K.k.1",
                    "source": "VA",
                    "subject": "Math",
                    "grade": 0,
                    "description": "Count",
                },
                {
                    "id": "math-k",
                    "title": "T",
                    "subject": "Math",
                    "grade": "K",
                    "categories": [{"x": 1}],
                },
                {"id": "VA.MATH.1.1.1", "subject": "Math", "grade": 1, "description": ""},
                "not a dict",
            ]
        )
    )
    ing.ingest_standards_from_json(str(d))
    ids = [r[0] for r in sqlite3.connect(db).execute("SELECT standard_id FROM standards")]
    assert ids == ["VA.MATH.K.k.1"]


def test_reingest_purges_junk_left_by_older_versions(db):
    con = sqlite3.connect(db)
    con.execute(
        "INSERT INTO standards (standard_id, subject, grade_level, json_blob) VALUES ('history-k','History','K','{}')"
    )
    con.commit()
    con.close()
    ing.ingest_standards_from_json(ing.STANDARDS_DIR)
    assert (
        sqlite3.connect(db)
        .execute("SELECT COUNT(*) FROM standards WHERE standard_id='history-k'")
        .fetchone()[0]
        == 0
    )
