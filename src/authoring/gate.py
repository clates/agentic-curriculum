"""Completeness gate (M3.4): what the schema allows but a printable, teachable week cannot lack.

``completeness_problems`` returns every problem found; ``make_week_check`` wraps it as the
``check`` hook of ``generate_structured`` so each problem list becomes repair feedback. All
checks are deterministic.
"""

from __future__ import annotations

import re
from typing import Any, Callable

from weekdoc import STUDENT_NAME_TOKEN, WeekDoc, item_refs

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
GUIDE_CALLOUTS = ("answer", "misconception", "extension", "discuss")
MIN_PREP_CHECKS = 8
MIN_WORKSHEETS_PER_DAY = 2
# Open-response pages: the child writes or draws something personal, so there is no key to give.
OPEN_RESPONSE_KINDS = {"writingScaffoldWorksheet", "letterWorksheet", "storyMapWorksheet", "taskList"}
MAX_REPORTED = 12

_PLACEHOLDER = re.compile(
    r"\bTBD\b|\blorem\b|\bipsum\b|\[\s*insert|\binsert (?:text|name|question|answer)\b"
    r"|\bplaceholder\b|\bTODO\b|\bX{3,}\b|\bfill in later\b",
    re.I,
)


def _strings(x: Any, path: str = "") -> list[tuple[str, str]]:
    if isinstance(x, str):
        return [(path, x)]
    if isinstance(x, dict):
        return [s for k, v in x.items() for s in _strings(v, f"{path}.{k}" if path else k)]
    if isinstance(x, (list, tuple)):
        return [s for i, v in enumerate(x) for s in _strings(v, f"{path}.{i}")]
    return []


def _int_prefix(answer: str) -> int | None:
    m = re.match(r"\s*(-?\d+)\b", answer)
    return int(m.group(1)) if m else None


def _expected_arithmetic(kind: str, data: dict[str, Any], idx: int) -> int | None:
    """Recompute the answer for an arithmetic problem, or None for kinds we do not recompute."""
    try:
        if kind in ("twoOperandWorksheet", "mathWorksheet"):
            p = data["problems"][idx]
            a, b, op = int(p["operand_one"]), int(p["operand_two"]), p.get("operator", "+")
        elif kind == "speedMath":
            p = data["problems"][idx]
            a, b, op = int(p["a"]), int(p["b"]), p["op"]
        elif kind == "tenFrameWorksheet":
            p = data["problems"][idx]
            a, b, op = int(p["addend_a"]), int(p["addend_b"]), "+"
        else:
            return None
    except (KeyError, IndexError, TypeError, ValueError):
        return None
    return a + b if op == "+" else a - b


def _norm(s: str) -> str:
    return " ".join(s.casefold().split())


def _worksheet_problems(day: str, ws: Any) -> list[str]:
    out: list[str] = []
    where = f"{day} worksheet {ws.id} ({ws.kind})"
    refs = [r.ref for r in item_refs(ws.kind, ws.data)]
    answers = {a.item_ref: a.answer for a in ws.answers}
    if len(answers) != len(ws.answers):
        out.append(f"{where}: duplicate item_ref in answers")
    if refs and ws.kind not in OPEN_RESPONSE_KINDS:
        missing = [r for r in refs if r not in answers]
        if missing:
            out.append(
                f"{where}: answers missing for item_refs {', '.join(missing[:6])}"
                f"{' ...' if len(missing) > 6 else ''} (every item_ref needs an answer)"
            )
    for ref, ans in answers.items():
        m = re.fullmatch(r"problems\.(\d+)", ref)
        if m:
            expected = _expected_arithmetic(ws.kind, ws.data, int(m.group(1)))
            if expected is not None and _int_prefix(ans) != expected:
                out.append(f"{where}: {ref} answer {ans!r} is wrong; the correct answer is {expected}")
    if ws.kind == "matchingWorksheet" and ws.answers:
        left = ws.data.get("left_items", [])
        right = [r if isinstance(r, str) else r.get("text", "") for r in ws.data.get("right_items", [])]
        rights = {_norm(r): i for i, r in enumerate(right)}
        picked: list[int] = []
        for ref, ans in answers.items():
            hit = rights.get(_norm(ans))
            if hit is None:
                out.append(f"{where}: answer for {ref} ({ans!r}) is not one of right_items")
            else:
                picked.append(hit)
        if len(set(picked)) != len(picked):
            out.append(f"{where}: two left items share one right item; each right item is used once")
        if len(left) >= 3 and len(picked) == len(left) and picked == list(range(len(left))):
            out.append(
                f"{where}: right_items are in the same order as left_items, so each printed row "
                "shows its own answer; reorder right_items and answer with the matching item"
            )
    if ws.kind == "wordSortWorksheet" and ws.answers:
        labels = [c if isinstance(c, str) else c.get("label", "") for c in ws.data.get("categories", [])]
        for ref, ans in answers.items():
            if not any(_norm(lab) in _norm(ans) for lab in labels if lab):
                out.append(f"{where}: answer for {ref} ({ans!r}) names none of the categories {labels}")
    return out


