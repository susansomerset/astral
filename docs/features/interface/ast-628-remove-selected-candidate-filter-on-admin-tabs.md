# AST-628 — Remove "Selected Candidate" filter on admin tabs

<!-- linear-archive: AST-628 archived 2026-06-23 -->

## Linear archive (AST-628)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-628/remove-selected-candidate-filter-on-admin-tabs  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Administrators operating dispatch, execution history, and cost timesheets often need to focus on one candidate but sometimes need a cross-candidate view. Today **Scheduled Actions** hides candidate scoping behind the left-nav selection (rows are filtered with no on-page control), while **Execution History** and **Agent Timesheets** offer partial candidate filtering that does not default to the nav selection and is inconsistent between screens (dropdown vs free-text, options derived only from loaded rows on Execution History). This feature makes candidate scoping explicit and uniform on those three admin screens: a visible **Candidate** filter with **All**, defaulting to whoever is selected in the left nav, so Susan can see the current candidate's operational picture at a glance and switch to **All** when debugging across candidates.

## Functional scope

* **Scheduled Actions** (`/admin/scheduled_actions`): Add a **Candidate** filter control alongside the existing Task filter. Options: **All** plus every candidate the app already knows from the global candidate list (same source as the left-nav selector). **Remove** the silent rule that always restricts the table to the left-nav selected candidate; filtering is driven only by the on-page **Candidate** control (and existing Task filter). Default filter value: the left-nav selected candidate when one is selected; **All** when none is selected.
* **Execution History** (`/admin/performance_monitor` or equivalent route): Keep the existing **Candidate** filter but populate options from the full candidate list (not only candidates appearing in the currently loaded result set). Default filter value: the left-nav selected candidate when one is selected; **All** when none is selected. Existing Task, Status, date, and Skip Checks filters unchanged.
* **Agent Timesheets** (`/admin/agent_timesheets`): Replace the free-text **Candidate** field with the same **Candidate** dropdown pattern (**All** + full candidate list). Default filter value: the left-nav selected candidate when one is selected; **All** when none is selected. Existing date, batch, and other filters unchanged; export respects the active candidate filter.
* **Nav sync:** While the on-page **Candidate** filter is still at its **default** (tracking the left-nav selection — Susan has not manually chosen **All** or a different candidate on that screen), changing the left-nav candidate updates the on-page filter to match. After Susan manually changes the on-page filter, it **stays** on her choice until she changes the dropdown again (left-nav changes do not override a manual selection).
* **Consistent labeling:** On all three screens the control is labeled **Candidate**, first option **All**, remaining options identify candidates in a human-readable way (friendly name when available, with id distinguishable when names collide or are missing).
* **Data scope:** When a specific candidate is selected in the on-page filter, list data, totals, and export (where applicable) reflect only that candidate's rows. When **All** is selected, show rows for every candidate (subject to any other active filters on that screen).

## Boundaries

* Does **not** change the left-nav candidate selector or how other candidate-scoped screens (jobs, companies, profile, artifacts, Manage Tasks, Task Prompts, etc.) use the nav selection.
* Does **not** add server-side authorization changes or new admin APIs unless a plan discovers an existing endpoint cannot support **All** — prefer client-side filtering and existing list endpoints.
* Does **not** redesign table columns, phase grouping, run/stop behavior, or non-candidate filters on these three screens.
* Does **not** require backend debug-logging changes (UI-only feature).
* Must not break existing Execution History URL filter params for task, status, and dates; candidate param behavior may change to match the new defaulting rules.

## Acceptance criteria

1. On **Scheduled Actions**, with left-nav candidate **A** selected and no manual filter change yet, the **Candidate** filter shows **A** and the table lists only dispatch tasks for **A**; choosing **All** shows tasks for every candidate; choosing **B** shows only **B**'s tasks. No hidden nav-only filtering remains.
2. On **Execution History**, with left-nav candidate **A** selected on first visit (no `candidate_id` in URL), the **Candidate** filter defaults to **A** and the ledger list is scoped to **A**; **All** shows all candidates (within other active filters); the dropdown lists every candidate from the global list, including candidates with zero rows in the current date window.
3. On **Agent Timesheets**, with left-nav candidate **A** selected, the **Candidate** dropdown defaults to **A**; **All** shows all candidates within date/other filters; totals bars and **Export CSV** match the active candidate filter.
4. With no candidate selected in the left nav, all three screens default the **Candidate** filter to **All**.
5. All three screens use the same **Candidate** / **All** dropdown pattern and readable candidate labels.
6. **Nav sync:** With the on-page filter still at default on a screen, switching left-nav from **A** to **B** updates that screen's **Candidate** filter to **B** without a page reload. After Susan manually sets the on-page filter to **All** or a specific candidate other than the current default, subsequent left-nav changes do **not** change the on-page filter until she changes the dropdown.

## Dependencies and blockers

none.

## Open questions

none.

---

## Original brief

Please add a Candidate filter box for Scheduled Actions, Execution History, and Agent Timesheets, where "All" is an option, but the default is the selected candidate from the left nav pane.

### Comments

#### chuckles — 2026-06-14T18:21:20.571Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-628 (parent) | ftr/ast-628-remove-selected-candidate-filter-on-admin-tabs |
| AST-634 | sub/AST-628/AST-634-admin-candidate-filter-on-three-admin-tabs |

**Epic worktree:** `astral-AST-628/` — one active sub checked out at a time.

**Parent:** AST-628

— Chuckles

#### chuckles — 2026-06-14T17:42:41.634Z
@susan One open question before dispatch:

1. When you change the left-nav candidate after manually setting the on-page **Candidate** filter (e.g. to **All** or someone else), should the on-page filter follow the nav again, or stay on your manual choice until you change the dropdown?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
