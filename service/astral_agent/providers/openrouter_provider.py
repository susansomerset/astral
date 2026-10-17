"""OpenRouter host pin. Probe message mirrors platform LLM_PROBE_MESSAGE."""

from __future__ import annotations

import asyncio
import json
import threading
from concurrent.futures import Future
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple

from logging_util import get_logger

from providers.errors import normalize_provider_error

_log = get_logger("providers.openrouter_provider")

PROBE_MESSAGE = "Respond with 1."

_hosts: Dict[Tuple[str, str], Future] = {}
_hosts_lock = threading.Lock()


def _batch_key(batch_id: str, api_kwargs: Dict[str, Any]) -> Tuple[str, str]:
    rest = {k: v for k, v in api_kwargs.items() if k not in ("messages", "system")}
    return batch_id, json.dumps(rest, sort_keys=True, default=str)


def probe_request_kwargs(api_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    probe_kwargs = {k: v for k, v in api_kwargs.items() if k not in ("messages", "system")}
    probe_kwargs["messages"] = [{"role": "user", "content": [{"type": "text", "text": PROBE_MESSAGE}]}]
    extra = dict(probe_kwargs.get("extra_body") or {})
    extra["provider"] = {**(extra.get("provider") or {}), "zdr": True}
    probe_kwargs["extra_body"] = extra
    return probe_kwargs


async def probe_host(
    api_kwargs: Dict[str, Any],
    send: Callable[[Dict[str, Any]], Awaitable[Any]],
) -> str:
    response = await send(probe_request_kwargs(api_kwargs))
    host = getattr(response, "provider", None)
    if not host:
        detail = normalize_provider_error(getattr(response, "error", None) or response, fallback="empty body")
        raise ValueError(f"Probe response named no provider: {detail}")
    return host


async def get_batch_host(
    batch_id: str,
    api_kwargs: Dict[str, Any],
    send: Callable[[Dict[str, Any]], Awaitable[Any]],
) -> Tuple[Optional[str], Optional[str]]:
    """(host, None) or (None, error). One probe per batch key."""
    key = _batch_key(batch_id, api_kwargs)
    with _hosts_lock:
        fut = _hosts.get(key)
        owner = fut is None
        if owner:
            fut = _hosts[key] = Future()
    if not owner:
        _log.debug("Host map: awaiting probe result for batch=%s", batch_id)
        return await asyncio.wrap_future(fut)
    _log.debug("Host map: probing for batch=%s", batch_id)
    try:
        fut.set_result((await probe_host(api_kwargs, send), None))
    except Exception as exc:
        fut.set_result((None, f"Host probe failed: {normalize_provider_error(exc)}"))
    finally:
        if not fut.done():
            fut.set_result((None, "Host probe failed: probe cancelled"))
    return fut.result()
