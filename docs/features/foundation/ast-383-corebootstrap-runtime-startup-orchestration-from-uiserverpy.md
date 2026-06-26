<!-- linear-archive: AST-383 archived 2026-06-23 -->

## Linear archive (AST-383)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-383/corebootstrap-runtime-startup-orchestration-from-uiserverpy  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Goal

Centralize **process startup** that today lives partly in `src/ui/server.py` (direct `src.data` import for `sync_agent_tasks`) so the UI entrypoint calls **core** only, and coupling checks stay in one obvious place.

## Proposed shape

* Add `src/core/bootstrap.py` (name TBD) exposing something like `bootstrap_runtime()` (exact API TBD).
* `src/ui/server.py` calls that once after Flask blueprints are registered and **before** `start_scheduler()` (or the bootstrap module owns the ordering internally).

## Responsibilities (this ticket)

* **Validate** task / config / DB coupling that must hold before the app runs dispatch and agent work (exact assertions TBD—e.g. task keys vs `agent_task` rows, schema expectations).
* **Ensure** required DB rows for runtime (today: `database.sync_agent_tasks(get_task_keys())` or equivalent moved behind core).
* **Start** in-process scheduler via existing `src/core/dispatcher.py` entrypoints.

## Explicitly out of scope

* **Admin table export / import** and repo-pinned snapshot workflows are [AST-381](https://linear.app/astralcareermatch/issue/AST-381/pushing-database-content-to-github) only. Those flows must **not** run automatically from this bootstrap path; keep the tickets discrete.

## Related

* [AST-381](https://linear.app/astralcareermatch/issue/AST-381/pushing-database-content-to-github) — repo snapshot + UI-driven export / preview / import of admin DB content.
* [AST-321](https://linear.app/astralcareermatch/issue/AST-321/refactor-api-layer-to-use-core-components) — refactor `ui/api/*` to stop importing `data` directly (orthogonal; bootstrap is server entry, not blueprints).

### Comments

#### chuckles — 2026-06-15T00:48:40.575Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-383 (parent) | ftr/ast-383-corebootstrap-runtime-startup-orchestration-from-uiserverpy |
| AST-654 | sub/AST-383/AST-654-core-bootstrap-runtime-startup |

**Epic worktree:** `astral-AST-383/` — one active sub checked out at a time.

**Parent:** AST-383

— Chuckles

#### susan — 2026-06-15T00:08:06.613Z
You have all the information you need to execute this ticket.

#### chuckles — 2026-06-14T22:15:05.364Z
[check-linear] Still valid as **Foundation hygiene**, not shipped: `src/ui/server.py` still imports `src.data.database` for `sync_agent_tasks` and calls `start_scheduler` directly (lines 55–67 cite AST-383 as pending). No `src/core/bootstrap.py` on `dev`. The 2025-05-16 “already on origin/dev” note was wrong.

**Your call:** cancel/archive if layer cleanup isn’t worth the churn right now; or move to **Todo** when you want a small Foundation pass (plan + Betty branch exist). Nothing downstream is blocked today.

— Chuckles

#### susan — 2026-06-14T22:13:37.747Z
@chuckles  Does this still need doing?  It's pretty old, so I wanted to make sure we still need it.

#### chuckles — 2026-05-16T21:30:04.247Z
## Plan Review — Chuckles

**Verdict: APPROVED**

Plan is faithful to the definition. No findings. ASTRAL_CODE_RULES compliance confirmed. Self-assessment is honest (conf-Medium, risk-HIGH — bootstrap ordering and fail-fast validation documented).

**Note:** Implementation already on `origin/dev` ([retroactive-pipeline] C2).

— Chuckles

#### betty — 2026-05-08T22:08:25.327Z
**Plan posted** — `docs/features/foundation/ast-383-corebootstrap-runtime-startup-orchestration-from-uiserverpy.md`

GitHub: https://github.com/susansomerset/astral/blob/betty/ast-383-corebootstrap-runtime-startup-orchestration-from-uiserverpy/docs/features/foundation/ast-383-corebootstrap-runtime-startup-orchestration-from-uiserverpy.md

**Self-assessment**
- **Scope:** `MAJOR-CHANGE` — New `core/bootstrap.py` and Flask entry ordering for sync + scheduler.
- **Conf:** `Medium` — Startup validation rules are extendable; minimal fail-fast spelled in plan.
- **Risk:** `HIGH` — Ordering / silent failure risks unsynced tasks or duplicate scheduler; mitigated by explicit staged bootstrap and grep verification.

— Betty

---

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
