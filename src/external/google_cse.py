"""Google Custom Search JSON API v1 client (external layer only).

Thin HTTP wrapper: no logging here (see ASTRAL_CODE_RULES §2.5 / §3.2).
Callers and spike scripts surface human-facing errors.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from typing import Sequence, TypedDict

import requests

from src.utils.config import GOOGLE_CSE_CONFIG
from src.utils.integration_io import require_controlled_external_io

GOOGLE_CSE_API_URL = "https://www.googleapis.com/customsearch/v1"
_DEFAULT_REQUEST_TIMEOUT_SEC = 60

_last_cse_request_at: float | None = None

__all__ = ["GoogleCseHit", "search_google_cse"]


class GoogleCseHit(TypedDict):
    title: str
    url: str
    snippet: str


def _item_to_hit(item: object) -> GoogleCseHit:
    row = item if isinstance(item, dict) else {}
    title = row.get("title")
    snippet = row.get("snippet")
    link = row.get("link")
    return {
        "title": title if isinstance(title, str) else "",
        "url": link if isinstance(link, str) else "",
        "snippet": snippet if isinstance(snippet, str) else "",
    }


def _truncate_body(text: str, limit: int = 500) -> str:
    t = text if len(text) <= limit else text[:limit] + "…"
    return t


def _next_start_index(parsed: dict) -> int | None:
    queries = parsed.get("queries") if isinstance(parsed.get("queries"), dict) else {}
    next_pages = queries.get("nextPage")
    if not isinstance(next_pages, list) or not next_pages:
        return None
    first = next_pages[0]
    if not isinstance(first, dict) or "startIndex" not in first:
        return None
    raw = first["startIndex"]
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _pace_detail_emit(pace_detail: Callable[[str], None] | None, message: str) -> None:
    if pace_detail is not None:
        pace_detail(message)


def _is_rate_limit_response(status_code: int, parsed: dict | None) -> bool:
    if status_code == 429:
        return True
    if not isinstance(parsed, dict):
        return False
    err_obj = parsed.get("error")
    if not isinstance(err_obj, dict):
        return False
    code = err_obj.get("code")
    if code == 429 or code == "429":
        return True
    errors = err_obj.get("errors")
    if isinstance(errors, list):
        for row in errors:
            if isinstance(row, dict) and row.get("reason") == "rateLimitExceeded":
                return True
    return False


def _apply_inter_query_delay(pace_detail: Callable[[str], None] | None) -> None:
    global _last_cse_request_at
    delay = float(GOOGLE_CSE_CONFIG["inter_query_delay_sec"])
    if delay <= 0:
        return
    if _last_cse_request_at is None:
        return
    elapsed = time.monotonic() - _last_cse_request_at
    wait = delay - elapsed
    if wait > 0:
        _pace_detail_emit(
            pace_detail,
            f"pacing: sleeping {wait:.2f}s before CSE HTTP request",
        )
        time.sleep(wait)


def _parse_cse_json(response: requests.Response) -> dict | None:
    try:
        parsed = response.json()
    except ValueError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _http_get_with_pacing_and_retry(
    params: dict[str, str | int],
    *,
    pace_detail: Callable[[str], None] | None,
) -> tuple[requests.Response, dict | None]:
    """Return (response, parsed_dict|None). Raises RuntimeError on exhausted rate limit."""
    global _last_cse_request_at
    max_retries = int(GOOGLE_CSE_CONFIG["rate_limit_max_retries"])
    pause_sec = float(GOOGLE_CSE_CONFIG["rate_limit_pause_sec"])
    if max_retries < 0:
        max_retries = 0

    last_response: requests.Response | None = None
    last_parsed: dict | None = None

    for attempt in range(max_retries + 1):
        _apply_inter_query_delay(pace_detail)
        last_response = requests.get(
            GOOGLE_CSE_API_URL,
            params=params,
            timeout=_DEFAULT_REQUEST_TIMEOUT_SEC,
        )
        _last_cse_request_at = time.monotonic()
        last_parsed = _parse_cse_json(last_response)

        if _is_rate_limit_response(last_response.status_code, last_parsed):
            if attempt < max_retries:
                _pace_detail_emit(
                    pace_detail,
                    f"rate limit: HTTP {last_response.status_code}; pausing {pause_sec:.0f}s "
                    f"before retry {attempt + 1}/{max_retries}",
                )
                time.sleep(pause_sec)
                continue
            break

        return last_response, last_parsed

    assert last_response is not None
    raise RuntimeError(
        f"Google CSE HTTP {last_response.status_code}: "
        f"{_truncate_body(last_response.text)}"
    )


def search_google_cse(
    query: str,
    *,
    max_results: int = 10,
    site_filters: Sequence[str] | None = None,
    days: int | None = None,
    pace_detail: Callable[[str], None] | None = None,
) -> list[GoogleCseHit]:
    """Run a Custom Search query; returns normalized hits (title, url, snippet).

    Credentials: GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID via os.environ (no fallbacks).

    ``site_filters``: only ``str`` entries are used; other types in the sequence are
    skipped (callers should pass host/path tokens as strings).

    Pagination: Google's ``num`` is capped at 10 per request. ``max_results == 0``
    requests pages until the API provides no ``nextPage`` or returns an empty ``items``.

    ``days``: when set, passes ``dateRestrict=d<N>`` (results indexed within the last N days).

    ``pace_detail``: when provided, invoked with pacing/retry status strings (external
    layer does not log — callers wire to debug_detail when debug=True).
    """
    require_controlled_external_io("google_cse.search_google_cse")
    try:
        api_key = os.environ["GOOGLE_CSE_API_KEY"]
        cx = os.environ["GOOGLE_CSE_ID"]
    except KeyError as err:
        name = err.args[0]
        raise RuntimeError(
            f"missing environment variable {name!r}; set GOOGLE_CSE_API_KEY "
            "and GOOGLE_CSE_ID (see env.example)"
        ) from err

    base = query.strip()
    if not base:
        raise ValueError("empty query")

    if days is not None and days < 1:
        raise ValueError("days must be a positive integer")

    normalized_filters = tuple(
        s.strip()
        for s in (site_filters or ())
        if isinstance(s, str) and s.strip()
    )
    if normalized_filters:
        site_clause = " OR ".join(f"site:{token}" for token in normalized_filters)
        q_param = f"{base} ({site_clause})"
    else:
        q_param = base

    hits: list[GoogleCseHit] = []
    start = 1
    seen_starts: set[int] = set()

    while True:
        # Guard: Google must advance start each page; repeats would loop forever.
        if start in seen_starts:
            break
        seen_starts.add(start)

        if max_results > 0:
            remaining = max_results - len(hits)
            if remaining <= 0:
                return hits[:max_results]
            num_this = min(10, remaining)
        else:
            num_this = 10

        params: dict[str, str | int] = {
            "key": api_key,
            "cx": cx,
            "q": q_param,
            "num": num_this,
            "start": start,
        }
        if days is not None:
            params["dateRestrict"] = f"d{days}"

        response, parsed = _http_get_with_pacing_and_retry(params, pace_detail=pace_detail)

        if not response.ok:
            raise RuntimeError(
                f"Google CSE HTTP {response.status_code}: "
                f"{_truncate_body(response.text)}"
            )

        if parsed is None:
            try:
                response.json()
            except ValueError as err:
                raise RuntimeError(
                    "Google CSE returned a response body that is not valid JSON"
                ) from err
            raise RuntimeError("Google CSE returned JSON root that is not an object")

        err_obj = parsed.get("error")
        if isinstance(err_obj, dict):
            msg = err_obj.get("message")
            code = err_obj.get("code")
            detail = ""
            if isinstance(msg, str):
                detail = msg
            if code is not None:
                sep = "; " if detail else ""
                detail = f"{detail}{sep}code={code!r}"
            if not detail:
                detail = repr(err_obj)
            raise RuntimeError(f"Google CSE API error: {detail}")

        items = parsed.get("items")
        if items is None:
            items_list: list = []
        elif isinstance(items, list):
            items_list = items
        else:
            raise RuntimeError("Google CSE 'items' is not a list")

        for item in items_list:
            hits.append(_item_to_hit(item))

        if max_results > 0:
            if len(hits) >= max_results:
                return hits[:max_results]

        if not items_list:
            break

        next_start = _next_start_index(parsed)
        if next_start is None:
            break
        if next_start in seen_starts:
            break
        start = next_start

    if max_results > 0:
        return hits[:max_results]
    return hits
