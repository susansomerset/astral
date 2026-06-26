# -*- coding: utf-8 -*-
"""Lenient parse, diagnostic, and pipeline trace helpers for vector_reviews (AST-724 / AST-816 / AST-820)."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from src.utils.config import RUBRIC_FEEDBACK_CONFIG

_VECTOR_REVIEW_RE = re.compile(
    r"^([A-Za-z0-9]+)R([AOSRN])C([AOSRN])V([KED])$",
    re.IGNORECASE,
)
_REL_VALUES = frozenset(RUBRIC_FEEDBACK_CONFIG["feedback_types"]["relevance"]["value_codes"])
_CLA_VALUES = frozenset(RUBRIC_FEEDBACK_CONFIG["feedback_types"]["clarity"]["value_codes"])
_VER_VALUES = frozenset(RUBRIC_FEEDBACK_CONFIG["feedback_types"]["verdict"]["value_codes"])


def parse_vector_review_string(line: str) -> Optional[Tuple[str, Dict[str, str]]]:
    """Parse one compact review string; return (CODE_UPPER, {relevance, clarity, verdict}) or None."""
    if not isinstance(line, str) or not line.strip():
        return None
    m = _VECTOR_REVIEW_RE.match(line.strip())
    if not m:
        return None
    code = m.group(1).upper()
    rel, cla, ver = m.group(2).upper(), m.group(3).upper(), m.group(4).upper()
    if rel not in _REL_VALUES or cla not in _CLA_VALUES or ver not in _VER_VALUES:
        return None
    return code, {"relevance": rel, "clarity": cla, "verdict": ver}


def normalize_vector_reviews_raw(raw: Any) -> Optional[List[str]]:
    """Coerce vector_reviews envelope value to a non-empty list of stripped strings (AST-816)."""
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return None
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return None
    if not isinstance(raw, list) or not raw:
        return None
    out: List[str] = []
    for item in raw:
        if not isinstance(item, str):
            return None
        line = item.strip()
        if not line:
            return None
        out.append(line)
    return out or None


def parse_vector_reviews_diagnostic(
    raw_reviews: Any,
    expected_codes: frozenset[str],
    code_to_uuid: Dict[str, str],
) -> tuple[Optional[List[Dict[str, str]]], Optional[str], frozenset[str], frozenset[str]]:
    """Return (rows, failure_reason, parsed_codes, missing_codes) — strict match vs expected (AST-816)."""
    empty: frozenset[str] = frozenset()
    if not expected_codes:
        return None, "empty_expected", empty, empty
    raw_list = normalize_vector_reviews_raw(raw_reviews)
    if raw_list is None:
        return None, "not_list", empty, empty
    parsed_by_code: Dict[str, Dict[str, str]] = {}
    for item in raw_list:
        one = parse_vector_review_string(item)
        if one is None:
            return None, "bad_line", frozenset(parsed_by_code.keys()), empty
        code, vals = one
        if code in parsed_by_code:
            return None, "duplicate_code", frozenset(parsed_by_code.keys()), empty
        uuid = code_to_uuid.get(code)
        if not uuid:
            return None, "unknown_code", frozenset(parsed_by_code.keys()), empty
        parsed_by_code[code] = {
            "rubric_vector_uuid": uuid,
            "code": code,
            "relevance": vals["relevance"],
            "clarity": vals["clarity"],
            "verdict": vals["verdict"],
        }
    parsed_codes = frozenset(parsed_by_code.keys())
    if parsed_codes != expected_codes:
        missing = expected_codes - parsed_codes
        if missing:
            return None, "missing_codes", parsed_codes, missing
        return None, "extra_codes", parsed_codes, empty
    rows = [parsed_by_code[c] for c in sorted(parsed_by_code.keys())]
    return rows, None, parsed_codes, empty


def parse_vector_reviews(
    raw_reviews: Any,
    expected_codes: frozenset[str],
    code_to_uuid: Dict[str, str],
) -> Optional[List[Dict[str, str]]]:
    """Return parsed vector rows or None when unparseable (lenient — caller stores raw FEEDBACK)."""
    rows, _, _, _ = parse_vector_reviews_diagnostic(raw_reviews, expected_codes, code_to_uuid)
    return rows


def hydrate_vector_review_strings(
    raw_reviews: Any,
    rubric_by_code: Dict[str, Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Decode compact review strings into display rows (AST-808); partial lists OK."""
    raw_list = normalize_vector_reviews_raw(raw_reviews)
    if not raw_list:
        return []
    value_labels = RUBRIC_FEEDBACK_CONFIG.get("value_labels") or {}
    rows: List[Dict[str, str]] = []
    for line in raw_list:
        parsed = parse_vector_review_string(line)
        if parsed is None:
            continue
        code, vals = parsed
        rubric = rubric_by_code.get(code.upper()) or {}
        rows.append({
            "compact": line,
            "code": code,
            "label": str(rubric.get("label") or code),
            "content": str(rubric.get("content") or ""),
            "importance": str(rubric.get("importance") or ""),
            "relevance": vals["relevance"],
            "clarity": vals["clarity"],
            "verdict": vals["verdict"],
            "relevance_label": value_labels.get(vals["relevance"], vals["relevance"]),
            "clarity_label": value_labels.get(vals["clarity"], vals["clarity"]),
            "verdict_label": value_labels.get(vals["verdict"], vals["verdict"]),
        })
    return rows


