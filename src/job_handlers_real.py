"""The real ``outline`` and ``author`` handlers. Load with WORKER_HANDLER_MODULES=job_handlers_real.

Both are idempotent, because a job can run twice (a retry, a reclaimed lease, a second scheduler):
a plan that has moved on makes the job a no-op, and the week's packet id is fixed per plan so a
re-run replaces the saved week instead of adding a second one.
"""

from __future__ import annotations

import logging

try:
    from . import loop_state, pick_service, week_plan as wp, week_store  # type: ignore
    from .authoring import Tenant, author_week  # type: ignore
    from .job_registry import JobContext, handler  # type: ignore
    from .model_context import build_model_context  # type: ignore
except ImportError:
    import loop_state  # type: ignore
    import pick_service  # type: ignore
    import week_plan as wp  # type: ignore
    import week_store  # type: ignore
    from authoring import Tenant, author_week  # type: ignore
    from job_registry import JobContext, handler  # type: ignore
    from model_context import build_model_context  # type: ignore

logger = logging.getLogger(__name__)


class AuthoringFailed(RuntimeError):
    """The week did not come out valid or did not save. The text is the status code only: the
    validation errors can quote the child's lesson content, so they stay in the run record."""


def _llm_client():
    """The model client. None = the app's default (OpenRouter from env). Tests replace this."""
    return None


def author_context(ctx) -> dict:
    """The outline side and the author side each have their own student-context type. This hands
    the author only the five allowlisted fields; a missing reading level falls back to the grade."""
    return {
        "first_name": ctx.first_name,
        "grade": ctx.grade,
        "reading_level": ctx.reading_level or f"grade {ctx.grade_label}",
        "interests": list(ctx.interests),
        "parent_notes": ctx.parent_notes or "",
    }


def packet_id_for(plan_id: str) -> str:
    return f"pk_{plan_id}"


@handler("outline")
def outline(ctx: JobContext) -> None:
    """Write the three ideas for a plan that is outlining, and move it to awaiting_pick."""
    conn = ctx.connect()
    try:
        plan = pick_service.finish_outlining(
            conn, ctx.job.family_id, ctx.job.payload["plan_id"], client=_llm_client()
        )
        logger.info("outline job %s: plan is now %s", ctx.job.id, plan.status)
    finally:
        conn.close()


@handler("author")
def author(ctx: JobContext) -> None:
    """Write, validate and save the week for a picked idea, and move the plan to ready."""
    family_id = ctx.job.family_id
    plan_id, option = ctx.job.payload["plan_id"], ctx.job.payload["option_id"]
    conn = ctx.connect()
    try:
        plan = wp.get_plan(conn, family_id, plan_id)
        if plan.status != "authoring" or plan.picked_option != option or plan.outlines is None:
            logger.info("author job %s: plan is %s, nothing to do", ctx.job.id, plan.status)
            return
        packet_id = packet_id_for(plan_id)
        if week_store.get_week(plan.student_id, packet_id, family_id=family_id) is None:
            student = pick_service.get_student(conn, family_id, plan.student_id)
            model_ctx = build_model_context(
                student.metadata_blob,
                student.plan_rules_blob,
                fallback_grade=pick_service._latest_packet_grade(conn, family_id, plan.student_id),
            )
            idea = plan.outlines.get(option)
            result = author_week(
                Tenant(family_id=family_id),
                author_context(model_ctx),
                pick_service._topic_text(idea),
                list(idea.standard_ids),
                student_id=plan.student_id,
                packet_id=packet_id,
                week_of=plan.week_start,
                client=_llm_client(),
                db_path=ctx.db_path,
            )
            if not (result.ok and result.saved):
                raise AuthoringFailed(result.status)
        res = loop_state.advance(
            conn,
            family_id,
            plan_id,
            loop_state.Event(
                "authoring_done", key=f"authored:{plan_id}", payload={"packet_id": packet_id}
            ),
        )
        logger.info("author job %s: plan is now %s", ctx.job.id, res.plan.status)
    finally:
        conn.close()
