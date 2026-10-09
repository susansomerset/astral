<!-- linear-archive: AST-1063 archived 2026-08-07 -->

## Linear archive (AST-1063)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1063/job-carried-rubric-hydration-for-list-columns-issue-with-the-rubric  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** Medium / —  
**Parent:** AST-1059 — Issue with the rubric grade displays on the Jobs List pages  
**Blocked by / blocks / related:** parent: AST-1059; blocks: AST-1064

### Description

## What this implements

Owns write-path snapshot + API/job payload lift of the **analysis-time hydrated rubric** so list pages can build headers and tooltips without the live candidate rubric. Discovery: criteria are **not** already stored on `job_data` today — persist `{prefix}_rubric` beside grades, then flatten on list/detail. Does **not** own table grouping UI or score column paint (AST-1064).

## In scope

- [X] `pattern.layers.import-discipline` — list consumers paint API-shaped job data; no inventing criteria from live candidate artifacts in this ticket’s API surface
- [X] `astral.layers.import-direction` — UI over API; `_flatten_grades` lifts job-carried `*_rubric` / existing `*_score`
- [X] `astral.config.config-source-of-truth` — section → grade-field mapping stays config (`JOBS_*_GRADE_FIELD`); job-carried key = `grade_field.replace("_grades", "_rubric")`
- [X] `astral.layers.ui-config-driven-business-logic` — grade-field resolution remains config/manifest; React column switch is sibling

## Considered but excluded

- [X] Job-list tables keyed by job-carried rubric fingerprint — AST-1064 (new-pattern flag on parent)
- [X] Skipped / In Review grade-dot paint + Score column render — AST-1064
- [X] Live candidate rubric / `JOBS_UI_GRADE_RUBRIC` artifact remap — not this ticket
- [X] Historical job_data backfill / re-grade — Boundaries
- [X] Recommended phase-score UI / meteorite GDL — Boundaries
- [X] `astral.agent.grade-vector-validation` — parent secondary; not primary list hydration bug

## Acceptance criteria

