<!-- linear-archive: AST-311 archived 2026-06-03 -->

## Linear archive (AST-311)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-311/candidate-action-states-state-machine-and-db-layer  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-312

### Description

Add CANDIDATE_GHOSTED to JOB_STATES and TRACKER_CONFIG job_state_transitions in [config.py](<http://config.py>) alongside CANDIDATE_REJECTED (both terminal by default but reapplyable). Add backwards transitions from any CANDIDATE\_\* state back to CANDIDATE_REVIEW in job_state_transitions. Add job_data.candidate_results as a tracked JSON object in [tracker.py](<http://tracker.py>) with save/get helpers. Shape: { applied: {timestamp, notes}, interview: {timestamp, notes}, rejected: {timestamp, notes}, ghosted: {timestamp, notes} }. Each entry is written at the moment the candidate fires the action — timestamp auto-set server-side, notes optional. Entries are append-style per action (last write wins per key).

### Comments

#### chuckles — 2026-05-18T19:34:41.140Z
## Landed on origin/dev — Chuckles

- Local `dev` had prep-uat cherry-picks (`14bfe05e`, `978ed254`); added review/resolution docs (`5657adf0`, `f490b86a`)
- Pushed **`origin/dev`** @ `f490b86a`
- Deleted `origin/ftr/AST-311-candidate-action-states-state-machine-and`

(Full merge of ftr still conflicted on tests; product + tests landed via cherry-pick after your ftr merge `c258f189`.)

— Chuckles

#### chuckles — 2026-05-18T19:25:13.875Z
## UAT Ready — Chuckles

**AST-311** is standalone (no child branches).

**Feature branch:** `origin/ftr/AST-311-candidate-action-states-state-machine-and`

**Local `dev`:** Cherry-picked product commits (full `git merge` conflicted in `tests/component/ui/api/test_api_jobs.py`; avoided by taking `feat` + `fix` only):

1. `14bfe05e` — candidate_results helpers + `candidate_action` API
2. `978ed254` — 409 JSON on invalid state transition

Parent **ftr** branch left on origin for **finish-up** after UAT.

Restart the app if it is running, then test `POST /api/jobs/<id>/candidate_action` and skip → `transition_job_state`.

If testing fails on `dev`:
```
git reset --hard origin/dev
```

— Chuckles

#### chuckles — 2026-05-18T19:22:10.893Z
## finish-up blocked — Chuckles

AST-311 is **User Testing**, not **PR Ready** (proceeded with merge attempt per your request).

**Product not yet on `origin/dev`** — `get_candidate_results`, `set_candidate_result`, and `POST …/candidate_action` exist only on `origin/ftr/AST-311-candidate-action-states-state-machine-and`.

**Merge conflict** merging that branch into `dev`:

- `tests/component/ui/api/test_api_jobs.py`

Did not push `origin/dev`. **Not deleted** the feature branch.

@susan — resolve the conflict on `dev` (or rebase the ftr branch onto current `origin/dev`), push, then re-run finish-up or say the word and I’ll retry after you’ve pushed.

— Chuckles

#### hedy — 2026-05-16T23:07:44.643Z
Review feedback resolved. Branch `ftr/AST-311` ready for **prep-uat**. Commit: `a9bc73f2` — Hedy

#### hedy — 2026-05-16T22:49:56.177Z
Review feedback resolved. Branch `ftr/AST-311` ready for UAT merge. Commit: `a9bc73f2` — Hedy

**discuss:** `candidate_action` / `skip` return **409** JSON on illegal `transition_job_state`. `CANDIDATE_APPLIED` ← `BUILD_ARTIFACTS` intentional (see AST-302 Resolution).

#### radia — 2026-05-16T22:42:55.753Z
## review-astral (Radia)

**Diff:** `origin/dev...origin/ftr/AST-311`

**Summary:** `candidate_results` + `candidate_action` API + `CANDIDATE_GHOSTED` topology look good. **0 fix-now** · **2 discuss**

- **discuss:** `candidate_action` / `skip` do not catch `transition_job_state` `ValueError` — illegal transitions will 500; return 400/409 JSON.
- **discuss:** `CANDIDATE_APPLIED` from `BUILD_ARTIFACTS` — confirm product.

**Doc commit:** `6e8c79c9` on `origin/ftr/AST-311`

— Radia

#### hedy — 2026-05-16T22:38:34.300Z
**test-astral** — Hedy

**Integration:** `dev-hedy` after merges through `origin/ftr/AST-311` (Betty ref **`origin/ftr/AST-311`** @ **`d9643862`**).

**Command:**
`python3 -m pytest tests/component/core/test_tracker.py::TestAst311CandidateResults tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_candidate_action_applied_records_result tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_candidate_action_invalid_returns_400 tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_skip_job_updates_state -q` → **5 passed**

**Result:** **PASS** — no product fixes; no new commits.

— Hedy

#### betty — 2026-05-16T21:55:35.152Z
**[qa-astral] publish fix** — Betty tests on **`origin/ftr/AST-311`** @ **`d9643862`** (cherry-pick `50fdb1bb`).

— Betty

#### betty — 2026-05-16T21:54:53.688Z
**[qa-astral] branch correction** — published to **`origin/ftr/AST-311`** @ `5225d57a`. Ignore `hedy/ast-311-…` in the earlier manifest.

**Manifest** (run on **`origin/ftr/AST-311`**):
1. `tests/component/core/test_tracker.py::TestAst311CandidateResults`
2. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_candidate_action_applied_records_result`
3. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_candidate_action_invalid_returns_400`
4. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_skip_job_updates_state`

— Betty

#### betty — 2026-05-16T21:43:49.017Z
QA manifest by Betty.

**Integration:** `origin/hedy/ast-311-candidate-action-states-state-machine-and-db-layer` @ `5225d57a`.

**Manifest (run in order):**
1. `tests/component/core/test_tracker.py::TestAst311CandidateResults`
2. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_candidate_action_applied_records_result`
3. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_candidate_action_invalid_returns_400`
4. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_skip_job_updates_state`

**Test commit:** `50fdb1bb` on `dev-betty` (cherry-picked `5225d57a`)

— Betty

#### hedy — 2026-05-16T21:36:30.987Z
Built by Hedy.

**Branch:** `hedy/ast-311-candidate-action-states-state-machine-and-db-layer`
**Commit:** `cfa13d16` (`dev-hedy`, pushed to `origin/hedy/ast-311-candidate-action-states-state-machine-and-db-layer`)
**Label review:** agree on all three

#### chuckles — 2026-05-16T21:29:53.345Z
## Plan Review — Chuckles

**Verdict: APPROVED**

Plan is faithful to the definition. No findings. ASTRAL_CODE_RULES compliance confirmed. Self-assessment is honest.

**Note:** Implementation already on `origin/dev` ([retroactive-pipeline] C2).

— Chuckles

#### susan — 2026-05-05T17:31:21.240Z
[check-linear]

Thread reviewed for Hedy queue pass.

- Latest activity is the new plan-ready handoff comment for this ticket.
- No additional request, question, or blocker requiring code/docs changes beyond the posted plan.

Action: no-op.

— Hedy (check-linear)

#### susan — 2026-05-04T21:35:46.209Z
**Plan ready (a-plan-linear / Hedy)**

- **Doc:** `docs/features/artifacts/ast-311-candidate-action-states-state-machine-and-db-layer.md` on `chuckles/ast-311-candidate-action-states-state-machine-and-db-layer`.
- **Commit:** `01dd70f3`
- **Self-assessment:** Scope **MAJOR-CHANGE**; Conf **Medium**; Risk **HIGH**.
- **Link:** https://github.com/susansomerset/astral/blob/chuckles/ast-311-candidate-action-states-state-machine-and-db-layer/docs/features/artifacts/ast-311-candidate-action-states-state-machine-and-db-layer.md

— Hedy

---

# AST-311 — Candidate Action States — State Machine and DB Layer

**Linear:** [AST-311](https://linear.app/astralcareermatch/issue/AST-311/candidate-action-states-state-machine-and-db-layer)  
**Feature branch:** `<agent>/ast-311-candidate-action-states-state-machine-and-db-layer`

## Summary

Add **`CANDIDATE_GHOSTED`** alongside **`CANDIDATE_REJECTED`** in **`JOB_STATES`** (terminal by default, re-applyable per Linear). Add **backwards** `prior_states` edges from each **`CANDIDATE_*`** outcome state back to **`CANDIDATE_REVIEW`** so a job can return to review when product allows. Introduce **`job_data.candidate_results`** as a structured object with keys **`applied`**, **`interview`**, **`rejected`**, **`ghosted`** — each value **`{ "timestamp": ISO8601 string, "notes": string }`** (or `null` when unset). **`tracker.py`** exposes **`get_candidate_results(job)`** / **`set_candidate_result(job_id, action_key, notes=None)`** (exact signatures after grep) that **merge** into `job_data` using existing save helpers. Timestamps are set **server-side** in the API/core layer at write time. **Last write wins** per action key unless product specifies append — Linear says “last write wins per key”; implement overwrite for that key’s object.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOB_STATES` additions/edits; any UI state ordering constants. | utils |
| `src/core/tracker.py` | Read/merge/write helpers for `job_data["candidate_results"]`. | core |
| `src/data/database.py` | Only if new column required — **prefer** JSON inside existing `job_data` blob; document if schema change unavoidable. | data |
| `src/ui/api/api_jobs.py` (or dedicated jobs mutation module) | Authenticated endpoints or existing PATCH paths that record candidate actions call tracker helpers — **no** dispatcher writes to `CANDIDATE_*` states. | ui |

## Stage 1: JOB_STATES topology

**Done when:** `validate_job_transition` (or equivalent on `dev`) accepts new states without violating `prior_states` rules.

1. Add `CANDIDATE_GHOSTED` mirroring `CANDIDATE_REJECTED` patterns.
2. For each `CANDIDATE_APPLIED` / `SKIPPED` / `INTERVIEW` / `REJECTED` / `GHOSTED`, add `CANDIDATE_REVIEW` to `prior_states` where backwards transition is allowed (exact list from Linear: “any CANDIDATE_*” — enumerate keys present on branch at implementation time).

## Stage 2: candidate_results shape

**Done when:** `get_job` returns `candidate_results` key inside `job_data` when present; missing key behaves as `{}`.

1. Define constant default shape in `tracker.py` module docstring.
2. Implement merge: `set_candidate_result` reads job, deep-merges `candidate_results[action] = {timestamp, notes}`, writes via `save_job_data`.

## Stage 3: API wiring

**Done when:** UI can persist at least one action end-to-end (reuse existing job update route if it exists; else add minimal POST under `/api/jobs/...` with `require_auth`).

1. Grep for job PATCH / candidate action handlers.
2. Wire timestamp `datetime.now(timezone.utc).isoformat()`.

## Self-Assessment

**Scope — `MAJOR-CHANGE`**  
Config + tracker + API surface.

**Conf — `Medium`**  
Depends on **AST-302** naming for `CANDIDATE_REVIEW` existing.

**Risk — `HIGH`**  
Wrong transitions corrupt funnel metrics.

## Self-review vs ASTRAL_CODE_RULES

§2.6 state machine; §3.3 no UI imports in `tracker.py`.

---

## Review stub (build)

Built by Hedy.

- **Branch:** `hedy/ast-311-candidate-action-states-state-machine-and-db-layer`
- **Integration:** `dev-hedy`
- **API:** `POST /api/jobs/<id>/candidate_action`, `skip` uses `transition_job_state`

---

## Radia review (review-astral 2026-05-16)

**Diff:** `origin/dev...origin/ftr/AST-311`

### What's solid

- `CANDIDATE_GHOSTED` in `JOB_STATES` with backwards edges to `CANDIDATE_REVIEW` on candidate outcome states.
- `get_candidate_results` / `set_candidate_result` server timestamps, last-write-wins per key, merge via `save_job_data`.
- `POST /api/jobs/<id>/candidate_action` maps actions → states; `skip` refactored to `transition_job_state` (§2.6).
- Tests cover tracker helpers and API happy/invalid paths.

### Issues

| Severity | Item |
|----------|------|
| **discuss** | `candidate_action` / `skip_job` do not catch `ValueError` from `transition_job_state` — illegal transitions will 500 instead of 4xx JSON; return 400/409 with message when `prior_states` fails. |
| **discuss** | `CANDIDATE_APPLIED` allows predecessor `BUILD_ARTIFACTS` — confirm Susan wants apply-without-review. |

### Recommended actions

| Action | Owner |
|--------|-------|
| Wrap `transition_job_state` in API routes; map `ValueError` → `{error: ...}` + 400/409 | Hedy |

**Counts:** 0 fix-now · 2 discuss · 0 advisory

— Radia

---

## Resolution (resolve-astral)

2026-05-16 — Radia **review-astral** (`origin/dev...origin/ftr/AST-311`).

| Item | Action |
|------|--------|
| **discuss** `candidate_action` / `skip` + `ValueError` | **`api_jobs.py`** — `transition_job_state` failures return **409** JSON `{"error": "…"}` instead of 500; component tests added. |
| **discuss** `CANDIDATE_APPLIED` ← `BUILD_ARTIFACTS` | **Intentional** — documented on **AST-302** Resolution; shared `prior_states` in `config.py`. |

