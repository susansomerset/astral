"""
Core gazer business logic.

In-scope: scrape_one, process_gazer_batch, fetch_jd_batch, fetch_relative_jd_batch, fetch_culture_pages_batch, fetch_company_culture_pages_batch,
fetch_website_batch, fetch_job_pages_batch, validate_title_batch,
contact_task_gazer_scrape (AST-1516 contact-task scrape),
ingest_meteorite_jobs_from_email_html (AST-1061 gazer-reads-email).
telescope_data owner (AST-2132): keep_telescope_data, keep_page_scrape, scrape_visible_text_and_keep, scrape_page_links_and_keep, resolve_telescope_value — the only core caller of the telescope_data data functions.
Re-exports get_new_company_batch and clear_company_batch from roster for callers
that want a single import from core.
Orchestration for job list scraping and scan lifecycle (scrape -> tracker ingest -> record);
batch lifecycle (claim, release) is owned by CLI.
"""

import asyncio
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from src.core.roster import (
    get_company_data,
    get_new_company_batch,
    clear_company_batch,
    save_company_data,
    scrape_company_homepage_content,
    transition_company_state,
    _merge_pjl_scrape_record,
    _scrape_pjl_page,
)
from src.utils.config import (
    GAZER_CONFIG,
    METEORITE_EMAIL_INGEST_CONFIG,
    ROSTER_CONFIG,
    SOURCE_ENTITY_TYPE_METEORITE,
    TELESCOPE_DATA_CONFIG,
    TRACKER_CONFIG,
)
from src.core.tracker import ingest_jobs, persist_http_job_link, save_job_data, transition_job_state
from src.core.meteorite import create_meteorite_job
from src.data.database import (
    get_company,
    get_telescope_data_for_ids,
    job_link_exists_for_candidate,
    record_to_company_job_scan,
    raw_job_listing_is_duplicate,
    save_telescope_data,
    text_matches_known_company_job_id_for_candidate,
    update_company_last_scan_at,
)
from src.external.telescope import (
    create_browser_context,
    create_batch_browser_session,
    get_page,
    close_page,
    load_all_jobs,
    extract_page_dom,
    extract_page_scrape_contract,
    extract_site_page_list,
    get_visible_text,
    check_connectivity,
    extract_raw_job_listings,
    run_one_shot,
    click_through_visible_text,
    PlaywrightInfraError,
    TELESCOPE_CLICK_TARGET_MISSING,
)
from src.utils.formatting import (
    collapse_consecutive_blank_lines,
    enumerate_array,
    normalize_pasted_list_email_html,
)
from src.utils.logging import get_logger, truncate_debug_content

_log = get_logger(__name__)

# AST-2132: gazer owns telescope_data. Row ids are uuid4 strings (database.save_telescope_data).
_TELESCOPE_ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_VISIBLE_TEXT = TELESCOPE_DATA_CONFIG["data_types"]["VISIBLE_TEXT"]
_PAGE_LINKS = TELESCOPE_DATA_CONFIG["data_types"]["PAGE_LINKS"]


def _is_fetch_website_infra_error(error: str) -> bool:
    """True when scrape error is browser infra (AST-853 prefix or scrape_timeout label)."""
    msg = (error or "").strip()
    return msg.startswith("[playwright:")


def _fetch_website_fail_destination(
    company_state: str, error: str, cfg: Dict[str, Any], visible_text: str = "",
) -> Optional[str]:
    """Route infra → retry once; bot wall → BOT_BLOCKED_<task>; site failure or retry re-fail → fail_state.
    None when the scrape neither errored nor hit a bot wall (success path)."""
    if is_bot_wall(visible_text):
        return cfg["bot_blocked_state"]
    if not error:
        return None
    retry_state = cfg["retry_state"]
    fail_state = cfg["fail_state"]
    if _is_fetch_website_infra_error(error):
        if (company_state or "").strip() == retry_state:
            return fail_state
        return retry_state
    return fail_state


def _gazer_job_identifier(job: Dict[str, Any]) -> str:
    """Primary debug identifier for a job row (§1.5.1 style D)."""
    return str(job.get("astral_job_id") or job.get("job_title") or "?")


def _gazer_company_identifier(row: Dict[str, Any]) -> str:
    """Primary debug identifier for a company row in gaze batches."""
    return str(row.get("short_name") or "?")


