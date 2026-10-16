# AST-1941 — Hold state on BUILD_ARTIFACTS hop provider failure (BUG: BUILD_ARTIFACTS -> ERROR_BUILD_ARTIFACTS)

<!-- linear-archive: AST-1941 archived 2026-10-08 -->

## Linear archive (AST-1941)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1941/hold-state-on-build-artifacts-hop-provider-failure-bug-build-artifacts  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / 1  
**Parent:** AST-1940 — BUG: BUILD_ARTIFACTS -> ERROR_BUILD_ARTIFACTS  
**Blocked by / blocks / related:** parent: AST-1940; blocks: AST-1942

### Description

## What this implements

Stop a failed provider call on a BUILD_ARTIFACTS dispatch-chain hop from moving the job to `ERROR_BUILD_ARTIFACTS`. Today `_apply_dispatch_chain_hop_failure` in `src/core/agent.py` (provider-failure branch added by AST-1191) counts `provider_failed and not balance_hold` as a hard failure. The job is transitioned to `TASK_CONFIG[*].error_state` and drops out of the dispatch pool, so the hop is never retried. After this fix the job keeps its last happy state / hop label, the batch claim is still released, and the next sweep retries the hop.

## Scope

### Component scope

* `src/core/agent.py` (modified): `_apply_dispatch_chain_hop_failure` owns the hard-vs-hold decision for dispatch-chain hop failures. Provider failures are wrongly classed as hard here.
* `tests/component/core/test_agent.py` (modified, Betty's tree): the existing AST-1191 / AST-1298 hop-failure tests assert the error-state transition being removed. They must instead assert held state + claim release.

### Technical scope

* `src/core/agent.py`: modify `_apply_dispatch_chain_hop_failure`, narrowing the `hard` predicate to the missing-job / missing-candidate strings. Provider failures (balance or otherwise) then hold state and release the claim, which restores the AST-596 "stay in last happy compound state" decision. No new function, table, field, or config state. `TASK_CONFIG` `error_state` strings and `JOB_STATES` registry stay as they are.
* `tests/component/core/test_agent.py`: modify the existing provider-failure hop tests' expectations (no `transition_job_state` call, `batch_released` true). No new fixtures.

## Acceptance criteria

1. A dispatch-chain hop whose provider call returns `success=False` (any `failure_class`) does not call `transition_job_state` to `ERROR_BUILD_ARTIFACTS`. The job stays on its current state / hop label.
2. The job's batch claim is still released on that path (`batch_released: True`), so the next dispatch sweep picks it up again.
3. `Job not found` / `Missing candidate_data` hop failures still transition to `ERROR_BUILD_ARTIFACTS` and release the claim.
4. The existing `do_task(...) provider call failed batch_id=… error=…` ERROR line and the AST-538 debug detail still emit with the non-empty error.

## Boundaries

Adds no retry cap or backoff (Susan's rule: no limits without her say-so). Does not change `TASK_CONFIG` `error_state` strings, `JOB_STATES` / prior-states registry, `run_next` membership, hop topology, or LLM adapters. Does not touch the consult batch runner's own failure branch.

## Notes for planning

Susan approved without checking an ancestor box. The bug-find read is in mini-parent AST-1940's Description: AST-1191 (`docs/features/artifacts/ast-1191-artifact-hop-failure-release-debug-trail.md`) introduced the provider-failure → error-state rule. AST-596 / AST-788 / AST-803 hold the earlier "retryable hop failure stays on last happy state" decision. Full as-is/to-be is in AST-1940.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1940-hop-failure-preserve-state`, child `sub/AST-1940/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-02T19:12:18.657Z
[code-rubric] PROCEED (Commit: 75baf6cc4) product hold predicate

#### katherine — 2026-10-02T19:10:35.502Z
`origin/sub/AST-1940/AST-1941-hold-state-on-hop-provider-failure` @ `75baf6cc` — test-fix lighter check (no qa-fix manifest; test work is AST-1942)

```bash
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py tests/component/utils/test_llm_external.py -q
```

- Tip: 46 failed / 355 passed. Baseline (same tree, `src/core/agent.py` from `origin/ftr/AST-1940-hop-failure-preserve-state`): 40 failed / 361 passed.
- 40 failures are shared with the ftr baseline (pre-existing, not touched by this change). 0 tests fixed, 6 new — exactly the plan's Blast radius list.

**Expected failures — flip owned by AST-1942 (not a product defect):**
1. `TestAst1191ArtifactHopFailureRelease::test_apply_provider_failed_transitions_and_releases` — `apply_error_state` now False
2. `TestAst1191ArtifactHopFailureRelease::test_do_task_provider_timeout_releases_and_errors` — transition called 0 times
3. `TestAst1191ArtifactHopFailureRelease::test_do_task_debug_emits_found_and_recorded` — transition called 0 times
4. `TestAst1191ArtifactHopFailureRelease::test_do_task_debug_false_skips_found_recorded` — transition called 0 times
5. `TestAst1298OrphanedJobClaimRelease::test_do_task_draft_job_resume_connection_error_releases_and_errors` — transition called 0 times
6. `TestAst1298OrphanedJobClaimRelease::test_apply_transition_non_value_error_still_releases` — DID NOT RAISE RuntimeError (Connection error no longer transitions; switch `error` to a hard string per plan)

No other new failures; no product change needed. Nothing pushed this pass.

#### joan — 2026-10-02T19:06:42.618Z
[board-joan]  CANON: OK

context_tokens≈14000

#### betty — 2026-10-02T19:06:22.401Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md § AST-1191 · AST-1164 (+ § AST-1298 · AST-1280) — broken tests — tests/component/core/test_agent.py pins the superseded provider-failure → ERROR_BUILD_ARTIFACTS transition: TestAst1191ArtifactHopFailureRelease::{test_apply_provider_failed_transitions_and_releases, test_do_task_provider_timeout_releases_and_errors, test_do_task_debug_emits_found_and_recorded, test_do_task_debug_false_skips_found_recorded} and TestAst1298OrphanedJobClaimRelease::test_do_task_draft_job_resume_connection_error_releases_and_errors flip to transition.assert_not_called() + release once (apply-level: apply_error_state False / error_state "" / batch_released True); TestAst1298OrphanedJobClaimRelease::test_apply_transition_non_value_error_still_releases needs a hard error string ("Job not found") to keep the Stage 1 non-ValueError-still-releases invariant reachable; bible AST-1191 "non-balance provider failures apply error_state" → held-state rule. Repro is the revised apply-level node (red on tip, green post-fix). Unaffected: balance-hold, hop-label-false, Missing-candidate_data hard-string (L5603), tests/integration (no hits).

#### katherine — 2026-10-02T19:05:09.134Z
`origin/sub/AST-1940/AST-1941-hold-state-on-hop-provider-failure` @ `c4669172` · provider failures hold, release

---

_Implementation detail may live in git history on `origin/dev`._
