<!-- linear-archive: AST-302 archived 2026-06-03 -->

## Linear archive (AST-302)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-302/job-state-machine-artifacts-and-candidate-states  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-311; blocks: AST-307; blocks: AST-300

### Description

Retire PASSED_LIKE. LIKE analysis pass_state is now BUILD_ARTIFACTS. New states added to JOB_STATES and TRACKER_CONFIG job_state_transitions in [config.py](<http://config.py>): BUILD_ARTIFACTS (batch_criteria: limit 10, triggers artifact pipeline), BUILD_FAILED (error holding state), CANDIDATE_REVIEW (artifact draft ready, candidate owns content), CANDIDATE_APPLIED, CANDIDATE_SKIPPED, CANDIDATE_INTERVIEW, CANDIDATE_REJECTED. Candidate\_ states are candidate-only transitions — no dispatcher or batch runner may set them. Add save/get helpers in [tracker.py](<http://tracker.py>) for job_data.artifacts (resume_content, cover_letter). Config changes are complete; this feature covers the [tracker.py](<http://tracker.py>) helper layer and any UI state label/grouping updates needed.

### Comments

#### chuckles — 2026-05-18T19:17:58.587Z
## finish-up blocked — Chuckles

AST-302 is **Done**, not **PR Ready** (finish-up gate skipped for status).

Product is already on `origin/dev` (PR #139). Remaining commits on `origin/ftr/AST-302-job-state-machine-artifacts-and-candidate` (resolution doc + test manifest trim) **conflict** with current `dev` when merging:

- `tests/component/core/test_tracker.py`

**Not deleted** the feature branch — resolve conflict on `dev` or on the ftr branch, then re-run finish-up or push manually.

— Chuckles

#### hedy — 2026-05-16T23:07:44.040Z
Review feedback resolved. Branch `ftr/AST-302` ready for **prep-uat**. Commit: `b104b3a0` — Hedy

#### hedy — 2026-05-16T22:49:54.265Z
Review feedback resolved. Branch `ftr/AST-302` ready for UAT merge. Commit: `b104b3a0` — Hedy

**fix-now:** trimmed `TestAst309*` / `TestAst311*` from tracker manifest on this branch tip.
**discuss:** `CANDIDATE_APPLIED` ← `BUILD_ARTIFACTS` intentional (fast-path apply).

#### radia — 2026-05-16T22:42:53.408Z
## review-astral (Radia)

**Diff:** `origin/dev...origin/ftr/AST-302`

**Summary:** State machine + migration solid, but **tests on this branch will fail**. **1 fix-now** · **2 discuss**

- **fix-now:** `test_tracker.py` calls `normalize_cover_letter_artifact`, `save_job_artifact_cover_letter`, `get_candidate_results`, `set_candidate_result` — **not defined** in `tracker.py` on `origin/ftr/AST-302`. Trim tests to AST-302-only or do not publish 309/311 test classes on this branch.
- **discuss:** `CANDIDATE_APPLIED` allows `BUILD_ARTIFACTS` predecessor (skip review?).
- **discuss:** Cross-ticket test classes on wrong `ftr/*` tip.

**Doc commit:** `7f3eae8c` on `origin/ftr/AST-302`

— Radia

#### hedy — 2026-05-16T22:38:16.061Z
**test-astral** — Hedy

**Integration:** `dev-hedy` after `git merge origin/dev` + `git merge origin/ftr/AST-302` (Betty ref **`origin/ftr/AST-302`** @ **`c745be43`**).

**Commands:**
1. `python3 -m pytest tests/component/utils/test_config.py::TestAst302JobStates tests/component/core/test_tracker.py::TestAst302JobArtifacts tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_skip_job_updates_state -q` → **7 passed**
2. `cd src/ui/frontend && npm run test:component -- --run ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx` → **4 passed** (Vitest; manifest paths are frontend component tests)

**Result:** **PASS** — no product fixes; no new commits on `dev-hedy`.

— Hedy

#### betty — 2026-05-16T21:55:33.494Z
**[qa-astral] publish fix** — Betty tests now on **`origin/ftr/AST-302`** @ **`c745be43`** (cherry-pick `50fdb1bb` on top of `660964b8`). Use this ref for **test-astral**.

— Betty

#### betty — 2026-05-16T21:54:51.307Z
**[qa-astral] branch correction** — published to **`origin/ftr/AST-302`** @ `91455a43` (product `cfa13d16` + tests `50fdb1bb`). Ignore `hedy/ast-302-…` in the earlier manifest.

**Manifest unchanged** — run against **`origin/ftr/AST-302`**:
1. `tests/component/utils/test_config.py::TestAst302JobStates`
2. `tests/component/core/test_tracker.py::TestAst302JobArtifacts`
3. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default`
4. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_skip_job_updates_state`
5. `tests/component/frontend/pages/test_JobsRecommended.test.tsx`
6. `tests/component/frontend/pages/test_JobsSkipped.test.tsx`

— Betty

#### betty — 2026-05-16T21:43:46.313Z
QA manifest by Betty.

**Integration:** `origin/hedy/ast-302-job-state-machine-artifacts-and-candidate-states` @ `91455a43` (product `cfa13d16` + tests).

**Manifest (run in order):**
1. `tests/component/utils/test_config.py::TestAst302JobStates`
2. `tests/component/core/test_tracker.py::TestAst302JobArtifacts`
3. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default`
4. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_skip_job_updates_state`
5. `tests/component/frontend/pages/test_JobsRecommended.test.tsx`
6. `tests/component/frontend/pages/test_JobsSkipped.test.tsx`

**Test commit:** `50fdb1bb` (cherry-picked `91455a43` on feature branch)

— Betty

#### hedy — 2026-05-16T21:36:28.893Z
Built by Hedy.

**Branch:** `hedy/ast-302-job-state-machine-artifacts-and-candidate-states`
**Commit:** `cfa13d16` (`dev-hedy`, pushed to `origin/hedy/ast-302-job-state-machine-artifacts-and-candidate-states`)
**Label review:** agree on all three

#### chuckles — 2026-05-16T21:29:51.916Z
## Plan Review — Chuckles

**Verdict: APPROVED**

Plan is faithful to the definition. No findings. ASTRAL_CODE_RULES compliance confirmed. Self-assessment is honest (conf-LOW, risk-HIGH — plan addresses state machine and config-driven transitions).

**Note:** Implementation already on `origin/dev` ([retroactive-pipeline] C2).

— Chuckles

#### susan — 2026-05-05T17:31:22.617Z
[check-linear]

Thread reviewed for Hedy queue pass.

- Latest activity is the new plan-ready handoff comment for this ticket.
- No additional request, question, or blocker requiring code/docs changes beyond the posted plan.

Action: no-op.

— Hedy (check-linear)

#### susan — 2026-05-04T21:35:28.509Z
**Plan ready (a-plan-linear / Hedy)**

- **Doc:** `docs/features/artifacts/ast-302-job-state-machine-artifacts-and-candidate-states.md` on `chuckles/ast-302-job-state-machine-artifacts-and-candidate-states`.
- **Commit:** `c7e9659c`
- **Self-assessment:** Scope **MAJOR-CHANGE**; Conf **LOW**; Risk **HIGH**.
- **Link:** https://github.com/susansomerset/astral/blob/chuckles/ast-302-job-state-machine-artifacts-and-candidate-states/docs/features/artifacts/ast-302-job-state-machine-artifacts-and-candidate-states.md

— Hedy

---

# AST-302 — Job State Machine — Artifacts and Candidate States

**Linear:** [AST-302](https://linear.app/astralcareermatch/issue/AST-302/job-state-machine-artifacts-and-candidate-states)  
**Feature branch:** `<agent>/ast-302-job-state-machine-artifacts-and-candidate-states`

## Summary

Retire **`PASSED_LIKE`** as the post-LIKE success gate: introduce **`BUILD_ARTIFACTS`** (batch-capable, triggers artifact pipeline per Linear), **`BUILD_FAILED`**, **`CANDIDATE_REVIEW`**, and candidate outcome states **`CANDIDATE_APPLIED`**, **`CANDIDATE_SKIPPED`**, **`CANDIDATE_INTERVIEW`**, **`CANDIDATE_REJECTED`**. Candidate_* states are **UI / human** transitions only — **dispatcher** and **batch runners** must never assign them (enforce in the code paths that mutate job state today). Update **`CONSULT_CONFIG`** / any **`dispatch_tasks`** rows that reference **`PASSED_LIKE`**. Add **`tracker.py`** helpers to read/write **`job_data.artifacts.resume_content`** and **`job_data.artifacts.cover_letter`** without bypassing existing `save_job` / merge semantics. Refresh **`api_jobs`**, **`api_system`**, and frontend-facing state lists (`IN_REVIEW_STATES`, **`SKIPPED_STATES`**, nav counts) to use **`BUILD_ARTIFACTS`** where **`PASSED_LIKE`** appeared.

**Superseded in part by AST-479 / AST-478:** Automatic promotion **`PASSED_LIKE` → `BUILD_ARTIFACTS`** on DB open was removed; LIKE consult success now lands in **`PASSED_LIKE`** for the synthesis queue, then **`RECOMMENDED`**, with **`BUILD_ARTIFACTS`** reachable only after **`RECOMMENDED`** via UI (see parent **AST-478**). This doc’s original “retire PASSED_LIKE” migration narrative no longer matches runtime behavior.

⚠️ **Decision — `TRACKER_CONFIG.job_state_transitions`:** Linear text references legacy key; on current `dev`, transitions live in **`JOB_STATES[...]["prior_states"]`** only. This plan uses **`JOB_STATES`** / **`CONSULT_CONFIG`** / **`dispatch_tasks`** as the authoritative edit surfaces — do **not** resurrect a second transition table.

**Superseded in part (AST-479 / AST-478 family):** **`PASSED_LIKE`** is again the post-LIKE consult success gate because **`analysis_upshot`** dispatch runs from **`PASSED_LIKE`** before **`RECOMMENDED`**. The database hook that rewrote **`PASSED_LIKE` → `BUILD_ARTIFACTS`** on open is removed; **`BUILD_ARTIFACTS`** follows **`RECOMMENDED`** via UI/epic, not automated LIKE promotion.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOB_STATES` entries; `CONSULT_CONFIG["consult_like"]["pass_state"]`; `IN_REVIEW_STATES`, `PASSED_SCORE_GATED_STATES`, `SKIPPED_STATES` as needed; any nav/job view constants referencing `PASSED_LIKE`. | utils |
| `src/data/database.py` | Only if `dispatch_tasks` seed data or migrations embed state literals — align with new names. | data |
| `src/core/tracker.py` | `get_job_artifacts`, `save_job_artifact_resume_content`, `save_job_artifact_cover_letter` (exact names chosen to match existing `save_job_data` patterns — **grep** `job_data` / `artifacts` on `dev` before naming). | core |
| `src/core/dispatcher.py` (or consult batch modules) | Any transition from LIKE pass to artifact build must target **`BUILD_ARTIFACTS`**; error paths to **`BUILD_FAILED`**. | core |
| `src/ui/api/api_jobs.py` | Replace `PASSED_LIKE` list filters with **`BUILD_ARTIFACTS`** (or the final agreed “recommended jobs” state name). | ui |
| `src/ui/api/api_system.py` | Nav counts `/jobs/recommended` use new state. | ui |
| `src/ui/frontend` (if any) | Meteors / Jobs labels: search `PASSED_LIKE` string — update copy + API query params if embedded. | ui |

## Stage 1: JOB_STATES and consult pass

**Done when:** No remaining `PASSED_LIKE` string in executable code paths (docs import CSV optional).

1. Add `JOB_STATES` keys: `BUILD_ARTIFACTS`, `BUILD_FAILED`, `CANDIDATE_REVIEW`, `CANDIDATE_APPLIED`, `CANDIDATE_SKIPPED`, `CANDIDATE_INTERVIEW`, `CANDIDATE_REJECTED` with **`prior_states`** consistent with Linear (BUILD_ARTIFACTS follows LIKE pass; candidate states only from listed “human predecessor” states — **stop** on Linear if product intent for `prior_states` is ambiguous).
2. Remove or alias `PASSED_LIKE` — if removal breaks DB rows, add a **one-release** migration note: either migrate rows to `BUILD_ARTIFACTS` in `database.py` startup migration, or keep `PASSED_LIKE` as an alias key mapping to same `prior_states` until migration runs (pick one and document in Stage 1 commit message).
3. Set `CONSULT_CONFIG["consult_like"]["pass_state"]` to **`BUILD_ARTIFACTS`**.

## Stage 2: dispatch_tasks and batch triggers

**Done when:** Rows that triggered post-LIKE work now reference **`BUILD_ARTIFACTS`** as `trigger_state` (or equivalent column on `dev`).

1. Inspect `dispatch_tasks` table population (`database.sync_*` or seed SQL).
2. Update sort/limit criteria per Linear (`batch_criteria: limit 10` for artifact pipeline — express using the same structure other states use in this repo).

## Stage 3: tracker artifact helpers

**Done when:** Core modules can merge `resume_content` / `cover_letter` dicts into `job_data` through **one** code path reused by pipeline and tests.

1. Implement helpers in `tracker.py` calling into `database.save_job` / `save_job_data` (whichever exists) with deep-merge semantics matching jobs today.
2. Unit-level **manual** verification: load job, call helper, `get_job` shows merged artifacts.

## Stage 4: UI API and labels

**Done when:** Recommended jobs endpoint and nav counts match new state; no 500s when DB still has old state values if migration chosen in Stage 1.

1. Update `api_jobs.py` and `api_system.py` per grep hits.
2. Grep entire repo for `PASSED_LIKE` again.

## Self-Assessment

**Scope — `MAJOR-CHANGE`**  
Touches config registry, dispatch, tracker, UI lists — cross-cutting.

**Conf — `LOW`**  
State topology is product-critical; expect follow-up tickets when first live batch runs.

**Risk — `HIGH`**  
Wrong `prior_states` strands jobs or double-runs artifact batches.

## Self-review vs ASTRAL_CODE_RULES

§2.6 / §2.4 — batch_id pattern unchanged; only state names and triggers. §2.1 — literals only in `config.py`.

---

## Review stub (build)

Built by Hedy.

- **Branch:** `hedy/ast-302-job-state-machine-artifacts-and-candidate-states`
- **Integration:** `dev-hedy`

---

## Radia review (review-astral 2026-05-16)

**Diff:** `origin/dev...origin/ftr/AST-302`  
**Note:** Supersedes the premature Resolution above — full diff review below.

### What's solid

- `JOB_STATES` adds `BUILD_ARTIFACTS`, candidate funnel states, `BUILD_FAILED`; `CONSULT_CONFIG.consult_like.pass_state` → `BUILD_ARTIFACTS`.
- Idempotent `PASSED_LIKE` → `BUILD_ARTIFACTS` migration in `_ensure_job_schema`.
- `RECOMMENDED_JOB_STATES` + `api_jobs` / `api_system` nav counts updated; frontend tests use `BUILD_ARTIFACTS`.
- `get_job_artifacts` / `save_job_artifact_resume_content` follow existing `save_job_data` merge path (§2.6).

### Issues

| Severity | Item |
|----------|------|
| **fix-now** | `tests/component/core/test_tracker.py` on this branch defines `TestAst309CoverLetterArtifact` and `TestAst311CandidateResults` calling `normalize_cover_letter_artifact`, `save_job_artifact_cover_letter`, `get_candidate_results`, `set_candidate_result` — **those functions are not in `src/core/tracker.py` on `origin/ftr/AST-302`**. Component suite will fail until tests are trimmed to AST-302-only **or** tracker helpers from AST-309/311 are removed from this branch’s test file. |
| **discuss** | `CANDIDATE_APPLIED` `prior_states` includes `BUILD_ARTIFACTS` (skip review) — confirm product intent. |
| **discuss** | Cross-ticket tests on the AST-302 feature branch blur publish boundaries (309/311 coverage belongs on their `ftr/*` tips). |

### Recommended actions

| Action | Owner |
|--------|-------|
| Remove or gate `TestAst309*` / `TestAst311*` from AST-302 publish until those tickets land tracker code on **this** branch | Hedy |
| Re-run Betty manifest on `dev-hedy` after fix | Hedy / Betty |

**Counts:** 1 fix-now · 2 discuss · 0 advisory

— Radia

---

## Resolution (resolve-astral)

2026-05-16 — Radia **review-astral** (`origin/dev...origin/ftr/AST-302`).

| Item | Action |
|------|--------|
| **fix-now** | Removed `TestAst309CoverLetterArtifact` and `TestAst311CandidateResults` from `test_tracker.py` on **`ftr/AST-302`** — those helpers ship on **AST-309** / **AST-311** branches; Betty’s shared test commit had cross-ticket classes that failed import on the 302-only tip. |
| **discuss** `CANDIDATE_APPLIED` ← `BUILD_ARTIFACTS` | **Intentional** — same fast-path as `CANDIDATE_SKIPPED` so a candidate can mark applied/skipped without waiting in `CANDIDATE_REVIEW`. |
| **discuss** cross-ticket tests | Addressed by trimming 302 branch manifest to `TestAst302JobArtifacts` only. |
