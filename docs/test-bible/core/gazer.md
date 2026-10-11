# Gazer

**Test module:** `tests/component/core/test_gazer.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/gazer.py` | `tests/component/core/test_gazer.py` | yes |

---

### AST-2086 · AST-2073 (pointer)

**`TestAst2086GazerBotWallSplit`** — AC4 bot split: fetch_website (`_fetch_website_fail_destination` bot-first), fetch_job_pages (walled PJL dropped like a failed scrape; prior capture survives), fetch_culture_pages (fresh + cached, all-walled only; `_website_content_bot_walled` shapes). **`TestAst1195BotBlockedErrorState`** — per-task `classified_states`; `_JD_ERROR_STATES` removed. fetch_relative_jd short text → `ERROR_FETCH_RELATIVE_JD_UNREADABLE`. Primary manifest: **`docs/test-bible/utils/config.md`** § AST-2086.

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

**`fetch_job_pages_batch`** debug outcomes report **`visible_chars`** + **`nav_links`** count per URL. ~~Skipped ledger URLs log **`skipped-already-scraped`** when **`debug=True`**.~~ (**AST-1995**: no ledger skip — every candidate URL is scraped and gets its own per-URL line; see § AST-1999.) Persist path unchanged — enriched **`_scrape_pjl_page`** records carry **`enumerated_nav_links`** into **`pjl_scrape_pages`** / **`pjl_assembled_content`**.

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

**`fetch_job_pages_batch`** — ~~additive~~ Playwright scrape of **`possible_joblist_links`** (AST-718 ledger; **AST-1995** replaced additive skip with refresh/upsert — § AST-1999); persist **`pjl_scrape_pages`**, **`pjl_assembled_content`**, optional **`pjl_nav_links`**; pass **`PJL_READY`**, fail **`JOBSITE_SCRAPE_ISSUE`**. Consult routes **`dispatch_task_key=fetch_job_pages`** before **`run_company_task`**. Config: **`PJL_READY`**, **`GAZER_CONFIG["fetch_job_pages"]`**, dispatch registry.

| Area | Source | Component tests |
| --- | --- | --- |
| **`fetch_job_pages_batch`** connectivity / missing ledger / pass / refresh re-scrape (was additive skip) / empty fail | `src/core/gazer.py` | `tests/component/core/test_gazer.py::TestFetchJobPagesBatch` |
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

### AST-1999 · AST-1994 (gap — PJL refresh; product AST-1995)

