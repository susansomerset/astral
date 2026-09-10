# AST-281 — View Execution History
**Component:** administrator  
**Children:** — (single ticket)  
**Linear archived:** AST-281 2026-06-03  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-03-02 16:33 | AST-281 | — | `499359d4a` | ast-281: View Execution History — full feature |
| 2026-03-02 16:48 | AST-281 | — | `0db73d781` | ast-281: Address code review feedback |
| 2026-03-02 16:54 | AST-281 | merge | `2c7861851` | Merge pull request #34 from susansomerset/chuckles/ast-281-view-execution-history |

_The review doc's own SHAs (`1975913`, `03bb089`) predate the repo-history migration and do not resolve on `origin/dev`; the two commits above are the real trail. Era path convention was `ui/…` (not `src/ui/…`)._

## Epic — AST-281
_Archived: 2026-06-03 · Linear URL: https://linear.app/astralcareermatch/issue/AST-281/view-execution-history · Status at archive: Done · Project: Astral Administrator · Assignee: susan · Priority / estimate: Medium / 5_

### Original brief

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

#### Comments

_No comments._

### Plan — ast-281: View Execution History

#### Subissues (from CSV, revised)

The feature has four subissues:

1. **dispatch_ledger + app_log tables and database functions** (High priority, estimate 1)
2. **logging.py database handler with contextvars** (High priority, estimate 1)
3. **Core wrappers, API endpoints + nav enable** (High priority, estimate 1)
4. **View Execution History screen** (Medium priority, estimate 1)

Better Stack is deferred — logs go to a database table. `logging.py` is the abstraction boundary; when/if we switch to Better Stack or another provider, only `logging.py` changes. *(Supersedes the "Better Stack Setup" acceptance criteria in the brief above — the `execution_session` table becomes `dispatch_ledger`, and log content is served from a new `app_log` table.)*

#### Sub 1: database.py — dispatch_ledger + app_log tables

**Files:** [src/data/database.py](src/data/database.py)

##### dispatch_ledger table

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

##### app_log table

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

#### Sub 2: logging.py — database handler with contextvars

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

#### Sub 3: Core wrappers, API endpoints + nav enable

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

#### Sub 4: View Execution History screen

**File:** [src/ui/frontend/src/pages/Admin/PerformanceMonitor.tsx](src/ui/frontend/src/pages/Admin/PerformanceMonitor.tsx) (keep filename — nav label is what matters)

De-stub into a working screen. Pattern follows [AgentTimesheets.tsx](src/ui/frontend/src/pages/Admin/AgentTimesheets.tsx).

- Sortable list of dispatch_ledger records, newest first
- Columns: `started_at`, `task_key`, `candidate_id`, `status`, `total_processed`, `total_passed`, `total_failed`, `total_errors`, `duration` (computed client-side from `started_at`/`completed_at`)
- Status column with color-coded badges: green (COMPLETED), amber (RUNNING), red (FAILED)
- Click row → expands inline log viewer showing log entries for that batch_id (fetched from `/api/admin/dispatch_ledger/<batch_id>/logs`)
- Link per row → Agent Timesheets: `/admin/agent_timesheets?session_id=<batch_id>` (deep-link; populates once ast-282 Dispatcher passes batch_id as session_id to anthropic calls)
- Filter controls: `task_key` dropdown, `candidate_id` dropdown, `status` dropdown, date range
- Styles added to [App.css](src/ui/frontend/src/App.css)

#### Dependencies / Notes

- **dispatch_ledger table is shared with ast-282 (Manage Task Dispatcher).** We create the table and read functions here. ast-282 uses the write functions.
- **app_log replaces Better Stack.** Logs go to a database table instead of an external service. `logging.py` is the abstraction boundary — switching to Better Stack later means updating the handler in `logging.py` only.
- **`log_batch_id` context var is set by ast-282.** Until the Dispatcher is built, `batch_id` will be null on log entries. The UI handles this (shows all logs, or empty set when filtering by batch_id). Manual CLI runs won't have a batch_id unless they set the context var.
- **Timesheets deep-link depends on ast-282.** Same as ast-285 — the link is wired now, data flows once Dispatcher passes batch_id through.

### Code review (`1975913` per doc → real trail `499359d4a` + `0db73d781`)

Four-subissue feature delivered in a single commit:
1. `dispatch_ledger` + `app_log` tables with full CRUD in `database.py`
2. `DatabaseLogHandler` in `logging.py` with `log_batch_id` contextvar for automatic batch tagging
3. Core wrappers, API endpoints, nav enable
4. De-stubbed Execution History screen with filters, status badges, expandable inline log viewer, and timesheets deep-link

#### The Good

