<!-- linear-archive: AST-997 archived 2026-08-05 -->

## Linear archive (AST-997)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-997/job-tailored-experience-on-job-array-shape-parse-resume-json-output-is  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-994 — Parse resume json output is incomplete  
**Blocked by / blocks / related:** parent: AST-994

### Description

## What this implements

Job-tailored resume hop(s) use the same experience job-array contract; may tailor accomplishments/highlights for the target job while preserving company, title, dates, location. Does **not** own craft-base parse or HTML emit.

## Acceptance criteria

6. Job-tailored resume hops accept and emit the same experience job-array shape; tailored output may change accomplishments/highlights for the target job while leaving company, title, dates, and location unchanged from the base facts.
7. When `debug=True` on touched parse/tailor hops, debug output shows what was found/recorded for the experience jobs (Style D index + detail), not only a pass/fail summary.

## Boundaries

* Does **not** own craft-base parse JSON shape — sibling **Judith craft-base: experience job array** (AST-996).
* Does **not** own HTML emit — sibling **Base + session + job builders: experience job render**.
* Does **not** invent new experience fields beyond the shared job-array contract from AST-996.

## Notes for planning

* Depends on AST-996 Experience job-array contract.
* Tailor highlights only — never rewrite factual metadata for the posting.

## Git branch (authoritative)

Per **orientation** § Branch law: parent **ftr/<parent-segment>**, child **sub/<parent-id>/<child-segment>**. Created at dispatch-parent. Publish to **origin/<sub-ref>** only.

### Comments

#### ada — 2026-07-28T02:36:01.861Z
[merge-child] publish-ref hygiene: rebuilt linear stack from `origin/ftr` (no `Merge remote-tracking` subjects; `plan(AST-997):` present).

`origin/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape` @ `18801985`

#### chuckles — 2026-07-28T02:34:30.388Z
[merge-child] blocked: validate-sub-log — git pull merge on sub (`Merge remote-tracking branch` subjects in ftr..sub range: ftr merge + AST-996 sibling merges). Also plan landed as `docs(AST-997): plan` — need canonical `plan(AST-997):`.

@Ada Lovelace — republish `origin/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape` from clean `origin/ftr/ast-994-parse-resume-json-output-is-incomplete` with linear plan|code|merge-tests|test|docs|resolve only (no `Merge remote-tracking branch`). Then Chuckles re-runs merge-child.

— Chuckles