**Parent:** [AST-1994](https://linear.app/astralcareermatch/issue/AST-1994) (orphaned mini-parent). **Publish:** `origin/sub/AST-1994/AST-1999-fetch-refresh-tests`. **Gap from** `[board-betty] TESTS: REVISE` on **AST-1995** — product (re-scrape every candidate URL, upsert `pjl_scrape_pages` by `normalize_link`, rebuild + always write `pjl_nav_links` from this run, failed/empty re-scrape keeps the prior row and carries its nav links) is **AST-1995** (`origin/sub/AST-1994/AST-1995-fetch-refresh`); this ticket is test tree + bible only. Plan: `docs/features/roster/ast-719-fetch-job-pages-gazer-batch-and-pjl-ready-state.md` § Bug: AST-1995.

| Area | Source | Component tests (`TestFetchJobPagesBatch::`) |
| --- | --- | --- |
| Stored URL re-scraped; replaced row keeps index, new URL appends; per-URL Style D line, no `skipped-already-scraped` | `src/core/gazer.py` | `test_refresh_rescrapes_already_scraped_url` (rewrite of `test_additive_skips_already_scraped_url`) |
| Plan repro — row replaced, assembled drops OLD BOARD, nav rebuilt (dead link gone), `PJL_READY` | same | `test_ast1995_repro_rescrape_replaces_row_and_rebuilds_nav` |
| Failed re-scrape with prior row — row + its nav kept, stale global nav dropped, debug `error=` line | same | `test_ast1995_failed_rescrape_keeps_prior_row_and_carries_its_nav` |
| Failed/empty capture with no prior row contributes no nav | same | `test_ast1995_failed_scrape_without_prior_row_contributes_no_nav` |
| `pjl_nav_links` written even when `""`; non-candidate rows left in place (no pruning) | same | `test_ast1995_nav_written_empty_and_non_candidate_rows_kept` |
| Fail paths `debug` False/True (`LOCKED_AT_100` pairs) | same | `test_missing_possible_joblist_links_fails[*]`, `test_all_scrapes_empty_fails_with_notes[*]` (parametrized) |

Roster upsert nodes: **`docs/test-bible/core/roster.md`** § AST-1999.

**Broken / obsolete:** `test_additive_skips_already_scraped_url` — rewritten (refresh semantics). Pre-existing drift fixed in the same class: module helper **`_mock_browser_context`** (renamed away by AST-853 for `fetch_website`; `fetch_job_pages_batch` still opens `create_browser_context`) restored — four AST-719 nodes were `NameError`; stale `"errors": 0` in expected return dicts removed (`fetch_job_pages_batch` never returns `errors`).

**Integration:** none.

**Sequencing deviation (gap child):** product not on ftr yet. `[bug-repro]` proven both ways — **RED on pre-fix tree** (9 nodes across gazer + roster; assertion diffs, no import/name errors) and **GREEN with AST-1995 plan `## Proposed change` overlaid** on `src/core/gazer.py` + `src/core/roster.py` (scratch, restored, not committed); overlay coverage of `fetch_job_pages_batch` + `_merge_pjl_scrape_record` 100% lines/branches.

## QA test manifest (AST-1999)

1. `[bug-repro]` nodes (must flip red→green under `test-fix` once AST-1995 lands): gazer `test_refresh_rescrapes_already_scraped_url`, `test_ast1995_repro_rescrape_replaces_row_and_rebuilds_nav`, `test_ast1995_failed_rescrape_keeps_prior_row_and_carries_its_nav`, `test_ast1995_failed_scrape_without_prior_row_contributes_no_nav`, `test_ast1995_nav_written_empty_and_non_candidate_rows_kept`; roster `test_merge_pjl_scrape_record_replaces_duplicate_and_skips_empty`, `test_ast1995_upsert_replaces_matching_row_in_place`, `test_ast1995_error_record_discarded_even_with_text`, `test_ast1995_whole_row_replace_drops_enumerated_nav_links`
2. Guards stay green: rest of both classes (connectivity, missing links ×2, success persist, all-empty fail ×2, assemble ×2, nav-links append, enumerated-nav persist)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestFetchJobPagesBatch \
  tests/component/core/test_roster.py::TestAst719PjlRosterHelpers \
  -q
```

**Pass criterion:** pytest green on both classes (19 nodes) with AST-1995 product merged — not zero-arg harness / branch-lock gate (both files carry ~53 unrelated pre-existing reds on this tip, outside this gap).

**Bible shasum (after publish):** `git show origin/sub/AST-1994/AST-1999-fetch-refresh-tests:docs/test-bible/core/gazer.md | shasum`

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

External taxonomy + **`get_page`** recovery: **`docs/test-bible/external/telescope.md`** (**AST-853**). Roster infra error prefix: **`docs/test-bible/core/roster.md`** (**AST-853**).

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

**AST-892 revision:** skip path returns `skipped` + work-only `total` (pure skip → `total=0`); claim/count exclusion is primary — see **`docs/test-bible/data/database/dispatch_tasks.md`** (**AST-892**).

**AST-1810 (supersedes the skip above):** the second-strike skip is removed — every claimed `WEBSITE_FOUND_RETRY` row is scraped; the return dict keeps `skipped`, always 0. Revised nodes: `::test_scrapes_wfr_even_when_homepage_text_present` (was `test_skips_wfr_when_homepage_text_present`) and `::test_mixed_second_strike_and_fresh_both_scrape` (was `test_mixed_skip_and_scrape_excludes_skips_from_total`). Primary manifest: **`docs/test-bible/data/database/dispatch_tasks.md`** (**AST-1810**).

Roster + claim: **`docs/test-bible/core/roster.md`** · **`docs/test-bible/utils/config.md`** (**AST-882**).

### AST-1014 · AST-952

`title_patterns` under `contact`. Primary: **`docs/test-bible/core/candidate.md`** § AST-1014 — revised **`TestCompiledTitlePatterns`**.

### AST-1061 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`.

`ingest_meteorite_jobs_from_email_html(_sync)`: body vs links modes; Playwright fetch (mocked); `known_job_link` / `known_company_job_id` / `jd_too_short` skips; Style D when `debug=True`.

| Area | Source | Component tests |
| --- | --- | --- |
| Email ingest + dedupe | `src/core/gazer.py` | **`TestAst1061MeteoriteEmailIngest`** (appended to **`test_gazer.py`**) |

**Broken / obsolete:** none — additive ingest path.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestAst1061MeteoriteEmailIngest \
  -q
```

### AST-1131 · AST-1130

**Parent:** [AST-1130 — Manage Email create button for job lists isn't working](https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working). **Publish:** `origin/sub/AST-1130/AST-1131-normalize-pasted-list-email-html`.

`ingest_meteorite_jobs_from_email_html` calls `normalize_pasted_list_email_html` before `_meteorite_email_candidate_links`. Primary helper: **`docs/test-bible/utils/formatting.md`** (**AST-1131**).

| Area | Source | Component tests |
| --- | --- | --- |
| Ingest after paste normalize | `src/core/gazer.py` | **`TestAst1131NormalizePastedListEmailIngest`** (+ regression **`TestAst1061MeteoriteEmailIngest`**) |

**Broken / obsolete:** none — normalize is idempotent on clean HTML; AST-1061 cases remain green.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestAst1131NormalizePastedListEmailIngest \
  tests/component/core/test_gazer.py::TestAst1061MeteoriteEmailIngest \
  -q
```

### AST-1132 · AST-1130

**Parent:** [AST-1130 — Manage Email create button for job lists isn't working](https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working). **Publish:** `origin/sub/AST-1130/AST-1132-job-link-hygiene-non-job-create-skip`.

`_meteorite_email_candidate_links` applies expanded excludes + optional allow. Links ingest: final-URL exclude (`excluded_link`), non-job visible markers (`non_job_page`), candidate-scoped dedupe. Config: **`docs/test-bible/utils/config.md`**; data helpers: **`docs/test-bible/data/database/jobs.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Hygiene + non-job skip + scoped dedupe | `src/core/gazer.py` | **`TestAst1132MeteoriteEmailIngestHygiene`**; revised **`TestAst1061MeteoriteEmailIngest`** (company `candidate_id`) |

**Broken / obsolete:** AST-1061 dedupe fixtures that seeded companies without `candidate_id` — revised so candidate-scoped helpers still exercise skip paths.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestAst1132MeteoriteEmailIngestHygiene \
  tests/component/core/test_gazer.py::TestAst1061MeteoriteEmailIngest \
  -q
```

### AST-1146 · AST-1130 (UAT)

**Parent:** [AST-1130 — Manage Email create button for job lists isn't working](https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working). **Publish:** `origin/sub/AST-1130/AST-1146-uat-create-skips-null-company-job-id-dedupe`.

Create ingest still calls `text_matches_known_company_job_id_for_candidate`; short stored ids no longer produce `known_company_job_id` skips. Helper: **`docs/test-bible/data/database/jobs.md`** (**AST-1146**).

| Area | Source | Component tests |
| --- | --- | --- |
| Create skip vs short id | `src/core/gazer.py` (via helper) | **`TestAst1146CreateSkipShortCompanyJobId`** |

**Broken / obsolete:** none — long-id AST-1061 body skip still holds.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestAst1146CreateSkipShortCompanyJobId \
  tests/component/core/test_gazer.py::TestAst1061MeteoriteEmailIngest::test_body_mode_skips_known_company_job_id \
  -q
```

### AST-1195 · AST-1188

**Parent:** [AST-1188 — Errors for qualify_meteorite dispatch task](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task). **Publish:** `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked`.

`_JD_ERROR_STATES["bot"]` → **`BOT_BLOCKED`** (cookie/missing/closed stay `JD_SCRAPE_FAIL_*`). Config registry / schema: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Bot → `BOT_BLOCKED` map | `src/core/gazer.py` | **`TestAst1195BotBlockedErrorState`** |

**Broken / obsolete:** none in gazer tests (classification still returns `"bot"`; state name change only).

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestAst1195BotBlockedErrorState \
  -q
```

### AST-1197 · AST-1188

**Parent:** [AST-1188 — Errors for qualify_meteorite dispatch task](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task). **Publish:** `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`.

Shared `jd_classifier.bot_signals` widened so parent-captured Cloudflare interstitial scores ≥ `bot_threshold` (2) → `"bot"`. Consult apply: **`docs/test-bible/core/consult.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Challenge body → bot | `src/core/gazer.py` / config signals | **`TestAst1197ChallengeBotSignals`** |

**Broken / obsolete:** none.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestAst1197ChallengeBotSignals \
  -q
```

### AST-1516 · AST-1414

**Parent:** [AST-1414 — Estelle needs to be able to use our endpoints](https://linear.app/astralcareermatch/issue/AST-1414/estelle-needs-to-be-able-to-use-our-endpoints). **Publish:** `origin/sub/AST-1414/AST-1516-gazer-scrape-contact-task`.

`contact_task_gazer_scrape`: one-URL Playwright scrape via `extract_page_scrape_contract`; `_classify_jd` → Estelle-facing `page_status` (`cookie`/`bot` → `blocked`); no job create/transition. Dispatch/follow-up owned by **AST-1515**.

| Area | Source | Component tests |
| --- | --- | --- |
| Handler payload + map + Style D + no persist | `src/core/gazer.py` | **`TestAst1516ContactTaskGazerScrape`** |

**Broken / obsolete (AST-1515 revise this pass):** `TestAst1515ContactTaskMarkup` / turn fixtures that pinned `gazer_scrape` → `handler_unavailable` — retargeted to `create_contact_meteorite` (still missing until AST-1517). See **`docs/test-bible/core/contact.md`** § AST-1515.

**Integration:** no existing scenario asserts contact-task gazer scrape — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestAst1516ContactTaskGazerScrape \
  tests/component/core/test_contact.py::TestAst1515ContactTaskMarkup \
  tests/component/core/test_contact.py::TestAst1515ContactEstelleTurnMarkup \
  -q
```

### AST-1704 · AST-1640

**Parent:** [AST-1640 — Job source_entity parent](https://linear.app/astralcareermatch/issue/AST-1640). **Publish:** `origin/sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers`.

`validate_title_batch` skips title-pattern screen when `source == meteorite` (not `is_meteorite_company(company)`). Primary manifest: **`docs/test-bible/core/consult.md`** § AST-1704.

| Area | Source | Component tests |
| --- | --- | --- |
| Skip meteorite source; roster peer fails | `src/core/gazer.py` | **`TestValidateTitleBatch::test_skips_meteorite_source_roster_still_fails`** (revised) |

**Broken / obsolete this pass:** `test_skips_meteorite_company_roster_still_fails` — retargeted to `source` SoT (+ real `company_id` must stay skipped).

**Integration:** none.

### AST-2002 · AST-1928 (bug-repro for AST-1997)

**Parent:** AST-1928 (gaze scrape failure reason). **Publish:** `origin/sub/AST-1928/AST-2002-scrape-failure-message-coverage`. Product fix: **AST-1997** (`process_gazer_batch` only).

`process_gazer_batch` failure branch records the real reason in `record_to_company_job_scan(failure_message=…)` and the outcome `message`: `Scrape failed: <ExceptionType>: <str(e)>`, `Scrape failed: <ExceptionType>` when `str(e)` is empty, `No job_site to scrape` for a blank `job_site`. Same text for `debug=False` and `debug=True`. **Red on pre-fix tree** (hard-coded `"Scrape failed"`); flips green when AST-1997 lands.

| Area | Source | Component tests |
| --- | --- | --- |
| Scrape-failure reason on scan row + outcome, debug on/off | `src/core/gazer.py` | **`test_gazer_scrape_failure.py::TestProcessGazerBatchFailureMessage`** (new) |

**Broken / obsolete this pass:** none. `TestProcessGazerBatch` / `TestProcessGazerBatchDebugBranchCoverage` assert status/call counts only; `test_roster.py` `"scrape failed"` asserts cover `_fetch_job_links_content`, not gaze.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer_scrape_failure.py::TestProcessGazerBatchFailureMessage \
  tests/component/core/test_gazer.py::TestProcessGazerBatch \
  tests/component/core/test_gazer.py::TestProcessGazerBatchDebugBranchCoverage \
  -q
```

### AST-2004 · AST-1998 (shared `is_bot_wall`)

Public `is_bot_wall(text)` = the `jd_classifier` bot-signal count vs `bot_threshold`; `_classify_jd` delegates (one detector — roster select calls the same helper). `None` text safe.

| Area | Source | Component tests |
| --- | --- | --- |
| threshold hit / single-signal miss / `None` | `src/core/gazer.py` | **`TestAst2004IsBotWall::test_threshold_hit_and_miss`** |
| `_classify_jd` routes through `is_bot_wall` | same | **`TestAst2004IsBotWall::test_classify_jd_delegates`** |

Regression guards unchanged: **`TestAst1197ChallengeBotSignals`**, **`TestAst1195BotBlockedErrorState`**. Manifest: **`docs/test-bible/core/roster.md`** § AST-2004.

### AST-2025 · AST-2022 (`fetch_relative_jd_batch` click-through runner + shared `_apply_jd_gates`)

**Scope:** `_apply_jd_gates` lifts the JD gates (collapse → empty → prune → `min_chars` → `_classify_jd` → `_JD_ERROR_STATES`) out of `fetch_jd_batch`; new `fetch_relative_jd_batch` clicks the stored relative `job_link` on the company `job_site` via `click_through_visible_text`, writes the resolved URL with `persist_http_job_link`, then runs the same gates. Qualify routing + router branch: [`consult.md`](consult.md) § AST-2025; dispatch claim / picker: [`dispatcher.md`](dispatcher.md) / [`../ui/api/api_admin.md`](../ui/api/api_admin.md) § AST-2025.

| Area | Component tests |
| --- | --- |
| AC4 ok → `JD_READY` + JD saved; bot → `BOT_BLOCKED`; closed → `JD_SCRAPE_FAIL_CLOSED` (link resolved); click miss → `RELATIVE_LINK_FAIL` (link relative) — real `_classify_jd` on config signals | `TestAst2025FetchRelativeJdBatch::test_ac4_outcomes` |
| Miss = one WARNING, no traceback; other Telescope error = one ERROR with `exc_info`; both → `RELATIVE_LINK_FAIL` | `…::test_click_miss_warns_other_error_logs_exception` |
| Non-http `final_url` → `RELATIVE_LINK_FAIL`, nothing persisted | `…::test_non_http_final_url_fails_without_persist` |
| Missing `job_site` / `job_link` → `RELATIVE_LINK_FAIL`, no click | `…::test_missing_job_site_or_link_fails_without_click` |
| Empty / short text after a reached destination → `ERROR_FETCH_RELATIVE_JD_UNREADABLE` (**AST-2086**; was fetch_jd's `JD_SCRAPE_FAIL`), link resolved | `…::test_short_text_after_click_is_relative_unreadable_with_link_resolved` |
| No connectivity → `ConnectionError` | `…::test_aborts_without_connectivity` |
| AC5 both runners call `_apply_jd_gates` (`short_state` / `pass_state`) | `…::test_ac5_both_runners_call_shared_gate_helper` |
| `fetch_jd_batch` behavior after the lift (regression) | `TestFetchJdBatch` (minus two pre-existing reds below) |

Test-data note: bot / closed signals must trail the body — `_prune_jd` trims the page head before classification.

**Broken / obsolete (revised):** two `test_consult.py` nodes — see [`consult.md`](consult.md) § AST-2025. **Pre-existing red (not AST-2025):** `TestFetchJdBatch::test_passes_with_existing_job_data` / `::test_collapses_consecutive_blank_lines_before_save` expect an `errors` key `fetch_jd_batch` never returns — identical before and after this diff. Across `test_gazer` / `test_consult` / `test_dispatcher` / `test_api_admin` / `test_tracker`, the only failures this diff introduced were the two revised nodes (60 baseline reds unchanged).

**Observation for Susan (not pinned):** a relative-link qualify pass returns `RELATIVE_JOB_LINK` ≠ `pass_state`, so `qualify_job_listings`' summary counts it in `failed`, not `passed`. ACs are state-based; no test asserts the count either way.

**Integration:** none.

## QA test manifest

1. **Gap + revised (required):**

```bash
/home/susan/astral/.venv/bin/python -m pytest \
  tests/component/core/test_gazer.py::TestAst2025FetchRelativeJdBatch \
  tests/component/core/test_gazer.py::TestFetchJdBatch \
  tests/component/core/test_consult.py::TestQualifyJobListings::test_relative_link_routes_to_relative_job_link \
  tests/component/core/test_consult.py::TestAst1895InvalidJobLinkError \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_ast2025_routes_fetch_relative_jd_batch \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast2025_fetch_relative_jd_claims_trigger_state_and_releases_on_error \
  tests/component/ui/api/test_api_admin.py::TestAst2025FetchRelativeJdDispatchTaskKey \
  --deselect tests/component/core/test_gazer.py::TestFetchJdBatch::test_passes_with_existing_job_data \
  --deselect tests/component/core/test_gazer.py::TestFetchJdBatch::test_collapses_consecutive_blank_lines_before_save \
  -q
```

2. **AC3 (required):** `rg -n 'raise InvalidJobLinkError' src/core/consult.py` → exactly one hit, directly under `if not job_link:`.
3. **AC5 (required):** `rg -n '_apply_jd_gates' src/core/gazer.py` → one `def` + one call in `fetch_jd_batch` + one in `fetch_relative_jd_batch`; no `_classify_jd(` call inside either runner body.

**Pass criterion:** all three — not zero-arg harness / branch-lock gate (baseline reds in these files unchanged by AST-2025).

### AST-2070 · AST-2054 (GET_UPSHOT culture fetch)

**Parent:** [AST-2054](https://linear.app/astralcareermatch/issue/AST-2054). **Publish:** `origin/sub/AST-2054/AST-2070-upshot-hops`. Primary block + manifest: [`roster.md`](roster.md) § AST-2070.

`fetch_company_culture_pages_batch`: connectivity loss raises before any transition; otherwise every company → `UPSHOT_READY` (cached `website_content` skips the coat-check; scraped / none found / coat-check `ValueError` / missing `company_data` all advance). Returns `{passed: n, failed: 0, total: n}`.

| AC | Component tests |
| --- | --- |
| 4 GET_UPSHOT always advances; connectivity abort | new **`TestAst2070FetchCompanyCulturePagesBatch`** (3 incl. debug parametrize) in `test_gazer.py` |

**Broken / obsolete:** none — additive function.

### AST-2132 · AST-2130 (gazer owns telescope_data; gazer scrapes keep everything)

**Parent:** [AST-2130](https://linear.app/astralcareermatch/issue/AST-2130). **Publish:** `origin/sub/AST-2130/AST-2132-gazer-telescope-owner`. Plan: `docs/features/foundation/ast-2132-gazer-owns-telescope-data-gazer-scrapes-keep-everything.md`. Table / data functions: [`../data/database/telescope_data.md`](../data/database/telescope_data.md) § AST-2131.

Gazer API: `is_telescope_id`, `keep_telescope_data` (blank → `None`, nothing stored), `keep_page_scrape`, `scrape_visible_text_and_keep` / `scrape_page_links_and_keep`, `resolve_telescope_value` (id / `[{url, id}]` / legacy passthrough; missing rows → warning, dropped, all-missing → `None`). Writers keep every capture before routing: `fetch_website` stores `homepage_text` / `nav_links` as ids; `fetch_job_pages` keeps each page and writes `pjl_assembled_content` / `pjl_nav_links` as `None` (`pjl_scrape_pages` stays text rows until AST-2134); `fetch_jd` / `fetch_relative_jd` store `jd_telescope_data_id` (raw capture) on pass **and** classified — never `job_description`; culture caches resolve ids.

| Area | Component tests |
| --- | --- |
| API branches (id shape, blank keep, page keep ± links, scrape wrappers incl. empty / final_url fallback, resolve shapes + missing-row warning) | new **`TestAst2132TelescopeApi`** (6) |
| Culture caches resolve ids (cached ok / bot-walled / missing row → coat-check, coat-check ids resolved; GET_UPSHOT cached ids) | **`TestAst2132TelescopeApi::{test_culture_pages_cached_ids_resolve,test_company_culture_cached_ids_resolve}`** |
| AC3 kept with `candidate_id` — homepage + links; PJL page; JD classified + passed; relative ok / bot / closed | revised **`TestFetchWebsiteBatch::test_success_persists_homepage_and_nav_links`**, **`TestFetchJobPagesBatch::test_success_transitions_pjl_ready_and_persists`**, **`TestFetchJdBatch::test_routes_classified_failures_and_passes`**, **`TestAst2025FetchRelativeJdBatch::test_ac4_outcomes`** |
| AC3 bot walls still kept | **`TestAst2086GazerBotWallSplit::{test_fetch_website_bot_wall_is_bot_blocked_not_homepage,test_fetch_job_pages_all_walled_is_bot_blocked}`** (asserts added) |
| AC5 ids not text; derived PJL fields `None` | revised website ×2 + **`TestAst882HomepageReadyWfrSkip::test_scrapes_wfr_even_when_homepage_text_present`**; PJL ×5 below |

**Broken / obsolete (revised this pass):** `TestFetchWebsiteBatch` ×2 + AST-882 WFR (`homepage_text` text → id); `TestFetchJobPagesBatch::{test_success_transitions_pjl_ready_and_persists, test_ast1995_repro_rescrape_replaces_row_and_rebuilds_nav, test_ast1995_failed_rescrape_keeps_prior_row_and_carries_its_nav, test_ast1995_failed_scrape_without_prior_row_contributes_no_nav, test_ast1995_nav_written_empty_and_non_candidate_rows_kept}` (assembled / nav rebuild + carry-forward retired → `None`; names kept for node-id stability); `TestFetchJdBatch::test_routes_classified_failures_and_passes`, `TestAst2025FetchRelativeJdBatch::{test_ac4_outcomes, test_ac5_both_runners_call_shared_gate_helper}` (`get_visible_text` now `(text, final_url)`; `jd_telescope_data_id`; gate kwarg `telescope_data_id`). **Vacuous since the wrapper landed** (bare-string mocks failed on unpack, never reached the gates) — revised to tuple mocks + gate asserts: `test_fails_empty_and_short_job_descriptions`, `test_passes_with_existing_job_data`, `test_collapses_consecutive_blank_lines_before_save` (now: reference → raw capture), `TestFetchJdBatchDebugPaths::test_scrape_error_empty_short_and_classified_with_debug`, `TestFetchJdBatchDebugBranchCoverage::test_classified_failure_without_debug`.

**Isolation (required):** `test_gazer.py` gains an autouse **`_telescope_tmp_db`** fixture (core `sqlite_in_memory`) and core `conftest.py` resets **`_telescope_data_schema_ensured`**. Without it unpatched keeps write to the default `ASTRAL_DB_DIR=data/` — in epic worktrees `data/astral.db` is a symlink to the live DB.

**Coverage:** every new / modified `gazer.py` line and branch is covered by `test_gazer.py`; missed set equals the ftr baseline (59 stmts / 25 partial, shifted by the insert).

**Pre-existing (not this ticket):** `TestFetchWebsiteBatch::test_scrape_timeout_fails_with_labeled_infra_error`; `TestFetchJdBatch::{test_passes_with_existing_job_data, test_collapses_consecutive_blank_lines_before_save}` — still red **only** on the stale `"errors": 0` key (deselected in § AST-2025 too). `tests/component/core` failure set otherwise equals `origin/ftr/AST-2130-telescope-data`, except env-dependent `test_candidate.py::TestAst1881PrefilterRcDefaultVector::test_craft_prefilter_generate_merges_into_response_and_stash` (409 against the live DB via the `data/` symlink; passes with an empty `ASTRAL_DB_DIR`) and flaky `test_intake.py::TestIntakeSessionFlow::test_background_initiate_failure_writes_assistant_error` (passes alone).

**Integration:** none.

## QA test manifest

1. `tests/component/core/test_gazer.py` — all green except the 3 pre-existing nodes above.
2. `tests/component/data/database/test_telescope_data.py` — green (AST-2131 storage under the gazer API).
3. No-regression: `tests/component/core` (`--continue-on-collection-errors`) failure set equals the ftr baseline, modulo the two env / flaky nodes above.
4. AC4: `git grep -n -i "telescope_data" -- src/core src/ui ':!src/core/gazer.py'` shows no `database` telescope import / call; `git diff origin/dev...HEAD --stat -- src/external/telescope.py service/telescope` empty.
5. Live DB untouched: `telescope_data` row count in `~/astral/data/astral.db` is the same before and after item 1.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py \
  tests/component/data/database/test_telescope_data.py \
  --deselect tests/component/core/test_gazer.py::TestFetchWebsiteBatch::test_scrape_timeout_fails_with_labeled_infra_error \
  --deselect tests/component/core/test_gazer.py::TestFetchJdBatch::test_passes_with_existing_job_data \
  --deselect tests/component/core/test_gazer.py::TestFetchJdBatch::test_collapses_consecutive_blank_lines_before_save \
  -q
```

**Pass criterion:** items 1–5 — not zero-arg harness / branch-lock gate (pre-existing reds on the ftr tip).

**Bible shasum (after publish):** `git show origin/sub/AST-2130/AST-2132-gazer-telescope-owner:docs/test-bible/core/gazer.md | shasum`

### AST-2134 · AST-2130 (PJL ledger rows hold row ids)

`fetch_job_pages` passes `visible_text_id` / `page_links_id` to roster's `_merge_pjl_scrape_record`, so `pjl_scrape_pages` rows are `{url, id, links_id?}`. **Revised:** every `saved["pjl_scrape_pages"]` assert in `TestFetchJobPagesBatch` / `TestAst2086GazerBotWallSplit` (8) goes through **`_pjl_ledger`** — asserts the uuid row shape (legacy text rows pass) and compares roster's resolved view to the original expected rows. Manifest: [`roster.md`](roster.md) § AST-2134.