# Maps _classify_jd() → Estelle/contact page_status (parent AC2: blocked/ok/closed/missing)
_CONTACT_PAGE_STATUS = {
    "ok": "ok",
    "closed": "closed",
    "missing": "missing",
    "bot": "blocked",
    "cookie": "blocked",
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


def is_bot_wall(text: str) -> bool:
    """True when page text trips the shared bot/challenge detector in TRACKER_CONFIG['jd_classifier'].
    Single source for JD classification and roster select_job_page (AST-2004) — do not copy the loop."""
    cfg = TRACKER_CONFIG.get("jd_classifier", {})
    text_lower = (text or "").lower()
    hits = sum(1 for s in cfg.get("bot_signals", []) if s.lower() in text_lower)
    return hits >= cfg.get("bot_threshold", 2)


# ---- telescope_data (AST-2132) ----

def is_telescope_id(value: Any) -> bool:
    """True when value is a telescope_data row id (uuid-shaped str), not legacy scraped text."""
    return isinstance(value, str) and bool(_TELESCOPE_ID_RE.match(value))


def keep_telescope_data(
    candidate_id: str | None, url: str, data_type: str, content: str,
) -> str | None:
    """Store one scrape result in telescope_data and return its row id; None when content is blank.

    data_type is passed through unchecked (free text by design). Links are stored as the
    enumerated string readers use today, so resolving an id never needs the type.
    DB errors propagate to the caller's existing failure path."""
    if not (content or "").strip():
        return None
    _log.debug(
        "Calling save_telescope_data: [candidate_id=%s url=%s data_type=%s content=%s]",
        candidate_id, url, data_type, content,
    )
    row_id = save_telescope_data(candidate_id, url, data_type, content)
    _log.debug("Response from save_telescope_data: %s", row_id)
    return row_id


def keep_page_scrape(
    candidate_id: str | None, url: str, scrape: dict[str, Any],
) -> tuple[str | None, str | None]:
    """Keep a page-contract scrape (roster scrape_company_homepage_content / _scrape_pjl_page result):
    visible_text as VISIBLE_TEXT, enumerated_nav_links as PAGE_LINKS. Returns (text_id, links_id)."""
    return (
        keep_telescope_data(candidate_id, url, _VISIBLE_TEXT, scrape.get("visible_text") or ""),
        keep_telescope_data(candidate_id, url, _PAGE_LINKS, scrape.get("enumerated_nav_links") or ""),
    )


async def scrape_visible_text_and_keep(
    candidate_id: str | None, url: str, *, context: Any = None,
) -> tuple[str, str, str | None]:
    """Telescope visible text for url, kept in telescope_data. Returns (text, final_url, row_id).
    Scrape errors propagate — callers already route them."""
    _log.debug("Calling get_visible_text: [url=%s]", url)
    text, final_url = await get_visible_text(url=url, context=context, return_final_url=True)
    _log.debug("Response from get_visible_text: final_url=%s text=%s", final_url, text)
    text = text or ""
    return text, final_url or url, keep_telescope_data(candidate_id, url, _VISIBLE_TEXT, text)


async def scrape_page_links_and_keep(
    candidate_id: str | None, url: str, *, context: Any = None,
) -> tuple[list[str], str | None]:
    """Telescope link list for url (depth 1, unverified — roster's nav_links fetch shape), kept in
    telescope_data as the enumerated list. Returns (urls, row_id). Scrape errors propagate."""
    _log.debug("Calling extract_site_page_list: [url=%s]", url)
    urls = await extract_site_page_list(url, max_depth=1, verify=False, context=context) or []
    _log.debug("Response from extract_site_page_list: %s", urls)
    enumerated = enumerate_array("", urls) if urls else ""
    return urls, keep_telescope_data(candidate_id, url, _PAGE_LINKS, enumerated)


def resolve_telescope_value(value: Any) -> Any:
    """Stored blob value -> content in today's shape; legacy text tolerant.

    Row id -> that row's content (text, or enumerated links), None when the row is gone.
    List -> each {url, id, ...} entry becomes {url, content, ...} (other keys kept); entries
    without a row id (legacy {url, content}) pass through; entries whose row is gone drop;
    an empty result is None so fetch-on-missing callers re-scrape.
    Anything else (legacy text, None, dict) is returned unchanged."""
    if is_telescope_id(value):
        ids = [value]
    elif isinstance(value, list):
        ids = [e["id"] for e in value if isinstance(e, dict) and is_telescope_id(e.get("id"))]
    else:
        return value
    _log.debug("Calling get_telescope_data_for_ids: %s", ids)
    rows = get_telescope_data_for_ids(ids)
    _log.debug("Response from get_telescope_data_for_ids: %s", rows)
    missing = [i for i in ids if i not in rows]
    if missing:
        _log.warning(
            "telescope_data %s missing — resolving without them; fetch-on-missing callers re-scrape",
            missing,
        )
    if isinstance(value, str):
        return rows.get(value)
    out = []
    for e in value:
        if not (isinstance(e, dict) and is_telescope_id(e.get("id"))):
            out.append(e)
        elif e["id"] in rows:
            out.append({**{k: v for k, v in e.items() if k != "id"}, "content": rows[e["id"]]})
    return out or None


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
    if is_bot_wall(text):
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


def _apply_jd_gates(
    job: dict[str, Any], text: str, *, short_state: str, pass_state: str, classified_states: Dict[str, str],
    telescope_data_id: str | None,
) -> bool:
    """Shared JD gates for fetch_jd_batch and fetch_relative_jd_batch (AST-2025).

    collapse blank lines -> empty check -> prune -> min_chars -> classify. Stores the scraped-JD
    reference (telescope_data row id of the raw capture) — never JD text; job_description stays
    the preamble (AST-2130) — and transitions the job. Empty / too-short -> short_state; classified -> the calling task's
    GAZER_CONFIG classified_states (cookie / bot / missing / closed); ok -> pass_state.
    Returns True only when the job reached pass_state.
    """
    ref_key = TRACKER_CONFIG["job_data_keys"]["jd_telescope_data_id"]
    min_chars = TRACKER_CONFIG.get("jd_min_chars", 200)
    aid = job.get("astral_job_id", "")
    text = collapse_consecutive_blank_lines(text)
    if not text or not text.strip():
        _log.warning("%s -> %s [empty visible text]", aid, short_state)
        transition_job_state([aid], short_state)
        return False
    text = _prune_jd(text, job.get("job_title", ""))
    if len(text) < min_chars:
        _log.warning("%s -> %s [JD too short: %d < %d chars]", aid, short_state, len(text), min_chars)
        transition_job_state([aid], short_state)
        return False
    classification = _classify_jd(text)
    if classification != "ok":
        error_state = classified_states[classification]
        # Reference the kept capture so the bad page stays inspectable; job_description (preamble) is untouched
        save_job_data(aid, {ref_key: telescope_data_id})
        _log.warning("%s -> %s [JD classified %r]", aid, error_state, classification)
        transition_job_state([aid], error_state)
        return False
    save_job_data(aid, {ref_key: telescope_data_id})
    # Write back into in-memory dict so coat-check is a true no-op if called after this
    if not isinstance(job.get("job_data"), dict):
        job["job_data"] = {}
    job["job_data"][ref_key] = telescope_data_id
    transition_job_state([aid], pass_state)
    return True


async def fetch_jd_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    debug: bool = False,
    ) -> Dict[str, int]:
    """Scrape, prune, and gate JDs for a batch of jobs (ast-326).
    Transitions each job to JD_READY (pass) or ERROR_FETCH_JD_UNREADABLE (fail/short).
    Returns {"passed": N, "failed": N, "total": N}."""
    if not await check_connectivity():
        raise ConnectionError(f"fetch_jd_batch: no internet connectivity, aborting batch {batch_id} ({len(jobs)} jobs)")
    if debug:
        _log.set_debug_flag(True)
    # Success / generic scrape-fail transitions (classified JD errors route via classified_states)
    pass_state = GAZER_CONFIG["fetch_jd"]["pass_state"]
    fail_state = GAZER_CONFIG["fetch_jd"]["fail_state"]
    job_total = len(jobs)

    passed = failed = 0
    if debug and job_total > 0:
        _log.debug_index(
            func="gazer.fetch_jd_batch",
            index=1,
            total=1,
            identifier=batch_id,
            outcome=f"batch start {job_total} job(s)",
        )

    async def _scrape_one(job: Dict, job_index: int) -> None:
        nonlocal passed, failed
        aid = job.get("astral_job_id", "")
        job_link = (job.get("job_link") or "").strip()
        if not job_link:
            if debug:
                _log.debug_index(
                    func="gazer.fetch_jd_batch",
                    index=job_index,
                    total=job_total,
                    identifier=_gazer_job_identifier(job),
                    outcome=f"failed — no job_link -> {fail_state}",
                )
            _log.warning("[%s] no job_link, cannot scrape JD", aid)
            transition_job_state([aid], fail_state)
            failed += 1
            return
        try:
            text, _, row_id = await scrape_visible_text_and_keep(job.get("candidate_id"), job_link)
        except Exception as e:
            if debug:
                _log.debug_index(
                    func="gazer.fetch_jd_batch",
                    index=job_index,
                    total=job_total,
                    identifier=_gazer_job_identifier(job),
                    outcome=f"failed — scrape error: {e!s} -> {fail_state}",
                )
                _log.debug_detail(f"job_link={job_link!r}")
            _log.warning("[%s] get_visible_text failed: %s", aid, e)
            transition_job_state([aid], fail_state)
            failed += 1
            return
        _log.debug(
            "Calling JD gates: [astral_job_id=%s short_state=%s pass_state=%s text=%s]",
            aid, fail_state, pass_state, text,
        )
        gated = _apply_jd_gates(
            job, text, short_state=fail_state, pass_state=pass_state,
            classified_states=GAZER_CONFIG["fetch_jd"]["classified_states"],
            telescope_data_id=row_id,
        )
        _log.debug("Response from JD gates: %s", gated)
        if gated:
            _log.info("%s | job %s: %s (batch: %s)", aid, "JD kept", pass_state, batch_id)
            passed += 1
        else:
            failed += 1

    await asyncio.gather(
        *[_scrape_one(j, ji) for ji, j in enumerate(jobs, start=1)],
        return_exceptions=False,
    )
    if debug:
        _log.debug_detail(
            f"summary passed={passed} failed={failed} total={job_total} "
            f"pass_state={pass_state!r} fail_state={fail_state!r}"
        )
    return {"passed": passed, "failed": failed, "total": len(jobs)}


