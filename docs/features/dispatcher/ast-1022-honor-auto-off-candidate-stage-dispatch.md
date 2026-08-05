<!-- linear-archive: AST-1022 archived 2026-08-05 -->

## Linear archive (AST-1022)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1022/honor-auto-off-for-candidate-stage-dispatch-dispatch-running-requested  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** Urgent / —  
**Parent:** AST-1018 — Dispatch running requested resume tasks despite the auto = false  
**Blocked by / blocks / related:** parent: AST-1018

### Description

## What this implements

Find and fix why `candidate_requested_resume` / `candidate_requested_artifacts` still auto-dispatch when AUTO is false. Tick must not spawn AUTO-off rows; CLICK Run must still work; existing operator AUTO settings must survive provision/boot; **new** stage rows seed AUTO **off**; debug skip lines when `debug=True`.

## Acceptance criteria

1. With AUTO off on a `candidate_requested_resume` row that has available work, after a scheduler tick (and without clicking Run), logs show no dispatch start for that row.
2. Same as (1) for `candidate_requested_artifacts`.
3. With AUTO off, clicking Run on that row still starts a CLICK dispatch (or skips with the existing no-candidate/API-key message when applicable).
4. With AUTO on and available ≥ min_count, the tick still starts the row as before.
5. After Susan turns AUTO off in Scheduled Actions and restarts (or re-runs provision), that same row remains AUTO off — no silent re-enable.
6. Newly provisioned stage-dispatch rows for these two task keys are created with AUTO **off**.
7. When `debug=True` on a touched path, a skip-for-AUTO-off decision emits Style D index + `|` detail naming the task/candidate and outcome.

## Boundaries

Does not own craft prompts or candidate state redesign. Does not redesign REQUESTED_RESUME / REQUESTED_ARTIFACTS workers. Does not reintroduce automatic re-seed of deleted dispatch_task rows (AST-745).

## Notes for planning

Stage provision today hardcodes AUTO on for these keys (AST-972). Susan confirmed new rows seed AUTO **off**. Dispatcher tick already filters `auto_mode=1` via `get_due_tasks` — investigate seed/default, toggle persist, and any path that still spawns AUTO-off rows.

