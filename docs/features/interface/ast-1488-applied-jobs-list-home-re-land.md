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

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1488
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1485/AST-1488-applied-jobs-list-home-re-land` @ `f9d38262827744b317e0173e68bd8be96c3ad366`

## Traceability

AC1→St1+St3; AC2→St2+St3; AC3→St3; AC4→St3; AC5→St1; AC6→all — parent AC fully mapped; St1→config/nav (AC1, AC5); St2→`view=applied` API (AC2, AC6); St3→`JobsApplied` restore (AC1–AC4, AC6); no orphan stages.

## Findings

### acceptable — procedural

- **Location:** Linear assignee at fetch (`Ada Lovelace`, not Joan).
- **Finding:** Skill §1 expects Joan assignee; Chuckles spawn is authoritative for this pass.
- **Recommendation:** None blocking — proceed.

### discuss — pattern citation

- **Location:** Parent Architectural definition + plan Stage 3 (`pattern.ui.in-place-live-refresh`).
- **Finding:** Pattern catalog entry is `status: proposed`, not `approved`.
- **Recommendation:** Accept for this re-land — hook exists on dev, plan matches `# Solution shape`, AUTHORING note permits pre-approval use; inherited from parent definition. No plan rewrite required.

### acceptable — self-assessment

- **Location:** Plan `## Estimate` only (no conf/risk block).
- **Finding:** Missing formal self-assessment axes.
- **Recommendation:** Acceptable — byte-faithful AST-1479 restore (`81f1c7b1`), explicit scope gate, Betty tests already on dev define the bar.

## R6 checklist (summary)

- **Definition fidelity:** Plan implements exactly the AST-1485/AST-1488 child slice — three scoped files only; boundaries respected (no Responded, badge counts, mark-applied, analysis/detail).
- **Scope gate:** Files Changed matches ticket `## Scope`; no out-of-scope files.
- **Layer compliance:** `ui` → `utils` imports only; no business logic in wrong layer; page uses shared hooks/components, not duplicated transition policy.
- **Config compliance:** `APPLIED_JOB_STATES` + nav enablement in `config.py`; API imports config constant; no inline state sets in API/page steps.
- **File placement:** `JobsApplied.tsx` stays in `src/pages/` (flat); no new subdirectories.
- **Pattern compliance:** `pattern.ui.icon-control` (`approved`) — restore keeps `CandidateJobRowActions` icon-controls; in-place refresh via existing hook matches sibling list pages.
- **DRY / scope:** Prior-art restore strategy avoids reinventing page shape; explicit stop-if-drift guard in Stage 3.
- **Tests alignment:** Plan names the three AST-1479 component tests on dev; staged changes satisfy `TestAst1479AppliedJobStatesAndNav`, `test_list_applied_uses_applied_job_states`, and `JobsApplied — AST-1479 applied list home` expectations verified against current test tree.

No `fix-now` findings. R1–R5 pass for this scoped re-land.

context_tokens≈52000

[plan-rubric] PROCEED (Commit: f9d38262827744b317e0173e68bd8be96c3ad366) faithful AST-1479 re-land

## Review

- Publish ref: `sub/AST-1485/AST-1488-applied-jobs-list-home-re-land`
- Build tip: `632a73daf80ddae40033c4934a4c93ef3c301081`

## Radia review

# Radia review — AST-1488

**Status gate:** Tests Passed (spawn prompt; trusted)  
**Publish ref:** `origin/sub/AST-1485/AST-1488-applied-jobs-list-home-re-land` @ `e883c0db843951c98605eb0fea5f3e11245eddf8`  
**Baseline:** `origin/dev` (three-dot diff)  
**Rubric:** code-rubric.v1  

