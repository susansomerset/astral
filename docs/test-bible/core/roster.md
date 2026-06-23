# Roster

**Test module:** `tests/component/core/test_roster.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/roster.py` | `tests/component/core/test_roster.py` | yes |

---

### AST-463 · AST-460

**`recheck_no_openings`** dispatch batch: Playwright **`get_visible_text`** on stored **`job_site`** only; substring match on **`company_data.no_jobs_message`** keeps **NO_OPENINGS** + **`last_scan_at`**; absence transitions to **JOBS_FOUND**. **TO_WATCH** **`find_job_page`** path unchanged. Admin adhoc live preview echoes **`job_site`** for **`recheck_no_openings`**.

| Area | Source | Component tests |
| --- | --- | --- |
| **`process_recheck_no_openings`** + **`run_company_task`** **NO_OPENINGS** branch | `src/core/roster.py` | `tests/component/core/test_roster.py` (**`TestProcessRecheckNoOpenings`**, **`TestRunCompanyTask::test_no_openings_routes_to_recheck_not_find_job_page`**, **`TestRunCompanyTask::test_locate_job_page_paths`**) |
| Admin adhoc content for **locate_job_page** (nav_links) + **`recheck_no_openings`** (**`job_site`**) | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py` (**`test_build_adhoc_live_content_remaining_company_and_job_edges`** in **`TestApiAdminBranchGaps`**) |
| Dispatch seed **`recheck_no_openings`** + migration off **`find_job_page`** | `src/data/database.py` | Exercised via full component run / DB harness; roster tests mock I/O |

---

### AST-606 · AST-602

**AST-606** replaces **`PREFILTER_UNKNOWN`** on active prefilter failure paths with **`WEBSITE_FOUND_RETRY`** (decode/hydration/missing-parse / API body retryable) vs **`ERROR_PREFILTER`** (bare API failure). **`ROSTER_CONFIG["prefilter"]`** uses **`retry_state`**; dispatch seeds **`prefilter`** from **`WEBSITE_FOUND_RETRY`**. **`run_company_task`** treats **`WEBSITE_FOUND_RETRY`** like **`WEBSITE_FOUND`**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-606** | **`_prefilter_fail`** retry vs error routing; **`WEBSITE_FOUND_RETRY`** state + transitions; dispatch retry seed | `src/core/roster.py`, `src/utils/config.py`, `src/data/database.py` | `tests/component/core/test_roster.py::TestPrefilterCompany::test_api_failure_and_missing_parsed_response`; `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_company_states_and_transitions` |

**AST-606** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestPrefilterCompany::test_api_failure_and_missing_parsed_response \
  tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_company_states_and_transitions
```

---

### AST-621 · AST-542

**AST-542 (parent):** Backfill **AST-538** §1.5.1 contract across **`src/core/roster.py`** inflow paths — **`run_inflow_discovery_batch`** / **`vet_inflow_discovery`** baseline from **AST-557** on **`ftr/`**; this child adds **`resolve_company_website`** contract debug, **`_ingest_failure_reason`** ` | ` detail under vet-row headers, and empty-dedupe skip header. **No Betty log-string tests** (parent + child explicit); plan Stage 4 is manual UAT spot-check only. **`debug=False`** must stay unchanged — existing inflow behavior tests are the gate.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-621** | Ingest failure reason helper; `resolve_company_website` CSE/vet/state contract; empty-dedupe header in discovery batch | `src/core/roster.py` | **`tests/component/core/test_roster.py`** (full file — **`LOCKED_AT_100`**); **`tests/component/utils/test_debug_logging.py`** + **`tests/component/utils/test_logging_batch.py`** (**§7.13zt** contract regression) |

**AST-621** narrowed run (pytest-only — instrumentation-only child; no new log-string assertions):

```bash
.venv/bin/python -m pytest tests/component/core/test_roster.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

Equivalent harness:

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_roster.py
```

**Manifest focus (existing coverage — no new tests):**

