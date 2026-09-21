# AST-1315 — Do not navigate away from dirty content

<!-- linear-archive: AST-1315 archived 2026-08-31 -->

## Linear archive (AST-1315)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1315/do-not-navigate-away-from-dirty-content  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators lose in-progress Candidate Profile edits when they leave the page for another in-app destination. This epic makes dirty Profile content safe to leave: the product asks to save first (affirmative default), persists on yes, then completes the navigation so written text is not silently discarded.

## Functional scope

* Treat Candidate Profile as dirty when the on-screen values differ from the last successfully loaded or saved snapshot for the selected candidate.
* When Profile is dirty, intercept in-app navigation away from Profile (left nav and other in-app route changes). Do not silently drop the draft.
* On intercepted leave: show the themed confirm asking to save. Affirmative / primary action is Save (default). On Save: persist via the existing Profile save path, then complete the pending navigation. On cancel/decline of that prompt: stay on Profile (abort the leave; draft remains).
* If the save attempt fails, stay on Profile, surface the failure the same way a normal Save failure does, and do not complete the pending navigation.
* Switching among Profile’s own in-page text tabs while staying on Profile must keep draft values (no false “leave” prompt for those tabs alone).
* Scope is Candidate Profile only for this epic (not other Save pages).

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.shared-button-roles` — Save is `btn primary`; cancel/stay is `btn secondary`.
* **New patterns proposed**
  * `pattern.ui.dirty-leave-save-then-navigate` — when a page has unsaved edits and the operator tries to leave via in-app navigation, prompt with save-as-default; on affirm: save then continue navigation; on cancel: stay with draft intact; on save failure: stay and show error. Distinct from Modal’s discard-on-close confirm and from ArtifactEditor-style autosave/beforeunload. Flag for Archie approval before implementation depends on cataloging it.
* **Applicable statutes**
  * `astral.ui.frontend-file-placement` — UI work stays under the frontend layout.
  * `astral.ui.naming-conventions` — shared hook/component names match existing conventions.
  * `astral.layers.ui-config-driven-business-logic` — Profile continues to render from shapes; this epic does not hardcode field lists.
  * `astral.standards.in-scope-only` — Candidate Profile dirty-leave only.
  * `astral.standards.dry-and-focused-functions` — shared leave/save helper reused rather than one-off page glue.
  * `astral.docs.features-single-file-per-ticket` — one plan doc per child.

## Boundaries

* Does **not** change Modal close/discard confirm semantics (unsaved modal close stays discard-oriented).
* Does **not** add ArtifactEditor-style autosave or debounce save for Profile.
* Does **not** change Profile field contracts, shapes, or save API semantics beyond invoking the existing save path from the leave prompt.
* Does **not** cover admin edit screens, Artifacts editors, or other Save pages (Profile only).
* Does **not** require a custom themed dialog for hard browser tab close/refresh (`beforeunload`); that remains browser-native if addressed later — this epic is in-app navigation.
* Must not break clean (non-dirty) Profile navigation or ordinary header Save / Cancel.
* Cancel on the leave prompt does **not** discard the draft and does **not** complete navigation.

## Acceptance criteria

1. With unsaved Profile edits, choosing another left-nav / in-app destination shows a themed save prompt (not a silent wipe); primary action is Save.
2. Choosing Save on that prompt persists the draft (reload Profile shows the same values) and then lands on the destination that was requested.
3. Choosing Cancel on that prompt leaves the operator on Profile with the draft intact (no navigation, no silent discard).
4. If that save fails, the operator remains on Profile with a visible error and is not taken to the other destination.
5. With no unsaved changes, leaving Profile does not show the save prompt.
6. Switching only among Profile’s in-page text tabs does not by itself show the leave/save prompt, and draft text across those tabs remains intact until a real leave or header Cancel.
7. Existing header Save and Cancel on Profile still work as today when the operator is not mid-navigation.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1!: **Dirty-leave save-then-navigate helper - Ada**

Shared in-app dirty-leave affordance: detect dirty, block pending navigation, themed confirm with Save as primary/default, on affirm run caller-provided save then continue, on cancel stay with draft intact, on save failure stay and surface error. Introduces proposed `pattern.ui.dirty-leave-save-then-navigate` (subject to Archie approval). Does **not** wire Profile itself (#2).
**Citations:** `pattern.ui.shared-button-roles`; proposed `pattern.ui.dirty-leave-save-then-navigate`; `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`; `astral.standards.dry-and-focused-functions`.
**Estimate: 3**

#### 2: **Candidate Profile dirty-leave wiring - Katherine**

After #1: Candidate Profile tracks dirty vs last loaded/saved snapshot, uses the shared helper on in-app leave, reuses the existing Profile save path, keeps Cancel/Save header behavior, and does not treat in-page text-tab switches as leave. Profile only — no other pages.
**Citations:** proposed `pattern.ui.dirty-leave-save-then-navigate`; `pattern.ui.shared-button-roles`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`; `astral.docs.features-single-file-per-ticket`.
**Estimate: 2**

---

## Original brief

When I am editing a profile and I navigate to another tab, the text I am writing is lost.  Prompt me to save, default to yes, then save and navigate away.

### Comments

#### susan — 2026-08-12T17:53:24.871Z
\[bug\]

Dirty flag does not reset if the users uses Undo, or restores the screen to its virgin state.  It should.

#### chuckles — 2026-08-12T12:55:51.811Z
@susan
1. Scope: Candidate Profile only for this epic, or should the same dirty-leave / save-then-navigate behavior apply to every candidate (or admin) page that already has a manual Save and can lose drafts on nav?
2. When the operator declines the save prompt: stay on Profile (discard the leave), or leave without saving?

#### chuckles — 2026-08-12T12:50:07.346Z
@susan Dispatch blocked — definition incomplete for AST-1315:

- Missing `## Architectural definition` (pattern ids or explicit new-pattern / no-established-pattern flag)
- Missing `## Proposed child tickets` with `####` blocks (assignees, bangs, Citations, In scope)
- Description is still only the original brief (dirty-nav save prompt) — needs `define-parent` before Todo + Chuckles again

No children, no recoverable text in comments/legacy Citations. Please run define (or paste an approved definition), then Todo + assign Chuckles when ready to dispatch.

---

_Implementation detail may live in git history on `origin/dev`._
