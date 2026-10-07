# AST-1812 — gap: tests for skipped-job any-state override (AST-1811 board REVISE)

<!-- linear-archive: AST-1812 archived 2026-10-07 -->

## Linear archive (AST-1812)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1812/gap-tests-for-skipped-job-any-state-override-ast-1811-board-revise  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1809 — Allow Skipped Job state change to ANY job state, do not filter/validate  
**Blocked by / blocks / related:** parent: AST-1809

### Description

## What this implements

Test gap from `[board-betty] TESTS: REVISE` on AST-1811: bring component tests and bible in line with the skipped-job operator override (any `JOB_STATES` key, no prior-state filter on the skipped-edit path) and cover the new bypass.

## Scope

### Component scope

* `tests/component/core/test_tracker.py` — modified: `TestAst1453LegalJobSuccessorStates` asserts the prior-filtered list; `test_writes_title_link_jd_then_transition` mocks `transition_job_state` without kwargs (TypeErrors once persist passes `enforce_prior_states=False`); `test_field_writes_before_illegal_transition_propagates` premise must become an unregistered-target case; new coverage for the bypass and default enforcement.
* `tests/component/ui/api/test_api_jobs.py` — modified: `test_put_illegal_transition_409` premise must become an unregistered-target (non-`JOB_STATES`) 409 case.
* `docs/test-bible/core/tracker.md` — modified: AST-1453 entries describe the old prior-filtered contract.
* `docs/test-bible/ui/api/api_jobs.md` — modified: PUT 409 entry describes an "illegal transition" premise that no longer exists for registry keys.

### Technical scope

* `test_tracker.py` — modified test classes/functions: successor list = every `JOB_STATES` key except current; transition mock accepts the keyword-only flag; new tests that `enforce_prior_states=False` skips the prior check, default still raises `Invalid transition`, and persist rejects a non-`JOB_STATES` target (`*_RETRY` / hop label) with "not in allowed list" while keeping field edits.
* `test_api_jobs.py` — modified test function: 409 on an unregistered target instead of an illegal hop.
* Bible files — modified entries: document the new contract and the new nodes.

## Boundaries

Product code stays on AST-1811; canon carve-out on the sibling canon gap. Test tree / bible only (Betty).

## Notes for planning

Board: `[board-betty] TESTS: REVISE` on AST-1811 (full text in that comment). `src/core/tracker.py` is `LOCKED_AT_100` — new branches need coverage. Plan: `docs/features/interface/ast-1453-persist-skipped-job-field-and-state-edits.md` `## Bug: AST-1811`.

## Git branch (authoritative)

Parent `ftr/AST-1809-skipped-any-state`, child `sub/AST-1809/AST-1812-skipped-any-state-tests`. Created at bug-fix.

### Comments

#### radia — 2026-09-27T01:28:47.653Z
[code-rubric] PROCEED (Commit: 2d6b6e6e) bug-repro manifest clean

#### ada — 2026-09-27T01:27:23.513Z
`origin/sub/AST-1809/AST-1812-skipped-any-state-tests` @ `2d6b6e6e` · repro flipped, manifest green

- Pushed: `sync(ftr)` merge only (ftr now carries AST-1811 product + AST-1813 carve-out); no product/test edits.
- `[bug-repro]` gate: manifest (`TestTransitionJobState`, `TestAst1453LegalJobSuccessorStates`, `TestAst1453PersistSkippedJobEdits`, `TestAst1453SkippedEditMetaAndPut`) with `tracker.py` @ `origin/dev` → **8 failed / 21 passed** (all 3 `[bug-repro]` nodes red); at tip → **29 passed**.
- Whole `test_tracker.py` + `test_api_jobs.py`: 19 failed / 199 passed — all 19 in the pre-existing unrelated set (bible § AST-1812); 0 new reds; 3 prior `TestAst1453SkippedEditMetaAndPut` reds now green (`_detail_wire` fix).
- Ran pytest directly with the `astral-tests` venv interpreter (same targets as `run_component_tests.sh`; skipped the harness's worktree `.venv` build).

#### betty — 2026-09-27T01:14:54.531Z
[bug-repro]
`origin/sub/AST-1809/AST-1812-skipped-any-state-tests` @ `b84b95ee` · 8 red pre-fix, green on AST-1811 `57b178d8`
Manifest + repro nodes: `docs/test-bible/core/tracker.md` § AST-1812.

---

_Implementation detail may live in git history on `origin/dev`._
