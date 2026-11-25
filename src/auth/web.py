"""FastAPI side: the global gate, the /auth routes, client IP, cookie and origin handling."""

from __future__ import annotations

import ipaddress
import os
from collections.abc import Callable
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import registration, service, store

COOKIE_NAME = "curriculum_session"
CLIENT_IP_HEADER = "x-curriculum-client-ip"
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Reachable without a session. Each one has a reason:
#   /auth/login   you have no session yet
#   /auth/logout  harmless and must work with a stale cookie
#   /auth/register, /auth/verify, /auth/resend  signing up happens before there is an account
#   /health       the container healthcheck and deploy.sh poll it through the app (/api/health)
#   /version      the version footer on the login page, and deploy checks
PUBLIC_PATHS = frozenset(
    {"/auth/login", "/auth/logout", "/auth/register", "/auth/verify", "/auth/resend", "/health",
     "/version"}
)  # fmt: skip


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


def _allowed_hosts() -> set[str]:
    raw = os.environ.get("AUTH_ALLOWED_HOSTS", "")
    return {h.strip().lower() for h in raw.split(",") if h.strip()}


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
    allowed = _allowed_hosts()
    # With AUTH_ALLOWED_HOSTS set, only those hosts count and proxy headers are not consulted.
    if host not in allowed if allowed else host != _own_host(request):
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


def current_family(request: Request) -> str:
    """The caller's family: fam_local with login off, otherwise the session user's."""
    return request.state.user.family_id if auth_required() else store.DEFAULT_FAMILY


def user_permissions(request: Request) -> frozenset[str]:
    """Every permission with login off; otherwise read from the store on each request."""
    if not auth_required():
        return store.PERMISSIONS
    conn = store.connect()
    try:
        return store.permissions(conn, request.state.user.id)
    finally:
        conn.close()


def require_permission(permission: str) -> Callable:
    """Dependency: 404 (not 403, so the route's existence is not revealed) without the permission."""

    def check(request: Request) -> None:
        if permission not in user_permissions(request):
            raise HTTPException(404, "Not Found")

    return check


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginBody(BaseModel):
    username: str = Field(max_length=store.USERNAME_MAX)
    password: str = Field(max_length=1024)


def _held_back(result) -> JSONResponse | None:
    """429 for a lockout, 503 when too many password checks are running; else None."""
    status = {"locked": (429, "too_many_attempts"), "busy": (503, "busy")}.get(result.kind)
    if status is None:
        return None
    return JSONResponse(
        {"detail": status[1], "retry_after": result.retry_after},
        status_code=status[0],
        headers={"Retry-After": str(result.retry_after)},
    )


def _mail_later(mail: tuple[str, str] | None) -> None:
    """Mail goes out on its own thread, so its timing says nothing about the account."""
    if mail:
        registration.send_later(*mail)


@router.post("/login")
def login(body: LoginBody, request: Request, response: Response):
    result = service.attempt_login(
        body.username, body.password, client_ip(request), request.headers.get("user-agent")
    )
    if held := _held_back(result):
        return held
    if result.kind == "unverified" and result.user:
        _mail_later(registration.issue_code(result.user.username))
        return JSONResponse({"detail": "email_not_verified"}, status_code=403)
    if result.kind != "ok" or not result.token or not result.user:
        raise HTTPException(401, "invalid_credentials")
    set_session_cookie(response, request, result.token)
    return {"user": {"username": result.user.username}}


CHECK_EMAIL = {"status": "check_email"}


class RegisterBody(BaseModel):
    email: str = Field(max_length=320)
    password: str = Field(max_length=1024)
    family_name: str = Field(max_length=200)
    invite_code: str = Field(max_length=64)


@router.post("/register", status_code=202)
def register(body: RegisterBody, request: Request):
    try:
        result = registration.register(
            body.email, body.password, body.family_name, body.invite_code, client_ip(request)
        )
    except registration.RegistrationError as exc:
        raise HTTPException(400, str(exc)) from None
    if held := _held_back(result):
        return held
    if result.kind != "ok":
        raise HTTPException(400, "invalid_invite")
    _mail_later(result.mail)
    return CHECK_EMAIL


class VerifyBody(BaseModel):
    email: str = Field(max_length=320)
    code: str = Field(max_length=32)
    password: str = Field(max_length=1024)


@router.post("/verify")
def verify(body: VerifyBody, request: Request, response: Response):
    result = registration.verify(
        body.email,
        body.code,
        body.password,
        client_ip(request),
        request.headers.get("user-agent"),
    )
    if held := _held_back(result):
        return held
    if result.kind != "ok" or not result.token or not result.user:
        raise HTTPException(400, "invalid_code")
    set_session_cookie(response, request, result.token)
    return {"user": {"username": result.user.username}}


class ResendBody(BaseModel):
    email: str = Field(max_length=320)


@router.post("/resend", status_code=202)
def resend(body: ResendBody):
    _mail_later(registration.issue_code(body.email))
    return CHECK_EMAIL


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
    permissions = sorted(user_permissions(request))
    if not auth_required():
        return {"auth_required": False, "user": None, "permissions": permissions}
    user = request.state.user
    return {"auth_required": True, "user": {"username": user.username}, "permissions": permissions}


# --- request size and validation errors on /auth/* -------------------------------------------

AUTH_BODY_MAX = 16 * 1024


class AuthBodyLimit:
    """Pure ASGI: /auth/* bodies over 16 KiB get 413 (Content-Length first, then streamed bytes)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope["path"].startswith("/auth/"):
            return await self.app(scope, receive, send)
        declared = dict(scope["headers"]).get(b"content-length")
        too_big = JSONResponse({"detail": "request_too_large"}, status_code=413)
        if declared is not None and declared.isdigit() and int(declared) > AUTH_BODY_MAX:
            return await too_big(scope, receive, send)
        seen = 0
        refused = False

        async def counting_receive():
            nonlocal seen, refused
            if refused:
                return {"type": "http.disconnect"}
            message = await receive()
            if message["type"] == "http.request":
                seen += len(message.get("body", b""))
                if seen > AUTH_BODY_MAX:
                    refused = True  # stop feeding the app; whatever it answers is replaced
                    return {"type": "http.disconnect"}
            return message

        async def guarded_send(message):
            if not refused:
                await send(message)

        try:
            await self.app(scope, counting_receive, guarded_send)
        except Exception:
            if not refused:
                raise
        if refused:
            await too_big(scope, receive, send)


async def invalid_request_handler(request: Request, exc):
    """422 without echoing what was submitted (a mistyped password must not come back)."""
    from fastapi.exception_handlers import request_validation_exception_handler

    if request.url.path.startswith("/auth/"):
        return JSONResponse({"detail": "invalid_request"}, status_code=422)
    return await request_validation_exception_handler(request, exc)
