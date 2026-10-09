# AST-1862 — Recommended Job Modal Changes

<!-- linear-archive: AST-1862 archived 2026-10-08 -->

## Linear archive (AST-1862)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1862/recommended-job-modal-changes  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Recommended Job Report modal is where Susan decides whether a job is worth pursuing, and today it makes her work for it. The report opens on Summary when the decision lives in Analysis. The phase headers show the score breakdown but not the one number she sorted the list by. The only way to skip a job is to close the modal and hit **S** on the list row. Two of the button labels ("Copy Link", "Copy") don't say what they copy. And the header wastes vertical space: the buttons sit on their own row, and the title bar is big and spaced out. This ticket tightens the modal so the triage decision (read the analysis, see the score, skip or keep) happens in one place without scrolling.

## Functional scope

1. **Analysis first.** The report's top tabs read **Analysis**, **Summary**, **Artifacts**, **Discussion**, **Meteorite** (Meteorite still only when present). Opening the modal, or opening a different job in it, lands on **Analysis**. The default is whatever tab config lists first, not a tab name hard-coded in React.
2. **List score in Analysis headers.** Each Analysis phase header (JD / DO / GET / LIKE) that already shows the score details also shows that phase's score from the Recommended list (the same number, same one-decimal format as the list's JD / DO / GET / LIKE columns), between the phase title and the score details. Example: `JD Analysis - 3.7 - score: 42 out of 50 possible (60 max total)`. A phase with no list score keeps today's header. A phase with no score details keeps today's plain title.
3. **Skip this Job.** The modal header gets a **Skip this Job** button, last in the button row (right of Copy Job Link / Copy Job JSON / Copy Application Email / Copy LinkedIn Profile). It is shown only when the job is in a state that can legally move to skipped, and the server decides that. Clicking it skips the job through the existing skip endpoint, refreshes the list behind the modal, and closes the modal. On the `/jobs/detail/<id>` deeplink, closing already returns to Recommended. A failed skip shows the error toast and leaves the modal open.
4. **Clearer copy labels.** In this modal only, **Copy Link** becomes **Copy Job Link** and **Copy** becomes **Copy Job JSON**. Both still read **Copied** for about 2 seconds after a click. The Job Detail modal's own **Copy** button is not renamed.
5. **Buttons beside the title.** The copy/skip button row moves onto the same row as the job title, with the title on the left and the buttons on the right. The title word-wraps so a long title never pushes under or clips the buttons. The Print Resume / Print Cover Letter row stays where it is.
6. **Job link shown, title not linked.** The job title is plain text, not a hyperlink. Directly below it, the full job link appears in small text. When the resolved listing URL is http(s) (AST-1694 `listing_href`: `job_link` when http(s), else the related meteorite link), that URL is shown and hyperlinked (new tab). Otherwise the raw `job_link` is shown as plain text. With no link at all, the line is omitted.
7. **Tighter title bar.** On this modal only, the modal title bar (the company name at the top, i.e. the "screen title") uses a smaller font, and the vertical gap between it and the job title shrinks. Every other modal keeps today's title size and spacing.

## Component scope

