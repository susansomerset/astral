# AST-1488 — Applied jobs list home (re-land)

**Linear:** [AST-1488](https://linear.app/astralcareermatch/issue/AST-1488)
**Parent:** [AST-1485](https://linear.app/astralcareermatch/issue/AST-1485) — Enable Applied job list in nav
**Publish ref:** `sub/AST-1485/AST-1488-applied-jobs-list-home-re-land`

Restore the AST-1479 vertical slice that was wiped during AST-1476 conflict resolution while component tests remained on `origin/dev`. Today Jobs → Applied is still `"enabled": False`, `GET /api/jobs?view=applied` falls through to `[]`, and `JobsApplied.tsx` is an empty `ListPage` stub. This ticket re-lands config state list + nav enablement, the `view=applied` API branch, and the real Applied page with shared post-applied row actions — not mark-applied entry points (AST-1464 siblings) or Responded list.

**Prior art (canonical product delta):** commit `81f1c7b189cf709aaa7a235d08c76b91a3cd794f` (`code(AST-1479): applied jobs list home`). Plan `docs/features/tracker/ast-1479-applied-jobs-list-home.md` on `origin/dev`. Restore that product shape; do not invent a new design.

## Scope gate

Ticket **## Scope** (only these files / kinds of change):

| File | Allowed change |
|------|----------------|
| `src/utils/config.py` | Named applied-view state list (parallel to `RECOMMENDED_JOB_STATES` / `SKIPPED_STATES`); enable Jobs → Applied in `NAV_CONFIG` |
| `src/ui/api/api_jobs.py` | Implement `view=applied` list (today else-branch returns `[]`) |
| `src/ui/frontend/src/pages/JobsApplied.tsx` | Replace stub with real applied list + shared candidate actions |

Out of scope (do not touch): `CandidateJobRowActions`, `JobsRecommended`, `JobAnalysisReportModal`, `api_system.py` nav-count map, mark-applied / report Skip (siblings), Responded nav/list, Applied badge counts, Job Detail / Analysis Report from Applied.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `APPLIED_JOB_STATES`; enable Applied nav item | utils |
| `src/ui/api/api_jobs.py` | Import `APPLIED_JOB_STATES`; `view=applied` branch | ui |
| `src/ui/frontend/src/pages/JobsApplied.tsx` | Real list + actions + notes modal + live refresh | ui |

## Stage 1: Config — applied-view states + nav

**Done when:** `APPLIED_JOB_STATES` is importable from `config` and lists exactly the four post-applied states already targeted by `CandidateJobRowActions`’s post-applied branch; Jobs → Applied in `NAV_CONFIG` is enabled the same way as Recommended/Skipped (no `"enabled": False`); Responded remains `"enabled": False`.

1. In `src/utils/config.py`, immediately after `RECOMMENDED_JOB_STATES` (currently near the `# Recommended jobs list + nav counts` comment), add:

   ```python
   # Applied jobs list + nav — post-applied candidate outcomes (AST-1488 re-land of AST-1479).
   APPLIED_JOB_STATES = [
       "CANDIDATE_APPLIED",
       "CANDIDATE_INTERVIEW",
       "CANDIDATE_REJECTED",
       "CANDIDATE_GHOSTED",
   ]
   assert all(s in JOB_STATES for s in APPLIED_JOB_STATES)
   ```

   ⚠️ **Decision:** Name `APPLIED_JOB_STATES` (parallel to `RECOMMENDED_JOB_STATES`) — same name and membership as AST-1479 so existing Betty tests (`TestAst1479AppliedJobStatesAndNav`, `test_list_applied_uses_applied_job_states`) pass without rename. Membership matches the post-applied icon set in `CandidateJobRowActions` (`CANDIDATE_APPLIED` / `INTERVIEW` / `REJECTED` / `GHOSTED`). Do **not** add `CANDIDATE_REVIEW` or Recommended-pipeline states.

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

**Done when:** `/jobs/applied` shows a non-stub list for the selected candidate: rows from `view=applied`, Actions column mounts `CandidateJobRowActions` with `onAction` → shared notes modal → `candidate_action`, list refreshes in place after success, and failed actions surface a visible error toast (no silent no-op). Empty state copy when there are no rows.

1. Replace the entire contents of `src/ui/frontend/src/pages/JobsApplied.tsx`. Do **not** keep the empty `ListPage` stub. **Restore the page body from** `git show 81f1c7b189cf709aaa7a235d08c76b91a3cd794f:src/ui/frontend/src/pages/JobsApplied.tsx`, with only this edit: change the file header comment from `AST-1479` to `AST-1488 (re-land of AST-1479)`.

2. Required shape (must match that commit / sibling list wiring):
   - `useCandidate` → `selectedId`
   - `useInPlaceLiveRefresh` → `loading` / `beginRefresh` / `endRefresh`
   - `useCandidateJobActions(load)` → `requestAction` / notes modal / errors
   - `api` for `GET /api/jobs?view=applied&candidate_id=…`
   - `CandidateJobRowActions`, `CandidateActionNotesModal`, `Toast`, `Time`
   - In-file `sortAppliedJobs` helper (title / company / state / `state_changed_at`)
   - Default sort: `state_changed_at` descending
   - Flat table columns: **Actions | Job Title | Company | State | Updated**
   - Empty copy: `No applied jobs yet`; loading: `Loading...`
   - Toast when `actions.error` is set (same `useEffect` pattern as `JobsRecommended`)
   - `CandidateJobRowActions` with `state` + `onAction` only — no `onSkip` / `onViewAnalysis` / `onResurrect`

3. Do **not** open Job Analysis Report or Job Detail from this page. Do **not** add Recommended-style state sections or a `build_state_ui_manifest` `jobs.applied` block.

⚠️ **Decision:** Flat table, not Recommended-style state sections. Ticket Scope allows only the applied-view **state list** + nav flip in config — inventing UI-section config / manifest keys would exceed Scope. Nav badge count in `api_system._get_job_counts` stays out of scope.

⚠️ **Decision:** Prefer byte-faithful restore from `81f1c7b1` over rewriting from `JobsRecommended` — that commit already passed Joan/Radia and matches Betty’s AST-1479 tests still on `origin/dev`. If hooks/import paths have drifted since that commit, stop and comment on the parent (do not invent a new page shape).

## Estimate

Confirm Chuckles estimate: 3 — agree

## Traceability

AC1→St1+St3 (nav omit `enabled` + real `JobsApplied`); AC2→St2+St3 (`view=applied` list + empty copy); AC3→St3 (`CandidateJobRowActions` + `useCandidateJobActions` + notes modal + live refresh); AC4→St3 (Toast on `actions.error`; API 409 via `postCandidateAction`); AC5→St1 (Responded stays disabled; Recommended/Skipped/In Review untouched); AC6→all stages (restore product so existing AST-1479 tests pass).
