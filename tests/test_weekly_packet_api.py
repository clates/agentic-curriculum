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


def _materialize_artifacts(root: Path, weekly_plan: dict) -> None:
    for day in weekly_plan.get("daily_plan", []):
        resources = day.get("resources") or {}
        for payload in resources.values():
            for artifact in payload.get("artifacts", []):
                rel_path = artifact.get("path")
                if not rel_path:
                    continue
                path = root / rel_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(rel_path.encode("utf-8"))


def _setup_packet_with_artifacts(tmp_path: Path, student_id: str = "student-artifacts"):
    db_path = tmp_path / "api.db"
    main_module, packet_store = _reload_app(db_path)
    main_module.PROJECT_ROOT = tmp_path
    packet_store.PROJECT_ROOT = tmp_path

    plan = build_weekly_plan(plan_id="plan_artifacts", student_id=student_id)
    packet_store.save_weekly_packet(plan)
    _materialize_artifacts(tmp_path, plan)
    client = TestClient(main_module.app)
    return client, plan, main_module, packet_store


def test_weekly_packet_list_endpoint_returns_paginated(tmp_path):
    db_path = tmp_path / "api.db"
    main_module, packet_store = _reload_app(db_path)

    student_id = "student-123"
    packet_store.save_weekly_packet(
        build_weekly_plan(plan_id="plan_future",
                          week_of="2025-12-08", student_id=student_id)
    )
    packet_store.save_weekly_packet(
        build_weekly_plan(plan_id="plan_current",
                          week_of="2025-12-01", student_id=student_id)
    )

    client = TestClient(main_module.app)

    resp = client.get(
        f"/students/{student_id}/weekly-packets", params={"page_size": 1})
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


def test_weekly_packet_manifest_endpoint_groups_artifacts(tmp_path):
    client, plan, _, _ = _setup_packet_with_artifacts(tmp_path)

    resp = client.get(
        f"/students/{plan['student_id']}/weekly-packets/{plan['plan_id']}/worksheets"
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["packet_id"] == plan["plan_id"]
    assert payload["artifact_count"] == 3
    assert len(payload["items"]) == 2  # Monday and Tuesday

    monday_group = next(
        item for item in payload["items"] if item["day_label"] == "Monday")
    assert monday_group["resource_kind"] == "mathWorksheet"
    assert len(monday_group["artifacts"]) == 2
    assert monday_group["artifacts"][0]["download_url"].startswith(
        "/students/")


def test_download_endpoint_streams_files_and_handles_missing(tmp_path):
    client, plan, _, _ = _setup_packet_with_artifacts(tmp_path)

    manifest_resp = client.get(
        f"/students/{plan['student_id']}/weekly-packets/{plan['plan_id']}/worksheets"
    )
    artifact_entry = manifest_resp.json()["items"][0]["artifacts"][0]

    download_resp = client.get(artifact_entry["download_url"])
    assert download_resp.status_code == 200
    assert download_resp.headers.get(
        "Content-Type") in {"application/pdf", "image/png"}
    assert download_resp.headers.get("ETag")
    assert download_resp.headers.get("Last-Modified")
    assert download_resp.headers.get(
        "Content-Disposition", "").startswith("attachment;")
    assert download_resp.content

    missing_path = Path(
        tmp_path) / plan["daily_plan"][0]["resources"]["mathWorksheet"]["artifacts"][0]["path"]
    missing_path.unlink()
    missing_resp = client.get(artifact_entry["download_url"])
    assert missing_resp.status_code == 410

    unauthorized_resp = client.get(
        f"/students/unauthorized/worksheet-artifacts/{artifact_entry['artifact_id']}"
    )
    assert unauthorized_resp.status_code == 404


def test_download_endpoint_rejects_paths_outside_project_root(tmp_path):
    db_path = tmp_path / "api.db"
    main_module, packet_store = _reload_app(db_path)
    main_module.PROJECT_ROOT = tmp_path
    packet_store.PROJECT_ROOT = tmp_path

    plan = build_weekly_plan(plan_id="plan_escape",
                             student_id="student-escape")
    outside_dir = tmp_path.parent / "outside"
    outside_dir.mkdir(parents=True, exist_ok=True)
    outside_file = outside_dir / "escape.pdf"
    plan["daily_plan"][0]["resources"]["mathWorksheet"]["artifacts"][0]["path"] = str(
        outside_file
    )

    packet_store.save_weekly_packet(plan)
    outside_file.write_bytes(b"escape-artifact")

    client = TestClient(main_module.app)
    manifest = client.get(
        f"/students/{plan['student_id']}/weekly-packets/{plan['plan_id']}/worksheets"
    ).json()

    escape_entry = next(
        artifact
        for item in manifest["items"]
        for artifact in item["artifacts"]
        if artifact["file_size_bytes"] == 1024
    )

    download_resp = client.get(escape_entry["download_url"])
    assert download_resp.status_code == 404
