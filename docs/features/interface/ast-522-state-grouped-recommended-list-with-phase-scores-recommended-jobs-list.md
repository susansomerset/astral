# State-grouped Recommended list with phase scores (Recommended Jobs List)

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-522/state-grouped-recommended-list-with-phase-scores-recommended-jobs-list  
**Parent:** https://linear.app/astralcareermatch/issue/AST-498/recommended-jobs-list  

**Publish ref (origin):** `sub/AST-498/AST-522-state-grouped-recommended-list-with-phase-scores`  
**Parent integration ref:** `ftr/AST-498-recommended-jobs-list`  

Rebuild **`JobsRecommended.tsx`** so the Recommended landing page groups jobs into three config-driven sections (**Recommended**, **In Progress**, **Ready**) by job state, shows plain numeric **JD / DO / GET / LIKE** phase scores (already flattened by **`GET /api/jobs?view=recommended`**), supports per-section sorting, and preserves Skip / View Job Analysis / row-detail entry points. Does **not** implement the full report modal (**AST-499**).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `JOBS_RECOMMENDED_UI_SECTIONS`, `JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS`; extend `build_state_ui_manifest()` with `jobs.recommended` | utils |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Extend `StateUiManifest` + `EMPTY` default for `jobs.recommended` | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Replace flat LIKE-rubric table with state-grouped sections + phase score columns + per-section sort | ui |
| `tests/component/utils/test_config.py` | Assert manifest `jobs.recommended` sections and phase columns | utils |
| `tests/component/frontend/pages/test_JobsRecommended.test.tsx` | Replace rubric-column assertions with section + phase score coverage | ui |

**Not in scope:** `api_jobs.py` (already flattens `jd_score`, `do_score`, `get_score`, `like_score` via `_flatten_grades`), `JobAnalysisReportModal`, consult scoring, Skipped / In Review pages, heat-map styling, **AST-499**.

**Verified (plan time):** `list_jobs(states=list(RECOMMENDED_JOB_STATES))` + `_flatten_grades` already expose phase scores at top level — no duplicate flatten logic in the frontend.

---

## Stage 1: Config + state UI manifest

**Done when:** `build_state_ui_manifest()["jobs"]["recommended"]` returns section order/labels and phase score column defs aligned with `RECOMMENDED_JOB_STATES`; `python3 -m py_compile src/utils/config.py` passes; config test updated and green.

1. In `src/utils/config.py`, immediately after `JOBS_IN_REVIEW_UI_SECTIONS`, add:

   ```python
   JOBS_RECOMMENDED_UI_SECTIONS = [
       {"state": "RECOMMENDED", "label": "Recommended"},
       {"state": "BUILD_ARTIFACTS", "label": "In Progress"},
       {"state": "CANDIDATE_REVIEW", "label": "Ready"},
   ]

   JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS = [
       {"field": "jd_score", "label": "JD"},
       {"field": "do_score", "label": "DO"},
       {"field": "get_score", "label": "GET"},
       {"field": "like_score", "label": "LIKE"},
   ]
   ```

2. Assert every `JOBS_RECOMMENDED_UI_SECTIONS[].state` is in `RECOMMENDED_JOB_STATES` (same file, inline `assert` block like other manifest guards).

3. In `build_state_ui_manifest()`, inside the `"jobs"` dict, add:

   ```python
   "recommended": {
       "sections": [
           row for row in JOBS_RECOMMENDED_UI_SECTIONS
           if row["state"] in RECOMMENDED_JOB_STATES
       ],
       "phase_score_columns": list(JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS),
   },
   ```

   Keep section order identical to `JOBS_RECOMMENDED_UI_SECTIONS` (not alphabetical).

