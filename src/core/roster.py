"""
Core roster business logic.

Contains business logic for company roster management and job page discovery.
"""

import asyncio
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
    extract_site_page_list,
    extract_visible_text,
    extract_page_dom,
    get_visible_text,
    get_page,
    close_page,
    create_browser_context,
    BrowserSession,
    normalize_url,
    wait_for_careers_list_readiness,
)
from src.external.google_cse import GoogleCseHit, search_google_cse
from src.core.agent import do_task
from src.data.database import (
    claim_company_batch,
    count_companies,
    get_active_trigger_states,
    get_agent_data_for_ids,
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
)
from src.utils.logging import get_logger
from src.utils.config import (
    ASTRAL_CONFIG,
    COMPANY_STATES,
    INFLOW_CONFIG,
    ROSTER_CONFIG,
    TASK_CONFIG,
    roster_scrape_readiness_config,
    validate_value,
)
from src.utils.formatting import (
    collapse_consecutive_blank_lines,
    enumerate_array,
    parse_enumerate_array,
    find_job_containers,
)

# Logger for this module
logger = get_logger(__name__)


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
        containers = find_job_containers(dom_full, titles)
        culled = "\n".join(containers) if containers else ""
        vis = (visible_map.get(sp_int) or "").strip()
        return (culled, vis)

    return resolve_run_next_live


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
        logger.info(
            "[%s] company state %s -> %s (batch_id=%s)",
            short_name,
            from_state or "(none)",
            to_state,
            batch_id or "",
        )
    update_company(short_name, state=to_state, state_history=history)


# ---- Roster inflow discovery (AST-505) ----

_INFLOW_SLUG_RE = re.compile(r"^[a-z0-9_]+$")


def _normalize_company_url_for_dedupe(url: str) -> str:
    """Host-level URL key for roster ingest dedupe (strip www. after normalize_url)."""
    u = (url or "").strip()
    if not u:
        return ""
    n = normalize_url(u)
    parsed = urlparse(n)
    netloc = parsed.netloc or ""
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parsed.path.rstrip("/") if parsed.path else ""
    out = f"{parsed.scheme.lower() if parsed.scheme else 'https'}://{netloc}{path}"
    if parsed.query:
        out += f"?{parsed.query}"
    return out


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
    return urls


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
) -> bool:
    """Create NEW or WEBSITE_FOUND company row for an accepted inflow hit."""
    slug = (slug or "").strip().lower()
    if not slug or not _INFLOW_SLUG_RE.match(slug):
        logger.warning("ingest_new_companies: invalid slug %r for candidate %s", slug, candidate_id)
        return False
    existing = get_company(slug)
    if existing:
        if (existing.get("candidate_id") or "") != candidate_id:
            logger.warning("ingest_new_companies: slug %r owned by another candidate", slug)
        return False
    site = (website or "").strip()
    if site:
        norm = _normalize_company_url_for_dedupe(site)
        if norm and norm in _candidate_company_urls(candidate_id):
            logger.info("ingest_new_companies: duplicate URL for %s candidate %s", slug, candidate_id)
            return False
    target_state = "WEBSITE_FOUND" if site else "NEW"
    save_company(
        short_name=slug,
        state=target_state,
        company_website=site,
        candidate_id=candidate_id,
        company_name=slug,
    )
    if source_hit:
        note_url = (source_hit.get("url") or "").strip()
        if note_url:
            save_company_data(slug, {"inflow_discovery_notes": note_url})
    return True