1. **`DatabaseLogHandler` is well-designed.** Late import of `add_log_entry` inside `emit()` avoids the circular import problem (utils → data) without any wiring code in entry points. The bare `except Exception: pass` is correct — a logging handler must never crash the caller. Handler is attached once via `_db_handler_attached` flag.
2. **`log_batch_id` contextvar is the right primitive.** Automatically propagates through async call chains, requires zero changes to existing logging call sites, and the Dispatcher (ast-282) only needs to set/reset it at batch boundaries. All 13+ modules using `get_logger` immediately gain batch tagging for free.
3. **`date_to` bug from ast-285 is fixed here.** `list_dispatch_ledger` appends `T23:59:59` to `date_to` before comparison, correctly including entries on the end date. Same fix applied to `list_log_entries`. This pattern should be backported to `list_timesheets` (ast-285).
4. **`list_dispatch_ledger` and `list_log_entries` both use `_run_with_retry`.** Follows the standard pattern, unlike the `list_timesheets` function from ast-285. Consistent.
5. **`update_dispatch_ledger` uses `**kwargs` with parameterized SQL.** Clean and flexible — the Dispatcher can update any subset of fields (status, completed_at, totals) without the function signature growing. Column names come from trusted internal code, not user input.
6. **Inline log viewer UX is solid.** Click-to-expand, per-batch log fetch, color-coded log levels, monospace log table, max-height with scroll. Error rows get a subtle red background. The expand toggle (▶/▼) is clean.
7. **Timesheets deep-link is wired.** Each dispatch row links to `/admin/agent_timesheets?session_id=<batch_id>`, which the ast-285 `useSearchParams` implementation will pick up. The `stopPropagation` on the link prevents the row-expand from firing.
8. **Core module docstring explicitly notes the write-side gap.** `dispatch.py` says "Write-side wrappers will be added when ast-282 lands." Clear intent.

#### Issues to Address

##### 1. RISK: Every log message writes to SQLite — volume and performance

Every `logger.info()`, `logger.warning()`, `logger.error()` across the entire application now writes a row to the `app_log` table via `add_log_entry`. This includes:
- High-frequency paths like roster scanning (logs per company, per job)
- Anthropic API call logging (multiple log lines per `do_task`)
- Any third-party library using the root logger at INFO+ level

`add_log_entry` opens a new connection, ensures schema, executes an INSERT, commits, and closes — per log line. Under batch processing (dozens of companies, hundreds of jobs), this could produce thousands of rows per run and significantly slow execution.

**Fix options:**
- Buffer log entries and flush in batches (e.g., every N entries or every T seconds)
- Add a minimum level filter on the database handler (e.g., WARNING+) to reduce volume, keeping INFO for stdout only
- Add an `app_log` retention/cleanup function to prevent unbounded table growth

##### 2. `update_dispatch_ledger` accepts arbitrary column names from `**kwargs`

```python
def update_dispatch_ledger(batch_id: str, **kwargs) -> None:
    pairs = [f"{k} = ?" for k in kwargs]
```

