<!-- linear-archive: AST-950 archived 2026-08-05 -->

## Linear archive (AST-950)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-950/analysis-tab-grades-and-confidence-redesign-recommended-job-modal  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-858 — Redesign Recommended Job Modal  
**Blocked by / blocks / related:** parent: AST-858

### Description

## What this implements

Analysis tab phase sections (no Overview): **JD Analysis** default expanded; **DO / GET / LIKE Analysis**. Each section header shows horizontal grade icons **with confidence dots for every graded vector** (visible collapsed or expanded). Expanded body shows phase upshot (`take_jd` / `take_do` / `take_get` / `take_like`) above hydrated per-vector rubric display.

## Acceptance criteria

3. Analysis tab shows **JD / DO / GET / LIKE Analysis** only (no Overview section); **JD Analysis** is expanded by default.
4. Each analysis section header displays a **horizontal grade-icon row with confidence dots for every graded vector**, visible whether the section is collapsed or expanded.
5. Expanding a phase section shows that phase's Estelle upshot (`take_jd`, `take_do`, `take_get`, or `take_like`) **above** the per-vector rubric grades for that phase.

## Boundaries

* Does **not** own Summary or Artifacts tabs (AST-949, AST-951).
* Does **not** change consult scoring or grade persistence.

## Notes for planning

