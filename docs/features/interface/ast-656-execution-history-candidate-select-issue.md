# AST-656 — Execution History Candidate Select Issue

<!-- linear-archive: AST-656 archived 2026-06-23 -->

## Linear archive (AST-656)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-656/execution-history-candidate-select-issue  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Execution History admin screen gained an on-page **Candidate** filter in [AST-634](https://linear.app/astralcareermatch/issue/AST-634) (parent [AST-628](https://linear.app/astralcareermatch/issue/AST-628)): **All** plus the full global candidate list, defaulting to the left-nav selection, with URL persistence for bookmarks. Susan cannot reliably switch from one specific candidate to another — the dropdown opens and accepts a click, but the filtered ledger does not update unless she selects **All** first, then picks the target candidate. That breaks day-to-day admin use (comparing runs across candidates, drilling into one person's history) and undermines the [AST-634](https://linear.app/astralcareermatch/issue/AST-634/admin-candidate-filter-on-three-admin-tabs-remove-selected-candidate) contract. This bug fix restores direct candidate-to-candidate switching on Execution History only.

## Functional scope

* On **Execution History** (`/admin/performance`), choosing any candidate in the on-page **Candidate** dropdown immediately applies that filter: the dropdown shows the selected candidate, the ledger request uses that candidate (or no candidate filter when **All** is selected), and the table and total-cost summary reflect the new result set without requiring an intermediate **All** selection.
* Switching directly from candidate A to candidate B works in one step whenever both appear in the dropdown (including when A matches the current left-nav selection).
* **All** continues to show ledger rows for every candidate within the other active filters (task, status, date range, Skip Checks).
* Other filter controls (Task, Status, From, To, Skip Checks) behave as before; changing Candidate does not reset them.
* URL query behavior for `candidate_id` remains consistent with AST-634: a specific candidate is reflected in the URL; **All** removes `candidate_id`; other query params are preserved.
* After a manual Candidate change on Execution History, the on-page filter stays pinned to that choice until Susan changes it again (nav sync per [AST-634](https://linear.app/astralcareermatch/issue/AST-634/admin-candidate-filter-on-three-admin-tabs-remove-selected-candidate) applies only until the first manual pick on that visit).
* Component-level regression coverage is added or extended so direct candidate-to-candidate selection on Execution History is exercised (not only **All** or URL-seeded loads).

## Boundaries

* Primary deliverable is correct Execution History Candidate filter behavior. Scheduled Actions and Agent Timesheets are out of scope unless a shared fix is strictly required and verified not to regress those screens.
* Does not change left-nav candidate selection, nav visibility rules, or `/api/nav_config`.
* Does not change dispatch ledger API semantics, backend filtering, or debug logging (UI-only bug).
* Does not redesign the filter bar, table layout ([AST-633](https://linear.app/astralcareermatch/issue/AST-633)), or re-open AST-628/634 feature scope beyond this defect.

## Acceptance criteria

1. With two or more candidates in the system and Execution History showing rows for the nav-default candidate, selecting a different candidate in the on-page **Candidate** dropdown updates the visible rows and total cost to that candidate's ledger entries (within current date/task/status filters) without first selecting **All**.
2. Selecting **All** shows cross-candidate rows within the other filters; then selecting a specific candidate filters correctly (existing workaround path remains valid).
3. The dropdown displayed value always matches the active filter after each change (no silent snap-back to the previous candidate).
4. The browser URL's `candidate_id` param matches the active selection (**All** → param absent; specific candidate → param set to that id).
5. Task, Status, date, and Skip Checks filters remain unchanged when only Candidate changes.
6. Automated tests cover direct switch from one candidate id to another on Execution History (in addition to existing [AST-634](https://linear.app/astralcareermatch/issue/AST-634/admin-candidate-filter-on-three-admin-tabs-remove-selected-candidate) cases for global candidate list and URL-seeded fetch).

## Dependencies and blockers

* [AST-634](https://linear.app/astralcareermatch/issue/AST-634) (Done) — introduced the shared admin candidate filter on Execution History; this ticket corrects defective behavior in that delivery.
* [AST-628](https://linear.app/astralcareermatch/issue/AST-628) (Done) — parent epic for admin candidate filter consistency.
* None blocking start.

## Open questions

none.

---

## Original brief

I can't change the candidate dropdown selection on Execution History page.  I can open it, I can click on another candidate, but it doesn't take effect.  Only if I click on All first does it do the right thing.

### Comments

#### chuckles — 2026-06-15T02:04:14.496Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-656 (parent) | ftr/AST-656-execution-history-candidate-select |
| AST-662 | sub/AST-656/AST-662-execution-history-candidate-switch |

**Epic worktree:** `astral-AST-656/` — one active sub checked out at a time.

**Parent:** AST-656

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