4. In `tests/component/utils/test_config.py`, class `TestBuildStateUiManifest`, extend `test_manifest_contains_expected_sections` (or add a sibling test) to assert:
   - `manifest["jobs"]["recommended"]["sections"]` has three entries with states `RECOMMENDED`, `BUILD_ARTIFACTS`, `CANDIDATE_REVIEW` in that order.
   - `manifest["jobs"]["recommended"]["phase_score_columns"]` maps to fields `jd_score`, `do_score`, `get_score`, `like_score`.

5. Run `python3 -m py_compile src/utils/config.py`.

⚠️ **Decision:** Section labels live in config/manifest (not hardcoded in TS) per **ASTRAL_CODE_RULES §1.4** and ticket boundary “config-driven state lists.” Phase column labels are also manifest-driven so consult phase renames stay server-side.

---

## Stage 2: `StateUiContext` manifest mirror

**Done when:** `cd src/ui/frontend && npx tsc -b --noEmit` passes with updated types.

1. In `src/ui/frontend/src/contexts/StateUiContext.tsx`, extend `StateUiManifest["jobs"]` with:

   ```typescript
   recommended: {
     sections: Array<{ state: string; label: string }>
     phase_score_columns: Array<{ field: string; label: string }>
   }
   ```

2. Add matching defaults to the `EMPTY` constant (same three sections and four phase columns as `config.py` defaults) so first paint matches server before `GET /api/state_ui_manifest` returns.

3. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

---

## Stage 3: Rebuild `JobsRecommended.tsx`

**Done when:** Recommended page renders grouped sections with JD/DO/GET/LIKE numeric cells, per-section sort, Actions (Skip + Jr), row click → detail modal, Jr → analysis modal; no LIKE rubric grade-dot columns; `tsc` passes.

1. **`git fetch origin && git merge origin/dev`** on `dev-kath`, then **`git merge origin/sub/AST-498/AST-522-state-grouped-recommended-list-with-phase-scores`** before editing (build-astral habit).

2. Replace imports: remove `buildJobListRubricColumns`, `formatGradeDotTooltip`, `RUBRIC_DEFAULT_IMPORTANCE`, `JobListRubricColumn`, and all rubric/grade-dot helpers. Add `useStateUi` from `../contexts/StateUiContext`.

3. Extend local `Job` interface with optional numeric fields: `jd_score?: number | null`, `do_score?: number | null`, `get_score?: number | null`, `like_score?: number | null`. Remove reliance on `like_grades` for column rendering.

4. Add module-level helper **`formatPhaseScore(value: unknown): string`** — if `value` is a finite number, return `value.toFixed(1)`; otherwise return `"\u2014"` (em dash). No heat-map classes.

5. Add module-level **`sortRecommendedJobs(jobs: Job[], col: string, asc: boolean, phaseFields: string[]): Job[]`** — copy the comparison structure from `JobsInReview.tsx` `sortJobs` for `job_title`, `company`, `state_changed_at`; for each `phaseFields` entry, compare numeric values with nulls sorting last (same null-last pattern as `latest_score` in In Review). Do **not** import grade-order logic.

6. Replace single global `sort` state with **`sorts: Record<string, SortState>`** keyed by section `state` (same pattern as `JobsInReview.tsx`).

7. Build **`sections`** via `useMemo`:
   - Group `rows` by `job.state`.
   - Iterate `stateUi.jobs.recommended.sections` in manifest order.
   - Include a section only when `byState[state]?.length > 0` (hide empty sections).
   - Each section object: `{ state, label, jobs }`.

8. Replace the single flat `<table>` with **`sections.map(sec => …)`** rendering:
   - A static section header (not collapsible): `<h2>` or styled `<div>` showing `{sec.label} ({sec.jobs.length})` — always expanded.
   - One `<table className="list-page-table">` per section with columns in order:
     - **Actions** (not sortable)
     - **Job Title** (sortable)
     - **Company** (sortable)
     - Each `stateUi.jobs.recommended.phase_score_columns` entry: header `{col.label}`, sort key `{col.field}`, cell `formatPhaseScore(job[col.field])`, centered
     - **Updated** (sortable, key `state_changed_at`) — rename from “Passed At”
   - Remove the **`latest_score`** column entirely.
   - Remove all rubric / grade-dot columns.