async def resolve_company_website(
    short_name: str,
    entity: Dict[str, Any],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Phase 2: CSE resolution search + find_company_website → WEBSITE_FOUND | NO_WEBSITE."""
    cfg = INFLOW_CONFIG["resolve"]
    log = logger
    log.set_debug_flag(debug)
    site = (entity.get("company_website") or "").strip()
    if site:
        if debug:
            log.debug_index(
                func="roster.resolve_company_website",
                index=1,
                total=1,
                identifier=short_name,
                outcome="skipped — company_website already set",
            )
            log.debug_detail(f"company_website={site!r}")
        return {"success": True, "state": "WEBSITE_FOUND", "error": None}
    name = (entity.get("company_name") or short_name or "").strip()
    query = f"{name} official website"
    try:
        hits = search_google_cse(
            query=query,
            max_results=int(cfg["max_results"]),
            site_filters=None,
            days=cfg["date_restrict_days"],
        )
    except (RuntimeError, ValueError) as exc:
        if debug:
            log.debug_index(
                func="roster.resolve_company_website",
                index=1,
                total=1,
                identifier=short_name,
                outcome=f"CSE failed: {exc!s}",
            )
            log.debug_detail(f"query={query!r}")
        logger.warning("[%s] resolve_company_website: CSE failed: %s", short_name, exc)
        return {"success": False, "state": None, "error": str(exc)}
    if debug:
        log.debug_index(
            func="roster.resolve_company_website",
            index=1,
            total=1,
            identifier=short_name,
            outcome=f"{len(hits)} CSE hit(s)",
        )
        log.debug_detail(f"query={query!r} raw_hits={len(hits)}")
        for hi, hit in enumerate(hits):
            if hi >= 20:  # UAT cap — same as discovery
                log.debug_detail(f"... {len(hits) - 20} more hits omitted from log")
                break
            log.debug_detail(
                f"hit title={hit.get('title', '')!r} url={hit.get('url', '')!r}"
            )
    if not hits:
        if debug:
            log.debug_index(
                func="roster.resolve_company_website",
                index=1,
                total=1,
                identifier=short_name,
                outcome="NO_WEBSITE — zero CSE hits",
            )
            log.debug_detail(f"query={query!r}")
        transition_company_state(short_name, "NO_WEBSITE")
        return {"success": True, "state": "NO_WEBSITE", "error": None}
    # find_company_website: row 0 = company slug; hit rows 1..N (1-based index in live_content).
    lines = [f"0|{short_name}|"]
    for i, hit in enumerate(hits):
        snip = (hit.get("snippet") or "")[:500]
        lines.append(f"{i + 1}|{hit.get('title', '')}|{hit.get('url', '')}|{snip}")
    live_content = "\n".join(lines)
    if debug:
        log.debug_index(
            func="roster.resolve_company_website",
            index=1,
            total=1,
            identifier=short_name,
            outcome=f"vet {cfg['ai_task_key']} {len(hits)} hit(s)",
        )
        log.debug_detail_block(live_content)
    api_result = await do_task(
        task_key=cfg["ai_task_key"],
        live_content=live_content,
        index=short_name,
        ctx=ctx,
        debug=debug,
    )
    if not api_result.get("success"):
        if debug:
            log.debug_index(
                func="roster.resolve_company_website",
                index=1,
                total=1,
                identifier=short_name,
                outcome="find_company_website task failed",
            )
            log.debug_detail(f"error={api_result.get('error')!r}")
        return {"success": False, "state": None, "error": api_result.get("error") or "task failed"}
    parsed = api_result.get("parsed_response") or {}
    website = (parsed.get("website") or "").strip()
    if not parsed.get("task_success") or not website:
        if debug:
            log.debug_index(
                func="roster.resolve_company_website",
                index=1,
                total=1,
                identifier=short_name,
                outcome="NO_WEBSITE — task_success false or empty website",
            )
            log.debug_detail(
                f"task_success={parsed.get('task_success')!r} website={website!r}"
            )
        transition_company_state(short_name, "NO_WEBSITE")
        return {"success": True, "state": "NO_WEBSITE", "error": None}
    update_company(short_name, company_website=website)
    transition_company_state(short_name, "WEBSITE_FOUND")
    if debug:
        log.debug_index(
            func="roster.resolve_company_website",
            index=1,
            total=1,
            identifier=short_name,
            outcome=f"recorded WEBSITE_FOUND website={website!r}",
        )
    return {"success": True, "state": "WEBSITE_FOUND", "error": None}


async def run_inflow_discovery_batch(
    candidate: Dict[str, Any],
    batch_id: str,
    ctx: Optional[Dict[str, Any]],
    debug: bool,
) -> Dict[str, Any]:
    """Phase 1: CSE per stale table term, vet hits, ingest accepted slugs (AST-525)."""
    zero = {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}
    candidate_id = (candidate.get("astral_candidate_id") or candidate.get("candidate_id") or "").strip()
    cfg = INFLOW_CONFIG["discovery"]
    log = logger
    log.set_debug_flag(debug)
    scan_h = float(cfg["scan_interval_hours"])
    terms = list_stale_company_search_terms(candidate_id, scan_h)
    term_total = len(terms)
    if not terms:
        if debug:
            log.debug_index(
                func="roster.run_inflow_discovery_batch",
                index=1,
                total=1,
                identifier=candidate_id,
                outcome="no stale search terms",
            )
        logger.warning("run_inflow_discovery_batch: no stale search terms for %s", candidate_id)
        return {**zero, "total_errors": 0}
    all_hits: List[GoogleCseHit] = []
    seen_urls: Set[str] = set()
    errors = 0
    for term_i, term in enumerate(terms, start=1):
        try:
            hits = search_google_cse(
                query=term,
                max_results=int(cfg["max_results_per_query"]),
                site_filters=None,
                days=int(cfg["date_restrict_days"]),
            )
        except (RuntimeError, ValueError) as exc:
            if debug:
                log.debug_index(
                    func="roster.run_inflow_discovery_batch",
                    index=term_i,
                    total=term_total,
                    identifier=term,
                    outcome=f"CSE failed: {exc!s}",
                )
            logger.warning("run_inflow_discovery_batch: CSE failed for term %r: %s", term, exc)
            errors += 1
            continue
        if debug:
            log.debug_index(
                func="roster.run_inflow_discovery_batch",
                index=term_i,
                total=term_total,
                identifier=term,
                outcome=f"{len(hits)} hit(s)",
            )
            log.debug_detail(f"search_term={term!r} raw_hits={len(hits)}")
            for hi, hit in enumerate(hits):
                if hi >= 20:  # UAT cap per term
                    log.debug_detail(f"... {len(hits) - 20} more hits omitted from log")
                    break
                log.debug_detail(
                    f"hit title={hit.get('title', '')!r} url={hit.get('url', '')!r}"
                )
        update_company_search_term_last_scan_at(candidate_id, term)
        if debug:
            log.debug_detail("last_scan_at bumped")
        for hit in hits:
            norm = _normalize_company_url_for_dedupe(hit.get("url") or "")
            if not norm or norm in seen_urls:
                continue
            seen_urls.add(norm)
            all_hits.append(hit)
    if not all_hits:
        if debug:
            log.debug_index(
                func="roster.run_inflow_discovery_batch",
                index=1,
                total=1,
                identifier=candidate_id,
                outcome="no deduped hits after CSE — vet skipped",
            )
            log.debug_detail(
                f"terms_searched={term_total} errors={errors} deduped_hits=0"
            )
        return {**zero, "total_errors": errors}
    lines = ["Discovery hits (index|title|url|snippet)"]
    for i, hit in enumerate(all_hits):
        snip = (hit.get("snippet") or "")[:500]
        lines.append(f"{i:03d}|{hit.get('title', '')}|{hit.get('url', '')}|{snip}")
    live_content = "\n".join(lines)
    if debug:
        log.debug_index(
            func="roster.run_inflow_discovery_batch",
            index=1,
            total=1,
            identifier=candidate_id,
            outcome=f"vet {cfg['vet_task_key']} {len(all_hits)} deduped hit(s)",
        )
        log.debug_detail_block(live_content)
    task_ctx = ctx or candidate
    api_result = await do_task(
        task_key=cfg["vet_task_key"],
        live_content=live_content,
        index=candidate_id,
        ctx=task_ctx,
        debug=debug,
    )
    if not api_result.get("success"):
        if debug:
            log.debug_index(
                func="roster.run_inflow_discovery_batch",
                index=1,
                total=1,
                identifier=candidate_id,
                outcome="vet task failed",
            )
        logger.error("run_inflow_discovery_batch: vet task failed for %s", candidate_id)
        return {**zero, "total_errors": max(1, errors + 1)}
    parsed = api_result.get("parsed_response") or {}
    rows = parsed.get("results")
    if not isinstance(rows, list):
        if debug:
            log.debug_detail("vet parsed_response missing results list")
        return {**zero, "total_errors": max(1, errors + 1)}
    ingested = 0
    skipped = 0
    dict_rows = [r for r in rows if isinstance(r, dict)]
    row_total = len(dict_rows)
    row_i = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        row_i += 1
        fail_reason = None
        action = (row.get("action") or "").strip().lower()
        slug = (row.get("short_name") or "").strip()
        site = (row.get("website") or "").strip() or None
        hi_raw = row.get("hit_index")
        try:
            hi = int(hi_raw)
            provenance = all_hits[hi] if 0 <= hi < len(all_hits) else None
        except (TypeError, ValueError):
            provenance = None
            hi = hi_raw
        if action == "ignore":
            outcome = "ignored"
        elif action != "slug":
            logger.warning("run_inflow_discovery_batch: unknown action %r", row.get("action"))
            outcome = "skipped unknown action"
        elif not slug:
            outcome = "skipped empty slug"
        else:
            if ingest_new_companies(candidate_id, slug, site, source_hit=provenance):
                outcome = (
                    f"recorded state={'WEBSITE_FOUND' if site else 'NEW'} website={site or ''}"
                )
            else:
                fail_reason = _ingest_failure_reason(candidate_id, slug, site)
                outcome = (
                    f"not recorded — {fail_reason}"
                    if fail_reason
                    else "not recorded (unknown)"
                )
        if debug:
            log.debug_index(
                func="roster.run_inflow_discovery_batch",
                index=row_i,
                total=row_total,
                identifier=slug or f"hit_index={hi}",
                outcome=outcome,
            )
            if fail_reason:
                log.debug_detail(f"ingest failed: {fail_reason}")
            log.debug_detail(
                f"action={action!r} hit_index={row.get('hit_index')!r} website={site!r}"
            )
        if action == "ignore":
            skipped += 1
            continue
        if action != "slug":
            skipped += 1
            continue
        if not slug:
            skipped += 1
            continue
        if outcome.startswith("recorded"):
            ingested += 1
        else:
            skipped += 1
    if debug:
        log.debug_detail(
            f"batch summary total_processed=1 total_passed={ingested} "
            f"total_failed={skipped} total_errors={errors} terms={term_total} "
            f"deduped_hits={len(all_hits)}"
        )
    return {
        "total_processed": 1,
        "total_passed": ingested,
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
        if input_state == "NEW":
            r = await resolve_company_website(short_name, entity, ctx=ctx, debug=debug)
            if r.get("error"):
                return {**zero, "total_errors": 1}
            if r.get("state") in ("WEBSITE_FOUND", "NO_WEBSITE"):
                return {**zero, "total_passed": 1}
            return {**zero, "total_failed": 1}

        elif input_state in ("WEBSITE_FOUND", "WEBSITE_FOUND_RETRY"):
            tk = (dispatch_task_key or "").strip()
            logger.warning(
                "run_company_task: monolithic WEBSITE_FOUND dispatch removed for %s "
                "(dispatch_task_key=%r; use fetch_website or HOMEPAGE_READY prefilter batch)",
                short_name, tk or None,
            )
            return {**zero, "total_errors": 1}

        elif input_state == "NO_OPENINGS":
            r = await process_recheck_no_openings(entity, batch_id, ctx=ctx, debug=debug)
            if not r.get("success"):
                logger.error("[%s] recheck_no_openings failed (state unchanged): %s", short_name, r.get("message", ""))
                return {**zero, "total_errors": 1}
            logger.info(
                "[%s] recheck_no_openings ok: %s (state=%s)",
                short_name,
                r.get("message", ""),
                r.get("new_state", ""),
            )
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
                logger.error(f"[{short_name}] jobs_found_process_job_site error: {result['error']}")
                if error_state:  # pragma: no branch
                    transition_company_state(short_name, error_state)
                return {**zero, "total_errors": 1}
            pass_states = ROSTER_CONFIG.get("locate_job_page", {}).get("pass_states", [])
            if result.get("state") in pass_states:  # pragma: no branch
                return {**zero, "total_passed": 1}
            return {**zero, "total_failed": 1}

        elif input_state in frozenset(
            ROSTER_CONFIG.get("locate_job_page", {}).get("dispatch_input_states") or ("TO_WATCH",)
        ):
            locate_states = frozenset(
                ROSTER_CONFIG.get("locate_job_page", {}).get("dispatch_input_states") or ("TO_WATCH",)
            )
            tk = (dispatch_task_key or "").strip()
            if not tk and input_state in locate_states:
                tk = "find_job_page"
            error_state = ROSTER_CONFIG.get("locate_job_page", {}).get("error_state")
            pass_states = ROSTER_CONFIG.get("locate_job_page", {}).get("pass_states", [])
            if tk == "find_job_page":
                result = await find_job_page(
                    url=company_website, short_name=short_name,
                    company_website=company_website, debug=debug, ctx=ctx,
                )
            elif tk == "select_job_page":
                result = await run_select_job_page_dispatch(entity, batch_id, ctx, debug)
            elif tk == "parse_job_list":
                result = await run_parse_job_list_dispatch(entity, batch_id, ctx, debug)
            else:
                logger.warning(
                    "run_company_task: unhandled dispatch_task_key=%s for input_state=%s %s",
                    tk, input_state, short_name,
                )
                return {**zero, "total_errors": 1}
            if result.get("error"):
                logger.error(f"[{short_name}] {tk} error: {result['error']}")
                if error_state:
                    transition_company_state(short_name, error_state)
                return {**zero, "total_errors": 1}
            if result.get("state") in pass_states:
                return {**zero, "total_passed": 1}
            return {**zero, "total_failed": 1}

        elif input_state == "WATCH":
            from src.core.gazer import process_gazer_batch  # lazy import avoids circular
            error_state = ROSTER_CONFIG.get("gaze", {}).get("error_state")
            outcomes = await process_gazer_batch(batch_id, [entity], debug=debug, ctx=ctx)
            o = outcomes[0] if outcomes else {}
            if o.get("status") == "failure":
                logger.error(f"[{short_name}] {o.get('message', '')}")
                if error_state:
                    transition_company_state(short_name, error_state)
                return {**zero, "total_errors": 1}
            logger.info(f"[{short_name}] {o.get('message', '')}")
            return {**zero, "total_passed": 1}

        else:
            logger.warning("run_company_task: unhandled input_state=%s for %s", input_state, short_name)
            return {**zero, "total_errors": 1}

    except Exception as e:
        logger.exception(f"[{short_name}] run_company_task exception: {e}")
        return {**zero, "total_errors": 1}


async def run_select_job_page_dispatch(
    entity: Dict[str, Any],
    batch_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """TO_WATCH entry: select_job_page only — no run_next parse chain (AST-535)."""
    short_name = entity.get("short_name", "")
    company_website = entity.get("company_website", "")
    company = get_company(short_name)
    cdata = (company.get("company_data") or {}) if company else {}
    possible_job_links = cdata.get("possible_job_links") or []
    nav_links = cdata.get("nav_links") or ""
    if not possible_job_links or not nav_links:
        _save_company(short_name=short_name, company_website=company_website,
                      state="NO_JOBLIST", page_option_url=company_website,
                      raw_response={"response_type": "NO_JOBLIST_FOUND", "reason": "No possible_job_links from prefilter"})
        return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": "NO_JOBLIST_FOUND"}
    ctx_no_chain = {k: v for k, v in (ctx or {}).items() if k != "resolve_run_next_live"}
    async with create_browser_context() as browser_context:
        assembled_content, page_url_map, page_dom_map, visible_map = await _fetch_job_links_content(
            possible_job_links, nav_links, browser_context, debug=debug,
        )
        if not assembled_content.strip():
            _save_company(short_name=short_name, company_website=company_website,
                          state="NO_JOBLIST", page_option_url=company_website,
                          raw_response={"response_type": "NO_JOBLIST_FOUND", "reason": "All PJL scrapes failed"})
            return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": "NO_JOBLIST_FOUND"}
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
            ctx=ctx_no_chain,
            chain_parse=False,
        )


async def _scrape_job_site_dom(job_site: str, browser_context: BrowserSession, debug: bool = False) -> str:
    """Load job_site once and return culled page DOM for parse_job_list dispatch entry."""
    pg = await get_page(browser_context, job_site)
    try:
        return (await extract_page_dom(pg)) or ""
    finally:
        await close_page(pg)


async def run_parse_job_list_dispatch(
    entity: Dict[str, Any],
    batch_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """TO_WATCH entry: parse_job_list on stored job_site (AST-535)."""
    short_name = entity.get("short_name", "")
    company_website = entity.get("company_website", "")
    job_site = str(entity.get("job_site") or "").strip()
    if not job_site:
        logger.warning("run_parse_job_list_dispatch: missing job_site for %s", short_name)
        return {"short_name": short_name, "state": "NO_JOBLIST", "error": "missing job_site"}
    company = get_company(short_name)
    cdata = (company.get("company_data") or {}) if company else {}
    job_titles = cdata.get("job_titles") or []
    async with create_browser_context() as browser_context:
        dom_html = await _scrape_job_site_dom(job_site, browser_context, debug=debug)
        if not dom_html.strip():
            _save_company(short_name=short_name, company_website=company_website,
                          state="NO_JOBLIST", page_option_url=company_website,
                          raw_response={"response_type": "PARSE_DISPATCH_EMPTY_DOM", "job_site": job_site})
            return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": job_site, "response_type": "PARSE_DISPATCH_EMPTY_DOM"}
        containers = find_job_containers(dom_html, job_titles)
        if not containers:
            _save_company(short_name=short_name, company_website=company_website,
                          state="CANNOT_PARSE_JOB_SITE", page_option_url=job_site,
                          raw_response={"response_type": "PARSE_DISPATCH_NO_CONTAINERS"})
            return {"short_name": short_name, "state": "CANNOT_PARSE_JOB_SITE", "job_site": job_site, "response_type": "PARSE_DISPATCH_NO_CONTAINERS"}
        dom_joined = "\n".join(containers)
        parsed = await _fetch_parse_job_list(dom_joined, short_name, debug=debug, ctx=ctx)
        container = (parsed.get("job_container") or "").strip()
        job_tag = (parsed.get("job_tag") or "").strip()
        if not container or not job_tag:
            save_company_data(short_name, {"parse_job_list_notes": "parse returned empty container or job_tag"})
            _save_company(short_name=short_name, company_website=company_website,
                          state="CANNOT_PARSE_JOB_SITE", page_option_url=job_site, raw_response=parsed)
            return {"short_name": short_name, "state": "CANNOT_PARSE_JOB_SITE", "job_site": job_site, "response_type": "PARSE_DISPATCH_INVALID"}
        err, _, _ = _validate_parse_job_list_raw_job_listings(dom_joined, container, job_tag, parsed.get("job_ids", []))
        if err:
            save_company_data(short_name, {"parse_job_list_notes": err})
            _save_company(short_name=short_name, company_website=company_website,
                          state="CANNOT_PARSE_JOB_SITE", page_option_url=job_site, raw_response=parsed)
            return {"short_name": short_name, "state": "CANNOT_PARSE_JOB_SITE", "job_site": job_site, "response_type": "PARSE_DISPATCH_VALIDATION"}
        container_index = _compute_container_index(dom_html, container, job_titles)
        parse_instructions = {"container": container, "job_tag": job_tag, "container_index": container_index}
        save_company_data(short_name, {"parse_instructions": parse_instructions})
        _save_company(short_name=short_name, company_website=company_website,
                      state="WATCH", page_option_url=job_site, raw_response=parsed)
        return {"short_name": short_name, "state": "WATCH", "job_site": job_site, "response_type": "PARSE_DISPATCH_OK", "parse_instructions": parse_instructions}


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
        logger.warning("[%s] recheck_no_openings: playwright failed (state unchanged): %s", short_name, ex)
        return {"success": False, "message": f"playwright scrape: {ex}", "new_state": ""}

    if final_url and final_url != job_site:
        logger.info("[%s] recheck_no_openings: job_site redirect %s -> %s", short_name, job_site, final_url)
        update_company(short_name, job_site=final_url)
        job_site = final_url

    text_blob = visible_text or ""
    if no_jobs_message in text_blob:
        update_company_last_scan_at(short_name)
        logger.info(
            "[%s] recheck_no_openings: no_jobs_message still on page; staying NO_OPENINGS (job_site=%s)",
            short_name,
            job_site,
        )
        return {"success": True, "message": "no_jobs_message_present", "new_state": "NO_OPENINGS"}

    logger.info(
        "[%s] recheck_no_openings: no_jobs_message absent from visible text; transitioning NO_OPENINGS -> JOBS_FOUND (job_site=%s)",
        short_name,
        job_site,
    )
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
    )
    companies = get_company_batch(bid)
    return (bid, companies)

def clear_company_batch(batch_id: str) -> int:
    """Release batch. Returns count cleared."""
    return set_company_batch(batch_id, clear=True)


# ---- Prefilter ----

def _vector_labels_from_ctx(ctx: Optional[Dict[str, Any]]) -> Dict[str, str]:
    from src.core.consult import _rubric_criteria_from_cd

    cd = (ctx or {}).get("candidate_data") or {}
    criteria = _rubric_criteria_from_cd(cd, "company_prefilter")
    return {item["code"]: item["label"] for item in criteria if item.get("code") and item.get("label")}


def _flatten_prefilter_parsed(parsed: Any) -> Dict[str, Any]:
    if isinstance(parsed, dict) and isinstance(parsed.get("jobs"), list) and parsed["jobs"]:
        first = parsed["jobs"][0]
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
    """Route retryable prefilter failures to WEBSITE_FOUND_RETRY; hard errors to ERROR_PREFILTER."""
    retryable = api_result is None or (
        not api_result.get("success") and _prefilter_api_failure_is_retryable(api_result)
    )
    dest = cfg["retry_state"] if retryable else cfg["error_state"]
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


async def scrape_company_homepage_content(
    short_name: str,
    company_website: str,
    *,
    browser_context=None,
) -> Dict[str, Any]:
    """Scrape homepage visible text and nav_links without agent evaluation (AST-701 fetch_website)."""
    out: Dict[str, Any] = {
        "company_website": company_website,
        "visible_text": "",
        "enumerated_nav_links": "",
        "error": None,
    }
    try:
        visible_text, final_url = await get_visible_text(
            company_website, context=browser_context, return_final_url=True
        )
    except Exception as scrape_err:
        out["error"] = str(scrape_err)
        return out
    if final_url and final_url != company_website:
        update_company(short_name, company_website=final_url)
        company_website = final_url
        out["company_website"] = company_website
    visible_text = collapse_consecutive_blank_lines(visible_text or "")
    out["visible_text"] = visible_text
    if not out["visible_text"].strip():
        out["error"] = "No visible text extracted"
        return out
    try:
        url_list = await extract_site_page_list(
            company_website, max_depth=1, verify=False, context=browser_context
        )
        if url_list:
            out["enumerated_nav_links"] = enumerate_array("", url_list)
    except Exception as nav_err:
        logger.warning(f"[{short_name}] nav_links extraction failed (non-fatal): {nav_err}")
    return out


def _apply_prefilter_decoded_company_outcome(
    short_name: str,
    flat: Dict[str, Any],
    cfg: Dict[str, Any],
    ctx: Optional[Dict[str, Any]],
    *,
    nav_links_from_data: str = "",
) -> str:
    """Shared post-decode prefilter outcome: hydrate, verdict, persist, transition."""
    from src.core.consult import (
        _render_pass_fail,
        _render_score,
        _rubric_criteria_from_cd,
        _hydrate_grade_reasons_from_rubric,
    )

    grades = flat.get("grades") or []
    rubric_list = _rubric_criteria_from_cd((ctx or {}).get("candidate_data") or {}, "company_prefilter")
    if grades and rubric_list:
        _hydrate_grade_reasons_from_rubric(grades, rubric_list)
    verdict_state = _render_pass_fail("prefilter_company", grades)
    if _company_used_inflow_prefilter(short_name):
        new_state = verdict_state
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
        "prefilter_company_notes": notes,
    }
    if verdict_state == cfg["pass_state"] and rubric_list:
        task_cfg = TASK_CONFIG.get("prefilter_company") or {}
        _, score = _render_score(task_cfg, rubric_list, grades, 0.0)
        data_to_save["prefilter_score"] = float(score)
    if nav_links_from_data:
        data_to_save["nav_links"] = nav_links_from_data
    data_to_save["possible_job_links"] = flat.get("possible_job_links") or []
    if decision == "TO_WATCH" or new_state == "PREFILTER_PASSED":
        data_to_save["culture_links_to_explore"] = flat.get("culture_links_to_explore") or []
    save_company_data(short_name, data_to_save)
    transition_company_state(short_name, new_state)
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
            "batch_entities": [{"astral_job_id": short_name}],
            "batch_size": 1,
            "vector_labels": _vector_labels_from_ctx(ctx),
        }
        api_result = await do_task(
            task_key="prefilter_company",
            live_content=live_content,
            index=short_name,
            ctx=task_ctx,
            debug=debug,
        )

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


def _transition_prefilter_batch_failures(companies: List[Dict[str, Any]], cfg: Dict[str, Any]) -> None:
    by_dest: Dict[str, List[str]] = {}
    for company in companies:
        short_name = company.get("short_name")
        if not short_name:
            continue
        dest = _prefilter_batch_fail_dest(company.get("state"), cfg)
        if dest:
            by_dest.setdefault(dest, []).append(short_name)
    for dest, names in by_dest.items():
        for short_name in names:
            transition_company_state(short_name, dest)


async def _run_batch_company_prefilter(
    batch_id: str,
    companies: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    """Pattern-A company prefilter batch: one do_task, position-indexed decode, shared outcome helper."""
    from src.core import tracker
    from src.core.consult import _hydrate_response_jobs_grade_reasons, _rubric_criteria_from_cd

    agent_task_key = "prefilter_company"
    cfg = ROSTER_CONFIG["prefilter"]
    pass_states = cfg.get("pass_states") or []
    normalized: List[Dict[str, Any]] = []
    for company in companies:
        short_name = company["short_name"]
        normalized.append({
            "astral_job_id": short_name,
            "short_name": short_name,
            "state": company.get("state"),
            "company_data": company.get("company_data") or {},
        })
    companies = normalized
    input_by_id = {c["short_name"]: c for c in companies}
    short_names = [c["short_name"] for c in companies]

    if debug:
        logger.set_debug_flag(True)
        logger.debug_index(
            func="roster._run_batch_company_prefilter",
            index=1,
            total=1,
            identifier=batch_id,
            outcome=f"batch start n={len(companies)}",
        )
        logger.debug_detail(
            f"batch_id={batch_id} batch_chunk_index={batch_chunk_index!r} short_names={short_names}"
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

    rubric_list = _rubric_criteria_from_cd((ctx or {}).get("candidate_data") or {}, "company_prefilter")
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
    result = await do_task(
        task_key=agent_task_key,
        live_content=assemble(companies),
        index=do_index,
        ctx=task_ctx,
        debug=debug,
    )

    if not result.get("success"):
        if debug:
            logger.debug_index(
                func="roster._run_batch_company_prefilter",
                index=1,
                total=1,
                identifier=batch_id,
                outcome="do_task failed — batch error transition",
            )
            logger.debug_detail(f"error={result.get('error')!r}")
        _transition_prefilter_batch_failures(companies, cfg)
        return {"passed": 0, "failed": 0, "total": len(companies)}

    parsed = result.get("parsed_response") or {}
    response_jobs = parsed.get("jobs") or []
    try:
        _hydrate_response_jobs_grade_reasons(response_jobs, rubric_list)
    except ValueError as hydrate_err:
        logger.error("[prefilter_company_batch] grade reason hydration failed: %s", hydrate_err)
        _transition_prefilter_batch_failures(companies, cfg)
        return {"passed": 0, "failed": 0, "total": len(companies)}

    sent_ids = set(input_by_id.keys())
    received_ids = {rj["astral_job_id"] for rj in response_jobs}
    missing = sent_ids - received_ids
    fabricated = received_ids - sent_ids
    missing_rows = [input_by_id[mid] for mid in missing if mid in input_by_id]

    if missing:
        logger.warning(
            "[prefilter_company_batch] batch incomplete: %d/%d IDs omitted: %s",
            len(missing), len(sent_ids), sorted(missing),
        )
        _transition_prefilter_batch_failures(missing_rows, cfg)

    passed = failed = 0
    bad_grades: Set[str] = set()

    for job_idx, response_job in enumerate(response_jobs, start=1):
        aid = response_job["astral_job_id"]
        if aid in fabricated:
            continue
        input_company = input_by_id[aid]
        nav_links = (input_company.get("company_data") or {}).get("nav_links") or ""
        try:
            new_state = _apply_prefilter_decoded_company_outcome(
                aid,
                response_job,
                cfg,
                ctx,
                nav_links_from_data=nav_links,
            )
        except Exception as e:
            bad_grades.add(aid)
            if debug:
                logger.debug_index(
                    func="roster._run_batch_company_prefilter",
                    index=job_idx,
                    total=len(response_jobs),
                    identifier=aid,
                    outcome="process failed",
                )
                logger.debug_detail(f"short_name={aid} error={e!r} grades={response_job.get('grades')!r}")
            logger.warning("[%s] prefilter batch process failed: %s | grades: %s", aid, e, response_job.get("grades"))
            continue
        if debug:
            grades = response_job.get("grades") or []
            links_count = len(response_job.get("possible_job_links") or []) + len(
                response_job.get("culture_links_to_explore") or []
            )
            logger.debug_index(
                func="roster.prefilter_company_batch",
                index=job_idx,
                total=len(response_jobs),
                identifier=aid,
                outcome=str(new_state),
            )
            logger.debug_detail(
                f"short_name={aid} grades={len(grades)} links={links_count} state={new_state!r}"
            )
        if new_state in pass_states:
            passed += 1
        else:
            failed += 1

    if bad_grades:
        bad_rows = [input_by_id[aid] for aid in bad_grades if aid in input_by_id]
        _transition_prefilter_batch_failures(bad_rows, cfg)

    agent_ref = result.get("agent_ref")
    if agent_ref:
        entity_type = TASK_CONFIG.get(agent_task_key, {}).get("entity_type", "company")
        processed_ids = received_ids - fabricated - bad_grades
        for aid in processed_ids:
            try:
                tracker.append_agent_response(entity_type, aid, agent_ref)
            except Exception:
                logger.debug("append_agent_response failed for %s", aid, exc_info=True)

    if debug and missing:
        for mi, mid in enumerate(sorted(missing), start=1):
            row = input_by_id.get(mid)
            dest = _prefilter_batch_fail_dest(row.get("state") if row else None, cfg)
            logger.debug_index(
                func="roster._run_batch_company_prefilter",
                index=mi,
                total=len(missing),
                identifier=mid,
                outcome=f"missing from response -> {dest or '?'}",
            )

    return {"passed": passed, "failed": failed, "total": len(companies)}


async def prefilter_company_batch(
    batch_id: str,
    companies: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Batch company prefilter from HOMEPAGE_READY rows (AST-702)."""
    ready: List[Dict[str, Any]] = []
    not_ready: List[Dict[str, Any]] = []
    for company in companies:
        if _company_homepage_ready(company):
            ready.append(company)
        else:
            not_ready.append(company)

    if debug:
        logger.set_debug_flag(True)
        logger.debug_detail(
            f"prefilter_company_batch batch_id={batch_id} ready={len(ready)} not_ready={len(not_ready)}"
        )

    for ni, company in enumerate(not_ready, start=1):
        short_name = company["short_name"]
        transition_company_state(short_name, "CANNOT_READ_WEBSITE")
        save_company_data(short_name, {"prefilter_company_notes": "No homepage_text in company_data"})
        if debug:
            logger.debug_index(
                func="roster.prefilter_company_batch",
                index=ni,
                total=len(not_ready),
                identifier=short_name,
                outcome="readiness skip -> CANNOT_READ_WEBSITE",
            )

    if not ready:
        return {
            "passed": 0,
            "failed": 0,
            "total": len(companies),
            "skipped": len(not_ready),
        }

    batch_result = await _run_batch_company_prefilter(batch_id, ready, ctx=ctx, debug=debug)
    batch_result["total"] = len(companies)
    if not_ready:
        batch_result["skipped"] = len(not_ready)
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
    browser_context: BrowserSession,
    debug: bool,
    ctx: Optional[Dict[str, Any]],
    chain_parse: bool = True,
) -> Dict[str, Any]:
    """AST-469: shared select_job_page + optional TRY_LINK retry + run_next parse chain.
    chain_parse=False: select-only dispatch entry (AST-535) — no run_next parse resolver."""

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
        res = await do_task(
            "select_job_page",
            live_content=live_sel,
            index=short_name,
            ctx=merged_ctx,
            debug=debug,
        )
        if not res.get("success"):  # pragma: no branch
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

        if debug:
            logger.test(f"[find_job_page] select_job_page response_type={response_type}")

        if response_type != "TRY_LINKS":
            break

        try_links = parsed_top.get("try_links") or []
        if not try_links or not try_link_retry_pending:
            _save_company(short_name=short_name, company_website=company_website,
                               state="NO_JOBLIST", page_option_url=company_website, raw_response=parsed_top)
            return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": response_type}

        if debug:
            logger.test(f"[find_job_page] TRY_LINKS: scraping {len(try_links)} suggested URLs")
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
        debug=debug, ctx=ctx,
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
        logger.warning("[%s] jobs_found: initial scrape failed: %s", short_name, ex)
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


