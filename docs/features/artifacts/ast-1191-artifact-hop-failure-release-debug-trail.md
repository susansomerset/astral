# Artifact hop failure release + debug trail (anticipate_scan jobs failing)

**Linear:** [AST-1191](https://linear.app/astralcareermatch/issue/AST-1191/artifact-hop-failure-release-debug-trail-anticipate-scan-jobs-failing)  
**Parent:** [AST-1164 — anticipate_scan jobs failing](https://linear.app/astralcareermatch/issue/AST-1164/anticipate-scan-jobs-failing)  
**Publish ref:** `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug`

After AST-1189 (timeout `failure_class`) and AST-1190 (hollow/blank-error surfacing): when a provider call fails on `anticipate_scan` or any shared resume-artifact dispatch-chain hop, the job must leave the batch claim, land on the configured artifact error/hold state (`TASK_CONFIG[*].error_state` → `ERROR_BUILD_ARTIFACTS`), keep the non-empty failure reason visible against that `batch_id` in app_log / Execution History, and — when `debug=True` — emit AST-538 found/recorded detail for duration, stop, tokens, and error/failure class. Does **not** redesign LLM adapters beyond consuming their structured `error` / `failure_class` / `timesheet` returns.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Expand `_apply_dispatch_chain_hop_failure` for provider failures (error_state + claim release); wire provider-failed `_close_hop_ledger` with `failure_class`; add debug found/recorded lines on that path | core |

**Not in scope:** `src/external/{deepseek,anthropic}.py` / timeout budget (AST-1189); hollow-response classification (AST-1190); `run_next` / BUILD_ARTIFACTS hop topology; AST-1163 name/ANALYSIS tokens; UI; `src/data/**`.

---

## Stage 1: Provider failure → error_state + batch claim release

**Done when:** On a dispatch-chain job hop (`ctx.dispatch_trigger_state` set, graduation target exists) whose provider call returns `success=False`, the job (1) transitions to `task_config["error_state"]` when that state is configured (for artifact hops: `ERROR_BUILD_ARTIFACTS`), (2) has its `batch_id` lock cleared, and (3) still emits the existing `do_task(...) provider call failed batch_id=… error=…` ERROR line with the non-empty error from AST-1190. Provider balance refusal (`failure_class=provider_balance_refusal`) still **holds** state (no error_state transition) but **does** release the claim. Non-provider hop failures keep today’s hard-string gate (`Job not found` / `Missing candidate_data` only).

1. In `src/core/agent.py`, extend `_apply_dispatch_chain_hop_failure` signature to:

```python
def _apply_dispatch_chain_hop_failure(
    *,
    entity_type: str,
    index: Optional[str],
    ctx: Optional[Dict[str, Any]],
    task_config: Dict[str, Any],
    error: str,
    debug: bool,
    provider_failed: bool = False,
    failure_class: Optional[str] = None,
) -> None:
```

2. Keep the existing early return when `_should_write_dispatch_hop_label(...)` is false (not a dispatch-chain job hop — no state/claim side effects).

3. Replace the hard-fail gate so error_state applies when `err_state` is non-empty **and** any of:
   - existing hard strings: `"Job not found" in error` or `"Missing candidate_data" in error`
   - `provider_failed is True` **and** `failure_class != PROVIDER_BALANCE_REFUSAL["failure_class"]` (import `PROVIDER_BALANCE_REFUSAL` from `src.utils.config`, or reuse `is_provider_balance_refusal` by building a one-key dict — prefer calling the existing `is_provider_balance_refusal({"failure_class": failure_class})` already imported in this module)

   Concrete:

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
```

4. When `hard and err_state and index`:
   - `tracker_mod.transition_job_state([index], err_state)` inside the existing `try/except ValueError` (warning log unchanged).
   - **Order:** transition **before** claim release so `state_history[].batch_id` still captures the in-flight claim (`transition_job_state` reads `job.get("batch_id")`).

5. When `provider_failed and index` (including balance_hold): call `tracker_mod.release_job_dispatch_claim(index)` after the transition attempt (or immediately when not hard). Idempotent with `_run_dispatch_chain_job_batch`’s existing `release_job_dispatch_claim` on `!success` — leave that consult release in place; do not remove it.

6. Update `_close_hop_ledger` to accept and forward:

```python
def _close_hop_ledger(
    *,
    success: bool,
    clear_log: bool = False,
    failure_error: Optional[str] = None,
    provider_failed: bool = False,
    failure_class: Optional[str] = None,
) -> None:
```

   Pass `provider_failed` / `failure_class` into `_apply_dispatch_chain_hop_failure` only when `not success and failure_error`.

7. On the existing provider-failure return path in `do_task` (the block after `send_to_*` where `batch_id and not result.get("success")` already normalizes `error`, and the later `if not result.get("success"):` that calls `_close_hop_ledger`):

   - Change the `_close_hop_ledger` call to:

```python
_close_hop_ledger(
    success=False,
    clear_log=True,
    failure_error=str(result.get("error") or "provider_failed"),
    provider_failed=True,
    failure_class=(
        str(result.get("failure_class")).strip()
        if result.get("failure_class") is not None
        else None
    ) or None,
)
```

   - Do **not** set `provider_failed=True` on other `_close_hop_ledger(success=False, …)` call sites (envelope / validation / decode failures keep the hard-string-only behavior).

8. Debug detail on this helper when `debug=True` (replace the current single `chain_hop_failed retryable=…` line):

```text
chain_hop_failed apply_error_state=<bool> error_state=<err_state or ''> batch_released=<bool> failure_class=<…> error=<…>
```

⚠️ **Decision:** Apply configured `error_state` for **all** non-balance provider failures on dispatch-chain hops (timeout, empty response, max_tokens, generic provider error), not only AST-1189/1190 classes — AC3 names “such a failure” after the provider path; balance refusal keeps the existing hold semantics used elsewhere in consult.  
⚠️ **Decision:** Claim release lives in `_apply_dispatch_chain_hop_failure` (defense in depth) **and** remains in `_run_dispatch_chain_job_batch` — dual clear is idempotent via `clear_job_batch_lock`.  
⚠️ **Decision:** No consult.py / dispatcher.py edits — topology and claim/get/clear finally block stay as-is (`astral.dispatch.run-next-is-chain-authority`).

---

## Stage 2: Debug found/recorded trail on provider failure

**Done when:** With `debug=True`, a provider-failed `do_task` on an artifact hop emits Style D index detail under the existing hop/provider-failed path with **found** (duration, stop, token counts, failure_class) and **recorded** (non-empty error string, error_state applied or held, batch_released) lines. With `debug=False`, no new contract lines. No changes to external `send_to_*` beyond consuming fields already on `result`.

1. In the same `if not result.get("success"):` provider-failure block in `do_task`, **after** `_store_response_block` (best-effort) and **before** `_close_hop_ledger`, when `debug` is True, emit found/recorded via `_do_task_debug_logger(debug)`:

   - Read timesheet: `ts = result.get("timesheet") if isinstance(result.get("timesheet"), dict) else {}`
   - `duration = ts.get("duration")` (format `duration={float:.1f}s` when numeric, else `duration=n/a`)
   - Stop: `api = result.get("api_response")`; `stop = getattr(api, "stop_reason", None) if api is not None else None`; display `stop` if non-empty else `"?"`
   - Tokens: prefer timesheet keys already used by externals (`input_tokens` / `output_tokens` / cache fields if present on `ts`); if absent, use `0`. Do not call the provider again.
   - `fc = result.get("failure_class")` (display `n/a` when missing)

   Found line (exact shape):

```text
found duration=<…> stop=<…> tokens_in=<int> tokens_out=<int> failure_class=<…>
```

   Recorded line **after** `_close_hop_ledger` returns (so it can reflect the actual apply/release outcome). To do that without probing the DB twice awkwardly: have Stage 1’s `_apply_dispatch_chain_hop_failure` return a small dict:

```python
{"apply_error_state": bool, "error_state": str, "batch_released": bool}
```

   (return `{"apply_error_state": False, "error_state": "", "batch_released": False}` on the early no-op return). Thread that return value through `_close_hop_ledger` → local variable on the provider-failure path only.

   Recorded line:

```text
recorded error=<non-empty error> error_state=<applied state or 'held'> batch_released=<true|false>
```

   Use `error_state='held'` when `apply_error_state` is False (balance hold or non-chain hop).

2. Keep the existing debug_detail lines (`exit provider_failed…`, balance/empty class lines from AST-1190). Add found/recorded; do not delete sibling lines.

3. Do **not** edit `emit_llm_call_debug` in `llm_external.py` or either external client — ticket boundary is consume structured failures in core.

⚠️ **Decision:** Found/recorded lives in `do_task` (core), not a second pass through external debug helpers — honors “does not redesign LLM adapters” and still satisfies §1.5.1 (gated, `debug_detail`, found + recorded).

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug`.
- Do not add files outside the Files Changed table.
- If `_apply_dispatch_chain_hop_failure` / `_close_hop_ledger` / provider-failure block shape has drifted, stop and comment on **AST-1164** with the Stage N blocked template.
- Healthy provider success path unchanged (parent AC5 — owned by siblings; this ticket must not regress graduation / hop labels).
- Do not change `run_next` membership, `DISPATCH_CHAIN_TERMINAL_GRADUATION`, or TASK_CONFIG `error_state` strings (already `ERROR_BUILD_ARTIFACTS`).

---

## Self-Assessment

**Scope:** `Single-Component` — `src/core/agent.py` dispatch-chain hop failure + debug only; consumes sibling `failure_class` / `error` / `timesheet` without touching externals.

**Conf:** `high` — the gap is localized: today’s `_apply_dispatch_chain_hop_failure` only hard-fails on two missing-entity strings, so provider failures leave jobs in `BUILD_ARTIFACTS` while consult only clears the claim; extending that helper + provider-path `_close_hop_ledger` kwargs is the direct fix.

**Risk:** `Medium` — wrong hard-fail breadth could send balance-refusal or non-provider validation failures to `ERROR_BUILD_ARTIFACTS`; mitigated by `provider_failed` flag only on the provider return path and explicit balance hold.

---

## Code rules check

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | One failure helper owns error_state + release; debug found/recorded once on the provider path |
| §1.5.1 debug-contract-gated | New found/recorded only when `debug=True`; `debug_detail` under existing hop context |
| §2.2 / do-task-delegation | Core consumes structured provider result; no adapter redesign |
| §2.4 claim-process-release | Transition then release; dual clear with consult is idempotent |
| §2.6 / run-next-is-chain-authority | No hop topology / graduation map edits |
| §3.3 imports | Core ← utils (`is_provider_balance_refusal` already present); no new upward imports |
| in-scope-only | No AST-1189 budget, AST-1190 hollow predicate, AST-1163 tokens, UI, data layer |
