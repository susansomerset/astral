# AST-1549 — Fix: error toast X dismisses without copying (Close button on error toast copies error)

<!-- linear-archive: AST-1549 archived 2026-09-09 -->

## Linear archive (AST-1549)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1549/fix-error-toast-x-dismisses-without-copying-close-button-on-error  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1543 — Close button on error toast copies error  
**Blocked by / blocks / related:** parent: AST-1543

### Description

## What this implements

Split dismiss vs click-to-copy on the shared error toast: an explicit dismiss (X) control closes the toast with no clipboard write; clicking the error message or the “Click to copy” hint copies the diagnostic bundle. Stops the leading ✗ status glyph from acting like a close control that copies instead of dismissing.

## Scope

### Component scope

* `src/ui/frontend/src/components/Toast.tsx` — modified: split dismiss vs click-to-copy hit targets; add dismiss control wired to `onDone`.
* `src/ui/frontend/src/App.css` — modified: styles for the dismiss control and narrowed clickable copy affordance (existing `.toast-error-clickable` / hint rules from AST-779).

### Technical scope

* `Toast.tsx` — modified component handlers/render: remove blanket root `onClick` copy for errors; add a dismiss button/handler that stops propagation and dismisses; keep `handleClick` / keyboard copy on the message and/or hint only; optionally change the status icon so it is not an X-shaped close lookalike.
* `App.css` — modified toast CSS: layout/affordance for the new dismiss control and clickable copy region without changing success/info toast chrome.

## Acceptance criteria

- [X] Clicking the dismiss (X) control on an error toast dismisses it and does **not** write diagnostics to the clipboard.
- [X] Clicking the error message text or the “Click to copy” hint copies the diagnostic bundle (same payload path as today).
- [X] Success/info toasts and the existing 15s error auto-dismiss / copy-confirmation behavior stay unchanged.

## Proposed change

- [X] Remove blanket root copy wiring; copy target on message/hint; `icon-control` dismiss; error glyph `\u26A0`.
- [X] Radia fix-now: publish tip reset to ftr + product (`Toast.tsx` / `App.css`) + AST-1549 plan-fix doc only — `sync(dev)` archive waves stripped.

## Boundaries

Does **not** change toast consumers, API error enrichment, or `toastDiagnostics.ts` bundle formatting beyond what Toast.tsx already calls. Does **not** redesign success/info toast chrome. Tests/bible owned by sibling AST-1553 (on ftr).

## Notes for planning

Orphaned mini-parent AST-1543. Closest historical doc: `docs/features/foundation/ast-779-error-toast-duration-click-to-copy-and-diagnostics.md`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### katherine — 2026-08-31T21:22:00.701Z
`origin/sub/AST-1543/AST-1549-fix-error-toast-x-dismisses-without-copying` @ `69f70abc` · §9a ftr clean; origin/dev dry-run conflicts match ftr↔dev lineage (pre-existing)

#### radia — 2026-08-31T21:19:22.232Z
[code-rubric] REVIEW (Commit: a0c94dd9) sync(dev) pollutes publish ref

fix-now: reset tip to ftr + product (`d218b062` / plan-fix doc) only — drop sync(dev) archive waves. Then User Testing.

#### joan — 2026-08-31T20:56:39.661Z
[board-joan] CANON: OK

No statute/pattern gap. Prefer `className="icon-control"` on dismiss (Modal × pattern) over a new `.toast-dismiss` family — make-fix note only.

#### betty — 2026-08-31T20:56:01.513Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md (AST-779 / test_Toast.test.tsx) — missing dismiss-without-copy coverage; existing click-copy + ✗ glyph cases assume root `.toast-error-clickable` / `\u2717` and will break under Proposed change

#### katherine — 2026-08-31T20:54:59.340Z
`origin/sub/AST-1543/AST-1549-fix-error-toast-x-dismisses-without-copying` @ `20087ea90c897737265b7c2a67b2541eb039cb5a` · split dismiss vs copy

---

_Implementation detail may live in git history on `origin/dev`._