| Touched path | Existing tests |
| --- | --- |
| `run_inflow_discovery_batch` vet-row ingest outcomes + empty dedupe | **`TestAst505InflowDiscovery`** (`test_run_batch_happy_path`, `test_run_batch_cse_failure_continues`, `test_run_batch_no_stale_terms_returns_zero_errors`, `test_run_batch_searches_only_stale_terms`) |
| `resolve_company_website` CSE + `find_company_website` + state transitions | **`TestAst506InflowResolve`** |
| `debug=False` unchanged on inflow paths | **`TestAst505InflowDiscovery`** / **`TestAst506InflowResolve`** paths without **`debug=True`**; full-file branch lock |

**Rollup reconcile (AST-621):** Betty publish ref **`origin/sub/AST-542/AST-621-roster-inflow-vet-ingest-debug`** — one **§7.13zzf** table row; **`rollup-child`** merges into **`origin/ftr/ast-542-debug-logging-backfill-roster`**.

---

### AST-673 · AST-671

**AST-673 (child):** **`find_job_page`** failure and early-exit paths must not overwrite a verified **job_site** with **company_website**. **`_job_site_for_persist`** centralizes column writes in **`_save_company`**; non-empty pre-run **job_site** → **`find_job_page`** delegates to **`jobs_found_process_job_site`** (same as **JOBS_FOUND** dispatch). Empty pre-run baseline stays empty on failure.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1–2 | **NO_JOBLIST** preserves distinct pre-run **job_site** via **`_save_company`** | `src/core/roster.py` | `tests/component/core/test_roster.py::TestFindJobPageAst673::test_save_company_no_joblist_preserves_pre_run_job_site` |
| 3 | **WATCH** success writes confirmed listings URL | `src/core/roster.py` | `tests/component/core/test_roster.py::TestFindJobPageAst673::test_save_company_watch_writes_confirmed_job_site` |
| 4 | Empty **job_site** baseline stays empty on PJL failure | `src/core/roster.py` | `tests/component/core/test_roster.py::TestFindJobPageAst673::test_find_job_page_failure_empty_job_site_stays_empty` |
| 5 | Stored **job_site** → **`jobs_found_process_job_site`** redirect; scrape-empty failure preserves column | `src/core/roster.py` | `tests/component/core/test_roster.py::TestFindJobPageAst673::test_find_job_page_with_job_site_delegates_jobs_found_path`; `TestJobsFoundProcessJobSite469::test_scrape_empty_preserves_pre_run_job_site`; `TestJobSiteForPersist673` (helper unit) |

**AST-673** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestJobSiteForPersist673 \
  tests/component/core/test_roster.py::TestFindJobPageAst673 \
  tests/component/core/test_roster.py::TestJobsFoundProcessJobSite469::test_missing_site_response \
  tests/component/core/test_roster.py::TestJobsFoundProcessJobSite469::test_scrape_empty_preserves_pre_run_job_site
```

---

### AST-674 · AST-669

**AST-674 (child):** **`find_job_page`** delegates to **`jobs_found_process_job_site`** only when stored **job_site** normalizes to a URL **distinct from** **company_website** (**`_is_verified_job_site_distinct`**). Equal or empty **job_site** keeps the PJL discovery path. Early **NO_JOBLIST** exits without **`do_task`** emit INFO **`NO_JOBLIST without LLM — reason=…`** so Susan can distinguish no-LLM-by-design from missing **agent_data**. Stage 3 audit: **`dispatcher._dispatch_one`** already sets **`log_batch_id`** to entity **`batch_id`** before **`run_company_task`** — **`select_job_page`** **agent_data** keys to the Execution History row Susan clicked.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Distinct **job_site**, 0 PJLs → **`jobs_found_process_job_site`**, not instant PJL **NO_JOBLIST** | `src/core/roster.py` | `tests/component/core/test_roster.py::TestFindJobPageAst674::test_distinct_job_site_delegates_before_empty_pjl_exit` |
| 1 (neg) | **job_site** equals **company_website** → PJL path, **`jobs_found_process_job_site`** not called | `src/core/roster.py` | `tests/component/core/test_roster.py::TestFindJobPageAst674::test_equal_job_site_falls_through_to_pjl_path` |
| 2–3 | Stored-URL chain: **`select_job_page`** **`do_task`** sees entity **`log_batch_id`** + dispatcher **`ctx`** | `src/core/roster.py`, `src/core/dispatcher.py`, `src/core/agent.py` | `tests/component/core/test_roster.py::TestFindJobPageAst674::test_find_assembled_select_job_page_uses_entity_log_batch_id` |
| 4 | No-LLM **NO_JOBLIST** logs **`reason=no_pjl_or_nav`** / **`all_pjl_scrapes_failed`** | `src/core/roster.py` | `tests/component/core/test_roster.py::TestFindJobPageAst674::test_no_pjl_emits_no_llm_log`; `::test_all_pjl_scrapes_failed_emits_no_llm_log` |
| 5 | Other dispatch **`do_task`** paths unchanged | existing suite | `tests/component/core/test_agent.py` (existing **`do_task`** / **AST-531** coverage — no new roster-only smoke) |

**Helper:** `tests/component/core/test_roster.py::TestJobSiteDistinct674::test_is_verified_job_site_distinct`

**AST-674** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestJobSiteDistinct674 \
  tests/component/core/test_roster.py::TestFindJobPageAst674
```

