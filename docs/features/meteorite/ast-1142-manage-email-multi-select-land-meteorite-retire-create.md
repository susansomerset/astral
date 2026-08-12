<!-- linear-archive: AST-1142 archived 2026-08-11 -->

## Linear archive (AST-1142)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1142/manage-email-multi-select-land-meteorite-retire-create-manage-email  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1129 — Manage Email — select inbox messages and Land Meteorite  
**Blocked by / blocks / related:** parent: AST-1129

### Description

## What this implements

After #2: Manage Email list multi-select + **Land Meteorite** control wired to the admin API; operator-visible batch outcome (including skips); **retire** the per-row Create control when Land Meteorite ships. Does **not** redesign the rest of Manage Email.

## Acceptance criteria

- [X] 1. On Manage Email, Archie can select multiple current inbox messages and clear that selection without leaving the page.
- [X] 2. With a non-empty selection, **Land Meteorite** is available; with an empty selection it is not actionable.
- [X] 3. After the action, Archie can tell which selected messages succeeded, were skipped, or failed, without leaving Manage Email.
- [X] 4. When Land Meteorite is available on Manage Email, the per-row **Create** control is gone (retired).

## Boundaries

* Does **not** redesign the rest of Manage Email.
* Does **not** own core selected-ids ingest (AST-1140).
* Does **not** own admin Land Meteorite HTTP (AST-1141).
* Does **not** delete leftover `/create-job` API (UI Create retirement only).
* Does **not** stamp `last_email_check` or change bind rules.

## In scope

- [X] `pattern.ui.admin-endpoint` — consume existing `POST /api/admin/inbox/land-meteorite`; no new Flask route (`src/ui/frontend/src/pages/AdminManageEmail.tsx`)
- [X] `astral.layers.ui-config-driven-business-logic` — React selects ids + renders server `outcome` strings; no bind/ingest rules in the page (`AdminManageEmail.tsx`)
- [X] `astral.standards.in-scope-only` — multi-select + Land Meteorite + Create retirement only (`AdminManageEmail.tsx`, `App.css`)
- [X] `astral.ui.frontend-file-placement` — edit stays under `src/ui/frontend/src/pages/` + existing `App.css`
- [X] `astral.ui.naming-conventions` — route `admin/manage_email` unchanged; page remains `AdminManageEmail.tsx`

## Considered but excluded

- [X] Selected-ids core ingest / Style D — AST-1140 (`src/core/gaze_email.py`)
- [X] Admin `POST /land-meteorite` mutator — AST-1141 (`src/ui/api/api_inbox.py`)
- [X] Delete leftover `/messages/<id>/create-job` API — UI Create retirement only this ticket
- [X] Migrate Manage Email onto shared `ListPage` selectable chrome — custom page kept
- [X] NAV_CONFIG / routes / match-rules redesign — out of parent boundaries
- [X] React debug logging — parent AC is backend Style D only

## Notes for planning

After AST-1141. Plan: `docs/features/meteorite/ast-1142-manage-email-multi-select-land-meteorite-retire-create.md`.

## Git branch (authoritative)

`origin/sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create` — ignore Linear `gitBranchName`.

### Comments

#### chuckles — 2026-08-02T22:39:54.474Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` fails on `origin/sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create` vs `origin/ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite` because range includes:
`2bb45ac1 Merge remote-tracking branch 'origin/ftr/AST-1128-gaze-email-candidate-bound-dispatch-redesign' into dev`
(brought in via `83a3d706 merge(AST-1142): origin/dev into publish ref`).

