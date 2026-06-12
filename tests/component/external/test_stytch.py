"""Component tests for src/external/stytch.py (AST-610)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.external import stytch as stytch_mod


@pytest.fixture(autouse=True)
def _reset_stytch_client() -> None:
    stytch_mod._client = None


def _fake_user(
    *,
    user_id: str = "user-test-1",
    emails: list | None = None,
    first: str = "Susan",
    last: str = "Somerset",
) -> SimpleNamespace:
    if emails is None:
        emails = [SimpleNamespace(email="Susan@Example.com", verified=True)]
    return SimpleNamespace(
        user_id=user_id,
        emails=emails,
        name=SimpleNamespace(first_name=first, last_name=last),
    )


# Branches: happy path mapping; empty JWT; SDK error wrap; missing env on client.
class TestAuthenticateSessionJwt:
    def test_happy_path_maps_user_id_email_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        mock_sessions = MagicMock()
        mock_sessions.authenticate_jwt.return_value = SimpleNamespace(user=_fake_user())
        mock_client = MagicMock(sessions=mock_sessions)
        monkeypatch.setattr(stytch_mod, "_get_client", lambda: mock_client)

        out = stytch_mod.authenticate_session_jwt("  jwt-here  ")
        assert out == {
            "user_id": "user-test-1",
            "email": "susan@example.com",
            "name": "Susan Somerset",
        }
        mock_sessions.authenticate_jwt.assert_called_once_with(session_jwt="jwt-here")

    def test_empty_jwt_raises_stytch_auth_error(self) -> None:
        with pytest.raises(stytch_mod.StytchAuthError, match="missing session JWT"):
            stytch_mod.authenticate_session_jwt("")

    def test_sdk_exception_wraps_stytch_auth_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        mock_sessions = MagicMock()
        mock_sessions.authenticate_jwt.side_effect = RuntimeError("jwt expired")
        mock_client = MagicMock(sessions=mock_sessions)
        monkeypatch.setattr(stytch_mod, "_get_client", lambda: mock_client)

        with pytest.raises(stytch_mod.StytchAuthError, match="jwt expired"):
            stytch_mod.authenticate_session_jwt("expired")

    def test_missing_env_raises_stytch_auth_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            stytch_mod,
            "AUTH_CONFIG",
            {"stytch_project_id": "", "stytch_secret": ""},
            raising=False,
        )
        with pytest.raises(stytch_mod.StytchAuthError, match="STYTCH_PROJECT_ID"):
            stytch_mod._get_client()
