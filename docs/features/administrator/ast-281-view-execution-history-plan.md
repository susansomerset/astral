<!-- linear-archive: AST-281 archived 2026-06-03 -->

## Linear archive (AST-281)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-281/view-execution-history  
**Status at archive:** Done  
**Project:** Astral Administrator  
**Assignee:** susan  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Admin screen showing a summary list of Dispatcher-initiated batch runs. The Dispatcher writes execution_session records as a side effect of orchestrating each run. Clicking a session opens a modal surfacing log content from Better Stack filtered to that batch_id.

Execution History is Dispatcher-only — manually triggered CLI runs go to console and are not recorded here.

**Acceptance Criteria:**

**Better Stack Setup:**

* Configure Better Stack (Logtail) as Railway log drain — one-click integration in Railway dashboard
* All existing stdout log output flows to Better Stack automatically via the drain — no [logging.py](<http://logging.py>) changes required
* Better Stack search URL pattern documented so batch_id deep-link URLs can be constructed dynamically

`execution_session` Table (new, written by Dispatcher only):

* `batch_id` — PK (the batch_id from the dispatch run — no new identifier needed)
* `task_key` — TEXT (which task was dispatched)
* `candidate_id` — TEXT (FK to candidate)
* `started_at` — TIMESTAMP
* `completed_at` — TIMESTAMP (nullable, set on completion)
* `status` — TEXT (RUNNING, COMPLETED, FAILED)
* `total_processed` — INTEGER
* `total_passed` — INTEGER
* `total_failed` — INTEGER
* `total_errors` — INTEGER
* `better_stack_url` — TEXT (constructed deep-link URL to Better Stack filtered to this batch_id)

**View Execution History Screen (UI — Admin > Execution History):**

* ListPage showing execution_session records, newest first
* Columns: started_at, task_key, candidate_id, status, total_processed, total_passed, total_failed, total_errors, duration
* Click row → modal surfacing log content from Better Stack for this batch_id (implementation at Chuckles' discretion)
* Link from row → Agent Timesheets filtered by batch_id (URL querystring)

**API Endpoints:**

* GET /api/admin/execution_sessions — list sessions (filterable by task_key, candidate_id, status, date range)
* GET /api/admin/execution_sessions/:batch_id — single session detail

**Notes:**

* execution_session records are created and updated by [dispatcher.py](<http://dispatcher.py>) — this feature is UI-only on the read side
* No CLI changes required

**Database:**

* execution_session table: CREATE TABLE as above
* [database.py](<http://database.py>) module docstring updated per ASTRAL_CODE_RULES 1.1

### Comments

_No comments._

---

# ast-281: View Execution History

## Subissues (from CSV, revised)

The feature has four subissues:

1. **dispatch_ledger + app_log tables and database functions** (High priority, estimate 1)
2. **logging.py database handler with contextvars** (High priority, estimate 1)
3. **Core wrappers, API endpoints + nav enable** (High priority, estimate 1)
4. **View Execution History screen** (Medium priority, estimate 1)

Better Stack is deferred — logs go to a database table. `logging.py` is the abstraction boundary; when/if we switch to Better Stack or another provider, only `logging.py` changes.

---

## Sub 1: database.py — dispatch_ledger + app_log tables

**Files:** [src/data/database.py](src/data/database.py)

### dispatch_ledger table

Written by Dispatcher (ast-282), read by this feature.

- `_ensure_dispatch_ledger_schema()` — idempotent, following existing pattern
- Schema:

```
batch_id         TEXT PK
task_key         TEXT
candidate_id     TEXT (FK to candidate)
started_at       TIMESTAMP
completed_at     TIMESTAMP (nullable)
status           TEXT (RUNNING, COMPLETED, FAILED)
total_processed  INTEGER
total_passed     INTEGER
total_failed     INTEGER
total_errors     INTEGER
```

- `save_dispatch_ledger(batch_id, task_key, candidate_id, started_at, status)` — insert new record
- `update_dispatch_ledger(batch_id, **kwargs)` — update fields on existing record
- `get_dispatch_ledger(batch_id)` — single record by PK
- `list_dispatch_ledger(task_key=None, candidate_id=None, status=None, date_from=None, date_to=None)` — all filters optional, dynamic WHERE, newest first. Uses `_run_with_retry`. `date_to` appends `T23:59:59`.

### app_log table

Append-only log storage, written by the logging handler (Sub 2).

- `_ensure_app_log_schema()` — idempotent
- Schema:

```
id            TEXT PK
level         TEXT
logger_name   TEXT
message       TEXT
batch_id      TEXT (nullable — set from contextvar during dispatch runs)
created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

- `add_log_entry(level, logger_name, message, batch_id=None)` — fast write path, same pattern as `add_timesheet_entry`
- `list_log_entries(batch_id=None, level=None, date_from=None, date_to=None)` — filters optional, newest first, `_run_with_retry`
- Update `database.py` module docstring to add both tables to inventory

---

## Sub 2: logging.py — database handler with contextvars

**Files:** [src/utils/logging.py](src/utils/logging.py)

- Add a `contextvars.ContextVar` named `log_batch_id` (default `None`). The Dispatcher (ast-282) will call `log_batch_id.set(batch_id)` at the start of each run and reset it on completion.
- Add a custom `logging.Handler` subclass (`DatabaseLogHandler`) that:
  - On each `emit()`, calls `database.add_log_entry(level, logger_name, message, batch_id)` reading `batch_id` from the context var
  - Catches and silences its own exceptions (a logging handler must never crash the caller)
- Attach `DatabaseLogHandler` in `get_logger()` alongside the existing stdout handler
- All existing `logger.info()` / `logger.warning()` / etc. calls automatically flow to both stdout and the database — no caller changes

**Import note:** `logging.py` is in the utils layer, which per section 3.3 imports nothing. But it needs to call `database.add_log_entry()`. Two options:
- (a) Late import `from src.data.database import add_log_entry` inside `emit()` to avoid circular import at module load
- (b) Register the handler lazily from `server.py` / CLI startup code (keeps utils pure, wires at the entry point)

Option (a) is simpler and self-contained. The late import inside `emit()` avoids any load-order issues.

---

## Sub 3: Core wrappers, API endpoints + nav enable

**Files:** new [src/core/dispatch.py](src/core/dispatch.py), new [src/ui/api/admin_dispatch.py](src/ui/api/admin_dispatch.py), [src/ui/server.py](src/ui/server.py), [src/utils/config.py](src/utils/config.py)

- New `src/core/dispatch.py` with read-side wrappers:
  - `list_dispatch_ledger(...)` — delegates to `database.list_dispatch_ledger`
  - `get_dispatch_ledger(batch_id)` — delegates to `database.get_dispatch_ledger`
  - `list_log_entries(...)` — delegates to `database.list_log_entries`
  - Core layer — imports data, per section 3.3. Write-side wrappers added when ast-282 lands.
- New Blueprint `admin_dispatch_bp` with `url_prefix="/api/admin/dispatch_ledger"`
  - `GET /api/admin/dispatch_ledger` — list with filter query params (`task_key`, `candidate_id`, `status`, `date_from`, `date_to`), returns JSON array
  - `GET /api/admin/dispatch_ledger/<batch_id>` — single record detail
  - `GET /api/admin/dispatch_ledger/<batch_id>/logs` — log entries for this batch, returns JSON array
- Register blueprint in `server.py`
- In NAV_CONFIG: remove `"enabled": False` from the Execution History item

---

## Sub 4: View Execution History screen

**File:** [src/ui/frontend/src/pages/Admin/PerformanceMonitor.tsx](src/ui/frontend/src/pages/Admin/PerformanceMonitor.tsx) (keep filename — nav label is what matters)

De-stub into a working screen. Pattern follows [AgentTimesheets.tsx](src/ui/frontend/src/pages/Admin/AgentTimesheets.tsx).

- Sortable list of dispatch_ledger records, newest first
- Columns: `started_at`, `task_key`, `candidate_id`, `status`, `total_processed`, `total_passed`, `total_failed`, `total_errors`, `duration` (computed client-side from `started_at`/`completed_at`)
- Status column with color-coded badges: green (COMPLETED), amber (RUNNING), red (FAILED)
- Click row → expands inline log viewer showing log entries for that batch_id (fetched from `/api/admin/dispatch_ledger/<batch_id>/logs`)
- Link per row → Agent Timesheets: `/admin/agent_timesheets?session_id=<batch_id>` (deep-link; populates once ast-282 Dispatcher passes batch_id as session_id to anthropic calls)
- Filter controls: `task_key` dropdown, `candidate_id` dropdown, `status` dropdown, date range
- Styles added to [App.css](src/ui/frontend/src/App.css)

---

## Dependencies / Notes

- **dispatch_ledger table is shared with ast-282 (Manage Task Dispatcher).** We create the table and read functions here. ast-282 uses the write functions.
- **app_log replaces Better Stack.** Logs go to a database table instead of an external service. `logging.py` is the abstraction boundary — switching to Better Stack later means updating the handler in `logging.py` only.
- **`log_batch_id` context var is set by ast-282.** Until the Dispatcher is built, `batch_id` will be null on log entries. The UI handles this (shows all logs, or empty set when filtering by batch_id). Manual CLI runs won't have a batch_id unless they set the context var.
- **Timesheets deep-link depends on ast-282.** Same as ast-285 — the link is wired now, data flows once Dispatcher passes batch_id through.