---

### AST-689 · AST-684

**AST-689 (child):** Config-driven **`wait_for_careers_list_readiness`** in **`playwright.py`**; **`_fetch_job_links_content`** polls after **`get_page`** before **`extract_visible_text`**; AST-538 debug headers when **`debug=True`**. Failure proceeds best-effort (**AST-692** owns **JOBSITE_SCRAPE_ISSUE**). **`roster_scrape_readiness_config()`** env overrides for timing knobs.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Readiness helper exits **ready** on listing selector hits | `src/external/playwright.py` | `tests/component/core/test_roster.py::TestAst689ScrapeReadiness::test_wait_for_careers_list_readiness_ready_on_listing_hits` |
| 2 | Bounded wait returns **timeout** when listings never appear | `src/external/playwright.py` | `tests/component/core/test_roster.py::TestAst689ScrapeReadiness::test_wait_for_careers_list_readiness_timeout` |
| 3 | **`_fetch_job_links_content`** invokes readiness before extract | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst689ScrapeReadiness::test_fetch_job_links_content_calls_readiness` |
| — | Existing PJL scrape debug test must not hit 20s gate | `src/core/roster.py` | `tests/component/core/test_roster.py::TestRosterCoverageGaps::test_fetch_job_links_content_dom_new_links_and_scrape_debug` (readiness mock) |

**AST-689** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst689ScrapeReadiness \
  tests/component/core/test_roster.py::TestRosterCoverageGaps::test_fetch_job_links_content_dom_new_links_and_scrape_debug
```

**Broken / obsolete (Betty fix):** **`test_fetch_job_links_content_dom_new_links_and_scrape_debug`** — without readiness mock, real gate waits **`max_wait_ms=20000`** per page (~21s test time).

---

### AST-692 · AST-684

**AST-692 (child):** Grace **JOBSITE_SCRAPE_ISSUE** → terminal company state **JOBSITE_SCRAPE_ISSUE** via **`_check_parse_results`** / **`_save_company`**; structured **`jobsite_scrape_issue_*`** in **`company_data`**; **`job_list_visible`** stripped; no **`parse_job_list`** chain (**AST-469** guard in **`agent.py`** unchanged).

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | **`_check_parse_results`** maps **JOBSITE_SCRAPE_ISSUE** → terminal state + persisted summary | `src/core/roster.py`, `src/utils/config.py` | `tests/component/core/test_roster.py::TestAst692JobsiteScrapeIssue::test_check_parse_results_jobsite_scrape_issue` |
| 2 | **`_find_job_page_from_assembled`** routes to **`_check_parse_results`**, not **`_finalize_joblist_titles_after_chain`** | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst692JobsiteScrapeIssue::test_find_job_page_from_assembled_jobsite_scrape_issue_no_chain` |
| 3 | Unknown response types still **NO_JOBLIST** (no bleed from scrape-issue branch) | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst692JobsiteScrapeIssue::test_unknown_response_type_still_no_joblist` |
| 4 | **`do_task`** suppresses **parse_job_list** when **response_type** ≠ **JOBLIST_TITLES** | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst692JobsiteScrapeIssueAgent::test_select_job_page_suppresses_parse_chain_for_jobsite_scrape_issue` |

**AST-692** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst692JobsiteScrapeIssue \
  tests/component/core/test_agent.py::TestAst692JobsiteScrapeIssueAgent
```

