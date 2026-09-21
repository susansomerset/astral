<!-- linear-archive: AST-1064 archived 2026-08-07 -->

## Linear archive (AST-1064)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1064/group-by-aligned-rubric-jobs-list-tables-issue-with-the-rubric-grade  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** Medium / —  
**Parent:** AST-1059 — Issue with the rubric grade displays on the Jobs List pages  
**Blocked by / blocks / related:** parent: AST-1059

### Description

## What this implements

Owns Skipped + In Review list rendering: drop live-rubric columns; group jobs by aligned job-carried rubric into separate tables with matching headers/tooltips; paint grade-dots from stored grades; paint Score from analysis-time job data. After AST-1063. Does **not** own hydration payload shape beyond consuming it; does not own Recommended phase-score UI.

## In scope

- [X] `astral.layers.ui-config-driven-business-logic` — section→gradeKey stays manifest/config; React paints API-resolved job-carried shapes (group/fingerprint presentation only).
- [X] `astral.layers.import-direction` — UI over API job fields (`*_rubric` / `*_grades` / `*_score`); no UI→data; no live-artifact invent of criteria.
- [X] `pattern.layers.import-discipline` — list tables consume job-carried hydration; do not invent rubric criteria from live candidate artifacts.
- [X] **New pattern:** job-list tables keyed by job-carried rubric fingerprint (Archie-approved on parent AST-1059).

## Considered but excluded

- [X] `astral.config.config-source-of-truth` — section→grade_field mapping already owned by State UI manifest / prior tickets; this plan does not edit config maps.
- [X] `astral.agent.grade-vector-validation` — write-path / grade acceptance is not this ticket (list display only).
- [X] `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` — helpers stay in existing `lib/rubricDisplay.ts` and `pages/Jobs*.tsx`; no new placement dispute.
- [X] API / core hydration (`consult.py`, `api_jobs.py`) — sibling AST-1063.
- [X] Recommended phase-score UI / meteorite GDL — out of boundaries.

## Acceptance criteria

- [X] 2. Jobs in the same section with **different** rubric shapes appear in **separate tables**, each with headers and tooltips matching that group’s rubric; grades fill those columns for every stored vector.
- [X] 3. Jobs sharing an aligned rubric share one table; every stored vector for the section grade field shows grade-dot + confidence (regression: the brief’s meteorite-somerset style rows show full grades, not mostly dashes).
- [X] 4. Score on those rows is the **analysis-time score from job data**, consistent with the grades shown for that analysis.
- [X] 5. In Review sections that use the same per-vector grade-dot pattern follow the same job-aligned / group-by-rubric rules.
- [X] 6. Happy path: a section of jobs that all share one rubric still renders one coherent table with correct grades and Score.

## Boundaries

* Does **not** own API/job hydration payload shape (sibling Ada / AST-1063).
* Does **not** re-grade jobs or update live candidate rubrics.
* Does **not** own Recommended phase-score UI or meteorite GDL.

## Notes for planning

Parent new-pattern flag: job-list tables keyed by job-carried rubric fingerprint.

