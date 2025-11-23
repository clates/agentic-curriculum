# Story 06 – Testing, Validation, and Rollout Controls

## Goal
Ensure the worksheet feature ships safely with automated coverage, validation hooks, and operational controls.

## Scope
- Expand `tests/validate_chunk4.py` (and other relevant validators) to assert that worksheet resource payloads and artifact metadata meet the schema from Story 01.
- Add integration tests that mock LLM outputs end-to-end, verifying that artifacts are generated and referenced correctly.
- Introduce a feature flag or environment variable (e.g., `ENABLE_WORKSHEETS`) so the feature can be toggled during rollout.
- Document operational guidance (log locations, artifact cleanup strategy, troubleshooting steps) in `docs/WORKSHEET_REQUEST_SCHEMA.md` or a new ops note.

## Acceptance Criteria
- `pytest` (or the existing test harness) covers the happy path and failure cases for the full worksheet pipeline.
- Validation scripts fail loudly if the LLM outputs malformed resource blocks.
- The feature flag defaults to disabled/enabled per team decision and is honored across CLI/API entry points.
- Ops documentation explains how to re-run rendering, how to inspect logs, and how to clean old artifacts.

## Dependencies
- Stories 01–05 must be complete so tests and flags can target the finalized behavior.
