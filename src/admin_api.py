"""Admin tools (``/admin-api/*``): behind the login gate, 404 without the ``admin`` permission."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request

from auth import store
from auth.web import current_family, require_permission

router = APIRouter(
    prefix="/admin-api", tags=["admin-api"], dependencies=[Depends(require_permission("admin"))]
)


@router.post("/invites")
def make_invite(request: Request, _family: str = Depends(current_family)):
    """Make an invite code. The plain code is in this response only; the database keeps a hash."""
    user = getattr(request.state, "user", None)  # None with login off
    conn = store.connect()
    try:
        code = store.create_invite(conn, user.id if user else None)
        (expires,) = conn.execute(
            "SELECT expires_at FROM invite WHERE code_hash=?", (store.token_hash(code),)
        ).fetchone()
    finally:
        conn.close()
    return {"code": code, "expires_at": datetime.fromtimestamp(expires, UTC).isoformat()}
