# Story 05 – API & Documentation Updates

## Goal
Expose the new worksheet resources through the FastAPI surface and ensure all public docs describe the enhanced response shape.

## Scope
- Update the Pydantic response models in `src/main.py` (or wherever FastAPI schemas live) to include the optional `resources` field with nested artifact metadata.
- Adjust any serialization helpers/loggers so the new data survives persistence and logging flows.
- Refresh `README.md`, `docs/ARCHITECTURE_IMPROVEMENTS.md`, and any onboarding material with examples that show worksheet resource objects and artifact references.
- Link to `docs/WORKSHEET_REQUEST_SCHEMA.md` from relevant docs so consumers know how requests map to responses.

## Acceptance Criteria
- FastAPI’s OpenAPI schema displays the new `resources` definitions, and the `/generate_weekly_plan` response example matches reality.
- Documentation screenshots/snippets highlight the worksheet feature and explain how consumers retrieve artifacts.
- Existing clients remain backward compatible (omitted `resources` keeps responses valid for older consumers).

## Dependencies
- Story 04 (API should advertise data that is actually produced).