#### radia — 2026-07-28T02:28:42.599Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-997
**Publish ref:** `7f2720d6` on `origin/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape` (baseline `origin/dev`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| --- | --- | --- | --- |
| astral.agent.confidence-bounds | scoped | conforms | core/utils touched; no graded confidence changes |
| astral.agent.do-task-delegation | scoped | conforms | pin + debug beside existing draft/finalize `do_task` validate |
| astral.agent.grade-vector-validation | scoped | conforms | no graded vectors |
| astral.batch.batch-id-first | scoped | conforms | no new batch-id APIs |
| astral.batch.batch-id-format | scoped | conforms | untouched |
| astral.batch.claim-process-release | scoped | conforms | no new claim pattern |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | untouched |
| astral.config.config-source-of-truth | scoped | conforms | finalize reuses AST-996 `_EXPERIENCE_JOB_*` objects |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | thresholds untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | conforms | no repo-root `artifacts/` dump |
| astral.debug.spikes-under-debug-dir | scoped | conforms | plan under `docs/features/**` |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one combined plan/review file for AST-997 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty `test`/`merge-tests` touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code(AST-997)` has no tests/ |
| astral.layers.core-vs-external-bright-line | scoped | conforms | pin/persist/debug in core; no external LLM edits |
| astral.layers.import-direction | scoped | conforms | utils/core (+ merged UI from 996); no ui→data in 997 code |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss (no `scripts/**`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | tip includes 996 ArtifactEditor; 997 code has no UI |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check changes |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no consult/render-verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new endpoints |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer logging |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss (`src/data/**`) |
| astral.standards.debug-contract-gated | scoped | conforms | Style D detail only when `debug=True` on tailor hops |
| astral.standards.dry-and-focused-functions | scoped | conforms | shared schema + one pin helper for draft/finalize |
| astral.standards.in-scope-only | scoped | conforms | no craft-base rewrite / no builder HTML |
| astral.standards.logging-via-utils | scoped | conforms | Style D via utils logger helpers |
| astral.standards.no-cross-contamination | scoped | conforms | layer boundaries held |
| astral.standards.no-hardcoded-sets | scoped | conforms | wire shape from config; pin fields match plan contract |
| astral.standards.public-then-helpers | scoped | conforms | public `is_experience_job_array` for tracker; pin public |
| astral.standards.utils-data-late-import-only | scoped | conforms | config-only utils; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | no state machine |
| astral.state.job-prior-states-enforced | scoped | conforms | untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | untouched |
| astral.ui.frontend-file-placement | scoped | conforms | tip UI from 996 only; existing ArtifactEditor |
| astral.ui.naming-conventions | scoped | conforms | no new UI files/routes in 997 |
| astral.ui.single-gunicorn-worker | scoped | conforms | untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip includes `merge-tests(AST-997)` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests`/`resolve` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish to child `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-994/AST-997-…` matches branch law |
| orch.git.merge-on-checkout | universal | conforms | tip merges AST-996 sub as precondition |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | work on ticket sub |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-994` |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no new `highlights` field; AC6 pin policy followed |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–5 match tip; siblings excluded |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible via Betty |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Chuckles not assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Ada through resolve; assignee left untouched |
| orch.roles.pre-commit-path-bans | universal | conforms | role path bans respected |

## Pattern conformance

none cited

## Plan adherence

Stages 1–5 match: optional finalize job-array schema (shared `items_schema`), draft normalize/validate + `(company, title)` pin (no index fallback), tracker persist/body gates, four hop prompts, Style D on draft/finalize under `debug=True`. Self-Assessment Single-Component still fits. AST-996 merge precondition satisfied. Joan plan-rubric APPROVED (rev 1).

## Findings

### fix-now
(none)

### discuss
1. **C4 straggler** — Joan excluded `astral.debug.no-repo-root-artifacts-dir`; tip in-scope — **conforms**.
2. **C4 straggler** — Joan excluded `astral.debug.spikes-under-debug-dir`; tip has `docs/features/**` — **conforms**.
3. **C4 straggler** — Joan excluded `astral.docs.features-single-file-per-ticket`; tip adds AST-997 plan — **conforms**.
4. **C4 straggler** — Joan excluded `astral.git.engineer-test-tree-ban`; tip includes Betty tests — **conforms**.
5. **C4 straggler** — Joan excluded `astral.patterns.require-auth-on-protected-endpoints`; tip has UI via 996 merge — **conforms** (no new endpoints).
6. **C4 straggler** — Joan excluded `astral.ui.frontend-file-placement`; tip UI from 996 — **conforms**.
7. **C4 straggler** — Joan excluded `astral.ui.naming-conventions`; tip UI from 996 — **conforms**.

### advisory
1. `agent.py` late-imports private `_debug_experience_jobs` (tracker correctly uses public `is_experience_job_array`).

## What’s solid

Pin-by-identity metadata lock; persist path keeps arrays; hop prompts aligned; debug gated; no builder/craft-base ownership creep.

## Notes

Plan-rubric verdict attached (Joan APPROVED). Three-dot vs `origin/dev` includes merged AST-996; stragglers are process notes only — no product fix-now.

context_tokens≈42000

#### betty — 2026-07-28T02:02:00.363Z
## QA test manifest — AST-997

**Publish:** `origin/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape` @ `fb33bcbc` (`merge-tests(AST-997): origin/tests 0b9bd01c`)

### Classification
1. **Existing coverage:** `TestAst594DraftJobResumePayload` (legacy string experience still accepted)
2. **Broken / obsolete:** none
3. **Gaps (new):** `TestAst997JobTailoredExperience` (normalize/validate/pin by company+title, prompts); `TestAst997FinalizeExperienceJobArray`; `TestAst997ExperienceJobArrayPersist`

### Manifest (test-child)

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestAst997JobTailoredExperience tests/component/core/test_candidate.py::TestAst594DraftJobResumePayload tests/component/core/test_tracker.py::TestAst997ExperienceJobArrayPersist tests/component/utils/test_config.py::TestAst997FinalizeExperienceJobArray -q`

**Pass criterion:** pytest green on the line above — not zero-arg harness / branch-lock gate.

### Bible shasums (on publish tip)
- `cef07cfff844e4b6a14620eff1426b0477a3a5335b7f49dd99b6329643f28315` `docs/test-bible/core/candidate.md`
- `a10a0a8d94566db83766ed696196aff719f0ac1389d6da41ac958cd78e61f550` `docs/test-bible/core/tracker.md`
- `2b0a632fa0cd2cc467fb9aa63fea43848041e69a7e2e25396a8de366a97d3df8` `docs/test-bible/utils/config.md`

— Betty

#### joan — 2026-07-28T01:44:11.633Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-997
**Overall:** APPROVED

**Notes:** Plan Discuss round=1 completed (concern + reply). Files Changed layer `repo admin JSON` mapped to `docs`. Tip `d51ab862`. Prior fix-now (index-first pin match) addressed in Revision 1 — `(company, title)` only, no index fallback.
**Implementer:** Ada (parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1–5 craft-base parse / session-base HTML | N/A — boundary: AST-996 / AST-998 |
| 6 Job-tailored hops same job-array shape; tailor accomplishments; pin factual metadata | Stages 1–4 |
| 7 Job-tailored HTML recognition | N/A — boundary: AST-998 |
| 8 Dates freeform | Inherited via AST-996 contract + pin preserves `dates` |
| 9 `debug=True` Style D on touched parse/tailor hops | Stage 5 covers draft/finalize; craft-base parse N/A — AST-996 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 6 accept/emit job-array; tailor accomplishments; leave company/title/dates/location from base | 1–4 |
| 7 Style D experience detail when `debug=True` on tailor hops | 5 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 finalize schema reuses shared job array | Functional scope job-tailored same shape |
| 2 draft normalize/validate + pin base facts | AC6 metadata lock + accept job-array |
| 3 tracker persist keeps arrays | Contract alignment; persist job-array |
| 4 four hop prompts tailor-accomplishments-only | AC6 policy |
| 5 Style D on draft/finalize | Child AC7 / parent AC9 tailor portion |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-997):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | 996/ftr merge precondition correct |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-994` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | No new `highlights` field |
| orch.pipeline.plan-is-bible | conforms | Stages binding; siblings excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Artifacts |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready re-check after discuss |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | Pin beside existing draft validate |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Reuses AST-996 schema objects |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | Pin/persist/debug in core |
| astral.layers.import-direction | conforms | utils/core/repo JSON |
| astral.layers.ui-config-driven-business-logic | conforms | No UI changes |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging |
| astral.standards.debug-contract-gated | conforms | Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | conforms | Shared schema/helpers; one pin |
| astral.standards.in-scope-only | conforms | Excludes craft-base/builder/UI |
| astral.standards.logging-via-utils | conforms | Style D helpers |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | Field keys from config |
| astral.standards.public-then-helpers | conforms | Public alias option for tracker |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | No state machine |
| astral.state.job-prior-states-enforced | conforms | Untouched |
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
- astral.patterns.require-auth-on-protected-endpoints — layers `ui` / paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. No new `highlights` field — parent wording = single accomplishments block.
2. Legacy string pass-through until re-craft — transitional.
3. Unmatched pin left for Grace — safer than wrong-base overwrite.
4. Self-assessment Single-Component / high / Medium — honest.
5. Build precondition merge AST-996 — correct dependency.

— Joan
context_tokens≈68000

#### ada — 2026-07-28T01:42:17.473Z
[plan-discuss] round=1 reply

**Delta:** Stage 2 `pin_experience_job_facts_from_base` no longer prefers same-index when lengths match. Match is **only** `(company.strip().lower(), title.strip().lower())`, consuming the first unused base job with that key (handles duplicate company+title stints in base order). **No index fallback** — unmatched/garbled identity jobs stay unpinned for Grace rather than a wrong-base metadata overwrite after reorder.

Plan tip: `d51ab862` — https://github.com/susansomerset/astral/blob/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape/docs/features/artifacts/ast-997-job-tailored-experience-on-job-array-shape.md

**Scope:** Single-Component — pin-match fix only.
**Conf:** high — Joan’s corruption case is removed by dropping index-first.
**Risk:** Medium — same coerce/persist destroyers; pin now safe under reorder.

#### joan — 2026-07-28T01:40:30.056Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-997
**Overall:** REVISE

**Notes:** Files Changed layer `repo admin JSON` mapped to `docs`. Tip `7ccfea69`. Blocked-by AST-996 Plan Approved acknowledged; build precondition to merge 996 contract is sound.
**Implementer:** Ada (parent Team table / plan author).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1–5 craft-base parse / session-base HTML | N/A — boundary: AST-996 / AST-998 |
| 6 Job-tailored hops same job-array shape; tailor accomplishments; pin factual metadata | Stages 1–4 (schema, validate/pin, persist, prompts) — **pin match order blocked** (see fix-now) |
| 7 Job-tailored HTML recognition | N/A — boundary: AST-998 |
| 8 Dates freeform | Inherited via AST-996 contract + pin preserves `dates` string |
| 9 `debug=True` Style D on touched parse/tailor hops | Stage 5 covers draft/finalize tailor hops; craft-base parse N/A — AST-996 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 6 accept/emit job-array; tailor accomplishments; leave company/title/dates/location from base | 1–4 |
| 7 Style D experience detail when `debug=True` on tailor hops | 5 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 finalize schema reuses shared job array | Functional scope job-tailored same shape; Contract alignment |
| 2 draft normalize/validate + pin base facts | AC6 metadata lock + accept job-array |
| 3 tracker persist keeps arrays | Contract alignment; emit/persist job-array |
| 4 four hop prompts tailor-accomplishments-only | AC6 policy in advise/draft/finalize/check |
| 5 Style D on draft/finalize | Child AC7 / parent AC9 tailor portion |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Plan-only `docs(AST-997):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Precondition merge of 996/ftr is correct direction |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-994` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | No `highlights` field — explicit decision matches child boundary |
| orch.pipeline.plan-is-bible | conforms | Stages binding; craft-base/HTML excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Artifacts |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada after this pass |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded confidence |
| astral.agent.do-task-delegation | conforms | Keeps do_task hops; pin hooked beside existing draft validate |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | No new batch APIs |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Reuses AST-996 schema objects; only `required` differs |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | Pin/persist/debug stay in core |
| astral.layers.import-direction | conforms | utils/core/repo JSON; tracker already imports candidate |
| astral.layers.ui-config-driven-business-logic | conforms | No UI changes |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging |
| astral.standards.debug-contract-gated | conforms | Tailor Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | conforms | Reuse schema/helpers; one pin for draft+finalize |
| astral.standards.in-scope-only | conforms | Explicitly excludes craft-base, builder, ArtifactEditor, contemplate |
| astral.standards.logging-via-utils | conforms | Style D helpers |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | Field keys from config items_schema |
| astral.standards.public-then-helpers | conforms | Public alias decision if tracker needs it |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | No state machine |
| astral.state.job-prior-states-enforced | conforms | Untouched |
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
- astral.patterns.require-auth-on-protected-endpoints — layers `ui` / paths `src/ui/**` miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

### fix-now
1. **Location:** Stage 2 step 3 — `pin_experience_job_facts_from_base` match order
   **Finding:** Plan prefers **same index when `len(tailored) == len(base)`**, else `(company, title)`. AC6 requires company/title/dates/location unchanged **from the base facts for that role**. If Judith reorders roles but keeps the same count (allowed by “reframe/reorder/emphasize accomplishments”), index-first pinning copies base[i] metadata onto tailored[i] accomplishments that belong to a different employer/title — silently corrupting role identity while looking like a successful pin.
   **Recommendation:** Match **primarily** on `(company.strip().lower(), title.strip().lower())`. Use index only as a last-resort fallback when no unique (company, title) match exists (e.g. model already garbled both). Document that behavior in Stage 2. Optionally: if index fallback fires, leave metadata unpinned and rely on Grace rather than wrong-base overwrite.

### discuss
(none blocking)

### acceptable
1. No new `highlights` field — parent “accomplishments/highlights” = single accomplishments block — matches child boundary.
2. Legacy string experience pass-through until re-craft — transitional given AST-996; happy path after 996 is job-array emit.
3. Build precondition merge of AST-996 before product commits — correct dependency handling.
4. Self-assessment Single-Component / high / Medium — honest about coerce/persist destroyers.
5. tracker already imports `candidate` — public alias decision is fine, not a layer violation.

— Joan
context_tokens≈62000

#### ada — 2026-07-28T01:35:00.456Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape/docs/features/artifacts/ast-997-job-tailored-experience-on-job-array-shape.md

**Scope:** Single-Component — finalize schema reuse of AST-996 job-array + draft validate/pin + tracker persist + four hop prompts + Style D tailor debug; craft-base and HTML stay with siblings.

**Conf:** high — Plan Approved AST-996 contract is the spine; known destroyers are draft list→string coerce and tracker str-only `_resume_payload_body`; pin-from-base enforces AC6 metadata lock.

**Risk:** Medium — a missed coerce/persist path would flatten or drop job-array experience from `job_data.artifacts.resume_content` before AST-998 can render.

---

# Job-tailored experience on job-array shape (Parse resume json output is incomplete)

**Linear:** [AST-997](https://linear.app/astralcareermatch/issue/AST-997/job-tailored-experience-on-job-array-shape-parse-resume-json-output-is)
**Parent:** [AST-994](https://linear.app/astralcareermatch/issue/AST-994/parse-resume-json-output-is-incomplete) — Parse resume json output is incomplete
**Publish ref:** `origin/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape`
**Blocked by:** [AST-996](https://linear.app/astralcareermatch/issue/AST-996/judith-craft-base-experience-job-array-parse-resume-json-output-is) — Plan Approved job-array contract (`_EXPERIENCE_JOB_*`, paste-faithful craft-base). Plan against that contract; do **not** re-own craft-base parse or HTML emit.

Job-tailored resume hops (`draft_job_resume` / `finalize_job_resume`, plus advise/check prompt guidance) accept and emit the same Experience job-array shape as AST-996. Tailoring may change **`accomplishments`** for the target job; **company, title, dates, location** stay the base facts. Does **not** invent a new `highlights` field, rewrite craft-base, or touch builders (AST-998).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Point `TASK_CONFIG["finalize_job_resume"]["response_schema"]["experience"]` at the shared job-array field (required False); do not duplicate item keys — reuse AST-996 `_EXPERIENCE_JOB_ITEM_SCHEMA` / array field | utils |
| `src/core/candidate.py` | Stop string-coercing experience job arrays in draft normalize/validate; accept/validate job-array `experience`; pin factual metadata from base; Style D job detail helper reusable by tailor hops | core |
| `src/core/tracker.py` | Persist path keeps experience job arrays (`_resume_payload_body`, match gates, `_prepare_job_resume_content` typing) | core |
| `src/core/agent.py` | On successful `draft_job_resume` / `finalize_job_resume` when `debug=True`, emit Style D detail for recorded experience jobs (reuse candidate helper) | core |
| `data/admin/agent_task.json` | Update `draft_job_resume`, `finalize_job_resume`, `advise_job_resume`, `check_job_resume` prompts for job-array shape + tailor-accomplishments-only / flag metadata rewrites | repo admin JSON |

**Out of scope (do not touch):** `craft_resume_base` schema/prompt (AST-996); `src/core/builder.py` / HTML emit (AST-998); ArtifactEditor Base Resume Content UI; `contemplate_job` prose hop; `prior_experience` stays `str`; `tests/`, bible.

**Build precondition:** Before Stage 1 product commits, merge `origin/sub/AST-994/AST-996-judith-craft-base-experience-job-array` (or rolled-up `origin/ftr/…` once Chuckles merges 996) so `_EXPERIENCE_JOB_*` and `_is_experience_job_array` / filter preserve helpers exist. If those symbols are missing after merge, **stop** and comment on the parent — do not re-implement craft-base contract here.

## Contract reference (AST-996 — do not redefine)

Each experience job object:

| Field | Type | Tailor policy |
|-------|------|---------------|
| `company` | str | **Pinned** to base facts |
| `title` | str | **Pinned** to base facts |
| `dates` | str (freeform) | **Pinned** to base facts |
| `location` | str (`""` if absent) | **Pinned** to base facts |
| `accomplishments` | str (one block) | **May tailor** for the target job |

⚠️ **Decision:** No new `highlights` field. Parent “accomplishments/highlights” means the single accomplishments text block on the shared job object. Inventing a second body field would violate child boundary “do not invent new experience fields beyond the shared job-array contract.”

## Stage 1: Config — finalize schema uses shared job array

**Done when:** `finalize_job_resume` response_schema `experience` is a `list` with the same `items_schema` as craft-base (required False); `draft_job_resume` stays `resume_section_payload: True` with no static experience:str; no craft-base schema edits.

1. In `src/utils/config.py`, after AST-996’s `_EXPERIENCE_JOB_ARRAY_FIELD` (required True) exists, add or inline for finalize:
   ```python
   _EXPERIENCE_JOB_ARRAY_FIELD_OPTIONAL: Dict[str, Any] = {
       "type": "list",
       "required": False,
       "items_schema": _EXPERIENCE_JOB_ITEM_SCHEMA,
   }
   ```
   ⚠️ **Decision:** Share `items_schema` object identity with craft-base; only `required` differs (finalize sections are optional).
2. Replace `TASK_CONFIG["finalize_job_resume"]["response_schema"]["experience"]` with `_EXPERIENCE_JOB_ARRAY_FIELD_OPTIONAL`.
3. Do **not** change `craft_resume_base`, `BUILD_CONFIG["artifact_shapes"]` (already job-array after AST-996), or other hop schemas that do not emit resume section bodies.

## Stage 2: Draft normalize/validate — accept job array; pin base facts

**Done when:** `normalize_draft_job_resume_agent_payload` no longer turns experience job arrays into prose strings; `validate_draft_job_resume_payload` accepts a non-empty job array (or empty/`""` skip); after successful draft validation, company/title/dates/location on each tailored job are restored from the matching base job when base experience is a job array.

1. In `src/core/candidate.py` `normalize_draft_job_resume_agent_payload`:
   - Before the loop that coerces `isinstance(val, (list, dict))` via `_coerce_resume_section_string`, skip when `key == "experience"` and `_is_experience_job_array(val)`.
   - Same skip when promoting nested content dict values for `experience`.
2. In `validate_draft_job_resume_payload`, for `key == "experience"`:
   - If `_is_experience_job_array(val)`: keep the list; optionally run a light per-item check that each item is a dict with string fields for the five keys (missing location → treat as `""` only if you normalize in place; do not invent other fields). Do **not** require `_coerce_resume_section_string`.
   - Elif `val` is a non-empty str: keep as legacy string (pre-996 base) — do not fail the hop solely for legacy shape.
   - Else if val is list/dict that is not a job array: return a clear error (`Section 'experience' must be a job array or prose string`).
3. Add `pin_experience_job_facts_from_base(payload: dict, candidate_data: dict) -> None` (mutates payload):
   - Read `base = (candidate_data.get("artifacts") or {}).get("base_resume")`; if `experience` on base is not a job array, return (nothing to pin).
   - If payload `experience` is not a job array, return.
   - **Match primarily on role identity**, never index-first:
     1. Build an ordered pool of unused base jobs (base array order).
     2. For each tailored job in tailored order, find the **first unused** base job whose `(company.strip().lower(), title.strip().lower())` equals the tailored job’s pair.
     3. On match: copy that base job’s `company`, `title`, `dates`, `location` onto the tailored job; leave tailored `accomplishments` unchanged; mark that base job used.
     4. If no `(company, title)` match: **do not pin** that tailored job (leave model metadata as returned). Do **not** fall back to same-index overwrite — equal lengths after reorder would attach the wrong role’s dates/location to another employer’s accomplishments.
   - Duplicate company+title stints: consume the next unused base match in base order (first unused with that key), so two Amazon/SPM tours still pin distinct base rows without index-aligning the whole array.
   ⚠️ **Decision (AC6 / Joan round=1):** Pin by `(company, title)` only. Index-first when `len` matches is forbidden — Judith may reorder roles while keeping count. Unmatched / garbled identity jobs stay unpinned for Grace (`check_job_resume`) rather than a wrong-base metadata overwrite.
4. Call `pin_experience_job_facts_from_base` on the inner payload at the end of successful `validate_draft_job_resume_payload` (after shape checks pass), so `do_task` returns the pinned payload downstream.
5. For `finalize_job_resume`: schema validation already runs in `do_task`. After schema success for `finalize_job_resume` only, call the same pin helper on the inner payload (from `agent.py` next to the draft validate block, or a tiny shared hook). Do **not** enable `resume_section_payload` on finalize unless required — prefer one explicit pin call for `task_key == "finalize_job_resume"`.

## Stage 3: Tracker persist — do not drop job arrays

**Done when:** `persist_job_artifact_from_parsed` / `save_job_artifact_resume_content` can store `experience` as a job array; match gates treat a non-empty job array as body content.

1. In `src/core/tracker.py`, change `_resume_payload_body` to return `Dict[str, Any]` and include:
   - string section values (as today), and
   - `experience` when `_is_experience_job_array(v)` (import/reuse `candidate_mod._is_experience_job_array` or a public alias `is_experience_job_array` if you prefer not to use a leading-underscore helper across modules — ⚠️ **Decision:** add public `is_experience_job_array = _is_experience_job_array` in `candidate.py` if tracker should not import a private name).
2. Update `parsed_matches_resume_content_shape` and `parsed_matches_job_resume_content`: a section counts as present when it is a non-empty str **or** (for `experience`) a non-empty job array.
3. Update `job_has_persisted_resume_body` the same way for stored `resume_content["experience"]`.
4. Widen `_prepare_job_resume_content` return type to `Dict[str, Any]`; rely on AST-996’s `filter_content_to_resume_structure` preserving job arrays. Contact snapshot logic stays string-only.
5. Do **not** change cover-letter persist paths.

## Stage 4: Prompts — tailor accomplishments only

**Done when:** Repo `agent_task.json` for the four hops below teaches the job-array wire shape and the tailor-vs-pin policy; bootstrap apply picks it up.

1. **`draft_job_resume` `user_prompt`:** After the existing “same JSON structure as the base resume” / “every claim must trace to base” rules, add an explicit Experience block:
   - `experience` is an ordered **array of job objects** with `company`, `title`, `dates`, `location`, `accomplishments`.
   - You may reframe/reorder/emphasize **`accomplishments`** text for the target role (still every claim must trace to the base resume — no invented metrics/employers).
   - **Do not** change `company`, `title`, `dates`, or `location` from the base resume for that role.
2. **`finalize_job_resume` `user_prompt`:** Same job-array output shape; when correcting Grace findings, restore factual metadata to base; accomplishments may stay tailored if Grace did not flag them as invented.
3. **`advise_job_resume` `user_prompt`:** In the resume-revision instruction list, tell Estelle to brief Judith on accomplishment emphasis/cuts/keyword weave **per role**, and to **forbid** rewriting company/title/dates/location.
4. **`check_job_resume` `user_prompt`:** Extend Grace’s checklist: flag any change to company/title/dates/location vs base; accomplishments may differ in wording/emphasis but must remain traceable (no new employers/metrics). Keep accuracy-only scope (no style critique).
5. Do **not** edit `craft_resume_base` prompts.

## Stage 5: Style D debug on tailor hops

**Done when:** With `debug=True`, successful `draft_job_resume` and `finalize_job_resume` emit Style D detail for each experience job (company/title/dates/location + truncated accomplishments), not only hop pass/fail.

1. Reuse AST-996’s `_debug_experience_jobs` (or extract to a shared name if draft path cannot see a session-only helper). If AST-996 landed the helper only beside session parse, move it to a module-level helper both tickets can call — still in `candidate.py`, no new module.
2. In `src/core/agent.py`, after successful validation for `draft_job_resume` and `finalize_job_resume` when `debug=True`, call that helper on the inner payload (under the existing hop `debug_index` from `_resume_hop_debug_index` — add detail lines, do not replace the hop header).
3. Gate all new lines on `debug=True` only (§1.5.1). Do not add tailor debug to advise/check/contemplate.

## Self-Assessment

**Scope:** `Single-Component` — finalize schema reuse + draft validate/pin + tracker persist + four hop prompts + debug detail; no craft-base ownership, no HTML builder.

**Conf:** `high` — AST-996 contract is Plan Approved; destroyers are known; pin match is now `(company, title)`-first with no index fallback (Joan round=1).

**Risk:** `Medium` — a missed coerce/persist path would flatten tailored experience back to prose or drop it from `job_data.artifacts.resume_content`, breaking the chain before AST-998 can render jobs.

## Code rules check

- §1.3 DRY: reuse AST-996 schema objects and `_is_experience_job_array` / debug helper; one pin function for draft + finalize.
- §2.1: no new hardcoded job field sets in core — config `items_schema` only.
- §2.4 / §2.6: no new batch claim or state machine.
- §3.3: core/utils/repo JSON only; no ui→data; no builder.
- §1.5.1: tailor debug Style D only when `debug=True`.
- §3.6: no repo-root `artifacts/` directory.

## Revisions

### Revision 1 — 2026-07-28
Driven by: Joan `[plan-discuss] round=1 concern` fix-now — Stage 2 pin match preferred same index when lengths equal, which corrupts role metadata after reorder.
Changes: `pin_experience_job_facts_from_base` now matches only on `(company, title)` (consume first unused base with that key); **no index-first / no index fallback**; unmatched jobs stay unpinned for Grace.

## Review (build stub)

**Publish ref:** `origin/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape`
**Plan path:** `docs/features/artifacts/ast-997-job-tailored-experience-on-job-array-shape.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–5 | (see tip) | finalize optional job-array schema, draft pin/validate, tracker persist, prompts, Style D tailor debug |

**Tip:** publish-ref tip after this stub append.

## Review (Radia — code-rubric.v1)

`[code-rubric] revision=1`

**Publish ref tip:** (see Linear / post-push SHA) on `origin/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape`
**Baseline:** `origin/dev`
**Overall:** DISCUSS

### What’s solid
- Finalize reuses shared `_EXPERIENCE_JOB_ITEM_SCHEMA` via optional array field; draft normalize/validate keeps job arrays; pin by `(company, title)` only (no index fallback).
- Tracker persist/`_resume_section_has_body` keep non-empty job arrays; four hop prompts teach tailor-accomplishments-only.
- Style D `_debug_experience_jobs` on draft/finalize when `debug=True`; Betty `test`/`merge-tests` on test-tree only.

### Issues
**discuss (C4 stragglers):** Joan excluded debug/docs/engineer-test-tree/UI auth+placement/naming statutes that the tip brings in-scope via AST-996 merge + features/tests — all scored **conforms** (no product defect).

**advisory:** `agent.py` imports private `_debug_experience_jobs` (tracker correctly uses public `is_experience_job_array`).

### Recommended actions
No fix-now. Stragglers are process notes — resolve-child may proceed without product edits unless Ada wants a public debug-helper alias.

## Resolution

**Date:** 2026-07-28  
**Review tip:** `7f2720d6` (Radia `docs(AST-997): Radia review — findings`)  
**Overall:** DISCUSS → resolved for User Testing (no fix-now)

### fix-now
(none)

### discuss
C4 stragglers (Joan exclusions vs tip in-scope via AST-996 merge + features/tests) — accepted as process notes; all already **conforms**. No product change.

### advisory
1. Public `debug_experience_jobs` alias added beside `_debug_experience_jobs`; `agent.py` tailor hops import the public name (mirrors `is_experience_job_array` for tracker).
