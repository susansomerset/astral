# BUILD_ARTIFACTS CHAIN dispatch and state flattening (BUILD_ARTIFACTS substates do not graduate)

**Linear:** [AST-803](https://linear.app/astralcareermatch/issue/AST-803/build-artifacts-chain-dispatch-and-state-flattening-build-artifacts)  
**Parent:** [AST-788](https://linear.app/astralcareermatch/issue/AST-788/build-artifacts-substates-do-not-graduate) (AC reference only — do not expand epic scope)  
**Publish ref:** `origin/sub/AST-788/AST-803-build-artifacts-chain-dispatch`

Susan UAT proved AST-789 (batch-exit graduation helper on compound `BUILD_ARTIFACTS.<task_key>` states) was the wrong model. This ticket **reverts that machinery**, **flattens** artifact build to base **`BUILD_ARTIFACTS`**, adds **`CHAIN`** task type + **`ERROR_BUILD_ARTIFACTS`**, and implements **`do_chain()`** in `consult.py` so hops run via `dispatch_tasks` + `run_next` with one base state, mid-chain resume, retry hold on flat `BUILD_ARTIFACTS`, and terminal **`BUILD_ARTIFACTS → CANDIDATE_REVIEW`**.

**Supersedes (remove, do not extend):** AST-595 compound `JOB_STATES`, AST-597 per-hop compound transitions in `agent.py`, AST-789 `_try_graduate_artifact_job_to_candidate_review`, `run_resume_artifact_chain_for_job`, `_maybe_transition_resume_hop_progress`, `_resume_artifact_dispatch_row_ok` compound matching.

**Out of scope:** coat-check / post-run `agent_data` harvest; CRAFT/RUBRIC/CHAT consult wiring beyond schema; hop prompts / `run_next` graph edits; cover-letter side effect after `contemplate_job` entry; one-time backfill for stuck legacy compound rows; `tests/` edits (Betty at Code Complete).

**Related (context only):** [AST-789](./ast-789-graduate-build-artifacts-to-candidate-review.md), [AST-595](../artifacts/ast-595-compound-build-artifacts-hop-states.md), [AST-596](../artifacts/ast-596-mid-chain-dispatch-claim-and-hop-failure-batch-release.md), [AST-597](../artifacts/ast-597-per-hop-transitions-and-agent-data-mid-chain-resume-need-to-pick-up-and-parse-daisy-chained-prompts-from-the-middle-using-agent_data-content.md).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Remove AST-789 graduation; add chain helpers + `do_chain()`; replace artifact batch path | core |
| `src/utils/config.py` | Flat `BUILD_ARTIFACTS`, `ERROR_BUILD_ARTIFACTS`, `task_type` enum; remove compound registry; dispatch/UI manifest updates | utils |
| `src/core/tracker.py` | Flat generate/cancel; dispatch-task list helper; legacy compound parse helpers (read-only) | core |
| `src/core/agent.py` | Remove compound hop transitions + `run_resume_artifact_chain_for_job`; keep caller hydration | core |
| `src/core/dispatcher.py` | Flat `BUILD_ARTIFACTS` claim/validation; legacy compound claim expansion | core |
| `src/ui/api/api_admin.py` | Admin dispatch validation for flat `BUILD_ARTIFACTS` trigger | ui |

No frontend TS edits in this ticket (manifest drives UI sections).

---

## Stage 1: Remove AST-789 graduation machinery

**Done when:** `_try_graduate_artifact_job_to_candidate_review` and its batch-loop call sites are gone; `consult.py` compiles.

1. In `src/core/consult.py`, delete `_try_graduate_artifact_job_to_candidate_review` (~1654–1686).
2. In `_run_job_artifact_entry_batch` (~1711–1721), remove the graduation helper call and structured graduation failure branch (this function is replaced in Stage 6 — leave a minimal stub only if needed for compile until Stage 6 lands in the same build pass; prefer deleting the whole function in Stage 6 atomically with `do_chain` wiring).
3. Grep `src/` for `_try_graduate_artifact_job_to_candidate_review` — zero hits.
4. `python3 -m py_compile src/core/consult.py`

⚠️ **Decision:** AST-789 product commits remain in git history on `origin/dev`; this stage **removes the code**, not revert commits. Full git revert of AST-789 is **not** required if the deletion in this branch achieves AC #1.

---

## Stage 2: Config — flat states, `task_type`, chain constants

**Done when:** `JOB_STATES` has flat `BUILD_ARTIFACTS` + `ERROR_BUILD_ARTIFACTS`; compound state entries and generators are removed; resume hops carry `task_type: "CHAIN"`; dispatch defaults use `BUILD_ARTIFACTS` trigger.

1. In `src/utils/config.py`, add module-level allowed set and validator:

   ```python
   TASK_TYPES = frozenset({"CRAFT", "RUBRIC", "CHAT", "CHAIN"})
   BUILD_ARTIFACTS_BASE_STATE = "BUILD_ARTIFACTS"
   ERROR_BUILD_ARTIFACTS_STATE = "ERROR_BUILD_ARTIFACTS"
   LEGACY_BUILD_ARTIFACTS_PREFIX = "BUILD_ARTIFACTS."  # mid-chain resume for in-flight rows only
   ```

2. Add flat states to `JOB_STATES` (replace compound spread `**_resume_artifact_compound_job_states()`):

   ```python
   BUILD_ARTIFACTS_BASE_STATE: {
       "prior_states": ["RECOMMENDED"],
   },
   ERROR_BUILD_ARTIFACTS_STATE: {
       "prior_states": [BUILD_ARTIFACTS_BASE_STATE],  # legacy compound names added in step 4 helper tuple
   },
   ```

   Update `RECOMMENDED` `prior_states`: remove `*_ALL_RESUME_ARTIFACT_COMPOUND_STATES`; add `BUILD_ARTIFACTS_BASE_STATE` and `ERROR_BUILD_ARTIFACTS_STATE` where cancel/regress paths require them.

   Update `CANDIDATE_REVIEW`, `CANDIDATE_APPLIED`, `CANDIDATE_SKIPPED`, `BUILD_FAILED` prior_states: replace compound tuples with `[BUILD_ARTIFACTS_BASE_STATE]` (+ keep `BUILD_FAILED` / review paths as today minus compound names).

3. Delete `_resume_artifact_compound_job_states`, `_all_resume_artifact_compound_state_names`, and the `**_resume_artifact_compound_job_states()` spread from `JOB_STATES`.

4. Replace compound helpers with legacy-aware flat helpers (keep hop order from `BUILD_CONFIG['resume_artifact_chain']['hop_task_keys']`):

   - Rename `resume_artifact_hop_task_keys()` → keep name (still canonical hop list).
   - Replace `resume_artifact_compound_state(task_key)` usages with **`BUILD_ARTIFACTS_BASE_STATE`** for new dispatch defaults.
   - Add `legacy_build_artifacts_hop(state: str) -> str | None` — if `state.startswith(LEGACY_BUILD_ARTIFACTS_PREFIX)`, return suffix hop key; else `None`.
   - Add `is_build_artifacts_in_progress(state: str) -> bool` — true for `BUILD_ARTIFACTS_BASE_STATE`, `ERROR_BUILD_ARTIFACTS_STATE`, or legacy prefix.
   - Add `build_artifacts_claim_states() -> tuple[str, ...]` — `(BUILD_ARTIFACTS_BASE_STATE,)` plus legacy compound names derived from hop keys for in-flight rows until flattened.
   - Remove `resume_artifact_next_compound_state`, `resume_artifact_first_compound_state`, `all_resume_artifact_compound_states`, `parse_resume_artifact_hop` **or** reimplement `parse_resume_artifact_hop` as alias of `legacy_build_artifacts_hop`.

5. Set `RECOMMENDED_JOB_STATES = ["RECOMMENDED", BUILD_ARTIFACTS_BASE_STATE, "CANDIDATE_REVIEW"]` (drop per-hop compound entries).

6. Update `JOBS_RECOMMENDED_UI_SECTIONS`: replace compound `"In Progress"` rows with one row `{"state": BUILD_ARTIFACTS_BASE_STATE, "label": "In Progress"}`.

7. Update `JOBS_RECOMMENDED_PRIMARY_ACTIONS`:
   - `RECOMMENDED` → Generate Artifacts (unchanged).
   - `BUILD_ARTIFACTS_BASE_STATE` → Cancel (replace per-compound cancel map).
   - Remove compound-state keys from the dict comprehension.

8. For each key in `resume_artifact_hop_task_keys()` inside `TASK_CONFIG`, add `"task_type": "CHAIN"` and `"error_state": ERROR_BUILD_ARTIFACTS_STATE`. Do **not** add `pass_state` per hop (chain terminal is `do_chain()` graduation, not per-hop state advance).

9. Add `"task_type"` optional field documentation in a one-line comment above `TASK_CONFIG` header. Add assert at bottom of config module: every `task_type` value ∈ `TASK_TYPES`.

10. In `_dispatch_trigger_state_for_task_key`, replace compound return (~1333–1334):

    ```python
    if task_key in resume_artifact_hop_task_keys():
        return BUILD_ARTIFACTS_BASE_STATE
    ```

11. In `_dispatch_sort_by_for`, keep `state_changed_at` sort for `BUILD_ARTIFACTS_BASE_STATE` and legacy prefix match (replace compound prefix check with `LEGACY_BUILD_ARTIFACTS_PREFIX`).

12. Extend `DISPATCH_SCHEDULABLE_TASK_KEYS` to include all `resume_artifact_hop_task_keys()` entries (admin defaults must resolve for artifact hops).

13. `python3 -m py_compile src/utils/config.py`

---

## Stage 3: Tracker — flat generate/cancel + dispatch list helper

**Done when:** UI Generate/Cancel use flat `BUILD_ARTIFACTS`; consult can list dispatch rows without importing `database` directly.

1. In `src/core/tracker.py`, update imports: replace `resume_artifact_first_compound_state` / `is_resume_artifact_in_progress` with `BUILD_ARTIFACTS_BASE_STATE`, `is_build_artifacts_in_progress` from config.

2. `start_artifact_build`: transition `RECOMMENDED → BUILD_ARTIFACTS` (not compound first hop); return `BUILD_ARTIFACTS`.

3. `cancel_artifact_build`: allow cancel when `is_build_artifacts_in_progress(state)`; transition to `RECOMMENDED` (unchanged clear/lock behavior).

4. Add thin wrapper:

   ```python
   def list_dispatch_tasks_for_candidate(
       candidate_id: str,
       *,
       trigger_state: Optional[str] = None,
   ) -> List[Dict[str, Any]]:
   ```

   Lazy-import `database.list_dispatch_tasks`, filter rows where `str(row.get("candidate_id")) == str(candidate_id)` and optional `trigger_state` match (also match legacy compound states when `trigger_state == BUILD_ARTIFACTS_BASE_STATE` and row still stores legacy value — admin migration is out of scope; reader accepts both during UAT).

5. `python3 -m py_compile src/core/tracker.py`

---

## Stage 4: Agent — remove compound progression + chain entry function

**Done when:** `do_task` no longer transitions compound states; `run_resume_artifact_chain_for_job` deleted; caller hydration helpers remain.

1. In `src/core/agent.py`, delete `run_resume_artifact_chain_for_job` (~1345–1441).

2. Delete `_maybe_transition_resume_hop_progress` (~812–829) and remove the call at ~2295–2296 (`if result.get("success") and entity_type == "job" and index: _maybe_transition_resume_hop_progress(...)`).

3. Remove import of `resume_artifact_next_compound_state`.

4. Keep `_resume_artifact_parent_hop_key`, `_hydrate_resume_entry_chain_context`, `_hydrate_caller_chain_context`, `_parent_hop_task_key_for_child` resume-artifact special case in `_parent_hop_task_key_for_child` (~679–680) — `do_chain()` reuses these for mid-chain caller tokens.

5. Update `_resume_hop_debug_index` to use `resume_artifact_hop_task_keys()` index (unchanged behavior, no state transitions).

6. Grep `src/` for `run_resume_artifact_chain_for_job` and `_maybe_transition_resume_hop_progress` — zero hits.

7. `python3 -m py_compile src/core/agent.py`

---

## Stage 5: Consult — chain helpers

**Done when:** Private helpers exist for entry discovery, dispatch-row validation, progress resolution, and failure classification; not yet wired to `run_consult_task`.

Add after `_artifact_entry_hop_failed` in `src/core/consult.py`:

1. **`_chain_run_next_targets(task_keys: Iterable[str]) -> set[str]`**  
   For each `task_key`, lazy-import `get_agent_task` from `src.data.database`; collect stripped non-empty `run_next` values.

2. **`_build_artifacts_chain_entry_task_key(candidate_id: str) -> str`**  
   - Rows = `tracker.list_dispatch_tasks_for_candidate(candidate_id, trigger_state=BUILD_ARTIFACTS_BASE_STATE)`.
   - Collect `task_key` from rows whose hop ∈ `resume_artifact_hop_task_keys()`.
   - `run_next_targets = _chain_run_next_targets(keys)`.
   - Entry candidates = `[k for k in keys if k not in run_next_targets]`.
   - If exactly one candidate → return it.
   - If zero: fall back to first key in `resume_artifact_hop_task_keys()` (config order) and log warning.
   - If >1: raise `ValueError` with candidate list (stop — comment on AST-788 parent).

3. **`_chain_last_successful_hop(job: dict, anchor_batch_id: Optional[str]) -> Optional[str]`**  
   Walk `resume_artifact_hop_task_keys()` order; for each hop, check `job["agent_responses"]` (reversed) for matching `task_key` + `batch_id` (when anchor set) with successful RESPONSE block (reuse `_hop_agent_ref_for_parent` pattern from `agent.py` — import or duplicate minimal check inline in consult to avoid consult→agent cycle at module load; **lazy-import** `from src.core import agent as agent_mod` inside function).

4. **`_resolve_chain_start_task_key(job, *, dispatch_task_key: str, input_state: str, candidate_id: str) -> Optional[str]`**  
   - Legacy: `legacy_hop = legacy_build_artifacts_hop(input_state)` — if set, return legacy hop **only when** `dispatch_task_key == legacy_hop` or dispatch row is chain-entry (AST-534 mid-chain honesty).
   - Flat job on `BUILD_ARTIFACTS`: if `dispatch_task_key` in hop keys → return `dispatch_task_key`.
   - Flat job on `BUILD_ARTIFACTS` with entry dispatch row → return `_build_artifacts_chain_entry_task_key(candidate_id)`.
   - Else → `None`.

5. **`_chain_dispatch_row_ok(job, dispatch_task_key: str, input_state: str, candidate_id: str) -> bool`**  
   Wrap `_resolve_chain_start_task_key`; on `None`, log warning with expected flat/legacy states; return False.

6. **`_chain_failure_mode(result: dict, task_key: str) -> Literal["retry", "hard"]`**  
   - Hard when `result.get("error")` indicates missing job/candidate/hydration (`"Job not found"`, `"Missing candidate_data"`, `"hydration"` substring) **or** task config marks non-retryable schema failures after second attempt — for this ticket: **hard** only when error message contains `"Missing candidate_data"` or `"Job not found"`; all other hop failures → **retry** (stay on `BUILD_ARTIFACTS`, release claim).

7. **`_chain_graduate_to_candidate_review(astral_job_id: str, *, debug: bool) -> tuple[bool, str]`**  
   Same persist gate as AST-789 (`tracker.job_has_persisted_resume_body(..., None)`) then `tracker.transition_job_state([astral_job_id], "CANDIDATE_REVIEW")`. Return `(ok, reason)` tuple. **Not** named `_try_graduate_*` (AST-789 retired).

8. `python3 -m py_compile src/core/consult.py`

---

## Stage 6: Consult — `do_chain()` and batch wiring

**Done when:** `_run_job_artifact_entry_batch` replaced by `do_chain()`; `run_consult_task` routes CHAIN hops through it; terminal graduation and retry/error paths match AC #3–#5.

1. Add async **`do_chain_for_job(astral_job_id, *, batch_id, ctx, debug, dispatch_task_key, input_state) -> dict`** returning `{"success": bool, "error": optional str}`:

   **Setup**
   - Load job via `tracker.get_job`; require `is_build_artifacts_in_progress(job.state)`.
   - Resolve `start_key = _resolve_chain_start_task_key(...)`. On failure return `{"success": False, "error": "dispatch_row_mismatch"}`.
   - Build `task_ctx` like deleted `run_resume_artifact_chain_for_job` (candidate_data, batch_entities, vector_labels).
   - Seed `chain_context` via lazy `agent_mod._hydrate_resume_entry_chain_context` when mid-chain.

   **Walk**
   - `current_key = start_key`
   - Loop:
     - Lazy `from src.core.agent import do_task`
     - `result = await do_task(current_key, index=astral_job_id, ctx=task_ctx, debug=debug, chain_context=seed_or_merged)`
     - On `not result.get("success")`:
       - If `_chain_failure_mode(...) == "hard"`: `tracker.transition_job_state([astral_job_id], ERROR_BUILD_ARTIFACTS_STATE)`; return failure.
       - Else: return failure (caller releases claim; job stays on `BUILD_ARTIFACTS`).
     - Read `run_next` from `get_agent_task(current_key)` stripped.
     - If `run_next`: merge hop tokens from result into chain context; `current_key = run_next`; continue.
     - If no `run_next`: break (chain exhausted).

   **Terminal**
   - `ok, reason = _chain_graduate_to_candidate_review(astral_job_id, debug=debug)`
   - If not ok: return `{"success": False, "error": reason}`
   - Return `{"success": True}`

   ⚠️ **Decision:** Job state stays **`BUILD_ARTIFACTS`** for all in-chain hops (no per-hop `JOB_STATES` transitions). Progress is implied by `agent_responses` + dispatch row, not state string.

   ⚠️ **Decision:** Remove `_run_cover_letter_for_job` side effect when entry was `contemplate_job` (parent lists cover-letter side effect as retired with `do_chain()`).

2. Replace `_run_job_artifact_entry_batch` body:

   ```python
   async def _run_build_artifacts_chain_batch(...):
       for job in entities:
           aid = job["astral_job_id"]
           if not _chain_dispatch_row_ok(job, entry_task_key, input_state, candidate_id_from_ctx):
               continue  # zero summary for mismatch (AST-596)
           r = await do_chain_for_job(aid, batch_id=batch_id, ctx=..., dispatch_task_key=entry_task_key, input_state=input_state, debug=debug)
           if not r.get("success"):
               _artifact_entry_hop_failed(aid)
               errors += 1
               continue
           passed += 1
   ```

   Extract `candidate_id` from `ctx["astral_candidate_id"]`.

3. Delete `_resume_artifact_dispatch_row_ok`.

4. In `run_consult_task` (~1895–1898), keep routing `task_key in _JOB_ARTIFACT_ENTRY_KEYS` but call `_run_build_artifacts_chain_batch` (rename from `_run_job_artifact_entry_batch`).

5. Remove imports of `resume_artifact_compound_state`, `resume_artifact_hop_task_keys` where unused; keep hop keys import for routing set.

6. Grep `src/core/consult.py` for `resume_artifact_compound_state`, `_try_graduate`, `run_resume_artifact_chain_for_job` — zero hits.

7. `python3 -m py_compile src/core/consult.py`
8. `python3 -c "from src.core import consult; print('ok')"`

---

## Stage 7: Dispatcher + admin validation

**Done when:** Claim uses flat + legacy states; pre-claim guard accepts `BUILD_ARTIFACTS` trigger for all resume hops.

1. In `src/core/dispatcher.py` `_run_unified` (~195–214), replace compound expected-state check:

   - For `dispatch_task_key in resume_artifact_hop_task_keys()`:
     - Accept when `(input_state or "").strip() == BUILD_ARTIFACTS_BASE_STATE`.
     - Also accept legacy compound state matching `legacy_build_artifacts_hop(input_state) == dispatch_task_key` (in-flight rows).
     - Else skip claim (existing debug + warning pattern).

2. When claiming jobs for `BUILD_ARTIFACTS` dispatch rows, pass `states=build_artifacts_claim_states()` into `get_new_job_batch` instead of default `dispatch_claim_states` only — implement by extending claim path when `input_state == BUILD_ARTIFACTS_BASE_STATE`.

3. In `src/ui/api/api_admin.py` `_dispatch_task_key_trigger_error` (~938–941), replace compound requirement with:

   ```python
   if tk in resume_artifact_hop_task_keys():
       if ts != BUILD_ARTIFACTS_BASE_STATE and legacy_build_artifacts_hop(ts) != tk:
           return f"task_key {tk!r} requires trigger_state {BUILD_ARTIFACTS_BASE_STATE!r} (got {ts!r})"
   ```

4. `python3 -m py_compile src/core/dispatcher.py src/ui/api/api_admin.py`

---

## Stage 8: Compile gate + Betty handoff targets

**Done when:** Product imports cleanly; Linear comment lists Betty manifest (no test edits here).

1. Run:

   ```bash
   python3 -m py_compile \
     src/utils/config.py \
     src/core/tracker.py \
     src/core/agent.py \
     src/core/consult.py \
     src/core/dispatcher.py \
     src/ui/api/api_admin.py
   python3 -c "from src.core import consult, agent, dispatcher, tracker; print('ok')"
   ```

2. Code Complete comment for Betty — manifest targets:

   | # | Area | Test focus |
   |---|------|------------|
   | 1 | Chain entry discovery | New consult tests: entry task_key = hop with no incoming `run_next` |
   | 2 | Full chain terminal | Mock `do_task` walk; assert single `CANDIDATE_REVIEW` transition after last hop |
   | 3 | Mid-chain resume | `dispatch_task_key=draft_job_resume`, flat `BUILD_ARTIFACTS`, caller hydration invoked |
   | 4 | Legacy compound resume | Job state `BUILD_ARTIFACTS.draft_job_resume` + matching dispatch row runs |
   | 5 | Retry hold | Hop failure → `release_job_dispatch_claim`; state stays `BUILD_ARTIFACTS`; no `CANDIDATE_REVIEW` |
   | 6 | Hard error | Missing candidate / hard path → `ERROR_BUILD_ARTIFACTS` |
   | 7 | Flat generate/cancel | Tracker/API: `RECOMMENDED → BUILD_ARTIFACTS → RECOMMENDED` |
   | 8 | Dispatcher guard | Flat trigger accepts; legacy compound still accepts until flattened |
   | 9 | AST-789 regression | Remove/replace `TestAst789TerminalGraduation` with CHAIN graduation tests |

   Narrow run (Betty):

   ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
     tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
     tests/component/core/test_consult.py::TestAst789TerminalGraduation \
     tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions \
     tests/component/core/test_dispatcher.py::TestRunUnified \
     tests/component/utils/test_config.py::TestAst595CompoundBuildArtifactsHopStates
   ```

   Expect **`TestAst595CompoundBuildArtifactsHopStates`** and **`TestAst789TerminalGraduation`** to require Betty rewrites — flag in comment.

---

## Execution contract (for the developer agent)

- Execute stages in order. **Stop** on ambiguity — comment on **AST-788** parent with 🛑 template from **plan-child**.
- **Do not** edit `tests/`, bible, or hop prompts / `agent_task.run_next` DB content.
- **Do not** add coat-check harvest or CRAFT/RUBRIC/CHAT consult wiring.
- When `_build_artifacts_chain_entry_task_key` finds >1 entry candidate, **stop** — do not guess.
- When legacy compound rows fail mid-chain resume after flat dispatch migration, **stop** and comment with job id + state (admin row migration may be follow-on).

Blocking questions use parent **AST-788**:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope — `MAJOR-CHANGE`**  
Six product modules across config, core consult/agent/tracker/dispatcher, and admin API — replaces the AST-595/597/789 compound-state model with flat `BUILD_ARTIFACTS` + `do_chain()`.

**Conf — `Medium`**  
Hop execution reuses existing `do_task` + `run_next`; the risk is mid-chain resume + legacy compound coexistence and dispatch row trigger migration — helpers are specified, but build must validate against real dispatch rows in Susan's environment.

**Risk — `HIGH`**  
Wrong chain entry, graduation, or retry/error classification breaks Recommended Jobs **Ready** vs **In Progress**, leaves jobs stuck or false-promoted, or regresses AST-534/596 mid-chain dispatch honesty.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `do_chain_for_job` replaces `run_resume_artifact_chain_for_job` + compound transitions + AST-789 graduation helper. |
| §1.4 config | States, `task_type`, hop list, UI manifest driven from `config.py`; no inline state sets. |
| §2.1 config | `dispatch_tasks` + `run_next` define hop order; `JOB_STATES` only for base/recovery/terminal. |
| §2.4 batch | Same `batch_id` through chain; hop failure releases claim (`_artifact_entry_hop_failed`); no `BUILD_FAILED` on hop failure. |
| §2.6 state machine | Transitions via `tracker.transition_job_state` only — terminal `CANDIDATE_REVIEW`, hard `ERROR_BUILD_ARTIFACTS`, cancel → `RECOMMENDED`. |
| §3.3 imports | Consult → tracker + lazy agent; dispatch list via tracker wrapper (no consult → database at load). |
| §3.5 naming | `do_chain_for_job`, `_chain_*` helpers, `BUILD_ARTIFACTS_BASE_STATE` constants. |

No unresolved conflicts with ASTRAL_CODE_RULES.

---

## Review (build)

**Built:** `origin/sub/AST-788/AST-803-build-artifacts-chain-dispatch` (pending publish)

Stages 1–7: flat `BUILD_ARTIFACTS` + `ERROR_BUILD_ARTIFACTS`, `task_type: CHAIN` on resume hops, removed AST-789/597 compound progression, `do_chain_for_job` + `_run_build_artifacts_chain_batch`, dispatcher/admin flat trigger validation. Component tests deferred to Betty per build-child test-tree ban.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-788/AST-803-build-artifacts-chain-dispatch` (15 files; product + Betty tests on tip `92bc89b`)

### What's solid

| Area | Notes |
|------|-------|
| Config / state machine | Flat `BUILD_ARTIFACTS` + `ERROR_BUILD_ARTIFACTS`; `task_type: CHAIN` on resume hops; legacy compound helpers retained for in-flight rows (§2.6 / §1.4). |
| Agent | Compound hop transitions and `run_resume_artifact_chain_for_job` removed; `do_task` internal `run_next` recursion is the correct chain walker. |
| Tracker / dispatcher / admin | Flat generate/cancel; `build_artifacts_claim_states()` on claim; flat + legacy trigger validation. |
| Consult routing | `_run_build_artifacts_chain_batch` per-job mismatch skip (AST-596); cover-letter side effect removed from `contemplate_job` entry; terminal graduation via `_chain_graduate_to_candidate_review` with persist gate. |
| Tests | `TestAst803ChainGraduation`, helpers, AST-534 routing, config flattening — manifest-aligned. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **fix-now** | `src/core/consult.py` `do_chain_for_job` ~1805–1806 | Early `Missing candidate_data` return skips `_chain_failure_mode` — job stays on `BUILD_ARTIFACTS` with no `ERROR_BUILD_ARTIFACTS` transition. Plan Stage 5.6 / AC hard path requires `ERROR_BUILD_ARTIFACTS` for missing candidate data (same as post-`do_task` path at ~1837–1842). |
| **discuss** | `src/core/consult.py` `_build_artifacts_chain_entry_task_key` vs `_resolve_chain_start_task_key` | Entry-discovery helper is implemented + tested but never called from `_resolve_chain_start_task_key` (plan Stage 5.4). Current flat path always returns `dispatch_task_key` when `job_state == BUILD_ARTIFACTS` — OK for AST-534 row honesty if dispatch rows are always hop-specific; confirm whether discovery is still required or delete dead path. |
| **discuss** | `src/core/consult.py` `_build_artifacts_chain_entry_task_key` ~1673–1681 | Second warning fallback (all hops have incoming `run_next` → first hop in config) is not in plan; silent wrong-entry risk on misconfigured dispatch graph. |
| **discuss** | Plan Stage 5.3 | `_chain_last_successful_hop` specified but not implemented — defer or add if mid-chain resume needs `agent_responses` walk beyond caller hydration. |

### Recommended actions

| # | Action |
|---|--------|
| 1 | In `do_chain_for_job`, route pre-`do_task` `Missing candidate_data` (and optionally `job_not_found` if desired) through hard failure → `tracker.transition_job_state(..., ERROR_BUILD_ARTIFACTS_STATE)`. |
| 2 | Wire or remove `_build_artifacts_chain_entry_task_key`; if kept, drop unplanned fallback-to-first-hop or raise per plan stop rule. |
| 3 | Resolve `_chain_last_successful_hop` deferral in thread or implement. |

---

## Resolution

**Resolved:** 2026-06-25 (Hedy)

**fix-now:** Pre-`do_task` `Missing candidate_data` in `do_chain_for_job` now routes through `_chain_fail_result` → `_chain_failure_mode` → `ERROR_BUILD_ARTIFACTS` (same as post-`do_task` hard path). Extracted `_chain_fail_result` to DRY hop-failure handling.

**discuss (accepted, no product change):** `_build_artifacts_chain_entry_task_key` remains helper-only — flat `BUILD_ARTIFACTS` + AST-534 dispatch row honesty uses explicit `dispatch_task_key`; entry discovery reserved for future generic chain rows. `_chain_last_successful_hop` deferred — mid-chain resume uses caller hydration + legacy compound state parse.

**§9a dry-run:** clean on `origin/dev` and `origin/ftr/AST-788-build-artifacts-chain-dispatch` @ `2d0b0a4`.
