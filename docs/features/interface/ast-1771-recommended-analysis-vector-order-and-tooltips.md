# AST-1771 — Recommended Analysis vector order and tooltips

**Parent:** [AST-1770 — Vector Icons are out of sequence](https://linear.app/astralcareermatch/issue/AST-1770/vector-icons-are-out-of-sequence)

**Publish ref:** `sub/AST-1770/AST-1771-recommended-analysis-vector-order-and-tooltips`

Operators reading a Recommended Job Report Analysis phase should scan vectors in descending rubric importance, then descending letter grade (A best), in both the compact header grade row and the expanded per-vector detail. Today those surfaces follow consult payload order (or importance-only column sort in headers), so vectors appear out of sequence. This child adds a shared importance-then-grade sort for Recommended-report render sites only and prefixes the vector label on header grade-dot hover tooltips. Skipped/In Review list tables, consult scoring, rubric persistence, and Summary/Artifacts tabs are unchanged.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/rubricDisplay.ts` | Export grade rank map; add Recommended-report sort helper; add vector-prefixed grade-dot tooltip formatter | ui/lib |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Use new sort + prefixed tooltips in `buildPhaseSectionGradeConfidenceRow` | ui/lib |
| `src/ui/frontend/src/components/AgentAnalysisHeader.tsx` | Sort expanded detail rows with the same helper | ui/components |
| `tests/component/frontend/lib/test_rubricDisplay.test.ts` | Unit tests for sort + tooltip prefix | tests |
| `tests/component/frontend/lib/test_recommendedJobReport.test.tsx` | Header row DOM order + tooltip prefix | tests |
| `tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx` | Detail list DOM order | tests |
| `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` | End-to-end header + expanded detail order on AST-1328 fixture | tests |

## Stage 1: Shared sort + tooltip helpers (`rubricDisplay.ts`)

**Done when:** `sortRubricColumnsByImportanceAndGrade` and `formatGradeDotTooltipWithVectorLabel` are exported from `rubricDisplay.ts`, `sortJobListRubricColumns` is untouched, and no Recommended-report call sites are wired yet.

1. In `src/ui/frontend/src/lib/rubricDisplay.ts`, after the existing `formatGradeDotTooltip` function, add and export a grade-rank map matching list-table semantics (`JobsInReview.tsx` / `JobsSkipped.tsx` local `GRADE_ORDER`):

   ```typescript
   export const GRADE_RANK: Record<string, number> = { A: 0, B: 1, C: 2, D: 3, F: 4, X: 5 }

   export function gradeRank(letter: string): number {
     return GRADE_RANK[(letter ?? "").trim().toUpperCase()] ?? 99
   }
   ```

2. In the same file, add and export `sortRubricColumnsByImportanceAndGrade` **without modifying** `sortJobListRubricColumns`:

   ```typescript
   export function sortRubricColumnsByImportanceAndGrade(
     cols: JobListRubricColumn[],
     gradeForCol: (col: JobListRubricColumn) => string,
   ): JobListRubricColumn[] {
     return [...cols].sort((a, b) => {
       const impDiff = b.importance - a.importance
       if (impDiff !== 0) return impDiff
       const gradeDiff = gradeRank(gradeForCol(a)) - gradeRank(gradeForCol(b))
       if (gradeDiff !== 0) return gradeDiff
       return a.code.localeCompare(b.code)
     })
   }
   ```

   ⚠️ **Decision:** New helper instead of extending `sortJobListRubricColumns` — list-table column order (AC4) must keep importance-then-code only; Recommended report is the sole consumer of grade as secondary key.

3. In the same file, add and export `formatGradeDotTooltipWithVectorLabel` that wraps `formatGradeDotTooltip`:

   ```typescript
   export function formatGradeDotTooltipWithVectorLabel(
     col: JobListRubricColumn,
     grade: string,
     reasonFromJob?: string,
     confidence?: number,
   ): string {
     const label = (col.label ?? col.code ?? "").trim()
     const body = formatGradeDotTooltip(col, grade, reasonFromJob, confidence)
     if (label && body) return `${label}: ${body}`
     return label || body
   }
   ```

4. In the same file, add and export `sortGradesByRubricDisplayOrder` for `AgentAnalysisHeader` detail rows:

   ```typescript
   export function sortGradesByRubricDisplayOrder<T extends { vector: string; grade: string }>(
     grades: T[],
     rubricItems?: Array<{ code?: string; label?: string; importance?: unknown }> | null,
   ): T[] {
     if (!grades.length) return grades
     let cols: JobListRubricColumn[]
     if (Array.isArray(rubricItems) && rubricItems.length) {
       cols = buildJobListRubricColumnsFromArtifact(rubricItems)
     } else {
       cols = grades.map(g => {
         const { code, label } = parseGradesVectorName(g.vector)
         return {
           code,
           label,
           importance: RUBRIC_DEFAULT_IMPORTANCE,
           headerCode: resolveRubricHeaderCode({ code, label }),
           headerTooltip: formatRubricColumnTooltip(label, RUBRIC_DEFAULT_IMPORTANCE),
           gradeDescriptions: {},
         }
       })
     }
     const gradeByColKey = new Map<string, T>()
     for (const g of grades) {
       const { code, label } = parseGradesVectorName(g.vector)
       gradeByColKey.set(normalizeRubricVectorKey(code), g)
       gradeByColKey.set(normalizeRubricVectorKey(label), g)
       gradeByColKey.set(normalizeRubricVectorKey(g.vector), g)
     }
     const sortedCols = sortRubricColumnsByImportanceAndGrade(cols, col => {
       const hit =
         gradeByColKey.get(normalizeRubricVectorKey(col.code)) ??
         gradeByColKey.get(normalizeRubricVectorKey(col.label))
       return hit?.grade ?? ""
     })
     const seen = new Set<T>()
     const ordered: T[] = []
     for (const col of sortedCols) {
       const hit =
         gradeByColKey.get(normalizeRubricVectorKey(col.code)) ??
         gradeByColKey.get(normalizeRubricVectorKey(col.label))
       if (hit && !seen.has(hit)) {
         seen.add(hit)
         ordered.push(hit)
       }
     }
     for (const g of grades) {
       if (!seen.has(g)) ordered.push(g)
     }
     return ordered
   }
   ```

5. Commit on epic worktree: `docs(AST-1771): plan — rubric display sort helpers` is **not** this stage — product commit message: `feat(AST-1771): add importance+grade rubric sort helpers`.

## Stage 2: Wire Recommended report header + detail order

**Done when:** Analysis phase header grade dots and expanded `AgentAnalysisHeader` rows both render in importance-then-grade order; header grade-dot `title` attributes prefix the vector label; `sortJobListRubricColumns` call sites in `JobsInReview.tsx` and `JobsSkipped.tsx` are unchanged.

1. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`, add imports for `sortRubricColumnsByImportanceAndGrade` and `formatGradeDotTooltipWithVectorLabel` from `./rubricDisplay`.

2. In `gradeAndConfidenceForCol`, leave grade lookup unchanged — sorting happens on columns, not inside this helper.

3. In `buildPhaseSectionGradeConfidenceRow`, replace the `sortJobListRubricColumns(...)` wrapper around `buildJobListRubricColumnsForGroup` with:

   - `const baseCols = buildJobListRubricColumnsForGroup({ gradeKey: gradesField, columnSourceJob: job })`
   - `const cols = sortRubricColumnsByImportanceAndGrade(baseCols, col => gradeAndConfidenceForCol(gradesRaw, col).grade)`

4. In the same function's loop, replace `formatGradeDotTooltip` (via `gradeAndConfidenceForCol`'s returned tooltip) with an explicit call to `formatGradeDotTooltipWithVectorLabel(col, grade, row.reason, confidence)` when building each cell's `title`. Pass `reason` and `confidence` from the destructured `gradeAndConfidenceForCol` result (extend destructuring if needed — do not change `gradeAndConfidenceForCol` signature for list consumers).

   ⚠️ **Decision:** Prefix tooltips only on Recommended-report header grade dots (this function), not on Skipped/In Review list cells that still call `formatGradeDotTooltip` directly.

