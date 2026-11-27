"""Self-registration: an invite code, then a 6-digit code by email.

Codes live in ``auth_challenge`` (purpose 'verify_email', subject the email, only a SHA-256 kept).
Only the newest code for an email works: issuing one retires the others, which are kept for a day
so that at most 10 codes go to one email in 24 hours. A code lasts 15 minutes and allows 5 tries;
a try without the account's password (which can never succeed) does not use one up.
Verifying needs the code AND the account's password, so re-registering a pending email cannot
hand the attacker the victim's verification. Register and resend answer the same whether or not
the email has an account; every accepted registration spends its invite. Failed registers and
verifies count against the login lockout keyed per email (``register:<email>``,
``verify:<email>``), so failures pile up on the email across resends and one email's trouble
never touches another's. Every resend counts against the address's login lockout.
Mail goes out on a daemon thread, after the response.
Times are unix seconds from ``auth.clock``. No code, password or email body is ever logged.
"""

from __future__ import annotations

import hmac
import logging
import re
import secrets
import threading
import unicodedata
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import mailer

from . import clock, lockout, passwords, service, store

logger = logging.getLogger(__name__)

PURPOSE = "verify_email"
CODE_TTL_S = 15 * 60
MAX_ATTEMPTS = 5
RESEND_S = 60  # times AUTH_BACKOFF_SCALE
CODES_PER_DAY = 10
DAY_S = 86400
FAMILY_NAME_MAX = 80
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")
SUBJECT = "Your sign-in code"
BODY = (
    "Your sign-in code is {code}.\n\n"
    "It expires in 15 minutes.\n\n"
    "If you didn't sign up, you can ignore this email.\n"
)


class RegistrationError(ValueError):
    """Input that cannot be accepted. The message is plain and says nothing about accounts."""


@dataclass(frozen=True)
class Result:
    kind: str  # "ok" | "invalid_invite" | "bad" | "locked" | "busy"
    retry_after: int = 0
    mail: tuple[str, str] | None = None  # (email, code) to send after the response
    token: str | None = None
    user: store.User | None = None


def normalize_email(raw: str) -> str | None:
    """Lower-cased and trimmed, or None if it is not an address of at most 64 characters."""
    email = unicodedata.normalize("NFKC", raw).strip().lower()
    return email if len(email) <= store.USERNAME_MAX and EMAIL_RE.fullmatch(email) else None


def _new_code(conn, email: str, now: float) -> str | None:
    """Inside the transaction: a new code that retires the old ones, or None past the daily cap."""
    mine = "purpose=? AND subject=?"
    conn.execute(
        f"DELETE FROM auth_challenge WHERE {mine} AND CAST(created_at AS REAL) <= ?",
        (PURPOSE, email, now - DAY_S),
    )
    (issued,) = conn.execute(
        f"SELECT COUNT(*) FROM auth_challenge WHERE {mine}", (PURPOSE, email)
    ).fetchone()
    if issued >= CODES_PER_DAY:
        return None
    # Defensive only: _use_code reads just the newest code, so older ones are already unusable.
    conn.execute(
        f"UPDATE auth_challenge SET expires_at=MIN(CAST(expires_at AS REAL), ?) WHERE {mine}",
        (now, PURPOSE, email),
    )
    code = f"{secrets.randbelow(10**6):06d}"
    conn.execute(
        "INSERT INTO auth_challenge (challenge_id, purpose, subject, code_hash, created_at, "
        "expires_at) VALUES (?,?,?,?,?,?)",
        (uuid.uuid4().hex, PURPOSE, email, store.token_hash(code), now, now + CODE_TTL_S),
    )
    return code


def _apply(conn, email: str, password_hash: str, family_name: str, invite_code: str):
    """Inside the transaction: (invite spent?, code to mail or None)."""
    user = store.get_user(conn, email)
    if user and (user.verified or user.disabled):
        return store.consume_invite(conn, invite_code, None), None  # nothing created, no mail
    if user:  # still pending: the new registration replaces it
        store.replace_hash(conn, user.id, password_hash)
        conn.execute("UPDATE family SET name=? WHERE family_id=?", (family_name, user.family_id))
        user_id = user.id
    else:
        family_id = store.create_family(conn, family_name)
        user_id = store.insert_user(conn, email, password_hash, family_id, verified=False)
    return store.consume_invite(conn, invite_code, user_id), _new_code(conn, email, clock.now())


def register(email: str, password: str, family_name: str, invite_code: str, ip: str) -> Result:
    address = normalize_email(email)
    if not address:
        raise RegistrationError("Enter a valid email address.")
    name = family_name.strip()
    if not 1 <= len(name) <= FAMILY_NAME_MAX:
        raise RegistrationError(f"Family name must be 1 to {FAMILY_NAME_MAX} characters.")
    try:
        passwords.validate_new_password(password)
    except passwords.PasswordError as exc:
        raise RegistrationError(str(exc)) from None
    with service.hash_slot() as got:
        if not got:
            return Result("busy", retry_after=service.BUSY_RETRY_AFTER_S)
        conn = store.connect()
        try:
            wait = lockout.reserve(conn, f"register:{address}", ip, clock.now())
            if wait > 0:
                return Result("locked", retry_after=int(wait))
            # Hashed before the invite is checked, so every outcome costs the same time.
            password_hash = passwords.hash_password(password)
            conn.execute("BEGIN IMMEDIATE")
            try:
                spent, code = _apply(conn, address, password_hash, name, invite_code)
                conn.execute("COMMIT" if spent else "ROLLBACK")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
            if not spent:
                return Result("invalid_invite")
            lockout.record_success(conn, f"register:{address}", ip, clock.now())
            return Result("ok", mail=(address, code) if code else None)
        finally:
            conn.close()


