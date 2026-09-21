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

Print Resume / Cover open `/candidate/resume|<job_id>` and `/candidate/cover/<job_id>`. Vite must proxy **print HTML prefixes** (`/candidate/resume`, `/candidate/cover`) → Flask — not the whole `/candidate` SPA section. Flask SPA catch-all **404 JSON** only for unmatched **print-shaped** paths; candidate SPA routes (`/candidate/backstory`, …) get `index.html`. Narrowed by **AST-1435**. HTML blueprints + pin resolve remain AST-605 / AST-1100.

| Area | Source | Component tests |
| --- | --- | --- |
| SPA catch-all guard | `src/ui/server.py` `serve_react` | **`TestAst1117CandidateSpaGuard`** (rewritten AST-1435) |
| Vite print-HTML proxy | `src/ui/frontend/vite.config.ts` | **`TestAst1117ViteCandidateProxy`** (rewritten AST-1435) |

**Existing (bible-backed, not re-authored):** `TestResumeHtmlRoutes` / `TestAst581CoverRoute` (`docs/test-bible/ui/api/api_resume_html.md`); JAR Print `window.open('/candidate/…')` + pin visibility (`docs/test-bible/frontend/lib.md` AST-605 / AST-1100).

**Broken / obsolete:** blanket `/candidate` 404 + Vite `'/candidate'` proxy assertions — see **AST-1435**.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/test_server.py::TestAst1117CandidateSpaGuard \
  tests/component/ui/test_server.py::TestAst1117ViteCandidateProxy \
  tests/component/ui/api/test_api_resume_html.py::TestResumeHtmlRoutes \
  tests/component/ui/api/test_api_resume_html.py::TestAst581CoverRoute \
  -q
```

### AST-1435 · AST-1424

**Parent:** [AST-1424](https://linear.app/astralcareermatch/issue/AST-1424/refresh-from-a-deeplink-on-staging-i-get-an-error). **Publish:** `origin/sub/AST-1424/AST-1435-test-gap-candidate-spa-guard`. Product fix: **AST-1433**.

Rewrite AST-1117 blanket `/candidate` 404 + Vite proxy. Repro: document GET `/candidate/backstory` → 200 `index.html` (red on pre-fix `serve_react`; green after AST-1433 narrows the guard to print prefixes). Unmatched `/candidate/resume` and `/candidate/cover` (no blueprint match) still JSON 404.

| Area | Source | Component tests |
| --- | --- | --- |
| [bug-repro] SPA deeplink GET | `src/ui/server.py` `serve_react` | **`TestAst1117CandidateSpaGuard::test_candidate_backstory_serves_index`** |
| SPA `/candidate` fallback | same | **`test_candidate_prefix_spa_routes_serve_index`**, **`test_candidate_exact_path_serves_index`** |
| Print-prefix unmatched 404 | same | **`test_unmatched_print_resume_prefix_returns_404_json`**, **`test_unmatched_print_cover_prefix_returns_404_json`** |
| Vite print-only proxy | `src/ui/frontend/vite.config.ts` | **`TestAst1117ViteCandidateProxy::test_vite_config_proxies_print_html_not_candidate_spa`** |

**Broken / obsolete:** `test_candidate_prefix_returns_404_json_not_spa`, `test_candidate_exact_path_returns_404_json`, `test_vite_config_proxies_candidate_to_flask`.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/test_server.py::TestAst1117CandidateSpaGuard \
  tests/component/ui/test_server.py::TestAst1117ViteCandidateProxy \
  -q
```

### AST-1236 · AST-1174

**Parent:** [AST-1174 — Human-paced fan-out over the batch worklist](https://linear.app/astralcareermatch/issue/AST-1174/human-paced-fan-out-over-the-batch-worklist). **Publish:** `origin/sub/AST-1174/AST-1236-pacing-config`.

Registers `surfer_bp` (`GET /api/surfer/pacing_config`). Route behavior: **`docs/test-bible/ui/api/api_surfer.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Blueprint registration | `src/ui/server.py` | import coverage via **`server_client`** / **`surfer_client`** |

**Broken / obsolete:** none.

**Integration:** none.


### AST-1235 · AST-1173

**Parent:** [AST-1173 — Consent — install disclosure, affirmative opt-in, and off-switch](https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch). **Publish:** `origin/sub/AST-1173/AST-1235-versioned-consent-record-and-api`.

Registers `surfer_bp` (`GET`/`PUT /api/candidates/<id>/surfer/consent`). Route behavior: **`docs/test-bible/ui/api/api_surfer.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Blueprint registration | `src/ui/server.py` | import coverage via **`surfer_consent_client`** |

**Broken / obsolete:** none.

**Integration:** none.