5. Leave `buildPhaseTabGradeDots` on `sortJobListRubricColumns` — out of scope (phase tab nav labels, not Analysis section header row).

6. In `src/ui/frontend/src/components/AgentAnalysisHeader.tsx`, import `sortGradesByRubricDisplayOrder` from `../lib/rubricDisplay`.

7. At the start of the component body (after `labelList` is computed, before `return`), add:

   ```typescript
   const orderedGrades = sortGradesByRubricDisplayOrder(grades, rubricItems)
   ```

8. Replace `grades.map(g => {` with `orderedGrades.map(g => {`.

9. Verify boundary: run `grep -rn 'sortJobListRubricColumns' src/ui/frontend/src/pages/JobsInReview.tsx src/ui/frontend/src/pages/JobsSkipped.tsx` — both files must still import and call `sortJobListRubricColumns` with no signature or behavior change to that function.

10. Commit on epic worktree: `feat(AST-1771): sort Recommended Analysis vectors by importance and grade`.

## Stage 3: Component tests

**Done when:** All listed test files pass; AST-1328-style fixture asserts QC before EFW in header dots and expanded detail; tooltip prefix asserted on header dot.

### Fixture contract (reuse across tests)

Use the AST-1328 meteorite jd_rubric shape — consult array lists EFW first, but display order must be QC (importance 5, grade B) then EFW (importance 1, grade A):

