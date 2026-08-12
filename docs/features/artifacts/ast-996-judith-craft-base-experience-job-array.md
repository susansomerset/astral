<!-- linear-archive: AST-996 archived 2026-08-05 -->

## Linear archive (AST-996)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-996/judith-craft-base-experience-job-array-parse-resume-json-output-is  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-994 — Parse resume json output is incomplete  
**Blocked by / blocks / related:** parent: AST-994; blocks: AST-998; blocks: AST-997

### Description

## What this implements

Updates Judith’s craft-base prompt and response contract so Experience is an ordered array of jobs (company, title, dates, location, one accomplishments block) with no fabrication/rewrite of facts. Owns parse JSON shape for session and candidate craft-base paths. Does **not** own HTML emit or job-tailored highlight rewriting.

## Acceptance criteria

1. After craft-base parse of a multi-job resume paste, Experience is an ordered list of jobs; each job exposes company, title, dates, location, and one accomplishments text block observable in the parse JSON (session parse response and/or Base Resume Content equivalent).
2. Company, title, dates, and location for each job match source content for that role — no invented employers, titles, dates, or locations.
3. Accomplishments for craft-base match source content for that role (same facts and wording intent) — no added bullet claims that were not in the paste.
4. Dates remain freeform strings as supplied by the source (year-only and range forms both acceptable); the product does not require a rigid start/end date schema for this epic.
5. When `debug=True` on touched parse/tailor hops, debug output shows what was found/recorded for the experience jobs (Style D index + detail), not only a pass/fail summary.

## Boundaries

* Does **not** own HTML emit for base/session/job builders — sibling **Base + session + job builders: experience job render**.
* Does **not** own job-tailored highlight rewriting — sibling **Job-tailored experience on job-array shape**.
* Does **not** own AST-993 golden-fixture education/skills/header chrome or richer lead/bullet role layout.

## Notes for planning

* Experience job-array is a new structured contract for craft-base; keep schema/contract literals config-driven (Code Rules §2.1).
* Session parse path reuses craft-base — do not invent a second parse agent.
* Parent blocks AST-993 until this epic lands.

## Git branch (authoritative)

Per **orientation** § Branch law: parent **ftr/<parent-segment>**, child **sub/<parent-id>/<child-segment>**. Created at dispatch-parent. Publish to **origin/<sub-ref>** only — never Linear **gitBranchName** when it disagrees.

### Comments

#### chuckles — 2026-07-28T02:24:15.324Z
[merge-child] blocked: missing plan(AST-996): — publish log has `docs(AST-996): plan — …` only. Need a commit subject matching `^plan(AST-996):`.

@Ada Lovelace fixing publish-ref log; Chuckles will re-run merge-child after tip validates.

— Chuckles

