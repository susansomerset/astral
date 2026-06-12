"""
Core gazer business logic.

In-scope: scrape_one, process_gazer_batch, process_gaze_board_batch, scrape_jd_batch, validate_title_batch. Re-exports get_new_company_batch and clear_company_batch
from roster for callers that want a single import from core.
Orchestration for job list scraping and scan lifecycle (scrape -> tracker ingest -> record); batch lifecycle (claim, release) is owned by CLI.
"""

import asyncio
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.core.roster import (
    get_company_data,
    get_new_company_batch,
    clear_company_batch,
    save_company_data,
)
from src.utils.config import BOARD_SEARCH_STATES, GAZER_CONFIG, ROSTER_CONFIG, TRACKER_CONFIG
from src.core.tracker import ingest_jobs, save_job_data, transition_job_state
from src.data.database import (
    get_company,
    record_to_company_job_scan,
    set_board_search_state,
    update_board_search_last_scan_at,
    update_company_last_scan_at,
)
from src.external.playwright import create_browser_context, get_page, load_all_jobs, extract_page_dom, get_visible_text, check_connectivity, extract_raw_job_listings
from src.utils.logging import get_logger

_log = get_logger(__name__)

# Maps _classify_jd() return value → JD_SCRAPE_FAIL_* state name
_JD_ERROR_STATES = {
    "cookie":  "JD_SCRAPE_FAIL_COOKIE",
    "bot":     "JD_SCRAPE_FAIL_BOT",
    "missing": "JD_SCRAPE_FAIL_MISSING",
    "closed":  "JD_SCRAPE_FAIL_CLOSED",
}


def _prune_jd(text: str, job_title: str = "") -> str:
    """Apply jd_prune_rules from TRACKER_CONFIG to trim boilerplate from JD text.
    Rules are applied in order; each mutates the text in place for the next rule.
    tail: truncate from rightmost match onward. head: discard up to and including match."""
    for rule in TRACKER_CONFIG.get("jd_prune_rules") or []:
        needle = (rule.get("prune_text") or "").replace("{$JOB_TITLE}", job_title)
        if not needle:
            continue
        idx = text.lower().find(needle.lower())
        if idx == -1:
            continue
        if rule.get("prune_type") == "tail":
            idx = text.lower().rfind(needle.lower())
            text = text[:idx]
        elif rule.get("prune_type") == "head":
            text = text[idx:]
    return text.strip()


