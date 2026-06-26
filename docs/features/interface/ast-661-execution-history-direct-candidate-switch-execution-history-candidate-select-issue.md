# AST-661 — Execution History direct candidate switch (Execution History Candidate Select Issue)

<!-- linear-archive: AST-661 archived 2026-06-23 -->

## Linear archive (AST-661)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-661/execution-history-direct-candidate-switch-execution-history-candidate  
**Status at archive:** Duplicate  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-656 — Execution History Candidate Select Issue  
**Blocked by / blocks / related:** parent: AST-656; duplicate: AST-662

### Description

## What this implements

Fix the Execution History (`/admin/performance`) on-page **Candidate** dropdown so selecting a different candidate immediately applies the filter without requiring an intermediate **All** selection. The dropdown display, ledger fetch, table rows, total-cost summary, and URL `candidate_id` param must stay in sync on every direct candidate-to-candidate change. Add or extend component-level regression coverage for direct A→B selection.

## Acceptance criteria

1. With two or more candidates in the system and Execution History showing rows for the nav-default candidate, selecting a different candidate in the on-page **Candidate** dropdown updates the visible rows and total cost to that candidate's ledger entries (within current date/task/status filters) without first selecting **All**.
2. Selecting **All** shows cross-candidate rows within the other filters; then selecting a specific candidate filters correctly (existing workaround path remains valid).
3. The dropdown displayed value always matches the active filter after each change (no silent snap-back to the previous candidate).
4. The browser URL's `candidate_id` param matches the active selection (**All** → param absent; specific candidate → param set to that id).
5. Task, Status, date, and Skip Checks filters remain unchanged when only Candidate changes.
6. Automated tests cover direct switch from one candidate id to another on Execution History (in addition to existing AST-634 cases for global candidate list and URL-seeded fetch).

## Boundaries

* Execution History only — do not change Scheduled Actions or Agent Timesheets unless a shared fix is strictly required and verified not to regress those screens.
* Does not change left-nav candidate selection, nav visibility rules, or `/api/nav_config`.
* Does not change dispatch ledger API semantics, backend filtering, or debug logging (UI-only bug).
* Does not redesign the filter bar or table layout.

## Notes for planning

* AST-634 introduced the shared admin candidate filter — inspect how nav sync vs manual pin interacts with state updates on Execution History.
* Likely files: React admin performance/execution history components and existing AST-634 test coverage.
* plan-child §3.5 — new components go in `src/components/` flat.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-656-execution-history-candidate-select`, child `sub/AST-656/<child-id>-execution-history-candidate-switch`. Created at **dispatch-parent**.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
