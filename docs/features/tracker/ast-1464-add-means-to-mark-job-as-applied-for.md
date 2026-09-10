# AST-1464 — Add means to mark job as applied for

<!-- linear-archive: AST-1464 archived 2026-09-09 -->

## Linear archive (AST-1464)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1464/add-means-to-mark-job-as-applied-for  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** chuckles  
**Priority / estimate:** None / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators need a deliberate way to record that a candidate has applied for a job. Backend already supports `CANDIDATE_APPLIED` via `POST /api/jobs/<id>/candidate_action` (`action=applied`), and post-applied row actions (reapply / interview / rejected / ghosted) already exist — but there is no control that *enters* Applied from Recommended, the Job Analysis Report has neither Applied nor Skip, and the Applied nav/list is a disabled stub whose API view returns an empty list. Closing the review→applied loop needs mark-applied controls, Skip parity on the report, and an Applied list home for jobs that leave Recommended.

## Functional scope

* **Mark as applied (list).** From Recommended jobs that are in a legal prior for `CANDIDATE_APPLIED`, the operator can mark the job applied via a list-row icon-control; optional notes use the shared candidate-action notes modal; the job transitions to `CANDIDATE_APPLIED` and records `candidate_results.applied`.
* **Mark as applied (report).** The Job Analysis Report also offers a labeled Applied control that runs the same `candidate_action` / notes path (not the external job-link “Apply”).
* **Skip on report.** The Job Analysis Report offers a labeled Skip control consistent with the Recommended list Skip (→ `CANDIDATE_SKIPPED` via existing skip API).
* **External Apply unchanged.** Report-header / artifacts manifest `action_key: apply` still opens `job_link` in a new tab and does not change job state — distinct from terminal Applied.
* **Applied list home.** Jobs in post-applied states are visible on `/jobs/applied`: enable the existing disabled Jobs → Applied nav item, implement API `view=applied`, and replace the stub page with a real list that shows post-applied row actions (reapply / interview / rejected / ghosted) with the shared notes modal.
* **Out of scope.** Building the Responded list; changing `JOB_STATES` priors; new candidate_action API endpoints; AST-1463 single-page report deeplink (sibling may later reuse report actions).

## Component scope

* `src/ui/frontend/src/components/CandidateJobRowActions.tsx` — **modified** — expose Applied icon-control for legal pre-applied Recommended states alongside Skip / View Analysis.
* `src/ui/frontend/src/pages/JobsRecommended.tsx` — **modified** — wire list Applied through existing `useCandidateJobActions` / notes modal; pass Skip / Applied handlers into the report modal as needed.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — add labeled Applied and Skip controls on the report (shared notes + skip/candidate_action paths); keep external job-link Apply separate.
* `src/ui/api/api_jobs.py` — **modified** — implement `view=applied` list (today falls through to `[]`).
* `src/utils/config.py` — **modified** — define the applied-view state set used by the API; enable Jobs → Applied in `NAV_CONFIG`.
* `src/ui/frontend/src/pages/JobsApplied.tsx` — **modified** — replace stub empty `ListPage` with a real applied jobs list using shared candidate action plumbing.

## Technical scope

