# AST-1543 — Close button on error toast copies error

<!-- linear-archive: AST-1543 archived 2026-09-09 -->

## Linear archive (AST-1543)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1543/close-button-on-error-toast-copies-error  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

When I click on the "X" to dismiss a toast, it copies the error code to clipboard. I want it to copy to clipboard when I do NOT click the X, but click the error message or the Copy link.

When I click on the X, it should dismiss the toast.

## As-is

On an error toast, the shared `Toast` root is fully click-to-copy (AST-779). There is no separate dismiss control. The leading glyph is ✗ (`\u2717`), which reads as an “X” close affordance; clicking it (or anywhere on the toast) copies the diagnostic bundle to the clipboard instead of dismissing.

## To-be

Clicking a dedicated dismiss (X) control dismisses the toast with no clipboard write. Clicking the error message text or the “Click to copy” hint copies the diagnostic bundle (same as today’s copy path). Dismiss and copy are separate actions.

## Proposed steps

1. In `Toast.tsx`, stop treating the whole error toast root as the sole copy hit-target; keep copy on the message text and/or the “Click to copy” hint only.
2. Add an explicit dismiss (X) control that calls `onDone` (after stopping propagation) and does not invoke clipboard copy.
3. Adjust error-toast CSS so dismiss vs copy regions are visually distinct and the ✗ glyph is not mistaken for the only close control (either move dismiss to its own button or change the status icon).
4. Confirm success/info toasts and the existing 15s error auto-dismiss / copy-confirmation behavior stay unchanged.

## Component scope

* `src/ui/frontend/src/components/Toast.tsx` — modified: split dismiss vs click-to-copy hit targets; add dismiss control wired to `onDone`.
* `src/ui/frontend/src/App.css` — modified: styles for the dismiss control and narrowed clickable copy affordance (existing `.toast-error-clickable` / hint rules from AST-779).

## Technical scope

* `Toast.tsx` — modified component handlers/render: remove blanket root `onClick` copy for errors; add a dismiss button/handler that stops propagation and dismisses; keep `handleClick` / keyboard copy on the message and/or hint only; optionally change the status icon so it is not an X-shaped close lookalike.
* `App.css` — modified toast CSS: layout/affordance for the new dismiss control and clickable copy region without changing success/info toast chrome.

## Ancestor candidates

- [ ] AST-779 — Error toast duration, click-to-copy, and diagnostics (`docs/features/foundation/ast-779-error-toast-duration-click-to-copy-and-diagnostics.md`; archived; owns shared `Toast.tsx` click-to-copy)
- [ ] AST-770 — Update error toast (`docs/features/foundation/ast-770-update-error-toast.md`; archived parent epic for the error-toast UX)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
