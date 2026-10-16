# AST-1967 — Updates to the recommended jobs list page

<!-- linear-archive: AST-1967 archived 2026-10-08 -->

## Linear archive (AST-1967)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1967/updates-to-the-recommended-jobs-list-page  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Recommended list is where the candidate triages post-upshot jobs, but today every decision is one row at a time and the only at-a-glance signal is four numeric phase scores. Opening the Job Analysis Report modal is the only way to see the grade colours and the only place to start an artifact build. This epic brings those signals and actions to the list itself: a per-row Generate Artifacts control, multi-select bulk Skip / Applied / Generate Artifacts, an Analysis toggle (on by default) that lays the modal's grade colours under each job so "more green" jobs stand out, and a sortable Total score. The aim is faster triage of many jobs without opening each report.

## Functional scope

1. **Row-level Generate Artifacts.** Each row whose job can start an artifact build (state `RECOMMENDED` today, i.e. the states where the manifest's `primary_actions_by_state` lists `generate_artifacts`) gets a Generate Artifacts icon action next to Skip / Applied. Clicking it starts the build exactly like the modal's Generate Artifacts button, and the list refreshes (the job moves to In Progress). Rows in other states do not show it.
2. **Multi-select with bulk actions.** Every job row on the page (all sections, including Meteorites) gets a selection checkbox. While one or more jobs are selected, the page header shows three bulk buttons with the selected count: **Skip**, **Applied**, **Generate Artifacts**.
   * **Skip** skips every selected job, using the same per-job skip the row S button uses.
   * **Applied** opens the existing notes modal **once**; on confirm, every selected job is marked Applied with that same note (same per-job candidate action the row A button uses).
   * **Generate Artifacts** starts a build only for selected jobs eligible per capability 1; ineligible selected jobs are left alone, not sent.
   * After any bulk action, a toast reports how many jobs succeeded and how many failed, the list refreshes, and the selection clears. The selection also clears on reload and on candidate switch.
3. **Analysis toggle (default on).** A page-level Analysis toggle in the list header, **on** at page load (not persisted). When on, each job row expands with four stacked lines — JD, DO, GET, LIKE, in the modal's phase order — each showing that phase's coloured grade circles for the job. The circles show **no letters and no confidence ratings**. Their colours, the vectors present, and their left-to-right order match the modal Analysis tab for that job; hover text is kept. A phase with no grades shows an em dash. Clicking the expanded area opens the report, same as clicking the row. When off, the table looks like it does today (plus the new checkbox and Total columns).
4. **Total score column.** A sortable **Total** column placed after the four phase score columns, showing JD + DO + GET + LIKE scores to one decimal. If any of the four scores is missing, Total shows an em dash. Total sorts with the same rules as the phase score columns.

## Component scope

* `src/ui/frontend/src/pages/JobsRecommended.tsx` — **modified** — selection checkboxes, header bulk bar, row Generate wiring, Analysis toggle and per-job expanded lines, Total column and sort.
* `src/ui/frontend/src/components/CandidateJobRowActions.tsx` — **modified** — optional Generate Artifacts icon control.
* `src/ui/frontend/src/lib/candidateJobActions.ts` — **modified** — client call that starts a job's artifact build.
* `src/ui/frontend/src/hooks/useCandidateJobActions.ts` — **modified** — generate flow and multi-job skip / applied flows.
* `src/ui/frontend/src/lib/recommendedJobReport.tsx` — **modified** — letterless, confidence-free phase grade row for list use.
* `src/ui/frontend/src/App.css` — **modified** — letterless dot variant and the list's expanded analysis lines.

No backend, API route, or `src/utils/config.py` change: bulk actions fan out over the existing per-job endpoints (`/skip`, `/candidate_action`, `/generate_artifacts`), which already enforce prior-state legality. The list response already carries `{jd,do,get,like}_grades`, `_rubric`, and `_score` per job.

## Technical scope

* `JobsRecommended.tsx` — add page-level selection state keyed by `astral_job_id`, plus a checkbox column. Add a header bulk bar that calls the hook's multi-job flows; Generate eligibility comes from `manifest.jobs.recommended.primary_actions_by_state`, not a hardcoded state list. Pass a row Generate handler only to eligible rows. Add page-level Analysis toggle state (default true). When it's on, render one expanded row per job, spanning the table, with the four phase lines built from `manifest.jobs.recommended.report_phase_tabs` (phase order + `grades_field`) via the new builder in `recommendedJobReport.tsx`. Add a Total column whose value is the sum of the manifest `phase_score_columns` fields (null if any is missing). Extend the existing `sortRecommendedJobs` to sort it with the same null handling as the phase fields — not a second sorter.
* `CandidateJobRowActions.tsx` — new optional generate callback prop. When provided, render one more `icon-control` button (title / aria-label "Generate Artifacts"). Existing behaviour is unchanged for callers that don't pass it (Skipped, Applied, In Review pages).
* `candidateJobActions.ts` — new exported function that POSTs `/api/jobs/<id>/generate_artifacts` and throws with the server error text on non-OK, same shape as the existing skip helper.
* `useCandidateJobActions.ts` — new generate flow for one or many job ids. Multi-job skip. Pending notes state that can carry a list of job ids, so one `CandidateActionNotesModal` confirm applies the action to each. Calls go per job, and success/failure counts are reported back to the page for the toast. Existing single-job call sites keep working unchanged.
* `recommendedJobReport.tsx` — new exported builder: given a job and a `grades_field`, return the row of coloured grade circles with **no letter text and no** `ConfidenceBullets`. It reuses the same column source (`buildJobListRubricColumnsForGroup`), order (`sortRubricColumnsByImportanceAndGrade`), grade lookup, and tooltip formatting as `buildPhaseSectionGradeConfidenceRow`, so list and modal can't drift. Factor out a shared internal helper rather than copying the logic.
* `App.css` — a letterless grade-dot size modifier (reusing `.dot-a`…`.dot-x` colours) and layout for the four stacked lines in the expanded list row.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies`. Of the 21 in-force directives (`canon_clerk.py index`), the only frontend pattern is `patt.artifact.ui-consistency`, which governs artifact **editors** by `body_shape`. This epic only triggers the existing build start endpoint and edits no artifact body.
* **New patterns proposed** — none.
* **Applicable statutes** — none apply. The epic is frontend-only: no `src/ui/api/**` route is added or changed (so `stat.logging.info.api` is out of territory), no logging is added, and nothing writes an entity outside the existing per-job endpoints. The draft UI rules (`pattern.ui.icon-control`, `stat.ui.*`) are not in force and are not cited as law. The Generate control still uses the existing `icon-control` class to match its siblings.

**Canon Scope:** empty — locked at Discussion.

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

## Open questions

none

## Proposed child tickets

#### 1: **Recommended list triage upgrades - Ada**

Delivers all four capabilities: row Generate Artifacts, multi-select bulk Skip / Applied / Generate Artifacts, the default-on Analysis toggle with letterless four-phase grade lines, and the sortable Total column. Does not touch the Job Analysis Report modal's behaviour or any backend route.
**Citations:** none — no in-force directive governs frontend list pages; see Architectural definition.
**Scope:** `src/ui/frontend/src/pages/JobsRecommended.tsx` (selection + bulk bar, row Generate wiring, Analysis toggle + expanded lines from `report_phase_tabs`, Total column via `sortRecommendedJobs`); `src/ui/frontend/src/components/CandidateJobRowActions.tsx` (optional Generate `icon-control`); `src/ui/frontend/src/lib/candidateJobActions.ts` (generate-artifacts POST helper); `src/ui/frontend/src/hooks/useCandidateJobActions.ts` (generate + multi-job skip/applied, one notes confirm over many ids); `src/ui/frontend/src/lib/recommendedJobReport.tsx` (letterless, confidence-free phase row sharing the modal's column/order/lookup helper); `src/ui/frontend/src/App.css` (letterless dot modifier + expanded-line layout).
Estimate: 5

**New patterns:** none.

**Monolith check:** Functional scope has 4 items and 1 child, on purpose. All four capabilities land in `JobsRecommended.tsx`, and the scope partition rule lets only one child claim that file. A split would also serialize every child on the same component.

**Scope partition check:** all six Component scope files and every Technical scope item belong to child 1, with no gaps or overlaps.

---

## Original brief

1. Add generate artifacts to the list level actions
2. Bulk actions, select multiple jobs and click the skip or apply or generate artifacts
3. Add a toggle for analysis to Expand the rows per job to show four rows of colored circles (without confidence ratings or letters) to emulate the analysis tab from the modal, so tha candidate can see at a glance from the list that some jobs are more green than others default the toggle to on.  When the toggle is off, the table should display much like it does today.
4. Add a total score column to sort by that adds together the four scores.

### Comments

#### ada — 2026-10-04T12:34:21.973Z
🛑 Stage 5 blocked (lint only): plan step adds one new lint error
Step: Stage 5 step 4 — `useEffect(() => { setSelected(new Set()) }, [selectedId])` (clear selection on candidate switch)
Issue: `react-hooks/set-state-in-effect` flags it → lint 32 → 33 problems. Built and pushed as written (`origin/sub/AST-1967/AST-1968-recommended-list-triage-upgrades` @ `055a551e7`); all six stages done, build + tsc clean, every other stage adds zero lint.
Proposed resolutions:
1. **(recommended)** Drop the effect; clear in `load` when `showSpinner` is true (`if (showSpinner) setSelected(new Set())`). `load(true)` runs only on mount and candidate switch — same behaviour, zero new lint. One line in `JobsRecommended.tsx`.
2. Keep the effect as-is and accept the +1 (fits with resolution 1 on the AC 16 comment above).
3. Hold selection as `{ owner: candidateId, ids }` and derive empty when owner ≠ `selectedId` — no effect, ~4 lines.
Holding Code Complete until @susan picks (together with the AC 16 lint question above).

#### ada — 2026-10-04T12:30:41.606Z
🛑 Stage 1 blocked (AC 16 gate only): `npm run lint` already fails on `origin/dev`
Step: every stage's "Done when … `npm run lint` exit 0" / AC 16
Issue: Baseline `origin/dev` @ `79c4f9b44` fails `npm run lint` with 32 problems (27 errors, 5 warnings) in ~25 files outside AST-1968 Scope (e.g. `NavigationShell.tsx`, `Toast.tsx`, `JobsSkipped.tsx`, `AdminVectorFeedback.tsx`). One is in scope: `JobsRecommended.tsx:78` (`react-hooks/set-state-in-effect`, the existing `actions.error` → toast effect). AST-1968 changes add **zero** new lint problems (before/after file lists identical). `npm run build` exits 0.
Proposed resolutions:
1. Read AC 16 as "no new lint problems vs `origin/dev`" (current state) — no extra code.
2. Same as 1, plus fix the one in-scope hit at `JobsRecommended.tsx:78`.
3. Widen scope to clear all 27 baseline errors (separate ticket recommended).
Build continues against option 1's gate; holding Code Complete until @susan picks.

#### chuckles — 2026-10-04T06:09:30.349Z
@susan dispatch blocked. What's missing:

- **Linear project.** AST-1967 has no project, and children can't be created without one. Earlier Recommended-list work lives under **Astral Tracker** (AST-1477, AST-1479); some UI-only siblings have gone to **Astral Interface**. Set the project, then move back to Todo and assign Chuckles.

---

_Implementation detail may live in git history on `origin/dev`._
