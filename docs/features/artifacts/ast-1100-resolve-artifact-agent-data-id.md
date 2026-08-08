<!-- linear-archive: AST-1100 archived 2026-08-07 -->

## Linear archive (AST-1100)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1100/resolve-artifact-bodies-from-pinned-agent-data-id-for-uat-surfaces-job  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1091 — Job resume artifact, cover letter and suggested responses is not saved in job_data  
**Blocked by / blocks / related:** parent: AST-1091

### Description

## What this implements

Job Resume / Cover Letter / suggested-answers surfaces used in UAT load body content via the pinned `agent_data_id` on `job_resume` / `cover_letter` / `proposed_answers` (existing agent_data read paths). After AST-1099.

## In scope

- [X] `pattern.batch.entity-agent-responses` — body stays in `agent_data`; display resolves by pinned id
- [X] `astral.batch.entity-agent-responses-latest-only` — no entity-row `agent_responses` revival; pin → `get_agent_data` / parse
- [X] `astral.layers.import-direction` — UI hydrates via core tracker helper → data read
- [X] `astral.standards.in-scope-only` — three pin slots + JAR/Materials/builder resolve only
- [X] `astral.patterns.coat-check-never-store-empty` — blank pin / missing row skips; hydrate does not write empties
- [X] `astral.standards.debug-contract-gated` — Style D resolve found/recorded only when `debug=True`
- [X] `astral.standards.dry-and-focused-functions` — one resolve + one hydrate helper; builder/API reuse
- [X] `astral.config.config-source-of-truth` — `JOBS_RECOMMENDED_ARTIFACT_TABS` remaps in `config.py`

## Considered but excluded

- [X] Writing / mid-chain pin of RESPONSE ids — AST-1099
- [X] TASK_CONFIG `persist_in` — parent forbids
- [X] Unrelated JAR chrome / tab redesign beyond these three pointers
- [X] Session cover letter / session resume paste
- [X] `tests/` / `docs/test-bible/**` — Betty

## Acceptance criteria

- [X] 4. A full successful daisy-chain that ran those three hops leaves all three pointer keys set; UAT surfaces that show Job Resume / Cover Letter / suggested answers resolve content via those ids without a manual PUT of the response body.

## Boundaries

Does not own writing the pins (AST-1099). Does not redesign unrelated JAR chrome beyond resolving these three pointers for display/UAT.

## Notes for planning

Resolve via existing agent_data read paths; pin keys are `job_resume` / `cover_letter` / `proposed_answers`.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/ast-1091-job-artifact-agent-data-pins`, child `sub/AST-1091/<this-id>-resolve-artifact-agent-data-id`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-31T06:06:27.360Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` failed for `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id` vs `origin/ftr/ast-1091-job-artifact-agent-data-pins`. Offending ancestry in `ftr..sub` (via `merge origin/dev`):
- `1a933c7e Merge remote-tracking branch 'origin/dev' into tmp-refresh-AST-1096-…`
- `2db5045f Merge remote-tracking branch 'origin/dev' into tmp-refresh-AST-1093-…`

AST-1100 ticket sequence itself looks complete (plan/code/merge-tests/test/docs/resolve). @Katherine Johnson — rebuild/republish sub onto `origin/ftr/ast-1091-job-artifact-agent-data-pins` without `Merge remote-tracking` ancestry in the ftr..sub range, then re-run merge-child.

— Chuckles

