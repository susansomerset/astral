"""Native Anthropic Messages call from an assembled request dict."""

from __future__ import annotations

from typing import Any, Dict

import httpx
from anthropic import Anthropic

from providers.errors import (
    CALL_BUDGET,
    EMPTY_RESPONSE,
    classify_provider_balance_refusal,
    classify_provider_call_timeout,
    is_unusable_provider_response,
    normalize_provider_error,
    soft_fail,
    success_result,
    timeout_error_message,
    usage_from_response,
    await_provider_call_with_budget,
)


def _int_or(request: Dict[str, Any], key: str, default: int) -> int:
    raw = request.get(key)
    return default if raw is None else int(raw)


def _kwargs(request: Dict[str, Any]) -> Dict[str, Any]:
    api_kwargs: Dict[str, Any] = {
        "model": request["model"],
        "max_tokens": request["max_tokens"],
        "messages": request["messages"],
    }
    if request.get("system"):
        api_kwargs["system"] = request["system"]
    if request.get("temperature") is not None:
        api_kwargs["temperature"] = request["temperature"]
    if request.get("extra_body"):
        api_kwargs["extra_body"] = request["extra_body"]
    if request.get("extra_headers"):
        api_kwargs["extra_headers"] = request["extra_headers"]
    if request.get("tools"):
        api_kwargs["tools"] = request["tools"]
    if request.get("tool_choice"):
        api_kwargs["tool_choice"] = request["tool_choice"]
    return api_kwargs


def _truncated(request: Dict[str, Any], stop_reason: Any) -> bool:
    # Same gate as platform send: json format or a forced tool, and stop max_tokens.
    forced = bool(request.get("tool_choice") or request.get("forced_tool"))
    return (request.get("response_format") == "json" or forced) and stop_reason == "max_tokens"


async def send(request: Dict[str, Any]) -> Dict[str, Any]:
    timeout_s = _int_or(request, "timeout_seconds", int(CALL_BUDGET["timeout_seconds"]))
    grace = _int_or(request, "grace_seconds", int(CALL_BUDGET["grace_seconds"]))
    max_retries = _int_or(request, "max_retries", int(CALL_BUDGET["max_retries"]))
    client = Anthropic(
        api_key=request["api_key"],
        timeout=httpx.Timeout(timeout_s),
        max_retries=max_retries,
    )
    api_kwargs = _kwargs(request)
    wall = float(timeout_s) + float(grace)
    try:
        response = await await_provider_call_with_budget(
            lambda: client.messages.create(**api_kwargs),
            timeout_seconds=wall,
            timeout_message=timeout_error_message(timeout_s),
        )
    except Exception as exc:
        return _from_exception(exc, timeout_s)
    usage = usage_from_response(response)
    if is_unusable_provider_response(
        response,
        input_tokens=usage["input_tokens"],
        output_tokens=usage["output_tokens"],
    ):
        return soft_fail(error=EMPTY_RESPONSE["error"], failure_class=EMPTY_RESPONSE["failure_class"])
    if _truncated(request, getattr(response, "stop_reason", None)):
        return soft_fail(
            error="Generation truncated (max_tokens) before complete JSON",
            failure_class="max_tokens",
        )
    return success_result(response)


def _from_exception(exc: BaseException, timeout_s: int) -> Dict[str, Any]:
    fc_timeout = classify_provider_call_timeout(exc)
    if fc_timeout:
        return soft_fail(error=timeout_error_message(timeout_s), failure_class=fc_timeout)
    err = normalize_provider_error(exc)
    fc = classify_provider_balance_refusal(exc)
    return soft_fail(error=err, failure_class=fc)
