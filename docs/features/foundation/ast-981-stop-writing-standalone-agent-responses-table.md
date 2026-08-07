<!-- linear-archive: AST-981 archived 2026-08-05 -->

## Linear archive (AST-981)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-981/stop-writingreading-the-standalone-agent-responses-table-decommission  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-975 — Decommission table AGENT_RESPONSES  
**Blocked by / blocks / related:** parent: AST-975; blocks: AST-982

### Description

## What this implements

Removes all runtime and script call sites that insert into or query the standalone `agent_responses` **table**. Leaves entity-column latest-only behavior alone for sibling work. Does not own schema drop.

## Acceptance criteria

2. A repo-wide search of product code under `src/`, `scripts/`, and `tests/` finds no remaining create/read/write of the standalone `agent_responses` **table** (entity-column name collisions are allowed until the column-retirement sibling lands).
3. Successful `do_task` runs still persist durable history in `agent_data` and still behave correctly for dispatch/UAT without writing the retired table.

## Boundaries

* Does **not** drop the table from schema/bootstrap (sibling: Drop table from schema and existing DBs).
* Does **not** own docs/bible/test prose sweep (sibling: Docs, bible, and test sweep).
* Does **not** drop entity JSON columns (sibling: Retire entity agent_responses columns).
* Does **not** change `agent_data` storage.

## Notes for planning

* Live write path today is core agent audit insert into the standalone table; remove those calls without inventing a replacement store.
* Entity-row `agent_responses` JSON columns remain in use until the later sibling — do not break latest-only upserts.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent. Publish to `origin/<publish-ref>` only.

### Comments

#### chuckles — 2026-07-25T19:32:31.700Z
[merge-child] blocked: git pull merge on sub — `Merge remote-tracking branch 'origin/dev' into sub/AST-975/...` @ c25a5f6. @Ada Lovelace republish from `origin/ftr/AST-975-decommission-table-agent-responses` without pull-merge subjects (merge `origin/ftr` / `origin/dev` with canonical messages only).

— Chuckles

#### radia — 2026-07-25T19:30:22.961Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-981
**Publish ref:** `abb6972c97c2edac33eb5b92ce239b687c422ee1` (`origin/sub/AST-975/AST-981-stop-writing-standalone-agent-responses-table`)
**Overall:** DISCUSS

