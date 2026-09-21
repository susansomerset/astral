# AST-1415 — Candidate state validation bug

<!-- linear-archive: AST-1415 archived 2026-09-09 -->

## Linear archive (AST-1415)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1415/candidate-state-validation-bug  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

`run_requested_artifacts_dispatch` for candidate `somerset` fails with `Invalid candidate state 'REQUESTED_ARTIFACTS.craft_get_rubric'. Must be one of: [bare CANDIDATE_STATES keys]`. After the first craft hop, something tries to persist that compound hop label as `candidate.state`; a registry-membership check rejects it (the label is not a `CANDIDATE_STATES` key), the worker logs the error, and the artifacts daisy chain stops.

## To-be

Compound hop labels of the form `REQUESTED_ARTIFACTS.<completed_task_key>` (e.g. `REQUESTED_ARTIFACTS.craft_get_rubric`) are accepted as runtime candidate states on the artifacts dispatch path — same shape as job `BUILD_ARTIFACTS` hop labels, and **not** registry keys. Writes succeed; later hops and terminal `ARTIFACTS_READY` / retry / error can follow. `somerset` (and any candidate on this path) continues the craft chain without this `ValueError`.

## Proposed steps

1. Trace who writes `'REQUESTED_ARTIFACTS.craft_get_rubric'` into `candidate.state` during `run_requested_artifacts_dispatch` (likely AST-1388's hop-label path) and which helper still requires `state in CANDIDATE_STATES` (`save_candidate` / `transition_candidate_state` membership, not the `Invalid candidate state transition` gate).
2. Restore the AST-1388 carve-out: hop-label writes bypass registry membership; `_candidate_state_allowed` treats a parsed `REQUESTED_ARTIFACTS.<hop>` as the trigger for prior-state; claim / in-flight hide still recognize hop labels.
3. Confirm a following hop or `ARTIFACTS_READY` can legally follow the compound label.
4. Re-run `REQUESTED_ARTIFACTS` dispatch on `somerset` (or equivalent) and confirm the error is gone.

---

## Original report

[2026-08-17 05:05:26] ERROR src.core.candidate: run_requested_artifacts_dispatch failed candidate_id=somerset error=Invalid candidate state 'REQUESTED_ARTIFACTS.craft_get_rubric'. Must be one of: ['PROSPECT', 'NEW_CANDIDATE', 'INTAKE_INITIATED', 'REQUIRED_TOPICS_READY', 'REQUIRED_TOPICS_READY_STALE', 'ALL_TOPICS_READY', 'ALL_TOPICS_READY_STALE', 'REQUESTED_RESUME', 'REQUESTED_RESUME_RETRY', 'REQUESTED_RESUME_ERROR', 'RESUME_READY', 'RESUME_READY_STALE', 'REQUESTED_ARTIFACTS', 'REQUESTED_ARTIFACTS_RETRY', 'REQUESTED_ARTIFACTS_ERROR', 'ARTIFACTS_READY', 'ARTIFACTS_READY_STALE', 'ACTIVE_SEARCH', 'PAUSE_SEARCH', 'INACTIVE', 'DELETED']

### Comments

#### susan — 2026-08-17T05:24:03.297Z
1388

#### chuckles — 2026-08-17T05:20:55.145Z
Ancestor candidates (ranked — pick one, ask about one, or reject the lot):

1. **AST-1388** (Done, parent AST-1387, Astral Dispatcher) — closest. It *is* the hop-label feature: after `craft_get_rubric` succeeds, `candidate.state` becomes `REQUESTED_ARTIFACTS.craft_get_rubric`. Plan lives on the AST-1252 feature doc. Runtime labels were never supposed to be `CANDIDATE_STATES` keys; today's error is membership rejection of exactly that string.
2. **AST-1387** (Done) — parent of AST-1388: “ARTIFACTS_REQUESTED daisy chain state doesn't update like BUILD_ARTIFACTS.”
3. **AST-1252** (Done, parent AST-1243) — owns the `run_requested_artifacts_dispatch` rewrite onto `craft_get_rubric` @ `REQUESTED_ARTIFACTS`; AST-1388's as-is/to-be is patched onto this same plan doc.
4. **AST-1243** (Done) — epic “Candidate Artifacts now daisy chain” (parent of AST-1252 and AST-1264).
5. **AST-1264** (Done, parent AST-1243) — same candidate `somerset`, same `REQUESTED_ARTIFACTS` + `craft_get_rubric` hop; different failure (run_next did not continue to `craft_do_rubric`).
6. **AST-1285** (Done) — “State transition validation for candidates is broken.” Related machinery; error text here is membership (`Invalid candidate state 'X'. Must be one of:`), not `Invalid candidate state transition`.
7. **AST-1287** (child of AST-1285) — admin force-override for illegal hops; unknown state names stay rejected even with `force=True`.
8. **AST-970** (Archive) — candidate state registry that defined the allowed list (no compound hop labels).
9. **AST-1113** (Archive) — earlier `run_requested_artifacts_dispatch` succession rewrite.

Move this ticket to Todo (assignee Chuckles) when the ancestor + as-is/to-be look right. I will not seed git or start the fix lane until then.

---

_Implementation detail may live in git history on `origin/dev`._
