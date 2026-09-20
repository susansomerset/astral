"""
Core roster business logic.

Contains business logic for company roster management and job page discovery.
"""

import asyncio
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional, Set
from urllib.parse import urlparse

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.external.playwright import (
    extract_page_scrape_contract,
    extract_site_page_list,
    extract_visible_text,
    extract_page_dom,
    get_visible_text,
    get_page,
    close_page,
    create_browser_context,
    create_batch_browser_session,
    BrowserSession,
    normalize_url,
    wait_for_careers_list_readiness,
    PlaywrightInfraError,
    classify_playwright_failure,
    is_playwright_infra_failure,
)
from src.external.google_cse import GoogleCseHit, search_google_cse
from src.core.agent import do_task
from src.data.database import (
    claim_company_batch,
    count_companies,
    get_active_trigger_states,
    get_company,
    get_company_batch,
    get_company_job_counts,
    list_companies,
    list_company_job_scans,
    list_stale_company_search_terms,
    save_company,
    set_company_batch,
    update_company,
    update_company_last_scan_at,
    update_company_search_term_last_scan_at,
    COMPANY_BATCH_SORT_COLUMNS,
    ensure_batch_response_entity_ids,
)
from src.utils.logging import get_logger, log_batch_id
from src.utils.llm_external import is_provider_balance_refusal
from src.utils.config import (
    ASTRAL_CONFIG,
    COMPANY_STATES,
    INFLOW_CONFIG,
    PLAYWRIGHT_CONFIG,
    ROSTER_CONFIG,
    TASK_CONFIG,
    roster_scrape_readiness_config,
    validate_value,
)
from src.utils.formatting import (
    collapse_consecutive_blank_lines,
    enumerate_array,
    normalize_link,
    parse_enumerate_array,
    find_job_containers,
)

# Logger for this module
logger = get_logger(__name__)


def _entity_info(entity_id: Any, entity_type: str, event: str, detail: Any) -> None:
    logger.info(
        "%s | %s %s: %s (batch: %s)",
        entity_id,
        entity_type,
        event,
        detail,
        log_batch_id.get() or "-",
    )


def _warn_company(aid: Any, dest: Any, reason: str) -> None:
    logger.warning("%s -> %s [%s]", aid, dest, reason)


def _pace_debug(message: str) -> None:
    logger.debug("%s", message)


def make_locate_parse_resolver(dom_map: Dict[int, str], visible_map: Dict[int, str]):  # pragma: no cover
    """AST-469: ctx['resolve_run_next_live'] for select_job_page → parse_job_list chain.

    Stateful only via captured maps; returns (culled_dom, visible_text) for tuple contract in agent.do_task.
    """

    def resolve_run_next_live(parsed: Any):
        if not isinstance(parsed, dict):
            return ("", "")
        sp = parsed.get("selected_page")
        titles = parsed.get("job_titles") or []
        try:
            sp_int = int(sp) if sp is not None else None
        except (TypeError, ValueError):
            sp_int = None
        if sp_int is None:
            return ("", "")
        dom_full = (dom_map.get(sp_int) or "").strip()
        if not dom_full:
            return ("", (visible_map.get(sp_int) or "").strip())
        dom_joined, _, cull_outcome = _culled_dom_for_parse(dom_full, titles)
        vis = (visible_map.get(sp_int) or "").strip()
        if cull_outcome == "cull_miss" or not dom_joined.strip():
            return ("", vis)
        return (dom_joined, vis)

    return resolve_run_next_live


def _normalize_job_titles(raw: Any) -> List[str]:
    """Strip blanks; preserve order from select/company_data."""
    if not isinstance(raw, list):
        return []
    return [str(t).strip() for t in raw if str(t).strip()]


def _dom_text_covers_titles(dom_html: str, job_titles: List[str]) -> bool:
    blob = (dom_html or "").lower()
    return all(t.lower() in blob for t in job_titles if t.strip())


def _culled_dom_for_parse(
    dom_html: str, job_titles: List[str]
) -> Tuple[str, List[str], str]:
    """Returns (dom_joined, containers, outcome_label).
    outcome_label: no_titles | full_dom | culled | cull_miss."""
    titles = _normalize_job_titles(job_titles)
    if not titles:
        return ("", [], "no_titles")
    if len(titles) < 2:
        dom = (dom_html or "").strip()
        if not dom:
            return ("", [], "cull_miss")
        containers = find_job_containers(dom, titles)
        joined = "\n".join(containers).strip() if containers else ""
        if not joined:
            return ("", containers or [], "cull_miss")
        return (joined, containers, "full_dom")
    containers = find_job_containers(dom_html or "", titles)
    dom_joined = "\n".join(containers).strip()
    if not dom_joined:
        return ("", containers, "cull_miss")
    if _dom_text_covers_titles(dom_joined, titles):
        return (dom_joined, containers, "culled")
    # find_job_containers fallback [dom_html] may not cover all titles on partial rescrape
    if _dom_text_covers_titles(dom_html or "", titles):
        return ((dom_html or "").strip(), containers, "full_dom")
    return ("", containers, "cull_miss")


def _strip_company_data_keys(short_name: str, keys: Tuple[str, ...]) -> None:  # pragma: no cover
    """Remove keys from merged company_data (AST-469: stale job_list_visible on NO_OPENINGS)."""
    company = get_company(short_name)
    if not company:
        return
    cd = dict(company.get("company_data") or {})
    changed = False
    for k in keys:
        if k in cd:
            cd.pop(k, None)
            changed = True
    if changed:
        update_company(short_name, company_data=cd)



# ---- Multi-use helpers ----

def _extract_company_name_from_url(url: Optional[str]) -> Optional[str]:
    """Extract company name (display) from URL/domain."""
    if not url:
        return None
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        if domain.startswith('www.'):
            domain = domain[4:]
        parts = domain.split('.')
        if len(parts) >= 2:
            main_domain = parts[-2]
        else:
            main_domain = parts[0] if parts else domain
        return main_domain.capitalize() if main_domain else None
    except Exception:
        return None


# ---- Company data ----

def save_company_data(short_name: str, company_data: Dict[str, Any], replace: bool = False) -> None:
    """Update company_data for a company. replace=False: merge keys; replace=True: full overwrite.
    Mirrors tracker.save_job_data. No state change.
    Raises ValueError if company not found (when merging)."""
    if replace:
        update_company(short_name, company_data=company_data)
    else:
        existing = get_company(short_name)
        if not existing:
            raise ValueError(f"Company not found: {short_name}")
        merged = dict(existing.get("company_data") or {})
        merged.update(company_data)
        update_company(short_name, company_data=merged)


# ---- State transition ----

_COMPANY_STATE_LIST = list(COMPANY_STATES.keys())

def transition_company_state(short_name: str, to_state: str) -> None:
    """Record company state transition (mirrors tracker.transition_job_state).
    Appends to state_history; updates state. Validates to_state against COMPANY_STATES.
    Raises ValueError if invalid or company not found."""
    validate_value(_COMPANY_STATE_LIST, to_state)
    company = get_company(short_name)
    if not company:
        raise ValueError(f"Company not found: {short_name}")
    from_state = str(company.get("state") or "")
    history = list(company.get("state_history") or [])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    batch_id = company.get("batch_id")
    history.append({"from_state": from_state, "to_state": to_state, "timestamp": now, "batch_id": batch_id})
    if from_state != to_state:
        _entity_info(short_name, "company", "state", f"{from_state or '(none)'} -> {to_state}")
    update_company(short_name, state=to_state, state_history=history)


# ---- Roster inflow discovery (AST-505) ----

_INFLOW_SLUG_RE = re.compile(r"^[a-z0-9_]+$")


def _normalize_company_url_for_dedupe(url: str) -> str:
    """Host-level URL key for roster ingest dedupe (strip www. after normalize_url)."""
    u = (url or "").strip()
    if not u:
        return ""
    try:
        n = normalize_url(u)
        parsed = urlparse(n)
    except ValueError:
        return ""
    netloc = parsed.netloc or ""
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parsed.path.rstrip("/") if parsed.path else ""
    out = f"{parsed.scheme.lower() if parsed.scheme else 'https'}://{netloc}{path}"
    if parsed.query:
        out += f"?{parsed.query}"
    return out


def _slug_from_discovery_url(url: str) -> str:
    """Mechanical company slug from a CSE hit URL (hostname-based)."""
    norm = _normalize_company_url_for_dedupe(url)
    if not norm:
        return f"inflow_{hashlib.sha256((url or '').encode()).hexdigest()[:12]}"
    netloc = urlparse(norm).netloc or ""
    if netloc.startswith("www."):
        netloc = netloc[4:]
    slug = netloc.lower().replace(".", "_")
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    if slug:
        return slug
    return f"inflow_{hashlib.sha256(norm.encode()).hexdigest()[:12]}"


def _discovery_blurb_line(hit: dict, *, index: int = 0) -> str:
    title = hit.get("title") or ""
    hit_url = hit.get("url") or ""
    snippet = (hit.get("snippet") or "")[:500]
    return f"{index:03d}|{title}|{hit_url}|{snippet}"


def _renumber_vet_blurb_line(blurb: str, batch_index: int) -> str:
    parts = blurb.split("|", 3)
    if len(parts) >= 4:
        return f"{batch_index:03d}|{parts[1]}|{parts[2]}|{parts[3]}"
    return f"{batch_index:03d}|{blurb}"


def _apply_vet_inflow_result_row(
    short_name: str,
    row: dict,
    cfg: Dict[str, Any],
    log: Any,
    debug: bool,
    *,
    index: int,
    total: int,
) -> Dict[str, Any]:
    _ = (log, debug, index, total)
    grade = (row.get("grade") or "").strip().upper()
    website = (row.get("website") or "").strip()
    if not website:
        logger.debug("Response from vet grade row: grade=%r missing website", grade)
        return {"success": False, "state": None, "error": "missing website"}
    if grade in cfg["fail_grades"]:
        transition_company_state(short_name, cfg["fail_state"])
        _warn_company(short_name, cfg["fail_state"], f"vet grade {grade}")
        logger.debug(
            "Response from vet grade row: grade=%r website=%r state=%s",
            grade, website, cfg["fail_state"],
        )
        return {"success": True, "state": cfg["fail_state"], "error": None}
    if grade not in cfg["pass_grades"]:
        _warn_company(short_name, "-", f"unknown grade {row.get('grade')!r}")
        return {"success": False, "state": None, "error": f"unknown grade {grade!r}"}
    update_company(short_name, company_website=website)
    transition_company_state(short_name, cfg["pass_state"])
    logger.debug(
        "Response from vet grade row: grade=%r website=%r state=%s",
        grade, website, cfg["pass_state"],
    )
    return {"success": True, "state": cfg["pass_state"], "error": None}


def _candidate_company_urls(candidate_id: str) -> Set[str]:
    urls: Set[str] = set()
    for row in list_companies(candidate_id=candidate_id):
        for key in ("company_website", "job_site"):
            raw = (row.get(key) or "").strip()
            if not raw:
                continue
            norm = _normalize_company_url_for_dedupe(raw)
            if norm:
                urls.add(norm)
        data = row.get("company_data") or {}
        if not isinstance(data, dict):
            continue
        notes = (data.get("inflow_discovery_notes") or "").strip()
        if notes:
            norm = _normalize_company_url_for_dedupe(notes)
            if norm:
                urls.add(norm)
        blurb = (data.get("inflow_discovery_blurb") or "").strip()
        if blurb:
            parts = blurb.split("|", 3)
            if len(parts) >= 3 and (parts[2] or "").strip():
                norm = _normalize_company_url_for_dedupe(parts[2])
                if norm:
                    urls.add(norm)
    return urls


def record_inflow_discovery_hit(
    candidate_id: str,
    hit: dict,
    *,
    index: int = 0,
    search_term: str = "",
) -> Tuple[bool, str]:
    """Record one CSE hit as a company in discovery land_state (DISCOVERED) with blurb stored."""
    url = (hit.get("url") or "").strip()
    if not url:
        return False, "skipped empty url"
    norm = _normalize_company_url_for_dedupe(url)
    if not norm or norm in _candidate_company_urls(candidate_id):
        return False, f"skipped duplicate url {url!r}"
    slug = _slug_from_discovery_url(url)
    if not slug or not _INFLOW_SLUG_RE.match(slug):
        return False, f"invalid slug from url {url!r}"
    resolved_slug: Optional[str] = None
    for candidate_slug in [slug] + [f"{slug}_{n}" for n in range(2, 10)]:
        existing = get_company(candidate_slug)
        if not existing:
            resolved_slug = candidate_slug
            break
        if (existing.get("candidate_id") or "") == candidate_id:
            return False, f"duplicate slug {candidate_slug!r}"
    if not resolved_slug:
        return False, f"slug collision for {url!r}"
    slug = resolved_slug
    term = (search_term or "").strip() or None
    save_company(
        short_name=slug,
        state=INFLOW_CONFIG["discovery"]["land_state"],
        company_website="",
        candidate_id=candidate_id,
        company_name=slug,
        originating_search_term=term,
    )
    save_company_data(
        slug,
        {
            "inflow_discovery_blurb": _discovery_blurb_line(hit, index=index),
            "inflow_discovery_notes": url,
        },
    )
    land = INFLOW_CONFIG["discovery"]["land_state"]
    _entity_info(slug, "company", "inflow recorded", land)
    if term:
        return True, f"recorded {land} slug={slug} term={term!r}"
    return True, f"recorded {land} slug={slug}"


def _ingest_failure_reason(
    candidate_id: str,
    slug: str,
    website: Optional[str],
) -> Optional[str]:
    """Return human-readable ingest failure reason, or None if ingest would succeed."""
    slug = (slug or "").strip().lower()
    if not slug or not _INFLOW_SLUG_RE.match(slug):
        return f"invalid slug {slug!r}"
    existing = get_company(slug)
    if existing:
        if (existing.get("candidate_id") or "") != candidate_id:
            return f"slug {slug!r} owned by another candidate"
        return f"duplicate slug {slug!r} for candidate {candidate_id}"
    site = (website or "").strip()
    if site:
        norm = _normalize_company_url_for_dedupe(site)
        if norm and norm in _candidate_company_urls(candidate_id):
            return f"duplicate URL {site!r} for candidate {candidate_id}"
    return None


def ingest_new_companies(
    candidate_id: str,
    slug: str,
    website: Optional[str],
    *,
    source_hit: Optional[dict] = None,
    originating_search_term: Optional[str] = None,
) -> bool:
    """Create NEW or WEBSITE_FOUND company row for an accepted inflow hit."""
    slug = (slug or "").strip().lower()
    if not slug or not _INFLOW_SLUG_RE.match(slug):
        _warn_company(slug or "-", "-", f"invalid slug {slug!r}")
        return False
    existing = get_company(slug)
    if existing:
        if (existing.get("candidate_id") or "") != candidate_id:
            _warn_company(slug, "-", f"owned by another candidate")
        return False
    site = (website or "").strip()
    if site:
        norm = _normalize_company_url_for_dedupe(site)
        if norm and norm in _candidate_company_urls(candidate_id):
            _warn_company(slug, "-", f"duplicate URL {site!r}")
            return False
    term = originating_search_term
    if term is None and isinstance(source_hit, dict):
        raw = source_hit.get("originating_search_term")
        if raw is None:
            raw = source_hit.get("search_term")
        term = (raw or "").strip() or None
    else:
        term = (term or "").strip() or None
    target_state = "WEBSITE_FOUND" if site else "NEW"
    save_company(
        short_name=slug,
        state=target_state,
        company_website=site,
        candidate_id=candidate_id,
        company_name=slug,
        originating_search_term=term,
    )
    if source_hit:
        note_url = (source_hit.get("url") or "").strip()
        if note_url:
            save_company_data(slug, {"inflow_discovery_notes": note_url})
    _entity_info(slug, "company", "inflow recorded", target_state)
    return True