@Katherine Johnson — republish the sub tip stacked on `origin/ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite` only (keep plan/code/merge-tests/test/docs/resolve for AST-1142; drop the origin/dev merge that imported the pull-merge subject). Then Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-08-02T22:38:20.305Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1142
**Publish ref:** `e70e804e605624b257662bd9645f32297b645e1e` (`origin/sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create`)
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create`. Active statutes: **65**.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no graded confidence path |
| `astral.agent.do-task-delegation` | scoped | conforms | React does not call `do_task` |
| `astral.agent.grade-vector-validation` | scoped | conforms | no grade-vector path |
| `astral.batch.batch-id-first` | scoped | conforms | no claim_batch path |
| `astral.batch.batch-id-format` | scoped | conforms | no new batch_id minting |
| `astral.batch.claim-process-release` | scoped | conforms | no claim/release rewrite |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | no agent_data latest-ref |
| `astral.config.config-source-of-truth` | scoped | conforms | no new config; renders server outcome strings |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | no scoring/floor changes |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env values |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths `['artifacts/**', 'scripts/spikes/**']` miss |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | feature plans under `docs/features` |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | React does not hop-chain |
| `astral.dispatch.seed-auto-false` | scoped | conforms | no seed auto_mode flip |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | AST-1142 plan at `docs/features/meteorite/ast-1142-…md` |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty owns tests/bible; engineer owns src/features |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | tests/bible via Betty `test()`/`merge-tests` |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | frontend→api only; ingest stays core |
| `astral.layers.import-direction` | scoped | conforms | React→`api()` only; no core/data/external imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers `['scripts']` miss; paths `['scripts/**']` miss |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | any row selectable; skip/bind stay server-side |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | no coat-check changes |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | no consult/render_verdict |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | conforms | consumes auth’d land-meteorite via `api()` |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | no agent JSON seed |
| `astral.seed.archie-catalog-wins` | scoped | conforms | no agent catalog seed |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | no seed in request path |
| `astral.seed.define-approved` | scoped | conforms | no define-approved seed |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | no operator-row resurrection |
| `astral.seed.other-via-coverage-join` | scoped | conforms | no coverage-join seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | UI shows `landError` from HTTP body |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers `['data']` miss; paths `['src/data/**']` miss |
| `astral.standards.debug-contract-gated` | scoped | conforms | no React debug logging; AC9 backend |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | reuse api/toast/load; no ListPage migration |
| `astral.standards.in-scope-only` | scoped | conforms | 1142 code=`AdminManageEmail`+`App.css`; siblings via dependency merge |
| `astral.standards.logging-via-utils` | scoped | conforms | frontend toast/error text only |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | Land Meteorite label; `AdminManageEmail` unchanged |
| `astral.standards.no-cross-contamination` | scoped | conforms | stays on Manage Email frontend |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | `outcomeKind` display-only CSS bucketing of server strings |
| `astral.standards.public-then-helpers` | scoped | conforms | page-local helpers; no scattered public API |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | config on tip from AST-1140; no new utils→data |
| `astral.state.core-decides-transitions` | scoped | conforms | React does not decide job transitions |
| `astral.state.job-prior-states-enforced` | scoped | conforms | no JOB_STATES bypass |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | React does not call qualify/GDL |
| `astral.ui.frontend-file-placement` | scoped | conforms | `pages/AdminManageEmail.tsx` + `App.css` only |
| `astral.ui.naming-conventions` | scoped | conforms | route `admin/manage_email` + PascalCase page unchanged |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no gunicorn/worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1142)` one SHA |
| `orch.git.commit-vocabulary` | universal | conforms | `code()`/`docs()`/`merge-tests()` vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish on `origin/sub/AST-1129/AST-1142-…` |
| `orch.git.ftr-sub-topology` | universal | conforms | child sub under parent AST-1129 |
| `orch.git.merge-on-checkout` | universal | conforms | merged ftr/dev before build |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no cherry-pick/rebase/force |
| `orch.git.no-dev-agent-branches` | universal | conforms | uses `sub/AST-1129/AST-1142-…` only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review in `astral-AST-1129` |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | custom page / Set / subject snapshot / raw outcomes documented |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match tip; Create retired |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute corpus edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty owns tests/bible |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Katherine through Tests Passed |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Katherine remains assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path product edits by Radia |

