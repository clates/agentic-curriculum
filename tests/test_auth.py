"""Login: hashing, sessions, lockout, proxy trust, CSRF, route inventory and the CLI."""

from __future__ import annotations

import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import db_utils  # noqa: E402
from auth import clock, lockout, passwords, service, store  # noqa: E402
from auth.web import COOKIE_NAME, PUBLIC_PATHS, current_family  # noqa: E402
from main import app  # noqa: E402
from migrations import apply_migrations  # noqa: E402
from tenancy import owned_student_id  # noqa: E402

PASSWORD = "correct horse battery"
FAST = passwords.ScryptParams(n=2**10, r=8, p=1)  # tests do not need the production cost


class Clock:
    def __init__(self, start: float = 1_000_000.0):
        self.t = start

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


@pytest.fixture(autouse=True)
def auth_env(tmp_path, monkeypatch):
    db = tmp_path / "auth.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    monkeypatch.setattr(db_utils, "DB_FILE", str(db))  # import-time snapshot some routes read
    monkeypatch.delenv("AUTH_REQUIRED", raising=False)
    monkeypatch.delenv("AUTH_BACKOFF_SCALE", raising=False)
    monkeypatch.delenv("COOKIE_SECURE", raising=False)
    monkeypatch.setattr(passwords, "CURRENT", FAST)
    passwords._dummy.clear()
    monkeypatch.delenv("AUTH_ALLOWED_HOSTS", raising=False)
    monkeypatch.delenv("AUTH_MAX_CONCURRENT_HASHES", raising=False)
    monkeypatch.setattr(lockout, "_last_prune", float("-inf"))
    monkeypatch.setattr(service, "_slots", None)
    fake = Clock()
    clock.set_source(fake)
    apply_migrations(db)
    yield fake
    clock.set_source(None)


@pytest.fixture
def now(auth_env) -> Clock:
    return auth_env


@pytest.fixture
def user():
    conn = store.connect()
    try:
        created = store.create_user(conn, "Parent", PASSWORD)
    finally:
        conn.close()
    return created


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def required(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "1")


def login(c, username="parent", password=PASSWORD, **kwargs):
    return c.post("/auth/login", json={"username": username, "password": password}, **kwargs)


def db_rows(sql, *args):
    conn = store.connect()
    try:
        return conn.execute(sql, args).fetchall()
    finally:
        conn.close()


# --- hashing ---------------------------------------------------------------------------------


def test_hash_verifies_and_is_salted():
    a, b = passwords.hash_password(PASSWORD), passwords.hash_password(PASSWORD)
    assert a != b  # per-user salt
    assert passwords.verify_password(PASSWORD, a) and passwords.verify_password(PASSWORD, b)
    assert not passwords.verify_password(PASSWORD + "x", a)
    assert a.startswith("scrypt$1024$8$1$") and PASSWORD not in a


def test_verify_uses_constant_time_compare(monkeypatch):
    calls = []
    real = passwords.hmac.compare_digest
    monkeypatch.setattr(
        passwords.hmac, "compare_digest", lambda x, y: calls.append(1) or real(x, y)
    )
    passwords.verify_password(PASSWORD, passwords.hash_password(PASSWORD))
    assert calls


def test_malformed_hash_is_just_a_wrong_password():
    for bad in ("", "x", "scrypt$a$b$c$d$e", "bcrypt$1$2$3$AA==$AA=="):
        assert passwords.verify_password(PASSWORD, bad) is False


def test_old_parameters_still_verify_and_ask_for_a_rehash(monkeypatch):
    old = passwords.hash_password(PASSWORD)
    monkeypatch.setattr(passwords, "CURRENT", passwords.ScryptParams(n=2**11, r=8, p=1))
    assert passwords.verify_password(PASSWORD, old)
    assert passwords.needs_rehash(old)
    assert not passwords.needs_rehash(passwords.hash_password(PASSWORD))


def test_login_upgrades_an_old_hash(user, monkeypatch):
    monkeypatch.setattr(passwords, "CURRENT", passwords.ScryptParams(n=2**11, r=8, p=1))
    assert service.attempt_login("parent", PASSWORD, "1.1.1.1").kind == "ok"
    (stored,) = db_rows("SELECT password_hash FROM app_user")[0]
    assert stored.startswith("scrypt$2048$")


def test_minimum_length_is_enforced_when_creating_a_user():
    conn = store.connect()
    with pytest.raises(passwords.PasswordError):
        store.create_user(conn, "short", "elevenchars")
    assert store.create_user(conn, "twelve", "twelvechars!") is not None
    conn.close()


def test_usernames_are_unique_ignoring_case(user):
    conn = store.connect()
    assert store.create_user(conn, "PARENT", PASSWORD) is None
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO app_user (id, username, password_hash, family_id, created_at) "
            "VALUES ('x','Parent','h','fam_local','t')"
        )
    conn.close()


