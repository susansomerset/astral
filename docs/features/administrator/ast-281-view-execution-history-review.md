# Code Review: `1975913` — ast-281: View Execution History

## What it does

Four-subissue feature delivered in a single commit:
1. `dispatch_ledger` + `app_log` tables with full CRUD in `database.py`
2. `DatabaseLogHandler` in `logging.py` with `log_batch_id` contextvar for automatic batch tagging
3. Core wrappers, API endpoints, nav enable
4. De-stubbed Execution History screen with filters, status badges, expandable inline log viewer, and timesheets deep-link

## The Good

1. **`DatabaseLogHandler` is well-designed.** Late import of `add_log_entry` inside `emit()` avoids the circular import problem (utils → data) without any wiring code in entry points. The bare `except Exception: pass` is correct — a logging handler must never crash the caller. Handler is attached once via `_db_handler_attached` flag.

2. **`log_batch_id` contextvar is the right primitive.** Automatically propagates through async call chains, requires zero changes to existing logging call sites, and the Dispatcher (ast-282) only needs to set/reset it at batch boundaries. All 13+ modules using `get_logger` immediately gain batch tagging for free.

3. **`date_to` bug from ast-285 is fixed here.** `list_dispatch_ledger` appends `T23:59:59` to `date_to` before comparison, correctly including entries on the end date. Same fix applied to `list_log_entries`. This pattern should be backported to `list_timesheets` (ast-285).

4. **`list_dispatch_ledger` and `list_log_entries` both use `_run_with_retry`.** Follows the standard pattern, unlike the `list_timesheets` function from ast-285. Consistent.

5. **`update_dispatch_ledger` uses `**kwargs` with parameterized SQL.** Clean and flexible — the Dispatcher can update any subset of fields (status, completed_at, totals) without the function signature growing. Column names come from trusted internal code, not user input.

6. **Inline log viewer UX is solid.** Click-to-expand, per-batch log fetch, color-coded log levels, monospace log table, max-height with scroll. Error rows get a subtle red background. The expand toggle (▶/▼) is clean.

7. **Timesheets deep-link is wired.** Each dispatch row links to `/admin/agent_timesheets?session_id=<batch_id>`, which the ast-285 `useSearchParams` implementation will pick up. The `stopPropagation` on the link prevents the row-expand from firing.

8. **Core module docstring explicitly notes the write-side gap.** `dispatch.py` says "Write-side wrappers will be added when ast-282 lands." Clear intent.

---

## Issues to Address

### 1. RISK: Every log message writes to SQLite — volume and performance

Every `logger.info()`, `logger.warning()`, `logger.error()` across the entire application now writes a row to the `app_log` table via `add_log_entry`. This includes:
- High-frequency paths like roster scanning (logs per company, per job)
- Anthropic API call logging (multiple log lines per `do_task`)
- Any third-party library using the root logger at INFO+ level

`add_log_entry` opens a new connection, ensures schema, executes an INSERT, commits, and closes — per log line. Under batch processing (dozens of companies, hundreds of jobs), this could produce thousands of rows per run and significantly slow execution.

**Fix options:**
- Buffer log entries and flush in batches (e.g., every N entries or every T seconds)
- Add a minimum level filter on the database handler (e.g., WARNING+) to reduce volume, keeping INFO for stdout only
- Add an `app_log` retention/cleanup function to prevent unbounded table growth

### 2. `update_dispatch_ledger` accepts arbitrary column names from `**kwargs`

```python
def update_dispatch_ledger(batch_id: str, **kwargs) -> None:
    pairs = [f"{k} = ?" for k in kwargs]
```

