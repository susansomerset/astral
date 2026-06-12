<!-- linear-archive: AST-293 archived 2026-06-03 -->

## Linear archive (AST-293)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-293/in-process-dispatch-scheduler  
**Status at archive:** Done  
**Project:** Astral Dispatcher  
**Assignee:** susan  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Upgrade the Dispatcher from an external Railway cron service to a self-managed, in-process scheduler with full admin controls on the Task Dispatcher page.

**Problem:**
The current Dispatcher runs as a separate Railway cron service that triggers the web server via webhook. This creates operational risks: zombie processes run for hours with no timeout, the scheduler cannot be paused or adjusted from the UI, the cron and web services deploy independently (a rename can silently break dispatch), and dispatch logic is split between the CLI and core layers with no functional benefit.

**Solution:**
Move the scheduler into the web server and expose controls on the existing Task Dispatcher admin page.

**Acceptance Criteria:**

**Codebase Consolidation:**

* Merge all batch runner logic and dispatch orchestration from `src/cli/run_astral.py` into `src/core/dispatcher.py`
* Delete `src/cli/` directory entirely — no CLI entry points remain
* Rename `src/core/dispatch.py` to `src/core/dispatcher.py` (consistent with `gazer.py`, `tracker.py`, `roster.py`)
* Rename `ui/api/admin_dispatch.py` to `ui/api/admin_dispatch_history.py` for clarity
* Update all import paths across backend and API layers

**In-Process Scheduler Thread:**

* Background daemon thread runs inside the web server process — no external cron service required
* Event-based sleep (`threading.Event.wait`) for interruptible intervals
* Skip dispatch cycle if previous cycle is still running (overlap guard)
* 20-minute hard timeout per dispatch cycle (`asyncio.wait_for`) — kills stuck scrapes/API calls
* Supports multiple concurrent Gunicorn workers (existing DB-level batch claim locks prevent double-processing)

**Admin UI Controls (Task Dispatcher page — status bar between title and table):**

* **Active / Paused toggle** — Click to flip scheduler state. Green badge when active, grey when paused. Calls `POST /api/admin/scheduler/toggle`
* **Run Now button** — Triggers an immediate dispatch cycle regardless of interval timer. Calls `POST /api/admin/scheduler/run`
* **Last Run timestamp** — Displays the time of the last completed dispatch cycle using the candidate's timezone
* **Interval setting** — Editable number input (minutes) to control how often the scheduler fires. Saves on blur via `PUT /api/admin/scheduler`
* **Auto-refresh** — Status bar polls `GET /api/admin/scheduler` every 15 seconds to stay current

**API Endpoints:**

* `GET /api/admin/scheduler` — Returns scheduler status (active, interval_seconds, last_run_at, running)
* `POST /api/admin/scheduler/toggle` — Flip active/paused state
* `POST /api/admin/scheduler/run` — Wake the scheduler thread immediately
* `PUT /api/admin/scheduler` — Update interval (accepts `interval_seconds`)
* Remove `POST /api/internal/dispatch` — no longer needed

**Configuration:**

* Add `dispatch_interval_minutes` (default 5) and `dispatch_workers` (default 2) to `ASTRAL_CONFIG`
* `railway.toml` worker count reads from config

**Notes:**

* Scheduler thread starts automatically when the web server boots — no manual activation needed, runs even with no active users
* Existing DB-level batch claim locks ensure safe concurrent dispatch across Gunicorn workers
* Railway cron service should be disabled in the Railway dashboard after deployment

### Comments

_No comments._

---

# In-Process Dispatch Scheduler

## Step 0: Create Linear feature CSV

Create `docs/linear-imports/dispatcher-features.csv` matching the format of [admin-features.csv](docs/linear-imports/admin-features.csv) — one row with Title, Description (markdown), State, Priority, Labels, Project, Estimate.

The single feature covers the full scope:

