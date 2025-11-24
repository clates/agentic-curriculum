# Story 10 – Generation Workflow & Status

## Goal
Introduce a first-class workflow for triggering weekly packet generation via POST plus pollable status endpoints (including `/current`) so the UI can guide parents from request to completion without manual refreshes.

## Scope
- Add `POST /students/{student_id}/weekly-packets` that validates inputs, enqueues `generate_weekly_plan` (background task or job queue), and immediately returns `202 Accepted` with `packet_id`, `status`, and URLs for polling.
- Implement `/students/{student_id}/weekly-packets/status/{packet_id}` (or similar) and `/students/{student_id}/weekly-packets/current` that expose packet states (`pending`, `ready`, `failed`), timestamps, and optional progress metadata.
- Prevent duplicate packets in the same `week_of` unless `force_regenerate` is specified; tie status transitions to persistence completion (Story 07) and log failures for observability.
- Ensure the legacy synchronous `/generate_weekly_plan` path either delegates to the new workflow or is clearly documented as deprecated once parity is reached.

## Acceptance Criteria
- POST endpoint responds within ~1s, returns `202` body `{packet_id, status: "pending", status_url, current_url}`; invalid inputs raise FastAPI validation errors.
- Status and `/current` endpoints reflect real-time state changes: immediately `pending` after POST, flip to `ready` when data + artifacts are written, `failed` with an `error` payload when generation throws.
- Concurrent POST requests for the same student/week either reuse the existing pending packet or honor `force_regenerate`; no duplicate `ready` packets are created unintentionally.
- Tests cover POST happy path, status polling, `/current` behavior (pending + ready), and race conditions around duplicate submissions.

## Dependencies
- Stories 07–09 supply the persisted data, retrieval surfaces, and artifact metadata consumed once generation completes.
