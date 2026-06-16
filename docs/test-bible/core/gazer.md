# Gazer

**Test module:** `tests/component/core/test_gazer.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/gazer.py` | `tests/component/core/test_gazer.py` | yes |

---

### AST-622 · AST-544

**AST-544 (parent):** Backfill **AST-538** §1.5.1 contract across **`src/core/gazer.py`** — company gaze (`process_gazer_batch`), job-list dedupe trace (`raw_job_listing_is_duplicate` read-only), JD scrape / title-validation batches (`scrape_jd_batch`, `validate_title_batch`), and board gaze (`process_gaze_board_batch`); retire hand-rolled **`[DEBUG]`** / noise **`_log.debug`** in touched blocks. **No Betty log-string tests** (parent + child explicit); Radia enforces instrumentation on review. **`debug=False`** must stay unchanged — existing gazer behavior tests + branch lock are the gate.

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
| `scrape_jd_batch` outcome paths (missing link, scrape error, empty/short JD, classify fail, pass) | **`TestScrapeJdBatch`**, **`TestScrapeJdBatchDebugPaths`**, **`TestScrapeJdBatchDebugBranchCoverage`** |
| `validate_title_batch` pass/fail + batch summary | **`TestValidateTitleBatch`**, **`TestValidateTitleBatchDebugPaths`** |
| `process_gazer_batch` scrape/parse/ingest + dedupe trace | **`TestProcessGazerBatch`**, **`TestProcessGazerBatchDebugPaths`**, **`TestProcessGazerBatchDebugBranchCoverage`**, **`TestLogListingDedupeTrace`** |
| `process_gaze_board_batch` success/failure rows | **`TestProcessGazeBoardBatch`**, **`TestProcessGazeBoardBatchDebugPaths`** |
| Identifier helpers | **`TestGazerIdentifierHelpers`** |
| `debug=False` unchanged | All **`debug=False`** rows above; full-file branch lock |

**Betty test fix (AST-622):** Extended **`test_gazer.py`** for **`LOCKED_AT_100`** on new **`debug=True`/`False`** branch pairs — not golden log-line asserts.

---

### AST-701 · AST-700

**AST-701:** **`fetch_website_batch`** mirrors **`scrape_jd_batch`** — scrape homepage visible text + **`nav_links`** for **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`** companies; pass **`HOMEPAGE_READY`**, fail **`CANNOT_READ_WEBSITE`** with **`prefilter_company_notes`**. Shared **`scrape_company_homepage_content`** helper in roster (**`prefilter_company`** refactor unchanged observable outcomes). Consult routes **`dispatch_task_key=fetch_website`** before **`run_company_task`**. Config: **`HOMEPAGE_READY`**, **`GAZER_CONFIG["fetch_website"]`**, **`homepage_text`** company_data key, dispatch registry. Database: **`_RETRY_TASK_SEED`** companion **`WEBSITE_FOUND_RETRY`** row.

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

**Collapse consecutive blank lines** in gazer visible-text save paths — **`scrape_jd_batch`** (JD **`job_description`**) and **`fetch_website_batch`** (**`homepage_text`**) call **`collapse_consecutive_blank_lines`** immediately after scrape, before empty-text gating / persist. **`nav_links`** and **`_prune_jd`** unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| JD post-scrape normalize + empty gate order | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestScrapeJdBatch::test_collapses_consecutive_blank_lines_before_save` |
| Homepage post-scrape normalize | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestFetchWebsiteBatch::test_collapses_consecutive_blank_lines_in_homepage_text` |
| Shared helper | `src/utils/formatting.py` | `tests/component/utils/test_formatting.py::TestCollapseConsecutiveBlankLines` |

**AST-713** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestCollapseConsecutiveBlankLines \
  tests/component/core/test_gazer.py::TestScrapeJdBatch::test_collapses_consecutive_blank_lines_before_save \
  tests/component/core/test_gazer.py::TestFetchWebsiteBatch::test_collapses_consecutive_blank_lines_in_homepage_text \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.
