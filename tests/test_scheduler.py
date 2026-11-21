"""Scheduler tests (M8.4) with an injected clock: windows, DST, timezones, idempotency, expiry."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

import jobs
import loop_state as ls
import scheduler
import week_plan as wp
from migrations import apply_migrations
from outline_models import OutlineSet

NY = ZoneInfo("America/New_York")
LA = ZoneInfo("America/Los_Angeles")


def at(tz, y, m, d, h=0, mi=0):
    return datetime(y, m, d, h, mi, tzinfo=tz)


def utc(y, m, d, h=0, mi=0):
    return datetime(y, m, d, h, mi, tzinfo=UTC)


def outlines():
    def o(i, d):
        return {
            "option_id": i,
            "title": i,
            "hook": "h",
            "difficulty": d,
            "standard_ids": ["VA.MATH.2.1"],
        }

    return OutlineSet.model_validate(
        {"options": [o("a", "easier"), o("b", "on_level"), o("c", "stretch")]}
    )


@pytest.fixture
def conn(tmp_path):
    path = str(tmp_path / "s.db")
    apply_migrations(path)
    c = jobs.connect(path)
    set_tz(c, "fam_local", "America/New_York")
    c.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, "
        "metadata_blob, family_id) VALUES ('stu_1','{}','{}','{}','fam_local')"
    )
    yield c
    c.close()


def set_tz(conn, fam, tz):
    conn.execute(
        "INSERT OR REPLACE INTO family_settings (family_id, timezone, updated_at) "
        "VALUES (?,?,'2026-01-01T00:00:00Z')",
        (fam, tz),
    )


def add_family(conn, fam, tz, student="stu_x"):
    conn.execute(
        "INSERT INTO family (family_id, name, created_at) VALUES (?,?,?)",
        (fam, fam, "2026-01-01T00:00:00Z"),
    )
    set_tz(conn, fam, tz)
    conn.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, "
        "metadata_blob, family_id) VALUES (?,'{}','{}','{}',?)",
        (student, fam),
    )
    conn.commit()


def all_jobs(conn):
    return [
        (r["family_id"], r["kind"], r["idempotency_key"])
        for r in conn.execute("SELECT * FROM jobs ORDER BY id")
    ]


def plan_of(conn, fam="fam_local", student="stu_1", week=None):
    row = conn.execute(
        "SELECT plan_id FROM week_plan WHERE family_id=? AND student_id=?"
        + (" AND week_start=?" if week else ""),
        (fam, student) + ((week,) if week else ()),
    ).fetchone()
    return wp.get_plan(conn, fam, row[0])


def to_pick(conn, plan):
    ls.advance(conn, plan.family_id, plan.plan_id, ls.Event("feedback_submitted"))
    wp.store_outlines(conn, plan.family_id, plan.plan_id, outlines())
    ls.advance(conn, plan.family_id, plan.plan_id, ls.Event("outlines_ready"))


def test_no_planning_monday_to_thursday(conn):
    rep = scheduler.tick(at(NY, 2026, 1, 8, 12), conn)  # Thursday
    assert not rep.plans_created and not all_jobs(conn)


def test_friday_creates_plan_with_local_deadlines_and_reminds_at_3pm(conn):
    rep = scheduler.tick(at(NY, 2026, 1, 9, 14, 59), conn)  # Fri, 1 min before the window
    assert len(rep.plans_created) == 1 and all_jobs(conn) == []
    plan = plan_of(conn)
    assert plan.week_start == "2026-01-12" and plan.status == "awaiting_feedback"
    assert plan.pick_deadline == "2026-01-11T17:00:00.000000Z"  # Sun 12:00 EST
    assert plan.print_deadline == "2026-01-12T01:00:00.000000Z"  # Sun 20:00 EST
    scheduler.tick(at(NY, 2026, 1, 9, 15, 0), conn)
    assert all_jobs(conn) == [("fam_local", "send_notice", "reminder:fam_local:2026-01-12")]
    payload = conn.execute("SELECT payload_json FROM jobs").fetchone()[0]
    assert "stu_1" not in payload and "plan_ids" in payload


def test_double_tick_and_many_ticks_enqueue_nothing_new(conn):
    now = at(NY, 2026, 1, 10, 11)  # Saturday after the safety-net time
    first = scheduler.tick(now, conn)
    before = all_jobs(conn)
    assert first.jobs_enqueued and before
    for minute in range(0, 30):
        rep = scheduler.tick(at(NY, 2026, 1, 10, 11, minute), conn)
        assert not (rep.jobs_enqueued or rep.plans_created or rep.expired or rep.safety_net)
    assert all_jobs(conn) == before
    assert conn.execute("SELECT COUNT(*) FROM week_plan").fetchone()[0] == 1


def test_saturday_safety_net_moves_on_and_enqueues_outline_once(conn):
    scheduler.tick(at(NY, 2026, 1, 9, 16), conn)
    scheduler.tick(at(NY, 2026, 1, 10, 9, 59), conn)
    assert plan_of(conn).status == "awaiting_feedback"
    rep = scheduler.tick(at(NY, 2026, 1, 10, 10, 0), conn)
    plan = plan_of(conn)
    assert plan.status == "outlining" and rep.safety_net == [plan.plan_id]
    assert ("fam_local", "outline", f"outlines:{plan.plan_id}") in all_jobs(conn)
    scheduler.tick(at(NY, 2026, 1, 10, 10, 1), conn)
    assert [j for j in all_jobs(conn) if j[1] == "outline"] == [
        ("fam_local", "outline", f"outlines:{plan.plan_id}")
    ]
    ev = conn.execute(
        "SELECT payload_json FROM loop_event WHERE event_type='feedback_submitted'"
    ).fetchone()[0]
    assert "safety_net" in ev


def test_nudge_goes_to_awaiting_pick_only_and_once(conn):
    scheduler.tick(at(NY, 2026, 1, 9, 16), conn)
    to_pick(conn, plan_of(conn))
    scheduler.tick(at(NY, 2026, 1, 10, 10, 0), conn)
    scheduler.tick(at(NY, 2026, 1, 10, 10, 1), conn)
    notices = [j for j in all_jobs(conn) if j[1] == "send_notice"]
    assert notices[-1] == ("fam_local", "send_notice", "nudge:fam_local:2026-01-12")
    assert len([n for n in notices if n[2].startswith("nudge")]) == 1


def test_catch_up_sends_only_the_latest_window(conn):
    # scheduler was down Fri-Sat; first tick is Sunday 09:00
    scheduler.tick(at(NY, 2026, 1, 8, 12), conn)  # nothing (Thursday)
    from week_plan import create_plan

    p = create_plan(conn, "fam_local", "stu_1", "2026-01-12")
    to_pick(conn, p)
    scheduler.tick(at(NY, 2026, 1, 11, 9, 0), conn)
    keys = [j[2] for j in all_jobs(conn) if j[1] == "send_notice"]
    assert keys == ["lastcall:fam_local:2026-01-12"]


def test_expiry_of_awaiting_pick_at_deadline_then_no_more_notices(conn):
    scheduler.tick(at(NY, 2026, 1, 9, 16), conn)
    to_pick(conn, plan_of(conn))
    rep = scheduler.tick(utc(2026, 1, 11, 16, 59), conn)  # 11:59 EST Sunday
    assert not rep.expired and plan_of(conn).status == "awaiting_pick"
    rep = scheduler.tick(utc(2026, 1, 11, 17, 0), conn)  # 12:00 EST
    assert len(rep.expired) == 1 and plan_of(conn).status == "expired"
    assert not scheduler.tick(utc(2026, 1, 11, 17, 1), conn).expired


def test_picked_week_gets_one_author_job_and_regeneration_gets_a_new_key(conn):
    scheduler.tick(at(NY, 2026, 1, 9, 16), conn)
    p = plan_of(conn)
    to_pick(conn, p)
    ls.advance(conn, p.family_id, p.plan_id, ls.Event("pick_made", payload={"option_id": "b"}))
    scheduler.tick(at(NY, 2026, 1, 10, 12), conn)
    scheduler.tick(at(NY, 2026, 1, 10, 12, 1), conn)
    assert [j for j in all_jobs(conn) if j[1] == "author"] == [
        ("fam_local", "author", f"author:{p.plan_id}:b")
    ]
    # outlines regeneration after an expiry is new work, not a duplicate of the first round
    p2 = wp.create_plan(conn, "fam_local", "stu_1", "2026-01-19")
    to_pick(conn, p2)
    ls.advance(conn, p2.family_id, p2.plan_id, ls.Event("pick_expired"))
    ls.advance(conn, p2.family_id, p2.plan_id, ls.Event("outlines_regenerate"))
    jobs.enqueue(conn, "fam_local", "outline", f"outlines:{p2.plan_id}")  # round 0 already ran
    scheduler.tick(at(NY, 2026, 1, 16, 12), conn)  # Friday before 2026-01-19
    assert ("fam_local", "outline", f"outlines:{p2.plan_id}:r1") in all_jobs(conn)


def test_spring_forward_week_deadlines_and_expiry(conn):
    # US DST starts Sun 2026-03-08 at 02:00. Target Monday is 2026-03-09.
    scheduler.tick(at(NY, 2026, 3, 6, 16), conn)
    p = plan_of(conn)
    assert p.week_start == "2026-03-09"
    assert p.feedback_due_at == "2026-03-06T20:00:00.000000Z"  # Fri 15:00 EST
    assert p.pick_deadline == "2026-03-08T16:00:00.000000Z"  # Sun 12:00 EDT (not 17:00Z)
    assert p.print_deadline == "2026-03-09T00:00:00.000000Z"  # Sun 20:00 EDT
    to_pick(conn, p)
    assert not scheduler.tick(utc(2026, 3, 8, 15, 59), conn).expired
    assert len(scheduler.tick(utc(2026, 3, 8, 16, 0), conn).expired) == 1


def test_fall_back_week_deadlines_and_expiry(conn):
    # US DST ends Sun 2026-11-01 at 02:00. Target Monday is 2026-11-02.
    scheduler.tick(at(NY, 2026, 10, 30, 16), conn)
    p = plan_of(conn)
    assert p.week_start == "2026-11-02"
    assert p.feedback_due_at == "2026-10-30T19:00:00.000000Z"  # Fri 15:00 EDT
    assert p.pick_deadline == "2026-11-01T17:00:00.000000Z"  # Sun 12:00 EST (not 16:00Z)
    to_pick(conn, p)
    assert not scheduler.tick(utc(2026, 11, 1, 16, 59), conn).expired
    assert len(scheduler.tick(utc(2026, 11, 1, 17, 0), conn).expired) == 1


def test_saturday_window_instant_across_dst_change(conn):
    # Sat 10:00 local before the Sunday change is EST: 15:00Z. 14:59Z is still before it.
    scheduler.tick(at(NY, 2026, 3, 6, 16), conn)
    scheduler.tick(utc(2026, 3, 7, 14, 59), conn)
    assert plan_of(conn).status == "awaiting_feedback"
    scheduler.tick(utc(2026, 3, 7, 15, 0), conn)
    assert plan_of(conn).status == "outlining"


def test_two_timezones_fire_at_their_own_local_time(conn):
    add_family(conn, "fam_la", "America/Los_Angeles")
    # Fri 2026-01-09 15:00 EST = 20:00Z (NY due), 15:00 PST = 23:00Z (LA not yet)
    scheduler.tick(utc(2026, 1, 9, 20, 0), conn)
    reminders = [j for j in all_jobs(conn) if j[2].startswith("reminder")]
    assert reminders == [("fam_local", "send_notice", "reminder:fam_local:2026-01-12")]
    scheduler.tick(utc(2026, 1, 9, 23, 0), conn)
    reminders = [j[0] for j in all_jobs(conn) if j[2].startswith("reminder")]
    assert sorted(reminders) == ["fam_la", "fam_local"]
    la = plan_of(conn, "fam_la", "stu_x")
    assert la.pick_deadline == "2026-01-11T20:00:00.000000Z"  # Sun 12:00 PST


def test_week_boundary_late_sunday_and_monday(conn):
    scheduler.tick(at(NY, 2026, 1, 9, 16), conn)
    # Sunday 23:30 local: past the print deadline, still the same target week, no new notice
    scheduler.tick(at(NY, 2026, 1, 11, 23, 30), conn)
    assert conn.execute("SELECT COUNT(*) FROM week_plan").fetchone()[0] == 1
    # Monday: planning for the *following* week has not started
    rep = scheduler.tick(at(NY, 2026, 1, 12, 8), conn)
    assert not rep.plans_created
    # Next Friday plans the week after
    rep = scheduler.tick(at(NY, 2026, 1, 16, 9), conn)
    assert plan_of(conn, week="2026-01-19").status == "awaiting_feedback"


def test_bad_timezone_isolated_to_its_family(conn):
    add_family(conn, "fam_bad", "Mars/Olympus")
    rep = scheduler.tick(at(NY, 2026, 1, 9, 16), conn)
    assert rep.errors and rep.errors[0].startswith("fam_bad")
    assert plan_of(conn).status == "awaiting_feedback"  # the good family still got its plan


def test_null_timezone_uses_default(conn, monkeypatch):
    conn.execute("DELETE FROM family_settings")
    monkeypatch.setenv("SCHEDULER_DEFAULT_TZ", "America/Los_Angeles")
    scheduler.tick(utc(2026, 1, 9, 22, 59), conn)
    assert not [j for j in all_jobs(conn)]
    scheduler.tick(utc(2026, 1, 9, 23, 0), conn)
    assert all_jobs(conn)


def test_naive_now_rejected(conn):
    with pytest.raises(ValueError):
        scheduler.tick(datetime(2026, 1, 9, 15), conn)