* `src/utils/config.py`: **modified**. The report top-tab order, and the phase header title template gains a place for the list score.
* `src/core/tracker.py`: **modified**. Core answers "can this job legally move to state X" so the API does not re-implement the prior-state rule.
* `src/ui/api/api_jobs.py`: **modified**. Job detail response tells the UI whether Skip is legal for this job.
* `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`: **modified**. Title/button row layout, plain title plus job-link line, renamed labels, and the Skip button.
* `src/ui/frontend/src/App.css`: **modified**. Title-row layout with wrapping title, job-link line style, and a report-modal-scoped smaller title bar with a tighter gap.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`: **modified**. Default tab from config, list score into Analysis headers, skip handler, and the new header props.
* `src/ui/frontend/src/lib/recommendedJobReport.tsx`: **modified**. Shared phase-score formatting, and the header title formatter takes the score.
* `src/ui/frontend/src/pages/JobsRecommended.tsx`: **modified**. List columns use the shared phase-score formatter instead of the page-local copy.

Tests and test-bible pages (`tests/component/frontend/components/test_RecommendedJobReportHeader.test.tsx`, `test_JobAnalysisReportModal.test.tsx`, `tests/component/frontend/lib/` for `recommendedJobReport`, `tests/component/frontend/pages/` for `JobsRecommended`, API/tracker/config component tests, `docs/test-bible/frontend/components.md`, `docs/test-bible/frontend/lib.md`) belong to Betty in each child's `qa-child`. Existing asserts on **Copy Link** / **Copy** labels, the title `<a>`, and the Summary default tab will need revising there. No file is deleted.

**Out of scope:** `Modal.tsx` (the shared modal component is not changed; title-bar sizing is CSS scoped to this report), `CandidateJobRowActions.tsx` (list-row Skip unchanged), `JobDetailModal.tsx`, `JobsJobDetail.tsx`, the skip endpoint itself, and any schema change.

## Technical scope

* `src/utils/config.py`: modified constant. The Recommended report top-tab list is reordered so `analysis` comes first and `summary` second, with the rest unchanged. Modified constant: the phase score header title template gains a score placeholder between the phase label and the breakdown, rendering as `{phase_label} - {score} - score: {earned} out of {possible} possible ({max} max total)`. Both already flow to React through the state-UI manifest.
* `src/core/tracker.py`: new public function. Given a current job state and a target state, it returns whether the target's configured prior states admit the current one, reusing the existing private prior-state matcher (so `BUILD_ARTIFACTS` hop sub-states behave exactly as `transition_job_state` treats them). No change to `transition_job_state`.
* `src/ui/api/api_jobs.py`: modified function (job detail route). It attaches a boolean field saying whether the job can move to `CANDIDATE_SKIPPED`, computed through the new tracker function. The field name is `plan-child`'s call. No new route, and the skip route is unchanged.
* `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`: modified component. The title always renders as plain text. A new small job-link line under the title takes the display text plus an optional http(s) href (hyperlinked in a new tab when the href is present). The button row renders on the title row, right-aligned. Labels change to **Copy Job Link** / **Copy Job JSON** (the **Copied** feedback is unchanged). New optional skip callback and busy props render **Skip this Job** as the last `.btn secondary` in the row, disabled while busy. The row stays visible when only Skip is present.
* `src/ui/frontend/src/App.css`: modified rules. The header title row becomes a two-column flex row: the title/company/link column shrinks and wraps, and the buttons column does not shrink. A new job-link-line rule uses small, secondary text. New rules scoped to the report modal only (no change to the shared `.modal-title` / `.modal-header` / `.modal-body` rules) reduce the title font below 18px and cut the combined vertical gap between the title bar and the job title (today 16px header bottom padding + 20px body top padding + 12px report header top padding).
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`: modified component. The initial and per-job reset active tab come from the first manifest top tab instead of the literal `"summary"`. The Analysis section header labels pass the phase's list score (the `<prefix>_score` field matching each phase's `grades_field`, already flattened onto the detail GET) into the title formatter. There is a new skip handler: it calls the existing `postSkipJob`, then `onRefresh?.()` and `onClose()` on success, and shows the error toast on failure. It is wired to the header only when the detail response's skip-legal flag is true. The header gets the job-link display text (`listing_href` when http(s), else raw `job_link`) plus the http href.
* `src/ui/frontend/src/lib/recommendedJobReport.tsx`: new exported function, the list's phase-score formatter (number to one decimal, else em dash), moved here from `JobsRecommended.tsx`, not copied. Modified function: the phase header title formatter takes an optional score and fills the new placeholder. Its no-template fallback string gets the same score segment. When the score is absent, the ` - {score}` segment is dropped, not rendered as an em dash.
* `src/ui/frontend/src/pages/JobsRecommended.tsx`: modified. The page-local phase-score formatter is removed and the shared one imported. Column output is unchanged.

## Architectural definition

* **Patterns to reuse:** no established pattern applies. The in-force pattern roster (`canon_clerk.py index`) covers artifacts, entity batching and task chains, not UI layout or modal actions.
* **New patterns proposed:** none.
* **Applicable statutes:**
  * `astral.layers.ui-config-driven-business-logic`: Skip visibility is resolved server-side from the configured state rules and served on the detail response. React must not hard-code which states can skip (the list row's existing local set is not copied into the modal). [current file](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>)
  * `astral.config.config-source-of-truth`: tab order and the header title template live in `config.py`. React takes the default tab from the manifest, not from a literal. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
  * `astral.state.core-decides-transitions`: the "can this job skip" answer comes from core's prior-state rule, not a re-implementation in the API layer. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.core-decides-transitions.md>)
  * `astral.standards.dry-and-focused-functions`: one phase-score formatter shared by the list and the modal headers. A second copy is a defect. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)
  * `astral.idioms.require-auth-on-protected-endpoints`: the detail route stays `@require_auth`, and no new unauthenticated surface is added. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/idioms/astral.idioms.require-auth-on-protected-endpoints.md>)

