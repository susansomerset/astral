# AST-654 — Core bootstrap runtime startup (`core/bootstrap`: runtime startup orchestration from `ui/server.py`)

- **Linear (this ticket):** [AST-654](https://linear.app/astralcareermatch/issue/AST-654/core-bootstrap-runtime-startup-corebootstrap-runtime-startup)
- **Parent:** [AST-383](https://linear.app/astralcareermatch/issue/AST-383/corebootstrap-runtime-startup-orchestration-from-uiserverpy)
- **Publish ref:** `origin/sub/AST-383/AST-654-core-bootstrap-runtime-startup` (child of AST-383; not Linear `gitBranchName`)
- **Reference plan (parent epic):** `docs/features/foundation/ast-383-corebootstrap-runtime-startup-orchestration-from-uiserverpy.md`

## Summary

Move **process startup** out of `src/ui/server.py` into a new **`src/core/bootstrap.py`** module. Today `server.py` imports `src.data.database` for `sync_agent_tasks`, imports `start_scheduler` from dispatcher, and calls `validate_llm_provider_environment()` inline after blueprint registration. Replace that block with a **single** core call — **`bootstrap_runtime()`** — that runs, in order: **(1) fail-fast runtime validation**, **(2) `database.sync_agent_tasks(get_task_keys())`**, **(3) `start_scheduler()`**. The UI entrypoint then imports **core + utils only** for bootstrap (matching the existing module docstring on `server.py`).

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| Admin table export / import / preview (repo-pinned snapshots) | [AST-381](https://linear.app/astralcareermatch/issue/AST-381/pushing-database-content-to-github) — must **not** be invoked from bootstrap |
| Refactor `ui/api/*` to stop importing `data` directly | [AST-321](https://linear.app/astralcareermatch/issue/AST-321/refactor-api-layer-to-use-core-components) |
| Residual B2 grep / integration verification after this lands | [AST-385](https://linear.app/astralcareermatch/issue/AST-385/ast-382-resolve-vector-b2-layer-compliance) |
| `docs/ASTRAL_CODE_RULES.md` §3.5 startup bullet update | Optional — only if **validate-plan** explicitly requests in same PR |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/bootstrap.py` | **New:** `_validate_runtime_coupling()` + public `bootstrap_runtime()` with ordered validation → sync → scheduler | core |
| `src/ui/server.py` | Remove `from src.data import database`, `get_task_keys`, `start_scheduler` startup block; call `bootstrap_runtime()` once after blueprint registration | ui |

**No changes:** `src/data/database.py` (`sync_agent_tasks` stays as-is; core calls it). No test or bible edits on this ticket (Betty owns `merge-tests`).

## Stage 1: Add `src/core/bootstrap.py`

**Done when:** `bootstrap_runtime()` exists with the full ordered pipeline; `python3 -m py_compile src/core/bootstrap.py` passes; module docstring documents the three-step contract and that **AST-381 export/import paths are not called here**.

1. Create `src/core/bootstrap.py` with module docstring stating:
   - Called once from `src/ui/server.py` after Flask blueprints register.
   - Order: `_validate_runtime_coupling()` → `database.sync_agent_tasks(get_task_keys())` → `start_scheduler()`.
   - Does **not** run AST-381 admin snapshot export/import/preview.

2. Add imports at top of `bootstrap.py` (core may import data, utils, other core):

```python
from src.data import database
from src.core.dispatcher import start_scheduler
from src.utils.config import (
    DISPATCH_SCHEDULABLE_TASK_KEYS,
    TASK_CONFIG,
    get_task_keys,
    validate_llm_provider_environment,
)
```

3. Implement `_validate_runtime_coupling() -> None` that **raises `RuntimeError`** with a clear message on failure (no logging-only failures):

   a. Call `validate_llm_provider_environment()` — preserves today's fail-fast LLM secret check (currently in `server.py` line 59) before any DB work.

   b. `task_keys = get_task_keys()`. If `not task_keys`, raise `RuntimeError("bootstrap: TASK_CONFIG defines no task keys")`.

   c. For each `key` in `task_keys`, if `key not in TASK_CONFIG`, raise `RuntimeError(f"bootstrap: task key {key!r} missing from TASK_CONFIG")` (defensive; documents AST-654 coupling intent in code).

   d. For each `key` in `DISPATCH_SCHEDULABLE_TASK_KEYS`, if `key not in TASK_CONFIG`, raise `RuntimeError(f"bootstrap: dispatch schedulable key {key!r} missing from TASK_CONFIG")` — **dispatch contract alignment** per acceptance criteria.

4. Implement public `bootstrap_runtime() -> None`:

```python
def bootstrap_runtime() -> None:
    _validate_runtime_coupling()
    database.sync_agent_tasks(get_task_keys())
    start_scheduler()
```

5. Set `__all__ = ["bootstrap_runtime"]`.

⚠️ **Decision:** Keep `validate_llm_provider_environment()` inside `_validate_runtime_coupling()` (not in `server.py`) so **all** pre-sync fail-fast checks live in one core function; `server.py` only calls `bootstrap_runtime()`.

⚠️ **Decision:** Callable name is **`bootstrap_runtime`** (matches Linear AST-654 description; not `bootstrap_app`).

## Stage 2: Rewire `src/ui/server.py`

**Done when:** After blueprint registration, `server.py` calls `bootstrap_runtime()` only; `rg "from src.data|import database" src/ui/server.py` returns zero matches; `python3 -m py_compile src/ui/server.py` passes.

1. **Delete** lines 54–67 (the block from `# --- Sync agent_task rows at startup ---` through `start_scheduler()`), including:
   - `from src.utils.config import get_task_keys, validate_llm_provider_environment`
   - `validate_llm_provider_environment()`
   - `from src.data import database`
   - `database.sync_agent_tasks(get_task_keys())`
   - `from src.core.dispatcher import start_scheduler`
   - `start_scheduler()`

2. **Insert** immediately after the last `app.register_blueprint(...)` (after `resume_html_bp`, before `# --- Serve React app ---`):

```python
# --- Runtime bootstrap (validation → agent_task sync → scheduler) ---
from src.core.bootstrap import bootstrap_runtime  # noqa: E402

bootstrap_runtime()
```

3. Do **not** change blueprint registration order, `wire_stytch_token_authenticator()`, static routes, or `if __name__ == "__main__"` block.

4. Do **not** add any new imports from `src.data` or `src.core.dispatcher` elsewhere in `server.py`.

## Stage 3: Verification

**Done when:** Layer grep is clean; local import smoke passes; Flask debug reloader caveat is recorded in the plan comment on Linear (not a code change).

1. From repo root:

```bash
rg "from src.data|import database" src/ui/server.py
```

Expected: **no matches**.

2. Compile check:

```bash
python3 -m py_compile src/core/bootstrap.py src/ui/server.py
```

3. Optional manual smoke (when env has DB + LLM secrets configured):

```bash
cd src/ui && python3 -c "import server; print('import ok')"
```

Expect process import to complete without `ImportError` / `RuntimeError`. Do **not** leave a running server in CI; this is local dev only.

4. **Flask debug reloader note (document only):** `server.py` runs module-level code on import. With `app.run(debug=True)` (line 82), Werkzeug may execute startup **twice** (parent + reloader child). `start_scheduler()` is already idempotent (`dispatcher.start_scheduler` returns early if tick thread is alive). `sync_agent_tasks` only inserts missing keys — safe on second pass. No code change required; mention in build completion if Susan debugs double-start logs.

## Execution contract (for build-child)

- Execute stages **in order**; one **`code(AST-654)`** commit per stage on **`epic worktree`**, publish each to **`origin/sub/AST-383/AST-654-core-bootstrap-runtime-startup`** before the next stage.
- Do **not** add files beyond the plan table.
- Do **not** invoke AST-381 export/import/preview from bootstrap.
- Blocking ambiguity → comment on **AST-383** parent with 🛑 template from **plan-child** §6.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Adds a new core module and changes Flask process startup ordering for the entire web server.

**Conf:** `Medium` — Pattern is straightforward (move existing calls behind core facade); validation rules are minimal but touch dispatch + TASK_CONFIG contract.

**Risk:** `HIGH` — Wrong ordering or swallowed startup failure leaves scheduler unsynced or tasks missing; mitigated by fail-fast `RuntimeError` in validation and preserving existing `sync_agent_tasks` / idempotent `start_scheduler` behavior.

## Plan vs ASTRAL_CODE_RULES

| Rule | Compliance |
|------|------------|
| §3.3 ui imports | `server.py` ends with **ui → core** for bootstrap; **no** `src.data` in ui after Stage 2 |
| §3.3 core imports | `bootstrap.py` imports **data**, **core.dispatcher**, **utils** — allowed |
| §2.1 config | Validation reads `TASK_CONFIG`, `DISPATCH_SCHEDULABLE_TASK_KEYS`, `get_task_keys()` from config only — no hardcoded task lists in bootstrap |
| §3.5 scheduler | `start_scheduler()` moves from server to bootstrap; dispatcher behavior unchanged |
| DRY §1.3 | No duplicate sync/scheduler calls in server — single `bootstrap_runtime()` entry |

No conflicts requiring `conf-!!-NONE`.

## Review (build stub)

**Built:** `origin/sub/AST-383/AST-654-core-bootstrap-runtime-startup` @ `60433538`.

**Stages delivered:**
- Stage 1: `src/core/bootstrap.py` — `3f742853`.
- Stage 2: `src/ui/server.py` calls `bootstrap_runtime()` only — `60433538`.
- Stage 3: `rg` clean (no `src.data` in `server.py`); `py_compile` pass. Flask debug reloader may double-run module-level bootstrap; `start_scheduler` is idempotent.

**Betty:** manifest at **Code Complete** — layer grep on `server.py`, bootstrap import smoke if env configured.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-383/AST-654-core-bootstrap-runtime-startup` @ `9088ec20`

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | `bootstrap_runtime()` runs validation → `sync_agent_tasks(get_task_keys())` → `start_scheduler()` in order; AST-381 paths not invoked |
| B2 layer | `server.py` has zero `src.data` imports; bootstrap lives in core with allowed data/core/utils imports |
| Fail-fast | `_validate_runtime_coupling()` raises `RuntimeError` on LLM env, empty task keys, and coupling gaps — no swallowed startup failures |
| Tests | `test_bootstrap.py` covers validation branches and call ordering; `conftest.server_client` stubs `bootstrap_runtime` before server reload |
| Dispatch coupling | Validation uses `resolve_dispatch_task_config_key` (not naive `key in TASK_CONFIG`) — matches live dispatch-row → agent-key mapping |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | No fix-now or discuss items |

### Recommended actions

| Action | Owner |
|--------|-------|
| Cherry-pick or merge sub tip; proceed to `resolve-child` if no open threads | Hedy |
| Optional: update `ASTRAL_CODE_RULES.md` §3.2 server.py bullet (scheduler now in `core/bootstrap`) | AST-385 or follow-up |

**Verdict:** Clean — approve for merge integration.

## Resolution (Hedy)

**Resolved:** 2026-06-15 · publish ref @ resolve tip (see git log)

Radia **Review Posted** @ `f5153328`: **fix-now** and **discuss** empty; advisory dispatch-key validation already addressed in `9088ec20` (product fix during test-child). No additional product changes required.

**Shipped:**
- `src/core/bootstrap.py` — `bootstrap_runtime()` pipeline (validation → sync → scheduler); dispatch keys validated via `resolve_dispatch_task_config_key` + `dispatch_task_admin_defaults` fallback.
- `src/ui/server.py` — single `bootstrap_runtime()` call; zero `src.data` imports.

**Deferred:** `ASTRAL_CODE_RULES.md` §3.2 scheduler bullet → AST-385 per Radia advisory.
