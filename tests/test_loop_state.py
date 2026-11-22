"""Tests for the loop state machine (M8.1): legal path, illegal transitions, replays, CAS."""

import sqlite3
import threading

import pytest

from src import week_plan as wp
from src.loop_state import ConcurrentUpdate, Event, IllegalTransition, TRANSITIONS, advance
from src.migrations import apply_migrations
from src.outline_models import OutlineSet

FAM = "fam_local"
NOW = "2026-01-01T00:00:00Z"
STATES = (
    "awaiting_feedback",
    "outlining",
    "awaiting_pick",
    "authoring",
    "ready",
    "printed",
    "expired",
)


def _outlines():
    def o(i, d):  # d is the topic
        return {
            "option_id": i,
            "title": i,
            "hook": "h",
            "topic": d,
            "standard_ids": ["VA.MATH.2.1"],
        }

    return OutlineSet.model_validate(
        {"options": [o("a", "Weather"), o("b", "Baking"), o("c", "Space")]}
    )


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "t.db"
    apply_migrations(path)
    c = sqlite3.connect(path)
    c.execute(
        "INSERT INTO student_profiles (student_id, progress_blob, plan_rules_blob, metadata_blob,"
        " family_id) VALUES ('stu_1','{}','{}','{}',?)",
        (FAM,),
    )
    c.commit()
    c.close()
    return path


@pytest.fixture
def conn(db):
    c = sqlite3.connect(db, timeout=10)
    c.execute("PRAGMA foreign_keys = ON")
    yield c
    c.close()


def _plan_in(conn, status, week="2026-01-05"):
    """Create a plan and walk it to ``status`` using only legal events."""
    plan = wp.create_plan(conn, FAM, "stu_1", week)
    path = {
        "awaiting_feedback": [],
        "outlining": ["feedback_submitted"],
        "awaiting_pick": ["feedback_submitted", "outlines_ready"],
        "expired": ["feedback_submitted", "outlines_ready", "pick_expired"],
        "authoring": ["feedback_submitted", "outlines_ready", "pick_made"],
        "ready": ["feedback_submitted", "outlines_ready", "pick_made", "authoring_done"],
        "printed": [
            "feedback_submitted",
            "outlines_ready",
            "pick_made",
            "authoring_done",
            "marked_printed",
        ],
    }[status]
    for kind in path:
        if kind == "outlines_ready":
            wp.store_outlines(conn, FAM, plan.plan_id, _outlines())
        advance(conn, FAM, plan.plan_id, _event(kind))
    return wp.get_plan(conn, FAM, plan.plan_id)


def _event(kind, **kw):
    payload = {"pick_made": {"option_id": "b"}, "authoring_done": {"packet_id": "pk_1"}}.get(
        kind, {}
    )
    return Event(kind, payload={**payload, **kw})


def test_happy_path(conn):
    plan = _plan_in(conn, "printed")
    assert plan.status == "printed" and plan.picked_option == "b" and plan.packet_id == "pk_1"
    assert plan.state_version == 5
    log = conn.execute("SELECT event_type FROM loop_event ORDER BY event_id").fetchall()
    assert [r[0] for r in log] == [
        "feedback_submitted",
        "outlines_ready",
        "pick_made",
        "authoring_done",
        "marked_printed",
    ]


@pytest.mark.parametrize("status", STATES)
@pytest.mark.parametrize("kind", sorted(TRANSITIONS))
def test_every_illegal_transition_raises_and_changes_nothing(conn, status, kind):
    allowed, target = TRANSITIONS[kind]
    plan = _plan_in(conn, status)
    if status in allowed or status == target:
        pytest.skip("legal, or a replay (covered elsewhere)")
    with pytest.raises(IllegalTransition):
        advance(conn, FAM, plan.plan_id, _event(kind))
    after = wp.get_plan(conn, FAM, plan.plan_id)
    assert after.status == status and after.state_version == plan.state_version


def test_unknown_event_is_illegal(conn):
    plan = _plan_in(conn, "awaiting_feedback")
    with pytest.raises(IllegalTransition):
        advance(conn, FAM, plan.plan_id, Event("explode"))


@pytest.mark.parametrize("status", ["outlining", "awaiting_pick", "authoring", "ready", "printed"])
def test_replaying_the_event_that_got_here_is_a_no_op(conn, status):
    plan = _plan_in(conn, status)
    last = {
        "outlining": "feedback_submitted",
        "awaiting_pick": "outlines_ready",
        "authoring": "pick_made",
        "ready": "authoring_done",
        "printed": "marked_printed",
    }[status]
    result = advance(conn, FAM, plan.plan_id, _event(last))
    assert result.applied is False
    assert result.plan.status == status and result.plan.state_version == plan.state_version


