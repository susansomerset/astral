# AST-1307 — Please set the page title to Astral - <full_name>

<!-- linear-archive: AST-1307 archived 2026-08-19 -->

## Linear archive (AST-1307)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1307/please-set-the-page-title-to-astral-full-name  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan keeps multiple Astral tabs open. Chrome’s tab and window list currently all say “Astral,” so she cannot tell which candidate a tab belongs to. This epic makes the browser tab title carry the selected candidate’s Full Name so the chrome list is scannable.

## Functional scope

* When a candidate is selected, the browser tab title is `Astral - <Full Name>` (space-hyphen-space), using the existing candidate Full Name field — the same value Profile already stores, including the existing first-plus-last join when Full Name is empty. This is not a new name string and not the picker label that appends an id on collisions.
* The title stays in sync when the selected candidate changes, including a persisted selection on reload. When no candidate is selected, or Full Name cannot be formed, the title is `Astral` with no dangling hyphen.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies`. Catalog UI patterns (`pattern.ui.shared-button-roles`, `pattern.ui.icon-control`, `pattern.ui.admin-endpoint`) do not govern document title.
* **New patterns proposed** — none. One-place shell presentation of an already-loaded candidate field; not a reusable catalog shape.
* **Applicable statutes** — `astral.ui.frontend-file-placement` (any helper stays in prescribed frontend locations); `astral.ui.naming-conventions`; `astral.layers.ui-config-driven-business-logic` (do not invent a second name-resolution rule in React — use the Full Name the candidate payload already carries); `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.names-not-ticket-ids`; universal orchestration set (`orch.pipeline.*`, `orch.git.*`, `orch.roles.*`) for the pipeline after approval.

## Boundaries

* Does not append the current route, page heading, or job/company name to the tab title.
* Does not change in-page headings (list page `h1`s, modal titles) or the left-nav candidate picker UX.
* Does not change how Full Name is edited or recomputed on Profile ([AST-1081](https://linear.app/astralcareermatch/issue/AST-1081/contact-shapes-websites-full-name-field-contract-update-candidate-ui) / [AST-1082](https://linear.app/astralcareermatch/issue/AST-1082/candidate-profile-contact-manage-ui-nav-title-patterns-cleanup-update)).
* Does not change exported resume or cover-letter HTML `<title>` values.
* Does not restyle or restructure the nav shell owned by [AST-1284](https://linear.app/astralcareermatch/issue/AST-1284/make-left-nav-responsive).
* Does not change how candidate selection is shared across browser tabs, who may change the selection, or favicon / unauthenticated chrome.
* Must not regress candidate selection, nav destinations, or login handoff.

## Acceptance criteria

1. With a candidate selected whose Full Name is `Jolane Abrams`, the browser tab title is exactly `Astral - Jolane Abrams`.
2. Changing the selected candidate updates the tab title to `Astral - ` plus that candidate’s Full Name without a reload.
3. Reloading a session that already has a persisted selected candidate shows that candidate’s Full Name in the tab title after the app loads.
4. With no candidate selected, or when Full Name cannot be formed, the tab title is exactly `Astral`.
5. Navigating between app pages does not add route or page names to the tab title; the title remains product name plus selected Full Name (or `Astral` alone).
6. Unauthenticated / sign-in chrome still shows `Astral`.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1: **Browser tab title follows selected candidate - Katherine**

Owns setting the SPA browser tab title from the selected candidate’s Full Name and keeping it in sync with selection and reload. Does not own nav layout, picker UX, Profile name editing, or exported document titles.
**Citations:** `no established pattern applies`; `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`; `astral.standards.names-not-ticket-ids`.

---

## Original brief

When I select a candidate in the ui, please update the page title so that when I see tabs in the chrome window list, it says "Astral - Jolane Abrams", etc.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1307 (parent) | ftr/AST-1307-please-set-the-page-title-to-astral-full-name |
| AST-1311 | sub/AST-1307/AST-1311-browser-tab-title-follows-selected-candidate |

**Epic worktree:** `astral-AST-1307/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/8ce53068ebee247d0f8e319148abf0a3/39ef743a-c564-4d0d-aa6d-21ac72d453a5/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/2af2e4b0-8ecc-407e-9d25-8a354546e11f/store.db` |
| Radia | review | `/home/susan/.cursor/chats/8ce53068ebee247d0f8e319148abf0a3/1842c362-f3d6-4e3c-8b68-91f8af260520/store.db` |

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
