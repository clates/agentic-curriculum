"""Keep API keys out of logs and error text.

``redact`` replaces the configured keys and anything shaped like an OpenRouter/OpenAI key or a
Bearer token. ``install_log_redaction`` wraps the logging record factory so EVERY log record
(ours, openai's, httpx's, uvicorn's) is scrubbed, including formatted tracebacks.
"""

from __future__ import annotations

import logging
import os
import re

REDACTED = "[redacted]"
_PATTERNS = [
    re.compile(r"sk-(?:or-)?[A-Za-z0-9_\-]{12,}"),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-]{12,}"),
]
_SECRET_ENV = ("OPENROUTER_API_KEY", "OPENAI_API_KEY")
_installed = False


def _known_secrets() -> list[str]:
    return [v for name in _SECRET_ENV if len(v := os.environ.get(name, "")) >= 8]


def redact(text: str) -> str:
    for secret in _known_secrets():
        text = text.replace(secret, REDACTED)
    text = _PATTERNS[0].sub(REDACTED, text)
    return _PATTERNS[1].sub(lambda m: m.group(1) + REDACTED, text)


def install_log_redaction() -> None:
    """Idempotent. Safe to call from any entry point."""
    global _installed
    if _installed:
        return
    previous = logging.getLogRecordFactory()

    def factory(*args, **kwargs):
        record = previous(*args, **kwargs)
        try:
            message = record.getMessage()
            clean = redact(message)
            if clean != message:
                record.msg, record.args = clean, None
            if record.exc_info and record.exc_info[0] is not None:
                trace = logging.Formatter().formatException(record.exc_info)
                record.exc_text = redact(trace)
        except Exception:  # logging must never raise
            pass
        return record

    logging.setLogRecordFactory(factory)
    _installed = True