---

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1488  
**Publish ref:** `origin/sub/AST-1485/AST-1488-applied-jobs-list-home-re-land` @ `e883c0db843951c98605eb0fea5f3e11245eddf8`  
**Overall:** CLEAN  

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
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `ast-1488-applied-jobs-list-home-re-land.md` |
| astral.git.betty-no-src-or-features | scoped | not-applicable | engineer commits: `src/` only; Betty bible/docs separate |
| astral.git.engineer-test-tree-ban | scoped | conforms | no `tests/` in engineer product commits |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `list_view` retains `@require_auth` |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | no core/external diff |
| astral.layers.import-direction | scoped | conforms | `api_jobs.py` adds `utils.config` import only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts paths |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | state set in config; API filters; page renders rows |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed paths |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed paths |
| astral.seed.define-approved | scoped | not-applicable | no seed paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | no DB/migration paths |
| astral.standards.debug-contract-gated | scoped | not-applicable | no `debug=` surfaces |
| astral.standards.dry-and-focused-functions | scoped | conforms | mirrors `recommended` API branch + prior-art page |
| astral.standards.in-scope-only | scoped | conforms | product delta = 3 scoped files only |
| astral.standards.logging-via-utils | scoped | conforms | no new logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | ticket id only in file header comment |
| astral.standards.no-cross-contamination | scoped | conforms | no sibling-file edits |
| astral.standards.no-hardcoded-sets | scoped | conforms | `APPLIED_JOB_STATES` in `config.py` |
| astral.standards.public-then-helpers | scoped | not-applicable | no new module API surface |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data imports added |
| astral.state.core-decides-transitions | scoped | conforms | actions via `candidate_action` / `useCandidateJobActions` |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no transition-policy changes |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run/dispatch paths |
| astral.ui.frontend-file-placement | scoped | conforms | `JobsApplied.tsx` in `src/pages/` |
| astral.ui.naming-conventions | scoped | conforms | matches sibling list pages |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server/worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1488)` @ `e883c0db` |
| orch.git.commit-vocabulary | universal | conforms | standard commit vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1485/…` publish ref |
| orch.git.ftr-sub-topology | universal | conforms | child under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | no rebase/cherry-pick evidence |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no destructive git |
| orch.git.no-dev-agent-branches | universal | conforms | standard `sub/` ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1485 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` only |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | byte-faithful AST-1479 restore |
| orch.pipeline.plan-is-bible | universal | conforms | all three stages match plan |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Interface child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review |
| orch.roles.archie-approves-statutes | universal | conforms | n/a to code delta |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty bible + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path violations |

**Straggler (C4):** Joan plan-rubric APPROVED @ `f9d38262`; no Excluded statute list — no stragglers.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.in-place-live-refresh | needs-discussion | `status: proposed`; hook usage matches solution shape; Joan accepted at plan |
| pattern.ui.icon-control | conforms | via existing `CandidateJobRowActions` (consumption correct) |

## Plan adherence

Diff vs `origin/dev` matches approved re-land across all three stages:

- **`config.py`:** `APPLIED_JOB_STATES` + nav enablement; Responded stays disabled.
- **`api_jobs.py`:** `view=applied` → `list_jobs(states=APPLIED_JOB_STATES, …)`.
- **`JobsApplied.tsx`:** restore from `81f1c7b1` (header comment only differs).

Scope gate honored. Estimate **3** fits. No out-of-scope files in product commits.

## Frame diff

`APPLIED_JOB_STATES` in config; Applied nav enabled; `view=applied` returns rows; `JobsApplied` replaces stub. No new manifest keys beyond config state list.

## Findings

### discuss (non-blocking)

**`pattern.ui.in-place-live-refresh` — proposed, not approved** — Joan carry-forward; implementation correct; not a product fix.

### advisory

- Nav badge count for Applied still out of scope (`api_system._get_job_counts`).
- Inline `style` on sort/Actions column matches sibling pages.
- No fetch `.catch` — same as `JobsRecommended`.

## What's solid

- Byte-faithful AST-1479 product restore.
- Config/API/page wiring complete.
- Betty AST-1479 tests on `origin/dev` cover restored behavior.
- Three-file product footprint only.

## Recommended actions (downstream — Chuckles only)

1. Append verdict to issue doc; commit `docs(AST-1488): Radia review — clean`; push `origin/sub/…`.
2. Post slim upshot via `linear_proxy --as radia save-comment`.
3. Move AST-1488 → Review Posted; route PROCEED → User Testing per datt §3h.

context_tokens≈18000

---

```
[code-rubric] PROCEED (Commit: e883c0db843951c98605eb0fea5f3e11245eddf8) faithful AST-1479 re-land
```

## Test run (test-child)

Betty manifest (`docs/test-bible/frontend/pages.md` § AST-1488). Tip at run: `e883c0db`. No product fixes.

```bash
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_uses_applied_job_states \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default \
  tests/component/utils/test_config.py::TestAst1479AppliedJobStatesAndNav \
  -q
