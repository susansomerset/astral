# AST-1477 — Mark applied from Recommended list

**Linear:** [AST-1477](https://linear.app/astral-tracker/issue/AST-1477)
**Parent:** [AST-1464](https://linear.app/astral-tracker/issue/AST-1464) — Add means to mark job as applied for
**Publish ref:** `sub/AST-1464/AST-1477-mark-applied-from-recommended-list`

Operators on Recommended can mark a job Applied via a list-row icon-control when the job is in a legal prior for `CANDIDATE_APPLIED`. Confirmation uses the existing notes modal and `POST …/candidate_action` (`action=applied`); list refresh drops the row from Recommended. This child does **not** add report Applied/Skip (AST-1478) or the Applied list home (AST-1479).

## Explicit scope gate

Ticket **## Scope** names only:

- `src/ui/frontend/src/components/CandidateJobRowActions.tsx` — Applied icon on legal pre-applied states
- `src/ui/frontend/src/pages/JobsRecommended.tsx` — list Applied via shared `requestAction` / notes path and list refresh; may pass action handlers through to the report modal for sibling AST-1478

No other files. Do **not** edit `JobAnalysisReportModal.tsx`, `api_jobs.py`, `config.py`, or `JobsApplied.tsx`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/CandidateJobRowActions.tsx` | On the review-like / pre-applied branch, add an Applied `icon-control` for states that are legal `CANDIDATE_APPLIED` priors appearing on Recommended; call `onAction("applied")` | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Confirm list Applied uses existing `useCandidateJobActions` → `requestAction` / `CandidateActionNotesModal` / error toast / `load` refresh; only edit if that wiring is incomplete. Do **not** add report-modal Applied/Skip props here (AST-1478 owns `JobAnalysisReportModal`) | ui |

## Stages

### Stage 1: Applied icon on legal Recommended priors

**Done when:** On Recommended, rows in `RECOMMENDED` / `BUILD_ARTIFACTS` / `CANDIDATE_REVIEW` show an Applied icon-control next to Skip; clicking it opens the existing notes modal with title “Applied”; confirming POSTs `candidate_action` with `action=applied` (via existing `onAction` → `requestAction` → `confirmPending`). Illegal / failed transitions still surface via the existing error toast (no silent no-op).

1. In `CandidateJobRowActions.tsx`, keep the existing `REVIEW_LIKE` branch that renders Skip (and optional View Analysis). Do not remove Skip or change post-applied R/I/X/G behavior.
2. Add a module-level set of states that may show the **Applied** mark-control on this list. Exact members:

   ```ts
   const PRE_APPLIED_MARK = new Set([
     "CANDIDATE_REVIEW",
     "BUILD_ARTIFACTS",
     "RECOMMENDED",
   ])
   ```

   These are the intersection of Recommended-list states (`RECOMMENDED_JOB_STATES` in config) and `JOB_STATES["CANDIDATE_APPLIED"]["prior_states"]`. Do **not** add `PASSED_LIKE` (it is in `REVIEW_LIKE` for Skip/view legacy, but is **not** a `CANDIDATE_APPLIED` prior — showing Applied there would invite illegal hops).

   ⚠️ **Decision:** Keep this set as a module-level `Set` next to `REVIEW_LIKE` / `POST_APPLIED`. Ticket Scope does not include `config.py` or a state-UI manifest field; the component already hardcodes review/post-applied sets the same way. Do not invent a config/API surface for this child.

3. Inside the `REVIEW_LIKE.has(state) && onSkip` branch (same `job-list-actions` div as Skip), when `onAction` is defined **and** `PRE_APPLIED_MARK.has(state)`, render:

   ```tsx
   <button type="button" className="icon-control" title="Applied" aria-label="Applied"
     onClick={() => onAction("applied")}>A</button>
   ```

   Place Applied after Skip (and before View Analysis when that button is shown). Glyph `A`, labels `Applied` — matches `CandidateActionNotesModal` `LABELS.applied` and `pattern.ui.icon-control` (class `icon-control`, not a labeled `.btn`).

4. Do not call the API from this component. Only `onAction("applied")`. Backend `candidate_action` + `transition_job_state` + `candidate_results.applied` already exist (AST-311); do not duplicate POST logic.

### Stage 2: Recommended list wiring (verify / minimal edit)

**Done when:** After Stage 1, marking Applied from a Recommended row opens notes, confirms, refreshes the list (row leaves Recommended when the API succeeds), and failed/409 responses still toast via `actions.error`. No report Applied/Skip controls are added.

1. Read `JobsRecommended.tsx`. Today it already:

   - mounts `useCandidateJobActions(load)`
   - passes `onAction={a => actions.requestAction(job.astral_job_id, a)}` into `CandidateJobRowActions`
   - mounts `CandidateActionNotesModal` on `actions.pending` / `confirmPending`
   - toasts `actions.error`

   `CandidateActionKey` already includes `"applied"`; `postCandidateAction` already POSTs it. **If that wiring is still present, make no functional change** (optional: one short comment above the `CandidateJobRowActions` usage stating that `onAction` covers list Applied via notes + `candidate_action`).

2. If `onAction` / notes modal / error toast / refresh path is missing or broken for Applied, restore only the list path to match the pattern above — still inside `JobsRecommended.tsx` only.

3. ⚠️ **Decision:** Do **not** pass Applied/Skip handlers into `JobAnalysisReportModal` in this ticket. Ticket Scope’s “may pass … for sibling” would require accepting props on `JobAnalysisReportModal.tsx`, which is AST-1478’s Scope file. Leave the modal mount as `jobId` / `onClose` / `onRefresh` only. Sibling AST-1478 owns report labeled Applied/Skip.

4. Do not implement `/jobs/applied` visibility, nav enablement, or `view=applied` — AST-1479. Acceptance criterion 2’s “appear on `/jobs/applied`” is satisfied for this child by completing the mark-applied transition; list home is sibling ownership per Boundaries.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1477
**Overall:** APPROVED
**Publish ref:** `sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `06a60cc2023dea7c92a9b34e045db976ccaa2f0d`

## Traceability
AC1→Stage 1+2 (Applied `icon-control` → `onAction("applied")` → notes modal → `candidate_action` applied); AC2→Stage 2 (row leaves Recommended on success; `/jobs/applied` list home→AST-1479 per Boundaries); AC3→Stage 1 Done-when + Stage 2 (`actions.error` toast, no silent no-op)

## Findings
None (`fix-now`).

**acceptable** — `PRE_APPLIED_MARK` module-level `Set` in `CandidateJobRowActions.tsx`: extends existing `REVIEW_LIKE` / `POST_APPLIED` pattern; intersection (`RECOMMENDED`, `BUILD_ARTIFACTS`, `CANDIDATE_REVIEW`) matches config; `PASSED_LIKE` excluded; API enforces illegal hops (409). Child scope excludes `config.py`.

**R6 checklist (summary):** Scope gate honored (two in-scope files; AST-1478/1479 exclusions explicit). Ui-only, layer-clean. `pattern.ui.icon-control` conforms. Reuses `useCandidateJobActions` / notes modal — no parallel POST. Stage 2 verify-first on existing `JobsRecommended` wiring. No `JobAnalysisReportModal` props.

**Considered (in-session):** Universal `orch.*` (20) — conforms. Scoped: `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.standards.dry-and-focused-functions`, `astral.standards.in-scope-only`, `astral.standards.no-hardcoded-sets` — conforms or acceptable; `astral.layers.ui-config-driven-business-logic` — acceptable. Excluded: `astral.state.*` (no core/data/config touch).

context_tokens≈35000

## Review

**Publish ref:** `origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list`
**Tip (pre-review):** _(filled at Code Complete)_

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | _(SHA)_ | Applied icon on legal Recommended priors; JobsRecommended onAction comment |
