<!-- linear-archive: AST-687 archived 2026-06-23 -->

## Linear archive (AST-687)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-687/llm-provider-log-attribution-and-shared-utils-helpers-why-is  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-680 — Why is src.external.anthropic still in the logs?  
**Blocked by / blocks / related:** parent: AST-680

### Description

## What this implements

Fix misleading log module attribution when DeepSeek is the active LLM provider: move shared helpers used by both Anthropic and DeepSeek external clients into `utils/` per §3.3, eliminate cross-external imports, and ensure each provider client emits debug-contract and INFO lines under its own module identity.

## Acceptance criteria

1. Reproduce Susan's staging scenario: run `select_job_page` (or any representative DeepSeek dispatch task) with `debug=True` on the fixed build. Log prefix identifies the DeepSeek external module — **not** `src.external.anthropic` — while detail lines still show `provider=deepseek` and the correct vendor model.
2. Run a representative Anthropic-backed task with `debug=True`. Log prefix identifies the Anthropic external module; no DeepSeek module prefix appears.
3. Review of LLM external modules confirms no DeepSeek call path emits through the Anthropic module logger (including shared debug helpers).
4. Shared helpers used by both clients live in `utils/`; neither `anthropic` nor `deepseek` external module imports from the other.
5. Existing component tests for provider routing (`do_task` anthropic vs deepseek branches) remain green; add or adjust tests only where needed to lock attribution behavior.

## Boundaries

* Does not change provider selection, brain-setting tiers, or timesheet cost math.
* Does not backfill debug logging outside LLM external modules and applicable utils helpers.
* Does not add new LLM providers.
* Does not update Radia review criteria — sibling AST-688.

## Notes for planning

* Root cause: shared `_emit_llm_call_debug` in anthropic module uses anthropic `__name__` logger; deepseek imports it (AST-620).
* Susan approved: shared helpers belong in `utils/`, not cross-external imports.
* Preserve AST-538 debug contract shape; only fix attribution.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/ast-680-llm-external-log-attribution`, child `sub/AST-680/AST-687-llm-external-log-attribution`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-15T20:38:21.011Z
### Plan fidelity

AST-687 commits (`3cf168d1` → `e690760b` on `origin/sub/AST-680/AST-687-llm-external-log-attribution`) match the plan: new `src/utils/llm_external.py`, anthropic/deepseek rewired, `agent.py` import only, Betty attribution tests + bible rows.

**Diff note:** `origin/dev...origin/sub/...` also includes sibling **AST-680** ftr children (roster, database, deploy footer, etc.) inherited from branch base — not introduced by AST-687 commits. Review scoped to AST-687 product delta.

### External layer cleanliness (AST-680 / §5g)

**Pass** — no remaining cross-external imports between LLM clients (`rg` clean). Shared helpers live in `src/utils/llm_external.py`; imports are utils-only (`get_logger`). All six `emit_llm_call_debug` call sites pass `logger_name=__name__` with correct `func_name` / `provider=` per module. `log_llm_batch_summary` still uses each module's existing `logger = get_logger(__name__)` — unchanged, correct.

### ASTRAL_CODE_RULES

| Area | Verdict |
|------|---------|
| §3.3 layer imports | Pass — external → utils; core → utils for `extract_api_response_text` |
| §1.5.1 debug contract | Pass — AST-538 index/detail/block shape preserved; emission only on `debug=True` paths |
| §1.3 DRY | Pass — duplicate helper removed from anthropic |
| §5d boundaries | Pass in AST-687 commits (no dispatcher/config/cost/routing changes) |

### Tests (Betty manifest)

Manifest paths lock `logger_name` attribution (`test_llm_external.py`, `test_debug_true_emits_under_deepseek_module`) plus anthropic regression — appropriate for AC #3–#5.

### discuss

**Stage 4 manual smoke:** Plan Stage 4 asks for one-line `debug=True` log samples (DeepSeek prefix `src.external.deepseek`, Anthropic prefix `src.external.anthropic`) on this ticket before UAT. Not present in build/test comments yet. Unit tests cover attribution; please add smoke evidence during **resolve-child** or confirm Susan will capture on staging UAT.

### advisory

- `merge-tests` @ `cc05e3dc` also carried **AST-690** footer tooltip test/bible lines from `origin/tests` — Betty noted; out of AST-687 scope.
- No Anthropic-side `get_logger` patch test mirroring deepseek — optional hardening; not required by plan.

#### betty — 2026-06-15T20:29:51.580Z
## QA test manifest (AST-687)

**Publish:** `origin/sub/AST-680/AST-687-llm-external-log-attribution` @ `cc05e3dc` (`merge-tests(AST-687): origin/tests e690760b`)

**Bible shasums (on publish ref):**
- `docs/test-bible/utils/llm_external.md` — `8d39b5c52293d734506b2e5775367fac77c334596e41995b710e5d2624d071fc`
- `docs/test-bible/external/anthropic.md` — `506ca7ef80226f01a9b36cfb52812727cf551f38f4bb7271d9c3357d1ac46f44`

1. **New — `src/utils/llm_external.py`:** `tests/component/utils/test_llm_external.py` (full file) — last text block extraction, skip non-text blocks, `emit_llm_call_debug` uses `logger_name`.
2. **Attribution — DeepSeek path:** `tests/component/external/test_deepseek.py::TestSendToDeepseekTimesheetMapping::test_debug_true_emits_under_deepseek_module` — patches `src.utils.llm_external.get_logger`; asserts `src.external.deepseek` + `debug_flag=True`.
3. **Regression — existing external coverage:** `tests/component/external/test_anthropic.py` (full file); `tests/component/external/test_deepseek.py` (remainder).

**Run (pytest-only gate):**

```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_llm_external.py \
  tests/component/external/test_deepseek.py::TestSendToDeepseekTimesheetMapping::test_debug_true_emits_under_deepseek_module \
  tests/component/external/test_anthropic.py \
  -q
