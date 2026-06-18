# AST-720 — select_job_page dispatch refactor

**Linear:** [AST-720 — select_job_page dispatch refactor (find_job_page logic confirmation)](https://linear.app/astralcareermatch/issue/AST-720/select-job-page-dispatch-refactor-find-job-page-logic-confirmation)

**Parent (reference only):** [AST-716 — find_job_page logic confirmation](https://linear.app/astralcareermatch/issue/AST-716/find-job-page-logic-confirmation)

**Publish ref:** `origin/sub/AST-716/select-job-page-dispatch-refactor`

**Summary:** Refactor **`select_job_page`** into an independent dispatch hop from **`PJL_READY`**: load **`pjl_assembled_content`** produced by **`fetch_job_pages`** (**AST-719**), call the existing **`select_job_page`** agent task, and route outcomes to **`JOBLIST_IDENTIFIED`**, **`PREFILTER_PASSED_RETRY`**, or **`NO_PJL_SELECTED`** with **`normalize_link`** dedupe against **`possible_joblist_links`** (**AST-718**). Preserve **`TRY_LINKS`** / **`JOBSITE_SCRAPE_ISSUE`** / **`JOBLIST_NO_JOBS`** terminal behavior from **AST-689** / **AST-692** / **AST-469** without invoking **`parse_job_list`** or setting **`job_site`** (**AST-673**, **AST-721** owns parse). Legacy **`TO_WATCH`** **`select_job_page`** dispatch (**AST-535**) stays until **AST-721** removes the monolith.

**Depends on:** **AST-718** (`possible_joblist_links`, `normalize_link()`), **AST-719** (`PJL_READY`, `pjl_assembled_content`, `pjl_scrape_pages`, `pjl_nav_links`). Merge sibling product commits on **`origin/ftr/AST-716-find-job-page-logic-confirmation`** before **build-child**.

**Out of scope:** `parse_job_list` DOM reload / **`WATCH`** transition (**AST-721**), `fetch_job_pages` scrape batch (**AST-719**), monolithic **`find_job_page`** removal (**AST-721**), select_job_page agent prompt changes, UI.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOBLIST_IDENTIFIED`, `PREFILTER_PASSED_RETRY`, `NO_PJL_SELECTED` states + transitions; `ROSTER_CONFIG["select_job_page"]`; extend `fetch_job_pages` dispatch trigger for retry; `_dispatch_trigger_state_for_task_key("select_job_page")` → `PJL_READY` | utils |
| `src/core/roster.py` | PJL_READY entry for `run_select_job_page_dispatch`; map rebuild from persisted PJL data; decomposed TRY_LINKS / JOBLIST_TITLES outcome helpers; `run_company_task` branch for `PJL_READY`; AST-538 debug on touched paths | core |

**Verify only (Betty / qa-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | PJL_READY dispatch: JOBLIST_TITLES → `JOBLIST_IDENTIFIED` (no parse, `job_site` unset); TRY_LINKS new URLs → `PREFILTER_PASSED_RETRY` + ledger append; TRY_LINKS exhausted → `NO_PJL_SELECTED`; `JOBSITE_SCRAPE_ISSUE` / `JOBLIST_NO_JOBS` preserved |
| `tests/component/utils/test_config.py` | New states, transitions, `select_job_page` dispatch default trigger `PJL_READY`; `fetch_job_pages` accepts `PREFILTER_PASSED_RETRY` |

**Read-only reuse (do not duplicate):**

| Symbol | Location | Use |
|--------|----------|-----|
| `_find_job_page_from_assembled` | `src/core/roster.py` | Agent loop, `TRY_LINKS` once, `do_task("select_job_page", …)` — extend via flags, do not fork a second agent caller |
| `_check_parse_results` | `src/core/roster.py` | `JOBLIST_NO_JOBS`, `JOBSITE_SCRAPE_ISSUE`, default `NO_JOBLIST` mapping |
| `run_select_job_page_dispatch` | `src/core/roster.py` | AST-535 TO_WATCH legacy body — keep behind state branch |
| `normalize_link` | `src/utils/formatting.py` | Dedupe `try_links` against `possible_joblist_links` |
| `parse_enumerate_array` / `enumerate_array` | `src/utils/formatting.py` | Resolve agent link tokens against `pjl_nav_links` + homepage `nav_links` when needed |
| `_save_company`, `save_company_data`, `_strip_company_data_keys` | `src/core/roster.py` | Persistence + AST-673 `job_site` rules |
| `make_locate_parse_resolver` | `src/core/roster.py` | **Do not** wire on PJL_READY path (`chain_parse=False`) |
| `_fetch_job_links_content` | `src/core/roster.py` | Legacy TO_WATCH path only — PJL_READY must not re-scrape on entry |

---

## Stage 1: Config — selection states, retry loop, dispatch trigger

**Done when:** Company state machine admits `JOBLIST_IDENTIFIED`, `PREFILTER_PASSED_RETRY`, `NO_PJL_SELECTED`; `select_job_page` admin default `trigger_state` is `PJL_READY`; `fetch_job_pages` can be scheduled from `PREFILTER_PASSED_RETRY`.

1. In `src/utils/config.py`, inside `COMPANY_STATES`, add:

   ```python
   "JOBLIST_IDENTIFIED": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
   "PREFILTER_PASSED_RETRY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
   "NO_PJL_SELECTED": {},
   ```

   ⚠️ **Decision:** `NO_PJL_SELECTED` has no `batch_criteria` — terminal/holding (parent brief; future CSE action out of scope).

2. In `ASTRAL_CONFIG["company_state_transitions"]`, append (keep all existing tuples):

   ```python
   ("PJL_READY", "JOBLIST_IDENTIFIED"),
   ("PJL_READY", "PREFILTER_PASSED_RETRY"),
   ("PJL_READY", "NO_PJL_SELECTED"),
   ("PJL_READY", "NO_OPENINGS"),
   ("PJL_READY", "JOBSITE_SCRAPE_ISSUE"),
   ("PJL_READY", "NO_JOBLIST"),
   ("PREFILTER_PASSED_RETRY", "PJL_READY"),
   ("PREFILTER_PASSED_RETRY", "JOBSITE_SCRAPE_ISSUE"),
   ```

3. After `ROSTER_CONFIG["locate_job_page"]`, add:

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

4. Extend **`fetch_job_pages`** dispatch trigger (**AST-719** integration — do not reimplement batch):

   In `_dispatch_trigger_state_for_task_key`, replace the single-string return for `fetch_job_pages` with logic that reads a new config list:

   ```python
   "fetch_job_pages_trigger_states": ["PREFILTER_PASSED", "PREFILTER_PASSED_RETRY"],
   ```

   under `GAZER_CONFIG["fetch_job_pages"]` (or `ROSTER_CONFIG` if `GAZER_CONFIG` block not yet present — match **AST-719** plan location). Dispatcher claim SQL already matches `trigger_state` on the row; this step only fixes **default row seeding** and any helper that resolves trigger for admin UI. **build-child** must ensure a `dispatch_tasks` row exists for `fetch_job_pages` with `trigger_state=PREFILTER_PASSED_RETRY` (Susan seeds or migration script per existing prefilter pattern — do not invent new seed machinery).

5. In `_dispatch_trigger_state_for_task_key`, change the locate trio branch:

   ```python
   if task_key == "select_job_page":
       return ROSTER_CONFIG["select_job_page"]["dispatch_trigger_state"]
   if task_key in ("find_job_page", "parse_job_list"):
       return ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"][0]
   ```

   ⚠️ **Decision:** Default admin trigger for **`select_job_page`** becomes **`PJL_READY`**; legacy **`TO_WATCH`** rows seeded under **AST-535** remain valid until **AST-721** — do not delete them in this ticket.

6. **Do not** add `PJL_READY` to `locate_job_page.dispatch_input_states` (monolith **`find_job_page`** still uses `PREFILTER_PASSED` there until **AST-721**).

---

## Stage 2: Roster — rebuild PJL maps from persisted scrape data

**Done when:** Given `company_data` from **AST-719**, roster can build `assembled_content`, `page_url_map`, and `visible_map` without Playwright, and can append deduped URLs to `possible_joblist_links`.

1. In `src/core/roster.py`, import `normalize_link` from `src.utils.formatting`.

2. Add `_pjl_maps_from_company_data(cdata: dict) -> tuple[str, dict[int, str], dict[int, str]]`:

   - Read `pjl_assembled_content` (str). If non-empty after strip, use as `assembled_content`.
   - Else rebuild from `pjl_scrape_pages` (list of `{"url", "visible_text"}`): for each index `i` starting at 1, append section `=== PAGE {i}: {url} ===\n{visible_text}` joined by `\n\n` (same shape as `_fetch_job_links_content` / **AST-719**).
   - Build `page_url_map`: `{i: url}` from `pjl_scrape_pages` order (1-based keys).
   - Build `visible_map`: `{i: visible_text}` from same records.
   - Return `(assembled_content, page_url_map, visible_map)`.
   - Empty `pjl_scrape_pages` and empty assembled string → return `("", {}, {})`.

3. Add `_merge_try_links_into_pjl_ledger(short_name: str, try_links: list, nav_links: str, pjl_nav_links: str, existing: list) -> list[str]`:

   - `existing` is current `possible_joblist_links` (ordered normalized URL strings).
   - Build `seen = {normalize_link(u) for u in existing if normalize_link(u)}`.
   - For each item in `try_links` (agent output list):
     - If item is int or numeric string, resolve via `parse_enumerate_array(pjl_nav_links or nav_links, index)` then `normalize_link`.
     - Else treat as URL string → `normalize_link`.
     - Skip empty keys; if key not in `seen`, append to `existing` list and add to `seen`.
   - Return the updated list (may be identical to input if no new keys).

4. Add `_nav_links_for_try_links(cdata: dict) -> str`:

   - Return `(cdata.get("pjl_nav_links") or cdata.get("nav_links") or "").strip()` — merged PJL nav from **AST-719** with homepage fallback.

---

## Stage 3: Roster — PJL_READY `select_job_page` outcomes (no parse, no entry scrape)

**Done when:** `run_select_job_page_dispatch` serves **`PJL_READY`** companies using persisted assembly, routes **`JOBLIST_TITLES`** to **`JOBLIST_IDENTIFIED`** without `parse_job_list` or `job_site` column write, routes **`TRY_LINKS`** to retry or exhausted states per parent AC, and preserves **`JOBSITE_SCRAPE_ISSUE`** / **`JOBLIST_NO_JOBS`** via existing helpers.

1. At top of `run_select_job_page_dispatch`, read `short_name`, `company_website`, load `company` / `cdata`. If `entity.get("state") != "PJL_READY"` (and company row state not `PJL_READY`), **fall through** to existing AST-535 body unchanged (lines ~750–779: `possible_job_links` + live `_fetch_job_links_content`).

2. For **`PJL_READY`** path:

   - `assembled_content, page_url_map, visible_map = _pjl_maps_from_company_data(cdata)`.
   - If not `assembled_content.strip()`:
     - `_save_company(..., state="NO_PJL_SELECTED", page_option_url=company_website, raw_response={"response_type": "NO_PJL_ASSEMBLED"})`.
     - Return `{"short_name": short_name, "state": "NO_PJL_SELECTED", "job_site": "", "response_type": "NO_PJL_ASSEMBLED"}`.
   - `nav_links = _nav_links_for_try_links(cdata)`.
   - Call `_find_job_page_from_assembled(..., page_dom_map={}, browser_context=None, chain_parse=False, decomposed=True)` — add keyword-only param `decomposed: bool = False` default **False** for legacy callers.

3. In `_find_job_page_from_assembled`, when `decomposed=True`:

   - **Do not** open `create_browser_context` in caller; assert `browser_context is None` and skip any scrape paths except documented below.
   - **`TRY_LINKS` branch** (replace inline `_fetch_job_links_content` retry):
     - After first `TRY_LINKS` response (still allow **one** TRY_LINKS iteration, matching monolith):
       - `try_links = parsed_top.get("try_links") or []`
       - `ledger = list(cdata.get(ROSTER_CONFIG["select_job_page"]["pjl_url_data_key"]) or [])`
       - `updated = _merge_try_links_into_pjl_ledger(short_name, try_links, cdata.get("nav_links") or "", cdata.get("pjl_nav_links") or "", ledger)`
       - If `updated != ledger`:
         - `save_company_data(short_name, {pjl_url_data_key: updated})`
         - `transition_company_state(short_name, ROSTER_CONFIG["select_job_page"]["retry_state"])`
         - Return `{"short_name": short_name, "state": "PREFILTER_PASSED_RETRY", "job_site": "", "response_type": "TRY_LINKS"}`
       - Else (no new unique normalized URLs):
         - `_save_company(..., state="NO_PJL_SELECTED", page_option_url=company_website, raw_response=parsed_top)`
         - Return `{"short_name": short_name, "state": "NO_PJL_SELECTED", "job_site": "", "response_type": "TRY_LINKS"}`
     - If `try_links` empty or second TRY_LINKS would fire (`try_link_retry_pending` false): same **`NO_PJL_SELECTED`** path as exhausted.
   - **`JOBLIST_TITLES` branch**: call new `_finalize_joblist_identified(...)` instead of `_finalize_joblist_titles_select_only` / `_finalize_joblist_titles_after_chain`.
   - **All other `response_type` values**: delegate to `_check_parse_results(..., page_dom_map=page_dom_map or {}, ...)` unchanged (covers `JOBLIST_NO_JOBS`, `JOBSITE_SCRAPE_ISSUE`, default `NO_JOBLIST`). Pass `job_site_url` from `page_url_map.get(selected_page, company_website)`; **`_check_parse_results` must not set `companies.job_site`** on these paths when `decomposed=True` — if `_save_company` would persist `job_site`, pass `pre_run_job_site=""` and verify `_job_site_for_persist` leaves column empty for `JOBLIST_IDENTIFIED` family (add `JOBLIST_IDENTIFIED` to non-persist job_site set if needed).

4. Add `_finalize_joblist_identified(select_parsed, short_name, company_website, job_site_url, visible_map, selected_page, response_type, debug, ctx)`:

   - `job_titles = select_parsed.get("job_titles", [])`.
   - `save_company_data(short_name, {"job_titles": job_titles, ROSTER_CONFIG["select_job_page"]["selected_pjl_url_key"]: job_site_url})`.
   - `vis_save = ""` from `visible_map.get(int(selected_page))` when `selected_page` is int-coercible.
   - If `vis_save`: `save_company_data(short_name, {"job_list_visible": vis_save})`.
   - `_save_company(short_name=short_name, company_website=company_website, state="JOBLIST_IDENTIFIED", page_option_url=job_site_url, raw_response=select_parsed)` — **do not** pass `job_site=` kwarg; column stays NULL (**AST-673**).
   - Debug (AST-538): `logger.test(f"index 1/1 | {short_name} | JOBLIST_IDENTIFIED | selected_url={job_site_url} titles={len(job_titles)}")`.
   - Return `{"short_name": short_name, "state": "JOBLIST_IDENTIFIED", "job_site": "", "response_type": response_type, "job_titles": job_titles}`.

5. **`SELECT_FAILED` / invalid parse** on decomposed path: transition `NO_JOBLIST` (existing) — acceptable terminal; do not introduce new state names.

---

## Stage 4: `run_company_task` routing + consult parity + debug

**Done when:** Dispatcher invokes `run_select_job_page_dispatch` for `input_state=PJL_READY` + `dispatch_task_key=select_job_page`; pass/fail counts use `ROSTER_CONFIG["select_job_page"]["pass_states"]`; AST-538 Style D headers appear on PJL_READY select path when `debug=True`.

1. In `run_company_task`, before the `locate_job_page` `dispatch_input_states` branch (~line 682), add:

   ```python
   elif input_state == ROSTER_CONFIG["select_job_page"]["dispatch_trigger_state"]:
       tk = (dispatch_task_key or "").strip()
       if tk != "select_job_page":
           logger.warning("run_company_task: PJL_READY expects select_job_page, got %s", tk)
           return {**zero, "total_errors": 1}
       result = await run_select_job_page_dispatch(entity, batch_id, ctx, debug)
       sel_cfg = ROSTER_CONFIG["select_job_page"]
       if result.get("error"):
           ...
       if result.get("state") in sel_cfg.get("pass_states", []):
           return {**zero, "total_passed": 1}
       if result.get("state") in (sel_cfg.get("identified_state"), sel_cfg.get("exhausted_state"), "NO_OPENINGS", "JOBSITE_SCRAPE_ISSUE", "NO_JOBLIST"):
           # identified + terminal outcomes are successful dispatch completion (state moved)
           return {**zero, "total_passed": 1}
       return {**zero, "total_failed": 1}
   ```

   ⚠️ **Decision:** `NO_PJL_SELECTED`, `JOBLIST_IDENTIFIED`, `NO_OPENINGS`, and `JOBSITE_SCRAPE_ISSUE` count as **passed** dispatch waves (company reached explicit terminal/intermediate state). Only unexpected errors / missing transitions count as failed — mirror `prefilter_company` / `fetch_website` gazer batches.

2. **Consult routing:** No change required if `run_consult_task` already delegates company entities to `roster.run_company_task` with `dispatch_task_key` — verify only in **build-child**; do not add a consult-only code path.

3. **AST-538 debug** on PJL_READY entry in `run_select_job_page_dispatch`:

   - Before agent call: `logger.test(f"index 1/1 | {short_name} | select_job_page | pages={len(page_url_map)} assembled_chars={len(assembled_content)}")`.
   - After outcome: one `logger.test` line with `response_type` and resulting state (handled in stage 3 helpers).

4. **Do not** remove or alter monolithic `find_job_page` in this ticket.

---

## Self-Assessment

**Scope:** `Single-Component` — primary work is `src/core/roster.py` select/dispatch routing plus `src/utils/config.py` state machine keys; no UI or new agent tasks.

**Conf:** `Medium` — outcome routing reuses `_find_job_page_from_assembled` and `_check_parse_results`, but PJL_READY persisted-shape integration depends on **AST-718**/**AST-719** landing first.

**Risk:** `Medium` — incorrect state transitions or `job_site` persistence would break the decomposed PJL chain and regress **AST-673**; legacy **TO_WATCH** path must remain untouched until **AST-721**.

## Rules self-review

- **§2.1 config:** All new states and `ROSTER_CONFIG["select_job_page"]` keys live in `config.py`.
- **§2.6 state machine:** Transitions listed explicitly; no silent `TO_WATCH` on decomposed path.
- **§1.3 DRY:** Reuses `_find_job_page_from_assembled`, `_check_parse_results`, `normalize_link`; no parallel agent caller.
- **§1.5.1 debug:** Style D `index | id | outcome` on PJL_READY path.
- **§3.3 imports:** `normalize_link` from `formatting` only; no new cross-layer violations.
