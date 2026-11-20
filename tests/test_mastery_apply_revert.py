"""M5.2: idempotent mastery apply and exact revert, keyed by packet_id."""

import copy
import json

from src.feedback_processor import (
    is_standard_eligible,
    process_mastery_feedback,
    revert_mastery_feedback,
)

D1, D2, D3 = "2026-01-05T10:00:00Z", "2026-01-12T10:00:00Z", "2026-01-19T10:00:00Z"
START = {"mastered_standards": ["S.old"], "developing_standards": ["S.dev"]}


def _apply(blob, fb, date, packet):
    return process_mastery_feedback(blob, fb, date, packet_id=packet)


def _sets(blob):
    p = json.loads(blob)
    return set(p["mastered_standards"]), set(p["developing_standards"])


def test_same_feedback_twice_changes_nothing():
    once = _apply(json.dumps(START), {"S.a": "MASTERED", "S.b": "DEVELOPING"}, D1, "p1")
    twice = _apply(once, {"S.a": "MASTERED", "S.b": "DEVELOPING"}, D2, "p1")
    assert twice == once  # even the date stays put


def test_edit_reverts_and_reapplies_without_double_counting():
    once = _apply(json.dumps(START), {"S.a": "MASTERED"}, D1, "p1")
    edited = _apply(once, {"S.a": "STRUGGLING"}, D2, "p1")
    mastered, developing = _sets(edited)
    assert "S.a" not in mastered and "S.a" in developing
    hist = json.loads(edited)["standard_metadata"]["S.a"]["feedback_history"]
    assert [h["rating"] for h in hist] == ["STRUGGLING"]  # one entry, not two


def test_edit_that_drops_a_standard_removes_its_effect():
    once = _apply(json.dumps(START), {"S.a": "MASTERED", "S.b": "MASTERED"}, D1, "p1")
    edited = _apply(once, {"S.a": "MASTERED"}, D2, "p1")
    p = json.loads(edited)
    assert "S.b" not in p["standard_metadata"]
    assert "S.b" not in p["mastered_standards"]


def test_revert_restores_original_exactly():
    original = json.dumps(START)
    applied = _apply(
        original, {"S.old": "STRUGGLING", "S.dev": "MASTERED", "S.new": "MASTERED"}, D1, "p1"
    )
    assert json.loads(revert_mastery_feedback(applied, "p1")) == {
        **START,
        "standard_metadata": {},
    }


def test_revert_keeps_other_packets():
    b = _apply(json.dumps(START), {"S.a": "MASTERED"}, D1, "p1")
    b = _apply(b, {"S.a": "DEVELOPING"}, D2, "p2")
    assert "S.a" in _sets(b)[1]
    reverted = revert_mastery_feedback(b, "p2")
    assert "S.a" in _sets(reverted)[0]
    assert reverted == _apply(json.dumps(START), {"S.a": "MASTERED"}, D1, "p1")


def test_consecutive_mastery_grows_cooldown_and_replays_deterministically():
    b = json.dumps(START)
    for i, d in enumerate((D1, D2, D3)):
        b = _apply(b, {"S.a": "MASTERED"}, d, f"p{i}")
    assert json.loads(b)["standard_metadata"]["S.a"]["cooldown_weeks"] == 4
    # Editing the middle packet re-derives from base, in order.
    edited = _apply(b, {"S.a": "DEVELOPING"}, D2, "p1")
    assert json.loads(edited)["standard_metadata"]["S.a"]["cooldown_weeks"] == 2


def test_shaky_does_not_hide_the_standard():
    b = _apply(json.dumps(START), {"S.a": "DEVELOPING"}, D1, "p1")
    meta = json.loads(b)["standard_metadata"]["S.a"]
    assert meta["cooldown_weeks"] == 0
    assert is_standard_eligible(meta, "2026-01-06T10:00:00Z")


def test_mastered_after_shaky_gets_a_real_cooldown():
    b = _apply(json.dumps(START), {"S.a": "DEVELOPING"}, D1, "p1")
    b = _apply(b, {"S.a": "MASTERED"}, D2, "p2")
    assert json.loads(b)["standard_metadata"]["S.a"]["cooldown_weeks"] == 2


def test_legacy_untagged_history_is_not_replayed_twice():
    legacy = {
        "mastered_standards": ["S.a"],
        "developing_standards": [],
        "standard_metadata": {
            "S.a": {
                "feedback_history": [
                    {"date": D1, "rating": "MASTERED"},
                    {"date": D2, "rating": "MASTERED"},
                ],
                "last_seen": D2,
                "last_feedback": "MASTERED",
                "cooldown_weeks": 3,
            }
        },
    }
    before = copy.deepcopy(legacy)
    b = _apply(json.dumps(legacy), {"S.a": "MASTERED"}, D3, "p1")
    assert json.loads(b)["standard_metadata"]["S.a"]["cooldown_weeks"] == 4
    assert json.loads(revert_mastery_feedback(b, "p1")) == before


def test_untagged_call_still_works_like_before():
    b = process_mastery_feedback(json.dumps(START), {"S.a": "MASTERED"}, D1)
    assert "S.a" in _sets(b)[0]
