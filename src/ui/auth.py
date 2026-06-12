"""IP-allowlist authentication for UI API endpoints. Imported by blueprint modules."""

import os
from functools import wraps

from flask import g, jsonify, request

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
    """IP gate + Bearer token scaffold. Token validation is a stub until Auth0 is wired up."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_ip_allowed():
            return jsonify({"error": "Access denied"}), 403
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        # TODO: validate JWT via Auth0 once tenant is configured
        g.user = {"user_id": "susan", "name": "Susan Somerset"}
        return f(*args, **kwargs)
    return decorated
