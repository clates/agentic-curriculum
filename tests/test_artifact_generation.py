import src.agent as agent
from src.worksheet_requests import WorksheetArtifactPlan
from src.worksheets import generate_two_operand_math_worksheet


def _make_math_plan():
    worksheet = generate_two_operand_math_worksheet(
        problems=[{"operand_one": 2, "operand_two": 3, "operator": "+"}],
        title="Warm-Up",
    )
    return WorksheetArtifactPlan(
        kind="mathWorksheet",
        worksheet=worksheet,
        filename_hint="warmup",
        metadata={},
    )


def test_render_artifacts_creates_png_and_pdf(tmp_path, monkeypatch):
    plan = _make_math_plan()
    monkeypatch.setattr(agent, "ARTIFACTS_DIR", tmp_path / "artifacts")
    monkeypatch.setattr(agent, "PROJECT_ROOT", tmp_path)

    artifact_map, errors = agent._render_worksheet_artifacts(
        "plan_demo", "Monday", [plan], generation_logger=None
    )

    assert errors == []
    assert "mathWorksheet" in artifact_map
    artifact_paths = {entry["type"]: entry["path"] for entry in artifact_map["mathWorksheet"]}
    assert "png" in artifact_paths and "pdf" in artifact_paths
    for rel_path in artifact_paths.values():
        expected = tmp_path / rel_path
        assert expected.exists()


def test_render_artifacts_records_errors(tmp_path, monkeypatch):
    plan = _make_math_plan()
    monkeypatch.setattr(agent, "ARTIFACTS_DIR", tmp_path / "artifacts")
    monkeypatch.setattr(agent, "PROJECT_ROOT", tmp_path)

    def fail_png(_worksheet, _path):
        raise ValueError("png boom")

    monkeypatch.setattr(agent, "render_worksheet_to_image", fail_png)

    artifact_map, errors = agent._render_worksheet_artifacts(
        "plan_demo", "Tuesday", [plan], generation_logger=None
    )

    # PDF should still render even if PNG fails.
    assert "mathWorksheet" in artifact_map
    pdf_entries = [entry for entry in artifact_map["mathWorksheet"] if entry["type"] == "pdf"]
    assert pdf_entries
    assert errors and any(err["kind"] == "mathWorksheet" for err in errors)
    for entry in pdf_entries:
        assert (tmp_path / entry["path"]).exists()
