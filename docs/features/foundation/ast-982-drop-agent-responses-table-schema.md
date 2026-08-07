<!-- linear-archive: AST-982 archived 2026-08-05 -->

## Linear archive (AST-982)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-982/drop-agent-responses-table-from-schema-and-existing-dbs-decommission  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-975 — Decommission table AGENT_RESPONSES  
**Blocked by / blocks / related:** parent: AST-975; blocks: AST-983

### Description

## What this implements

Removes the standalone `agent_responses` table from the data-layer inventory/bootstrap/ensure path and drops it on upgrade so local and Railway DBs match. Does not own docs/test prose.

## Acceptance criteria

1. After deploy/bootstrap on a legacy DB that still had the standalone `agent_responses` table, that table is gone and is not recreated on subsequent starts.
2. A repo-wide search of product code under `src/`, `scripts/`, and `tests/` finds no remaining create/read/write of the standalone `agent_responses` **table** (entity-column name collisions are allowed until the column-retirement sibling lands).

## Boundaries

* Does **not** remove runtime call sites (sibling AST-981 owns stop-writes).
* Does **not** own docs/bible/test prose (sibling: Docs sweep).
* Does **not** drop entity JSON columns (sibling: Retire entity columns).
* Hard-drop of historical standalone-table rows is approved — no archive/export.

## Notes for planning

* Database header inventory must drop the table; ensure/bootstrap must not recreate it.
* Coordinate with AST-981 so no code path still expects the table at runtime.

## Git branch (authoritative)

Per orientation § Branch law. Publish to `origin/<publish-ref>` only.

### Comments

#### radia — 2026-07-25T19:41:53.789Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-982
**Publish ref:** `dde1cf017fe260c21e37937ef6b9b89e7a213911` (`origin/sub/AST-975/AST-982-drop-agent-responses-table-schema`)
**Overall:** DISCUSS

Diff baseline: `origin/dev...origin/sub/AST-975/AST-982-drop-agent-responses-table-schema` (includes AST-981 ancestors not yet on `origin/dev` via ftr merge).

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | No grade/confidence edits in AST-982; core delta is AST-981 ancestor |
| astral.agent.do-task-delegation | scoped | conforms | AST-982 does not alter `do_task` delegation; ancestor stop-writes already reviewed |
| astral.agent.grade-vector-validation | scoped | conforms | Grade-vector validation untouched |
| astral.batch.batch-id-first | scoped | conforms | No claim/get/clear signature changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id format changes |
| astral.batch.claim-process-release | scoped | conforms | No claim→process→release edits |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | `append_agent_response` + entity JSON columns kept |
| astral.config.config-source-of-truth | scoped | conforms | No new config keys |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Scoring thresholds untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env handling changes |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (`artifacts/**` / `scripts/spikes/**`) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan docs under `docs/features/`; not misplaced spikes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One features file per ticket (981 + 982) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty `test(AST-982)` touched bible/tests/conftest only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code(AST-982)` is `database.py` only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No external I/O moves |
| astral.layers.import-direction | scoped | conforms | Data-layer DDL only; no illegal imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Script paths are AST-981 ancestors; AST-982 has no script edits |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers miss (no ui) |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Coat-check keys untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Consult orchestrator not in AST-982 delta |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers miss (no ui) |
| astral.standards.data-raises-caller-logs | scoped | conforms | Sunset helper is DDL only; no data-layer logging |
| astral.standards.database-header-inventory | scoped | conforms | Retired standalone table removed from header inventory |
| astral.standards.debug-contract-gated | scoped | conforms | No new ungated debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | One sunset helper + one bootstrap call |
| astral.standards.in-scope-only | scoped | conforms | Schema/bootstrap lane only; no column retirement / prose steal |
| astral.standards.logging-via-utils | scoped | conforms | No logging facade changes |
| astral.standards.no-cross-contamination | scoped | conforms | AST-982 stays in `src/data/database.py` |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new inline state sets |
| astral.standards.public-then-helpers | scoped | conforms | Private sunset helper; not registered as upsert handler |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers miss (no utils) |
| astral.state.core-decides-transitions | scoped | conforms | No state-transition logic |
| astral.state.job-prior-states-enforced | scoped | conforms | No JOB_STATES edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No run_next / daisy-chain changes |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers miss (no ui) |
| astral.ui.naming-conventions | scoped | not-applicable | layers miss (no ui) |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/start_server edits |
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-982): origin/tests 7215e0b…` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocab |
| orch.git.flow-direction-inviolable | universal | conforms | Tip on child `sub/` publish-ref |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-975/AST-982-drop-agent-responses-table-schema` |
| orch.git.merge-on-checkout | universal | conforms | Merged `origin/dev` + ftr (AST-981) before Stage 1 |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in ticket commits |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named publish branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Reviewed in `astral-AST-975` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Hard-drop per OQ2; no new product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 + build gate match delivery |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Tests/bible via Betty `test()` + `merge-tests` |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Implementer Hedy; Chuckles not assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Review does not flip assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Docs-only Radia commit |

## Pattern conformance

none cited

## Plan adherence

Matches Stages 1–2 and Self-Assessment Scope (Single-Component). Header inventory + CREATE/ensure/registry removed; DROP sunset hooked from `ensure_all_upsert_registry_schemas_at_startup` before registry loop; entity `append_agent_response` kept. AST-981 `blockedBy` / ftr ancestor satisfied before DROP.

## Findings

**discuss (C4 straggler):** Joan Excluded these 15 statutes; three-dot scores them in-scope due to AST-981 ancestor paths still absent from `origin/dev`: `astral.agent.confidence-bounds`, `astral.agent.do-task-delegation`, `astral.agent.grade-vector-validation`, `astral.config.secrets-and-env-specific-from-environ`, `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.core-vs-external-bright-line`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.patterns.coat-check-never-store-empty`, `astral.patterns.render-verdict-orchestrates-consult`, `astral.standards.debug-contract-gated`, `astral.standards.logging-via-utils`, `astral.state.no-daisy-chain-in-run`, `astral.ui.single-gunicorn-worker`. Substance for all: **conforms**. No product fix expected.

