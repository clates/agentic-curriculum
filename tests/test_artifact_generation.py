import src.agent as agent
from src.worksheet_requests import WorksheetArtifactPlan


def _make_math_plan():
    """Return a twoOperandWorksheet plan with html_data for HTML rendering."""
    return WorksheetArtifactPlan(
        kind="twoOperandWorksheet",
        html_data={
            "title": "Warm-Up",
            "problems": [{"operand_one": 2, "operand_two": 3, "operator": "+"}],
        },
        filename_hint="warmup",
        metadata={},
    )


def test_render_artifacts_creates_html_artifact(tmp_path, monkeypatch):
    plan = _make_math_plan()
    monkeypatch.setattr(agent, "ARTIFACTS_DIR", tmp_path / "artifacts")
    monkeypatch.setattr(agent, "PROJECT_ROOT", tmp_path)

    artifact_map, errors = agent._render_worksheet_artifacts(
        "plan_demo", "Monday", [plan], generation_logger=None
    )

    assert errors == []
    assert "twoOperandWorksheet" in artifact_map
    artifact_paths = {entry["type"]: entry["path"] for entry in artifact_map["twoOperandWorksheet"]}
    assert "html" in artifact_paths
    for rel_path in artifact_paths.values():
        expected = tmp_path / rel_path
        assert expected.exists()


def test_render_artifacts_records_errors(tmp_path, monkeypatch):
    plan = _make_math_plan()
    monkeypatch.setattr(agent, "ARTIFACTS_DIR", tmp_path / "artifacts")
    monkeypatch.setattr(agent, "PROJECT_ROOT", tmp_path)

    # Replace render_worksheet_html with a failing function
    def fail_html(kind, data, day_label=""):
        raise ValueError("html boom")

    monkeypatch.setattr(agent, "render_worksheet_html", fail_html)

    artifact_map, errors = agent._render_worksheet_artifacts(
        "plan_demo", "Tuesday", [plan], generation_logger=None
    )

    # Should record the error
    assert errors
    assert any(err["kind"] == "twoOperandWorksheet" for err in errors)