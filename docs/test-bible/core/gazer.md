# Gazer

**Test module:** `tests/component/core/test_gazer.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/gazer.py` | `tests/component/core/test_gazer.py` | yes |

---

### AST-622 · AST-544

**AST-544 (parent):** Backfill **AST-538** §1.5.1 contract across **`src/core/gazer.py`** — company gaze (`process_gazer_batch`), job-list dedupe trace (`raw_job_listing_is_duplicate` read-only), JD scrape / title-validation batches (`fetch_jd_batch`, `validate_title_batch`); retire hand-rolled **`[DEBUG]`** / noise **`_log.debug`** in touched blocks. **No Betty log-string tests** (parent + child explicit); Radia enforces instrumentation on review. **`debug=False`** must stay unchanged — existing gazer behavior tests + branch lock are the gate.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-622** | Contract debug across four batch entry points; identifier helpers; listing dedupe trace helper | `src/core/gazer.py` | **`tests/component/core/test_gazer.py`** (full file — **`LOCKED_AT_100`**); **`tests/component/utils/test_debug_logging.py`** + **`tests/component/utils/test_logging_batch.py`** (**§7.13zt** contract regression) |

**AST-622** narrowed run (pytest-only — instrumentation-only child; no new log-string assertions):

```bash
.venv/bin/python -m pytest tests/component/core/test_gazer.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

Equivalent harness:

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_gazer.py
```

**Manifest focus (existing + branch-coverage extensions — no log-string asserts):**

| Touched path | Existing / extended tests |
| --- | --- |
| `fetch_jd_batch` outcome paths (missing link, scrape error, empty/short JD, classify fail, pass) | **`TestFetchJdBatch`**, **`TestFetchJdBatchDebugPaths`**, **`TestFetchJdBatchDebugBranchCoverage`** |
| `validate_title_batch` pass/fail + batch summary | **`TestValidateTitleBatch`**, **`TestValidateTitleBatchDebugPaths`** |
| `process_gazer_batch` scrape/parse/ingest + dedupe trace | **`TestProcessGazerBatch`**, **`TestProcessGazerBatchDebugPaths`**, **`TestProcessGazerBatchDebugBranchCoverage`**, **`TestLogListingDedupeTrace`** |
| Identifier helpers | **`TestGazerIdentifierHelpers`** |
| `debug=False` unchanged | All **`debug=False`** rows above; full-file branch lock |

**Betty test fix (AST-622):** Extended **`test_gazer.py`** for **`LOCKED_AT_100`** on new **`debug=True`/`False`** branch pairs — not golden log-line asserts.

---

### AST-759 · AST-753

**`fetch_job_pages_batch`** debug outcomes report **`visible_chars`** + **`nav_links`** count per URL; skipped ledger URLs log **`skipped-already-scraped`** when **`debug=True`**. Persist path unchanged — enriched **`_scrape_pjl_page`** records carry **`enumerated_nav_links`** into **`pjl_scrape_pages`** / **`pjl_assembled_content`**.

| Area | Source | Component tests |
| --- | --- | --- |
| PJL batch persist with per-page nav section | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestFetchJobPagesBatch::test_success_transitions_pjl_ready_and_persists` |

Roster contract + select live content: **`docs/test-bible/core/roster.md`** (**AST-759**).

**AST-759** narrowed run (gazer line):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestFetchJobPagesBatch::test_success_transitions_pjl_ready_and_persists \
  -q
```

---

### AST-719 · AST-716

**`fetch_job_pages_batch`** — additive Playwright scrape of **`possible_joblist_links`** (AST-718 ledger); persist **`pjl_scrape_pages`**, **`pjl_assembled_content`**, optional **`pjl_nav_links`**; pass **`PJL_READY`**, fail **`JOBSITE_SCRAPE_ISSUE`**. Consult routes **`dispatch_task_key=fetch_job_pages`** before **`run_company_task`**. Config: **`PJL_READY`**, **`GAZER_CONFIG["fetch_job_pages"]`**, dispatch registry.

