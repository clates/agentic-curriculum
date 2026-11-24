"""The loop console's API (``/loop-admin/*``): see where each child's week is, and push it a step.

The weekly loop has six steps, and two actors:

    Feedback (parent) -> Feed forward (system) -> Outlines (system) -> Pick (parent)
        -> Author (system) -> Print (parent)

Every action here goes through the same code the real loop uses (``loop_state.advance``, the pick
service, the job queue), so forcing a step cannot reach a state the loop could not. Nothing here
moves a plan backwards: to start over, reset the child's weeks. The console works whether or not
``LOOP_JOBS_ENABLED`` is set: it queues jobs itself, and the worker runs them either way.

The routes sit behind the global login gate like every other route.
"""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import date, timedelta
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from . import jobs, loop_integration, loop_state, pick_service, print_week, week_plan as wp  # type: ignore
    from . import week_review  # type: ignore
    from .candidate_selector import NoCandidates, load_candidate_inputs, select_week_standards  # type: ignore
    from .db_utils import get_db_path  # type: ignore
    from .model_context import build_model_context  # type: ignore
except ImportError:
    import jobs  # type: ignore
    import loop_integration  # type: ignore
    import loop_state  # type: ignore
    import pick_service  # type: ignore
    import print_week  # type: ignore
    import week_plan as wp  # type: ignore
    import week_review  # type: ignore
    from candidate_selector import NoCandidates, load_candidate_inputs, select_week_standards  # type: ignore
    from db_utils import get_db_path  # type: ignore
    from model_context import build_model_context  # type: ignore

FAMILY = loop_integration.LOCAL_FAMILY_ID
router = APIRouter(prefix="/loop-admin", tags=["loop-admin"])

# (key, label, who does it)
STEPS = (
    ("feedback", "Feedback", "parent"),
    ("feed_forward", "Feed forward", "system"),
    ("outlines", "Outlines", "system"),
    ("pick", "Pick", "parent"),
    ("author", "Author", "system"),
    ("print", "Print", "parent"),
)
# The step each plan status is working on. Steps before it are done, steps after it are to do.
_CURRENT = {
    "awaiting_feedback": "feedback",
    "outlining": "outlines",
    "awaiting_pick": "pick",
    "expired": "pick",
    "authoring": "author",
    "ready": "print",
}


class ActionBody(BaseModel):
    option: Literal["a", "b", "c"] | None = None
    week: str | None = None  # Monday, YYYY-MM-DD


class _NoCap:
    """Fresh ideas as often as the operator asks (the parent-facing cap does not apply here)."""

    def max_regenerations(self, family_id: str) -> int:
        return 10_000


def _open() -> sqlite3.Connection:
    conn = jobs.connect(get_db_path())
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _refuse(status: int, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"message": message})


def _meta(blob: str | None) -> dict[str, Any]:
    try:
        return json.loads(blob or "{}") or {}
    except ValueError:
        return {}


def _steps(status: str | None) -> list[dict[str, str]]:
    keys = [k for k, _, _ in STEPS]
    here = keys.index(_CURRENT[status]) if status in _CURRENT else (len(keys) if status else -1)
    out = []
    for i, (key, label, actor) in enumerate(STEPS):
        state = "done" if i < here else "current" if i == here else "todo"
        if state == "current" and status == "expired":
            state = "expired"
        out.append({"key": key, "label": label, "actor": actor, "state": state})
    return out


def _action(action_id: str, label: str, enabled: bool, why: str = "") -> dict[str, Any]:
    return {"id": action_id, "label": label, "enabled": enabled, "why_not": "" if enabled else why}


