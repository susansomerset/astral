<!-- linear-archive: AST-1060 archived 2026-08-07 -->

## Linear archive (AST-1060)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1060/meteorite-qualified-qualify-meteorite-configdispatch-qualify-meteorite  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1058 — Qualify Meteorite  
**Blocked by / blocks / related:** parent: AST-1058; blocks: AST-1062; blocks: AST-1061

### Description

## What this implements

Owns `JOB_STATES` for **METEORITE_QUALIFIED** and **METEORITE_FAILED_QUALIFY** (and error sibling if needed), UI manifests, update **METEORITE_NEW** role as pre-AI entry, retarget meteorite `evaluate_jd` / GDL priors so GDL starts at **METEORITE_QUALIFIED**, plus `TASK_CONFIG` / agent_task shell for `qualify_meteorite` and dispatch_task row(s) claiming **METEORITE_NEW**. Does **not** own gazer Playwright ingest or core apply beyond config defaults.

## Citations

`pattern.config.config-block`; `pattern.state.entity-state-transitions`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.state.job-prior-states-enforced`.

## Acceptance criteria

- [X] 3. New jobs from this path land on **METEORITE_NEW** with JD text and without Ruth metadata (pre-AI).
- [X] 4. Batch task `qualify_meteorite` claims **METEORITE_NEW**, returns external job UUID, job title, `job_link`, and visible JD content; on success the job is on **METEORITE_QUALIFIED** with those fields as authoritative content. (config/schema/dispatch half)
- [X] 5. Meteorite `evaluate_jd` claims/grades from **METEORITE_QUALIFIED** only — not from unenriched **METEORITE_NEW**.
- [X] 6. Bogus / 404 / unusable extracts land on **METEORITE_FAILED_QUALIFY** (visible in Jobs skipped manifests). (state registration)
- [X] 7. Non-meteorite `qualify_job_listings` / scrape / GDL paths unchanged (smoke).

## Boundaries

- [X] Does **not** own gazer Playwright ingest or core apply beyond config defaults. Sibling Katherine owns gazer email→meteorite create; sibling Hedy owns qualify batch apply.

## Notes for planning

Citations above. Retarget AST-1052 meteorite `evaluate_jd` claim from **METEORITE_NEW** to **METEORITE_QUALIFIED**.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1058-qualify-meteorite`, child `sub/AST-1058/<this-id>-slug`. Created at dispatch-parent.

### Comments

#### betty — 2026-07-30T01:27:22.108Z
[check-linear]

Reconciled duplicate `merge-tests(AST-1060)` (was 3) → **one** delivery of final tests SHA `35c22e42` (catalog 42 / handoff fixes). Tip `86e426d8` (`resolve` on top). `validate-sub-log` **ok**. Force-with-lease to publish ref only.

— Betty

#### chuckles — 2026-07-30T01:26:06.992Z
[merge-child] blocked: duplicate merge-tests(AST-1060) on sub — count=3 (amend on tests, one merge-tests only).

@Betty White — please reconcile so `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch` has **one** `merge-tests(AST-1060)` only, then leave publish tip ready for Chuckles merge-child retry. Assignee stays Ada for product; this is tests hygiene on the sub tip.

— Chuckles