The column names are interpolated directly into SQL (not parameterized — you can't parameterize column names). While the callers will be internal code (the Dispatcher), the function signature doesn't validate that the keys match actual columns. A typo like `update_dispatch_ledger(batch_id, stauts="COMPLETED")` would silently succeed as a no-op (SQLite doesn't error on updating nonexistent columns with `SET` if the WHERE matches nothing, but it would error if the column doesn't exist — actually this would raise `OperationalError`).

Not a security risk (internal callers only), but worth noting. A whitelist of allowed columns would catch typos early:

```python
_LEDGER_UPDATE_COLS = {"completed_at", "status", "total_processed", "total_passed", "total_failed", "total_errors"}
```

### 3. React fragment `<>` wrapping in tbody produces a warning

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

### 4. Logs are fetched on every expand toggle — no caching

```typescript
function toggleExpand(batchId: string) {
    setExpandedBatch(batchId)
    setLogsLoading(true)
    api(`/api/admin/dispatch_ledger/${batchId}/logs`)
      .then(r => r.json())
      .then(data => setLogs(Array.isArray(data) ? data : []))
```

If the user expands, collapses, and re-expands the same row, it re-fetches the logs each time. For completed batches (whose logs won't change), this is unnecessary. A simple cache (`Record<string, LogEntry[]>`) keyed by `batch_id` would avoid the repeated fetches.

Low priority for an admin tool, but noticeable if the log list is large.

### 5. No result limit on `list_dispatch_ledger` or `list_log_entries`

Same issue as flagged on ast-285's `list_timesheets` — both functions return all matching rows with no LIMIT. The dispatch ledger will grow unbounded as the Dispatcher runs. The log table will grow even faster (many log entries per dispatch run). An unfiltered load could be very large.

The plan's use of `useSearchParams`-driven filters helps (users will likely filter), but the default unfiltered view on first load will fetch everything.

---

## Minor Notes

- **Reuses `timesheet-filters` CSS class.** The filters div uses `className="timesheet-filters"` rather than a dispatch-specific class. This works because the styling is identical, but it creates a hidden coupling — changing the timesheets filter layout would affect this page too. A shared `.admin-filters` class (or similar) would be cleaner.

- **`add_log_entry` doesn't use `_run_with_retry`.** Same as `add_timesheet_entry` — it's a fast write path with its own try/except. This is consistent with the timesheet pattern but differs from the dispatch ledger functions. The plan specified this pattern, so it's by design.

- **Duration sort uses string comparison on formatted values.** Sorting by the `_duration` column compares strings like `"3s"`, `"1m 30s"`, `"—"`. This won't sort correctly — `"3s"` > `"1m 30s"` lexicographically. Sorting should compare the underlying millisecond difference, not the formatted string.

- **`dispatch.py` core wrappers are pure passthroughs.** All three functions are `return _db_function(**kwargs)`. The module docstring explains this is for layering compliance. Clear and correct — the write-side wrappers (ast-282) will add actual logic.

---

## Summary

This is a clean, well-structured four-subissue feature that lands all the pieces called out in the plan. The logging handler design is particularly good — zero changes to existing callers, proper isolation via late import, contextvar for batch tagging. The main concern is **#1** (log volume/performance) — every log line now does a synchronous SQLite write, which will be noticeable during batch processing. A buffering strategy or level filter on the database handler would mitigate this. **#3** (React fragment key warning) is a quick fix. Everything else is minor.

---

## Review Fixes Applied

### Fix #1: Log buffering
`_DatabaseLogHandler` now buffers entries in a thread-safe list and flushes to SQLite every 50 entries instead of per-line. `flush_log_buffer()` exposed for Dispatcher to call at batch end. `atexit` handler registered for normal shutdown.

### Fix #2: Column whitelist on `update_dispatch_ledger`
Added `_LEDGER_UPDATE_COLS` set. `update_dispatch_ledger` raises `ValueError` if any key is not in the whitelist — catches typos before SQL execution.

### Fix #3: React Fragment key warning
Replaced `<>` with `<Fragment key={row.batch_id}>` (imported from React). Removed redundant `key` from inner `<tr>` elements.

### Fix #4: Log cache
Added `logCache: Record<string, LogEntry[]>` state. `toggleExpand` returns cached logs immediately if the batch has been fetched before, skipping the API call.

### Minor: CSS class rename
Renamed `.timesheet-filters` → `.admin-filters` in `App.css`, `AgentTimesheets.tsx`, and `PerformanceMonitor.tsx`. Both admin pages now share the class without naming coupling.

### Minor: Duration sort fix
Split `duration()` into `durationMs()` (returns raw ms) and `formatDuration()` (display string). Sort comparator now uses millisecond values so `1m 30s` correctly sorts after `3s`.

### Commit: `03bb089`