def test_first_user_belongs_to_the_default_family(user):
    assert user.family_id == "fam_local" == store.DEFAULT_FAMILY


# --- login, sessions, cookie -----------------------------------------------------------------


def test_login_sets_a_hardened_cookie_and_stores_only_a_hash(client, user):
    r = login(client, headers={"user-agent": "A" * 500})
    assert r.status_code == 200 and r.json() == {"user": {"username": "parent"}}
    cookie = r.headers["set-cookie"]
    token = client.cookies.get(COOKIE_NAME)
    assert "HttpOnly" in cookie and "SameSite=lax" in cookie and "Path=/" in cookie
    assert "Secure" not in cookie and "Max-Age=2592000" in cookie
    assert len(token) >= 43  # 32 random bytes, url-safe base64
    (row,) = db_rows("SELECT token_hash, user_agent FROM auth_session")
    assert row[0] == store.token_hash(token) != token and len(row[0]) == 64
    assert len(row[1]) == 200
    assert token not in repr(db_rows("SELECT * FROM auth_session"))


def test_cookie_is_secure_behind_https_or_by_env(client, user, monkeypatch):
    local = TestClient(app, client=("127.0.0.1", 1234))
    r = login(local, headers={"x-forwarded-proto": "https"})
    assert "Secure" in r.headers["set-cookie"]
    # a stranger cannot claim https: only the loopback proxy is believed (cookie stays plain)
    r = login(client, headers={"x-forwarded-proto": "https"})
    assert "Secure" not in r.headers["set-cookie"]
    monkeypatch.setenv("COOKIE_SECURE", "1")
    assert "Secure" in login(client).headers["set-cookie"]


def test_wrong_password_and_unknown_user_look_identical(client, user):
    a = login(client, password="wrong password!!")
    b = login(client, username="nobody", password="wrong password!!")
    assert (
        (a.status_code, a.json())
        == (b.status_code, b.json())
        == (401, {"detail": "invalid_credentials"})
    )
    assert "set-cookie" not in a.headers and "set-cookie" not in b.headers


def test_unknown_user_costs_a_real_hash(user, monkeypatch):
    seen = []
    real = passwords._derive
    monkeypatch.setattr(passwords, "_derive", lambda *a, **k: seen.append(1) or real(*a, **k))
    service.attempt_login("parent", "wrong password!!", "9.9.9.9")
    known = len(seen)
    service.attempt_login("nobody", "wrong password!!", "9.9.9.9")
    service.attempt_login("nobody", "wrong password!!", "9.9.9.9")
    assert known == 1 and len(seen) >= 3  # the dummy is built once, then one hash per attempt
    start = time.perf_counter()
    service.attempt_login("nobody", "wrong password!!", "8.8.8.8")
    unknown_t = time.perf_counter() - start
    start = time.perf_counter()
    service.attempt_login("parent", "wrong password!!", "8.8.4.4")
    known_t = time.perf_counter() - start
    assert abs(unknown_t - known_t) < 0.25  # same order of magnitude, not an instant return


def test_disabled_user_cannot_sign_in_and_loses_sessions(client, user):
    assert login(client).status_code == 200
    conn = store.connect()
    store.set_disabled(conn, "parent", True)
    conn.close()
    assert db_rows("SELECT COUNT(*) FROM auth_session") == [(0,)]
    other = TestClient(app)
    assert login(other).status_code == 401


def test_session_expires_after_30_days_and_slides(client, user, required, now):
    login(client)
    assert client.get("/auth/me").status_code == 200
    now.advance(29 * 86400)
    assert client.get("/auth/me").status_code == 200  # use refreshes the expiry
    now.advance(29 * 86400)
    assert client.get("/auth/me").status_code == 200  # 58 days after login, 29 after last use
    now.advance(31 * 86400)
    r = client.get("/auth/me")
    assert r.status_code == 401 and r.json() == {"detail": "not_authenticated"}


def test_sliding_reissues_the_cookie_but_not_on_every_request(client, user, required, now):
    login(client)
    first = client.get("/auth/me")
    assert "set-cookie" not in first.headers  # seen a moment ago: no rewrite
    now.advance(store.SESSION_REFRESH_S + 1)
    again = client.get("/auth/me")
    assert "Max-Age=2592000" in again.headers["set-cookie"]


def test_expired_sessions_are_cleaned_on_next_login(user, now):
    conn = store.connect()
    store.create_session(conn, user.id, None)
    now.advance(31 * 86400)
    store.create_session(conn, user.id, None)
    assert conn.execute("SELECT COUNT(*) FROM auth_session").fetchone() == (1,)
    conn.close()


def test_logout_ends_the_session_and_clears_the_cookie(client, user, required):
    login(client)
    r = client.post("/auth/logout")
    assert r.status_code == 200 and "Max-Age=0" in r.headers["set-cookie"]
    assert db_rows("SELECT COUNT(*) FROM auth_session") == [(0,)]
    assert client.get("/auth/me").status_code == 401


