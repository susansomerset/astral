# AST-719 — fetch_job_pages gazer batch and PJL_READY state

**Linear:** [AST-719 — fetch_job_pages gazer batch and PJL_READY state (find_job_page logic confirmation)](https://linear.app/astralcareermatch/issue/AST-719/fetch-job-pages-gazer-batch-and-pjl-ready-state-find-job-page-logic-confirmation)

**Parent (reference only — do not implement sibling scope):** [AST-716 — find_job_page logic confirmation](https://linear.app/astralcareermatch/issue/AST-716/find-job-page-logic-confirmation)

**Publish ref:** `origin/sub/AST-716/fetch-job-pages-batch-scrape`

**Summary:** Add **`fetch_job_pages`** as a schedulable company dispatch hop (mirror **`fetch_website`** / **`prefilter`** batch routing) that Playwright-scrapes each URL in **`company_data.possible_joblist_links`** additively, persists assembled PJL visible text for downstream **`select_job_page`**, and transitions successful companies to **`PJL_READY`**. Reuses existing roster PJL scrape + AST-689 readiness gate; does not run the selection agent or remove monolithic **`find_job_page`**.

**Build gate (sibling):** [AST-718](https://linear.app/astralcareermatch/issue/AST-718) must be **`code()`-complete on `origin/ftr/AST-716-find-job-page-logic-confirmation`** before **build-child** — this ticket reads **`possible_joblist_links`** (normalized URL ledger) and **`normalize_link()`** from formatting. Planning assumes AST-718 plan shapes; if AST-718 is not merged to ftr at build time, stop and comment on AST-719.

**Depends on (Done on `origin/dev` / ftr):** AST-689 (`wait_for_careers_list_readiness`), AST-673 (`_job_site_for_persist` — fetch must not write **`job_site`**), AST-718 (PJL URL ledger — build gate).

**Out of scope (sibling tickets):** **`select_job_page`** dispatch refactor + **`PJL_READY` → `JOBLIST_IDENTIFIED`** state machine (AST-720), **`parse_job_list`** dispatch refactor (AST-721), monolithic **`find_job_page`** removal, Grace **`JOBSITE_SCRAPE_ISSUE`** emission (AST-692 — agent hop only), prompt edits, UI.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | **`PJL_READY`** state + transitions; **`GAZER_CONFIG["fetch_job_pages"]`**; **`ROSTER_CONFIG`** PJL data keys; register **`fetch_job_pages`** in dispatch registries | utils |
| `src/core/roster.py` | Extract single-URL PJL scrape helper from **`_fetch_job_links_content`**; add **`scrape_company_pjl_pages_additive`**; refactor **`_fetch_job_links_content`** to call helper (behavior unchanged for monolith) | core |
| `src/core/gazer.py` | Add **`fetch_job_pages_batch`** mirroring **`fetch_website_batch`** | core |
| `src/core/consult.py` | Route **`entity_type == "company"`** + **`dispatch_task_key == "fetch_job_pages"`** to **`fetch_job_pages_batch`** before **`run_company_task`** | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | Additive skip, append, **`PJL_READY`** / **`NO_JOBLIST`** transitions, readiness debug |
| `tests/component/core/test_gazer.py` | **`fetch_job_pages_batch`** summary shape (if file exists; else roster integration tests suffice per Betty manifest) |
| `tests/component/utils/test_config.py` | Assert **`PJL_READY`**, **`fetch_job_pages`** schedulable key |

**Read-only reuse (do not duplicate):**

| Symbol | Location | Use |
|--------|----------|-----|
| `fetch_website_batch` | `src/core/gazer.py` | Batch shell: connectivity gate, semaphore=3, per-company **`debug_index`**, `{passed, failed, total}` return |
| `_fetch_job_links_content` | `src/core/roster.py` | Scrape loop to extract/refactor — readiness, visible text, new links |
| `wait_for_careers_list_readiness` | `src/external/playwright.py` | AST-689 gate (already called in scrape path) |
| `normalize_link` | `src/utils/formatting.py` | AST-718 ledger dedupe for skip + append |
| `parse_enumerate_array` | `src/utils/formatting.py` | Build homepage **`nav_links`** URL set for “new link” detection |
| `_job_site_for_persist` / `_save_company` | `src/core/roster.py` | **Do not** call with **`job_site`** during fetch — no **`update_company(..., job_site=…)`** in this hop |

---

## Stage 1: Config — `PJL_READY`, gazer orch, data keys, dispatch registry

**Done when:** **`PJL_READY`** is claimable; **`fetch_job_pages`** appears in admin schedulable keys with default **`trigger_state=PREFILTER_PASSED`**; PJL persistence keys are registered in **`ROSTER_CONFIG["company_data_keys"]`**.

1. In `src/utils/config.py`, **`COMPANY_STATES`**, add after **`PREFILTER_PASSED`**:

   ```python
   "PJL_READY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
   ```

2. In **`ASTRAL_CONFIG["company_state_transitions"]`**, append:

   ```python
   ("PREFILTER_PASSED", "PJL_READY"),
   ("PREFILTER_PASSED", "NO_JOBLIST"),
   ```

   Keep existing **`PREFILTER_PASSED → WATCH|NO_JOBLIST|…`** tuples (monolithic **`find_job_page`** path until AST-721 removes it).

3. In **`GAZER_CONFIG`**, after **`fetch_website`**, add:

   ```python
   "fetch_job_pages": {
       "fallback_batch_size": 10,
       "pass_state": "PJL_READY",
       "fail_state": "NO_JOBLIST",
   },
   ```

   ⚠️ **Decision:** All pending PJL URLs scraped with **zero** non-empty visible text → **`NO_JOBLIST`** (same observable outcome as monolith **`find_job_page`** when **`assembled_content`** is empty). Partial success → **`PJL_READY`** even if some URLs failed individually.

4. In **`ROSTER_CONFIG["company_data_keys"]`**, add:

   ```python
   "pjl_scraped_pages": "pjl_scraped_pages",
   "pjl_assembled_content": "pjl_assembled_content",
   ```

   **`possible_joblist_links`** key is added by AST-718 — verify present at build; do not duplicate if already there.

5. Dispatch registry (mirror AST-701 **`fetch_website`** registration):

   - Add **`"fetch_job_pages"`** to **`DISPATCH_SCHEDULABLE_TASK_KEYS`** and **`_DISPATCH_COMPANY_ENTITY_TASK_KEYS`**.
   - In **`_dispatch_trigger_state_for_task_key`**, before the final **`KeyError`**:

     ```python
     if task_key == "fetch_job_pages":
         return "PREFILTER_PASSED"
     ```

   - Leave **`batch_call_mode=0`** (per-entity batch call like **`fetch_website`** / **`scrape_jd`**).

   ⚠️ **Decision:** **`fetch_job_pages`** and legacy **`find_job_page`** may both use **`trigger_state=PREFILTER_PASSED`** with different **`task_key`** values (unique **`(candidate_id, task_key, trigger_state)`**). Susan must not enable **`auto_mode=1`** on both simultaneously — same cutover discipline as AST-701/702. **Do not** delete or retarget existing **`find_job_page`** rows in this ticket.

6. **Do not** add **`PJL_READY`** to **`ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]`** — AST-720 wires **`select_job_page`** on **`PJL_READY`**.

---

## Stage 2: Roster — single-URL scrape helper + additive merger

**Done when:** **`scrape_company_pjl_pages_additive`** scrapes only URLs not yet in the ledger, appends page records without duplicating prior visible text, rebuilds **`pjl_assembled_content`**, optionally extends **`possible_joblist_links`** with newly discovered normalized URLs, and returns `{pass: bool, scraped_count, skipped_count, error: Optional[str]}`; monolithic **`_fetch_job_links_content`** behavior is unchanged.

1. In `src/core/roster.py`, extract from the inner loop of **`_fetch_job_links_content`** (~lines 1768–1822) a new async helper immediately above **`_fetch_job_links_content`**:

   ```python
   async def _scrape_one_pjl_url(
       url: str,
       *,
       nav_url_set: Set[str],
       browser_context: BrowserSession,
       debug: bool = False,
       page_num: int = 1,
       page_total: int = 1,
   ) -> Dict[str, Any]:
   ```

   **Return dict keys:** `url` (final URL after navigation if available), `visible_text` (str), `new_links` (list[str] — links on page not in **`nav_url_set`**), `error` (str or None).

   Move verbatim: **`get_page` → `wait_for_careers_list_readiness` → `extract_visible_text` → `extract_site_page_list`**; readiness debug block stays inside this helper (AST-689). **Do not** extract DOM here — AST-721 reloads DOM at parse hop.

   Refactor **`_fetch_job_links_content`** to call **`_scrape_one_pjl_url`** for each index-resolved URL; assembled section format unchanged:

   ```
   === PAGE {n}: {url} ===
   {visible_text}
   --- NEW LINKS ---
   1. {link}
   ```

2. Add pure helper **`_build_pjl_assembled_content(pjl_scraped_pages: List[Dict[str, Any]]) -> str`** (module level, below scrape helper):

   - Iterate **`pjl_scraped_pages`** in list order with 1-based page numbers.
   - Use the same section template as step 1.
   - Join sections with **`"\n\n"`**.

3. Add async **`scrape_company_pjl_pages_additive(short_name, company, *, browser_context, debug=False) -> Dict[str, Any]`**:

   **Read inputs from `company` / `get_company`:**

   - `pjl_urls = (company_data.get("possible_joblist_links") or [])` — list of normalized URL strings (AST-718).
   - `existing_pages = list(company_data.get("pjl_scraped_pages") or [])` — each item `{url_key, url, visible_text, new_links}`.
   - `scraped_keys = {row["url_key"] for row in existing_pages if row.get("url_key")}`.
   - `nav_links = company_data.get("nav_links") or ""`.
   - `nav_url_set = set(parse_enumerate_array(nav_links).values())`.

   **Early exits:**

   - If not `pjl_urls`: return `{pass: False, error: "no possible_joblist_links", ...}` (caller transitions **`NO_JOBLIST`**).
   - If not `nav_links.strip()`: return `{pass: False, error: "no nav_links", ...}`.

   **Scrape loop** — for each `url_key` in `pjl_urls` (already normalized):

   - If `url_key in scraped_keys`: increment **`skipped_count`**; continue (additive skip — no duplicate visible text).
   - Resolve fetch URL: use `url_key` as navigation target; if it lacks scheme, prepend **`https://`** (single branch only — do not guess multiple schemes).
   - Call **`_scrape_one_pjl_url`** with updated **`nav_url_set`** (include URLs from prior **`existing_pages`** **`url`** fields).
   - Append to **`existing_pages`**:

     ```python
     {
         "url_key": url_key,
         "url": scrape_result["url"] or fetch_url,
         "visible_text": (scrape_result["visible_text"] or "").strip(),
         "new_links": scrape_result.get("new_links") or [],
     }
     ```

   - For each link in **`new_links`**, compute **`nk = normalize_link(link)`**; if **`nk`** and **`nk` not in pjl_urls` ledger list, append to a local **`ledger_append`** list (dedupe with set of current **`pjl_urls` + ledger_append**).

   **After loop:**

   - `assembled = _build_pjl_assembled_content(existing_pages)`.
   - `data_to_save = {
         "pjl_scraped_pages": existing_pages,
         "pjl_assembled_content": assembled,
     }`
   - If **`ledger_append`**: `data_to_save["possible_joblist_links"] = pjl_urls + ledger_append` (preserve order — existing first, then new).
   - `save_company_data(short_name, data_to_save)`.
   - `pass = bool(assembled.strip())` — at least one page with content in assembled string.
   - Return `{pass, scraped_count, skipped_count, error: None}`.

   ⚠️ **Decision:** Store **`pjl_scraped_pages`** as the durable ledger (not only **`pjl_assembled_content`**) so re-runs can skip by **`url_key`** without re-parsing the assembled string. **`pjl_assembled_content`** is a denormalized cache for AST-720 **`select_job_page`** input.

4. **Do not** modify **`find_job_page`**, **`run_select_job_page_dispatch`**, or **`run_company_task`** locate branches in this stage.

---

## Stage 3: `fetch_job_pages_batch` (gazer)

**Done when:** Dispatching **`fetch_job_pages`** on a **`PREFILTER_PASSED`** company with **`possible_joblist_links`** produces its own Execution History batch, lands **`PJL_READY`** when assembled content is non-empty, and **`NO_JOBLIST`** when not; **`job_site`** column unchanged.

1. In `src/core/gazer.py` module docstring first line, append **`fetch_job_pages_batch`** to the in-scope list.

2. Add import:

   ```python
   from src.core.roster import scrape_company_pjl_pages_additive, transition_company_state
   ```

3. Add **`async def fetch_job_pages_batch(batch_id, companies, debug=False) -> Dict[str, int]`** beside **`fetch_website_batch`**, matching outer structure:

   - **`check_connectivity()`** → raise **`ConnectionError`** on failure.
   - **`cfg = GAZER_CONFIG["fetch_job_pages"]`**, **`pass_state`**, **`fail_state`**.
   - **`async with create_browser_context() as browser_context:`** for entire batch.
   - Semaphore **`asyncio.Semaphore(3)`** — same concurrency as **`fetch_website_batch`**.

4. Inner **`async def _fetch_one(company, company_index)`**:

   - **`short_name = company.get("short_name") or ""`**.
   - **`result = await scrape_company_pjl_pages_additive(short_name, company, browser_context=browser_context, debug=debug)`**.
   - If **`result.get("error")`** (missing inputs): **`transition_company_state(short_name, fail_state)`**; **`failed += 1`**; debug_index outcome **`failed — {error} -> {fail_state}`**; **do not** write **`job_site`**.
   - Elif **`result.get("pass")`**: **`transition_company_state(short_name, pass_state)`**; **`passed += 1`**; debug_index outcome **`passed -> PJL_READY scraped={scraped_count} skipped={skipped_count}`**.
   - Else: **`transition_company_state(short_name, fail_state)`**; **`failed += 1`**; debug_index outcome **`failed — empty assembled content -> NO_JOBLIST`**.

   **AST-538:** When **`debug=True`**, each company gets Style D **`debug_index`** (`index=company_index`, `total=company_total`, identifier **`_gazer_company_identifier(company)`**); **`debug_detail`** lines include **`possible_joblist_links` count**, per-URL scrape/skip outcomes from roster helper (forward **`debug`** into **`scrape_company_pjl_pages_additive`** — emit detail there for each URL attempted).

5. Return **`{"passed": passed, "failed": failed, "total": len(companies)}`**.

---

## Stage 4: Consult routing

**Done when:** Scheduler / admin **Run** on a **`fetch_job_pages`** dispatch row invokes **`fetch_job_pages_batch`** and returns normalized summary counts (same shape as **`fetch_website`**).

1. In `src/core/consult.py`, inside **`run_consult_task`**, **`entity_type == "company"`** block, after the **`fetch_website`** branch and before **`prefilter`**:

   ```python
   if task_key == "fetch_job_pages":
       from src.core.gazer import fetch_job_pages_batch
       r = await fetch_job_pages_batch(batch_id, entities, debug=debug)
       total = r.get("total", len(entities))
       passed = r.get("passed", 0)
       failed = r.get("failed", 0)
       errors = max(0, total - passed - failed)
       return {
           "total_processed": total,
           "total_passed": passed,
           "total_failed": failed,
           "total_errors": errors,
       }
   ```

2. **Do not** add **`fetch_job_pages`** handling inside **`run_company_task`** — consult short-circuit only (same as **`fetch_website`**).

---

## Stage 5: Roster debug passthrough

**Done when:** With **`debug=True`**, Susan sees per-URL scrape/skip lines under each company index header during **`fetch_job_pages`** dispatch; no new debug output when **`debug=False`**.

1. In **`scrape_company_pjl_pages_additive`**, when **`debug=True`**:

   - Before loop: **`logger.set_debug_flag(True)`**.
   - For each URL: **`debug_index`** with `func="roster.scrape_company_pjl_pages_additive"`, `identifier=url_key`, outcome **`skipped-already-scraped`** or **`scraped N chars M new_links`** or **`scrape-failed: {error}`**.
   - After loop: **`debug_detail`** with **`assembled_chars={len(assembled)} ledger_size={len(existing_pages)}`**.

2. **Do not** add production **`logger.info`** chatter beyond existing roster patterns.

---

## Self-Assessment

**Scope:** `Single-Component` — config + roster scrape refactor + one gazer batch + one consult branch; no dispatcher schema beyond schedulable key registration, no UI, no agent tasks.

**Conf:** `Medium` — clear mirror of AST-701 **`fetch_website_batch`** and existing **`_fetch_job_links_content`**, but additive persistence shape is new and depends on AST-718 landing first.

**Risk:** `Medium` — incorrect skip/append logic would duplicate PJL text or skip needed re-scrapes; running **`fetch_job_pages`** and monolithic **`find_job_page`** concurrently on **`PREFILTER_PASSED`** would double-scrape until Susan disables legacy row.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single-URL scrape extracted once; monolith + batch share helper |
| §2.1 config | States, pass/fail, data keys in config |
| §2.4 batch | Follows claim → process → release via dispatcher; batch fn returns counts |
| §2.5 bright line | Playwright in external; roster orchestrates |
| §2.6 state machine | Core chooses **`PJL_READY`** / **`NO_JOBLIST`**; data layer not deciding |
| §3.3 imports | gazer → roster → external; consult → gazer |
| §3.5 naming | snake_case keys; task_key **`fetch_job_pages`** matches dispatch convention |

No unresolved conflicts.

---

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-716/fetch-job-pages-batch-scrape`  
**Product commits:** `04e39cf4` (Stage 1 — config), `6d0a31cf` (Stage 2 — PJL scrape helpers), `437bfe70` (Stage 3 — `fetch_job_pages_batch`), `e9df44c2` (Stage 4 — consult routing)
