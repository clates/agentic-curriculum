# User Flows — CurricuLearn

Last updated: 2026-10-03 (post-deploy verification). Documents expected behavior per flow vs. observed behavior. Gaps are flagged with ⚠️.

---

## 1. Student Management

### Create Student
| Step | Expected | Endpoint | Status |
|------|----------|----------|--------|
| Navigate to /students | See student list with existing students | `GET /students` | ✅ |
| Click "Add Student" | Form opens with ID, name, birthday fields | — | ✅ |
| Submit valid data | Student created, appears in list | `POST /students` | ✅ |
| Invalid ID (special chars) | Validation error shown inline | — | ✅ |
| Empty name | ⚠️ Should reject whitespace-only | — | ⚠️ passes |
| Duplicate ID | Error "already exists" | — | ✅ |
| Missing birthday | Validation error | — | ✅ |

### View/Edit Student
| Step | Expected | Endpoint | Status |
|------|----------|----------|--------|
| Click student card | Opens edit modal with current data | `GET /student/{id}` | ✅ |
| Update name | Name changes on save | `PUT /student/{id}` | ✅ |
| Partial update (name only) | Birthday preserved | — | ✅ |

### Delete Student
| Step | Expected | Endpoint | Status |
|------|----------|----------|--------|
| Click delete | Confirmation dialog appears | — | ✅ |
| Confirm delete | Student removed from list | `DELETE /student/{id}` | ✅ |

---

## 2. Weekly Plan Generation

| Step | Expected | Endpoint | Status |
|------|----------|----------|--------|
| Navigate to /plans | See pending + completed sections | `GET /students/{id}/weekly-packets` | ✅ |
| Click "Generate New Plan" | Modal with student/grade/subject selects | `GET /system/options` | ✅ |
| Select all fields | "Generate Plan" button enabled | — | ✅ |
| Submit | Toast: "Plan is being generated!" | `POST /generate_weekly_plan` | ✅ |
| Generation completes | New packet appears after auto-refresh | — | ✅ |
| ⚠️ LLM unavailable | Plan generates but with 0 worksheet artifacts, generic fallback lessons | — | ⚠️ known |

---

## 3. Packet Review

| Step | Expected | Endpoint | Status |
|------|----------|----------|--------|
| Click pending packet card | Plan detail modal opens | `GET /students/{id}/weekly-packets/{pid}` | ✅ |
| View daily plans | Each day shows: focus, objective, procedure steps, worksheets | — | ✅ |
| See worksheet artifacts | List of worksheets with download links | `GET /students/{id}/weekly-packets/{pid}/worksheets` | ✅ |
| Click "Print All" | New tab with printable HTML, auto window.print() | `GET /students/{id}/weekly-packets/{pid}/print` | ✅ |
| Close modal | Modal dismissed (Close, Escape, backdrop click) | — | ✅ |
| ⚠️ Standards shown as wall of text | Should be formatted as list | — | ⚠️ UX |
| ⚠️ Keyboard accessibility | Plan cards now have role=button, tabIndex, key handlers | — | ✅ fixed |
| ⚠️ Print All | Opens print tab and renders correctly, but throws React #185 (max update depth) in calling tab | — | ⚠️ |

---

## 4. Feedback Submission

