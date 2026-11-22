"""M3.1 / M3.2: prompt assets, generated kind menu, student allowlist, standards grounding."""

import json
import sqlite3

import pytest

from authoring import catalog
from authoring.context import ModelStudentContext
from authoring.prompts_builder import build_prompts, prompt_hash, prompt_version
from authoring.standards import UnknownStandardsError, load_standards, search_standards
from weekdoc import HOSTED_KINDS, item_refs

STUDENT = ModelStudentContext(
    first_name="Ada", grade=2, reading_level="on grade level", interests=["space"],
    parent_notes="likes hands-on",
)


def _all_samples():
    from tests.test_weekdoc_kinds_blocks import CASES as BLOCKS
    from tests.test_weekdoc_kinds_classification import CASES as CLASSIFICATION
    from tests.test_weekdoc_kinds_comprehension import CASES as COMPREHENSION
    from tests.test_weekdoc_kinds_crafts import CASES as CRAFTS
    from tests.test_weekdoc_kinds_fractions import CASES as FRACTIONS
    from tests.test_weekdoc_kinds_graphs import CASES as GRAPHS
    from tests.test_weekdoc_kinds_handwriting import CASES as HANDWRITING
    from tests.test_weekdoc_kinds_math import CASES as MATH
    from tests.test_weekdoc_kinds_ordered import CASES as ORDERED
    from tests.test_weekdoc_kinds_visual import SAMPLES as VISUAL

    samples = {**COMPREHENSION, **CLASSIFICATION, **ORDERED, **MATH, **BLOCKS, **FRACTIONS,
               **HANDWRITING, **GRAPHS, **VISUAL, **CRAFTS}
    samples["storyPanel"] = {"who": "Zara", "text": "A beat."}
    return samples


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "s.db"
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE standards (standard_id TEXT PRIMARY KEY, source TEXT, subject TEXT, "
        "grade_level INTEGER, description TEXT, json_blob TEXT)"
    )
    con.executemany(
        "INSERT INTO standards (standard_id, subject, grade_level, description) VALUES (?,?,?,?)",
        [
            ("VA.SCIENCE.2.2.6.a", "Science", 2, "Weather types"),
            ("VA.SCIENCE.2.2.6.b", "Science", 2, "Track weather"),
            ("VA.MATH.2.2.1", "Math", 2, "Count to 1000"),
        ],
    )
    con.commit()
    con.close()
    return str(path)


def test_every_registered_kind_has_a_menu_line():
    menu = catalog.kind_menu().splitlines()
    assert len(menu) == len(HOSTED_KINDS)
    for kind in HOSTED_KINDS:
        assert any(line.startswith(f"- {kind} [") for line in menu), kind
        assert catalog.purpose(kind)


def test_purposes_file_has_no_stale_kinds():
    assert set(catalog._purposes()) == set(HOSTED_KINDS)


def test_a_kind_without_a_purpose_is_a_loud_error(monkeypatch):
    monkeypatch.setattr(catalog, "_purposes", lambda: {})
    with pytest.raises(catalog.CatalogError, match="readingWorksheet"):
        catalog.kind_menu(["readingWorksheet"])


def test_ref_patterns_file_matches_the_registry_samples():
    """prompts/kind_ref_patterns.json is derived from the kind sample data; keep it current."""
    import re

    samples = _all_samples()
    for kind, entry in HOSTED_KINDS.items():
        expected = (
            sorted({re.sub(r"\d+", "N", r.ref) for r in item_refs(kind, samples[kind])})
            if entry.enumerate
            else []
        )
        assert catalog._ref_patterns().get(kind, []) == expected, kind


def test_kind_block_carries_schema_and_ref_shapes():
    block = catalog.kind_block("matchingWorksheet")
    assert "left_items" in block and "left_items.N" in block
    assert "no answers" in catalog.kind_block("storyPanel")
    assert "mode" in catalog.kind_block("shapeIdWorksheet")


def test_prompt_records_version_and_hash():
    prompts = build_prompts(STUDENT, "Weather", [])
    assert prompts.version == prompt_version() and prompts.hash == prompt_hash()
    assert prompts.version and len(prompts.hash) == 16


def test_prompts_carry_only_allowlisted_student_fields(db):
    profile = {
        "first_name": "Ada", "grade": "2", "reading_level": "grade 2", "interests": ["space"],
        "parent_notes": "likes hands-on", "last_name": "Lovelace-Quux", "email": "a@secret.example",
        "birthday": "2019-03-04", "student_id": "stu_abc123", "family_id": "fam_zzz",
    }
    student = ModelStudentContext.from_profile(profile)
    stds = load_standards(["VA.SCIENCE.2.2.6.a"], db)
    p = build_prompts(student, "Weather", stds)
    text = json.dumps([p.plan_messages(), p.week_messages("{}", ["storyPanel"], student)])
    for leaked in ("Lovelace", "secret.example", "2019-03-04", "stu_abc123", "fam_zzz"):
        assert leaked not in text
    assert '"first_name": "Ada"' in p.common and "likes hands-on" in p.common


def test_context_rejects_extra_fields_and_bad_names():
    with pytest.raises(ValueError):
        ModelStudentContext(first_name="Ada", grade=2, reading_level="x", last_name="L")
    with pytest.raises(ValueError):
        ModelStudentContext(first_name="ada@example.com", grade=2, reading_level="x")
    assert ModelStudentContext(first_name="Ada", grade="K", reading_level="x").grade_label == "K"


def test_standards_load_from_db_and_unknown_ids_raise(db):
    got = load_standards(["VA.SCIENCE.2.2.6.b", "VA.SCIENCE.2.2.6.a", "VA.SCIENCE.2.2.6.b"], db)
    assert [s.standard_id for s in got] == ["VA.SCIENCE.2.2.6.b", "VA.SCIENCE.2.2.6.a"]
    assert got[0].description == "Track weather"
    with pytest.raises(UnknownStandardsError) as exc:
        load_standards(["VA.SCIENCE.2.2.6.a", "VA.NOPE.1"], db)
    assert exc.value.missing == ["VA.NOPE.1"]


def test_search_standards_filters(db):
    assert [s.standard_id for s in search_standards(grade=2, subject="science", db_path=db)] == [
        "VA.SCIENCE.2.2.6.a", "VA.SCIENCE.2.2.6.b",
    ]
    assert len(search_standards(grade=2, keyword="count", db_path=db)) == 1