def test_a_garbage_cookie_is_401_and_gets_cleared(client, required):
    client.cookies.set(COOKIE_NAME, "not-a-real-token")
    r = client.get("/students")
    assert r.status_code == 401
    assert "Max-Age=0" in r.headers["set-cookie"]


def test_me_when_login_is_off_says_so(client):
    assert client.get("/auth/me").json() == {
        "auth_required": False,
        "user": None,
        "permissions": ["admin"],
    }


def test_nothing_changes_when_login_is_off(client):
    assert client.get("/students").status_code == 200
    assert client.get("/system/options").status_code == 200


# --- lockout ---------------------------------------------------------------------------------


def test_lock_math_doubles_to_an_hour_cap():
    assert [lockout.lock_seconds(n) for n in range(1, 8)] == [0, 0, 0, 15, 30, 60, 120]
    assert lockout.lock_seconds(40) == 3600


def test_backoff_scale_shrinks_every_number(monkeypatch):
    monkeypatch.setenv("AUTH_BACKOFF_SCALE", "0.1")
    assert lockout.lock_seconds(4) == pytest.approx(1.5)


def wrong(ip="1.1.1.1", name="parent"):
    return service.attempt_login(name, "wrong password!!", ip)


def test_three_free_failures_then_progressive_locks(user, now):
    assert [wrong().kind for _ in range(4)] == ["bad"] * 4  # the 4th wrong try starts the lock
    blocked = wrong()
    assert blocked.kind == "locked" and blocked.retry_after == 15
    now.advance(15)
    assert wrong().kind == "bad"  # 5th wrong try: lock is now 30 s
    now.advance(10)
    assert wrong().retry_after == 20
    now.advance(20)
    assert wrong().kind == "bad"  # 6th: 60 s
    assert wrong().retry_after == 60


def test_a_locked_attempt_does_not_check_the_password(user, now, monkeypatch):
    for _ in range(4):
        wrong()
    monkeypatch.setattr(passwords, "verify_password", lambda *a: pytest.fail("password evaluated"))
    monkeypatch.setattr(passwords, "verify_dummy", lambda *a: pytest.fail("dummy evaluated"))
    assert service.attempt_login("parent", PASSWORD, "1.1.1.1").kind == "locked"  # even if right
    assert service.attempt_login("parent", "x", "1.1.1.1").kind == "locked"


def test_locking_does_not_reveal_whether_the_username_exists(user, now):
    for name in ("parent", "ghost"):
        for _ in range(4):
            wrong(name=name)
    a, b = wrong(name="parent"), wrong(name="ghost")
    assert (a.kind, a.retry_after) == (b.kind, b.retry_after) == ("locked", 15)


def test_success_resets_and_a_quiet_period_forgives(user, now):
    for _ in range(3):
        wrong()
    assert service.attempt_login("parent", PASSWORD, "1.1.1.1").kind == "ok"
    for _ in range(3):
        assert wrong().kind == "bad"  # the three free tries are back
    for _ in range(2):
        wrong()  # 4th and 5th: lock of 30 s
    now.advance(lockout.QUIET_RESET_S + 1)
    assert [wrong().kind for _ in range(3)] == ["bad"] * 3  # slate is clean after a quiet period
    assert wrong().kind == "bad"


def test_the_owner_is_not_locked_out_from_another_address(user, now):
    for _ in range(6):
        wrong(ip="6.6.6.6")  # an attacker hammering the owner's username
    assert wrong(ip="6.6.6.6").kind == "locked"
    assert service.attempt_login("parent", PASSWORD, "2.2.2.2").kind == "ok"


def test_per_address_ceiling_covers_every_username(user, now):
    for i in range(lockout.IP_CEILING):
        wrong(ip="7.7.7.7", name=f"user{i}")  # one try each: never trips a per-user lock
    r = service.attempt_login("parent", PASSWORD, "7.7.7.7")
    assert r.kind == "locked" and r.retry_after == lockout.IP_LOCK_S  # right password, still held
    assert service.attempt_login("parent", PASSWORD, "3.3.3.3").kind == "ok"
    now.advance(lockout.IP_LOCK_S + 1)
    assert service.attempt_login("parent", PASSWORD, "7.7.7.7").kind == "ok"


def test_spread_out_attack_slows_strangers_but_never_the_known_address(user, now):
    assert service.attempt_login("parent", PASSWORD, "10.0.0.1").kind == "ok"  # the owner's home
    for i in range(lockout.USER_CEILING):
        wrong(ip=f"20.0.{i // 250}.{i % 250}")  # one try from each of many addresses
    stranger = service.attempt_login("parent", PASSWORD, "30.0.0.1")
    assert stranger.kind == "locked" and 0 < stranger.retry_after <= lockout.USER_BASE_LOCK_S
    assert service.attempt_login("parent", PASSWORD, "10.0.0.1").kind == "ok"  # never blocked
    now.advance(lockout.USER_BASE_LOCK_S + 1)
    assert service.attempt_login("parent", PASSWORD, "30.0.0.1").kind == "ok"  # only slowed


