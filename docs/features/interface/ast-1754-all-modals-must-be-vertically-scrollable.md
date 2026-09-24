# AST-1754 — All modals must be vertically scrollable

<!-- linear-archive: AST-1754 archived 2026-09-24 -->

## Linear archive (AST-1754)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1754/all-modals-must-be-vertically-scrollable  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

We keep implementing modals that are not vertically scrollable.

## As-is

New and existing admin modals keep shipping without vertical scroll. Tall content is clipped inside the dialog (especially `size="wide"`), so operators can only see the first viewport of body content. Default `.modal-body` already scrolls, but `.modal-card--wide .modal-body` sets `overflow: hidden` so nested panels can own scroll — callers that put tall content directly in the body (no inner scroll wrapper) hit the same clip that AST-1511 fixed only for Show Differences.

## To-be

Every shared `Modal` is vertically scrollable by default: when body content exceeds the card height, the operator can scroll to the rest while the header (and footer, when present) stay put. Nested layouts that intentionally own their own scroll (e.g. SideTabPanel) must keep working — the fix is a shared shell contract, not one more per-screen wrapper.

## Proposed steps

1. Treat scrollability as a shared `Modal` / `App.css` contract, not a per-call-site wrapper (AST-1511’s local div fixed one screen; the same failure mode keeps recurring).
2. Adjust `.modal-card--wide .modal-body` (and any related shell rules) so tall direct children scroll, without breaking SideTabPanel / other inner scroll owners that rely on the wide body filling height.
3. If CSS alone is unsafe, add a small shell change in `Modal.tsx` (e.g. size-aware body class or default scroll region) so new modals inherit scroll without inventing another inline wrapper.
4. Spot-check a few known wide modals (Show Differences, Read email / HTML source, Recommended report / SideTabPanel) so one class of layout does not regress the other.
5. Leave individual feature screens alone unless a call site is fighting the new shell contract.

## Component scope

* `src/ui/frontend/src/components/Modal.tsx` — modified: shared modal shell is where “all modals scroll” has to land if CSS alone cannot cover wide + nested-scroll layouts.
* `src/ui/frontend/src/App.css` — modified: `.modal-body` / `.modal-card--wide .modal-body` (and related wide-modal rules) are the rules that currently clip tall content or force per-screen wrappers.

## Technical scope

* `Modal.tsx` — modified component markup/props only as needed so the shell exposes a reliable vertical scroll region (or a size-aware body class) for tall children; exact naming is plan-fix’s call.
* `App.css` — modified CSS rules for default and wide modal body overflow/flex so content scrolls when the shell owns scroll, while layouts that nest their own scroll region still fill height correctly.

## Ancestor candidates

- [X] AST-1511 — Show Differences modal does not scroll (archived; same clip on wide Modal; fixed with a local wrapper and explicitly avoided changing global wide-modal CSS)
- [ ] AST-1506 — Show Differences / Update file divergence banner (introduced the wide Show Differences Modal that hit the overflow:hidden trap)
- [ ] AST-1455 — Add Show Differences and Update file with table version (parent epic for AST-1506 / AST-1511)
- [ ] AST-1040 — UAT Read email modal raw HTML (wide-modal inner-scroll pattern via `.email-html-source`)
- [ ] AST-1033 — Read email admin screen (wide Modal + `.modal-card--wide .modal-body { overflow: hidden }` for nested scroll)
- [ ] AST-1413 — Ad hoc Preview Prompt scrollable modal (explicit scrollable-modal AC on shared Modal)
- [ ] AST-948 — Modal shell / horizontal tabs sticky header (modal shell redesign; weaker fit for scroll contract)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
