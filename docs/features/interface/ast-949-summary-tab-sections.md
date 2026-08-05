<!-- linear-archive: AST-949 archived 2026-08-05 -->

## Linear archive (AST-949)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-949/summary-tab-sections-redesign-recommended-job-modal  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-858 — Redesign Recommended Job Modal  
**Blocked by / blocks / related:** parent: AST-858

### Description

## What this implements

Summary tab collapsible sections: **Job Summary** (`whole_jd_upshot`, default expanded), **Company Upshot** (`prefilter_company_notes`, expanded unless empty), **Noteworthy Caveats** and **Questions to Ask** from `analysis_upshot`, **Raw Job Description** (default collapsed). Graceful empty states.

## Acceptance criteria

2. Summary tab shows **Job Summary** (`whole_jd_upshot`), **Company Upshot** (`prefilter_company_notes`), **Noteworthy Caveats**, **Questions to Ask**, and **Raw Job Description** (collapsed by default) as independent collapsible sections with clear empty states when data is missing.
3. Jobs without `analysis_upshot` or partial data render graceful empty states — no crash.

## Boundaries

* Does **not** own Analysis phase sections or Artifacts tab (AST-950, AST-951).
* Does **not** own modal shell/header (AST-948).

## Notes for planning

Blocked by AST-948 shell. Company notes come from company record API already used for website.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-858-redesign-recommended-job-modal`, child `sub/AST-858/AST-949-summary-tab-sections`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-23T23:27:07.565Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-949
**Publish ref:** `3c4e3879711286fc5bd8375920fc00b3637b241d` (`origin/sub/AST-858/AST-949-summary-tab-sections`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | config.py on tip is AST-948 manifest only; no confidence math |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths (core) miss diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths (core) miss diff |
| astral.batch.batch-id-first | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.batch-id-format | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.claim-process-release | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.config.config-source-of-truth | scoped | conforms | section ids/labels stay AST-948 manifest; content-aware expand is data-dependent per plan Decision |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | no pass_threshold / score_floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths (artifacts/spikes) miss diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | features plans only; not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one AST-949 features file (+ AST-948 inherited on tip) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test/merge-tests stay off src/features |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer code/docs/plan only; tests via Betty |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths (core/external) miss diff |
| astral.layers.import-direction | scoped | conforms | frontend + inherited utils; notes via existing UI API |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths (scripts) miss diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | chrome from manifest; expand overrides match parent “unless empty” |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths (core) miss diff |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths (core) miss diff |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new endpoints |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer logging |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths (data) miss diff |
| astral.standards.debug-contract-gated | scoped | conforms | React-only; no debug-contract work |
| astral.standards.dry-and-focused-functions | scoped | conforms | one `renderSummarySection`; reuses `parseAnalysisUpshot` |
| astral.standards.in-scope-only | scoped | conforms | Summary bodies only; Analysis/Artifacts stay empty |
| astral.standards.logging-via-utils | scoped | conforms | no new logging |
| astral.standards.no-cross-contamination | scoped | conforms | ui frontend for AST-949 delta |
| astral.standards.no-hardcoded-sets | scoped | conforms | no new state enums; empty copy is UI strings |
| astral.standards.public-then-helpers | scoped | conforms | render switch kept in modal at readable size |
| astral.standards.utils-data-late-import-only | scoped | conforms | no utils→data import on tip |
| astral.state.core-decides-transitions | scoped | not-applicable | layers/paths (core/data) miss diff |
| astral.state.job-prior-states-enforced | scoped | conforms | no JOB_STATES / prior_states edits |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths (core) miss diff |
| astral.ui.frontend-file-placement | scoped | conforms | edits in existing modal; no new nested dirs |
| astral.ui.naming-conventions | scoped | conforms | reuses existing upshot/JD/empty class names |
| astral.ui.single-gunicorn-worker | scoped | conforms | no worker/deploy changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one `merge-tests(AST-949)` onto sub |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests/plan vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | child sub under parent ftr |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-858/AST-949-summary-tab-sections` |
| orch.git.merge-on-checkout | universal | conforms | tip includes merge of ftr + AST-948 lineage |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rewrite/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | authoritative publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-858` |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | empty-copy Decision explicit; no product ambiguity |
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

AST-949 delta (`4881b86`) fills Summary `renderSection` per Stage 2 table, lifts `prefilter_company_notes` on the existing company GET (Stage 1), and overrides Summary `default_expanded` content-aware (Stage 3). Self-Assessment Single-Component matches. Analysis/Artifacts/`JobsRecommended` untouched. AST-948 shell prerequisite present on tip.

## Findings

### discuss

**C4 stragglers** — Joan excluded these at plan time (plan Files Changed UI-only); three-dot `origin/dev...` tip includes AST-948 utils/docs/tests so they are in-scope. All score **conforms** (no product defect):

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

Company notes from API (not `job_data`); five Summary bodies + empty states; content-aware expand; graceful null upshot; sibling boundaries held.

### Notes

Plan-rubric verdict attached (Joan APPROVED). Docs append: `docs(AST-949): Radia review — findings`.

context_tokens≈42000

#### betty — 2026-07-23T23:17:20.326Z
## QA test manifest — AST-949

**Publish:** `origin/sub/AST-858/AST-949-summary-tab-sections` @ `2329d10`
**Betty commit:** `origin/tests` `e9a6bdc` → `merge-tests(AST-949): origin/tests e9a6bdc9255fcdea60d3796aae218ea5edd1e9d6`

### Coverage

1. **Summary bodies** — `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` (`JobAnalysisReportModal — AST-949 Summary tab sections`)
   - Job Summary / company notes / caveats / questions / Raw JD (expand to reveal)
   - Content-aware expand (4 open + Raw JD collapsed when populated)
   - Empty-state copy for all five sections
   - Company notes from `/api/companies` (not `job_data`)
2. **Shell regression** — same file (`AST-948 horizontal shell`) — empty-upshot case updated for AST-949 empty copy; chrome/tabs/header/Generate/Print still covered.

### Narrowed run

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

### Bible shasum (`origin/sub/...`)

- `docs/test-bible/frontend/components.md` → `9e13767088b71cea624993218b3209d3982100adf5d45ad7984a762bf249dd4a`

— Betty

#### joan — 2026-07-23T22:44:16.946Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-949
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1. Horizontal top tabs; Summary default | N/A — boundary (AST-948 shell) |
| 2. Summary tab five collapsible sections + empty states | Stages 1–3 |
| 3. Analysis JD/DO/GET/LIKE sections | N/A — boundary (AST-950) |
| 4. Grade-icon + confidence header rows | N/A — boundary (AST-950) |
| 5. Phase upshot above rubric | N/A — boundary (AST-950) |
| 6. Artifacts empty → Generate | N/A — boundary (AST-951) |
| 7. Generating… + Cancel | N/A — boundary (AST-951) |
| 8. Editable artifact sections | N/A — boundary (AST-951) |
| 9. Sticky header deeplinks / copy / print | N/A — boundary (AST-948) |
| 10. Missing/partial `analysis_upshot` graceful empty — no crash | Stage 2 (null upshot → empty copy; chrome stays) |
| 11. List row-click + Skip unchanged | N/A — out of scope (no `JobsRecommended` edits) |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| Prerequisite gate | Dependencies / blockedBy AST-948 shell APIs |
| 1 Company notes on existing company GET | Functional scope Company Upshot from `prefilter_company_notes`; child notes |
| 2 Summary `renderSection` bodies + empty states | Parent AC2 + AC10; Purpose Summary sections |
| 3 Content-aware initial expand | Parent Functional scope “expanded unless empty” for company/caveats/questions; Raw JD collapsed; Job Summary expanded |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No engineer test merge work |
| orch.git.commit-vocabulary | conforms | No contrary commit guidance |
| orch.git.flow-direction-inviolable | conforms | Child sub under parent ftr |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Prerequisite merges origin/dev + ftr + AST-948 |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite/force guidance |
| orch.git.no-dev-agent-branches | conforms | Authoritative sub publish ref |
| orch.git.one-epic-worktree-per-parent | conforms | Epic AST-858 worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | No product ambiguity; empty-copy Decision explicit |
| orch.pipeline.plan-is-bible | conforms | Concrete section_id → body table; stop gate if shell missing |
| orch.pipeline.project-scoped-queues | conforms | Interface child only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready + Joan assignee |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | Betty QA note; engineer skips tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | Return to Katherine |
| orch.roles.engineer-assignee-through-resolve | conforms | Katherine implementer |
| orch.roles.pre-commit-path-bans | conforms | No banned-path instructions |
| astral.config.config-source-of-truth | conforms | Section ids/labels remain AST-948 manifest; no new behavior constants in modules |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env introduced |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; plan already on sub |
| astral.layers.import-direction | conforms | Frontend-only; company notes via existing UI API |
| astral.layers.ui-config-driven-business-logic | conforms | Section chrome from manifest; content-aware expand is data-dependent per parent “unless empty” |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new endpoints |
| astral.standards.data-raises-caller-logs | conforms | No data-layer changes |
| astral.standards.debug-contract-gated | conforms | React-only |
| astral.standards.dry-and-focused-functions | conforms | Reuses `parseAnalysisUpshot` + existing CSS classes |
| astral.standards.in-scope-only | conforms | Summary bodies only; stops if shell symbols missing |
| astral.standards.logging-via-utils | conforms | No new logging |
| astral.standards.no-cross-contamination | conforms | ui frontend only |
| astral.standards.no-hardcoded-sets | conforms | No new state/enum sets; empty copy is UI strings |
| astral.standards.public-then-helpers | conforms | Render switch stays in modal unless size forces extract |
| astral.ui.frontend-file-placement | conforms | No new nested dirs; optional CSS in App.css |
| astral.ui.naming-conventions | conforms | Reuses existing class names |
| astral.ui.single-gunicorn-worker | conforms | No deploy/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.confidence-bounds — layers/paths (core/utils) miss
- astral.agent.do-task-delegation — layers/paths (core) miss
- astral.agent.grade-vector-validation — layers/paths (core) miss
- astral.batch.batch-id-first — layers/paths (core/data) miss
- astral.batch.batch-id-format — layers/paths (core/data) miss
- astral.batch.claim-process-release — layers/paths (core/data) miss
- astral.batch.entity-agent-responses-latest-only — layers/paths (core/data) miss
- astral.config.pass-threshold-vs-score-floor — layers/paths miss
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths (docs) miss
- astral.git.engineer-test-tree-ban — paths (tests/bible) miss
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
1. Fixed English empty-state copy (Stage 2 Decision) matches existing `recommended-report-empty` tone; not a config/enum set.
2. Content-aware `default_expanded` overrides in the modal (Stage 3) correctly implement parent “expanded unless empty” without encoding live emptiness into config — depends on AST-948 `ReportSectionList` reseeding when overridden defs change.

**Self-assessment:** Scope Single-Component / Conf high / Risk Medium — honest; prerequisite stop-gate is specific. No `!!-NONE`. No fix-now.

— Joan
context_tokens≈56000

#### katherine — 2026-07-23T22:36:20.851Z
Plan: [`docs/features/interface/ast-949-summary-tab-sections.md`](https://github.com/susansomerset/astral/blob/sub/AST-858/AST-949-summary-tab-sections/docs/features/interface/ast-949-summary-tab-sections.md) on **`origin/sub/AST-858/AST-949-summary-tab-sections`** @ `29fb587`.

**Scope — Single-Component:** Summary tab bodies in `JobAnalysisReportModal` (company notes on existing company GET + content-aware expand); depends on AST-948 shell, does not re-own it.

**Conf — high:** Reuses `parseAnalysisUpshot`, existing upshot/JD CSS, and lifted `prefilter_company_notes` from `/api/companies`; section ids fixed by AST-948.

**Risk — Medium:** Missing AST-948 merge or wrong empty/expand wiring leaves Summary blank or brittle on partial upshot; notes must come from company API lift, not `job_data`.

---

# Summary tab sections (Redesign Recommended Job Modal)

**Linear:** [AST-949](https://linear.app/astralcareermatch/issue/AST-949/summary-tab-sections-redesign-recommended-job-modal)  
**Parent:** [AST-858 — Redesign Recommended Job Modal](https://linear.app/astralcareermatch/issue/AST-858/redesign-recommended-job-modal)  
**Publish ref (origin):** `sub/AST-858/AST-949-summary-tab-sections`  
**Parent integration ref:** `ftr/AST-858-redesign-recommended-job-modal`  
**Blocked by:** [AST-948](https://linear.app/astralcareermatch/issue/AST-948/modal-shell-horizontal-tabs-sticky-header-redesign-recommended-job) (modal shell / `ReportSectionList` / `report_summary_sections`)

Fill the Summary tab section bodies left empty by AST-948: **Job Summary** (`whole_jd_upshot`), **Company Upshot** (`prefilter_company_notes` from the company record), **Noteworthy Caveats** / **Questions to Ask** (`analysis_upshot`), and **Raw Job Description** (`job_data.job_description`, collapsed by default). Graceful empty states when upshot or fields are missing — no crash. Does **not** touch Analysis / Artifacts bodies, shell, or header.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-858/AST-949-summary-tab-sections`; `git merge origin/dev`; `git merge origin/ftr/AST-858-redesign-recommended-job-modal`; merge-clean gate (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).
2. Merge **`origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`** (or `origin/ftr/…` after AST-948 is rolled up) so `ReportSectionList`, `report_summary_sections`, and Summary tab `renderSection={() => null}` exist.
3. If `ReportSectionList` or `report_summary_sections` is missing after that merge, **stop** — comment on AST-949 naming the missing symbol/SHA; do not reimplement shell chrome.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Load company `prefilter_company_notes`; implement Summary `renderSection` bodies; content-aware `default_expanded` for company/caveats/questions | ui |
| `src/ui/frontend/src/App.css` | Only if Summary empty/list body needs a missing class under existing `job-analysis-upshot-*` / `recommended-report-empty` — prefer reuse; no new design system | ui |