Diff baseline: `origin/dev...origin/sub/AST-975/AST-981-stop-writing-standalone-agent-responses-table`

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | Grade/confidence validators untouched; only audit side-write removed |
| astral.agent.do-task-delegation | scoped | conforms | `do_task` still owns provider call + `agent_data` / entity ref writes |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector validation edits |
| astral.batch.batch-id-first | scoped | conforms | No claim/get/clear signature changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id format changes |
| astral.batch.claim-process-release | scoped | conforms | No claim→process→release edits |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | `append_agent_response` kept on success path; entity JSON latest-only intact |
| astral.config.config-source-of-truth | scoped | conforms | No new config keys or invented behavior constants |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Scoring thresholds untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env handling changes |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (`artifacts/**` / `scripts/spikes/**`) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan doc under `docs/features/`; not a misplaced spike |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single features file for AST-981 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty `test()` touched bible/tests only; no `src/` or features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code()` touched src/scripts only; tests via Betty |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No external I/O moves; core drops data audit insert only |
| astral.layers.import-direction | scoped | conforms | Removes unused `add_agent_response_entry` import; direction OK |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Migration retirement is scripts-lane one-off |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers miss (no ui) |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Coat-check keys untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Consult orchestrator not in diff |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers miss (no ui) |
| astral.standards.data-raises-caller-logs | scoped | conforms | Deletes data helpers; no new data-layer logging |
| astral.standards.database-header-inventory | scoped | conforms | No new undeclared table; inventory/`_ensure_*` left for AST-982 per plan |
| astral.standards.debug-contract-gated | scoped | conforms | No new ungated debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Deletes duplicate audit path; no no-op stub |
| astral.standards.in-scope-only | scoped | conforms | Sibling boundaries held (no schema drop / column retirement / docs sweep) |
| astral.standards.logging-via-utils | scoped | conforms | No logging facade changes |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in core/data/scripts lanes |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new inline state sets |
| astral.standards.public-then-helpers | scoped | conforms | Deletes helpers; no scattered new public API |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers miss (no utils) |
| astral.state.core-decides-transitions | scoped | conforms | No state-transition logic changes |
| astral.state.job-prior-states-enforced | scoped | conforms | No JOB_STATES / prior-state edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No run_next / daisy-chain changes |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers miss (no ui) |
| astral.ui.naming-conventions | scoped | not-applicable | layers miss (no ui) |
| astral.ui.single-gunicorn-worker | scoped | conforms | Scripts touched are migrations, not gunicorn/start |
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-981): origin/tests 6629664…` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocab on publish-ref |
| orch.git.flow-direction-inviolable | universal | conforms | Tip published on child `sub/` ref only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-975/AST-981-stop-writing-standalone-agent-responses-table` |
| orch.git.merge-on-checkout | universal | conforms | `origin/dev` merge into sub present; no rebase of tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in ticket commits |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named publish branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Reviewed in `astral-AST-975` epic worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch invented |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No new product fork; OQ2 hard-drop already approved |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–4 match delivered code + Betty handoff |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Tests/bible via Betty `test()` + `merge-tests` |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Implementer Ada; Chuckles not assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Review leaves engineer as implementer of record (no assignee flip here) |
| orch.roles.pre-commit-path-bans | universal | conforms | No banned-path product edits in Radia docs commit |

## Pattern conformance

none cited

## Plan adherence

Matches plan Stages 1–4 and Self-Assessment Scope (Single-Component). Sibling keep-list honored: `_ensure_agent_responses_schema` / upsert registry / entity `append_agent_response` / `agent_data` writes remain; schema drop and entity-column retirement not smuggled. Stage 4 acceptance search clean for standalone-table I/O under `src/`/`scripts/`.

## Findings

**discuss (C4 straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` at plan time; this sweep scores them in-scope on the three-dot diff (`docs/features/**`, `tests/**` / `docs/test-bible/**`). Substance verdict for all three is **conforms** — no product fix expected; resolve-child should acknowledge.

**advisory:** `src/data/database.py` header inventory still names `add_agent_response_entry` — plan left inventory for AST-982; comment-only stale helper reference.

### What’s solid

- Audit table write/read/delete call sites removed from core + data; migrator hard-retired.
- Durable history + latest-only entity refs still land via `_store_response_block` / `append_agent_response`.
- One Betty merge-tests SHA; targeted bible/tests updates landed.

### Recommended actions

1. Acknowledge C4 straggler discuss rows (no code change).
2. AST-982 owns ensure/CREATE/header cleanup; AST-983 owns broader prose sweep.

**Notes:** Joan plan-rubric verdict attached (APPROVED). Docs append on plan file @ tip.

context_tokens≈42000

#### betty — 2026-07-25T19:25:55.301Z
## QA test manifest

**Publish:** `origin/sub/AST-975/AST-981-stop-writing-standalone-agent-responses-table` @ `0daf9ad` (`merge-tests(AST-981): origin/tests 6629664fa87c65d04c0d1f4f1fea4f5c91867ed3`)

### 1. Existing coverage (keep)
1. `tests/component/data/database/test_agent_responses.py::TestAst726AppendAgentResponseUpsert` — entity-column latest-only upsert (sibling AST-984 keeps columns).

### 2. Obsolete revised this pass
1. `tests/component/core/test_agent.py` — removed `test_store_agent_response_skips_or_records`; dropped all `add_agent_response_entry` monkeypatches / `stub_agent_storage["audit"]`; renamed failure path to `TestDoTask::test_returns_api_failure_and_stores_agent_data`.
2. `tests/component/data/database/test_agent_responses.py` — removed `TestAddAgentResponseEntry` (standalone insert/list).
3. `tests/component/data/conftest.py` — `seeded_db` state `NEW` → `NEW_CANDIDATE` (registry vocab already on tip; fixture was AttributeError/ValueError before DB tests could run).

### 3. New coverage
1. `TestAst981StandaloneTableAuditRetired` — no `_store_agent_response` / `add_agent_response_entry`; success `do_task` still calls `save_agent_data` + `append_agent_response`.
2. `TestAst981StandaloneTableIoRetired` — data helpers gone; `hard_delete_candidate` counts omit `agent_responses`; `_ensure_*` + `append_agent_response` remain.
3. `tests/component/scripts/test_migrate_agent_data.py::TestAst981MigrateAgentDataRetired` — retired SystemExit / CLI exit 2.

