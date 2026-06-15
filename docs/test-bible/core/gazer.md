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
