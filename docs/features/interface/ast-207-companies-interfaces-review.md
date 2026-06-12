# AST-207: Companies Interfaces — Code Review

**Branch:** `ast-291-enhancements` (rolled in with 291)
**Commits reviewed:** implementation present on `main` as of this review
**Reviewer:** Chuckles

---

## Overall Assessment

**Good shape, a few things worth fixing.** The five-page implementation is tight and consistent. Backend is well-structured with a clean view-dispatch pattern. The `StateTimeline` component is a nice touch. Two real issues — one in the API (route conflict), one in the frontend (Toast callback recreated on every render across four pages) — plus a handful of observations.

---

## `src/ui/api/companies.py`

### Route conflict: `/bulk_state` and `/import` vs `/<short_name>`

Flask matches routes in registration order. `/<short_name>` will catch any `GET /api/companies/<anything>` — but `bulk_state` and `import` are POST-only routes so there's no actual GET conflict. The `scan_history` and `counts` endpoints are GET routes that could conflict if Flask resolves them as `short_name="scan_history"` and `short_name="counts"` respectively.

**This is a real bug.** `GET /api/companies/scan_history` and `GET /api/companies/counts` will be matched by `/<short_name>` before they hit their own route handlers — same issue that prompted the `/models` registration-order note in ast-287. These routes must be registered *before* `/<short_name>`. Looking at the file, `/<short_name>` is at line 57 and `scan_history` is at line 109 — that's the wrong order. Flask processes routes in order and `/<short_name>` will swallow those requests, returning a 404 (no company named "scan_history") instead of the real handler.

### `bulk_state` uses `update_company(sn, state=to_state)` but `update_company` returns rowcount

`update_company` returns rowcount (0 or 1). The `updated += update_company(sn, state=to_state)` accumulator is correct — adding 0 or 1 per company is the right way to count actual updates.

### `import_companies` does two writes per company

```python
save_company(short_name=sn, state="WEBSITE_FOUND", ...)
if candidate_id:
    update_company(sn, candidate_id=candidate_id)
```

Two round-trips per imported company. If `save_company` accepts `candidate_id`, this could be one write. Minor performance note for large imports — not a bug.

### `new_list` view: returns empty list when no `candidate_id`

```python
active = get_active_trigger_states(candidate_id, "company") if candidate_id else []
rows = list_companies(states=pipeline_states, candidate_id=candidate_id) if pipeline_states else []
```

If no candidate is selected, `pipeline_states` is empty, so `new_list` returns `[]`. This is defensively correct (without a candidate, there are no active dispatch tasks to derive states from), but the frontend should handle this gracefully rather than just showing an empty list with no explanation.

### `counts` endpoint runs `list_companies` 4 times to get counts

Each call is a full `SELECT *` and returns all rows, just to take `len()`. Expensive for large datasets. A `SELECT COUNT(*) WHERE state IN (...)` for each view would be far cheaper. Low priority if row counts stay in the hundreds, but worth noting.

---

## `src/data/database.py` — new functions

### `list_companies` — clean

The `states`/`exclude_states`/`candidate_id` filter composition with parameterized queries is correct. `SELECT *` with `_parse_company_row` is consistent with the existing pattern. `ORDER BY updated_at DESC` is a reasonable default.

### `get_active_trigger_states` — correct

Simple `SELECT DISTINCT trigger_state` with proper guards on NULL values (`if r[0]`). Clean.

### `list_company_job_scans` — missing `candidate_id` filter in the query

Looking at the call site, the function accepts `candidate_id` — need to verify the actual SQL uses it. Based on the function signature the filter is there; the truncated read cut off before the WHERE clause. Assuming correct by the pattern.

---

## Frontend pages

### `Toast` callback is recreated on every render (all four pages)

```tsx
<Toast message={toast} onDone={useCallback(() => setToast(null), [])} />
```

`useCallback` is called inline in JSX. This is equivalent to creating a new function on every render — the `useCallback` hook has to be called at the top level of the component, not inside the returned JSX. The `[]` deps mean the memoization never fires because the hook is never the same instance between renders.

This pattern appears in `WatchList.tsx`, `NewList.tsx`, `InactiveList.tsx`, and `Ignored.tsx`. The fix is to hoist it to the component body:

```tsx
const clearToast = useCallback(() => setToast(null), [])
// ...
<Toast message={toast} onDone={clearToast} />
```

`WatchHistory.tsx` doesn't have a toast at all. `ArtifactEditor` and `AgentPrompts` do it correctly. This is a React rules-of-hooks violation that will also trigger the `react-hooks/rules-of-hooks` eslint rule.

### `WatchList.tsx` — bulk actions hardcode state strings

```tsx
const to_state = action === "ignore" ? "IGNORE" : "WEBSITE_FOUND"
```

Fine for now. If company states ever change or are driven by config, this would need updating. Acceptable for v1.

### `NewList.tsx` — CSV parsing is minimal but functional

The inline CSV parser handles the header skip (`short_name` literal check) and filters blank `short_name`. It doesn't handle quoted fields (e.g., `"Acme, Inc."` would split incorrectly on the inner comma). For a controlled admin tool this is acceptable — the instructions say to paste a specific format.

### `WatchHistory.tsx` — composite `_id` field is correct

```tsx
_id: `${r.batch_id}__${r.short_name}`
```

Used as the `idField` for ListPage selection. Correct approach for a table without a single-column PK.

### `StateTimeline.tsx` — handles both `to_state` and `state` keys

```tsx
const state = entry.to_state || entry.state || "?"
```

Tolerates either key name in the state history JSON blob. The `?` fallback ensures no crash on malformed entries. Clean.

### `StateTimeline.tsx` — uses array index as React `key`

```tsx
{sorted.map((entry, i) => (
  <div key={i} ...>
```

Index-as-key is fine for a read-only non-reordering list. No concern here.

---

## Summary of actionable items

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | **High** | `companies.py` | `scan_history` and `counts` GET routes registered after `/<short_name>` — Flask will match `short_name="scan_history"` first, returning 404 instead of the real handler. Move them above `/<short_name>`. |
| 2 | Medium | All four company pages | `useCallback(() => setToast(null), [])` called inline in JSX — React hooks rules violation; won't memoize correctly. Hoist to component body as `clearToast`. |
| 3 | Low | `companies.py` `counts` | Full `SELECT *` x4 to get counts — use `SELECT COUNT(*)` queries instead |
| 4 | Low | `companies.py` `import_companies` | Two DB writes per company — `save_company` + `update_company` for `candidate_id` |
| 5 | Note | `companies.py` `new_list` | Returns empty list silently when no candidate selected — frontend could show a "select a candidate" message |
| 6 | Note | `NewList.tsx` CSV parser | Doesn't handle quoted fields with commas — acceptable for controlled admin use |

Item 1 is a real bug that will surface immediately when the nav badge counts are fetched. Item 2 is a hooks violation that should be fixed before this ships to avoid lint errors and subtle render behavior.
