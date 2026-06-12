# AST-444 — Quickie: Execution History Today Filter and Skip Checks

**Linear:** https://linear.app/astralcareermatch/issue/AST-444/quickie-bugs-execution-history-today-filter-and-skip-checks  
**Feature ref:** `sub/AST-436/AST-444-quickie-bugs-execution-history-today-filter-and-skip-checks` (origin only)

Fix **Execution History** (`/admin/performance_monitor`): (a) first load shows **today** in candidate timezone without a flash of unfiltered history; (b) **Skip Checks** hides only **finished** all-zero batches while **RUNNING** all-zero batches stay visible.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | Default `date_from` in API filters before URL sync; fix Skip Checks filter for `RUNNING` | ui |

---

## Stage 1: Today filter on first fetch (no flash)

**Done when:** First API request to `/api/admin/dispatch_ledger` always includes `date_from` = today in candidate TZ, even before the URL `useEffect` runs.

1. In `AdminPerformanceMonitor.tsx`, update the `filters` `useMemo` (around lines 112–118):
   - After copying `FILTER_KEYS` from `searchParams`, if `f.date_from` is still unset, set `f.date_from = todayInTz(tz)`.
   - Add `tz` to the `useMemo` dependency array: `[searchParams, tz]`.

2. Keep the existing `useEffect` that writes `date_from` into `searchParams` when missing (so the date input shows today). No change to that effect’s behavior.

⚠️ **Decision:** Apply default **in `filters` for the API** rather than blocking render — avoids a second loading state while preserving URL sync for the date input.

---

## Stage 2: Skip Checks — keep RUNNING zero-count rows

**Done when:** With **Skip Checks** on (default), finished batches with all count columns zero are hidden; `RUNNING` batches with all zeros remain visible with status **RUNNING**.

1. In the `filtered` `useMemo` (lines 156–159), replace the filter body with:

```typescript
if (!skipChecks) return rows
return rows.filter(r => {
  const allZero =
    (r.total_processed ?? 0) === 0 &&
    (r.total_passed ?? 0) === 0 &&
    (r.total_failed ?? 0) === 0 &&
    (r.total_errors ?? 0) === 0
  if (!allZero) return true
  return r.status === "RUNNING"
})
```

2. Do **not** change ledger API routes or query params.

---

## Stage 3: Verify

**Done when:** TypeScript compiles; acceptance criteria 4–8 satisfied manually.

1. `cd src/ui/frontend && npx tsc -b --noEmit`
2. Cold load Execution History with a candidate TZ set → only today’s batches (no full-history flash).
3. Widen From/To dates → wider set appears.
4. With Skip Checks on: hide completed all-zero row; show RUNNING all-zero row.
5. Skip Checks off → finished all-zero rows visible again.

---

## Self-Assessment

**Scope:** `scope-Single-Component` — `AdminPerformanceMonitor.tsx` only.

**Conf:** `conf-high` — Root cause identified in ticket notes (fetch race + filter ignores status).

**Risk:** `risk-low` — UI filtering and default query param only; ledger API unchanged.

---

## Resolution (resolve-astral 2026-05-22)

- **fix-now:** none.
- **discuss:** none.
- Radia review 2026-05-22: approve. No product changes on resolve pass.
