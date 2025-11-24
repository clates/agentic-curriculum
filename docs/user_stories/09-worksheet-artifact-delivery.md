# Story 09 – Worksheet Artifact Delivery

## Goal
Provide stable, secure download surfaces for every worksheet artifact (PNG/PDF) so parents can open resources from the UI long after generation.

## Scope
- Implement `/students/{student_id}/weekly-packets/{packet_id}/worksheets` to return a manifest of available artifacts, grouped by day and worksheet kind with human-friendly labels.
- Add `/worksheet-artifacts/{artifact_id}` (or equivalent signed URL redirect) that streams the underlying file with accurate headers, caching directives, and authorization tied back to the student.
- Capture and expose artifact metadata stored in Story 07 (format, checksum, file size, last_generated_at) to help clients prefetch or validate downloads.
- Handle missing or corrupted files gracefully, surfacing actionable errors and telemetry without crashing the API.

## Acceptance Criteria
- Manifest endpoint lists every artifact for the packet, including day label, worksheet kind, available formats, relative URLs, and last-generated timestamps; response matches OpenAPI schema examples.
- Download endpoint successfully streams both PNG and PDF artifacts with correct `Content-Type`, `Content-Length` (when available), and cache headers; unauthorized or expired links return `403/404` as appropriate.
- Tests cover manifest generation, download success, missing-file scenarios, and authorization edge cases.
- Observability logs/metrics capture artifact downloads for future rate tracking.

## Dependencies
- Story 07 persistence (artifact table) and Story 08 retrieval APIs for packet ownership and metadata.