def test_user_ceiling_lock_is_capped(user, now):
    for round_ in range(8):
        for i in range(lockout.USER_CEILING):
            wrong(ip=f"40.{round_}.{i // 250}.{i % 250}")
        now.advance(lockout.USER_MAX_LOCK_S + 1)
    (locked_until,) = db_rows("SELECT locked_until FROM login_attempt WHERE scope='user'")[0]
    assert locked_until - now.t <= 0  # never beyond the cap into the future


def test_parallel_guesses_are_counted_before_the_password_is_checked(user, now):
    """Each try is booked as a failure up front, so a burst cannot beat a lock not yet written."""
    conn = store.connect()
    waits = [lockout.reserve(conn, "parent", "1.1.1.1", now.t) for _ in range(5)]
    conn.close()
    assert waits[:4] == [0.0] * 4 and waits[4] == 15


def test_attempt_rows_are_pruned_after_the_quiet_period(user, now):
    wrong(ip="5.5.5.5", name="ghost")
    now.advance(lockout.QUIET_RESET_S * 2)
    wrong(ip="5.5.5.6", name="other")
    keys = {r[0] for r in db_rows("SELECT key FROM login_attempt")}
    assert "ghost|5.5.5.5" not in keys and "5.5.5.5" not in keys


def test_endpoint_returns_429_with_retry_after(client, user):
    for _ in range(4):
        assert login(client, password="wrong password!!").status_code == 401
    r = login(client, password="wrong password!!")
    assert r.status_code == 429 and r.headers["retry-after"] == "15"
    assert r.json() == {"detail": "too_many_attempts", "retry_after": 15}


# --- client address: trusted only from the local proxy -----------------------------------------


def test_forwarded_address_is_trusted_only_from_loopback(user):
    local = TestClient(app, client=("127.0.0.1", 1))
    remote = TestClient(app, client=("203.0.113.9", 1))
    for _ in range(4):
        login(
            local, password="wrong password!!", headers={"x-curriculum-client-ip": "198.51.100.1"}
        )
    # the proxy said the caller is 198.51.100.1: that address is locked, a different one is not
    assert login(local, headers={"x-curriculum-client-ip": "198.51.100.1"}).status_code == 429
    assert login(local, headers={"x-curriculum-client-ip": "198.51.100.2"}).status_code == 200
    # a direct caller cannot pick its own address by sending the header
    for i in range(5):
        login(remote, password="wrong password!!", headers={"x-curriculum-client-ip": f"9.9.9.{i}"})
    assert login(remote, headers={"x-curriculum-client-ip": "9.9.9.99"}).status_code == 429


def test_a_junk_forwarded_address_falls_back_to_the_connection(user):
    local = TestClient(app, client=("127.0.0.1", 1))
    for _ in range(4):
        login(local, password="wrong password!!", headers={"x-curriculum-client-ip": "not-an-ip"})
    assert login(local).status_code == 429  # lumped under 127.0.0.1


# --- CSRF ------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "headers,status",
    [
        ({"origin": "http://testserver"}, 200),
        ({"origin": "http://evil.example"}, 403),
        ({"origin": "null"}, 403),
        ({"referer": "http://evil.example/page"}, 403),
        ({"referer": "http://testserver/login"}, 200),
        ({"sec-fetch-site": "cross-site"}, 403),
        ({}, 200),  # not a browser
    ],
)
def test_origin_check_on_login(client, user, headers, status):
    assert login(client, headers=headers).status_code == status


def test_origin_check_uses_the_forwarded_host_from_the_proxy(user):
    local = TestClient(app, client=("127.0.0.1", 1))
    ok = {"origin": "https://home.example", "x-forwarded-host": "home.example"}
    assert login(local, headers=ok).status_code == 200
    bad = {"origin": "https://evil.example", "x-forwarded-host": "home.example"}
    assert login(local, headers=bad).status_code == 403


def test_origin_check_guards_unsafe_methods_on_every_route(client, user, required):
    login(client)
    evil = {"origin": "http://evil.example"}
    assert client.post("/auth/logout", headers=evil).status_code == 403
    assert client.post("/students", json={}, headers=evil).status_code == 403
    assert client.get("/students", headers=evil).status_code == 200  # reads are not state changes
    assert client.post("/auth/logout", headers={"origin": "http://testserver"}).status_code == 200


# --- route inventory -------------------------------------------------------------------------


def iter_routes(routes):
    for route in routes:
        inner = getattr(route, "original_router", None)
        if inner is not None:
            yield from iter_routes(inner.routes)
        elif getattr(route, "path", None):
            yield route


