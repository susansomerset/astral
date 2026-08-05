# AST-1190: Empty / unusable provider response surfacing (anticipate_scan jobs failing)

**Linear:** [AST-1190](https://linear.app/astralcareermatch/issue/AST-1190/empty-unusable-provider-response-surfacing-anticipate-scan-jobs)
**Parent:** [AST-1164](https://linear.app/astralcareermatch/issue/AST-1164/anticipate-scan-jobs-failing)
**Publish ref:** `origin/sub/AST-1164/AST-1190-empty-unusable-provider-response`

When a provider call ends with a hollow outcome (`stop=?`, zero in/out tokens, no usable content) — or when the failure path carries a blank `error` string (the observed `TimeoutError` / empty `str(e)` shape that logged a healthy LLM summary then `provider call failed … error=`) — `do_task` must return `success=False` with a **non-empty** error and must not emit a healthy-looking `LLM … stop=? tokens in=0 out=0` INFO line for that outcome. Timeout **budget** and timeout-specific `failure_class` remain Ada’s AST-1189; this ticket owns hollow-response classification + blank-error surfacing on the shared DeepSeek/Anthropic path.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `PROVIDER_EMPTY_RESPONSE` block (`failure_class` + canonical error string) | utils |
| `src/utils/llm_external.py` | Add hollow-response predicate + `is_provider_empty_response`; shared non-empty error normalize helper | utils |
| `src/utils/logging.py` | `log_llm_batch_summary`: never treat a provided empty/whitespace `error` as a healthy response summary | utils |
| `src/external/deepseek.py` | Detect hollow response before healthy INFO summary; normalize blank exception errors; tag `failure_class` | external |
| `src/external/anthropic.py` | Mirror DeepSeek hollow + blank-error handling | external |
| `src/core/agent.py` | Guarantee non-empty `error=` on `provider call failed` log / return; debug detail when empty-response tagged | core |

## Execution contract

The plan is binding. Execute stages in order. Do not add files outside the table. Do not change per-call time budget / `asyncio.wait_for` timeout values (AST-1189). On ambiguity or codebase drift, stop and comment on **AST-1164** with the 🛑 Stage format from plan-child.

**Sibling vocabulary (coordinate, do not own):**

| Class | Owner | Meaning |
|-------|-------|---------|
| `provider_call_timeout` | AST-1189 (Ada) — published plan | Over per-call budget (`PROVIDER_CALL_BUDGET`) |
| `provider_empty_response` | AST-1190 (this plan) | Hollow / unusable response + blank-error / fake-healthy-summary surfacing |
| `provider_balance_refusal` | shipped (AST-897) | Billing/credit refusal |
| `max_tokens` | shipped (AST-903) | JSON truncated at max_tokens |

Do not rename Ada’s `provider_call_timeout`. Overlap note: AST-1189 already normalizes blank `TimeoutError` on the timeout path; this ticket still owns (1) hollow-response fail-closed before a healthy LLM INFO line, (2) `log_llm_batch_summary` never treating `error=""` as healthy, (3) `do_task` non-empty `error=` coerce for any remaining blank provider failure.

---

## Stage 1: Config + shared helpers + summary logging

**Done when:** `PROVIDER_EMPTY_RESPONSE` is readable from config; `llm_external` exposes hollow detection + result predicate + blank-error normalize; `log_llm_batch_summary(..., error="")` emits an ERROR line (never the healthy `stop=? tokens in=0 out=0` INFO shape).

1. In `src/utils/config.py`, immediately after the existing `PROVIDER_BALANCE_REFUSAL` block, add:

```python
# PROVIDER_EMPTY_RESPONSE — hollow / unusable LLM response (AST-1190).
# Used by utils.llm_external classifiers and external send_to_* failure returns.
PROVIDER_EMPTY_RESPONSE = {
    "failure_class": "provider_empty_response",
    "error": (
        "Provider returned unusable response "
        "(missing stop reason, zero tokens, no content)"
    ),
}
```

Update the file header inventory comment to mention `PROVIDER_EMPTY_RESPONSE` next to the `PROVIDER_BALANCE_REFUSAL` line.

⚠️ **Decision:** Canonical error text and `failure_class` live in config (§1.4 / §2.1), matching `PROVIDER_BALANCE_REFUSAL`. Do not invent additional hollowness knobs (thresholds, retries, token floors beyond the AC’s zero-token conjunction).

2. In `src/utils/llm_external.py`, import `PROVIDER_EMPTY_RESPONSE` from config (alongside `PROVIDER_BALANCE_REFUSAL`) and add:

- `normalize_provider_error(exc_or_msg: Any, *, fallback: Optional[str] = None) -> str`  
  - If `exc_or_msg` is a `BaseException`, start from `str(exc_or_msg)`; else coerce with `str(exc_or_msg)` (treat `None` as `""`).  
  - If the stripped string is non-empty, return that stripped string.  
  - Else return `fallback` if provided and non-empty after strip; else return `f"{type(exc_or_msg).__name__}: provider call failed with empty error detail"` when `exc_or_msg` is a `BaseException`; else return `"provider call failed with empty error detail"`.  
  - **Do not** set or infer `failure_class` here — this helper only guarantees a non-empty error string.

- `is_unusable_provider_response(response: Any, *, input_tokens: int, output_tokens: int) -> bool`  
  - `stop = getattr(response, "stop_reason", None)`  
  - `stop_missing = stop is None or (isinstance(stop, str) and stop.strip() in ("", "?"))`  
  - `zero_tokens = int(input_tokens or 0) == 0 and int(output_tokens or 0) == 0`  
  - Usable content: try `extract_api_response_text(response)`; `no_content = True` on `ValueError`, or when the returned string is empty/whitespace.  
  - Return `True` only when **all three** are true: `stop_missing` and `zero_tokens` and `no_content` (parent AC2 / this ticket AC2).  
  - Do **not** treat a normal `end_turn` (or other non-empty stop) with positive tokens as unusable even if parse later fails — that stays on existing parse-failure paths.

- `is_provider_empty_response(result: Optional[Dict[str, Any]]) -> bool`  
  - `True` iff `result` is a dict and `result.get("failure_class") == PROVIDER_EMPTY_RESPONSE["failure_class"]`.

⚠️ **Decision:** Shared helpers stay in `llm_external.py` (AST-687 / AST-897 pattern) — one predicate for both providers; no new module; no cross-import between `anthropic.py` and `deepseek.py`.

3. In `src/utils/logging.py`, change `log_llm_batch_summary` so a **provided** `error` argument (including `""` / whitespace-only) never falls through to the healthy INFO summary:

- Keep the signature `error: Optional[str] = None`.  
- Branch: `if error is not None:` → ERROR path. Display `error` if `str(error).strip()` else `"(empty error)"`.  
- Only when `error is None` (caller omitted failure) use the healthy `response=` INFO path (`stop` / token counts).

⚠️ **Decision:** Use `error is not None` (not truthiness). The live bug is `str(TimeoutError()) == ""` passed as `error=` — falsy today, so the function logs a fake healthy summary. Fixing truthiness here is blank-error **surfacing** (this ticket), not timeout budget (AST-1189).

---

## Stage 2: External — hollow response fail-closed + blank exception errors (DeepSeek + Anthropic)

**Done when:** Both `send_to_deepseek` and `send_to_anthropic`, on a returned API object that matches the AC2 hollow shape, return `success=False` with `PROVIDER_EMPTY_RESPONSE["error"]` and `failure_class=provider_empty_response`, and log that outcome via `log_llm_batch_summary(..., error=...)` **instead of** the healthy INFO summary. Exception paths never return a blank `error` string. Healthy responses with a real stop reason and non-zero tokens still return `success=True` when parsing succeeds (AC5).

Apply the same structural edits in **both** `src/external/deepseek.py` and `src/external/anthropic.py` (keep the existing mirror; do not refactor the two files into one).

1. Imports (top-level): from `src.utils.llm_external` also import `is_unusable_provider_response`, `normalize_provider_error`, and keep existing `classify_provider_balance_refusal` / `extract_api_response_text` / `emit_llm_call_debug`. From `src.utils.config` import `PROVIDER_EMPTY_RESPONSE` (or read it only via helpers — prefer importing the dict for the error string + failure_class on the return, same style as literal `"max_tokens"` today; if the file does not already import config, import `PROVIDER_EMPTY_RESPONSE` only — do not pull unrelated config).

2. **Hollow gate — place after token counts are computed from `response.usage` and BEFORE the healthy `log_llm_batch_summary(..., response=response)` call** (today that healthy log is immediately after usage extraction in both files).

   For DeepSeek, use the already-computed `input_total` / `output_total` from `deepseek_usage_to_token_counts` **plus** cache/read components already folded into those variables as the file does today for the summary — specifically pass the same integers the healthy summary would expose as in/out. Concrete: call  
   `is_unusable_provider_response(response, input_tokens=input_total + input_cached, output_tokens=output_total)`  
   so “zero in/out tokens” matches the log line’s `tokens in=` / `out=` sense (in = fresh+cached for DeepSeek counts already split; if `input_total` is cache_miss only, **sum** `input_total + input_cached` for the in-token side so a response that only had cached prompt tokens is not falsely hollow).  
   For Anthropic, pass `input_tokens=input_total` and `output_tokens=output_total` as those variables are already defined for the summary.

   When `is_unusable_provider_response(...)` is True:

   - `err = PROVIDER_EMPTY_RESPONSE["error"]`  
   - `log_llm_batch_summary(logger, <provider>, prompt_label, duration, error=err)`  
   - If `debug`: `emit_llm_call_debug(..., stop_reason=getattr(response, "stop_reason", None) or "?", ..., error=err, ...)` (same token fields as the success debug path).  
   - Build `timesheet` the same way as the success path immediately below (calltime/duration/token fields already available).  
   - If timesheet kwargs / `record_timesheet` are available at this point in the file: record `agent_performance="failure"` with `failure_note=err` (same try/except swallow as max_tokens). If timesheet kwargs are only built later in the current file order, **move** the hollow check to immediately after `_timesheet_kwargs` / `timesheet` are built and **still before** any path that returns `success=True` — but **do not** leave the healthy `log_llm_batch_summary(..., response=response)` above the hollow check. Preferred order: compute usage → build timesheet + timesheet kwargs (existing try) → hollow check (ERROR summary + failure return) → else healthy summary → max_tokens / parse / success.  
   - Return:

```python
{
    "success": False,
    "api_response": response,
    "parsed_response": None,
    "timesheet": timesheet,
    "error": err,
    "failure_class": PROVIDER_EMPTY_RESPONSE["failure_class"],
}
```

⚠️ **Decision:** Fail at the external boundary before a healthy INFO summary (coat-check / never treat empty as success). Do not wait for `do_task` to notice — by then the misleading LLM INFO line is already in app_log.

3. **Exception paths** (both inner and outer `except Exception as e` returns that today set `"error": str(e)`):

   - Set `err = normalize_provider_error(e)`.  
   - Pass `error=err` into `log_llm_batch_summary` and into the returned dict.  
   - Keep existing `classify_provider_balance_refusal(e)` tagging unchanged.  
   - **Do not** set `failure_class` to `provider_empty_response` on generic exceptions (including `TimeoutError` / `asyncio.TimeoutError`). Ada’s AST-1189 owns timeout class + budget message; this normalize only prevents blank `error=`. If Ada’s merge later sets `failure_class=provider_timeout` and a non-empty timeout error on the same path, leave that logic intact — only ensure that when this ticket’s normalize runs, it does not overwrite a non-empty error Ada already assigned (normalize is applied to the exception, then Ada’s timeout branch if present takes precedence when both land on ftr; if only this ticket has landed, blank `TimeoutError` becomes a non-empty type-based message without claiming timeout class).

4. Parse-failure returns that already use `error=str(parse_err)`: run `normalize_provider_error(parse_err)` so a pathological empty parse message cannot blank-out either. Do **not** add `failure_class=provider_empty_response` on ordinary parse failures.

---

## Stage 3: `do_task` — non-empty `provider call failed` surfacing + debug

**Done when:** For any provider result with `success` falsy, the `do_task(...) provider call failed … error=` log line always shows a non-empty error string; the returned dict’s `error` is non-empty; when `debug=True` and `is_provider_empty_response(result)`, a debug_detail line names the failure_class. Healthy provider success path unchanged (AC5).

1. In `src/core/agent.py`, import `is_provider_empty_response` and `normalize_provider_error` from `src.utils.llm_external` (extend the existing `llm_external` import that already pulls `extract_api_response_text` / `is_provider_balance_refusal`).

2. Immediately after the provider returns (`result = await send_to_*`) and `result["runtime_prompt"] = runtime_prompt`, when `batch_id and not result.get("success")`:

   - `err = normalize_provider_error(result.get("error"), fallback=result.get("failure_class"))`  
   - If `result.get("error")` is missing/blank, set `result["error"] = err` so callers and the return value stay non-empty.  
   - Log with that `err`:

```python
logger.error(
    "do_task(%s) provider call failed batch_id=%s error=%s",
    task_key,
    batch_id,
    err,
)
```

3. On the existing `if not result.get("success"):` block where balance-refusal debug detail already lives, add a parallel `debug=True` detail when `is_provider_empty_response(result)`:

```text
provider_empty_response failure_class=<…> error=<…>
```

Do not add state transitions, batch release, or hop topology changes (AST-1191 / Katherine).

⚠️ **Decision:** Core coerces blank errors at the log/return boundary as defense in depth; external remains the primary classifier. No new exception types.

---

## Self-Assessment

**Scope:** `Single-Component` — shared LLM utils + both external send paths + the existing `do_task` provider-failure log/return; no dispatch, batch release, or UI.

**Conf:** `high` — same envelope as AST-897 / AST-903 (`success=False` + `failure_class` + non-empty `error`); the blank-`TimeoutError` → fake healthy summary path is reproducible from `log_llm_batch_summary` truthiness.

**Risk:** `Medium` — wrong hollowness predicate could fail closed on an edge response shape, but the AC conjunction (missing stop **and** zero tokens **and** no content) is narrow; healthy AC5 path stays on existing success return.

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** One hollow predicate + normalize helper in `llm_external`; both providers call it (mirror edits, no cross-external import).  
- **§2.1 config:** `failure_class` + canonical error string in `PROVIDER_EMPTY_RESPONSE`; no inline magic sets.  
- **§2.2 / do-task-delegation:** Classification at external I/O boundary; core only coerces blank error for log/return + debug.  
- **§1.5 logging:** Summary + `do_task` ERROR via existing loggers; no new `logger.info("[DEBUG]")`; debug detail gated.  
- **§1.4:** No new hardcoded token budgets or timeout seconds (Ada).  
- **§2.4 / §2.6:** Untouched — Katherine owns release/hold.  
- **§3.3 imports:** utils ← config; external ← utils; core ← utils; no upward imports.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1164/AST-1190-empty-unusable-provider-response`
**Tip:** `597a41d9`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `c3a39ddf` | `PROVIDER_EMPTY_RESPONSE` + `llm_external` helpers; `log_llm_batch_summary` empty-`error` ERROR path |
| 2 | `968a3a7c` | DeepSeek/Anthropic hollow fail-closed + blank exception/parse normalize |
| 3 | `597a41d9` | `do_task` non-empty `error=` coerce + empty-response debug detail |

## Radia review — [code-rubric] revision=1

**Rubric:** code-rubric.v1
**Publish ref tip:** `0f4469e1`
**Overall:** DISCUSS

**Full-set sweep:** all `status: active` statutes scored in-session (universal + scoped). No `violates`. One `discuss` straggler below; everything else `conforms` or `not-applicable` (diff doesn't touch `src/ui/**`, `src/data/**`, `canon/statutes/**`, `artifacts/**`, `scripts/spikes/**`).

**What's solid**

- Hollow-response gate sits before the healthy `log_llm_batch_summary` call in both `send_to_anthropic` / `send_to_deepseek`, mirrored structurally, no cross-external import — matches Stage 2 order exactly (usage → timesheet kwargs → hollow check → healthy summary).
- `log_llm_batch_summary`'s `error is not None` branch (not truthiness) correctly fixes the blank-`TimeoutError` → fake-healthy-INFO bug this ticket exists to close.
- `PROVIDER_EMPTY_RESPONSE` config block mirrors `PROVIDER_BALANCE_REFUSAL` shape exactly (`astral.config.config-source-of-truth`); `do_task` coercion is defense-in-depth only, classification stays in external (`astral.agent.do-task-delegation`, `astral.layers.core-vs-external-bright-line`).
- Clean git separation confirmed: `code(AST-1190)` commits touch only `src/`; Betty's `test(AST-1190)` commit + `merge-tests(AST-1190)` touch only `tests/` + `docs/test-bible/`; no AST-1189 (timeout budget) or AST-1191 (hop release) scope smuggled — branch still runs the pre-AST-1189 `asyncio.wait_for` timeout mechanism, confirming isolation.
- Self-Assessment Scope/Conf/Risk still matches the diff's real footprint (shared utils + both externals + `do_task` only).

**discuss:** Commit `0f4469e1` (`test(AST-1190): import hollow-response helpers in provider clients`) touches only `src/external/anthropic.py` + `src/external/deepseek.py` — pure product-code import fix, not a test-tree change — but carries the `test(...)` vocabulary prefix instead of `code(...)` (`orch.git.commit-vocabulary`). Not fix-now: already pushed, and rewriting it would need rebase/force-push (banned by `orch.git.no-cherry-pick-rebase-force`). Flagging so future post-merge-tests fixups on this lineage use `code(...)`.

**Pattern conformance:** `astral.patterns.coat-check-never-store-empty` — conforms (this ticket is the positive instance: hollow provider payload is never treated as a stored success).

## Frame diff

(none — description accurately reflects the shipped diff; no scope drift from the `## Files Changed` table.)

context_tokens≈9

— Radia

## Resolution

**Date:** 2026-08-05  
**Review tip ingested:** `2311dbca` (`docs(AST-1190): Radia review — findings`)  
**Overall:** DISCUSS — **no fix-now**; Frame diff none.

| Item | Action |
|------|--------|
| discuss — `0f4469e1` used `test(AST-1190):` for a pure product import fixup | Accepted; no rewrite (rebase/force-push banned). Future post-merge-tests product fixups on this lineage use `code(...)`. No product change this pass. |

**§9a:** dry-run `origin/sub/AST-1164/AST-1190-empty-unusable-provider-response` → `origin/dev` (ftr parent not on origin yet — skipped).
