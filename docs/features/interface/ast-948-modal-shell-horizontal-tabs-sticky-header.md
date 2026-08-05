<!-- linear-archive: AST-948 archived 2026-08-05 -->

## Linear archive (AST-948)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-948/modal-shell-horizontal-tabs-sticky-header-redesign-recommended-job  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-858 — Redesign Recommended Job Modal  
**Blocked by / blocks / related:** parent: AST-858; blocks: AST-951; blocks: AST-950; blocks: AST-949

### Description

## What this implements

Rebuild the Recommended Job Report chrome: horizontal top tabs **Summary** / **Analysis** / **Artifacts** (Summary default), shared collapsible section list pattern, and sticky header with deeplinked job title (apply URL), deeplinked company homepage, Copy Application Email, Copy LinkedIn Profile, plus **Print Resume** / **Print Cover Letter** (open server-rendered HTML in a new tab when content exists; no print for application questions). List row-click entry and Skip unchanged.

## Acceptance criteria

1. Opening a Recommended job shows **Summary**, **Analysis**, and **Artifacts** as **horizontal** top tabs; **Summary** is selected by default.
2. Header shows deeplinked **job title** (apply URL) and **company name** (homepage when known), **Copy Application Email**, **Copy LinkedIn Profile**, and **Print Resume** / **Print Cover Letter** buttons (each only when that artifact exists) opening print-ready HTML in a new tab.
3. Existing Recommended-list entry (row click opens modal) and Skip behavior unchanged from current shipped UX.

## Boundaries

