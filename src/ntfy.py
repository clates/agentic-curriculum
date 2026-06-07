import logging
import requests

logger = logging.getLogger(__name__)

NTFY_URL = "http://100.97.236.69:2586/homeschool"


def notify(title: str, message: str, priority: str = "default") -> None:
    """POST a push notification to the NTFY homeschool topic.

    Swallows all errors — a failed push must never crash the caller.
    """
    try:
        resp = requests.post(
            NTFY_URL,
            headers={"Title": title, "Priority": priority},
            data=message,
            timeout=5,
        )
        if resp.status_code >= 400:
            logger.warning("ntfy push returned %s for title=%r", resp.status_code, title)
    except Exception as exc:
        logger.warning("ntfy push failed for title=%r: %s", title, exc)
