# AST-1298 — Release orphaned job claim after provider Connection error

**Linear:** [AST-1298](https://linear.app/astralcareermatch/issue/AST-1298/release-orphaned-job-claim-after-provider-connection-error-connection)
**Parent:** [AST-1280](https://linear.app/astralcareermatch/issue/AST-1280/connection-error-on-dispatch-task-did-not-clear-the-batch-id) — Connection error on dispatch task did not clear the batch_id
**Publish ref:** `origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error`

Close the live job-artifacts dispatch gap where `draft_job_resume` logged provider `Connection error.` / `do_task(...) provider call failed` and the job row kept a populated `batch_id` after the run. Reuse AST-1191’s hop-failure helper (no parallel release design): durable claim clear + configured error/hold + honest debug `batch_released`. Does not own provider retry or hop-topology redesign.

## Survey findings (baked into this plan — builder does not re-decide)

On tip after `sync-child` (AST-1191 already on `origin/dev`):

| Location | Finding | Action this ticket |
|----------|---------|-------------------|
| `src/core/agent.py` `_apply_dispatch_chain_hop_failure` | Early `return dict(_HOP_FAILURE_NOOP)` when `_should_write_dispatch_hop_label` is false skips **both** error_state **and** `release_job_dispatch_claim`, even when `provider_failed=True` and `index` is set | **Fix:** release the job claim on provider failure before / outside that gate; keep error_state / hop-label side effects gated |
| Same helper, `provider_failed and index` arm | Claim release only runs after the hop-label gate — defeats AST-1191 “defense in depth for `do_task` callers outside consult” when ctx is not graduation-eligible | Same fix |
| `src/core/consult.py` `_run_dispatch_chain_job_batch` | Still calls `release_job_dispatch_claim` on `not result.get("success")` — dual clear remains idempotent via `clear_job_batch_lock` | **Do not remove**; leave as second belt |
| `src/core/dispatcher.py` `_run_unified` `finally` | `clear_job_batch(bid)` still clears by claim `batch_id` | **Do not change** |
| `src/external/deepseek.py` | Connection failures already return `success=False` + non-empty `error` (matches live ERROR line) | **Out of scope** — consume structured failure only |
| AST-1191 tests (`TestAst1191ArtifactHopFailureRelease`) | Cover `anticipate_scan` + timeout/empty; do not assert ungated release when hop-label write is false | Betty extends coverage after Code Complete — engineer does not edit `tests/` |

⚠️ **Decision — root cause:** The orphaned lock is not a missing DeepSeek adapter path. The live `do_task(draft_job_resume) provider call failed … error=Connection error.` line means the structured `success=False` arm ran and called `_close_hop_ledger(..., provider_failed=True)`. `_apply_dispatch_chain_hop_failure` still no-ops the entire side-effect block (including release) when `_should_write_dispatch_hop_label` is false. That makes AST-1191’s per-`do_task` release conditional on hop-label eligibility instead of on “rows were claimed + provider failed.” Outer consult/dispatcher clears are necessary but not sufficient as the sole belt for every `do_task` caller / mid-chain hop. Fix release duty inside the existing helper — do not invent a second release module.

⚠️ **Decision — wrong fix rejected:** Swallowing / retrying Connection errors, clearing only in `dispatcher.finally`, or adding a draft_job_resume-only special case would leave the same gate for other artifact hops and would not restore claim-process-release at the failure site AST-1191 already owns.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | In `_apply_dispatch_chain_hop_failure`: always `release_job_dispatch_claim` for job + `provider_failed` + non-empty `index` even when hop-label write is false; keep error_state / hard-string / balance-hold logic behind the existing hop-label gate; avoid double-release in the gated arm; keep provider-failure found/recorded consuming `batch_released` from the outcome dict | core |

No `src/external/**`, no `src/data/**`, no `src/utils/config.py`, no consult/dispatcher edits, no `tests/` / bible (Betty).

## Stage 1: Ungate claim release on provider hop failure

**Done when:** For a job `do_task` whose provider returns `success=False`, `_apply_dispatch_chain_hop_failure(..., provider_failed=True, index=<astral_job_id>)` calls `tracker.release_job_dispatch_claim(index)` and returns `batch_released=True` whether or not `_should_write_dispatch_hop_label` is true. When hop-label write **is** true, behavior matches AST-1191 for error_state / balance hold (transition then release; balance refusal holds state, still releases). Dual clear with consult remains idempotent. Existing `do_task(...) provider call failed batch_id=… error=…` ERROR line is unchanged.

1. In `src/core/agent.py`, rewrite `_apply_dispatch_chain_hop_failure` so claim release is **not** swallowed by the `_should_write_dispatch_hop_label` early-return. Use **two branches** (preserve AST-1191 transition-then-release on the gated path so `state_history` still stamps the in-flight `batch_id`):

   **Branch A — hop-label write false** (`_should_write_dispatch_hop_label` is false):
   - If `provider_failed and index and entity_type == "job"`: call `tracker.release_job_dispatch_claim(index)`; `batch_released = True`.
   - Else: `batch_released = False`.
   - No error_state transition.
   - If `debug`: emit the existing `chain_hop_failed apply_error_state=… batch_released=…` detail line (same format as today).
   - `return {"apply_error_state": False, "error_state": "", "batch_released": batch_released}`.

   **Branch B — hop-label write true** (dispatch-chain job hop):
   - Keep today’s `err_state` / `balance_hold` / `hard` computation and `transition_job_state` try/except unchanged.
   - **After** the transition attempt: if `provider_failed and index`: `release_job_dispatch_claim(index)`; `batch_released = True` (same as AST-1191; `entity_type` is already job when this branch runs).
   - Debug detail + return dict unchanged from AST-1191 (`error_state` only when `apply_error_state`).

   Late-import `from src.core import tracker as tracker_mod` once at the top of the function (both branches). Do not call release twice on Branch B.

2. Do **not** change `_close_hop_ledger` kwargs or the provider-failure call site that passes `provider_failed=True` / `failure_class=…` (AST-1191 wiring stays).
3. Do **not** change `_HOP_FAILURE_NOOP` constant meaning for non-failure exits; success-path and non-`failure_error` closes still return that constant via `_close_hop_ledger`.
4. Do **not** edit `consult.py` or `dispatcher.py` in this stage — their clears stay as the outer belt.

⚠️ **Decision:** Release runs for `entity_type == "job"` only (this epic’s repro and Boundaries). Candidate/company claim parity is out of scope (AST-1257 family / parent Boundaries).

⚠️ **Decision:** Branch A releases without error_state (no hop-label eligibility → no configured chain error write). Branch B keeps transition-then-release. Outer consult + dispatcher clears remain idempotent.

## Stage 2: Connection-error draft hop — debug trail unchanged

**Done when:** The existing provider-failure block in `do_task` (ERROR log + `_close_hop_ledger(..., provider_failed=True)` + debug found/recorded with `batch_released=true|false`) still compiles and types cleanly after Stage 1; no new debug-contract lines when `debug=False`; no DeepSeek/adapter edits. A manual or existing-component check that monkeypatches `send_to_deepseek` to return `success=False, error="Connection error."` for `draft_job_resume` with BUILD_ARTIFACTS dispatch ctx shows `release_job_dispatch_claim` called and, when hop-label write applies, `ERROR_BUILD_ARTIFACTS` transition.

1. Do **not** add new found/recorded strings. Keep AST-1191’s `found duration=…` / `recorded error=… error_state=… batch_released=…` lines; they already read the outcome dict.
2. Do **not** special-case the substring `"Connection error"` — any `provider_failed=True` path must release (timeout, empty response, Connection error, etc.).
3. Compile / lint the touched file (`src/core/agent.py`) before commit.
4. Engineer does **not** edit `tests/` or `docs/test-bible/**`. Note for Betty (comment optional at Code Complete only if needed): extend `TestAst1191ArtifactHopFailureRelease` (or sibling) with (a) `draft_job_resume` + `error="Connection error."` + dispatch ctx → release + `ERROR_BUILD_ARTIFACTS`; (b) `provider_failed=True` with empty/`{}` ctx → `batch_released=True` and no error_state (ungated release).

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; push to `origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error`.
- Do not add files outside the Files Changed table.
- If `_apply_dispatch_chain_hop_failure` / `_close_hop_ledger` / provider-failure block shape has drifted from this plan, stop and comment on **AST-1280** with the Stage N blocked template.
- Deviation from this plan is escalation, not autonomy.

## Self-Assessment

**Scope:** `Single-Component` — one helper in `src/core/agent.py` (core); no data/external/UI.

**Conf:** `high` — root cause is the hop-label early return swallowing provider-failure release; fix reuses AST-1191’s helper and consult dual-clear pattern.

**Risk:** `Medium` — claim release sits on the hot provider-failure path for all job `do_task` calls; wrong breadth could clear a lock that should stay, but gating on `provider_failed + job index` matches claim-process-release and keeps balance-hold / error_state rules intact.

## Self-review vs ASTRAL_CODE_RULES

- §1.3 DRY — single helper owns release + error_state; no parallel draft_job_resume-only clear.
- §2.1 config — no new config keys; consumes existing `task_config["error_state"]`.
- §2.4 batch / claim-process-release — clear on provider-failure early exit when a job index was in play; outer `finally` clears unchanged.
- §2.6 state machine — core still decides `error_state` via existing hard/balance rules; data layer only clears lock / applies transition args.
- §3.3 imports — late `tracker` import inside helper preserved.
- §1.5.1 debug — found/recorded remain `debug=True` only; no new ungated debug lines.