async def fetch_relative_jd_batch(batch_id: str, jobs: list[dict[str, Any]]) -> dict[str, int]:
    """Click-through JD fetch for RELATIVE_JOB_LINK jobs (AST-2025).

    Per claimed job: Telescope opens company job_site, clicks the <a> whose href equals the
    stored relative job_link, returns (final_url, text). The resolved absolute URL replaces
    job_link, then the same JD gates as fetch_jd_batch decide the state. Click / Telescope
    failure -> fail_state with job_link left relative. Processes only `jobs` (dispatcher
    claimed and releases them). Returns {"passed": N, "failed": N, "total": N}.
    """
    if not await check_connectivity():
        raise ConnectionError(
            f"fetch_relative_jd_batch: no internet connectivity, aborting batch {batch_id} ({len(jobs)} jobs)"
        )
    cfg = GAZER_CONFIG["fetch_relative_jd"]
    pass_state = cfg["pass_state"]
    fail_state = cfg["fail_state"]
    # Empty / too-short text after a successful click: this task's own unreadable terminal.
    short_state = cfg["unreadable_state"]
    passed = failed = 0

    async def _fetch_one(job: dict[str, Any]) -> None:
        nonlocal passed, failed
        aid = job.get("astral_job_id", "")
        job_site = (job.get("job_site") or "").strip()
        href = (job.get("job_link") or "").strip()
        if not job_site or not href:
            _log.warning("%s -> %s [missing job_site %r or job_link %r]", aid, fail_state, job_site, href)
            transition_job_state([aid], fail_state)
            failed += 1
            return
        try:
            final_url, text = await click_through_visible_text(job_site, href)
        except Exception as e:  # noqa: BLE001 — every Telescope/client failure routes to fail_state (AST-2022 §5)
            if isinstance(e, PlaywrightInfraError) and e.failure_class == TELESCOPE_CLICK_TARGET_MISSING:
                _log.warning("%s -> %s [click target missing: href=%r list_url=%s]", aid, fail_state, href, job_site)
            else:
                _log.exception(
                    "%s -> %s [click-through failed: href=%r list_url=%s]\n  %s: %s\n  Continuing to the next job",
                    aid, fail_state, href, job_site, type(e).__name__, e,
                )
            transition_job_state([aid], fail_state)
            failed += 1
            return
        row_id = keep_telescope_data(job.get("candidate_id"), final_url, _VISIBLE_TEXT, text)
        if not final_url.startswith(("http://", "https://")):
            _log.warning("%s -> %s [click-through returned non-http final_url %r]", aid, fail_state, final_url)
            transition_job_state([aid], fail_state)
            failed += 1
            return
        _log.debug("Calling persist_http_job_link: [astral_job_id=%s job_link=%s]", aid, final_url)
        persist_http_job_link(aid, final_url)
        _log.debug(
            "Calling JD gates: [astral_job_id=%s short_state=%s pass_state=%s text=%s]",
            aid, short_state, pass_state, text,
        )
        gated = _apply_jd_gates(
            job, text, short_state=short_state, pass_state=pass_state, classified_states=cfg["classified_states"],
            telescope_data_id=row_id,
        )
        _log.debug("Response from JD gates: %s", gated)
        if gated:
            _log.info("%s | job %s: %s (batch: %s)", aid, "relative link fetched", pass_state, batch_id)
            passed += 1
        else:
            failed += 1

    _log.debug("Beginning fetch_relative_jd loop on %s items", len(jobs))
    await asyncio.gather(*[_fetch_one(j) for j in jobs], return_exceptions=False)
    _log.debug("End fetch_relative_jd loop after %s items", passed + failed)
    return {"passed": passed, "failed": failed, "total": len(jobs)}


def _website_content_is_recorded(website_content: Any) -> bool:
    """True when company_data already has usable culture page bodies (AST-874 cache path)."""
    if isinstance(website_content, list):
        return any(
            isinstance(p, dict) and str(p.get("content") or "").strip()
            for p in website_content
        )
    if isinstance(website_content, str):
        return bool(website_content.strip())
    return False


def _website_content_bot_walled(content: Any) -> bool:
    """True when every fetched page in website_content is a bot wall (nothing usable to grade)."""
    if isinstance(content, list):
        pages = [p.get("content") or "" for p in content if isinstance(p, dict)]
    else:
        pages = [content] if isinstance(content, str) and content else []
    return bool(pages) and all(is_bot_wall(t) for t in pages)


def _website_content_debug_summary(website_content: Any) -> str:
    """Short found/recorded summary for fetch_culture_pages debug detail lines."""
    if isinstance(website_content, list):
        pages = [
            p for p in website_content
            if isinstance(p, dict) and str(p.get("content") or "").strip()
        ]
        urls = [str(p.get("url") or "") for p in pages[:5]]
        return f"pages={len(pages)} urls={urls!r}"
    if isinstance(website_content, str):
        return f"chars={len(website_content.strip())}"
    return "empty"