## Pattern conformance

| pattern id (from ticket In scope) | verdict |
|-----------------------------------|---------|
| `pattern.ui.admin-endpoint` | conforms — consumes existing `POST /api/admin/inbox/land-meteorite`; no new Flask route |
| `astral.layers.ui-config-driven-business-logic` | conforms — selects ids + renders server outcomes |
| `astral.standards.in-scope-only` | conforms — multi-select + Land Meteorite + Create retirement |
| `astral.ui.frontend-file-placement` | conforms — `pages/` + `App.css` |
| `astral.ui.naming-conventions` | conforms — `admin/manage_email` / `AdminManageEmail.tsx` unchanged |

## Plan adherence

Stages 1–2 match tip: selection chrome, enablement gate, POST with ordered ids + leftovers, subject snapshot, results panel with raw outcomes, Create fully retired (no `create-job` / `manage-email-create`). Self-Assessment Scope `Single-Component` matches `code()` footprint (`AdminManageEmail.tsx` + `App.css`).

## Findings

**fix-now:** none.

**discuss (C4 stragglers — excluded at plan time but in-scope on three-dot tip):** tip carries AST-1140/1141 + Betty tests/bible via dependency/`merge-tests`. All scored **conforms**; no product rewrite for this UI:
`astral.agent.confidence-bounds`, `astral.agent.do-task-delegation`, `astral.agent.grade-vector-validation`, `astral.batch.batch-id-first`, `astral.batch.batch-id-format`, `astral.batch.claim-process-release`, `astral.batch.entity-agent-responses-latest-only`, `astral.config.pass-threshold-vs-score-floor`, `astral.debug.spikes-under-debug-dir`, `astral.dispatch.run-next-is-chain-authority`, `astral.dispatch.seed-auto-false`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.core-vs-external-bright-line`, `astral.patterns.coat-check-never-store-empty`, `astral.patterns.render-verdict-orchestrates-consult`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`, `astral.seed.boot-only-not-hot-path`, `astral.seed.define-approved`, `astral.seed.operator-rows-stay-deleted`, `astral.seed.other-via-coverage-join`, `astral.standards.utils-data-late-import-only`, `astral.state.core-decides-transitions`, `astral.state.job-prior-states-enforced`, `astral.state.no-daisy-chain-in-run`.

**advisory:** `outcomeKind` display bucketing matches Joan’s non-blocking plan discuss — not eligibility logic.

## What’s solid

- Empty selection → Land Meteorite disabled; checkbox does not open modal.
- Create retired completely on the page/CSS.
- Outcomes stay server-authored strings.

## Notes

Joan plan-rubric verdict attached (APPROVED).

context_tokens≈48000

#### betty — 2026-08-02T22:36:03.303Z
## QA test manifest

**Publish:** `origin/sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create` @ `957d91db` (`merge-tests(AST-1142): origin/tests 83fc167a`)

### 1. Existing coverage (bible-backed)
1. `test_AdminManageEmail.test.tsx` — first-paint list, Candidate column, modal raw HTML (AST-1033/1040/1048) — retained
2. `TestAst1141InboxLandMeteoriteApi` — admin POST this page consumes

### 2. Broken / obsolete (revised this pass)
1. AST-1049/1051/1061 list-row **Create** POST/toast + Actions column cases — Create retired
2. Body-error case that expected Create enabled — now asserts Create absent + Land Meteorite present (disabled with empty selection)

### 3. Gaps (new)
1. `AdminManageEmail — AST-1142` describe (§6c):
   - Select / Select all / Clear; Land Meteorite enablement; checkbox does not open modal
   - Land Meteorite POST `message_ids` + results panel (archived / skipped-unbound) + toast totals; reload drops archived; **never** `/create-job`
   - HTTP error keeps selection + inline error

