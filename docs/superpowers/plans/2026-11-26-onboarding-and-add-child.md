# First-child onboarding and adding a child Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A newly registered family is guided to add its first child (name, interests, math and
language arts grades, notes), the child's first week starts, and the family can add more children
the same way, up to 5.

**Architecture:** A new family-scoped `POST /children` creates a child from the new profile shape and
starts its first week; the legacy `/students` routes stay as they are. The planner reads a grade per
subject. One shared React form serves the welcome page and "Add a child".

**Tech Stack:** FastAPI, SQLite, pytest, Next.js 16 / React 19, Playwright.

**Spec:** `docs/superpowers/specs/2026-11-25-family-accounts-design.md` — D4, "Design: E2 onboarding
and E4 add a child", builder-check calls 2 and 8.

## Global Constraints

- Every new route depends on `current_family`; another family's data answers 404 with the same body
  as a missing record. The route-inventory test must keep passing.
- Login off: nothing changes for self-hosters or the main E2E suite (no welcome redirect).
- Child profile, stored in `metadata_blob`: `name` (first name, 1–40 characters, trimmed),
  `interests` (0–8 items, each 1–40 characters), `math_grade` and `la_grade` (integers 0–8, 0 = K),
  `notes` (0–500 characters), plus `grade_level` = `la_grade`.
- At most 5 children per family: the 6th `POST /children` answers `409 {"detail": "too_many_children"}`
  and creates nothing.
- First week: added Monday–Wednesday (family-local date, `SCHEDULER_DEFAULT_TZ` when the family has
  no timezone) → this week's Monday; Thursday–Sunday → next Monday.
- Planner grades: Math skills compare to `math_grade`; every other subject to `la_grade`; a child
  without them keeps today's single-grade rule (`grade_level`, fallback grade, birthday).
- Form copy includes, verbatim: "These are starting points. We'll calibrate after the first few
  activities." and the existing note that an AI service reads what the parent writes.
- Python: black and ruff, 100-character lines. Frontend: Prettier, `npm run lint:copy`.

## Review Focus

1. **A 6th child requested twice at once** (double tap): must not create 6 or 7 children. Task 2
   tests a concurrent pair.
2. **Grades or interests that are out of range or not the right type** (`"3"`, `9`, `-1`, a 500-item
   list): 422 with nothing created. Task 2 tests them.
3. **Text the parent types that ends up in a model prompt** (interests, notes): length-capped and
   passed only through the existing allowlisted model context. Task 1 checks the context caps hold.
4. **A family that already has children never sees the welcome page; a family with none can still
   use other pages** (the redirect is only from This week). Task 3 tests both.
5. **The child whose week starts on a Thursday** lands on next Monday's week, not this one. Task 2
   tests a fixed clock on each weekday.

---

### Task 1: Grades per subject in the planner

**Files:** Modify `src/model_context.py`, `src/candidate_selector.py`, `src/pick_service.py`;
Test `tests/test_model_context.py`, `tests/test_candidate_selector.py` (extend).

**Interfaces — Produces:**
- `ModelStudentContext.math_grade: int | None`, `ModelStudentContext.la_grade: int | None`,
  `ModelStudentContext.grade_for(subject: str) -> int` (`"Math"` → math_grade, else la_grade, each
  falling back to `.grade`).
- `select_week_standards(..., grade: int, grade_by_subject: Mapping[str, int] | None = None, ...)`:
  when given, each standard is compared with `grade_by_subject.get(subject, grade)`.
- `load_candidate_inputs(db_path, grade, *, span=2, extra_grades=())` loads the union of spans.

- [ ] Write failing tests: a child with math 3 / LA 1 gets Math skills around grade 3 and English
      around grade 1; a child without the fields gets exactly today's selection (same seed → same
      ids); the model-facing lines mention both grades; interests and notes caps unchanged.
- [ ] Implement; run focused tests, then the full backend suite. Commit
      `feat: the planner picks math at the math grade and everything else at the language arts grade`.

### Task 2: `POST /children`

**Files:** Modify `src/main.py` (route + request model), `src/db_utils.py` (count helper if needed);
Test `tests/test_children_api.py`.

**Interfaces — Consumes:** `current_family`, `tenancy.new_student_id`, `db_utils.create_student(...,
family_id=)`, `loop_integration.start_week(conn, student_id, week_start, family_id=)`.
**Produces:** `POST /children {name, interests, math_grade, la_grade, notes}` → `201
{"student_id", "week_start"}`; 409 `too_many_children`; 422 on invalid input.

- [ ] Write failing tests: creates the child in the caller's family with a `stu_` id and the stored
      profile shape; starts the first week (a `week_plan` row for the computed Monday); the 6th child
      gets 409 and nothing is written; two simultaneous 5th/6th requests leave exactly 5 children
      (serialise the count-and-insert with `BEGIN IMMEDIATE`); invalid inputs from Review Focus 2 get
      422; weekday rule on a fixed clock for Mon/Wed/Thu/Sun; another family never sees the child
      (`/students` and `/this-week`).
- [ ] Implement; full backend suite. Commit `feat: add a child (profile, first week, at most five)`.

### Task 3: Welcome, the child form and "Add a child"

**Files:** Create `frontend/components/parent/ChildForm.tsx`, `frontend/app/welcome/page.tsx`,
`frontend/app/children/new/page.tsx`; Modify `frontend/app/week/page.tsx` (login-on first run: no
children → `/welcome`; an "Add a child" button when under 5), `frontend/lib/copy.ts`, the sign-up flow's
post-verify destination (`/welcome`), `frontend/e2e/COVERAGE.md`; Test
`frontend/e2e/auth/onboarding.spec.ts`, and the main project's existing This week specs unchanged.

- [ ] Write the failing spec (auth project): register → verify → lands on /welcome → fill the form →
      This week shows the child's card; "Add a child" → second child appears; with 5 children the
      button is gone and a direct POST gets the "five children" message; axe + no sideways scroll at
      360px on /welcome and /children/new; a family with children opening /welcome is sent to This
      week.
- [ ] Implement: grades as K–8 selects, interests as a comma-separated field split client-side,
      the calibration and AI notes verbatim.
- [ ] Full e2e, type-check, prettier, lint:copy, backend suite. Commit
      `feat(frontend): welcome a new family and add children`.

### Task 4: Docs

**Files:** a new `docs/how-to/add-a-child.md` (how-to), `docs/reference/` entry for `POST /children`
and the profile fields and limits (extend `docs/reference/development.md` API table or a new
`docs/reference/children.md`), `docs/explanation/the-weekly-loop.md` (one paragraph on grades per
subject and calibration), `docs/README.md` index.

- [ ] Each page its own Diátaxis kind; link check 0 problems. Commit `docs: adding a child`.