**Out of scope:** AST-948 shell/header/tabs; Analysis grade headers (AST-950); Artifacts generate/edit (AST-951); `JobsRecommended` list/Skip; config/manifest section id changes (owned by AST-948); any `tests/` or `docs/test-bible/**` edits (Betty).

**QA note (Betty):** Frontend tests should assert Summary section bodies (job summary text, company notes, caveats/questions lists, collapsed Raw JD) and empty-state copy when `analysis_upshot` / notes / JD are missing.

---

## Stage 1: Company notes on the existing company fetch

**Done when:** Opening the report still fetches `/api/companies/<company>` once; modal state holds both `companyWebsite` and `companyNotes` (`prefilter_company_notes` string or null). No new API route.

1. In `JobAnalysisReportModal.tsx`, extend the existing company `api(`/api/companies/…`)` `.then` (already used for `company_website` per AST-948 / current modal):

   - Read `co?.prefilter_company_notes` (top-level — `api_companies._lift_company_notes` already lifts it from `company_data`).
   - If typeof string and `.trim()`, store trimmed string in new state `companyNotes`; else `null`.
   - Reset `companyNotes` to `null` at the start of `load()` / when `jobId` clears, same as website.

2. Do **not** add a second company request. Do **not** read notes from `job_data`.

---

