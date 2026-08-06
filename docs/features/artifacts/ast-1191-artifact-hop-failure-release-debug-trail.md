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

**Done when:** On a dispatch-chain job hop (`ctx.dispatch_trigger_state` set, graduation target exists) whose provider call returns `success=False`, the job (1) transitions to `task_config["error_state"]` when that state is configured (for artifact hops: `ERROR_BUILD_ARTIFACTS`), (2) has its `batch_id` lock cleared, and (3) still emits the existing `do_task(...) provider call failed batch_id=… error=…` ERROR line with the non-empty error from AST-1190. Provider balance refusal (`failure_class=provider_balance_refusal`) still **holds** state (no error_state transition) but **does** release the claim. Non-provider hop failures keep today’s hard-string gate (`Job not found` / `Missing candidate_data` only). Both `_apply_dispatch_chain_hop_failure` and `_close_hop_ledger` return the outcome dict `{"apply_error_state": bool, "error_state": str, "batch_released": bool}` from **every** exit — including `_close_hop_ledger`’s `hop_ledger_closed or not hop_ledger_batch_id` path (never bare `return` / `None`). Stage 2 consumes that dict — no signature rewrite later.

1. In `src/core/agent.py`, add a module-level no-op outcome constant (near the hop-failure helper) and extend `_apply_dispatch_chain_hop_failure` to return that outcome dict from **every** exit:

```python
_HOP_FAILURE_NOOP = {
    "apply_error_state": False,
    "error_state": "",
    "batch_released": False,
}

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
) -> Dict[str, Any]:
```

2. When `_should_write_dispatch_hop_label(...)` is false (not a dispatch-chain job hop — no state/claim side effects): `return dict(_HOP_FAILURE_NOOP)`.

3. Replace the hard-fail gate so error_state applies when `err_state` is non-empty **and** any of:
   - existing hard strings: `"Job not found" in error` or `"Missing candidate_data" in error`
   - `provider_failed is True` **and** not balance refusal — call the existing `is_provider_balance_refusal({"failure_class": failure_class})` already imported in this module

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
apply_error_state = False
batch_released = False
```

4. When `hard and err_state and index`:
   - `tracker_mod.transition_job_state([index], err_state)` inside the existing `try/except ValueError` (warning log unchanged).
   - On successful transition (no `ValueError`): set `apply_error_state = True`.
   - **Order:** transition **before** claim release so `state_history[].batch_id` still captures the in-flight claim (`transition_job_state` reads `job.get("batch_id")`).

5. When `provider_failed and index` (including balance_hold): call `tracker_mod.release_job_dispatch_claim(index)` after the transition attempt (or immediately when not hard); set `batch_released = True`. Idempotent with `_run_dispatch_chain_job_batch`’s existing `release_job_dispatch_claim` on `!success` — leave that consult release in place; do not remove it.

6. Before returning, when `debug=True`, emit (replace the current single `chain_hop_failed retryable=…` line):

```text
chain_hop_failed apply_error_state=<bool> error_state=<err_state or ''> batch_released=<bool> failure_class=<…> error=<…>
```

   Then always:

```python
return {
    "apply_error_state": apply_error_state,
    "error_state": err_state if apply_error_state else "",
    "batch_released": batch_released,
}
```

7. Update `_close_hop_ledger` to accept the new kwargs **and return the same outcome dict**:

```python
def _close_hop_ledger(
    *,
    success: bool,
    clear_log: bool = False,
    failure_error: Optional[str] = None,
    provider_failed: bool = False,
    failure_class: Optional[str] = None,
) -> Dict[str, Any]:
```

   - Replace the body so **every** exit returns a dict (including the existing early exit). Concrete body:

```python
nonlocal hop_ledger_closed
if not success and failure_error:
    outcome = _apply_dispatch_chain_hop_failure(
        entity_type=entity_type or "",
        index=index,
        ctx=ctx,
        task_config=task_config,
        error=failure_error,
        debug=debug,
        provider_failed=provider_failed,
        failure_class=failure_class,
    )
else:
    outcome = dict(_HOP_FAILURE_NOOP)
# Existing early exit — MUST return outcome, not bare `return` / None
# (hop_ledger_batch_id is None for non-chain calls and chain hops without candidate_id).
if hop_ledger_closed or not hop_ledger_batch_id:
    return outcome
_finalize_run_next_hop_ledger(
    hop_ledger_batch_id, success=success, batch_size=batch_size
)
hop_ledger_closed = True
if clear_log:
    log_batch_id.set(None)
