<!-- linear-archive: AST-1968 archived 2026-10-08 -->

## Linear archive (AST-1968)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1968/recommended-list-triage-upgrades-updates-to-the-recommended-jobs-list  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 5  
**Parent:** AST-1967 — Updates to the recommended jobs list page  
**Blocked by / blocks / related:** parent: AST-1967

### Description

## What this implements

Delivers all four capabilities: row Generate Artifacts, multi-select bulk Skip / Applied / Generate Artifacts, the default-on Analysis toggle with letterless four-phase grade lines, and the sortable Total column. Does not touch the Job Analysis Report modal's behaviour or any backend route.

## Citations

none — no in-force directive governs frontend list pages; see Architectural definition.

## Scope

`src/ui/frontend/src/pages/JobsRecommended.tsx` (selection + bulk bar, row Generate wiring, Analysis toggle + expanded lines from `report_phase_tabs`, Total column via `sortRecommendedJobs`); `src/ui/frontend/src/components/CandidateJobRowActions.tsx` (optional Generate `icon-control`); `src/ui/frontend/src/lib/candidateJobActions.ts` (generate-artifacts POST helper); `src/ui/frontend/src/hooks/useCandidateJobActions.ts` (generate + multi-job skip/applied, one notes confirm over many ids); `src/ui/frontend/src/lib/recommendedJobReport.tsx` (letterless, confidence-free phase row sharing the modal's column/order/lookup helper); `src/ui/frontend/src/App.css` (letterless dot modifier + expanded-line layout).

## Acceptance criteria

 1. **Row Generate shows only where legal.** On Recommended, every row in the Recommended section has a button with `title="Generate Artifacts"`; no row in In Progress or Ready does. **Fail:** button missing on a `RECOMMENDED` row, or present on a `BUILD_ARTIFACTS` / `CANDIDATE_REVIEW` row.
 2. **Row Generate starts the build.** Clicking it on a `RECOMMENDED` row sends `POST /api/jobs/<id>/generate_artifacts` (200), and after refresh that job is listed under In Progress. **Fail:** no request, non-200, or job still under Recommended.
 3. **One client call site for generate.** `rg -n "generate_artifacts" src/ui/frontend/src/lib/candidateJobActions.ts` returns a hit; `rg -n "/generate_artifacts" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/components/CandidateJobRowActions.tsx` returns nothing. **Fail:** an inline fetch in the page or component (a parallel path instead of the shared helper).
 4. **Bulk bar appears with selection.** With zero rows checked, no bulk buttons render. Checking 3 rows shows `Skip (3)`, `Applied (3)`, and `Generate Artifacts (n)` in the header, where n = number of checked `RECOMMENDED` jobs. **Fail:** bar visible with nothing selected, wrong counts, or a section without checkboxes.
 5. **Bulk Skip.** Select 2 Recommended + 1 Ready job, then click Skip. All 3 disappear from Recommended and appear on the Skipped page as `CANDIDATE_SKIPPED`. The toast reads 3 succeeded. **Fail:** any of the 3 still on Recommended.
 6. **Bulk Applied, one prompt.** Select 2 jobs, click Applied, enter note `bulk-test`, confirm. Exactly one notes modal opened, and both jobs appear on the Applied page with their applied note = `bulk-test`. **Fail:** a modal per job, a job not moved, or a note missing on either.
 7. **Bulk Generate skips ineligible jobs.** Select 1 Recommended + 1 Ready job, click Generate Artifacts. The network log shows exactly one `POST …/generate_artifacts`, for the Recommended job only. The Ready job's state is unchanged. **Fail:** a POST for the Ready job, or a 409 error toast caused by sending it.
 8. **Selection clears.** After any bulk action completes, every checkbox is unchecked and the bulk bar is gone. **Fail:** any box still checked.
 9. **Toggle defaults on.** On first load, the Analysis toggle is on and each job row is followed by an expanded area with exactly four labelled lines in order JD, DO, GET, LIKE. Toggling off removes every expanded area (`tbody tr` count = job count). **Fail:** toggle off at load, wrong line count/order, or expanded rows remaining when off.
10. **Circles: no letters, no confidence.** With the toggle on, every grade circle inside the list has empty text content, and the list contains zero `ConfidenceBullets` elements. **Fail:** any visible letter or confidence bullet in a list row.
11. **Circles match the modal.** For any job, each phase line's circle count, colours, and left-to-right order equal the grade circles in that phase's section of the modal's Analysis tab for the same job. **Fail:** any count, colour, or order mismatch.
12. **No copied grade logic.** The new builder and `buildPhaseSectionGradeConfidenceRow` share one internal column/order/lookup helper in `recommendedJobReport.tsx`. Neither `JobsRecommended.tsx` nor the builder calls `sortRubricColumnsByImportanceAndGrade` on its own. `rg -n "sortRubricColumnsByImportanceAndGrade" src/ui/frontend/src/lib/recommendedJobReport.tsx` returns exactly one call site. **Fail:** two independent copies of the ordering.
13. **Total value.** A job with JD 7.0, DO 6.5, GET 8.0, LIKE 5.5 shows Total `27.0`. A job missing any one phase score shows `—`. **Fail:** any other value.
14. **Total sorts like the phase columns.** Clicking Total toggles ascending/descending with the same placement of `—` rows that the JD column uses. `rg -n "function sortRecommendedJobs" src/ui/frontend/src/pages/JobsRecommended.tsx` returns exactly one hit (Total sorts through it). **Fail:** wrong order, or a second sort function.
15. **Other pages unaffected.** Skipped, Applied, and In Review row actions render the same as before (no Generate button) because they don't pass the new callback. **Fail:** Generate shows on any other page.
16. **Builds clean; no new lint.** In `src/ui/frontend`, `npm run build` exits 0. `npm run lint` reports no problem that is absent on `origin/dev` (diff the problem lists), and the baseline `react-hooks/set-state-in-effect` error at `JobsRecommended.tsx` (the `actions.error` → toast effect) is gone (per AST-1969). **Fail:** build non-zero, any new lint problem, or that baseline error still reported.

## Boundaries

Single child — owns the whole epic. Does not change Job Analysis Report modal behaviour or any backend / API route / `src/utils/config.py`.

## Notes for planning

Canon Scope empty (no in-force directive governs frontend list pages). Bulk actions fan out over existing per-job endpoints. Parent Technical scope has the function-level detail.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`,
child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-04T14:46:26.449Z
[code-rubric] PROCEED (Commit: 0970ea6973c7945a9853c73fcfd97cf89d5e1dc7) Empty canon; plan delivered

#### betty — 2026-10-04T14:43:39.946Z
`origin/sub/AST-1967/AST-1968-recommended-list-triage-upgrades` @ `0970ea697` · manifest in pages.md

#### joan — 2026-10-04T12:28:48.978Z
[plan-rubric] PROCEED (Commit: 5c00918) six-stage triage plan

#### ada — 2026-10-04T12:27:09.090Z
`origin/sub/AST-1967/AST-1968-recommended-list-triage-upgrades` @ `5c00918ee` · six-stage plan ready

---

# AST-1968 — Recommended list triage upgrades

- **Parent:** [AST-1967 — Updates to the recommended jobs list page](https://linear.app/astralcareermatch/issue/AST-1967)
- **Ticket:** [AST-1968](https://linear.app/astralcareermatch/issue/AST-1968)
- **Publish ref:** `origin/sub/AST-1967/AST-1968-recommended-list-triage-upgrades`
- **Canon Scope:** empty (locked at Discussion — no in-force directive governs frontend list pages).

Brings the Job Analysis Report's signals and actions onto the Recommended list so the
candidate can triage many jobs without opening each report: a per-row Generate Artifacts
icon (only where the manifest allows it), multi-select with bulk Skip / Applied / Generate
Artifacts, a default-on Analysis toggle that renders four letterless grade-circle lines
(JD, DO, GET, LIKE) under each row using the same column/order/lookup as the modal, and a
sortable Total column (sum of the four phase scores). Frontend only — no backend route,
no `src/utils/config.py`, no modal behaviour change.

## Explicit scope gate

Every file below is named in this ticket's `## Scope`. Every function-level change is the
kind that Scope / parent Technical scope describes for that file. No gaps found.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/candidateJobActions.ts` | Add `postGenerateArtifacts(astralJobId)` | ui/lib |
| `src/ui/frontend/src/hooks/useCandidateJobActions.ts` | Add optional `onBulkDone` param, `BulkActionResult` type, `generateJob`, `skipJobs`, `generateJobs`, `requestBulkAction`; pending carries `jobIds` + `bulk`; `confirmPending` fans out for bulk | ui/hooks |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Extract shared `phaseGradeCells` helper; `gradeDot` gets a `letterless` flag; add exported `buildPhaseListGradeRow(job, gradesField)` | ui/lib |
| `src/ui/frontend/src/App.css` | `.grade-dot-letterless` modifier; `.recommended-list-header-actions`, `.recommended-analysis-*` layout, `.recommended-list-phase-grade-row` | ui/css |
| `src/ui/frontend/src/components/CandidateJobRowActions.tsx` | Optional `onGenerate` prop → one more `icon-control` button | ui/components |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Total column + sort branch; selection checkboxes + header bulk bar; row Generate wiring; Analysis toggle + expanded rows | ui/pages |

No other files. `tests/` and `docs/test-bible/**` are Betty's — not touched.

## Known test impact (for Betty, not for build-child)

- `tests/component/frontend/pages/test_JobsRecommended.test.tsx` line ~101 reads every
  `row` in a section and asserts textContent order. With the Analysis toggle **on by
  default** (AC 9), each job row is followed by an expanded `<tr>`, so that row list
  doubles. That is the specified behaviour, not a regression — flagged for `qa-child`.
- Column count grows by two (checkbox + Total); any test that indexes cells by position
  will shift.

---

## Stage 1: Generate helper + hook bulk flows

**Done when:** `postGenerateArtifacts` exists in `candidateJobActions.ts`; the hook exposes
`generateJob`, `skipJobs`, `generateJobs`, `requestBulkAction` and still compiles for
`JobsApplied.tsx`, `JobsSkipped.tsx`, `JobsRecommended.tsx` unchanged. `npm run build`
and `npm run lint` in `src/ui/frontend` exit 0.

1. In `src/ui/frontend/src/lib/candidateJobActions.ts`, append after `postSkipJob`:

   ```ts
   /** Start a job's artifact build (RECOMMENDED → BUILD_ARTIFACTS); server enforces legality (409). */
   export async function postGenerateArtifacts(astralJobId: string): Promise<void> {
     const res = await api(`/api/jobs/${encodeURIComponent(astralJobId)}/generate_artifacts`, { method: "POST" })
     if (!res.ok) {
       const body = await res.json().catch(() => ({}))
       throw new Error((body as { error?: string }).error || "Generate failed")
     }
   }
   ```

2. In `src/ui/frontend/src/hooks/useCandidateJobActions.ts`, replace the file body with the
   following (existing exported names and single-job behaviour preserved):

   ```ts
   import { useCallback, useState } from "react"
   import {
     postCandidateAction,
     postGenerateArtifacts,
     postSkipJob,
     type CandidateActionKey,
   } from "../lib/candidateJobActions"

   /** Bulk outcome reported to the page for its toast (AST-1968). */
   export interface BulkActionResult {
     label: string
     succeeded: number
     failed: number
   }

   // `jobId` stays (= jobIds[0]) because JobsApplied reads pending.jobId directly.
   interface PendingAction {
     jobId: string
     jobIds: string[]
     action: CandidateActionKey
     bulk: boolean
     label: string
   }

   // One POST per job, in order; a failure is counted, never thrown, so the rest still run.
   async function runPerJob(jobIds: string[], post: (id: string) => Promise<void>) {
     let succeeded = 0
     for (const id of jobIds) {
       try {
         await post(id)
         succeeded += 1
       } catch {
         // counted as failed below
       }
     }
     return { succeeded, failed: jobIds.length - succeeded }
   }

   /** AST-312: shared skip / candidate_action flow for job list pages. AST-1968: generate + bulk. */
   export function useCandidateJobActions(
     onRefresh: () => void,
     onBulkDone?: (result: BulkActionResult) => void,
   ) {
     const [pending, setPending] = useState<PendingAction | null>(null)
     const [busy, setBusy] = useState(false)
     const [error, setError] = useState<string | null>(null)

     const clearError = useCallback(() => setError(null), [])

     // Single-job flow: surfaces the server error via `error` (page toasts it).
     const runSingle = useCallback(async (
       jobId: string,
       post: (id: string) => Promise<void>,
       fallback: string,
     ) => {
       setBusy(true)
       setError(null)
       try {
         await post(jobId)
         onRefresh()
       } catch (e) {
         setError(e instanceof Error ? e.message : fallback)
       } finally {
         setBusy(false)
       }
     }, [onRefresh])

     // Bulk flow: never sets `error`; counts go to onBulkDone so the page shows one toast.
     const runBulk = useCallback(async (
       label: string,
       jobIds: string[],
       post: (id: string) => Promise<void>,
     ) => {
       setBusy(true)
       setError(null)
       try {
         const counts = await runPerJob(jobIds, post)
         onRefresh()
         onBulkDone?.({ label, ...counts })
       } finally {
         setBusy(false)
       }
     }, [onRefresh, onBulkDone])

     const skipJob = useCallback(
       (jobId: string) => runSingle(jobId, postSkipJob, "Skip failed"),
       [runSingle],
     )

     const generateJob = useCallback(
       (jobId: string) => runSingle(jobId, postGenerateArtifacts, "Generate failed"),
       [runSingle],
     )

     const skipJobs = useCallback(
       (jobIds: string[]) => runBulk("Skip", jobIds, postSkipJob),
       [runBulk],
     )

     const generateJobs = useCallback(
       (jobIds: string[]) => runBulk("Generate Artifacts", jobIds, postGenerateArtifacts),
       [runBulk],
     )

     const requestAction = useCallback((jobId: string, action: CandidateActionKey) => {
       setPending({ jobId, jobIds: [jobId], action, bulk: false, label: "" })
     }, [])

     // One notes modal for many jobs; confirm applies the same note to each.
     const requestBulkAction = useCallback((jobIds: string[], action: CandidateActionKey, label: string) => {
       if (!jobIds.length) return
       setPending({ jobId: jobIds[0], jobIds, action, bulk: true, label })
     }, [])

     const confirmPending = useCallback(async (notes: string) => {
       if (!pending || busy) return
       if (pending.bulk) {
         const { action, jobIds, label } = pending
         await runBulk(label, jobIds, id => postCandidateAction(id, action, notes))
         setPending(null)
         return
       }
       setBusy(true)
       setError(null)
       try {
         await postCandidateAction(pending.jobId, pending.action, notes)
         setPending(null)
         onRefresh()
       } catch (e) {
         setError(e instanceof Error ? e.message : "Action failed")
       } finally {
         setBusy(false)
       }
     }, [pending, busy, onRefresh, runBulk])

     return {
       pending,
       busy,
       error,
       clearError,
       skipJob,
       generateJob,
       skipJobs,
       generateJobs,
       requestAction,
       requestBulkAction,
       confirmPending,
       closePending: () => setPending(null),
     }
   }
   ```

   ⚠️ **Decision:** Bulk calls run **sequentially** (one `await` per job), not
   `Promise.all`. Keeps server load flat for large selections and makes counts
   deterministic; no batching or concurrency limit is introduced.

   ⚠️ **Decision:** `pending.jobId` is retained (always `jobIds[0]`) because
   `src/ui/frontend/src/pages/JobsApplied.tsx` reads it and that file is outside this
   ticket's Scope. `bulk` and `label` are internal to the hook's bulk path.

   ⚠️ **Decision:** Bulk Applied keeps the notes modal open (showing its existing
   "Saving…" state via `busy`) until every POST finishes, then closes it — even if some
   failed, because the toast reports the split and the selection clears (AC 8).

3. Run `npm run build` and `npm run lint` in `src/ui/frontend`. Both exit 0.

---

## Stage 2: Shared grade-cell helper, letterless list builder, CSS

**Done when:** `buildPhaseSectionGradeConfidenceRow` renders exactly as before (same cells,
order, tooltip, `ConfidenceBullets`), `buildPhaseListGradeRow` exists, and
`rg -n "sortRubricColumnsByImportanceAndGrade(" src/ui/frontend/src/lib/recommendedJobReport.tsx`
returns exactly one call line (the import line has no `(`). Build + lint exit 0.

1. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`, replace `function gradeDot`
   with:

   ```tsx
   // letterless: list rows show colour only (AST-1968); modal keeps the letter.
   function gradeDot(grade: string, tooltip: string, letterless = false) {
     return (
       <span
         className={`grade-dot dot-${grade.toLowerCase()}${letterless ? " grade-dot-letterless" : ""}`}
         title={tooltip || undefined}
       >
         {letterless ? null : grade}
       </span>
     )
   }
   ```

   `buildPhaseTabGradeDots` keeps calling `gradeDot(grade, gradeTooltip)` unchanged.

2. In the same file, immediately above `buildPhaseSectionGradeConfidenceRow`, add the
   shared helper:

   ```tsx
   /**
    * Single source of column set, order, grade lookup and tooltip for a phase's grade row.
    * Shared by the modal Analysis header and the Recommended list lines so they can't drift.
    */
   function phaseGradeCells(gradesRaw: unknown, job: Record<string, unknown>, gradesField: string) {
     // Job-carried *_rubric (or grades-only) — never live candidate artifacts (AST-1327).
     const baseCols = buildJobListRubricColumnsForGroup({ gradeKey: gradesField, columnSourceJob: job })
     const cols = sortRubricColumnsByImportanceAndGrade(
       baseCols,
       col => gradeAndConfidenceForCol(gradesRaw, col).grade,
     )
     const out: Array<{ key: string; grade: string; tooltip: string; confidence?: number }> = []
     for (const col of cols) {
       const { grade, confidence, reason } = gradeAndConfidenceForCol(gradesRaw, col)
       if (!grade) continue
       out.push({
         key: col.code || col.label,
         grade,
         tooltip: formatGradeDotTooltipWithVectorLabel(col, grade, reason, confidence),
         confidence,
       })
     }
     return out
   }
   ```

3. Replace the body of `buildPhaseSectionGradeConfidenceRow` (signature unchanged) with:

   ```tsx
   const cells = phaseGradeCells(gradesRaw, job, gradesField)
   if (!cells.length) return null
   return (
     <div className="recommended-report-phase-grade-row">
       {cells.map(c => (
         <span key={c.key} className="recommended-report-phase-grade-cell">
           {gradeDot(c.grade, c.tooltip)}
           <ConfidenceBullets confidence={c.confidence} />
         </span>
       ))}
     </div>
   )
   ```

   Keep its existing doc comment (`/** Horizontal grade + confidence row … */`).

4. Directly after `buildPhaseSectionGradeConfidenceRow`, add:

   ```tsx
   /** Recommended list line: same circles/order/tooltip as the modal, no letters, no confidence (AST-1968). */
   export function buildPhaseListGradeRow(job: Record<string, unknown>, gradesField: string): ReactNode {
     const cells = phaseGradeCells(jobGradesForField(job, gradesField), job, gradesField)
     if (!cells.length) return null
     return (
       <div className="recommended-list-phase-grade-row">
         {cells.map(c => <span key={c.key}>{gradeDot(c.grade, c.tooltip, true)}</span>)}
       </div>
     )
   }
   ```

   `jobGradesForField` is declared later in the same module as a function declaration
   (hoisted) — no reorder needed. The `gradesRaw` source matches the modal's
   `renderAnalysisMetadata` (`jobGradesForField(jobRec, phase.grades_field)`).

5. In `src/ui/frontend/src/App.css`, directly after the `.dot-x` rule (line ~1094), add:

   ```css
   /* AST-1968: colour-only grade circle for Recommended list analysis lines */
   .grade-dot-letterless {
     width: 12px;
     height: 12px;
     font-size: 0;
   }
   ```

6. In `src/ui/frontend/src/App.css`, directly after the
   `.recommended-report-phase-grade-cell .grade-dot` rule (line ~968), add:

   ```css
   /* AST-1968: Recommended list header — bulk buttons + Analysis toggle */
   .recommended-list-header-actions {
     display: flex;
     align-items: center;
     gap: 8px;
   }

   .recommended-analysis-toggle {
     display: inline-flex;
     align-items: center;
     gap: 6px;
     font-size: 13px;
     color: var(--text-secondary);
     cursor: pointer;
   }

   /* AST-1968: expanded per-job analysis row (four stacked phase lines) */
   .list-page-table tbody tr.recommended-analysis-row td {
     padding-top: 0;
   }

   .recommended-analysis-lines {
     display: flex;
     flex-direction: column;
     gap: 3px;
   }

   .recommended-analysis-line {
     display: flex;
     align-items: center;
     gap: 8px;
   }

   .recommended-analysis-line-label {
     width: 36px;
     font-size: 11px;
     font-weight: 600;
     color: var(--text-secondary);
   }

   .recommended-list-phase-grade-row {
     display: flex;
     flex-wrap: wrap;
     align-items: center;
     gap: 4px;
   }
   ```

   ⚠️ **Decision:** 12px circles / 36px label width are visual sizing only (no
   truncation or limits). The expanded row's `td` keeps the default bottom border so each
   job block stays visually separated; the job row above it keeps its own border too.

7. Run `npm run build` and `npm run lint`. Both exit 0.

---

## Stage 3: Row Generate control

**Done when:** `CandidateJobRowActions` renders a `title="Generate Artifacts"` icon button
only when `onGenerate` is passed; Skipped / Applied / Recommended render unchanged until
Stage 5 passes it. Build + lint exit 0.

1. In `src/ui/frontend/src/components/CandidateJobRowActions.tsx`, add to `interface Props`
   after `onAction`:

   ```ts
   /** AST-1968: only passed by Recommended for rows whose state allows generate_artifacts. */
   onGenerate?: () => void
   ```

   Destructure `onGenerate` in the component parameters after `onAction`.

2. In the `REVIEW_LIKE.has(state) && onSkip` branch, insert directly after the Applied
   button block and before the View Job Analysis block:

   ```tsx
   {onGenerate && (
     <button type="button" className="icon-control" title="Generate Artifacts" aria-label="Generate Artifacts"
       onClick={onGenerate}>G</button>
   )}
   ```

   ⚠️ **Decision:** Gating is by the caller passing `onGenerate`, not by a state set in
   this component — eligibility comes from the manifest in the page (Stage 5). No other
   branch changes.

3. Run `npm run build` and `npm run lint`. Both exit 0.

---

## Stage 4: Total column + sort

**Done when:** Each section table shows a sortable **Total** header after the four phase
headers; a job with 7.0 / 6.5 / 8.0 / 5.5 shows `27.0`; a job missing any phase score
shows `—`; clicking Total sorts through `sortRecommendedJobs` with the same null placement
as JD. `rg -n "function sortRecommendedJobs" src/ui/frontend/src/pages/JobsRecommended.tsx`
returns one hit. Build + lint exit 0.

1. In `src/ui/frontend/src/pages/JobsRecommended.tsx`, above `sortRecommendedJobs`, add:

   ```ts
   const TOTAL_SCORE_COL = "total_score"

   function finiteOrNull(v: unknown): number | null {
     return typeof v === "number" && Number.isFinite(v) ? v : null
   }

   // Sum of manifest phase_score_columns; null if any phase score is missing (AST-1968).
   function totalScore(job: Job, phaseFields: string[]): number | null {
     if (!phaseFields.length) return null
     let sum = 0
     for (const field of phaseFields) {
       const n = finiteOrNull(job[field])
       if (n === null) return null
       sum += n
     }
     return sum
   }
   ```

2. In `sortRecommendedJobs`, replace the `else if (phaseFields.includes(col)) { … }`
   branch with:

   ```ts
   } else if (phaseFields.includes(col) || col === TOTAL_SCORE_COL) {
     // Total shares the phase columns' null handling — one sorter, not two.
     const an = col === TOTAL_SCORE_COL ? totalScore(a, phaseFields) : finiteOrNull(a[col])
     const bn = col === TOTAL_SCORE_COL ? totalScore(b, phaseFields) : finiteOrNull(b[col])
     if (an === null && bn === null) cmp = 0
     else if (an === null) cmp = 1
     else if (bn === null) cmp = -1
     else cmp = an - bn
   }
   ```

3. In the `<thead>` row, directly after the `phase_score_columns.map(...)` header block and
   before the Updated `<th>`, add:

   ```tsx
   <th
     className="sortable"
     style={{ textAlign: "center", whiteSpace: "nowrap", width: 1 }}
     onClick={() => handleSort(sec.state, TOTAL_SCORE_COL)}
   >
     Total{sortIndicator(sec.state, TOTAL_SCORE_COL)}
   </th>
   ```

4. In the job `<tr>`, directly after the `phase_score_columns.map(...)` cell block and
   before the `<Time>` cell, add:

   ```tsx
   <td style={{ textAlign: "center", whiteSpace: "nowrap", width: 1 }}>
     {formatPhaseScore(totalScore(job, phaseFields))}
   </td>
   ```

   `formatPhaseScore(null)` already returns the em dash; `27` renders `27.0`.

5. Run `npm run build` and `npm run lint`. Both exit 0.

---

## Stage 5: Selection, bulk bar, row Generate wiring

**Done when:** Every row in every section (incl. Meteorites) has a checkbox; with ≥1
checked, the header shows `Skip (N)`, `Applied (N)`, `Generate Artifacts (n)` (n = checked
jobs whose state's manifest actions include `generate_artifacts`); each bulk action toasts
`<label>: X succeeded, Y failed`, refreshes, and clears the selection; Recommended-state
rows show the G icon; no `/generate_artifacts` string in the page. Build + lint exit 0.

1. In `src/ui/frontend/src/pages/JobsRecommended.tsx`:
   - Change the import `{ formatPhaseScore }` from `../lib/recommendedJobReport` to
     `{ formatPhaseScore, primaryActionsForState }` (`buildPhaseListGradeRow` is added in
     Stage 6 step 1, where it is first used).
   - Change the hook import to
     `import { useCandidateJobActions, type BulkActionResult } from "../hooks/useCandidateJobActions"`.

2. Inside `Recommended()`, after the `sorts` state line, add:

   ```ts
   // Page-level selection keyed by astral_job_id; not persisted (AST-1968).
   const [selected, setSelected] = useState<Set<string>>(new Set())
   ```

3. Replace `const actions = useCandidateJobActions(load)` with:

   ```ts
   // After any bulk action: one toast with the split, then clear selection (AC 8).
   const handleBulkDone = useCallback((r: BulkActionResult) => {
     setSelected(new Set())
     setToast({
       text: `${r.label}: ${r.succeeded} succeeded, ${r.failed} failed`,
       variant: r.failed ? "error" : "success",
     })
   }, [])

   const actions = useCandidateJobActions(load, handleBulkDone)
   ```

4. After `useEffect(() => { load(true) }, [load])`, add:

   ```ts
   // Candidate switch drops the previous candidate's selection.
   useEffect(() => { setSelected(new Set()) }, [selectedId])
   ```

5. After the `phaseFields` memo, add:

   ```ts
   // Eligibility from manifest primary_actions_by_state — no hardcoded state list.
   const canGenerate = useCallback(
     (state: string) => primaryActionsForState(manifest, state).some(a => a.action_key === "generate_artifacts"),
     [manifest],
   )

   // Derived from current rows so ids that left the list (row action, refresh) never count.
   const selectedIds = useMemo(
     () => rows.filter(j => selected.has(j.astral_job_id)).map(j => j.astral_job_id),
     [rows, selected],
   )
   const generateIds = useMemo(
     () => rows.filter(j => selected.has(j.astral_job_id) && canGenerate(j.state)).map(j => j.astral_job_id),
     [rows, selected, canGenerate],
   )

   const toggleSelect = useCallback((id: string) => setSelected(prev => {
     const next = new Set(prev)
     if (next.has(id)) next.delete(id); else next.add(id)
     return next
   }), [])
   ```

   ⚠️ **Decision:** Selection is **not** cleared on every `load()` (unlike Skipped),
   because single-row actions and the modal's `onRefresh` call `load()` and would wipe an
   in-progress multi-select. It clears after bulk actions (step 3), on candidate switch
   (step 4), and on page reload (state is not persisted). Stale ids are filtered by
   deriving from `rows`.

6. Replace the `<div className="list-page-header">…</div>` block with:

   ```tsx
   <div className="list-page-header">
     <h1 className="list-page-title">Recommended</h1>
     <div className="recommended-list-header-actions">
       {selectedIds.length > 0 && (
         <>
           <button type="button" className="btn secondary" disabled={actions.busy}
             onClick={() => actions.skipJobs(selectedIds)}>
             Skip ({selectedIds.length})
           </button>
           <button type="button" className="btn secondary" disabled={actions.busy}
             onClick={() => actions.requestBulkAction(selectedIds, "applied", "Applied")}>
             Applied ({selectedIds.length})
           </button>
           <button type="button" className="btn primary" disabled={actions.busy || generateIds.length === 0}
             onClick={() => actions.generateJobs(generateIds)}>
             Generate Artifacts ({generateIds.length})
           </button>
         </>
       )}
     </div>
   </div>
   ```

   (Stage 6 adds the Analysis toggle inside `.recommended-list-header-actions`.)

   ⚠️ **Decision:** `Generate Artifacts (0)` renders **disabled** when the selection has
   no eligible jobs (AC 4 requires the button with its count while anything is selected;
   AC 7 forbids sending ineligible jobs). Bulk Skip and Applied send every selected job;
   the server enforces per-job legality and failures show in the toast count.

7. In `<thead>`, insert a new first header cell before the Actions `<th>`:

   ```tsx
   <th style={{ width: 1 }} aria-label="Select" />
   ```

8. In the job `<tr>`, insert a new first cell before the Actions `<td>`:

   ```tsx
   <td onClick={e => e.stopPropagation()}>
     <input
       type="checkbox"
       aria-label={`Select ${job.job_title || job.astral_job_id}`}
       checked={selected.has(job.astral_job_id)}
       onChange={() => toggleSelect(job.astral_job_id)}
     />
   </td>
   ```

9. On the existing `<CandidateJobRowActions … />` in the job row, add the prop:

   ```tsx
   onGenerate={canGenerate(job.state) ? () => actions.generateJob(job.astral_job_id) : undefined}
   ```

   Row Generate uses the single-job flow: on failure the existing `actions.error` effect
   toasts the server message; on success `load()` moves the job to In Progress (AC 2).

10. Run `npm run build` and `npm run lint`. Both exit 0.
    Verify AC 3: `rg -n "/generate_artifacts" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/components/CandidateJobRowActions.tsx` returns nothing.

---

## Stage 6: Analysis toggle + expanded rows

**Done when:** On load the header shows an **Analysis** checkbox, checked; each job row is
followed by one `tr.recommended-analysis-row` spanning all columns with four lines labelled
JD, DO, GET, LIKE (manifest `report_phase_tabs` order), each showing letterless circles or
`—`; clicking the expanded row opens the report; unchecking removes every expanded row.
Build + lint exit 0.

1. In `src/ui/frontend/src/pages/JobsRecommended.tsx`:
   - Change the React import to
     `import { Fragment, useCallback, useEffect, useMemo, useState } from "react"`.
   - Change the `../lib/recommendedJobReport` import to
     `{ buildPhaseListGradeRow, formatPhaseScore, primaryActionsForState }`.

2. After the `selected` state line, add:

   ```ts
   // Analysis toggle: on at page load, not persisted (AST-1968).
   const [showAnalysis, setShowAnalysis] = useState(true)
   ```

3. After the `phaseFields` memo, add:

   ```ts
   // Line order + grades_field from report_phase_tabs (modal order); short label from the
   // matching phase_score_columns entry (jd_grades → jd_score → "JD"), else the tab nav_label.
   const phaseLines = useMemo(() => {
     const rec = manifest?.jobs.recommended
     return (rec?.report_phase_tabs ?? []).map(tab => ({
       gradesField: tab.grades_field,
       label: rec?.phase_score_columns.find(
         c => c.field === tab.grades_field.replace(/_grades$/, "_score"),
       )?.label ?? tab.nav_label,
     }))
   }, [manifest])
   ```

4. Inside `.recommended-list-header-actions` (Stage 5 step 6), after the bulk-button
   fragment, add:

   ```tsx
   <label className="recommended-analysis-toggle">
     <input type="checkbox" checked={showAnalysis} onChange={e => setShowAnalysis(e.target.checked)} />
     Analysis
   </label>
   ```

5. Inside `sections.map(sec => { … })`, after `const sorted = …`, add:

   ```ts
   // checkbox + actions + title + company + state + phase cols + total + updated
   const columnCount = 7 + manifest.jobs.recommended.phase_score_columns.length
   ```

6. Replace `{sorted.map(job => ( <tr key={job.astral_job_id} …>…</tr> ))}` with a
   `Fragment` per job: move `key={job.astral_job_id}` from the `<tr>` to
   `<Fragment key={job.astral_job_id}>`, keep the existing job `<tr>` (with Stage 4/5
   cells) unchanged inside it, and append after it:

   ```tsx
   {showAnalysis && (
     <tr className="clickable recommended-analysis-row" onClick={() => openJobReport(job.astral_job_id)}>
       <td colSpan={columnCount}>
         <div className="recommended-analysis-lines">
           {phaseLines.map(p => (
             <div key={p.gradesField} className="recommended-analysis-line">
               <span className="recommended-analysis-line-label">{p.label}</span>
               {buildPhaseListGradeRow(job, p.gradesField) ?? "\u2014"}
             </div>
           ))}
         </div>
       </td>
     </tr>
   )}
   ```

   ⚠️ **Decision:** Lines are always rendered for all `report_phase_tabs` entries (four
   today); a phase with no grades shows the em dash rather than omitting the line, so the
   count stays exactly four (AC 9).

7. Run `npm run build` and `npm run lint`. Both exit 0.

---

## AC trace

| AC | Covered by |
|----|------------|
| 1, 15 | Stage 3 (prop-gated button) + Stage 5 step 9 (manifest `canGenerate`) |
| 2 | Stage 1 `generateJob` + Stage 5 step 9 |
| 3 | Stage 1 step 1; Stage 5 step 10 check |
| 4 | Stage 5 steps 6–8 |
| 5, 6, 7, 8 | Stage 1 bulk flows + Stage 5 steps 3, 6 |
| 9 | Stage 6 |
| 10, 11, 12 | Stage 2 (`phaseGradeCells` shared, `letterless`, no `ConfidenceBullets` in list builder) + Stage 6 |
| 13, 14 | Stage 4 |
| 16 | build + lint at the end of every stage |

## Estimate

Confirm Chuckles estimate: 5 — agree


## Joan validate

```text
[plan-rubric]
**Ticket:** AST-1968
**Overall:** APPROVED
**Corpus:** bd68954dc854ca80fca1fc391821dff9ff288a7a
**Publish ref:** origin/sub/AST-1967/AST-1968-recommended-list-triage-upgrades @ 5c00918ee04b43bb6a391a2242ffe13d2b6052d6

## Canon scores

(no ids on frozen Canon Scope — parent AST-1967 locked **Canon Scope: empty** at Discussion; ticket mirrors that declaration. Not a missing-scope ESCALATE per validate-plan §4a.)

## Traceability

AC 1–16 → Stages 1–6 and plan `## AC trace` (row/bulk generate, shared `postGenerateArtifacts`, bulk bar + manifest `canGenerate`/`generateIds`, Analysis default-on + `phaseGradeCells`/`buildPhaseListGradeRow`, Total via `sortRecommendedJobs`; build+lint each stage; no orphan stages).

## Findings

### acceptable
- **Location:** Ticket + parent `## Architectural definition` / `Canon Scope`
- **Finding:** Deliberately empty directive list with documented rationale (frontend list page; no in-force UI list statute).
- **Recommendation:** None — Radia will have the same empty list at review-child.

### discuss
- **Location:** Parent Canon Scope vs typical frontend touches
- **Finding:** `astral.ui.frontend-file-placement` and `astral.standards.dry-and-focused-functions` would be the usual candidates if Archie had listed them; all planned paths stay under existing UI dirs and the plan explicitly factors grade ordering into `phaseGradeCells` rather than duplicating in `JobsRecommended.tsx`.
- **Recommendation:** No plan change required; keep empty scope unless Archie amends at Discussion.

### acceptable
- **Location:** Plan doc (no `## Self-assessment`)
- **Finding:** No `!!-NONE` confidence block; stages are concrete (full hook body, CSS, six stages with done-when gates).
- **Recommendation:** None for approve; optional polish only.

### acceptable
- **Location:** Stage 1 — bulk toast shape vs AC 5 wording
- **Finding:** Toast template is `"<label>: X succeeded, Y failed"`; AC 5 example `"3 succeeded"` is satisfied when Y=0.
- **Recommendation:** None.

### acceptable
- **Location:** Stage 3 — `G` on Generate vs Ghosted on Applied list
- **Finding:** Generate `G` only renders in `REVIEW_LIKE` when `onGenerate` is passed; Applied-page Ghosted `G` is a different branch.
- **Recommendation:** None.

**Definition fidelity (R6):** Plan matches parent Purpose and all four functional capabilities; files/stages align with child `## Scope` and explicit scope gate; no backend/modal behaviour change; `JobsApplied`’s separate `confirmPending` remains compatible with `pending.jobId` = `jobIds[0]`. Generate POST path matches modal (`/api/jobs/<id>/generate_artifacts`).

context_tokens≈24000
```

## Review

- **Branch:** `sub/AST-1967/AST-1968-recommended-list-triage-upgrades`
- **Build commits:** `9524a2c68` (Stage 1 generate helper + hook bulk flows) · `1fbace403` (Stage 2 shared `phaseGradeCells`, letterless list row, CSS) · `85a6afb16` (Stage 3 row Generate control) · `f6341f34a` (Stage 4 Total column + sort) · `c5c3a9ab1` (Stage 5 selection, bulk bar, row Generate wiring) · `8cc4ca5fb` (Stage 6 Analysis toggle + expanded lines)
- **Build notes:** All six stages executed as written. `npm run build` and `npx tsc -b --noEmit` exit 0 after every stage. AC 3 `rg -n "/generate_artifacts"` on page + component: no hits. AC 12 `sortRubricColumnsByImportanceAndGrade(` call lines in `recommendedJobReport.tsx`: 1. AC 14 `function sortRecommendedJobs`: 1 hit. `validate-sub-log.sh --stage=build`: ok.
- **Gate resolution (Susan, AST-1969):** Q1=2 — AC 16 = no new lint problems vs `origin/dev`, plus fix the baseline `set-state-in-effect` in `JobsRecommended.tsx`; Q2=1 — drop the Stage 5 selection-clear effect, clear in `load` when `showSpinner`.
- **Gate fix commit:** `547d832b3` — `actions.error` toast is now derived (`useMemo` → `Toast message={toast ?? errorToast}`, `dismissToast` clears both); selection clear moved into `load`'s fetch `.then` behind `showSpinner` (a synchronous call in `load` is still traced through the mount effect by `react-hooks/set-state-in-effect`; the async callback is not — same pattern as `JobsSkipped`).
- **Lint vs `origin/dev`:** 32 → 31 problems (27 → 26 errors); only diff is the removed `JobsRecommended.tsx` hit; zero new problems. `npm run build` + `tsc -b --noEmit` exit 0.

## Radia review

```
[code-rubric]
**Ticket:** AST-1968
**Publish ref:** `0970ea6973c7945a9853c73fcfd97cf89d5e1dc7` (`origin/sub/AST-1967/AST-1968-recommended-list-triage-upgrades`)
**Corpus:** `e1f2699fad44e4083e39a9a066cc87cae494ad51`
**Overall:** CLEAN

## Canon scores

(frozen Canon Scope empty — no directive ids locked at Plan Approved; parent AST-1967 and ticket mirror “no in-force directive governs frontend list pages.” Nothing to score per validate-plan §4a; not a scope-gap ESCALATE.)

## Column diff vs plan stage

(aligned) — Joan: APPROVED with the same empty canon column; implementation matches the six-stage plan and AC trace.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** `git diff origin/dev...origin/sub/AST-1967/AST-1968-recommended-list-triage-upgrades` — non-`src/ui/frontend` paths
- **Finding:** **sibling test carry:** `tests/component/core/test_timesheets.py`, `tests/component/external/test_llm_compat.py`, `tests/component/external/test_openrouter.py`, `tests/component/utils/test_config.py` plus matching `docs/test-bible/**` edits (AST-1966 / AST-1959 lineage), not AST-1968 product scope.
- **Recommendation:** No action for this child; expected merge-tests carry.

- **Location:** Review pass
- **Finding:** AC 16 (`npm run build` / lint delta vs `origin/dev`) was not re-run in this Radia session; relied on **Tests Passed**, issue doc build notes (`547d832b3` gate fix), and component tests covering AST-1968 ACs.
- **Recommendation:** If Susan wants belt-and-suspenders before **User Testing**, re-run `npm run build` and `npm run lint` in `src/ui/frontend` on the publish tip.

- **Location:** Notes — Canon Scope (off-list, not scored)
- **Finding:** Joan’s plan discuss named `astral.ui.frontend-file-placement` and `astral.standards.dry-and-focused-functions` as usual candidates; diff stays within ticket Scope and centralizes grade ordering in `phaseGradeCells` — consistent with empty scope unless Archie amends Discussion.
- **Recommendation:** No change unless Archie expands Canon Scope on the parent.

## What's solid

- **Scope:** Product diff is exactly the six scoped files (`JobsRecommended.tsx`, `CandidateJobRowActions.tsx`, `candidateJobActions.ts`, `useCandidateJobActions.ts`, `recommendedJobReport.tsx`, `App.css`); no backend routes or `config.py`.
- **AC 3 / 12 / 14:** `postGenerateArtifacts` is the sole `generate_artifacts` client path in lib; page/component have no `/generate_artifacts` strings; one `sortRubricColumnsByImportanceAndGrade(` call site in `recommendedJobReport.tsx`; one `sortRecommendedJobs` in the page.
- **Generate gating:** Manifest-driven `canGenerate` / `generateIds`; bulk generate filters to eligible ids; row `onGenerate` only when manifest allows.
- **Grade parity:** `phaseGradeCells` shared by modal and list; `buildPhaseListGradeRow` letterless; tests assert modal/list dot signature match (AC 10–11).
- **Bulk flows:** Sequential `runPerJob`, single notes modal for bulk Applied, selection cleared via `handleBulkDone` and `load(true)` spinner path (Susan gate: lint-safe vs dropped `selectedId` effect).
- **Hook compat:** Optional `onBulkDone`; `pending.jobId` preserved for `JobsApplied.tsx`.
- **Tests:** Dedicated `AST-1968` block on `test_JobsRecommended.test.tsx` covers AC 1–2, 4–10, 13–14; component/lib tests cover Generate prop and shared helper.

## Recommended actions (for Chuckles — not Radia)

1. Append this artifact to `docs/features/interface/ast-1968-recommended-list-triage-upgrades.md` under `## Review`.
2. Commit `docs(AST-1968): Radia review — clean` on the publish ref and push.
3. Post slim upshot via `linear_proxy.py --as radia save-comment`.
4. Move ticket to **Review Posted**; datt **§3h** → **PROCEED** path toward **User Testing** (no fix-now canon or plan gaps).

context_tokens≈28000
```
