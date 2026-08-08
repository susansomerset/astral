<!-- linear-archive: AST-1098 archived 2026-08-07 -->

## Linear archive (AST-1098)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1098/seed-gaze-email-click-statute-seed-auto-false-gnarly-looking-deploy  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1093 — Gnarly looking deploy logs on railway  
**Blocked by / blocks / related:** parent: AST-1093

### Description

## What this implements

Owns config + provision/reconcile so the shared `gaze_email` row seeds and stays CLICK; creates canon statute `astral.dispatch.seed-auto-false` (seeded dispatch tasks always auto=false); no in-scope seed path writes Auto true. Does **not** own Gmail scopes, Railway log severity, or meteorite runner logic. Observable: local/staging boot no longer auto-dispatches `gaze_email`; Dispatcher shows AUTO off until flipped; statute file present under `canon/statutes/`.

## In scope

- [X] `pattern.config.config-block` — `GAZE_EMAIL_CONFIG.auto_mode` seed CLICK
- [X] `astral.config.config-source-of-truth` — seed default lives in config; ensure reads it
- [X] `astral.standards.no-hardcoded-sets` — desired AUTO posture from config (+ seed-law reconcile to match)
- [X] `astral.standards.in-scope-only` — config + ensure reconcile + statute only
- [X] `astral.dispatch.seed-auto-false` — new statute (this ticket lands it)
- [X] `astral.layers.import-direction` — core→data update path only; no new cross-layer edges
- [X] `astral.docs.features-single-file-per-ticket` — one plan file under `docs/features/foundation/`

## Considered but excluded

- [X] `astral.config.secrets-and-env-specific-from-environ` — no secrets/env posture change
- [X] `astral.layers.core-vs-external-bright-line` — no Gmail/external I/O on this child
- [X] `astral.standards.debug-contract-gated` — no Style D / runner path changes
- [X] `astral.ui.*` / `astral.patterns.require-auth-on-protected-endpoints` — no UI
- [X] Gmail `invalid_scope` remint / Railway stderr severity / oauth2client+Stytch quieting — parent Boundaries
- [X] Ruth parse / meteorite create / Manage Email UI — parent Boundaries
- [X] Rewrite every historical `dispatch_task` AUTO row — Boundaries (shared `gaze_email` reconcile only)

## Acceptance criteria

- [X] 1. Fresh provision of the null-candidate `gaze_email` `dispatch_task` row has AUTO off (CLICK).
- [X] 2. Config seed for that row defaults `auto_mode` false (no seed path writes Auto true for it).
- [X] 3. On an environment that already has that row stuck AUTO-on from the bad seed, after boot/provision reconcile the row is CLICK and the scheduler does not claim `gaze_email` every tick until Susan turns AUTO on.
- [X] 4. No other product seed/provision path introduced or left by this epic inserts new `dispatch_task` rows with Auto true.
- [X] 5. Canon contains active statute `astral.dispatch.seed-auto-false` stating seeded dispatch tasks are always auto=false; HARVEST/README updated per statute authoring norms used in-repo.
- [X] 6. Susan can still flip AUTO on in Task Dispatcher and Run still works in CLICK.

## Boundaries

* Does **not** own Gmail scopes, Railway log severity, or meteorite runner logic.
* Does **not** strip admin ability to set AUTO = true after seed.
* Does **not** rewrite every historical dispatch row beyond the shared `gaze_email` seed reconcile.

## Notes for planning

