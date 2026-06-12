# AST-534 — Honor dispatch task_key in dispatcher, consult, and artifact entry

**Linear:** [AST-534](https://linear.app/astralcareermatch/issue/AST-534/honor-dispatch-task-key-in-dispatcher-consult-and-artifact-entry-bug)  
**Parent:** [AST-533](https://linear.app/astralcareermatch/issue/AST-533/bug-scheduled-actions-ignore-dispatch-task-key-consult-hardcodes)  
**Publish ref:** `sub/AST-533/AST-534-honor-dispatch-task-key-core-routing` (origin only)

Scheduled Actions and Auto dispatch must execute the `task_key` on the active `dispatch_task` row as the first LLM hop. Today `dispatcher._run_unified` passes only `trigger_state` into `consult.run_consult_task`, which re-derives the runner from `_INPUT_STATE_TO_TASK` and artifact helpers that hardcode `BUILD_CONFIG['resume_artifact_chain']['first_task_key']` (`contemplate_job`). Susan's UAT repro — Run on `anticipate_scan` @ `BUILD_ARTIFACTS` with `run_next` cleared — still runs `contemplate_job`. This ticket fixes the runtime entry path only; `trigger_state` continues to drive entity claim.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/dispatcher.py` | Pass dispatch row `task_key` into every `run_consult_task` call | core |
| `src/core/consult.py` | Add `dispatch_task_key` param; route job dispatch by row key; generalize artifact entry batch | core |
| `src/core/agent.py` | `run_resume_artifact_chain_for_job`: optional `first_task_key` override (dispatch row wins over BUILD_CONFIG) | core |
| `tests/component/core/test_consult.py` | Update job `run_consult_task` call sites; add AST-534 routing tests | tests |
| `tests/component/core/test_dispatcher.py` | Assert `_run_unified` forwards row `task_key` to consult | tests |

**Out of scope (sibling AST-535):** `dispatch_task` unique constraint, roster `TO_WATCH` trio routing, company `run_company_task` task_key routing, `ASTRAL_TEST_BIBLE` prose updates, AST-529 caller tokens.

---

## Stage 1: Agent artifact chain entry accepts explicit first hop

**Done when:** `run_resume_artifact_chain_for_job` runs the caller-supplied task key as hop 1 when provided; default behavior unchanged when omitted.

1. In `src/core/agent.py`, on `async def run_resume_artifact_chain_for_job(...)`, add keyword-only parameter `first_task_key: Optional[str] = None` after `store_agent_data`.
2. Replace the block that reads `first_key` from `BUILD_CONFIG['resume_artifact_chain']['first_task_key']` with:
   - `entry_key = (first_task_key or "").strip() or (chain_cfg.get("first_task_key") or "").strip()`
   - Use `entry_key` everywhere the function currently uses `first_key` (validation against `TASK_CONFIG`, `_prep_live_content(..., scoring_task_key=entry_key)`, and `do_task(entry_key, ...)`).
3. Keep the existing `ValueError` when the resolved key is empty or missing from `TASK_CONFIG`.

⚠️ **Decision:** Dispatch rows override BUILD_CONFIG for resume-chain entry; BUILD_CONFIG remains the default for non-dispatch callers (craft/workbench paths that call `run_resume_artifact_chain_for_job` without `first_task_key`).

---

## Stage 2: Consult routes job dispatch by row task_key

**Done when:** `run_consult_task` for `entity_type == "job"` executes handlers keyed by `dispatch_task_key`, not `_INPUT_STATE_TO_TASK[input_state]`; artifact batch uses row key as first hop; `contemplate_job` still auto-invokes cover letter follow-on; `anticipate_scan` does not.

1. In `src/core/consult.py`, add optional parameter to `run_consult_task` signature (after `batch_chunk_index`):
   `dispatch_task_key: Optional[str] = None`
2. In the job branch (after company/board_search/candidate early returns), replace:
   ```python
   task_key = _INPUT_STATE_TO_TASK.get(input_state)
   ```
   with:
   ```python
   task_key = (dispatch_task_key or "").strip()
   if not task_key:
       logger.warning(
           "run_consult_task: dispatch_task_key required for job dispatch (input_state=%s)",
           input_state,
       )
       return zero
   ```
3. Leave `_INPUT_STATE_TO_TASK` dict in file but add comment `# Legacy map — not used for dispatch routing (AST-534). Tests pass dispatch_task_key explicitly.` Do **not** read it in `run_consult_task`.
4. Rename `_run_craft_job_resume_batch` → `_run_job_artifact_entry_batch` and add first positional-after-entities parameter `entry_task_key: str`. Update its docstring to state it runs one artifact hop per job starting at `entry_task_key`.
5. Inside `_run_job_artifact_entry_batch`, replace `run_resume_artifact_chain_for_job(aid, chain_ctx, debug=debug)` with:
   `run_resume_artifact_chain_for_job(aid, chain_ctx, debug=debug, first_task_key=entry_task_key)`
6. Replace unconditional `await _run_cover_letter_for_job(...)` with:
   ```python
   if entry_task_key == "contemplate_job":
       await _run_cover_letter_for_job(aid, job, base_ctx, debug)
   ```
   (Preserves today’s contemplate → resume chain → cover behavior; `anticipate_scan` and other Phase E hops do not auto-run cover letter.)
7. In `run_consult_task` job routing, replace `elif task_key == "contemplate_job": return await _run_craft_job_resume_batch(...)` with:
   `elif task_key in _JOB_ARTIFACT_ENTRY_KEYS: return await _run_job_artifact_entry_batch(batch_id, entities, ctx, debug, task_key)`
   where `_JOB_ARTIFACT_ENTRY_KEYS` is a module-level `frozenset` defined immediately above `_run_job_artifact_entry_batch` containing every `TASK_CONFIG` key whose `"phase"` value starts with `"E. Job Artifacts"` **plus** any other job artifact dispatch keys already routed here (`contemplate_job` is included via phase E). Build the set at module load:
   ```python
   _JOB_ARTIFACT_ENTRY_KEYS = frozenset(
       k for k, v in TASK_CONFIG.items()
       if str(v.get("phase") or "").startswith("E. Job Artifacts")
   )
   ```
8. Keep existing branches for `validate_title`, `scrape_jd`, `qualify_job_listings`, `evaluate_jd`, `consult_do`/`consult_get`/`consult_like`, `analysis_upshot`, and `draft_cover_letter` unchanged except they now receive `task_key` from the dispatch row (caller must pass matching keys — seeded rows already align).
9. Update every internal reference to `_run_craft_job_resume_batch` (grep) to `_run_job_artifact_entry_batch`.

---

## Stage 3: Dispatcher forwards dispatch_task.task_key

**Done when:** All three `consult.run_consult_task(...)` calls in `_run_unified` pass `dispatch_task_key=task.get("task_key", "")`.

1. In `src/core/dispatcher.py`, inside `_run_unified`, after `task_key_run = task.get("task_key", "")` (line ~187), store `dispatch_task_key = task_key_run` for clarity.
2. At the `_consult_chunk` inner function (~line 256), add keyword argument `dispatch_task_key=dispatch_task_key` to `consult.run_consult_task(...)`.
3. At the single batch call (~line 277), add `dispatch_task_key=dispatch_task_key`.
4. At the per-entity `_one` lambda (~line 282), add `dispatch_task_key=dispatch_task_key`.

---

## Stage 4: Component tests lock dispatch-row routing

**Done when:** New/updated tests fail on current `dev` behavior and pass after Stages 1–3; manifest paths listed below run green.

1. In `tests/component/core/test_consult.py`, update **every** `run_consult_task("job", ...)` call to pass `dispatch_task_key=` matching the task that `_INPUT_STATE_TO_TASK` previously implied for that `input_state`. Examples:
   - `"NEW"` → `dispatch_task_key="validate_title"`
   - `"PASSED_JOBLIST"` → `dispatch_task_key="scrape_jd"`
   - `"JD_READY"` → `dispatch_task_key="evaluate_jd"`
   - `"PASSED_JD"` → `dispatch_task_key="consult_do"`
   - `"BUILD_ARTIFACTS"` in `TestAst371ResumeArtifactDispatch.test_routes_build_artifacts_to_resume_batch` → `dispatch_task_key="contemplate_job"`
   - `"PASSED_LIKE"` → `dispatch_task_key="analysis_upshot"`
   - `"UNKNOWN"` / unhandled: pass a bogus key like `dispatch_task_key="not_a_real_task"` (remove monkeypatch of `_INPUT_STATE_TO_TASK` in `test_returns_zero_for_unhandled_task_key`).
2. Add class `TestAst534DispatchTaskKeyRouting` in `test_consult.py`:
   - **`test_consult_do_routes_by_dispatch_task_key_not_state_map`**: monkeypatch `render_verdict` to AsyncMock returning `{"success": True, "to_state": "PASSED_DO"}`; call `run_consult_task("job", "PASSED_JD", [job], "b1", {}, dispatch_task_key="consult_do")`; assert `render_verdict` awaited with first arg `"consult_do"`.
   - **`test_anticipate_scan_build_artifacts_does_not_invoke_contemplate_job`**: monkeypatch `run_resume_artifact_chain_for_job` to AsyncMock(return_value={"success": True}) and `do_task` to AsyncMock; call `run_consult_task("job", "BUILD_ARTIFACTS", [{"astral_job_id": "j1"}], "b2", {"astral_candidate_id": "c1", "candidate_api_key": "k"}, dispatch_task_key="anticipate_scan")`; assert `run_resume_artifact_chain_for_job` awaited once with `first_task_key="anticipate_scan"` (use `call_args.kwargs["first_task_key"]`); assert no call to `do_task` with task_key `"contemplate_job"` (if `do_task` is invoked, it must be for `"anticipate_scan"` only — simplest: assert `do_task` not called when chain helper is mocked to succeed without delegating).
   - **`test_contemplate_job_still_runs_cover_letter_follow_on`**: keep existing resume-batch integration test pattern; assert `_run_cover_letter_for_job` still awaited when `dispatch_task_key="contemplate_job"`.
3. In `tests/component/core/test_dispatcher.py`, add **`test_run_unified_passes_dispatch_task_key_to_consult`**: monkeypatch `get_new_job_batch` to return `("bid", [{"astral_job_id": "j1"}])`, monkeypatch `consult.run_consult_task` to AsyncMock returning `_SUMMARY_ZERO`, call `_run_unified` with task dict `{"entity_type": "job", "trigger_state": "BUILD_ARTIFACTS", "task_key": "anticipate_scan", "batch_call_mode": 1, "batch_size": 5}`; assert mock called with `dispatch_task_key="anticipate_scan"`.

**Manifest (Betty / test-astral narrow run):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyRouting \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_run_unified_passes_dispatch_task_key_to_consult
```

(Correct dispatcher path: `tests/component/core/test_dispatcher.py` — fix path in manifest when qa runs.)

---

## Self-Assessment

**Scope:** `Single-Component` — All edits sit in the dispatch→consult→do_task entry path in `src/core/` plus targeted component tests; no UI, schema, or roster changes.

**Conf:** `high` — Root cause is documented on AST-533; fix follows existing consult task_key branches and AST-531 hop-ledger patterns with explicit parameter threading.

**Risk:** `Medium` — Incorrect routing breaks Scheduled Actions and job consult batches, but claim/scoring/state transitions stay unchanged; regression tests lock the Susan repro and one consult step.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §2.1 dispatch_task as source of truth | **Aligned** — row `task_key` becomes execution entry; `trigger_state` still claim-only. |
| §2.4 batch processing | **Aligned** — claim/release unchanged in `_run_unified`; only consult routing changes. |
| §2.6 state machine | **Aligned** — pass/fail states still come from TASK_CONFIG orchestration per task_key. |
| §3.3 imports | **Aligned** — keep lazy imports in consult (`gazer`, `agent`) to avoid cycles. |
| §3.5 naming | **Aligned** — `dispatch_task_key` parameter name matches DB column semantics. |
| DRY | **Aligned** — single `_run_job_artifact_entry_batch` for all Phase E dispatch hops; no duplicate state map. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build stub)

**Built:** `origin/sub/AST-533/AST-534-honor-dispatch-task-key-core-routing` @ `41c3cc78`.

**Stages delivered:**
- Stage 1: `run_resume_artifact_chain_for_job` optional `first_task_key` override (`353fd647`).
- Stage 2: `dispatch_task_key` routing in `run_consult_task`; `_run_job_artifact_entry_batch` + `_JOB_ARTIFACT_ENTRY_KEYS` (`02f43e53`).
- Stage 3: `_run_unified` forwards row `task_key` to all `run_consult_task` calls (`41c3cc78`).

**Manual smoke:** Scheduled Action `anticipate_scan` @ `BUILD_ARTIFACTS` with `run_next` cleared — first hop must be `anticipate_scan` only; `contemplate_job` must not run unless chained.

---

## Resolution (2026-05-29, resolve-astral)

**Review:** Radia @ `d12f0a10` — fix-now #1: `draft_cover_letter` was in `_JOB_ARTIFACT_ENTRY_KEYS`, so Phase E routing ran `_run_job_artifact_entry_batch` → `run_resume_artifact_chain_for_job` before the dead `elif draft_cover_letter` branch.

**Fix:** Exclude `draft_cover_letter` from `_JOB_ARTIFACT_ENTRY_KEYS`; evaluate `draft_cover_letter` before the Phase E frozenset in `run_consult_task` so `CANDIDATE_REVIEW` dispatch rows call `_run_craft_job_cover_letter_batch` → `run_cover_letter_artifact_chain_for_job` (resume-content gate + `BUILD_CONFIG['cover_letter_artifact_chain']`), per plan Stage 2.

**Tests:** `test_routes_candidate_review_via_dispatch_task_key` asserts cover batch, not artifact entry batch.
