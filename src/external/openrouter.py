"""OpenRouter host discovery (AST-1959): one probe per batch key, then the batch is pinned to that host.

OpenRouter routes every call on its own and prompt caches live on one host, so a batch whose warm call
and gather calls land on different hosts pays full input on every call. Servers opt in via the
LLM_SERVER_CONFIG `probe` flag; send_to_llm_compat calls get_batch_host only when that flag is on and
log_batch_id is set.
"""

import asyncio
import json
import threading
from concurrent.futures import Future
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple

from src.utils.config import LLM_PROBE_MESSAGE
from src.utils.llm_external import normalize_provider_error
from src.utils.logging import get_logger

__all__ = ["probe_host", "get_batch_host"]

logger = get_logger(__name__)

# (batch_id, request-args json) → Future[(host, error)]. Never evicted: a restart clears it, no cap / TTL.
# concurrent.futures.Future + threading.Lock (not asyncio primitives) because callers may run on
# different event loops / worker threads; asyncio.wrap_future bridges each waiter to its own loop.
_hosts: Dict[Tuple[str, str], Future] = {}
_hosts_lock = threading.Lock()


def _batch_key(batch_id: str, api_kwargs: Dict[str, Any]) -> Tuple[str, str]:
    """Batch id + every request argument except content and system — same settings, same host."""
    rest = {k: v for k, v in api_kwargs.items() if k not in ("messages", "system")}
    return batch_id, json.dumps(rest, sort_keys=True, default=str)


async def probe_host(
    api_kwargs: Dict[str, Any],
    send: Callable[[Dict[str, Any]], Awaitable[Any]],
    record_probe: Callable[[Any], None],
) -> str:
    """Send the real call's request with the probe message as its only content and no system block;
    return the response's `provider`. Raises when the call fails or names no provider."""
    # Content swapped wholesale and system dropped → no cache_control can ride along. Everything else
    # (max_tokens, temperature, effort, agent provider object) is the real call's, so OpenRouter
    # filters eligible hosts exactly as it will for the batch.
    probe_kwargs = {k: v for k, v in api_kwargs.items() if k not in ("messages", "system")}
    probe_kwargs["messages"] = [{"role": "user", "content": [{"type": "text", "text": LLM_PROBE_MESSAGE}]}]
    logger.debug("Calling messages.create (probe): %s", probe_kwargs)
    response = await send(probe_kwargs)
    logger.debug("Response from messages.create (probe): %s", response)
    record_probe(response)
    host = getattr(response, "provider", None)
    if not host:
        raise ValueError("Probe response named no provider")
    return host


async def get_batch_host(
    batch_id: str,
    api_kwargs: Dict[str, Any],
    send: Callable[[Dict[str, Any]], Awaitable[Any]],
    record_probe: Callable[[Any], None],
) -> Tuple[Optional[str], Optional[str]]:
    """(host, None) for the batch key, or (None, error) when its probe failed. Exactly one probe per key:
    the first caller runs it, concurrent and later callers await the same result."""
    key = _batch_key(batch_id, api_kwargs)
    with _hosts_lock:
        fut = _hosts.get(key)
        owner = fut is None
        if owner:
            fut = _hosts[key] = Future()
    if not owner:
        logger.debug("Host map: awaiting probe result for batch=%s", batch_id)
        return await asyncio.wrap_future(fut)
    logger.debug("Host map: probing for batch=%s key=%s", batch_id, key[1])
    try:
        fut.set_result((await probe_host(api_kwargs, send, record_probe), None))
    except Exception as e:
        fut.set_result((None, f"Host probe failed: {normalize_provider_error(e)}"))
    finally:
        # Cancelled owner (caller timeout) must not strand the waiters on a never-resolved future.
        if not fut.done():
            fut.set_result((None, "Host probe failed: probe cancelled"))
    host, err = fut.result()
    logger.debug("Host map: batch=%s host=%s error=%s", batch_id, host, err)
    return host, err