Parent law: never seed Auto=true. Statute + live `gaze_email` row must ship together.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1093-gnarly-looking-deploy-logs-on-railway`, child `sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-31T04:50:27.584Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log.sh` failed on `origin/sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false`:
- offending: `0f2c4f39 Merge remote-tracking branch 'origin/dev' into sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false`

@Ada Lovelace — rewrite/republish this child `sub/*` without `Merge remote-tracking branch` (merge `origin/ftr/AST-1093-gnarly-looking-deploy-logs-on-railway` / `origin/dev` with proper `merge(AST-1098):` subjects only). Keep plan/code/merge-tests/test/docs/resolve sequence for AST-1098. Push `origin/sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false`.

— Chuckles

#### radia — 2026-07-31T04:45:20.551Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1098
**Publish ref:** `origin/sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false` tip `d89d079369404084a54050e24cdc2f7f2b07ac3f` (product tip reviewed `22304612`; docs() `d89d0793`)
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1098): origin/tests b93e7c34…` on sub |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/docs/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Published to origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1093/AST-1098-…` under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | ftr already aligned |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in history |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named epic branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1093 |
| orch.git.three-permanent-branches | universal | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Boot-reconcile tradeoff documented |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match Files Changed |
| orch.pipeline.project-scoped-queues | universal | conforms | Foundation child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | New statute has approved_by Archie / approved_at |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible via Betty test + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Role path bans respected |
| astral.agent.confidence-bounds | scoped | conforms | No graded-task path |
| astral.agent.do-task-delegation | scoped | conforms | No do_task changes |
| astral.agent.grade-vector-validation | scoped | conforms | No grading path |
| astral.batch.batch-id-first | scoped | conforms | No claim/batch signature changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id generation changes |
| astral.batch.claim-process-release | scoped | conforms | get_due_tasks / claim path untouched |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data RESPONSE work |
| astral.config.config-source-of-truth | scoped | conforms | auto_mode default in GAZE_EMAIL_CONFIG; ensure reads it |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring/dispatch floor changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env posture change |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths {artifacts/**,scripts/spikes/**} no match |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan docs, not spike findings |
| astral.dispatch.seed-auto-false | scoped | conforms | Seed/reconcile leave auto_mode false; statute matches code |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One foundation plan file for AST-1098 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No Gmail/external I/O on this child |
| astral.layers.import-direction | scoped | conforms | core→data update_dispatch_task already established |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers {scripts} ∩ diff empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Seed bool only; no React rules |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult path |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers {ui} ∩ diff empty |
| astral.standards.data-raises-caller-logs | scoped | conforms | Uses existing update_dispatch_task |
| astral.standards.database-header-inventory | scoped | not-applicable | layers {data} ∩ diff empty |
| astral.standards.debug-contract-gated | scoped | conforms | No Style D / debug runner changes |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses ensure_gaze_email + update_dispatch_task |
| astral.standards.in-scope-only | scoped | conforms | Config + ensure reconcile + statute only |
| astral.standards.logging-via-utils | scoped | conforms | No new logging surface |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in utils/core/canon |
| astral.standards.no-hardcoded-sets | scoped | conforms | Seed posture from config; catalog asserts |
| astral.standards.public-then-helpers | scoped | conforms | Extend existing ensure return shape |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data import introduced |
| astral.state.core-decides-transitions | scoped | conforms | No entity state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No run_next / chain changes |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers {ui} ∩ diff empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers {ui} ∩ diff empty |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker changes |

## Pattern conformance

- `pattern.config.config-block` — **conforms** (`GAZE_EMAIL_CONFIG.auto_mode` seed CLICK)
- Active `astral.patterns.*` — covered via statutes table

## Plan adherence

Self-Assessment Scope `Single-Component` matches config + ensure reconcile + statute footprint. Stages 1–3 delivered. AC1–6 covered (fresh CLICK seed, config false, boot reconcile, catalog asserts, statute+register, admin AUTO/Run untouched).

## Findings

**discuss (straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; tip three-dot includes `docs/features/**` + Betty test-tree so sweep scores them in-scope (all still **conforms**). Joan artifact present.

**advisory:** Boot-reconcile clears operator AUTO on shared `gaze_email` each ensure (Joan discuss / plan Decision). Provision INFO log omits `reconciled=` though return shape includes it.

### What’s solid

`auto_mode: False` + asserts; ensure insert from config + AUTO→CLICK reconcile; statute with Archie approval; README/HARVEST 57.

### Recommended actions

None for fix-now.

context_tokens≈42000

#### betty — 2026-07-31T04:40:57.926Z
## QA test manifest — AST-1098

**Publish tip:** `origin/sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false` @ `22304612`
**Delivery:** `merge-tests(AST-1098): origin/tests b93e7c34a00032d8f7ca2ba63bcc66346db50475`

### Run (epic worktree on publish tip)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1098GazeEmailSeedClick \
  tests/component/utils/test_config.py::TestAst1088GazeEmailConfig \
  tests/component/core/test_dispatcher.py::TestAst1098GazeEmailReconcile \
  tests/component/core/test_dispatcher.py::TestAst1088GazeEmailDispatchProvision \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1088NullCandidateGazeEmail \
  -q
```

### Manifest

1. **Config seed CLICK + catalog locks + statute register** — `TestAst1098GazeEmailSeedClick` (`auto_mode is False`; meteorite + candidate-stage catalogs falsy; statute file + README/HARVEST).
2. **Revised shell config** — `TestAst1088GazeEmailConfig` now expects `auto_mode is False` (seed law).
3. **Ensure reconcile AUTO→CLICK** — `TestAst1098GazeEmailReconcile` (`reconciled: 1` + `update_dispatch_task`; already-CLICK → `skipped: 1`).
4. **Revised provision** — `TestAst1088GazeEmailDispatchProvision` insert uses `auto_mode is False`; return shape includes `reconciled`.
5. **Revised null-candidate save** — `TestAst1088NullCandidateGazeEmail::test_save_null_candidate_for_gaze_email` expects `auto_mode == 0` when reading config.

### Broken / obsolete (revised this pass)

- AST-1088 `auto_mode is True` / `auto_mode == 1` asserts on gaze_email seed path.

### Integration

none

### Bible shasums (on publish tip)

- `docs/test-bible/utils/config.md` — `ff93cf14ad423023584a5dfa73dbb6611136fef669ba9cc387e22d974951dc79`
- `docs/test-bible/core/dispatcher.md` — `52fbb5674b9ecd1eebcb9b78e84ecdb2aaf65a7972ac87464021bb34c7b408db`
- `docs/test-bible/data/database/dispatch_tasks.md` — `68ea4fa7ca2bf6426eaeed5f6bd2a8831c9d7ff89a8f6c380fa882179d42d168`

#### chuckles — 2026-07-31T04:33:05.511Z
[thread-orphan] Joan session store relocated for epic workspace hash.

found: `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`
expected: `/home/susan/.cursor/chats/72c3fb4765b5d4b9b58c017950919863/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`
UUID unchanged: `da0027e7-276d-4fe2-a6e6-65c8eb77e24d`

— Chuckles

#### joan — 2026-07-31T04:32:32.901Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1098
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Fresh null-candidate gaze_email provision is CLICK | Stage 1 config False + Stage 2 insert uses `GAZE_EMAIL_CONFIG["auto_mode"]` |
| AC2 Config seed defaults auto_mode false | Stage 1 flip + assert |
| AC3 Stuck AUTO-on shared row reconciles to CLICK at boot | Stage 2 `update_dispatch_task(..., auto_mode=False)` + return `reconciled` |
| AC4 No other product seed path inserts Auto true | Stage 1 Decision: sole True flip + meteorite/stage asserts; admin create out of seed |
| AC5 Canon statute + README/HARVEST | Stage 3 `astral.dispatch.seed-auto-false` + register |
| AC6 Susan can flip AUTO / Run in CLICK | Stage 2 Decision: no admin/PATCH/Run removal; out of code changes beyond not stripping |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 Config seed CLICK | Purpose seed law; Functional scope gaze_email fix; AC2/AC4 |
| Stage 2 Provision reconcile | Functional scope already-provisioned rows; AC1/AC3 |
| Stage 3 Canon statute | Purpose lasting statute; Architectural new statute; AC5 |

**Notes:** Files Changed layer `docs/canon` mapped → `docs` for matching.

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Stage commits via build-child vocabulary on sub ref |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1093/AST-1098-… only |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1093 worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; block→parent on drift |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child Foundation scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate gate |
| orch.roles.archie-approves-statutes | conforms | New statute lands with Archie approved_by/at per parent |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded-task / confidence path touched |
| astral.agent.do-task-delegation | conforms | No do_task / agent_task changes |
| astral.agent.grade-vector-validation | conforms | No grading path |
| astral.batch.batch-id-first | conforms | No claim/batch signature changes |
| astral.batch.batch-id-format | conforms | No batch_id generation changes |
| astral.batch.claim-process-release | conforms | get_due_tasks / claim path untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE work |
| astral.config.config-source-of-truth | conforms | auto_mode default in GAZE_EMAIL_CONFIG; ensure reads it |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring/dispatch floor changes |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env posture change |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src + features; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | No Gmail/external I/O; core→data update only |
| astral.layers.import-direction | conforms | core→data update_dispatch_task already established |
| astral.layers.ui-config-driven-business-logic | conforms | Config touch is seed bool, not UI visibility rules |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult path |
| astral.standards.data-raises-caller-logs | conforms | Uses existing update_dispatch_task; no new data log path |
| astral.standards.debug-contract-gated | conforms | No Style D / debug runner changes |
| astral.standards.dry-and-focused-functions | conforms | Reuses ensure_gaze_email + update_dispatch_task |
| astral.standards.in-scope-only | conforms | Config + ensure reconcile + statute only; Boundaries held |
| astral.standards.logging-via-utils | conforms | No new logging surface |
| astral.standards.no-cross-contamination | conforms | Stays in utils/core/canon |
| astral.standards.no-hardcoded-sets | conforms | Seed posture from config; reconcile False matches asserted config |
| astral.standards.public-then-helpers | conforms | Extend existing ensure return shape; no scatter |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import introduced |
| astral.state.core-decides-transitions | conforms | No entity state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No run_next / chain changes |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — paths match none of plan paths (plan doc not in Files Changed)
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan empty
- astral.standards.database-header-inventory — layers ∩ plan empty
- astral.ui.frontend-file-placement — layers ∩ plan empty
- astral.ui.naming-conventions — layers ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Stage 2 re-CLICK on every ensure means operator AUTO on the shared `gaze_email` row does not survive the next boot. Parent Functional scope allows an idempotent “seed wants CLICK” reconcile and child AC3 requires boot fix for bad-seed AUTO; plan Decision + Medium risk document the tradeoff. Sticky “Susan toggled” would need a new pattern — out of Boundaries.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium is honest; AC4 via asserts (not a global scanner) matches epic Boundaries.

**R6:** Definition fidelity pass. Layer/import pass. Config source-of-truth pass. No UI/batch/state-machine creep. Statute AUTHORING shape with Archie approval present.

context_tokens≈48000

— Joan

#### ada — 2026-07-31T04:30:12.502Z
**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false/docs/features/foundation/ast-1098-seed-gaze-email-click-statute-seed-auto-false.md

**Tip:** `1184a8e2` on `origin/sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false`

**Self-assessment**
- **Scope:** `Single-Component` — config seed flip, ensure reconcile for the shared null-candidate row, + statute/README/HARVEST register.
- **Conf:** `high` — sole `auto_mode: True` seed is `GAZE_EMAIL_CONFIG`; `update_dispatch_task` already whitelists `auto_mode`; Archie named `astral.dispatch.seed-auto-false`.
- **Risk:** `Medium` — provision always re-CLICK-s the shared row (operator AUTO lasts until next boot); corpus register miss would leave Joan/Radia incomplete.

---

# Seed gaze_email CLICK + statute seed-auto-false

**Linear:** [AST-1098](https://linear.app/astralcareermatch/issue/AST-1098/seed-gaze-email-click-statute-seed-auto-false-gnarly-looking-deploy)  
**Parent:** [AST-1093](https://linear.app/astralcareermatch/issue/AST-1093) — Gnarly looking deploy logs on railway  
**Publish ref:** `sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false`

Correct the AST-1088 seed that set the shared null-candidate `gaze_email` `dispatch_task` to AUTO-on (every-tick scheduler claim → Gmail `invalid_scope` log spam). Config + provision seed CLICK; boot reconcile flips an already-stuck AUTO shared row back to CLICK; land Archie-approved canon statute `astral.dispatch.seed-auto-false`. Does not own Gmail scopes, Railway severity cosmetics, or meteorite/gaze runner logic.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `GAZE_EMAIL_CONFIG["auto_mode"]` → `False`; assert False; assert other in-tree seed catalogs stay False | utils |
| `src/core/dispatcher.py` | `ensure_gaze_email_dispatch_task`: on existing shared row with AUTO on, `update_dispatch_task(..., auto_mode=False)`; return `reconciled` | core |
| `canon/statutes/astral/dispatch/astral.dispatch.seed-auto-false.md` | New active scoped statute (SCHEMA + AUTHORING) | docs/canon |
| `canon/statutes/README.md` | Add statute to harvested corpus table; bump active count | docs/canon |
| `canon/statutes/HARVEST.md` | Add crosswalk row for the new statute; bump counts | docs/canon |

## Stage 1: Config seed CLICK

**Done when:** `GAZE_EMAIL_CONFIG["auto_mode"]` is `False` with a module assert; the only former `True` product seed for dispatch AUTO in `config.py` is corrected; meteorite + candidate-stage seed catalogs remain `False` (asserted).

1. In `src/utils/config.py`, in `GAZE_EMAIL_CONFIG`, change `"auto_mode": True` to `"auto_mode": False`. Update the nearby comment so it states seed is CLICK (AST-1098 / parent seed law), not AUTO.
2. Immediately after the existing `GAZE_EMAIL_CONFIG` asserts, add:
   - `assert GAZE_EMAIL_CONFIG["auto_mode"] is False`
3. Immediately after that (same stage), add asserts that every entry in `METEORITE_DISPATCH_TASKS` has `auto_mode` falsy, and every entry in `CANDIDATE_STAGE_DISPATCH.values()` that has an `"auto_mode"` key has it falsy. Do **not** change those catalogs’ values unless an assert fails (on tip they are already `False`).
4. Do **not** change `TASK_CONFIG["gaze_email"]` shape, admin-defaults special-case, Gmail scopes, or runner keys.

⚠️ **Decision:** AC4 is satisfied by (a) flipping the sole `True` seed (`GAZE_EMAIL_CONFIG`) and (b) locking meteorite/stage seed catalogs with asserts — not by inventing a runtime scanner over every `save_dispatch_task` call site. Admin UI create can still accept AUTO when an operator sets it (AC6 / Boundaries).

## Stage 2: Provision reconcile shared gaze_email → CLICK

**Done when:** Fresh insert of the null-candidate `gaze_email` row uses `GAZE_EMAIL_CONFIG["auto_mode"]` (False). If that shared row already exists with AUTO on, `ensure_gaze_email_dispatch_task` (via `provision_gaze_email_dispatch_task` / `start_scheduler`) forces `auto_mode=False` through `database.update_dispatch_task` and reports `reconciled: 1`. No other `dispatch_task` rows are rewritten.

1. In `src/core/dispatcher.py`, in `ensure_gaze_email_dispatch_task`, when the shared null-candidate row for `GAZE_EMAIL_CONFIG["task_key"]` is found:
   - If `bool(existing.get("auto_mode"))` is true: call `database.update_dispatch_task(int(existing["id"]), auto_mode=False)` (use the same `database` import style already used for `save_dispatch_task` in this function).
   - Return dict shape extended with `"reconciled": 1` (and keep `added: 0`, `skipped: 1` or set `skipped: 0` — pick one consistent convention: **`added: 0`, `skipped: 0`, `reconciled: 1`, `skipped_missing_config: 0`, `id`: existing id** when a flip occurred; when already CLICK: **`added: 0`, `skipped: 1`, `reconciled: 0`, …**).
   - When inserting a new row, keep `auto_mode=bool(GAZE_EMAIL_CONFIG["auto_mode"])` and include `"reconciled": 0` on the success return.
   - When `skipped_missing_config`, include `"reconciled": 0`.
2. Do **not** change `get_due_tasks`, `_dispatch_one`, `run_gaze_email`, admin PATCH semantics, or meteorite/stage ensure loops.
3. Do **not** reconcile any candidate-scoped `gaze_email` rows (there should be none for this task); match only `task_key == tk` and null/blank `candidate_id` as today.

⚠️ **Decision:** Reconcile runs on every ensure/provision for this **shared** row only. That clears bad-seed AUTO at boot (AC3). Operator AUTO after boot lasts until the next provision/boot; no sticky “Susan toggled” flag (Boundaries: do not rewrite every historical row; no new pattern). AC6 (flip AUTO + Run in CLICK) remains admin/UI + existing dispatch paths — out of this ticket’s code changes beyond not removing those capabilities.

## Stage 3: Canon statute `astral.dispatch.seed-auto-false`

**Done when:** Active statute file exists at the SCHEMA path; README harvested table + HARVEST crosswalk list it; id is `astral.dispatch.seed-auto-false`.

1. Create directory `canon/statutes/astral/dispatch/` if missing.
2. Create `canon/statutes/astral/dispatch/astral.dispatch.seed-auto-false.md` with YAML frontmatter (all SCHEMA keys, no extras):

```yaml
---
id: astral.dispatch.seed-auto-false
title: Seeded dispatch tasks are auto=false
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "utils"]
  paths: ["src/core/dispatcher.py", "src/utils/config.py"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/foundation/ast-1098-seed-gaze-email-click-statute-seed-auto-false.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---
```

3. Body sections in SCHEMA order:

   - `# Statement` — Product seed/provision paths that insert or reconcile `dispatch_task` rows must leave `auto_mode` false (CLICK). Operators may turn AUTO on later via Task Dispatcher; seed paths must not write Auto true.
   - `## Rationale` — AUTO-true seeds (e.g. shared `gaze_email`) cause every-tick scheduler claims; failures then drown deploy logs. Seed law is CLICK; AUTO is an operator choice after seed.
   - `## Examples` / `### Conforming` — `GAZE_EMAIL_CONFIG["auto_mode"]` false; `ensure_gaze_email_dispatch_task` inserts/reconciles CLICK; meteorite/stage seed catalogs seed false.
   - `### Violating` — Config or ensure path inserts a new `dispatch_task` with `auto_mode` true; provision skips correcting a shared bad-seed AUTO-on `gaze_email` row.
   - Optional `## Notes` — Admin create/PATCH may still set AUTO true after seed (not a seed path). Does not require rewriting every historical row beyond shared `gaze_email` reconcile. Archie approved id on parent AST-1093 (2026-07-31).

4. In `canon/statutes/README.md`, add a harvested-corpus table row for this statute (alphabetically near other `astral.dispatch.*` / after `astral.debug.*` as fits the existing table order) and bump the active-statute count text from **56** to **57**.
5. In `canon/statutes/HARVEST.md`, add one crosswalk row, e.g. `| create (AST-1098) | \`astral.dispatch.seed-auto-false\` | scoped | judgment | AST-1093 / AST-1098 | \`astral/dispatch/astral.dispatch.seed-auto-false.md\` |`, and update the **Counts** line to include this create (56→57 active mappings).

⚠️ **Decision:** Domain folder is `dispatch` (new under `astral/`) — matches id `astral.dispatch.seed-auto-false` per AUTHORING. `approved_by: Archie` / `approved_at: 2026-07-31` per parent Architectural definition (Archie approved via comment 2026-07-31) and AUTHORING lifecycle.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1093 with the Stage N blocked template.
- Leave Gmail scopes, Railway log severity, `gaze_email` runner, Ruth parse, and Manage Email UI untouched.

## Self-Assessment

**Scope:** `Single-Component` — config seed literal + one ensure reconcile path + one new statute (+ README/HARVEST register). No schema migration, no UI, no Gmail/external.

**Conf:** `high` — flip known `True` seed; `update_dispatch_task` already whitelists `auto_mode`; statute shape copies SCHEMA exemplars; Archie already named the id.

**Risk:** `Medium` — wrong reconcile could fight operator AUTO across every boot for this shared row (documented Decision); forgetting README/HARVEST register leaves Joan/Radia corpus incomplete; touching other provision loops would expand epic Boundaries.

## Self-review vs ASTRAL_CODE_RULES

- **§2.1 / config-source-of-truth / pattern.config.config-block:** `auto_mode` default stays in `GAZE_EMAIL_CONFIG`; ensure reads config.
- **§1.4 / no-hardcoded-sets:** Desired CLICK comes from config bool, not a stray `False` literal beside an unrelated key (insert still uses `bool(GAZE_EMAIL_CONFIG["auto_mode"])`; reconcile writes `False` only to enforce seed law matching config — acceptable because config assert requires False).
- **§3.3 imports:** core→data for `update_dispatch_task` already established; no new layer violations.
- **in-scope-only:** No Gmail remint, no Railway severity, no runner/Ruth/UI redesign.
- **Statute AUTHORING:** active + Archie approved; no draft status in-repo.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false`
**Tip:** `927ce685`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `c9ed3be6` | GAZE_EMAIL_CONFIG seed auto_mode CLICK |
| 2 | `93538a82` | reconcile shared gaze_email AUTO to CLICK |
| 3 | `927ce685` | statute astral.dispatch.seed-auto-false + register |

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1098
**Publish ref tip (at review):** `2230461251bf6e1991a3b57254c15f6012ddec85`
**Overall:** CLEAN

### What’s solid

- Stages 1–3 match plan: `GAZE_EMAIL_CONFIG["auto_mode"]=False` + seed catalog asserts; ensure insert from config + reconcile stuck AUTO→CLICK; statute `astral.dispatch.seed-auto-false` with Archie approval + README/HARVEST 57.
- Betty `test` + one `merge-tests(AST-1098)` SHA on the sub.

### Issues

**discuss (straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; tip three-dot includes `docs/features/**` + Betty test-tree so sweep scores them in-scope (all still **conforms**).

**advisory:** Joan’s boot-reconcile tradeoff (operator AUTO on shared `gaze_email` does not survive next ensure) is intentional per plan Decision. Provision INFO log still omits `reconciled=` (return shape has it).

### Recommended actions

None for fix-now.

### Statutes checked (summary)

57 active statutes swept vs `origin/dev...origin/sub/AST-1093/AST-1098-…`. No violates. Full table in Linear review comment.

## Resolution

**Date:** 2026-07-31  
**Publish tip before resolve:** `d89d0793` (`docs(AST-1098): Radia review — CLEAN with Joan straggler discuss`)

Radia overall **CLEAN** — no fix-now product or plan-doc edits.

| Finding | Disposition |
|---------|-------------|
| discuss (Joan Excluded stragglers on three-dot tip) | Accepted as non-blocking; statutes still **conforms**; no product change |
| advisory (boot-reconcile clears operator AUTO; provision INFO omits `reconciled=`) | Accepted — boot-reconcile matches plan Decision / AC3; log field optional, not fix-now |

No product commits on this resolve pass. Merge of `origin/dev` kept Betty AST-1098 test tip (engineer hook excludes foreign test-tree paths from the merge commit).
