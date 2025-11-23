from src.resource_models import ResourceRequests
from src.worksheet_requests import build_worksheets_from_requests
from src.worksheets import ReadingWorksheet


def test_build_math_only():
    resources = ResourceRequests.model_validate(
        {
            "mathWorksheet": {
                "title": "Warm-Up",
                "problems": [
                    {"operand_one": 2, "operand_two": 3, "operator": "+"}
                ]
            }
        }
    )
    plans, errors = build_worksheets_from_requests(resources)
    assert not errors
    assert len(plans) == 1
    assert plans[0].kind == "mathWorksheet"
    assert plans[0].worksheet.title == "Warm-Up"


def test_build_reading_only():
    resources = ResourceRequests.model_validate(
        {
            "readingWorksheet": {
                "passage_title": "Morning Garden",
                "passage": "Lina checked on the beans every morning.",
                "questions": [{"prompt": "What did Lina do?"}],
            }
        }
    )
    plans, errors = build_worksheets_from_requests(resources)
    assert not errors
    assert len(plans) == 1
    assert plans[0].kind == "readingWorksheet"
    assert isinstance(plans[0].worksheet, ReadingWorksheet)
    assert plans[0].worksheet.passage_title == "Morning Garden"


def test_build_both_resources():
    resources = ResourceRequests.model_validate(
        {
            "mathWorksheet": {
                "problems": [
                    {"operand_one": 5, "operand_two": 1, "operator": "-"}
                ]
            },
            "readingWorksheet": {
                "passage_title": "Garden",
                "passage": "Text",
                "questions": [{"prompt": "Question"}],
            }
        }
    )
    plans, errors = build_worksheets_from_requests(resources)
    assert not errors
    assert len(plans) == 2
    kinds = {plan.kind for plan in plans}
    assert kinds == {"mathWorksheet", "readingWorksheet"}


def test_math_generator_failure_is_captured(monkeypatch):
    resources = ResourceRequests.model_validate(
        {
            "mathWorksheet": {
                "problems": [
                    {"operand_one": 5, "operand_two": 1, "operator": "-"}
                ]
            }
        }
    )

    monkeypatch.setattr(
        "src.worksheet_requests.generate_two_operand_math_worksheet",
        lambda **_: (_ for _ in ()).throw(ValueError("boom")),
    )

    plans, errors = build_worksheets_from_requests(resources)
    assert not plans
    assert len(errors) == 1
    assert errors[0].kind == "mathWorksheet"
    assert "boom" in errors[0].message


def test_filename_hint_uses_metadata():
    resources = ResourceRequests.model_validate(
        {
            "mathWorksheet": {
                "metadata": {"artifact_label": "warmup"},
                "problems": [
                    {"operand_one": 2, "operand_two": 3, "operator": "+"}
                ]
            }
        }
    )
    plans, errors = build_worksheets_from_requests(resources)
    assert not errors
    assert plans[0].filename_hint.startswith("warmup")
