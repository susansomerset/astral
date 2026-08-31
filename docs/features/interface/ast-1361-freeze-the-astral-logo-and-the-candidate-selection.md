# AST-1361 — Freeze the Astral Logo and the candidate selection

<!-- linear-archive: AST-1361 archived 2026-08-31 -->

## Linear archive (AST-1361)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1361/freeze-the-astral-logo-and-the-candidate-selection  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

On wide layouts the left nav scrolls as one pane, so the Astral logo and the selected-candidate control scroll out of view. Operators on long admin navs lose sight of who is selected. This epic pins that chrome so candidate context stays visible while the nav list scrolls.

## Functional scope

* On wide viewports, the Astral logo and the candidate selection control stay fixed at the top of the left nav while the operator scrolls.
* Vertical scroll of the left nav begins at the first navigation group (or loading/error state in that region), not at the logo or candidate control.
* While scrolling a long left-nav list on wide screens, the currently selected candidate remains visible in the pinned candidate control without scrolling back to the top.
* Existing wide vs narrow shell behavior from the responsive left-nav work stays intact: desktop native candidate select, narrow hamburger drawer and candidate menu, breakpoint, and backdrop/close-on-navigate rules are unchanged in product behavior.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` for pinned sidebar chrome (catalog has shared button/icon/dirty-leave UI patterns, not sticky nav chrome). Layout stays inside the existing `NavigationShell` / sidebar CSS surface established by the responsive left-nav epic.
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.ui.frontend-file-placement` (shell and styles stay in prescribed frontend locations); `astral.layers.ui-config-driven-business-logic` (no new React business rules for nav visibility/enablement — `NAV_CONFIG` / `/api/nav_config` resolution unchanged); `astral.standards.in-scope-only` (chrome pin only; no adjacent admin/page work); `astral.standards.dry-and-focused-functions` (prefer a small shell/CSS structure over duplicated sticky logic); `astral.ui.naming-conventions` (any new class names follow UI naming).

## Boundaries

* Does not change candidate selection semantics (admin lock, who may switch, candidate list source).
* Does not change `NAV_CONFIG`, `/api/nav_config`, route map, or which groups/items appear.
* Does not redesign the logo asset, candidate control UX (native select vs narrow menu), hamburger drawer, or breakpoint.
* Does not pin or redesign the admin deploy footer (tempting adjacent sticky-footer work — out of scope unless Susan expands).
* Does not change page content layout, table freeze columns, or browser tab title behavior.
* Must not regress the AST-1284 / AST-1286 responsive left-nav shell on narrow or wide viewports.

## Acceptance criteria

1. On a wide viewport (≥1024px) with enough left-nav content to scroll, scrolling the left nav leaves the Astral logo fully visible at the top of the sidebar.
2. Under the same conditions, the candidate selection control stays fully visible directly under the logo; the selected candidate label/value remains readable without scrolling to the top.
3. Under the same conditions, the first scrollable nav content is the first nav group (or the loading/error message that replaces groups), not the logo or candidate control.
4. On a narrow viewport, hamburger open/close, backdrop dismiss, close-on-navigate, and candidate menu behavior still match today’s responsive shell (no regression).
5. Non-admin candidate lock and admin candidate switching still behave as today.

## Dependencies and blockers

none. Sibling interface work in flight (dirty-leave, profile resume text, analysis header chrome) does not block this chrome-only epic.

## Open questions

none

## Proposed child tickets

#### 1: **Pin left-nav logo and candidate chrome - Katherine**

Restructure the wide left-nav so logo + candidate selection stay pinned while nav groups (and footer content below them) scroll in a dedicated region. Preserve the existing responsive shell: wide native select, narrow drawer/menu, and AST-1286 open/close rules. Does not own nav config, candidate context APIs, or footer redesign.
**Citations:** `astral.ui.frontend-file-placement`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.ui.naming-conventions`
**Estimate: 2**

Monolith check: four functional capabilities, one child — intentional single vertical slice (shell structure + CSS must ship together for UAT on wide scroll).

---

## Original brief

in the left nav on wide screens, allow the scroll to start from the first nav element, not from the top of the pane.  It's easy to forget who is the selected candidate from the admin pages.

### Comments

#### chuckles — 2026-08-14T19:46:49.367Z
AST-1369 REVIEW — Radia discuss: scroll-pinning UAT smoke (no fix-now).

#### chuckles — 2026-08-14T18:35:48.380Z
[thread-missing] Cursor chat `8830e246-0f66-4bef-bedb-fedac1d0e890` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/8830e246-0f66-4bef-bedb-fedac1d0e890/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `70aa7f91-4df0-4498-8c6b-14f1c7011482`.

Watcher rule `define` on `AST-1361` (Thread owner `AST-1361`).

#### chuckles — 2026-08-14T18:29:24.054Z
[thread-missing] Cursor chat `5105ff5e-391d-497e-acae-618dbe37efa3` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/5105ff5e-391d-497e-acae-618dbe37efa3/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `241c7951-c38d-408a-ba5c-0e8a2aa8df2d`.

Watcher rule `define` on `AST-1361` (Thread owner `AST-1361`).

#### chuckles — 2026-08-14T18:19:01.311Z
[thread-missing] Cursor chat `66b749e1-88f1-4b63-8dd7-0ec02e9e2a02` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/66b749e1-88f1-4b63-8dd7-0ec02e9e2a02/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `cdbfbcf5-bb80-4ab0-808f-8cd7526ebf49`.

Watcher rule `define` on `AST-1361` (Thread owner `AST-1361`).

#### chuckles — 2026-08-14T18:08:39.612Z
[thread-missing] Cursor chat `c5ae76bc-197d-4f09-b7c5-503905eba067` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/c5ae76bc-197d-4f09-b7c5-503905eba067/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `19545767-474d-4e67-87c1-4f397a997ed0`.

Watcher rule `define` on `AST-1361` (Thread owner `AST-1361`).

---

_Implementation detail may live in git history on `origin/dev`._
