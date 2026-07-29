# AST-886 — Allow "Expand One/Expand All" for sectioned list components

<!-- linear-archive: AST-886 archived 2026-07-29 -->

## Linear archive (AST-886)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-886/allow-expand-oneexpand-all-for-sectioned-list-components  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-858

### Description

## Purpose

Sectioned list screens today mostly behave as accordions: opening one section closes another. That is right as the default for dense catalogs, but wrong when a user needs several sections open at once. This feature makes expansion policy an optional choice of the TypeScript page that renders the sectioned list — **Expand One** by default (current accordion behavior, no forced refactor of existing screens) vs **Expand All** when the page opts in — including bulk expand/collapse controls and independent multi-section expand.

## Functional scope

1. **Optional Expand All on sectioned lists.** Shared sectioned-list UI supports an optional page-set expansion policy when rendering the list:
   * **Expand One (default)** — opening a section closes any other open section; zero expanded remains valid. All existing sectioned-list screens stay on this default so current accordion logic does not need a refactor pass.
   * **Expand All (opt-in)** — the hosting page turns this on via the list’s optional expand-all setting; multiple sections may stay open at once.
2. **Page owns the setting.** The TypeScript page that uses the component declares Expand All when it wants it; omission means Expand One.
3. **Expand All chrome and free multi-toggle.** When Expand All is on, the user gets visible **Expand all** and **Collapse all** controls, and may still expand or collapse individual sections so one or more sections are open without requiring every section to be expanded.
4. **Per-section expand/collapse still works.** Under Expand One, sibling sections follow accordion rules. Under Expand All, collapsing one section does not force-close others.
5. **Zero expanded remains valid.** Under both policies, every section can be left collapsed (established Manage Tasks / CollapsiblePanel expectation).

## Boundaries

* Does **not** force existing screens off Expand One — default stays Expand One everywhere unless a page opts into Expand All.
* Does **not** invent new list data, filters, sort rules, or API contracts — expansion policy and expand/collapse chrome only.
* Does **not** redesign section chrome beyond Expand all / Collapse all controls for Expand All mode, table layout, sticky columns, or admin filter bars.
* Does **not** add a global user preference or persisted “last expanded sections” store — policy is page-declared for this epic.
* Does **not** change Recommended Jobs list sectioning/scoring (sections stay always-visible as today), Recommended Job Modal (AST-858), or scheduled-actions filter work (AST-885) beyond any shared expand primitive those screens happen to reuse.
* Must not change Expand One accordion behavior on screens that remain on the default (Manage Tasks list, Scheduled Actions, In Review, Skipped, and any other current accordion consumers).
* Frontend-only concern — no backend debug-logging requirements.

## Acceptance criteria

1. With the default (Expand One / expand-all unset): at most one section is open at a time; expanding a second section closes the first; collapsing the open section leaves zero expanded — matching current accordion behavior on existing screens that are not opted in.
2. With Expand All opted in by the page: two or more sections can be open at the same time; collapsing one does not force-close the others.
3. With Expand All opted in: visible **Expand all** opens every section; visible **Collapse all** closes every section.
4. With Expand All opted in: the user can expand or collapse individual sections so that one or more (but not necessarily all) sections are open, without using Expand all.
5. Under both policies, every section can be collapsed so that zero sections are expanded.
6. Existing sectioned-list screens that do not opt in continue to behave as Expand One with no accidental multi-open and no required refactor of their prior expand logic beyond wiring the shared default.

## Dependencies and blockers

none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-886 (parent) | ftr/AST-886-expand-one-expand-all-sectioned-lists |
| AST-893 | sub/AST-886/AST-893-expand-policy-sectioned-lists |

**Epic worktree:** `astral-AST-886/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | ef700803-314d-4b4e-8a75-2841525295a0 |
| Betty | qa | af2ca0e1-58bc-4d1c-b84c-ea6732ed25ad |
| Radia | review | dd2382bb-6d13-48cd-a489-30dd8b84aad9 |

---

## Original brief

To be set by the ts page using the component.

### Comments

#### chuckles — 2026-07-13T21:25:15.712Z
[merge-child] blocked: AST-893 sub-log missing `plan(AST-893):` (got `docs(AST-893): plan —`).

@Katherine Johnson — fixing on publish ref; Chuckles will re-run merge-child after.

— Chuckles

#### chuckles — 2026-07-13T18:26:43.129Z
@susan

1. Which screens should ship on **Expand All** vs stay on **Expand One** in this epic? (In Review, Skipped, Manage Tasks list, Scheduled Actions — and leave Recommended alone unless you say otherwise.)
2. For any screen moved to **Expand All**, do you also want bulk **Expand all** / **Collapse all** controls, or only independent per-section toggles?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