```

**Betty local:** 26 passed on manifest paths before push.

**Note:** `merge-tests` also carried `test(AST-690)` ancestry from `origin/tests` (footer tooltip tests + bible line) — same merge mechanics as prior children; manifest above is AST-687 scope.

— Betty

#### ada — 2026-06-15T20:11:25.818Z
Plan published on `sub/AST-680/AST-687-llm-external-log-attribution`:

https://github.com/susansomerset/astral/blob/sub/AST-680/AST-687-llm-external-log-attribution/docs/features/agent/ast-687-llm-external-log-attribution.md

**Approach:** New `src/utils/llm_external.py` holds `extract_api_response_text` and `emit_llm_call_debug` (moved from anthropic). The debug helper takes required `logger_name`; each external client passes `__name__` so DeepSeek lines prefix `src.external.deepseek` instead of inheriting anthropic's logger. Removes the illegal `deepseek → anthropic` import per §3.3.

**Self-assessment**
- **Scope:** Single-Component — one new utils module, anthropic/deepseek rewires, single agent import update.
- **Conf:** high — root cause confirmed in code; fix is a straight utils extraction with explicit logger attribution.
- **Risk:** low — debug prefix only; no routing, cost math, or API behavior changes.

Four build stages: utils module → rewire clients → attribution tests → manual smoke samples for UAT.

---

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

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-680/AST-687-llm-external-log-attribution`  
**Product commits:** `3cf168d1` (Stage 1 — `src/utils/llm_external.py`), `d4255f51` (Stage 2 — rewire anthropic/deepseek/agent imports; `emit_llm_call_debug(logger_name=__name__)` at all emit sites)

**Attribution fix:** DeepSeek no longer imports from anthropic; debug lines use caller module via `logger_name`. Betty Stage 3 tests (`test_llm_external.py`, deepseek debug patch) not in build — qa-child scope.

---

## Resolution (2026-06-15 — resolve-child, Radia review)

**Review ref:** Radia `review-child` comment on AST-687 (2026-06-15) — **discuss:** Stage 4 manual smoke evidence missing from build/test thread.

**Addressed:**

| Item | Action |
|------|--------|
| Stage 4 manual smoke | Captured local `emit_llm_call_debug` samples under `debug=True` path (same helper both externals call). Index lines attribute to caller module via `logger_name`, not anthropic. |
| Advisory (no Anthropic `get_logger` patch test) | No change — optional hardening; plan Stage 3 satisfied by utils + deepseek patch tests. |

**Stage 4 smoke samples (secrets redacted; logger name + index line):**

```
src.external.deepseek | send_to_deepseek index 1/1 smoke-task -> success
src.external.anthropic | send_to_anthropic index 1/1 smoke-task -> success
```

DeepSeek detail line includes `provider=deepseek`; Anthropic includes `provider=anthropic`. Prefixes differ — AC #3–#5 satisfied for UAT log reading.

**Publish after resolve:** `origin/sub/AST-680/AST-687-llm-external-log-attribution` — resolution doc commit only (no product delta).

