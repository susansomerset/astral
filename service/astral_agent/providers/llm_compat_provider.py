"""Anthropic-compat Messages (DeepSeek, Kimi, OpenRouter) from an assembled request."""

from __future__ import annotations

import asyncio
import random
from contextlib import nullcontext
from typing import Any, Dict, Optional

import httpx
from anthropic import AsyncAnthropic, RateLimitError

from logging_util import get_logger
from providers import openrouter_provider
from providers.errors import (
    CALL_BUDGET,
    EMPTY_RESPONSE,
    PROBE_FAILURE,
    classify_provider_balance_refusal,
    classify_provider_call_timeout,
    classify_provider_rate_limit,
    is_unusable_provider_response,
    normalize_provider_error,
    soft_fail,
    success_result,
    timeout_error_message,
    usage_from_response,
    await_provider_call_with_budget,
)

_log = get_logger("providers.llm_compat_provider")

# Per-server in-flight limit (step 6 removes it). Single event loop, so no lock.
_slots: Dict[str, asyncio.Semaphore] = {}


def _int_or(request: Dict[str, Any], key: str, default: int) -> int:
    raw = request.get(key)
    return default if raw is None else int(raw)


def _client(request: Dict[str, Any], timeout_s: int, max_retries: int) -> AsyncAnthropic:
    cred = {"auth_token": request["api_key"]} if request.get("auth") == "bearer" else {"api_key": request["api_key"]}
    return AsyncAnthropic(
        base_url=request["base_url"],
        timeout=httpx.Timeout(timeout_s),
        max_retries=max_retries,
        **cred,
    )


async def _create(client: AsyncAnthropic, api_kwargs: Dict[str, Any], server_id: str, concurrency: Optional[Dict[str, Any]]) -> Any:
    """Same jittered doubling 429 backoff as the platform compat client."""
    if not concurrency:
        return await client.messages.create(**api_kwargs)
    sem: Any = nullcontext()
    if concurrency.get("max_concurrent"):
        sem = _slots.setdefault(server_id, asyncio.Semaphore(int(concurrency["max_concurrent"])))
    attempts = int(concurrency["rate_limit_retries"]) + 1
    base = float(concurrency["backoff_base_seconds"])
    cap = concurrency.get("backoff_max_seconds")
    for attempt in range(attempts):
        try:
            async with sem:
                return await client.messages.create(**api_kwargs)
        except RateLimitError:
            if attempt == attempts - 1:
                raise
            delay = base * (2 ** attempt)
            if cap is not None:
                delay = min(delay, float(cap))
            delay *= random.uniform(0.5, 1.0)
            _log.warning("%s 429; retry %d/%d in %.1fs", server_id, attempt + 1, attempts - 1, delay)
            await asyncio.sleep(delay)


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
        api_kwargs["extra_body"] = dict(request["extra_body"])
    if request.get("extra_headers"):
        api_kwargs["extra_headers"] = request["extra_headers"]
    if request.get("tools"):
        api_kwargs["tools"] = request["tools"]
    if request.get("tool_choice"):
        api_kwargs["tool_choice"] = request["tool_choice"]
    return api_kwargs


def _truncated(request: Dict[str, Any], stop_reason: Any) -> bool:
    forced = bool(request.get("tool_choice") or request.get("forced_tool"))
    return (request.get("response_format") == "json" or forced) and stop_reason == "max_tokens"


def _from_exception(exc: BaseException, timeout_s: int, *, host: str, stops_batch: bool) -> Dict[str, Any]:
    fc_timeout = classify_provider_call_timeout(exc)
    if fc_timeout:
        return soft_fail(error=timeout_error_message(timeout_s), failure_class=fc_timeout, host=host)
    err = normalize_provider_error(exc)
    fc = classify_provider_balance_refusal(exc) or (stops_batch and classify_provider_rate_limit(exc))
    return soft_fail(error=err, failure_class=fc or None, host=host)


async def send(request: Dict[str, Any]) -> Dict[str, Any]:
    timeout_s = _int_or(request, "timeout_seconds", int(CALL_BUDGET["timeout_seconds"]))
    max_retries = _int_or(request, "max_retries", int(CALL_BUDGET["max_retries"]))
    # Client is closed on every exit, including a cancel (no leaked sockets).
    async with _client(request, timeout_s, max_retries) as client:
        return await _run(request, client, timeout_s)


async def _run(request: Dict[str, Any], client: AsyncAnthropic, timeout_s: int) -> Dict[str, Any]:
    grace = _int_or(request, "grace_seconds", int(CALL_BUDGET["grace_seconds"]))
    server_id = str(request.get("server_id") or "compat")
    host_label = server_id
    concurrency = request.get("concurrency") if isinstance(request.get("concurrency"), dict) else None
    stops_batch = bool((concurrency or {}).get("exhausted_stops_batch"))
    api_kwargs = _kwargs(request)
    wall = float(timeout_s) + float(grace)

    async def _send(kwargs: Dict[str, Any]) -> Any:
        return await await_provider_call_with_budget(
            lambda: _create(client, kwargs, server_id, concurrency),
            timeout_seconds=wall,
            timeout_message=timeout_error_message(timeout_s),
        )

    if request.get("probe") and request.get("routing") == "openrouter" and request.get("batch_id"):
        host, probe_err = await openrouter_provider.get_batch_host(str(request["batch_id"]), api_kwargs, _send)
        if probe_err is not None:
            fc = PROBE_FAILURE["failure_class"]
            if stops_batch and classify_provider_rate_limit(probe_err):
                fc = "provider_rate_limit"
            return soft_fail(error=probe_err, failure_class=fc, host=host_label)
        extra_body = dict(api_kwargs.get("extra_body") or {})
        api_kwargs["extra_body"] = {
            **extra_body,
            "provider": {**(extra_body.get("provider") or {}), "only": [host]},
        }

    try:
        response = await _send(api_kwargs)
    except Exception as exc:
        return _from_exception(exc, timeout_s, host=host_label, stops_batch=stops_batch)

    served = getattr(response, "provider", None) or host_label
    usage = usage_from_response(response)
    if is_unusable_provider_response(
        response,
        input_tokens=usage["input_tokens"] + usage["cache_read_input_tokens"],
        output_tokens=usage["output_tokens"],
    ):
        return soft_fail(error=EMPTY_RESPONSE["error"], failure_class=EMPTY_RESPONSE["failure_class"], host=served)
    if _truncated(request, getattr(response, "stop_reason", None)):
        return soft_fail(
            error="Generation truncated (max_tokens) before complete JSON",
            failure_class="max_tokens",
            host=served,
        )
    return success_result(response, host=served)
