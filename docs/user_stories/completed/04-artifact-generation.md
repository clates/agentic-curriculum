# Story 04 – Artifact Generation & Response Augmentation

## Goal
Render requested worksheets to disk and attach artifact metadata back onto each `daily_plan` entry so API clients can link to the files.

## Scope
- Decide on an artifact layout (e.g., `artifacts/{plan_id}/{day}/`) and ensure directories are created automatically.
- Use `render_worksheet_to_image/pdf` (and the reading equivalents) to emit at least one deterministic format per worksheet (PNG or PDF minimum; both if feasible).
- Extend the day-plan data structure to include `resources.<type>.artifacts = [{"type": "pdf", "path": "..."}, ...]`.
- Ensure rendering happens after lesson JSON parsing but before the final weekly plan is returned.

## Acceptance Criteria
- Running the weekly planner with mocked LLM responses that include worksheet requests produces real files in the artifact directory.
- The returned `weekly_plan.daily_plan[*].resources` entries include artifact metadata with absolute or repo-relative paths.
- Errors during rendering are logged and result in the offending artifact being skipped while other resources continue processing.
- Basic cleanup (e.g., ensuring previous runs don’t overwrite unless intended) is addressed or documented.

## Dependencies
- Story 03 (requires worksheet objects + render configuration).
