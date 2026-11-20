"""Small valid WeekDoc payloads for tests (no real names, placeholder token only)."""

from __future__ import annotations

import copy


def minimal_week() -> dict:
    return copy.deepcopy(
        {
            "schema_version": 1,
            "title": "Tiny Week",
            "packet_title": "Tiny Week for {{student_name}}",
            "theme": "Tiny",
            "grade_band": "K-1",
            "days": [
                {
                    "day": "Monday",
                    "title": "Start",
                    "standards": ["VA.SCIENCE.K.k.6"],
                    "worksheets": [
                        {
                            "id": "mon-note",
                            "kind": "storyPanel",
                            "data": {"who": "Zara", "text": "Hello {{student_name}}"},
                        }
                    ],
                }
            ],
            "prep_checks": [
                {
                    "id": "c1",
                    "day": "Monday",
                    "standard_id": "VA.SCIENCE.K.k.6",
                    "kind": "oral",
                    "prompt": "Ask what the sun does.",
                    "pass_criteria": "Says it warms the ground.",
                }
            ],
            "teacher_guide": {
                "title": "Tiny Guide",
                "days": [
                    {
                        "day": "Monday",
                        "title": "Start",
                        "blocks": [
                            {"heading": "Answer Key"},
                            {"style": "answer", "paragraphs": ["**Q1:** warms it."]},
                        ],
                    }
                ],
            },
        }
    )