### Run
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx
```

### Bible shasums (`origin/<publish-ref>`)
- `docs/test-bible/frontend/pages.md` — `edc8211579affd26645ed5d1f232933099f3e716115192a54f2c65fbb36cc5da`
- `docs/test-bible/ui/api/api_inbox.md` — `118b8e3cd838f868a60a86cf6ef0865c5c5520d76cde312b1ac650dff459973e`

— Betty

#### joan — 2026-08-02T22:30:56.066Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1142
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 multi-select + clear selection | Stage 1 — checkbox column, Select all / Clear, selection stays on page |
| AC2 Land Meteorite enablement | Stage 1 — enabled iff selection non-empty and not busy |
| AC3 selected-ids shared ingest | Stage 2 — POST `/api/admin/inbox/land-meteorite` with selected ids only |
| AC4 not Create strip/extract path | Stage 2 — ban `/create-job`; retire Create UI |
| AC5 unbound/unmatched skipped with feedback | Stage 2 — results panel shows raw skip outcomes from API |
| AC6 operator-visible batch outcome on page | Stage 2 — per-id results + error paragraph; no navigation away |
| AC7 no qualify/GDL; no `last_email_check` | N/A ownership — core/API siblings; React does not stamp or hop |
| AC8 retire per-row Create | Stage 2 — delete Create button/handler/Actions column/CSS |
| AC9 Style D debug | N/A — boundary (backend AST-1140/1141); no React debug |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 multi-select + enablement | Functional scope §1–2; Purpose selection chrome |
| Stage 2 POST + outcomes + retire Create | Functional scope §3–6 + Create retirement; Purpose Land Meteorite |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| astral.config.config-source-of-truth | conforms | No new config; consumes AST-1141/1140 outcome strings as returned |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values introduced |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.import-direction | conforms | React → api() only; no core/data/external imports |
| astral.layers.ui-config-driven-business-logic | conforms | Any inbox row selectable; skip/bind decisions stay server-side; renders outcome strings |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Consumes existing auth’d land-meteorite via api(); no new open routes |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work; UI shows landError from HTTP body |
| astral.standards.debug-contract-gated | conforms | No React debug logging; parent AC9 is backend |
| astral.standards.dry-and-focused-functions | conforms | Reuse api()/toast/load pattern; no ListPage migration churn |
| astral.standards.in-scope-only | conforms | Multi-select + Land Meteorite + Create retirement only; no nav/core/API edits |
| astral.standards.logging-via-utils | conforms | No Python logging path; frontend toast/error text only |
| astral.standards.names-not-ticket-ids | conforms | Product labels Land Meteorite; page AdminManageEmail unchanged |
| astral.standards.no-cross-contamination | conforms | Stays on Manage Email frontend surface |
| astral.standards.no-hardcoded-sets | conforms | No eligibility sets; outcomeKind is display-only CSS bucketing of server strings |
| astral.standards.public-then-helpers | conforms | Page-local helpers for selection/land; no scattered public API |
| astral.ui.frontend-file-placement | conforms | Edit pages/AdminManageEmail.tsx + App.css; no new subdirs |
| astral.ui.naming-conventions | conforms | Route admin/manage_email and PascalCase page unchanged |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub via plan()/code() vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/…; merge ftr tip before build |
| orch.git.ftr-sub-topology | conforms | Child publish ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | Depends on AST-1141 via ftr merge; no illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1129/AST-1142-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1129 assumed |
| orch.git.three-permanent-branches | conforms | Does not invent permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented (custom page, client Set, subject snapshot, raw outcomes) |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed + Create retirement checklist present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan gate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly no tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits proposed |

## Considered and excluded

**Considered:** astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker, orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans

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

## Findings

None fix-now.

**discuss (non-blocking):** Stage 2 `outcomeKind` buckets server `outcome` strings into CSS classes via a few literal compares / `skipped-` prefix. Plan labels this display-only (not eligibility). Acceptable vs `ui-config-driven-business-logic`; if Archie wants zero outcome-string knowledge in React later, CSS could be driven by a server-supplied presentation hint — out of this child’s AC.

**acceptable:** Self-assessment Scope Single-Component / Conf high / Risk Medium matches UI-only wiring with explicit Create deletion + literal endpoint path.

**R6 checklist:** Definition fidelity pass for child #3. Layer/import pass. No new config/routes. File placement pass. No core/API/nav scope creep. Create retired when Land Meteorite ships (same Stage 2).

context_tokens≈45000

— Joan

#### katherine — 2026-08-02T22:28:51.105Z
Plan published on `origin/sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create` @ `a82f3119`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create/docs/features/meteorite/ast-1142-manage-email-multi-select-land-meteorite-retire-create.md

**Self-assessment**
- **Scope:** Single-Component — `AdminManageEmail.tsx` + small `App.css`; consumes AST-1141 `POST /land-meteorite` only.
- **Conf:** high — API contract is on ftr; page already lists inbox via `api()`; Create retirement is delete of known UI.
- **Risk:** Medium — wrong POST wiring or leaving Create would miss parent AC; mitigated by literal endpoint path, empty-selection disable, and explicit Create deletion checklist.

**Stages:** (1) multi-select chrome + Land Meteorite enablement; (2) POST + per-id outcome panel + retire Create.

---

# AST-1142 — Manage Email multi-select + Land Meteorite + retire Create

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1142/manage-email-multi-select-land-meteorite-retire-create-manage-email  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite  

**Publish ref (origin):** `sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create`  
**Parent integration ref:** `ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite`

After AST-1141: add multi-select + **Land Meteorite** on Manage Email, wire it to `POST /api/admin/inbox/land-meteorite`, show per-selected-message outcomes (including skips) without leaving the page, and **retire** the per-row **Create** control. Does **not** redesign the rest of Manage Email. Does **not** own core ingest (AST-1140) or the admin API (AST-1141). Does **not** call `/create-job` / strip-extract create.

**Depends on:** AST-1141 on `origin/ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite` (merge that tip before build — `POST /api/admin/inbox/land-meteorite` + pass-through `results` / totals must exist).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminManageEmail.tsx` | Multi-select; Land Meteorite; batch outcome panel; remove Create | ui |
| `src/ui/frontend/src/App.css` | Toolbar / outcome / checkbox styles; drop `.manage-email-create` | ui |

