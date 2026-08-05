"""Shared helpers for Anthropic- and DeepSeek-compatible external LLM clients (AST-687 / AST-538)."""

import asyncio
from typing import Any, Callable, Dict, List, Optional

from src.utils.config import (
    PROVIDER_BALANCE_REFUSAL,
    PROVIDER_CALL_BUDGET,
    PROVIDER_EMPTY_RESPONSE,
)
from src.utils.logging import get_logger


def classify_provider_balance_refusal(exc: BaseException) -> Optional[str]:
    """Return PROVIDER_BALANCE_REFUSAL failure_class when exc is billing/credit exhaustion."""
    fc = PROVIDER_BALANCE_REFUSAL["failure_class"]
    status = getattr(exc, "status_code", None)
    if status is None:
        status = getattr(getattr(exc, "response", None), "status_code", None)
    if status in PROVIDER_BALANCE_REFUSAL["http_status_codes"]:
        return fc
    msg = str(exc).lower()
    for substr in PROVIDER_BALANCE_REFUSAL["message_substrings"]:
        if substr in msg:
            return fc
    return None


def is_provider_balance_refusal(result: Optional[Dict[str, Any]]) -> bool:
    """True when an agent/provider result dict was tagged as balance/credit refusal."""
    if not isinstance(result, dict):
        return False
    return result.get("failure_class") == PROVIDER_BALANCE_REFUSAL["failure_class"]


def provider_call_http_timeout_seconds() -> float:
    """httpx / Anthropic client timeout (seconds)."""
    return float(PROVIDER_CALL_BUDGET["timeout_seconds"])


def provider_call_wait_timeout_seconds() -> float:
    """Caller-observed wall budget = timeout_seconds + grace_seconds."""
    return float(PROVIDER_CALL_BUDGET["timeout_seconds"]) + float(
        PROVIDER_CALL_BUDGET["grace_seconds"]
    )


def provider_call_timeout_error_message() -> str:
    """Non-empty operator-facing timeout error (str(TimeoutError()) is '')."""
    return PROVIDER_CALL_BUDGET["error_template"].format(
        timeout_seconds=int(PROVIDER_CALL_BUDGET["timeout_seconds"])
    )


def provider_call_max_retries() -> int:
    return int(PROVIDER_CALL_BUDGET["max_retries"])


def classify_provider_call_timeout(exc: BaseException) -> Optional[str]:
    """Return PROVIDER_CALL_BUDGET failure_class when exc (or cause/context) is a call-budget timeout."""
    fc = PROVIDER_CALL_BUDGET["failure_class"]
    names = PROVIDER_CALL_BUDGET["exception_type_names"]
    seen: set[int] = set()
    cur: Optional[BaseException] = exc
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        if isinstance(cur, TimeoutError) or type(cur).__name__ in names:
            return fc
        cur = cur.__cause__ if cur.__cause__ is not None else cur.__context__
    return None


def non_empty_provider_error(exc: BaseException, *, fallback: str) -> str:
    """str(exc) or fallback — never '' (TimeoutError default)."""
    err = str(exc).strip()
    return err if err else fallback


async def await_provider_call_with_budget(
    make_call: Callable[[], Any],
    *,
    timeout_seconds: float,
) -> Any:
    """Run blocking SDK call in a worker thread; release the caller at timeout_seconds.

    On timeout: raise TimeoutError with provider_call_timeout_error_message() and do
    **not** await the pending thread task (orphan may finish later; caller is free).
    """
    task = asyncio.create_task(asyncio.to_thread(make_call))
    done, _pending = await asyncio.wait({task}, timeout=timeout_seconds)
    if task in done:
        return task.result()
    raise TimeoutError(provider_call_timeout_error_message())


def normalize_provider_error(exc_or_msg: Any, *, fallback: Optional[str] = None) -> str:
    """Non-empty error string for provider failure returns / logs (AST-1190)."""
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


def is_unusable_provider_response(
    response: Any, *, input_tokens: int, output_tokens: int
) -> bool:
    """True when stop is missing, tokens are zero, and content is empty (AST-1190 AC2)."""
    stop = getattr(response, "stop_reason", None)
    stop_missing = stop is None or (isinstance(stop, str) and stop.strip() in ("", "?"))
    zero_tokens = int(input_tokens or 0) == 0 and int(output_tokens or 0) == 0
    try:
        text = extract_api_response_text(response)
        no_content = not (isinstance(text, str) and text.strip())
    except ValueError:
        no_content = True
    return stop_missing and zero_tokens and no_content


def is_provider_empty_response(result: Optional[Dict[str, Any]]) -> bool:
    """True when an agent/provider result dict was tagged as hollow/unusable."""
    if not isinstance(result, dict):
        return False
    return result.get("failure_class") == PROVIDER_EMPTY_RESPONSE["failure_class"]


def extract_api_response_text(api_response: Any) -> str:
    """Return model answer text; skip thinking blocks that lack `.text` (DeepSeek / extended thinking)."""
    if not hasattr(api_response, "content") or not api_response.content:
        raise ValueError("API response content is empty or missing")
    text_parts: List[str] = []
    for block in api_response.content:
        text = getattr(block, "text", None)
        if isinstance(text, str) and text:
            text_parts.append(text)
    if not text_parts:
        raise ValueError("API response content block missing text attribute")
    return text_parts[-1]


def emit_llm_call_debug(
    *,
    logger_name: str,
    func_name: str,
    prompt_label: str,
    model: str,
    duration: float,
    stop_reason: str,
    input_total: int,
    input_cached: int,
    cache_creation_tokens: int,
    output_total: int,
    raw_text: str = "",
    error: Optional[str] = None,
    provider: str = "anthropic",
    vendor_detail: Optional[str] = None,
) -> None:
    """Emit AST-538 contract lines for one external LLM call (debug_flag must already be True)."""
    dbg = get_logger(logger_name, debug_flag=True)
    outcome = "error" if error else ("max_tokens" if stop_reason == "max_tokens" else "success")
    dbg.debug_index(
        func=func_name,
        index=1,
        total=1,
        identifier=prompt_label or "(unknown)",
        outcome=outcome,
    )
    dbg.debug_detail(
        f"provider={provider} model={model} task={prompt_label} "
        f"duration={duration:.1f}s stop_reason={stop_reason or 'n/a'}"
    )
    token_line = (
        f"tokens fresh={input_total} cache_read={input_cached} "
        f"cache_write={cache_creation_tokens} output={output_total}"
    )
    if vendor_detail:
        token_line = f"{vendor_detail} {token_line}"
    dbg.debug_detail(token_line)
    if error:
        dbg.debug_detail(f"error={error}")
    elif stop_reason == "max_tokens":
        dbg.debug_detail("warning=stop_reason_max_tokens — API response may be truncated")
    if raw_text and not error:
        dbg.debug_detail("response_preview:")
        dbg.debug_detail_block(raw_text)
