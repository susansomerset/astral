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

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/19c5d0fc90a5e3a503adcd6a92005fd7/4d75d419-105f-4e0c-bd76-2b389e6f710d/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/d6893c63-fc40-4352-a9a7-15be56caf78c/store.db` |
| Radia | review | `/home/susan/.cursor/chats/19c5d0fc90a5e3a503adcd6a92005fd7/093a70ee-4637-48ee-9cbe-3cdb5781a809/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1321 (parent) | ftr/AST-1321-missing-vector-grades-rubric-headers |
| AST-1327 | sub/AST-1321/AST-1327-fix-missing-vector-grades-headers |
| AST-1328 | sub/AST-1321/AST-1328-gap-analysis-header-tests |

**Epic worktree:** `astral-AST-1321/` — one active sub checked out at a time.