def _actions(plan: wp.WeekPlan | None) -> list[dict[str, Any]]:
    status = plan.status if plan else None
    return [
        _action("new_week", "Start a new week", True),
        _action(
            "skip_checkin",
            "Skip check-in",
            status == "awaiting_feedback",
            "Only while the week waits for a check-in.",
        ),
        _action(
            "generate_ideas",
            "Fresh ideas" if status in ("awaiting_pick", "expired") else "Generate ideas",
            status in ("outlining", "awaiting_pick", "expired"),
            "Needs a week that is past the check-in and not yet picked.",
        ),
        _action("pick", "Pick", status == "awaiting_pick", "Only while the ideas are open."),
        _action(
            "author_now",
            "Author now",
            status == "authoring",
            "Only after an idea is picked and before the week is ready.",
        ),
        _action("mark_printed", "Mark printed", status == "ready", "Only once the week is ready."),
        _action("reset_weeks", "Reset this child's weeks", plan is not None, "No weeks yet."),
    ]


def _plan_jobs(conn: sqlite3.Connection, plan_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT id, kind, state, attempts, max_attempts, last_error, run_after FROM jobs "
        "WHERE family_id=? AND (idempotency_key LIKE ? OR idempotency_key LIKE ?) "
        "ORDER BY id DESC LIMIT 6",
        (FAMILY, f"outlines:{plan_id}%", f"author:{plan_id}:%"),
    ).fetchall()
    return [
        {
            "id": r[0],
            "kind": r[1],
            "state": r[2],
            "attempts": r[3],
            "max_attempts": r[4],
            "last_error": (r[5] or "")[:300] or None,
            "run_after": r[6],
        }
        for r in rows
    ]


def _skill_info(conn: sqlite3.Connection, ids) -> dict[str, dict[str, str]]:
    """Standard id -> {subject, description}, for showing which skills an idea or a week carries."""
    ids = list(dict.fromkeys(ids))
    if not ids:
        return {}
    marks = ",".join("?" * len(ids))
    try:
        rows = conn.execute(
            f"SELECT standard_id, subject, description FROM standards WHERE standard_id IN ({marks})",  # noqa: S608
            ids,
        ).fetchall()
    except sqlite3.OperationalError:
        return {}
    return {r[0]: {"subject": r[1] or "", "description": r[2] or ""} for r in rows}


def _idea(o, info: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "option_id": o.option_id,
        "title": o.title,
        "hook": o.hook,
        "topic": o.topic,
        "activities": getattr(o, "activities", None),
        "effort": getattr(o, "effort", None),
        "skill_names": list(getattr(o, "skills", None) or []),
        "skills": [
            {
                "id": s,
                "subject": info.get(s, {}).get("subject", ""),
                "description": info.get(s, {}).get("description", ""),
            }
            for s in o.standard_ids
        ],
    }


def _plan_view(conn: sqlite3.Connection, plan: wp.WeekPlan) -> dict[str, Any]:
    options = plan.outlines.options if plan.outlines else []
    info = _skill_info(conn, [s for o in options for s in o.standard_ids])
    return {
        "plan_id": plan.plan_id,
        "week_start": plan.week_start,
        "status": plan.status,
        "picked_option": plan.picked_option,
        "packet_id": plan.packet_id,
        "needs_attention": plan.needs_attention,
        "pick_deadline": plan.pick_deadline,
        "outlines": [_idea(o, info) for o in options],
        "jobs": _plan_jobs(conn, plan.plan_id),
    }


def _grade(conn: sqlite3.Connection, student_id: str) -> int | None:
    """The grade the engine and the author use (from the profile, the last week, or the birthday)."""
    row = conn.execute(
        "SELECT metadata_blob, plan_rules_blob FROM student_profiles WHERE family_id=? AND student_id=?",
        (FAMILY, student_id),
    ).fetchone()
    if row is None:
        return None
    try:
        return build_model_context(
            row[0],
            row[1],
            fallback_grade=pick_service._latest_packet_grade(conn, FAMILY, student_id),
        ).grade
    except Exception:  # an incomplete profile: show no grade rather than fail the page
        return None


def _weeks(conn: sqlite3.Connection, student_id: str, limit: int = 6) -> list[dict[str, Any]]:
    """The child's recent weeks, newest first, so an earlier week can still be reviewed."""
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM week_plan WHERE family_id=? AND student_id=? ORDER BY week_start DESC LIMIT ?",
        (FAMILY, student_id, limit),
    ).fetchall()
    out = []
    for r in rows:
        p = wp.row_to_plan(r)
        picked = None
        if p.outlines and p.picked_option:
            try:
                picked = p.outlines.get(p.picked_option).title
            except KeyError:
                picked = None
        out.append(
            {
                "plan_id": p.plan_id,
                "week_start": p.week_start,
                "status": p.status,
                "picked_title": picked,
                "packet_id": p.packet_id,
            }
        )
    return out


