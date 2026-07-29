# AST-885 — Add filter flag to scheduled_actions for Avail > 0

<!-- linear-archive: AST-885 archived 2026-07-29 -->

## Linear archive (AST-885)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-885/add-filter-flag-to-scheduled-actions-for-avail-0  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Admin operators use Scheduled Actions to find and run dispatch rows that actually have work waiting. The screen already shows an Available (Avail) count per row, but zero-available rows dominate the list, so finding runnable work means scanning past noise. This feature adds a filter so Susan can instantly narrow the table to rows with Avail greater than zero — the same client-side filter bar pattern already used for AUTO, Debug, and the other operational filters.

## Functional scope

* Add an on-page filter control on Admin → Scheduled Actions that, when engaged, shows only rows whose Available count is greater than zero.
* When the filter is not engaged, Available count does not constrain which rows appear (existing Candidate, Task, Floor, AUTO, Debug, Freq, Min count, Batch size, and Run-count filters continue to work as today).
* The new filter intersects with every other active filter (AND), matching the existing filter-bar behavior.
* Rows whose Available count is zero or empty are excluded when the filter is engaged (same cases the Avail column already displays as an em dash).
* After filtering, section/group headers omit groups that have no remaining rows; remaining section AUTO summaries continue to reflect the filtered row set.
* Default state: filter not engaged (full list subject only to other filters).

## Boundaries

* Does not change how Available is calculated, claimed, or dispatched — display and eligibility math stay as they are.
* Does not change Avail column formatting (zero/empty still show as an em dash).
* Does not add server-side query parameters or alter the dispatch-tasks list API payload — filtering stays on-page like the rest of the Scheduled Actions filter bar.
* Does not change Run / Stop / AUTO / edit-modal / Manage Tasks behavior.
* Does not add range filters on Available (min/max) — this is a single greater-than-zero flag only.
* Must not break existing Scheduled Actions filters, sorting, section grouping, or polling.

## Acceptance criteria

1. On Admin → Scheduled Actions, a filter control is available that can be engaged to mean “Avail > 0.”
2. With that filter engaged and no other narrowing filters, every visible row shows a numeric Avail greater than zero (no em-dash Avail rows).
3. With that filter engaged together with any other existing filter(s), only rows that satisfy all engaged filters remain visible.
4. With that filter not engaged, rows with Avail zero or empty remain visible when they would otherwise match the other filters.
5. Engaging the filter removes empty section/group headers; clearing it restores sections that again have matching rows.
6. Page load / default view does not engage the Avail > 0 filter.

## Dependencies and blockers

none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-885 (parent) | ftr/AST-885-avail-gt-zero-filter |
| AST-887 | sub/AST-885/AST-887-avail-gt-zero-filter |

**Epic worktree:** `astral-AST-885/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | 47770c70-43c1-488a-9d92-58b5c7e58c48 |
| Betty | qa | b4a4e2e6-ce76-47f6-b414-672d91c80d17 |
| Radia | review | b90203bf-98db-4270-8046-5556a4e43c4a |

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
