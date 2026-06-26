# AST-705 — Nav Menu stops working while on agent timesheets

<!-- linear-archive: AST-705 archived 2026-06-23 -->

## Linear archive (AST-705)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-705/nav-menu-stops-working-while-on-agent-timesheets  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Agent Timesheets persists filter state in the URL (candidate, dates, batch). While on this page, sidebar navigation fails: clicking another destination briefly changes the address bar, then snaps back to `/admin/agent_timesheets`, trapping Susan on the page until a full refresh. That blocks normal admin workflow. [AST-634](https://linear.app/astralcareermatch/issue/AST-634/admin-candidate-filter-on-three-admin-tabs-remove-selected-candidate) added URL-backed candidate sync here; [AST-662](https://linear.app/astralcareermatch/issue/AST-662/execution-history-direct-candidate-switch-execution-history-candidate) fixed a related race on Execution History but deferred Agent Timesheets pending UAT. Susan's report confirms the defect on this screen and extends it to route escape, not only in-page candidate switching.

## Functional scope

* Restore reliable sidebar navigation from Agent Timesheets to any other enabled nav destination (admin siblings and non-admin sections reachable from the same shell).
* Eliminate flicker-and-revert: after a nav click, pathname and rendered page must match the selected item without refresh.
* Preserve [AST-634](https://linear.app/astralcareermatch/issue/AST-634/admin-candidate-filter-on-three-admin-tabs-remove-selected-candidate) candidate-filter behavior: default from left-nav candidate, **All** option, manual pin blocks nav sync, export respects filtered candidate when set.
* Preserve existing timesheet list, totals, filters (dates, batch, model, performance), and CSV export — no change to data semantics beyond fixing navigation.

## Boundaries

* Does not change timesheet API, cost calculation, or ledger schema.
* Does not redesign the shared candidate filter hook beyond what is required to stop navigation interference on this page (Execution History already received its fix in [AST-662](https://linear.app/astralcareermatch/issue/AST-662/execution-history-direct-candidate-switch-execution-history-candidate)).
* Does not change nav config, sidebar layout, or admin route gating.
* Does not scope-fix unrelated admin pages unless a minimal shared guard is necessary and safe.
* Must not regress Execution History or Scheduled Actions candidate-filter behavior from AST-634/662.

## Acceptance criteria

1. With Agent Timesheets active and a left-nav candidate selected, clicking at least two other **Admin** nav items (e.g. Scheduled Actions, Execution History) navigates successfully — pathname changes and the destination page renders; no return to `agent_timesheets`.
2. With Agent Timesheets active, clicking at least one **non-admin** nav item navigates successfully with the same no-revert behavior Susan reported as intermittently failing.
3. After navigating away and back to Agent Timesheets, filters behave per AST-634: empty URL defaults candidate from nav; manually pinned candidate stays pinned; **All** shows cross-candidate rows.
4. In-page candidate dropdown supports direct switch between two specific candidates without selecting **All** first (parity with [AST-662](https://linear.app/astralcareermatch/issue/AST-662/execution-history-direct-candidate-switch-execution-history-candidate) on Execution History).
5. No new console errors during nav-away from Agent Timesheets in a normal session.

## Dependencies and blockers

* [AST-634](https://linear.app/astralcareermatch/issue/AST-634/admin-candidate-filter-on-three-admin-tabs-remove-selected-candidate) (Done) — URL-backed candidate filter on Agent Timesheets.
* [AST-662](https://linear.app/astralcareermatch/issue/AST-662/execution-history-direct-candidate-switch-execution-history-candidate) (Done) — hook manual-pin guard and Execution History URL-backed stabilization; Agent Timesheets follow-up was deferred pending UAT.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-705 (parent) | ftr/ast-705-nav-menu-stops-working-while-on-agent-timesheets |
| AST-709 | sub/AST-705/AST-709-agent-timesheets-nav-and-candidate-filter |

**Epic worktree:** `astral-AST-705/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | 4f63e977-7aff-4630-8cc7-c34687924865 |
| Betty | qa | 438083ff-adfc-42f1-9f4a-979f074a36d1 |
| Radia | review | 7ae79a91-8e6f-4c50-8131-0cc161c3efd2 |

---

## Original brief

When I have agent Timesheets active, if I click on other Admin menu options (and sometimes even other menu options), the address bar flickers, but returns to agent_timesheets.  This is not an issue from other menu options in the nav.

Refreshing the page resolves the issue, but it shouldn't be happening.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
