"""Utilities for generating error-audit ("Bug Hunt") worksheet data structures.

Generic template behind the repair cohort: each specimen shows something wrong
(a worked solution, a picture, a sentence). The student marks the bug,
diagnoses it against a legend, fixes it, and verifies. Theming (doctor,
detective, mechanic, ...) is just labels — the stages are the same.

Stage flags:
  fix_mode "rewrite" — ruled lines for a corrected rework (Division Detective)
  fix_mode "redraw"  — empty box for a corrected drawing (Clock Doctor)
  fix_mode "none"    — verdict/diagnose only (Find the Lie, Taxonomy Tag)
  verify=True        — adds a "re-check" checkbox line per specimen
  adversarial=True   — student PLANTS an assigned bug (Error Chef inverse)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


FIX_MODES = ("rewrite", "redraw", "none")


@dataclass(frozen=True)
class ErrorAuditSpecimen:
    """One buggy specimen: what the student sees, plus the answer key."""

    prompt: str  # e.g. "Rory says this clock shows 3:30" or the worked steps
    lines: List[str]  # specimen body lines (work, labels, caption)
    bug_location: str | None = None  # answer key: where the bug is
    diagnosis: str | None = None  # answer key: legend entry that applies
    fix_text: str | None = None  # answer key: corrected version (rewrite mode)
    art: dict | None = None  # optional picture: {"kind": "clock"|"dots"|"partitions", ...}
    #   clock: {"hour": 3.0, "minute": 30, "missing": "minute"|"hour"|None}
    #     hour is a clock position (3.5 = halfway past 3); minute is 0-59.
    #   dots: {"rows": 3, "cols": 4} — filled-circle array grid.
    #   partitions: {"parts": N, "broken": i, "shaded": i|[i,...]}
    #     circle cut into N wedges; wedge i is mis-sized (unequal) — the bug
    #     to circle. "shaded" (optional) fills wedge(s) for shaded-fraction
    #     claims. broken/shaded may be None for count/shading bugs.
    starter_art: dict | None = None  # optional redraw-scaffold override:
    #   the CORRECT target shape (e.g. equal thirds when the bug is a
    #   four-piece "thirds"). Defaults to art rendered without the bug.
    fix_scaffold: dict | None = None  # optional guided rewrite grid:
    #   {"kind": "decimal_stack", "addends": ["0.5", "0.25"],
    #    "answer": "0.75"} — replaces ruled lines with decimal-aligned
    #   digit slots. Decimal points are pre-printed in their column;
    #   short terms are padded with faint helper zeroes to trace.
    blank_fix_circle: bool = False  # redraw mode, partitions art only:
    #   the fix area is a single blank circle outline — the student draws
    #   the partition lines themselves instead of tracing a starter shape.

    @classmethod
    def from_mapping(cls, payload: dict) -> "ErrorAuditSpecimen":
        lines = payload.get("lines", [])
        if isinstance(lines, str):
            lines = [lines]
        return cls(
            prompt=payload.get("prompt", ""),
            lines=list(lines),
            bug_location=payload.get("bug_location"),
            diagnosis=payload.get("diagnosis"),
            fix_text=payload.get("fix_text"),
            art=payload.get("art"),
            starter_art=payload.get("starter_art"),
            fix_scaffold=payload.get("fix_scaffold"),
            blank_fix_circle=bool(payload.get("blank_fix_circle", False)),
        )


def _validate_clock_art(art: dict) -> None:
    """Validate a clock art dict; raise ValueError on bad specs."""
    try:
        hour = float(art.get("hour", 12))
    except (TypeError, ValueError):
        raise ValueError(f"clock art needs numeric hour, got {art.get('hour')!r}")
    if not 0 <= hour <= 12:
        raise ValueError(f"clock art hour must be 0-12, got {hour!r}")
    minute = art.get("minute", 0)
    if isinstance(minute, bool) or not isinstance(minute, int) or not 0 <= minute <= 59:
        raise ValueError(f"clock art minute must be int 0-59, got {minute!r}")
    if art.get("missing") not in (None, "hour", "minute", "both"):
        raise ValueError(
            "clock art missing must be hour/minute/both/None, "
            f"got {art.get('missing')!r}"
        )


def _validate_dots_art(art: dict) -> None:
    """Validate a dots art dict; raise ValueError on bad specs."""
    for field in ("rows", "cols"):
        val = art.get(field, 2)
        if isinstance(val, bool) or not isinstance(val, int) or val < 1:
            raise ValueError(f"dots art {field!r} must be int >= 1, got {val!r}")


def _validate_partitions_art(art: dict) -> None:
    """Validate a partitions art dict; raise ValueError on bad specs."""
    parts = art.get("parts")
    if not isinstance(parts, int) or isinstance(parts, bool) or not 2 <= parts <= 12:
        raise ValueError(f"partitions art needs integer parts 2-12, got {parts!r}")
    for field in ("broken", "shaded"):
        val = art.get(field)
        if val is None:
            continue
        idxs = val if isinstance(val, (list, tuple)) else [val]
        for idx in idxs:
            if not isinstance(idx, int) or isinstance(idx, bool) or not 0 <= idx < parts:
                raise ValueError(
                    f"partitions {field!r} must be an integer index 0-{parts - 1}, "
                    f"got {idx!r}"
                )


@dataclass
class ErrorAuditWorksheet(BaseWorksheet):
    """Bug-hunt worksheet with staged audit cards."""

    title: str
    instructions: str
    theme_label: str  # e.g. "Clock Doctor" — printed as a badge, theming only
    legend: List[str]  # error-type names for the diagnose stage
    specimens: List[ErrorAuditSpecimen]
    fix_mode: str = "rewrite"
    verify: bool = True
    adversarial: bool = False
    show_answers: bool = False
    fix_lines: int = 2  # ruled lines in rewrite mode
    columns: int = 1  # case cards per row (1 or 2; 2-up halves the whitespace)
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the worksheet."""
        header = [f"# {self.title}", f"*{self.theme_label}*", self.instructions]
        if self.legend and not self.adversarial:
            header.append("Suspects: " + ", ".join(self.legend))
        elif self.legend:
            header.append("ASSIGN SUSPECTS: " + ", ".join(self.legend))
        body = []
        for idx, spec in enumerate(self.specimens, start=1):
            block = [f"## Case {idx}: {spec.prompt}"]
            block.extend(f"    {line}" for line in spec.lines)
            if self.show_answers:
                if spec.bug_location:
                    block.append(f"    **Bug:** {spec.bug_location}")
                if spec.diagnosis:
                    block.append(f"    **Diagnosis:** {spec.diagnosis}")
                if spec.fix_text and self.fix_mode == "rewrite":
                    block.append(f"    **Fix:** {spec.fix_text}")
            else:
                block.append("    ( ) Bug circled")
                if self.legend:
                    block.append(
                        "    Diagnosis: "
                        + " / ".join(f"( ) {entry}" for entry in self.legend)
                    )
                if self.fix_mode == "rewrite":
                    if spec.fix_scaffold:
                        block.append("    Fix (line up the decimals):")
                        grid = decimal_stack_rows(
                            spec.fix_scaffold, filled=self.show_answers
                        )
                        for row in grid["terms"]:
                            block.append("    " + _scaffold_row_text(row))
                        block.append("    " + "-" * (len(grid["terms"][0]) * 2 + 1))
                        block.append("    " + _scaffold_row_text(grid["answer"]))
                        if grid["has_pads"]:
                            block.append("    (gray 0s are helpers — trace them)")
                    else:
                        block.append("    Fix:" + " _" * 20)
                elif self.fix_mode == "redraw":
                    if spec.blank_fix_circle:
                        block.append("    [blank circle — draw the partition lines]")
                    else:
                        block.append("    [redraw box]")
                if self.verify:
                    block.append("    ( ) Re-checked my fix")
            body.append("\n".join(block))
        return "\n\n".join(header + body)