#### radia — 2026-07-30T01:24:17.378Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1060
**Publish ref:** `3f8f6fc46eb022b937ab0a7929e08ca8e6cf5d0b` (`origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch`)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch` — layers `{core, docs, utils}`.
**This ticket owns:** METEORITE_QUALIFIED / FAILED_QUALIFY / ERROR_QUALIFY + UI; qualify_meteorite TASK_CONFIG / METEORITE_DISPATCH_TASKS; evaluate_jd@METEORITE_QUALIFIED; retire evaluate_jd@METEORITE_NEW; Ruth agent_task shell.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| `astral.agent.confidence-bounds` | scoped | conforms | Unscored enrichment task; no confidence math |
| `astral.agent.do-task-delegation` | scoped | conforms | Config/dispatch only; apply deferred AST-1062 |
| `astral.agent.grade-vector-validation` | scoped | conforms | scored False / fields schema; no grade vectors |
| `astral.batch.batch-id-first` | scoped | conforms | Reuses ensure_meteorite_dispatch_tasks; no new claim APIs |
| `astral.batch.batch-id-format` | scoped | conforms | Untouched |
| `astral.batch.claim-process-release` | scoped | conforms | Dispatch rows only; apply AST-1062 |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | Untouched |
| `astral.config.config-source-of-truth` | scoped | conforms | States/schema/dispatch/triggers in config + agent_task |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | evaluate_jd score_floor None retained |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss (artifacts/**, scripts/spikes/**) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Plan under docs/features/; no spikes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single AST-1060 plan file |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test()/merge-tests; engineer code() owns src+features |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | test() owns tests/bible; engineer code() product only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Retire stays in dispatcher; no external I/O |
| `astral.layers.import-direction` | scoped | conforms | dispatcher already data+config; no new UI→core |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers/paths miss (scripts) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | In Review/Skipped manifests via config lists |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | Untouched |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | Untouched |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers/paths miss (src/ui) |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | Uses existing delete_dispatch_task wrapper |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers/paths miss (src/data) |
| `astral.standards.debug-contract-gated` | scoped | conforms | No apply/ingest debug on this tip |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Extends ensure_meteorite_dispatch_tasks |
| `astral.standards.in-scope-only` | scoped | conforms | No gazer/consult apply; boundaries held |
| `astral.standards.logging-via-utils` | scoped | conforms | Untouched |
| `astral.standards.no-cross-contamination` | scoped | conforms | Meteorite qualify vs non-meteorite paths separated |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Retire hard-matches AC5 meteorite GDL pair only |
| `astral.standards.public-then-helpers` | scoped | conforms | Extends existing public ensure helper |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No new utils→data |
| `astral.state.core-decides-transitions` | scoped | conforms | No transition code; priors in config |
| `astral.state.job-prior-states-enforced` | scoped | conforms | GDL from QUALIFIED; live claim surface matches via retire |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | Untouched |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers/paths miss (frontend) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers/paths miss (src/ui) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | Untouched |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Tip = merge-tests after qa-handoff rounds |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | Work on sub/* only |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1058/AST-1060-… |
| `orch.git.merge-on-checkout` | universal | conforms | No conflicting checkout rewrite |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No rewrite ops |
| `orch.git.no-dev-agent-branches` | universal | conforms | Ticket sub publish-ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | astral-AST-1058 |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Three qualify outcomes + retire decision documented |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match tip; Joan Discuss retire landed |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty owns tests/bible |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Assignee remains Ada |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Role-appropriate paths per vocabulary |

## Pattern conformance

- `pattern.config.config-block` — conforms (JOB_STATES / TASK_CONFIG / METEORITE_DISPATCH_TASKS)
- `pattern.state.entity-state-transitions` — conforms (priors QUALIFIED→GDL; claim surface retire)
- Cited statutes covered in Statutes checked

## Plan adherence

Stages 1–2 match tip: qualify states/UI; GDL retarget; qualify_meteorite TASK_CONFIG + dispatch row; ensure retire evaluate_jd@METEORITE_NEW; Ruth agent_task shell. Self-Assessment Single-Component matches. Boundaries held vs gazer (AST-1061) / apply (AST-1062). Non-meteorite qualify_job_listings / evaluate_jd@JD_READY untouched.

## Findings

### fix-now
(none)

### discuss
1. **straggler ×3** — Joan excluded at plan time; in-scope on three-dot vs `origin/dev` via plan docs + Betty tests/bible (all substance **conforms**):
   - `astral.debug.spikes-under-debug-dir`
   - `astral.docs.features-single-file-per-ticket`
   - `astral.git.engineer-test-tree-ban`

### advisory
(none)

### What’s solid
- Manifest/config-driven qualify insert; surgical retire closes AC5 claim surface; JD_READY preserved.

### Recommended actions
- Ada: acknowledge stragglers → resolve-child → User Testing.

**Notes:** Joan plan-rubric APPROVED (Discuss round=1 retire fix). Docs append @ `3f8f6fc4`. Product tip before docs: `6f155650`.

context_tokens≈28000

#### betty — 2026-07-30T01:20:56.357Z
[check-linear]

Cleared Ada second `[qa-handoff]` — test/manifest only:
- Restored **AST-786** catalog lock to **42** + frozenset **without** `preamble_validate_response` (AST-1060 tip = `origin/dev` 41 + `qualify_meteorite` only).
- Preamble stays in `TestAst1015PreambleValidateCatalogRow` — not folded into this tip’s AST-786 lock.

**Publish tip:** `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch` @ `6f155650` (`merge-tests` of `35c22e42`).
**Assignee:** Ada — re-run same manifest.

```bash
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow \
  -q
```

— Betty

#### ada — 2026-07-30T01:18:11.742Z
[qa-handoff]

@Betty White — second pass red after your return @ `68dc3ba2`. Still **test/manifest**, not product. Status stays **Tests Ready**; reassigned to you. No product commits.

**Tip verified:** `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch` @ `68dc3ba2` (`BEHIND=0`). Prior two qa-handoff fixes (qjl `agent_task`, provision skip sum) are green.

**Command:** (same as your return-pass re-run)
```bash
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow \
  -q
