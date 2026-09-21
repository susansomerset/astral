<!-- linear-archive: AST-1136 archived 2026-08-11 -->

## Linear archive (AST-1136)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1136/candidate-bound-gaze-email-runner-last-email-check-unbound-hygiene  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1128 — gaze_email — candidate-bound dispatch (redesign)  
**Blocked by / blocks / related:** parent: AST-1128

### Description

## What this implements

After #1/#2: redesign the core runner so a run for candidate A filters inbox to From→A only, reuses Ruth/scrape/dedupe/create/archive outcomes for those messages, stamps `last_email_check`, and applies unbound leave-then-Trash after `unbound_retention_days` as shared mailbox hygiene **without** restoring a null-candidate primary Avail shell; Style D debug. Leaves a callable core path AST-1129 can reuse for selected message rows.

## Acceptance criteria

- [X] 2. Running `gaze_email` for candidate A processes only current inbox messages whose From binds to A; messages that bind only to other candidates are left for those candidates’ rows.
- [X] 3. After a `gaze_email` run for candidate A, `candidate.last_email_check` for A is non-null and reflects that run (including runs that found zero matching messages).
- [X] 4. An unbound message newer than `unbound_retention_days` remains in the inbox unchanged (so a later profile/email update can bind it).
- [X] 5. An unbound message older than `unbound_retention_days` is moved to Gmail **Trash** without restoring a null-candidate primary Avail/dispatch shell.
- [X] 6. Bound in-scope message shapes still produce the AST-1087 ingest outcomes for that candidate (**METEORITE_NEW** / archive / ignore rules as already established for bound mail); a single run does not advance jobs into qualify/GDL.
- [X] 7. With `debug=True`, each candidate run, each considered message, and each create/skip/archive/trash/ignore outcome is visible in Style D (found + recorded); with `debug=False`, no new debug noise from this path.
- [X] 8. Gmail secrets remain environ-only; Ruth invocations for a bound message continue to use **that candidate’s** API key; retention days remain config-owned.

## Boundaries