Plan: `docs/features/interface/ast-1064-group-by-aligned-rubric-jobs-list-tables.md` on `origin/sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1059-rubric-grade-displays-jobs-list`, child `sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-30T01:54:06.716Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1064
**Publish ref:** `69240a7a9d4d1a7b18a174fad5126b4a79a1e6d5` (`origin/sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`)
**Overall:** DISCUSS

Three-dot: `origin/dev...origin/sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`. Diff layers: core, ui, docs (includes AST-1063 hydration + Betty tests on tip). This ticket’s product commit: `rubricDisplay.ts`, `JobsSkipped.tsx`, `JobsInReview.tsx`.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | no confidence change (AST-1063 on tip only) |
| astral.agent.do-task-delegation | scoped | conforms | no do_task change beyond prior AST-1063 snapshot |
| astral.agent.grade-vector-validation | scoped | conforms | list display only; no validation change |
| astral.batch.batch-id-first | scoped | conforms | no new batch APIs |
| astral.batch.batch-id-format | scoped | conforms | untouched |
| astral.batch.claim-process-release | scoped | conforms | no claim-loop change |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | untouched |
| astral.config.config-source-of-truth | scoped | conforms | gradeKey from manifest; no new config maps |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | applies_when.paths no match |
| astral.debug.spikes-under-debug-dir | scoped | conforms | no spike artifacts committed |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket (1063+1064 each) |
| astral.git.betty-no-src-or-features | scoped | conforms | frontend via code(); Betty merge-tests only tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | code(AST-1064) frontend only; tests via Betty merge-tests |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external; core only via prior AST-1063 |
| astral.layers.import-direction | scoped | conforms | frontend consumes job JSON; no UI→data |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | applies_when.layers no match |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | section→gradeKey config; paints job-carried shapes |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no verdict orchestration change this ticket |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new API routes |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer work |
| astral.standards.database-header-inventory | scoped | not-applicable | applies_when.layers no match |
| astral.standards.debug-contract-gated | scoped | conforms | UI-only; no ungated debug contract |
| astral.standards.dry-and-focused-functions | scoped | conforms | helpers once in rubricDisplay; both pages call |
| astral.standards.in-scope-only | scoped | conforms | frontend list only; Recommended/API out |
| astral.standards.logging-via-utils | scoped | conforms | no Python logging path |
| astral.standards.no-cross-contamination | scoped | conforms | stays in frontend UI (+ prior 1063 on tip) |
| astral.standards.no-hardcoded-sets | scoped | conforms | grades:/__empty__ presentation sentinels only |
| astral.standards.public-then-helpers | scoped | conforms | exported pure helpers in lib |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | applies_when.layers no match |
| astral.state.core-decides-transitions | scoped | conforms | no transition changes |
| astral.state.job-prior-states-enforced | scoped | conforms | untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | untouched |
| astral.ui.frontend-file-placement | scoped | conforms | lib/rubricDisplay.ts + existing pages/ |
| astral.ui.naming-conventions | scoped | conforms | PascalCase pages; camelCase helpers |
| astral.ui.single-gunicorn-worker | scoped | conforms | untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests(AST-1064) one SHA on tip |
| orch.git.commit-vocabulary | universal | conforms | code/docs/test/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | sub/AST-1059/AST-1064-… |
| orch.git.merge-on-checkout | universal | conforms | tip includes ftr/1063 lineage |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | ticket sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1059 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | fingerprint Decisions + Archie pattern |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–3 match frontend diff |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Interface child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty merge-tests after engineer code |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | assignee remains Katherine |
| orch.roles.pre-commit-path-bans | universal | conforms | role-split commits on tip |

## Pattern conformance

| id | verdict |
| -- | -- |
| pattern.layers.import-discipline | conforms — list tables consume job-carried hydration; no live-artifact invent |
| (via statutes) astral.layers.import-direction | conforms |
| (via statutes) astral.layers.ui-config-driven-business-logic | conforms |
| **New pattern:** job-list tables keyed by job-carried rubric fingerprint | conforms — Archie-approved on parent; `groupJobsByAlignedRubric` |

## Plan adherence

Stages 1–3 match: helpers + Skipped/In Review group-by tables; live `artifacts` column source removed; Score via `analysisTimeScoreForJob`. In Review always-on Score when `gradeKey` set (Joan plan discuss addressed). Self-Assessment Single-Component holds. Boundary vs AST-1063 / Recommended held in `code(AST-1064)`.

## Findings

### fix-now
(none)

### discuss
**straggler ×17** — Joan excluded these at plan time (UI-only Files Changed); three-dot vs `origin/dev` in-scope (AST-1063 + features + Betty tests). All score **conforms**:
- `astral.agent.confidence-bounds`
- `astral.agent.do-task-delegation`
- `astral.agent.grade-vector-validation`
- `astral.batch.batch-id-first`
- `astral.batch.batch-id-format`
- `astral.batch.claim-process-release`
- `astral.batch.entity-agent-responses-latest-only`
- `astral.config.pass-threshold-vs-score-floor`
- `astral.debug.spikes-under-debug-dir`
- `astral.docs.features-single-file-per-ticket`
- `astral.git.engineer-test-tree-ban`
- `astral.layers.core-vs-external-bright-line`
- `astral.patterns.coat-check-never-store-empty`
- `astral.patterns.render-verdict-orchestrates-consult`
- `astral.state.core-decides-transitions`
- `astral.state.job-prior-states-enforced`
- `astral.state.no-daisy-chain-in-run`

### advisory
(none)

## What’s solid
- Fingerprint / grades-fallback / `__empty__` grouping; columns from job-carried `*_rubric` (or grades).
- Prefer `{prefix}_score` then `latest_score`; floor section unchanged on Skipped.
- Composite sort keys per group table.

## Recommended actions
Acknowledge stragglers → resolve-child → User Testing (no product delta).

docs() on publish ref: `docs(AST-1064): Radia review — findings` @ `69240a7a`.

context_tokens≈48000

#### betty — 2026-07-30T01:51:10.775Z
1. `tests/component/frontend/lib/test_rubricDisplay.test.ts` — **AST-1064 job-carried list helpers** (key map / fingerprint / group / columns / `analysisTimeScoreForJob`)
2. `tests/component/frontend/pages/test_JobsSkipped.test.tsx` — **AST-1064 group-by job-carried rubric** (multi-table + happy-path single table; grades paint; phase score)
3. `tests/component/frontend/pages/test_JobsInReview.test.tsx` — **AST-1064 group-by job-carried rubric** (Passed Job List split by `joblist_rubric`)

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_rubricDisplay.test.ts \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx
```

