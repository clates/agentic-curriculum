import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trio_generator


def _make_profile(name: str = "Alice") -> dict:
    return {
        "student_id": "s1",
        "progress_blob": json.dumps({"mastered_standards": [], "developing_standards": []}),
        "plan_rules_blob": json.dumps({}),
        "metadata_blob": json.dumps({"name": name}),
    }


def test_generates_three_plans_and_notifies():
    with (
        patch("trio_generator.get_student_profile", return_value=_make_profile("Alice")),
        patch("trio_generator._get_grade_level", return_value=2),
        patch("trio_generator.pick_subjects", return_value=["Math", "English", "Science"]),
        patch("trio_generator.generate_weekly_plan", return_value={"ok": True}) as mock_gen,
        patch("trio_generator.notify") as mock_notify,
    ):
        trio_generator.generate_trio_for_student("s1")

    assert mock_gen.call_count == 3
    subjects_called = {c.kwargs["subject"] for c in mock_gen.call_args_list}
    assert subjects_called == {"Math", "English", "Science"}
    mock_notify.assert_called_once()
    assert "Alice" in mock_notify.call_args[0][0]


def test_notifies_failure_on_exception():
    with (
        patch("trio_generator.get_student_profile", return_value=_make_profile("Bob")),
        patch("trio_generator._get_grade_level", return_value=0),
        patch("trio_generator.pick_subjects", return_value=["Math", "English", "Science"]),
        patch("trio_generator.generate_weekly_plan", side_effect=RuntimeError("openai down")),
        patch("trio_generator.notify") as mock_notify,
    ):
        import pytest

        with pytest.raises(RuntimeError):
            trio_generator.generate_trio_for_student("s1")

    mock_notify.assert_called_once()
    title = mock_notify.call_args[0][0]
    assert "FAILED" in title
    priority = mock_notify.call_args[1].get("priority") or mock_notify.call_args[0][2]
    assert priority == "high"


def test_get_grade_level_from_most_recent_packet():
    packets = [{"grade_level": 3}, {"grade_level": 1}]
    with patch("trio_generator.list_weekly_packets", return_value=(packets, False)):
        assert trio_generator._get_grade_level("s1") == 3


def test_get_grade_level_defaults_to_zero_when_no_packets():
    with patch("trio_generator.list_weekly_packets", return_value=([], False)):
        assert trio_generator._get_grade_level("s1") == 0


def test_get_grade_level_uses_metadata_fallback_when_no_packets():
    with patch("trio_generator.list_weekly_packets", return_value=([], False)):
        assert trio_generator._get_grade_level("s1", metadata_fallback={"grade_level": 4}) == 4


def test_get_grade_level_empty_metadata_dict_falls_back_to_zero():
    """An empty metadata dict ({}) must not be treated as falsy — grade must default to 0."""
    with patch("trio_generator.list_weekly_packets", return_value=([], False)):
        assert trio_generator._get_grade_level("s1", metadata_fallback={}) == 0


def test_get_grade_level_kindergarten_metadata_returns_zero():
    """metadata_fallback with grade_level=0 (Kindergarten) must return 0, not 1."""
    with patch("trio_generator.list_weekly_packets", return_value=([], False)):
        assert trio_generator._get_grade_level("s1", metadata_fallback={"grade_level": 0}) == 0
