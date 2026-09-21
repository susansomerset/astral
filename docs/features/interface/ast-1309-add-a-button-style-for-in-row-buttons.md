# AST-1309 — Add a button style for in-row buttons

<!-- linear-archive: AST-1309 archived 2026-08-19 -->

## Linear archive (AST-1309)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1309/add-a-button-style-for-in-row-buttons  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Low / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Shared labeled buttons are sized for toolbars, modal footers, and page actions. When those same controls sit inside a data-table row, their height stretches the row and wastes vertical space. This epic adds one compact in-row size to the existing labeled-button family and applies it to every labeled shared-role button that lives in a table row, so lists stay dense without inventing a third control family or turning word labels into icons.

## Functional scope

1. **In-row size on the labeled family** — The shared labeled-button roles keep their meaning and colors. An optional in-row size makes those controls about 60% the height of the page/toolbar labeled button, still with a readable word label.
2. **Apply to table-row labeled buttons** — Every labeled shared-role button that sits in a data-table row uses the in-row size, including dispatch Run / Stop (and the in-row busy/stop label) on Scheduled Actions. New in-row labeled actions follow the same size.
3. **Leave full-size and icon-only alone** — Page, toolbar, modal, and card-footer labeled buttons stay the existing full size. Icon-only row actions stay on the existing icon-control family.

### In-row size lock (approve via Todo)

* **Token:** `in-row` — a size modifier on the labeled family, never a fifth role. Always paired with exactly one role: `btn primary in-row`, `btn secondary in-row`, `btn danger in-row`, and `btn primary in-flight in-row` when that control is already the in-flight primary.
* **Height:** about 60% of the current shared labeled-button height (cut vertical padding; keep the label readable — do not scale the type down to icon-control size).
* **Not a new family:** same green / muted / red / gold roles as today’s labeled buttons. Do not add a parallel class system or a wrapper component.
* **Not icon-control:** if the control has a word label and belongs in a table cell, it stays a labeled button at the in-row size.

## Architectural definition

* **Patterns to reuse** — `pattern.ui.shared-button-roles` (roles, pairing, `App.css`-only styles, no fifth role, presentation only); `pattern.ui.icon-control` (boundary: glyph/initial row actions stay that family, not a size of labeled buttons).
* **New patterns proposed** — catalog amendment to `pattern.ui.shared-button-roles`: optional `in-row` size modifier as locked above. Not a new pattern id and not a third family. Archie Todo on this Description is approval to treat the amendment as catalog law.
* **Applicable statutes** — `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.names-not-ticket-ids`; `astral.standards.no-hardcoded-sets` (size lives in the shared style, not per call site); `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`; `orch.pipeline.call-susan-for-product-decisions` (size lock is here); `orch.roles.archie-approves-statutes` (catalog amendment); plus the active universal git/pipeline set for the epic.

## Boundaries

* Does **not** convert labeled in-row actions to icon-controls, or icon-controls to labeled buttons.
* Does **not** restyle page, toolbar, modal-footer, or card-footer labeled buttons.
* Does **not** restyle AUTO / Debug status-badge toggles, more/less cell chrome, nav, tabs, or other non-button chrome.
* Does **not** change what any control does (handlers, enablement, labels’ meaning) — presentation only.
* Does **not** reopen AST-1166 roles, icon-control remediations, or leftover-family retirement.
* Does **not** touch backend, config business rules, or debug-logging (UI-only; no `debug=` surfaces).

## Acceptance criteria

1. The shared labeled-button catalog documents the `in-row` size modifier (roles unchanged; always paired with a role).
2. A labeled button in a data-table row uses the in-row size and is about 60% the height of a page/toolbar labeled button on the same screen.
3. Scheduled Actions row Run / Stop (including the in-row busy/stop label) use the in-row size and no longer set the row height to the full labeled-button size.
4. Page, toolbar, modal, and card-footer labeled buttons still use the existing full size.
5. Icon-only row actions are still icon-controls.
6. No change in enablement or actions on touched flows (including auto-mode / running gating on Scheduled Actions).

## Dependencies and blockers

none. AST-1166 / AST-1300–AST-1302 are adjacent (roles and icon-controls already exist on integration) — do not reopen them.

## Open questions

none.

## Proposed child tickets

#### 1!: **Codify in-row labeled-button size - Ada**

Amend `pattern.ui.shared-button-roles` with the Todo-locked `in-row` size and land the shared style. Does not switch call sites. **Citations:** `pattern.ui.shared-button-roles`; `pattern.ui.icon-control` (boundary); `astral.standards.dry-and-focused-functions`; `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`; `astral.standards.names-not-ticket-ids`.
**Estimate: 2**

#### 2: **Apply in-row size on table-row labeled buttons - Hedy**

After #1: put the in-row size on every labeled shared-role button that sits in a data-table row (Scheduled Actions Run / Stop included). Does not restyle full-size surfaces or icon-controls. **Citations:** `pattern.ui.shared-button-roles`; `astral.standards.in-scope-only`; `astral.standards.no-hardcoded-sets`.
**Estimate: 2**

**New patterns:** Child #1 introduces the `in-row` size amendment; #2 only consumes it.

**Monolith check:** Functional scope has 3 capabilities; 2 children — catalog/style vs call-site apply.

---

## Original brief

Make the buttons that appear on table rows shorter in height (60% of current height, perhaps) so it does not inflate the row spacing in tables.

### Comments

#### chuckles — 2026-08-11T22:01:07.684Z
AST-1317 REVIEW — merge-child blocked; recalling Ada for missing test() and resolve() on the sub log.

---

_Implementation detail may live in git history on `origin/dev`._
