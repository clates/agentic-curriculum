# Story 01 – Worksheet Request Models

## Goal
Provide strongly typed request objects that mirror `docs/WORKSHEET_REQUEST_SCHEMA.md` so worksheet payloads coming from the LLM can be validated before downstream processing.

## Scope
- Introduce a new module (e.g., `src/resource_models.py`) containing Pydantic models for `MathWorksheetRequest`, `ReadingWorksheetRequest`, and a parent `ResourceRequests` wrapper.
- Enforce helper-aligned constraints (integer operands, operator enum, ≥1 problem/question, max practical limits to keep render time predictable).
- Surface friendly validation errors that can be logged without interrupting weekly plan generation.
- Add unit tests that cover happy-path and failure cases for each model.

## Acceptance Criteria
- Deserializing a sample payload from `docs/WORKSHEET_REQUEST_SCHEMA.md` produces fully validated model instances.
- Invalid inputs (e.g., unsupported operators, empty question arrays) raise descriptive validation errors caught by callers.
- Tests live under `tests/` and run via `pytest` (or existing harness) without additional setup.
- Documentation in the schema file references the new module so future contributors know where validation lives.

## Dependencies
- None (this is the first story and unblocks the remainder).
