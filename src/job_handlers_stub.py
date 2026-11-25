"""STUB handlers for the job kinds the loop uses. They log and succeed; they do no real work.

Other streams replace them: the outline generator registers ``@handler("outline")`` and the week
author ``@handler("author")`` (non-stub registrations win over these). ``send_notice`` is replaced
by the email work (M8.5). Real handler modules are loaded by the worker from the
``WORKER_HANDLER_MODULES`` env var (comma-separated import paths).
"""

from __future__ import annotations

import logging

try:
    from .job_registry import JobContext, handler  # type: ignore
except ImportError:
    from job_registry import JobContext, handler  # type: ignore

logger = logging.getLogger(__name__)


def _stub(ctx: JobContext) -> None:
    logger.info(
        "STUB handler for %r ran (job=%s key=%s): nothing real was done",
        ctx.job.kind,
        ctx.job.id,
        ctx.job.idempotency_key,
    )


for _kind in ("outline", "author", "send_notice"):
    handler(_kind, stub=True)(_stub)
