<!-- linear-archive: AST-972 archived 2026-08-05 -->

## Linear archive (AST-972)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-972/dispatch-and-stale-eligibility-for-candidate-stages-candidate-state  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-871 — Candidate state machine  
**Blocked by / blocks / related:** parent: AST-871

### Description

## What this implements

Wire REQUESTED_RESUME / REQUESTED_ARTIFACTS (and stale aging) so dispatch can claim and resolve to ready/retry/error; ACTIVE_SEARCH as the sole company/job search-ready gate.

## Acceptance criteria

5. REQUESTED_RESUME and REQUESTED_ARTIFACTS are claimable by dispatch and can move to ready, retry, or error companions as appropriate.
6. ACTIVE_SEARCH is the only candidate state that qualifies a candidate for company/job search dispatch (replacing LIVE_PROMPTS).

## Boundaries

Does **not** own craft prompts, daisy-chain generation, Topic Menu, or bulk FK remaps (sibling: Legacy candidate migration).

## Notes for planning

Depends on AST-970 state vocabulary. ACTIVE_SEARCH replaces LIVE_PROMPTS for search dispatch eligibility.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-871-candidate-state-machine`, child `sub/AST-871/<this-id>-dispatch-stale-eligibility`. Created at dispatch-parent.

### Comments

#### betty — 2026-07-24T00:59:35.502Z
[merge-child] blocked: git pull merge on sub — `Merge remote-tracking branch` in ftr..sub (aee8912). Rewrite tip onto `origin/ftr/AST-871-candidate-state-machine`, cherry-pick only AST-972 labeled commits, force-with-lease push `origin/sub/AST-871/AST-972-dispatch-stale-eligibility`. @Katherine Johnson

— Chuckles

#### radia — 2026-07-24T00:24:19.648Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-972
**Publish ref:** `origin/sub/AST-871/AST-972-dispatch-stale-eligibility` @ `582b6501b433733dbc08342bdfe22bee6aabcfd0`
**Overall:** FIX-NOW

Diff: `origin/dev...origin/sub/AST-871/AST-972-dispatch-stale-eligibility` — layers `core`/`data`/`utils`/`ui`/`docs` (+ Betty tests/bible; blockedBy AST-970).

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-972)` of `ceeb114` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` / merge blockedBy |
| orch.git.flow-direction-inviolable | universal | conforms | Child publish on `sub/AST-871/…` |
| orch.git.ftr-sub-topology | universal | conforms | Under parent AST-871 |
| orch.git.merge-on-checkout | universal | conforms | `origin/dev` + blockedBy 970 merges on tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | No agent long-lived branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree `astral-AST-871` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Craft fan-in + provision Decisions recorded |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–5 match plan bible |
| orch.pipeline.project-scoped-queues | universal | conforms | Untouched |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No `canon/statutes/**` edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty `test`/`merge-tests` own bible+tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Path ownership respected across commits |
| astral.agent.confidence-bounds | scoped | conforms | No graded/confidence surface |
| astral.agent.do-task-delegation | scoped | conforms | Craft via existing `do_task` |
| astral.agent.grade-vector-validation | scoped | conforms | No grade vectors |
| astral.batch.batch-id-first | scoped | conforms | Single-candidate ctx claim model retained |
| astral.batch.batch-id-format | scoped | conforms | No new mint rules |
| astral.batch.claim-process-release | scoped | conforms | Claim gate + workers; no pool claim |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | `CANDIDATE_STAGE_DISPATCH` + TASK_CONFIG keys |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env splits |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan under `docs/features/**` |
| astral.docs.features-single-file-per-ticket | scoped | conforms | AST-972 plan in `docs/features/candidate/` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits are test-tree only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code`/`docs` leave tests/bible to Betty |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No new external I/O |
| astral.layers.import-direction | scoped | violates | `_tick_loop` late-imports `candidate.age_stale_candidate_states` with no cycle-break comment |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Tip UI/config from AST-970; no React rule duplication |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Routes stage workers via consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | No new open endpoints |
| astral.standards.data-raises-caller-logs | scoped | conforms | Count/eligibility stay in data; core decides hops |
| astral.standards.database-header-inventory | scoped | conforms | No new tables/columns |
| astral.standards.debug-contract-gated | scoped | conforms | Workers accept `debug` and pass through to `do_task` |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses claim_states + AST-970 aging + persist helper |
| astral.standards.in-scope-only | scoped | conforms | Vocabulary/prompts/daisy-chain/LIVE_PROMPTS remap left to siblings |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger`; provision failure logged |
| astral.standards.no-cross-contamination | scoped | conforms | Layered files only |
| astral.standards.no-hardcoded-sets | scoped | conforms | Craft lists + triggers in config |
| astral.standards.public-then-helpers | scoped | conforms | Public stage workers + ensure/provision helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | Config-only utils |
| astral.state.core-decides-transitions | scoped | conforms | Workers call `transition_candidate_state` only |
| astral.state.job-prior-states-enforced | scoped | conforms | Extends claim_states for candidate registry |
| astral.state.no-daisy-chain-in-run | scoped | conforms | One registered-state hop per claim; craft fan-in ≠ state daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | paths miss |
| astral.ui.naming-conventions | scoped | conforms | No new frontend product files |
| astral.ui.single-gunicorn-worker | scoped | conforms | Tick + `start_scheduler` provision only |

## Pattern conformance

none cited

## Plan adherence

Stages 1–5 match: config + claim helpers; provision rows from `start_scheduler`; eligibility/claim gate; resume/artifacts workers + consult routes; tick aging. Self-Assessment Single-Component / high / Medium matches. Joan APPROVED @ `3e19b2d`.

## Findings

### fix-now
1. **Location:** `src/core/dispatcher.py` `_tick_loop`
   **Finding:** Late `from src.core.candidate import age_stale_candidate_states` has no in-code comment. Candidate already imports dispatcher at module top — late import is the right cycle break, but B1 / CODE_RULES require a short why comment on function-scoped imports.
   **Recommendation:** Add e.g. `# late: avoid cycle with candidate → dispatcher` above the import (or hoist only if the cycle is proven gone).

### discuss
1. **C4 stragglers** — Joan Excluded at plan time; tip brings them in-scope: `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.ui.naming-conventions`. Scored **conforms**. Acknowledge on resolve.

### advisory
1. `start_scheduler` provision failure uses bare `except Exception` but logs via `_sched_log.exception` — acceptable mitigation.
2. CREATE candidate `state … DEFAULT 'NEW'` remains for AST-973.

## What’s solid

- AC5/AC6 wiring: provisioned REQUESTED_* rows, claim gate, ready/retry/error workers, ACTIVE_SEARCH inflow gate from AST-970, tick-driven aging.

## Notes

Joan Excluded otherwise still `not-applicable`: `no-repo-root-artifacts-dir`, `scripts-exempt`, `frontend-file-placement`.

— Radia
context_tokens≈105000

#### betty — 2026-07-23T23:55:05.898Z
1. **Publish:** `origin/sub/AST-871/AST-972-dispatch-stale-eligibility` @ `5b69e41` (`merge-tests(AST-972): origin/tests ceeb114`)
2. **Tests SHA:** `ceeb114` — `test(AST-972): stage dispatch eligibility, workers, and ACTIVE_SEARCH gate`
3. **Coverage**
   - Config: `CANDIDATE_STAGE_DISPATCH`, claim states (+ retry), trigger/entity helpers
   - Dispatcher: ensure/provision idempotent; candidate claim gate; tick → `age_stale_candidate_states`; `start_scheduler` provision
   - Workers: resume/artifacts success → ready; primary fail → retry; retry fail → error
   - Consult routes `candidate_requested_*` to workers
   - Data: stage-key eligibility 1/0; inflow still `ACTIVE_SEARCH` + `task_key=inflow_discovery`
4. **Revised (broken by tip):** dispatcher + `test_dispatch_tasks` `LIVE_PROMPTS` → `ACTIVE_SEARCH`; invalid candidate fixture `NEW` → `NEW_CANDIDATE`; AST-525 missing `task_key`; AST-875 template key → `qualify_job_listings`; HOMEPAGE claim expects WFR union
5. **Manifest**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst972CandidateStageDispatch \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch \
  tests/component/core/test_dispatcher.py::TestScheduler \
  tests/component/core/test_candidate.py::TestAst972RequestedStageDispatch \
  tests/component/core/test_consult.py::TestAst972CandidateStageConsultRouting \
  tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility \
  tests/component/data/database/test_dispatch_tasks.py::TestAst525InflowDiscoveryEligible \
  tests/component/data/database/test_dispatch_tasks.py::TestAst802InflowDiscoveryEligible \
  -q
```
6. **Bible shasums** (on publish tip)
   - `d7ad6778d15f9b4c8f0f979ce03e0a094cdeb66569b8480531a9f03246978083` `docs/test-bible/core/candidate.md`
   - `8bd0d0ace174fc7d2d5a6de504253971d8ab6be32539d4b1dacdc5103148fa17` `docs/test-bible/core/dispatcher.md`
   - `236e7ae0ae3c7175a0e8d22874b3552354b6d35c490f7fde087c48ff6aeb40c4` `docs/test-bible/core/consult.md`
   - `b6a084acd828b4b5436592cd63de587420e16259c32ef974ddd5e093341bf963` `docs/test-bible/utils/config.md`
   - `e4b9fa710119dd409c3fcd69614eac31218bdef2e51507425fa665e41fa90a3b` `docs/test-bible/data/database/dispatch_tasks.md`

— Betty

#### joan — 2026-07-23T23:23:13.326Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-972
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-871/AST-972-dispatch-stale-eligibility` @ `3e19b2d`
**Implementer:** Katherine Johnson
**Plan Discuss:** round 1 completed (concern + reply); fix-now closed

## Traceability

### Parent / child AC → plan stages

| AC | Coverage |
| -- | -- |
| **#5** REQUESTED_RESUME / REQUESTED_ARTIFACTS claimable; resolve ready/retry/error | Stage 1 config; Stage 2 `dispatch_task` provisioning; Stage 3 eligibility/claim gate; Stage 4 workers + consult route |
| **#6** ACTIVE_SEARCH sole company/job search gate | Prerequisite AST-970 INFLOW flip + Stage 3 claim gate |
| Stale aging invocation | Stage 5 tick → `age_stale_candidate_states` |
| Parent AC 1–4, 7–10 | N/A — Boundaries |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Config stage-dispatch + claim helpers | Dispatch-triggering stages; config SSoT |
| 2 Provision REQUESTED_* dispatch_task rows | AC#5 claimability (DB SSOT) |
| 3 Eligibility + claim gate | ACTIVE_SEARCH search gate; REQUESTED_* claim |
| 4 Workers + consult routing | ready/retry/error; named craft helpers |
| 5 Tick aging | Waiting-stage stale activation |
| 6 Smoke / CC | Gate hygiene |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge SHA work |
| orch.git.commit-vocabulary | conforms | Plan-only |
| orch.git.flow-direction-inviolable | conforms | Child sub publish ref |
| orch.git.ftr-sub-topology | conforms | Under ftr AST-871 |
| orch.git.merge-on-checkout | conforms | Merge AST-970 prerequisite |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrites |
| orch.git.no-dev-agent-branches | conforms | No agent branches |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Craft fan-in Decision clear; helpers named |
| orch.pipeline.plan-is-bible | conforms | Plan on publish ref |
| orch.pipeline.project-scoped-queues | conforms | Untouched |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready re-validate after discuss |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Katherine |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Katherine on APPROVED |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No grades |
| astral.agent.do-task-delegation | conforms | Craft via `do_task` |
| astral.agent.grade-vector-validation | conforms | N/A |
| astral.batch.batch-id-first | conforms | Single-candidate ctx claim model |
| astral.batch.batch-id-format | conforms | No new mint rules |
| astral.batch.claim-process-release | conforms | Matches current candidate claim pattern |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | CANDIDATE_STAGE_DISPATCH + TASK_CONFIG keys |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned |
| astral.layers.core-vs-external-bright-line | conforms | No new external I/O |
| astral.layers.import-direction | conforms | utils/data/core only |
| astral.layers.ui-config-driven-business-logic | conforms | No React rule duplication |
| astral.patterns.coat-check-never-store-empty | conforms | N/A |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Routes via consult |
| astral.standards.data-raises-caller-logs | conforms | Count helpers stay data |
| astral.standards.database-header-inventory | conforms | No new tables/columns |
| astral.standards.debug-contract-gated | conforms | Workers accept debug flag |
| astral.standards.dry-and-focused-functions | conforms | Reuses claim_states + AST-970 aging |
| astral.standards.in-scope-only | conforms | No vocabulary/prompts/daisy-chain/nav remaps |
| astral.standards.logging-via-utils | conforms | No print paths |
| astral.standards.no-cross-contamination | conforms | Layered files |
| astral.standards.no-hardcoded-sets | conforms | Craft lists + triggers in config |
| astral.standards.public-then-helpers | conforms | Public stage workers + ensure helpers |
| astral.standards.utils-data-late-import-only | conforms | Config-only utils |
| astral.state.core-decides-transitions | conforms | Workers call transition_candidate_state only |
| astral.state.job-prior-states-enforced | conforms | Extends claim_states for candidate registry |
| astral.state.no-daisy-chain-in-run | conforms | One registered-state hop per claim |
| astral.ui.single-gunicorn-worker | conforms | Tick + start_scheduler provision only |

## Considered and excluded

**Considered:** all rows above (48).

**Excluded:**
- `astral.debug.no-repo-root-artifacts-dir` — paths miss
- `astral.debug.spikes-under-debug-dir` — paths miss
- `astral.docs.features-single-file-per-ticket` — layers/paths miss (no docs in Files Changed)
- `astral.git.engineer-test-tree-ban` — paths miss
- `astral.layers.scripts-exempt-from-layer-rules` — layers/paths miss
- `astral.patterns.require-auth-on-protected-endpoints` — layers/paths miss
- `astral.ui.frontend-file-placement` — layers/paths miss
- `astral.ui.naming-conventions` — layers/paths miss

## Findings

### fix-now
None. Round-1 fix-now closed: Stage 2 provisions REQUESTED_* `dispatch_task` rows on template + existing schedules; AST-973 limited to retired-key remaps.

### discuss (resolved — non-blocking)
1. Craft helpers named (`do_task`, `split_craft_resume_base_payload`, persist from `run_candidate_artifact_generation`).
2. Sequential artifacts fan-in remains an accepted Decision.

### acceptable
- `dispatch_claim_states` for CANDIDATE_STATES; tick-driven aging; Single-Component / high / Medium honest.

**Self-assessment:** Single-Component / high / Medium — honest.

— Joan
context_tokens≈90000

#### joan — 2026-07-23T23:20:04.981Z
[validate-plan] blocked — assignee gate

Status is **Plan Ready** (post Plan Discuss r1), but assignee is still **Katherine Johnson**, not Joan.

Chuckles must assign **Joan** before re-validate. Prior note: revise @ `3e19b2d` (REQUESTED_* dispatch_task provisioning) is ready to score once assigned.

— Joan
context_tokens≈84000

#### joan — 2026-07-23T23:18:52.086Z
[validate-plan] blocked — assignee gate

Status is **Plan Ready** (post Plan Discuss r1), but assignee is **Katherine Johnson**, not Joan.

Chuckles must assign **Joan** before re-validate. Round-1 reply + plan revise @ `3e19b2d` (REQUESTED_* `dispatch_task` provisioning) look ready to score once assigned.

— Joan
context_tokens≈78000

#### katherine — 2026-07-23T23:14:05.290Z
[plan-discuss] round=1 reply

Addressed Joan fix-now on `origin/sub/AST-871/AST-972-dispatch-stale-eligibility` @ `3e19b2d`.

**Delta**
- Added **Stage 2**: `ensure_candidate_stage_dispatch_tasks` + `provision_candidate_stage_dispatch_tasks` — idempotent upsert of `(candidate_requested_resume, REQUESTED_RESUME)` and `(candidate_requested_artifacts, REQUESTED_ARTIFACTS)` onto `template_candidate_id` first, then every candidate that already has ≥1 `dispatch_task` row; fields from `dispatch_task_admin_defaults` / `save_dispatch_task`; invoked from `start_scheduler`.
- Clarified AST-973 owns **retired** trigger remaps only (LIVE_PROMPTS→ACTIVE_SEARCH), not creating these new orchestration rows.
- Named concrete craft helpers in Stage 4 (`do_task`, `split_craft_resume_base_payload`, persist shape from `run_candidate_artifact_generation`; no `parse_candidate_resume` / no nested `asyncio.run`).
- Renumbered stages; Revisions § Revision 1.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-871/AST-972-dispatch-stale-eligibility/docs/features/candidate/ast-972-dispatch-and-stale-eligibility-for-candidate-stages.md

Moving back to Plan Ready for Joan re-validate.

#### joan — 2026-07-23T23:08:58.744Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-972
**Overall:** REVISE
**Publish ref:** `origin/sub/AST-871/AST-972-dispatch-stale-eligibility`
**Implementer:** Katherine Johnson

## Traceability

### Parent / child AC → plan stages

| AC | Coverage |
| -- | -- |
| **#5** REQUESTED_RESUME / REQUESTED_ARTIFACTS claimable; resolve ready/retry/error | Stages 1–3 (config, eligibility/claim gate, workers + consult route) — **gap: no `dispatch_task` row provisioning** |
| **#6** ACTIVE_SEARCH sole company/job search gate (replaces LIVE_PROMPTS) | Prerequisite (AST-970 INFLOW flip) + Stage 2 claim gate for candidate tasks |
| Stale aging invocation (parent waiting stages; AST-970 helper) | Stage 4 tick hook |
| Parent AC 1–4, 7–10 | N/A — vocabulary/history/migration Boundaries |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Config stage-dispatch + claim helpers | Waiting vs dispatch-triggering stages; config SSoT |
| 2 Eligibility + claim gate | ACTIVE_SEARCH search gate; REQUESTED_* claimability logic |
| 3 Workers + consult routing | Claim → ready/retry/error; no craft prompt edits |
| 4 Tick → `age_stale_candidate_states` | Stale aging activation |
| 5 Smoke / CC note | Gate hygiene |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge SHA work |
| orch.git.commit-vocabulary | conforms | Plan-only |
| orch.git.flow-direction-inviolable | conforms | Child sub publish ref |
| orch.git.ftr-sub-topology | conforms | Under ftr AST-871 |
| orch.git.merge-on-checkout | conforms | Merge AST-970 prerequisite stated |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrites |
| orch.git.no-dev-agent-branches | conforms | No agent branches |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Sequential craft fan-in is engineering; craft keys stop-rule present |
| orch.pipeline.plan-is-bible | conforms | Plan on publish ref |
| orch.pipeline.project-scoped-queues | conforms | Untouched |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Katherine |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Katherine on REVISE |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No grades |
| astral.agent.do-task-delegation | conforms | Craft via existing do_task helpers |
| astral.agent.grade-vector-validation | conforms | N/A |
| astral.batch.batch-id-first | conforms | Keeps single-candidate ctx claim model |
| astral.batch.batch-id-format | conforms | No new mint rules |
| astral.batch.claim-process-release | conforms | Matches current candidate (no pool claim) pattern |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | `CANDIDATE_STAGE_DISPATCH` + TASK_CONFIG orchestration keys |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned |
| astral.layers.core-vs-external-bright-line | conforms | No new external I/O |
| astral.layers.import-direction | conforms | utils/data/core only |
| astral.layers.ui-config-driven-business-logic | conforms | No React rule duplication |
| astral.patterns.coat-check-never-store-empty | conforms | N/A |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Routes via consult; not consult-grade |
| astral.standards.data-raises-caller-logs | conforms | Count helpers stay data |
| astral.standards.database-header-inventory | conforms | No new tables/columns; eligibility logic only |
| astral.standards.debug-contract-gated | conforms | Workers accept `debug` flag |
| astral.standards.dry-and-focused-functions | conforms | Reuses claim_states + AST-970 aging |
| astral.standards.in-scope-only | conforms | No vocabulary/prompts/daisy-chain/nav remaps |
| astral.standards.logging-via-utils | conforms | No print paths |
| astral.standards.no-cross-contamination | conforms | Layered files |
| astral.standards.no-hardcoded-sets | conforms | Craft lists + triggers in config |
| astral.standards.public-then-helpers | conforms | Public stage workers |
| astral.standards.utils-data-late-import-only | conforms | Config-only utils |
| astral.state.core-decides-transitions | conforms | Workers call `transition_candidate_state` only |
| astral.state.job-prior-states-enforced | conforms | Extends claim_states for candidate registry; jobs untouched |
| astral.state.no-daisy-chain-in-run | conforms | One registered-state hop per claim; craft fan-in ≠ state daisy-chain |
| astral.ui.single-gunicorn-worker | conforms | Tick hook only; no worker-count change |

## Considered and excluded

**Considered:** all rows above (48).

**Excluded:**
- `astral.debug.no-repo-root-artifacts-dir` — paths miss
- `astral.debug.spikes-under-debug-dir` — paths miss
- `astral.docs.features-single-file-per-ticket` — layers/paths miss (no docs in Files Changed)
- `astral.git.engineer-test-tree-ban` — paths miss
- `astral.layers.scripts-exempt-from-layer-rules` — layers/paths miss
- `astral.patterns.require-auth-on-protected-endpoints` — layers/paths miss
- `astral.ui.frontend-file-placement` — layers/paths miss
- `astral.ui.naming-conventions` — layers/paths miss

## Findings

### fix-now
1. **Location:** Out of scope / Stage 5 note vs child AC **#5**
   **Finding:** `dispatch_tasks` DB is the sole source of truth for what the scheduler can run. Plan wires TASK_CONFIG + claim/eligibility/workers but **explicitly refuses** to create/upsert live `dispatch_task` rows for `candidate_requested_resume` / `candidate_requested_artifacts`, parking “adding REQUESTED_* rows to template candidates” on AST-973. AST-973’s charter is remapping **retired** state keys/FKs — not owning new REQUESTED_* orchestration rows. Without template (and existing-candidate) rows, AC#5 “are claimable by dispatch” is not met by this ticket’s deliverable; tick/`get_due_tasks` will never select the new keys.
   **Recommendation:** Add a Stage (or Stage 1/2 step) that upserts the two new `dispatch_task` rows onto `template_candidate_id` via `dispatch_task_admin_defaults` (and states how existing candidates receive them — set-from-template / one-time upsert). Keep AST-973 for LIVE_PROMPTS→ACTIVE_SEARCH remaps of **existing** rows only.

### discuss
1. Name the concrete existing craft/persist helpers for resume + each artifact craft key (Conf already flags residual uncertainty).
2. Artifacts sequential fan-in of ~7 crafts in one dispatch claim — acceptable vs one craft per cycle; Decision is clear, confirm with Archie/Susan only if runtime/cost is a product concern.

### acceptable
- Extending `dispatch_claim_states` for `CANDIDATE_STATES` (today candidate registry is ignored → no retry companion) is required for AC#5.
- Not re-flipping INFLOW / not reimplementing aging matches AST-970 ownership.
- Tick-driven aging (not a new dispatch task) is a sound Decision.
- Self-assessment Single-Component / high / Medium is honest.

Update plan on publish ref → Plan Ready + Joan re-validate.

— Joan
context_tokens≈62000

#### joan — 2026-07-23T23:03:09.776Z
[validate-plan] blocked — assignee gate

Status is **Plan Ready**, but assignee is **Katherine Johnson**, not Joan.

Chuckles must assign **Joan** (`susan+joan@susansomerset.com`) before validate-plan runs. No rubric pass until then.

— Joan
context_tokens≈16000

#### katherine — 2026-07-23T22:59:07.824Z
Plan published on `origin/sub/AST-871/AST-972-dispatch-stale-eligibility` @ `9b14341`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-871/AST-972-dispatch-stale-eligibility/docs/features/candidate/ast-972-dispatch-and-stale-eligibility-for-candidate-stages.md

**Self-assessment**
- **Scope:** Single-Component — config + dispatcher/consult/candidate claim/resolve for REQUESTED_* and tick hook for AST-970 aging; no UI, no job/company machine changes.
- **Conf:** high — Ada’s AST-970 plan already defines `retry_state` / `error_state` / `stale_after_hours` / `stale_state`, flips INFLOW → ACTIVE_SEARCH, and ships `age_stale_candidate_states`; this ticket only wires claim, stage workers, eligibility split, and the tick call.
- **Risk:** Medium — wrong claim gate could starve inflow or fire craft on the wrong state; wrong retry/error hop could strand candidates; mitigated by registry-only transitions and leaving live `dispatch_task` remaps to AST-973.

Consumes AST-970 registry (blockedBy). Does not re-implement vocabulary, INFLOW flip, or aging helper.

---

# AST-972 — Dispatch and stale eligibility for candidate stages (Candidate state machine)

**Linear:** [AST-972](https://linear.app/astralcareermatch/issue/AST-972/dispatch-and-stale-eligibility-for-candidate-stages-candidate-state)
**Parent:** [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine)
**Publish ref:** `origin/sub/AST-871/AST-972-dispatch-stale-eligibility`

Wire REQUESTED_RESUME / REQUESTED_ARTIFACTS so per-candidate dispatch can claim and resolve them to ready / retry / error; provision the matching `dispatch_task` rows so the scheduler can select them; invoke AST-970’s stale-aging helper from the dispatcher tick; keep ACTIVE_SEARCH as the sole company/job search dispatch gate. Does not invent vocabulary, craft prompts, daisy-chain `run_next`, Topic Menu, nav remaps, or remapping retired LIVE_PROMPTS FKs (AST-973).

---

## Prerequisite (AST-970)

**Blocked by AST-970.** Before Stage 1, merge `origin/sub/AST-871/AST-970-candidate-state-registry` (or parent ftr once Ada’s registry is there) into this sub. Confirm Ada’s plan landed:

| Expectation | Source (AST-970 plan) |
|-------------|----------------------|
| `CANDIDATE_STATES` with `REQUESTED_RESUME` / `REQUESTED_ARTIFACTS` + `retry_state` / `error_state` companions | Stage 1 registry |
| Waiting states with `stale_after_hours` + `stale_state` | Stage 1 registry |
| `ACTIVE_SEARCH` in registry; `INFLOW_CONFIG["discovery"]["dispatch_trigger_state"] == "ACTIVE_SEARCH"` | Stage 1 config-local gate |
| `age_stale_candidate_states(*, now=None) -> int` in `src/core/candidate.py` | Stage 2 (helper only — no tick hook) |

If metadata keys differ from `retry_state` / `error_state` / `stale_after_hours` / `stale_state`, **stop** and comment — do not invent a parallel schema.

⚠️ **Decision:** Do **not** re-set `INFLOW_CONFIG` or re-implement `age_stale_candidate_states` here — AST-970 owns those. This ticket owns claim wiring, stage workers, eligibility split, **new REQUESTED_* `dispatch_task` row provisioning**, and the tick call. AST-973 remaps **existing** retired-state keys (e.g. LIVE_PROMPTS → ACTIVE_SEARCH) only — it does not own creating the new orchestration rows.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_STAGE_DISPATCH`; extend `dispatch_claim_states` for candidate; register orchestration task_keys + trigger/entity rules | utils |
| `src/data/database.py` | Branch `count_eligible_for_dispatch_task` for non-inflow candidate triggers; helper listing candidate_ids that already have any `dispatch_task` row; fix inflow eligibility docstring if still says LIVE_PROMPTS | data |
| `src/core/candidate.py` | `run_requested_resume_dispatch` / `run_requested_artifacts_dispatch` workers only (aging helper already AST-970) | core |
| `src/core/dispatcher.py` | Candidate claim gate in `_run_unified`; `ensure_candidate_stage_dispatch_tasks` + one-time provision call path; tick → `age_stale_candidate_states()` | core |
| `src/core/consult.py` | Route new candidate dispatch task_keys to stage workers (keep `inflow_discovery` → roster) | core |

**Out of scope:** rewriting `CANDIDATE_STATES` / INFLOW trigger (AST-970); history (AST-971); remapping **existing** `dispatch_task.trigger_state` values off retired names like LIVE_PROMPTS (AST-973); craft prompt content; `run_next` daisy-chain; Topic Menu; Betty tests.

---

## Stage 1: Config — stage-dispatch map + claim helpers

**Done when:** `dispatch_claim_states("REQUESTED_RESUME", "candidate")` returns primary + registry `retry_state`; `CANDIDATE_STAGE_DISPATCH` names the two orchestration task_keys and which existing craft keys they call; `_dispatch_trigger_state_for_task_key` / entity-type helpers resolve those keys to REQUESTED_* / `candidate`.

1. In `src/utils/config.py`, add `CANDIDATE_STAGE_DISPATCH` near `INFLOW_CONFIG`:

   ```python
   CANDIDATE_STAGE_DISPATCH = {
       "requested_resume": {
           "task_key": "candidate_requested_resume",
           "trigger_state": "REQUESTED_RESUME",
           "pass_state": "RESUME_READY",
           # Existing craft entry — do not edit craft_resume_base prompts/schema.
           "craft_task_key": "craft_resume_base",
       },
       "requested_artifacts": {
           "task_key": "candidate_requested_artifacts",
           "trigger_state": "REQUESTED_ARTIFACTS",
           "pass_state": "ARTIFACTS_READY",
           # Ordered list of existing craft_* keys already in TASK_CONFIG / UI generate.
           # Sequential fan-in only — not run_next daisy-chain.
           # No craft_job_title_patterns key exists; title patterns stay profile/intake.
           "craft_task_keys": [
               "craft_company_search_terms",
               "craft_joblist_rubric",
               "craft_jobdesc_rubric",
               "craft_do_rubric",
               "craft_get_rubric",
               "craft_like_rubric",
               "craft_prefilter_rubric",
           ],
       },
   }
   ```

   ⚠️ **Decision:** Dedicated orchestration task_keys (`candidate_requested_*`) — not reusing `craft_*` as `dispatch_task.task_key`. If any `craft_task_keys` string is missing from `TASK_CONFIG` at build time, **stop** and comment with actual keys.

2. In `dispatch_claim_states`, when `entity_type == "candidate"`, use `CANDIDATE_STATES` the same way job/company use theirs (prefer `retry_state` on the primary entry, else `{ts}_RETRY` if present, else `[ts]`).

3. In `_dispatch_trigger_state_for_task_key`, map:
   - `candidate_requested_resume` → `CANDIDATE_STAGE_DISPATCH["requested_resume"]["trigger_state"]`
   - `candidate_requested_artifacts` → `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"]`

4. In `_dispatch_entity_type_for_task_key` (or equivalent), map both new keys to `"candidate"`.

5. Add minimal `TASK_CONFIG` entries for both orchestration keys: `entity_type: "candidate"`, `trigger_state` matching step 3, `requires_candidate_key: True`, no response_schema. Ensure `dispatch_task_admin_defaults` works.

**Commit message:** `code(AST-972): stage 1 — stage-dispatch config + candidate claim helpers`

---

## Stage 2: Provision `dispatch_task` rows (template + existing schedules)

**Done when:** `template_candidate_id()` has two rows `(candidate_requested_resume, REQUESTED_RESUME)` and `(candidate_requested_artifacts, REQUESTED_ARTIFACTS)` with fields filled from `dispatch_task_admin_defaults`; every other candidate that already had ≥1 `dispatch_task` row also has those two pairs (idempotent upsert — skip if present); candidates with zero dispatch rows are untouched (they get the keys later via Manage Candidates set-from-template once the template is seeded). AST-973 is **not** responsible for these new rows.

1. In `src/data/database.py`, add:

   ```python
   def list_candidate_ids_with_dispatch_tasks() -> List[str]:
       """Distinct candidate_id values that already own ≥1 dispatch_task row."""
   ```

2. In `src/core/dispatcher.py`, add:

   ```python
   def ensure_candidate_stage_dispatch_tasks(candidate_id: str) -> Dict[str, Any]:
   ```

   For each entry in `CANDIDATE_STAGE_DISPATCH`:
   - Resolve `task_key` / `trigger_state` from the entry.
   - If `list_dispatch_tasks_for_candidate(candidate_id)` already contains a row with that `(task_key, trigger_state)`, skip.
   - Else call `save_dispatch_task` with:
     - `candidate_id=candidate_id`
     - `task_key` / `trigger_state` from the entry (defaults fill `entity_type` / `sort_by` / `batch_call_mode` via `dispatch_task_admin_defaults`)
     - `min_count=1`, `auto_mode=True`, `batch_size=1`, `freq_hrs=0`
   - Return counts `{added, skipped}`.

3. Add:

   ```python
   def provision_candidate_stage_dispatch_tasks() -> Dict[str, Any]:
   ```

   - Call `ensure_candidate_stage_dispatch_tasks(template_candidate_id())` first (fail if template candidate missing).
   - For each id in `list_candidate_ids_with_dispatch_tasks()` (including template is fine — idempotent), call `ensure_candidate_stage_dispatch_tasks(id)`.
   - Return aggregate `{template_candidate_id, candidates_touched, added, skipped}`.

4. Invoke `provision_candidate_stage_dispatch_tasks()` once from `start_scheduler()` (same place that marks interrupted ledgers) so production picks up rows on process start without a separate migration script. Idempotent — safe on every restart.

⚠️ **Decision:** One-time-style **ensure upsert** of only the two new keys (not full `set_candidate_dispatch_tasks_from_template`, which would prune non-template extras). Existing candidates with schedules get REQUESTED_* rows; empty candidates stay empty until an operator runs set-from-template (which then copies the seeded template including these keys). AST-973 still remaps LIVE_PROMPTS→ACTIVE_SEARCH on **existing** inflow rows only.

**Commit message:** `code(AST-972): stage 2 — provision REQUESTED_* dispatch_task rows`

---

## Stage 3: Eligibility counts + candidate claim gate

**Done when:** `inflow_discovery` eligibility still uses search-term staleness and compares candidate state to `INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]` (ACTIVE_SEARCH after AST-970). For `candidate_requested_*`, count is `1` iff that candidate’s state ∈ `dispatch_claim_states(trigger, "candidate")`, else `0`. `_run_unified` yields an empty batch when ctx state is not claimable.

1. In `src/data/database.py`, if `count_candidate_inflow_discovery_eligible` docstring still says LIVE_PROMPTS, update it to say the config discovery trigger (ACTIVE_SEARCH). Leave `describe_candidate_inflow_discovery_eligibility` logic alone (already compares to `INFLOW_CONFIG`).

2. In `count_eligible_for_dispatch_task`, replace the blanket `entity_type == "candidate"` → inflow helper with:
   - `task_key == INFLOW_CONFIG["discovery"]["task_key"]` → existing inflow helper
   - `task_key` in the two `CANDIDATE_STAGE_DISPATCH[*]["task_key"]` values → load candidate; return `1` if state in `dispatch_claim_states(trigger_state, "candidate")` else `0`
   - else → `0`

3. In `src/core/dispatcher.py` `_run_unified`, for `entity_type == "candidate"`:
   - `claim_states = dispatch_claim_states(input_state, "candidate")`
   - If ctx missing or `(ctx.get("state") or "").strip()` not in `claim_states` → `entities = []`
   - Else `entities = [ctx]`
   - Keep `_dispatch_one` inflow `freq_hrs` enrichment unchanged.

⚠️ **Decision:** Keep single-candidate-per-task claim (current model). No cross-candidate `claim_candidate_batch` pool.

**Commit message:** `code(AST-972): stage 3 — candidate claim gate + eligibility split`

---

## Stage 4: Stage workers + consult routing (ready / retry / error)

**Done when:** Dispatch with `task_key=candidate_requested_resume` on a candidate in `REQUESTED_RESUME` (or retry companion) transitions to `RESUME_READY` on craft success, to registry `retry_state` on first-strike failure from primary, or to registry `error_state` when already on retry (or hard failure). Same pattern for artifacts → `ARTIFACTS_READY` / retry / error. No craft prompt or schema edits.

1. In `src/core/candidate.py`, add:

   ```python
   async def run_requested_resume_dispatch(candidate_id: str, *, debug: bool = False) -> Dict[str, int]:
   ```

   Concrete craft/persist path (named — no judgment call):
   - Resolve `retry_state` / `error_state` from `CANDIDATE_STATES["REQUESTED_RESUME"]`.
   - Read `live_content` from `candidate_data.context.starting_resume_text` (same source as `parse_candidate_resume`).
   - `response = await do_task(task_key="craft_resume_base", live_content=..., index=candidate_id, ctx=candidate, debug=debug)`.
   - On success: `structure, content = split_craft_resume_base_payload(parsed)`; `database.save_candidate(..., candidate_data={"artifacts": {"resume_structure": structure, "base_resume": content}}, merge=True)` — same persist shape as the success branch inside `run_candidate_artifact_generation` for `craft_resume_base`.
   - Then `transition_candidate_state(candidate_id, pass_state)` (`RESUME_READY`).
   - On failure: primary → `retry_state`; already on retry → `error_state`.
   - **Do not** call `parse_candidate_resume` (it auto-hops `NEW → PROFILE_READY`). **Do not** call sync `run_candidate_artifact_generation` from this async worker (it uses `asyncio.run` and owns its own ledger — dispatcher already has the outer ledger).

2. Add:

   ```python
   async def run_requested_artifacts_dispatch(candidate_id: str, *, debug: bool = False) -> Dict[str, int]:
   ```

   Concrete path per craft key:
   - Same retry/error routing from `CANDIDATE_STATES["REQUESTED_ARTIFACTS"]`.
   - For each key in `craft_task_keys` in order: `await do_task(task_key=key, live_content="", index=candidate_id, ctx=candidate, debug=debug)` (empty live_content matches UI generate when content comes from tokens/ctx). Persist success the same way `run_candidate_artifact_generation` already does for that key (reuse its post-success persist branches by extracting a shared helper **only if** needed to avoid copy-paste of the craft_resume_base / rubric stash paths — prefer calling a new internal `async def _persist_craft_success(candidate_id, task_key, parsed)` lifted from the existing success block rather than inventing new storage).
   - Stop at first failure → retry/error.
   - All succeed → `ARTIFACTS_READY`.
   - ⚠️ **Decision:** Sequential fan-in of the config craft list in **one** dispatch claim is intentional (engineering cost/runtime tradeoff). Not a product open question unless Archie/Susan objects after UAT — do not split to one craft per tick in this ticket.

3. In `src/core/consult.py` `run_consult_task`, replace blanket candidate → `run_inflow_discovery_batch` with:
   - `inflow_discovery` → existing roster batch
   - `candidate_requested_resume` → `run_requested_resume_dispatch(...)`
   - `candidate_requested_artifacts` → `run_requested_artifacts_dispatch(...)`
   - else → warning + zero summary

**Commit message:** `code(AST-972): stage 4 — requested resume/artifacts dispatch workers`

---

## Stage 5: Tick hook for AST-970 stale aging

**Done when:** Each dispatcher tick calls `age_stale_candidate_states()` once before spawning due AUTO tasks. No reimplementation of aging logic; no new auto `dispatch_task` for stale.

1. In `src/core/dispatcher.py` `_tick_loop`, at the start of each `try` body (before `get_due_tasks`), call:

   ```python
   from src.core.candidate import age_stale_candidate_states
   age_stale_candidate_states()
   ```

   (or a top-level import if already consistent with file style). Exceptions remain covered by the existing tick `except`.

⚠️ **Decision:** Tick-driven invocation (not a new dispatch task) so waiting stages age even when no REQUESTED_* task is due. Hours/companions stay solely on AST-970’s `CANDIDATE_STATES`.

**Commit message:** `code(AST-972): stage 5 — tick invokes candidate stale aging`

---

## Stage 6: Smoke + Code Complete note

**Done when:** Compile/lint clean on touched files; Code Complete comment maps AC5/AC6 including that template + scheduled candidates now have REQUESTED_* `dispatch_task` rows; AST-973 still owns remapping **retired** trigger_state values (LIVE_PROMPTS → ACTIVE_SEARCH) on existing inflow rows only.

1. `python -m compileall` on edited paths; fix any issues introduced here.
2. Code Complete checklist:
   - AC5: provisioned rows + claim gate + workers + retry/error for REQUESTED_RESUME / REQUESTED_ARTIFACTS
   - AC6: search eligibility via INFLOW trigger (ACTIVE_SEARCH from AST-970) + claim gate
   - Stale: tick calls AST-970 `age_stale_candidate_states`
   - Not here: LIVE_PROMPTS→ACTIVE_SEARCH remaps of existing inflow rows (AST-973), craft prompts

**Commit message:** none if Stage 5 is green — else `code(AST-972): stage 6 — lint/compile fixes`

---

## Self-Assessment

**Scope:** Single-Component — config + dispatcher/consult/candidate claim/resolve + dispatch_task provisioning for candidate entity_type; consumes AST-970 registry; no job/company machine changes; no UI.

**Conf:** high — Ada’s AST-970 plan already names companions / stale metadata / INFLOW flip / aging helper; Joan’s fix-now closes the AC#5 gap by owning template + existing-schedule row upserts here; craft path is named (`do_task` + `split_craft_resume_base_payload` / existing persist branches).

**Risk:** Medium — wrong claim gate could starve inflow or fire craft on the wrong state; ensure-upsert with `auto_mode=True` could wake empty REQUESTED_* queues until eligibility returns 0 (acceptable); mitigated by registry-only transitions and leaving retired-key remaps to AST-973.

---

## Code rules check

| Rule | Plan alignment |
|------|----------------|
| §1.4 / §2.1 config SSoT | Orchestration keys + craft lists in config; state names/hours from AST-970 registry only |
| §2.4 batch processing | Per-candidate claim; eligibility shared with count helper; rows via `save_dispatch_task` + admin defaults |
| §2.6 state machine | All hops via `transition_candidate_state`; no ad-hoc state writes in workers |
| §3.3 imports | UI untouched; core ↔ data/config; consult routes to candidate workers |
| DRY | Reuse `dispatch_claim_states`, AST-970 aging helper, existing craft/persist helpers; no second INFLOW flip |

---

## Revisions

### Revision 1 — 2026-07-23

Driven by: Joan `[plan-discuss] round=1 concern` fix-now — plan wired TASK_CONFIG/claim/workers but refused to create live `dispatch_task` rows for `candidate_requested_*`, parking that on AST-973; without rows AC#5 is unmet because `get_due_tasks` never selects the new keys.

Changes:
- Added **Stage 2** provisioning: `ensure_candidate_stage_dispatch_tasks` + `provision_candidate_stage_dispatch_tasks` (template first, then every candidate with an existing schedule); idempotent upsert via `dispatch_task_admin_defaults` / `save_dispatch_task`; invoke from `start_scheduler`.
- Clarified AST-973 owns **retired** trigger remaps only (LIVE_PROMPTS→ACTIVE_SEARCH), not new REQUESTED_* orchestration rows.
- Named concrete craft helpers in Stage 4 (`do_task`, `split_craft_resume_base_payload`, persist shape from `run_candidate_artifact_generation`; no `parse_candidate_resume` / no nested `asyncio.run`).
- Renumbered former stages 2–5 → 3–6; updated Files Changed, Out of scope, Self-Assessment Conf, Stage 6 CC note.

## Review

| Commit | Note |
|--------|------|
| `bf81fda` on `sub/AST-871/AST-972-dispatch-stale-eligibility` | Code Complete — build-child AST-972 |

### Radia code-rubric.v1 (revision=1)

**Overall:** FIX-NOW  
**Publish tip reviewed:** `aee89123471e20729c4369f89c7814287af7ab4b` (`origin/dev...origin/sub/AST-871/AST-972-dispatch-stale-eligibility`)

**What’s solid**
- `CANDIDATE_STAGE_DISPATCH` + candidate `dispatch_claim_states`; provision REQUESTED_* rows; claim gate + eligibility split; tick → `age_stale_candidate_states`; resume/artifacts workers + consult routing; transitions via core only.

**Issues**
- **fix-now:** `src/core/dispatcher.py` `_tick_loop` late-imports `age_stale_candidate_states` with no cycle-break comment (candidate↔dispatcher). B1 / CODE_RULES: function-scoped imports need a short why comment.
- **discuss (C4 stragglers):** Joan Excluded statutes that are in-scope on tip (blockedBy 970 + Betty tests + feature docs): `spikes-under-debug-dir`, `features-single-file-per-ticket`, `engineer-test-tree-ban`, `require-auth-on-protected-endpoints`, `ui.naming-conventions`. Substance conforms.
- **advisory:** `start_scheduler` provision `except Exception` logs via `_sched_log.exception` (acceptable); CREATE candidate `DEFAULT 'NEW'` remains AST-973.

**Recommended actions**
- Engineer: add one-line late-import comment on the tick aging import; acknowledge C4 stragglers.

## Resolution

**2026-07-24** — Radia code-rubric.v1 revision=1 (FIX-NOW) @ `582b650`

| Finding | Action |
|---------|--------|
| fix-now: `_tick_loop` late import of `age_stale_candidate_states` needs cycle-break comment | Added `# late: avoid cycle with candidate → dispatcher (module-top import)` above the import |
| discuss: C4 stragglers Joan Excluded at plan time, scored conforms on tip | Acknowledged — no product change |
| advisory: provision `except Exception` + CREATE DEFAULT NEW | No change — acceptable / AST-973 |
