# Story 02 – Prompt & Parsing Updates

## Goal
Teach the lesson-planning LLM how to request worksheets and ensure daily plan parsing preserves the optional `resources` block without breaking existing behavior.

## Scope
- Update `_build_day_plan` (and related helpers) in `src/agent.py` to expand the system/user prompts with concise instructions describing when and how to emit `daily_plan[n].resources`.
- Provide one or two few-shot snippets showing math and reading worksheet requests so the model sees the target structure.
- After receiving each daily lesson response, attempt to parse a `resources` object using the models from Story 01; log-and-drop invalid payloads.
- Keep prompts focused on sparsity (“omit the key when no worksheet is needed”) to avoid bloated responses.

## Acceptance Criteria
- The prompt template includes explicit mention of `mathWorksheet`/`readingWorksheet` schemas and expectations on optionality.
- When the LLM omits `resources`, the code path behaves exactly as before.
- Valid `resources` payloads deserialize successfully; invalid ones do not crash the agent and are reported via structured logs.
- Unit tests mock the OpenAI response to verify parsing logic for: no resources, valid math worksheet, valid reading worksheet, invalid payload.

## Dependencies
- Story 01 (models are required to parse/validate responses).
