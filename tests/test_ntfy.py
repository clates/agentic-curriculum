import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ntfy


def test_notify_posts_to_correct_url():
    with patch("ntfy.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        ntfy.notify("Test Title", "Test message")
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert call_kwargs[0][0] == "http://100.97.236.69:2586/homeschool"
        assert call_kwargs[1]["headers"]["Title"] == "Test Title"
        assert call_kwargs[1]["data"] == "Test message"
        assert call_kwargs[1]["headers"]["Priority"] == "default"


def test_notify_uses_custom_priority():
    with patch("ntfy.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        ntfy.notify("Urgent", "Something broke", priority="high")
        assert mock_post.call_args[1]["headers"]["Priority"] == "high"


def test_notify_swallows_network_errors(caplog):
    import logging

    with patch("ntfy.requests.post", side_effect=Exception("timeout")):
        with caplog.at_level(logging.WARNING, logger="ntfy"):
            ntfy.notify("Fail", "This will fail silently")
    # Should not raise; warning should be logged
    assert any("timeout" in r.message for r in caplog.records)


def test_notify_swallows_bad_status(caplog):
    import logging

    with patch("ntfy.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=403)
        with caplog.at_level(logging.WARNING, logger="ntfy"):
            ntfy.notify("Fail", "403 from server")
    assert any("403" in r.message for r in caplog.records)