#### radia — 2026-07-31T06:03:12.611Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1100
**Publish ref:** `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id` @ `8a94d00b` (code `b6be8d5e`; merge-tests `7eb0759b`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1100)` → `c1c77d53` |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | Publish forward on origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1091/AST-1100-…` matches Git table |
| orch.git.merge-on-checkout | universal | conforms | No illegal merge recipe in ticket commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in AST-1100 history |
| orch.git.no-dev-agent-branches | universal | conforms | Child sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Reviewed in astral-AST-1091 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No open product fork in diff |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–5 implemented as planned |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty test + merge-tests + fixture align |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Implementer path was Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Assignee left with Katherine |
| orch.roles.pre-commit-path-bans | universal | conforms | Doc-only Radia commit; engineer off bans |
| astral.agent.confidence-bounds | scoped | conforms | No graded confidence path touched |
| astral.agent.do-task-delegation | scoped | conforms | No do_task bypass; reads existing RESPONSE rows |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector changes |
| astral.batch.batch-id-first | scoped | conforms | No claim/batch API signature changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id format changes |
| astral.batch.claim-process-release | scoped | conforms | No claim/release changes |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Body stays in `agent_data`; pin → get_agent_data/parse |
| astral.config.config-source-of-truth | scoped | conforms | Tab keys remapped only in `JOBS_RECOMMENDED_ARTIFACT_TABS` |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring/threshold changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no `artifacts/**` / spikes paths |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/` (not misplaced spike) |
| astral.dispatch.seed-auto-false | scoped | conforms | Config touch is tab remap only; no dispatch seed/`auto_mode` |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-1100-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty did not edit src/features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer code commit left tests/bible to Betty |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Resolve via data read; no external I/O |
| astral.layers.import-direction | scoped | conforms | UI→core→data; lazy imports documented |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` in ticket change set |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Tab keys from config; hydrate in API via core |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Blank pin/missing row → None; hydrate does not write |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult/`render_verdict` changes |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | New PUT aliases use `@require_auth` |
| astral.standards.data-raises-caller-logs | scoped | conforms | Data read; core/UI handle missing |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` in ticket change set |
| astral.standards.debug-contract-gated | scoped | conforms | Style D resolve only when `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | conforms | One resolve + one hydrate; builder/API reuse |
| astral.standards.in-scope-only | scoped | conforms | Three pin slots + UAT surfaces; AST-1099 write excluded |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` / `debug_detail` |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in utils/core/ui (+ Betty tests) |
| astral.standards.no-hardcoded-sets | scoped | conforms | Pin keys once in hydrate; tabs from config |
| astral.standards.public-then-helpers | scoped | conforms | Helpers beside existing tracker artifact saves |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data import |
| astral.state.core-decides-transitions | scoped | conforms | No state-machine transition changes |
| astral.state.job-prior-states-enforced | scoped | conforms | No job prior-state changes |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Read-only resolve; no new daisy-chain |
| astral.ui.frontend-file-placement | scoped | conforms | Edit stays in `lib/`; no new FE subdirs |
| astral.ui.naming-conventions | scoped | conforms | Existing snake_case API paths; remapped keys match pins |
| astral.ui.single-gunicorn-worker | scoped | conforms | Config touch is tab remap only; no worker changes |

## Pattern conformance

| cited | verdict |
|-------|---------|
| pattern.batch.entity-agent-responses | conforms |
| astral.batch.entity-agent-responses-latest-only | conforms |
| astral.layers.import-direction | conforms |
| astral.standards.in-scope-only | conforms |
| astral.patterns.coat-check-never-store-empty | conforms |
| astral.standards.debug-contract-gated | conforms |
| astral.standards.dry-and-focused-functions | conforms |
| astral.config.config-source-of-truth | conforms |

## Plan adherence

Stages 1–5 match: tab remap, resolve+hydrate, GET hydrate + PUT aliases, builder pin read, FE visibility. Self-Assessment Single-Component / high / Medium still fits. Sibling AST-1099 (pin write) untouched.

## Findings

**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket` and `astral.debug.spikes-under-debug-dir`; ticket-scoped diff brings them in-scope. Both **conform**. No product fix-now.

**advisory:** Human PUT replaces pin string with body dict on that key — intentional per plan Medium risk.

## Notes

- Change set for applies_when + product judgment: AST-1100 commits on publish tip.
- Plan-rubric verdict attached (Joan APPROVED). Active statutes = 57.
- Docs append @ `8a94d00b`.
- C6: UI has no `src.data`/`src.external` imports; lazy tracker/agent imports carry cycle comments; new routes `@require_auth`; debug Style D gated on resolve helper.

context_tokens≈45000

— Radia

#### betty — 2026-07-31T05:59:15.766Z
## QA test manifest

`origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id` @ `7eb0759b` (`merge-tests(AST-1100): origin/tests c1c77d5319208246a0def65791a09599cefb266f`)

### 1. Existing coverage (bible-backed)

- Pin write path remains AST-1099 suites (already on ftr/sub).
- Legacy PUT `resume_content` / `cover_letter` / `application_responses` routes still covered by existing `TestJobsRoutes` cases.