**Broken / obsolete:** none.
**Integration:** none revised.

**Publish:** `origin/sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables` @ `bd51dbfa` (`merge-tests(AST-1064): origin/tests 5f8412a9`)

**Bible shasum on publish-ref:**
- `docs/test-bible/frontend/pages.md` `a3fab08ead2311e86c9a8e2c7edacfd7549d6c8a`
- `docs/test-bible/frontend/components.md` `60c882442e7b31b94ce3d77b1b57006d5d8a8d39`

#### joan — 2026-07-30T01:42:55.166Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1064
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 columns from job-carried hydrated rubric, not live artifact | Stages 1–2 — drop live `artifacts` / `buildJobListRubricColumns` for lists; columns via `buildJobListRubricColumnsForGroup` (payload shape owned by AST-1063) |
| AC2 different rubric shapes → separate tables + matching headers/tooltips + grades | Stage 1 `groupJobsByAlignedRubric` + Stage 2/3 one table per group |
| AC3 aligned rubric → one table; grade-dot + confidence per stored vector | Stages 1–3; preserves `gradeAndConfidenceForCol`; AC6 happy path explicit |
| AC4 Score = analysis-time job score | Stage 1 `analysisTimeScoreForJob`; Stages 2–3 Score cells/sort |
| AC5 In Review same rules | Stage 3 |
| AC6 single shared rubric → one coherent table | Stage 2 §4 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 rubricDisplay helpers | Purpose/Functional scope job-carried fingerprint + Score resolver; new pattern |
| Stage 2 JobsSkipped | Functional scope Skipped list grouping / grade-dots / Score |
| Stage 3 JobsInReview | Functional scope In Review same rules (AC5) |
| Stage 4 manual smoke | Builder verification of AC2–AC6; no Betty tests |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests in this UI plan |
| orch.git.commit-vocabulary | conforms | Sub publish path; no illegal commit types |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/…; merges from ftr/dev as prerequisite |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table sub/AST-1059/AST-1064-… |
| orch.git.merge-on-checkout | conforms | Prerequisite gate uses merge-on-checkout recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses authoritative sub ref only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1059 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Fingerprint/score Decisions explicit; Archie-approved pattern on parent |
| orch.pipeline.plan-is-bible | conforms | Binding Files Changed + stages + Decisions |
| orch.pipeline.project-scoped-queues | conforms | Single-child Interface scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible commits; Stage 4 builder smoke only |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.config.config-source-of-truth | conforms | gradeKey still from State UI manifest; no new config maps |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env introduced |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.import-direction | conforms | Frontend only; consumes job JSON; no UI→data |
| astral.layers.ui-config-driven-business-logic | conforms | section→gradeKey config/API; React paints job-carried shapes + Archie-approved fingerprint grouping |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new API routes |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work |
| astral.standards.debug-contract-gated | conforms | UI; no debug-contract requirement |
| astral.standards.dry-and-focused-functions | conforms | Helpers once in rubricDisplay; both pages call them |
| astral.standards.in-scope-only | conforms | Three frontend files; API/Recommended/re-grade excluded |
| astral.standards.logging-via-utils | conforms | No Python logging path |
| astral.standards.no-cross-contamination | conforms | Stays in frontend UI |
| astral.standards.no-hardcoded-sets | conforms | No product state enums; `grades:` / `__empty__` are presentation sentinels |
| astral.standards.public-then-helpers | conforms | Pure exported helpers in lib |
| astral.ui.frontend-file-placement | conforms | lib/rubricDisplay.ts + existing pages/ |
| astral.ui.naming-conventions | conforms | Existing PascalCase pages; camelCase helpers |
| astral.ui.single-gunicorn-worker | conforms | No worker/config changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.confidence-bounds — layers ∩ plan {ui} empty
- astral.agent.do-task-delegation — layers ∩ plan {ui} empty
- astral.agent.grade-vector-validation — layers ∩ plan {ui} empty
- astral.batch.batch-id-first — layers ∩ plan {ui} empty
- astral.batch.batch-id-format — layers ∩ plan {ui} empty
- astral.batch.claim-process-release — layers ∩ plan {ui} empty
- astral.batch.entity-agent-responses-latest-only — layers ∩ plan {ui} empty
- astral.config.pass-threshold-vs-score-floor — layers ∩ plan {ui} empty
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {ui} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.core-vs-external-bright-line — layers ∩ plan {ui} empty
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan {ui} empty
- astral.patterns.coat-check-never-store-empty — layers ∩ plan {ui} empty
- astral.patterns.render-verdict-orchestrates-consult — layers ∩ plan {ui} empty
- astral.standards.database-header-inventory — layers ∩ plan {ui} empty
- astral.standards.utils-data-late-import-only — layers ∩ plan {ui} empty
- astral.state.core-decides-transitions — layers ∩ plan {ui} empty
- astral.state.job-prior-states-enforced — layers ∩ plan {ui} empty
- astral.state.no-daisy-chain-in-run — layers ∩ plan {ui} empty

