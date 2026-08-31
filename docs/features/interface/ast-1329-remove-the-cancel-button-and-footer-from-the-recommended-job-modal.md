# AST-1329 — Remove the Cancel button and footer from the Recommended Job Modal

<!-- linear-archive: AST-1329 archived 2026-08-31 -->

## Linear archive (AST-1329)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1329/remove-the-cancel-button-and-footer-from-the-recommended-job-modal  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 1  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Recommended Job Report modal already dismisses via the header close control, but the shared modal footer still shows a Cancel button that covers report content. Remove that redundant footer chrome so operators can read the full report without a duplicate dismiss path.

## Functional scope

* The Recommended Job Report modal no longer shows a bottom footer Cancel (or any empty Save/Cancel footer strip) that covers report content.
* Operators dismiss the Recommended Job Report modal only via the existing header close control.
* Closing the modal this way continues to leave the operator on the Recommended list with no other navigation change.

## Architectural definition

* **Patterns to reuse** — `pattern.ui.icon-control` (header × remains the dismiss control); `pattern.ui.shared-button-roles` (do not invent a parallel dismiss control or restyle Cancel elsewhere to compensate).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.standards.in-scope-only` (Recommended Job Report modal only); `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`; `astral.standards.dry-and-focused-functions`; `astral.standards.names-not-ticket-ids`.

## Boundaries

* Does **not** remove the Artifacts-tab **Cancel** that aborts an in-flight artifact build (`cancel_build`) — that is a workflow action, not modal dismiss chrome.
* Does **not** strip footers from other shared-Modal consumers (company/job detail, intake, rubric, preview, edit/save modals, etc.).
* Does **not** change Save + Cancel footers on dirty edit modals, dirty-discard confirm behavior, or AST-1315 (navigate-away-from-dirty) scope.
* Does **not** change Recommended list entry, Skip, tabs, header actions, or artifact generate/edit/print behavior.

## Acceptance criteria

1. Opening a Recommended job report shows no bottom footer Cancel button.
2. No modal footer strip covers Summary / Analysis / Artifacts content.
3. The header close control still closes the modal and returns the operator to the Recommended list context.
4. While artifacts are generating, the Artifacts-tab Cancel (abort build) remains available beside the in-flight generate control.

## Dependencies and blockers

none.

## Open questions

none.

Monolith check: one inseparable vertical slice — footer removal and ×-only dismiss must ship atomically for UAT.

## Proposed child tickets

#### 1: **Remove Recommended Job Report modal footer - Katherine**

Hide the shared modal footer Cancel/chrome for the Recommended Job Report modal only so content is fully visible; keep header × dismiss and Artifacts in-flight Cancel. Does **not** own other Modal call sites or dirty-discard policy (AST-1315).
**Citations:** `pattern.ui.icon-control`; `pattern.ui.shared-button-roles`; `astral.standards.in-scope-only`.
**Estimate: 1**

---

## Original brief

There's a footer there that has a cancel button, but the window already has a close X option in the upper right, and the footer literally covers screen content.  Just get ride of it.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