**Prerequisite (integration):** sibling **AST-689** readiness on **`origin/ftr/AST-684-job-site-scrape-is-too-fast`** for end-to-end staging repro — not required for this pytest slice.

---

### AST-698 · AST-696

**UAT fix:** **`prefilter_company`** forwards **`debug`** to **`do_task`**; **`run_company_task`** passes batch **`debug`** on **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`**. Agent hop emission: **`docs/test-bible/core/agent.md`** (**AST-698**).

| Area | Source | Component tests |
| --- | --- | --- |
| **`prefilter_company` → `do_task` debug passthrough** | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst698PrefilterDebugPassthrough::test_prefilter_company_forwards_debug_to_do_task` |
| **`run_company_task` → `prefilter_company` debug passthrough** | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst698PrefilterDebugPassthrough::test_run_company_task_forwards_debug_to_prefilter` |

**AST-698** narrowed run (roster slice):

```bash
.venv/bin/python -m pytest tests/component/core/test_roster.py::TestAst698PrefilterDebugPassthrough -q
```

---

### AST-701 · AST-700

**AST-701:** Shared **`scrape_company_homepage_content`** — homepage scrape + nav enumeration without agent hop; **`prefilter_company`** calls helper (behavior unchanged). **`fetch_website_batch`** persistence uses **`homepage_text`** + optional **`nav_links`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Scrape helper error / redirect / empty text / nav failure | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent` |

Gazer batch + consult routing: **`docs/test-bible/core/gazer.md`** · **`docs/test-bible/core/consult.md`** (**AST-701**).

---

### AST-759 · AST-753

**Shared page scrape contract** — single Playwright load → collapsed visible text + enumerated nav links; **`scrape_company_homepage_content`** and **`_scrape_pjl_page`** route through **`scrape_loaded_page_contract`** / **`finalize_page_scrape_contract`**; PJL rows persist **`enumerated_nav_links`**; **`_assemble_pjl_content`** embeds per-page **`--- NAV LINKS ---`**; **`run_select_job_page_dispatch`** passes **`_build_select_job_page_live_content`** (global **`pjl_nav_links`**) into **`_find_job_page_from_assembled`**. Does not change AST-720 routing or **`fetch_job_pages_batch`** pass/fail transitions.

| Area | Source | Component tests |
| --- | --- | --- |
| Contract finalize + select live content helpers | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst759SharedPageScrapeContract` |
| PJL merge/assemble nav persistence | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst719PjlRosterHelpers` |
| PJL_READY select live content parity | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst720PjlReadySelectDispatch::test_select_dispatch_passes_live_content_with_nav_links` |
| Homepage scrape via shared contract | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent` |

Gazer batch debug + assembled persist: **`docs/test-bible/core/gazer.md`** (**AST-759**).

**Broken / obsolete (Betty revision):** **`TestAst701ScrapeCompanyHomepageContent`** — mocks **`scrape_loaded_page_contract`** instead of separate **`get_visible_text`** / **`extract_site_page_list`** (AST-759 single-load refactor).

**AST-759** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst759SharedPageScrapeContract \
  tests/component/core/test_roster.py::TestAst719PjlRosterHelpers \
  tests/component/core/test_roster.py::TestAst720PjlReadySelectDispatch::test_select_dispatch_passes_live_content_with_nav_links \
  tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent \
  tests/component/core/test_gazer.py::TestFetchJobPagesBatch::test_success_transitions_pjl_ready_and_persists \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-720 · AST-716

**`select_job_page`** decomposed dispatch from **`PJL_READY`** — load **`pjl_assembled_content`** / **`pjl_scrape_pages`** (AST-719); **`JOBLIST_TITLES` → `JOBLIST_IDENTIFIED`** without parse or **`job_site`** column write; **`TRY_LINKS`** → **`PREFILTER_PASSED_RETRY`** + ledger append or **`NO_PJL_SELECTED`**; **`JOBSITE_SCRAPE_ISSUE`** / **`JOBLIST_NO_JOBS`** with **`suppress_job_site`**. Default admin trigger **`select_job_page` → `PJL_READY`**.

