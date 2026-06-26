<!-- linear-archive: AST-552 archived 2026-06-23 -->

## Linear archive (AST-552)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-552/build-artifacts-gate-and-structure-keyed-persistence-build-resume  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-300 — Build Resume Artifact  
**Blocked by / blocks / related:** parent: AST-300

### Description

## What this implements

Resume artifact batch dispatch runs only when job is **BUILD_ARTIFACTS** (explicit candidate approval after RECOMMENDED — **AST-478**). On successful chain completion, persist `job_data.artifacts.resume_content` with keys from candidate `artifacts.resume_structure`, contact/header sections as point-in-time snapshot at persist (**AST-477** Q4). Transition job to **CANDIDATE_REVIEW** on success or **BUILD_FAILED** on failure with no partial publish.

## Acceptance criteria

1. A job at **RECOMMENDED** does **not** start the resume chain until the candidate's explicit approval sets **BUILD_ARTIFACTS**.
2. A BUILD_ARTIFACTS job claimed by the artifact dispatch produces a complete resume chain run (all configured hops through the terminal resume-craft task) and persists `job_data.artifacts.resume_content`.
3. Persisted `resume_content` keys are a subset of the candidate's enabled structure section ids; contact sections present match the snapshot rules from **AST-477**.
4. On chain failure, the job is **BUILD_FAILED** (or configured error state) and no false CANDIDATE_REVIEW draft is shown.

## Boundaries

Does not redefine chain hop logic (**sibling Ada ticket**). Does not build JAR editor UI (**sibling Katherine ticket**). Cover letter (**AST-301** canceled) out of scope.

## Notes for planning

**AST-371** Done work predates **AST-477** — gap-fill only. Reuse `persist_job_artifact_from_parsed` patterns where applicable. Dispatcher/tracker/gazer integration per Hedy domain.

## Git branch (authoritative)

Per **orientation-astral** § Branch law: parent **ftr/AST-300-build-resume-artifact**, child **sub/AST-300/<child-id>-build-artifacts-gate-persistence**.

### Comments

#### radia — 2026-06-03T00:42:18.452Z
**Review** — `origin/dev...origin/sub/AST-300/AST-552-build-artifacts-gate-persistence` (scoped ~653 LOC in gate/persist paths; sub tip is composite with sibling epic work).

