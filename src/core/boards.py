"""Core logic for Astral Boards saved searches and listing parse."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional  # noqa: F401 — Dict used in parse_board_listing
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from src.core.agent import _current_agent_task_run_next, do_task
from src.core.dispatcher import compute_batch_cost
from src.data import database
from src.utils.config import BOARD_CONFIG, BOARD_SEARCH_STATES, BOARDS_CONFIG, TASK_CONFIG
from src.utils.logging import flush_log_buffer, get_logger, log_batch_id

logger = get_logger(__name__)

_BOARD_SEARCH_TASK_KEYS = frozenset({"craft_board_search_label", "craft_board_search_criteria"})
_HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)

# PATCH: field omitted vs explicitly provided (criteria / deeplink_url / mode / state / label)
_PATCH_UNSET = object()


class DuplicateBoardSearchError(ValueError):
    """Conflict: same normalized criteria or deeplink for (candidate_id, board_key)."""


class DeeplinkDomainMismatchError(ValueError):
    """Deeplink host does not match board profile entry_netloc."""

    def __init__(self) -> None:
        super().__init__("deeplink domain does not match board entry domain")


def parse_board_listing(raw_html: str, parse_instructions: dict) -> dict:
    """Extract title/link/id from a listing HTML snippet (v1 heuristic + optional selectors)."""
    out: Dict[str, Any] = {"job_title": "", "job_link": "", "company_job_id": ""}
    if not raw_html:
        return out
    link_sel = (parse_instructions or {}).get("job_link")
    if isinstance(link_sel, str) and link_sel.startswith("http"):
        out["job_link"] = link_sel.strip()
    else:
        m = _HREF_RE.search(raw_html)
        if m:
            out["job_link"] = m.group(1).strip()
    title_sel = (parse_instructions or {}).get("job_title")
    if isinstance(title_sel, str) and title_sel and not title_sel.startswith(("[", ".")):
        out["job_title"] = title_sel.strip()
    else:
        text = re.sub(r"<[^>]+>", " ", raw_html)
        out["job_title"] = " ".join(text.split())[:200]
    link = out["job_link"]
    if link:
        tail = link.rstrip("/").split("/")[-1]
        if tail and tail not in ("jobs", "job"):
            out["company_job_id"] = tail
    return out


def listing_key(raw_html: str, parse_instructions: dict) -> str:
    parsed = parse_board_listing(raw_html, parse_instructions)
    link = (parsed.get("job_link") or "").strip().lower()
    if link:
        return link
    norm = re.sub(r"\s+", " ", raw_html[:2048]).strip()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def validate_board_key_adopted(board_key: str) -> None:
    if board_key not in BOARD_CONFIG:
        raise ValueError(f"board_key not in BOARD_CONFIG: {board_key!r}")


def _criteria_to_json(criteria: Any) -> str:
    if isinstance(criteria, str):
        json.loads(criteria)  # validate
        return criteria
    return json.dumps(criteria)


def _criteria_as_dict(criteria: Any) -> dict:
    if isinstance(criteria, dict):
        return criteria
    if isinstance(criteria, str):
        obj = json.loads(criteria)
        if not isinstance(obj, dict):
            raise ValueError("criteria must be a JSON object")
        return obj
    raise ValueError("criteria must be a JSON object")


def _board_save_modes() -> tuple:
    return tuple(BOARDS_CONFIG.get("board_search", {}).get("save_modes") or ("criteria", "deeplink"))


def _normalize_board_deeplink_url(url: str) -> str:
    """Fingerprint form: lowercase scheme/host, trimmed path slashes, sorted query keys, fragment dropped."""
    raw = (url or "").strip()
    if not raw:
        raise ValueError("deeplink URL required")
    p = urlparse(raw)
    scheme = (p.scheme or "").strip().lower()
    netloc = (p.netloc or "").strip().lower()
    if not scheme:
        raise ValueError("deeplink URL must include scheme (http/https)")
    if not netloc:
        raise ValueError("deeplink URL missing host")
    path_part = p.path or ""
    if path_part == "":
        normalized_path = "/"
    else:
        stripped = path_part.rstrip("/")
        normalized_path = "/" if stripped == "" else stripped
    pairs = parse_qsl(p.query, keep_blank_values=True)
    indexed = list(enumerate(pairs))
    indexed.sort(key=lambda x: (x[1][0], x[0]))
    sorted_pairs = [x[1] for x in indexed]
    new_query = urlencode(sorted_pairs, doseq=True)
    rebuilt = urlparse("")
    rebuilt = rebuilt._replace(
        scheme=scheme,
        netloc=netloc,
        path=normalized_path,
        query=new_query,
        params="",
    )
    return urlunparse(rebuilt)


def _criteria_fingerprint_json(criteria_obj: dict) -> str:
    try:
        return json.dumps(criteria_obj, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as e:
        raise ValueError(f"criteria JSON fingerprint error: {e}") from e


def _row_duplicate_fingerprint(row: Dict[str, Any]) -> tuple:
    """(kind criteria|deeplink, fingerprint_string)."""
    mode = row.get("search_mode") or "criteria"
    if mode == "deeplink":
        u = (row.get("deeplink_url") or "").strip()
        # Normalization requires non-empty scheme+host; drifting empty rows fingerprint as error path
        if not u:
            return ("deeplink", "")
        return ("deeplink", _normalize_board_deeplink_url(u))
    raw_c = row.get("criteria") or {}
    cdict = _criteria_as_dict(raw_c) if not isinstance(raw_c, dict) else raw_c
    return ("criteria", _criteria_fingerprint_json(cdict))


def _candidate_board_duplicate(
    board_search_id: Optional[str],
    candidate_id: str,
    board_key: str,
    fingerprint: str,
    fingerprint_kind: Literal["criteria", "deeplink"],
) -> Optional[str]:
    siblings = database.list_board_search_rows(candidate_id, board_key=board_key)
    for r in siblings:
        rid = r.get("board_search_id")
        if board_search_id and rid == board_search_id:
            continue
        kind, fp = _row_duplicate_fingerprint(r)
        if kind == fingerprint_kind and fp == fingerprint:
            return rid
    return None


def _board_entry_url_for_domain(board_key: str) -> str:
    validate_board_key_adopted(board_key)
    profile = BOARD_CONFIG[board_key]
    raw = (profile.get("entry_url") or "").strip()
    if raw:
        if "://" not in raw:
            raise ValueError(f"board profile misconfigured: {board_key} entry_url missing scheme")
        return raw
    raw = (profile.get("jobs_url") or "").strip()
    if not raw or "://" not in raw:
        raise ValueError(f"board profile misconfigured: {board_key}")
    return raw


def _validate_deeplink_domain(board_key: str, normalized_or_raw_url: str) -> None:
    entry = urlparse(_board_entry_url_for_domain(board_key))
    tgt = urlparse(normalized_or_raw_url)
    if not tgt.scheme:
        raise ValueError("deeplink URL must include scheme (http/https)")
    if entry.netloc.lower() != tgt.netloc.lower():
        raise DeeplinkDomainMismatchError()


def _coerce_board_search_state(raw: Any) -> str:
    s = BOARD_SEARCH_STATES[0] if raw is None or str(raw).strip() == "" else str(raw).strip().upper()
    if s not in BOARD_SEARCH_STATES:
        raise ValueError(f"invalid state: {raw!r}")
    return s


def save_board_search(
    candidate_id: str,
    board_key: str,
    label: str,
    criteria: Any,
    *,
    board_search_id: Optional[str] = None,
    state: Optional[str] = None,
    search_mode: str = "criteria",
    deeplink_url: Optional[str] = None,
) -> Dict[str, Any]:
    modes = _board_save_modes()
    validate_board_key_adopted(board_key)
    sid = board_search_id or str(uuid.uuid4())
    wf = _coerce_board_search_state(state)
    if wf == BOARD_SEARCH_STATES[2]:
        raise ValueError("cannot create board_search in ERROR state — gaze sets ERROR after a failed run")

    if search_mode not in modes:
        raise ValueError(f"invalid mode: {search_mode!r}")
    effective_mode = search_mode

    if effective_mode == "criteria":
        criteria_json = _criteria_to_json(criteria if criteria is not None else {})
        cdict = _criteria_as_dict(criteria if criteria is not None else {})
        deeplink_sql: Optional[str] = None
        fp_kind: Literal["criteria", "deeplink"] = "criteria"
        fingerprint = _criteria_fingerprint_json(cdict)
    else:
        raw_dl = (deeplink_url or "").strip()
        if not raw_dl:
            raise ValueError("deeplink_url required when mode is deeplink")
        normalized_dl = _normalize_board_deeplink_url(raw_dl)
        _validate_deeplink_domain(board_key, normalized_dl)
        criteria_json = "{}"
        deeplink_sql = normalized_dl
        fp_kind = "deeplink"
        fingerprint = normalized_dl

    dup = _candidate_board_duplicate(None, candidate_id, board_key, fingerprint, fp_kind)
    if dup:
        raise DuplicateBoardSearchError("duplicate board search")

    database.save_board_search_row(
        sid,
        candidate_id,
        board_key,
        label,
        criteria_json,
        state=wf,
        search_mode=effective_mode,
        deeplink_url=deeplink_sql,
    )
    row = database.get_board_search_row(sid)
    if not row:
        raise RuntimeError(f"board_search insert failed: {sid!r}")
    return row


def get_board_search(board_search_id: str) -> Optional[Dict[str, Any]]:
    return database.get_board_search_row(board_search_id)


def list_board_searches(
    candidate_id: str,
    board_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    return database.list_board_search_rows(candidate_id, board_key=board_key)


def delete_board_search(board_search_id: str) -> bool:
    return database.delete_board_search_row(board_search_id)


def update_board_search(
    board_search_id: str,
    *,
    label: Any = _PATCH_UNSET,
    state: Any = _PATCH_UNSET,
    mode: Any = _PATCH_UNSET,
    criteria: Any = _PATCH_UNSET,
    deeplink_url: Any = _PATCH_UNSET,
) -> Optional[Dict[str, Any]]:
    row = database.get_board_search_row(board_search_id)
    if not row:
        return None

    modes = _board_save_modes()
    board_key_row = row.get("board_key") or ""

    cur_mode = row.get("search_mode") or "criteria"
    cur_crit_raw = row.get("criteria") or {}
    ocrit_dict = cur_crit_raw if isinstance(cur_crit_raw, dict) else _criteria_as_dict(cur_crit_raw)
    cur_dl = row.get("deeplink_url")

    crit_in = criteria is not _PATCH_UNSET
    dl_in = deeplink_url is not _PATCH_UNSET
    mode_in = mode is not _PATCH_UNSET

    dl_nonempty = (
        dl_in
        and deeplink_url is not None
        and str(deeplink_url).strip() != ""
    )

    if not mode_in and crit_in and dl_in and dl_nonempty:
        raise ValueError("mutually_exclusive")

    if mode_in:
        if mode not in modes:
            raise ValueError(f"invalid mode: {mode!r}")
        if mode == "criteria" and dl_nonempty:
            raise ValueError("mutually_exclusive")
        if mode == "deeplink" and crit_in:
            raise ValueError("mutually_exclusive")
        next_mode = mode
    elif cur_mode == "criteria" and dl_nonempty:
        next_mode = "deeplink"
    elif cur_mode == "deeplink" and crit_in:
        next_mode = "criteria"
    else:
        next_mode = cur_mode

    if mode_in and next_mode == "deeplink" and cur_mode == "criteria" and not dl_nonempty:
        raise ValueError("deeplink_url required when mode is deeplink")

    if next_mode == "criteria":
        if crit_in:
            nc_dict = _criteria_as_dict(criteria)
        elif mode_in and cur_mode == "deeplink":
            nc_dict = {}
        else:
            nc_dict = ocrit_dict
        criteria_json = _criteria_to_json(nc_dict)
        deeplink_sql: Optional[str] = None
        fp_kind: Literal["criteria", "deeplink"] = "criteria"
        fingerprint = _criteria_fingerprint_json(nc_dict)
    else:
        # Deeplink persistence: PATCH may omit URL to preserve stored row.
        raw_dl = ""
        if dl_in and deeplink_url is not None:
            raw_dl = str(deeplink_url).strip()
        elif dl_in and deeplink_url is None:
            raw_dl = (cur_dl or "").strip()
        else:
            raw_dl = (cur_dl or "").strip()
        if not raw_dl:
            raise ValueError("deeplink_url required when mode is deeplink")
        normalized_dl = _normalize_board_deeplink_url(raw_dl)
        _validate_deeplink_domain(board_key_row, normalized_dl)
        deeplink_sql = normalized_dl
        criteria_json = "{}"
        fp_kind = "deeplink"
        fingerprint = normalized_dl

    dup = _candidate_board_duplicate(board_search_id, row["candidate_id"], board_key_row, fingerprint, fp_kind)
    if dup:
        raise DuplicateBoardSearchError("duplicate board search")

    final_label = label if label is not _PATCH_UNSET else row["label"]

    if state is not _PATCH_UNSET:
        incoming = _coerce_board_search_state(state)
        act, inactive, err_st = BOARD_SEARCH_STATES
        # API must not PUT rows into ERROR; gazer owns that terminal.
        if incoming == err_st:
            raise ValueError("state ERROR is set by gaze failures only — use PATCH to resume (ACTIVE)")
        cur = _coerce_board_search_state(row.get("state"))
        if incoming != cur:
            allowed_pairs = {(act, inactive), (inactive, act), (err_st, act)}
            if (cur, incoming) not in allowed_pairs:
                raise ValueError(f"illegal state transition: {cur} -> {incoming}")
        final_state = incoming
    else:
        final_state = _coerce_board_search_state(row.get("state"))

    database.update_board_search_row(
        board_search_id,
        label=final_label,
        criteria_json=criteria_json,
        state=final_state,
        search_mode=next_mode,
        deeplink_url=deeplink_sql,
    )
    return get_board_search(board_search_id)


def extract_board_listings(page_html: str, parse_instructions: dict) -> List[str]:
    """Pull listing HTML snippets using profile parse_instructions (container/job_tag)."""
    # Lazy import: avoid importing Playwright stack at boards module import time (heavy + import cycles).
    from src.external.playwright import extract_raw_job_listings

    pi = parse_instructions or {}
    container = pi.get("container") or ""
    job_tag = pi.get("job_tag") or ""
    if not container or not job_tag:
        return [page_html] if page_html else []
    return extract_raw_job_listings(
        page_html, container, job_tag, int(pi.get("container_index", 0))
    )


async def run_board_search_gaze(batch_id: str, row: dict, ctx: Optional[dict] = None) -> dict:
    """Scrape one board_search row and ingest via AST-417 fork."""
    # Lazy imports: gazer/tracker/playwright pulled only when gaze runs — keeps dispatcher import graph light.
    from src.core.gazer import _compiled_title_patterns
    from src.core.tracker import ingest_board_listings
    from src.external.playwright import (
        board_search_deeplink,
        check_connectivity,
        create_browser_context,
        get_page,
    )

    board_key = row.get("board_key") or ""
    validate_board_key_adopted(board_key)
    profile = BOARD_CONFIG[board_key]
    if profile.get("login_required"):
        raise ValueError(f"board {board_key!r} requires login — anonymous gaze_board only")

    criteria = row.get("criteria") or {}
    if isinstance(criteria, str):
        criteria = json.loads(criteria)
    parse_instructions = profile.get("parse_instructions") or {}

    mode = row.get("search_mode") or "criteria"
    # Deeplink gaze uses stored URL and must not hit the interactive scrape_mode gate (AST-487 UAT).
    if mode == "deeplink":
        nav_url = (row.get("deeplink_url") or "").strip()
        if not nav_url:
            raise ValueError("run_board_search_gaze: deeplink mode requires non-empty deeplink_url")
        query_params = None
    else:
        scrape_mode = profile.get("scrape_mode", "deep_link")
        if scrape_mode == "interactive":
            raise NotImplementedError("interactive gaze_board — follow-on after BOARD_CONFIG profiles")
        if scrape_mode != "deep_link":
            scrape_mode = "deep_link"
        nav_url = profile.get("entry_url") or profile.get("jobs_url") or ""
        if not nav_url:
            raise ValueError(f"BOARD_CONFIG[{board_key!r}] missing entry_url")
        query_params = {k: criteria[k] for k in ("title_query", "work_mode", "max_listing_age") if k in criteria}

    if not await check_connectivity():
        raise ConnectionError("run_board_search_gaze: no internet connectivity")

    # Tests mock ``get_page``; production opens an empty tab, then ``board_search_deeplink`` navigates.
    async with create_browser_context() as context:
        page = await get_page(context)
        try:
            html, _meta = await board_search_deeplink(page, nav_url, query_params)
        finally:
            await page.close()

    raw_listings = extract_board_listings(html, parse_instructions)
    patterns = _compiled_title_patterns(ctx or {})
    title_matchers = patterns or profile.get("title_patterns")
    if title_matchers and not hasattr(title_matchers[0], "search"):
        import re
        title_matchers = [re.compile(p) for p in title_matchers if p]

    counts = ingest_board_listings(
        row["candidate_id"],
        board_key,
        row["board_search_id"],
        batch_id,
        raw_listings,
        title_matchers,
        parse_instructions,
    )
    return {"board_search_id": row["board_search_id"], "status": "success", **counts}


def run_board_search_generation(
    board_search_id: str,
    task_key: str,
    live_content: Optional[str],
) -> Tuple[Dict[str, Any], int]:
    """Run craft_board_search_* via do_task; board_search row merged into ctx."""
    if task_key not in _BOARD_SEARCH_TASK_KEYS:
        return ({"error": f"Unknown board search task: {task_key}"}, 400)
    if task_key not in TASK_CONFIG:
        return ({"error": f"Unknown task: {task_key}"}, 400)

    row = get_board_search(board_search_id)
    if not row:
        return ({"error": f"board_search not found: {board_search_id}"}, 404)

    candidate = database.get_candidate(row["candidate_id"])
    if not candidate:
        return ({"error": f"Candidate not found: {row['candidate_id']}"}, 404)

    skip_outer_ledger = bool(_current_agent_task_run_next(task_key))
    batch_id: Optional[str] = None
    if not skip_outer_ledger:
        ledger_task_key = f"user-{task_key}"
        batch_id = f"{ledger_task_key}-{uuid.uuid4()}"
        started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        database.save_dispatch_ledger(
            batch_id,
            ledger_task_key,
            row["candidate_id"],
            started_at,
            entity_type="candidate",
            batch_size=1,
        )
        logger.info(
            "UI board generate started task_key=%r batch_id=%s board_search_id=%s",
            task_key,
            batch_id,
            board_search_id,
        )
    ctx = {**candidate, "board_search": row}
    if batch_id:
        log_batch_id.set(batch_id)
    try:
        try:
            result = asyncio.run(
                do_task(
                    task_key=task_key,
                    live_content=live_content or "",
                    index=row["candidate_id"],
                    ctx=ctx,
                )
            )
        except Exception as e:
            if batch_id:
                database.update_dispatch_ledger(
                    batch_id,
                    status="FAILED",
                    completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    total_processed=1,
                    total_failed=1,
                )
            logger.error(
                "board search generation exception task_key=%r batch_id=%s error=%s",
                task_key,
                batch_id or log_batch_id.get(),
                e,
            )
            return ({"success": False, "error": str(e)}, 500)

        completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        response_batch_id = batch_id or log_batch_id.get()
        if not result or not result.get("success"):
            err = (
                result.get("error", "Generation failed")
                if result
                else "do_task returned None"
            )
            logger.error(
                "board search generation failed task_key=%r batch_id=%s error=%s",
                task_key,
                response_batch_id,
                err,
            )
            if batch_id:
                total_cost = compute_batch_cost(batch_id)
                database.update_dispatch_ledger(
                    batch_id,
                    status="FAILED",
                    completed_at=completed_at,
                    total_processed=1,
                    total_passed=0,
                    total_failed=1,
                    total_cost=total_cost,
                )
            return (
                {
                    "success": False,
                    "error": err,
                    "batch_id": response_batch_id,
                },
                500,
            )

        if batch_id:
            total_cost = compute_batch_cost(batch_id)
            database.update_dispatch_ledger(
                batch_id,
                status="COMPLETED",
                completed_at=completed_at,
                total_processed=1,
                total_passed=1,
                total_failed=0,
                total_cost=total_cost,
            )
            logger.info(
                "UI board generate completed task_key=%r batch_id=%s status=COMPLETED cost=%s",
                task_key,
                batch_id,
                total_cost,
            )
        return (
            {
                "success": True,
                "parsed_response": result.get("parsed_response"),
                "timesheet": result.get("timesheet", {}),
                "batch_id": response_batch_id,
            },
            200,
        )
    finally:
        flush_log_buffer()
        log_batch_id.set(None)
