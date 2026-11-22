"""A complete, gate-passing week and its plan, as JSON text for scripted-provider tests."""

from __future__ import annotations

import copy
import json

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
STANDARDS = ["VA.SCIENCE.2.2.6.a", "VA.SCIENCE.2.2.6.b"]


def good_plan() -> dict:
    return {
        "narrator": "Nova the Night Owl",
        "arc": "Sun, clouds, rain, wind, forecast",
        "days": [
            {
                "day": d,
                "title": f"{d} lesson",
                "standards": [STANDARDS[i % 2]],
                "worksheets": [
                    {"id": f"{d[:3].lower()}-1", "kind": "readingWorksheet", "focus": "read a passage"},
                    {"id": f"{d[:3].lower()}-2", "kind": "twoOperandWorksheet", "focus": "count rain"},
                ],
            }
            for i, d in enumerate(DAYS)
        ],
    }


def good_week() -> dict:
    days, checks, guide = [], [], []
    for i, d in enumerate(DAYS):
        p = d[:3].lower()
        sheets = [
            {
                "id": f"{p}-1",
                "kind": "readingWorksheet",
                "data": {
                    "title": f"{d} reading",
                    "passage": "Nova looks at the sky.\n\nIt is sunny.",
                    "vocabulary": [{"term": "sun", "definition": "a star"}],
                    "questions": [{"prompt": "Who looks?"}, {"prompt": "LET'S DISCUSS: why?", "response_lines": 0}],
                },
                "answers": [
                    {"item_ref": "questions.0", "answer": "Nova"},
                    {"item_ref": "questions.1", "answer": "Answers vary."},
                ],
            },
            {
                "id": f"{p}-2",
                "kind": "twoOperandWorksheet",
                "data": {
                    "title": f"{d} math",
                    "problems": [
                        {"operand_one": 4, "operand_two": 3, "operator": "+"},
                        {"operand_one": 9, "operand_two": 6, "operator": "-"},
                    ],
                },
                "answers": [
                    {"item_ref": "problems.0", "answer": "7"},
                    {"item_ref": "problems.1", "answer": "3"},
                ],
            },
        ]
        if d == "Wednesday":
            sheets.append(
                {
                    "id": "wed-3",
                    "kind": "matchingWorksheet",
                    "data": {
                        "title": "Match",
                        "left_items": ["Wind", "Rain", "Sun"],
                        "right_items": ["Falling water", "Warm light", "Moving air"],
                    },
                    "answers": [
                        {"item_ref": "left_items.0", "answer": "Moving air"},
                        {"item_ref": "left_items.1", "answer": "Falling water"},
                        {"item_ref": "left_items.2", "answer": "Warm light"},
                    ],
                }
            )
        days.append(
            {"day": d, "title": f"{d} lesson", "standards": [STANDARDS[i % 2]], "worksheets": sheets}
        )
        for n in (1, 2):
            checks.append(
                {
                    "id": f"chk-{len(checks) + 1}",
                    "day": d,
                    "standard_id": STANDARDS[i % 2],
                    "kind": "oral",
                    "prompt": "Ask what the sky looks like.",
                    "pass_criteria": "Names one thing about the sky.",
                }
            )
        guide.append(
            {
                "day": d,
                "title": f"{d} lesson",
                "blocks": [
                    {"heading": "Answers"},
                    {"style": "answer", "paragraphs": ["Q1 Nova."]},
                    {"style": "misconception", "paragraphs": ["Clouds are not smoke."]},
                    {"style": "extension", "paragraphs": ["Draw the sky."]},
                    {"style": "discuss", "paragraphs": ["Why is the sky blue?"]},
                ],
            }
        )
    return {
        "schema_version": 1,
        "title": "Weather Week",
        "packet_title": "Weather Week for {{student_name}}",
        "theme": "Weather",
        "subject": "Science",
        "grade_band": "2",
        "narrator": "Nova the Night Owl",
        "arc": "Sun to forecast",
        "days": days,
        "prep_checks": checks,
        "teacher_guide": {"title": "Weather Guide", "days": guide},
    }


def mutate(fn) -> dict:
    week = copy.deepcopy(good_week())
    fn(week)
    return week


def text(obj: dict) -> str:
    return json.dumps(obj)
