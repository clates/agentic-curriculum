"""M5.1: Got it / Shaky / Missed to mastery states (pure)."""

from types import SimpleNamespace as C

import pytest

from src.check_mastery import map_check_results, normalize_result
from src.weekdoc import PrepCheck

CHECKS = [
    C(id="c1", standard_id="S.a"),
    C(id="c2", standard_id="S.a"),
    C(id="c3", standard_id="S.b"),
    C(id="c4", standard_id="S.c"),
    C(id="c5", standard_id="S.c"),
]


def test_across_several_standards():
    out = map_check_results(
        CHECKS,
        {"c1": "got_it", "c2": "got_it", "c3": "shaky", "c4": "got_it", "c5": "missed"},
    )
    assert out == {"S.a": "MASTERED", "S.b": "DEVELOPING", "S.c": "STRUGGLING"}


def test_missed_wins_over_shaky_and_got_it():
    checks = [C(id=f"k{i}", standard_id="S.x") for i in range(3)]
    out = map_check_results(checks, {"k0": "got_it", "k1": "shaky", "k2": "missed"})
    assert out == {"S.x": "STRUGGLING"}


def test_shaky_beats_got_it():
    out = map_check_results(CHECKS, {"c1": "got_it", "c2": "shaky"})
    assert out == {"S.a": "DEVELOPING"}


def test_no_over_crediting_when_a_check_is_unanswered():
    # S.a has two checks, only one ticked Got it: not enough to call it mastered.
    assert map_check_results(CHECKS, {"c1": "got_it"}) == {}
    # ...but a miss on a partial standard still counts.
    assert map_check_results(CHECKS, {"c1": "missed"}) == {"S.a": "STRUGGLING"}


def test_empty_results_change_nothing():
    assert map_check_results(CHECKS, {}) == {}


def test_labels_are_forgiving():
    assert normalize_result("Got it") == "got_it"
    assert normalize_result(" SHAKY ") == "shaky"
    assert normalize_result("Missed") == "missed"


def test_rejects_unknown_values_and_checks():
    with pytest.raises(ValueError):
        map_check_results(CHECKS, {"c1": "great"})
    with pytest.raises(ValueError):
        map_check_results(CHECKS, {"nope": "got_it"})


def test_accepts_real_prep_checks():
    check = PrepCheck(
        id="q1",
        day="Monday",
        standard_id="VA.SCIENCE.K.k.6",
        kind="oral",
        prompt="Ask what plants need.",
        pass_criteria="Says water and light.",
    )
    assert map_check_results([check], {"q1": "got_it"}) == {"VA.SCIENCE.K.k.6": "MASTERED"}