- Merge all batch runner + dispatch logic from `src/cli/run_astral.py` into `src/core/dispatcher.py`
- Delete the `src/cli/` directory entirely
- In-process scheduler thread with 20-minute timeout protection
- **Active/Paused toggle** on the Task Dispatcher admin page
- **Run Now** button to trigger an immediate dispatch cycle
- **Last Run** timestamp display
- **Configurable interval** (minutes between runs)
- Scheduler API endpoints (status, toggle, run, set interval)
- Remove dependency on external Railway cron service

## Step 1: Merge `run_astral.py` into `dispatch.py`, rename to `dispatcher.py`

Move from `src/cli/run_astral.py` into `src/core/dispatch.py`:

- `_SUMMARY_ZERO`, `_now_iso()`
- All `_run_*` batch runner helper functions
- `_RUNNERS` registry dict
- `_dispatch_one()` orchestrator
- `dispatch()` main entry point

Rename `src/core/dispatch.py` to `src/core/dispatcher.py` (matches `gazer.py`, `tracker.py`, `roster.py`).

Existing thin wrappers (`list_dispatch_ledger`, `save_dispatch_task`, etc.) stay.

## Step 2: Add scheduler to `dispatcher.py`

Module-level state:

- `_active` (bool, default True) / `_interval` (seconds) / `_last_run_at` (ISO string) / `_running` (bool) / `_event` (threading.Event)
- `_DISPATCH_TIMEOUT = 20 * 60` (moved from system.py)

Daemon thread loop: sleep via `_event.wait(timeout=_interval)`, skip if paused or already running, run `dispatch()` wrapped in `asyncio.wait_for` with timeout.

Public API: `start_scheduler()`, `stop_scheduler()`, `run_now()`, `set_interval(seconds)`, `scheduler_status() -> dict`

## Step 3: Fix imports + rename admin file

- `src/ui/api/admin_dispatch_tasks.py` — `src.core.dispatch` -> `src.core.dispatcher`
- Rename `src/ui/api/admin_dispatch.py` -> `src/ui/api/admin_dispatch_history.py`, update internal imports
- `src/ui/server.py` — update import path for both, call `start_scheduler()`
- `src/ui/api/admin_timesheets.py` — update import path if it references `src.core.dispatch`

## Step 4: Config + API endpoints

`src/utils/config.py` — add `dispatch_interval_minutes` (default 5), `dispatch_workers` (default 2) to `ASTRAL_CONFIG`.

`src/ui/api/system.py` — replace `POST /internal/dispatch` with:
- `GET /api/admin/scheduler` — returns status
- `POST /api/admin/scheduler/toggle` — flip active/paused
- `POST /api/admin/scheduler/run` — wake the thread
- `PUT /api/admin/scheduler` — set interval

## Step 5: Frontend scheduler status bar

`ScheduledActions.tsx` — add a status bar between title and table:

```
Scheduler: [Active] | Last Run: 3/8/2026, 9:32 PM | Every [5] min | [Run Now]
```

- Active/Paused badge (toggle on click)
- `<Time>` component for Last Run
- Editable interval (number input, saves on blur)
- Run Now button
- Poll `GET /api/admin/scheduler` every 15s

## Step 6: Cleanup

- Delete `src/cli/run_astral.py` and `src/cli/__init__.py`
- Update `railway.toml` worker count to reference config
- Compile check (TypeScript + Python)

## Files Changed

- `docs/linear-imports/dispatcher-features.csv` — **new**
- `src/core/dispatch.py` -> **renamed** `src/core/dispatcher.py`, absorbs run_astral.py + scheduler
- `src/ui/api/admin_dispatch.py` -> **renamed** `src/ui/api/admin_dispatch_history.py`
- `src/utils/config.py` — add config entries
- `src/ui/server.py` — start_scheduler(), updated imports
- `src/ui/api/system.py` — scheduler endpoints, remove /internal/dispatch
- `src/ui/api/admin_dispatch_tasks.py` — update import
- `src/ui/frontend/src/pages/Admin/ScheduledActions.tsx` — scheduler status bar
- `railway.toml` — worker count
- `src/cli/run_astral.py` — **deleted**
- `src/cli/__init__.py` — **deleted**
