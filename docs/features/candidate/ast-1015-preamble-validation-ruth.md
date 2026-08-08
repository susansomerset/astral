<!-- linear-archive: AST-1015 archived 2026-08-07 -->

## Linear archive (AST-1015)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1015/preamble-valid-try-again-escalate-via-ruth-candidate-profile-preamble  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-952 — Candidate Profile Preamble to Intake  
**Blocked by / blocks / related:** parent: AST-952; blocks: AST-1017

### Description

## What this implements

New **agent_task** only, using **Ruth (Little Brain)**: “Does this response look like a valid answer to this question?” → Valid / Try Again / Escalate. Callable for every preamble intake answer.

## Acceptance criteria

- [X] 2. Ruth agent_task validation returns Valid / Try Again / Escalate; Try Again does not advance; Escalate ≠ Valid; no new agent persona shipped.
- [X] 3. Touched backend `debug=True` validation/write paths emit per-step found/recorded debug lines per the contract above.

## Boundaries

- [X] Does **not** own the data library (AST-1014), PREAMBLE_CONFIG (#3), or intake UI (#4). No new agents or agent patterns — Ruth + one new agent_task only.

## Notes for planning

After AST-1014. Config-driven task key (§2.1).

## Git branch (authoritative)

`sub/AST-952/<this-id>-preamble-validation-ruth`. Publish to `origin/<publish-ref>` only.

### Comments

#### chuckles — 2026-07-30T01:24:17.536Z
[merge-child] blocked:

`validate-sub-log` fails: `git pull merge on sub` — six `Merge remote-tracking branch` commits appear in `origin/sub/AST-952/AST-1015-preamble-validation-ruth --not origin/ftr/…` but they are already on `origin/dev` (brought in by Hedy’s proper `merge(AST-1015): resolve origin/dev conflicts`). Not a local `git pull` on this sub.

Tried `refresh-ftr AST-952-candidate-profile-preamble-to-intake` to absorb `origin/dev` into ftr so those SHAs leave the validate range — **CONFLICT files:**
- `src/core/candidate.py`
- `src/ui/api/api_admin.py`
- `src/utils/config.py`

`origin/ftr/AST-952-candidate-profile-preamble-to-intake` unchanged @ `e10d0f9c`. Blocker AST-1014 tip also still `NOT_ON_FTR` (one commit: `merge(AST-1014): origin/dev`).

@Hedy Lamarr — resolve refresh-ftr product conflicts on epic worktree / ftr for those three paths (or republish stacking), then Chuckles re-runs merge-child. @Ada Lovelace — roll AST-1014 onto ftr when ready (blockedBy order).

— Chuckles

#### radia — 2026-07-30T01:20:28.040Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1015
**Publish ref:** `sub/AST-952/AST-1015-preamble-validation-ruth` @ `f90fdf6cd78b28f08a102c545a9e1a45fd5b6185` (product tip `7ff0ac90`; docs append `f90fdf6c`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests on tip; follow-up `test(AST-1015)` after qa-handoff (no second merge-tests) |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge/merge-tests/resolve vocab |
| orch.git.flow-direction-inviolable | universal | conforms | Sub tip ahead of origin/dev; no reverse-flow |
| orch.git.ftr-sub-topology | universal | conforms | Child on `sub/AST-952/AST-1015-preamble-validation-ruth` |
| orch.git.merge-on-checkout | universal | conforms | Tip merges origin/dev + ftr before finalize |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | Named sub/ only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-952 |
| orch.git.three-permanent-branches | universal | conforms | No fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Revision 1 closed key-clash without new product ask |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–4 match Revision 1 ship |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Candidate only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute authorship |
| orch.roles.betty-owns-test-tree | universal | conforms | Catalog/bible locks via Betty; engineer code commits exclude tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer code = config/agent_task/intake/api only |
| astral.agent.confidence-bounds | scoped | conforms | Confidence math untouched |
| astral.agent.do-task-delegation | scoped | conforms | Core calls do_task with config task_key |
| astral.agent.grade-vector-validation | scoped | conforms | Not a graded-vector task |
| astral.batch.batch-id-first | scoped | conforms | No claim-signature change |
| astral.batch.batch-id-format | scoped | conforms | `preamble-{task_key}-{uuid}` ledger ids |
| astral.batch.claim-process-release | scoped | conforms | On-demand ledger; no entity claim batch |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Relies on existing do_task storage |
| astral.config.config-source-of-truth | scoped | conforms | task_key + outcomes in PREAMBLE_VALIDATION_CONFIG; asserted == PREAMBLE_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | Literals only |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths artifacts/** / scripts/spikes/** miss diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under docs/features/; not a spike dump |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan file ast-1015-…md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits exclude src/features product |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer code commits have no tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | External only via do_task |
| astral.layers.import-direction | scoped | conforms | ui→core; core→do_task/utils/data |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths scripts miss diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Thin API; no React rules |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `@require_auth` on POST preamble/validate |
| astral.standards.database-header-inventory | scoped | conforms | Header intact on ancestor data touch |
| astral.standards.data-raises-caller-logs | scoped | conforms | Core raises ValueError; API maps 400/404 |
| astral.standards.debug-contract-gated | scoped | conforms | Style-D only when debug=True; truncate Q/A |
| astral.standards.dry-and-focused-functions | scoped | conforms | One epic task_key; ledger mirrors intake pattern |
| astral.standards.in-scope-only | scoped | conforms | AST-1015 delta = validation only (no UI/PREAMBLE_CONFIG ownership) |
| astral.standards.logging-via-utils | scoped | conforms | get_logger / truncate_debug_content |
| astral.standards.no-cross-contamination | scoped | conforms | Layered paths + repo admin JSON |
| astral.standards.no-hardcoded-sets | scoped | conforms | Outcomes from PREAMBLE_VALIDATION_CONFIG |
| astral.standards.public-then-helpers | scoped | conforms | Public validate_preamble_answer before private helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data |
| astral.state.core-decides-transitions | scoped | conforms | No candidate transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No daisy-chain |
| astral.ui.frontend-file-placement | scoped | conforms | AST-1015 code does not edit frontend |
| astral.ui.naming-conventions | scoped | conforms | snake_case POST …/preamble/validate |
| astral.ui.single-gunicorn-worker | scoped | conforms | Worker count untouched |

## Pattern conformance

none cited

## Plan adherence

Revision 1 bible matched: `preamble_validate_response` everywhere (callable name stays `validate_preamble_answer`); Ruth-only row; no library writes; unrecognized outcome ≠ Valid; debug gated; thin authenticated API. Self-Assessment Single-Component / high / Medium still fits. Sibling AST-1016 key contract asserted at import.

## Findings

### discuss
1. **C4 stragglers** — Joan excluded at plan time, in-scope on three-dot tip (ancestor AST-1014/1016 + tests/frontend): `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.standards.database-header-inventory`, `astral.ui.frontend-file-placement`. All **conform**; topology-only — no AST-1015 product fix.

## What’s solid

Closed three-outcome parse, no coerce-to-Valid, no save_candidate_data, Ruth `college_intern_ruth` only, catalog/fixture locked after qa-handoff.

## Recommended actions

No fix-now. Engineer may proceed via resolve-child / User Testing.

## Notes

Joan plan-rubric APPROVED (post Plan Discuss Revision 1). Docs append @ `f90fdf6c`.

context_tokens≈78000

#### betty — 2026-07-30T01:12:19.836Z
[check-linear]

Cleared `[qa-handoff]`: AST-786 catalog locks now expect **42** keys including `preamble_validate_response` (tip product after `merge origin/dev`).

- Publish tip: `origin/sub/AST-952/AST-1015-preamble-validation-ruth` @ `7ff0ac90` (`test(AST-1015): AST-786 catalog 42 includes preamble row`) — no second `merge-tests` (one already on tip).
- Bible: `agent_tasks.md` / `repo_admin_json.md` updated for 42-row catalog.
- Manifest: AST-786 count **41→42**; stay Tests Ready; Hedy for `test-child`.

Bible shasums @ tip:
- `docs/test-bible/data/database/agent_tasks.md` `989459c087fed099feb63c6609b913026c578f8f`
- `docs/test-bible/core/repo_admin_json.md` `8bf0682c5151e1c815955c8482a4c8de0832e912`

#### hedy — 2026-07-30T01:05:58.484Z
[qa-handoff]

@Betty White

**Command (Betty manifest):**
```
pytest \
  tests/component/utils/test_config.py::TestAst1015PreambleValidationConfig \
  tests/component/core/test_intake.py::TestAst1015ValidatePreambleAnswer \
  tests/component/ui/api/test_api_intake.py::TestAst1015PreambleValidateRoute \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1015PreambleValidateCatalogRow
```
**Result:** 16 passed, **2 failed** (product AST-1015 items green).

**Failures (test layer):**
- `TestAst786AgentTaskRepoJsonSeed::test_repo_json_has_41_current_catalog_keys` — `assert 42 == 41`
- `…::test_startup_apply_loads_all_41_current_rows` — same

**Why test/manifest, not product:** After mandatory `git merge origin/dev` on the epic worktree, `data/admin/agent_task.json` correctly unions origin/dev’s 41-key catalog (`simple_resume_parse` / `meteorite_like` / `meteorite_upshot` …) **plus** this ticket’s `preamble_validate_response` → **42** current rows. Fixture is byte-identical to tip (`docs/uat-fixtures/AST-756/expected-agent_task.json`).

`AST786_EXPECTED_TASK_KEYS` on the merged tip still omits `preamble_validate_response` on purpose (`Parallel AST-1015 … is not on that base yet`), so the AST-786 count/frozenset lock fails against the combined product. `TestAst1015PreambleValidateCatalogRow` already green for the Ruth row.

**Betty fix:** Update AST-786 expected frozenset/count **41→42** to include `preamble_validate_response` (and any fixture-lock text), republish merge-tests onto `origin/sub/AST-952/AST-1015-preamble-validation-ruth`, reassign Hedy.

**Publish tip (product merge):** `origin/sub/AST-952/AST-1015-preamble-validation-ruth` @ `489c8c56` (`merge(AST-1015): resolve origin/dev conflicts — keep preamble + meteorite catalog`).

Status left **Tests Ready**.

#### betty — 2026-07-28T19:22:40.145Z
## QA test manifest

Publish: `origin/sub/AST-952/AST-1015-preamble-validation-ruth` @ `0807ed95` (`merge-tests(AST-1015): origin/tests 409e7c68`)

1. `tests/component/utils/test_config.py::TestAst1015PreambleValidationConfig` — PREAMBLE_VALIDATION_CONFIG outcomes + TASK_CONFIG + key equality vs PREAMBLE_CONFIG when present
2. `tests/component/core/test_intake.py::TestAst1015ValidatePreambleAnswer` — Valid/Try Again/Escalate; empty answer; unknown ≠ Valid; no library writes; debug found|outcome
3. `tests/component/ui/api/test_api_intake.py::TestAst1015PreambleValidateRoute` — POST `/api/candidates/<id>/preamble/validate` auth/200/404/400/structured failure
4. `tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed` — catalog **39** + fixture byte-identity (revised)
5. `tests/component/core/test_repo_admin_json.py::TestAst1015PreambleValidateCatalogRow` — Ruth `preamble_validate_response` row

Broken / revised: AST-786 expected keys/count 38→39 for new Ruth task.

Bible shasums on publish tip:
- `docs/test-bible/utils/config.md` `33994a843f16553b6825a6999058b17dca52adff`
- `docs/test-bible/core/intake.md` `cbd92688a1b7b347d909fbb1a14036ab8c28f874`
- `docs/test-bible/ui/api/api_intake.md` `a206472f4dee0c59e2b70d9b7b9808c4784e9928`
- `docs/test-bible/data/database/agent_tasks.md` `09f9160bfd355a7c5d0c8da61812bbe0cce9e570`
- `docs/test-bible/core/repo_admin_json.md` `0267f838f16f7cef26faf7b3deb31e3e7476e1fc`

Run on epic worktree after merge-on-checkout of the publish tip.

#### betty — 2026-07-28T19:15:37.140Z
Product bug — holding **Code Complete** (no Tests Ready / no merge-tests).

Stage 2 added `preamble_validate_response` to `data/admin/agent_task.json` (39 current rows on tip) but did **not** sync `docs/uat-fixtures/AST-756/expected-agent_task.json` (still 38 rows, missing that key). Tip bytes diverge → existing catalog locks fail against this publish tip:

1. `TestAst786AgentTaskRepoJsonSeed::test_repo_json_matches_uat_fixture_byte_for_byte`
2. `…::test_repo_json_has_38_current_catalog_keys`
3. `…::test_startup_apply_loads_all_38_current_rows`

**Fix (product):** copy tip `data/admin/agent_task.json` → `docs/uat-fixtures/AST-756/expected-agent_task.json` (or otherwise make them byte-identical) and push `origin/sub/AST-952/AST-1015-preamble-validation-ruth`. After that, Betty revises the AST-786 expected frozenset/count to **39** + `preamble_validate_response`, and adds AST-1015 coverage for config / `validate_preamble_answer` / `POST …/preamble/validate`.

Tip checked: `01d62d5c` / build `3a6444b1`.

— Betty

#### joan — 2026-07-28T19:06:54.125Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1015
**Overall:** APPROVED

**Plan tip:** `origin/sub/AST-952/AST-1015-preamble-validation-ruth` @ `b7283c57` (Revision 1 after Plan Discuss round=1).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 library + columns | N/A — boundary (AST-1014) |
| AC2 Ruth Valid / Try Again / Escalate; Try Again does not advance; Escalate ≠ Valid; no new persona | Stages 1–4; no library writes; Ruth `college_intern_ruth` only |
| AC3 PREAMBLE_CONFIG | N/A — boundary (AST-1016); outcomes stay in `PREAMBLE_VALIDATION_CONFIG`; task_key asserted equal when both present |
| AC4 mechanical UI | N/A — boundary (AST-1017); no React |
| AC5–AC7 | N/A — boundaries / siblings |
| AC8 debug on touched validation paths | Stage 3 `debug=` style-D on `validate_preamble_answer` |

### Child AC → plan stages

| Child AC | Stages |
|----------|--------|
| (parent) AC2 three outcomes; no advance; Escalate ≠ Valid; Ruth only | 1–4 |
| (parent) AC8 debug on validation path | Stage 3 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| 1 `PREAMBLE_VALIDATION_CONFIG` + `TASK_CONFIG["preamble_validate_response"]` + equality assert | §2.1; closed outcomes; aligned epic task_key |
| 2 Ruth `agent_task` row | Functional scope Ruth + one new agent_task |
| 3 Core callable + debug + no writes | AC2 semantics; AC8 |
| 4 Thin authenticated API | Callable for AST-1017 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge path |
| orch.git.commit-vocabulary | conforms | No forbidden git ops |
| orch.git.flow-direction-inviolable | conforms | Publish ref `sub/AST-952/AST-1015-preamble-validation-ruth` |
| orch.git.ftr-sub-topology | conforms | Child `sub/` under parent `ftr/` |
| orch.git.merge-on-checkout | conforms | Merge ftr tip before build noted |
| orch.git.no-cherry-pick-rebase-force | conforms | None planned |
| orch.git.no-dev-agent-branches | conforms | Named `sub/` only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic AST-952 |
| orch.git.three-permanent-branches | conforms | No fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | conforms | No open product decision |
| orch.pipeline.plan-is-bible | conforms | Stages bind build after Revision 1 |
| orch.pipeline.project-scoped-queues | conforms | Astral Candidate only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready after completed discuss round |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No test-tree edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | N/A to plan body |
| orch.roles.engineer-assignee-through-resolve | conforms | Joan does not reassign |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.config.config-source-of-truth | conforms | Task key `preamble_validate_response` shared with AST-1016; outcomes in validation config |
| astral.config.secrets-and-env-specific-from-environ | conforms | Literals only |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.standards.in-scope-only | conforms | Validation only; library/PREAMBLE_CONFIG/UI excluded |
| astral.standards.no-cross-contamination | conforms | Layered paths + repo admin JSON |
| astral.standards.dry-and-focused-functions | conforms | One epic task_key string; callable name ≠ task_key by design |
| astral.standards.public-then-helpers | conforms | Public callable placement noted |
| astral.standards.no-hardcoded-sets | conforms | Outcomes in `PREAMBLE_VALIDATION_CONFIG` |
| astral.standards.logging-via-utils | conforms | `get_logger` / truncate |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.standards.debug-contract-gated | conforms | Style-D only when `debug=True` |
| astral.layers.import-direction | conforms | ui→core; core→do_task |
| astral.layers.core-vs-external-bright-line | conforms | External via `do_task` only |
| astral.layers.ui-config-driven-business-logic | conforms | Thin API; no React rules |
| astral.ui.naming-conventions | conforms | snake_case route |
| astral.ui.single-gunicorn-worker | conforms | Untouched |
| astral.git.betty-no-src-or-features | conforms | Engineer owns paths |
| astral.agent.do-task-delegation | conforms | Core calls `do_task` with config task_key |
| astral.agent.grade-vector-validation | conforms | Not a graded vectors task |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.batch.claim-process-release | conforms | On-demand ledger; no entity claim batch |
| astral.batch.batch-id-format | conforms | `preamble-{task_key}-{uuid}` |
| astral.batch.batch-id-first | conforms | N/A claim signature |
| astral.batch.entity-agent-responses-latest-only | conforms | Relies on existing `do_task` storage |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `@require_auth` on new route |
| astral.state.core-decides-transitions | conforms | Explicitly no candidate transitions |
| astral.state.no-daisy-chain-in-run | conforms | No daisy-chain |
| astral.state.job-prior-states-enforced | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.config.pass-threshold-vs-score-floor, astral.standards.in-scope-only, astral.standards.no-cross-contamination, astral.standards.dry-and-focused-functions, astral.standards.public-then-helpers, astral.standards.no-hardcoded-sets, astral.standards.logging-via-utils, astral.standards.data-raises-caller-logs, astral.standards.utils-data-late-import-only, astral.standards.debug-contract-gated, astral.layers.import-direction, astral.layers.core-vs-external-bright-line, astral.layers.ui-config-driven-business-logic, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker, astral.git.betty-no-src-or-features, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.agent.confidence-bounds, astral.batch.claim-process-release, astral.batch.batch-id-format, astral.batch.batch-id-first, astral.batch.entity-agent-responses-latest-only, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.state.core-decides-transitions, astral.state.no-daisy-chain-in-run, astral.state.job-prior-states-enforced

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss (plan file not in Files Changed table)
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.standards.database-header-inventory — paths miss (`data/admin/**` ≠ `src/data/**`)
- astral.ui.frontend-file-placement — paths miss

**Notes:** Layer cell `data (repo admin JSON)` mapped to `data`. Plan Discuss round=1 completed (concern + reply); fix-now task_key clash closed.

## Findings

### resolved (was fix-now round=1)
- Task key now `preamble_validate_response` across `PREAMBLE_VALIDATION_CONFIG` / `TASK_CONFIG` / `agent_task.json` / `do_task`, with equality assert vs `PREAMBLE_CONFIG["validation_task_key"]` when present. Python callable remains `validate_preamble_answer`.

### acceptable
- Dual config homes for the same literal (AST-1016 `validation_task_key` + this ticket’s `task_key`) with assert — consumer has one string.
- No library writes; empty answer → Ruth Try Again; unrecognized outcome never coerced to Valid.
- Ruth-only; on-demand (no `dispatch_tasks` row); debug style-D when `debug=True`.

**Self-assessment:** Single-Component / Conf high / Risk Medium — honest; key-clash risk closed by Revision 1.

— Joan
context_tokens≈86000

#### joan — 2026-07-28T19:04:32.695Z
[validate-plan] **STOP — assignee still Hedy**

Re-checked `get_issue` AST-1015: assignee=`Hedy Lamarr` (`c12a27a1-…`), status=Plan Ready. Spawn claimed Joan; Linear does not.

Joan identity + `AGENTS.md` OK. Revised plan tip `b7283c57` already uses `preamble_validate_response`.

Chuckles: `save_issue` assignee → Joan, then re-spawn validate-plan. Joan does not self-assign.

— Joan
context_tokens≈84000

#### joan — 2026-07-28T19:03:46.857Z
[validate-plan] **STOP — assignee is not Joan**

Linear identity is Joan; epic `AGENTS.md` is Joan; AST-1015 is **Plan Ready**.

Assignee is currently **Hedy Lamarr**, not Joan. Round=1 concern/reply is complete (`[plan-discuss] round=1 reply` present); revised plan tip uses `preamble_validate_response`.

Per validate-plan identity gate: Chuckles must assign Joan on AST-1015, then re-spawn/resume validate-plan. I will not run the rubric or flip status while assignee is the implementer.

Status left **Plan Ready**. No assignee change from Joan.

— Joan
context_tokens≈82000

#### hedy — 2026-07-28T19:01:42.999Z
[plan-discuss] round=1 reply

**Delta:** Aligned this ticket’s agent/`TASK_CONFIG`/`PREAMBLE_VALIDATION_CONFIG` task_key to approved AST-1016 `PREAMBLE_CONFIG["validation_task_key"]` = **`preamble_validate_response`** (dropped invented `validate_preamble_answer` as a task_key). Python callable stays `validate_preamble_answer`. Added sibling-contract note + module assert equality when `PREAMBLE_CONFIG` is present. Outcomes remain in `PREAMBLE_VALIDATION_CONFIG` only.

Plan tip: `origin/sub/AST-952/AST-1015-preamble-validation-ruth` @ `b7283c57` — [`ast-1015-preamble-validation-ruth.md`](https://github.com/susansomerset/astral/blob/sub/AST-952/AST-1015-preamble-validation-ruth/docs/features/candidate/ast-1015-preamble-validation-ruth.md)

**Self-assessment (unchanged axes):** Scope Single-Component · Conf high · Risk Medium (key-clash closed by this revise).

#### joan — 2026-07-28T18:55:55.069Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1015
**Overall:** REVISE

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 library + columns | N/A — boundary (AST-1014) |
| AC2 Ruth Valid / Try Again / Escalate; Try Again does not advance; Escalate ≠ Valid; no new persona | Stages 1–4 (config + Ruth `agent_task` + core + API); no library writes; no persona JSON |
| AC3 PREAMBLE_CONFIG | N/A — boundary (AST-1016); plan Decision keeps outcomes/task_key out of that block |
| AC4 mechanical UI | N/A — boundary (AST-1017); no React |
| AC5–AC7 | N/A — boundaries / siblings |
| AC8 debug on touched validation/write paths | Stage 3 `debug=` contract on `validate_preamble_answer` |

### Child AC → plan stages

| Child AC | Stages |
|----------|--------|
| (parent) AC2 Ruth three outcomes; no advance; Escalate ≠ Valid; Ruth only | 1–4 |
| (parent) AC8 debug lines on touched validation path | Stage 3 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| 1 `PREAMBLE_VALIDATION_CONFIG` + `TASK_CONFIG` | Config-driven task key (§2.1); closed outcome set |
| 2 Ruth `agent_task` row | Functional scope Ruth + one new agent_task |
| 3 Core callable + debug + no writes | AC2 semantics; AC8 debug |
| 4 Thin authenticated API | Callable for AST-1017; no UI |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge path |
| orch.git.commit-vocabulary | conforms | No forbidden git ops |
| orch.git.flow-direction-inviolable | conforms | Publish ref `sub/AST-952/AST-1015-preamble-validation-ruth` |
| orch.git.ftr-sub-topology | conforms | Child `sub/` under parent `ftr/` |
| orch.git.merge-on-checkout | conforms | Merge ftr tip before build noted |
| orch.git.no-cherry-pick-rebase-force | conforms | None planned |
| orch.git.no-dev-agent-branches | conforms | Named `sub/` only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic AST-952 |
| orch.git.three-permanent-branches | conforms | No fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | conforms | Key clash is engineer fix vs approved sibling, not new product intent |
| orch.pipeline.plan-is-bible | needs-discussion | Stages are buildable but task_key conflicts with approved AST-1016 contract |
| orch.pipeline.project-scoped-queues | conforms | Astral Candidate only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready gate |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No test-tree edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | N/A to plan body |
| orch.roles.engineer-assignee-through-resolve | conforms | Joan does not reassign |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.config.config-source-of-truth | violates | Task key invented as `validate_preamble_answer` while approved AST-1016 already sets `PREAMBLE_CONFIG.validation_task_key` = `preamble_validate_response` — dual homes / broken consumer contract |
| astral.config.secrets-and-env-specific-from-environ | conforms | Literals only |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.standards.in-scope-only | conforms | Validation only; library/PREAMBLE_CONFIG/UI excluded |
| astral.standards.no-cross-contamination | conforms | Layered paths + repo admin JSON |
| astral.standards.dry-and-focused-functions | violates | Same epic needs one task_key string; plan forks a second name instead of aligning to approved sibling |
| astral.standards.public-then-helpers | conforms | Public callable placement noted |
| astral.standards.no-hardcoded-sets | conforms | Outcomes in `PREAMBLE_VALIDATION_CONFIG` |
| astral.standards.logging-via-utils | conforms | `get_logger` / truncate helpers |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.standards.debug-contract-gated | conforms | Style-D only when `debug=True` |
| astral.layers.import-direction | conforms | ui→core; core→do_task |
| astral.layers.core-vs-external-bright-line | conforms | External via `do_task` only |
| astral.layers.ui-config-driven-business-logic | conforms | Thin API; no React rules |
| astral.ui.naming-conventions | conforms | snake_case route |
| astral.ui.single-gunicorn-worker | conforms | Untouched |
| astral.git.betty-no-src-or-features | conforms | Engineer owns paths |
| astral.agent.do-task-delegation | conforms | Core calls `do_task` with config task_key |
| astral.agent.grade-vector-validation | conforms | Not a graded vectors task |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.batch.claim-process-release | conforms | On-demand ledger; no entity claim batch |
| astral.batch.batch-id-format | conforms | `preamble-{task_key}-{uuid}` |
| astral.batch.batch-id-first | conforms | N/A claim signature |
| astral.batch.entity-agent-responses-latest-only | conforms | Relies on existing `do_task` storage |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `@require_auth` on new route |
| astral.state.core-decides-transitions | conforms | Explicitly no candidate transitions |
| astral.state.no-daisy-chain-in-run | conforms | No daisy-chain |
| astral.state.job-prior-states-enforced | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.config.pass-threshold-vs-score-floor, astral.standards.in-scope-only, astral.standards.no-cross-contamination, astral.standards.dry-and-focused-functions, astral.standards.public-then-helpers, astral.standards.no-hardcoded-sets, astral.standards.logging-via-utils, astral.standards.data-raises-caller-logs, astral.standards.utils-data-late-import-only, astral.standards.debug-contract-gated, astral.layers.import-direction, astral.layers.core-vs-external-bright-line, astral.layers.ui-config-driven-business-logic, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker, astral.git.betty-no-src-or-features, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.agent.confidence-bounds, astral.batch.claim-process-release, astral.batch.batch-id-format, astral.batch.batch-id-first, astral.batch.entity-agent-responses-latest-only, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.state.core-decides-transitions, astral.state.no-daisy-chain-in-run, astral.state.job-prior-states-enforced

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss (plan file not in Files Changed table)
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.standards.database-header-inventory — paths miss (`data/admin/**` ≠ `src/data/**`)
- astral.ui.frontend-file-placement — paths miss

**Notes:** Layer cell `data (repo admin JSON)` mapped to `data`.

## Findings

### fix-now
1. **Task key diverges from approved AST-1016.** This plan uses `PREAMBLE_VALIDATION_CONFIG["task_key"]` / `TASK_CONFIG` / `agent_task` key **`validate_preamble_answer`**. Approved AST-1016 plan (Plan Approved) already binds `PREAMBLE_CONFIG["validation_task_key"]` = **`preamble_validate_response`** and states AST-1015 must register that exact key (or stop on parent and update AST-1016). Dual names break §2.1 / DRY and will strand AST-1017. **Fix:** set this ticket’s task_key (config + TASK_CONFIG + agent_task.json + core) to `preamble_validate_response`, **or** open parent coordination and revise AST-1016 first — do not ship a silent second key.

### discuss
1. Prefer a single config home for the string (AST-1016 `validation_task_key` as the consumer-facing literal; this ticket’s block can re-export/assert equality) so AST-1017 has one read path.

### acceptable
- No library writes; empty answer allowed → Ruth Try Again; unrecognized outcome never coerced to Valid.
- Ruth-only persona; no new agent JSON; on-demand (no `dispatch_tasks` row).
- Debug style-D on the validation callable when `debug=True`.

**Self-assessment:** Single-Component / Conf high / Risk Medium — honest; Risk Medium correctly flags coerce-to-Valid, which the plan mitigates.

— Joan
context_tokens≈78000

#### joan — 2026-07-28T18:53:34.314Z
[validate-plan] **STOP — worktree AGENTS.md corruption**

Linear identity is Joan (`susan+joan@susansomerset.com`); AST-1015 is **Plan Ready** and assigned to Joan.

Epic worktree `/home/susan/astral-AST-952/AGENTS.md` header is **`# Ada — Dev Agent`**, not `# Joan — Statute Validator`.

Per validate-plan identity gate: I do **not** run the rubric while the worktree is seeded for another persona. Chuckles must `seed-agents-md` Joan (`joan-AGENTS.md`) into this epic worktree, then re-spawn/resume validate-plan for AST-1015.

Status left **Plan Ready**. No assignee change. No plan-rubric verdict.

— Joan
context_tokens≈72000

#### hedy — 2026-07-28T18:10:44.979Z
Plan: [`docs/features/candidate/ast-1015-preamble-validation-ruth.md`](https://github.com/susansomerset/astral/blob/sub/AST-952/AST-1015-preamble-validation-ruth/docs/features/candidate/ast-1015-preamble-validation-ruth.md) on `origin/sub/AST-952/AST-1015-preamble-validation-ruth` @ `34930846`.

**Scope:** Single-Component — Ruth `validate_preamble_answer` agent_task + `PREAMBLE_VALIDATION_CONFIG`/`TASK_CONFIG` + intake core callable + one `POST .../preamble/validate` route; no UI, library, or PREAMBLE_CONFIG.

**Conf:** high — reuses `do_task` envelope, existing `college_intern_ruth`, intake ledger pattern, and repo `agent_task.json` apply-at-startup; closed three-string outcome set with exact-match parse (no coerce-to-Valid).

**Risk:** Medium — a wrong Valid coerce would let bad answers persist once AST-1017 wires writes; mitigated by membership check and zero library writes in this ticket.

Note: publish tip dropped an accidental sibling `ast-1016` plan file that landed when the epic worktree was on the wrong sub during commit; AST-1016 keeps its own plan on its publish ref.

---

# AST-1015 — Preamble Valid / Try Again / Escalate via Ruth

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1015/preamble-valid-try-again-escalate-via-ruth-candidate-profile-preamble  
**Parent:** https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake  

**Publish ref (origin):** `sub/AST-952/AST-1015-preamble-validation-ruth`  
**Parent integration ref:** `ftr/AST-952-candidate-profile-preamble-to-intake`

Ship a **reusable Ruth (Little Brain) validation call** for preamble answers: one new `agent_task` + config-driven task key + core callable (+ thin API) that returns exactly **Valid**, **Try Again**, or **Escalate**. Callers (AST-1017) use the outcome to decide whether to advance; this ticket never writes library fields and never advances preamble steps.

Boundaries (do **not** implement): contact/context/artifacts library (AST-1014), `PREAMBLE_CONFIG` Intro/1st/2nd Try copy or step sequence (AST-1016), mechanical intake UI (AST-1017), Estelle confirm (AST-953), new agent personas or agent-framework patterns, candidate state-machine vocabulary changes.

Depends on AST-1014 library already on `origin/ftr/AST-952-candidate-profile-preamble-to-intake` (User Testing) — merge that ftr tip before build; do not re-implement library work.

**Sibling contract (AST-1016, Plan Approved):** `PREAMBLE_CONFIG["validation_task_key"]` is already bound to **`preamble_validate_response`**. This ticket registers that **exact** `task_key` (config + `TASK_CONFIG` + `agent_task.json` + `do_task`). Do not invent a second key.

---

## Revisions

### Revision 1 — 2026-07-28
Driven by: Joan `[plan-discuss] round=1 concern` — task_key `validate_preamble_answer` diverged from approved AST-1016 `PREAMBLE_CONFIG["validation_task_key"]` = `preamble_validate_response` (§2.1 / DRY).
Changes: Renamed agent/`TASK_CONFIG`/`PREAMBLE_VALIDATION_CONFIG` task_key to `preamble_validate_response` everywhere; kept Python callable name `validate_preamble_answer`; added equality assert vs `PREAMBLE_CONFIG["validation_task_key"]` when that block is present; consumer-facing string remains AST-1016’s `validation_task_key`.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `PREAMBLE_VALIDATION_CONFIG` (task_key=`preamble_validate_response` + outcomes); add `TASK_CONFIG["preamble_validate_response"]` with `response_schema`; assert equality with `PREAMBLE_CONFIG["validation_task_key"]` when that block exists | utils |
| `data/admin/agent_task.json` | New row `preamble_validate_response` assigned to `college_intern_ruth` with Valid/Try Again/Escalate prompts | data (repo admin JSON) |
| `src/core/intake.py` | Public `validate_preamble_answer(...)` — ledger + `do_task(task_key=preamble_validate_response)` + outcome parse; `debug=` contract lines; widen module docstring | core |
| `src/ui/api/api_intake.py` | `POST /api/candidates/<candidate_id>/preamble/validate` thin wrapper | ui |

---

## Stage 1: Config — task key, outcomes, TASK_CONFIG schema

**Done when:** `PREAMBLE_VALIDATION_CONFIG["task_key"]` is `"preamble_validate_response"` (same string as approved AST-1016 `validation_task_key`); outcomes are exactly the three AC strings; `TASK_CONFIG` has a matching entry with `response_schema.outcome` required string; `get_task_keys()` includes the new key; if `PREAMBLE_CONFIG` is already defined in `config.py`, a module-level assert enforces key equality. No agent_task JSON or core/UI yet.

1. In `src/utils/config.py`, immediately after `CANDIDATE_LIBRARY_CONFIG` (or after `PREAMBLE_CONFIG` if AST-1016 has already landed on this tree — place this block **after** `PREAMBLE_CONFIG` when both exist so the assert can see it), add:

```python
# AST-1015: Ruth preamble answer validation (Valid / Try Again / Escalate).
# task_key MUST match PREAMBLE_CONFIG["validation_task_key"] (AST-1016) = preamble_validate_response.
PREAMBLE_VALIDATION_CONFIG = {
    "task_key": "preamble_validate_response",
    "outcomes": ("Valid", "Try Again", "Escalate"),
    "outcome_field": "outcome",  # agent_payload key
}
```

2. Immediately after both blocks exist in the file, add (skip only if `PREAMBLE_CONFIG` is not yet defined on this checkout — then the literal alone is the contract; when ftr/sibling merge brings `PREAMBLE_CONFIG`, add the assert in the same stage before Code Complete):

```python
assert PREAMBLE_VALIDATION_CONFIG["task_key"] == PREAMBLE_CONFIG["validation_task_key"]
```

⚠️ **Decision:** Consumer-facing task_key string lives on AST-1016 as `PREAMBLE_CONFIG["validation_task_key"]`. This ticket’s `PREAMBLE_VALIDATION_CONFIG["task_key"]` is the **same literal** (`preamble_validate_response`) plus outcome vocabulary — not a second name. Outcomes stay here (not in PREAMBLE_CONFIG). AST-1017 may read `validation_task_key` from ui_config/`PREAMBLE_CONFIG` and/or call this ticket’s API without choosing between two keys.

⚠️ **Decision:** Do **not** invent `validate_preamble_answer` as a task_key. That name is reserved for the Python callable only (Stage 3).

3. In `TASK_CONFIG`, add an entry keyed `"preamble_validate_response"` (place with other candidate intake tasks, after `intake_build_request`):

```python
"preamble_validate_response": {
    "response_schema": {
        "outcome": {"type": "str", "required": True},
    },
    "response_format": "json",
    "context_format": "preamble_validate_{index}",
    "entity_type": "candidate",
    "requires_candidate_key": True,
    "trigger_state": None,
},
```

4. Do **not** add a `dispatch_tasks` row. This task is on-demand (UI/API), not a scheduler batch.

---

## Stage 2: Repo agent_task row — Ruth only

**Done when:** `data/admin/agent_task.json` contains one new object with `task_key` == `"preamble_validate_response"` (== `PREAMBLE_VALIDATION_CONFIG["task_key"]`), `agent_id` == `"college_intern_ruth"`, prompts that force the three-outcome envelope, and no other agent/persona rows changed. Startup apply of repo JSON would load Ruth on this key (no blank `sync_agent_tasks` stub left as the live row).

1. Append a new object to the JSON array in `data/admin/agent_task.json` with these fields (generate a fresh `task_key_uuid` via `uuid.uuid4()`; set `updated_at` to current UTC `YYYY-MM-DD HH:MM:SS`; leave unused cache slots empty strings):

| Field | Value |
|-------|--------|
| `task_key` | `preamble_validate_response` |
| `agent_id` | `college_intern_ruth` |
| `task_name` | `Validate Preamble Answer` |
| `task_group_name` | `Candidate Preamble` |
| `task_group_order` | `1` |
| `task_seq` | `1` |
| `current` | `1` |
| `run_next` | `""` |
| `system_prompt` | `""` (persona lives on the Ruth agent row) |
| `cache_prompt_b` / `_c` / `_d` / `nocache_prompt` | `""` |

2. Set `cache_prompt` to the standing instructions (exact text):

```
## PREAMBLE ANSWER VALIDATION

You judge whether a candidate ANSWER is a valid response to a QUESTION.
The QUESTION and ANSWER are in the live CONTENT / TASK block as:

QUESTION:
<question text>

ANSWER:
<answer text>

## OUTCOMES (pick exactly one)

- Valid — the answer is recognizably the kind of content the question asked for (even if imperfect, informal, or short).
- Try Again — empty, whitespace-only, off-topic, nonsense, or clearly not what the question asked; the candidate should re-enter.
- Escalate — cannot be judged safely (ambiguous, contradictory, or needs human review). Escalate is never Valid.

## OUTPUT

Return the standard Astral JSON envelope only.
agent_payload must be a JSON object with exactly one key: "outcome"
"outcome" must be exactly one of: Valid | Try Again | Escalate
No extra keys. No commentary outside the envelope. Prefer Try Again over Valid when the answer type is doubtful. Use Escalate only when human review is truly needed.
```

3. Set `user_prompt` to the turn instruction (exact text):

```
Validate the QUESTION/ANSWER pair in the CONTENT block using your PREAMBLE ANSWER VALIDATION instructions. Respond with the envelope and agent_payload.outcome only.
```

⚠️ **Decision:** One generic task for every preamble step (question text supplied at call time), not per-field task keys. AST-1016/1017 pass the step’s `validation_question` string; Ruth does not own PREAMBLE_CONFIG.

⚠️ **Decision:** Do not create or edit any `data/admin/agent.json` persona. Existing `college_intern_ruth` (Little brain) is mandatory.

---

## Stage 3: Core callable — parse outcomes, debug contract, no library writes

**Done when:** `validate_preamble_answer` exists on `src/core/intake.py`, calls `do_task` with `task_key` from `PREAMBLE_VALIDATION_CONFIG` (`preamble_validate_response`), returns one of the three config outcomes on success, never writes `candidate_data` / name columns, treats unrecognized model text as failure (not Valid), and with `debug=True` emits style-D found/recorded lines. Manual call with mocked/`do_task` success path can return `"Try Again"` without advancing anything.

1. Widen the module docstring of `src/core/intake.py` to state it owns mechanical preamble validation **and** Estelle multi-turn sessions.

2. Import `PREAMBLE_VALIDATION_CONFIG` from `src.utils.config`. Import `get_logger` / `truncate_debug_content` from `src.utils.logging` (reuse existing `flush_log_buffer` / `log_batch_id` imports).

3. Add public async function (public section, before session helpers):

```python
async def validate_preamble_answer(
    candidate_id: str,
    question: str,
    answer: str,
    *,
    step_index: int = 1,
    step_total: int = 1,
    debug: bool = False,
) -> dict:
```

**Behavior (literal):**

- Resolve `task_key = PREAMBLE_VALIDATION_CONFIG["task_key"]` (must be `"preamble_validate_response"`).
- Load candidate via `get_candidate(candidate_id)`; if missing → raise `ValueError(f"Candidate not found: {candidate_id}")`.
- If `(question or "").strip()` is empty → raise `ValueError("question required")`.
- Strip `answer` for the model input but **allow** empty answer (Ruth should return Try Again) — do not raise on empty answer.
- Build `live_content` exactly:

```
QUESTION:
{question.strip()}

ANSWER:
{(answer or "").strip()}
```

- Open a dispatch ledger like `_run_intake_task`: `batch_id = f"preamble-{task_key}-{uuid.uuid4()}"`, `save_dispatch_ledger(..., entity_type="candidate", batch_size=1)`, `log_batch_id.set(batch_id)`.
- `await do_task(task_key=task_key, live_content=live_content, index=candidate_id, ctx=candidate, debug=debug)`.
- On `do_task` failure / missing success: update ledger FAILED; return `{"success": False, "outcome": None, "error": <msg>, "batch_id": batch_id}` — **do not** invent Valid.
- On success: read `parsed = result.get("parsed_response")`. After `do_task` unwrap, `parsed` is the `agent_payload` dict (same as other JSON tasks). Read `raw = parsed.get(PREAMBLE_VALIDATION_CONFIG["outcome_field"])` if `parsed` is a dict; else treat as failure.
- If `raw` is not in `PREAMBLE_VALIDATION_CONFIG["outcomes"]` (exact string match): ledger FAILED; return success False with error `invalid preamble validation outcome: {raw!r}` — **never** coerce Escalate or unknown → Valid.
- Else: ledger COMPLETED with `total_passed=1`; return `{"success": True, "outcome": raw, "error": None, "batch_id": batch_id}`.
- `finally`: `flush_log_buffer()`; `log_batch_id.set(None)`.

4. **Debug contract** (`debug=True` only), after the outcome is known (success or typed failure):

- One `logger.debug_index(func="validate_preamble_answer", index=step_index, total=step_total, identifier=candidate_id, outcome=...)` where outcome is `found|Valid` / `found|Try Again` / `found|Escalate` on success, or `found|error` on failure.
- `logger.debug_detail` lines: `question=` and `answer=` via `truncate_debug_content(...)` on the stripped strings; on failure also `error=...`.

5. **Hard rules in this function:** no `save_candidate_data`, no column writes, no candidate state transitions, no PREAMBLE_CONFIG step/Intro reads (task_key may come only from `PREAMBLE_VALIDATION_CONFIG`, which is asserted equal to AST-1016’s key). Try Again / Escalate “do not advance” is satisfied because this callable never advances or persists preamble progress — AST-1017 must not write library fields unless `outcome == "Valid"`.

⚠️ **Decision:** Place the callable in `intake.py` (not a new module, not `candidate.py`) so AST-1017 shares the intake API blueprint and the existing single-shot ledger/`do_task` pattern (`_run_intake_task`), while keeping library persistence owned by AST-1014 helpers.

---

## Stage 4: Thin API — callable from mechanical UI later

**Done when:** Authenticated `POST /api/candidates/<candidate_id>/preamble/validate` with JSON `{question, answer, step_index?, step_total?}` returns `{success, outcome, batch_id}` on Ruth success, 400 on validation ValueErrors, 404 when candidate missing, and never writes candidate data. No React changes.

1. In `src/ui/api/api_intake.py`, import `validate_preamble_answer` from `src.core.intake`.

2. Add route on `intake_bp`:

```
POST /<candidate_id>/preamble/validate
@require_auth
```

3. Handler body:

- `body = request.get_json(silent=True) or {}`
- `question = body.get("question")`; `answer = body.get("answer")` (default `""` if key missing for answer only)
- Optional `step_index` / `step_total`: ints defaulting to `1` / `1`; if present and not int-coercible → 400 `{"error": "step_index and step_total must be integers"}`
- `asyncio.run(validate_preamble_answer(..., debug=_debug_flag()))`
- On `ValueError` with `"Candidate not found"` → 404; other `ValueError` → 400 `{"error": str(e)}`
- On success dict with `success is False` → HTTP 200 still with the JSON body (caller inspects `success` / `outcome`) — same pattern as other LLM wrappers that return structured failure without 500, unless `RuntimeError`/unexpected → 500
- Return `jsonify({k: result[k] for k in ("success", "outcome", "error", "batch_id")})` with status 200 when the callable returns normally

4. Do **not** add frontend pages, PREAMBLE_CONFIG prompts, or library write endpoints.

---

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the Files Changed table.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes a stage on the epic worktree, commits, publishes to `origin/sub/AST-952/AST-1015-preamble-validation-ruth`, then proceeds.

Blocking comment format (parent AST-952):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** Single-Component — one new Ruth `agent_task` (`preamble_validate_response`) + config/`TASK_CONFIG` + intake core callable + one intake API route; no UI, no library schema, no PREAMBLE_CONFIG ownership.

**Conf:** high — aligned to approved AST-1016 `validation_task_key`; reuses `do_task` envelope/`response_schema`, existing Ruth agent, intake ledger pattern, and repo `agent_task.json` apply-at-startup; outcomes are a closed three-string set.

**Risk:** Medium — a wrong coerce-to-Valid path would let bad preamble answers persist once AST-1017 wires writes; mitigated by exact outcome membership check and no writes in this ticket. Key-clash risk with AST-1016 is closed by Revision 1.

---

## Code Rules self-review

| Rule | Check |
|------|--------|
| §1.3 DRY | One epic task_key string shared with AST-1016 (`preamble_validate_response`); reuse `_run_intake_task`-style ledger/`do_task` |
| §1.4 / §2.1 | Task key matches `PREAMBLE_CONFIG["validation_task_key"]`; outcomes only in `PREAMBLE_VALIDATION_CONFIG`; no inline Valid/Try Again/Escalate sets in core/UI |
| §1.5.1 | Debug lines only when `debug=True`; style-D index + ` \| ` detail; truncate long Q/A |
| §2.2 | Core calls `do_task`; no UI→external |
| §2.6 | No candidate state transitions |
| §3.3 | UI imports core only; core does not import UI; no new persona JSON beyond the task row |
| New agents | Forbidden — `college_intern_ruth` only |

## Review

**Publish ref:** `sub/AST-952/AST-1015-preamble-validation-ruth`
**Build tip:** `3a6444b16efae68f0f1bf1180dc04772d7256f31`

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Tip reviewed:** `7ff0ac90955ae70340c4ec1efe57f1e99f6c6ebc` (`origin/sub/AST-952/AST-1015-preamble-validation-ruth` vs `origin/dev`)
**Overall:** DISCUSS

#### What’s solid
- Stages 1–4 match Revision 1: `PREAMBLE_VALIDATION_CONFIG["task_key"]` == `PREAMBLE_CONFIG["validation_task_key"]` == `preamble_validate_response`; Ruth-only `agent_task` row; `validate_preamble_answer` via `do_task` with closed outcomes (no coerce-to-Valid); no library writes / state transitions.
- Debug style-D gated on `debug=True` with truncated Q/A detail; API `POST …/preamble/validate` keeps `@require_auth` and `_debug_flag()`.
- Betty catalog lock 39 + fixture sync for `preamble_validate_response` on ftr base (no polluted origin/dev merge).

#### Issues
1. **discuss** — C4 stragglers: Joan excluded statutes that the three-dot tip scores in-scope (tip carries AST-1014/1016 + frontend/tests): `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.standards.database-header-inventory`, `astral.ui.frontend-file-placement`. All **conform**; no product fix for AST-1015.

#### Notes
Joan plan-rubric APPROVED (Revision 1 after Plan Discuss). No fix-now on the Ruth validation delta.

## Resolution

**2026-07-30** — `resolve(AST-1015): — clean`

- **fix-now:** none (Radia Overall DISCUSS; recommended proceed).
- **discuss (C4 stragglers):** noted — tip-topology statute in-scope vs Joan plan exclude; all scored **conform**; no AST-1015 product change.
- Tip after resolve publish: `origin/sub/AST-952/AST-1015-preamble-validation-ruth` (this commit).

