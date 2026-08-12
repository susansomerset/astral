<!-- linear-archive: AST-1134 archived 2026-08-11 -->

## Linear archive (AST-1134)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1134/retire-null-shell-candidate-bound-config-schema-provision-last-email  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1128 — gaze_email — candidate-bound dispatch (redesign)  
**Blocked by / blocks / related:** parent: AST-1128; blocks: AST-1135

### Description

## What this implements

Owns retiring the shared null-`candidate_id` `gaze_email` provision/shell as the primary design; moves TASK_CONFIG / `GAZE_EMAIL_CONFIG` expectations to candidate-bound rows (keep `unbound_retention_days`); adds `candidate.last_email_check` (default null); provisions a `gaze_email` row for **every** `candidate` via coverage join; removes always-visible-under-Avail-gt0 special-casing for this task once Avail is real. Does **not** own the per-message runner decision tree (sibling #3) or the live bind-filtered Avail count implementation detail beyond making the shell honest (sibling #2).

## Acceptance criteria

- [X] 1. There is no primary shared null-`candidate_id` `gaze_email` dispatch row in active use; **every** `candidate` has a `gaze_email` `dispatch_task` row bound to that `candidate_id`.
- [X] 2. After a `gaze_email` run for candidate A, `candidate.last_email_check` for A is non-null and reflects that run (including runs that found zero matching messages). — schema/default + update surface ownership shared with runner; this child owns the column and provision so the stamp can land.
- [X] 3. Scheduled Actions Avail for a candidate’s `gaze_email` row equals the live count of current inbox messages that bind to that candidate; zero-Avail rows are not kept visible by a `gaze_email`-specific carve-out. — this child removes the carve-out/special-case shell; sibling #2 owns live count wiring.
- [X] 4. Gmail secrets remain environ-only; Ruth invocations for a bound message continue to use **that candidate’s** API key; retention days remain config-owned. — retention days stay config-owned on this child.

## Boundaries

* Does **not** own the per-message runner decision tree (sibling #3 / AST-1136).
* Does **not** own the live bind-filtered Avail count implementation beyond making the shell honest (sibling #2 / AST-1135).
* Does **not** redesign Manage Email / Land Meteorite (AST-1129).

## In scope

- [X] `pattern.config.config-block` — `GAZE_EMAIL_CONFIG` / `TASK_CONFIG["gaze_email"]` candidate-bound expectations; keep `unbound_retention_days`
- [X] `astral.config.config-source-of-truth` — task key, seed sizes, retention days, account expectation stay config-owned
- [X] `astral.seed.other-via-coverage-join` — provision `gaze_email` for every row in `candidate` (not hardcoded ids; not only candidates with existing dispatch rows)
- [X] `astral.standards.in-scope-only` — config + schema stamp surface + dispatcher provision/ledger honesty only
- [X] `astral.config.secrets-and-env-specific-from-environ` — Gmail secrets remain environ-only (no move into config)

## Considered but excluded

- [X] Live bind-filtered Avail / due eligibility rewrite — AST-1135 (`src/data/database.py` count path + admin Avail wiring)
- [X] Per-message runner, unbound Trash hygiene, `last_email_check` call site — AST-1136 (`src/core/gaze_email.py`)
- [X] Manage Email / Land Meteorite UI — AST-1129
- [X] React Scheduled Actions filter plumbing — keep generic `always_visible_under_avail_gt0` flag; only empty `ADMIN_CONFIG` source tuple here
- [X] Rebuild `dispatch_task.candidate_id` to NOT NULL — residual null rows deleted at provision; schema nullity left for this ticket

## Notes for planning

Keep `unbound_retention_days`. Coverage = every `candidate` row.

## Git branch (authoritative)

`sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config` (parent table). Ignore Linear `gitBranchName`.

### Comments

#### radia — 2026-08-02T20:24:27.342Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1134
**Publish ref:** `origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config` tip `a5c23ed0b18bf539af63e370085ab134812a6590`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no graded-task / confidence path edits |
| `astral.agent.do-task-delegation` | scoped | conforms | no do_task / external LLM assembly |
| `astral.agent.grade-vector-validation` | scoped | conforms | no vector/grade validation work |
| `astral.batch.batch-id-first` | scoped | conforms | no new claim/get/clear batch APIs |
| `astral.batch.batch-id-format` | scoped | conforms | entity_batch_id still task_key-uuid |
| `astral.batch.claim-process-release` | scoped | conforms | mailbox remains non-claim; no CPR rewrite |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | no agent_data RESPONSE path edits |
| `astral.config.config-source-of-truth` | scoped | conforms | task key/seed sizes/retention/always-visible tuple stay config-owned |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | no scoring / score_floor work |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | Gmail secrets not moved into config |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths artifacts/**\|scripts/spikes/** no match |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | features plan doc is ticket plan, not spike dump |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | no run_next / hop-chain membership sets |
| `astral.dispatch.seed-auto-false` | scoped | conforms | new inserts use GAZE_EMAIL_CONFIG auto_mode False; null shell deleted |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single docs/features/meteorite/ast-1134-….md |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test commits avoid src/features (merge-tests ok) |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | code() commits are src-only; tests via Betty |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | no Gmail I/O; core provision/ledger only |
| `astral.layers.import-direction` | scoped | conforms | dispatcher→data/utils; data stamp helper; utils pure |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers/paths scripts/** no match |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | carve-out retired via empty ADMIN_CONFIG tuple; no React edit |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | no coat-check work |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | no consult/render_verdict work |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers/paths src/ui/** no match |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | no agent JSON seed table edits |
| `astral.seed.archie-catalog-wins` | scoped | conforms | gaze_email task_key remains Archie-named catalog ensure |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | provision only from start_scheduler |
| `astral.seed.define-approved` | scoped | conforms | no invented seed catalogs; coverage rule from define |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | re-ensure is catalog gaze_email coverage, not random operator rows |
| `astral.seed.other-via-coverage-join` | scoped | conforms | provision loops list_candidates(); retires null shell |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | stamp helper raises; no data-layer logging |
| `astral.standards.database-header-inventory` | scoped | conforms | candidate header notes last_email_check |
| `astral.standards.debug-contract-gated` | scoped | conforms | added debug_detail under existing debug=True gate |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | ensure+provision+stamp focused; reuses list/save helpers |
| `astral.standards.in-scope-only` | scoped | conforms | no runner/Avail API/React/Manage Email creep |
| `astral.standards.logging-via-utils` | scoped | conforms | scheduler get_logger; no bare logging/print |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | APIs named by domain; ticket ids only in comments/logs |
| `astral.standards.no-cross-contamination` | scoped | conforms | touches planned utils/data/core surfaces only |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | always-visible set emptied in config; no inline carve-out |
| `astral.standards.public-then-helpers` | scoped | conforms | public ensure/provision/stamp APIs |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | no new utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | conforms | no job state work |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | no ingest/run_next daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers/paths src/ui/frontend/** no match |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers/paths src/ui/** no match |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no gunicorn/worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | single merge-tests(AST-1134) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests vocabulary on sub |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish stays on origin/sub child ref |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1128/AST-1134-… matches parent Git table |
| `orch.git.merge-on-checkout` | universal | conforms | no illegal merge/rebase recipe in commits |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear history; no cherry-pick/rebase/force |
| `orch.git.no-dev-agent-branches` | universal | conforms | no agent-named branches; epic worktree sub tip |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review on astral-AST-1128 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | sibling Avail/runner boundaries held; no product invent |
| `orch.pipeline.plan-is-bible` | universal | needs-discussion | stages match; unbound gaze_email early-return omits FAILED ledger stamp |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Meteorite child AST-1134 only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | review-child entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | no canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test()+merge-tests own tests/bible; code() is src-only |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada stays assignee through Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | engineer commits avoided banned test-tree paths |

## Pattern conformance

- `pattern.config.config-block` — conforms (GAZE_EMAIL_CONFIG / TASK_CONFIG / ADMIN_CONFIG block edits stay config-owned)
- Active `astral.patterns.*` covered in Statutes checked

## Plan adherence

Stages 1–3 match Files Changed and Self-Assessment Scope (Single-Component). Sibling boundaries (AST-1135 Avail, AST-1136 runner/stamp call site, AST-1129 UI) not smuggled. One plan-literalism gap: unbound `_dispatch_one` path logs+returns without FAILED ledger.

## Findings

**discuss:** `src/core/dispatcher.py` `_dispatch_one` gaze_email unbound guard — Stage 3 said "log + mark ledger failed / return"; implementation logs and returns with no ledger write. Residual after null-shell retire; confirm intentional vs add bounded FAILED stamp.

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; post-Betty diff brings them in-scope. All three **conforms**.

## What's solid

Coverage-join provision, null-shell retire, bound ledger cid, stamp helper + schema, empty always-visible tuple, secrets stay environ. No fix-now.

## Notes

Joan plan-rubric verdict attached (APPROVED). Stragglers called out above.

context_tokens≈52000

#### betty — 2026-08-02T20:21:10.466Z
## QA test manifest

`origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config` @ `89a305cb`
`merge-tests(AST-1134): origin/tests fdaddd51f0c97b9384c9aaff94b74a1e4b39d867`

### Existing coverage (revised)

1. `tests/component/utils/test_config.py::TestAst1088GazeEmailConfig` — candidate-bound shell; no `dispatch_ledger_candidate_id`; `freq_hrs == 0.1`
2. `tests/component/utils/test_config.py::TestAst1090GazeEmailRunnerConfig` — runner literals without ledger placeholder
3. `tests/component/utils/test_config.py::TestAst1106AlwaysVisibleUnderAvailGt0` — empty always-visible carve-out
4. `tests/component/data/database/test_dispatch_tasks.py::TestAst1088NullCandidateGazeEmail` — reject null `gaze_email` save; bound save; schema/index remain
5. `tests/component/data/database/test_dispatch_tasks.py::TestAst1090GazeEmailDue` — due/count on bound row (AUTO fixture)
6. `tests/component/core/test_dispatcher.py::TestAst1090GazeEmailDispatchOne` — ledger uses bound cid; unbound skip

### Gaps (new)

7. `tests/component/core/test_dispatcher.py::TestAst1134GazeEmailDispatchProvision` — per-candidate ensure; retire null shell; coverage over `list_candidates()`; scheduler hook
8. `tests/component/data/database/test_candidates.py::TestAst1134LastEmailCheck` — `last_email_check` column + stamp helper

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1088GazeEmailConfig \
  tests/component/utils/test_config.py::TestAst1090GazeEmailRunnerConfig \
  tests/component/utils/test_config.py::TestAst1106AlwaysVisibleUnderAvailGt0 \
  tests/component/core/test_dispatcher.py::TestAst1134GazeEmailDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst1090GazeEmailDispatchOne \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1088NullCandidateGazeEmail \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1090GazeEmailDue \
  tests/component/data/database/test_candidates.py::TestAst1134LastEmailCheck \
  -q
```

### Bible shasums (`origin/<publish-ref>`)

- `docs/test-bible/utils/config.md` `883354bf41dc4c42983c141adc2d67aa7f021b03`
- `docs/test-bible/core/dispatcher.md` `9f50beefa0a36d4b8deb08250e78e9072584493d`
- `docs/test-bible/data/database/dispatch_tasks.md` `fb254c11da12b01f7212f4e93af3cdbc1bc97c5c`
- `docs/test-bible/data/database/candidates.md` `8e753a038f342918398f8782747061ea03e7a130`

API/React AST-1106 generic flag plumbing left as-is (config source emptied; plan: no React edits). No integration scenario drift.

— Betty

#### joan — 2026-08-02T20:11:38.856Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1134
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 no null shell; every candidate has gaze_email row | Stages 1 + 3 — retire null shell; coverage-join provision |
| AC2 run processes only From→A messages | N/A — boundary (AST-1136 runner) |
| AC3 last_email_check stamped after run | Stage 2 — column + `update_candidate_last_email_check`; call site AST-1136 |
| AC4 live bind-filtered Avail; no carve-out | Stage 1 empties always-visible tuple; live count N/A (AST-1135) |
| AC5 unbound newer than retention stays | N/A — boundary (AST-1136); retention days kept config-owned Stage 1 |
| AC6 unbound older → Trash without null shell | N/A — boundary (AST-1136); Stage 3 removes null primary shell |
| AC7 METEORITE_NEW ingest outcomes | N/A — boundary (AST-1136) |
| AC8 Style D debug | N/A — boundary (AST-1136); this child no new debug paths |
| AC9 secrets environ; Ruth key; retention config | Stage 1 — secrets stay environ; unbound_retention_days kept |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 config + empty always-visible | Purpose retire null shell; Functional scope §1 carve-out; child AC1/AC3/AC4 |
| Stage 2 last_email_check + save gate | Functional scope §3; child AC2 schema surface |
| Stage 3 coverage provision + ledger cid | Functional scope §1 every-candidate rows; Purpose candidate-bound dispatch; child AC1 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub via plan()/code() vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table sub ref |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1128/AST-1134-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1128 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Explicit Decisions; sibling handoffs clear |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded-task / confidence work |
| astral.agent.do-task-delegation | conforms | No do_task / Ruth path changes |
| astral.agent.grade-vector-validation | conforms | No grade validation work |
| astral.batch.batch-id-first | conforms | No new claim/get/clear batch APIs |
| astral.batch.batch-id-format | conforms | No batch_id format change |
| astral.batch.claim-process-release | conforms | Mailbox remains non-claim; no new CPR |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE path edits |
| astral.config.config-source-of-truth | conforms | GAZE_EMAIL_CONFIG / ADMIN tuple / seed sizes stay config-owned |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring / score_floor work |
| astral.config.secrets-and-env-specific-from-environ | conforms | Explicitly keeps Gmail secrets environ-only |
| astral.dispatch.run-next-is-chain-authority | conforms | No run_next / hop-chain edits |
| astral.dispatch.seed-auto-false | conforms | New inserts use GAZE_EMAIL_CONFIG auto_mode False; null shell deleted (not left AUTO) |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | No Gmail I/O; core provision/ledger only |
| astral.layers.import-direction | conforms | dispatcher→data/utils; data→utils; utils pure |
| astral.layers.ui-config-driven-business-logic | conforms | Carve-out retired via ADMIN_CONFIG empty tuple; no React hardcodes |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check work |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult work |
| astral.seed.agent-tables-in-repo-json | conforms | No agent JSON seed tables |
| astral.seed.archie-catalog-wins | conforms | Keeps Archie-named gaze_email task_key |
| astral.seed.boot-only-not-hot-path | conforms | Provision at start_scheduler only |
| astral.seed.define-approved | conforms | No rename of task_key / catalog invent |
| astral.seed.operator-rows-stay-deleted | conforms | No revive of deleted operator rows |
| astral.seed.other-via-coverage-join | conforms | Every `list_candidates()` row; rejects under-seed via dispatch-only ids |
| astral.standards.data-raises-caller-logs | conforms | Stamp helper raises; no data-layer logging |
| astral.standards.database-header-inventory | conforms | Header notes last_email_check; candidate table only |
| astral.standards.debug-contract-gated | conforms | No new debug-contract lines on this child |
| astral.standards.dry-and-focused-functions | conforms | Reuses list_candidates/save_dispatch_task; focused ensure+provision |
| astral.standards.in-scope-only | conforms | No runner/Avail API/React/Manage Email |
| astral.standards.logging-via-utils | conforms | Scheduler info log only; no bare logging |
| astral.standards.names-not-ticket-ids | conforms | No ticket-id product names |
| astral.standards.no-cross-contamination | conforms | Stays in utils/data/core layers named |
| astral.standards.no-hardcoded-sets | conforms | Empties config tuple; no inline task-key carve-out set |
| astral.standards.public-then-helpers | conforms | Focused public ensure/provision/stamp APIs |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data import |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No ingest/run_next daisy-chain |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {utils,data,core} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan empty
- astral.ui.naming-conventions — layers {ui} ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Stage 3 intentionally leaves existing `get_due_tasks` / `count_eligible_for_dispatch_task` gaze_email special-case until AST-1135. Honest shell (empty always-visible) may hide zero-Avail rows before live bind counts land — matches child AC3 split with sibling #2.

**acceptable:** Scope Single-Component / Conf high / Risk Medium honest; keep null entity/trigger Decision correctly avoids routing mailbox into claim-queue counting.

**R6:** Definition fidelity pass for child #1. Layer/import pass. Config/secrets pass. File placement N/A (existing modules). Coverage-join pass. No runner/Avail/React creep.

context_tokens≈48000

— Joan

#### chuckles — 2026-08-02T20:09:57.441Z
[thread-orphan] Joan session da0027e7-276d-4fe2-a6e6-65c8eb77e24d relocated
found: /home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db
expected: /home/susan/.cursor/chats/1c0e795437f6ce7d14a00499faa7508f/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db
— Chuckles

#### ada — 2026-08-02T20:09:34.019Z
Plan published on `origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config` @ `5551f130`.

Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config/docs/features/meteorite/ast-1134-retire-null-shell-candidate-bound-config.md

**Self-assessment**
- **Scope:** Single-Component — utils config + data schema/save gate + dispatcher provision/ledger for one task key; no runner rewrite and no Avail API redesign.
- **Conf:** high — replaces a known null-shell provision with the coverage-join pattern already used for candidate-scoped catalogs; carve-out retirement is emptying an existing config tuple.
- **Risk:** Medium — wrong coverage loop or leftover null shell would break Scheduled Actions / dispatch UAT for every candidate; ledger cid mistake would orphan batch history. Mitigated by explicit retire-then-ensure steps and by leaving Avail/runner to siblings.

Three stages: (1) candidate-bound config + empty always-visible tuple, (2) `candidate.last_email_check` + require bound `candidate_id` on save, (3) coverage-join provision over every `candidate` row, delete null shell, ledger uses row `candidate_id`.

---

# AST-1134 — Retire null shell — candidate-bound config, schema, provision, last_email_check

**Linear:** [AST-1134](https://linear.app/astralcareermatch/issue/AST-1134/retire-null-shell-candidate-bound-config-schema-provision-last-email)
**Parent:** [AST-1128](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign) — gaze_email — candidate-bound dispatch (redesign)
**Publish ref:** `origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config`

Retires the shared null-`candidate_id` `gaze_email` dispatch shell as the primary design. Moves `GAZE_EMAIL_CONFIG` / `TASK_CONFIG["gaze_email"]` expectations to candidate-bound rows (keep `unbound_retention_days`), adds `candidate.last_email_check` (default null) plus a data-layer stamp helper, provisions one `gaze_email` `dispatch_task` per every `candidate` row via coverage join, and removes the AST-1106 always-visible-under-Avail-gt0 carve-out for this task. Does **not** own live bind-filtered Avail count (AST-1135) or the per-message runner / unbound hygiene / `last_email_check` call site (AST-1136).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Candidate-bound `GAZE_EMAIL_CONFIG` / `TASK_CONFIG["gaze_email"]` comments + keys; empty always-visible tuple | utils |
| `src/data/database.py` | `candidate.last_email_check`; stamp helper; require `candidate_id` on `save_dispatch_task` for `gaze_email` | data |
| `src/core/dispatcher.py` | Coverage-join provision; retire null shell; ledger uses row `candidate_id` | core |

No `tests/` / bible / React / `src/core/gaze_email.py` runner body / live inbox Avail count on this ticket.

## Stage 1: Candidate-bound config + retire Avail carve-out

**Done when:** `GAZE_EMAIL_CONFIG` documents candidate-bound rows (still owns `unbound_retention_days` + seed sizes); `TASK_CONFIG["gaze_email"]` remains a non-claim mailbox shell (`entity_type`/`trigger_state` null) but no longer describes a null-`candidate_id` primary design; `admin_always_visible_under_avail_gt0_dispatch_task_keys()` is empty so Scheduled Actions no longer special-cases `gaze_email` under Avail > 0; Gmail secrets stay environ-only.

1. In `src/utils/config.py`, rewrite the `GAZE_EMAIL_CONFIG` block comment from “shared Astral inbox … null candidate_id row” to candidate-bound dispatch rows (AST-1134 / parent AST-1128). Keep keys that still apply:
   - `task_key`, `account_address`, `unbound_retention_days`, `auto_mode`, `min_count`, `batch_size`, `freq_hrs`
   - `entity_type`: `None` (mailbox poller — no ENTITY_TYPES claim queue; Avail remains task-key special-cased until AST-1135)
   - `trigger_state`: `None`
   - `subject_url_schemes`, `debug_func` (runner literals for AST-1136; do not change values)
2. **Remove** `dispatch_ledger_candidate_id` from `GAZE_EMAIL_CONFIG` (empty-string ledger placeholder for the null shell). Ledger candidate id becomes the `dispatch_task.candidate_id` on the row (Stage 3).
3. Keep existing asserts for `unbound_retention_days`, `task_key`, `subject_url_schemes`, `debug_func`, `auto_mode`. Do **not** add a new assert that requires `dispatch_ledger_candidate_id`.
4. Update `TASK_CONFIG["gaze_email"]` comment from “mailbox dispatch shell” null-shell wording to “candidate-bound mailbox dispatch shell (no claim queue; row binds via `dispatch_task.candidate_id`)”. Keep:
   ```python
   "gaze_email": {
       "entity_type": None,
       "requires_candidate_key": False,
       "trigger_state": None,
   },
   ```
   ⚠️ **Decision — keep null entity/trigger on the shell:** Parent requires candidate-bound **rows**, not an entity claim queue. Live bind-filtered Avail is AST-1135. Setting `entity_type="candidate"` here would route `count_eligible_for_dispatch_task` into inflow-discovery counting and is out of scope.
5. Keep the `dispatch_task_admin_defaults` early return for `GAZE_EMAIL_CONFIG["task_key"]` that returns null entity/trigger/sort_by and `batch_call_mode=0` — still correct for a non-claim mailbox row.
6. In `ADMIN_CONFIG`, set `"always_visible_under_avail_gt0_dispatch_task_keys"` to an empty tuple `()`. Update the comment to note AST-1134 retired the gaze_email mailbox carve-out (helper + API stamp may remain for empty/future keys). Do **not** delete `admin_always_visible_under_avail_gt0_dispatch_task_keys()` or the API/React generic flag plumbing — emptying the config source is enough to remove the special case.
7. Do **not** move Gmail OAuth / `GMAIL_USER` into config. Do **not** change `unbound_retention_days` value. Do **not** edit React `AdminScheduledActions.tsx`.

**Done when (recheck):** `GAZE_EMAIL_CONFIG` has no `dispatch_ledger_candidate_id`; `admin_always_visible_under_avail_gt0_dispatch_task_keys()` is empty; `dispatch_task_admin_defaults("gaze_email")` still returns null entity/trigger.

## Stage 2: `candidate.last_email_check` + require bound `candidate_id` on save

**Done when:** Every `candidate` row has nullable `last_email_check` (default null on create/migrate); `update_candidate_last_email_check` can stamp an ISO timestamp; `save_dispatch_task` rejects null/blank `candidate_id` for `gaze_email` the same as every other task_key.

1. In `src/data/database.py` module header inventory for `candidate`, note `last_email_check` (nullable timestamp; stamped after `gaze_email` runs — AST-1134 column / AST-1136 call site).
2. In `_ensure_candidate_schema`:
   - Add `last_email_check TIMESTAMP` to the fresh `CREATE TABLE candidate` column list (nullable, no DEFAULT needed — SQLite NULL).
   - Add `("last_email_check", "TIMESTAMP")` to the idempotent `ALTER TABLE … ADD COLUMN` migration loop so existing DBs gain the column.
3. Add a focused stamp helper next to other candidate writers (near `clear_candidate_api_key` / similar):

   ```python
   def update_candidate_last_email_check(
       candidate_id: str, when: Optional[str] = None
   ) -> None:
       """Set candidate.last_email_check (UTC). when=None → now. Raises if candidate missing."""
   ```

   Concrete behavior:
   - Strip `candidate_id`; raise `ValueError` if blank.
   - `stamp = when if (when or "").strip() else _utc_now()` (or equivalent existing UTC helper).
   - `_ensure_candidate_schema`; `UPDATE candidate SET last_email_check = ?, updated_at = ? WHERE astral_candidate_id = ?`.
   - If `rowcount == 0`, raise `LookupError` (candidate missing).
   - No logging in data layer.

   ⚠️ **Decision — dedicated stamp helper, not `save_candidate` kwarg:** Runner (AST-1136) needs a one-field write that does not merge `candidate_data`. Matches `update_company_search_term_last_scan_at`-style cadence stamps.

4. In `save_dispatch_task`, **remove** the gaze_email-only null-`candidate_id` allowance:

   ```python
   # DELETE this branch:
   if tk == GAZE_EMAIL_CONFIG["task_key"] and not cid_raw:
       cid_val = None
   ```

   Blank/None `candidate_id` must always raise `ValueError("candidate_id is required")` before INSERT. Update the docstring to drop “NULL only for GAZE_EMAIL_CONFIG”.

5. Leave `dispatch_task.candidate_id` schema nullable and leave `idx_dispatch_task_null_candidate_task_key` in place for this ticket — Stage 3 deletes any residual null shell rows; a full NOT NULL rebuild is not required by AC and is out of scope.

6. Do **not** call `update_candidate_last_email_check` from the runner or `_dispatch_one` here (AST-1136). Do **not** change `_gaze_email_available_count` / live inbox counting (AST-1135).

**Done when (recheck):** Fresh + migrated DBs expose `last_email_check`; stamp helper updates one row; `save_dispatch_task(candidate_id=None, task_key="gaze_email", …)` raises `ValueError`.

## Stage 3: Coverage-join provision + retire null shell + honest ledger cid

**Done when:** Scheduler startup deletes any null-`candidate_id` `gaze_email` row(s), then idempotently ensures one `gaze_email` dispatch row per every row in `candidate` (config seed sizes / `auto_mode` CLICK); `_dispatch_one` ledger writes the row’s `candidate_id` (no empty placeholder).

1. Replace `ensure_gaze_email_dispatch_task` in `src/core/dispatcher.py` with a per-candidate ensure:

   ```python
   def ensure_gaze_email_dispatch_task(candidate_id: str) -> Dict[str, Any]:
       """Idempotent insert of candidate-bound gaze_email dispatch_task (AST-1134)."""
   ```

   Concrete steps:
   - `cid = str(candidate_id or "").strip()`; if blank → raise `ValueError("candidate_id is required")`.
   - `tk = str(GAZE_EMAIL_CONFIG["task_key"]).strip()`.
   - If `tk not in TASK_CONFIG`: return `{candidate_id, task_key, added:0, skipped:0, skipped_missing_config:1, id:None}`.
   - Scan `database.list_dispatch_tasks_for_candidate(cid)` for a row with `task_key == tk` (trigger_state null/empty pair is fine — at most one gaze_email per candidate under current unique key).
   - If found: return `{candidate_id: cid, task_key: tk, added:0, skipped:1, skipped_missing_config:0, id: row["id"]}`.
   - If missing: `database.save_dispatch_task(candidate_id=cid, task_key=tk, min_count=int(GAZE_EMAIL_CONFIG["min_count"]), auto_mode=bool(GAZE_EMAIL_CONFIG["auto_mode"]), entity_type=GAZE_EMAIL_CONFIG["entity_type"], trigger_state=GAZE_EMAIL_CONFIG["trigger_state"], batch_size=GAZE_EMAIL_CONFIG["batch_size"], freq_hrs=float(GAZE_EMAIL_CONFIG["freq_hrs"] or 0))` → return `added:1` + new id.
   - Do **not** reconcile AUTO→CLICK on already-present rows beyond what seed already stores (new inserts use config `auto_mode`; leave existing row `auto_mode` alone unless it is the retired null shell deleted below).

2. Replace `provision_gaze_email_dispatch_task` with plural coverage provision:

   ```python
   def provision_gaze_email_dispatch_tasks() -> Dict[str, Any]:
       """Retire null gaze_email shell; ensure gaze_email for every candidate (AST-1134)."""
   ```

   Concrete steps:
   - `tk = GAZE_EMAIL_CONFIG["task_key"]`.
   - **Retire null shell:** for each row in `database.list_dispatch_tasks()` where `task_key == tk` and (`candidate_id` is None or blank after strip), call `database.delete_dispatch_task(int(row["id"]))`. Count deletions as `retired_null`.
   - **Coverage join:** `candidates = database.list_candidates()` (or equivalent select of every `astral_candidate_id` from `candidate` — must be every row, **not** `list_candidate_ids_with_dispatch_tasks()`).
   - For each candidate id, call `ensure_gaze_email_dispatch_task(cid)` and sum `added` / `skipped` / `skipped_missing_config`; track `candidates_touched`.
   - Return `{task_key, retired_null, candidates_touched, added, skipped, skipped_missing_config}`.

   ⚠️ **Decision — every `candidate` row, not “candidates that already have dispatch rows”:** Statute `astral.seed.other-via-coverage-join` and parent AC require coverage = extant `candidate` table. Meteorite’s `list_candidate_ids_with_dispatch_tasks` under-seeds and is the wrong pattern here.

3. In `start_scheduler`, call `provision_gaze_email_dispatch_tasks()` (plural). Update the info log to include `retired_null` + `candidates_touched` + `added` / `skipped` / `skipped_missing_config`. Keep try/except so provision failure does not crash scheduler startup.

4. In `_dispatch_one`, for the `gaze_email` branch:
   - Set `ledger_cid = (candidate_id or "").strip()` from the task row (the existing `candidate_id = task["candidate_id"]` local).
   - If `ledger_cid` is empty: treat as failure before runner (log + mark ledger failed / return — do not call `run_gaze_email` with an unbound row). Primary design no longer allows null-candidate gaze_email.
   - Pass `ledger_cid` into `save_dispatch_ledger` (replace `GAZE_EMAIL_CONFIG["dispatch_ledger_candidate_id"]`).
   - Do **not** redesign `run_gaze_email` message filtering, unbound Trash, or `last_email_check` stamping (AST-1136). Do **not** change `_gaze_email_available_count` to bind-filtered inbox counts (AST-1135). Leaving the existing task-key due/avail special-case in `get_due_tasks` / `count_eligible_for_dispatch_task` is intentional so candidate-bound rows still have a due signal until AST-1135 lands.

5. Do **not** add `gaze_email` to `METEORITE_DISPATCH_TASKS` or wire template-only coverage. Template candidate is covered because it is a `candidate` row.

**Done when (recheck):** After provision, zero null-`candidate_id` `gaze_email` rows; every `list_candidates()` id has exactly one `gaze_email` row; Click-run ledger for that row uses that candidate id.

## Self-Assessment

**Scope:** `Single-Component` — utils config + data schema/save gate + dispatcher provision/ledger for one task key; no runner rewrite and no Avail API redesign.

**Conf:** `high` — replaces a known null-shell provision with the coverage-join pattern already used for candidate-scoped catalogs; carve-out retirement is emptying an existing config tuple.

**Risk:** `Medium` — wrong coverage loop or leftover null shell would break Scheduled Actions / dispatch UAT for every candidate; ledger cid mistake would orphan batch history. Mitigated by explicit retire-then-ensure steps and by leaving Avail/runner to siblings.

## Rules check (plan vs ASTRAL_CODE_RULES)

- §1.3 DRY — reuse `list_candidates` / `save_dispatch_task` / existing admin-defaults special-case; no parallel provision framework.
- §2.1 config — task key, retention days, seed sizes stay in `GAZE_EMAIL_CONFIG`; secrets stay environ.
- §2.4 batch — no new claim/get/clear; mailbox still non-claim until AST-1135/1136.
- §2.6 state machine — no job/candidate state transitions on this ticket.
- §3.3 imports — dispatcher already imports config + database; no new upward imports.
- §3.5 naming — `provision_gaze_email_dispatch_tasks` (plural) matches meteorite provision naming.
- Statute `astral.seed.other-via-coverage-join` — coverage from every `candidate` row.
- Statute `astral.standards.in-scope-only` — no React / runner / live Avail / Manage Email (AST-1129).

## Review

**Publish ref:** `origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config`
**Tip:** `89a305cb464aaf66c1f62add928ae143c36efe92`
**Overall:** DISCUSS

[code-rubric] revision=1 — Radia full-set sweep vs `origin/dev...origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config`.

### What's solid

- Stages 1–3 landed on planned surfaces: candidate-bound `GAZE_EMAIL_CONFIG`, empty always-visible tuple, `last_email_check` + stamp helper, `save_dispatch_task` requires bound cid, coverage-join provision via `list_candidates()`, null shell retired, ledger uses row `candidate_id`.
- Sibling boundaries held (no runner / live Avail / React).
- Engineer `code()` commits are src-only; Betty owns tests/bible via `test()` + `merge-tests`.

### Issues

**discuss:** Stage 3 asked unbound `gaze_email` to "log + mark ledger failed / return"; `_dispatch_one` logs and returns without a FAILED ledger write. Residual path after null-shell retire — confirm whether silent skip is enough once bound cid is mandatory.

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; post-Betty diff brings them in-scope. All three score **conforms** (plan doc not a spike; single features file; engineer did not edit test tree).

### Recommended actions

- Ada: confirm unbound early-return is intentional (no FAILED ledger without cid), or add a bounded failure stamp if resolve wants plan literalism.
- No fix-now product edits from this review.

## Resolution

**Date:** 2026-08-02  
**Review tip:** `a5c23ed0` · **Overall:** DISCUSS (no fix-now)

**discuss — unbound `_dispatch_one` early-return (no FAILED ledger):** Confirmed intentional. After null-shell retire, a blank `candidate_id` is a residual/corrupt row, not a supported path. Stamping FAILED with an empty ledger cid would reintroduce the retired null-shell ledger placeholder. Behavior matches the existing no-candidate/API-key skip (log + return, no ledger) and Betty’s `TestAst1090GazeEmailDispatchOne::test_skips_unbound_candidate_id` (`save_ledger` not called). No product change.

**discuss (straggler):** Noted — no action; all three statutes conform on tip.

**fix-now:** none.
