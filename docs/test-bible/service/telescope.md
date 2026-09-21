# Telescope service (`service/telescope/`)

**Test modules:** `tests/component/service/test_telescope_*.py`

Isolated FastAPI microservice — **not** under `src/`. Flat imports (`from auth import …`); component conftest puts `service/telescope/` on `sys.path`. No `LOCKED_AT_100` (coverage gate is `--cov=src` only).

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `service/telescope/capture.py` | `tests/component/service/test_telescope_capture.py` | no |
| `service/telescope/app.py` + auth | `tests/component/service/test_telescope_app.py` | no |
| Import fence + Dockerfile / requirements | `tests/component/service/test_telescope_fence.py` | no |
| Railway Phase 1 + bidirectional CI fence | `tests/component/service/test_telescope_deploy_ci.py` | no |

**Integration tier:** no existing `tests/integration/` scenario exercises Telescope (platform client is sibling **AST-1726**). No integration revision this pass.

---

### AST-1725 · AST-1721 (Telescope service container and API)

**Scope:** Stand up `service/telescope/` — FastAPI `/telescope`, `/telescope/html`, `/healthz`; bearer auth; one-Firefox pool (mocked in component tests); expand/links default on, wait_ready default off; multi-match text; console-only (no DB); zero `src` imports; Dockerfile Playwright `1.49.1-jammy` + single uvicorn worker.

| Area | Component tests |
| --- | --- |
| Request defaults (expand / links / wait_ready) | `test_telescope_app.py::TestTelescopeRequestDefaults` |
| Bearer 401 on `/healthz` + `/telescope` | `test_telescope_app.py::TestBearerAuth` |
| `/healthz` ok vs unhealthy 503 | `test_telescope_app.py::TestHealthz` |
| `POST /telescope` + `/telescope/html` contract | `test_telescope_app.py::TestTelescopeRoutes` |
| Timeout 504 / scrape_failed 502 | `test_telescope_app.py::TestRunBrowserJobErrors` |
| Multi-match / single / empty `capture_text` | `test_telescope_capture.py` |
| Zero `src` imports + Dockerfile pin | `test_telescope_fence.py` |

**AST-1725** narrowed run:

```bash
# ensure_component_venv.sh installs fastapi/pydantic/httpx when service/telescope exists
./scripts/testing/run_component_tests.sh tests/component/service/ -q
```

**Pass criterion:** pytest green on `tests/component/service/` — not zero-arg harness / branch-lock gate.

**Out of scope for this manifest:** Railway/CI (**AST-1727**), platform `src/external/telescope.py` (**AST-1726**), live Firefox / Docker image build.

---

### AST-1727 · AST-1721 (Railway Phase 1 deploy + import-boundary CI)

**Scope:** `service/telescope/railway.toml` (Phase 1 `numReplicas = 1`, Dockerfile builder, memory ceiling, no `healthcheckPath`); `scripts/ci/check-service-src-import-fence.sh` + `.github/workflows/service-src-import-fence.yml` — bidirectional anchored import fence (`service/telescope` ↔ `src`).

| Area | Component tests |
| --- | --- |
| railway.toml Phase 1 contract | `test_telescope_deploy_ci.py::TestRailwayPhase1Toml` |
| `src` → `service` import scan | `test_telescope_deploy_ci.py::TestBidirectionalImportFence::test_src_py_files_have_zero_service_imports` |
| CI script green + catches service→src | `test_telescope_deploy_ci.py::TestBidirectionalImportFence` (script exit 0 + probe) |
| Workflow wires script | `test_telescope_deploy_ci.py::…::test_workflow_invokes_fence_script` |

**AST-1727** narrowed run:

```bash
./scripts/testing/run_component_tests.sh tests/component/service/test_telescope_deploy_ci.py -q
```

**Pass criterion:** pytest green on that path — not zero-arg harness / branch-lock gate.

**Out of scope:** live Railway dashboard wiring (operator), statute amendment, Surfer / Phase 2 autoscaler, service app / platform client (AST-1725 / AST-1726).

---

### AST-1728 · AST-1721 (qa-fix bug-repro — scrape_meta)

**Board REVISE:** additive `scrape_meta` on `/telescope` + `/telescope/html`.

