# Generate Artifacts and Cancel job transitions API (Recommended Job Modal)

**Linear:** [AST-562](https://linear.app/astralcareermatch/issue/AST-562/generate-artifacts-and-cancel-job-transitions-api-recommended-job)  
**Parent:** [AST-499](https://linear.app/astralcareermatch/issue/AST-499/recommended-job-modal)  
**Publish ref (origin):** `sub/AST-499/AST-562-generate-artifacts-cancel-job-transitions-api`

Candidate-facing **Generate Artifacts** and **Cancel** transitions for the Recommended Job Report: explicit UI/API only (never dispatch-driven entry into `BUILD_ARTIFACTS`); cancel returns `BUILD_ARTIFACTS` → `RECOMMENDED` and clears partial job build artifacts. Exposes config/manifest entries so **AST-565** (Katherine) wires buttons without hardcoded TS state machines. Does **not** ship React modal chrome, **Apply**, or `take_jd` schema work.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOB_STATES` edge for cancel; `JOB_BUILD_ARTIFACT_CLEAR_KEYS`; `JOBS_RECOMMENDED_PRIMARY_ACTIONS`; extend `build_state_ui_manifest()`; remove duplicate `jobs.recommended` dict key | utils |
| `src/core/tracker.py` | `clear_job_build_artifacts`, `cancel_artifact_build` (clear + release lock + transition) | core |
| `src/data/database.py` | `clear_job_batch_lock(astral_job_id)` — NULL `batch_id` / `batch_created_at` for one job | data |
| `src/ui/api/api_jobs.py` | `POST …/generate_artifacts`, `POST …/cancel_artifact_build` | ui |

**Out of scope:** `src/ui/frontend/**` ( **AST-565** ), `consult.py` post-batch **CANDIDATE_REVIEW** / **BUILD_FAILED** exits ( **AST-552** / artifact pipeline siblings ), `analysis_upshot` / `take_jd` ( **AST-561** ), **Apply** action, dispatcher changes, new dispatch rows.

---

## Stage 1: Config — state machine + manifest contract

**Done when:** `transition_job_state([id], "RECOMMENDED")` succeeds from `BUILD_ARTIFACTS`; `build_state_ui_manifest()["jobs"]["recommended"]["primary_actions_by_state"]` lists Generate/Cancel for the two states; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py` `JOB_STATES`, change **`RECOMMENDED`** `prior_states` from `["PASSED_LIKE", "PASSED_LIKE_RETRY"]` to **`["PASSED_LIKE", "PASSED_LIKE_RETRY", "BUILD_ARTIFACTS"]`** so cancel is legal (today cancel would raise `ValueError`).

2. Add module-level constant after `RECOMMENDED_JOB_STATES`:

   ```python
   JOB_BUILD_ARTIFACT_CLEAR_KEYS = (
       "resume_content",
       "cover_letter",
       "application_responses",
   )
   ```

   Keys are removed from `job_data.artifacts` on cancel only — **do not** touch `analysis_upshot`, grade blobs, or `candidate_results`.

3. Add **`JOBS_RECOMMENDED_PRIMARY_ACTIONS`** (single source for manifest + API docs):

   ```python
   JOBS_RECOMMENDED_PRIMARY_ACTIONS = {
       "RECOMMENDED": [
           {
               "action_key": "generate_artifacts",
               "label": "Generate Artifacts",
               "method": "POST",
               "path_suffix": "generate_artifacts",
           },
       ],
       "BUILD_ARTIFACTS": [
           {
               "action_key": "cancel_build",
               "label": "Cancel",
               "method": "POST",
               "path_suffix": "cancel_artifact_build",
           },
       ],
   }
   ```

   Assert every key in `JOBS_RECOMMENDED_PRIMARY_ACTIONS` is in `RECOMMENDED_JOB_STATES`.

4. In **`build_state_ui_manifest()`**, inside the surviving **`jobs["recommended"]`** block (remove the earlier duplicate `"recommended"` key at ~1258–1261 so only one block remains), add:

   ```python
   "primary_actions_by_state": {
       state: list(actions)
       for state, actions in JOBS_RECOMMENDED_PRIMARY_ACTIONS.items()
   },
   ```

5. Grep `src/` for assignments to **`BUILD_ARTIFACTS`** outside UI/API candidate paths (`pass_state`, `render_verdict`, `analysis_upshot`, consult batch). Confirm **AST-479** behavior unchanged — no dispatch auto-entry from **RECOMMENDED** / **PASSED_LIKE**.

⚠️ **Decision:** Dedicated **`POST /api/jobs/<id>/generate_artifacts`** and **`…/cancel_artifact_build`** routes (not new `candidate_action` keys) because cancel has artifact + batch-lock side effects and does not use `candidate_results`. Manifest `path_suffix` maps to those routes; Katherine adds thin fetch wrappers in **AST-565**.

---

## Stage 2: Tracker + data — clear artifacts and release batch lock

**Done when:** `tracker.cancel_artifact_build(astral_job_id)` on a job in `BUILD_ARTIFACTS` clears listed artifact keys, NULLs `batch_id`, and leaves job in `RECOMMENDED`; unit-testable via existing tracker test patterns.

1. In `src/data/database.py`, add:

   ```python
   def clear_job_batch_lock(astral_job_id: str) -> None:
       """Clear batch_id and batch_created_at for one job row (candidate cancel during BUILD_ARTIFACTS)."""
   ```

   Implementation: `UPDATE job SET batch_id = NULL, batch_created_at = NULL, updated_at = ? WHERE astral_job_id = ?`. No change to `save_job` nullable-column pattern.

2. In `src/core/tracker.py`, add **`clear_job_build_artifacts(astral_job_id: str) -> None`**:
   - Load job via `get_job`; if missing, raise `ValueError` (API maps to 404).
   - Read `job_data.artifacts` dict (via `get_job_artifacts`).
   - Build patch `{"artifacts": {k: {} for k in JOB_BUILD_ARTIFACT_CLEAR_KEYS if k in artifacts}}` — empty dict per key matches merge semantics used elsewhere ( **AST-552** Stage 4 ). If merge cannot remove a key, **stop** and comment on **AST-562** with options.
   - Call `save_job_data(astral_job_id, patch)` (merge=True).

3. In `src/core/tracker.py`, add **`cancel_artifact_build(astral_job_id: str) -> str`** returning final state `"RECOMMENDED"`:
   - Load job; raise `ValueError` if missing.
   - If `job["state"] != "BUILD_ARTIFACTS"`, raise `ValueError` with message `cancel only from BUILD_ARTIFACTS` (API → 409).
   - Call `clear_job_build_artifacts(astral_job_id)`.
   - If `job.get("batch_id")`, call `database.clear_job_batch_lock(astral_job_id)`.
   - Call `transition_job_state([astral_job_id], "RECOMMENDED")`.
   - Return `"RECOMMENDED"`.

4. Add **`start_artifact_build(astral_job_id: str) -> str`** in `tracker.py` returning `"BUILD_ARTIFACTS"`:
   - Load job; raise if missing.
   - If `job["state"] != "RECOMMENDED"`, raise `ValueError` with message `generate only from RECOMMENDED`.
   - Call `transition_job_state([astral_job_id], "BUILD_ARTIFACTS")`.
   - Return `"BUILD_ARTIFACTS"`.
   - **Do not** invoke dispatch or `run_resume_artifact_chain_for_job` — scheduler picks up `contemplate_job` on `BUILD_ARTIFACTS` per existing seed row.

⚠️ **Decision:** In-flight dispatch may still finish after cancel and briefly repopulate artifacts until the batch exits; Susan accepted log-based inspection. Do **not** add consult guards in this ticket.

---

## Stage 3: API routes

**Done when:** Authenticated POSTs return `{ok, state}` on success; illegal state returns **409** JSON `{"error": "…"}`; missing job **404**; pattern matches `skip_job` / `candidate_action`.

1. In `src/ui/api/api_jobs.py`, add:

   **`POST /api/jobs/<astral_job_id>/generate_artifacts`** (`@require_auth`):
   - `get_job`; 404 if missing.
   - Try `start_artifact_build(astral_job_id)` from tracker.
   - `ValueError` → **409** `jsonify({"error": str(exc)})`.
   - Success: `jsonify({"ok": True, "state": "BUILD_ARTIFACTS"})`.

2. Add **`POST /api/jobs/<astral_job_id>/cancel_artifact_build`** (`@require_auth`):
   - Same error mapping using `cancel_artifact_build`.
   - Success: `jsonify({"ok": True, "state": "RECOMMENDED"})`.

3. Do **not** add frontend files or change `candidateJobActions.ts` in this ticket.

---

## Stage 4: Verify

**Done when:** `python3 -m py_compile` passes on all touched `.py` files; Linear build comment lists Betty manifest extensions for **test-astral**.

1. Run:

   ```bash
   python3 -m py_compile src/utils/config.py src/data/database.py src/core/tracker.py src/ui/api/api_jobs.py
   ```

2. Linear comment for Betty (engineer does not edit tests): extend `tests/component/ui/api/test_api_jobs.py` — happy paths for generate/cancel, 409 wrong state, 404 missing job; `tests/component/utils/test_config.py` — manifest `primary_actions_by_state`; `tests/component/core/test_tracker.py` — cancel clears artifact keys and releases `batch_id`.

---

## Execution contract (for the developer agent)

- Execute stages in order. **Stop** if `save_job_data` merge cannot clear artifact keys — comment on **AST-562** with merge-behavior options; do not patch `consult.py` or frontend.
- Do not add files beyond the table unless Stage 2 requires only `clear_job_batch_lock` in `database.py`.
- Katherine (**AST-565**) consumes `GET /api/state_ui_manifest` → `jobs.recommended.primary_actions_by_state`; no parallel TS state→label maps for these two buttons.

Blocking questions use parent **AST-499** thread:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope — `Single-Component`**  
Config manifest + tracker helpers + two Flask routes + one small data-layer lock release; no React, no consult batch exit logic.

**Conf — `high`**  
Reuses **AST-311** transition/error patterns, **AST-522** manifest shape, and existing `BUILD_ARTIFACTS` / `contemplate_job` dispatch seed; cancel artifact key list is explicit in config.

**Risk — `Medium`**  
Wrong `prior_states` or incomplete artifact clear would strand jobs or show stale drafts; in-flight dispatch after cancel is a known race accepted by Susan.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Plan compliance |
|------|-----------------|
| §1.4 config SSOT | States, clear keys, and manifest actions live in `config.py`. |
| §2.4 batch lock | Cancel releases per-job `batch_id` via `clear_job_batch_lock`. |
| §2.6 state machine | Transitions only through `tracker.transition_job_state`; API does not write state directly. |
| §3.3 imports | API imports tracker only; tracker imports data for lock clear. |
| §3.5 naming | Helpers named by behavior (`start_artifact_build`, `cancel_artifact_build`, `clear_job_build_artifacts`). |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Built:** `origin/sub/AST-499/AST-562-generate-artifacts-cancel-job-transitions-api` @ `19f3f615`.

**Out of build scope (Betty / qa-astral):** Plan Stage 4 — `tests/component/ui/api/test_api_jobs.py` (generate/cancel happy paths, 409, 404); `tests/component/utils/test_config.py` (`primary_actions_by_state`); `tests/component/core/test_tracker.py` (cancel clears artifacts + releases `batch_id`).


---

## Radia review (AST-562)

**Diff:** `origin/dev...origin/sub/AST-499/AST-562-generate-artifacts-cancel-job-transitions-api` @ `deeca407` (product + tests; bible rollup includes sibling epic sections).

### What's solid

| Area | Notes |
|------|--------|
| **Plan fidelity (AC #5)** | `RECOMMENDED` → `BUILD_ARTIFACTS` only via `POST …/generate_artifacts` → `start_artifact_build`; no dispatch call in generate path. Cancel via `cancel_artifact_build` clears `JOB_BUILD_ARTIFACT_CLEAR_KEYS`, releases `batch_id`, returns `RECOMMENDED`. |
| **§1.4 / §2.6 config SSOT** | `JOB_STATES["RECOMMENDED"].prior_states` includes `BUILD_ARTIFACTS`; `JOBS_RECOMMENDED_PRIMARY_ACTIONS` + `primary_actions_by_state` in `build_state_ui_manifest()` for **AST-565**. |
| **§2.4 batch lock** | `clear_job_batch_lock` UPDATE matches plan; cancel gates on pre-transition `batch_id`. |
| **§3.3 layers** | `api_jobs.py` → `tracker` only; tracker → `database` for lock clear. |
| **§2.6 transitions** | State changes only through `transition_job_state`; API maps `ValueError` → 409 / missing job → 404 like `skip_job`. |
| **Artifact clear** | `clear_job_build_artifacts` uses **AST-552** `replace=True` key removal (not empty-dict merge); `test_cancel_persists_cleared_build_artifact_keys` enforces persisted DB AC. |
| **Tests** | Manifest §7.13zv narrowed run matches Betty manifest; `TestAst562GenerateCancelRoutes` + `TestAst562ArtifactBuildTransitions` cover happy/409/404 and lock release. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `api_jobs.py` + manifest | Publish tip also exposes **`POST …/approve_artifacts`** (**AST-552**) alongside **`generate_artifacts`** (**AST-562**). Both can move `RECOMMENDED` → `BUILD_ARTIFACTS`. Manifest `primary_actions_by_state` lists **generate** only — confirm **AST-565** wires manifest actions, not approve, for the Recommended Job Report **Generate Artifacts** button. |
| **discuss** | `docs/ASTRAL_TEST_BIBLE.md` on publish ref | Large bible diff includes **AST-549/551/552/558** sections (cumulative sub tip). Not an **AST-562** product defect; note for prep-uat bible merge only. |
| **advisory** | Plan Stage 2 race | In-flight `contemplate_job` after cancel may briefly repopulate artifacts — accepted in plan; no consult guard required this ticket. |

### Recommended actions

| Action | Owner |
|--------|--------|
| **resolve-astral:** none required for **AST-562** scope — no **fix-now** items. | Hedy |
| **AST-565:** consume `GET /api/state_ui_manifest` → `jobs.recommended.primary_actions_by_state`; POST `…/generate_artifacts` and `…/cancel_artifact_build` per `method` + `path_suffix`. | Katherine |
| **Susan (optional):** Confirm whether **approve_artifacts** stays a separate JAR-only entry (**AST-553**) vs deprecating in favor of generate-only on Recommended list. | Susan |

---

## Resolution (resolve-astral)

**Date:** 2026-06-03  
**Review:** Radia @ `deeca407` — **fix-now:** none for **AST-562** scope.  
**Publish ref:** `origin/sub/AST-499/AST-562-generate-artifacts-cancel-job-transitions-api` @ `8ae20990` (Radia review doc) → resolve tip after Joan `store-resolve-commit`.

### vs Radia review

| Item | Outcome |
|------|---------|
| **fix-now** | None — no product or plan edits required for **AST-562** scope. |
| **discuss** | **approve_artifacts** vs **generate_artifacts** — deferred to **AST-565** (manifest-driven wiring) and optional Susan call on **AST-553**; no API change this ticket. |
| **discuss** | Cumulative bible on sub tip — Betty/prep-uat merge concern only. |
| **advisory** | Post-cancel in-flight `contemplate_job` may briefly repopulate artifacts — plan-accepted race; no consult guard this ticket. |

**Product changes:** None. Publish tip already satisfies AC #5, config manifest contract, tracker cancel/clear (**AST-552** `replace=True` key removal), and API routes. Betty republished test fix @ `deeca407` after `[qa-handoff]` on `test_clear_job_build_artifacts_patches_listed_keys`.

### Radia doc handoff

Merged Radia **`docs(AST-562): Radia review — …`** @ `8ae20990` onto **`dev-hedy`** (§5); review table under **Radia review (AST-562)** above.

### Merge gates (§9a)

- **`origin/sub/AST-499/AST-562-generate-artifacts-cancel-job-transitions-api` → `origin/dev`:** clean.
- **Same sub → `origin/ftr/AST-499-recommended-job-modal`:** clean.

**Status:** **User Testing** — implementer assignee unchanged (**Hedy**). Parent **AST-499** rollup/prep-uat when siblings ready.