| Area | Source | Component tests |
| --- | --- | --- |
| PJL map + try_links ledger helpers | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst720PjlMapsAndLedger` |
| PJL_READY select outcomes + `run_company_task` routing | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst720PjlReadySelectDispatch` |
| Selection states + dispatch trigger | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst720SelectJobPageConfig` |

**Broken / obsolete (Betty revision):** **`TestAst549DispatchAdminDefaults::test_ast485_roster_dispatch_trio_matches_config_defaults`** — **`select_job_page`** default trigger is **`PJL_READY`**, not **`TO_WATCH`**.

**AST-720** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst720SelectJobPageConfig \
  tests/component/core/test_roster.py::TestAst720PjlMapsAndLedger \
  tests/component/core/test_roster.py::TestAst720PjlReadySelectDispatch \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-721 · AST-716

**`parse_job_list`** decomposed dispatch from **`JOBLIST_IDENTIFIED`** / **`JOBLIST_IDENTIFIED_RETRY`** — DOM reload via **`_scrape_list_page_dom_for_parse`**, **`selected_pjl_url`** + **`job_titles`** from company_data; first fail → **`JOBLIST_IDENTIFIED_RETRY`**, second → **`COULD_NOT_PARSE_JOBLIST`**; success → **`WATCH`** + first **`job_site`** write via **`_save_company`**. **`find_job_page()`** monolith removed; **`locate_job_page.dispatch_input_states`** is **`JOBS_FOUND`** only. Admin schedulable keys: **`select_job_page`** @ **`PJL_READY`**, **`parse_job_list`** @ **`JOBLIST_IDENTIFIED`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Parse states + roster config + schedulable keys | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst721ParseJobListConfig` |
| URL/title helpers + failure ladder | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst721ParseDispatchHelpers` |
| Parse dispatch outcomes + `run_company_task` routing | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst721ParseJobListDispatch`, `TestAst721ParseDispatchRouting` |
| Admin task_keys + adhoc preview | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template`, `TestAdhocHelpers::test_build_adhoc_live_content_company_paths` |
| PREFILTER_PASSED claim score_floor (fetch_job_pages) | `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast508_prefilter_passed_dispatch_passes_score_floor` |

**Broken / obsolete (Betty revision):** **`TestFindJobPage*`** classes skipped (monolith removed); **`TestAst535ToWatchDispatchTaskKeyRouting`** replaced by **`TestAst721ParseDispatchRouting`**; **`test_ast485_roster_dispatch_trio_matches_config_defaults`** — **`find_job_page`** not schedulable, **`parse_job_list` → `JOBLIST_IDENTIFIED`**; **`TestRunCompanyTask`** TO_WATCH / PREFILTER_PASSED no longer route to **`find_job_page`**.

**AST-721** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst721ParseJobListConfig \
  tests/component/core/test_roster.py::TestAst721ParseDispatchHelpers \
  tests/component/core/test_roster.py::TestAst721ParseJobListDispatch \
  tests/component/core/test_roster.py::TestAst721ParseDispatchRouting \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_ast485_roster_dispatch_trio_matches_config_defaults \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_build_adhoc_live_content_company_paths \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast508_prefilter_passed_dispatch_passes_score_floor \
  -q
```

---

### AST-719 · AST-716

