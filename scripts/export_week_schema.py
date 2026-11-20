"""Regenerate src/weekdoc/week.v1.schema.json from the WeekDoc models.

    venv/bin/python scripts/export_week_schema.py
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(ROOT))

from src.weekdoc.models import week_json_schema  # noqa: E402

SCHEMA_PATH = ROOT / "src" / "weekdoc" / "week.v1.schema.json"


def render_schema_text() -> str:
    return json.dumps(week_json_schema(), indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    SCHEMA_PATH.write_text(render_schema_text(), encoding="utf-8")
    print(f"wrote {SCHEMA_PATH}")