9. Per-section sort handlers: `handleSort(sectionState, col)` and `sortIndicator(sectionState, col)` matching In Review’s `Record<string, SortState>` pattern; default sort `{ col: "state_changed_at", asc: false }` per section when unset.

10. Row body unchanged for interactions:
    - `<CandidateJobRowActions state={job.state} onSkip=… onViewAnalysis=… onAction=… />` with `stopPropagation` on actions cell.
    - Row `onClick` → `setViewingId(job.astral_job_id)`.
    - Keep `JobDetailModal`, `JobAnalysisReportModal`, `CandidateActionNotesModal`, `Toast`, `useCandidateJobActions(load)`.

11. Empty page: when `sections.length === 0` after load, show existing copy **“No recommended jobs yet”** (not three empty section headers).

12. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

⚠️ **Decision:** Sections are **always expanded** (no collapse chevron). Recommended is the default jobs landing route; hiding rows behind collapse would fight “triage at a glance.” In Review keeps collapse because it has many pipeline states.

⚠️ **Decision:** Hide empty sections (do not render “Ready (0)”). Matches In Review filtering and parent allowance for empty-section presentation.

---

## Stage 4: Component tests

**Done when:** `cd src/ui/frontend && npx vitest run tests/component/frontend/pages/test_JobsRecommended.test.tsx` passes.

1. Replace mock job fixtures to include `jd_score`, `do_score`, `get_score`, `like_score` instead of `like_grades` for display assertions.

2. Add fixture coverage with **three jobs** in states `RECOMMENDED`, `BUILD_ARTIFACTS`, and `CANDIDATE_REVIEW` (one job each). Assert all three section labels appear (“Recommended”, “In Progress”, “Ready”) and each job title appears under the correct section header block.

3. Assert phase column headers **JD**, **DO**, **GET**, **LIKE** are present (not rubric codes like **TE**).

4. Assert a job with `jd_score: 8.5` renders **8.5** (or **8.5** via toFixed) and a job with missing `like_score` renders em dash in the LIKE column.

5. Update sort test: click **Company** column header within a section; verify order changes (keep existing pattern but drop rubric **TE** / **Score** column clicks).

6. Keep existing Skip / View Job Analysis tests; adjust mocks so row states remain `RECOMMENDED` or `CANDIDATE_REVIEW` as today.

7. Remove assertions that expect rubric grade-dot columns or **`latest_score`** header **Score**.

8. Run vitest for this file only.

---

## Stage 5: Verify

**Done when:** Typecheck + targeted tests green; no new dependencies.

1. `cd src/ui/frontend && npx tsc -b --noEmit`
2. `cd src/ui/frontend && npx vitest run tests/component/frontend/pages/test_JobsRecommended.test.tsx`
3. `python3 -m py_compile src/utils/config.py`

---

## Execution contract (developer agent)

Per **plan-astral** / **build-astral**: execute stages in order; one commit per stage on `dev-kath` with subject containing **`AST-522`**, then cherry-pick each stage SHA to **`origin/sub/AST-498/AST-522-state-grouped-recommended-list-with-phase-scores`** via detached `/tmp/astral-kath-pub-AST-522-*` worktree only. If manifest shape or API payload differs from what this plan assumes, **stop** with **🛑** comment on **AST-522** (parent **AST-498** only if cross-cutting) — do not invent API fields or hardcode state lists in the frontend.

Blocking question format:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope — `Single-Component`**  
One page rewrite plus config manifest wiring, context types, and focused tests — no new API routes or consult pipeline changes.

**Conf — `high`**  
`_flatten_grades` already exposes phase scores; In Review provides a proven section + per-section sort pattern; state membership stays in `RECOMMENDED_JOB_STATES` / manifest.

