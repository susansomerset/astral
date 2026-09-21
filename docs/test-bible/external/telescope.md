# Telescope (platform HTTP client)

**Test module:** `tests/component/external/test_telescope.py`

Replaces retired `src/external/playwright.py` (AST-1726). Public drop-in names (`PlaywrightInfraError`, `classify_playwright_failure`, `[playwright:…]` prefixes) stay for core routing.

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/external/telescope.py` | `tests/component/external/test_telescope.py` | yes (`LOCKED_AT_100`) |

**Retired:** `docs/test-bible/external/playwright.md` — historical AST-853 paths; live map is this file.

---

### AST-853 · AST-850 (historical — browser session)

**Original scope:** Firefox batch stability. **AST-1726** moved the module to Telescope HTTP; classifier + infra error type + drop-in `get_page` remain under the same public names in `telescope.py`.

| Area | Source | Component tests |
| --- | --- | --- |
| Failure classifier + infra error type | `src/external/telescope.py` | `test_telescope.py::TestClassifyPlaywrightFailure`, `::TestPlaywrightInfraError` |
| `get_page` drop-in (PageHandle) | `src/external/telescope.py` | `test_telescope.py::TestGetPageDropIn` |
| HTTP pool failover / timeout | `src/external/telescope.py` | `test_telescope.py::TestTelescopePoolHttp` |

Gazer batch + roster scrape manifests: **`docs/test-bible/core/gazer.md`** · **`docs/test-bible/core/roster.md`**.

---

### AST-1726 · AST-1721 (platform telescope.py drop-in / playwright decommission)

**Scope:** `src/external/telescope.py` full drop-in; delete `playwright.py`; core import-path rewires; `TELESCOPE_CONFIG`; cull default on; no platform Firefox install scripts; `LOCKED_AT_100` retarget.

| Area | Component tests |
| --- | --- |
| Module gone | `test_telescope.py::TestPlaywrightModuleGone` |
| Cull default on/off | `test_telescope.py::TestCullHtmlDefault` |
| HTTP pool 5xx failover + timeout + missing bearer | `test_telescope.py::TestTelescopePoolHttp` |
| TELESCOPE_CONFIG + trimmed PLAYWRIGHT_CONFIG | `test_config.py::TestAst1726TelescopeConfig`, `::TestAst853PlaywrightConfig` |
| Roster import + readiness (empty≠listing timeout) | `test_roster.py` imports `telescope`; `TestAst689ScrapeReadiness` |
| Infra prefix unchanged | `test_roster.py::…::test_playwright_infra_error_prefixes_failure_class` |

**AST-1726** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_telescope.py \
  tests/component/utils/test_config.py::TestAst853PlaywrightConfig \
  tests/component/utils/test_config.py::TestAst1726TelescopeConfig \
  tests/component/core/test_roster.py::TestAst689ScrapeReadiness \
  tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_playwright_infra_error_prefixes_failure_class \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

**Out of scope:** Railway/CI fence (**AST-1727**), service container (**AST-1725**), Surfer.