def _child(conn: sqlite3.Connection, student_id: str, metadata_blob: str | None) -> dict[str, Any]:
    meta = _meta(metadata_blob)
    plan = wp.latest_plan_for_student(conn, FAMILY, student_id)
    return {
        "student_id": student_id,
        "name": (meta.get("name") or student_id).split()[0],
        "grade": _grade(conn, student_id),
        "demo": student_id == loop_integration.DEMO_STUDENT,
        "plan": _plan_view(conn, plan) if plan else None,
        "weeks": _weeks(conn, student_id),
        "steps": _steps(plan.status if plan else None),
        "actions": _actions(plan),
    }


def _child_row(conn: sqlite3.Connection, student_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT metadata_blob FROM student_profiles WHERE family_id=? AND student_id=?",
        (FAMILY, student_id),
    ).fetchone()
    if row is None:
        raise _refuse(404, "No such child.")
    return _child(conn, student_id, row[0])


def _queue(conn: sqlite3.Connection) -> dict[str, Any]:
    st = jobs.status(conn)
    waited = None
    if st["oldest_ready_run_after"]:
        waited = round(
            (jobs.utcnow() - jobs.parse_iso(st["oldest_ready_run_after"])).total_seconds()
        )
    return {
        "counts": st["counts"],
        "ready_now": st["ready_now"],
        "running": st["running"],
        "oldest_ready_wait_s": waited,
        # work is waiting, nothing is running and it has waited a while: the worker may be down
        "worker_may_be_down": bool(st["ready_now"] and not st["running"] and (waited or 0) > 90),
        "dead": [{**d, "last_error": (d["last_error"] or "")[:300]} for d in st["dead"]],
    }


@router.get("/overview")
def overview():
    conn = _open()
    try:
        rows = conn.execute(
            "SELECT student_id, metadata_blob FROM student_profiles WHERE family_id=? "
            "ORDER BY student_id",
            (FAMILY,),
        ).fetchall()
        return {
            "loop_switch": loop_integration.enabled(),
            "children": [_child(conn, sid, blob) for sid, blob in rows],
            "queue": _queue(conn),
        }
    finally:
        conn.close()


@router.get("/students/{student_id}/feed-forward")
def feed_forward(student_id: str, week: str | None = None):
    """What the engine would pick for this child's next week, from mastery alone. No model call."""
    conn = _open()
    try:
        try:
            student = pick_service.get_student(conn, FAMILY, student_id)
        except pick_service.PickError as exc:
            raise _refuse(exc.status, exc.message) from exc
        latest = wp.latest_plan_for_student(conn, FAMILY, student_id)
        week_start = week or (latest.week_start if latest else _next_monday(None))
        context = build_model_context(
            student.metadata_blob,
            student.plan_rules_blob,
            fallback_grade=pick_service._latest_packet_grade(conn, FAMILY, student_id),
        )
        progress = _meta(student.progress_blob)
        known = {
            "mastered": len(progress.get("mastered_standards") or []),
            "developing": len(progress.get("developing_standards") or []),
            "rated": len(progress.get("standard_metadata") or {}),
        }
        standards, prereqs = load_candidate_inputs(get_db_path(), context.grade)
        try:
            chosen = select_week_standards(
                progress=student.progress_blob,
                standards=standards,
                prereqs=prereqs,
                grade=context.grade,
                seed=f"{student_id}:{week_start}",  # the same seed the outline step uses
            )
        except NoCandidates:
            return {"week_start": week_start, "grade": context.grade, "known": known, "skills": []}
        return {
            "week_start": week_start,
            "grade": context.grade,
            "known": known,
            "skills": [
                {
                    "standard_id": c.standard_id,
                    "subject": c.subject,
                    "grade": c.grade,
                    "description": c.description,
                    "reason": c.reason,
                }
                for c in chosen.items
            ],
        }
    finally:
        conn.close()


