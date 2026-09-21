"""
Stytch B2C Consumer session client.

External service layer: validates session JWTs via Stytch SDK only.
Returns a plain dict for src/utils/auth.py normalization — no Flask imports.

Required env vars (read via AUTH_CONFIG):
  STYTCH_PROJECT_ID — Stytch project id
  STYTCH_SECRET     — Stytch secret

Public API: authenticate_session_jwt, log_stytch_project_env, StytchAuthError
"""

import logging
from typing import Any

from src.utils.config import AUTH_CONFIG
from src.utils.integration_io import require_controlled_external_io

__all__ = ["authenticate_session_jwt", "log_stytch_project_env", "StytchAuthError"]

_client = None
_profile_by_user_id: dict[str, dict] = {}
_log = logging.getLogger(__name__)


def _stytch_project_env(project_id: str) -> str:
    pid = (project_id or "").strip()
    if pid.startswith("project-live-"):
        return "live"
    if pid.startswith("project-test-"):
        return "test"
    return "unknown"


def log_stytch_project_env() -> None:
    """Log configured Stytch project env once at startup (no secrets)."""
    project_id = AUTH_CONFIG["stytch_project_id"]
    if not project_id:
        _log.warning("STYTCH_PROJECT_ID is unset — Bearer auth will fail until configured")
        return
    env = _stytch_project_env(project_id)
    short_id = project_id if len(project_id) <= 32 else f"{project_id[:32]}…"
    _log.info("Stytch auth configured: env=%s project_id=%s", env, short_id)


class StytchAuthError(Exception):
    """Raised when Stytch rejects a session JWT."""


def _get_client():
    global _client
    if _client is not None:
        return _client
    from stytch import Client  # lazy import — optional until AST-611 cutover

    project_id = AUTH_CONFIG["stytch_project_id"]
    secret = AUTH_CONFIG["stytch_secret"]
    if not project_id or not secret:
        raise StytchAuthError("STYTCH_PROJECT_ID and STYTCH_SECRET must be set")
    _client = Client(project_id=project_id, secret=secret)
    return _client


def _primary_email(user: Any) -> str | None:
    emails = getattr(user, "emails", None) or []
    if not emails:
        return None
    verified = [e for e in emails if getattr(e, "verified", False)]
    chosen = verified[0] if verified else emails[0]
    email = getattr(chosen, "email", None)
    return email.lower() if email else None


def _display_name(user: Any, email: str | None, user_id: str) -> str:
    name = getattr(user, "name", None)
    if name is not None:
        first = getattr(name, "first_name", "") or ""
        last = getattr(name, "last_name", "") or ""
        full = f"{first} {last}".strip()
        if full:
            return full
    return email or user_id


def authenticate_session_jwt(session_jwt: str, *, remote: bool = True) -> dict:
    """Validate a Stytch session JWT; return user_id, email, name dict.

    remote=True (user-initiated): force SessionsAuthenticate + users.get, cache profile.
    remote=False (silent poll): local JWT only; reuse cached profile; never users.get.
    """
    require_controlled_external_io("stytch.authenticate_session_jwt")
    token = (session_jwt or "").strip()
    if not token:
        raise StytchAuthError("missing session JWT")
    try:
        client = _get_client()
        jwt_kwargs: dict[str, Any] = {"session_jwt": token}
        if remote:
            jwt_kwargs["max_token_age_seconds"] = 0
        resp = client.sessions.authenticate_jwt(**jwt_kwargs)
        user = getattr(resp, "user", None)
        session = getattr(resp, "session", None)
        user_id = str(
            getattr(user, "user_id", None)
            or getattr(session, "user_id", None)
            or ""
        )
        if not user_id:
            raise StytchAuthError("missing session user_id in JWT response")
        if not remote:
            cached = _profile_by_user_id.get(user_id)
            if cached is not None:
                return dict(cached)
            return {"user_id": user_id, "email": None, "name": user_id}
        if user is None:
            # users.get returns GetResponse — user fields live on the response itself.
            user = client.users.get(user_id=user_id)
    except StytchAuthError:
        raise
    except Exception as exc:
        raise StytchAuthError(str(exc)) from exc
    email = _primary_email(user)
    profile = {
        "user_id": str(user.user_id),
        "email": email,
        "name": _display_name(user, email, str(user.user_id)),
    }
    _profile_by_user_id[profile["user_id"]] = profile
    return dict(profile)