No `src/core/**`, no `src/ui/api/**`, no `src/utils/config.py`, no `tests/` / bible, no route/nav changes.

---

## Stage 1: Multi-select chrome + Land Meteorite enablement (no POST yet)

**Done when:** On Manage Email, Archie can select/deselect individual inbox rows, select all visible rows, and clear selection without leaving the page. A **Land Meteorite** control is visible; it is disabled (not actionable) when the selection is empty and enabled when one or more message ids are selected. Per-row **Create** is still present in this stage (retired in Stage 2). No Land Meteorite network call yet.

1. In `src/ui/frontend/src/pages/AdminManageEmail.tsx`, add selection state:

   ```ts
   const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
   ```

   Helpers (inline functions or `useCallback` — match existing page style; this file already uses `useCallback` for toast clear):

   - `toggleSelect(id: string)` — add/remove id in a new `Set` copy.
   - `selectAllVisible()` — `setSelectedIds(new Set(messages.map(m => m.id)))`.
   - `clearSelection()` — `setSelectedIds(new Set())`.
   - `selectionCount = selectedIds.size`.
   - `landEnabled = selectionCount > 0 && !landBusy` (introduce `landBusy` boolean state now, default `false`; Stage 2 sets it during POST).

2. Above the table (inside the `!loading && !error` block), add a toolbar row with:

   - Button **Select all** → `selectAllVisible()` (disabled when `messages.length === 0`).
   - Button **Clear selection** → `clearSelection()` (disabled when `selectionCount === 0`).
   - Button **Land Meteorite** → Stage 1: `type="button"` with `disabled={!landEnabled}`; `onClick` may be a no-op stub `() => {}` or omitted until Stage 2 — must not call `/create-job`. Label text exactly `Land Meteorite`.
   - Short status text: `{selectionCount} selected` (plain text).

