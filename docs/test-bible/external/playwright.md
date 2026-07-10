# Playwright

**Test module:** `tests/component/external/test_playwright.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/external/playwright.py` | `tests/component/external/test_playwright.py` | yes |

---

### AST-765 · AST-757 (SUNSET — documentation)

**RETIRED (AST-757):** Boards channel removed from product (**AST-765**) and schema (**AST-766**). No active boards manifest obligations. See **`docs/ASTRAL_CODE_RULES.md` §3.7**.

---

### AST-853 · AST-850

**Scope:** Production **`fetch_website`** batch browser stability — **`PLAYWRIGHT_CONFIG`**, failure taxonomy (**`classify_playwright_failure`**, **`PlaywrightInfraError`**), **`BatchBrowserSession`** + **`get_page`** recovery, **`fetch_website_batch`** wiring (sibling **AST-854** owns state routing). **`src/external/playwright.py`** is **`LOCKED_AT_100`** — narrowed manifest only.

| Area | Source | Component tests |
| --- | --- | --- |
| Failure classifier + infra error type | `src/external/playwright.py` | `tests/component/external/test_playwright.py::TestClassifyPlaywrightFailure`, `::TestPlaywrightInfraError` |
| **`get_page`** batch recovery | `src/external/playwright.py` | `tests/component/external/test_playwright.py::TestGetPageBatchRecovery` |
| **`PLAYWRIGHT_CONFIG`** literals | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst853PlaywrightConfig` |

Gazer batch + roster scrape manifests: **`docs/test-bible/core/gazer.md`** · **`docs/test-bible/core/roster.md`** (**AST-853**).

**AST-853** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_playwright.py::TestClassifyPlaywrightFailure \
  tests/component/external/test_playwright.py::TestPlaywrightInfraError \
  tests/component/external/test_playwright.py::TestGetPageBatchRecovery \
  tests/component/utils/test_config.py::TestAst853PlaywrightConfig \
  tests/component/core/test_gazer.py::TestFetchWebsiteBatch \
  tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_playwright_infra_error_prefixes_failure_class \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.
