"""
Anthropic API client module.

External service layer: pure API client only.
Sends assembled content blocks to Anthropic; optional `record_timesheet` callback
(from core) persists cost rows. No business logic.

Public API: send_to_anthropic, get_receipt, getTimestampPrefix
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from src.utils.config import ASTRAL_CONFIG
from src.utils.formatting import (
    heal_agent_payload_envelope,
    heal_json,
)
from src.utils.llm_external import (
    extract_api_response_text,
    provider_call_http_timeout_seconds,
    provider_call_max_retries,
)
from src.utils.logging import get_logger

__all__ = ["send_to_anthropic", "getTimestampPrefix"]

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

def _get_client() -> Anthropic:  # pragma: no cover
    """Get initialized Anthropic client with API key from environment."""
    apiKey = os.environ.get("ANTHROPIC_API_KEY")
    if not apiKey:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    return Anthropic(
        api_key=apiKey,
        timeout=_httpx.Timeout(provider_call_http_timeout_seconds()),
        max_retries=provider_call_max_retries(),
    )


def getTimestampPrefix(structured: bool = False) -> str:
    """Generate timestamp prefix for user prompts.

    structured=True swaps the two-key envelope sentence for prompt_prefix_structured (forced-tool calls, AST-2172).
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

    envelope_instruction = ASTRAL_CONFIG.get("prompt_prefix_structured" if structured else "prompt_prefix", "")
    return (
        f"Today is {dayOfWeek}, {date}, and it's {hour12}:{minute}{ampm} Pacific time. "
        f"{envelope_instruction}\n"
    )


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


def _effort_body(reasoning_effort: Optional[str]) -> Dict[str, Any]:
    """The agent's reasoning_effort as Messages-protocol body fields, sent as stored (AST-1956).
    "none" turns thinking off; any other value goes in output_config.effort; empty sends nothing.
    No vocabulary and no per-model check — an endpoint that rejects it fails the call."""
    if not reasoning_effort:
        return {}
    if reasoning_effort == "none":
        return {"thinking": {"type": "disabled"}}
    return {"output_config": {"effort": reasoning_effort}}


def _forced_tool_body(forced_tool: Dict[str, Any]) -> Dict[str, Any]:
    """One forced tool as Messages-protocol kwargs (AST-2172): the model must answer by calling it."""
    name = forced_tool["name"]
    return {
        "tools": [{"name": name, "input_schema": forced_tool["input_schema"]}],
        "tool_choice": {"type": "tool", "name": name},
    }


async def send_to_anthropic(
    content_blocks: List[Dict[str, Any]],
    *,
    system_blocks: Optional[List[Dict[str, Any]]] = None,
    model_code: Optional[str] = None,
    temperature: Optional[float] = None,
    reasoning_effort: Optional[str] = None,
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
    forced_tool: Optional[Dict[str, Any]] = None,
    request_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    ) -> Dict[str, Any]:
    raise RuntimeError(
        "send_to_anthropic retired (AST-2239); use src.external.astral_agent.submit with an assembled provider request"
    )


def get_receipt(external_ids: List[str], api_key: str) -> List[Dict[str, Any]]:
    """Zero-stub receipts (AST-2217). No network. platform_cost always None."""
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