| Area | Component tests |
| --- | --- |
| scrape_meta keys on text/html POST | `test_telescope_app.py::TestAst1728ScrapeMeta` (**bug-repro**, red pre-fix) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_app.py::TestAst1728ScrapeMeta -q
```

---

### AST-1729 · AST-1721 (qa-fix bug-repro — html default full document)

**Board REVISE:** omitted `selector` on `capture_html` / `POST /telescope/html` must use `documentElement` (same as `"page"`), not body.

| Area | Component tests |
| --- | --- |
| None/`""` → documentElement path | `test_telescope_capture.py::test_capture_html_omitted_selector_uses_document_element` (**bug-repro**, red pre-fix) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_capture_html_omitted_selector_uses_document_element -q
```

---

### AST-1731 · AST-1721 (qa-fix bug-repro — bare class + multi-match html)

**Board REVISE:** bare class token (e.g. `points-container` → `.class` retry) + multi-match `html` list asserts; AST-1725 only covers `#main` / `page` / `body`.

| Area | Component tests |
| --- | --- |
| Bare class → `.class` retry on html | `test_telescope_capture.py::test_capture_html_bare_class_token_retries_as_class` (**bug-repro**, red pre-fix) |
| Multi-match css → `list[str]` html | `test_telescope_capture.py::test_capture_html_multi_match_returns_list` (**bug-repro**, red pre-fix) |
| Same bare→class retry on text | `test_telescope_capture.py::test_capture_text_bare_class_token_retries_as_class` (**bug-repro**, red pre-fix) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_capture_html_bare_class_token_retries_as_class \
  tests/component/service/test_telescope_capture.py::test_capture_html_multi_match_returns_list \
  tests/component/service/test_telescope_capture.py::test_capture_text_bare_class_token_retries_as_class -q
```

---

### AST-1732 · AST-1721 (qa-fix bug-repro — scoped capture_links)

**Board REVISE:** `capture_links(page, selector)` scopes http(s) anchors under match roots; multi-match dedupe by href; `POST /telescope` forwards `body.selector`.

| Area | Component tests |
| --- | --- |
| Scoped evaluate (not whole-page `a[href]`) | `test_telescope_capture.py::test_ast1732_capture_links_scoped_to_selector` (**bug-repro**) |
| Multi-match href merge → `text[]` | `test_telescope_capture.py::test_ast1732_capture_links_multi_match_dedupes_by_href` (rewritten AST-1747) |
| App passes selector | `test_telescope_app.py::TestTelescopeRoutes::test_ast1732_post_telescope_passes_selector_to_capture_links` (**bug-repro**) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_ast1732_capture_links_scoped_to_selector \
  tests/component/service/test_telescope_capture.py::test_ast1732_capture_links_multi_match_dedupes_by_href \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1732_post_telescope_passes_selector_to_capture_links -q
```

---

### AST-1733 · AST-1721 (qa-fix bug-repro — selector text strips style)

**Board REVISE:** `capture_text` CSS selector path (e.g. `"head"`) must clone-and-strip `style`/`script`/`noscript` like the page/body path; existing body-path test does not cover this.

| Area | Component tests |
| --- | --- |
| Selector path clone + style/script/noscript strip | `test_telescope_capture.py::test_ast1733_capture_text_selector_strips_style_script_noscript` (**bug-repro**) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_ast1733_capture_text_selector_strips_style_script_noscript -q
```

---

### AST-1735 · AST-1721 (qa-fix bug-repro — head/body scoped links)

**Board REVISE:** `capture_links("head"|"body")` must be element-scoped (`body` not whole-page alias); omit/`"page"` stay document-wide. AST-1732 only covers class selectors.

| Area | Component tests |
| --- | --- |
| `"body"` scoped (not whole-page) | `test_telescope_capture.py::test_ast1735_capture_links_body_is_scoped_not_whole_page` (**bug-repro**) |
| `"head"` scoped; omit/`page` whole-doc | `test_telescope_capture.py::test_ast1735_capture_links_head_scoped_and_page_stays_whole_document` (**bug-repro**) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_ast1735_capture_links_body_is_scoped_not_whole_page \
  tests/component/service/test_telescope_capture.py::test_ast1735_capture_links_head_scoped_and_page_stays_whole_document -q
```

