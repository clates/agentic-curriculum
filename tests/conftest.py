"""Test configuration for agentic-curriculum."""

from pathlib import Path
import socket
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Hermetic-test guardrails: no test may ever reach a real LLM or any external service.
#
# 1. Env: every test starts with a fake OpenAI key and LLM/ntfy endpoints that point at an
#    unroutable local port, so an unmocked call fails fast and locally. A test that needs
#    other values sets its own (monkeypatch.setenv / os.environ) and that wins for the test.
# 2. Sockets: connecting to (or resolving) anything that is not loopback raises immediately,
#    regardless of which library or env var a future code path uses.
# ---------------------------------------------------------------------------

UNROUTABLE_LOCAL_URL = "http://127.0.0.1:9"  # discard port: nothing listens, refused instantly
_LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0", "", None}


class ExternalNetworkBlocked(RuntimeError):
    """Raised when a test tries to talk to a non-loopback host."""


def _assert_loopback(host) -> None:
    if isinstance(host, bytes):
        host = host.decode()
    if host in _LOOPBACK_HOSTS or (isinstance(host, str) and host.startswith("127.")):
        return
    raise ExternalNetworkBlocked(
        f"Tests must not touch the network: attempted to reach {host!r}. "
        "Mock the call or point it at a local stub."
    )


@pytest.fixture(autouse=True)
def _hermetic_network(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "pytest-not-a-real-key")
    monkeypatch.setenv("OPENAI_BASE_URL", f"{UNROUTABLE_LOCAL_URL}/v1")
    monkeypatch.setenv("OPENAI_MODEL", "pytest-stub")
    monkeypatch.setenv("NTFY_URL", f"{UNROUTABLE_LOCAL_URL}/ntfy")

    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex
    real_getaddrinfo = socket.getaddrinfo

    def guarded_connect(self, address):
        if self.family in (socket.AF_INET, socket.AF_INET6):
            _assert_loopback(address[0])
        return real_connect(self, address)

    def guarded_connect_ex(self, address):
        if self.family in (socket.AF_INET, socket.AF_INET6):
            _assert_loopback(address[0])
        return real_connect_ex(self, address)

    def guarded_getaddrinfo(host, *args, **kwargs):
        _assert_loopback(host)
        return real_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
    yield
