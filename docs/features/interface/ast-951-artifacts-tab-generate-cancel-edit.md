<!-- linear-archive: AST-951 archived 2026-08-05 -->

## Linear archive (AST-951)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-951/artifacts-tab-generate-cancel-edit-redesign-recommended-job-modal  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-858 — Redesign Recommended Job Modal  
**Blocked by / blocks / related:** parent: AST-858

### Description

## What this implements

Artifacts tab: empty state shows **Generate Artifacts**; during **BUILD_ARTIFACTS** / daisy-chain show yellow **Generating…** with **Cancel** beside it; when content exists show collapsible editable **Job Resume**, **Cover Letter**, **Application Questions** (resume mirrors candidate resume structure; saves to `job_data`). Reset/Regenerate out of scope.

## Acceptance criteria

6. Artifacts tab with no artifact content shows **Generate Artifacts**; clicking it starts the build using today's server action.
7. While the job is in **BUILD_ARTIFACTS** (including compound states), the generate control is yellow/in-flight, labeled **Generating…**, with **Cancel** beside it; Cancel returns the job to **RECOMMENDED** as today.
8. When artifact blobs exist, Artifacts tab shows **Job Resume**, **Cover Letter**, and **Application Questions** with editable content; resume sections mirror candidate resume structure; edits save to `job_data` and survive reload.

## Boundaries

* Does **not** own Summary/Analysis bodies or header Print buttons (siblings).
* Does **not** add Reset/Regenerate.

## Notes for planning

