# AST-1291 — Move table lookup and field lookup objects on Data Management page

<!-- linear-archive: AST-1291 archived 2026-08-19 -->

## Linear archive (AST-1291)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1291/move-table-lookup-and-field-lookup-objects-on-data-management-page  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Admin Data Management page puts the table/field schema browser on the left of the SQL workbench, which steals horizontal space from the query input Susan actually types into. This epic moves that lookup chrome to the right of the SQL input so the primary writing surface sits first, while table and field lookups stay immediately available for drafting queries.

## Functional scope

* **Schema browser on the right of SQL** — On Data Management, the tables list and the fields list for the selected table appear to the right of the SQL input (and its history controls), instead of to the left. Selecting a table still reveals that table’s fields in the same lookup grouping; only placement changes.
* **Behavior unchanged** — Table list loading, table selection, field display (names/types/PK cues), SQL history navigation, Run, result grid, Copy Output, and Table Upsert stay as they work today. This epic is layout only.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` (catalog has admin-endpoint / layer patterns, not an approved admin-page layout pattern; this is a placement change on an existing Admin page).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.standards.in-scope-only` (layout-only; no feature creep); `astral.ui.frontend-file-placement` (stay in existing page placement); `astral.ui.naming-conventions` (no rename churn); `astral.layers.ui-config-driven-business-logic` (do not invent new frontend business rules while moving chrome); `astral.git.engineer-test-tree-ban` (engineers do not own the test tree); plus the active `universal` orchestration set for pipeline discipline.

## Boundaries

* Does **not** change SQL execution, schema discovery queries, upsert/copy flows, session SQL history semantics, or admin auth.
* Does **not** redesign Table Upsert, result-grid presentation, or other Admin pages.
* Does **not** add responsive/hamburger work (that lives under AST-1284 / AST-1286).
* Must **not** break existing Data Management behaviors listed under Functional scope.

## Acceptance criteria

1. On Admin → Data Management, the tables lookup panel is visually to the **right** of the SQL input window (not to the left).
2. After selecting a table, the fields lookup for that table appears with the tables lookup on the **right** of the SQL input (same grouping as today, mirrored side).
3. SQL history controls, Run, result display, Copy Output, and Table Upsert still work as before this change.
4. No other Admin page layout changes ship in this epic.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1: **Move Data Management schema browser right of SQL - Katherine**

Relocate the tables + fields lookup grouping from the left of the SQL workbench to the right of the SQL input on Data Management. Preserve selection and display behavior; do not own upsert, SQL execution, or other Admin pages.
**Citations:** `astral.standards.in-scope-only`; `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`; `astral.layers.ui-config-driven-business-logic`.

Monolith note: two Functional scope bullets, one child — intentional single vertical slice (one page row reorder; inseparable for UAT).

---

## Original brief

Reposition the table structure lookup to be to the right of the SQL input window on Data Management page.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1291 (parent) | ftr/AST-1291-move-table-lookup-and-field-lookup-objects-on-data |
| AST-1295 | sub/AST-1291/AST-1295-move-data-management-schema-browser-right-of-sql |

**Epic worktree:** `astral-AST-1291/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/8d5b6185d527b8304c8d7fb6a044a94d/88838791-10b2-43fa-8c03-006be7a32645/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/068b3ce1-0195-4356-9dac-f4ef4bfe7baf/store.db` |
| Radia | review | `/home/susan/.cursor/chats/8d5b6185d527b8304c8d7fb6a044a94d/b4b7c6ea-743f-4c89-8c0e-b020ebc0bec4/store.db` |

### Comments

#### chuckles — 2026-08-10T04:30:13.934Z
[check-linear] answered — server LAN IP is `192.168.4.36` (hostname `chuckles`).

— Chuckles

#### susan — 2026-08-10T04:10:01.267Z
@chuckles what ip is your server? i lost connection on the local network and it rebooted to a different address.

---

_Implementation detail may live in git history on `origin/dev`._
