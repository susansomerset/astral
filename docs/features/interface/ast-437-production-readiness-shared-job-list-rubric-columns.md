# Production readiness: shared job-list rubric columns

**Linear:** https://linear.app/astralcareermatch/issue/AST-437/production-readiness-shared-job-list-rubric-columns  
**Parent:** [AST-434](https://linear.app/astralcareermatch/issue/AST-434/production-readiness-job-list-rubrics-ui-promptrubric-diagnostic)  
**Feature ref:** `sub/AST-434/AST-437-production-readiness-shared-job-list-rubric-columns` (origin only; child of **AST-434** — no `origin/ftr/AST-437`)

Introduce a **shared** job-list rubric column model for tables that show per-vector grades. Visible column headers show the **short vector code only** (e.g. `TE`). Header `title` tooltip shows **`{label} ({importance})`** (e.g. `Title Match (7)`). Rubric columns sort **descending by importance** after fixed columns (Job Title, Company, …). **Skipped** is the readability reference (code in cell, label on tooltip); **In Review** and **Recommended** today render the full `formatRubricVectorHeader` string in the `<th>` and must converge.

**Blocked by:** none for UI-only work. **Sibling:** **AST-438** (admin prompt/rubric diagnostic — out of scope).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/rubricDisplay.ts` | `JobListRubricColumn` type; tooltip helper; importance sort; `buildJobListRubricColumns` from artifact + job-grade fallback | ui |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Use shared builder; importance-ordered cols; tooltip `Label (n)` on `<th>` | ui |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | Replace local `getRubricCols` + `headerText` in `<th>` with shared columns | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Replace `gradeCols` memo with shared builder | ui |
| `tests/component/frontend/pages/test_JobsSkipped.test.tsx` | Optional: assert tooltip/title on rubric header if test touches rubric row | ui |
| `tests/component/frontend/pages/test_JobsInReview.test.tsx` | Same — only if existing assertions break | ui |
| `tests/component/frontend/pages/test_JobsRecommended.test.tsx` | Same | ui |

Do **not** edit `formatRubricVectorHeader` call sites in **`ArtifactEditor.tsx`** or **`AgentAnalysisHeader.tsx`** (full header string remains correct there). Do **not** change consult scoring, `api_jobs` payloads, or rubric artifact save shape.

---

## Stage 1: Shared helpers in `rubricDisplay.ts`

**Done when:** Exported helpers exist; `cd src/ui/frontend && npx tsc -b --noEmit` passes with no page imports yet (or with imports if you add them in the same commit — prefer one commit for this stage = helpers only, pages in Stage 2+).

1. Add exported interface **`JobListRubricColumn`** with fields: `code: string`, `label: string`, `importance: number`, `headerCode: string`, `headerTooltip: string`.

2. Add **`formatRubricColumnTooltip(label: string | undefined, importance: number | undefined): string`** — returns `` `${lab} (${imp})` `` where `lab = (label ?? "").trim() || "??"` and `imp` uses the same 1–10 clamp as `rubricItemImportance` (call `rubricItemImportance({ importance })` when importance is passed on an object, or accept a bare number).

3. Add **`resolveRubricHeaderCode(item: { code?: string; label?: string }): string`** — return `item.code || item.label?.slice(0, 2).toUpperCase() || "??"` (same as existing page logic).

4. Add **`sortJobListRubricColumns(cols: JobListRubricColumn[]): JobListRubricColumn[]`** — return a **new** array sorted by **`importance` descending**, then **`code` ascending** tiebreaker (stable enough for UI).

5. Add **`buildJobListRubricColumnsFromArtifact(items: Array<{ code?: string; label?: string; importance?: unknown }>): JobListRubricColumn[]`** — map each item to `{ code, label, importance: rubricItemImportance(item), headerCode: resolveRubricHeaderCode(item), headerTooltip: formatRubricColumnTooltip(item.label || item.code, rubricItemImportance(item)) }`, then **`sortJobListRubricColumns`**.

6. Add **`buildJobListRubricColumnsFromJobGrades(gradeKey: string, jobs: Array<Record<string, unknown>>): JobListRubricColumn[]`** — copy the fallback branch from **`JobsInReview.tsx`** `getRubricCols` (first job with `job[gradeKey]` array or object keys); for fallback rows use `importance: RUBRIC_DEFAULT_IMPORTANCE` and `headerTooltip: formatRubricColumnTooltip(label, RUBRIC_DEFAULT_IMPORTANCE)`; do **not** call `formatRubricVectorHeader` here.

7. Add **`buildJobListRubricColumns(opts: { rubricArtifactKey?: string; artifacts: Record<string, unknown>; gradeKey: string; jobs: Array<Record<string, unknown>> }): JobListRubricColumn[]`** — if `rubricArtifactKey` and `artifacts[rubricArtifactKey]` is a non-empty array, return `buildJobListRubricColumnsFromArtifact(...)`; else return `buildJobListRubricColumnsFromJobGrades(gradeKey, jobs)`.

⚠️ **Decision:** Keep **`formatRubricVectorHeader`** unchanged for artifact editor / analysis headers; job-list tables use the new compact header + tooltip helpers only.

---

## Stage 2: `JobsSkipped.tsx` (reference parity)

**Done when:** Skipped rubric headers show **code** only; `title` on `<th>` is `Label (n)`; column order matches importance when artifact rows carry `importance`; bulk-retry and floor section behavior unchanged.

1. Import `buildJobListRubricColumns` from `../lib/rubricDisplay`.

2. Extend local **`RubricItem`** type to include optional **`importance?: number`** (or import a shared type from `rubricDisplay` if exported).

3. Replace **`getRubricCols`** body with:

   ```typescript
   const rubricKey = stateUi.jobs.grade_rubric_by_field[gradeKey]
   return buildJobListRubricColumns({
     rubricArtifactKey: rubricKey || undefined,
     artifacts,
     gradeKey,
     jobs,
   })
   ```

4. In `<thead>`, for rubric columns change `title={c.label}` to **`title={c.headerTooltip}`** and keep visible text **`{c.code}`** (not `headerCode` — must equal `code`).

5. In grade cells, keep **`gradeDot(cell.grade, c.label)`** (dot tooltip = human label; header tooltip = `Label (n)` per AC).

6. Run `npx tsc -b --noEmit`.

---

## Stage 3: `JobsInReview.tsx`

**Done when:** In Review rubric `<th>` cells show **short code only**; tooltip `Label (n)`; columns importance-ordered; section expand/collapse and sort unchanged.

1. Change **`ColHeader`** usage to **`JobListRubricColumn`** (import from `rubricDisplay`; remove `headerText` field).

2. Replace **`getRubricCols`** with `buildJobListRubricColumns` (same `opts` pattern as Stage 2, using `stateUi.jobs.grade_rubric_by_field[gradeKey]`).

3. In `<thead>` rubric headers: **`title={c.headerTooltip}`**, visible text **`{c.headerCode}`** (or `{c.code}`).

4. In tbody, change **`gradeDot(cell.grade, c.headerText)`** to **`gradeDot(cell.grade, c.label)`** (or `c.headerTooltip` — prefer **`c.label`** to match Skipped).

5. Remove unused imports: **`formatRubricVectorHeader`**, **`rubricItemImportance`** if no longer referenced in this file.

6. Run `npx tsc -b --noEmit`.

---

## Stage 4: `JobsRecommended.tsx`

**Done when:** Recommended matches In Review / Skipped compact header behavior; `like_rubric` artifact drives order; single-table sort unchanged.

1. Replace **`gradeCols`** `useMemo` with `buildJobListRubricColumns({ rubricArtifactKey: "like_rubric", artifacts, gradeKey: "like_grades", jobs: rows })` (cast `rows` as needed).

2. Update **`ColHeader`** type to **`JobListRubricColumn`**; fix sort fallback object (lines ~107–112) to include `headerCode` / `headerTooltip` or use `code` only.

3. Update `<thead>`: **`title={c.headerTooltip}`**, visible **`{c.headerCode}`**.

4. Update **`gradeDot(g, c.headerText)`** → **`gradeDot(g, c.label)`**.

5. Remove unused `formatRubricVectorHeader` / `rubricItemImportance` imports.

6. Run `npx tsc -b --noEmit`.

---

## Stage 5: Tests and verify

**Done when:** Vitest for the three job pages passes; manual smoke on In Review + Recommended + Skipped confirms Susan AC1.

1. From repo root (match existing frontend test invocation):

   ```bash
   cd src/ui/frontend && npm run test:component -- \
     ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
     ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx \
     ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
   ```

2. If a test fails because columnheader name changed from a long header string to a short code, update the test to click/query by **code** (e.g. `/TE/`) only — do not revert compact headers.

3. Optional unit tests in **`tests/component/frontend/lib/`** for `sortJobListRubricColumns` and `formatRubricColumnTooltip` — add only if Stage 5 failures need coverage; not required if page tests pass.

4. Smoke: with a candidate that has `like_rubric` / section rubrics with varied `importance`, confirm In Review and Recommended show codes in headers, hover shows `Label (n)`, left-to-right rubric order is highest importance first after Company column.

---

## Execution contract (for the developer agent)

- Execute stages in order; one commit per stage on **`dev-kath`**; publish each stage commit to **`origin/sub/AST-434/AST-437-production-readiness-shared-job-list-rubric-columns`** per **build-astral** §6 (cherry-pick; commit subject includes **`AST-437`**).
- Do **not** change **`JobsApplied.tsx`** / **`JobsResponded.tsx`** (no rubric columns today).
- If artifact rows lack `importance`, behavior must match **AST-359** default (5) via `rubricItemImportance`.
- On ambiguity about tooltip format, use **`{label} ({importance})`** exactly — not the `formatRubricVectorHeader` `imp - label (code)` pattern.

---

## Self-Assessment

**Scope — `Single-Component`**  
One shared lib module plus three job-list pages and targeted frontend tests — UI only, no API or core.

**Conf — `high`**  
Skipped already implements the target header pattern; work is extracting shared helpers and aligning two pages that still use `formatRubricVectorHeader` in `<th>`.

**Risk — `low`**  
Display-only change; grade matching and sort keys stay keyed by `code`; consult scoring untouched.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.3 DRY | Single `buildJobListRubricColumns` path for all three pages; remove duplicated `getRubricCols` / normalize logic. |
| §2.1 config | Importance default from `rubricItemImportance` / `RUBRIC_DEFAULT_IMPORTANCE` — no magic numbers in pages. |
| §2.4 batch | N/A. |
| §2.6 state machine | N/A. |
| §3.3 imports | Pages import `lib/rubricDisplay` only. |
| §3.5 naming | Keep `Jobs*` page names; new exports live in `rubricDisplay.ts`. |

**Conflicts:** None.

---

## Review (build)

**Branch:** `sub/AST-434/AST-437-production-readiness-shared-job-list-rubric-columns`  
**Commit:** `3ca7dbe2` (see Linear build comment)

## Radia review

**Reviewed:** `origin/dev`…`origin/sub/AST-434/AST-437-production-readiness-shared-job-list-rubric-columns` (no `origin/ftr/AST-437`; AST-434 sub-issue).

### What's solid

| Area | Notes |
|------|--------|
| Plan fidelity | Shared `rubricDisplay.ts`: compact `headerCode`, tooltip `Label (n)`, importance-desc sort; In Review, Recommended, Skipped wired through `buildJobListRubricColumns`. |
| Boundaries | Display-only; no consult scoring or AST-438 diagnostic scope. |
| Tests | `test_rubricDisplay.test.ts` covers builders, sort, tooltip. |
| G1 | Uses artifact importance / `RUBRIC_DEFAULT_IMPORTANCE`; no hardcoded job state strings added. |

### Issues

| Severity | Item |
|----------|------|
| **fix-now** | 0 |
| **discuss** | 0 |
| **advisory** | 1 — Confirm Susan UAT on In Review + Recommended parity with Skipped readability (acceptance criterion 1). |

### Recommended actions

| Action | Owner |
|--------|--------|
| Cherry-pick doc commit onto `dev-kath` | Katherine |

## Resolution (resolve-astral 2026-05-18)

- **fix-now / discuss:** None — no product code changes required.
- **Advisory:** Left for Susan UAT on parent **AST-434** (In Review + Recommended header parity with Skipped).
- **Doc:** Radia review section integrated; build commit SHA recorded above.

— Katherine