def test_every_route_is_public_on_purpose_or_protected(required, client):
    """With login required, an anonymous call must get 401 unless the path is on the allowlist.
    A new route that forgets protection (or sneaks onto the list) fails here."""
    seen = set()
    docs = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}  # switched off at startup
    plain = {r.path for r in iter_routes(app.routes) if not isinstance(r, APIRoute)}
    assert plain <= docs, f"unexpected non-API routes the gate cannot see: {plain - docs}"
    for route in (r for r in iter_routes(app.routes) if isinstance(r, APIRoute)):
        path = route.path
        concrete = path.replace("{", "x").replace("}", "")  # {student_id} -> xstudent_id
        for method in sorted(route.methods - {"HEAD", "OPTIONS"}):
            seen.add((method, path))
            r = client.request(method, concrete)
            if path in PUBLIC_PATHS:
                assert r.status_code != 401, f"{method} {path} is public but answered 401"
            else:
                assert r.status_code == 401, f"{method} {path} answered {r.status_code} anonymously"
    assert ("GET", "/students") in seen and ("POST", "/auth/login") in seen
    assert PUBLIC_PATHS == {"/auth/login", "/auth/logout", "/health", "/version"}


def _reaches(dependant, call) -> bool:
    return any(d.call is call or _reaches(d, call) for d in dependant.dependencies)


def _reaches_admin(dependant) -> bool:
    """require_permission("admin") makes a fresh closure, so match it by name and captured value."""
    return any(
        (
            getattr(d.call, "__qualname__", "") == "require_permission.<locals>.check"
            and d.call.__closure__[0].cell_contents == "admin"
        )
        or _reaches_admin(d)
        for d in dependant.dependencies
    )


def test_every_route_declares_its_family():
    """Every non-public route acts for one family; every student route checks ownership.
    Unscoped on purpose: public paths, /auth/*, the hello at /, and the shared standards data."""
    checked = set()
    for route in (r for r in iter_routes(app.routes) if isinstance(r, APIRoute)):
        path = route.path
        if path in PUBLIC_PATHS | {"/", "/system/options"}:
            continue
        if path.startswith(("/auth/", "/curriculum/")):
            continue
        checked.add(path)
        assert _reaches(route.dependant, current_family), f"{path} does not ask for the family"
        if "{student_id}" in path:
            assert _reaches(route.dependant, owned_student_id), f"{path} skips the ownership check"
        if path.startswith("/loop-admin/"):
            assert _reaches_admin(route.dependant), f"{path} is not admin-only"
    assert {"/students", "/this-week", "/generate_weekly_plan", "/student/{student_id}"} <= checked


def test_every_public_path_is_a_real_route():
    paths = {r.path for r in iter_routes(app.routes)}
    assert PUBLIC_PATHS <= paths


def test_docs_are_not_served_when_login_is_required(monkeypatch):
    """The docs routes sit outside the gate, so they are switched off at startup."""
    code = (
        "import sys; sys.path.insert(0, 'src'); import main; "
        "print(sorted(getattr(r, 'path', '') for r in main.app.routes if getattr(r, 'path', '') in "
        "('/docs', '/redoc', '/openapi.json')))"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True,
        env={"PATH": "/usr/bin:/bin", "AUTH_REQUIRED": "1"},
    )  # fmt: skip
    assert out.stdout.strip() == "[]", out.stderr


def test_a_valid_session_passes_the_gate(client, user, required):
    login(client)
    assert client.get("/students").status_code == 200
    assert client.get("/auth/me").json() == {
        "auth_required": True,
        "user": {"username": "parent"},
        "permissions": [],
    }
    assert client.get("/health").status_code == 200


def test_health_and_version_need_no_session(client, required):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/version").status_code == 200


# --- the command line --------------------------------------------------------------------------


def run_cli(tmp_path, *args, password=None, extra_env=None):
    import os

    env = {
        **os.environ,
        "CURRICULUM_DB_PATH": str(tmp_path / "auth.db"),
        "PYTHONPATH": str(ROOT / "src"),
    }
    env.pop("AUTH_NEW_PASSWORD", None)
    if password is not None:
        env["AUTH_NEW_PASSWORD"] = password
    return subprocess.run(
        [sys.executable, "-m", "auth", *args], cwd=ROOT / "src", env=env,
        capture_output=True, text=True, stdin=subprocess.DEVNULL,
    )  # fmt: skip


def test_cli_creates_is_idempotent_and_never_prints_the_password(tmp_path):
    first = run_cli(tmp_path, "create-user", "Mama", password=PASSWORD)
    assert first.returncode == 0 and "Created user 'mama'" in first.stdout
    assert PASSWORD not in first.stdout + first.stderr
    again = run_cli(tmp_path, "create-user", "mama", password="a different password")
    assert again.returncode == 0 and "already exists" in again.stdout
    rows = db_rows("SELECT username, family_id FROM app_user")
    assert rows == [("mama", "fam_local")]
    assert service.attempt_login("mama", PASSWORD, "1.1.1.1").kind == "ok"  # not overwritten


