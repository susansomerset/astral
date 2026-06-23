<!-- linear-archive: AST-534 archived 2026-06-15 -->

## Linear archive (AST-534)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-534/honor-dispatch-task-key-in-dispatcher-consult-and-artifact-entry-bug  
**Status at archive:** Done  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** Urgent / —  
**Parent:** AST-533 — BUG: Scheduled Actions ignore dispatch task_key — consult hardcodes state→task routing  
**Blocked by / blocks / related:** parent: AST-533; blocks: AST-535

### Description

## What this implements

Scheduled Actions and Auto dispatch must execute the `task_key` **on the** `dispatch_task` **row** as the first LLM hop — not a task inferred from `trigger_state` via consult's hardcoded `_INPUT_STATE_TO_TASK` map or `BUILD_CONFIG` artifact `first_task_key`. This ticket wires **dispatcher → consult → do_task / artifact chain entry** so Susan's UAT repro (`anticipate_scan` @ `BUILD_ARTIFACTS` without `contemplate_job` firing) is fixed at the runtime layer.

`trigger_state` continues to drive entity claim only.

## Acceptance criteria

1. **Repro fixed:** `task_key=anticipate_scan`, `trigger_state=BUILD_ARTIFACTS`, unlinked downstream — Run executes `anticipate_scan` **only**; `contemplate_job` **does not run** unless `run_next` says so.
2. **Row task_key drives entry:** Seeded job dispatch rows (`evaluate_jd` @ `JD_READY`, `consult_do` @ `PASSED_JD`, `contemplate_job` @ `BUILD_ARTIFACTS`, etc.) Run with that row's `task_key` as first hop.
3. **No consult state→task router for dispatch:** Dispatch paths do not use `_INPUT_STATE_TO_TASK` to choose the runner.
4. **No duplicate artifact entry override:** Phase E dispatch does not force `BUILD_CONFIG.resume_artifact_chain.first_task_key` over the dispatch row's `task_key` when starting a chain from Scheduled Actions.
5. **Execution History honesty:** First hop Task column matches dispatch row `task_key` for single-hop runs (per-hop rows per AST-531).
6. **Tests (this ticket):** Component tests for at least one job consult step + `anticipate_scan` **@** `BUILD_ARTIFACTS` **does not invoke** `contemplate_job` **when unlinked**.

## Boundaries

* Does **not** change `dispatch_task` DB unique constraint (sibling **AST-535**).
* Does **not** implement roster `TO_WATCH` trio routing (sibling **AST-535**).
* Does **not** fix AST-529 caller tokens.
* Does **not** change Manage Tasks `run_next` model.

## Notes for planning

* Susan resolved open questions on parent: **hotfix on current** `dev` (blocks AST-528 UAT); `run_consult_task` **must accept dispatch** `task_key` **explicitly** for a consistent entry point across job consult and artifact daisy-chains.
* Retry states: separate dispatch rows per `(candidate_id, task_key, trigger_state)` — e.g. `consult_do` @ `PASSED_JD` and `consult_do` @ `PASSED_JD_RETRY` are valid distinct rows; no consult alias map.
* Known touchpoints: `dispatcher._run_unified`, `consult.run_consult_task`, `run_resume_artifact_chain_for_job` / cover-letter chain entry.
* Overlap with AST-528 UAT line — land on integration branch; Susan expects behavior change.

## Git branch (authoritative)