async def fetch_culture_pages_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    debug: bool = False,
) -> Dict[str, int]:
    """Ensure culture page content via roster coat-check; gate jobs to CULTURE_READY (AST-874).

    Transitions each job to CULTURE_READY (pass), ERROR_FETCH_CULTURE_PAGES_UNREADABLE (coat-check
    fail), BOT_BLOCKED_FETCH_CULTURE_PAGES (every page a bot wall, cached or fresh), or
    ERROR_FETCH_CULTURE_PAGES_NO_CULTURE_LINKS (no culture_links_to_explore).
    Returns {"passed", "failed", "total"}.
    """
    if not await check_connectivity():
        raise ConnectionError(
            f"fetch_culture_pages_batch: no internet connectivity, aborting batch {batch_id} "
            f"({len(jobs)} jobs)"
        )
    if debug:
        _log.set_debug_flag(True)
    cfg = GAZER_CONFIG["fetch_culture_pages"]
    pass_state = cfg["pass_state"]
    fail_state = cfg["fail_state"]
    bot_state = cfg["bot_blocked_state"]
    no_links_state = cfg["no_links_state"]
    job_total = len(jobs)
    passed = failed = 0

    if debug and job_total > 0:
        _log.debug_index(
            func="gazer.fetch_culture_pages_batch",
            index=1,
            total=1,
            identifier=batch_id,
            outcome=f"batch start {job_total} job(s)",
        )

    # Sequential: coat-check scrapes one company at a time; shared company rows must not race.
    for job_index, job in enumerate(jobs, start=1):
        aid = job.get("astral_job_id", "")
        company_key = (job.get("company") or "").strip()
        if not company_key:
            if debug:
                _log.debug_index(
                    func="gazer.fetch_culture_pages_batch",
                    index=job_index,
                    total=job_total,
                    identifier=_gazer_job_identifier(job),
                    outcome=f"failed — no company -> {fail_state}",
                )
            transition_job_state([aid], fail_state)
            failed += 1
            continue
        company = get_company(company_key)
        if company is None:
            if debug:
                _log.debug_index(
                    func="gazer.fetch_culture_pages_batch",
                    index=job_index,
                    total=job_total,
                    identifier=_gazer_job_identifier(job),
                    outcome=f"failed — no company -> {fail_state}",
                )
            transition_job_state([aid], fail_state)
            failed += 1
            continue

        cd = company.get("company_data")
        if not isinstance(cd, dict):
            cd = {}
            company["company_data"] = cd

        recorded = resolve_telescope_value(cd.get("website_content"))
        if _website_content_is_recorded(recorded):
            if _website_content_bot_walled(recorded):
                transition_job_state([aid], bot_state)
                if debug:
                    _log.debug_index(
                        func="gazer.fetch_culture_pages_batch",
                        index=job_index,
                        total=job_total,
                        identifier=_gazer_job_identifier(job),
                        outcome=f"failed — bot wall -> {bot_state} (cached)",
                    )
                failed += 1
                continue
            transition_job_state([aid], pass_state)
            if debug:
                _log.debug_index(
                    func="gazer.fetch_culture_pages_batch",
                    index=job_index,
                    total=job_total,
                    identifier=_gazer_job_identifier(job),
                    outcome=f"passed -> {pass_state} (cached)",
                )
                _log.debug_detail(
                    f"{_website_content_debug_summary(recorded)} recorded=cached "
                    f"company={company_key!r}"
                )
            passed += 1
            continue

        links = cd.get("culture_links_to_explore") or []
        if not links:
            transition_job_state([aid], no_links_state)
            if debug:
                _log.debug_index(
                    func="gazer.fetch_culture_pages_batch",
                    index=job_index,
                    total=job_total,
                    identifier=_gazer_job_identifier(job),
                    outcome=f"failed — no culture links -> {no_links_state}",
                )
                _log.debug_detail(
                    f"culture_links_to_explore=[] company={company_key!r}"
                )
            failed += 1
            continue

        content = await get_company_data(company, "website_content")
        if content:
            company.setdefault("company_data", {})["website_content"] = content
            if _website_content_bot_walled(resolve_telescope_value(content)):
                transition_job_state([aid], bot_state)
                if debug:
                    _log.debug_index(
                        func="gazer.fetch_culture_pages_batch",
                        index=job_index,
                        total=job_total,
                        identifier=_gazer_job_identifier(job),
                        outcome=f"failed — bot wall -> {bot_state}",
                    )
                failed += 1
                continue
            transition_job_state([aid], pass_state)
            if debug:
                _log.debug_index(
                    func="gazer.fetch_culture_pages_batch",
                    index=job_index,
                    total=job_total,
                    identifier=_gazer_job_identifier(job),
                    outcome=f"passed -> {pass_state}",
                )
                _log.debug_detail(
                    f"{_website_content_debug_summary(content)} recorded=coat-check "
                    f"company={company_key!r}"
                )
            passed += 1
            continue

        transition_job_state([aid], fail_state)
        if debug:
            _log.debug_index(
                func="gazer.fetch_culture_pages_batch",
                index=job_index,
                total=job_total,
                identifier=_gazer_job_identifier(job),
                outcome=f"failed — coat-check empty -> {fail_state}",
            )
            _log.debug_detail(
                f"links_present={len(links)} company={company_key!r} recorded=none"
            )
        failed += 1

    if debug:
        _log.debug_detail(
            f"summary passed={passed} failed={failed} total={job_total} "
            f"pass_state={pass_state!r} fail_state={fail_state!r} "
            f"bot_state={bot_state!r} no_links_state={no_links_state!r}"
        )
    return {"passed": passed, "failed": failed, "total": len(jobs)}


async def fetch_company_culture_pages_batch(
    batch_id: str,
    companies: List[Dict[str, Any]],
    debug: bool = False,
) -> Dict[str, int]:
    """Scrape culture pages into company_data.website_content for GET_UPSHOT companies (AST-2070).

    Every company transitions to UPSHOT_READY whether its content was cached, scraped, or not
    found; this hop never fails a company out. Lost connectivity raises ConnectionError before any transition.
    Returns {"passed", "failed", "total"}.
    """
    if not await check_connectivity():
        raise ConnectionError(
            f"fetch_company_culture_pages_batch: no internet connectivity, aborting batch {batch_id} "
            f"({len(companies)} companies)"
        )
    if debug:
        _log.set_debug_flag(True)
    pass_state = GAZER_CONFIG["fetch_company_culture_pages"]["pass_state"]
    company_total = len(companies)
    passed = 0

    # Sequential like fetch_culture_pages_batch: each coat-check scrape opens its own browser context.
    for company_index, company in enumerate(companies, start=1):
        short_name = company.get("short_name") or ""
        cd = company.get("company_data") if isinstance(company.get("company_data"), dict) else {}
        found = resolve_telescope_value(cd.get("website_content"))
        if _website_content_is_recorded(found):
            outcome = "cached"
        else:
            try:
                # Coat-check scrapes culture_links_to_explore and saves website_content itself.
                found = resolve_telescope_value(await get_company_data(company, "website_content"))
            except ValueError as e:
                # Only a missing short_name/company_website escapes the coat-check; the hop still advances.
                _log.exception(
                    "%s | company culture page fetch\n  %s: %s\n  Moving on to %s without culture pages",
                    short_name,
                    type(e).__name__,
                    e,
                    pass_state,
                )
                found = None
            outcome = "scraped" if found else "none found"
        transition_company_state(short_name, pass_state)
        passed += 1
        if debug:
            _log.debug_index(
                func="gazer.fetch_company_culture_pages_batch",
                index=company_index,
                total=company_total,
                identifier=_gazer_company_identifier(company),
                outcome=f"passed -> {pass_state} ({outcome})",
            )
            _log.debug_detail(f"{_website_content_debug_summary(found)} company={short_name!r}")

    return {"passed": passed, "failed": 0, "total": company_total}



