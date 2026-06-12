<!-- linear-archive: AST-327 archived 2026-06-03 -->

## Linear archive (AST-327)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-327/refactor-task-dispatcher-to-run-independent-threads  
**Status at archive:** Done  
**Project:** Astral Dispatcher  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Right now, the Task Dispatcher has a screen with a header space, and a "Run Now" button.

What I want is a "thread" for each task in the dispatch which can be set to auto-run or to be manually run from a button on its row.  I think this means setting the enabled status options to "CLICK|AUTO", but it will allow me to test various dispatch tasks without having to interfere with the auto-running threads.

Dispatch tasks cannot be run manually when they are in AUTO, and when they are in CLICK, they get an enabled "Run" button on the row.  "Run" is Disabled when in AUTO.

While running, there should be a "Stop" button next to the "Run" button goes, and that should be enabled whenever the task thread is active, regardless of AUTO or CLICK, the Admin needs to be able to kill stuck threads.

Be sure that the killing activity that happens when the Admin clicks "Stop" is included in the log content to confirm that the tasks are fully cleared from memory on the server, no orphaned runs.

Add an expand arrow to the left of the columns on each row, and when it expands, show the expandable execution history for that task, showing up to 8 rows of history and making the set vertically scrollable, in descending order of ledger_created_at.

Keep the execution history page as is, until we are happy with the new task dispatcher screen.

### Comments

_No comments._

---

# AST-327: Refactor Task Dispatcher to Run Independent Threads

## Summary

Replace the single global scheduler loop (which runs all due tasks serially) with per-task daemon threads — one per dispatch_task row. Each task thread operates independently: AUTO tasks run on their own `freq_hrs` schedule, CLICK tasks wait for a manual Run button press. The header-level "Run Now" is removed; a "Stop All" confirmation modal replaces it. The `enabled` column is renamed `auto_mode` (CLICK = 0, AUTO = 1).

---

## Decisions

| Topic | Decision |
|---|---|
| `enabled` column | Rename to `auto_mode` via SQLite table-rebuild migration. `0 = CLICK` (manual only), `1 = AUTO` (scheduled). |
| Global "Run Now" | Removed. Replaced by per-row Run button (CLICK mode) and "Stop All" modal. |
| Parallel execution | True parallel per-task daemon threads with per-task asyncio event loops. |
| Thread cap | `max_auto_threads` in `ASTRAL_CONFIG` (default 3). AUTO tasks that exceed the cap wait FIFO until next tick. CLICK tasks are excluded from this limit. |
| Tick rate | `tick_rate_minutes` in `ASTRAL_CONFIG` (default 1). Global tick thread wakes every N minutes to check which AUTO tasks are due. |
| Execution history | Deferred — future scope. |

---

## Step 1: `src/data/database.py` — Schema migration + reference updates

**Migration** (in `_ensure_dispatch_task_schema`):
- If table exists and has `enabled` column but no `auto_mode`: rebuild table via CREATE new → copy (`auto_mode = enabled`) → DROP old → RENAME
- New table definition uses `auto_mode INTEGER NOT NULL DEFAULT 0`
- `_DISPATCH_TASK_UPDATE_COLS`: replace `"enabled"` with `"auto_mode"`
- `save_dispatch_task`: param `enabled` → `auto_mode`, default `False`
- `get_due_tasks`: `WHERE enabled = 1` → `WHERE auto_mode = 1`
- `get_active_trigger_states`: same filter update

---

## Step 2: `src/utils/config.py` — New dispatcher config keys

Replace `dispatch_interval_minutes` and `auto_run` with:

```python
"tick_rate_minutes": 1,        # how often the global tick wakes to check AUTO tasks
"max_auto_threads": 3,         # ceiling for concurrent AUTO task threads; CLICK threads excluded
"dispatch_timeout_seconds": 1200,  # per-task asyncio.wait_for timeout (20 min)
```

`dispatcher.py` reads `ASTRAL_CONFIG["dispatch_timeout_seconds"]` — the module-level `_DISPATCH_TIMEOUT = 20 * 60` constant is removed.

