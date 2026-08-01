# Server

**Test module:** `tests/component/ui/test_server.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/server.py` | `tests/component/ui/test_server.py` | yes |

---

### AST-654 · AST-383

**AST-383 (parent epic):** Move Flask process startup (LLM env validation → repo admin JSON upsert (**AST-782**) → schema ensure (**AST-843**) → `sync_agent_tasks` → `start_scheduler`) from **`src/ui/server.py`** into **`src/core/bootstrap.py`**. UI calls **`bootstrap_runtime()`** once after blueprint registration — no direct **`src.data`** import in **`server.py`**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-654** | Ordered **`bootstrap_runtime()`** pipeline; fail-fast **`_validate_runtime_coupling()`** before DB sync | `src/core/bootstrap.py`, `src/ui/server.py` | **`tests/component/core/test_bootstrap.py`** (full file); **`tests/component/ui/test_server.py::TestServeReact`** ( **`server_client`** stubs **`bootstrap_runtime`** ); **`tests/component/ui/conftest.py`** **`server_client`** fixture |

**AST-654** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_bootstrap.py \
  tests/component/ui/test_server.py
```

**test-child note:** After **AST-960**, catalog membership is **`TASK_CONFIG`** only (no **`DISPATCH_SCHEDULABLE_TASK_KEYS`**). Dispatch-row keys such as **`grade_do`** share strings with **`TASK_CONFIG`** after **AST-747**; gazer/roster gap keys (`fetch_jd`, `prefilter`, …) are not forced into the admin catalog. **`resolve_dispatch_task_config_key()`** trims only.

### AST-758 · AST-744

Local dev: Flask `:5001` serves gitignored **`frontend/dist/`**; **`git pull`** does not rebuild. Debug **`python server.py`** warns when dist missing or older than **`frontend/src/**/*.{ts,tsx}`** (import-time silent for gunicorn/Railway).

| Area | Source | Component tests |
| --- | --- | --- |
| Stale-dist stderr warning | `src/ui/server.py` (`_warn_stale_frontend_dist`) | `tests/component/ui/test_server.py::TestWarnStaleFrontendDist` |

**AST-758** narrowed run (pair with **`docs/test-bible/dev/launch_frontend_deps.md`**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/test_server.py::TestWarnStaleFrontendDist \
  tests/component/dev/test_launch_frontend_deps.py::TestLaunchFrontendBuild \
  -q
```

**Manual UAT:** Susan Stage 4 in plan — `:5001` after pull without manual rebuild shows AST-746 Scheduled Actions layout.

---

### AST-779 · AST-770

**API error enrichment:** **`api_errors.py`** + **`server.py`** `/api/*` uncaught exception handler returns JSON **`error`**, **`exception_type`**, **`traceback`** on 500; non-`/api/` routes re-raise (not swallowed).

| Area | Source | Component tests |
| --- | --- | --- |
| Shared error JSON helpers + handler contract | `src/ui/api_errors.py`, `src/ui/server.py` (`_api_uncaught_exception`) | `tests/component/ui/api/test_api_errors.py` |

**AST-779** narrowed run:

```bash
./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_errors.py -q
```


---

### AST-1117 · AST-1091 (UAT)

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1117-print-html-blobs`.

Print Resume / Cover open `/candidate/resume|<job_id>` and `/candidate/cover/<job_id>`. Vite must proxy `/candidate` → Flask; Flask SPA catch-all must **404 JSON** for unmatched `candidate/*` instead of serving `index.html` (SPA `*` → recommended). HTML blueprints + pin resolve remain AST-605 / AST-1100.

| Area | Source | Component tests |
| --- | --- | --- |
| SPA catch-all guard | `src/ui/server.py` `serve_react` | **`TestAst1117CandidateSpaGuard`** |
| Vite `/candidate` proxy | `src/ui/frontend/vite.config.ts` | **`TestAst1117ViteCandidateProxy`** |

**Existing (bible-backed, not re-authored):** `TestResumeHtmlRoutes` / `TestAst581CoverRoute` (`docs/test-bible/ui/api/api_resume_html.md`); JAR Print `window.open('/candidate/…')` + pin visibility (`docs/test-bible/frontend/lib.md` AST-605 / AST-1100).

**Broken / obsolete:** none.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/test_server.py::TestAst1117CandidateSpaGuard \
  tests/component/ui/test_server.py::TestAst1117ViteCandidateProxy \
  tests/component/ui/api/test_api_resume_html.py::TestResumeHtmlRoutes \
  tests/component/ui/api/test_api_resume_html.py::TestAst581CoverRoute \
  -q
```
