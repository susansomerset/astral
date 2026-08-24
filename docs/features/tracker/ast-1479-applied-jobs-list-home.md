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