**Citations:** `pattern.batch.entity-claim-process-release`, `pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.config.config-source-of-truth`, `astral.standards.debug-contract-gated`, `astral.standards.logging-via-utils`, `astral.standards.in-scope-only`, `astral.standards.no-hardcoded-sets`, `astral.batch.claim-process-release`, `astral.layers.import-direction` (+ full universal set for plan/code review).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1018-honor-auto-off-candidate-stage-dispatch`, child `sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch`. Publish to `origin/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch` only.

### Comments

#### radia — 2026-07-29T02:54:36.605Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1022
**Publish ref:** `8772fb17` (`origin/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch`)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch`
**Layers:** core, docs, utils · **Change types:** add, modify
**Notes:** Plan-rubric verdict attached (APPROVED). Joan discuss on hardcoded `index=1,total=1` was fixed in Stage 2 (collect eligible → `N/M`). C4 stragglers below — no product fix-now.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1022)` SHA `359c046c` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary used |
| orch.git.flow-direction-inviolable | universal | conforms | Published to child `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | Matches parent Git table publish-ref |
| orch.git.merge-on-checkout | universal | conforms | No procedure skipping ftr merge |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Linear history; no rewrite ops in tip range |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket sub branch only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-1018` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | AUTO-off seed already decided on parent |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match plan; out-of-scope held |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Dispatcher child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | `test()`/`merge-tests()` separate from engineer `code()` |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Assignee left Ada through review |
| orch.roles.pre-commit-path-bans | universal | conforms | Role path bans honored on commit set |
| astral.agent.confidence-bounds | scoped | conforms | No confidence/scoring paths touched |
| astral.agent.do-task-delegation | scoped | conforms | No do_task / AI delegation changes |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector paths touched |
| astral.batch.batch-id-first | scoped | conforms | No claim API signature changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id format changes |
| astral.batch.claim-process-release | scoped | conforms | AUTO-on / CLICK claim path unchanged; helper never runs |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | Seed `auto_mode` on `CANDIDATE_STAGE_DISPATCH`; ensure reads it |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | predicate failed: paths |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Features plan doc — not a spike under features/ |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/dispatcher/ast-1022-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer owns src/features; Betty only tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code()` SHAs touch only `src/`; tests via Betty |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Fix stays core + utils |
| astral.layers.import-direction | scoped | conforms | No new imports; core→data/utils unchanged |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | predicate failed: layers,paths |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Config seed only; no UI business logic |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | predicate failed: layers,paths |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer logging; tick except path unchanged |
| astral.standards.database-header-inventory | scoped | not-applicable | predicate failed: layers,paths |
| astral.standards.debug-contract-gated | scoped | conforms | Style D only when row `debug` truthy; index N/M honest |
| astral.standards.dry-and-focused-functions | scoped | conforms | One private skip helper; ensure stays insert-only |
| astral.standards.in-scope-only | scoped | conforms | Stage keys only; no workers/UI/AST-745 re-seed |
| astral.standards.logging-via-utils | scoped | conforms | `debug_index` / `debug_detail` via utils logger |
| astral.standards.no-cross-contamination | scoped | conforms | Layered structure preserved |
| astral.standards.no-hardcoded-sets | scoped | conforms | Stage keys from `CANDIDATE_STAGE_DISPATCH.values()` |
| astral.standards.public-then-helpers | scoped | conforms | `_debug_log_auto_off_stage_skips` above `_tick_loop` |
| astral.standards.utils-data-late-import-only | scoped | conforms | Config-only utils change; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | No candidate state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | not-applicable | predicate failed: layers,paths |
| astral.ui.naming-conventions | scoped | not-applicable | predicate failed: layers,paths |
| astral.ui.single-gunicorn-worker | scoped | conforms | Config touch unrelated to gunicorn |

## Pattern conformance

| cited | verdict |
| -- | -- |
| pattern.batch.entity-claim-process-release | conforms (claim path unchanged) |
| pattern.config.config-block | conforms (`CANDIDATE_STAGE_DISPATCH` seed) |
| pattern.layers.import-discipline | conforms |
| astral.config.config-source-of-truth | conforms (statute row) |
| astral.standards.debug-contract-gated | conforms |
| astral.standards.logging-via-utils | conforms |
| astral.standards.in-scope-only | conforms |
| astral.standards.no-hardcoded-sets | conforms |
| astral.batch.claim-process-release | conforms |
| astral.layers.import-direction | conforms |

## Plan adherence

Self-Assessment Scope Single-Component matches footprint (`config.py` + `dispatcher.py` + docs/tests). Stages 1–2 implemented as written; AC1–7 covered by seed-off + existing `get_due_tasks` filter + Style D side path; no existing-row AUTO rewrite; Joan’s N/M honesty discuss addressed in code.

## Findings

### fix-now
(none)

### discuss
1. **C4 straggler — `astral.debug.spikes-under-debug-dir`:** Joan excluded; diff adds `docs/features/**` so in-scope. Verdict remains **conforms** (plan file, not a spike).
2. **C4 straggler — `astral.docs.features-single-file-per-ticket`:** Joan excluded; now in-scope. **conforms** (single features file).
3. **C4 straggler — `astral.git.engineer-test-tree-ban`:** Joan excluded; tests/bible in three-dot diff. **conforms** (Betty `test`/`merge-tests`; engineer `code` = `src/` only).

### advisory
(none)

## What’s solid

- Smoking-gun seed default flipped in config; ensure reads it; insert-missing only.
- Tick debug helper scoped + gated; never spawns; Style D N/M batch honesty.
- CLICK / AUTO-on paths left intact.

