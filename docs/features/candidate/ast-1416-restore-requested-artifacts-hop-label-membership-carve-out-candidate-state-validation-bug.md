# AST-1416 — Restore REQUESTED_ARTIFACTS hop-label membership carve-out (Candidate state validation bug)

<!-- linear-archive: AST-1416 archived 2026-09-09 -->

## Linear archive (AST-1416)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1416/restore-requested-artifacts-hop-label-membership-carve-out-candidate  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1415 — Candidate state validation bug  
**Blocked by / blocks / related:** parent: AST-1415

### Description

## What this implements

Restore the AST-1388 carve-out so compound hop labels like `REQUESTED_ARTIFACTS.craft_get_rubric` are accepted as runtime candidate states during `run_requested_artifacts_dispatch` — they are not `CANDIDATE_STATES` registry keys. Membership rejection of that label currently kills the artifacts daisy chain for candidate `somerset`.

Approved ancestor: AST-1388 (live, Done). Feature doc: `docs/features/candidate/ast-1252-artifacts-dispatch-chain-persistence-and-retire-wrappers.md` (`## Bug: AST-1388`).

## As-is

`run_requested_artifacts_dispatch` for candidate `somerset` fails with `Invalid candidate state 'REQUESTED_ARTIFACTS.craft_get_rubric'. Must be one of: [bare CANDIDATE_STATES keys]`. After the first craft hop, something tries to persist that compound hop label as `candidate.state`; a registry-membership check rejects it, the worker logs the error, and the chain stops.

## To-be

Compound hop labels of the form `REQUESTED_ARTIFACTS.<completed_task_key>` are accepted as runtime candidate states on the artifacts dispatch path (same shape as job `BUILD_ARTIFACTS` hop labels, not registry keys). Writes succeed; later hops and terminal `ARTIFACTS_READY` / retry / error can follow.

## Citations

AST-1388 hop-label plan on the AST-1252 feature doc. `astral.state.candidate-registry` / code-rules hop-label carve-out (jobs already have this; candidates should match).

## Acceptance criteria

- [X] `run_requested_artifacts_dispatch` can persist `REQUESTED_ARTIFACTS.craft_get_rubric` (and later hops) without `Invalid candidate state '...'. Must be one of:`.
- [X] A following hop or `ARTIFACTS_READY` can legally follow the compound label.
- [X] Job `BUILD_ARTIFACTS` hop-label behavior is unchanged.

## Proposed change

- [X] `save_candidate` INSERT/UPDATE membership uses `is_valid_candidate_batch_claim_state` (registry keys + `REQUESTED_ARTIFACTS.<TASK_CONFIG key>`).
- [X] Rejects still use `Invalid candidate state '{state}'. Must be one of: {allowed}` with registry keys as `allowed`.
- [X] `is_valid_candidate_batch_claim_state` docstring widened to persist + claim (no logic change).
- [X] Hop labels not added to `CANDIDATE_STATES`; write path / job graduation maps untouched.

## Boundaries

Does not re-plan AST-1252's dispatch rewrite. Does not add hop labels to `CANDIDATE_STATES`. Does not change job graduation maps.

## Notes for planning

Patch the existing AST-1252 / AST-1388 feature doc — do not create a new plan doc. Parent mini-epic is AST-1415 (orphaned bug; its own ftr off origin/dev).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1415-candidate-state-validation-bug`, child `sub/AST-1415/<this-id>-restore-hop-label-membership`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-17T06:00:53.954Z
[code-rubric] PROCEED (Commit: 1b16124c) hop-label persist carve-out

#### betty — 2026-08-17T05:40:30.935Z
[board-betty] TESTS: REVISE
What: docs/test-bible/data/database/candidates.md — missing coverage — save_candidate persist of REQUESTED_ARTIFACTS.<hop> (AST-1389 mocks the write; TestSaveCandidate only rejects NOT_A_STATE)

#### joan — 2026-08-17T05:38:26.942Z
[board-joan]  CANON: OK

context_tokens≈12000

#### ada — 2026-08-17T05:35:04.888Z
`origin/sub/AST-1415/AST-1416-restore-hop-label-membership` @ `50221217` · save_candidate rejects hop labels

---

_Implementation detail may live in git history on `origin/dev`._