def _classify_jd(text: str) -> str:
    """Classify scraped page content. Returns 'ok', 'cookie', 'bot', 'missing', or 'closed'.
    Check order matters: closed → bot → cookie → missing → ok.
    Reads all signals and thresholds from TRACKER_CONFIG['jd_classifier']."""
    cfg = TRACKER_CONFIG.get("jd_classifier", {})
    text_lower = text.lower()
    meaningful = re.sub(r"\s+", " ", text.strip())

    # --- No Longer Open ---
    for sig in cfg.get("closed_signals", []):
        if sig.lower() in text_lower:
            return "closed"

    # --- Bot Blocked --- (checked before cookie; LinkedIn auth pages mention "Cookie Policy")
    bot_hits = sum(1 for s in cfg.get("bot_signals", []) if s.lower() in text_lower)
    if bot_hits >= cfg.get("bot_threshold", 2):
        return "bot"

    # --- Cookie Block ---
    cookie_hits = sum(1 for s in cfg.get("cookie_signals", []) if s.lower() in text_lower)
    if cookie_hits >= cfg.get("cookie_threshold", 3):
        return "cookie"
    if cookie_hits >= cfg.get("cookie_short_threshold", 1) and len(meaningful) < cfg.get("cookie_short_max", 400):
        return "cookie"

    # --- Missing Page (wrong page / 404 / job board / empty shell) ---
    if len(meaningful) < cfg.get("min_meaningful_chars", 500):
        return "missing"
    ws_ratio = (text.count("\n") + text.count("\t") + text.count(" ")) / max(len(text), 1)
    words = re.findall(r"\b\w{4,}\b", text)
    if ws_ratio > 0.60 and len(words) < 200:
        return "missing"
    date_hits = len(re.findall(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+202\d", text))
    if date_hits >= cfg.get("date_pattern_threshold", 5):
        return "missing"

    return "ok"


async def scrape_jd_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    debug: bool = False,
    ) -> Dict[str, int]:
    """Scrape, prune, and gate JDs for a batch of jobs (ast-326).
    Transitions each job to JD_READY (pass) or JD_SCRAPE_FAIL (fail/short).
    Returns {"passed": N, "failed": N, "total": N}."""
    if not await check_connectivity():
        raise ConnectionError(f"scrape_jd_batch: no internet connectivity, aborting batch {batch_id} ({len(jobs)} jobs)")
    cfg = TRACKER_CONFIG
    jd_key = cfg.get("job_data_keys", {}).get("job_description", "job_description")
    min_chars = cfg.get("jd_min_chars", 200)
    # Success / generic scrape-fail transitions (classified JD errors route via _JD_ERROR_STATES)
    pass_state = GAZER_CONFIG["scrape_jd"]["pass_state"]
    fail_state = GAZER_CONFIG["scrape_jd"]["fail_state"]

    passed = failed = 0

    async def _scrape_one(job: Dict) -> None:
        nonlocal passed, failed
        aid = job.get("astral_job_id", "")
        job_link = (job.get("job_link") or "").strip()
        title = job.get("job_title", aid)
        if not job_link:
            _log.warning("[%s] no job_link, cannot scrape JD", aid)
            transition_job_state([aid], fail_state)
            failed += 1
            return
        try:
            text = await get_visible_text(url=job_link)
        except Exception as e:
            _log.warning("[%s] get_visible_text failed: %s", aid, e)
            transition_job_state([aid], fail_state)
            failed += 1
            return
        if not text or not text.strip():
            _log.warning("[%s] empty visible text from %s", aid, job_link)
            transition_job_state([aid], fail_state)
            failed += 1
            return
        text = _prune_jd(text, job.get("job_title", ""))
        if debug:
            _log.info("[%s] pruned JD: %d chars", aid, len(text))
        if len(text) < min_chars:
            _log.warning("[%s] JD too short (%d chars < %d), -> %s", aid, len(text), min_chars, fail_state)
            transition_job_state([aid], fail_state)
            failed += 1
            return
        classification = _classify_jd(text)
        if classification != "ok":
            error_state = _JD_ERROR_STATES[classification]
            # Save the text so the bad capture is inspectable in the DB
            save_job_data(aid, {jd_key: text})
            _log.warning("[%s] JD classified as %r -> %s", aid, classification, error_state)
            transition_job_state([aid], error_state)
            failed += 1
            return
        save_job_data(aid, {jd_key: text})
        # Write back into in-memory dict so coat-check is a true no-op if called after this
        if not isinstance(job.get("job_data"), dict):
            job["job_data"] = {}
        job["job_data"][jd_key] = text
        transition_job_state([aid], pass_state)
        if debug:
            _log.info("[%s] %s -> %s (%d chars)", aid, title, pass_state, len(text))
        passed += 1

    # Cap concurrent Firefox instances to avoid exhausting container resources (EAGAIN / SIGSEGV)
    sem = asyncio.Semaphore(3)
    async def _limited(job: Dict) -> None:
        async with sem:
            await _scrape_one(job)

    await asyncio.gather(*[_limited(j) for j in jobs], return_exceptions=False)
    return {"passed": passed, "failed": failed, "total": len(jobs)}


def _compiled_title_patterns(ctx: Dict[str, Any]) -> List[Any]:
    """Parse profile.title_patterns (newline-delimited regexes). Skip invalid lines; empty / missing => []."""
    cd = ctx.get("candidate_data") or {}
    if not isinstance(cd, dict):
        return []
    profile = cd.get("profile") or {}
    if not isinstance(profile, dict):
        return []
    raw = profile.get("title_patterns") or profile.get("TITLE_PATTERNS") or ""
    if not isinstance(raw, str):
        raw = str(raw) if raw else ""
    out: List[Any] = []
    for line in raw.splitlines():
        pat = line.strip()
        if not pat:
            continue
        try:
            out.append(re.compile(pat, re.IGNORECASE | re.DOTALL))
        except re.error as e:
            _log.warning("validate_title_batch: skipping invalid regex %r: %s", pat, e)
    return out


async def validate_title_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Dict[str, Any],
    debug: bool = False,
    ) -> Dict[str, int]:
    """AST-335: NEW jobs -> VALID_TITLE if raw_job_listing matches any profile title regex, else INVALID_TITLE.
    No patterns (or only invalid lines): all jobs -> VALID_TITLE so qualify is not blocked."""
    _ = batch_id  # batch id is on claimed rows; transitions use existing job batch_id in DB
    task_cfg = GAZER_CONFIG["validate_title"]
    pass_state = task_cfg["pass_state"]
    fail_state = task_cfg["fail_state"]
    patterns = _compiled_title_patterns(ctx)
    passed = failed = 0
    for job in jobs:
        aid = job.get("astral_job_id", "")
        jd = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}
        raw_listing = (jd or {}).get("raw_job_listing") or ""
        if not isinstance(raw_listing, str):
            raw_listing = str(raw_listing) if raw_listing else ""
        # No usable patterns => permissive (same as empty title_patterns field)
        if not patterns:
            ok = True
        else:
            ok = any(p.search(raw_listing) for p in patterns)
        if ok:
            transition_job_state([aid], pass_state)
            passed += 1
            if debug:
                _log.info("[%s] title pattern match -> %s", aid, pass_state)
        else:
            transition_job_state([aid], fail_state)
            failed += 1
            if debug:
                _log.info("[%s] no title pattern match -> %s", aid, fail_state)
    return {"passed": passed, "failed": failed, "total": len(jobs)}


