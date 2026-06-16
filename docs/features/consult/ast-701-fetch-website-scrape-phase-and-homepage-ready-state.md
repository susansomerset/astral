# fetch_website scrape phase and HOMEPAGE_READY state (prefilter as batch process)

**Linear:** [AST-701](https://linear.app/astralcareermatch/issue/AST-701/fetch-website-scrape-phase-and-homepage-ready-state-prefilter-as-batch-process)  
**Parent:** [AST-700](https://linear.app/astralcareermatch/issue/AST-700/prefilter-as-batch-process)  
**Publish ref:** `origin/sub/AST-700/AST-701-fetch-website-scrape-phase-and-homepage-ready-state`

Phase 1 of the AST-700 two-phase company prefilter pipeline: a new **`fetch_website`** dispatch task claims companies in **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`**, scrapes homepage visible text and **nav_links**, persists prepared content in **`company_data`**, and transitions successful rows to **`HOMEPAGE_READY`**. Scrape failures keep today's **`CANNOT_READ_WEBSITE`** semantics with notes persisted. Redirect detection normalizes **`company_website`**. Does **not** run the prefilter agent, change rubric/decode, or cut over from the monolithic **`prefilter`** dispatch path (**AST-702** owns evaluate-phase batching and cutover).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`HOMEPAGE_READY`** to **`COMPANY_STATES`**; add **`WEBSITE_FOUND`/`WEBSITE_FOUND_RETRY` → `HOMEPAGE_READY`/`CANNOT_READ_WEBSITE`** transitions; add **`GAZER_CONFIG["fetch_website"]`**; add **`homepage_text`** to **`ROSTER_CONFIG["company_data_keys"]`**; register **`fetch_website`** in **`DISPATCH_SCHEDULABLE_TASK_KEYS`**, **`_DISPATCH_COMPANY_ENTITY_TASK_KEYS`**, **`_dispatch_trigger_state_for_task_key`** | utils |
| `src/core/roster.py` | Extract shared **`async def scrape_company_homepage_content(...)`** from **`prefilter_company`** steps 1–2; refactor **`prefilter_company`** to call the helper (behavior unchanged) | core |
| `src/core/gazer.py` | Add **`fetch_website_batch`** mirroring **`scrape_jd_batch`** (connectivity gate, semaphore=3, per-company debug_index, summary dict) | core |
| `src/core/consult.py` | Route **`entity_type == "company"`** + **`dispatch_task_key == "fetch_website"`** to **`fetch_website_batch`** before **`run_company_task`** | core |
| `src/data/database.py` | Add **`("fetch_website", "WEBSITE_FOUND_RETRY")`** to **`_RETRY_TASK_SEED`** so retry companion dispatch rows clone from base **`fetch_website`** rows | data |

**Out of scope (AST-702 / later):** batch prefilter agent evaluation, disabling **`prefilter`** dispatch on **`WEBSITE_FOUND`**, changes to **`prefilter_company`** rubric/decode/persist beyond the scrape-helper refactor, UI work, tests (Betty manifest during **qa-child**).

---

## Stage 1: State machine and config scaffolding

**Done when:** **`HOMEPAGE_READY`** is a valid company state with batch criteria, transitions from **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`** to **`HOMEPAGE_READY`** and **`CANNOT_READ_WEBSITE`** exist in config, and **`fetch_website`** is a schedulable dispatch task key with admin defaults pointing at **`WEBSITE_FOUND`**.

1. In **`src/utils/config.py`**, block **`COMPANY_STATES`**, add after **`WEBSITE_FOUND_RETRY`**:
   ```python
   "HOMEPAGE_READY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
   ```

2. In **`src/utils/config.py`**, list **`ASTRAL_CONFIG["company_state_transitions"]`**, append (do not remove existing rows):
   - `("WEBSITE_FOUND", "HOMEPAGE_READY")`
   - `("WEBSITE_FOUND", "CANNOT_READ_WEBSITE")`
   - `("WEBSITE_FOUND_RETRY", "HOMEPAGE_READY")`
   - `("WEBSITE_FOUND_RETRY", "CANNOT_READ_WEBSITE")`

   ⚠️ **Decision:** Add explicit transitions even though **`prefilter_company`** already transitions to **`CANNOT_READ_WEBSITE`** without a listed edge — keeps the state graph honest for roster UI / future validation.

3. In **`src/utils/config.py`**, block **`GAZER_CONFIG`**, add after **`scrape_jd`**:
   ```python
   "fetch_website": {
       "fallback_batch_size": 10,
       "pass_state": "HOMEPAGE_READY",
       "fail_state": "CANNOT_READ_WEBSITE",
   },
   ```

4. In **`src/utils/config.py`**, block **`ROSTER_CONFIG["company_data_keys"]`**, add:
   ```python
   "homepage_text": "homepage_text",
   ```
   (Explicit storage only — **not** a coat-check handler; same pattern as **`job_list_visible`**.)

5. In **`src/utils/config.py`**, dispatch registry updates:
   - Add **`"fetch_website"`** to **`DISPATCH_SCHEDULABLE_TASK_KEYS`**.
   - Add **`"fetch_website"`** to **`_DISPATCH_COMPANY_ENTITY_TASK_KEYS`**.
   - In **`_dispatch_trigger_state_for_task_key`**, before the final **`KeyError`**, add:
     ```python
     if task_key == "fetch_website":
         return "WEBSITE_FOUND"
     ```
   - Leave **`_dispatch_batch_call_mode_for`** unchanged — **`fetch_website`** stays **`batch_call_mode=0`** (same as **`scrape_jd`**: dispatcher **`_warm_then_gather`** calls **`fetch_website_batch`** once per claimed company).

   ⚠️ **Decision:** **`fetch_website`** and legacy **`prefilter`** both default to **`trigger_state=WEBSITE_FOUND`**. This ticket seeds schedulability only; Susan must not run **`auto_mode=1`** on both simultaneously. **AST-702** cutover disables **`prefilter`** on **`WEBSITE_FOUND`** when batch evaluate goes live.

---

## Stage 2: Shared homepage scrape helper (roster)

**Done when:** **`prefilter_company`** still passes/fails exactly as before (manual verification on one company), and **`scrape_company_homepage_content`** returns structured scrape output usable by **`fetch_website_batch`**.

1. In **`src/core/roster.py`**, immediately above **`async def prefilter_company`**, add:

   ```python
   async def scrape_company_homepage_content(
       short_name: str,
       company_website: str,
       *,
       browser_context=None,
   ) -> Dict[str, Any]:
   ```

   **Return dict keys (always present):** `company_website` (possibly updated canonical URL), `visible_text` (str), `enumerated_nav_links` (str, may be empty), `error` (str or None).

2. Move **`prefilter_company`** steps 1–2 into the helper without semantic change:
   - Call **`get_visible_text(company_website, context=browser_context, return_final_url=True)`**; on exception return `{..., "error": str(scrape_err)}` **without** transitioning state (caller decides).
   - If **`final_url`** differs from input, call **`update_company(short_name, company_website=final_url)`** and update local **`company_website`** variable.
   - If visible text is empty/whitespace-only, return `{..., "visible_text": visible_text or "", "error": "No visible text extracted"}`.
   - Call **`extract_site_page_list(company_website, max_depth=1, verify=False, context=browser_context)`** inside **`try/except`**; on success with URLs, set **`enumerated_nav_links = enumerate_array("", url_list)`**; on nav failure log **`logger.warning`** (non-fatal) and leave **`enumerated_nav_links=""`** — same as today.

3. Refactor **`prefilter_company`** body:
   - Replace inline steps 1–2 with **`scrape = await scrape_company_homepage_content(short_name, company_website, browser_context=browser_context)`**.
   - If **`scrape.get("error")`**: transition **`CANNOT_READ_WEBSITE`**, **`save_company_data(short_name, {"prefilter_company_notes": scrape["error"]})`**, set result fields, **`return result`** — identical observable outcomes to today.
   - Set **`company_website = scrape["company_website"]`**, **`visible_text = scrape["visible_text"]`**, **`enumerated_nav_links = scrape["enumerated_nav_links"]`**; continue with step 3 assembly unchanged.

---

## Stage 3: `fetch_website_batch` (gazer)

**Done when:** Calling **`fetch_website_batch(batch_id, [company_dict], debug=True)`** on a **`WEBSITE_FOUND`** row with a reachable homepage transitions it to **`HOMEPAGE_READY`** with **`homepage_text`** (+ **`nav_links`** when extracted) in **`company_data`**; scrape failures land in **`CANNOT_READ_WEBSITE`** with **`prefilter_company_notes`** set.

1. In **`src/core/gazer.py`**, add imports from roster:
   ```python
   from src.core.roster import scrape_company_homepage_content, transition_company_state
   from src.utils.config import ROSTER_CONFIG
   ```
   ( **`transition_company_state`** may already be available via roster import path — dedupe imports.)

2. Add **`async def fetch_website_batch(batch_id, companies, debug=False) -> Dict[str, int]`** beside **`scrape_jd_batch`**, matching its outer structure:
   - **`check_connectivity()`** gate — raise **`ConnectionError`** with batch id + count on failure.
   - Read **`cfg = GAZER_CONFIG["fetch_website"]`**, **`pass_state`**, **`fail_state`**, notes key **`notes_key = ROSTER_CONFIG["company_data_keys"]["prefilter_company_notes"]`**.
   - **`debug`**: call **`_log.set_debug_flag(True)`**; log batch start via **`_log.debug_index(func="gazer.fetch_website_batch", ...)`** mirroring **`scrape_jd_batch`**.
   - **`async with create_browser_context() as browser_context:`** for the whole batch; pass **`browser_context`** into each scrape call (reuse session across companies in one dispatch batch when **`batch_call_mode=1`** later; safe for per-entity **`batch_call_mode=0`** too).

3. Inner **`async def _fetch_one(company, company_index)`**:
   - **`short_name = company.get("short_name") or ""`**, **`company_website = (company.get("company_website") or "").strip()`**.
   - If no **`company_website`**: **`transition_company_state(short_name, fail_state)`**, **`save_company_data(short_name, {notes_key: "No company_website"})`**, increment **`failed`**, debug_index outcome **`failed — no company_website`**, **`return`**.
   - **`scrape = await scrape_company_homepage_content(short_name, company_website, browser_context=browser_context)`**.
   - If **`scrape.get("error")`**: **`transition_company_state(short_name, fail_state)`**, **`save_company_data(short_name, {notes_key: scrape["error"]})`**, increment **`failed`**, debug_index with redirect/char counts when known, **`return`**.
   - Success path — build **`data_to_save`**:
     ```python
     data_to_save = {"homepage_text": scrape["visible_text"]}
     if scrape.get("enumerated_nav_links"):
         data_to_save["nav_links"] = scrape["enumerated_nav_links"]
     save_company_data(short_name, data_to_save)
     transition_company_state(short_name, pass_state)
     ```
   - Increment **`passed`**; **`debug_index`** outcome must include: homepage char count, whether redirect normalized (**`final_url != original`**), nav link count or **non-fatal nav failure** — e.g. **`passed -> HOMEPAGE_READY (12345 chars redirect=yes nav=42 links)`**; use **`_log.debug_detail`** for **`company_website`**, canonical URL, and truncated homepage preview per AST-538 truncation contract.

4. Concurrency: **`asyncio.Semaphore(3)`** + **`asyncio.gather`** over companies (same cap as **`scrape_jd_batch`**).

5. Return **`{"passed": passed, "failed": failed, "total": len(companies)}`**; debug batch-end summary line like **`scrape_jd_batch`**.

   ⚠️ **Decision:** Persist scrape failures under **`prefilter_company_notes`** (not a new key) so roster UI and existing admin preview strings stay consistent until **AST-702** batch evaluate owns outcomes.

---

## Stage 4: Dispatcher routing (consult)

**Done when:** A dispatch run with **`task_key=fetch_website`**, **`entity_type=company`**, **`trigger_state=WEBSITE_FOUND`** invokes **`fetch_website_batch`** and returns normalized **`total_processed/passed/failed/errors`** counts.

1. In **`src/core/consult.py`**, function **`run_consult_task`**, in the **`if entity_type == "company":`** block **before** **`run_company_task`**:
   ```python
   task_key = (dispatch_task_key or "").strip()
   if task_key == "fetch_website":
       from src.core.gazer import fetch_website_batch
       r = await fetch_website_batch(batch_id, entities, debug=debug)
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

2. Leave the existing **`WEBSITE_FOUND` → `prefilter_company`** path in **`run_company_task`** untouched (**AST-702** cutover).

3. Manual verification (no test edits in this ticket):
   - Admin UI or SQL: ensure a candidate has a **`dispatch_task`** row with **`task_key='fetch_website'`**, **`trigger_state='WEBSITE_FOUND'`**, **`entity_type='company'`**, **`batch_call_mode=0`**, **`auto_mode=0`** initially.
   - Place one test company in **`WEBSITE_FOUND`** with valid **`company_website`**; run dispatch with **`debug=1`**; confirm **`HOMEPAGE_READY`**, **`company_data.homepage_text`**, and debug index lines.

---

## Stage 5: Dispatch retry seed (database)

**Done when:** Existing candidates with a base **`fetch_website`** dispatch row receive an **`INSERT OR IGNORE`** companion row with **`trigger_state='WEBSITE_FOUND_RETRY'`** on schema ensure (same mechanism as **`prefilter`** retry rows).

1. In **`src/data/database.py`**, tuple list **`_RETRY_TASK_SEED`**, append:
   ```python
   ("fetch_website", "WEBSITE_FOUND_RETRY"),
   ```

2. No change to **`save_dispatch_task`** — Susan creates base **`fetch_website`** rows via admin when enabling the task; schema backfill clones retry rows from each base row on next DB open/migration.

---

## Self-Assessment

### Scope — **Single-Component**

Touches config state registry, roster scrape helper, gazer batch runner, consult dispatch routing, and dispatch retry seed — one vertical slice (scrape phase only) with no agent or rubric changes.

### Conf — **Medium**

Pattern is established (**`scrape_jd_batch`** + existing **`prefilter_company`** scrape steps); open operational dependency is Susan not running **`prefilter`** and **`fetch_website`** dispatch concurrently until **AST-702** cutover.

### Risk — **Medium**

Incorrect scrape persistence or state transitions would block companies between **`WEBSITE_FOUND`** and batch prefilter, but would not corrupt grades or job consult pipelines.

---

## Plan vs ASTRAL_CODE_RULES cross-check

- **§1.3 DRY:** Scrape logic lives once in **`scrape_company_homepage_content`**; **`prefilter_company`** and **`fetch_website_batch`** both call it.
- **§2.1 config:** States, transitions, and **`GAZER_CONFIG`** orchestration fields live in **`config.py`** — no hard-coded state names in dispatcher.
- **§2.4 batch processing:** Uses existing claim/release via dispatcher **`get_new_company_batch`** / **`clear_company_batch`**; batch function returns pass/fail counts.
- **§2.6 state machine:** Core (**roster/gazer**) chooses target states; data layer only persists via **`transition_company_state`** / **`save_company_data`**.
- **§2.8 coat-check:** **`homepage_text`** is explicit storage only — no empty failure caching.
- **§3.5 naming:** Dispatch task key **`fetch_website`** matches job-side **`scrape_jd`** verb_noun pattern; holding state **`HOMEPAGE_READY`** mirrors **`JD_READY`**.

No conflicts requiring plan revision.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-700/AST-701-fetch-website-scrape-phase-and-homepage-ready-state` @ `4f6037b`

**Built:** five `code(AST-701)` commits — config (`HOMEPAGE_READY`, `fetch_website` dispatch registry), `scrape_company_homepage_content`, `fetch_website_batch`, consult routing, `_RETRY_TASK_SEED` for `fetch_website`.
