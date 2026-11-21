"""scripts/quality_check.py: budget guard, kind catalog coverage, reading-level maths, the
per-kind sheet validator. No network: a fake provider stands in for OpenRouter."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import quality_check as qc  # noqa: E402

from llm.types import Completion, CompletionRequest, Usage  # noqa: E402
from src.weekdoc import HOSTED_KINDS  # noqa: E402


class Fake:
    def __init__(self, cost: float | None, text: str = "{}") -> None:
        self.cost, self.text, self.n = cost, text, 0

    def complete(self, request: CompletionRequest) -> Completion:
        self.n += 1
        return Completion(
            self.text, request.model, Usage(100, 50, 150, self.cost), 0.01, "stop", {}
        )


PRICES = {"m": (1e-6, 1e-6)}


def _req(max_tokens: int = 100) -> CompletionRequest:
    return CompletionRequest(
        model="m", messages=[{"role": "user", "content": "hi"}], max_tokens=max_tokens
    )


def test_every_registered_kind_has_a_purpose_and_a_schema():
    assert set(qc.PURPOSE) == set(HOSTED_KINDS)
    for kind in HOSTED_KINDS:
        assert qc.kind_schema(kind)
    assert qc.kind_menu().count("\n") == len(HOSTED_KINDS) - 1


def test_budget_guard_blocks_before_the_call(tmp_path):
    inner = Fake(cost=0.6)
    p = qc.MeteredProvider(inner, tmp_path / "l.jsonl", cap_usd=1.0, prices=PRICES)
    p.complete(_req())
    assert p.spent() == pytest.approx(0.6)
    # worst case for a huge max_tokens would pass the cap: refuse without calling the provider
    with pytest.raises(qc.BudgetStop):
        p.complete(_req(max_tokens=500_000))
    assert inner.n == 1
    p.complete(_req())  # 0.6 + 0.6 is allowed by the guard (worst case is tiny)
    with pytest.raises(qc.BudgetStop):
        qc.MeteredProvider(inner, tmp_path / "l.jsonl", 1.0, {}).complete(_req())  # unknown price


def test_unreported_cost_is_estimated_from_prices(tmp_path):
    p = qc.MeteredProvider(Fake(cost=None), tmp_path / "l.jsonl", 1.0, PRICES)
    p.complete(_req())
    row = json.loads((tmp_path / "l.jsonl").read_text())
    assert row["cost_estimated"] is True and row["cost_usd"] == pytest.approx(150e-6)
    assert "text" not in row  # the ledger never stores response text


def test_fk_grade_is_lower_for_simple_text():
    easy = qc.fk_grade(["The sun is hot. The sky is blue. I see a big cloud."])
    hard = qc.fk_grade(
        ["Meteorological phenomena necessitate comprehensive observational documentation."]
    )
    assert easy["fk_grade"] < hard["fk_grade"]


def test_sheet_model_checks_answers_against_item_refs():
    sheet = qc.sheet_model("readingWorksheet")
    data = {
        "title": "T",
        "passage": "Sea.",
        "questions": [{"prompt": "Q?", "response_lines": 1}],
    }
    ok = sheet.model_validate(
        {"data": data, "answers": [{"item_ref": "questions.0", "answer": "a"}]}
    )
    assert ok.answers[0].item_ref == "questions.0"
    with pytest.raises(ValueError):
        sheet.model_validate(
            {"data": data, "answers": [{"item_ref": "questions.9", "answer": "a"}]}
        )


def test_samples_cover_every_kind():
    assert set(qc.sample_data()) == set(HOSTED_KINDS)
