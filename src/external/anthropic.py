"""
Anthropic API client module.

External service layer: pure API client only.
Sends assembled content blocks to Anthropic; optional `record_timesheet` callback
(from core) persists cost rows. No business logic.

Public API: send_to_anthropic, getTimestampPrefix
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from src.utils.cost_calculator import calculate_cost_with_cache, calculate_cost_components
from src.utils.config import ASTRAL_CONFIG, get_model, CHARS_PER_TOKEN
from src.utils.formatting import (
    coerce_grades_encoded_json_parse,
    heal_agent_payload_envelope,
    heal_json,
    looks_like_encoded_grades_text,
    clean_encoded_agent_payload,
)
from src.utils.logging import get_logger, log_batch_id, log_llm_batch_summary

__all__ = ["send_to_anthropic", "getTimestampPrefix", "extract_api_response_text"]

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

_API_CALL_TIMEOUT = 5 * 60  # 5 minutes per call


def _get_client() -> Anthropic:  # pragma: no cover
    """Get initialized Anthropic client with API key from environment."""
    apiKey = os.environ.get("ANTHROPIC_API_KEY")
    if not apiKey:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    return Anthropic(api_key=apiKey, timeout=_httpx.Timeout(_API_CALL_TIMEOUT))


def getTimestampPrefix() -> str:
    """Generate timestamp prefix for user prompts.

    Returns: Formatted timestamp string
    Example: "Today is Thursday, 11/6/25, and it's 3:18pm Pacific time.\\n"
    """
    now = datetime.now()
    dayOfWeek = now.strftime('%A')
    date = now.strftime('%-m/%-d/%y')
    hour = now.hour
    minute = now.strftime('%M')
    ampm = 'am' if hour < 12 else 'pm'
    hour12 = hour if hour <= 12 else hour - 12
    if hour12 == 0:
        hour12 = 12

    envelope_instruction = ASTRAL_CONFIG.get("prompt_prefix", "")
    return (
        f"Today is {dayOfWeek}, {date}, and it's {hour12}:{minute}{ampm} Pacific time. "
        f"{envelope_instruction}\n"
    )


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


def _emit_llm_call_debug(
    *,
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
    dbg = get_logger(__name__, debug_flag=True)
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


async def _parse_api_response(response: Dict[str, Any]) -> str:
    """Extract text content from an API response dict."""
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
                pass  # pragma: no cover
        envelope_healed = heal_agent_payload_envelope(cleaned)
        if envelope_healed is not None:  # pragma: no cover
            try:
                return json.loads(envelope_healed)
            except json.JSONDecodeError:
                pass  # pragma: no cover
        healed = heal_json(cleaned)
        if healed is not None:  # pragma: no cover
            try:
                return json.loads(healed)
            except json.JSONDecodeError:
                pass  # pragma: no cover
        if looks_like_encoded_grades_text(cleaned):
            return {"agent_payload": clean_encoded_agent_payload(cleaned)}
        raise ValueError(
            f"Failed to parse JSON response: {e}\n"
            f"Original response (first 500 chars): {response_text[:500]}\n"
            f"Cleaned response (first 500 chars): {cleaned[:500]}"
        )


def _parse_python_code_response(response_text: str) -> Dict[str, Any]:
    """Parse Python code format response (parse_job_list task). Snake_case only; fails loudly."""
    import ast

    cleaned = response_text.strip()
    if cleaned.startswith("```"):  # pragma: no cover
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
    if parse_result is None or not parse_result.strip():  # pragma: no cover
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
        raise ValueError(f"parse_job_list response missing required job_container.")
    result["job_container"] = val.strip()

    val = _extract_quoted("job_tag")
    if val is None or not val.strip():
        raise ValueError(f"parse_job_list response missing required job_tag.")
    result["job_tag"] = val.strip()

    job_ids_match = re.search(r'job_ids\s*[=:]\s*(\[[^\]]*\])', cleaned, re.DOTALL)
    if not job_ids_match:
        job_ids_match = re.search(r'job_ids\s*[=:]\s*\[(.*?)\]', cleaned, re.DOTALL)
    if not job_ids_match:
        raise ValueError(f"parse_job_list response missing required job_ids.")
    try:
        list_str = job_ids_match.group(1) if job_ids_match.lastindex else ""
        if not list_str.strip().startswith('['):  # pragma: no cover
            list_str = f"[{list_str}]"
        job_ids = ast.literal_eval(list_str)
        if not isinstance(job_ids, list):  # pragma: no cover
            raise ValueError(f"parse_job_list response job_ids must be a list, got {type(job_ids).__name__}")
        result["job_ids"] = job_ids
    except (ValueError, SyntaxError) as e:  # pragma: no cover
        raise ValueError(f"parse_job_list response job_ids could not be parsed as list: {e}") from e

    return result


async def send_to_anthropic(
    content_blocks: List[Dict[str, Any]],
    *,
    system_blocks: Optional[List[Dict[str, Any]]] = None,
    model_code: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    response_format: Optional[str] = None,
    prompt_label: str = "(unknown)",
    candidate_id: Optional[str] = None,
    enable_web_search: bool = False,
    api_key_override: Optional[str] = None,
    debug: bool = False,
    task_key_uuid: Optional[str] = None,
    no_cache_prompt_tokens: int = 0,
    no_cache_live_tokens: int = 0,
    batch_size: int = 1,
    record_timesheet: Optional[Callable[..., None]] = None,
    ) -> Dict[str, Any]:
    """Send assembled content blocks to Anthropic; optional DB timesheet via record_timesheet.

    system_blocks → API `system` param (supports cache_control).
    content_blocks → messages[user].
    Returns dict with success, api_response, parsed_response, timesheet, error."""
    start_time = datetime.now()
    calltime = start_time.strftime("%Y-%m-%d %H:%M:%S")

    if not model_code:
        raise ValueError("model_code is required for send_to_anthropic")

    _empty_timesheet = lambda: {
        "calltime": calltime,
        "duration": (datetime.now() - start_time).total_seconds(),
        "inputtotal": 0, "inputcached": 0, "outputtotal": 0, "cache_creation_tokens": 0,
    }

    if debug:
        logger.set_debug_flag(True)

    try:
        client = Anthropic(api_key=api_key_override, timeout=_httpx.Timeout(_API_CALL_TIMEOUT)) if api_key_override else _get_client()

        api_kwargs: Dict[str, Any] = {
            "model": model_code,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": content_blocks}],
        }
        if system_blocks:
            api_kwargs["system"] = system_blocks

        has_documents = any(isinstance(b, dict) and b.get("type") == "document" for b in content_blocks)
        if has_documents:
            api_kwargs["extra_headers"] = {"anthropic-beta": "files-api-2025-04-14"}

        if enable_web_search:
            api_kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]

        def _make_api_call():
            return client.messages.create(**api_kwargs)

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(_make_api_call),
                timeout=_API_CALL_TIMEOUT + 10,
            )
            duration = (datetime.now() - start_time).total_seconds()

            usage = response.usage
            input_total = usage.input_tokens
            input_cached = getattr(usage, "cache_read_input_tokens", 0)
            output_total = usage.output_tokens
            cache_creation_tokens = getattr(usage, "cache_creation_input_tokens", 0) or 0

            log_llm_batch_summary(
                logger, "anthropic", prompt_label, duration, response=response
            )

            if debug:
                raw_text = extract_api_response_text(response) if response.content else ""
                stop_reason = getattr(response, "stop_reason", "?")
                _emit_llm_call_debug(
                    func_name="send_to_anthropic",
                    prompt_label=prompt_label,
                    model=model_code,
                    duration=duration,
                    stop_reason=stop_reason,
                    input_total=input_total,
                    input_cached=input_cached,
                    cache_creation_tokens=cache_creation_tokens,
                    output_total=output_total,
                    raw_text=raw_text,
                    provider="anthropic",
                )

            try:
                cost_parts = calculate_cost_components(usage, model_code)
                _timesheet_kwargs = dict(
                    agent_req_id=getattr(response, "id", None),
                    task_key_uuid=task_key_uuid,
                    model_code=model_code,
                    candidate_id=candidate_id,
                    batch_id=log_batch_id.get(),
                    batch_size=batch_size,
                    cache_write_tokens=cache_creation_tokens,
                    cache_read_tokens=input_cached,
                    no_cache_prompt_tokens=no_cache_prompt_tokens,
                    no_cache_live_tokens=no_cache_live_tokens,
                    total_no_cache_input_tokens=input_total,
                    total_output_tokens=output_total,
                    calc_cost_cache_write=cost_parts["calc_cost_cache_write"],
                    calc_cost_cache_read=cost_parts["calc_cost_cache_read"],
                    calc_cost_no_cache_input=cost_parts["calc_cost_no_cache_input"],
                    calc_cost_output=cost_parts["calc_cost_output"],
                    provider="anthropic",
                )
            except Exception:  # pragma: no cover
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
                    elif response_format == "python":  # pragma: no cover
                        parsed_response = _parse_python_code_response(await _parse_api_response(response_dict))
                except Exception as parse_err:  # pragma: no cover
                    log_llm_batch_summary(
                        logger, "anthropic", prompt_label, duration, error=str(parse_err)
                    )
                    if _timesheet_kwargs is not None and record_timesheet is not None:
                        try:
                            record_timesheet(**_timesheet_kwargs, agent_performance="failure", failure_note=str(parse_err))
                        except Exception:  # pragma: no cover
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
            log_llm_batch_summary(logger, "anthropic", prompt_label, duration, error=str(e))
            if debug:
                _emit_llm_call_debug(
                    func_name="send_to_anthropic",
                    prompt_label=prompt_label,
                    model=model_code,
                    duration=duration,
                    stop_reason="error",
                    input_total=0,
                    input_cached=0,
                    cache_creation_tokens=0,
                    output_total=0,
                    error=str(e),
                    provider="anthropic",
                )
            return {"success": False, "api_response": None, "timesheet": _empty_timesheet(), "error": str(e)}
    except Exception as e:  # pragma: no cover
        duration = (datetime.now() - start_time).total_seconds()
        log_llm_batch_summary(logger, "anthropic", prompt_label, duration, error=str(e))
        if debug:
            _emit_llm_call_debug(
                func_name="send_to_anthropic",
                prompt_label=prompt_label,
                model=model_code,
                duration=duration,
                stop_reason="error",
                input_total=0,
                input_cached=0,
                cache_creation_tokens=0,
                output_total=0,
                error=str(e),
                provider="anthropic",
            )
        return {"success": False, "api_response": None, "timesheet": _empty_timesheet(), "error": str(e)}
