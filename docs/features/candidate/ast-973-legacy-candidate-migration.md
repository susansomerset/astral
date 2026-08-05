<!-- linear-archive: AST-973 archived 2026-08-05 -->

## Linear archive (AST-973)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-973/legacy-candidate-migration-consumers-and-dispatchtask-config-keys  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-871 — Candidate state machine  
**Blocked by / blocks / related:** parent: AST-871

### Description

## What this implements

Migrate LIVE_PROMPTS → ACTIVE_SEARCH; hard-delete existing DELETED rows; map remaining legacy states → NEW_CANDIDATE; remap dispatch-table foreign keys and task-config entries off retired candidate states; update nav/gates and other consumers so retired names are gone.

## Acceptance criteria

 8. Migration: LIVE_PROMPTS → ACTIVE_SEARCH; existing DELETED rows hard-deleted; all other legacy states → NEW_CANDIDATE; no silent data loss for remapped live rows.
 9. Dispatch-table foreign keys and task-config entries that referenced retired candidate states are remapped (or rewritten) so they resolve correctly under the new vocabulary — no orphaned LIVE_PROMPTS (or other legacy) dispatch/task-config keys left behind.
10. Nav and other state-gated candidate UI still resolve correctly for candidates on the new states.

## Boundaries

Does **not** invent new product flows. Does **not** own the state registry (AST-970) or history storage (sibling: Candidate transition history).

## Notes for planning

