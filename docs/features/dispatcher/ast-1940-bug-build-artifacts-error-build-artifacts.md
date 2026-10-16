# AST-1940 — BUG: BUILD_ARTIFACTS -> ERROR_BUILD_ARTIFACTS

<!-- linear-archive: AST-1940 archived 2026-10-08 -->

## Linear archive (AST-1940)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1940/bug-build-artifacts-error-build-artifacts  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

When a provider call fails on a BUILD_ARTIFACTS dispatch-chain hop (job sitting on a runtime hop label such as `BUILD_ARTIFACTS.anticipate_scan`), `_apply_dispatch_chain_hop_failure` in `src/core/agent.py` counts `provider_failed and not balance_hold` as a **hard** failure. The job is transitioned to `TASK_CONFIG[*].error_state` = `ERROR_BUILD_ARTIFACTS` and the claim is released. The job leaves the BUILD_ARTIFACTS dispatch pool, so the hop is never retried. This behavior arrived with AST-1191 (commit `7f5b132e`). It overrides the earlier rule from AST-596/AST-788/AST-803: retryable hop failures stay on the last happy compound state, and only `Job not found` / `Missing candidate_data` are hard. Today only provider balance refusals (AST-897) still hold state.

## To-be

A mid-run BUILD_ARTIFACTS hop failure does **not** change the job to an error state. The job keeps its previous (last happy) state / hop label, the batch claim is released, and the next dispatch sweep retries the hop. `ERROR_BUILD_ARTIFACTS` is reserved for the genuinely unrecoverable cases (`Job not found`, `Missing candidate_data`). Failure recording (app_log ERROR line, Execution History against the batch_id, AST-538 debug detail) is unchanged.

## Proposed steps

1. In `_apply_dispatch_chain_hop_failure`, drop the `(provider_failed and not balance_hold)` clause from the `hard` predicate so provider failures follow the same hold-and-release path balance refusals already take.
2. Keep the `finally` claim release exactly as it is, so the held job goes back into the dispatch pool.
3. Keep the hard-string gate (`Job not found` / `Missing candidate_data`) → `ERROR_BUILD_ARTIFACTS`.
4. Make sure the outcome dict (`apply_error_state: False`, `batch_released: True`) and the debug line correctly report a held, released job.
5. Betty flips the AST-1191 / AST-1298 component tests in `tests/component/core/test_agent.py` that currently assert `transition_job_state(..., ERROR_BUILD_ARTIFACTS)` on provider failure, so they assert held state + claim release instead.

Open point for Susan (does not block the fix shape): this adds no retry cap, so a provider that keeps failing will be retried on every sweep. That matches how balance-refusal holds behave today. Per house rules, no limit is added unless you ask for one.

## Component scope

* `src/core/agent.py` (modified): `_apply_dispatch_chain_hop_failure` owns the hard-vs-hold decision for dispatch-chain hop failures. Provider failures are wrongly classed as hard here.
* `tests/component/core/test_agent.py` (modified, Betty's tree): the existing AST-1191 / AST-1298 hop-failure tests assert the error-state transition being removed. They must instead assert held state + claim release.

## Technical scope

* `src/core/agent.py`: modify `_apply_dispatch_chain_hop_failure`, narrowing the `hard` predicate to the missing-job / missing-candidate strings. Provider failures (balance or otherwise) then hold state and release the claim, which restores the AST-596 "stay in last happy compound state" decision. No new function, table, field, or config state. `TASK_CONFIG` `error_state` strings and `JOB_STATES` registry stay as they are.
* `tests/component/core/test_agent.py`: modify the existing provider-failure hop tests' expectations (no `transition_job_state` call, `batch_released` true). No new fixtures.

## Ancestor candidates

- [ ] AST-1191 — artifact hop failure release + debug trail (`docs/features/artifacts/ast-1191-artifact-hop-failure-release-debug-trail.md`): introduced provider-failure → `ERROR_BUILD_ARTIFACTS`. Direct cause.
- [ ] AST-596 — mid-chain dispatch claim and hop-failure batch release (`docs/features/artifacts/ast-596-mid-chain-dispatch-claim-and-hop-failure-batch-release.md`): Susan's decision that daisy-chain jobs stay in the last happy compound state on hop failure.
- [ ] AST-803 — BUILD_ARTIFACTS chain dispatch (`docs/features/consult/ast-803-build-artifacts-chain-dispatch.md`): original rule that only `Job not found` / `Missing candidate_data` are hard and all other hop failures retry.
- [ ] AST-788 — BUILD_ARTIFACTS substates do not graduate (`docs/features/consult/ast-788-build-artifacts-substates-do-not-graduate.md`): defined `ERROR_BUILD_ARTIFACTS` as the hard-only holding state, with retryable failures staying on the last completed state.
- [ ] AST-1298 — release orphaned job claim after provider connection error (`docs/features/dispatcher/ast-1298-release-orphaned-job-claim-after-provider-connection-error.md`): extended the same failure path's claim release and tests.
- [ ] AST-897 — hold entity state on provider balance refusal (`docs/features/agent/ast-897-hold-entity-state-on-provider-balance-refusal.md`): the existing hold-state path this fix generalizes.

---

## Original brief

When a BUILD_ARTIFACTS mid-run hop fails, the state does NOT change to an error state, it preserves the previous state so that the retry can happen.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