# ---- Scrape ----

async def scrape_one(short_name: str, job_site: str) -> Tuple[str, str, str]:
    """Scrape one company's job page. Creates its own browser context; returns (short_name, job_site, page_html)."""
    async with create_browser_context() as context:
        page = await get_page(context, job_site)
        try:
            await load_all_jobs(page, short_name)
            dom_html = await extract_page_dom(page, "body")
            return (short_name, job_site, dom_html)
        finally:
            await page.close()


# ---- Process batch (scrape -> parse -> ingest -> record) ----

async def process_gazer_batch(
    batch_id: str,
    companies: List[Dict[str, Any]],
    debug: bool = False,
    ctx: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
    """Scrape each company, parse job list, ingest via tracker, record scan outcome. Returns list of outcome dicts (short_name, status, message, new, duplicates, title_mismatch)."""
    if not await check_connectivity():
        raise ConnectionError(f"process_gazer_batch: no internet connectivity, aborting batch {batch_id} ({len(companies)} companies)")
    to_scrape = []
    for c in companies:
        short_name = c.get("short_name", "")
        job_site = (c.get("job_site") or "").strip()
        if short_name and job_site:
            to_scrape.append((short_name, job_site))
    results = await asyncio.gather(
        *[scrape_one(sn, js) for sn, js in to_scrape],
        return_exceptions=True,
    )
    results_by_short_name: Dict[str, Tuple[str, str, str]] = {}
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            continue
        short_name, job_site, page_html = r
        results_by_short_name[short_name] = (short_name, job_site, page_html)

    scan_completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    outcomes: List[Dict[str, Any]] = []

    for c in companies:
        short_name = c.get("short_name", "")
        if not short_name:
            continue

        if short_name not in results_by_short_name:
            record_to_company_job_scan(
                batch_id, short_name, scan_completed_at,
                total_found=None, new=None, duplicates=None,
                status="failure", failure_message="Scrape failed",
            )
            outcomes.append({"short_name": short_name, "status": "failure", "message": "Scrape failed", "new": None, "duplicates": None})
            continue

        _, job_site, page_html = results_by_short_name[short_name]
        raw_job_listings: List[str] = []
        parse_instructions = await get_company_data(
            c, ROSTER_CONFIG["company_data_keys"]["parse_instructions"]
        )

        if not parse_instructions:
            record_to_company_job_scan(
                batch_id, short_name, scan_completed_at,
                total_found=None, new=None, duplicates=None,
                status="failure", failure_message="no parse_instructions — re-run find_job_page",
            )
            outcomes.append({"short_name": short_name, "status": "failure", "message": "no parse_instructions — re-run find_job_page", "new": None, "duplicates": None})
            continue

        container = parse_instructions.get("container") or ""
        job_tag = parse_instructions.get("job_tag") or ""
        container_index = parse_instructions.get("container_index", 0)
        raw_job_listings = extract_raw_job_listings(page_html, container, job_tag, container_index)
        patterns = _compiled_title_patterns(ctx or {})
        title_matchers = patterns or None

        try:
            result = ingest_jobs(short_name, batch_id, raw_job_listings, title_matchers=title_matchers)
            total_found = len(raw_job_listings)
            new_count = result.get("new", 0)
            dup_count = result.get("duplicates", 0)
            # Canonical ingest_jobs key invalid_title (board-ingest parity); legacy return dict may still use title_mismatch.
            title_mismatch_count = result.get("invalid_title", result.get("title_mismatch", 0))
            record_to_company_job_scan(
                batch_id, short_name, scan_completed_at,
                total_found=total_found, new=new_count, duplicates=dup_count,
                title_mismatch=title_mismatch_count,
                status="success", failure_message=None,
            )
            update_company_last_scan_at(short_name)
            outcomes.append({
                "short_name": short_name, "status": "success",
                "message": f"ingest: new={new_count} duplicates={dup_count} title_mismatch={title_mismatch_count}",
                "new": new_count, "duplicates": dup_count, "title_mismatch": title_mismatch_count,
            })
        except Exception as e:
            record_to_company_job_scan(
                batch_id, short_name, scan_completed_at,
                total_found=len(raw_job_listings), new=None, duplicates=None,
                status="failure", failure_message=str(e),
            )
            outcomes.append({"short_name": short_name, "status": "failure", "message": f"ingest_error: {e}", "new": None, "duplicates": None})

    return outcomes


async def process_gaze_board_batch(
    batch_id: str,
    searches: List[Dict[str, Any]],
    debug: bool = False,
    ctx: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Scrape claimed board_search rows (anonymous gaze_board path). Matches consult.run_consult_task board_search routing."""
    from src.core.boards import run_board_search_gaze

    act, _, err_st = BOARD_SEARCH_STATES
    outcomes: List[Dict[str, Any]] = []
    cctx = ctx if ctx is not None else {}
    for row in searches:
        sid = (row.get("board_search_id") or "").strip()
        if not sid:
            continue
        try:
            r = await run_board_search_gaze(batch_id, row, ctx=cctx)
            merged = dict(r)
            merged.setdefault("status", "success")
            update_board_search_last_scan_at(sid)
            outcomes.append(merged)
            set_board_search_state(sid, act)
        except Exception as e:
            _log.error(
                "process_gaze_board_batch board_search_id=%s board_key=%s error=%s",
                sid,
                (row.get("board_key") or ""),
                str(e),
            )
            outcomes.append({"board_search_id": sid, "status": "failure", "error": str(e)})
            set_board_search_state(sid, err_st)
        if debug:
            _log.debug(  # pragma: no cover — noise-only trace; branches covered via debug toggle in tests (§7.12 lock).
                "process_gaze_board_batch batch_id=%s board_search_id=%s",
                batch_id,
                sid,
            )

    return outcomes
