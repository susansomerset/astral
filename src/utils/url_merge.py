"""Merge query strings into a base URL (board search deeplink). Split from playwright so that
module stays within component branch-coverage locks while tests mock navigation."""

from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def merge_url_query_params(entry_url: str, query_params: Optional[Dict[str, Any]]) -> str:
    """Strip entry_url, merge existing query with query_params (None values skipped), return final URL."""
    parsed = urlparse(entry_url.strip())
    merged: Dict[str, str] = {}
    if parsed.query:
        merged.update(dict(parse_qsl(parsed.query, keep_blank_values=True)))
    for k, v in (query_params or {}).items():
        if v is not None:
            merged[str(k)] = str(v)
    new_query = urlencode(list(merged.items())) if merged else ""
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, new_query, "", ""))
