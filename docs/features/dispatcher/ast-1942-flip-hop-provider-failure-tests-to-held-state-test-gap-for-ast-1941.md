# AST-1942 — Flip hop provider-failure tests to held state (test gap for AST-1941)

<!-- linear-archive: AST-1942 archived 2026-10-08 -->

## Linear archive (AST-1942)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1942/flip-hop-provider-failure-tests-to-held-state-test-gap-for-ast-1941  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / 1  
**Parent:** AST-1940 — BUG: BUILD_ARTIFACTS -> ERROR_BUILD_ARTIFACTS  
**Blocked by / blocks / related:** parent: AST-1940

### Description

## What this implements

Test gap from fix-board on AST-1941 (`[board-betty] TESTS: REVISE`). Six existing `tests/component/core/test_agent.py` tests pin the provider-failure → `ERROR_BUILD_ARTIFACTS` transition that AST-1941 removes. The test bible's AST-1191 entry still documents the old rule.

## Scope

### Component scope

* `tests/component/core/test_agent.py` (modified): flip `TestAst1191ArtifactHopFailureRelease::{test_apply_provider_failed_transitions_and_releases, test_do_task_provider_timeout_releases_and_errors, test_do_task_debug_emits_found_and_recorded, test_do_task_debug_false_skips_found_recorded}` and `TestAst1298OrphanedJobClaimRelease::test_do_task_draft_job_resume_connection_error_releases_and_errors` to "no transition, claim released once". Repoint `TestAst1298OrphanedJobClaimRelease::test_apply_transition_non_value_error_still_releases` to a hard error string (`Job not found`) so the non-ValueError-still-releases invariant stays reachable.
* `docs/test-bible/core/agent.md` (modified): § AST-1191 · AST-1164 (and § AST-1298 · AST-1280 where it repeats the rule) — "non-balance provider failures apply `error_state`" becomes the held-state rule.

### Technical scope

* `tests/component/core/test_agent.py`: modified test functions only. Apply-level assertions become `transition.assert_not_called()` + release once, with outcome `{"apply_error_state": False, "error_state": "", "batch_released": True}`. The revised apply-level provider-failure test is the bug repro. No new fixtures.
* `docs/test-bible/core/agent.md`: modified bible prose/rows for the AST-1191 / AST-1298 entries.

## Acceptance criteria

1. The bug-repro test (revised apply-level provider-failure node) fails on `origin/dev`'s `src/core/agent.py` and passes once AST-1941's product fix is on the tip.
2. The repointed non-ValueError test still proves the claim is released when the transition raises a non-ValueError.
3. Balance-hold, hop-label-false, and `Missing candidate_data` hard-string tests are unchanged and still pass.
4. No product code changes on this ticket.

## Boundaries

Tests and bible only. The product fix (narrowing the `hard` predicate in `_apply_dispatch_chain_hop_failure`, `src/core/agent.py`) belongs to sibling AST-1941. It lands on the mini-parent ftr first and reaches this sub via sync-child. No integration scenarios touch this path (Betty confirmed).

## Notes for planning

Gap child filed by bug-fix from Betty's `[board-betty] TESTS: REVISE` on AST-1941 — read that comment. Plan section home: `docs/features/dispatcher/ast-1298-release-orphaned-job-claim-after-provider-connection-error.md` (same doc as AST-1941's `## Bug:` block).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1940-hop-failure-preserve-state`, child `sub/AST-1940/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-02T19:23:04.395Z
[code-rubric] PROCEED (Commit: 48c4881a0) tests bible gap closed

#### katherine — 2026-10-02T19:22:01.423Z
`origin/sub/AST-1940/AST-1942-flip-hop-provider-failure-tests` @ `48c4881a` — test-fix

**[bug-repro] gate:** `TestAst1191ArtifactHopFailureRelease::test_apply_provider_failed_holds_state_and_releases` — **red** with `origin/dev` `src/core/agent.py` temporarily checked out (`error_state` 'ERROR_BUILD_ARTIFACTS' != ''), **green** on tip; `src/` restored clean.

**Manifest** (`ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh …`):
- `tests/component/core/test_agent.py`: 40 failed / 342 passed.
- `+ tests/component/utils/test_llm_external.py`: 40 failed / 361 passed (was 46 / 355 at AST-1941 test-fix).
- vs pre-fix ftr baseline: 0 new failures; the six AST-1941 nodes are all green; the 40 remaining are the identical pre-existing baseline nodes (Python 3.14 env) — out of scope.

No product change needed; nothing pushed this stage.

#### betty — 2026-10-02T19:18:28.917Z
[bug-repro]
`origin/sub/AST-1940/AST-1942-flip-hop-provider-failure-tests` @ `a9cc5e1b2` · repro red pre-fix, green on tip
Repro node `TestAst1191ArtifactHopFailureRelease::test_apply_provider_failed_holds_state_and_releases`. Stacked deviation (AST-1941 fix already on ftr): **red** with `origin/dev` `src/core/agent.py` temporarily checked out (Differing: `apply_error_state` True≠False, `error_state` 'ERROR_BUILD_ARTIFACTS'≠'' — the Root-cause provider clause), restored (src clean); **green** on synced tip. `test_agent.py` + `test_llm_external.py`: 46 failed → 40 failed / 361 passed; the 40 are the identical pre-existing ftr-baseline nodes (0 new). Manifest: `docs/test-bible/core/agent.md` § AST-1191 (shasum `9192e549`).

#### joan — 2026-10-02T19:14:49.637Z
[board-joan]  CANON: OK

context_tokens≈18000

#### betty — 2026-10-02T19:14:34.166Z
[board-betty] TESTS: OK
Plan-fix covers the full AST-1941 REVISE gap (6 test_agent.py nodes + docstring + agent.md § AST-1191 / § AST-1298 prose/rows); all node ids, line refs, inputs, and bible rows verified against origin/sub/AST-1940/AST-1942-flip-hop-provider-failure-tests @ 0a31a7861. Renamed repro node test_apply_provider_failed_holds_state_and_releases carries the red-on-origin/dev / green-on-tip gate (AC1). No further test work beyond this patch; tests/integration unaffected.

#### katherine — 2026-10-02T19:13:44.981Z
`origin/sub/AST-1940/AST-1942-flip-hop-provider-failure-tests` @ `0a31a786` · six tests flip, bible held-state

---

_Implementation detail may live in git history on `origin/dev`._
