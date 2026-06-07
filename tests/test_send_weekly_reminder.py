import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import send_weekly_reminder


def _make_student(sid: str, name: str) -> dict:
    return {
        "student_id": sid,
        "progress_blob": json.dumps({}),
        "plan_rules_blob": json.dumps({}),
        "metadata_blob": json.dumps({"name": name}),
    }


def test_sends_reminder_listing_student_names():
    students = [_make_student("s1", "Christopher"), _make_student("s2", "Theodore")]

    with (
        patch("send_weekly_reminder.list_students", return_value=students),
        patch("send_weekly_reminder.notify") as mock_notify,
    ):
        send_weekly_reminder.send_reminder()

    mock_notify.assert_called_once()
    message = mock_notify.call_args[0][1]
    assert "Christopher" in message
    assert "Theodore" in message


def test_sends_reminder_with_no_students():
    with (
        patch("send_weekly_reminder.list_students", return_value=[]),
        patch("send_weekly_reminder.notify") as mock_notify,
    ):
        send_weekly_reminder.send_reminder()

    mock_notify.assert_called_once()


def test_does_not_raise_on_ntfy_failure():
    with (
        patch("send_weekly_reminder.list_students", return_value=[]),
        patch("send_weekly_reminder.notify", side_effect=Exception("network down")),
    ):
        # Should not raise — reminder failure is non-fatal
        send_weekly_reminder.send_reminder()
