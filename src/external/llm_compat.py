"""One client for every Anthropic-Messages-compatible server in LLM_SERVER_CONFIG (AST-1851).

Parameterized by server id + SKU; key always passed by the caller (no env fallback).
"""

import random
import threading
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from anthropic import Anthropic, RateLimitError
import httpx as _httpx

from src.external.anthropic import _parse_api_response, _parse_json_response, _parse_python_code_response
from src.utils.config import PROVIDER_EMPTY_RESPONSE, get_llm_server
from src.utils.cost_calculator import calculate_cost_components_from_counts, usage_to_token_counts
from src.utils.integration_io import require_controlled_external_io
from src.utils.llm_external import (
    await_provider_call_with_budget,
    classify_provider_balance_refusal,
    classify_provider_call_timeout,
    is_unusable_provider_response,
    normalize_provider_error,
    provider_call_http_timeout_seconds,
    provider_call_max_retries,
    provider_call_timeout_error_message,
    provider_call_wait_timeout_seconds,
)
from src.utils.logging import get_logger, log_batch_id, log_llm_batch_summary

__all__ = ["send_to_llm_compat"]

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
    """Blocking messages.create in a worker thread; servers with a concurrency block get a
    process-wide slot cap and jittered 429 backoff (slot held only during the call)."""
    if not concurrency:
        return client.messages.create(**api_kwargs)
    with _slots_lock:
        sem = _slots.setdefault(server_id, threading.BoundedSemaphore(int(concurrency["max_concurrent"])))
    attempts = int(concurrency["rate_limit_retries"]) + 1
    base = float(concurrency["backoff_base_seconds"])
    cap = float(concurrency["backoff_max_seconds"])
    for attempt in range(attempts):
        try:
            with sem:
                return client.messages.create(**api_kwargs)
        except RateLimitError:
            if attempt == attempts - 1:
                raise
            delay = min(base * (2 ** attempt), cap) * random.uniform(0.5, 1.0)
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
) -> Dict[str, Any]:
    """Send blocks to the server's Anthropic-compatible API; timesheet via record_timesheet callback."""
    require_controlled_external_io("llm_compat.send_to_llm_compat")
    server = get_llm_server(server_id)
    if server["protocol"] != "anthropic_compat":
        raise ValueError(f"Server {server_id!r} is not anthropic_compat")
    if not sku:
        raise ValueError("sku is required for send_to_llm_compat")
    if not api_key:
        raise ValueError(f"No API key for server {server_id!r}")

    start_time = datetime.now()
    calltime = start_time.strftime("%Y-%m-%d %H:%M:%S")

    _empty_timesheet = lambda: {
        "calltime": calltime,
        "duration": (datetime.now() - start_time).total_seconds(),
        "inputtotal": 0, "inputcached": 0, "outputtotal": 0, "cache_creation_tokens": 0,
    }

    try:
        client = _get_client(server, api_key)

        api_kwargs: Dict[str, Any] = {
            "model": sku,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": content_blocks}],
        }
        # Thinking + server extras + brain-size extras (OpenRouter provider pin) are vendor body fields
        # taken verbatim from config; later wins on key collision, so the size's extras beat the server's.
        thinking_on = bool(tier.get("thinking"))
        thinking_body = (tier.get("thinking_params") or {}) if thinking_on else server["thinking_off_params"]
        api_kwargs["extra_body"] = {**thinking_body, **server["request_extras"], **tier.get("request_extras", {})}
        if temperature is not None and not thinking_on:
            api_kwargs["temperature"] = temperature
        if system_blocks:
            api_kwargs["system"] = system_blocks

        def _make_api_call():
            return _create(client, api_kwargs, server_id, server["concurrency"])

        try:
            logger.debug("Calling messages.create: server=%s %s", server_id, api_kwargs)
            response = await await_provider_call_with_budget(
                _make_api_call,
                timeout_seconds=provider_call_wait_timeout_seconds(),
            )
            logger.debug("Response from messages.create: %s", response)
            duration = (datetime.now() - start_time).total_seconds()

            counts = usage_to_token_counts(response.usage)
            input_total = counts["cache_miss"]
            input_cached = counts["cache_read"]
            output_total = counts["output"]
            cache_creation_tokens = counts["cache_write"]

            try:
                cost_parts = calculate_cost_components_from_counts(
                    counts["cache_read"],
                    counts["cache_miss"],
                    counts["output"],
                    counts["cache_write"],
                    sku=sku,
                    server_id=server_id,
                )
                _timesheet_kwargs = dict(
                    agent_req_id=getattr(response, "id", None),
                    task_key_uuid=task_key_uuid,
                    model_code=sku,
                    candidate_id=candidate_id,
                    batch_id=log_batch_id.get(),
                    batch_size=batch_size,
                    cache_write_tokens=counts["cache_write"],
                    cache_read_tokens=counts["cache_read"],
                    no_cache_prompt_tokens=no_cache_prompt_tokens,
                    no_cache_live_tokens=no_cache_live_tokens,
                    total_no_cache_input_tokens=counts["cache_miss"],
                    total_output_tokens=counts["output"],
                    calc_cost_cache_write=cost_parts["calc_cost_cache_write"],
                    calc_cost_cache_read=cost_parts["calc_cost_cache_read"],
                    calc_cost_no_cache_input=cost_parts["calc_cost_no_cache_input"],
                    calc_cost_output=cost_parts["calc_cost_output"],
                    provider=server_id,
                )
            except Exception:
                _timesheet_kwargs = None

            timesheet = {
                "calltime": calltime, "duration": duration,
                "inputtotal": input_total, "inputcached": input_cached,
                "outputtotal": output_total, "cache_creation_tokens": cache_creation_tokens,
            }

            # Hollow response: fail before healthy INFO summary (AST-1190).
            if is_unusable_provider_response(
                response,
                input_tokens=input_total + input_cached,
                output_tokens=output_total,
            ):
                err = PROVIDER_EMPTY_RESPONSE["error"]
                log_llm_batch_summary(logger, server_id, prompt_label, duration, error=err)
                if _timesheet_kwargs is not None and record_timesheet is not None:
                    try:
                        record_timesheet(
                            **_timesheet_kwargs,
                            agent_performance="failure",
                            failure_note=err,
                        )
                    except Exception:
                        pass
                return {
                    "success": False,
                    "api_response": response,
                    "parsed_response": None,
                    "timesheet": timesheet,
                    "error": err,
                    "failure_class": PROVIDER_EMPTY_RESPONSE["failure_class"],
                }

            log_llm_batch_summary(
                logger, server_id, prompt_label, duration, response=response
            )

            # JSON cut mid-string when output hits max_tokens — fail closed, do not heal (AST-903).
            stop_reason = getattr(response, "stop_reason", None)
            if response_format == "json" and stop_reason == "max_tokens":
                trunc_err = "Generation truncated (max_tokens) before complete JSON"
                log_llm_batch_summary(
                    logger, server_id, prompt_label, duration, error=trunc_err
                )
                if _timesheet_kwargs is not None and record_timesheet is not None:
                    try:
                        record_timesheet(
                            **_timesheet_kwargs,
                            agent_performance="failure",
                            failure_note=trunc_err,
                        )
                    except Exception:
                        pass
                return {
                    "success": False,
                    "api_response": response,
                    "parsed_response": None,
                    "timesheet": timesheet,
                    "error": trunc_err,
                    "failure_class": "max_tokens",
                }

            parsed_response = None
            if response_format:
                if response_format not in ("text", "json", "python"):
                    raise ValueError(f"Invalid response_format: {response_format}")
                response_dict = {"success": True, "api_response": response, "timesheet": timesheet}
                try:
                    if response_format == "text":
                        parsed_response = await _parse_api_response(response_dict)
                    elif response_format == "json":
                        parsed_response = _parse_json_response(await _parse_api_response(response_dict))
                    elif response_format == "python":
                        parsed_response = _parse_python_code_response(await _parse_api_response(response_dict))
                except Exception as parse_err:
                    parse_err_msg = normalize_provider_error(parse_err)
                    log_llm_batch_summary(
                        logger, server_id, prompt_label, duration, error=parse_err_msg
                    )
                    if _timesheet_kwargs is not None and record_timesheet is not None:
                        try:
                            record_timesheet(
                                **_timesheet_kwargs,
                                agent_performance="failure",
                                failure_note=parse_err_msg,
                            )
                        except Exception:
                            pass
                    return {
                        "success": False,
                        "api_response": response,
                        "parsed_response": None,
                        "timesheet": timesheet,
                        "error": parse_err_msg,
                    }

            _ap_status = "success"
            _ap_note = None
            if isinstance(parsed_response, dict):
                ap = parsed_response.get("agent_performance")
                if isinstance(ap, dict):
                    _ap_status = ap.get("status") or "success"
                    _ap_note = ap.get("failure_note")

            if _timesheet_kwargs is not None and record_timesheet is not None:
                try:
                    record_timesheet(**_timesheet_kwargs, agent_performance=_ap_status, failure_note=_ap_note)
                except Exception:
                    pass

            return {"success": True, "api_response": response, "parsed_response": parsed_response, "timesheet": timesheet}

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            fc_timeout = classify_provider_call_timeout(e)
            if fc_timeout:
                err = provider_call_timeout_error_message()
            else:
                err = normalize_provider_error(e)
            log_llm_batch_summary(logger, server_id, prompt_label, duration, error=err)
            out = {"success": False, "api_response": None, "timesheet": _empty_timesheet(), "error": err}
            if fc_timeout:
                out["failure_class"] = fc_timeout
            else:
                fc = classify_provider_balance_refusal(e)
                if fc:
                    out["failure_class"] = fc
            return out
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        fc_timeout = classify_provider_call_timeout(e)
        if fc_timeout:
            err = provider_call_timeout_error_message()
        else:
            err = normalize_provider_error(e)
        log_llm_batch_summary(logger, server_id, prompt_label, duration, error=err)
        out = {"success": False, "api_response": None, "timesheet": _empty_timesheet(), "error": err}
        if fc_timeout:
            out["failure_class"] = fc_timeout
        else:
            fc = classify_provider_balance_refusal(e)
            if fc:
                out["failure_class"] = fc
        return out