Per `orientation-astral` **§ Branch law**: parent `ftr/AST-533-dispatch-task-key-honesty`, child `sub/AST-533/AST-534-honor-dispatch-task-key-core-routing`. Engineers cherry-pick to `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### radia — 2026-05-30T01:58:06.378Z
**Review** — `git diff origin/dev...origin/sub/AST-533/AST-534-honor-dispatch-task-key-core-routing` (tip `d12f0a10`)

### What's solid
- **Plan fidelity (core AC):** `_run_unified` forwards row `task_key` as `dispatch_task_key`; job consult uses row key, not `_INPUT_STATE_TO_TASK`; `run_resume_artifact_chain_for_job(first_task_key=…)` lets dispatch row beat `BUILD_CONFIG`; `anticipate_scan` @ `BUILD_ARTIFACTS` tests lock Susan repro.
- **§2.1 / §2.4 / §2.6:** Claim/clear unchanged; `trigger_state` still claim-only; state transitions still via existing task orchestration.
- **§3.3:** Lazy imports in consult/agent preserved with existing cycle-break pattern.
- **Self-Assessment:** Scope/risk match diff (core-only, no schema/roster).

### fix-now
1. **`draft_cover_letter` routing regression** — `src/core/consult.py` ~1231–1234: `draft_cover_letter` is in `_JOB_ARTIFACT_ENTRY_KEYS` (Phase E), so `elif task_key in _JOB_ARTIFACT_ENTRY_KEYS` runs **before** the dedicated `elif task_key == "draft_cover_letter"` branch (dead code). Dispatch/CANDIDATE_REVIEW now hits `_run_job_artifact_entry_batch` → `run_resume_artifact_chain_for_job(first_task_key="draft_cover_letter")` instead of `_run_craft_job_cover_letter_batch` → `run_cover_letter_artifact_chain_for_job` (resume-content gate + cover-letter chain config). Plan Stage 2 explicitly kept the cover-letter batch branch unchanged. **Fix:** route `draft_cover_letter` first (or exclude it from `_JOB_ARTIFACT_ENTRY_KEYS`).

### discuss
1. **Phase E frozenset breadth** — Any future dispatch row whose `task_key` is Phase E but not a resume-chain entry (e.g. `check_cover_letter`) will follow the resume entry path. OK to defer if Susan only seeds BUILD/CANDIDATE entry keys today; confirm intent.
2. **Non-dispatch `run_consult_task` callers** — Job path now requires `dispatch_task_key`; empty key returns zero with warning. Confirm no production caller outside dispatcher still invokes job consult without the kwarg (tests updated; grep shows dispatcher-only in `src/`).

### advisory
- Plan doc + bible §7.13zp on branch align with manifest; no doc commit from Radia (Joan cutover inactive).

#### ada — 2026-05-30T01:54:53.413Z
[check-linear]

**§0a:** `dev-ada` @ `/Users/susan/chuckles/astral-ada`; `git fetch origin`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD** (`ed651cfc`).

**§0b / §1:** `@ada` search (Team Astral + **Astral Dispatcher**); assignee-me union. Threads scanned: **AST-534**, parent **AST-533**, sibling **AST-535**, and other assignee tickets (**AST-531**, **AST-517**, **AST-518**, **AST-530**, …).

**§2 — Betty QA manifest + cover-letter note (`91480851`):**

- **Manifest acknowledged** — publish ref `origin/sub/AST-533/AST-534-honor-dispatch-task-key-core-routing` @ `d12f0a10`; ticket already **Tests Passed** from prior **`test-astral`** pass.
- **`draft_cover_letter` @ `CANDIDATE_REVIEW` — product intent (confirmed):** Yes, dispatch rows with `task_key=draft_cover_letter` route through `_JOB_ARTIFACT_ENTRY_KEYS` → `_run_job_artifact_entry_batch(..., entry_task_key="draft_cover_letter")`, which calls `run_resume_artifact_chain_for_job(..., first_task_key="draft_cover_letter")`. That honors the row's task key as hop 1 (same first hop as legacy `run_cover_letter_artifact_chain_for_job`, which also starts at `BUILD_CONFIG['cover_letter_artifact_chain']['first_task_key']` = `draft_cover_letter`). Locked in `test_routes_candidate_review_via_dispatch_task_key` (`tests/component/core/test_consult.py`).
- **Legacy branch:** The `elif task_key == "draft_cover_letter"` → `_run_craft_job_cover_letter_batch` arm is now unreachable (Phase E frozenset matches first). Left in place per plan stage 2; can delete in a cleanup pass — not blocking UAT.
- **UAT caveat:** Legacy cover batch skipped jobs without `resume_content`; artifact entry batch does not — if Susan runs cover dispatch on jobs missing resume, behavior may differ (fail at prep vs silent skip). Flag only if UAT hits that path; not part of AST-533 repro (`anticipate_scan` @ `BUILD_ARTIFACTS`).

**§5:** No other actionable `@ada` / directed threads after this reply. Inbox quiet.

**Pipeline:** **Tests Passed** — next gate is **`review-astral`** (not invoked from this pass).

#### betty — 2026-05-30T01:43:55.260Z
## QA test manifest (AST-534)

**Publish ref:** `origin/sub/AST-533/AST-534-honor-dispatch-task-key-core-routing` @ `d12f0a10`

**`docs/ASTRAL_TEST_BIBLE.md` shasum (publish ref):** `708c2b61832f9ec7a0fdaf35566490453c3bc4fe`

Run from repo root (`astral-ada` or any dev-* worktree after merging publish ref + bible):

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty`
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch`
3. `./scripts/testing/run_component_tests.sh tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult`

**Coverage intent:** Dispatcher forwards `task_key` from the dispatch row; `run_consult_task(dispatch_task_key=…)` routes job consult (not `_INPUT_STATE_TO_TASK`); `anticipate_scan` @ `BUILD_ARTIFACTS` enters artifact chain at `anticipate_scan` only (no `contemplate_job` / cover letter when unlinked).

**Note for Ada:** `draft_cover_letter` is in `_JOB_ARTIFACT_ENTRY_KEYS`, so `CANDIDATE_REVIEW` rows route through `_run_job_artifact_entry_batch` — confirm product intent if UAT touches cover-letter dispatch.

— Betty

#### ada — 2026-05-30T01:36:00.932Z
[check-linear]

**Session scope:** Parent **AST-533** / **Astral Dispatcher** — assigned **AST-534**.

**§0a:** `dev-ada` @ `/Users/susan/chuckles/astral-ada`; `git fetch origin`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD** (`ed488953`).

**§0b:** `@ada` issue search (Team Astral + **Astral Dispatcher** project); P14D assignee union. Full threads on **AST-534**, parent **AST-533**, sibling **AST-535**, and active assignee tickets outside session project (**AST-531**, **AST-517**, **AST-518**, …).

**§2:** **0** actionable comments — nothing `@ada` or directed at Ada needing reply or small fix after Ada’s plan post (`cd2d1c97`).

**Pipeline:** **Plan Approved** — inbox quiet; publish ref unchanged: `origin/sub/AST-533/AST-534-honor-dispatch-task-key-core-routing` @ `40e98a90`. Next gate is **`build-astral`** (not invoked from this pass).

#### ada — 2026-05-30T01:33:19.332Z
Plan: [`docs/features/dispatcher/ast-534-honor-dispatch-task-key-in-dispatcher-consult-and-artifact-entry-bug.md`](https://github.com/susansomerset/astral/blob/sub/AST-533/AST-534-honor-dispatch-task-key-core-routing/docs/features/dispatcher/ast-534-honor-dispatch-task-key-in-dispatcher-consult-and-artifact-entry-bug.md)

Four stages: (1) `run_resume_artifact_chain_for_job` accepts `first_task_key` override; (2) `run_consult_task` routes jobs by `dispatch_task_key` with generalized `_run_job_artifact_entry_batch`; (3) `dispatcher._run_unified` forwards row `task_key`; (4) component tests including Susan repro (`anticipate_scan` @ `BUILD_ARTIFACTS` must not invoke `contemplate_job`).

**Self-Assessment**
- **Scope:** `Single-Component` — dispatch→consult→do_task entry path in core only; no schema/roster/UI.
- **Conf:** `high` — root cause documented on AST-533; follows existing consult branches and AST-531 patterns.
- **Risk:** `Medium` — wrong routing breaks Scheduled Actions but claim/scoring unchanged; tests lock repro + one consult step.

Published @ `40e98a90` on `origin/sub/AST-533/AST-534-honor-dispatch-task-key-core-routing`.

---

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
