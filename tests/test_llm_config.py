"""M1.2: per-task model config; swapping a model is a config edit, not a code change."""

import json

import pytest

from llm import CompletionRequest, Completion, LLMClient, LLMConfigError, Usage, task_config
from llm.config import known_tasks


def test_checked_in_config_covers_the_core_tasks():
    assert {"outline", "author", "judge", "repair", "scaffold", "lesson"} <= set(known_tasks())
    for task in known_tasks():
        cfg = task_config(task, env={})
        assert "/" in cfg.model and cfg.max_tokens and cfg.timeout_s


def test_tasks_can_use_different_models():
    assert task_config("judge", env={}).model != task_config("author", env={}).model


def test_env_override_precedence():
    base = task_config("outline", env={}).model
    assert task_config("outline", env={"OPENAI_MODEL": "legacy/m"}).model == "legacy/m"
    env = {"OPENAI_MODEL": "legacy/m", "LLM_MODEL": "all/m"}
    assert task_config("outline", env=env).model == "all/m"
    env["LLM_MODEL_OUTLINE"] = "one/m"
    assert task_config("outline", env=env).model == "one/m"
    assert task_config("author", env=env).model == "all/m"
    assert base not in ("legacy/m", "all/m", "one/m")


def test_numeric_overrides_and_bad_values():
    cfg = task_config("author", env={"LLM_MAX_TOKENS_AUTHOR": "123", "LLM_TIMEOUT_S_AUTHOR": "9.5"})
    assert (cfg.max_tokens, cfg.timeout_s) == (123, 9.5)
    with pytest.raises(LLMConfigError):
        task_config("author", env={"LLM_MAX_TOKENS_AUTHOR": "lots"})


def test_unknown_task_is_an_error():
    with pytest.raises(LLMConfigError, match="unknown LLM task"):
        task_config("nonexistent", env={})


def test_swapping_a_model_is_only_a_config_edit(tmp_path):
    """Edit the JSON file only: the same code path now calls a different model."""
    config = {"defaults": {"model": "a/one"}, "tasks": {"judge": {}}}
    path = tmp_path / "models.json"
    path.write_text(json.dumps(config))
    env = {"LLM_MODELS_FILE": str(path)}

    seen = []

    class Recorder:
        def complete(self, request: CompletionRequest) -> Completion:
            seen.append(request.model)
            return Completion(text="{}", model=request.model, usage=Usage(), latency_s=0.0)

    client = LLMClient(Recorder(), env=env)
    client.complete("judge", [{"role": "user", "content": "x"}])
    config["tasks"]["judge"]["model"] = "b/two"
    path.write_text(json.dumps(config))
    client.complete("judge", [{"role": "user", "content": "x"}])
    assert seen == ["a/one", "b/two"]


def test_request_carries_task_limits():
    seen = []

    class Recorder:
        def complete(self, request):
            seen.append(request)
            return Completion(text="", model=request.model, usage=Usage(), latency_s=0.0)

    LLMClient(Recorder(), env={}).complete("author", [])
    assert seen[0].max_tokens == task_config("author", env={}).max_tokens
    assert seen[0].timeout_s == task_config("author", env={}).timeout_s
