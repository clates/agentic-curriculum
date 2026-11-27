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
def make_invite(
    request: Request,
    _family: str = Depends(current_family),  # unused: test_every_route_declares_its_family
):
    """Make an invite code. The plain code is in this response only; the database keeps a hash."""
    user = getattr(request.state, "user", None)  # None with login off
    conn = store.connect()
    try:
        code, expires = store.create_invite(conn, user.id if user else None)
    finally:
        conn.close()
    return {"code": code, "expires_at": datetime.fromtimestamp(expires, UTC).isoformat()}
