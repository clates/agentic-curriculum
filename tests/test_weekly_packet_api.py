import importlib
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from .factories import build_weekly_plan


MODULE_NAMES_TO_CLEAR = [
    "packet_store",
    "db_utils",
    "src.packet_store",
    "src.db_utils",
    "src.main",
    "main",
]


def _reload_app(db_path: Path):
    os.environ["CURRICULUM_DB_PATH"] = str(db_path)
    for name in MODULE_NAMES_TO_CLEAR:
        sys.modules.pop(name, None)

    db_utils_module = importlib.import_module("src.db_utils")
    sys.modules["db_utils"] = db_utils_module

    packet_store = importlib.import_module("src.packet_store")
    sys.modules["packet_store"] = packet_store

    main_module = importlib.import_module("src.main")
    importlib.reload(main_module)
    return main_module, packet_store


def test_weekly_packet_list_endpoint_returns_paginated(tmp_path):
    db_path = tmp_path / "api.db"
    main_module, packet_store = _reload_app(db_path)

    student_id = "student-123"
    packet_store.save_weekly_packet(
        build_weekly_plan(plan_id="plan_future", week_of="2025-12-08", student_id=student_id)
    )
    packet_store.save_weekly_packet(
        build_weekly_plan(plan_id="plan_current", week_of="2025-12-01", student_id=student_id)
    )

    client = TestClient(main_module.app)

    resp = client.get(f"/students/{student_id}/weekly-packets", params={"page_size": 1})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["pagination"]["has_more"] is True
    assert payload["items"][0]["packet_id"] == "plan_future"

    resp_page_2 = client.get(
        f"/students/{student_id}/weekly-packets",
        params={"page_size": 1, "page": 2},
    )
    assert resp_page_2.status_code == 200
    payload_page_2 = resp_page_2.json()
    assert payload_page_2["pagination"]["has_more"] is False
    assert payload_page_2["items"][0]["packet_id"] == "plan_current"


def test_weekly_packet_detail_endpoint_includes_cache_headers(tmp_path):
    db_path = tmp_path / "api.db"
    main_module, packet_store = _reload_app(db_path)

    packet_store.save_weekly_packet(
        build_weekly_plan(plan_id="plan_detail", student_id="student-abc")
    )

    client = TestClient(main_module.app)
    resp = client.get("/students/student-abc/weekly-packets/plan_detail")
    assert resp.status_code == 200
    assert resp.headers.get("ETag")
    assert resp.headers.get("Last-Modified")
    body = resp.json()
    assert body["plan_id"] == "plan_detail"

    resp_not_found = client.get("/students/other/weekly-packets/plan_detail")
    assert resp_not_found.status_code == 404