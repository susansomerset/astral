<!-- linear-archive: AST-1057 archived 2026-08-07 -->

## Linear archive (AST-1057)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1057/recommended-page-meteorites-section-processing-meteorites  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1052 — Processing meteorites  
**Blocked by / blocks / related:** parent: AST-1052

### Description

## What this implements

Owns a distinct **Meteorites** section on Recommended for meteorite-track jobs (post-upshot / recommended surface). After #1; needs #3 upshot semantics for correct membership. Does **not** own GDL states or dispatch.

## Acceptance criteria

- [X] 5. Recommended UI shows a distinct **Meteorites** section for meteorite jobs that reach the post-upshot / recommended surface.
- [X] Non-meteorite Recommended / In Progress / Ready sections remain unchanged for vetted-company jobs (smoke).

## Boundaries

Does **not** own GDL states (sibling 1), dispatch (sibling 2), agent prompts (sibling 3), or Create landing (sibling 4).

## In scope

- [X] `pattern.config.config-block` — `JOBS_RECOMMENDED_METEORITE_SECTION` + manifest `meteorite_section` in `src/utils/config.py`
- [X] `astral.config.config-source-of-truth` — section label + company_prefix from `METEORITE_CONFIG` / config only
- [X] `astral.standards.no-hardcoded-sets` — no inline meteorite membership sets in UI
- [X] `pattern.layers.import-discipline` / `astral.layers.import-direction` — UI reads manifest; no UI→core
- [X] `astral.layers.ui-config-driven-business-logic` — Recommended partition driven by manifest prefix
- [X] universal set — product + plan doc

## Considered but excluded

- [X] `pattern.state.entity-state-transitions` / new Recommended job states — membership by company prefix (AST-1055 already lands on shared `RECOMMENDED`)
- [X] Dispatch / `score_floor` — AST-1054
- [X] `meteorite_like` / `meteorite_upshot` prompts — AST-1055
- [X] Create landing — AST-1056
- [X] Parallel `JOB_STATES` track — AST-1053
- [X] `astral.standards.database-header-inventory` — no new tables
- [X] `astral.debug.spikes-under-debug-dir` — no spikes
- [X] `astral.git.engineer-test-tree-ban` — Betty owns tests/bible after Code Complete
- [X] Changing report modal / Company Upshot copy for meteorites

## Notes for planning

After AST-1053; needs AST-1055 upshot semantics. Plan: `docs/features/meteorite/ast-1057-recommended-page-meteorites-section.md`.

## Git branch (authoritative)

`origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`

### Comments

