"""Failure-class literals and call-budget helpers.

Mirror platform PROVIDER_* / PROVIDER_CALL_BUDGET and src/utils/llm_external.py.
Change both sides together when classes change. No platform imports.
"""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, List, Optional

# Mirror src/utils/config.py PROVIDER_BALANCE_REFUSAL.
BALANCE_REFUSAL = {
    "failure_class": "provider_balance_refusal",
    "http_status_codes": (402,),
    "message_substrings": (
        "insufficient balance",
        "insufficient credit",
        "credit exhausted",
        "out of credit",
        "payment required",
    ),
}

# Mirror PROVIDER_RATE_LIMIT.
RATE_LIMIT = {
    "failure_class": "provider_rate_limit",
    "http_status_codes": (429,),
    "message_substrings": ("error code: 429", "rate_limit_error"),
}

# Mirror PROVIDER_PROBE_FAILURE.
PROBE_FAILURE = {
    "failure_class": "provider_probe_failure",
}

# Mirror PROVIDER_EMPTY_RESPONSE.
EMPTY_RESPONSE = {
    "failure_class": "provider_empty_response",
    "error": (
        "Provider returned unusable response "
        "(missing stop reason, zero tokens, no content)"
    ),
}

# Mirror PROVIDER_CALL_BUDGET.
CALL_BUDGET = {
    "timeout_seconds": 600,
    "grace_seconds": 10,
    "max_retries": 0,
    "failure_class": "provider_call_timeout",
    "error_template": (
        "Provider call exceeded per-call time budget ({timeout_seconds}s)"
    ),
    "exception_type_names": (
        "TimeoutError",
        "TimeoutException",
        "ReadTimeout",
        "ConnectTimeout",
        "WriteTimeout",
        "PoolTimeout",
        "APITimeoutError",
    ),
}

ZERO_USAGE = {
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read_input_tokens": 0,
    "cache_creation_input_tokens": 0,
}


class ProviderJobError(Exception):
    """Malformed request — worker writes jobqueue.fail with error_class."""

    def __init__(self, error_class: str, detail: str) -> None:
        self.error_class = error_class
        self.detail = detail
        super().__init__(f"[{error_class}] {detail}")


def classify_provider_balance_refusal(exc: BaseException) -> Optional[str]:
    fc = BALANCE_REFUSAL["failure_class"]
    status = getattr(exc, "status_code", None)
    if status is None:
        status = getattr(getattr(exc, "response", None), "status_code", None)
    if status in BALANCE_REFUSAL["http_status_codes"]:
        return fc
    msg = str(exc).lower()
    for substr in BALANCE_REFUSAL["message_substrings"]:
        if substr in msg:
            return fc
    return None


def classify_provider_rate_limit(exc_or_msg: Any) -> Optional[str]:
    status = getattr(exc_or_msg, "status_code", None)
    if status is None:
        status = getattr(getattr(exc_or_msg, "response", None), "status_code", None)
    if status in RATE_LIMIT["http_status_codes"]:
        return RATE_LIMIT["failure_class"]
    msg = str(exc_or_msg).lower()
    if any(s in msg for s in RATE_LIMIT["message_substrings"]):
        return RATE_LIMIT["failure_class"]
    return None


def classify_provider_call_timeout(exc: BaseException) -> Optional[str]:
    fc = CALL_BUDGET["failure_class"]
    names = CALL_BUDGET["exception_type_names"]
    seen: set[int] = set()
    cur: Optional[BaseException] = exc
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        if isinstance(cur, TimeoutError) or type(cur).__name__ in names:
            return fc
        cur = cur.__cause__ if cur.__cause__ is not None else cur.__context__
    return None


def non_empty_provider_error(exc: BaseException, *, fallback: str) -> str:
    err = str(exc).strip()
    return err if err else fallback


def normalize_provider_error(exc_or_msg: Any, *, fallback: Optional[str] = None) -> str:
    if isinstance(exc_or_msg, BaseException):
        raw = str(exc_or_msg)
    elif exc_or_msg is None:
        raw = ""
    else:
        raw = str(exc_or_msg)
    stripped = raw.strip()
    if stripped:
        return stripped
    if fallback is not None and str(fallback).strip():
        return str(fallback).strip()
    if isinstance(exc_or_msg, BaseException):
        return f"{type(exc_or_msg).__name__}: provider call failed with empty error detail"
    return "provider call failed with empty error detail"


def timeout_error_message(timeout_seconds: int) -> str:
    return CALL_BUDGET["error_template"].format(timeout_seconds=int(timeout_seconds))


def extract_api_response_text(api_response: Any) -> str:
    if not hasattr(api_response, "content") or not api_response.content:
        raise ValueError("API response content is empty or missing")
    text_parts: List[str] = []
    for block in api_response.content:
        text = getattr(block, "text", None)
        if isinstance(text, str) and text:
            text_parts.append(text)
    return "".join(text_parts)


def is_unusable_provider_response(
    response: Any, *, input_tokens: int, output_tokens: int
) -> bool:
    stop = getattr(response, "stop_reason", None)
    stop_missing = stop is None or (isinstance(stop, str) and stop.strip() in ("", "?"))
    zero_tokens = int(input_tokens or 0) == 0 and int(output_tokens or 0) == 0
    try:
        text = extract_api_response_text(response)
        no_content = not (isinstance(text, str) and text.strip())
    except ValueError:
        no_content = True
    return stop_missing and zero_tokens and no_content


def tool_use_json(response: Any) -> Optional[str]:
    """JSON of the first tool_use input, or None when the reply is plain text."""
    import json

    for block in getattr(response, "content", None) or []:
        if getattr(block, "type", None) == "tool_use":
            return json.dumps(getattr(block, "input", None), default=str)
    return None


def usage_from_response(response: Any) -> dict:
    usage = getattr(response, "usage", None)
    return {
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
        "cache_read_input_tokens": int(getattr(usage, "cache_read_input_tokens", 0) or 0),
        "cache_creation_input_tokens": int(getattr(usage, "cache_creation_input_tokens", 0) or 0),
    }


def soft_fail(
    *,
    error: str,
    failure_class: Optional[str] = None,
    host: Optional[str] = None,
) -> dict:
    out = {
        "success": False,
        "api_response": "",
        "stop_reason": None,
        "response_id": None,
        "usage": dict(ZERO_USAGE),
        "error": error,
    }
    if failure_class:
        out["failure_class"] = failure_class
    if host is not None:
        out["host"] = host
    return out


def success_result(response: Any, *, host: Optional[str] = None) -> dict:
    dumped = tool_use_json(response)
    if dumped is not None:
        text = dumped
    else:
        text = extract_api_response_text(response)
    out = {
        "success": True,
        "api_response": text,
        "stop_reason": getattr(response, "stop_reason", None),
        "response_id": getattr(response, "id", None),
        "usage": usage_from_response(response),
    }
    if host is not None:
        out["host"] = host
    return out


async def await_provider_call_with_budget(
    make_call: Callable[[], Awaitable[Any]],
    *,
    timeout_seconds: float,
    timeout_message: str,
) -> Any:
    """Await an async SDK call under a wall clock.

    wait_for cancels the inner call on expiry and on an outer cancel, so the HTTP
    connection is closed and nothing keeps running (or billing) behind the caller.
    """
    try:
        return await asyncio.wait_for(make_call(), timeout=timeout_seconds)
    except TimeoutError:
        raise TimeoutError(timeout_message) from None
