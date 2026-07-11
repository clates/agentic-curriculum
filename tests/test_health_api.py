"""Tests for GET /health endpoint."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import app


client = TestClient(app)


def test_health_returns_200():
    """GET /health returns HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_status_ok():
    """GET /health returns {"status": "ok"}."""
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