---

## Step 3: `src/core/dispatcher.py` — Per-task thread model

### Remove
- `_active`, `_interval`, `_last_run_at`, `_run_now_requested`, `_event`, `_thread`
- `_current_task`, `_current_loop` (single-task tracking)
- `_scheduler_loop()`, `_dispatch_with_tracking()`
- `start_scheduler()`, `stop_scheduler()`, `run_now()`, `cancel_dispatch()`, `set_interval()`, `toggle_active()`, `scheduler_status()`

### Add: per-task thread state

```python
# task_id -> { thread, loop, asyncio_task, task_key, candidate_id, is_auto }
_task_registry: Dict[int, Dict] = {}
_registry_lock = threading.Lock()
```

### Add: per-task runner

`_run_task_thread(task_id, task_dict)` — daemon thread target:
1. Creates its own asyncio event loop
2. Registers itself in `_task_registry`
3. Runs `_dispatch_with_timeout(task_dict)` (wraps existing `dispatch()` logic for a single task)
4. On completion or cancellation: writes ledger final status, logs "thread cleared" confirmation, removes itself from registry

Kill logging: when `cancel_task()` triggers cancellation, the `except asyncio.CancelledError` block in the thread writes a ledger entry with `status="INTERRUPTED"` and logs:
```
[task_key/batch_id] KILLED by admin — thread cleared from memory
```

### Add: public control functions

| Function | Behaviour |
|---|---|
| `run_task(task_id)` | Spawns a new daemon thread for the given task_id if not already running. Works for both CLICK and AUTO tasks. |
| `cancel_task(task_id)` | Cancels the asyncio task for task_id, logs kill to ledger, confirms thread cleared. Returns `{"task_key", "candidate_id", "killed": bool}`. |
| `cancel_all_tasks()` | Iterates all active registry entries, cancels each, returns list of `{"task_key", "candidate_id"}` killed. |
| `task_status_all()` | Returns `{task_id: {"running": bool, "task_key": str, "candidate_id": str}}` for all registry entries. |

### Add: global tick thread

`_tick_loop()` — lightweight daemon, wakes every `tick_rate_minutes`:
1. Calls `database.get_due_tasks()` (returns `auto_mode=1` tasks with available entities)
2. Counts currently running AUTO threads from registry
3. If count < `max_auto_threads`: spawn threads for due tasks, FIFO by id, up to the cap
4. Already-running tasks are skipped (no duplicate threads)

`start_scheduler()` — starts the tick daemon thread. Called once from `src/ui/server.py`. Safe to call multiple times (checks if alive).

---

## Step 4: `src/ui/api/api_admin.py` — All scheduler + per-task endpoints

All scheduler control moves here (out of `api_system.py`). `api_admin.py` already imports from `src.core.dispatcher` — this consolidates all dispatch-related API into one module.

**Remove from `api_system.py`** (these move here):
- `GET /api/admin/scheduler` — old status
- `POST /api/admin/scheduler/toggle`
- `POST /api/admin/scheduler/run`
- `POST /api/admin/scheduler/cancel`
- `PUT /api/admin/scheduler` (interval)

**New endpoints added to `api_admin.py`:**

| Endpoint | Method | Description |
|---|---|---|
| `/api/admin/dispatch_tasks/<id>/run` | POST | Calls `run_task(id)`. Returns `{"started": bool}`. |
| `/api/admin/dispatch_tasks/<id>/stop` | POST | Calls `cancel_task(id)`. Returns killed task info. |
| `/api/admin/scheduler/stop_all` | POST | Calls `cancel_all_tasks()`. Returns list of killed tasks. |
| `/api/admin/scheduler/thread_status` | GET | Calls `task_status_all()`. Returns active thread map. |

**Update `_DISPATCH_TASK_COLUMNS`**: replace `{"key": "enabled", ...}` with `{"key": "auto_mode", "label": "AUTO", "type": "str"}`

**Update `update_dtask`**: replace `"enabled"` with `"auto_mode"` in allowed set; update int-cast block.

