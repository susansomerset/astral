<!-- linear-archive: AST-970 archived 2026-08-05 -->

## Linear archive (AST-970)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-970/candidate-state-registry-and-transitions-candidate-state-machine  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-871 — Candidate state machine  
**Blocked by / blocks / related:** parent: AST-871; blocks: AST-973; blocks: AST-972; blocks: AST-971

### Description

## What this implements

Config-backed runtime candidate state vocabulary (no PROSPECT), allowed transitions, stale/retry/error companions, INACTIVE + DELETED (DELETED starts reap timer), and enforced transition behavior replacing the old four-step machine. Manual topic-ready transitions allowed.

## Acceptance criteria

1. Product config exposes the runtime candidate state vocabulary (no PROSPECT) and allowed transitions; disallowed hops are rejected.
2. INACTIVE and DELETED both exist; entering DELETED starts the configured reap timer toward hard delete of candidate data in production.
3. A candidate can move through the documented happy path from NEW_CANDIDATE through intake topic-ready stages (manual transitions acceptable), resume request/ready, artifacts request/ready, to ACTIVE_SEARCH, and into PAUSE_SEARCH / INACTIVE / DELETED as defined.
4. Waiting stages Susan marked for stale age into their stale companion after the configured hours.

## Boundaries

Does **not** own history storage (sibling: Candidate transition history), dispatch claim wiring (sibling: Dispatch and stale eligibility), or legacy row / FK migration (sibling: Legacy candidate migration).

## Notes for planning

