"""Stytch session auth for UI API endpoints. Imported by blueprint modules.

@require_auth validates the Stytch session JWT from Authorization: Bearer or the
stytch_session_jwt cookie (opaque/HttpOnly SDK mode — cookie forwarded via Vite proxy
or same-site deploy). Sets g.user to {user_id, name, is_admin}.

@require_admin requires is_admin on g.user (403 otherwise).

@require_ip gates script callers without Bearer tokens. ASTRAL_ALLOWED_IPS applies
only to @require_ip routes; empty allowlist = open (dev mode).
"""

import os
from functools import wraps

from flask import g, jsonify, request

from src.utils.auth import validate_bearer_token

_STYTCH_JWT_COOKIE = "stytch_session_jwt"

_ALLOWED_IPS: set[str] = set()


def _load_allowed_ips() -> set[str]:
    """Parse ASTRAL_ALLOWED_IPS env var (comma-separated) into a set. Cached after first call."""
    global _ALLOWED_IPS
    if not _ALLOWED_IPS:
        raw = os.environ.get("ASTRAL_ALLOWED_IPS", "")
        _ALLOWED_IPS = {ip.strip() for ip in raw.split(",") if ip.strip()}
    return _ALLOWED_IPS


def get_client_ip() -> str:
    """Real client IP from X-Forwarded-For (Railway proxy) or remote_addr fallback."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or ""


def is_ip_allowed() -> bool:
    allowed = _load_allowed_ips()
    if not allowed:  # no allowlist configured = open access (dev mode)
        return True
    return get_client_ip() in allowed


def require_ip(f):
    """IP gate only — for script callers that don't carry a Bearer token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_ip_allowed():
            return jsonify({"error": "Access denied"}), 403
        return f(*args, **kwargs)
    return decorated


def _session_jwt_from_request() -> str | None:
    """Bearer header first; fall back to Stytch JWT cookie when SDK uses opaque tokens."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if token:
            return token
    cookie_jwt = request.cookies.get(_STYTCH_JWT_COOKIE)
    if cookie_jwt:
        return cookie_jwt.strip()
    return None


def require_auth(f):
    """Validate Stytch session JWT from Bearer header or stytch_session_jwt cookie."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _session_jwt_from_request()
        if not token:
            return jsonify({"error": "Missing or invalid session credentials"}), 401
        user = validate_bearer_token(token)
        if user is None:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.user = user
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """Require authenticated admin user."""
    @require_auth
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user.get("is_admin"):
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated
