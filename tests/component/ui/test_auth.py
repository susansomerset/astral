"""Component tests for src/ui/auth.py (AST-394, AST-611)."""

from __future__ import annotations

import pytest
from flask import Flask, g

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
        return {"ok": True, "user_id": g.user.get("user_id"), "is_admin": g.user.get("is_admin")}

    @app.route("/admin-only")
    @auth_mod.require_admin
    def admin_route():
        return {"ok": True}

    return app


# Branches: require_ip open/blocked IP.
class TestRequireIp:
    def test_open_route_allows_without_token(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", set())
        client = flask_app.test_client()
        assert client.get("/open").status_code == 200

    def test_open_route_blocks_disallowed_ip(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", {"203.0.113.1"})
        client = flask_app.test_client()
        assert client.get("/open", environ_base={"REMOTE_ADDR": "198.51.100.2"}).status_code == 403


# Branches: missing/invalid Bearer; valid JWT; IP not checked on require_auth.
class TestRequireAuth:
    def test_missing_bearer_returns_401(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", set())
        assert flask_app.test_client().get("/secure").status_code == 401

    def test_invalid_authorization_header_returns_401(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", set())
        client = flask_app.test_client()
        assert client.get("/secure", headers={"Authorization": "Basic x"}).status_code == 401

    def test_invalid_token_returns_401(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", set())
        assert (
            flask_app.test_client().get("/secure", headers={"Authorization": "Bearer bad"}).status_code == 401
        )

    def test_valid_token_sets_g_user_fields(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", set())
        from src.utils import auth as utils_auth

        monkeypatch.setattr(
            utils_auth,
            "AUTH_CONFIG",
            {"admin_user_ids": frozenset(), "admin_emails": frozenset()},
            raising=False,
        )
        resp = flask_app.test_client().get("/secure", headers={"Authorization": "Bearer good-jwt"})
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["user_id"] == "u1"
        assert payload["is_admin"] is False

    def test_valid_stytch_jwt_cookie_sets_g_user_fields(
        self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", set())
        client = flask_app.test_client()
        client.set_cookie("stytch_session_jwt", "good-jwt")
        resp = client.get("/secure")
        assert resp.status_code == 200
        assert resp.get_json()["user_id"] == "u1"

    def test_require_auth_ignores_ip_allowlist_with_valid_bearer(
        self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", {"203.0.113.1"})
        resp = flask_app.test_client().get(
            "/secure",
            headers={"Authorization": "Bearer good-jwt"},
            environ_base={"REMOTE_ADDR": "198.51.100.2"},
        )
        assert resp.status_code == 200


# Branches: non-admin 403; admin 200.
class TestRequireAdmin:
    def test_non_admin_returns_403(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", set())
        resp = flask_app.test_client().get("/admin-only", headers={"Authorization": "Bearer non-admin-jwt"})
        assert resp.status_code == 403

    def test_admin_returns_200(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(auth_mod, "_ALLOWED_IPS", set())
        resp = flask_app.test_client().get("/admin-only", headers={"Authorization": "Bearer test-token"})
        assert resp.status_code == 200


class TestClientIp:
    def test_prefers_forwarded_for_header(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(headers={"X-Forwarded-For": "203.0.113.5, 198.51.100.2"}):
            assert auth_mod.get_client_ip() == "203.0.113.5"

    def test_falls_back_to_remote_addr(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(environ_base={"REMOTE_ADDR": "198.51.100.9"}):
            assert auth_mod.get_client_ip() == "198.51.100.9"


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

    def test_rejects_disallowed_client_ip(self, flask_app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
        auth_mod._ALLOWED_IPS = set()
        monkeypatch.setenv("ASTRAL_ALLOWED_IPS", "203.0.113.1")
        with flask_app.test_request_context(environ_base={"REMOTE_ADDR": "198.51.100.2"}):
            assert auth_mod.is_ip_allowed() is False