def completeness_problems(
    week: WeekDoc,
    *,
    student_first_name: str | None = None,
    allowed_standards: set[str] | None = None,
) -> list[str]:
    problems: list[str] = []
    if [d.day for d in week.days] != DAYS:
        problems.append("days must be exactly Monday, Tuesday, Wednesday, Thursday, Friday in order")
    for d in week.days:
        if len(d.worksheets) < MIN_WORKSHEETS_PER_DAY:
            problems.append(f"{d.day} has {len(d.worksheets)} worksheet(s); need at least 2")
        if not d.standards:
            problems.append(f"{d.day} lists no standards")
        problems += [p for ws in d.worksheets for p in _worksheet_problems(d.day, ws)]
    if len(week.prep_checks) < MIN_PREP_CHECKS:
        problems.append(f"only {len(week.prep_checks)} prep checks; need at least {MIN_PREP_CHECKS} (about 10)")
    checked_days = {c.day for c in week.prep_checks}
    for day in DAYS:
        if day not in checked_days:
            problems.append(f"no prep check on {day}")
    if [g.day for g in week.teacher_guide.days] != DAYS:
        problems.append("teacher_guide must have exactly one entry for each of Monday..Friday in order")
    for g in week.teacher_guide.days:
        styles = {b.style for b in g.blocks if b.style}
        for need in GUIDE_CALLOUTS:
            if need not in styles:
                problems.append(f"teacher_guide {g.day} lacks a '{need}' callout block")
    if allowed_standards is not None:
        for d in week.days:
            bad = [s for s in d.standards if s not in allowed_standards]
            if bad:
                problems.append(f"{d.day} uses standards not in the STANDARDS list: {', '.join(bad)}")
        for c in week.prep_checks:
            if c.standard_id not in allowed_standards:
                problems.append(
                    f"prep check {c.id} standard_id {c.standard_id} is not in the STANDARDS list"
                )
    dumped = week.model_dump(mode="json", by_alias=True)
    name_re = (
        re.compile(rf"(?<!\w){re.escape(student_first_name)}(?!\w)", re.I)
        if student_first_name
        else None
    )
    name_hits = placeholder_hits = 0
    for path, text in _strings(dumped):
        if name_re and name_re.search(text):
            name_hits += 1
            if name_hits <= 2:
                problems.append(
                    f"the child's name appears literally at {path}; write {STUDENT_NAME_TOKEN} instead"
                )
        if _PLACEHOLDER.search(text) or text.strip() in ("...", "…"):
            placeholder_hits += 1
            if placeholder_hits <= 2:
                problems.append(f"placeholder text at {path}: {text[:60]!r}")
    return problems


def make_week_check(
    *, student_first_name: str | None, allowed_standards: set[str] | None
) -> Callable[[WeekDoc], str | None]:
    """The ``check`` hook for generate_structured."""

    def check(week: WeekDoc) -> str | None:
        problems = completeness_problems(
            week, student_first_name=student_first_name, allowed_standards=allowed_standards
        )
        if not problems:
            return None
        extra = f" (+{len(problems) - MAX_REPORTED} more)" if len(problems) > MAX_REPORTED else ""
        return "; ".join(problems[:MAX_REPORTED]) + extra

    return check
