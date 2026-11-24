# The weekly loop

The hosted app is built around one cycle a week. The parent says how last week went, the system
proposes three ideas for the next one, the parent picks one, the system writes it, and the parent
prints it. Then the cycle starts again.

```
Feedback → Feed forward → Outlines → Pick → Author → Print → (next week)
 parent      system        system    parent  system    parent
```

## The six steps

**Feedback** is the Friday check-in. The parent marks each of the week's checks as *got it*,
*shaky* or *missed*, or gives a quick overall rating, and says whether the workload was right.

**Feed forward** turns that into what next week should cover. Solid skills step aside for a
while, shaky ones come back, and the amount of work goes up or down. This step is entirely the
system's. No model is involved, so it's cheap, repeatable and easy to check.

**Outlines** asks a model for three short ideas for the week, each built around the skills feed
forward chose and the child's interests. One is deliberately a fresh direction, so a child who
always gets dinosaurs sees something else on offer.

**Pick** is the parent's choice among the three. It's the one place a person shapes the week's
theme, and it stays a single click.

**Author** is the expensive step. A model writes the whole week as a structured document, then the
server checks it: every day present, every planned skill taught, answers kept apart from the
child's pages. When a check fails, the model is asked to repair the week, within a spending cap.

**Print** is the parent printing the packet, the teacher guide and the prep sheet. Marking the
week printed closes it.

## Why it runs on a schedule

A family shouldn't have to remember to press anything for Monday's packet to exist. So a scheduler
works through the weekend in the family's own timezone: a reminder on Friday afternoon, a nudge on
Saturday morning, a last call on Sunday morning. If nobody has picked by Sunday noon, one of the
three ideas is chosen at random and written anyway. A random pick is fairer than always taking the
first idea, and fixing that choice per plan means a retry can't pick a different one.

The Saturday safety net does the same for feedback. A family that skipped the check-in still gets
outlines, built from what the system already knows.

## Why every step is idempotent

The scheduler is a tick every few minutes, not a precise alarm. A tick can arrive late, twice, or
after the server restarts. Each action therefore compares against the start of its window and
carries a key such as `author:{plan}:{option}`, so repeating it changes nothing. The same is true
for jobs: a worker can die halfway through one, and the job runs again from the start. Handlers
are written so that running twice is safe.

That choice is why a slower tick only delays a notice. It never doubles one, and it never skips a
week.

## Why jobs are queued rather than run inline

Authoring takes minutes and calls a paid model. If it ran inside a web request, a closed browser
tab would cancel it and a timeout would waste the money. Instead the web app and the scheduler put
a job on a queue in the same SQLite file, and a separate worker process runs it with a lease and
heartbeats. Failures retry with backoff. A job that fails every attempt is set aside as *dead*:
kept for a person to look at, never silently dropped.

## Why the loop has an off switch and a console

`LOOP_JOBS_ENABLED` is a break-glass switch. With it off, nothing is planned or queued and no model
is called. That's the state to fall back to when spend or behaviour looks wrong.

The loop console at `/loop` is always on. It shows each child's week as the six steps, with a button
for each step, and it can only do what the loop itself could do. Testing with it can't put a week
in a state the real schedule would never produce. It's also where a written week gets checked
before anyone prints it: **Review this week** reports reading levels, word counts and skill
coverage, without calling a model.

## What's not there yet

Notices are still a stub that only logs, so no parent is emailed yet. Dead-job email is built but
off until a mail relay is configured.

Facts and numbers: [Worker and scheduler reference](../reference/worker-and-scheduler.md).
Turning it on: [Run the worker](../how-to/run-the-worker.md).
