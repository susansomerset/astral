"""Stytch Bearer auth for UI API endpoints. Imported by blueprint modules.

@require_auth validates Authorization: Bearer via src.utils.auth.validate_bearer_token
and sets g.user to {user_id, name, is_admin}.

@require_admin requires is_admin on g.user (403 otherwise).

@require_ip gates script callers without Bearer tokens. ASTRAL_ALLOWED_IPS applies
only to @require_ip routes; empty allowlist = open (dev mode).
"""

import os
from functools import wraps

from flask import g, jsonify, request

from src.utils.auth import validate_bearer_token

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


def require_auth(f):
    """Validate Stytch session JWT from Authorization: Bearer header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header[7:].strip()
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
