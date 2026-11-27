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
- The limit counts the children the family has now. Deleting a child frees a place.

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
| `/children/new` | The form, or a notice when the family has 5. Returns to `/week` after saving; with `?from=students`, to `/students` |
| `/students` | With login on, "Add a child" opens `/children/new?from=students` |
| `/week` | An "Add a child" button when login is on and the family has fewer than 5 |

The form says: "These are starting points. We'll calibrate after the first few activities."

Why: [The weekly loop](../explanation/the-weekly-loop.md#why-math-has-its-own-grade),
[why at most five](../explanation/the-weekly-loop.md#why-a-family-has-at-most-five-children).