**Doc:** [ast-552 plan + review](https://github.com/susansomerset/astral/blob/sub/AST-300/AST-552-build-artifacts-gate-persistence/docs/features/artifacts/ast-552-build-artifacts-gate-and-structure-keyed-persistence.md) @ `45ae0014`

**fix-now:** none for acceptance criteria

**discuss**
- `tracker.py` — plan named `parsed_matches_job_resume_content` for persist gate; code uses `parsed_matches_resume_content_shape` (+ `agent_payload`); `parsed_matches_job_resume_content` is tested but unused in `persist_job_artifact_from_parsed`. `job_has_persisted_resume_body` enforces non-contact after persist — likely fine; align helper or drop duplicate on resolve.
- `consult.py` `_run_job_artifact_entry_batch` — if `CANDIDATE_REVIEW` transition raises `ValueError`, job may stay **BUILD_ARTIFACTS** with `resume_content` already saved.
- publish ref three-dot diff includes non–AST-552 files (`agent.py`, intake `config`, etc.) — resolve against this ticket’s commits, not whole sub tip blindly.

**advisory**
- `evaluate_jd_batch` `jd_score` write on same branch — confirm sibling ownership.
- `RESUME_SECTION_CATALOG` in `build_job_token_context` — good **AST-551** alignment.

**AC spot-check:** only `approve_artifacts` sets **BUILD_ARTIFACTS** from product code; batch exit → **BUILD_FAILED** + `clear_job_artifact_resume_content` or **CANDIDATE_REVIEW** per tests.

#### betty — 2026-06-03T00:30:20.705Z
**Manifest** (`origin/sub/AST-300/AST-552-build-artifacts-gate-persistence` @ `934385e0`)

`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `7a2ae2adad0dd394905aa49d264b9a3b576d645c`

1. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_from_recommended`
2. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_wrong_state_returns_409`
3. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_invalid_transition_returns_409`
4. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_missing_job_returns_404`
5. `tests/component/core/test_tracker.py::TestAst552BuildArtifactsGate`
6. `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_runs_chain_then_cover_letter_for_contemplate_job`
7. `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_errors_skip_cover_letter`
8. `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_empty_persist_build_failed`

Narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_from_recommended \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_wrong_state_returns_409 \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_invalid_transition_returns_409 \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_missing_job_returns_404 \
  tests/component/core/test_tracker.py::TestAst552BuildArtifactsGate \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_runs_chain_then_cover_letter_for_contemplate_job \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_errors_skip_cover_letter \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_empty_persist_build_failed
```

Bible §7.13zs (**AST-552**). Chain hop wiring covered by sibling **AST-551** on integration branch — not in this manifest scope.

— Betty

#### hedy — 2026-06-02T22:32:10.034Z
Plan: `docs/features/artifacts/ast-552-build-artifacts-gate-and-structure-keyed-persistence.md`

https://github.com/susansomerset/astral/blob/sub/AST-300/AST-552-build-artifacts-gate-persistence/docs/features/artifacts/ast-552-build-artifacts-gate-and-structure-keyed-persistence.md

**Scope:** `scope-Single-Component` — `api_jobs` approve route, tracker structure-aware persist gate, consult post-batch **CANDIDATE_REVIEW** / **BUILD_FAILED** only.

**Conf:** `conf-Medium` — **AST-518** / **AST-477** helpers exist; terminal JSON shape depends on **AST-551** output matching structure ids.

**Risk:** `risk-HIGH` — Wrong transitions or auto-dispatch from **RECOMMENDED** violate **AST-478** and strand jobs without a valid draft.

**Publish ref:** `origin/sub/AST-300/AST-552-build-artifacts-gate-persistence` @ `5ac9e4eb` (plan-only; already on ref).

**UAT note:** Approve API is backend-only until **AST-553** wires JAR; curl against `POST …/approve_artifacts` from **RECOMMENDED** for gate smoke.

#### hedy — 2026-06-02T22:31:20.903Z
Plan: [ast-552-build-artifacts-gate-and-structure-keyed-persistence.md](https://github.com/susansomerset/astral/blob/sub/AST-300/AST-552-build-artifacts-gate-persistence/docs/features/artifacts/ast-552-build-artifacts-gate-and-structure-keyed-persistence.md) (`origin/sub/AST-300/AST-552-build-artifacts-gate-persistence` @ `5ac9e4eb`).

**Self-assessment**
- **Scope — Single-Component:** `api_jobs.py` approve route, `tracker.py` structure-aware persist gate + optional rollback helper, `consult.py` post-batch **CANDIDATE_REVIEW** / **BUILD_FAILED** only.
- **Conf — Medium:** **AST-518** / **AST-477** helpers exist; terminal JSON contract depends on **AST-551** (Ada) — plan stops if incompatible.
- **Risk — HIGH:** Wrong transitions strand jobs in **BUILD_ARTIFACTS** or show **CANDIDATE_REVIEW** without a valid draft; auto-dispatch from **RECOMMENDED** would violate **AST-478**.

**Out of scope in this plan:** chain hops (**AST-551**), JAR approve UI + draft tabs (**AST-553**). UAT approve via new API until Katherine lands UI.

**Betty manifest hints (test-astral):** extend `tests/component/core/test_consult.py` (`TestAst371ResumeArtifactDispatch`), `tests/component/core/test_tracker.py` (`TestPersistJobArtifactFromParsed`, `TestAst518JobResumeArtifacts`), `tests/component/ui/api/test_api_jobs.py` (approve route).

---

# BUILD_ARTIFACTS gate and structure-keyed persistence (Build Resume Artifact)

**Linear:** [AST-552](https://linear.app/astralcareermatch/issue/AST-552/build-artifacts-gate-and-structure-keyed-persistence-build-resume)  
**Parent:** [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact)  
**Publish ref (origin):** `sub/AST-300/AST-552-build-artifacts-gate-persistence`

## Summary

Close the **AST-300** integration gap left by **AST-371** / **AST-518** before **AST-477**: resume artifact batch work must run only for jobs in **BUILD_ARTIFACTS** (explicit candidate approval after **RECOMMENDED**, per **AST-478**), persist **`job_data.artifacts.resume_content`** using each candidate's **enabled** `artifacts.resume_structure` section ids (contact snapshot at persist time), and transition jobs to **CANDIDATE_REVIEW** on a successful terminal chain with non-empty persisted resume, or **BUILD_FAILED** on failure with **no** draft-ready state and **no** partial `resume_content` publish. Chain hop logic and prompt wiring stay on sibling **AST-551** (Ada); structure-driven JAR draft tabs stay on sibling **AST-553** (Katherine).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_jobs.py` | Candidate-only transition **RECOMMENDED → BUILD_ARTIFACTS** (approve action); 409 on illegal `prior_states`. | ui |
| `src/core/tracker.py` | Structure-aware resume persist gate (`parsed_matches` / slice path); optional `clear_job_artifact_resume_content` for failure rollback. | core |
| `src/core/consult.py` | After each job in `_run_job_artifact_entry_batch`, transition **CANDIDATE_REVIEW** or **BUILD_FAILED**; no transition on empty persist. | core |
| `src/core/dispatcher.py` | No code change expected — verify job claim uses row `trigger_state` only (already **BUILD_ARTIFACTS**). | core |
| `src/utils/config.py` | Comment-only on `BUILD_CONFIG["artifact_shapes"]["resume_content"]` if needed (runtime subset = structure). | utils |

**Out of scope (sibling tickets):** `src/core/agent.py` chain hops / `run_next` (**AST-551**), Manage Tasks prompts, `JobAnalysisReportModal` approve button and draft tabs (**AST-553**), cover letter pipeline (**AST-301** canceled).

## Stage 1: RECOMMENDED → BUILD_ARTIFACTS gate (API only)

**Done when:** `POST` approve from **RECOMMENDED** sets **BUILD_ARTIFACTS**; jobs in **RECOMMENDED** are not claimed by `contemplate_job` dispatch; grep shows no consult/dispatch path auto-assigns **BUILD_ARTIFACTS** from **RECOMMENDED**, **PASSED_LIKE**, or **consult_like** pass.

1. Grep repo for `BUILD_ARTIFACTS` assignments outside UI/API candidate paths: `consult_like`, `pass_state`, `database` open hooks, `render_verdict`, `analysis_upshot`. Confirm **AST-479** behavior remains (**PASSED_LIKE** / **RECOMMENDED** only; no auto **BUILD_ARTIFACTS**).
2. In `src/ui/api/api_jobs.py`, extend `_CANDIDATE_ACTION_STATE` **or** add dedicated route `POST /api/jobs/<astral_job_id>/approve_artifacts` with `@require_auth`:
   - Load job via `get_job`; 404 if missing.
   - If `job["state"] != "RECOMMENDED"`, return **409** JSON `{"error": "…"}` (message states approval only from RECOMMENDED).
   - Call `transition_job_state([astral_job_id], "BUILD_ARTIFACTS")`; catch `ValueError` → **409** with message (same pattern as `skip_job` / `candidate_action`).
   - Return `{"ok": true, "state": "BUILD_ARTIFACTS"}`.
3. Do **not** add React approve UI in this ticket (**AST-553** owns JAR). Document in Linear build comment that Susan can UAT approve via API/curl until UI lands.

⚠️ **Decision:** Use a **dedicated** `approve_artifacts` route (not `candidate_action`) so **BUILD_ARTIFACTS** stays dispatcher/batch-only per **AST-302** ("candidate_* transitions only from UI") without overloading `candidate_results` keys.

## Stage 2: Structure-aware resume persist match

**Done when:** Terminal `do_task` persist accepts parsed JSON keyed to a **subset** of the job candidate's enabled structure ids (not all global `artifact_shapes` required keys); `save_job_artifact_resume_content` still filters via `_prepare_job_resume_content` (**AST-518**).

1. In `src/core/tracker.py`, add `parsed_matches_job_resume_content(astral_job_id: str, parsed: Any) -> bool`:
   - Return `False` if `parsed` is not a `dict`.
   - Load candidate via `_candidate_data_for_job(astral_job_id)`; `structure = candidate_mod.resolve_resume_structure(cd)`.
   - Build `allowed = set(candidate_mod.enabled_resume_section_ids(structure))`.
   - Require **at least one** enabled **non-contact** section id (exclude `RESUME_STRUCTURE_CONTACT_SECTION_IDS`) present in `parsed` with a non-empty string after strip.
   - Do **not** require every `BUILD_CONFIG["artifact_shapes"]["resume_content"]` required key.
2. In `persist_job_artifact_from_parsed`, replace `parsed_matches_artifact_shape(parsed, "resume_content")` check with `parsed_matches_job_resume_content(astral_job_id, parsed)`.
3. Keep `slice_parsed_for_artifact_shape(parsed, "resume_content")` **or** replace slice with `filter_content_to_resume_structure(parsed, structure, allow_contact=True)` then pass to `save_job_artifact_resume_content` — prefer filter path so orphan keys from Ada's terminal hop never touch DB.
4. Leave cover-letter shape logic unchanged.

⚠️ **Decision:** Structure-aware **match** gate lives in **tracker** (Hedy); terminal hop **JSON shape** from the model is validated by **AST-551**. If terminal hop returns nested blobs, **stop** and comment on **AST-552** referencing **AST-551** — do not add promotion logic here.

## Stage 3: Post-batch job state transitions

**Done when:** After `_run_job_artifact_entry_batch` processes each job, success with non-empty `resume_content` → **CANDIDATE_REVIEW**; chain failure or empty persist → **BUILD_FAILED**; failed jobs do not remain in **BUILD_ARTIFACTS** as if ready for review.

1. In `src/core/consult.py`, inside `_run_job_artifact_entry_batch` loop (after `run_resume_artifact_chain_for_job` returns):
   - `aid = job["astral_job_id"]`.
   - If `not r.get("success")`: call `tracker.transition_job_state([aid], "BUILD_FAILED")` inside try/except; on `ValueError`, log warning and count as error (do not raise). Increment `errors`. **Do not** call `_run_cover_letter_for_job`. Continue.
   - On success: `row = tracker.get_job(aid) or job`; `rc = tracker.get_job_artifacts(row).get("resume_content")`.
   - If `rc` is not a non-empty dict **or** no enabled non-contact section has a non-empty string in `rc` (reuse `candidate_mod` helpers with job candidate data): treat as failure — `transition_job_state([aid], "BUILD_FAILED")`; increment `errors`; continue.
   - Else: `transition_job_state([aid], "CANDIDATE_REVIEW")`; increment `passed`; then if `entry_task_key == "contemplate_job"`, await `_run_cover_letter_for_job` (preserve **AST-369** resume-first cover sequencing; cover letter out of parent resume-only scope but already on integration line).
2. Use `tracker.transition_job_state` directly for artifact outcomes — **not** `_transition_job_state_for_task` (no scored consult config on Phase E hops).
3. Ensure no code path transitions to **CANDIDATE_REVIEW** when `r.get("success")` is false.

⚠️ **Decision:** **BUILD_FAILED** is set on any resume entry batch failure, including empty post-chain persist, so the Recommended list does not show a false "Ready" job (**AST-300** AC #6). Susan may re-approve from **RECOMMENDED** only if product adds a repair path later — not in this ticket.

## Stage 4: No partial publish on failure

**Done when:** A failed job in Stage 3 has no `resume_content` left from that failed run (or content unchanged from pre-run snapshot).

1. Before the chain call in the loop, optionally snapshot `before = copy of get_job_artifacts(job).get("resume_content")` only if needed for rollback tests.
2. On the failure branch in Stage 3 (chain fail or empty persist), if `get_job_artifacts` shows `resume_content` that was written during this hop (terminal persist on a hop that still returned failure upstream — edge case), call new helper `clear_job_artifact_resume_content(astral_job_id: str)` in `tracker.py` that `save_job_data(..., {"artifacts": {"resume_content": {}}}, merge=True)` or merge-delete key per existing `save_job_data` merge semantics — **grep** `save_job_data` merge behavior before implementing.
3. If merge cannot delete a key cleanly, **stop** and comment on **AST-552** with two options: (A) merge empty dict `{}` as canonical "no draft", (B) explicit null sentinel agreed with Susan.

## Stage 5: Verify dispatch claim gate (read-only)

**Done when:** Confirmed `get_new_job_batch` / dispatch claim for `trigger_state="BUILD_ARTIFACTS"` never selects `state="RECOMMENDED"` rows.

1. Read `src/core/dispatcher.py` and `src/data/database.py` claim path for job batches; confirm claim filters on `trigger_state` from the dispatch row, not `_INPUT_STATE_TO_TASK`.
2. No product change unless grep finds a bug — if found, fix in this ticket and note in Linear comment.

## Stage 6: Verify

**Done when:** `python3 -m py_compile` passes on all touched `.py` files; Betty manifest entries noted in Linear comment for `test-astral` (engineer does not add tests).

1. `python3 -m py_compile src/core/consult.py src/core/tracker.py src/ui/api/api_jobs.py`
2. Linear comment for Betty: extend `tests/component/core/test_consult.py` (`TestAst371ResumeArtifactDispatch`), `tests/component/core/test_tracker.py` (`TestPersistJobArtifactFromParsed`, `TestAst518JobResumeArtifacts`), `tests/component/ui/api/test_api_jobs.py` (approve route).

## Execution contract (for the developer agent)

- Execute stages in order. **Stop** if **AST-551** terminal hop JSON is incompatible with Stage 2 — comment on **AST-552**, do not patch `agent.py` chain logic.
- Do not add files beyond the table unless Stage 4 rollback requires a one-line helper in `tracker.py`.
- Do not implement JAR approve button or draft save UI (**AST-553**).

## Self-Assessment

**Scope — `Single-Component`**  
Touches `api_jobs.py`, `tracker.py`, and `consult.py` artifact batch exit path only; no dispatcher schema or frontend components.

**Conf — `Medium`**  
**AST-518** / **AST-477** helpers exist; remaining work is approve API, structure-aware persist gate, and explicit post-batch transitions. Terminal JSON contract depends on **AST-551** landing compatible output.

**Risk — `HIGH`**  
Incorrect transitions strand jobs in **BUILD_ARTIFACTS** or **CANDIDATE_REVIEW** without a valid draft; auto-dispatch from **RECOMMENDED** would violate **AST-478** cost gate.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuse `_prepare_job_resume_content`, `enabled_resume_section_ids`, `transition_job_state`; one batch exit path in `_run_job_artifact_entry_batch`. |
| §2.1 config | No new state lists; `JOB_STATES` / `RECOMMENDED_JOB_STATES` already correct. |
| §2.4 batch | Preserves `batch_id` claim; per-job transitions after chain completes. |
| §2.6 state machine | All transitions via `tracker.transition_job_state`; UI approve only for **RECOMMENDED → BUILD_ARTIFACTS**; batch sets **CANDIDATE_REVIEW** / **BUILD_FAILED** only. |
| §3.3 imports | `consult` may call `tracker` / `candidate`; no new `data` imports from `consult`. |
| §3.5 naming | New helpers named by behavior (`parsed_matches_job_resume_content`, `clear_job_artifact_resume_content`). |

No unresolved conflicts — plan is implementable once **AST-551** terminal output is structure-keyed.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-300/AST-552-build-artifacts-gate-persistence` (publish ref). **AST-552 footprint** (~653 LOC in 9 paths); sub tip also carries sibling epic work (~4.5k LOC / 61 files) — findings below apply to the gate/persist scope.

### What's solid

| Area | Notes |
|------|--------|
| **AC #1 gate** | `POST /api/jobs/<id>/approve_artifacts` is the only product path that sets **BUILD_ARTIFACTS** (grep on publish ref). **RECOMMENDED** check + **409** on illegal transition matches existing `skip_job` / `candidate_action` patterns. |
| **AC #2–3 persist** | `persist_job_artifact_from_parsed` uses `parsed_matches_resume_content_shape` + `filter_content_to_resume_structure` + `_prepare_job_resume_content`; terminal persist gated to `finalize_job_resume` in `agent.do_task`. |
| **AC #4 / #6 outcomes** | `_run_job_artifact_entry_batch`: chain failure or empty/non-contact body → **BUILD_FAILED** + `clear_job_artifact_resume_content`; success with body → **CANDIDATE_REVIEW** then cover letter. Tests in `test_consult.py` / `test_tracker.py` / `test_api_jobs.py` lock the branches. |
| **§2.4 / §2.6** | Per-job transitions via `tracker.transition_job_state` after batch processing; no scored-task transition helper misuse. |
| **§3.3 layers** | `api_jobs` → `transition_job_state`; `consult` → `tracker` / `candidate` import at function scope for catalog token — no new `data` from `consult`. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `tracker.py` | Plan Stage 2 named `parsed_matches_job_resume_content` for the persist gate; implementation persists on `parsed_matches_resume_content_shape` (any enabled section, supports `agent_payload` wrapper). `parsed_matches_job_resume_content` is implemented and tested but unused in `persist_job_artifact_from_parsed`. Post-persist `job_has_persisted_resume_body` enforces non-contact — behavior likely correct; confirm whether to wire the plan-named helper or drop duplicate. |
| **discuss** | `consult.py` `_run_job_artifact_entry_batch` | If `transition_job_state(..., "CANDIDATE_REVIEW")` raises **ValueError**, job can remain **BUILD_ARTIFACTS** with `resume_content` already written (logged warning, counted error). Rare config bug; worth a one-line recovery (**BUILD_FAILED**?) or documented manual fix. |
| **discuss** | publish ref composite | Sub branch includes **AST-551**-adjacent `agent.py` / `config.py` intake+dispatch work not in this ticket's file table. **resolve-astral** should target this ticket's commits on the sub tip, not assume every file in the three-dot diff is **AST-552**. |
| **advisory** | `consult.py` | `evaluate_jd_batch` adds `jd_score` persistence — outside **AST-552** plan; verify sibling ownership so it does not surprise UAT. |
| **advisory** | `consult.py` | `RESUME_SECTION_CATALOG` in `build_job_token_context` — good **AST-551** alignment; not listed in plan table. |

### Recommended actions

| Action | Owner |
|--------|--------|
| **resolve-astral:** cherry-pick Joan review doc SHA if needed; implement any **discuss** cleanup on `dev-hedy` → publish ref. | Hedy |
| Optional: use `parsed_matches_job_resume_content` in persist path **or** remove dead helper after confirming shape helper is canonical. | Hedy |
| UAT approve via `POST …/approve_artifacts` until **AST-553** JAR button ships (per plan Stage 1). | Susan |

## Resolution (Hedy)

**Date:** 2026-06-03  
**Review ref:** Radia comment on **AST-552** (`45ae0014` doc already on publish ref)

| Discuss item | Resolution |
|--------------|------------|
| Persist gate helper alignment | `persist_job_artifact_from_parsed` now uses `parsed_matches_job_resume_content` (plan Stage 2). Helper updated to unwrap `agent_payload` via `_resume_payload_body` so **AST-551** terminal JSON still matches. `parsed_matches_resume_content_shape` remains for **AST-551** shape checks elsewhere; post-persist `job_has_persisted_resume_body` unchanged. |
| **CANDIDATE_REVIEW** transition **ValueError** | On failure after successful persist, attempt **BUILD_FAILED** transition and `clear_job_artifact_resume_content` so job does not remain **BUILD_ARTIFACTS** with a draft. |
| Composite publish ref | Product fix commits scoped to `tracker.py` / `consult.py` only; no changes to sibling **AST-551** `agent.py` paths on this resolve pass. |
| Advisory: `evaluate_jd_batch` **jd_score** | Out of **AST-552** scope — sibling ownership; no product change. |
| Advisory: **RESUME_SECTION_CATALOG** token | **AST-551** alignment; no change. |

**fix-now:** none required (Radia AC spot-check clean).