async def fetch_website_batch(
    batch_id: str,
    companies: List[Dict[str, Any]],
    debug: bool = False,
) -> Dict[str, int]:
    """Scrape homepage + nav_links for WEBSITE_FOUND companies (AST-701).
    Transitions each company to HOMEPAGE_READY (pass), WEBSITE_FOUND_RETRY (infra retry),
    BOT_BLOCKED_FETCH_WEBSITE (bot wall) or ERROR_FETCH_WEBSITE_UNREADABLE (fail). Returns {"passed", "failed", "errors", "skipped", "total"};
    every claimed row is scraped, so skipped stays 0 (AST-1810 removed the AST-892 split)."""
    if not await check_connectivity():
        raise ConnectionError(
            f"fetch_website_batch: no internet connectivity, aborting batch {batch_id} "
            f"({len(companies)} companies)"
        )
    if debug:
        _log.set_debug_flag(True)
    cfg = GAZER_CONFIG["fetch_website"]
    pass_state = cfg["pass_state"]
    fail_state = cfg["fail_state"]
    notes_key = ROSTER_CONFIG["company_data_keys"]["prefilter_company_notes"]
    company_total = len(companies)
    passed = failed = errors = skipped = 0

    if debug and company_total > 0:
        _log.debug_index(
            func="gazer.fetch_website_batch",
            index=1,
            total=1,
            identifier=batch_id,
            outcome=f"batch start {company_total} company/companies",
        )

    async with create_batch_browser_session() as batch_session:

        async def _fetch_one_inner(company: Dict[str, Any], company_index: int) -> None:
            nonlocal passed, failed
            short_name = company.get("short_name") or ""
            company_state = (company.get("state") or "").strip()
            original_website = (company.get("company_website") or "").strip()
            if not original_website:
                if debug:
                    _log.debug_index(
                        func="gazer.fetch_website_batch",
                        index=company_index,
                        total=company_total,
                        identifier=_gazer_company_identifier(company),
                        outcome=f"failed — no company_website -> {fail_state}",
                    )
                transition_company_state(short_name, fail_state)
                save_company_data(short_name, {notes_key: "No company_website"})
                failed += 1
                return
            scrape = await scrape_company_homepage_content(
                short_name, original_website, batch_session=batch_session
            )
            # Keep every capture — bot walls included — before routing (AST-2132).
            text_id, links_id = keep_page_scrape(company.get("candidate_id"), scrape["company_website"], scrape)
            dest = _fetch_website_fail_destination(
                company_state, scrape.get("error") or "", cfg, scrape.get("visible_text") or "",
            )
            if dest:
                reason = scrape.get("error") or "bot wall"
                if debug:
                    _log.debug_index(
                        func="gazer.fetch_website_batch",
                        index=company_index,
                        total=company_total,
                        identifier=_gazer_company_identifier(company),
                        outcome=f"failed — {reason!s} -> {dest}",
                    )
                    _log.debug_detail(f"company_website={original_website!r}")
                transition_company_state(short_name, dest)
                save_company_data(short_name, {notes_key: reason})
                failed += 1
                return
            canonical = scrape["company_website"]
            visible_text = scrape["visible_text"]
            nav_links = scrape.get("enumerated_nav_links") or ""
            nav_count = len([ln for ln in nav_links.splitlines() if ln.strip()]) if nav_links else 0
            redirect = "yes" if canonical != original_website else "no"
            data_to_save: Dict[str, Any] = {"homepage_text": text_id}
            if links_id:
                data_to_save["nav_links"] = links_id
            save_company_data(short_name, data_to_save)
            transition_company_state(short_name, pass_state)
            _log.info("%s | company %s: %s (batch: %s)", short_name, "homepage kept", pass_state, batch_id)
            passed += 1
            if debug:
                _log.debug_index(
                    func="gazer.fetch_website_batch",
                    index=company_index,
                    total=company_total,
                    identifier=_gazer_company_identifier(company),
                    outcome=(
                        f"passed -> {pass_state} ({len(visible_text)} chars "
                        f"redirect={redirect} nav={nav_count} links)"
                    ),
                )
                _log.debug_detail(
                    f"company_website={original_website!r} canonical={canonical!r} "
                    f"homepage_chars={len(visible_text)} nav_links={nav_count}"
                )

        results = await asyncio.gather(
            *[_fetch_one_inner(c, ci) for ci, c in enumerate(companies, start=1)],
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, BaseException):
                errors += 1
                _log.exception(
                    "fetch_website_batch unhandled error batch_id=%s: %s",
                    batch_id,
                    r,
                    exc_info=r,
                )

    work_total = passed + failed + errors
    if debug:
        _log.debug_detail(
            f"summary passed={passed} failed={failed} errors={errors} skipped={skipped} "
            f"total={work_total} pass_state={pass_state!r} fail_state={fail_state!r}"
        )
    return {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "total": work_total,
    }


async def fetch_job_pages_batch(
    batch_id: str,
    companies: List[Dict[str, Any]],
    debug: bool = False,
) -> Dict[str, int]:
    """Scrape possible_joblist_links (refresh: upsert per URL, AST-1995) for PREFILTER_PASSED companies (AST-719).
    Transitions each company to PJL_READY (pass), BOT_BLOCKED_FETCH_JOB_PAGES (bot wall on every
    PJL, no prior capture) or ERROR_FETCH_JOB_PAGES_UNREADABLE (fail).
    Returns {"passed": N, "failed": N, "total": N}."""
    if not await check_connectivity():
        raise ConnectionError(
            f"fetch_job_pages_batch: no internet connectivity, aborting batch {batch_id} "
            f"({len(companies)} companies)"
        )
    if debug:
        _log.set_debug_flag(True)
    cfg = GAZER_CONFIG["fetch_job_pages"]
    pass_state = cfg["pass_state"]
    fail_state = cfg["fail_state"]
    bot_state = cfg["bot_blocked_state"]
    notes_key = ROSTER_CONFIG["company_data_keys"]["prefilter_company_notes"]
    company_total = len(companies)
    passed = failed = 0

    if debug and company_total > 0:
        _log.debug_index(
            func="gazer.fetch_job_pages_batch",
            index=1,
            total=1,
            identifier=batch_id,
            outcome=f"batch start {company_total} company/companies",
        )

    async with create_browser_context() as browser_context:

        async def _fetch_one(company: Dict[str, Any], company_index: int) -> None:
            nonlocal passed, failed
            short_name = company.get("short_name") or ""
            cd = company.get("company_data") or {}
            candidate_id = company.get("candidate_id")
            candidate_urls = cd.get("possible_joblist_links") or []
            if not candidate_urls:
                _log.warning("[%s] fetch_job_pages: no possible_joblist_links", short_name)
                if debug:
                    _log.debug_index(
                        func="gazer.fetch_job_pages_batch",
                        index=company_index,
                        total=company_total,
                        identifier=_gazer_company_identifier(company),
                        outcome=f"failed — no candidate URLs -> {fail_state}",
                    )
                transition_company_state(short_name, fail_state)
                failed += 1
                return

            pjl_pages = list(cd.get("pjl_scrape_pages") or [])

            walled = False
            # AST-1995: every candidate is re-scraped each run — no already-scraped skip.
            for url_idx, url in enumerate(candidate_urls, start=1):
                record = await _scrape_pjl_page(url, browser_context, debug=debug)
                text_id, links_id = keep_page_scrape(candidate_id, record["url"], record)
                # Row ids ride on the record for the PJL merge (AST-2134 reshapes pjl_scrape_pages to {url, id}).
                record = {**record, "visible_text_id": text_id, "page_links_id": links_id}
                # A bot wall is not page content: drop it like a failed scrape so the prior capture survives.
                if not record.get("error") and is_bot_wall(record.get("visible_text") or ""):
                    record = {**record, "error": "bot wall"}
                    walled = True
                if debug:
                    err = record.get("error")
                    chars = len(record.get("visible_text") or "")
                    nav_count = len(record.get("page_links") or [])
                    if err:
                        outcome = f"error={err!r}"
                    else:
                        outcome = f"scraped visible_chars={chars} nav_links={nav_count}"
                    _log.debug_index(
                        func="gazer.fetch_job_pages_batch",
                        index=url_idx,
                        total=len(candidate_urls) or 1,
                        identifier=short_name,
                        outcome=f"pjl url {url!r} {outcome}",
                    )
                    enum_nav = record.get("enumerated_nav_links") or ""
                    if enum_nav:
                        _log.debug_detail(
                            f"enumerated_nav_chars={len(enum_nav)} collapsed_visible_chars={chars}"
                        )
                pjl_pages = _merge_pjl_scrape_record(pjl_pages, record)

            save_company_data(
                short_name,
                {
                    "pjl_scrape_pages": pjl_pages,
                    # Derived on read from pjl_scrape_pages (AST-2134); None clears copies written before AST-2130.
                    "pjl_assembled_content": None,
                    "pjl_nav_links": None,
                },
            )

            if pjl_pages:
                transition_company_state(short_name, pass_state)
                passed += 1
                _log.info(
                    "%s | company %s: %s (batch: %s)",
                    short_name, "job pages kept", f"{len(pjl_pages)} page(s) -> {pass_state}", batch_id,
                )
                if debug:
                    _log.debug_index(
                        func="gazer.fetch_job_pages_batch",
                        index=company_index,
                        total=company_total,
                        identifier=_gazer_company_identifier(company),
                        outcome=(
                            f"passed -> {pass_state} ({len(pjl_pages)} pages "
                            f"scraped={len(candidate_urls)})"
                        ),
                    )
            else:
                dest = bot_state if walled else fail_state
                transition_company_state(short_name, dest)
                save_company_data(
                    short_name,
                    {notes_key: "fetch_job_pages: bot wall on every PJL" if walled
                     else "fetch_job_pages: all PJL scrapes failed"},
                )
                failed += 1
                if debug:
                    _log.debug_index(
                        func="gazer.fetch_job_pages_batch",
                        index=company_index,
                        total=company_total,
                        identifier=_gazer_company_identifier(company),
                        outcome=f"failed — no storable PJL content -> {dest}",
                    )

        await asyncio.gather(
            *[_fetch_one(c, ci) for ci, c in enumerate(companies, start=1)],
            return_exceptions=False,
        )

    if debug:
        _log.debug_detail(
            f"summary passed={passed} failed={failed} total={company_total} "
            f"pass_state={pass_state!r} fail_state={fail_state!r}"
        )
    return {"passed": passed, "failed": failed, "total": len(companies)}