return outcome
```

   - Other call sites that ignore the return value stay valid (Python allows discarding returns).
   - **Do not** leave the bare `return` at today’s `agent.py` early-exit line — that is the round=2 crash: Stage 2 would subscript `None`, abort `do_task`, and skip consult’s claim release (AC3 regress under `debug=True`).

8. On the existing provider-failure return path in `do_task` (the block after `send_to_*` where `batch_id and not result.get("success")` already normalizes `error`, and the later `if not result.get("success"):` that calls `_close_hop_ledger`):

   - Change the `_close_hop_ledger` call to capture the outcome (Stage 2 recorded line uses it):

```python
hop_fail_outcome = _close_hop_ledger(
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

⚠️ **Decision:** Apply configured `error_state` for **all** non-balance provider failures on dispatch-chain hops (timeout, empty response, max_tokens, generic provider error), not only AST-1189/1190 classes — AC3 names “such a failure” after the provider path; balance refusal keeps the existing hold semantics used elsewhere in consult.  
⚠️ **Decision:** Claim release lives in `_apply_dispatch_chain_hop_failure` (defense in depth for `do_task` callers outside `_run_dispatch_chain_job_batch`) **and** remains in that consult batch runner — dual clear is idempotent via `clear_job_batch_lock` (Joan #3: recorded, not accidental).  
⚠️ **Decision:** No consult.py / dispatcher.py edits — topology and claim/get/clear finally block stay as-is (`astral.dispatch.run-next-is-chain-authority`).  
⚠️ **Decision:** Outcome-dict return lands in Stage 1 for both helpers so Stage 2 does not amend signatures (`orch.pipeline.plan-is-bible`). `_close_hop_ledger` returns `outcome` from **every** exit (including no-ledger early return) — same discipline as `_HOP_FAILURE_NOOP` on `_apply_dispatch_chain_hop_failure`.

---

## Stage 2: Debug found/recorded trail on provider failure

**Done when:** With `debug=True`, a provider-failed `do_task` on an artifact hop emits Style D index detail under the existing hop/provider-failed path with **found** (duration, stop, token counts from real timesheet keys, failure_class) and **recorded** (non-empty error string, error_state applied or held, batch_released) lines. With `debug=False`, no new contract lines. No changes to external `send_to_*` beyond consuming fields already on `result`. Silent `tokens_*=0` fallbacks are forbidden when keys are missing.

1. In the same `if not result.get("success"):` provider-failure block in `do_task`, **after** `_store_response_block` (best-effort), when `debug` is True:

   - Read timesheet: `ts = result.get("timesheet") if isinstance(result.get("timesheet"), dict) else {}`
   - Duration: if `ts.get("duration")` is `int` or `float`, format `duration={float(ts["duration"]):.1f}s`; else `duration=n/a`.
   - Stop: `api = result.get("api_response")`; `stop = getattr(api, "stop_reason", None) if api is not None else None`; display `stop` if it is a non-empty string after strip, else `"?"`.
   - Tokens — use the **actual** external timesheet keys (both DeepSeek and Anthropic): `inputtotal`, `inputcached`, `outputtotal`, `cache_creation_tokens`. Helper for display (inline or small local lambda is fine):

```python
def _ts_num(key: str) -> str:
    v = ts.get(key)
    return str(int(v)) if isinstance(v, (int, float)) else "n/a"
```

     Do **not** invent `input_tokens` / `output_tokens`. Do **not** default missing keys to `0` — missing → `n/a` (timeout `_empty_timesheet` still supplies real zeros as ints, which print as `0` honestly).
   - `fc = result.get("failure_class")`; display `str(fc)` if non-empty after strip, else `n/a`.
   - Emit **found** line before `_close_hop_ledger`, matching `emit_llm_call_debug` vocabulary (`llm_external.py` token line: fresh / cache_read / cache_write / output):

```text
found duration=<…> stop=<…> tokens fresh=<inputtotal> cache_read=<inputcached> cache_write=<cache_creation_tokens> output=<outputtotal> failure_class=<…>
```

2. Call `_close_hop_ledger` as in Stage 1 step 8, then normalize before any subscript (belt-and-braces if Stage 1’s every-exit return is missed):

```python
hop_fail_outcome = _close_hop_ledger(...)  # same kwargs as Stage 1 step 8
hop_fail_outcome = hop_fail_outcome or _HOP_FAILURE_NOOP
```

   Then when `debug` is True, emit **recorded** from the normalized dict:

```text
recorded error=<non-empty error> error_state=<applied state or 'held'> batch_released=<true|false>
```

   - `error_state` display: `hop_fail_outcome["error_state"]` when `hop_fail_outcome["apply_error_state"]` else `'held'`.
   - `batch_released`: lowercase `true` / `false` from the bool.

3. Keep the existing debug_detail lines (`exit provider_failed…`, balance/empty class lines from AST-1190). Add found/recorded; do not delete sibling lines.

4. Do **not** edit `emit_llm_call_debug` in `llm_external.py` or either external client — ticket boundary is consume structured failures in core.

⚠️ **Decision:** Found/recorded lives in `do_task` (core), not a second pass through external debug helpers — honors “does not redesign LLM adapters” and still satisfies §1.5.1 (gated, `debug_detail`, found + recorded).  
⚠️ **Decision:** Token field names and `n/a`-not-silent-zero match Joan round=1 fix-now — operators see the same fresh/cache_read/cache_write/output vocabulary as `emit_llm_call_debug`, and max_tokens / hollow paths keep real counts.

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

---

## Revisions

Revision 1 — 2026-08-05  
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE) — Stage 2 timesheet keys wrong (`input_tokens`/`output_tokens` never emitted; silent `0` fallback reprints the parent symptom); Stage 1 `_close_hop_ledger` → `None` vs Stage 2 return-dict threading contradiction.  
Changes:
- Stage 1: both helpers return `{"apply_error_state", "error_state", "batch_released"}` from the start (including early no-op); Done-when + Decision document that Stage 2 does not amend signatures; dual claim-release recorded as intentional defense-in-depth.
- Stage 2: read real keys `inputtotal` / `inputcached` / `outputtotal` / `cache_creation_tokens`; missing → `n/a` (never silent `0`); found line mirrors `emit_llm_call_debug` token vocabulary (`fresh` / `cache_read` / `cache_write` / `output`); recorded line consumes Stage 1 `hop_fail_outcome`.

Revision 2 — 2026-08-06  
Driven by: Joan `[plan-discuss] round=2 concern` (plan-rubric.v1 REVISE) — Stage 1 step 7 left `_close_hop_ledger`’s existing `if hop_ledger_closed or not hop_ledger_batch_id: return` as a bare `return` (`None`); Stage 2 subscripted that unconditionally → `TypeError` under `debug=True`, skipping consult claim release (AC3 regress).  
Changes:
- Stage 1 step 7: full concrete body; early no-ledger exit `return outcome` (never bare `return`); Decision restates every-exit return discipline for `_close_hop_ledger`.
- Stage 2 step 2: `hop_fail_outcome = hop_fail_outcome or _HOP_FAILURE_NOOP` before any key access.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug`  
**Tip:** `3aa816f3`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `7f5b132e` | hop failure → `ERROR_BUILD_ARTIFACTS` + claim release; outcome dict every exit |
| 2 | `3aa816f3` | found/recorded duration/stop/tokens/failure_class on provider fail |

---

## Radia review — code-rubric.v1 revision=1

**Publish ref tip:** `5c6cdcda`

**Overall:** CLEAN

### Plan adherence

Isolated this ticket's own contribution via `git diff ee5e760f..5c6cdcda` (the tip AST-1189 left for merge-child) rather than the full three-dot `origin/dev` diff, since the latter also carries already-reviewed AST-1189/AST-1190 product code stacked via `ftr`. AST-1191's own footprint is exactly `src/core/agent.py` (105 lines) + its plan doc + test-bible + tests — matching the Files Changed table with no scope creep. Both Joan revision rounds are honored: `_apply_dispatch_chain_hop_failure` and `_close_hop_ledger` return the outcome dict from **every** exit (including the no-op / no-ledger early returns — no bare `return None` regression), balance-refusal still holds state while releasing the claim, transition happens before release (state_history still stamps the in-flight `batch_id`), and Stage 2's found/recorded lines read the real timesheet keys (`inputtotal`/`inputcached`/`outputtotal`/`cache_creation_tokens`) with honest `n/a` on missing keys — no silent-zero regression of the parent symptom.

Verified `clear_job_batch_lock` (`src/data/database.py`) is a plain `UPDATE ... SET batch_id = NULL` — confirms the plan's "dual clear is idempotent" claim for the intentional double release (`_apply_dispatch_chain_hop_failure` + the existing consult batch runner clear).

Ran the ticket's own test class plus the adjacent `TestAst848DispatchChainDoTask` regression test in a fresh venv: **11/11 pass**. The broader touched-file test run surfaces ~30 pre-existing failures (statute-count fixture drift, shared sqlite db schema state, and unrelated in-flight epics AST-901/1054/1060/1127/1195 whose product code isn't on this branch) — none in `TestAst1191*` or `TestAst848*`, confirmed against an `origin/dev` baseline showing the same classes of failure already present. Not diff-caused.

### Findings

None (fix-now / discuss). No repeat of AST-1189's cross-ticket merge-tests contamination — this branch's `merge-tests(AST-1191)` diff is a clean, isolated 2-file/240-line addition (own test-bible + test file only).

### Pattern conformance

None cited (plan lists statute ids under In-scope / Considered-but-excluded, covered by the full-set sweep).

### Frame diff

(none) — diff matches the plan's Files Changed table exactly; no unplanned adds.

### What's solid

- `_apply_dispatch_chain_hop_failure` / `_close_hop_ledger` outcome-dict threading is correct on every exit path (verified against both Joan revision concerns).
- Debug found/recorded gating is correct — `found` sits inside the existing `if debug:` block, `recorded` is gated separately after `_close_hop_ledger`, and `debug=False` emits neither (test-covered).
- `astral.batch.claim-process-release`, `astral.state.core-decides-transitions`, `astral.state.job-prior-states-enforced` all conform — transition-then-release ordering, `ValueError` enforcement preserved via existing try/except, core (not data) decides `err_state`.

`context_tokens≈52000`
— Radia
