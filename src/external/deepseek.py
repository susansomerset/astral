"""
DeepSeek API client (Anthropic-compatible Messages API at api.deepseek.com/anthropic).

mirror anthropic.py — avoid refactor in this ticket (AST-493).
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from src.utils.cost_calculator import (
    calculate_cost_components_deepseek_from_counts,
    deepseek_usage_to_token_counts,
)
from src.utils.formatting import (
    coerce_grades_encoded_json_parse,
    heal_agent_payload_envelope,
    heal_json,
    looks_like_encoded_grades_text,
    clean_encoded_agent_payload,
)
from src.utils.llm_external import extract_api_response_text, emit_llm_call_debug
from src.utils.logging import get_logger, log_batch_id, log_llm_batch_summary

__all__ = ["send_to_deepseek"]

logger = get_logger(__name__)

import logging as _logging
for _name in ("httpcore", "httpx", "anthropic"):
    _logging.getLogger(_name).setLevel(_logging.WARNING)

try:
    from anthropic import Anthropic
    import httpx as _httpx
except ImportError:  # pragma: no cover
    logger.error("Anthropic SDK not installed. Run: pip install anthropic")
    sys.exit(1)

_API_CALL_TIMEOUT = 5 * 60


def _get_client(api_key_override: Optional[str] = None) -> Anthropic:
    key = api_key_override if api_key_override else os.environ["DEEPSEEK_API_KEY"]
    return Anthropic(api_key=key, base_url="https://api.deepseek.com/anthropic", timeout=_httpx.Timeout(_API_CALL_TIMEOUT))


async def _parse_api_response(response: Dict[str, Any]) -> str:
    """Extract text content from an API response dict (same contract as anthropic.py)."""
    if response is None:
        raise ValueError("API response is None")
    if not response.get("success"):
        raise RuntimeError(f"API call failed: {response.get('error', 'Unknown API error')}")
    api_response = response.get("api_response")
    if not api_response:
        raise ValueError("API response missing from response dict")
    return extract_api_response_text(api_response)


def _parse_json_response(response_text: str) -> Dict[str, Any]:
    """Parse JSON from response text; handles markdown code fences."""
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```\s*$', '', cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, str):
            wrapped = coerce_grades_encoded_json_parse(obj)
            if isinstance(wrapped, dict):
                return wrapped
        return obj
    except json.JSONDecodeError as e:
        if "Extra data" in str(e) and hasattr(e, "pos") and e.pos > 0:  # pragma: no cover
            try:
                return json.loads(cleaned[:e.pos])
            except json.JSONDecodeError:
                pass
        envelope_healed = heal_agent_payload_envelope(cleaned)
        if envelope_healed is not None:
            try:
                return json.loads(envelope_healed)
            except json.JSONDecodeError:
                pass
        healed = heal_json(cleaned)
        if healed is not None:
            try:
                return json.loads(healed)
            except json.JSONDecodeError:
                pass
        if looks_like_encoded_grades_text(cleaned):
            return {"agent_payload": clean_encoded_agent_payload(cleaned)}
        raise ValueError(
            f"Failed to parse JSON response: {e}\n"
            f"Original response (first 500 chars): {response_text[:500]}\n"
            f"Cleaned response (first 500 chars): {cleaned[:500]}"
        )


def _parse_python_code_response(response_text: str) -> Dict[str, Any]:
    """Parse Python code format response (mirror anthropic.py)."""
    import ast

    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```(?:python)?\s*', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```\s*$', '', cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()
    result: Dict[str, Any] = {}

    def _extract_quoted(name: str) -> Optional[str]:
        m = re.search(rf'{re.escape(name)}\s*[=:]\s*"([^"]*)"', cleaned)
        if not m:
            m = re.search(rf"{re.escape(name)}\s*[=:]\s*'([^']*)'", cleaned)
        return m.group(1) if m else None

    parse_result = _extract_quoted("parse_result")
    if parse_result is None or not parse_result.strip():
        parse_result = "success"
    else:
        parse_result = parse_result.strip().lower()
    if parse_result not in ("success", "problem"):
        raise ValueError(f"parse_job_list response parse_result must be 'success' or 'problem', got {parse_result!r}.")
    result["parse_result"] = parse_result

    if parse_result == "problem":
        result["problem_notes"] = (_extract_quoted("problem_notes") or "").strip()
        return result

    val = _extract_quoted("job_container")
    if val is None or not val.strip():
        raise ValueError("parse_job_list response missing required job_container.")
    result["job_container"] = val.strip()

    val = _extract_quoted("job_tag")
    if val is None or not val.strip():
        raise ValueError("parse_job_list response missing required job_tag.")
    result["job_tag"] = val.strip()

    job_ids_match = re.search(r'job_ids\s*[=:]\s*(\[[^\]]*\])', cleaned, re.DOTALL)
    if not job_ids_match:
        job_ids_match = re.search(r'job_ids\s*[=:]\s*\[(.*?)\]', cleaned, re.DOTALL)
    if not job_ids_match:
        raise ValueError("parse_job_list response missing required job_ids.")
    try:
        list_str = job_ids_match.group(1) if job_ids_match.lastindex else ""
        if not list_str.strip().startswith('['):
            list_str = f"[{list_str}]"
        job_ids = ast.literal_eval(list_str)
        if not isinstance(job_ids, list):
            raise ValueError(f"parse_job_list response job_ids must be a list, got {type(job_ids).__name__}")
        result["job_ids"] = job_ids
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"parse_job_list response job_ids could not be parsed as list: {e}") from e

    return result


async def send_to_deepseek(
    content_blocks: List[Dict[str, Any]],
    *,
    system_blocks: Optional[List[Dict[str, Any]]] = None,
    vendor_model: str,
    tier_meta: Dict[str, Any],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    response_format: Optional[str] = None,
    prompt_label: str = "(unknown)",
    candidate_id: Optional[str] = None,
    api_key_override: Optional[str] = None,
    debug: bool = False,
    task_key_uuid: Optional[str] = None,
    no_cache_prompt_tokens: int = 0,
    no_cache_live_tokens: int = 0,
    batch_size: int = 1,
    record_timesheet: Optional[Callable[..., None]] = None,
) -> Dict[str, Any]:
    """Send blocks to DeepSeek Anthropic-compatible API; timesheet via record_timesheet callback."""
    start_time = datetime.now()
    calltime = start_time.strftime("%Y-%m-%d %H:%M:%S")

    if not vendor_model:
        raise ValueError("vendor_model is required for send_to_deepseek")

    _empty_timesheet = lambda: {
        "calltime": calltime,
        "duration": (datetime.now() - start_time).total_seconds(),
        "inputtotal": 0, "inputcached": 0, "outputtotal": 0, "cache_creation_tokens": 0,
    }

    if debug:
        logger.set_debug_flag(True)

    try:
        client = _get_client(api_key_override)

        api_kwargs: Dict[str, Any] = {
            "model": vendor_model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": content_blocks}],
        }
        # DeepSeek thinking (Anthropic-format control): docs/api-docs.deepseek.com/guides/thinking_mode
        if tier_meta.get("thinking"):
            api_kwargs["thinking"] = {"type": "enabled"}
            effort = tier_meta.get("reasoning_effort") or "high"
            if effort not in ("high", "max"):
                effort = "high"
            api_kwargs["output_config"] = {"effort": effort}
        else:
            api_kwargs["thinking"] = {"type": "disabled"}

        thinking_on = bool(tier_meta.get("thinking"))
        if temperature is not None and not thinking_on:
            api_kwargs["temperature"] = temperature

        has_documents = any(isinstance(b, dict) and b.get("type") == "document" for b in content_blocks)
        if has_documents:
            api_kwargs["extra_headers"] = {"anthropic-beta": "files-api-2025-04-14"}

        if system_blocks:
            api_kwargs["system"] = system_blocks

        def _make_api_call():
            return client.messages.create(**api_kwargs)

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(_make_api_call),
                timeout=_API_CALL_TIMEOUT + 10,
            )
            duration = (datetime.now() - start_time).total_seconds()

            usage = response.usage
            counts = deepseek_usage_to_token_counts(usage)
            input_total = counts["cache_miss"]
            input_cached = counts["cache_read"]
            output_total = counts["output"]
            cache_creation_tokens = counts["cache_write"]

            log_llm_batch_summary(
                logger, "deepseek", prompt_label, duration, response=response
            )

            if debug:
                raw_text = extract_api_response_text(response) if response.content else ""
                stop_reason = getattr(response, "stop_reason", "?")
                emit_llm_call_debug(
                    logger_name=__name__,
                    func_name="send_to_deepseek",
                    prompt_label=prompt_label,
                    model=vendor_model,
                    duration=duration,
                    stop_reason=stop_reason,
                    input_total=input_total,
                    input_cached=input_cached,
                    cache_creation_tokens=cache_creation_tokens,
                    output_total=output_total,
                    raw_text=raw_text,
                    provider="deepseek",
                    vendor_detail=f"vendor={vendor_model}",
                )

            try:
                cost_parts = calculate_cost_components_deepseek_from_counts(
                    counts["cache_read"],
                    counts["cache_miss"],
                    counts["output"],
                    counts["cache_write"],
                    vendor_model,
                )
                _timesheet_kwargs = dict(
                    agent_req_id=getattr(response, "id", None),
                    task_key_uuid=task_key_uuid,
                    model_code=vendor_model,
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
                    provider="deepseek",
                )
            except Exception:
                _timesheet_kwargs = None

            timesheet = {
                "calltime": calltime, "duration": duration,
                "inputtotal": input_total, "inputcached": input_cached,
                "outputtotal": output_total, "cache_creation_tokens": cache_creation_tokens,
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
                    log_llm_batch_summary(
                        logger, "deepseek", prompt_label, duration, error=str(parse_err)
                    )
                    if _timesheet_kwargs is not None and record_timesheet is not None:
                        try:
                            record_timesheet(**_timesheet_kwargs, agent_performance="failure", failure_note=str(parse_err))
                        except Exception:
                            pass
                    return {"success": False, "api_response": response, "parsed_response": None, "timesheet": timesheet, "error": str(parse_err)}

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
            log_llm_batch_summary(logger, "deepseek", prompt_label, duration, error=str(e))
            if debug:
                emit_llm_call_debug(
                    logger_name=__name__,
                    func_name="send_to_deepseek",
                    prompt_label=prompt_label,
                    model=vendor_model,
                    duration=duration,
                    stop_reason="error",
                    input_total=0,
                    input_cached=0,
                    cache_creation_tokens=0,
                    output_total=0,
                    error=str(e),
                    provider="deepseek",
                    vendor_detail=f"vendor={vendor_model}",
                )
            return {"success": False, "api_response": None, "timesheet": _empty_timesheet(), "error": str(e)}
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        log_llm_batch_summary(logger, "deepseek", prompt_label, duration, error=str(e))
        if debug:
            emit_llm_call_debug(
                logger_name=__name__,
                func_name="send_to_deepseek",
                prompt_label=prompt_label,
                model=vendor_model,
                duration=duration,
                stop_reason="error",
                input_total=0,
                input_cached=0,
                cache_creation_tokens=0,
                output_total=0,
                error=str(e),
                provider="deepseek",
                vendor_detail=f"vendor={vendor_model}",
            )
        return {"success": False, "api_response": None, "timesheet": _empty_timesheet(), "error": str(e)}
