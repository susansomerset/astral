<!-- linear-archive: AST-1132 archived 2026-08-07 -->

## Linear archive (AST-1132)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1132/job-link-hygiene-non-job-create-skip-manage-email-create-button-for  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1130 — Manage Email create button for job lists isn't working  
**Blocked by / blocks / related:** parent: AST-1130; blocks: AST-1133

### Description

## What this implements

After #1 (AST-1131), owns tightening which http(s) candidates may Playwright-fetch and create: config-driven excludes/allow rules for non-job hosts/paths, and skip-create when the fetched page is clearly not a job posting (so min-length alone cannot admit SVG/spec pages). Preserves dedupe and Manage Email created/skipped reporting. Dedupe must be keyed by the candidate's companies only — do not bounce listings when another candidate already has the same job. Does **not** own HTML unescape (#1) or qualify ERROR bind (#3).

## In scope

- [X] `pattern.config.config-block` — extend `METEORITE_EMAIL_INGEST_CONFIG` (excludes / allow / non-job visible markers)
- [X] `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — all hygiene fragments live in config
- [X] `astral.standards.debug-contract-gated` — Style D on new skip paths in gazer ingest when `debug=True`
- [X] `astral.standards.in-scope-only` — gazer ingest + config + candidate-scoped dedupe helpers only
- [X] `pattern.state.entity-state-transitions` — create still lands **METEORITE_NEW** via existing `create_meteorite_job` (no new states)

## Considered but excluded

* `astral.agent.do-task-delegation` / qualify consult — AST-1133 owns `qualify_meteorite` apply
* `astral.layers.core-vs-external-bright-line` for new Playwright primitives — reuse existing `get_visible_text` only; no external edits
* `pattern.ui.admin-endpoint` / Manage Email UI — toast already surfaces created/skipped; no API/UI change this ticket
* `gaze_email` dispatch redesign (AST-1087 / AST-1128) — out of epic boundaries
* AST-1131 paste normalize — already on ftr; do not re-own

## Acceptance criteria

- [X] Create on a Dice “Saved jobs” multi-card HTML email (or newline-delimited job-link paste) creates **only** jobs for real job-detail postings — **zero** jobs whose `job_link` is an SVG/namespace/spec URL (e.g. `w3.org/.../svg`).
- [X] Re-running Create on the same message skips already-known links/ids without duplicating rows; dedupe scoped to the candidate's companies only.
- [X] With `debug=True` on Create/ingest, logs show per-link Style D `index N/M` headers and `|` detail for found / skipped / recorded outcomes (not summary-only).
- [X] A single-link or single-JD Create that already succeeded before this epic still succeeds.

## Boundaries

Does **not** own HTML normalize (AST-1131) or qualify path (sibling #3). Does not redesign gaze_email.

## Notes for planning

Plan: `docs/features/meteorite/ast-1132-job-link-hygiene-non-job-create-skip.md` on publish ref below.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1130-manage-email-create-button-for-job-lists-isnt-working`, child `sub/AST-1130/AST-1132-job-link-hygiene-non-job-create-skip`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-02T20:29:48.322Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1132
**Publish ref:** origin/sub/AST-1130/AST-1132-job-link-hygiene-non-job-create-skip @ `dc59cc77bca294725d1fcdb731e358704df862e5`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | No graded consult / confidence path |
| `astral.agent.do-task-delegation` | scoped | conforms | No do_task; qualify left to AST-1133 |
| `astral.agent.grade-vector-validation` | scoped | conforms | No grade vectors |
| `astral.batch.batch-id-first` | scoped | conforms | Reuses claim_job_batch company subquery shape only |
| `astral.batch.batch-id-format` | scoped | conforms | No batch_id generation |
| `astral.batch.claim-process-release` | scoped | conforms | No claim/process/release changes |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | No agent_data RESPONSE work |
| `astral.config.config-source-of-truth` | scoped | conforms | Excludes/allow/markers in METEORITE_EMAIL_INGEST_CONFIG |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | No scoring thresholds |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env values |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss diff (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Combined plan under docs/features — not spike notes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | No dispatch/run_next changes |
| `astral.dispatch.seed-auto-false` | scoped | conforms | No seed/dispatch_task rows |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | One docs/features plan file for AST-1132 |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test/bible only; merge-tests exception ok |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | code() commits src-only; tests from Betty |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Reuse existing Playwright fetch; decisions in core |
| `astral.layers.import-direction` | scoped | conforms | utils←config; data←utils; core←data/utils |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ∩ diff empty (['scripts']); paths miss diff (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | No UI rules; toast already surfaces created/skipped |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | No coat-check keys |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | No consult/render_verdict |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | No seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | conforms | No catalog seed |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | No boot seed path |
| `astral.seed.define-approved` | scoped | conforms | No seed define work |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | No operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | conforms | No coverage-join seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | Data helpers return bool/Optional; no data logging |
| `astral.standards.database-header-inventory` | scoped | conforms | Existing job/company tables only; bind counts match |
| `astral.standards.debug-contract-gated` | scoped | conforms | New skip paths Style D gated on debug=True |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Config fragments; shared candidate company subquery |
| `astral.standards.in-scope-only` | scoped | conforms | Hygiene+dedupe only; qualify/gaze redesign untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | Style D via existing gazer logging helpers |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | Helper/config names product-shaped |
| `astral.standards.no-cross-contamination` | scoped | conforms | Stays on email→meteorite ingest + scoped helpers |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Exclude/allow/marker sets live in config |
| `astral.standards.public-then-helpers` | scoped | conforms | Public data helpers; gates in existing ingest path |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | Create still METEORITE_NEW via create_meteorite_job |
| `astral.state.job-prior-states-enforced` | scoped | conforms | No JOB_STATES / transition edits |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No run_next / daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | config.py hygiene knobs only; no worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1132) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests/resolve vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | Publish stays on origin/sub/AST-1130/AST-1132-… |
| `orch.git.ftr-sub-topology` | universal | conforms | Child sub under AST-1130 parent topology |
| `orch.git.merge-on-checkout` | universal | conforms | No illegal merge-on-checkout recipe |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No cherry-pick/rebase/force on publish ref |
| `orch.git.no-dev-agent-branches` | universal | conforms | Uses sub/AST-1130/AST-1132-… only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Review in astral-AST-1130 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branch invented |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Empty-allow + candidate dedupe AC-aligned |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–3 match Files Changed and diff |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via test()+merge-tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee remains Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Implementer stays assignee through review |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path product commits |

## Pattern conformance

- `pattern.config.config-block` — **conforms**
- `pattern.state.entity-state-transitions` — **conforms** (still METEORITE_NEW via create_meteorite_job)

## Plan adherence

Three-dot vs origin/dev matches Stages 1–3 (config hygiene, candidate-scoped dedupe helpers with company-schema ensure, gazer allow + Gate A/B + Style D). Self-Assessment Single-Component holds. AST-1131 normalize present via resolve merge (not re-owned in AST-1132 code commits). AST-1133 qualify untouched. Joan-noted gaze_email shared-helper widening is intentional AC alignment.

## Findings

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; diff touches docs/features. Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; plan file landed. Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; tests/bible on tip via Betty. Scores **conforms** (code commits src-only). No product action — ack only.

**fix-now:** none

### What's solid

- Excludes/allow/markers in METEORITE_EMAIL_INGEST_CONFIG; empty allow keeps non-Dice newline pastes.
- SQL bind orders match plan; company schema ensure before candidate subquery.
- New skip reasons excluded_link / non_job_page emit Style D only when debug=True.
- One merge-tests(AST-1132) SHA.

### Notes

Joan plan-rubric verdict attached (APPROVED). Docs append on plan file.

context_tokens≈45000

#### betty — 2026-08-02T20:26:49.878Z
## QA test manifest

**Publish:** `origin/sub/AST-1130/AST-1132-job-link-hygiene-non-job-create-skip` @ `8dcb3a57` (`merge-tests(AST-1132): origin/tests 42790483ba42fdea9e253554df2b228365339cd7`)

### Classification

1. **Existing coverage (bible-backed):** `TestAst1061MeteoriteEmailIngest` — regression (fixtures revised for candidate-scoped company ownership).
2. **Broken / obsolete (revised this pass):**
   - `TestAst1090JobLinkExistsForCandidate` — was meteorite-name equality; now `company.candidate_id` scope.
   - AST-1061 dedupe setups — companies now saved with `candidate_id`.
3. **Gaps (this pass):** hygiene excludes / non-job visible skip / final-URL exclude / cross-candidate create + config knobs + candidate-scoped `company_job_id` helper.

### Manifest (run these)

1. `tests/component/data/database/test_jobs.py::TestAst1090JobLinkExistsForCandidate`
2. `tests/component/data/database/test_jobs.py::TestAst1132TextMatchesKnownCompanyJobIdForCandidate`
3. `tests/component/utils/test_config.py::TestAst1132MeteoriteEmailIngestHygieneConfig`
4. `tests/component/core/test_gazer.py::TestAst1132MeteoriteEmailIngestHygiene`
5. `tests/component/core/test_gazer.py::TestAst1061MeteoriteEmailIngest`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_jobs.py::TestAst1090JobLinkExistsForCandidate \
  tests/component/data/database/test_jobs.py::TestAst1132TextMatchesKnownCompanyJobIdForCandidate \
  tests/component/utils/test_config.py::TestAst1132MeteoriteEmailIngestHygieneConfig \
  tests/component/core/test_gazer.py::TestAst1132MeteoriteEmailIngestHygiene \
  tests/component/core/test_gazer.py::TestAst1061MeteoriteEmailIngest \
  -q
```

### Bible shasums on publish-ref

- `d2d01180228bbef65cfbb8648d96c43d166709b21c1a6bb1b637f55d76b5db0b` `docs/test-bible/utils/config.md`
- `2c3251a404a4d737102c71c2d74ef6e30b652348bfbe66c65f8a97fa58bae003` `docs/test-bible/core/gazer.md`
- `358c22086dadf92ca20ba1bb2c645439992001db96f40c9b2d8e053973eb2436` `docs/test-bible/data/database/jobs.md`

— Betty

#### hedy — 2026-08-02T20:25:19.802Z
origin/sub/AST-1130/AST-1132-job-link-hygiene-non-job-create-skip @ `0c04e3dc` — both candidate-scoped dedupe helpers now `_ensure_company_schema` + `_ensure_company_candidate_fk` before the company subquery.

#### betty — 2026-08-02T20:23:10.005Z
Product bug blocking QA manifest (do not advance Tests Ready).

**Symptom:** `ingest_meteorite_jobs_from_email_html` body/links paths call `job_link_exists_for_candidate` / `text_matches_known_company_job_id_for_candidate` before any `save_company`. On a DB that has candidate (+ optional job) but no `company` table yet, SQLite raises:

`sqlite3.OperationalError: no such table: company`

**Repro (component):** AST-1061 body-mode create with only `save_candidate` then ingest — fails inside the new candidate-scoped helper before create can `ensure_meteorite_company`.

**Root:** helpers run `company IN (SELECT short_name FROM company WHERE candidate_id = ?)` after `_ensure_job_schema` only — no company-schema ensure (global helpers never touched `company`).

**Fix (product):** ensure company schema (same pattern as other data helpers that join `company`) inside both new/widened helpers before the subquery — or otherwise guarantee the table exists for empty-candidate first Create.

**Also fails the same way:** links-mode path that reaches `job_link_exists_for_candidate` before create on a fresh candidate.

Leaving **Code Complete**, assignee Hedy. Will resume manifest after the helper schema fix lands on the publish ref.

— Betty

#### joan — 2026-08-02T20:16:07.017Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1132
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Create list paste → only real job-detail jobs; zero SVG/namespace/spec `job_link`; also newline-delimited | Stages 1+3 — expanded excludes, empty allow (not Dice-locked), post-fetch non-job markers; residual normalize cases caught |
| AC2 Clean ATS `job_link` (no nested auto-link markup) | N/A — boundary (AST-1131); this child filters residual bad hrefs post-normalize |
| AC3 Re-Create dedupe; candidate-company scope only (not cross-candidate bounce) | Stages 2–3 — widen `job_link_exists_for_candidate` + new `text_matches_known_company_job_id_for_candidate` |
| AC4 `qualify_meteorite` → QUALIFIED with title + company_job_id | N/A — boundary (AST-1133) |
| AC5 `debug=True` Style D per-link found/skipped/recorded | Stage 3 — new skip reasons + existing Style D preserved |
| AC6 Single-link / single-JD Create still succeeds | Stage 3 Done-when; empty allow + gates only when markers/excludes hit |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 Config knobs | Architectural config-block; Functional scope job-link selection gates |
| Stage 2 Candidate-scoped dedupe helpers | Parent AC3 candidate-company dedupe note; Functional scope existing dedupe stays |
| Stage 3 Gazer filters + ingest gates | Purpose/Functional scope non-job never become meteorites; Style D; create still METEORITE_NEW |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub ref with plan()/code() vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/AST-1130/AST-1132-… |
| orch.git.ftr-sub-topology | conforms | Child ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1130/AST-1132-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1130 |
| orch.git.three-permanent-branches | conforms | Does not invent permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; empty-allow + candidate dedupe are AC-aligned |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan gate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.agent.confidence-bounds | conforms | No graded consult path |
| astral.agent.do-task-delegation | conforms | No do_task; qualify left to AST-1133 |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | No batch claim changes; reuses claim_job_batch company subquery shape only |
| astral.batch.batch-id-format | conforms | No batch_id generation |
| astral.batch.claim-process-release | conforms | No claim/process/release changes |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE work |
| astral.config.config-source-of-truth | conforms | Excludes/allow/markers extend METEORITE_EMAIL_INGEST_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values |
| astral.dispatch.run-next-is-chain-authority | conforms | No dispatch/run_next changes |
| astral.dispatch.seed-auto-false | conforms | No seed/dispatch_task rows |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Reuse existing Playwright fetch; decisions in core; no external edits |
| astral.layers.import-direction | conforms | utils←config; data←utils; core←data/utils; no illegal imports |
| astral.layers.ui-config-driven-business-logic | conforms | No React rules; toast already surfaces created/skipped |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.seed.agent-tables-in-repo-json | conforms | No seed JSON |
| astral.seed.archie-catalog-wins | conforms | No catalog seed |
| astral.seed.boot-only-not-hot-path | conforms | No boot seed path |
| astral.seed.define-approved | conforms | No seed define work |
| astral.seed.operator-rows-stay-deleted | conforms | No operator seed rows |
| astral.seed.other-via-coverage-join | conforms | No coverage-join seed |
| astral.standards.data-raises-caller-logs | conforms | Data helpers return bool/Optional; no data-layer logging |
| astral.standards.database-header-inventory | conforms | Uses existing job/company tables only; no new table inventory |
| astral.standards.debug-contract-gated | conforms | New skip paths Style D gated on debug=True |
| astral.standards.dry-and-focused-functions | conforms | Config-driven fragments; shared candidate company subquery |
| astral.standards.in-scope-only | conforms | Hygiene+dedupe only; normalize/qualify/gaze redesign excluded |
| astral.standards.logging-via-utils | conforms | Style D via existing gazer logging helpers |
| astral.standards.names-not-ticket-ids | conforms | Config/helper names product-shaped |
| astral.standards.no-cross-contamination | conforms | Stays on email→meteorite ingest + scoped helpers |
| astral.standards.no-hardcoded-sets | conforms | Exclude/allow/marker sets live in config; core reads cfg |
| astral.standards.public-then-helpers | conforms | Public data helpers; ingest gates in existing public path |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import |
| astral.state.core-decides-transitions | conforms | Create still METEORITE_NEW via existing create_meteorite_job |
| astral.state.job-prior-states-enforced | conforms | No JOB_STATES / transition edits |
| astral.state.no-daisy-chain-in-run | conforms | No run_next / daisy-chain |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker config changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {core,data,utils} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan {core,data,utils} empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan {core,data,utils} empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan {core,data,utils} empty
- astral.ui.naming-conventions — layers {ui} ∩ plan {core,data,utils} empty

## Findings

None fix-now.

**discuss (non-blocking):** Widening `job_link_exists_for_candidate` also affects existing `gaze_email` callers. Plan explicitly aligns that helper with parent AC (candidate-scoped); acceptable shared-helper effect, not scope creep into gaze_email redesign.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium matches over-skip risk; empty `link_allow_substrings` correctly avoids Dice-locking newline pastes.

**R6 checklist:** Definition fidelity pass for child #2. Layers/import pass. Config owns exclude/allow/markers. Data helpers SQL-only. No UI. Create state unchanged. Boundaries vs AST-1131/1133 respected.

context_tokens≈42000

— Joan

#### hedy — 2026-08-02T20:13:55.029Z
Plan published on `origin/sub/AST-1130/AST-1132-job-link-hygiene-non-job-create-skip` @ `49adb7c6`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1130/AST-1132-job-link-hygiene-non-job-create-skip/docs/features/meteorite/ast-1132-job-link-hygiene-non-job-create-skip.md

**Self-assessment**
- **Scope:** Single-Component — config + candidate-scoped dedupe helpers + gazer ingest gates only; no UI/API/qualify.
- **Conf:** high — reuses `METEORITE_EMAIL_INGEST_CONFIG`, Style D, and existing `job_link_exists_for_candidate` pattern; gate order is concrete.
- **Risk:** Medium — over-aggressive exclude/marker lists could skip real postings; widening link-exists to all candidate companies also affects `gaze_email` (AC-aligned). Empty `link_allow_substrings` avoids Dice-locking newline pastes.

#### chuckles — 2026-08-02T20:10:47.510Z
[thread-missing] Cursor chat `b5e12956-24a2-4cd2-a71e-b0dcf3216e24` has no local `store.db` on **this host** (`/home/susan/.cursor/chats/f83db4c242138fcc700ad43e401aac8e/b5e12956-24a2-4cd2-a71e-b0dcf3216e24/store.db`).

Minted replacement `7e8b2b69-c68a-469e-bcff-80d9c29a6796` for Hedy · engineer on AST-1130; updating ## Team. Continuing with first-spawn.

— Chuckles

---

# AST-1132 — Job-link hygiene + non-job create skip

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1132/job-link-hygiene-non-job-create-skip-manage-email-create-button-for  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working  

**Publish ref (origin):** `sub/AST-1130/AST-1132-job-link-hygiene-non-job-create-skip`  
**Parent integration ref:** `ftr/AST-1130-manage-email-create-button-for-job-lists-isnt-working`

After AST-1131 normalize, owns tightening which http(s) candidates may Playwright-fetch and create: config-driven exclude/allow substring rules for non-job hosts/paths, post-fetch skip when the final URL or visible text is clearly not a job posting (so `min_jd_chars` alone cannot admit SVG/spec pages), and candidate-scoped dedupe for Manage Email Create (same link/id on another candidate must not block create). Preserves created/skipped reporting and Style D debug. Does **not** own HTML unescape (AST-1131) or `qualify_meteorite` apply (AST-1133). Does not redesign `gaze_email`.

**Current gap (tip after AST-1131 merge):** `_meteorite_email_candidate_links` only excludes unsubscribe/tracking fragments — not `w3.org` / SVG / schema hosts. `ingest_meteorite_jobs_from_email_html` uses global `job_link_exists` + global `text_matches_known_company_job_id`, which bounces cross-candidate duplicates contrary to parent AC. Post-fetch gate is length-only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `METEORITE_EMAIL_INGEST_CONFIG` with expanded excludes, optional allow substrings, and non-job visible-text markers | utils |
| `src/data/database.py` | Widen `job_link_exists_for_candidate` to all companies for the candidate; add `text_matches_known_company_job_id_for_candidate` | data |
| `src/core/gazer.py` | Apply allow filter in link discovery; post-fetch URL/content non-job skip; switch ingest dedupe to candidate-scoped helpers; Style D for new skip reasons | core |

No UI, API, Playwright, inbox strip, qualify, `gaze_email` redesign, or `tests/` / bible changes (Betty after Code Complete).

---

## Stage 1: Config knobs for hygiene + non-job skip

**Done when:** `METEORITE_EMAIL_INGEST_CONFIG` exposes the keys below as importable literals; no data/gazer behavior changes yet.

1. In `src/utils/config.py`, inside `METEORITE_EMAIL_INGEST_CONFIG`, **replace** the existing `link_exclude_substrings` tuple with:

```python
    # Lowercased path/host fragments that disqualify an href (unsubscribe, tracking,
    # namespace/spec/asset URLs — AST-1132 hygiene).
    "link_exclude_substrings": (
        "unsubscribe",
        "mailto:",
        "list-manage.com",
        "/preferences",
        "/email-settings",
        "w3.org",
        "/2000/svg",
        "schemas.xmlsoap.org",
        "xmlns=",
    ),
```

2. Immediately after `link_exclude_substrings`, add:

```python
    # When non-empty: after exclude check, href must contain ≥1 allow substring (casefold)
    # to remain a Playwright candidate. Empty = no allow filter (newline pastes of any
    # ATS URL still work — not Dice-exclusive).
    "link_allow_substrings": (),
    # After Playwright: if any marker appears in visible text (casefold), skip create
    # even when len(text) >= min_jd_chars (SVG/spec docs that are "long enough").
    "non_job_visible_substrings": (
        "www.w3.org/2000/svg",
        "w3.org/2000/svg",
        "schemas.xmlsoap.org",
        "xml schema",
        "svg namespace",
    ),
```

3. Update the top-of-file config inventory one-liner for `METEORITE_EMAIL_INGEST_CONFIG` to mention AST-1132 hygiene / non-job skip (keep AST-1061 + AST-1131 mentions).

⚠️ **Decision — extend ingest config, not a new block:** Parent architectural definition says extend `METEORITE_EMAIL_INGEST_CONFIG`. Thresholds stay next to link discovery / min_jd.

⚠️ **Decision — empty allow by default:** Parent forbids Dice-only coding and requires `\n`-delimited arbitrary job-link pastes. An empty `link_allow_substrings` keeps allow as a real config knob without locking create to `/job-detail/`. Operators can tighten later without a code change.

⚠️ **Decision — exclude `xmlns=` as substring:** Catches rare residual attribute-shaped hrefs if normalize missed a case; casefold match on the full href string.

---

## Stage 2: Candidate-scoped dedupe helpers

**Done when:** `job_link_exists_for_candidate` scopes to all companies owned by the candidate; `text_matches_known_company_job_id_for_candidate` is importable and mirrors the global inverted match with the same company scope; global helpers remain for any non-ingest callers; no gazer wiring yet.

1. In `src/data/database.py`, update `job_link_exists_for_candidate` docstring to:  
   `True when any job under a company owned by this candidate has this exact job_link.`  
   Replace the meteorite-`short_name_template` company equality with the same candidate company subquery used by `claim_job_batch`:

```sql
SELECT 1 FROM job
 WHERE job_link = ?
   AND job_link IS NOT NULL AND TRIM(job_link) != ''
   AND company IN (SELECT short_name FROM company WHERE candidate_id = ?)
 LIMIT 1
```

Bind order: `(link, cid)`. Remove the `METEORITE_CONFIG["short_name_template"]` local if it becomes unused in this function (do not remove unrelated METEORITE_CONFIG imports used elsewhere in the file).

⚠️ **Decision — all candidate companies, not meteorite-only:** Parent AC: “dedupe is keyed by the candidate's companies only.” `claim_job_batch` already uses `company IN (SELECT short_name FROM company WHERE candidate_id = ?)`. Widening this helper also aligns `gaze_email` (existing caller) with the same AC without a second fork.

2. Immediately after `job_link_exists_for_candidate`, add:

```python
def text_matches_known_company_job_id_for_candidate(
    candidate_id: str, text: str
) -> Optional[str]:
    """Inverted company_job_id match scoped to this candidate's companies.

    Returns the matched company_job_id when any non-empty company_job_id on a job
    under the candidate's companies appears as a substring of text; else None.
    """
```

Empty/`None` `text` or empty `candidate_id` → return `None` without querying.

SQL:

```sql
SELECT company_job_id FROM job
 WHERE company_job_id IS NOT NULL AND TRIM(company_job_id) != ''
   AND company IN (SELECT short_name FROM company WHERE candidate_id = ?)
   AND ? LIKE '%' || company_job_id || '%'
 LIMIT 1
```

Bind order: `(cid, text)`.

3. Keep `job_link_exists` and `text_matches_known_company_job_id` unchanged (global). Do not delete them.

**Done when (recheck):** Helpers importable; `python3 -m py_compile src/data/database.py` succeeds.

---

## Stage 3: Gazer link filter + ingest gates + candidate dedupe

**Done when:** Link discovery applies exclude then allow; links mode re-checks final URL against excludes, skips non-job visible markers, and dedupes with candidate-scoped helpers; body mode uses candidate-scoped id match; new skip reasons appear in `skipped` and Style D when `debug=True`; single-link / body create path still creates when gates pass.

1. In `src/core/gazer.py` imports from `src.data.database`:  
   - Remove `job_link_exists` and `text_matches_known_company_job_id` if unused after this stage.  
   - Add `job_link_exists_for_candidate` and `text_matches_known_company_job_id_for_candidate`.

2. In `_meteorite_email_candidate_links`, after the existing exclude check (`if any(frag in low for frag in excludes): continue`), apply allow:

```python
    allows = tuple(s.casefold() for s in cfg["link_allow_substrings"])
    ...
        if allows and not any(frag in low for frag in allows):
            continue
```

Do not Playwright-fetch excluded or non-allowed hrefs (they do not enter `links` and do not need `skipped` rows — same silent drop as today's unsubscribe excludes).

3. In `ingest_meteorite_jobs_from_email_html` **links** branch, inside `_one`, after successful Playwright fetch and `link = (final_url or url).strip() or url`, **before** dedupe / min_chars / create, add two gates (use `cfg` already loaded; casefold helpers inline):

**Gate A — final URL exclude (redirect hygiene):**  
- `low_link = link.casefold()`  
- `excludes = tuple(s.casefold() for s in cfg["link_exclude_substrings"])`  
- If `any(frag in low_link for frag in excludes)`: append skipped `{reason: "excluded_link", url: link, matched_company_job_id: None}`; if `debug`, Style D `debug_index` with `outcome="skipped-excluded"` and `debug_detail("reason=excluded_link")`; `return`.

**Gate B — non-job visible text:**  
- `markers = tuple(s.casefold() for s in cfg["non_job_visible_substrings"])`  
- `hay_vis = (text or "").casefold()`  
- If `markers` and `any(m in hay_vis for m in markers)`: append skipped `{reason: "non_job_page", url: link, matched_company_job_id: None}`; if `debug`, Style D `outcome="skipped-non-job"` and `debug_detail("reason=non_job_page")`; `return`.

4. Replace dedupe calls in the **links** branch:  
   - `if job_link_exists(link):` → `if job_link_exists_for_candidate(candidate_id, link):` (same skipped reason `known_job_link`, same Style D).  
   - `matched = text_matches_known_company_job_id(haystack)` → `matched = text_matches_known_company_job_id_for_candidate(candidate_id, haystack)` (same skipped reason `known_company_job_id`).

5. In the **body** branch, replace  
   `matched = text_matches_known_company_job_id(text)`  
   with  
   `matched = text_matches_known_company_job_id_for_candidate(candidate_id, text)`  
   (same skipped shape / Style D). Body mode has no job_link; leave that path without a link-exists check.

6. Keep existing `min_jd_chars` gate, `create_meteorite_job`, concurrency, return shape, and AST-1131 normalize call unchanged. Do not edit `inbox.py`, `api_inbox.py`, or Manage Email UI — they already surface `created` / `skipped`.

7. Style D contract: every new skip path above emits `debug_index` + `debug_detail` only when `debug=True` (same `func="gazer.meteorite_email_ingest"`, `index`/`total`/`identifier` pattern as existing skips). No summary-only replacement for per-link headers.

⚠️ **Decision — silent drop at discovery vs skipped row:** Pre-fetch exclude/allow continue to omit URLs from `links` (no Playwright cost). Post-fetch exclude/non-job use explicit `skipped` reasons so Create toasts can show hygiene skips when a redirect or fat SVG page slips past discovery.

⚠️ **Decision — do not touch qualify or gaze_email orchestration:** AST-1133 owns qualify ERROR bind. `gaze_email` already uses `job_link_exists_for_candidate`; Stage 2 widening is the only intentional shared-helper effect.

**Done when (recheck):**  
- A Dice Saved-jobs HTML (post-1131 normalize) with residual `w3.org` / SVG hrefs yields **zero** created rows with those `job_link`s (filtered or `excluded_link` / `non_job_page`).  
- Re-Create on the same candidate skips known links/ids; a second candidate can still create the same ATS URL.  
- `debug=True` shows per-link Style D for found / skipped / recorded including new skip outcomes.  
- Single-link / body Create that passed before still creates when gates pass.

---

## Self-Assessment

**Scope:** `Single-Component` — config + one data helper pair + gazer ingest path only; no UI/API/qualify.

**Conf:** `high` — reuses existing `METEORITE_EMAIL_INGEST_CONFIG` / Style D / `job_link_exists_for_candidate` patterns; concrete SQL and gate order already established by AST-1061/1131.

**Risk:** `Medium` — wrong exclude/marker lists could over-skip real postings, and widening candidate-scoped link exists affects `gaze_email` callers; empty allow + conservative markers keep the blast radius small.

---

## Rules check (ASTRAL_CODE_RULES)

- §1.3 DRY: shared candidate company subquery pattern from `claim_job_batch`; no duplicated exclude lists in gazer — read config.
- §1.4 / §2.1: all fragments and markers in `METEORITE_EMAIL_INGEST_CONFIG`; no inline magic sets in core.
- §1.5.1: new debug lines gated on `debug=True` Style D only.
- §2.5 / §3.3: Playwright stays in external via existing `_meteorite_fetch_link_visible_text`; decisions stay in core; data helpers have no business branching beyond SQL scope.
- §2.6: create still lands **METEORITE_NEW** via unchanged `create_meteorite_job`; no new job states.
- Out of scope honored: no AST-1131 normalize edits, no AST-1133 qualify, no `tests/` / bible.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1130/AST-1132-job-link-hygiene-non-job-create-skip`  
**Plan path:** `docs/features/meteorite/ast-1132-job-link-hygiene-non-job-create-skip.md`  
**Built tip:** `24528f0f1d0f250441dc8c9b3efa5acce31164c5` (`24528f0f`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–3 | `24528f0f` | Config hygiene knobs + candidate-scoped dedupe helpers + gazer gates |

---

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1132
**Publish ref tip:** `8dcb3a577eec575b6cebe637cf6dde3d56149331`
**Overall:** DISCUSS

### What’s solid

- Stages 1–3 match: config excludes/allow/markers, candidate-scoped dedupe helpers (SQL bind order + company schema ensure), gazer allow filter + Gate A/B + Style D.
- Empty `link_allow_substrings` keeps newline ATS pastes; create still `METEORITE_NEW` via existing path.
- AST-1131 normalize carried via resolve merge (not re-owned); AST-1133 qualify untouched.
- Betty `test()` + one `merge-tests` SHA; engineer `code()` is src-only.

### Issues

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; diff touches `docs/features/**`. Scores **conforms**. No product action.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; plan file landed. Scores **conforms**. No product action.

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; tests/bible on tip via Betty. Scores **conforms**. No product action.

### Recommended actions

- Engineer: ack the three C4 stragglers (no src change) via `resolve-child`, then User Testing.
- Note: widened `job_link_exists_for_candidate` intentionally aligns `gaze_email` callers with candidate-company AC (Joan plan discuss already accepted).

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | No graded consult / confidence path |
| `astral.agent.do-task-delegation` | scoped | conforms | No do_task; qualify left to AST-1133 |
| `astral.agent.grade-vector-validation` | scoped | conforms | No grade vectors |
| `astral.batch.batch-id-first` | scoped | conforms | Reuses claim_job_batch company subquery shape only |
| `astral.batch.batch-id-format` | scoped | conforms | No batch_id generation |
| `astral.batch.claim-process-release` | scoped | conforms | No claim/process/release changes |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | No agent_data RESPONSE work |
| `astral.config.config-source-of-truth` | scoped | conforms | Excludes/allow/markers in METEORITE_EMAIL_INGEST_CONFIG |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | No scoring thresholds |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env values |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss diff (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Combined plan under docs/features — not spike notes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | No dispatch/run_next changes |
| `astral.dispatch.seed-auto-false` | scoped | conforms | No seed/dispatch_task rows |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | One docs/features plan file for AST-1132 |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test/bible only; merge-tests exception ok |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | code() commits src-only; tests from Betty |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Reuse existing Playwright fetch; decisions in core |
| `astral.layers.import-direction` | scoped | conforms | utils←config; data←utils; core←data/utils |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ∩ diff empty (['scripts']); paths miss diff (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | No UI rules; toast already surfaces created/skipped |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | No coat-check keys |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | No consult/render_verdict |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | No seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | conforms | No catalog seed |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | No boot seed path |
| `astral.seed.define-approved` | scoped | conforms | No seed define work |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | No operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | conforms | No coverage-join seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | Data helpers return bool/Optional; no data logging |
| `astral.standards.database-header-inventory` | scoped | conforms | Existing job/company tables only; bind counts match |
| `astral.standards.debug-contract-gated` | scoped | conforms | New skip paths Style D gated on debug=True |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Config fragments; shared candidate company subquery |
| `astral.standards.in-scope-only` | scoped | conforms | Hygiene+dedupe only; qualify/gaze redesign untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | Style D via existing gazer logging helpers |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | Helper/config names product-shaped |
| `astral.standards.no-cross-contamination` | scoped | conforms | Stays on email→meteorite ingest + scoped helpers |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Exclude/allow/marker sets live in config |
| `astral.standards.public-then-helpers` | scoped | conforms | Public data helpers; gates in existing ingest path |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | Create still METEORITE_NEW via create_meteorite_job |
| `astral.state.job-prior-states-enforced` | scoped | conforms | No JOB_STATES / transition edits |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No run_next / daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | config.py hygiene knobs only; no worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1132) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests/resolve vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | Publish stays on origin/sub/AST-1130/AST-1132-… |
| `orch.git.ftr-sub-topology` | universal | conforms | Child sub under AST-1130 parent topology |
| `orch.git.merge-on-checkout` | universal | conforms | No illegal merge-on-checkout recipe |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No cherry-pick/rebase/force on publish ref |
| `orch.git.no-dev-agent-branches` | universal | conforms | Uses sub/AST-1130/AST-1132-… only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Review in astral-AST-1130 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branch invented |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Empty-allow + candidate dedupe AC-aligned |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–3 match Files Changed and diff |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via test()+merge-tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee remains Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Implementer stays assignee through review |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path product commits |

### Pattern conformance

- `pattern.config.config-block` — **conforms**
- `pattern.state.entity-state-transitions` — **conforms** (still METEORITE_NEW via `create_meteorite_job`)

### Plan adherence

Diff matches Self-Assessment **Single-Component**. Boundaries vs AST-1131/1133 held. Three-dot vs `origin/dev` also carries AST-1131 product + Betty AST-1134 test corpus from merge history — expected rollup, not scope smuggle in AST-1132 `code()` commits.

context_tokens≈45000

---

## Resolution

**Date:** 2026-08-02  
**Review:** [code-rubric] revision=1 @ `dc59cc77` — Overall DISCUSS; **fix-now:** none.

| Finding | Action |
|---------|--------|
| discuss (C4) `astral.debug.spikes-under-debug-dir` — conforms, ack only | Acknowledged; no product change |
| discuss (C4) `astral.docs.features-single-file-per-ticket` — conforms, ack only | Acknowledged; no product change |
| discuss (C4) `astral.git.engineer-test-tree-ban` — conforms, ack only | Acknowledged; no product change |

Tip after resolve commit below; product code unchanged from Tests Passed tip.