Depends on AST-970 vocabulary. Include dispatch_tasks / task_config state-key remaps per parent Functional scope.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-871-candidate-state-machine`, child `sub/AST-871/<this-id>-legacy-candidate-migration`. Created at dispatch-parent.

### Comments

#### betty — 2026-07-24T00:59:49.877Z
[merge-child] blocked: git pull merge on sub — `Merge remote-tracking branch` in ftr..sub (91ab821, b05c75c). Rewrite tip onto `origin/ftr/AST-871-candidate-state-machine`, cherry-pick only AST-973 labeled commits, force-with-lease push `origin/sub/AST-871/AST-973-legacy-candidate-migration`. @Ada Lovelace

— Chuckles

#### radia — 2026-07-24T00:25:50.510Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-973
**Publish ref:** `origin/sub/AST-871/AST-973-legacy-candidate-migration` @ `ab4671e5e0042cfd3c25968bcdc1f13b28d6b910`
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-871/AST-973-legacy-candidate-migration` — layers `core`/`data`/`utils`/`ui`/`docs`/`scripts` (+ Betty tests/bible; blockedBy AST-970).

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-973)` of `890f8e0` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` / merge blockedBy |
| orch.git.flow-direction-inviolable | universal | conforms | Child publish on `sub/AST-871/…` |
| orch.git.ftr-sub-topology | universal | conforms | Under parent AST-871 |
| orch.git.merge-on-checkout | universal | conforms | `origin/dev` + blockedBy 970 merges on tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | No agent long-lived branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree `astral-AST-871` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Phase A CLI-only after Susan OK; ensure = B/C |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–4 match plan bible |
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
| astral.batch.batch-id-format | scoped | conforms | Untouched |
| astral.batch.claim-process-release | scoped | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Cascade only; no latest-only rewrite |
| astral.config.config-source-of-truth | scoped | conforms | Legacy map + remap helper in config |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env splits |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature/data-model docs under `docs/features/**` |
| astral.docs.features-single-file-per-ticket | scoped | conforms | AST-973 plan in `docs/features/candidate/` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits are test-tree only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code`/`docs` leave tests/bible to Betty |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No external I/O |
| astral.layers.import-direction | scoped | conforms | CLI → data/core; layers respected |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Migration CLI under `scripts/` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Manage Candidates logical-delete copy; states from API |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult orchestration |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | No new open endpoints |
| astral.standards.data-raises-caller-logs | scoped | conforms | Data owns migrate/hard-delete; core wraps |
| astral.standards.database-header-inventory | scoped | conforms | Inventoried tables only; no new undeclared tables |
| astral.standards.debug-contract-gated | scoped | conforms | No new debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Single map + one migrate writer |
| astral.standards.in-scope-only | scoped | conforms | Registry/history/claim left to siblings |
| astral.standards.logging-via-utils | scoped | conforms | Product paths clean; CLI prints OK |
| astral.standards.no-cross-contamination | scoped | conforms | Layered files only |
| astral.standards.no-hardcoded-sets | scoped | conforms | Remap table in config |
| astral.standards.public-then-helpers | scoped | conforms | Core wrappers + data migrate |
| astral.standards.utils-data-late-import-only | scoped | conforms | Config-only utils |
| astral.state.core-decides-transitions | scoped | conforms | Remap is cutover; hard-delete ≠ state hop |
| astral.state.job-prior-states-enforced | scoped | conforms | Job/company `NEW` not remapped |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No multi-state dispatch chain |
| astral.ui.frontend-file-placement | scoped | conforms | Existing pages; no new frontend files required |
| astral.ui.naming-conventions | scoped | conforms | No new files/routes |
| astral.ui.single-gunicorn-worker | scoped | conforms | Untouched |

## Pattern conformance

none cited

## Plan adherence

Stages 1–4 match: legacy map; Phase A CLI-only pre-cutover DELETED; ensure=`phases="BC"`; hard-delete/purge; bootstrap + grep-clean product paths; data-model cutover note. CREATE default is `NEW_CANDIDATE`. AdminManageCandidates already states logical delete → DELETED. Self-Assessment MAJOR-CHANGE / high / HIGH matches. Joan APPROVED @ `935226a`.

## Findings

### discuss
1. **C4 straggler** — Joan Excluded `astral.git.engineer-test-tree-ban`; tip includes Betty `tests/**` + `docs/test-bible/**`. Scored **conforms**. Acknowledge on resolve.

### advisory
1. `CANDIDATE_DATA_MODEL.md` context section still says four fields “gate the `CONTEXT_READY` state transition” while State machine + Legacy cutover sections are updated.

### fix-now
None.

## What’s solid

- AC#8–#10: LIVE_PROMPTS→ACTIVE_SEARCH, pre-cutover DELETED hard-delete (CLI only), other legacy→NEW_CANDIDATE with audit list, dispatch trigger remap with candidate-only NEW, consumer/bootstrap sweep, reap-due purge entrypoint.

## Notes

Joan Excluded `astral.debug.no-repo-root-artifacts-dir` remains `not-applicable`.

— Radia
context_tokens≈110000

#### betty — 2026-07-24T00:00:25.981Z
1. **Publish:** `origin/sub/AST-871/AST-973-legacy-candidate-migration` @ `fd94a82` (`merge-tests(AST-973): origin/tests 890f8e0`)
2. **Tests SHA:** `890f8e0` — `test(AST-973): legacy candidate migrate, hard-delete, and vocab sweep`
3. **Coverage**
   - Config: `CANDIDATE_LEGACY_STATE_MAP` / `remap_legacy_candidate_state`
   - Data: hard_delete satellites; Phase A pre-cutover DELETED only; Phase B remap + preserve `state_changed_at`; Phase C trigger remap (company NEW untouched); ensure = BC only
   - Core: `hard_delete_candidate` / `purge_reap_due_candidates`
   - Fixture sweep: roster/integration `LIVE_PROMPTS`→`ACTIVE_SEARCH`; frontend `CONTEXT_READY`→`ACTIVE_SEARCH`
4. **Note:** AST-972 TestAst* classes skip when `CANDIDATE_STAGE_DISPATCH` absent on this tip
5. **Manifest**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst973LegacyCandidateRemap \
  tests/component/core/test_candidate.py::TestAst973HardDeleteAndReapPurge \
  tests/component/data/database/test_candidates.py::TestAst973LegacyCandidateMigration \
  -q
```
6. **Bible shasums** (on publish tip)
   - `c0aff3b6290e188e0a812e2d5050d2208678d9fd777df73902d42b12630597d7` `docs/test-bible/core/candidate.md`
   - `5ec82e1a0db20697f20f5ccde4f93df558397b057007fcec53a2e85c4e7284f4` `docs/test-bible/utils/config.md`
   - `7221aa79d3952e3d4f512aa80d406eb383fe253648521eb24b04191997a46522` `docs/test-bible/data/database/candidates.md`

— Betty

#### joan — 2026-07-23T23:20:47.020Z
[validate-plan] no-op — already past gate

Spawn asked for Plan Ready re-validate after Plan Discuss r1, but AST-973 is already **Plan Approved** (assignee Ada; verdict attachment `Plan rubric verdict (rev 1)` present @ `935226a`).

No second rubric pass. Status stays Plan Approved.

— Joan
context_tokens≈86000

#### joan — 2026-07-23T23:19:54.553Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-973
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-871/AST-973-legacy-candidate-migration` @ `935226a`
**Implementer:** Ada Lovelace
**Plan Discuss:** round 1 completed (concern + reply); fix-now closed

## Traceability

### Parent / child AC → plan stages

| AC | Coverage |
| -- | -- |
| **#8** LIVE_PROMPTS→ACTIVE_SEARCH; hard-delete existing (pre-cutover) DELETED; other legacy→NEW_CANDIDATE; auditable unknown remaps | Stage 1 Phase A (CLI) + B/C; Stage 4 doc |
| **#9** dispatch_task / task-config keys off retired states | Stage 1 Phase C + Stage 3 grep / INFLOW confirm |
| **#10** Nav and state-gated UI on new states | Stage 3 consumer sweep + AST-970 config gates |
| Parent AC 1–7 | N/A — Boundaries |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Config map + migrate (A CLI / BC ensure) | Legacy migration + dispatch trigger remaps |
| 2 Reap-due hard delete | Post-cutover DELETED + AST-970 timer |
| 3 Consumer sweep + grep | Retired names gone from product paths |
| 4 Data-model doc | Cutover contract |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge SHA |
| orch.git.commit-vocabulary | conforms | Plan-only |
| orch.git.flow-direction-inviolable | conforms | Child sub publish ref |
| orch.git.ftr-sub-topology | conforms | Under ftr AST-871 |
| orch.git.merge-on-checkout | conforms | Merge AST-970 prerequisite |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrites |
| orch.git.no-dev-agent-branches | conforms | No agent branches |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Phase A only on CLI after Susan OK; ensure = B/C only |
| orch.pipeline.plan-is-bible | conforms | Feature plan on publish ref |
| orch.pipeline.project-scoped-queues | conforms | Untouched |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready re-validate after discuss |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Ada on APPROVED |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | N/A |
| astral.agent.do-task-delegation | conforms | N/A |
| astral.agent.grade-vector-validation | conforms | N/A |
| astral.batch.batch-id-first | conforms | No new claim APIs |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Cascade only |
| astral.config.config-source-of-truth | conforms | Legacy map in config |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets |
| astral.debug.spikes-under-debug-dir | conforms | Production data-model doc |
| astral.docs.features-single-file-per-ticket | conforms | docs/features/candidate/ |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O |
| astral.layers.import-direction | conforms | CLI → data/core |
| astral.layers.scripts-exempt-from-layer-rules | conforms | Migration CLI under scripts/ |
| astral.layers.ui-config-driven-business-logic | conforms | UI copy only; states from API |
| astral.patterns.coat-check-never-store-empty | conforms | N/A |
| astral.patterns.render-verdict-orchestrates-consult | conforms | N/A |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new endpoints |
| astral.standards.data-raises-caller-logs | conforms | Data owns migrate/hard-delete |
| astral.standards.database-header-inventory | conforms | Inventoried tables only |
| astral.standards.debug-contract-gated | conforms | No new debug contract |
| astral.standards.dry-and-focused-functions | conforms | Single map + one migrate writer |
| astral.standards.in-scope-only | conforms | Sibling boundaries respected |
| astral.standards.logging-via-utils | conforms | CLI prints OK |
| astral.standards.no-cross-contamination | conforms | Layered files |
| astral.standards.no-hardcoded-sets | conforms | Remap table in config |
| astral.standards.public-then-helpers | conforms | Core wrappers + data migrate |
| astral.standards.utils-data-late-import-only | conforms | Config-only utils |
| astral.state.core-decides-transitions | conforms | Remap is cutover; hard-delete ≠ state hop |
| astral.state.job-prior-states-enforced | conforms | Job/company NEW not remapped |
| astral.state.no-daisy-chain-in-run | conforms | No multi-state dispatch chain |
| astral.ui.frontend-file-placement | conforms | Existing flat page |
| astral.ui.naming-conventions | conforms | No new files/routes |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** all rows above (54).

**Excluded:**
- `astral.debug.no-repo-root-artifacts-dir` — paths miss
- `astral.git.engineer-test-tree-ban` — paths miss

## Findings

### fix-now
None. Round-1 fix-now closed: Phase A = pre-cutover DELETED only (missing `lifecycle.reap_started_at`), CLI `--execute` only; schema-ensure = `phases="BC"` only.

### discuss (resolved in plan Decisions — non-blocking)
1. `agent_data` orphans left intentionally (no `entity_id`).
2. Company/job orphan FK posture accepted for UAT.
3. Unknown→NEW_CANDIDATE audited via `states_unknown_to_new_candidate`.

### acceptable
- Candidate-only NEW trigger remap; preserve `state_changed_at`; grep gate; HIGH risk honest with CLI gates.

**Self-assessment:** MAJOR-CHANGE / high / HIGH — honest.

— Joan
context_tokens≈82000

#### ada — 2026-07-23T23:16:26.343Z
[plan-discuss] round=1 reply

**fix-now:** Split cutover from steady-state.
- Phase A hard-deletes only **pre-cutover** `DELETED` (missing `lifecycle.reap_started_at`); never all `DELETED`.
- Schema-ensure calls `migrate_legacy_candidate_states(phases="BC")` only — remaps, no hard-delete.
- Irreversible Phase A stays on CLI `--execute` (phases `ABC`) after Susan OK / dry-run; Stage 2 handles reap-due post-cutover soft deletes.

**Discuss resolutions (in plan Decisions):**
1. **`agent_data`:** leave orphans (no `entity_id`); cascade `agent_responses` via `(entity_type, entity_id)`.
2. **Company/job `candidate_id`:** orphan FK posture confirmed acceptable for UAT (no tenant wipe).
3. **Unknown states → `NEW_CANDIDATE`:** count + list `astral_candidate_id`/old state in migrate return (`states_unknown_to_new_candidate`) for auditability.

Published @ `935226a` on `origin/sub/AST-871/AST-973-legacy-candidate-migration`. Returning to **Plan Ready** for Joan re-validate.

— Ada

#### joan — 2026-07-23T23:10:15.786Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-973
**Overall:** REVISE
**Publish ref:** `origin/sub/AST-871/AST-973-legacy-candidate-migration`
**Implementer:** Ada Lovelace

## Traceability

### Parent / child AC → plan stages

| AC | Coverage |
| -- | -- |
| **#8** LIVE_PROMPTS→ACTIVE_SEARCH; hard-delete existing DELETED; other legacy→NEW_CANDIDATE; no silent loss for remapped live rows | Stage 1 map + Phase A/B; Stage 4 doc |
| **#9** dispatch_task / task-config keys off retired states; no orphaned LIVE_PROMPTS | Stage 1 Phase C + Stage 3 grep / INFLOW confirm |
| **#10** Nav and state-gated UI resolve on new states | Stage 3 consumer sweep + AST-970 config gates; Manage Candidates copy |
| Parent AC 1–7 | N/A — registry/history/dispatch claim Boundaries |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Config map + DB migrate | Legacy migration + dispatch trigger remaps |
| 2 Reap-due hard delete | DELETED reap completion (AST-970 timer) |
| 3 Consumer sweep + grep | State consumers coherent; retired names gone |
| 4 Data-model doc | Cutover contract for operators/AST-869 readers |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge SHA |
| orch.git.commit-vocabulary | conforms | Plan-only |
| orch.git.flow-direction-inviolable | conforms | Child sub publish ref |
| orch.git.ftr-sub-topology | conforms | Under ftr AST-871 |
| orch.git.merge-on-checkout | conforms | Merge AST-970 prerequisite |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrites |
| orch.git.no-dev-agent-branches | conforms | No agent branches |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | needs-discussion | CLI says Susan OK before `--execute`; ensure-path auto live migrate undercuts that |
| orch.pipeline.plan-is-bible | conforms | Feature plan on publish ref |
| orch.pipeline.project-scoped-queues | conforms | Untouched |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly no tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Ada on REVISE |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | N/A |
| astral.agent.do-task-delegation | conforms | N/A |
| astral.agent.grade-vector-validation | conforms | N/A |
| astral.batch.batch-id-first | conforms | No new claim APIs |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Cascade only; no latest-only rewrite |
| astral.config.config-source-of-truth | conforms | Legacy map in config |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets |
| astral.debug.spikes-under-debug-dir | conforms | Production data-model doc, not spike output |
| astral.docs.features-single-file-per-ticket | conforms | Docs under docs/features/candidate/ |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O |
| astral.layers.import-direction | conforms | CLI → data/core; layers respected |
| astral.layers.scripts-exempt-from-layer-rules | conforms | Migration CLI under scripts/ |
| astral.layers.ui-config-driven-business-logic | conforms | UI copy only; states from API |
| astral.patterns.coat-check-never-store-empty | conforms | N/A |
| astral.patterns.render-verdict-orchestrates-consult | conforms | N/A |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new endpoints |
| astral.standards.data-raises-caller-logs | conforms | Data owns migrate/hard-delete |
| astral.standards.database-header-inventory | conforms | Uses inventoried tables; no new undeclared tables |
| astral.standards.debug-contract-gated | conforms | No new debug contract |
| astral.standards.dry-and-focused-functions | conforms | Single map + one migrate writer |
| astral.standards.in-scope-only | conforms | Registry/history/claim wiring left to siblings |
| astral.standards.logging-via-utils | conforms | No print in product paths (CLI prints OK) |
| astral.standards.no-cross-contamination | conforms | Layered files |
| astral.standards.no-hardcoded-sets | conforms | Remap table in config |
| astral.standards.public-then-helpers | conforms | Core wrappers + data migrate |
| astral.standards.utils-data-late-import-only | conforms | Config-only utils |
| astral.state.core-decides-transitions | conforms | Remap is cutover, not runtime transition policy; hard-delete ≠ state hop |
| astral.state.job-prior-states-enforced | conforms | Job/company `NEW` not remapped |
| astral.state.no-daisy-chain-in-run | conforms | No multi-state dispatch chain |
| astral.ui.frontend-file-placement | conforms | Existing flat page edit |
| astral.ui.naming-conventions | conforms | No new files/routes |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** all rows above (54).

**Excluded:**
- `astral.debug.no-repo-root-artifacts-dir` — paths (`artifacts/**`, `scripts/spikes/**`) miss plan paths
- `astral.git.engineer-test-tree-ban` — paths (`tests/**`, test-bible, …) miss plan paths

## Findings

### fix-now
1. **Location:** Stage 1 Phase A + step 4 (schema-ensure auto-run)
   **Finding:** Phase A is `WHERE state = 'DELETED'` → hard-delete. After AST-970, `DELETED` remains a **live** registry state for soft-delete + reap. Binding full migrate (`dry_run=False`) to candidate schema-ensure means **every** ensure/server load permanently destroys all soft-deleted candidates (including those with `lifecycle.reap_started_at` still counting down). That collapses AC#2’s reap window and contradicts Stage 2 / CLI “Susan OK” / `--dry-run` default. Idempotency “second run counts zero” does **not** hold for Phase A while any `DELETED` rows exist.
   **Recommendation:** Split cutover from steady-state:
   - Phase A only targets **pre-cutover** DELETED (e.g. missing `candidate_data.lifecycle.reap_started_at`) **or** runs once behind an explicit migration marker.
   - Schema-ensure may run Phase B/C (state/trigger remaps) safely; do **not** hard-delete all `DELETED` on every ensure.
   - Irreversible Phase A / purge stays on CLI `--execute` (and Stage 2 reap-due) after dry-run.

### discuss
1. `agent_data` has `entity_type` but **no** `entity_id` — cascade step must name a real join (e.g. via `agent_responses`/`batch_id`) or explicitly leave orphans.
2. Companies/jobs retaining `candidate_id` after hard-delete — Decision is clear; confirm acceptable orphan FK posture for UAT.
3. Unknown non-registry candidate states → `NEW_CANDIDATE` — parent wants that for legacy; log/count those rows so “no silent data loss” is auditable.

### acceptable
- Candidate-only `NEW` trigger remap vs job/company `NEW` is correctly guarded.
- Preserving `state_changed_at` on remap protects stale clocks.
- Grep gate + bootstrap/script sweep match AC#9–#10.
- Self-assessment MAJOR-CHANGE / high / HIGH is honest; HIGH risk is why Phase A must not ride ensure.

Update plan on publish ref → Plan Ready + Joan re-validate.

— Joan
context_tokens≈68000

#### joan — 2026-07-23T23:03:30.070Z
[validate-plan] blocked — assignee gate

Status is **Plan Ready**, but assignee is **Ada Lovelace**, not Joan.

Chuckles must assign **Joan** (`susan+joan@susansomerset.com`) before validate-plan runs. No rubric pass until then.

— Joan
context_tokens≈18000

#### ada — 2026-07-23T23:01:25.127Z
Plan published on `origin/sub/AST-871/AST-973-legacy-candidate-migration` @ `0f54de9`.

**Plan:** [docs/features/candidate/ast-973-legacy-candidate-migration.md](https://github.com/susansomerset/astral/blob/sub/AST-871/AST-973-legacy-candidate-migration/docs/features/candidate/ast-973-legacy-candidate-migration.md)

**Self-assessment**
- **Scope:** MAJOR-CHANGE — idempotent DB migrate (hard-delete pre-cutover `DELETED`, remap states + safe `dispatch_task` triggers), hard-delete/reap-due helpers, consumer/script sweep + grep gate; blocked by AST-970 vocabulary.
- **Conf:** high — parent AC #8–#10 and AST-970 handoff are explicit; remap rules keep job/company `NEW` untouched.
- **Risk:** HIGH — irreversible hard-delete and dispatch unique-key collisions; mitigated by CLI `--dry-run` default, idempotent ensure-path migrate, and dupe handling on trigger remap.

---

# Legacy candidate migration, consumers, and dispatch/task-config keys

**Linear:** [AST-973](https://linear.app/astralcareermatch/issue/AST-973/legacy-candidate-migration-consumers-and-dispatchtask-config-keys)  
**Parent:** [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine)  
**Publish ref:** `origin/sub/AST-871/AST-973-legacy-candidate-migration`  
**Blocked by:** AST-970 (vocabulary + transition enforcement)

Migrate persisted candidate rows and dispatch/task-config state keys off the retired four-step vocabulary onto the AST-970 registry; hard-delete existing `DELETED` candidate rows (not remap); finish consumer/nav/config string sweep so no product path still requires `NEW` / `PROFILE_READY` / `CONTEXT_READY` / `LIVE_PROMPTS` as candidate states. Does **not** invent new product flows, does **not** redefine the registry (AST-970), does **not** own transition history writes (AST-971) or dispatch claim/stale scheduling (AST-972).

**Prerequisite contract (from AST-970 plan):** runtime keys include `NEW_CANDIDATE`, `ACTIVE_SEARCH`, `DELETED`, etc.; `transition_candidate_state` enforces `prior_states`; `INFLOW_CONFIG` discovery trigger and `NAV_CONFIG` / `gen_states` already retargeted for config import coherence. This ticket owns DB remaps, hard-delete of legacy `DELETED` rows, remaining consumer literals, and a grep gate.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_LEGACY_STATE_MAP` + helper `remap_legacy_candidate_state(state)`; ensure any leftover candidate-facing literals after AST-970 are on the new vocabulary | utils |
| `src/data/database.py` | `migrate_legacy_candidate_states()` with Phase A (pre-cutover DELETED hard-delete, CLI-only) + Phase B/C remaps; `hard_delete_candidate`; schema-ensure invokes **Phase B/C only** | data |
| `src/core/candidate.py` | Thin wrappers: `hard_delete_candidate`, `purge_reap_due_candidates` (uses AST-970 `is_candidate_reap_due`); keep logical `delete_candidate` → `DELETED` | core |
| `scripts/migrations/migrate_legacy_candidate_states.py` | Operator CLI: `--dry-run` / live run wrapping the same migrate + optional `--purge-reap-due` | scripts |
| `scripts/migrations/bootstrap_candidate.py` | Stop writing retired states (`NEW` / `CONTEXT_READY`); use `CANDIDATE_CONFIG["initial_state"]` / `ACTIVE_SEARCH` as appropriate to the script’s intent | scripts |
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | Delete confirm copy: logical delete still sets `DELETED` (reap later); no hardcoded legacy state names | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document legacy remap table + hard-delete of pre-cutover `DELETED` rows | docs |

**Out of scope:** AST-970 registry shape; AST-971 history table; AST-972 claim/aging schedule wiring; deleting companies/jobs owned by a hard-deleted candidate (see Decision).

## Stage 1: Config remap table + idempotent DB migration

**Done when:** Phase B/C remaps `LIVE_PROMPTS` → `ACTIVE_SEARCH` and other legacy candidate states → `NEW_CANDIDATE`, remaps dispatch trigger keys per rules below, and a second B/C run is a no-op. Phase A hard-deletes only **pre-cutover** `DELETED` rows (CLI `--execute`, not schema-ensure). After full CLI migrate, no candidate row remains whose `state` is outside `CANDIDATE_STATES`. Post-cutover soft-deleted candidates (`DELETED` + `lifecycle.reap_started_at`) are preserved until Stage 2 reap-due.

1. In `src/utils/config.py`, add (next to `CANDIDATE_CONFIG` from AST-970):

```python
# Retired four-step names → AST-970 registry. DELETED is not remapped (hard-deleted).
CANDIDATE_LEGACY_STATE_MAP = {
    "LIVE_PROMPTS": "ACTIVE_SEARCH",
    "NEW": "NEW_CANDIDATE",
    "PROFILE_READY": "NEW_CANDIDATE",
    "CONTEXT_READY": "NEW_CANDIDATE",
}

# Candidate-only legacy labels (never job/company registry keys). Safe to remap on any
# dispatch_task.trigger_state regardless of entity_type.
CANDIDATE_LEGACY_TRIGGER_STATES = frozenset({
    "LIVE_PROMPTS", "PROFILE_READY", "CONTEXT_READY",
})

def remap_legacy_candidate_state(state: str) -> str:
    """Map a persisted candidate.state value onto CANDIDATE_STATES keys.
    Unknown non-empty values that are not already registry keys → NEW_CANDIDATE.
    Empty/None → CANDIDATE_CONFIG['initial_state']. Does not handle DELETED."""
```

   Implement `remap_legacy_candidate_state` exactly:
   - If `state` in `CANDIDATE_STATES`: return `state`.
   - If `state` in `CANDIDATE_LEGACY_STATE_MAP`: return mapped value.
   - If `state` is `DELETED`: raise `ValueError` (caller must hard-delete, not remap).
   - Otherwise return `CANDIDATE_CONFIG["initial_state"]` (`NEW_CANDIDATE`).

   Assert every map **value** is in `CANDIDATE_STATES` and `"DELETED" not in CANDIDATE_LEGACY_STATE_MAP`.

2. In `src/data/database.py`, add `hard_delete_candidate(astral_candidate_id: str) -> Dict[str, int]` that, in one transaction, deletes candidate-scoped rows then the candidate row. Counts keys at minimum: `dispatch_task`, `candidate_intake_session`, `company_search_terms`, `rubric_vector`, `vector_feedback`, `agent_responses`, `candidate`.

   Cascade deletes:
   - `dispatch_task`, `candidate_intake_session`, `company_search_terms`, `rubric_vector`, `vector_feedback` where `candidate_id = ?`
   - `agent_responses` where `entity_type = 'candidate'` and `entity_id = ?`
   - then the `candidate` row

   Do **not** delete `job` or `company` rows. Do **not** delete `agent_data` rows.

   ⚠️ **Decision:** Hard-delete removes the candidate row and the satellites listed above. Companies/jobs that still point at that `candidate_id` are left in place (orphan FK posture — same as AST-729 leaving related rows for deleted jobs). Acceptable for UAT; full tenant wipe is out of scope.

   ⚠️ **Decision (`agent_data`):** `agent_data` has `entity_type` + `batch_id` but **no** `entity_id`. There is no reliable candidate-scoped join without inventing batch archaeology. Leave `agent_data` orphans; do not guess. Optionally delete `agent_data` rows only when a future ticket adds a durable candidate key.

3. Add `migrate_legacy_candidate_states(*, dry_run: bool = False, phases: str = "BC") -> Dict[str, int]` in `database.py`.

   `phases` is one of: `"A"`, `"BC"`, `"ABC"` (default `"BC"` for ensure-safe calls).

   **Phase A — hard-delete pre-cutover DELETED only (never all DELETED)**
   - Select candidates where `state = 'DELETED'` **and** `candidate_data.lifecycle.reap_started_at` is missing/empty (pre-AST-970 soft deletes / cutover leftovers).
   - Do **not** select post-cutover soft deletes that already have `lifecycle.reap_started_at` (those wait for Stage 2 `purge_reap_due_candidates`).
   - For each id: if `dry_run`, count only; else `hard_delete_candidate(id)`.
   - Count `deleted_hard_pre_cutover`.
   - ⚠️ **Decision:** Phase A is cutover cleanup, not steady-state reap. Binding “delete every DELETED” to schema-ensure would collapse AC#2’s reap window.

   **Phase B — remap candidate.state**
   - Select all remaining candidates whose `state` is **not** `DELETED` (DELETED rows are either pre-cutover handled by A, or live soft-deletes left alone).
   - For each row, compute `new_state = remap_legacy_candidate_state(old_state)` (skip if equal).
   - Track `states_remapped` and separately `states_unknown_to_new_candidate` when `old_state` was not in `CANDIDATE_STATES` and not in `CANDIDATE_LEGACY_STATE_MAP` (auditable “no silent data loss” — print/return the list of `astral_candidate_id` + old state in the counts/details dict).
   - If not dry_run: `UPDATE candidate SET state=?, updated_at=now` and **preserve** `state_changed_at` on remap so stale aging clocks are not reset by cutover.
   - Never write a state absent from `CANDIDATE_STATES`. Never remap `DELETED` via Phase B.

   **Phase C — remap dispatch_task.trigger_state**
   - For each `dispatch_task` row:
     - If `trigger_state` in `CANDIDATE_LEGACY_TRIGGER_STATES`: map via `CANDIDATE_LEGACY_STATE_MAP` (all such keys are in the map).
     - Else if `entity_type == 'candidate'` and `trigger_state == 'NEW'`: map to `NEW_CANDIDATE`.
     - Else if `entity_type == 'candidate'` and `trigger_state` not in `CANDIDATE_STATES` and not empty: map via `remap_legacy_candidate_state(trigger_state)`.
     - Do **not** remap job/company `NEW` / other job-company registry keys.
   - On unique conflicts `(candidate_id, task_key, trigger_state)` after remap: keep one row (prefer the pre-existing target-key row if present; else keep lowest `id`) and delete the duplicate. Count `dispatch_triggers_remapped`, `dispatch_trigger_dupes_removed`.

   Return counts dict. Phase B/C idempotent on second live run. Phase A idempotent once pre-cutover DELETED rows are gone (post-cutover DELETED with reap metadata remain and are **not** counted by A).

4. Schema-ensure (candidate `_ensure_*` on first DB access): call **only**
   `migrate_legacy_candidate_states(dry_run=False, phases="BC")`.
   Do **not** run Phase A from ensure. Do **not** hard-delete any `DELETED` row from ensure.

5. Add `scripts/migrations/migrate_legacy_candidate_states.py`:
   - argparse: `--dry-run` (default True unless `--execute`), `--execute` for live, `--phases` default `ABC` for operator cutover, `--purge-reap-due` optional (Stage 2).
   - Operator cutover path: `--dry-run` then `--execute` (phases ABC) **after Susan OK** on production — this is the only path that runs Phase A.
   - Print full counts including `states_unknown_to_new_candidate` detail lines; exit 0.
   - Docstring: backup DB first; ensure-path only self-heals B/C remaps.

## Stage 2: Reap-due hard delete (production timer completion)

**Done when:** Candidates in `DELETED` with due reap (AST-970 `lifecycle.reap_started_at`) can be hard-deleted via one core entrypoint; pre-cutover `DELETED` (no reap metadata) are handled only by Stage 1 Phase A on CLI `--execute`.

1. In `src/core/candidate.py`, add:

```python
def hard_delete_candidate(candidate_id: str) -> Dict[str, int]:
    """Physical delete — database.hard_delete_candidate. Not a state transition."""
    return database.hard_delete_candidate(candidate_id)

def purge_reap_due_candidates(*, now=None) -> int:
    """Hard-delete every candidate where is_candidate_reap_due(...). Return count."""
```

   Implementation: `list_candidates(include_deleted=True)`, filter `state=='DELETED'` and `is_candidate_reap_due`, call `hard_delete_candidate` each. No dispatcher registration here (AST-972 may call later; CLI `--purge-reap-due` is enough for this ticket).

2. Wire `scripts/migrations/migrate_legacy_candidate_states.py --purge-reap-due` to call `purge_reap_due_candidates` after (or instead of, when flag-only) the legacy migrate when `--execute` is set. Dry-run lists due ids without deleting.

## Stage 3: Consumer sweep + grep gate

**Done when:** Under `src/` and `scripts/` (product paths), no remaining required use of retired candidate state string literals as live vocabulary; admin UI still loads states from `/api/candidates/states`; Manage Candidates delete copy does not claim hard-delete.

1. After AST-970’s config-local retargets, finish any remaining product consumers this ticket owns:
   - `scripts/migrations/bootstrap_candidate.py`: replace `state="NEW"` / `state="CONTEXT_READY"` with `CANDIDATE_CONFIG["initial_state"]` and, for the “ready for prompts” bootstrap end state, `ACTIVE_SEARCH` (script intent: candidate usable for generation — document in a one-line comment).
   - `src/ui/frontend/src/pages/AdminManageCandidates.tsx`: keep confirm as logical delete to `DELETED`; do not introduce hardcoded `LIVE_PROMPTS` / `PROFILE_READY` / etc. (states already from API).
   - Grep `src/` + `scripts/` for `LIVE_PROMPTS`, `PROFILE_READY`, `CONTEXT_READY` as candidate vocabulary. Allowed leftovers: comments pointing at this migration, `CANDIDATE_LEGACY_*` map keys, and string literals inside `migrate_legacy_candidate_states` / remap helpers. Job/company uses of unrelated tokens must not be rewritten.
   - Confirm `INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]` is `ACTIVE_SEARCH` (AST-970); if still `LIVE_PROMPTS` on the integration line when this builds, set it here (consumer coherence).

2. Grep gate (builder runs before stage-complete commit):

```bash
rg -n 'LIVE_PROMPTS|PROFILE_READY|CONTEXT_READY' src scripts \
  --glob '!**/migrate_legacy_candidate_states*' 