def test_cli_rejects_a_short_password(tmp_path):
    r = run_cli(tmp_path, "create-user", "mama", password="tooshort")
    assert r.returncode == 1 and "at least 12" in r.stderr
    assert db_rows("SELECT COUNT(*) FROM app_user") == [(0,)]


def test_cli_does_not_take_a_password_argument(tmp_path):
    r = run_cli(tmp_path, "create-user", "mama", "hunter2hunter2")
    assert r.returncode == 2  # argparse: unrecognized argument


def test_cli_set_password_signs_out_and_disable_works(tmp_path):
    run_cli(tmp_path, "create-user", "mama", password=PASSWORD)
    conn = store.connect()
    store.create_session(conn, store.get_user(conn, "mama").id, None)
    conn.close()
    r = run_cli(tmp_path, "set-password", "mama", password="a brand new password")
    assert r.returncode == 0 and db_rows("SELECT COUNT(*) FROM auth_session") == [(0,)]
    assert service.attempt_login("mama", PASSWORD, "1.1.1.1").kind == "bad"
    assert service.attempt_login("mama", "a brand new password", "1.1.1.2").kind == "ok"
    assert run_cli(tmp_path, "disable", "mama").returncode == 0
    assert service.attempt_login("mama", "a brand new password", "1.1.1.3").kind == "bad"
    assert run_cli(tmp_path, "enable", "mama").returncode == 0
    assert service.attempt_login("mama", "a brand new password", "1.1.1.4").kind == "ok"
    assert run_cli(tmp_path, "disable", "nobody").returncode == 1


def test_migration_runner_tolerates_the_gap_before_0011(tmp_path):
    import shutil

    from migrations import MIGRATIONS_DIR

    d = tmp_path / "gap"
    d.mkdir()
    for f in [*MIGRATIONS_DIR.glob("000[1-8]_*.sql"), *MIGRATIONS_DIR.glob("0011_*.sql")]:
        shutil.copy(f, d / f.name)
    assert apply_migrations(tmp_path / "gap.db", d) == [1, 2, 3, 4, 5, 6, 7, 8, 11]


# --- security review follow-up ---------------------------------------------------------------


def test_busy_hashing_turns_attempts_away_before_the_lockout_gate(user, monkeypatch, client):
    import threading

    monkeypatch.setenv("AUTH_MAX_CONCURRENT_HASHES", "1")
    monkeypatch.setattr(service, "BUSY_WAIT_S", 0.2)
    inside, release = threading.Event(), threading.Event()

    def slow_verify(*args):
        inside.set()
        release.wait(5)
        return False

    monkeypatch.setattr(passwords, "verify_password", slow_verify)
    first = threading.Thread(target=lambda: service.attempt_login("parent", "x", "1.1.1.1"))
    first.start()
    assert inside.wait(5)
    r = login(client, password="another wrong one")
    assert r.status_code == 503 and r.headers["retry-after"] == "3"
    assert r.json() == {"detail": "busy", "retry_after": 3}
    release.set()
    first.join()
    # only the attempt that ran was recorded; the turned-away one counted against nobody
    assert db_rows("SELECT failures FROM login_attempt WHERE scope='user_ip'") == [(1,)]
    monkeypatch.undo()


def test_the_slot_is_released_after_every_attempt(user, monkeypatch):
    monkeypatch.setenv("AUTH_MAX_CONCURRENT_HASHES", "1")
    for _ in range(3):
        assert service.attempt_login("parent", "x" * 12, "1.1.1.1").kind in {"bad", "locked"}


@pytest.mark.parametrize(
    "origin,status",
    [("https://home.example", 200), ("https://evil.example", 403), ("https://other.example", 403)],
)
def test_allowed_hosts_list_overrides_proxy_headers(user, monkeypatch, origin, status):
    monkeypatch.setenv("AUTH_ALLOWED_HOSTS", "Home.example, second.example")
    local = TestClient(app, client=("127.0.0.1", 1))
    # the Host / X-Forwarded-Host the proxy sends is ignored once the list is set
    headers = {"origin": origin, "x-forwarded-host": "evil.example"}
    if origin == "https://other.example":
        headers["x-forwarded-host"] = "other.example"
    assert login(local, headers=headers).status_code == status