#### radia — 2026-07-28T02:06:57.718Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-996
**Publish ref:** `8ed58ac4` on `origin/sub/AST-994/AST-996-judith-craft-base-experience-job-array` (baseline `origin/dev`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| --- | --- | --- | --- |
| astral.agent.confidence-bounds | scoped | conforms | core/utils touched; no graded confidence changes |
| astral.agent.do-task-delegation | scoped | conforms | still `do_task("craft_resume_base")`; no second parse agent |
| astral.agent.grade-vector-validation | scoped | conforms | no graded vectors |
| astral.batch.batch-id-first | scoped | conforms | session parse debug only; no new batch-id APIs |
| astral.batch.batch-id-format | scoped | conforms | batch id format untouched |
| astral.batch.claim-process-release | scoped | conforms | no new claim/process/release pattern |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | entity agent responses untouched |
| astral.config.config-source-of-truth | scoped | conforms | job-array contract in `config.py`; prompt in admin JSON |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | thresholds untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env literals added |
| astral.debug.no-repo-root-artifacts-dir | scoped | conforms | no repo-root `artifacts/` dump; features path only |
| astral.debug.spikes-under-debug-dir | scoped | conforms | plan under `docs/features/**`; no spike dumps |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single combined plan/review file for AST-996 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty `test`/`merge-tests` touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code()` has no tests/; Betty owns test tree |
| astral.layers.core-vs-external-bright-line | scoped | conforms | preserve/debug stay in core; no external LLM edits |
| astral.layers.import-direction | scoped | conforms | utils/core/ui only; no ui→data |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss (no `scripts/**`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | `experience_jobs` from DATA_SHAPES drives JSON round-trip |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check changes |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no consult/render-verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new endpoints |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer logging |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss (`src/data/**`) |
| astral.standards.debug-contract-gated | scoped | conforms | Style D index+detail only when `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | conforms | shared schema + `_is_experience_job_array` / `_debug_experience_jobs` |
| astral.standards.in-scope-only | scoped | conforms | no builder HTML / tailor hops (AST-997/998) |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` + `truncate_debug_content` from utils |
| astral.standards.no-cross-contamination | scoped | conforms | layer boundaries held |
| astral.standards.no-hardcoded-sets | scoped | conforms | wire shape from config literals |
| astral.standards.public-then-helpers | scoped | conforms | helpers near craft flatten / after parse path |
| astral.standards.utils-data-late-import-only | scoped | conforms | config-only utils edit; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | no state machine changes |
| astral.state.job-prior-states-enforced | scoped | conforms | no job prior-state changes |
| astral.state.no-daisy-chain-in-run | scoped | conforms | no dispatch daisy-chain |
| astral.ui.frontend-file-placement | scoped | conforms | edit stays in existing ArtifactEditor.tsx |
| astral.ui.naming-conventions | scoped | conforms | no new files/routes |
| astral.ui.single-gunicorn-worker | scoped | conforms | gunicorn/worker untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip includes one `merge-tests(AST-996)` SHA |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` only |
| orch.git.flow-direction-inviolable | universal | conforms | publish to child `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-994/AST-996-…` matches branch law |
| orch.git.merge-on-checkout | universal | conforms | no skip of ftr merge procedure |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rewrite ops on tip |
| orch.git.no-dev-agent-branches | universal | conforms | work on ticket sub ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-994` |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | AC3 paste-faithful accomplishments followed |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–5 implemented; siblings excluded |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible via Betty commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Chuckles not assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Ada through resolve; review leaves assignee untouched |
| orch.roles.pre-commit-path-bans | universal | conforms | role path bans respected on commit types |

## Pattern conformance

none cited

## Plan adherence

Stages 1–5 match the tip: shared job-array schema, preserve/split/filter, Judith paste-faithful experience prompt, ArtifactEditor JSON round-trip, Style D debug on session + candidate craft-base + `parse_candidate_resume(debug=)`. Self-Assessment Scope Single-Component still fits. Boundaries vs AST-997/998 held. Joan plan-rubric attachment present (APPROVED).

## Findings

### fix-now
(none)

### discuss
1. **C4 straggler** — Joan excluded `astral.debug.no-repo-root-artifacts-dir`; tip scores in-scope via `artifacts/**` path match under `docs/features/artifacts/` — **conforms** (no repo-root dump dir).
2. **C4 straggler** — Joan excluded `astral.debug.spikes-under-debug-dir`; tip has `docs/features/**` — **conforms**.
3. **C4 straggler** — Joan excluded `astral.docs.features-single-file-per-ticket` (plan Files Changed omitted features path); tip adds the combined plan — **conforms**.
4. **C4 straggler** — Joan excluded `astral.git.engineer-test-tree-ban`; tip includes Betty `test`/`merge-tests` — **conforms** (engineer `code()` did not touch tests/).

### advisory
1. `craft_resume_base` `user_prompt` still says LinkedIn/backstory “add context and color” without the experience carve-out present in `cache_prompt`.
2. Quality checklist still says every key is a non-empty **string** while `experience` is now a job array (schema insertion should dominate).
3. Public `is_experience_job_array` alias + ArtifactEditor `key === "experience"` Save fallback go slightly beyond Stage 2/4 plan text (harmless for siblings / structureMode).

## What’s solid

Config single-source job array; no `str(list)` destroyers; AC3 prompt lock; debug Style D gated; UI round-trip with toast on bad JSON.

## Notes

Plan-rubric verdict attached (Joan APPROVED). Stragglers are process notes only — no product fix-now.

context_tokens≈45000

#### betty — 2026-07-28T01:57:31.943Z
## QA test manifest — AST-996

**Publish:** `origin/sub/AST-994/AST-996-judith-craft-base-experience-job-array` @ `e8e843ae` (`merge-tests(AST-996): origin/tests 2d15bac7`)

### Classification
1. **Existing coverage (revised):** `TestAst517ResumeStructure` schema fixtures; `TestAst519ResumeStructureUiHelpers::test_filter_base_resume_to_structure_drops_orphans_and_accent`; `TestAst986SessionResumeParse::test_200_success_debug_style_d`
2. **Broken / obsolete (fixed this pass):** string-`experience` schema asserts; filter `str(99)` coercion; session debug `debug_detail_block` (now job-focused `debug_detail`)
3. **Gaps (new):** `TestAst996ExperienceJobArray`, `TestAst996ExperienceJobArrayConfig`, ArtifactEditor `AST-996:*` JSON round-trip / invalid toast

### Manifest (test-child)

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestAst996ExperienceJobArray tests/component/core/test_candidate.py::TestAst517ResumeStructure tests/component/core/test_candidate.py::TestAst519ResumeStructureUiHelpers tests/component/core/test_candidate.py::TestAst986SessionResumeParse tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration tests/component/utils/test_config.py::TestAst996ExperienceJobArrayConfig -q`
2. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx --testNamePattern="AST-996"`

**Pass criterion:** pytest + Vitest green on the lines above — not zero-arg harness / branch-lock gate.

### Bible shasums (on publish tip)
- `bf2cadd089f40c8cff53de1e228d05a3e28e7b44587b48bee745dda20d18a907` `docs/test-bible/core/candidate.md`
- `a15f31a3ac31c6478873e22755786b85ddd8ac803c8dc0fee69babbc8e0d1a18` `docs/test-bible/utils/config.md`
- `b8a0abd5e9f898b3bccb3b3945137ea913c2e2cdbe1dd5f71d73b997ad3acb17` `docs/test-bible/frontend/components.md`

— Betty

#### joan — 2026-07-28T01:32:26.933Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-996
**Overall:** APPROVED

**Notes:** Plan Discuss round=1 completed (concern + reply). Files Changed layer `repo admin JSON` mapped to `docs`. Tip `4a62a3ae`. Prior fix-now (Stage 3 LinkedIn/backstory enrichment vs AC3) addressed in Revision 1.
**Implementer:** Ada (parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Experience ordered job list + five fields in parse JSON | Stages 1–4 |
| 2 company/title/dates/location match source; no invention | Stages 1, 3 |
| 3 accomplishments match source; no added claims not in the paste | Stage 3 (paste/resume-faithful; Revision 1) |
| 4 Session HTML role subheaders | N/A — boundary: AST-998 |
| 5 Candidate base-resume HTML parity | N/A — boundary: AST-998 |
| 6 Job-tailored hop same shape / tailor highlights only | N/A — boundary: AST-997 |
| 7 Job-tailored HTML recognition | N/A — boundary: AST-998 |
| 8 Dates freeform strings | Stages 1, 3 |
| 9 `debug=True` Style D for experience on touched parse/tailor hops | Stage 5 covers craft-base/session parse; tailor hops N/A — AST-997 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 job array observable in session parse / Base Resume Content | 1–4 |
| 2 factual metadata fidelity | 1, 3 |
| 3 accomplishments = paste/source; no added bullets | 3 |
| 4 freeform dates | 1, 3 |
| 5 Style D experience job detail when `debug=True` | 5 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Config job-array contract | Purpose / Functional scope craft-base shape; AC1, AC8; child AC1/4 |
| 2 Preserve through split/filter | Contract alignment; AC1 observability |
| 3 Judith prompt | Functional scope + AC2/3/8; child AC2/3/4 |
| 4 ArtifactEditor JSON round-trip | AC1 Base Resume Content observability; Boundaries (do not break Base Resume Content editing) |
| 5 Style D debug | Parent/child AC5/9 parse portion |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | Plan does not touch Betty merge-tests delivery |
| orch.git.commit-vocabulary | conforms | Plan publishes with `docs(AST-996):`; no banned types |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` publish only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table sub ref |
| orch.git.merge-on-checkout | conforms | No procedure that skips ftr merge |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops proposed |
| orch.git.no-dev-agent-branches | conforms | Work on ticket sub |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree `astral-AST-994` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | AC3 followed; no invented LinkedIn carve-out |
| orch.pipeline.plan-is-bible | conforms | Stages binding; sibling scope excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Artifacts |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready re-check after discuss reply |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned path commits planned |
| astral.agent.confidence-bounds | conforms | No graded confidence changes |
| astral.agent.do-task-delegation | conforms | Keeps `do_task("craft_resume_base")` |
| astral.agent.grade-vector-validation | conforms | No graded vectors |
| astral.batch.batch-id-first | conforms | No new batch APIs |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | No new batch pattern |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Shared `_EXPERIENCE_JOB_*` in config.py |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env literals |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src + features |
| astral.layers.core-vs-external-bright-line | conforms | Preserve/debug in core |
| astral.layers.import-direction | conforms | utils / core / ui; no ui→data |
| astral.layers.ui-config-driven-business-logic | conforms | `experience_jobs` from DATA_SHAPES |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check changes |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new endpoints |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging |
| astral.standards.debug-contract-gated | conforms | Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | conforms | Shared schema + preserve helper |
| astral.standards.in-scope-only | conforms | Excludes AST-997/998/993 |
| astral.standards.logging-via-utils | conforms | Existing Style D helpers |
| astral.standards.no-cross-contamination | conforms | Layered structure only |
| astral.standards.no-hardcoded-sets | conforms | Contract in config |
| astral.standards.public-then-helpers | conforms | Helpers near craft flatten helpers |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | No state machine |
| astral.state.job-prior-states-enforced | conforms | No job transitions |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch chaining |
| astral.ui.frontend-file-placement | conforms | Existing flat ArtifactEditor.tsx |
| astral.ui.naming-conventions | conforms | No new files/routes |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths `artifacts/**`, `scripts/spikes/**` miss plan paths
- astral.debug.spikes-under-debug-dir — paths `debug/**`, `docs/features/**`, `scripts/spikes/**` miss plan paths
- astral.docs.features-single-file-per-ticket — paths `docs/features/**` miss Files Changed table
- astral.git.engineer-test-tree-ban — paths `tests/**` / bible miss
- astral.layers.scripts-exempt-from-layer-rules — layers `scripts` / paths `scripts/**` miss
- astral.standards.database-header-inventory — layers `data` / paths `src/data/**` miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. Interim HTML may JSON-dump structured experience until AST-998 — in bounds.
2. Legacy string `experience` readable until re-parse; no migration — reasonable.
3. Self-assessment Scope Single-Component / Conf high / Risk Medium — honest.
4. Stage 3 leaves non-experience multi-source synthesis (e.g. professional_summary) alone while locking experience jobs to paste/resume — matches AC3 scope.

— Joan
context_tokens≈58000

#### ada — 2026-07-28T01:30:19.323Z
[plan-discuss] round=1 reply

**Delta:** Stage 3 now locks craft-base `accomplishments` to paste/resume-source only — organize/copy facts and wording intent; no LinkedIn/backstory/strengths enrichment or narrative “improvement” (matches child/parent AC3). Added an explicit scan to neutralize other `craft_resume_base` prompt lines that still teach experience blend, without touching non-experience synthesis (e.g. `professional_summary`). Files Changed / Done when / Conf + Revisions §1 updated.

Plan tip: `4a62a3ae` — https://github.com/susansomerset/astral/blob/sub/AST-994/AST-996-judith-craft-base-experience-job-array/docs/features/artifacts/ast-996-judith-craft-base-experience-job-array.md

**Scope:** Single-Component — unchanged surface; AC3 fidelity fix only in Stage 3.
**Conf:** high — Joan’s fix-now was a single contradictory bullet; AC already decided paste-faithful.
**Risk:** Medium — same stringify/filter destroyers as before; prompt now aligned with AC3.

#### joan — 2026-07-28T01:27:41.062Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-996
**Overall:** REVISE

**Notes:** Files Changed layer `repo admin JSON` mapped to `docs` (unrecognized → docs per matching algorithm).
**Implementer:** Ada (parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Experience ordered job list + five fields in parse JSON | Stages 1–4 |
| 2 company/title/dates/location match source; no invention | Stage 3 (prompt) + Stage 1 contract |
| 3 accomplishments match source; no added claims not in the paste | Stage 3 — **blocked** (see fix-now) |
| 4 Session HTML role subheaders | N/A — boundary: AST-998 |
| 5 Candidate base-resume HTML parity | N/A — boundary: AST-998 |
| 6 Job-tailored hop same shape / tailor highlights only | N/A — boundary: AST-997 |
| 7 Job-tailored HTML recognition | N/A — boundary: AST-998 |
| 8 Dates freeform strings | Stages 1, 3 |
| 9 `debug=True` Style D for experience on touched parse/tailor hops | Stage 5 covers craft-base/session parse; tailor hops N/A — AST-997 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 job array observable in session parse / Base Resume Content | 1–4 |
| 2 factual metadata fidelity | 1, 3 |
| 3 accomplishments = paste/source; no added bullets | 3 (must align — fix-now) |
| 4 freeform dates | 1, 3 |
| 5 Style D experience job detail when `debug=True` | 5 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Config job-array contract | Purpose / Functional scope craft-base shape; AC1, AC8; child AC1/4 |
| 2 Preserve through split/filter | Contract alignment; AC1 observability |
| 3 Judith prompt | Functional scope + AC2/3/8; child AC2/3/4 |
| 4 ArtifactEditor JSON round-trip | AC1 Base Resume Content observability; Boundaries (do not break Base Resume Content editing) |
| 5 Style D debug | Parent/child AC5/9 parse portion |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | Plan does not touch Betty merge-tests delivery |
| orch.git.commit-vocabulary | conforms | Plan-only publish already used `docs(AST-996):`; no banned commit types proposed |
| orch.git.flow-direction-inviolable | conforms | Publish ref is child `sub/*`; no tests↔dev contamination |
| orch.git.ftr-sub-topology | conforms | Publish ref matches parent Git table `sub/AST-994/AST-996-…` |
| orch.git.merge-on-checkout | conforms | No checkout procedure that skips ftr merge |
| orch.git.no-cherry-pick-rebase-force | conforms | Plan does not propose cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Work stays on ticket sub |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree `astral-AST-994` only |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | AC3 already decides paste-faithful accomplishments; plan must follow AC, not invent a LinkedIn carve-out |
| orch.pipeline.plan-is-bible | conforms | Once revised/approved, stages are binding; no improvised sibling scope |
| orch.pipeline.project-scoped-queues | conforms | Single-child validate; Astral Artifacts |
| orch.pipeline.status-gates-skill-entry | conforms | Validated at Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly out of scope: tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | Child implementer is Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign to Ada after this pass |
| orch.roles.pre-commit-path-bans | conforms | No engineer test-tree or Betty src/features commits planned |
| astral.agent.confidence-bounds | conforms | No graded confidence changes |
| astral.agent.do-task-delegation | conforms | Keeps `do_task("craft_resume_base")`; no second agent |
| astral.agent.grade-vector-validation | conforms | No graded vectors touched |
| astral.batch.batch-id-first | conforms | No new batch claim APIs |
| astral.batch.batch-id-format | conforms | No batch_id format changes |
| astral.batch.claim-process-release | conforms | No new batch claim/process/release |
| astral.batch.entity-agent-responses-latest-only | conforms | No entity latest-ref storage changes |
| astral.config.config-source-of-truth | conforms | Shared `_EXPERIENCE_JOB_*` in `config.py`; prompt text stays in `agent_task.json` |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env literals |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src + features plan |
| astral.layers.core-vs-external-bright-line | conforms | Preserve/debug stay in core; no external I/O move |
| astral.layers.import-direction | conforms | utils / core / ui layers; no ui→data |
| astral.layers.ui-config-driven-business-logic | conforms | `experience_jobs` type from DATA_SHAPES drives ArtifactEditor JSON round-trip |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check changes |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new endpoints |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging |
| astral.standards.debug-contract-gated | conforms | Stage 5 Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | conforms | One shared schema object + one preserve helper |
| astral.standards.in-scope-only | conforms | Explicitly excludes AST-997/998/993 and builder |
| astral.standards.logging-via-utils | conforms | Uses existing Style D logger helpers |
| astral.standards.no-cross-contamination | conforms | Stays in layered structure |
| astral.standards.no-hardcoded-sets | conforms | Job field contract in config, not inline sets in core/ui |
| astral.standards.public-then-helpers | conforms | Helpers proposed near existing craft flatten helpers |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | No state machine |
| astral.state.job-prior-states-enforced | conforms | No job transitions |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch run chaining |
| astral.ui.frontend-file-placement | conforms | Edit existing flat `components/ArtifactEditor.tsx` |
| astral.ui.naming-conventions | conforms | No new files/routes |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths `artifacts/**`, `scripts/spikes/**` miss plan paths
- astral.debug.spikes-under-debug-dir — paths `debug/**`, `docs/features/**`, `scripts/spikes/**` miss plan paths
- astral.docs.features-single-file-per-ticket — paths `docs/features/**` miss Files Changed table
- astral.git.engineer-test-tree-ban — paths `tests/**` / bible miss
- astral.layers.scripts-exempt-from-layer-rules — layers `scripts` / paths `scripts/**` miss
- astral.standards.database-header-inventory — layers `data` / paths `src/data/**` miss

## Findings

### fix-now
1. **Location:** Stage 3 step 1 (LinkedIn/backstory enrichment bullet) vs child AC3 / parent AC3 / Purpose
   **Finding:** Plan requires accomplishments as one block “as in the source” / “not rewritten or expanded with invented claims,” then also allows “LinkedIn/backstory may enrich narrative inside `accomplishments` … (same rules as today’s synthesis guidance).” Child AC3: accomplishments match source for that role with **no added bullet claims that were not in the paste**. Parent Purpose/Functional scope: extract/organize what is present; accomplishments from what the source says; no inventing accomplishments. Preserving today’s LinkedIn/backstory/strengths blend re-authorizes claims outside the paste and contradicts the locked AC.
   **Recommendation:** Rewrite Stage 3 so craft-base `### experience` instructs paste/resume-source-only accomplishments (organize/copy facts and wording intent; no LinkedIn/backstory/strengths enrichment, no narrative “improvement”). Scan other `craft_resume_base` prompt lines that still teach LinkedIn blend for experience and neutralize only those that conflict. If product still wants LinkedIn blend, stop and `@susan` — do not keep both in the plan.

### discuss
(none blocking)

### acceptable
1. Interim HTML may JSON-dump structured experience until AST-998 — called out; in bounds.
2. Legacy string `experience` readable until re-parse; no migration — reasonable.
3. Self-assessment Scope Single-Component / Conf high / Risk Medium — honest for the known stringify destroyers.

— Joan
context_tokens≈52000

#### ada — 2026-07-28T01:24:03.247Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-994/AST-996-judith-craft-base-experience-job-array/docs/features/artifacts/ast-996-judith-craft-base-experience-job-array.md

**Scope:** Single-Component — config job-array contract + craft-base preserve/split + Judith `agent_task` prompt + thin ArtifactEditor JSON round-trip; builder HTML and job-tailored hops stay with siblings.

**Conf:** high — nested `list`/`items_schema` validation already exists; known destroyers are `str(list)` in filter/split and the prose experience prompt segment.

**Risk:** Medium — a missed flatten/filter path would drop or stringify jobs on session parse / Base Resume Content Save; interim HTML still JSON-dumps structured experience until AST-998.

---

# Judith craft-base: experience job array (Parse resume json output is incomplete)

**Linear:** [AST-996](https://linear.app/astralcareermatch/issue/AST-996/judith-craft-base-experience-job-array-parse-resume-json-output-is)
**Parent:** [AST-994](https://linear.app/astralcareermatch/issue/AST-994/parse-resume-json-output-is-incomplete) — Parse resume json output is incomplete
**Publish ref:** `origin/sub/AST-994/AST-996-judith-craft-base-experience-job-array`

Updates Judith’s `craft_resume_base` response contract and prompt so **Experience** is an ordered array of jobs (company, title, dates, location, one accomplishments block) with no fabrication or rewrite of facts. Owns the parse JSON shape on session parse and candidate craft-base paths. Does **not** own HTML emit (AST-998) or job-tailored highlight rewriting (AST-997).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add shared experience-job item schema; set `TASK_CONFIG["craft_resume_base"]["response_schema"]["experience"]` and `BUILD_CONFIG["artifact_shapes"]["resume_content"]["experience"]` to list-of-jobs; mark `DATA_SHAPES` base_resume_structure `experience` as structured list | utils |
| `src/core/candidate.py` | Preserve experience job arrays through flatten / split / filter / token helpers; Style D debug detail for recorded jobs on session + candidate craft-base success paths | core |
| `data/admin/agent_task.json` | Rewrite `craft_resume_base` `cache_prompt` **### experience** for job-array contract; accomplishments paste/resume-source-only (no LinkedIn/backstory/strengths enrichment) | repo admin JSON |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Round-trip non-string section values as JSON text for load / Generate / Save so Base Resume Content does not stringify-corrupt the job array | ui |

**Out of scope (do not touch):** `src/core/builder.py` / HTML emit (AST-998); `draft_job_resume` / `finalize_job_resume` / job-tailored hops (AST-997); `prior_experience` remains `str`; AST-993 chrome; `tests/`, bible.

## Stage 1: Config — experience job-array contract

**Done when:** `TASK_CONFIG["craft_resume_base"]["response_schema"]["experience"]` is a required `list` with `items_schema` for company/title/dates/location/accomplishments; `stringify_response_schema("craft_resume_base")` shows that array shape; `BUILD_CONFIG["artifact_shapes"]["resume_content"]["experience"]` matches; no other task schemas changed.

1. In `src/utils/config.py`, near the other shared schema helpers (`_CRAFT_RUBRIC_*`), add:
   ```python
   _EXPERIENCE_JOB_ITEM_SCHEMA: Dict[str, Dict[str, Any]] = {
       "company": {"type": "str", "required": True},
       "title": {"type": "str", "required": True},
       "dates": {"type": "str", "required": True},
       "location": {"type": "str", "required": True},
       "accomplishments": {"type": "str", "required": True},
   }
   _EXPERIENCE_JOB_ARRAY_FIELD: Dict[str, Any] = {
       "type": "list",
       "required": True,
       "items_schema": _EXPERIENCE_JOB_ITEM_SCHEMA,
   }
   ```
   ⚠️ **Decision:** `location` is required as `str`; when the source has no location for a role, Judith returns `""`. Dates stay a single freeform string (e.g. `2023`, `Jan 2023 to Dec 2023`) — no start/end split. Field name `accomplishments` (not `highlights`) for craft-base; AST-997 may introduce tailored highlights later on the same job-object spine.
2. In `TASK_CONFIG["craft_resume_base"]["response_schema"]`, replace `"experience": {"type": "str", "required": True}` with `"experience": _EXPERIENCE_JOB_ARRAY_FIELD` (same object reference, not a duplicated literal).
3. In `BUILD_CONFIG["artifact_shapes"]["resume_content"]`, set `"experience": _EXPERIENCE_JOB_ARRAY_FIELD` the same way (single source for the wire shape).
4. In `DATA_SHAPES["candidates"]["detail"]["base_resume_structure"]`, change the experience entry from `"type": "str"` to `"type": "experience_jobs"` (label stays `"Experience"`). ArtifactEditor Stage 4 keys off this type for JSON round-trip.
5. Do **not** change `prior_experience`, `finalize_job_resume`, `draft_job_resume`, or `BUILD_CONFIG["supported_sections"]["experience"]["body_kind"]` (HTML sibling owns render recognition).
6. Confirm `_schema_to_example` / `stringify_response_schema` already recurse `items_schema` for lists (they do) — no validator changes required for the new shape; `_coerce_schema_str_fields_from_list` only coerces fields with `type == "str"`, so once experience is `list` it will not be flattened to a newline string.

## Stage 2: Preserve job arrays through craft-base split/filter paths

**Done when:** `split_craft_resume_base_payload` puts a job list on `content["experience"]`; `filter_base_resume_to_structure` / `filter_content_to_resume_structure` / `format_base_resume_for_token` keep that list (no `str(list)`); `_flatten_craft_resume_section_strings` does not coerce a list-of-job-dicts into a prose string.

1. In `src/core/candidate.py`, add a small helper (near the craft flatten helpers):
   ```python
   def _is_experience_job_array(val: Any) -> bool:
       return isinstance(val, list) and all(isinstance(item, dict) for item in val)
   ```
2. Update `_coerce_resume_section_string`: if `_is_experience_job_array(val)`, return `None` (do not join dicts into prose). List-of-strings coercion for other sections stays as today.
3. Update `_flatten_craft_resume_section_strings` `_promote`: if `sid == "experience"` and `_is_experience_job_array(val)` and experience is not already a job array on the payload, set `payload["experience"] = val` and return (do not require string coerce). If top-level `experience` is already a job array, leave it.
4. Update `split_craft_resume_base_payload`:
   - Change `content` typing to `Dict[str, Any]`.
   - For each enabled key in `parsed`: if `key == "experience"` and `_is_experience_job_array(val)`, set `content[key] = val`; elif `isinstance(val, str)`, set `content[key] = val` (existing). Do not drop experience when it is a list.
   ⚠️ **Decision:** Legacy stored string `experience` remains readable as a string until re-parse; this ticket does not migrate old blobs. New craft-base success always emits the job array.
5. Update `filter_base_resume_to_structure`: replace `{k: str(v) for ...}` with: keep job arrays as-is for `experience`; for other keys keep `str(v)` only when value is not a `dict`/`list`, else `json.dumps(v)` is **not** used here — non-experience structured values are out of scope; only experience list + string scalars are expected.
   ```python
   out = {}
   for k, v in content.items():
       if k not in section_ids:
           continue
       if k == "experience" and _is_experience_job_array(v):
           out[k] = v
       elif isinstance(v, str):
           out[k] = v
       # else: drop unexpected shapes (do not str()-corrupt)
   return out
   ```
6. Update `filter_content_to_resume_structure`: when `key == "experience"` and `_is_experience_job_array(val)` and the list is non-empty, copy the list into `out`; keep existing non-empty string handling for other keys. Widen `out` type to `Dict[str, Any]`.
7. `format_base_resume_for_token` already `json.dumps`s the filtered payload — once filter preserves the list, the token JSON carries the job array. No further change unless the filter call path regresses.
8. Do **not** edit `normalize_draft_job_resume_agent_payload` / `validate_draft_job_resume_payload` (AST-997).

## Stage 3: Judith prompt — experience as job array

**Done when:** `data/admin/agent_task.json` row `craft_resume_base` `cache_prompt` **### experience** instructs an ordered JSON array of job objects with the five fields above; accomplishments are paste/resume-source-only (organize/copy facts and wording intent — no LinkedIn/backstory/strengths enrichment, no narrative “improvement”); freeform dates; `{$RESPONSE_SCHEMA}` remains the schema insertion point (no hardcoded duplicate schema block).

1. In `data/admin/agent_task.json`, find the `craft_resume_base` row. Replace the **### experience** segment (currently prose “COMPANY NAME / Title | dates | Location” blocks separated by blank lines) with instructions that:
   - `experience` is an **ordered JSON array** of job objects (resume order).
   - Each object has exactly: `company`, `title`, `dates`, `location`, `accomplishments` (all strings).
   - `dates` is freeform as in the paste/resume source (year-only or ranges OK).
   - `location` is the paste/resume location string, or `""` if absent.
   - `accomplishments` is **one** text block for that role taken from what the paste/resume says for that role (paragraph and/or bullets) — same facts and wording intent; organize into the field, do not rewrite.
   - Paste/resume text is the **only** source for company, title, dates, location, and accomplishments for this section. Do **not** invent employers, titles, dates, locations, or accomplishments. Do **not** paraphrase factual metadata to “improve” it. Do **not** add bullet claims that were not in the paste.
   ⚠️ **Decision (AC3 / Joan round=1):** Craft-base `accomplishments` are **paste/resume-faithful only**. Do **not** allow LinkedIn, backstory, or strengths to enrich, blend, or expand `accomplishments` (that re-authorizes claims outside the paste and contradicts child/parent AC3). Other sections (e.g. `professional_summary`) may keep existing multi-source synthesis; this lock applies to **experience jobs** only.
2. Scan the rest of the `craft_resume_base` `cache_prompt` (and `user_prompt` if needed) for lines that still teach LinkedIn/backstory/strengths blend **for experience / roles / accomplishments** (e.g. input-source bullets that say LinkedIn “Enriches … experience sections,” or synthesis rules that map strengths into roles). Neutralize **only** those experience-conflicting lines so they do not override Stage 3 step 1 — leave `professional_summary` / non-experience synthesis language alone unless it explicitly tells Judith to put LinkedIn/backstory claims into experience.
3. Leave other segment instructions (`candidate_name`, `professional_summary`, `prior_experience`, etc.) unchanged except for the experience-conflict fixes in step 2, and any sentence that still says experience is a single prose string (fix those to the job-array shape).
4. Do **not** invent a second parse agent or session-only prompt; session parse continues to call `do_task("craft_resume_base")`.
5. Repo JSON applies at bootstrap (`apply_repo_admin_json_at_startup`); no Manage Tasks UI change in this ticket. If local DB has diverged, note in the Linear stage comment that Railway/startup apply picks up the file — do not hand-edit production DB in this plan.

## Stage 4: Base Resume Content JSON round-trip (no corrupt Save)

**Done when:** ArtifactEditor load / Generate / Save for `craft_resume_base` fixed fields shows experience as pretty-printed JSON and saves it back as a parsed array (not `"[object Object]"` / stringified garbage).

1. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, add helpers:
   ```ts
   function sectionValueToTabContent(val: unknown): string {
     if (typeof val === "string") return val
     if (val == null) return ""
     return JSON.stringify(val, null, 2)
   }
   function tabContentToSectionValue(key: string, content: string, fieldType?: string): unknown {
     if (fieldType === "experience_jobs") {
       const t = content.trim()
       if (!t) return []
       return JSON.parse(t)  // let Save catch path surface parse errors via toast
     }
     return content
   }
   ```
2. Wire `sectionValueToTabContent` into `mapFixedFieldsFromRaw` and the Generate success `fixedFields.map` path (replace `String(...)`).
3. Wire `tabContentToSectionValue` into `buildPayload` for fixed-fields mode: look up each field’s `type` from `fixedFields` / shapes (experience → `experience_jobs`). Widen payload typing from `Record<string, string>` to `Record<string, unknown>`.
4. On Save, if `JSON.parse` throws for experience, show a toast (`Experience must be valid JSON`) and abort the request — do not PUT a broken string.
5. Do **not** redesign the tab into a structured job editor; JSON textarea is sufficient for observability and non-destructive Save.

## Stage 5: Style D debug for experience jobs on craft-base parse hops

**Done when:** With `debug=True`, successful `run_session_resume_parse` and successful `craft_resume_base` path inside `run_candidate_artifact_generation` (and `parse_candidate_resume` when debug is threaded) emit Style D detail lines listing each recorded job’s company/title/dates/location plus truncated accomplishments — not only pass/fail.

1. In `src/core/candidate.py`, add helper `_debug_experience_jobs(logger, content_or_parsed)` that:
   - Reads `experience` from a dict (prefer split `content`, else `parsed`).
   - If job array: for each index `i`, `logger.debug_detail(f"experience[{i}] company=... title=... dates=... location=...")` and one detail line for accomplishments via `truncate_debug_content` when long.
   - If missing/legacy string: one detail line noting shape (`experience_shape=str|missing|other`).
2. Call it after successful split in `run_session_resume_parse` (under the existing `debug_index` success header; keep or trim the full `debug_detail_block(json.dumps(parsed))` — prefer job-focused detail + optional truncated payload, do not remove the index header).
3. Call it on successful `craft_resume_base` persist in `run_candidate_artifact_generation` when `debug=True` (same Style D helpers; gate on `debug` only — §1.5.1).
4. Thread `debug: bool = False` onto `parse_candidate_resume` if it lacks it; when `debug=True`, same job detail after split. Callers that omit `debug` stay quiet.
5. Do **not** add tailor-hop debug here (AST-997).

## Self-Assessment

**Scope:** `Single-Component` — config contract + craft-base preserve/split path + Judith prompt row + thin ArtifactEditor JSON round-trip; no builder HTML and no job-tailored hops.

**Conf:** `high` — schema already supports nested `list`/`items_schema`; known destroyers (`str(list)` in filter/split) are called out; AC3 paste-faithful accomplishments are now explicit in Stage 3 (Joan round=1).

**Risk:** `Medium` — wrong flatten/filter would drop or stringify jobs and break session parse observability and Base Resume Content Save; HTML still uses `_format_experience_value` JSON dump until AST-998, so interim print is ugly but not empty.

## Code rules check

- §1.3 DRY: one `_EXPERIENCE_JOB_*` config object shared by TASK_CONFIG and artifact_shapes; one preserve helper used by split/filter.
- §2.1: schema/contract literals only in `config.py`; prompt text in repo `agent_task.json` (existing pattern).
- §2.4: no new batch claim pattern; session ledger unchanged.
- §2.6: no state machine changes.
- §3.3: ui → core only; core edits stay in candidate; no ui→data.
- §1.5.1: debug Style D only when `debug=True`.
- §3.6: no repo-root `artifacts/` directory.

## Revisions

### Revision 1 — 2026-07-28
Driven by: Joan `[plan-discuss] round=1 concern` fix-now — Stage 3 LinkedIn/backstory enrichment bullet vs child/parent AC3 (accomplishments must match paste/source; no added claims not in the paste).
Changes: Stage 3 rewritten so craft-base `accomplishments` are paste/resume-faithful only (no LinkedIn/backstory/strengths enrichment); added scan of other `craft_resume_base` prompt lines that teach experience blend and neutralize only those conflicts; Files Changed / Done when / Conf updated to match.

## Review (build stub)

**Publish ref:** `origin/sub/AST-994/AST-996-judith-craft-base-experience-job-array`
**Plan path:** `docs/features/artifacts/ast-996-judith-craft-base-experience-job-array.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–5 | `30b4320f` | experience job-array schema, preserve/split/filter, Judith prompt, ArtifactEditor JSON round-trip, Style D debug |

**Tip:** `30b4320f` on publish-ref (this stub append may tip further).

## Review (Radia — code-rubric.v1)

`[code-rubric] revision=1`

**Publish ref tip:** `e8e843ae` (`origin/sub/AST-994/AST-996-judith-craft-base-experience-job-array`)
**Baseline:** `origin/dev`
**Overall:** DISCUSS

### What’s solid
- Shared `_EXPERIENCE_JOB_*` in `config.py` wired into TASK_CONFIG + BUILD_CONFIG + `DATA_SHAPES` `experience_jobs`.
- Preserve/split/filter paths keep job arrays (no `str(list)` corruption); Style D job detail gated on `debug=True`.
- Judith `### experience` is paste/resume-faithful; LinkedIn experience-enrichment neutralized in cache_prompt.
- ArtifactEditor JSON round-trip + invalid-JSON toast; Betty `test()` / `merge-tests` only on test-tree paths.

### Issues
**discuss (C4 stragglers):** Joan excluded `astral.debug.no-repo-root-artifacts-dir`, `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` — all in-scope on tip (features doc + Betty tests). Scored **conforms** (no product defect).

**advisory:** `user_prompt` still says LinkedIn/backstory “add context and color” without experience carve-out; quality checklist still says every key is a non-empty string; public `is_experience_job_array` alias + `key === "experience"` Save fallback beyond Stage 4 plan text.

### Recommended actions
No fix-now. Stragglers are process notes only — resolve-child may proceed without product edits unless Ada wants the advisory prompt/checklist tighten-ups.

## Resolution

**Date:** 2026-07-28  
**Review tip:** `8ed58ac4` (Radia `docs(AST-996): Radia review — findings`)  
**Overall:** DISCUSS → resolved for User Testing (no fix-now)

### fix-now
(none)

### discuss
C4 stragglers (Joan exclusions vs tip in-scope statutes) — accepted as process notes; all already **conforms** on tip. No product change.

### advisory
1. `craft_resume_base` `user_prompt` — added experience carve-out so LinkedIn/backstory “context and color” does not override paste-faithful experience (aligns with Stage 3 / AC3).
2. Quality checklist — “every key is a non-empty string” → experience may be a job array; string sections remain non-empty when sourced.
3. Public `is_experience_job_array` + ArtifactEditor `key === "experience"` Save fallback — left as-is (harmless for siblings / structureMode; Radia noted beyond plan text only).