### 2. Broken / obsolete (revised this pass)

1. Fixture `report_artifact_tabs` keys `resume_content` / `application_responses` → `job_resume` / `proposed_answers` (`stateUiManifestFixture.ts`).
2. `anyReportArtifactContent` + AST-581 materials assert updated for remapped keys (`test_recommendedJobReport.test.tsx`).

### 3. Gaps (this pass)

1. Tab key remap — `tests/component/utils/test_config.py::TestAst1100ArtifactTabPinKeys`
2. Resolve + hydrate — `tests/component/core/test_tracker.py::TestAst1100ResolveHydrateJobArtifactPins`
3. GET hydrate + PUT aliases — `tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi`
4. Builder pin resolve — `tests/component/core/test_builder.py::TestAst1100BuilderPinResolve`
5. FE visibility + pin strings — `tests/component/frontend/lib/test_recommendedJobReport.test.tsx` (`recommendedJobReport — AST-1100 pin-slot visibility`)

**Integration:** none (revise-existing only).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1100ArtifactTabPinKeys \
  tests/component/core/test_tracker.py::TestAst1100ResolveHydrateJobArtifactPins \
  tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi \
  tests/component/core/test_builder.py::TestAst1100BuilderPinResolve \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx
```

### Bible shasums on publish tip

- `docs/test-bible/core/tracker.md` `6e9bb3a52d227563afa8086701d6f44a9bd67a97e590f14d90848fda777728d5`
- `docs/test-bible/core/builder.md` `024a7f70677b2d3b6c40b49665e531570f09614321b15ef1d1e744e9d765e3f5`
- `docs/test-bible/utils/config.md` `21968875601e512e408019896a8a366fb35ce476483da74cc54f855012dd8a9b`
- `docs/test-bible/ui/api/api_jobs.md` `b0faa492e7fb06d46a8a46be932e6a52f48249280d56aff91d7b51290335c269`
- `docs/test-bible/frontend/lib.md` `75e2d2ed5f9041bacc403819361c02810b6fa09aed446c030ea41c33ec285b25`

— Betty

#### joan — 2026-07-31T05:47:09.148Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1100
**Overall:** APPROVED

**Notes:** Files Changed row `tests/.../stateUiManifestFixture.ts` Layer cell `—` mapped to `docs` for matching only; path still considered for path-scoped statutes.

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1–3 pin writes after hops | N/A — boundary (AST-1099). Load/display of bodies via pin ids: Stages 2–5 |
| AC4 daisy-chain leaves three pointers; UAT surfaces resolve via ids without manual PUT | Pointers already AST-1099. Resolve/display: Stages 1–5 (tab remap, hydrate GET, builder, FE visibility) |
| AC5 debug on pin persist path | N/A — boundary (AST-1099). Resolve path Style D when `debug=True`: Stage 2 |
| AC6 failed/empty hops do not blank prior pointer | N/A write — AST-1099. Hydrate/resolve skip blank/missing without writing empties: Stage 2 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 tab `artifact_key` remap | Architectural config alignment; Functional scope UAT surfaces |
| Stage 2 resolve + display hydrate | Purpose — load `agent_data` by stored id; coat-check empty |
| Stage 3 job GET hydrate + PUT aliases | UAT JAR/ArtifactEditor; no manual PUT required after chain |
| Stage 4 builder pin read | Materials/print HTML paths |
| Stage 5 FE visibility helpers | Print/Materials gates on remapped keys |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub via plan/code vocabulary |
| orch.git.flow-direction-inviolable | conforms | origin/sub only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1091/AST-1100-… only |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1091 epic worktree |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; no open product fork |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate only |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | Product `tests/` edits deferred to Betty; hand-off if fixture blocks |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned-path product edits planned |
| astral.agent.confidence-bounds | conforms | No grade confidence path |
| astral.agent.do-task-delegation | conforms | No new do_task bypass; read existing RESPONSE rows |
| astral.agent.grade-vector-validation | conforms | No grade-vector changes |
| astral.batch.batch-id-first | conforms | No claim API changes |
| astral.batch.batch-id-format | conforms | No batch_id format changes |
| astral.batch.claim-process-release | conforms | No claim/release changes |
| astral.batch.entity-agent-responses-latest-only | conforms | Body stays in `agent_data`; pin → get_agent_data / parse |
| astral.config.config-source-of-truth | conforms | Tab keys remapped only in `JOBS_RECOMMENDED_ARTIFACT_TABS` |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring changes |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.dispatch.seed-auto-false | conforms | No dispatch_task seed/`auto_mode` changes |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features |
| astral.git.engineer-test-tree-ban | conforms | Plan forbids engineer `tests/` edit; Betty owns fixture align |
| astral.layers.core-vs-external-bright-line | conforms | Resolve via data read; no external I/O |
| astral.layers.import-direction | conforms | UI→core→data; lazy imports for cycles |
| astral.layers.ui-config-driven-business-logic | conforms | Tab keys from config; hydrate resolved in API via core helper |
| astral.patterns.coat-check-never-store-empty | conforms | Blank pin/missing row → None; hydrate does not write empties |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult changes |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Extends existing auth’d jobs routes; no new open routes |
| astral.standards.data-raises-caller-logs | conforms | Data read; core/UI handle missing |
| astral.standards.debug-contract-gated | conforms | Style D resolve only when `debug=True` |
| astral.standards.dry-and-focused-functions | conforms | One resolve + one hydrate; builder/API reuse |
| astral.standards.in-scope-only | conforms | Three pin slots + UAT surfaces; AST-1099 write excluded |
| astral.standards.logging-via-utils | conforms | Style D via existing logger helpers |
| astral.standards.no-cross-contamination | conforms | Stays in utils/core/ui |
| astral.standards.no-hardcoded-sets | conforms | Pin keys listed once in hydrate; tabs from config |
| astral.standards.public-then-helpers | conforms | New helpers beside existing tracker artifact saves |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state changes |
| astral.state.no-daisy-chain-in-run | conforms | Read-only resolve; no new daisy-chain |
| astral.ui.frontend-file-placement | conforms | Edit stays in `lib/`; no new FE subdirs |
| astral.ui.naming-conventions | conforms | Existing snake_case API paths; remapped keys match pins |
| astral.ui.single-gunicorn-worker | conforms | No worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.git.engineer-test-tree-ban, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — paths {docs/features/**} match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Stage 3 PUT step wanders through alternate options before the binding **Use:** (write edited dict onto pin key). Final choice is clear; tighten prose on next plan touch if revisited.

**discuss (non-blocking):** Files Changed lists a `tests/` fixture “for completeness” while forbidding engineer edits — fine if Betty owns it; do not ship engineer commits under `tests/`.

**acceptable:** Self-assessment Single-Component / high / Medium matches the resolve-only scope; Medium risk (bad parse / hydrate mask) is specific.

**R6:** Definition fidelity pass (resolve UAT surfaces; no pin write; no `persist_in`). Layer/import pass. Config tab remap pass. Coat-check + debug-gated pass. Sibling AST-1099 correctly excluded.

context_tokens≈55000

— Joan

#### katherine — 2026-07-31T05:44:33.876Z
Plan published on `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id` @ `e45d2015`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id/docs/features/artifacts/ast-1100-resolve-artifact-agent-data-id.md

**Approach:** Remap `JOBS_RECOMMENDED_ARTIFACT_TABS` to pin slots → tracker `resolve_job_artifact_agent_data_body` + `hydrate_job_artifacts_for_display` (read-only overlay via existing `get_agent_data` / parse helper) → hydrate on job GET; builder prefers resolved pins when legacy body dicts missing; FE visibility helpers use remapped keys (+ string pin counts as content).

**Self-assessment**
- **Scope — Single-Component:** config remap + tracker resolve/hydrate + builder pin read + jobs API GET/PUT aliases + FE visibility helpers.
- **Conf — high:** reuses agent_data id read + `_parsed_response_from_stored_response_text`; AST-1099 slots already on `ftr`.
- **Risk — Medium:** bad RESPONSE parse leaves tabs empty after a green chain; PUT may overwrite a pin string with an edited body dict (intentional after human edit).

---

# AST-1100 — Resolve artifact bodies from pinned agent_data_id for UAT surfaces

**Linear:** [AST-1100](https://linear.app/astralcareermatch/issue/AST-1100/resolve-artifact-bodies-from-pinned-agent-data-id-for-uat-surfaces-job)

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved) (AC reference only)

**Publish ref:** `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`

After AST-1099 pins RESPONSE `agent_data_id` under `job_data.artifacts.job_resume` / `cover_letter` / `proposed_answers`, UAT surfaces (JAR Artifacts tabs, print/Materials Preview, job HTML builders) must load the hop body via existing `agent_data` read paths — no manual PUT of the response JSON onto the job row.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Remap `JOBS_RECOMMENDED_ARTIFACT_TABS` `artifact_key` values to the three pin slots | utils |
| `src/core/tracker.py` | Add pin→body resolve + display hydrate helpers (read-only overlay; coat-check empty) | core |
| `src/core/builder.py` | Prefer resolved pin bodies for job resume / cover letter HTML when legacy body dicts are absent | core |
| `src/ui/api/api_jobs.py` | Hydrate artifacts on job GET; accept PUT for remapped keys (map to existing body saves) | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Visibility helpers use remapped pin keys (after hydrate, values are bodies) | ui |
| `tests/component/frontend/fixtures/stateUiManifestFixture.ts` | Align fixture `artifact_key`s with remapped tabs (Betty may own; list for completeness — engineer does not edit `tests/` unless Betty already landed; if fixture blocks FE typecheck in-tree, stop and hand off) | — |

**Out of scope (do not touch):**

| Item | Owner |
|------|--------|
| Writing / mid-chain pin of `agent_data_id` | AST-1099 (already on `ftr`) |
| TASK_CONFIG `persist_in` | parent forbids |
| Unrelated JAR chrome / tab redesign beyond these three pointers | excluded |
| Session cover letter / session resume paste | excluded |
| `tests/` / `docs/test-bible/**` product coverage | Betty |

## Stage 1: Config — remap JAR artifact tab keys

**Done when:** `JOBS_RECOMMENDED_ARTIFACT_TABS` points Job Resume / Cover Letter / Application Questions at `job_resume` / `cover_letter` / `proposed_answers`; `shapes_key` for cover stays `"cover_letter"`; Job Resume keeps `use_resume_structure: True`; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, change `JOBS_RECOMMENDED_ARTIFACT_TABS` to:

```python
JOBS_RECOMMENDED_ARTIFACT_TABS = [
    {
        "tab_id": "artifact_resume",
        "nav_label": "Job Resume",
        "artifact_key": "job_resume",
        "shapes_key": None,
        "use_resume_structure": True,
    },
    {
        "tab_id": "artifact_cover",
        "nav_label": "Cover Letter",
        "artifact_key": "cover_letter",
        "shapes_key": "cover_letter",
        "use_resume_structure": False,
    },
    {
        "tab_id": "artifact_application",
        "nav_label": "Application Questions",
        "artifact_key": "proposed_answers",
        "shapes_key": None,
        "use_resume_structure": False,
    },
]
```

⚠️ **Decision:** Remap to the AST-1099 pin slot names (not keep `resume_content` / `application_responses` as tab keys). Legacy body keys remain on the job for older rows and for PUT body-storage aliases in Stage 3; display hydrate (Stage 2) bridges pin → body for the remapped keys.

## Stage 2: Tracker — resolve pin id → body + display hydrate

**Done when:** Given a non-empty pin string, resolve returns the parsed RESPONSE body from `agent_data` (same parse spirit as mid-chain hydration); blank/missing id or missing row returns `None` without writing; hydrate returns a shallow-copied `artifacts` dict where each pin-slot string is replaced by the resolved body when resolve succeeds; `python3 -m py_compile src/core/tracker.py` passes.

1. In `src/core/tracker.py`, next to `pin_job_artifact_agent_data_id`, add:

   - `resolve_job_artifact_agent_data_body(agent_data_id: Any, *, debug: bool = False) -> Any`:
     - Coat-check: blank/None/whitespace → return `None` (optional Style D skip when `debug=True`: `artifact_resolve skipped reason=empty_agent_data_id`).
     - Load row via existing data API already used by core: `from src.data.database import get_agent_data` (or the same import path `agent.py` uses as `_get_agent_data_row`) — **one id**.
     - If row missing → `None` (skip reason `missing_agent_data_row`).
     - Take `block_data` (or `content`) text; if empty → `None`.
     - Parse with the same rules as `src.core.agent._parsed_response_from_stored_response_text` — **lazy-import** that helper from `src.core.agent` (cycle-safe) OR duplicate the tiny JSON/`agent_payload` unwrap inline in tracker to avoid import cycles. Prefer lazy-import of the existing helper.
     - When `debug=True`: Style D `artifact_resolve agent_data_id=<id> recorded` (or skip). No ungated `[DEBUG]` spam.

   - `hydrate_job_artifacts_for_display(artifacts: Any, *, debug: bool = False) -> Dict[str, Any]`:
     - If `artifacts` is not a dict → return `{}`.
     - Shallow-copy the dict.
     - For each pin key in `("job_resume", "cover_letter", "proposed_answers")`:
       - If value is a non-empty `str`: `body = resolve_job_artifact_agent_data_body(value, debug=debug)`; if `body is not None`, set `out[key] = body`.
       - If value is already a non-empty dict/list (legacy body still under `cover_letter`), leave it.
     - Do **not** call `save_job_data` — display overlay only; stored pins stay strings on disk.

2. Export / use only from core + ui (API). No new TASK_CONFIG fields.

⚠️ **Decision:** Hydrate is response-overlay only. Editing via PUT may replace a pin string with a body dict on that key (Stage 3); initial UAT after a successful chain must work with zero PUTs.

## Stage 3: API — hydrate on job GET; PUT aliases for remapped keys

**Done when:** `GET /api/jobs/<astral_job_id>` returns `job_data.artifacts` after `hydrate_job_artifacts_for_display`; PUT endpoints exist (or alias) so ArtifactEditor can save under remapped keys without 404; `python3 -m py_compile src/ui/api/api_jobs.py` passes.

1. In `src/ui/api/api_jobs.py`, locate the single-job GET handler that returns the job JSON used by `JobAnalysisReportModal` / `ArtifactEditor` (`GET /api/jobs/<id>`). After loading the job row and before `jsonify`:
   - Copy `job_data` if needed; replace `artifacts` with `hydrate_job_artifacts_for_display(get_job_artifacts(job) or artifacts_dict)`.
   - Do not persist the hydrated copy.

2. PUT aliases (ArtifactEditor posts to `/api/jobs/<id>/artifacts/<artifactKey>`):
   - Keep existing `resume_content` / `cover_letter` / `application_responses` routes.
   - Add (or generalize) routes so `job_resume` and `proposed_answers` accept the same body shapes:
     - `PUT .../artifacts/job_resume` → same implementation as `put_job_resume_content` (calls `save_job_artifact_resume_content`) **and/or** also write the dict onto `artifacts.job_resume` if you choose body-on-pin-key — **pick one**:
       - **Required choice:** `PUT job_resume` calls `save_job_artifact_resume_content` (legacy `resume_content` body store) **and** does not clear `job_resume` pin string if still present — wait: `save_job_artifact_resume_content` only merges `resume_content`. After remap, ArtifactEditor reads `job_resume` from hydrated GET. On save it PUTs to `job_resume`. Implement `PUT job_resume` to: validate dict body; `save_job_data(..., {"artifacts": {"job_resume": body}})` (body dict replaces pin — acceptable after human edit) **OR** save to `resume_content` and leave pin. **Use:** write the edited dict to `job_resume` via `save_job_data` (same key the tab reads). Mirror for `proposed_answers` (dict/list as today for application responses). `PUT cover_letter` already exists — leave it (dict overwrites pin string after edit).

3. Do not add new JAR routes beyond these aliases / hydrate.

## Stage 4: Builder — HTML preview resolves pins

**Done when:** `build_resume(job_id)` / cover-letter HTML path can render from a pin when `resume_content` / cover body dict is missing; `python3 -m py_compile src/core/builder.py` passes.

1. In `src/core/builder.py` `_resolve_resume_sections`:
   - After checking `artifacts.resume_content`, if missing/empty: if `artifacts.job_resume` is a non-empty string, `body = resolve_job_artifact_agent_data_body(...)` (lazy-import from tracker); if body is a non-empty dict, use it; else fall through to `base_resume`.
2. In `_resolve_cover_letter`:
   - If `artifacts.cover_letter` is a non-empty string pin, resolve to body; if dict with fields, normalize via existing `_cover_letter_fields_for_read` / `normalize_cover_letter_artifact` as appropriate; if resolve fails, keep existing sample_cover fallback.

## Stage 5: Frontend visibility helpers

**Done when:** Print / Materials Preview / `anyReportArtifactContent` gate on the remapped keys; hydrated GET bodies (dicts) still count as content; `artifactHasContent` also treats a non-empty string as content (pin present even if hydrate skipped); no other JAR chrome changes.

1. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`:
   - Update `artifactHasContent`: after the object/array branches, if `typeof raw === "string"` return `raw.trim().length > 0`.
   - `printResumeVisible` → `artifactHasContent(artifacts, "job_resume")` (fallback: also true if legacy `resume_content` has content — `artifactHasContent(..., "job_resume") || artifactHasContent(..., "resume_content")`).
   - `printCoverVisible` → keep `"cover_letter"` (pin or body).
   - `materialsPreviewVisible` → use the same resume/cover checks as above.
2. Do **not** redesign `JobAnalysisReportModal` section layout — it already iterates `report_artifact_tabs` from the manifest.

## Self-Assessment

**Scope — Single-Component:** Config tab remap + tracker resolve/hydrate + builder pin read + jobs API GET/PUT aliases + small FE visibility helpers for the three pin slots.

**Conf — high:** Reuses `get_agent_data` / `_parsed_response_from_stored_response_text` and existing JAR tab/ArtifactEditor wiring; AST-1099 already defines slot names and stops body-copy on finalize hops.

**Risk — Medium:** Wrong parse of RESPONSE text leaves tabs empty after a successful chain; GET hydrate bugs could mask stored pins; PUT overwrite of `cover_letter` pin with an edited dict is intentional after human edit.

## Code rules check

| Rule | Notes |
|------|-------|
| §1.3 DRY | One resolve helper; builder + API call it |
| §2.1 config | Tab keys only in `JOBS_RECOMMENDED_ARTIFACT_TABS` |
| §2.4.1 entity-agent-responses-latest-only | Body stays in `agent_data`; job holds pointer until edit |
| coat-check-never-store-empty | Resolve skips blank ids; hydrate does not write empties |
| §3.3 import-direction | UI → core → data; lazy imports for cycles |
| in-scope-only | Three UAT surfaces / three pin keys only |

## Review

**Branch:** `sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`  
**Code:** `b6be8d5e`  
**Publish tip reviewed:** `7eb0759b` (`merge-tests(AST-1100)`)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1100  
**Overall:** DISCUSS

### What’s solid
- Tab remap to AST-1099 pin slots; GET hydrate via core helper; PUT aliases under remapped keys with `@require_auth`.
- `resolve_job_artifact_agent_data_body` coat-checks blank/missing; Style D gated; lazy agent parse import documented.
- Builder prefers legacy body then pin resolve then fallback; FE visibility accepts pin strings + hydrated bodies.
- UI imports core only (no `src.data` / `src.external`); Betty owns tests/bible + fixture align.

### Issues
**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket` and `astral.debug.spikes-under-debug-dir`; ticket-scoped diff makes them in-scope. Both **conform**. No product fix-now.

### Recommended actions
- Engineer: no fix-now. Acknowledge stragglers on resolve-child / move to User Testing if no disagreement.
- Pointer overwrite on human PUT remains intentional (plan Medium risk).

### Notes
- Statute applies_when + product judgment used AST-1100 commit change set (formal `origin/dev...` three-dot may include epic ancestry).
- Plan-rubric verdict attached (Joan APPROVED). Active statute set count=57 (includes `astral.dispatch.seed-auto-false`).

context_tokens≈45000

— Radia

## Resolution

**Date:** 2026-07-31  
**Publish tip before resolve:** `8a94d00b` (Radia `docs(AST-1100)` on merge-tests `7eb0759b` / code `b6be8d5e`)

- **fix-now:** none — Radia overall DISCUSS with no product fix-now.
- **discuss (C4 straggler):** Acknowledged. Joan’s excluded `astral.docs.features-single-file-per-ticket` / `astral.debug.spikes-under-debug-dir` are in-scope on the ticket diff and both **conform**; no product change.
- **advisory:** Human PUT may replace pin string with body dict — left as planned Medium risk; no code change.