1. [x] List grade columns for a section are derived from each job group’s **job-carried hydrated rubric**, not from the live candidate rubric artifact. Changing the live rubric without re-analyzing jobs does not retitle empty columns over old grades. *(This ticket: persist + surface* `*_rubric` *on job/list payload; AST-1064 consumes it for columns.)*
2. [x] Score on those rows is the **analysis-time score from job data**, consistent with the grades shown for that analysis. *(This ticket: keep* `*_score` */* `latest_score` *flattened; do not recompute from live rubric.)*

## Boundaries

* Does **not** own Skipped/In Review table grouping UI or grade-dot paint (sibling Katherine / AST-1064).
* Does **not** re-grade jobs or rewrite historical grades/scores.
* Does **not** change Recommended phase-score UI or meteorite GDL.

## Notes for planning

Plan corrects parent note: fully hydrated rubrics were **not** on job data — snapshot at grade-write (`consult`) + flatten (`api_jobs`). Pre-snapshot jobs omit `*_rubric`; sibling defines grades-only fallback. New pattern for group-by tables remains sibling scope.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1059-rubric-grade-displays-jobs-list`, child `sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-30T01:28:59.047Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1063
**Publish ref:** `c5a92b2f8414ad2084b5be251feab0730a378076` (`origin/sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns`)
**Overall:** DISCUSS

Three-dot: `origin/dev...origin/sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns`. Diff layers: core, ui, docs. Product footprint: `src/core/consult.py` (`_rubric_snapshot_for_job_data` + three write sites), `src/ui/api/api_jobs.py` (`_flatten_grades` + detail). Plan doc + Betty tests/bible via `merge-tests`.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | no confidence bounds change |
| astral.agent.do-task-delegation | scoped | conforms | snapshot beside existing do_task/verdict paths |
| astral.agent.grade-vector-validation | scoped | conforms | no grade-vector validation change |
| astral.batch.batch-id-first | scoped | conforms | no new batch claim APIs |
| astral.batch.batch-id-format | scoped | conforms | untouched |
| astral.batch.claim-process-release | scoped | conforms | snapshot inside existing process/verdict saves |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | untouched |
| astral.config.config-source-of-truth | scoped | conforms | key pairing from existing *_grades / save_prefix |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | applies_when.paths no match |
| astral.debug.spikes-under-debug-dir | scoped | conforms | no spike artifacts committed; plan smoke uses gitignored debug/spikes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single plan file under docs/features/interface/ |
| astral.git.betty-no-src-or-features | scoped | conforms | src + features via code/docs; Betty merge-tests only tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer code(AST-1063) touched src only; tests via Betty merge-tests |
| astral.layers.core-vs-external-bright-line | scoped | conforms | persist in core consult; no external |
| astral.layers.import-direction | scoped | conforms | api_jobs lifts stored keys only; no consult import in UI |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | applies_when.layers no match |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | section→grade_field stays config; React is AST-1064 |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | snapshot in _apply_render_verdict_decoded_job |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | list + detail remain @require_auth |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer logging |
| astral.standards.database-header-inventory | scoped | not-applicable | applies_when.layers no match |
| astral.standards.debug-contract-gated | scoped | conforms | no new ungated debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | one snapshot helper; three write sites |
| astral.standards.in-scope-only | scoped | conforms | no list UI / Recommended / backfill |
| astral.standards.logging-via-utils | scoped | conforms | untouched |
| astral.standards.no-cross-contamination | scoped | conforms | core write + ui flatten only |
| astral.standards.no-hardcoded-sets | scoped | conforms | flatten keys parallel existing grade/score names |
| astral.standards.public-then-helpers | scoped | conforms | helper beside hydrate helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | applies_when.layers no match |
| astral.state.core-decides-transitions | scoped | conforms | no transition changes |
| astral.state.job-prior-states-enforced | scoped | conforms | untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | untouched |
| astral.ui.frontend-file-placement | scoped | not-applicable | applies_when.paths no match |
| astral.ui.naming-conventions | scoped | conforms | snake_case *_rubric API fields |
| astral.ui.single-gunicorn-worker | scoped | conforms | untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests(AST-1063) one SHA on tip |
| orch.git.commit-vocabulary | universal | conforms | code/docs/test/merge-tests vocabulary used |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | sub/AST-1059/AST-1063-… |
| orch.git.merge-on-checkout | universal | conforms | no evidence of skipped ftr merge on this tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rewrite ops in tip history for this ticket |
| orch.git.no-dev-agent-branches | universal | conforms | ticket sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1059 worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | jd_rubric naming decided in plan; no open product Q |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–3 match diff; UI deferred to AST-1064 |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Interface child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | test/bible via Betty merge-tests after engineer code |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | assignee remains Ada |
| orch.roles.pre-commit-path-bans | universal | conforms | role-split commits respected on tip |

## Pattern conformance

| id | verdict |
| -- | -- |
| pattern.layers.import-discipline | conforms — list consumers paint API-shaped job data; no live-candidate criteria invent in API |
| (via statutes) astral.layers.import-direction | conforms |
| (via statutes) astral.config.config-source-of-truth | conforms |
| (via statutes) astral.layers.ui-config-driven-business-logic | conforms |

## Plan adherence

Matches plan stages 1–3: snapshot helper omits `content`, write-time persist on verdict/joblist/jd, `_flatten_grades` + detail lift. Self-Assessment Single-Component holds. Boundary vs AST-1064 held (no list React / grouping / live `JOBS_UI_GRADE_RUBRIC` remap / backfill).

## Findings

### fix-now
(none)

### discuss
1. **straggler** — Joan excluded `astral.debug.spikes-under-debug-dir` at plan time; three-dot vs `origin/dev` in-scope → **conforms** (no committed spikes).
2. **straggler** — Joan excluded `astral.docs.features-single-file-per-ticket`; in-scope → **conforms** (single plan file).
3. **straggler** — Joan excluded `astral.git.engineer-test-tree-ban`; in-scope via Betty `tests/` / bible on tip → **conforms** (`code(AST-1063)` was src-only; tests via `merge-tests`).

### advisory
(none)

## What’s solid
- Job-carried `*_rubric` written beside grades from the same criteria used to hydrate/score.
- API flatten is the single lift path for list + detail; scores not recomputed from live rubric.

## Recommended actions
Acknowledge stragglers → resolve-child → User Testing (no product delta).

docs() on publish ref: `docs(AST-1063): Radia review — findings` @ `c5a92b2f`.

context_tokens≈42000

#### betty — 2026-07-30T01:25:02.384Z
1. `tests/component/core/test_consult.py::TestAst1063JobCarriedRubricHydration` — snapshot omits `content` / preserves order / ensure-on-copy; persist `do_rubric` / `joblist_rubric` / `jd_rubric` on verdict / qualify / evaluate_jd writes
2. `tests/component/ui/api/test_api_jobs.py::TestFlattenGrades` — lifts `*_rubric` + scores; pre-snapshot jobs omit `*_rubric` keys

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst1063JobCarriedRubricHydration \
  tests/component/ui/api/test_api_jobs.py::TestFlattenGrades \
  -q
```

**Broken / obsolete:** none for this diff (additive).
**Integration:** none revised.

**Publish:** `origin/sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns` @ `b9b61e63` (`merge-tests(AST-1063): origin/tests d5839b4a`)

**Bible shasum on publish-ref:**
- `docs/test-bible/core/consult.md` `f0791727998bc1afe91926e8819e3048901b703f`
- `docs/test-bible/ui/api/api_jobs.md` `ccb6c08a897c59d89812800b9d0b5911d6357e02`

#### joan — 2026-07-30T01:13:49.992Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1063
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `96787e7a`. Publish ref `origin/sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns`. Discovery corrects parent “rubric already on job_data” — verified: grade saves write `*_grades` / scores only today; list UI still reads live `JOBS_UI_GRADE_RUBRIC` artifacts.
**Implementer:** Ada (parent Team table / plan author).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 List columns from job-carried hydrated rubric (not live candidate) | Stages 1–3 persist + flatten `*_rubric`; column consume N/A — AST-1064 |
| 2 Separate tables when rubric shape differs | N/A — boundary: AST-1064 |
| 3 Shared-shape group paints all vectors | N/A — boundary: AST-1064 |
| 4 Score = analysis-time job data | Stage 3 keeps `*_score` / `latest_score` lift; no live recompute |
| 5 In Review same rules | Stage 3 lifts on `view=in_review` via same `_flatten_grades`; UI N/A — AST-1064 |
| 6 Happy path single shared-rubric table | N/A — boundary: AST-1064 (payload enables it) |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 Persist + surface `*_rubric` on job/list payload | 1–3 (+ Stage 4 smoke) |
| 2 Keep analysis-time `*_score` / `latest_score`; do not recompute from live rubric | 3 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Snapshot helper | Purpose / Functional scope job-carried hydration |
| 2 Persist on every grade write | AC1 write path; Architecture import-discipline |
| 3 API `_flatten_grades` lift | AC1 surface + AC2/4 score consistency; import-direction |
| 4 Manual smoke | Builder verification of AC1/2 readiness for sibling |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1063):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Prerequisite merge gate correct |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1059` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | No open product questions; `jd_rubric` vs `jobdesc_rubric` decided |
| orch.pipeline.plan-is-bible | conforms | Stages binding; UI sibling excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Interface |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope (QA note only) |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | Snapshot beside existing do_task/verdict paths |
| astral.agent.grade-vector-validation | conforms | No validation change; secondary per parent |
| astral.batch.batch-id-first | conforms | No new batch APIs |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Snapshot inside existing process/verdict |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Key convention from existing `*_grades` / save_prefix; no dual-source into live `JOBS_UI_GRADE_RUBRIC` |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | Persist in core consult |
| astral.layers.import-direction | conforms | ui `api_jobs` lifts only; no UI→data; API does not import consult |
| astral.layers.ui-config-driven-business-logic | conforms | Section→grade_field stays config; React consume is sibling |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Snapshot in `_apply_render_verdict_decoded_job` |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Existing `@require_auth` list routes |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging |
| astral.standards.debug-contract-gated | conforms | No new ungated debug |
| astral.standards.dry-and-focused-functions | conforms | One snapshot helper; three write sites |
| astral.standards.in-scope-only | conforms | Excludes list UI, Recommended, backfill, live rubric edits |
| astral.standards.logging-via-utils | conforms | Untouched |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | Key pairing from existing grade field names |
| astral.standards.public-then-helpers | conforms | Helper near hydrate helpers |
| astral.state.core-decides-transitions | conforms | No transition changes |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.naming-conventions | conforms | Snake_case API fields |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.standards.utils-data-late-import-only — layers/paths miss
- astral.ui.frontend-file-placement — paths miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. Parent “already lives on job” corrected — write-time snapshot is the right product fix.
2. `jd_rubric` (job-carried) ≠ `jobdesc_rubric` (candidate artifact / `JOBS_UI_GRADE_RUBRIC`) — documented; sibling must not reuse live map for columns.
3. Shared names `joblist_rubric` / `do_rubric` / `get_rubric` / `like_rubric` exist on candidate artifacts and will also be job_data keys — distinct objects; list JSON lift is unambiguous.
4. Historical jobs without snapshot — grades-only fallback owned by AST-1064.
5. Self-assessment Single-Component / Conf Medium / Risk Medium — honest about write-site completeness risk.
6. All three grade write sites in `consult.py` covered (`_apply_render_verdict_decoded_job`, joblist, jd); no other `*_grades` writers found.

— Joan
context_tokens≈45000

#### ada — 2026-07-30T01:08:04.905Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns/docs/features/interface/ast-1063-job-carried-rubric-hydration-for-list-columns.md

`origin/sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns` @ `96787e7a`

**Scope:** Single-Component — `consult.py` grade-write snapshot + `api_jobs.py` flatten only.

**Conf:** Medium — write sites are few and known, but parent “rubric already on job” was wrong; historical jobs stay without `*_rubric` until re-graded (AST-1064 fallback).

**Risk:** Medium — a missed write site leaves that phase without job-carried rubric for the sibling list work.

---

# Job-carried rubric hydration for list columns

**Linear:** [AST-1063](https://linear.app/astralcareermatch/issue/AST-1063/job-carried-rubric-hydration-for-list-columns-issue-with-the-rubric)  
**Parent:** [AST-1059 — Issue with the rubric grade displays on the Jobs List pages](https://linear.app/astralcareermatch/issue/AST-1059/issue-with-the-rubric-grade-displays-on-the-jobs-list-pages)  
**Publish ref (origin):** `sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns`  
**Parent integration ref:** `ftr/AST-1059-rubric-grade-displays-jobs-list`  
**Blocks:** [AST-1064](https://linear.app/astralcareermatch/issue/AST-1064/group-by-aligned-rubric-jobs-list-tables-issue-with-the-rubric-grade) (consumer of this payload; list grouping / grade-dot / Score paint)

Persist and surface the **analysis-time rubric criteria** with each graded job so Skipped / In Review list APIs return a job-carried hydrated rubric for headers and tooltips — never forcing list consumers to read the **live** candidate rubric artifact. Also keep analysis-time scores visible on the same list payload (already partially lifted). Does **not** own Jobs list grouping UI, grade-dot paint, Score column rendering, Recommended phase-score layout, re-grading, or live rubric edits.

---

## Discovery (binding)

Parent wording said the fully hydrated rubric “already lives with the job’s analysis data.” **That is false today.**

- Grade write paths (`_apply_render_verdict_decoded_job`, qualify `joblist_*`, evaluate `jd_*`) call `_rubric_criteria_for_cfg` / `rubric_list` only to hydrate reasons and score, then save `{prefix}_grades` (+ optional `{prefix}_score` / notes). **No rubric criteria list is written to `job_data`.**
- List UI (`JobsSkipped.tsx` / `JobsInReview.tsx`) builds columns via `buildJobListRubricColumns` from **live** `candidate_data.artifacts[JOBS_UI_GRADE_RUBRIC[gradeKey]]` — the UAT dash sea when live rubric labels diverge from stored grade `vector` names.
- Grades already carry analysis-time **vector labels**, letters, confidence, and often **reason** text. Missing for headers: **code**, **importance**, **grade_descriptions** (for tip fallback when reason empty).

This ticket **must** snapshot criteria at write time, then lift them on list responses. Historical jobs without a snapshot stay without `{prefix}_rubric` until re-graded; AST-1064 defines any grades-only fallback for those rows.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns`; `git merge origin/dev`; `git merge origin/ftr/AST-1059-rubric-grade-displays-jobs-list`; merge-clean gate (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).
2. Do **not** merge or implement AST-1064 UI work on this ref.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Snapshot helper; write `{prefix}_rubric` beside every `{prefix}_grades` save | core |
| `src/ui/api/api_jobs.py` | Flatten `{prefix}_rubric` (+ ensure `{prefix}_score` lift unchanged) on list/detail payloads | ui |

**Out of scope:** `JobsSkipped.tsx` / `JobsInReview.tsx` / `rubricDisplay.ts` grouping or column source switch (AST-1064); Recommended pages; `JOBS_UI_GRADE_RUBRIC` live-artifact map changes unless a one-line comment clarifying “candidate artifact key, not job-carried”; backfill scripts for historical jobs; `tests/` / bible (Betty).

**Contract for AST-1064 (consume only — do not implement here):**

| Section grade field (`JOBS_*_GRADE_FIELD`) | Job-carried rubric key on list JSON | Analysis-time score key(s) |
|-------------------------------------------|-------------------------------------|----------------------------|
| `joblist_grades` | `joblist_rubric` | `joblist_score`, else existing `latest_score` lift |
| `jd_grades` | `jd_rubric` | `jd_score` (+ `latest_score` when set) |
| `get_grades` | `get_rubric` | `get_score` |
| `do_grades` | `do_rubric` | `do_score` |
| `like_grades` | `like_rubric` | `like_score` |

Derive convention: `grade_field.replace("_grades", "_rubric")` / `"_score"`. Do **not** reuse candidate artifact key `jobdesc_rubric` as the job-carried key — job carried is always `jd_rubric`.

Each `*_rubric` value is a **list** of criterion dicts:

```python
{
  "code": str | None,
  "label": str | None,
  "importance": int | float | None,  # as stored on criterion at analysis time
  "grade_descriptions": [{"grade": "A"|"B"|..., "description": str}, ...],
}
```

- **No** `content` field in the snapshot (keep blob size down; descriptions already parsed).
- Absent or empty `*_rubric` means “pre-snapshot job” — AST-1064 may fall back; do not invent live-artifact merge in Ada’s API.

**QA note (Betty):** After land, assert list payloads include `*_rubric` when a fresh grade write runs; assert codes/labels match the criteria used at write (not live candidate after rubric rename); assert scores still flatten. Historical fixture without snapshot: key absent.

---

## Stage 1: Snapshot helper in `consult.py`

**Done when:** A pure helper turns a criteria list into the job-carried shape above; unit-callable with no tracker I/O; criteria with missing `grade_descriptions` get them via `ensure_criterion_grade_table` on a **copy** (do not strip content from the live criteria object used for scoring in the same request).

1. In `src/core/consult.py`, near `_hydrate_grade_reasons_from_rubric`, add:

   ```python
   def _rubric_snapshot_for_job_data(rubric_criteria: list) -> list:
       """Analysis-time rubric criteria for list headers (AST-1063). Omits content."""
   ```

2. Behavior (exact):

   - If `rubric_criteria` is not a list or is empty → return `[]`.
   - For each dict item: shallow-copy the item (or build a new dict); if `grade_descriptions` missing/empty, call `rubric_text.ensure_criterion_grade_table` on the **working copy only** (catch `ValueError` → leave `grade_descriptions` as `[]`).
   - Append `{"code": …, "label": …, "importance": …, "grade_descriptions": …}` only (drop `content` and any other keys).
   - Preserve order of the input criteria list (do not re-sort; UI importance-sort is AST-1064).

⚠️ **Decision:** Snapshot at write time rather than reconstructing from grade `vector` strings alone — codes / importance / grade_descriptions are not on grade rows, and parent AC requires job-carried **hydrated rubric**, not live candidate artifact.

---

## Stage 2: Persist snapshot on every grade write path

**Done when:** Every successful save of `joblist_grades`, `jd_grades`, or `{save_prefix}_grades` also writes the matching `*_rubric` from the **same** `rubric_criteria` / `rubric_list` used for reason hydrate + score in that call. No new transitions; no re-grade of existing jobs.

1. **`_apply_render_verdict_decoded_job`** (get/do/like and any path using it): after building `rubric_criteria` and before/with `save_data`, set:

   ```python
   save_data[f"{prefix}_rubric"] = _rubric_snapshot_for_job_data(rubric_criteria)
   ```

   always when grades are saved (even binary / empty score), so list headers match stored grades for that analysis.

2. **`qualify_job_listings` / `_save_joblist_result`**: when writing `joblist_grades`, also set `joblist_rubric` from the outer `rubric_list` (same list used for `_score_from_grades`). If `rubric_list` is empty, still write `joblist_rubric: []` when grades are written (explicit empty vs key-absent for pre-change data).

3. **`evaluate_jd_batch` `process`**: when writing `jd_grades`, also set `jd_rubric` from the outer `rubric_list` (same rule as joblist).

4. Do **not** change `_render_score`, transition rules, or reason hydration semantics beyond ensuring the snapshot reflects the criteria already in hand.

5. Do **not** backfill historical `job_data` in this ticket.

---

## Stage 3: List / detail API flatten

**Done when:** `GET /api/jobs?view=in_review|skipped|recommended` (and any existing detail path that already uses `_flatten_grades`) lifts `joblist_rubric`, `jd_rubric`, `get_rubric`, `do_rubric`, `like_rubric` to the top-level job object the same way grades/scores are lifted. Score keys already in `_flatten_grades` remain; do not recompute scores from live rubric.

1. In `src/ui/api/api_jobs.py` `_flatten_grades`, extend the key loop (or a second loop) to also lift:

   ```text
   joblist_rubric, jd_rubric, get_rubric, do_rubric, like_rubric
   ```

   from `job_data` when present (same pattern as grades).

2. Keep existing score lift (`*_score` and `latest_score` ← `joblist_score` fallback). **Do not** add live-artifact reading in the API.

3. If a job detail endpoint bypasses `_flatten_grades`, apply the same lift there or route through `_flatten_grades` — grep `get_job` / detail handlers in `api_jobs.py` and match list behavior. Prefer one helper path.

⚠️ **Decision:** Lift on API rather than forcing the UI to dig `job_data.*` — matches current grades flatten and keeps AST-1064 on top-level fields only (`astral.layers.import-direction` / import-discipline).

---

## Stage 4: Manual smoke (builder)

**Done when:** After a local grade write (or unit-level save_job_data of grades+rubric), list JSON shows matching `*_rubric` codes/labels alongside `*_grades` vectors; changing the live candidate rubric in DB **without** re-grading does **not** change the job-carried `*_rubric` on that job.

1. Smoke with one existing consult write path (prefer `grade_like` or `evaluate_jd`) against a temp candidate, or assert via a focused call of `_rubric_snapshot_for_job_data` + `save_job_data` + `_flatten_grades` in a throwaway `debug/spikes/` script (gitignored). Do not commit spike scripts.
2. Confirm AC2 readiness for sibling: `*_score` / `latest_score` still present on flattened jobs when job_data holds them.

---

## Self-Assessment

**Scope:** `Single-Component` — consult grade-write + `api_jobs` flatten only; no list React, no Recommended, no live rubric schema.

**Conf:** `Medium` — write sites are known and few, but parent “already lives” was wrong; historical absence + empty-rubric edge need sibling fallback (documented, not implemented here).

**Risk:** `Medium` — missing a write site leaves some phases without `*_rubric` and AST-1064 still shows dashes for those rows; oversized snapshots if we mistakenly keep `content` (plan omits it).

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** One snapshot helper; three call sites (verdict + joblist + jd) instead of three copy-pasted serializers.
- **§2.1 config:** No new config block; grade/rubric key pairing follows existing `save_prefix` / `*_grades` names. Do not dual-source into `JOBS_UI_GRADE_RUBRIC` (that remains candidate artifact ids for other consumers until AST-1064).
- **§2.4 batch:** Snapshot inside existing `process` / verdict paths — no new batch claim loop.
- **§2.6 state machine:** No state/transition changes.
- **§3.3 imports:** `rubric_text.ensure_criterion_grade_table` stays utils→consult; API does not import consult — only lifts stored keys.
- **§3.5 naming:** `*_rubric` parallel to `*_grades` / `*_score`; `jd_rubric` not `jobdesc_rubric` on job payload.
- **import-direction / ui-config-driven:** API shapes job payloads; section→grade_field stays config/manifest; React (sibling) paints resolved shapes without inventing live rubric criteria.

---

## Review (build)

**Built:** `origin/sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns` @ `bb67d4920ec0d867473d46b04fc13202380a49ac`

Stages 1–3: `_rubric_snapshot_for_job_data`; persist `*_rubric` on verdict / joblist / jd writes; `_flatten_grades` + detail lift. Stage 4 smoke: snapshot omits content, flatten lifts rubric/scores. Tests deferred to Betty.

## Radia review (code-rubric.v1)

**Date:** 2026-07-30  
**Publish tip before this docs commit:** `b9b61e6352611e74034765165f5168ae62e53f4b`  
**Overall:** DISCUSS — **fix-now:** none; **discuss:** statute straggler ×3 (substance **conforms**); no advisory.

### What’s solid
- `_rubric_snapshot_for_job_data` omits `content`, copies before `ensure_criterion_grade_table`, covers verdict / joblist / jd write sites.
- `_flatten_grades` lifts all five `*_rubric` keys; detail now shares the helper; scores unchanged.
- Boundaries held vs AST-1064 (no list React / grouping / live artifact remap).

### Issues
- **discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot vs `origin/dev` brings them in-scope — all score **conforms** (no product delta).

### Recommended actions
- Acknowledge stragglers → resolve-child → User Testing (same pattern as recent clean DISCUSS tips).


## Resolution

**Date:** 2026-07-30  
**Publish tip before resolve:** `c5a92b2f` (`docs(AST-1063): Radia review — findings` on `origin/sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns`)

| Finding | Action |
| -- | -- |
| fix-now | none |
| discuss — statute stragglers ×3 (all conforms) | **No action** — informational plan-vs-diff predicate drift only. |

No product code changes in resolve. Proceeding to User Testing after §9a dry-run.

---

## Bug: AST-1327 — Missing vector grades in Analysis-tab headers (meteorites)

### As-is

On Recommended Job Report → **Analysis** tab, collapsed phase headers show only a subset of per-vector grade icons for **meteorite** jobs (often a single shared vector such as Quality Check / Gut Check). **Gazer** jobs show the full grade row. Expanded phase bodies already list every graded vector via `AgentAnalysisHeader`. **JD Analysis** opens expanded by default (`default_expanded: p.tab_id === "phase_jd"`).

### To-be

Collapsed Analysis section headers show a grade+confidence cell for **every** graded vector on that phase for meteorites and gazers alike, using analysis-time **job-carried** `*_rubric` (with grades-only fallback when the snapshot is absent). Expanded body vector identity/labels follow the same job-carried source. All Analysis-tab sections start **collapsed**. Summary / Artifacts expand rules unchanged.

### Repro

1. Open a meteorite Recommended job whose `jd_grades` has multiple vectors (e.g. Embedded/Firmware, International, ML/IC, Onsite, Pre-PMF, Quality Check, Gut Check) while the candidate’s live `jobdesc_rubric` only overlaps on a subset.
2. Analysis → JD Analysis header (collapsed): only the overlapping vector(s) appear in `.recommended-report-phase-grade-row`.
3. Expand the section: `.analysis-header` lists every grade row from `jd_grades`.
4. Repeat on a gazer job graded against live `jobdesc_rubric`: header row matches body.
5. Open Analysis: JD Analysis panel has `aria-expanded="true"`; other phases collapsed.

Fixture shape (no DB seed — file/JSON persistence):

```json
{
  "jd_grades": [
    {"vector": "Embedded/Firmware/Hardware Domain", "grade": "A", "confidence": 5},
    {"vector": "Quality Check", "grade": "B", "confidence": 4}
  ],
  "jd_rubric": [
    {"code": "EFW", "label": "Embedded/Firmware/Hardware Domain", "importance": 1, "grade_descriptions": []},
    {"code": "QC", "label": "Quality Check", "importance": 5, "grade_descriptions": []}
  ]
}
```

With live candidate `artifacts.jobdesc_rubric` containing only Quality Check, pre-fix header shows one cell; post-fix shows two from `jd_rubric`.

### Root cause

AST-950 wired Analysis header metadata through `buildPhaseSectionGradeConfidenceRow(gradesRaw, rubricKey, candidateArtifacts)` where `rubricKey = manifest.jobs.grade_rubric_by_field[phase.grades_field]` → always `jobdesc_rubric` for `jd_grades` (`JOBS_UI_GRADE_RUBRIC`). Meteorite JD shares `jd_grades` / `jd_rubric` storage but was scored against **`meteorite_jobdesc_rubric`** (config already documents this in `JOBS_UI_STATE_RUBRIC_OVERRIDE`; list UI / consult text paths honor it; Analysis tab does not).

Header columns are built from the **live** gazer artifact; `gradeAndConfidenceForCol` skips non-matching grade vectors (`if (!grade) continue`). Body uses `gradesForHeader(gradesRaw)` (iterate grades) so every vector appears. AST-1063 already persists + flattens job-carried `*_rubric` on detail (`GET /api/jobs/<id>` → `_flatten_grades`); Analysis never consumes it.

Secondary: Analysis section expand hardcodes JD open — contradicts current UAT ask (collapse all Analysis sections).

### Proposed change

Frontend-only consumer of AST-1063 payload on the Recommended report Analysis tab. Reuse `jobCarriedRubricKey` / `buildJobListRubricColumnsForGroup` (AST-1064) — do not reintroduce live `grade_rubric_by_field` / `candidateArtifacts` for header column identity. Do not change consult write paths or API flatten (already landed).

1. **`src/ui/frontend/src/lib/recommendedJobReport.tsx` — `buildPhaseSectionGradeConfidenceRow`**
   - Change signature to take the job object + `gradesField` (not live artifact key + `candidateArtifacts`):
     ```ts
     buildPhaseSectionGradeConfidenceRow(
       gradesRaw: unknown,
       job: Record<string, unknown>,
       gradesField: string,
     ): ReactNode
     ```
   - Build columns via `buildJobListRubricColumnsForGroup({ gradeKey: gradesField, columnSourceJob: job })` then `sortJobListRubricColumns` (same as Skipped/In Review). Paint grade+confidence cells exactly as today (`gradeAndConfidenceForCol` + `ConfidenceBullets`).
   - When job-carried `*_rubric` is absent/empty, `buildJobListRubricColumnsForGroup` already falls back to grades-only columns — keep that; **do not** fall back to live `jobdesc_rubric` / `meteorite_jobdesc_rubric` for header identity (that is the defect).
   - Update / remove `buildPhaseTabGradeDots` only if still referenced; if unused by Analysis, leave alone unless a single call site still passes live artifacts for this report.

2. **`src/ui/frontend/src/components/JobAnalysisReportModal.tsx`**
   - `renderAnalysisMetadata`: pass `job` + `phase.grades_field` into the revised helper; stop reading `manifest.jobs.grade_rubric_by_field` / `candidateArtifacts` for the header row.
   - `analysisSections`: set `default_expanded: false` for every phase (drop `p.tab_id === "phase_jd"`). Summary / Artifacts logic untouched.
   - `renderAnalysisSection` / `AgentAnalysisHeader`: pass job-carried rubric items for vector labels — resolve via `jobCarriedRubricKey(phase.grades_field)` from flattened job (top-level or `job_data`, same as `jobGradesForField`). Keep live `rubricArtifact` **only** as optional content lookup for “show rubric” (snapshot omits `content` per AST-1063); label/order must not depend on live artifact match. Prefer a small helper `jobRubricForField(job, gradesField)` next to `jobGradesForField` if it keeps both call sites DRY.
   - Extend local `JobDetail` typing with optional `jd_rubric` / `do_rubric` / `get_rubric` / `like_rubric` (and joblist if ever shown) so TypeScript matches `_flatten_grades`.

3. **Out of scope**
   - Consult snapshot / API flatten (AST-1063 already done).
   - Skipped / In Review list grouping (AST-1064).
   - Changing `JOBS_UI_GRADE_RUBRIC` / state override maps for other consumers.
   - Backfill historical `*_rubric`; grades-only fallback covers pre-snapshot rows.
   - `tests/` / bible (Betty / fix-board).

⚠️ **Decision:** Prefer job-carried `*_rubric` over wiring `jobs_ui_rubric_for_state` / live meteorite artifact into the Analysis tab. Job-carried matches analysis-time criteria for both pipelines without state branching in React; state override remains for consumers that still need a live artifact key.

### Blast radius

- Analysis header metadata + section default expand in Recommended Job Report only.
- Shared helper `buildPhaseSectionGradeConfidenceRow` — any test or caller still using `(grades, rubricKey, candidateArtifacts)` must update (Betty).
- `AgentAnalysisHeader` label path may accept explicit rubric items; other call sites (if any) keep current live-artifact behavior unless they pass the new prop.
- Does not affect Jobs list tables, Summary expand rules, or scoring.

### What must still hold

- AST-1063: job-carried `*_rubric` shape (no `content`); API flatten of `*_rubric` / `*_score` on list + detail; historical jobs may omit `*_rubric`.
- AST-950: horizontal grade+confidence header row; expanded body = phase `take_*` above per-vector rows; four phase sections (JD/DO/GET/LIKE); no Overview.
- AST-1064 contract: `grade_field.replace("_grades", "_rubric")`; grades-only fallback when snapshot missing — Analysis reuses that consumer pattern, does not invent a third source.
- Live candidate rubric edits without re-grade must not retitle Analysis header columns for already-graded jobs.

## Radia review (AST-1327 review-fix)

**Verdict:** REVIEW (DISCUSS, no fix-now) — Commit `a4549715`

**fix-now:** (none)

**Discuss:**
1. Stale AST-950 component tests still call old 3-arg `buildPhaseSectionGradeConfidenceRow` — tracked on sibling gap **AST-1328**; not product fix-now.
2. Meteorite “show rubric” content may still use `jobdesc_rubric` live key for modal content (headers fixed; content out of header-bug scope).

**Advisory:** `buildJobListRubricColumnsForGroup` top-level-only vs `jobRubricForField` job_data asymmetry — safe with API flatten; optional follow-up. Bible rows for AST-950 still live-artifact wording — AST-1328.

**What’s solid:** Analysis headers consume job-carried `*_rubric` via AST-1064 path; Analysis sections default collapsed; engineer test-tree ban held.

## docs-acceptance (AST-1327)

Test/bible coverage for this fix is owned by sibling gap **AST-1328** (Betty board TESTS: REVISE). Product code on this ref is docs-acceptance for merge-child — no fabricated `test(AST-1327)` noop.

---

## Bug: AST-1328 — gap: Analysis header job-carried / collapse tests

### As-is

No bible or component coverage for Recommended Analysis headers keyed off job-carried `*_rubric` (meteorite vs gazer live-artifact mismatch). Existing AST-950 asserts still call the pre–AST-1327 `buildPhaseSectionGradeConfidenceRow(grades, rubricArtifactKey, candidateArtifacts)` signature and expect **JD Analysis** default-expanded (`Collapse section` count === 1 on Analysis open). Against `origin/ftr/AST-1321-missing-vector-grades-rubric-headers` (AST-1327 product), those asserts fail (`gradeKey.endsWith is not a function`; no Collapse control until a section is expanded).

### To-be

Bible (`docs/test-bible/frontend/lib.md` + `components.md` AST-950 sections) and tests document/assert: header columns from job-carried `*_rubric` (or grades-only fallback); meteorite-shaped fixture where live `jobdesc_rubric` underlaps `jd_grades` still shows every graded vector in the header row; all four Analysis sections start collapsed. Obsolete live-artifact / JD-expanded AST-950 asserts are revised (not deleted wholesale).

### Repro

Against product tip with AST-1327 landed (no test updates):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  --testNamePattern="AST-950"
```

Fails: lib helper calls with `"jobdesc_rubric"` + artifacts map; JAR “JD expanded by default” / Collapse-first flows. Fixture that demonstrates the product bug (pre-fix) and the gap (post-fix without tests):

```json
{
  "jd_grades": [
    {"vector": "Embedded/Firmware/Hardware Domain", "grade": "A", "confidence": 5},
    {"vector": "Quality Check", "grade": "B", "confidence": 4}
  ],
  "jd_rubric": [
    {"code": "EFW", "label": "Embedded/Firmware/Hardware Domain", "importance": 1, "grade_descriptions": []},
    {"code": "QC", "label": "Quality Check", "importance": 5, "grade_descriptions": []}
  ]
}
```

with candidate `artifacts.jobdesc_rubric` containing only Quality Check — header must render **two** cells from `jd_rubric`, not one from live artifact.

### Root cause

Betty `[board-betty] TESTS: REVISE` on AST-1327: bible AST-950 rows still describe live-artifact header wiring; component tests encode AST-950 Stage 3 expand seed and old helper arity. Product fix shipped on AST-1327 without revising those contracts — gap child owns test/bible only.

### Proposed change

**Owner:** Betty (test-tree + bible). No product `src/` changes on this ticket — AST-1327 already landed job-carried headers + collapse-all. Do not reopen Analysis React for coverage convenience.

1. **`docs/test-bible/frontend/lib.md` (AST-950 section)**
   - Rewrite the AST-950 helper row: `buildPhaseSectionGradeConfidenceRow(gradesRaw, job, gradesField)` columns via `buildJobListRubricColumnsForGroup` / job-carried `*_rubric` (grades-only when snapshot absent) — **not** live `jobdesc_rubric` / `candidateArtifacts`.
   - Add a manifest line for meteorite mismatch: header cell count follows `jd_rubric` ∩ graded vectors when live gazer artifact underlaps.
   - Keep narrowed run command; add `--testNamePattern` tokens for any new describe names below.

2. **`docs/test-bible/frontend/components.md` (AST-950 section)**
   - Replace “JD Analysis default expanded” with **all Analysis sections start collapsed** (AST-1327 UAT).
   - Note JAR Analysis metadata uses job-carried flatten (`jd_rubric` et al. on job payload), not `grade_rubric_by_field` live lookup for header identity.
   - Point manifest at revised JAR + lib cases (and optional `AgentAnalysisHeader` job-carried `rubricItems` label case if covered).

3. **`tests/component/frontend/lib/test_recommendedJobReport.test.tsx` — describe `recommendedJobReport — AST-950 grade+confidence header row`**
   - Update both helper cases to the 3-arg job form:
     - Happy path: `job = { jd_grades: [...], jd_rubric: [{ code, label, importance }] }`; call `buildPhaseSectionGradeConfidenceRow(grades, job, "jd_grades")`.
     - Grades-only fallback: job with grades, **no** `jd_rubric` (or empty); still paints dots in array/column order.
   - **Add** a case: job has full `jd_rubric` + multi-vector `jd_grades`; if a third arg were live artifacts with underlapping `jobdesc_rubric`, header must still show all graded vectors (prove job-carried path — do not pass live artifacts into the helper at all).

4. **`tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — describe `JobAnalysisReportModal — AST-950 Analysis tab grades and confidence`**
   - Rename/revise “JD expanded by default”: on Analysis open, assert **zero** `Collapse section` and **four** `Expand section`; still no Overview; four phase labels present.
   - “header grade+confidence row visible when JD collapsed…”: start collapsed — assert header row/dots visible **before** expand; then expand JD to assert `take_jd` + body reason; collapse again and assert body hidden / header retained.
   - “expanded DO…”: first expand is no longer “after JD”; click the DO section’s Expand (by label/order) — keep take_do + reason asserts.
   - Empty-grades case: open Analysis with all collapsed; expand JD (or the empty phase) before asserting “No consult detail…” empty copy.
   - Extend at least one JAR fixture with top-level (or `job_data`) `jd_rubric` matching grades so header paint is job-carried, not live CandidateContext artifacts. Add one meteorite-mismatch fixture: multi-vector `jd_grades` + matching `jd_rubric`, CandidateContext `jobdesc_rubric` underlapping — expect header cell count === graded vectors present in `jd_rubric`.

5. **Out of scope**
   - Product changes under `src/ui/frontend` (AST-1327).
   - Skipped/In Review list tests (AST-1064).
   - New integration scenarios as the default.
   - Re-grading / consult snapshot writes.

⚠️ **Decision:** Revise AST-950 describes in place (same files Betty named) rather than inventing a parallel AST-1328-only test file — keeps the bible AST-950 run command the single narrowed suite for Analysis header chrome.

### Blast radius

- AST-950 bible sections + the two component test files above; any tip still on pre–AST-1327 helper arity will fail until this gap merges onto `ftr`.
- Does not change product behavior. Sibling AST-1327 remains the product source of truth.
- `test_ReportSectionList` AST-950 `renderMetadata` slot tests — touch only if they hardcode JD expand or old helper; otherwise leave.

### What must still hold

- AST-1327 / AST-1063: job-carried `*_rubric` header identity; grades-only fallback; Analysis all-collapsed; Summary/Artifacts expand rules unchanged.
- AST-950: horizontal grade+confidence header row; expanded body = `take_*` above `AgentAnalysisHeader`; four phases; no Overview.
- Engineer test-tree ban on AST-1327 stays intact — this gap child is the only place those asserts move.
- Live candidate rubric underlap must not shrink the Analysis header row when `*_rubric` is present on the job.

## Radia review (AST-1328 review-fix)

**Verdict:** PROCEED (CLEAN) — Commit `585397a4`

**fix-now / discuss:** none.

**Advisory:** lib bug-repro decoy placement harmless; optional AgentAnalysisHeader rubricItems label case not added.

**What’s solid:** bug-repro fixtures match plan; AST-950 suite migrated to job-carried; bible honest; merge-tests discipline held.

---

## Bug: AST-2059 — show rubric modal reads rubric content from hydrated candidate detail

**Mini-parent:** [AST-2058](https://linear.app/astralcareermatch/issue/AST-2058) · **Publish ref:** `sub/AST-2058/AST-2059-show-rubric-content` · **ftr:** `ftr/AST-2058-show-rubric-content`

### As-is

On the Recommended Job Report → **Analysis** tab (`JobAnalysisReportModal`) and on the agent story tab (`AgentStoryTab`), clicking **show rubric** next to a graded vector opens `RubricModal` with the correct title (`Rubric — <vector>`), but the body always reads `No rubric found for this vector.`

### To-be

**show rubric** shows that vector's criterion `content` for the selected candidate, matched by label or code the same way as today. While the content is loading, the modal shows a loading line instead of the not-found text. `No rubric found for this vector.` appears only when the candidate's hydrated rubric really has no matching row.

### Repro

Persistence is file/JSON plus the `rubric_vector` table, so the repro is a payload shape, not a seeded DB row.

1. Select a candidate whose `evaluate_jd` rubric lives in `rubric_vector` (any post-AST-723 candidate).
2. Open a Recommended job → **Analysis** → expand **JD Analysis** → click **show rubric** on any graded vector.
3. Modal body: `No rubric found for this vector.`

Data each source returns for that candidate:

```json
// GET /api/candidates  (CandidateContext list — raw candidate_data, never hydrated)
{ "astral_candidate_id": "c1", "candidate_data": { "artifacts": {} } }

// GET /api/candidates/c1  (detail — hydrate_rubric_artifacts_for_response ran)
{ "astral_candidate_id": "c1", "candidate_data": { "artifacts": {
  "jobdesc_rubric": [
    { "code": "QC", "label": "Quality Check", "importance": 5, "content": "Grade A when …" }
  ]
} } }

// job (flattened) — AST-1063 snapshot, no content by design
{ "jd_grades": [{ "vector": "Quality Check", "grade": "B", "confidence": 4 }],
  "jd_rubric": [{ "code": "QC", "label": "Quality Check", "importance": 5, "grade_descriptions": [] }] }
```

Before the fix, `AgentAnalysisHeader` reads the first payload, so `liveList` is `[]`, falls back to the `jd_rubric` row (no `content`), passes `content=null`, and the modal shows the fallback. After the fix it reads the second payload and the modal shows `Grade A when …`.

### Root cause

`AgentAnalysisHeader` gets rubric **content** from `useCandidate().candidates[].candidate_data.artifacts[rubricArtifact]`. `CandidateContext` loads that list from `GET /api/candidates`, which returns the raw `candidate_data` blob. Since AST-723, rubric criteria live in `rubric_vector`, not in the artifacts blob. They are only overlaid into `artifacts` by `hydrate_rubric_artifacts_for_response` (`src/core/candidate.py`), and that runs only on the single-candidate route `get_candidate_detail` (`GET /api/candidates/<id>`, `src/ui/api/api_candidate.py`). So `liveList` is always empty. The only other source is the job-carried `{prefix}_rubric` snapshot (this ticket, AST-1063), which leaves out `content` on purpose (Stage 1). With both sources lacking content, `RubricModal` gets `null` and renders the fallback.

### Proposed change

Frontend only. Two files, both in AST-2059 `## Scope`. No backend, API, or caller changes.

1. **`src/ui/frontend/src/components/AgentAnalysisHeader.tsx`** (modified component function)
   - Add `import { useEffect, useState } from "react"` (replacing the bare `useState` import) and `import api from "../lib/api"`.
   - New state: `const [detailArtifacts, setDetailArtifacts] = useState<Record<string, unknown> | null>(null)` and `const [contentLoading, setContentLoading] = useState(false)`.
   - New `useEffect`, deps `[rubricVector, selectedId, rubricArtifact]`:
     - When `!rubricVector || !selectedId || !rubricArtifact`, return without fetching.
     - Otherwise run `setContentLoading(true)`, `setDetailArtifacts(null)`, then `api(\`/api/candidates/${selectedId}\`)`. On `r.ok`, parse JSON and set `detailArtifacts` to `body?.candidate_data?.artifacts` when it is an object, otherwise `{}`. On `!r.ok` or a thrown error, set `{}` (this is "loaded, nothing found", not "still loading"). Always end with `setContentLoading(false)`.
     - Stale-response guard: use a local `let cancelled = false`, return a cleanup that sets `cancelled = true`, and skip both setters when `cancelled`. Closing the modal or switching candidates mid-fetch must not paint the wrong candidate's content.
     - Fetch on every modal open. No per-candidate cache, because a rubric edit elsewhere should show on the next open.
   - Split the live list in two:
     - `listLiveList`: the current derivation from `candidate?.candidate_data.artifacts[rubricArtifact]`, kept **only** for the existing `labelList` legacy fallback (`rubricItems` empty, as in `AgentStoryTab`). Grade-row labels and order stay exactly as they are today (AST-2059 Boundaries).
     - `contentLiveList`: `Array.isArray(detailArtifacts?.[rubricArtifact])`, otherwise `[]`. Every `findRubricRow(liveList, …)` inside the `contentRow` derivation switches to `contentLiveList`. The match order stays the same: live row by vector, then live row by `labelRow.code`, then `labelRow`.
   - Pass `loading={contentLoading}` to `RubricModal`.
   - ⚠️ **Decision:** the hydrated fetch feeds **content only**. AST-2059 Technical scope says to point the `liveList` derivation at the fetch, but letting it feed `labelList` too would retitle `AgentStoryTab` rows after the first modal open, which breaks the Boundary "no change to grade-row labels/order". Labels keep their pre-fix source.
2. **`src/ui/frontend/src/components/RubricModal.tsx`** (props interface plus render)
   - Add the optional prop `loading?: boolean`, defaulting to `false`.
   - Body: `loading ? "Loading rubric…" : (content ?? "No rubric found for this vector.")`. Title, `stacked`, and the `entity-jd-content` wrapper are unchanged.
3. **Out of scope:** `CandidateContext` (do not hydrate the list), `GET /api/candidates` and `hydrate_rubric_artifacts_for_response` (unchanged), the `{prefix}_rubric` snapshot shape (still no `content`), `JobAnalysisReportModal` / `AgentStoryTab` props, the meteorite `rubricArtifact` key choice (see Blast radius), and `tests/` / bible (Betty, via fix-board).

### Blast radius

- **Callers:** `JobAnalysisReportModal.renderAnalysisSection` (passes `rubricItems` plus `rubricArtifact = grade_rubric_by_field[phase.grades_field]`) and `AgentStoryTab` (passes `rubricArtifact = entry.rubric_artifact`, no `rubricItems`). Both keep their props and both get content through the new fetch.
- **Network:** one extra `GET /api/candidates/<id>` per **show rubric** click. That route also runs the operative hydrators (base resume, strengths, and others), so it is heavier than a rubric-only read. That is acceptable for a click-triggered fetch, and no new endpoint is allowed by scope.
- **Meteorite jobs:** the Analysis tab still passes `jobdesc_rubric` (the gazer key) for `jd_grades`, even though meteorites are scored against `meteorite_jobdesc_rubric`. This was flagged by Radia on AST-1327 (discuss item 2). After this fix, meteorite vectors that exist only in the meteorite rubric can still show not-found. Changing the key is a `JobAnalysisReportModal` change outside AST-2059 scope, so it is left alone here.
- **Tests:** any component test that renders `AgentAnalysisHeader` with a `CandidateContext` mock carrying `candidate_data.artifacts[rubricArtifact].content` and expects that text in the modal now needs a mocked `api` / `fetch` for `/api/candidates/<id>`. `RubricModal` tests that expect the fallback while content is `null` still pass (`loading` defaults to false). Betty owns these via fix-board.

### What must still hold

- AST-1063: the job-carried `*_rubric` snapshot omits `content`, and list/detail flatten is unchanged.
- AST-1327: header and body labels/order come from job-carried `rubricItems` when present (`sortGradesByRubricDisplayOrder`, `formatRubricVectorHeader`), and live-artifact label fallback applies only when `rubricItems` is empty.
- The **show rubric** button renders under the same condition as today: `rubricArtifact` set, or non-empty `rubricItems`.
- The content match order is unchanged: vector, then job-carried `code`, then the job-carried row.
- `RubricModal` keeps the `Rubric — <vector>` title and the exact fallback string `No rubric found for this vector.`
- No backend or API change. The `GET /api/candidates` list payload stays unhydrated.


## Joan fix-board — AST-2059

**Verdict (for Chuckles to post)**

```
[board-joan]  CANON: OK
```

**Stdout**

```text
AST-2059 board-joan done — CANON: OK.
```

**Triage note (not for Linear):** Read `## Bug: AST-2059` on `origin/sub/AST-2058/AST-2059-show-rubric-content` and skimmed overlap via `canon/docs/DIRECTIVES-DIRECTORY.md` / in-force UI+layer statutes (`docs/canon-index.md` absent on this ref, same as other fix-board passes). Frontend-only: on **show rubric**, `AgentAnalysisHeader` calls existing `GET /api/candidates/<id>` so rubric **content** comes from server-side `hydrate_rubric_artifacts_for_response`, while labels/order still use list context + job-carried `rubricItems` per plan boundaries. That matches `astral.layers.import-direction` (UI → API, hydration stays off the list route), `astral.layers.ui-config-driven-business-logic` (no new conditional rules in React; no API shape change), and `astral.ui.frontend-file-placement` (edits under `components/`). AST-1063’s no-`content` snapshot and “list stays unhydrated” are preserved in **What must still hold** — no carve-out or statute edit. Meteorite `rubricArtifact` key mismatch is documented blast radius and explicitly out of scope; not an Archie gate for this fix. F3 not indicated.

**Chuckles routing:** Betty's `TESTS: REVISE` routes to a test-gap sibling (test tree + bible), so qa-fix is skipped on AST-2059. Joan `CANON: OK`.


## Radia review — AST-2059

```
[code-rubric]
**Ticket:** AST-2059
**Publish ref:** `61f1f40ea6c050b2d72c42a21019407d05c49b9d` (`origin/sub/AST-2058/AST-2059-show-rubric-content`)
**Diff base:** `origin/ftr/AST-2058-show-rubric-content...origin/sub/AST-2058/AST-2059-show-rubric-content` (3 commits; product: `AgentAnalysisHeader.tsx`, `RubricModal.tsx` + plan-fix doc patch)
**Corpus:** `6f3edaa90d`
**Overall:** CLEAN

## Fix-specific checks

- **[bug-repro]** not applicable — clean board opt-out (`[board-betty] TESTS: REVISE` routed to test-gap sibling AST-2060; qa-fix did not run on this ticket).
- **## What must still hold — OK** — Traced all six bullets against the diff: no `src/core` / `src/ui/api` / snapshot changes; `labelList` still `rubricItems` → `listLiveList`; show-rubric gate unchanged; `contentRow` match order uses `contentLiveList` then `labelRow`; `RubricModal` title/fallback/loading strings match plan; hydration only via existing `GET /api/candidates/<id>` from the UI layer.

## Canon scores

*(Linear Description has no **Canon Scope (frozen at plan)** block. Scored Joan fix-board F2 overlap from issue doc § Joan fix-board — AST-2059, same fix-lane precedent as AST-1821 / AST-1892.)*

| id | grade | effort | one-line |
| -- | -- | -- | -- |
| astral.layers.import-direction | A | | UI uses `../lib/api` → existing detail route; no core/data import inversion |
| astral.layers.ui-config-driven-business-logic | A | | Display fetch only; no new conditional business rules in React |
| astral.ui.frontend-file-placement | A | | Edits confined to `src/ui/frontend/src/components/` |

## Column diff vs plan stage

no plan-stage scores attached (Joan pass was fix-board `CANON: OK`, not per-id `validate-plan` fix-mode rubric)

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

1. **Canon Scope process gap (Archie)** — AST-2059 Description never froze a canon id list; comparability with feature children relies on fix-board overlap skim only.  
   **Default:** Ship this tip; do not block on list backfill. Chuckles may note for Archie whether fix bugs should always get an explicit frozen block at intake.

### advisory

1. **Test bar deferred to AST-2060** — Betty `TESTS: REVISE` documents broken/missing component tests and the intended `[bug-repro]`; Ada’s Tests Passed note explains 8/8 green because mocks still satisfy modal text via `labelRow` / list fixture `content`, not the detail-fetch path. Product diff is still reviewable; regression lock lands on the sibling.
2. **Meteorite `rubricArtifact` key** — Plan blast radius: meteorite JD vectors may still show not-found; explicitly out of scope (same as AST-1327 discuss lineage).
3. **Plan vs implementation (loading)** — Plan-fix described effect-driven `contentLoading`; tip uses derived loading from keyed `detail` + `closeRubric` reset. Behavior matches To-be (no not-found flash, refetch each open); no product concern.

## What’s solid

- `listLiveList` / `contentLiveList` split preserves AST-1327 label/order boundaries while sourcing **content** from hydrated detail artifacts.
- Stale-response guard (`cancelled` + `detail.key` match on `selectedId:rubricArtifact`).
- Frontend-only footprint matches Estimate **2** and plan **Proposed change**.

## Recommended actions (Chuckles)

| Gate | Parent shape |
|------|----------------|
| **PROCEED** (C7 complete) | **Normal** mini-parent (live `ftr/AST-2058-show-rubric-content`, not orphaned-to-dev) → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** (`resolve-child` skipped). |

Append this artifact to the issue doc; commit `docs(AST-2059): Radia review — clean` on `origin/sub/AST-2058/AST-2059-show-rubric-content`; post slim upshot `--as radia`.

context_tokens≈28000
```

```
[code-rubric] PROCEED (Commit: 61f1f40ea) Hydrated detail rubric content
```

### Test delivery — AST-2059

No test-tree delivery on this sub (docs-acceptance). Betty's `[board-betty] TESTS: REVISE` coverage (URL-routed api mock, bug-repro, loading/failed-fetch cases, RubricModal bible entry) lands on test-gap sibling AST-2060, which is blocked by this ticket.

---

## Bug: AST-2060 — show rubric hydrated-content tests + bible (test gap for AST-2059)

**Mini-parent:** [AST-2058](https://linear.app/astralcareermatch/issue/AST-2058) · **Publish ref:** `sub/AST-2058/AST-2060-show-rubric-tests` · **Product fix:** AST-2059 (`61f1f40ea`, on `ftr/AST-2058-show-rubric-content`) · **Owner of edits:** Betty (test tree + bible). No `src/` change.

### As-is

`test_AgentAnalysisHeader.test.tsx` uses one `mockedApi.mockResolvedValue` for **every** call. It returns the `/api/candidates` list array, with no `ok` field, and the list rows carry `joblist_rubric` **with `content`**. On the AST-2059 tip, all 8 tests in `test_AgentAnalysisHeader` + `test_RubricModal` pass, but for the wrong reason:

- The detail fetch to `/api/candidates/c1` gets the list array. `r.ok` is undefined, so AST-2059 treats it as a failed fetch and `contentLiveList` is `[]`.
- Modal content then falls through to `labelRow`, which comes from the **list fixture** (`listLiveList`). That row carries `content`, so "Rubric body" / "Body" render anyway.
- The real `GET /api/candidates` never carries rubric rows (root cause, AST-2059 block). So these tests cover a payload production never sends, and they never exercise the hydrated detail fetch, the loading state, or the failed-fetch fallback.
- `test_RubricModal.test.tsx` has no `loading` case. `docs/test-bible/frontend/components.md` has no `RubricModal` entry, and the Analysis / job surfaces row doesn't mention the detail-fetch content source.

Betty's `[board-betty] TESTS: REVISE` on AST-2059 predicted that two tests would go **red**. They did not (AST-2059 test-fix run, 8/8 green), for the reason above. The fix those two tests need is to make the fixture realistic, not just to await the content.

### To-be

The header suite builds its fixtures the way production does. The list payload carries **no** rubric content, and the detail payload (`/api/candidates/c1`) carries hydrated `content`. Modal-content assertions pass only through the AST-2059 detail fetch. A bug-repro test fails on the pre-fix tree. The header's loading state (no not-found flash) and the failed-fetch fallback are asserted. `RubricModal` covers `loading`. The bible lists all of it.

### Repro

The test delta is itself the repro. Against the **pre-fix** tree (`06df211db`, before AST-2059), the new bug-repro case renders `No rubric found for this vector.` and fails its content assertion. Against `4ee1d7029` (AST-2059 merged), it passes.

```ts
// list (CandidateContext) — production shape: no rubric content
[{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { artifacts: {} } }]

// detail GET /api/candidates/c1 — hydrated
{ astral_candidate_id: "c1", candidate_data: { artifacts: {
  joblist_rubric: [{ label: "Fit", code: "FIT", content: "Hydrated body", importance: 8 }],
} } }
```

### Root cause

The AST-2059 product fix moved the content source to the detail fetch. The existing test fixtures predate it. They stuff `content` into the list payload, a shape that predates AST-723 and that the real list route doesn't return. They answer every URL with the same response, so the legacy `labelRow` fallback keeps content assertions green no matter where content actually comes from.

### Proposed change

Betty lands all of this via qa-fix, in `tests/` and `docs/test-bible/` only. Every item maps to AST-2060 `## Scope`.

1. **`tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx`**
   - **URL-routed mock helper.** At the top of the `describe` block, add a helper `mockApiRoutes({ list, detail })`, where `detail` is `Promise<Response>`, `Response`, or a function returning one. `beforeEach` installs it via `mockedApi.mockImplementation((path: string) => …)`:
     - `path === "/api/candidates"` → `{ ok: true, json: async () => list } as Response`
     - `path === "/api/candidates/c1"` → `detail`
     - any other path → the same list response as today, so `renderWithProviders` providers behave unchanged.
   - Default `list` = `[{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { artifacts: {} } }]`, with **no** `joblist_rubric` and no `content`. Default `detail` = `{ ok: true, json: async () => ({ astral_candidate_id: "c1", candidate_data: { artifacts: { joblist_rubric: [{ label: "Fit", code: "FIT", content: "Rubric body", importance: 8 }] } } }) }`.
   - **"renders grades with rubric links and opens the modal"** — use the defaults. After clicking **show rubric**, `expect(await screen.findByText("Rubric body")).toBeInTheDocument()` replaces the synchronous `getByText`.
   - **"matches rubric rows by code and handles missing modal content"** — keep the list empty. Set the detail to `joblist_rubric: [{ code: "FIT", content: "Body", importance: 8 }]` (code only, no label). Assert `await screen.findByText("Body")`.
   - **"opens the rubric modal with no matching row (null content)"** — use the defaults (the detail has only `Fit`, and the vector is `orphan`). Change to `expect(await screen.findByText("No rubric found for this vector.")).toBeInTheDocument()`.
   - **New bug-repro: `AST-2059: show rubric reads content from hydrated candidate detail, not the list payload`**
     - The list is the default (empty artifacts). Create a deferred detail promise: `let resolveDetail!: (r: Response) => void; const detail = new Promise<Response>(r => { resolveDetail = r })`.
     - Render `<AgentAnalysisHeader grades={[{ vector: "fit", grade: "A" }]} rubricArtifact="joblist_rubric" />` and click **show rubric**.
     - Before resolving: `expect(screen.getByText("Loading rubric…")).toBeInTheDocument()` **and** `expect(screen.queryByText("No rubric found for this vector.")).not.toBeInTheDocument()`. This is the AST-2059 no-flash AC.
     - `resolveDetail({ ok: true, json: async () => ({ candidate_data: { artifacts: { joblist_rubric: [{ label: "Fit", code: "FIT", content: "Hydrated body", importance: 8 }] } } }) } as Response)`.
     - `expect(await screen.findByText("Hydrated body")).toBeInTheDocument()`, then `expect(mockedApi).toHaveBeenCalledWith("/api/candidates/c1")`.
     - Pre-fix, this fails at the loading assertion and the content assertion (the modal shows the fallback immediately).
   - **New: `AST-2059: failed detail fetch ends on the fallback, not stuck loading`.** Two cases inside one `it` (or an `it.each`), each rendering `vector: "fit"` with `rubricArtifact="joblist_rubric"` and clicking **show rubric**:
     - detail = `{ ok: false, json: async () => ({}) } as Response`
     - detail = `Promise.reject(new Error("network"))`
     - For each: `expect(await screen.findByText("No rubric found for this vector.")).toBeInTheDocument()` and `expect(screen.queryByText("Loading rubric…")).not.toBeInTheDocument()`. Close the modal between cases, or `unmount`.
   - **Unchanged:** "falls back to raw vector labels without rubric data" (no `rubricArtifact`, so no fetch); "normalizes an empty vector key…" (button presence only); **AST-1771** order test (`rubricItems`, no modal). Keep the `vi.mock(... importOriginal ...)` keeper.
   - Optional, Betty's call: a stale-response test (switch candidate mid-fetch). Not required by AST-2060 AC.

2. **`tests/component/frontend/components/test_RubricModal.test.tsx`**
   - **New: `shows loading text instead of the fallback while loading`**: render `<RubricModal open onClose={vi.fn()} vector="Culture" content={null} loading />` and assert `getByText("Loading rubric…")`, `queryByText("No rubric found for this vector.")` absent, heading `Rubric — Culture` present.
   - Keep "shows rubric content and falls back when content is missing" as is. It proves `loading` defaults to false.

3. **`docs/test-bible/frontend/components.md`**
   - **Row at line 50 (Analysis / job surfaces):** Source becomes `AgentAnalysisHeader.tsx`, `RubricModal.tsx`, job pages. Add `tests/component/frontend/components/test_RubricModal.test.tsx` to Component tests.
   - **New section** after the last `### AST-…` block, before any trailing manifest, using the AST-1771 section shape: `### AST-2060 · AST-2058 (show rubric reads hydrated detail content)`, with Parent/Publish lines, a one-line summary (rubric content comes from `GET /api/candidates/<id>`, list payload carries none), an Area / Source / Component tests table (header content source → the three revised plus two new `test_AgentAnalysisHeader` cases; modal loading → the new `test_RubricModal` case), and **Broken / obsolete:** "header fixtures carried list-payload `content` (pre-AST-723 shape) — revised". **Integration:** none.
   - **QA test manifest — AST-2060** with the narrowed command:

     ```bash
     cd src/ui/frontend && npm run test:component -- \
       ../../../tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx \
       ../../../tests/component/frontend/components/test_RubricModal.test.tsx
     ```

4. **Out of scope:** any `src/` change (AST-2059); the meteorite `rubricArtifact` key mismatch; `test_JobAnalysisReportModal.test.tsx` (it never clicks show rubric); `CandidateContext` tests.

⚠️ **Decision:** the header-level no-flash check goes inside the bug-repro test, using a deferred promise, rather than a separate test function. That keeps the new header functions to the two AST-2060 Technical scope names (repro + failed fetch), while still covering the loading-state gap from the AST-2059 test-fix note.

⚠️ **Decision:** unknown URLs fall back to the list response, as the mock does today, rather than a 404. That way the URL routing doesn't change behaviour in the providers `renderWithProviders` mounts.

### Blast radius

- Only the two test files and the bible page above. No product code, no other suites.
- `renderWithProviders` providers still get a list-shaped response for unrecognised URLs, so there's no provider-side behaviour change.
- AST-1771 bible rows and manifest stay valid. The AST-1771 test is untouched, and `--testNamePattern="AST-1771"` still selects it.

### What must still hold

- AST-2059 product behaviour as shipped: content comes from the detail fetch; labels and order come from `rubricItems`, then the list fallback; "Loading rubric…" shows until the fetch settles; failure goes to the fallback text; `RubricModal` `loading` defaults to false.
- AST-1771: detail row order test unchanged and green.
- AST-1063 / AST-1327: no test asserts or introduces `content` on the job-carried `*_rubric` snapshot.
- Engineer test-tree ban: Ada does not edit `tests/` or `docs/test-bible/`. Betty lands this.


## Joan fix-board — AST-2060

**Verdict (for Chuckles to post)**

```
[board-joan]  CANON: OK
```

**Stdout**

```text
AST-2060 board-joan done — CANON: OK.
```

**Triage note (not for Linear):** Read `## Bug: AST-2060` on `origin/sub/AST-2058/AST-2060-show-rubric-tests`. Scope is **tests + `docs/test-bible/` only** (no `src/`). The plan realigns fixtures with post–AST-723 / AST-2059 production shapes (list unhydrated, detail hydrated), adds bug-repro + loading/failed-fetch coverage, and bible rows — without asserting `content` on job-carried `*_rubric` (AST-1063). That pins existing in-force behaviour (`astral.layers.import-direction`, detail hydration, Betty-owned test tree / engineer ban) rather than contradicting or extending any statute or pattern. Same shape as other gap siblings (e.g. AST-1328, AST-1911): no F3 canon landing.


## Radia review — AST-2060

```
[code-rubric]
**Ticket:** AST-2060
**Publish ref:** `1537b4b8bb491d65029163055680a01d259713c7` (`origin/sub/AST-2058/AST-2060-show-rubric-tests`)
**Diff base:** `origin/ftr/AST-2058-show-rubric-content...origin/sub/AST-2058/AST-2060-show-rubric-tests` (no `src/`; AST-2060-owned deltas in `test_AgentAnalysisHeader.test.tsx`, `test_RubricModal.test.tsx`, `docs/test-bible/frontend/components.md` + plan patch; `merge-tests` carries additional `origin/tests` commits)
**Corpus:** `6f3edaa90d`
**Overall:** CLEAN

## Fix-specific checks

- **[bug-repro] OK** — `test_AgentAnalysisHeader.test.tsx` (`// AST-2060 [bug-repro]:` + `it("AST-2059: show rubric reads content from hydrated candidate detail, not the list payload")`): `LIST` has empty `artifacts` (no list rubric); detail is a deferred promise; before resolve asserts `Loading rubric…` and absence of `No rubric found for this vector.`; after `resolveDetail(detailWith([… content: "Hydrated body" …]))` asserts `Hydrated body` and `mockedApi` called with `/api/candidates/c1`. That pins AST-2059 To-be (content only from hydrated detail), not a tautology. On pre-fix `06df211db` there is no detail fetch and no loading UI — modal would show the fallback immediately, so the loading gate and `Hydrated body` assertion would fail (matches plan § Repro / bible red-green note).
- **## What must still hold — OK** — AST-1771 order test untouched; fixtures do not put `content` on job-carried `rubricItems`; failed-fetch cases assert fallback not stuck on loading; `RubricModal` default-false `loading` case retained; delivery is tests+bible only (`code(AST-2060)` empty product commit on tip).

## Canon scores

*(Linear Description has no **Canon Scope (frozen at plan)** block. Scored Joan fix-board F2 overlap from issue doc § Joan fix-board — AST-2060.)*

| id | grade | effort | one-line |
| -- | -- | -- | -- |
| astral.layers.import-direction | A | | Tests document list-unhydrated vs detail-hydrated rubric content (UI → existing API) |
| astral.git.engineer-test-tree-ban | A | | No `src/`; AST-2060 test/bible commits + `merge-tests(AST-2060)` only |
| orch.roles.betty-owns-test-tree | A | | Gap delivery in `tests/` + `docs/test-bible/` per plan |

## Column diff vs plan stage

no plan-stage scores attached (Joan fix-board `CANON: OK`, not per-id validate-plan rubric)

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

1. **Canon Scope process gap (Archie)** — Same as AST-2059: no frozen canon id list on the bug ticket; overlap skim only.  
   **Default:** Ship; note for Archie without blocking.

### advisory

1. **sibling test carry (merge-tests):** `merge-tests(AST-2060)` includes non–AST-2060 suites (e.g. AST-2047/2048/2049 theme/color-guard, AST-2056/2057 bug-repros, `test_ArtifactEditor`, `test_AdminThemeExamples`, assorted bible rows) — expected `origin/tests` rollup; not AST-2060 product scope.
2. **Mock routing shape** — `mockApiRoutes` serves the list-shaped `{ ok: true, json }` response for every path except `/api/candidates/c1` (not only `path === "/api/candidates"`). Matches plan ⚠️ Decision (unknown URLs → list); slightly broader than the plan’s two-path table but intentional for `renderWithProviders`.
3. **`[bug-repro]` tag placement** — Tag is on the line comment above `it(...)`, not the first line inside the test body; sufficient for fix-lane machinery.

## What’s solid

- URL-routed `api` mock separates list vs detail; legacy header tests retargeted with `findByText`.
- Bug-repro embeds no-flash loading check via deferred detail (plan decision).
- Bible § AST-2060 + narrowed QA manifest align with the two component files.

## Recommended actions (Chuckles)

| Gate | Parent shape |
|------|----------------|
| **PROCEED** (C7 complete) | **Normal** mini-parent (`ftr/AST-2058-show-rubric-content`; AST-2059 on ftr) → **Review Posted** → §3h clean-review shortcut → **User Testing** (`resolve-child` skipped). |

Append artifact; commit `docs(AST-2060): Radia review — clean` on `origin/sub/AST-2058/AST-2060-show-rubric-tests`; post slim upshot `--as radia`.

context_tokens≈22000
```

```
[code-rubric] PROCEED (Commit: 1537b4b8b) Hydrated-detail rubric tests
```

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/dedb6627a33e68a75b16494f7070d79e/b49e980b-7194-43ab-bef1-a6187cd47744/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/31becfa8-298a-44e6-a12a-92b6e6ecc5c7/store.db` |
| Radia | review | `/home/susan/.cursor/chats/dedb6627a33e68a75b16494f7070d79e/8311cb55-4861-438f-abad-81b58015841a/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-2058 (parent) | ftr/AST-2058-show-rubric-content |
| AST-2059 | sub/AST-2058/AST-2059-show-rubric-content |
| AST-2060 | sub/AST-2058/AST-2060-show-rubric-tests |

**Epic worktree:** `astral-AST-2058/` — one active sub checked out at a time.
