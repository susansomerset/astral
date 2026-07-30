# Group-by-aligned-rubric Jobs list tables

**Linear:** [AST-1064](https://linear.app/astralcareermatch/issue/AST-1064/group-by-aligned-rubric-jobs-list-tables-issue-with-the-rubric-grade)  
**Parent:** [AST-1059 — Issue with the rubric grade displays on the Jobs List pages](https://linear.app/astralcareermatch/issue/AST-1059/issue-with-the-rubric-grade-displays-on-the-jobs-list-pages)  
**Publish ref (origin):** `sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`  
**Parent integration ref:** `ftr/AST-1059-rubric-grade-displays-jobs-list`  
**Blocked by:** [AST-1063](https://linear.app/astralcareermatch/issue/AST-1063/job-carried-rubric-hydration-for-list-columns-issue-with-the-rubric) (job-carried `*_rubric` + score flatten on list payloads — already on parent `ftr`)

On Skipped and In Review Jobs list pages, stop building grade columns from the **live** candidate rubric artifact. Within each state section that shows per-vector grade-dots, **group jobs by aligned job-carried rubric fingerprint**, render **one table per group** with headers/tooltips from that group’s hydration, paint grade-dots from stored grades under matching columns, and paint Score from **analysis-time job score** for that section’s grade field. Does **not** change API hydration shape, Recommended phase-score UI, re-grading, or live rubric edits.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`; `git merge origin/dev`; `git merge origin/ftr/AST-1059-rubric-grade-displays-jobs-list`; merge-clean (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).
2. Confirm list JSON already lifts `joblist_rubric` / `jd_rubric` / `get_rubric` / `do_rubric` / `like_rubric` via AST-1063 (`_flatten_grades` in `api_jobs.py`). Do **not** edit `consult.py` or `api_jobs.py` in this ticket.
3. Do **not** touch Recommended pages or meteorite GDL.

---

## Contract consumed (AST-1063 — do not re-implement)

| Section `gradeKey` (`JOBS_*_GRADE_FIELD` / manifest `grade_field_by_job_state`) | Job-carried rubric on job JSON | Analysis-time score key |
|---|---|---|
| `joblist_grades` | `joblist_rubric` | `joblist_score`, else `latest_score` |
| `jd_grades` | `jd_rubric` | `jd_score`, else `latest_score` |
| `get_grades` | `get_rubric` | `get_score`, else `latest_score` |
| `do_grades` | `do_rubric` | `do_score`, else `latest_score` |
| `like_grades` | `like_rubric` | `like_score`, else `latest_score` |

Convention: `gradeKey.replace("_grades", "_rubric")` / `"_score"`. Each `*_rubric` is a list of `{ code, label, importance, grade_descriptions }` (no `content`). Absent/empty `*_rubric` = pre-snapshot job → **grades-only fallback** defined below.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/rubricDisplay.ts` | Job-carried key helpers; rubric fingerprint; group-by-aligned; column build preferring job-carried over live artifact; analysis-time score resolver | ui (frontend lib) |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Per-section group → multiple tables; drop live-artifact column source; Score from analysis-time field | ui |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | Same grouping / column / Score rules as Skipped (grade-dot sections) | ui |

**Out of scope:** `src/core/consult.py`, `src/ui/api/api_jobs.py`, Recommended pages, `JobAnalysisReportModal`, candidate artifact editors, `tests/` / bible (Betty), backfill of historical `*_rubric`.

---

## Stage 1: Job-carried helpers in `rubricDisplay.ts`

**Done when:** Pure helpers (no React) can (a) map `gradeKey` → rubric/score keys, (b) fingerprint a job’s aligned rubric shape, (c) partition a job list into ordered groups, (d) build `JobListRubricColumn[]` from a group’s job-carried rubric (or grades-only fallback), and (e) resolve display score for a row — without reading `candidate_data.artifacts`.

1. Add:

   ```ts
   export function jobCarriedRubricKey(gradeKey: string): string {
     return gradeKey.replace(/_grades$/, "_rubric")
   }

   export function jobCarriedScoreKey(gradeKey: string): string {
     return gradeKey.replace(/_grades$/, "_score")
   }
   ```

   If `gradeKey` is empty or does not end with `_grades`, return `""` (callers skip rubric grouping).

2. Add fingerprint of **aligned shape** (same criteria identity → same table; order of criteria in the snapshot must not split groups):

   ```ts
   export function jobListRubricFingerprint(
     rubricItems: Array<{ code?: string; label?: string }> | null | undefined,
   ): string
   ```

   - Empty / non-array → `""`.
   - For each item, identity token = `normalizeRubricVectorKey(label || code || "")` plus `|` plus `(code || "").trim().toUpperCase()`.
   - Drop empty tokens; **sort** tokens ascending; join with `\0`.
   - Do **not** include importance or `grade_descriptions` in the fingerprint (display-only).

3. Add grades-only fallback fingerprint when `*_rubric` is missing/empty but grades exist:

   ```ts
   export function jobListRubricFingerprintFromGrades(
     grades: unknown,
   ): string
   ```

   - Array of `{ vector }`: tokens = `normalizeRubricVectorKey(vector)` for each; sort; join `\0`.
   - Object map: tokens = normalized keys; sort; join.
   - Else `""`.

4. Add grouping:

   ```ts
   export type JobListRubricGroup<T extends Record<string, unknown> = Record<string, unknown>> = {
     fingerprint: string
     jobs: T[]
     /** First job in group used as column source (stable: first encounter order). */
     columnSourceJob: T
   }

   export function groupJobsByAlignedRubric<T extends Record<string, unknown>>(
     jobs: T[],
     gradeKey: string,
   ): JobListRubricGroup<T>[]
   ```

   Per job:
   - `rubricKey = jobCarriedRubricKey(gradeKey)`.
   - If `job[rubricKey]` is a non-empty array → fingerprint via `jobListRubricFingerprint`.
   - Else if grades at `job[gradeKey]` yield a non-empty grades fingerprint → use `"grades:" + that` (prefix so it never collides with a real rubric fp).
   - Else fingerprint `"__empty__"` (jobs with neither rubric nor grades share one no-column / dash table).
   - Emit groups in **first-seen fingerprint order**; append jobs to matching group preserving relative order within the group.

⚠️ **Decision:** Fingerprint ignores importance / descriptions so two jobs with the same criteria labels/codes but different importance metadata still share a table; column headers come from the **first** job’s rubric snapshot (importance-sorted via existing `buildJobListRubricColumnsFromArtifact`).

5. Add column builder that **never** reads live artifacts:

   ```ts
   export function buildJobListRubricColumnsForGroup(opts: {
     gradeKey: string
     columnSourceJob: Record<string, unknown>
   }): JobListRubricColumn[]
   ```

   - `items = columnSourceJob[jobCarriedRubricKey(gradeKey)]`.
   - If non-empty array → `buildJobListRubricColumnsFromArtifact(items)` (existing importance sort + tooltips + grade_descriptions).
   - Else → `buildJobListRubricColumnsFromJobGrades(gradeKey, [columnSourceJob])` (existing path).
   - Do **not** call `buildJobListRubricColumns` with `artifacts` / `rubricArtifactKey` from this helper.

6. Deprecate live-artifact preference for list pages only — leave `buildJobListRubricColumns` intact for any other callers (`JobAnalysisReportModal`, tests). Add a one-line comment above `buildJobListRubricColumns`: list Skipped/In Review must use `buildJobListRubricColumnsForGroup` (AST-1064); live artifact path remains for non-list consumers until separately migrated.

7. Add score resolver:

   ```ts
   export function analysisTimeScoreForJob(
     job: Record<string, unknown>,
     gradeKey: string,
   ): number | null
   ```

   - If `gradeKey` empty → return `typeof job.latest_score === "number" ? job.latest_score : null` (floor section).
   - Else read `job[jobCarriedScoreKey(gradeKey)]`; if number, return it.
   - Else if `typeof job.latest_score === "number"`, return it.
   - Else `null`.

⚠️ **Decision:** Prefer `{prefix}_score` over `latest_score` so JD / get / do / like sections show the score from the same analysis epoch as the grades, not a later phase’s `latest_score`.

---

## Stage 2: `JobsSkipped.tsx` — group-by tables + Score

**Done when:** Each non-floor section with a `gradeKey` renders **N** `list-page-table` blocks (N = number of aligned-rubric groups). Headers/tooltips come from job-carried rubric (or grades fallback). Grade-dots match stored vectors (meteorite-somerset style rows fill cells, not dashes, when grades+rubric align). Score cells use `analysisTimeScoreForJob`. Floor / below-dispatch section unchanged (no grade columns; still uses `latest_score` / floor columns). Live `candidates[].candidate_data.artifacts` is **not** used for column build.

1. Remove `artifacts` `useMemo` and stop importing/using `buildJobListRubricColumns` with `manifest.jobs.grade_rubric_by_field`. Import `groupJobsByAlignedRubric`, `buildJobListRubricColumnsForGroup`, `analysisTimeScoreForJob` from `rubricDisplay`.

2. Keep existing section construction (`virtual_skip` floor, state sections, legacy unmapped) unchanged.

3. Inside each expanded **non-floor** section with `sec.gradeKey`:
   - `const groups = groupJobsByAlignedRubric(sec.jobs as …, sec.gradeKey)`.
   - For each group, build `cols = buildJobListRubricColumnsForGroup({ gradeKey: sec.gradeKey, columnSourceJob: group.columnSourceJob })`.
   - Sort key for this table: `${sec.state}::${group.fingerprint}` (update `sorts` / `handleSort` / `sortIndicator` to take that composite key so tables sort independently).
   - Render **one** `<div className="list-page-table-wrap"><table>…</table></div>` per group (same column structure as today: Actions, checkbox, title, company, rubric cols, Score if any row has score, Failed At).
   - `showScore` per group: `group.jobs.some(j => analysisTimeScoreForJob(j, sec.gradeKey) != null)`.
   - Score cell / sort comparator: use `analysisTimeScoreForJob` instead of raw `job.latest_score` for grade-dot tables. Keep floor section on `latest_score` / `dispatch_score_floor` as today.

4. Happy path: all jobs same fingerprint → still **one** table under the section (AC6).

5. Preserve `gradeAndConfidenceForCol` / confidence bullets / row actions behavior — only change which `cols` and which job subset feed each table.

6. Do **not** change bulk retry, expand policy (still one expand control per `sec.state` wrapping all group tables), or JobDetailModal.

---

## Stage 3: `JobsInReview.tsx` — same rules

**Done when:** In Review sections that use `gradeKey` follow the same group-by-aligned-rubric + job-carried columns + `analysisTimeScoreForJob` rules as Skipped. Sections without `gradeKey` stay a single table with no rubric columns.

1. Mirror Stage 2 changes: drop live-artifact `getRubricCols`; use `groupJobsByAlignedRubric` + `buildJobListRubricColumnsForGroup`; composite sort keys; Score via `analysisTimeScoreForJob`.
2. Keep `showScore = Boolean(sec.gradeKey)` at section level **or** per-group `group.jobs.some(… score …)` — prefer per-group so a grades-less subgroup does not force an empty Score column; if `sec.gradeKey` is set but all scores null, still show Score header with em-dashes (match current In Review always-on Score when gradeKey set).
3. Do not add Actions/checkbox columns that In Review does not already have.

---

## Stage 4: Manual smoke (builder)

**Done when:** Local UI against a candidate with (a) two jobs sharing one `joblist_rubric` and (b) one job with a different `joblist_rubric` shape shows **two** tables in that Skipped section with distinct header codes; grades paint under matching headers; Score matches `{prefix}_score` / `latest_score` fallback. A job with grades but no `*_rubric` still gets a grades-fallback table (headers from vector names). Changing live candidate artifact without re-grade does **not** change headers.

1. Use existing fixture / local DB jobs if available; otherwise seed via temporary `debug/spikes/` script (gitignored) that does not land in the commit.
2. Do not commit tests (Betty).

---

## Self-Assessment

**Scope:** `Single-Component` — frontend list lib + Skipped / In Review pages only; API/core already delivered by AST-1063.

**Conf:** `high` — AST-1063 contract and current dash-sea root cause (`buildJobListRubricColumns` + live artifact) are known; grouping is a new pattern but fingerprint + first-job columns are mechanical.

**Risk:** `Medium` — wrong fingerprint splits or merges tables incorrectly; preferring `{prefix}_score` over `latest_score` could surprise if a section’s `latest_score` was the only populated field historically (mitigated by fallback to `latest_score`).

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** Fingerprint / group / column / score helpers live once in `rubricDisplay.ts`; both pages call them — no copy-pasted fingerprint logic.
- **§2.1 config:** Section → `gradeKey` still from State UI manifest (`grade_field_by_job_state`); this ticket does not invent grade-field maps in React. Column *content* comes from job payload, not live artifacts.
- **§2.4 / §2.6:** N/A — no batch or state-machine changes.
- **§3.2 ui-config-driven:** Grouping is presentation of already-resolved job shapes from the API; no new business rules inventing rubric criteria client-side beyond the Archie-approved job-carried fingerprint pattern.
- **§3.3 import-direction:** Frontend only; no UI→data. Does not call consult or invent hydration.
- **§3.5 naming / file placement:** Helpers stay in `lib/rubricDisplay.ts`; pages stay under `pages/`.
- **New pattern:** job-list tables keyed by job-carried rubric fingerprint (parent Architectural definition — Archie-approved).
