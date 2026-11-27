"""Self-registration: invite code, emailed 6-digit code, verify, resend, and login while pending."""

from __future__ import annotations

import json
import logging
import re
import sys
import threading
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import db_utils  # noqa: E402
import mailer  # noqa: E402
from auth import clock, lockout, passwords, registration, service, store  # noqa: E402
from main import app  # noqa: E402
from migrations import apply_migrations  # noqa: E402

PW = "correct horse battery"
NEW = "a brand new password"
EMAIL = "ana@example.com"
CODE_RE = re.compile(r"\b(\d{6})\b")


class Clock:
    def __init__(self):
        self.t = 1_000_000.0

    def __call__(self):
        return self.t


@pytest.fixture(autouse=True)
def now(tmp_path, monkeypatch):
    db = tmp_path / "reg.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    monkeypatch.setattr(db_utils, "DB_FILE", str(db))
    monkeypatch.setenv("AUTH_REQUIRED", "1")
    monkeypatch.setenv("MAILER_OUTBOX", str(tmp_path / "outbox.jsonl"))
    for k in ("SMTP_HOST", "AUTH_BACKOFF_SCALE", "AUTH_ALLOWED_HOSTS"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(passwords, "CURRENT", passwords.ScryptParams(n=2**10, r=8, p=1))
    passwords._dummy.clear()
    monkeypatch.setattr(lockout, "_last_prune", float("-inf"))
    monkeypatch.setattr(service, "_slots", None)
    fake = Clock()
    clock.set_source(fake)
    send_later = registration.send_later  # still a real thread; joined so tests can read the mail
    monkeypatch.setattr(registration, "send_later", lambda *a: send_later(*a).join())
    apply_migrations(db)
    yield fake
    clock.set_source(None)


@pytest.fixture
def client():
    return TestClient(app)


def rows(sql, *args):
    conn = store.connect()
    try:
        return conn.execute(sql, args).fetchall()
    finally:
        conn.close()


def invite(days=14):
    conn = store.connect()
    try:
        return store.create_invite(conn, None, days)
    finally:
        conn.close()


def used(code):
    return (
        rows("SELECT used_at FROM invite WHERE code_hash=?", store.token_hash(code))[0][0]
        is not None
    )


def outbox():
    path = Path(mailer.os.environ["MAILER_OUTBOX"])
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def last_code(to=EMAIL):
    mine = [m for m in outbox() if m["to"] == [to]]
    return CODE_RE.search(mine[-1]["body"]).group(1)


def register(c, email=EMAIL, password=PW, family="The Anas", code=None):
    body = {"email": email, "password": password, "family_name": family}
    return c.post("/auth/register", json={**body, "invite_code": code or invite()})


def verify(c, code, email=EMAIL, password=PW):
    return c.post("/auth/verify", json={"email": email, "code": code, "password": password})


def wrong_for(code):
    return "000000" if code != "000000" else "111111"


def counts():
    return {
        "family": rows("SELECT COUNT(*) FROM family")[0][0],
        "user": rows("SELECT COUNT(*) FROM app_user")[0][0],
        "challenge": rows("SELECT COUNT(*) FROM auth_challenge")[0][0],
    }


# --- registering ---------------------------------------------------------------------------


def test_register_creates_a_family_an_unverified_user_and_mails_a_code(client):
    r = register(client, email="  Ana@Example.COM ")
    assert r.status_code == 202 and r.json() == {"status": "check_email"}
    assert "set-cookie" not in r.headers
    [(username, verified_at, family)] = rows(
        "SELECT u.username, u.email_verified_at, f.name FROM app_user u "
        "JOIN family f ON f.family_id = u.family_id"
    )
    assert (username, verified_at, family) == (EMAIL, None, "The Anas")
    [msg] = outbox()
    assert msg["to"] == [EMAIL] and msg["subject"] == "Your sign-in code"
    assert "15 minutes" in msg["body"] and "ignore" in msg["body"]
    code = last_code()
    assert rows("SELECT purpose, subject, code_hash FROM auth_challenge") == [
        ("verify_email", EMAIL, store.token_hash(code))
    ]
    assert rows("SELECT used_at IS NOT NULL FROM invite") == [(1,)]


def test_verify_signs_in(client):
    register(client)
    assert client.get("/auth/me").status_code == 401
    r = verify(client, last_code())
    assert r.status_code == 200 and r.json() == {"user": {"username": EMAIL}}
    me = client.get("/auth/me")
    assert me.status_code == 200 and me.json()["user"] == {"username": EMAIL}
    assert rows("SELECT email_verified_at IS NOT NULL FROM app_user") == [(1,)]


@pytest.mark.parametrize("kind", ["bad", "used", "expired"])
def test_a_bad_used_or_expired_invite_creates_nothing(client, now, kind):
    code = {"bad": "ABCDEFGHJK", "used": None, "expired": None}[kind]
    if kind == "used":
        code = invite()
        assert register(client, email="first@example.com", code=code).status_code == 202
    if kind == "expired":
        code = invite(days=1)
        now.t += 2 * 86400
    before, mail = counts(), len(outbox())
    r = register(client, code=code)
    assert r.status_code == 400 and r.json() == {"detail": "invalid_invite"}
    assert counts() == before and len(outbox()) == mail


@pytest.mark.parametrize(
    "field,value",
    [("email", "not-an-email"), ("email", "a" * 60 + "@x.com"), ("password", "short"),
     ("family", "   ")],
)  # fmt: skip
def test_bad_input_gets_a_plain_400(client, field, value):
    r = register(client, **{field: value})
    assert r.status_code == 400 and isinstance(r.json()["detail"], str)
    assert r.json()["detail"] != "invalid_invite"
    assert counts()["user"] == 0
    assert rows("SELECT COUNT(*) FROM invite WHERE used_at IS NOT NULL") == [(0,)]


def test_a_verified_email_registering_again_looks_the_same_and_creates_nothing(client):
    register(client)
    verify(client, last_code())
    before, mail = counts(), len(outbox())
    code = invite()
    r = register(TestClient(app), password="another long password", family="Imposters", code=code)
    assert r.status_code == 202 and r.json() == {"status": "check_email"}
    assert counts() == before and len(outbox()) == mail
    assert used(code)
    assert service.attempt_login(EMAIL, PW, "1.2.3.4").kind == "ok"  # password unchanged


def test_an_unverified_email_registering_again_replaces_the_pending_account(client, now):
    register(client)
    first = last_code()
    code = invite()
    r = register(client, password=NEW, family="Renamed", code=code)
    assert r.status_code == 202
    # fam_local + the pending family; the old code is kept (retired) to count toward the daily cap
    assert counts() == {"family": 2, "user": 1, "challenge": 2}
    assert rows("SELECT f.name FROM family f JOIN app_user u USING (family_id)") == [("Renamed",)]
    assert used(code)
    second = last_code()
    assert len(outbox()) == 2
    if first != second:
        assert verify(client, first, password=NEW).status_code == 400  # the old code is gone
    assert verify(client, second, password=NEW).status_code == 200
    assert service.attempt_login(EMAIL, NEW, "1.2.3.4").kind == "ok"


def test_operator_made_users_are_verified():
    conn = store.connect()
    try:
        assert store.create_user(conn, "ops", PW).verified
    finally:
        conn.close()
    assert rows("SELECT email_verified_at IS NOT NULL FROM app_user") == [(1,)]


def test_the_session_lookup_reads_the_verified_flag():
    conn = store.connect()
    try:
        made = store.insert_user(conn, "new@x.com", store.hash_password(PW), "fam_local", False)
        token = store.create_session(conn, made, None)
        assert store.resolve_session(conn, token)[0].verified is False
    finally:
        conn.close()


# --- code guessing ---------------------------------------------------------------------------


def test_five_wrong_codes_lock_the_challenge(client, now, monkeypatch):
    monkeypatch.setenv("AUTH_BACKOFF_SCALE", "0.001")  # keep the per-IP lockout out of the way
    register(client)
    code = last_code()
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(5):
        now.t += 1
        r = verify(client, wrong)
        assert r.status_code == 400 and r.json() == {"detail": "invalid_code"}
    now.t += 1
    assert verify(client, code).status_code == 400
    assert rows("SELECT email_verified_at FROM app_user") == [(None,)]


def test_a_code_signs_in_once_only(client):
    register(client)
    code = last_code()
    assert verify(client, code).status_code == 200
    r = verify(TestClient(app), code)
    assert r.status_code == 400 and "set-cookie" not in r.headers
    assert rows("SELECT COUNT(*) FROM auth_session") == [(1,)]


def test_a_code_expires_after_15_minutes(client, now):
    register(client)
    now.t += 15 * 60 + 1
    assert verify(client, last_code()).status_code == 400


def test_wrong_codes_from_one_ip_trigger_the_lockout(client):
    register(client)
    code = last_code()
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(lockout.FREE_FAILURES):
        assert verify(client, wrong).status_code == 400
    assert verify(client, wrong).status_code == 400  # counted, and now locked
    r = verify(client, code)
    assert r.status_code == 429 and r.json()["detail"] == "too_many_attempts"


def test_bad_invites_from_one_ip_trigger_the_lockout(client):
    for _ in range(lockout.FREE_FAILURES + 1):
        assert register(client, code="ABCDEFGHJK").status_code == 400
    r = register(client)  # a good invite, but this address is locked
    assert r.status_code == 429 and r.json()["detail"] == "too_many_attempts"
    assert counts()["user"] == 0


# --- resend ----------------------------------------------------------------------------------


def test_resend_is_at_most_once_a_minute_and_always_202(client, now):
    register(client)
    resend = lambda email=EMAIL: client.post("/auth/resend", json={"email": email})  # noqa: E731
    for email in (EMAIL, "nobody@example.com", "not an email"):
        r = resend(email)
        assert r.status_code == 202 and r.json() == {"status": "check_email"}
    assert len(outbox()) == 1  # too soon for EMAIL; nothing for the others
    now.t += 61
    assert resend().status_code == 202 and len(outbox()) == 2
    assert resend().status_code == 202 and len(outbox()) == 2
    assert verify(client, last_code()).status_code == 200
    now.t += 61
    assert resend().status_code == 202 and len(outbox()) == 2  # verified: nothing more is sent


# --- login while pending ---------------------------------------------------------------------


def test_login_to_an_unverified_account(client, now):
    register(client)
    login = lambda pw: client.post("/auth/login", json={"username": EMAIL, "password": pw})  # noqa
    r = login("wrong password here")
    assert r.status_code == 401 and r.json() == {"detail": "invalid_credentials"}
    r = login(PW)
    assert r.status_code == 403 and r.json() == {"detail": "email_not_verified"}
    assert "set-cookie" not in r.headers and len(outbox()) == 1  # within the resend limit
    now.t += 61
    assert login(PW).status_code == 403 and len(outbox()) == 2
    assert verify(client, last_code()).status_code == 200
    assert login(PW).status_code == 200


# --- mail failures and logs ------------------------------------------------------------------


def _broken_smtp(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.invalid")
    monkeypatch.setenv("SMTP_PORT", "not-a-port")  # int() raises ValueError, not MailError


def _outbox_is_a_directory(monkeypatch):
    monkeypatch.setenv("MAILER_OUTBOX", str(Path(mailer.os.environ["MAILER_OUTBOX"]).parent))


def _mail_error(monkeypatch):
    def boom(*a, **k):
        raise mailer.MailError("mail transport failed: SMTPException")

    monkeypatch.setattr(mailer, "send", boom)


@pytest.mark.parametrize("breakage", [_broken_smtp, _outbox_is_a_directory, _mail_error])
def test_a_failing_mail_transport_still_answers_202(client, monkeypatch, caplog, breakage):
    breakage(monkeypatch)
    code = invite()
    with caplog.at_level(logging.DEBUG):
        r = register(client, code=code)
    assert r.status_code == 202 and r.json() == {"status": "check_email"}
    assert rows("SELECT email_verified_at FROM app_user") == [(None,)]
    assert rows("SELECT used_at IS NOT NULL FROM invite") == [(1,)]
    assert any("not sent" in rec.getMessage() for rec in caplog.records)


def test_logs_hold_no_code_and_no_password(client, monkeypatch, caplog, now):
    with caplog.at_level(logging.DEBUG):
        invite_code = invite()
        register(client, code=invite_code)
        code = last_code()
        verify(client, "999999" if code != "999999" else "888888")
        client.post("/auth/login", json={"username": EMAIL, "password": PW})
        now.t += 61
        client.post("/auth/resend", json={"email": EMAIL})
        _broken_smtp(monkeypatch)
        now.t += 61
        client.post("/auth/resend", json={"email": EMAIL})
        verify(client, last_code())
    text = "\n".join(
        rec.getMessage() + repr(rec.args) + (rec.exc_text or "") for rec in caplog.records
    )
    for secret in (PW, code, invite_code, last_code()):
        assert secret not in text


# --- review fixes: password on verify, per-email lockout, mail thread, resend cooldown ------------


def test_re_registering_a_pending_email_cannot_take_it_over(client):
    register(client)  # the victim
    register(TestClient(app), password="the attacker's password", family="Mine")
    code = last_code()  # mailed to the victim
    assert verify(client, code).status_code == 400  # victim's password no longer matches
    attacker = verify(TestClient(app), wrong_for(code), password="the attacker's password")
    assert attacker.status_code == 400  # and the attacker never sees the code
    assert rows("SELECT email_verified_at FROM app_user") == [(None,)]
    register(client)  # the victim takes it back
    assert verify(client, last_code()).status_code == 200
    login = {"username": EMAIL, "password": "the attacker's password"}
    assert TestClient(app).post("/auth/login", json=login).status_code == 401


def test_the_right_code_with_a_wrong_password_fails_and_counts(client):
    register(client)
    assert verify(client, last_code(), password="not the password").status_code == 400
    assert rows("SELECT attempts FROM auth_challenge") == [(0,)]  # no try used: it could never win
    [(failures,)] = rows(
        "SELECT failures FROM login_attempt WHERE scope='user_ip' AND key=?",
        f"verify:{EMAIL}|testclient",
    )
    assert failures == 1  # but the lockout counts it
    assert verify(client, last_code()).status_code == 200


def test_wrong_passwords_do_not_burn_the_challenge(client, now, monkeypatch):
    monkeypatch.setenv("AUTH_BACKOFF_SCALE", "0.001")  # keep the lockout out of the way
    register(client)
    for _ in range(registration.MAX_ATTEMPTS + 2):
        now.t += 1
        assert verify(client, last_code(), password="a stranger's guess").status_code == 400
    now.t += 1
    assert verify(client, last_code()).status_code == 200  # the owner's code still works


def test_every_verify_failure_looks_the_same(client, now, monkeypatch):
    monkeypatch.setenv("AUTH_BACKOFF_SCALE", "0.001")
    register(client)
    code = last_code()
    cases = [
        dict(code=wrong_for(code)),
        dict(code=code, password="not the password"),
        dict(code=code, email="nobody@example.com"),
        dict(code=code, email="not an email"),
    ]
    answers = set()
    for case in cases:
        now.t += 1
        r = verify(client, **case)
        answers.add((r.status_code, r.content, "set-cookie" in r.headers))
    now.t += 15 * 60 + 1
    r = verify(client, code)  # expired
    answers.add((r.status_code, r.content, "set-cookie" in r.headers))
    assert answers == {(400, b'{"detail":"invalid_code"}', False)}


def test_verify_failures_stay_with_their_email(client, now):
    register(client)
    register(client, email="bo@example.com")
    for _ in range(lockout.FREE_FAILURES + 1):
        verify(client, wrong_for(last_code()))
    assert verify(client, last_code()).status_code == 429  # ana is held back from here
    assert verify(client, last_code("bo@example.com"), email="bo@example.com").status_code == 200


def test_many_addresses_cannot_lock_another_email_or_everyone(client, now):
    register(client)
    register(client, email="bo@example.com")
    for i in range(lockout.USER_CEILING + 5):
        registration.verify(EMAIL, "000000", "wrong guess here", f"10.0.0.{i}", None)
        registration.register("x@example.com", PW, "X", "ABCDEFGHJK", f"10.0.1.{i}")
    bo = registration.verify("bo@example.com", last_code("bo@example.com"), PW, "10.9.9.9", None)
    assert bo.kind == "ok"
    keys = {k for (k,) in rows("SELECT key FROM login_attempt WHERE scope='user'")}
    emails = (EMAIL, "bo@example.com", "x@example.com")
    assert keys <= {f"{kind}:{e}" for kind in ("verify", "register") for e in emails}


def test_failures_pile_up_on_the_email_across_resends(client, now, monkeypatch):
    monkeypatch.setenv("AUTH_BACKOFF_SCALE", "0.001")  # also scales the resend cooldown
    register(client)
    for _ in range(5):
        now.t += 1
        assert verify(client, wrong_for(last_code())).status_code == 400
    now.t += 1
    assert client.post("/auth/resend", json={"email": EMAIL}).status_code == 202
    assert len(outbox()) == 2  # a new code (and a fresh 5 tries on the challenge)
    for _ in range(5):
        now.t += 1
        assert verify(client, wrong_for(last_code())).status_code == 400
    [(failures,)] = rows(
        "SELECT failures FROM login_attempt WHERE scope='user_ip' AND key=?",
        f"verify:{EMAIL}|testclient",
    )
    assert failures == 10  # the resend did not reset the email's lockout
    assert verify(client, last_code()).status_code == 429  # and it is holding


def test_resend_cooldown_scales(client, now, monkeypatch):
    monkeypatch.setenv("AUTH_BACKOFF_SCALE", "0.1")
    register(client)
    now.t += 5
    assert client.post("/auth/resend", json={"email": EMAIL}).status_code == 202
    assert len(outbox()) == 1
    now.t += 2
    client.post("/auth/resend", json={"email": EMAIL})
    assert len(outbox()) == 2


def test_mail_goes_out_on_a_daemon_thread(monkeypatch):
    seen, made = [], []
    monkeypatch.setattr(mailer, "send", lambda *a: seen.append(threading.current_thread()))
    real = threading.Thread
    monkeypatch.setattr(registration.threading, "Thread", lambda **k: made.append(k) or real(**k))
    registration.send_later(EMAIL, "123456")  # the fixture's wrapper joins the thread
    assert made[0]["daemon"] is True and seen[0] is not threading.main_thread()


# --- final fixes: header-shaped emails, resend limits ---------------------------------------


@pytest.mark.parametrize(
    "email", ["a,victim@t.com", "x<victim@t.com>", '"x"@t.com', "a b@t.com", "a@t", "a@t..com"]
)
def test_header_shaped_emails_get_the_plain_400(client, email):
    r = register(client, email=email)
    assert r.status_code == 400 and r.json() == {"detail": "Enter a valid email address."}
    assert counts()["user"] == 0 and outbox() == []


def test_many_resends_from_one_ip_are_held_whatever_the_email(client, now):
    register(client)
    for i in range(lockout.IP_CEILING):
        email = EMAIL if i % 2 else f"nobody{i}@example.com"
        r = client.post("/auth/resend", json={"email": email})
        assert r.status_code == 202 and r.json() == {"status": "check_email"}
    for email in (EMAIL, "nobody@example.com"):
        r = client.post("/auth/resend", json={"email": email})
        assert r.status_code == 429 and r.json()["detail"] == "too_many_attempts"
        assert int(r.headers["Retry-After"]) > 0
    now.t += lockout.IP_LOCK_S + 1
    assert client.post("/auth/resend", json={"email": EMAIL}).status_code == 202


def test_at_most_ten_codes_per_account_in_a_day(client, now, monkeypatch):
    monkeypatch.setenv("AUTH_BACKOFF_SCALE", "0.001")  # resend cooldown and IP limit out of the way
    register(client)  # code 1
    register(client)  # code 2: registering again always issues one
    now.t += 1
    client.post("/auth/login", json={"username": EMAIL, "password": PW})  # code 3
    for _ in range(registration.CODES_PER_DAY - 3):
        now.t += 1
        client.post("/auth/resend", json={"email": EMAIL})
    assert len(outbox()) == registration.CODES_PER_DAY
    tenth = last_code()
    now.t += 1
    r = client.post("/auth/resend", json={"email": EMAIL})  # the 11th
    assert r.status_code == 202 and r.json() == {"status": "check_email"}
    assert register(client).status_code == 202
    assert len(outbox()) == registration.CODES_PER_DAY  # nothing more sent
    assert last_code() == tenth
    now.t += registration.DAY_S  # a rolling day: the first codes have aged out
    client.post("/auth/resend", json={"email": EMAIL})
    assert len(outbox()) == registration.CODES_PER_DAY + 1
    assert verify(client, last_code()).status_code == 200
