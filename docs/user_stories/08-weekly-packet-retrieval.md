# Story 08 – Weekly Packet Retrieval APIs

## Goal
Expose read-only FastAPI endpoints that list historical weekly packets and return full packet details so parents can revisit any prior week without regenerating plans.

## Scope
- Add `GET /students/{student_id}/weekly-packets` with pagination, `week_of` filters, and lightweight metadata (subject, grade, status, worksheet counts, focus tags) sourced from the persistence tables.
- Add `GET /students/{student_id}/weekly-packets/{packet_id}` (and optionally `/days/{day}` for narrow views) that returns the entire stored weekly plan, including embedded worksheet manifests.
- Reuse existing Pydantic models to serialize the persisted data and surface caching hints (ETag/Last-Modified) for clients polling frequently.
- Enforce ownership: students can only access their packets; unexpected IDs return `404` without leaking existence.

## Acceptance Criteria
- Listing endpoint responds within pagination limits, sorted by `week_of desc`, and includes a consistent metadata envelope (`packet_id`, `week_of`, `status`, `worksheet_counts`, `updated_at`).
- Detail endpoint returns the exact payload previously persisted (weekly overview + five daily lessons + resource metadata) and matches OpenAPI documentation.
- Requesting a packet that does not belong to the student yields a `404` with structured error; invalid IDs or filters are validated via FastAPI responses.
- Automated tests cover both endpoints for success paths, pagination, filtering, and authorization failures.

## Dependencies
- Story 07 provides the persisted packet/daily/artifact tables that these endpoints read from.