# 4 passed

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsApplied.test.tsx \
  --testNamePattern="AST-1479"
# 4 passed
```

## Bug: AST-1498 — CANDIDATE_APPLIED job missing from Applied screen

### As-is

A job whose `job.state` is `CANDIDATE_APPLIED` does not appear on `/jobs/applied` for the selected candidate, even though AST-1488 re-landed `APPLIED_JOB_STATES` (includes `CANDIDATE_APPLIED`), the `view=applied` API branch, and a real `JobsApplied` page on tip (`origin/dev` @ `ca860885`).

### To-be

For the selected candidate, every job in `APPLIED_JOB_STATES` — including `CANDIDATE_APPLIED` — appears on `/jobs/applied` with the same candidate scoping Susan expects from Recommended (mark-applied → row leaves Recommended → row appears on Applied).

### Repro

Fixture shape (file/JSON — no SQL seed in Astral):

```json
{
  "candidate_id": "cand-a",
  "company": {
    "short_name": "alice@example.com-cand-a",
    "candidate_id": null,
    "state": "METEORITE"
  },
  "job": {
    "astral_job_id": "job-applied-1",
    "company": "alice@example.com-cand-a",
    "state": "CANDIDATE_APPLIED",
    "job_title": "Role A"
  }
}
```

Steps:

1. Select `cand-a` in the candidate picker.
2. `GET /api/jobs/job-applied-1` (detail) → `state` is `CANDIDATE_APPLIED`.
3. `GET /api/jobs?view=applied&candidate_id=cand-a` → `[]` (missing row).
4. `/jobs/applied` UI → “No applied jobs yet”.

Same failure mode for any applied-state job whose `company` row exists but `company.candidate_id` is NULL/empty while `job.company` is not matched by the subquery. Meteorite/stem companies (`{stem}-{candidate_id}` or `meteorite-{candidate_id}` per `METEORITE_CONFIG`) are the highest-risk shape after AST-1495 stem attach; vetted roster companies with NULL `candidate_id` are also excluded.

Secondary UX repro (no bad data): mount `/jobs/applied` before `CandidateContext` hydration finishes — `selectedId` may be null, `load()` returns early, page shows definitive empty copy instead of loading.

### Root cause

**Not** a missing `CANDIDATE_APPLIED` entry in `APPLIED_JOB_STATES` or a missing `view=applied` branch — those are present and component-tested (AST-1479 manifest).

Applied list membership is determined entirely by `database.list_jobs` candidate scoping:

```sql
company IN (SELECT short_name FROM company WHERE candidate_id = ?)
```

Jobs have no direct `candidate_id` column (`docs/features/candidate/CANDIDATE_DATA_MODEL.md`). When `company.candidate_id` is NULL/empty or ≠ the picker value, the job is **silently excluded** even though `job.state` is `CANDIDATE_APPLIED`.

`POST /api/jobs/<id>/candidate_action` (mark-applied / post-applied actions) does **not** accept or persist `candidate_id`, so transitions cannot repair stale company linkage at mark-applied time.

`JobsApplied.tsx` does not gate on `candidatesHydrated` (unlike `JobsJobDetail.tsx`), so a pre-hydration fetch skip can flash a false empty state.

### Proposed change

**Stage 1 — `src/ui/api/api_jobs.py` (`list_view` applied branch only)**

Add a private helper in this file, e.g. `_list_applied_jobs_for_candidate(candidate_id: Optional[str]) -> list[dict]`, used only by the `view=applied` branch:

1. **Primary pass (unchanged):** `list_jobs(states=list(APPLIED_JOB_STATES), candidate_id=candidate_id, order_by="state_changed_at")`.

2. **Supplement + repair pass** when `candidate_id` is non-empty after strip:
   - Import `get_company`, `update_company` from `src.core.roster` (same as `api_companies.py`).
   - Import `METEORITE_CONFIG` from config.
   - Compute `default_meteorite = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)` and suffix `f"-{cid}"`.
   - Iterate `list_jobs(states=list(APPLIED_JOB_STATES), candidate_id=None, order_by="state_changed_at")` (dedupe by `astral_job_id` against primary pass).
   - For each candidate row whose `job.company` equals `default_meteorite` **or** ends with suffix `f"-{cid}"`:
     - Load company via `get_company(co_name)`; skip if no row.
     - Let `existing = (company.get("candidate_id") or "").strip()`.
     - If `existing == cid`: append job to results.
     - If `existing == ""`: call `update_company(co_name, candidate_id=cid)` then append (repair-on-read for stem/meteorite companies missing linkage).
     - If `existing` is another candidate: skip (do not steal).
   - Re-sort merged rows by `state_changed_at` descending (match skipped branch pattern).

3. Return `[ _flatten_grades(r) for r in rows ]` from `list_view` as today.

Do **not** change `list_jobs` in `database.py` (out of parent Component scope). Do **not** change recommended/skipped/in_review branches.

**Stage 2 — `src/ui/api/api_jobs.py` (`candidate_action`)**

1. Read optional `candidate_id` from JSON body **or** query param `candidate_id` (either form OK — Applied page may use body).

2. After `get_job` succeeds and before `transition_job_state`, when `candidate_id` is provided and action maps to a post-applied state (`applied`, `interview`, `rejected`, `ghosted`) or `applied` from review-like mark:
   - `co = get_company(job.get("company") or "")`; if missing, proceed unchanged (no new company creation in this bug).
   - If `co` exists: let `existing = (co.get("candidate_id") or "").strip()`, `cid = candidate_id.strip()`.
     - If `existing == ""`: `update_company(co["short_name"], candidate_id=cid)`.
     - Elif `existing != cid`: return `409` with `{"error": "Job belongs to another candidate"}`.

3. Existing `set_candidate_result` + `transition_job_state` logic unchanged.

**Stage 3 — `src/ui/frontend/src/pages/JobsApplied.tsx`**

1. Destructure `candidatesHydrated` from `useCandidate()`.

2. While `!candidatesHydrated`, render loading status (`Loading...`) — do not show “No applied jobs yet”.

3. When calling `actions.requestAction`, ensure post-applied POST includes `candidate_id: selectedId` — implement inline in this file if shared `candidateJobActions.ts` is out of scope: wrap confirm path or extend the existing `useCandidateJobActions` call with a thin local POST that adds `candidate_id` to the JSON body (keep using shared modal/busy/error plumbing).

4. Do **not** add Recommended-style sections, report modal, or nav changes.

⚠️ **Decision:** Repair-on-read + repair-at-action for stem/meteorite `{stem}-{candidate_id}` / `meteorite-{candidate_id}` companies only in the supplement pass — avoids widening Applied list to all NULL-`candidate_id` companies globally (which could cross candidates if slug collision ever existed). If UAT still fails on a vetted slug, escalate with job id — may need a targeted backfill, not a broader list widen.

### Blast radius

| Area | Risk |
|------|------|
| `GET view=applied` | Extra unscoped scan + optional `update_company` on read for stem/meteorite NULL linkage; other views untouched |
| `POST candidate_action` | New optional `candidate_id` validation/repair; 409 when company owned by another candidate |
| `JobsApplied.tsx` | Hydration gate + POST body delta only |
| Recommended mark-applied | Still uses shared `useCandidateJobActions` — **make-fix should pass `candidate_id` from Recommended in the same epic pass** via query/body (may require `[scope-gate]` to touch `candidateJobActions.ts` + `JobsRecommended.tsx` if inline wrap is insufficient) |
| Betty tests | Expect qa-fix `[bug-repro]` for AST-1498: applied job with NULL `company.candidate_id` on stem company appears after fix; existing AST-1479 tests must stay green |

### What must still hold

- Parent AST-1485 AC: Applied nav enabled; `APPLIED_JOB_STATES` unchanged; Responded nav stays disabled; Recommended/Skipped/In Review behavior unchanged.
- AST-1488 boundaries: no Responded list, no nav badge counts, no Job Analysis Report / Job Detail from Applied page.
- `candidate_action` still enforces `JOB_STATES` priors via `transition_job_state` (409 + toast on illegal hops).
- Post-applied row actions remain `CandidateJobRowActions` R/I/X/G via shared notes modal.
- Do not invent parallel state lists — keep using `APPLIED_JOB_STATES` from config.
