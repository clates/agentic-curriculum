# Children reference

Adding a child to a family. Steps: [Add a child](../how-to/add-a-child.md).

## `POST /children`

Adds a child to the caller's family and starts its first week. With the login on, it needs a
signed-in family. With the login off, the child goes to the server's one family.

Request body. Unknown fields are refused, and numbers must be real integers (not `"3"`, `3.0` or
`true`).

| Field | Type | Limits |
|---|---|---|
| `name` | string | 1 to 40 characters after trimming |
| `interests` | list of strings | up to 8, each 1 to 40 characters after trimming. Default `[]` |
| `math_grade` | integer | 0 to 8, where 0 is kindergarten |
| `la_grade` | integer | 0 to 8, where 0 is kindergarten |
| `notes` | string | up to 500 characters after trimming. Default empty |

The server also stores `grade_level`, set to `la_grade`.

| Status | Meaning |
|---|---|
| 201 | Added. Body: `{"student_id": "...", "week_start": "YYYY-MM-DD"}` |
| 401 | Login on and not signed in. Nothing is created |
| 409 | `too_many_children`: the family already has 5 |
| 422 | Invalid input |

## First week

`week_start` is the Monday of the child's first week, using the family's local date: the
family's timezone in `family_settings`, else `SCHEDULER_DEFAULT_TZ`. If that timezone doesn't load,
the UTC date is used.

| Added on | First week starts |
|---|---|
| Monday to Wednesday | This Monday |
| Thursday to Sunday | Next Monday |

With `LOOP_JOBS_ENABLED` on, the week is started: the check-in is skipped and the outlines are
queued. With it off, only the plan is made, and nothing is queued or paid for. If starting the
week fails, the child is still saved and "This week" makes the plan on its next read.

## Limits

- At most 5 children per family. The count and the insert happen in one write transaction.
- With the login on, `POST /students` has the same limit and also returns 409 `too_many_children`.
- On a self-hosted server without login, `POST /children` applies the same limit.
- The limit counts children now. Deleting a child frees a place, so it doesn't cap spending.

## Grades in planning

| Subject | Grade used |
|---|---|
| Math | `math_grade` |
| Every other subject | `la_grade` |

A child with no `math_grade` or `la_grade` (an older profile) is planned at its single `grade`.

## Web pages

| Page | Shows |
|---|---|
| `/welcome` | The form, for a family with no children. Sends a family that has children to `/week` |
| `/children/new` | The form, or a notice when the family has 5 |
| `/week` | An "Add a child" button when login is on and the family has fewer than 5. Each child's card links to "Past weeks" and "Skills by subject" |
| `/children/{student_id}` | The child's page, headed by the child's first name ("Your child" when the name is empty): "Past weeks", then "Skills by subject". "We couldn't find that child" for an unknown child. The browser tab reads "Your child" |

### Child page

| Section | Shows |
|---|---|
| Past weeks | Weeks already written, newest first, up to 50. Each shows "Checked in" or "Not checked in yet" (`has_feedback` in the weekly-packets list) and links to the documents that exist: the child's pages, the teacher guide, the prep sheet. A week still being written is not listed. If a week's documents can't be loaded, the week says so and shows "Try again" |
| Skills by subject | One bar per subject from `GET /students/{student_id}/coverage`: solid, shaky, still to come. A child with no history has bars that are all still to come. "Nothing to show yet" only when the child's grades have no skills and there is no progress |

Only the newest 50 weeks show. Older weeks stay saved but have no link here.

The form says: "These are starting points. We'll calibrate after the first few activities."

Why: [The weekly loop](../explanation/the-weekly-loop.md#why-math-has-its-own-grade).

## `GET /students/{student_id}/coverage`

Returns a list, one object per subject. Counts only: no standard ids or skill names.

```json
[{"subject": "Math", "solid": 12, "shaky": 3, "to_come": 20}]
```

| Field | Counts |
|---|---|
| `solid` | Mastered skills, including ones due for a refresher |
| `shaky` | Skills that are shaky or need more work |
| `to_come` | Whole skills at the child's grade for the subject that are neither solid nor shaky |

"Shaky" and "needs more work" are defined in `classify_progress` in `src/progress_summary.py`.
The grade for `to_come` is `math_grade` for Math and `la_grade` for every other subject (see
[Grades in planning](#grades-in-planning)). Only whole skills count (`is_whole_skill` in
`src/candidate_selector.py`).

Subjects come in the order Math, English, Science, History, Computer Science, then the rest
alphabetically. A subject with no counts is left out.

| Status | When |
|---|---|
| 404 `Student not found` | The child doesn't exist, or belongs to another family |
