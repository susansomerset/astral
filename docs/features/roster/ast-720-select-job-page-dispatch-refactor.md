<!-- linear-archive: AST-720 archived 2026-07-22 -->

## Linear archive (AST-720)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-720/select-job-page-dispatch-refactor-find-job-page-logic-confirmation  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-716 — find_job_page logic confirmation  
**Blocked by / blocks / related:** parent: AST-716; blocks: AST-721

### Description

## What this implements

Refactor select_job_page to run as an independent dispatch hop from PJL_READY: send assembled PJL visible text to the agent; on confirmed list page + titles → JOBLIST_IDENTIFIED; on new unique URLs → PREFILTER_PASSED_RETRY with dedupe against possible_joblist_links; on exhaustion → NO_PJL_SELECTED. Split from monolithic find_job_page; preserve TRY_LINKS / JOBSITE_SCRAPE_ISSUE behavior from AST-689/692.

## Acceptance criteria

4. `select_job_page` transitions match Susan's brief: confirmed titles → `JOBLIST_IDENTIFIED`; new links → `PREFILTER_PASSED_RETRY`; exhausted candidates → `NO_PJL_SELECTED`; proposed URLs dedupe against `possible_joblist_links`.
5. With `debug=True`, Susan can trace each PJL URL scrape, selection outcome, and parse hop using Style D index headers and `|` detail lines without reading production-only aggregate logs.

## Boundaries

Does not implement parse_job_list DOM reload or final WATCH transition — sibling ticket. Does not reimplement scrape batch — prior child.

## Notes for planning

