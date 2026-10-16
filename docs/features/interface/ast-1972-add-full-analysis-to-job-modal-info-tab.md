# AST-1972 — Add full analysis to job modal Info tab

<!-- linear-archive: AST-1972 archived 2026-10-08 -->

## Linear archive (AST-1972)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1972/add-full-analysis-to-job-modal-info-tab  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

When a candidate opens a Skipped or In Review (Processing, after AST-1970) job, the Job Detail modal shows metadata and state history but none of the analysis grades. To see why a job was dropped, or how far it has got, she has to piece it together elsewhere. The Recommended/Review list already draws each job's analysis as colored grade dots on JD / DO / GET / LIKE lines (AST-1967 / AST-1968). This epic puts that same component in the Job Detail modal's Info tab, above State History, so every skipped or in-process job shows whatever analysis has been completed so far.

## Functional scope

1. **Analysis in the Info tab.** The Job Detail modal's Info tab shows an **Analysis** block in its right-hand column, directly above **State History**. Each phase gets one line, in the same order and with the same short labels as the Recommended/Review list (JD, DO, GET, LIKE).
2. **Same dots as the list.** Each line's grade circles (vectors shown, colors, left-to-right order, hover text) match that job's line on the Recommended/Review list exactly: no letters, no confidence bullets. In the modal the block is display-only, with no click action.
3. **Partial analysis.** A phase the job has not reached, or has no grades for, shows an em dash on its line, exactly as the list does. The block shows for every job the modal opens (all Skipped and In Review/Processing jobs, including virtual skips), whatever its state.
4. **One component, two hosts.** The Recommended/Review list and the Job Detail modal render this block from the same shared component, so they cannot drift apart.

## Component scope

* `src/ui/frontend/src/components/PhaseAnalysisLines.tsx` — **new** — shared phase-lines component (manifest-driven line order + labels, one letterless grade row per phase, em dash when empty).
* `src/ui/frontend/src/pages/JobsRecommended.tsx` — **modified** — expanded analysis row renders the shared component instead of its inline phase-lines block.
* `src/ui/frontend/src/components/JobDetailModal.tsx` — **modified** — Info tab right column renders the shared component above State History.

No backend, API, `src/utils/config.py`, or `App.css` change. `GET /api/jobs/<id>` already runs `_flatten_grades`, so the detail payload carries `{jd,do,get,like}_grades` and `_rubric` the way list rows do. The existing `recommended-analysis-*` classes and `entity-section-label` cover the styling.

## Technical scope

* `PhaseAnalysisLines.tsx`: a new component that takes one job record. It derives its phase lines from `manifest.jobs.recommended.report_phase_tabs`, using that order and each tab's `grades_field`. Each line's short label comes from the matching `phase_score_columns` entry, falling back to the tab's `nav_label`. This derivation moves here from `JobsRecommended.tsx` unchanged. For each line, the component renders the label plus `buildPhaseListGradeRow(job, gradesField)`, or an em dash when that returns nothing. It reads the manifest through `useStateUi`.
* `JobsRecommended.tsx`: a modified page render. The `phaseLines` memo and the inline `recommended-analysis-lines` markup inside the analysis row are replaced by the shared component. The surrounding row, `colSpan`, click-to-open-report, and Analysis toggle stay as they are.
* `JobDetailModal.tsx`: a modified `InfoTab`. The right-hand column gets an **Analysis** section label (the same `entity-section-label` style as State History) with the shared component under it, placed before the State History label. `JobDetail` gains an index signature or cast so the job record can be passed. The block is not gated on state.

## Architectural definition

