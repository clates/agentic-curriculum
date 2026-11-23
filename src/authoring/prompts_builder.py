"""Prompt assembly from the versioned files in ``prompts/`` (M3.1).

Every run records ``prompt_version`` (the VERSION file) and ``prompt_hash`` (a hash of every
asset that went into the prompts, so an edit without a version bump is still visible in the run
record). Student data enters ONLY through ``ModelStudentContext.prompt_json()``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from . import catalog
from .catalog import PROMPTS_DIR
from .context import ModelStudentContext
from .standards import Standard

ASSET_FILES = (
    "system.md",
    "rules.md",
    "plan_task.md",
    "week_task.md",
    "reference_intro.md",
    "reference_example.json",
    "kind_purposes.json",
    "kind_ref_patterns.json",
)


def _read(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8").strip()


def prompt_version() -> str:
    return _read("VERSION")


def prompt_hash() -> str:
    digest = hashlib.sha256()
    for name in ASSET_FILES:
        digest.update(name.encode())
        digest.update((PROMPTS_DIR / name).read_bytes())
    return digest.hexdigest()[:16]


def student_block(student: ModelStudentContext, topic: str, standards: list[Standard]) -> str:
    lines = "\n".join(f"- {s.standard_id}: {s.description}" for s in standards)
    return (
        "STUDENT (the only personal data you get):\n"
        + json.dumps(student.prompt_json(), ensure_ascii=False)
        + f"\n\nTOPIC: {topic.strip()}\n\nSTANDARDS (use ONLY these ids, character for character):\n"
        + lines
    )


def reference_block() -> str:
    ref = json.loads(_read("reference_example.json"))
    lines = [
        f"  {d['day']}: {d['title']}  [{', '.join(f'{i}={k}' for i, k in d['kinds'])}]"
        f"  standards={d['standards']}"
        for d in ref["days"]
    ]
    return (
        _read("reference_intro.md")
        + "\n"
        + "\n".join(lines)
        + "\nEach day: one readingWorksheet (the daily lesson) plus one or two activity pages; "
        "Friday is a capstone. A Parent Prep Sheet of about 10 quick checks; a teacher guide "
        "with answer keys.\n\nExample readingWorksheet (K-1 level, for shape and quality only):\n"
        + json.dumps(ref["reading_worksheet"], ensure_ascii=False)
        + "\n\nExample prep check:\n"
        + json.dumps(ref["prep_check"])
        + "\n\nExample teacher_guide day (first blocks):\n"
        + json.dumps(ref["teacher_guide_day"], ensure_ascii=False)
        + "\nTeacher guide summary shape:\n"
        + json.dumps(ref["teacher_guide_summary"], ensure_ascii=False)
    )


@dataclass(frozen=True)
class Prompts:
    system: str
    common: str  # identical for both steps: student, standards, reference, rules
    version: str
    hash: str

    def plan_messages(self) -> list[dict[str, str]]:
        user = (
            f"{self.common}\n\nKIND MENU (the only kinds that exist; one line each):\n"
            f"{catalog.kind_menu()}\n\n{_read('plan_task.md')}"
        )
        return [{"role": "system", "content": self.system}, {"role": "user", "content": user}]

    def week_messages(
        self, plan_json: str, kinds: list[str], student: ModelStudentContext
    ) -> list[dict[str, str]]:
        task = _read("week_task.md").replace("<<grade_label>>", student.grade_label)
        user = (
            f"{self.common}\n\nYOUR PLAN FROM STEP 1 (follow it):\n{plan_json}\n\n"
            f"SCHEMAS for the kinds in your plan:\n{catalog.kind_blocks(kinds)}\n\n{task}"
        )
        return [{"role": "system", "content": self.system}, {"role": "user", "content": user}]


def build_prompts(student: ModelStudentContext, topic: str, standards: list[Standard]) -> Prompts:
    common = "\n\n".join(
        [student_block(student, topic, standards), reference_block(), _read("rules.md")]
    )
    return Prompts(
        system=_read("system.md"), common=common, version=prompt_version(), hash=prompt_hash()
    )
