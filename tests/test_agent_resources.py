import pytest

import src.agent as agent
from src.prompts import build_lesson_plan_prompt, RESOURCE_GUIDANCE

_extract_lesson_and_resources = agent._extract_lesson_and_resources


@pytest.fixture
def sample_rules():
    return {"allowed_materials": ["Paper", "Counters"], "parent_notes": "stay upbeat"}


@pytest.fixture
def sample_standard():
    return {"description": "Practice repeated addition", "subject": "Math", "grade_level": 2}


def test_prompt_mentions_resources(sample_standard, sample_rules):
    allowed_materials = sample_rules["allowed_materials"]
    parent_notes = sample_rules["parent_notes"]
    prompt = build_lesson_plan_prompt(sample_standard, allowed_materials, parent_notes)
    assert "resources" in prompt
    assert RESOURCE_GUIDANCE.strip() in prompt


def test_extract_without_resources():
    lesson = {"objective": "Learn"}
    payload = {"lesson_plan": lesson}
    parsed_lesson, resources = _extract_lesson_and_resources(payload, "Monday")
    assert parsed_lesson == lesson
    assert resources is None


def test_extract_with_math_resources():
    payload = {
        "lesson_plan": {"objective": "Practice"},
        "resources": {
            "mathWorksheet": {
                "problems": [
                    {"operand_one": 2, "operand_two": 3, "operator": "+"},
                ]
            }
        },
    }
    parsed_lesson, resources = _extract_lesson_and_resources(payload, "Tuesday")
    assert parsed_lesson == payload["lesson_plan"]
    assert resources is not None
    assert resources.mathWorksheet is not None
    assert resources.mathWorksheet.problems[0].operator == "+"


def test_extract_invalid_resources_logs_and_drops(capsys):
    payload = {
        "lesson_plan": {"objective": "Practice"},
        "resources": {
            "mathWorksheet": {
                "problems": [
                    {"operand_one": 2, "operand_two": 3, "operator": "*"},
                ]
            }
        },
    }
    _, resources = _extract_lesson_and_resources(payload, "Wednesday")
    captured = capsys.readouterr()
    assert "Invalid worksheet resources" in captured.out
    assert resources is None


def test_extract_with_reading_resources():
    payload = {
        "lesson_plan": {"objective": "Comprehension"},
        "resources": {
            "readingWorksheet": {
                "passage_title": "Garden Morning",
                "passage": "Lina checked on the beans every morning.",
                "questions": [{"prompt": "What did Lina do?"}],
            }
        },
    }
    _, resources = _extract_lesson_and_resources(payload, "Thursday")
    assert resources is not None
    assert resources.readingWorksheet is not None
    assert resources.readingWorksheet.passage_title == "Garden Morning"