3. Add a leading checkbox column:

   - Header: checkbox that is checked when `messages.length > 0 && selectedIds.size === messages.length`; `onChange` → if all selected then `clearSelection()`, else `selectAllVisible()`. Stop row-open behavior is N/A on `<th>`.
   - Each body row: `<td onClick={e => e.stopPropagation()}>` wrapping `<input type="checkbox" checked={selectedIds.has(row.id)} onChange={() => toggleSelect(row.id)} />`.
   - Keep existing row `onClick={() => openMessage(row)}` for subject/body open; checkbox cell must not open the modal.

4. Update empty-state `colSpan` from `6` to `7` (new checkbox column).

5. In `src/ui/frontend/src/App.css`, add minimal classes next to the existing `.manage-email-*` block (after `.manage-email-create` is fine):

   - `.manage-email-toolbar` — flex row, gap, margin under the h1 / above the table.
   - `.manage-email-toolbar button` — reuse button look consistent with `.manage-email-create` (padding/font), including `:disabled` opacity.
   - Do **not** delete `.manage-email-create` yet (Stage 2).

⚠️ **Decision — stay on custom `AdminManageEmail` page, do not migrate to `ListPage`:** Parent AC is selection + Land Meteorite + Create retirement only. Rewiring the page through `ListPage` would expand scope into shared list chrome without buying AC fidelity.

⚠️ **Decision — selection is client-only `Set<string>` of message ids:** Server already owns ingest eligibility (AST-1140/1141). React must not invent bind/match filters for which rows may be selected — any current inbox row is selectable; skips come back in the API `results`.

**Done when (recheck):** With ≥2 loaded messages, select two → toolbar shows `2 selected` and Land Meteorite enabled; Clear → `0 selected` and Land Meteorite disabled; Select all → all checkboxes on; clicking a checkbox does not open the message modal; Create still visible on matched rows.

---

## Stage 2: Wire Land Meteorite POST + outcome panel + retire Create

**Done when:** Clicking **Land Meteorite** with a non-empty selection `POST`s `{ "message_ids": [...] }` to `/api/admin/inbox/land-meteorite`, shows each selected id’s `outcome` (and subject when known) on the page, surfaces HTTP errors without navigating away, retires per-row Create (button + handler + busy state + CSS), and does not call `/create-job`.

1. Add types for the AST-1141 response (local to the page file):

   ```ts
   type LandMeteoriteResultRow = {
     message_id: string
     outcome: string
     astral_candidate_id: string | null
   }

   type LandMeteoriteResponse = {
     results?: LandMeteoriteResultRow[]
     total_processed?: number
     total_passed?: number
     total_failed?: number
     total_errors?: number
     total_skipped?: number
     error?: string
   }
   ```

2. Add state:

   ```ts
   const [landBusy, setLandBusy] = useState(false)
   const [landResults, setLandResults] = useState<LandMeteoriteResultRow[] | null>(null)
   const [landError, setLandError] = useState<string | null>(null)
   ```

