<!-- linear-archive: AST-1062 archived 2026-08-07 -->

## Linear archive (AST-1062)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1062/qualify-meteorite-batch-apply-meteorite-qualified-qualify-meteorite  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1058 — Qualify Meteorite  
**Blocked by / blocks / related:** parent: AST-1058

### Description

## What this implements

Owns core/consult wiring so the `qualify_meteorite` batch (same claim/process shape as `qualify_job_listings`) writes UUID → `company_job_id`, title, `job_link`, visible JD, transitions **METEORITE_NEW → METEORITE_QUALIFIED** or **METEORITE_FAILED_QUALIFY**, Style D debug. After AST-1060; needs AST-1061 producing claimable **METEORITE_NEW** rows for full-path UAT. Does **not** author gazer ingest.

## In scope

- [X] `pattern.batch.entity-claim-process-release` — `qualify_meteorite` claim → `_run_batch_consult` → process → release (mirror `qualify_job_listings`)
- [X] `pattern.batch.entity-agent-responses` / `astral.batch.entity-agent-responses-latest-only` — RESPONSE tagging via existing `_run_batch_consult` `agent_ref` path
- [X] `astral.agent.do-task-delegation` — Ruth I/O via `do_task`; core `process_fn` persists + transitions
- [X] `astral.state.core-decides-transitions` — pass/fail/error only in consult apply
- [X] `astral.standards.debug-contract-gated` — Style D on apply path only when `debug=True`
- [X] `astral.config.config-source-of-truth` — content-gate mins on `TASK_CONFIG["qualify_meteorite"]` only (schema/states already AST-1060)

## Considered but excluded

- [X] `pattern.config.config-block` / new JOB_STATES — Ada AST-1060 (already on ftr tip)
- [X] Gazer email ingest / Playwright / dedupe — Katherine AST-1061
- [X] New Ruth batch pattern / grades-encoded decode — not this ticket; `output_type: "fields"`
- [X] `qualify_job_listings` / roster scrape / GDL rubric changes — smoke-only; no edits
- [X] Frontend / Jobs skipped section labels — AST-1060 manifests; apply only lands states
- [X] `tests/` / test-bible — Betty after Code Complete

## Acceptance criteria

- [X] 4. Batch task `qualify_meteorite` claims **METEORITE_NEW**, returns external job UUID, job title, `job_link`, and visible JD content; on success the job is on **METEORITE_QUALIFIED** with those fields as authoritative content.
- [X] 5. Meteorite `evaluate_jd` claims/grades from **METEORITE_QUALIFIED** only — not from unenriched **METEORITE_NEW**. (verify retained; retarget owned by AST-1060)
- [X] 6. Bogus / 404 / unusable extracts land on **METEORITE_FAILED_QUALIFY** (visible in Jobs skipped manifests).
- [X] 7. Non-meteorite `qualify_job_listings` / scrape / GDL paths unchanged (smoke).
- [X] 8. With `debug=True` on touched ingest/qualify paths, Style D index + `|` detail shows found vs recorded; with `debug=False`, no new debug-contract lines from those paths.

## Boundaries

- [X] Does **not** author gazer ingest. After AST-1060; pairs with AST-1061 for claimable rows. Sibling Ada owns states/config/dispatch shells.

## Notes for planning