def test_set_password_and_enable_clear_lockouts(user, now):
    for _ in range(5):
        wrong()
    wrong(ip="2.2.2.2", name="ghost")
    assert wrong().kind == "locked"
    conn = store.connect()
    store.set_password(conn, "parent", "a brand new password")
    conn.close()
    assert service.attempt_login("parent", "a brand new password", "1.1.1.1").kind == "ok"
    # the unrelated name's rows are untouched (substr match, not LIKE)
    assert db_rows("SELECT COUNT(*) FROM login_attempt WHERE key LIKE 'ghost|%'") == [(1,)]
    for _ in range(5):
        wrong()
    conn = store.connect()
    store.set_disabled(conn, "parent", True)
    store.set_disabled(conn, "parent", False)
    conn.close()
    assert wrong().kind == "bad"


def test_clear_attempts_matches_the_exact_username_prefix(user):
    conn = store.connect()
    for name in ("al", "al_b", "alb", "a%"):
        lockout.reserve(conn, name, "1.1.1.1", clock.now())
    store.clear_attempts(conn, "al")
    left = {r[0] for r in conn.execute("SELECT key FROM login_attempt WHERE scope='user_ip'")}
    assert left == {"al_b|1.1.1.1", "alb|1.1.1.1", "a%|1.1.1.1"}
    assert store.clear_attempts(conn) > 0
    assert conn.execute("SELECT COUNT(*) FROM login_attempt").fetchone() == (0,)
    conn.close()


def test_cli_unlock_one_user_or_everything(tmp_path):
    run_cli(tmp_path, "create-user", "mama", password=PASSWORD)
    for _ in range(5):
        wrong(name="mama")
    for i in range(lockout.IP_CEILING):
        wrong(ip="7.7.7.7", name=f"u{i}")
    assert service.attempt_login("mama", PASSWORD, "1.1.1.1").kind == "locked"
    assert run_cli(tmp_path, "unlock", "mama").returncode == 0
    assert service.attempt_login("mama", PASSWORD, "1.1.1.1").kind == "ok"
    assert service.attempt_login("mama", PASSWORD, "7.7.7.7").kind == "locked"  # the address lock
    out = run_cli(tmp_path, "unlock")
    assert out.returncode == 0 and "Cleared" in out.stdout
    assert service.attempt_login("mama", PASSWORD, "7.7.7.7").kind == "ok"


def test_the_owners_known_address_is_not_held_by_the_address_ceiling(user, now):
    assert service.attempt_login("parent", PASSWORD, "5.5.5.5").kind == "ok"  # now a known pair
    for i in range(lockout.IP_CEILING):
        wrong(ip="5.5.5.5", name=f"stranger{i}")  # someone behind the same address
    assert service.attempt_login("parent", PASSWORD, "5.5.5.5").kind == "ok"
    # a name that was never used from there is held
    assert service.attempt_login("newcomer", PASSWORD, "5.5.5.5").kind == "locked"
    # the pair layer still applies to the known pair
    for _ in range(5):
        wrong(ip="5.5.5.5")
    assert wrong(ip="5.5.5.5").kind == "locked"


def test_prune_runs_at_most_once_a_minute_and_survives_a_clock_that_goes_back(user, now):
    wrong(ip="9.9.9.1", name="old")
    now.advance(lockout.QUIET_RESET_S * 2)
    wrong(ip="9.9.9.2", name="a")  # prunes: the old rows go
    assert not db_rows("SELECT 1 FROM login_attempt WHERE key LIKE 'old|%'")
    conn = store.connect()
    conn.execute(
        "INSERT INTO login_attempt (scope,key,failures,window_start,last_failure_at,locked_until)"
        " VALUES ('user_ip','stale|1.1.1.1',1,0,0,0)"
    )
    conn.close()
    now.advance(30)
    wrong(ip="9.9.9.3", name="b")  # inside the minute: no prune
    assert db_rows("SELECT 1 FROM login_attempt WHERE key='stale|1.1.1.1'")
    now.advance(31)
    wrong(ip="9.9.9.4", name="c")
    assert not db_rows("SELECT 1 FROM login_attempt WHERE key='stale|1.1.1.1'")
    now.advance(-10_000)  # the clock steps back: the next attempt prunes rather than stalling
    assert lockout._last_prune > now.t


def test_the_attempt_table_is_capped(user, now, monkeypatch):
    monkeypatch.setattr(lockout, "MAX_ROWS", 50)
    conn = store.connect()
    conn.executemany(
        "INSERT INTO login_attempt (scope,key,failures,window_start,last_failure_at,locked_until)"
        " VALUES ('user_ip',?,1,?,?,?)",
        [(f"n{i}|1.1.1.1", now.t, now.t + i, 0) for i in range(200)],
    )
    conn.execute(
        "INSERT INTO login_attempt (scope,key,failures,window_start,last_failure_at,locked_until,"
        "last_success_at) VALUES ('user_ip','keep|1.1.1.1',0,0,1,0,?)",
        (now.t,),
    )
    conn.close()
    wrong(ip="9.9.9.9", name="trigger")
    (count,) = db_rows("SELECT COUNT(*) FROM login_attempt")[0]
    assert count <= 50 + 4  # the cap, plus this attempt's own rows written after the prune
    assert db_rows("SELECT 1 FROM login_attempt WHERE key='keep|1.1.1.1'")
    assert not db_rows("SELECT 1 FROM login_attempt WHERE key='n0|1.1.1.1'")  # oldest went first


