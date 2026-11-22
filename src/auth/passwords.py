"""Password hashing: scrypt from the standard library, salted per user.

Stored form: ``scrypt$<N>$<r>$<p>$<salt b64>$<hash b64>``. The parameters travel with the hash, so
raising ``CURRENT`` later does not break old hashes: ``needs_rehash`` says an old one should be
rewritten, and the login flow does that right after a correct password.

Nothing here logs or returns a password.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 1024  # more than any person types; bounds the work an attacker can request
SALT_BYTES = 16
KEY_BYTES = 32


@dataclass(frozen=True)
class ScryptParams:
    n: int
    r: int
    p: int

    @property
    def maxmem(self) -> int:
        # scrypt needs about 128 * N * r bytes; leave headroom so OpenSSL never refuses.
        return 128 * self.n * self.r * 2 + 1024 * 1024


# The one place the cost lives. N=2**15, r=8, p=1 uses 32 MiB and takes roughly 100 ms on a small
# VPS: logins are rare, so a slow check costs nothing, and a thief of the database pays it per guess.
CURRENT = ScryptParams(n=2**15, r=8, p=1)


class PasswordError(ValueError):
    """A password that must not be accepted (too short, too long)."""


def validate_new_password(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise PasswordError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise PasswordError("Password is too long.")


def _derive(password: str, salt: bytes, params: ScryptParams) -> bytes:
    return hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=params.n,
        r=params.r,
        p=params.p,
        maxmem=params.maxmem,
        dklen=KEY_BYTES,
    )


def hash_password(password: str, params: ScryptParams | None = None) -> str:
    params = params or CURRENT
    salt = secrets.token_bytes(SALT_BYTES)
    digest = _derive(password, salt, params)
    b64 = lambda raw: base64.b64encode(raw).decode("ascii")  # noqa: E731
    return f"scrypt${params.n}${params.r}${params.p}${b64(salt)}${b64(digest)}"


def _parse(stored: str) -> tuple[ScryptParams, bytes, bytes] | None:
    try:
        scheme, n, r, p, salt, digest = stored.split("$")
        if scheme != "scrypt":
            return None
        return (
            ScryptParams(int(n), int(r), int(p)),
            base64.b64decode(salt, validate=True),
            base64.b64decode(digest, validate=True),
        )
    except (ValueError, TypeError):
        return None


def verify_password(password: str, stored: str) -> bool:
    """Constant-time check. A malformed stored hash is simply a wrong password."""
    parsed = _parse(stored)
    if parsed is None or len(password) > MAX_PASSWORD_LENGTH:
        return False
    params, salt, expected = parsed
    try:
        actual = _derive(password, salt, params)
    except ValueError:  # parameters this OpenSSL refuses
        return False
    return hmac.compare_digest(actual, expected)


def needs_rehash(stored: str) -> bool:
    parsed = _parse(stored)
    return parsed is None or parsed[0] != CURRENT


_dummy: dict[ScryptParams, str] = {}


def verify_dummy(password: str) -> None:
    """Spend the same time as a real check, for a username that does not exist."""
    stored = _dummy.get(CURRENT)
    if stored is None:
        stored = _dummy[CURRENT] = hash_password(secrets.token_urlsafe(16))
    verify_password(password, stored)