* Does **not** own null-shell retirement / every-candidate provision / carve-out removal (sibling #1 / AST-1134).
* Does **not** own Avail count / due-path wiring (sibling #2 / AST-1135).
* Does **not** redesign Manage Email UI or Land Meteorite (AST-1129) — leaves a callable core path.

## In scope

- [X] `pattern.state.entity-state-transitions` — bound ingest still lands **METEORITE_NEW** only via existing shape route (`src/core/gaze_email.py`).
- [X] `astral.state.no-daisy-chain-in-run` — single run does not advance into qualify/GDL (`src/core/gaze_email.py`).
- [X] `astral.standards.debug-contract-gated` — Style D run + per-message + footer only when `debug=True` (`src/core/gaze_email.py`).
- [X] `astral.layers.core-vs-external-bright-line` — Gmail list/archive/trash stay external; filter / hygiene / stamp orchestration in core (`src/core/gaze_email.py`, `src/external/gmail.py` call sites only).
- [X] `astral.standards.in-scope-only` — runner + config comment only; no Avail/provision/UI/tests tree.
- [X] `astral.config.config-source-of-truth` — `unbound_retention_days` / `debug_func` / subject schemes stay on `GAZE_EMAIL_CONFIG` (`src/utils/config.py`).
- [X] `astral.config.secrets-and-env-specific-from-environ` — Gmail OAuth / `GMAIL_USER` remain environ-only.

## Considered but excluded

- [X] `pattern.config.config-block` / `astral.seed.other-via-coverage-join` — candidate-bound provision + null-shell retire already AST-1134 (`src/core/dispatcher.py`, `src/data/database.py`).
- [X] `pattern.ui.admin-endpoint` / live bind-filtered Avail — AST-1135 (`src/core/inbox.py`, `src/ui/api/api_admin.py`).
- [X] Manage Email / Land Meteorite UI — AST-1129 (calls `process_gaze_email_messages` later; not built here).
- [X] React `AdminScheduledActions.tsx` — no UI work on this ticket.
- [X] `astral.git.engineer-test-tree-ban` — Betty owns tests/bible; engineer plan/code only under `src/` + this plan doc.

## Notes for planning

After AST-1134 and AST-1135 (both on `origin/ftr/AST-1128-…`). Plan: `docs/features/meteorite/ast-1136-candidate-bound-gaze-email-runner-last-email-check-unbound-hygiene.md`.

## Git branch (authoritative)

`origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner` — ignore Linear `gitBranchName`.

### Comments

#### radia — 2026-08-02T20:59:04.322Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1136
**Publish ref:** `origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner` tip `78b7cbb6622c24a55d5046197bd90eab5ac35203`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no graded-task / confidence path edits |
| `astral.agent.do-task-delegation` | scoped | conforms | reuses existing Ruth path via _ruth_parse / _handle_bound |
| `astral.agent.grade-vector-validation` | scoped | conforms | no vector/grade validation work |
| `astral.batch.batch-id-first` | scoped | conforms | no new claim/get/clear batch APIs |
| `astral.batch.batch-id-format` | scoped | conforms | no batch_id format change |
| `astral.batch.claim-process-release` | scoped | conforms | mailbox remains non-claim |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | no agent_data RESPONSE redesign |
| `astral.config.config-source-of-truth` | scoped | conforms | retention/debug_func/schemes stay on GAZE_EMAIL_CONFIG |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | no scoring / score_floor work |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | Gmail OAuth/GMAIL_USER stay environ-only |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths artifacts/**\|scripts/spikes/** no match |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | features plan docs are ticket plans, not spike dumps |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | no run_next / hop-chain membership sets |
| `astral.dispatch.seed-auto-false` | scoped | conforms | no seed/provision path |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | one features file per ticket (1134/1135/1136 each own slug) |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test commits avoid src/features (merge-tests ok) |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | code() commits are src-only; tests via Betty |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Gmail list/archive/trash external; filter/hygiene/stamp in core |
| `astral.layers.import-direction` | scoped | conforms | core→data stamp/dedupe; no UI imports from gaze_email |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers/paths scripts/** no match |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | no React; config comment only |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | no coat-check work |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | no consult/render_verdict work |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | conforms | existing admin routes from prior siblings; no new open endpoints |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | no agent JSON seed table edits |
| `astral.seed.archie-catalog-wins` | scoped | conforms | keeps Archie-named gaze_email / debug_func |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | no provision/seed path |
| `astral.seed.define-approved` | scoped | conforms | no catalog invent/rename |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | no revive of deleted operator rows |
| `astral.seed.other-via-coverage-join` | scoped | conforms | no provision rewrite; coverage remains AST-1134 |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | stamp raises propagate; no data logging from this child |
| `astral.standards.database-header-inventory` | scoped | conforms | prior sibling header updates only; no new tables here |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D run+per-message+footer only when debug=True |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | bound outcomes in _handle_bound; explicit dispatch loop for hygiene |
| `astral.standards.in-scope-only` | scoped | conforms | runner+config comment; no Avail/provision/UI creep |
| `astral.standards.logging-via-utils` | scoped | conforms | uses existing logger / Style D helpers |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | APIs named by domain; ticket ids only in comments |
| `astral.standards.no-cross-contamination` | scoped | conforms | stays in planned core/utils surfaces for this child |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | retention/debug_func from config; no new carve-out sets |
| `astral.standards.public-then-helpers` | scoped | conforms | public process_/run_; private _handle_bound retained |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | no new utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | core still decides METEORITE_NEW landing via existing route |
| `astral.state.job-prior-states-enforced` | scoped | conforms | no new job-state transitions beyond established ingest |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | no qualify/GDL in one run |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers/paths src/ui/frontend/** no match |
| `astral.ui.naming-conventions` | scoped | conforms | no new UI endpoints; prior admin path unchanged by this child |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no gunicorn/worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | single merge-tests(AST-1136) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests vocabulary on sub |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish stays on origin/sub child ref |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1128/AST-1136-… matches parent Git table |
| `orch.git.merge-on-checkout` | universal | conforms | no illegal merge/rebase recipe |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear history; no cherry-pick/rebase/force |
| `orch.git.no-dev-agent-branches` | universal | conforms | no agent-named branches; epic worktree sub tip |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review on astral-AST-1128 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | sibling Avail/provision/UI boundaries held |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match Files Changed and Decisions |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Meteorite child AST-1136 only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | review-child entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | no canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test()+merge-tests own tests/bible; code() is src-only |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Katherine |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Katherine stays assignee through Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | engineer commits avoided banned test-tree paths |

## Pattern conformance

- `pattern.state.entity-state-transitions` — conforms (bound ingest still lands METEORITE_NEW only via `_handle_bound`)
- Active `astral.patterns.*` covered in Statutes checked

## Plan adherence

Stages 1–2 match plan Decisions (separate `run_gaze_email` vs `process_gaze_email_messages`; stamp only on dispatch run). Sibling boundaries held (no Avail/provision/UI). Three-dot vs `origin/dev` includes landed AST-1134/1135; this ticket’s `code(AST-1136)` is `gaze_email.py` + config comment only.

## Findings

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.database-header-inventory`, `astral.ui.naming-conventions`; post-sibling/Betty three-dot brings them in-scope. All **conforms**.

## What's solid

Candidate filter, unbound Trash hygiene, stamp after completed run, Style D gated, AST-1129 reuse path. No fix-now.

## Notes

Joan plan-rubric verdict attached (APPROVED). Stragglers called out above.

context_tokens≈46000

#### betty — 2026-08-02T20:55:21.254Z
## QA test manifest

`origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner` @ `d4069a01`
`merge-tests(AST-1136): origin/tests a59e95fb1b7b3437b597b8361e29b7fe7992c663`

### Broken / obsolete (revised)

1. `tests/component/core/test_gaze_email.py::TestAst1090RunGazeEmail` — `run_gaze_email` requires `candidate_id`; stamp stub; Style D `run-start` / `run-complete`

### Existing (unchanged helpers)

2. `tests/component/core/test_gaze_email.py::TestAst1090SubjectIsUrl`
3. `tests/component/core/test_gaze_email.py::TestAst1090UnboundStale`

### Gaps (new)

4. `tests/component/core/test_gaze_email.py::TestAst1136CandidateBoundGazeEmail` — require cid; skip other-candidate; stamp on empty inbox; `process_gaze_email_messages` no trash/stamp

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gaze_email.py::TestAst1090SubjectIsUrl \
  tests/component/core/test_gaze_email.py::TestAst1090UnboundStale \
  tests/component/core/test_gaze_email.py::TestAst1090RunGazeEmail \
  tests/component/core/test_gaze_email.py::TestAst1136CandidateBoundGazeEmail \
  -q
```

### Bible shasum (`origin/<publish-ref>`)

- `docs/test-bible/core/gaze_email.md` `2c12a3cea2f0e4b04bad6e514453c707158ab75c`

Config comment-only; no dispatcher/Avail/React; no new integration scenarios.

— Betty

#### joan — 2026-08-02T20:51:08.416Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1136
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 no null shell; every candidate has gaze_email row | N/A — boundary (AST-1134) |
| AC2 run processes only From→A messages | Stage 1 — three-way branch unbound / other / selected |
| AC3 last_email_check stamped after run | Stage 2 — stamp on `run_gaze_email` completion incl. zero-match |
| AC4 live bind-filtered Avail; no carve-out | N/A — boundary (AST-1135) |
| AC5 unbound newer than retention stays | Stage 1 — `ignored-unbound` when not stale |
| AC6 unbound older → Trash without null shell | Stage 1 — stale unbound `trash_message`; no null Avail shell |
| AC7 METEORITE_NEW ingest; no qualify/GDL | Stage 1 — `_handle_bound` unchanged; no daisy-chain |
| AC8 Style D debug found+recorded | Stages 1–2 — run header, per-message, footer; gated on debug=True |
| AC9 secrets environ; Ruth key; retention config | Stage 1–2 — secrets environ; `_handle_bound` uses that candidate’s key; retention config-owned |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 candidate filter + callable ingest | Purpose candidate-bound run; Functional scope §2/§5; child AC2/4/5/6; AST-1129 reuse path |
| Stage 2 stamp + debug/config honesty | Functional scope §3/§6; child AC3/7/8 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub via plan()/code() vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table sub ref |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1128/AST-1136-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1128 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Explicit Decisions; sibling/1129 handoffs clear |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded-task work |
| astral.agent.do-task-delegation | conforms | Reuses existing Ruth path via `_ruth_parse` / `_handle_bound` |
| astral.agent.grade-vector-validation | conforms | No grade validation work |
| astral.batch.batch-id-first | conforms | No new claim/get/clear batch APIs |
| astral.batch.batch-id-format | conforms | No batch_id format change |
| astral.batch.claim-process-release | conforms | Mailbox remains non-claim |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE path redesign |
| astral.config.config-source-of-truth | conforms | Retention/debug_func/schemes stay on GAZE_EMAIL_CONFIG; comment-only |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring work |
| astral.config.secrets-and-env-specific-from-environ | conforms | Gmail OAuth/GMAIL_USER stay environ-only |
| astral.dispatch.run-next-is-chain-authority | conforms | No run_next / hop-chain edits |
| astral.dispatch.seed-auto-false | conforms | No seed/provision path |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Gmail list/archive/trash external; filter/hygiene/stamp in core |
| astral.layers.import-direction | conforms | core→data for stamp/dedupe; no UI imports |
| astral.layers.ui-config-driven-business-logic | conforms | No React; config comment only |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check work |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult work |
| astral.seed.agent-tables-in-repo-json | conforms | No agent JSON seed |
| astral.seed.archie-catalog-wins | conforms | Keeps Archie-named gaze_email / debug_func |
| astral.seed.boot-only-not-hot-path | conforms | No provision/seed path |
| astral.seed.define-approved | conforms | No catalog rename |
| astral.seed.operator-rows-stay-deleted | conforms | No revive of deleted operator rows |
| astral.seed.other-via-coverage-join | conforms | No provision rewrite (AST-1134) |
| astral.standards.data-raises-caller-logs | conforms | Stamp raises propagate; no data logging from this child |
| astral.standards.debug-contract-gated | conforms | Style D only when debug=True; run + per-message + footer |
| astral.standards.dry-and-focused-functions | conforms | Bound outcomes stay in `_handle_bound`; explicit dispatch loop for hygiene |
| astral.standards.in-scope-only | conforms | No Avail/provision/UI/tests; dispatcher untouched |
| astral.standards.logging-via-utils | conforms | Uses existing logger / Style D helpers |
| astral.standards.names-not-ticket-ids | conforms | No ticket-id product names |
| astral.standards.no-cross-contamination | conforms | Stays in core/utils named files |
| astral.standards.no-hardcoded-sets | conforms | Retention/debug_func from config; no new inline carve-out sets |
| astral.standards.public-then-helpers | conforms | Public `process_gaze_email_messages` / `run_gaze_email`; private `_handle_bound` retained |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data import |
| astral.state.core-decides-transitions | conforms | Core still decides METEORITE_NEW landing via existing route |
| astral.state.job-prior-states-enforced | conforms | No new job-state transitions beyond established ingest |
| astral.state.no-daisy-chain-in-run | conforms | Explicitly no qualify/GDL in one run |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan empty
- astral.ui.naming-conventions — layers {ui} ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Separate loops in `run_gaze_email` vs `process_gaze_email_messages` intentionally avoid Trash/stamp flag soup for AST-1129 — accepted Decision vs forced DRY.

**acceptable:** Scope Single-Component / Conf high / Risk Medium honest; stamp-only-on-dispatch-run Decision correctly matches parent AC3 vs Land Meteorite.

**R6:** Definition fidelity pass for child #3. Layer/import pass. Config/secrets pass. No Avail/provision/UI creep. Daisy-chain ban respected.

context_tokens≈45000

— Joan

#### katherine — 2026-08-02T20:48:07.750Z
Plan published on `origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner` @ `7489cdae`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner/docs/features/meteorite/ast-1136-candidate-bound-gaze-email-runner-last-email-check-unbound-hygiene.md

**Self-assessment**
- **Scope:** Single-Component — core runner redesign in `gaze_email.py` plus a config comment; no Avail/provision/UI.
- **Conf:** high — AST-1090 already owns bind/route/Ruth/archive/trash; AST-1134 shipped the stamp helper; this ticket filters by row `candidate_id`, stamps, and extracts the bound ingest entrypoint.
- **Risk:** Medium — wrong filter would ingest another candidate’s mail or skip real work; wrong hygiene placement could Trash on Land Meteorite or leave stale unbound forever; missed stamp breaks AC3.

---

# AST-1136 — Candidate-bound gaze_email runner + last_email_check + unbound hygiene

**Linear:** [AST-1136](https://linear.app/astralcareermatch/issue/AST-1136/candidate-bound-gaze-email-runner-last-email-check-unbound-hygiene)
**Parent:** [AST-1128](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign) — gaze_email — candidate-bound dispatch (redesign)
**Publish ref:** `origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner`

After AST-1134 (candidate-bound rows + `update_candidate_last_email_check`) and AST-1135 (live bind-filtered Avail / AUTO due), redesign the AST-1090 null-shell runner so a `gaze_email` run for candidate A processes only inbox messages whose From binds to A, reuses Ruth/scrape/dedupe/create/archive outcomes for those messages, stamps `candidate.last_email_check` (including zero-match runs), and applies unbound leave-then-Trash after `unbound_retention_days` as shared mailbox hygiene without restoring a null-candidate Avail shell. Style D when `debug=True`. Leaves a callable core ingest path AST-1129 can reuse for selected messages. Does **not** own provision/Avail/Manage Email UI.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/gaze_email.py` | Candidate filter; unbound hygiene under bound run; stamp `last_email_check`; extract callable ingest; Style D run header | core |
| `src/utils/config.py` | Comment-only: runner is candidate-bound (AST-1136); no key/value changes | utils |

No `tests/` / bible / React / dispatcher provision/Avail / Manage Email (AST-1129) / Gmail external API changes. `_dispatch_one` already passes the bound task row into `run_gaze_email` — do **not** edit `src/core/dispatcher.py` unless a literal compile break appears (escalate; do not invent dispatcher scope).

## Stage 1: Candidate filter + callable bound ingest

**Done when:** `run_gaze_email(task)` requires a non-blank `task["candidate_id"]` and only runs bound ingest for messages whose `candidate_match` binds to that id; messages bound only to other candidates are left untouched; a public `process_gaze_email_messages` performs the same bound ingest outcomes on a caller-supplied message list (AST-1129 reuse); unbound leave/Trash still runs inside `run_gaze_email` over the full inbox list.

1. In `src/core/gaze_email.py`, rewrite the module docstring from “null-candidate dispatch row” to candidate-bound runner (AST-1136 / parent AST-1128): list Astral inbox → filter From→selected candidate → unbound age→Trash (shared hygiene) → bound shape route → Ruth/scrape/dedupe/create → archive; stamp `last_email_check`; Style D when `debug=True`; no qualify/GDL.

2. Import `update_candidate_last_email_check` from `src.data.database` alongside the existing `job_link_exists_for_candidate` import (core→data allowed). Do **not** import dispatcher or UI.

3. Add a public async helper **above** `run_gaze_email` (keep existing private helpers where they are — do not reshuffle the whole file for public-first churn):

   ```python
   async def process_gaze_email_messages(
       candidate_id: str,
       messages: list[dict],
       *,
       debug: bool = False,
   ) -> dict[str, int]:
       """Bound-ingest only for messages whose From binds to candidate_id.

       Same Ruth/scrape/dedupe/create/archive outcomes as the dispatch runner.
       Does not list Gmail, does not Trash unbound mail, does not stamp
       last_email_check. AST-1129 Land Meteorite calls this with selected rows.
       """
   ```

   Concrete behavior:
   - `cid = str(candidate_id or "").strip()`; if blank → raise `ValueError("candidate_id is required")`.
   - If `debug`: `logger.set_debug_flag(True)`.
   - `n = len(messages)`; init `processed = passed = failed = errors = 0`.
   - For `i, msg in enumerate(messages, start=1)`:
     - `mid = msg.get("id") or ""`
     - Style D `found` header + `from_address` detail (same helpers `_dbg` / `_detail` as today).
     - `match = msg.get("candidate_match") or {}`
     - If not `match.get("matched")`: `_dbg(..., outcome="skipped-unbound")` + detail that this path does not mutate unbound mail; `processed += 1`; `passed += 1`; continue. (Land Meteorite must not Trash via this helper.)
     - `bound_cid = str(match.get("astral_candidate_id") or "").strip()`
     - If `bound_cid != cid`: `_dbg(..., outcome="skipped-other-candidate")`; `processed += 1`; `passed += 1`; continue. (No archive/trash/create.)
     - Else: `p, pa, fa, er = await _handle_bound(msg, match, debug=debug, index=i, total=n)` and accumulate.
     - Outer `except`: same as today’s per-message error path (errors++, processed++, Style D `error` + truncated detail).
   - Return `{"total_processed", "total_passed", "total_failed", "total_errors"}` (same keys as today).

   ⚠️ **Decision — message dicts, not raw ids:** Manage Email already holds list/get payloads with `candidate_match`. Requiring ids-only would force a second list/get shape inside core. AST-1129 filters selected rows then calls this; dispatch runner builds the list via `list_inbox_messages`.

4. Rewrite `run_gaze_email(task, *, debug=False)`:

   ```python
   async def run_gaze_email(task: dict, *, debug: bool = False) -> dict[str, int]:
       """AST-1136: candidate-bound mailbox run + unbound hygiene + last_email_check stamp."""
   ```

   Concrete behavior:
   - `cid = str((task or {}).get("candidate_id") or "").strip()`; if blank → raise `ValueError("candidate_id is required")` (dispatcher already skips unbound rows; this hard-fails misuse).
   - If `debug`: `logger.set_debug_flag(True)` and emit one Style D run header:
     - `func=GAZE_EMAIL_CONFIG["debug_func"]` (keep config value `gaze_email.run`)
     - `index=1`, `total=1`, `identifier=cid[:80]`, `outcome="run-start"`
     - detail: `account_address` expectation vs `GMAIL_USER` casefold mismatch warning (keep today’s mismatch detail; do not read secrets from config).
   - `messages = list_inbox_messages(debug=debug)`; `n = len(messages)`; `now_ms = int(time.time() * 1000)`.
   - Init summary counters to 0.
   - For each message with Style D `found` + from detail:
     - **Unbound** (`not match.get("matched")`): if `_unbound_is_stale(internal_date_ms, now_ms=now_ms)` → `trash_message(mid)` + outcome `trashed`; else outcome `ignored-unbound`. `processed += 1`; `passed += 1`. Do **not** call `_handle_bound`.
     - **Bound to other** (`bound_cid != cid`): outcome `skipped-other-candidate`; leave inbox untouched; `processed += 1`; `passed += 1`.
     - **Bound to selected** (`bound_cid == cid`): call `_handle_bound` and accumulate (unchanged Ruth/scrape/dedupe/create/archive behavior; still uses **that** candidate’s API key via `get_candidate(cid)` inside `_handle_bound`).
     - Per-message `except`: same as today.
   - Do **not** call `process_gaze_email_messages` from inside the unbound/other branches — keep one clear loop in `run_gaze_email` so hygiene and filter stay visible. Optionally factor only the bound branch through a tiny private call into `_handle_bound` (already exists). `process_gaze_email_messages` is the external reuse surface; DRY with it is optional if it forces awkward double-indexing — prefer a clear loop over forced DRY.

   ⚠️ **Decision — one inbox loop in `run_gaze_email`, separate public ingest for AST-1129:** Forcing hygiene + stamp through `process_gaze_email_messages` would either Trash unbound on Land Meteorite calls or need flag soup. Duplicate Style D headers between the two publics is acceptable; bound outcome logic stays in `_handle_bound` (single pipeline).

5. Leave `_handle_bound`, `_ruth_parse`, `_ingest_link`, `_finalize_archive`, and shape routing **behaviorally unchanged** (still lands **METEORITE_NEW** only; no qualify/GDL; per-candidate `job_link_exists_for_candidate` only). Do **not** call global AST-1061 skip helpers.

6. Do **not** restore null-candidate ledger placeholders or edit Avail/provision code.

**Done when (recheck):** With inbox messages binding to A, B, and unbound: a run for A ingests only A’s bound mail, leaves B’s messages in inbox, trashes only stale unbound, leaves fresh unbound; `process_gaze_email_messages("A", selected)` never trashes unbound.

## Stage 2: Stamp `last_email_check` + debug/config honesty

**Done when:** Every completed `run_gaze_email` for candidate A stamps `candidate.last_email_check` (including zero bound matches); stamp failures surface as runner errors without swallowing; `debug=False` emits no new Style D lines; config comment names AST-1136 as runner owner.

1. At the end of `run_gaze_email`, **after** the message loop and **before** the summary return, call:

   ```python
   update_candidate_last_email_check(cid)
   ```

   Concrete rules:
   - Stamp even when zero messages bound to `cid` and even when the inbox was empty.
   - Stamp after per-message errors that were handled inside the loop (run still completed).
   - If `list_inbox_messages` raises before the loop: do **not** stamp (run did not complete) — let the exception propagate to `_dispatch_one`.
   - If `update_candidate_last_email_check` raises (`ValueError` / `LookupError` / DB): do **not** swallow; let it propagate (ledger FAILED path already exists).
   - Do **not** stamp from `process_gaze_email_messages` (Land Meteorite is not a mailbox check cadence).

   ⚠️ **Decision — stamp only on `run_gaze_email` completion:** Parent AC3 is about the dispatch `gaze_email` run for that candidate. Selected-message Land Meteorite must not pretend the whole mailbox was checked.

2. When `debug=True`, after the stamp succeeds, emit a Style D run footer header:
   - same `func`, `index=1`, `total=1`, `identifier=cid[:80]`, `outcome="run-complete"`
   - detail lines: `last_email_check=stamped` and `summary={total_processed, total_passed, total_failed, total_errors}` (aggregate allowed; must not replace per-message headers).

3. When `debug=False`: no `debug_index` / `debug_detail` from this module (existing `_dbg` / `_detail` gates stay).

4. In `src/utils/config.py`, update the `GAZE_EMAIL_CONFIG` block comment: replace “Runner literals feed AST-1136” deferral with “Runner is candidate-bound (AST-1136): filter From→row candidate_id, stamp last_email_check, unbound Trash hygiene via unbound_retention_days”. Do **not** change any key values, asserts, secrets, or `unbound_retention_days`.

5. Do **not** move Gmail OAuth / `GMAIL_USER` into config. Do **not** edit React or Manage Email.

**Done when (recheck):** After a click-run for A with zero bound messages, `get_candidate(A)["last_email_check"]` is non-null; stale unbound was trashed if present; `debug=False` produces no new debug-contract lines from `gaze_email.py`.

## Self-Assessment

**Scope:** `Single-Component` — core runner redesign in `gaze_email.py` plus a config comment; no Avail/provision/UI surfaces.

**Conf:** `high` — AST-1090 already owns bind/route/Ruth/archive/trash; AST-1134 shipped the stamp helper; this ticket filters by row `candidate_id`, stamps, and extracts the bound ingest entrypoint.

**Risk:** `Medium` — wrong filter would ingest another candidate’s mail or skip real work; wrong hygiene placement could Trash on Land Meteorite or leave stale unbound forever; missed stamp breaks AC3. Mitigated by explicit three-way branch (unbound / other / selected) and stamp-only on `run_gaze_email`.

## Rules check (plan vs ASTRAL_CODE_RULES)

- §1.3 DRY — bound outcomes stay in `_handle_bound`; public AST-1129 path shares that helper; dispatch loop stays explicit for hygiene/stamp.
- §2.1 config — retention days / debug_func / subject schemes remain in `GAZE_EMAIL_CONFIG`; secrets stay environ.
- §2.4 batch — mailbox remains non-claim; no new claim/get/clear.
- §2.6 state machine — still lands **METEORITE_NEW** only; no daisy-chain into qualify/GDL (`astral.state.no-daisy-chain-in-run`).
- §3.3 imports — core→data for stamp + dedupe; Gmail archive/trash stay external; no UI imports.
- §3.5 naming — `process_gaze_email_messages` / `run_gaze_email` / existing `_handle_bound`.
- §1.5.1 debug — Style D only when `debug=True`; run header + per-message headers + run footer.
- Statute `astral.layers.core-vs-external-bright-line` — Gmail I/O external; filter/hygiene/orchestration core.
- Statute `astral.standards.in-scope-only` — no Avail (1135), no provision (1134), no Manage Email UI (1129), no tests tree.

## Review

**Publish ref:** `origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner`
**Tip:** `d4069a010d958fabc65cacfa4639d137b2913992`
**Overall:** DISCUSS

[code-rubric] revision=1 — Radia full-set sweep vs `origin/dev...origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner`.

### What's solid

- Stages 1–2 match plan: three-way unbound / other / selected filter, `process_gaze_email_messages` reuse path (no Trash/stamp), `run_gaze_email` stamps `last_email_check` after completed loop, Style D run+per-message+footer gated on `debug=True`.
- Bound ingest stays in `_handle_bound` (METEORITE_NEW only; no qualify/GDL). Secrets/retention stay config/environ-owned.
- Engineer `code()` is src-only; Betty owns tests/bible.

### Issues

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.database-header-inventory`, `astral.ui.naming-conventions` at plan time; post-sibling/Betty three-dot brings them in-scope. All score **conforms**.

### Recommended actions

- No fix-now product edits from this review. Stragglers are bookkeeping only for resolve.

## Resolution

**Date:** 2026-08-02  
**Review tip:** `78b7cbb6` · **Overall:** DISCUSS (no fix-now)

**discuss (straggler):** Noted — no action; `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.database-header-inventory`, and `astral.ui.naming-conventions` all conform on tip.

**fix-now:** none.
