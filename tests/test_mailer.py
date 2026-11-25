"""The mailer: outbox file, no-SMTP no-op, SMTP transport (faked), and error hygiene."""

import json
import logging
import smtplib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import mailer  # noqa: E402


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for k in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "MAILER_OUTBOX"):
        monkeypatch.delenv(k, raising=False)


class FakeSMTP:
    instances: list = []

    def __init__(self, host, port, timeout=None):
        self.host, self.port, self.calls, self.msg = host, port, [], None
        FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def starttls(self, context=None):
        self.calls.append("starttls")

    def login(self, user, password):
        self.calls.append(("login", user))
        if password == "bad":
            raise smtplib.SMTPAuthenticationError(535, b"nope " + password.encode())

    def send_message(self, msg):
        self.msg = msg


def test_outbox_gets_one_json_line_per_message(monkeypatch, tmp_path):
    box = tmp_path / "out.jsonl"
    monkeypatch.setenv("MAILER_OUTBOX", str(box))
    mailer.send("a@x.com", "S1", "B1")
    mailer.send(["b@x.com", "c@x.com"], "S2", "B2")
    lines = [json.loads(line) for line in box.read_text().splitlines()]
    assert lines == [
        {"to": ["a@x.com"], "subject": "S1", "body": "B1"},
        {"to": ["b@x.com", "c@x.com"], "subject": "S2", "body": "B2"},
    ]


def test_no_smtp_and_no_outbox_logs_subject_only(caplog):
    assert not mailer.enabled()
    with caplog.at_level(logging.INFO):
        mailer.send("a@x.com", "Hello subject", "secret body 123456")
    assert "mail not sent: no SMTP_HOST" in caplog.text
    assert "Hello subject" in caplog.text
    assert "secret body" not in caplog.text


def test_smtp_uses_from_starttls_and_login(monkeypatch):
    FakeSMTP.instances.clear()
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USER", "user@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "pw")
    monkeypatch.setenv("SMTP_FROM", "Family <noreply@example.com>")
    assert mailer.enabled()
    mailer.send("a@x.com", "Subj", "Body")
    s = FakeSMTP.instances[0]
    assert (s.host, s.port) == ("smtp.example.com", 587)
    assert s.calls == ["starttls", ("login", "user@example.com")]
    assert s.msg["From"] == "Family <noreply@example.com>"
    assert s.msg["To"] == "a@x.com"
    assert s.msg["Subject"] == "Subj"


def test_transport_failure_raises_mailerror_without_password(monkeypatch):
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USER", "u")
    monkeypatch.setenv("SMTP_PASSWORD", "bad")
    with pytest.raises(mailer.MailError) as ei:
        mailer.send("a@x.com", "S", "B")
    assert "bad" not in str(ei.value)
    assert ei.value.__cause__ is None