Blocked by AST-948 shell. Reuse ConfidenceBullets / AgentAnalysisHeader patterns; grade row must include confidence, not letter-only dots.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-858-redesign-recommended-job-modal`, child `sub/AST-858/AST-950-analysis-tab-grades-confidence`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-23T23:28:03.549Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-950
**Publish ref:** `057641f20391def97cf6acf1579c7c5613ed61f3` (`origin/sub/AST-858/AST-950-analysis-tab-grades-confidence`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | UI displays confidence; no scoring bounds / config math changes |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths (core) miss diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths (core) miss diff |
| astral.batch.batch-id-first | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.batch-id-format | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.claim-process-release | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.config.config-source-of-truth | scoped | conforms | phase ids / grades_field / take_key stay manifest-driven |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | no pass_threshold / score_floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths (artifacts/spikes) miss diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | features plans only; not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one AST-950 features file (+ AST-948 on tip) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test/merge-tests stay off src/features |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer code/docs/plan only; tests via Betty |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths (core/external) miss diff |
| astral.layers.import-direction | scoped | conforms | frontend-only AST-950 delta (+ inherited utils) |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths (scripts) miss diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | sections from report_phase_tabs; rubric keys from manifest |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths (core) miss diff |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths (core) miss diff |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new endpoints |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer logging |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths (data) miss diff |
| astral.standards.debug-contract-gated | scoped | conforms | React-only; no debug-contract work |
| astral.standards.dry-and-focused-functions | scoped | conforms | new grade+confidence helper; reuses ConfidenceBullets / AgentAnalysisHeader |
| astral.standards.in-scope-only | scoped | conforms | Analysis only; Summary/Artifacts empty; letter-only helper not deleted |
| astral.standards.logging-via-utils | scoped | conforms | no new logging |
| astral.standards.no-cross-contamination | scoped | conforms | ui frontend for AST-950 delta |
| astral.standards.no-hardcoded-sets | scoped | conforms | phase set from manifest; no new state enums |
| astral.standards.public-then-helpers | scoped | conforms | named export helper + gradesForHeader in lib |
| astral.standards.utils-data-late-import-only | scoped | conforms | no utils→data import on tip |
| astral.state.core-decides-transitions | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.state.job-prior-states-enforced | scoped | conforms | no JOB_STATES / prior_states edits |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths (core) miss diff |
| astral.ui.frontend-file-placement | scoped | conforms | flat components + lib + App.css |
| astral.ui.naming-conventions | scoped | conforms | PascalCase / recommended-report CSS patterns |
| astral.ui.single-gunicorn-worker | scoped | conforms | no worker/deploy changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one merge-tests(AST-950) onto sub |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests/plan vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | child sub under parent ftr |
| orch.git.ftr-sub-topology | universal | conforms | sub/AST-858/AST-950-analysis-tab-grades-confidence |
| orch.git.merge-on-checkout | universal | conforms | tip includes merge of ftr + AST-948 lineage |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rewrite/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | authoritative publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in astral-AST-858 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | compact-header vs full-body Decision explicit |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 implemented as written |
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

AST-950 delta (`9bbfa70`) adds `renderMetadata`, `buildPhaseSectionGradeConfidenceRow` + CSS, and Analysis `renderSection` with `take_*` above `AgentAnalysisHeader`. Self-Assessment Single-Component matches. No Overview; four phase sections always; Summary/Artifacts bodies not owned. Scoring/dispatch untouched.

## Findings

### discuss

**C4 stragglers** — Joan excluded at plan time (UI-only Files Changed); three-dot tip includes AST-948 utils/docs/tests so in-scope. All score **conforms**:

1. `astral.agent.confidence-bounds`
2. `astral.config.pass-threshold-vs-score-floor`
3. `astral.debug.spikes-under-debug-dir`
4. `astral.docs.features-single-file-per-ticket`
5. `astral.git.engineer-test-tree-ban`
6. `astral.standards.utils-data-late-import-only`
7. `astral.state.job-prior-states-enforced`

### fix-now

none

### What’s solid

Header grade+confidence (not letter-only); body take above full rubric; `renderMetadata` handoff from AST-948 shell; sibling boundaries held.

### Notes

Plan-rubric verdict attached (Joan APPROVED). Docs append: `docs(AST-950): Radia review — findings`.

context_tokens≈40000

#### betty — 2026-07-23T23:20:49.524Z
## QA test manifest — AST-950

**Publish:** `origin/sub/AST-858/AST-950-analysis-tab-grades-confidence` @ `fe49e3c`
**Betty commit:** `origin/tests` `6e0a646` → `merge-tests(AST-950): origin/tests 6e0a64681f2cd95828bff166cad5150995277820`

### Coverage

1. **Analysis tab** — `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` (`JobAnalysisReportModal — AST-950 Analysis tab grades and confidence`)
   - JD/DO/GET/LIKE only (no Overview); JD default expanded
   - Header grade+confidence row visible when collapsed; `take_*` above `AgentAnalysisHeader` when expanded
   - Empty grades → **No consult detail on file.**
2. **ReportSectionList `renderMetadata`** — `tests/component/frontend/components/test_ReportSectionList.test.tsx` (`ReportSectionList — AST-950 renderMetadata`)
3. **Helpers** — `tests/component/frontend/lib/test_recommendedJobReport.test.tsx` (`recommendedJobReport — AST-950 grade+confidence header row`)

### Sibling note

AST-949 Summary tests may be present on this tip (tests-branch ancestry). **Use `--testNamePattern="AST-950"`** so Summary-body asserts are not required for this child’s product tip.

### Narrowed run

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_ReportSectionList.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  --testNamePattern="AST-950"
```

### Bible shasums (`origin/sub/...`)

- `docs/test-bible/frontend/components.md` → `f45cf08c32b9a2b791cb45f5358f00d02b86ace69982705f9e302f4a5b713ec2`
- `docs/test-bible/frontend/lib.md` → `05c7fd8f961ec7df0bfa4cc8ddb469095f2b2790dd2f80f5023768a1f70ad201`

— Betty

