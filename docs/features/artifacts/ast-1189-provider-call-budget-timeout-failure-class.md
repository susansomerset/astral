# Provider call budget + timeout failure class (anticipate_scan jobs failing)

**Linear:** [AST-1189](https://linear.app/astralcareermatch/issue/AST-1189/provider-call-budget-timeout-failure-class-anticipate-scan-jobs-failing)  
**Parent:** [AST-1164 — anticipate_scan jobs failing](https://linear.app/astralcareermatch/issue/AST-1164/anticipate-scan-jobs-failing)  
**Publish ref:** `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout`

Raise the shared DeepSeek / Anthropic per-call time budget to **10 minutes** (config-owned), keep **+10s** grace, and make the **caller-observed** duration honor that budget: over-budget calls must return `success=False` with a **non-empty** timeout `error` and `failure_class=provider_call_timeout` at ≈ budget+grace — not after the SDK thread finally finishes (the parent log waited **1425.7s** while the old 310s `wait_for` failed to release the caller). Hollow `stop=?` / zero-token response classification is **AST-1190**; batch release / debug trail is **AST-1191**.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `PROVIDER_CALL_BUDGET` (600s timeout, 10s grace, `max_retries: 0`, failure_class, error template, exception type names); document in module header | utils |
| `src/utils/llm_external.py` | Budget readers; cause-chain timeout classifier; non-empty error helpers; `await_provider_call_with_budget` (release caller at deadline without awaiting the orphan thread) | utils |
| `src/external/deepseek.py` | Drop `_API_CALL_TIMEOUT`; client uses config httpx timeout + `max_retries`; replace `asyncio.wait_for(to_thread…)` with `await_provider_call_with_budget`; timeout/balance tagging + never-empty `error` on failure returns | external |
| `src/external/anthropic.py` | Same budget, wall-release, `max_retries`, and failure tagging as DeepSeek | external |

**Not in scope:** `src/core/agent.py` (consumes existing `error` / `failure_class` only); prompts / `run_next` / BUILD_ARTIFACTS topology; AST-1163 name/ANALYSIS tokens; AST-1190 empty-response surfacing; AST-1191 hop release + debug found/recorded; migrating to the Anthropic async SDK.

---

## Stage 1: Config — `PROVIDER_CALL_BUDGET`

**Done when:** `PROVIDER_CALL_BUDGET` is importable with `timeout_seconds == 600`, `grace_seconds == 10`, `max_retries == 0`, and `failure_class == "provider_call_timeout"`.

1. In `src/utils/config.py` module docstring `Config sections:`, add a line after `PROVIDER_BALANCE_REFUSAL`:
   `PROVIDER_CALL_BUDGET — LLM per-call wall budget + timeout failure class (AST-1189)`.
2. Immediately after the existing `PROVIDER_BALANCE_REFUSAL = {…}` block, add:

```python
# PROVIDER_CALL_BUDGET — per-call LLM wall time (AST-1189 / Archie: 10 minutes).
# httpx client timeout uses timeout_seconds; caller wait uses timeout_seconds + grace_seconds.
# max_retries=0 → one attempt (SDK default 2 would allow up to 3× wall time inside the worker thread).
PROVIDER_CALL_BUDGET = {
    "timeout_seconds": 600,
    "grace_seconds": 10,
    "max_retries": 0,
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

3. Do not add env lookups. Do not change `dispatch_timeout_seconds` (3600) or Railway gunicorn timeout — with `max_retries=0` and a 610s caller budget, worst-case hop latency stays under the AUTO dispatch wall.

⚠️ **Decision:** Dedicated top-level block (parallel to `PROVIDER_BALANCE_REFUSAL`), not a nested `ASTRAL_CONFIG` key — same failure-class pattern as AST-897.

---

## Stage 2: Shared helpers in `llm_external`

**Done when:** DeepSeek/Anthropic can import budget readers, a cause-chain timeout classifier, never-empty error helpers, and an async wall-budget runner that releases the caller at the deadline without awaiting the worker thread — without either external importing the other.

1. In `src/utils/llm_external.py`, import `PROVIDER_CALL_BUDGET` alongside the existing `PROVIDER_BALANCE_REFUSAL` import. Add `asyncio` and `Callable` / `Any` as needed for the await helper. **Do not** add `BaseException` to the `typing` import — it is a builtin (same as the existing `classify_provider_balance_refusal(exc: BaseException)` annotation, which already works with no import).
2. Add budget readers + timeout error message:

```python
def provider_call_http_timeout_seconds() -> float:
    """httpx / Anthropic client timeout (seconds)."""
    return float(PROVIDER_CALL_BUDGET["timeout_seconds"])


def provider_call_wait_timeout_seconds() -> float:
    """Caller-observed wall budget = timeout_seconds + grace_seconds."""
    return float(PROVIDER_CALL_BUDGET["timeout_seconds"]) + float(
        PROVIDER_CALL_BUDGET["grace_seconds"]
    )


def provider_call_timeout_error_message() -> str:
    """Non-empty operator-facing timeout error (str(TimeoutError()) is '')."""
    return PROVIDER_CALL_BUDGET["error_template"].format(
        timeout_seconds=int(PROVIDER_CALL_BUDGET["timeout_seconds"])
    )


def provider_call_max_retries() -> int:
    return int(PROVIDER_CALL_BUDGET["max_retries"])
```

3. Add cause-chain classifier (covers wrapped `APIConnectionError` → `__cause__` `ReadTimeout`, etc.):

```python
def classify_provider_call_timeout(exc: BaseException) -> Optional[str]:
    """Return PROVIDER_CALL_BUDGET failure_class when exc (or cause/context) is a call-budget timeout."""
    fc = PROVIDER_CALL_BUDGET["failure_class"]
    names = PROVIDER_CALL_BUDGET["exception_type_names"]
    seen: set[int] = set()
    cur: Optional[BaseException] = exc
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        if isinstance(cur, TimeoutError) or type(cur).__name__ in names:
            return fc
        cur = cur.__cause__ if cur.__cause__ is not None else cur.__context__
    return None
```

4. Add never-empty error guard (AC1 second half — blank `error=` must not ship on any failure path this ticket touches):

```python
def non_empty_provider_error(exc: BaseException, *, fallback: str) -> str:
    """str(exc) or fallback — never '' (TimeoutError default)."""
    err = str(exc).strip()
    return err if err else fallback
```

5. Add the wall-budget runner that **does not** use `asyncio.wait_for` (wait_for cancels then **awaits** the uncancellable `to_thread` worker, so the caller stays blocked until the SDK returns — that is why 310s failed to bound the 1425.7s run):

```python
async def await_provider_call_with_budget(
    make_call: Callable[[], Any],
    *,
    timeout_seconds: float,
) -> Any:
    """Run blocking SDK call in a worker thread; release the caller at timeout_seconds.

    On timeout: raise TimeoutError with provider_call_timeout_error_message() and do
    **not** await the pending thread task (orphan may finish later; caller is free).
    """
    task = asyncio.create_task(asyncio.to_thread(make_call))
    done, _pending = await asyncio.wait({task}, timeout=timeout_seconds)
    if task in done:
        return task.result()
    raise TimeoutError(provider_call_timeout_error_message())
```

6. Do **not** change `classify_provider_balance_refusal`, `emit_llm_call_debug`, or hollow-response logic.

⚠️ **Decision:** Wall-time release via `asyncio.wait(..., FIRST_COMPLETED` default) + abandon pending task — Joan option 2. Chosen over async-SDK migration (larger slice) and over granular httpx-only (still leaves wait_for awaiting the thread). `max_retries=0` is the companion so the abandoned worker is one attempt, not three.

⚠️ **Decision:** Prefer typed/name matching (plus cause/context walk) over message substrings — same as Joan discuss #3 agreement.

---

## Stage 3: Wire DeepSeek + Anthropic — config budget, wall release, timeout failure class

**Done when:** Both `send_to_deepseek` and `send_to_anthropic` (1) build clients with config httpx timeout + `max_retries`, (2) invoke the SDK via `await_provider_call_with_budget` at `provider_call_wait_timeout_seconds()`, (3) on timeout-class failures return `success=False`, non-empty `error` from `provider_call_timeout_error_message()`, and `failure_class=provider_call_timeout`, and (4) every other failure return uses `non_empty_provider_error` so `error` is never `""`. **Observable for AC1 timing:** a forced over-budget call logs `log_llm_batch_summary` with `duration` ≈ budget+grace (≈610s), not the provider’s eventual return time.

### 3a. `src/external/deepseek.py`

1. Remove module-level `_API_CALL_TIMEOUT = 5 * 60`.
2. Extend the `llm_external` import to include:
   `provider_call_http_timeout_seconds`, `provider_call_wait_timeout_seconds`,
   `provider_call_max_retries`, `await_provider_call_with_budget`,
   `classify_provider_call_timeout`, `provider_call_timeout_error_message`,
   `non_empty_provider_error`
   (keep `classify_provider_balance_refusal`).
3. In `_get_client`, construct:
   ```python
   return Anthropic(
       api_key=key,
       base_url="https://api.deepseek.com/anthropic",
       timeout=_httpx.Timeout(provider_call_http_timeout_seconds()),
       max_retries=provider_call_max_retries(),
   )
   ```
4. Replace:
   ```python
   response = await asyncio.wait_for(
       asyncio.to_thread(_make_api_call),
       timeout=_API_CALL_TIMEOUT + 10,
   )
   ```
   with:
   ```python
   response = await await_provider_call_with_budget(
       _make_api_call,
       timeout_seconds=provider_call_wait_timeout_seconds(),
   )
   ```
5. In **both** `except Exception as e:` blocks that build the failure `out` dict (inner call-path and outer), after computing `duration`:
   - `fc_timeout = classify_provider_call_timeout(e)`
   - If `fc_timeout`: `err = provider_call_timeout_error_message()`; set `out["failure_class"] = fc_timeout`
   - Else: `err = non_empty_provider_error(e, fallback=type(e).__name__)`; apply existing `classify_provider_balance_refusal(e)` tagging when it returns a value
   - Pass `error=err` into `log_llm_batch_summary` and `emit_llm_call_debug` (when debug); set `out["error"] = err`
   - Assert by construction: `err` is never `""`
6. Do not add hollow-response checks on successful returns. Do not change max_tokens hard-fail (AST-903).

### 3b. `src/external/anthropic.py`

1. Mirror 3a exactly: drop `_API_CALL_TIMEOUT`; same imports; `_get_client` and the `api_key_override` inline `Anthropic(...)` both get `timeout=_httpx.Timeout(provider_call_http_timeout_seconds())` and `max_retries=provider_call_max_retries()`; replace `wait_for(to_thread…)` with `await_provider_call_with_budget`; same timeout-vs-balance tagging + never-empty `error` in both except blocks.

⚠️ **Decision:** Leave `src/core/agent.py` unchanged. `do_task` already logs `result.get("error")` and returns the provider dict. Found/recorded debug enrichment and batch release are AST-1191.

⚠️ **Decision:** Abandoned worker threads are accepted — when the deadline fires we return timeout to the caller immediately; the thread may still finish later. No thread-kill / async-SDK migration in this ticket.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout`.
- Do not add files outside the Files Changed table.
- If `PROVIDER_BALANCE_REFUSAL` / except-block / `Anthropic(...)` constructor shape has drifted from this plan, stop and comment on **AST-1164** (parent) with the Stage N blocked template — do not invent a third failure path or widen into async-SDK rewrite.
- Healthy path (normal stop reason + tokens within budget) must remain a successful return with no timeout tagging.
- AC1 timing proof for build/test: over-budget path’s logged `duration` ≈ `timeout_seconds + grace_seconds`, not provider-return wall time.

---

## Self-Assessment

**Scope:** `Single-Component` — config + shared LLM utils (including wall-budget await helper) + mirrored DeepSeek/Anthropic external call wrappers; no core orchestration, UI, or dispatch topology.

**Conf:** `Medium` — blank `error=` from `str(TimeoutError())` and the failure_class envelope are well understood (AST-897/903), but the 1425.7s parent log proved the prior wait_for+to_thread budget was not caller-enforcing; the FIRST_COMPLETED abandon path is the right fix and is new wiring on this call site.

**Risk:** `Medium` — orphan threads after abandon; mis-tagging wrapped non-timeout errors if cause-walk is too eager (mitigated by type-name allowlist); 10-minute budget raises worst-case hop latency by design (Archie) but stays under 3600s dispatch timeout with `max_retries=0`.

---

## Code rules check

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | Timeout classify, message, never-empty, and wall-budget await live once in `llm_external` |
| §1.4 / §2.1 config | Budget + retries + failure_class literals in `PROVIDER_CALL_BUDGET`; no env; no magic `5 * 60` left in externals |
| §2.2 / bright line | Provider I/O + timeout tagging stay in external; utils hold pure helpers + await orchestration of the thread |
| §2.4 batch | Untouched — release/hold is AST-1191 |
| §3.3 imports | utils ← config; external ← utils; no external↔external; no `BaseException` from `typing` |
| §3.5 naming | `provider_call_timeout` failure_class; `PROVIDER_CALL_BUDGET` parallel to balance refusal |
| in-scope-only | No hollow-response, prompt, hop-release, or async-SDK migration |

---

## Revisions

Revision 1 — 2026-08-05  
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE) — AC1 timing half unmet by raising an already-unenforced budget; Stage 2 `BaseException` typing-import step would ImportError; classifier may miss wrapped timeouts / blank `error=` fall-through.  
Changes:
- Stage 1: add config-owned `max_retries: 0`.
- Stage 2: delete the `BaseException` typing-import step; add cause/context walk on classifier; add `non_empty_provider_error`; add `await_provider_call_with_budget` (FIRST_COMPLETED / abandon pending — replaces wait_for).
- Stage 3: wire both externals to the wall-budget await + `max_retries`; never-empty `error` on all touched failure returns; Done-when asserts logged `duration` ≈ budget+grace.
- Conf softened `high` → `Medium`. Summary + Decisions updated to match Joan’s wait_for/to_thread analysis.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout`  
**Tip:** `663f6a07`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `d41b16c7` | `PROVIDER_CALL_BUDGET` (600s / 10s grace / `max_retries: 0`) |
| 2 | `6d650feb` | wall-budget helpers + cause-chain classify + never-empty error |
| 3 | `663f6a07` | DeepSeek + Anthropic client budget, `await_provider_call_with_budget`, timeout `failure_class` |

---

## Radia review — code-rubric.v1 revision=1

**Publish ref tip:** `683bcb1f`

**Overall:** FIX-NOW

### Plan adherence

Stages 1–3 (`d41b16c7`, `6d650feb`, `663f6a07`) match the plan's code blocks essentially verbatim — `PROVIDER_CALL_BUDGET` shape, the four `llm_external` helpers, `await_provider_call_with_budget`'s `asyncio.wait(FIRST_COMPLETED)`-and-abandon design, and the mirrored DeepSeek/Anthropic wiring (client `max_retries`, timeout-vs-balance tagging, never-empty `error`) all land as specified. `src/core/agent.py` is untouched, honoring the stated boundary.

### Findings

**fix-now — cross-ticket test/doc contamination breaks this publish ref's own test tree.** The `merge-tests(AST-1189): origin/tests 886b1033` commit pulls in `748a5725 test(AST-1190): hollow provider response + blank error= coverage` as an ancestor on the shared `origin/tests` branch, plus `docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md` (added earlier in this branch's own history, survives a `347bf506` attempt to drop the "sibling" file). Confirmed by running the touched test files against this tip in a fresh venv: **9 failing tests** (`TestAst1190DoTaskEmptyProviderError` x2, `TestAst1190EmptyUnusableProviderResponse` in both `test_anthropic.py`/`test_deepseek.py`, `TestAst1190ProviderEmptyResponseConfig`, `TestAst1190EmptyResponseHelpers` x5) — all `ImportError`/`AttributeError` on `PROVIDER_EMPTY_RESPONSE`, `normalize_provider_error`, `is_unusable_provider_response`, none of which exist on this tip (`src/core/agent.py` and `src/utils/config.py` carry no AST-1190 product surface here — that work lives on AST-1190's own branch). The plan's own boundary line ("Not in scope: ... AST-1190 empty-response surfacing") is correct in intent but not honored by the merged test/doc state. Fix: re-cut the `merge-tests` merge (or have Betty publish an AST-1189-only `origin/tests` SHA that does not stack on the AST-1190 test commit) and drop the leftover `ast-1190-*.md` plan file from this branch before re-requesting review.

**advisory — `astral.standards.debug-contract-gated` mechanically in-scope but content is benign.** The plan's Considered-but-excluded table marks debug/found-recorded trail as AST-1191, but the diff does touch `emit_llm_call_debug(..., error=err, ...)` call sites in both externals. No new debug capability or ungating was added (only the `error=` value changed from `str(e)` to the classified/never-empty string) — not a straggler in substance, noting for completeness.

### Pattern conformance

None cited (plan lists statute ids under In-scope / Considered-but-excluded, not `canon/patterns/*`; those ids are covered by the full-set sweep).

### What's solid

- `PROVIDER_CALL_BUDGET` config shape, the wall-budget release-without-awaiting-the-orphan design, and the mirrored DeepSeek/Anthropic wiring are clean, DRY, and layer-correct (external → utils only, no cross-external import).
- Never-empty `error` guarantee is enforced consistently on every touched failure path in both externals.

### Recommended actions

1. Re-publish `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout` with a `merge-tests` SHA scoped to AST-1189 only (or coordinate ordering with Betty so AST-1190's test commit isn't an ancestor).
2. Drop `docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md` from this branch — it belongs on AST-1190's own publish ref only.
3. Re-run the full touched-file test set on the corrected tip before re-requesting Review Posted.

`context_tokens≈45000`
— Radia

---

## Resolution

**Date:** 2026-08-05  
**Driven by:** Radia `[code-rubric] revision=1` FIX-NOW — cross-ticket AST-1190 test/doc contamination on this publish ref.

| Finding | Action |
|---------|--------|
| leftover `docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md` on this branch | **Done (engineer):** removed from `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout` |
| `merge-tests(AST-1189)` stacks on `748a5725 test(AST-1190)` → 9 failing AST-1190 tests without product surface | **Handed to Betty** via `[qa-handoff]` — stay Review Posted; engineer cannot re-cut `origin/tests` / test-tree |
| advisory debug-contract touch (`error=` value only) | Accepted — no product change |

**Next:** Betty re-publishes AST-1189-scoped `merge-tests`, reassigns Ada; Ada re-runs touched-file suite, then finishes resolve → User Testing.
