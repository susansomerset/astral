<!-- linear-archive: AST-1141 archived 2026-08-11 -->

## Linear archive (AST-1141)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1141/admin-land-meteorite-api-for-selected-message-ids-manage-email-select  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1129 — Manage Email — select inbox messages and Land Meteorite  
**Blocked by / blocks / related:** parent: AST-1129; blocks: AST-1142

### Description

## What this implements

After #1: thin authenticated admin endpoint that accepts selected message ids, calls the shared selected-ids ingest entrypoint, and returns per-id (or equivalent) outcome payload including skips. Does **not** own multi-select chrome (sibling #3).

## Acceptance criteria

- [X] 2. With a non-empty selection, **Land Meteorite** is available; with an empty selection it is not actionable. *(API: reject empty/missing* `message_ids` *with 400; UI enablement is AST-1142.)*
- [X] 3. Clicking **Land Meteorite** processes **only** the selected message ids through the shared `gaze_email` ingest path from AST-1128 / AST-1140 (`run_gaze_email_selected_ids`).
- [X] 4. Unbound / unmatched selected messages are skipped with explicit feedback; bound selected messages in the same batch still process. *(API returns per-id outcomes from core.)*
- [X] 5. After the action, Archie can tell which selected messages succeeded, were skipped, or failed, without leaving Manage Email. *(API returns* `results` *+ totals; React display is AST-1142.)*

## Boundaries

