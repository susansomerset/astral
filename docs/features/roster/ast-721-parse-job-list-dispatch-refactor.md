# AST-721 — parse_job_list dispatch refactor and monolith removal

**Linear:** [AST-721 — parse_job_list dispatch refactor and monolith removal (find_job_page logic confirmation)](https://linear.app/astralcareermatch/issue/AST-721/parse-job-list-dispatch-refactor-and-monolith-removal-find-job-page)

**Parent (reference only):** [AST-716 — find_job_page logic confirmation](https://linear.app/astralcareermatch/issue/AST-716/find-job-page-logic-confirmation)

**Publish ref:** `origin/sub/AST-716/parse-job-list-dispatch-refactor`

**Summary:** After **`JOBLIST_IDENTIFIED`** (**AST-720**), run **`parse_job_list`** as its own dispatch hop: Playwright DOM reload of **`selected_pjl_url`** with **AST-689** careers-list readiness, existing **`find_job_containers`** trimming, **`_fetch_parse_job_list`** + validation, success → **`WATCH`** with **`job_site`** column set for the first time; first failure → **`JOBLIST_IDENTIFIED_RETRY`**, second failure → **`COULD_NOT_PARSE_JOBLIST`**. Retire the monolithic **`find_job_page`** dispatch chain (AST-535 **`TO_WATCH`** / **`PREFILTER_PASSED`** trio) in favor of the decomposed **`fetch_job_pages` → `select_job_page` → `parse_job_list`** pipeline; keep **`JOBS_FOUND`** **`jobs_found_process_job_site`** path (**AST-469**) unchanged. Close duplicate **AST-666** when shipped.

**Depends on:** **AST-718**–**AST-720** on **`origin/ftr/AST-716-find-job-page-logic-confirmation`** (`JOBLIST_IDENTIFIED`, `selected_pjl_url`, `job_titles`, `job_list_visible`). Merge ftr before **build-child**.

**Out of scope:** Prefilter routing (**AST-718**), `fetch_job_pages` batch (**AST-719**), `select_job_page` agent prompts, UI, new LLM task shapes.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOBLIST_IDENTIFIED_RETRY`, `COULD_NOT_PARSE_JOBLIST` states + transitions; `ROSTER_CONFIG["parse_job_list"]`; remove `find_job_page` from schedulable keys; narrow `locate_job_page.dispatch_input_states`; `_dispatch_trigger_state_for_task_key("parse_job_list")` → `JOBLIST_IDENTIFIED` | utils |
| `src/core/roster.py` | Decomposed `run_parse_job_list_dispatch`; shared parse finalize helpers; readiness-aware DOM reload; `run_company_task` `JOBLIST_IDENTIFIED` / `JOBLIST_IDENTIFIED_RETRY` branches; remove monolith `find_job_page` dispatch routing; delete `find_job_page()` entrypoint; remove legacy TO_WATCH bodies from `run_select_job_page_dispatch` | core |
| `src/ui/api/api_admin.py` | Adhoc preview: drop or guard `find_job_page` live-content builder if key removed from schedulable set | ui |

**Verify only (Betty / qa-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | Decomposed parse: success → `WATCH` + `job_site` set; first fail → `JOBLIST_IDENTIFIED_RETRY`; second fail → `COULD_NOT_PARSE_JOBLIST`; monolith dispatch routes removed; `JOBS_FOUND` path unchanged |
| `tests/component/utils/test_config.py` | New states/transitions; `parse_job_list` trigger `JOBLIST_IDENTIFIED`; `find_job_page` not schedulable |
| `tests/component/ui/api/test_api_admin.py` | Admin task_keys / adhoc no longer expose monolith `find_job_page` as schedulable default |
| `tests/component/core/test_dispatcher.py` | No `PREFILTER_PASSED → find_job_page` claim path |

**Read-only reuse (do not duplicate):**

| Symbol | Location | Use |
|--------|----------|-----|
| `run_parse_job_list_dispatch` | `src/core/roster.py` | Refactor in place — extract `_finalize_parse_dispatch_success` / `_parse_dispatch_failure_state` |
| `_scrape_job_site_dom` | `src/core/roster.py` | Extend or wrap with readiness (see Stage 2) |
| `wait_for_careers_list_readiness`, `roster_scrape_readiness_config` | `playwright.py` / `config.py` | AST-689 gate on DOM reload |
| `find_job_containers`, `_compute_container_index` | `formatting.py` / `roster.py` | Single/multi-title trim |
| `_fetch_parse_job_list`, `_validate_parse_job_list_raw_job_listings` | `src/core/roster.py` | Agent call + DOM validation |
| `_save_company`, `_job_site_for_persist` | `src/core/roster.py` | `WATCH` sets `job_site`; failures on decomposed path keep column empty (**AST-673**) |
| `jobs_found_process_job_site`, `_find_job_page_from_assembled` | `src/core/roster.py` | **JOBS_FOUND** only — do not delete |
| `_fetch_job_links_content` | `src/core/roster.py` | Used by **JOBS_FOUND** / internal helpers only after monolith removal |

**Dispatch rows (Susan / admin — not code seeds per AST-549):**

| Action | `task_key` | `trigger_state` |
|--------|------------|-----------------|
| **Add** | `parse_job_list` | `JOBLIST_IDENTIFIED` |
| **Add** | `parse_job_list` | `JOBLIST_IDENTIFIED_RETRY` |
| **Deactivate or delete** | `find_job_page` | `TO_WATCH`, `PREFILTER_PASSED` |
| **Deactivate or delete** | `select_job_page` | `TO_WATCH` (legacy AST-535) |
| **Deactivate or delete** | `parse_job_list` | `TO_WATCH` (legacy AST-535) |

Existing rows for **`fetch_job_pages`** / **`select_job_page` @ `PJL_READY`** come from **AST-719** / **AST-720**.

---

## Stage 1: Config — parse retry states and dispatch trigger

**Done when:** State machine admits `JOBLIST_IDENTIFIED_RETRY` and `COULD_NOT_PARSE_JOBLIST`; `parse_job_list` default `trigger_state` is `JOBLIST_IDENTIFIED`; `find_job_page` is not schedulable.

1. In `src/utils/config.py`, inside `COMPANY_STATES`, add:

   ```python
   "JOBLIST_IDENTIFIED_RETRY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
   "COULD_NOT_PARSE_JOBLIST": {},
   ```

2. In `ASTRAL_CONFIG["company_state_transitions"]`, append:

   ```python
   ("JOBLIST_IDENTIFIED", "WATCH"),
   ("JOBLIST_IDENTIFIED", "JOBLIST_IDENTIFIED_RETRY"),
   ("JOBLIST_IDENTIFIED", "COULD_NOT_PARSE_JOBLIST"),
   ("JOBLIST_IDENTIFIED_RETRY", "WATCH"),
   ("JOBLIST_IDENTIFIED_RETRY", "COULD_NOT_PARSE_JOBLIST"),
   ```

   Keep existing `→ CANNOT_PARSE_JOB_SITE` edges for **JOBS_FOUND** / legacy locate until a future cleanup ticket.

3. After `ROSTER_CONFIG["select_job_page"]` (from **AST-720**), add:

   ```python
   "parse_job_list": {
       "dispatch_trigger_state": "JOBLIST_IDENTIFIED",
       "retry_trigger_state": "JOBLIST_IDENTIFIED_RETRY",
       "pass_state": "WATCH",
       "retry_state": "JOBLIST_IDENTIFIED_RETRY",
       "terminal_fail_state": "COULD_NOT_PARSE_JOBLIST",
       "selected_pjl_url_key": "selected_pjl_url",
   },
   ```

4. In `_dispatch_trigger_state_for_task_key`, replace the locate trio branch with per-task config:

   ```python
   if task_key == "parse_job_list":
       return ROSTER_CONFIG["parse_job_list"]["dispatch_trigger_state"]
   if task_key == "select_job_page":
       return ROSTER_CONFIG["select_job_page"]["dispatch_trigger_state"]
   if task_key == "find_job_page":
       return ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"][0]
   ```

   (The `find_job_page` branch is removed in Stage 4 when the key is dropped from schedulable set.)

5. Narrow `ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]` to:

   ```python
   "dispatch_input_states": ["JOBS_FOUND"],
   ```

   Remove `"TO_WATCH"` and `"PREFILTER_PASSED"`. Update the comment above the key to state only **JOBS_FOUND** uses `jobs_found_process_job_site`.

6. Remove obsolete `INFLOW_CONFIG["locate"]` block (`dispatch_trigger_state: PREFILTER_PASSED`) if nothing in `src/` references it after grep — it targeted monolith locate dispatch (**AST-508**).

---

## Stage 2: Roster — DOM reload + shared parse finalize helpers

**Done when:** Helpers reload list-page DOM with readiness polling, run parse validation, and map failures to retry vs terminal states without setting `job_site` until `WATCH`.

1. Add `_scrape_list_page_dom_for_parse(url: str, browser_context, debug: bool) -> str` in `src/core/roster.py`:

   - Mirror single-page body inside `_fetch_job_links_content` (lines ~1770–1798): `get_page` → `wait_for_careers_list_readiness` with `roster_scrape_readiness_config()` → `extract_page_dom` → `close_page`.
   - AST-538 when `debug=True`: `logger.debug_index(func="roster._scrape_list_page_dom_for_parse", index=1, total=1, identifier=url, outcome=…)` plus `logger.debug_detail` for readiness meta (same fields as PJL scrape).
   - On exception or empty DOM, return `""`.

2. Add `_resolve_selected_pjl_url(cdata: dict, company_row: dict) -> str`:

   - Return stripped `cdata.get(ROSTER_CONFIG["parse_job_list"]["selected_pjl_url_key"]) or company_row.get("page_option_url") or ""`.
   - **Do not** read `companies.job_site` on decomposed path (column unset until **WATCH**).

3. Extract `_finalize_parse_dispatch_success(short_name, company_website, list_url, dom_html, job_titles, parsed, debug) -> dict` from current `run_parse_job_list_dispatch` success block (~lines 835–840):

   - `container_index = _compute_container_index(dom_html, container, job_titles)`
   - `parse_instructions = {"container": container, "job_tag": job_tag, "container_index": container_index}`
   - `save_company_data(short_name, {"parse_instructions": parse_instructions})`
   - `_save_company(..., state="WATCH", page_option_url=list_url, raw_response=parsed)` — **`WATCH`** is in `_PERSIST_PAGE_OPTION_URL_STATES`, so **`job_site`** column is set to confirmed list URL here (**AST-673** first write).
   - Return `{"short_name": short_name, "state": "WATCH", "job_site": list_url, "response_type": "PARSE_DISPATCH_OK", "parse_instructions": parse_instructions}`.

4. Add `_parse_dispatch_failure_state(input_state: str) -> str`:

   - If `input_state == "JOBLIST_IDENTIFIED"` → `ROSTER_CONFIG["parse_job_list"]["retry_state"]` (`JOBLIST_IDENTIFIED_RETRY`).
   - If `input_state == "JOBLIST_IDENTIFIED_RETRY"` → `ROSTER_CONFIG["parse_job_list"]["terminal_fail_state"]` (`COULD_NOT_PARSE_JOBLIST`).
   - Else → `COULD_NOT_PARSE_JOBLIST` (defensive).

5. Add `_save_parse_dispatch_failure(short_name, company_website, list_url, input_state, raw_response, notes: str | None)`:

   - `fail_state = _parse_dispatch_failure_state(input_state)`
   - If `notes`: `save_company_data(short_name, {"parse_job_list_notes": notes})`
   - `_save_company(short_name=short_name, company_website=company_website, state=fail_state, page_option_url=list_url, raw_response=raw_response, pre_run_job_site="")` — **do not** add `COULD_NOT_PARSE_JOBLIST` to `_PERSIST_PAGE_OPTION_URL_STATES`; `job_site` column stays empty.

   ⚠️ **Decision:** Decomposed parse failures use **`COULD_NOT_PARSE_JOBLIST`** / **`JOBLIST_IDENTIFIED_RETRY`**, not legacy **`CANNOT_PARSE_JOB_SITE`**, so Susan can distinguish decomposed-chain parse failures from **JOBS_FOUND** locate failures.

---

## Stage 3: Roster — `run_parse_job_list_dispatch` for `JOBLIST_IDENTIFIED` (+ retry)

**Done when:** `run_parse_job_list_dispatch` serves only **`JOBLIST_IDENTIFIED`** and **`JOBLIST_IDENTIFIED_RETRY`**; reloads DOM, trims containers, calls parse agent, applies retry/terminal states; legacy **`TO_WATCH` / `job_site` column** entry path removed.

1. Rewrite `run_parse_job_list_dispatch` header docstring: dispatch entry for **`JOBLIST_IDENTIFIED`** and **`JOBLIST_IDENTIFIED_RETRY`** only.

2. At function start:

   - `short_name`, `company_website` from `entity`.
   - `input_state = str(entity.get("state") or "").strip()`
   - If `input_state` not in `("JOBLIST_IDENTIFIED", "JOBLIST_IDENTIFIED_RETRY")`:
     - `logger.warning("run_parse_job_list_dispatch: unexpected state %s for %s", input_state, short_name)`
     - Return `{**zero-shaped, "error": "unexpected_state"}`.
   - Load `company`, `cdata`, `list_url = _resolve_selected_pjl_url(cdata, company or {})`.
   - If not `list_url`: log warning; `_save_parse_dispatch_failure(..., input_state, {"response_type": "MISSING_SELECTED_PJL_URL"}, "missing selected_pjl_url")`; return with `state` from `_parse_dispatch_failure_state(input_state)`.

3. `job_titles = cdata.get("job_titles") or []` — if empty, treat as parse failure (same retry/terminal routing) with notes `"missing job_titles"`.

4. `async with create_browser_context()`:

   - `dom_html = await _scrape_list_page_dom_for_parse(list_url, browser_context, debug=debug)`
   - Empty DOM → `_save_parse_dispatch_failure(..., {"response_type": "PARSE_DISPATCH_EMPTY_DOM"}, "empty dom after reload")`
   - `containers = find_job_containers(dom_html, job_titles)` — empty → failure with `"containers not found for titles"`
   - `dom_joined = "\n".join(containers)`
   - `parsed = await _fetch_parse_job_list(dom_joined, short_name, debug=debug, ctx=ctx)`
   - Empty container/job_tag or `_validate_parse_job_list_raw_job_listings` error → `_save_parse_dispatch_failure` with appropriate notes (mirror current messages).

5. Success → `return await _finalize_parse_dispatch_success(...)`.

6. AST-538: before agent call when `debug=True`:

   ```python
   logger.test(f"index 1/1 | {short_name} | parse_job_list | url={list_url} titles={len(job_titles)} state={input_state}")
   ```

   After outcome: one `logger.test` with resulting state.

7. **Delete** the legacy branch that read `entity.job_site` for **`TO_WATCH`** parse dispatch.

---

## Stage 4: Monolith removal — dispatch keys, routing, `find_job_page()` deletion

**Done when:** No schedulable **`find_job_page`** row defaults; `run_company_task` does not route **`PREFILTER_PASSED`** / **`TO_WATCH`** to monolith; `find_job_page()` removed; legacy **`run_select_job_page_dispatch`** TO_WATCH body removed.

1. In `src/utils/config.py`:

   - Remove `"find_job_page"` from `DISPATCH_SCHEDULABLE_TASK_KEYS` and `_DISPATCH_COMPANY_ENTITY_TASK_KEYS`.
   - Remove the `if task_key == "find_job_page"` branch from `_dispatch_trigger_state_for_task_key` (added in Stage 1 step 4).

2. In `run_company_task`, **delete** the entire `elif input_state in locate_job_page.dispatch_input_states` block (~lines 682–715) that routes `find_job_page` / `select_job_page` / `parse_job_list` on **`TO_WATCH`** / **`PREFILTER_PASSED`**.

   Keep the **`JOBS_FOUND`** branch immediately above it (unchanged).

3. Add **before** the `JOBS_FOUND` branch (or after `NO_OPENINGS`), two branches mirroring **AST-720** `PJL_READY` pattern:

   ```python
   elif input_state == ROSTER_CONFIG["parse_job_list"]["dispatch_trigger_state"]:
       # JOBLIST_IDENTIFIED → parse_job_list
       ...
   elif input_state == ROSTER_CONFIG["parse_job_list"]["retry_trigger_state"]:
       # JOBLIST_IDENTIFIED_RETRY → parse_job_list (same handler)
       ...
   ```

   Both call `run_parse_job_list_dispatch`. Pass/fail counting:

   - `WATCH` → `total_passed`
   - `JOBLIST_IDENTIFIED_RETRY`, `COULD_NOT_PARSE_JOBLIST` → `total_passed` (explicit terminal/intermediate state reached)
   - `error` key or unexpected state → `total_errors` / `total_failed` per existing roster dispatch conventions.

4. In `run_select_job_page_dispatch`, **remove** the legacy fall-through body (AST-535 **`TO_WATCH`** scrape + `_fetch_job_links_content`). Function serves **`PJL_READY`** only (**AST-720**); if state ≠ `PJL_READY`, log warning and return error-shaped dict.

5. **Delete** `async def find_job_page(...)` (~lines 1631–1731) and any helpers only referenced from that function (grep before delete). **Do not** delete `_find_job_page_from_assembled`, `_fetch_job_links_content`, `jobs_found_process_job_site`, `_finalize_joblist_*`, or `_check_parse_results`.

6. In `src/ui/api/api_admin.py`, remove `find_job_page` from adhoc live-content branches that assume schedulable monolith (grep `find_job_page`); keep `select_job_page` / `parse_job_list` adhoc paths if still valid for isolated agent preview.

7. **Scripts:** `scripts/test_find_job_page.py` and `scripts/test_extraction_validation.py` — add module docstring **deprecated** pointing to decomposed dispatch; optional follow-up: Susan runs manually. **Do not** block build on script updates unless import fails — then minimal fix to import `jobs_found_process_job_site` or skip.

8. Linear: comment on **AST-666** that scope folded into **AST-716** / **AST-721**; set **AST-666** `duplicateOf` → **AST-716** via `save_issue` when product ships (build-child or resolve-child — engineer adds comment in Stage 4 commit message; Susan or resolve-child closes duplicate formally).

---

## Stage 5: Integration verification (no new features)

**Done when:** Decomposed pipeline is schedulable end-to-end via config defaults; **JOBS_FOUND** regression surface documented for Betty.

1. Grep `src/` for remaining `find_job_page` string references — update comments/logs only; no resurrected dispatch paths.

2. Confirm `DISPATCH_SCHEDULABLE_TASK_KEYS` includes: `prefilter`, `fetch_website`, `fetch_job_pages` (**AST-719**), `select_job_page`, `parse_job_list`, … — not `find_job_page`.

3. Confirm `_dispatch_trigger_state_for_task_key` returns:

   | `task_key` | `trigger_state` |
   |------------|-----------------|
   | `fetch_job_pages` | `PREFILTER_PASSED` (+ retry per **AST-720**) |
   | `select_job_page` | `PJL_READY` |
   | `parse_job_list` | `JOBLIST_IDENTIFIED` |

   Admin must seed a **second** `parse_job_list` row with `trigger_state=JOBLIST_IDENTIFIED_RETRY` (Step 1 dispatch table).

4. **Do not** change `src/core/agent.py` `run_next` suppression for **JOBS_FOUND** `select_job_page` → `parse_job_list` chain.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — config state machine, dispatch registry, monolith deletion in `roster.py`, and admin adhoc touch; core roster locate/parse surface.

**Conf:** `Medium` — parse finalize logic is lifted from existing `run_parse_job_list_dispatch`; retry states and monolith removal depend on **AST-718**–**AST-720** data contracts landing on ftr first.

**Risk:** `High` — removing `find_job_page` dispatch affects every company on the old **TO_WATCH** / **PREFILTER_PASSED** monolith path; incorrect `job_site` persistence on decomposed parse would regress **AST-673**; **JOBS_FOUND** path must remain untouched.

## Rules self-review

- **§2.1 config:** New states and `ROSTER_CONFIG["parse_job_list"]` in `config.py` only.
- **§2.6 state machine:** Explicit transitions; one retry hop then terminal `COULD_NOT_PARSE_JOBLIST`.
- **§1.3 DRY:** Reuses `_fetch_parse_job_list`, `find_job_containers`, readiness scrape pattern from `_fetch_job_links_content`.
- **§1.5.1 debug:** Style D on DOM reload and parse dispatch entry.
- **§3.3 imports:** No new cross-layer violations.