def test_keyed_replay_is_a_no_op_even_from_a_later_state(conn):
    plan = _plan_in(conn, "awaiting_feedback")
    first = advance(conn, FAM, plan.plan_id, Event("feedback_submitted", key="job-1"))
    assert first.applied
    again = advance(conn, FAM, plan.plan_id, Event("feedback_submitted", key="job-1"))
    assert again.applied is False and again.plan.state_version == first.plan.state_version
    n = conn.execute("SELECT COUNT(*) FROM loop_event WHERE event_key='job-1'").fetchone()[0]
    assert n == 1


def test_replaying_a_pick_with_a_different_option_is_illegal(conn):
    plan = _plan_in(conn, "authoring")
    with pytest.raises(IllegalTransition):
        advance(conn, FAM, plan.plan_id, Event("pick_made", payload={"option_id": "a"}))


def test_pick_needs_a_real_option_and_outlines(conn):
    plan = _plan_in(conn, "awaiting_pick")
    with pytest.raises(IllegalTransition):
        advance(conn, FAM, plan.plan_id, Event("pick_made", payload={"option_id": "z"}))
    with pytest.raises(IllegalTransition):
        advance(conn, FAM, plan.plan_id, Event("authoring_done", payload={}))


def test_authoring_done_needs_a_packet(conn):
    plan = _plan_in(conn, "authoring")
    with pytest.raises(IllegalTransition):
        advance(conn, FAM, plan.plan_id, Event("authoring_done"))


def test_regenerate_clears_outlines_and_returns_to_outlining(conn):
    for start in ("awaiting_pick", "expired"):
        plan = _plan_in(conn, start, week="2026-01-12" if start == "expired" else "2026-01-05")
        got = advance(conn, FAM, plan.plan_id, Event("outlines_regenerate")).plan
        assert got.status == "outlining" and got.outlines is None and got.picked_option is None


def test_needs_attention_is_a_flag_in_every_state(conn):
    for i, status in enumerate(STATES):
        plan = _plan_in(conn, status, week=f"2026-02-{i + 1:02d}")
        flagged = advance(
            conn, FAM, plan.plan_id, Event("flag_attention", payload={"reason": "slow"})
        )
        assert flagged.applied and flagged.plan.needs_attention and flagged.plan.status == status
        assert flagged.plan.attention_reason == "slow"
        again = advance(
            conn, FAM, plan.plan_id, Event("flag_attention", payload={"reason": "slow"})
        )
        assert again.applied is False
        cleared = advance(conn, FAM, plan.plan_id, Event("clear_attention"))
        assert cleared.applied and not cleared.plan.needs_attention
        assert advance(conn, FAM, plan.plan_id, Event("clear_attention")).applied is False


def test_other_family_cannot_advance_a_plan(conn):
    plan = _plan_in(conn, "awaiting_feedback")
    with pytest.raises(wp.PlanNotFound):
        advance(conn, "fam_other", plan.plan_id, _event("feedback_submitted"))


def test_two_connections_racing_exactly_one_wins(db):
    setup = sqlite3.connect(db)
    setup.execute("PRAGMA foreign_keys = ON")
    plan = wp.create_plan(setup, FAM, "stu_1", "2026-03-02")
    setup.close()
    results, barrier = [], threading.Barrier(4)

    def worker(n):
        c = sqlite3.connect(db, timeout=10)
        c.execute("PRAGMA foreign_keys = ON")
        barrier.wait()
        results.append(advance(c, FAM, plan.plan_id, Event("feedback_submitted", key=f"w{n}")))
        c.close()

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(4)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert sum(r.applied for r in results) == 1
    c = sqlite3.connect(db)
    assert c.execute("SELECT status, state_version FROM week_plan").fetchone() == ("outlining", 1)
    assert c.execute("SELECT COUNT(*) FROM loop_event").fetchone()[0] == 1


def test_stale_compare_and_set_gives_up_with_concurrent_update(conn, monkeypatch):
    plan = _plan_in(conn, "awaiting_feedback")
    real = conn.execute

    class Bumper:
        """Bump state_version before every update so the CAS can never match."""

        def __init__(self, c):
            self.c = c

        def execute(self, sql, params=()):
            if sql.startswith("UPDATE week_plan SET status"):
                real("UPDATE week_plan SET state_version = state_version + 1")
            return real(sql, params)

        def __getattr__(self, name):
            return getattr(self.c, name)

    with pytest.raises(ConcurrentUpdate):
        advance(Bumper(conn), FAM, plan.plan_id, _event("feedback_submitted"))