**advisory:** Mandate/bible prose sweep remains AST-983.

### What’s solid

- Idempotent `DROP TABLE IF EXISTS` + process flag; no CREATE/ensure left.
- Entity latest-only path preserved; compress helpers kept.
- One Betty merge-tests SHA with sunset bootstrap coverage.

### Recommended actions

1. Acknowledge C4 stragglers at resolve-child (no code).
2. AST-983 / AST-984 for remaining epic lanes.

**Notes:** Joan plan-rubric verdict attached (APPROVED). Docs append on plan file @ tip.

context_tokens≈38000

#### betty — 2026-07-25T19:39:56.731Z
## QA test manifest

**Publish:** `origin/sub/AST-975/AST-982-drop-agent-responses-table-schema` @ `f201a47` (`merge-tests(AST-982): origin/tests 7215e0b5e23be4fd2d5bae4f9a9fc949e9402098`)

### 1. Existing coverage (keep)
1. `TestAst726AppendAgentResponseUpsert` — entity JSON latest-only (AST-984).
2. `TestAst981StandaloneTableIoRetired` — table I/O helpers gone; hard_delete omits table key (revised: no longer asserts `_ensure_*`).

### 2. Obsolete revised
1. AST-981 ensure-kept assertion → ensure/registry removed under AST-982.
2. Conftest `_SCHEMA_FLAGS`: `_agent_responses_schema_ensured` → `_agent_responses_table_sunset_applied` (data/core/ui/integration).
3. PUB tip was missing AST-981 test tree (merge ancestry quirk); `merge-tests` of this SHA also lands AST-981 test/bible corpus onto the publish-ref.

### 3. New coverage
1. `TestAst982StandaloneTableSunset::test_ensure_and_registry_symbols_removed`
2. `TestAst982StandaloneTableSunset::test_bootstrap_drops_legacy_table_and_does_not_recreate` — DROP via `ensure_all_upsert_registry_schemas_at_startup`; second bootstrap no recreate; company entity column remains.

### 4. Run (test-child)
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_responses.py::TestAst981StandaloneTableIoRetired \
  tests/component/data/database/test_agent_responses.py::TestAst982StandaloneTableSunset \
  tests/component/data/database/test_agent_responses.py::TestAst726AppendAgentResponseUpsert \
  -q
