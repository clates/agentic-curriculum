"""FastAPI side: the global gate, the /auth routes, client IP, cookie and origin handling."""

from __future__ import annotations

import ipaddress
import os
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import service, store

COOKIE_NAME = "curriculum_session"
CLIENT_IP_HEADER = "x-curriculum-client-ip"
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Reachable without a session. Each one has a reason:
#   /auth/login   you have no session yet
#   /auth/logout  harmless and must work with a stale cookie
#   /health       the container healthcheck and deploy.sh poll it through the app (/api/health)
#   /version      the version footer on the login page, and deploy checks
PUBLIC_PATHS = frozenset({"/auth/login", "/auth/logout", "/health", "/version"})


def auth_required() -> bool:
    return os.environ.get("AUTH_REQUIRED", "").strip().lower() in {"1", "true", "yes", "on"}


def _is_loopback(host: str | None) -> bool:
    try:
        return bool(host) and ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host == "localhost"


def client_ip(request: Request) -> str:
    """The caller's address. The Next proxy runs on this machine and forwards the real client in
    a header; that header is trusted ONLY when the connection itself is from loopback."""
    peer = request.client.host if request.client else "unknown"
    if _is_loopback(peer):
        claimed = request.headers.get(CLIENT_IP_HEADER, "").strip()
        try:
            return str(ipaddress.ip_address(claimed))
        except ValueError:
            pass
    return peer


def _trusted_proxy(request: Request) -> bool:
    return request.client is not None and _is_loopback(request.client.host)


def _is_https(request: Request) -> bool:
    if os.environ.get("COOKIE_SECURE", "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    if _trusted_proxy(request):
        return request.headers.get("x-forwarded-proto", "").split(",")[0].strip() == "https"
    return request.url.scheme == "https"


def _own_host(request: Request) -> str:
    if _trusted_proxy(request) and request.headers.get("x-forwarded-host"):
        return request.headers["x-forwarded-host"].split(",")[0].strip().lower()
    return request.headers.get("host", "").strip().lower()


def check_origin(request: Request) -> None:
    """CSRF: a state-changing request from a browser must come from this site.

    Browsers always send Origin on cross-site POSTs. Present and not our host (or the literal
    "null") is refused; Sec-Fetch-Site: cross-site is refused; no Origin and no Referer means a
    non-browser client, which cannot be riding a victim's cookie. SameSite=Lax on the cookie is
    the second layer."""
    if request.headers.get("sec-fetch-site", "").lower() == "cross-site":
        raise HTTPException(403, "bad_origin")
    source = request.headers.get("origin") or request.headers.get("referer")
    if not source:
        return
    host = (urlsplit(source).netloc or "").lower() if source != "null" else ""
    if host != _own_host(request):
        raise HTTPException(403, "bad_origin")


def set_session_cookie(response: Response, request: Request, token: str) -> None:
    response.set_cookie(
        COOKIE_NAME, token, max_age=store.SESSION_LIFETIME_S, path="/", httponly=True,
        samesite="lax", secure=_is_https(request),
    )  # fmt: skip


def clear_session_cookie(response: Response, request: Request) -> None:
    response.delete_cookie(
        COOKIE_NAME, path="/", httponly=True, samesite="lax", secure=_is_https(request)
    )


def _unauthenticated(request: Request, had_cookie: bool) -> HTTPException:
    headers = {}
    if had_cookie:  # a stale cookie: tell the browser to drop it
        cleared = Response()
        clear_session_cookie(cleared, request)
        headers["set-cookie"] = cleared.headers["set-cookie"]
    return HTTPException(401, "not_authenticated", headers=headers)


def auth_gate(request: Request, response: Response) -> None:
    """Global dependency: every route needs a session unless it is on PUBLIC_PATHS.

    Does nothing unless AUTH_REQUIRED is on (self-hosting, dev, CI), except that /auth/* routes
    always get the origin check."""
    route = request.scope.get("route")
    path = getattr(route, "path", None) or request.url.path
    enforcing = auth_required()
    if request.method in UNSAFE_METHODS and (enforcing or path.startswith("/auth/")):
        check_origin(request)
    if not enforcing or path in PUBLIC_PATHS:
        return
    token = request.cookies.get(COOKIE_NAME)
    conn = store.connect()
    try:
        found = store.resolve_session(conn, token)
    finally:
        conn.close()
    if found is None:
        raise _unauthenticated(request, bool(token))
    user, refreshed = found
    request.state.user = user
    if refreshed and token:
        set_session_cookie(response, request, token)


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginBody(BaseModel):
    username: str = Field(max_length=store.USERNAME_MAX)
    password: str = Field(max_length=1024)


@router.post("/login")
def login(body: LoginBody, request: Request, response: Response):
    result = service.attempt_login(
        body.username, body.password, client_ip(request), request.headers.get("user-agent")
    )
    if result.kind == "locked":
        return JSONResponse(
            {"detail": "too_many_attempts", "retry_after": result.retry_after},
            status_code=429,
            headers={"Retry-After": str(result.retry_after)},
        )
    if result.kind != "ok" or not result.token or not result.user:
        raise HTTPException(401, "invalid_credentials")
    set_session_cookie(response, request, result.token)
    return {"user": {"username": result.user.username}}


@router.post("/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE_NAME)
    conn = store.connect()
    try:
        store.delete_session(conn, token)
    finally:
        conn.close()
    clear_session_cookie(response, request)
    return {"ok": True}


@router.get("/me")
def me(request: Request):
    if not auth_required():
        return {"auth_required": False, "user": None}
    user = request.state.user
    return {"auth_required": True, "user": {"username": user.username}}
