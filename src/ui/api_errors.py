"""Shared JSON error responses for UI API routes (AST-779)."""

from __future__ import annotations

import traceback
from typing import Any

from flask import jsonify


def error_json(message: str, status: int = 400, **extra: Any):
    """Return (Response, status). Always includes \"error\" key; extra keys are optional enrichments."""
    body: dict[str, Any] = {"error": message}
    for key, value in extra.items():
        if value is not None:
            body[key] = value
    return jsonify(body), status


def server_error_from_exception(exc: BaseException):
    """500 payload for toast diagnostics — no secrets, no request headers."""
    return error_json(
        str(exc) or exc.__class__.__name__,
        500,
        exception_type=exc.__class__.__name__,
        traceback="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )
