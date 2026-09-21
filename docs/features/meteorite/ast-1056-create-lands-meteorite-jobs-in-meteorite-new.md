<!-- linear-archive: AST-1056 archived 2026-08-07 -->

## Linear archive (AST-1056)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1056/create-lands-meteorite-jobs-in-meteorite-new-processing-meteorites  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1052 — Processing meteorites  
**Blocked by / blocks / related:** parent: AST-1052

### Description

## What this implements

Owns retargeting meteorite create (Manage Email **Create** / create path / `METEORITE_CONFIG` create default) so new jobs start in **METEORITE_NEW**. After #1. Does **not** own GDL processing or Recommended section.

## In scope

- [X] `pattern.config.config-block` — `METEORITE_CONFIG["job_create_state"]` owns create landing
- [X] `astral.config.config-source-of-truth` — landing state from config only; core reads the key
- [X] `astral.state.job-prior-states-enforced` — insert into `METEORITE_NEW` (`prior_states: None`) as lawful unrestricted entry
- [X] `astral.standards.no-hardcoded-sets` — do not hardcode `METEORITE_NEW` in create call path

## Considered but excluded

* `pattern.state.entity-state-transitions` / meteorite `JOB_STATES` registration — AST-1053 (`src/utils/config.py` JOB_STATES)
* `pattern.batch.entity-claim-process-release` / dispatch `score_floor` 0 — AST-1054 (dispatcher / TASK_CONFIG)
* company-absent `meteorite_like` / meteorite upshot agent_task prompts — AST-1055 (`src/utils/config.py` agent tasks)
* Recommended Meteorites section — AST-1057 (`src/ui/` Recommended)
* `astral.batch.claim-process-release` — create is not a claim batch
* Universal `orch.*` — not listed per-child

## Acceptance criteria

- [X] 6. Manage Email **Create** (meteorite create path) inserts jobs in **METEORITE_NEW**.

## Boundaries

- [X] Does **not** own GDL states (sibling 1), dispatch (sibling 2), agent prompts (sibling 3), or Recommended section (sibling 5).
- [X] Does **not** change `job_create_latest_score` or normal (non-meteorite) `JD_READY` create/scrape paths.
- [X] Does **not** edit test-tree / bible (Betty).

## Notes for planning

After AST-1053. Retarget from JD_READY create default via `METEORITE_CONFIG["job_create_state"]` only; API/inbox already propagate core `state`.

## Git branch (authoritative)

`origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`

### Comments

#### chuckles — 2026-07-29T22:23:23.363Z
[merge-child] blocked:

`validate-sub-log` failed on `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`:
- **duplicate `merge-tests(AST-1056)`** count=2 (`62ae4183`, `a84a6d5e`) — @Betty White amend on tests; one `merge-tests` only
- also present: `Merge remote-tracking branch 'origin/ftr/…'` (`473dd4d8`) — forbidden on sub; @Hedy Lamarr restack onto current `origin/ftr/AST-1052-processing-meteorites` without pull-merge commits
- sub not ancestor-stacked on current ftr tip (`93a76295` includes AST-1054)

Stay **User Testing**. Chuckles will re-run merge-child after republish.

— Chuckles

#### radia — 2026-07-29T22:21:06.980Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1056
**Publish ref:** `5d0f3615fb38dc63172fc7b0ad5258a06543e823` (`origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new` — layers `{core, docs, utils}`; product `src/utils/config.py` (`job_create_state` → `METEORITE_NEW`) + `src/core/meteorite.py` docstring honesty; Betty tests/bible + stacked AST-1053 plan.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| `astral.agent.confidence-bounds` | scoped | conforms | No agent confidence changes |
| `astral.agent.do-task-delegation` | scoped | conforms | No do_task changes |
| `astral.agent.grade-vector-validation` | scoped | conforms | No grade vectors |
| `astral.batch.batch-id-first` | scoped | conforms | Create is not a claim batch |
| `astral.batch.batch-id-format` | scoped | conforms | Untouched |
| `astral.batch.claim-process-release` | scoped | conforms | Create is not claim-process-release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | No agent_data edits |
| `astral.config.config-source-of-truth` | scoped | conforms | Landing state only via METEORITE_CONFIG key |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | job_create_latest_score unchanged; score_floor sibling |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Plan docs under docs/features/; no spikes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single AST-1056 plan (+ stacked 1053 plan) |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test()/merge-tests; engineer code() owns src+features |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | test() owns tests/bible; engineer code() product only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | No external I/O |
| `astral.layers.import-direction` | scoped | conforms | core already imports utils; no new imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers miss (['scripts']); paths miss (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Config key only; no UI |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | No coat-check |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | No consult edits |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/**']) |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No data-layer edits |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers miss (['data']); paths miss (['src/data/**']) |
| `astral.standards.debug-contract-gated` | scoped | conforms | No new ungated debug lines |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Config retarget + docs only |
| `astral.standards.in-scope-only` | scoped | conforms | GDL/dispatch/prompts/Recommended deferred |
| `astral.standards.logging-via-utils` | scoped | conforms | Logging untouched |
| `astral.standards.no-cross-contamination` | scoped | conforms | Meteorite create path only; JD_READY scrape untouched |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Landing state in METEORITE_CONFIG; core reads key |
| `astral.standards.public-then-helpers` | scoped | conforms | No API surface reorder |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data |
| `astral.state.core-decides-transitions` | scoped | conforms | Direct insert carve-out for unrestricted entry |
| `astral.state.job-prior-states-enforced` | scoped | conforms | METEORITE_NEW prior_states None; assert in JOB_STATES |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No run_next |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | config.py path only; no worker change |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | merge-tests(AST-1056) SHAs on tip |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | Work on sub/* only |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1052/AST-1056-… |
| `orch.git.merge-on-checkout` | universal | conforms | No conflicting checkout rewrite |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No rewrite ops |
| `orch.git.no-dev-agent-branches` | universal | conforms | Ticket sub publish-ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | astral-AST-1052 |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | No product decision gap |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match tip; boundaries held |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty owns tests/bible |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Assignee remains Hedy |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Role-appropriate paths per vocabulary |

## Pattern conformance

- `pattern.config.config-block` — conforms (`METEORITE_CONFIG["job_create_state"]` owns landing)
- Cited statutes covered in Statutes checked

## Plan adherence

Stages 1–2 match tip: config retarget only; create body still reads `METEORITE_CONFIG`; no hardcode; `job_create_latest_score` unchanged; direct insert carve-out retained. Self-Assessment `minor` matches footprint. Boundaries held vs AST-1053/1054/1055/1057.

## Findings

### fix-now
(none)

### discuss
1. **straggler ×3** — Joan excluded at plan time; in-scope on three-dot vs `origin/dev` (all substance **conforms**):
   - `astral.debug.spikes-under-debug-dir`
   - `astral.docs.features-single-file-per-ticket`
   - `astral.git.engineer-test-tree-ban`

### advisory
(none)

### What’s solid
- Landing via config key; API/inbox already propagate `payload["state"]`.

### Recommended actions
- Hedy: acknowledge stragglers → resolve-child → User Testing.

**Notes:** Joan plan-rubric APPROVED. Docs append @ `5d0f3615`.

context_tokens≈22000

#### radia — 2026-07-29T22:20:23.647Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1056
**Publish ref:** `5d0f3615fb38dc63172fc7b0ad5258a06543e823` (`origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new` — layers `{core, docs, utils}`; product delta vs AST-1053 tip is `METEORITE_CONFIG["job_create_state"]` + `meteorite.py` docs.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| `astral.agent.confidence-bounds` | scoped | conforms | No agent confidence changes |
| `astral.agent.do-task-delegation` | scoped | conforms | No do_task changes |
| `astral.agent.grade-vector-validation` | scoped | conforms | No grade vectors |
| `astral.batch.batch-id-first` | scoped | conforms | Create is not a claim batch |
| `astral.batch.batch-id-format` | scoped | conforms | Untouched |
| `astral.batch.claim-process-release` | scoped | conforms | Out of scope; create not claim |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | No agent_data edits |
| `astral.config.config-source-of-truth` | scoped | conforms | Landing via METEORITE_CONFIG job_create_state only |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | job_create_latest_score untouched; score_floor is AST-1054 |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Plan docs under docs/features/; no spikes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single AST-1056 plan (+ stacked 1053 plan) |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test()/merge-tests; engineer code() owns src+features |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | test() owns tests/bible; engineer code() product only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | No external I/O |
| `astral.layers.import-direction` | scoped | conforms | core already imports utils; no new imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers miss (['scripts']); paths miss (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Config key only; no UI |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | No coat-check |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | No consult edits on this tip product |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/**']) |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No data-layer edits |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers miss (['data']); paths miss (['src/data/**']) |
| `astral.standards.debug-contract-gated` | scoped | conforms | No new ungated debug lines |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Config retarget + docstring only |
| `astral.standards.in-scope-only` | scoped | conforms | GDL/dispatch/prompts/Recommended deferred |
| `astral.standards.logging-via-utils` | scoped | conforms | Logging untouched |
| `astral.standards.no-cross-contamination` | scoped | conforms | Meteorite create path only; JD_READY scrape untouched |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | No hardcoded METEORITE_NEW in create body |
| `astral.standards.public-then-helpers` | scoped | conforms | No API surface reorder |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data |
| `astral.state.core-decides-transitions` | scoped | conforms | Direct insert for unrestricted entry; not transition |
| `astral.state.job-prior-states-enforced` | scoped | conforms | METEORITE_NEW prior_states None; assert in JOB_STATES |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No run_next |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | config.py path only; no worker change |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | merge-tests(AST-1056) SHAs on tip |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | Work on sub/* only |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1052/AST-1056-… |
| `orch.git.merge-on-checkout` | universal | conforms | No conflicting checkout rewrite |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No rewrite ops |
| `orch.git.no-dev-agent-branches` | universal | conforms | Ticket sub publish-ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | astral-AST-1052 |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | No product decision gap |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match tip |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty owns tests/bible |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Assignee remains Hedy |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Role-appropriate paths per vocabulary |

## Pattern conformance

- `pattern.config.config-block` — conforms (`METEORITE_CONFIG["job_create_state"]` owns landing)
- Cited statutes covered in Statutes checked

## Plan adherence

Stages 1–2 match tip: config retarget to `METEORITE_NEW`, docstring honesty, create body still reads config (no hardcode). Self-Assessment `minor` matches footprint. Boundaries held (no GDL/dispatch/prompts/Recommended). `job_create_latest_score` unchanged.

## Findings

### fix-now
(none)

### discuss
1. **straggler ×3** — Joan excluded at plan time; in-scope on three-dot vs `origin/dev` (all substance **conforms**):
   - `astral.debug.spikes-under-debug-dir`
   - `astral.docs.features-single-file-per-ticket`
   - `astral.git.engineer-test-tree-ban`

### advisory
(none)

### What’s solid
- Create lands via config key; unrestricted-entry insert carve-out retained.

### Recommended actions
- Hedy: acknowledge stragglers → resolve-child → User Testing.

**Notes:** Joan plan-rubric verdict attached (APPROVED). Docs append @ `5d0f3615`.

context_tokens≈22000

#### betty — 2026-07-29T22:16:13.266Z
[check-linear]

Cleared Hedy [qa-handoff]: collection IDs were wrong on the prior manifest.

**Fixes**
- Pytest node: `TestAst1049InboxCreateJob` → `TestAst1049CreateMeteoriteJobFromInboxMessage`
- Dropped `.tsx` from `run_component_tests.sh`; Vitest via `npm run test:component`
- Restored `TestAst1056MeteoriteCreateLanding` + `METEORITE_NEW` landing asserts overwritten on `tests` tip

**Republished command:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1056MeteoriteCreateLanding \
  tests/component/utils/test_config.py::TestAst1041MeteoriteConfig \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates::test_non_meteorite_gdl_and_recommended_untouched \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  tests/component/ui/api/test_api_meteorite.py \
  tests/component/core/test_inbox.py::TestAst1049CreateMeteoriteJobFromInboxMessage \
  tests/component/ui/api/test_api_inbox.py::TestAst1049InboxCreateJobApi \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx
```

**Publish:** `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new` @ `a84a6d5e`
`merge-tests(AST-1056): origin/tests 7f0eef8e`

**Bible shasums on publish-ref:**
- `docs/test-bible/utils/config.md` `ddafe6b10274802e37a2a98fb5c65ac96da23cd0`
- `docs/test-bible/core/meteorite.md` `6b6f1e8841451945e5528f66b6e272baf5403da7`

Assignee → Hedy for `test-child`. Stay Tests Ready.

#### hedy — 2026-07-29T22:12:28.339Z
[qa-handoff]

Manifest command fails at **collection** (exit 4) — no product failures yet; runner never executes cases.

**Command (as posted):**
```bash
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1056MeteoriteCreateLanding \
  tests/component/utils/test_config.py::TestAst1041MeteoriteConfig \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates::test_non_meteorite_gdl_and_recommended_untouched \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  tests/component/ui/api/test_api_meteorite.py \
  tests/component/core/test_inbox.py::TestAst1049InboxCreateJob \
  tests/component/ui/api/test_api_inbox.py::TestAst1049InboxCreateJobApi \
  tests/component/frontend/pages/test_AdminManageEmail.test.tsx \
  -q
```

**Errors:**
1. `tests/component/core/test_inbox.py::TestAst1049InboxCreateJob` — **no such class**. Actual create class on tip is `TestAst1049CreateMeteoriteJobFromInboxMessage` (strip/extract is `TestAst1049StripExtractEmailHtml`).
2. `tests/component/frontend/pages/test_AdminManageEmail.test.tsx` — pytest/`run_component_tests.sh` does not collect this Vitest `.tsx` file (`ERROR: not found`).

**Why test/manifest (not product):** collection ID / runner mismatch vs files Betty already revised on `62ae4183`. Product tip unchanged from Code Complete (`b8850e8e`).

**Need from Betty:** republish runnable manifest (correct inbox node id; drop or split frontend to the Vitest command used elsewhere) + reassign Hedy.

@Betty White

— Hedy

#### betty — 2026-07-29T22:11:19.444Z
1. `tests/component/utils/test_config.py::TestAst1056MeteoriteCreateLanding` — `job_create_state` → `METEORITE_NEW` + unrestricted entry
2. Revised `TestAst1041MeteoriteConfig` — landing assert flip
3. Revised `TestAst1053MeteoriteGdlJobStates::test_non_meteorite_gdl_and_recommended_untouched` — create smoke removed (superseded)
4. Revised `TestAst1042CreateMeteoriteJob` — insert asserts config landing (`METEORITE_NEW`)
5. Revised API/inbox/Manage Email create mocks — `METEORITE_NEW` honesty

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1056MeteoriteCreateLanding \
  tests/component/utils/test_config.py::TestAst1041MeteoriteConfig \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates::test_non_meteorite_gdl_and_recommended_untouched \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  tests/component/ui/api/test_api_meteorite.py \
  tests/component/core/test_inbox.py::TestAst1049InboxCreateJob \
  tests/component/ui/api/test_api_inbox.py::TestAst1049InboxCreateJobApi \
  tests/component/frontend/pages/test_AdminManageEmail.test.tsx \
  -q
```

**Pass:** pytest green on tip.

**Broken/revised:** AST-1041/1042/1053 `JD_READY` create landing asserts; passthrough mock states.
**Integration:** none.

**Publish:** `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new` @ `62ae4183`
`merge-tests(AST-1056): origin/tests 4f08e590`

**Bible shasums on publish-ref:**
- `docs/test-bible/utils/config.md` `a257b3ddc68732d6d73ad68a781b2fa9b50763ff`
- `docs/test-bible/core/meteorite.md` `cabe4688815b3a33f2feb233706f619421ea4511`

#### joan — 2026-07-29T22:02:41.233Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1056
**Overall:** APPROVED
**Plan tip:** `f51a93ed6b2a03ce659b76629df72f45501a55a6` @ `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`
**Layers:** utils, core | **Change types:** modify

## Traceability

### Parent AC → plan stages

| Parent AC | Mapping |
|-----------|---------|
| AC1 METEORITE_* JOB_STATES | N/A — AST-1053 (dependency; already on ftr) |
| AC2 dispatch score_floor 0 | N/A — AST-1054 |
| AC3 meteorite_like / no CULTURE | N/A — AST-1055 |
| AC4 meteorite upshot | N/A — AST-1055 |
| AC5 Recommended Meteorites | N/A — AST-1057 |
| AC6 Create → METEORITE_NEW | Stages 1–2 (config key + docstring honesty; call path already reads config) |
| AC7 fail states + non-meteorite smoke | N/A — boundary (no GDL/vetted create edits) |
| AC8 Style D debug | N/A — no new processing paths; existing debug in ensure/create untouched |

### Child AC → plan stages

| Child AC | Stages |
|----------|--------|
| AC6 Manage Email Create inserts METEORITE_NEW | 1 (landing key), 2 (docs; runtime body already config-driven) |

### Plan stages → definition

| Stage | Definition |
|-------|------------|
| 1 Config `job_create_state` → METEORITE_NEW | Purpose/Functional: Create lands METEORITE_NEW; Architectural config-block |
| 2 Docstring honesty in meteorite.py | Keeps config SoT / no hardcode; documents unrestricted entry insert |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | Test-tree out of scope (Betty) |
| orch.git.commit-vocabulary | conforms | No commit ops in plan |
| orch.git.flow-direction-inviolable | conforms | sub under AST-1052 |
| orch.git.ftr-sub-topology | conforms | Publish ref matches Git table |
| orch.git.merge-on-checkout | conforms | No alternate merge strategy |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Uses sub/* |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-1052 |
| orch.git.three-permanent-branches | conforms | No permanent-branch mutation |
| orch.pipeline.call-susan-for-product-decisions | conforms | No product decision gap |
| orch.pipeline.plan-is-bible | conforms | Stages are implementation bible |
| orch.pipeline.project-scoped-queues | conforms | Single child in Meteorite project |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready path |
| orch.roles.archie-approves-statutes | conforms | No statute authorship |
| orch.roles.betty-owns-test-tree | conforms | Explicit Betty assert flips |
| orch.roles.chuckles-never-ticket-assignee | conforms | N/A plan content |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer Hedy per parent Team |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No agent confidence changes |
| astral.agent.do-task-delegation | conforms | No do_task changes |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | Create is not a claim batch |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Explicitly out of scope |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data edits |
| astral.config.config-source-of-truth | conforms | Landing state only via METEORITE_CONFIG key |
| astral.config.pass-threshold-vs-score-floor | conforms | Leaves job_create_latest_score alone; score_floor is sibling |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src + feature plan |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O |
| astral.layers.import-direction | conforms | core already imports utils; no new imports |
| astral.layers.ui-config-driven-business-logic | conforms | Config key only; no UI |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult edits |
| astral.standards.data-raises-caller-logs | conforms | No data-layer edits |
| astral.standards.debug-contract-gated | conforms | No new ungated debug lines |
| astral.standards.dry-and-focused-functions | conforms | No new create path; config retarget only |
| astral.standards.in-scope-only | conforms | GDL/dispatch/prompts/Recommended deferred |
| astral.standards.logging-via-utils | conforms | Logging untouched |
| astral.standards.no-cross-contamination | conforms | Meteorite create path only; JD_READY scrape untouched |
| astral.standards.no-hardcoded-sets | conforms | Explicitly refuses hardcoding METEORITE_NEW in core |
| astral.standards.public-then-helpers | conforms | No API surface reorder |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.state.core-decides-transitions | conforms | Create stays direct insert (not transition); lawful for unrestricted entry |
| astral.state.job-prior-states-enforced | conforms | METEORITE_NEW prior_states None; assert in JOB_STATES |
| astral.state.no-daisy-chain-in-run | conforms | No run_next |
| astral.ui.single-gunicorn-worker | conforms | config.py path only; no worker change |

## Considered and excluded

**Considered:** all Statute verdicts rows (18 universal + 29 scoped).

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — docs layer/paths miss
- astral.git.engineer-test-tree-ban — tests paths miss
- astral.layers.scripts-exempt-from-layer-rules — scripts miss
- astral.patterns.require-auth-on-protected-endpoints — ui miss
- astral.standards.database-header-inventory — data miss
- astral.ui.frontend-file-placement — ui miss
- astral.ui.naming-conventions — ui miss

## Findings

None fix-now.

- **acceptable** — Scope labeled `minor` (vs Single-Component); change set is genuinely one config key + docs; assessment honest.
- **acceptable** — Keeps `job_create_latest_score` at 10.0; parent AC6 is landing state only; score-floor is AST-1054.

## R6 checklist (abbrev)

Definition fidelity OK (AC6 only); config SoT OK; no UI/API creep (propagates existing payload.state); priors/unrestricted entry OK; self-assessment Conf high / Risk Medium honest.

— Joan
context_tokens≈68000

#### hedy — 2026-07-29T22:00:56.590Z
Plan published on `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new` @ `f51a93ed`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new/docs/features/meteorite/ast-1056-create-lands-meteorite-jobs-in-meteorite-new.md

**Self-assessment**
- **Scope:** `minor` — one `METEORITE_CONFIG` key retarget (`job_create_state` → `METEORITE_NEW`) plus docstring honesty in `src/core/meteorite.py`; create body already reads the config key.
- **Conf:** `high` — AST-1053 already registered unrestricted `METEORITE_NEW` on ftr; API/inbox/Manage Email Create need no wiring changes.
- **Risk:** `Medium` — wrong landing state puts meteorite jobs on the wrong GDL trail; blast radius stays the meteorite create path only.

— Hedy

---

# AST-1056 — Create lands meteorite jobs in METEORITE_NEW

**Linear:** [AST-1056](https://linear.app/astralcareermatch/issue/AST-1056/create-lands-meteorite-jobs-in-meteorite-new-processing-meteorites)
**Parent:** [AST-1052](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites) — Processing meteorites
**Publish ref:** `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`

Retarget meteorite job create so Manage Email **Create** / `POST …/meteorite/jobs` / `create_meteorite_job` inserts new jobs in **METEORITE_NEW** (meteorite GDL entry) instead of the AST-1042 default **JD_READY**. Config owns the landing state; core already reads `METEORITE_CONFIG["job_create_state"]`. Does **not** own GDL state registration, dispatch rows, agent prompts, or Recommended Meteorites.

**Depends on:** AST-1053 (`METEORITE_NEW` in `JOB_STATES` with `prior_states: None`) — already on `origin/ftr/AST-1052-processing-meteorites` / this sub after merge.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Set `METEORITE_CONFIG["job_create_state"]` → `"METEORITE_NEW"`; refresh adjacent comments | utils |
| `src/core/meteorite.py` | Update module + `create_meteorite_job` docstrings to name **METEORITE_NEW** / config key (no call-path logic change) | core |

No API, inbox, UI, dispatcher, or Recommended edits. Do **not** edit `tests/` or `docs/test-bible/**` (Betty).

## Stage 1: Config create landing → METEORITE_NEW

**Done when:** `METEORITE_CONFIG["job_create_state"] == "METEORITE_NEW"`, the existing `assert … in JOB_STATES` still passes at import, and comments no longer claim JD_READY as the create default. No dispatcher / Recommended / GDL-state edits.

1. In `src/utils/config.py`, in the `METEORITE_CONFIG` block (after AST-1041 company template keys), change:

```python
    # AST-1042 / AST-1056 job-create defaults (consumed by create_meteorite_job)
    "job_create_state": "METEORITE_NEW",
    "job_create_latest_score": 10.0,
```

Keep `"job_create_latest_score": 10.0` unchanged (synthetic score stand-in; meteorite dispatch `score_floor` 0 is sibling AST-1054 — out of scope).

2. Update the block comment immediately above `METEORITE_CONFIG` so it no longer says create defaults are **JD_READY**. Replace the JD_READY phrase with **METEORITE_NEW** (meteorite GDL entry / AST-1056). Leave company-ensure commentary intact.

3. Do **not** change `JOB_STATES`, `IN_REVIEW_STATES`, `SKIPPED_STATES`, `PASSED_SCORE_GATED_STATES`, `RECOMMENDED` priors, `TASK_CONFIG`, or any `DISPATCH_*` tables.

⚠️ **Decision — config-only landing retarget:** `create_meteorite_job` already assigns `state = METEORITE_CONFIG["job_create_state"]` and inserts via `save_job` (AST-1042 create carve-out). Hardcoding `"METEORITE_NEW"` in core would violate `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets`. Do not invent a second create path.

⚠️ **Decision — keep direct insert (no `transition_job_state`):** `METEORITE_NEW` has `prior_states: None` (AST-1053), so first-write insert is a lawful unrestricted entry (same shape as `ingest_jobs` → `NEW`). Do not route create through `transition_job_state`.

⚠️ **Decision — leave `job_create_latest_score` at 10.0:** Parent AC6 is landing state only. Score-floor behavior for meteorite GDL is AST-1054.

## Stage 2: Docstring honesty in `meteorite.py`

**Done when:** Module and `create_meteorite_job` docs describe landing via `METEORITE_CONFIG["job_create_state"]` (**METEORITE_NEW** after Stage 1); create still inserts without `transition_job_state`; runtime body unchanged except docs.

1. In `src/core/meteorite.py`, rewrite the module docstring so it no longer claims jobs land in **JD_READY**. State that API-facing create inserts into `METEORITE_CONFIG["job_create_state"]` (meteorite GDL entry **METEORITE_NEW** after AST-1056), with synthetic `latest_score` from `job_create_latest_score`. Keep: lazy-ensure company, no email ingest / admin UI ownership in this module’s ensure path, leave-in-place rows.

2. Rewrite `create_meteorite_job`’s docstring:

- Summary line: insert a job from raw HTML into `METEORITE_CONFIG["job_create_state"]` (not a hardcoded **JD_READY** name).
- Carve-out paragraph: first write inserts directly into that config state via `save_job` (same pattern as ingest → `NEW`); do **not** call `transition_job_state`. Note that **METEORITE_NEW** is unrestricted (`prior_states: None`); do **not** expand normal `JD_READY` priors and do **not** invent a new job state on this ticket.
- Returns block: keep the same keys (`astral_job_id`, `company`, `state`, `latest_score`, `company_inserted`, `job`).

3. Do **not** change the function body: still read `state` / `score` from `METEORITE_CONFIG`, still two-step `save_job` + `latest_score` update, still postcondition checks against the config-derived `state` / `score`.

4. Do **not** edit `src/ui/api/api_meteorite.py`, `src/core/inbox.py`, `src/ui/api/api_inbox.py`, or frontend Manage Email — they already propagate `payload["state"]` from core.

**Done when (recheck):** `python3 -m py_compile src/utils/config.py src/core/meteorite.py` succeeds; `from src.utils.config import METEORITE_CONFIG, JOB_STATES` shows `METEORITE_CONFIG["job_create_state"] == "METEORITE_NEW"` and that key is in `JOB_STATES`; a manual mental trace of Manage Email Create → `create_meteorite_job_from_inbox_message` → `create_meteorite_job` yields insert state **METEORITE_NEW**.

## Out of scope (do not implement)

- Parallel meteorite `JOB_STATES` / In Review manifests (AST-1053 — already landed on ftr).
- Meteorite dispatch rows / `score_floor` 0 (AST-1054).
- `meteorite_like` / meteorite upshot agent_task prompts (AST-1055).
- Recommended **Meteorites** section (AST-1057).
- Normal (non-meteorite) GDL create / `JD_READY` scrape path.
- Test-tree or bible edits (Betty updates AST-1041/1042/1053 asserts that still expect `JD_READY`).

## Self-Assessment

**Scope:** `minor` — one config key retarget plus docstring updates in the existing meteorite create module; no new files or layers.

**Conf:** `high` — create already consumes `job_create_state`; AST-1053 already registered unrestricted `METEORITE_NEW`; API/inbox need no wiring changes.

**Risk:** `Medium` — wrong landing state would put meteorite jobs on the vetted-company GDL trail (or an illegal state); confining the change to the config key plus docs keeps the blast radius to the meteorite create path only.

## Rules self-review

- §1.4 / `astral.standards.no-hardcoded-sets` — landing state stays in `METEORITE_CONFIG`, not hardcoded in core.
- §2.1 / `astral.config.config-source-of-truth` — single key owns create default; assert `in JOB_STATES` unchanged.
- §2.6 / `astral.state.job-prior-states-enforced` — insert into `METEORITE_NEW` (`prior_states: None`) is lawful unrestricted entry; no illegal hop via `transition_job_state`.
- §3.3 imports — no new imports.
- §2.4 batch — untouched (create is not a claim batch).
- Engineer must not edit `tests/` / bible; Betty owns assert flips from `JD_READY` → `METEORITE_NEW`.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`
**Plan path:** `docs/features/meteorite/ast-1056-create-lands-meteorite-jobs-in-meteorite-new.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `b8850e8e` | `job_create_state` → METEORITE_NEW + meteorite.py docstring honesty |

**Tip:** `b8850e8e83f185083250b42be865dc613651b434` on `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1056
**Publish ref:** `a84a6d5e24dffd8ecc8bb2cc7cc1d5721ee50d43` (`origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`)
**Overall:** DISCUSS

### What’s solid
- `METEORITE_CONFIG["job_create_state"]` → `METEORITE_NEW`; create body still reads config (no hardcode).
- Docstrings honest; `job_create_latest_score` unchanged; direct insert carve-out retained.
- Boundaries held vs dispatch / prompts / Recommended.

### Issues
- **discuss (straggler ×3):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot vs `origin/dev` includes `docs/features/**` + Betty tests/bible — all **conforms** on substance.

### Recommended actions
- Hedy: acknowledge stragglers → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `5d0f3615` — **Overall:** DISCUSS; **fix-now:** none; **discuss:** statute straggler ×3 (all substance **conforms**); no advisory.

No product changes. Acknowledged discuss stragglers as plan-time Joan exclusions that became in-scope on the three-dot vs `origin/dev` (`docs/features/**` + Betty tests/bible) — no code delta. Advanced to **User Testing**.
