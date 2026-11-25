"""Families and the user_permission table: store functions and the grant/revoke CLI."""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import db_utils  # noqa: E402
from auth import passwords, store  # noqa: E402
from migrations import apply_migrations  # noqa: E402

PW = "correct horse battery"


@pytest.fixture(autouse=True)
def env(tmp_path, monkeypatch):
    db = tmp_path / "perm.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    monkeypatch.setattr(db_utils, "DB_FILE", str(db))
    monkeypatch.setattr(passwords, "CURRENT", passwords.ScryptParams(n=2**10, r=8, p=1))
    apply_migrations(db)
    return db


@pytest.fixture
def conn():
    c = store.connect()
    yield c
    c.close()


def test_create_family_and_user_in_it(conn):
    fid = store.create_family(conn, "Rivera")
    assert fid.startswith("fam_") and len(fid) == len("fam_") + 12
    assert store.create_user(conn, "ana", PW, fid).family_id == fid


def test_unknown_family_is_refused(conn):
    with pytest.raises(store.UserError, match="No such family"):
        store.create_user(conn, "ana", PW, "fam_nope")


def test_grant_revoke_and_read(conn):
    user = store.create_user(conn, "ana", PW)
    assert store.permissions(conn, user.id) == frozenset()
    assert store.grant(conn, "ana", "admin") is True
    assert store.grant(conn, "ana", "admin") is True  # idempotent
    assert store.permissions(conn, user.id) == {"admin"}
    assert conn.execute("SELECT COUNT(*) FROM user_permission").fetchone() == (1,)
    assert store.revoke(conn, "ana", "admin") is True
    assert store.permissions(conn, user.id) == frozenset()
    with pytest.raises(store.UserError):
        store.grant(conn, "ana", "root")
    assert store.grant(conn, "ghost", "admin") is False
    assert store.revoke(conn, "ghost", "admin") is False


def test_permissions_vanish_with_the_user(conn):
    user = store.create_user(conn, "ana", PW)
    store.grant(conn, "ana", "admin")
    conn.execute("DELETE FROM app_user WHERE id=?", (user.id,))
    assert conn.execute("SELECT COUNT(*) FROM user_permission").fetchone() == (0,)


def _cli(db, *args):
    env = {**os.environ, "CURRICULUM_DB_PATH": str(db), "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "auth", *args], cwd=ROOT / "src", env=env,
        capture_output=True, text=True, stdin=subprocess.DEVNULL,
    )  # fmt: skip


def test_cli_grant_and_revoke(env, conn):
    store.create_user(conn, "ana", PW)
    assert _cli(env, "grant", "ana", "admin").returncode == 0
    rows = sqlite3.connect(env).execute("SELECT permission FROM user_permission").fetchall()
    assert rows == [("admin",)]
    assert _cli(env, "revoke", "ana", "admin").returncode == 0
    assert sqlite3.connect(env).execute("SELECT COUNT(*) FROM user_permission").fetchone() == (0,)
    r = _cli(env, "grant", "ghost", "admin")
    assert r.returncode == 1 and "No such user" in r.stderr
    assert _cli(env, "revoke", "ghost", "admin").returncode == 1


def test_cli_list_users_shows_family_disabled_and_permissions(env, conn):
    fid = store.create_family(conn, "Rivera")
    ana = store.create_user(conn, "ana", PW)
    store.create_user(conn, "bo", PW, fid)
    store.grant(conn, "ana", "admin")
    store.set_disabled(conn, "bo", True)
    r = _cli(env, "list-users")
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines() == [
        "ana\tfam_local\tenabled\tadmin",
        f"bo\t{fid}\tdisabled\t-",
    ]
    assert ana.password_hash not in r.stdout and "scrypt" not in r.stdout


# --- request dependencies ------------------------------------------------------------------


@pytest.fixture
def web_client():
    """A small app with the real gate and /auth routes plus throwaway routes for the dependencies."""
    from fastapi import Depends, FastAPI
    from fastapi.testclient import TestClient

    from auth.web import auth_gate, current_family, require_permission
    from auth.web import router as auth_router

    app = FastAPI(dependencies=[Depends(auth_gate)])
    app.include_router(auth_router)

    @app.get("/t/family")
    def family(fid: str = Depends(current_family)):
        return {"family": fid}

    @app.get("/t/admin", dependencies=[Depends(require_permission("admin"))])
    def admin_only():
        return {"ok": True}

    return TestClient(app)


def _login(c, username="ana"):
    assert c.post("/auth/login", json={"username": username, "password": PW}).status_code == 200


def test_me_reports_permissions_when_login_off(web_client, monkeypatch):
    monkeypatch.delenv("AUTH_REQUIRED", raising=False)
    assert web_client.get("/auth/me").json() == {
        "auth_required": False,
        "user": None,
        "permissions": ["admin"],
    }
    assert web_client.get("/t/admin").status_code == 200


def test_me_reports_permissions_when_login_on(web_client, conn, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "1")
    store.create_user(conn, "ana", PW)
    _login(web_client)
    assert web_client.get("/auth/me").json()["permissions"] == []
    store.grant(conn, "ana", "admin")
    assert web_client.get("/auth/me").json()["permissions"] == ["admin"]


def test_revoke_takes_effect_on_the_next_request(web_client, conn, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "1")
    store.create_user(conn, "ana", PW)
    assert store.grant(conn, "ana", "admin")
    _login(web_client)
    assert web_client.get("/t/admin").status_code == 200
    store.revoke(conn, "ana", "admin")
    r = web_client.get("/t/admin")
    assert (r.status_code, r.json()) == (404, {"detail": "Not Found"})


def test_current_family_follows_the_session(web_client, conn, monkeypatch):
    fid = store.create_family(conn, "Rivera")
    store.create_user(conn, "ana", PW, fid)
    monkeypatch.setenv("AUTH_REQUIRED", "1")
    _login(web_client)
    assert web_client.get("/t/family").json() == {"family": fid}
    monkeypatch.delenv("AUTH_REQUIRED")
    assert web_client.get("/t/family").json() == {"family": "fam_local"}
