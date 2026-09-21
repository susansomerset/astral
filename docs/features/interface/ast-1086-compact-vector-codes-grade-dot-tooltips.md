<!-- linear-archive: AST-1086 archived 2026-08-07 -->

## Linear archive (AST-1086)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1086/compact-vector-codes-and-grade-dot-tooltips-on-job-lists-small-bug  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1078 — Small bug: Headers for Job Lists  
**Blocked by / blocks / related:** parent: AST-1078

### Description

## What this implements

One UI slice: shared job-list rubric column builder always emits compact `headerCode` (including grades-only fallback); Skipped / In Review render that compact code in the header cell with the full-name tooltip; grade-dot hover includes rubric text plus parenthetical confidence. Does **not** own rubric snapshot writes, grouping, or Recommended phase-score layout.

## In scope

- [X] `astral.standards.dry-and-focused-functions` — fix shared `rubricDisplay` builder + tooltip helper once
- [X] `astral.ui.frontend-file-placement` — `src/lib/rubricDisplay.ts` + existing Jobs list pages only
- [X] `astral.standards.in-scope-only` — header/grade-dot display surfaces on Skipped / In Review only

## Considered but excluded

* `astral.layers.ui-config-driven-business-logic` — confidence **numbers** still come from job payload; description strings are a deliberate frontend mirror of `CONFIDENCE_DESCRIPTIONS` (no API expansion in this ticket)
* Recommended phase-score / `recommendedJobReport.tsx` — parent Boundaries
* Rubric snapshot writes / grouping (`groupJobsByAlignedRubric`, `api_jobs`) — owned by AST-1063/1064
* `ConfidenceBullets` glyph redesign — out of Boundaries

## Acceptance criteria

1. [x] On Skipped and In Review Jobs list sections that show per-vector grade columns, each grade `<th>` visible text is a two-letter (or short) vector **code**, not the full vector label.
2. [x] Hovering that `<th>` shows a tooltip with the full vector name (label; importance retained per AST-437).
3. [x] For a group whose jobs only have grades (no job-carried `*_rubric`), headers are still compact codes — e.g. a vector like `Technical (TE)` does **not** appear as the full string in the header cell.
4. [x] Skipped and In Review both show compact codes in the header cell (no page still rendering the long label while the other shows the code).
5. [x] Grade dots still align under the correct columns; sorting by a grade column still works.
6. [x] Hovering a grade-dot on Skipped and In Review shows rubric criterion text for that letter (reason when present, else grade description) **and** a parenthetical confidence description when confidence is present on the cell.

## Boundaries

Does **not** own rubric snapshot writes, grouping, or Recommended phase-score layout. Does **not** redesign ConfidenceBullets glyphs beyond grade-dot hover text.

## Notes for planning

Compact headers + grade-dot tooltips are one display contract on Skipped / In Review.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1078-headers-for-job-lists`, child `sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-31T00:35:58.169Z
[publish-ref] rebuilt clean tip on `origin/ftr/AST-1078-headers-for-job-lists` — removed `Merge remote-tracking branch` subjects. Force-with-lease on `sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips` → `af563eaa`. `validate-sub-log` ok. Status unchanged (User Testing / Katherine).

— Katherine

#### chuckles — 2026-07-31T00:34:41.923Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log.sh` failed on `origin/sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips` (tip `b5888213`). Offending subjects in ftr..sub range:
- `b91f64a4` Merge remote-tracking branch 'origin/sub/…'
- `d88de206` Merge remote-tracking branch 'origin/dev' into sub/…

@Katherine Johnson — republish a clean sub tip stacked on `origin/ftr/AST-1078-headers-for-job-lists` (no `Merge remote-tracking branch` subjects). Keep plan/code/merge-tests/test/docs/resolve sequence for AST-1086. Chuckles will re-run merge-child after.

— Chuckles

