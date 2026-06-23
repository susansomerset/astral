# AST-759 — Shared page scrape contract and fetch_job_pages nav-link parity

**Linear:** [AST-759 — Shared page scrape contract and fetch_job_pages nav-link parity (fetch_job_pages does not fetch nav links)](https://linear.app/astralcareermatch/issue/AST-759/shared-page-scrape-contract-and-fetch-job-pages-nav-link-parity-fetch)

**Parent (reference only — do not implement sibling scope):** [AST-753 — fetch_job_pages does not fetch nav links](https://linear.app/astralcareermatch/issue/AST-753/fetch-job-pages-does-not-fetch-nav-links)

**Publish ref:** `origin/sub/AST-753/AST-759-shared-page-scrape-fetch-job-pages-nav-links`

**Summary:** Restore one shared Playwright page-scrape contract (collapsed visible text + numbered nav-link enumeration from a single page load) and route both **fetch_website** and **fetch_job_pages** through it. Persist PJL scrape pages with normalized text and enumerated nav links; ensure **select_job_page** at **PJL_READY** receives that link material in agent live content. Fixes pattern drift Susan flagged on AST-753 without changing AST-720 dispatch routing or AST-719 additive ledger semantics.

**Depends on (Done on `origin/ftr/AST-753-fetch-job-pages-nav-links`):** AST-719 (`fetch_job_pages_batch`, `pjl_scrape_pages`, `pjl_assembled_content`, `pjl_nav_links`), AST-720 (`run_select_job_page_dispatch`, `_nav_links_for_try_links`), AST-718 (`possible_joblist_links` ledger), AST-710/715 (`collapse_consecutive_blank_lines`).

**Out of scope:** **select_job_page** routing / TRY_LINKS retry / state transitions (AST-720); monolithic **find_job_page** removal (AST-721); careers-list readiness rule changes (AST-689); Betty log-string tests; **job_site** writes on fetch (AST-673).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/playwright.py` | Add `extract_page_scrape_contract(page)` — single-load raw visible text + nav URL list | external |
| `src/core/roster.py` | Add `finalize_page_scrape_contract(...)`; refactor `scrape_company_homepage_content`, `_scrape_pjl_page`; extend `_merge_pjl_scrape_record`, `_assemble_pjl_content`; add `_build_select_job_page_live_content`; wire into `run_select_job_page_dispatch` | core |
| `src/core/gazer.py` | Update `fetch_job_pages_batch` per-URL debug outcomes (nav count + collapsed char length) | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | Shared contract collapse; PJL page record carries enumerated nav links; assembled content includes nav section; select live content includes `pjl_nav_links` |
| `tests/component/core/test_gazer.py` | `fetch_job_pages_batch` debug outcome shape (if Betty extends manifest) |

**Read-only reuse (do not duplicate):**

| Symbol | Location | Use |
|--------|----------|-----|
| `collapse_consecutive_blank_lines`, `enumerate_array`, `normalize_link`, `parse_enumerate_array` | `src/utils/formatting.py` | Blank-line normalization + numbered nav list |
| `extract_visible_text`, `extract_site_page_list`, `get_page`, `close_page`, `wait_for_careers_list_readiness` | `src/external/playwright.py` | Playwright I/O |
| `_merge_pjl_nav_links`, `_pjl_scrape_ledger_keys`, `fetch_job_pages_batch` | `src/core/gazer.py` / `src/core/roster.py` | Additive PJL persistence unchanged except data shape enrichment |
| `_nav_links_for_try_links`, `_find_job_page_from_assembled` | `src/core/roster.py` | TRY_LINK resolution — do not refactor routing |

---

## Stage 1: Shared Playwright + roster contract helpers

**Done when:** A loaded `PageHandle` can be passed through one roster entry point and returns collapsed visible text plus `enumerate_array` nav output from the same page load; external helper performs I/O only (no collapse/enumerate in external).

1. In `src/external/playwright.py`, immediately after `extract_visible_text` (~line 539), add:

   ```python
   async def extract_page_scrape_contract(page: PageHandle) -> Dict[str, Any]:
   ```

   Implementation (single page load — caller already navigated):

   - `vt = await extract_visible_text(page)`
   - `nav_urls = await extract_site_page_list(page=page, max_depth=1, verify=False) or []`
   - Return `{"visible_text": vt.get("text") or "", "nav_urls": nav_urls, "final_url": vt.get("url") or page.url}`

   **Do not** import `collapse_consecutive_blank_lines` or `enumerate_array` here (external → utils only for formatting helpers used in product contract lives in core).

2. In `src/core/roster.py`, after existing formatting imports, add a small pure helper and async wrapper:

   ```python
   def finalize_page_scrape_contract(raw: Dict[str, Any]) -> Dict[str, Any]:
   ```

   - Input keys: `visible_text`, `nav_urls`, `final_url` (optional), passthrough `error` if present.
   - Apply `collapse_consecutive_blank_lines` to `visible_text`; store result in `visible_text`.
   - If `nav_urls` non-empty: set `enumerated_nav_links = enumerate_array("", nav_urls)` else `""`.
   - Return dict with at least: `visible_text`, `enumerated_nav_links`, `nav_urls`, `final_url`.

   ```python
   async def scrape_loaded_page_contract(page, *, debug: bool = False) -> Dict[str, Any]:
   ```

   - Call `extract_page_scrape_contract(page)` then `finalize_page_scrape_contract`.
   - When `debug=True`, emit one AST-538 `debug_index` with `func="roster.scrape_loaded_page_contract"`, `identifier=final_url or page.url`, outcome `visible_chars={len(visible_text)} nav_links={len(nav_urls)}` plus `debug_detail` with collapsed char count.

3. **Do not** wire callers yet — helpers only in this stage.

⚠️ **Decision:** Product contract (collapse + enumerate) lives in **core** (`finalize_page_scrape_contract`); **external** returns raw scrape payload only. Matches Susan’s “reusable Playwright function” intent while honoring §2.5 bright line and §3.3 import rules.

---

## Stage 2: Route fetch_website and fetch_job_pages through shared contract

**Done when:** `scrape_company_homepage_content` and `_scrape_pjl_page` both use `scrape_loaded_page_contract` after a single navigation; PJL page records store collapsed text + per-page enumerated nav links; `pjl_assembled_content` includes nav sections when links exist; `fetch_job_pages_batch` debug traces nav count per URL.

1. Refactor `scrape_company_homepage_content` in `src/core/roster.py`:

   - Replace separate `get_visible_text(...)` + `extract_site_page_list(company_website, ...)` (two navigations) with:
     - `pg = await get_page(browser_context, company_website)` (preserve existing redirect handling via `final_url` from contract).
     - `contract = await scrape_loaded_page_contract(pg, debug=False)` inside `try/finally: await close_page(pg)`.
   - Map contract fields to existing return shape: `visible_text`, `enumerated_nav_links`, `company_website` from `final_url` when set.
   - Keep existing error strings (`"No visible text extracted"`) and non-fatal nav warning behavior.

2. Refactor `_scrape_pjl_page` in `src/core/roster.py`:

   - After `wait_for_careers_list_readiness` (unchanged), replace direct `extract_visible_text` + `extract_site_page_list` with `contract = await scrape_loaded_page_contract(pg, debug=debug)`.
   - Set `out["visible_text"]` from collapsed contract text (strip for storage).
   - Set `out["page_links"]` from `contract["nav_urls"]` (raw URLs — gazer `_merge_pjl_nav_links` unchanged).
   - Add `out["enumerated_nav_links"] = contract["enumerated_nav_links"]` when non-empty.
   - Remove duplicate readiness debug block if `scrape_loaded_page_contract` already emitted per-URL detail when `debug=True`; keep readiness `debug_index` under `func="roster._scrape_pjl_page.scrape_readiness"` as today.

3. Extend `_merge_pjl_scrape_record` in `src/core/roster.py`:

   - When appending a new page row, persist optional `enumerated_nav_links` key from `new_record` when non-empty (alongside `url`, `visible_text`).

4. Extend `_assemble_pjl_content` in `src/core/roster.py`:

   - For each page row, after collapsed `visible_text`, when `row.get("enumerated_nav_links")` is non-empty, append:

     ```
     --- NAV LINKS ---
     {enumerated_nav_links}
     ```

   - Preserve existing `=== PAGE N: {url} ===` header format.

5. In `src/core/gazer.py` `fetch_job_pages_batch`, update per-URL debug block (~lines 441–452):

   - Outcome must include **collapsed** `visible_chars`, `nav_links={len(record.get('page_links') or [])}`, and `skipped` vs `scraped` when ledger skip applies (ledger skip stays in gazer loop — do not re-scrape duplicates).
   - Add `debug_detail` line: `enumerated_nav_chars={len(record.get('enumerated_nav_links') or '')}` when links recorded.

6. **Do not** change `fetch_job_pages_batch` pass/fail transitions, `_merge_pjl_nav_links` merge logic, or `possible_joblist_links` ledger filtering.

⚠️ **Decision:** Per-page nav links are stored on `pjl_scrape_pages[]` rows **and** merged globally into `pjl_nav_links` (existing gazer behavior). Assembly embeds per-page nav in `pjl_assembled_content`; global `pjl_nav_links` remains for TRY_LINK numeric resolution (AST-720).

---

## Stage 3: select_job_page live content parity at PJL_READY

**Done when:** `run_select_job_page_dispatch` passes agent live content that includes enumerated PJL nav links when scraped, without altering AST-720 state routing or TRY_LINK retry behavior.

1. In `src/core/roster.py`, add:

   ```python
   def _build_select_job_page_live_content(assembled_content: str, pjl_nav_links: str) -> str:
   ```

   - If `pjl_nav_links` is blank after strip → return `assembled_content` unchanged.
   - If `assembled_content` already contains the exact `pjl_nav_links` substring → return unchanged (idempotent).
   - Else append:

     ```
     === NAV LINKS ===
     {pjl_nav_links}
     ```

   - Single blank line separator before `=== NAV LINKS ===` when `assembled_content` non-empty.

2. In `run_select_job_page_dispatch`, after `_pjl_maps_from_company_data` and `_nav_links_for_try_links`:

   - `live_content = _build_select_job_page_live_content(assembled_content, nav_links)`
   - Pass `live_content` (not raw `assembled_content`) into `_find_job_page_from_assembled(..., assembled_content=live_content, ...)`.
   - Keep `nav_links=` argument unchanged for TRY_LINK resolution.

3. When `debug=True`, extend existing `run_select_job_page_dispatch` `debug_detail` to log `nav_links_chars={len(nav_links)} live_chars={len(live_content)}`.

4. **Do not** modify `_find_job_page_from_assembled` retry loop, `decomposed=True` branches, or `_check_parse_results`.

---

## Self-Assessment

**Scope:** `Single-Component` — three modules (`playwright.py`, `roster.py`, `gazer.py` debug-only touch); no config/state-machine changes; no UI or test edits by engineer.

**Conf:** `high` — AST-719/720 shipped the decomposed pipeline; this ticket consolidates an existing split scrape path and fills a known persistence/prompt gap (blank lines + nav enumeration + select live content).

**Risk:** `Medium` — incorrect single-load refactor on homepage could regress redirect detection or nav extraction; wrong assembly could duplicate nav blocks in select prompts — mitigated by idempotent `_build_select_job_page_live_content` and Betty roster tests on helpers.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | One external raw extractor + one core finalize/wrapper; homepage and PJL share `scrape_loaded_page_contract` |
| §2.1 config | No new config keys; existing `pjl_nav_links` / `nav_links` data keys reused |
| §2.4 batch | `fetch_job_pages_batch` structure unchanged; batch_id / transitions untouched |
| §2.5 bright line | Playwright I/O in external; collapse/enumerate in core |
| §2.6 state machine | No new transitions; gazer still sets `PJL_READY` / fail states |
| §3.3 imports | gazer → roster → external; external imports utils only inside new raw helper (none added) |
| §3.5 naming | snake_case; helper names describe contract not ticket id |

No unresolved conflicts.

---

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-753/AST-759-shared-page-scrape-fetch-job-pages-nav-links`  
**Product commits:** `c7a9be5` (Stage 1 — shared contract helpers), `7ec374e` (Stage 2 — fetch_job_pages wiring), `7513459` (Stage 3 — select_job_page live content parity)

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-753/AST-759-shared-page-scrape-fetch-job-pages-nav-links` @ `3061c92` (AST-759 product: `c7a9be5`, `7ec374e`, `7513459`)

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | All three stages land: `extract_page_scrape_contract` (external raw I/O), `finalize_page_scrape_contract` / `scrape_loaded_page_contract` (core collapse + enumerate), homepage + `_scrape_pjl_page` single-load routing, `_merge_pjl_scrape_record` / `_assemble_pjl_content` nav persistence, `_build_select_job_page_live_content` + `run_select_job_page_dispatch` live content parity, gazer per-URL debug outcomes. |
| Layer / §2.5 | Product contract (collapse, enumerate) in core; external returns raw payload only; import graph unchanged. |
| §2.6 / batch | No new transitions; `fetch_job_pages_batch` ledger skip + `_merge_pjl_nav_links` additive semantics preserved. |
| Tests | Betty manifest green (`TestAst759SharedPageScrapeContract`, extended AST-719/720/701 + gazer batch tests). |

### Issues

| Severity | Item | Location |
| --- | --- | --- |
| **fix-now** | Plan Stage 2 §1 requires preserving **non-fatal nav warning** on homepage scrape. Pre-refactor `scrape_company_homepage_content` logged `logger.warning` when `extract_site_page_list` raised; new path routes through `extract_page_scrape_contract`, which swallows `Exception` → `nav_urls=[]` with no signal, and core no longer warns. Operators lose visibility into nav extraction failures on fetch_website. | `src/external/playwright.py` `extract_page_scrape_contract`; `src/core/roster.py` `scrape_company_homepage_content` |
| **discuss** | Ledger-skip debug block emits `index=1, total=1` for **each** already-scraped URL — misleading batch headers when multiple skips (§1.5.1 universal `index N/M`). | `src/core/gazer.py` `fetch_job_pages_batch` ~440–449 |

### Recommended actions

| Severity | Action |
| --- | --- |
| **fix-now** | Surface nav extraction failure to core (e.g. optional `nav_error` on raw contract) and restore `logger.warning(f"[{short_name}] nav_links extraction failed (non-fatal): …")` in `scrape_company_homepage_content` when nav I/O fails but visible text succeeded — match pre-AST-759 behavior per plan. |
| **discuss** | If ledger skips can be >1 per company, use a single skip summary header or proper `index/total` over skipped URLs. |
| **Advisory** | Full three-dot diff vs `origin/dev` includes sibling epic merges on the AST-753 ftr line (AST-747/750/751 docs + interface/config deltas); AST-759 product commits stay within planned three-module footprint. |

**Verdict:** One **fix-now** (homepage nav warning regression) — `resolve-child` after restore.
