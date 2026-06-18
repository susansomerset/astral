# AST-720 — select_job_page dispatch refactor

**Linear:** [AST-720 — select_job_page dispatch refactor (find_job_page logic confirmation)](https://linear.app/astralcareermatch/issue/AST-720/select-job-page-dispatch-refactor-find-job-page-logic-confirmation)

**Parent (reference only):** [AST-716 — find_job_page logic confirmation](https://linear.app/astralcareermatch/issue/AST-716/find-job-page-logic-confirmation)

**Publish ref:** `origin/sub/AST-716/select-job-page-dispatch-refactor`

**Summary:** Refactor **`select_job_page`** into an independent dispatch hop from **`PJL_READY`**: load **`pjl_assembled_content`** / **`pjl_scraped_pages`** produced by **`fetch_job_pages`** (**AST-719**), call the existing **`select_job_page`** agent task, and route outcomes to **`JOBLIST_IDENTIFIED`**, **`PREFILTER_PASSED_RETRY`**, or **`NO_PJL_SELECTED`** with **`normalize_link`** dedupe against **`possible_joblist_links`** (**AST-718**). Preserve **`TRY_LINKS`**, **`JOBSITE_SCRAPE_ISSUE`**, and **`JOBLIST_NO_JOBS`** behavior from **AST-469** / **AST-689** / **AST-692** without invoking **`parse_job_list`** or writing **`companies.job_site`** on the identified path (**AST-673**; **AST-721** owns parse + **`WATCH`**). Legacy **`TO_WATCH`** **`select_job_page`** dispatch (**AST-535**) stays until **AST-721** removes the monolith.

**Build gate (siblings):** **AST-718** (`possible_joblist_links`, `normalize_link()`) and **AST-719** (`PJL_READY`, `pjl_scraped_pages`, `pjl_assembled_content`) must be **`code()`-complete on `origin/ftr/AST-716-find-job-page-logic-confirmation`** before **build-child** for this ticket.

**Out of scope:** `parse_job_list` DOM reload / **`WATCH`** transition (**AST-721**), `fetch_job_pages` scrape batch implementation (**AST-719**), monolithic **`find_job_page`** removal (**AST-721**), select_job_page agent prompt edits, UI.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOBLIST_IDENTIFIED`, `PREFILTER_PASSED_RETRY`, `NO_PJL_SELECTED` + transitions; `ROSTER_CONFIG["select_job_page"]`; extend **`fetch_job_pages`** default trigger list for **`PREFILTER_PASSED_RETRY`**; `_dispatch_trigger_state_for_task_key("select_job_page")` → **`PJL_READY`** | utils |
| `src/core/roster.py` | PJL_READY branch in `run_select_job_page_dispatch`; map rebuild from persisted PJL data; `decomposed=True` path in `_find_job_page_from_assembled`; `_finalize_joblist_identified`; `run_company_task` branch for **`PJL_READY`**; AST-538 debug | core |

**Verify only (Betty / qa-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | PJL_READY: `JOBLIST_TITLES` → `JOBLIST_IDENTIFIED` (no parse, `job_site` column empty); `TRY_LINKS` new URLs → `PREFILTER_PASSED_RETRY` + ledger append; exhausted `TRY_LINKS` → `NO_PJL_SELECTED`; `JOBSITE_SCRAPE_ISSUE` / `JOBLIST_NO_JOBS` unchanged |
| `tests/component/utils/test_config.py` | New states, transitions, `select_job_page` default trigger `PJL_READY` |

**Read-only reuse (do not duplicate):**

| Symbol | Location | Use |
|--------|----------|-----|
| `_find_job_page_from_assembled` | `src/core/roster.py` | Agent loop + one `TRY_LINKS` iteration — extend with `decomposed` flag; do not fork a second `do_task` caller |
| `_check_parse_results` | `src/core/roster.py` | `JOBLIST_NO_JOBS`, `JOBSITE_SCRAPE_ISSUE`, default fallthrough |
| `run_select_job_page_dispatch` | `src/core/roster.py` | AST-535 **`TO_WATCH`** body unchanged behind state gate |
| `normalize_link` | `src/utils/formatting.py` | Dedupe `try_links` against `possible_joblist_links` |
| `parse_enumerate_array` | `src/utils/formatting.py` | Resolve numeric `try_links` entries against `nav_links` |
| `_save_company`, `save_company_data`, `transition_company_state` | `src/core/roster.py` | Persistence + AST-673 rules |
| `_fetch_job_links_content` | `src/core/roster.py` | Legacy **`TO_WATCH`** path only — **`PJL_READY`** must not scrape on entry |

---

## Stage 1: Config — selection states, retry loop, dispatch triggers

**Done when:** State machine admits **`JOBLIST_IDENTIFIED`**, **`PREFILTER_PASSED_RETRY`**, **`NO_PJL_SELECTED`**; admin default for **`select_job_page`** is **`trigger_state=PJL_READY`**; **`fetch_job_pages`** can be seeded for **`PREFILTER_PASSED_RETRY`**.

1. In `src/utils/config.py`, inside **`COMPANY_STATES`**, add:

   ```python
   "JOBLIST_IDENTIFIED": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
   "PREFILTER_PASSED_RETRY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
   "NO_PJL_SELECTED": {},
   ```

   ⚠️ **Decision:** **`NO_PJL_SELECTED`** has no batch criteria — terminal/holding (parent brief; future CSE action out of epic scope).

2. In **`ASTRAL_CONFIG["company_state_transitions"]`**, append (keep all existing tuples):

   ```python
   ("PJL_READY", "JOBLIST_IDENTIFIED"),
   ("PJL_READY", "PREFILTER_PASSED_RETRY"),
   ("PJL_READY", "NO_PJL_SELECTED"),
   ("PJL_READY", "NO_OPENINGS"),
   ("PJL_READY", "JOBSITE_SCRAPE_ISSUE"),
   ("PJL_READY", "NO_JOBLIST"),
   ("PREFILTER_PASSED_RETRY", "PJL_READY"),
   ("PREFILTER_PASSED_RETRY", "NO_JOBLIST"),
   ("PREFILTER_PASSED_RETRY", "JOBSITE_SCRAPE_ISSUE"),
   ```

3. After **`ROSTER_CONFIG["locate_job_page"]`**, add:

   ```python
   "select_job_page": {
       "dispatch_trigger_state": "PJL_READY",
       "pass_states": ["JOBLIST_IDENTIFIED", "PREFILTER_PASSED_RETRY"],
       "retry_state": "PREFILTER_PASSED_RETRY",
       "identified_state": "JOBLIST_IDENTIFIED",
       "exhausted_state": "NO_PJL_SELECTED",
       "pjl_url_data_key": "possible_joblist_links",
       "selected_pjl_url_key": "selected_pjl_url",
   },
   ```

4. Extend **`fetch_job_pages`** admin default trigger (**AST-719** integration — do not reimplement the batch):

   In **`GAZER_CONFIG["fetch_job_pages"]`** (added by AST-719), add:

   ```python
   "input_states": ["PREFILTER_PASSED", "PREFILTER_PASSED_RETRY"],
   ```

   In **`_dispatch_trigger_state_for_task_key`**, for **`task_key == "fetch_job_pages"`**, return **`"PREFILTER_PASSED"`** (admin template default for new rows). Susan may create a second scheduled row with **`trigger_state=PREFILTER_PASSED_RETRY`** manually — UNIQUE is **`(candidate_id, task_key, trigger_state)`**, so both rows may coexist. **Do not** add automatic DB seed for the retry row in this ticket.

5. In **`_dispatch_trigger_state_for_task_key`**, replace the locate-trio branch:

   ```python
   if task_key == "select_job_page":
       return ROSTER_CONFIG["select_job_page"]["dispatch_trigger_state"]
   if task_key in ("find_job_page", "parse_job_list"):
       return ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"][0]
   ```

   ⚠️ **Decision:** Default admin trigger for **`select_job_page`** becomes **`PJL_READY`**. Legacy **`TO_WATCH`** rows from **AST-535** remain valid until **AST-721** — do not delete or migrate them here.

6. **Do not** add **`PJL_READY`** to **`locate_job_page.dispatch_input_states`** (monolith **`find_job_page`** still uses **`PREFILTER_PASSED`** until **AST-721**).

---

## Stage 2: Roster — rebuild PJL maps from persisted scrape data

**Done when:** Given **`company_data`** from **AST-719**, roster builds **`assembled_content`**, **`page_url_map`**, and **`visible_map`** without Playwright, and can append deduped URLs to **`possible_joblist_links`**.

1. In `src/core/roster.py`, add **`normalize_link`** to the existing **`src.utils.formatting`** import line.

2. Add **`_pjl_maps_from_company_data(cdata: Dict[str, Any]) -> Tuple[str, Dict[int, str], Dict[int, str]]`**:

   - Prefer **`pjl_assembled_content`** when non-empty after strip.
   - Else rebuild from **`pjl_scraped_pages`** (list of **`{url_key, url, visible_text, new_links}`** per AST-719): for index **`i`** starting at 1, section `=== PAGE {i}: {url} ===\n{visible_text or "(no visible text)"}` joined by **`"\n\n"`**.
   - **`page_url_map`**: `{i: row["url"] or row["url_key"]}` in list order (1-based keys).
   - **`visible_map`**: `{i: row.get("visible_text") or ""}`.
   - If both assembled string and pages list are empty → return **`("", {}, {})`**.

3. Add **`_merge_try_links_into_pjl_ledger(try_links: List[Any], nav_links: str, existing: List[str]) -> Tuple[List[str], List[str]]`**:

   - **`existing`**: current **`possible_joblist_links`** (ordered normalized keys).
   - **`seen = set(existing)`**.
   - **`url_map = parse_enumerate_array(nav_links)`** for index resolution.
   - For each **`item`** in **`try_links`**:
     - If **`item`** is int or numeric string: **`raw = url_map.get(int(item))`**; else **`raw = str(item)`**.
     - **`key = normalize_link(raw)`**; skip if falsy or **`key in seen`**.
     - Append **`key`** to a **`added`** list and add to **`seen`**.
   - Return **`(existing + added, added)`** — caller persists only when **`added`** is non-empty.

4. **Do not** add Playwright imports or calls in this stage.

---

## Stage 3: Roster — PJL_READY select outcomes (no parse, no entry scrape)

**Done when:** **`run_select_job_page_dispatch`** serves **`PJL_READY`** from persisted assembly; **`JOBLIST_TITLES`** → **`JOBLIST_IDENTIFIED`** without parse or **`job_site`** column write; **`TRY_LINKS`** → retry or exhausted states; **`JOBSITE_SCRAPE_ISSUE`** / **`JOBLIST_NO_JOBS`** unchanged.

1. At top of **`run_select_job_page_dispatch`**, after loading **`company`** / **`cdata`**, branch on state:

   - If **`(entity.get("state") or company.get("state")) != "PJL_READY"`**: execute existing AST-535 body unchanged (lines ~750–779: **`possible_job_links`** + live **`_fetch_job_links_content`** + **`_find_job_page_from_assembled(..., chain_parse=False)`**).
   - **`PJL_READY`** path continues below.

2. **`PJL_READY`** path:

   ```python
   assembled_content, page_url_map, visible_map = _pjl_maps_from_company_data(cdata)
   ```

   - If not **`assembled_content.strip()`**:
     - Load pre-run **`job_site`** via **`get_company`**; call **`_save_company(..., state=ROSTER_CONFIG["select_job_page"]["exhausted_state"], page_option_url=company_website, raw_response={"response_type": "NO_PJL_ASSEMBLED"}, pre_run_job_site=pre_js)`**.
     - Return **`{"short_name": short_name, "state": "NO_PJL_SELECTED", "job_site": "", "response_type": "NO_PJL_ASSEMBLED"}`**.

   - Call **`_find_job_page_from_assembled(..., assembled_content=..., page_url_map=..., page_dom_map={}, visible_map=..., nav_links=cdata.get("nav_links") or "", browser_context=None, chain_parse=False, decomposed=True)`**.

3. Add keyword-only **`decomposed: bool = False`** to **`_find_job_page_from_assembled`** (default **`False`** — all existing callers unchanged).

   When **`decomposed=True`**:

   - **`TRY_LINKS`** (one iteration only — keep existing **`try_link_retry_pending`** flag):
     - Do **not** call **`_fetch_job_links_content`**.
     - **`try_links = parsed_top.get("try_links") or []`**
     - If empty or second **`TRY_LINKS`**: fall through to exhausted handling (step 4 bullet below).
     - Else:
       - **`ledger = list(cdata.get(ROSTER_CONFIG["select_job_page"]["pjl_url_data_key"]) or [])`**
       - **`updated, added = _merge_try_links_into_pjl_ledger(try_links, cdata.get("nav_links") or "", ledger)`**
       - If **`added`**:
         - **`save_company_data(short_name, {pjl_url_data_key: updated})`**
         - **`transition_company_state(short_name, ROSTER_CONFIG["select_job_page"]["retry_state"])`**
         - Return **`{"short_name": short_name, "state": "PREFILTER_PASSED_RETRY", "job_site": "", "response_type": "TRY_LINKS"}`**
       - Else: exhausted (no new unique normalized URLs) — step 4.

   - **`JOBLIST_TITLES`**: call **`_finalize_joblist_identified(...)`** (new helper below) — **not** **`_finalize_joblist_titles_select_only`** / chain finalizer.

   - **All other `response_type` values**: delegate to **`_check_parse_results(...)`** unchanged. Pass **`page_dom_map={}`**, **`selected_page`** from parsed response, **`job_site_url = page_url_map.get(selected_page, company_website)`**.

4. Add **`async def _finalize_joblist_identified(...)`** (select-only, no parse):

   - Persist **`job_titles`** and **`selected_pjl_url`** (= **`job_site_url`**, the chosen list page URL) via **`save_company_data`**.
   - If **`visible_map.get(int(selected_page))`** non-empty: also save **`job_list_visible`**.
   - **`transition_company_state(short_name, "JOBLIST_IDENTIFIED")`** — **do not** call **`update_company(..., job_site=...)`**.
   - **`_save_company(..., state="JOBLIST_IDENTIFIED", page_option_url=job_site_url, raw_response=select_parsed, pre_run_job_site=str((get_company(short_name) or {}).get("job_site") or ""))`** so **`_job_site_for_persist`** leaves column empty (**`JOBLIST_IDENTIFIED` ∉ `_PERSIST_PAGE_OPTION_URL_STATES`**).
   - Return **`{"short_name": short_name, "state": "JOBLIST_IDENTIFIED", "job_site": "", "response_type": response_type}`**.

5. Exhausted **`TRY_LINKS`** / empty try list on decomposed path:

   - **`_save_company(..., state="NO_PJL_SELECTED", page_option_url=company_website, raw_response=parsed_top, pre_run_job_site=pre_js)`**
   - Return **`{"short_name": short_name, "state": "NO_PJL_SELECTED", "job_site": "", "response_type": "TRY_LINKS"}`**.

6. **`SELECT_FAILED`** on decomposed path: keep existing **`NO_JOBLIST`** mapping (no new state name).

---

## Stage 4: `run_company_task` routing + debug

**Done when:** Dispatcher runs **`run_select_job_page_dispatch`** for **`input_state=PJL_READY`** + **`dispatch_task_key=select_job_page`**; summary counts treat explicit terminal/intermediate outcomes as processed; AST-538 detail when **`debug=True`**.

1. In **`run_company_task`**, insert **before** the **`locate_job_page.dispatch_input_states`** branch (~line 682):

   ```python
   elif input_state == ROSTER_CONFIG["select_job_page"]["dispatch_trigger_state"]:
       tk = (dispatch_task_key or "").strip()
       if tk != "select_job_page":
           logger.warning(
               "run_company_task: PJL_READY expects select_job_page, got %r for %s",
               tk or None, short_name,
           )
           return {**zero, "total_errors": 1}
       result = await run_select_job_page_dispatch(entity, batch_id, ctx, debug)
       sel_cfg = ROSTER_CONFIG["select_job_page"]
       if result.get("error"):
           err_st = ROSTER_CONFIG.get("locate_job_page", {}).get("error_state")
           if err_st:
               transition_company_state(short_name, err_st)
           return {**zero, "total_errors": 1}
       terminal_ok = frozenset({
           sel_cfg["identified_state"],
           sel_cfg["retry_state"],
           sel_cfg["exhausted_state"],
           "NO_OPENINGS",
           "JOBSITE_SCRAPE_ISSUE",
           "NO_JOBLIST",
       })
       if result.get("state") in terminal_ok:
           return {**zero, "total_passed": 1}
       return {**zero, "total_failed": 1}
   ```

   ⚠️ **Decision:** Explicit state transitions (**including **`NO_PJL_SELECTED`**) count as successful dispatch completion — mirror gazer batch semantics. Only API/exception failures increment **`total_errors`**.

2. **Consult routing:** No code change if **`run_consult_task`** already delegates **`entity_type=="company"`** to **`roster.run_company_task`** with **`dispatch_task_key`** — verify in **build-child** only.

3. **AST-538** on **`PJL_READY`** path when **`debug=True`**:

   - Before agent: **`debug_index(func="roster.run_select_job_page_dispatch", index=1, total=1, identifier=short_name, outcome=f"pages={len(page_url_map)} assembled_chars={len(assembled_content)}")`**.
   - After outcome: **`debug_detail(f"response_type={response_type} -> state={result_state}")`** in **`_find_job_page_from_assembled`** decomposed exit paths.

4. **Do not** modify monolithic **`find_job_page`** in this ticket.

---

## Self-Assessment

**Scope:** `Single-Component` — config state keys + roster select/dispatch routing; no UI, no new agent tasks, no parse hop.

**Conf:** `Medium` — reuses **`_find_job_page_from_assembled`** and **`_check_parse_results`**, but persisted PJL shape and sibling build order (**AST-718** / **AST-719**) must land first.

**Risk:** `Medium` — wrong state or **`job_site`** write breaks the decomposed chain and regresses **AST-673**; legacy **`TO_WATCH`** path must remain bit-identical until **AST-721**.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §2.1 config | New states + `ROSTER_CONFIG["select_job_page"]` centralized |
| §2.6 state machine | Transitions explicit; core calls `transition_company_state` only |
| §1.3 DRY | Extends `_find_job_page_from_assembled`; no parallel agent module |
| §1.5.1 debug | Style D headers on PJL_READY path when `debug=True` |
| §3.3 imports | `normalize_link` from formatting; roster → consult unchanged |
| §3.5 naming | snake_case keys; states match parent brief |

No unresolved conflicts.

---

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-716/select-job-page-dispatch-refactor`  
**Product commits:** `7b58fc12` (Stage 1 — config), `74ae5627` (Stages 2–4 — PJL helpers, decomposed routing, `run_company_task` PJL_READY entry)
