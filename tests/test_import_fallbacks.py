"""Regression tests ensuring src modules work when executed as scripts."""

from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"


def test_agent_module_executes_as_script():
    """Running agent.py directly should succeed without import errors."""
    module_globals = runpy.run_path(str(SRC_DIR / "agent.py"))
    assert "generate_weekly_plan" in module_globals


def test_worksheet_requests_executes_as_script():
    """Running worksheet_requests.py directly should succeed without import errors."""
    module_globals = runpy.run_path(str(SRC_DIR / "worksheet_requests.py"))
    assert "build_worksheets_from_requests" in module_globals
