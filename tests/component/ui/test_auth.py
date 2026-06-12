"""Component tests for src/ui/auth.py (AST-394)."""

from __future__ import annotations

import pytest
from flask import Flask

from ui import auth as auth_mod


@pytest.fixture
def flask_app() -> Flask:
    app = Flask(__name__)

    @app.route("/open")
    @auth_mod.require_ip
    def open_route():
        return {"ok": True}

    @app.route("/secure")
    @auth_mod.require_auth
    def secure_route():
        return {"ok": True}

    return app


# Branches: open allowlist; blocked IP; bearer required.
class TestAuthDecorators:
    def test_open_route_allows_without_token(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", set())
        client = flask_app.test_client()
        assert client.get("/open").status_code == 200

    def test_open_route_blocks_disallowed_ip(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", {"203.0.113.1"})
        client = flask_app.test_client()
        assert client.get("/open", environ_base={"REMOTE_ADDR": "198.51.100.2"}).status_code == 403

    def test_secure_route_requires_bearer(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", set())
        client = flask_app.test_client()
        assert client.get("/secure").status_code == 401
        assert client.get("/secure", headers={"Authorization": "Bearer test"}).status_code == 200

    def test_secure_route_blocks_disallowed_ip(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", {"203.0.113.1"})
        client = flask_app.test_client()
        assert client.get("/secure", headers={"Authorization": "Bearer test"}, environ_base={"REMOTE_ADDR": "198.51.100.2"}).status_code == 403


class TestClientIp:
    def test_prefers_forwarded_for_header(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(headers={"X-Forwarded-For": "203.0.113.5, 198.51.100.2"}):
            assert auth_mod.get_client_ip() == "203.0.113.5"


class TestAllowedIps:
    def test_loads_allowlist_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        auth_mod._ALLOWED_IPS = set()
        monkeypatch.setenv("ASTRAL_ALLOWED_IPS", "203.0.113.1, 198.51.100.2")
        assert auth_mod._load_allowed_ips() == {"203.0.113.1", "198.51.100.2"}

    def test_allows_configured_client_ip(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        auth_mod._ALLOWED_IPS = set()
        monkeypatch.setenv("ASTRAL_ALLOWED_IPS", "203.0.113.1")
        with flask_app.test_request_context(environ_base={"REMOTE_ADDR": "203.0.113.1"}):
            assert auth_mod.is_ip_allowed() is True