#### radia — 2026-07-31T00:32:15.886Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1086
**Publish ref:** a87ef7e96c9a13546ee13eb591b716c645a1b720 (`origin/sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | layers {core,utils} ∩ diff {docs,ui} empty |
| astral.agent.do-task-delegation | scoped | not-applicable | layers {core} ∩ diff {docs,ui} empty |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers {core} ∩ diff {docs,ui} empty |
| astral.batch.batch-id-first | scoped | not-applicable | layers {data,core} ∩ diff {docs,ui} empty |
| astral.batch.batch-id-format | scoped | not-applicable | layers {core,data} ∩ diff {docs,ui} empty |
| astral.batch.claim-process-release | scoped | not-applicable | layers {core,data} ∩ diff {docs,ui} empty |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers {core,data} ∩ diff {docs,ui} empty |
| astral.config.config-source-of-truth | scoped | conforms | CONFIDENCE_DESCRIPTIONS frontend mirror matches config.py strings |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | layers {core,data,utils} ∩ diff {docs,ui} empty |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env introduced |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths artifacts/** / scripts/spikes/** miss diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plan file (not spike notes); see straggler |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single plan at docs/features/interface/ast-1086-…; see straggler |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test/bible commits; engineer owns src + features plan |
| astral.git.engineer-test-tree-ban | scoped | conforms | code(AST-1086) touches src only; tests via Betty |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers {core,external} ∩ diff {docs,ui} empty |
| astral.layers.import-direction | scoped | conforms | frontend lib + pages only; no core/data/external imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers {scripts} ∩ diff {docs,ui} empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | codes/labels/confidence numbers from job payload; description mirror per plan Decision |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers {core} ∩ diff {docs,ui} empty |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers {core} ∩ diff {docs,ui} empty |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new API routes |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer work |
| astral.standards.database-header-inventory | scoped | not-applicable | layers {data} ∩ diff {docs,ui} empty |
| astral.standards.debug-contract-gated | scoped | conforms | no backend debug path changes |
| astral.standards.dry-and-focused-functions | scoped | conforms | shared rubricDisplay builder + tooltip; Skipped converges on headerCode |
| astral.standards.in-scope-only | scoped | conforms | lib + JobsSkipped/JobsInReview only; Recommended/grouping/API untouched |
| astral.standards.logging-via-utils | scoped | conforms | no Python logging path |
| astral.standards.no-cross-contamination | scoped | conforms | stays in frontend UI |
| astral.standards.no-hardcoded-sets | scoped | conforms | confidence copy is byte-identical config mirror, not new vocabulary |
| astral.standards.public-then-helpers | scoped | conforms | parseGradesVectorName / confidenceDescription next to existing helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers {utils} ∩ diff {docs,ui} empty |
| astral.state.core-decides-transitions | scoped | not-applicable | layers {core,data} ∩ diff {docs,ui} empty |
| astral.state.job-prior-states-enforced | scoped | not-applicable | layers {core,data,utils} ∩ diff {docs,ui} empty |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers {core} ∩ diff {docs,ui} empty |
| astral.ui.frontend-file-placement | scoped | conforms | src/lib/rubricDisplay.ts + existing Jobs pages |
| astral.ui.naming-conventions | scoped | conforms | existing page/lib names unchanged |
| astral.ui.single-gunicorn-worker | scoped | conforms | no gunicorn/worker changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests(AST-1086) one-SHA merge from origin/tests |
| orch.git.commit-vocabulary | universal | conforms | code/test/docs/merge-tests vocabulary on sub publish |
| orch.git.flow-direction-inviolable | universal | conforms | publish to origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | sub/AST-1078/AST-1086-… matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | tip includes merge origin/dev |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force in range |
| orch.git.no-dev-agent-branches | universal | conforms | sub/AST-1078/… only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1078 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | confidence-mirror Decision already in plan; no new product ask |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–3 match shipped src |
| orch.pipeline.project-scoped-queues | universal | conforms | single Interface child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | review-child from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/ + bible from Betty |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee through review |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer avoided tests/; Radia docs-only |

## Pattern conformance

none cited

## Plan adherence

Diff matches plan Stages 1–3: grades-only `parseGradesVectorName` + `resolveRubricHeaderCode`, Skipped `{c.headerCode}`, grade-dot confidence parenthetical on both pages. Self-Assessment Single-Component / Conf high / Risk Medium still matches the footprint. Boundaries held (no Recommended, grouping, API, ConfidenceBullets glyph). Joan plan-rubric APPROVED attached.

## Findings

**discuss (straggler):** `astral.debug.spikes-under-debug-dir` and `astral.docs.features-single-file-per-ticket` were Joan-excluded (plan layers `{ui}`) but three-dot diff adds `docs/features/interface/ast-1086-….md`, so both score in-scope. Each **conforms** (normal single plan file, not spike notes). No product fix — C4 belt-and-suspenders only.

**advisory:** Tip also carries unrelated Betty sibling test/bible paths (AST-1080/81/82/84) via merge-tests / origin/tests not yet on `origin/dev`. Outside AST-1086 product scope; not a fix-now.

## What’s solid

Compact header + confidence tooltip contract lands in the shared helper once; Skipped/In Review consistent; config mirror verified byte-identical.

context_tokens≈28000

— Radia

#### betty — 2026-07-31T00:25:01.167Z
## QA test manifest

**origin/sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips** @ `b54bdb6f` (`merge-tests(AST-1086): origin/tests c7b214a878a886f24afe2c852e83a296c3b06c32`)

### Classification

1. **Existing coverage (bible-backed, still run):** `test_JobsSkipped.test.tsx` / `test_JobsInReview.test.tsx` Expand One + AST-1064 group-by; prior compact-header clicks (`TE` / `JL` / `JD`).
2. **Broken / obsolete (revised this pass):** `test_rubricDisplay.test.ts` grades-only fallback expected `headerCode === "Technical (TE)"` → now `"TE"` + tooltip `"Technical (5)"`.
3. **Gaps (added):** lib coverage for `parseGradesVectorName` / `CONFIDENCE_DESCRIPTIONS` / `formatGradeDotTooltip` confidence parenthetical; §6c page cases for compact `<th>` title + grade-dot tooltip on Skipped and In Review.

### Manifest

1. `tests/component/frontend/lib/test_rubricDisplay.test.ts` — **AST-1086 compact headers and grade-dot confidence tooltips** (+ revised AST-1064 grades-only expectation)
2. `tests/component/frontend/pages/test_JobsSkipped.test.tsx` — **AST-1086 compact headers and grade-dot tooltips** (§6c)
3. `tests/component/frontend/pages/test_JobsInReview.test.tsx` — **AST-1086 compact headers and grade-dot tooltips** (§6c)

### Run

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_rubricDisplay.test.ts \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx
```

### Bible (on publish tip)

- `docs/test-bible/frontend/lib.md` sha1 `11780357d7ea0dc5d2c8301c261ee397cfbc690c`
- `docs/test-bible/frontend/pages.md` sha1 `b637e63674f0a988c0d2a7226398079d327523c4`

**Integration:** none revised.

— Betty

#### joan — 2026-07-31T00:18:59.840Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1086
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 compact code in grade `<th>` on Skipped/In Review | Stages 1–2 (`headerCode` builder + Skipped paint) |
| AC2 `<th>` tooltip full vector name (+ importance) | Stage 1 `headerTooltip` / `formatRubricColumnTooltip`; pages keep `title={c.headerTooltip}` |
| AC3 grades-only still compact (e.g. `Technical (TE)` → `TE`) | Stage 1 parse helper + `buildJobListRubricColumnsFromJobGrades` rewrite |
| AC4 Skipped and In Review consistent | Stage 2 Skipped → `headerCode` (In Review already) |
| AC5 grade dots align; sort still works | Stage 2 keeps `key`/`handleSort` on `c.code` |
| AC6 grade-dot hover rubric text + confidence parenthetical | Stage 3 `formatGradeDotTooltip` + both pages pass confidence |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 grades-only compact headers | Purpose compact codes; Functional scope grades-only fallback; AC1/AC3 |
| Stage 2 Skipped `headerCode` | Functional scope Skipped/In Review consistency; AC4 |
| Stage 3 grade-dot + confidence | Purpose/Functional scope grade-dot hover + parenthetical confidence; AC6 |
| Stage 4 engineer verify (no tests/) | Build hygiene; Betty owns test updates listed in Files Changed |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests recipe in this plan |
| orch.git.commit-vocabulary | conforms | Sub publish path; no illegal commit types |
| orch.git.flow-direction-inviolable | conforms | Publish to origin/sub only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table `sub/AST-1078/AST-1086-…` |
| orch.git.merge-on-checkout | conforms | Prerequisite gate merges origin/dev + ftr before build |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1078/… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1078 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Explicit Decision on CONFIDENCE_DESCRIPTIONS mirror (no product ambiguity) |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed + Decisions |
| orch.pipeline.project-scoped-queues | conforms | Single-child Interface scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | Tests listed for Betty; Stage 4 bans engineer tests/ commits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Katherine engineer path after approve |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer owns build through resolve |
| orch.roles.pre-commit-path-bans | conforms | Engineer avoids tests/; Betty path noted |
| astral.config.config-source-of-truth | conforms | Confidence copy mirrors config.py strings; no invented vocabulary |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env introduced |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty owns tests only |
| astral.git.engineer-test-tree-ban | conforms | Stage 4: engineer does not commit under tests/ |
| astral.layers.import-direction | conforms | Frontend lib + pages only; no core/data imports |
| astral.layers.ui-config-driven-business-logic | conforms | Codes/labels/confidence numbers from payload; description mirror is documented Decision (ticket excluded API expansion) |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new API routes |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work |
| astral.standards.debug-contract-gated | conforms | No backend debug path changes |
| astral.standards.dry-and-focused-functions | conforms | Shared `rubricDisplay` builder + tooltip once; Skipped converges on In Review |
| astral.standards.in-scope-only | conforms | Skipped/In Review + lib only; Recommended/grouping/API excluded |
| astral.standards.logging-via-utils | conforms | No Python logging path |
| astral.standards.no-cross-contamination | conforms | Stays in frontend UI |
| astral.standards.no-hardcoded-sets | conforms | CONFIDENCE_DESCRIPTIONS is byte-identical config mirror, not a new set |
| astral.standards.public-then-helpers | conforms | Helper next to existing normalize/resolve helpers |
| astral.ui.frontend-file-placement | conforms | `src/lib/rubricDisplay.ts` + existing Jobs pages; no new subdirs |
| astral.ui.naming-conventions | conforms | Existing PascalCase pages / lib names unchanged |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

**Notes:** Layer cells `ui (frontend lib)` / `ui (Betty)` normalized to `ui` for matching.

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.git.engineer-test-tree-ban, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

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

**discuss (non-blocking):** Stage 3 mirrors `CONFIDENCE_DESCRIPTIONS` in frontend lib instead of API. Matches child “Considered but excluded” and explicit Decision; parent Architecture wants no new hardcoded *vector name* sets — confidence copy is config-string mirror. Separate ticket if Archie wants single API source later.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium is honest; Medium risk scoped to grades-only parse with concrete Done-when checks.

**R6:** Definition fidelity pass (single child owns all parent AC). Boundaries respected. DRY shared helper. File placement pass. No API/core/state-machine creep.

context_tokens≈48000

— Joan

#### katherine — 2026-07-31T00:16:38.891Z
Plan: [`docs/features/interface/ast-1086-compact-vector-codes-grade-dot-tooltips.md`](https://github.com/susansomerset/astral/blob/sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips/docs/features/interface/ast-1086-compact-vector-codes-grade-dot-tooltips.md) on `origin/sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips` @ `17a39663`.

**Scope:** Single-Component — `rubricDisplay.ts` + JobsSkipped / JobsInReview only.
**Conf:** high — Skipped still paints `c.code` while In Review uses `headerCode`; grades-only path sets `headerCode` to the raw `Technical (TE)` vector; grade-dot tooltip omits confidence parenthetical.
**Risk:** Medium — grades-only parse mistakes could mis-label headers or weaken column match for pre-snapshot jobs.

⚠️ Decision in plan: mirror `CONFIDENCE_DESCRIPTIONS` in the frontend lib (exact `config.py` strings) rather than expand state-ui API.

#### chuckles — 2026-07-31T00:13:04.997Z
[thread-missing] Cursor chat `02f904a9-f50e-47f0-9459-b08b0c1e7ed0` has no local `store.db` on **chuckles** (expected under epic hash; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `3a96093d-30b6-45bf-93e6-190c0dae9a78` (Katherine · engineer). Betty → `e7d725cb-da4c-4747-871f-7a4a849f7455`; Radia → `f8658bda-ea58-433c-8041-1c20336d09c9`.

— Chuckles

---

# Compact vector codes and grade-dot tooltips on job lists

**Linear:** [AST-1086](https://linear.app/astralcareermatch/issue/AST-1086/compact-vector-codes-and-grade-dot-tooltips-on-job-lists-small-bug)  
**Parent:** [AST-1078 — Small bug: Headers for Job Lists](https://linear.app/astralcareermatch/issue/AST-1078/small-bug-headers-for-job-lists)  
**Publish ref (origin):** `sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips`  
**Parent integration ref:** `ftr/AST-1078-headers-for-job-lists`  
**Blocked by:** none

Restore the AST-437 compact header contract on Skipped / In Review after AST-1059 hydration: grade `<th>` visible text is always a short vector **code** (with full name on `title` tooltip), including grades-only groups whose vectors look like `Technical (TE)`. Extend grade-dot hover text so rubric criterion text is followed by a parenthetical confidence description when confidence is present. Does **not** touch rubric snapshot writes, grouping, Recommended phase-score layout, or ConfidenceBullets glyph rendering.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips`; `git merge origin/dev`; `git merge origin/ftr/AST-1078-headers-for-job-lists`; merge-clean (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).
2. Confirm current drift (do not “fix” by guessing):
   - `JobsInReview.tsx` already paints `{c.headerCode}` in grade `<th>`; `JobsSkipped.tsx` still paints `{c.code}`.
   - `buildJobListRubricColumnsFromJobGrades` sets `headerCode` to the raw vector / key (so `Technical (TE)` appears as the cell text).
   - `formatGradeDotTooltip` returns reason or `gradeDescriptions[letter]` only — no confidence parenthetical.
3. Do **not** edit `consult.py`, `api_jobs.py`, Recommended pages, or `ConfidenceBullets.tsx` glyph markup.

---

## Contract (AST-437 + this ticket)

| Surface | Visible `<th>` | `<th title>` | Grade-dot `title` |
|---------|----------------|--------------|-------------------|
| Artifact / job-carried `*_rubric` columns | `headerCode` (= vector `code`, else first two letters) | `Label (importance)` via `formatRubricColumnTooltip` | Rubric text (reason else grade description) **+** ` (confidence description)` when confidence 1–5 present |
| Grades-only fallback | Compact code extracted from `Name (XX)` → `XX`; bare short labels (e.g. `Fit`) stay as today | Tooltip uses **stripped** human label + default importance — never `Technical (TE) (5)` | Same grade-dot rule |

Identity / sort keys must keep matching grades under the correct columns (`gradeAndConfidenceForCol` already normalizes `Name (XX)` vs code/label).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/rubricDisplay.ts` | Grades-only compact `headerCode` / clean label; confidence description map + `formatGradeDotTooltip` parenthetical | ui (frontend lib) |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Paint `{c.headerCode}` in grade `<th>`; pass confidence into `formatGradeDotTooltip` | ui |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | Pass confidence into `formatGradeDotTooltip` (header already uses `headerCode`) | ui |
| `tests/component/frontend/lib/test_rubricDisplay.test.ts` | Expect compact grades-only `headerCode`; cover confidence parenthetical — **Betty** (engineer hook blocks `tests/`) | ui (Betty) |
| `tests/component/frontend/pages/test_JobsSkipped.test.tsx` | Assert compact header text / title if existing assertions break — **Betty** | ui (Betty) |
| `tests/component/frontend/pages/test_JobsInReview.test.tsx` | Same — **Betty** | ui (Betty) |

Do **not** edit: `recommendedJobReport.tsx` (out of Boundaries), `ConfidenceBullets.tsx`, `api_jobs.py`, grouping helpers (`groupJobsByAlignedRubric`), or artifact editors.

---

## Stage 1: Compact grades-only headers in `rubricDisplay.ts`

**Done when:** `buildJobListRubricColumnsForGroup` / `buildJobListRubricColumnsFromJobGrades` for vector `Technical (TE)` yields `headerCode === "TE"`, `label === "Technical"`, `headerTooltip === "Technical (5)"` (default importance). Bare vector `Fit` still yields `headerCode === "Fit"` (no forced two-letter slice that changes today’s short-label behavior). `cd src/ui/frontend && npx tsc -b --noEmit` passes. No page edits in this stage.

1. In `src/ui/frontend/src/lib/rubricDisplay.ts`, add a small helper (public or file-private — prefer public next to `normalizeRubricVectorKey` if tests need it) that parses a grades vector / object key into `{ code, label }`:
   - If the string matches `/^(.*?)\s*\(([A-Z]{2})\)\s*$/`, `label` = trimmed name group, `code` = the two-letter group.
   - Else `label` = trimmed string, `code` = that same trimmed string (preserve short bare labels like `Fit`).
2. Update **`resolveRubricHeaderCode`** so when `item.code` is absent and `item.label` ends with ` (XX)`, return the `XX` group (same regex). Keep `item.code` preferred when present. Keep `label?.slice(0, 2).toUpperCase()` only when there is no paren code and no `code` (artifact path without stored code).
3. Rewrite **`buildJobListRubricColumnsFromJobGrades`** array branch: for each `{ vector }`, parse with the helper; set `code` to parsed `code`, `label` to parsed `label`, `importance: RUBRIC_DEFAULT_IMPORTANCE`, `headerCode: resolveRubricHeaderCode({ code, label })` (must equal the compact code for `Name (XX)`), `headerTooltip: formatRubricColumnTooltip(label, RUBRIC_DEFAULT_IMPORTANCE)`, `gradeDescriptions: {}`.
4. Rewrite the object-keys branch the same way (parse each key).
5. Do **not** change `buildJobListRubricColumnsFromArtifact` beyond what `resolveRubricHeaderCode` already implies for labels that embed `(XX)`.

⚠️ **Decision:** Keep bare grades vectors without a `(XX)` suffix as their own `headerCode` (e.g. `Fit`), matching today’s test `headerCode === "Fit"`. Only strings with an explicit two-letter paren code become compact two-letter headers — that is the AC3 regression (`Technical (TE)` must not stay in the `<th>`).

---

## Stage 2: Skipped header cell uses `headerCode`

**Done when:** Skipped grade `<th>` visible text is `c.headerCode` (same as In Review); `title={c.headerTooltip}` unchanged; sort still uses `c.code` as the sort column id.

1. In `src/ui/frontend/src/pages/JobsSkipped.tsx`, in the non-floor rubric header map, change the cell text from `{c.code}{sortIndicator(...)}` to `{c.headerCode}{sortIndicator(...)}`.
2. Leave `key={c.code}`, `onClick={() => handleSort(sortKey, c.code)}`, and `title={c.headerTooltip}` unchanged.
3. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

---

## Stage 3: Grade-dot tooltip + confidence parenthetical

**Done when:** Hovering a grade-dot on Skipped and In Review shows rubric criterion text (job `reason` when present, else `col.gradeDescriptions[letter]`) and, when `confidence` is a number in 1–5, appends a space and parenthetical description matching `CONFIDENCE_DESCRIPTIONS` in `src/utils/config.py`. Missing / out-of-range confidence omits the parenthetical. `ConfidenceBullets` markup unchanged.

1. In `rubricDisplay.ts`, add exported constant **`CONFIDENCE_DESCRIPTIONS`** keyed `1`–`5` with **exact** strings from `src/utils/config.py` (`CONFIDENCE_DESCRIPTIONS`):
   - `5`: `The source explicitly states it.`
   - `4`: `The source strongly suggests it.`
   - `3`: `The source hints about it.`
   - `2`: `The source makes a vague reference.`
   - `1`: `The source doesn't say it out loud, but it's possible.`
2. Add exported **`confidenceDescription(confidence?: number): string`** — if `typeof confidence === "number"` and integer (or `Math.floor`) in 1–5, return the map entry; else `""`.
3. Extend **`formatGradeDotTooltip(col, grade, reasonFromJob?, confidence?: number): string`**:
   - Compute `base` exactly as today (trimmed reason, else `gradeDescriptions[letter]`, else `""`).
   - Compute `conf = confidenceDescription(confidence)`.
   - If `conf` and `base`: return `` `${base} (${conf})` ``.
   - If `conf` and no `base`: return `` `(${conf})` ``.
   - Else return `base`.
4. In **`JobsSkipped.tsx`** `gradeAndConfidenceForCol`, pass `row.confidence` (array path) into `formatGradeDotTooltip` as the 4th argument on every call that builds `gradeTooltip`. Object-map path has no confidence — omit / pass `undefined`.
5. Mirror the same 4th-argument wiring in **`JobsInReview.tsx`** `gradeAndConfidenceForCol`.
6. Do **not** change `recommendedJobReport.tsx` (optional 4th arg keeps that call site compiling).
7. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

⚠️ **Decision:** Mirror `CONFIDENCE_DESCRIPTIONS` in the frontend lib rather than extending `/api/state_ui_manifest` (or any API). Ticket Boundaries are UI display only; Python `config.py` already documents intentional duplication for prompt/`output_types` text. UI mirror must stay byte-identical to the five config strings — do not invent alternate copy. If Archie later wants a single API source, that is a separate ticket.

---

## Stage 4: Engineer verify (no `tests/` commits)

**Done when:** Typecheck clean; manual spot-check notes recorded in the Linear stage comment if useful; existing Betty component tests are left for qa-child.

1. Re-run `cd src/ui/frontend && npx tsc -b --noEmit`.
2. Do **not** commit under `tests/` (pre-commit hook). Note for Betty: `test_rubricDisplay.test.ts` currently expects `fallback[0].headerCode === "Technical (TE)"` — that expectation must flip to `"TE"` (and tooltip `"Technical (5)"`); add cases for `formatGradeDotTooltip` + confidence parenthetical.

---

## Self-Assessment

**Scope:** `Single-Component` — one frontend lib module plus the two Jobs list pages that already share `JobListRubricColumn`; no API/core.

**Conf:** `high` — AST-437 / AST-1064 patterns are in-tree; the Skipped `{c.code}` vs In Review `{c.headerCode}` mismatch and grades-only `headerCode: label` assignment are concrete, localized bugs.

**Risk:** `Medium` — wrong headerCode/label parsing could mis-align grade columns or tooltips on Skipped / In Review for pre-snapshot jobs; artifact-backed groups are low risk if Stage 1 stays grades-only focused.

---

## Code-rules check

- **§1.1 / in-scope-only:** Only job-list header + grade-dot tooltip display; no Recommended / hydration / grouping edits.
- **§1.3 DRY:** Fix shared builder + shared tooltip helper once; Skipped converges on `headerCode` like In Review.
- **§1.4 no-hardcoded-sets:** Confidence copy mirrors `config.py` with an explicit Decision (no API in scope); not a new invented vocabulary.
- **§3.5 frontend-file-placement:** Changes stay in `src/lib/rubricDisplay.ts` and existing `src/pages/Jobs*.tsx`.
- **§2.1 / ui-config-driven:** Grade letters and confidence numbers still come from job payload; description text is the approved config mirror.

---

## Review

| Field | Value |
|-------|-------|
| Branch | `sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips` |
| Build tip | `ec36ef4fb76e73729cc73efafb77c909e62efd3e` |
| Status | Code Complete |

---

## Radia code-rubric review

**Rubric:** code-rubric.v1 (`[code-rubric] revision=1`)  
**Publish ref tip:** `b91f64a42de2fc11442d5ed8b376cbc8a2553d19`  
**Overall:** DISCUSS (straggler callouts only — no product fix-now)

### What’s solid

- Shared `rubricDisplay` grades-only path parses `Name (XX)` → compact `headerCode` + clean label/tooltip; Skipped paints `{c.headerCode}` like In Review; sort keys stay on `c.code`.
- `formatGradeDotTooltip` + `CONFIDENCE_DESCRIPTIONS` mirror matches `src/utils/config.py` byte-for-byte; both Jobs pages pass confidence on the array path.
- Scope stays in frontend lib + two Jobs pages; Betty owns `tests/` / bible; engineer `code(AST-1086)` commit is src-only.

### Issues

**discuss (straggler):** `astral.debug.spikes-under-debug-dir` and `astral.docs.features-single-file-per-ticket` were Joan-excluded at plan time (plan layers `{ui}`) but the three-dot diff adds `docs/features/interface/ast-1086-…md`, so both score in-scope here. Verdict on each: **conforms** (normal plan file, not spike notes; single features file). No product action — belt-and-suspenders C4 only.

### Recommended actions

- Engineer: none for product. Acknowledge stragglers if desired, then resolve-child → User Testing.

---

## Resolution

**Date:** 2026-07-31  
**Status:** User Testing (resolve clean)

Radia **DISCUSS** overall with **no product fix-now**. Straggler callouts on `astral.debug.spikes-under-debug-dir` / `astral.docs.features-single-file-per-ticket` already **conforms** (normal single plan file). Advisory sibling test/bible tips via merge-tests left alone (outside AST-1086 product scope).

No product code changes in resolve. Publish tip after this commit; §9a dry-run vs `origin/dev` and `origin/ftr/AST-1078-headers-for-job-lists` required before UT.