Blocked by AST-948 shell. Reuse ArtifactEditor + AST-645 in-flight styling; keep Generate/Cancel on Artifacts tab (not header Apply).

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-858-redesign-recommended-job-modal`, child `sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-23T23:29:39.775Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-951
**Publish ref:** `e6f32a3616629b907284bf28527246ffa15a6228` (`origin/sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | no confidence math; UI Artifacts only |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths (core) miss diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths (core) miss diff |
| astral.batch.batch-id-first | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.batch-id-format | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.claim-process-release | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.config.config-source-of-truth | scoped | needs-discussion | action labels/paths manifest-driven; compound in-progress + Cancel fallback still React-side (Joan discuss / plan Decision) |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | no pass_threshold / score_floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths (artifacts/spikes) miss diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | features plans only; not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one AST-951 features file (+ AST-948 on tip) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test/merge-tests stay off src/features |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer code/docs/plan only; tests via Betty |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths (core/external) miss diff |
| astral.layers.import-direction | scoped | conforms | frontend-only AST-951 delta (+ inherited utils) |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths (scripts) miss diff |
| astral.layers.ui-config-driven-business-logic | scoped | needs-discussion | BUILD_ARTIFACTS. prefix + base-state action fallback is frontend state logic; approved Stage 1 Decision |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths (core) miss diff |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths (core) miss diff |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new endpoints; existing generate/cancel POSTs |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer logging |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths (data) miss diff |
| astral.standards.debug-contract-gated | scoped | conforms | React-only; no debug-contract work |
| astral.standards.dry-and-focused-functions | scoped | conforms | shared helpers; reuses ArtifactEditor / artifactHasContent |
| astral.standards.in-scope-only | scoped | conforms | Artifacts tab only; supersedes AST-948 empty section shell for this tab |
| astral.standards.logging-via-utils | scoped | conforms | no new logging |
| astral.standards.no-cross-contamination | scoped | conforms | ui frontend for AST-951 delta |
| astral.standards.no-hardcoded-sets | scoped | needs-discussion | compound-state string/prefix in React; action_key checks match existing UI pattern / plan Decision |
| astral.standards.public-then-helpers | scoped | conforms | named exports in lib |
| astral.standards.utils-data-late-import-only | scoped | conforms | no utils→data import on tip |
| astral.state.core-decides-transitions | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.state.job-prior-states-enforced | scoped | conforms | no JOB_STATES / prior_states edits |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths (core) miss diff |
| astral.ui.frontend-file-placement | scoped | conforms | flat components + lib; no new nested dirs |
| astral.ui.naming-conventions | scoped | conforms | existing class/label patterns; exact Generating… |
| astral.ui.single-gunicorn-worker | scoped | conforms | no worker/deploy changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one merge-tests(AST-951) onto sub |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests/plan vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | child sub under parent ftr |
| orch.git.ftr-sub-topology | universal | conforms | sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit |
| orch.git.merge-on-checkout | universal | conforms | tip includes merge of ftr + AST-948 lineage |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rewrite/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | authoritative publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in astral-AST-858 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | compound-state Decision explicit; ERROR excluded from chrome |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 implemented as written |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Interface; Tests Passed gate |
| orch.pipeline.status-gates-skill-entry | universal | conforms | entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes amendments |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible via Betty |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | role path bans respected |

## Pattern conformance

none cited

## Plan adherence

AST-951 delta (`e0c6344`) adds Stage 1 helpers and Stage 2 exclusive layouts A/B/C; restores resume-structure fetch + ArtifactEditor; close-on-action keys `generate_artifacts` / `cancel_build`. Self-Assessment Single-Component matches. No Reset/Regenerate. Summary/Analysis bodies not owned on tip.

## Findings

### discuss

1. **Compound-state action resolve (Joan #1, still true)** — `isArtifactsBuildInProgress` / `artifactsTabPrimaryActions` keep `BUILD_ARTIFACTS` / `BUILD_ARTIFACTS.*` detection and base-state Cancel fallback in React. Scores needs-discussion on `astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, and `astral.standards.no-hardcoded-sets`. Non-blocking vs approved Stage 1 Decision; optional later manifest/constants lift.
2. **C4 stragglers** — Joan excluded; tip includes AST-948 utils/docs/tests so in-scope; all score **conforms**: `astral.agent.confidence-bounds`, `astral.config.pass-threshold-vs-score-floor`, `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.standards.utils-data-late-import-only`, `astral.state.job-prior-states-enforced`.

### fix-now

none

### What’s solid

Empty Generate / in-flight Generating…+Cancel (incl. compound hops) / populated editors; ERROR_BUILD_ARTIFACTS not Generating chrome; cancel_build close path; sibling boundaries held.

### Notes

Plan-rubric verdict attached (Joan APPROVED). Docs append: `docs(AST-951): Radia review — findings`.

context_tokens≈45000

#### betty — 2026-07-23T23:23:19.024Z
## QA test manifest — AST-951

**Publish:** `origin/sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit` @ `44a0bb2`
**Betty commit:** `origin/tests` `2d99e18` → `merge-tests(AST-951): origin/tests 2d99e18039dc38aaa1129038db44a939b5a5c2b4`

### Coverage

1. **Artifacts layouts** — `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` (`JobAnalysisReportModal — AST-951 Artifacts tab layouts`)
   - Compound hop **Generating…** + **Cancel**
   - Cancel POST `cancel_artifact_build` closes modal (`cancel_build` key)
   - `ERROR_BUILD_ARTIFACTS` is not Generating… chrome
   - Populated editable Job Resume (structure fetch); no Generate strip; no Application Questions without blob
   - No Reset/Regenerate
2. **Revised shell Artifacts cases** (same file, AST-948 describe) — empty Generate-only (no section chrome); AST-645 in-flight keeps **Generate Artifacts** label; BUILD_ARTIFACTS → Generating…+Cancel
3. **Helpers** — `tests/component/frontend/lib/test_recommendedJobReport.test.tsx` (`AST-951 Artifacts helpers`)

### Sibling note

Use `--testNamePattern="AST-951|AST-948"` so Summary/Analysis sibling body asserts are not required on this tip.

### Narrowed run

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  --testNamePattern="AST-951|AST-948"
```

### Bible shasums (`origin/sub/...`)

- `docs/test-bible/frontend/components.md` → `53e9092547ee069a65c0670810ff3ae949ca534ba34e1a9a192c494738300caf`
- `docs/test-bible/frontend/lib.md` → `100287a4db063db01088bea5442ba8f61f346e96fa3bab019eab2aaa2db55cee`

— Betty

#### joan — 2026-07-23T22:47:41.127Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-951
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1. Horizontal top tabs; Summary default | N/A — boundary (AST-948) |
| 2. Summary tab sections | N/A — boundary (AST-949) |
| 3–5. Analysis sections / grades / takes | N/A — boundary (AST-950) |
| 6. Empty Artifacts → Generate Artifacts (today’s server action) | Stages 1–2 layout B |
| 7. BUILD_ARTIFACTS (+ compound): yellow Generating… + Cancel → RECOMMENDED | Stages 1–2 layout A + `artifactsTabPrimaryActions` fallback |
| 8. Populated editable Job Resume / Cover / Application Questions; save `job_data` | Stage 2 layout C (`ArtifactEditor` + resume structure fetch) |
| 9. Sticky header Print / deeplinks / copy | N/A — boundary (AST-948) |
| 10. Graceful empty / partial data | Stage 2 gates (empty vs populated vs in-flight; no crash paths) |
| 11. List row-click + Skip | N/A — out of scope |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| Prerequisite gate | blockedBy AST-948 Artifacts shell / `leading` / `report_artifact_tabs` |
| 1 In-progress + action-resolve helpers | Parent AC7 compound/daisy-chain; Functional scope Artifacts empty/in-progress |
| 2 Empty / in-flight / populated layouts + close-on-action fix | Parent AC6–8; Boundaries (no Reset/Regenerate); must-not-break Generate/Cancel |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No engineer test-merge work |
| orch.git.commit-vocabulary | conforms | No contrary commit guidance |
| orch.git.flow-direction-inviolable | conforms | Child sub under parent ftr |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Prerequisite merges + AST-948 |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite/force guidance |
| orch.git.no-dev-agent-branches | conforms | Authoritative sub publish ref |
| orch.git.one-epic-worktree-per-parent | conforms | Epic AST-858 worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Compound-state Decision explicit; no Archie product ambiguity |
| orch.pipeline.plan-is-bible | conforms | Three exclusive layouts + named helpers; stop if shell missing |
| orch.pipeline.project-scoped-queues | conforms | Interface child only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready + Joan assignee |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | Betty QA note |
| orch.roles.chuckles-never-ticket-assignee | conforms | Return to Katherine |
| orch.roles.engineer-assignee-through-resolve | conforms | Katherine implementer |
| orch.roles.pre-commit-path-bans | conforms | No banned-path instructions |
| astral.config.config-source-of-truth | needs-discussion | Action labels/paths stay manifest-driven; compound in-progress prefix + action fallback duplicated in React vs config constants |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.import-direction | conforms | Frontend-only; existing POSTs |
| astral.layers.ui-config-driven-business-logic | needs-discussion | `BUILD_ARTIFACTS.` prefix + fallback to base-state actions is frontend state logic; Decision documents why (manifest keys base only) |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new endpoints |
| astral.standards.data-raises-caller-logs | conforms | No data-layer changes |
| astral.standards.debug-contract-gated | conforms | React-only |
| astral.standards.dry-and-focused-functions | conforms | Shared helpers; reuses `ArtifactEditor` / `artifactHasContent` |
| astral.standards.in-scope-only | conforms | Artifacts tab only; supersedes AST-948 empty section shell for this tab only |
| astral.standards.logging-via-utils | conforms | No new logging |
| astral.standards.no-cross-contamination | conforms | ui frontend only |
| astral.standards.no-hardcoded-sets | needs-discussion | Same compound-state string/prefix concern; action_key checks match existing UI pattern |
| astral.standards.public-then-helpers | conforms | Named exports in lib |
| astral.ui.frontend-file-placement | conforms | Flat components + lib + optional App.css |
| astral.ui.naming-conventions | conforms | Existing class / label patterns; exact `Generating…` |
| astral.ui.single-gunicorn-worker | conforms | No deploy/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.confidence-bounds — layers/paths miss
- astral.agent.do-task-delegation — layers/paths miss
- astral.agent.grade-vector-validation — layers/paths miss
- astral.batch.batch-id-first — layers/paths miss
- astral.batch.batch-id-format — layers/paths miss
- astral.batch.claim-process-release — layers/paths miss
- astral.batch.entity-agent-responses-latest-only — layers/paths miss
- astral.config.pass-threshold-vs-score-floor — layers/paths miss
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.core-vs-external-bright-line — layers/paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.coat-check-never-store-empty — layers/paths miss
- astral.patterns.render-verdict-orchestrates-consult — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.standards.utils-data-late-import-only — layers/paths miss
- astral.state.core-decides-transitions — layers/paths miss
- astral.state.job-prior-states-enforced — layers/paths miss
- astral.state.no-daisy-chain-in-run — layers/paths miss

## Findings

### discuss
1. **Location:** Stage 1 `isArtifactsBuildInProgress` / `artifactsTabPrimaryActions` Decision.
   **Finding:** Compound-state detection (`BUILD_ARTIFACTS` / `BUILD_ARTIFACTS.*`) and fallback to base-state Cancel actions live in React, while config already owns `BUILD_ARTIFACTS_BASE_STATE`, `LEGACY_BUILD_ARTIFACTS_PREFIX`, and `is_build_artifacts_in_progress`. Parent asks workflow actions to follow manifests, not hardcoded React state machines.
   **Recommendation:** Non-blocking for this ticket (AC7 requires Cancel on daisy-chain; manifest only keys base). Prefer later (or light utils touch) expanding `primary_actions_by_state` for compound labels in `build_state_ui_manifest`, or exposing the in-progress prefix/constants via the existing manifest — not duplicating every hop by hand. Keep excluding `ERROR_BUILD_ARTIFACTS` from Generating… chrome unless product asks otherwise (Python helper treats ERROR as in-progress for cancel eligibility).

### acceptable
1. Superseding AST-948’s always-on empty Artifacts section chrome for empty/in-flight layouts matches AC #6–7.
2. Fixing close-on-cancel to `action_key === "cancel_build"` (not `path_suffix` `cancel_artifact_build`) is a real shipped bug and belongs here.
3. No Reset/Regenerate; populated tab omits Generate — matches Boundaries.

**Self-assessment:** Scope Single-Component / Conf high / Risk Medium — honest about compound Cancel and empty-shell AC risk. No `!!-NONE`. No fix-now.

— Joan
context_tokens≈70000

#### katherine — 2026-07-23T22:39:32.572Z
Plan: [`docs/features/interface/ast-951-artifacts-tab-generate-cancel-edit.md`](https://github.com/susansomerset/astral/blob/sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit/docs/features/interface/ast-951-artifacts-tab-generate-cancel-edit.md) on **`origin/sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit`** @ `f6504ea`.

**Scope — Single-Component:** Artifacts tab empty / in-flight / populated layouts plus helpers; reuses `ArtifactEditor` and existing generate/cancel POSTs — no new API.

**Conf — high:** Paths, job persistence, AST-645 `.in-flight`, and `report_artifact_tabs` already ship; ticket re-homes and gates them. Compound-state Cancel fallback is an explicit Decision.

**Risk — Medium:** Missing compound-state action resolve strands daisy-chain jobs without Cancel; empty section shells during Generate would fail AC #6; close-on-cancel must key `cancel_build` (not path_suffix).

---

# Artifacts tab generate, cancel, edit (Redesign Recommended Job Modal)

**Linear:** [AST-951](https://linear.app/astralcareermatch/issue/AST-951/artifacts-tab-generate-cancel-edit-redesign-recommended-job-modal)  
**Parent:** [AST-858 — Redesign Recommended Job Modal](https://linear.app/astralcareermatch/issue/AST-858/redesign-recommended-job-modal)  
**Publish ref (origin):** `sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit`  
**Parent integration ref:** `ftr/AST-858-redesign-recommended-job-modal`  
**Blocked by:** [AST-948](https://linear.app/astralcareermatch/issue/AST-948/modal-shell-horizontal-tabs-sticky-header-redesign-recommended-job) (Artifacts tab shell / `ReportSectionList` `leading` / `report_artifact_tabs`)

Own the Artifacts tab UX: empty → **Generate Artifacts**; in-flight **BUILD_ARTIFACTS** (including daisy-chain / `BUILD_ARTIFACTS.<hop>`) → yellow **Generating…** with **Cancel** beside it; when artifact blobs exist → collapsible editable **Job Resume** / **Cover Letter** / **Application Questions** via existing `ArtifactEditor` + job persistence (saves to `job_data`). No Reset/Regenerate. Does **not** own Summary/Analysis bodies or header Print controls.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit`; `git merge origin/dev`; `git merge origin/ftr/AST-858-redesign-recommended-job-modal`; merge-clean gate.
2. Merge **`origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`** (or rolled-up `origin/ftr/…`) so the Artifacts tab has `ReportSectionList`, optional `leading` action strip, and `report_artifact_tabs` section chrome.
3. If those pieces are missing, **stop** — comment on AST-951; do not rebuild shell/header.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Helpers: build-in-progress state detect; resolve primary actions for base + compound `BUILD_ARTIFACTS.*`; any-artifact / per-key content gates used by the tab | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Artifacts empty / in-flight / populated layouts; wire `ArtifactEditor` bodies; restore resume-structure fetch; fix Generate/Cancel strip labels + close-on-action keys | ui |
| `src/ui/frontend/src/App.css` | Only if Artifacts action strip needs a small flex row class under recommended-report (prefer existing `.recommended-report-header-actions` / `.modal-btn` / `.in-flight`) | ui |

**Out of scope:** new Flask routes; Reset/Regenerate; changing `ArtifactEditor` job-persistence contract; Summary/Analysis (AST-949/950); header Print (AST-948); `tests/` / bible (Betty).

**QA note (Betty):** Empty Generate; in-flight Generating…+Cancel (base + compound state); editable sections with job_data save/reload; Cancel → RECOMMENDED; no Reset/Regenerate.

---

## Stage 1: Artifacts action helpers (in-progress + action resolve)

**Done when:** Helpers exist to detect build-in-progress (including compound states) and to resolve Cancel/Generate actions when `job.state` is `BUILD_ARTIFACTS` or `BUILD_ARTIFACTS.<hop>`.

1. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`, add:

   ```tsx
   /** True for BUILD_ARTIFACTS and legacy daisy-chain BUILD_ARTIFACTS.<hop> (not ERROR_BUILD_ARTIFACTS). */
   export function isArtifactsBuildInProgress(jobState: string): boolean

   /**
    * Primary actions for the Artifacts strip.
    * Looks up manifest.primary_actions_by_state[jobState]; if empty and
    * isArtifactsBuildInProgress(jobState), fall back to actions for "BUILD_ARTIFACTS".
    * Filters out action_key === "apply" (job-title deeplink owns apply).
    */
   export function artifactsTabPrimaryActions(
     manifest: StateUiManifest | null,
     jobState: string,
   ): ReportPrimaryAction[]

   /** True if any report_artifact_tabs artifact_key has content on job artifacts blob. */
   export function anyReportArtifactContent(
     artifacts: unknown,
     artifactTabs: Array<{ artifact_key: string }> | undefined,
   ): boolean
   ```

2. `isArtifactsBuildInProgress`: `jobState === "BUILD_ARTIFACTS"` OR `jobState.startsWith("BUILD_ARTIFACTS.")`. Do **not** treat `ERROR_BUILD_ARTIFACTS` as in-progress chrome (no Generating… strip unless manifest later adds actions for that state).

3. Keep existing `primaryActionsForState` / `artifactHasContent` as-is for other callers.

⚠️ **Decision:** Frontend fallback to `BUILD_ARTIFACTS` actions for compound states — manifest today only keys the base state; duplicating every hop into config is unnecessary for this presentation ticket. Mirror the intent of Python `is_build_artifacts_in_progress` but **exclude** `ERROR_BUILD_ARTIFACTS` from the Generating… chrome.

---

## Stage 2: Empty / in-flight / populated Artifacts layouts

**Done when:** Artifacts tab matches AC #6–8 layout rules; Generate/Cancel use today’s POST paths; in-flight shows yellow **Generating…** + **Cancel**; section list only when at least one artifact blob has content.

1. In `JobAnalysisReportModal.tsx`, replace AST-948’s always-on empty Artifacts `ReportSectionList` with three mutually exclusive layouts:

   **A — In progress** (`isArtifactsBuildInProgress(job.state)`):

   - Render an action row (class reuse: e.g. `recommended-report-header-actions` or `recommended-report-artifacts-actions`):
     - A **disabled** button, `className="modal-btn save in-flight"`, visible label exactly **`Generating…`** (ellipsis character `…`, not three ASCII dots).
     - Beside it, every action from `artifactsTabPrimaryActions` with `action_key === "cancel_build"` (label from manifest, normally **Cancel**), enabled unless `primaryBusy`.
   - Do **not** render the three section panels while in progress (even if partial blobs exist mid-chain).

   **B — Empty** (not in progress AND `!anyReportArtifactContent(artifacts, report_artifact_tabs)`):

   - Render **only** the Generate control from `artifactsTabPrimaryActions` (`action_key === "generate_artifacts"`, label from manifest **Generate Artifacts**).
   - On click: same POST as today (`/api/jobs/<id>/generate_artifacts`); apply `in-flight` + busy while request runs; on success keep AST-591 behavior (`onRefresh` + `onClose`).
   - No section list.

   **C — Populated** (`anyReportArtifactContent(…)` and not in progress):

   - Render `ReportSectionList` with sections = each `report_artifact_tabs` row where `artifactHasContent(artifacts, artifact_key)` (map `section_id=tab_id`, `nav_label` from manifest, `default_expanded: false`).
   - Omit `leading` Generate/Cancel on the populated layout (Print stays in header per AST-948; Apply stays job-title deeplink). If product later needs regenerate, that is out of scope.
   - `renderSection(sectionId)` → `ArtifactEditor` as in the pre-redesign modal:
     - Resume (`use_resume_structure`): restore `/api/candidates/<id>/resume_structure` fetch; show structure error / loading empty lines; pass `structureSections` + `useCandidateResumeStructure` + `jobPersistence={{ jobId, artifactKey, onSaved: load }}`; `taskKey="craft_resume_base"`.
     - Cover: `taskKey="craft_cover_letter"`, `shapesKey` from manifest when set.
     - Application: `taskKey="propose_application_responses"`, `shapesKey` from manifest when set.
   - Do **not** add Reset/Regenerate controls.

2. Fix close-on-action keys when running Cancel: config `action_key` is **`cancel_build`** (path_suffix `cancel_artifact_build`). Close the modal after successful generate **or** cancel when `action_key` is `generate_artifacts` **or** `cancel_build` (today’s modal incorrectly checks `cancel_artifact_build` — correct it in this ticket as part of Artifacts strip wiring).

3. While `primaryBusy` on Generate (before close), show `in-flight` on the Generate button; label may stay **Generate Artifacts** until unmount/close (in-progress chrome on reopen is **Generating…**).

4. `npx tsc -b --noEmit` for touched frontend files.

⚠️ **Decision:** Hide section chrome for empty and in-progress layouts — AC #6 is Generate-only; AC #7 is Generating…+Cancel; AC #8 sections only when blobs exist. This supersedes AST-948’s temporary “always three empty sections” shell decision for the Artifacts tab only.

⚠️ **Decision:** Populated tab does not show Generate again (no Reset/Regenerate in scope). Candidate with artifacts in `CANDIDATE_REVIEW` edits via sections; apply remains the header job-title link.

---

## Self-Assessment

**Scope:** Single-Component — Artifacts tab layout + helpers inside the Recommended report modal; reuses `ArtifactEditor` and existing generate/cancel APIs.

**Conf:** high — generate/cancel paths, `ArtifactEditor` job persistence, AST-645 `.in-flight`, and `report_artifact_tabs` are already shipped; this ticket re-homes and gates them on the Artifacts tab.

**Risk:** Medium — missing compound-state Cancel fallback would strand daisy-chain jobs without Cancel; showing empty section shells during Generate would fail AC #6; wrong `action_key` check would skip close-on-cancel.

---

## Code rules check

- **§1.3 DRY:** One in-progress helper + one action resolver; reuse `artifactHasContent` / `ArtifactEditor`; no second editor.
- **§1.4 / §2.1:** Action labels/paths and artifact section metadata stay manifest-driven; only compound-state **lookup fallback** is frontend (documented Decision).
- **§2.4 / §2.6:** N/A — no dispatch/state-machine changes; POSTs already exist.
- **§3.3 / §3.5:** Frontend only.
- **Tests / bible:** Betty owns.

---

## Review (build)

**Built:** `origin/sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit` @ `e0c6344ee3fd26889f45f5cf57ccb2e034057345`

Stages 1–2: `isArtifactsBuildInProgress` / `artifactsTabPrimaryActions` / `anyReportArtifactContent`; Artifacts empty Generate, in-flight Generating…+Cancel, populated `ArtifactEditor` sections with resume-structure fetch. Tests deferred to Betty.

---

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-951
**Publish ref tip (pre-docs):** `44a0bb22c9dd099f25f0397f19c5ec417bf55eb9`
**Overall:** DISCUSS

### What’s solid

- Stages 1–2: three exclusive Artifacts layouts (in-flight Generating…+Cancel; empty Generate-only; populated `ArtifactEditor` sections); resume-structure fetch restored; close-on-action uses `cancel_build` / `generate_artifacts`.
- Helpers match plan names/behavior; `ERROR_BUILD_ARTIFACTS` excluded from Generating… chrome; no Reset/Regenerate; Summary/Analysis bodies untouched on tip.
- Betty `test`/`merge-tests`; engineer `code`/`docs`/`plan`.

### Issues / findings

**discuss**

1. **astral.config.config-source-of-truth / astral.layers.ui-config-driven-business-logic / astral.standards.no-hardcoded-sets** — Compound in-progress detect (`BUILD_ARTIFACTS` / `BUILD_ARTIFACTS.*`) and fallback to base-state Cancel actions remain in React (`isArtifactsBuildInProgress` / `artifactsTabPrimaryActions`). Same Joan plan-time discuss; matches approved Stage 1 Decision (non-blocking). Optional later: expose via manifest / shared constants.
2. **C4 stragglers** (Joan excluded; tip includes AST-948 utils/docs/tests; all **conforms**): `astral.agent.confidence-bounds`, `astral.config.pass-threshold-vs-score-floor`, `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.standards.utils-data-late-import-only`, `astral.state.job-prior-states-enforced`.

**fix-now:** none

### Recommended actions

- No product fix required for this review. Optional follow-up for compound-state action keys in manifest remains non-blocking.

---

## Resolution

**Date:** 2026-07-23  
**Publish tip before resolve:** `e6f32a3` (`docs(AST-951): Radia review — findings` on `origin/sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit`)

| Finding | Action |
| -- | -- |
| fix-now | none |
| discuss #1 — compound-state action resolve in React | **Deferred** — matches approved Stage 1 Decision; Radia/Joan mark non-blocking. Optional later: lift prefix/Cancel fallback into manifest or shared constants. |
| discuss #2 — C4 statute stragglers (all conforms) | **No action** — informational composite-tip / plan-vs-diff predicate drift only. |

No product code changes in resolve. Proceeding to User Testing after §9a dry-run.
