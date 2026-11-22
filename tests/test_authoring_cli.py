"""M3.7: the CLI authors and saves a week end to end (scripted provider, no network)."""

import json

import pytest

from authoring import __main__ as cli
from tests.authoring_fixtures import STANDARDS, good_plan, good_week, text
from tests.llm_provider_fakes import ScriptedProvider
from tests.test_authoring_pipeline import env  # noqa: F401  (fixture: tmp DB with standards)


def test_cli_end_to_end(env, monkeypatch, capsys):  # noqa: F811
    import authoring.pipeline as pipeline
    from llm import LLMClient

    provider = ScriptedProvider(text(good_plan()), text(good_week()))
    monkeypatch.setattr(
        pipeline, "default_client", lambda: LLMClient(provider, env={"LLM_MODEL_AUTHOR": "z-ai/glm-5.3"})
    )
    import sqlite3, os
    con = sqlite3.connect(os.environ["CURRICULUM_DB_PATH"])
    con.execute("INSERT OR IGNORE INTO family (family_id, created_at) VALUES ('fam_local', '2026-01-01')")
    con.commit(); con.close()
    child = env / "child.json"
    child.write_text(json.dumps({"first_name": "Ada", "grade": 2, "reading_level": "grade 2",
                                 "interests": ["space"], "parent_notes": "hands-on"}))
    out = env / "out"
    code = cli.main(["--student-json", str(child), "--topic", "Weather", "--standards",
                     ",".join(STANDARDS), "--out-dir", str(out)])
    text_out = capsys.readouterr().out
    assert code == 0 and "status:        success" in text_out and "saved packet:" in text_out
    assert json.loads((out / "week.json").read_text())["title"] == "Weather Week"
    assert json.loads((out / "run.json").read_text())["status"] == "success"


def test_cli_find_standards(env, capsys):  # noqa: F811
    assert cli.main(["--find-standards", "--grade", "2", "--subject", "science"]) == 0
    assert STANDARDS[0] in capsys.readouterr().out


def test_cli_requires_arguments(env):  # noqa: F811
    with pytest.raises(SystemExit):
        cli.main(["--topic", "x"])