def verify(email: str, code: str, password: str, ip: str, user_agent: str | None) -> Result:
    address = normalize_email(email)
    if not address:  # can never have an account: nothing to look up or count
        return Result("bad")
    key = f"verify:{address}"
    with service.hash_slot() as got:
        if not got:
            return Result("busy", retry_after=service.BUSY_RETRY_AFTER_S)
        conn = store.connect()
        try:
            wait = lockout.reserve(conn, key, ip, clock.now())
            if wait > 0:
                return Result("locked", retry_after=int(wait))
            user = store.get_user(conn, address)
            # Checked outside the write lock, at the same cost when there is no account.
            password_ok = bool(user) and passwords.verify_password(password, user.password_hash)
            if not user:
                passwords.verify_dummy(password)
            now = clock.now()
            conn.execute("BEGIN IMMEDIATE")
            try:
                token = _use_code(conn, address, code, password_ok, user, now, user_agent)
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
            if token is None:
                return Result("bad")
            lockout.record_success(conn, key, ip, now)
            return Result("ok", token=token, user=user)
        finally:
            conn.close()


def _use_code(conn, address, code, password_ok, user, now, user_agent) -> str | None:
    """Inside the transaction: a session token on a match, else None. A wrong code with the right
    password counts a try; a wrong password never could have worked, so it costs no try (the
    lockout still counts it)."""
    row = conn.execute(
        "SELECT challenge_id, code_hash, attempts, expires_at FROM auth_challenge "
        "WHERE purpose=? AND subject=? AND consumed_at IS NULL "
        "ORDER BY rowid DESC LIMIT 1",  # the newest
        (PURPOSE, address),
    ).fetchone()
    # The account must be the one whose password was checked (not replaced since).
    live = user is not None and store.get_user(conn, address) == user and not user.disabled
    if not (password_ok and row and live and row[2] < MAX_ATTEMPTS and float(row[3]) > now):
        return None
    if not hmac.compare_digest(row[1], store.token_hash(code.strip())):
        conn.execute(
            "UPDATE auth_challenge SET attempts=attempts+1 WHERE challenge_id=?", (row[0],)
        )
        return None
    conn.execute("UPDATE auth_challenge SET consumed_at=? WHERE challenge_id=?", (now, row[0]))
    conn.execute(
        "UPDATE app_user SET email_verified_at=COALESCE(email_verified_at, ?) WHERE id=?",
        (datetime.fromtimestamp(now, UTC).isoformat(timespec="seconds"), user.id),
    )
    return store.create_session(conn, user.id, user_agent)


def _due(conn, address: str, now: float) -> bool:
    """A pending, enabled account whose last code is older than the cooldown."""
    user = store.get_user(conn, address)
    if not user or user.verified or user.disabled:
        return False
    (last,) = conn.execute(
        "SELECT MAX(created_at) FROM auth_challenge WHERE purpose=? AND subject=?",
        (PURPOSE, address),
    ).fetchone()
    return last is None or now - float(last) >= RESEND_S * lockout.scale()


def issue_code(email: str) -> tuple[str, str] | None:
    """A fresh code for a pending account whose last code is past the cooldown, else None."""
    address = normalize_email(email)
    if not address:
        return None
    conn = store.connect()
    try:
        now = clock.now()
        if not _due(conn, address, now):  # read first: most calls need no write lock
            return None
        conn.execute("BEGIN IMMEDIATE")
        try:
            code = _new_code(conn, address, now) if _due(conn, address, now) else None
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        return (address, code) if code else None
    finally:
        conn.close()


def resend(email: str, ip: str) -> Result:
    """Every request counts against the address (whatever the email); a held address waits."""
    conn = store.connect()
    try:
        wait = lockout.reserve_ip(conn, ip, clock.now())
    finally:
        conn.close()
    if wait > 0:
        return Result("locked", retry_after=int(wait))
    return Result("ok", mail=issue_code(email))


def send_code(email: str, code: str) -> None:
    """Any failure is logged by type only; the account stays pending."""
    try:
        mailer.send(email, SUBJECT, BODY.format(code=code))
    except Exception as exc:  # noqa: BLE001 - a bad port or an outbox OSError count too
        logger.warning("sign-in code not sent: %s", type(exc).__name__)


def send_later(email: str, code: str) -> threading.Thread:
    """Fire and forget on a daemon thread, so SMTP time never shows on any connection."""
    thread = threading.Thread(target=send_code, args=(email, code), daemon=True)
    thread.start()
    return thread