## Findings

None fix-now.

**discuss (non-blocking):** Stage 3 Score visibility — prefer per-group `some(score)` but keep always-on Score header when `sec.gradeKey` set and all scores null. Implementer should follow the always-on-when-gradeKey clause for In Review parity; not a definition conflict.

**acceptable:** Self-assessment Single-Component / high / Medium matches; Medium risk (fingerprint merge/split; `{prefix}_score` vs `latest_score`) mitigated by grades-fallback prefix and `latest_score` fallback. Fingerprint ignoring importance is an explicit Decision aligned with Archie-approved pattern.

**R6:** Definition fidelity pass (Skipped+In Review grouping only). Boundaries respected (no API/Recommended/re-grade). Layer/import pass. Config consume-only. File placement pass. DRY helpers in one lib. No sibling scope creep into AST-1063.

context_tokens≈55000

— Joan

#### chuckles — 2026-07-30T01:38:54.190Z
[thread-orphan] Joan session store relocated for validate-plan resume.

found: `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`
expected: `/home/susan/.cursor/chats/845cf1b3ae7cc5921673592f13d91e09/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`
UUID unchanged: `da0027e7-276d-4fe2-a6e6-65c8eb77e24d`

— Chuckles

#### katherine — 2026-07-30T01:38:31.286Z
Plan published for AST-1064 (group-by-aligned-rubric Jobs list tables).

**Plan doc:** https://github.com/susansomerset/astral/blob/sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables/docs/features/interface/ast-1064-group-by-aligned-rubric-jobs-list-tables.md

**origin tip:** `sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables` @ `15484c98`

**Approach:** Helpers in `rubricDisplay.ts` fingerprint job-carried `*_rubric` (grades-only fallback when snapshot absent), partition section jobs into aligned groups, build columns via `buildJobListRubricColumnsFromArtifact` / grades fallback — never live candidate artifacts. `JobsSkipped` + `JobsInReview` render one table per group; Score prefers `{prefix}_score` then `latest_score`.