#### joan — 2026-07-23T22:45:44.063Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-950
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1. Horizontal top tabs; Summary default | N/A — boundary (AST-948) |
| 2. Summary tab sections | N/A — boundary (AST-949) |
| 3. Analysis JD/DO/GET/LIKE only; JD default expanded; no Overview | Stages 1, 3 (manifest `report_phase_tabs`; AST-948 `phase_jd` seed) |
| 4. Header horizontal grade icons **with confidence dots** (collapsed or expanded) | Stages 1–3 (`renderMetadata` + `buildPhaseSectionGradeConfidenceRow` + `ConfidenceBullets`) |
| 5. Expanded body: phase `take_*` **above** per-vector rubric | Stage 3 (`take_*` then `AgentAnalysisHeader`) |
| 6–8. Artifacts generate/edit | N/A — boundary (AST-951) |
| 9. Sticky header deeplinks / copy / print | N/A — boundary (AST-948) |
| 10. Missing/partial upshot graceful empty | Stage 3 (omit empty take; empty consult copy; always four sections) |
| 11. List row-click + Skip | N/A — out of scope |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| Prerequisite gate | blockedBy AST-948 shell / `ReportSectionList` / phase sections |
| 1 `renderMetadata` slot | Functional scope grade-at-a-glance in section headers (collapsed or expanded) |
| 2 Grade+confidence header helper | Parent AC4; Notes (not letter-only dots) |
| 3 Wire Analysis bodies + metadata | Parent AC3–5; Purpose Analysis drill-down; Boundaries (no scoring change) |

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
| orch.pipeline.call-susan-for-product-decisions | conforms | Compact-header vs full-body Decision is product-aligned, not ambiguous |
| orch.pipeline.plan-is-bible | conforms | Named helper + explicit wire steps; stop if shell missing |
| orch.pipeline.project-scoped-queues | conforms | Interface child only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready + Joan assignee |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | Betty QA note; no test-tree edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Return to Katherine |
| orch.roles.engineer-assignee-through-resolve | conforms | Katherine implementer |
| orch.roles.pre-commit-path-bans | conforms | No banned-path instructions |
| astral.config.config-source-of-truth | conforms | Phase ids / `grades_field` / `take_key` stay manifest-driven |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.import-direction | conforms | Frontend-only |
| astral.layers.ui-config-driven-business-logic | conforms | Section list from `report_phase_tabs`; rubric keys from manifest |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new endpoints |
| astral.standards.data-raises-caller-logs | conforms | No data-layer changes |
| astral.standards.debug-contract-gated | conforms | React-only |
| astral.standards.dry-and-focused-functions | conforms | New helper; reuses rubric sort / `ConfidenceBullets` / `AgentAnalysisHeader` |
| astral.standards.in-scope-only | conforms | Analysis only; does not delete unused letter-only helper |
| astral.standards.logging-via-utils | conforms | No new logging |
| astral.standards.no-cross-contamination | conforms | ui frontend only |
| astral.standards.no-hardcoded-sets | conforms | No new state enums; phase set from manifest |
| astral.standards.public-then-helpers | conforms | Named export helper; optional grades normalize to lib if large |
| astral.ui.frontend-file-placement | conforms | Flat components + `lib/` + `App.css` |
| astral.ui.naming-conventions | conforms | PascalCase / existing CSS patterns |
| astral.ui.single-gunicorn-worker | conforms | No deploy/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.confidence-bounds — layers/paths (core/utils) miss (UI display only; no scoring bounds change)
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

### acceptable
1. Extending AST-948 `ReportSectionList` with optional `renderMetadata` is the intended handoff (shell left `metadata` unset for AST-950).
2. Leaving letter-only `buildPhaseTabGradeDots` undeleted if unused avoids scope creep; new helper is required for confidence AC.
3. Always rendering four phase sections (even when upshot null) matches parent AC10 / “no Overview” and avoids hiding DO/GET/LIKE on partial data.

**Self-assessment:** Scope Single-Component / Conf high / Risk Medium — honest about letter-only vs confidence and header/body split. No `!!-NONE`. No fix-now.

— Joan
context_tokens≈62000