# Fail the stage if matches remain outside CANDIDATE_LEGACY_* definitions,
# remap helpers, or explicit "legacy" comments in database migrate function.
```

   Also assert no `candidate_state_transitions` key remains (AST-970 removal); if present, stop and escalate — do not reintroduce.

3. Do **not** edit `tests/` or the test bible (Betty). Do **not** expand nav beyond ensuring config gates use new names (AST-970 + this sweep).

## Stage 4: Data-model doc note

**Done when:** `CANDIDATE_DATA_MODEL.md` documents the one-time remap table and that **pre-cutover** `DELETED` rows (no `lifecycle.reap_started_at`) are hard-deleted only via CLI Phase A; post-cutover DELETED use reap-due purge.

1. Append a short **Legacy cutover (AST-973)** subsection under the state machine section:
   - Map table matching `CANDIDATE_LEGACY_STATE_MAP`.
   - Pre-cutover `DELETED` (no reap metadata) → CLI Phase A hard delete (not remapped). Post-cutover `DELETED` kept until reap-due.
   - `dispatch_task.trigger_state`: `LIVE_PROMPTS`/`PROFILE_READY`/`CONTEXT_READY` always; `NEW` only when `entity_type='candidate'`.
   - Schema-ensure runs Phase B/C only; operator script runs Phase ABC after Susan OK.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — data-layer migration + hard-delete cascade + config remap table + consumer/script sweep; depends on AST-970 registry already on the branch line at build time.

**Conf:** `high` — parent AC #8–#10 and AST-970 out-of-scope handoff are explicit; remap rules distinguish candidate-only triggers from job/company `NEW`.

**Risk:** `HIGH` — wrong dispatch remap could break scheduled actions; hard-delete is irreversible; mitigated by CLI `--dry-run` default, Phase A only on CLI for pre-cutover DELETED (ensure = B/C only), auditable unknown-state counts, unique-constraint dupe handling, and preserving `state_changed_at` on remap.

## Code Rules self-review

| Rule | Result |
|------|--------|
| §1.3 DRY | Single map in config; database migrate is the only writer of remaps |
| §2.1 config SSOT | Legacy map + new vocabulary in config; no hardcoded remap dict in the CLI |
| §2.4 batch | No new claim APIs |
| §2.6 state machine | Remap runs before enforcement; does not invent transitions; hard-delete is not a state hop |
| §3.3 imports | CLI → database/core; core wraps data hard-delete |
| §3.5 naming | Legacy keys only inside `CANDIDATE_LEGACY_*` |

No unresolved conflicts with AST-970 boundaries.

## Revisions

Revision 1 — 2026-07-23
Driven by: Joan `[plan-discuss] round=1 concern` fix-now — schema-ensure must not hard-delete all live `DELETED` rows (collapses AST-970 reap window).
Changes:
- Split Phase A (pre-cutover DELETED only, CLI `--execute`) from Phase B/C (ensure-safe remaps).
- Schema-ensure calls `phases="BC"` only; operator CLI defaults to `ABC` after Susan OK.
- `agent_data`: leave orphans (no `entity_id`); cascade `agent_responses` by `(entity_type, entity_id)`.
- Confirm orphan company/job `candidate_id` FK posture for UAT.
- Count/list unknown legacy states remapped to `NEW_CANDIDATE` for auditability.

## Review

| Field | Value |
| -- | -- |
| Ticket | AST-973 |
| Publish ref | `origin/sub/AST-871/AST-973-legacy-candidate-migration` |
| Built | `e5b05d77dc8be3759851953beedf47cd7a9338b5` |
| Notes | Stages 1–4: legacy map, migrate/hard-delete (ensure=BC), reap-due, consumer sweep. |

### Radia code-rubric.v1 (revision=1)

**Overall:** DISCUSS  
**Publish tip reviewed:** `b05c75c60e5119d26a66c676ea98fcb3c51866d9` (`origin/dev...origin/sub/AST-871/AST-973-legacy-candidate-migration`)

**What’s solid**
- `CANDIDATE_LEGACY_STATE_MAP` + remap helper; Phase A pre-cutover DELETED only on CLI; ensure = Phase B/C only; preserve `state_changed_at`; candidate-only `NEW` trigger remap; hard-delete/purge wrappers; CREATE default `NEW_CANDIDATE`; bootstrap + data-model cutover note.

**Issues**
- **discuss (C4 straggler):** Joan Excluded `astral.git.engineer-test-tree-ban`; tip includes Betty tests/bible so statute is in-scope. Substance **conforms**.
- **advisory:** `CANDIDATE_DATA_MODEL.md` context section still says four fields “gate the `CONTEXT_READY` state transition” (legacy narrative leftover outside the cutover table).

**Recommended actions**
- Engineer: acknowledge C4 straggler; optional one-line CONTEXT_READY doc cleanup.

## Resolution

2026-07-24 — Radia code-rubric.v1 revision=1 (**DISCUSS**; fix-now none).

| Finding | Action |
| -- | -- |
| discuss — C4 `engineer-test-tree-ban` straggler | Acknowledged: Betty owns tip `tests/**` + bible; engineer `code`/`docs` commits did not touch test-tree. No product change. |
| advisory — `CONTEXT_READY` leftover in data-model context section | One-line cleanup in `CANDIDATE_DATA_MODEL.md`: completeness helper, not a state-transition gate. |
