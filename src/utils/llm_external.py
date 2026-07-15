"""Shared helpers for Anthropic- and DeepSeek-compatible external LLM clients (AST-687 / AST-538)."""

from typing import Any, Dict, List, Optional

from src.utils.config import PROVIDER_BALANCE_REFUSAL
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