```typescript
const grades = [
  { vector: "Embedded/Firmware/Hardware Domain", grade: "A", confidence: 5, reason: "fit" },
  { vector: "Quality Check", grade: "B", confidence: 4, reason: "ok" },
]
const rubric = [
  { code: "EFW", label: "Embedded/Firmware/Hardware Domain", importance: 1, grade_descriptions: [] },
  { code: "QC", label: "Quality Check", importance: 5, grade_descriptions: [] },
]
```

1. In `tests/component/frontend/lib/test_rubricDisplay.test.ts`, import `gradeRank`, `sortRubricColumnsByImportanceAndGrade`, and `formatGradeDotTooltipWithVectorLabel`.

2. Add test `gradeRank orders A before B before X`.

3. Add test `sortRubricColumnsByImportanceAndGrade orders QC/5/B before EFW/1/A when consult lists EFW first` — build two `JobListRubricColumn` entries from the fixture rubric; pass grade lookup `{ EFW: "A", QC: "B" }`; expect sorted codes `["QC", "EFW"]`.

4. Add test `sortRubricColumnsByImportanceAndGrade breaks importance ties by better letter grade` — two columns both importance 5, grades B vs A; A column first.

5. Add test `formatGradeDotTooltipWithVectorLabel prefixes label before rubric body` — col label `"Quality Check"`, grade `"B"`, reason `"ok"` → title starts with `"Quality Check:"`.

6. In `tests/component/frontend/lib/test_recommendedJobReport.test.tsx`, extend the existing `AST-1328` test (or add sibling `AST-1771`) to assert DOM order:

   - `container.querySelectorAll(".recommended-report-phase-grade-cell")` length 2
   - First cell contains `.grade-dot.dot-b` (QC)
   - Second cell contains `.grade-dot.dot-a` (EFW)
   - First grade dot `title` attribute starts with `"Quality Check"`

7. In `tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx`, add test `AST-1771: detail rows match importance+grade order`:

   - Render with fixture `grades` + `rubricItems={rubric}` (no live artifact required)
   - `screen.getAllByClassName` or query `.analysis-vector` — first text matches `/Quality Check/`, second matches `/Embedded/` or `/Firmware/`

8. In `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx`, extend `AST-1328: Analysis header uses job-carried jd_rubric when live jobdesc_rubric underlaps`:

   - After existing cell-count asserts, assert header dot order (QC/B before EFW/A) same as step 6
   - Expand JD Analysis section (click section header / chevron per existing AST-950 patterns in this file)
   - Assert `.analysis-vector` order matches header order (QC before EFW)

9. Run component tests scoped to this ticket:

   ```bash
   cd src/ui/frontend && npm run test:component -- \
     ../../../tests/component/frontend/lib/test_rubricDisplay.test.ts \
     ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
     ../../../tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx \
     ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
     --testNamePattern="AST-1771|AST-1328|sortRubricColumnsByImportanceAndGrade|formatGradeDotTooltipWithVectorLabel|gradeRank"
   ```

10. Commit on epic worktree: `test(AST-1771): Recommended Analysis vector order and tooltips`.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

