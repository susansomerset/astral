<!-- linear-archive: AST-1135 archived 2026-08-11 -->

## Linear archive (AST-1135)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1135/candidate-bound-avail-count-dispatch-eligibility-gaze-email-candidate  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1128 — gaze_email — candidate-bound dispatch (redesign)  
**Blocked by / blocks / related:** parent: AST-1128; blocks: AST-1136

### Description

## What this implements

After #1 (or tightly with it): Avail / eligible count for a candidate’s `gaze_email` row is the live API count of current inbox messages that bind to that candidate; wire due/dispatch selection so candidate-bound rows fire under normal dispatch without the null-candidate mailbox carve-out. Does **not** own ingest shape routing or unbound Trash hygiene (sibling #3).

## Acceptance criteria

- [X] 4. Scheduled Actions Avail for a candidate’s `gaze_email` row equals the live count of current inbox messages that bind to that candidate; zero-Avail rows are not kept visible by a `gaze_email`-specific carve-out.
- [X] 5. Running `gaze_email` for candidate A processes only current inbox messages whose From binds to A — dispatch eligibility must select the candidate-bound row under normal dispatch (runner owns filter).

## Boundaries

* Does **not** own ingest shape routing or unbound Trash hygiene (sibling #3 / AST-1136).
* Does **not** own null-shell retirement / `last_email_check` column / every-candidate provision (sibling #1 / AST-1134).
* Does **not** redesign Manage Email / Land Meteorite (AST-1129).
* Does **not** change From→candidate bind rules (reuses `list_inbox_messages` enrichment).

## In scope

- [X] `pattern.layers.import-discipline` — Gmail list stays external; bind-filtered count orchestration in core; admin Avail stamp stays thin (`src/core/inbox.py`, `src/ui/api/api_admin.py`).
- [X] `pattern.ui.admin-endpoint` — Scheduled Actions Avail resolved in API from core bind counts, not React business rules (`src/ui/api/api_admin.py`).
- [X] `astral.layers.core-vs-external-bright-line` — data layer must not own live Gmail/bind Avail; retire fake data-layer due signal (`src/data/database.py`, `src/core/inbox.py`).
- [X] `astral.standards.no-hardcoded-sets` — compare task key via `GAZE_EMAIL_CONFIG["task_key"]` only; do not re-seed always-visible carve-out (`src/utils/config.py`, dispatcher/admin callers).
- [X] `astral.config.config-source-of-truth` — comment/config ownership of gaze Avail contract stays on `GAZE_EMAIL_CONFIG` (`src/utils/config.py`).

## Considered but excluded

- [X] `pattern.state.entity-state-transitions` / `astral.state.no-daisy-chain-in-run` — runner ingest outcomes / METEORITE_NEW landing are AST-1136 (`src/core/gaze_email.py`).
- [X] `astral.standards.debug-contract-gated` — Style D on runner path is AST-1136; this ticket adds no new debug surfaces.
- [X] `astral.seed.other-via-coverage-join` — every-candidate provision already owned by AST-1134 (`src/core/dispatcher.py` provision helpers).
- [X] `pattern.config.config-block` key/value redesign — seed sizes / `entity_type` null shell unchanged; comment-only on this ticket.
- [X] React `AdminScheduledActions.tsx` — real `available_count` + empty always-visible set is enough; no UI carve-out restore.
- [X] Manage Email / Land Meteorite UI — AST-1129.

## Notes for planning

After AST-1134. Plan: `docs/features/meteorite/ast-1135-candidate-bound-avail-count-dispatch-eligibility.md`.

## Git branch (authoritative)

`origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility` — ignore Linear `gitBranchName`.

### Comments

#### radia — 2026-08-02T20:43:45.260Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1135
**Publish ref:** `origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility` tip `8992aa1b5d32d4f0d8b88247a4b281f68378fe5d`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no graded-task / confidence path edits |
| `astral.agent.do-task-delegation` | scoped | conforms | no do_task / external LLM assembly |
| `astral.agent.grade-vector-validation` | scoped | conforms | no vector/grade validation work |
| `astral.batch.batch-id-first` | scoped | conforms | no new claim/get/clear batch APIs |
| `astral.batch.batch-id-format` | scoped | conforms | no batch_id format change |
| `astral.batch.claim-process-release` | scoped | conforms | mailbox remains non-claim; Avail is a count |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | no agent_data RESPONSE path edits |
| `astral.config.config-source-of-truth` | scoped | conforms | task key / Avail contract stay on GAZE_EMAIL_CONFIG |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | no scoring / score_floor work |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets moved into config |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths artifacts/**\|scripts/spikes/** no match |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | features plan docs are ticket plans, not spike dumps |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | no run_next / hop-chain membership sets |
| `astral.dispatch.seed-auto-false` | scoped | conforms | no seed/provision inserts; AUTO due merge only |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | one features file per ticket (1134+1135 each own slug) |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test commits avoid src/features (merge-tests ok) |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | code() commits are src-only; tests via Betty |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Gmail list stays external; bind count in core; fake data avail removed |
| `astral.layers.import-direction` | scoped | conforms | ui→core inbox; core→external via inbox; data drops GAZE import |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers/paths scripts/** no match |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Avail stamped in api_admin from core; no React edit |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | no coat-check work |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | no consult/render_verdict work |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | conforms | existing admin list route; no new open endpoints |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | no agent JSON seed table edits |
| `astral.seed.archie-catalog-wins` | scoped | conforms | keeps Archie-named gaze_email task_key |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | no new provision/seed path; Avail is list/due path |
| `astral.seed.define-approved` | scoped | conforms | no catalog invent/rename |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | no revive of deleted operator rows |
| `astral.seed.other-via-coverage-join` | scoped | conforms | no provision rewrite; coverage remains AST-1134 |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | data returns counts; callers warn on Gmail/bind failures |
| `astral.standards.database-header-inventory` | scoped | conforms | dispatch_task header notes live Avail is core |
| `astral.standards.debug-contract-gated` | scoped | conforms | passes debug into existing list helper; no new Style D surfaces |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | one inbox list → many counts; reuses bind enrichment |
| `astral.standards.in-scope-only` | scoped | conforms | no runner/unbound/Manage Email/React carve-out restore |
| `astral.standards.logging-via-utils` | scoped | conforms | warning logs via get_logger; no bare print |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | APIs named by domain; ticket ids only in comments |
| `astral.standards.no-cross-contamination` | scoped | conforms | stays in planned core/data/ui/utils surfaces |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | compares via GAZE_EMAIL_CONFIG task_key; carve-out stays empty |
| `astral.standards.public-then-helpers` | scoped | conforms | public count/freq helpers + private due merge |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | no new utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | conforms | no job state work |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | no ingest/run_next daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers/paths src/ui/frontend/** no match |
| `astral.ui.naming-conventions` | scoped | conforms | existing snake_case admin API path unchanged |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no gunicorn/worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | single merge-tests(AST-1135) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests vocabulary on sub |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish stays on origin/sub child ref |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1128/AST-1135-… matches parent Git table |
| `orch.git.merge-on-checkout` | universal | conforms | no illegal merge/rebase recipe |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear history; no cherry-pick/rebase/force |
| `orch.git.no-dev-agent-branches` | universal | conforms | no agent-named branches; epic worktree sub tip |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review on astral-AST-1128 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | sibling runner/UI boundaries held |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–3 match Files Changed and Decisions |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Meteorite child AST-1135 only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | review-child entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | no canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test()+merge-tests own tests/bible; code() is src-only |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Hedy stays assignee through Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | engineer commits avoided banned test-tree paths |

## Pattern conformance

- `pattern.layers.import-discipline` — conforms (Gmail external; bind count in core; admin thin)
- `pattern.ui.admin-endpoint` — conforms (Avail stamped in `api_admin` from core counts)
- Active `astral.patterns.*` covered in Statutes checked

## Plan adherence

Stages 1–3 match plan Decisions (one inbox snapshot; freq gates AUTO due only, not Avail). Sibling boundaries held (AST-1134 provision, AST-1136 runner, no React carve-out restore). Three-dot vs `origin/dev` also includes landed AST-1134; this ticket’s `code(AST-1135)` is the five planned src files only.

## Findings

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; post-Betty/docs diff brings them in-scope. All three **conforms**.

## What's solid

Live bind-filtered Avail, fake data due signal retired, AUTO due merge + `dispatch_task_freq_allows`, empty always-visible carve-out preserved. No fix-now.

## Notes

Joan plan-rubric verdict attached (APPROVED). Stragglers called out above.

context_tokens≈48000

#### betty — 2026-08-02T20:40:10.265Z
## QA test manifest

`origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility` @ `30e4a45f`
`merge-tests(AST-1135): origin/tests fd6a91df1a931f1055f481b1b432d6446b81b7c8`

### Broken / obsolete (revised)

1. `tests/component/data/database/test_dispatch_tasks.py::TestAst1090GazeEmailDue` — data layer no longer returns gaze due / fake avail `1`

### Gaps (new)

2. `tests/component/data/database/test_dispatch_tasks.py::TestAst1135DispatchTaskFreqAllows` — public freq/cooldown gate
3. `tests/component/core/test_inbox.py::TestAst1135InboxBoundCounts` — bind-filtered inbox map + per-candidate count
4. `tests/component/core/test_dispatcher.py::TestAst1135GazeEmailDueTasks` — AUTO due merge + `run_task` Avail enrich
5. `tests/component/ui/api/test_api_admin.py::TestAst1135ListDtasksGazeAvail` — one inbox snapshot stamps gaze `available_count`

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1090GazeEmailDue \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1135DispatchTaskFreqAllows \
  tests/component/core/test_inbox.py::TestAst1135InboxBoundCounts \
  tests/component/core/test_dispatcher.py::TestAst1135GazeEmailDueTasks \
  tests/component/ui/api/test_api_admin.py::TestAst1135ListDtasksGazeAvail \
  -q
```

### Bible shasums (`origin/<publish-ref>`)

- `docs/test-bible/core/inbox.md` `a6bc771e0a3f0d936f9e8b73705b65835bf861ab`
- `docs/test-bible/core/dispatcher.md` `43faee27a7ff06d1b555881cec0bcb7cfa7ea3d0`
- `docs/test-bible/data/database/dispatch_tasks.md` `7a482c3853c7d49ea61ed960520a81d77b986d82`
- `docs/test-bible/ui/api/api_admin.md` `238b90ca637a9a33a66e946ed56134abce8e3e1e`

Config comment-only; no React; no new integration scenarios.

— Betty

#### joan — 2026-08-02T20:34:06.227Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1135
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 no null shell; every candidate has gaze_email row | N/A — boundary (AST-1134) |
| AC2 run processes only From→A messages | Stage 3 — dispatch eligibility selects candidate-bound row; message filter N/A (AST-1136) |
| AC3 last_email_check stamped after run | N/A — boundary (AST-1134 column / AST-1136 call site) |
| AC4 live bind-filtered Avail; no carve-out | Stages 1–3 — core counts, retire fake data avail, admin stamp; carve-out stays empty |
| AC5 unbound newer than retention stays | N/A — boundary (AST-1136) |
| AC6 unbound older → Trash without null shell | N/A — boundary (AST-1136) |
| AC7 METEORITE_NEW ingest outcomes | N/A — boundary (AST-1136) |
| AC8 Style D debug | N/A — boundary (AST-1136); debug flag only passed through existing list helper |
| AC9 secrets environ; Ruth key; retention config | N/A — untouched; comment-only on GAZE_EMAIL_CONFIG |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 core bind-filtered counts | Purpose real Avail; Functional scope §4; child AC4 |
| Stage 2 retire fake data-layer due signal | Functional scope §4; core-vs-external bright line; child AC4 |
| Stage 3 admin stamp + AUTO due merge | Functional scope §1/§4; child AC4 + AC5 eligibility |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub via plan()/code() vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table sub ref |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1128/AST-1135-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1128 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Explicit Decisions; sibling handoffs clear |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded-task work |
| astral.agent.do-task-delegation | conforms | No do_task / Ruth path changes |
| astral.agent.grade-vector-validation | conforms | No grade validation work |
| astral.batch.batch-id-first | conforms | No new claim/get/clear batch APIs |
| astral.batch.batch-id-format | conforms | No batch_id format change |
| astral.batch.claim-process-release | conforms | Mailbox remains non-claim; Avail is a count |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE path edits |
| astral.config.config-source-of-truth | conforms | Task key / Avail contract comment on GAZE_EMAIL_CONFIG; no new magic sets |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring work |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets moved into config |
| astral.dispatch.run-next-is-chain-authority | conforms | No run_next / hop-chain edits |
| astral.dispatch.seed-auto-false | conforms | No seed/provision inserts; AUTO due merge only |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Gmail list stays external; bind count in core; fake data avail removed |
| astral.layers.import-direction | conforms | ui→core; core→external via inbox; data does not import core |
| astral.layers.ui-config-driven-business-logic | conforms | Avail stamped in api_admin from core; no React business rules |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check work |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult work |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Existing admin list route; no new open endpoints |
| astral.seed.agent-tables-in-repo-json | conforms | No agent JSON seed |
| astral.seed.archie-catalog-wins | conforms | Keeps Archie-named gaze_email task_key |
| astral.seed.boot-only-not-hot-path | conforms | No new provision/seed path (AST-1134 owns provision) |
| astral.seed.define-approved | conforms | No catalog rename |
| astral.seed.operator-rows-stay-deleted | conforms | No revive of deleted operator rows |
| astral.seed.other-via-coverage-join | conforms | No provision rewrite; coverage already AST-1134 |
| astral.standards.data-raises-caller-logs | conforms | Data raises/returns; callers log Gmail failures |
| astral.standards.database-header-inventory | conforms | Updates comments; no new tables |
| astral.standards.debug-contract-gated | conforms | Passes debug into existing list helper; no new Style D surfaces |
| astral.standards.dry-and-focused-functions | conforms | One inbox list → many counts; reuses bind enrichment |
| astral.standards.in-scope-only | conforms | No runner/unbound/Manage Email/React carve-out restore |
| astral.standards.logging-via-utils | conforms | Warning logs on failure paths; no bare print |
| astral.standards.names-not-ticket-ids | conforms | No ticket-id product names |
| astral.standards.no-cross-contamination | conforms | Stays in named layers/files |
| astral.standards.no-hardcoded-sets | conforms | Compares via GAZE_EMAIL_CONFIG["task_key"]; carve-out stays empty |
| astral.standards.public-then-helpers | conforms | Focused public count/freq helpers + private due merge |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data import |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No ingest daisy-chain |
| astral.ui.naming-conventions | conforms | Existing snake_case admin API path unchanged |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.ui.frontend-file-placement — paths match none of plan paths

## Findings

None fix-now.

**discuss (non-blocking):** Admin `list_dtasks` and AUTO tick each take one inbox list snapshot — correct for AC fidelity; operational Gmail cost is accepted by the one-list Decision, not a definition mismatch.

**acceptable:** Scope Single-Component / Conf high / Risk Medium honest; freq-vs-Avail split correctly keeps AC4 live count pure.

**R6:** Definition fidelity pass for child #2. Layer/import pass (data out of Gmail/bind). Config/no-hardcoded-sets pass. No runner/React carve-out creep.

context_tokens≈42000

— Joan

#### hedy — 2026-08-02T20:32:03.366Z
Plan published on `origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility` @ `492b2a53`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility/docs/features/meteorite/ast-1135-candidate-bound-avail-count-dispatch-eligibility.md

**Self-assessment**
- **Scope:** `Single-Component` — core inbox bind-count helpers, retire data-layer fake gaze avail, dispatcher AUTO due merge + click enrichment, thin admin Avail stamp; no runner rewrite.
- **Conf:** `high` — `list_inbox_messages` already owns From→candidate enrichment; AST-1134 already bound every candidate row and emptied the always-visible carve-out; this swaps the known fake due signal for parent AC4’s live count at the correct layer.
- **Risk:** `Medium` — wrong count or due merge would mis-show Scheduled Actions rows or AUTO-fire/miss mailbox tasks; mitigated by one inbox snapshot per list/tick and keeping `freq_hrs` out of displayed Avail.

---

# AST-1135 — Candidate-bound Avail count + dispatch eligibility

**Linear:** [AST-1135](https://linear.app/astralcareermatch/issue/AST-1135/candidate-bound-avail-count-dispatch-eligibility-gaze-email-candidate)
**Parent:** [AST-1128](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign) — gaze_email — candidate-bound dispatch (redesign)
**Publish ref:** `origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility`

After AST-1134’s candidate-bound `gaze_email` rows (carve-out emptied), Scheduled Actions Avail and AUTO due selection still treat the mailbox as a fake due signal (`available_count=1` when `freq_hrs` allows) and the admin list never calls that path because `entity_type`/`trigger_state` are null. This ticket makes Avail / eligible count the live API count of current inbox messages whose From binds to the row’s `candidate_id`, and selects candidate-bound rows under normal dispatch without restoring a null-candidate or always-visible carve-out. Does **not** own runner filter / unbound Trash / `last_email_check` stamp (AST-1136) or Manage Email Land Meteorite (AST-1129).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/inbox.py` | Bind-filtered inbox count helpers (single list → per-candidate counts) | core |
| `src/data/database.py` | Retire fake `_gaze_email_available_count`; drop gaze special-case from `count_eligible_for_dispatch_task` / `get_due_tasks`; public `dispatch_task_freq_allows` | data |
| `src/core/dispatcher.py` | AUTO tick merges candidate-bound gaze due rows (live Avail + freq); click-run `available_count` enrichment for gaze | core |
| `src/ui/api/api_admin.py` | `list_dtasks` stamps live bind-filtered `available_count` for gaze rows | ui |
| `src/utils/config.py` | Comment-only: Avail is live bind-filtered (AST-1135) | utils |

No `tests/` / bible / React / `src/core/gaze_email.py` runner body / unbound hygiene / `last_email_check` call site on this ticket.

## Stage 1: Core — live bind-filtered inbox counts

**Done when:** Core can return how many current Astral inbox messages bind to a given `candidate_id` (and a full `{candidate_id: count}` map from one inbox list), reusing `list_inbox_messages` From→candidate enrichment. No admin or dispatcher wiring yet.

1. In `src/core/inbox.py`, add:

   ```python
   def count_inbox_bound_by_candidate(*, debug: bool = False) -> dict[str, int]:
       """One inbox list → {astral_candidate_id: message_count} for matched From binds."""
   ```

   Concrete behavior:
   - Call `list_inbox_messages(debug=debug)` (existing helper; raises on Gmail failure — do not swallow here).
   - Build a `dict[str, int]`: for each message, read `candidate_match`; if `matched` is true and `astral_candidate_id` is a non-empty string after strip, increment that id’s count.
   - Unmatched / unbound messages do not appear in the map (count contribution 0 for every candidate).
   - Return the map (empty dict when inbox empty).

2. In the same module, add:

   ```python
   def count_inbox_messages_bound_to_candidate(
       candidate_id: str, *, debug: bool = False
   ) -> int:
       """Live count of current inbox messages whose From binds to candidate_id."""
   ```

   Concrete behavior:
   - `cid = str(candidate_id or "").strip()`; if blank → return `0` (do not list inbox).
   - `return int(count_inbox_bound_by_candidate(debug=debug).get(cid, 0))`.

   ⚠️ **Decision — count in core/inbox, not database:** Live Avail needs Gmail list + From-bind (already owned by `inbox.py`). Data layer must not import core/external. AST-1090’s data-layer fake `1` was a null-shell due signal; parent AC4 requires the real bind-filtered count.

3. Do **not** fold `freq_hrs` / `last_run_at` into these counts — Avail is the live bind count only (Stage 2/3 gate AUTO cadence separately).
4. Do **not** change `list_inbox_messages` bind rules, Gmail external I/O, or the runner.

**Done when (recheck):** With a mocked/injected inbox of N messages binding to candidate A and M to B, `count_inbox_messages_bound_to_candidate(A) == N` and the map has keys only for matched candidates.

## Stage 2: Data — retire fake gaze avail; expose freq gate

**Done when:** `count_eligible_for_dispatch_task` no longer returns the AST-1090 fake due signal for `gaze_email`; `get_due_tasks` no longer special-cases `gaze_email` (those rows are skipped by the existing `et/ts/cid` gate like other non-claim shells); callers that need cadence use a small public freq helper. Live counting stays in core (Stage 1/3).

1. In `src/data/database.py`, **delete** `_gaze_email_available_count` entirely.

2. In `count_eligible_for_dispatch_task`, **remove** the gaze early branch:

   ```python
   # DELETE:
   tk = (task.get("task_key") or "").strip()
   if tk == GAZE_EMAIL_CONFIG["task_key"]:
       return _gaze_email_available_count(task)
   ```

   After removal, `gaze_email` rows (null `entity_type` / `trigger_state`) fall through to `if not entity_type or not state or not candidate_id: return 0`. That is correct — data no longer owns mailbox Avail.

3. In `get_due_tasks`, **remove** the `gaze_email` special-case block that called `count_eligible_for_dispatch_task` and `continue`d. After removal, AUTO gaze rows are not returned from this function (Stage 3 merges them in the dispatcher). Leave the generic `if not et or not ts or not cid: continue` path unchanged for all other keys.

4. Promote the freq/cooldown check that lived inside `_gaze_email_available_count` to a public helper (keep `_parse_dispatch_last_run_at` private; reuse it):

   ```python
   def dispatch_task_freq_allows(task: Dict[str, Any]) -> bool:
       """True when freq_hrs is 0/absent, or last_run_at is missing/stale vs freq_hrs."""
   ```

   Concrete behavior (same math as the deleted helper):
   - `freq = float(task.get("freq_hrs") or 0)`.
   - If `freq <= 0`: return `True`.
   - `last = _parse_dispatch_last_run_at(task.get("last_run_at"))`; if `last is None`: return `True`.
   - Return `True` iff `(datetime.now(timezone.utc) - last).total_seconds() >= freq * 3600`.

   ⚠️ **Decision — freq gates AUTO due only, not Avail:** Parent AC4 says Avail equals the live bind count. Folding freq into `available_count` would hide real inbox work under Scheduled Actions after a recent run. Cadence stays a separate due predicate in Stage 3.

5. Update module/doc comments that still describe gaze as “available_count=1 when due” / null-candidate due signal (header inventory / `get_due_tasks` docstring) so they no longer claim data-layer gaze Avail.
6. Do **not** import `src.core.inbox` from `database.py`. Do **not** re-add always-visible carve-out keys.

**Done when (recheck):** `count_eligible_for_dispatch_task({task_key: gaze_email, candidate_id: "x", entity_type: None, trigger_state: None}) == 0`; `get_due_tasks()` never includes a gaze row; `dispatch_task_freq_allows` matches the old cooldown math.

## Stage 3: Admin Avail stamp + dispatcher due / click enrichment

**Done when:** `GET /api/admin/dispatch_tasks` shows live bind-filtered Avail on each candidate-bound `gaze_email` row; zero-Avail gaze rows are not kept visible by any gaze-specific carve-out (AST-1134 already emptied the config tuple); AUTO tick can select candidate-bound gaze rows when live Avail ≥ `min_count` and freq allows; click-run enrichment records the same live Avail on the task dict. Runner body unchanged.

1. In `src/ui/api/api_admin.py` `list_dtasks()`, replace the per-row Avail assignment so gaze rows are not stuck at `0` by the `et and ts and cid` gate:

   - Import `GAZE_EMAIL_CONFIG` (if not already) and `count_inbox_bound_by_candidate` from `src.core.inbox`.
   - **Before** the per-row loop (or once when any gaze row with non-blank `candidate_id` exists): try `bound_counts = count_inbox_bound_by_candidate()`; on exception, log a warning (same style as today’s per-row failure log) and set `bound_counts = {}`.
   - Inside the loop, when `(row.get("task_key") or "").strip() == GAZE_EMAIL_CONFIG["task_key"]`:
     - `cid = str(row.get("candidate_id") or "").strip()`
     - `row["available_count"] = int(bound_counts.get(cid, 0)) if cid else 0`
     - Do **not** call `database.count_eligible_for_dispatch_task` for these rows.
   - Else keep the existing `et and ts and cid` → `count_eligible_for_dispatch_task` / else `0` path (including its try/except).
   - Keep stamping `always_visible_under_avail_gt0` from the (now empty) config helper — do not hardcode `gaze_email` into that set.

   ⚠️ **Decision — one inbox list per `list_dtasks`:** Avail for every candidate-bound gaze row is derived from the same current inbox snapshot. Re-listing Gmail once per row would repeat the same external call without changing the AC result.

2. In `src/core/dispatcher.py`, add a focused helper (module-private is fine):

   ```python
   def _gaze_email_due_tasks() -> List[Dict[str, Any]]:
       """AUTO candidate-bound gaze_email rows with live Avail ≥ min_count and freq allowing."""
   ```

   Concrete steps:
   - `tk = GAZE_EMAIL_CONFIG["task_key"]`.
   - Collect `auto_gaze = [t for t in database.list_dispatch_tasks() if (t.get("task_key") or "").strip() == tk and bool(t.get("auto_mode")) and str(t.get("candidate_id") or "").strip()]`.
   - If none: return `[]`.
   - Try `bound_counts = count_inbox_bound_by_candidate()`; on exception, log warning and return `[]` (do not crash the tick).
   - For each task in `auto_gaze`:
     - `cid = str(task["candidate_id"]).strip()`
     - `avail = int(bound_counts.get(cid, 0))`
     - If `avail < (task.get("min_count") or 1)`: skip.
     - If not `database.dispatch_task_freq_allows(task)`: skip.
     - Set `task["available_count"] = avail` and append a copy/`task` to the result list.
   - Return that list.

3. In `_tick_loop`, after `due = database.get_due_tasks()`, merge:

   ```python
   due = list(due) + _gaze_email_due_tasks()
   ```

   Keep existing slot / already-running / `run_task` logic. Update the nearby comment that claims freq is never a task-level cooldown so it notes gaze_email AUTO uses `dispatch_task_freq_allows` as task cadence (mailbox has no claim-queue entity filter).

4. In the click/manual path that sets `task["available_count"]` only when `et and ts` (today ~line that assigns `0` for mailbox shells), when `task_key == GAZE_EMAIL_CONFIG["task_key"]` and `candidate_id` is non-blank: set `available_count` via `count_inbox_messages_bound_to_candidate(candidate_id)` inside try/except → `0` on failure. Leave non-gaze behavior unchanged.

5. In `src/utils/config.py`, update the `GAZE_EMAIL_CONFIG` block comment: remove “live bind-filtered Avail is AST-1135” deferral wording; state that Avail/eligible count is the live bind-filtered inbox count (AST-1135) while `entity_type`/`trigger_state` remain `None` (no claim queue). Do **not** change key values, seed sizes, `auto_mode`, or secrets.

6. Do **not** edit React `AdminScheduledActions.tsx` — with real `available_count` and an empty always-visible set, default Avail > 0 shows rows that have bind work and hides zero-Avail gaze rows (parent AC4).
7. Do **not** change `run_gaze_email` message filtering, unbound Trash, or `update_candidate_last_email_check` (AST-1136).
8. Do **not** restore null-`candidate_id` provision or re-seed `always_visible_under_avail_gt0_dispatch_task_keys`.

**Done when (recheck):** Admin list for candidate A’s `gaze_email` row shows Avail = number of current inbox messages binding to A; with Avail 0 the row is absent under default Avail > 0 (no carve-out); with AUTO on, bind count ≥ `min_count`, and freq allowing, `_tick_loop`’s due set includes that row; with freq blocking, it does not.

## Self-Assessment

**Scope:** `Single-Component` — core inbox count + data fake-avail retirement + dispatcher due merge + thin admin Avail stamp for one task key; no runner rewrite.

**Conf:** `high` — bind enrichment already exists on `list_inbox_messages`; AST-1134 already emptied the carve-out and bound every candidate row; this ticket swaps the known fake due signal for the parent’s live count at the correct layer.

**Risk:** `Medium` — wrong count or due merge would hide/show Scheduled Actions rows or AUTO-fire mailbox tasks with no work / miss real work; mitigated by one shared inbox snapshot and explicit freq-vs-Avail split.

## Rules check (plan vs ASTRAL_CODE_RULES)

- §1.3 DRY — reuse `list_inbox_messages` bind enrichment; one list → many candidate counts; no parallel bind pipeline.
- §2.1 config — task key still from `GAZE_EMAIL_CONFIG`; no new hardcoded gaze sets in React; carve-out tuple stays empty.
- §2.4 batch — still no claim/get/clear for mailbox; Avail is a count, not a claim queue.
- §2.6 state machine — no job/candidate state transitions on this ticket.
- §3.3 imports — ui→core and core→external allowed; data must not import core for Gmail/bind (fake data avail removed).
- §3.5 naming — `count_inbox_messages_bound_to_candidate` / `count_inbox_bound_by_candidate` / `dispatch_task_freq_allows` / `_gaze_email_due_tasks`.
- Statute `astral.layers.core-vs-external-bright-line` / `pattern.layers.import-discipline` — Gmail stays external; bind count orchestration in core; admin stays thin.
- Statute `astral.standards.no-hardcoded-sets` — compare via `GAZE_EMAIL_CONFIG["task_key"]` only.
- Statute `pattern.ui.admin-endpoint` — Avail resolved in API from core count, not React business rules.
- Out of scope: runner / unbound hygiene / Manage Email (AST-1129) / tests tree.

## Review

**Publish ref:** `origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility`
**Tip:** `30e4a45f1da13635ec32cde6d95812a9d182d757`
**Overall:** DISCUSS

[code-rubric] revision=1 — Radia full-set sweep vs `origin/dev...origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility`.

### What's solid

- Stages 1–3 match plan: core bind-filtered counts, data fake-avail retired (`dispatch_task_freq_allows`), admin one-snapshot Avail stamp, AUTO due merge via `_gaze_email_due_tasks`, freq kept out of Avail.
- Layer bright line holds (Gmail external / bind count core / data out of live Avail). Carve-out tuple stays empty; no React/runner creep.
- Engineer `code()` is src-only; Betty owns tests/bible.

### Issues

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; post-Betty/docs diff brings them in-scope. All three score **conforms**.

### Recommended actions

- No fix-now product edits from this review. Stragglers are bookkeeping only for resolve.

## Resolution

**Date:** 2026-08-02  
**Review tip:** `8992aa1b` · **Overall:** DISCUSS (no fix-now)

**discuss (straggler):** Noted — no action; `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` all conform on tip.

**fix-now:** none.