| Step | Expected | Endpoint | Status |
|------|----------|----------|--------|
| Open pending packet | "Provide Feedback" button visible (no prior feedback) | — | ✅ |
| Click "Provide Feedback" | Feedback modal opens | — | ✅ |
| Select mastery rating | Rating highlighted with ring | — | ✅ |
| Select workload rating | Submit button enables (both required) | — | ✅ |
| Submit | Modal closes, button changes to "Edit Feedback" | `POST /students/{id}/weekly-packets/{pid}/feedback` | ✅ |
| STRUGGLING rating | Now accepted (cooldown=0, same as NOT_STARTED) | — | ✅ fixed |
| DEVELOPING rating | Accepted (cooldown=1 week) | — | ✅ |
| MASTERED rating | Accepted (moves to mastered list, progressive cooldown) | — | ✅ |
| Edit existing feedback | "Edit Feedback" opens modal with pre-filled ratings | `GET .../feedback` | ✅ |
| Update Feedback | Submits updated ratings | `POST .../feedback` | ✅ |
| ⚠️ Empty body {} | Previously overwrote feedback with nulls — now rejected | — | ✅ fixed |
| ⚠️ Double-submit protection | No debounce on submit button — multiple POSTs possible | — | ⚠️ |
| Failed submission (400/500) | Error toast shown (#129) | — | ✅ fixed |

### Feedback — Locked State
| Step | Expected | Status |
|------|----------|--------|
| Feedback >3 weeks old | "Feedback Submitted" button shown, disabled | ✅ |
| Recent feedback | "Edit Feedback" button enabled | ✅ |

---

## 5. Dashboard

| Step | Expected | Endpoint | Status |
|------|----------|----------|--------|
| Navigate to / | Redirects to /dashboard | — | ✅ |
| See student cards | Shows real name, grade, subject, progress | `GET /students` | ✅ fixed |
| Stats: "Plans This Week" | Counts packets with week_of = current Monday | — | ✅ fixed |
| Stats: "Worksheets Ready" | Total worksheets across all packets | — | ✅ |
| "Submit Feedback" button | Navigates to /plans via Link wrapper (#129) | — | ✅ fixed |
| ⚠️ Grade label | Now shows real grade_level (or Kindergarten) | — | ✅ fixed |

---

## 6. Progress Map

| Step | Expected | Endpoint | Status |
|------|----------|----------|--------|
| Select student + subject | Progress map renders with nodes/edges | `GET /students/{id}/progress-map/{subject}` | ✅ |
| Error state | Red card with "Failed to load" + retry button | — | ✅ fixed |
| ⚠️ Missing curriculum.db | Returns empty graph (nodes=0) — no standards data to map | — | ⚠️ data |

---

## 7. Navigation & Shell

| Step | Expected | Status |
|------|----------|--------|
| Dashboard link | Navigates to /dashboard | ✅ |
| Students link | Navigates to /students | ✅ |
| Plans link | Navigates to /plans | ✅ |
| Progress Map link | Navigates to /progress | ✅ |
| ⚠️ Settings link | Removed (was dead href="#") | ✅ fixed |
| 404 page | Styled page with "Back to Dashboard" link | ✅ fixed |
| Welcome message | "Welcome back!" (was "Welcome back, Sarah!") | ✅ fixed |

---

## API Reference

| Flow | Method | Path |
|------|--------|------|
| List students | GET | `/students` |
| Create student | POST | `/students` |
| Get student | GET | `/student/{id}` |
| Update student | PUT | `/student/{id}` |
| Delete student | DELETE | `/student/{id}` |
| Generate plan | POST | `/generate_weekly_plan` |
| List packets | GET | `/students/{id}/weekly-packets` |
| Get packet | GET | `/students/{id}/weekly-packets/{pid}` |
| Worksheet manifest | GET | `/students/{id}/weekly-packets/{pid}/worksheets` |
| Print packet | GET | `/students/{id}/weekly-packets/{pid}/print` |
| Submit feedback | POST | `/students/{id}/weekly-packets/{pid}/feedback` |
| Get feedback | GET | `/students/{id}/weekly-packets/{pid}/feedback` |
| Progress map | GET | `/students/{id}/progress-map/{subject}` |
| Curriculum graph | GET | `/curriculum/graph/{subject}` |
| System options | GET | `/system/options` |
| Health | GET | `/health` |

---

## Recently Deployed (2026-10-03)

All verified on prod:

| Fix | PR |
|-----|-----|
| Dashboard button navigation (Link wrapper) | #129 |
| Pending plans filter excludes feedback-submitted packets | #129 |
| Silent feedback errors now show toast | #129 |
| STRUGGLING rating support | #126 |
| Null/empty feedback rejection | #126 |
| Progress page error state (was misleading empty) | #123 |
| Dashboard real student data + stats | #124 |
| "Plans This Week" filtering | #124 |
| Generator scripts PIL cleanup | #125 |
| SQLite WAL mode + busy_timeout (DELETE timeout) | #127 |
| User flows documentation | #128 |

## Known Gaps (not yet addressed)

- ⚠️ No double-submit protection on feedback/generate buttons
- ⚠️ Whitespace-only student names pass validation
- ⚠️ curriculum.db missing → progress map + curriculum graph always empty (nodes=0, edges=0 for all subjects)
- ⚠️ Plan generation produces 0 artifacts when LLM unavailable (no API key?)
- ⚠️ Standards rendered as run-on text in plan modal
- ⚠️ "Plans This Week" counts current week → shows 0 when no plans generated this week (correct but confusing)
- ⚠️ "Worksheets Ready" counts ALL worksheets ever, not just "ready" ones
- ⚠️ Past-dated plans shown identically to current ones
- ⚠️ Print All throws React error #185 (max update depth) in main tab — packet renders fine but console errors