```
[plan-rubric]
**Ticket:** AST-1771
**Overall:** APPROVED
**Corpus:** 2ac86c3f69
**Publish ref:** `sub/AST-1770/AST-1771-recommended-analysis-vector-order-and-tooltips` @ `94fce7f2135c53f6ca1ab536dacce2b58e001f1d`

## Canon scores

(no directives on frozen Canon Scope — child Citations: none (active catalog); parent declares no applicable statutes; presentational frontend-only slice; nothing to score)

## Traceability

AC1→S2.3,S3.6,8 · AC2→S2.7-8,S3.7,8 · AC3→S1.3,S2.4,S3.5-6 · AC4→S1.2⚠️,S2.5,S2.9

## Findings

### discuss — Assignee gate (procedural)

- **Severity:** discuss
- **Location:** Linear ticket state
- **Finding:** Status is Plan Ready (valid), but assignee is Katherine Johnson, not Joan. `validate-plan` §1 expects Joan assigned before this pass.
- **Recommendation:** Chuckles restores implementer after posting; no plan change.

### discuss — Empty Canon Scope is intentional

- **Severity:** discuss
- **Location:** Ticket Description Citations; parent Architectural definition
- **Finding:** Frozen directive list is empty by dispatch design ("none (active catalog)"), not an omitted Canon Scope. Parent explicitly states no active-catalog statutes govern rubric display ordering; AST-1063 / AST-1321 are honor-only job-carried rubric conventions, not scored directives.
- **Recommendation:** No Canon Scope amendment required unless Archie wants Radia comparability on placement/scope statutes for this frontend slice.

### discuss — Canon Scope gap (do not score)

- **Severity:** discuss
- **Location:** Plan footprint vs frozen list
- **Finding:** `astral.standards.in-scope-only` plainly governs the shared-component blast radius but is absent from the frozen list. Plan behavior stays inside the ticket's Files Changed table and parent Component scope.
- **Recommendation:** Archie may amend Canon Scope at Discussion if scope discipline should be an explicit graded column for interface children; do not widen the list in-flight.

### discuss — AgentAnalysisHeader is a shared component

- **Severity:** discuss
- **Location:** Stage 2 §6–8; `AgentAnalysisHeader.tsx` consumers
- **Finding:** Sorting inside `AgentAnalysisHeader` also affects `AgentStoryTab` (entity story grades), not only `JobAnalysisReportModal`. Parent Component scope names this file; boundaries exclude list tables and Summary/Artifacts tabs but not story panes. Existing `test_AgentStoryTab.test.tsx` uses a single vector and should not regress; multi-vector story entries would reorder by grade when `rubricItems` is absent.
- **Recommendation:** Optional one-line blast-radius note in the plan for UAT awareness; acceptable side effect unless Susan wants story-tab order frozen (then sort at the Recommended modal call site instead).

### acceptable — New test file

- **Severity:** acceptable
- **Location:** Stage 3 §7; Files Changed table
- **Finding:** `test_AgentAnalysisHeader.test.tsx` does not exist on the branch yet; plan correctly creates it. Consistent with parent Component scope.
- **Recommendation:** None.

### acceptable — Confidence now included in header tooltips

- **Severity:** acceptable
- **Location:** Stage 2 §4 vs current `gradeAndConfidenceForCol` (reason only, no confidence in `formatGradeDotTooltip`)
- **Finding:** Plan explicitly passes `confidence` into `formatGradeDotTooltipWithVectorLabel`, fixing a pre-existing gap relative to list-table tooltips.
- **Recommendation:** None.

### acceptable — AC4 guard is explicit

- **Severity:** acceptable
- **Location:** Stage 1 §2 ⚠️ Decision; Stage 2 §5, §9
- **Finding:** New `sortRubricColumnsByImportanceAndGrade` leaves `sortJobListRubricColumns` untouched; `buildPhaseTabGradeDots` stays on importance+code sort; grep verification step guards JobsInReview/JobsSkipped.
- **Recommendation:** None.

## R6 checklist (summary)

- Definition fidelity: plan implements parent Purpose/Functional scope for Recommended Analysis header row, detail body, and tooltip prefix; no scope creep into list tables, persistence, or consult scoring.
- Files Changed and Stages align with ticket `## Scope` and parent Component scope.
- DRY: new helpers in `rubricDisplay.ts` rather than duplicating sort in two call sites; does not extend `sortJobListRubricColumns` (correct per AC4).
- Missing `## Self-assessment` section: minor hygiene only (sibling plans often carry one); estimate confirm line present; no `!!-NONE` conf gap.
- Fixture contract (QC/5/B before EFW/1/A) matches parent AC wording and extends existing AST-1328 tests with order assertions the current tests lack.
```
