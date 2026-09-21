<!-- linear-archive: AST-1156 archived 2026-08-07 -->

## Linear archive (AST-1156)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1156/skipped-retry-hop-correct-dispatchable-state-all-rubric-tasks  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1150 — Technical fail for Do prompt  
**Blocked by / blocks / related:** parent: AST-1150

### Description

## What this implements

Replace hard-coded Skipped `bulk_retry_to_state: NEW` with family- and hop-aware re-entry so Retry works for **all** rubric tasks (meteorite and regular): restore the claimable trigger for the hop that landed the job on Skipped (e.g. meteorite Do → `METEORITE_PASSED_JD`). Avail must go **> 0** on the matching dispatch task. Does **not** own grade completeness.

## In scope

- [X] `pattern.config.config-block` — `JOBS_SKIPPED_BULK_RETRY_TO_STATE` + manifest `bulk_retry_to_state_by_from_state` (no hard-coded NEW in UI)
- [X] `astral.state.core-decides-transitions` — Skipped Retry destinations owned in config; UI reads manifest map
- [X] `astral.state.job-prior-states-enforced` — expand target `prior_states`; `bulk_state` uses `transition_job_state`
- [X] `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — retry map literals in `config.py` only
- [X] Skipped page Retry groups selection by current job state and posts one `to_state` per hop/family

## Considered but excluded

- [X] `astral.agent.grade-vector-validation` / completeness prompts — AST-1154 (`src/core/agent.py`, `agent_task` prompts)
- [X] Incomplete-grade → retry holding / consult apply — AST-1155 (`src/core/consult.py`)
- [X] `_render_score` math / rubric content — parent boundary
- [X] `CANDIDATE_SKIPPED` Resurrect path — already separate UI action
- [X] Betty `tests/**` / `docs/test-bible/**` — qa-child after Code Complete

## Acceptance criteria

- [X] 4. From Skipped, Retry on a **meteorite** job that failed at a rubric hop leaves Avail **> 0** on the matching meteorite dispatch task (not plain **NEW** with Avail 0). Retry on a **regular** job likewise restores that job’s claimable rubric trigger (not a cross-family state).

## Boundaries

Does **not** own grade completeness contracts or incomplete-grade consult routing. After #1 and #2 (bang blockers).

## Notes for planning

Parent decision: Skipped Retry for all rubric tasks with hop/family-correct landing. Plan: `docs/features/consult/ast-1156-skipped-retry-hop-correct-dispatchable-state.md`.

## Git branch (authoritative)

`sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state` (ignore Linear gitBranchName).

### Comments

#### chuckles — 2026-08-03T02:19:35.058Z
[merge-child] blocked: git pull merge on sub (`e011a77d` — `Merge remote-tracking branch 'origin/dev' into sub/AST-1150/AST-1156-…`). validate-sub-log refuses rollup until that commit is gone from the publish-ref history.

@katherine — rebuild `origin/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state` from `origin/ftr/AST-1150-technical-fail-for-do-prompt` (fetch + merge ftr, never `git pull` / merge `origin/dev` into sub). Preserve plan/code/merge-tests/test/docs/resolve commits for AST-1156; force-push republish the cleaned sub. Leave status User Testing.

— Chuckles

#### chuckles — 2026-08-03T02:18:33.980Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

Offending commit on `origin/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`:
`e011a77d Merge remote-tracking branch 'origin/dev' into sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`

@Katherine Johnson — republish the sub without a `Merge remote-tracking branch` commit (merge `origin/ftr/AST-1150-technical-fail-for-do-prompt` only, then re-push the AST-1156 work). merge-child will retry after the tip is clean.

— Chuckles

#### radia — 2026-08-03T02:14:10.078Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1156
**Publish ref:** a394d7c4 (doc commit; code tip 7b725de8796ff98028ebcf303da1fbddaf818515)
**Overall:** DISCUSS

## Plan adherence
- Stage 1 (`src/utils/config.py`): `JOBS_SKIPPED_BULK_RETRY_TO_STATE` matches the plan's literal dict exactly (30 entries, all three families — regular/meteorite/non-rubric). `prior_states` widened on exactly the 10 targets the plan's table names, with exactly the from-states it names (`JD_READY`, `PASSED_JD`, `PASSED_DO`, `CULTURE_READY`, `PASSED_GET`, `PASSED_JOBLIST`, and the four meteorite mirrors) — no extra, no missing. `*_RETRY` holdings from AST-1155 correctly left untouched (Retry lands on primaries only, per plan's explicit ⚠️ decision). Manifest key swap (`bulk_retry_to_state` → `bulk_retry_to_state_by_from_state`) matches verbatim. Module-load integrity asserts match the plan's Stage 1 step 2 exactly.
- Stage 2 (`src/ui/api/api_jobs.py`, `StateUiContext.tsx`, `JobsSkipped.tsx`): `bulk_state` swapped `save_job` → `transition_job_state` with the same per-id try/except ValueError partial-success semantics the plan specifies; `@require_auth` and the request-body contract (`astral_job_ids`/`to_state`) untouched. TS manifest type matches Stage 1's shape. `JobsSkipped.handleRetry` groups selection by `job.state`, looks up the map, skips unmapped partitions, issues one POST per destination, sums `updated` — and goes slightly beyond the plan's flexible step 3e by distinguishing `"No retryable jobs in selection"` (nothing mapped) from `"Retry failed"` (posted but zero updated), which is a sensible refinement of the plan's either/or wording choice, not a deviation.
- **Live-ran the plan's own verification scripts against the actual publish tip**: Stage 1's `build_state_ui_manifest()` + `JOB_STATES` prior assertions (incl. the meteorite Do example named in the parent AC), and `py_compile` on both touched Python files. Both green.
- Full active statute set (65) scored in-session — 0 fix-now, 1 discuss carried from Joan's plan-rubric verdict (confirmed still accurate against the shipped diff), 3 trivially-clean C4 stragglers (see Notes), 1 advisory.

## Pattern conformance
- `pattern.config.config-block` — conforms. `JOBS_SKIPPED_BULK_RETRY_TO_STATE` is a named block in `config.py`, sole source of truth; the manifest exposes it read-only and the frontend never hard-codes a destination.

## Findings

**discuss — `astral.state.job-prior-states-enforced`.** Carried from Joan's plan-rubric verdict, confirmed unchanged in the shipped diff: the `prior_states` expansion is a global widening of the state machine (e.g. `FAILED_DO` is now a legal prior of `PASSED_JD` for *any* caller of `transition_job_state`, not just the Skipped Retry button), even though the mechanism itself is a net improvement — Retry no longer bypasses priors / `state_history` via the old `save_job` path. Exposure is backward edges out of terminal fail states only; nothing in the automated pipeline transitions out of a fail state today. Not fix-now.

**advisory — unused import.** `src/ui/api/api_jobs.py` still imports `save_job` (line 17) but no longer calls it anywhere in the file after the `bulk_state` refactor — dead import. Harmless, no runtime impact; worth a cleanup pass whenever the file is next touched.

## Frame diff
(none) — description already reflects the shipped diff via the plan doc's Files Changed table, Decisions, and Review stub section; no adds/moves applied to the Linear description itself.

## Notes
- Joan's plan-time discuss 2 (the `FAILED_TECHNICAL` → `NEW` row is the one map entry that still does a full restart, unlike every other hop-correct row) was proactively addressed: the shipped map carries the inline comment `# Full restart: origin hop unknowable (prior_states None / upshot-path generic).` directly above that entry — exactly the clarification Joan asked for. No longer open.
- Joan's plan-time discuss 3 (client-side grouping / N-POST design vs. a single server-resolved POST) was implemented as planned (Decision 5) — engineer's call exercised, not a code deviation; recording for traceability only.
- C4 straggler check: 3 statutes Joan's plan-rubric verdict scored not-applicable/excluded on plan layers (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`) score `conforms` on this diff-based sweep — same structural cause as AST-1154/AST-1155's reviews: the actual diff includes this ticket's own plan doc plus test/test-bible commits, neither of which sit in the plan's Files-Changed table by convention. Per-commit role separation verified clean this round with no sibling-ticket bleed-in: `code()` commits (`35931486`, `d04c2e5e`) touch only `src/utils/config.py` / `src/ui/api/api_jobs.py` / `src/ui/frontend/**`; `test()`/`merge-tests()` commits touch only `tests/**` and `docs/test-bible/**`, and this time the two match 1:1 (no unrelated sibling entries).
- Diff also carries ancestry-only content from AST-1154 (`_ENCODED_GRADE_SET_COMPLETENESS` in `config.py`) and AST-1155 (`consult.py`/`roster.py`, the `*_RETRY` holdings) via the merged `origin/ftr/AST-1150` base — confirmed byte-identical to what I already reviewed and posted Review Posted on for both sibling tickets; not re-scored here, not this ticket's work.
- Observed one out-of-band merge commit (`e011a77d`, authored by Susan directly) pulling `origin/dev` into this sub branch mid-build, bringing in unrelated meteorite title-pattern-screening changes (including a `src/core/consult.py` hunk from a different ticket). Flagging for visibility since `orch.git.flow-direction-inviolable` names `dev→ftr→sub` as the canonical path rather than `dev→sub` directly — but this was a human (not agent) git operation outside the build-child pipeline, introduced no conflicts with this ticket's own commits, and the ticket's own Files Changed set is unaffected. Not a finding against the engineer.

## What's solid
- Root cause and fix are a clean match: the old `save_job` bypass is gone, `transition_job_state` now enforces priors and appends `state_history`, and the `prior_states` table was expanded exactly enough (not more) to make every mapped Retry edge legal — confirmed live via the meteorite Do → `METEORITE_PASSED_JD` example the parent AC names verbatim.
- Family discipline held throughout: zero cross-family map entries (meteorite fail states target meteorite triggers only), and `*_RETRY` holdings correctly excluded as Retry targets.
- Clean boundary discipline: no `consult.py`/`agent.py`/grade-path touch in this ticket's own commits, `CANDIDATE_SKIPPED` Resurrect untouched, `bulk_state`'s request contract and `@require_auth` preserved.

context_tokens≈210000

— Radia

#### betty — 2026-08-03T02:08:44.249Z
## QA test manifest — AST-1156

**Publish:** `origin/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state` @ `7b725de8`
**tests SHA:** `0defa0c4` (`test(AST-1156): Skipped Retry hop-correct dispatchable state map`)
**merge-tests:** `merge-tests(AST-1156): origin/tests 0defa0c4a98ff30db5f02b2b68b7d21affaed902`

### Classification

1. **Existing coverage (bible-backed)**
   - `tests/component/frontend/pages/test_JobsSkipped.test.tsx` — Retry toast / Expand One / Resurrect paths still apply; Retry body now asserts hop-correct `to_state`.

2. **Broken / obsolete (revised this pass)**
   - `TestBuildStateUiManifest` — scalar `bulk_retry_to_state == "NEW"` → map assertions.
   - `TestAst874FetchCulturePagesConfig` / `TestAst1053MeteoriteGdlJobStates` — prior lists expanded for Skipped Retry from-states.
   - `TestJobsRoutes::test_bulk_state_updates_jobs` — mocks `transition_job_state` (not `save_job`).
   - `stateUiManifestFixture.ts` — map + meteorite Skipped sections/labels.

3. **Gaps (new this pass)**
   1. `tests/component/utils/test_config.py::TestAst1156SkippedBulkRetryMap` — map coverage, AC targets, manifest key, prior acceptance.
   2. `test_JobsSkipped.test.tsx` — **AST-1156 hop-correct Skipped Retry** (meteorite Do → `METEORITE_PASSED_JD`; mixed Do/Get → two POSTs).

**Integration:** none — no existing scenario asserts Skipped Retry destinations.

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1156SkippedBulkRetryMap \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_manifest_contains_expected_sections \
  tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_bulk_state_updates_jobs \
  -q

cd src/ui/frontend && npx vitest run \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx
```

### Bible (on publish-ref)

- `docs/test-bible/utils/config.md` shasum `f78b7a7fe53d108b6425fd2dcb7b8879e0bba0da`
- `docs/test-bible/frontend/pages.md` shasum `2bd70f704676e3bb08e7da89e5711e297c23eafc`
- `docs/test-bible/ui/api/api_jobs.md` shasum `6b3e025bae791c23ad6c8a01c4b9215872bddb65`

— Betty

#### joan — 2026-08-03T01:59:14.639Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1156
**Overall:** APPROVED

Publish ref confirmed against parent Git table: `sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state` @ `36bdfb38`.

Both blockers are satisfied on the base: the worktree tip merges `origin/ftr/AST-1150-technical-fail-for-do-prompt`, and I can see AST-1155's `*_RETRY` holdings already sitting in `JOB_STATES` prior lists, so the plan's "parent ftr already carries both" is true rather than aspirational.

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 incomplete vectors → retry holding | N/A — boundary (AST-1155); Non-goals name it |
| AC2 complete grade sets unchanged | N/A — no scoring path touched |
| AC3 model-facing contracts | N/A — boundary (AST-1154) |
| AC4 Skipped Retry leaves Avail > 0 on the matching dispatch task, family- and hop-correct | Stage 1 (config map + `prior_states` + manifest) + Stage 2 (`transition_job_state` + per-from-state grouping); Stage 2 UAT checklist asserts the meteorite Do → `METEORITE_PASSED_JD` case named in the AC verbatim |
| AC5 `debug=True` vector detail | N/A — boundary (AST-1155) |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 config map, prior expansion, manifest key swap | Functional scope 4 "Skipped Retry for all rubric tasks"; Architectural definition `pattern.config.config-block` and "no hard-coded NEW in UI" |
| Stage 2 `bulk_state` → `transition_job_state`, Skipped page grouping | Same functional scope, delivery half; `astral.state.job-prior-states-enforced` (removes the `save_job` bypass) |

No orphan stages.

## Adversarial verification (plan claims checked against the worktree)

| Plan claim | Result |
|------------|--------|
| Module-load assertion `set(map) == set(JOBS_SKIPPED_SECTION_ORDER) - {CANDIDATE_SKIPPED}` | **Verified by executing it** — 30 map keys against 31 sections, both difference sets empty. This was the highest-risk item in the plan: a single missing or surplus key would have made `config.py` fail to import and taken the whole app down at boot. It is exact |
| Every map key and value is a `JOB_STATES` key | Verified — 30 keys, 12 distinct targets, zero misses |
| `prior_states` table covers every target that needs it | Verified — the ten listed targets are exactly the ten with non-`None` priors; `NEW` and `METEORITE_NEW` are `None` as the plan says. No target left out |
| `__BELOW_DISPATCH_FLOOR__` is synthetic and excluded from the map | Verified and consistent — the floor is `below_dispatch_key` in the manifest, not a `JOBS_SKIPPED_SECTION_ORDER` member, so Decision 7 does not collide with the Stage 1 assertion. Floor rows carry real `PASSED_*` states, which are unmapped, so they skip |
| `bulk_state` uses `save_job` and bypasses priors / `state_history` | Verified at `api_jobs.py:89-105` |
| `api_jobs.py` already imports `transition_job_state` | Verified at line 24; also already used at lines 210 and 288, so the call style is established in-file |
| `transition_job_state([id], to_state)` signature and `ValueError` behaviour | Verified at `tracker.py:657-682` — raises on unknown job and on prior violation, appends `state_history`. The plan's per-id `try/except ValueError` genuinely preserves today's partial-success semantics |
| `JobsSkipped.handleRetry` posts one `to_state` for all selected ids | Verified at `JobsSkipped.tsx:209-222` |
| Rows carry `state` for client-side grouping | Verified — row type declares `state: string` (line 27) and sections are already built by bucketing `job.state` (lines 157-158), so Stage 2 step 3a needs no new data |
| Every consumer of the scalar `bulk_retry_to_state` is accounted for | Verified — three product consumers (`config.py`, `StateUiContext.tsx`, `JobsSkipped.tsx`) all appear in Files Changed; the two test consumers (`test_config.py`, `stateUiManifestFixture.ts`) are correctly parked in the Betty verify-only table. No consumer is missed |
| `@require_auth` on `bulk_state` | Verified present at line 90 and untouched by the plan |
| `/api/jobs/bulk_state` caller count | One — `JobsSkipped.tsx`. The Companies pages hit a different endpoint. Relevant to discuss 3 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | One `code()` commit per stage on the sub ref |
| orch.git.flow-direction-inviolable | conforms | Publishes to `origin/sub/...` only |
| orch.git.ftr-sub-topology | conforms | Publish ref matches the parent Git table row |
| orch.git.merge-on-checkout | conforms | Explicitly merges the authoritative `origin/ftr/AST-1150-technical-fail-for-do-prompt` segment, and warns against the bare `ftr/AST-1150` form |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Sub branch only |
| orch.git.one-epic-worktree-per-parent | conforms | Executes on `astral-AST-1150` |
| orch.git.three-permanent-branches | conforms | Invents no permanent branch |
| orch.pipeline.call-susan-for-product-decisions | conforms | Stage-blocked template escalates to parent AST-1150 |
| orch.pipeline.plan-is-bible | conforms | Binding contract, Files Changed table, full literal map. Step 3e leaves the zero-result toast wording to the engineer, which is cosmetic and bounded by the existing error-toast style already in the file |
| orch.pipeline.project-scoped-queues | conforms | Single child, Astral Consult |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready entry |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Both test consumers of the removed scalar are listed verify-only for Betty, with the engineer explicitly barred from editing them |
| orch.roles.chuckles-never-ticket-assignee | conforms | Katherine implements |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.agent.confidence-bounds | conforms | No grade or confidence handling touched |
| astral.config.config-source-of-truth | conforms | The whole change moves the Retry destination from a UI literal into `config.py`, surfaced through the manifest |
| astral.config.pass-threshold-vs-score-floor | conforms | Neither value touched; floor rows deliberately left out of the map |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets or env lookups |
| astral.dispatch.run-next-is-chain-authority | conforms | The map is a fail-state → re-entry-trigger table for an operator action, not a hop-succession list; it adds no parallel `run_next` chain |
| astral.dispatch.seed-auto-false | conforms | No `dispatch_task` rows touched |
| astral.git.betty-no-src-or-features | conforms | Engineer owns `src/`; Betty's files are verify-only |
| astral.layers.import-direction | conforms | UI API already imports `transition_job_state` from core; no new edge |
| astral.layers.ui-config-driven-business-logic | conforms | This statute is the point of the ticket — the React page stops hard-coding `NEW` and reads destinations from the manifest |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `@require_auth` on `bulk_state` verified present and untouched |
| astral.seed.agent-tables-in-repo-json | conforms | No `data/admin/**` edits |
| astral.seed.archie-catalog-wins | conforms | Committed config edit, not a live DB edit |
| astral.seed.boot-only-not-hot-path | conforms | Map is a module constant read at manifest build |
| astral.seed.define-approved | conforms | Invents no `JOB_STATES` key — Decision 3 forbids it and the assertion enforces it |
| astral.seed.operator-rows-stay-deleted | conforms | No dispatch-row inserts |
| astral.seed.other-via-coverage-join | conforms | No candidate-scoped seed inserts |
| astral.standards.data-raises-caller-logs | conforms | `tracker.transition_job_state` raises; the API caller handles per id |
| astral.standards.debug-contract-gated | conforms | No debug emission added |
| astral.standards.dry-and-focused-functions | conforms | One config dict is the single source; the UI holds no second copy |
| astral.standards.in-scope-only | conforms | Out-of-scope list covers `consult.py`, `agent.py`, grade paths, tests, and the Betty fixture |
| astral.standards.logging-via-utils | conforms | No logging change |
| astral.standards.names-not-ticket-ids | conforms | `JOBS_SKIPPED_BULK_RETRY_TO_STATE` and `bulk_retry_to_state_by_from_state` are domain names; AST-1156 appears only in a comment |
| astral.standards.no-cross-contamination | conforms | Stays inside config plus the Skipped surface |
| astral.standards.no-hardcoded-sets | conforms | Directly remediates a hardcoded value — the literal `"NEW"` leaves the UI and becomes a config-owned map |
| astral.standards.public-then-helpers | conforms | Module-level constant beside the sibling `JOBS_SKIPPED_*` maps |
| astral.standards.utils-data-late-import-only | conforms | No `utils → data` import added |
| astral.state.job-prior-states-enforced | needs-discussion | Net improvement — Retry stops bypassing priors via `save_job` — but the enabling mechanism permanently widens ten targets' prior lists for all callers. See discuss 1 |
| astral.ui.frontend-file-placement | conforms | Edits existing `pages/` and `contexts/` files; adds no new frontend file |
| astral.ui.naming-conventions | conforms | Manifest key is snake_case matching its siblings; no component renames |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn or worker change |

## Considered and excluded

**Considered (48):** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded (17):**
- astral.agent.do-task-delegation — layers [core] does not intersect plan layers [ui, utils]
- astral.agent.grade-vector-validation — layers [core] does not intersect plan layers
- astral.batch.batch-id-first — layers [data, core] does not intersect plan layers
- astral.batch.batch-id-format — layers [core, data] does not intersect plan layers
- astral.batch.claim-process-release — layers [core, data] does not intersect plan layers
- astral.batch.entity-agent-responses-latest-only — layers [core, data] does not intersect plan layers
- astral.debug.no-repo-root-artifacts-dir — paths [artifacts/**, scripts/spikes/**] match no plan path
- astral.debug.spikes-under-debug-dir — paths [debug/**, docs/features/**, scripts/spikes/**] match no plan path
- astral.docs.features-single-file-per-ticket — layers [docs] does not intersect plan layers
- astral.git.engineer-test-tree-ban — paths [tests/**, docs/test-bible/**, ...] match no plan path; test references live in the verify-only Betty table
- astral.layers.core-vs-external-bright-line — layers [core, external] does not intersect plan layers
- astral.layers.scripts-exempt-from-layer-rules — layers [scripts] does not intersect plan layers
- astral.patterns.coat-check-never-store-empty — layers [core] does not intersect plan layers
- astral.patterns.render-verdict-orchestrates-consult — layers [core] does not intersect plan layers
- astral.standards.database-header-inventory — layers [data] does not intersect plan layers
- astral.state.core-decides-transitions — layers [core, data] does not intersect plan layers [ui, utils] (see Notes)
- astral.state.no-daisy-chain-in-run — layers [core] does not intersect plan layers

## Findings

**No fix-now findings.**

**discuss 1 — the `prior_states` expansion is global, not scoped to the Retry button.** Stage 1 step 3 appends fail states to ten targets' prior lists so `transition_job_state` will accept the Retry edge. That is the correct mechanism and I confirmed the table is complete, but priors are a global guard: once `FAILED_DO` is a legal prior of `PASSED_JD`, *any* caller of `transition_job_state` can make that backward jump, not just the Skipped page. In practice the exposure is small — these are backward edges out of terminal fail states, and nothing in the automated pipeline transitions out of a fail state — so I am not asking for a change. Worth naming because the plan presents the expansion purely as plumbing for one button, and it is actually a permanent widening of the state machine that outlives this feature. `astral.state.job-prior-states-enforced` is scored needs-discussion on that basis, even though the plan is a net improvement to that statute (it removes the `save_job` bypass that skipped prior checks and `state_history` entirely).

**discuss 2 — `FAILED_TECHNICAL` → `NEW` is the one row that keeps the behaviour this ticket exists to remove.** Every other mapping lands on the hop that failed. `FAILED_TECHNICAL` has `prior_states: None`, is documented in config as the generic technical failure, and is returned by `consult.py:1203` on the analysis-upshot path — so a job sitting there may already have cleared JD, DO, GET and LIKE. Retry sends it back to `NEW` for a full re-run of every hop, including the agent calls. This is today's behaviour and therefore not a regression, and it is consistent with the epic deliberately leaving upshot alone (AST-1155 also excluded the `PASSED_LIKE_RETRY` holdings), so it does not block. But the plan's Decision 6 says non-rubric rows get hop-correct targets "so NEW is not a silent default", and this row is exactly a silent default. One sentence in the map comment saying `FAILED_TECHNICAL` is intentionally a full restart because its origin hop is unknowable would keep a future reader from treating the map as uniformly hop-correct.

**discuss 3 — client-side grouping was a free choice, not a compatibility constraint.** Decision 5 keeps the `{astral_job_ids, to_state}` body and has the frontend partition and issue one POST per destination. I checked: `/api/jobs/bulk_state` has exactly one caller in the codebase, `JobsSkipped.tsx`. The Companies pages use a separate `/api/companies/bulk_state`. So nothing forced the contract to stay as-is — the endpoint could have taken ids alone and resolved each job's destination from the same config map server-side, giving one POST instead of N and keeping a thirty-entry map out of every manifest consumer's payload. Both shapes satisfy `astral.layers.ui-config-driven-business-logic` since the destinations are config-owned either way, and the plan's version has the virtue of leaving `bulk_state` a dumb generic setter. Raising it because Decision 5 argues only against adding a *second* endpoint and never addresses reusing the existing one. Engineer's call.

**Notes — a named in-scope statute is mechanically excluded.** The ticket lists `astral.state.core-decides-transitions` in scope, but its `applies_when.layers` is `[core, data]`, so the matching algorithm drops it for a ui/utils change set. Recording it so the exclusion does not read as an oversight. The plan honours it in spirit regardless: the UI never computes a destination, it reads one from the config-built manifest and hands it to the core `transition_job_state`, which is the function that enforces the rules.

**acceptable — self-assessment honesty.** Scope `Single-Component`, Conf `high`, Risk `Medium` are all fair. The Risk note names the two things that would actually bite — a wrong map entry or a missing prior leaving Avail at 0 or silently dropping updates — and both are covered by the module-load assertion and the Stage 1 verify snippet, which I ran against the current tree rather than trusting. `high` confidence is earned: the parent AC supplies the worked example the map is built around, and every structural claim held.

**R6 checklist.** Definition fidelity pass — implements parent Functional scope 4 and nothing else. Boundaries pass — no completeness contracts, no consult routing, no `_render_score` math, `CANDIDATE_SKIPPED` Resurrect left alone. Layer and import pass. Config-as-source-of-truth pass, emphatically. File placement pass. Auth preserved. No batch or dispatch-chain changes. DRY pass. No sibling scope creep into AST-1154 or AST-1155, and the blockedBy dependency is real and already merged into the base.

context_tokens≈150000

— Joan

#### katherine — 2026-08-03T01:52:03.158Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state/docs/features/consult/ast-1156-skipped-retry-hop-correct-dispatchable-state.md (`origin/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state` @ `36bdfb38`)

**Scope:** Single-Component — config Retry map + prior expansions, `bulk_state` → `transition_job_state`, Skipped page groups by from-state.

**Conf:** high — parent AC names meteorite Do → `METEORITE_PASSED_JD`; fail-state priors already encode the hop trigger; manifest bulk targets match company bulk_transitions pattern.

**Risk:** Medium — wrong map/missing prior leaves Avail 0 or silently drops updates; mixed-selection Retry multi-posts on Skipped only.

---

# AST-1156 — Skipped Retry → hop-correct dispatchable state (all rubric tasks)

**Linear:** [AST-1156](https://linear.app/astralcareermatch/issue/AST-1156/skipped-retry-hop-correct-dispatchable-state-all-rubric-tasks)  
**Parent:** [AST-1150](https://linear.app/astralcareermatch/issue/AST-1150/technical-fail-for-do-prompt) — Technical fail for Do prompt  
**Project:** Astral Consult  
**Publish ref:** `sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`

Replace the Skipped page’s hard-coded `bulk_retry_to_state: NEW` with a config-owned **from-state → claimable trigger** map so Retry restores family- and hop-correct dispatchable states for every rubric fail/technical Skipped section (meteorite and regular). After Retry, Scheduled Actions Avail must be **> 0** on the matching dispatch task (e.g. meteorite Do fail → `METEORITE_PASSED_JD` for `grade_do`, not plain `NEW` with Avail 0).

**Non-goals:** Grade completeness contracts (AST-1154). Incomplete-grade → retry holding routing (AST-1155). Rubric content / `_render_score` math. Redesigning Skipped UI beyond Retry destination resolution. `CANDIDATE_SKIPPED` Resurrect (already separate). Betty test-tree / bible edits.

**Depends on:** AST-1154 + AST-1155 (Linear blockedBy). Parent ftr `origin/ftr/AST-1150-technical-fail-for-do-prompt` already carries both — merge it on checkout before build (authoritative segment, not bare `ftr/AST-1150`).

---

## Root cause (locked)

`build_state_ui_manifest()` exposes a single string `jobs.skipped.bulk_retry_to_state = "NEW"`. `JobsSkipped.handleRetry` posts every selected id to that one target via `POST /api/jobs/bulk_state`.

Meteorite (and regular mid-pipeline) jobs that landed on Skipped after a rubric hop are not claimable from `NEW`: meteorite `grade_do` claims `METEORITE_PASSED_JD`, regular `grade_do` claims `PASSED_JD`, etc. Retry → `NEW` leaves Avail at 0 on the hop that failed.

`bulk_state` today calls `tracker.save_job` (bypasses `prior_states` and does not append `state_history`). Hop-correct targets have restricted `prior_states` that do **not** yet list the fail/technical Skipped states, so switching to `transition_job_state` without expanding priors would silently no-op updates (`ValueError` swallowed).

---

## Decisions (locked for build)

1. **Config owns the Retry map.** Add `JOBS_SKIPPED_BULK_RETRY_TO_STATE: Dict[str, str]` (from Skipped section state → claimable **primary** trigger). Manifest exposes it as `bulk_retry_to_state_by_from_state`. Remove scalar `bulk_retry_to_state`.
2. **Land on the primary trigger, not `*_RETRY` holdings.** Parent AC example is `METEORITE_PASSED_JD`. AST-1155 holdings remain for incomplete-grade first-strike inside consult; operator Skipped Retry is a full hop re-entry on the dispatch claim state.
3. **Family stays family.** Meteorite fail/technical → meteorite triggers only; regular → regular only. No cross-family targets.
4. **Expand `prior_states` on every Retry target** so `transition_job_state` accepts from→to. Do not leave Retry on the `save_job` bypass.
5. **`bulk_state` uses `transition_job_state`.** Same endpoint body `{ astral_job_ids, to_state }`; frontend groups selected jobs by current `job.state` and issues one POST per destination.
6. **Map covers every `JOBS_SKIPPED_SECTION_ORDER` entry except `CANDIDATE_SKIPPED`.** Rubric rows are AC-critical; non-rubric rows get hop-correct targets too so NEW is not a silent default. `CANDIDATE_SKIPPED` stays Resurrect-only (omit from map; frontend skips unmapped ids).
7. **Below-dispatch floor section** is synthetic (`__BELOW_DISPATCH_FLOOR__`) — not in the map; those rows are still `PASSED_*` in DB and must not be bulk-retried via this map (checkboxes may exist — if selected with no map key, skip with toast that none were queued).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOBS_SKIPPED_BULK_RETRY_TO_STATE`; expand target `prior_states`; manifest key swap | utils |
| `src/ui/api/api_jobs.py` | `bulk_state` → `transition_job_state` | ui |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Manifest type: map replaces scalar | ui |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Group Retry by `job.state`; look up map; one POST per `to_state` | ui |

**Out of scope:** `src/core/consult.py`, `src/core/agent.py`, grade/prompt paths, `tests/**`, `docs/test-bible/**`, `stateUiManifestFixture.ts` (Betty).

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/utils/test_config.py` | Assert map entries + `bulk_retry_to_state_by_from_state`; drop scalar `== "NEW"` |
| `tests/component/frontend/fixtures/stateUiManifestFixture.ts` | Mirror new manifest shape |
| `tests/component/frontend/pages/test_JobsSkipped.test.tsx` | Retry posts hop-correct `to_state` for a meteorite/regular fixture row |
| `tests/component/ui/api/test_api_jobs.py` | If present: bulk_state goes through transition / prior enforcement |
| `docs/test-bible/utils/config.md` (+ frontend pages if needed) | Skipped Retry map wording |

---

## Stage 1: Config map + prior_states + manifest

**Done when:** `JOBS_SKIPPED_BULK_RETRY_TO_STATE` is the SSOT; every listed from-state maps to a `JOB_STATES` key; each target’s `prior_states` includes its mapped from-states (or target has `prior_states is None`); manifest serves `bulk_retry_to_state_by_from_state` and no longer serves `bulk_retry_to_state`; a one-liner import check prints `ok`.

1. In `src/utils/config.py`, immediately above `build_state_ui_manifest` (near the other `JOBS_SKIPPED_*` maps), add:

   ```python
   # AST-1156: Skipped Retry — from Skipped section state → claimable primary trigger.
   # Keys ⊆ JOBS_SKIPPED_SECTION_ORDER except CANDIDATE_SKIPPED (Resurrect-only).
   JOBS_SKIPPED_BULK_RETRY_TO_STATE = {
       # Regular rubric / qualify / JD
       "FAILED_JOBLIST": "NEW",
       "ERROR_QUALIFY_JOB_LISTINGS": "NEW",
       "INVALID_TITLE": "NEW",
       "FAILED_JD": "JD_READY",
       "ERROR_EVALUATE_JD": "JD_READY",
       "FAILED_TECHNICAL": "NEW",
       "FAILED_DO": "PASSED_JD",
       "FAILED_TECHNICAL_DO": "PASSED_JD",
       "FAILED_GET": "PASSED_DO",
       "FAILED_TECHNICAL_GET": "PASSED_DO",
       "FAILED_LIKE": "CULTURE_READY",
       "FAILED_TECHNICAL_LIKE": "CULTURE_READY",
       # Meteorite rubric / qualify / JD
       "METEORITE_FAILED_QUALIFY": "METEORITE_NEW",
       "METEORITE_ERROR_QUALIFY": "METEORITE_NEW",
       "METEORITE_FAILED_JD": "METEORITE_QUALIFIED",
       "METEORITE_ERROR_EVALUATE_JD": "METEORITE_QUALIFIED",
       "METEORITE_FAILED_DO": "METEORITE_PASSED_JD",
       "METEORITE_FAILED_TECHNICAL_DO": "METEORITE_PASSED_JD",
       "METEORITE_FAILED_GET": "METEORITE_PASSED_DO",
       "METEORITE_FAILED_TECHNICAL_GET": "METEORITE_PASSED_DO",
       "METEORITE_FAILED_LIKE": "METEORITE_PASSED_GET",
       "METEORITE_FAILED_TECHNICAL_LIKE": "METEORITE_PASSED_GET",
       # Non-rubric hop re-entry (replace hard-coded NEW; not AC-critical but map-complete)
       "JD_SCRAPE_FAIL": "PASSED_JOBLIST",
       "JD_SCRAPE_FAIL_COOKIE": "PASSED_JOBLIST",
       "JD_SCRAPE_FAIL_BOT": "PASSED_JOBLIST",
       "JD_SCRAPE_FAIL_MISSING": "PASSED_JOBLIST",
       "JD_SCRAPE_FAIL_CLOSED": "PASSED_JOBLIST",
       "NEED_CULTURE_CONTENT": "PASSED_GET",
       "NO_CULTURE_LINKS": "PASSED_GET",
       "NEED_WEBSITE_CONTENT": "CULTURE_READY",
   }
   ```

2. Assert map integrity (module load):

   ```python
   assert "CANDIDATE_SKIPPED" not in JOBS_SKIPPED_BULK_RETRY_TO_STATE
   assert all(k in JOB_STATES and v in JOB_STATES for k, v in JOBS_SKIPPED_BULK_RETRY_TO_STATE.items())
   assert all(
       k in JOBS_SKIPPED_SECTION_ORDER
       for k in JOBS_SKIPPED_BULK_RETRY_TO_STATE
   )
   _skipped_retryable = [s for s in JOBS_SKIPPED_SECTION_ORDER if s != "CANDIDATE_SKIPPED"]
   assert set(JOBS_SKIPPED_BULK_RETRY_TO_STATE) == set(_skipped_retryable)
   ```

3. Expand `JOB_STATES[...]["prior_states"]` lists so each mapped transition is legal under `transition_job_state`. Append (do not remove existing priors) the from-states that Retry into each target:

   | Target | Append to `prior_states` |
   |--------|--------------------------|
   | `JD_READY` | `FAILED_JD`, `ERROR_EVALUATE_JD` |
   | `PASSED_JD` | `FAILED_DO`, `FAILED_TECHNICAL_DO` |
   | `PASSED_DO` | `FAILED_GET`, `FAILED_TECHNICAL_GET` |
   | `CULTURE_READY` | `FAILED_LIKE`, `FAILED_TECHNICAL_LIKE`, `NEED_WEBSITE_CONTENT` |
   | `PASSED_GET` | `NEED_CULTURE_CONTENT`, `NO_CULTURE_LINKS` |
   | `PASSED_JOBLIST` | all five `JD_SCRAPE_FAIL*` keys |
   | `METEORITE_QUALIFIED` | `METEORITE_FAILED_JD`, `METEORITE_ERROR_EVALUATE_JD` |
   | `METEORITE_PASSED_JD` | `METEORITE_FAILED_DO`, `METEORITE_FAILED_TECHNICAL_DO` |
   | `METEORITE_PASSED_DO` | `METEORITE_FAILED_GET`, `METEORITE_FAILED_TECHNICAL_GET` |
   | `METEORITE_PASSED_GET` | `METEORITE_FAILED_LIKE`, `METEORITE_FAILED_TECHNICAL_LIKE` |

   Targets with `prior_states is None` (`NEW`, `METEORITE_NEW`) need no change.

   ⚠️ **Decision:** Do **not** add fail states as priors on AST-1155 `*_RETRY` holdings — Retry lands on primaries only. Do **not** invent new JOB_STATES keys.

4. In `build_state_ui_manifest()`, under `jobs.skipped`, **replace**:

   ```python
   "bulk_retry_to_state": "NEW",
   ```

   with:

   ```python
   "bulk_retry_to_state_by_from_state": dict(JOBS_SKIPPED_BULK_RETRY_TO_STATE),
   ```

5. Verify:

   ```bash
   python3 -c "
   from src.utils.config import (
       JOBS_SKIPPED_BULK_RETRY_TO_STATE, JOB_STATES, build_state_ui_manifest, dispatch_claim_states,
   )
   m = build_state_ui_manifest()['jobs']['skipped']
   assert 'bulk_retry_to_state' not in m
   assert m['bulk_retry_to_state_by_from_state']['METEORITE_FAILED_DO'] == 'METEORITE_PASSED_JD'
   assert m['bulk_retry_to_state_by_from_state']['FAILED_DO'] == 'PASSED_JD'
   assert 'METEORITE_FAILED_DO' in JOB_STATES['METEORITE_PASSED_JD']['prior_states']
   assert 'FAILED_DO' in JOB_STATES['PASSED_JD']['prior_states']
   # claimable primary still companions with AST-1155 holding
   assert 'METEORITE_PASSED_JD' in dispatch_claim_states('METEORITE_PASSED_JD', 'job')
   print('ok')
   "
   ```

⚠️ **Decision:** Explicit dict (not “first prior of the fail state”) so multi-prior Skipped rows (`NEED_WEBSITE_CONTENT`) and `prior_states is None` error states stay unambiguous and reviewable.

---

## Stage 2: API transition + Skipped Retry UI

**Done when:** `POST /api/jobs/bulk_state` updates via `transition_job_state` (priors + `state_history`); Skipped Retry groups selection by each job’s current `state`, posts the mapped `to_state` per group, and reports how many jobs were queued; TypeScript manifest type matches Stage 1; `py_compile` + frontend typecheck of touched files succeed.

1. In `src/ui/api/api_jobs.py` `bulk_state`, replace the per-id `save_job(job_id, state=to_state)` loop with `transition_job_state`:

   ```python
   updated = 0
   for job_id in ids:
       try:
           transition_job_state([job_id], to_state)
           updated += 1
       except ValueError:
           pass
   return jsonify({"updated": updated})
   ```

   Keep the same request body contract (`astral_job_ids` + `to_state`). Do not add a second endpoint.

   ⚠️ **Decision:** Per-id try/except preserves today’s partial-success behavior when one id is illegal; do not fail the whole batch on the first `ValueError`.

2. In `src/ui/frontend/src/contexts/StateUiContext.tsx`, change `jobs.skipped` typing:

   - Remove `bulk_retry_to_state: string`
   - Add `bulk_retry_to_state_by_from_state: Record<string, string>`

3. In `src/ui/frontend/src/pages/JobsSkipped.tsx` `handleRetry`:

   a. Build `id → state` from the loaded `rows` (each job already has `state`).
   b. Partition selected ids by `state`; for each partition look up `manifest.jobs.skipped.bulk_retry_to_state_by_from_state[state]`.
   c. Skip partitions with no map entry (e.g. accidental `CANDIDATE_SKIPPED` or floor synthetic key if ever selected).
   d. For each `(to_state, ids)` group, `POST /api/jobs/bulk_state` with that `to_state` and those ids (sequential `await` is fine — no new concurrency helper).
   e. Sum `updated` across responses; toast `` `${total} jobs queued for retry` `` on success; if `total === 0`, toast error `"Retry failed"` (or `"No retryable jobs in selection"` — pick the existing error toast style if `total === 0` after skips).
   f. Clear selection / `load()` as today after the loop.

4. Verify (engineer, no test-tree edits):

   ```bash
   python3 -m py_compile src/utils/config.py src/ui/api/api_jobs.py
   # From src/ui/frontend — typecheck only if the repo already has a script; otherwise:
   npx tsc --noEmit -p src/ui/frontend 2>/dev/null || true
   ```

   Manual UAT checklist (record in Linear stage comment, not in this plan as status):

   - Meteorite job in `METEORITE_FAILED_DO` → Retry → state `METEORITE_PASSED_JD`; Scheduled Actions Avail for `grade_do` @ `METEORITE_PASSED_JD` **> 0**.
   - Regular job in `FAILED_GET` → Retry → `PASSED_DO`; Avail for `grade_get` **> 0**.
   - Mixed selection (meteorite Do fail + regular Get fail) → two POSTs; each family lands correctly.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each tip to `origin/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`.
- Do not edit files outside the Files Changed table.
- When a step is ambiguous, contradicts another step, or the codebase has drifted — stop, comment on the **parent** Linear issue with the Stage N blocked format, and wait.
- Do not edit `tests/**` or `docs/test-bible/**`.

---

## Self-Assessment

**Scope:** `Single-Component` — config state-UI map + job prior expansions, one API call-site swap, Skipped page Retry grouping; no consult/agent grade path changes.

**Conf:** `high` — parent AC names the meteorite Do → `METEORITE_PASSED_JD` example; fail-state priors already encode the hop trigger; manifest-driven bulk targets match existing company bulk_transitions pattern.

**Risk:** `Medium` — wrong map entry or missing prior would leave Avail at 0 or silently drop updates; mixed-selection Retry now multi-posts (regression surface on the Skipped page only).

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** One config dict; UI does not hard-code destinations.
- **§1.4 / §2.1:** Retry targets live in `config.py`; manifest is the UI read path (`pattern.config.config-block`).
- **§2.6 / `astral.state.core-decides-transitions` / `astral.state.job-prior-states-enforced`:** Retry goes through `transition_job_state` with expanded `prior_states`; data layer still does not decide targets.
- **§2.4:** No new batch claim helpers — dispatch continues to claim primary (+ AST-1155 companion holdings).
- **§3.3 imports:** UI API already imports `transition_job_state`; no new layer violations.
- **No conflicts** requiring `conf-!!-NONE`.

---

## Review stub (build)

**Publish ref:** `sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`  
**Tip:** `d04c2e5e`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `35931486` | `JOBS_SKIPPED_BULK_RETRY_TO_STATE` + prior expansions + manifest map |
| 2 | `d04c2e5e` | `bulk_state` → `transition_job_state`; Skipped Retry groups by from-state |

---

## Radia review

**[code-rubric] revision=1** · **Publish ref:** `7b725de8796ff98028ebcf303da1fbddaf818515` · **Overall:** DISCUSS

Full active statute set (65) scored in-session — 0 fix-now. Live-ran the plan's own verification scripts against the actual publish tip (manifest + `JOB_STATES` prior assertions incl. the meteorite Do → `METEORITE_PASSED_JD` example named in the parent AC; `py_compile` on both touched Python files). Both green. Map, prior expansions, and manifest key swap all match the plan verbatim — no extra targets, no missing ones. `handleRetry` groups by `job.state`, one POST per destination, matching Stage 2 exactly (and refines the plan's flexible toast wording sensibly).

**discuss — `astral.state.job-prior-states-enforced`.** Carried from Joan's plan-rubric verdict, confirmed unchanged in the shipped diff: the `prior_states` expansion is a global widening of the state machine (backward edges out of terminal fail states are now legal for *any* caller of `transition_job_state`, not just this button) even though the mechanism is a net improvement over the old `save_job` bypass. Not fix-now.

**advisory:** `save_job` import in `src/ui/api/api_jobs.py` is now unused after the `bulk_state` refactor — harmless dead import, cleanup whenever convenient.

**Notes:** Joan's plan-time discuss 2 (`FAILED_TECHNICAL` → `NEW` needing a clarifying comment) was proactively addressed in the shipped map. Discuss 3 (client-side grouping design) was implemented as planned — engineer's call, not a deviation. Diff also carries ancestry-only content from AST-1154/AST-1155 (already reviewed, unchanged) plus one out-of-band `origin/dev`→sub merge by Susan mid-build (human git op, no conflict with this ticket's commits, not an engineer finding).

— Radia

---

## Resolution

**2026-08-03** — resolve-child after Radia **DISCUSS** (0 fix-now).

| Finding | Action |
|---------|--------|
| **discuss** `astral.state.job-prior-states-enforced` (global prior widening) | **Accepted as shipped.** Intentional: Retry must use `transition_job_state`; exposure is backward edges from terminal fail/technical Skipped states only. No product change (Joan/Radia both non-blocking). |
| **advisory** unused `save_job` import in `api_jobs.py` | **Removed** the dead import. |

**Publish tip after resolve:** see resolve commit on `origin/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`.
