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

**test-child note:** Live **`DISPATCH_SCHEDULABLE_TASK_KEYS`** are dispatch-row keys (e.g. **`consult_do`**, **`prefilter`**) resolved via **`resolve_dispatch_task_config_key()`** into **`TASK_CONFIG`** agent keys — raw membership in **`TASK_CONFIG`** fails server import until **`bootstrap.py`** aligns validation with that helper.