## Stage 2: Summary `renderSection` bodies + empty states

**Done when:** On the Summary tab, each of the five `report_summary_sections` ids renders real content or a clear empty state; missing/partial `analysis_upshot` does not throw; Raw JD uses existing JD text normalization.

1. Keep using AST-948’s Summary `ReportSectionList` with manifest `report_summary_sections`. Replace `renderSection={() => null}` with a `renderSummarySection(sectionId: string)` that switches on `section_id` exactly:

   | `section_id` | Body |
   |--------------|------|
   | `job_summary` | If `parseAnalysisUpshot(job.job_data.analysis_upshot)` yields a string `whole_jd_upshot.trim()`, render it as a paragraph using existing `.job-analysis-upshot-body` (no extra heading inside the panel — panel label is already **Job Summary**). Else `<p className="recommended-report-empty">No job summary on file.</p>`. |
   | `company_upshot` | If `companyNotes` nonempty, render as `.job-analysis-upshot-body` text. Else `<p className="recommended-report-empty">No company upshot on file.</p>`. |
   | `caveats` | From parsed upshot `caveats` where `text.trim()`; if any, `<ul className="job-analysis-upshot-list">` of those texts. Else empty-state **No noteworthy caveats on file.** |
   | `questions` | Same pattern from `candidate_questions` → **No questions to ask on file.** |
   | `raw_jd` | `String(job.job_data?.job_description ?? "").trim().replace(/\n{3,}/g, "\n\n")`; if nonempty, `<div className="entity-jd-content">…</div>`; else **No job description on file.** |

