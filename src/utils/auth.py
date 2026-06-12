"""
Provider-agnostic authentication helpers (AST-609 / AST-610).

Normalizes authenticated users for g.user and resolves admin from AUTH_CONFIG.
Token validation uses a registerable authenticator so utils never imports external.

AST-611 must call register_token_authenticator(stytch.authenticate_session_jwt)
before require_auth can validate real Stytch sessions.

Public API: register_token_authenticator, validate_bearer_token, normalize_user, is_admin
"""

from typing import Any, Callable, Mapping

from src.utils.config import AUTH_CONFIG

__all__ = [
    "register_token_authenticator",
    "validate_bearer_token",
    "normalize_user",
    "is_admin",
    "TokenAuthenticator",
]

TokenAuthenticator = Callable[[str], Mapping[str, Any]]
_authenticate: TokenAuthenticator | None = None


def register_token_authenticator(fn: TokenAuthenticator) -> None:
    """Wire the external token validator (e.g. stytch.authenticate_session_jwt)."""
    global _authenticate
    _authenticate = fn


def is_admin(*, user_id: str, email: str | None) -> bool:
    if user_id in AUTH_CONFIG["admin_user_ids"]:
        return True
    if email is not None and email.lower() in AUTH_CONFIG["admin_emails"]:
        return True
    return False


def normalize_user(*, user_id: str, name: str, email: str | None) -> dict:
    display_name = (name or "").strip() or (email or user_id)
    return {
        "user_id": user_id,
        "name": display_name,
        "is_admin": is_admin(user_id=user_id, email=email),
    }


def validate_bearer_token(raw_token: str) -> dict | None:
    token = (raw_token or "").strip()
    if not token or _authenticate is None:
        return None
    try:
        session = _authenticate(token)
        return normalize_user(
            user_id=str(session["user_id"]),
            name=str(session.get("name") or ""),
            email=session.get("email"),
        )
    except Exception:
        return None
