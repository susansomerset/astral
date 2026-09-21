# AST-1485 — Enable Applied job list in nav

<!-- linear-archive: AST-1485 archived 2026-09-09 -->

## Linear archive (AST-1485)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1485/enable-applied-job-list-in-nav  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators can mark jobs applied from Recommended (AST-1464 shipped), but Jobs → Applied is still a permanently disabled nav stub on `origin/dev`: `NAV_CONFIG` keeps `"enabled": False`, `GET /api/jobs?view=applied` falls through to `[]`, and `JobsApplied` is an empty shell. The same slice landed in AST-1479 and was reverted during AST-1476 conflict resolution while component tests for AST-1479 remain on dev. Susan wants Applied visible and usable — not hidden behind a disabled nav item.

## Functional scope

* **Applied nav visible.** Jobs → Applied appears in the left nav as an enabled item (same treatment as Recommended / Skipped / In Review), not a grayed permanently disabled stub.
* **Applied list API.** Authenticated `GET /api/jobs?view=applied&candidate_id=<id>` returns jobs in post-applied candidate states for that candidate, ordered by `state_changed_at` like sibling job views.
* **Applied list page.** `/jobs/applied` loads those rows for the selected candidate and shows post-applied row actions (Reapply / Interview / Rejected / Ghosted) via the shared candidate-action notes modal, with in-place refresh after successful transitions and a visible error toast on failure.
* **Out of scope.** Responded list (nav stays disabled); mark-applied from Recommended or report Applied/Skip (already shipped under AST-1464); nav badge counts for Applied; Job Analysis Report or Job Detail from the Applied page; new `candidate_action` endpoints or `JOB_STATES` priors changes.

## Component scope

* `src/utils/config.py` — **modified** — add named applied-view state list (parallel to `RECOMMENDED_JOB_STATES` / `SKIPPED_STATES`); remove `"enabled": False` from Jobs → Applied in `NAV_CONFIG`.
* `src/ui/api/api_jobs.py` — **modified** — implement `view=applied` list branch (today the final `else` returns `[]`).
* `src/ui/frontend/src/pages/JobsApplied.tsx` — **modified** — replace empty `ListPage` stub with a real applied jobs list using shared candidate-action plumbing.

## Technical scope