[roster.py](<http://roster.py>) run_select_job_page_dispatch / _find_job_page_from_assembled reuse. AST-535 task_key routing.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-716-find-job-page-logic-confirmation`, child `sub/AST-716/<slug>` at dispatch-parent.

### Comments

#### radia — 2026-06-18T01:54:23.334Z
**Diff:** `origin/dev...origin/sub/AST-716/select-job-page-dispatch-refactor` @ `d4ef7f5`

**Plan doc (review section):** https://github.com/susansomerset/astral/blob/sub/AST-716/select-job-page-dispatch-refactor/docs/features/roster/ast-720-select-job-page-dispatch-refactor.md#radia-review-2026-06-18

### fix-now

None.

### discuss

- **Transitions:** plan listed `PREFILTER_PASSED_RETRY → NO_JOBLIST` — not in config; no decomposed path hits it today.
- **`_merge_try_links_into_pjl_ledger`:** appends raw URLs into `possible_joblist_links` beside AST-718 normalized keys; dedupe works via `normalize_link` but ledger format is mixed.
- **`run_company_task` error path:** no `locate_job_page.error_state` transition on `result.error` (plan showed one).

### advisory

- `_finalize_joblist_identified` debug uses `logger.test` not `debug_detail`.
- Decomposed `SELECT_FAILED` return dict still carries `job_site=company_website` (column safe).

### sign-off

PJL_READY select path, decomposed routing, AST-673 `job_site` suppression, legacy TO_WATCH gate, and Betty manifest align. Ready for `resolve-child`.

#### betty — 2026-06-18T01:50:03.016Z
**Bible shasum** (`origin/sub/AST-716/select-job-page-dispatch-refactor`):
- `docs/test-bible/core/roster.md` `392f8fc554d60e5a41e28d266d9ce1e8e609a41277a566b8d7c94fe784a1b072`
- `docs/test-bible/utils/config.md` `2cd1385d36138cc1e838b4e64c045f08d192c3a8df1cee9b77dfc4f0ae6a10a6`

#### betty — 2026-06-18T01:49:57.969Z
## QA test manifest (AST-720)

**Publish ref:** `origin/sub/AST-716/select-job-page-dispatch-refactor` @ `5ffabcc` (`merge-tests(AST-720): origin/tests b02c448`)

**Existing coverage (bible-backed):** AST-535 **`TO_WATCH`** select dispatch (`TestAst535ToWatchDispatchTaskKeyRouting`); AST-674 batch-id audit; AST-692 agent parse suppression — unchanged for legacy path.

**Broken / obsolete (revised):** `TestAst549DispatchAdminDefaults::test_ast485_roster_dispatch_trio_matches_config_defaults` — `select_job_page` admin default trigger is now **`PJL_READY`**.

**Gaps (new tests):**

1. `tests/component/utils/test_config.py::TestAst720SelectJobPageConfig`
2. `tests/component/core/test_roster.py::TestAst720PjlMapsAndLedger`
3. `tests/component/core/test_roster.py::TestAst720PjlReadySelectDispatch`

**Narrowed run (test-child):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst720SelectJobPageConfig \
  tests/component/core/test_roster.py::TestAst720PjlMapsAndLedger \
  tests/component/core/test_roster.py::TestAst720PjlReadySelectDispatch \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (`origin/sub/AST-716/select-job-page-dispatch-refactor`):**
- `docs/test-bible/core/roster.md` — see publish tip
- `docs/test-bible/utils/config.md` — see publish tip

— Betty

#### chuckles — 2026-06-18T01:23:08.676Z
## Plan validation — APPROVED

**Verdict:** APPROVED → Plan Approved

**Summary:** PJL_READY hop, tri-state outcomes, ledger dedupe, AST-689/692 preservation, no `job_site` until parse sibling — aligned with parent AC#4–6. Reuses `_find_job_page_from_assembled` pattern.

**Findings:** none blocking.

— Chuckles

#### hedy — 2026-06-18T01:22:33.347Z
Plan: `docs/features/roster/ast-720-select-job-page-dispatch-refactor.md`
https://github.com/susansomerset/astral/blob/sub/AST-716/select-job-page-dispatch-refactor/docs/features/roster/ast-720-select-job-page-dispatch-refactor.md

**Scope:** Single-Component — config (`JOBLIST_IDENTIFIED`, `PREFILTER_PASSED_RETRY`, `NO_PJL_SELECTED`, `ROSTER_CONFIG["select_job_page"]`) + roster PJL_READY select path via `_find_job_page_from_assembled(decomposed=True)`; no parse or entry scrape.

**Conf:** Medium — reuses existing select agent loop and `_check_parse_results`, but depends on AST-718/719 persisted PJL fields landing on ftr before build.

**Risk:** Medium — incorrect TRY_LINKS dedupe or `job_site` write would break the decomposed chain; legacy TO_WATCH select path must stay untouched until AST-721.

#### hedy — 2026-06-18T01:19:53.900Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-716/select-job-page-dispatch-refactor/docs/features/roster/ast-720-select-job-page-dispatch-refactor.md

**Self-assessment**
- **Scope:** Single-Component — `roster.py` select/dispatch routing + `config.py` state keys; no UI or new agent tasks.
- **Conf:** Medium — reuses `_find_job_page_from_assembled` / `_check_parse_results`, but PJL_READY persisted data depends on AST-718/719 landing first.
- **Risk:** Medium — wrong transitions or `job_site` write would break the decomposed chain; legacy TO_WATCH select path must stay until AST-721.

Four build stages: (1) `JOBLIST_IDENTIFIED` / `PREFILTER_PASSED_RETRY` / `NO_PJL_SELECTED` + dispatch trigger `PJL_READY`; (2) map rebuild from `pjl_assembled_content` / `pjl_scrape_pages`; (3) decomposed outcomes (no entry scrape, no parse, TRY_LINKS ledger dedupe); (4) `run_company_task` PJL_READY branch + AST-538 debug.

---

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
**Product commits:** `7b58fc12` (Stage 1 — config), `74ae5627` (Stages 2–4 — PJL helpers, decomposed routing, `run_company_task` PJL_READY entry), `c0e88d99` (AST-538 debug_index)

---

## Radia review (2026-06-18)

**Diff:** `origin/dev...origin/sub/AST-716/select-job-page-dispatch-refactor` (`5ffabcc`)

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity (core) | `JOBLIST_IDENTIFIED` / `PREFILTER_PASSED_RETRY` / `NO_PJL_SELECTED` states + PJL_READY transitions; `ROSTER_CONFIG["select_job_page"]`; `_dispatch_trigger_state_for_task_key("select_job_page")` → `PJL_READY`; `fetch_job_pages_trigger_states` for retry loop. |
| PJL_READY path | `run_select_job_page_dispatch` loads persisted assembly via `_pjl_maps_from_company_data`; no entry scrape; `decomposed=True` in `_find_job_page_from_assembled`; legacy `TO_WATCH` body behind state gate unchanged. |
| Outcomes | `JOBLIST_TITLES` → `_finalize_joblist_identified` with `suppress_job_site=True`; `TRY_LINKS` ledger append + retry / exhausted; `JOBSITE_SCRAPE_ISSUE` / empty assembled covered; `run_company_task` PJL_READY + `select_job_page` key guard. |
| AST-673 | `JOBLIST_IDENTIFIED` ∉ `_PERSIST_PAGE_OPTION_URL_STATES`; decomposed returns `job_site=""`; tests assert `update_company` not called with `job_site`. |
| AC / tests | Betty manifest (`TestAst720PjlMapsAndLedger`, `TestAst720PjlReadySelectDispatch`, config + `run_company_task` routing) matches routing matrix. |
| Boundaries | No `parse_job_list` / monolith removal / AST-721 scope. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `config.py` transitions | Plan Stage 1 listed `("PREFILTER_PASSED_RETRY", "NO_JOBLIST")` — not appended (only `PJL_READY` / `JOBSITE_SCRAPE_ISSUE` from retry). No current decomposed path hits it; add if monolith/retry combo needs it. |
| **discuss** | `_merge_try_links_into_pjl_ledger` ~2044–2053 | Appends raw resolved URLs to `possible_joblist_links` (e.g. `https://acme.com/newjobs`) alongside AST-718 normalized keys (`acme.com/careers`). Dedupe uses `normalize_link` on read — works today, but mixed ledger format may confuse downstream consumers; plan asked normalized keys only. |
| **discuss** | `run_company_task` ~693–695 | Plan showed `transition_company_state` to `locate_job_page.error_state` on `result.get("error")`; impl logs + `total_errors` only. Low risk if dispatch errors are rare. |
| **advisory** | `_finalize_joblist_identified` ~2183 | Debug uses `logger.test` string, not `debug_detail` under Style D header — minor AST-538 drift on identified path. |
| **advisory** | `_find_job_page_from_assembled` ~1633–1637 | Decomposed `SELECT_FAILED` still maps to `NO_JOBLIST` with return `job_site=company_website` (column safe — `NO_JOBLIST` ∉ persist set); return shape mismatch vs empty `job_site` on other decomposed exits. |

### Recommended actions

| Item | Action |
|------|--------|
| fix-now | None — ready for `resolve-child` / merge. |
| discuss | Optional: normalize keys on `try_links` ledger append; add `PREFILTER_PASSED_RETRY → NO_JOBLIST` if retry+monolith path needs it. |
| advisory | Align `_finalize_joblist_identified` debug with `debug_detail` when touching file next. |

---

## Resolution (2026-06-18)

**Radia fix-now:** none — clean sign-off @ `d4ef7f5`.

**Discuss (deferred):** mixed raw/normalized keys in `possible_joblist_links` ledger append, missing `PREFILTER_PASSED_RETRY → NO_JOBLIST` transition, and dispatch-error `error_state` transition — no decomposed-path regression today; revisit if monolith/retry combo needs them.

**Publish ref:** `origin/sub/AST-716/select-job-page-dispatch-refactor`

---

## Bug: AST-1892 — persist job_site on decomposed JOBLIST_NO_JOBS → NO_OPENINGS

**Parent:** AST-1887 (orphaned Bug mini-parent). **Publish ref:** `origin/sub/AST-1887/AST-1892-no-openings-job-site`. **Canon Scope:** none cited on AST-1887 / AST-1892.

### As-is

A `PJL_READY` company whose decomposed `select_job_page` hop returns `JOBLIST_NO_JOBS` transitions to `NO_OPENINGS` with `companies.job_site` written as `""`. Any existing value is wiped, and the selected list-page URL is never stored. From then on, `process_recheck_no_openings` returns `{"success": False, "message": "missing job_site"}` on every run, and the company stays stuck in `NO_OPENINGS`.

### To-be

The decomposed `JOBLIST_NO_JOBS` → `NO_OPENINGS` transition persists `job_site` exactly as the legacy (`decomposed=False`) path does: `_save_company` → `_job_site_for_persist` writes `job_site_url`, because `NO_OPENINGS` ∈ `_PERSIST_PAGE_OPTION_URL_STATES`. The return dict's `job_site` equals that same `job_site_url`. `recheck_no_openings` then has a URL to load on its 24h cadence.

### Repro

Fixture (component level, no DB), mirroring `TestAst1842SelectJobPageTimeoutHold`:

```python
monkeypatch.setattr(roster_mod, "do_task", AsyncMock(return_value={
    "success": True,
    "parsed_response": {"response_type": "JOBLIST_NO_JOBS", "selected_page": 1, "no_jobs_message": "No openings"},
}))
monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value={"short_name": "acme", "state": "PJL_READY", "job_site": "https://old/jobs"}))
update = MagicMock(); monkeypatch.setattr(roster_mod, "update_company", update)
monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
out = await roster_mod._find_job_page_from_assembled(
    short_name="acme", company_website="https://cw", assembled_content="asm",
    page_url_map={1: "https://jobs"}, page_dom_map={}, visible_map={1: ""},
    nav_links="", browser_context=None, debug=False, ctx=None,
    chain_parse=False, decomposed=True,
)
```

Today: `update_company` is called with `job_site=""`, and `out["job_site"] == ""`. Expected: `job_site="https://jobs"` in both places.

### Root cause

`74ae56276 code(AST-720)` added `decomposed` to `_check_parse_results` (`src/core/roster.py`) as `suppress = decomposed`, and applied it to **every** branch, including `JOBLIST_NO_JOBS`: `_save_company(..., suppress_job_site=suppress)`, which returns `"job_site": "" if suppress else job_site_url`. `_save_company` with `suppress_job_site=True` hard-writes `job_site_to_write = ""` and never consults `_job_site_for_persist`. Stage 3 of this plan said `JOBLIST_NO_JOBS` stays "unchanged". The AST-673 suppression was meant only for `JOBLIST_IDENTIFIED`, where the AST-721 parse sibling writes `job_site` later. `NO_OPENINGS` is terminal, and no later hop writes the column.

### Proposed change

One file, one branch: `src/core/roster.py`, `_check_parse_results`, the `if response_type == "JOBLIST_NO_JOBS":` block only.

1. In the `_save_company(...)` call for `state="NO_OPENINGS"`, **remove** the `suppress_job_site=suppress` argument. The call becomes `_save_company(short_name=..., company_website=..., state="NO_OPENINGS", page_option_url=job_site_url, raw_response=result, no_jobs_message=no_jobs_msg)`. `_save_company` then defaults to `suppress_job_site=False` and writes `_job_site_for_persist(terminal_state="NO_OPENINGS", page_option_url=job_site_url, ...)`, which returns `job_site_url.strip()`.
2. In that branch's return dict, replace `"job_site": "" if suppress else job_site_url` with `"job_site": job_site_url`.
3. Leave `suppress = decomposed` in place. The `JOBSITE_SCRAPE_ISSUE` branch still uses it, and that branch is out of scope. Add a short inline comment on the `JOBLIST_NO_JOBS` save explaining why it's not suppressed: `NO_OPENINGS` is terminal, `recheck_no_openings` needs `job_site`, and AST-673 suppression applies only to `JOBLIST_IDENTIFIED`.
4. No change to `_save_company`, `_job_site_for_persist`, `_PERSIST_PAGE_OPTION_URL_STATES`, config, schema, `_find_job_page_from_assembled`, or `run_select_job_page_dispatch`.

⚠️ **Decision (fallback value):** AST-1887's To-be says the fallback is "the pre-run value". In the code, `_find_job_page_from_assembled` computes `job_site_url = page_url_map.get(selected_page, company_website)`, and `_job_site_for_persist` returns `page_option_url` as-is for persist-set states. So when `selected_page` is missing or unmapped, both paths persist `company_website`, not the pre-run `job_site`. This fix matches the **legacy path exactly**, which is what the ticket's Technical scope asks for, and does not add a pre-run fallback. Doing that would mean changing `_find_job_page_from_assembled` or `_job_site_for_persist`, which is outside the declared scope and would also change legacy behavior. Susan or fix-board can widen scope if a pre-run fallback is wanted.

### Blast radius

- `_check_parse_results` has one caller: `_find_job_page_from_assembled` (~line 2364). The legacy `decomposed=False` path (AST-535 `TO_WATCH`) already took the non-suppressed branch, so it is bit-identical.
- Decomposed callers: only `run_select_job_page_dispatch` (`PJL_READY`). The behavior change is limited to `PJL_READY` + `JOBLIST_NO_JOBS`.
- Downstream: `process_recheck_no_openings` now receives a non-empty `job_site` for these rows (the intended consumer, AST-463). `run_company_task`'s `terminal_ok` set already includes `NO_OPENINGS`, so counts are unchanged.
- Tests: `tests/component/core/test_roster.py` has no assertion that pins decomposed `JOBLIST_NO_JOBS` to `job_site=""`. `grep suppress_job_site` finds zero hits in tests. The existing tests that stub `_check_parse_results` (e.g. the AST-674 batch-id test) are unaffected. Betty owns the new regression test (Repro above).
- Already-stuck `NO_OPENINGS` rows with an empty `job_site` are not repaired. Backfill is out of scope.

### What must still hold

- AST-673 / AST-720: `_finalize_joblist_identified` keeps `suppress_job_site=True` (no `job_site` column write on `JOBLIST_IDENTIFIED`, return `job_site=""`).
- The decomposed `TRY_LINKS`-exhausted exits (`suppress_job_site=True` → `NO_PJL_SELECTED`) are unchanged.
- The decomposed `JOBSITE_SCRAPE_ISSUE` branch is unchanged (still suppressed). It's out of scope unless Susan widens it.
- Legacy `TO_WATCH` `select_job_page` behavior is bit-identical.
- `_save_company` still sets `no_jobs_message` in `company_data` and transitions to `NO_OPENINGS`.
- No new limits, caps, retries, schema, or config.

## Joan fix-board — AST-1892

**Ticket context:** Orphaned bug under AST-1887. **Canon Scope on AST-1887 / AST-1892:** none cited (per plan-fix patch). **Question (F2):** Does the proposed fix conflict with or require updating any directive in force?

**Plan-fix read** (`origin/sub/AST-1887/AST-1892-no-openings-job-site` → `## Bug: AST-1892`):

| Section | Summary |
|--------|---------|
| **As-is** | Decomposed `JOBLIST_NO_JOBS` → `NO_OPENINGS` clears `companies.job_site` to `""`; `recheck_no_openings` then fails with “missing job_site”. |
| **To-be** | Same persistence as legacy (`decomposed=False`): `_save_company` / `_job_site_for_persist` for `NO_OPENINGS` (in `_PERSIST_PAGE_OPTION_URL_STATES`). |
| **Root cause** | AST-720 `suppress = decomposed` was applied to **all** branches; AST-673 suppression was only meant for `JOBLIST_IDENTIFIED`, not terminal `NO_OPENINGS`. |
| **Proposed change** | Only `src/core/roster.py`, `JOBLIST_NO_JOBS` block: drop `suppress_job_site=suppress` on save; return `job_site_url`; keep `suppress` for `JOBSITE_SCRAPE_ISSUE`; inline comment; no API/schema/config changes. |
| **Blast radius** | Decomposed `PJL_READY` + `JOBLIST_NO_JOBS` only; legacy path unchanged; AST-673 finalize path unchanged per “What must still hold”. |
| **Scope note** | Pre-run `job_site` fallback vs `company_website` is explicitly **out of scope** (matches legacy); product decision, not widened in this patch. |

**Corpus check (registry skim, not R1–R7):** `docs/canon-index.md` is not on the publish ref; used `canon/docs/DIRECTIVES-DIRECTORY.md` and grep on `canon/directives/active/` for overlap with `src/core/roster.py`, `job_site`, `NO_OPENINGS`, `suppress`, AST-673/720.

**Findings:**

1. **No cited canon list** — Nothing to reconcile against a frozen parent/child directive set; Joan still checks obvious roster/task overlap from the registry.

2. **Persistence path stays canonical** — The fix removes an erroneous flag and uses existing `_save_company` / `_job_site_for_persist` for a terminal state. That **aligns** with the in-force entity pattern (`stat.core.entity-save` in the directory table; save stays in `core/roster`, not a new writer or `data.database` bypass). No new carve-out or exception text is required.

3. **Active directives touched in blast radius do not encode the bug** — `patt.task.dispatch-retry` mentions `NO_OPENINGS` as a valid “passing” terminal state; restoring `job_site` for recheck **supports** downstream task behavior, it does not contradict retry/dispatch statutes. `patt.entity.batch-processing` and entity logging statutes (`stat.logging.info.entity`, etc.) scope `roster.py` but do not specify decomposed `suppress_job_site` for `JOBLIST_NO_JOBS`. No active directive mentions `suppress_job_site`, `JOBLIST_IDENTIFIED` suppression, or AST-673/720 IDs in the corpus.

4. **“What must still hold” is product/plan contract** — Preserving `suppress_job_site=True` on `JOBLIST_IDENTIFIED`, `TRY_LINKS` / `JOBSITE_SCRAPE_ISSUE`, and legacy `TO_WATCH` is implementation discipline for this bug, not a statute amendment. F3 (`validate-plan` fix mode) is unnecessary for canon **unless** someone later encodes AST-673 branch rules in a directive (not in force today).

5. **Fallback wording (AST-1887 To-be vs code)** — Plan flags a possible product widen; Joan does **not** treat that as ESCALATE here: it is bounded scope choice already documented in plan-fix, not ambiguous statute intent or new architectural precedent requiring Archie.

**Conclusion:** No in-force statute or pattern needs updating; no Archie gate for canon.

BEGIN-VERDICT
[board-joan]  CANON: OK

context_tokens≈4200
END-VERDICT

```text
AST-1892 board-joan done — CANON: OK.
```
