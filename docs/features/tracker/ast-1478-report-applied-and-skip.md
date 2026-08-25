# AST-1478 — Report Applied and Skip

**Linear:** [AST-1478](https://linear.app/astralcareermatch/issue/AST-1478)
**Parent:** [AST-1464](https://linear.app/astralcareermatch/issue/AST-1464) — Add means to mark job as applied for
**Publish ref:** `sub/AST-1464/AST-1478-report-applied-and-skip`

Operators reviewing a Recommended job in the Job Analysis Report need the same terminal outcomes as the list: mark Applied (notes → `candidate_action`) and Skip (`POST …/skip`). Today the report has neither control; external job-link Apply (title deeplink / manifest `action_key: apply`, CLIENT `job_link`) must stay separate and must not set `CANDIDATE_APPLIED`. This ticket owns labeled Applied + Skip on the report and the Recommended-page wiring into the existing shared hook — not list-row Applied (AST-1477) or the Applied list home (AST-1479).

## Scope gate

Ticket **## Scope** (only these files / kinds of change):

| File | Allowed change |
|------|----------------|
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Labeled Applied + Skip controls; props for skip/applied callbacks; keep CLIENT job-link Apply separate |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Only as needed to supply skip/applied callbacks or shared hook into the modal |

Out of scope (do not touch): `CandidateJobRowActions`, `useCandidateJobActions`, `candidateJobActions.ts`, `config.py`, `api_jobs.py`, `JobsApplied`, Applied nav, list-row Applied icon.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Optional `onSkip` / `onRequestApplied` props; labeled `.btn` Skip + Applied strip in report chrome | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Pass shared-hook skip / `requestAction(..., "applied")` into the modal; close report when the job leaves the recommended list after a successful transition | ui |

## Stage 1: Modal — labeled Applied + Skip

**Done when:** With both callbacks passed and a job loaded, the report chrome shows labeled **Skip** (`btn secondary`) and **Applied** (`btn primary`); Skip invokes `onSkip`; Applied invokes `onRequestApplied`; neither path calls `runPrimaryAction` or opens `job_link`; the title/job-link deeplink and Artifacts Generate/Cancel behavior are unchanged.

1. In `JobAnalysisReportModal.tsx`, extend `Props`:

   ```ts
   interface Props {
     jobId: string | null
     onClose: () => void
     onRefresh?: () => void
     /** Recommended Skip — parent runs shared postSkipJob / useCandidateJobActions.skipJob */
     onSkip?: () => void
     /** Opens parent notes modal for candidate_action applied — parent runs requestAction(jobId, "applied") */
     onRequestApplied?: () => void
   }
   ```

2. Destructure `onSkip` and `onRequestApplied` in the component signature (alongside existing props).

3. Inside `recommended-report-chrome`, **after** `<RecommendedJobReportHeader … />` and **before** the top-tabs block, when `job` is loaded and at least one of `onSkip` / `onRequestApplied` is defined, render an action strip using the existing class `recommended-report-header-actions` (do **not** add new CSS rules or touch `App.css` — that file is out of scope):

   ```tsx
   {(onSkip || onRequestApplied) && (
     <div className="recommended-report-header-actions" style={{ padding: "0 16px 12px" }}>
       {onSkip && (
         <button
           type="button"
           className="btn secondary"
           disabled={primaryBusy}
           onClick={() => onSkip()}
         >
           Skip
         </button>
       )}
       {onRequestApplied && (
         <button
           type="button"
           className={`btn primary${primaryBusy ? " in-flight" : ""}`}
           disabled={primaryBusy}
           onClick={() => onRequestApplied()}
         >
           Applied
         </button>
       )}
     </div>
   )}
   ```

   ⚠️ **Decision — inline padding only:** Scope forbids `App.css`. Reuse `recommended-report-header-actions` for flex/gap; the small horizontal padding keeps the strip aligned with the header without a new stylesheet rule. Do not invent a parallel button family (`modal-btn`, icon-controls for these labels, etc.) — `pattern.ui.shared-button-roles` requires full-size labeled `.btn` + role.

   ⚠️ **Decision — no hardcoded state set in the modal:** Visibility is “callbacks provided,” not a React copy of `REVIEW_LIKE` / `JOB_STATES` priors (`astral.layers.ui-config-driven-business-logic` / no-hardcoded-sets). `JobsRecommended` only opens this modal for recommended-list jobs and always passes both callbacks; illegal transitions still fail at the API (409) with a visible error.

4. Do **not** add a labeled CLIENT **Apply** button. Do **not** map Applied → `runPrimaryAction` / `action_key: apply` / `window.open(job_link)`. Leave `artifactsTabPrimaryActions` filtering and the title deeplink untouched (AC4).

5. Do **not** mount a second `CandidateActionNotesModal` or call `postSkipJob` / `postCandidateAction` inside the modal — parent supplies the shared hook (AC: no parallel POSTs).

## Stage 2: JobsRecommended — wire shared hook + close when job leaves list

**Done when:** Opening a report from Recommended and clicking Skip runs the same `actions.skipJob` path as the list S icon; clicking Applied opens the existing `CandidateActionNotesModal` for `action: "applied"` via `actions.requestAction`; on success the job disappears from recommended rows and the report closes; on 409/error the existing toast shows the message and the report stays open (job still in `rows`).

1. In `JobsRecommended.tsx`, on `<JobAnalysisReportModal … />`, pass:

   ```tsx
   <JobAnalysisReportModal
     jobId={reportId}
     onClose={() => setReportId(null)}
     onRefresh={load}
     onSkip={
       reportId
         ? () => { void actions.skipJob(reportId) }
         : undefined
     }
     onRequestApplied={
       reportId
         ? () => { actions.requestAction(reportId, "applied") }
         : undefined
     }
   />
   ```

   Keep the existing page-level `<CandidateActionNotesModal … />` and toast/`actions.error` effect unchanged — Applied from the report reuses that notes modal and error toast.

2. Add an effect so the report closes only when the job is no longer on the recommended list (successful Skip or Applied + refresh), not on cancel of the notes modal and not on failed transitions:

   ```tsx
   useEffect(() => {
     if (!reportId) return
     if (!rows.some(j => j.astral_job_id === reportId)) {
       setReportId(null)
     }
   }, [rows, reportId])
   ```

   ⚠️ **Decision — close via list membership, not hook return values:** `useCandidateJobActions` is out of scope and swallows errors into `error` state (no success boolean). Closing when `reportId ∉ rows` after `onRefresh` matches parent technical scope (“refresh parent list and close”) without forking the hook or duplicating POSTs. Failed skip/applied leave the job in `rows` → modal stays; `actions.error` toast already surfaces the message (AC5).

3. Do not change list-row `CandidateJobRowActions` props (AST-1477 owns Applied on the row).

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1478
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1464/AST-1478-report-applied-and-skip` @ `4aae3fcfb1b2d3d293477265cc170c2e0ee87ceb`

**Gate:** Plan Ready · assignee Joan · parent AST-1464 · first pass (no `[plan-discuss]` rounds).

**Considered:** (in-session — universal `orch.*` delivery set + scoped `astral.standards.dry-and-focused-functions`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.layers.import-direction`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only`; parent-cited `astral.state.core-decides-transitions` / `astral.state.job-prior-states-enforced` excluded — plan paths are `src/ui/frontend/**` only, transitions stay on existing API routes; `astral.standards.no-hardcoded-sets` excluded — no `config.py` in Files Changed). All considered statutes **conform**.

## Traceability
AC2→S1+S2 (labeled Applied → parent `requestAction` / notes / `candidate_action`); AC3→S1+S2 (`onSkip` → `actions.skipJob`); AC4→S1§4 (no `runPrimaryAction` / `job_link` for Applied; title deeplink + artifacts apply unchanged); AC5→S2§2–3 (409/error via existing `actions.error` toast; report closes only when `reportId ∉ rows` after refresh); parent AC1/4–7 N/A — sibling AST-1477 / AST-1479 per Boundaries.

## Findings

**acceptable** · `JobAnalysisReportModal.tsx` Stage 1 · Inline `padding` on the action strip while `App.css` is out of scope — documented ⚠️; reuses `recommended-report-header-actions` + `pattern.ui.shared-button-roles` (`.btn primary` / `.btn secondary` / `in-flight`), not a parallel button family.

**acceptable** · `JobAnalysisReportModal.tsx` Stage 1 §3 · Visibility gated on callbacks supplied, not a React copy of `JOB_STATES` priors — consistent with scope (no `config.py`) and Recommended-only modal context; illegal hops still 409 at API.

No `fix-now` or `discuss` blockers.

**R6 checklist:** Scope gate honored (two files only); layer/import/placement/config checks pass; `pattern.ui.shared-button-roles` matches solution shape; no parallel POSTs (`useCandidateJobActions` on parent); close-on-list-membership fits existing `useInPlaceLiveRefresh` + `load` on `JobsRecommended`; Estimate confirm present (3 — agree).

context_tokens≈23000

---

[plan-rubric] PROCEED (Commit: 4aae3fcfb1b2d3d293477265cc170c2e0ee87ceb) report Applied Skip wired

AST-1478 plan approved.

## Review (build)

**Built:** `origin/sub/AST-1464/AST-1478-report-applied-and-skip` @ `d4bfa409acdd473a08d3dd7c27c4500435e3bba9`

Stages 1–2: labeled Skip (`btn secondary`) + Applied (`btn primary`) on report chrome; `JobsRecommended` wires `skipJob` / `requestAction(..., "applied")` and closes the report when the job leaves recommended rows. CLIENT job-link Apply unchanged. Tests deferred to Betty.

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1478
**Publish ref:** `origin/sub/AST-1464/AST-1478-report-applied-and-skip` @ `43da07a87aa77385f0372cd159d1fd7dabe2f44b`
**Overall:** FIX-NOW

## Statutes checked

65 active statutes scored in-session. No **violates**. Full table:

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | ui/docs diff only |
| astral.agent.do-task-delegation | scoped | not-applicable | no agent paths |
| astral.agent.grade-vector-validation | scoped | not-applicable | no agent paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch paths |
| astral.batch.claim-process-release | scoped | not-applicable | no batch paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch paths |
| astral.config.config-source-of-truth | scoped | not-applicable | no config.py in delta |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets paths |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no dispatch paths |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single AST-1478 issue doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty: bible + tests only |
| astral.git.engineer-test-tree-ban | scoped | conforms | product `d4bfa409` → `src/ui` only |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | ui-only |
| astral.layers.import-direction | scoped | conforms | no layer violations |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | callback-gated strip |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no new routes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed |
| astral.seed.define-approved | scoped | not-applicable | no seed |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug= |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuses parent hook |
| astral.standards.in-scope-only | scoped | conforms | product delta = two scoped files |
| astral.standards.logging-via-utils | scoped | not-applicable | no logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain names |
| astral.standards.no-cross-contamination | scoped | not-applicable | single feature |
| astral.standards.no-hardcoded-sets | scoped | conforms | callbacks not JOB_STATES (Joan straggler — discuss) |
| astral.standards.public-then-helpers | scoped | not-applicable | no new surface |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils |
| astral.state.core-decides-transitions | scoped | not-applicable | API via parent hook |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no prior logic in diff |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run paths |
| astral.ui.frontend-file-placement | scoped | conforms | correct tree |
| astral.ui.naming-conventions | scoped | conforms | consistent naming |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests at tip |
| orch.git.commit-vocabulary | universal | conforms | standard prefixes |
| orch.git.flow-direction-inviolable | universal | conforms | sub topology |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1464/AST-1478-…` |
| orch.git.merge-on-checkout | universal | conforms | no rebase issues |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | merge only |
| orch.git.no-dev-agent-branches | universal | conforms | branch naming |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1464 worktree |
| orch.git.three-permanent-branches | universal | conforms | vs origin/dev |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no policy invention |
| orch.pipeline.plan-is-bible | universal | conforms | matches plan |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | approved pattern |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty manifest |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Hedy assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | no bypass |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.shared-button-roles | conforms | `btn secondary` Skip; `btn primary` + `in-flight` Applied |

## Plan adherence

Product code (`d4bfa409`) matches approved plan: labeled Skip/Applied on report chrome; `JobsRecommended` wires `skipJob` / `requestAction(…, "applied")`; close when `reportId ∉ rows`; no parallel POSTs; CLIENT Apply stays separate. Two scoped files; estimate 3 fits.

## Frame diff

(none)

## Findings

### fix-now

**`tests/component/frontend/pages/test_JobsRecommended.test.tsx` — `describe` closes at line 335**

`merge-tests(AST-1478)` (`43da07a8`) strands AST-1057 `it` blocks outside `describe("JobsRecommended")`; they lose suite `beforeEach`. Move closing `})` below AST-1057.

**Same merge — AST-1477 test block dropped**

`describe("AST-1477 mark applied from Recommended")` removed from incoming tests side. Restore at epic merge or confirm AST-1477 lands separately.

### discuss

- Joan excluded `no-hardcoded-sets`; implementation conforms (callback gating) — straggler note only.
- AC5: no report-strip 409/error test; success paths only. Optional follow-up.

### advisory

- Three-dot diff vs `origin/dev` inflated (multiple merge bases); scoped product delta = `d4bfa409` only.
- AST-1106 bible drift on publish ref — epic merge, not AST-1478.
- Inline padding on strip — plan-documented, acceptable.

## What's solid

Shared-hook wiring, `.btn` roles, AC4 separation, close-via-list-membership, AST-1478 component tests green on manifest.

## Recommended actions (downstream)

1. **resolve-child:** fix test nesting in `test_JobsRecommended.test.tsx`.
2. **merge-child:** restore AST-1477 tests; reconcile bible drift.
3. **Optional:** report-path 409 component test.

## Notes

Joan APPROVED @ `4aae3fcf`. Tip unchanged (`43da07a8`). Chuckles: append artifact; post slim upshot; route to **resolve-child**.

context_tokens≈34000

---

```
[code-rubric] REVIEW (Commit: 43da07a8) test merge nesting fix

## Resolution

**2026-08-25** — Radia Overall **FIX-NOW** is test-tree nesting / AST-1477 restore in `test_JobsRecommended.test.tsx`. Engineer cannot edit `tests/`; posted `[qa-handoff]` @Betty White; status stays **Review Posted**; assignee Betty. Discuss/advisory items need no product change on this tip.


**2026-08-25 (resume)** — Betty cleared `[qa-handoff]` @ `c6617b48`: `describe("JobsRecommended")` now closes after AST-1057; `AST-1477 mark applied from Recommended` restored under the suite. Re-ran Betty AST-1478 Vitest manifest — **8 passed**. Discuss/advisory (Joan straggler, optional AC5 409 test, AST-1477 product on sibling sub) need no product change on this tip. Proceeding to User Testing after §9a dry-run.