* `CandidateJobRowActions` — add Applied icon-control on the pre-applied / review-like branch for states that are legal priors of `CANDIDATE_APPLIED`; call `onAction("applied")`; keep Skip / View Analysis behavior.
* `JobsRecommended` — ensure list `onAction` covers `"applied"` via `requestAction`; refresh after confirm; plumb Skip / Applied into `JobAnalysisReportModal` (props or shared hook) so the modal does not invent a parallel POST.
* `JobAnalysisReportModal` — labeled `btn` Applied (notes → `candidate_action` applied) and labeled `btn` Skip (`postSkipJob` / existing skip route); after success refresh parent list and close or reload as appropriate; do not conflate with CLIENT `apply` (job_link).
* `api_jobs.list_view` — for `view=applied`, list jobs in the applied-view state set (post-applied states the row actions already target), scoped by `candidate_id`, ordered like sibling views.
* `config` — named applied-view state list (parallel to `RECOMMENDED_JOB_STATES` / `SKIPPED_STATES`); flip Applied nav `enabled`.
* `JobsApplied` — load `/api/jobs?view=applied&candidate_id=…`, render rows, mount `CandidateJobRowActions` + `CandidateActionNotesModal` + `useCandidateJobActions` (live refresh after transitions).

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.icon-control` — Applied (and existing post-applied glyphs) on list rows are icon-controls. [current](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.icon-control.md>)
  * `pattern.ui.shared-button-roles` — report Applied / Skip are full-size labeled `.btn` roles (not icon-controls); modal labeled Skip stays a labeled button. [current](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.shared-button-roles.md>)
  * `pattern.ui.in-place-live-refresh` — Applied list (and Recommended after transitions) refresh after candidate_action / skip. [current](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.in-place-live-refresh.md>)
* **New patterns proposed** — none.
* **Applicable statutes**
  * `astral.state.core-decides-transitions` — UI keeps using `candidate_action` / `transition_job_state` / skip route, not direct saves. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.core-decides-transitions.md>)
  * `astral.state.job-prior-states-enforced` — Applied only on legal priors; illegal hops stay 409. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.job-prior-states-enforced.md>)
  * `astral.standards.no-hardcoded-sets` — applied-view state membership lives in config. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
  * `astral.layers.ui-config-driven-business-logic` — nav enablement and view state lists from config. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>)
  * `astral.ui.frontend-file-placement` — page/component paths stay under established UI layout. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.frontend-file-placement.md>)
  * `astral.ui.naming-conventions` — icon/button labels and action keys stay domain-named. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.naming-conventions.md>)
  * `astral.idioms.require-auth-on-protected-endpoints` — applied list and action routes stay behind existing jobs auth. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/idioms/astral.idioms.require-auth-on-protected-endpoints.md>)
  * Universal orchestration set (`orch.pipeline.*`, `orch.git.*`, `orch.roles.*`) applies to delivery mechanics as usual.

## Acceptance criteria

1. On Recommended, a job in a legal prior for `CANDIDATE_APPLIED` shows an Applied list-row icon-control; confirming with optional notes transitions to `CANDIDATE_APPLIED` and writes `candidate_results.applied`.
2. On the Job Analysis Report for such a job, labeled Applied runs the same notes + `candidate_action` path and reaches `CANDIDATE_APPLIED`.
3. On the Job Analysis Report, labeled Skip transitions the job to `CANDIDATE_SKIPPED` (same outcome as list Skip).
4. After mark-applied, the job no longer appears on Recommended and does appear on `/jobs/applied` for that candidate.
5. Jobs → Applied is enabled in nav and routes to a non-stub list.
6. On `/jobs/applied`, post-applied icon actions Reapply / Interview / Rejected / Ghosted work via the shared notes + `candidate_action` path.
7. External job-link “Apply” (manifest `action_key: apply`) is unchanged and does not set `CANDIDATE_APPLIED`.
8. Illegal transitions still fail with a visible error (no silent no-op).

## Open questions

none

## Proposed child tickets

#### 1: **Mark applied from Recommended list - Katherine**

Add the Applied icon-control on Recommended list rows for legal `CANDIDATE_APPLIED` priors; wire through existing `useCandidateJobActions` / `CandidateActionNotesModal` / `candidate_action`. Does not own report Applied/Skip (child #2) or the Applied list page (child #3).
**Citations:** `pattern.ui.icon-control`; `astral.state.core-decides-transitions`; `astral.state.job-prior-states-enforced`; `astral.ui.naming-conventions`
**Scope:** `src/ui/frontend/src/components/CandidateJobRowActions.tsx` (modified — Applied icon on legal pre-applied states); `src/ui/frontend/src/pages/JobsRecommended.tsx` (modified — list Applied via shared requestAction/notes path and list refresh; may pass action handlers through to the report modal for child #2)
**Estimate: 2**

#### 2: **Report Applied and Skip - Hedy**

Add labeled Applied and Skip on `JobAnalysisReportModal`, reusing skip + candidate_action / notes plumbing (no parallel POSTs). Keep CLIENT job-link Apply separate. Does not own list-row Applied (child #1) or Applied list home (child #3).
**Citations:** `pattern.ui.shared-button-roles`; `astral.state.core-decides-transitions`; `astral.state.job-prior-states-enforced`; `astral.ui.naming-conventions`; `astral.standards.dry-and-focused-functions`
**Scope:** `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` (modified — labeled Applied + Skip); `src/ui/frontend/src/pages/JobsRecommended.tsx` (modified — only as needed to supply skip/applied callbacks or shared hook into the modal)
**Estimate: 3**

#### 3: **Applied jobs list home - Ada**

Config applied-view state set; implement API `view=applied`; enable Jobs → Applied nav; replace `JobsApplied` stub with a list that shows post-applied rows and existing R/I/X/G actions. Does not own mark-applied / report Skip (children #1–#2).
**Citations:** `pattern.ui.in-place-live-refresh`; `pattern.ui.icon-control`; `astral.standards.no-hardcoded-sets`; `astral.layers.ui-config-driven-business-logic`; `astral.idioms.require-auth-on-protected-endpoints`; `astral.ui.frontend-file-placement`
**Scope:** `src/utils/config.py` (modified — applied-view state list + NAV_CONFIG Applied enabled); `src/ui/api/api_jobs.py` (modified — `view=applied` list implementation); `src/ui/frontend/src/pages/JobsApplied.tsx` (modified — real applied list + shared candidate actions)
**Estimate: 3**

---

## Original brief

Creat an option to update a job state to APPLIED.

### Comments

#### chuckles — 2026-08-25T02:32:40.818Z
AST-1477 REVIEW — merge-child into ftr blocked on test-bible + JobsRecommended tests; recalling @Betty White to resolve (Katherine product already on sub).

#### chuckles — 2026-08-25T02:20:51.806Z
AST-1477 merge-child blocked on validate-sub-log false-positive (plan/code already on ftr via AST-1478 sync) — recalling Katherine for tip-marker commits.

#### chuckles — 2026-08-25T01:32:41.498Z
AST-1477 REVIEW — merge-child/§9a blocked; recalling Betty for bible + JobsRecommended tests vs AST-1478 on ftr; Katherine for feature-doc merge.

#### chuckles — 2026-08-25T01:18:57.580Z
[check-linear] answered — AST-1478 User Testing (Hedy finished refresh/resolve path).

#### chuckles — 2026-08-25T01:18:52.572Z
Hedy refreshed the stale publish ref — AST-1478 is User Testing. Continuing the wave on AST-1477 and AST-1479.

#### susan — 2026-08-25T00:42:36.811Z
@chuckles you have you call hedy to tell her to do that and wait for her to finish.

#### chuckles — 2026-08-25T00:41:33.123Z
AST-1478 STALE(dev+436) — pausing build until Hedy refreshes `origin/sub/AST-1464/AST-1478-report-applied-and-skip` (merge origin/dev + origin/ftr/AST-1464-add-means-to-mark-job-as-applied-for + republish). @Hedy Lamarr

#### chuckles — 2026-08-25T00:39:30.576Z
AST-1477 REVIEW — Radia needs resolve on test_JobsRecommended describe nesting (AST-1057 stranded outside suite).

#### chuckles — 2026-08-25T00:26:20.705Z
AST-1478 REVIEW — Radia fix-now: test_JobsRecommended describe nesting + restore AST-1477 block on merge.

#### chuckles — 2026-08-24T23:41:47.309Z
AST-1478 REVIEW — Joan validated PROCEED (docs commit 2eb8c676); LINEAR_KEY_JOAN unset on host so slim upshot could not post as Joan (same ops gap as AST-1473).

#### chuckles — 2026-08-24T22:09:18.038Z
@susan

1. This ticket has **no Linear project** — assign to **Astral Interface**?
2. Confirm the **Applied list home** (nav + API `view=applied` + real `JobsApplied` page with post-applied actions) is **in scope** with the mark-applied control — without it, Applied jobs leave Recommended and have no UI home today?
3. Confirm mark-applied is **Recommended list-row icon only** (no Applied button back on Job Analysis Report) — matches AST-565?

---

_Implementation detail may live in git history on `origin/dev`._
