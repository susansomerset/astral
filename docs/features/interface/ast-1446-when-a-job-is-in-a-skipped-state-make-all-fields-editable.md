# AST-1446 — When a job is in a Skipped state, make all fields editable

<!-- linear-archive: AST-1446 archived 2026-09-09 -->

## Linear archive (AST-1446)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1446/when-a-job-is-in-a-skipped-state-make-all-fields-editable  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Jobs that land on Skipped are often wrong in the source fields — bad title, dead link, missing or garbage job description, or a state the operator needs to correct — but Job Detail only displays those values. This epic lets an authenticated operator fix title, link, job description, and state on a skipped job and persist the change, without opening agent responses for edit. Retry and Skip remain; this is the missing “correct the record” path so a skipped job can be repaired and put back on a legal next hop.

## Functional scope

Jobs whose current state is in the same skipped-state set the Skipped jobs list already uses can be edited from Job Detail (opened from Skipped). Editability follows the job’s current state, not which page opened the modal.

The operator can change and persist job title, job link, and job description. Empty job description still shows an editor on skipped jobs so a description can be pasted in.

The operator can change and persist job state. The state control offers only registered job states that the current state may legally enter under existing prior-state rules. Illegal jumps stay rejected.

Agent response / agent story tabs stay read-only. Non-skipped jobs keep today’s read-only Job Detail. Saving reloads the job and the Skipped list so the row reflects the new title, link, and (if state left skipped) disappears from Skipped.

## Architectural definition

* **Patterns to reuse** — `pattern.state.entity-state-transitions` (operator-chosen state still goes through the existing job transition path and prior-state check; no row UPDATE that skips history). `pattern.ui.admin-endpoint` (authenticated thin persist; eligibility resolved in the API, not invented in React). `pattern.ui.shared-button-roles` (Save is `btn primary`; discard/cancel is `btn secondary`). `pattern.layers.import-discipline` (UI calls core; core owns field write and transition). `pattern.config.config-block` (skipped-state membership and legal next states come from existing job-state config / state-ui manifest, not a parallel TypeScript list).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.state.job-prior-states-enforced` (no waived jumps). `astral.state.core-decides-transitions` (UI does not pick a next state in data). `astral.layers.ui-config-driven-business-logic` (editable vs locked is served from config/API). `astral.idioms.require-auth-on-protected-endpoints`. `astral.standards.no-hardcoded-sets`. `astral.standards.in-scope-only`. `astral.layers.import-direction`. `astral.ui.frontend-file-placement`. `astral.ui.naming-conventions`. `astral.standards.dry-and-focused-functions`.

## Boundaries

Does not make agent responses, grades, artifacts, company, created time, last-transition display, or state-history rows editable.

Does not waive prior-state law so an operator can jump to any registered state. If a desired target is not legal from the current skipped state, Retry (existing hop map) or a later prior-state change is the path — not this epic.

Does not unlock Job Detail on In Review, Recommended, or other non-skipped states. Jobs that appear on Skipped only because they are below the dispatch score floor, but whose state is not a skipped state, stay read-only.

Does not auto-re-run consult, scrape, or dispatch after a field save. Does not change bulk Retry, Skip This Job, Copy, or list-row Skip. Does not add Data Management / SQL editing. Does not edit Recommended Job Report.

## Acceptance criteria

1. Open a job whose state is a skipped state: title, link, job description, and state are editable controls; agent story tabs are not.
2. Save persists title, link, and job description; reload of Job Detail and the Skipped list shows the saved values.
3. A skipped job with no job description still offers a job-description editor; saving a pasted description persists it.
4. The state control lists only legal successor states; choosing one and saving moves the job through the existing transition path (history recorded). An illegal target is rejected and the job stays in its current state.
5. After a save that leaves a skipped state, the job is gone from Skipped on refresh and is not still shown as skipped.
6. Open a job that is not in a skipped state: title, link, job description, and state remain display-only as today.
7. Copy, Skip This Job, and Skipped Retry behave as they do today.

## Dependencies and blockers

none. Adjacent Interface work in User Testing (job modal Copy) must not be broken; this epic does not own Copy.

## Open questions

none.

## Proposed child tickets

#### 1!: **Persist skipped-job field and state edits - Ada**

Authenticated persist for title, link, and job description on jobs whose current state is skipped; state changes use the existing job transition path with prior-state enforcement. API tells the client whether the job is field-editable and which states are legal next. Rejects edits when the job is not skipped. Does not own the Job Detail form chrome (#2).
**Citations:** `pattern.state.entity-state-transitions`, `pattern.ui.admin-endpoint`, `pattern.config.config-block`, `astral.state.job-prior-states-enforced`, `astral.state.core-decides-transitions`, `astral.layers.ui-config-driven-business-logic`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`.
**Estimate: 3**

#### 2: **Job Detail skipped-field editors - Katherine**

When Job Detail loads a skipped job, title, link, job description, and state are editable; agent story stays read-only. Save uses #1; empty JD still shows an editor. Non-skipped jobs stay display-only. Copy / Skip This Job unchanged. After #1.
**Citations:** `pattern.ui.shared-button-roles`, `pattern.ui.admin-endpoint`, `astral.layers.ui-config-driven-business-logic`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.standards.dry-and-focused-functions`.
**Estimate: 3**

---

## Original brief

Except the agent responses, of course.  Allow state change, job description, job link, job title changes.

### Comments

#### katherine — 2026-08-25T00:48:47.740Z
Stage 1 unblocked: merged origin/ftr/AST-1446-when-a-job-is-in-a-skipped-state-make-all-fields-editable (registry parent_ftr; spawn --ftr AST-1446 alone does not match that ref). AST-1453 API present; resuming build.

#### katherine — 2026-08-25T00:47:36.040Z
🛑 Stage 1 blocked: AST-1453 API missing on worktree tip
Step: Stage 1 step 1 — Prerequisite check (`_attach_skipped_edit_meta` + `persist_skipped_edits` PUT)
Issue: After sync-child, `src/ui/api/api_jobs.py` has neither helper. `origin/ftr/AST-1446*` is not on origin (sync skipped ftr merge), so sibling #1 persist surface is not on `sub/AST-1446/AST-1454-job-detail-skipped-field-editors`. Plan forbids reimplementing persist or inventing a TS skipped-state list.
Proposed resolutions: 1) Chuckles merge-child AST-1453 → publish `origin/ftr/AST-1446-…`, then re-run sync-child on AST-1454 and resume build. 2) Otherwise green-light how #1 lands on this sub without inventing API here.

#### chuckles — 2026-08-25T00:14:09.789Z
AST-1454 gated on AST-1473 — LINEAR_KEY_JOAN missing; Joan PROCEED docs landed; cannot post §3i upshot.

#### chuckles — 2026-08-24T21:50:25.802Z
[thread-missing] Cursor chat `954428ff-603b-4c5b-836e-af4498850330` has no local `store.db` on **not-chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/954428ff-603b-4c5b-836e-af4498850330/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `6f950d28-0e2f-4695-9875-19e2827bc953`.

Watcher rule `datt` on `AST-1446` (Thread owner `AST-1446`).

---

_Implementation detail may live in git history on `origin/dev`._
