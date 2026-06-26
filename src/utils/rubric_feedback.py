# -*- coding: utf-8 -*-
"""Lenient parse helpers for rubric vector_reviews envelope strings (AST-724)."""

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


def parse_vector_reviews(
    raw_reviews: Any,
    expected_codes: frozenset[str],
    code_to_uuid: Dict[str, str],
) -> Optional[List[Dict[str, str]]]:
    """Return parsed vector rows or None when unparseable (lenient — caller stores raw FEEDBACK)."""
    if not expected_codes:
        return None
    if not isinstance(raw_reviews, list) or not raw_reviews:
        return None
    parsed_by_code: Dict[str, Dict[str, str]] = {}
    for item in raw_reviews:
        if not isinstance(item, str):
            return None
        one = parse_vector_review_string(item)
        if one is None:
            return None
        code, vals = one
        if code in parsed_by_code:
            return None
        uuid = code_to_uuid.get(code)
        if not uuid:
            return None
        parsed_by_code[code] = {
            "rubric_vector_uuid": uuid,
            "code": code,
            "relevance": vals["relevance"],
            "clarity": vals["clarity"],
            "verdict": vals["verdict"],
        }
    if frozenset(parsed_by_code.keys()) != expected_codes:
        return None
    return [parsed_by_code[c] for c in sorted(parsed_by_code.keys())]


def hydrate_vector_review_strings(
    raw_reviews: Any,
    rubric_by_code: Dict[str, Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Decode compact review strings into display rows (AST-808); partial lists OK."""
    if not isinstance(raw_reviews, list):
        return []
    value_labels = RUBRIC_FEEDBACK_CONFIG.get("value_labels") or {}
    rows: List[Dict[str, str]] = []
    for line in raw_reviews:
        if not isinstance(line, str):
            continue
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


def format_vector_reviews_raw(perf: dict) -> str:
    """Serialize vector_reviews or whole agent_performance for FEEDBACK block storage."""
    if not isinstance(perf, dict):
        return json.dumps(perf)
    if "vector_reviews" in perf:
        return json.dumps(perf.get("vector_reviews"))
    return json.dumps(perf)
