"""M5.4: shaky returns at 1, 2, 4 weeks; missed is due now; mastered keeps its cooldown."""

import json

from src.feedback_processor import is_standard_eligible, process_mastery_feedback
from src.review_policy import review_due, review_schedule

BLANK = json.dumps({"mastered_standards": [], "developing_standards": []})
T0 = "2026-01-05T10:00:00Z"


def _ids(due):
    return [d["standard_id"] for d in due]


def test_missed_is_due_now():
    b = process_mastery_feedback(BLANK, {"S.m": "STRUGGLING"}, T0, packet_id="p1")
    assert _ids(review_due(b, T0)) == ["S.m"]


def test_shaky_returns_at_one_week():
    b = process_mastery_feedback(BLANK, {"S.s": "DEVELOPING"}, T0, packet_id="p1")
    assert review_due(b, "2026-01-11T10:00:00Z") == []  # day 6
    assert _ids(review_due(b, "2026-01-12T10:00:00Z")) == ["S.s"]  # day 7


def test_shaky_again_stretches_to_two_then_four_weeks():
    b = process_mastery_feedback(BLANK, {"S.s": "DEVELOPING"}, T0, packet_id="p1")
    b = process_mastery_feedback(b, {"S.s": "DEVELOPING"}, "2026-01-12T10:00:00Z", packet_id="p2")
    sched = {r["standard_id"]: r for r in review_schedule(b)}
    assert sched["S.s"]["due_at"] == "2026-01-26T10:00:00Z"  # +2 weeks
    b = process_mastery_feedback(b, {"S.s": "DEVELOPING"}, "2026-01-26T10:00:00Z", packet_id="p3")
    assert review_schedule(b)[0]["due_at"] == "2026-02-23T10:00:00Z"  # +4 weeks
    b = process_mastery_feedback(b, {"S.s": "DEVELOPING"}, "2026-02-23T10:00:00Z", packet_id="p4")
    assert review_schedule(b)[0]["due_at"] == "2026-03-23T10:00:00Z"  # capped at 4


def test_shaky_streak_resets_after_a_win():
    b = process_mastery_feedback(BLANK, {"S.s": "DEVELOPING"}, T0, packet_id="p1")
    b = process_mastery_feedback(b, {"S.s": "MASTERED"}, "2026-01-12T10:00:00Z", packet_id="p2")
    b = process_mastery_feedback(b, {"S.s": "DEVELOPING"}, "2026-01-19T10:00:00Z", packet_id="p3")
    assert review_schedule(b)[0]["due_at"] == "2026-01-26T10:00:00Z"  # 1 week again


def test_mastered_keeps_its_cooldown():
    b = process_mastery_feedback(BLANK, {"S.g": "MASTERED"}, T0, packet_id="p1")
    assert review_due(b, "2026-01-12T10:00:00Z") == []
    assert _ids(review_due(b, "2026-01-19T10:00:00Z")) == ["S.g"]  # 2 weeks
    meta = json.loads(b)["standard_metadata"]["S.g"]
    # Agrees with the self-hosted eligibility rule, which stays untouched.
    assert is_standard_eligible(meta, "2026-01-19T10:00:00Z")
    assert not is_standard_eligible(meta, "2026-01-12T10:00:00Z")


def test_ordering_missed_then_shaky_then_mastered():
    b = BLANK
    for i, (sid, rating) in enumerate(
        [("S.g", "MASTERED"), ("S.s", "DEVELOPING"), ("S.m", "STRUGGLING")]
    ):
        b = process_mastery_feedback(b, {sid: rating}, T0, packet_id=f"p{i}")
    assert _ids(review_due(b, "2026-03-01T00:00:00Z")) == ["S.m", "S.s", "S.g"]


def test_no_feedback_means_nothing_due():
    assert review_due(BLANK, T0) == []
    assert review_due(None, T0) == []