**Self-assessment**
- **Scope:** Single-Component — frontend `rubricDisplay` + Skipped / In Review pages only; hydration stays on AST-1063.
- **Conf:** high — dash-sea root cause and AST-1063 payload contract are known; fingerprint + first-job columns are mechanical.
- **Risk:** Medium — bad fingerprint merges/splits tables; `{prefix}_score` preference could surprise if only `latest_score` was populated historically (fallback mitigates).

---

# Group-by-aligned-rubric Jobs list tables

**Linear:** [AST-1064](https://linear.app/astralcareermatch/issue/AST-1064/group-by-aligned-rubric-jobs-list-tables-issue-with-the-rubric-grade)  
**Parent:** [AST-1059 — Issue with the rubric grade displays on the Jobs List pages](https://linear.app/astralcareermatch/issue/AST-1059/issue-with-the-rubric-grade-displays-on-the-jobs-list-pages)  
**Publish ref (origin):** `sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`  
**Parent integration ref:** `ftr/AST-1059-rubric-grade-displays-jobs-list`  
**Blocked by:** [AST-1063](https://linear.app/astralcareermatch/issue/AST-1063/job-carried-rubric-hydration-for-list-columns-issue-with-the-rubric) (job-carried `*_rubric` + score flatten on list payloads — already on parent `ftr`)

On Skipped and In Review Jobs list pages, stop building grade columns from the **live** candidate rubric artifact. Within each state section that shows per-vector grade-dots, **group jobs by aligned job-carried rubric fingerprint**, render **one table per group** with headers/tooltips from that group’s hydration, paint grade-dots from stored grades under matching columns, and paint Score from **analysis-time job score** for that section’s grade field. Does **not** change API hydration shape, Recommended phase-score UI, re-grading, or live rubric edits.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`; `git merge origin/dev`; `git merge origin/ftr/AST-1059-rubric-grade-displays-jobs-list`; merge-clean (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).
2. Confirm list JSON already lifts `joblist_rubric` / `jd_rubric` / `get_rubric` / `do_rubric` / `like_rubric` via AST-1063 (`_flatten_grades` in `api_jobs.py`). Do **not** edit `consult.py` or `api_jobs.py` in this ticket.
3. Do **not** touch Recommended pages or meteorite GDL.

---

## Contract consumed (AST-1063 — do not re-implement)

| Section `gradeKey` (`JOBS_*_GRADE_FIELD` / manifest `grade_field_by_job_state`) | Job-carried rubric on job JSON | Analysis-time score key |
|---|---|---|
| `joblist_grades` | `joblist_rubric` | `joblist_score`, else `latest_score` |
| `jd_grades` | `jd_rubric` | `jd_score`, else `latest_score` |
| `get_grades` | `get_rubric` | `get_score`, else `latest_score` |
| `do_grades` | `do_rubric` | `do_score`, else `latest_score` |
| `like_grades` | `like_rubric` | `like_score`, else `latest_score` |

Convention: `gradeKey.replace("_grades", "_rubric")` / `"_score"`. Each `*_rubric` is a list of `{ code, label, importance, grade_descriptions }` (no `content`). Absent/empty `*_rubric` = pre-snapshot job → **grades-only fallback** defined below.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/rubricDisplay.ts` | Job-carried key helpers; rubric fingerprint; group-by-aligned; column build preferring job-carried over live artifact; analysis-time score resolver | ui (frontend lib) |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Per-section group → multiple tables; drop live-artifact column source; Score from analysis-time field | ui |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | Same grouping / column / Score rules as Skipped (grade-dot sections) | ui |

**Out of scope:** `src/core/consult.py`, `src/ui/api/api_jobs.py`, Recommended pages, `JobAnalysisReportModal`, candidate artifact editors, `tests/` / bible (Betty), backfill of historical `*_rubric`.

---

## Stage 1: Job-carried helpers in `rubricDisplay.ts`

**Done when:** Pure helpers (no React) can (a) map `gradeKey` → rubric/score keys, (b) fingerprint a job’s aligned rubric shape, (c) partition a job list into ordered groups, (d) build `JobListRubricColumn[]` from a group’s job-carried rubric (or grades-only fallback), and (e) resolve display score for a row — without reading `candidate_data.artifacts`.

1. Add:

   ```ts
   export function jobCarriedRubricKey(gradeKey: string): string {
     return gradeKey.replace(/_grades$/, "_rubric")
   }

   export function jobCarriedScoreKey(gradeKey: string): string {
     return gradeKey.replace(/_grades$/, "_score")
   }
   ```

   If `gradeKey` is empty or does not end with `_grades`, return `""` (callers skip rubric grouping).

2. Add fingerprint of **aligned shape** (same criteria identity → same table; order of criteria in the snapshot must not split groups):

   ```ts
   export function jobListRubricFingerprint(
     rubricItems: Array<{ code?: string; label?: string }> | null | undefined,
   ): string
   ```

   - Empty / non-array → `""`.
   - For each item, identity token = `normalizeRubricVectorKey(label || code || "")` plus `|` plus `(code || "").trim().toUpperCase()`.
   - Drop empty tokens; **sort** tokens ascending; join with `\0`.
   - Do **not** include importance or `grade_descriptions` in the fingerprint (display-only).

3. Add grades-only fallback fingerprint when `*_rubric` is missing/empty but grades exist:

   ```ts
   export function jobListRubricFingerprintFromGrades(
     grades: unknown,
   ): string
   ```

   - Array of `{ vector }`: tokens = `normalizeRubricVectorKey(vector)` for each; sort; join `\0`.
   - Object map: tokens = normalized keys; sort; join.
   - Else `""`.

4. Add grouping:

   ```ts
   export type JobListRubricGroup<T extends Record<string, unknown> = Record<string, unknown>> = {
     fingerprint: string
     jobs: T[]
     /** First job in group used as column source (stable: first encounter order). */
     columnSourceJob: T
   }

   export function groupJobsByAlignedRubric<T extends Record<string, unknown>>(
     jobs: T[],
     gradeKey: string,
   ): JobListRubricGroup<T>[]
   ```

   Per job:
   - `rubricKey = jobCarriedRubricKey(gradeKey)`.
   - If `job[rubricKey]` is a non-empty array → fingerprint via `jobListRubricFingerprint`.
   - Else if grades at `job[gradeKey]` yield a non-empty grades fingerprint → use `"grades:" + that` (prefix so it never collides with a real rubric fp).
   - Else fingerprint `"__empty__"` (jobs with neither rubric nor grades share one no-column / dash table).
   - Emit groups in **first-seen fingerprint order**; append jobs to matching group preserving relative order within the group.

⚠️ **Decision:** Fingerprint ignores importance / descriptions so two jobs with the same criteria labels/codes but different importance metadata still share a table; column headers come from the **first** job’s rubric snapshot (importance-sorted via existing `buildJobListRubricColumnsFromArtifact`).

5. Add column builder that **never** reads live artifacts:

   ```ts
   export function buildJobListRubricColumnsForGroup(opts: {
     gradeKey: string
     columnSourceJob: Record<string, unknown>
   }): JobListRubricColumn[]
   ```

   - `items = columnSourceJob[jobCarriedRubricKey(gradeKey)]`.
   - If non-empty array → `buildJobListRubricColumnsFromArtifact(items)` (existing importance sort + tooltips + grade_descriptions).
   - Else → `buildJobListRubricColumnsFromJobGrades(gradeKey, [columnSourceJob])` (existing path).
   - Do **not** call `buildJobListRubricColumns` with `artifacts` / `rubricArtifactKey` from this helper.

6. Deprecate live-artifact preference for list pages only — leave `buildJobListRubricColumns` intact for any other callers (`JobAnalysisReportModal`, tests). Add a one-line comment above `buildJobListRubricColumns`: list Skipped/In Review must use `buildJobListRubricColumnsForGroup` (AST-1064); live artifact path remains for non-list consumers until separately migrated.

7. Add score resolver:

   ```ts
   export function analysisTimeScoreForJob(
     job: Record<string, unknown>,
     gradeKey: string,
   ): number | null
   ```

   - If `gradeKey` empty → return `typeof job.latest_score === "number" ? job.latest_score : null` (floor section).
   - Else read `job[jobCarriedScoreKey(gradeKey)]`; if number, return it.
   - Else if `typeof job.latest_score === "number"`, return it.
   - Else `null`.

⚠️ **Decision:** Prefer `{prefix}_score` over `latest_score` so JD / get / do / like sections show the score from the same analysis epoch as the grades, not a later phase’s `latest_score`.

---

## Stage 2: `JobsSkipped.tsx` — group-by tables + Score

**Done when:** Each non-floor section with a `gradeKey` renders **N** `list-page-table` blocks (N = number of aligned-rubric groups). Headers/tooltips come from job-carried rubric (or grades fallback). Grade-dots match stored vectors (meteorite-somerset style rows fill cells, not dashes, when grades+rubric align). Score cells use `analysisTimeScoreForJob`. Floor / below-dispatch section unchanged (no grade columns; still uses `latest_score` / floor columns). Live `candidates[].candidate_data.artifacts` is **not** used for column build.

1. Remove `artifacts` `useMemo` and stop importing/using `buildJobListRubricColumns` with `manifest.jobs.grade_rubric_by_field`. Import `groupJobsByAlignedRubric`, `buildJobListRubricColumnsForGroup`, `analysisTimeScoreForJob` from `rubricDisplay`.

2. Keep existing section construction (`virtual_skip` floor, state sections, legacy unmapped) unchanged.

3. Inside each expanded **non-floor** section with `sec.gradeKey`:
   - `const groups = groupJobsByAlignedRubric(sec.jobs as …, sec.gradeKey)`.
   - For each group, build `cols = buildJobListRubricColumnsForGroup({ gradeKey: sec.gradeKey, columnSourceJob: group.columnSourceJob })`.
   - Sort key for this table: `${sec.state}::${group.fingerprint}` (update `sorts` / `handleSort` / `sortIndicator` to take that composite key so tables sort independently).
   - Render **one** `<div className="list-page-table-wrap"><table>…</table></div>` per group (same column structure as today: Actions, checkbox, title, company, rubric cols, Score if any row has score, Failed At).
   - `showScore` per group: `group.jobs.some(j => analysisTimeScoreForJob(j, sec.gradeKey) != null)`.
   - Score cell / sort comparator: use `analysisTimeScoreForJob` instead of raw `job.latest_score` for grade-dot tables. Keep floor section on `latest_score` / `dispatch_score_floor` as today.

4. Happy path: all jobs same fingerprint → still **one** table under the section (AC6).

5. Preserve `gradeAndConfidenceForCol` / confidence bullets / row actions behavior — only change which `cols` and which job subset feed each table.

6. Do **not** change bulk retry, expand policy (still one expand control per `sec.state` wrapping all group tables), or JobDetailModal.

---

## Stage 3: `JobsInReview.tsx` — same rules

**Done when:** In Review sections that use `gradeKey` follow the same group-by-aligned-rubric + job-carried columns + `analysisTimeScoreForJob` rules as Skipped. Sections without `gradeKey` stay a single table with no rubric columns.

1. Mirror Stage 2 changes: drop live-artifact `getRubricCols`; use `groupJobsByAlignedRubric` + `buildJobListRubricColumnsForGroup`; composite sort keys; Score via `analysisTimeScoreForJob`.
2. Keep `showScore = Boolean(sec.gradeKey)` at section level **or** per-group `group.jobs.some(… score …)` — prefer per-group so a grades-less subgroup does not force an empty Score column; if `sec.gradeKey` is set but all scores null, still show Score header with em-dashes (match current In Review always-on Score when gradeKey set).
3. Do not add Actions/checkbox columns that In Review does not already have.

---

## Stage 4: Manual smoke (builder)

**Done when:** Local UI against a candidate with (a) two jobs sharing one `joblist_rubric` and (b) one job with a different `joblist_rubric` shape shows **two** tables in that Skipped section with distinct header codes; grades paint under matching headers; Score matches `{prefix}_score` / `latest_score` fallback. A job with grades but no `*_rubric` still gets a grades-fallback table (headers from vector names). Changing live candidate artifact without re-grade does **not** change headers.

1. Use existing fixture / local DB jobs if available; otherwise seed via temporary `debug/spikes/` script (gitignored) that does not land in the commit.
2. Do not commit tests (Betty).

---

## Self-Assessment

**Scope:** `Single-Component` — frontend list lib + Skipped / In Review pages only; API/core already delivered by AST-1063.

**Conf:** `high` — AST-1063 contract and current dash-sea root cause (`buildJobListRubricColumns` + live artifact) are known; grouping is a new pattern but fingerprint + first-job columns are mechanical.

**Risk:** `Medium` — wrong fingerprint splits or merges tables incorrectly; preferring `{prefix}_score` over `latest_score` could surprise if a section’s `latest_score` was the only populated field historically (mitigated by fallback to `latest_score`).

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** Fingerprint / group / column / score helpers live once in `rubricDisplay.ts`; both pages call them — no copy-pasted fingerprint logic.
- **§2.1 config:** Section → `gradeKey` still from State UI manifest (`grade_field_by_job_state`); this ticket does not invent grade-field maps in React. Column *content* comes from job payload, not live artifacts.
- **§2.4 / §2.6:** N/A — no batch or state-machine changes.
- **§3.2 ui-config-driven:** Grouping is presentation of already-resolved job shapes from the API; no new business rules inventing rubric criteria client-side beyond the Archie-approved job-carried fingerprint pattern.
- **§3.3 import-direction:** Frontend only; no UI→data. Does not call consult or invent hydration.
- **§3.5 naming / file placement:** Helpers stay in `lib/rubricDisplay.ts`; pages stay under `pages/`.
- **New pattern:** job-list tables keyed by job-carried rubric fingerprint (parent Architectural definition — Archie-approved).

---

## Review (build)

**Built:** `origin/sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables` @ `707be3e69cf1bb637675eb7451c06779ae514a4a`

Stages 1–3: `jobCarriedRubricKey` / fingerprint / `groupJobsByAlignedRubric` / `buildJobListRubricColumnsForGroup` / `analysisTimeScoreForJob` in `rubricDisplay.ts`; Skipped + In Review render one table per aligned group; live candidate artifacts no longer drive list columns; Score prefers `{prefix}_score` then `latest_score`. In Review Score header always-on when `gradeKey` set (Joan discuss). Stage 4 smoke: deferred to UAT / Betty. Tests deferred to Betty.

## Radia review (code-rubric.v1)

**Date:** 2026-07-30  
**Publish tip before this docs commit:** `bd51dbfac475c4e73e202caf2923bc348cb69655`  
**Overall:** DISCUSS — **fix-now:** none; **discuss:** statute straggler ×17 (substance **conforms**; tip includes AST-1063 + Betty tests vs Joan UI-only exclusion set); no advisory.

### What’s solid
- Dropped live-artifact column source on Skipped + In Review; `groupJobsByAlignedRubric` + `buildJobListRubricColumnsForGroup` + `analysisTimeScoreForJob`.
- In Review Score header always-on when `gradeKey` set (addresses Joan plan discuss).
- Boundaries vs AST-1063 / Recommended held in this ticket’s `code(AST-1064)` commit.

### Issues
- **discuss (straggler ×17):** Joan excluded core/batch/docs/test-tree statutes at plan time (UI-only Files Changed); three-dot vs `origin/dev` brings AST-1063 + features + Betty tests in-scope — all score **conforms**.

### Recommended actions
- Acknowledge stragglers → resolve-child → User Testing (no product delta).

---

## Resolution

**Date:** 2026-07-30  
**Publish tip before resolve:** `69240a7a` (`docs(AST-1064): Radia review — findings` on `origin/sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`)

| Finding | Action |
| -- | -- |
| fix-now | none |
| discuss — statute stragglers ×17 (all conforms) | **No action** — informational plan-vs-diff predicate drift only (AST-1063 + Betty tests on tip). |

No product code changes in resolve. Proceeding to User Testing after §9a dry-run.

---

## Resolution

**Date:** 2026-07-30  
**Publish tip before resolve:** `69240a7a` (`docs(AST-1064): Radia review — findings` on `origin/sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`)

| Finding | Action |
| -- | -- |
| fix-now | none |
| discuss — statute stragglers ×17 (all conforms) | **No action** — informational plan-vs-diff predicate drift only (AST-1063 + Betty tests on tip vs Joan UI-only exclusion set). |

No product code changes in resolve. Proceeding to User Testing after §9a dry-run.