### 4. Run (test-child)
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst981StandaloneTableAuditRetired \
  tests/component/core/test_agent.py::TestDoTask::test_returns_api_failure_and_stores_agent_data \
  tests/component/data/database/test_agent_responses.py::TestAst981StandaloneTableIoRetired \
  tests/component/data/database/test_agent_responses.py::TestAst726AppendAgentResponseUpsert \
  tests/component/scripts/test_migrate_agent_data.py::TestAst981MigrateAgentDataRetired \
  -q
```

Also Stage 4 product `rg` gates from the plan (src/scripts) on the epic worktree tip.

### Bible shasums on publish-ref
- `docs/test-bible/core/agent.md` `eab7e8f3392c77095979dcfdd900444ff50a8a5f`
- `docs/test-bible/data/database/agent_responses.md` `69a06bdf640756fab260ce08f6d882d653f30bc8`
- `docs/test-bible/dev/migrate_agent_data.md` `8be51ec9fed833247b9845e4997d06a30cbb8821`
- `docs/test-bible/dev/cleanup_duplicate_and_board_gaze_jobs.md` `0a3e7e85b6c53bd9bdcfdc33236b8503cbc16c6c`

Broader mandate/bible prose sweep remains sibling **AST-983**.

— Betty

#### joan — 2026-07-25T19:06:23.978Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-981
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-975/AST-981-stop-writing-standalone-agent-responses-table`
**Implementer:** Ada (parent Team table / plan author)

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| AC1 — standalone table gone after deploy/bootstrap; not recreated | N/A — boundary: child “Does not drop the table from schema/bootstrap (sibling AST-982)” |
| AC2 — no create/read/write of standalone table under `src/`, `scripts/`, `tests/` | Stages 1–4 for `src/` + `scripts/`; `tests/` portion N/A — boundary: “Does not own docs/bible/test prose sweep (sibling AST-983)” + Betty note |
| AC3 — `do_task` still persists `agent_data` + dispatch/UAT without writing retired table | Stages 1–2 keep `_store_response_block` + `append_agent_response`; Stage 4 sanity-check |
| AC4 — mandate/bible prose | N/A — AST-983 |
| AC5 — drop entity columns (if OQ1) | N/A — AST-984 |
| AC6 — keep entity columns / latest-only upserts | Stages 1–2 explicit keep-list for `append_agent_response` / entity JSON |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| Stage 1 — remove core `_store_agent_response` / `add_agent_response_entry` | Parent Functional scope §2; child AC3; Purpose (stop feeding standalone table) |
| Stage 2 — delete data-layer insert/list/delete I/O; keep ensure | Parent Functional scope §2; sibling boundary AST-982 |
| Stage 3 — retire `migrate_agent_data.py` table SQL; docstring cleanup | Parent Functional scope §2 (scripts); OQ2 hard-drop of historical rows |
| Stage 4 — rg acceptance on src/scripts | Parent AC2 (src/scripts slice); child AC2 |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| astral.agent.confidence-bounds | conforms | Plan does not touch grade/confidence validation paths |
| astral.agent.do-task-delegation | conforms | Removes audit side-write only; `do_task` still owns agent_data + external delegation |
| astral.agent.grade-vector-validation | conforms | No change to grade-vector validation |
| astral.batch.batch-id-first | conforms | No claim/get/clear signature changes |
| astral.batch.batch-id-format | conforms | No batch_id format changes |
| astral.batch.claim-process-release | conforms | No claim→process→release edits |
| astral.batch.entity-agent-responses-latest-only | conforms | Explicitly preserves `append_agent_response` / entity JSON latest-only upserts |
| astral.config.config-source-of-truth | conforms | No new config keys; no behavior constants invented |
| astral.config.pass-threshold-vs-score-floor | conforms | Scoring thresholds untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env handling changes |
| astral.git.betty-no-src-or-features | conforms | Engineer owns `src/` + plan doc; Betty called out for tests only |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O moves; core stops calling data audit insert |
| astral.layers.import-direction | conforms | Removes unused data import from core; no illegal imports |
| astral.layers.scripts-exempt-from-layer-rules | conforms | Script retirement is one-off migration path, not runtime layer breach |
| astral.patterns.coat-check-never-store-empty | conforms | Coat-check keys untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Consult orchestrator not in Files Changed |
| astral.standards.data-raises-caller-logs | conforms | Deletes data helpers; does not add data-layer logging |
| astral.standards.database-header-inventory | conforms | Leaves header inventory + `_ensure_*` for AST-982; stops undeclared new table use |
| astral.standards.debug-contract-gated | conforms | No new debug-contract emission |
| astral.standards.dry-and-focused-functions | conforms | Deletes duplicate audit path rather than wrapping/no-op stub |
| astral.standards.in-scope-only | conforms | Sibling keep/out tables named; no schema drop / docs / column retirement |
| astral.standards.logging-via-utils | conforms | No logging facade changes |
| astral.standards.no-cross-contamination | conforms | Stays inside core/data/scripts layered paths |
| astral.standards.no-hardcoded-sets | conforms | No new inline state sets/magic numbers |
| astral.standards.public-then-helpers | conforms | Deletes helpers; does not scatter new public API |
| astral.state.core-decides-transitions | conforms | No state-transition logic |
| astral.state.job-prior-states-enforced | conforms | No JOB_STATES / transition edits |
| astral.state.no-daisy-chain-in-run | conforms | No run_next / daisy-chain changes |
| astral.ui.single-gunicorn-worker | conforms | Scripts touched are migrations, not gunicorn/start_server |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work in this plan |
| orch.git.commit-vocabulary | conforms | Plan implies normal engineer commits on publish-ref |
| orch.git.flow-direction-inviolable | conforms | Publish ref is child `sub/AST-975/...` per parent Git table |
| orch.git.ftr-sub-topology | conforms | Child branch naming matches parent Git table |
| orch.git.merge-on-checkout | conforms | No git anti-pattern prescribed |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force instructed |
| orch.git.no-dev-agent-branches | conforms | Uses `sub/` publish-ref, not agent-named branches |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-975 assumed |
| orch.git.three-permanent-branches | conforms | Does not invent permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | OQ1/OQ2 already answered; no new product fork |
| orch.pipeline.plan-is-bible | conforms | Stages are concrete, searchable acceptance gates |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate path only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicit Betty note; engineer does not edit `tests/` |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer is Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Ada on Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits planned |