def _run_record(packet_id: str) -> dict[str, Any] | None:
    """The authoring run record saved next to the week (cost, model, rewrites), if there is one."""
    import json as _json
    import os as _os

    try:
        from authoring.pipeline import _runs_dir  # type: ignore
    except ImportError:  # pragma: no cover - package-relative import in some contexts
        from .authoring.pipeline import _runs_dir  # type: ignore
    name = _os.path.basename(packet_id)  # never a path from the request
    path = _os.path.join(_runs_dir(), f"{name}.json")
    try:
        with open(path, encoding="utf-8") as f:
            return _json.load(f)
    except (OSError, ValueError):
        return None


@router.get("/students/{student_id}/weeks/{plan_id}/review")
def review(student_id: str, plan_id: str):
    """Is this week well formed and well curated? Facts and flags from the saved week, no model call."""
    conn = _open()
    try:
        _child_row(conn, student_id)
        try:
            plan = wp.get_plan(conn, FAMILY, plan_id)
        except wp.PlanNotFound as exc:
            raise _refuse(404, "No such week.") from exc
        if plan.student_id != student_id:
            raise _refuse(404, "No such week.")
        if not plan.packet_id:
            raise _refuse(409, "This week has not been written yet.")
        import week_store  # at call time: it snapshots the database path when imported

        week = week_store.get_week(student_id, plan.packet_id, family_id=FAMILY)
        if week is None:
            raise _refuse(404, "The written week could not be found.")
        planned = []
        if plan.outlines and plan.picked_option:
            try:
                planned = list(plan.outlines.get(plan.picked_option).standard_ids)
            except KeyError:
                planned = []
        ids = planned + [s for d in week.days for s in d.standards]
        result = week_review.review_week(
            week,
            grade=_grade(conn, student_id) or 0,
            skills=_skill_info(conn, ids),
            planned=planned,
            run=_run_record(plan.packet_id),
        ).to_dict()
        base = f"/api/students/{student_id}/weekly-packets/{plan.packet_id}/print?doc="
        result.update(
            plan_id=plan.plan_id,
            week_start=plan.week_start,
            status=plan.status,
            packet_id=plan.packet_id,
            documents=[
                {"doc": d, "label": label, "url": base + d}
                for d, label in (
                    ("packet", "Student packet"),
                    ("guide", "Teacher guide"),
                    ("prep", "Prep sheet"),
                )
            ],
        )
        return result
    finally:
        conn.close()


def _next_monday(latest_week: str | None) -> str:
    today = date.today()
    nxt = today + timedelta(days=7 - today.weekday())
    if latest_week and date.fromisoformat(latest_week) >= nxt:
        nxt = date.fromisoformat(latest_week) + timedelta(days=7)
    return nxt.isoformat()


def _ensure_job_runs(conn: sqlite3.Connection, job: jobs.Job) -> None:
    """A job that gave up is put back in the queue; one already waiting or running is left alone."""
    if job.state == "dead":
        jobs.retry_dead(conn, job.id)


def _require(plan: wp.WeekPlan | None, *statuses: str) -> wp.WeekPlan:
    if plan is None:
        raise _refuse(409, "This child has no week yet. Start a new week first.")
    if plan.status not in statuses:
        raise _refuse(409, f"Not possible while the week is “{plan.status}”.")
    return plan


@router.post("/students/{student_id}/actions/{action}")
def act(student_id: str, action: str, body: ActionBody | None = None):
    body = body or ActionBody()
    conn = _open()
    try:
        _child_row(conn, student_id)  # 404 for an unknown child
        plan = wp.latest_plan_for_student(conn, FAMILY, student_id)
        try:
            _run(conn, student_id, plan, action, body)
        except pick_service.PickError as exc:
            raise _refuse(exc.status, exc.message) from exc
        except loop_state.IllegalTransition as exc:
            raise _refuse(409, str(exc)) from exc
        except print_week.PlanNotReady as exc:
            raise _refuse(409, f"Not possible while the week is “{exc.status}”.") from exc
        return {"child": _child_row(conn, student_id)}
    finally:
        conn.close()