Citations migrated into In scope / Excluded. Mirror `qualify_job_listings` claim/process exactly under key `qualify_meteorite` — no new Ruth batch pattern. Content fails via apply gates on blank/short fields (not grade vectors).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1058-qualify-meteorite`, child `sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`.

### Comments

#### radia — 2026-07-30T02:18:32.797Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1062
**Publish ref:** `3a05d08edc852060a1100ed5873d05f3dad1fd1b` (`origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified` — layers `{core, data, docs, ui, utils}` (includes stacked AST-1060/1061).
**This ticket owns:** `TASK_CONFIG["qualify_meteorite"]` min_* gates; `consult.qualify_meteorite` + `run_consult_task` branch; `_CHUNK_EXHAUST_CONSULT_JOB_KEYS`; Ad Hoc `METEORITE JOBS:` assemble.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| `astral.agent.confidence-bounds` | scoped | conforms | fields output; no grade confidence math |
| `astral.agent.do-task-delegation` | scoped | conforms | Ruth via do_task in _run_batch_consult; core process_fn persists |
| `astral.agent.grade-vector-validation` | scoped | conforms | Not grades-encoded; stays off strict-encoded frozenset |
| `astral.batch.batch-id-first` | scoped | conforms | Consult takes batch_id first; claim surface unchanged |
| `astral.batch.batch-id-format` | scoped | conforms | No new batch_id scheme |
| `astral.batch.claim-process-release` | scoped | conforms | Mirrors qualify_job_listings claim→_run_batch_consult→release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | Existing _run_batch_consult agent_ref RESPONSE path |
| `astral.config.config-source-of-truth` | scoped | conforms | min_* on TASK_CONFIG[qualify_meteorite]; states from AST-1060 |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | Content mins are apply gates, not score_floor mix-up |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss (artifacts/**, scripts/spikes/**) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Plan under docs/features/; no spikes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single AST-1062 plan (+ stacked sibling plans) |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test()/merge-tests; engineer code() owns src+features |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | test() owns tests/bible; engineer code() product only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Ruth I/O via agent/external; core owns persist/transitions |
| `astral.layers.import-direction` | scoped | conforms | core/utils/ui Ad Hoc; no new UI→core invent path |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers/paths miss (scripts) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Thin Ad Hoc live-content parity only |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | Fail skips initialize_job; pass remaps jd_text→job_description |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | Pattern A qualify_* batch (not graded render_verdict) |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | conforms | Ad Hoc on existing admin surface |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No data-layer authorship on 1062 path |
| `astral.standards.database-header-inventory` | scoped | conforms | Stacked helpers use existing job columns |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D only when debug=True |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | One wrapper; shared _run_batch_consult/initialize_job |
| `astral.standards.in-scope-only` | scoped | conforms | No gazer/GDL/qualify_job_listings edits on 1062 code |
| `astral.standards.logging-via-utils` | scoped | conforms | logger.info + debug_index/detail via utils logging |
| `astral.standards.no-cross-contamination` | scoped | conforms | Meteorite qualify branch isolated from listing qualify |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Thresholds/states in config |
| `astral.standards.public-then-helpers` | scoped | conforms | New public qualify_meteorite + nested assemble/process |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data load-time import |
| `astral.state.core-decides-transitions` | scoped | conforms | Transitions only in process_fn / batch error paths |
| `astral.state.job-prior-states-enforced` | scoped | conforms | Uses _transition_job_state_for_task; priors from AST-1060 |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | Single qualify dispatch cycle; GDL separate |
| `astral.ui.frontend-file-placement` | scoped | conforms | Stacked AdminManageEmail only; 1062 no frontend |
| `astral.ui.naming-conventions` | scoped | conforms | No new frontend routes/components on 1062 |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | Untouched |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1062) onto tip |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | Work on sub/* only |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1058/AST-1062-… |
| `orch.git.merge-on-checkout` | universal | conforms | No conflicting checkout rewrite |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No rewrite ops |
| `orch.git.no-dev-agent-branches` | universal | conforms | Ticket sub publish-ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | astral-AST-1058 |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Content-fail vs error split documented |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match tip |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty owns tests/bible |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Assignee remains Hedy |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Role-appropriate paths per vocabulary |

## Pattern conformance

- `pattern.batch.entity-claim-process-release` — conforms (mirror qualify_job_listings)
- `pattern.batch.entity-agent-responses` — conforms (existing _run_batch_consult agent_ref)
- Cited statutes covered in Statutes checked

## Plan adherence

Stages 1–2 match tip: min_* thresholds; qualify_meteorite wrapper + run_consult_task + chunk-exhaust + Ad Hoc assemble. Self-Assessment Single-Component matches. Boundaries held vs gazer (AST-1061) / config shells (AST-1060). qualify_job_listings untouched on 1062 code commits.

## Findings

### fix-now
(none)

### discuss
1. **straggler ×5** — Joan excluded at plan time; in-scope on three-dot vs `origin/dev` via stacked siblings + Betty tests/docs (all substance **conforms**):
   - `astral.debug.spikes-under-debug-dir`
   - `astral.docs.features-single-file-per-ticket`
   - `astral.git.engineer-test-tree-ban`
   - `astral.standards.database-header-inventory`
   - `astral.ui.frontend-file-placement`

### advisory
(none)

### What’s solid
- Content gates → FAILED_QUALIFY without initialize_job; pass remaps jd_text→job_description; Style D found vs recorded; chunk-exhaust parity with listing qualify.

### Recommended actions
- Hedy: acknowledge stragglers → resolve-child → User Testing.

**Notes:** Joan plan-rubric APPROVED. Docs append @ `3a05d08e`. Product tip before docs: `748ffd39`.

context_tokens≈30000

#### betty — 2026-07-30T02:15:10.219Z
## QA test manifest — AST-1062

**Publish:** `origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified` @ `748ffd39bc1454b5cd7cd93f64e2642f06ed680d`
**Betty delivery:** `merge-tests(AST-1062): origin/tests e116905571d3474d5113c79db1f0c803629352c1`

### 1. Covered paths
1. `min_job_title_length` / `min_jd_chars` — `TestAst1062QualifyMeteoriteThresholds`
2. Chunk-exhaust membership — `TestAst1062QualifyMeteoriteChunkExhaust`
3. Pass persist (`initialize_job` + QUALIFIED), content gates → FAILED_QUALIFY, identity collision, Style D off, not strict-encoded — `TestAst1062QualifyMeteorite`
4. `run_consult_task` route — revised `TestRunConsultTaskRoutes::test_routes_qualify_and_evaluate_batches`
5. Ad Hoc `METEORITE JOBS:` assemble — `TestAdhocHelpers::test_build_adhoc_live_content_qualify_meteorite`

### 2. Broken / obsolete (revised)
- Route test lacked `qualify_meteorite` arm (revised)

### 3. Run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1062QualifyMeteoriteThresholds \
  tests/component/core/test_dispatcher.py::TestAst1062QualifyMeteoriteChunkExhaust \
  tests/component/core/test_consult.py::TestAst1062QualifyMeteorite \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_qualify_and_evaluate_batches \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_build_adhoc_live_content_qualify_meteorite \
  -q
```