## Recommended actions

- resolve-child: acknowledge C4 stragglers (no product edit required).

context_tokens≈42000

#### betty — 2026-07-29T02:50:08.402Z
## QA test manifest — AST-1022

`origin/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch` @ `359c046c` (`merge-tests(AST-1022): origin/tests 0fe065c2`).

### 1. Existing coverage (bible-backed)
1. `tests/component/core/test_dispatcher.py::TestScheduler::test_tick_loop_spawns_due_auto_tasks` — AUTO-on tick still spawns (AC4)
2. `tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch` — ensure idempotent / provision / claim gate unchanged
3. CLICK with `auto_mode=0` — existing `TestDispatchOne` / run_task AUTO-off paths (AC3; no product change)

### 2. Broken / obsolete (revised this pass)
1. `_run_one_tick` + `TestScheduler::test_tick_loop_calls_clear_after_wait_then_stops` — stub `list_dispatch_tasks` → `[]` so the new Style D side path stays DB-free (same contract as AST-972 `age_stale` stub)

### 3. Gaps (new this pass)
1. `tests/component/utils/test_config.py::TestAst1022HonorAutoOffStageDispatch` — both stage entries seed `auto_mode is False` (AC6)
2. `tests/component/core/test_dispatcher.py::TestAst1022HonorAutoOffStageDispatch`
   - `test_ensure_seeds_auto_mode_false` (AC6)
   - `test_ensure_does_not_rewrite_existing_auto_mode` (AC5)
   - `test_debug_log_auto_off_stage_skips_style_d` — index N/M, stage keys only, no `run_task` (AC1/2/7)
   - `test_debug_log_skips_when_below_min_count`
   - `test_tick_loop_calls_auto_off_debug_helper_before_spawn` — helper before AUTO-on spawn (AC4 + AC7 wiring)

**Integration:** no existing `tests/integration/` scenarios for these stage keys — no drift revision.

### Narrowed run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1022HonorAutoOffStageDispatch \
  tests/component/core/test_dispatcher.py::TestAst1022HonorAutoOffStageDispatch \
  tests/component/core/test_dispatcher.py::TestScheduler \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch \
  -q
```

### Bible shasums on publish-ref
- `docs/test-bible/core/dispatcher.md` — `c7781cc62fdb235390c3a5c129eb2cfe04b5716f`
- `docs/test-bible/utils/config.md` — `c66654321929cb8be431c762e3dd32619411771b`

— Betty

#### joan — 2026-07-29T02:40:11.646Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1022
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `e223114f`. Publish ref `origin/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch`. Diagnosis verified: `ensure_candidate_stage_dispatch_tasks` hardcodes `auto_mode=True`; `get_due_tasks` already `WHERE auto_mode = 1`; ensure skips existing pairs; CLICK `run_task(..., ui_initiated=True)` does not require AUTO on.
**Implementer:** Ada (parent Team table / plan author).

## Traceability

### Parent / child AC → plan stages

| AC | Plan coverage |
| -- | -- |
| 1 Tick does not start AUTO-off `candidate_requested_resume` | Already enforced by `get_due_tasks`; Stage 1 keeps seed off so new rows stay out of due set; Stage 2 does not spawn |
| 2 Same for `candidate_requested_artifacts` | Same as AC1 |
| 3 CLICK Run still works with AUTO off | Confirm-only Stage 1.3 / Stage 2.3 — no change to `run_task` |
| 4 AUTO on still ticks when available ≥ min_count | Stage 1–2 leave due/spawn selection intact |
| 5 Operator AUTO off survives restart/provision | Stage 1.2 — ensure remains insert-missing only; no `update_dispatch_task` on existing |
| 6 New stage rows seed AUTO **off** | Stage 1 — `CANDIDATE_STAGE_DISPATCH` `auto_mode: False` + ensure reads it |
| 7 Style D skip when debug on touched AUTO-off path | Stage 2 — tick side-path for stage keys with row `debug` truthy |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Config seed + ensure reads it | Purpose / Functional scope 4–5 / AC5–6; config-as-source-of-truth |
| 2 Tick Style D AUTO-off skips | Functional scope 7 / AC7; debug-contract-gated |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1022):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No procedure that skips ftr merge |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1018` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | AUTO-off seed already decided by Susan / parent |
| orch.pipeline.plan-is-bible | conforms | Stages binding; UI/workers excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Dispatcher |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | Untouched |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched when rows do run |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Claim/process/release unchanged for AUTO-on / CLICK |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Seed `auto_mode` on `CANDIDATE_STAGE_DISPATCH`, not a lone dispatcher literal |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | Fix stays core + utils |
| astral.layers.import-direction | conforms | Core → data/utils; no new layer violations |
| astral.layers.ui-config-driven-business-logic | conforms | No UI changes |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging |
| astral.standards.debug-contract-gated | conforms | Style D only when row `debug` truthy; no spawn from helper |
| astral.standards.dry-and-focused-functions | conforms | One tick skip helper; ensure stays insert-only |
| astral.standards.in-scope-only | conforms | Stage keys only; no craft workers / UI / AST-745 re-seed |
| astral.standards.logging-via-utils | conforms | Style D logger helpers |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | Stage keys from `CANDIDATE_STAGE_DISPATCH` |
| astral.standards.public-then-helpers | conforms | Private helper placement called out |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | No candidate state machine changes |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

