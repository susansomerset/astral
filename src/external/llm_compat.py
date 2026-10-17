"""One client for every Anthropic-Messages-compatible server in LLM_SERVER_CONFIG (AST-1851).

Parameterized by server id + SKU; key always passed by the caller (no env fallback). Probe-flagged servers lock each batch to one host (AST-1959).
"""

import random
import threading
import time
from contextlib import nullcontext
from typing import Any, Callable, Dict, List, Optional

from anthropic import Anthropic, RateLimitError
import httpx as _httpx

from src.utils.llm_external import (
    provider_call_http_timeout_seconds,
    provider_call_max_retries,
)
from src.utils.logging import get_logger

__all__ = ["send_to_llm_compat", "get_receipt"]

logger = get_logger(__name__)


def _get_client(server: Dict[str, Any], api_key: str) -> Anthropic:
    # Exactly one explicit credential: the SDK then skips ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN
    # env lookup, so no other platform's key can ride along.
    cred = {"auth_token": api_key} if server["auth"] == "bearer" else {"api_key": api_key}
    return Anthropic(
        base_url=server["base_url"],
        timeout=_httpx.Timeout(provider_call_http_timeout_seconds()),
        max_retries=provider_call_max_retries(),
        **cred,
    )


_slots: Dict[str, threading.BoundedSemaphore] = {}
_slots_lock = threading.Lock()


def _create(client: Anthropic, api_kwargs: Dict[str, Any], server_id: str, concurrency: Optional[Dict[str, Any]]) -> Any:
    """Blocking messages.create in a worker thread; servers with a concurrency block get jittered,
    doubling 429 backoff. The process-wide slot cap (held only during the call) and the delay
    ceiling apply only when max_concurrent / backoff_max_seconds are configured (AST-2010)."""
    if not concurrency:
        return client.messages.create(**api_kwargs)
    sem: Any = nullcontext()
    if concurrency.get("max_concurrent"):
        with _slots_lock:
            sem = _slots.setdefault(server_id, threading.BoundedSemaphore(int(concurrency["max_concurrent"])))
    attempts = int(concurrency["rate_limit_retries"]) + 1
    base = float(concurrency["backoff_base_seconds"])
    cap = concurrency.get("backoff_max_seconds")
    for attempt in range(attempts):
        try:
            with sem:
                return client.messages.create(**api_kwargs)
        except RateLimitError:
            if attempt == attempts - 1:
                raise
            delay = base * (2 ** attempt)
            if cap is not None:
                delay = min(delay, float(cap))
            delay *= random.uniform(0.5, 1.0)
            logger.warning("%s 429; retry %d/%d in %.1fs", server_id, attempt + 1, attempts - 1, delay)
            time.sleep(delay)


async def send_to_llm_compat(
    content_blocks: List[Dict[str, Any]],
    *,
    server_id: str,
    sku: str,
    tier: Dict[str, Any],
    api_key: str,
    system_blocks: Optional[List[Dict[str, Any]]] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    response_format: Optional[str] = None,
    prompt_label: str = "(unknown)",
    candidate_id: Optional[str] = None,
    task_key_uuid: Optional[str] = None,
    no_cache_prompt_tokens: int = 0,
    no_cache_live_tokens: int = 0,
    batch_size: int = 1,
    record_timesheet: Optional[Callable[..., None]] = None,
    forced_tool: Optional[Dict[str, Any]] = None,
    request_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> Dict[str, Any]:
    raise RuntimeError(
        "send_to_llm_compat retired (AST-2239); use src.external.astral_agent.submit with an assembled provider request"
    )


def get_receipt(external_ids: List[str], api_key: str) -> List[Dict[str, Any]]:
    """Zero-stub receipts for direct servers (AST-2217). No network. platform_cost always None.
    OpenRouter-routed generation ids are answered by openrouter.get_receipt (AST-2218)."""
    from src.utils.config import TIMESHEET_RECEIPT_FIELDS
    out: List[Dict[str, Any]] = []
    for _eid in external_ids:
        row = {k: None for k in TIMESHEET_RECEIPT_FIELDS}
        row["native_tokens_prompt"] = 0
        row["native_tokens_completion"] = 0
        row["native_tokens_cached"] = 0
        row["cache_write_tokens"] = 0
        row["response_item_count"] = 0
        row["response_char_length"] = 0
        row["platform_cost"] = None
        row["completion_status"] = "stub"
        out.append(row)
    return out
