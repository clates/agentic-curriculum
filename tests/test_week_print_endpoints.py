"""Print endpoints for structured weeks (M2.8)."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tests.factories import build_weekly_plan
from tests.weekdoc_fixtures import minimal_week

ROOT = Path(__file__).resolve().parents[1]
WEATHER = json.loads(
    (ROOT / "tests/fixtures/weekdoc/weather_week.json").read_text(encoding="utf-8")
)


@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(tmp_path / "p.db"))
    monkeypatch.syspath_prepend(str(ROOT / "src"))
    for name in list(sys.modules):
        if name in {
            "main",
            "db_utils",
            "packet_store",
            "week_store",
            "migrations",
        } or name.startswith(("weekdoc", "src.")):
            sys.modules.pop(name, None)
    main = importlib.import_module("main")
    importlib.import_module("packet_store").ensure_schema()
    importlib.import_module("db_utils").create_student(
        "stu_1", {"name": "Zoe Quillfeather", "birthday": "2019-01-01"}, {}
    )
    ws = importlib.import_module("week_store")
    return TestClient(main.app), ws, importlib.import_module("packet_store")


URL = "/students/stu_1/weekly-packets/pk1/print"


def test_structured_week_opens_all_three_documents_with_the_first_name_only(api):
    client, ws, _ = api
    ws.save_week("stu_1", "pk1", WEATHER, grade_level=0, week_of="2026-01-05")
    packet = client.get(URL)
    assert packet.status_code == 200 and "text/html" in packet.headers["content-type"]
    assert "Science for Zoe" in packet.text and "Quillfeather" not in packet.text
    assert "{{student_name}}" not in packet.text
    assert packet.text == client.get(URL + "?doc=packet").text  # packet is the default
    guide = client.get(URL + "?doc=guide")
    assert guide.status_code == 200 and "Teacher / Parent Guide" in guide.text
    prep = client.get(URL + "?doc=prep")
    assert prep.status_code == 200 and prep.text.count('class="pc-card"') == 10
    assert "Quillfeather" not in guide.text + prep.text


def test_rendering_is_stable_between_requests(api):
    client, ws, _ = api
    ws.save_week("stu_1", "pk1", WEATHER, grade_level=0, week_of="2026-01-05")
    assert client.get(URL).text == client.get(URL).text


def test_unknown_doc_is_rejected(api):
    client, ws, _ = api
    ws.save_week("stu_1", "pk1", minimal_week(), grade_level=0, week_of="2026-01-05")
    assert client.get(URL + "?doc=bogus").status_code == 422


def test_missing_and_foreign_packets_are_404(api):
    client, ws, _ = api
    assert client.get(URL).status_code == 404
    ws.save_week("stu_1", "pk1", minimal_week(), grade_level=0, week_of="2026-01-05")
    assert client.get("/students/stu_2/weekly-packets/pk1/print").status_code == 404


def test_legacy_packet_still_404s_without_html_artifacts_and_rejects_guide(api):
    client, _, ps = api
    plan = build_weekly_plan(plan_id="pk1", student_id="stu_1")
    ps.save_weekly_packet(plan)
    assert client.get(URL).status_code == 404  # existing behaviour: no HTML artifacts
    guide = client.get(URL + "?doc=guide")
    assert guide.status_code == 404 and "no structured week" in guide.json()["detail"]


def test_structured_week_also_appears_in_the_existing_list_and_get_endpoints(api):
    client, ws, _ = api
    ws.save_week("stu_1", "pk1", WEATHER, grade_level=0, week_of="2026-01-05")
    listing = client.get("/students/stu_1/weekly-packets").json()
    assert listing["items"][0]["packet_id"] == "pk1"
    assert client.get("/students/stu_1/weekly-packets/pk1").json()["plan_id"] == "pk1"
