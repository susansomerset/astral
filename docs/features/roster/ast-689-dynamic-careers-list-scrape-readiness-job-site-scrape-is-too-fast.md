<!-- linear-archive: AST-689 archived 2026-06-23 -->

## Linear archive (AST-689)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-689/dynamic-careers-list-scrape-readiness-job-site-scrape-is-too-fast  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-684 — Job Site scrape is too fast?  
**Blocked by / blocks / related:** parent: AST-684; blocks: AST-692

### Description

## What this implements

Before visible-text extraction on every roster Playwright path that feeds **select_job_page**, wait for dynamic careers-list content to render (config-driven readiness). Applies to **find_job_page** / **jobs_found_process_job_site** and any other scrape that supplies page text to **select_job_page**. Add debug logging per AST-538 contract when readiness fails or times out.

## Acceptance criteria

1. PagerDuty repro (`careers.pagerduty.com/jobs/search`, batch `select_job_page-54d02162-370a-4548-b166-664bc2350bbb`): scraped visible text includes job titles present in the DOM before **select_job_page** runs.
2. Readiness gate applies to **all** roster scrapes that feed **select_job_page**, not only PagerDuty.
3. Config-driven wait/selector (no hard-coded site list); tunable via `config.py` / env as established for roster Playwright.
4. Debug log lines when readiness fails (per AST-538 shared helper / contract).
5. Automated regression test covers readiness path (mock or fixture acceptable if it asserts gate behavior).

## Boundaries

* Does **not** define **JOBSITE_SCRAPE_ISSUE** response type or company state — sibling AST-685 (blocked downstream).
* Does **not** change **select_job_page** prompt semantics beyond receiving complete scrape text.
* Out of scope: AST-666 hang class; gazer-only **load_all_jobs** unless wired into roster discovery scrape path.

## Notes for planning

* Hot files: `src/core/roster.py`, `src/external/playwright.py`, `src/utils/config.py`.
* **load_all_jobs** exists in gazer path; roster discovery may need analogous wait on careers search pages.
* Follow ASTRAL_CODE_RULES layer boundaries; plan in epic worktree on `sub/AST-684/<this-ticket>`.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-684-job-site-scrape-is-too-fast`, child `sub/AST-684/<child-id>-dynamic-scrape-readiness`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-16T00:40:18.966Z
**Diff:** `origin/dev...origin/sub/AST-684/AST-689-dynamic-scrape-readiness` @ `7e8984c`
**Doc:** `docs/features/roster/ast-689-dynamic-careers-list-scrape-readiness-job-site-scrape-is-too-fast.md` (Radia review section)

**Verdict:** Clean — no **fix-now** or **discuss**.

### Plan fidelity
- Stage 1–3 match combined plan: config block + env overrides, `wait_for_careers_list_readiness` in external (no log), single call site in `_fetch_job_links_content` before extract.
- AST-692 boundary respected — timeout proceeds best-effort; no **JOBSITE_SCRAPE_ISSUE** state.
- Betty manifest covers ready / timeout / integration + existing scrape-debug mock.

### §5f debug
Per-page `debug_index` + `debug_detail` when `debug=True` only; universal `index N/M`, URL identifier, outcome + readiness metrics; failure detail notes AST-692 ownership.

### Advisory
- Sub tip diff vs dev includes sibling AST-684 children; AST-689 product commits (`4cfeec0`, `676001b`, `94021d6`) stay in plan scope.
- `except Exception: pass` on bad selector counts — plan-specified; acceptable per §5b.
- Generic listing selectors may false-ready on nav links — tune config if staging shows false positives.

#### chuckles — 2026-06-16T00:37:06.963Z
## QA test manifest (AST-689)

**Publish ref:** `origin/sub/AST-684/AST-689-dynamic-scrape-readiness` @ `e7c579c`
**Tests SHA:** `7d915e9`

1. `tests/component/core/test_roster.py::TestAst689ScrapeReadiness::test_wait_for_careers_list_readiness_ready_on_listing_hits` — readiness helper exits **ready** on listing selector hits
2. `tests/component/core/test_roster.py::TestAst689ScrapeReadiness::test_wait_for_careers_list_readiness_timeout` — bounded wait returns **timeout** when listings never appear
3. `tests/component/core/test_roster.py::TestAst689ScrapeReadiness::test_fetch_job_links_content_calls_readiness` — `_fetch_job_links_content` invokes readiness before `extract_visible_text`
4. `tests/component/core/test_roster.py::TestRosterCoverageGaps::test_fetch_job_links_content_dom_new_links_and_scrape_debug` — existing PJL scrape debug test (readiness mock; fixes ~21s gate wait)

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst689ScrapeReadiness \
  tests/component/core/test_roster.py::TestRosterCoverageGaps::test_fetch_job_links_content_dom_new_links_and_scrape_debug
```

