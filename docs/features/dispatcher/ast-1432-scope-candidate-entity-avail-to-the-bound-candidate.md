# AST-1432 — Scope candidate-entity Avail to the bound candidate

<!-- linear-archive: AST-1432 archived 2026-09-09 -->

## Linear archive (AST-1432)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1432/scope-candidate-entity-avail-to-the-bound-candidate  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1425 — dispatch tasks with entity_type = 'candidate' do not filter properly  
**Blocked by / blocks / related:** parent: AST-1425

### Description

## What this implements

Scope Scheduled Actions Availability for `entity_type=candidate` dispatch tasks to the row's own `dispatch_task.candidate_id`, so Avail is always 0 or 1. Other candidates in the same trigger state must not add to the count.

Approved ancestor: AST-1257 (Susan). Product change landed on AST-1258 (`count_eligible_for_dispatch_task` cross-candidate pool).

## Citations

pattern.batch.entity-claim-process-release
astral.batch.claim-process-release

## Acceptance criteria

- [X] Scheduled Actions Avail for a candidate-entity dispatch_task row is 0 or 1: whether that row's candidate is eligible.
- [X] Other candidates in the same trigger state do not increase the count.
- [X] Job/company pool Avail and mailbox `gaze_email` bind-counts stay unchanged.

## Proposed change

- [X] `count_candidates_unclaimed_in_states` optional `candidate_id` (0/1 when set).
- [X] `count_eligible_for_dispatch_task` candidate non-inflow arm passes `candidate_id`.
- [X] Docstring: candidate non-inflow Avail is this row's candidate, not the pool.
- [X] Claim/get/clear / `get_new_candidate_batch` / `list_dtasks` / job-company branches untouched.

## Boundaries

Does not unwind candidate `batch_id` locking or AST-1259 dispatcher pool claim unless the Avail-only change is insufficient (plan-fix decides). Does not change job/company Avail. Does not retouch gaze_email mailbox counts.

## Notes for planning

Patch the existing AST-1258 feature doc (`docs/features/dispatcher/ast-1258-candidate-batch-lock-schema-and-pool-claim-apis.md`) — do not create a new plan doc. Parent bug AST-1425 Description has As-is / To-be / Proposed steps.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1425-candidate-dispatch-avail-filter`, child `sub/AST-1425/<this-id>-scope-candidate-avail-to-bound-candidate`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-19T00:54:53.315Z
[code-rubric] PROCEED (Commit: 83575853) bound Avail scoped

#### joan — 2026-08-19T00:40:10.513Z
[board-joan]  CANON: OK

Pool claim unchanged: `claim_candidate_batch` / `get_new_candidate_batch` stay cross-candidate; `astral.batch.claim-process-release` and `pattern.batch.entity-claim-process-release` govern claim → process → release only, not Avail display. Optional `candidate_id` on `count_candidates_unclaimed_in_states` scopes the eligibility query to 0/1 for a bound row — same shape job/company Avail already uses via owner `candidate_id`, not a statute carve-out. AST-1258's pool-wide Avail decision lives in the feature doc; no active statute or pattern mandates global pool Avail for candidate stage keys. AUTO/run_task sharing the same counter (0/1 side effect) is an accepted product decision in the plan-fix patch, not an open architectural canon question.

#### betty — 2026-08-19T00:36:28.604Z
[board-betty] TESTS: REVISE
What: docs/test-bible/data/database/dispatch_tasks.md § AST-1258 — broken test TestAst1258CandidatePoolEligibility::test_pool_count_zero_when_all_matching_rows_locked asserts pool 2 on a bound row; missing coverage of the two-candidate repro (bound Avail 1; lock bound / other unclaimed → 0)

#### katherine — 2026-08-19T00:33:16.553Z
`origin/sub/AST-1425/AST-1432-scope-candidate-avail-to-bound-candidate` @ `bd5f31db` · bound-candidate Avail 0/1

---

_Implementation detail may live in git history on `origin/dev`._