| Area | Source | Component tests |
| --- | --- | --- |
| **`fetch_job_pages_batch`** connectivity / missing ledger / pass / additive skip / empty fail | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestFetchJobPagesBatch` |
| **`run_consult_task`** company routing | `src/core/consult.py` | `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_job_pages_batch` |
| PJL ledger helpers | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst719PjlRosterHelpers` |
| Config state + dispatch registry | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst719FetchJobPagesConfig` |

Roster helpers + config cross-refs: **`docs/test-bible/core/roster.md`** · **`docs/test-bible/utils/config.md`** (**AST-719**).

**AST-719** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestFetchJobPagesBatch \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_job_pages_batch \
  tests/component/core/test_roster.py::TestAst719PjlRosterHelpers \
  tests/component/utils/test_config.py::TestAst719FetchJobPagesConfig \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-701 · AST-700

**AST-701:** **`fetch_website_batch`** mirrors **`fetch_jd_batch`** — scrape homepage visible text + **`nav_links`** for **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`** companies; pass **`HOMEPAGE_READY`**, fail **`CANNOT_READ_WEBSITE`** with **`prefilter_company_notes`**. Shared **`scrape_company_homepage_content`** helper in roster (**`prefilter_company`** refactor unchanged observable outcomes). Consult routes **`dispatch_task_key=fetch_website`** before **`run_company_task`**. Config: **`HOMEPAGE_READY`**, **`GAZER_CONFIG["fetch_website"]`**, **`homepage_text`** company_data key, dispatch registry. Database: **`_RETRY_TASK_SEED`** companion **`WEBSITE_FOUND_RETRY`** row.

| Area | Source | Component tests |
| --- | --- | --- |
| **`fetch_website_batch`** connectivity / missing URL / scrape fail / pass persist | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestFetchWebsiteBatch` |
| **`run_consult_task`** company routing | `src/core/consult.py` | `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_website_batch` |
| **`scrape_company_homepage_content`** helper | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent` |
| Config state + dispatch registry | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig` |
| Retry dispatch seed | `src/data/database.py` | `tests/component/data/database/test_dispatch_tasks.py::TestAst701FetchWebsiteRetrySeed` |

**AST-701** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestFetchWebsiteBatch \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_website_batch \
  tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent \
  tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig \
  tests/component/data/database/test_dispatch_tasks.py::TestAst701FetchWebsiteRetrySeed
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-713 · AST-710

**Collapse consecutive blank lines** in gazer JD visible-text save — **`fetch_jd_batch`** (**`job_description`**) calls **`collapse_consecutive_blank_lines`** immediately after scrape, before empty-text gating / persist. Homepage normalize moved to **`scrape_company_homepage_content`** per **AST-715**. **`nav_links`** and **`_prune_jd`** unchanged.

---

### AST-797 · AST-794

**`scrape_jd_batch` → `fetch_jd_batch`** — reads **`GAZER_CONFIG["fetch_jd"]`**; no backward-compat alias. Consult/tracker call **`fetch_jd_batch`** only (**AST-797**).

| Area | Source | Component tests |
| --- | --- | --- |
| JD batch rename + outcomes | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestFetchJdBatch` (+ debug classes) |
| Consult routing | `src/core/consult.py` | `TestRunConsultTaskRoutes::test_routes_fetch_jd_batch` |
| Tracker self-heal | `src/core/tracker.py` | coat-check tests monkeypatch **`fetch_jd_batch`** |

Consult inline validate: **`docs/test-bible/core/consult.md`** (**AST-797**).