**Broken / obsolete (fixed this pass):** `test_fetch_job_links_content_dom_new_links_and_scrape_debug` — without readiness mock, real gate waits `max_wait_ms=20000` per page.

**Bible shasum (publish ref):**
- `docs/test-bible/core/roster.md` → `2785b3c28a5cb0541dddbb745273e9f14fff2037`

— Betty

#### hedy — 2026-06-16T00:31:02.396Z
Plan doc: `https://github.com/susansomerset/astral/blob/sub/AST-684/AST-689-dynamic-scrape-readiness/docs/features/roster/ast-689-dynamic-careers-list-scrape-readiness-job-site-scrape-is-too-fast.md`

**Self-assessment**
- **Scope:** Single-Component — `config.py` scrape_readiness block, one Playwright helper, and `_fetch_job_links_content` (the single funnel for all PJL scrapes feeding select_job_page).
- **Conf:** Medium — new readiness heuristics, but integration is one call site and load_all_jobs / AST-538 debug patterns already exist in roster.
- **Risk:** Medium — overly long waits could slow every PJL scrape; mitigated by early exit on selector hits, 20s cap, env overrides, and Betty regression tests on gate behavior.

---

# AST-689 — Dynamic careers-list scrape readiness (Job Site scrape is too fast?)

**Linear:** [AST-689 — Dynamic careers-list scrape readiness (Job Site scrape is too fast?)](https://linear.app/astralcareermatch/issue/AST-689/dynamic-careers-list-scrape-readiness-job-site-scrape-is-too-fast)

**Parent (reference only — orchestration AC):** [AST-684 — Job Site scrape is too fast?](https://linear.app/astralcareermatch/issue/AST-684/job-site-scrape-is-too-fast)

**Publish ref:** `origin/sub/AST-684/AST-689-dynamic-scrape-readiness` (origin only)

## Summary

Roster job-page discovery scrapes careers URLs with Playwright, then passes visible text to **select_job_page**. On JS-heavy listing pages (PagerDuty repro: `careers.pagerduty.com/jobs/search`), **get_page** completes on document **load** before job titles render, so Grace sees page chrome without listings and may hallucinate **JOBLIST_TITLES**. This ticket adds a **shared, config-driven readiness gate** on every roster scrape that feeds **select_job_page**, waits up to bounded limits for listing-like DOM/text, optionally triggers lazy-load scroll, and emits **AST-538** debug headers when readiness fails or times out. **JOBSITE_SCRAPE_ISSUE** response type and terminal company state are **sibling AST-692** — not implemented here.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `ROSTER_CONFIG["scrape_readiness"]` block + optional env overrides for `max_wait_ms` / `poll_interval_ms` | utils |
| `src/external/playwright.py` | New `wait_for_careers_list_readiness(page, cfg) -> dict` — bounded poll, generic listing selectors, optional `load_all_jobs` | external |
| `src/core/roster.py` | Call readiness after `get_page` inside `_fetch_job_links_content`; AST-538 debug on fail/timeout; import readiness helper | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | New readiness gate tests (mock page + `_fetch_job_links_content` integration) per Stage 4 spec |

**Out of scope:** `JOBSITE_SCRAPE_ISSUE` state/response ([AST-692](https://linear.app/astralcareermatch/issue/AST-692)), **select_job_page** prompt edits, **gazer** JD scrape paths, **`_scrape_job_site_dom`** / **parse_job_list** dispatch-only scrapes, UI, unbounded waits, per-company hardcoded selectors.

---

## Stage 1: Config — `ROSTER_CONFIG["scrape_readiness"]`

**Done when:** Readiness knobs are readable from `config.py`; defaults are safe for fast-loading static sites (short total wait, low bar); env can override primary timeouts without code edits.

1. In `src/utils/config.py`, inside `ROSTER_CONFIG` (after `"locate_job_page"` block, before `"gaze"`), add:

```python
"scrape_readiness": {
    "max_wait_ms": 20000,
    "poll_interval_ms": 500,
    "stability_polls": 2,
    "min_visible_chars": 400,
    "min_listing_hits": 1,
    "run_load_all_jobs": True,
    "load_all_jobs_after_ms": 3000,
    "listing_selectors": [
        "[class*='job-list']",
        "[class*='JobList']",
        "[class*='job-listing']",
        "[class*='opening']",
        "[data-testid*='job']",
        "a[href*='/job']",
        "a[href*='/jobs/']",
        "li[class*='job']",
        "article[class*='job']",
    ],
},
```

2. Immediately below the `ROSTER_CONFIG = { ... }` closing brace (same file), add env override helper used only for scrape readiness:

```python
def roster_scrape_readiness_config() -> Dict[str, Any]:
    """Return ROSTER_CONFIG['scrape_readiness'] with optional env overrides."""
    cfg = dict(ROSTER_CONFIG.get("scrape_readiness") or {})
    for key, env_name in (
        ("max_wait_ms", "ROSTER_SCRAPE_READINESS_MAX_WAIT_MS"),
        ("poll_interval_ms", "ROSTER_SCRAPE_READINESS_POLL_INTERVAL_MS"),
    ):
        raw = os.environ.get(env_name, "").strip()
        if raw.isdigit():
            cfg[key] = int(raw)
    return cfg
```

3. Ensure `import os` already present at top of `config.py` (it is — reuse).

⚠️ **Decision:** Generic CSS selector list lives in config (not a per-site map). Tunable without redeploy via env for the two timing knobs Susan is most likely to tweak on staging.

---

## Stage 2: Playwright readiness helper

**Done when:** `wait_for_careers_list_readiness` returns a deterministic dict for ready, timeout, and empty-page cases; function has **no logging** (external layer); uses existing `load_all_jobs` when config enables it.

1. In `src/external/playwright.py`, add typed-ish return shape (plain `dict` is fine — match repo style):

```python
async def wait_for_careers_list_readiness(
    page: PageHandle,
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
```

2. Implement poll loop (pseudocode — execute literally):

   - Read `max_wait_ms`, `poll_interval_ms`, `stability_polls`, `min_visible_chars`, `min_listing_hits`, `listing_selectors`, `run_load_all_jobs`, `load_all_jobs_after_ms` from `cfg` with the defaults above if keys missing.
   - Record `started = time.monotonic()` (import `time` at module top if not present).
   - Track `stable_count = 0`, `last_len = 0`, `load_all_jobs_ran = False`.
   - Loop until elapsed ≥ `max_wait_ms`:
     - `visible_len = len((await extract_visible_text(page)).get("text") or "")`
     - `listing_hits = 0` — for each selector in `listing_selectors`, `listing_hits += await page.locator(sel).count()` (wrap each selector in try/except; skip bad selectors).
     - **Ready** when `(listing_hits >= min_listing_hits)` OR `(visible_len >= min_visible_chars and visible_len == last_len)` — increment `stable_count` on length match else reset to 0; ready when `listing_hits` threshold met OR `stable_count >= stability_polls`.
     - If not ready and `run_load_all_jobs` and not `load_all_jobs_ran` and elapsed ≥ `load_all_jobs_after_ms`: `await load_all_jobs(page, "roster")`; set `load_all_jobs_ran = True`.
     - `await page.wait_for_timeout(poll_interval_ms)`.
   - Return dict always:

```python
{
    "ready": bool,
    "outcome": "ready" | "timeout" | "empty",
    "visible_chars": int,
    "listing_hits": int,
    "wait_ms": int,
    "load_all_jobs_ran": bool,
}
```

   - Set `outcome="ready"` when loop breaks early on ready; `outcome="timeout"` when loop exhausts `max_wait_ms` without ready; `outcome="empty"` when final `visible_chars == 0` regardless of ready flag.

3. Do **not** add logger calls in this function (**ASTRAL_CODE_RULES** § external no-log).

⚠️ **Decision:** Reuse **`load_all_jobs`** (scroll + Load More) mid-wait for lazy-loaded lists — same primitive as gazer, but invoked only from this roster readiness path when config enables it.

---

## Stage 3: Wire readiness into roster PJL scrapes + debug logging

**Done when:** Every `_fetch_job_links_content` page load waits for readiness before `extract_visible_text`; debug runs emit AST-538 index headers per page with URL, outcome, char counts; non-debug runs have zero new log lines; scrape still proceeds after timeout (AST-692 owns terminal handling).

1. In `src/core/roster.py`, extend playwright import:

```python
from src.external.playwright import (
    ...
    wait_for_careers_list_readiness,
)
```

2. Extend config import:

```python
from src.utils.config import (
    ...
    roster_scrape_readiness_config,
)
```

3. In `_fetch_job_links_content`, after `pg = await get_page(browser_context, url)` and before `extract_visible_text(pg)`:

```python
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
        outcome=ready_meta.get("outcome") or ("ready" if ready_meta.get("ready") else "timeout"),
    )
    log.debug_detail(
        f"ready={ready_meta.get('ready')} visible_chars={ready_meta.get('visible_chars')} "
        f"listing_hits={ready_meta.get('listing_hits')} wait_ms={ready_meta.get('wait_ms')} "
        f"load_all_jobs_ran={ready_meta.get('load_all_jobs_ran')}"
    )
    if not ready_meta.get("ready"):
        log.debug_detail("readiness gate exhausted — proceeding with best-effort extract (AST-692 owns JOBSITE_SCRAPE_ISSUE)")
```

4. Leave the remainder of `_fetch_job_links_content` unchanged (still `extract_visible_text`, DOM, links, section assembly).

5. Do **not** wire readiness into:
   - `prefilter_company` / `get_visible_text` homepage scrape
   - `_scrape_job_site_dom` (**parse_job_list** dispatch)
   - `recheck_no_openings`
   - culture-page coat-check paths

6. Do **not** change `jobs_found_process_job_site`'s redirect-only `get_visible_text` call — assembled content for **select_job_page** already flows through `_fetch_job_links_content` which receives the readiness gate.

⚠️ **Decision:** Readiness failure does **not** abort the scrape in AST-689 — extract proceeds so AST-692 can classify incomplete shell vs titles. Debug makes the failure visible for Susan's staging repro.

---

## Stage 4: Regression test contract (Betty manifest — qa-child)

**Done when:** Component test(s) assert readiness helper behavior and `_fetch_job_links_content` invokes it; `pytest` slice green in test-child.

Betty adds to `tests/component/core/test_roster.py` (engineer does not commit test file):

1. **`TestAst689ScrapeReadiness.test_wait_for_careers_list_readiness_ready_on_listing_hits`**
   - Import `wait_for_careers_list_readiness` from `src.external.playwright`.
   - Mock `PageHandle`: first poll `locator().count()` returns 0, second returns 2; mock `extract_visible_text` returning increasing text lengths.
   - Assert `result["ready"] is True`, `result["outcome"] == "ready"`, `result["listing_hits"] >= 1`.

2. **`TestAst689ScrapeReadiness.test_wait_for_careers_list_readiness_timeout`**
   - Mock page where `listing_hits` stays 0 and visible text stays below `min_visible_chars` for entire `max_wait_ms` (use tiny `max_wait_ms=100`, `poll_interval_ms=50` in cfg dict passed to helper).
   - Assert `result["ready"] is False`, `result["outcome"] == "timeout"`.

3. **`TestAst689ScrapeReadiness.test_fetch_job_links_content_calls_readiness`**
   - Monkeypatch `roster_mod.wait_for_careers_list_readiness` with `AsyncMock(return_value={"ready": True, "outcome": "ready", "visible_chars": 500, "listing_hits": 3, "wait_ms": 100, "load_all_jobs_ran": False})`.
   - Monkeypatch `get_page`, `close_page`, `extract_visible_text`, `extract_page_dom`, `extract_site_page_list`, `parse_enumerate_array` (reuse patterns from `test_fetch_job_links_content_dom_new_links_and_scrape_debug`).
   - Call `_fetch_job_links_content([1], "1. https://acme.com/jobs", AsyncMock(), debug=True)`.
   - Assert readiness mock called once before `extract_visible_text`.

---

## Self-Assessment

**Scope:** `Single-Component` — touches `config.py` readiness block, one new external Playwright helper, and the single roster scrape funnel `_fetch_job_links_content` that feeds **select_job_page** (including **find_job_page**, **jobs_found_process_job_site**, **run_select_job_page_dispatch**, and TRY_LINKS retry).

**Conf:** `Medium` — readiness heuristics are new, but the integration surface is narrow (one call site), `load_all_jobs` already exists, and AST-538 debug patterns are established in `roster.py`.

**Risk:** `Medium` — waits that are too aggressive could slow every PJL scrape; defaults keep `max_wait_ms=20000` and early-exit on selector hit so static ATS pages should pass quickly. Wrong tuning could still add latency — mitigated by env overrides and Betty regression tests on gate behavior.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| **§1.3 DRY** | Single readiness helper in `playwright.py`; one call site in `_fetch_job_links_content`. No duplicate wait loops in `find_job_page` branches. |
| **§2.1 config** | All knobs in `ROSTER_CONFIG["scrape_readiness"]`; env overrides via `roster_scrape_readiness_config()`. No magic numbers in roster. |
| **§2.4 batch processing** | No dispatcher / claim semantics change. |
| **§2.6 state machine** | No new states or transitions (AST-692). |
| **§3.3 imports** | `roster` → `external` + `utils`; `external` imports only `utils` (+ stdlib). |
| **§3.4 Playwright** | Readiness lives in external; core orchestrates and logs. |
| **§3.5 naming** | snake_case functions; config keys lowercase. |
| **§1.5 debug** | Debug only when `debug=True` via `set_debug_flag`; external helper silent. |

No unresolved conflicts.

---

## Execution contract (for the developer agent)

- Execute stages **1 → 2 → 3 → 4** in order; one commit per stage on epic worktree; publish each to `origin/sub/AST-684/AST-689-dynamic-scrape-readiness` per **build-child** §6.
- Do **not** implement **JOBSITE_SCRAPE_ISSUE**, company state, or **select_job_page** prompt changes — blocked on **AST-692**.
- Do **not** add files beyond the table above.
- Blocking ambiguity → comment on **AST-684** parent with 🛑 template from **plan-child** §6.

---

## Boundary echo (ticket)

- **In scope:** Readiness wait + debug on all roster scrapes feeding **select_job_page**.
- **Out of scope:** **JOBSITE_SCRAPE_ISSUE** / terminal state (**AST-692**), **select_job_page** prompt semantics, **AST-666** hang class, gazer-only paths unless wired here via `_fetch_job_links_content`.

---

## Review stub (post-build — build-child §11)

| Item | Value |
|------|-------|
| **Publish ref** | `origin/sub/AST-684/AST-689-dynamic-scrape-readiness` |
| **Tip SHA** | `94021d6` |
| **Stages** | config `4cfeec0`, playwright `676001b`, roster wire `94021d6` |

---

## Radia review (2026-06-16)

**Diff:** `origin/dev...origin/sub/AST-684/AST-689-dynamic-scrape-readiness` @ `e7c579c`  
**Verdict:** Clean — no fix-now items.

### What's solid

| Stage | Check |
|-------|-------|
| 1 | `ROSTER_CONFIG["scrape_readiness"]` block + `roster_scrape_readiness_config()` env overrides match plan Stage 1 |
| 2 | `wait_for_careers_list_readiness` in `playwright.py` — bounded poll, listing selectors, optional `load_all_jobs`, deterministic return dict; no logging in external layer |
| 3 | `_fetch_job_links_content` calls readiness after `get_page` before `extract_visible_text`; AST-538 `debug_index` / `debug_detail` only when `debug=True`; proceeds on timeout (AST-692 boundary respected) |
| 4 | Betty manifest `TestAst689ScrapeReadiness` + readiness mock on existing scrape-debug test per bible |

**§5f (debug):** Per-page index headers use universal `index N/M`, URL identifier, outcome; detail lines record ready/visible_chars/listing_hits/wait_ms/load_all_jobs_ran; failure path adds best-effort note. No emission when `debug=False`.

**§5b (exceptions):** `except Exception: pass` on per-selector `locator().count()` is plan-specified (skip bad selectors); acceptable.

### Advisory

- Sub tip three-dot diff vs `origin/dev` includes sibling AST-684 children (674, 687, 681, etc.) merged on the branch — AST-689 product commits (`4cfeec0`, `676001b`, `94021d6`) stay within plan file table; no boundary smuggle in engineer commits.
- `roster_scrape_readiness_config()` is called inside the per-page loop — could hoist once before the loop; negligible cost vs Playwright I/O.
- Readiness polls call `extract_visible_text` each iteration, then `_fetch_job_links_content` extracts again — per plan; duplicate DOM walk on ready path is acceptable tradeoff for stability detection.
- Generic listing selectors may false-ready on nav/footer `a[href*='/job']` hits — inherent heuristic risk; plan Self-Assessment **Medium**; tune via config if staging repro shows false positives.

### Recommended actions

None — **resolve-child** may proceed.

---

## Resolution (resolve-child)

**Date:** 2026-06-16 (**Review Posted → User Testing**)

**Review:** Radia @ `7e8984c` — **clean**, no fix-now or discuss items.

| Item | Outcome |
|------|---------|
| **fix-now** | 0 — no product or plan doc changes required |
| **discuss** | 0 |
| **advisory** | Acknowledged — generic selector false-ready risk tunable via config; per-page config read and double extract acceptable per plan |

**§9a dry-run:** `origin/sub/AST-684/AST-689-dynamic-scrape-readiness` merges cleanly into `origin/dev` and `origin/ftr/AST-684-job-site-scrape-is-too-fast`.

**Publish tip:** `7e8984c` (`docs(AST-689): Radia review — clean`)
