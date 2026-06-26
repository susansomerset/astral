# AST-564 — Generate Artifacts and Cancel job transitions API (Recommended Job Modal)

<!-- linear-archive: AST-564 archived 2026-06-23 -->

## Linear archive (AST-564)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-564/generate-artifacts-and-cancel-job-transitions-api-recommended-job  
**Status at archive:** Canceled  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-499 — Recommended Job Modal  
**Blocked by / blocks / related:** parent: AST-499; related: AST-313

### Description

## What this implements

Candidate-facing transitions for the Recommended Job Report: **Generate Artifacts** moves `RECOMMENDED` → `BUILD_ARTIFACTS` only via explicit UI action (never dispatch-driven); **Cancel** during build returns `BUILD_ARTIFACTS` → `RECOMMENDED` and clears partial `job_data.artifacts` (and related in-flight artifact state per parent open question). Actions are config/manifest-driven, not hardcoded TS state machines. May add `candidate_action` values or a dedicated endpoint — dev plan picks API shape (parent: agreed, not dispatch side effects).

## Acceptance criteria

5. **Generate Artifacts** on `RECOMMENDED` moves job to `BUILD_ARTIFACTS` only via that button; UI reflects in-progress; **Cancel** returns to `RECOMMENDED`.

(Parent boundary: Does **not** auto-enter `BUILD_ARTIFACTS` except via **Generate Artifacts** UI.)

## Boundaries

* Does **not** build the tabbed report shell, tabs, header, or list row entry (sibling Katherine).
* Does **not** add `take_jd` schema/prompt (sibling Ada — parallel OK).
* Does **not** reimplement artifact pipeline authoring ([AST-313](https://linear.app/astralcareermatch/issue/AST-313)).

## Notes for planning

* Cancel clears partial artifacts — Susan confirmed in parent Open questions.
* Katherine wires buttons into the report modal after this ticket's contract exists.

## Git branch (authoritative)

Per **orientation-astral** branch law: parent `ftr/AST-499-recommended-job-modal`, child `sub/AST-499/<ticket-id>-generate-artifacts-cancel-job-transitions-api`. Created at dispatch-linear.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
