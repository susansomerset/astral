# AST-1284 — Make left nav responsive

<!-- linear-archive: AST-1284 archived 2026-08-19 -->

## Linear archive (AST-1284)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1284/make-left-nav-responsive  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

On smaller viewports the always-on left sidebar steals horizontal space and makes the app hard to use. This epic collapses that chrome into a hamburger-opened panel so page content can use the full width on narrow screens, while keeping the same navigation destinations, candidate selection, and admin footer Susan already relies on.

## Functional scope

* Below **1024px** viewport width, the persistent left sidebar is hidden and a hamburger control opens navigation.
* Opened nav is an **overlay drawer** over page content; **backdrop tap dismisses** the drawer. The drawer also closes after a successful nav destination click so the destination page is usable at full width.
* The drawer carries today's sidebar capabilities: logo, config-resolved nav groups/items with expand/collapse memory, and the admin deploy footer when applicable.
* **Candidate selection in the drawer:** Susan can change the selected candidate from inside the drawer (required). Prefer a candidate submenu/list with a check next to the selected candidate (not a cramped native select), while keeping existing admin vs non-admin selection rules.
* At **1024px and above**, today's always-visible left sidebar (including its current candidate select) is unchanged — no hamburger required for normal desktop use.
* Nav item visibility and enablement remain server-resolved via existing nav config — the shell only changes presentation and open/close chrome, not which links appear.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` for responsive shell / hamburger collapse. Existing `pattern.ui.admin-endpoint` does not apply (no new admin API).
* **New patterns proposed** — `pattern.ui.responsive-nav-shell` — shared NavigationShell collapses the left nav below 1024px into hamburger + overlay drawer (backdrop dismiss); desktop always-visible sidebar remains the wide-viewport default; collapsed mode exposes candidate pick as a checked list/submenu inside the drawer. Flag for Archie approval before implementation treats it as catalog law.
* **Applicable statutes** — `astral.ui.frontend-file-placement` (shell/components/CSS stay in prescribed frontend locations); `astral.ui.naming-conventions` (component/route naming); `astral.layers.ui-config-driven-business-logic` (nav visibility/enablement stays config-resolved in the API — no new business rules in React); `astral.standards.in-scope-only` (shell responsiveness only); universal orchestration set (`orch.pipeline.*`, `orch.git.*`, `orch.roles.*`) for the pipeline after approval.

## Boundaries

* Does not redesign nav group labels, routes, badges, or `NAV_CONFIG` content.
* Does not redesign individual page layouts, tables, or modals for mobile — only the shared left-nav shell.
* Does not change auth rules, who may change candidate, or admin deploy-footer data sources.
* Does not own [AST-1166](https://linear.app/astralcareermatch/issue/AST-1166/button-consistency) (button styling consistency) or Recommended-page work under [AST-1273](https://linear.app/astralcareermatch/issue/AST-1273/job-isnt-loading-on-recommended-page).
* Must not regress desktop sidebar navigation, group expand persistence, or admin-only footer visibility.

## Acceptance criteria

1. Below 1024px width, the persistent left sidebar is not occupying a fixed column; a hamburger control is visible and opens an overlay drawer over content.
2. Backdrop tap dismisses the open drawer without navigating away.
3. The open drawer shows the same nav groups/items Susan sees on desktop for the same candidate (including disabled items as disabled), plus admin deploy footer for admins only.
4. From the open drawer, Susan can select a different candidate via a checked list/submenu; the selected candidate is visually marked; admin/non-admin selection rules match desktop.
5. Choosing an enabled nav destination navigates successfully and leaves the content area usable at full width (drawer closed).
6. At 1024px and above, the left sidebar is always visible as today (including current candidate select); hamburger collapse is not required for normal use.
7. Non-admin sessions still omit the admin deploy footer in both desktop and collapsed modes.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

Monolith note: Functional scope spans several capabilities but one inseparable shell slice (breakpoint + hamburger overlay + drawer contents including checked candidate list + dismiss/nav-close + desktop parity) — shipping them separately would leave UAT half-broken. Single child is intentional.

#### 1: **Responsive left-nav hamburger shell - Katherine**

Owns NavigationShell responsive behavior end-to-end: collapse below 1024px, hamburger + overlay drawer with backdrop dismiss, drawer carrying today's sidebar contents (checked candidate list/submenu, nav groups, admin footer), post-navigate close, and unchanged always-visible sidebar at ≥1024px. Does not own page-level mobile redesigns or nav-config content changes.
**Citations:** proposed `pattern.ui.responsive-nav-shell`; `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`.

---

## Original brief

When on a smaller screen, collapse the menu to a hamburger menu

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1284 (parent) | ftr/ast-1284-make-left-nav-responsive |
| AST-1286 | sub/AST-1284/AST-1286-responsive-left-nav-hamburger-shell |

**Epic worktree:** `astral-AST-1284/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/465a92656b870e11f62ceb31ede48cdf/4675750d-a59b-4ca3-878f-d9f293d36afc/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/6546dee7-e8fc-4e4b-a338-909960c33827/store.db` |
| Radia | review | `/home/susan/.cursor/chats/465a92656b870e11f62ceb31ede48cdf/6e5aa815-9371-4e10-a095-9a403d42b61e/store.db` |

### Comments

#### chuckles — 2026-08-08T19:55:09.006Z
@susan

1. What viewport width should trigger collapse (e.g. `<768px`, `<1024px`, or another cutoff you prefer for your usual windows)?
2. When open, should the menu be an overlay drawer over content (typical hamburger) or push the content aside? Confirm backdrop tap dismisses.
3. Any chrome that must stay visible outside the hamburger on small screens (e.g. always-visible candidate name), or is "everything that is in today's sidebar goes inside the panel" correct?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
