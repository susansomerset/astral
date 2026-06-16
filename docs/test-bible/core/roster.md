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
