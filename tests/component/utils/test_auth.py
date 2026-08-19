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


class TestAst1440LocalOperator:
    """AST-1440: synthetic always-admin operator + public passthrough payload."""

    def test_identity_from_auth_config_always_admin(self) -> None:
        from src.utils.config import AUTH_CONFIG

        assert AUTH_CONFIG["local_operator"] == {
            "user_id": "local-operator",
            "name": "Local Operator",
        }
        out = auth_mod.local_operator_user()
        assert out == {
            "user_id": "local-operator",
            "name": "Local Operator",
            "is_admin": True,
        }

    def test_always_admin_without_admin_lists(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            auth_mod,
            "AUTH_CONFIG",
            {
                "admin_user_ids": frozenset(),
                "admin_emails": frozenset(),
                "local_operator": {"user_id": "local-operator", "name": "Local Operator"},
            },
            raising=False,
        )
        out = auth_mod.local_operator_user()
        assert out["is_admin"] is True
        assert auth_mod.is_admin(user_id=out["user_id"], email=None) is False

    def test_payload_true_when_local(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")
        assert auth_mod.local_auth_passthrough_payload() == {"local_auth_passthrough": True}

    def test_payload_false_when_staging_or_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")
        assert auth_mod.local_auth_passthrough_payload() == {"local_auth_passthrough": False}
        monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        assert auth_mod.local_auth_passthrough_payload() == {"local_auth_passthrough": False}

    def test_payload_has_only_boolean_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")
        payload = auth_mod.local_auth_passthrough_payload()
        assert set(payload) == {"local_auth_passthrough"}
        assert isinstance(payload["local_auth_passthrough"], bool)
        for forbidden in ("stytch_secret", "stytch_project_id", "admin_user_ids", "admin_emails"):
            assert forbidden not in payload
