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
