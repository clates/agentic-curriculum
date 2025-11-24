# Story 07 – Weekly Packet Persistence

## Goal
Persist every generated weekly packet (lesson plans plus worksheet manifest) to SQLite so subsequent API calls can reference durable data instead of re-running the generator.

## Scope
- Introduce normalized tables for `weekly_packets`, `daily_lessons`, and `worksheet_artifacts` with migrations and indexes on `student_id`, `week_of`, and `status`.
- Extend `agent.generate_weekly_plan` to write the produced JSON + artifact metadata into the new tables atomically, reusing existing worksheet serialization output.
- Record artifact filesystem paths (relative to the repo root) plus content metadata (kind, format, checksum, size) for future download endpoints.
- Keep legacy `/generate_weekly_plan` behavior and response shape stable by layering persistence underneath without changing the HTTP contract.

## Acceptance Criteria
- Generating a plan inserts exactly one `weekly_packets` row, five `daily_lessons` rows, and matching `worksheet_artifacts` rows per produced PDF/PNG file, with referential integrity enforced.
- Restarting the API server still allows previously generated packet data to be retrieved directly from the database; logs and artifacts remain consistent via the stored relative paths.
- Failures during DB writes surface clear errors and leave no partial rows (transactional rollback verified in tests).
- FastAPI’s OpenAPI schema references the persisted models (Pydantic) so future endpoints reuse the same structures.

## Dependencies
- Story 04 ensured worksheet serialization produces artifact files and metadata the persistence layer can reuse.