## Acceptance criteria

 1. **Analysis is first and default.** `JOBS_RECOMMENDED_REPORT_TOP_TABS` in `src/utils/config.py` lists `analysis` at index 0 and `summary` at index 1. In `test_JobAnalysisReportModal.test.tsx`, opening the modal with the manifest renders the Analysis pane (phase sections visible) and the tab bar order is Analysis, Summary, Artifacts, Discussion. Switching to a different `jobId` after selecting Summary returns to Analysis. Fail = Summary pane shown on open, or wrong order.
 2. **No hard-coded default tab.** `grep -n 'useState("summary")\|setActiveTopTab("summary")' src/ui/frontend/src/components/JobAnalysisReportModal.tsx` returns nothing. Fail = either literal still present (a reorder in React instead of config).
 3. **Score in Analysis header.** With a job whose `jd_score` is `3.66` and `jd_score_breakdown` is `{earned: 42, possible: 50, max: 60}`, the JD Analysis section header reads exactly `JD Analysis - 3.7 - score: 42 out of 50 possible (60 max total)`. With `jd_score` absent, it reads `JD Analysis - score: 42 out of 50 possible (60 max total)`. Fail = score missing, misplaced, or not one decimal, or an empty `-` segment / em dash rendered when the score is absent.
 4. **One score formatter.** `grep -rn "toFixed(1)" src/ui/frontend/src/pages/JobsRecommended.tsx` returns nothing, and the Recommended list JD/DO/GET/LIKE cells still render `3.7` / `—` exactly as before (existing page tests pass without behavioral edits). Fail = the formatter exists in both files, or list output changed.
 5. **Skip legality is server-resolved.** `GET /api/jobs/<id>` for a job in `RECOMMENDED`, `CANDIDATE_REVIEW`, or a `BUILD_ARTIFACTS` hop sub-state returns the skip-legal flag `true`. For `CANDIDATE_SKIPPED` or `CANDIDATE_APPLIED` it returns `false`. Fail = any of those inverted, or the flag missing.
 6. **Skip button visibility.** In `test_RecommendedJobReportHeader.test.tsx` / `test_JobAnalysisReportModal.test.tsx`, **Skip this Job** is the last button in the header button row when the detail flag is `true`, and absent when `false`. `grep -n "CANDIDATE_REVIEW\|REVIEW_LIKE" src/ui/frontend/src/components/JobAnalysisReportModal.tsx src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` returns nothing. Fail = the button is shown for a non-skippable job, is not last, or the modal carries its own state list.
 7. **Skip acts and closes.** Clicking **Skip this Job** sends `POST /api/jobs/<id>/skip`. On `200`, `onRefresh` is called once and `onClose` is called once. On `409`, the error toast shows the server message and `onClose` is not called. Fail = no POST, modal stays open on success, or closes on failure.
 8. **Renamed labels.** In the report header, buttons read **Copy Job Link** and **Copy Job JSON** when idle and **Copied** after click. `grep -n '"Copy Link"\|>Copy<\|"Copy"' src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` returns nothing. Job Detail modal's **Copy** test still passes unedited. Fail = old label present, or the Job Detail label changed.
 9. **Buttons share the title row.** In `RecommendedJobReportHeader`, the button row element is a descendant of the same row container as the job title (not a sibling row below it), and App.css gives the title column `min-width: 0` plus wrapping (`overflow-wrap`/`word-break`) while the button column has `flex-shrink: 0`. Fail = buttons render in a separate row, or the title has `white-space: nowrap`/no wrap rule.
10. **Title not linked, link shown below.** With `listing_href: "https://x.test/j"`, the title renders with no `<a>` ancestor, and a small link line below it shows `https://x.test/j` as an `<a href="https://x.test/j" target="_blank">`. With `listing_href: null` and `job_link: "meteorite-123"`, the line shows `meteorite-123` as plain text (no `<a>`). With neither, no link line renders. Fail = title is a link, URL not shown, or non-http text hyperlinked.
11. **Title bar scoped.** `git diff origin/dev -- src/ui/frontend/src/App.css` shows no change to the existing `.modal-title`, `.modal-header`, or `.modal-body` rule blocks, and a new report-scoped rule sets the title font-size below `18px`. In UAT, the company-name title bar on the Recommended report is visibly smaller, with less space above the job title, while the Company and Job Detail modals look unchanged. Fail = shared modal rules edited, or other modals change.
12. **No new routes or schema.** `git diff origin/dev...<ftr> -- src/data/ src/ui/frontend/src/components/Modal.tsx` is empty, and `grep -n "@jobs_bp.route" src/ui/api/api_jobs.py | wc -l` is unchanged from `origin/dev`. Fail = any change there.

