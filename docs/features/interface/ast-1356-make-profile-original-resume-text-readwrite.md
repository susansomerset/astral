# AST-1356 — Make profile original resume text read/write

<!-- linear-archive: AST-1356 archived 2026-08-31 -->

## Linear archive (AST-1356)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1356/make-profile-original-resume-text-readwrite  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Candidate Profile currently locks Original Resume Text once a base resume exists. Operators need that field editable again so they can paste fresh source text, save it, and regenerate repeatedly without being blocked by the early lock.

## Functional scope

* On Candidate Profile, Original Resume Text is always editable (read and write), including when a base resume already exists for the selected candidate.
* Edits to Original Resume Text persist and reload through the existing Profile save path the same way other Profile text fields do.
* After a successful save of updated Original Resume Text, the operator can use the existing Artifacts regenerate flow so subsequent generation consumes the fresh text.

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.dirty-leave-save-then-navigate` — Profile leave/save wiring must keep treating Original Resume Text as an ordinary editable field (dirty when changed); do not reintroduce a lock that bypasses draft/save behavior. Adjacent epic [AST-1315](https://linear.app/astralcareermatch/issue/AST-1315/do-not-navigate-away-from-dirty-content) / [AST-1336](https://linear.app/astralcareermatch/issue/AST-1336/candidate-profile-dirty-leave-wiring-do-not-navigate-away-from-dirty).
* **New patterns proposed**
  * none
* **Applicable statutes**
  * `astral.layers.ui-config-driven-business-logic` — remove the ad-hoc React enablement lock on Original Resume Text; do not invent a parallel frontend business rule for locking.
  * `astral.ui.frontend-file-placement` — Profile UI change stays in the frontend layout.
  * `astral.ui.naming-conventions` — naming stays consistent with existing Profile controls.
  * `astral.standards.in-scope-only` — unlock/edit/save Original Resume Text only; no adjacent Profile or Artifacts redesign.
  * `astral.standards.dry-and-focused-functions` — remove lock logic rather than add parallel edit paths.
  * `astral.docs.features-single-file-per-ticket` — one plan doc per child.
  * universal orchestration set (`orch.pipeline.*`, `orch.roles.*`, `orch.git.*`) — standard product epic pipeline applies.

## Boundaries

* Does **not** change Artifacts generate/regenerate UX, chain hops, or craft-resume task behavior beyond consuming whatever Original Resume Text is already saved.
* Does **not** auto-clear, invalidate, or rewrite an existing base resume merely because Original Resume Text was edited — stale base content remains until the operator regenerates via the existing path.
* Does **not** add a new warning dialog, lock toggle, or config flag for resume editability.
* Does **not** change Contact fields, other Profile text tabs, Intake preamble paste, or Admin session resume paste.
* Does **not** alter Profile dirty-leave behavior except that resume edits are editable again and therefore participate normally in dirty/save (must not break [AST-1336](https://linear.app/astralcareermatch/issue/AST-1336/candidate-profile-dirty-leave-wiring-do-not-navigate-away-from-dirty) wiring).
* Must not break ordinary Profile load/save/cancel for other fields.

## Acceptance criteria

1. With a candidate that already has a base resume, Candidate Profile → Original Resume Text is enabled (not disabled) and accepts typed/pasted edits.
2. Saving Profile with a changed Original Resume Text persists that text; reopen/reload Profile shows the same text.
3. Cancel on Profile still restores Original Resume Text to the last loaded/saved value (same as other Profile text fields).
4. After saving fresh Original Resume Text, regenerating via the existing Artifacts base-resume generate/regenerate path uses the updated text (observable in the regenerated result / generation input behavior already product-owned).
5. Candidates without a base resume keep editable Original Resume Text as today (no regression).
6. Profile dirty-leave still prompts on unsaved Original Resume Text edits the same way it does for other Profile text fields.

## Dependencies and blockers

none. Adjacent dirty-leave work ([AST-1315](https://linear.app/astralcareermatch/issue/AST-1315/do-not-navigate-away-from-dirty-content) / [AST-1336](https://linear.app/astralcareermatch/issue/AST-1336/candidate-profile-dirty-leave-wiring-do-not-navigate-away-from-dirty)) is already in User Testing — this epic must not regress it, but does not wait on further changes there.

## Open questions

none.

## Proposed child tickets

#### 1: **Unlock Profile Original Resume Text - Katherine**

Remove the Candidate Profile lock that disables Original Resume Text when a base resume exists (including the lock placeholder copy). Field stays bound to the existing Profile shapes/save path; no Artifacts regenerate redesign; no new warning/config lock. Single vertical slice — UI unlock + persist behavior only.
**Citations:** `pattern.ui.dirty-leave-save-then-navigate`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`; `astral.ui.frontend-file-placement`; `astral.docs.features-single-file-per-ticket`.
**Estimate: 2**

Monolith check: Functional scope has 3 bullets; one child is intentional — unlock, persist, and regenerate-consume are one inseparable Profile edit surface (regenerate path already exists; this epic only restores the editable source field).

---

## Original brief

We disabled it early on, I just want it back so I can regenerate repeatedly with fresh content.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