async def vet_inflow_discovery_company(
    short_name: str,
    entity: Dict[str, Any],
    batch_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Company dispatch: vet stored discovery blurb → WEBSITE_FOUND | VET_FAILED (AST-776)."""
    del batch_id  # company batch_id is on entity row; do_task uses log_batch_id from dispatcher
    cfg = INFLOW_CONFIG["vet"]
    blurb = ((entity.get("company_data") or {}).get(cfg["blurb_data_key"]) or "").strip()
    if not blurb:
        _warn_company(short_name, "-", "missing inflow_discovery_blurb")
        return {"success": False, "state": None, "error": "missing inflow_discovery_blurb"}
    live_content = f"Discovery hit (index|title|url|snippet)\n{blurb}"
    logger.debug("Calling agent.do_task: task_key=%s index=%s", cfg["task_key"], short_name)
    logger.debug("Calling agent.do_task live_content: %s", live_content)
    api_result = await do_task(
        task_key=cfg["task_key"],
        live_content=live_content,
        index=short_name,
        ctx={
            **(ctx or {}),
            "batch_entities": [{"company_id": short_name, "short_name": short_name}],
            "batch_size": 1,
        },
        debug=debug,
    )
    logger.debug("Response from agent.do_task: %s", api_result)
    if not api_result.get("success"):
        _warn_company(short_name, "-", api_result.get("error") or "task failed")
        return {"success": False, "state": None, "error": api_result.get("error") or "task failed"}
    parsed = api_result.get("parsed_response") or {}
    rows = parsed.get("results")
    row: Optional[dict] = None
    if isinstance(rows, list):
        for r in rows:
            if isinstance(r, dict):
                row = r
                break
    if not row:
        _warn_company(short_name, "-", "missing results")
        logger.debug("Response from vet parse: missing results list")
        return {"success": False, "state": None, "error": "missing results"}
    return _apply_vet_inflow_result_row(
        short_name, row, cfg, logger, debug, index=1, total=1,
    )


async def vet_inflow_discovery_company_batch(
    batch_id: str,
    companies: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Batch company vet: one do_task, hit_index decode → WEBSITE_FOUND | VET_FAILED (AST-822)."""
    cfg = INFLOW_CONFIG["vet"]
    blurb_key = cfg["blurb_data_key"]
    ready: List[Dict[str, Any]] = []
    not_ready: List[Dict[str, Any]] = []
    logger.debug("Beginning vet_inflow_discovery loop on %s items", len(companies))
    for company in companies:
        blurb = ((company.get("company_data") or {}).get(blurb_key) or "").strip()
        if blurb:
            ready.append(company)
        else:
            not_ready.append(company)
    for company in not_ready:
        sn = company.get("short_name") or "?"
        _warn_company(sn, "-", "missing inflow_discovery_blurb")
    total = len(companies)
    if not ready:
        logger.debug("End vet_inflow_discovery loop after %s items", total)
        return {"passed": 0, "failed": 0, "skipped": 0, "total": total}
    short_names = [c.get("short_name") or "?" for c in ready]
    logger.debug("Calling agent.do_task: task_key=%s short_names=%s", cfg["task_key"], short_names)
    ready_blurbs = [
        ((c.get("company_data") or {}).get(blurb_key) or "").strip() for c in ready
    ]
    header = (
        "Discovery hit (index|title|url|snippet)"
        if len(ready) == 1
        else "Discovery hits (index|title|url|snippet)"
    )
    body = "\n".join(_renumber_vet_blurb_line(b, i) for i, b in enumerate(ready_blurbs))
    live_content = f"{header}\n{body}"
    logger.debug("Calling agent.do_task live_content: %s", live_content)
    ready_for_decode = [
        {
            "company_id": c.get("short_name") or "?",
            "short_name": c.get("short_name") or "?",
            "company_data": c.get("company_data") or {},
            "state": c.get("state"),
        }
        for c in ready
    ]
    api_result = await do_task(
        task_key=cfg["task_key"],
        live_content=live_content,
        index=f"vet_inflow_discovery_batch_{batch_id}",
        ctx={
            **(ctx or {}),
            "batch_entities": ready_for_decode,
            "batch_size": len(ready_for_decode),
        },
        debug=debug,
    )
    logger.debug("Response from agent.do_task: %s", api_result)
    if not api_result.get("success"):
        for company in ready:
            _warn_company(company.get("short_name") or "?", "-", api_result.get("error") or "task failed")
        logger.debug("End vet_inflow_discovery loop after %s items", total)
        return {"passed": 0, "failed": 0, "skipped": 0, "total": total}
    parsed = api_result.get("parsed_response") or {}
    rows = parsed.get("results")
    index_by_hit: Dict[int, dict] = {}
    if isinstance(rows, list):
        for r in rows:
            if isinstance(r, dict):
                hi = r.get("hit_index")
                if isinstance(hi, int):
                    index_by_hit[hi] = r
    passed = failed = errors = 0
    errors += len(not_ready)
    for i, company in enumerate(ready):
        short_name = company.get("short_name") or "?"
        row = index_by_hit.get(i)
        if not row:
            _warn_company(short_name, "-", f"missing results row hit_index={i}")
            errors += 1
            continue
        r = _apply_vet_inflow_result_row(
            short_name, row, cfg, logger, debug, index=i + 1, total=len(ready),
        )
        if r.get("error"):
            errors += 1
        elif r.get("state") == cfg["pass_state"]:
            passed += 1
        elif r.get("state") == cfg["fail_state"]:
            failed += 1
        else:
            errors += 1
    logger.debug("End vet_inflow_discovery loop after %s items", total)
    return {"passed": passed, "failed": failed, "skipped": 0, "total": total}


async def resolve_company_website(
    short_name: str,
    entity: Dict[str, Any],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """CSE-only fetch hop for inflow_resolve_website → persist hits → WEBSITE_REVIEW | NO_WEBSITE; never do_task."""
    del ctx  # fetch hop — no agent call
    _ = debug
    cfg = INFLOW_CONFIG["resolve"]
    site = (entity.get("company_website") or "").strip()
    if site:
        logger.debug("Calling search_google_cse skipped: company_website=%r", site)
        return {"success": True, "state": "WEBSITE_FOUND", "error": None}
    name = (entity.get("company_name") or short_name or "").strip()
    query = f"{name} official website"
    logger.debug("Calling search_google_cse: query=%r", query)
    try:
        hits = search_google_cse(
            query=query,
            max_results=int(cfg["max_results"]),
            site_filters=None,
            days=cfg["date_restrict_days"],
            pace_detail=_pace_debug,
        )
    except (RuntimeError, ValueError) as exc:
        logger.exception(
            "%s | company CSE search\n  %s: %s\n  Leaving website unresolved",
            short_name,
            type(exc).__name__,
            exc,
        )
        return {"success": False, "state": None, "error": str(exc)}
    logger.debug("Response from search_google_cse: %s", hits)
    if not hits:
        logger.debug("Response from search_google_cse: zero hits query=%r", query)
        fail_state = cfg["fail_state"]
        transition_company_state(short_name, fail_state)
        return {"success": True, "state": fail_state, "error": None}
    # Persist CSE hits for resolve_website apply (AST-1674); wait on WEBSITE_REVIEW.
    logger.debug("Calling save_company_data: %s=%s", cfg["hit_list_data_key"], hits)
    save_company_data(short_name, {cfg["hit_list_data_key"]: hits})
    pass_state = cfg["pass_state"]
    transition_company_state(short_name, pass_state)
    _entity_info(
        short_name, "company", "inflow_resolve_website",
        f"{len(hits)} hits -> {pass_state}",
    )
    return {"success": True, "state": pass_state, "error": None}


async def resolve_website_company(
    short_name: str,
    entity: Dict[str, Any],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """resolve_website AI apply — load persisted CSE hits → find_company_website → WEBSITE_FOUND | NO_WEBSITE."""
    hit_key = INFLOW_CONFIG["resolve"]["hit_list_data_key"]
    sa_cfg = TASK_CONFIG["resolve_website"]
    agent_task_key = sa_cfg["agent_task"]  # find_company_website — agent identity, not SA key
    pass_state = sa_cfg["pass_state"]
    fail_state = sa_cfg["fail_state"]

    hits = (entity.get("company_data") or {}).get(hit_key)
    if not isinstance(hits, list) or not hits:
        _warn_company(short_name, "-", f"missing or empty {hit_key}")
        return {"success": False, "state": None, "error": f"missing or empty {hit_key}"}

    # Same live_content shape as pre-split resolve: row 0 = slug; hits 1..N (1-based).
    lines = [f"0|{short_name}|"]
    for i, hit in enumerate(hits):
        snip = (hit.get("snippet") or "")[:500]
        lines.append(f"{i + 1}|{hit.get('title', '')}|{hit.get('url', '')}|{snip}")
    live_content = "\n".join(lines)
    logger.debug("Calling agent.do_task: task_key=%s index=%s", agent_task_key, short_name)
    logger.debug("Calling agent.do_task live_content: %s", live_content)
    api_result = await do_task(
        task_key=agent_task_key,
        live_content=live_content,
        index=short_name,
        ctx=ctx,
        debug=debug,
    )
    logger.debug("Response from agent.do_task: %s", api_result)
    if not api_result.get("success"):
        _warn_company(short_name, "-", api_result.get("error") or "task failed")
        return {"success": False, "state": None, "error": api_result.get("error") or "task failed"}

    parsed = api_result.get("parsed_response") or {}
    website = (parsed.get("website") or "").strip()
    if not parsed.get("task_success") or not website:
        logger.debug(
            "Response from find_company_website: task_success=%r website=%r",
            parsed.get("task_success"), website,
        )
        transition_company_state(short_name, fail_state)
        _entity_info(short_name, "company", "resolve_website", f"-> {fail_state}")
        return {"success": True, "state": fail_state, "error": None}

    update_company(short_name, company_website=website)
    transition_company_state(short_name, pass_state)
    _entity_info(
        short_name, "company", "resolve_website",
        f"website={website!r} -> {pass_state}",
    )
    return {"success": True, "state": pass_state, "error": None}


async def run_inflow_discovery_batch(
    candidate: Dict[str, Any],
    batch_id: str,
    ctx: Optional[Dict[str, Any]],
    debug: bool,
) -> Dict[str, Any]:
    """Phase 1: CSE per stale table term, record deduped hits as DISCOVERED (land_state)."""
    _ = debug
    zero = {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}
    candidate_id = (candidate.get("astral_candidate_id") or candidate.get("candidate_id") or "").strip()
    cfg = INFLOW_CONFIG["discovery"]
    freq_hrs = float((ctx or {}).get("inflow_discovery_freq_hrs") or 0)
    terms = list_stale_company_search_terms(candidate_id, freq_hrs)
    term_total = len(terms)
    if not terms:
        _entity_info(candidate_id, "candidate", "inflow_discovery", "no stale search terms")
        return {**zero, "total_errors": 0}
    all_hits: List[Tuple[str, GoogleCseHit]] = []
    seen_urls: Set[str] = set()
    errors = 0
    logger.debug("Beginning CSE term loop on %s items", term_total)
    for term in terms:
        logger.debug("Calling search_google_cse: query=%r", term)
        try:
            hits = search_google_cse(
                query=term,
                max_results=int(cfg["max_results_per_query"]),
                site_filters=None,
                days=int(cfg["date_restrict_days"]),
                pace_detail=_pace_debug,
            )
        except (RuntimeError, ValueError) as exc:
            logger.exception(
                "%s | candidate CSE search term %r\n  %s: %s\n  Continuing to the next search term",
                candidate_id,
                term,
                type(exc).__name__,
                exc,
            )
            errors += 1
            continue
        logger.debug("Response from search_google_cse: %s", hits)
        update_company_search_term_last_scan_at(candidate_id, term)
        for hit in hits:
            norm = _normalize_company_url_for_dedupe(hit.get("url") or "")
            if not norm or norm in seen_urls:
                continue
            seen_urls.add(norm)
            all_hits.append((term, hit))
    logger.debug("End CSE term loop after %s items", term_total)
    if not all_hits:
        logger.debug(
            "Response from run_inflow_discovery_batch: terms_searched=%s errors=%s deduped_hits=0",
            term_total, errors,
        )
        return {**zero, "total_errors": errors}
    hit_total = len(all_hits)
    recorded = 0
    skipped = 0
    logger.debug("Beginning inflow record loop on %s items", hit_total)
    for hit_i, (term, hit) in enumerate(all_hits):
        ok, outcome = record_inflow_discovery_hit(
            candidate_id, hit, index=hit_i, search_term=term,
        )
        logger.debug("Response from record_inflow_discovery_hit: %s", outcome)
        if ok:
            recorded += 1
        else:
            skipped += 1
            _warn_company(
                _normalize_company_url_for_dedupe((hit.get("url") or "").strip()) or f"hit_{hit_i}",
                "-",
                outcome,
            )
    logger.debug("End inflow record loop after %s items", hit_total)
    return {
        "total_processed": 1,
        "total_passed": recorded,
        "total_failed": skipped,
        "total_errors": errors,
    }


# ---- Dispatch entry point (called by consult.run_consult_task) ----

async def run_company_task(
    input_state: str,
    entity: Dict[str, Any],
    batch_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    dispatch_task_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Process a single company for the given input_state. Returns _SUMMARY_ZERO-shaped dict.
    Dispatcher handles concurrency (warm_then_gather); this fn processes one entity at a time."""
    zero = {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}
    short_name = entity.get("short_name", "")
    company_website = entity.get("company_website", "")

    try:
        if input_state == "DISCOVERED":
            tk = (dispatch_task_key or "").strip()
            if tk == INFLOW_CONFIG["vet"]["task_key"]:
                r = await vet_inflow_discovery_company(
                    short_name, entity, batch_id, ctx=ctx, debug=debug,
                )
            elif tk == INFLOW_CONFIG["resolve"]["task_key"]:
                r = await resolve_company_website(short_name, entity, ctx=ctx, debug=debug)
            else:
                _warn_company(
                    short_name, "-",
                    f"DISCOVERED requires dispatch_task_key {INFLOW_CONFIG['vet']['task_key']!r} or {INFLOW_CONFIG['resolve']['task_key']!r}",
                )
                return {**zero, "total_errors": 1}
            if r.get("error"):
                return {**zero, "total_errors": 1}
            terminal_ok = (
                INFLOW_CONFIG["vet"]["pass_state"],
                INFLOW_CONFIG["vet"]["fail_state"],
                INFLOW_CONFIG["resolve"]["pass_state"],
                INFLOW_CONFIG["resolve"]["fail_state"],
            )
            if r.get("state") in terminal_ok:
                return {**zero, "total_passed": 1}
            return {**zero, "total_failed": 1}

        elif input_state == "WEBSITE_REVIEW":
            tk = (dispatch_task_key or "").strip()
            if tk != "resolve_website":
                _warn_company(short_name, "-", f"WEBSITE_REVIEW expects resolve_website, got {tk}")
                return {**zero, "total_errors": 1}
            r = await resolve_website_company(short_name, entity, ctx=ctx, debug=debug)
            if r.get("error"):
                return {**zero, "total_errors": 1}
            terminal_ok = (
                TASK_CONFIG["resolve_website"]["pass_state"],
                TASK_CONFIG["resolve_website"]["fail_state"],
            )
            if r.get("state") in terminal_ok:
                return {**zero, "total_passed": 1}
            return {**zero, "total_failed": 1}

        elif input_state in ("WEBSITE_FOUND", "WEBSITE_FOUND_RETRY"):
            tk = (dispatch_task_key or "").strip()
            _warn_company(
                short_name, "-",
                f"monolithic WEBSITE_FOUND dispatch removed (dispatch_task_key={tk or None!r}; use fetch_website or HOMEPAGE_READY prefilter batch)",
            )
            return {**zero, "total_errors": 1}

        elif input_state == "NO_OPENINGS":
            r = await process_recheck_no_openings(entity, batch_id, ctx=ctx, debug=debug)
            if not r.get("success"):
                _warn_company(short_name, "-", r.get("message", "") or "recheck_no_openings failed")
                return {**zero, "total_errors": 1}
            _entity_info(short_name, "company", "recheck_no_openings", r.get("new_state", ""))
            return {**zero, "total_passed": 1}

        elif input_state == "JOBS_FOUND" and "JOBS_FOUND" in frozenset(
            ROSTER_CONFIG.get("locate_job_page", {}).get("dispatch_input_states") or ()
        ):
            job_site_entity = str(entity.get("job_site") or "").strip()
            result = await jobs_found_process_job_site(
                short_name, company_website, job_site_entity, debug=debug, ctx=ctx,
            )
            error_state = ROSTER_CONFIG.get("locate_job_page", {}).get("error_state")
            if result.get("error"):  # pragma: no branch
                dest = error_state if (
                    error_state
                    and not result.get("state_held")
                    and not is_provider_balance_refusal(result)
                ) else "-"
                _warn_company(short_name, dest, result["error"])
                # AST-897: balance/credit hold already kept loop-eligible state — do not undo with error_state
                if (
                    error_state
                    and not result.get("state_held")
                    and not is_provider_balance_refusal(result)
                ):  # pragma: no branch
                    transition_company_state(short_name, error_state)
                return {**zero, "total_errors": 1}
            pass_states = ROSTER_CONFIG.get("locate_job_page", {}).get("pass_states", [])
            if result.get("state") in pass_states:  # pragma: no branch
                return {**zero, "total_passed": 1}
            return {**zero, "total_failed": 1}

        elif input_state == ROSTER_CONFIG["select_job_page"]["dispatch_trigger_state"]:
            tk = (dispatch_task_key or "").strip()
            if tk != "select_job_page":
                _warn_company(short_name, "-", f"PJL_READY expects select_job_page, got {tk}")
                return {**zero, "total_errors": 1}
            result = await run_select_job_page_dispatch(entity, batch_id, ctx, debug)
            sel_cfg = ROSTER_CONFIG["select_job_page"]
            if result.get("error"):
                _warn_company(short_name, "-", result["error"])
                return {**zero, "total_errors": 1}
            terminal_ok = frozenset({
                sel_cfg.get("identified_state"),
                sel_cfg.get("exhausted_state"),
                sel_cfg.get("retry_state"),
                "NO_OPENINGS",
                "JOBSITE_SCRAPE_ISSUE",
                "NO_JOBLIST",
            })
            if result.get("state") in sel_cfg.get("pass_states", []) or result.get("state") in terminal_ok:
                return {**zero, "total_passed": 1}
            return {**zero, "total_failed": 1}

        elif input_state in (
            ROSTER_CONFIG["parse_job_list"]["dispatch_trigger_state"],
            ROSTER_CONFIG["parse_job_list"]["retry_trigger_state"],
        ):
            tk = (dispatch_task_key or "").strip()
            if tk != "parse_job_list":
                _warn_company(short_name, "-", f"{input_state} expects parse_job_list, got {tk}")
                return {**zero, "total_errors": 1}
            result = await run_parse_job_list_dispatch(entity, batch_id, ctx, debug)
            parse_cfg = ROSTER_CONFIG["parse_job_list"]
            if result.get("error"):
                _warn_company(short_name, "-", result["error"])
                return {**zero, "total_errors": 1}
            ok_states = frozenset({
                parse_cfg["pass_state"],
                parse_cfg["retry_state"],
                parse_cfg["terminal_fail_state"],
            })
            if result.get("state") in ok_states:
                return {**zero, "total_passed": 1}
            return {**zero, "total_failed": 1}

        elif input_state == "WATCH":
            from src.core.gazer import process_gazer_batch  # lazy import avoids circular
            error_state = ROSTER_CONFIG.get("gaze", {}).get("error_state")
            outcomes = await process_gazer_batch(batch_id, [entity], debug=debug, ctx=ctx)
            o = outcomes[0] if outcomes else {}
            if o.get("status") == "failure":
                _warn_company(short_name, error_state or "-", o.get("message", "") or "gaze failed")
                if error_state:
                    transition_company_state(short_name, error_state)
                return {**zero, "total_errors": 1}
            _entity_info(short_name, "company", "gaze", o.get("message", "") or "ok")
            return {**zero, "total_passed": 1}

        else:
            _warn_company(short_name, "-", f"unhandled input_state={input_state}")
            return {**zero, "total_errors": 1}

    except Exception as e:
        logger.exception(
            "%s | company run_company_task\n  %s: %s\n  Continuing to the next company",
            short_name,
            type(e).__name__,
            e,
        )
        return {**zero, "total_errors": 1}


async def run_select_job_page_dispatch(
    entity: Dict[str, Any],
    batch_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """PJL_READY decomposed select_job_page entry (AST-720)."""
    _ = batch_id
    short_name = entity.get("short_name", "")
    company_website = entity.get("company_website", "")
    company = get_company(short_name)
    cdata = (company.get("company_data") or {}) if company else {}
    row_state = (company or {}).get("state") or ""
    entity_state = entity.get("state") or row_state
    if entity_state != "PJL_READY" and row_state != "PJL_READY":
        _warn_company(short_name, "-", f"unexpected state {entity_state or row_state} (PJL_READY only)")
        return {"short_name": short_name, "state": entity_state or row_state, "error": "unexpected_state"}

    assembled_content, page_url_map, visible_map = _pjl_maps_from_company_data(cdata)
    if not assembled_content.strip():
        _save_company(short_name=short_name, company_website=company_website,
                      state="NO_PJL_SELECTED", page_option_url=company_website,
                      raw_response={"response_type": "NO_PJL_ASSEMBLED"})
        return {"short_name": short_name, "state": "NO_PJL_SELECTED", "job_site": "", "response_type": "NO_PJL_ASSEMBLED"}
    nav_links = _nav_links_for_try_links(cdata)
    live_content = _build_select_job_page_live_content(assembled_content, nav_links)
    logger.debug(
        "Calling _find_job_page_from_assembled: page_url_map=%s assembled_content=%s",
        page_url_map, live_content,
    )
    ctx_no_chain = {k: v for k, v in (ctx or {}).items() if k != "resolve_run_next_live"}
    result = await _find_job_page_from_assembled(
        short_name=short_name,
        company_website=company_website,
        assembled_content=live_content,
        page_url_map=page_url_map,
        page_dom_map={},
        visible_map=visible_map,
        nav_links=nav_links,
        browser_context=None,
        debug=debug,
        ctx=ctx_no_chain,
        chain_parse=False,
        decomposed=True,
    )
    logger.debug("Response from _find_job_page_from_assembled: %s", result)
    return result


async def _scrape_list_page_dom_for_parse(
    url: str,
    browser_context: Optional[BrowserSession] = None,
    debug: bool = False,
    *,
    batch_session=None,
    short_name: str = "",
) -> str:
    """Playwright DOM reload for parse_job_list — careers-list readiness (AST-689)."""
    _ = debug
    try:
        if batch_session is not None:
            pg = await get_page(batch_session=batch_session, url=url)
        else:
            pg = await get_page(browser_context, url)
        try:
            readiness_cfg = roster_scrape_readiness_config()
            ready_meta = await wait_for_careers_list_readiness(pg, readiness_cfg)
            logger.debug("Response from wait_for_careers_list_readiness: %s", ready_meta)
            return (await extract_page_dom(pg)) or ""
        finally:
            await close_page(pg)
    except Exception as scrape_err:
        if isinstance(scrape_err, PlaywrightInfraError):
            fc = scrape_err.failure_class
            msg = scrape_err.detail
        else:
            fc = classify_playwright_failure(scrape_err)
            msg = str(scrape_err)
        if is_playwright_infra_failure(fc):
            if isinstance(scrape_err, PlaywrightInfraError):
                raise
            raise PlaywrightInfraError(fc, msg) from scrape_err
        raise


def _resolve_selected_pjl_url(cdata: dict) -> str:
    key = ROSTER_CONFIG["parse_job_list"]["selected_pjl_url_key"]
    return str(cdata.get(key) or "").strip()


def _parse_dispatch_failure_state(input_state: str) -> str:
    st = (input_state or "").strip()
    parse_cfg = ROSTER_CONFIG["parse_job_list"]
    if st == parse_cfg["dispatch_trigger_state"]:
        return parse_cfg["retry_state"]
    if st == parse_cfg["retry_trigger_state"]:
        return parse_cfg["terminal_fail_state"]
    return parse_cfg["terminal_fail_state"]


def _save_parse_dispatch_failure(
    short_name: str,
    company_website: str,
    list_url: str,
    input_state: str,
    raw_response: Optional[Dict[str, Any]] = None,
    notes: Optional[str] = None,
    response_type: str = "PARSE_DISPATCH_FAIL",
) -> Dict[str, Any]:
    fail_state = _parse_dispatch_failure_state(input_state)
    if notes:
        save_company_data(short_name, {"parse_job_list_notes": notes})
    _save_company(
        short_name=short_name,
        company_website=company_website,
        state=fail_state,
        page_option_url=list_url or company_website,
        raw_response=raw_response or {"response_type": response_type},
        pre_run_job_site="",
    )
    return {
        "short_name": short_name,
        "state": fail_state,
        "job_site": "",
        "response_type": response_type,
    }


def _finalize_parse_dispatch_success(
    short_name: str,
    company_website: str,
    list_url: str,
    dom_html: str,
    parsed: Dict[str, Any],
    job_titles: List[Any],
) -> Dict[str, Any]:
    container = (parsed.get("job_container") or "").strip()
    job_tag = (parsed.get("job_tag") or "").strip()
    container_index = _compute_container_index(dom_html, container, job_titles)
    parse_instructions = {"container": container, "job_tag": job_tag, "container_index": container_index}
    save_company_data(short_name, {"parse_instructions": parse_instructions})
    _save_company(
        short_name=short_name,
        company_website=company_website,
        state="WATCH",
        page_option_url=list_url,
        raw_response=parsed,
    )
    return {
        "short_name": short_name,
        "state": "WATCH",
        "job_site": list_url,
        "response_type": "PARSE_DISPATCH_OK",
        "parse_instructions": parse_instructions,
    }


async def run_parse_job_list_dispatch(
    entity: Dict[str, Any],
    batch_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_session=None,
) -> Dict[str, Any]:
    """JOBLIST_IDENTIFIED / JOBLIST_IDENTIFIED_RETRY: DOM reload + parse_job_list (AST-721)."""
    _ = batch_id
    short_name = entity.get("short_name", "")
    company_website = entity.get("company_website", "")
    input_state = str(entity.get("state") or "").strip()
    allowed = (
        ROSTER_CONFIG["parse_job_list"]["dispatch_trigger_state"],
        ROSTER_CONFIG["parse_job_list"]["retry_trigger_state"],
    )
    if input_state not in allowed:
        _warn_company(short_name, "-", f"unexpected state {input_state}")
        return {"short_name": short_name, "state": input_state, "error": "unexpected_state"}
    company = get_company(short_name)
    cdata = (company.get("company_data") or {}) if company else {}
    list_url = _resolve_selected_pjl_url(cdata)
    if not list_url:
        return _save_parse_dispatch_failure(
            short_name, company_website, "", input_state,
            notes="missing selected_pjl_url", response_type="PARSE_DISPATCH_MISSING_URL",
        )
    job_titles = _normalize_job_titles(cdata.get("job_titles"))
    if not job_titles:
        return _save_parse_dispatch_failure(
            short_name, company_website, list_url, input_state,
            notes="missing job_titles", response_type="PARSE_DISPATCH_MISSING_TITLES",
        )
    cull_outcome = ""
    logger.debug(
        "Calling run_parse_job_list_dispatch: url=%s titles=%s state=%s",
        list_url, job_titles, input_state,
    )

    async def _scrape_and_parse(browser_context=None):
        nonlocal cull_outcome
        dom_html = await _scrape_list_page_dom_for_parse(
            list_url,
            browser_context,
            debug=debug,
            batch_session=batch_session,
            short_name=short_name,
        )
        if not dom_html.strip():
            return _save_parse_dispatch_failure(
                short_name, company_website, list_url, input_state,
                notes="empty dom after reload", response_type="PARSE_DISPATCH_EMPTY_DOM",
            )
        dom_joined, containers, cull_outcome = _culled_dom_for_parse(dom_html, job_titles)
        logger.debug(
            "Response from _culled_dom_for_parse: titles=%s containers=%s cull_outcome=%r dom_joined=%s",
            job_titles, containers, cull_outcome, dom_joined,
        )
        if cull_outcome == "cull_miss" or not dom_joined.strip():
            return _save_parse_dispatch_failure(
                short_name, company_website, list_url, input_state,
                notes="containers not found for titles", response_type="PARSE_DISPATCH_NO_CONTAINERS",
            )
        parsed = await _fetch_parse_job_list(dom_joined, short_name, debug=debug, ctx=ctx)
        container = (parsed.get("job_container") or "").strip()
        job_tag = (parsed.get("job_tag") or "").strip()
        if not container or not job_tag:
            return _save_parse_dispatch_failure(
                short_name, company_website, list_url, input_state,
                raw_response=parsed, notes="parse returned empty container or job_tag",
                response_type="PARSE_DISPATCH_INVALID",
            )
        err, _, _ = _validate_parse_job_list_raw_job_listings(
            dom_joined, container, job_tag, parsed.get("job_ids", []),
        )
        if err:
            return _save_parse_dispatch_failure(
                short_name, company_website, list_url, input_state,
                raw_response=parsed, notes=err, response_type="PARSE_DISPATCH_VALIDATION",
            )
        return _finalize_parse_dispatch_success(
            short_name, company_website, list_url, dom_html, parsed, job_titles,
        )

    try:
        if batch_session is not None:
            result = await _scrape_and_parse()
        else:
            async with create_browser_context() as browser_context:
                result = await _scrape_and_parse(browser_context)
    except PlaywrightInfraError as ex:
        logger.exception(
            "%s | company parse_job_list scrape\n  %s: %s\n  Continuing to the next company",
            short_name,
            type(ex).__name__,
            ex,
        )
        result = _save_parse_dispatch_failure(
            short_name, company_website, list_url, input_state,
            notes=f"[playwright:{ex.failure_class}] {ex.detail}",
            response_type="PARSE_DISPATCH_INFRA",
        )
    except Exception as ex:
        logger.exception(
            "%s | company parse_job_list scrape\n  %s: %s\n  Continuing to the next company",
            short_name,
            type(ex).__name__,
            ex,
        )
        result = _save_parse_dispatch_failure(
            short_name, company_website, list_url, input_state,
            notes=str(ex),
            response_type="PARSE_DISPATCH_ERROR",
        )
    logger.debug("Response from run_parse_job_list_dispatch: %s", result)
    return result


async def parse_job_list_batch(
    batch_id: str,
    companies: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, int]:
    """Shared-browser parse_job_list for a claimed company batch (AST-891)."""
    parse_cfg = ROSTER_CONFIG["parse_job_list"]
    max_concurrent = int(parse_cfg["max_concurrent"])
    scrape_timeout = PLAYWRIGHT_CONFIG["company_scrape_timeout_seconds"]
    ok_states = frozenset({
        parse_cfg["pass_state"],
        parse_cfg["retry_state"],
        parse_cfg["terminal_fail_state"],
    })
    company_total = len(companies)
    passed = errors = 0
    logger.debug("Beginning parse_job_list loop on %s items", company_total)

    async with create_batch_browser_session() as batch_session:
        async def _one(company: Dict[str, Any], company_index: int) -> None:
            nonlocal passed, errors
            short_name = company.get("short_name") or ""
            company_website = company.get("company_website") or ""
            input_state = str(company.get("state") or "").strip()
            company_row = get_company(short_name)
            cdata = (company_row.get("company_data") or {}) if company_row else {}
            list_url = _resolve_selected_pjl_url(cdata)
            logger.debug(
                "Calling run_parse_job_list_dispatch: [%s/%s] %s state=%s url=%s",
                company_index, company_total, short_name, input_state, list_url,
            )
            try:
                result = await asyncio.wait_for(
                    run_parse_job_list_dispatch(
                        company, batch_id, ctx, debug, batch_session=batch_session,
                    ),
                    timeout=scrape_timeout,
                )
            except asyncio.TimeoutError:
                logger.exception(
                    "%s | company parse_job_list scrape\n  TimeoutError: scrape exceeded %ss\n  Continuing to the next company",
                    short_name,
                    scrape_timeout,
                )
                result = _save_parse_dispatch_failure(
                    short_name,
                    company_website,
                    list_url,
                    input_state,
                    notes=f"[playwright:scrape_timeout] company scrape exceeded {scrape_timeout}s",
                    response_type="PARSE_DISPATCH_INFRA",
                )
            logger.debug("Response from run_parse_job_list_dispatch: %s", result)
            if result.get("error") or result.get("state") not in ok_states:
                errors += 1
            else:
                passed += 1

        sem = asyncio.Semaphore(max_concurrent)

        async def _limited(company: Dict[str, Any], company_index: int) -> None:
            async with sem:
                await _one(company, company_index)

        results = await asyncio.gather(
            *[_limited(c, ci) for ci, c in enumerate(companies, start=1)],
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, BaseException):
                errors += 1
                logger.exception(
                    "%s | company parse_job_list_batch\n  %s: %s\n  Continuing to the next company",
                    batch_id,
                    type(r).__name__,
                    r,
                    exc_info=r,
                )

    logger.debug("End parse_job_list loop after %s items", company_total)
    return {"passed": passed, "failed": 0, "total": company_total, "errors": errors}


async def process_recheck_no_openings(
    entity: Dict[str, Any],
    batch_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """NO_OPENINGS: load job_site, visible text via Playwright only (no Anthropic).

    Mirrors prefilter_company redirect normalization. ctx/debug reserved for dispatcher parity.
    """
    _ = (batch_id, ctx, debug)
    short_name = str(entity.get("short_name") or "").strip()
    job_site = str(entity.get("job_site") or "").strip()
    if not short_name:
        return {"success": False, "message": "missing short_name", "new_state": ""}
    if not job_site:
        return {"success": False, "message": "missing job_site", "new_state": ""}

    cdata = entity.get("company_data") if isinstance(entity.get("company_data"), dict) else {}
    no_jobs_message = str((cdata or {}).get("no_jobs_message") or "").strip()
    if not no_jobs_message:
        return {"success": False, "message": "no_jobs_message missing", "new_state": ""}

    try:
        async with create_browser_context() as browser_context:
            visible_text, final_url = await get_visible_text(
                job_site, context=browser_context, return_final_url=True
            )
    except Exception as ex:
        logger.exception(
            "%s | company recheck_no_openings\n  %s: %s\n  State unchanged",
            short_name,
            type(ex).__name__,
            ex,
        )
        return {"success": False, "message": f"playwright scrape: {ex}", "new_state": ""}

    if final_url and final_url != job_site:
        _entity_info(short_name, "company", "job_site redirect", f"{job_site} -> {final_url}")
        update_company(short_name, job_site=final_url)
        job_site = final_url

    text_blob = visible_text or ""
    if no_jobs_message in text_blob:
        update_company_last_scan_at(short_name)
        _entity_info(short_name, "company", "recheck_no_openings", "staying NO_OPENINGS")
        return {"success": True, "message": "no_jobs_message_present", "new_state": "NO_OPENINGS"}

    transition_company_state(short_name, "JOBS_FOUND")
    update_company_last_scan_at(short_name)
    return {"success": True, "message": "no_jobs_message_absent", "new_state": "JOBS_FOUND"}


# ---- Batch API ----
def get_new_company_batch(
    state: str, limit: Optional[int] = None, candidate_id: Optional[str] = None,
    batch_id: Optional[str] = None, context: Optional[str] = None,
    *,
    sort_by: Optional[str] = None,
    scan_interval_hours: Optional[float] = None,
    require_empty_website: bool = False,
    score_floor: Optional[float] = None,
    states: Optional[List[str]] = None,
    exclude_prefilter_second_strike: bool = False,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Claim companies for batch processing. Returns (batch_id, companies).

    Criteria (limit, sort_by, scan_interval_hours) from COMPANY_STATES[state]["batch_criteria"],
    optionally overridden by the dispatcher (dispatch_task.sort_by, freq_hrs for gaze cadence).
    Caller passes state only; limit overrides criteria when provided.
    candidate_id: when provided, scopes claim to this candidate's companies.
    batch_id: when provided, uses this batch_id instead of generating a new one.
    context: prefix for auto-generated batch_id (required when batch_id is not provided).
    """
    allowed = list(COMPANY_STATES.keys()) if COMPANY_STATES else []
    if states is None:
        if not allowed or state not in allowed:
            raise ValueError(f"state must be one of {allowed!r}, got {state!r}")
    else:
        for s in states:
            if not allowed or s not in allowed:
                raise ValueError(f"state must be one of {allowed!r}, got {s!r}")
    state_config = (COMPANY_STATES or {}).get(state, {})
    batch_criteria = state_config.get("batch_criteria", {})
    limit_val = limit if limit is not None else batch_criteria.get("limit", 10)
    default_sort = batch_criteria.get("sort_by", "updated_at")
    sort_by = sort_by if sort_by and sort_by in COMPANY_BATCH_SORT_COLUMNS else default_sort
    scan_from_state = batch_criteria.get("scan_interval_hours")
    eff_scan = scan_interval_hours if scan_interval_hours is not None and scan_interval_hours > 0 else scan_from_state
    if not batch_id and not context:
        raise ValueError("batch_id or context is required for batch_id generation")
    bid = batch_id or f"{context}-{uuid.uuid4()}"
    claim_company_batch(
        bid, state, limit_val, sort_by=sort_by, scan_interval_hours=eff_scan,
        candidate_id=candidate_id, require_empty_website=require_empty_website,
        score_floor=score_floor,
        states=states,
        exclude_prefilter_second_strike=exclude_prefilter_second_strike,
    )
    companies = get_company_batch(bid)
    return (bid, companies)

def clear_company_batch(batch_id: str) -> int:
    """Release batch. Returns count cleared."""
    return set_company_batch(batch_id, clear=True)


# ---- Prefilter ----

def _vector_labels_from_ctx(ctx: Optional[Dict[str, Any]]) -> Dict[str, str]:
    from src.core.candidate import rubric_criteria_for_task

    candidate_id = str((ctx or {}).get("astral_candidate_id") or "")
    criteria = rubric_criteria_for_task(candidate_id, "prefilter_company") if candidate_id else []
    return {item["code"]: item["label"] for item in criteria if item.get("code") and item.get("label")}


def _flatten_prefilter_parsed(parsed: Any) -> Dict[str, Any]:
    if isinstance(parsed, dict) and isinstance(parsed.get("companies"), list) and parsed["companies"]:
        first = parsed["companies"][0]
        if isinstance(first, dict):
            return first
    if isinstance(parsed, dict) and isinstance(parsed.get("grades"), list):
        return parsed
    raise ValueError("prefilter_company: unrecognised parsed_response shape")


def _prefilter_api_failure_is_retryable(api_result: Dict[str, Any]) -> bool:
    """True when the model call returned a body but decode/validation failed (AST-606)."""
    if api_result.get("raw_response") is not None:
        return True
    return api_result.get("api_response") is not None


def _prefilter_fail(
    short_name: str,
    cfg: Dict[str, Any],
    result: Dict[str, Any],
    error: str,
    *,
    api_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Route retryable failures via current state (one retry then ERROR_PREFILTER); hard → error."""
    company = get_company(short_name) or {}
    current_state = (company.get("state") or "").strip()
    # AST-897: provider balance/credit refusal — hold current loop-eligible state
    if api_result is not None and is_provider_balance_refusal(api_result):
        result["error"] = error
        result["state"] = current_state
        result["decision"] = "HOLD"
        result["failure_class"] = api_result.get("failure_class")
        result["state_held"] = True
        return result
    retryable = api_result is None or (
        not api_result.get("success") and _prefilter_api_failure_is_retryable(api_result)
    )
    if not retryable:
        dest = cfg["error_state"]
    else:
        dest = _prefilter_batch_fail_dest(current_state, cfg) or cfg["error_state"]
    transition_company_state(short_name, dest)
    result["error"] = error
    result["state"] = dest
    result["decision"] = "RETRY" if dest == cfg["retry_state"] else "ERROR"
    return result


def _company_used_inflow_prefilter(short_name: str) -> bool:
    company = get_company(short_name)
    if not company:
        return False
    for entry in reversed(company.get("state_history") or []):
        if entry.get("to_state") == "WEBSITE_FOUND" and entry.get("from_state") == "NEW":
            return True
    return False


def _company_on_decomposed_pjl_path(short_name: str, *, input_state: str = "") -> bool:
    if _company_used_inflow_prefilter(short_name):
        return True
    if input_state == "HOMEPAGE_READY":
        return True
    company = get_company(short_name)
    return (company or {}).get("state") == "HOMEPAGE_READY"


def _hydrate_prefilter_pjl_urls(link_indices: List[int], nav_links_enumerated: str) -> List[str]:
    if not link_indices or not (nav_links_enumerated or "").strip():
        return []
    url_map = parse_enumerate_array(nav_links_enumerated)
    out: List[str] = []
    for idx in link_indices:
        raw = url_map.get(int(idx)) if isinstance(idx, int) or str(idx).isdigit() else None
        if not raw and str(idx).startswith("http"):
            raw = str(idx)
        if not raw:
            continue
        norm = normalize_link(raw)
        if norm and norm not in out:
            out.append(norm)
    return out


def _has_dealbreaker_f(grades: List[Dict[str, Any]]) -> bool:
    return any(
        g.get("grade") == "F"
        and isinstance(g.get("confidence"), int)
        and g["confidence"] >= 2
        for g in (grades or [])
    )


def finalize_page_scrape_contract(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Collapse visible text and enumerate nav links from raw Playwright scrape (AST-759)."""
    out = dict(raw or {})
    visible_text = collapse_consecutive_blank_lines(out.get("visible_text") or "")
    nav_urls = out.get("nav_urls") or []
    out["visible_text"] = visible_text
    out["enumerated_nav_links"] = enumerate_array("", nav_urls) if nav_urls else ""
    out["nav_urls"] = nav_urls
    return out


async def scrape_loaded_page_contract(page, *, debug: bool = False) -> Dict[str, Any]:
    """Single page load → collapsed visible text + enumerated nav links (AST-759)."""
    _ = debug
    raw = await extract_page_scrape_contract(page)
    contract = finalize_page_scrape_contract(raw)
    final_url = contract.get("final_url") or getattr(page, "url", "")
    visible_text = contract.get("visible_text") or ""
    nav_urls = contract.get("nav_urls") or []
    logger.debug(
        "Response from extract_page_scrape_contract: url=%s visible_text=%s nav_urls=%s",
        final_url, visible_text, nav_urls,
    )
    return contract


async def scrape_company_homepage_content(
    short_name: str,
    company_website: str,
    *,
    browser_context=None,
    batch_session=None,
) -> Dict[str, Any]:
    """Scrape homepage visible text and nav_links without agent evaluation (AST-701 fetch_website)."""
    out: Dict[str, Any] = {
        "company_website": company_website,
        "visible_text": "",
        "enumerated_nav_links": "",
        "error": None,
    }
    try:
        if batch_session is not None:
            pg = await get_page(batch_session=batch_session, url=company_website)
            try:
                contract = await scrape_loaded_page_contract(pg, debug=False)
            finally:
                await close_page(pg)
        elif browser_context is not None:
            pg = await get_page(browser_context, company_website)
            try:
                contract = await scrape_loaded_page_contract(pg, debug=False)
            finally:
                await close_page(pg)
        else:
            async with create_browser_context() as ctx:
                pg = await get_page(ctx, company_website)
                try:
                    contract = await scrape_loaded_page_contract(pg, debug=False)
                finally:
                    await close_page(pg)
    except Exception as scrape_err:
        if isinstance(scrape_err, PlaywrightInfraError):
            fc = scrape_err.failure_class
            msg = scrape_err.detail
        else:
            fc = classify_playwright_failure(scrape_err)
            msg = str(scrape_err)
        if is_playwright_infra_failure(fc):
            out["error"] = f"[playwright:{fc}] {msg}"
        else:
            out["error"] = str(scrape_err)
        logger.exception(
            "%s | company homepage scrape\n  %s: %s\n  Leaving homepage unread",
            short_name,
            type(scrape_err).__name__,
            scrape_err,
        )
        return out
    final_url = contract.get("final_url") or company_website
    if final_url and final_url != company_website:
        update_company(short_name, company_website=final_url)
        company_website = final_url
        out["company_website"] = company_website
    visible_text = contract.get("visible_text") or ""
    out["visible_text"] = visible_text
    if not out["visible_text"].strip():
        out["error"] = "No visible text extracted"
        return out
    enumerated = contract.get("enumerated_nav_links") or ""
    if enumerated:
        out["enumerated_nav_links"] = enumerated
    nav_error = contract.get("nav_error")
    if nav_error:
        _warn_company(short_name, "-", f"nav_links extraction failed (non-fatal): {nav_error}")
    return out


def _apply_prefilter_decoded_company_outcome(
    short_name: str,
    flat: Dict[str, Any],
    cfg: Dict[str, Any],
    ctx: Optional[Dict[str, Any]],
    *,
    nav_links_from_data: str = "",
    debug: bool = False,
    debug_index: int = 1,
    debug_total: int = 1,
) -> str:
    """Shared post-decode prefilter outcome: hydrate, verdict, persist, transition."""
    from src.core.consult import (
        _render_pass_fail,
        _render_score,
        _dispatch_score_floor_for_task,
        _hydrate_grade_reasons_from_rubric,
        _require_complete_grade_set,
        _debug_incomplete_grade_set,
    )
    from src.core.candidate import rubric_criteria_for_task

    grades = flat.get("grades") or []
    candidate_id = str((ctx or {}).get("astral_candidate_id") or "")
    rubric_list = rubric_criteria_for_task(candidate_id, "prefilter_company") if candidate_id else []
    if grades and rubric_list:
        _hydrate_grade_reasons_from_rubric(grades, rubric_list)
        # Incomplete/extra → re-raise for caller `_prefilter_fail` retry path (AST-1155).
        try:
            _require_complete_grade_set(rubric_list, grades)
        except ValueError:
            if debug:
                _debug_incomplete_grade_set(
                    func="roster._apply_prefilter_decoded_company_outcome",
                    identifier=short_name,
                    rubric_criteria=rubric_list,
                    grades=grades,
                    dest=cfg.get("retry_state") or cfg.get("error_state"),
                    index=debug_index,
                    total=debug_total,
                )
            raise
    verdict_state = _render_pass_fail("prefilter_company", grades)
    prefilter_score = None
    # Soft-fail against dispatch row score_floor before pass/fail → new_state branching.
    if verdict_state == cfg["pass_state"] and rubric_list:
        task_cfg = TASK_CONFIG.get("prefilter_company") or {}
        floor = _dispatch_score_floor_for_task(candidate_id, "prefilter_company")
        score_state, score = _render_score(task_cfg, rubric_list, grades, floor)
        if score is not None:
            prefilter_score = float(score)
        if score_state == cfg["fail_state"]:
            verdict_state = cfg["fail_state"]
    link_indices = flat.get("possible_job_links") or []
    on_decomposed = _company_on_decomposed_pjl_path(
        short_name, input_state=cfg.get("input_state") or ""
    )
    pjl_urls: List[str] = []

    if on_decomposed:
        if _has_dealbreaker_f(grades) or verdict_state == cfg["fail_state"]:
            new_state = cfg["fail_state"]
        elif not link_indices:
            new_state = cfg["no_pjl_state"]
        else:
            pjl_urls = _hydrate_prefilter_pjl_urls(link_indices, nav_links_from_data)
            if not pjl_urls:
                new_state = cfg["no_pjl_state"]
            else:
                new_state = cfg["pass_state"]
    elif verdict_state == cfg["pass_state"]:
        new_state = cfg["legacy_pass_state"]
    else:
        new_state = cfg["legacy_fail_state"]

    decision = "TO_WATCH" if new_state in ("TO_WATCH", "PREFILTER_PASSED") else "IGNORE"
    notes = " | ".join(
        f"{g['vector']}={g['grade']}: {g['reason']}" for g in grades if g.get("reason")
    )
    data_to_save: Dict[str, Any] = {
        "prefilter_grades": grades,
        "prefilter_company_notes": notes or "",
        "prefilter_score": prefilter_score,
    }
    if nav_links_from_data:
        data_to_save["nav_links"] = nav_links_from_data
    data_to_save["possible_job_links"] = link_indices
    if new_state == cfg["pass_state"] and pjl_urls:
        data_to_save[cfg["pjl_url_data_key"]] = pjl_urls
    if new_state == cfg["no_pjl_state"]:
        data_to_save["possible_joblist_links"] = []
        data_to_save["possible_job_links"] = []
    if decision == "TO_WATCH" or new_state == cfg["pass_state"]:
        data_to_save["culture_links_to_explore"] = flat.get("culture_links_to_explore") or []
    save_company_data(short_name, data_to_save)
    transition_company_state(short_name, new_state)
    logger.debug(
        "Response from _apply_prefilter_decoded_company_outcome: %s -> %s link_indices=%r",
        short_name, new_state, link_indices,
    )
    return new_state


async def prefilter_company(
    short_name: str,
    company_website: str,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    browser_context=None,
) -> Dict[str, Any]:
    """Scrape company homepage + nav_links, call Estelle's prefilter task (graded rubric
    + culture page selection in one API call), persist result.
    ctx: full candidate raft, forwarded to do_task for token resolution + API key override.
    debug: forwarded to do_task for AST-538 contract debug on the LLM hop.
    browser_context: optional shared BrowserSession to reuse across a batch.
    Returns {decision, state, notes, error}."""
    result: Dict[str, Any] = {"decision": None, "state": None, "notes": None, "error": None}
    if not company_website:
        result["error"] = "No company_website"
        return result
    try:
        scrape = await scrape_company_homepage_content(
            short_name, company_website, browser_context=browser_context
        )
        if scrape.get("error"):
            transition_company_state(short_name, "CANNOT_READ_WEBSITE")
            save_company_data(short_name, {"prefilter_company_notes": scrape["error"]})
            result["error"] = scrape["error"]
            result["state"] = "CANNOT_READ_WEBSITE"
            return result
        company_website = scrape["company_website"]
        visible_text = scrape["visible_text"]
        enumerated_nav_links = scrape["enumerated_nav_links"]

        # Step 3: assemble live_content with homepage + nav_links
        parts = [f"[company_id={short_name}]", f"\n## Homepage Content\n{visible_text}"]
        if enumerated_nav_links:
            parts.append(f"\n## Navigation Links\n{enumerated_nav_links}")
        live_content = "\n".join(parts)

        task_ctx = {
            **(ctx or {}),
            "batch_entities": [{"company_id": short_name, "short_name": short_name}],
            "batch_size": 1,
            "vector_labels": _vector_labels_from_ctx(ctx),
        }
        logger.debug("Calling agent.do_task: task_key=prefilter_company index=%s", short_name)
        logger.debug("Calling agent.do_task live_content: %s", live_content)
        api_result = await do_task(
            task_key="prefilter_company",
            live_content=live_content,
            index=short_name,
            ctx=task_ctx,
            debug=debug,
        )
        logger.debug("Response from agent.do_task: %s", api_result)

        cfg = ROSTER_CONFIG.get("prefilter", {})

        if not api_result.get("success"):
            return _prefilter_fail(
                short_name,
                cfg,
                result,
                api_result.get("error", "Unknown API error: prefilter_company " + short_name),
                api_result=api_result,
            )

        parsed = api_result.get("parsed_response")
        if not parsed:
            return _prefilter_fail(short_name, cfg, result, "No parsed_response from do_task")

        try:
            flat = _flatten_prefilter_parsed(parsed)
        except ValueError as shape_err:
            return _prefilter_fail(short_name, cfg, result, str(shape_err))

        try:
            new_state = _apply_prefilter_decoded_company_outcome(
                short_name,
                flat,
                cfg,
                ctx,
                nav_links_from_data=enumerated_nav_links,
                debug=debug,
            )
        except ValueError as outcome_err:
            return _prefilter_fail(short_name, cfg, result, str(outcome_err))

        decision = "TO_WATCH" if new_state in ("TO_WATCH", "PREFILTER_PASSED") else "IGNORE"
        grades = flat.get("grades") or []
        notes = " | ".join(
            f"{g['vector']}={g['grade']}: {g['reason']}" for g in grades if g.get("reason")
        )
        result["decision"] = decision
        result["state"] = new_state
        result["notes"] = notes
    except Exception as e:
        logger.exception(
            "%s | company prefilter_company\n  %s: %s\n  Continuing without a prefilter decision",
            short_name,
            type(e).__name__,
            e,
        )
        error_state = ROSTER_CONFIG.get("prefilter", {}).get("error_state")
        if error_state:
            transition_company_state(short_name, error_state)
            result["state"] = error_state
        result["error"] = str(e)
    return result


def _company_homepage_ready(company: Dict[str, Any]) -> bool:
    cd = company.get("company_data") or {}
    return len((cd.get("homepage_text") or "").strip()) > 0


def _prefilter_batch_fail_dest(entity_state: Optional[str], cfg: Dict[str, Any]) -> Optional[str]:
    st = (entity_state or "").strip()
    if not st:
        return cfg.get("error_state")
    retry = COMPANY_STATES.get(st, {}).get("retry_state")
    if retry:
        return retry
    if st == cfg.get("retry_state"):
        return cfg.get("error_state")
    return cfg.get("error_state")


def _transition_prefilter_batch_failures(
    companies: List[Dict[str, Any]],
    cfg: Dict[str, Any],
    *,
    debug: bool = False,
    fail_class: str = "technical fail",
) -> None:
    _ = debug
    by_dest: Dict[str, List[str]] = {}
    for company in companies:
        short_name = company.get("short_name")
        if not short_name:
            continue
        dest = _prefilter_batch_fail_dest(company.get("state"), cfg)
        if dest:
            by_dest.setdefault(dest, []).append(short_name)
    for dest, names in by_dest.items():
        for i, short_name in enumerate(names, start=1):
            transition_company_state(short_name, dest)
            logger.debug(
                "Response from _transition_prefilter_batch_failures: %s %s -> %s",
                fail_class, short_name, dest,
            )


async def _run_batch_company_prefilter(
    batch_id: str,
    companies: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    """Pattern-A company prefilter batch: one do_task, position-indexed decode, shared outcome helper."""
    from src.core import tracker
    from src.core.consult import _hydrate_response_jobs_grade_reasons
    from src.core.candidate import rubric_criteria_for_task

    agent_task_key = "prefilter_company"
    cfg = ROSTER_CONFIG["prefilter"]
    pass_states = cfg.get("pass_states") or []
    normalized: List[Dict[str, Any]] = []
    for company in companies:
        short_name = company["short_name"]
        normalized.append({
            "company_id": short_name,
            "short_name": short_name,
            "state": company.get("state"),
            "company_data": company.get("company_data") or {},
        })
    companies = normalized
    input_by_id = {c["short_name"]: c for c in companies}
    short_names = [c["short_name"] for c in companies]

    logger.debug(
        "Beginning company prefilter loop on %s items batch_id=%s chunk=%r short_names=%s",
        len(companies), batch_id, batch_chunk_index, short_names,
    )

    def assemble(batch_companies: List[Dict[str, Any]]) -> str:
        blocks: List[str] = []
        for company in batch_companies:
            sn = company["short_name"]
            cd = company.get("company_data") or {}
            homepage = (cd.get("homepage_text") or "").strip()
            nav = cd.get("nav_links") or ""
            parts = [f"[company_id={sn}]", f"\n## Homepage Content\n{homepage}"]
            if nav:
                parts.append(f"\n## Navigation Links\n{nav}")
            blocks.append("\n".join(parts))
        return enumerate_array(
            "COMPANY PREFILTER ROWS",
            blocks,
            index_key="index",
            index_values=[f"{i:03d}" for i in range(len(batch_companies))],
        )

    candidate_id = str((ctx or {}).get("astral_candidate_id") or "")
    rubric_list = rubric_criteria_for_task(candidate_id, "prefilter_company") if candidate_id else []
    vector_labels = _vector_labels_from_ctx(ctx)
    task_ctx = {
        **(ctx or {}),
        "batch_entities": companies,
        "batch_size": len(companies),
        "vector_labels": vector_labels,
    }
    do_index = f"prefilter_company_batch_{batch_id}"
    if batch_chunk_index is not None:
        do_index = f"{do_index}_c{batch_chunk_index}"
    logger.debug("Calling agent.do_task: task_key=%s index=%s", agent_task_key, do_index)
    logger.debug("Calling agent.do_task live_content: %s", assemble(companies))
    result = await do_task(
        task_key=agent_task_key,
        live_content=assemble(companies),
        index=do_index,
        ctx=task_ctx,
        debug=debug,
    )
    logger.debug("Response from agent.do_task: %s", result)

    if not result.get("success"):
        if is_provider_balance_refusal(result):
            logger.debug(
                "Response from agent.do_task: provider_balance_refusal error=%r failure_class=%r",
                result.get("error"), result.get("failure_class"),
            )
            return {
                "passed": 0,
                "failed": 0,
                "total": len(companies),
                "failure_class": result.get("failure_class"),
                "state_held": True,
            }
        logger.debug("Response from agent.do_task: do_task failed error=%r", result.get("error"))
        _transition_prefilter_batch_failures(
            companies, cfg, debug=debug, fail_class="do_task",
        )
        return {"passed": 0, "failed": 0, "total": len(companies)}

    parsed = result.get("parsed_response") or {}
    response_companies = parsed.get("companies") or []
    try:
        _hydrate_response_jobs_grade_reasons(response_companies, rubric_list)
    except ValueError as hydrate_err:
        logger.exception(
            "%s | company prefilter hydrate\n  %s: %s\n  Continuing without this batch's grades",
            batch_id,
            type(hydrate_err).__name__,
            hydrate_err,
        )
        _transition_prefilter_batch_failures(
            companies, cfg, debug=debug, fail_class="hydrate",
        )
        return {"passed": 0, "failed": 0, "total": len(companies)}

    sent_ids = set(input_by_id.keys())
    received_ids = {rc["company_id"] for rc in response_companies}
    missing = sent_ids - received_ids
    fabricated = received_ids - sent_ids
    missing_rows = [input_by_id[mid] for mid in missing if mid in input_by_id]

    if missing:
        for mid in sorted(missing):
            _warn_company(mid, "-", "prefilter batch omitted this id")
        _transition_prefilter_batch_failures(
            missing_rows, cfg, debug=debug, fail_class="missing id",
        )

    passed = failed = 0
    bad_grades: Set[str] = set()

    for row_idx, response_company in enumerate(response_companies, start=1):
        cid = response_company["company_id"]
        if cid in fabricated:
            continue
        input_company = input_by_id[cid]
        nav_links = (input_company.get("company_data") or {}).get("nav_links") or ""
        try:
            new_state = _apply_prefilter_decoded_company_outcome(
                cid,
                response_company,
                cfg,
                ctx,
                nav_links_from_data=nav_links,
                debug=debug,
                debug_index=row_idx,
                debug_total=len(response_companies),
            )
        except Exception as e:
            bad_grades.add(cid)
            logger.exception(
                "%s | company prefilter decode\n  %s: %s\n  Continuing to the next company",
                cid,
                type(e).__name__,
                e,
            )
            logger.debug(
                "Response from _apply_prefilter_decoded_company_outcome: grades=%s",
                response_company.get("grades"),
            )
            continue
        if new_state in pass_states:
            passed += 1
        else:
            failed += 1

    if bad_grades:
        bad_rows = [input_by_id[cid] for cid in bad_grades if cid in input_by_id]
        # Per-company debug already emitted in the process-exception loop above.
        _transition_prefilter_batch_failures(bad_rows, cfg)

    agent_ref = result.get("agent_ref")
    if agent_ref:
        entity_type = TASK_CONFIG.get(agent_task_key, {}).get("entity_type", "company")
        processed_ids = received_ids - fabricated - bad_grades
        try:
            ensure_batch_response_entity_ids(entity_type, list(processed_ids), agent_ref)
        except Exception as stamp_err:
            logger.exception(
                "%s | company ensure_batch_response_entity_ids\n  %s: %s\n  Continuing without stamping those entity ids",
                batch_id,
                type(stamp_err).__name__,
                stamp_err,
            )

    return {"passed": passed, "failed": failed, "total": len(companies)}


async def prefilter_company_batch(
    batch_id: str,
    companies: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Batch company prefilter from HOMEPAGE_READY rows (AST-702)."""
    cfg = ROSTER_CONFIG["prefilter"]
    ready: List[Dict[str, Any]] = []
    not_ready: List[Dict[str, Any]] = []
    for company in companies:
        if _company_homepage_ready(company):
            ready.append(company)
        else:
            not_ready.append(company)

    logger.debug(
        "Beginning prefilter_company_batch loop on %s items ready=%s not_ready=%s",
        len(companies), len(ready), len(not_ready),
    )

    # Not-ready WFR: leave for fetch_website scrape retry; do not CANNOT_READ.
    skipped = 0
    for ni, company in enumerate(not_ready, start=1):
        short_name = company["short_name"]
        st = (company.get("state") or "").strip()
        if st == cfg["retry_state"]:
            skipped += 1
            logger.debug(
                "End not_ready skip: %s leave WEBSITE_FOUND_RETRY for fetch_website",
                short_name,
            )
            continue
        transition_company_state(short_name, "CANNOT_READ_WEBSITE")
        save_company_data(short_name, {"prefilter_company_notes": "No homepage_text in company_data"})
        skipped += 1
        logger.debug("End not_ready skip: %s -> CANNOT_READ_WEBSITE", short_name)

    if not ready:
        return {
            "passed": 0,
            "failed": 0,
            "total": len(companies),
            "skipped": skipped,
        }

    batch_result = await _run_batch_company_prefilter(batch_id, ready, ctx=ctx, debug=debug)
    batch_result["total"] = len(companies)
    if skipped:
        batch_result["skipped"] = skipped
    return batch_result


# ---- Find job page ----

async def _find_job_page_from_assembled(
    *,
    short_name: str,
    company_website: str,
    assembled_content: str,
    page_url_map: Dict[int, str],
    page_dom_map: Dict[int, str],
    visible_map: Dict[int, str],
    nav_links: str,
    browser_context: Optional[BrowserSession],
    debug: bool,
    ctx: Optional[Dict[str, Any]],
    chain_parse: bool = True,
    decomposed: bool = False,
) -> Dict[str, Any]:
    """AST-469: shared select_job_page + optional TRY_LINK retry + run_next parse chain.
    chain_parse=False: select-only dispatch entry (AST-535) — no run_next parse resolver."""

    logger.debug("Beginning select_job_page loop on 1 items")
    live_sel = assembled_content
    res: Dict[str, Any] = {}
    parsed_top: Dict[str, Any] = {}
    response_type = ""
    try_link_retry_pending = True
    while True:
        rslv = make_locate_parse_resolver(page_dom_map, visible_map) if chain_parse else None
        merged_ctx = dict(ctx) if ctx else {}
        if chain_parse and rslv is not None:
            merged_ctx["resolve_run_next_live"] = rslv
        logger.debug("Calling agent.do_task: task_key=select_job_page index=%s", short_name)
        logger.debug("Calling agent.do_task live_content: %s", live_sel)
        res = await do_task(
            "select_job_page",
            live_content=live_sel,
            index=short_name,
            ctx=merged_ctx,
            debug=debug,
        )
        logger.debug("Response from agent.do_task: %s", res)
        if not res.get("success"):  # pragma: no branch
            if is_provider_balance_refusal(res):
                current_state = (get_company(short_name) or {}).get("state")
                logger.debug(
                    "Response from agent.do_task: provider_balance_refusal failure_class=%r error=%r current_state=%r",
                    res.get("failure_class"), res.get("error"), current_state,
                )
                return {
                    "short_name": short_name,
                    "state": current_state,
                    "job_site": company_website,
                    "response_type": "SELECT_FAILED",
                    "error": res.get("error"),
                    "failure_class": res.get("failure_class"),
                    "state_held": True,
                }
            _save_company(short_name=short_name, company_website=company_website,
                               state="NO_JOBLIST", page_option_url=company_website,
                               raw_response={"response_type": "SELECT_FAILED", "error": res.get("error"), "api": res})
            return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": "SELECT_FAILED"}

        pp = res.get("run_next_parent_parsed")
        parsed_top = pp if pp is not None else res.get("parsed_response")  # type: ignore[assignment]
        if not isinstance(parsed_top, dict):  # pragma: no branch
            _save_company(short_name=short_name, company_website=company_website,
                               state="NO_JOBLIST", page_option_url=company_website, raw_response={"parse": "invalid"})
            return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": "NO_JOBLIST_FOUND"}

        response_type = str(parsed_top.get("response_type") or "")

        logger.debug("Response from select_job_page: response_type=%s", response_type)

        if response_type != "TRY_LINKS":
            break

        try_links = parsed_top.get("try_links") or []
        if decomposed:
            sel_cfg = ROSTER_CONFIG["select_job_page"]
            if not try_links or not try_link_retry_pending:
                _save_company(
                    short_name=short_name, company_website=company_website,
                    state=sel_cfg["exhausted_state"], page_option_url=company_website,
                    raw_response=parsed_top, suppress_job_site=True,
                )
                return {
                    "short_name": short_name,
                    "state": sel_cfg["exhausted_state"],
                    "job_site": "",
                    "response_type": response_type,
                }
            company_row = get_company(short_name)
            cdata = (company_row.get("company_data") or {}) if company_row else {}
            pjl_url_key = sel_cfg["pjl_url_data_key"]
            ledger = list(cdata.get(pjl_url_key) or [])
            updated = _merge_try_links_into_pjl_ledger(
                short_name,
                try_links,
                cdata.get("nav_links") or "",
                cdata.get("pjl_nav_links") or "",
                ledger,
            )
            if updated != ledger:
                save_company_data(short_name, {pjl_url_key: updated})
                transition_company_state(short_name, sel_cfg["retry_state"])
                return {
                    "short_name": short_name,
                    "state": sel_cfg["retry_state"],
                    "job_site": "",
                    "response_type": response_type,
                }
            _save_company(
                short_name=short_name, company_website=company_website,
                state=sel_cfg["exhausted_state"], page_option_url=company_website,
                raw_response=parsed_top, suppress_job_site=True,
            )
            return {
                "short_name": short_name,
                "state": sel_cfg["exhausted_state"],
                "job_site": "",
                "response_type": response_type,
            }

        if not try_links or not try_link_retry_pending:
            _save_company(short_name=short_name, company_website=company_website,
                               state="NO_JOBLIST", page_option_url=company_website, raw_response=parsed_top)
            return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": response_type}

        logger.debug("Beginning TRY_LINKS scrape loop on %s items", len(try_links))
        retry_content, retry_url_map, retry_dom_map, retry_visible = await _fetch_job_links_content(
            try_links, nav_links, browser_context, debug=debug,
        )
        if not retry_content.strip():
            _save_company(short_name=short_name, company_website=company_website,
                               state="NO_JOBLIST", page_option_url=company_website, raw_response=parsed_top)
            return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": response_type}

        page_url_map.update(retry_url_map)
        page_dom_map.update(retry_dom_map)
        visible_map.update(retry_visible)
        live_sel = retry_content
        try_link_retry_pending = False

    selected_page = parsed_top.get("selected_page")
    job_site_url = page_url_map.get(selected_page, company_website)
    pp = res.get("run_next_parent_parsed")

    if response_type == "JOBLIST_TITLES":  # pragma: no branch
        if decomposed:
            return await _finalize_joblist_identified(
                parsed_top, short_name, company_website, job_site_url,
                visible_map, selected_page, response_type, debug, ctx,
            )
        if chain_parse and pp is not None:  # pragma: no branch
            return await _finalize_joblist_titles_after_chain(
                parsed_top, res, short_name, company_website, job_site_url,
                page_dom_map, visible_map, selected_page, response_type, debug, ctx,
            )
        return await _finalize_joblist_titles_select_only(
            parsed_top, short_name, company_website, job_site_url,
            page_dom_map, selected_page, response_type, debug, ctx, visible_map,
        )

    return await _check_parse_results(
        parsed_top, response_type, short_name, company_website, job_site_url,
        page_dom_map=page_dom_map, selected_page=selected_page,
        debug=debug, ctx=ctx, decomposed=decomposed,
    )


async def jobs_found_process_job_site(
    short_name: str,
    company_website: str,
    job_site: str,
    *,
    debug: bool = False,
    ctx: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:  # pragma: no cover — AST-469 JOBS_FOUND path exercised via mocks; roster branch-lock §7.12
    """AST-469: JOBS_FOUND — fresh scrape of stored job_site; same select→parse chain as TO_WATCH locate (no stale job_list_visible)."""
    job_site = (job_site or "").strip()
    if not job_site:
        return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": "", "response_type": "MISSING_JOB_SITE"}

    _strip_company_data_keys(short_name, ("job_list_visible",))

    try:
        visible_text, final_url = await get_visible_text(job_site, return_final_url=True)
    except Exception as ex:
        logger.exception(
            "%s | company jobs_found scrape\n  %s: %s\n  Leaving job_site unscanned",
            short_name,
            type(ex).__name__,
            ex,
        )
        err_st = ROSTER_CONFIG.get("locate_job_page", {}).get("error_state")
        if err_st:
            transition_company_state(short_name, err_st)
        return {"short_name": short_name, "state": err_st or "ERROR_LOCATE_JOB_PAGE", "job_site": job_site, "response_type": "SCRAPE_FAIL"}

    if final_url and final_url != job_site:
        update_company(short_name, job_site=final_url)
        job_site = final_url

    nav_links = enumerate_array("", [job_site])

    async with create_browser_context() as browser_context:
        assembled_content, page_url_map, page_dom_map, visible_map = await _fetch_job_links_content(
            [1], nav_links, browser_context, debug=debug,
        )
        if not assembled_content.strip():
            _save_company(short_name=short_name, company_website=company_website,
                               state="NO_JOBLIST", page_option_url=company_website,
                               raw_response={"response_type": "JOBS_FOUND_SCRAPE_EMPTY", "job_site": job_site})
            return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": job_site, "response_type": "JOBS_FOUND_SCRAPE_EMPTY"}

        return await _find_job_page_from_assembled(
            short_name=short_name,
            company_website=company_website,
            assembled_content=assembled_content,
            page_url_map=page_url_map,
            page_dom_map=page_dom_map,
            visible_map=visible_map,
            nav_links=nav_links,
            browser_context=browser_context,
            debug=debug,
            ctx=ctx,
        )


def _pjl_scrape_ledger_keys(pjl_scrape_pages: list) -> Set[str]:
    return {
        normalize_link(row["url"])
        for row in (pjl_scrape_pages or [])
        if row.get("url")
    }


async def _scrape_pjl_page(
    url: str, browser_context, *, debug: bool = False
) -> Dict[str, Any]:
    fetch_url = (url or "").strip()
    if fetch_url and "://" not in fetch_url:
        fetch_url = f"https://{fetch_url.lstrip('/')}"
    out: Dict[str, Any] = {"url": fetch_url, "visible_text": "", "page_links": []}
    try:
        pg = await get_page(browser_context, fetch_url)
        try:
            readiness_cfg = roster_scrape_readiness_config()
            ready_meta = await wait_for_careers_list_readiness(pg, readiness_cfg)
            logger.debug("Response from wait_for_careers_list_readiness: %s", ready_meta)
            contract = await scrape_loaded_page_contract(pg, debug=debug)
            out["visible_text"] = (contract.get("visible_text") or "").strip()
            out["page_links"] = contract.get("nav_urls") or []
            enum_nav = contract.get("enumerated_nav_links") or ""
            if enum_nav:
                out["enumerated_nav_links"] = enum_nav
            out["readiness"] = ready_meta
        finally:
            await close_page(pg)
    except Exception as e:
        out["error"] = str(e)
        logger.exception(
            "%s | company PJL page scrape\n  %s: %s\n  Continuing to the next page",
            fetch_url,
            type(e).__name__,
            e,
        )
    return out


def _merge_pjl_scrape_record(existing_pages: list, new_record: dict) -> list:
    if normalize_link(new_record.get("url") or "") in _pjl_scrape_ledger_keys(existing_pages):
        return existing_pages
    text = (new_record.get("visible_text") or "").strip()
    if not text:
        return existing_pages
    row: Dict[str, Any] = {"url": new_record["url"], "visible_text": text}
    enum_nav = (new_record.get("enumerated_nav_links") or "").strip()
    if enum_nav:
        row["enumerated_nav_links"] = enum_nav
    return list(existing_pages or []) + [row]


def _merge_pjl_nav_links(existing_enum: str, new_urls: List[str]) -> str:
    existing_map = parse_enumerate_array(existing_enum or "")
    merged: List[str] = []
    seen: Set[str] = set()
    for key in sorted(existing_map.keys()):
        u = existing_map[key]
        nk = normalize_link(u)
        if nk and nk not in seen:
            seen.add(nk)
            merged.append(u)
    for u in new_urls:
        nk = normalize_link(u)
        if nk and nk not in seen:
            seen.add(nk)
            merged.append(u)
    return enumerate_array("", merged) if merged else ""


def _assemble_pjl_content(pjl_scrape_pages: list) -> str:
    sections: List[str] = []
    for n, row in enumerate(pjl_scrape_pages or [], 1):
        url = row.get("url") or ""
        text = row.get("visible_text") or ""
        parts = [f"=== PAGE {n}: {url} ===", text]
        enum_nav = (row.get("enumerated_nav_links") or "").strip()
        if enum_nav:
            parts.extend(["--- NAV LINKS ---", enum_nav])
        sections.append("\n".join(parts))
    return "\n\n".join(sections)


def _assembled_has_embedded_nav_links(assembled_content: str) -> bool:
    return "--- NAV LINKS ---" in (assembled_content or "")


def _build_select_job_page_live_content(assembled_content: str, pjl_nav_links: str) -> str:
    """Build select_job_page agent live content; dedupe global nav when per-page nav present (AST-826)."""
    nav = (pjl_nav_links or "").strip()
    assembled = assembled_content or ""
    if not nav:
        return assembled
    if _assembled_has_embedded_nav_links(assembled):
        return assembled
    if nav in assembled:
        return assembled
    if assembled.strip():
        return f"{assembled.rstrip()}\n\n=== NAV LINKS ===\n{nav}"
    return f"=== NAV LINKS ===\n{nav}"


def _pjl_maps_from_company_data(
    cdata: dict,
) -> Tuple[str, Dict[int, str], Dict[int, str]]:
    assembled = (cdata.get("pjl_assembled_content") or "").strip()
    pages = cdata.get("pjl_scrape_pages") or []
    if not assembled and pages:
        assembled = _assemble_pjl_content(pages)
    page_url_map: Dict[int, str] = {}
    visible_map: Dict[int, str] = {}
    for i, row in enumerate(pages, 1):
        url = row.get("url") or ""
        if url:
            page_url_map[i] = url
        text = (row.get("visible_text") or "").strip()
        if text:
            visible_map[i] = text
    if not assembled and not pages:
        return "", {}, {}
    return assembled, page_url_map, visible_map


def _nav_links_for_try_links(cdata: dict) -> str:
    return (cdata.get("pjl_nav_links") or cdata.get("nav_links") or "").strip()


def _resolve_try_link_normalized(
    item: Any, pjl_nav_links: str, nav_links: str
) -> str:
    if isinstance(item, int) or (isinstance(item, str) and str(item).isdigit()):
        url_map = parse_enumerate_array(pjl_nav_links or nav_links or "")
        raw = url_map.get(int(item))
        return normalize_link(raw or "")
    return normalize_link(str(item))


def _merge_try_links_into_pjl_ledger(
    short_name: str,
    try_links: list,
    nav_links: str,
    pjl_nav_links: str,
    existing: List[str],
) -> List[str]:
    _ = short_name
    out = list(existing or [])
    seen = {normalize_link(u) for u in out if normalize_link(u)}
    for item in try_links or []:
        key = _resolve_try_link_normalized(item, pjl_nav_links, nav_links)
        if key and key not in seen:
            seen.add(key)
            if isinstance(item, int) or (isinstance(item, str) and str(item).isdigit()):
                url_map = parse_enumerate_array(pjl_nav_links or nav_links or "")
                raw = url_map.get(int(item)) or ""
                out.append(raw if raw else str(item))
            else:
                out.append(str(item))
    return out


async def _fetch_job_links_content(
    possible_job_links: List[int],
    nav_links: str,
    browser_context: BrowserSession,
    debug: bool = False,
    ) -> Tuple[str, Dict[int, str], Dict[int, str], Dict[int, str]]:
    """Scrape visible text, DOM, and NEW links from each possible_job_link URL.

    Opens each URL once and extracts all three from the same page load to avoid
    re-navigation (which triggers bot detection on some sites).

    Returns (assembled_content, page_url_map, page_dom_map, page_visible_map) where:
      - assembled_content: enumerated sections ready for select_job_page prompt
      - page_url_map: {page_number: url}
      - page_dom_map: {page_number: culled_dom_html}
      - page_visible_map: {page_number: stripped visible text for JOB_LIST_VISIBLE (AST-469)}
    """
    _ = debug
    url_map = parse_enumerate_array(nav_links)
    nav_url_set = set(url_map.values())

    sections: List[str] = []
    page_url_map: Dict[int, str] = {}
    page_dom_map: Dict[int, str] = {}
    page_visible_map: Dict[int, str] = {}

    logger.debug("Beginning PJL page loop on %s items", len(possible_job_links))
    for page_num, link_id in enumerate(possible_job_links, 1):
        try:
            url = url_map.get(int(link_id))
        except (ValueError, TypeError):
            url = str(link_id) if str(link_id).startswith("http") else None
        if not url:
            logger.debug("PJL page skip: link_id=%s not found in nav_links", link_id)
            continue
        page_url_map[page_num] = url
        try:
            # Single page load — extract text, DOM, and links from the same navigation
            pg = await get_page(browser_context, url)
            try:
                readiness_cfg = roster_scrape_readiness_config()
                ready_meta = await wait_for_careers_list_readiness(pg, readiness_cfg)
                logger.debug("Response from wait_for_careers_list_readiness: %s", ready_meta)
                vt_result = await extract_visible_text(pg)
                visible_text = vt_result.get("text", "") or ""
                dom_html = await extract_page_dom(pg)
                page_links = await extract_site_page_list(page=pg, max_depth=1, verify=False)
            finally:
                await close_page(pg)

            if dom_html:
                page_dom_map[page_num] = dom_html
            vis_stripped = (visible_text or "").strip()
            if vis_stripped:
                page_visible_map[page_num] = vis_stripped

            new_links = [lnk for lnk in (page_links or []) if lnk not in nav_url_set]
            parts = [f"=== PAGE {page_num}: {url} ==="]
            parts.append(visible_text.strip() if visible_text else "(no visible text)")
            if new_links:
                parts.append("--- NEW LINKS ---")
                for i, lnk in enumerate(new_links, 1):
                    parts.append(f"{i}. {lnk}")
            sections.append("\n".join(parts))
            logger.debug(
                "Response from PJL scrape: page=%s url=%s visible_text=%s new_links=%s dom_html=%s",
                page_num, url, visible_text, new_links, dom_html,
            )
        except Exception as e:
            sections.append(f"=== PAGE {page_num}: {url} ===\n(scrape failed: {e})")
            logger.exception(
                "%s | company PJL page scrape\n  %s: %s\n  Continuing to the next page",
                url,
                type(e).__name__,
                e,
            )

    logger.debug("End PJL page loop after %s items", len(possible_job_links))
    return "\n\n".join(sections), page_url_map, page_dom_map, page_visible_map


async def _finalize_joblist_identified(
    select_parsed: Dict[str, Any],
    short_name: str,
    company_website: str,
    job_site_url: str,
    visible_map: Dict[int, str],
    selected_page: Optional[int],
    response_type: str,
    debug: bool,
    ctx: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """AST-720: JOBLIST_TITLES on PJL_READY path — no parse, job_site column unset."""
    _ = debug
    _ = ctx
    sel_cfg = ROSTER_CONFIG["select_job_page"]
    job_titles = _normalize_job_titles(select_parsed.get("job_titles"))
    save_company_data(short_name, {
        "job_titles": job_titles,
        sel_cfg["selected_pjl_url_key"]: job_site_url,
    })
    logger.debug(
        "Response from _finalize_joblist_identified: titles=%r url=%s",
        job_titles, job_site_url,
    )
    vis_save = ""
    if selected_page is not None:
        try:
            vis_save = (visible_map.get(int(selected_page)) or "").strip()
        except (TypeError, ValueError):
            vis_save = ""
    if vis_save:
        save_company_data(short_name, {"job_list_visible": vis_save})
    _save_company(
        short_name=short_name, company_website=company_website,
        state=sel_cfg["identified_state"], page_option_url=job_site_url,
        raw_response=select_parsed, suppress_job_site=True,
    )
    _entity_info(short_name, "company", "joblist identified", sel_cfg["identified_state"])
    return {
        "short_name": short_name,
        "state": sel_cfg["identified_state"],
        "job_site": "",
        "response_type": response_type,
        "job_titles": job_titles,
    }


async def _finalize_joblist_titles_after_chain(
    select_parsed: Dict[str, Any],
    chain_res: Dict[str, Any],
    short_name: str,
    company_website: str,
    job_site_url: str,
    page_dom_map: Dict[int, str],
    visible_map: Dict[int, str],
    selected_page: Optional[int],
    response_type: str,
    debug: bool,
    ctx: Optional[Dict[str, Any]],
) -> Dict[str, Any]:  # pragma: no cover — parse_job_list chained path §7.12
    """AST-469: parse_job_list already ran via run_next; validate and persist like legacy _check_parse_results."""
    _ = debug
    job_titles = _normalize_job_titles(select_parsed.get("job_titles"))
    save_company_data(short_name, {"job_titles": job_titles})
    parsed = chain_res.get("parsed_response") or {}
    dom_html = page_dom_map.get(selected_page, "") if selected_page is not None else ""
    if not dom_html:
        _save_company(short_name=short_name, company_website=company_website,
                           state="NO_JOBLIST", page_option_url=company_website, raw_response=select_parsed)
        return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": response_type}

    dom_joined, _, cull_outcome = _culled_dom_for_parse(dom_html, job_titles)
    if cull_outcome == "cull_miss" or not dom_joined.strip():
        logger.debug("Response from _culled_dom_for_parse: cull_miss possible bot block")
        _save_company(short_name=short_name, company_website=company_website,
                           state="CANNOT_PARSE_JOB_SITE", page_option_url=job_site_url, raw_response=select_parsed)
        return {"short_name": short_name, "state": "CANNOT_PARSE_JOB_SITE", "job_site": job_site_url, "response_type": response_type}
    full_dom_html = dom_html

    container = (parsed.get("job_container") or "").strip()
    job_tag = (parsed.get("job_tag") or "").strip()

    if not container or not job_tag:
        save_company_data(short_name, {"parse_job_list_notes": "parse returned empty container or job_tag"})
        _save_company(short_name=short_name, company_website=company_website,
                           state="CANNOT_PARSE_JOB_SITE", page_option_url=job_site_url, raw_response=parsed)
        return {"short_name": short_name, "state": "CANNOT_PARSE_JOB_SITE", "job_site": job_site_url, "response_type": response_type}

    err, raw_job_listings, _ = _validate_parse_job_list_raw_job_listings(dom_joined, container, job_tag, parsed.get("job_ids", []))
    if err:
        save_company_data(short_name, {"parse_job_list_notes": err})
        _save_company(short_name=short_name, company_website=company_website,
                           state="CANNOT_PARSE_JOB_SITE", page_option_url=job_site_url, raw_response=parsed)
        return {"short_name": short_name, "state": "CANNOT_PARSE_JOB_SITE", "job_site": job_site_url, "response_type": response_type}

    container_index = _compute_container_index(full_dom_html, container, job_titles)
    parse_instructions = {"container": container, "job_tag": job_tag, "container_index": container_index}

    vis_save = ""
    try:
        sp_i = int(selected_page)  # type: ignore[arg-type]
        vis_save = (visible_map.get(sp_i) or "").strip()
    except (TypeError, ValueError):
        vis_save = ""
    extra_cd: Dict[str, Any] = {"parse_instructions": parse_instructions}
    if vis_save:
        extra_cd["job_list_visible"] = vis_save
    save_company_data(short_name, extra_cd)
    _save_company(short_name=short_name, company_website=company_website,
                       state="WATCH", page_option_url=job_site_url, raw_response=parsed)
    return {"short_name": short_name, "state": "WATCH", "job_site": job_site_url, "response_type": response_type, "parse_instructions": parse_instructions}


async def _finalize_joblist_titles_select_only(
    select_parsed: Dict[str, Any],
    short_name: str,
    company_website: str,
    job_site_url: str,
    page_dom_map: Dict[int, str],
    selected_page: Optional[int],
    response_type: str,
    debug: bool,
    ctx: Optional[Dict[str, Any]],
    visible_map: Dict[int, str],
) -> Dict[str, Any]:  # pragma: no cover — select-only PJL fallback §7.12
    """AST-469: run_next suppressed (empty culled DOM) — validate with legacy _fetch_parse_job_list path."""
    job_titles = _normalize_job_titles(select_parsed.get("job_titles"))
    save_company_data(short_name, {"job_titles": job_titles})
    logger.debug("Calling _fetch_parse_job_list: titles=%s job_site=%s", job_titles, job_site_url)

    dom_html = page_dom_map.get(selected_page, "") if selected_page is not None else ""
    if not dom_html:
        _save_company(short_name=short_name, company_website=company_website,
                           state="NO_JOBLIST", page_option_url=company_website, raw_response=select_parsed)
        return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": response_type}

    dom_joined, _, cull_outcome = _culled_dom_for_parse(dom_html, job_titles)
    if cull_outcome == "cull_miss" or not dom_joined.strip():
        logger.debug("Response from _culled_dom_for_parse: cull_miss possible bot block")
        _save_company(short_name=short_name, company_website=company_website,
                           state="CANNOT_PARSE_JOB_SITE", page_option_url=job_site_url, raw_response=select_parsed)
        return {"short_name": short_name, "state": "CANNOT_PARSE_JOB_SITE", "job_site": job_site_url, "response_type": response_type}
    full_dom_html = dom_html

    parsed = await _fetch_parse_job_list(dom_joined, short_name, debug=debug, ctx=ctx)

    container = (parsed.get("job_container") or "").strip()
    job_tag = (parsed.get("job_tag") or "").strip()

    if not container or not job_tag:
        save_company_data(short_name, {"parse_job_list_notes": "parse returned empty container or job_tag"})
        _save_company(short_name=short_name, company_website=company_website,
                           state="CANNOT_PARSE_JOB_SITE", page_option_url=job_site_url, raw_response=parsed)
        return {"short_name": short_name, "state": "CANNOT_PARSE_JOB_SITE", "job_site": job_site_url, "response_type": response_type}

    err, raw_job_listings, _ = _validate_parse_job_list_raw_job_listings(dom_joined, container, job_tag, parsed.get("job_ids", []))
    if err:
        save_company_data(short_name, {"parse_job_list_notes": err})
        _save_company(short_name=short_name, company_website=company_website,
                           state="CANNOT_PARSE_JOB_SITE", page_option_url=job_site_url, raw_response=parsed)
        return {"short_name": short_name, "state": "CANNOT_PARSE_JOB_SITE", "job_site": job_site_url, "response_type": response_type}

    container_index = _compute_container_index(full_dom_html, container, job_titles)
    parse_instructions = {"container": container, "job_tag": job_tag, "container_index": container_index}
    vis_save = ""
    try:
        vis_save = (visible_map.get(int(selected_page)) or "").strip()  # type: ignore[arg-type]
    except (TypeError, ValueError):
        vis_save = ""
    extra: Dict[str, Any] = {"parse_instructions": parse_instructions}
    if vis_save:
        extra["job_list_visible"] = vis_save
    save_company_data(short_name, extra)
    _save_company(short_name=short_name, company_website=company_website,
                       state="WATCH", page_option_url=job_site_url, raw_response=parsed)
    return {"short_name": short_name, "state": "WATCH", "job_site": job_site_url, "response_type": response_type, "parse_instructions": parse_instructions}


async def _fetch_select_job_page(
    assembled_content: str, short_name: str, debug: bool = False, ctx: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Call select_job_page AI task and return parsed response."""
    _ = debug
    logger.debug("Calling agent.do_task: task_key=select_job_page index=%s", short_name)
    logger.debug("Calling agent.do_task live_content: %s", assembled_content)
    response = await do_task(task_key="select_job_page", live_content=assembled_content, index=short_name, ctx=ctx)
    logger.debug("Response from agent.do_task: %s", response)
    parsed = response.get("parsed_response")
    if parsed is None:
        raise ValueError(f"select_job_page failed: {response.get('error', 'no parsed_response')}")
    return parsed


async def _check_parse_results(
    result: Dict[str, Any],
    response_type: str,
    short_name: str,
    company_website: str,
    job_site_url: str,
    page_dom_map: Dict[int, str],
    selected_page: Optional[int] = None,
    debug: bool = False,
    ctx: Optional[Dict[str, Any]] = None,
    decomposed: bool = False,
) -> Dict[str, Any]:
    """Map select_job_page response_type to company state.

    AST-469: JOBLIST_TITLES is finalized in find_job_page (run_next chain); no longer handled here.
    """
    suppress = decomposed
    if response_type == "JOBLIST_NO_JOBS":
        no_jobs_msg = result.get("no_jobs_message", "")
        _strip_company_data_keys(short_name, ("job_list_visible",))
        _save_company(short_name=short_name, company_website=company_website,
                           state="NO_OPENINGS", page_option_url=job_site_url,
                           raw_response=result, no_jobs_message=no_jobs_msg,
                           suppress_job_site=suppress)
        logger.debug("Response from select_job_page: JOBLIST_NO_JOBS %s", no_jobs_msg)
        return {"short_name": short_name, "state": "NO_OPENINGS", "job_site": "" if suppress else job_site_url, "response_type": response_type}

    if response_type == "JOBSITE_SCRAPE_ISSUE":
        summary = str(result.get("scrape_issue_summary") or "").strip()
        evidence = str(result.get("scrape_issue_evidence") or "").strip()
        _strip_company_data_keys(short_name, ("job_list_visible",))
        _save_company(
            short_name=short_name,
            company_website=company_website,
            state=ROSTER_CONFIG["locate_job_page"]["scrape_issue_state"],
            page_option_url=job_site_url,
            raw_response=result,
            jobsite_scrape_issue_summary=summary or None,
            jobsite_scrape_issue_evidence=evidence or None,
            suppress_job_site=suppress,
        )
        logger.debug(
            "Response from select_job_page: JOBSITE_SCRAPE_ISSUE summary=%r job_site=%s",
            summary, job_site_url,
        )
        return {
            "short_name": short_name,
            "state": ROSTER_CONFIG["locate_job_page"]["scrape_issue_state"],
            "job_site": "" if suppress else job_site_url,
            "response_type": response_type,
        }

    if response_type == "JOBLIST_TITLES":
        # Deprecated direct path: tests and legacy callers; find_job_page uses run_next chain (AST-469).
        return await _finalize_joblist_titles_select_only(
            result, short_name, company_website, job_site_url,
            page_dom_map, selected_page, response_type, debug, ctx, {},
        )

    _save_company(short_name=short_name, company_website=company_website,
                       state="NO_JOBLIST", page_option_url=company_website, raw_response=result)
    return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": response_type}



def _derive_shortname_from_url(url: str) -> str:
    """Extract domain from URL and derive shortname.
    
    Args:
        url: URL string
        
    Returns:
        Lowercase shortname (domain without www. and TLD)
        
    Raises:
        ValueError: If URL cannot be parsed
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        if domain.startswith('www.'):
            domain = domain[4:]
        parts = domain.split('.')
        if len(parts) >= 2:
            main_domain = parts[-2]
        else:
            main_domain = parts[0] if parts else domain
        return main_domain.lower()
    except Exception as e:
        raise ValueError(f"Failed to derive shortname from URL '{url}': {e}")




_PERSIST_PAGE_OPTION_URL_STATES = frozenset({
    "WATCH", "NO_OPENINGS", "CANNOT_PARSE_JOB_SITE", "JOBSITE_SCRAPE_ISSUE",
})


def _job_site_for_persist(
    *,
    terminal_state: str,
    page_option_url: str,
    pre_run_job_site: str,
) -> str:
    """Return job_site column value — never substitute company_website on locate failure."""
    st = (terminal_state or "").strip()
    pre = (pre_run_job_site or "").strip()
    purl = (page_option_url or "").strip()
    if st in _PERSIST_PAGE_OPTION_URL_STATES:
        return purl
    if pre:
        return pre
    return ""


def _save_company(
    short_name: str,
    company_website: str,
    state: str,
    page_option_url: str,
    raw_response: Optional[Dict[str, Any]] = None,
    no_jobs_message: Optional[str] = None,
    parse_type: Optional[str] = None,
    job_tag: Optional[str] = None,
    parse_instructions: Optional[Dict[str, Any]] = None,
    pre_run_job_site: Optional[str] = None,
    jobsite_scrape_issue_summary: Optional[str] = None,
    jobsite_scrape_issue_evidence: Optional[str] = None,
    suppress_job_site: bool = False,
    ) -> None:
    """Save company result to database, then transition state.
    
    Data save via update_company + save_company_data; state transition via transition_company_state.
    Builds company_data (no_jobs_message, parse_instructions when applicable).
    
    Args:
        short_name: Company short name
        company_website: Original company website URL
        state: Company state (UPPERCASE from COMPANY_STATES)
        page_option_url: Candidate listings URL from locate path; persisted via _job_site_for_persist
        raw_response: Raw API response for audit (includes response_type)
        no_jobs_message: Optional message for NO_OPENINGS
        parse_type: Optional parse type (legacy)
        job_tag: Optional job tag (legacy)
        parse_instructions: Optional parse_instructions blob
        pre_run_job_site: Pre-run job_site column; fetched from DB when omitted
        jobsite_scrape_issue_summary: Optional Grace summary for JOBSITE_SCRAPE_ISSUE
        jobsite_scrape_issue_evidence: Optional page-text evidence for JOBSITE_SCRAPE_ISSUE
    """
    if pre_run_job_site is None:
        row = get_company(short_name)
        pre_run_job_site = str((row or {}).get("job_site") or "")
    if suppress_job_site:
        job_site_to_write = ""
    else:
        job_site_to_write = _job_site_for_persist(
            terminal_state=state,
            page_option_url=page_option_url,
            pre_run_job_site=pre_run_job_site,
        )
    cd: Dict[str, Any] = {}
    if no_jobs_message:
        cd["no_jobs_message"] = no_jobs_message
    if jobsite_scrape_issue_summary:
        cd["jobsite_scrape_issue_summary"] = jobsite_scrape_issue_summary
    if jobsite_scrape_issue_evidence:
        cd["jobsite_scrape_issue_evidence"] = jobsite_scrape_issue_evidence
    if parse_instructions:
        cd["parse_instructions"] = parse_instructions
    elif parse_type or job_tag:
        cd["parse_instructions"] = {k: v for k, v in [("parse_type", parse_type), ("job_tag", job_tag)] if v is not None}

    company_name = _extract_company_name_from_url(company_website or page_option_url)
    update_company(short_name,
        company_website=company_website,
        job_site=job_site_to_write,
        company_name=company_name,
    )
    if cd:
        save_company_data(short_name, cd)
    transition_company_state(short_name, state)




async def _fetch_nav_links(company: Dict[str, Any]) -> Optional[str]:
    """Coat-check handler for nav_links. Scrapes homepage link list, saves, returns."""
    short_name = (company.get("short_name") or "").strip()
    company_website = (company.get("company_website") or company.get("job_site") or "").strip()
    if not short_name or not company_website:
        raise ValueError(
            "get_company_data: short_name and company_website (or job_site) required for fetch-on-missing nav_links"
        )
    try:
        logger.debug("Calling extract_site_page_list: url=%s", company_website)
        async with create_browser_context() as context:
            url_list = await extract_site_page_list(
                company_website, max_depth=1, verify=False, context=context
            )
        logger.debug("Response from extract_site_page_list: %s", url_list)
        if not url_list:
            return None
        nav_links = enumerate_array("", url_list)
        save_company_data(short_name, {"nav_links": nav_links})
        _entity_info(short_name, "company", "nav_links saved", len(url_list))
        return nav_links
    except ValueError:
        raise
    except Exception as e:
        logger.exception(
            "%s | company nav_links fetch\n  %s: %s\n  Leaving nav_links unset",
            short_name,
            type(e).__name__,
            e,
        )
        return None


async def _fetch_prefilter_notes(company: Dict[str, Any]) -> Optional[str]:
    """Coat-check handler for prefilter_company_notes.
    Calls prefilter_company (grade-based) and derives notes from grade reasons.
    Does NOT change company state — only persists notes + grades.
    """
    short_name = (company.get("short_name") or "").strip()
    company_website = (company.get("company_website") or company.get("job_site") or "").strip()
    if not short_name or not company_website:
        return None
    try:
        logger.debug("Calling get_visible_text: url=%s", company_website)
        visible_text = await get_visible_text(company_website)
        logger.debug("Response from get_visible_text: %s", visible_text)
        if not visible_text or not visible_text.strip():
            return None

        # Extract nav_links for combined prefilter prompt
        enumerated_nav_links = ""
        try:
            url_list = await extract_site_page_list(
                company_website, max_depth=1, verify=False
            )
            if url_list:
                enumerated_nav_links = enumerate_array("", url_list)
        except Exception as nav_err:
            logger.exception(
                "%s | company prefilter_notes nav_links\n  %s: %s\n  Continuing without nav_links",
                short_name,
                type(nav_err).__name__,
                nav_err,
            )

        parts = [f"[company_id={short_name}]", f"\n## Homepage Content\n{visible_text}"]
        if enumerated_nav_links:
            parts.append(f"\n## Navigation Links\n{enumerated_nav_links}")

        task_ctx = {
            "batch_entities": [{"company_id": short_name, "short_name": short_name}],
            "batch_size": 1,
            "vector_labels": _vector_labels_from_ctx(None),
        }
        logger.debug("Calling agent.do_task: task_key=prefilter_company index=%s", short_name)
        logger.debug("Calling agent.do_task live_content: %s", "\n".join(parts))
        api_result = await do_task(
            task_key="prefilter_company",
            live_content="\n".join(parts),
            index=short_name,
            ctx=task_ctx,
        )
        logger.debug("Response from agent.do_task: %s", api_result)
        if not api_result.get("success"):
            return None
        parsed = api_result.get("parsed_response")
        if not parsed:
            return None
        try:
            flat = _flatten_prefilter_parsed(parsed)
        except ValueError:
            return None
        grades = flat.get("grades") or []
        from src.core.consult import _hydrate_grade_reasons_from_rubric
        from src.core.candidate import get_candidate, rubric_criteria_for_task

        company_row = get_company(short_name) or {}
        candidate_id = company_row.get("candidate_id")
        rubric_list = (
            rubric_criteria_for_task(str(candidate_id), "prefilter_company")
            if candidate_id
            else []
        )
        if grades and rubric_list:
            try:
                _hydrate_grade_reasons_from_rubric(grades, rubric_list)
            except ValueError:
                return None
        notes = " | ".join(
            f"{g['vector']}={g['grade']}: {g['reason']}" for g in grades if g.get("reason")
        )
        if not notes:
            return None
        data_to_save: Dict[str, Any] = {
            "prefilter_company_notes": notes,
            "prefilter_grades": grades,
        }
        if enumerated_nav_links:
            data_to_save["nav_links"] = enumerated_nav_links
        data_to_save["possible_job_links"] = flat.get("possible_job_links") or []
        hydrated = _hydrate_prefilter_pjl_urls(
            flat.get("possible_job_links") or [], enumerated_nav_links
        )
        if hydrated:
            data_to_save["possible_joblist_links"] = hydrated
        culture_links = flat.get("culture_links_to_explore") or []
        if culture_links:
            data_to_save["culture_links_to_explore"] = culture_links
        save_company_data(short_name, data_to_save)
        _entity_info(short_name, "company", "prefilter_notes saved", "ok")
        return notes
    except Exception as e:
        logger.exception(
            "%s | company prefilter_notes fetch\n  %s: %s\n  Leaving prefilter_notes unset",
            short_name,
            type(e).__name__,
            e,
        )
        return None


async def _fetch_website_content(company: Dict[str, Any]) -> Optional[list]:
    """Coat-check handler for website_content.
    Uses culture_links_to_explore from prefilter to select pages to scrape.
    Scrapes selected pages, saves [{url, content}] array.
    """
    short_name = (company.get("short_name") or "").strip()
    if not short_name:
        return None
    try:
        logger.debug("Calling _fetch_website_content for %s", short_name)

        nav_links = await get_company_data(company, "nav_links")
        if not nav_links:
            _warn_company(short_name, "-", "no nav_links available, cannot select pages")
            return None

        cd = (company.get("company_data") or {})
        culture_link_ids = cd.get("culture_links_to_explore") or []

        if not culture_link_ids:
            _entity_info(short_name, "company", "website_content", "no culture pages selected")
            return None

        # Step 3: map selected IDs back to URLs
        url_map = parse_enumerate_array(nav_links)
        selected_urls = [url_map[int(sid)] for sid in culture_link_ids if url_map.get(int(sid))]
        if not selected_urls:
            _warn_company(short_name, "-", "no valid URLs from culture_link_ids")
            return None

        # Step 4: scrape each selected page
        max_pages = ROSTER_CONFIG.get("culture_pages", {}).get("max_pages", 6)
        logger.debug("Beginning culture page scrape loop on %s items", len(selected_urls))
        pages = []
        async with create_browser_context() as context:
            for url in selected_urls[:max_pages]:
                try:
                    text = await get_visible_text(url=url, context=context)
                    logger.debug("Response from get_visible_text: url=%s text=%s", url, text)
                    if text and text.strip():
                        pages.append({"url": url, "content": text.strip()})
                except Exception as e:
                    logger.exception(
                        "%s | company culture page scrape\n  %s: %s\n  Continuing to the next page",
                        url,
                        type(e).__name__,
                        e,
                    )
                    continue

        logger.debug("End culture page scrape loop after %s items", len(pages))
        if not pages:
            _warn_company(short_name, "-", "all culture page scrapes failed")
            return None

        # Step 5: save and return
        save_company_data(short_name, {"website_content": pages})
        _entity_info(short_name, "company", "website_content saved", len(pages))
        return pages
    except ValueError:
        raise
    except Exception as e:
        logger.exception(
            "%s | company website_content fetch\n  %s: %s\n  Leaving website_content unset",
            short_name,
            type(e).__name__,
            e,
        )
        return None



_COATCHECK_HANDLERS = {
    "nav_links": _fetch_nav_links,
    "prefilter_company_notes": _fetch_prefilter_notes,
    "website_content": _fetch_website_content,
}

async def get_company_data(company: Dict[str, Any], key: str) -> Any:
    """Return company_data[key], fetching on-demand if missing (coat-check pattern).
    Registered keys in ROSTER_CONFIG['company_data_keys'] have fetch-on-missing handlers.
    Unregistered keys return None if absent. Never stores empty/failed data.
    """
    company_data = company.get("company_data") or {}
    if not isinstance(company_data, dict):
        company_data = {}
    if key in company_data and company_data[key] is not None:
        return company_data[key]
    registered = ROSTER_CONFIG.get("company_data_keys", {})
    if key not in registered:
        return None
    handler = _COATCHECK_HANDLERS.get(key)
    if not handler:
        return None
    return await handler(company)




def _compute_container_index(full_dom: str, container_selector: str, job_titles: List[str]) -> int:
    """Find which occurrence of container_selector in the full DOM holds the job listings.
    Returns 0 when there's only one match or when job_titles can't disambiguate."""
    # B1 lazy import: BeautifulSoup is heavy and only used on HTML parse paths here.
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(full_dom, "html.parser")
    try:
        all_containers = soup.select(container_selector)
    except Exception:
        return 0
    if len(all_containers) <= 1:
        return 0
    titles_lower = [t.lower() for t in job_titles if t.strip()]
    if not titles_lower:
        return 0
    for i, el in enumerate(all_containers):
        text = el.get_text(" ", strip=True).lower()
        # First container whose text includes any known job title is the one
        if any(t in text for t in titles_lower):
            return i
    return 0


async def _fetch_parse_job_list(dom_html: str, short_name: str, debug: bool = False, ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call parse_job_list task: culled DOM only; returns container, job_tag, job_ids.
    Returns empty dict on failure so caller can fall through to CANNOT_PARSE_JOB_SITE."""
    _ = debug
    logger.debug("Calling agent.do_task: task_key=parse_job_list index=%s", short_name)
    logger.debug("Calling agent.do_task live_content: %s", dom_html or "")
    response = await do_task(
        task_key="parse_job_list",
        live_content=dom_html or "",
        index=short_name,
        ctx=ctx,
    )
    logger.debug("Response from agent.do_task: %s", response)
    if not response or not response.get("success"):
        err = (response or {}).get("error", "no parsed_response")
        _warn_company(short_name, "-", f"parse_job_list failed: {err}")
        save_company_data(short_name, {"parse_job_list_notes": err})
        return {}
    return response.get("parsed_response") or {}


def _validate_parse_job_list_raw_job_listings(
    dom_html: str, container: str, job_tag: str, job_ids: List[str]
    ) -> Tuple[Optional[str], Optional[List[str]], List[str]]:
    """From culled DOM, extract raw_job_listings. Returns (error_or_None, raw_job_listings_or_None, job_ids_not_found)."""
    # B1 lazy import: same as _compute_container_index — bs4 only on parse_job_list validation.
    from bs4 import BeautifulSoup
    if not container or not job_tag or job_ids is None:
        return ("missing container, job_tag, or job_ids", None, [])
    selector = f"{container} {job_tag}".strip()
    soup = BeautifulSoup(dom_html, "html.parser")
    try:
        elements = soup.select(selector)
    except Exception as e:
        return (f"selector invalid: {e}", None, [])
    raw_job_listings = [str(el) for el in elements]
    if len(raw_job_listings) != len(job_ids):
        return (f"raw_job_listing count {len(raw_job_listings)} != job_ids count {len(job_ids)}", None, [])
    job_ids_not_found: List[str] = []
    for i, jid in enumerate(job_ids):
        # Unreachable once lengths match above; retained as belt-and-suspenders (coverage: §7.12 branch lock).
        if i >= len(raw_job_listings):  # pragma: no cover
            return (f"job_ids index {i} out of range", None, job_ids_not_found)
        if jid is None or str(jid).strip() == "":
            continue
        if str(jid) not in raw_job_listings[i]:
            job_ids_not_found.append(str(jid))
    if job_ids_not_found:
        return (f"job_id(s) not found in raw_job_listing: {job_ids_not_found}", None, job_ids_not_found)
    return (None, raw_job_listings, [])



# ---------------------------------------------------------------------------
# Entity page helpers (AST-329)
# ---------------------------------------------------------------------------

def get_company_job_state_counts(short_name: str) -> Dict[str, int]:
    """Return {state: count} for all jobs belonging to company."""
    return get_company_job_counts(short_name)