Follow Code Rules §2.1 / §2.6 — state lists and transitions in config. Align toward job-style prior/allowed transitions. PROSPECT is conceptual only.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-871-candidate-state-machine`, child `sub/AST-871/<this-id>-candidate-state-registry`. Created at dispatch-parent.

### Comments

#### betty — 2026-07-24T00:59:33.641Z
[merge-child] blocked: git pull merge on sub — `Merge remote-tracking branch` in ftr..sub (bdf294a, 5a75bdc). Rewrite tip: reset onto `origin/ftr/AST-871-candidate-state-machine`, cherry-pick only `plan|code|merge-tests|test|docs|resolve(AST-970)` commits (no pull merges), force-with-lease push `origin/sub/AST-871/AST-970-candidate-state-registry`. @Ada Lovelace

— Chuckles

#### radia — 2026-07-24T00:19:53.415Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-970
**Publish ref:** `origin/sub/AST-871/AST-970-candidate-state-registry` @ `c694ba1cda9fbcd003550a8dbfe6818279434723`
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-871/AST-970-candidate-state-registry` — layers `core`/`utils`/`ui`/`docs` (+ Betty `tests`/`docs/test-bible`).

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-970)` of `58ef660` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` only |
| orch.git.flow-direction-inviolable | universal | conforms | Child publish on `sub/AST-871/…` |
| orch.git.ftr-sub-topology | universal | conforms | Under parent AST-871 |
| orch.git.merge-on-checkout | universal | conforms | `origin/dev` merge present on tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | No agent long-lived branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree `astral-AST-871` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Hour knobs / ERROR exits decided in plan |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match plan bible |
| orch.pipeline.project-scoped-queues | universal | conforms | Untouched |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No `canon/statutes/**` edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty `test`/`merge-tests` own bible+tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Path ownership respected across commits |
| astral.agent.confidence-bounds | scoped | conforms | No graded/confidence surface |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` path change |
| astral.agent.grade-vector-validation | scoped | conforms | No grade vectors |
| astral.batch.batch-id-first | scoped | conforms | No new claim APIs |
| astral.batch.batch-id-format | scoped | conforms | No batch_id minting |
| astral.batch.claim-process-release | scoped | conforms | Dispatch claim deferred (AST-972) |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_responses writes |
| astral.config.config-source-of-truth | scoped | conforms | Registry/hours/initial_state in config; parallel transitions list removed |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env splits |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (`artifacts/**` / spikes) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan under `docs/features/**` |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single AST-970 plan file |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits are test-tree only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code`/`docs` commits leave tests/bible to Betty |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core owns transition policy; no external I/O |
| astral.layers.import-direction | scoped | conforms | ui→core; core→utils/data; config-only utils |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss (no `scripts/**`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Nav/`progress_rank` from `CANDIDATE_STATES` |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult orchestration |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | No new open endpoints; admin override stays gated |
| astral.standards.data-raises-caller-logs | scoped | conforms | Core `ValueError`; UI maps to 400 |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss (no `src/data/**`) |
| astral.standards.debug-contract-gated | scoped | conforms | No new debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Job-style prior helpers; single registry |
| astral.standards.in-scope-only | scoped | conforms | History/dispatch/legacy left to siblings |
| astral.standards.logging-via-utils | scoped | conforms | Existing `get_logger`; no print/bare logging |
| astral.standards.no-cross-contamination | scoped | conforms | Layered files only |
| astral.standards.no-hardcoded-sets | scoped | conforms | Vocabulary/hours/ranks live in config |
| astral.standards.public-then-helpers | scoped | conforms | New prior/reap/aging helpers grouped with transition block |
| astral.standards.utils-data-late-import-only | scoped | conforms | Config-only utils; no data import |
| astral.state.core-decides-transitions | scoped | conforms | Core enforces; data receives target state |
| astral.state.job-prior-states-enforced | scoped | conforms | Candidate mirrors job `prior_states`; jobs untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Retired PROFILE/CONTEXT auto-hops |
| astral.ui.frontend-file-placement | scoped | not-applicable | paths miss (`src/ui/frontend/**`) |
| astral.ui.naming-conventions | scoped | conforms | No new frontend product files |
| astral.ui.single-gunicorn-worker | scoped | conforms | Untouched |

## Pattern conformance

none cited

## Plan adherence

Stages 1–3 match the plan bible: registry + asserts + config-local NAV/gen_states/INFLOW strings; `transition_candidate_state` / DELETED reap / `age_stale_candidate_states` / create+delete+admin paths; CODE_RULES §2.1/§2.6.3 + State machine section in `CANDIDATE_DATA_MODEL.md`. Self-Assessment MAJOR-CHANGE / high / HIGH matches footprint. Sibling boundaries (AST-971/972/973) not smuggled. Joan plan-rubric APPROVED @ `4cde59f`.

## Findings

### discuss
1. **C4 straggler** — Joan Excluded `astral.git.engineer-test-tree-ban` at plan time; tip includes Betty `tests/**` + `docs/test-bible/**`, so statute is in-scope. Scored **conforms** (engineer commits do not touch test-tree). No product fix required — acknowledge on resolve.

### advisory
1. `docs/features/candidate/CANDIDATE_DATA_MODEL.md` context section still says four fields “gate the `CONTEXT_READY` state transition” while the State machine section is updated. Optional one-line cleanup (or leave for AST-973 consumer sweep).

### fix-now
None.

## What’s solid

- Full runtime vocabulary (no PROSPECT), stale/retry/error companions, INACTIVE/DELETED with `progress_rank=-1`, DELETED reap timer on lifecycle, fail-closed admin hops, stale aging helper without scheduler wiring.

## Notes

Joan plan-rubric Excluded set: `astral.debug.no-repo-root-artifacts-dir`, `astral.git.engineer-test-tree-ban`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.standards.database-header-inventory`, `astral.ui.frontend-file-placement`. Only `engineer-test-tree-ban` scored in-scope (straggler above); others remain `not-applicable`.

— Radia
context_tokens≈95000

#### betty — 2026-07-23T23:41:54.111Z
## QA test manifest — AST-970

`origin/sub/AST-871/AST-970-candidate-state-registry` @ `168c02e` (`merge-tests(AST-970): origin/tests 58ef660207d9897dcc2111f86c9d85b6df5f5c91`)

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst970CandidateStateRegistry \
  tests/component/core/test_candidate.py::TestAst970CandidateStateMachine \
  tests/component/core/test_candidate.py::TestInitiateCandidate \
  tests/component/core/test_candidate.py::TestTransitionCandidateState \
  tests/component/core/test_candidate.py::TestTransitionCandidateStateSuccess \
  tests/component/core/test_candidate.py::TestDeleteCandidate \
  tests/component/core/test_candidate.py::TestCheckContextComplete \
  tests/component/core/test_candidate.py::TestCheckContextCompleteExtended \
  tests/component/core/test_candidate.py::TestParseCandidateResume \
  tests/component/core/test_candidate.py::TestParseCandidateResumeExtended \
  tests/component/ui/api/test_api_candidate.py::TestAst970AdminStateOverride \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_merges_data_state_and_api_key \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_list_candidates_and_states \
  tests/component/ui/api/test_api_system.py::TestSystemNavHelpers \
  tests/component/ui/api/test_api_admin.py::TestAst804CandidateDispatchAdminValidation \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_config_discovery_literals \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-804"
```

### Coverage
1. **Registry** — no PROSPECT; prior_states/companions/ranks; DELETED reap hours; stale→next priors; nav/inflow `ACTIVE_SEARCH`; gen_states `RESUME_READY`/`ACTIVE_SEARCH` (`TestAst970CandidateStateRegistry`)
2. **Transitions** — happy path, manual topic-ready, stale advance, INACTIVE/DELETED unrestricted, ERROR closed forward, PAUSE round-trip (`TestAst970CandidateStateMachine`)
3. **DELETED reap** — lifecycle timer start; `candidate_reap_due_at` / `is_candidate_reap_due`
4. **Stale aging** — `age_stale_candidate_states` moves due waiting rows only
5. **Parse / context** — no auto state writes; completeness via fields / progress_rank
6. **Admin API** — state override via `transition_candidate_state`; illegal hop → 400
7. **Nav** — `progress_rank` gates; terminals never unlock
8. **Obsolete revise** — four-step vocab removed from primary modules; AST-804 options → `ACTIVE_SEARCH` (trigger cases use `intake_initiate_candidate` — inflow_discovery not in TASK_CONFIG / AST-960)

Opaque `LIVE_PROMPTS`/`CONTEXT_READY` fixtures in roster/dispatcher/integration left for **AST-973** consumer sweep (not registry membership asserts).

### Bible shasums (`origin/sub/…`)
- `docs/test-bible/core/candidate.md` `30bd155e442ab6f3fc3fbd9d4b93f59f83c5ee0cd31a54b5660fd5e25e54153b`
- `docs/test-bible/utils/config.md` `f4dc6f068797d3a2453bd870aa32e75bb6d097527a201804103f6c3d96a24cf6`
- `docs/test-bible/ui/api/api_candidate.md` `2883188fe703b122d85d9224e0cfd1b27aeb850fa58c00b4cdc6d81471e04819`
- `docs/test-bible/ui/api/api_system.md` `dd423035707fb53fc71c29e3b78cd8e187331d2523902b51159dc7b113fea06a`
- `docs/test-bible/ui/api/api_admin.md` `d6cb3ac1f95dc2022b62c5dccb8719205e56983c645dfd27c1dcd572e4dcdccb`

— Betty

#### joan — 2026-07-23T23:19:23.226Z
[validate-plan] no-op — already past gate

Spawn asked for Plan Ready re-validate after Plan Discuss r1, but AST-970 is already **Plan Approved** (assignee Ada; verdict attachment `Plan rubric verdict (rev 1)` present from prior pass @ `4cde59f`).

No second rubric pass. Status stays Plan Approved.

— Joan
context_tokens≈80000

#### joan — 2026-07-23T23:17:52.753Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-970
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-871/AST-970-candidate-state-registry` @ `4cde59f`
**Implementer:** Ada Lovelace
**Plan Discuss:** round 1 completed (concern + reply); fix-now closed

## Traceability

### Parent / child AC → plan stages

| AC | Coverage |
| -- | -- |
| 1. Config vocabulary (no PROSPECT) + allowed transitions; disallowed hops rejected | Stage 1 registry + asserts; Stage 2 `transition_candidate_state` / `_candidate_state_allowed` |
| 2. INACTIVE + DELETED; DELETED starts reap timer | Stage 1 keys + `reap_after_hours`; Stage 2 `_start_candidate_reap_timer` / due helpers |
| 3. Happy path NEW_CANDIDATE → … → ACTIVE_SEARCH (+ pause/inactive/deleted) | Stage 1 `prior_states` graph (incl. stale→next); Stage 2 create/delete/admin paths |
| 4. Waiting stages age to stale companions after configured hours | Stage 1 stale metadata; Stage 2 `age_stale_candidate_states` (invocation = AST-972) |
| Parent AC 5–10 | N/A — Boundaries quote siblings AST-971/972/973 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Config registry | Purpose + Functional scope vocabulary / transitions / INACTIVE+DELETED; no PROSPECT; §2.1/§2.6 |
| 2 Enforced transitions + reap + stale helper | Transition rules, DELETED reap start, stale aging capability |
| 3 Docs | CODE_RULES + data model coherent with registry |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge/test SHAs |
| orch.git.commit-vocabulary | conforms | Plan-only publish |
| orch.git.flow-direction-inviolable | conforms | Child `sub/AST-871/…` publish ref |
| orch.git.ftr-sub-topology | conforms | Under parent ftr AST-871 |
| orch.git.merge-on-checkout | conforms | No checkout/merge steps claimed |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | No agent long-lived branches |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-871 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Hour literals recorded as config knobs / product defaults; ERROR exits + AC#4 ownership decided |
| orch.pipeline.plan-is-bible | conforms | Single plan under docs/features/candidate/ |
| orch.pipeline.project-scoped-queues | conforms | Untouched |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready re-validate after discuss |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Ada on APPROVED |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded surface |
| astral.agent.do-task-delegation | conforms | No do_task |
| astral.agent.grade-vector-validation | conforms | No vectors |
| astral.batch.batch-id-first | conforms | No new claim APIs |
| astral.batch.batch-id-format | conforms | No batch_id minting |
| astral.batch.claim-process-release | conforms | Dispatch claim deferred to AST-972 |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_responses writes |
| astral.config.config-source-of-truth | conforms | Registry/hours/initial_state in config; removes parallel transitions list |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets |
| astral.debug.spikes-under-debug-dir | conforms | Feature plan path |
| astral.docs.features-single-file-per-ticket | conforms | Plan at docs/features/candidate/ |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned |
| astral.layers.core-vs-external-bright-line | conforms | Core owns transition policy |
| astral.layers.import-direction | conforms | utils/core/ui only |
| astral.layers.ui-config-driven-business-logic | conforms | Nav/progress_rank via config + API |
| astral.patterns.coat-check-never-store-empty | conforms | N/A |
| astral.patterns.render-verdict-orchestrates-consult | conforms | N/A |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new open endpoints |
| astral.standards.data-raises-caller-logs | conforms | ValueError in core; UI → 400 |
| astral.standards.debug-contract-gated | conforms | No new debug-contract lines |
| astral.standards.dry-and-focused-functions | conforms | Job prior_states mirror; single registry |
| astral.standards.in-scope-only | conforms | Sibling boundaries respected |
| astral.standards.logging-via-utils | conforms | No print/bare logging |
| astral.standards.no-cross-contamination | conforms | Layered files |
| astral.standards.no-hardcoded-sets | conforms | States/hours in config |
| astral.standards.public-then-helpers | conforms | Public transition/aging + private priors |
| astral.standards.utils-data-late-import-only | conforms | Config-only utils |
| astral.state.core-decides-transitions | conforms | Core enforces; data receives target |
| astral.state.job-prior-states-enforced | conforms | Candidate mirrors job priors |
| astral.state.no-daisy-chain-in-run | conforms | Retires auto PROFILE/CONTEXT hops |
| astral.ui.naming-conventions | conforms | No new frontend files |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** all rows in Statute verdicts above (51).

**Excluded:**
- `astral.debug.no-repo-root-artifacts-dir` — paths miss plan paths
- `astral.git.engineer-test-tree-ban` — paths miss plan paths
- `astral.layers.scripts-exempt-from-layer-rules` — layers/paths miss
- `astral.standards.database-header-inventory` — layers/paths miss (no `src/data/**`)
- `astral.ui.frontend-file-placement` — paths miss (`src/ui/frontend/**`)

## Findings

### fix-now
None. Round-1 fix-now closed: `ALL_TOPICS_READY.prior_states` includes `REQUIRED_TOPICS_READY_STALE`; stale→next Decision documents the full graph check.

### discuss (resolved in plan Decisions — non-blocking)
1. ERROR exits closed for v1 (INACTIVE/DELETED escape); AST-972 may extend later.
2. Hours 72/168/720 remain config knobs.
3. Aging helper here; scheduler invocation AST-972.

### acceptable
- HIGH risk + AST-973 remaps; fail-closed + `progress_rank=-1` for terminals.
- Reap on `candidate_data.lifecycle`; config-local NAV/gen_states/INFLOW vs full consumer sweep.

**Self-assessment:** MAJOR-CHANGE / high / HIGH — honest.

— Joan
context_tokens≈72000

#### ada — 2026-07-23T23:13:43.094Z
[plan-discuss] round=1 reply

**fix-now:** Added `REQUIRED_TOPICS_READY_STALE` to `ALL_TOPICS_READY.prior_states`. Re-scanned stale→next edges — the other three (`ALL_TOPICS_READY_STALE`→`REQUESTED_RESUME`, `RESUME_READY_STALE`→`REQUESTED_ARTIFACTS`, `ARTIFACTS_READY_STALE`→`ACTIVE_SEARCH`) were already present; no further graph gaps.

**Discuss resolutions (recorded as Decisions in plan):**
1. **ERROR exits:** intentional for v1 — closed forward; escape via unrestricted `INACTIVE`/`DELETED` only. AST-972 may add `*_ERROR`→`*_RETRY`/re-request later.
2. **Hours 72/168/720:** remain config knobs / product defaults in `config.py` (no code change to retune).
3. **AC#4 vs AST-972:** aging helper stays here; no dispatch/scheduler registration in AST-970.

Published @ `4cde59f` on `origin/sub/AST-871/AST-970-candidate-state-registry`. Returning to **Plan Ready** for Joan re-validate.

— Ada

#### joan — 2026-07-23T23:06:21.277Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-970
**Overall:** REVISE
**Publish ref:** `origin/sub/AST-871/AST-970-candidate-state-registry`
**Implementer:** Ada Lovelace

## Traceability

### Parent / child AC → plan stages

| AC | Coverage |
| -- | -- |
| 1. Config vocabulary (no PROSPECT) + allowed transitions; disallowed hops rejected | Stage 1 registry + asserts; Stage 2 `transition_candidate_state` / `_candidate_state_allowed` |
| 2. INACTIVE + DELETED; DELETED starts reap timer | Stage 1 keys + `reap_after_hours`; Stage 2 `_start_candidate_reap_timer` / due helpers |
| 3. Happy path NEW_CANDIDATE → … → ACTIVE_SEARCH (+ pause/inactive/deleted) | Stage 1 `prior_states` graph; Stage 2 create/delete/admin paths; manual topic-ready noted |
| 4. Waiting stages age to stale companions after configured hours | Stage 1 `stale_after_hours`/`stale_state`; Stage 2 `age_stale_candidate_states` (scheduler call = AST-972) |
| Parent AC 5–10 | N/A — boundaries quote siblings AST-971/972/973 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Config registry | Purpose + Functional scope lifecycle vocabulary / transition rules / INACTIVE+DELETED; Boundaries no PROSPECT; Code Rules §2.1/§2.6 |
| 2 Enforced transitions + reap + stale helper | Transition rules, DELETED reap start, stale aging capability; Boundaries (no history/dispatch claim/legacy remap) |
| 3 Docs | Keep CODE_RULES + data model coherent with shipped registry |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | Plan does not touch Betty merge/test SHAs |
| orch.git.commit-vocabulary | conforms | Plan-only publish; no commit-message invention in scope |
| orch.git.flow-direction-inviolable | conforms | Uses child `sub/AST-871/…` publish ref only |
| orch.git.ftr-sub-topology | conforms | Child under parent `ftr/AST-871-candidate-state-machine` |
| orch.git.merge-on-checkout | conforms | No checkout/merge steps claimed |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite history ops |
| orch.git.no-dev-agent-branches | conforms | No agent-named long-lived branches |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-871 assumed |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | needs-discussion | Stale/reap hour literals (72/168/720) invented as defaults — confirm or leave as config knobs |
| orch.pipeline.plan-is-bible | conforms | Single plan file under `docs/features/candidate/` |
| orch.pipeline.project-scoped-queues | conforms | No queue-scope change |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready path only |
| orch.roles.archie-approves-statutes | conforms | Does not amend `canon/statutes/**` |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Ada on REVISE |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded/confidence surface |
| astral.agent.do-task-delegation | conforms | No `do_task` / Anthropic path |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | No new claim APIs; aging left unscheduled |
| astral.batch.batch-id-format | conforms | No new batch_id minting |
| astral.batch.claim-process-release | conforms | Explicitly defers dispatch claim to AST-972 |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_responses writes |
| astral.config.config-source-of-truth | conforms | Registry/hours/initial_state in `config.py`; removes parallel transitions list |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env splits |
| astral.debug.spikes-under-debug-dir | conforms | Feature plan path, not spike docs |
| astral.docs.features-single-file-per-ticket | conforms | Plan at `docs/features/candidate/ast-970-….md` |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src/docs plan |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O; core owns transition policy |
| astral.layers.import-direction | conforms | Files stay utils/core/ui; no illegal imports |
| astral.layers.ui-config-driven-business-logic | conforms | Nav/`progress_rank` resolved via config + API helper |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new open endpoints |
| astral.standards.data-raises-caller-logs | conforms | ValueError in core; UI → 400 |
| astral.standards.debug-contract-gated | conforms | No new debug-contract lines specified |
| astral.standards.dry-and-focused-functions | conforms | Mirrors job prior_states helpers; single registry |
| astral.standards.in-scope-only | conforms | Sibling history/dispatch/migration explicitly out |
| astral.standards.logging-via-utils | conforms | No print/bare logging added |
| astral.standards.no-cross-contamination | conforms | Layered files only |
| astral.standards.no-hardcoded-sets | conforms | States/hours in config; assert guards |
| astral.standards.public-then-helpers | conforms | Public transition/aging + private prior helpers |
| astral.standards.utils-data-late-import-only | conforms | Config-only utils edits |
| astral.state.core-decides-transitions | conforms | Core enforces; data still receives target state |
| astral.state.job-prior-states-enforced | conforms | Candidate mirrors job prior_states; does not weaken job enforcement |
| astral.state.no-daisy-chain-in-run | conforms | Retires auto PROFILE/CONTEXT hops; no multi-state run chain |
| astral.ui.naming-conventions | conforms | No new frontend files |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** all rows in Statute verdicts above (51).

**Excluded:**
- `astral.debug.no-repo-root-artifacts-dir` — paths miss plan paths
- `astral.git.engineer-test-tree-ban` — paths miss plan paths
- `astral.layers.scripts-exempt-from-layer-rules` — layers/paths miss (no scripts)
- `astral.standards.database-header-inventory` — layers/paths miss (no `src/data/**`)
- `astral.ui.frontend-file-placement` — paths miss (`src/ui/frontend/**`)

## Findings

### fix-now
1. **Location:** Stage 1 registry — `ALL_TOPICS_READY.prior_states`
   **Finding:** Priors are `REQUIRED_TOPICS_READY`, `ALL_TOPICS_READY_STALE` only. After AC#4 ages a row to `REQUIRED_TOPICS_READY_STALE`, a manual (or future Topic Menu) hop to `ALL_TOPICS_READY` is rejected. Every other forward hop in this registry includes the prior stage’s `*_STALE` companion; this one does not — happy path breaks after stale aging.
   **Recommendation:** Add `REQUIRED_TOPICS_READY_STALE` to `ALL_TOPICS_READY.prior_states` (and re-scan the graph once for any other missing stale→next edges).

### discuss
1. **`REQUESTED_*_ERROR` exits:** Error companions have no forward prior into retry/ready (only INACTIVE/DELETED unrestricted escape). Confirm intentional for v1 vs add `*_ERROR` → `*_RETRY` / re-request priors (likely matters for AST-972).
2. **Stale/reap hour defaults (72 / 168 / 720):** Flagged Decision; Susan did not specify numbers. Leave as config knobs after a quick product nod, or set different literals.
3. **AC#4 vs AST-972:** Aging helper lands here; scheduler/dispatch invocation is sibling. Acceptable given boundaries — do not register a dispatch task in AST-970.

### acceptable
- HIGH risk + leaving DB remaps to AST-973 is honest; fail-closed + `progress_rank=-1` for terminals is sound.
- Reap metadata on `candidate_data.lifecycle` (no new SQL column) fits Boundaries (no data-layer schema work).
- Config-local NAV/`gen_states`/`INFLOW` string updates vs full consumer sweep (AST-973) matches child Boundaries.

**Self-assessment:** MAJOR-CHANGE / high / HIGH — honest; HIGH does not alone force escalate given concrete job-mirror plan + clear sibling cuts.

Update the plan doc on the publish ref, then return to Plan Ready / re-assign Joan for re-validate.

— Joan
context_tokens≈52000

#### joan — 2026-07-23T23:02:25.519Z
[validate-plan] blocked — assignee gate

Status is **Plan Ready**, but assignee is **Ada Lovelace**, not Joan.

Chuckles must assign **Joan** (`susan+joan@susansomerset.com`) before validate-plan runs. No rubric pass until then.

— Joan
context_tokens≈12000

#### ada — 2026-07-23T22:58:30.341Z
Plan published on `origin/sub/AST-871/AST-970-candidate-state-registry` @ `1b5dc11`.

**Plan:** [docs/features/candidate/ast-970-candidate-state-registry.md](https://github.com/susansomerset/astral/blob/sub/AST-871/AST-970-candidate-state-registry/docs/features/candidate/ast-970-candidate-state-registry.md)

**Self-assessment**
- **Scope:** MAJOR-CHANGE — replaces candidate vocabulary + `prior_states` enforcement in config/core (thin API/`progress_rank` helper); history, dispatch claim, and legacy migration stay with AST-971/972/973.
- **Conf:** high — mirrors `JOB_STATES` / `transition_job_state`; registry, DELETED reap start, and stale-aging helper are spelled out call-site by call-site.
- **Risk:** HIGH — wrong priors or retiring auto `PROFILE_READY`/`CONTEXT_READY` hops can block onboarding until AST-973 remaps rows; fail-closed transitions + `progress_rank=-1` for INACTIVE/DELETED mitigate nav leaks.

Note: shared epic worktree raced onto AST-971 mid-commit; follow-up commit dropped the sibling plan file from this publish tip so tree content is AST-970-only (history still contains that sibling commit until a later clean rewrite if wanted).

---

# Candidate state registry and transitions (Candidate state machine)

**Linear:** [AST-970](https://linear.app/astralcareermatch/issue/AST-970/candidate-state-registry-and-transitions-candidate-state-machine)  
**Parent:** [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine)  
**Publish ref:** `origin/sub/AST-871/AST-970-candidate-state-registry`

Replace the four-step candidate lifecycle (`NEW` → `PROFILE_READY` → `CONTEXT_READY` → `LIVE_PROMPTS` + `DELETED`) with a config-backed registry aligned to the job-style `prior_states` machine: full runtime vocabulary (no `PROSPECT`), stale/retry/error companions, `INACTIVE` + `DELETED` (DELETED starts a configured reap timer), and enforced transitions. Manual hops into topic-ready stages are allowed. Does **not** own transition history (AST-971), dispatch claim / scheduler wiring (AST-972), or legacy row / FK / consumer migration (AST-973).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Replace `CANDIDATE_STATES` with job-style registry (`prior_states`, companions, stale/reap metadata); remove `ASTRAL_CONFIG["candidate_state_transitions"]`; add `CANDIDATE_CONFIG` reap default; update config-local gates that assert membership (`NAV_CONFIG` visible keys, `build_state_ui_manifest` gen_states, `INFLOW_CONFIG` candidate search trigger) so `config.py` imports cleanly | utils |
| `src/core/candidate.py` | Rewrite `transition_candidate_state` to enforce `prior_states`; route `delete_candidate` through DELETED transition + reap timer start; create path uses `NEW_CANDIDATE`; retire auto hops to `PROFILE_READY` / `CONTEXT_READY`; add stale-aging helper; add reap-due helpers | core |
| `src/ui/api/api_system.py` | `_is_at_or_past` uses optional `progress_rank` on `CANDIDATE_STATES` (INACTIVE/DELETED do not unlock gated nav) | ui |
| `src/ui/api/api_candidate.py` | Admin state override goes through `transition_candidate_state` (fail closed); `/states` unchanged shape (list of keys) | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Replace state-machine section with new vocabulary + prior_states pointer | docs |
| `docs/ASTRAL_CODE_RULES.md` | Update §2.1 `CANDIDATE_STATES` bullet and §2.6.3 Candidates narrative to the new registry (no parallel hardcoded sets) | docs |

**Out of scope (siblings):** history table/writes (AST-971); dispatcher claim of `REQUESTED_*` / invoking aging on a schedule (AST-972); DB row remap, `dispatch_task` FK remap, full nav/UI consumer sweep beyond config-local string updates listed above (AST-973).

## Stage 1: Config registry — vocabulary, prior_states, companions

**Done when:** `CANDIDATE_STATES` contains every runtime key below with `prior_states` / companion metadata; `ASTRAL_CONFIG["candidate_state_transitions"]` is gone; `python -c "from src.utils.config import CANDIDATE_STATES"` succeeds; `PROSPECT` is absent.

1. In `src/utils/config.py`, replace the `CANDIDATE_STATES` block (currently `NEW` / `PROFILE_READY` / `CONTEXT_READY` / `LIVE_PROMPTS` / `DELETED`) with the registry below. Preserve insertion order exactly as listed (happy path, then terminals). Every entry must include `progress_rank` (int) for nav gating.

```
# progress_rank: happy-path depth; companions share the primary's rank;
# INACTIVE/DELETED use -1 so they never satisfy "at or past" gates.

NEW_CANDIDATE              prior_states=None, progress_rank=0
INTAKE_INITIATED           prior_states=["NEW_CANDIDATE"], progress_rank=1
REQUIRED_TOPICS_READY      prior_states=["INTAKE_INITIATED", "REQUIRED_TOPICS_READY_STALE"],
                           stale_after_hours=72, stale_state="REQUIRED_TOPICS_READY_STALE",
                           progress_rank=2
REQUIRED_TOPICS_READY_STALE prior_states=["REQUIRED_TOPICS_READY"], progress_rank=2
ALL_TOPICS_READY           prior_states=["REQUIRED_TOPICS_READY", "REQUIRED_TOPICS_READY_STALE",
                                         "ALL_TOPICS_READY_STALE"],
                           stale_after_hours=72, stale_state="ALL_TOPICS_READY_STALE",
                           progress_rank=3
ALL_TOPICS_READY_STALE     prior_states=["ALL_TOPICS_READY"], progress_rank=3
REQUESTED_RESUME           prior_states=["ALL_TOPICS_READY", "ALL_TOPICS_READY_STALE",
                                         "REQUESTED_RESUME_RETRY"],
                           retry_state="REQUESTED_RESUME_RETRY",
                           error_state="REQUESTED_RESUME_ERROR",
                           progress_rank=4
REQUESTED_RESUME_RETRY     prior_states=["REQUESTED_RESUME"], progress_rank=4
REQUESTED_RESUME_ERROR     prior_states=["REQUESTED_RESUME", "REQUESTED_RESUME_RETRY"],
                           progress_rank=4
RESUME_READY               prior_states=["REQUESTED_RESUME", "REQUESTED_RESUME_RETRY",
                                         "RESUME_READY_STALE"],
                           stale_after_hours=168, stale_state="RESUME_READY_STALE",
                           progress_rank=5
RESUME_READY_STALE         prior_states=["RESUME_READY"], progress_rank=5
REQUESTED_ARTIFACTS        prior_states=["RESUME_READY", "RESUME_READY_STALE",
                                         "REQUESTED_ARTIFACTS_RETRY"],
                           retry_state="REQUESTED_ARTIFACTS_RETRY",
                           error_state="REQUESTED_ARTIFACTS_ERROR",
                           progress_rank=6
REQUESTED_ARTIFACTS_RETRY  prior_states=["REQUESTED_ARTIFACTS"], progress_rank=6
REQUESTED_ARTIFACTS_ERROR  prior_states=["REQUESTED_ARTIFACTS", "REQUESTED_ARTIFACTS_RETRY"],
                           progress_rank=6
ARTIFACTS_READY            prior_states=["REQUESTED_ARTIFACTS", "REQUESTED_ARTIFACTS_RETRY",
                                         "ARTIFACTS_READY_STALE"],
                           stale_after_hours=168, stale_state="ARTIFACTS_READY_STALE",
                           progress_rank=7
ARTIFACTS_READY_STALE      prior_states=["ARTIFACTS_READY"], progress_rank=7
ACTIVE_SEARCH              prior_states=["ARTIFACTS_READY", "ARTIFACTS_READY_STALE",
                                         "PAUSE_SEARCH"],
                           progress_rank=8
PAUSE_SEARCH               prior_states=["ACTIVE_SEARCH"], progress_rank=8
INACTIVE                   prior_states=None, progress_rank=-1
DELETED                    prior_states=None, progress_rank=-1,
                           reap_after_hours=720
```

⚠️ **Decision:** Align candidate enforcement to job-style `prior_states` on the registry (not a parallel `candidate_state_transitions` tuple list). Jobs already deleted `job_state_transitions`; candidates follow the same pattern so AST-971/972 can share mental model with `transition_job_state`.

⚠️ **Decision:** Stale hours are literals in config (72h topic-ready waits, 168h resume/artifacts ready waits; DELETED reap 720h / 30d). Susan did not specify numbers — these are product defaults / config knobs; change only in `config.py` later (no code change required).

⚠️ **Decision:** `INACTIVE` and `DELETED` use `prior_states=None` (unrestricted entry from any current state), matching unrestricted job terminal patterns. Disallowed hops still fail when `to_state` is missing from the registry.

⚠️ **Decision (stale→next edges):** Every waiting stage’s `*_STALE` companion must appear in the **next** happy-path state’s `prior_states` (not only recover-to-primary). Graph check: `REQUIRED_TOPICS_READY_STALE` → `ALL_TOPICS_READY`; `ALL_TOPICS_READY_STALE` → `REQUESTED_RESUME`; `RESUME_READY_STALE` → `REQUESTED_ARTIFACTS`; `ARTIFACTS_READY_STALE` → `ACTIVE_SEARCH`. No other waiting stages exist in this registry.

⚠️ **Decision (ERROR exits, v1):** `REQUESTED_RESUME_ERROR` / `REQUESTED_ARTIFACTS_ERROR` do **not** list forward priors into retry/ready. Escape is via unrestricted `INACTIVE` / `DELETED` only. AST-972 may propose `*_ERROR` → `*_RETRY` / re-request edges later; do not add them in AST-970.

⚠️ **Decision (AC#4 vs AST-972):** `age_stale_candidate_states` lands in this ticket; do **not** register a dispatch task or scheduler hook here — AST-972 owns invocation.

2. Add a small `CANDIDATE_CONFIG` dict immediately after `CANDIDATE_STATES` with a single key used as documentation/default mirror (do not fork per-state hours here):

```python
CANDIDATE_CONFIG = {
    # Per-state stale_after_hours / DELETED reap_after_hours live on CANDIDATE_STATES entries.
    # This block holds only cross-cutting candidate lifecycle knobs that are not per-state.
    "initial_state": "NEW_CANDIDATE",
}
```

3. Delete the entire `ASTRAL_CONFIG["candidate_state_transitions"]` key and its comment block (the three-tuple list under `# --- Candidate state machine`).

4. Config-local string updates required for import/assert coherence (not the full consumer sweep — that is AST-973):
   - `NAV_CONFIG`: change group `"visible": "LIVE_PROMPTS"` → `"ACTIVE_SEARCH"` (Jobs, Companies); `"visible": "CONTEXT_READY"` → `"RESUME_READY"` (Artifacts).
   - In `build_state_ui_manifest`, set `gen_states = ["RESUME_READY", "ACTIVE_SEARCH"]` (must remain keys ⊆ `CANDIDATE_STATES`).
   - `INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]`: `"LIVE_PROMPTS"` → `"ACTIVE_SEARCH"` (candidate search-ready gate name only; AST-972 owns claim wiring).

5. Update the module header comment that lists `CANDIDATE_STATES` so it describes prior_states / companions, not the four-step list.

6. Add a module-level assert after `CANDIDATE_STATES` is defined:

```python
assert "PROSPECT" not in CANDIDATE_STATES
for _name, _cfg in CANDIDATE_STATES.items():
    assert "progress_rank" in _cfg, _name
    assert "prior_states" in _cfg, _name
    _stale = _cfg.get("stale_state")
    if _stale is not None:
        assert _stale in CANDIDATE_STATES and "stale_after_hours" in _cfg, _name
    _retry = _cfg.get("retry_state")
    if _retry is not None:
        assert _retry in CANDIDATE_STATES, _name
    _err = _cfg.get("error_state")
    if _err is not None:
        assert _err in CANDIDATE_STATES, _name
assert CANDIDATE_STATES["DELETED"].get("reap_after_hours", 0) > 0
assert CANDIDATE_CONFIG["initial_state"] in CANDIDATE_STATES
```

## Stage 2: Enforced transitions, DELETED reap start, stale aging helper

**Done when:** Illegal hops raise `ValueError`; happy-path and documented side-path hops succeed; entering `DELETED` records reap metadata from config; `age_stale_candidate_states` moves due waiting rows to their `stale_state`; create/delete/admin paths no longer write retired state names.

1. In `src/core/candidate.py`, add helpers next to the existing `_CANDIDATE_STATE_LIST` usage:

```python
def _candidate_prior_states(to_state: str):
    cfg = CANDIDATE_STATES.get(to_state)
    if cfg is None:
        raise ValueError(f"Unknown candidate state: {to_state}")
    return cfg.get("prior_states")

def _candidate_state_allowed(from_state: str, to_state: str) -> bool:
    prior = _candidate_prior_states(to_state)
    if prior is None:
        return True
    return from_state in prior
```

2. Rewrite `transition_candidate_state(candidate_id, to_state)`:
   - Load candidate; raise if missing.
   - If `to_state not in CANDIDATE_STATES`: raise `ValueError`.
   - If not `_candidate_state_allowed(from_state, to_state)`: raise `ValueError` with message `Invalid candidate state transition: {from} -> {to}`.
   - Call `database.save_candidate(candidate_id, state=to_state)`.
   - If `to_state == "DELETED"`: call `_start_candidate_reap_timer(candidate_id)` (step 3).
   - Do **not** write transition history here (AST-971).

3. Add `_start_candidate_reap_timer(candidate_id)`:
   - Read `hours = CANDIDATE_STATES["DELETED"]["reap_after_hours"]`.
   - Merge into `candidate_data`:

```python
{"lifecycle": {"reap_after_hours": hours, "reap_started_at": <UTC ISO8601 now>}}
```

   - Use existing `database.save_candidate(..., candidate_data=..., merge=True)`.
   - ⚠️ **Decision:** Persist reap start on `candidate_data.lifecycle` (no new SQL column). Due time is `reap_started_at + reap_after_hours`. Hard-delete executor and production purge of already-DELETED rows are AST-973; this ticket only starts the timer.

4. Add public helpers (no scheduler wiring):

```python
def candidate_reap_due_at(candidate: dict) -> Optional[datetime]:
    """Return UTC due datetime when state is DELETED and lifecycle.reap_started_at is set; else None."""

def is_candidate_reap_due(candidate: dict, *, now: Optional[datetime] = None) -> bool:
    """True when DELETED and now >= candidate_reap_due_at."""
```

5. Rewrite `delete_candidate(candidate_id)` to call `transition_candidate_state(candidate_id, "DELETED")` instead of bypassing validation. Because `DELETED.prior_states is None`, any current state may enter DELETED.

6. Create path (`initiate` / create currently `state="NEW"`): write `state=CANDIDATE_CONFIG["initial_state"]` (`NEW_CANDIDATE`).

7. In `parse_candidate_resume`: **remove** the block that transitions `NEW` → `PROFILE_READY`. After save of resume artifacts, leave state unchanged.
   ⚠️ **Decision:** Legacy auto-progress into `PROFILE_READY` is retired. Intake / operators move `NEW_CANDIDATE` → `INTAKE_INITIATED` (and later topic-ready) via explicit transitions; Topic Menu (AST-953) will later automate topic-ready.

8. Rewrite `check_context_complete(candidate_id)`:
   - Keep the four context-field completeness check.
   - **Do not** call `transition_candidate_state(..., "CONTEXT_READY")` (state retired).
   - Return `True` when all four fields are non-empty; `False` otherwise.
   - Remove `_CONTEXT_READY_IDX` / slice-based “already past CONTEXT_READY” short-circuit that indexes retired names. Optional: if `progress_rank` of current state is `>= CANDIDATE_STATES["ALL_TOPICS_READY"]["progress_rank"]` and current rank >= 0, return `True` without re-checking fields (context already accepted further along the path).

9. Add `age_stale_candidate_states(*, now: Optional[datetime] = None) -> int`:
   - Load all non-deleted candidates via existing list/get helpers (include only rows whose `state` is a key in `CANDIDATE_STATES` with both `stale_after_hours` and `stale_state`).
   - For each, if `state_changed_at` (or equivalent timestamp already on the row) is older than `stale_after_hours`, call `transition_candidate_state(id, stale_state)`.
   - Skip rows whose current state is already the stale companion.
   - Return count of successful transitions.
   - ⚠️ **Decision:** Aging logic lives in core here (AC #4). AST-972 owns calling this from dispatch/scheduler and claiming `REQUESTED_*` batches — do not register a dispatch task in this ticket.

10. In `src/ui/api/api_candidate.py`, when admin supplies `state` override, call `transition_candidate_state(candidate_id, state_override)` instead of `save_candidate_admin(..., state=...)`. On `ValueError`, return 400 with the error message. Non-state admin fields still use `save_candidate_admin`.

11. In `src/ui/api/api_system.py`, change `_is_at_or_past` to compare `progress_rank`:

```python
def _progress_rank(state: str) -> int:
    cfg = CANDIDATE_STATES.get(state) or {}
    return int(cfg.get("progress_rank", -1))

def _is_at_or_past(current_state: str, required_state: str) -> bool:
    return _progress_rank(current_state) >= _progress_rank(required_state) and _progress_rank(current_state) >= 0
```

Remove the old `_STATE_INDEX` enumeration if unused.

## Stage 3: Docs — data model + Code Rules narrative

**Done when:** `CANDIDATE_DATA_MODEL.md` and Code Rules §2.1 / §2.6.3 describe the new registry; no doc still teaches the four-step machine as current truth in those two places.

1. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, replace the **State machine** section with:
   - Runtime keys listed in Stage 1 (explicitly: no `PROSPECT`).
   - Note that transitions are enforced via `CANDIDATE_STATES[*].prior_states` in `transition_candidate_state`.
   - Note manual topic-ready hops until AST-953.
   - Note DELETED reap: `candidate_data.lifecycle.reap_started_at` + `reap_after_hours` from registry.
   - Point legacy migration to AST-973.

2. In `docs/ASTRAL_CODE_RULES.md`:
   - §2.1 bullet **CANDIDATE_STATES**: replace the four-step description with “Candidate state registry; each entry has `prior_states` (list or `None`), optional `stale_after_hours`/`stale_state`, optional `retry_state`/`error_state`, `progress_rank`; `DELETED` carries `reap_after_hours`. No `PROSPECT`.”
   - §2.6.3 Candidates: replace the simple progression + `candidate_state_transitions` text with prior_states enforcement via `transition_candidate_state`, list the happy path `NEW_CANDIDATE` → … → `ACTIVE_SEARCH`, and note companions + INACTIVE/DELETED. Remove `CONTEXT_READY` / `check_context_complete` as the gate for a state transition (completeness helper may remain; it does not write state).

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — replaces the candidate state vocabulary and enforcement path in config + core + thin API/nav rank helper; docs updated to match. Sibling tickets still own history, dispatch claim, and legacy data migration.

**Conf:** `high` — mirrors existing `JOB_STATES` / `transition_job_state` patterns; ticket boundaries and parent AC are explicit; concrete registry and call-site rewrites are specified.

**Risk:** `HIGH` — wrong `prior_states` or premature removal of legacy auto-transitions can block onboarding or unlock nav incorrectly until AST-973 migrates rows; mitigated by fail-closed validation, `progress_rank` for INACTIVE/DELETED, and leaving DB remaps to AST-973.

## Code Rules self-review

| Rule | Result |
|------|--------|
| §1.3 DRY | Single registry in config; no duplicate transition tuple list |
| §2.1 config SSOT | All state names, stale hours, reap hours, initial state in config |
| §2.4 batch | No new batch claim APIs (AST-972) |
| §2.6 state machine | Core decides transitions; data layer still receives target state only; prior_states enforced in core like jobs |
| §3.3 imports | Helpers stay in `candidate.py` / `config.py`; no new cross-layer violations |
| §3.5 naming | UPPERCASE state keys; snake_case config keys |

No unresolved conflicts. Code Rules narrative update is Stage 3 (required so §2.6.3 does not contradict the shipped registry).

## Revisions

Revision 1 — 2026-07-23
Driven by: Joan `[plan-discuss] round=1 concern` fix-now — `ALL_TOPICS_READY.prior_states` omitted `REQUIRED_TOPICS_READY_STALE`, so happy path broke after stale aging.
Changes:
- Added `REQUIRED_TOPICS_READY_STALE` to `ALL_TOPICS_READY.prior_states`.
- Documented full stale→next graph check (four edges); no other missing edges found.
- Recorded Decisions for ERROR exits (v1 closed; AST-972 may extend), hour literals as config knobs, and AC#4 helper vs AST-972 scheduler ownership.

## Review

| Field | Value |
| -- | -- |
| Ticket | AST-970 |
| Publish ref | `origin/sub/AST-871/AST-970-candidate-state-registry` |
| Built | `5e0a8856678efff89a917a4d19e3de8bc56f6406` |
| Notes | Stages 1–3 implemented per plan (registry, transitions/reap/stale, docs). |

### Radia code-rubric.v1 (revision=1)

**Overall:** DISCUSS  
**Publish tip reviewed:** `5a75bdc87a52131c8041bc5c738612b18158efc3` (`origin/dev...origin/sub/AST-871/AST-970-candidate-state-registry`)

**What’s solid**
- Job-style `CANDIDATE_STATES` registry (no `PROSPECT`), `prior_states` enforcement, DELETED reap start on `candidate_data.lifecycle`, `age_stale_candidate_states` without scheduler wiring.
- Admin state override fail-closed via `transition_candidate_state`; `progress_rank` gates terminals.
- Sibling boundaries held (no history table, no dispatch claim, no legacy remap).

**Issues**
- **discuss (C4 straggler):** Joan excluded `astral.git.engineer-test-tree-ban` at plan time; Betty’s `test`/`merge-tests` land on the tip so the statute is in-scope. Substance **conforms** (engineers did not edit test-tree in `code` commits).
- **advisory:** `CANDIDATE_DATA_MODEL.md` context section still says four fields “gate the `CONTEXT_READY` state transition” while the State machine section is updated.

**Recommended actions**
- Engineer: acknowledge straggler / no product change required for it; optional one-line doc cleanup on the CONTEXT_READY leftover (or leave for AST-973 consumer sweep).

## Resolution

2026-07-24 — Radia code-rubric.v1 revision=1 (**DISCUSS**; fix-now none).

| Finding | Action |
| -- | -- |
| discuss — C4 `engineer-test-tree-ban` straggler | Acknowledged: Betty owns tip `tests/**` + bible; engineer `code`/`docs` commits did not touch test-tree. No product change. |
| advisory — `CONTEXT_READY` leftover in data-model context section | One-line cleanup in `CANDIDATE_DATA_MODEL.md`: completeness helper, not a state-transition gate. |
