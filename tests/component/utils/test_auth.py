"""Component tests for src/utils/auth.py (AST-610)."""

from __future__ import annotations

import pytest

from src.utils import auth as auth_mod


@pytest.fixture(autouse=True)
def _reset_authenticator() -> None:
    auth_mod._authenticate = None


# Branches: admin by user_id; admin by email (case-insensitive); neither.
class TestIsAdmin:
    def test_admin_user_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            auth_mod,
            "AUTH_CONFIG",
            {
                "admin_user_ids": frozenset({"user-admin-1"}),
                "admin_emails": frozenset(),
            },
            raising=False,
        )
        assert auth_mod.is_admin(user_id="user-admin-1", email="other@example.com") is True

    def test_admin_email_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            auth_mod,
            "AUTH_CONFIG",
            {
                "admin_user_ids": frozenset(),
                "admin_emails": frozenset({"susan@susansomerset.com"}),
            },
            raising=False,
        )
        assert auth_mod.is_admin(user_id="user-2", email="Susan@Susansomerset.com") is True

    def test_not_admin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            auth_mod,
            "AUTH_CONFIG",
            {
                "admin_user_ids": frozenset({"other-id"}),
                "admin_emails": frozenset({"other@example.com"}),
            },
            raising=False,
        )
        assert auth_mod.is_admin(user_id="user-3", email="plain@example.com") is False


# Branches: normalized shape; blank name falls back to email then user_id.
class TestNormalizeUser:
    def test_returns_user_id_name_is_admin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            auth_mod,
            "AUTH_CONFIG",
            {
                "admin_user_ids": frozenset({"uid-1"}),
                "admin_emails": frozenset(),
            },
            raising=False,
        )
        out = auth_mod.normalize_user(user_id="uid-1", name="Ada Lovelace", email="ada@example.com")
        assert out == {"user_id": "uid-1", "name": "Ada Lovelace", "is_admin": True}

    def test_blank_name_falls_back_to_email(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            auth_mod,
            "AUTH_CONFIG",
            {"admin_user_ids": frozenset(), "admin_emails": frozenset()},
            raising=False,
        )
        out = auth_mod.normalize_user(user_id="uid-2", name="   ", email="ada@example.com")
        assert out["name"] == "ada@example.com"
        assert out["is_admin"] is False


# Branches: empty token; no authenticator; happy path; authenticator raises.
class TestValidateBearerToken:
    def test_none_when_token_empty(self) -> None:
        assert auth_mod.validate_bearer_token("") is None
        assert auth_mod.validate_bearer_token("   ") is None

    def test_none_when_no_authenticator_registered(self) -> None:
        assert auth_mod.validate_bearer_token("jwt-token") is None

    def test_happy_path_with_mock_authenticator(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            auth_mod,
            "AUTH_CONFIG",
            {"admin_user_ids": frozenset(), "admin_emails": frozenset({"ada@example.com"})},
            raising=False,
        )

        def _auth(token: str) -> dict:
            assert token == "good-jwt"
            return {"user_id": "uid-9", "name": "Ada", "email": "ada@example.com"}

        auth_mod.register_token_authenticator(_auth)
        out = auth_mod.validate_bearer_token("good-jwt")
        assert out == {"user_id": "uid-9", "name": "Ada", "is_admin": True}

    def test_none_when_authenticator_raises(self) -> None:
        def _boom(_token: str) -> dict:
            raise RuntimeError("invalid jwt")

        auth_mod.register_token_authenticator(_boom)
        assert auth_mod.validate_bearer_token("bad-jwt") is None

    def test_session_not_found_logs_ops_hint(self, caplog: pytest.LogCaptureFixture) -> None:
        def _missing(_token: str) -> dict:
            raise RuntimeError("error_type='session_not_found'")

        auth_mod.register_token_authenticator(_missing)
        with caplog.at_level("WARNING"):
            assert auth_mod.validate_bearer_token("stale-jwt") is None
        assert "Bearer token validation failed" in caplog.text
        assert "Stytch session_not_found — verify STYTCH_PROJECT_ID" in caplog.text
