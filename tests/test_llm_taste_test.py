"""M1.7: model taste-test harness."""

import json

from pydantic import BaseModel

from llm import Completion, LLMClient, LLMServerError, Usage
from llm.taste_test import main, run_taste_test, slug, write_outputs

PROMPT = "Write a one-line lesson about <fractions> & more"


class Scripted:
    """Provider answering per model: (text, cost) or an exception."""

    def __init__(self, by_model):
        self.by_model = by_model
        self.calls = []

    def complete(self, request):
        self.calls.append(request.model)
        item = self.by_model[request.model]
        if isinstance(item, BaseException):
            raise item
        text, cost = item
        return Completion(text, request.model, Usage(11, 7, 18, cost), 0.25)


def client(by_model):
    provider = Scripted(by_model)
    return provider, LLMClient(provider, env={}, sleep=lambda s: None)


def test_runs_each_model_and_records_tokens_cost_latency():
    provider, c = client({"a/one": ("A out", 0.01), "b/two": ("B out", 0.02)})
    run = run_taste_test(c, PROMPT, ["a/one", "b/two"], max_usd=1.0)
    assert provider.calls == ["a/one", "b/two"]
    first = run.results[0]
    assert (first.status, first.output, first.prompt_tokens, first.cost_usd) == (
        "ok",
        "A out",
        11,
        0.01,
    )
    assert first.latency_s == 0.25
    assert run.total_cost_usd == 0.03


def test_budget_is_enforced_before_the_next_call():
    provider, c = client({"a/one": ("x", 0.6), "b/two": ("y", 0.6), "c/three": ("z", 0.6)})
    run = run_taste_test(c, PROMPT, ["a/one", "b/two", "c/three"], max_usd=1.0)
    # 0.6 then 1.2 (one call may overshoot); the third is never sent.
    assert provider.calls == ["a/one", "b/two"]
    assert [r.status for r in run.results] == ["ok", "ok", "skipped"]
    assert "budget" in run.results[2].error


def test_unknown_cost_stops_the_run_unless_allowed():
    provider, c = client({"a/one": ("x", None), "b/two": ("y", None)})
    run = run_taste_test(c, PROMPT, ["a/one", "b/two"], max_usd=1.0)
    assert provider.calls == ["a/one"] and run.results[1].status == "skipped"
    provider, c = client({"a/one": ("x", None), "b/two": ("y", None)})
    run_taste_test(c, PROMPT, ["a/one", "b/two"], max_usd=1.0, allow_unknown_cost=True)
    assert provider.calls == ["a/one", "b/two"]


def test_a_failing_model_does_not_stop_the_others_and_never_falls_back():
    provider, c = client({"a/one": LLMServerError("boom"), "b/two": ("ok", 0.0)})
    run = run_taste_test(c, PROMPT, ["a/one", "b/two"], max_usd=1.0)
    assert run.results[0].status == "error" and "LLMServerError" in run.results[0].error
    assert run.results[1].status == "ok"
    assert set(provider.calls) == {"a/one", "b/two"}  # fallback model was not substituted


def test_schema_mode_reports_validity_and_repairs():
    class Out(BaseModel):
        title: str

    provider, c = client({"a/one": ('{"title": "T"}', 0.01), "b/two": ("not json", 0.01)})
    # repair calls use the "repair" task but stay pinned to the model under test
    provider.by_model["b/two"] = ("not json", 0.01)
    run = run_taste_test(c, PROMPT, ["a/one", "b/two"], max_usd=5.0, schema=Out)
    good, bad = run.results
    assert good.schema_valid is True and good.repairs == 0
    assert bad.schema_valid is False and bad.repairs == 2 and "StructuredOutputError" in bad.error
    assert set(provider.calls) == {"a/one", "b/two"}


def test_files_and_html_are_written_and_escaped(tmp_path):
    _, c = client({"google/gemini-x": ("<script>alert(1)</script>", 0.01)})
    run = run_taste_test(c, PROMPT, ["google/gemini-x"], max_usd=1.0)
    page = write_outputs(run, tmp_path)
    text = page.read_text()
    assert "google/gemini-x" in text and "<script>alert" not in text and "&lt;script&gt;" in text
    assert "&lt;fractions&gt;" in text  # prompt escaped too
    data = json.loads((tmp_path / "results.json").read_text())
    assert data["schema_version"] == 1 and data["results"][0]["cost_usd"] == 0.01
    assert (tmp_path / f"{slug('google/gemini-x')}.json").exists()


def test_cli_end_to_end(tmp_path, capsys):
    _, c = client({"a/one": ("A", 0.01), "b/two": ("B", 0.01)})
    code = main(
        [
            "--prompt",
            PROMPT,
            "--model",
            "a/one",
            "--model",
            "b/two",
            "--max-usd",
            "1",
            "--out",
            str(tmp_path),
        ],
        client=c,
    )
    out = capsys.readouterr().out
    assert code == 0 and "a/one" in out and "total $0.02000" in out
    assert (tmp_path / "comparison.html").exists()


def test_default_models_include_gemini_and_a_haiku():
    from llm.config import DEFAULT_FILE, _load

    models = _load(DEFAULT_FILE)["taste_test_models"]
    assert len(models) >= 3
    assert any(m.startswith("google/gemini") for m in models)
    assert any("haiku" in m for m in models)
