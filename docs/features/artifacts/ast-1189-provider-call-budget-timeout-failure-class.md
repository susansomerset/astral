# Provider call budget + timeout failure class (anticipate_scan jobs failing)

**Linear:** [AST-1189](https://linear.app/astralcareermatch/issue/AST-1189/provider-call-budget-timeout-failure-class-anticipate-scan-jobs-failing)  
**Parent:** [AST-1164 — anticipate_scan jobs failing](https://linear.app/astralcareermatch/issue/AST-1164/anticipate-scan-jobs-failing)  
**Publish ref:** `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout`

Raise the shared DeepSeek / Anthropic per-call time budget to **10 minutes** (config-owned), keep the existing `asyncio.wait_for` grace of **+10s**, and ensure an over-budget call returns `success=False` with a **non-empty** timeout `error` and `failure_class=provider_call_timeout`. Today `str(asyncio.TimeoutError())` is `""`, which is why `do_task(…) provider call failed … error=` can be blank after a wait_for timeout. Hollow `stop=?` / zero-token response classification is **AST-1190**; batch release / debug trail is **AST-1191**.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `PROVIDER_CALL_BUDGET` block (10 min timeout, 10s grace, failure_class, error template, exception type names); document in module header | utils |
| `src/utils/llm_external.py` | Helpers: http/wait timeout seconds, `classify_provider_call_timeout`, non-empty timeout error string; compose with existing balance-refusal tagging | utils |
| `src/external/deepseek.py` | Drop module `_API_CALL_TIMEOUT`; httpx + `wait_for` from config; on timeout-class exceptions return non-empty error + `failure_class` | external |
| `src/external/anthropic.py` | Same budget + timeout tagging as DeepSeek | external |

**Not in scope:** `src/core/agent.py` (beyond consuming the existing `error` / `failure_class` on the result dict — no new hollow-response or release logic); prompts / `run_next` / BUILD_ARTIFACTS topology; AST-1163 name/ANALYSIS tokens; AST-1190 empty-response surfacing; AST-1191 hop release + debug found/recorded.

---

## Stage 1: Config — `PROVIDER_CALL_BUDGET`

**Done when:** `PROVIDER_CALL_BUDGET` is importable from `config.py` with `timeout_seconds == 600`, `grace_seconds == 10`, and `failure_class == "provider_call_timeout"`.

1. In `src/utils/config.py` module docstring `Config sections:`, add a line after `PROVIDER_BALANCE_REFUSAL`:
   `PROVIDER_CALL_BUDGET — LLM per-call wall budget + timeout failure class (AST-1189)`.
2. Immediately after the existing `PROVIDER_BALANCE_REFUSAL = {…}` block, add:

```python
# PROVIDER_CALL_BUDGET — per-call LLM wall time (AST-1189 / Archie: 10 minutes).
# httpx client timeout uses timeout_seconds; asyncio.wait_for uses timeout_seconds + grace_seconds.
PROVIDER_CALL_BUDGET = {
    "timeout_seconds": 600,
    "grace_seconds": 10,
    "failure_class": "provider_call_timeout",
    "error_template": (
        "Provider call exceeded per-call time budget ({timeout_seconds}s)"
    ),
    "exception_type_names": (
        "TimeoutError",       # builtin / asyncio.TimeoutError
        "TimeoutException",   # httpx base
        "ReadTimeout",
        "ConnectTimeout",
        "WriteTimeout",
        "PoolTimeout",
        "APITimeoutError",    # anthropic SDK
    ),
}
```

3. Do not add env lookups. Do not change `dispatch_timeout_seconds` or Railway gunicorn timeout.

⚠️ **Decision:** Dedicated top-level block (parallel to `PROVIDER_BALANCE_REFUSAL`), not a nested `ASTRAL_CONFIG` key — same failure-class pattern as AST-897 so utils classifiers stay config-sourced without digging through path/dispatch bags.

---

## Stage 2: Shared timeout helpers in `llm_external`

**Done when:** DeepSeek/Anthropic can import helpers that (a) read budget seconds, (b) classify timeout exceptions, (c) produce a non-empty timeout error string, without importing either external module.

1. In `src/utils/llm_external.py`, import `PROVIDER_CALL_BUDGET` from `src.utils.config` (add to the existing `PROVIDER_BALANCE_REFUSAL` import).
2. Add:

```python
def provider_call_http_timeout_seconds() -> float:
    """httpx / Anthropic client timeout (seconds)."""
    return float(PROVIDER_CALL_BUDGET["timeout_seconds"])


def provider_call_wait_timeout_seconds() -> float:
    """asyncio.wait_for budget = timeout_seconds + grace_seconds."""
    return float(PROVIDER_CALL_BUDGET["timeout_seconds"]) + float(
        PROVIDER_CALL_BUDGET["grace_seconds"]
    )


def provider_call_timeout_error_message() -> str:
    """Non-empty operator-facing timeout error (str(TimeoutError()) is '')."""
    return PROVIDER_CALL_BUDGET["error_template"].format(
        timeout_seconds=int(PROVIDER_CALL_BUDGET["timeout_seconds"])
    )


def classify_provider_call_timeout(exc: BaseException) -> Optional[str]:
    """Return PROVIDER_CALL_BUDGET failure_class when exc is a call-budget timeout."""
    fc = PROVIDER_CALL_BUDGET["failure_class"]
    if isinstance(exc, TimeoutError):
        return fc
    if type(exc).__name__ in PROVIDER_CALL_BUDGET["exception_type_names"]:
        return fc
    return None
```

3. Add `BaseException` to the typing import (or use a bare import) so the classifier signature type-checks the same way as `classify_provider_balance_refusal`.
4. Do **not** change `classify_provider_balance_refusal`, `emit_llm_call_debug`, or hollow-response logic.

⚠️ **Decision:** Prefer `isinstance(exc, TimeoutError)` plus config type-name allowlist over message substrings — avoids false-positive “timeout” text in unrelated API errors; mirrors AST-897’s typed/status matching more than free text.

---

## Stage 3: Wire DeepSeek + Anthropic to config budget and timeout failure class

**Done when:** Both `send_to_deepseek` and `send_to_anthropic` use `PROVIDER_CALL_BUDGET` for httpx + `wait_for`, and any timeout-class exception returns `success=False`, non-empty `error` from `provider_call_timeout_error_message()`, and `failure_class` from config — never blank `error=` from bare `TimeoutError`.

### 3a. `src/external/deepseek.py`

1. Remove module-level `_API_CALL_TIMEOUT = 5 * 60`.
2. Extend the `llm_external` import to include:
   `provider_call_http_timeout_seconds`, `provider_call_wait_timeout_seconds`,
   `classify_provider_call_timeout`, `provider_call_timeout_error_message`
   (keep `classify_provider_balance_refusal`).
3. In `_get_client`, set:
   `timeout=_httpx.Timeout(provider_call_http_timeout_seconds())`.
4. Replace `asyncio.wait_for(..., timeout=_API_CALL_TIMEOUT + 10)` with
   `timeout=provider_call_wait_timeout_seconds()`.
5. In **both** `except Exception as e:` blocks that build the failure `out` dict (inner call-path and outer), after computing `duration` / logging:
   - Let `err = str(e)`.
   - Let `fc_timeout = classify_provider_call_timeout(e)`.
   - If `fc_timeout`: set `err = provider_call_timeout_error_message()`, and set `out["failure_class"] = fc_timeout`.
   - Else: keep today’s `classify_provider_balance_refusal(e)` tagging (set `failure_class` only when that returns a value).
   - Pass `error=err` into `log_llm_batch_summary` and into `emit_llm_call_debug` (when debug), and set `out["error"] = err`.
6. Do not add hollow-response checks on successful returns. Do not change max_tokens hard-fail (AST-903).

### 3b. `src/external/anthropic.py`

1. Mirror 3a exactly: drop `_API_CALL_TIMEOUT`, import the same helpers, use `provider_call_http_timeout_seconds()` everywhere a client is constructed with `_httpx.Timeout(...)` (both `_get_client` and the `api_key_override` inline client), use `provider_call_wait_timeout_seconds()` for `wait_for`, and apply the same timeout-vs-balance failure tagging in both except blocks.

⚠️ **Decision:** Keep dual enforcement (httpx timeout = budget; wait_for = budget + grace) — parent AC explicitly allows “budget plus the small existing grace.” Do not redesign `asyncio.to_thread` cancellation; when wait_for fires, the caller must still get the structured timeout failure even if the worker thread keeps running.

⚠️ **Decision:** Leave `src/core/agent.py` unchanged. `do_task` already logs `result.get("error")` and returns the provider dict; once `error` is non-empty and `failure_class` is set, AC1 is met. Found/recorded debug enrichment and batch release are AST-1191.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout`.
- Do not add files outside the Files Changed table.
- If `PROVIDER_BALANCE_REFUSAL` / except-block shape has drifted from this plan, stop and comment on **AST-1164** (parent) with the Stage N blocked template — do not invent a third failure path.
- Healthy path (normal stop reason + tokens) must remain a successful return with no timeout tagging.

---

## Self-Assessment

**Scope:** `Single-Component` — config + shared LLM utils + mirrored DeepSeek/Anthropic external call wrappers; no core orchestration, UI, or dispatch topology.

**Conf:** `high` — budget already exists as `_API_CALL_TIMEOUT` + wait_for grace; blank `error=` is the known `str(TimeoutError()) == ""` footgun; AST-897/AST-903 already established `failure_class` on the same return envelope.

**Risk:** `Medium` — wrong classification could label ordinary API errors as timeouts, or a missed except path could still emit blank errors; 10-minute budget increases worst-case hop latency by design (Archie).

---

## Code rules check

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | Timeout classify + message live once in `llm_external`; both externals call the same helpers |
| §1.4 / §2.1 config | Budget + failure_class literals in `PROVIDER_CALL_BUDGET`; no env; no magic `5 * 60` left in externals |
| §2.2 / bright line | Provider I/O + timeout tagging stay in external; core only consumes the result dict |
| §2.4 batch | Untouched — release/hold is AST-1191 |
| §3.3 imports | utils ← config; external ← utils; no external↔external |
| §3.5 naming | `provider_call_timeout` failure_class; `PROVIDER_CALL_BUDGET` block name parallel to balance refusal |
| in-scope-only | No hollow-response, prompt, or hop-release work |