```

Also Stage 2 plan `rg` gates on epic worktree tip.

### Bible shasum on publish-ref
- `docs/test-bible/data/database/agent_responses.md` `cf355487b1143b1b12b6a05302e6e2e65286c421`

Mandate/prose sweep remains sibling **AST-983**.

— Betty

#### joan — 2026-07-25T19:09:41.445Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-982
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-975/AST-982-drop-agent-responses-table-schema`
**Implementer:** Hedy (parent Team table / plan author)

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| AC1 — after deploy/bootstrap, standalone table gone and not recreated | Stage 1 (`_apply_agent_responses_table_sunset` + bootstrap hook); Stage 2 greps |
| AC2 — no create/read/write of standalone table under `src/`/`scripts/`/`tests/` | Stages 1–2 for CREATE/ensure/registry in `src/` (schema lane); runtime I/O N/A — boundary AST-981; `tests/` N/A — boundary AST-983 / Betty |
| AC3 — `do_task` / `agent_data` without writing retired table | N/A — boundary: “Does not remove runtime call sites (sibling AST-981)” |
| AC4 — mandate/bible prose | N/A — AST-983 |
| AC5 — drop entity columns (if OQ1) | N/A — AST-984 |
| AC6 — keep entity columns / latest-only | Stage 1 keep-list: `append_agent_response` + entity JSON columns |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| Stage 1 — delete ensure/CREATE/registry/header; DROP sunset on bootstrap | Parent Purpose + Functional scope §1; parent AC1; child AC1; OQ2 hard drop |
| Stage 2 — acceptance rg + py_compile | Parent AC1/AC2 (schema slice); child AC1–2 (src lane) |
| Build gate — blockedBy AST-981 + ftr ancestor check | Parent Dependencies sequencing (after #1); child Notes |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| astral.batch.batch-id-first | conforms | No claim/get/clear signature changes |
| astral.batch.batch-id-format | conforms | No batch_id format changes |
| astral.batch.claim-process-release | conforms | No claim→process→release edits |
| astral.batch.entity-agent-responses-latest-only | conforms | Explicit keep-list for `append_agent_response` / entity JSON columns |
| astral.config.config-source-of-truth | conforms | No new config keys |
| astral.config.pass-threshold-vs-score-floor | conforms | Scoring thresholds untouched |
| astral.git.betty-no-src-or-features | conforms | Engineer owns `src/data/database.py`; Betty owns tests |
| astral.layers.import-direction | conforms | Data-layer only; no new cross-layer imports |
| astral.standards.data-raises-caller-logs | conforms | Sunset helper does DDL only; no data-layer logging |
| astral.standards.database-header-inventory | conforms | Stage 1 step 7 deletes retired table from header inventory |
| astral.standards.dry-and-focused-functions | conforms | One sunset helper + one bootstrap call; no parallel CLI |
| astral.standards.in-scope-only | conforms | Sibling out-of-scope table explicit; no docs/core/column drop |
| astral.standards.no-cross-contamination | conforms | Stays in `src/data/database.py` |
| astral.standards.no-hardcoded-sets | conforms | No new inline state sets |
| astral.standards.public-then-helpers | conforms | Private sunset helper; no scattered public API |
| astral.state.core-decides-transitions | conforms | No state-transition logic |
| astral.state.job-prior-states-enforced | conforms | No JOB_STATES edits |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Normal engineer commits on publish-ref |
| orch.git.flow-direction-inviolable | conforms | Child `sub/AST-975/...` per parent Git table |
| orch.git.ftr-sub-topology | conforms | Publish ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | Build gate requires merge ftr/dev before Stage 1 |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force instructed |
| orch.git.no-dev-agent-branches | conforms | Uses `sub/` publish-ref |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-975 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | OQ2 hard-drop already answered; no new product fork |
| orch.pipeline.plan-is-bible | conforms | Concrete stages + rg gates + blockedBy gate |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate path |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Betty note; engineer does not edit `tests/` |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer is Hedy |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Hedy on Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits planned |

## Considered and excluded

**Considered:** astral.batch.batch-id-first; astral.batch.batch-id-format; astral.batch.claim-process-release; astral.batch.entity-agent-responses-latest-only; astral.config.config-source-of-truth; astral.config.pass-threshold-vs-score-floor; astral.git.betty-no-src-or-features; astral.layers.import-direction; astral.standards.data-raises-caller-logs; astral.standards.database-header-inventory; astral.standards.dry-and-focused-functions; astral.standards.in-scope-only; astral.standards.no-cross-contamination; astral.standards.no-hardcoded-sets; astral.standards.public-then-helpers; astral.state.core-decides-transitions; astral.state.job-prior-states-enforced; orch.git.betty-merge-tests-one-sha; orch.git.commit-vocabulary; orch.git.flow-direction-inviolable; orch.git.ftr-sub-topology; orch.git.merge-on-checkout; orch.git.no-cherry-pick-rebase-force; orch.git.no-dev-agent-branches; orch.git.one-epic-worktree-per-parent; orch.git.three-permanent-branches; orch.pipeline.call-susan-for-product-decisions; orch.pipeline.plan-is-bible; orch.pipeline.project-scoped-queues; orch.pipeline.status-gates-skill-entry; orch.roles.archie-approves-statutes; orch.roles.betty-owns-test-tree; orch.roles.chuckles-never-ticket-assignee; orch.roles.engineer-assignee-through-resolve; orch.roles.pre-commit-path-bans

**Excluded:**
- astral.agent.confidence-bounds — layers/paths miss (core/utils)
- astral.agent.do-task-delegation — layers/paths miss
- astral.agent.grade-vector-validation — layers/paths miss
- astral.config.secrets-and-env-specific-from-environ — layers miss (no data)
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss (no tests/** in Files Changed)
- astral.layers.core-vs-external-bright-line — layers/paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.layers.ui-config-driven-business-logic — layers/paths miss
- astral.patterns.coat-check-never-store-empty — layers/paths miss
- astral.patterns.render-verdict-orchestrates-consult — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.debug-contract-gated — layers miss
- astral.standards.logging-via-utils — layers miss
- astral.standards.utils-data-late-import-only — layers/paths miss
- astral.state.no-daisy-chain-in-run — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss
- astral.ui.single-gunicorn-worker — layers/paths miss

## Findings

None fix-now.

- **acceptable** — AST-766 board sunset hooks from `_ensure_job_schema`; this plan hooks from `ensure_all_upsert_registry_schemas_at_startup` instead. Justified: agent_responses is not an entity-table ensure, and bootstrap is the AC1 contract path (`src/core/bootstrap.py`). Explicitly rejects wiring DROP into job/company/candidate ensures.
- **acceptable** — Child AC2 names `tests/`; plan correctly defers test edits to AST-983 / Betty per Boundaries.
- **acceptable** — Self-assessment Scope Single-Component / Conf high / Risk Medium matches localized surface + blockedBy/ftr gate.

## R6 checklist (summary)

Definition fidelity: schema drop only, hard drop per OQ2. Layers: data only. Config: none new. Placement: no new files. Patterns: entity latest-only + agent_data preserved. DRY/scope: one sunset helper; siblings named; AST-981 gate before DROP. Self-assessment: honest.

context_tokens≈85000

— Joan

#### hedy — 2026-07-25T19:00:30.894Z
Plan on publish ref `origin/sub/AST-975/AST-982-drop-agent-responses-table-schema` @ `20c67cd`:

https://github.com/susansomerset/astral/blob/sub/AST-975/AST-982-drop-agent-responses-table-schema/docs/features/foundation/ast-982-drop-agent-responses-table-schema.md

**Scope:** Single-Component — `src/data/database.py` only: remove standalone-table header inventory + CREATE/`_ensure_agent_responses_schema` + upsert-registry keys; add `_apply_agent_responses_table_sunset` (`DROP TABLE IF EXISTS`) hooked from `ensure_all_upsert_registry_schemas_at_startup`.

**Conf:** high — AST-981 already reserved this surface; AST-766 establishes the DROP-on-bootstrap pattern; sibling keep-list (entity columns / `append_agent_response` / compress helpers) is explicit.

**Risk:** Medium — DROP while AST-981 writers remain would break inserts; mitigated by Linear `blockedBy` + ftr ancestor gate before Stage 1. Entity-column helpers are keep-listed so latest-only refs survive until AST-984.

---

# AST-982 — Drop agent_responses table from schema and existing DBs

**Linear:** [AST-982 — Drop agent_responses table from schema and existing DBs (Decommission table AGENT_RESPONSES)](https://linear.app/astralcareermatch/issue/AST-982/drop-agent-responses-table-from-schema-and-existing-dbs-decommission)

**Parent:** [AST-975 — Decommission table AGENT_RESPONSES](https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses) (AC reference only)

**Publish ref:** `origin/sub/AST-975/AST-982-drop-agent-responses-table-schema`

Removes the standalone `agent_responses` **table** from the data-layer header inventory, upsert-registry ensure path, and bootstrap so local and Railway DBs drop it on upgrade and never recreate it. Hard-drop of historical standalone-table rows is approved (parent Open question 2). Runtime table I/O stop is sibling AST-981; docs/bible/test prose is sibling AST-983; entity JSON column retirement is sibling AST-984.

## UAT fitness

- **AC restored:** Parent AST-975 AC 1 — “After deploy/bootstrap on a legacy DB that still had the standalone `agent_responses` table, that table is gone and is not recreated on subsequent starts.” Parent AST-975 AC 2 (schema/create half, coordinated with AST-981) — “A repo-wide search of product code under `src/`, `scripts/`, and `tests/` finds no remaining create/read/write of the standalone `agent_responses` **table** (entity-column name collisions are allowed only if Open question 1 keeps the columns).” Child AST-982 AC 1–2 match those sentences for the schema/bootstrap lane.
- **Correct outcome:** After server bootstrap (`ensure_all_upsert_registry_schemas_at_startup`), a legacy DB that still had the standalone table no longer has `agent_responses` in `sqlite_master`, and a second bootstrap does not recreate it. Entity-row `agent_responses` JSON columns on company/job/candidate remain. Durable history stays in `agent_data`.
- **Sibling check:** AST-981 removes `add_agent_response_entry` / `list_agent_responses` / `_store_agent_response` and all executable `INSERT`/`SELECT`/`DELETE` against the table, and **leaves** `_ensure_agent_responses_schema` + upsert-registry `"agent_responses"` keys for this ticket. AST-983 owns mandate/bible/test prose. AST-984 owns entity-column drop. Before Stage 1, merge `origin/ftr/AST-975-decommission-table-agent-responses` and confirm AST-981’s stop-writes commits are ancestors (Linear `blockedBy` AST-981). If ftr still has live table I/O call sites, **stop** and comment on AST-982 — do not drop the table while writers remain.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Deleting entity-column `append_agent_response` / JSON columns, or rewriting §2.4.1 / `astral.batch.entity-agent-responses-latest-only` — that is AST-984. Soft-deleting rows while leaving CREATE/`_ensure_*` live would fail AC 1 (table recreated on next start). Inventing an archive/export before DROP contradicts parent Open question 2 (hard drop approved). Stealing AST-981’s call-site removals into this plan is out of scope.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Remove standalone-table inventory + CREATE/ensure/upsert-registry; add idempotent DROP sunset hooked from bootstrap | data |

**Out of scope (do not touch in this ticket):**

| Item | Owner |
|------|--------|
| `src/core/agent.py` audit call sites; `add_agent_response_entry` / `list_agent_responses` / cascade DELETE I/O; migration script retirement | AST-981 |
| Mandate / Code Rules / Test Bible prose; `tests/**` edits | AST-983 / Betty |
| Entity JSON column DDL, `append_agent_response`, roster expand/dedupe | AST-984 (keep live here) |
| `agent_data` block storage; `_compress_payload` / `_decompress_payload` | unchanged (shared) |
| `docs/ASTRAL_CODE_RULES.md`, `src/utils/config.py` inventory comments | AST-983 |

**Betty note (not engineer commits):** Expect `tests/component/data/database/test_agent_responses.py` cases that call `_ensure_agent_responses_schema` or assert the standalone table exists to be retired or rewritten at qa-child; engineer does not edit `tests/`.

**Build gate:** Linear `blockedBy` AST-981. Before Stage 1 product edits, merge `origin/ftr/AST-975-decommission-table-agent-responses` (and `origin/dev` per merge-clean). Confirm AST-981 commits that remove table I/O are ancestors of `HEAD`. If not, **stop** and comment — do not implement the DROP while writers remain on ftr.

## Stage 1: Idempotent sunset — drop standalone table; never recreate

**Done when:** On a DB that previously had the standalone `agent_responses` table, `_apply_agent_responses_table_sunset(conn)` runs `DROP TABLE IF EXISTS agent_responses` and sets a process flag so the helper is a no-op on later calls in the same process; after `ensure_all_upsert_registry_schemas_at_startup()`, `sqlite_master` has no `agent_responses` table; a second bootstrap does not recreate it. Entity tables still have their `agent_responses` JSON columns.

1. Near the module globals (with the other `_*_schema_ensured` flags), **delete** `_agent_responses_schema_ensured`. Add `_agent_responses_table_sunset_applied = False`.

2. **Delete** the entire `_ensure_agent_responses_schema` function (CREATE TABLE + ALTER COLUMN migration block currently ~lines 2325–2363). Do **not** leave a CREATE path under any name.

3. Immediately after the compress/decompress helpers (or where `_ensure_agent_responses_schema` was), implement **`_apply_agent_responses_table_sunset(conn: sqlite3.Connection) -> None`**:
   - If `_agent_responses_table_sunset_applied` is True, return.
   - `conn.execute("DROP TABLE IF EXISTS agent_responses")`.
   - `conn.commit()`.
   - Set `_agent_responses_table_sunset_applied = True`.
   - Docstring: one-time AST-982 sunset — hard-drop standalone audit table; entity JSON columns unchanged.

   ⚠️ **Decision:** Follow the AST-766 board sunset pattern (DROP inside ensure/bootstrap, not a separate operator CLI). Parent Open question 2 already approved hard drop with no archive/export. SQLite drops indexes with the table — no separate `DROP INDEX` needed.

4. In **`ensure_all_upsert_registry_schemas_at_startup`**, after `_get_connection()` and **before** the `for table in sorted(_UPSERT_LAZY_SCHEMA_HANDLERS)` loop, call `_apply_agent_responses_table_sunset(conn)`. This is the deploy/bootstrap path that satisfies AC 1.

5. In **`_UPSERT_SCHEMA_ENSURE_FLAGS`**, delete the `"agent_responses": ("_agent_responses_schema_ensured",)` entry.

6. In **`_UPSERT_LAZY_SCHEMA_HANDLERS`**, delete the `"agent_responses": _ensure_agent_responses_schema` entry. Do not register the sunset helper as an upsert handler — upsert must not treat `agent_responses` as a live table name.

7. In the module header **Tables used (inventory)**, delete the bullet:
   `- agent_responses — Agent response audit (insert-only from add_agent_response_entry).`
   Leave entity-column mentions on `company` / `job` / `candidate` inventory lines unchanged (those are JSON columns, not this table).

8. Keep `_compress_payload` / `_decompress_payload` (used by `agent_data`). Keep `append_agent_response` and all entity-column parse/update helpers.

9. Confirm by search in `src/data/database.py`:
   - Zero matches for `_ensure_agent_responses_schema`, `_agent_responses_schema_ensured`, `CREATE TABLE agent_responses`.
   - Exactly one `DROP TABLE IF EXISTS agent_responses` (inside the sunset helper).
   - Zero upsert-registry keys named `"agent_responses"` (entity-column SQL strings that mention the column name remain allowed).

⚠️ **Decision:** Do not call sunset from `_ensure_job_schema` / `_ensure_company_schema` / `_ensure_candidate_schema`. Those ensures own entity tables; wiring DROP there would couple unrelated schema paths. Bootstrap (`ensure_all_upsert_registry_schemas_at_startup` via `src/core/bootstrap.py`) is the AC 1 contract path (same family as AST-843).

## Stage 2: Acceptance search (schema lane)

**Done when:** The searches below show no remaining standalone-table CREATE/ensure/registry in `src/` or `scripts/`; DROP exists only in the sunset helper; entity-column identifiers may still appear.

1. From repo root, run:

```bash
rg -n "CREATE TABLE agent_responses|_ensure_agent_responses_schema|_agent_responses_schema_ensured" src scripts --glob '*.py'
rg -n "DROP TABLE IF EXISTS agent_responses" src --glob '*.py'
rg -n '"agent_responses":\s*\(_agent_responses|"agent_responses":\s*_ensure_agent' src/data/database.py
```

2. Expected:
   - Zero matches for CREATE / `_ensure_agent_responses_schema` / `_agent_responses_schema_ensured`.
   - Exactly one `DROP TABLE IF EXISTS agent_responses` in `src/data/database.py`.
   - Zero upsert-registry registrations for the standalone table key.
3. Manually sanity-check that `append_agent_response` and entity-column `agent_responses` handling on company/job/candidate still exist unchanged.
4. `python3 -m py_compile src/data/database.py` passes.

## Self-Assessment

**Scope:** Single-Component — `src/data/database.py` only: inventory, CREATE/ensure removal, upsert-registry deregistration, bootstrap-hooked DROP sunset.

**Conf:** high — AST-981 plan already reserved this exact surface (`_ensure_agent_responses_schema`, registry keys, header inventory); AST-766 establishes the DROP-on-ensure pattern; AC and sibling boundaries are explicit.

**Risk:** Medium — dropping while AST-981 writers still exist would break inserts at runtime; mitigated by Linear `blockedBy` + ftr ancestor gate before Stage 1. Wrongly removing entity-column helpers would break latest-only refs (AST-984 lane) — keep-list and Stage 2 grep mitigate.

## Code Rules check

- §1.1 / `astral.standards.database-header-inventory`: header inventory must drop the retired table (Stage 1 step 7).
- §2.4.1 / `astral.batch.entity-agent-responses-latest-only`: preserved — entity JSON columns and `append_agent_response` stay.
- §2.4 batch / `agent_data`: unchanged — RESPONSE blocks remain the durable store; compress helpers kept.
- §1.3 DRY: one sunset helper + one bootstrap call; no parallel migration script.
- §2.1 config: no new config keys.
- §3.3 imports: no new cross-layer imports; data-layer only.
- Layers: data only; no UI/core edits in this ticket.
- Engineer test-tree ban: Stages forbid engineer commits to `tests/` / bible.

## Review (build stub)

**Built:** `origin/sub/AST-975/AST-982-drop-agent-responses-table-schema` @ `58ee447`.

**Stages delivered:**
- Stage 1: `src/data/database.py` — removed header inventory + `_ensure_agent_responses_schema` + upsert-registry keys; added `_apply_agent_responses_table_sunset` (`DROP TABLE IF EXISTS`) hooked from `ensure_all_upsert_registry_schemas_at_startup`; kept `append_agent_response` + compress helpers — `58ee447`.
- Stage 2: acceptance rg clean (no CREATE/`_ensure_*`); one DROP; entity JSON columns retained.

**Betty:** at **Code Complete** — retire cases that call `_ensure_agent_responses_schema` or assert the standalone table exists in `tests/component/data/database/test_agent_responses.py`; keep entity-column `append_agent_response` coverage until AST-984.


## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-982
**Publish ref tip (pre-docs):** `f201a4785fdeb383eb2d4476978ef8cf483956d3`
**Overall:** DISCUSS

### What’s solid

- Stage 1 matches plan: header inventory bullet removed; `_ensure_agent_responses_schema` / ensure flag / upsert-registry keys gone; `_apply_agent_responses_table_sunset` does single `DROP TABLE IF EXISTS agent_responses` before registry loop in `ensure_all_upsert_registry_schemas_at_startup`.
- Stage 2 rg clean on tip: zero CREATE/`_ensure_*`; exactly one DROP; `append_agent_response` + entity JSON column mentions retained.
- Build gate: AST-981 merge on ftr is an ancestor (`14bc714` / `resolve(AST-981)` lineage) before DROP.
- Betty: one `test(AST-982)` + one `merge-tests(AST-982)` SHA `7215e0b`; sunset bootstrap coverage; conftest flag rename.

### Issues

**discuss (C4 straggler):** Joan Excluded 15 statutes that this three-dot scores in-scope because `origin/dev...publish-ref` still carries AST-981 ancestor paths (`src/core/**`, `scripts/**`, `docs/features/**`, `tests/**`). Substance for all is **conforms** (AST-981 already reviewed; AST-982 `code()` is `database.py` only). No product fix expected — acknowledge at resolve-child.

**advisory:** Broader mandate/bible prose remains AST-983.

### Recommended actions

1. Acknowledge C4 straggler discuss list (no code change).
2. AST-983: mandate/bible/test prose sweep; AST-984: entity JSON column retirement.

### Pattern conformance

none cited

### Plan adherence

Self-Assessment Scope (Single-Component / `database.py`) matches engineer `code(AST-982)`. Sibling keep-list honored. Stages 1–2 delivered.

## Resolution

**Date:** 2026-07-25  
**Review tip:** `dde1cf0` (`docs(AST-982): Radia review — findings`)  
**Outcome:** clean — no product changes.

| Finding | Disposition |
| -- | -- |
| discuss (C4 straggler) — 15 Joan-Excluded statutes scored in-scope via AST-981 ancestors on three-dot vs `origin/dev` | Acknowledged. Substance **conforms**; no product fix. AST-982 `code()` remains `src/data/database.py` only. |
| advisory — mandate/bible prose sweep | Deferred to sibling **AST-983** (and entity-column retirement to **AST-984**). |

