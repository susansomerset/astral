# AST-633 — Table Layout fix

<!-- linear-archive: AST-633 archived 2026-06-23 -->

## Linear archive (AST-633)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-633/table-layout-fix  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Wide list and table screens (admin timesheets, execution history, job triage lists, company rosters, and other tabular views) are hard to use when many columns push key identifiers off-screen or long cell text blows up row height. Susan needs a consistent table layout layer: keep the leftmost columns and header row visible while scrolling, truncate noisy cell text with full value on hover, and preserve existing row-click paths into record detail. This belongs in Astral Interface now because several screens already scroll horizontally or carry very wide column sets, and the shared list table pattern is duplicated across ListPage and bespoke pages — one behavior contract avoids fixing the same UX screen by screen.

## Functional scope

* **Frozen left columns:** Every shared list/table view that uses the standard list table presentation (ListPage and pages that render the same list-table markup and styles) supports horizontal scroll with the leftmost **N** data columns remaining visible (sticky) while columns to the right scroll underneath. **N** is configurable per screen; when a screen does not specify **N**, it uses the product default from config (initial value **2**). Frozen columns follow the user's current column order (after drag-and-drop reorder where supported), counting from the left edge of the data columns.
* **Sticky header row:** When the user scrolls vertically through many rows, the table header row stays visible at the top of the table's scroll region (filters, page title, bulk bars, and section chrome outside the table remain as they are today).
* **Long cell display:** When cell content is long or would wrap to multiple lines, the visible cell shows at most the first **30** characters followed by an ellipsis. The full text appears in a hover tooltip. Screens that already open a record detail on row click keep that behavior; the tooltip is additive, not a replacement for existing detail flows.
* **Config default:** Add the default frozen-column count (**2**) to config as the single source of truth, exposed to the frontend through the existing UI config API so ListPage and bespoke list tables read the same default without hardcoding.
* **Per-screen overrides:** Any list screen may specify its own frozen-column count when the default is wrong for that layout (e.g., a screen that must keep three identifier columns visible). Unspecified screens inherit the config default.
* **Horizontal scroll where needed:** Wide tables enable horizontal scrolling in the table body rather than squishing columns; frozen-column behavior applies whenever horizontal overflow exists.

## Boundaries

* Does **not** change column definitions, sort/filter behavior, bulk actions, phase grouping, or row actions on individual screens — layout and cell presentation only.
* Does **not** redesign modals, entity detail pages, or add new row-detail surfaces where none exist today; row click continues to mean whatever that screen already wired.
* Does **not** alter backend debug logging (UI-only per Code Rules §1.5.1).
* Does **not** apply to non-tabular admin views (e.g., artifact editors, profile forms, script sandbox log stream, Data Management ad-hoc query result table unless explicitly adopted later).
* Must not break existing column reorder, resize, and localStorage layout persistence on ListPage.
* Per Code Rules §2.1, the default frozen-column count lives in config (not inline magic numbers in React); per-screen overrides are declarative props or equivalent, not scattered literals.

## Acceptance criteria

1. With config default **2**, a wide list screen with horizontal overflow keeps the leftmost **two** data columns visible while scrolling right; remaining columns scroll normally.
2. A screen that declares a different frozen-column count (e.g., **3**) keeps that many left columns visible instead of the default.
3. Scrolling down through a long table keeps header labels visible at the top of the table scroll area on representative screens using both ListPage (e.g., Agent Timesheets) and a bespoke grouped list (e.g., Recommended or Scheduled Actions phase table).
4. A cell with content longer than 30 characters displays truncated text with ellipsis; hovering shows the full value in a tooltip.
5. On a screen that already opens detail on row click (e.g., company or job list with modal), row click still opens that detail after this change.
6. List screens that do not override frozen-column count all inherit **2** from config via the UI config API — no hardcoded default in frontend source.
7. Sort, filter, checkbox selection, and column drag/reorder still work on at least one ListPage consumer and one bespoke table after the layout change.

## Dependencies and blockers

none.

## Open questions

1. When a list shows a checkbox selection column, does that column count toward the configured **N** frozen columns, or should the checkbox column always stay frozen in addition to **N** data columns?
   1. Do not count the checkbox or "action" column in the default, but always include them in the freeze.

---

## Original brief

Update UI components for lists to have a set number of fixed columns on the left and then scroll to the right.  In other words, support "freeze columns", so that those columns remain visible as we scroll to the right.

Freeze Table Headers at the top when scrolling down through records.

