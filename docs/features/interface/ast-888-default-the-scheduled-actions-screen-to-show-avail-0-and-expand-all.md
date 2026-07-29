# AST-888 — Default the scheduled_actions screen to show avail >0 and expand all

<!-- linear-archive: AST-888 archived 2026-07-29 -->

## Linear archive (AST-888)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-888/default-the-scheduled-actions-screen-to-show-avail-0-and-expand-all  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Admin operators open Scheduled Actions to find and run dispatch rows that actually have work waiting. After the Avail > 0 filter landed ([AST-885](https://linear.app/astralcareermatch/issue/AST-885/add-filter-flag-to-scheduled-actions-for-avail-0) / [AST-887](https://linear.app/astralcareermatch/issue/AST-887/avail-0-filter-on-scheduled-actions-add-filter-flag-to-scheduled)), Susan still has to engage that filter herself and only the first section auto-opens ([AST-785](https://linear.app/astralcareermatch/issue/AST-785/uat-dispatch-task-rows-missing-from-scheduled-actions-ui-vet-inflow)), so other groups with available entities stay hidden until she expands them one by one. This feature changes the landing experience: on entry, show only rows with available work and expand every section that still has rows, so every runnable group is visible in one glance.

## Functional scope

1. **Default Avail > 0 on page load.** When Admin → Scheduled Actions first loads, the existing Avail filter starts engaged as “> 0” with the same meaning as [AST-885](https://linear.app/astralcareermatch/issue/AST-885/add-filter-flag-to-scheduled-actions-for-avail-0) / [AST-887](https://linear.app/astralcareermatch/issue/AST-887/avail-0-filter-on-scheduled-actions-add-filter-flag-to-scheduled) (hide rows whose Available is zero or empty / em dash). The operator can still clear it back to All or change any other filter at any time.
2. **Expand every section that has visible rows.** On that default landing view, every section/group that still has at least one row under the current filters is expanded together so all sections with available entities are open at once — not only the first section.
3. **Operator control after landing.** The landing expand does not lock the list open: the operator may collapse individual sections (and use any Expand all / Collapse all chrome if the page has it). Changing filters continues to omit empty sections and keeps section AUTO summaries on the filtered set, as today.
4. **Filter intersection unchanged.** Default Avail > 0 still ANDs with Candidate, Section/Group, Task, Floor, AUTO, Debug, Freq, Min count, Batch size, and Run-count filters. No new filter kinds.

## Boundaries

* Does not change how Available is calculated, claimed, or dispatched.
* Does not change Avail column formatting (zero/empty still show as an em dash).
* Does not add server-side query parameters or alter the dispatch-tasks list API.
* Does not add new Avail modes (no “= 0 only,” no min/max range) — only changes the default of the existing greater-than-zero flag.
* Does not change Run / Stop / AUTO / edit-modal / Manage Tasks behavior.
* Does not redesign table layout, sticky columns, or the rest of the filter bar beyond default Avail and section expansion on this page.
* Does not change Recommended Jobs, Manage Tasks, or other sectioned screens’ default expansion — Scheduled Actions landing only.
* Must not break [AST-885](https://linear.app/astralcareermatch/issue/AST-885/add-filter-flag-to-scheduled-actions-for-avail-0) / [AST-887](https://linear.app/astralcareermatch/issue/AST-887/avail-0-filter-on-scheduled-actions-add-filter-flag-to-scheduled) filter semantics when the operator moves Avail away from the new default.
* Adjacent: [AST-886](https://linear.app/astralcareermatch/issue/AST-886/allow-expand-oneexpand-all-for-sectioned-list-components) (shared Expand One / Expand All) — opt into Expand All on Scheduled Actions; do not fork a conflicting page-local expand policy.
* Frontend-only — no backend debug-logging requirements.

## Acceptance criteria

1. Fresh navigation to Admin → Scheduled Actions engages the Avail filter as “> 0” without the operator touching the control.
2. With that default and matching rows in more than one section, every section that has at least one matching row is expanded at the same time (no actionable section left collapsed solely because another is open).
3. Under that default view with no other narrowing filters, every visible row shows a numeric Avail greater than zero (no em-dash Avail rows).
4. Switching Avail back to All restores zero/empty Avail rows that match the other filters, and empty-section omission continues to follow the filtered set.
5. After landing, the operator can collapse a section without that action being blocked by the default expand behavior.
6. The prior first-section-only auto-open no longer leaves other Avail > 0 sections collapsed on the default landing view when multiple sections have matching rows.

## Dependencies and blockers

* [AST-885](https://linear.app/astralcareermatch/issue/AST-885/add-filter-flag-to-scheduled-actions-for-avail-0) / [AST-887](https://linear.app/astralcareermatch/issue/AST-887/avail-0-filter-on-scheduled-actions-add-filter-flag-to-scheduled) (Avail > 0 filter on Scheduled Actions) — filter control must be present; currently User Testing.
* [AST-886](https://linear.app/astralcareermatch/issue/AST-886/allow-expand-oneexpand-all-for-sectioned-list-components) (Expand One / Expand All for sectioned lists) — ready (User Testing); use shared Expand All on Scheduled Actions; do not invent a page-local multi-expand fork. Susan: no block remains.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-888 (parent) | ftr/AST-888-sa-default-avail-expand-all |
| AST-894 | sub/AST-888/AST-894-sa-default-avail-expand-all |

**Epic worktree:** `astral-AST-888/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | 33d8deaf-ebc2-4667-8477-19e0fb446718 |
| Betty | qa | 3ff77fe3-3d0a-48ae-88bb-dcefa63ae0e0 |
| Radia | review | f39c5387-3eb2-4b21-8dde-4f2f11cf144e |

---

## Original brief

Please incorporate the recent changes so that when I click on scheduled actions I see all the different sections that have available entities to run.

### Comments

#### chuckles — 2026-07-14T01:03:51.093Z
@susan

Still blocked on Open question #1 (wait on AST-886 vs page-local expand). Answer in a comment or remove that bullet from the Description, then reassign Chuckles.

— Chuckles

#### chuckles — 2026-07-14T01:03:00.630Z
@susan

Dispatch blocked — Open questions still live on the Description (and unanswered in comments):

1. Should AST-888 wait on AST-886 (shared Expand All), or may Scheduled Actions ship page-local multi-section expand without waiting?

Reply (or clear that bullet from Open questions), then reassign Chuckles on Todo to resume.

— Chuckles

#### chuckles — 2026-07-13T19:36:52.156Z
@susan

1. Should AST-888 wait on AST-886 (shared Expand All) for multi-section expand on Scheduled Actions, or may this epic ship page-local multi-section expand without waiting on AST-886?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
