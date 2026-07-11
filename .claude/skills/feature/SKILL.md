---
name: feature
description: Take a feature request through the full pipeline — explore, plan, implement on a branch, test, and open a PR. Use when the user requests a new feature or behavior change in the app.
---

# Feature pipeline

Input: a feature request, possibly one line. Output: a reviewed-ready PR with tests.

## 1. Scope

Restate the request in one sentence. If it is genuinely ambiguous (not just underspecified in ways
sensible defaults cover), ask **one** clarifying question; otherwise proceed.

## 2. Explore

Find the closest existing analog and mirror its structure rather than inventing new patterns:
- New endpoint → nearest endpoint in `src/main.py` + its test in `tests/test_*_api.py`
- New UI behavior → nearest page/component under `frontend/app/` + its spec in `frontend/e2e/`
- New worksheet type → existing type in `src/worksheets/` + `factory.py` registration + AGENTS.md §3

## 3. Plan

Write a short plan before coding: files to touch, tests to add, done-criteria. For non-trivial
features, show the plan to the user before implementing.

## 4. Branch

```bash
git fetch origin
git checkout -b feat/<kebab-slug> origin/main   # or fix/<kebab-slug>
```
Follow AGENTS.md §7 (never commit to `main`; verify the branch isn't already merged before pushing).

## 5. Implement

Match surrounding style. Before committing, on every file you touched:
`venv/bin/python -m ruff check --fix <files> && venv/bin/python -m black <files>` for Python,
`npm run format` for frontend files. Pre-commit hooks enforce these.

## 6. Test policy — required, within reason

- Each new backend behavior gets a pytest test (use `tests/factories.py` builders and
  `tests/conftest.py` fixtures; temp DBs only).
- Each UI-facing use case gets Playwright coverage of its **happy path** in the relevant
  `frontend/e2e/*.spec.ts` (seeding helpers in `e2e/fixtures/api.ts`). Cover the use case's
  correctness, **not** exhaustive boundary matrices.
- No new test frameworks. Ad-hoc lesson content (`/generate-week`) is exempt from this policy.

## 7. Verify

Use the `/test` skill. While iterating, run single files/specs; before the PR, all of:

```bash
venv/bin/python -m pytest tests/ -v --tb=short
cd frontend && npm run type-check && npm run format:check && npm run test:e2e
```

All green before opening the PR. Report failures verbatim — never weaken an existing test to pass.
If a check fails, confirm it isn't pre-existing (`git stash && <re-run check> && git stash pop`):
report pre-existing failures to the user separately instead of bundling fixes into your PR.

## 8. PR

```bash
git push -u origin <branch>
gh pr create --head <branch> --base main --title "feat: <summary>" --body "..."
```

(`--head`/`--base` are required when the working tree has unrelated uncommitted files —
without them `gh` may refuse to pick a branch.)

- Conventional-commit title (`feat:` / `fix:`).
- Body: what & why, test evidence (suite counts), `Closes #N` when an issue exists.
- End the body with the standard Claude Code attribution footer.