**PJL ledger helpers** — **`_scrape_pjl_page`**, **`_merge_pjl_scrape_record`**, **`_assemble_pjl_content`**, **`_merge_pjl_nav_links`**; gazer **`fetch_job_pages_batch`** imports these for additive scrape. Does not write **`job_site`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Additive merge + assembled content + nav append | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst719PjlRosterHelpers` |

Gazer batch + consult routing: **`docs/test-bible/core/gazer.md`** · **`docs/test-bible/core/consult.md`** (**AST-719**).

---

### AST-718 · AST-716

**Prefilter routing on decomposed PJL path** — after **HOMEPAGE_READY** / inflow prefilter, route to **`NO_PREFILTER_JOBLISTS`**, **`PREFILTER_FAILED`**, or **`PREFILTER_PASSED`**; hydrate **`possible_joblist_links`** via **`normalize_link()`** + **`parse_enumerate_array`**. Legacy manual path still **TO_WATCH** / **IGNORE**. Config: **`NO_PREFILTER_JOBLISTS`**, **`no_pjl_state`**, **`pjl_url_data_key`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Decomposed routing + PJL hydration | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst718PrefilterPjlRouting` |
| Coat-check **`possible_joblist_links`** | `src/core/roster.py` | `tests/component/core/test_roster.py::TestRosterCoverageGaps::test_prefilter_notes_returns_saved_notes_with_nav_links` |
| **`NO_PREFILTER_JOBLISTS`** config | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_company_states_and_transitions` |
| **`normalize_link()`** | `src/utils/formatting.py` | `tests/component/utils/test_formatting.py::TestNormalizeLink` |

**Broken / obsolete (Betty revision):** inflow/batch pass cases that assumed **`PREFILTER_PASSED`** without PJL indices + resolvable nav — updated in **`TestAst507EncodedPrefilter`**, **`TestAst603ConsultParityHydration`**, **`TestAst702PrefilterCompanyBatch::test_batch_pass_and_fail_counts`**.

**AST-718** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestNormalizeLink \
  tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_company_states_and_transitions \
  tests/component/core/test_roster.py::TestAst718PrefilterPjlRouting \
  tests/component/core/test_roster.py::TestAst507EncodedPrefilter::test_legacy_empty_history_maps_pass_to_to_watch \
  tests/component/core/test_roster.py::TestRosterCoverageGaps::test_prefilter_notes_returns_saved_notes_with_nav_links \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-715 · AST-710

**UAT fix:** **`collapse_consecutive_blank_lines`** in **`scrape_company_homepage_content`** immediately after **`get_visible_text`**, before empty-text error gate — single normalize site for homepage scrape (**AST-701** DRY). Redundant gazer **`fetch_website_batch`** collapse removed (**AST-713** regression).

| Area | Source | Component tests |
| --- | --- | --- |
| Collapse at scrape helper | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_collapses_consecutive_blank_lines_at_scrape` |

Gazer passthrough: **`docs/test-bible/core/gazer.md`** (**AST-715**).

**AST-715** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_collapses_consecutive_blank_lines_at_scrape \
  tests/component/core/test_gazer.py::TestFetchWebsiteBatch::test_persists_normalized_visible_text_from_scrape_helper \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-702 · AST-700

**AST-702:** **`prefilter_company_batch`** from **`HOMEPAGE_READY`** rows; readiness gate on **`homepage_text`**; **`_apply_prefilter_decoded_company_outcome`** shared helper; **`run_company_task`** no longer runs monolithic **`prefilter_company`** on **`WEBSITE_FOUND`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Batch runner + readiness skip | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst702PrefilterCompanyBatch` |
| Fail-dest helpers | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst702PrefilterBatchHelpers` |
| Monolithic dispatch removed | `src/core/roster.py` | `tests/component/core/test_roster.py::TestRunCompanyTask::test_website_found_monolithic_dispatch_removed` |
| Debug passthrough on batch | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst698PrefilterDebugPassthrough::test_prefilter_company_batch_forwards_debug_to_do_task` |

Consult routing + config + dispatcher + database: **`docs/test-bible/core/consult.md`** · **`docs/test-bible/utils/config.md`** (**AST-702**).

---

### AST-707 · AST-700

**UAT fix:** Batch **`prefilter_company_batch`** must hydrate **RC** grades when candidate **`company_prefilter`** artifact has **MP/US** only — embedded **RC** from **`config.py`** via **`_rubric_criteria_from_cd`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Batch RC hydration (no mass **WEBSITE_FOUND_RETRY**) | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst707EmbeddedRcBatchHydration` |

Consult merge + config registry: **`docs/test-bible/core/consult.md`** · **`docs/test-bible/utils/config.md`** (**AST-707**).

**AST-707** narrowed run: **`docs/test-bible/core/consult.md`** (**AST-707**).

---

### AST-703 · AST-700

**UAT fix:** **`_ensure_dispatch_task_schema`** DELETE **`prefilter`/`WEBSITE_FOUND_RETRY`** before UPDATE **`prefilter`/`WEBSITE_FOUND` → `HOMEPAGE_READY`** — avoids triple-unique collision when legacy candidates had both rows.

| Area | Source | Component tests |
| --- | --- | --- |
| Dual-row migration idempotency | `src/data/database.py` | `tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision` |

Regression: **`TestAst702PrefilterDispatchMigration`** (AST-702 base/retry cases).

