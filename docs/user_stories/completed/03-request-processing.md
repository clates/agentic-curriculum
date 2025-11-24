# Story 03 – Worksheet Request Processing

## Goal
Transform validated worksheet requests into in-memory worksheet objects ready for rendering.

## Scope
- Create a helper module (e.g., `src/worksheet_requests.py`) that translates `MathWorksheetRequest`/`ReadingWorksheetRequest` models into calls to `generate_two_operand_math_worksheet` and `generate_reading_comprehension_worksheet`.
- Return lightweight results that include the generated worksheet object plus minimal metadata needed by later stages (e.g., target filenames, labels pulled from `metadata`).
- Handle per-day batching so multiple worksheet types can be processed sequentially without duplicating code.
- Ensure failures in one worksheet request do not prevent other resources from being processed for the same day.

## Acceptance Criteria
- Given a validated request model, the helper returns a tuple/object containing the worksheet instance and render configuration.
- Errors from `generate_*` helpers are caught and logged, and the failure is surfaced back to the caller without raising uncaught exceptions.
- Unit tests cover math-only, reading-only, both types, and failure scenarios.

## Dependencies
- Story 02 (parsing layer must deliver validated request models to this module).
