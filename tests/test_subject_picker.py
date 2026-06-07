import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from subject_picker import pick_subjects


def _make_profile(developing: list[str]) -> dict:
    return {
        "student_id": "test_student",
        "progress_blob": json.dumps(
            {
                "mastered_standards": [],
                "developing_standards": developing,
            }
        ),
        "plan_rules_blob": json.dumps({}),
        "metadata_blob": json.dumps({}),
    }


def _make_graph(node_ids: list[str]) -> MagicMock:
    g = MagicMock()
    g.graph.nodes.return_value = node_ids
    return g


def test_returns_three_subjects():
    profile = _make_profile(["MATH.1", "MATH.2", "ENG.1", "SCI.1", "SCI.2", "SCI.3", "HIST.1"])

    def fake_load(db_path, subject_keyword=None):
        mapping = {
            "Math": ["MATH.1", "MATH.2"],
            "English": ["ENG.1"],
            "Science": ["SCI.1", "SCI.2", "SCI.3"],
            "History": ["HIST.1"],
            "Computer Science": [],
        }
        return _make_graph(mapping.get(subject_keyword, []))

    with (
        patch("subject_picker.get_student_profile", return_value=profile),
        patch("subject_picker.load_from_db", side_effect=fake_load),
    ):
        result = pick_subjects("test_student")

    assert len(result) == 3
    assert result[0] == "Science"  # 3 developing
    assert result[1] == "Math"  # 2 developing
    assert result[2] == "English"  # 1 developing (History also has 1, tie broken by SUBJECTS order)


def test_falls_back_when_progress_sparse():
    profile = _make_profile([])  # no developing standards

    with (
        patch("subject_picker.get_student_profile", return_value=profile),
        patch("subject_picker.load_from_db", return_value=_make_graph([])),
    ):
        result = pick_subjects("test_student")

    assert len(result) == 3
    # Falls back to first 3 from SUBJECTS
    from constants import SUBJECTS

    assert result == SUBJECTS[:3]


def test_falls_back_when_only_one_subject_has_gap():
    profile = _make_profile(["MATH.1"])

    def fake_load(db_path, subject_keyword=None):
        return _make_graph(["MATH.1"] if subject_keyword == "Math" else [])

    with (
        patch("subject_picker.get_student_profile", return_value=profile),
        patch("subject_picker.load_from_db", side_effect=fake_load),
    ):
        result = pick_subjects("test_student")

    assert len(result) == 3
    assert "Math" in result


def test_raises_when_student_not_found():
    with patch("subject_picker.get_student_profile", return_value=None):
        import pytest

        with pytest.raises(ValueError, match="Student not found"):
            pick_subjects("ghost_student")
