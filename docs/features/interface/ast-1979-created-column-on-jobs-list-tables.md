# AST-1979 — Created column on Jobs list tables

- **Linear:** [AST-1979](https://linear.app/astralcareermatch/issue/AST-1979) · parent [AST-1971](https://linear.app/astralcareermatch/issue/AST-1971) (Add Created to the job list table)
- **Publish ref:** `origin/sub/AST-1971/AST-1979-created-col`
- **Canon Scope (this child):** none — every file is under `src/ui/frontend/`, outside `stat.logging.error` / `stat.logging.info.api` territory.

Every job-row table on Ready, Review (both rendered by `JobsRecommended.tsx` — `routes.tsx` lines 90–91), Processing, Skipped (regular + below-floor variants), and Applied gains a sortable **Created** column showing the job's `created_at`, placed immediately left of **Updated** / **Failed At**. No backend change: `GET /api/jobs?view=…` rows already carry `created_at`. Each page extends its own existing sorter with one `created_at` branch that copies the `state_changed_at` branch's string-compare / null handling. Default sort (`state_changed_at` desc) is untouched. Meteorites and all backend/config files belong to sibling AST-1971 #2 and are not touched here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | `created_at` on `Job`; `created_at` branch in `sortRecommendedJobs`; Created `<th>` + `<td>`; `columnCount` 8 → 9 | ui/frontend |
| `src/ui/frontend/src/pages/JobsProcessing.tsx` | `created_at` on `Job`; `created_at` branch in `sortJobs`; Created `<th>` + `<td>` | ui/frontend |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | `created_at` on `Job`; `created_at` branch in `sortJobs`; Created `<th>` + `<td>` (one shared header/cell serves both `isFloor` variants) | ui/frontend |
| `src/ui/frontend/src/pages/JobsApplied.tsx` | `created_at` on `Job`; `created_at` branch in `sortAppliedJobs`; Created `<th>` + `<td>` | ui/frontend |

No other file. `JobsMeteorites.tsx`, `src/data/**`, `src/ui/api/**`, `src/utils/config.py`, `src/ui/frontend/src/components/Time.tsx`, `src/ui/frontend/src/lib/fmt.ts` are **not** edited. `debug/spikes/ast-1979/*` lint logs are gitignored scratch (`.gitignore:34 debug/*`), never committed.

⚠️ **Decision (applies to every page):** the sort branch is the literal sibling of the existing `state_changed_at` branch — `cmp = (a.created_at || "").localeCompare(b.created_at || "")`. That makes null `created_at` behave exactly as null `state_changed_at` does (empty string: first ascending, last descending), satisfying AC 3 without new null logic. No shared helper (ticket Boundaries).

⚠️ **Decision (applies to every page):** the cell is `<Time value={job.created_at} />`, the same component the Updated cell uses. `Time` → `fmtTime(value, candidateTz)` already renders `—` for null/undefined and uses the selected candidate's timezone, so AC 2 (format, `—`, same tz as Updated) holds by construction.

⚠️ **Decision (applies to every page):** no change to `handleSort`, `sortIndicator`, or any `useState` / `?? { col: "state_changed_at", asc: false }` default. First click on Created therefore follows the same rule as any header not currently active (`asc: true`), the second click reverses, and the default sort stays on Updated (AC 3, AC 4).

## Stage 1: Created column on all four job list pages

**Done when:** On Ready, Review, Processing, Skipped (both tables), and Applied, a sortable `Created` header sits immediately left of `Updated` / `Failed At`, its cells show `fmtTime(created_at, tz)` (or `—`), clicking it sorts by `created_at` and toggles, the default load is still sorted by Updated desc, and `npm run build` passes with no new lint problems vs `origin/dev`.

### Baseline (before any edit)

1. `cd src/ui/frontend && npm ci` (worktree has no `node_modules`; `package-lock.json` present — installs the locked tree, adds no dependency).
2. From `src/ui/frontend`: `mkdir -p ../../../debug/spikes/ast-1979 && npm run lint > ../../../debug/spikes/ast-1979/lint-before.txt 2>&1; true`.
3. From repo root: `rg -c "function sort" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/pages/JobsProcessing.tsx src/ui/frontend/src/pages/JobsSkipped.tsx src/ui/frontend/src/pages/JobsApplied.tsx` — expected baseline `2` per file (the page sorter + `sortIndicator`), 8 total. If it differs, stop and comment (drift).

### `JobsRecommended.tsx`

4. In `interface Job`, insert `created_at?: string | null` on the line immediately after `state_changed_at: string | null`.
5. In `sortRecommendedJobs`, immediately after the branch
   ```
   } else if (col === "state_changed_at") {
     cmp = (a.state_changed_at || "").localeCompare(b.state_changed_at || "")
   ```
   insert:
   ```
   } else if (col === "created_at") {
     cmp = (a.created_at || "").localeCompare(b.created_at || "")
   ```
6. Replace the `columnCount` comment + line inside `sections.map`:
   - from `// checkbox + actions + title + company + source + state + phase cols + total + updated` / `const columnCount = 8 + manifest.jobs.recommended.phase_score_columns.length`
   - to `// checkbox + actions + title + company + source + state + phase cols + total + created + updated` / `const columnCount = 9 + manifest.jobs.recommended.phase_score_columns.length`
7. In `<thead>`, immediately **before** the `<th className="sortable" onClick={() => handleSort(sec.state, "state_changed_at")}>` element (i.e. after the `Total` `<th>`), insert:
   ```
   <th className="sortable" onClick={() => handleSort(sec.state, "created_at")}>
     Created{sortIndicator(sec.state, "created_at")}
   </th>
   ```
8. In the main row `<tr className="clickable" …>`, immediately **before** `<td><Time value={job.state_changed_at} /></td>`, insert `<td><Time value={job.created_at} /></td>`.

### `JobsProcessing.tsx`

9. In `interface Job`, insert `created_at?: string | null` immediately after `state_changed_at: string | null`.
10. In `sortJobs`, immediately after the `col === "state_changed_at"` branch, insert the same `created_at` branch as step 5.
11. In `<thead>`, immediately **before** `<th className="sortable" onClick={() => handleSort(sortKey, "state_changed_at")}>` (after the `{showScore && (…)}` Score header), insert:
    ```
    <th className="sortable" onClick={() => handleSort(sortKey, "created_at")}>
      Created{sortIndicator(sortKey, "created_at")}
    </th>
    ```
12. In the row, immediately **before** `<td><Time value={job.state_changed_at} /></td>`, insert `<td><Time value={job.created_at} /></td>` (row-level `onClick` already opens the job; no cell handler).

### `JobsSkipped.tsx`

13. In `interface Job`, insert `created_at?: string | null` immediately after `state_changed_at: string | null`.
14. In `sortJobs`, immediately after the `col === "state_changed_at"` branch, insert the same `created_at` branch as step 5.
15. In `<thead>`, immediately **before** the `<th className="sortable" onClick={() => handleSort(sortKey, "state_changed_at")}>` element whose label is `{isFloor ? "Updated" : "Failed At"}`, insert (unconditional — it renders in both the regular and below-floor variants, which share this one `<thead>`):
    ```
    <th className="sortable" onClick={() => handleSort(sortKey, "created_at")}>
      Created{sortIndicator(sortKey, "created_at")}
    </th>
    ```
16. In the row, immediately **before** `<td onClick={() => setViewingId(job.astral_job_id)}><Time value={job.state_changed_at} /></td>`, insert `<td onClick={() => setViewingId(job.astral_job_id)}><Time value={job.created_at} /></td>` (matches the per-cell click-to-open pattern of its neighbours; no `colSpan` exists in this file).

### `JobsApplied.tsx`

17. In `interface Job`, insert `created_at?: string | null` immediately after `state_changed_at: string | null`.
18. In `sortAppliedJobs`, immediately after the `col === "state_changed_at"` branch, insert the same `created_at` branch as step 5.
19. In `<thead>`, immediately **before** `<th className="sortable" onClick={() => handleSort("state_changed_at")}>`, insert:
    ```
    <th className="sortable" onClick={() => handleSort("created_at")}>
      Created{sortIndicator("created_at")}
    </th>
    ```
20. In the row, immediately **before** `<td><Time value={job.state_changed_at} /></td>`, insert `<td><Time value={job.created_at} /></td>`.

### Verify, then commit

21. From `src/ui/frontend`: `npx tsc -b --noEmit` exits 0 (build-child §7).
22. From `src/ui/frontend`: `npm run build` exits 0 (AC 6).
23. From `src/ui/frontend`: `npm run lint > ../../../debug/spikes/ast-1979/lint-after.txt 2>&1; true`, then `diff <(rg -o '^\s+\d+:\d+\s+\S+\s+.*$' ../../../debug/spikes/ast-1979/lint-before.txt | sed -E 's/^\s+[0-9]+:[0-9]+//' | sort) <(rg -o '^\s+\d+:\d+\s+\S+\s+.*$' ../../../debug/spikes/ast-1979/lint-after.txt | sed -E 's/^\s+[0-9]+:[0-9]+//' | sort)` — any line prefixed `>` is a new problem; fix it before committing (line:col stripped so shifted line numbers don't count as new).
24. Re-run step 3: still `2` per file / 8 total, and `rg -n '"created_at"' src/ui/frontend/src/pages/Jobs{Recommended,Processing,Skipped,Applied}.tsx` shows each file's sort comparison line between its sorter's opening `return [...jobs].sort(` and closing `})` (AC 5).
25. `git diff --stat origin/dev` lists only the four page files plus this plan doc.
26. `git add` the four page files; `git commit -m "code(AST-1979): Created column + created_at sort on Ready/Review/Processing/Skipped/Applied"`; `git push origin HEAD:sub/AST-1971/AST-1979-created-col`.

## Acceptance mapping

| AC | Satisfied by |
|----|--------------|
| 1 Column present, left of Updated / Failed At | steps 7, 11, 15, 19 |
| 2 Value = `fmtTime(created_at, tz)`, `—` on null | steps 8, 12, 16, 20 (`<Time>`) |
| 3 Sorts by creation time, toggles, indicator, null parity | steps 5, 10, 14, 18 + unchanged `handleSort` / `sortIndicator` |
| 4 Default sort unchanged | no edit to any default `SortState` |
| 5 Extends existing sorters only | steps 3, 24 |
| 6 Build clean, no new lint | steps 21–23 |

## Execution contract

Binding as written. Steps in order; no added files, helpers, or dependencies. If a quoted anchor line is missing or differs from what is quoted here, stop and post on [AST-1971](https://linear.app/astralcareermatch/issue/AST-1971):

```
🛑 Stage 1 blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

## Estimate

Confirm Chuckles estimate: 2 — agree