2. `parseAnalysisUpshot` returns `null` when missing/empty — treat as no upshot: job_summary / caveats / questions all show their empty states (do **not** crash; do **not** hide the section chrome).

3. Reuse existing CSS classes from the pre-redesign summary pane (`job-analysis-upshot-body`, `job-analysis-upshot-list`, `entity-jd-content`, `recommended-report-empty`). Only add App.css rules if a class is truly missing after AST-948 — do not invent a parallel Summary design.

4. Do **not** render Analysis or Artifacts bodies in this ticket. Do **not** restore `SideTabPanel` content.

⚠️ **Decision:** Empty copy is fixed English strings above (match tone of existing `recommended-report-empty` lines). No i18n, no config strings for empty copy.

---

## Stage 3: Content-aware initial expand for Summary sections

**Done when:** First paint of Summary matches parent defaults: Job Summary expanded; Company Upshot / Caveats / Questions expanded **only when** that section has content, else start collapsed; Raw JD always starts collapsed. User can still expand empty sections to read the empty state.

1. When building the `sections` array passed to Summary `ReportSectionList`, map each manifest row to `ReportSectionDef` but **override** `default_expanded` as follows (do not change `config.py` / manifest):

   - `job_summary` → `true` (always; empty state visible when expanded).
   - `company_upshot` → `true` iff `companyNotes` nonempty, else `false`.
   - `caveats` → `true` iff parsed upshot has ≥1 trimmed caveat text, else `false`.
   - `questions` → `true` iff ≥1 trimmed question text, else `false`.
   - `raw_jd` → `false` always.

