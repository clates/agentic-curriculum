"""Tests for the week_plan table, the outline model and its data functions (M6.2)."""

import sqlite3

import pytest
from pydantic import ValidationError

from src.migrations import apply_migrations
from src.outline_models import Outline, OutlineSet
from src import week_plan as wp

NOW = "2026-01-01T00:00:00Z"


def _outline(option_id, topic="Dinosaurs", ids=("VA.MATH.2.1",)):
    return {
        "option_id": option_id,
        "title": f"Option {option_id}",
        "hook": "A week about dinosaurs",
        "topic": topic,
        "standard_ids": list(ids),
    }


def _set():
    return OutlineSet.model_validate(
        {
            "options": [
                _outline("a", "Weather"),
                _outline("b", "Baking"),
                _outline("c", "Space"),
            ]
        }
    )


@pytest.fixture
def conn(tmp_path):
    db = tmp_path / "t.db"
    apply_migrations(db)
    c = sqlite3.connect(db)
    c.execute("PRAGMA foreign_keys = ON")
    c.execute("INSERT INTO family (family_id, name, created_at) VALUES ('fam_b', 'B', ?)", (NOW,))
    for fam, stu in (("fam_local", "stu_1"), ("fam_local", "stu_2"), ("fam_b", "stu_9")):
        c.execute(
            "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, "
            "metadata_blob, family_id) VALUES (?, '{}', '{}', '{}', ?)",
            (stu, fam),
        )
    c.commit()
    yield c
    c.close()


def test_migration_0006_applies_once(tmp_path):
    db = tmp_path / "m.db"
    assert 6 in apply_migrations(db)
    assert apply_migrations(db) == []


def test_create_plan_is_idempotent_per_student_week(conn):
    a = wp.create_plan(conn, "fam_local", "stu_1", "2026-01-05", pick_deadline="2026-01-03")
    b = wp.create_plan(conn, "fam_local", "stu_1", "2026-01-05")
    assert a.plan_id == b.plan_id and a.status == "awaiting_feedback"
    assert a.state_version == 0 and a.needs_attention is False
    assert a.plan_id.startswith("wp_")
    other_week = wp.create_plan(conn, "fam_local", "stu_1", "2026-01-12")
    assert other_week.plan_id != a.plan_id


def test_plan_needs_a_real_student_in_the_same_family(conn):
    with pytest.raises(sqlite3.IntegrityError):
        wp.create_plan(conn, "fam_local", "stu_9", "2026-01-05")  # belongs to fam_b


def test_status_check_rejects_unknown_values(conn):
    plan = wp.create_plan(conn, "fam_local", "stu_1", "2026-01-05")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE week_plan SET status='bogus' WHERE plan_id=?", (plan.plan_id,))


def test_another_familys_plan_looks_missing(conn):
    plan = wp.create_plan(conn, "fam_local", "stu_1", "2026-01-05")
    with pytest.raises(wp.PlanNotFound):
        wp.get_plan(conn, "fam_b", plan.plan_id)
    assert wp.current_plans(conn, "fam_b", "2026-01-05") == []
    with pytest.raises(wp.PlanNotFound):
        wp.store_outlines(conn, "fam_b", plan.plan_id, _set())


def test_outlines_round_trip(conn):
    plan = wp.create_plan(conn, "fam_local", "stu_1", "2026-01-05")
    wp.store_outlines(conn, "fam_local", plan.plan_id, _set())
    got = wp.get_plan(conn, "fam_local", plan.plan_id)
    assert got.outlines is not None and got.outlines.get("c").topic == "Space"
    assert got.outlines_ready_at


def test_current_plans_lists_one_per_child(conn):
    wp.create_plan(conn, "fam_local", "stu_2", "2026-01-05")
    wp.create_plan(conn, "fam_local", "stu_1", "2026-01-05")
    wp.create_plan(conn, "fam_local", "stu_1", "2026-01-12")
    plans = wp.current_plans(conn, "fam_local", "2026-01-05")
    assert [p.student_id for p in plans] == ["stu_1", "stu_2"]
    latest = wp.latest_plan_for_student(conn, "fam_local", "stu_1")
    assert latest is not None and latest.week_start == "2026-01-12"


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["options"].pop(),  # two options
        lambda d: d["options"].append(_outline("a")),  # four options
        lambda d: d["options"][1].update(option_id="a"),  # duplicate id
        lambda d: d["options"][0].update(standard_ids=[]),  # no standards
        lambda d: d["options"][0].update(standard_ids=["X", "X"]),  # repeated standard
        lambda d: d["options"][0].update(topic="x" * 61),
        lambda d: d["options"][0].update(title=""),
        lambda d: d["options"][0].update(extra="nope"),
    ],
)
def test_outline_set_rejects_bad_shapes(mutate):
    data = _set().model_dump()
    mutate(data)
    with pytest.raises(ValidationError):
        OutlineSet.model_validate(data)


def test_outline_event_note_is_optional():
    assert Outline.model_validate(_outline("a")).event_note is None


def test_outlines_stored_with_the_old_difficulty_field_still_load():
    old = _outline("a")
    old["difficulty"] = "easier"
    assert (
        OutlineSet.model_validate({"options": [old, _outline("b"), _outline("c")]}).get("a").topic
        == "Dinosaurs"
    )
    assert (
        "difficulty"
        not in OutlineSet.model_validate(
            {"options": [old, _outline("b"), _outline("c")]}
        ).model_dump_json()
    )
