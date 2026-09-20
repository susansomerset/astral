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
