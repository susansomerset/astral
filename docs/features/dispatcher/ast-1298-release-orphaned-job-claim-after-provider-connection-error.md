<!-- linear-archive: AST-1298 archived 2026-08-19 -->

## Linear archive (AST-1298)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1298/release-orphaned-job-claim-after-provider-connection-error-connection  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1280 — Connection error on dispatch task did not clear the batch_id  
**Blocked by / blocks / related:** parent: AST-1280

### Description

## What this implements

One vertical slice on the **job-artifacts dispatch** path: close the live `draft_job_resume` Connection-error orphaned `batch_id` on the hop-label-true BUILD_ARTIFACTS path by making AST-1191 helper release exception-safe and ensuring `_run_dispatch_chain_job_batch` releases when `do_task` raises — keep configured error/hold + debug `batch_released` honest. Does not own provider retry policy or hop-topology redesign.

## Acceptance criteria

- [X] 1. Reproduce the logged shape on a **job-artifacts dispatch** run: `draft_job_resume` with provider `Connection error.` and `do_task(draft_job_resume) provider call failed batch_id=draft_job_resume-<uuid> error=Connection error.` After the run finishes, that job row’s `batch_id` is null/empty — without operator intervention.
- [X] 2. That job is on `ERROR_BUILD_ARTIFACTS` (or the task’s configured error_state), not left mid-chain under a live claim — unless the failure is a documented balance-refusal hold, in which case state is held and `batch_id` is still cleared.
- [X] 3. A later dispatch claim for the same eligible work can claim that job again (no permanent lock under the failed batch_id).
- [X] 4. With `debug=True` on the failure path, found/recorded lines show a non-empty error and `batch_released=true`. With `debug=False`, no new debug-contract lines are added.
- [X] 5. Healthy `draft_job_resume` success path still claims, processes, and clears normally (no double-clear breakage; no stuck locks on success).

## Boundaries

- [X] Does not own provider retry / backoff for Connection errors.
- [X] Does not redesign `run_next` / BUILD_ARTIFACTS hop topology.
- [X] Does not own AST-1189 timeout budget or AST-1190 empty-response classification beyond consuming structured failure fields.
- [X] Single child for this parent — no sibling slices.
- [X] Does not edit `src/external/**`, `src/data/**`, or `dispatcher.py`. Exception-safe per-job release in `consult._run_dispatch_chain_job_batch` is in scope (Joan plan-discuss amend). Does not edit Betty’s `tests/` / bible tree.

## In scope

- [X] `pattern.batch.entity-claim-process-release` — provider failure / raised `do_task` still claim/process/release; no orphaned `batch_id` (`src/core/agent.py` `_apply_dispatch_chain_hop_failure`, `src/core/consult.py` `_run_dispatch_chain_job_batch`)
- [X] `astral.batch.claim-process-release` — clear job claim on hop-label-true provider-failure early exits and consult exception exits; transition then release when hard-fail applies
- [X] `astral.agent.do-task-delegation` — core consumes structured provider `success=False` / `error` / `failure_class`; no adapter redesign
- [X] `astral.standards.debug-contract-gated` — found/recorded release trail only when `debug=True`
- [X] `astral.standards.logging-via-utils` — keep existing `do_task(...) provider call failed …` ERROR line
- [X] `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` — extend AST-1191 helper + consult dual-clear only; no parallel release design
- [X] `astral.state.core-decides-transitions` — error/hold state changes stay in core via existing hard/balance rules

## Considered but excluded

- [X] `astral.batch.batch-id-first` / `astral.batch.batch-id-format` — consume existing dispatch / hop `task_key-uuid` locks; no new lock shape (`src/data/**` untouched)
- [X] `astral.dispatch.run-next-is-chain-authority` — no `run_next` / BUILD_ARTIFACTS topology change (Boundaries)
- [X] `pattern.config.config-block` / provider timeout budget — AST-1189
- [X] Empty/unusable response classification — AST-1190
- [X] `astral.layers.core-vs-external-bright-line` edits in `src/external/**`
- [X] `astral.standards.data-raises-caller-logs` — no `src/data/**` changes
- [X] Candidate/company claim APIs — AST-1257 family; parent Boundaries
- [X] `src/ui/**` — no stuck-claim chrome
- [X] `src/core/dispatcher.py` — `_run_unified` `finally` `clear_job_batch` left as third belt (unchanged)

## Notes for planning

Adjacent shipped contract: AST-1191 hop-failure release. AC path is hop-label-true BUILD_ARTIFACTS dispatch — harden exception-safe release there; do not treat hop-label-false ungating as the epic fix.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

Publish ref: `sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error`

### Comments

#### radia — 2026-08-10T05:07:31.361Z
[code-rubric] revision=2
**Overall:** DISCUSS
discuss: uncited pattern match — diff shape matches approved `pattern.batch.entity-claim-process-release`, not cited in ticket doc
— Radia

#### betty — 2026-08-10T04:55:48.333Z
1. `tests/component/core/test_agent.py::TestAst1298OrphanedJobClaimRelease` — transition non-`ValueError` still releases; `draft_job_resume` + BUILD_ARTIFACTS + `Connection error.` → `ERROR_BUILD_ARTIFACTS` + `batch_released=true`
2. `tests/component/core/test_agent.py::TestAst1191ArtifactHopFailureRelease` — regression; hop-label-false job release replaces obsolete noop assert
3. `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_dispatch_chain_batch_do_task_raise_releases_claim` — `do_task` raise clears claim before re-raise
4. `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_dispatch_chain_batch_failure_releases_claim` — structured `success=False` still releases

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1298OrphanedJobClaimRelease \
  tests/component/core/test_agent.py::TestAst1191ArtifactHopFailureRelease \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_dispatch_chain_batch_do_task_raise_releases_claim \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_dispatch_chain_batch_failure_releases_claim \
  -q
```

`origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error` @ `38d8bbdf` (`merge-tests(AST-1298): origin/tests bc4b100a2fb20432d9c814475cb900c33a369b53`)

`docs/test-bible/core/agent.md` shasum `848e83a090b993c7cdf0941d5309bc5322e8a36d`

#### katherine — 2026-08-10T04:52:21.977Z
origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error @ 35de382e474cb673b7da44ddba55c39286a2d69c

Betty: extend TestAst1191 / consult dispatch-chain — (a) draft_job_resume + Connection error + BUILD_ARTIFACTS → ERROR_BUILD_ARTIFACTS + release; (b) do_task raise in _run_dispatch_chain_job_batch → release still called; (c) transition_job_state non-ValueError → helper finally still releases.

#### joan — 2026-08-10T04:50:46.849Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1298
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error` @ `204dcac67e1b9e1c220e6defeac797783a2f959d`

