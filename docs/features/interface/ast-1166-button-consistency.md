# AST-1166 — Button consistency

<!-- linear-archive: AST-1166 archived 2026-08-19 -->

## Linear archive (AST-1166)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1166/button-consistency  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators currently meet several different button looks and interaction habits across the UI — list-page actions, modal footers, detail/edit saves, Manage Email toolbar controls, exports, and ad-hoc one-offs among them. That inconsistency makes the product feel unfinished and forces Susan to re-learn which control is primary, cancel, or destructive on each screen. This epic locks an intentional button-class catalog in Discussion, codifies it as patterns, then brings every frontend UI file into compliance (pattern first, then code).

## Functional scope

1. **Discussion-locked button class catalog** — The intentional labeled-button classes and the separate icon-control family are decided here (see **Button class catalog** below) so development is not blocked waiting on Archie mid-build.
2. **Codify as patterns** — Land the catalog in the pattern corpus before call-site rewrites; implementation follows the approved pattern ids.
3. **Full frontend evaluation** — For every UI page/component that renders a clickable control, classify it into a catalog class or an explicit exception (nav links, tabs, and similar non-button chrome stay out of the button catalog).
4. **Remediate labeled buttons** — Replace one-off / bare / divergent labeled buttons (including Manage Email toolbar, list bulk/toolbar, export, duplicate `dep-btn` vs `modal-btn` families, inline style color overrides on actions) with the catalog classes.
5. **List row actions → icons** — Row actions on lists use the icon-control family only (not labeled text buttons). Includes fixing controls that currently render poorly as tiny text (e.g. list Skip as "Sk").
6. **Exception register** — Document any intentional leftover exceptions Archie accepts; unexplained third families are not allowed on in-scope surfaces.

### Button class catalog (Discussion lock — approve via Todo)

**Labeled action buttons** (text labels; shared size/weight/hover/disabled habits within each class):

| Class | Role | Use for | Visual baseline (intentional) |
| -- | -- | -- | -- |
| `btn primary` | Affirmative / commit | Save, Continue, Land Meteorite, Run, Generate (idle), Add, Export, Retry, Select all (when framed as a page action) | Green primary (today’s `modal-btn save` / `dep-btn save`) |
| `btn secondary` | Cancel / neutral alternate | Cancel, Clear selection, Start over, non-destructive dismiss, Preview when not the commit | Muted elevated + border (today’s `*.cancel`) |
| `btn danger` | Destructive | Delete / kill / destructive confirm | Red (today’s `*.danger`) |
| `btn primary` + `in-flight` | Busy primary | Same control while a slow action runs | Gold busy (today’s `.save.in-flight`) |

**Retired as separate looks** (must map into the table above): `list-page-bulk-btn`, `timesheet-export-btn`, bare `manage-email-toolbar button`, parallel `dep-btn` vs `modal-btn` duplicate families, one-off inline background overrides on action buttons, `entity-skip-btn` when it is a labeled action (use `btn secondary` or `btn danger` by product meaning), `sql-hist-btn` / `dispatch-log-copy-btn` and peers unless listed as exceptions.

**Icon controls** (not labeled buttons — separate family):

| Class | Role | Use for |
| -- | -- | -- |
| `icon-control` | Compact glyph/initial action | List row actions (Skip, Edit, View, Resurrect, pipeline state moves), modal × dismiss, chevron expand/collapse |

**Recommendation (in scope):** Prefer **icons only** on list row action columns; do not use labeled buttons in that column. Modal labeled Skip ("Skip This Job") stays a labeled `btn` of the appropriate class, not an icon-control.