def _compiled_title_patterns(ctx: Dict[str, Any]) -> List[Any]:
    """Parse contact.title_patterns (newline-delimited regexes). Skip invalid lines; empty / missing => []."""
    cd = ctx.get("candidate_data") if isinstance(ctx.get("candidate_data"), dict) else ctx
    if not isinstance(cd, dict):
        return []
    contact = cd.get("contact") or {}
    if not isinstance(contact, dict):
        return []
    raw = contact.get("title_patterns") or contact.get("TITLE_PATTERNS") or ""
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
    if debug:
        _log.set_debug_flag(True)
    job_total = len(jobs)
    pattern_count = len(patterns)
    if debug and job_total:
        _log.debug_index(
            func="gazer.validate_title_batch",
            index=1,
            total=1,
            identifier=batch_id,
            outcome=f"batch start {job_total} job(s) pattern_count={pattern_count}",
        )
    passed = failed = 0
    for ji, job in enumerate(jobs, start=1):
        aid = job.get("astral_job_id", "")
        # AST-1152 / AST-1704: meteorite track (source SoT) never gets roster title-pattern outcomes.
        if (job.get("source") or "").strip() == SOURCE_ENTITY_TYPE_METEORITE:
            if debug:
                _log.debug_index(
                    func="gazer.validate_title_batch",
                    index=ji,
                    total=job_total,
                    identifier=_gazer_job_identifier(job),
                    outcome="skipped — meteorite company (no title-pattern screen)",
                )
            continue
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
                _log.debug_index(
                    func="gazer.validate_title_batch",
                    index=ji,
                    total=job_total,
                    identifier=_gazer_job_identifier(job),
                    outcome=f"passed -> {pass_state}",
                )
                _log.debug_detail(
                    f"raw_listing_chars={len(raw_listing)} patterns={pattern_count} "
                    f"permissive={not patterns}"
                )
        else:
            transition_job_state([aid], fail_state)
            failed += 1
            if debug:
                _log.debug_index(
                    func="gazer.validate_title_batch",
                    index=ji,
                    total=job_total,
                    identifier=_gazer_job_identifier(job),
                    outcome=f"failed -> {fail_state}",
                )
                _log.debug_detail(
                    f"raw_listing_chars={len(raw_listing)} patterns={pattern_count} "
                    f"permissive={not patterns}"
                )
    if debug:
        _log.debug_detail(f"summary passed={passed} failed={failed} total={job_total}")
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


# ---- Contact-task scrape (AST-1516) ----

