# Friday form contract

What the Friday form (the parent's end-of-week check-in) sends and reads. The backend half lives
in `src/feedback_service.py`, `src/progress_summary.py` and `src/review_policy.py`.

## 1. What the form needs to know

Read the packet's checks (id, standard, prompt, "what a good answer sounds like"). They come from
the stored week's `prep_checks`. Each check has a stable id for that packet. The form shows one
row per check with three buttons: **Got it**, **Shaky**, **Missed**.

## 2. Submit

`POST /students/{student_id}/weekly-packets/{packet_id}/feedback` (204 on success)

Send exactly one of:

```json
{ "check_results": { "<check_id>": "got_it" | "shaky" | "missed" }, "workload": -2 }
```
```json
{ "quick_rating": "smooth" | "mixed" | "rough", "workload": 0 }
```

- `workload` is optional: -2 (far too little) to 2 (far too much), 0 is just right.
- Not every check has to be ticked, but a skill only counts as solid once every one of its checks
  was ticked Got it. Any Missed marks the skill as needing work; otherwise any Shaky marks it shaky.
- A quick rating never credits mastery. Smooth changes nothing, mixed marks the week's skills
  shaky, rough marks them as needing work. Prefer per-check results when the parent has them.
- Sending both `check_results` and `quick_rating` is a 422. Unknown check ids or values are 400,
  an unknown packet or student is 404.
- Mixing in the old `mastery_feedback` field is a 422. The old fields alone still work.

## 3. Editing

Submit again for the same packet. The new submission replaces the old one in a single transaction:
the earlier effect on mastery and workload is undone, then the new one applied. Sending the exact
same body again changes nothing and does not queue plan generation, so double taps are safe.

## 4. Read back

- `GET /students/{student_id}/weekly-packets/{packet_id}/feedback` returns what was saved:
  `check_results` (raw ticks, the source of truth), `quick_rating`, `quantity_feedback`
  (the workload), `derived_mastery`, and `version` (1 on first save, +1 per edit).
- `GET /students/{student_id}/progress-summary` answers "how is my child doing?" in plain words:
  `summary` (one sentence), `solid`, `shaky`, `needs_work`, `due_for_review` (each with a short
  `why`), and `last_four_weeks`. It carries no ids or internal terms, so it can be shown as is.

## 5. What the form should show after saving

Re-fetch the progress summary and show `summary` plus the `due_for_review` list as "coming back
next week". Do not compute any of it client side.
