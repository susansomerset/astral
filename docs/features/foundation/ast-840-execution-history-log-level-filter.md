# AST-840 — Execution History log level filter

**Linear:** [AST-840 — Execution History log level filter](https://linear.app/astralcareermatch/issue/AST-840/execution-history-log-level-filter-filter-execution-history-log-by)  
**Parent:** [AST-838 — Filter Execution History Log by Level](https://linear.app/astralcareermatch/issue/AST-838/filter-execution-history-log-by-level)  
**Publish ref:** `origin/sub/AST-838/AST-840-execution-history-log-level-filter`

Susan triages failed dispatch runs from Execution History (`/admin/performance`), but verbose INFO lines (especially long inflow_discovery debug runs) bury the ERROR and WARNING rows she needs. This ticket adds a URL-persisted **Level** filter to the page header so expanding any batch shows only log entries at the selected severity. The ledger table and `/api/admin/dispatch_ledger` fetch stay unchanged; filtering applies only to the expanded log viewer and to **Copy**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | **Level** filter control in filter bar; URL `log_level` param; pass filter into log viewer; client-side level filter, filtered-empty message, filtered **Copy** | ui |

**Out of scope (this ticket):** `src/ui/api/api_admin.py`, `src/core/dispatcher.py`, `src/data/database.py`, `App.css` (existing `.dispatch-log-level-*` classes suffice), backend log volume (AST-538), sibling **AST-841** inflow_discovery FAILED alignment, `tests/` / bible (Betty manifest below).

**QA manifest (Betty — not engineer commits):** Extend `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` with describe **`AST-840 log level filter`** covering: **Level** control renders with default **All**; URL `?log_level=ERROR` seeds the dropdown; expand batch with mixed severities shows only matching rows when **ERROR** selected; batch with logs but no ERROR rows shows `No 'ERROR' type log entries for this batch.` (not the zero-log message); ledger table still lists FAILED batch rows when **ERROR** selected (expand to see filtered-empty); **Copy** writes only filtered lines (mock clipboard assert). Regression: existing AST-532 / AST-634 / copy-toolbar describes still pass with default **All**.

## Stage 1: URL-backed Level filter control

**Done when:** Filter bar includes a **Level** dropdown with **All** (default), **DEBUG**, **INFO**, **WARNING**, **ERROR**; selection persists in the URL as `log_level=<LEVEL>` (absent or empty = **All**); changing Level does not alter ledger fetch query params or `FILTER_KEYS` ledger API filters.

1. In `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`, add a module-level constant immediately after `STATUSES` (~line 39):

   ```ts
   const LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"] as const
   ```

2. Do **not** add `log_level` to `FILTER_KEYS` — that array drives `/api/admin/dispatch_ledger` query params only. Level is a display filter for expanded logs.

3. Derive the active level filter from URL search params (same pattern as other filters):

   ```ts
   const logLevelFilter = searchParams.get("log_level") || ""
   ```

   Place this inside `PerformanceMonitor` after the `filters` `useMemo` (~line 143).

4. In the `.admin-filters` block (~line 289), insert a new **Level** control **after** the **Status** `<label>` and **before** the **From** date `<label>`:

   ```tsx
   <label>
     Level
     <select value={logLevelFilter} onChange={e => setFilter("log_level", e.target.value)}>
       <option value="">All</option>
       {LOG_LEVELS.map(level => (
         <option key={level} value={level}>{level}</option>
       ))}
     </select>
   </label>
   ```

5. Reuse existing `setFilter(key, value)` — it already updates `searchParams` with `{ replace: true }` and deletes the param when value is empty (**All**).

6. Manual verification before `code()`: local dev → Execution History → confirm `?log_level=WARNING` survives refresh; ledger network request URL must **not** include `log_level`.

⚠️ **Decision:** URL param name is `log_level` (parent AST-838 definition). Values are uppercase strings matching `LogEntry.level` as stored in `app_log` and rendered today (`ERROR`, `WARNING`, etc.) — filter compares with strict equality, no case normalization.

## Stage 2: Client-side log filtering, empty state, and filtered Copy

**Done when:** Expanding a batch shows only entries matching the selected level; batches with logs but none at the selected level show the explicit no-matching-level message; **Copy** exports only visible (filtered) lines; ledger row list, expand fetch, and `logCache` remain unfiltered full-batch payloads.

1. Update `LogViewer` props (~line 422) to accept the level filter:

   ```ts
   function LogViewer({
     logs,
     loading,
     logLevelFilter,
   }: {
     logs: LogEntry[]
     loading: boolean
     logLevelFilter: string
   })
   ```

2. At the top of `LogViewer`, add `useMemo` to the React import if not already present (file already imports `useMemo`).

3. Inside `LogViewer`, compute visible rows:

   ```ts
   const visibleLogs = useMemo(() => {
     if (!logLevelFilter) return logs
     return logs.filter(entry => entry.level === logLevelFilter)
   }, [logs, logLevelFilter])
   ```

4. Replace the early empty check (~line 426). Order matters:

   ```tsx
   if (loading) return <div className="dispatch-log-panel"><p className="list-page-status">Loading logs...</p></div>
   if (logs.length === 0) {
     return <div className="dispatch-log-panel"><p className="list-page-status">No log entries for this batch.</p></div>
   }
   if (visibleLogs.length === 0) {
     return (
       <div className="dispatch-log-panel">
         <p className="list-page-status">{`No '${logLevelFilter}' type log entries for this batch.`}</p>
       </div>
     )
   }
   ```

   ⚠️ **Decision:** When filtered-empty, omit the **Copy** toolbar — there is nothing to copy. Susan sees only the explicit message (parent AC #2).

5. Update `copyLogs` to map **`visibleLogs`**, not `logs`:

   ```ts
   const text = visibleLogs.map(e => `[${e.created_at}] ${e.level} ${e.logger_name}: ${e.message}`).join("\n")
   ```

6. Render table body from **`visibleLogs`** instead of `logs` (~line 453):

   ```tsx
   {visibleLogs.map(entry => (
   ```

7. In `PerformanceMonitor`, pass the filter into the expanded row (~line 398):

   ```tsx
   <LogViewer logs={logs} loading={logsLoading} logLevelFilter={logLevelFilter} />
   ```

8. Do **not** change `toggleExpand`, `logCache`, `/api/admin/dispatch_ledger/${batchId}/logs` fetch, ledger sorting, Skip Checks, candidate filter, or Agent Data modal.

9. Manual verification before `code()`: expand a batch with mixed INFO + ERROR → **Level = ERROR** shows ERROR rows only; **Copy** clipboard text contains no INFO lines; set **Level = ERROR** on a batch with only INFO logs → filtered-empty message (ledger row still visible in table); switch **Level** while expanded → view updates without refetch.

## Execution contract

Binding per **plan-child**: execute **Stage 1** then **Stage 2** in order; **one commit per stage** on epic worktree during **build-child**, publish each to **`origin/sub/AST-838/AST-840-execution-history-log-level-filter`**. Do not edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`. Do not edit backend files. On ambiguity — post **`🛑 Stage N blocked`** on **AST-838** parent; stop.

## Self-Assessment

**Scope:** `Single-Component` — one React page file (`AdminPerformanceMonitor.tsx`) for filter control, URL param, and log viewer filtering; no API or data-layer changes.

**Conf:** `high` — parent and child AC are explicit; existing `LogEntry.level`, log table CSS, and `setFilter` URL pattern are already in place on Execution History.

**Risk:** `low` — client-side display filter only; wrong filter logic would mislead triage but cannot affect dispatch execution, ledger queries, or log persistence.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Single `visibleLogs` memo; reuses `setFilter` and existing log panel markup — no duplicate fetch paths. |
| §2.1 config | No new config keys; level enum is UI-only constant matching stored log severities. |
| §2.4 batch | Not touched — no claim/process/release changes. |
| §2.6 state machine | Not touched. |
| §3.3 imports | Page stays in `src/ui/frontend`; no new cross-layer imports. |
| §3.5 naming | Follows existing `admin-filters` / `setFilter` / `dispatch-log-*` conventions. |

No conflicts requiring plan revision.

---

## Review (build)

**Built:** `origin/sub/AST-838/AST-840-execution-history-log-level-filter` @ `55852b20755a314212892f5e1dbcf264697bbf3a`

Stage 1: URL-backed **Level** filter control (`log_level` param, not in `FILTER_KEYS`).  
Stage 2: `LogViewer` client-side `visibleLogs` filter, filtered-empty message, filtered **Copy**.
