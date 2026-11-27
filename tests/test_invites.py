"""Invite codes: the store, the CLI, POST /admin-api/invites and the email_verified_at backfill."""

from __future__ import annotations

import os
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import db_utils  # noqa: E402
from auth import clock, passwords, store  # noqa: E402
from migrations import MIGRATIONS_DIR, apply_migrations  # noqa: E402

PW = "correct horse battery"
CODE_RE = re.compile(r"^[ABCDEFGHJKMNPQRSTVWXYZ23456789]{10}$")


@pytest.fixture(autouse=True)
def env(tmp_path, monkeypatch):
    db = tmp_path / "inv.db"
    monkeypatch.setenv("CURRICULUM_DB_PATH", str(db))
    monkeypatch.setattr(db_utils, "DB_FILE", str(db))
    monkeypatch.setattr(passwords, "CURRENT", passwords.ScryptParams(n=2**10, r=8, p=1))
    apply_migrations(db)
    yield db
    clock.set_source(None)


@pytest.fixture
def conn():
    c = store.connect()
    yield c
    c.close()


def test_code_has_the_alphabet_and_length(conn):
    codes = {store.create_invite(conn, None)[0] for _ in range(20)}
    assert len(codes) == 20 and all(CODE_RE.match(c) for c in codes)


def test_consume_works_once(conn):
    user = store.create_user(conn, "ana", PW)
    code, _ = store.create_invite(conn, user.id)
    assert store.consume_invite(conn, code, user.id) is True
    assert store.consume_invite(conn, code, user.id) is False
    assert store.consume_invite(conn, "NOSUCHCODE", user.id) is False


def test_expired_code_is_refused(conn):
    user = store.create_user(conn, "ana", PW)
    code, expires = store.create_invite(conn, user.id, days=1)
    assert expires == conn.execute("SELECT expires_at FROM invite").fetchone()[0]
    clock.set_source(lambda: __import__("time").time() + 2 * 86400)
    assert store.consume_invite(conn, code, user.id) is False


def test_only_a_hash_is_stored(conn):
    code, _ = store.create_invite(conn, None)
    dump = repr(conn.execute("SELECT * FROM invite").fetchall())
    assert code not in dump
    assert conn.execute("SELECT code_hash FROM invite").fetchone() == (store.token_hash(code),)


def _cli(db, *args):
    e = {**os.environ, "CURRICULUM_DB_PATH": str(db), "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "auth", *args], cwd=ROOT / "src", env=e,
        capture_output=True, text=True, stdin=subprocess.DEVNULL,
    )  # fmt: skip


def test_cli_prints_one_code(env):
    r = _cli(env, "invite", "--days", "3")
    assert r.returncode == 0, r.stderr
    lines = r.stdout.split()
    codes = [w for w in lines if CODE_RE.match(w)]
    assert len(codes) == 1
    row = sqlite3.connect(env).execute("SELECT code_hash FROM invite").fetchall()
    assert row == [(store.token_hash(codes[0]),)]


def _signed_in(username):
    from main import app

    c = TestClient(app)
    assert c.post("/auth/login", json={"username": username, "password": PW}).status_code == 200
    return c


def test_admin_api_is_admin_only(conn, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "1")
    store.create_user(conn, "parent", PW)
    admin = store.create_user(conn, "boss", PW)
    store.grant(conn, "boss", "admin")
    r = _signed_in("parent").post("/admin-api/invites")
    assert r.status_code == 404 and r.json() == {"detail": "Not Found"}
    assert conn.execute("SELECT COUNT(*) FROM invite").fetchone() == (0,)
    r = _signed_in("boss").post("/admin-api/invites")
    assert r.status_code == 200
    body = r.json()
    assert CODE_RE.match(body["code"]) and body["expires_at"]
    assert conn.execute("SELECT created_by FROM invite").fetchone() == (admin.id,)


def test_existing_users_are_backfilled_verified(tmp_path):
    db = tmp_path / "old.db"
    older = tmp_path / "m"
    older.mkdir()
    for p in MIGRATIONS_DIR.glob("*.sql"):
        if not p.name.startswith("0013"):
            shutil.copy(p, older)
    apply_migrations(db, older)
    c = sqlite3.connect(db)
    c.execute(
        "INSERT INTO app_user (id, username, password_hash, family_id, created_at) "
        "VALUES ('u1','old','x','fam_local','2025-01-02T03:04:05+00:00')"
    )
    c.commit()
    c.close()
    apply_migrations(db)
    got = sqlite3.connect(db).execute("SELECT email_verified_at FROM app_user").fetchone()
    assert got == ("2025-01-02T03:04:05+00:00",)
