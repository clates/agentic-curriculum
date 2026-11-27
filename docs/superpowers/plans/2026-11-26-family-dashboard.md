# Family dashboard (v1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** From This week, a parent opens a child's page showing their past weeks (with the three
printable documents) and simple per-subject coverage bars.

**Architecture:** One new family-scoped read endpoint computes coverage; past weeks reuse the existing
weekly-packets list and print-info. The This week cards gain two links.

**Tech Stack:** FastAPI, SQLite, pytest, Next.js 16 / React 19, Playwright.

**Spec:** `docs/superpowers/specs/2026-11-25-family-accounts-design.md` — D6, "Design: E3 family
dashboard (v1)", builder-check calls 6 and 7.

## Global Constraints

- New routes take `owned_student_id` (404 with the same body for missing or another family's child).
- Coverage per subject: `solid` and `shaky` from the child's progress data; `to_come` = that
  subject's skills at the child's grade for the subject (math grade for Math, language arts grade
  otherwise; `grade_level` fallback) that are neither. Plain words on screen, no standard ids.
- Past weeks: the child's written weeks from the existing weekly-packets list, newest first, with the
  documents print-info says exist. A week still being written is not listed.
- Login off: works the same for self-hosters (no new gating).

## Review Focus

1. **A child with no history** shows an empty past-weeks state and coverage bars with only "still to
   come". Task 1 and Task 2 test it.
2. **Another family's child id** on the new endpoint and the new page → 404 / "We couldn't find that
   child". Task 1 tests the API; the inventory test covers the route.
3. **A subject the child has progress in but no grade-level standards** (e.g. a skill from another
   grade): counts in solid/shaky without breaking `to_come`. Task 1 tests it.

---

### Task 1: `GET /students/{student_id}/coverage`

**Files:** Create `src/coverage.py`; Modify `src/main.py`; Test `tests/test_coverage.py`.
**Produces:** `[{"subject": str, "solid": int, "shaky": int, "to_come": int}]`, subjects ordered
Math, English, Science, History, Computer Science, then others; only subjects with any count.

- [ ] Failing tests: Review Focus 1–3, the per-subject grade rule, isolation (B gets 404).
- [ ] Implement; full backend suite. Commit `feat: per-subject coverage for a child`.

### Task 2: The child page and the This week links

**Files:** Create `frontend/app/children/[studentId]/page.tsx`; Modify the This week card component
(links "Past weeks" and "How it's going"), `frontend/lib/copy.ts`, `frontend/e2e/COVERAGE.md`; Test
`frontend/e2e/parent/child-page.spec.ts`.

- [ ] Failing spec: a child with two written weeks lists both newest first with their document links;
      the coverage bars show per-subject counts in words; an unknown child shows "We couldn't find
      that child"; axe + no sideways scroll at 360px.
- [ ] Implement; full e2e, type-check, prettier, lint:copy. Commit
      `feat(frontend): a page per child with past weeks and coverage`.

### Task 3: Docs

**Files:** `docs/reference/` (the coverage endpoint), `docs/how-to/track-a-student.md` or a new
how-to for the hosted dashboard, `docs/README.md`.

- [ ] Diátaxis kinds; link check 0 problems. Commit `docs: the family dashboard`.