3. Implement `async function onLandMeteorite()`:

   - If `selectedIds.size === 0` or `landBusy`: return.
   - `const ids = messages.filter(m => selectedIds.has(m.id)).map(m => m.id)` — preserve **current list order** (stable display); if a selected id is missing from `messages` (stale), append leftovers from `[...selectedIds]` after the ordered ones so the POST still includes every selected id.
   - `setLandBusy(true)`; `setLandError(null)`; `setLandResults(null)`; clear toast optional.
   - `POST` via existing `api()` helper:

     ```ts
     const r = await api("/api/admin/inbox/land-meteorite", {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify({ message_ids: ids }),
     })
     ```

   - Parse JSON as `LandMeteoriteResponse`.
   - If `!r.ok`: set `landError` from `data.error` or `HTTP ${r.status}`; optional error toast; do **not** clear selection.
   - If `r.ok`: `setLandResults(Array.isArray(data.results) ? data.results : [])`; `clearSelection()`; optional success toast with totals (`total_passed` / `total_skipped` / `total_failed` / `total_errors` when present) — toast is summary only; the results panel is the AC6 surface.
   - After `r.ok`, reload the inbox list with the same fetch pattern as the mount `useEffect` (extract a `loadMessages` async function used by mount + post-land) so archived rows disappear.
   - `finally`: `setLandBusy(false)`.

4. Wire toolbar **Land Meteorite** `onClick={onLandMeteorite}` and `disabled={!landEnabled}` where `landEnabled = selectedIds.size > 0 && !landBusy`. While busy, button label may stay `Land Meteorite` (disabled) — do not invent a spinner requirement.

5. Below the toolbar (still above the table), render batch feedback when `landError` or `landResults`:

   - If `landError`: a paragraph with `color: var(--danger)` showing the error string.
   - If `landResults`: a compact results block titled `Land Meteorite results` listing one line/row per result:

     - Resolve subject: `messages.find(m => m.id === row.message_id)?.subject` **or** keep a snapshot map built just before POST from the then-current `messages` if the reload clears subjects — **Decision below** requires a pre-POST snapshot.
     - Show: subject (or message_id fallback), `outcome` string exactly as returned, and `astral_candidate_id` when non-null.
     - Presentation class helper (local function, not config):

       ```ts
       function outcomeKind(outcome: string): "skip" | "fail" | "ok" {
         const o = (outcome || "").trim()
         if (o.startsWith("skipped-") || o === "skipped-other-candidate") return "skip"
         if (o === "error" || o === "failed") return "fail"
         return "ok"
       }
       ```

       Map kind → CSS class (`manage-email-outcome--skip` / `--fail` / `--ok`). Do **not** invent ingest eligibility; this is display-only bucketing of server outcome strings.

⚠️ **Decision — snapshot subjects at POST time:** After a successful land, inbox reload may drop archived messages. Build `const subjectById = Object.fromEntries(messages.map(m => [m.id, m.subject]))` (or a `Map`) immediately before `fetch`/`api` and use it when rendering `landResults` so Archie still sees which selected subjects landed/skipped/failed.

⚠️ **Decision — show raw `outcome` strings from AST-1141/1140:** Skip vocabulary (`skipped-unbound`, `skipped-not-in-inbox`, `skipped-unmatched`) and bound outcomes (`archived`, `ignored`, `ignored-empty`, `error`, …) stay server-authored. React must not remap them to Create-era “Created job …” copy.

6. **Retire Create** in the same stage (same commit):

   - Delete `createBusyId` state, `onCreateClick`, and the entire Actions column cell that renders the Create button (matched-only Create).
   - Remove the **Actions** column header and body cells; drop Actions from the table entirely (checkbox + Subject + From + Candidate + Date + Status).
   - Update empty-state `colSpan` to `6` (checkbox + 5 data columns).
   - Delete unused `MouseEvent` import if nothing else needs it.
   - In `App.css`, **delete** `.manage-email-create` and `.manage-email-create:disabled`.
   - Add `.manage-email-results` / `.manage-email-outcome--ok|skip|fail` minimal styles (muted / warning / danger text colors using existing CSS variables where present).

7. Do **not**:

   - Call `/api/admin/inbox/messages/<id>/create-job` from this page.
   - Delete or edit `src/ui/api/api_inbox.py` create-job / land-meteorite routes (API leftover create-job is out of scope; Land Meteorite already exists from AST-1141).
   - Edit `src/core/**`, NAV_CONFIG, or routes.
   - Add React debug logging.
   - Filter selectable rows by `candidate_match` (unbound selected rows are valid; API returns skip outcomes).

