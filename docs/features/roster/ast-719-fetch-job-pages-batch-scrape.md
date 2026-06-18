# AST-719 — fetch_job_pages gazer batch and PJL_READY state

**Linear:** [AST-719 — fetch_job_pages gazer batch and PJL_READY state (find_job_page logic confirmation)](https://linear.app/astralcareermatch/issue/AST-719/fetch-job-pages-gazer-batch-and-pjl-ready-state-find-job-page-logic)

**Parent (reference only):** [AST-716 — find_job_page logic confirmation](https://linear.app/astralcareermatch/issue/AST-716/find-job-page-logic-confirmation)

**Publish ref:** `origin/sub/AST-716/fetch-job-pages-batch-scrape`

**Summary:** Add **`fetch_job_pages`** as a schedulable gazer-style company dispatch hop triggered from **`PREFILTER_PASSED`**. For each company, scrape every URL in **`possible_joblist_links`** additively (skip URLs already captured, append page visible text and PJL nav links without wiping prior PJL data), honor **AST-689** careers-list readiness polling and **AST-692** **`JOBSITE_SCRAPE_ISSUE`** when the full candidate set fails to yield content, and land success in **`PJL_READY`** with persisted assembled PJL content for sibling **`select_job_page`** (**AST-720**). **`job_site`** remains unset.

**Depends on:** **AST-718** (`possible_joblist_links` hydrated normalized URLs + `normalize_link()` in `formatting.py`). Build **AST-718** on `origin/ftr/AST-716-*` before or merge sibling sub into ftr before **build-child** for this ticket.

**Out of scope:** `select_job_page` agent prompts / selection state machine (**AST-720**), monolithic **`find_job_page`** removal (**AST-721**), dispatch changes to **`parse_job_list`**, UI, new LLM tasks.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `PJL_READY` state + transitions; `GAZER_CONFIG["fetch_job_pages"]`; `ROSTER_CONFIG` PJL data keys; dispatch registry (`DISPATCH_SCHEDULABLE_TASK_KEYS`, trigger_state, entity type) | utils |
| `src/core/roster.py` | PJL scrape helpers (`_scrape_pjl_page`, `_merge_pjl_scrape_record`, `_assemble_pjl_content`); export for gazer | core |
| `src/core/gazer.py` | `fetch_job_pages_batch` mirroring `fetch_website_batch` | core |
| `src/core/consult.py` | `run_consult_task` route for `dispatch_task_key == "fetch_job_pages"` | core |

**Verify only (Betty / qa-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_gazer.py` | Additive skip, append, PJL_READY transition, all-fail → `JOBSITE_SCRAPE_ISSUE` |
| `tests/component/core/test_roster.py` | Scrape helper unit cases (readiness mocked) |
| `tests/component/utils/test_config.py` | `PJL_READY`, `fetch_job_pages` dispatch defaults |
| `tests/component/core/test_consult.py` | `run_consult_task` routes `fetch_job_pages` to gazer batch |

**Read-only reuse (do not duplicate):**

| Symbol | Location | Use |
|--------|----------|-----|
| `fetch_website_batch` | `src/core/gazer.py` | Structural template (connectivity, semaphore, debug batch header, per-entity loop) |
| `wait_for_careers_list_readiness` | `src/external/playwright.py` | AST-689 readiness gate per PJL URL |
| `roster_scrape_readiness_config` | `src/utils/config.py` | Readiness cfg for PJL scrapes |
| `_fetch_job_links_content` | `src/core/roster.py` | Section assembly format reference (`=== PAGE N: url ===`) — do not change monolithic path in this ticket |
| `normalize_link` | `src/utils/formatting.py` | Skip / dedupe ledger keys (**AST-718**) |
| `enumerate_array` / `parse_enumerate_array` | `src/utils/formatting.py` | PJL nav link merge |
| `get_visible_text`, `extract_site_page_list`, `get_page`, `close_page` | `src/external/playwright.py` | Single-page scrape |
| `create_browser_context` | `src/external/playwright.py` | Shared browser per batch entity |

---

## Stage 1: Config — `PJL_READY`, gazer block, dispatch registry

**Done when:** Config exposes `PJL_READY`, `GAZER_CONFIG["fetch_job_pages"]`, PJL `company_data_keys`, and admin can seed a `dispatch_task` row for `fetch_job_pages` with `trigger_state=PREFILTER_PASSED`.

1. In `src/utils/config.py`, inside `COMPANY_STATES`, add:

   ```python
   "PJL_READY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
   ```

2. In `ASTRAL_CONFIG["company_state_transitions"]`, append:

   ```python
   ("PREFILTER_PASSED", "PJL_READY"),
   ("PREFILTER_PASSED", "JOBSITE_SCRAPE_ISSUE"),
   ```

   Keep existing `PREFILTER_PASSED → WATCH|NO_JOBLIST|…` edges for monolithic `find_job_page` until **AST-721** removes them.

3. In `GAZER_CONFIG`, after `"fetch_website"`, add:

   ```python
   "fetch_job_pages": {
       "fallback_batch_size": 10,
       "pass_state": "PJL_READY",
       "fail_state": "JOBSITE_SCRAPE_ISSUE",
   },
   ```

   ⚠️ **Decision:** All candidate URLs fail to produce storable visible text → **`JOBSITE_SCRAPE_ISSUE`** (AST-692 terminal family). Partial success (≥1 page record after batch, including pre-existing) → **`PJL_READY`**.

4. In `ROSTER_CONFIG["company_data_keys"]`, add:

   ```python
   "possible_joblist_links": "possible_joblist_links",  # no-op if AST-718 already added
   "pjl_scrape_pages": "pjl_scrape_pages",
   "pjl_assembled_content": "pjl_assembled_content",
   "pjl_nav_links": "pjl_nav_links",
   ```

   **`pjl_scrape_pages`** shape: ordered list of `{"url": str, "visible_text": str}` — one entry per normalized URL successfully scraped (additive; never overwrite existing entries).

   **`pjl_assembled_content`**: single string, `=== PAGE n: {url} ===` sections joined by `\n\n` (same visual shape as `_fetch_job_links_content` output for **AST-720**).

   **`pjl_nav_links`**: enumerated multiline string (`enumerate_array`) of nav URLs discovered on PJL pages, merged additively across runs.

5. Add `"fetch_job_pages"` to:

   - `DISPATCH_SCHEDULABLE_TASK_KEYS`
   - `_DISPATCH_COMPANY_ENTITY_TASK_KEYS`

   Do **not** add to `_DISPATCH_BATCH_CALL_MODE_ONE` (mirror **`fetch_website`**: `batch_call_mode=0`, dispatcher calls batch with one company per wave).

6. In `_dispatch_trigger_state_for_task_key`, add before the `fetch_website` branch:

   ```python
   if task_key == "fetch_job_pages":
       return "PREFILTER_PASSED"
   ```

7. **Do not** add `PJL_READY` to `locate_job_page.dispatch_input_states` or seed `select_job_page` dispatch rows — **AST-720**.

---

## Stage 2: Roster — PJL scrape helpers (no dispatch entry yet)

**Done when:** Helpers scrape one PJL URL with readiness polling, merge records additively by `normalize_link`, and rebuild assembled content + merged nav links.

1. In `src/core/roster.py`, import `normalize_link` from `src.utils.formatting` (provided by **AST-718**).

2. Add `_pjl_scrape_ledger_keys(pjl_scrape_pages: list) -> set[str]`:

   - Return `{normalize_link(row["url"]) for row in (pjl_scrape_pages or []) if row.get("url")}`.

3. Add `async def _scrape_pjl_page(url: str, browser_context, *, debug: bool = False) -> Dict[str, Any]`:

   - Open page via `get_page(browser_context, url)`; `try/finally` `close_page`.
   - Call `wait_for_careers_list_readiness(page, roster_scrape_readiness_config())` — same as `_fetch_job_links_content` (AST-689).
   - When `debug=True`, emit `debug_index` / `debug_detail` for readiness outcome (func=`roster._scrape_pjl_page.scrape_readiness`).
   - Extract visible text via `extract_visible_text` pattern from `_fetch_job_links_content` (import `extract_visible_text` from playwright if not already imported).
   - Extract `page_links = await extract_site_page_list(page=page, max_depth=1, verify=False)`.
   - Return `{"url": url, "visible_text": stripped_text, "page_links": page_links or [], "readiness": ready_meta}`.
   - On exception, return `{"url": url, "error": str(e), "visible_text": "", "page_links": []}`.

4. Add `_merge_pjl_scrape_record(existing_pages: list, new_record: dict) -> list`:

   - If `normalize_link(new_record["url"])` already in ledger keys, return `existing_pages` unchanged (additive skip).
   - If `not (new_record.get("visible_text") or "").strip()`, do not append (failed scrape).
   - Else append `{"url": new_record["url"], "visible_text": new_record["visible_text"].strip()}`.

5. Add `_merge_pjl_nav_links(existing_enum: str, new_urls: list[str]) -> str`:

   - Parse existing with `parse_enumerate_array(existing_enum or "")` into ordered unique URL list (values only, preserve first-seen order).
   - For each `u` in `new_urls`, append if `normalize_link(u)` not already represented.
   - Return `enumerate_array("", merged_urls)` or `""` if empty.

6. Add `_assemble_pjl_content(pjl_scrape_pages: list) -> str`:

   - For each record at index `n` (1-based), emit:

     ```
     === PAGE {n}: {url} ===
     {visible_text}
     ```

   - Join sections with `\n\n` (no `--- NEW LINKS ---` block in persisted assembled content — nav lives in `pjl_nav_links`; **AST-720** can join if needed).

7. **Do not** modify `_fetch_job_links_content` or `find_job_page` in this stage.

---

## Stage 3: Gazer — `fetch_job_pages_batch`

**Done when:** Batch scrapes pending PJL URLs per company, persists additive `pjl_*` fields, transitions to `PJL_READY` or `JOBSITE_SCRAPE_ISSUE`, returns `{passed, failed, total}` like `fetch_website_batch`.

1. In `src/core/gazer.py`, update module docstring in-scope list to include `fetch_job_pages_batch`.

2. Add imports from `src.core.roster`:

   ```python
   _assemble_pjl_content,
   _merge_pjl_nav_links,
   _merge_pjl_scrape_record,
   _pjl_scrape_ledger_keys,
   _scrape_pjl_page,
   ```

   Also import `normalize_link` from `src.utils.formatting`.

3. Add `async def fetch_job_pages_batch(batch_id, companies, debug=False) -> Dict[str, int]` modeled on `fetch_website_batch` (lines ~265–375):

   **Preamble:** `check_connectivity()` or raise; load `cfg = GAZER_CONFIG["fetch_job_pages"]`; `pass_state` / `fail_state`; `asyncio.Semaphore(3)`; shared `create_browser_context()`.

   **Per company (`_fetch_one`):**

   - `short_name`, `cd = company.get("company_data") or {}`.
   - `candidate_urls = cd.get("possible_joblist_links") or []` — list of URL strings (**AST-718**). If empty, log warning, `transition_company_state(short_name, fail_state)`, `failed += 1`, return.
   - `pjl_pages = list(cd.get("pjl_scrape_pages") or [])` (copy for mutation).
   - `ledger = _pjl_scrape_ledger_keys(pjl_pages)`.
   - `pending = [u for u in candidate_urls if normalize_link(u) not in ledger]`.
   - `new_nav_urls: list[str] = []`.

   **Scrape loop** — for `url_idx, url` in `enumerate(pending, start=1)`:

   - `record = await _scrape_pjl_page(url, browser_context, debug=debug)`.
   - When `debug=True`, `debug_index` func=`gazer.fetch_job_pages_batch`, identifier=`short_name`, outcome includes url + chars scraped or error.
   - `pjl_pages = _merge_pjl_scrape_record(pjl_pages, record)`.
   - Extend `new_nav_urls` with `record.get("page_links") or []` (dedupe later in merge).

   **Persist + transition:**

   - `assembled = _assemble_pjl_content(pjl_pages)`.
   - `merged_nav = _merge_pjl_nav_links(cd.get("pjl_nav_links") or "", new_nav_urls)`.
   - `data_to_save = {"pjl_scrape_pages": pjl_pages, "pjl_assembled_content": assembled}`.
   - If `merged_nav`: `data_to_save["pjl_nav_links"] = merged_nav`.
   - `save_company_data(short_name, data_to_save)`.

   - If `pjl_pages` non-empty → `transition_company_state(short_name, pass_state)`; `passed += 1`.
   - Else → `transition_company_state(short_name, fail_state)`; optional `save_company_data` note `prefilter_company_notes`: `"fetch_job_pages: all PJL scrapes failed"`; `failed += 1`.

   - **Do not** set `job_site` or clear `possible_joblist_links`.

   **Re-run idempotency:** When all `candidate_urls` already in ledger, `pending` is empty, `pjl_pages` unchanged, still non-empty → transition **`PJL_READY`** (no duplicate scrape work).

4. Return `{"passed": passed, "failed": failed, "total": len(companies)}` with debug batch summary matching `fetch_website_batch`.

---

## Stage 4: Consult routing + debug surfaces

**Done when:** Scheduled Actions `fetch_job_pages` dispatch appears as its own Execution History batch; `debug=True` traces each PJL URL scrape.

1. In `src/core/consult.py`, inside `run_consult_task` `entity_type == "company"` block, after the `fetch_website` branch, add:

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

2. **Do not** add a `run_company_task` branch for `PREFILTER_PASSED` + `fetch_job_pages` — consult route is the only entry (same as `fetch_website`).

3. Confirm dispatcher `batch_call_mode=0` path calls `run_consult_task` with `dispatch_task_key="fetch_job_pages"` once per claimed company — no code change expected if defaults from Stage 1 are correct.

4. AST-538: debug coverage is in Stage 3 (`gazer.fetch_job_pages_batch` + `roster._scrape_pjl_page.scrape_readiness`). No new production `logger.info` strings.

---

## Execution contract (for the developer agent)

- Execute stages in order; **one commit per stage** on **`astral-AST-716`**, publish each to **`origin/sub/AST-716/fetch-job-pages-batch-scrape`** via `git push origin HEAD:sub/AST-716/fetch-job-pages-batch-scrape` with **`--session astral-AST-716`**.
- If **`possible_joblist_links`** or **`normalize_link`** are missing at build time, stop and comment on **AST-716** — merge **AST-718** product commits first; do not reimplement hydration here.
- Stops if monolithic `find_job_page` must change to function — out of scope; escalate on parent.

---

## Self-Assessment

**Scope:** `Single-Component` — config + gazer batch + roster scrape helpers + one consult route; no UI, DB schema, or agent task changes.

**Conf:** `high` — Direct mirror of **AST-701** `fetch_website_batch`; scrape/readiness code already exists in `_fetch_job_links_content`; additive storage shape is explicit in parent **AST-716** AC #3.

**Risk:** `Medium` — Wrong skip/merge logic could duplicate PJL text or block **AST-720** `select_job_page`; mitigated by `normalize_link` ledger and persisted `pjl_assembled_content` contract documented here.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Scrape/readiness extracted to `_scrape_pjl_page`; gazer batch mirrors `fetch_website_batch` |
| §2.1 config | States, gazer block, dispatch registry, data keys in config |
| §2.4 batch | Uses existing claim/process/release; `batch_call_mode=0` per company |
| §2.6 state machine | Transitions in config; `transition_company_state` only |
| §3.3 imports | Gazer imports roster helpers; formatting for `normalize_link` |
| §3.5 naming | `pjl_*` keys snake_case; dispatch key `fetch_job_pages` matches task family |

No unresolved conflicts.
