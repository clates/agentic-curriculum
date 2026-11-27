"""Outgoing email: SMTP in production, a JSON-lines outbox file in dev and tests.

Env: SMTP_HOST, SMTP_PORT (587 STARTTLS; 465 implicit TLS), SMTP_USER, SMTP_PASSWORD, SMTP_FROM
(default SMTP_USER, then the caller's ``fallback_from`` if it gave one; with none of them,
sending over SMTP raises MailError), MAILER_OUTBOX (path; every
message is appended as one JSON line). With neither SMTP_HOST nor MAILER_OUTBOX set, nothing is
sent. Mail goes only to the given recipients. The password and message bodies are never logged.
"""

from __future__ import annotations

import json
import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class MailError(Exception):
    """The mail transport failed. The message never contains credentials."""


def enabled() -> bool:
    return bool(os.environ.get("SMTP_HOST", "").strip())


def send(to: str | list[str], subject: str, body: str, fallback_from: str | None = None) -> None:
    recipients = [to] if isinstance(to, str) else list(to)
    outbox = os.environ.get("MAILER_OUTBOX", "").strip()
    if outbox:
        with open(outbox, "a", encoding="utf-8") as f:
            f.write(json.dumps({"to": recipients, "subject": subject, "body": body}) + "\n")
    if not enabled():
        if not outbox:
            logger.warning("mail not sent: no SMTP_HOST (subject: %s)", subject)
        return
    host = os.environ["SMTP_HOST"].strip()
    port = int(os.environ.get("SMTP_PORT", "587") or 587)
    user = os.environ.get("SMTP_USER", "").strip()
    sender = os.environ.get("SMTP_FROM", "").strip() or user or (fallback_from or "").strip()
    if not sender:
        raise MailError("mail not sent: set SMTP_FROM or SMTP_USER")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)
    context = ssl.create_default_context()
    try:
        if port == 465:
            server: smtplib.SMTP = smtplib.SMTP_SSL(host, port, timeout=15, context=context)
        else:
            server = smtplib.SMTP(host, port, timeout=15)
        with server:
            if port != 465:
                server.starttls(context=context)
            if user:
                server.login(user, os.environ.get("SMTP_PASSWORD", ""))
            server.send_message(msg, to_addrs=recipients)
    except (smtplib.SMTPException, OSError) as exc:
        raise MailError(f"mail transport failed: {type(exc).__name__}") from None