def _scaffold_row_text(row: list[tuple[str, str]]) -> str:
    """Render one decimal_stack row as plain text (markdown fallback)."""
    glyphs = []
    for char, kind in row:
        if kind == "write":
            glyphs.append("_")
        elif kind == "spacer":
            glyphs.append(" ")
        else:
            glyphs.append(char)
    return " ".join(glyphs)


def _validate_fix_scaffold(scaffold: dict | None) -> None:
    """Validate a specimen's guided rewrite scaffold; raise ValueError."""
    if scaffold is None:
        return
    if not isinstance(scaffold, dict):
        raise ValueError(f"fix_scaffold must be a dict, got {scaffold!r}")
    kind = scaffold.get("kind")
    if kind != "decimal_stack":
        raise ValueError(
            f"fix_scaffold kind must be 'decimal_stack', got {kind!r}"
        )
    addends = scaffold.get("addends")
    answer = scaffold.get("answer")
    if not isinstance(addends, list) or not addends:
        raise ValueError("decimal_stack scaffold needs a non-empty 'addends' list")
    for label, value in [("answer", answer), *[(f"addend[{i}]", a) for i, a in enumerate(addends)]]:
        if not isinstance(value, str) or "." not in value:
            raise ValueError(
                f"decimal_stack {label} must be a decimal string like "
                f"'0.50', got {value!r}"
            )
        whole, _, frac = value.partition(".")
        if not whole.isdigit() or not frac.isdigit():
            raise ValueError(
                f"decimal_stack {label} must be digits around one '.', "
                f"got {value!r}"
            )


