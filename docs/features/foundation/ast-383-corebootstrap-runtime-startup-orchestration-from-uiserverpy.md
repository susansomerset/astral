# Plan: AST-383 — core/bootstrap: runtime startup orchestration from `ui/server.py`

**Linear:** https://linear.app/astralcareermatch/issue/AST-383/corebootstrap-runtime-startup-orchestration-from-uiserverpy  
**Feature branch:** `betty/ast-383-corebootstrap-runtime-startup-orchestration-from-uiserverpy`

## Summary

Move **process startup** out of `src/ui/server.py`: today it imports `src.data.database` for `sync_agent_tasks` and imports `start_scheduler` from dispatcher. Replace with a **single** core entrypoint (file `src/core/bootstrap.py`, callable `bootstrap_runtime()` — exact name in code may be `bootstrap_runtime` or `bootstrap_app`; pick one and use it consistently) invoked from `server.py` **after** blueprints register and **before** serving traffic, so the UI package imports **core + utils only** at bootstrap (matching server docstring intent).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/bootstrap.py` | **New:** `bootstrap_runtime()` runs ordered steps: (1) validate config/DB coupling TBD, (2) `sync_agent_tasks(get_task_keys())` via data from core, (3) `start_scheduler()` from dispatcher | core |
| `src/ui/server.py` | Remove `from src.data import database` block and inline `sync_agent_tasks`; call `from src.core.bootstrap import bootstrap_runtime` then `bootstrap_runtime()` once; keep blueprint registration order unchanged | ui |
| `src/data/database.py` | No public API change required if `sync_agent_tasks` stays on database; core calls existing function | data |
| `docs/ASTRAL_CODE_RULES.md` | Optional short §3.1/startup note: “Flask entry calls `core.bootstrap` only” — only if Susan wants doc parity in same PR | docs |

**Explicitly out of scope:** [AST-381](https://linear.app/astralcareermatch/issue/AST-381/pushing-database-content-to-github) export/import/preview — must not be invoked from bootstrap.

## Stage 1: `bootstrap_runtime` skeleton

**Done when:** `bootstrap_runtime()` exists, is a no-op or logging-only stub, and `server.py` can call it without importing `database`.

1. Add `src/core/bootstrap.py` with module docstring listing ordering contract vs scheduler.
2. Temporarily move **only** `sync_agent_tasks` + `get_task_keys` call into `bootstrap_runtime` using **core-internal** import of `database` (core may import data per rules).
3. Replace lines 44–47 in `src/ui/server.py` with `bootstrap_runtime()`.

## Stage 2: Validation hooks (coupling checks)

**Done when:** Before `sync_agent_tasks`, bootstrap asserts invariant Susan selects (minimum: `get_task_keys()` non-empty and each key exists in `TASK_CONFIG` / dispatch contract — **concrete asserts listed in code comments** referencing ticket).

1. Add private `_validate_runtime_coupling()` in `bootstrap.py` raising `RuntimeError` with clear message on failure (fail-fast at startup per secrets/config rules spirit).
2. Order: `_validate_runtime_coupling()` → `database.sync_agent_tasks(...)` → `start_scheduler()`.

## Stage 3: Scheduler ownership

**Done when:** `server.py` does not import `start_scheduler` directly; `bootstrap_runtime` is the only caller.

1. Move `from src.core.dispatcher import start_scheduler` and call into `bootstrap_runtime` tail.
2. Confirm single scheduler start on reload (Flask debug reloader: document double-start caveat if applicable).

## Stage 4: Verification

**Done when:** `rg "from src.data|import database" src/ui/server.py` returns zero matches; app starts and one dispatch cycle can tick (manual or existing script).

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — New core module and changes Flask entrypoint ordering (touches whole process startup).

**Conf:** `Medium` — Validation rules are “TBD” in Linear; planner locked minimal fail-fast; Susan may extend asserts.

**Risk:** `HIGH` — Bad ordering or swallowed exception leaves scheduler unsynced or tasks missing; mitigated by fail-fast validation and clear logs.

## Plan vs ASTRAL_CODE_RULES

§3.3: `server.py` ends up **ui** importing **core** only for bootstrap; `database` stays behind core. No automatic **AST-381** paths.
