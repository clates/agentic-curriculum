from pydantic import ValidationError
import pytest

from src.resource_models import (
    MAX_MATH_PROBLEMS,
    MathWorksheetRequest,
    ReadingWorksheetRequest,
    ResourceRequests,
)


def build_math_payload(problem_count: int = 2):
    return {
        "title": "Repeated Addition Warm-Up",
        "instructions": "Solve and circle the sums",
        "problems": [
            {"operand_one": i, "operand_two": i + 1, "operator": "+"}
            for i in range(1, problem_count + 1)
        ],
        "metadata": {"artifact_label": "warmup"},
    }


def build_reading_payload(question_count: int = 2, vocab_count: int = 1):
    return {
        "passage_title": "Garden Morning",
        "passage": "Lina checked on the beans every morning.",
        "questions": [
            {"prompt": f"Question {i}", "response_lines": 2}
            for i in range(1, question_count + 1)
        ],
        "vocabulary": [
            {"term": f"word{i}", "definition": "definition"}
            for i in range(1, vocab_count + 1)
        ],
        "instructions": "Read and respond",
        "metadata": {"artifact_label": "literacy"},
    }


def test_math_request_accepts_valid_payload():
    payload = build_math_payload()
    request = MathWorksheetRequest.model_validate(payload)
    assert request.title == "Repeated Addition Warm-Up"
    assert len(request.problems) == 2
    assert request.problems[0].operator == "+"


def test_math_request_rejects_invalid_operator():
    payload = build_math_payload()
    payload["problems"][0]["operator"] = "*"
    with pytest.raises(ValidationError):
        MathWorksheetRequest.model_validate(payload)


def test_math_request_respects_problem_cap():
    payload = build_math_payload(problem_count=MAX_MATH_PROBLEMS + 1)
    with pytest.raises(ValidationError):
        MathWorksheetRequest.model_validate(payload)


def test_reading_request_accepts_valid_payload():
    payload = build_reading_payload()
    request = ReadingWorksheetRequest.model_validate(payload)
    assert request.passage_title == "Garden Morning"
    assert request.questions[0].prompt == "Question 1"


def test_reading_request_requires_passage_text():
    payload = build_reading_payload()
    payload["passage"] = "   "
    with pytest.raises(ValidationError):
        ReadingWorksheetRequest.model_validate(payload)


def test_resource_requests_helper_detects_presence():
    resources = ResourceRequests.model_validate({"mathWorksheet": build_math_payload()})
    assert resources.has_requests() is True
    assert resources.mathWorksheet is not None
    assert ResourceRequests.model_validate({}).has_requests() is False