def decimal_stack_rows(
    scaffold: dict, *, filled: bool = False
) -> dict:
    """Build decimal-aligned grid rows for a decimal_stack scaffold.

    Every row has the same columns: integer digits right-aligned, one
    decimal-point column, fractional digits left-aligned. Short fraction
    parts are extended with ("0", "pad") helper cells meant to be traced.
    In student mode (filled=False) digit positions are ("", "write")
    blanks; in key mode (filled=True) they carry the answer digits.

    Returns {"terms": [[(char, kind)]], "answer": [(char, kind)],
    "has_pads": bool}. Kinds: "given" | "pad" | "point" | "write" |
    "spacer".
    """
    addends = list(scaffold.get("addends", []))
    answer = scaffold.get("answer", "")
    wholes = [a.partition(".")[0] for a in addends] + [answer.partition(".")[0]]
    fracs = [a.partition(".")[2] for a in addends] + [answer.partition(".")[2]]
    left = max(len(w) for w in wholes)
    right = max(len(f) for f in fracs)

    def _term_row(term: str) -> list[tuple[str, str]]:
        whole, _, frac = term.partition(".")
        cells: list[tuple[str, str]] = []
        for _ in range(left - len(whole)):
            cells.append(("", "spacer"))
        cells.extend((ch, "given") for ch in whole)
        cells.append((".", "point"))
        cells.extend((ch, "given") for ch in frac)
        for _ in range(right - len(frac)):
            cells.append(("0", "pad"))
        return cells

    def _answer_row() -> list[tuple[str, str]]:
        whole, _, frac = answer.partition(".")
        cells: list[tuple[str, str]] = []
        for _ in range(left - len(whole)):
            cells.append(("", "spacer"))
        if filled:
            cells.extend((ch, "given") for ch in whole)
            cells.append((".", "point"))
            cells.extend((ch, "given") for ch in frac)
            for _ in range(right - len(frac)):
                cells.append(("0", "pad"))
        else:
            cells.extend(("", "write") for _ in whole)
            cells.append((".", "point"))
            cells.extend(("", "write") for _ in frac)
            for _ in range(right - len(frac)):
                cells.append(("0", "pad"))
        return cells

    terms = [_term_row(a) for a in addends]
    ans = _answer_row()
    has_pads = any(kind == "pad" for row in terms + [ans] for _, kind in row)
    return {"terms": terms, "answer": ans, "has_pads": has_pads}


def _normalize_specimens(
    specimens: Sequence[ErrorAuditSpecimen | dict],
) -> List[ErrorAuditSpecimen]:
    normalized: List[ErrorAuditSpecimen] = []
    for item in specimens:
        if isinstance(item, ErrorAuditSpecimen):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(ErrorAuditSpecimen.from_mapping(item))
        else:
            raise TypeError("Specimens must be ErrorAuditSpecimen or dict entries")
        for target in (normalized[-1].art, normalized[-1].starter_art):
            if isinstance(target, dict):
                kind = target.get("kind")
                if kind == "partitions":
                    _validate_partitions_art(target)
                elif kind == "clock":
                    _validate_clock_art(target)
                elif kind == "dots":
                    _validate_dots_art(target)
        _validate_fix_scaffold(normalized[-1].fix_scaffold)
    return normalized


def generate_error_audit_worksheet(
    specimens: Sequence[ErrorAuditSpecimen | dict],
    *,
    title: str = "Bug Hunt",
    instructions: str = (
        "Something is wrong in each case. Circle the bug, "
        "diagnose it, fix it, then re-check your fix."
    ),
    theme_label: str = "Bug Hunter",
    legend: Sequence[str] | None = None,
    fix_mode: str = "rewrite",
    verify: bool = True,
    adversarial: bool = False,
    show_answers: bool = False,
    fix_lines: int = 2,
    columns: int = 1,
    metadata: dict | None = None,
) -> ErrorAuditWorksheet:
    """Create an error-audit worksheet.

    Args:
        specimens: Buggy cases to audit (at least one required).
        title: Worksheet title.
        instructions: Student instructions.
        theme_label: Theming badge (doctor, detective, ...). Cosmetic only.
        legend: Error-type names for the diagnose stage. Empty legend
            skips the diagnose stage (pure mark-and-fix).
        fix_mode: "rewrite" (ruled lines), "redraw" (empty box), or
            "none" (verdict/diagnose only).
        verify: Whether to print a re-check line per specimen.
        adversarial: Inverse mode — the student plants an assigned bug
            (Error Chef). Legend becomes the assignment list.
        show_answers: Answer-key mode (fills bug/diagnosis/fix).
        fix_lines: Ruled lines per specimen in rewrite mode.
        columns: Case cards per row, 1 or 2. Two-up rendering halves
            whitespace on short-card sheets.
        metadata: Optional metadata dictionary.
    """
    if fix_mode not in FIX_MODES:
        raise ValueError(f"fix_mode must be one of {FIX_MODES}, got {fix_mode!r}")
    normalized = _normalize_specimens(specimens)
    if not normalized:
        raise ValueError("At least one specimen is required")
    if fix_lines < 1:
        raise ValueError("fix_lines must be at least 1")
    if columns not in (1, 2):
        raise ValueError(f"columns must be 1 or 2, got {columns!r}")

    return ErrorAuditWorksheet(
        title=title,
        instructions=instructions,
        theme_label=theme_label,
        legend=list(legend or []),
        specimens=normalized,
        fix_mode=fix_mode,
        verify=verify,
        adversarial=adversarial,
        show_answers=show_answers,
        fix_lines=fix_lines,
        columns=columns,
        metadata=metadata or {},
    )


__all__ = [
    "ErrorAuditSpecimen",
    "ErrorAuditWorksheet",
    "generate_error_audit_worksheet",
    "decimal_stack_rows",
    "FIX_MODES",
]
