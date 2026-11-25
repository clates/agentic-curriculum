"""Self-registration: an invite code, then a 6-digit code by email.

Codes live in ``auth_challenge`` (purpose 'verify_email', subject the email, only a SHA-256 kept),
one per email: issuing a new one deletes the old. They last 15 minutes and allow 5 tries.
Register and resend answer the same whether or not the email has an account; every accepted
registration spends its invite. Bad invites and wrong codes count against the per-address login
lockout under the pseudo-usernames below (the space keeps them apart from any real username).
Times are unix seconds from ``auth.clock``. No code, password or email body is ever logged.
"""

from __future__ import annotations

import hmac
import logging
import re
import secrets
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
RESEND_S = 60
FAMILY_NAME_MAX = 80
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
REGISTER_KEY = "register invite"
VERIFY_KEY = "verify code"
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
    mail: tuple[str, str] | None = None  # (email, code) to send once the response is out
    token: str | None = None
    user: store.User | None = None


def normalize_email(raw: str) -> str | None:
    """Lower-cased and trimmed, or None if it is not an address of at most 64 characters."""
    email = unicodedata.normalize("NFKC", raw).strip().lower()
    return email if len(email) <= store.USERNAME_MAX and EMAIL_RE.fullmatch(email) else None


def _new_code(conn, email: str, now: float) -> str:
    code = f"{secrets.randbelow(10**6):06d}"
    conn.execute("DELETE FROM auth_challenge WHERE purpose=? AND subject=?", (PURPOSE, email))
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
            wait = lockout.reserve(conn, REGISTER_KEY, ip, clock.now())
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
            lockout.record_success(conn, REGISTER_KEY, ip, clock.now())
            return Result("ok", mail=(address, code) if code else None)
        finally:
            conn.close()


def verify(email: str, code: str, ip: str, user_agent: str | None) -> Result:
    address = normalize_email(email) or ""
    conn = store.connect()
    try:
        wait = lockout.reserve(conn, VERIFY_KEY, ip, clock.now())
        if wait > 0:
            return Result("locked", retry_after=int(wait))
        now = clock.now()
        conn.execute("BEGIN IMMEDIATE")
        try:
            row = conn.execute(
                "SELECT challenge_id, code_hash, attempts, expires_at FROM auth_challenge "
                "WHERE purpose=? AND subject=? AND consumed_at IS NULL",
                (PURPOSE, address),
            ).fetchone()
            user = store.get_user(conn, address) if row else None
            token = None
            if user and not user.disabled and row[2] < MAX_ATTEMPTS and float(row[3]) > now:
                if hmac.compare_digest(row[1], store.token_hash(code.strip())):
                    conn.execute(
                        "UPDATE auth_challenge SET consumed_at=? WHERE challenge_id=?",
                        (now, row[0]),
                    )
                    conn.execute(
                        "UPDATE app_user SET email_verified_at=COALESCE(email_verified_at, ?) "
                        "WHERE id=?",
                        (datetime.now(UTC).isoformat(timespec="seconds"), user.id),
                    )
                    token = store.create_session(conn, user.id, user_agent)
                else:
                    conn.execute(
                        "UPDATE auth_challenge SET attempts=attempts+1 WHERE challenge_id=?",
                        (row[0],),
                    )
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        if token is None:
            return Result("bad")
        lockout.record_success(conn, VERIFY_KEY, ip, now)
        return Result("ok", token=token, user=user)
    finally:
        conn.close()


def issue_code(email: str) -> tuple[str, str] | None:
    """A fresh code for a pending account whose last code is over a minute old, else None."""
    address = normalize_email(email)
    if not address:
        return None
    conn = store.connect()
    try:
        now = clock.now()
        conn.execute("BEGIN IMMEDIATE")
        try:
            user = store.get_user(conn, address)
            last = conn.execute(
                "SELECT MAX(created_at) FROM auth_challenge WHERE purpose=? AND subject=?",
                (PURPOSE, address),
            ).fetchone()[0]
            due = last is None or now - float(last) >= RESEND_S
            pending = user and not user.verified and not user.disabled
            code = _new_code(conn, address, now) if pending and due else None
            conn.execute("COMMIT" if code else "ROLLBACK")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        return (address, code) if code else None
    finally:
        conn.close()


def send_code(email: str, code: str) -> None:
    """Runs after the response: any failure is logged by type only and the account stays pending."""
    try:
        mailer.send(email, SUBJECT, BODY.format(code=code))
    except Exception as exc:  # noqa: BLE001 - a bad port or an outbox OSError count too
        logger.warning("sign-in code not sent: %s", type(exc).__name__)
