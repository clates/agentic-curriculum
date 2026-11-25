"""Server-side account commands. There is no public signup; this is how accounts are made.

    python -m auth create-user <username> [--family fam_local]
    python -m auth set-password <username>
    python -m auth disable <username>
    python -m auth enable <username>
    python -m auth grant <username> <permission>     (permission: admin)
    python -m auth revoke <username> <permission>
    python -m auth unlock [<username>]   (no name: forget every lockout, addresses included)
    python -m auth invite [--days N]     (prints a one-time invite code, valid 14 days by default)
    python -m auth list-users            (username, family, disabled, permissions; no hashes)

`--family` takes any existing family id.

The password comes from the AUTH_NEW_PASSWORD environment variable or a hidden prompt, never a
command-line argument (arguments show up in process lists and shell history).
"""

from __future__ import annotations

import argparse
import getpass
import os
import sys

from db_utils import get_db_path
from migrations import apply_migrations

from . import store
from .passwords import PasswordError


def _password(confirm: bool) -> str:
    env = os.environ.get("AUTH_NEW_PASSWORD")
    if env:
        return env
    first = getpass.getpass("Password (at least 12 characters): ")
    if confirm and getpass.getpass("Again: ") != first:
        raise SystemExit("The two passwords differ. Nothing was changed.")
    return first


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m auth",
        description=__doc__.split("\n")[0],
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    create = sub.add_parser("create-user", help="make an account (does nothing if it exists)")
    create.add_argument("username")
    create.add_argument(
        "--family",
        default=store.DEFAULT_FAMILY,
        help="the id of an existing family",
    )
    sub.add_parser("unlock", help="forget lockouts: one user's, or all of them").add_argument(
        "username", nargs="?"
    )
    sub.add_parser("invite", help="make an invite code (shown once)").add_argument(
        "--days", type=int, default=store.INVITE_DAYS
    )
    sub.add_parser("list-users", help="one line per user: family, disabled, permissions")
    for name in ("grant", "revoke"):
        p = sub.add_parser(name, help=f"{name} a permission")
        p.add_argument("username")
        p.add_argument("permission")
    for name in ("set-password", "disable", "enable"):
        sub.add_parser(name).add_argument("username")
    args = parser.parse_args(argv)

    apply_migrations(get_db_path())
    conn = store.connect()
    try:
        if args.cmd == "create-user":
            if store.get_user(conn, args.username):
                print(f"User '{store.normalize_username(args.username)}' already exists.")
                return 0
            try:
                user = store.create_user(conn, args.username, _password(True), args.family)
            except (PasswordError, store.UserError) as err:
                print(f"Not created: {err}", file=sys.stderr)
                return 1
            print(f"Created user '{user.username}' in family {user.family_id}.")
        elif args.cmd == "set-password":
            try:
                done = store.set_password(conn, args.username, _password(True))
            except PasswordError as err:
                print(f"Not changed: {err}", file=sys.stderr)
                return 1
            if not done:
                print("No such user.", file=sys.stderr)
                return 1
            print("Password changed. Every session for this user was signed out.")
        elif args.cmd in ("grant", "revoke"):
            try:
                done = getattr(store, args.cmd)(conn, args.username, args.permission)
            except store.UserError as err:
                print(f"Not changed: {err}", file=sys.stderr)
                return 1
            if not done:
                print("No such user.", file=sys.stderr)
                return 1
            print(f"{args.cmd.capitalize()}: {args.permission} for {args.username}.")
        elif args.cmd == "invite":
            code = store.create_invite(conn, None, args.days)
            print(f"Invite code (shown once, valid {args.days} days): {code}")
        elif args.cmd == "list-users":
            rows = conn.execute(
                "SELECT u.username, u.family_id, u.disabled, group_concat(p.permission) "
                "FROM app_user u LEFT JOIN user_permission p ON p.user_id = u.id "
                "GROUP BY u.id ORDER BY u.username"
            ).fetchall()
            for username, family_id, disabled, perms in rows:
                flag = "disabled" if disabled else "enabled"
                perms = ",".join(sorted(perms.split(","))) if perms else "-"
                print(f"{username}\t{family_id}\t{flag}\t{perms}")
        elif args.cmd == "unlock":
            removed = store.clear_attempts(conn, args.username)
            print(f"Cleared {removed} lockout record(s).")
        else:
            disabled = args.cmd == "disable"
            if not store.set_disabled(conn, args.username, disabled):
                print("No such user.", file=sys.stderr)
                return 1
            print(f"User {'disabled' if disabled else 'enabled'}.")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