**Risk — `Medium`**  
Wrong section grouping or sort comparator bugs would mis-triage jobs on the primary landing page, but scope is isolated to Recommended UI and manifest defaults.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| **§1.3 DRY** | Reuses In Review section/sort structure; phase format helper is local to one page (no premature shared module). |
| **§1.4 / §2.1 config** | Section order, labels, and phase column defs live in `config.py` + manifest — not duplicated as TS state lists. |
| **§2.4 batch** | N/A — read-only list UI. |
| **§2.6 state machine** | No new transitions; uses existing `RECOMMENDED_JOB_STATES` filter on API. |
| **§3.3 imports** | UI-only changes; no layer violations. |
| **§3.5 naming / placement** | Edits stay in `pages/JobsRecommended.tsx`, `contexts/StateUiContext.tsx`, `config.py`, existing test paths — no new component files. |

No **conf-!!-NONE** conflicts identified.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-498/AST-522-state-grouped-recommended-list-with-phase-scores` @ `d78b57ce`

**Build:** Katherine — stages 1–3 (config manifest, StateUiContext, JobsRecommended). Betty — stage 4 tests + bible §7.13zm.

### What's solid

- Plan fidelity: three manifest-driven sections, JD/DO/GET/LIKE numeric cells, per-section sort keyed by state, empty-section hide, Updated column, rubric/`latest_score` removed; Skip / View Job Analysis / row detail preserved; `stopPropagation` on actions cell (good catch vs plan).
- **§1.4 / §2.1 / G1:** `JOBS_RECOMMENDED_UI_SECTIONS`, phase columns, and `build_state_ui_manifest()["jobs"]["recommended"]` with `RECOMMENDED_JOB_STATES` assert; page reads manifest via `useStateUi` — no hardcoded section lists in render logic.
- **§3.3 layer:** UI + utils/config only; no API duplication; boundaries respected (**AST-499** report modal untouched).
- Tests cover acceptance: three sections, phase headers, score + em dash, per-section Company sort, Skip/analysis, detail modal.

### Issues

| Severity | Location | Issue |
| --- | --- | --- |
| **fix-now** | `docs/ASTRAL_TEST_BIBLE.md` (commit `d78b57ce`) | Bible diff includes ~200 lines for **unrelated** tickets (**§7.13m AST-520**, **§7.13zg–§7.13zi** for AST-504–521, AST-517–519, AST-513, AST-510–511). Only **§7.13zm** + the superseded note on the prior Recommended row belong on this branch — strip the rest before parent UAT to avoid cross-ticket scope smuggling (plan **Single-Component**; **§5d**). |
| **advisory** | `tests/component/frontend/pages/test_JobsRecommended.test.tsx` | Prior test for `GET /api/state_ui_manifest` rejection + EMPTY fallback was removed; behavior still works via `StateUiContext.EMPTY` but is untested — optional restore if Katherine wants regression on offline manifest. |

### Recommended actions

1. **fix-now:** On publish ref, revert bible hunks outside **§7.13zm** (keep §7.13zm + rubric-era supersede note only); re-run narrowed manifest from bible §7.13zm.
2. Cherry-pick this doc commit onto `dev-kath` after resolve.

**Radia:** `docs/features/interface/ast-522-state-grouped-recommended-list-with-phase-scores-recommended-jobs-list.md` (this section) — doc-only commit on publish ref.

---

## Resolution

**2026-05-28** — Katherine resolved Radia **fix-now** on **`docs/ASTRAL_TEST_BIBLE.md`**: reverted unrelated **§7.13m AST-520** expansion and stripped **§7.13zg–§7.13zi** hunks (AST-504–521, AST-517–519, AST-513, AST-510–511) that Betty’s publish had picked up from **`dev-betty`**. Kept **§7.13zm** manifest + the **§7.13y** superseded note on the rubric-era Recommended row only.
