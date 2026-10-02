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
    art: dict | None = None  # optional picture: {"kind": "clock"|"dots", ...}
    #   clock: {"hour": 3.0, "minute": 30, "missing": "minute"|"hour"|None}
    #     hour is a clock position (3.5 = halfway past 3); minute is 0-59.
    #   dots: {"rows": 3, "cols": 4} — filled-circle array grid.

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
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the worksheet."""
        header = [f"# {self.title}", f"*{self.theme_label}*", self.instructions]
        if self.legend and not self.adversarial:
            header.append("Suspects: " + ", ".join(self.legend))
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
                    block.append("    Fix:" + " _" * 20)
                elif self.fix_mode == "redraw":
                    block.append("    [redraw box]")
                if self.verify:
                    block.append("    ( ) Re-checked my fix")
            body.append("\n".join(block))
        return "\n\n".join(header + body)


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
        metadata: Optional metadata dictionary.
    """
    if fix_mode not in FIX_MODES:
        raise ValueError(f"fix_mode must be one of {FIX_MODES}, got {fix_mode!r}")
    normalized = _normalize_specimens(specimens)
    if not normalized:
        raise ValueError("At least one specimen is required")
    if fix_lines < 1:
        raise ValueError("fix_lines must be at least 1")

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
        metadata=metadata or {},
    )


__all__ = [
    "ErrorAuditSpecimen",
    "ErrorAuditWorksheet",
    "generate_error_audit_worksheet",
    "FIX_MODES",
]