**AST-703** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision \
  tests/component/data/database/test_dispatch_tasks.py::TestAst702PrefilterDispatchMigration
```

**Pass criterion:** pytest green — not zero-arg harness / branch-lock gate.

### AST-726 (parent AST-717)

**Scope:** Read-path `agent_responses` dedupe by `task_key`; company prefilter `vector_grades` from `company_data`; latest-only prefilter score/notes clears on rerun.

| Area | Source | Component tests |
| --- | --- | --- |
| `dedupe_agent_responses_latest` | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst726LatestOnlyRosterStory::testdedupe_agent_responses_latest_wins_per_task_key` |
| Company `vector_grades` via `grades_key` | `src/core/roster.py` (`get_entity_agent_story`) | `TestAst726LatestOnlyRosterStory::test_company_prefilter_vector_grades_from_company_data` |
| Fail clears `prefilter_score` (explicit None) | `src/core/roster.py` (`_apply_prefilter_decoded_company_outcome`) | `TestAst726LatestOnlyRosterStory::test_prefilter_fail_clears_score` |

Data upsert + consult saves: **`docs/test-bible/data/database/agent_responses.md`**, **`docs/test-bible/core/consult.md`** (**AST-726**). Config `grades_key`: **`docs/test-bible/utils/config.md`** (**AST-726**).

**AST-726** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst726LatestOnlyRosterStory \
  tests/component/utils/test_config.py::TestAst726PrefilterGradesKey \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-727 (parent AST-717)

**Scope:** Public `dedupe_agent_responses_latest` + `normalize_agent_responses_for_backfill` for one-time migration script; runtime `get_entity_agent_story` shares dedupe helper (**AST-726**).

| Area | Source | Component tests |
| --- | --- | --- |
| Backfill normalizer (drop empty key, dedupe stats) | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst727NormalizeAgentResponsesForBackfill` |

Migration CLI: **`docs/test-bible/dev/backfill_latest_only_rubric_entity_data.md`** (**AST-727**).

---

### AST-775 · AST-754

**AST-775 (child):** Split **`run_inflow_discovery_batch`** — CSE + URL dedupe records each hit as **`NEW`** via **`record_inflow_discovery_hit`** (mechanical hostname slug, **`inflow_discovery_blurb`** + **`inflow_discovery_notes`**); **no** inline **`do_task(vet_inflow_discovery)`**. Zero deduped hits is success (nothing to record). Registers **`VET_FAILED`** terminal state + **`(NEW, VET_FAILED)`** transition for sibling **AST-776** vet dispatch.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | **`VET_FAILED`** state + transition from **`NEW`** | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_failed_state_and_transition` |
| 2 | Mechanical slug + blurb/notes persist on **`NEW`** row | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst775InflowDiscoveryRecordNew::test_slug_from_discovery_url_hostname`; `::test_record_hit_creates_new_with_blurb_and_notes`; `::test_discovery_blurb_line_truncates_snippet` |
| 3 | Expanded URL dedupe (**notes**, **blurb** pipe URL) + slug suffix collision | `src/core/roster.py` | `::TestAst775InflowDiscoveryRecordNew::test_record_hit_skips_duplicate_url_via_notes`; `::test_record_hit_skips_duplicate_url_via_blurb`; `::test_record_hit_slug_collision_suffix_other_candidate` |
| 4 | Batch records hits; zero deduped hits not an error | `src/core/roster.py` | `::TestAst505InflowDiscovery::test_run_batch_happy_path`; `::TestAst775InflowDiscoveryRecordNew::test_run_batch_no_deduped_hits_is_success`; `::TestAst505InflowDiscovery::test_run_batch_cse_failure_continues`; `::test_run_batch_searches_only_stale_terms`; `::test_run_batch_no_stale_terms_returns_zero_errors`; `::test_consult_routes_candidate_entity` |

**Broken / obsolete (Betty revision):** **`TestAst505InflowDiscovery::test_run_batch_happy_path`** — removed **`do_task`** / vet ingest mocks; asserts mechanical **`co_example`** **`NEW`** record (**AST-775**).

**AST-775** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery \
  tests/component/core/test_roster.py::TestAst775InflowDiscoveryRecordNew \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_failed_state_and_transition \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.