* **Patterns to reuse:** no established pattern applies. No active pattern governs frontend display components. `patt.artifact.ui-consistency` is a draft about artifact editors, so it is not cited.
* **New patterns proposed:** none.
* **Applicable statutes:**
  * [`astral.ui.frontend-file-placement`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.frontend-file-placement.md>): the new shared component goes flat in `components/`.
  * [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>): phase set, order, and labels come from the served manifest (`report_phase_tabs` / `phase_score_columns`). React must not hardcode a phase list or add its own state rule for when the block shows.
  * [`astral.standards.dry-and-focused-functions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>): the list and the modal share one component. Copying the phase-lines markup or the `phaseLines` derivation into the modal is the wrong shape.
  * [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>): `JobsRecommended.tsx` changes only at the analysis-row block. AST-1970 is also queued to modify this page, so any wider edit invites a merge collision.

## Acceptance criteria

1. **Block present and placed.** Open any job from Skipped or In Review. On the Info tab, the right column shows an **Analysis** label, then the phase lines, then the **State History** label, in that DOM order. **Fail:** block missing, or rendered below State History or in the left column.
2. **Lines follow the manifest.** The block has exactly one line per `report_phase_tabs` entry, in manifest order, labeled JD, DO, GET, LIKE. **Fail:** a missing, extra, or out-of-order line.
3. **Partial analysis shows em dashes.** For a job with `jd_grades` and `do_grades` but no `get_grades` or `like_grades`, the JD and DO lines show circles and the GET and LIKE lines show `—`. For a job with no phase grades, all four lines show `—` and the modal still renders. **Fail:** a crash, a hidden block, or circles on an ungraded phase.
4. **Dots match the list.** For a job present on both Recommended/Review (Analysis toggle on) and in the Job Detail modal, each phase line has the same circle count, `dot-*` color classes, left-to-right order, and `title` text in both places. **Fail:** any mismatch.
5. **No letters, no confidence.** Every grade circle inside the modal's Analysis block has empty text content, and the block contains zero `ConfidenceBullets` elements. **Fail:** a visible letter or a confidence bullet.
6. **One shared component.** `rg -n "PhaseAnalysisLines" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/components/JobDetailModal.tsx` returns a hit in each file. `rg -n "report_phase_tabs|buildPhaseListGradeRow" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/components/JobDetailModal.tsx` returns nothing. **Fail:** either host still derives phase lines or calls the row builder itself (a copy instead of the shared component).
7. **Recommended list unchanged.** On Recommended/Review with the Analysis toggle on, each job still has one expanded row with four lines in JD, DO, GET, LIKE order, and clicking it still opens the Job Analysis Report. Toggling off still removes every expanded row. **Fail:** any change in line count, order, circles, toggle, or click behavior compared with `origin/dev`.
8. **No backend change.** `git diff origin/dev...<publish-ref> --stat -- src/ui/api src/core src/data src/utils` is empty. **Fail:** any file listed.
9. **Builds clean; no new lint.** In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem that `origin/dev` does not already report. **Fail:** a non-zero build or any new lint problem.

## Open questions

none

## Proposed child tickets

#### 1: **Job modal Info-tab analysis via shared phase-lines component - Ada**

Extracts the Recommended/Review list's phase-lines block into one shared component and renders it in the Job Detail modal's Info tab above State History, with em dashes for phases not yet graded. Ships Functional scope 1–4. It does not touch the Job Analysis Report modal, the list's toggle or click behavior, or any backend route. If AST-1970 lands first, merge its `JobsRecommended.tsx` changes before editing the analysis row.
**Citations:** `astral.ui.frontend-file-placement`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.dry-and-focused-functions`, `astral.standards.in-scope-only`.
**Scope:**

* `src/ui/frontend/src/components/PhaseAnalysisLines.tsx` (**new**): a new component that takes one job record. It derives its phase lines from `manifest.jobs.recommended.report_phase_tabs`, using that order and each tab's `grades_field`. Each line's short label comes from the matching `phase_score_columns` entry, falling back to the tab's `nav_label`. This derivation moves here from `JobsRecommended.tsx` unchanged. For each line, the component renders the label plus `buildPhaseListGradeRow(job, gradesField)`, or an em dash when that returns nothing. It reads the manifest through `useStateUi`.
* `src/ui/frontend/src/pages/JobsRecommended.tsx` (**modified**): a modified page render. The `phaseLines` memo and the inline `recommended-analysis-lines` markup inside the analysis row are replaced by the shared component. The surrounding row, `colSpan`, click-to-open-report, and Analysis toggle stay as they are.
* `src/ui/frontend/src/components/JobDetailModal.tsx` (**modified**): a modified `InfoTab`. The right-hand column gets an **Analysis** section label (the same `entity-section-label` style as State History) with the shared component under it, placed before the State History label. `JobDetail` gains an index signature or cast so the job record can be passed. The block is not gated on state.

Estimate: 2

**Monolith check:** Functional scope has 4 items and there is 1 child, on purpose. The shared component, the list swap, and the modal mount are one small vertical slice of three files. Splitting the extraction from the modal mount would leave a component with one caller, or a copy in the modal, which `astral.standards.dry-and-focused-functions` forbids.

**Scope partition check:** child 1 claims all three Component scope files and all three Technical scope items. There are no gaps and no overlaps.

---

## Original brief

Where a job has been skipped or in process, allow the user to open the job modal and view the analysis dots as much as has been completed thus far above the history panel on the right.  Reuse the Analysis component used on the recommended/review page.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
