# Server

**Test module:** `tests/component/ui/test_server.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/server.py` | `tests/component/ui/test_server.py` | yes |

---

### AST-654 · AST-383

**AST-383 (parent epic):** Move Flask process startup (LLM env validation → `sync_agent_tasks` → `start_scheduler`) from **`src/ui/server.py`** into **`src/core/bootstrap.py`**. UI calls **`bootstrap_runtime()`** once after blueprint registration — no direct **`src.data`** import in **`server.py`**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-654** | Ordered **`bootstrap_runtime()`** pipeline; fail-fast **`_validate_runtime_coupling()`** before DB sync | `src/core/bootstrap.py`, `src/ui/server.py` | **`tests/component/core/test_bootstrap.py`** (full file); **`tests/component/ui/test_server.py::TestServeReact`** ( **`server_client`** stubs **`bootstrap_runtime`** ); **`tests/component/ui/conftest.py`** **`server_client`** fixture |

**AST-654** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_bootstrap.py \
  tests/component/ui/test_server.py
```

**test-child note:** Live **`DISPATCH_SCHEDULABLE_TASK_KEYS`** use **`grade_*`** dispatch-row keys (e.g. **`grade_do`**, **`prefilter`**) — same strings as **`TASK_CONFIG`** after **AST-747**; **`resolve_dispatch_task_config_key()`** trims only.

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