**Not in either catalog:** nav links, side-tab / section chrome, rubric text links, checkbox/radio inputs.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` today for shared button/icon-control roles (UI catalog has `pattern.ui.admin-endpoint` only). Reuse existing themed confirm / modal shell placement; do not invent a second confirm system.
* **New patterns proposed** — (1) `pattern.ui.shared-button-roles` — labeled `btn primary` / `btn secondary` / `btn danger` / `in-flight` contract above; (2) `pattern.ui.icon-control` — icon-only compact actions (lists, dismiss, chevrons), explicitly not labeled buttons. Archie approval of this Description (Todo) is approval to treat these as catalog law for the epic.
* **Applicable statutes** — `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.names-not-ticket-ids`; `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`; `orch.pipeline.call-susan-for-product-decisions` (catalog locked here so implementers are not blocked mid-flight); universal git/pipeline set for the epic.

## Boundaries

* Does **not** redesign page layouts, tables, modal shells, tabs, toasts, or navigation chrome beyond control classification.
* Does **not** change what each control does (API calls, enablement rules, product labels’ meaning) except presentation and list-row icon treatment.
* Does **not** reopen Manage Email meteorite/land semantics — presentation only.
* Does **not** require a full product theme redesign beyond the locked classes.
* Does **not** touch backend, config business rules, or debug-logging contracts (UI-only).
* Does **not** leave pattern approval as a mid-implementation Archie gate — classes are decided in this Description; Todo = approve catalog + children.

## Acceptance criteria

1. Canon (or epic-landed pattern docs per team process) contains `pattern.ui.shared-button-roles` and `pattern.ui.icon-control` matching the Discussion catalog before broad call-site remediation merges.
2. An inventory (plan or Code Complete note) maps every labeled `<button>` (and button-styled action) in `src/ui/frontend` to a catalog class or a named exception.
3. Manage Email toolbar actions, list bulk/toolbar actions, modal footers, detail/edit save bars, and export actions all use the shared labeled classes — no bare/browser-default toolbar buttons beside themed controls.
4. Duplicate parallel families (`dep-btn` vs `modal-btn`, gold bulk vs green save as separate systems) are gone; one class system remains.
5. List row action columns use icon-controls only; Skip/Edit/View-style actions are not cramped labeled text buttons.
6. In-flight primaries share one gold busy treatment wherever busy already exists.
7. No regression in enablement or actions on touched flows (e.g. Land Meteorite still gated correctly).

## Dependencies and blockers

none.

## Open questions

none — Susan’s answers folded in; class catalog locked above for Todo approval.

## Proposed child tickets

#### 1!: **Codify button + icon-control patterns - Ada**

Land `pattern.ui.shared-button-roles` and `pattern.ui.icon-control` from the Discussion catalog (shared styles/contract implementers will consume). Does not finish the full call-site sweep. **Citations:** proposed `pattern.ui.shared-button-roles`; proposed `pattern.ui.icon-control`; `astral.standards.dry-and-focused-functions`; `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`.

#### 2: **Full frontend audit + labeled-button remediation - Hedy**

After #1: evaluate each UI file against the patterns; map every labeled action; remediate anomalies onto `btn primary` / `secondary` / `danger` / `in-flight`. Does not own list icon-control remediation (#3). **Citations:** `pattern.ui.shared-button-roles`; `astral.standards.in-scope-only`.

#### 3: **List icon-control remediation - Katherine**

After #1 (parallel with #2 once patterns exist): bring list row actions (and peer icon-only controls in scope) onto `pattern.ui.icon-control`; fix poor labeled mini-text row actions (e.g. Skip). **Citations:** `pattern.ui.icon-control`; `astral.standards.in-scope-only`.

**New patterns:** Child #1 introduces both pattern ids; #2 and #3 only consume them.

**Monolith check:** Functional scope has 6 capabilities; 3 children — pattern codify vs labeled sweep vs icon-control sweep.

---

## Original brief

There are apparently several kinds of buttons in our system, such as the ones on the list pages, the modals, but also on the manage_email tab.

They seem to all have different behaviors and styles, and I want them to be consistent.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1166 (parent) | ftr/AST-1166-button-consistency |
| AST-1300 | sub/AST-1166/AST-1300-codify-button-icon-control-patterns |
| AST-1301 | sub/AST-1166/AST-1301-full-frontend-audit-labeled-button-remediation |
| AST-1302 | sub/AST-1166/AST-1302-list-icon-control-remediation |

**Epic worktree:** `astral-AST-1166/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/5de09e19196a2cc63930b9c78d59ee10/047ed3fa-21c6-4ccb-a939-0311f8930c04/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/5de09e19196a2cc63930b9c78d59ee10/82a5958d-5a61-4600-a612-0eb2824f341a/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/5de09e19196a2cc63930b9c78d59ee10/34ee266f-71aa-4005-b857-f1b6017ed7ae/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/07778aae-20ce-4fad-af0d-d13a4dd2e003/store.db` |
| Radia | review | `/home/susan/.cursor/chats/5de09e19196a2cc63930b9c78d59ee10/75604e2a-e20a-4622-8c9f-a1c2ddf10c4f/store.db` |

### Comments

#### chuckles — 2026-08-05T16:28:44.528Z
@susan

**§6a — dispatch produced no children**

- Parent Description already has Architectural definition, Proposed child tickets (3 `####` blocks with Citations), and cleared Open questions — nothing to backfill from comments/Citations.
- Dispatch still created **0** children; prior pass stopped because assignee was Joan Clarke, not Chuckles.
- Children cannot be recovered from comments or legacy Citations — needs a clean re-dispatch after you assign Chuckles and return this to Todo.

— Chuckles

#### chuckles — 2026-08-05T16:27:04.333Z
@susan dispatch was requested but AST-1166 is assigned to Joan Clarke, not Chuckles. Assign Chuckles when the definition is ready for dispatch (or use define-parent if definition work is still in flight). Stopping without creating children.

— Chuckles

#### susan — 2026-08-05T05:31:19.184Z
Questions are answered, but we should determine the button classes needed while we are in the Discussion stage, so that there isn't Archie-related interaction to unblock development.  Also, we would start with codifying the button classes as patterns, then evaluate each ui file against the new pattern and address anomalies.  Pattern first, then code correction to adhere to the pattern.

#### chuckles — 2026-08-05T05:17:25.685Z
@susan

1. Canonical look for labeled action buttons: modal/detail family (green primary / muted cancel / gold busy / red danger), gold list-page bulk, or a blend you specify?
2. Scope: list pages + modals + Manage Email only, or full sweep of other divergent action buttons (export, etc.) in this parent?
3. Icon-only controls (modal ×, etc.): force onto the same role system, or leave as exceptions?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