**Done when (recheck):**

- Empty selection → Land Meteorite disabled; no POST.
- Non-empty selection → POST body `message_ids` matches selection; `200` shows a per-id results list with outcomes including at least one skip string when an unbound id was selected; page stays on Manage Email.
- Matched-row **Create** button is gone; no `manage-email-create` class in CSS; no `create-job` string in `AdminManageEmail.tsx`.
- `npm`/Vite typecheck path the repo already uses for frontend still accepts the page (or `tsc --noEmit` if that is the local habit — do not add a new toolchain).

---

## Self-Assessment

**Scope:** `Single-Component` — Manage Email React page + small CSS; consumes AST-1141 API only.

**Conf:** `high` — API contract is on `ftr`; page already lists inbox via `api()`; checkbox multi-select pattern exists on `JobsSkipped`; Create retirement is delete of known UI.

**Risk:** `Medium` — wrong POST wiring or leaving Create active would regress parent AC3/AC4/AC8; mitigated by literal endpoint path, enablement gate, and explicit Create deletion checklist.

---

## Code Rules check

- **§3.2 / `astral.layers.ui-config-driven-business-logic`:** Ingest/skip/create decisions stay server-side; React only selects ids, posts them, and renders returned `outcome` strings. No hardcoded candidate-state or bind rules in the page.
- **`pattern.ui.admin-endpoint`:** Calls existing authenticated admin mutator; no new Flask route on this ticket.
- **`astral.standards.in-scope-only`:** Selection chrome + Land Meteorite + Create retirement only; no Manage Email redesign, no core/API edits.
- **`astral.ui.frontend-file-placement` / naming:** Edit stays in `pages/AdminManageEmail.tsx`; route `admin/manage_email` unchanged.
- **§3.3:** Frontend → `api()` only; no direct core/data/external imports.
- **§1.5.1 debug:** No React debug requirements (parent AC9 is backend).

---

## Review

**Publish ref:** `origin/sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create`
**Tip:** `2ee72f4b` (code); docs stub follows on publish-ref

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `1756919c` | multi-select chrome + Land Meteorite enablement |
| 2 | `2ee72f4b` | Land Meteorite POST + outcome panel; retire Create |

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Overall:** DISCUSS (no fix-now on Manage Email UI; C4 dependency-merge stragglers)

**What’s solid**
- Multi-select + Select all / Clear / Land Meteorite enablement; checkbox cell stops row-open.
- POST `/api/admin/inbox/land-meteorite` with ordered ids + leftovers; subject snapshot; results panel with raw outcomes; Create retired (handler/column/CSS gone); no `create-job` on the page.
- AST-1142 `code()` = `AdminManageEmail.tsx` + `App.css` only.

**Issues / Recommended**
- **discuss (C4 stragglers):** Tip includes AST-1140/1141 + Betty tests/bible via dependency/`merge-tests`; Joan-excluded statutes in-scope on three-dot tip all scored **conforms** (see Linear). No product rewrite for this UI.
- **advisory (matches Joan):** `outcomeKind` display bucketing of server outcome strings is plan-documented; not eligibility logic.

Full `## Statutes checked` (65/65) lives in the Linear Review Posted comment.

---

## Resolution

**Date:** 2026-08-02  
**Review tip intake:** `e70e804e` (`docs(AST-1142): Radia review — findings`)

| Finding | Disposition |
|---------|-------------|
| fix-now | none — no product change |
| discuss (C4 stragglers) | accepted as scored **conforms**; no rewrite for this UI child |
| advisory (`outcomeKind` display bucketing) | leave as plan-documented display-only CSS; not eligibility |

**Commit:** `resolve(AST-1142): — clean`