def _is_verified_job_site_distinct(job_site: str, company_website: str) -> bool:
    """True when stored job_site is non-empty and not the same URL as company_website (Susan AC)."""
    js = _normalize_company_url_for_dedupe(job_site)
    cw = _normalize_company_url_for_dedupe(company_website)
    return bool(js) and js != cw


async def find_job_page(
    url: str,
    short_name: Optional[str] = None,
    company_website: Optional[str] = None,
    debug: bool = False,
    ctx: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    """Find job listing page on a company website.

    Loads possible_job_links from prefilter, scrapes those pages,
    calls select_job_page AI to confirm which page has jobs (with one TRY_LINKS
    retry), then saves job_site + job_titles for downstream parse_job_list.

    Returns dict with: short_name, state, job_site, response_type.
    """
    if debug:
        logger.set_debug_flag(True)
        # Stdlib only: quiet third-party HTTP/SDK chatter (not app loggers; cf. anthropic.py).
        import logging as _stdlib_log

        _stdlib_log.getLogger("httpcore").setLevel(_stdlib_log.WARNING)
        _stdlib_log.getLogger("httpx").setLevel(_stdlib_log.WARNING)
        _stdlib_log.getLogger("anthropic").setLevel(_stdlib_log.WARNING)

    if not short_name:
        short_name = _derive_shortname_from_url(url)
    if not company_website:
        company_website = url

    # Load company data for possible_job_links + nav_links
    company = get_company(short_name)
    pre_job_site = str((company or {}).get("job_site") or "").strip()
    if _is_verified_job_site_distinct(pre_job_site, company_website):
        logger.info(
            "[%s] find_job_page: stored job_site path (%s)",
            short_name,
            pre_job_site,
        )
        return await jobs_found_process_job_site(
            short_name, company_website, pre_job_site, debug=debug, ctx=ctx,
        )
    cdata = (company.get("company_data") or {}) if company else {}
    possible_job_links = cdata.get("possible_job_links") or []
    nav_links = cdata.get("nav_links") or ""

    if debug:
        logger.test(f"[find_job_page] {short_name}: {len(possible_job_links)} PJLs, nav_links={len(nav_links)} chars")

    async with create_browser_context() as browser_context:
        if not possible_job_links or not nav_links:
            logger.info(
                "[%s] find_job_page: NO_JOBLIST without LLM — reason=no_pjl_or_nav "
                "pjl_count=%d nav_links_chars=%d verified_job_site=%s",
                short_name,
                len(possible_job_links),
                len(nav_links or ""),
                "yes" if _is_verified_job_site_distinct(pre_job_site, company_website) else "no",
            )
            _save_company(short_name=short_name, company_website=company_website,
                               state="NO_JOBLIST", page_option_url=company_website,
                               raw_response={"response_type": "NO_JOBLIST_FOUND", "reason": "No possible_job_links from prefilter"})
            pre_js = str((company or {}).get("job_site") or "")
            job_site_out = _job_site_for_persist(
                terminal_state="NO_JOBLIST", page_option_url=company_website, pre_run_job_site=pre_js,
            )
            return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": job_site_out, "response_type": "NO_JOBLIST_FOUND"}

        # Scrape PJL pages (text + DOM + visible + links in one page load each)
        assembled_content, page_url_map, page_dom_map, visible_map = await _fetch_job_links_content(
            possible_job_links, nav_links, browser_context, debug=debug,
        )
        if not assembled_content.strip():
            logger.info(
                "[%s] find_job_page: NO_JOBLIST without LLM — reason=all_pjl_scrapes_failed "
                "pjl_count=%d nav_links_chars=%d verified_job_site=%s",
                short_name,
                len(possible_job_links),
                len(nav_links or ""),
                "yes" if _is_verified_job_site_distinct(pre_job_site, company_website) else "no",
            )
            _save_company(short_name=short_name, company_website=company_website,
                               state="NO_JOBLIST", page_option_url=company_website,
                               raw_response={"response_type": "NO_JOBLIST_FOUND", "reason": "All PJL scrapes failed"})
            pre_js = str((company or {}).get("job_site") or "")
            job_site_out = _job_site_for_persist(
                terminal_state="NO_JOBLIST", page_option_url=company_website, pre_run_job_site=pre_js,
            )
            return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": job_site_out, "response_type": "NO_JOBLIST_FOUND"}

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
    url_map = parse_enumerate_array(nav_links)
    nav_url_set = set(url_map.values())

    sections: List[str] = []
    page_url_map: Dict[int, str] = {}
    page_dom_map: Dict[int, str] = {}
    page_visible_map: Dict[int, str] = {}

    for page_num, link_id in enumerate(possible_job_links, 1):
        try:
            url = url_map.get(int(link_id))
        except (ValueError, TypeError):
            url = str(link_id) if str(link_id).startswith("http") else None
        if not url:
            if debug:
                logger.test(f"  PJL #{page_num}: link_id={link_id} not found in nav_links, skipping")
            continue
        page_url_map[page_num] = url
        try:
            # Single page load — extract text, DOM, and links from the same navigation
            pg = await get_page(browser_context, url)
            try:
                readiness_cfg = roster_scrape_readiness_config()
                ready_meta = await wait_for_careers_list_readiness(pg, readiness_cfg)
                if debug:
                    log = logger
                    log.set_debug_flag(True)
                    total_pages = len(possible_job_links)
                    log.debug_index(
                        func="roster._fetch_job_links_content.scrape_readiness",
                        index=page_num,
                        total=total_pages,
                        identifier=url,
                        outcome=ready_meta.get("outcome")
                        or ("ready" if ready_meta.get("ready") else "timeout"),
                    )
                    log.debug_detail(
                        f"ready={ready_meta.get('ready')} visible_chars={ready_meta.get('visible_chars')} "
                        f"listing_hits={ready_meta.get('listing_hits')} wait_ms={ready_meta.get('wait_ms')} "
                        f"load_all_jobs_ran={ready_meta.get('load_all_jobs_ran')}"
                    )
                    if not ready_meta.get("ready"):
                        log.debug_detail(
                            "readiness gate exhausted — proceeding with best-effort extract "
                            "(AST-692 owns JOBSITE_SCRAPE_ISSUE)"
                        )
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
            if debug:
                logger.test(f"  PJL #{page_num}: {url} — {len(visible_text)} chars, {len(new_links)} new links, dom={len(dom_html or '')} chars")
        except Exception as e:
            sections.append(f"=== PAGE {page_num}: {url} ===\n(scrape failed: {e})")
            if debug:
                logger.test(f"  PJL #{page_num}: {url} — scrape failed: {e}")

    return "\n\n".join(sections), page_url_map, page_dom_map, page_visible_map


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
    job_titles = select_parsed.get("job_titles", [])
    save_company_data(short_name, {"job_titles": job_titles})
    parsed = chain_res.get("parsed_response") or {}
    dom_html = page_dom_map.get(selected_page, "") if selected_page is not None else ""
    if not dom_html:
        _save_company(short_name=short_name, company_website=company_website,
                           state="NO_JOBLIST", page_option_url=company_website, raw_response=select_parsed)
        return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": response_type}

    containers = find_job_containers(dom_html, job_titles)
    if not containers:
        if debug:
            logger.test(f"[find_job_page] DOM did not contain job titles — possible bot block")
        _save_company(short_name=short_name, company_website=company_website,
                           state="CANNOT_PARSE_JOB_SITE", page_option_url=job_site_url, raw_response=select_parsed)
        return {"short_name": short_name, "state": "CANNOT_PARSE_JOB_SITE", "job_site": job_site_url, "response_type": response_type}
    full_dom_html = dom_html
    dom_joined = "\n".join(containers)

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
    job_titles = select_parsed.get("job_titles", [])
    save_company_data(short_name, {"job_titles": job_titles})
    if debug:
        logger.test(f"[find_job_page] JOBLIST_TITLES (no chain): {len(job_titles)} titles, job_site={job_site_url}")

    dom_html = page_dom_map.get(selected_page, "") if selected_page is not None else ""
    if not dom_html:
        _save_company(short_name=short_name, company_website=company_website,
                           state="NO_JOBLIST", page_option_url=company_website, raw_response=select_parsed)
        return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": response_type}

    containers = find_job_containers(dom_html, job_titles)
    if not containers:
        if debug:
            logger.test(f"[find_job_page] DOM did not contain job titles — possible bot block")
        _save_company(short_name=short_name, company_website=company_website,
                           state="CANNOT_PARSE_JOB_SITE", page_option_url=job_site_url, raw_response=select_parsed)
        return {"short_name": short_name, "state": "CANNOT_PARSE_JOB_SITE", "job_site": job_site_url, "response_type": response_type}
    full_dom_html = dom_html
    dom_joined = "\n".join(containers)

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
    response = await do_task(task_key="select_job_page", live_content=assembled_content, index=short_name, ctx=ctx)
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
) -> Dict[str, Any]:
    """Map select_job_page response_type to company state.

    AST-469: JOBLIST_TITLES is finalized in find_job_page (run_next chain); no longer handled here.
    """
    if response_type == "JOBLIST_NO_JOBS":
        no_jobs_msg = result.get("no_jobs_message", "")
        _strip_company_data_keys(short_name, ("job_list_visible",))
        _save_company(short_name=short_name, company_website=company_website,
                           state="NO_OPENINGS", page_option_url=job_site_url,
                           raw_response=result, no_jobs_message=no_jobs_msg)
        if debug:
            logger.test(f"[find_job_page] JOBLIST_NO_JOBS: {no_jobs_msg}")
        return {"short_name": short_name, "state": "NO_OPENINGS", "job_site": job_site_url, "response_type": response_type}

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
        )
        if debug:
            logger.test(
                f"[find_job_page] JOBSITE_SCRAPE_ISSUE: summary={summary!r} job_site={job_site_url}"
            )
        return {
            "short_name": short_name,
            "state": ROSTER_CONFIG["locate_job_page"]["scrape_issue_state"],
            "job_site": job_site_url,
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
    ) -> None:
    """Save company result to database, then transition state.
    
    Data save via update_company + save_company_data; state transition via transition_company_state.
    Builds company_data (no_jobs_message, parse_instructions when applicable).
    
    Args:
        short_name: Company short name
        company_website: Original company website URL
        state: Company state (UPPERCASE from COMPANY_STATES)
        page_option_url: Candidate listings URL from locate path; persisted via _job_site_for_persist
        raw_response: Raw API response for agent_responses blob (includes response_type for audit)
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
        logger.info(f"[{short_name}] fetching nav_links from {company_website}")
        async with create_browser_context() as context:
            url_list = await extract_site_page_list(
                company_website, max_depth=1, verify=False, context=context
            )
        if not url_list:
            return None
        nav_links = enumerate_array("", url_list)
        save_company_data(short_name, {"nav_links": nav_links})
        logger.info(f"[{short_name}] saved {len(url_list)} nav_links")
        return nav_links
    except ValueError:
        raise
    except Exception as e:
        logger.warning(f"[{short_name}] nav_links fetch failed: {e}")
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
        logger.info(f"[{short_name}] fetching prefilter_notes (scrape + AI)")
        visible_text = await get_visible_text(company_website)
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
        except Exception:
            pass

        parts = [f"[company_id={short_name}]", f"\n## Homepage Content\n{visible_text}"]
        if enumerated_nav_links:
            parts.append(f"\n## Navigation Links\n{enumerated_nav_links}")

        task_ctx = {
            "batch_entities": [{"astral_job_id": short_name}],
            "batch_size": 1,
            "vector_labels": _vector_labels_from_ctx(None),
        }
        api_result = await do_task(
            task_key="prefilter_company",
            live_content="\n".join(parts),
            index=short_name,
            ctx=task_ctx,
        )
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
        from src.core.candidate import get_candidate
        from src.core.consult import _hydrate_grade_reasons_from_rubric, _rubric_criteria_from_cd

        company_row = get_company(short_name) or {}
        candidate_id = company_row.get("candidate_id")
        cd: Dict[str, Any] = {}
        if candidate_id:
            cand = get_candidate(candidate_id) or {}
            cd = {"artifacts": cand.get("artifacts") or {}}
        rubric_list = _rubric_criteria_from_cd(cd, "company_prefilter")
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
        culture_links = flat.get("culture_links_to_explore") or []
        if culture_links:
            data_to_save["culture_links_to_explore"] = culture_links
        save_company_data(short_name, data_to_save)
        logger.info(f"[{short_name}] saved prefilter_notes")
        return notes
    except Exception as e:
        logger.warning(f"[{short_name}] prefilter_notes fetch failed: {e}")
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
        logger.info(f"[{short_name}] fetching website_content")

        nav_links = await get_company_data(company, "nav_links")
        if not nav_links:
            logger.warning(f"[{short_name}] no nav_links available, cannot select pages")
            return None

        cd = (company.get("company_data") or {})
        culture_link_ids = cd.get("culture_links_to_explore") or []

        if not culture_link_ids:
            logger.info(f"[{short_name}] no culture pages selected")
            return None

        # Step 3: map selected IDs back to URLs
        url_map = parse_enumerate_array(nav_links)
        selected_urls = [url_map[int(sid)] for sid in culture_link_ids if url_map.get(int(sid))]
        if not selected_urls:
            logger.warning(f"[{short_name}] no valid URLs from culture_link_ids")
            return None

        # Step 4: scrape each selected page
        max_pages = ROSTER_CONFIG.get("culture_pages", {}).get("max_pages", 6)
        logger.info(f"[{short_name}] scraping {len(selected_urls)} culture pages")
        pages = []
        async with create_browser_context() as context:
            for url in selected_urls[:max_pages]:
                try:
                    text = await get_visible_text(url=url, context=context)
                    if text and text.strip():
                        pages.append({"url": url, "content": text.strip()})
                        logger.info(f"[{short_name}] scraped {url} ({len(text.strip())} chars)")
                except Exception as e:
                    logger.warning(f"[{short_name}] scrape failed for {url}: {e}")
                    continue

        if not pages:
            logger.warning(f"[{short_name}] all scrapes failed")
            return None

        # Step 5: save and return
        save_company_data(short_name, {"website_content": pages})
        logger.info(f"[{short_name}] saved website_content ({len(pages)} pages)")
        return pages
    except ValueError:
        raise
    except Exception as e:
        logger.warning(f"[{short_name}] website_content fetch failed: {e}")
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
    response = await do_task(
        task_key="parse_job_list",
        live_content=dom_html or "",
        index=short_name,
        ctx=ctx,
    )
    if not response or not response.get("success"):
        err = (response or {}).get("error", "no parsed_response")
        logger.error(f"[{short_name}] parse_job_list failed: {err}")
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


def get_entity_agent_story(entity: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Expand the entity's agent_responses column entries with their block content.

    Reads from entity['agent_responses'] (the JSON column on the entity row,
    already parsed to a list by get_company/get_job). Each entry contains
    prompt_blocks: [{type, id}] referencing agent_data rows.

    For scored tasks (TASK_CONFIG[task_key].scored == True):
    - Attaches vector_grades and rubric_artifact to the enriched entry for display.
    - RESPONSE blocks for batch tasks (those with a "jobs" array) are filtered to
      just the matching astral_job_id entry. Old encoded data (no astral_job_id in
      the jobs array) yields an empty content string so the frontend skips rendering.

    Duplicate block types get a counter suffix: NO_CACHE, NO_CACHE (2).
    """
    entries = entity.get("agent_responses") or []
    if not entries:
        return []

    # Batch-fetch all block content in a single query
    all_ids = [
        b["id"]
        for e in entries
        for b in (e.get("prompt_blocks") or [])
        if isinstance(b, dict) and "id" in b
    ]
    data_map = get_agent_data_for_ids(all_ids)

    entity_job_id = entity.get("astral_job_id")  # None for companies

    enriched = []
    for e in entries:
        task_key = e.get("task_key", "")
        task_cfg = TASK_CONFIG.get(task_key, {})
        is_scored = bool(task_cfg.get("scored"))

        type_counts: Dict[str, int] = {}
        blocks = []
        for ref in (e.get("prompt_blocks") or []):
            if not isinstance(ref, dict):
                continue
            btype = ref.get("type", "UNKNOWN")
            bid = ref.get("id", "")
            type_counts[btype] = type_counts.get(btype, 0) + 1
            label = btype if type_counts[btype] == 1 else f"{btype} ({type_counts[btype]})"
            content = data_map.get(bid, {}).get("block_data", "") or ""

            # For scored batch tasks, filter RESPONSE blocks to this job's entry only.
            # Old encoded data (no astral_job_id) yields empty content → frontend skips.
            if is_scored and btype == "RESPONSE" and entity_job_id:
                content = _filter_response_block(content, entity_job_id)

            blocks.append({"type": label, "id": bid, "content": content})

        entry = {**e, "blocks": blocks}

        if is_scored:
            grades_key = task_cfg.get("grades_key")
            entry["vector_grades"] = entity.get("job_data", {}).get(grades_key) if grades_key else None
            entry["rubric_artifact"] = task_cfg.get("rubric_artifact")

        enriched.append(entry)

    return enriched


def _filter_response_block(content: str, astral_job_id: str) -> str:
    """For batch task RESPONSE blocks: filter the jobs array to the matching job.

    Returns the matching job entry as pretty JSON, empty string for old encoded
    data (no astral_job_id present), or the original content for non-batch responses.
    """
    try:
        parsed = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return content  # not JSON — leave as-is

    jobs = parsed.get("jobs") if isinstance(parsed, dict) else None
    if jobs is None:
        return content  # single-job response — show as-is

    # Check if any entry has astral_job_id (i.e. decoded, not old encoded data)
    if not any(isinstance(j, dict) and j.get("astral_job_id") for j in jobs):
        return ""  # old encoded payload — skip

    match = next((j for j in jobs if isinstance(j, dict) and j.get("astral_job_id") == astral_job_id), None)
    return json.dumps(match, indent=2) if match else ""



