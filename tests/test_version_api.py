"""Tests for GET /version endpoint."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import app

client = TestClient(app)


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
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert body["sha"] == "unknown"
    assert body["build_time"] is None
    assert body["release_tag"] is None