def test_create_user_refuses_an_unknown_family(tmp_path):
    r = run_cli(tmp_path, "create-user", "mama", "--family", "fam_other", password=PASSWORD)
    assert r.returncode == 1 and "No such family" in r.stderr
    assert db_rows("SELECT COUNT(*) FROM app_user") == [(0,)]


def test_validation_errors_on_auth_do_not_echo_the_input(client):
    r = client.post("/auth/login", json={"username": "u", "password": "p" * 2000})
    assert r.status_code == 422 and r.json() == {"detail": "invalid_request"}
    r = client.post("/auth/login", json={"username": "secret-name-here"})
    assert r.status_code == 422 and "secret-name-here" not in r.text
    other = client.post("/students", json={"nope": "echoed-value"})
    assert other.status_code == 422 and "detail" in other.json()  # other paths keep the default


def test_auth_bodies_over_16_kib_are_refused(client):
    big = "x" * (17 * 1024)
    r = client.post("/auth/login", content=big, headers={"content-type": "application/json"})
    assert r.status_code == 413 and r.json() == {"detail": "request_too_large"}

    def chunks():  # streamed: no Content-Length to check
        for _ in range(20):
            yield b"x" * 1024

    r = client.post("/auth/login", content=chunks(), headers={"content-type": "application/json"})
    assert r.status_code == 413
    ok = client.post("/auth/login", json={"username": "a", "password": "b"})
    assert ok.status_code == 401


def test_an_active_lock_survives_a_flood_past_the_row_cap(user, now, monkeypatch):
    monkeypatch.setattr(lockout, "MAX_ROWS", 30)
    for _ in range(5):
        wrong(ip="1.1.1.1")  # a real lock on parent|1.1.1.1
    assert wrong(ip="1.1.1.1").kind == "locked"
    conn = store.connect()
    conn.executemany(
        "INSERT INTO login_attempt (scope,key,failures,window_start,last_failure_at,locked_until)"
        " VALUES ('user_ip',?,1,?,?,0)",
        [(f"flood{i}|9.9.9.9", now.t, now.t + i + 1) for i in range(200)],
    )
    conn.close()
    monkeypatch.setattr(lockout, "_last_prune", float("-inf"))  # let the prune run now
    wrong(ip="2.2.2.2", name="other")
    assert db_rows("SELECT COUNT(*) FROM login_attempt WHERE key LIKE 'flood%'")[0][0] < 200
    assert db_rows(
        "SELECT 1 FROM login_attempt WHERE key='parent|1.1.1.1' AND locked_until>?", now.t
    )
    assert wrong(ip="1.1.1.1").kind == "locked"


def test_the_prune_delete_uses_the_locked_until_index():
    plan = " ".join(
        str(r)
        for r in db_rows(
            "EXPLAIN QUERY PLAN DELETE FROM login_attempt WHERE locked_until < ? "
            "AND COALESCE(last_failure_at, 0) < ? AND (last_success_at IS NULL OR last_success_at < ?)",
            1,
            1,
            1,
        )
    )
    assert "idx_login_attempt_locked" in plan


def test_only_a_few_sign_ins_wait_and_the_rest_are_turned_away_at_once(user, monkeypatch):
    import threading

    monkeypatch.setenv("AUTH_MAX_CONCURRENT_HASHES", "2")
    monkeypatch.setattr(service, "BUSY_WAIT_S", 5.0)
    release = threading.Event()
    inside = 0
    peak = 0
    guard = threading.Lock()

    def slow_verify(*args):
        nonlocal inside, peak
        with guard:
            inside += 1
            peak = max(peak, inside)
        release.wait(10)
        with guard:
            inside -= 1
        return False

    monkeypatch.setattr(passwords, "verify_password", slow_verify)
    results = []

    def attempt(i):
        results.append(service.attempt_login("parent", "x", f"3.3.3.{i}").kind)

    threads = [threading.Thread(target=attempt, args=(i,)) for i in range(30)]
    for t in threads:
        t.start()
    # 2 running + 4 waiting = 6 are inside; the other 24 answer "busy" immediately
    deadline = time.time() + 5
    while results.count("busy") < 24 and time.time() < deadline:
        time.sleep(0.01)
    assert results.count("busy") == 24
    assert service._waiting == service.MAX_WAITERS
    release.set()
    for t in threads:
        t.join(10)
    assert peak <= 2 and sorted(set(results)) == ["bad", "busy"] and results.count("bad") == 6
    # nothing was recorded for the 24 turned away
    assert db_rows("SELECT COUNT(*) FROM login_attempt WHERE scope='user_ip'") == [(6,)]
    assert service._waiting == 0