2. Ensure `ReportSectionList`’s existing `setExpandedKeys` seed (AST-948) re-runs when these effective defaults change (company fetch completes, job load completes). If the AST-948 seed only keys off `section_id` list and static `default_expanded` from manifest, pass the **overridden** defs from this ticket so the seed sees the content-aware flags — do not fork a second expand hook.

3. Confirm `npx tsc -b --noEmit` in `src/ui/frontend` for files touched.

⚠️ **Decision:** Override expand defaults in the modal from live content rather than encoding emptiness in config — emptiness is data-dependent; config keeps the AST-948 chrome defaults as documentation/fallback for shell-only builds.

---

## Self-Assessment

**Scope:** Single-Component — Summary tab bodies inside `JobAnalysisReportModal` (plus optional CSS reuse); depends on AST-948 shell APIs but does not re-own them.

**Conf:** high — reuses `parseAnalysisUpshot`, existing upshot/JD CSS, and company GET that already lifts `prefilter_company_notes`; section ids are fixed by AST-948 plan.

**Risk:** Medium — wrong empty/expand wiring or a missing AST-948 merge would leave Summary blank or crash on partial upshot; company notes path must use the lifted API field, not invent a job_data key.

---

## Code rules check

- **§1.3 DRY:** One `renderSummarySection`; reuse `parseAnalysisUpshot` and existing empty/JD classes — no parallel upshot parser.
- **§1.4 / §2.1:** Section ids/labels stay manifest-driven (AST-948); this ticket only fills bodies + content-aware expand overrides.
- **§2.4 / §2.6:** N/A.
- **§3.3:** Frontend-only; company notes via existing UI API response.
- **§3.5:** No new page file required; optional small helpers stay in the modal or `lib/` only if extraction is needed for clarity — prefer keeping render switch in the modal unless it exceeds readable size.
- **Tests / bible:** Not touched by engineer (Betty).

---

## Review (build)

**Built:** `origin/sub/AST-858/AST-949-summary-tab-sections` @ `4881b863ef3cc20c3046e87e38ffdc9268fed191`

Stages 1–3: company `prefilter_company_notes` on existing company fetch; Summary `renderSummarySection` bodies + empty states for job_summary / company_upshot / caveats / questions / raw_jd; content-aware `default_expanded`. Tests deferred to Betty.

---

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-949
**Publish ref tip (pre-docs):** `2329d10df91ba4c2d4ef30f5947e495f38082220`
**Overall:** DISCUSS

### What’s solid

- Stages 1–3 on tip: company notes lifted from existing `/api/companies` fetch; `renderSummarySection` for all five Summary ids with planned empty copy; content-aware `default_expanded`; Analysis/Artifacts bodies still empty (sibling scope).
- Reuses `parseAnalysisUpshot` + existing upshot/JD CSS; no parallel parser; no new API.
- Betty `test`/`merge-tests` only for tests/bible; engineer `code`/`docs`/`plan` only.

### Issues / findings

**discuss** (C4 stragglers — Joan plan excluded; three-dot tip vs `origin/dev` includes AST-948 utils/docs/tests so statutes are in-scope; all score **conforms**):

1. `astral.agent.confidence-bounds`
2. `astral.config.pass-threshold-vs-score-floor`
3. `astral.debug.spikes-under-debug-dir`
4. `astral.docs.features-single-file-per-ticket`
5. `astral.git.engineer-test-tree-ban`
6. `astral.standards.utils-data-late-import-only`
7. `astral.state.job-prior-states-enforced`

**fix-now:** none

### Recommended actions

- No product fix required. Stragglers are composite-tip / plan-vs-diff predicate drift only.

---

## Resolution

**Date:** 2026-07-23  
**Publish tip before resolve:** `3c4e387` (`docs(AST-949): Radia review — findings` on `origin/sub/AST-858/AST-949-summary-tab-sections`)

| Finding | Action |
| -- | -- |
| fix-now | none |
| discuss — C4 statute stragglers (all conforms) | **No action** — informational composite-tip / plan-vs-diff predicate drift only. |

No product code changes in resolve. Proceeding to User Testing after §9a dry-run.