## Traceability
AC1→S1–2; AC2→S1; AC3→S1–2; AC4→S3; AC5→S2

Round=1 concern closed: AC path is hop-label-true; Stage 1 `try`/`finally` + Stage 2 consult exception release close the tip miss windows (non-`ValueError` after transition; `do_task` raise skips return-path release). Conf `Medium` is honest. Pattern `pattern.batch.entity-claim-process-release` + considered statutes scored in-session with no violations.

### discuss — Child Description Boundaries still ban consult edits
**Location:** AST-1298 Description Boundaries vs plan Files Changed
**Finding:** Child Boundaries still say “Does not edit … consult/dispatcher runners,” but Stage 2 edits `src/core/consult.py`. Parent Boundaries do not forbid that, and the edit is in scope for AC1.
**Recommendation:** Before or at build handoff, amend the child Description Boundaries to allow exception-safe release in `_run_dispatch_chain_job_batch` while keeping `dispatcher.py` out of scope. Non-blocking for Plan Approved.

— Joan
context_tokens≈68000

#### katherine — 2026-08-10T04:49:36.622Z
[plan-discuss] round=1 reply

Revised plan @ `204dcac67e1b9e1c220e6defeac797783a2f959d`: https://github.com/susansomerset/astral/blob/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error/docs/features/dispatcher/ast-1298-release-orphaned-job-claim-after-provider-connection-error.md

Delta vs round=1 concern:
1. **Retracted** hop-label-false as the AC1 root cause — BUILD_ARTIFACTS dispatch ctx is hop-label-true (agree).
2. **Re-staged hop-label-true belts:** Stage 1 helper `try`/`finally` so `provider_failed` release runs even when `transition_job_state` raises non-`ValueError`; Stage 2 consult per-job release when `do_task` raises (not only `success=False` return).
3. Files Changed adds `src/core/consult.py`; dispatcher `finally` stays third belt, unchanged.
4. Conf `high` → `Medium` (clean `success=False` already released on tip; remaining uncertainty is the exception / non-ValueError miss windows).
5. Hop-label-false release kept only as labeled defense-in-depth — not the epic AC fix.

**Scope:** Single-Component — `agent.py` + `consult.py`.
**Conf:** Medium — see above.
**Risk:** Medium — claim clear on provider-failure / raised `do_task`; success-path lifetime still dispatcher `finally`.

#### joan — 2026-08-10T04:45:32.206Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1298
**Overall:** REVISE
**Publish-ref:** `origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error` @ `4e3cd29774764d141b91b2a8554892e7fdb156ec`

## Traceability
AC1→S1 (gap); AC2→S1 Branch B only (gap vs stated root cause); AC3→S1; AC4→S1–2; AC5→S1 (unchanged success path)

### fix-now — Root cause does not match the in-scope job-artifacts dispatch path (R5/R6)
**Location:** Survey findings / Decision — root cause; Stage 1 Branch A vs Branch B
**Finding:** Plan asserts orphaned `batch_id` because `_apply_dispatch_chain_hop_failure` early-returns `_HOP_FAILURE_NOOP` when `_should_write_dispatch_hop_label` is false. For the parent AC repro (`draft_job_resume` on **job-artifacts dispatch**), `consult._run_dispatch_chain_job_batch` sets `dispatch_trigger_state` to registry `BUILD_ARTIFACTS`, and `dispatch_chain_graduation_target("BUILD_ARTIFACTS")` is set → hop-label write is **true**. On that path AST-1191 already transitions then `release_job_dispatch_claim`, and consult + `dispatcher._run_unified` `finally` `clear_job_batch(bid)` are additional belts. Stage 1 Branch B is “keep AST-1191”; Branch A only changes the hop-label-**false** path, which is not the cited live dispatch ctx. So the planned edit does not explain or close Archie’s orphan on the AC1 path.
**Recommendation:** Before build, either (1) cite evidence the live Connection-error run actually hit hop-label-false (missing/empty `dispatch_trigger_state`, non-graduation trigger, etc.), or (2) re-diagnose which belt failed on the hop-label-true path (consult release skipped, `finally` not run, claim `batch_id` ≠ cleared `bid`, cancel/timeout after ERROR log, etc.) and stage the fix that restores AC1–AC2 on that path. Do not ship Branch-A-only as the epic fix without closing that gap.

### discuss — Self-assessment Conf `high` vs Medium risk / unproven root cause
**Location:** Self-Assessment
**Finding:** Conf `high` rests on the hop-label early-return story; if that branch is not the live repro, confidence is overstated relative to Medium risk on the provider-failure hot path.
**Recommendation:** After root-cause rewrite, re-score Conf to match remaining uncertainty.

— Joan
context_tokens≈62000

#### katherine — 2026-08-10T04:42:53.394Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error/docs/features/dispatcher/ast-1298-release-orphaned-job-claim-after-provider-connection-error.md

`origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error` @ `4e3cd297`

**Scope:** Single-Component — `_apply_dispatch_chain_hop_failure` in `src/core/agent.py` only.
**Conf:** high — AST-1191 helper early-returns `_HOP_FAILURE_NOOP` before provider-failure release when hop-label write is false; ungate release on that branch, keep transition-then-release on the dispatch-chain branch.
**Risk:** Medium — claim clear on every job provider-failure path; breadth limited to `provider_failed + job index`, balance-hold / error_state rules unchanged.

#### katherine — 2026-08-10T04:38:20.527Z
🛑 plan-child blocked (FIX-UAT §0a Diagnosis gate)

Spawn said **FIX-UAT MODE**, but AST-1298 Description is dispatch-parent shaped (`## What this implements` / Citations / AC / Boundaries) — it does **not** include the mandatory UAT bug blocks:

- `## Parent AC (quoted inline)` with parent sentences pasted (not pointer-only)
- `## Diagnosis` with Hypothesis / Correct outcome / Wrong fix to avoid / Related siblings

Parent AST-1280 is **In Progress** (first-ship epic), not User Testing — so this may also be a wrong spawn mode rather than a missing re-file.