#### katherine — 2026-07-23T22:37:36.849Z
Plan: [`docs/features/interface/ast-950-analysis-tab-grades-confidence.md`](https://github.com/susansomerset/astral/blob/sub/AST-858/AST-950-analysis-tab-grades-confidence/docs/features/interface/ast-950-analysis-tab-grades-confidence.md) on **`origin/sub/AST-858/AST-950-analysis-tab-grades-confidence`** @ `2fcd9a8`.

**Scope — Single-Component:** Analysis tab wiring plus optional `ReportSectionList` metadata slot and a grade+confidence header-row helper/CSS; no scoring/dispatch changes.

**Conf — high:** Reuses `ConfidenceBullets`, rubric importance sort, `AgentAnalysisHeader`, `jobGradesForField`, and AST-948 phase section ids; AC split (compact header vs full body rubric) is explicit.

**Risk — Medium:** Letter-only header would miss confidence AC; stuffing full `AgentAnalysisHeader` into the collapsed header would hide reasons or bloat chrome; gating sections on upshot would drop phases when data is partial.

---

# Analysis tab grades and confidence (Redesign Recommended Job Modal)

**Linear:** [AST-950](https://linear.app/astralcareermatch/issue/AST-950/analysis-tab-grades-and-confidence-redesign-recommended-job-modal)  
**Parent:** [AST-858 — Redesign Recommended Job Modal](https://linear.app/astralcareermatch/issue/AST-858/redesign-recommended-job-modal)  
**Publish ref (origin):** `sub/AST-858/AST-950-analysis-tab-grades-confidence`  
**Parent integration ref:** `ftr/AST-858-redesign-recommended-job-modal`  
**Blocked by:** [AST-948](https://linear.app/astralcareermatch/issue/AST-948/modal-shell-horizontal-tabs-sticky-header-redesign-recommended-job) (shell / `ReportSectionList` / `report_phase_tabs` as Analysis sections)

Fill Analysis tab phase sections (no Overview): **JD Analysis** default expanded; **DO / GET / LIKE Analysis**. Each section header shows a **horizontal** grade-icon row **with confidence dots** for every graded vector (visible collapsed or expanded). Expanded body shows that phase’s Estelle upshot (`take_jd` / `take_do` / `take_get` / `take_like`) **above** the hydrated per-vector rubric display (`AgentAnalysisHeader`). Does **not** own Summary/Artifacts bodies, shell/header, or consult scoring.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-858/AST-950-analysis-tab-grades-confidence`; `git merge origin/dev`; `git merge origin/ftr/AST-858-redesign-recommended-job-modal`; merge-clean gate.
2. Merge **`origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`** (or rolled-up `origin/ftr/…`) so Analysis `ReportSectionList` exists with empty `renderSection`, sections from `report_phase_tabs` (`section_id` = `tab_id`), and `phase_jd` default expanded.
3. If `ReportSectionList` / `report_phase_tabs` wiring is missing, **stop** — comment on AST-950; do not rebuild shell.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/ReportSectionList.tsx` | Optional `renderMetadata?(sectionId) => ReactNode` → `CollapsiblePanel` `metadata` | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Add horizontal grade+confidence header-row helper (importance order; includes `ConfidenceBullets`) | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Wire Analysis `renderMetadata` + `renderSection` (upshot above `AgentAnalysisHeader`); restore grades helpers as needed | ui |
| `src/ui/frontend/src/App.css` | Compact horizontal grade+confidence row under recommended-report / analysis header (reuse `--confidence-*` / `.grade-dot`) | ui |

**Out of scope:** Summary bodies (AST-949); Artifacts (AST-951); shell/header (AST-948); changing `AgentAnalysisHeader` public API unless a one-line prop is required for layout; scoring/dispatch; `tests/` / bible (Betty).

**QA note (Betty):** Assert four Analysis sections (no Overview); JD default expanded; header grade+confidence visible when collapsed; expanded body shows `take_*` above rubric rows; missing upshot/grades → empty states, no crash.

---

## Stage 1: `ReportSectionList` metadata slot

**Done when:** Callers may pass optional `renderMetadata`; each panel sets `CollapsiblePanel` `metadata={renderMetadata?.(section_id)}`. Summary/Artifacts callers unchanged when omitted.

1. In `ReportSectionList.tsx`, extend props:

   ```tsx
   renderMetadata?: (sectionId: string) => ReactNode
   ```

2. Pass through to `CollapsiblePanel`: `metadata={renderMetadata?.(section.section_id)}` (omit / undefined when callback absent or returns null/undefined — CollapsiblePanel already skips null/false).

3. Do **not** change expand policy, `leading`, or `renderSection` contracts from AST-948.

---

## Stage 2: Horizontal grade + confidence header helper

**Done when:** A shared helper returns a horizontal row of grade-dot + `ConfidenceBullets` for every graded vector in rubric importance order (or raw grade order when rubric missing). Letter-only `buildPhaseTabGradeDots` is **not** used for this header (it lacks confidence).

1. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`, add (name exact):

   ```tsx
   export function buildPhaseSectionGradeConfidenceRow(
     gradesRaw: unknown,
     rubricArtifactKey: string | undefined,
     candidateArtifacts: Record<string, unknown>,
   ): ReactNode
   ```

2. Behavior:

   - Build ordered rubric columns the same way as `buildPhaseTabGradeDots` (`buildJobListRubricColumnsFromArtifact` + `sortJobListRubricColumns`) when `rubricArtifactKey` resolves to an array on `candidateArtifacts`.
   - For each column, resolve grade + confidence from `gradesRaw` (array rows include `confidence`; object map form → confidence omitted / bullets dim — same as list pages).
   - Skip columns with no grade letter.
   - Each cell: wrap `<span className="grade-dot …">` + `<ConfidenceBullets confidence={…} />` in a compact block (class `recommended-report-phase-grade-cell`); tooltip via `formatGradeDotTooltip` on the grade-dot.
   - If rubric artifact missing/empty but `gradesRaw` is a nonempty array, fall back to array order (vector/grade/confidence) so headers still render.
   - Return `null` when no graded cells.

3. In `App.css`, add a horizontal flex row for the metadata slot, e.g. `.recommended-report-phase-grade-row` (flex, wrap, gap) and `.recommended-report-phase-grade-cell` (column align center — grade above bullets, matching `.analysis-grade-block` density but tighter for headers). Do not invent new grade colors.

⚠️ **Decision:** New helper instead of overloading `buildPhaseTabGradeDots` — old helper is letter-only rail labels; Analysis header AC explicitly requires confidence. Leave `buildPhaseTabGradeDots` in place if still referenced elsewhere; if unused after AST-948, do not delete in this ticket.

---

## Stage 3: Wire Analysis tab bodies + header metadata

**Done when:** Analysis tab shows only JD/DO/GET/LIKE sections; JD expanded by default (AST-948 seed); each header shows the confidence grade row when grades exist; expanded body = phase `take_*` (if any) above `AgentAnalysisHeader`; missing upshot/grades → empty copy, no crash; no Overview section.

1. In `JobAnalysisReportModal.tsx` Analysis `ReportSectionList`:

   - Keep sections from `manifest.jobs.recommended.report_phase_tabs` with `section_id = tab_id`, `nav_label` from manifest, `default_expanded = (tab_id === "phase_jd")` (unchanged from AST-948).
   - Always render all four phase sections from the manifest (do **not** gate the section list on `parseAnalysisUpshot` truthiness — empty bodies handle missing data).
   - `renderMetadata(sectionId)`: find phase row; `gradesRaw = jobGradesForField(job, phase.grades_field)`; `rubricKey = manifest.jobs.grade_rubric_by_field[phase.grades_field]`; return `buildPhaseSectionGradeConfidenceRow(gradesRaw, rubricKey, candidateArtifacts)` (or null).
   - `renderSection(sectionId)`:
     - Resolve phase + `parseAnalysisUpshot(job.job_data?.analysis_upshot)`.
     - Upshot block: `takeBody = parsed?.[phase.take_key]` when string + trim; render with existing `.job-analysis-upshot-body` (no duplicate section heading inside the panel). If missing/empty, omit the upshot block (do not fail the section).
     - Rubric block: build grades via the same `gradesForHeader`-style normalization already used pre-redesign (vector/grade/confidence/reason). If `grades.length > 0`, render `<AgentAnalysisHeader grades={grades} rubricArtifact={rubricKey} />`. Else `<p className="recommended-report-empty">No consult detail on file.</p>`.
     - If both upshot and grades are empty, still show the empty consult line (header metadata may also be empty).

2. Re-import `AgentAnalysisHeader`, `jobGradesForField`, and restore a local `gradesForHeader` helper (or move it to `recommendedJobReport.tsx` if that keeps the modal thinner — prefer lib if the function is >~15 lines and shared with the header helper’s array parsing).

3. Do **not** add an Overview section. Do **not** put `AgentAnalysisHeader` in the collapsed header — header is the compact grade+confidence row only; body owns the full rubric list with reasons / “show rubric”.

4. `npx tsc -b --noEmit` for touched frontend files.

⚠️ **Decision:** Compact header row ≠ `AgentAnalysisHeader`. Header = glanceable grade+confidence; body = Estelle take + full colorful rubric (`AgentAnalysisHeader`). Matches parent AC split and avoids duplicating reason text in the sticky section chrome.

---

## Self-Assessment

**Scope:** Single-Component — Analysis tab wiring in the Recommended report modal plus a small `ReportSectionList` metadata hook and a grade+confidence row helper/CSS.

**Conf:** high — reuses `ConfidenceBullets`, rubric column sort, `AgentAnalysisHeader`, `jobGradesForField`, and AST-948 section ids; ticket explicitly points at these patterns.

**Risk:** Medium — wrong header helper (letter-only) would miss AC #4; putting full `AgentAnalysisHeader` only in the header would hide reasons when expanded or bloat collapsed chrome; gating sections on upshot would hide DO/GET/LIKE when partial.

---

## Code rules check

- **§1.3 DRY:** One metadata helper; reuse rubric sort / tooltip / `ConfidenceBullets`; do not fork a second AgentAnalysisHeader.
- **§1.4 / §2.1:** Phase section ids/labels/grades_field/take_key stay manifest-driven (`report_phase_tabs`).
- **§2.4 / §2.6:** N/A — presentation only.
- **§3.3 / §3.5:** Frontend components + `App.css` only.
- **Tests / bible:** Betty owns.

---

## Review (build)

**Built:** `origin/sub/AST-858/AST-950-analysis-tab-grades-confidence` @ `9bbfa70594ae9709ba7fe336a1f7379d8cdcc023`

Stages 1–3: `ReportSectionList` `renderMetadata`; `buildPhaseSectionGradeConfidenceRow` + CSS; Analysis `take_*` above `AgentAnalysisHeader` with header grade+confidence. Tests deferred to Betty.

---

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-950
**Publish ref tip (pre-docs):** `fe49e3cf39480689c8b67060dd4e0dcb847c804f`
**Overall:** DISCUSS

### What’s solid

- Stages 1–3: optional `renderMetadata` on `ReportSectionList`; `buildPhaseSectionGradeConfidenceRow` with `ConfidenceBullets` (not letter-only dots); Analysis `take_*` above `AgentAnalysisHeader`; four phase sections always; Summary/Artifacts bodies untouched on this tip.
- Manifest-driven `grades_field` / `take_key` / rubric keys; no scoring/dispatch changes.
- Betty `test`/`merge-tests`; engineer `code`/`docs`/`plan`.

### Issues / findings

**discuss** (C4 stragglers — Joan plan excluded; three-dot tip vs `origin/dev` includes AST-948 utils/docs/tests so in-scope; all **conforms**):

1. `astral.agent.confidence-bounds`
2. `astral.config.pass-threshold-vs-score-floor`
3. `astral.debug.spikes-under-debug-dir`
4. `astral.docs.features-single-file-per-ticket`
5. `astral.git.engineer-test-tree-ban`
6. `astral.standards.utils-data-late-import-only`
7. `astral.state.job-prior-states-enforced`

**fix-now:** none

### Recommended actions

- No product fix required.

---

## Resolution

**Date:** 2026-07-23  
**Publish tip before resolve:** `057641f` (`docs(AST-950): Radia review — findings` on `origin/sub/AST-858/AST-950-analysis-tab-grades-confidence`)

| Finding | Action |
| -- | -- |
| fix-now | none |
| discuss — C4 statute stragglers (all conforms) | **No action** — informational composite-tip / plan-vs-diff predicate drift only. |

No product code changes in resolve. Proceeding to User Testing after §9a dry-run.