def format_hydrated_review_debug_line(row: Dict[str, str]) -> str:
    """Single-line debug summary: code, label, R/C/V labels, criterion preview (AST-816)."""
    code = str(row.get("code") or "")
    label = str(row.get("label") or code)
    rel = str(row.get("relevance_label") or row.get("relevance") or "")
    cla = str(row.get("clarity_label") or row.get("clarity") or "")
    ver = str(row.get("verdict_label") or row.get("verdict") or "")
    content = str(row.get("content") or "")
    if len(content) > 80:
        content = content[:80] + "…"
    return f"{code} {label} — R/{rel} C/{cla} V/{ver} — {content}"


def _trace_repr_truncated(raw: Any, limit: int = 120) -> str:
    text = repr(raw)
    if len(text) > limit:
        return text[:limit] + "…"
    return text


def _normalize_failure_reason(raw: Any) -> str:
    if raw is None:
        return "missing"
    if isinstance(raw, str):
        stripped = raw.strip()
        if not stripped:
            return "empty_string"
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return "json_decode"
        if not isinstance(parsed, list):
            return "json_not_list"
        raw = parsed
    if isinstance(raw, list):
        if not raw:
            return "empty_list"
        for item in raw:
            if not isinstance(item, str):
                return "non_string_element"
            if not item.strip():
                return "empty_line"
        return "unknown"
    return f"bad_type_{type(raw).__name__}"


def vector_reviews_pipeline_trace(
    *,
    raw_reviews: Any,
    expected_codes: frozenset[str],
    code_to_uuid: Dict[str, str],
    rubric_by_code: Dict[str, Dict[str, Any]],
    candidate_id: str = "",
    owner_task_key: str = "",
) -> List[str]:
    """Ordered debug_detail lines for normalize → parse → hydrate (AST-820); no logging side effects."""
    lines: List[str] = [
        f"vector_reviews trace candidate={candidate_id} owner={owner_task_key}",
        f"raw type={type(raw_reviews).__name__} repr={_trace_repr_truncated(raw_reviews)}",
    ]
    raw_list = normalize_vector_reviews_raw(raw_reviews)
    if raw_list is None:
        lines.append(f"normalize -> None (reason={_normalize_failure_reason(raw_reviews)})")
    else:
        lines.append(f"normalize -> {len(raw_list)} lines")
    lines.append(f"expected_codes={sorted(expected_codes)} count={len(expected_codes)}")
    lines.append(
        f"rubric_lookup_keys={sorted(rubric_by_code.keys())} count={len(rubric_by_code)}"
    )
    for idx, compact in enumerate(raw_list or []):
        parsed = parse_vector_review_string(compact)
        if parsed is None:
            lines.append(f"line[{idx}] {compact} parse=fail")
        else:
            code, _ = parsed
            lines.append(f"line[{idx}] {compact} parse=ok code={code}")
    _, reason, parsed_codes, missing_codes = parse_vector_reviews_diagnostic(
        raw_reviews, expected_codes, code_to_uuid
    )
    extra = sorted(parsed_codes - expected_codes) if parsed_codes else []
    lines.append(
        f"diagnostic reason={reason or 'ok'} parsed={sorted(parsed_codes)} "
        f"missing={sorted(missing_codes)} extra={extra}"
    )
    hydrated = hydrate_vector_review_strings(
        raw_list if raw_list is not None else raw_reviews,
        rubric_by_code,
    )
    lines.append(f"hydrate rows={len(hydrated)}")
    for row in hydrated[:7]:
        lines.append(format_hydrated_review_debug_line(row))
    return lines


def format_vector_reviews_raw(perf: dict) -> str:
    """Serialize vector_reviews or whole agent_performance for FEEDBACK block storage."""
    if not isinstance(perf, dict):
        return json.dumps(perf)
    if "vector_reviews" in perf:
        return json.dumps(perf.get("vector_reviews"))
    return json.dumps(perf)