**Update `create_dtask`**: replace `enabled=bool(data.get("enabled", True))` with `auto_mode=bool(data.get("auto_mode", False))`.

---

## Step 5: `src/ui/api/api_system.py` — Strip scheduler endpoints

Remove all scheduler-related imports and routes (moved to `api_admin.py`). File becomes pure infrastructure: `/health`, `/me`, `/nav_config`, `/shapes/<entity>`, `/ui_config` only.

---

## Step 6: `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — UI refactor

### Remove
- `SchedulerStatus` interface and all `sched` state
- `loadScheduler`, `toggleScheduler`, `triggerRunNow`, `cancelDispatch`, `saveInterval`
- Scheduler header bar (Active/Paused badge, interval input, Run Now / Cancel Run button)

### Add: thread status polling
- `threadStatus: Record<number, {running: boolean, task_key: string, candidate_id: string}>`
- Poll `GET /api/admin/scheduler/thread_status` every 5 seconds
- Track active thread count: `activeAutoCount`, `activeClickCount`

### Header becomes
```
Task Dispatcher    [active: N threads]    [Stop All]
```
- Thread count is live from `threadStatus`
- "Stop All" button: disabled when no threads active; opens confirmation modal

### Stop All confirmation modal
- Lists each active thread explicitly: `task_key (candidate_id)`
- "Cancel" and "Kill All" buttons
- On confirm: POST `/api/admin/scheduler/stop_all`, refresh thread status + task list

### DispatchTask interface update
- `enabled: number` → `auto_mode: number`

### Per-row changes
- **AUTO column**: `ON/OFF` badge (replaces old Enabled badge), calls `PATCH auto_mode`
- **Run button**: always visible; enabled when task not currently running; disabled when running; calls `POST /dispatch_tasks/<id>/run`
- **Stop button**: always visible; enabled only when `threadStatus[row.id]?.running`; calls `POST /dispatch_tasks/<id>/stop`
- Row click still opens edit modal (no change to edit modal except `enabled` checkbox → `auto_mode` checkbox labelled "AUTO mode")

### Table column order
```
Candidate | Task | Entity | State | AUTO | Run | Stop | Freq | Min | Batch | Runs | Last Run
```

---

## Step 7: `docs/ASTRAL_CODE_RULES.md` — Update in-process scheduler description

Update §3.5 "In-process dispatch scheduler" section to reflect:
- Per-task daemon threads replacing single scheduler loop
- `start_scheduler()` starts tick thread, not a monolithic loop
- `run_task(id)` / `cancel_task(id)` / `cancel_all_tasks()` as the new control API
- All scheduler endpoints now live in `api_admin.py`
- Config keys: `tick_rate_minutes`, `max_auto_threads`, `dispatch_timeout_seconds`

---

## Files Changed

| File | Change |
|---|---|
| `src/data/database.py` | Table rebuild migration `enabled→auto_mode`; update `save_dispatch_task`, `_DISPATCH_TASK_UPDATE_COLS`, `get_due_tasks`, `get_active_trigger_states` |
| `src/utils/config.py` | Replace `dispatch_interval_minutes` + `auto_run` with `tick_rate_minutes`, `max_auto_threads`, `dispatch_timeout_seconds` |
| `src/core/dispatcher.py` | Full scheduler section rewrite: per-task threads, `run_task`, `cancel_task`, `cancel_all_tasks`, `task_status_all`, `_tick_loop`, `start_scheduler`; remove `_DISPATCH_TIMEOUT` constant |
| `src/ui/api/api_admin.py` | Add all new + moved scheduler endpoints; `enabled→auto_mode` in columns, allowed update fields, and create handler |
| `src/ui/api/api_system.py` | Remove all scheduler endpoints and imports — infrastructure only |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Per-row AUTO toggle, Run/Stop buttons, Stop All modal, thread status polling |
| `docs/ASTRAL_CODE_RULES.md` | Update §3.5 in-process scheduler description |

---

## Out of Scope (Future)

- Expandable per-row execution history (deferred per AST-327 discussion)
- The existing Execution History page (`dispatch_ledger` list view) is untouched
