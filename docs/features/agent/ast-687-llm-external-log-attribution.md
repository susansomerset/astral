# AST-687 — LLM provider log attribution and shared utils helpers

**Parent:** [AST-680 — LLM external log attribution (UAT)](https://linear.app/astralcareermatch/issue/AST-680/llm-external-log-attribution-uat)  
**Ticket:** [AST-687](https://linear.app/astralcareermatch/issue/AST-687/llm-provider-log-attribution-and-shared-utils-helpers-why-is)  
**Publish ref (origin):** `sub/AST-680/AST-687-llm-external-log-attribution`

Fix misleading log module attribution when DeepSeek is the active LLM provider. Today `src/external/deepseek.py` imports `_emit_llm_call_debug` from `src/external/anthropic.py`; that helper calls `get_logger(__name__)` inside the anthropic module, so DeepSeek debug lines print under `src.external.anthropic` even when `provider=deepseek`. Move shared helpers into `utils/` per §3.3, remove cross-external imports, and require each caller to pass its own module name so AST-538 debug-contract lines emit under the correct external module identity.

**Out of scope (sibling / parent):** Provider selection and brain tiers; timesheet cost math; Radia review rubric updates (**AST-688**); new LLM providers; debug logging outside LLM external modules and the new utils helper.

## Root cause (confirmed in codebase)

| Location | Problem |
|----------|---------|
| `src/external/deepseek.py` L26 | `from src.external.anthropic import extract_api_response_text, _emit_llm_call_debug` — violates §3.3 (external → external). |
| `src/external/anthropic.py` L110 | `_emit_llm_call_debug` uses `get_logger(__name__, debug_flag=True)` — `__name__` is always `src.external.anthropic`. |
| `src/external/deepseek.py` L252–265 | Calls imported `_emit_llm_call_debug` — debug index/detail lines inherit anthropic module prefix. |

Susan's AC: log **prefix** must identify the provider external module; detail lines keep `provider=deepseek` / `provider=anthropic` and correct vendor model unchanged.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/llm_external.py` | **New.** `extract_api_response_text`, `emit_llm_call_debug` (moved from anthropic; attribution fix via `logger_name`). | utils |
| `src/external/anthropic.py` | Remove local copies of moved helpers; import from `src.utils.llm_external`; pass `logger_name=__name__` at each debug emit site; drop `_emit_llm_call_debug` from module body; keep `extract_api_response_text` in `__all__` via re-export **or** update callers (see Stage 2 step 4). | external |
| `src/external/deepseek.py` | Replace anthropic import with `src.utils.llm_external`; pass `logger_name=__name__` at each debug emit site; confirm zero imports from `src.external.anthropic`. | external |
| `src/core/agent.py` | Update `extract_api_response_text` import to `src.utils.llm_external` (preferred) **or** keep importing via anthropic re-export — must not import debug helper from anthropic. | core |
| `tests/component/utils/test_llm_external.py` | **New.** Unit tests for `emit_llm_call_debug` logger attribution and `extract_api_response_text` edge cases. | tests |
| `tests/component/external/test_deepseek.py` | Extend one mocked `debug=True` case to assert `get_logger` receives `src.external.deepseek` module name (patch target per Stage 3). | tests |

## Stage 1: Shared utils module

**Done when:** `src/utils/llm_external.py` exists with both helpers; no external module imports another external module for these functions; file passes import-layer check (external → utils only).

1. Create `src/utils/llm_external.py` with module docstring noting shared helpers for Anthropic- and DeepSeek-compatible external clients (AST-687 / AST-538 contract).

2. Move `extract_api_response_text(api_response: Any) -> str` from `src/external/anthropic.py` (current L79–90) into `llm_external.py` **verbatim** in behavior:
   - Iterate `api_response.content` blocks; collect blocks with non-empty `.text`; return **last** text block.
   - Same `ValueError` messages when content missing or no text blocks.

3. Move `_emit_llm_call_debug` body from `src/external/anthropic.py` (current L93–136) into `llm_external.py` as **`emit_llm_call_debug`** (public name — callers are sibling external modules, not internal-only).

4. Add required keyword-only parameter **`logger_name: str`** as the **first** parameter after `*`. Replace:
   ```python
   dbg = get_logger(__name__, debug_flag=True)
   ```
   with:
   ```python
   dbg = get_logger(logger_name, debug_flag=True)
   ```
   Keep all other parameters and AST-538 line shapes unchanged (`debug_index`, `debug_detail`, `debug_detail_block`, token line, error/max_tokens branches).

5. In `llm_external.py`, import only from utils:
   ```python
   from src.utils.logging import get_logger
   ```
   No imports from `core`, `data`, `external`, or `ui`.

⚠️ **Decision:** Public name `emit_llm_call_debug` in utils (drop leading underscore) because multiple external modules call it; attribution is enforced by required `logger_name`, not by hiding the symbol in one provider module.

## Stage 2: Rewire Anthropic and DeepSeek external clients

**Done when:** Grep of `src/external/` shows no `from src.external.anthropic` in `deepseek.py`; both clients call `emit_llm_call_debug(..., logger_name=__name__, ...)`; Anthropic debug path unchanged in message shape.

1. In `src/external/anthropic.py`:
   - Add `from src.utils.llm_external import extract_api_response_text, emit_llm_call_debug`.
   - Delete the in-module definitions of `extract_api_response_text` and `_emit_llm_call_debug`.
   - At **every** call site that was `_emit_llm_call_debug(` (success ~L332, error paths ~L419 and ~L437), replace with:
     ```python
     emit_llm_call_debug(
         logger_name=__name__,
         func_name="send_to_anthropic",
         ...
     )
     ```
     Preserve all existing keyword args (`provider="anthropic"`, token counts, `raw_text`, etc.).

2. In `src/external/deepseek.py`:
   - Remove `from src.external.anthropic import extract_api_response_text, _emit_llm_call_debug`.
   - Add `from src.utils.llm_external import extract_api_response_text, emit_llm_call_debug`.
   - At **every** `_emit_llm_call_debug(` call (~L252, ~L346, ~L365), replace with `emit_llm_call_debug(logger_name=__name__, func_name="send_to_deepseek", ...)` preserving `provider="deepseek"` and `vendor_detail` kwargs.

3. Confirm `log_llm_batch_summary(logger, ...)` calls in both modules still use each module's existing `logger = get_logger(__name__)` — do **not** change batch summary attribution in this ticket.

4. In `src/core/agent.py`, change:
   ```python
   from src.external.anthropic import send_to_anthropic, getTimestampPrefix, extract_api_response_text
   ```
   to:
   ```python
   from src.external.anthropic import send_to_anthropic, getTimestampPrefix
   from src.utils.llm_external import extract_api_response_text
   ```
   Leave `send_to_anthropic` / `getTimestampPrefix` imports on anthropic unchanged.

5. Update `src/external/anthropic.py` `__all__` to **remove** `extract_api_response_text` if agent no longer re-exports through anthropic (step 4). If any other in-repo importer still uses `from src.external.anthropic import extract_api_response_text`, update that importer to `src.utils.llm_external` in this same stage — run ripgrep before commit:
   ```bash
   rg 'from src\.external\.anthropic import.*extract_api_response_text' src/
   rg 'from src\.external\.anthropic import' src/external/deepseek.py
   ```
   Both must return zero matches for deepseek cross-import; agent import updated per step 4.

## Stage 3: Tests locking attribution

**Done when:** New utils tests pass; extended deepseek test passes; existing `tests/component/external/test_deepseek.py` and `tests/component/external/test_anthropic.py` and `tests/component/core/test_agent.py` provider-routing tests remain green without weakening.

1. Create `tests/component/utils/test_llm_external.py`:
   - **`test_extract_api_response_text_last_text_block`:** Mock response with two text blocks; assert returned string is the last block's text.
   - **`test_extract_api_response_text_skips_non_text_blocks`:** Block without `.text` skipped (mirrors thinking-block behavior noted in current docstring).
   - **`test_emit_llm_call_debug_uses_logger_name`:** Patch `src.utils.llm_external.get_logger` with `MagicMock`; call `emit_llm_call_debug(logger_name="src.external.deepseek", func_name="send_to_deepseek", prompt_label="t", model="deepseek-v4-flash", duration=1.0, stop_reason="end_turn", input_total=1, input_cached=0, cache_creation_tokens=0, output_total=1)`; assert `get_logger.call_args[0][0] == "src.external.deepseek"` and `get_logger.call_args[1]["debug_flag"] is True`.

2. In `tests/component/external/test_deepseek.py`, add **`test_debug_true_emits_under_deepseek_module`**:
   - Reuse existing mock/fixture pattern for `send_to_deepseek` with `debug=True`.
   - Patch `src.utils.llm_external.get_logger` (not anthropic's logger).
   - After await, assert `get_logger` was called with first positional arg `"src.external.deepseek"` at least once during the emit path.

3. Run:
   ```bash
   pytest tests/component/utils/test_llm_external.py tests/component/external/test_deepseek.py tests/component/external/test_anthropic.py -q
   ```
   Fix **product code only** if red; if a test expectation is wrong, stop and `[qa-handoff]` on Linear.

## Stage 4: Manual smoke (Susan UAT prep)

**Done when:** Engineer documents one-line evidence in Linear comment on **AST-687** that DeepSeek and Anthropic prefixes differ under `debug=True`.

1. Local or staging: run one representative DeepSeek dispatch (e.g. task that hits `send_to_deepseek` with `debug=True`) and capture one debug index line — prefix must contain `src.external.deepseek`, not `src.external.anthropic`.

2. Run one Anthropic-backed call with `debug=True` — prefix must contain `src.external.anthropic`.

3. Post both one-line log samples (redact secrets) on **AST-687** in the build completion comment; no new spike files required.

## Self-Assessment

**Scope:** `Single-Component` — Touches one new utils module and two external LLM clients plus a single import line in `agent.py`; no dispatcher, config, or cost math changes.

**Conf:** `high` — Root cause is confirmed (cross-external import + hardcoded `__name__` in shared helper); fix is a straight move to utils with an explicit `logger_name` parameter following existing `get_logger` patterns.

**Risk:** `low` — Wrong attribution would confuse UAT logs only; API behavior, provider routing, and timesheet recording paths are untouched. Worst case is mislabeled debug prefix with unchanged functional output.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Pass — shared helper consolidated in utils instead of duplicated or cross-imported. |
| §2.1 config | N/A — no config changes. |
| §2.4 batch | N/A — no batch processing changes. |
| §2.6 state machine | N/A — no entity state changes. |
| §3.3 imports | Pass — external imports utils only after Stage 2; core imports utils for `extract_api_response_text`. |
| §3.5 naming | Pass — `llm_external.py` matches utils snake_case; public function names describe behavior. |

No conflicts requiring `conf-!!-NONE`.