Need Chuckles to either:
1. **Re-file** AST-1298 with the fix-uat Description template (What failed / Expected / Repro / Parent AC quotes / Diagnosis / Boundaries), or
2. **Re-spawn plan-child without FIX-UAT MODE** if this is a normal dispatch-parent child for a new epic.

Stopped before plan file / Plan Ready — will not invent Diagnosis or AC quotes.

---

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
| `src/core/consult.py` | `_run_dispatch_chain_job_batch`: per-job `try`/`except` around `do_task` so `release_job_dispatch_claim(aid)` runs on both `success=False` returns and exceptions | core |

**Pattern:** `pattern.batch.entity-claim-process-release` (`canon/patterns/batch/pattern.batch.entity-claim-process-release.md`) — both Files Changed rows instantiate claim → process → release on provider failure / raised `do_task` (paired with statute `astral.batch.claim-process-release`).

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
- §2.4 batch / claim-process-release — clear on every early-exit path where the job was claimed and provider/consult failed or raised. Pattern `pattern.batch.entity-claim-process-release` + statute `astral.batch.claim-process-release`.
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

## Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1298
**Publish ref:** `origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error` @ `38d8bbdf`
**Overall:** DISCUSS

Diff scope (`git diff origin/dev...origin/<publish-ref>`): `src/core/agent.py` (modify, core), `src/core/consult.py` (modify, core), `docs/features/dispatcher/ast-1298-...md` (add, docs), `docs/test-bible/core/agent.md` (modify, docs), `tests/component/core/test_agent.py` + `tests/component/core/test_consult.py` (modify, Betty's `test(AST-1298)` commit, merged via one `merge-tests` commit).

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine stays assignee through Tests Passed per spawn prompt |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | no Chuckles-assignee action in this review |
| orch.roles.pre-commit-path-bans | universal | conforms | `code()` commits touch only `src/core/agent.py` / `src/core/consult.py`, never test-tree paths |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/ + test-bible edits live in Betty's own `test(AST-1298)` commit, pulled in via `merge-tests` |
| orch.pipeline.plan-is-bible | universal | conforms | plan formally revised (Revision 1) after Joan round=1 before build; stages executed as written |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a — single explicit ticket id, no queue mode |
| orch.pipeline.status-gates-skill-entry | universal | conforms | entered review-child from Tests Passed per spawn prompt |
| orch.roles.archie-approves-statutes | universal | conforms | no `canon/statutes/**` edits in this diff |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | root-cause revision resolved via Joan round=1 discussion, not improvised |
| orch.git.one-epic-worktree-per-parent | universal | conforms | single `astral-AST-1280/` epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branch |
| orch.git.no-dev-agent-branches | universal | conforms | no `dev-<agent>` branch created |
| orch.git.commit-vocabulary | universal | conforms | `docs()` (plan/review-stub), `code()`, `test()`, `merge-tests()` types used correctly |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1280/AST-1298-...` naming, no invented ref |
| orch.git.merge-on-checkout | universal | conforms | plan doc records tip-after-`sync-child`; no stale-seed evidence |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | linear fast-forward commit chain, no rebase/force in log |
| orch.git.flow-direction-inviolable | universal | conforms | `tests`→`sub` via one `merge-tests` commit; no `tests`↔`dev` merge |
| orch.git.betty-merge-tests-one-sha | universal | conforms | exactly one `merge-tests(AST-1298): origin/tests bc4b100a...` commit |
| astral.agent.confidence-bounds | scoped | conforms | no grading/confidence math touched |
| astral.agent.do-task-delegation | scoped | conforms | `do_task` call site wrapped in `try`/`except` only; no inline external I/O added |
| astral.agent.grade-vector-validation | scoped | conforms | no vector/grade validation touched |
| astral.batch.batch-id-first | scoped | conforms | no new batch claim/get/clear helper signatures; `release_job_dispatch_claim(index)` call order unchanged |
| astral.batch.batch-id-format | scoped | conforms | no new `batch_id` construction in diff |
| astral.batch.claim-process-release | scoped | conforms | diff directly hardens claim→process→release: `finally`-based release in the hop-failure helper, release-on-raise in the consult per-job loop; dispatcher `finally` third belt untouched |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data/response persistence touched |
| astral.config.config-source-of-truth | scoped | conforms | no new inline config; reuses existing `cfg.*` / `task_config` values |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env-specific values touched |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | statute file absent from `canon/statutes/astral/debug/` (registry drift, see Notes); diff writes no repo-root artifacts dir regardless |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | statute file absent from `canon/statutes/astral/debug/` (registry drift, see Notes); diff adds no `debug/` spike files regardless |
| astral.dispatch.seed-auto-false | scoped | not-applicable | paths restricted to `dispatcher.py` / `config.py`; diff touches neither |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | no new config hop-membership/frozenset; hop-label helpers still read `run_next`-derived ctx |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `docs/features/dispatcher/ast-1298-...md`, no duplicate |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty's `test(AST-1298)` commit touches only `tests/` + `docs/test-bible/` |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code()` commits touch only `src/core/agent.py` / `src/core/consult.py` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | `do_task` remains the only I/O boundary; no new I/O added in core |
| astral.layers.import-direction | scoped | conforms | core→core `tracker` import only; no cross-layer import added |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` changes in diff |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no `src/ui/**` or `config.py` changes |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | `release_job_dispatch_claim` clears a lock, not a cached coat-check value |
| astral.idioms.render-verdict-orchestrates-consult | scoped | conforms | dispatcher/`render_verdict` orchestration untouched; change is inside the existing dispatch-chain batch helper |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no `src/ui/**` endpoint changes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | diff touches none of `repo_admin_json.py` / `bootstrap.py` / `config.py` / `data/admin/**` |
| astral.seed.archie-catalog-wins | scoped | not-applicable | `dispatcher.py` / `config.py` / `data/admin/**` untouched |
| astral.seed.boot-only-not-hot-path | scoped | conforms | no seed/bootstrap logic touched; change is runtime exception handling, unrelated to boot-time seeding |
| astral.seed.define-approved | scoped | conforms | no new/expanded product seed invented |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | `dispatcher.py` / `src/data/**` / `config.py` untouched |
| astral.seed.other-via-coverage-join | scoped | not-applicable | `dispatcher.py` / `config.py` / `src/data/**` untouched |
| astral.standards.data-raises-caller-logs | scoped | conforms | `logger.warning` stays in core (agent.py); no data-layer logging added |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` changes |
| astral.standards.debug-contract-gated | scoped | conforms | `debug_detail` stays under existing `if debug:` gate; no new `logger.info("[DEBUG] …")`; format shape unchanged from the pre-existing hop-label-true line |
| astral.standards.dry-and-focused-functions | scoped | conforms | `try`/`finally` consolidation removes a duplicate release call site rather than adding one |
| astral.standards.in-scope-only | scoped | conforms | diff matches Files Changed exactly: `src/core/agent.py` + `src/core/consult.py` |
| astral.standards.logging-via-utils | scoped | conforms | only existing `get_logger` / `_do_task_debug_logger` / module `logger` used |
| astral.standards.names-not-ticket-ids | scoped | conforms | no new ticket-id-named identifiers in `src/**`; `AST-1298` appears only in comments (carve-out) |
| astral.standards.no-cross-contamination | scoped | conforms | no out-of-layer reference added |
| astral.standards.no-hardcoded-sets | scoped | conforms | no new inline state/value sets; reuses `cfg.*` constants |
| astral.standards.public-then-helpers | scoped | conforms | function order/position unchanged |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no `src/utils/**` changes |
| astral.state.core-decides-transitions | scoped | conforms | `transition_job_state` still called with a core-chosen `err_state`; data layer untouched |
| astral.state.job-prior-states-enforced | scoped | conforms | `transition_job_state` prior_states enforcement path unchanged; diff only wraps the existing call |
| astral.state.no-daisy-chain-in-run | scoped | conforms | no new multi-hop auto-transition; release-on-failure is a lock-clear, not a state daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no `src/ui/**` changes |
| astral.ui.naming-conventions | scoped | not-applicable | no `src/ui/**` changes |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no `src/ui/**` / `scripts/**` / `config.py` changes |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | ticket doc cites no `canon/patterns/**` id — see discuss finding below |

### Plan adherence

Diff matches the Files Changed table exactly for engineer scope (`src/core/agent.py`, `src/core/consult.py`); Betty's test/bible edits arrive via her own commit + one `merge-tests` merge, not engineer edits. Stage 1 and Stage 2 "Done when" criteria are met and covered by `TestAst1298OrphanedJobClaimRelease` + the revised `TestAst1191ArtifactHopFailureRelease` + `TestAst371ResumeArtifactDispatch` cases (verified against the diff, not re-run here). Stage 3 required verification only (no code change) — call chain confirmed: `draft_job_resume` + `BUILD_ARTIFACTS` ctx + `success=False`/raise both now route through the hardened hop-label-true `finally` release and the consult except/failure release; no new debug-contract strings added. Self-Assessment Scope (`Single-Component`) matches actual footprint; Conf `Medium` / Risk `Medium` carry no red flags requiring escalation.

### Findings

**discuss:** Uncited pattern match — `src/core/consult.py`'s new `try`/`except`/release wrap around `do_task`, and `src/core/agent.py`'s `try`/`finally` release, both instantiate the shape of approved `pattern.batch.entity-claim-process-release` (`canon/patterns/batch/pattern.batch.entity-claim-process-release.md`), but neither the Files Changed table nor the Self-review section cites it. Not a functional defect — recommend citing the pattern id in the next plan/doc touching this helper for traceability (code-rubric.v2 C5).

### Notes

- No Joan plan-rubric verdict attachment is present on this ticket doc (only narrative "Revision 1" driven by a Joan round=1 comment) — per C4 straggler rule this is not a block; noting `no plan-rubric verdict attached`.
- Corpus drift (out of scope for this ticket, flagged downstream): `canon/statutes/README.md` § Harvested corpus lists `astral.debug.no-repo-root-artifacts-dir` and `astral.debug.spikes-under-debug-dir`, but `canon/statutes/astral/debug/` does not exist in the tree. Scored `not-applicable` to this diff either way; the registry/tree mismatch itself may warrant its own corpus-integrity ticket.
- Style nit (advisory, not fix-now): in `consult.py`'s new `except BaseException:` arm, `errors += 1` runs immediately before `raise` — the function always exits via the exception on that path, so the incremented counter is never read from a returned dict. Harmless; a future cleanup could drop it.

context_tokens≈60000

## Resolution

**Date:** 2026-08-10  
**Review:** [code-rubric] revision=2 — DISCUSS (no fix-now)

| Item | Action |
|------|--------|
| **discuss** — uncited `pattern.batch.entity-claim-process-release` | Cited under Files Changed + Self-review §2.4 (Linear In scope already listed the pattern id). |
| **advisory** — dead `errors += 1` before `raise` in consult except arm | Dropped the unused increment; release + re-raise unchanged. |

No product behavior change beyond the advisory cleanup. §9a dry-run vs `origin/dev` at resolve tip.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Katherine | engineer | `/home/susan/.cursor/chats/8675e3708318a1930b78ec858d53d9c0/5af8be6e-5434-4a78-8569-610b4b259765/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/76fc0138-37b1-4b19-a7a4-330a6a5a4aea/store.db` |
| Radia | review | `/home/susan/.cursor/chats/8675e3708318a1930b78ec858d53d9c0/599ee163-c3a6-4ef7-bab8-37ca369b84a1/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1280 (parent) | ftr/AST-1280-connection-error-on-dispatch-task-did-not-clear-the-batch-id |
| AST-1298 | sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error |

**Epic worktree:** `astral-AST-1280/` — one active sub checked out at a time.

## Bug: AST-1941 — Hold state on BUILD_ARTIFACTS hop provider failure

**Linear:** [AST-1941](https://linear.app/astralcareermatch/issue/AST-1941) (fix child of mini-parent [AST-1940](https://linear.app/astralcareermatch/issue/AST-1940) — BUG: BUILD_ARTIFACTS -> ERROR_BUILD_ARTIFACTS)
**Publish ref:** `origin/sub/AST-1940/AST-1941-hold-state-on-hop-provider-failure` (ftr `ftr/AST-1940-hop-failure-preserve-state`)
**Explicit scope:** AST-1941 `## Scope` (verbatim copy of AST-1940 Component/Technical scope). No ancestor scope imported. No Canon Scope list on AST-1941 / AST-1940; no canon ids resolved for this pass.

### As-is

When a provider call fails on a hop-label-true BUILD_ARTIFACTS dispatch-chain hop (for example a job on `BUILD_ARTIFACTS.anticipate_scan`, or `draft_job_resume` returning `Connection error.`), `_apply_dispatch_chain_hop_failure` in `src/core/agent.py` classes every **non-balance** provider failure as hard. It calls `transition_job_state([index], "ERROR_BUILD_ARTIFACTS")` and then releases the claim. The job leaves the BUILD_ARTIFACTS chain claim pool and the hop is never retried. Only provider balance refusals (AST-897) hold state today.

### To-be

A provider failure on a BUILD_ARTIFACTS hop does **not** change the job's state. The job keeps its last happy state / hop label, the claim is still released (`batch_id` cleared), and the next dispatch sweep reclaims it and retries the hop. `ERROR_BUILD_ARTIFACTS` is reserved for `Job not found` / `Missing candidate_data`. The provider ERROR line, Execution History against the batch_id, and the AST-538 debug detail are unchanged. No retry cap or backoff (Susan's rule).

### Repro

Read on worktree tip `de2664949` (`== origin/dev`; `src/core/agent.py` has no diff vs `origin/dev`). `src/core/agent.py` L1123–L1131:

```python
err_state = (task_config.get("error_state") or "").strip()
balance_hold = provider_failed and is_provider_balance_refusal(
    {"failure_class": failure_class}
)
hard = bool(err_state) and (
    "Job not found" in error
    or "Missing candidate_data" in error
    or (provider_failed and not balance_hold)   # AST-1191 (7f5b132e) — the defect
)
```

Fixture repro (no DB; same ctx shape as `TestAst1191ArtifactHopFailureRelease._dispatch_ctx`):

```python
ctx = {
    "astral_candidate_id": "somerset",
    "candidate_data": {"artifacts": {}},
    "batch_entities": [{"astral_job_id": "job-1941"}],
    "dispatch_trigger_state": cfg.BUILD_ARTIFACTS_BASE_STATE,   # hop-label-true
    "dispatch_chain_graduate_on_terminal": True,
}
agent._apply_dispatch_chain_hop_failure(
    entity_type="job", index="job-1941", ctx=ctx,
    task_config={"error_state": cfg.ERROR_BUILD_ARTIFACTS_STATE},
    error="Connection error.", debug=False,
    provider_failed=True, failure_class="provider_connection_error",
)
# Today:  tracker.transition_job_state(["job-1941"], "ERROR_BUILD_ARTIFACTS") is called;
#         returns {"apply_error_state": True, "error_state": "ERROR_BUILD_ARTIFACTS", "batch_released": True}
# To-be:  transition_job_state not called;
#         returns {"apply_error_state": False, "error_state": "", "batch_released": True}
```

Live shape: `do_task(...)` provider-failure branch (`src/core/agent.py` ~L2296) → `_close_hop_ledger(success=False, provider_failed=True, failure_class=…)` → this helper. The existing tests `TestAst1191ArtifactHopFailureRelease::test_apply_provider_failed_transitions_and_releases` and `TestAst1298OrphanedJobClaimRelease::test_do_task_draft_job_resume_connection_error_releases_and_errors` already pin the broken behavior (they assert the `ERROR_BUILD_ARTIFACTS` transition).

Retry path confirmed: for BUILD_ARTIFACTS chain triggers, `dispatcher` job claims use `dispatch_chain_claim_states_for_row` + `dispatch_chain_row_matches_job` (AST-596 / AST-803), so a job held on `BUILD_ARTIFACTS.<hop>` with a cleared `batch_id` is reclaimable on the next sweep.

### Root cause

AST-1191 (commit `7f5b132e`) added `or (provider_failed and not balance_hold)` to the `hard` predicate. That overrode the earlier rule (AST-596 / AST-788 / AST-803) that only `Job not found` / `Missing candidate_data` are hard and every other hop failure stays on the last happy compound state for retry. AST-1298 then hardened claim release around that same transition, but did not revisit the predicate. AST-1298 AC2 ("job is on `ERROR_BUILD_ARTIFACTS` … unless balance-refusal hold") is the half this fix deliberately supersedes; its claim-release half stays.

### Proposed change

Single file, single function family: `src/core/agent.py`.

1. **`_apply_dispatch_chain_hop_failure`, hop-label-true branch** — replace L1123–L1131 (the `err_state` / `balance_hold` / `hard` block) with:

   ```python
   err_state = (task_config.get("error_state") or "").strip()
   # Only a missing job / missing candidate_data is unrecoverable. Provider failures (balance
   # or otherwise) hold the last happy state / hop label; the finally release below lets the
   # next dispatch sweep reclaim and retry the hop. No retry cap by design.
   hard = bool(err_state) and (
       "Job not found" in error
       or "Missing candidate_data" in error
   )
   ```

   - `balance_hold` is deleted (its only purpose was to exempt balance refusals from the provider clause, which no longer exists).
   - Everything after it stays byte-for-byte: `apply_error_state` / `batch_released` init, the `try` / inner `try … except ValueError` transition, the `finally` release (which on tip releases unconditionally on this branch — AST-1298 `91c81ba2`), and the return dict. With `hard` false, the result is `{"apply_error_state": False, "error_state": "", "batch_released": True}`.
   - Hop-label-false branch (L1110–L1122) unchanged.

2. **Import block** (`src/core/agent.py` L49–L53) — drop `is_provider_balance_refusal,` from the `from src.utils.llm_external import (…)` list. The helper above was its only use in `agent.py` (grep: no other `agent.py` reference, and nothing in `src/` / `tests/` / `scripts/` reaches it through `agent`). Leaving it would fail lint (unused import).

3. ⚠️ **Decision — keep the `failure_class` parameter.** It becomes unused inside the helper. Keep it in the signature so the `_close_hop_ledger` → helper kwargs and the `do_task` provider-failure call site stay unchanged (AST-1298 Stage 1 step 4). Removing it would be a signature change outside this bug's delta.

4. ⚠️ **Decision — no special-casing.** No `failure_class` allow-list, no `Connection error` substring check, no retry counter / backoff / cap, no new config keys. Balance refusal and every other provider failure now take the same hold-and-release path.

5. Compile + lint `src/core/agent.py` before commit (`python -m py_compile src/core/agent.py` + repo lint). Engineer does not edit `tests/` or the bible.

### Blast radius

- **Callers:** only `_close_hop_ledger` inside `do_task` (L2183). Its result (`hop_fail_outcome`) is not read after assignment, so the outcome-dict change affects tests only. `consult._run_dispatch_chain_job_batch` and `dispatcher._run_unified` keep their own claim-release belts (AST-1298 Stage 2 / third belt) — untouched and still idempotent.
- **Tests that assert the broken behavior (Betty's tree, `tests/component/core/test_agent.py`):**
  - `TestAst1191ArtifactHopFailureRelease::test_apply_provider_failed_transitions_and_releases` → expect `apply_error_state is False`, `error_state == ""`, `batch_released is True`, `transition.assert_not_called()`, release called once.
  - `TestAst1191ArtifactHopFailureRelease::test_do_task_provider_timeout_releases_and_errors`, `::test_do_task_debug_emits_found_and_recorded`, `::test_do_task_debug_false_skips_found_recorded` → `transition.assert_not_called()`; release still called once.
  - `TestAst1298OrphanedJobClaimRelease::test_do_task_draft_job_resume_connection_error_releases_and_errors` → `transition.assert_not_called()`; release still called once.
  - `TestAst1298OrphanedJobClaimRelease::test_apply_transition_non_value_error_still_releases` → **breaks differently**: with `Connection error.` the transition is no longer attempted, so `pytest.raises(RuntimeError)` fails. To keep AST-1298's "non-`ValueError` from transition still releases" invariant covered, switch its `error` to a hard string (e.g. `"Job not found"`); expectations otherwise unchanged.
  - Unchanged / still green: `TestAst1191…::test_apply_balance_hold_skips_error_state_but_releases`, `::test_apply_hop_label_false_*`, and the hard-string do_task test at ~L5603 (`Missing candidate_data` → `ERROR_BUILD_ARTIFACTS` + release).
- **Test bible:** `docs/test-bible/core/agent.md` § AST-1191 · AST-1164 (L366) states "non-balance provider failures apply `error_state`" — Betty updates to the held-state rule.
- **Runtime behavior:** a persistently failing provider is retried on every sweep (same as balance holds today). Approved by Susan in AST-1940; no cap added.
- No `TASK_CONFIG` `error_state`, `JOB_STATES` / prior-states, `run_next`, hop topology, LLM adapter, or consult failure-branch change.

### What must still hold

- AST-1298 AC1 / AC3: after any provider failure on a hop-label-true BUILD_ARTIFACTS hop, the job row's `batch_id` is cleared and a later dispatch claim can reclaim it (`finally` release untouched; `batch_released: True`).
- AST-1298 Stage 1: a non-`ValueError` raised by `transition_job_state` (now only reachable on hard strings) still cannot skip the release.
- AST-1298 hop-label-false defense-in-depth release (job + `provider_failed`) unchanged; non-job / no-index hop-label-false still returns `_HOP_FAILURE_NOOP`.
- `Job not found` / `Missing candidate_data` still transition to `ERROR_BUILD_ARTIFACTS` (configured `error_state`) and release.
- AST-897 balance refusal still holds state and releases (now via the same path as every provider failure).
- AST-1298 AC4 / AST-1191 debug trail: `do_task` provider-failure logging (`log_llm_batch_summary(..., error=)` hop error line, non-empty error coercion, AST-538 `debug=True` detail) is not touched by this change.
- AST-1298 AC5: success path claim/process/clear unchanged (helper is only called on failure).
- **Superseded on purpose:** AST-1298 AC2's "job is on `ERROR_BUILD_ARTIFACTS`" for provider failures — now held state instead.

### Joan fix-board — AST-1941

**Triage:** The change narrows the hop-label-true `hard` predicate back to `"Job not found"` / `"Missing candidate_data"` only, keeps AST-1298’s `finally` claim release, and holds state for all provider failures (balance included) so the next sweep can reclaim. That matches **`astral.batch.claim-process-release`** as AST-1298 scored it (“transition then release **when hard-fail applies**”), **`patt.task.dispatch-retry`** / AST-788–AST-596 retry-on-last-hop intent, and AST-897’s documented expectation that balance (and other provider) failures on this helper stay retryable — AST-1191’s provider clause was the regression, not canon law. **`astral.state.core-decides-transitions`**, debug/logging statutes, and **`astral.dispatch.run-next-is-chain-authority`** are untouched. Superseding AST-1298 AC2 (“on `ERROR_BUILD_ARTIFACTS`”) is an explicit, Susan-approved product correction in **What must still hold**, not an in-force statute amend. **`docs/test-bible/core/agent.md`** prose is Betty’s test-tree work (blast radius), not a statute/pattern landing — so not **CANON: REVISE**. No ambiguous new precedent or unbounded architectural call → not **ESCALATE**.

```text
[board-joan]  CANON: OK

context_tokens≈14000
```

### Radia review-fix — AST-1941

[code-rubric]
**Ticket:** AST-1941
**Publish ref:** `75baf6cc4dbf9e5dd302a5875ea25fd1ddd7c89f` (`origin/sub/AST-1940/AST-1941-hold-state-on-hop-provider-failure`)
**Corpus:** (none cited — frozen Canon Scope empty on Linear description; plan-fix records the same)
**Overall:** CLEAN

## Canon scores

*(Frozen Canon Scope on Linear description: **none** — plan-fix § Bug: AST-1941: “No Canon Scope list on AST-1941 / AST-1940; no canon ids resolved for this pass.” No directive ids to score; roll-up from canon grades is vacuously clean. Fix-board Joan `[board-joan] CANON: OK` overlap narrative is context only, not a substitute frozen list. Off-list statutes named in Joan’s triage were not graded per review-child §5.3.)*

## Column diff vs plan stage

no plan-stage scores attached (Joan fix-board only; no `validate-plan` fix-mode canon table on this ticket)

## Frame diff

(none)

## Fix-specific checks

**[bug-repro]** not applicable — clean board opt-out: `qa-fix` did not run; fix-board `TESTS: REVISE` test/bible work was split to gap sibling **AST-1942** (per spawn prompt). Do not score missing `[bug-repro]` on this tip.

**## What must still hold — OK**

| Item | Verdict |
|------|---------|
| AST-1298 AC1/AC3: provider failure on hop-label-true BUILD_ARTIFACTS clears `batch_id` (`finally` release; `batch_released: True`) | OK — `try`/`finally` release block unchanged; only `hard` predicate narrowed |
| AST-1298 Stage 1: non-`ValueError` from `transition_job_state` cannot skip release | OK — inner `try`/`except ValueError` + `finally` release intact; hard paths still reach transition |
| Hop-label-false defense-in-depth (`provider_failed` + job) unchanged | OK — L1110–L1121 untouched |
| `Job not found` / `Missing candidate_data` → configured `error_state` + release | OK — sole `hard` conditions retained |
| AST-897 balance refusal holds state and releases | OK — now same hold-and-release path as all provider failures (plan decision § Proposed change item 4) |
| AST-1298 AC4 / AST-1191 debug trail (`do_task` provider-failure logging) | OK — no edits outside `_apply_dispatch_chain_hop_failure` hop-label-true predicate + import trim |
| AST-1298 AC5 success path | OK — helper only on failure path |
| Superseded AST-1298 AC2 (provider → `ERROR_BUILD_ARTIFACTS`) | OK — intentionally reversed per plan **What must still hold** |

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Sibling test carry / board split:** Product diff is `src/core/agent.py` only (+ plan doc). Linear **Scope** still lists `tests/component/core/test_agent.py`; board **TESTS: REVISE** and Katherine’s **test-fix** comment document **six** expected `tests/component/core/test_agent.py` failures on this tip, owned by **AST-1942** — not a product defect on AST-1941. Treat AST-1941 as the product slice; do not route product `resolve-child` for those reds.
- **Plan fidelity:** Matches plan-fix **Proposed change** (remove `balance_hold` / provider clause from `hard`, drop unused `is_provider_balance_refusal` import, keep `failure_class` in signature, hop-label-false branch byte-stable).

### Notes

- **Diff base:** `origin/ftr/AST-1940-hop-failure-preserve-state...origin/sub/AST-1940/AST-1941-hold-state-on-hop-provider-failure` — 2 files, +126/−5 (docs plan patch + 8-line product change).
- **Canon Scope gap → ESCALATE:** not warranted (empty list is explicit; board cleared canon at F2).
- **Chuckles post-review (§8):** **PROCEED** + **Normal** parent shape — mini-parent **AST-1940** with live `ftr/AST-1940-hop-failure-preserve-state` (not fix-lane **ORPHANED** / dev-seeded). → **Review Posted** → clean-review shortcut → **User Testing** (skip `resolve-child`). Do **not** use orphaned finish-up merge-to-`dev` path for this ticket.

### What's solid

- Minimal, surgical predicate change with inline comment tying hold-and-release to AST-596 / sweep retry intent.
- Blast-radius call sites (`_close_hop_ledger` / `do_task`) and AST-1298 release belt left intact.

context_tokens≈22000

---

```
[code-rubric] PROCEED (Commit: 75baf6cc4dbf9e5dd302a5875ea25fd1ddd7c89f) product hold predicate
```

### Resolution — AST-1941

docs-acceptance: product-only fix. The six `test_agent.py` flips and the bible update (Betty `[board-betty] TESTS: REVISE`) land on gap sibling AST-1942, stacked after this ticket on `ftr/AST-1940-hop-failure-preserve-state`.

## Bug: AST-1942 — Flip hop provider-failure tests to held state

**Linear:** [AST-1942](https://linear.app/astralcareermatch/issue/AST-1942) (test-gap sibling of AST-1941, mini-parent [AST-1940](https://linear.app/astralcareermatch/issue/AST-1940); filed from Betty's `[board-betty] TESTS: REVISE` on AST-1941)
**Publish ref:** `origin/sub/AST-1940/AST-1942-flip-hop-provider-failure-tests` (ftr `ftr/AST-1940-hop-failure-preserve-state`)
**Explicit scope:** AST-1942 `## Scope` — `tests/component/core/test_agent.py` (modified test functions only, no new fixtures) + `docs/test-bible/core/agent.md` (§ AST-1191 · AST-1164 and § AST-1298 · AST-1280 prose/rows). **No product code** (AC4). No Canon Scope list on AST-1942. Executor: Betty (test tree + bible).

### As-is

AST-1941's product fix (`75baf6cc`, already on this sub's tip via `ftr`) makes every provider failure on a hop-label-true BUILD_ARTIFACTS hop hold state and release the claim. Six existing `test_agent.py` tests still assert the superseded provider-failure → `ERROR_BUILD_ARTIFACTS` transition, so they fail on this tip. The bible's § AST-1191 · AST-1164 still says "non-balance provider failures apply `error_state`", and two § AST-1298 · AST-1280 rows describe the old Connection-error → `ERROR_BUILD_ARTIFACTS` outcome.

### To-be

The six tests assert the held-state rule ("no transition, claim released once"). The non-`ValueError`-still-releases invariant (AST-1298 Stage 1) stays covered by driving it with a hard error string. The bible states that provider failures hold state and only `Job not found` / `Missing candidate_data` apply `error_state`. Balance-hold, hop-label-false, and `Missing candidate_data` hard-string tests are untouched and green.

### Repro

Observed at AST-1941 test-fix (tip `75baf6cc`, same tests as this tip): tip with fix 46 failed / 355 passed vs. the same tree with `origin/ftr`'s pre-fix `src/core/agent.py` 40 / 361. The 40 shared failures pre-exist and are out of scope. The 6 new ones, and their messages:

| Node (`tests/component/core/test_agent.py::…`) | Failure on fixed tip |
|---|---|
| `TestAst1191ArtifactHopFailureRelease::test_apply_provider_failed_transitions_and_releases` | `assert False is True` (`apply_error_state`) |
| `TestAst1191ArtifactHopFailureRelease::test_do_task_provider_timeout_releases_and_errors` | transition `Called 0 times` |
| `TestAst1191ArtifactHopFailureRelease::test_do_task_debug_emits_found_and_recorded` | transition `Called 0 times` |
| `TestAst1191ArtifactHopFailureRelease::test_do_task_debug_false_skips_found_recorded` | transition `Called 0 times` |
| `TestAst1298OrphanedJobClaimRelease::test_do_task_draft_job_resume_connection_error_releases_and_errors` | transition `Called 0 times` |
| `TestAst1298OrphanedJobClaimRelease::test_apply_transition_non_value_error_still_releases` | `DID NOT RAISE RuntimeError` |

**Bug-repro node (AC1):** the revised apply-level test (Proposed change item 1). It must be **red** against `origin/dev`'s `src/core/agent.py` (the provider clause transitions → `transition.assert_not_called()` fails) and **green** on this tip. Verification recipe (test tree untouched by the engineer; `src/core/agent.py` restored afterwards):

```bash
NODE='tests/component/core/test_agent.py::TestAst1191ArtifactHopFailureRelease::test_apply_provider_failed_holds_state_and_releases'
git checkout origin/dev -- src/core/agent.py
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh "$NODE" -q   # expect 1 failed
git checkout HEAD -- src/core/agent.py
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh "$NODE" -q   # expect 1 passed
git status --short src/core/agent.py                                                                     # expect clean
```

### Root cause

The tests were written for AST-1191 / AST-1298 when the `hard` predicate in `_apply_dispatch_chain_hop_failure` included `(provider_failed and not balance_hold)`. AST-1941 removed that clause on purpose (superseding AST-1298 AC2). The tests and bible pin the removed behavior; they are stale, not the product.

### Proposed change

All edits in Betty's tree. Every other test in both classes stays byte-for-byte.

**`tests/component/core/test_agent.py`**

1. **`TestAst1191ArtifactHopFailureRelease` class docstring** (~L6066): `"""AST-1191: provider hop failure → error_state + claim release + debug trail."""` → `"""AST-1191 / AST-1941: provider hop failure → held state + claim release + debug trail."""`
2. **`test_apply_provider_failed_transitions_and_releases`** (~L6077) — **the bug repro.**
   - ⚠️ **Decision — rename** to `test_apply_provider_failed_holds_state_and_releases`. The old name asserts the opposite of the new behavior; leaving it would make the node id lie. Only this test is renamed; the other five keep their names (each name still holds: `do_task` still returns `success=False` / "errors", debug still emits).
   - Same inputs (ctx, `error="Provider call exceeded per-call time budget (600s)"`, `provider_failed=True`, `failure_class="provider_call_timeout"`).
   - Replace the four assertions with:
     ```python
     assert out == {"apply_error_state": False, "error_state": "", "batch_released": True}
     transition.assert_not_called()
     release.assert_called_once_with("job-1191")
     ```
3. **`test_do_task_provider_timeout_releases_and_errors`** (~L6201), **`test_do_task_debug_emits_found_and_recorded`** (~L6248), **`test_do_task_debug_false_skips_found_recorded`** (~L6288): replace `transition.assert_called_once_with(["job-1191"], cfg.ERROR_BUILD_ARTIFACTS_STATE)` with `transition.assert_not_called()`. Keep `release.assert_called_once_with("job-1191")` and every other assertion.
4. **`TestAst1298OrphanedJobClaimRelease::test_do_task_draft_job_resume_connection_error_releases_and_errors`** (~L6375): same swap → `transition.assert_not_called()`; keep `out["success"] is False`, `out.get("error") == "Connection error."`, `release.assert_called_once_with("job-1298")`.
5. **`TestAst1298OrphanedJobClaimRelease::test_apply_transition_non_value_error_still_releases`** (~L6305): change only `error="Connection error."` → `error="Job not found"` (a hard string, so the transition is attempted and the `RuntimeError` side effect fires). Leave `provider_failed=True` / `failure_class` as-is (the hard string decides `hard` regardless). Update the comment to: `# Non-ValueError from transition (hard string) must not skip finally release (AST-1298 Stage 1).` Assertions unchanged: `pytest.raises(RuntimeError, match="transition blew up")`, transition called once with `ERROR_BUILD_ARTIFACTS`, release called once.

**`docs/test-bible/core/agent.md`**

6. **§ AST-1191 · AST-1164 prose** (~L366): replace `non-balance provider failures apply \`error_state\` then \`release_job_dispatch_claim\`; balance refusal holds state but still releases claim;` with `provider failures (balance or otherwise) hold state — no \`error_state\` — and release the claim; only \`Job not found\` / \`Missing candidate_data\` apply \`error_state\` then release (**AST-1941**, supersedes the AST-1191 provider → \`error_state\` rule);`. Rest of the paragraph unchanged.
7. **§ AST-1191 · AST-1164 table, row 1** (~L370): area `Hop failure apply + claim release + debug` → `Hop failure apply (provider → held state) + claim release + debug`. Add one row after it: `| Bug repro: provider failure holds state (AST-1941 / AST-1942) | \`src/core/agent.py\` | **\`TestAst1191ArtifactHopFailureRelease::test_apply_provider_failed_holds_state_and_releases\`** |`.
8. **§ AST-1298 · AST-1280 prose** (~L386): after `helper \`try\`/\`finally\` still releases when \`transition_job_state\` raises non-\`ValueError\`` insert ` (reachable on hard strings only since AST-1941)`.
9. **§ AST-1298 · AST-1280 rows** (~L390–L391):
   - `Transition non-\`ValueError\` still releases` → `Transition non-\`ValueError\` (hard string \`Job not found\`) still releases`.
   - `` `draft_job_resume` Connection error → `ERROR_BUILD_ARTIFACTS` + release + debug `` → `` `draft_job_resume` Connection error → held state (no transition) + release + debug (AST-1941) ``.
   - Node ids in those rows unchanged.

⚠️ **Decision — no new bible section.** AST-1942 scope is "modified bible prose/rows for the AST-1191 / AST-1298 entries", so the repro and rule change go into those entries (items 6–9), not a new § AST-1941.

### Blast radius

- Only the six nodes above plus the one class docstring change in `test_agent.py`. The rename in item 2 changes one node id: the AST-1191 bible row added in item 7 carries the new id. Earlier Linear comments (AST-1941 test-fix) cite the old id as history — no edit needed.
- **Unchanged and must stay green:** `TestAst1191…::test_apply_balance_hold_skips_error_state_but_releases`, `::test_apply_hop_label_false_job_provider_failed_releases`, `::test_apply_hop_label_false_non_job_returns_noop`, `TestAst848DispatchChainDoTask::test_hard_failure_transitions_error_build_artifacts` (~L5603, `Missing candidate_data`), and the consult `TestAst371ResumeArtifactDispatch` release tests (they mock `do_task`; unaffected).
- `tests/integration/`: no scenario touches this path (Betty confirmed at board).
- No `src/**` edits.

### What must still hold

- AC1: the bug-repro node is red on `origin/dev`'s `src/core/agent.py` and green on this tip (recipe in Repro).
- AC2: the repointed non-`ValueError` test still proves release runs when `transition_job_state` raises non-`ValueError` (transition attempted once, release once, `RuntimeError` propagates).
- AC3: balance-hold, hop-label-false, and `Missing candidate_data` hard-string tests are unchanged and pass.
- AC4: no product code on this ticket.
- After this lands, `test_agent.py` + `test_llm_external.py` on this tip fail only on the 40 pre-existing nodes shared with the pre-fix baseline — the six AST-1941 nodes are green.
