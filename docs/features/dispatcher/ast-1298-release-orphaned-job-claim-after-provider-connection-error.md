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
