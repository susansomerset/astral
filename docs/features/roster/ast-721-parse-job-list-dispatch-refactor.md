# AST-721 — parse_job_list dispatch refactor and monolith removal

**Linear:** [AST-721 — parse_job_list dispatch refactor and monolith removal (find_job_page logic confirmation)](https://linear.app/astralcareermatch/issue/AST-721/parse-job-list-dispatch-refactor-and-monolith-removal-find-job-page)

**Parent (reference only):** [AST-716 — find_job_page logic confirmation](https://linear.app/astralcareermatch/issue/AST-716/find-job-page-logic-confirmation)

**Publish ref:** `origin/sub/AST-716/parse-job-list-dispatch-refactor`

**Summary:** After **`JOBLIST_IDENTIFIED`** (**AST-720**), run **`parse_job_list`** as its own dispatch hop: Playwright DOM reload of **`selected_pjl_url`** with **AST-689** careers-list readiness, existing **`find_job_containers`** trimming, **`_fetch_parse_job_list`** + validation, success → **`WATCH`** with **`job_site`** column set for the first time; first failure → **`JOBLIST_IDENTIFIED_RETRY`**, second failure → **`COULD_NOT_PARSE_JOBLIST`**. Retire the monolithic **`find_job_page`** dispatch chain (**AST-535** **`TO_WATCH`** / **`PREFILTER_PASSED`** trio) in favor of **`fetch_job_pages` → `select_job_page` → `parse_job_list`**; keep **`JOBS_FOUND`** **`jobs_found_process_job_site`** (**AST-469**) unchanged. Fold duplicate **AST-666** when shipped.

**Build gate (siblings):** **AST-718**–**AST-720** must be **`code()`-complete on `origin/ftr/AST-716-find-job-page-logic-confirmation`** before **build-child** (`JOBLIST_IDENTIFIED`, `selected_pjl_url`, `job_titles`, `pjl_assembled_content`).

**Out of scope:** Prefilter routing (**AST-718**), `fetch_job_pages` batch (**AST-719**), `select_job_page` agent prompts, UI, new LLM task shapes.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOBLIST_IDENTIFIED_RETRY`, `COULD_NOT_PARSE_JOBLIST` + transitions; `ROSTER_CONFIG["parse_job_list"]`; remove `find_job_page` from schedulable keys; narrow `locate_job_page.dispatch_input_states` to **`JOBS_FOUND`** only; `_dispatch_trigger_state_for_task_key("parse_job_list")` → **`JOBLIST_IDENTIFIED`** | utils |
| `src/core/roster.py` | Decomposed `run_parse_job_list_dispatch`; readiness-aware DOM reload; shared parse finalize helpers; `run_company_task` **`JOBLIST_IDENTIFIED`** / **`JOBLIST_IDENTIFIED_RETRY`** branches; remove monolith dispatch routing; delete **`find_job_page()`**; remove legacy **`TO_WATCH`** body from **`run_select_job_page_dispatch`** | core |
| `src/ui/api/api_admin.py` | Remove or guard adhoc live-content paths for dropped **`find_job_page`** schedulable key | ui |

**Verify only (Betty / qa-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | Parse: success → `WATCH` + `job_site`; first fail → `JOBLIST_IDENTIFIED_RETRY`; second fail → `COULD_NOT_PARSE_JOBLIST`; monolith routes gone; **`JOBS_FOUND`** unchanged |
| `tests/component/utils/test_config.py` | New states/transitions; `parse_job_list` trigger `JOBLIST_IDENTIFIED`; `find_job_page` not schedulable |
| `tests/component/ui/api/test_api_admin.py` | Admin task_keys / adhoc no longer list monolith `find_job_page` |
| `tests/component/core/test_dispatcher.py` | No `PREFILTER_PASSED → find_job_page` claim |

**Read-only reuse (do not duplicate):**

| Symbol | Location | Use |
|--------|----------|-----|
| `run_parse_job_list_dispatch` | `src/core/roster.py` | Refactor in place — extract finalize/failure helpers |
| `wait_for_careers_list_readiness`, `roster_scrape_readiness_config` | `playwright.py` / `config.py` | AST-689 gate on DOM reload |
| `find_job_containers`, `_compute_container_index` | `formatting.py` / `roster.py` | Single/multi-title trim |
| `_fetch_parse_job_list`, `_validate_parse_job_list_raw_job_listings` | `src/core/roster.py` | Agent + DOM validation |
| `_save_company`, `_job_site_for_persist` | `src/core/roster.py` | **`WATCH`** persists `job_site`; failures use `pre_run_job_site=""` (**AST-673**) |
| `jobs_found_process_job_site`, `_find_job_page_from_assembled` | `src/core/roster.py` | **JOBS_FOUND** only — do not delete |
| `_fetch_job_links_content` | `src/core/roster.py` | **JOBS_FOUND** / internal helpers after monolith removal |

**Dispatch rows (Susan / admin — not automatic DB seeds):**

| Action | `task_key` | `trigger_state` |
|--------|------------|-----------------|
| **Add** | `parse_job_list` | `JOBLIST_IDENTIFIED` |
| **Add** | `parse_job_list` | `JOBLIST_IDENTIFIED_RETRY` |
| **Deactivate** | `find_job_page` | `TO_WATCH`, `PREFILTER_PASSED` |
| **Deactivate** | `select_job_page` | `TO_WATCH` (legacy AST-535) |
| **Deactivate** | `parse_job_list` | `TO_WATCH` (legacy AST-535) |

Active decomposed rows: **`fetch_job_pages` @ `PREFILTER_PASSED`** (**AST-719**), **`select_job_page` @ `PJL_READY`** (**AST-720**).

---

## Stage 1: Config — parse retry states and dispatch trigger

**Done when:** State machine admits retry/terminal parse states; **`parse_job_list`** admin default trigger is **`JOBLIST_IDENTIFIED`**; **`find_job_page`** is not schedulable.

1. In `src/utils/config.py`, inside **`COMPANY_STATES`**, add:

   ```python
   "JOBLIST_IDENTIFIED_RETRY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
   "COULD_NOT_PARSE_JOBLIST": {},
   ```

   (**`JOBLIST_IDENTIFIED`** comes from **AST-720** — verify at build; do not duplicate if present.)

2. In **`ASTRAL_CONFIG["company_state_transitions"]`**, append:

   ```python
   ("JOBLIST_IDENTIFIED", "WATCH"),
   ("JOBLIST_IDENTIFIED", "JOBLIST_IDENTIFIED_RETRY"),
   ("JOBLIST_IDENTIFIED", "COULD_NOT_PARSE_JOBLIST"),
   ("JOBLIST_IDENTIFIED_RETRY", "WATCH"),
   ("JOBLIST_IDENTIFIED_RETRY", "COULD_NOT_PARSE_JOBLIST"),
   ```

3. After **`ROSTER_CONFIG["select_job_page"]`** (**AST-720**), add:

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

4. In **`_dispatch_trigger_state_for_task_key`**, replace the locate-trio branch with:

   ```python
   if task_key == "parse_job_list":
       return ROSTER_CONFIG["parse_job_list"]["dispatch_trigger_state"]
   if task_key == "select_job_page":
       return ROSTER_CONFIG["select_job_page"]["dispatch_trigger_state"]
   if task_key == "fetch_job_pages":
       return "PREFILTER_PASSED"
   ```

   Remove **`find_job_page`** branch in Stage 4 when the key is dropped from schedulable set.

5. Narrow **`ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]`** to:

   ```python
   "dispatch_input_states": ["JOBS_FOUND"],
   ```

   Remove **`TO_WATCH`** and **`PREFILTER_PASSED`**. Update the block comment: only **`JOBS_FOUND`** uses **`jobs_found_process_job_site`**.

6. Remove obsolete **`INFLOW_CONFIG["locate"]`** block (monolith **`PREFILTER_PASSED`** locate — unused in `src/` after grep).

---

## Stage 2: Roster — DOM reload + shared parse finalize helpers

**Done when:** Helpers reload list-page DOM with readiness, run parse validation, and map failures to retry vs terminal states without setting **`job_site`** until **`WATCH`**.

1. Add **`async def _scrape_list_page_dom_for_parse(url, browser_context, debug=False) -> str`**:

   - **`get_page` → `wait_for_careers_list_readiness(pg, roster_scrape_readiness_config())` → `extract_page_dom` → `close_page`** (mirror **`_fetch_job_links_content`** single-page path).
   - **`debug=True`**: AST-538 **`debug_index`** / **`debug_detail`** with readiness meta (same fields as PJL scrape).
   - On exception or empty DOM → return **`""`**.

2. Add **`_resolve_selected_pjl_url(cdata: dict) -> str`**:

   - Return stripped **`cdata.get(ROSTER_CONFIG["parse_job_list"]["selected_pjl_url_key"]) or ""`**.
   - **Do not** read **`companies.job_site`** on the decomposed path.

3. Add **`_finalize_parse_dispatch_success(...)`** — extract from current **`run_parse_job_list_dispatch`** success block (~835–840):

   - **`_compute_container_index`**, **`parse_instructions`**, **`save_company_data`**
   - **`_save_company(..., state="WATCH", page_option_url=list_url, raw_response=parsed)`** — **`WATCH ∈ _PERSIST_PAGE_OPTION_URL_STATES`** → first **`job_site`** column write (**AST-673**).
   - Return **`{"short_name", "state": "WATCH", "job_site": list_url, "response_type": "PARSE_DISPATCH_OK", ...}`**.

4. Add **`_parse_dispatch_failure_state(input_state: str) -> str`**:

   - **`JOBLIST_IDENTIFIED` → `JOBLIST_IDENTIFIED_RETRY`**
   - **`JOBLIST_IDENTIFIED_RETRY` → `COULD_NOT_PARSE_JOBLIST`**
   - Else → **`COULD_NOT_PARSE_JOBLIST`** (defensive).

5. Add **`_save_parse_dispatch_failure(short_name, company_website, list_url, input_state, raw_response, notes=None)`**:

   - **`fail_state = _parse_dispatch_failure_state(input_state)`**
   - Optional **`parse_job_list_notes`** via **`save_company_data`**
   - **`_save_company(..., state=fail_state, page_option_url=list_url, raw_response=..., pre_run_job_site="")`** — **`_save_company`** transitions state; **`COULD_NOT_PARSE_JOBLIST` ∉ _PERSIST_PAGE_OPTION_URL_STATES`** → **`job_site`** stays empty.

   ⚠️ **Decision:** Decomposed parse failures use **`JOBLIST_IDENTIFIED_RETRY`** / **`COULD_NOT_PARSE_JOBLIST`**, not legacy **`CANNOT_PARSE_JOB_SITE`** (reserved for **JOBS_FOUND** locate path).

---

## Stage 3: Roster — `run_parse_job_list_dispatch` for identified + retry

**Done when:** Handler serves only **`JOBLIST_IDENTIFIED`** and **`JOBLIST_IDENTIFIED_RETRY`**; legacy **`TO_WATCH` / `entity.job_site`** path removed.

1. Rewrite docstring: entry for **`JOBLIST_IDENTIFIED`** and **`JOBLIST_IDENTIFIED_RETRY`** only.

2. At function start:

   - **`input_state = str(entity.get("state") or "").strip()`**
   - If not in **`("JOBLIST_IDENTIFIED", "JOBLIST_IDENTIFIED_RETRY")`**: log warning; return **`{"error": "unexpected_state", ...}`**.
   - **`list_url = _resolve_selected_pjl_url(cdata)`** — if missing → **`_save_parse_dispatch_failure(..., "missing selected_pjl_url")`**.
   - **`job_titles = cdata.get("job_titles") or []`** — if empty → failure with **`"missing job_titles"`**.

3. **`async with create_browser_context()`**:

   - **`dom_html = await _scrape_list_page_dom_for_parse(list_url, ...)`**
   - Empty DOM → failure **`"empty dom after reload"`**
   - **`containers = find_job_containers(dom_html, job_titles)`** — empty → failure **`"containers not found for titles"`**
   - **`parsed = await _fetch_parse_job_list("\n".join(containers), ...)`**
   - Invalid container/tag or **`_validate_parse_job_list_raw_job_listings`** error → **`_save_parse_dispatch_failure`** (mirror current note strings).

4. Success → **`return _finalize_parse_dispatch_success(...)`**.

5. **AST-538** when **`debug=True`**: before agent — **`debug_index(..., outcome=f"url={list_url} titles={len(job_titles)} state={input_state}")`**; after — **`debug_detail`** with resulting state.

6. **Delete** legacy branch that read **`entity.job_site`** for **`TO_WATCH`** parse dispatch.

---

## Stage 4: Monolith removal — dispatch keys, routing, `find_job_page()` deletion

**Done when:** No schedulable **`find_job_page`**; **`run_company_task`** does not route monolith on **`TO_WATCH`** / **`PREFILTER_PASSED`**; **`find_job_page()`** removed; **`run_select_job_page_dispatch`** is **`PJL_READY`**-only.

1. In **`src/utils/config.py`**:

   - Remove **`"find_job_page"`** from **`DISPATCH_SCHEDULABLE_TASK_KEYS`** and **`_DISPATCH_COMPANY_ENTITY_TASK_KEYS`**.
   - Remove **`find_job_page`** branch from **`_dispatch_trigger_state_for_task_key`**.

2. In **`run_company_task`**, **delete** the **`locate_job_page.dispatch_input_states`** block (~682–715) that routed **`find_job_page` / `select_job_page` / `parse_job_list`** on **`TO_WATCH`** / **`PREFILTER_PASSED`**.

   Keep **`JOBS_FOUND`** branch unchanged.

3. Add parse branches (mirror **AST-720** **`PJL_READY`** pattern):

   ```python
   elif input_state in (
       ROSTER_CONFIG["parse_job_list"]["dispatch_trigger_state"],
       ROSTER_CONFIG["parse_job_list"]["retry_trigger_state"],
   ):
       if (dispatch_task_key or "").strip() != "parse_job_list":
           ... total_errors ...
       result = await run_parse_job_list_dispatch(entity, batch_id, ctx, debug)
       ok_states = frozenset({
           ROSTER_CONFIG["parse_job_list"]["pass_state"],
           ROSTER_CONFIG["parse_job_list"]["retry_state"],
           ROSTER_CONFIG["parse_job_list"]["terminal_fail_state"],
       })
       if result.get("error"):
           ... total_errors ...
       if result.get("state") in ok_states:
           return {**zero, "total_passed": 1}
       return {**zero, "total_failed": 1}
   ```

4. In **`run_select_job_page_dispatch`**, **remove** legacy **`TO_WATCH`** body (**`_fetch_job_links_content`** + monolith assemble). If state ≠ **`PJL_READY`**, log warning and return error-shaped dict (**AST-720** path only).

5. **Delete** **`async def find_job_page(...)`** (~1631–1731). Grep first — **do not** delete **`_find_job_page_from_assembled`**, **`_fetch_job_links_content`**, **`jobs_found_process_job_site`**, **`_check_parse_results`**, **`_finalize_joblist_*`**.

6. In **`src/ui/api/api_admin.py`**, remove **`find_job_page`** from adhoc live-content branches tied to schedulable keys; keep isolated **`select_job_page`** / **`parse_job_list`** preview if still useful.

7. **Scripts** **`scripts/test_find_job_page.py`**: add deprecation comment pointing to decomposed dispatch; fix imports only if build breaks.

8. Linear comment on **AST-666**: scope folded into **AST-716** / **AST-721** (Susan or **resolve-child** sets duplicate when parent ships).

---

## Stage 5: Integration verification

**Done when:** Decomposed pipeline schedulable end-to-end; **JOBS_FOUND** regression surface documented for Betty.

1. Grep **`src/`** for **`find_job_page`** — comments/logs only; no resurrected dispatch paths.

2. Confirm **`DISPATCH_SCHEDULABLE_TASK_KEYS`** includes **`fetch_job_pages`**, **`select_job_page`**, **`parse_job_list`** — not **`find_job_page`**.

3. Default **`_dispatch_trigger_state_for_task_key`**:

   | `task_key` | `trigger_state` |
   |------------|-----------------|
   | `fetch_job_pages` | `PREFILTER_PASSED` |
   | `select_job_page` | `PJL_READY` |
   | `parse_job_list` | `JOBLIST_IDENTIFIED` |

   Susan seeds second **`parse_job_list`** row at **`JOBLIST_IDENTIFIED_RETRY`**.

4. **Do not** change **`src/core/agent.py`** **`run_next`** suppression for **JOBS_FOUND** chain.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — config state machine, dispatch registry, monolith deletion in **`roster.py`**, admin adhoc touch.

**Conf:** `Medium` — parse finalize lifted from existing **`run_parse_job_list_dispatch`**; monolith removal depends on **AST-718**–**AST-720** data contracts on ftr first.

**Risk:** `High` — removing monolith dispatch affects every company on old **TO_WATCH** / **PREFILTER_PASSED** **`find_job_page`** rows; wrong **`job_site`** write regresses **AST-673**; **JOBS_FOUND** must stay untouched.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §2.1 config | New states + `ROSTER_CONFIG["parse_job_list"]` centralized |
| §2.6 state machine | One retry hop then `COULD_NOT_PARSE_JOBLIST`; explicit transitions |
| §1.3 DRY | Reuses parse/scrape helpers; no parallel parse module |
| §1.5.1 debug | Style D on DOM reload and parse dispatch |
| §3.3 imports | No new cross-layer violations |

No unresolved conflicts.

---

## Review stub (build-child)

**Branch:** `sub/AST-716/parse-job-list-dispatch-refactor`

**Product commits:** `f504d77c` (Stage 1 — config), `6f933343` (Stages 2–4 — parse dispatch, monolith removal, admin/scripts)

**Publish ref:** `origin/sub/AST-716/parse-job-list-dispatch-refactor` @ `2a3563d9`

---

## Radia review (2026-06-18)

**Diff:** `origin/dev...origin/sub/AST-716/parse-job-list-dispatch-refactor` (`3e93586`)

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity (core) | `JOBLIST_IDENTIFIED_RETRY` / `COULD_NOT_PARSE_JOBLIST` + transitions; `ROSTER_CONFIG["parse_job_list"]`; `locate_job_page.dispatch_input_states` → **`JOBS_FOUND`** only; `find_job_page` removed from schedulable keys; `_dispatch_trigger_state_for_task_key("parse_job_list")` → `JOBLIST_IDENTIFIED`. |
| Monolith removal | **`find_job_page()`** deleted; `run_company_task` no longer routes TO_WATCH / PREFILTER_PASSED locate trio; `run_select_job_page_dispatch` PJL_READY-only with warning on other states; legacy monolith tests skipped. |
| Parse dispatch | `_scrape_list_page_dom_for_parse` + readiness; `_resolve_selected_pjl_url`; failure ladder (`JOBLIST_IDENTIFIED` → retry, retry → terminal); `_finalize_parse_dispatch_success` → **`WATCH`** + first **`job_site`** write; failures use **`pre_run_job_site=""`** (**AST-673**). |
| JOBS_FOUND | **`jobs_found_process_job_site`** branch unchanged behind narrowed `dispatch_input_states`. |
| Admin / scripts | Adhoc live-content drops **`find_job_page`**; `scripts/test_find_job_page.py` deprecated stub. |
| AC / tests | Betty manifest (`TestAst721ParseJobListDispatch`, routing, config, dispatcher seed key, admin adhoc) matches plan matrix. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | Ops / dispatch rows | Plan documents Susan must **deactivate** legacy `find_job_page` @ TO_WATCH/PREFILTER_PASSED and seed decomposed rows — code no longer routes them (`total_errors`). Confirm admin cutover before UAT on live companies still on monolith rows. |
| **advisory** | `_scrape_list_page_dom_for_parse` ~844–845 | Bare **`except Exception: return ""`** — scrape errors become empty-DOM parse failures (retry/terminal) with no log line. Acceptable bounded tradeoff today; add **`debug_detail`** or warning if ops need scrape-fail vs empty-page distinction. |
| **advisory** | `gazer.py` ~748–754 | Failure message still says **"re-run find_job_page"** — monolith removed; stale operator string when parse_instructions missing. |
| **advisory** | `save_company_data` **`parse_job_list_notes`** | Written on failure but not registered in **`ROSTER_CONFIG["company_data_keys"]`** — minor config completeness. |

### Recommended actions

| Item | Action |
|------|--------|
| fix-now | None — ready for `resolve-child` / merge. |
| discuss | Confirm Susan deactivates legacy dispatch rows per plan table before parent UAT. |
| advisory | Update gazer "re-run find_job_page" copy when touching gaze path; optional scrape-error log in `_scrape_list_page_dom_for_parse`. |

---

## Resolution (2026-06-18)

**Radia fix-now:** none — clean sign-off @ `bd8fa7d`.

**Discuss (deferred):** Susan deactivates legacy monolith dispatch rows and seeds decomposed `fetch_job_pages` → `select_job_page` → `parse_job_list` before parent UAT — code no longer routes TO_WATCH/PREFILTER_PASSED monolith.

**Publish ref:** `origin/sub/AST-716/parse-job-list-dispatch-refactor`
