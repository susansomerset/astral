# AST-563 — take_jd in analysis_upshot schema and Estelle prompt (Recommended Job Modal)

<!-- linear-archive: AST-563 archived 2026-06-23 -->

## Linear archive (AST-563)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-563/take-jd-in-analysis-upshot-schema-and-estelle-prompt-recommended-job  
**Status at archive:** Canceled  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-499 — Recommended Job Modal  
**Blocked by / blocks / related:** parent: AST-499; related: AST-313

### Description

## What this implements

Extend the `analysis_upshot` consult contract so the JD phase has Estelle's per-phase thoughts in the same shape as DO/GET/LIKE: add `take_jd` to the JSON schema, update the Estelle prompt, and persist via the existing analysis_upshot dispatch and `job_data` path ([AST-480](https://linear.app/astralcareermatch/issue/AST-480) area). No React or report UI in this ticket.

## Acceptance criteria

10. `take_jd` is persisted by analysis_upshot task and rendered on the JD tab.

(Data contract from parent: Add `take_jd` to `analysis_upshot` schema and Estelle prompt so JD phase has the same "thoughts above vectors" shape as DO/GET/LIKE. Report UX is the contract; do not invent fields only in React.)

## Boundaries

* Does **not** build the Recommended Job Report modal (sibling Katherine).
* Does **not** implement **Generate Artifacts** / **Cancel** API or UI (sibling Hedy).
* Does **not** change consult scoring, dispatch batching, or graders beyond schema/prompt/persist for `take_jd`.

## Notes for planning

* Align with [AST-313](https://linear.app/astralcareermatch/issue/AST-313) artifact pipeline prompt patterns.
* Katherine's report consumes `take_jd` on the JD tab after this lands.

## Git branch (authoritative)

Per **orientation-astral** branch law: parent `ftr/AST-499-recommended-job-modal`, child `sub/AST-499/<ticket-id>-take-jd-analysis-upshot-schema-estelle-prompt`. Created at dispatch-linear.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
