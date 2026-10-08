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

---

### AST-1745 · AST-1721 (qa-fix bug-repro — cull preserves root svg.logo)

**Board REVISE:** `_cull_html` must preserve root `svg.logo` outerHTML on a class-scoped fragment; AST-1731/1736 cover capture resolve only, not platform cull erase.

| Area | Component tests |
| --- | --- |
| Root svg.logo fragment survives cull | `test_telescope.py::TestAst1745CullPreservesRootSvgLogo::test_cull_html_preserves_root_svg_logo_outerhtml` (**bug-repro**) |
| Nested svg under page content still stripped | `test_telescope.py::TestAst1745CullPreservesRootSvgLogo::test_cull_html_still_strips_nested_svg_under_page_content` |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_telescope.py::TestAst1745CullPreservesRootSvgLogo -q
```

---

### AST-1750 · AST-1721 (qa-fix bug-repro — _post_telescope debug dump)

**Board REVISE:** `_post_telescope` must emit ungated `logger.debug` callee-in (full request body) and callee-out (full response JSON) when `log_debug` is on; existing coverage has no HTTP-joint debug dump.

| Area | Component tests |
| --- | --- |
| Debug request body + full response | `test_telescope.py::TestAst1750PostTelescopeDebugDump::test_post_telescope_debug_emits_request_body_and_full_response` (**bug-repro**) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_telescope.py::TestAst1750PostTelescopeDebugDump -q
```

---

### AST-1840 · AST-1844 (qa-fix bug-repro — linear `_cull_html`, attribute snip, off-loop cull)

**Board REVISE:** nothing exercised the 2h event-loop freeze (`_in_preserved_svg` hashing bs4 Tags → quadratic `Tag.decode`; sync cull inside async `extract_page_dom`) or the new `html_cull` attribute snip (`max_html_tag_length` / `max_length_placeholder`). Product: **AST-1840**; tests on gap sibling **AST-1844**. `[bug-repro]` nodes red on pre-fix `31846c28`, green on AST-1840 (`fb472a98`). No wall-clock asserts, no size caps.

| Area | Component tests |
| --- | --- |
| Full `<body>` page cull never hashes a Tag (linear-time guard) | `test_telescope.py::TestAst1840CullHtmlLinearAndSnip::test_cull_html_full_page_never_hashes_tag` (**bug-repro**) |
| Snip: 500 kept, 501 → `(snipped)`, list `class` by joined length | `test_telescope.py::TestAst1840CullHtmlLinearAndSnip::test_cull_html_snips_attr_over_max_length` |
| Missing snip key → `ValueError` (both keys) | `test_telescope.py::TestAst1840CullHtmlLinearAndSnip::test_cull_html_missing_snip_key_raises` |
| `extract_page_dom` runs `_cull_html` off the loop thread | `test_telescope.py::TestAst1840CullHtmlLinearAndSnip::test_extract_page_dom_culls_off_event_loop` (**bug-repro**) |

**Broken / obsolete:** none — `TestCullHtmlDefault` and AST-1745 stay unchanged (monkeypatched `_cull_html` resolves at call time inside `to_thread`).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_telescope.py::TestAst1840CullHtmlLinearAndSnip \
  tests/component/external/test_telescope.py::TestCullHtmlDefault \
  tests/component/external/test_telescope.py::TestAst1745CullPreservesRootSvgLogo -q
```

---

### AST-1849 · AST-1850 (qa-fix bug-repro — one-shot loop teardown)

**Board REVISE:** no test referenced `close_loop_resources` / `aclose_current_loop` / `_LoopState` / `_pool._states`; one-shot `asyncio.run` callers leaked the per-loop asyncpg pool, LISTEN connection and `telescope-result-poller`. Product: **AST-1849** (`run_one_shot`); tests on gap sibling **AST-1850**. `[bug-repro]` node red on pre-fix `83a0c352` (`AttributeError`: no `run_one_shot`), green on ftr `0877d286` (AST-1849 `bf470756` merged). Control node green on both.

| Area | Component tests |
| --- | --- |
| `run_one_shot` releases loop state (pool + listener closed once, poller done, `_states` empty) | `test_telescope.py::TestAst1849OneShotLoopTeardown::test_run_one_shot_releases_loop_state` (**bug-repro**) |
| Exception re-raised unchanged, cleanup still done | `test_telescope.py::TestAst1849OneShotLoopTeardown::test_run_one_shot_reraises_and_still_releases` |
| No Telescope touch → value returned, no pool, `_states` unchanged | `test_telescope.py::TestAst1849OneShotLoopTeardown::test_run_one_shot_passthrough_without_telescope` |
| Control: bare `asyncio.run` leaves loop state open | `test_telescope.py::TestAst1849OneShotLoopTeardown::test_bare_asyncio_run_leaves_loop_state_control` |

**Broken / obsolete:** none. Call-site swaps (`api_admin`, `api_meteorite`, `api_inbox`, `gazer`, `contact`) need no new nodes; no test patches `asyncio.run` on those modules. Known residual: a single call site reverting to bare `asyncio.run` is not caught by these nodes.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_telescope.py::TestAst1849OneShotLoopTeardown -q
```

---

### AST-2023 · AST-2022 (Telescope click-then-capture — platform client)

**Scope:** `_post_telescope(click_href=…)` adds `body["click_href"]` only when set; `_TelescopeQueue.submit` maps queue `error_class="click_target_missing"` → `PlaywrightInfraError(TELESCOPE_CLICK_TARGET_MISSING)` (deliberately outside `PLAYWRIGHT_INFRA_FAILURE_CLASSES`); new public `click_through_visible_text(list_url, href) -> (final_url, text)` — one job, no client retry. Service half + full manifest: [`service/telescope.md`](../service/telescope.md) § AST-2023.

| Area | Component tests |
| --- | --- |
| Omitted option → pre-AST-2023 body key set exactly | `test_telescope.py::TestAst2023ClickThrough::test_post_telescope_without_click_href_body_unchanged` |
| `click_href` forwarded | `…::test_post_telescope_forwards_click_href` |
| Real `submit` maps `click_target_missing`; not an infra class | `…::test_submit_maps_click_target_missing` |
| Control: `scrape_failed` still `telescope_job_failed` | `…::test_submit_scrape_failed_still_job_failed_control` |
| `(final_url, text)` + body (`url`, `fields=["text"]`, `click_href`) | `…::test_click_through_returns_final_url_and_text` |
| List text joined `\n\n`; missing keys → `("", "")` | `…::test_click_through_joins_list_text_and_defaults_empty` |
| Missing target raises; exactly one `submit` (no retry) | `…::test_click_through_raises_on_missing_target_without_retry` |

`submit` tests drive the real method with a fake asyncpg pool (`_get_db` / `_state` / `_maybe_wake` patched; waiter future resolved with a canned failed row).

**Broken / obsolete:** none caused by this diff. **Pre-existing red on `origin/dev` (not AST-2023):** `TestTelescopePoolHttp` (×3) and `TestAst1750PostTelescopeDebugDump` patch the retired HTTP pool (`_pool.request` / `_TelescopePool`); the module is now a Postgres queue client. Not revised here — retire/retarget needs Susan's scope call.

**`LOCKED_AT_100`:** `test_telescope.py` alone reaches 39% branch on `src/external/telescope.py` before AST-2023 and 45% with the AST-2023 nodes (the queue / fetch paths have no live tests since the HTTP→queue move); the full-tree lock gate could not be measured here because five unrelated modules fail collection on `origin/dev`. AST-2023's new branches are covered by these nodes.
