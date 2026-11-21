"""Regression guard for the offline /generate-week path (M11.3).

The offline path is: a script in scripts/ calls render_worksheet_html() +
build_print_packet_html() and writes a packet and a teacher guide; the skill looks up
standards in curriculum.db with plain SQL; AGENTS.md tells authors which kinds exist.
Hosted work (WeekDoc, new renderers) must not break any of that, so this file pins it.

Packets are compared on the <body> only: the committed examples carry an older copy of the
stylesheet, but the rendered pages and the teacher guides must stay byte-identical.
"""

from __future__ import annotations

import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import ingest_standards  # noqa: E402
from worksheet_html_renderer import HTML_SUPPORTED_KINDS  # noqa: E402

# (generator script, its output dir, example dir, packet name, guide name)
EXAMPLES = [
    ("weather_week", "weather_week_series", "weather-week", "weather_week"),
    ("data_week", "data_week_series", "data-week", "data_week"),
    ("matter_week", "matter_week_series", "matter-week", "matter_week"),
    ("sky_week", "sky_week_series", "sky-week", "sky_week"),
    ("money_week", "money_week_series", "money-week", "money_week"),
    ("game_theory_week", "game_theory_week_series", "game-theory-week", "game_theory_week"),
    (
        "test_taking_strategies",
        "test_taking_strategies_series",
        "test-taking-strategies",
        "test_taking_strategies",
    ),
]


def _body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text[text.index("<body") :]


@pytest.mark.parametrize("script_stem,out_dir,example_dir,name", EXAMPLES)
def test_example_script_reproduces_committed_example(script_stem, out_dir, example_dir, name):
    script = next(
        p
        for p in (
            ROOT / "scripts" / f"generate_{script_stem}_series.py",
            ROOT / "scripts" / f"generate_{script_stem}_week_series.py",
        )
        if p.exists()
    )
    out = ROOT / out_dir
    existed = out.exists()
    try:
        result = subprocess.run(
            [sys.executable, str(script)], capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, result.stderr
        example = ROOT / "examples" / example_dir
        assert _body(out / f"{name}.html") == _body(example / f"{name}.html")
        assert (out / f"{name}_teacher_guide.html").read_bytes() == (
            example / f"{name}_teacher_guide.html"
        ).read_bytes()
    finally:
        if not existed:  # generated dirs are gitignored; leave the tree as we found it
            shutil.rmtree(out, ignore_errors=True)


def test_skill_standards_sql_still_runs(tmp_path, monkeypatch):
    skill = (ROOT / ".claude" / "skills" / "generate-week" / "SKILL.md").read_text()
    match = re.search(r"execute\(\s*\\?\"(SELECT standard_id.*?)\\?\"\):", skill, re.S)
    assert match, "SKILL.md no longer contains the standards lookup query"
    sql = match.group(1).replace('\\"', '"')
    assert "FROM standards" in sql

    db = tmp_path / "curriculum.db"
    monkeypatch.setattr(ingest_standards, "DB_FILE", str(db))
    ingest_standards.create_database()
    ingest_standards.ingest_standards_from_json(ingest_standards.STANDARDS_DIR)

    rows = sqlite3.connect(db).execute(sql).fetchall()
    assert rows, "the skill's Science K-1 lookup returned nothing"
    assert all(len(r) == 2 for r in rows)
    assert any(r[0].startswith("VA.SCIENCE.K.") for r in rows)


def test_every_kind_in_agents_md_has_a_renderer():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    kinds = set()
    for line in agents.splitlines():
        if line.startswith("|"):
            kinds.update(
                re.findall(r"`([a-z][A-Za-z]*(?:Worksheet|Panel|Card|Box|List|Math|Pairs))`", line)
            )
    kinds.add("letterWorksheet")
    assert len(kinds) >= 24
    assert kinds <= HTML_SUPPORTED_KINDS, sorted(kinds - HTML_SUPPORTED_KINDS)
