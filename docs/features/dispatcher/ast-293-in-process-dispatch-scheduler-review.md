# Code Review: AST-293 — In-Process Dispatch Scheduler

**Commit:** `e02980a`
**Branch:** `<agent>/ast-293-in-process-dispatch-scheduler`
**Reviewer:** Chuckles
**Date:** 2026-03-10

**Verdict: Approved with one required fix and two advisory items.**

**Resolution (post-review):**
- **Fix #1**: Added `RAILWAY_CONFIG` section to `config.py` with `workers: 1` and `timeout: 300`. Created `scripts/start_server.py` to build the gunicorn command from config. `railway.toml` now calls the script — no hardcoded gunicorn args or env-var configs.
- **Advisory #2**: Added comment in `dispatcher.py` explaining why batch runners call `database` directly.
- **Advisory #3**: Resolved by Fix #1 — worker count lives in `RAILWAY_CONFIG`, not a stray `dispatch_workers` key.

TypeScript compiles clean. Python imports resolve. Plan-to-implementation parity is complete.

---

## Required Fix

### 1. Gunicorn multi-worker = duplicate schedulers

This is the main one. `start_scheduler()` is called in `src/ui/server.py` at module load time. With `--workers ${ASTRAL_WORKERS:-2}`, gunicorn forks **two worker processes**, each with its own copy of the `dispatcher` module and its own scheduler thread. Result: two concurrent scheduler threads, both reading `get_due_tasks()`, both potentially dispatching the same tasks at the same time.

The batch-locking pattern (claim/process/release) protects against double-processing a single entity, so data integrity isn't at risk. But you'd be burning double the API calls and seeing confusing duplicate ledger entries.

**Fix options — simplest first:**

**Option A (recommended):** Set `ASTRAL_WORKERS=1` as a Railway environment variable and document that the scheduler process should be single-worker. `dispatch_workers: 2` in config suggests this was anticipated — it's cheap to document.

**Option B:** Use a gunicorn `post_fork` server hook or a `when_ready` hook in a `gunicorn.conf.py` to start the scheduler only in worker 0. More moving parts.

**Option C:** Wrap `start_scheduler()` in a filesystem lock or a DB-backed "scheduler claimed" flag so only one worker actually arms the loop. Most robust, most work.

Option A is the right call for now — single worker is fine for this app given SQLite and the batch-locking safety net.

---

## Advisory Items

### 2. `dispatcher.py` calls `database` module directly for 5 functions (layer rule gray area)

The file imports `from src.data import database` and calls `database.get_candidate()`, `database.save_dispatch_ledger()`, `database.update_dispatch_ledger()`, `database.get_due_tasks()`, and `database.update_dispatch_task()` directly, bypassing the thin-wrapper pattern used for the other db functions in the same file.

Per the ASTRAL_CODE_RULES (§3.3): core may import data, so this isn't a violation. The old `src/core/dispatch.py` explicitly noted a "documented exception" for `run_astral.py` calling data directly. Now that the dispatcher *is* core, the exception evaporates — but the direct calls remain.

This is fine functionally. Worth noting because it's inconsistent with the wrapper pattern used for the other six db calls in the same file, and a future reader might wonder why some go through `_db_*` aliases and some don't.

### 3. `dispatch_workers: 2` in config is unused

`ASTRAL_CONFIG["dispatch_workers"]` was added per the plan but nothing reads it. `railway.toml` uses `${ASTRAL_WORKERS:-2}` (an env var), not the config value. Either wire it up or remove it to avoid confusion.

---

## What Looks Good

- **Plan fidelity is 100%.** Every step in the plan (`ast-293-in-process-dispatch-scheduler-plan.md`) maps to the implementation. All six steps delivered.
- **Scheduler state design is clean.** Module-level globals + `threading.Event` for wake-on-toggle/run-now is the right pattern. The `_running` guard correctly skips cycles if the previous dispatch hasn't finished.
- **`log_batch_id` is a `ContextVar`.** Since `asyncio.gather` runs tasks concurrently in the same thread, each `_dispatch_one` coroutine sets `log_batch_id` independently. `ContextVar` handles this correctly — each asyncio task gets its own context copy, so log entries from concurrent tasks won't bleed into each other's batch_id.
- **`asyncio.wait_for` timeout.** Moved from `system.py` into the scheduler loop where it belongs. `_DISPATCH_TIMEOUT` constant is named and documented.
- **Old cron endpoint removed cleanly.** `POST /internal/dispatch` (secret-header auth) is gone; replaced by four properly `@require_auth`-decorated endpoints.
- **`set_interval` has a floor of 30s.** Prevents runaway calls if someone sends `interval_seconds=0`.
- **UI interval input saves on blur and Enter.** Correct pattern (matches the existing `onBlur` convention in this codebase per earlier commits).
- **`src/cli/` cleanup is complete.** `run_astral.py` and `__init__.py` deleted. No dangling imports anywhere in the codebase.
- **`railway.toml` env-var defaulting** (`${ASTRAL_WORKERS:-2}`) is cleaner than a hardcoded `2` — gives Railway-level override without a redeploy.
