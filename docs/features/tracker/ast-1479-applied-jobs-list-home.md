# AST-1479 — Applied jobs list home

**Linear:** [AST-1479](https://linear.app/astralcareermatch/issue/AST-1479)
**Parent:** [AST-1464](https://linear.app/astralcareermatch/issue/AST-1464) — Add means to mark job as applied for
**Publish ref:** `sub/AST-1464/AST-1479-applied-jobs-list-home`

Operators need a real Applied jobs home: post-applied jobs leave Recommended and must appear on `/jobs/applied` with the existing R/I/X/G row actions. Today `view=applied` falls through to `[]`, Jobs → Applied is nav-disabled, and `JobsApplied` is an empty stub. This ticket owns the applied-view state set, the API list branch, nav enablement, and the Applied page — not mark-applied from Recommended (AST-1477) or report Applied/Skip (AST-1478).

## Scope gate

Ticket **## Scope** (only these files / kinds of change):

| File | Allowed change |
|------|----------------|
| `src/utils/config.py` | Named applied-view state list (parallel to `RECOMMENDED_JOB_STATES` / `SKIPPED_STATES`); enable Jobs → Applied in `NAV_CONFIG` |
| `src/ui/api/api_jobs.py` | Implement `view=applied` list (today else-branch returns `[]`) |
| `src/ui/frontend/src/pages/JobsApplied.tsx` | Replace stub with real applied list + shared candidate actions |

Out of scope (do not touch): `CandidateJobRowActions`, `JobsRecommended`, `JobAnalysisReportModal`, `api_system.py` nav-count map, mark-applied / report Skip (siblings).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `APPLIED_JOB_STATES`; enable Applied nav item | utils |
| `src/ui/api/api_jobs.py` | Import `APPLIED_JOB_STATES`; `view=applied` branch | ui |
| `src/ui/frontend/src/pages/JobsApplied.tsx` | Real list + actions + notes modal + live refresh | ui |

## Stage 1: Config — applied-view states + nav

**Done when:** `APPLIED_JOB_STATES` is importable from `config` and lists exactly the four post-applied states already targeted by `CandidateJobRowActions`’s post-applied branch; Jobs → Applied in `NAV_CONFIG` is enabled the same way as Recommended/Skipped (no `"enabled": False`).

1. In `src/utils/config.py`, immediately after `RECOMMENDED_JOB_STATES` (near line ~2820), add:

   ```python
   # Applied jobs list + nav — post-applied candidate outcomes (AST-1479).
   APPLIED_JOB_STATES = [
       "CANDIDATE_APPLIED",
       "CANDIDATE_INTERVIEW",
       "CANDIDATE_REJECTED",
       "CANDIDATE_GHOSTED",
   ]
   assert all(s in JOB_STATES for s in APPLIED_JOB_STATES)
   ```

   ⚠️ **Decision:** Name `APPLIED_JOB_STATES` (parallel to `RECOMMENDED_JOB_STATES`) rather than `APPLIED_STATES`. Membership matches the existing post-applied icon set in `CandidateJobRowActions` (`CANDIDATE_APPLIED` / `INTERVIEW` / `REJECTED` / `GHOSTED`) — those are the states the Applied list must show and the only states whose row actions this page mounts. Do **not** add `CANDIDATE_REVIEW` or Recommended-pipeline states.

2. In `NAV_CONFIG` Jobs group, change the Applied item from
   `{"label": "Applied", "path": "/jobs/applied", "enabled": False}`
   to
   `{"label": "Applied", "path": "/jobs/applied"}`
   (omit `enabled` — always enabled, same as Recommended / Skipped / In Review). Leave Responded `"enabled": False` untouched.

## Stage 2: API — `view=applied`

**Done when:** `GET /api/jobs?view=applied&candidate_id=<id>` (auth required) returns flattened job rows whose `state` is in `APPLIED_JOB_STATES`, scoped to that candidate, ordered by `state_changed_at` like `view=recommended`. Unauthenticated calls still fail via existing `@require_auth`.

1. In `src/ui/api/api_jobs.py`, add `APPLIED_JOB_STATES` to the existing `from src.utils.config import (...)` block (alongside `RECOMMENDED_JOB_STATES` / `SKIPPED_STATES`).

2. In `list_view()`, after the `view == "recommended"` branch and **before** the final `else: return jsonify([])`, insert:

   ```python
   elif view == "applied":
       rows = list_jobs(
           states=list(APPLIED_JOB_STATES),
           candidate_id=candidate_id,
           order_by="state_changed_at",
       )
       return jsonify([_flatten_grades(r) for r in rows])
   ```

   Keep the docstring query-param list that already names `applied`. Do not change `candidate_action`, skip, or other routes. Do not add virtual-skip / score-floor logic (that is Skipped-only).

## Stage 3: Frontend — replace `JobsApplied` stub

**Done when:** `/jobs/applied` shows a non-stub list for the selected candidate: rows from `view=applied`, Actions column mounts `CandidateJobRowActions` with `onAction` → shared notes modal → `candidate_action`, list refreshes in place after success, and failed actions surface a visible error toast (no silent no-op).

1. Replace the entire contents of `src/ui/frontend/src/pages/JobsApplied.tsx`. Do **not** keep the empty `ListPage` stub. Follow the structure of `JobsRecommended.tsx` for load / refresh / actions / toast, but **simpler** — no sections from state-ui manifest, no phase-score columns, no `JobAnalysisReportModal`, no Skip handler.

2. Required imports / hooks (all already used by sibling job lists):
   - `useCandidate` → `selectedId`
   - `useInPlaceLiveRefresh` → `loading` / `beginRefresh` / `endRefresh`
   - `useCandidateJobActions(load)` → `requestAction` / notes modal / errors
   - `api` for `GET /api/jobs?view=applied&candidate_id=…`
   - `CandidateJobRowActions`, `CandidateActionNotesModal`, `Toast`, `Time`

3. `load(showSpinner = false)`: if no `selectedId`, return; else `beginRefresh(showSpinner)`, fetch
   `` `/api/jobs?view=applied&candidate_id=${encodeURIComponent(selectedId)}` ``,
   set rows from JSON array (else `[]`), `endRefresh` in `finally`. Wire `useEffect(() => { load(true) }, [load])`.

4. Render:
   - Header title **Applied**
   - Loading / empty states parallel to Recommended (“Loading…”, “No applied jobs yet”)
   - Single flat table (no section accordion): columns **Actions | Job Title | Company | State | Updated**
   - Default sort: `state_changed_at` descending (client-side sort OK; same pattern as Recommended’s per-section sort — implement a small `sortAppliedJobs` helper in-file for title/company/state/`state_changed_at`)
   - Each row: `CandidateJobRowActions` with `state={job.state}` and `onAction={a => actions.requestAction(job.astral_job_id, a)}` only (no `onSkip` / `onViewAnalysis` / `onResurrect` — post-applied branch is what mounts R/I/X/G)
   - `CandidateActionNotesModal` bound to `actions.pending` / `busy` / `closePending` / `confirmPending`
   - Toast when `actions.error` is set (copy the `useEffect` + Toast pattern from `JobsRecommended`)

5. Do **not** open Job Analysis Report or Job Detail from this page in this ticket (not in Scope / AC for this child). Row click may be inert or omitted; Actions stopPropagation as in Recommended.

⚠️ **Decision:** Flat table, not Recommended-style state sections and not a new `build_state_ui_manifest` `jobs.applied` block. Ticket Scope allows only the applied-view **state list** + nav flip in config — inventing UI-section config / manifest keys would exceed Scope. State remains visible as a column. Nav badge count in `api_system._get_job_counts` stays out of scope (Applied enables without a count until a later ticket).

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1479
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1464/AST-1479-applied-jobs-list-home` @ `beb7f3d410f9edd3add4c98c8affce9d1edef8da`

## Traceability
AC4→St2+St3 (API `view=applied` + page load lists post-applied rows; mark-applied entry is sibling AST-1477); AC5→St1+St3 (`APPLIED_JOB_STATES` + nav enable + real `JobsApplied`); AC6→St3 (`CandidateJobRowActions` + `useCandidateJobActions` + notes modal); AC7→St3 (Toast on `actions.error`; API 409 surfaces via `postCandidateAction`).

## Findings

### discuss
- **Location:** Citations / Stage 3
- **Finding:** `pattern.ui.in-place-live-refresh` is cited but canon status is `proposed` (not `approved`).
- **Recommendation:** Plan shape matches `canonical_refs` and sibling lists already use `useInPlaceLiveRefresh`; no stage rewrite needed. Track pattern promotion separately; optional citation tweak to “same hook as `JobsRecommended`” if approved-only refs are enforced later.

### acceptable
- **Location:** Stage 3 decision note
- **Finding:** Applied nav badge count left unchanged in `api_system._get_job_counts`.
- **Recommendation:** Explicit out-of-scope call is correct; badge can follow in a later ticket.

context_tokens≈32000
```

```
[plan-rubric] PROCEED (Commit: beb7f3d) applied list home ready

## Review

- Publish ref: `sub/AST-1464/AST-1479-applied-jobs-list-home`
- Build tip: `81f1c7b189cf709aaa7a235d08c76b91a3cd794f`

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1479
**Publish ref:** `origin/sub/AST-1464/AST-1479-applied-jobs-list-home` @ `5b8728e44df0cb323fef35f6c7752367ea4e89e5`
**Overall:** PROCEED

## Statutes checked

65 active statutes scored in-session. No **violates**. Full table:

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | utils/ui diff only |
| astral.agent.do-task-delegation | scoped | not-applicable | no agent paths |
| astral.agent.grade-vector-validation | scoped | not-applicable | no agent paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch paths |
| astral.batch.claim-process-release | scoped | not-applicable | no batch paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch paths |
| astral.config.config-source-of-truth | scoped | conforms | `APPLIED_JOB_STATES` + nav in `config.py` |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets paths |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no dispatch paths |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single AST-1479 issue doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty: bible + tests only |
| astral.git.engineer-test-tree-ban | scoped | conforms | product `81f1c7b1` → scoped files only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | API delegates to `list_jobs`; no core edits |
| astral.layers.import-direction | scoped | conforms | `api_jobs` imports utils config; page imports hooks/components |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | state list in config; flat table per plan decision |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `list_view` retains `@require_auth` |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed |
| astral.seed.define-approved | scoped | not-applicable | no seed |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug= |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuses `useCandidateJobActions` / `CandidateJobRowActions` |
| astral.standards.in-scope-only | scoped | conforms | product delta = four scoped files |
| astral.standards.logging-via-utils | scoped | not-applicable | no logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | `APPLIED_JOB_STATES` domain-shaped |
| astral.standards.no-cross-contamination | scoped | not-applicable | single feature |
| astral.standards.no-hardcoded-sets | scoped | conforms | state set in config with `JOB_STATES` assert |
| astral.standards.public-then-helpers | scoped | conforms | `sortAppliedJobs` helper after component |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data |
| astral.state.core-decides-transitions | scoped | not-applicable | transitions via existing `candidate_action` API (Joan excluded) |
| astral.state.job-prior-states-enforced | scoped | not-applicable | API enforces (Joan excluded) |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run paths |
| astral.ui.frontend-file-placement | scoped | conforms | `JobsApplied.tsx` in pages tree |
| astral.ui.naming-conventions | scoped | conforms | consistent naming |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests at tip |
| orch.git.commit-vocabulary | universal | conforms | standard prefixes |
| orch.git.flow-direction-inviolable | universal | conforms | sub topology |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1464/AST-1479-…` |
| orch.git.merge-on-checkout | universal | conforms | no rebase issues |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | merge only |
| orch.git.no-dev-agent-branches | universal | conforms | branch naming |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1464 worktree |
| orch.git.three-permanent-branches | universal | conforms | vs origin/dev |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no policy invention |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–3 match plan |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty manifest landed |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Ada assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | no bypass |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.in-place-live-refresh | needs-discussion | `status: proposed` — hook usage matches solution shape; Joan flagged at plan (see discuss) |
| pattern.ui.icon-control | not cited | post-applied R/I/X/G via existing `CandidateJobRowActions` (out of scope to edit) |
| pattern.ui.shared-button-roles | not cited | n/a |

## Plan adherence

`81f1c7b1` matches approved plan across all three stages:

- **`config.py`:** `APPLIED_JOB_STATES` (four post-applied states) + `assert all(s in JOB_STATES …)`; Jobs → Applied nav enabled (Responded still disabled).
- **`api_jobs.py`:** `view=applied` branch calls `list_jobs(states=APPLIED_JOB_STATES, …)` with `_flatten_grades`; auth unchanged.
- **`JobsApplied.tsx`:** real flat table, `view=applied` fetch, `useInPlaceLiveRefresh`, `useCandidateJobActions`, notes modal, error toast, post-applied `CandidateJobRowActions` only — no report modal / skip / sections.

Sibling boundaries honored (no `JobsRecommended`, `JobAnalysisReportModal`, or `CandidateJobRowActions` edits). `blockedBy` AST-1473 Done — no gate issue. Estimate 3 fits.

## Frame diff

`APPLIED_JOB_STATES` added to `config.py`; Jobs → Applied nav `enabled: False` removed. API `view=applied` now returns rows instead of `[]`. No manifest/schema frame beyond config state list.

## Findings

### discuss

**`pattern.ui.in-place-live-refresh` — proposed, not approved**

Joan plan discuss carries forward. `JobsApplied` correctly uses `useInPlaceLiveRefresh` per sibling list pattern. Not a product fix — track pattern promotion separately; no stage rewrite needed.

**Publish ref vs `origin/dev` — `test_api_jobs.py` missing AST-1453 block**

Branch tip (679 lines) vs dev (853 lines): `TestAst1453SkippedEditMetaAndPut` absent on publish ref (ftr-sync ancestry, not introduced by `d4d152db`). AST-1479's own `test_list_applied_uses_applied_job_states` is correct. Restore at epic merge / `merge-child` — not AST-1479 product scope.

### advisory

- Applied nav badge count still absent in `api_system._get_job_counts` — plan-documented out of scope.
- Inline `style` on sort indicator / Actions column width — minor; matches informal patterns on sibling pages.
- Publish ref includes ftr-sync commits from siblings; scoped two-dot product delta ≡ `81f1c7b1` only.

## What's solid

- Config state set matches `CandidateJobRowActions` post-applied branch exactly.
- API branch mirrors `recommended` / `skipped` shape.
- Page wiring: load, actions, notes modal, 409 toast — complete.
- Betty coverage: config (`TestAst1479AppliedJobStatesAndNav`), API (`test_list_applied_uses_applied_job_states`), page (4 cases §6c) — manifest-aligned.
- No parallel POST logic; no scope smuggling in product commits.

## Recommended actions (downstream)

1. **merge-child:** restore AST-1453 `test_api_jobs.py` block when integrating ftr onto dev.
2. **Optional:** promote `pattern.ui.in-place-live-refresh` to approved if citation enforcement tightens.

context_tokens≈52000