Does **not** own multi-select chrome (sibling #3). Does **not** own core ingest (sibling #1).

## In scope

- [X] `pattern.ui.admin-endpoint` — thin `POST /api/admin/inbox/land-meteorite` on `api_inbox.py`
- [X] `astral.patterns.require-auth-on-protected-endpoints` — `@require_admin` on the mutator
- [X] `astral.layers.ui-config-driven-business-logic` — skip/create decisions stay in core; API validates request shape and returns core outcomes
- [X] `astral.layers.core-vs-external-bright-line` — UI → core only; no Gmail/external in the route

## Considered but excluded

- [X] Selected-ids core entrypoint `run_gaze_email_selected_ids` + `GAZE_EMAIL_CONFIG` outcome vocabulary — AST-1140 (`src/core/gaze_email.py`, `src/utils/config.py`)
- [X] Manage Email multi-select + Land Meteorite React + Create retirement — AST-1142 (`src/ui/frontend/`)
- [X] Legacy Create strip/extract `POST …/create-job` retirement — AST-1142 (route may remain until then)
- [X] Candidate-bound dispatcher runner / `last_email_check` stamp — AST-1136 (`src/core/gaze_email.py` dispatch path)
- [X] `tests/` / bible — Betty

## Notes for planning

After AST-1140.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite`, child `sub/AST-1129/AST-1141-admin-land-meteorite-api-selected-message-ids`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-02T22:22:48.983Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` failed on `origin/sub/AST-1129/AST-1141-admin-land-meteorite-api-selected-message-ids`:
- offending: `9f4aa98d Merge remote-tracking branch 'origin/dev' into sub/AST-1129/AST-1141-admin-land-meteorite-api-selected-message-ids`

@Hedy Lamarr — republish tip without a `Merge remote-tracking branch` subject (prefer `merge(AST-1141): origin/dev` / merge `origin/ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite`). Keep docs+resolve after the clean merge. Do not force-push unless your skill allows republish rewrite for this gate.

— Chuckles

#### radia — 2026-08-02T22:20:59.709Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1141
**Publish ref:** `615d0767b0dda8a4dcf34853de53e82ae3c3b397` (`origin/sub/AST-1129/AST-1141-admin-land-meteorite-api-selected-message-ids`)
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1129/AST-1141-admin-land-meteorite-api-selected-message-ids`. Active statutes: **65**.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no graded confidence path |
| `astral.agent.do-task-delegation` | scoped | conforms | Ruth stays in AST-1140 shared `_handle_bound`; API does not call `do_task` |
| `astral.agent.grade-vector-validation` | scoped | conforms | no grade-vector path |
| `astral.batch.batch-id-first` | scoped | conforms | land-meteorite not a claim_batch path |
| `astral.batch.batch-id-format` | scoped | conforms | no new batch_id minting |
| `astral.batch.claim-process-release` | scoped | conforms | no claim/release rewrite |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | no agent_data latest-ref changes |
| `astral.config.config-source-of-truth` | scoped | conforms | no new config; consumes AST-1140 outcomes via core |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | no scoring/floor changes |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env values introduced |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths `['artifacts/**', 'scripts/spikes/**']` miss |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | feature plans under `docs/features`; no spikes committed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | API does not hop-chain; core selected-ids stops at METEORITE_NEW |
| `astral.dispatch.seed-auto-false` | scoped | conforms | no seed auto_mode flip |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | AST-1141 plan at `docs/features/meteorite/ast-1141-…md` |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty merge-tests owns tests/bible; engineer owns src/features |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | tests/bible on tip via Betty `test()`/`merge-tests` only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | UI→core only; no Gmail/external in land-meteorite route |
| `astral.layers.import-direction` | scoped | conforms | ui→core `gaze_email` + utils; no data/external added for 1141 |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers `['scripts']` miss; paths `['scripts/**']` miss |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | API validates shape; skip/create stay in core |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | no coat-check changes |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | no consult/render_verdict changes |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | conforms | `@require_admin` on `POST /land-meteorite` |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | no agent JSON seed edits |
| `astral.seed.archie-catalog-wins` | scoped | conforms | no agent catalog seed edits |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | land-meteorite hot path; no seed in request |
| `astral.seed.define-approved` | scoped | conforms | no define-approved seed surface |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | no operator-row resurrection |
| `astral.seed.other-via-coverage-join` | scoped | conforms | no coverage-join seed changes |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | API returns JSON errors; logs warning on 502 |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers `['data']` miss; paths `['src/data/**']` miss |
| `astral.standards.debug-contract-gated` | scoped | conforms | forwards debug via `ui_llm_debug` into core; no ungated Style D in API |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | thin wrapper; sole call `run_gaze_email_selected_ids` |
| `astral.standards.in-scope-only` | scoped | conforms | 1141 `code()` = `api_inbox.py`; core/config on tip from AST-1140 dependency merge |
| `astral.standards.logging-via-utils` | scoped | conforms | uses existing `api_inbox` `get_logger` warning path |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `land-meteorite` / `inbox_land_meteorite` product names |
| `astral.standards.no-cross-contamination` | scoped | conforms | stays on inbox admin UI; no React/Create retirement |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | pass-through core outcome vocabulary; no new sets |
| `astral.standards.public-then-helpers` | scoped | conforms | single route handler; no scattered helpers |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | `config.py` on tip from AST-1140; no new utils→data |
| `astral.state.core-decides-transitions` | scoped | conforms | create decisions remain in core selected-ids path |
| `astral.state.job-prior-states-enforced` | scoped | conforms | no JOB_STATES bypass in API |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | API does not call qualify/GDL; core stops at METEORITE_NEW |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | paths `['src/ui/frontend/**']` miss |
| `astral.ui.naming-conventions` | scoped | conforms | snake_case `POST /api/admin/inbox/land-meteorite` |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no gunicorn/worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1141)` one SHA on tip |
| `orch.git.commit-vocabulary` | universal | conforms | `code()`/`docs()`/`merge-tests()` vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish on `origin/sub/AST-1129/AST-1141-…` |
| `orch.git.ftr-sub-topology` | universal | conforms | child sub under parent AST-1129 |
| `orch.git.merge-on-checkout` | universal | conforms | merged AST-1140/ftr tip before build; `origin/dev` merge on tip |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no cherry-pick/rebase/force |
| `orch.git.no-dev-agent-branches` | universal | conforms | uses `sub/AST-1129/AST-1141-…` only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review in `astral-AST-1129` |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | empty-400 / `asyncio.run` / `api_inbox` surface documented |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 matches tip; Create call banned on new route |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute corpus edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty owns tests/bible via `test()`/`merge-tests` |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Hedy through Tests Passed |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Hedy remains assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path product edits by Radia |

## Pattern conformance

| pattern id (from ticket In scope) | verdict |
|-----------------------------------|---------|
| `pattern.ui.admin-endpoint` | conforms — thin `POST /api/admin/inbox/land-meteorite` on `api_inbox.py` |
| `astral.patterns.require-auth-on-protected-endpoints` | conforms — `@require_admin` |
| `astral.layers.ui-config-driven-business-logic` | conforms — shape validation only; decisions in core |
| `astral.layers.core-vs-external-bright-line` | conforms — UI→core only (Joan noted plan matching excluded this; tip now includes core via AST-1140 merge) |

## Plan adherence

Stage 1 matches tip literally: `@require_admin`, empty/non-list `message_ids` → 400, sole `asyncio.run(run_gaze_email_selected_ids(...))`, pass-through JSON, ValueError→400 / Exception→502+warning, debug via `ui_llm_debug`. Self-Assessment Scope `Single-Component` matches AST-1141 `code()` footprint (`api_inbox.py` only). Legacy Create import remains for `/create-job` until AST-1142 — plan-allowed; unused by land-meteorite.

## Findings

**fix-now:** none.

**discuss (C4 stragglers — excluded at plan time but in-scope on three-dot tip):** tip carries AST-1140 `gaze_email`/`config` + Betty tests/bible via dependency/`merge-tests`, so these Joan-excluded ids scored in-scope (all **conforms**; no product rewrite for the admin mutator):
`astral.agent.confidence-bounds`, `astral.agent.do-task-delegation`, `astral.agent.grade-vector-validation`, `astral.batch.batch-id-first`, `astral.batch.batch-id-format`, `astral.batch.claim-process-release`, `astral.batch.entity-agent-responses-latest-only`, `astral.config.pass-threshold-vs-score-floor`, `astral.debug.spikes-under-debug-dir`, `astral.dispatch.run-next-is-chain-authority`, `astral.dispatch.seed-auto-false`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.core-vs-external-bright-line`, `astral.patterns.coat-check-never-store-empty`, `astral.patterns.render-verdict-orchestrates-consult`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`, `astral.seed.boot-only-not-hot-path`, `astral.seed.define-approved`, `astral.seed.operator-rows-stay-deleted`, `astral.seed.other-via-coverage-join`, `astral.standards.utils-data-late-import-only`, `astral.state.core-decides-transitions`, `astral.state.job-prior-states-enforced`, `astral.state.no-daisy-chain-in-run`.

## What’s solid

- Auth + empty-selection edge + pass-through outcomes for AST-1142.
- No Create strip/extract on the new route; no data/external layer bend.

## Notes

Joan plan-rubric verdict attached (APPROVED).

context_tokens≈48000

#### betty — 2026-08-02T22:00:30.844Z
## QA test manifest

**Publish:** `origin/sub/AST-1129/AST-1141-admin-land-meteorite-api-selected-message-ids` @ `59da8dac` (`merge-tests(AST-1141): origin/tests 981bea0b`)

### 1. Existing coverage (bible-backed)
1. `tests/component/core/test_gaze_email.py::TestAst1140RunGazeEmailSelectedIds` — core selected-ids entrypoint this route calls
2. `tests/component/ui/api/test_api_inbox.py::TestAst1049InboxCreateJobApi` — create-job remains until AST-1142 (regression that Land Meteorite does not replace it yet)

### 2. Broken / obsolete
None — additive route.

### 3. Gaps (new)
1. `tests/component/ui/api/test_api_inbox.py::TestAst1141InboxLandMeteoriteApi` — 200 pass-through + stripped ids; debug wiring; non-list / empty → 400; ValueError → 400; upstream → 502; auth 401/403; **Create strip/extract never called**

### Run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_inbox.py::TestAst1141InboxLandMeteoriteApi \
  -q
```

### Bible shasums (`origin/<publish-ref>`)
- `docs/test-bible/ui/api/api_inbox.md` — `59b0dcdf7a418e93a349bae1d7347318519f24eb5a5768ba7e45e573f9b54ec1`
- `docs/test-bible/core/gaze_email.md` — `64749ff2e464bffbe0941718c064f83a67bc46b0a1c3f9e634e15af194782853`

— Betty

#### joan — 2026-08-02T21:50:40.593Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1141
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 multi-select Manage Email | N/A — boundary (AST-1142) |
| AC2 Land Meteorite available; empty not actionable | Stage 1 — API `400` on missing/empty/non-list `message_ids`; UI enablement AST-1142 |
| AC3 selected-ids shared gaze_email ingest | Stage 1 — sole call `run_gaze_email_selected_ids` |
| AC4 not Create strip/extract path | Stage 1 — forbid import/call of `create_meteorite_job_from_inbox_message` |
| AC5 unbound/unmatched skipped with feedback | Stage 1 — pass-through per-id `results` (skip outcomes from AST-1140) |
| AC6 operator-visible batch outcome without leaving page | Stage 1 — returns `results` + totals; React display AST-1142 |
| AC7 no qualify/GDL; no `last_email_check` | N/A ownership — core AST-1140; API does not stamp or hop |
| AC8 retire per-row Create | N/A — boundary (AST-1142); legacy create-job may remain until then |
| AC9 Style D debug | Stage 1 — forwards `debug` via `ui_llm_debug` into core selected-ids path |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 POST `/land-meteorite` | Functional scope §2 Land Meteorite action + §3 ingest via shared path + §6 outcome payload; Architectural admin-endpoint / require-auth |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| astral.config.config-source-of-truth | conforms | No new config; consumes AST-1140 GAZE_EMAIL_CONFIG outcomes via core return |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values introduced |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.import-direction | conforms | ui → core (run_gaze_email_selected_ids) + utils; no data/external |
| astral.layers.ui-config-driven-business-logic | conforms | API validates shape only; skip/create decisions stay in core |
| astral.patterns.require-auth-on-protected-endpoints | conforms | @require_admin on mutator (matches inbox blueprint) |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work; API returns JSON errors |
| astral.standards.debug-contract-gated | conforms | Forwards debug via ui_llm_debug into core; no React debug; no new ungated contract lines in API |
| astral.standards.dry-and-focused-functions | conforms | Thin wrapper mirrors create-job; no duplicated ingest |
| astral.standards.in-scope-only | conforms | Only api_inbox.py; no React/core/config ownership |
| astral.standards.logging-via-utils | conforms | Uses existing api_inbox logger warning on failure path |
| astral.standards.names-not-ticket-ids | conforms | Route/handler names product-shaped (land-meteorite / inbox_land_meteorite) |
| astral.standards.no-cross-contamination | conforms | Stays on inbox admin UI surface |
| astral.standards.no-hardcoded-sets | conforms | No new outcome/state sets; pass-through core vocabulary |
| astral.standards.public-then-helpers | conforms | Single route handler; no scattered helpers invented |
| astral.ui.naming-conventions | conforms | snake_case API path /land-meteorite under /api/admin/inbox |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub via plan()/code() vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/…; merge ftr tip before build |
| orch.git.ftr-sub-topology | conforms | Child publish ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | Depends on AST-1140 via ftr merge; no illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1129/AST-1141-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1129 assumed |
| orch.git.three-permanent-branches | conforms | Does not invent permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented (api_inbox surface, empty 400, asyncio.run) |
| orch.pipeline.plan-is-bible | conforms | Binding stage + Files Changed + forbidden Create call present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan gate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly no tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits proposed |

## Considered and excluded

**Considered:** astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker, orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans

**Excluded:**
- astral.agent.confidence-bounds — layers ['core', 'utils'] ∩ plan ['ui'] empty
- astral.agent.do-task-delegation — layers ['core'] ∩ plan ['ui'] empty
- astral.agent.grade-vector-validation — layers ['core'] ∩ plan ['ui'] empty
- astral.batch.batch-id-first — layers ['data', 'core'] ∩ plan ['ui'] empty
- astral.batch.batch-id-format — layers ['core', 'data'] ∩ plan ['ui'] empty
- astral.batch.claim-process-release — layers ['core', 'data'] ∩ plan ['ui'] empty
- astral.batch.entity-agent-responses-latest-only — layers ['core', 'data'] ∩ plan ['ui'] empty
- astral.config.pass-threshold-vs-score-floor — layers ['core', 'data', 'utils'] ∩ plan ['ui'] empty
- astral.debug.no-repo-root-artifacts-dir — paths ['artifacts/**', 'scripts/spikes/**'] match none of plan paths
- astral.debug.spikes-under-debug-dir — paths ['debug/**', 'docs/features/**', 'scripts/spikes/**'] match none of plan paths
- astral.dispatch.run-next-is-chain-authority — layers ['core', 'utils'] ∩ plan ['ui'] empty
- astral.dispatch.seed-auto-false — layers ['core', 'utils'] ∩ plan ['ui'] empty
- astral.docs.features-single-file-per-ticket — layers ['docs'] ∩ plan ['ui'] empty
- astral.git.engineer-test-tree-ban — paths ['tests/**', 'docs/test-bible/**', 'docs/ASTRAL_TEST_BIBLE.md', 'scripts/test_*.py', 'scripts/testing/**'] match none of plan paths
- astral.layers.core-vs-external-bright-line — layers ['core', 'external'] ∩ plan ['ui'] empty
- astral.layers.scripts-exempt-from-layer-rules — layers ['scripts'] ∩ plan ['ui'] empty
- astral.patterns.coat-check-never-store-empty — layers ['core'] ∩ plan ['ui'] empty
- astral.patterns.render-verdict-orchestrates-consult — layers ['core'] ∩ plan ['ui'] empty
- astral.seed.agent-tables-in-repo-json — layers ['core', 'data', 'utils'] ∩ plan ['ui'] empty
- astral.seed.archie-catalog-wins — layers ['core', 'utils'] ∩ plan ['ui'] empty
- astral.seed.boot-only-not-hot-path — layers ['core', 'data', 'utils', 'scripts'] ∩ plan ['ui'] empty
- astral.seed.define-approved — layers ['core', 'data', 'utils', 'docs'] ∩ plan ['ui'] empty
- astral.seed.operator-rows-stay-deleted — layers ['core', 'data', 'utils'] ∩ plan ['ui'] empty
- astral.seed.other-via-coverage-join — layers ['core', 'data', 'utils'] ∩ plan ['ui'] empty
- astral.standards.database-header-inventory — layers ['data'] ∩ plan ['ui'] empty
- astral.standards.utils-data-late-import-only — layers ['utils'] ∩ plan ['ui'] empty
- astral.state.core-decides-transitions — layers ['core', 'data'] ∩ plan ['ui'] empty
- astral.state.job-prior-states-enforced — layers ['core', 'data', 'utils'] ∩ plan ['ui'] empty
- astral.state.no-daisy-chain-in-run — layers ['core'] ∩ plan ['ui'] empty
- astral.ui.frontend-file-placement — paths ['src/ui/frontend/**'] match none of plan paths

## Findings

None fix-now.

**discuss (non-blocking):** Ticket In-scope cites `astral.layers.core-vs-external-bright-line`, but matching excludes it (layers core/external only). Plan still correctly keeps UI→core with no Gmail/external in the route; covered under `astral.layers.import-direction`.

**acceptable:** Self-assessment Scope Single-Component / Conf high / Risk Medium matches a thin mutator over live ingest with explicit Create-ban + `@require_admin`.

**R6 checklist:** Definition fidelity pass for child #2. Layer/import pass. No new config. Auth on mutator. File placement N/A (existing `api_inbox.py`). No React/core scope creep.

context_tokens≈42000

— Joan

#### hedy — 2026-08-02T21:48:18.970Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1129/AST-1141-admin-land-meteorite-api-selected-message-ids/docs/features/meteorite/ast-1141-admin-land-meteorite-api-selected-message-ids.md

- **Scope:** Single-Component — one `POST /api/admin/inbox/land-meteorite` route on existing `api_inbox` blueprint; calls AST-1140 `run_gaze_email_selected_ids`.
- **Conf:** high — return contract and outcome keys already on `ftr` from AST-1140; mirrors create-job + `asyncio.run` admin patterns.
- **Risk:** Medium — live mailbox mutator; mitigated by `@require_admin` and explicit ban on Create strip/extract path.

---

# AST-1141 — Admin Land Meteorite API for selected message ids

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1141/admin-land-meteorite-api-for-selected-message-ids-manage-email-select  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite  

**Publish ref (origin):** `sub/AST-1129/AST-1141-admin-land-meteorite-api-selected-message-ids`  
**Parent integration ref:** `ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite`

Thin authenticated admin HTTP surface for **Land Meteorite**: accept an explicit list of Astral inbox message ids, call AST-1140’s `run_gaze_email_selected_ids`, and return the per-id outcome payload (including skips) so Manage Email React (AST-1142) can show batch feedback without leaving the page. Does **not** own multi-select chrome or Create retirement (AST-1142). Does **not** own core ingest (AST-1140). Does **not** call the retired Create strip/extract path (`create_meteorite_job_from_inbox_message`).

**Depends on:** AST-1140 on `origin/ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite` (merge that tip before build — public `run_gaze_email_selected_ids` + `GAZE_EMAIL_CONFIG` selected outcome keys must exist).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_inbox.py` | Add `POST /land-meteorite` under existing inbox admin blueprint; `@require_admin`; call core selected-ids entrypoint; return per-id outcomes | ui |

No `src/core/**`, no React, no `src/utils/config.py` (outcome vocabulary already on AST-1140), no new blueprint, no `tests/` / bible.

---

## Stage 1: `POST /api/admin/inbox/land-meteorite`

**Done when:** An authenticated admin can `POST` a JSON body with a non-empty `message_ids` list and receive `200` with the AST-1140 result shape (`results` + totals). Empty / missing / non-list `message_ids` → `400`. Unauthenticated → `401`, non-admin → `403`. Upstream/core failures → `502`. The Create strip/extract helper is never imported or called from this route.

1. In `src/ui/api/api_inbox.py`, extend the module docstring to note AST-1141 Land Meteorite selected-ids admin mutator (keep the AST-1033/1047/1049/1061 lines).

2. Add imports (keep existing imports; add only what the new route needs):

```python
import asyncio

from src.core.gaze_email import run_gaze_email_selected_ids
```

Do **not** import `create_meteorite_job_from_inbox_message` for this route (it may remain for the legacy create-job route until AST-1142 retires Create).

3. Add this route on `inbox_bp` (after the existing create-job handler is fine — same blueprint prefix `/api/admin/inbox`):

```python
@inbox_bp.route("/land-meteorite", methods=["POST"])
@require_admin
def inbox_land_meteorite():
    body = request.get_json(silent=True) or {}
    raw_ids = body.get("message_ids")
    if not isinstance(raw_ids, list):
        return jsonify({"error": "message_ids must be a list"}), 400
    # Strip empties the same way core does; reject empty selection at the API edge
    # so Manage Email can treat empty as non-actionable without a core round-trip.
    message_ids = [str(x).strip() for x in raw_ids if str(x or "").strip()]
    if not message_ids:
        return jsonify({"error": "message_ids is required"}), 400
    explicit = (
        request.args.get("debug", "").lower() in ("1", "true", "yes")
        or bool(body.get("debug"))
    )
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        result = asyncio.run(
            run_gaze_email_selected_ids(message_ids, debug=debug)
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.warning("[api_inbox] land-meteorite failed: %s", e)
        return jsonify({"error": str(e)}), 502
    return jsonify(result), 200
```

4. Response contract (pass-through of AST-1140 return dict — do **not** reshape keys):

```json
{
  "results": [
    {
      "message_id": "<id>",
      "outcome": "<string from GAZE_EMAIL_CONFIG / bound helper>",
      "astral_candidate_id": "<id or null>"
    }
  ],
  "total_processed": 0,
  "total_passed": 0,
  "total_failed": 0,
  "total_errors": 0,
  "total_skipped": 0
}
```

Skip outcomes already defined on AST-1140 (`skipped-unbound`, `skipped-not-in-inbox`, `skipped-unmatched`, plus bound outcomes such as `archived` / `ignored` / `failed` / `error`). AST-1142 renders these; this ticket only returns them.

5. Behavior rules (literal):

   - Call **only** `run_gaze_email_selected_ids` for the batch — never `create_meteorite_job_from_inbox_message`, never dispatcher `run_gaze_email(task)`.
   - Preserve caller order of non-empty ids (core already preserves order).
   - Do **not** stamp `last_email_check` in the API (core already does not).
   - Do **not** add React, nav, or Create-retirement logic here.
   - Do **not** invent a parallel Land-Meteorite config block; wire path is the literal `/land-meteorite` on the existing inbox admin blueprint (same pattern as `/messages` and `/messages/<id>/create-job`).

⚠️ **Decision — stay on `api_inbox.py`:** Manage Email already talks to `/api/admin/inbox/**` (AST-1033/1048/1049). Land Meteorite is the batch mutator for that same surface; a new blueprint would only split the inbox admin contract without a layer reason.

⚠️ **Decision — reject empty at the API edge:** Parent AC2 (“empty selection is not actionable”) is primarily UI, but the mutator must not silently no-op. Mirror create-job’s `400` for missing id so AST-1142 can rely on enablement + a hard server check.

⚠️ **Decision — `asyncio.run`:** `run_gaze_email_selected_ids` is async (shares `_handle_bound`). Other admin/async Flask routes already use `asyncio.run` (`api_admin` adhoc, `api_intake`). No new event-loop helper.

**Done when (recheck):**

- `python3 -m py_compile src/ui/api/api_inbox.py` succeeds.
- Route is registered: `POST /api/admin/inbox/land-meteorite` with `@require_admin`.
- Manual smoke (admin token): non-empty `message_ids` → `200` + `results` length matching stripped ids; `{}` or `"message_ids": []` → `400`; no Bearer → `401`.

---

## Self-Assessment

**Scope:** `Single-Component` — one new route on the existing inbox admin blueprint; no core or React.

**Conf:** `high` — AST-1140 return contract is on `ftr`; pattern matches `api_inbox` create-job + `asyncio.run` elsewhere; auth decorator already required on this blueprint.

**Risk:** `Medium` — mutator touches live mailbox ingest for selected ids; wrong wiring to Create strip/extract or missing `@require_admin` would be severe. Mitigations are explicit import/call ban on Create and `@require_admin` on the route.

---

## Code Rules check

- **§2.9 / `astral.patterns.require-auth-on-protected-endpoints`:** `@require_admin` on the mutator (stricter than `@require_auth`; matches every other inbox admin route).
- **§3.2 / `astral.layers.core-vs-external-bright-line`:** UI calls core only; no Gmail/external imports in `api_inbox.py`.
- **`astral.layers.ui-config-driven-business-logic`:** eligibility/skip/create decisions stay in core; API validates request shape and returns core outcomes; React (sibling) only renders.
- **§1.3 / `pattern.ui.admin-endpoint`:** thin Flask wrapper; no business rules invented in the route beyond empty-list / type guards.
- **§2.1:** no new config block; selected outcome vocabulary already in `GAZE_EMAIL_CONFIG` (AST-1140).
- **§3.3:** ui → core + utils only; no data/external imports added.

---

## Review

| Stage | Commit | Notes |
|-------|--------|-------|
| 1 | `e7144d4a` | `POST /api/admin/inbox/land-meteorite` → `run_gaze_email_selected_ids` |

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Publish ref tip (at review):** see Linear comment after `docs()` push  
**Overall:** DISCUSS (no fix-now on AST-1141 API; C4 dependency-merge stragglers)

**What’s solid**
- Thin `POST /land-meteorite` with `@require_admin`; empty/non-list → 400; sole call `run_gaze_email_selected_ids` via `asyncio.run`; pass-through result JSON; 502 + warning on upstream failure.
- Debug forwarded via `ui_llm_debug`; no Create strip/extract on the new route; no Gmail/external/data imports added.
- AST-1141 `code()` touches only `src/ui/api/api_inbox.py` (+ plan stub).

**Issues / Recommended**
- **discuss (C4 stragglers):** Tip includes AST-1140 core/config + Betty tests/bible via dependency/`merge-tests`, so many Joan-excluded statutes are in-scope on the three-dot diff; all scored **conforms** (see Linear). No product rewrite for the admin mutator.
- Legacy `create_meteorite_job_from_inbox_message` import remains for `/create-job` until AST-1142 — plan-allowed; not used by land-meteorite.

Full `## Statutes checked` (65/65) lives in the Linear Review Posted comment.

---

## Resolution

**Date:** 2026-08-02  
**Radia tip:** `615d0767` (`docs(AST-1141): Radia review — findings`)  
**Outcome:** clean — no product changes

| Finding | Action |
|---------|--------|
| fix-now | none |
| discuss (C4 stragglers — dependency merge in-scope statutes) | Acknowledged; all scored **conforms**. No API rewrite. Legacy Create import stays until AST-1142 per plan. |

`POST /api/admin/inbox/land-meteorite` unchanged from Stage 1 tip `e7144d4a`.
