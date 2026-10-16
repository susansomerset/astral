# AST-2166 — Add a Select All checkbox (and unchecking it selects none) to Recommended list

<!-- linear-archive: AST-2166 archived 2026-10-16 -->

## Linear archive (AST-2166)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2166/add-a-select-all-checkbox-and-unchecking-it-selects-none-to  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 1  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Jobs → Review and Jobs → Ready lists (both rendered by the Recommended list page) already support row checkboxes and bulk Skip / Applied / Generate Artifacts, but Susan has to tick every row one by one to act on a whole list. A single Select All checkbox in the table header lets her select every job in a section with one click — and clear them all with one more — so bulk triage is actually fast.

## Functional scope

1. **Select All checkbox.** Each section table on the Recommended list page gets a checkbox in the header of its existing select column. Checking it selects every job row in that section.
2. **Unchecking selects none.** When the Select All checkbox is checked, clicking it again deselects every job row in that section.
3. **Header reflects the rows.** The Select All checkbox is checked exactly when every row in its section is selected (including when Susan ticked them all individually) and unchecked otherwise; clicking it while only some rows are selected selects all of them. This matches the existing header checkbox on Admin → Manage Email.
4. **Bulk bar unchanged.** Selection made through Select All drives the existing bulk buttons and counts exactly like row-by-row selection, and clears after a bulk action the same way it does today.

Out of scope: no indeterminate ("partially selected") visual state, no selection persistence, no change to bulk actions, row actions, sorting, or the Analysis toggle, and no other list pages.

## Component scope

* `src/ui/frontend/src/pages/JobsRecommended.tsx` — **modified** — adds the Select All checkbox to each section's select-column header and its select-all / select-none behaviour over that section's rows.

## Technical scope

* `src/ui/frontend/src/pages/JobsRecommended.tsx` — **modified function** (`Recommended` page component): render a checkbox in the currently empty select-column `<th>` of each section table; its checked state is derived from the section's rows against the existing page-level `selected` set (not stored separately); checking adds all of the section's `astral_job_id`s to `selected`, unchecking removes them. Reuses the existing `selected` state, so `selectedIds` / `generateIds` and the bulk bar need no change. The header checkbox's accessible name must not match the existing row-checkbox name pattern (`Select <job title>`), so row-checkbox queries keep counting rows only.

## Architectural definition

* **Patterns to reuse:** no established pattern applies — no in-force pattern governs frontend list pages. (Code precedent only, not canon: the header checkbox in `src/ui/frontend/src/pages/AdminManageEmail.tsx`.)
* **New patterns proposed:** none.
* **Applicable statutes:** none — no in-force directive (`canon/directives/active/`) covers frontend list pages; same empty Canon Scope as AST-1968 on this page.

## Acceptance criteria

1. **Header checkbox exists.** On Jobs → Review with at least one job, each section table's first header cell contains exactly one checkbox. **Fail:** no checkbox in the select-column header, or more than one.
2. **Select All.** With no rows selected, click the header checkbox: every row checkbox in that section is checked and the bulk bar shows `Skip (n)` / `Applied (n)` where n = the section's job count. **Fail:** any row in the section unchecked, or wrong n.
3. **Select none.** With all rows selected via the header, click it again: every row checkbox in the section is unchecked and no bulk buttons render. **Fail:** any row still checked, or bulk bar still visible.
4. **Partial → all.** Check one row only (header stays unchecked), then click the header: every row in the section becomes checked. **Fail:** header checked with only one row selected, or click clears instead of selecting all.
5. **Manual all → header checked.** Tick every row in a section individually: the header checkbox shows checked. Untick one: it shows unchecked. **Fail:** header state does not follow the rows.
6. **Bulk action clears it.** Select All, then run bulk Skip: after completion the header checkbox and all row checkboxes are unchecked. **Fail:** header still checked.
7. **Row-checkbox queries unaffected.** In `tests/component/frontend/pages/test_JobsRecommended.test.tsx`, `getAllByRole("checkbox", { name: /^Select / })` still returns exactly one checkbox per job row (the header checkbox's name does not match it). **Fail:** count includes the header checkbox.
8. **Same on Ready.** AC 2 and 3 pass on Jobs → Ready. **Fail:** either fails there.
9. **Builds clean; no new lint.** In `src/ui/frontend`, `npm run build` exits 0 and `npm run lint` reports no problem absent on `origin/dev`. **Fail:** non-zero build or any new lint problem.

## Open questions

none

## Proposed child tickets

#### 1: **Select All checkbox on Recommended list - Ada**

Adds the header Select All / select-none checkbox to each section of the Recommended list page (Jobs → Review and Jobs → Ready), driving the existing selection and bulk bar. Does not change bulk actions, row actions, or any other page.
**Citations:** none — no in-force directive governs frontend list pages (see Architectural definition).
**Scope:** `src/ui/frontend/src/pages/JobsRecommended.tsx` — **modified function** (`Recommended` page component): render a checkbox in the currently empty select-column `<th>` of each section table; its checked state is derived from the section's rows against the existing page-level `selected` set (not stored separately); checking adds all of the section's `astral_job_id`s to `selected`, unchecking removes them. Reuses the existing `selected` state, so `selectedIds` / `generateIds` and the bulk bar need no change. The header checkbox's accessible name must not match the existing row-checkbox name pattern (`Select <job title>`), so row-checkbox queries keep counting rows only.
Estimate: 1

**New patterns:** none.

**Monolith check:** Functional scope has 4 items, 1 child — intentional: one header checkbox in one file; the four items are a single inseparable behaviour.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