| Area | Source | Component tests |
| --- | --- | --- |
| JD post-scrape normalize + empty gate order | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestScrapeJdBatch::test_collapses_consecutive_blank_lines_before_save` |
| Shared helper | `src/utils/formatting.py` | `tests/component/utils/test_formatting.py::TestCollapseConsecutiveBlankLines` |

**AST-713** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestCollapseConsecutiveBlankLines \
  tests/component/core/test_gazer.py::TestScrapeJdBatch::test_collapses_consecutive_blank_lines_before_save \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-715 · AST-710

**UAT fix:** Homepage blank-line collapse at **`scrape_company_homepage_content`** (post-**`get_visible_text`**, pre-empty gate) — not redundant **`fetch_website_batch`** wrapper. **`prefilter_company`** callers receive normalized **`visible_text`**. Gazer persists helper output as-is.

| Area | Source | Component tests |
| --- | --- | --- |
| Collapse at shared scrape helper | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_collapses_consecutive_blank_lines_at_scrape` |
| **`fetch_website_batch`** passthrough persist | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestFetchWebsiteBatch::test_persists_normalized_visible_text_from_scrape_helper` |

**AST-715** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_collapses_consecutive_blank_lines_at_scrape \
  tests/component/core/test_gazer.py::TestFetchWebsiteBatch::test_persists_normalized_visible_text_from_scrape_helper \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-853 · AST-850

**Scope:** **`fetch_website_batch`** uses **`create_batch_browser_session()`** (recoverable shared session) instead of **`create_browser_context()`**; per-company **`asyncio.wait_for`** wall clock (**`PLAYWRIGHT_CONFIG["company_scrape_timeout_seconds"]`**); passes **`batch_session`** into **`scrape_company_homepage_content`**. State transitions unchanged (**AST-854** owns retry routing).

| Area | Source | Component tests |
| --- | --- | --- |
| Batch session wiring + scrape errors / pass | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestFetchWebsiteBatch` |
| Scrape timeout labeled infra error | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestFetchWebsiteBatch::test_scrape_timeout_fails_with_labeled_infra_error` |

External taxonomy + **`get_page`** recovery: **`docs/test-bible/external/playwright.md`** (**AST-853**). Roster infra error prefix: **`docs/test-bible/core/roster.md`** (**AST-853**).

**AST-853** narrowed run (gazer lines):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestFetchWebsiteBatch \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-854 · AST-850

**Scope:** Infra vs site fail routing for **`fetch_website_batch`** — **`[playwright:`** prefix → **`WEBSITE_FOUND_RETRY`** on first strike, **`CANNOT_READ_WEBSITE`** on retry re-fail or site errors; resilient **`gather`** (**`errors`** count); consult **`total_errors`** reads batch **`errors`**. Prerequisite **AST-853** (prefix + batch session).

| Area | Source | Component tests |
| --- | --- | --- |
| Fail-routing helpers | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestFetchWebsiteFailRouting` |
| Infra retry / terminal transitions + **`errors`** in return | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestFetchWebsiteFailRouting` (async), `::TestFetchWebsiteBatch` |
| **`retry_state`** in **`GAZER_CONFIG["fetch_website"]`** | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig`, `::TestAst854FetchWebsiteRetryConfig` |
| Consult **`total_errors`** from batch **`errors`** | `src/core/consult.py` | `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_website_batch_errors_count` |

**AST-854** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestFetchWebsiteFailRouting \
  tests/component/core/test_gazer.py::TestFetchWebsiteBatch \
  tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig \
  tests/component/utils/test_config.py::TestAst854FetchWebsiteRetryConfig \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_website_batch \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_website_batch_errors_count \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-765 · AST-757 (SUNSET — documentation)

**RETIRED (AST-757):** Boards channel removed from product (**AST-765**) and schema (**AST-766**). No active boards manifest obligations. See **`docs/ASTRAL_CODE_RULES.md` §3.7**.

---

### AST-874 · AST-872

**`fetch_culture_pages_batch`** — claim **`PASSED_GET`** jobs, ensure culture bodies via roster **`get_company_data(..., "website_content")`** coat-check only; pass **`CULTURE_READY`**, fail **`NEED_CULTURE_CONTENT`**, no-links **`NO_CULTURE_LINKS`**. Cached **`website_content`** skips coat-check; sequential batch writeback avoids duplicate scrapes for the same company. Consult routes **`dispatch_task_key=fetch_culture_pages`**. Config + dispatch migration: **`docs/test-bible/utils/config.md`** · **`docs/test-bible/data/database/dispatch_tasks.md`** (**AST-874**).

| Area | Source | Component tests |
| --- | --- | --- |
| Helpers + batch outcomes (connectivity / cache / no-links / coat-check / in-memory cache) | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestWebsiteContentHelpers`, `::TestFetchCulturePagesBatch` |
| Consult job routing | `src/core/consult.py` | `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_culture_pages_batch` |
| States + dispatch registry | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig` |
| Seed + retarget migration | `src/data/database.py` | `tests/component/data/database/test_dispatch_tasks.py::TestAst874FetchCulturePagesDispatchMigration` |

**AST-874** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestWebsiteContentHelpers \
  tests/component/core/test_gazer.py::TestFetchCulturePagesBatch \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_culture_pages_batch \
  tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig \
  tests/component/data/database/test_dispatch_tasks.py::TestAst874FetchCulturePagesDispatchMigration \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-882 · AST-881

**AST-882:** **`fetch_website_batch`** skips companies already in **`WEBSITE_FOUND_RETRY`** with non-empty **`homepage_text`** (leave for prefilter second strike). Infra retry without homepage text still follows **AST-854** routing.

| Area | Source | Component tests |
| --- | --- | --- |
| Homepage-ready WFR skip | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestAst882HomepageReadyWfrSkip::test_skips_wfr_when_homepage_text_present` |
| Bare WFR infra still terminals | `src/core/gazer.py` | `::TestAst882HomepageReadyWfrSkip::test_infra_retry_without_homepage_text_still_routes` |

Roster + claim: **`docs/test-bible/core/roster.md`** · **`docs/test-bible/utils/config.md`** (**AST-882**).
