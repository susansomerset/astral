<!-- linear-archive: AST-1979 archived 2026-10-08 -->

## Linear archive (AST-1979)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1979/created-column-on-jobs-list-tables-add-created-to-the-job-list-table  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1971 — Add Created to the job list table  
**Blocked by / blocks / related:** parent: AST-1971

### Description

## What this implements

Adds the sortable Created column (job `created_at`, left of Updated / Failed At, default sort unchanged) to every job table on Ready, Review, Processing, Skipped, and Applied. Each page extends its own existing sorter. Does not touch Meteorites (#2), any backend route, or config.

## Citations

none — every file is under `src/ui/frontend/`, outside both statutes' territory.

## Scope

`src/ui/frontend/src/pages/JobsRecommended.tsx` (Created header + cell; `created_at` branch in `sortRecommendedJobs`; column-count arithmetic); `src/ui/frontend/src/pages/JobsProcessing.tsx` (Created header + cell; `created_at` branch in its existing sorter); `src/ui/frontend/src/pages/JobsSkipped.tsx` (Created header + cell in both table variants; `created_at` branch in `sortJobs`); `src/ui/frontend/src/pages/JobsApplied.tsx` (Created header + cell; `created_at` branch in `sortAppliedJobs`). All four add the optional `created_at` field to the page's `Job` interface.

## Acceptance criteria

1. **Column present on job lists.** On Ready, Review, Processing, Skipped (regular and below-floor tables), and Applied, every job table's header row contains a `Created` header immediately left of `Updated` (or `Failed At`). **Fail:** any in-scope table without it, or in a different position.
2. **Value is the job's** `created_at`**.** For any row on those pages, the Created cell text equals `fmtTime(created_at, <candidate tz>)` for that job's `created_at` in the `GET /api/jobs?view=<page view>&candidate_id=X` response. A row whose `created_at` is null shows `—`. **Fail:** a cell showing `state_changed_at` / `updated_at`, a blank cell, or a timezone different from the Updated cell's.
3. **Sorts by creation time.** Clicking `Created` once orders that table's rows by `created_at` with the same direction rule the Updated header uses on first click. Clicking again reverses it, and the sort indicator shows on Created. Null `created_at` rows are placed the same way Updated places null `state_changed_at`. **Fail:** any out-of-order pair, no reversal, or the indicator on another header.
4. **Default sort unchanged.** On first load, each job list table is still sorted by `state_changed_at` descending, with the indicator on Updated / Failed At. **Fail:** the default switches to Created or anything else.
5. **Extends existing sorters, no parallel path.** `rg -n "function sort" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/pages/JobsProcessing.tsx src/ui/frontend/src/pages/JobsSkipped.tsx src/ui/frontend/src/pages/JobsApplied.tsx` returns the same count as on `origin/dev` at branch point, and each file's `"created_at"` sort comparison sits inside that existing function. **Fail:** a new sorter function, or a sort for Created implemented outside the page's existing sorter.
6. **Builds clean; no new lint (frontend half).** In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem that is absent on `origin/dev` (diff the problem lists). **Fail:** a non-zero exit, or any new lint problem.

## Boundaries

Does **not** touch Jobs → Meteorites, `JobsMeteorites.tsx`, `src/data/**`, `src/ui/api/**`, or `src/utils/config.py`. Those belong to sibling #2 (Meteorites Created from landed job). No new shared sort helper; no change to default sorts.

## Notes for planning

No backend change is needed: `database.list_jobs` selects `SELECT * FROM job`, so every `GET /api/jobs?view=…` row already carries `created_at`, including Skipped's below-floor virtual rows. Format the cell with the existing `<Time>` component, as the Updated cell does. Citations: none.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1971-created-col`, child `sub/AST-1971/AST-1979-created-col`. Created at dispatch-parent. Resolve with `epic_registry.py show AST-1971`.

### Comments

#### radia — 2026-10-04T21:06:00.437Z
[code-rubric] PROCEED (Commit: 7a4f7760e) Four pages match AC

#### betty — 2026-10-04T21:03:19.419Z
`origin/sub/AST-1971/AST-1979-created-col` @ `7a4f7760e` · Created column tests ready

#### joan — 2026-10-04T20:55:11.134Z
[plan-rubric] PROCEED (Commit: bb2506916) Four-page Created column

#### ada — 2026-10-04T20:53:47.085Z
`origin/sub/AST-1971/AST-1979-created-col` @ `bb2506916` · plan ready, four pages

---

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

## Review

- **Branch:** `origin/sub/AST-1971/AST-1979-created-col`
- **Build commits:** `c08d5b436` (Stage 1 Created column + `created_at` sort on all four pages)
- **Build notes:** `npx tsc -b --noEmit` and `npm run build` exit 0. `npm run lint` reports 31 problems before and after, and the line:col-stripped diff is empty, so nothing is new. `rg -c "function sort"` is still `2` per file. Each `"created_at"` comparison sits inside the page's existing sorter (Recommended:62, Processing:96, Skipped:102, Applied:32). `git diff --stat origin/dev` lists only the four pages + this doc.
- **Deviation:** none.
- **For QA:** no backend change; `created_at` comes from the existing `GET /api/jobs?view=…` rows. Skipped's one Created header/cell serves both `isFloor` variants. No manual browser smoke run in this headless build.

## Joan validate

```text
[plan-rubric]
**Ticket:** AST-1979
**Overall:** APPROVED
**Corpus:** e1f2699fad
**Publish ref:** bb2506916ea1a29936a1bfe4c9ae47838742fc21

## Canon scores
(no ids on frozen list — intentional per child Citations: none; parent logging statutes belong to sibling #2)

## Traceability
AC 1–6 → Stage 1 (steps 4–24) + ## Acceptance mapping; parent AC 6–10 N/A (Meteorites / backend — AST-1971 #2).

### Findings

**acceptable** · Plan doc · Execution contract + stop template on parent AST-1971 if anchors drift — appropriate for cross-child baseline risk.

**discuss** · Canon Scope · Parent epic lists `stat.logging.error` / `stat.logging.info.api`; this child correctly carries none. If Archie wants every frontend ticket to cite `astral.standards.in-scope-only` by default, amend at Discussion — not scored here.

**discuss** · R6 DRY · Four parallel `created_at` branches duplicate the `state_changed_at` pattern by design (ticket **Boundaries** forbid a shared helper); acceptable tradeoff for this slice.

context_tokens≈22000
```

## Radia review

[code-rubric]
**Ticket:** AST-1979
**Publish ref:** `7a4f7760eca2179e355e4e712c1f0ecfc9d81a32` (`origin/sub/AST-1971/AST-1979-created-col`)
**Corpus:** e1f2699fad
**Overall:** CLEAN

## Canon scores

(no ids on frozen list — intentional per child **Citations: none**; parent `stat.logging.*` belongs to sibling AST-1971 #2)

## Column diff vs plan stage

(aligned) — Joan also recorded no directive rows; plan APPROVED against the same empty frozen list.

## Frame diff

(none)

### Findings

**advisory** · `tests/**` + `docs/test-bible/**` · **sibling test carry:** `merge-tests(AST-1979)` on tip includes **AST-1978** artifacts from `origin/tests`: `tests/component/ui/api/test_api_admin.py` (`TestAst1978ResponseSchemaCount`), `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` (RSC header case), `docs/test-bible/ui/api/api_admin.md` (§ AST-1978). Expected per qa-child merge-tests; no product scope in `src/**` beyond the four Jobs pages.

**advisory** · Issue doc `## Review` · Build notes still describe `git diff --stat origin/dev` as “four pages + this doc” only; tip also carries Betty’s AST-1979 test/bible commits and the AST-1978 carry above. Metadata drift only — product delivery matches plan Stage 1.

**advisory** · Canon Scope · Parent epic cites logging statutes; this child deliberately carries **Citations: none** (frontend-only). Joan flagged optional future default `astral.standards.in-scope-only` at Discussion — not a review-time scope gap because Discussion locked “none” with rationale.

### What's solid

- **Product diff** is exactly the four in-scope pages: optional `created_at` on `Job`, sibling `created_at` sort branch to `state_changed_at`, Created `<th>`/`<td>` immediately left of Updated / Failed At, Recommended `columnCount` 9 + phase columns, cells use `<Time value={job.created_at} />` (Skipped keeps per-cell `setViewingId` on the new cell).
- **AC 5:** sort helpers extended in place; no new `function sort` entries.
- **AC 3–4:** defaults untouched (`state_changed_at` desc); null `created_at` uses `|| ""` parity with Updated.
- **Tests:** shared `created-column.ts` exercises AC 1–4 on Ready/Review (both routes), Processing, Skipped (below-floor + regular), Applied; Tokyo tz proves fmt/timezone; Applied asserts `Updated▼` at load where sort state is seeded.
- **Estimate 2** still matches footprint (four page files + focused component tests).

### Recommended actions (downstream — not for Radia)

- Chuckles: append this artifact to `docs/features/interface/ast-1979-created-column-on-jobs-list-tables.md`, commit `docs(AST-1979): Radia review — clean`, push publish ref, post slim upshot `--as radia`, move **Review Posted** → **PROCEED** path (no `resolve-child` unless datt routes otherwise).
- Optional doc touch: refresh `## Review` on the issue doc to mention tip `7a4f7760e` and QA manifest (six AST-1979 cases).

context_tokens≈38000