### fix-now
(none)

### discuss
1. **Location:** Stage 2 helper snippet — `debug_index(..., index=1, total=1)`
   **Finding:** If multiple stage AUTO-off + `debug` rows meet the available threshold in one tick, hardcoding `1/1` weakens Style D `index N/M` honesty (§1.5.1).
   **Recommendation:** Collect eligible skip rows first, then emit `index=i, total=len(eligible)` while enumerating. Non-blocking — build may correct without a plan rewrite if Ada treats the snippet as illustrative.

### acceptable
1. No one-time migration flipping already-seeded AUTO-on rows — AC6 is new-seed only; AC5 is toggle stick; operator turns existing rows off.
2. Tick spawn eligibility unchanged — AC1/AC2 already true once DB `auto_mode=0`; Stage 1 makes new seeds match product default.
3. Template-apply copy of `auto_mode` left out of scope — not boot provision; called out.
4. Self-assessment Single-Component / high / Medium — honest; seed smoking gun verified in tree.
5. Row `debug` column as AC7 gate matches existing `run_task` debug pattern.

— Joan
context_tokens≈48000

#### ada — 2026-07-29T02:36:33.834Z
Plan: [`docs/features/dispatcher/ast-1022-honor-auto-off-candidate-stage-dispatch.md`](https://github.com/susansomerset/astral/blob/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch/docs/features/dispatcher/ast-1022-honor-auto-off-candidate-stage-dispatch.md) @ `e223114f` on `origin/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch`.

**Scope:** Single-Component — `CANDIDATE_STAGE_DISPATCH` seed `auto_mode: False` + `ensure_candidate_stage_dispatch_tasks` reads it; tick-only Style D skip for debug-flagged AUTO-off stage rows. No UI/data schema.

**Conf:** high — AST-972 hardcoded `auto_mode=True` is the seed bug; `get_due_tasks` already gates tick spawn; ensure already skips existing pairs so operator toggles survive boot provision.

**Risk:** Medium — bad seed default or overly broad tick debug could hide AUTO-on work or spam logs; mitigated by config False default, stage-key filter from `CANDIDATE_STAGE_DISPATCH`, and row `debug` gate.

#### chuckles — 2026-07-28T19:29:28.383Z
[check-linear] Todo — idle because parent AST-1018 datt has not spawned the Ada plan-child drone yet (parent ## Team still empty)

#### susan — 2026-07-28T19:25:59.470Z
@chuckles Why has this ticket been idle for 48 minutes?

---

# AST-1022 — Honor AUTO off for candidate stage dispatch

**Linear:** [AST-1022](https://linear.app/astralcareermatch/issue/AST-1022/honor-auto-off-for-candidate-stage-dispatch-dispatch-running-requested)
**Parent:** [AST-1018](https://linear.app/astralcareermatch/issue/AST-1018/dispatch-running-requested-resume-tasks-despite-the-auto-false)
**Publish ref:** `origin/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch`

Candidate stage-dispatch rows (`candidate_requested_resume` / `candidate_requested_artifacts`) were provisioned with AUTO on (AST-972). Operators turn AUTO off in Scheduled Actions expecting CLICK-only, but new seeds keep waking on the tick and any silent re-enable would fight the toggle. This ticket makes the seed default AUTO **off**, keeps existing operator toggles across boot/provision, leaves tick/`get_due_tasks` AUTO filtering intact (CLICK Run still works), and adds Style D debug when a debug-flagged AUTO-off stage row is skipped on the tick.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `auto_mode: False` seed default on each `CANDIDATE_STAGE_DISPATCH` entry | utils |
| `src/core/dispatcher.py` | Read seed `auto_mode` from config in `ensure_candidate_stage_dispatch_tasks`; tick-path Style D skip for AUTO-off + `debug=True` stage rows with available work | core |

**Out of scope:** craft prompts / REQUESTED_* workers; Scheduled Actions UI redesign; unrelated `task_key`s; re-seeding deleted `dispatch_task` rows (AST-745); one-time migration flipping already-seeded AUTO-on rows (operator toggle + new-seed default cover AC); changing `set_dispatch_tasks_from_template_rows` copy semantics (operator-initiated template apply may still copy template `auto_mode` — that is not boot provision).

---

## Diagnosis (code-backed)

1. **Seed hardcodes AUTO on.** `ensure_candidate_stage_dispatch_tasks` in `src/core/dispatcher.py` calls `database.save_dispatch_task(..., auto_mode=True, ...)` for every missing `(task_key, trigger_state)` pair from `CANDIDATE_STAGE_DISPATCH`. That matches AST-972 plan wording and explains AC6 failure for new rows.
2. **Tick already filters AUTO.** `database.get_due_tasks()` selects `WHERE auto_mode = 1`; `_tick_loop` only `run_task`s that list. `run_task(..., ui_initiated=True)` from admin Run does **not** require `auto_mode=1` — CLICK path is already correct for AC3.
3. **Provision does not rewrite existing rows.** `ensure_candidate_stage_dispatch_tasks` skips when `(task_key, trigger_state)` already exists — no `update_dispatch_task` on AUTO. Boot `provision_candidate_stage_dispatch_tasks` only calls ensure. AC5 holds for that path today; do not add writes that flip `auto_mode` on existing rows.
4. **No Style D AUTO-off skip today.** Tick never sees `auto_mode=0` rows, so AC7 needs an explicit debug-only side path for stage keys (not a change to spawn eligibility).

---

## Stage 1: Config seed default + ensure reads it

**Done when:** Both `CANDIDATE_STAGE_DISPATCH` entries declare `auto_mode: False`. A fresh `ensure_candidate_stage_dispatch_tasks(cid)` insert for a candidate missing those rows passes `auto_mode=False` into `save_dispatch_task`. A second ensure on the same candidate still skips existing pairs and does not call `update_dispatch_task` / `save_dispatch_task` for them. `get_due_tasks` SQL and `run_task` CLICK path are unchanged.

1. In `src/utils/config.py`, on `CANDIDATE_STAGE_DISPATCH["requested_resume"]` and `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]`, add the literal key `"auto_mode": False` next to the existing `task_key` / `trigger_state` fields (same bool shape as DB / `save_dispatch_task`).

   ⚠️ **Decision:** Seed default lives in `CANDIDATE_STAGE_DISPATCH` (config source of truth) — do **not** leave a bare `auto_mode=True`/`False` literal only in `dispatcher.py`. Do **not** add a parallel hardcoded set of stage task keys for this default.

2. In `src/core/dispatcher.py` `ensure_candidate_stage_dispatch_tasks`, replace the hardcoded `auto_mode=True` with the entry’s config value:

   ```python
   auto_mode=bool(entry.get("auto_mode", False)),
   ```

   Keep `min_count=1`, `batch_size=1`, `freq_hrs=0`, and the existing skip-if-`(tk, ts) in existing` logic exactly as today. Do **not** update `auto_mode` (or any column) on rows that already exist.

3. Do **not** edit `get_due_tasks`, `_tick_loop` spawn selection (except Stage 2 debug side path), `run_task`, admin AUTO toggle in `api_admin.py`, or React Scheduled Actions for this stage.

---

## Stage 2: Tick Style D skip for AUTO-off stage rows

**Done when:** On a tick, a `dispatch_task` whose `task_key` is one of the two `CANDIDATE_STAGE_DISPATCH[*]["task_key"]` values, with `auto_mode` falsy, `debug` truthy, and `count_eligible_for_dispatch_task(task) >= (min_count or 1)`, emits one Style D `debug_index` plus `|` `debug_detail` naming task_key, candidate_id, available count, and outcome that it was skipped because AUTO is off — and **does not** call `run_task` for that row. Rows with `debug` falsy emit nothing new. AUTO-on due rows still spawn as before.

1. In `src/core/dispatcher.py`, add a private helper (public-then-helpers: place below `_tick_loop` / near other scheduler helpers — if that would put it after a public function that currently sits below, put the helper immediately above `_tick_loop` instead so `_tick_loop` can call it without forward-reference noise):

   Name: `_debug_log_auto_off_stage_skips() -> None`.

   Behavior:
   - Build the frozenset of stage task_keys from `CANDIDATE_STAGE_DISPATCH.values()` → each `entry["task_key"]` (no inline string set of the two keys).
   - Load candidate stage rows for those keys that are AUTO off. Prefer: `database.list_dispatch_tasks()`, filter in Python to `task_key in stage_keys` and `not bool(task.get("auto_mode"))` and `bool(task.get("debug"))`. Do **not** add a new data-layer query unless list filtering is clearly wrong — keep this ticket off `database.py` if list is sufficient.
   - For each matching row with non-empty `entity_type`, `trigger_state`, and `candidate_id`: `avail = database.count_eligible_for_dispatch_task(task)`; if `avail < (task.get("min_count") or 1)`, continue (no log — not a would-have-run skip).
   - When the threshold is met: `logger.set_debug_flag(True)` then:

     ```python
     logger.debug_index(
         func="dispatcher._tick_loop",
         index=1,
         total=1,
         identifier=task.get("task_key"),
         outcome="skipped — AUTO off",
     )
     logger.debug_detail(
         f"candidate_id={task.get('candidate_id')!r} task_id={task.get('id')} "
         f"available={avail} min_count={task.get('min_count') or 1} auto_mode={task.get('auto_mode')}"
     )
     ```

   - Never call `run_task` from this helper.

   ⚠️ **Decision:** Scope debug AUTO-off skips to the two stage task_keys only (`in-scope-only`). Do not log every AUTO-off row in the catalog. Emit only when the row’s own `debug` column is truthy (debug-contract-gated — no new lines when debug is off).

2. In `_tick_loop`, after `due = database.get_due_tasks()` and **before** the spawn loop, call `_debug_log_auto_off_stage_skips()` inside the existing `try` (so failures are covered by the tick’s `except` / `_sched_log.exception`). Do not change `slots` / `run_task` selection logic.

3. Confirm by inspection (no product change required if already true):
   - `get_due_tasks` still `WHERE auto_mode = 1`.
   - Admin Run still uses `run_task(task_id, ui_initiated=True)` without requiring AUTO on.
   - `ensure_candidate_stage_dispatch_tasks` still never updates existing `auto_mode`.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch`.
- Do not edit `tests/`, `docs/test-bible/**`, or `docs/ASTRAL_TEST_BIBLE.md`.
- If `CANDIDATE_STAGE_DISPATCH` shape differs from what Stage 1 assumes, or `list_dispatch_tasks` is unsuitable for Stage 2, **stop** and comment on the **parent** (AST-1018) with the blocking format — do not invent a second seed path or data API.

---

## Self-Assessment

**Scope:** Single-Component — `config.py` seed field + `dispatcher.py` ensure + tick debug helper; no UI/data schema change.

**Conf:** high — smoking gun is the AST-972 `auto_mode=True` seed; tick/`get_due_tasks` already enforce AUTO for spawn; persist-on-provision already skips existing pairs.

**Risk:** Medium — wrong seed default or overly broad tick debug could hide real AUTO-on work or spam logs; mitigated by config-only False default, stage-key filter, and `debug` column gate.

---

## Rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY / focused helpers | Stage 2 isolates skip logging in one helper; ensure stays insert-only |
| §2.1 config source of truth | `auto_mode` seed on `CANDIDATE_STAGE_DISPATCH`, not a lone dispatcher literal |
| §2.4 batch claim-process-release | Unchanged when a row does run (AUTO on / CLICK) |
| §2.6 state machine | No candidate state changes |
| §1.5.1 debug contract | Style D + `\|` detail only when row `debug` is truthy |
| §1.4 no hardcoded sets | Stage keys from `CANDIDATE_STAGE_DISPATCH`, not inline frozenset of string literals |
| §3.3 import direction | Core already imports data + utils; no new layer violations |
| AST-745 | No re-seed of deleted rows; ensure remains insert-missing only |

---

## Review (build stub)

| Commit | Note |
|--------|------|
| `f0234c4c` | Stage 1 — `CANDIDATE_STAGE_DISPATCH.auto_mode=False`; ensure reads config |
| `de222da4` on `sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch` | Stage 2 — `_debug_log_auto_off_stage_skips` (Style D index N/M); Code Complete |

---

## Radia review — code-rubric.v1

`[code-rubric] revision=1` · tip reviewed `359c046c` · **Overall: DISCUSS** (C4 stragglers only; no product fix-now)

### What’s solid

- Stage 1: `CANDIDATE_STAGE_DISPATCH` seeds `auto_mode: False`; `ensure_candidate_stage_dispatch_tasks` reads `entry.get("auto_mode", False)` and still skips existing `(task_key, trigger_state)` pairs.
- Stage 2: `_debug_log_auto_off_stage_skips` scopes stage keys from config, gates on row `debug`, collects eligible then emits Style D `index N/M` (Joan’s plan-time `1/1` discuss addressed), never calls `run_task`.
- Tick spawn / `get_due_tasks` / CLICK path untouched; Betty test + bible commits are vocabulary-separated from engineer `code()` SHAs.

### Issues

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` at plan time; this three-dot diff brings them in-scope (`docs/features/**`, `tests/**` / bible). All three **conform** (plan is a features file not a spike; single `docs/features/dispatcher/ast-1022-…md`; engineer `code()` commits touch only `src/`).

### Recommended actions

- Resolve-child: acknowledge stragglers (no product change required unless Ada/Archie want a different reading).
- No fix-now product edits from this review.

---

## Resolution (AST-1022)

**Date:** 2026-07-29  
**Outcome:** Clean — no product changes. Radia **fix-now:** none. **Discuss:** C4 stragglers (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`) acknowledged as **conforms** (plan file / single features doc / engineer `code()` = `src/` only); no alternate reading.

**Publish tip after resolve:** `origin/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch`