```
**Result:** 2 failed, 17 passed.

### Failures
- `TestAst786AgentTaskRepoJsonSeed::test_repo_json_has_43_current_catalog_keys` — `assert 42 == 43`
- `…::test_startup_apply_loads_all_43_current_rows` — `assert count == 43`

### Why test/manifest
This publish tip’s `data/admin/agent_task.json` is **42** rows = `origin/dev` (41) + AST-1060 `qualify_meteorite` only. There is **no** `preamble_validate_response` row here (`only here: qualify_meteorite`; `only dev: []`).

Your `d26c47ee` (`test(AST-1015): … catalog 42 includes preamble`) + the AST-1060 docstring bump to **43** folds sibling **AST-1015** product into this tip’s catalog lock. That’s the opposite of the prior correct note on this class: *“Parallel AST-1015 (`preamble_validate_response`) is not on that base yet — its row assertion stays in TestAst1015PreambleValidateCatalogRow.”*

**Ask:** restore AST-786 locks on this tip to **42** + frozenset **without** `preamble_validate_response` (keep preamble in AST-1015’s own class). Do not require AST-1015 product on AST-1060’s `sub/*`. Then `merge-tests` + reassign Ada.

#### betty — 2026-07-30T01:14:53.754Z
[check-linear]

Cleared Ada `[qa-handoff]` — test/manifest only (no product):
1. AC7 smoke: drop `qualify_job_listings["agent_task"]` invent; assert key absent + pass/fail/error + trigger NEW.
2. `test_provision_touches_scheduled_candidates`: expected `skipped_missing_config` **6** (template + loop `[tmpl,c2]` = 3× stub 2).

**Publish tip:** `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch` @ `68dc3ba2` (`merge-tests` of `1dd01ec3`).
**Assignee:** Ada — re-run same manifest via `test-child`.

```bash
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow \
  -q
```

— Betty

#### ada — 2026-07-30T01:10:39.523Z
[qa-handoff]

@Betty White — two reds on your AST-1060 manifest look like **test/manifest mismatch**, not product. Left status **Tests Ready**; reassigned to you. No product commits.

**Publish tip run:** `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch` @ `e4d3346a` (matches your Tests Ready SHA). `BEHIND=0` vs `origin/dev`.

**Command:**
```bash
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow \
  -q
```
**Result:** 2 failed, 17 passed.

### 1. `TestAst1053MeteoriteGdlJobStates::test_non_meteorite_gdl_and_recommended_untouched`
`KeyError: 'agent_task'` on `cfg.TASK_CONFIG["qualify_job_listings"]["agent_task"]`.

**Why test/manifest:** Non-meteorite `qualify_job_listings` TASK_CONFIG on this tip (and `origin/dev`) has never had an `agent_task` key — outcomes/pass/fail/error/schema only. AC7 smoke should assert pass/fail/error (those passed) without requiring `agent_task`. `qualify_meteorite` correctly has `agent_task` in `TestAst1060QualifyMeteoriteConfig`; do not invent one on `qualify_job_listings` to mirror it.

### 2. `TestAst1054MeteoriteDispatchProvision::test_provision_touches_scheduled_candidates`
`assert out["skipped_missing_config"] == 4` but got `6`.

**Why test/manifest:** Stub returns `skipped_missing_config: 2` per `ensure` call. `provision_meteorite_dispatch_tasks` always (1) ensures the template, then (2) loops `list_candidate_ids_with_dispatch_tasks()` which here is `["tmpl", "c2"]` — so **3** ensure calls → `2*3=6`. Product aggregation is correct (`candidates_touched==2` still only counts the loop). Expected should be `6` (or drop `tmpl` from the list so arithmetic is `2+2=4` for template + one other).

Please revise tests / republish `merge-tests` + updated re-run, then reassign Ada.

#### betty — 2026-07-30T01:06:18.748Z
## QA test manifest — AST-1060

**Publish:** `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch` @ `e4d3346a`
**tests SHA:** `082cac3d` (`merge-tests(AST-1060): origin/tests 082cac3d…`)

### 1. Existing / revised coverage
1. `tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates` — QUALIFIED priors, pre-AI NEW label, fail/error qualify in Skipped, ungated smoke + qualify_job_listings AC7
2. `tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch` — `evaluate_jd`@`METEORITE_QUALIFIED`; no `@METEORITE_NEW`
3. `tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision` — insert counts (+qualify), QUALIFIED trigger, retire stale `@METEORITE_NEW`, JD_READY untouched
4. `tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed` — catalog **42** + UAT fixture byte-lock
5. `tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision` — still stubs meteorite provision

### 2. Broken / obsolete (revised this pass)
- AST-1053 GDL priors from `METEORITE_NEW`; NEW UI label
- AST-1054 `evaluate_jd`@`METEORITE_NEW` + ensure insert counts
- AST-786 **41 → 42** (+ `docs/uat-fixtures/AST-756/expected-agent_task.json`)

### 3. Gaps (new)
6. `tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig`
7. `tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow`

**Integration:** none revised (no existing scenarios for qualify_meteorite / METEORITE_QUALIFIED).

### Re-run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow \
  -q
```

### Bible shasums on publish tip
- `docs/test-bible/utils/config.md` `2aa9b85b44e8de74710b0cae0b353be981a6e657`
- `docs/test-bible/core/dispatcher.md` `baa1bc02580903294abf5be68dc8e47a8eb6156a`
- `docs/test-bible/core/repo_admin_json.md` `e0c0513b389823f2f055b009db19b310166f2515`

— Betty

#### joan — 2026-07-30T00:52:06.572Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1060
**Overall:** APPROVED

**Notes:** Plan Discuss round=1 completed. Tip `3a76de4f`. Layer `data/admin` → `docs`. Prior fix-now (stale `evaluate_jd`@`METEORITE_NEW`) addressed — `ensure_meteorite_dispatch_tasks` retires that pair after insert. Assignee stays Joan; Chuckles restores Ada after wait.

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Gazer email → create | N/A — AST-1061 |
| 2 Dedupe on external job id | N/A — AST-1061 |
| 3 Land **METEORITE_NEW** pre-AI | Stage 1 frames state; create/gazer AST-1061/1056 |
| 4 `qualify_meteorite` enrich → **METEORITE_QUALIFIED** | Stages 1–2 config/schema/dispatch/agent_task; apply AST-1062 |
| 5 Meteorite `evaluate_jd` claims **METEORITE_QUALIFIED** only | Stage 1 config retarget + live-row retire |
| 6 Bogus/404 → **METEORITE_FAILED_QUALIFY** | Stage 1 state + SKIPPED manifests; apply AST-1062 |
| 7 Non-meteorite paths unchanged | Stage 1; JD_READY evaluate_jd untouched |
| 8 Style D ingest/qualify apply | N/A — AST-1061 / AST-1062 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 3 METEORITE_NEW pre-AI role | 1 |
| 4 qualify config/schema/dispatch half | 1–2 |
| 5 evaluate_jd from QUALIFIED only | 1 |
| 6 FAILED_QUALIFY registration + skipped UI | 1 |
| 7 Non-meteorite smoke | 1 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 States, UI, GDL retarget, TASK_CONFIG, dispatch helpers + retire | Purpose QUALIFIED insert; AC3–7 config half; AC5 live claim surface |
| 2 agent_task.json Ruth shell | AC4 enrichment prompts |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1060):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No rewrite flow |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1058` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Three outcomes decided; matches parent |
| orch.pipeline.plan-is-bible | conforms | Stages binding; siblings excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready re-check |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Chuckles restores Ada after wait |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Unscored enrichment task |
| astral.agent.do-task-delegation | conforms | No new I/O path; config/dispatch only |
| astral.agent.grade-vector-validation | conforms | No grade vectors on qualify_meteorite |
| astral.batch.batch-id-first | conforms | No new claim APIs; reuse ensure pattern |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Apply deferred to AST-1062; dispatch rows only |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched here |
| astral.config.config-source-of-truth | conforms | States/schema/dispatch in config + agent_task |
| astral.config.pass-threshold-vs-score-floor | conforms | evaluate_jd score_floor None retained |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned |
| astral.layers.core-vs-external-bright-line | conforms | Retire stays in dispatcher/core |
| astral.layers.import-direction | conforms | dispatcher already imports data + config |
| astral.layers.ui-config-driven-business-logic | conforms | Manifests via config lists |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | Uses existing delete wrapper |
| astral.standards.debug-contract-gated | conforms | No apply/ingest debug here |
| astral.standards.dry-and-focused-functions | conforms | Extends ensure_meteorite_dispatch_tasks |
| astral.standards.in-scope-only | conforms | Surgical retire only; no gazer/consult apply |
| astral.standards.logging-via-utils | conforms | Untouched |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | Retire targets named meteorite GDL pair from AC5 |
| astral.standards.public-then-helpers | conforms | Extends existing public ensure helper |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | No transition code; priors in config |
| astral.state.job-prior-states-enforced | conforms | GDL priors from QUALIFIED; live claim surface matches |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — paths miss
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
(none)

### acceptable
1. Surgical delete only `evaluate_jd`@`METEORITE_NEW` — protects AC7 / JD_READY.
2. Prefer delete over update — avoids duplicate `(task_key, trigger_state)` collision.
3. Three qualify outcomes + fields schema — correct.
4. `auto_mode: False` until AST-1062 — sensible.
5. Self-assessment Single-Component / high / Medium — honest.

— Joan
context_tokens≈82000

#### ada — 2026-07-30T00:49:26.295Z
[plan-discuss] round=1 reply

Addressed Joan fix-now: Stage 1 Step 5 now extends `ensure_meteorite_dispatch_tasks` to **delete** live `evaluate_jd`@`METEORITE_NEW` rows after inserting `evaluate_jd`@`METEORITE_QUALIFIED` (surgical — does not touch `evaluate_jd`@`JD_READY`). Removed the old “leave stale row / cleanup later” decision. `src/core/dispatcher.py` added to Files Changed. Tip on publish-ref after this commit.

**Plan:** [docs/features/meteorite/ast-1060-meteorite-qualified-qualify-meteorite-config-dispatch.md](https://github.com/susansomerset/astral/blob/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch/docs/features/meteorite/ast-1060-meteorite-qualified-qualify-meteorite-config-dispatch.md)

#### joan — 2026-07-30T00:46:57.582Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1060
**Overall:** REVISE

**Notes:** Files Changed layer `data/admin` mapped to `docs` (unrecognized → docs). Tip `5acf0bb3`. Assignee stays Joan per validate-plan §8 — Chuckles restores Ada after wait.

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Gazer email → create (+ Playwright when links) | N/A — boundary: AST-1061 |
| 2 Dedupe on external job id | N/A — boundary: AST-1061 |
| 3 Land **METEORITE_NEW** pre-AI | Stage 1 frames state + keeps `job_create_state`; create/gazer ownership AST-1061/1056 |
| 4 `qualify_meteorite` claim NEW → enrich → **METEORITE_QUALIFIED** | Stages 1–2 = config/schema/dispatch/agent_task shell; apply N/A — AST-1062 |
| 5 Meteorite `evaluate_jd` claims **METEORITE_QUALIFIED** only | Stage 1 retargets config `trigger_state` + GDL priors — **blocked** (stale DB row; see fix-now) |
| 6 Bogus/404 → **METEORITE_FAILED_QUALIFY** (Jobs skipped) | Stage 1 state + SKIPPED manifests; apply mapping AST-1062 |
| 7 Non-meteorite qualify/scrape/GDL unchanged | Stage 1 explicitly leaves `qualify_job_listings` / normal priors alone |
| 8 Style D on ingest/qualify apply paths | N/A — boundary: AST-1061 / AST-1062 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 3 METEORITE_NEW pre-AI role | 1 (label/priors/create_state unchanged) |
| 4 qualify config/schema/dispatch half | 1–2 |
| 5 evaluate_jd from QUALIFIED only | 1 — incomplete without live-row retarget |
| 6 FAILED_QUALIFY state registration + skipped UI | 1 |
| 7 Non-meteorite smoke | 1 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 States, UI, GDL retarget, TASK_CONFIG, dispatch helpers | Purpose METEORITE_QUALIFIED insert; AC3–7 config half; Architectural `pattern.config` / priors |
| 2 agent_task.json Ruth shell | AC4 schema prompts; Boundaries (new task key, not editing `qualify_job_listings`) |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1060):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No rewrite flow |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1058` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Three qualify outcomes decided in plan; matches parent AC6 + ERROR sibling |
| orch.pipeline.plan-is-bible | conforms | Stages binding; siblings excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Chuckles restores Ada after wait |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | New task is unscored enrichment |
| astral.config.config-source-of-truth | conforms | States/schema/dispatch in config + agent_task JSON |
| astral.config.pass-threshold-vs-score-floor | conforms | evaluate_jd score_floor stays None; no mix-up |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src/features |
| astral.layers.import-direction | conforms | utils + repo admin JSON only |
| astral.layers.ui-config-driven-business-logic | conforms | Jobs manifests via config lists; no React enums |
| astral.standards.debug-contract-gated | conforms | No apply/ingest debug in this ticket |
| astral.standards.dry-and-focused-functions | conforms | Reuses ensure_meteorite_dispatch_tasks + qualify_job_listings shape |
| astral.standards.in-scope-only | conforms | Explicitly excludes gazer/consult apply |
| astral.standards.logging-via-utils | conforms | Untouched |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | States/triggers in JOB_STATES / METEORITE_DISPATCH_TASKS |
| astral.standards.public-then-helpers | conforms | Extends existing dispatch helpers |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.job-prior-states-enforced | needs-discussion | Priors correctly retarget GDL outcomes to QUALIFIED, but insert-only provision leaves a claimable stale evaluate_jd@METEORITE_NEW row (AC5) |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.single-gunicorn-worker

**Excluded:** astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.debug.no-repo-root-artifacts-dir, astral.debug.spikes-under-debug-dir, astral.docs.features-single-file-per-ticket, astral.git.engineer-test-tree-ban, astral.layers.core-vs-external-bright-line, astral.layers.scripts-exempt-from-layer-rules, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.state.core-decides-transitions, astral.state.no-daisy-chain-in-run, astral.ui.frontend-file-placement, astral.ui.naming-conventions — layers/paths miss plan Files Changed (utils + `data/admin`→docs).

## Findings

### fix-now
1. **Location:** Stage 1 step 3 Decision — “do not mutate existing DB rows” / accept stale `evaluate_jd`@`METEORITE_NEW`
   **Finding:** Parent AC5 and Boundaries require meteorite `evaluate_jd` claims/grades from **METEORITE_QUALIFIED** only and must **not** leave evaluate_jd claiming unenriched **METEORITE_NEW**. Today `ensure_meteorite_dispatch_tasks` keys on `(task_key, trigger_state)` and only inserts. Changing `METEORITE_DISPATCH_TASKS` evaluate_jd → `METEORITE_QUALIFIED` adds a new row and **leaves** the live `evaluate_jd`@`METEORITE_NEW` row. That row remains claimable (CLICK or if auto later). Retargeting `JOB_STATES` priors alone blocks lawful transition out of NEW into PASSED_JD — it does **not** stop the claim of unenriched NEW for grading. Parent law is about the claim surface, not only successful transitions.
   **Recommendation:** Add an explicit Stage 1 provision step that makes the live claim surface match config: for each candidate (and template), when config says `evaluate_jd`@`METEORITE_QUALIFIED`, **retire** `evaluate_jd`@`METEORITE_NEW` (update `trigger_state`, or delete old + keep insert of new). If that requires a narrow `ensure_meteorite_dispatch_tasks` / data helper, allow it — the current “no dispatcher body change” constraint cannot override AC5. Manual “Chuckles cleanup later” is not sufficient for Plan Approved.

### discuss
(none blocking beyond the needs-discussion statute note above — resolved by the same fix-now)

### acceptable
1. Three outcomes QUALIFIED / FAILED_QUALIFY / ERROR_QUALIFY — matches parent AC6 + error sibling note.
2. `scored: False` + `output_type: "fields"` enrichment schema — correct split from `qualify_job_listings` grades.
3. `auto_mode: False` until AST-1062 — sensible risk control.
4. Self-assessment Single-Component / high / Medium — honest.
5. Out of scope gazer/consult apply / tests — correct sibling split.

— Joan
context_tokens≈78000

#### ada — 2026-07-30T00:43:12.493Z
Plan published on `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch`.

**Plan:** [docs/features/meteorite/ast-1060-meteorite-qualified-qualify-meteorite-config-dispatch.md](https://github.com/susansomerset/astral/blob/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch/docs/features/meteorite/ast-1060-meteorite-qualified-qualify-meteorite-config-dispatch.md)

**Self-assessment**
- **Scope:** Single-Component — `JOB_STATES`/UI + GDL retarget + `TASK_CONFIG`/`METEORITE_DISPATCH_TASKS` for `qualify_meteorite` + Ruth `agent_task` shell; no gazer/consult apply.
- **Conf:** high — same meteorite state/dispatch/agent_task patterns as AST-1053/1054/1055; evaluate_jd trigger swap is explicit.
- **Risk:** Medium — wrong prior/`trigger_state` would leave GDL on unenriched METEORITE_NEW; mitigated by locked priors + `auto_mode: False` until AST-1062.

---

# AST-1060 — METEORITE_QUALIFIED + qualify_meteorite config/dispatch

**Linear:** [AST-1060](https://linear.app/astralcareermatch/issue/AST-1060/meteorite-qualified-qualify-meteorite-configdispatch-qualify-meteorite)
**Parent:** [AST-1058](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite) — Qualify Meteorite
**Publish ref:** `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch`

Registers **METEORITE_QUALIFIED** / **METEORITE_FAILED_QUALIFY** / **METEORITE_ERROR_QUALIFY**, updates UI manifests, reframes **METEORITE_NEW** as pre-AI entry, retargets meteorite `evaluate_jd` claim from **METEORITE_NEW** → **METEORITE_QUALIFIED** (config **and** live `dispatch_task` rows), and adds `TASK_CONFIG` + `agent_task` shell + meteorite `dispatch_task` row for `qualify_meteorite` claiming **METEORITE_NEW**. Does **not** own gazer Playwright ingest (AST-1061) or core/consult batch apply (AST-1062).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | New qualify states + UI; retarget GDL priors/`METEORITE_DISPATCH_TASKS` evaluate_jd trigger; `TASK_CONFIG["qualify_meteorite"]`; dispatch helper rules | utils |
| `src/core/dispatcher.py` | Extend `ensure_meteorite_dispatch_tasks` to retire stale `evaluate_jd`@`METEORITE_NEW` after insert | core |
| `data/admin/agent_task.json` | `qualify_meteorite` shell row (Ruth) | data/admin |

No `consult.py` / `meteorite.py` apply path, no gazer, no frontend TS, no `tests/` / bible (Betty after Code Complete).

## Stage 1: Qualify states, UI, GDL retarget, `qualify_meteorite` TASK_CONFIG + dispatch

**Done when:** Config imports with the three new states; GDL `evaluate_jd` meteorite dispatch claims **METEORITE_QUALIFIED** in config **and** on live rows after provision (no remaining `evaluate_jd`@`METEORITE_NEW`); `TASK_CONFIG["qualify_meteorite"]` and a `METEORITE_DISPATCH_TASKS` row claim **METEORITE_NEW**; Jobs In Review / Skipped manifests include the new states; non-meteorite qualify/`JOB_STATES` priors / `evaluate_jd`@`JD_READY` unchanged.

1. In `src/utils/config.py` `JOB_STATES`, **replace** the meteorite GDL block comment and entries so the chain is:

```python
    # AST-1052 / AST-1053 / AST-1058: parallel meteorite track (no CULTURE_READY hop).
    # METEORITE_NEW = pre-AI landing (create / gazer ingest). Ruth qualify_meteorite →
    # METEORITE_QUALIFIED (GDL entry). evaluate_jd claims METEORITE_QUALIFIED only (AST-1060).
    "METEORITE_NEW":                  {"prior_states": None},
    "METEORITE_QUALIFIED":            {"prior_states": ["METEORITE_NEW"]},
    "METEORITE_FAILED_QUALIFY":       {"prior_states": ["METEORITE_NEW"]},
    "METEORITE_ERROR_QUALIFY":        {"prior_states": ["METEORITE_NEW"]},
    "METEORITE_PASSED_JD":            {"prior_states": ["METEORITE_QUALIFIED"]},
    "METEORITE_FAILED_JD":            {"prior_states": ["METEORITE_QUALIFIED"]},
    "METEORITE_ERROR_EVALUATE_JD":    {"prior_states": ["METEORITE_QUALIFIED"]},
    "METEORITE_PASSED_DO":            {"prior_states": ["METEORITE_PASSED_JD"]},
    # … keep DO/GET/LIKE meteorite siblings exactly as today (priors unchanged beyond JD hop)
```

Keep **METEORITE_NEW** `prior_states: None` (create / ingest unrestricted entry). Do **not** remove or rename existing METEORITE_* GDL/LIKE states.

⚠️ **Decision — three qualify outcomes:** Pass = **METEORITE_QUALIFIED**; content/bogus/404 = **METEORITE_FAILED_QUALIFY** (parent AC6 / Jobs skipped); technical = **METEORITE_ERROR_QUALIFY** (mirrors `METEORITE_ERROR_EVALUATE_JD` naming + `ERROR_QUALIFY_JOB_LISTINGS` role). AST-1062 maps Ruth outcomes onto these three.

2. Update ordered Jobs UI lists in the same file:

- **`IN_REVIEW_STATES`:** insert `"METEORITE_QUALIFIED"` immediately after `"METEORITE_NEW"` (before `METEORITE_PASSED_JD`).
- **`JOBS_IN_REVIEW_UI_SECTIONS`:** after the `METEORITE_NEW` row, insert  
  `{"state": "METEORITE_QUALIFIED", "label": "Meteorite Qualified"}`.  
  Change the `METEORITE_NEW` label to `"Meteorite New (pre-AI)"`.
- **`SKIPPED_STATES`:** append `"METEORITE_FAILED_QUALIFY", "METEORITE_ERROR_QUALIFY"` next to the other meteorite fails (before or with the evaluate_jd fail pair is fine — both must appear exactly once).
- **`JOBS_SKIPPED_SECTION_ORDER`:** insert both near the FAILED_JOBLIST / ERROR_QUALIFY_JOB_LISTINGS cluster (after `METEORITE_ERROR_EVALUATE_JD` or before `FAILED_JOBLIST` — keep meteorite qualifies readable together).
- **`JOBS_SKIPPED_SECTION_LABELS`:**  
  `"METEORITE_FAILED_QUALIFY": "Meteorite Failed Qualify"`,  
  `"METEORITE_ERROR_QUALIFY": "Meteorite Error Qualify"`.
- Do **not** add grade-field maps for these states (no rubric grades until AST-1062 persists fields; same as bare `METEORITE_NEW` today).

3. Retarget meteorite GDL entry in `METEORITE_DISPATCH_TASKS`: change the `evaluate_jd` entry’s `"trigger_state"` from `"METEORITE_NEW"` to `"METEORITE_QUALIFIED"`. Keep `"score_floor": None` (ungated GDL entry, mirrors prior METEORITE_NEW / normal JD_READY).

4. Append a new first entry to `METEORITE_DISPATCH_TASKS` (before `evaluate_jd`):

```python
    {
        "task_key": "qualify_meteorite",
        "trigger_state": "METEORITE_NEW",
        "score_floor": None,
        "auto_mode": False,
        "batch_size": 30,
        "min_count": 1,
        "freq_hrs": 0,
    },
```

5. In `src/core/dispatcher.py`, extend `ensure_meteorite_dispatch_tasks` so the **live claim surface** matches config (parent AC5 / Boundaries — meteorite `evaluate_jd` must not claim unenriched **METEORITE_NEW**):

- Keep the existing insert loop over `METEORITE_DISPATCH_TASKS` (adds `evaluate_jd`@`METEORITE_QUALIFIED` and `qualify_meteorite`@`METEORITE_NEW` when missing).
- **After** inserts, scan `database.list_dispatch_tasks_for_candidate(cid)` and **retire** every row where `task_key == "evaluate_jd"` and `trigger_state == "METEORITE_NEW"` by calling `database.delete_dispatch_task(row["id"])` (thin wrapper `delete_dispatch_task` already exists in this module — use that).
- Do **not** delete `evaluate_jd`@`JD_READY` (or any other non-meteorite trigger). Only the stale meteorite pair `"METEORITE_NEW"`.
- Prefer **delete** over `update_dispatch_task(... trigger_state=METEORITE_QUALIFIED)` so a candidate that already received the new insert does not hit a duplicate `(task_key, trigger_state)` collision.
- Include `retired` (int) in the function’s return dict alongside `added` / `skipped` / `skipped_missing_config`.
- `provision_meteorite_dispatch_tasks` already calls `ensure_meteorite_dispatch_tasks` for template + every candidate with dispatch rows — no second provision entry-point; optionally sum `retired` into its return stats the same way it sums `added`.

⚠️ **Decision — retire inside `ensure_meteorite_dispatch_tasks`:** Joan fix-now: insert-only leaves a claimable stale row. Surgical delete of `evaluate_jd`@`METEORITE_NEW` (not a blanket “mismatched trigger” cleanup) satisfies AC5 without touching normal `evaluate_jd`@`JD_READY`. Config retarget alone is not enough.

6. In `TASK_CONFIG`, immediately after `"qualify_job_listings"`, add:

```python
    # AST-1058 / AST-1060: Ruth meteorite qualify (pre-AI → METEORITE_QUALIFIED).
    # Same claim/batch shape as qualify_job_listings; apply wiring is AST-1062.
    "qualify_meteorite": {
        "response_format": "json",
        "output_type": "fields",
        "scored": False,
        "response_schema": {
            "jobs": {
                "type": "list",
                "required": True,
                "items_schema": {
                    "astral_job_id":   {"type": "str", "required": True},
                    "company_job_id":  {"type": "str", "required": True},  # external job UUID
                    "job_title":       {"type": "str", "required": True},
                    "job_link":        {"type": "str", "required": True},
                    "jd_text":         {"type": "str", "required": True},  # visible JD content
                },
            },
        },
        "fallback_batch_size": 30,
        "pass_state": "METEORITE_QUALIFIED",
        "fail_state": "METEORITE_FAILED_QUALIFY",
        "error_state": "METEORITE_ERROR_QUALIFY",
        "context_format": "qualify_meteorite_{index}",
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
        "agent_task": "qualify_meteorite",
    },
```

⚠️ **Decision — `scored: False` + `output_type: "fields"`:** Parent AC is enrichment (UUID/title/link/JD), not grade vectors. Do **not** reuse `grades_encoded_meta` / `joblist_rubric`. AST-1062 owns persist + transition; schema keys above are the contract.

⚠️ **Decision — do not edit `qualify_job_listings` TASK_CONFIG or normal `NEW`/`PASSED_JOBLIST` priors:** Non-meteorite path must stay byte-stable (parent AC7 smoke).

7. Wire dispatch defaults for the new task key:

- In `_dispatch_trigger_state_for_task_key`, add `if task_key == "qualify_meteorite": return "METEORITE_NEW"` (near the `qualify_job_listings` → `"NEW"` branch).
- In `_dispatch_entity_type_for_task_key`, add `"qualify_meteorite"` to the job-entity tuple that already lists `"qualify_job_listings", "evaluate_jd", …`.
- Add `"qualify_meteorite"` to `_DISPATCH_BATCH_CALL_MODE_ONE` (next to `"qualify_job_listings"`).

8. Do **not** edit `consult.py`, `agent.py`, batch runners, `meteorite.py`, gazer, or frontend. Do **not** set `auto_mode: True`. Do **not** change `METEORITE_CONFIG["job_create_state"]` (stays **METEORITE_NEW**). The only `dispatcher.py` change is Step 5 (`ensure_meteorite_dispatch_tasks` + optional provision stats).

**Done when (recheck):** `JOB_STATES["METEORITE_PASSED_JD"]["prior_states"] == ["METEORITE_QUALIFIED"]`; `METEORITE_DISPATCH_TASKS` has `qualify_meteorite`@`METEORITE_NEW` and `evaluate_jd`@`METEORITE_QUALIFIED`; after `ensure_meteorite_dispatch_tasks(cid)` a candidate that previously had `evaluate_jd`@`METEORITE_NEW` has that row gone and `evaluate_jd`@`METEORITE_QUALIFIED` present; `evaluate_jd`@`JD_READY` untouched; `TASK_CONFIG["qualify_meteorite"]["pass_state"] == "METEORITE_QUALIFIED"`; `_dispatch_trigger_state_for_task_key("qualify_meteorite") == "METEORITE_NEW"`; `python3 -m py_compile src/utils/config.py src/core/dispatcher.py` succeeds.

## Stage 2: `agent_task.json` shell for `qualify_meteorite`

**Done when:** `data/admin/agent_task.json` has a `current: 1` row for `task_key == "qualify_meteorite"` (Ruth, Job Review grouping); JSON still parses as a flat-row array; prompts describe enrichment (UUID / title / link / visible JD) without inventing a new batch pattern.

1. Append one object to `data/admin/agent_task.json` (flat scalars only), modeled on the existing `qualify_job_listings` row:

| Field | Value |
|-------|-------|
| `task_key` | `qualify_meteorite` |
| `task_key_uuid` | new UUID4 string |
| `current` | `1` |
| `agent_id` | `college_intern_ruth` (same as `qualify_job_listings`) |
| `task_group_order` | `4000` |
| `task_group_name` | `Job Review` |
| `task_name` | `Qualify Meteorite` |
| `task_seq` | place after listing qualify (e.g. `2.5` or next free seq in that group) |
| `system_prompt` / `cache_prompt_b|c|d` / `nocache_prompt` / `run_next` | `""` |
| `updated_at` | ISO-ish UTC timestamp string |

2. **`user_prompt` / `cache_prompt` shell** (keep short; AST-1062 / future prompt polish may refine):

- Instruct Ruth that each item is a **meteorite** job already holding raw / visible text (email body, forward, or Playwright-fetched page text) — **not** a normal job-board listing row.
- Require a JSON jobs list matching `TASK_CONFIG["qualify_meteorite"]["response_schema"]` keys: `astral_job_id`, `company_job_id` (employer external job UUID for dedupe), `job_title`, `job_link` (primary URL), `jd_text` (authoritative visible JD).
- Success path assumes usable extract; unusable / 404 / bogus pages are a fail outcome for the apply layer (do not invent grade vectors).
- Do **not** copy the seven-step joblist grading / vector rubric from `qualify_job_listings` — this key is enrichment-only.

⚠️ **Decision — prompts only in `agent_task.json`:** Same as AST-1055; startup `apply_repo_admin_json` ships the row. No parallel `_taskprompts` file.

3. Do **not** hand-edit the live DB; do **not** invent consult routes.

**Done when (recheck):** `qualify_meteorite` present in the JSON array; `agent_id` is Ruth; prompts mention meteorite enrichment + the five schema fields; `python3 -c "import json; json.load(open('data/admin/agent_task.json'))"` succeeds.

## Out of scope (do not implement here)

- Gazer email → Playwright → create / dedupe (AST-1061).
- `qualify_meteorite` consult/core batch apply, Style D on apply, persist of UUID/title/link/JD (AST-1062).
- Editing non-meteorite `qualify_job_listings` behavior or prompts.
- Frontend React enums (manifest is config-driven).
- `tests/` / `docs/test-bible/**` (Betty after Code Complete).
- Deleting or rewriting normal-track `evaluate_jd`@`JD_READY` (or any non-`METEORITE_NEW` evaluate_jd row).

## Self-Assessment

**Scope:** `Single-Component` — `config.py` state/dispatch/TASK_CONFIG + `ensure_meteorite_dispatch_tasks` retire + one `agent_task.json` row; no consult apply / gazer / UI TS.

**Conf:** `high` — mirrors AST-1053/1054/1055 patterns; Joan fix-now is a surgical delete of one stale `(task_key, trigger_state)` using existing `delete_dispatch_task`.

**Risk:** `Medium` — wrong retire predicate could drop normal `evaluate_jd`@`JD_READY`; mitigated by hard-matching only `trigger_state == "METEORITE_NEW"`. Stale claim surface is closed by the retire step (AC5).

## Rules self-review

- **§2.1 / no-hardcoded-sets / config-source-of-truth:** All states, task keys, schema, dispatch triggers in config / repo agent_task JSON; retire target is the prior meteorite GDL pair named in AC5.
- **§2.6 / job-prior-states-enforced:** GDL outcomes only from **METEORITE_QUALIFIED**; claim surface for meteorite `evaluate_jd` matches that; qualify outcomes only from **METEORITE_NEW**.
- **§3.3 imports:** Dispatcher already imports data + `METEORITE_DISPATCH_TASKS` / `TASK_CONFIG`; no new core↔UI edges.
- **In-scope only:** No gazer / consult apply / tests / bible.

## Revisions

**Revision 1 — 2026-07-30**
Driven by: Joan `[plan-discuss] round=1 concern` / plan-rubric fix-now — insert-only provision leaves claimable stale `evaluate_jd`@`METEORITE_NEW` (AC5).
Changes: Added `src/core/dispatcher.py` to Files Changed; Stage 1 Step 5 retires that pair via `delete_dispatch_task` after inserts; removed the old “do not mutate DB rows” decision and the out-of-scope “cleanup later” line; Done-when / Self-Assessment / Rules updated for live claim-surface match.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch`
**Plan path:** `docs/features/meteorite/ast-1060-meteorite-qualified-qualify-meteorite-config-dispatch.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `53df9c81` | JOB_STATES/UI + qualify_meteorite TASK_CONFIG/dispatch + retire evaluate_jd@METEORITE_NEW |
| 2 | `c055015f` | data/admin agent_task.json Ruth shell |

**Tip:** `6b89952b364a157cb9edc53a415cf19c3a2944d9` on `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1060
**Publish ref:** `6f15565094e8c7825e229b35e7c8e71094cc1ce0` (`origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch`)
**Overall:** DISCUSS

### What’s solid
- Qualify states + priors + UI manifests; `qualify_meteorite` TASK_CONFIG / METEORITE_DISPATCH_TASKS; evaluate_jd@METEORITE_QUALIFIED.
- Surgical retire of `evaluate_jd`@`METEORITE_NEW` in `ensure_meteorite_dispatch_tasks` (JD_READY untouched); provision sums `retired`.
- Ruth `agent_task` shell; Betty tests/bible on tip after qa-handoff catalog lock fix.

### Issues
- **discuss (straggler ×3):** Joan excluded at plan time; in-scope on three-dot vs `origin/dev` via plan docs + Betty tests/bible — all substance **conforms**:
  - `astral.debug.spikes-under-debug-dir`
  - `astral.docs.features-single-file-per-ticket`
  - `astral.git.engineer-test-tree-ban`

### Recommended actions
- Ada: acknowledge stragglers → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-30  
**Commit:** `resolve(AST-1060): — clean`

### Against Radia review (`3f8f6fc4` / Overall DISCUSS)

- **fix-now:** none — no product changes.
- **discuss (straggler ×3):** Acknowledged. Joan excluded at plan time; Radia re-checked on three-dot vs `origin/dev` via plan docs + Betty tests/bible — all substance **conforms** (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`). No further action.
- **advisory:** none.

Stages 1–2 product + Betty manifest green @ `6f155650`; Radia docs intake @ `3f8f6fc4` already on publish-ref before this resolve commit.

