"""Tests for GET /version endpoint."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import app

client = TestClient(app)


def _app_globals():
    """The namespace of the module that serves /version (robust to tests re-importing main)."""
    route = next(r for r in app.routes if getattr(r, "path", None) == "/version")
    return route.endpoint.__globals__


def test_version_reads_build_env(monkeypatch):
    sha = "0123456789abcdef0123456789abcdef01234567"
    monkeypatch.setenv("GIT_SHA", sha)
    monkeypatch.setenv("BUILD_TIME", "2026-01-02T03:04:05Z")
    monkeypatch.setenv("RELEASE_TAG", "auto-20260102-030405")
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {
        "sha": sha,
        "short_sha": sha[:7],
        "build_time": "2026-01-02T03:04:05Z",
        "release_tag": "auto-20260102-030405",
    }


def test_version_never_crashes_without_env(monkeypatch):
    for name in ("GIT_SHA", "BUILD_TIME", "RELEASE_TAG"):
        monkeypatch.delenv(name, raising=False)

    def boom(*args, **kwargs):
        raise OSError("no git")

    monkeypatch.setattr("main.subprocess.run", boom)
    _app_globals()["_git_head_sha"].cache_clear()  # cached lookup: start cold
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert body["sha"] == "unknown"
    assert body["build_time"] is None
    assert body["release_tag"] is None


def test_git_lookup_runs_once_and_the_env_is_still_read_each_call(monkeypatch):
    calls = []

    def fake_run(*args, **kwargs):
        calls.append(1)

        class Done:
            returncode, stdout = 0, "a" * 40 + "\n"

        return Done()

    monkeypatch.delenv("GIT_SHA", raising=False)
    monkeypatch.setattr("main.subprocess.run", fake_run)
    _app_globals()["_git_head_sha"].cache_clear()
    assert client.get("/version").json()["sha"] == "a" * 40
    assert client.get("/version").json()["sha"] == "a" * 40
    assert len(calls) == 1
    monkeypatch.setenv("GIT_SHA", "b" * 40)
    assert client.get("/version").json()["sha"] == "b" * 40
    _app_globals()["_git_head_sha"].cache_clear()
