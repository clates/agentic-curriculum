import logging
import os

import requests

logger = logging.getLogger(__name__)

DEFAULT_NTFY_URL = "http://100.97.236.69:2586/homeschool"


def get_ntfy_url() -> str:
    """Return the push endpoint, read from NTFY_URL at call time.

    Unset -> the production default. Set to an empty string -> push disabled (log only).
    Tests and the E2E suite always point this at a local address, never the real topic.
    """
    return os.environ.get("NTFY_URL", DEFAULT_NTFY_URL)


def notify(title: str, message: str, priority: str = "default") -> None:
    """POST a push notification to the NTFY homeschool topic.

    Swallows all errors — a failed push must never crash the caller.
    """
    url = get_ntfy_url()
    if not url:
        logger.info("ntfy push disabled (NTFY_URL empty): title=%r message=%r", title, message)
        return
    try:
        resp = requests.post(
            url,
            headers={"Title": title, "Priority": priority},
            data=message,
            timeout=5,
        )
        if resp.status_code >= 400:
            logger.warning("ntfy push returned %s for title=%r", resp.status_code, title)
    except Exception as exc:
        logger.warning("ntfy push failed for title=%r: %s", title, exc)