def _run(conn, student_id: str, plan: wp.WeekPlan | None, action: str, body: ActionBody) -> None:
    if action == "new_week":
        week = body.week or _next_monday(plan.week_start if plan else None)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", week) or date.fromisoformat(week).weekday() != 0:
            raise _refuse(422, "A week starts on a Monday (YYYY-MM-DD).")
        exists = conn.execute(
            "SELECT 1 FROM week_plan WHERE family_id=? AND student_id=? AND week_start=?",
            (FAMILY, student_id, week),
        ).fetchone()
        if exists:
            raise _refuse(409, f"There is already a week starting {week}.")
        wp.create_plan(conn, FAMILY, student_id, week)
    elif action == "skip_checkin":
        plan = _require(plan, "awaiting_feedback")
        res = loop_state.advance(
            conn,
            FAMILY,
            plan.plan_id,
            loop_state.Event("feedback_submitted", key=f"console:{plan.plan_id}"),
        )
        loop_integration.enqueue_outline(conn, FAMILY, res.plan.plan_id)
    elif action == "generate_ideas":
        plan = _require(plan, "outlining", "awaiting_pick", "expired")
        if plan.status == "outlining":  # the job exists or is missing: make sure it is queued
            _ensure_job_runs(conn, loop_integration.enqueue_outline(conn, FAMILY, plan.plan_id))
        else:  # fresh ideas now, in this request (a model call, so it can take a while)
            from llm import LLMError

            try:
                pick_service.regenerate(conn, FAMILY, student_id, plan.plan_id, limits=_NoCap())
            except LLMError as exc:
                raise _refuse(502, "The model could not write ideas just now. Try again.") from exc
    elif action == "pick":
        plan = _require(plan, "awaiting_pick")
        if body.option is None:
            raise _refuse(422, "Say which idea: a, b or c.")
        pick_service.pick(conn, FAMILY, student_id, body.option, plan.plan_id)
        loop_integration.enqueue_author(conn, FAMILY, plan.plan_id, body.option)
    elif action == "author_now":
        plan = _require(plan, "authoring")
        _ensure_job_runs(
            conn, loop_integration.enqueue_author(conn, FAMILY, plan.plan_id, plan.picked_option)
        )
    elif action == "mark_printed":
        plan = _require(plan, "ready")
        print_week.mark_printed(conn, FAMILY, student_id, plan.plan_id)
    elif action == "reset_weeks":
        _reset(conn, student_id)
    else:
        raise _refuse(404, "Unknown action.")


def _reset(conn: sqlite3.Connection, student_id: str) -> None:
    """Throw away this child's weeks and the jobs for them (loop events go with each plan). The
    child, their progress and any saved packets stay. For testing."""
    plan_ids = [
        r[0]
        for r in conn.execute(
            "SELECT plan_id FROM week_plan WHERE family_id=? AND student_id=?", (FAMILY, student_id)
        )
    ]
    for pid in plan_ids:
        conn.execute(
            "DELETE FROM jobs WHERE family_id=? AND (idempotency_key LIKE ? OR idempotency_key LIKE ?)",
            (FAMILY, f"outlines:{pid}%", f"author:{pid}:%"),
        )
    conn.execute("DELETE FROM week_plan WHERE family_id=? AND student_id=?", (FAMILY, student_id))
    conn.commit()


@router.post("/seed-demo")
def seed_demo():
    conn = _open()
    try:
        sid = loop_integration.seed_demo(conn)
        return {"child": _child_row(conn, sid)}
    finally:
        conn.close()


@router.post("/jobs/{job_id}/retry")
def retry_job(job_id: int):
    conn = _open()
    try:
        job = jobs.get_job(conn, job_id)
        if job is None or job.family_id != FAMILY:
            raise _refuse(404, "No such job.")
        if not jobs.retry_dead(conn, job_id):
            raise _refuse(409, "Only a job that gave up can be retried.")
        return {"queue": _queue(conn)}
    finally:
        conn.close()