#### radia — 2026-07-29T22:45:21.004Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1057
**Publish ref:** `36ae2906635866bb367eae69ffb3e75e6391ceb6` (`origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section` — layers `{core, docs, ui, utils}` (full sibling stack). **This ticket owns:** `JOBS_RECOMMENDED_METEORITE_SECTION` + manifest `meteorite_section`; `JobsRecommended` prefix partition + `StateUiContext` type.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| `astral.agent.confidence-bounds` | scoped | conforms | No confidence math in 1057; stacked twin prompts leave contract intact |
| `astral.agent.do-task-delegation` | scoped | conforms | Stacked AST-1055 twins via existing do_task; 1057 UI-only |
| `astral.agent.grade-vector-validation` | scoped | conforms | Stacked LIKE schema unchanged; 1057 UI-only |
| `astral.batch.batch-id-first` | scoped | conforms | Stacked AST-1054 provision; claim still batch_id-first |
| `astral.batch.batch-id-format` | scoped | conforms | Untouched |
| `astral.batch.claim-process-release` | scoped | conforms | Stacked AST-1054 rows; claim→consult→release shape |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | Untouched |
| `astral.config.config-source-of-truth` | scoped | conforms | meteorite_section from METEORITE_CONFIG / JOBS_RECOMMENDED_METEORITE_SECTION |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | No pass_threshold edits; score_floor sibling AST-1054 |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Plan docs under docs/features/; no spikes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single AST-1057 plan (+ stacked sibling plans) |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test()/merge-tests; engineer code() owns src+features |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | test() owns tests/bible; engineer code() product only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Stacked core consult/dispatch; no external I/O |
| `astral.layers.import-direction` | scoped | conforms | UI←manifest; stacked core/utils import direction held |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers miss (['scripts']); paths miss (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Partition driven by manifest company_prefix |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | Stacked twins company=None JD-only prep |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | Stacked twins via run_consult_task |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | conforms | No new endpoints |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No data-layer logging |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers miss (['data']); paths miss (['src/data/**']) |
| `astral.standards.debug-contract-gated` | scoped | conforms | UI-only 1057; stacked reuse existing debug gates |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Localized useMemo + config block |
| `astral.standards.in-scope-only` | scoped | conforms | 1057 adds Recommended partition only |
| `astral.standards.logging-via-utils` | scoped | conforms | Untouched on 1057 path |
| `astral.standards.no-cross-contamination` | scoped | conforms | Meteorites excluded from vetted Recommended sections |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Prefix from manifest; no inline meteorite- in page |
| `astral.standards.public-then-helpers` | scoped | conforms | Localized useMemo change |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data |
| `astral.state.core-decides-transitions` | scoped | conforms | Stacked overlay/transitions via TASK_CONFIG |
| `astral.state.job-prior-states-enforced` | scoped | conforms | No new Recommended state; prefix partition |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No run_next daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | conforms | pages/ + contexts/ flat paths |
| `astral.ui.naming-conventions` | scoped | conforms | JobsRecommended / StateUiContext naming intact |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | No worker change |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1057) onto tip |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | Work on sub/* only |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1052/AST-1057-… |
| `orch.git.merge-on-checkout` | universal | conforms | No conflicting checkout rewrite |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No rewrite ops |
| `orch.git.no-dev-agent-branches` | universal | conforms | Ticket sub publish-ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | astral-AST-1052 |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Prefix membership decision documented |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match tip; boundaries held |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty owns tests/bible |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Katherine |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Assignee remains Katherine |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Role-appropriate paths per vocabulary |

## Pattern conformance

- `pattern.config.config-block` — conforms (`JOBS_RECOMMENDED_METEORITE_SECTION` + manifest)
- `pattern.layers.import-discipline` — conforms (UI←manifest; no UI→core)
- Cited statutes covered in Statutes checked

## Plan adherence

Stages 1–2 match tip: config/manifest contract; partition by `company_prefix`; Meteorites prepended when non-empty; normal sections use `normalRows` only. Self-Assessment `Single-Component` matches. Boundaries held vs GDL/dispatch/prompts/Create. No new Recommended job state.

## Findings

### fix-now
(none)

### discuss
1. **straggler ×14** — Joan excluded at plan time (Files Changed utils+ui); in-scope on three-dot vs `origin/dev` via stacked siblings + Betty tests/docs (all substance **conforms**):
   - `astral.agent.do-task-delegation`, `astral.agent.grade-vector-validation`
   - `astral.batch.batch-id-first`, `astral.batch.batch-id-format`, `astral.batch.claim-process-release`, `astral.batch.entity-agent-responses-latest-only`
   - `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`
   - `astral.layers.core-vs-external-bright-line`
   - `astral.patterns.coat-check-never-store-empty`, `astral.patterns.render-verdict-orchestrates-consult`
   - `astral.state.core-decides-transitions`, `astral.state.no-daisy-chain-in-run`

### advisory
(none)

### What’s solid
- Manifest-driven prefix; no hardcoded `meteorite-` in page; vetted Recommended sections unchanged for non-meteorite jobs.

### Recommended actions
- Katherine: acknowledge stragglers → resolve-child → User Testing.

**Notes:** Joan plan-rubric APPROVED. Docs append @ `36ae2906`.

context_tokens≈26000

#### betty — 2026-07-29T22:41:23.825Z
1. `tests/component/utils/test_config.py::TestAst1057MeteoriteRecommendedSection` — `JOBS_RECOMMENDED_METEORITE_SECTION` + `build_state_ui_manifest()["jobs"]["recommended"]["meteorite_section"]`; Recommended sections smoke unchanged
2. `tests/component/frontend/pages/test_JobsRecommended.test.tsx` — Meteorites prepend for `meteorite-` company jobs; omit when none; vetted Recommended/In Progress/Ready counts intact
3. Fixture `stateUiManifestFixture.ts` — `meteorite_section` aligned with config

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1057MeteoriteRecommendedSection \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
```

**Pass:** pytest + Vitest green on tip.

**Broken/revised:** none — additive.
**Integration:** none.

**Publish:** `origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section` @ `37796488`
`merge-tests(AST-1057): origin/tests ef117983`

**Bible shasums on publish-ref:**
- `docs/test-bible/utils/config.md` `6f98a36c11d1ddc8eaf60997914421a871aacf4f`
- `docs/test-bible/frontend/pages.md` `9d1f4cbb997e212416b2f4893d35db865f04e8cf`

#### joan — 2026-07-29T22:34:25.469Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1057
**Overall:** APPROVED
**Plan tip:** `c2ce7f3b4c1ce7056e9c8b12458e4310724a755f` @ `origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`
**Layers:** utils, ui | **Change types:** add, modify

## Traceability

### Parent AC → plan stages

| Parent AC | Mapping |
|-----------|---------|
| AC1 JOB_STATES | N/A — AST-1053 |
| AC2 dispatch score_floor | N/A — AST-1054 |
| AC3 meteorite_like | N/A — AST-1055 |
| AC4 meteorite upshot | N/A — AST-1055 (dependency; shared RECOMMENDED landing enables membership) |
| AC5 Recommended Meteorites section | Stages 1–2 (config/manifest + JobsRecommended partition) |
| AC6 Create → METEORITE_NEW | N/A — AST-1056 |
| AC7 fail + non-meteorite smoke | Stage 2 — normal sections iterate non-meteorite rows only |
| AC8 Style D debug | N/A — UI-only; no new backend debug paths |

### Child AC → plan stages

| Child AC | Stages |
|----------|--------|
| AC5 distinct Meteorites section for post-upshot surface | 1–2 |
| Non-meteorite Recommended/In Progress/Ready unchanged | 2 (normalRows-only grouping) |

### Plan stages → definition

| Stage | Definition |
|-------|------------|
| 1 Config + manifest meteorite_section | Architectural config-block; SoT for label/prefix |
| 2 JobsRecommended partition + StateUi type | Functional distinct Meteorites section; import discipline UI←manifest |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | Test-tree out of scope |
| orch.git.commit-vocabulary | conforms | No commit ops |
| orch.git.flow-direction-inviolable | conforms | sub under AST-1052 |
| orch.git.ftr-sub-topology | conforms | Publish ref matches Git table |
| orch.git.merge-on-checkout | conforms | No alternate merge |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite |
| orch.git.no-dev-agent-branches | conforms | Uses sub/* |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-1052 |
| orch.git.three-permanent-branches | conforms | Untouched |
| orch.pipeline.call-susan-for-product-decisions | conforms | Prefix membership decision documented |
| orch.pipeline.plan-is-bible | conforms | Stages are implementation bible |
| orch.pipeline.project-scoped-queues | conforms | Single child |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready path |
| orch.roles.archie-approves-statutes | conforms | No statute authorship |
| orch.roles.betty-owns-test-tree | conforms | Betty owns tests |
| orch.roles.chuckles-never-ticket-assignee | conforms | N/A |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer Katherine |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No confidence math |
| astral.config.config-source-of-truth | conforms | Section contract from METEORITE_CONFIG / JOBS_RECOMMENDED_METEORITE_SECTION |
| astral.config.pass-threshold-vs-score-floor | conforms | No score_floor/pass_threshold edits |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src + plan |
| astral.layers.import-direction | conforms | UI reads manifest; no UI→core |
| astral.layers.ui-config-driven-business-logic | conforms | Partition driven by manifest company_prefix |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new endpoints; existing /api/jobs+manifest |
| astral.standards.data-raises-caller-logs | conforms | No data-layer edits |
| astral.standards.debug-contract-gated | conforms | No new backend debug lines |
| astral.standards.dry-and-focused-functions | conforms | Reuses existing section/table markup |
| astral.standards.in-scope-only | conforms | GDL/dispatch/prompts/Create deferred |
| astral.standards.logging-via-utils | conforms | Untouched |
| astral.standards.no-cross-contamination | conforms | Meteorites excluded from vetted state sections |
| astral.standards.no-hardcoded-sets | conforms | No inline meteorite- string; prefix from manifest |
| astral.standards.public-then-helpers | conforms | Localized useMemo change |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.state.job-prior-states-enforced | conforms | Explicitly refuses new METEORITE_RECOMMENDED state |
| astral.ui.frontend-file-placement | conforms | pages/ + contexts/ flat paths |
| astral.ui.naming-conventions | conforms | JobsRecommended / StateUiContext naming intact |
| astral.ui.single-gunicorn-worker | conforms | No worker change |

## Considered and excluded

**Considered:** all Statute verdicts rows (18 universal + 21 scoped).

**Excluded:**
- astral.agent.do-task-delegation — layers/paths miss (core)
- astral.agent.grade-vector-validation — layers/paths miss
- astral.batch.batch-id-first — layers/paths miss
- astral.batch.batch-id-format — layers/paths miss
- astral.batch.claim-process-release — layers/paths miss
- astral.batch.entity-agent-responses-latest-only — layers/paths miss
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — docs miss
- astral.git.engineer-test-tree-ban — tests paths miss
- astral.layers.core-vs-external-bright-line — layers/paths miss
- astral.layers.scripts-exempt-from-layer-rules — scripts miss
- astral.patterns.coat-check-never-store-empty — core miss
- astral.patterns.render-verdict-orchestrates-consult — core miss
- astral.standards.database-header-inventory — data miss
- astral.state.core-decides-transitions — core miss
- astral.state.no-daisy-chain-in-run — core miss

## Findings

None fix-now.

- **acceptable** — Membership by `METEORITE_CONFIG` company prefix (not a new Recommended state); documented Decision; aligns with AST-1055 shared RECOMMENDED landing.
- **acceptable** — One Meteorites section spanning RECOMMENDED / BUILD_ARTIFACTS / CANDIDATE_REVIEW; actions still key off `job.state`.
- **acceptable** — Rules self-review typo “AC6 smoke” means child non-meteorite smoke AC / parent AC7; substance correct.

## R6 checklist (abbrev)

Definition fidelity OK (AC5 + smoke); UI partition via manifest OK; file placement OK; no hardcoded prefix in page; self-assessment Conf high / Risk Medium honest.

— Joan
context_tokens≈72000

#### katherine — 2026-07-29T22:32:17.275Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1052/AST-1057-recommended-page-meteorites-section/docs/features/meteorite/ast-1057-recommended-page-meteorites-section.md

**Scope:** Single-Component — Recommended list UI + config/manifest `meteorite_section`; no GDL/dispatch.

**Conf:** high — partition by `METEORITE_CONFIG` company prefix already on shared Recommended states after AST-1055; page already manifests sections from config.

**Risk:** Medium — wrong prefix filter could hide vetted Recommended jobs or mix meteorites into normal sections; mitigated by literal `short_name_prefix` reuse and excluding meteorite rows from state sections.

---

# AST-1057 — Recommended page Meteorites section

**Linear:** [AST-1057](https://linear.app/astralcareermatch/issue/AST-1057/recommended-page-meteorites-section-processing-meteorites)
**Parent:** [AST-1052](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites) — Processing meteorites
**Publish ref:** `origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`

Show a distinct **Meteorites** section on the Recommended page for post-upshot meteorite-track jobs (company short_name under `METEORITE_CONFIG["short_name_prefix"]`), while non-meteorite jobs stay in the existing Recommended / In Progress / Ready state sections. Does **not** own GDL states, dispatch, agent prompts, or Create landing.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add meteorite Recommended section block; expose on `build_state_ui_manifest()` | utils |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Type the new `meteorite_section` manifest field | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Partition rows: Meteorites section vs normal state sections | ui |

## Stage 1: Config + state UI manifest — Meteorites section contract

**Done when:** Manifest `jobs.recommended.meteorite_section` exposes `section_id`, `label`, and `company_prefix` from `METEORITE_CONFIG`; no GDL / dispatch / Create / agent_task changes.

1. In `src/utils/config.py`, immediately after `JOBS_RECOMMENDED_UI_SECTIONS` (and before `JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS` is fine), add:

```python
# AST-1052 / AST-1057: Recommended page — distinct Meteorites section membership.
# Jobs already land in RECOMMENDED / BUILD_ARTIFACTS / CANDIDATE_REVIEW after meteorite_upshot
# (AST-1055); partition by company short_name prefix, not by a new job state.
JOBS_RECOMMENDED_METEORITE_SECTION = {
    "section_id": "meteorites",
    "label": "Meteorites",
    "company_prefix": METEORITE_CONFIG["short_name_prefix"],  # "meteorite-"
}
```

Assert: `JOBS_RECOMMENDED_METEORITE_SECTION["company_prefix"]` equals `METEORITE_CONFIG["short_name_prefix"]` and is a non-empty `str`. Do **not** invent a parallel `METEORITE_RECOMMENDED` job state.

⚠️ **Decision — membership by company short_name prefix, not state:** After AST-1055, meteorite upshot lands on shared `RECOMMENDED` (priors already allow `METEORITE_PASSED_LIKE` / `METEORITE_PASSED_LIKE_RETRY`). A new Recommended state would duplicate the surface and break Generate Artifacts / Ready flows. Prefix membership reuses `METEORITE_CONFIG` as the single source of truth for placeholder employers.

2. In `build_state_ui_manifest()`, under the existing `"recommended"` dict, add:

```python
"meteorite_section": {
    "section_id": JOBS_RECOMMENDED_METEORITE_SECTION["section_id"],
    "label": JOBS_RECOMMENDED_METEORITE_SECTION["label"],
    "company_prefix": JOBS_RECOMMENDED_METEORITE_SECTION["company_prefix"],
},
```

Do **not** add extra rows to `JOBS_RECOMMENDED_UI_SECTIONS` / `RECOMMENDED_JOB_STATES` (those stay state-driven for non-meteorite sections). Do **not** edit `TASK_CONFIG`, `METEORITE_DISPATCH_TASKS`, Create defaults, or agent_task JSON.

**Done when (recheck):** `build_state_ui_manifest()["jobs"]["recommended"]["meteorite_section"]["company_prefix"] == "meteorite-"`; `python3 -m py_compile src/utils/config.py` succeeds.

## Stage 2: Recommended page — Meteorites section UI

**Done when:** On `/jobs/recommended`, meteorite-company jobs appear under a **Meteorites** heading (when any exist); the existing Recommended / In Progress / Ready sections list only non-meteorite jobs for those states; empty-state and report modal behavior for remaining jobs unchanged.

1. In `src/ui/frontend/src/contexts/StateUiContext.tsx`, extend `StateUiManifest.jobs.recommended` with optional:

```ts
meteorite_section?: {
  section_id: string
  label: string
  company_prefix: string
}
```

2. In `src/ui/frontend/src/pages/JobsRecommended.tsx`, update the `sections` `useMemo` (currently groups solely by `job.state` against `manifest.jobs.recommended.sections`):

- Read `prefix = manifest.jobs.recommended.meteorite_section?.company_prefix ?? ""`.
- Define `isMeteoriteJob(job) => Boolean(prefix) && job.company.startsWith(prefix)`.
- Split `rows` into `meteoriteRows` and `normalRows` using that predicate.
- Build **normal** state sections exactly as today, but iterate **`normalRows` only** (so meteorite jobs never appear under Recommended / In Progress / Ready).
- If `meteoriteRows.length > 0` and `meteorite_section` is present, **prepend** one section object:

```ts
{
  state: meteorite_section.section_id,  // sort-key / React key — "meteorites", not a JOB_STATES value
  label: meteorite_section.label,
  jobs: meteoriteRows,
}
```

  before the normal state sections. Keep legacy unmapped handling on **`normalRows` only**.

- Reuse the existing table markup for the Meteorites section (same columns, sort, row click → Job Analysis Report, `CandidateJobRowActions`). Do **not** invent a second table design.

⚠️ **Decision — one Meteorites section spanning all recommended-surface states:** Meteorite jobs in `RECOMMENDED`, `BUILD_ARTIFACTS`, and `CANDIDATE_REVIEW` all list under **Meteorites**. Splitting Meteorites × state would clutter the page; primary actions still key off `job.state` via existing `CandidateJobRowActions` / `primary_actions_by_state`.

⚠️ **Decision — prepend Meteorites when non-empty:** Makes the parallel track visible above the vetted Recommended stack. Do not render an empty Meteorites heading when there are zero matching rows.

3. Do **not** change `/api/jobs?view=recommended` payload shape (company field is already present). Do **not** change report modal / summary “Company Upshot” copy on this ticket. Do **not** edit `tests/` or bible.

**Done when (recheck):** `cd src/ui/frontend && npx tsc -b --noEmit` succeeds; reading `JobsRecommended.tsx` shows partition by `company_prefix` and a prepended Meteorites section; non-meteorite path still groups by `manifest.jobs.recommended.sections` states only.

## Out of scope (do not implement here)

- Parallel GDL `JOB_STATES` (AST-1053 — landed).
- Dispatch rows / `score_floor` 0 (AST-1054).
- `meteorite_like` / `meteorite_upshot` prompts (AST-1055).
- Create landing / `METEORITE_CONFIG["job_create_state"]` (AST-1056).
- Changing non-meteorite Recommended section labels, report tabs, or artifact generate API.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — Recommended list UI + config/manifest contract for one section; no core GDL / dispatch.

**Conf:** `high` — company short_name prefix already owned by `METEORITE_CONFIG`; page already manifests sections from config; partition is a localized `useMemo` change.

**Risk:** `Medium` — wrong prefix predicate could hide vetted Recommended jobs or leak meteorites into normal sections; mitigated by literal reuse of `METEORITE_CONFIG["short_name_prefix"]` and excluding meteorite rows from state sections.

## Rules self-review

- **§2.1 / config-source-of-truth / no-hardcoded-sets:** Section label + prefix live in config; UI reads via manifest only (no inline `"meteorite-"` string in the page).
- **§3.3 / import-direction:** UI → manifest JSON from API; no UI importing core/data.
- **Boundaries:** No states / dispatch / prompts / Create edits.
- **AC6 smoke (non-meteorite Recommended unchanged):** Normal sections still driven by `JOBS_RECOMMENDED_UI_SECTIONS` + `RECOMMENDED_JOB_STATES`; only membership filter changes.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`
**Plan path:** `docs/features/meteorite/ast-1057-recommended-page-meteorites-section.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `60f68589` | `JOBS_RECOMMENDED_METEORITE_SECTION` + manifest `meteorite_section` |
| 2 | `f1c1808b` | JobsRecommended partition + StateUi `meteorite_section` type |

**Tip:** `fec43afc1fc9aaf94d4578ee63f6cced1494e686` on `origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1057
**Publish ref:** `37796488b181d764bf4308f7ae1a5334043d1a96` (`origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`)
**Overall:** DISCUSS

### What’s solid
- `JOBS_RECOMMENDED_METEORITE_SECTION` + manifest `meteorite_section`; prefix from `METEORITE_CONFIG`.
- JobsRecommended partitions by manifest prefix; meteorites prepended; normal sections use normalRows only.
- No hardcoded `meteorite-` in the page; no new Recommended job state.

### Issues
- **discuss (straggler ×14):** Joan excluded core/batch/docs/tests statutes at plan time (Files Changed utils+ui); three-dot vs `origin/dev` includes stacked sibling product + Betty tests/docs — all **conforms** on substance.

### Recommended actions
- Katherine: acknowledge stragglers → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `36ae2906` — **Overall:** DISCUSS; **fix-now:** none; **discuss:** statute straggler ×14 (all substance **conforms**); no advisory.

No product changes. Acknowledged discuss stragglers as plan-time Joan exclusions that became in-scope on the three-dot vs `origin/dev` (stacked siblings + Betty tests/docs) — no code delta. Advanced to **User Testing**.