* Does **not** implement Summary / Analysis / Artifacts section bodies (siblings [AST-949](https://linear.app/astralcareermatch/issue/AST-949/summary-tab-sections-redesign-recommended-job-modal), [AST-950](https://linear.app/astralcareermatch/issue/AST-950/analysis-tab-grades-and-confidence-redesign-recommended-job-modal), [AST-951](https://linear.app/astralcareermatch/issue/AST-951/artifacts-tab-generate-cancel-edit-redesign-recommended-job-modal)).
* Does **not** change consult scoring, dispatch, or artifact pipeline.

## Notes for planning

Reuse existing Recommended Job Report components and StateUi manifest tab config; replace left SideTabPanel rail with horizontal tabs. Print reuses AST-605 HTML routes (no Preview Materials modal).

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-858-redesign-recommended-job-modal`, child `sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-23T23:06:17.740Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-948
**Publish ref:** `dedf666f3b41d0cf4ac58f3d8a58d1c464876938` (`origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | config.py touch is report tab/section manifest only; no confidence math |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths (core) miss diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths (core) miss diff |
| astral.batch.batch-id-first | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.batch-id-format | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.claim-process-release | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.config.config-source-of-truth | scoped | needs-discussion | Summary `default_expanded` in config; Analysis/Artifacts expand seeds still React-mapped (Stage 4 / Joan discuss) |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | no pass_threshold / score_floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets or env-specific literals added |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths (artifacts/spikes) miss diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | features plan only; not spike notes under docs/features |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `docs/features/interface/ast-948-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty `test`/`merge-tests` stay off src/features (except merge) |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code`/`docs` only; tests/bible via Betty |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths (core/external) miss diff |
| astral.layers.import-direction | scoped | conforms | UI + utils only; React has no data/external imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths (scripts) miss diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | top tabs / sections / primary actions from manifest |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths (core) miss diff |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths (core) miss diff |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new API endpoints; frontend chrome only |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer logging changes |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths (data) miss diff |
| astral.standards.debug-contract-gated | scoped | conforms | no backend debug-contract emission in diff |
| astral.standards.dry-and-focused-functions | scoped | conforms | shared `ReportSectionList` + print helpers via `artifactHasContent` |
| astral.standards.in-scope-only | scoped | conforms | empty bodies for siblings; MaterialsPreview/SideTabPanel not deleted |
| astral.standards.logging-via-utils | scoped | conforms | no new logging paths |
| astral.standards.no-cross-contamination | scoped | conforms | stays in utils config + ui frontend (+ Betty tests/docs) |
| astral.standards.no-hardcoded-sets | scoped | conforms | tab/section id sets from config; seed rules match approved plan |
| astral.standards.public-then-helpers | scoped | conforms | small focused header / section-list / modal shell |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py only; no utils→data import |
| astral.state.core-decides-transitions | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.state.job-prior-states-enforced | scoped | conforms | no JOB_STATES / prior_states edits |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths (core) miss diff |
| astral.ui.frontend-file-placement | scoped | conforms | `ReportSectionList` under components/; styles in App.css |
| astral.ui.naming-conventions | scoped | conforms | PascalCase components; existing recommended-report CSS patterns |
| astral.ui.single-gunicorn-worker | scoped | conforms | no gunicorn/worker config changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one `merge-tests(AST-948)` onto sub from Betty tip |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests subjects with AST-948 |
| orch.git.flow-direction-inviolable | universal | conforms | publishes on child sub under parent ftr; no reverse merge |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header` |
| orch.git.merge-on-checkout | universal | conforms | no contrary merge instructions on tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | linear tip history; no rewrite/force |
| orch.git.no-dev-agent-branches | universal | conforms | authoritative publish-ref; not Linear gitBranchName |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-858` epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no product ambiguity; empty bodies / Generate strip match plan |
| orch.pipeline.plan-is-bible | universal | conforms | tip implements Stages 1–4 as written |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Interface child; review-child on Tests Passed |
| orch.pipeline.status-gates-skill-entry | universal | conforms | entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes amendments |
| orch.roles.betty-owns-test-tree | universal | conforms | tests + test-bible via Betty; engineer barred |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer stays assignee through review |
| orch.roles.pre-commit-path-bans | universal | conforms | role path bans respected across code/docs vs test commits |

## Pattern conformance

none cited

## Plan adherence

Diff matches plan Stages 1–4 and Self-Assessment Scope (Single-Component: config manifest + JAR chrome). Empty Summary/Analysis/Artifacts bodies and Artifacts `leading` Generate/Cancel strip match Boundaries vs AST-949/950/951. `JobsRecommended` list/Skip untouched. AST-591 close-on-generate/cancel preserved; cancel key corrected to manifest `cancel_build`.

## Findings

### discuss

1. **astral.config.config-source-of-truth** — `JobAnalysisReportModal` still seeds Analysis `default_expanded` via `tab_id === "phase_jd"` and Artifacts all-collapsed in React while Summary defaults come from `report_summary_sections` in config. Same mild SoT inconsistency Joan flagged at plan time (non-blocking vs approved Stage 4).
2. **C4 straggler** — Joan excluded `astral.debug.spikes-under-debug-dir`; code diff includes `docs/features/**` so in-scope. Verdict remains conforms (plan doc, not spike notes).
3. **C4 straggler** — Joan excluded `astral.docs.features-single-file-per-ticket`; features path present. Verdict remains conforms (one ticket file).
4. **C4 straggler** — Joan excluded `astral.git.engineer-test-tree-ban`; tests/bible present via Betty. Verdict remains conforms (engineer did not commit test-tree paths).

### fix-now

none

### What’s solid

Horizontal Summary/Analysis/Artifacts shell, sticky header deeplinks + Copy Application Email / LinkedIn + Print Resume/Cover (AST-605 routes), `ReportSectionList` Expand-All chrome, Generate/Cancel on Artifacts strip, sibling body boundaries held.

### Notes

Plan-rubric verdict attached (Joan APPROVED). Docs append: `docs(AST-948): Radia review — findings` on publish-ref.

context_tokens≈48000

#### betty — 2026-07-23T23:00:21.813Z
## QA test manifest — AST-948

**Publish:** `origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header` @ `b4c9201`
**Betty commit:** `origin/tests` `305d41b` → `merge-tests(AST-948): origin/tests 305d41bdf7ecb3469a19fbfeb6b2ec94d84d7fae`

### Coverage

1. **Config manifest** — `tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs`
   - `report_top_tabs` = Summary / Analysis / Artifacts; `report_summary_sections` present; `report_fixed_tabs` gone; phase/artifact section labels updated.
2. **JAR horizontal shell** — `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` (`JobAnalysisReportModal — AST-948 horizontal shell`)
   - Horizontal tabs, Summary default, empty section chrome, sticky header deeplinks + Copy controls, Print Resume/Cover → AST-605 routes, Generate/Cancel on Artifacts strip, AST-645 in-flight, no Preview Materials / Apply button.
3. **ReportSectionList** — `tests/component/frontend/components/test_ReportSectionList.test.tsx`
4. **Print helpers** — `tests/component/frontend/lib/test_recommendedJobReport.test.tsx` (`AST-948 print helpers`)
5. **List entry regression** — `tests/component/frontend/pages/test_JobsRecommended.test.tsx` (`opens the report modal from a row click`) — horizontal tabs; Skip unchanged.

### Obsolete / revised

Left-rail `.side-tab-list` / upshot bodies / Preview Materials / Apply-button / ArtifactEditor-in-JAR asserts (AST-565 / AST-581 / AST-553 body paths) rewritten for empty-shell chrome. Section bodies = AST-949/950/951.

### Narrowed run

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_ReportSectionList.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs
```

### Bible shasums (`origin/sub/...`)

- `docs/test-bible/frontend/components.md` → `58fa69e8386d7c4a447259cb882b23f935670918311b1ce91f21c5d3bfabb06b`
- `docs/test-bible/frontend/lib.md` → `aa6c8deda7dc93a9f4fe7177314eb8e9e8df7e79b8c9a056c3a24a62be515e3c`
- `docs/test-bible/frontend/pages.md` → `b78d9f7bf438877e88d71cb2024f70ac41a32103701f577089153668ff7b888a`
- `docs/test-bible/utils/config.md` → `585d2cddb638e5ca0cb4310e64b1e7313e05246ba5cdf856ee85d7a5946ae8c8`

— Betty

#### joan — 2026-07-23T22:42:15.563Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-948
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1. Horizontal Summary / Analysis / Artifacts; Summary default | Stages 1, 4 |
| 2. Summary tab section bodies | N/A — boundary (AST-949); Stage 1–2 chrome only (`report_summary_sections` + empty `ReportSectionList`) |
| 3. Analysis JD/DO/GET/LIKE sections; JD default expanded | N/A — body content AST-950; Stage 1 labels + Stage 4 empty section chrome / JD default expand seed |
| 4. Grade-icon + confidence header rows | N/A — boundary (AST-950) |
| 5. Phase upshot above rubric | N/A — boundary (AST-950) |
| 6. Artifacts empty → Generate | N/A — body/layout AST-951; Stage 4 parks Generate/Cancel on Artifacts `leading` strip to avoid header regression |
| 7. Generating… + Cancel in BUILD_ARTIFACTS | N/A — AST-951; Stage 4 preserves existing primary-action POST / in-flight / cancel behavior on strip |
| 8. Editable artifact sections | N/A — boundary (AST-951); Stage 4 empty artifact section chrome only |
| 9. Sticky header deeplinks, copy, Print Resume/Cover | Stages 3, 4 |
| 10. Graceful empty states for missing upshot/partial data | N/A — body empty states AST-949/950/951 |
| 11. List row-click + Skip unchanged | Stage 4 (explicitly no `JobsRecommended.tsx` edits) |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Manifest top tabs + section chrome defs | Purpose / Functional scope (three top tabs; config-driven tab/section labels); child AC1 |
| 2 `ReportSectionList` + CSS | Functional scope (collapsible section chrome; sticky header+tabs stack) |
| 3 Sticky header rewrite | Functional scope Modal header; child AC2; Boundaries (no Preview Materials) |
| 4 Modal shell wire + Artifacts action strip | Child AC1–3; parent “must not break Generate/Cancel”; Boundaries (no section bodies) |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | Plan leaves tests to Betty; no engineer merge-tests work |
| orch.git.commit-vocabulary | conforms | Plan does not invent commit subjects; build will use ticket slug |
| orch.git.flow-direction-inviolable | conforms | Publish ref is child `sub/AST-858/…` under parent ftr |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table topology |
| orch.git.merge-on-checkout | conforms | No contrary merge instructions |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite/force guidance |
| orch.git.no-dev-agent-branches | conforms | Uses authoritative sub ref, not Linear gitBranchName |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-858 only |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | No product ambiguity; open questions none; decisions documented in plan |
| orch.pipeline.plan-is-bible | conforms | Stages concrete enough to execute without improvisation |
| orch.pipeline.project-scoped-queues | conforms | Interface project child; no queue misuse |
| orch.pipeline.status-gates-skill-entry | conforms | Validate at Plan Ready with Joan assignee |
| orch.roles.archie-approves-statutes | conforms | Plan does not amend canon/statutes |
| orch.roles.betty-owns-test-tree | conforms | Explicit QA note; engineer does not touch tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Katherine; Joan validates then returns |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign to Katherine on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned-path instructions |
| astral.agent.confidence-bounds | conforms | config.py touch is manifest tabs only; no confidence math |
| astral.config.config-source-of-truth | needs-discussion | Top tabs + summary `default_expanded` in config; Analysis/Artifacts expand defaults still React-mapped in Stage 4 |
| astral.config.pass-threshold-vs-score-floor | conforms | No score_floor / pass_threshold edits |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env literals introduced |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src + plan; Betty barred correctly |
| astral.layers.import-direction | conforms | UI + utils only; no data/external from React |
| astral.layers.ui-config-driven-business-logic | conforms | Primary actions still from manifest; tab ids from `report_top_tabs` |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new API endpoints |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging changes |
| astral.standards.debug-contract-gated | conforms | React/UI path; no backend debug-contract work |
| astral.standards.dry-and-focused-functions | conforms | Shared `ReportSectionList` + `artifactHasContent` reuse |
| astral.standards.in-scope-only | conforms | Bodies deferred to siblings; MaterialsPreview/SideTabPanel not deleted (other screens) |
| astral.standards.logging-via-utils | conforms | No new logging paths |
| astral.standards.no-cross-contamination | conforms | Stays in utils config + ui frontend |
| astral.standards.no-hardcoded-sets | conforms | Tab/section id sets sourced from config lists; no new state enums |
| astral.standards.public-then-helpers | conforms | New component API is small and focused |
| astral.standards.utils-data-late-import-only | conforms | config.py only; no utils→data import |
| astral.state.job-prior-states-enforced | conforms | No JOB_STATES / transition edits |
| astral.ui.frontend-file-placement | conforms | New component flat under `components/`; styles in `App.css` |
| astral.ui.naming-conventions | conforms | PascalCase component; existing CSS class patterns |
| astral.ui.single-gunicorn-worker | conforms | No worker/deploy config changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.do-task-delegation — layers/paths (core) miss plan ui+utils
- astral.agent.grade-vector-validation — layers/paths (core) miss
- astral.batch.batch-id-first — layers/paths (core/data) miss
- astral.batch.batch-id-format — layers/paths (core/data) miss
- astral.batch.claim-process-release — layers/paths (core/data) miss
- astral.batch.entity-agent-responses-latest-only — layers/paths (core/data) miss
- astral.debug.no-repo-root-artifacts-dir — paths (artifacts/spikes) miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers docs miss (plan already published; Files Changed has no docs row)
- astral.git.engineer-test-tree-ban — paths (tests/bible) miss
- astral.layers.core-vs-external-bright-line — layers/paths (core/external) miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths (scripts) miss
- astral.patterns.coat-check-never-store-empty — layers/paths (core) miss
- astral.patterns.render-verdict-orchestrates-consult — layers/paths (core) miss
- astral.standards.database-header-inventory — layers/paths (data) miss
- astral.state.core-decides-transitions — layers/paths (core/data) miss
- astral.state.no-daisy-chain-in-run — layers/paths (core) miss

## Findings

### discuss
1. **Location:** Stage 4 Analysis/Artifacts `default_expanded` mapping; Stage 1 summary sections already carry `default_expanded` in config.
   **Finding:** Analysis JD expand (`tab_id === "phase_jd"`) and Artifacts all-collapsed are React-side seeds while Summary defaults live in config — mild config-source inconsistency with parent “section … follow config/API manifests.”
   **Recommendation:** Optionally add `default_expanded` on `JOBS_RECOMMENDED_REPORT_PHASE_TABS` / `JOBS_RECOMMENDED_ARTIFACT_TABS` (or a shared section shape) and map 1:1 in React. Non-blocking if Katherine keeps the Stage 4 seed as written.

### acceptable
1. Parking Generate/Cancel on Artifacts `leading` until AST-951 is the right bridge so header chrome AC does not break parent “must not break Generate/Cancel.”
2. Empty section bodies (and always-on Artifacts section chrome) are intentional shell; AST-951 owns empty-vs-populated Generate-only layout.

**Self-assessment:** Scope / Conf high / Risk Medium — honest and specific. No `!!-NONE`.

— Joan
context_tokens≈48000

#### katherine — 2026-07-23T22:34:05.354Z
Plan: [`docs/features/interface/ast-948-modal-shell-horizontal-tabs-sticky-header.md`](https://github.com/susansomerset/astral/blob/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header/docs/features/interface/ast-948-modal-shell-horizontal-tabs-sticky-header.md) on **`origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`** @ `3aa9838`.

**Scope — Single-Component:** Config manifest slice plus Recommended Job Report modal chrome (`JobAnalysisReportModal`, header, new `ReportSectionList`, CSS); no core/data/dispatch changes.

**Conf — high:** Reuses shipped `TabBar`, `CollapsiblePanel`, `useSectionExpandPolicy`, AST-605 `/candidate/resume|cover/<job_id>` routes, and existing primary-action helpers; sibling body boundaries (AST-949/950/951) are explicit.

**Risk — Medium:** Temporary empty tab bodies until siblings land, and Generate/Cancel move from header to Artifacts strip; wrong wiring would regress Recommended triage UX even though list Skip/row-click stay untouched.

---

# Modal shell, horizontal tabs, sticky header (Redesign Recommended Job Modal)

**Linear:** [AST-948](https://linear.app/astralcareermatch/issue/AST-948/modal-shell-horizontal-tabs-sticky-header-redesign-recommended-job)  
**Parent:** [AST-858 — Redesign Recommended Job Modal](https://linear.app/astralcareermatch/issue/AST-858/redesign-recommended-job-modal)  
**Publish ref (origin):** `sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`  
**Parent integration ref:** `ftr/AST-858-redesign-recommended-job-modal`

Rebuild the Recommended Job Report chrome: replace the left `SideTabPanel` rail with three horizontal top tabs (**Summary** / **Analysis** / **Artifacts**, Summary default), introduce a shared collapsible section-list pattern (empty bodies for siblings), and restyle the sticky header for deeplinked job title + company, Copy Application Email / Copy LinkedIn Profile, and Print Resume / Print Cover Letter (AST-605 HTML routes in a new tab). List row-click entry and Skip stay unchanged. Does **not** implement Summary / Analysis / Artifacts section bodies (AST-949 / AST-950 / AST-951) and does **not** change consult scoring, dispatch, or the artifact pipeline.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Replace `report_fixed_tabs` with `report_top_tabs`; add `report_summary_sections`; update phase/artifact `nav_label`s for section chrome; expose all via `build_state_ui_manifest` | utils |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Type manifest: `report_top_tabs`, `report_summary_sections`; drop `report_fixed_tabs` | ui |
| `src/ui/frontend/src/components/ReportSectionList.tsx` | **New** — Expand-All `CollapsiblePanel` stack driven by section defs + `renderSection` | ui |
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Sticky header: deeplinked job title + company; Copy Application Email / LinkedIn; Print Resume / Cover; remove Preview Materials + primary-action chrome | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Horizontal `TabBar` shell; wire `ReportSectionList` per top tab with empty bodies; park Generate/Cancel in Artifacts action strip; drop `SideTabPanel` + `MaterialsPreviewModal` usage | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Helpers for print visibility / top-tab ids; drop or stop using `materialsPreviewVisible` from the modal path | ui |
| `src/ui/frontend/src/App.css` | Styles for horizontal report tabs + section stack under recommended-report; adjust header title link | ui |

**Out of scope (this ticket):** section body content for Summary / Analysis / Artifacts (siblings); deleting `MaterialsPreviewModal.tsx` or `SideTabPanel.tsx` (other screens still use them); `JobsRecommended.tsx` list/Skip behavior; any edit under `tests/` or `docs/test-bible/**` (Betty at Code Complete).

**QA note (Betty — not engineer commits):** Manifest + frontend tests that still assert left-rail `report_fixed_tabs` / `.side-tab-list` for this modal must be updated for horizontal Summary/Analysis/Artifacts and sticky header print/copy controls.

---

## Stage 1: Manifest — top tabs + section chrome defs

**Done when:** `GET /api/state_ui_manifest` → `jobs.recommended` exposes `report_top_tabs` (Summary / Analysis / Artifacts), `report_summary_sections` (five section rows with `default_expanded`), and updated phase/artifact `nav_label`s for section headers. `report_fixed_tabs` is gone.

1. In `src/utils/config.py`, near `JOBS_RECOMMENDED_REPORT_PHASE_TABS` / `JOBS_RECOMMENDED_ARTIFACT_TABS`:

   - Add:

     ```python
     JOBS_RECOMMENDED_REPORT_TOP_TABS = [
         {"tab_id": "summary", "nav_label": "Summary"},
         {"tab_id": "analysis", "nav_label": "Analysis"},
         {"tab_id": "artifacts", "nav_label": "Artifacts"},
     ]

     JOBS_RECOMMENDED_REPORT_SUMMARY_SECTIONS = [
         {"section_id": "job_summary", "nav_label": "Job Summary", "default_expanded": True},
         {"section_id": "company_upshot", "nav_label": "Company Upshot", "default_expanded": True},
         {"section_id": "caveats", "nav_label": "Noteworthy Caveats", "default_expanded": True},
         {"section_id": "questions", "nav_label": "Questions to Ask", "default_expanded": True},
         {"section_id": "raw_jd", "nav_label": "Raw Job Description", "default_expanded": False},
     ]
     ```

   - Update `JOBS_RECOMMENDED_REPORT_PHASE_TABS` `nav_label` values to exactly: `"JD Analysis"`, `"DO Analysis"`, `"GET Analysis"`, `"LIKE Analysis"` (keep `tab_id` / `grades_field` / `take_key` unchanged — these rows are now **Analysis tab sections**, not top tabs).

   - Update `JOBS_RECOMMENDED_ARTIFACT_TABS` `nav_label` values to exactly: `"Job Resume"`, `"Cover Letter"`, `"Application Questions"` (keep `tab_id` / `artifact_key` / `shapes_key` / `use_resume_structure`).

2. In `build_state_ui_manifest()` under `jobs.recommended`:

   - Remove the inline `report_fixed_tabs` list.
   - Add `"report_top_tabs": list(JOBS_RECOMMENDED_REPORT_TOP_TABS)`.
   - Add `"report_summary_sections": list(JOBS_RECOMMENDED_REPORT_SUMMARY_SECTIONS)`.
   - Keep `"report_phase_tabs"` and `"report_artifact_tabs"` as today (same list sources; labels updated above).

3. In `src/ui/frontend/src/contexts/StateUiContext.tsx`, update `jobs.recommended` types:

   - Remove `report_fixed_tabs`.
   - Add `report_top_tabs?: Array<{ tab_id: string; nav_label: string }>`.
   - Add `report_summary_sections?: Array<{ section_id: string; nav_label: string; default_expanded: boolean }>`.
   - Leave `report_phase_tabs` / `report_artifact_tabs` types unchanged.

⚠️ **Decision:** Keep `report_phase_tabs` / `report_artifact_tabs` key names (semantic shift: top-level tabs → sections inside Analysis / Artifacts). Avoids renaming churn for sibling plans and existing helpers; only `report_fixed_tabs` → `report_top_tabs` is a breaking rename.

---

## Stage 2: Shared `ReportSectionList` + CSS chrome

**Done when:** `ReportSectionList` compiles; App.css has recommended-report horizontal-tab + section-stack rules. No modal behavior change yet (component unused until Stage 3).

1. Create `src/ui/frontend/src/components/ReportSectionList.tsx`:

   ```tsx
   export type ReportSectionDef = {
     section_id: string
     nav_label: string
     default_expanded: boolean
   }

   export type ReportSectionListProps = {
     sections: readonly ReportSectionDef[]
     /** Body for one section — AST-948 passes empty/null; siblings replace. */
     renderSection: (sectionId: string) => ReactNode
     /** Optional slot above the stack (e.g. Artifacts Generate/Cancel strip). */
     leading?: ReactNode
   }
   ```

   Implementation requirements:

   - Import `CollapsiblePanel` and `useSectionExpandPolicy`.
   - Call `useSectionExpandPolicy({ expandAll: true, sectionKeys })` where `sectionKeys = sections.map(s => s.section_id)`.
   - On mount and whenever `sectionKeys` / `default_expanded` set changes, `setExpandedKeys(new Set(sections.filter(s => s.default_expanded).map(s => s.section_id)))`.
   - Render `leading` (if any), then one `CollapsiblePanel` per section: `label={nav_label}`, controlled `expanded={isExpanded(section_id)}`, `onExpandedChange={(next) => onExpandedChange(section_id, next)}`, children = `renderSection(section_id)`.
   - Do **not** render `SectionExpandChrome` (no Expand all / Collapse all chrome in this modal).
   - Do **not** put grade/metadata slots here — AST-950 owns Analysis header metadata via `CollapsiblePanel` `metadata` later; AST-948 leaves `metadata` / `actions` unset.

2. In `src/ui/frontend/src/App.css` (recommended-report block / TOC):

   - Add rules so `.recommended-report-body` hosts a horizontal tab strip (reuse existing `.tabbed-ta-bar` / `.tabbed-ta-tab` visually, optionally scoped under `.recommended-report-tabs`) and a scrollable `.recommended-report-tab-pane` below it.
   - Ensure sticky stack works: header sticky at top; tab bar sticky directly under the header (`position: sticky` with an appropriate `top` matching header height, or wrap header+tabs in one sticky chrome container). Section list scrolls inside `.recommended-report-tab-pane` (`overflow: auto`, `min-height: 0`, flex child of the shell).
   - Add `.recommended-report-title-link` for the deeplinked job title (inherit title weight/size from `.recommended-report-title`; accent/underline only on hover — match existing `.recommended-report-company-link` density).
   - Remove or stop relying on `.recommended-report-body .side-tab-panel` for this modal (leave global `.side-tab-panel` rules intact for other screens).

⚠️ **Decision:** Expand All (`expandAll: true`) matches parent AC that sections open/close independently. Seed from `default_expanded` so first paint matches parent defaults (e.g. Raw JD collapsed).

---

## Stage 3: Sticky header — deeplinks, copy, print

**Done when:** Header shows deeplinked job title (apply URL), deeplinked company (homepage when known), **Copy Application Email**, **Copy LinkedIn Profile**, and **Print Resume** / **Print Cover Letter** only when those artifacts exist. Preview Materials and header primary-action buttons are gone from this component.

1. Rewrite `RecommendedJobReportHeader` props to:

   ```tsx
   interface Props {
     jobTitle: string
     jobLink: string | null
     companyName: string
     companyWebsite: string | null
     applicationEmail: string | null  // raw email; parent applies plus-tag on copy
     linkedInUrl: string | null
     copyFeedback?: string | null
     onCopyApplicationEmail?: () => void
     onCopyLinkedIn?: () => void
     showPrintResume: boolean
     showPrintCover: boolean
     onPrintResume?: () => void
     onPrintCover?: () => void
   }
   ```

2. Layout (single sticky header card, no state chip, no Generate/Cancel/Apply, no Preview Materials):

   - Row 1: Job title — if `jobLink` trim nonempty, `<a href={jobLink} target="_blank" rel="noopener noreferrer" className="recommended-report-title-link">`; else `<span className="recommended-report-title">`. Display text = `jobTitle` (fallback already resolved by parent to company or `"Recommended Job Report"`).
   - Same row or immediately under: company — website link when known (existing pattern), else plain span.
   - Row 2: Copy buttons — render **Copy Application Email** only when `applicationEmail` nonempty; **Copy LinkedIn Profile** only when `linkedInUrl` nonempty. Exact visible labels. Show `copyFeedback` beside them when set.
   - Row 3: Print buttons — **Print Resume** when `showPrintResume`; **Print Cover Letter** when `showPrintCover`. Use existing `modal-btn cancel` (or secondary) class; `type="button"`.

3. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`:

   - Add `printResumeVisible(artifacts)` → `artifactHasContent(artifacts, "resume_content")`.
   - Add `printCoverVisible(artifacts)` → `artifactHasContent(artifacts, "cover_letter")`.
   - Stop calling `materialsPreviewVisible` from `JobAnalysisReportModal` (function may remain exported for now — do not delete unless nothing else imports it; if unused after this ticket, leave it for Betty/cleanup rather than expanding scope).

4. Print handlers (owned by modal, passed into header): `window.open(`/candidate/resume/${encodeURIComponent(jobId)}`, "_blank", "noopener,noreferrer")` and `/candidate/cover/...` respectively. Do **not** open `MaterialsPreviewModal`. Do **not** add print for application questions.

⚠️ **Decision:** Application email = `candidate_data.profile.contact_email` if nonempty, else `reply_email` if nonempty, else null. Plus-tag copy continues via existing `emailWithJobPlusTag` + `external_job_id` / `astral_job_id` logic in the modal. LinkedIn = `profile.linkedin_url` only — drop GitHub / extra profile copy chips from this header (AC names two copy controls).

---

## Stage 4: Wire modal shell — horizontal tabs, empty sections, Artifacts action strip

**Done when:** Opening a Recommended job shows horizontal **Summary** / **Analysis** / **Artifacts** (Summary default); each tab shows the configured collapsible section chrome with empty bodies; sticky header matches Stage 3; Generate/Cancel remain reachable on the Artifacts tab; `SideTabPanel` and `MaterialsPreviewModal` are unused by this modal; `JobsRecommended` list entry/Skip untouched.

1. In `JobAnalysisReportModal.tsx`:

   - Remove imports/usage of `SideTabPanel`, `MaterialsPreviewModal`, `AgentAnalysisHeader`, `ArtifactEditor`, and phase-tab grade-dot label helpers used only for the old rail (`renderTabLabel` / `buildPhaseTabGradeDots` / `formatPhaseTabNavLabel` / `jobGradesForField` / structure-fetch effect for resume editor). Keep `parseAnalysisUpshot` only if still needed — for AST-948 empty bodies it is **not** needed; remove upshot-driven pane rendering.
   - Import `TabBar` from `./TabbedTextArea` and `ReportSectionList`.
   - Modal `title` prop: use `job?.company || "Recommended Job Report"` (job title lives in sticky header only — avoid duplicate titles).
   - Build top tabs from `manifest.jobs.recommended.report_top_tabs` (fallback empty → show `recommended-report-empty` “Report layout unavailable…”).
   - Local state `activeTopTab` initialized to `"summary"`; when tabs load, if current id missing from list, reset to first tab (Summary).
   - Persist tab selection while the modal is open (do not reset `activeTopTab` on `load()` refresh). Reset to `"summary"` when `jobId` changes (new open).
   - Shell structure:

     ```tsx
     <div className="recommended-report-shell">
       <RecommendedJobReportHeader … />
       <div className="recommended-report-body">
         <div className="recommended-report-tabs">
           <TabBar tabs={…} active={activeTopTab} onChange={setActiveTopTab} />
         </div>
         <div className="recommended-report-tab-pane">
           {activeTopTab === "summary" && (
             <ReportSectionList
               sections={summarySections /* map manifest rows to ReportSectionDef */}
               renderSection={() => null}
             />
           )}
           {activeTopTab === "analysis" && (
             <ReportSectionList
               sections={analysisSections /* from report_phase_tabs: section_id=tab_id, default_expanded = (tab_id === "phase_jd") */}
               renderSection={() => null}
             />
           )}
           {activeTopTab === "artifacts" && (
             <ReportSectionList
               leading={/* primary actions strip — see below */}
               sections={artifactSections /* from report_artifact_tabs; default_expanded false for all */}
               renderSection={() => null}
             />
           )}
         </div>
       </div>
     </div>
     ```

   - **Analysis default expand:** only `phase_jd` → `default_expanded: true`; other phase sections `false` (parent: JD Analysis expanded by default).
   - **Artifacts sections:** always render all three section chrome rows from manifest (do **not** gate on `artifactHasContent` — visibility of editors is AST-951). Bodies stay empty.
   - **Artifacts `leading` action strip:** using existing `primaryActionsForState(manifest, job.state)`:
     - Render every action **except** `action_key === "apply"` (apply is the job-title deeplink).
     - Keep Generate / Cancel POST behavior, busy/`in-flight` class, and AST-591 close-on-generate/cancel behavior exactly as today.
     - If no remaining actions, omit `leading`.
   - Wire header props from Stage 3 (print flags via new helpers; email/LinkedIn from profile; copy handlers).
   - Do **not** edit `JobsRecommended.tsx`.

2. Confirm compile: `cd src/ui/frontend && npx tsc -b --noEmit` (and Python syntax for config if touched). Fix only type errors caused by this plan’s files.

⚠️ **Decision:** Empty section bodies are intentional — AST-949/950/951 own content. Parking Generate/Cancel on the Artifacts tab leading strip (not header) prevents Generate regression before AST-951 while matching the redesign’s header AC. Apply is not duplicated as a button.

⚠️ **Decision:** Always show all three Artifacts section headers in the shell (empty). AST-951 will decide empty vs populated body / Generate-only layout; shell only establishes the section list pattern.

---

## Self-Assessment

**Scope:** Single-Component — config manifest slice plus Recommended Job Report modal chrome (`JobAnalysisReportModal`, header, new `ReportSectionList`, CSS); no core/data/dispatch changes.

**Conf:** high — reuses shipped `TabBar`, `CollapsiblePanel`, `useSectionExpandPolicy`, AST-605 `/candidate/resume|cover/<job_id>` routes, and existing primary-action helpers; scope boundaries vs AST-949/950/951 are explicit.

**Risk:** Medium — temporary empty tab bodies until siblings land, and Generate/Cancel move from header to Artifacts strip; wrong wiring would regress Recommended triage UX (open/copy/print/generate) even though list Skip/row-click are untouched.

---

## Code rules check

- **§1.3 DRY:** Shared section stack is one `ReportSectionList`; print visibility reuses `artifactHasContent`; no duplicated expand logic outside `useSectionExpandPolicy`.
- **§1.4 / §2.1:** Top tabs + summary section defaults live in `config.py` / manifest — not hardcoded tab id arrays in React beyond reading the manifest.
- **§2.4 / §2.6:** N/A — no batch or state-machine changes.
- **§3.3:** UI edits stay in `src/ui/frontend` + `config.py` manifest; no `data`/`external` imports from React.
- **§3.5:** New component flat under `components/`; styles only in `App.css`.
- **Tests / bible:** Not touched by engineer (Betty).

---

## Review (build)

**Built:** `origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header` @ `00a27e958be16afd6f78c43c20f542beb19188a8`

Stages 1–4: `report_top_tabs` / `report_summary_sections` manifest; `ReportSectionList` Expand-All stack; sticky header deeplinks + Copy Application Email / LinkedIn + Print Resume/Cover; horizontal Summary/Analysis/Artifacts shell with empty section bodies; Generate/Cancel parked on Artifacts `leading` strip. Tests deferred to Betty.

---

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-948
**Publish ref:** `b4c92015195e341ce05b4ffac7cfafd9492c8000` (`origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`)
**Overall:** DISCUSS

### What’s solid

- Stages 1–4 land on tip: manifest `report_top_tabs` / `report_summary_sections`, `ReportSectionList`, sticky chrome + horizontal `TabBar`, header deeplinks/copy/print, Artifacts `leading` Generate/Cancel, empty section bodies for siblings.
- Cancel close-on-success uses `action_key === "cancel_build"` (matches config); corrects prior `cancel_artifact_build` mismatch on `origin/dev`.
- Betty `test` + `merge-tests` only under tests/bible; engineer commits stay `code`/`docs`.
- Cross-ticket boundaries respected (no Summary/Analysis/Artifacts bodies; no `JobsRecommended` edits).

### Issues / findings

**discuss**

1. **astral.config.config-source-of-truth** — Analysis `default_expanded` (`phase_jd`) and Artifacts all-collapsed remain React-side seeds while Summary defaults live in config (Joan plan-time discuss; still true on tip). Non-blocking vs approved Stage 4.
2. **C4 straggler** — Joan excluded `astral.debug.spikes-under-debug-dir`; code diff includes `docs/features/**` so statute is in-scope. Score: conforms (plan file, not a spike).
3. **C4 straggler** — Joan excluded `astral.docs.features-single-file-per-ticket`; features path present. Score: conforms (single ticket file).
4. **C4 straggler** — Joan excluded `astral.git.engineer-test-tree-ban`; tests/bible in diff via Betty. Score: conforms (engineer did not author test-tree commits).

**fix-now:** none

### Recommended actions

- Optional: lift Analysis/Artifacts `default_expanded` into config section shape (Joan recommendation) on a sibling or small follow-up — not required to clear this review.
- No product fix required for C4 stragglers.

---

## Resolution

**Date:** 2026-07-23  
**Publish tip before resolve:** `dedf666` (`docs(AST-948): Radia review — findings` on `origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`)

| Finding | Action |
| -- | -- |
| fix-now | none |
| discuss #1 — Analysis/Artifacts `default_expanded` React seeds vs config SoT | **Deferred** — Radia Recommended actions: optional lift into config on sibling/follow-up; **not required to clear this review**. Stage 4 seed (`phase_jd` / Artifacts collapsed) stays as approved plan. |
| discuss #2–4 — C4 statute stragglers | **No action** — Radia scored conforms; informational only. |

No product code changes in resolve. Proceeding to User Testing after §9a dry-run.
