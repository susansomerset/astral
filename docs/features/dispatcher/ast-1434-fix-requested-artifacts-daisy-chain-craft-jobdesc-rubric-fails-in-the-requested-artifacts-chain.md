# AST-1434 — Fix REQUESTED_ARTIFACTS daisy chain (craft_jobdesc_rubric fails in the REQUESTED_ARTIFACTS chain)

<!-- linear-archive: AST-1434 archived 2026-09-09 -->

## Linear archive (AST-1434)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1434/fix-requested-artifacts-daisy-chain-craft-jobdesc-rubric-fails-in-the  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1426 — craft_jobdesc_rubric fails in the REQUESTED_ARTIFACTS chain  
**Blocked by / blocks / related:** parent: AST-1426

### Description

## What this implements

Unstick the `REQUESTED_ARTIFACTS` craft-rubric daisy chain so live `agent_task.run_next` is the only membership signal, hops persist, and `craft_jobdesc_rubric` (plus the rest of the walk) continues. Ancestor context: AST-1243 (`docs/features/candidate/ast-1243-candidate-artifacts-now-daisy-chain.md`) — archived; this mini-parent is a fresh epic off `origin/dev`, related only by that doc.

## Citations

* `astral.dispatch.run-next-is-chain-authority`
* `pattern.dispatch.run-next-chain-authority` (proposed)
* `astral.state.no-daisy-chain-in-run`

## Acceptance criteria

- [X] Daisy-chain participation is solely that `agent_task.run_next` is set (or reached via one); no remaining code/config membership list on this path.
- [X] A `skip-daisy-chain` toggle on `dispatch_task` (or equivalent of `suppress_run_next`) covers a one-off mid-hop run.
- [X] Chain hop output/graduation is `<dispatch_task.trigger_state>.<completed_task_key>` for current and future chains.
- [X] `craft_joblist_rubric` / `craft_jobdesc_rubric` persist and the `REQUESTED_ARTIFACTS` walk continues (grade-letter-per-line vs inline `A ==` persist reject unstuck).

## Boundaries

Does not revive AST-1109's `config.py` epic unless that remaining gate is the actual block on this path. Does not daisy-chain resume generation.

## Notes for planning

Patch the existing AST-1243 feature doc — do not create a new plan doc. Parent AST-1426 Description has As-is / To-be / Proposed steps plus the original log dump.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1426-craft-jobdesc-rubric-requested-artifacts`, child `sub/AST-1426/<this-id>-fix-requested-artifacts-daisy-chain`. Created at bug-fix (orphaned mini-parent).

### Comments

#### radia — 2026-08-19T01:06:11.185Z
[code-rubric] PROCEED (Commit: 1fd85ad1) Inline persist, run_next chain

#### ada — 2026-08-19T00:56:46.734Z
`origin/sub/AST-1426/AST-1434-fix-requested-artifacts-daisy-chain` @ `1fd85ad1`

#### joan — 2026-08-19T00:40:14.629Z
[board-joan]  CANON: OK

#### betty — 2026-08-19T00:37:42.190Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/rubric_text.md — missing coverage — pasted one-line A== B== persist (repro step 1) has no node; TestAst972CandidateStageConsultRouting is entry-hop-only and will break when consult passes task_key/trigger/skip

#### ada — 2026-08-19T00:35:30.001Z
`origin/sub/AST-1426/AST-1434-fix-requested-artifacts-daisy-chain` @ `9c11bbda` · daisy-chain plan patched

---

_Implementation detail may live in git history on `origin/dev`._