The column names are interpolated directly into SQL (not parameterized — you can't parameterize column names). While the callers will be internal code (the Dispatcher), the function signature doesn't validate that the keys match actual columns. A typo like `update_dispatch_ledger(batch_id, stauts="COMPLETED")` would silently succeed as a no-op (SQLite doesn't error on updating nonexistent columns with `SET` if the WHERE matches nothing, but it would error if the column doesn't exist — actually this would raise `OperationalError`).

Not a security risk (internal callers only), but worth noting. A whitelist of allowed columns would catch typos early:

```python
_LEDGER_UPDATE_COLS = {"completed_at", "status", "total_processed", "total_passed", "total_failed", "total_errors"}
```

##### 3. React fragment `<>` wrapping in tbody produces a warning

```tsx
{sorted.map(row => (
  <>
    <tr key={row.batch_id} ...>
    {expandedBatch === row.batch_id && (
      <tr key={`${row.batch_id}-logs`}>
    )}
  </>
))}
```

The fragment `<>` doesn't accept a `key` prop, and the `key` is on the inner `<tr>` instead of the fragment. React will warn about missing keys on list items. Should be `<Fragment key={row.batch_id}>` (imported from React) with the key on the Fragment.

##### 4. Logs are fetched on every expand toggle — no caching

```typescript
function toggleExpand(batchId: string) {
    setExpandedBatch(batchId)
    setLogsLoading(true)
    api(`/api/admin/dispatch_ledger/${batchId}/logs`)
      .then(r => r.json())
      .then(data => setLogs(Array.isArray(data) ? data : []))
```

If the user expands, collapses, and re-expands the same row, it re-fetches the logs each time. For completed batches (whose logs won't change), this is unnecessary. A simple cache (`Record<string, LogEntry[]>`) keyed by `batch_id` would avoid the repeated fetches. Low priority for an admin tool, but noticeable if the log list is large.

##### 5. No result limit on `list_dispatch_ledger` or `list_log_entries`

Same issue as flagged on ast-285's `list_timesheets` — both functions return all matching rows with no LIMIT. The dispatch ledger will grow unbounded as the Dispatcher runs. The log table will grow even faster (many log entries per dispatch run). An unfiltered load could be very large. The plan's use of `useSearchParams`-driven filters helps (users will likely filter), but the default unfiltered view on first load will fetch everything.

#### Minor Notes

- **Reuses `timesheet-filters` CSS class.** The filters div uses `className="timesheet-filters"` rather than a dispatch-specific class. This works because the styling is identical, but it creates a hidden coupling — changing the timesheets filter layout would affect this page too. A shared `.admin-filters` class (or similar) would be cleaner.
- **`add_log_entry` doesn't use `_run_with_retry`.** Same as `add_timesheet_entry` — it's a fast write path with its own try/except. This is consistent with the timesheet pattern but differs from the dispatch ledger functions. The plan specified this pattern, so it's by design.
- **Duration sort uses string comparison on formatted values.** Sorting by the `_duration` column compares strings like `"3s"`, `"1m 30s"`, `"—"`. This won't sort correctly — `"3s"` > `"1m 30s"` lexicographically. Sorting should compare the underlying millisecond difference, not the formatted string.
- **`dispatch.py` core wrappers are pure passthroughs.** All three functions are `return _db_function(**kwargs)`. The module docstring explains this is for layering compliance. Clear and correct — the write-side wrappers (ast-282) will add actual logic.

#### Summary

Clean, well-structured four-subissue feature that lands all the pieces called out in the plan. The logging handler design is particularly good — zero changes to existing callers, proper isolation via late import, contextvar for batch tagging. The main concern is **#1** (log volume/performance) — every log line now does a synchronous SQLite write, noticeable during batch processing. **#3** (React fragment key warning) is a quick fix. Everything else is minor.

#### Review Fixes Applied (`03bb089` per doc → landed in `0db73d781`)

- **Fix #1: Log buffering** — `_DatabaseLogHandler` now buffers entries in a thread-safe list and flushes to SQLite every 50 entries instead of per-line. `flush_log_buffer()` exposed for Dispatcher to call at batch end. `atexit` handler registered for normal shutdown.
- **Fix #2: Column whitelist on `update_dispatch_ledger`** — added `_LEDGER_UPDATE_COLS` set. `update_dispatch_ledger` raises `ValueError` if any key is not in the whitelist — catches typos before SQL execution.
- **Fix #3: React Fragment key warning** — replaced `<>` with `<Fragment key={row.batch_id}>` (imported from React). Removed redundant `key` from inner `<tr>` elements.
- **Fix #4: Log cache** — added `logCache: Record<string, LogEntry[]>` state. `toggleExpand` returns cached logs immediately if the batch has been fetched before, skipping the API call.
- **Minor: CSS class rename** — renamed `.timesheet-filters` → `.admin-filters` in `App.css`, `AgentTimesheets.tsx`, and `PerformanceMonitor.tsx`. Both admin pages now share the class without naming coupling.
- **Minor: Duration sort fix** — split `duration()` into `durationMs()` (returns raw ms) and `formatDuration()` (display string). Sort comparator now uses millisecond values so `1m 30s` correctly sorts after `3s`.

### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/data/database.py` | Sub 1 — `dispatch_ledger` + `app_log` schema/CRUD; module docstring inventory | `499359d4a` `0db73d781` |
| ✓ | `src/utils/logging.py` | Sub 2 — `DatabaseLogHandler` + `log_batch_id` contextvar; buffering added in review | `499359d4a` `0db73d781` |
| ✓ | `src/core/dispatch.py` (new) | Sub 3 — read-side wrappers | `499359d4a` |
| ✓ | `src/ui/api/admin_dispatch.py` (new) | Sub 3 — `admin_dispatch_bp` blueprint | `499359d4a` (`ui/api/admin_dispatch.py`) |
| ✓ | `src/ui/server.py` | Sub 3 — register blueprint | `499359d4a` (`ui/server.py`) |
| ✓ | `src/utils/config.py` | Sub 3 — NAV_CONFIG: enable Execution History | `499359d4a` |
| ✓ | `src/ui/frontend/src/pages/Admin/PerformanceMonitor.tsx` | Sub 4 — de-stub screen | `499359d4a` `0db73d781` |
| ✓ | `src/ui/frontend/src/App.css` | Sub 4 — styles | `499359d4a` `0db73d781` |
| + unplanned | `src/ui/frontend/src/pages/Admin/AgentTimesheets.tsx` | — | `0db73d781` — `.timesheet-filters` → `.admin-filters` rename (review Minor) |
| | _plan/review docs_ | — | `ast-281-view-execution-history-{plan,review}.md` (`499359d4a` `0db73d781`) |

_Implementation detail may live in git history on `origin/dev`._