When row contents are very long or multiple lines, show only the first 30 characters and an ellipsis, add the full text in a tooltip, and allow user to click on the row to see a full detail of the record.

Make this a consistent setting for all list components, and where the UI does not specify how many columns to freeze, default to the [config.py](<http://config.py>) value, and set that value to 2 in [config.py](<http://config.py>).

### Comments

#### chuckles — 2026-06-15T07:46:58.026Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-657** | First two data columns not frozen (only action column) (Table Layout fix) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-657** — _First two data columns not frozen (only action column) (Table Layout fix)_
- **Issue reported:** On wide list/table screens with horizontal scroll, the **row action** column stays frozen (sticky) when scrolling right, but the **first two data columns** do **not** remain visible — contrary to config default **N=2**.
- **Should now:** With config default **2**, horizontal scroll on a wide ListPage (or equivalent list-table) keeps the leftmost **two data columns** visible (plus checkbox and action columns always frozen), while columns to the right scroll underneath.
- **Quick check (this fix only):**
  1. Open a wide **ListPage** consumer with horizontal overflow (e.g. Agent Timesheets) after staging/dev with AST-647 + AST-652 landed.
  2. Scroll horizontally to the right.
  3. Observe: action column sticks; first two data columns scroll away instead of staying visible.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### chuckles — 2026-06-15T00:58:16.509Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-633 (parent) | ftr/AST-633 |
| AST-647 | sub/AST-633/AST-647-list-table-layout-freeze-sticky-tooltips |
| AST-652 | sub/AST-633/AST-652-uat-remove-force-fit-autosize-columns |
| AST-657 | sub/AST-633/AST-657-uat-freeze-first-n-data-columns |

**Epic worktree:** `astral-AST-633/` — one active sub checked out at a time.

**Parent:** AST-633

— Chuckles

#### susan — 2026-06-15T00:56:24.952Z
Action column freezes, but not the first 2 columns, per the config default.

#### chuckles — 2026-06-15T00:48:53.081Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-652** | Remove force-fit; autosize list table columns (Table Layout fix) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-652** — _Remove force-fit; autosize list table columns (Table Layout fix)_
- **Issue reported:** List tables still use `table-layout: fixed` and `width: 100%` on `.list-page-table`, forcing columns to squish to fit the viewport (“force to fit on one screen”) instead of autosizing to content and scrolling horizontally when wide.
- **Should now:** Shared list/table presentation (**ListPage** and pages using the same list-table markup/styles) autosizes column widths to content (natural/`auto` layout), drops the force-fit-on-one-screen rule, and relies on horizontal scroll (with existing frozen-column + sticky-header behavio
- **Quick check (this fix only):**
  1. Open a wide **ListPage** consumer (e.g. Agent Timesheets) or **Admin Scheduled Actions** with many columns.
  2. Observe columns compressed to fit the container width rather than sizing to header/cell content.
  3. Compare to bespoke job phase tables that already use `tableLayout: "auto"`.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-14T23:56:00.996Z
The child ticket isn't in User Testing yet.

#### chuckles — 2026-06-14T23:23:00.416Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-633 (parent) | ftr/AST-633 |
| AST-647 | sub/AST-633/AST-647-list-table-layout-freeze-sticky-tooltips |
| AST-652 | sub/AST-633/AST-652-uat-remove-force-fit-autosize-columns |

**Epic worktree:** `astral-AST-633/` — one active sub checked out at a time.

**Parent:** AST-633

— Chuckles

#### susan — 2026-06-14T23:21:07.194Z
I forgot to mention that this should also TAKE OUT the "force to fit on one screen" rule for the component, and autosize the columns.

#### susan — 2026-06-14T23:12:03.113Z
Not sure why/how this got assigned to me.

#### chuckles — 2026-06-14T21:22:51.864Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-633 (parent) | ftr/AST-633 |
| AST-647 | sub/AST-633/AST-647-list-table-layout-freeze-sticky-tooltips |

**Epic worktree:** `astral-AST-633/` — one active sub checked out at a time.

**Parent:** AST-633

— Chuckles

#### chuckles — 2026-06-14T20:59:51.408Z
@susan Queued — **AST-635** is **In Progress** (Chuckles orchestrating); **AST-633** will dispatch when no other parent is **In Progress**.

— Chuckles

#### chuckles — 2026-06-14T18:22:15.437Z
@susan Open question before dispatch:

1. When a list shows a checkbox selection column, does that column count toward the configured **N** frozen columns, or should the checkbox column always stay frozen in addition to **N** data columns?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