### 4. Bible shasums on publish tip
- `docs/test-bible/utils/config.md` `25f4c84d398346ccd2cf2cd547a298b9db91a131`
- `docs/test-bible/core/consult.md` `7f3a40ee3231a3c5b4f048f7ede8f53b5b7b77de`
- `docs/test-bible/core/dispatcher.md` `95e4a35cdeb079aa48ee7bb08d08e1b15514f75d`
- `docs/test-bible/ui/api/api_admin.md` `c40398febee7f9c9ec6a5128b959e7683e875ac3`

#### joan — 2026-07-30T02:05:55.485Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1062
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 gazer create from email shapes + Playwright before create | N/A — boundary (AST-1061) |
| AC2 post-Playwright external job-id dedupe skip | N/A — boundary (AST-1061) |
| AC3 survivors land METEORITE_NEW pre-AI | N/A — boundary (AST-1061 / create); this child claims METEORITE_NEW only |
| AC4 qualify_meteorite claims METEORITE_NEW; UUID/title/job_link/JD; success → METEORITE_QUALIFIED | Stages 1–2 (thresholds + consult wrapper / process_fn / initialize_job + pass_state) |
| AC5 meteorite evaluate_jd claims METEORITE_QUALIFIED only | Stage 2 §5 — verify retained; retarget owned by AST-1060; no evaluate_jd edits |
| AC6 bogus/404/unusable → METEORITE_FAILED_QUALIFY | Stage 1 Decision + Stage 2 process content gates → fail_state |
| AC7 non-meteorite qualify_job_listings / scrape / GDL unchanged | Stage 2 §5 — do not edit qualify_job_listings; smoke branch isolation |
| AC8 Style D debug=True found vs recorded; debug=False silent | Stage 2 assemble/process debug_index/debug_detail gated on debug |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 TASK_CONFIG min_* thresholds | Functional scope qualify failures via apply gates; `astral.config.config-source-of-truth` |
| Stage 2 qualify_meteorite wrapper + run_consult_task + chunk-exhaust + Ad Hoc assemble | Purpose/Functional scope `qualify_meteorite` batch + METEORITE_QUALIFIED after Ruth; Pattern A claim/process; child AC4–AC8 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Sub publish-ref plan()/code() path |
| orch.git.flow-direction-inviolable | conforms | Publish only to child sub ref |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1058/AST-1062-… only |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1058 epic worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Explicit Decisions; content-fail vs error split documented |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible; Betty after CC |
| orch.roles.chuckles-never-ticket-assignee | conforms | Hedy engineer build path |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | fields output; no grade confidence math |
| astral.agent.do-task-delegation | conforms | Ruth via do_task inside _run_batch_consult; core process_fn persists/transitions |
| astral.agent.grade-vector-validation | conforms | Not grades-encoded; stays out of strict-encoded frozenset |
| astral.batch.batch-id-first | conforms | Dispatcher claim surface unchanged; consult takes batch_id first |
| astral.batch.batch-id-format | conforms | No new batch_id scheme |
| astral.batch.claim-process-release | conforms | Mirrors qualify_job_listings claim→_run_batch_consult→release |
| astral.batch.entity-agent-responses-latest-only | conforms | Existing _run_batch_consult agent_ref RESPONSE path |
| astral.config.config-source-of-truth | conforms | min_* on TASK_CONFIG[qualify_meteorite]; states from AST-1060 |
| astral.config.pass-threshold-vs-score-floor | conforms | Content mins are apply gates, not score_floor/pass_threshold mix-up |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env introduced |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Ruth I/O via agent/external; core owns persist/transitions |
| astral.layers.import-direction | conforms | core/utils/ui only; Ad Hoc assemble mirrors existing listing qualify |
| astral.layers.ui-config-driven-business-logic | conforms | No React business rules; thin Ad Hoc live-content parity only |
| astral.patterns.coat-check-never-store-empty | conforms | Fail path skips initialize_job; pass remaps jd_text→job_description key |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Correct Pattern A qualify_* batch (not graded render_verdict) |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Ad Hoc on existing admin surface; no new open routes |
| astral.standards.data-raises-caller-logs | conforms | No data-layer authorship; tracker calls from core |
| astral.standards.debug-contract-gated | conforms | Style D only when debug=True |
| astral.standards.dry-and-focused-functions | conforms | One wrapper; shared _run_batch_consult/initialize_job |
| astral.standards.in-scope-only | conforms | No gazer/GDL/qualify_job_listings edits |
| astral.standards.logging-via-utils | conforms | logger.info + debug_index/detail via utils logging |
| astral.standards.no-cross-contamination | conforms | Stays in consult/dispatcher/config/admin Ad Hoc |
| astral.standards.no-hardcoded-sets | conforms | Thresholds/states in config; no inline state lists |
| astral.standards.public-then-helpers | conforms | New public qualify_meteorite + nested assemble/process |
| astral.standards.utils-data-late-import-only | conforms | No utils→data load-time import |
| astral.state.core-decides-transitions | conforms | Transitions only in process_fn / batch error paths |
| astral.state.job-prior-states-enforced | conforms | Uses _transition_job_state_for_task; priors from AST-1060 |
| astral.state.no-daisy-chain-in-run | conforms | Single qualify dispatch cycle; GDL separate |
| astral.ui.naming-conventions | conforms | No new frontend routes/components |
| astral.ui.single-gunicorn-worker | conforms | No worker/config change |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {utils,ui,core} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — paths src/ui/frontend/** match none

## Findings

None fix-now.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium is honest; Medium risk mitigation (mirror listing qualify; leave qualify_job_listings untouched; content gates → fail_state) is specific.

**R6 checklist:** Definition fidelity pass for child #3 (apply only). Layer/import pass. Config thresholds on TASK_CONFIG. Batch Pattern A + core transitions + debug-gated Style D pass. No gazer/GDL/scope creep.

context_tokens≈58000

— Joan

#### hedy — 2026-07-30T02:03:08.044Z
Plan published on publish-ref tip `3013c13b`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified/docs/features/meteorite/ast-1062-qualify-meteorite-batch-apply-meteorite-qualified.md

**Self-assessment**
- **Scope:** Single-Component — consult `qualify_meteorite` wrapper + `run_consult_task` / chunk-exhaust / Ad Hoc assemble + two TASK_CONFIG min thresholds; no gazer or new batch pattern.
- **Conf:** high — AST-1060 already shipped states/schema/dispatch/agent_task; apply mirrors `qualify_job_listings` → `_run_batch_consult` with a fields `process_fn`.
- **Risk:** Medium — bad persist/transition stalls meteorite GDL entry or identity columns; roster `qualify_job_listings` left untouched by construction.

Deps AST-1060 / AST-1061 are User Testing on ftr tip — plan assumes that shell; build stays on this publish-ref only.

---

# AST-1062 — qualify_meteorite batch apply → METEORITE_QUALIFIED

**Linear:** [AST-1062](https://linear.app/astralcareermatch/issue/AST-1062/qualify-meteorite-batch-apply-meteorite-qualified-qualify-meteorite)
**Parent:** [AST-1058](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite) — Qualify Meteorite
**Publish ref:** `origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`

Wires core/consult so Ruth task key `qualify_meteorite` (config/dispatch/agent_task already on tip from AST-1060) claims **METEORITE_NEW**, runs the same Pattern-A claim→`_run_batch_consult`→process→release shape as `qualify_job_listings`, persists external UUID / title / `job_link` / visible JD, and transitions **METEORITE_NEW → METEORITE_QUALIFIED** or **METEORITE_FAILED_QUALIFY** (technical batch failures → **METEORITE_ERROR_QUALIFY**). Style D on the apply path. Does **not** author gazer ingest (AST-1061) or invent a new Ruth batch pattern.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `min_job_title_length` + `min_jd_chars` on `TASK_CONFIG["qualify_meteorite"]` only | utils |
| `src/core/consult.py` | New `qualify_meteorite` batch wrapper + `run_consult_task` branch | core |
| `src/core/dispatcher.py` | Add `qualify_meteorite` to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` | core |
| `src/ui/api/api_admin.py` | Ad Hoc live-content assemble for `qualify_meteorite` (mirror listing qualify) | ui |

No gazer / meteorite create / `agent_task.json` prompt rewrite / frontend TS / `tests/` / bible (Betty after Code Complete). Do **not** edit `qualify_job_listings` behavior. Do **not** add `qualify_meteorite` to `agent._STRICT_ENCODED_BATCH_CONSULT_KEYS` (`output_type: "fields"`, not grades-encoded).

## Stage 1: Config thresholds for content fail gates

**Done when:** `TASK_CONFIG["qualify_meteorite"]` exposes the two mins below; other TASK_CONFIG / JOB_STATES / METEORITE_DISPATCH_TASKS rows unchanged; `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py`, inside the existing `"qualify_meteorite"` TASK_CONFIG block (do **not** change `response_schema`, `pass_state` / `fail_state` / `error_state`, `output_type`, or `agent_task`), add after `fallback_batch_size`:

```python
        "min_job_title_length": 5,   # same role as qualify_job_listings title gate
        "min_jd_chars": 40,          # usable visible JD floor (align with METEORITE_EMAIL_INGEST_CONFIG)
```

⚠️ **Decision — content fail via apply gates, not grade vectors:** AST-1060 chose `scored: False` + `output_type: "fields"`. Schema allows empty strings (`required` checks `None` only). Ruth may return blank / placeholder fields for bogus/404/unusable extracts; `process_fn` maps those to `fail_state` (**METEORITE_FAILED_QUALIFY**). Envelope / schema / `do_task` failures stay on `error_state` via existing `_run_batch_consult` (AST-1060 three-outcome split).

## Stage 2: `qualify_meteorite` consult batch + dispatch wiring

**Done when:** Dispatcher can invoke `qualify_meteorite` through `run_consult_task`; a claimed **METEORITE_NEW** job that receives usable Ruth fields lands on **METEORITE_QUALIFIED** with `company_job_id` / `job_title` / `job_link` columns and `job_data["job_description"]` = returned `jd_text`; content-gate fails land on **METEORITE_FAILED_QUALIFY**; `qualify_job_listings` path unchanged; Style D emits only when `debug=True`; `python3 -m py_compile src/core/consult.py src/core/dispatcher.py src/ui/api/api_admin.py` succeeds.

1. In `src/core/consult.py`, immediately after `qualify_job_listings` (before `_jd_ready_for_evaluate`), add:

```python
async def qualify_meteorite(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    """Meteorite pre-AI enrich (Pattern A). Same claim/process shape as qualify_job_listings;
    fields output (no grades). AST-1062."""
```

Implementation rules (literal):

- `task_key = "qualify_meteorite"`; `cfg = _consult_orchestration(task_key)` (no meteorite GDL overlay needed — this key already has meteorite pass/fail/error).
- Do **not** call `validate_title_batch` / filter to VALID_TITLE* (roster-only).
- Claimed jobs are already **METEORITE_NEW**; process all `jobs` passed in (dispatcher claim surface).
- When `debug`: `logger.set_debug_flag(True)`; one `debug_detail` for `batch_id` + `job_count`; per-job `debug_index` (`func="consult.qualify_meteorite"`, identifier=`_consult_job_identifier(j)`, outcome=`"input job"`) + `debug_detail` with found `job_link` and `job_description` char length from `job_data` (Style D found→recorded later in process).
- `assemble(jobs)` — 0-based numbered lines, **exclude** `astral_job_id` from live content (same position contract as listing qualify; response still carries `astral_job_id` per schema). Use:

```python
    jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
    lines = [
        f"{i:03d}: job_link: {j.get('job_link') or ''}\n"
        f"job_description: {(j.get('job_data') or {}).get(jd_key, '') or ''}"
        for i, j in enumerate(jobs)
    ]
    return "METEORITE JOBS:\n" + "\n".join(lines)
```

  Import `TRACKER_CONFIG` from `src.utils.config` if not already imported in this module.

- `process(input_job, response_job, cfg)`:
  1. `aid = response_job["astral_job_id"]`.
  2. Strip fields: `company_job_id`, `job_title`, `job_link`, `jd_text` from `response_job`.
  3. **Content fail → `cfg["fail_state"]`** (no `initialize_job`) when any of:
     - `company_job_id` empty after strip
     - `len(job_title) < cfg["min_job_title_length"]`
     - `job_link` does not start with `"http"`
     - `len(jd_text) < cfg["min_jd_chars"]`
     Transition via `_transition_job_state_for_task(task_key, [aid], cfg["fail_state"])`. When `debug`, `debug_index` + `debug_detail` with which gate failed and found vs required. When not debug, `logger.info` title/aid → fail_state. Return fail_state.
  4. **Pass path:** build `parsed_job` for `tracker.initialize_job`:

```python
     parsed_job = {
         "company_job_id": company_job_id,
         "job_title": job_title,
         "job_link": job_link,
         jd_key: jd_text,   # authoritative visible JD → job_data job_description
     }
```

     Do **not** pass a `jd_text` key into `initialize_job` (would pollute job_data). Company = `input_job["company"]`.
  5. If `initialize_job` returns `False` (identity collision / deleted): treat as content fail → `cfg["fail_state"]` (same as listing qualify collision → fail_state); do **not** transition after delete (row gone). Return fail_state.
  6. Else `_transition_job_state_for_task(task_key, [aid], cfg["pass_state"])`. When `debug`: Style D index outcome=`METEORITE_QUALIFIED` + detail `found` (response fields) vs `recorded` (re-read via `tracker.get_job(aid)` columns + `job_data[jd_key]` lengths/values). When not debug: `logger.info` → pass_state. Return pass_state.
  7. Raise `ValueError` only for unexpected programming errors (caught by `_run_batch_consult` → missing from pass/fail counts / bad_grades path). Do **not** raise for content gates — those are fail_state.

- Return `await _run_batch_consult(task_key, batch_id, jobs, assemble, process, ctx, debug, batch_chunk_index=batch_chunk_index)`.

⚠️ **Decision — reuse `initialize_job` for column write:** Same identity-collision enforcement as `qualify_job_listings`. Remap schema `jd_text` → `TRACKER_CONFIG["job_data_keys"]["job_description"]` so coat-check / `evaluate_jd` see authoritative JD under the standard key.

⚠️ **Decision — no title-screen prefilter:** Meteorite jobs already carry visible JD from gazer/create; Ruth enriches metadata. Roster `validate_title_batch` must not run.

2. In `run_consult_task` (job branch), immediately after the `qualify_job_listings` arm, add:

```python
    elif task_key == "qualify_meteorite":
        r = await qualify_meteorite(
            batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
        )
```

3. In `src/core/dispatcher.py`, add `"qualify_meteorite"` to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` (next to `"qualify_job_listings"`) so `batch_call_mode=1` uses the same widen-claim + chunk parallel waves as listing qualify.

⚠️ **Decision — chunk exhaust membership:** AST-1060 already put `qualify_meteorite` in `_DISPATCH_BATCH_CALL_MODE_ONE`. Without chunk-exhaust membership, mode-1 would claim full backlog in one consult call; listing qualify uses chunk waves — parent says “exact same batch shape.”

4. In `src/ui/api/api_admin.py` `_adhoc_live_content` (or equivalent job assemble helper around the `qualify_job_listings` branch ~1179), add a sibling branch for `task_key == "qualify_meteorite"`:

- Resolve job ids the same way as listing qualify.
- For each job: read `job_link` and `job_data[TRACKER_CONFIG["job_data_keys"]["job_description"]]`.
- Emit the same `METEORITE JOBS:\n{i:03d}: …` shape as consult `assemble` (keep Ad Hoc / production assemble in lockstep).

5. Do **not** modify `agent.py` strict-encoded frozenset. Do **not** change `qualify_job_listings`, gazer, meteorite create, or GDL `evaluate_jd` (already claims **METEORITE_QUALIFIED** from AST-1060).

**Done when (recheck):**

- `run_consult_task(..., dispatch_task_key="qualify_meteorite", ...)` reaches `qualify_meteorite`.
- Content-gate fail → `JOB_STATES` prior allows **METEORITE_NEW → METEORITE_FAILED_QUALIFY**.
- Pass → columns + `job_description` set; state **METEORITE_QUALIFIED**.
- `debug=False` produces no new `debug_index` / `debug_detail` lines from this path; `debug=True` shows index + `|`-style detail for input and recorded outcomes.
- Non-meteorite `qualify_job_listings` smoke still routes only on its own branch.

## Self-Assessment

**Scope:** `Single-Component` — consult batch apply + thin dispatcher/Ad Hoc assemble + two TASK_CONFIG threshold keys; no gazer, no new batch pattern, no frontend.

**Conf:** `high` — AST-1060 already shipped states/schema/dispatch/agent_task; this ticket mirrors `qualify_job_listings` → `_run_batch_consult` with a fields `process_fn` and known fail/error split.

**Risk:** `Medium` — wrong persist/transition would stall meteorite GDL entry or pollute identity columns; roster `qualify_job_listings` is untouched by construction but shared `_run_batch_consult` / `initialize_job` must stay behavior-stable.

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** One new wrapper; shared `_run_batch_consult` / `initialize_job` / `_transition_job_state_for_task` — no duplicated batch scaffolding.
- **§2.1 config:** Thresholds on `TASK_CONFIG["qualify_meteorite"]`; states/pass/fail/error already config-owned (AST-1060).
- **§2.2 / do-task-delegation:** Ruth I/O via `do_task` inside `_run_batch_consult`; core `process_fn` decides persist + transitions.
- **§2.4 claim-process-release / batch-id-first:** Dispatcher claim unchanged; consult processes claimed slice; chunk exhaust aligned with listing qualify.
- **§2.4.1 entity-agent-responses-latest-only:** Unchanged — `_run_batch_consult` already tags RESPONSE via `agent_ref`.
- **§2.6 core-decides-transitions:** Transitions only in consult `process_fn` / batch error paths — not in agent prompts.
- **§1.5.1 debug-contract-gated:** Style D only under `debug=True`.
- **§3.3 imports:** UI Ad Hoc may import `TRACKER_CONFIG` / database (existing pattern); no UI→core invent path for normalize.

No statute conflicts requiring `conf-!!-NONE`.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`
**Plan path:** `docs/features/meteorite/ast-1062-qualify-meteorite-batch-apply-meteorite-qualified.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `ffd116e7` | TASK_CONFIG min_job_title_length + min_jd_chars on qualify_meteorite |
| 2 | `03b0ab1f` | qualify_meteorite consult wrapper + run_consult_task + chunk-exhaust + Ad Hoc assemble |

**Tip:** `21fe8f774b0dc87110c6350b5dae3d83382415af` on `origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1062
**Publish ref:** `748ffd39bc1454b5cd7cd93f64e2642f06ed680d` (`origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`)
**Overall:** DISCUSS

### What’s solid
- `qualify_meteorite` Pattern A wrapper over `_run_batch_consult`; content gates → FAILED_QUALIFY; pass via `initialize_job` + QUALIFIED; Style D gated.
- Chunk-exhaust + Ad Hoc `METEORITE JOBS:` assemble lockstep; min_* thresholds on TASK_CONFIG only.
- No `qualify_job_listings` / gazer edits on this ticket’s code commits.

### Issues
- **discuss (straggler ×5):** Joan excluded at plan time; in-scope on three-dot vs `origin/dev` via stacked siblings + Betty tests/docs — all substance **conforms**:
  - `astral.debug.spikes-under-debug-dir`
  - `astral.docs.features-single-file-per-ticket`
  - `astral.git.engineer-test-tree-ban`
  - `astral.standards.database-header-inventory`
  - `astral.ui.frontend-file-placement`

### Recommended actions
- Hedy: acknowledge stragglers → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-30  
**Commit:** `resolve(AST-1062): — clean`

### Against Radia review (`3a05d08e` / Overall DISCUSS)

- **fix-now:** none — no product changes.
- **discuss (straggler ×5):** Acknowledged. Joan excluded at plan time; Radia re-checked on three-dot vs `origin/dev` via stacked siblings + Betty tests/docs — all substance **conforms** (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.standards.database-header-inventory`, `astral.ui.frontend-file-placement`). No further action.
- **advisory:** none.

Stages 1–2 product + Betty manifest green @ `748ffd39`; Radia docs intake @ `3a05d08e` already on publish-ref before this resolve commit.