---

### AST-1736 · AST-1721 (qa-fix bug-repro — tag/class_name filter)

**Board REVISE:** explicit `class_name` (e.g. `shaders`) → resolved `.class` html; `selector`+`class_name` → 400; `capture_links` bare→class retry. AST-1731 only covers bare `selector` heuristic.

| Area | Component tests |
| --- | --- |
| `class_name` → `.shaders` into capture_html | `test_telescope_app.py::TestTelescopeRoutes::test_ast1736_html_class_name_resolves_to_dot_class` (**bug-repro**) |
| Ambiguous XOR superseded by AST-1744 | see `test_ast1744_bare_primary_plus_class_name_resolves_to_tag_class` |
| Links bare-class retry | `test_telescope_capture.py::test_ast1736_capture_links_bare_class_retries_as_class` (**bug-repro**) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1736_html_class_name_resolves_to_dot_class \
  tests/component/service/test_telescope_capture.py::test_ast1736_capture_links_bare_class_retries_as_class -q
```

---

### AST-1746 · AST-1721 (qa-fix bug-repro — optional id filter)

**Board REVISE:** optional `id` (e.g. `hero` → `#hero`) into capture; `selector`+`id` → 400; Admin Id control. AST-1736 only covers `class_name`.

| Area | Component tests |
| --- | --- |
| `id` → `#hero` into capture_html | `test_telescope_app.py::TestTelescopeRoutes::test_ast1746_html_id_resolves_to_hash_id` (**bug-repro**) |
| Ambiguous selector+id → 400 | `test_telescope_app.py::TestTelescopeRoutes::test_ast1746_selector_plus_id_returns_400` (**bug-repro**) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1746_html_id_resolves_to_hash_id \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1746_selector_plus_id_returns_400 -q
```

---

### AST-1744 · AST-1721 (qa-fix bug-repro — unify tag/selector; class secondary)

**Board REVISE:** rewrite AST-1736 XOR (`selector`+`class_name`→400); bare primary + class → `tag.class`; Admin single Tag primary (no Selector) with Class always enabled.

| Area | Component tests |
| --- | --- |
| Bare selector + class → `div.logo` | `test_telescope_app.py::TestTelescopeRoutes::test_ast1744_bare_primary_plus_class_name_resolves_to_tag_class` (**bug-repro**) |
| Tag + class → `div.logo` | `test_telescope_app.py::TestTelescopeRoutes::test_ast1744_tag_plus_class_name_resolves_to_tag_class` |
| Complex CSS + class still 400 | `test_telescope_app.py::TestTelescopeRoutes::test_ast1744_complex_selector_plus_class_name_still_400` |
| Admin single primary | `test_AdminTelescope.test.tsx` — **`AST-1744: single Tag primary + Class always enabled; no Selector slot`** (**bug-repro**) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1744_bare_primary_plus_class_name_resolves_to_tag_class \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1744_tag_plus_class_name_resolves_to_tag_class \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1744_complex_selector_plus_class_name_still_400 -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTelescope.test.tsx -t 'AST-1744'
```

---

### AST-1747 · AST-1721 (qa-fix bug-repro — links href dedupe with text[])

**Board REVISE:** href-unique `links[]` with `text` as deduped `list[str]` (e.g. `["Software Engineer","View role"]`); rewrite AST-1732 string-text + JS `seen`/first-wins asserts.

| Area | Component tests |
| --- | --- |
| Fixture href merge + text[] | `test_telescope_capture.py::test_ast1747_capture_links_dedupes_href_with_text_array` (**bug-repro**) |
| Single-label → one-element array | `test_telescope_capture.py::test_capture_links_filters_http` / `test_ast1732_capture_links_scoped_to_selector` |
| Scoped multi-label merge | `test_telescope_capture.py::test_ast1732_capture_links_multi_match_dedupes_by_href` |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_ast1747_capture_links_dedupes_href_with_text_array \
  tests/component/service/test_telescope_capture.py::test_capture_links_filters_http \
  tests/component/service/test_telescope_capture.py::test_ast1732_capture_links_multi_match_dedupes_by_href -q
```