## Open questions

None.

## Proposed child tickets

#### 1!: **Config tab order, score template, and server-side skip flag - Katherine**

Backend and config only: the report top tabs are reordered so Analysis is first, the header title template gains the score placeholder, and the job detail response carries a flag saying whether Skip is legal, decided by core's prior-state rule. No UI changes. #3 consumes the flag and template.
**Citations:** `astral.config.config-source-of-truth`, `astral.state.core-decides-transitions`, `astral.layers.ui-config-driven-business-logic`, `astral.idioms.require-auth-on-protected-endpoints`.
**Scope:**

* `src/utils/config.py`: modified constant. The Recommended report top-tab list is reordered so `analysis` comes first and `summary` second, with the rest unchanged. Modified constant: the phase score header title template gains a score placeholder between the phase label and the breakdown, rendering as `{phase_label} - {score} - score: {earned} out of {possible} possible ({max} max total)`. Both already flow to React through the state-UI manifest.
* `src/core/tracker.py`: new public function. Given a current job state and a target state, it returns whether the target's configured prior states admit the current one, reusing the existing private prior-state matcher (so `BUILD_ARTIFACTS` hop sub-states behave exactly as `transition_job_state` treats them). No change to `transition_job_state`.
* `src/ui/api/api_jobs.py`: modified function (job detail route). It attaches a boolean field saying whether the job can move to `CANDIDATE_SKIPPED`, computed through the new tracker function. The field name is `plan-child`'s call. No new route, and the skip route is unchanged.

Estimate: 2

#### 2!: **Report header layout, labels, job-link line, Skip button - Hedy**

The header component and its CSS: buttons move onto the title row with a wrapping title, the title is un-linked with the full job link shown in small text below, the copy labels are renamed, the **Skip this Job** button renders when a skip callback is passed, and the modal title bar gets smaller and tighter (report-scoped CSS only). This child does not wire data or the skip action into the modal; that is #3.
**Citations:** `astral.standards.dry-and-focused-functions`.
**Scope:**

* `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`: modified component. The title always renders as plain text. A new small job-link line under the title takes the display text plus an optional http(s) href (hyperlinked in a new tab when the href is present). The button row renders on the title row, right-aligned. Labels change to **Copy Job Link** / **Copy Job JSON** (the **Copied** feedback is unchanged). New optional skip callback and busy props render **Skip this Job** as the last `.btn secondary` in the row, disabled while busy. The row stays visible when only Skip is present.
* `src/ui/frontend/src/App.css`: modified rules. The header title row becomes a two-column flex row: the title/company/link column shrinks and wraps, and the buttons column does not shrink. A new job-link-line rule uses small, secondary text. New rules scoped to the report modal only (no change to the shared `.modal-title` / `.modal-header` / `.modal-body` rules) reduce the title font below 18px and cut the combined vertical gap between the title bar and the job title (today 16px header bottom padding + 20px body top padding + 12px report header top padding).

Estimate: 3

#### 3: **Modal wiring: Analysis default, list score in headers, Skip action - Ada**

Wires everything into the report modal. The default tab comes from config (Analysis). Analysis headers show the list score through one shared formatter that the Recommended list also uses. The skip handler posts, refreshes, and closes, and is shown only when #1's flag is true. The header gets the job-link text and href that #2's props expect. Comes after #1 (flag and template) and #2 (header props).
**Citations:** `astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.dry-and-focused-functions`.
**Scope:**

* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`: modified component. The initial and per-job reset active tab come from the first manifest top tab instead of the literal `"summary"`. The Analysis section header labels pass the phase's list score (the `<prefix>_score` field matching each phase's `grades_field`, already flattened onto the detail GET) into the title formatter. There is a new skip handler: it calls the existing `postSkipJob`, then `onRefresh?.()` and `onClose()` on success, and shows the error toast on failure. It is wired to the header only when the detail response's skip-legal flag is true. The header gets the job-link display text (`listing_href` when http(s), else raw `job_link`) plus the http href.
* `src/ui/frontend/src/lib/recommendedJobReport.tsx`: new exported function, the list's phase-score formatter (number to one decimal, else em dash), moved here from `JobsRecommended.tsx`, not copied. Modified function: the phase header title formatter takes an optional score and fills the new placeholder. Its no-template fallback string gets the same score segment. When the score is absent, the ` - {score}` segment is dropped, not rendered as an em dash.
* `src/ui/frontend/src/pages/JobsRecommended.tsx`: modified. The page-local phase-score formatter is removed and the shared one imported. Column output is unchanged.

Estimate: 3

**New patterns:** none.

**Monolith check:** Functional scope has 7 items and there are 3 children. Split: backend/config (#1), header presentation (#2), and modal behavior wiring (#3).

**Scope partition check:** `config.py`, `tracker.py`, `api_jobs.py` → #1. `RecommendedJobReportHeader.tsx`, `App.css` → #2. `JobAnalysisReportModal.tsx`, `lib/recommendedJobReport.tsx`, `JobsRecommended.tsx` → #3. All 8 Component scope files are claimed exactly once.

---

## Original brief

Move the Summary tab to second position, move Analysis to first position (default view).

Show score from recommended job list in the analysis headers between the title and the score details.

Add a "Skip this Job" button to the modal on the right of the other three buttons.

Rename "Copy Link" to "Copy Job Link"

Rename "Copy" to "Copy Job JSON"

Move the series of buttons to the same tr as the title, and word-wrap the title td so that the buttons don't interfere with the full display.

Display the full job_link in small text below the title, instead of hyperlinking the title, and hyperlink the job link if it has a http address.

Make the Recommended Job Report header smaller font size, and decrease the space between the screen title and the job title.

### Comments

#### chuckles — 2026-10-01T01:09:52.150Z
[check-linear] answered — canceled AST-1903 (bug) and AST-1915 (its gate task). Run cancel-linear AST-1903 to clean up its git refs.

#### susan — 2026-10-01T01:09:11.417Z
@chuckles I can't reproduce this issue anymore.  Please cancel the related bug and task tickets.

#### chuckles — 2026-09-30T23:17:24.133Z
[fix-intake] Filed AST-1903 (job-link line missing for non-http job_link) at Discussion for you to confirm the diagnosis. Reassign it to Chuckles to release it into the fix lane.

#### susan — 2026-09-30T23:15:22.367Z
\[bug\] job link line is not appearing in the header (at least for email meteorites without an http link), and I want the information in job_link whether or not it is http.

#### chuckles — 2026-09-29T18:50:43.755Z
@susan merge-child for AST-1873 needs one decision. Wave 3 (AST-1874) is waiting on it.

- I refreshed `ftr/AST-1862-recommended-job-modal-changes` from dev, which cleared the inherited dev merge commit `075c3d78` from the validator's range.
- One check still fails: `validate-sub-log` reports `plan(AST-1873)` missing. The plan commit `d818add5` is already an ancestor of the ftr. It rode in on AST-1872's branch when the two wave-1 drones shared the epic worktree, so the sub-vs-ftr range can't see it.
- Everything else is on `origin/sub/…/AST-1873` against the ftr: code ×3, test, merge-tests, Joan, Radia, and resolve.

Please pick one:
1. Authorize a one-time merge of `origin/sub/AST-1862/AST-1873-…` into the ftr without the validator.
2. File a Team Chuckles fix so `validate-sub-log` accepts a `plan()`/`docs(): plan` commit that's already reachable from the ftr, then I re-run merge-child.

#### chuckles — 2026-09-29T18:49:55.038Z
AST-1873 merge-child blocked: validate-sub-log flags an inherited origin/dev merge commit (075c3d78) and would then miss plan() already on ftr. Needs a tooling or override decision; no engineer recall.

#### chuckles — 2026-09-29T18:23:27.147Z
AST-1873 blocked — @susan the AST-1872 and AST-1873 drones share one epic worktree, so parallel engineers collide: Katherine's AST-1872 plan commit (be770690) landed on local sub/…/AST-1873 and was pushed to origin/sub/…/AST-1872, which now also carries AST-1873's plan commit (d818add5). origin/sub/…/AST-1873 is clean (1e042804, Plan Approved). I stopped before build-child so the two builds don't run in the same working tree; AST-1873 should run after the AST-1872 drone finishes. Its local branch needs a reset to origin before Hedy builds.

---

_Implementation detail may live in git history on `origin/dev`._