## Considered and excluded

**Considered:** astral.agent.confidence-bounds; astral.agent.do-task-delegation; astral.agent.grade-vector-validation; astral.batch.batch-id-first; astral.batch.batch-id-format; astral.batch.claim-process-release; astral.batch.entity-agent-responses-latest-only; astral.config.config-source-of-truth; astral.config.pass-threshold-vs-score-floor; astral.config.secrets-and-env-specific-from-environ; astral.git.betty-no-src-or-features; astral.layers.core-vs-external-bright-line; astral.layers.import-direction; astral.layers.scripts-exempt-from-layer-rules; astral.patterns.coat-check-never-store-empty; astral.patterns.render-verdict-orchestrates-consult; astral.standards.data-raises-caller-logs; astral.standards.database-header-inventory; astral.standards.debug-contract-gated; astral.standards.dry-and-focused-functions; astral.standards.in-scope-only; astral.standards.logging-via-utils; astral.standards.no-cross-contamination; astral.standards.no-hardcoded-sets; astral.standards.public-then-helpers; astral.state.core-decides-transitions; astral.state.job-prior-states-enforced; astral.state.no-daisy-chain-in-run; astral.ui.single-gunicorn-worker; orch.git.betty-merge-tests-one-sha; orch.git.commit-vocabulary; orch.git.flow-direction-inviolable; orch.git.ftr-sub-topology; orch.git.merge-on-checkout; orch.git.no-cherry-pick-rebase-force; orch.git.no-dev-agent-branches; orch.git.one-epic-worktree-per-parent; orch.git.three-permanent-branches; orch.pipeline.call-susan-for-product-decisions; orch.pipeline.plan-is-bible; orch.pipeline.project-scoped-queues; orch.pipeline.status-gates-skill-entry; orch.roles.archie-approves-statutes; orch.roles.betty-owns-test-tree; orch.roles.chuckles-never-ticket-assignee; orch.roles.engineer-assignee-through-resolve; orch.roles.pre-commit-path-bans

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss plan paths
- astral.debug.spikes-under-debug-dir — paths miss plan paths
- astral.docs.features-single-file-per-ticket — layers/paths miss (plan Files Changed has no docs row)
- astral.git.engineer-test-tree-ban — paths miss (no tests/** in Files Changed)
- astral.layers.ui-config-driven-business-logic — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.utils-data-late-import-only — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

None fix-now.

- **acceptable** — Child AC2 text still names `tests/` while Stages 1–4 + Betty note correctly defer test edits to AST-983 / Betty; matches child Boundaries and parent child-split table.
- **acceptable** — Self-assessment Scope Single-Component / Conf high / Risk Medium matches localized call sites verified in tree (`_store_agent_response` branches; `add_agent_response_entry` / `list_agent_responses` / cascade DELETEs; `migrate_agent_data.py` JOINs).

## R6 checklist (summary)

Definition fidelity: yes (table I/O stop only). Layers: core→data import removal OK; scripts exempt. Config: none new. Placement: no new files. Patterns: entity latest-only + agent_data preserved; no batch/state changes. DRY/scope: delete duplicate audit; siblings named. Self-assessment: honest.

context_tokens≈68000

— Joan

#### ada — 2026-07-25T18:58:24.807Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-975/AST-981-stop-writing-standalone-agent-responses-table/docs/features/foundation/ast-981-stop-writing-standalone-agent-responses-table.md

**Approach:** Delete `_store_agent_response` / `add_agent_response_entry` / `list_agent_responses` and candidate cascade `DELETE`s against the standalone table; leave `_ensure_agent_responses_schema` + upsert registry for AST-982; keep entity `append_agent_response` + `agent_data` writes; retire `migrate_agent_data.py` table SQL (exit retired, no port).

**Self-assessment**
- **Scope:** Single-Component — core audit call removal, data-layer table I/O deletion, one retired migration script; schema ensure and entity-column contract untouched.
- **Conf:** high — call sites localized (`_store_agent_response` → `add_agent_response_entry`; `list_agent_responses` test-only; cascades are explicit SQL); sibling boundaries named on parent.
- **Risk:** Medium — a missed `_store_agent_response` branch or cascade DELETE would leave silent table writes; accidental removal of `append_agent_response` would break latest-only entity refs. Mitigated by Stage 4 rg gates and explicit keep-list.

---

# AST-981 — Stop writing/reading the standalone agent_responses table

**Linear:** [AST-981 — Stop writing/reading the standalone agent_responses table (Decommission table AGENT_RESPONSES)](https://linear.app/astralcareermatch/issue/AST-981/stop-writingreading-the-standalone-agent-responses-table-decommission)

**Parent:** [AST-975 — Decommission table AGENT_RESPONSES](https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses) (AC reference only)

**Publish ref:** `origin/sub/AST-975/AST-981-stop-writing-standalone-agent-responses-table`

Removes every runtime and script path that inserts into, selects from, or deletes from the standalone `agent_responses` **table**, without inventing a replacement store. Durable history stays in `agent_data`; latest-per-task entity JSON refs stay via `append_agent_response`. Schema/bootstrap drop is sibling AST-982; docs/bible/test prose is sibling AST-983; entity-column retirement is sibling AST-984.

## UAT fitness

- **AC restored:** Parent AC 2: “A repo-wide search of product code under `src/`, `scripts/`, and `tests/` finds no remaining create/read/write of the standalone `agent_responses` **table** (entity-column name collisions are allowed only if Open question 1 keeps the columns).” Parent AC 3: “Successful `do_task` runs still persist durable history in `agent_data` and still behave correctly for dispatch/UAT without writing the retired table.”
- **Correct outcome:** After a successful `do_task`, `agent_data` RESPONSE/prompt blocks and entity-row latest-only `agent_responses` JSON refs still land; the standalone audit table is never written or read by product/script code.
- **Sibling check:** AST-982 still owns `_ensure_agent_responses_schema` / upsert-registry / CREATE TABLE / hard DROP. AST-983 owns bible/docs/test prose and remaining test mocks of `add_agent_response_entry`. AST-984 owns entity JSON column drop. This plan leaves those intact and only removes table I/O call sites.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Redirecting audit inserts into a new parallel store or into `agent_data` under a different shape would invent replacement persistence the epic forbids. Deleting entity-column `append_agent_response` would break statute `astral.batch.entity-agent-responses-latest-only` and is AST-984’s lane. Dropping CREATE/`_ensure_*` here would steal AST-982.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Remove `add_agent_response_entry` import; delete `_store_agent_response` and every call site | core |
| `src/data/database.py` | Delete `add_agent_response_entry`, `list_agent_responses`, `_derive_agent_status`; remove `DELETE FROM agent_responses` from candidate hard-delete / legacy migrate cascades; keep `_ensure_agent_responses_schema`, compress helpers, entity `append_agent_response`, and upsert-registry entry for AST-982 | data |
| `scripts/migrations/migrate_agent_data.py` | Retire script so it no longer SELECTs/JOINs the standalone `agent_responses` table (exit with clear “retired” message; no table SQL) | scripts |
| `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` | Docstring only: drop standalone-table name from “related records” list (no SQL today) | scripts |

**Out of scope (do not touch in this ticket):**

| Item | Owner |
|------|--------|
| `_ensure_agent_responses_schema`, `_UPSERT_*` registry keys, CREATE TABLE, header inventory line for the table | AST-982 |
| Mandate / Code Rules / Test Bible prose; `tests/**` edits | AST-983 / Betty |
| Entity JSON column upserts (`append_agent_response`, roster expand/dedupe) | AST-984 (keep live here) |
| `agent_data` block storage | unchanged |

**Betty note (not engineer commits):** Expect `tests/component/core/test_agent.py` (monkeypatches of `add_agent_response_entry` / `_store_agent_response`) and `tests/component/data/database/test_agent_responses.py` to need update or removal after this lands — engineer does not edit `tests/`.

## Stage 1: Stop core audit writes into the standalone table

**Done when:** `src/core/agent.py` has no import of `add_agent_response_entry`, no `_store_agent_response` function, and no call to either; successful and failure `do_task` paths still call `_store_response_block` / `append_agent_response` as they do today.

1. In `src/core/agent.py`, remove `add_agent_response_entry` from the `from src.data.database import (...)` list.
2. Delete the entire `_store_agent_response` function (Audit logging section, currently ~lines 1627–1654).
3. Delete every call site of `_store_agent_response` in `do_task` (failure path after provider fail; strict-envelope fail; validation fail branches; and the terminal success call after `append_agent_response`). Do not replace those calls with anything — durable storage is already `_store_response_block` + `append_agent_response`.
4. Confirm by search in `src/core/agent.py`: zero matches for `_store_agent_response` and `add_agent_response_entry`.

⚠️ **Decision:** Remove the helper entirely rather than making it a no-op stub. A stub would leave dead API surface and confuse the AST-982/983 sweep; the ticket forbids inventing a replacement store.

## Stage 2: Remove data-layer table insert/list/delete I/O (keep schema ensure)

**Done when:** `src/data/database.py` has no `INSERT INTO agent_responses`, no `SELECT … FROM agent_responses`, and no `DELETE FROM agent_responses`; `_ensure_agent_responses_schema` and its upsert-registry registration remain for AST-982; `append_agent_response` (entity JSON column) is unchanged.

1. In `src/data/database.py`, delete `_derive_agent_status` (only used by `add_agent_response_entry`).
2. Delete `add_agent_response_entry` entirely (function body including `INSERT INTO agent_responses`).
3. Delete `list_agent_responses` entirely (function body including `SELECT * FROM agent_responses`).
4. In candidate hard-delete (`delete_candidate` / equivalent cascade that builds the `for table, sql in (...)` list with an `agent_responses` DELETE), remove that tuple from the loop and remove the `"agent_responses": 0` key from the counts dict. Do not remove entity-table deletes.
5. In `_legacy_candidate_migrate_conn` phase A inline cascade, remove the SQL string `"DELETE FROM agent_responses WHERE entity_type = 'candidate' AND entity_id = ?"`. Leave the other cascade DELETEs.
6. Keep `_compress_payload` / `_decompress_payload` (shared by `agent_data`). Keep `_ensure_agent_responses_schema`, `_agent_responses_schema_ensured`, and the `"agent_responses"` entries in `_UPSERT_SCHEMA_ENSURE_FLAGS` / `_UPSERT_LAZY_SCHEMA_HANDLERS` for AST-982.
7. Leave the module header inventory bullet for `agent_responses` as-is (schema inventory → AST-982). Do not edit entity-column parse/update helpers on company/job/candidate.

⚠️ **Decision:** Leave schema ensure live until AST-982. Removing CREATE/`ensure` here would recreate the table on next upsert/bootstrap gap and steal sibling scope; removing only I/O satisfies “stop writing/reading” while the empty table can still exist until drop.

## Stage 3: Retire scripts that query the standalone table

**Done when:** No file under `scripts/` executes SQL against the standalone `agent_responses` table; `migrate_agent_data.py` cannot be run as a silent partial migrator.

1. In `scripts/migrations/migrate_agent_data.py`, replace runnable migration logic that SELECTs/JOINs `agent_responses` with a retired entrypoint: on CLI / `run_*` invocation, print a one-line message that the standalone-table → `agent_data` migration is retired under AST-981/AST-975 and `sys.exit(2)` (or raise `SystemExit`) **before** any DB open that hits that table. Remove or gut functions whose bodies contain `FROM agent_responses` / `JOIN agent_responses` so a future import cannot accidentally run that SQL. Do **not** rewrite the script to read entity JSON columns as a substitute audit source.
2. In `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` module docstring, change the “Related records (agent_data, agent_responses, …)” sentence to omit the standalone table (e.g. list `agent_data`, timesheets, `dispatch_ledger` only). No code change — that script does not DELETE from the table today.

⚠️ **Decision:** Retire `migrate_agent_data.py` rather than porting it onto entity columns. Parent Open question 2 accepts hard drop of historical standalone rows; durable content already lives in `agent_data`. Porting would invent a new migration path outside this ticket.

## Stage 4: Acceptance search (product/scripts)

**Done when:** The searches below show no remaining standalone-table create/read/write in `src/` or `scripts/` except AST-982-owned schema ensure/CREATE (and comments/docstrings that do not execute SQL). Entity-column identifiers may still appear.

1. From repo root, run (adjust if `rg` unavailable — same patterns):

```bash
rg -n "INSERT INTO agent_responses|DELETE FROM agent_responses|FROM agent_responses|JOIN agent_responses|INTO agent_responses" src scripts --glob '*.py'
rg -n "add_agent_response_entry|list_agent_responses|_store_agent_response|_derive_agent_status" src scripts --glob '*.py'
```

2. Expected: zero matches for insert/delete/from/join/into against the table in executable code; zero matches for the removed function names in `src/` / `scripts/`. Allowed leftovers: `_ensure_agent_responses_schema`, upsert-registry `"agent_responses"` keys, header inventory comment, entity-column `agent_responses` / `append_agent_response` / `dedupe_agent_responses_*`.
3. Manually sanity-check that `do_task` success path still contains `_store_response_block` and `append_agent_response` calls (entity + `agent_data` contract intact).

## Self-Assessment

**Scope:** Single-Component — core audit call removal plus data-layer table I/O deletion and one retired migration script; schema ensure and entity-column contract untouched.

**Conf:** high — call sites are localized (`_store_agent_response` → `add_agent_response_entry`; `list_agent_responses` only used from tests; candidate cascades are explicit SQL strings); sibling boundaries are named in the parent dispatch table.

**Risk:** Medium — forgetting a `_store_agent_response` branch or a cascade DELETE would leave silent table writes; removing `append_agent_response` by mistake would break latest-only entity refs. Mitigated by Stage 4 rg gates and explicit keep-list for entity helpers.

## Code Rules check

- §2.4.1 / `astral.batch.entity-agent-responses-latest-only`: preserved — `append_agent_response` and entity JSON columns stay.
- §2.4 batch / `agent_data`: unchanged — RESPONSE blocks remain the durable store.
- §1.3 DRY: delete duplicate audit path rather than wrapping it.
- §3.3 imports: remove unused `add_agent_response_entry` import with the call sites.
- §2.1 config: no new config keys.
- Layers: core stops calling data audit insert; data stops exposing table I/O; no UI changes.

## Review (build stub)

**Built:** `origin/sub/AST-975/AST-981-stop-writing-standalone-agent-responses-table` @ `24ecb0c`.

**Stages delivered:**
- Stage 1: `src/core/agent.py` — removed `add_agent_response_entry` import, `_store_agent_response`, and all call sites; `_store_response_block` + `append_agent_response` remain — `24ecb0c`.
- Stage 2: `src/data/database.py` — deleted `_derive_agent_status` / `add_agent_response_entry` / `list_agent_responses` and candidate cascade `DELETE`s against the standalone table; kept `_ensure_agent_responses_schema` + upsert registry + `append_agent_response` — `24ecb0c`.
- Stage 3: retired `scripts/migrations/migrate_agent_data.py` (exit 2 / SystemExit); docstring cleanup on `cleanup_duplicate_and_board_gaze_jobs.py` — `24ecb0c`.
- Stage 4: acceptance rg clean for table SQL + removed symbols in `src/`/`scripts/` (header inventory comment left for AST-982).

**Betty:** at **Code Complete** — update/remove `add_agent_response_entry` / `_store_agent_response` mocks in `tests/component/core/test_agent.py` and standalone-table cases in `tests/component/data/database/test_agent_responses.py`; keep entity-column `append_agent_response` coverage until AST-984.

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-981
**Publish ref tip (pre-docs):** `0daf9ad024a532b75d8c4f613a880c4e5700f390`
**Overall:** DISCUSS

### What’s solid

- Stage 1–3 match the plan: `_store_agent_response` / `add_agent_response_entry` / `list_agent_responses` removed; candidate cascade `DELETE FROM agent_responses` gone; `migrate_agent_data.py` hard-retired (exit 2 / SystemExit) with no table SQL left.
- Durable path intact: `_store_response_block` + `append_agent_response` still on `do_task` success; `_ensure_agent_responses_schema` + upsert registry left for AST-982.
- Stage 4 rg on tip: no `INSERT`/`DELETE`/`FROM`/`JOIN`/`INTO agent_responses` executable table I/O under `src/`/`scripts/` (entity-column name collisions remain by design).
- Betty: one `test(AST-981)` + one `merge-tests(AST-981)` SHA; bible/tests updated without touching `src/` or plan features from Betty’s commit.

### Issues

**discuss (C4 straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; this code sweep scores them in-scope on the three-dot diff (`docs/features/**`, `tests/**` / `docs/test-bible/**`). Substance: all three **conform** (plan doc is not a misplaced spike; single features file; engineer `code()` did not touch tests — Betty owns test tree). No product fix required; note for resolve-child acknowledgment.

**advisory:** Header inventory line still says `insert-only from add_agent_response_entry` — plan Stage 2/4 left inventory for AST-982; stale helper name in comment only.

### Recommended actions

1. Implementer: acknowledge the three C4 straggler **discuss** rows (no code change expected).
2. AST-982: drop ensure/CREATE/header inventory for the standalone table.
3. AST-983: broader mandate/bible prose sweep beyond Betty’s targeted bible updates here.

### Pattern conformance

none cited

### Plan adherence

Diff footprint matches Self-Assessment Scope (Single-Component) and sibling boundaries (no schema drop, no entity-column retirement, no invented replacement store). Stages 1–4 delivered; Betty coverage lands on publish-ref tip.

## Resolution

**Date:** 2026-07-25  
**Review tip:** `abb6972` (`docs(AST-981): Radia review — findings`)  
**Outcome:** DISCUSS → acknowledged; no fix-now; advancing to User Testing.

### Discuss (C4 straggler) — acknowledged

Radia flagged that Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` at plan time, while the code-rubric three-dot sweep scores them in-scope because the tip includes `docs/features/**`, `tests/**`, and `docs/test-bible/**`. Substance verdicts remain **conforms** for all three:

- Plan doc is a real features file (not a misplaced spike).
- Single features file for AST-981.
- Engineer `code(AST-981)` did not touch the test tree; Betty owns tests/bible via `test()` / `merge-tests`.

No product change for these discuss rows.

### Advisory — acknowledged (sibling owns)

Header inventory still names `add_agent_response_entry` — left for **AST-982** per plan Stage 2/4 (schema/ensure/header cleanup). Broader mandate/bible prose remains **AST-983**.