* `config` — new applied-view state constant listing the four post-applied outcomes already handled by `CandidateJobRowActions` (`CANDIDATE_APPLIED`, `CANDIDATE_INTERVIEW`, `CANDIDATE_REJECTED`, `CANDIDATE_GHOSTED`), with membership asserted against `JOB_STATES`; Applied nav item omits `enabled` (always enabled) while Responded keeps `"enabled": False`.
* `api_jobs.list_view` — for `view=applied`, call `list_jobs` with the applied-view state list, `candidate_id` scope, and `order_by=state_changed_at`; return flattened rows like `view=recommended`.
* `JobsApplied` — fetch `/api/jobs?view=applied&candidate_id=…` on candidate selection; render flat table (Actions | Job Title | Company | State | Updated); wire `useCandidateJobActions` + `CandidateActionNotesModal` + `useInPlaceLiveRefresh` + error `Toast` following sibling job list pages (simpler than Recommended — no state sections, no report modal, no Skip handler).

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.in-place-live-refresh` — Applied list refreshes in place after candidate_action transitions. [current](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.in-place-live-refresh.md>)
  * `pattern.ui.icon-control` — post-applied row actions remain icon-controls via `CandidateJobRowActions`. [current](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.icon-control.md>)
* **New patterns proposed** — none.
* **Applicable statutes**
  * `astral.standards.no-hardcoded-sets` — applied-view state membership lives in config, not inline in API or page. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
  * `astral.layers.ui-config-driven-business-logic` — nav enablement and view state lists from config; frontend renders resolved `/api/nav_config`. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>)
  * `astral.state.core-decides-transitions` — page uses existing `candidate_action` path, not direct saves. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.core-decides-transitions.md>)
  * `astral.state.job-prior-states-enforced` — illegal post-applied hops stay 409 with visible UI error. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.job-prior-states-enforced.md>)
  * `astral.idioms.require-auth-on-protected-endpoints` — applied list and action routes stay behind existing jobs auth. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/idioms/astral.idioms.require-auth-on-protected-endpoints.md>)
  * `astral.ui.frontend-file-placement` — page stays under established UI layout. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.frontend-file-placement.md>)
  * Universal orchestration set (`orch.pipeline.*`, `orch.git.*`, `orch.roles.*`) applies to delivery mechanics as usual.

## Acceptance criteria

1. Jobs → Applied is enabled in nav (`/api/nav_config` serves Applied with `enabled: true`) and routes to a non-stub page.
2. For a candidate with jobs in post-applied states, `/jobs/applied` lists those jobs; empty state copy when none exist.
3. Post-applied row icon actions (Reapply / Interview / Rejected / Ghosted) work via shared notes + `candidate_action`, with list refresh after success.
4. Failed illegal transitions show a visible error toast (no silent no-op).
5. Responded nav item remains permanently disabled; no regression to Recommended / Skipped / In Review nav or list behavior.
6. Existing AST-1479 component tests on dev pass once product code is restored (`TestAst1479AppliedJobStatesAndNav`, `test_list_applied_uses_applied_job_states`, `JobsApplied — AST-1479 applied list home`).

## Open questions

none

## Proposed child tickets

Single child is intentional: config state list, nav flip, API branch, and page must ship atomically for UAT — enabling nav without a working list/API would violate AC1–AC2. Prior art: AST-1479 (re-land after AST-1476 conflict resolution).

#### 1: **Applied jobs list home (re-land) - Ada**

Restore the AST-1479 vertical slice on `origin/dev`: applied-view state constant + nav enablement in config, `view=applied` API branch, and real `JobsApplied` page with shared candidate actions. Does not own mark-applied entry points (AST-1464 siblings) or Responded list.
**Citations:** `pattern.ui.in-place-live-refresh`; `pattern.ui.icon-control`; `astral.standards.no-hardcoded-sets`; `astral.layers.ui-config-driven-business-logic`; `astral.state.core-decides-transitions`; `astral.state.job-prior-states-enforced`; `astral.idioms.require-auth-on-protected-endpoints`; `astral.ui.frontend-file-placement`
**Scope:** `src/utils/config.py` (modified — applied-view state list + NAV_CONFIG Applied enabled); `src/ui/api/api_jobs.py` (modified — `view=applied` list implementation); `src/ui/frontend/src/pages/JobsApplied.tsx` (modified — real applied list + shared candidate actions)
**Estimate: 3**

---

## Original brief

dont hide them!

### Comments

#### chuckles — 2026-08-27T01:27:33.341Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1498** | CANDIDATE_APPLIED job missing from Applied screen |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1498** — _CANDIDATE_APPLIED job missing from Applied screen_
- **Quick check:** re-run the failure you reported for **AST-1498**.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### chuckles — 2026-08-27T01:25:59.828Z
[refresh-ftr] blocked: attempt 1/3

Bible / test-tree (@Betty White):
- docs/test-bible/frontend/pages.md

Conflict: merging origin/dev into origin/ftr/AST-1485-enable-applied-job-list-in-nav.
ftr tip has ### AST-1498 · AST-1485; origin/dev has ### AST-1495 · AST-1484 after that point.
Keep both sections (AST-1498 then AST-1495), remove conflict markers, push reconcile to origin/ftr/AST-1485-enable-applied-job-list-in-nav so refresh-ftr can retry.

#### susan — 2026-08-26T15:37:35.223Z
\[bug\]

There is a job in state CANDIDATE_APPLIED that does not appear on the Applied screen.

#### chuckles — 2026-08-26T15:15:47.240Z
AST-1488 REVIEW — merge-child blocked; recalling Ada for missing test(AST-1488): after green manifest.

---

_Implementation detail may live in git history on `origin/dev`._
