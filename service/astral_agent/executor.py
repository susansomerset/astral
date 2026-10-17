"""Live provider executor — assembled request dict in, result dict out.

Signature stays ``async def execute(request: dict) -> dict`` for worker.py.
"""

from __future__ import annotations

from typing import Any, Dict

from providers.errors import ProviderJobError
from providers import anthropic_provider, llm_compat_provider

_REQUIRED = ("protocol", "server_id", "model", "api_key", "messages", "max_tokens")


def _require(request: Dict[str, Any]) -> None:
    if not isinstance(request, dict):
        raise ProviderJobError("bad_request", "request must be a dict")
    missing = [key for key in _REQUIRED if request.get(key) in (None, "")]
    if missing:
        raise ProviderJobError("bad_request", "missing " + ", ".join(missing))
    if not isinstance(request["messages"], list):
        raise ProviderJobError("bad_request", "messages must be a list")
    protocol = request["protocol"]
    if protocol not in ("anthropic", "anthropic_compat"):
        raise ProviderJobError("bad_request", f"unknown protocol {protocol!r}")
    if protocol == "anthropic_compat":
        if not request.get("base_url"):
            raise ProviderJobError("bad_request", "base_url required for anthropic_compat")
        if request.get("auth") not in ("x-api-key", "bearer"):
            raise ProviderJobError("bad_request", "auth must be x-api-key or bearer")


async def execute(request: dict) -> Dict[str, Any]:
    _require(request)
    if request["protocol"] == "anthropic":
        return await anthropic_provider.send(request)
    return await llm_compat_provider.send(request)