async def contact_task_gazer_scrape(
    astral_candidate_id: str,
    param: str,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """Fetch visible text + links + blocked/ok/closed/missing for one URL (no job create)."""
    log = get_logger(__name__)
    log.set_debug_flag(debug)

    def _fail(error: str, url: str = "") -> Dict[str, Any]:
        row: Dict[str, Any] = {"ok": False, "error": error, "task_key": "gazer_scrape"}
        if url:
            row["url"] = url
        if debug:
            log.debug_index(
                func="gazer.contact_task_gazer_scrape",
                index=1,
                total=1,
                identifier=(url or error)[:80],
                outcome=f"failed error={error}",
            )
            if url:
                log.debug_detail(f"final_url= visible_chars=0 links_count=0")
        return row

    url = (param or "").strip()
    if not url:
        return _fail("url_required")
    if "://" not in url:
        url = f"https://{url.lstrip('/')}"

    if not await check_connectivity():
        return _fail("no_connectivity", url)

    try:
        async with create_browser_context() as browser_context:
            page = await get_page(browser_context, url)
            try:
                raw = await extract_page_scrape_contract(page)
            finally:
                await close_page(page)
    except Exception as exc:
        log.warning("[gazer] contact_task_gazer_scrape failed url=%s: %s", url[:120], exc)
        return _fail(str(exc), url)

    visible_text = collapse_consecutive_blank_lines(raw.get("visible_text") or "")
    links = list(raw.get("nav_urls") or [])
    final_url = (raw.get("final_url") or url).strip() or url
    classification = _classify_jd(visible_text)
    page_status = _CONTACT_PAGE_STATUS.get(classification, "missing")

    if debug:
        log.debug_index(
            func="gazer.contact_task_gazer_scrape",
            index=1,
            total=1,
            identifier=url[:80],
            outcome=f"ok page_status={page_status}",
        )
        log.debug_detail(
            f"final_url={final_url!r} visible_chars={len(visible_text)} "
            f"links_count={len(links)}"
        )
        for line in truncate_debug_content(visible_text):
            log.debug_detail(line)

    return {
        "ok": True,
        "task_key": "gazer_scrape",
        "astral_candidate_id": (astral_candidate_id or "").strip(),
        "url": url,
        "final_url": final_url,
        "visible_text": visible_text,
        "links": links,
        "page_status": page_status,
        "classification": classification,
    }


# ---- Process batch (scrape -> parse -> ingest -> record) ----

def _log_listing_dedupe_trace(
    log: Any,
    company: str,
    raw_job_listings: List[str],
    title_matchers: Optional[List[Any]],
) -> None:
    """Debug-only: mirror ingest_jobs dedupe/title filter without inserting (AST-622)."""
    cap = 25
    for li, raw in enumerate(raw_job_listings):
        if li >= cap:
            log.debug_detail(f"... {len(raw_job_listings) - cap} more listings omitted from dedupe trace")
            break
        if raw_job_listing_is_duplicate(company, raw):
            log.debug_detail(f"listing {li + 1}: dedupe hit (duplicate)")
            continue
        if title_matchers and not any(m.search(raw) for m in title_matchers):
            log.debug_detail(f"listing {li + 1}: title filter miss (invalid_title)")
            continue
        log.debug_detail(f"listing {li + 1}: dedupe miss (would insert)")


async def process_gazer_batch(
    batch_id: str,
    companies: List[Dict[str, Any]],
    debug: bool = False,
    ctx: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
    """Scrape each company, parse job list, ingest via tracker, record scan outcome. Returns list of outcome dicts (short_name, status, message, new, duplicates, title_mismatch)."""
    if not await check_connectivity():
        raise ConnectionError(f"process_gazer_batch: no internet connectivity, aborting batch {batch_id} ({len(companies)} companies)")
    if debug:
        _log.set_debug_flag(True)
    company_total = len(companies)
    if debug and company_total:
        _log.debug_index(
            func="gazer.process_gazer_batch",
            index=1,
            total=1,
            identifier=batch_id,
            outcome=f"batch start {company_total} company/companies",
        )
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
    scrape_fail_logged: set[str] = set()
    if debug:
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                sn, js = to_scrape[i]
                scrape_fail_logged.add(sn)
                _log.debug_index(
                    func="gazer.process_gazer_batch",
                    index=i + 1,
                    total=len(to_scrape),
                    identifier=_gazer_company_identifier({"short_name": sn}),
                    outcome=f"scrape failed: {r!s}",
                )
                _log.debug_detail(f"job_site={js!r}")
    results_by_short_name: Dict[str, Tuple[str, str, str]] = {}
    # Real scrape failure reason per company, kept regardless of debug (AST-1997).
    scrape_errors: Dict[str, str] = {}
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            sn, _ = to_scrape[i]
            # Bare exceptions (e.g. asyncio.TimeoutError()) have empty str(); drop the trailing ": ".
            scrape_errors[sn] = f"Scrape failed: {type(r).__name__}: {r}" if str(r) else f"Scrape failed: {type(r).__name__}"
            continue
        short_name, job_site, page_html = r
        results_by_short_name[short_name] = (short_name, job_site, page_html)

    scan_completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    outcomes: List[Dict[str, Any]] = []

    for ci, c in enumerate(companies, start=1):
        short_name = c.get("short_name", "")
        if not short_name:
            continue

        if short_name not in results_by_short_name:
            if debug and short_name not in scrape_fail_logged:
                _log.debug_index(
                    func="gazer.process_gazer_batch",
                    index=ci,
                    total=company_total,
                    identifier=_gazer_company_identifier(c),
                    outcome="failure — scrape failed",
                )
                _log.debug_detail(f"job_site={(c.get('job_site') or '').strip()!r}")
            # Only blank-job_site companies reach here without a scrape error (never added to to_scrape).
            failure_message = scrape_errors.get(short_name, "No job_site to scrape")
            record_to_company_job_scan(
                batch_id, short_name, scan_completed_at,
                total_found=None, new=None, duplicates=None,
                status="failure", failure_message=failure_message,
            )
            outcomes.append({"short_name": short_name, "status": "failure", "message": failure_message, "new": None, "duplicates": None})
            continue

        _, job_site, page_html = results_by_short_name[short_name]
        if debug:
            _log.debug_index(
                func="gazer.process_gazer_batch",
                index=ci,
                total=company_total,
                identifier=_gazer_company_identifier(c),
                outcome="scrape ok",
            )
            _log.debug_detail(f"job_site={job_site!r}")
        raw_job_listings: List[str] = []
        parse_instructions = await get_company_data(
            c, ROSTER_CONFIG["company_data_keys"]["parse_instructions"]
        )

        if not parse_instructions:
            if debug:
                _log.debug_index(
                    func="gazer.process_gazer_batch",
                    index=ci,
                    total=company_total,
                    identifier=_gazer_company_identifier(c),
                    outcome="failure — no parse_instructions",
                )
                _log.debug_detail("re-run find_job_page")
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
        if debug:
            _log.debug_detail(
                f"extracted_listings={len(raw_job_listings)} container={container!r} job_tag={job_tag!r} "
                f"container_index={container_index}"
            )
        patterns = _compiled_title_patterns(ctx or {})
        title_matchers = patterns or None

        try:
            if debug and raw_job_listings:
                _log.debug_detail(f"dedupe trace for {short_name} ({len(raw_job_listings)} listing(s))")
                _log_listing_dedupe_trace(_log, short_name, raw_job_listings, title_matchers)
            result = ingest_jobs(short_name, batch_id, raw_job_listings, title_matchers=title_matchers)
            total_found = len(raw_job_listings)
            new_count = result.get("new", 0)
            dup_count = result.get("duplicates", 0)
            # Canonical ingest_jobs key invalid_title (board-ingest parity); legacy return dict may still use title_mismatch.
            title_mismatch_count = result.get("invalid_title", result.get("title_mismatch", 0))
            if debug:
                _log.debug_index(
                    func="gazer.process_gazer_batch",
                    index=ci,
                    total=company_total,
                    identifier=_gazer_company_identifier(c),
                    outcome=(
                        f"success ingest new={new_count} duplicates={dup_count} "
                        f"invalid_title={title_mismatch_count}"
                    ),
                )
                _log.debug_detail(f"total_found={total_found} scan_status=success")
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
            if debug:
                _log.debug_index(
                    func="gazer.process_gazer_batch",
                    index=ci,
                    total=company_total,
                    identifier=_gazer_company_identifier(c),
                    outcome=f"failure — ingest_error: {e!s}",
                )
                _log.debug_detail(f"extracted_listings={len(raw_job_listings)}")
            record_to_company_job_scan(
                batch_id, short_name, scan_completed_at,
                total_found=len(raw_job_listings), new=None, duplicates=None,
                status="failure", failure_message=str(e),
            )
            outcomes.append({"short_name": short_name, "status": "failure", "message": f"ingest_error: {e}", "new": None, "duplicates": None})

    if debug:
        success_ct = sum(1 for o in outcomes if o.get("status") == "success")
        _log.debug_detail(
            f"summary companies={company_total} success={success_ct} failure={company_total - success_ct}"
        )

    return outcomes


# ---------------------------------------------------------------------------
# AST-1061: gazer reads email → meteorite create (Playwright + dedupe)
# ---------------------------------------------------------------------------


def _meteorite_email_candidate_links(html: str) -> List[str]:
    """Ordered unique http(s) hrefs from html, minus METEORITE_EMAIL_INGEST_CONFIG excludes."""
    # B1 lazy import: bs4 only on the email-ingest path.
    from bs4 import BeautifulSoup

    cfg = METEORITE_EMAIL_INGEST_CONFIG
    schemes = {s.casefold() for s in cfg["link_schemes"]}
    excludes = tuple(s.casefold() for s in cfg["link_exclude_substrings"])
    allows = tuple(s.casefold() for s in cfg["link_allow_substrings"])
    soup = BeautifulSoup(html or "", "html.parser")
    seen: set[str] = set()
    out: List[str] = []
    for tag in soup.find_all("a", href=True):
        href = (tag.get("href") or "").strip()
        if not href or href in seen:
            continue
        parsed = urlparse(href)
        scheme = (parsed.scheme or "").casefold()
        if scheme not in schemes:
            continue
        low = href.casefold()
        if any(frag in low for frag in excludes):
            continue
        # Empty allow = no filter (AST-1132); non-empty requires ≥1 allow substring.
        if allows and not any(frag in low for frag in allows):
            continue
        seen.add(href)
        out.append(href)
    return out


def _meteorite_email_body_text(html: str) -> str:
    """Plain visible-ish text from stripped email HTML for body/forward shapes."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html or "", "html.parser")
    return (soup.get_text("\n", strip=True) or "").strip()


async def _meteorite_fetch_link_visible_text(
    url: str, *, debug: bool = False
) -> Tuple[str, str]:
    """Return (visible_text, final_url) via get_visible_text(..., return_final_url=True)."""
    result = await get_visible_text(url=url, return_final_url=True)
    if isinstance(result, tuple):
        text, final_url = result
        return (text or ""), (final_url or url)
    return (result or ""), url


async def ingest_meteorite_jobs_from_email_html(
    candidate_id: str,
    html: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    """Classify email HTML → optional Playwright → dedupe → create_meteorite_job.

    Returns:
      {
        "astral_candidate_id": str,
        "mode": "links" | "body",
        "created": [ create_meteorite_job result dicts ... ],
        "skipped": [ {"reason": str, "url": Optional[str], "matched_company_job_id": Optional[str]} ... ],
      }
    """
    candidate_id = (candidate_id or "").strip()
    if not candidate_id:
        raise ValueError("candidate_id is required")
    if not isinstance(html, str) or not html.strip():
        raise ValueError("html is required")

    # AST-1131: normalize paste/list HTML before link discovery (idempotent with inbox strip).
    html = normalize_pasted_list_email_html(html)

    log = get_logger(__name__)
    log.set_debug_flag(debug)
    cfg = METEORITE_EMAIL_INGEST_CONFIG
    min_chars = int(cfg["min_jd_chars"])
    created: List[dict[str, Any]] = []
    skipped: List[dict[str, Any]] = []

    links = _meteorite_email_candidate_links(html)
    if links:
        mode = "links"
        n = len(links)

        async def _one(i: int, url: str) -> None:
            try:
                text, final_url = await _meteorite_fetch_link_visible_text(url, debug=debug)
            except Exception as e:
                log.warning("[gazer] meteorite email Playwright failed url=%s: %s", url[:120], e)
                skipped.append({
                    "reason": "playwright_error",
                    "url": url,
                    "matched_company_job_id": None,
                })
                if debug:
                    log.debug_index(
                        func="gazer.meteorite_email_ingest",
                        index=i,
                        total=n,
                        identifier=url[:80],
                        outcome="skipped-error",
                    )
                    log.debug_detail(f"reason=playwright_error error={e!s}")
                return

            link = (final_url or url).strip() or url
            # AST-1132 Gate A: final URL may redirect onto excluded hosts/paths.
            low_link = link.casefold()
            excludes = tuple(s.casefold() for s in cfg["link_exclude_substrings"])
            if any(frag in low_link for frag in excludes):
                skipped.append({
                    "reason": "excluded_link",
                    "url": link,
                    "matched_company_job_id": None,
                })
                if debug:
                    log.debug_index(
                        func="gazer.meteorite_email_ingest",
                        index=i,
                        total=n,
                        identifier=link[:80],
                        outcome="skipped-excluded",
                    )
                    log.debug_detail("reason=excluded_link")
                return

            # AST-1132 Gate B: long-enough SVG/spec pages still skip create.
            markers = tuple(s.casefold() for s in cfg["non_job_visible_substrings"])
            hay_vis = (text or "").casefold()
            if markers and any(m in hay_vis for m in markers):
                skipped.append({
                    "reason": "non_job_page",
                    "url": link,
                    "matched_company_job_id": None,
                })
                if debug:
                    log.debug_index(
                        func="gazer.meteorite_email_ingest",
                        index=i,
                        total=n,
                        identifier=link[:80],
                        outcome="skipped-non-job",
                    )
                    log.debug_detail("reason=non_job_page")
                return

            haystack = f"{link}\n{text}"
            if job_link_exists_for_candidate(candidate_id, link):
                skipped.append({
                    "reason": "known_job_link",
                    "url": link,
                    "matched_company_job_id": None,
                })
                if debug:
                    log.debug_index(
                        func="gazer.meteorite_email_ingest",
                        index=i,
                        total=n,
                        identifier=link[:80],
                        outcome="skipped-duplicate",
                    )
                    log.debug_detail("reason=known_job_link")
                return

            matched = text_matches_known_company_job_id_for_candidate(
                candidate_id, haystack
            )
            if matched:
                skipped.append({
                    "reason": "known_company_job_id",
                    "url": link,
                    "matched_company_job_id": matched,
                })
                if debug:
                    log.debug_index(
                        func="gazer.meteorite_email_ingest",
                        index=i,
                        total=n,
                        identifier=link[:80],
                        outcome="skipped-duplicate",
                    )
                    log.debug_detail(f"reason=known_company_job_id matched={matched}")
                return

            if len((text or "").strip()) < min_chars:
                skipped.append({
                    "reason": "jd_too_short",
                    "url": link,
                    "matched_company_job_id": None,
                })
                if debug:
                    log.debug_index(
                        func="gazer.meteorite_email_ingest",
                        index=i,
                        total=n,
                        identifier=link[:80],
                        outcome="skipped-short",
                    )
                    log.debug_detail(f"reason=jd_too_short len={len((text or '').strip())}")
                return

            if debug:
                log.debug_index(
                    func="gazer.meteorite_email_ingest",
                    index=i,
                    total=n,
                    identifier=link[:80],
                    outcome="found",
                )
                log.debug_detail(f"visible_text_len={len(text or '')}")

            result = create_meteorite_job(
                candidate_id, text, job_link=link, debug=debug
            )
            created.append(result)
            if debug:
                log.debug_index(
                    func="gazer.meteorite_email_ingest",
                    index=i,
                    total=n,
                    identifier=link[:80],
                    outcome="recorded",
                )
                log.debug_detail(f"astral_job_id={result.get('astral_job_id')}")

        await asyncio.gather(*[_one(i, url) for i, url in enumerate(links, start=1)])
    else:
        mode = "body"
        text = _meteorite_email_body_text(html)
        if not text and not html.strip():
            raise ValueError("email body is empty")
        if not text:
            text = html.strip()

        matched = text_matches_known_company_job_id_for_candidate(candidate_id, text)
        if matched:
            skipped.append({
                "reason": "known_company_job_id",
                "url": None,
                "matched_company_job_id": matched,
            })
            if debug:
                log.debug_index(
                    func="gazer.meteorite_email_ingest",
                    index=1,
                    total=1,
                    identifier=candidate_id[:80],
                    outcome="skipped-duplicate",
                )
                log.debug_detail(f"reason=known_company_job_id matched={matched}")
        elif len(text.strip()) < min_chars:
            skipped.append({
                "reason": "jd_too_short",
                "url": None,
                "matched_company_job_id": None,
            })
            if debug:
                log.debug_index(
                    func="gazer.meteorite_email_ingest",
                    index=1,
                    total=1,
                    identifier=candidate_id[:80],
                    outcome="skipped-short",
                )
                log.debug_detail(f"reason=jd_too_short len={len(text.strip())}")
        else:
            # Prefer stripped HTML JD (subject wrapper) when present.
            jd_payload = html if html.strip() else text
            if debug:
                log.debug_index(
                    func="gazer.meteorite_email_ingest",
                    index=1,
                    total=1,
                    identifier=candidate_id[:80],
                    outcome="found",
                )
                log.debug_detail(f"mode=body jd_len={len(jd_payload)}")
            result = create_meteorite_job(
                candidate_id, jd_payload, job_link=None, debug=debug
            )
            created.append(result)
            if debug:
                log.debug_index(
                    func="gazer.meteorite_email_ingest",
                    index=1,
                    total=1,
                    identifier=candidate_id[:80],
                    outcome="recorded",
                )
                log.debug_detail(f"astral_job_id={result.get('astral_job_id')}")

    return {
        "astral_candidate_id": candidate_id,
        "mode": mode,
        "created": created,
        "skipped": skipped,
    }


def ingest_meteorite_jobs_from_email_html_sync(
    candidate_id: str,
    html: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    """Sync wrapper for Flask/inbox callers (run_one_shot)."""
    return run_one_shot(
        ingest_meteorite_jobs_from_email_html(candidate_id, html, debug=debug)
    )
