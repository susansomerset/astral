# AST-1298 — Release orphaned job claim after provider Connection error

**Linear:** [AST-1298](https://linear.app/astralcareermatch/issue/AST-1298/release-orphaned-job-claim-after-provider-connection-error-connection)
**Parent:** [AST-1280](https://linear.app/astralcareermatch/issue/AST-1280/connection-error-on-dispatch-task-did-not-clear-the-batch-id) — Connection error on dispatch task did not clear the batch_id
**Publish ref:** `origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error`

Close the live job-artifacts dispatch gap where `draft_job_resume` logged provider `Connection error.` / `do_task(...) provider call failed` and the job row kept a populated `batch_id` after the run. Reuse AST-1191’s hop-failure helper (no parallel release design): durable claim clear + configured error/hold + honest debug `batch_released` on the **hop-label-true** BUILD_ARTIFACTS dispatch path. Does not own provider retry or hop-topology redesign.

## Survey findings (baked into this plan — builder does not re-decide)

On tip after `sync-child` (AST-1191 already on `origin/dev`):

| Location | Finding | Action this ticket |
|----------|---------|-------------------|
| `consult._run_dispatch_chain_job_batch` | Sets `dispatch_trigger_state` to registry `BUILD_ARTIFACTS`; `dispatch_chain_graduation_target("BUILD_ARTIFACTS")` is set → `_should_write_dispatch_hop_label` is **true** on the AC1 path | **AC path is Branch B (hop-label-true), not hop-label-false** |
| `agent._apply_dispatch_chain_hop_failure` (hop-label-true) | AST-1191 already transitions then `release_job_dispatch_claim`, but release sits **after** the `transition_job_state` try/except and is skipped if transition raises anything other than `ValueError` | **Fix:** `try`/`finally` so `provider_failed` release always runs on this branch after the transition attempt |
| `consult._run_dispatch_chain_job_batch` | Releases only when `do_task` **returns** `success=False`; if `do_task` **raises** after the provider ERROR log (or during `_close_hop_ledger` after a partial side effect), this belt is skipped | **Fix:** per-job `try`/`finally` release around `do_task` so exception exits still clear the claim |
| `dispatcher._run_unified` `finally` | `clear_job_batch(bid)` remains the outer belt (do not remove) | **Do not change** — keep as third belt; Stages 1–2 must not rely on it alone for AC1 |
| Logged `batch_id=draft_job_resume-<uuid>` | Hop-ledger / `do_task` local id when `run_next` chain is active; job row claim id is dispatch `entity_batch_id` (`{entry_task_key}-<uuid>`) — may differ | Clear **job row** lock by `astral_job_id` / claim `bid`; do not require hop-ledger uuid equality |
| `src/external/deepseek.py` | Connection failures already return `success=False` + non-empty `error` | **Out of scope** |
| Hop-label-false early return | Real defense-in-depth gap for non-dispatch `do_task` callers; **not** the parent AC1 repro ctx | Optional small release on that branch only as defense-in-depth — **must not** be described as the AC fix |

⚠️ **Decision — root cause (revised after Joan round=1):** The AC1 job-artifacts dispatch repro uses hop-label-**true** ctx (`BUILD_ARTIFACTS` graduation). Claiming the orphan on hop-label-false was incorrect for AC1–AC2. On hop-label-true, AST-1191’s happy structured-`success=False` path already releases, but two belts still miss when the failure path does not return a clean failure dict: (1) helper release skipped on non-`ValueError` from `transition_job_state`; (2) consult release skipped when `do_task` raises. Archie’s “ERROR line present + `batch_id` still set after the run” matches those miss windows (and/or sole reliance on dispatcher `finally` when an inner belt aborted). Fix those two belts; do not invent a parallel release module or DeepSeek retry.

⚠️ **Decision — wrong fix rejected:** Shipping only hop-label-false ungating (prior plan Branch A) as the epic fix — does not explain or close the BUILD_ARTIFACTS dispatch orphan Joan flagged. Also rejected: Connection-error substring special case; adapter redesign; removing consult/dispatcher clears.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | `_apply_dispatch_chain_hop_failure` hop-label-true branch: wrap transition + release so `provider_failed` release runs in `finally` (transition attempt still first); optional defense-in-depth release on hop-label-false for job+provider_failed only; keep found/recorded consumers unchanged | core |
| `src/core/consult.py` | `_run_dispatch_chain_job_batch`: per-job `try`/`finally` around `do_task` so `release_job_dispatch_claim(aid)` runs on both `success=False` returns and exceptions | core |

No `src/external/**`, no `src/data/**`, no `src/utils/config.py`, no `dispatcher.py`, no `tests/` / bible (Betty).

## Stage 1: Exception-safe release on hop-label-true (agent helper)

**Done when:** On hop-label-true + `provider_failed=True` + non-empty `index`, `release_job_dispatch_claim(index)` runs even when `transition_job_state` raises a non-`ValueError`. Transition is still attempted before release when `hard` (AST-1191 history stamp). Balance refusal still skips transition and still releases. `batch_released` in the return dict is true when release ran. Existing ERROR log line unchanged.

1. In `src/core/agent.py` `_apply_dispatch_chain_hop_failure`, keep the `_should_write_dispatch_hop_label` gate for **error_state / hard / balance_hold** (hop-label-false still returns without error_state write).
2. **Hop-label-true branch** — replace the post-gate body with this control flow (late-import `tracker` once):

   ```python
   err_state = (task_config.get("error_state") or "").strip()
   balance_hold = provider_failed and is_provider_balance_refusal(
       {"failure_class": failure_class}
   )
   hard = bool(err_state) and (
       "Job not found" in error
       or "Missing candidate_data" in error
       or (provider_failed and not balance_hold)
   )
   apply_error_state = False
   batch_released = False
   from src.core import tracker as tracker_mod
   try:
       if hard and err_state and index:
           try:
               tracker_mod.transition_job_state([index], err_state)
               apply_error_state = True
           except ValueError as exc:
               logger.warning(
                   "[%s] dispatch chain error_state=%s failed: %s",
                   index, err_state, exc,
               )
   finally:
       if provider_failed and index:
           tracker_mod.release_job_dispatch_claim(index)
           batch_released = True
   ```

   Then keep the existing `debug` `chain_hop_failed …` detail line and the same return dict shape as today.

3. **Hop-label-false branch** (defense-in-depth only — not the AC root cause): if `provider_failed and index and entity_type == "job"`, call `release_job_dispatch_claim(index)` and return `batch_released=True` with `apply_error_state=False` / empty `error_state` (and the same debug detail shape). Do not transition.

4. Do **not** change `_close_hop_ledger` call-site kwargs (`provider_failed=True` / `failure_class`).

⚠️ **Decision:** `finally` release on hop-label-true may run after a failed transition attempt; that is intentional so AC1 cannot lose to a non-`ValueError` from `transition_job_state`. History still stamps in-flight `batch_id` when transition succeeds before `finally`.

## Stage 2: Consult per-job release on exception (dispatch-chain batch)

**Done when:** In `_run_dispatch_chain_job_batch`, every job that enters `do_task` has `release_job_dispatch_claim(aid)` invoked if that call raises **or** returns `success=False`. Success returns still do **not** eager-release here (dispatcher `finally` / graduation path unchanged). Missing-`candidate_data` early continue keeps its existing pre-`do_task` release.

1. In `src/core/consult.py` `_run_dispatch_chain_job_batch`, replace the bare:

   ```python
   result = await do_task(...)
   if not result.get("success"):
       tracker.release_job_dispatch_claim(aid)
       errors += 1
       continue
   passed += 1
   ```

   with:

   ```python
   try:
       result = await do_task(
           dispatch_task_key,
           index=aid,
           ctx=task_ctx,
           debug=debug,
       )
   except BaseException:
       tracker.release_job_dispatch_claim(aid)
       errors += 1
       raise
   if not result.get("success"):
       tracker.release_job_dispatch_claim(aid)
       errors += 1
       continue
   passed += 1
   ```

2. Keep the existing `if not cd: release; errors; continue` arm unchanged.
3. Do **not** edit `dispatcher.py` — `clear_job_batch(bid)` in `_run_unified` `finally` stays the third belt.
4. Compile / lint touched files (`src/core/agent.py`, `src/core/consult.py`) before commit.

⚠️ **Decision:** Re-raise after exception release so dispatcher/`_warm_then_gather` behavior stays visible; do not swallow. Dual clear with Stage 1 / dispatcher `finally` remains idempotent via `clear_job_batch_lock`.

## Stage 3: draft_job_resume Connection-error acceptance wiring (no new debug strings)

**Done when:** No new found/recorded contract lines; `debug=False` stays quiet; DeepSeek untouched. Builder confirms by reading the Stage 1–2 call chain that `draft_job_resume` + BUILD_ARTIFACTS dispatch ctx + `success=False` / `error="Connection error."` hits hop-label-true helper `finally` release and consult failure/exception release. Engineer does not edit `tests/` / bible.

1. Do **not** special-case the substring `"Connection error"`.
2. Do **not** add files beyond the Files Changed table.
3. Betty note (optional at Code Complete): extend `TestAst1191ArtifactHopFailureRelease` / consult dispatch-chain tests for (a) `draft_job_resume` + Connection error + BUILD_ARTIFACTS ctx → `ERROR_BUILD_ARTIFACTS` + release; (b) `do_task` raising inside `_run_dispatch_chain_job_batch` → `release_job_dispatch_claim` still called; (c) helper `transition_job_state` raising non-`ValueError` → release still called.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; push to `origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error`.
- Do not add files outside the Files Changed table.
- If helper / consult batch shapes have drifted from this plan, stop and comment on **AST-1280** with the Stage N blocked template.
- Deviation from this plan is escalation, not autonomy.

## Self-Assessment

**Scope:** `Single-Component` — `src/core/agent.py` + `src/core/consult.py` (core); no data/external/UI.

**Conf:** `Medium` — AC path is hop-label-true (Joan); tip already releases on clean `success=False`, so confidence rests on closing the exception / non-`ValueError` miss windows that still orphan the claim when inner belts abort.

**Risk:** `Medium` — claim clear on provider-failure and consult exception paths; wrong breadth could clear a lock early, but gating on `provider_failed` / failed-or-raised `do_task` matches claim-process-release and leaves success-path claim lifetime to dispatcher `finally`.

## Self-review vs ASTRAL_CODE_RULES

- §1.3 DRY — still one helper for hop failure side effects; consult only adds exception-safe dual clear, not a third design.
- §2.1 config — no new config keys.
- §2.4 batch / claim-process-release — clear on every early-exit path where the job was claimed and provider/consult failed or raised.
- §2.6 state machine — core still decides `error_state`; `finally` release does not move state on its own.
- §3.3 imports — late `tracker` import in helper preserved; consult already imports `tracker`.
- §1.5.1 debug — found/recorded remain `debug=True` only.

## Revisions

Revision 1 — 2026-08-10
Driven by: Joan `[plan-discuss] round=1 concern` — “Root cause does not match the in-scope job-artifacts dispatch path… Branch A only changes hop-label-false… Stage 1 Branch B is keep AST-1191.”
Changes: Retracted hop-label-false as the AC1 root cause. Re-staged hop-label-true hardening: helper `try`/`finally` release after transition attempt; consult per-job release when `do_task` raises; Files Changed adds `consult.py`; Conf `high` → `Medium`; optional hop-label-false release kept only as defense-in-depth and labeled as non-AC.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error`
**Tip:** `c74972b7`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `91c81ba2` | Helper `try`/`finally` provider release + hop-label-false defense-in-depth |
| 2 | `c74972b7` | Consult per-job release when `do_task` raises |
| 3 | _(verify)_ | Call chain: BUILD_ARTIFACTS ctx → hop-label-true `finally` + consult except/failure release; no new debug strings |
