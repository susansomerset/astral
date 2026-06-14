# AST-620 — External LLM wrapper debug instrumentation (Debug logging backfill: external LLM wrappers)

- **Linear (this ticket):** [AST-620](https://linear.app/astralcareermatch/issue/AST-620/external-llm-wrapper-debug-instrumentation-debug-logging-backfill)
- **Parent:** [AST-546](https://linear.app/astralcareermatch/issue/AST-546/debug-logging-backfill-external-llm-wrappers)
- **Publish ref:** `origin/sub/AST-546/AST-620-external-llm-wrapper-debug` (child of AST-546; not Linear `gitBranchName`)
- **Depends on:** [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging) / [AST-554](https://linear.app/astralcareermatch/issue/AST-554/debug-logging-contract-and-shared-helper) — shared helper + §1.5.1 on integration line.

## Summary

Backfill the **AST-538** debug logging contract in **`src/external/anthropic.py`** and **`src/external/deepseek.py`**: when `debug=True`, each LLM API call emits one Style D index header plus `|` detail lines for model, task key (`prompt_label`), timing, token counts, stop reason, and a **truncated raw response preview** via `debug_detail_block` / `truncate_debug_content`. Retire every hand-rolled `logger.info("[DEBUG] …")` in these modules. **`log_llm_batch_summary`** and all non-debug INFO/ERROR timing lines remain unchanged when `debug=False`.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| `src/core/agent.py`, dispatcher, consult, roster, gazer, builder | Sibling backfill tickets (**AST-541**–**AST-545**, **AST-618**, etc.) |
| API parameters, retry logic, cost calculation, timesheet recording | Forbidden per ticket |
| Logging full prompts or secrets at INFO when `debug=False` | Forbidden per parent |
| Betty log-string tests | Forbidden per ticket; Radia enforces on review |
| Other `src/external/*` modules (playwright, google_cse, stytch, gmail) | Not LLM wrappers; not in parent scope |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/anthropic.py` | Add `_emit_llm_call_debug` helper; replace `[DEBUG]` blocks with contract emission on success and error paths | external |
| `src/external/deepseek.py` | Import and call `_emit_llm_call_debug`; remove `[DEBUG]` blocks | external |

## Stage 1: Shared debug emitter in `anthropic.py`

**Done when:** `_emit_llm_call_debug` exists in `anthropic.py` and is callable with the fields below; no call sites wired yet; no behavior change.

1. After the module `logger = get_logger(__name__)` line (~32), add import if not already present:

```python
from src.utils.logging import get_logger, log_batch_id, log_llm_batch_summary  # extend existing import
```

(Ensure `get_logger` is already imported — it is.)

2. Add module-private helper (place after `extract_api_response_text`, before `_parse_api_response`):

```python
def _emit_llm_call_debug(
    *,
    func_name: str,
    prompt_label: str,
    model: str,
    duration: float,
    stop_reason: str,
    input_total: int,
    input_cached: int,
    cache_creation_tokens: int,
    output_total: int,
    raw_text: str = "",
    error: Optional[str] = None,
    provider: str = "anthropic",
    vendor_detail: Optional[str] = None,
) -> None:
    """Emit AST-538 contract lines for one external LLM call (debug_flag must already be True)."""
    dbg = get_logger(__name__, debug_flag=True)
    outcome = "error" if error else ("max_tokens" if stop_reason == "max_tokens" else "success")
    dbg.debug_index(
        func=func_name,
        index=1,
        total=1,
        identifier=prompt_label or "(unknown)",
        outcome=outcome,
    )
    dbg.debug_detail(
        f"provider={provider} model={model} task={prompt_label} "
        f"duration={duration:.1f}s stop_reason={stop_reason or 'n/a'}"
    )
    token_line = (
        f"tokens fresh={input_total} cache_read={input_cached} "
        f"cache_write={cache_creation_tokens} output={output_total}"
    )
    if vendor_detail:
        token_line = f"{vendor_detail} {token_line}"
    dbg.debug_detail(token_line)
    if error:
        dbg.debug_detail(f"error={error}")
    elif stop_reason == "max_tokens":
        dbg.debug_detail("warning=stop_reason_max_tokens — API response may be truncated")
    if raw_text and not error:
        dbg.debug_detail("response_preview:")
        dbg.debug_detail_block(raw_text)
```

⚠️ **Decision:** Single-call wrappers use **`index 1/1`** (not batch counters). `prompt_label` is the task key (agent passes `task_key` today). Raw text comes from `extract_api_response_text` — not parsed JSON — so Susan sees what the API returned before parsing.

## Stage 2: Wire `send_to_anthropic` success and error paths

**Done when:** With `debug=True`, every successful Anthropic call emits contract lines including truncated response preview; with `debug=False`, no new contract lines and `log_llm_batch_summary` behavior unchanged.

1. In `send_to_anthropic`, at function entry after `_empty_timesheet` lambda (~235), add:

```python
if debug:
    logger.set_debug_flag(True)
```

2. **Success path** — replace the entire `if debug:` block (~280–287) that uses `logger.info("[DEBUG] …")` with:

```python
if debug:
    raw_text = extract_api_response_text(response) if response.content else ""
    stop_reason = getattr(response, "stop_reason", "?")
    _emit_llm_call_debug(
        func_name="send_to_anthropic",
        prompt_label=prompt_label,
        model=model_code,
        duration=duration,
        stop_reason=stop_reason,
        input_total=input_total,
        input_cached=input_cached,
        cache_creation_tokens=cache_creation_tokens,
        output_total=output_total,
        raw_text=raw_text,
        provider="anthropic",
    )
```

3. **Inner API failure** — in the `except Exception as e:` block at ~358 (inside `_make_api_call` try), after `log_llm_batch_summary(..., error=str(e))` and before `return {"success": False, ...}`:

```python
if debug:
    _emit_llm_call_debug(
        func_name="send_to_anthropic",
        prompt_label=prompt_label,
        model=model_code,
        duration=duration,
        stop_reason="error",
        input_total=0,
        input_cached=0,
        cache_creation_tokens=0,
        output_total=0,
        error=str(e),
        provider="anthropic",
    )
```

4. **Outer failure** — in the `except Exception as e:` block at ~362, after `log_llm_batch_summary(..., error=str(e))` and before return, add the same `if debug:` `_emit_llm_call_debug(...)` block as step 3.

5. Do **not** move, gate, or alter `log_llm_batch_summary` calls — they run regardless of `debug` when `log_batch_id` is set (§1.5.1 coexistence).

6. Do **not** add debug logging inside `_parse_json_response`, `_parse_api_response`, or other helpers — only at the `send_to_anthropic` call boundary.

## Stage 3: Wire `send_to_deepseek` via shared helper

**Done when:** DeepSeek wrapper mirrors Anthropic contract; no `[DEBUG]` lines remain in `deepseek.py`; with `debug=False` behavior unchanged.

1. Extend import from anthropic (~26):

```python
from src.external.anthropic import extract_api_response_text, _emit_llm_call_debug
```

2. At `send_to_deepseek` entry after `_empty_timesheet` lambda (~194), add:

```python
if debug:
    logger.set_debug_flag(True)
```

3. **Success path** — replace the `if debug:` block (~246–253) with:

```python
if debug:
    raw_text = extract_api_response_text(response) if response.content else ""
    stop_reason = getattr(response, "stop_reason", "?")
    _emit_llm_call_debug(
        func_name="send_to_deepseek",
        prompt_label=prompt_label,
        model=vendor_model,
        duration=duration,
        stop_reason=stop_reason,
        input_total=input_total,
        input_cached=input_cached,
        cache_creation_tokens=cache_creation_tokens,
        output_total=output_total,
        raw_text=raw_text,
        provider="deepseek",
        vendor_detail=f"vendor={vendor_model}",
    )
```

4. **Inner and outer failure paths** — mirror Stage 2 steps 3–4 in `send_to_deepseek`'s two `except Exception as e:` blocks (~330 and ~334), using `vendor_model` for `model=` and `provider="deepseek"`, `vendor_detail=f"vendor={vendor_model}"`.

5. Remove all remaining `logger.info("[DEBUG]` strings from both files (grep confirm zero matches in `src/external/anthropic.py` and `src/external/deepseek.py`).

## Self-Assessment

**Scope:** `Single-Component` — Two mirrored files in `src/external/` only; no core, data, or config changes.

**Conf:** `high` — AST-554 helpers and sibling plans (e.g. AST-618) establish the exact emission pattern; ticket AC and boundaries are explicit.

**Risk:** `Medium` — Every production LLM call flows through these wrappers, but changes are debug-gated only with no API, retry, or cost-path edits; wrong debug output would not affect dispatch outcomes.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Shared `_emit_llm_call_debug` in anthropic, imported by deepseek — avoids duplicating index/detail/block logic |
| §1.5 / §1.5.1 | Uses `debug_index`, `debug_detail`, `debug_detail_block`; no new contract lines when `debug=False`; `log_llm_batch_summary` untouched |
| §2.5 Bright line | External layer only; no business logic |
| §3.3 Imports | deepseek → anthropic for helper is existing pattern (`extract_api_response_text`); no utils→data |
| §3.5 Naming | Private helper `_emit_llm_call_debug`; snake_case params |

No conflicts requiring `conf-!!-NONE`.

## Review (build stub)

**Built:** `origin/sub/AST-546/AST-620-external-llm-wrapper-debug` @ `6e66f8e5`.

**Stages delivered:**
- Stage 1: `_emit_llm_call_debug` helper + `send_to_anthropic` success/error paths — `6e66f8e5`.
- Stage 2: `send_to_deepseek` imports helper; success/error paths; zero `[DEBUG]` strings — `6e66f8e5`.

## Review (Radia — AST-620)

**Diff:** `origin/dev...origin/sub/AST-546/AST-620-external-llm-wrapper-debug` @ `da1e7c89`.

### What's solid

| Area | Notes |
|------|--------|
| Plan fidelity | Stages 1–3 delivered: shared `_emit_llm_call_debug`, both wrappers wired on success + inner/outer API error paths; `[DEBUG]` retired (grep clean). |
| §1.5.1 contract | `debug=True` gates via `set_debug_flag` + `if debug:` call sites; Style D `index 1/1`; `\|` detail lines; `debug_detail_block` for response preview; `log_llm_batch_summary` coexistence preserved. |
| §2.5 / §3.3 layer | External-only; deepseek → anthropic helper import matches existing `extract_api_response_text` pattern; no utils→data, no core/data edits in product diff. |
| Scope / boundaries | No API, retry, cost, or sibling-module scope; bible §7.13zzh via `merge-tests` (Betty manifest), not engineer bible edit. |
| Self-assessment | `scope-Single-Component` / `conf-high` / `risk-Medium` matches actual footprint. |

### Issues

| Severity | Item | Location |
|----------|------|----------|
| advisory | Parse-failure path (API OK, schema/parse fail) still emits only `log_llm_batch_summary` when `debug=True` — no contract block. Pre-change parity (old `[DEBUG]` never ran there either). Optional follow-up if Susan wants raw preview on parse errors. | `send_to_anthropic` / `send_to_deepseek` parse `except` blocks |
| advisory | `_emit_llm_call_debug` uses a fresh `get_logger(__name__, debug_flag=True)` while call sites also `set_debug_flag(True)` on module logger — redundant but correct. | `anthropic.py` `_emit_llm_call_debug` |

### Recommended actions

| Action | Owner |
|--------|-------|
| None required for merge — approve for `resolve-child` / User Testing path. | Ada |
| (Optional) Emit contract debug on parse-failure if debug runs should show the raw body that failed parsing. | Future ticket / Susan call |
