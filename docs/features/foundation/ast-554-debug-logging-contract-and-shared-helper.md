# AST-554 — Debug logging contract and shared helper (Improve Quality of Debug Logging)

- **Linear (this ticket):** [AST-554](https://linear.app/astralcareermatch/issue/AST-554/debug-logging-contract-and-shared-helper-improve-quality-of-debug)
- **Parent:** [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging)
- **Publish ref:** `origin/sub/AST-538/AST-554-debug-logging-contract-and-helper` (child of AST-538; not Linear `gitBranchName`)

## Summary

Deliver the **mandatory backend debug logging contract** in `docs/ASTRAL_CODE_RULES.md` and a **shared emission API** in `src/utils/logging.py` so downstream children (e.g. **AST-557** inflow backfill, future component tickets) can log UAT-grade traces without hand-rolled `logger.info("[DEBUG] …")`. This ticket implements parent acceptance criteria **1, 3, 4 (helper gating only), and 7** — not dispatcher/roster instrumentation, nav rename (**AST-555**), or **review-astral** rubric (**AST-556**).

## Out of scope (explicit)

| Item | Owner ticket |
|------|----------------|
| `inflow_discovery` / `vet_inflow_discovery` per-index “found + recorded” logs | **AST-557** (Hedy) |
| Dispatcher/roster path edits beyond `logging.py` | **AST-557** and later backfill children |
| Sidebar **Agent Ad Hoc** rename | **AST-555** (Katherine) |
| `review-astral` fix-now for insufficient debug | **AST-556** (Radia) |
| Retiring existing `[DEBUG]` lines in untouched files | Grandfather per parent — **no** migration commits in AST-554 |
| Hop-boundary lines (`run_next hop: …`, AST-527/530) | Unchanged — remain **INFO**, not `debug=` gated |
| Betty log-string manifest tests | Forbidden per parent; Betty tests **gating + truncation math** only |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/logging.py` | Constants + pure truncation helper + `_PrefixedLogger` debug emission methods | utils |
| `docs/ASTRAL_CODE_RULES.md` | Expand §1.5 with debug contract (trigger, two line kinds, truncation, anti-patterns, coexistence) | docs |
| `tests/component/utils/test_debug_logging.py` | New — gating and truncation behavior only (no golden log prose) | tests |

## Stage 1: Shared helper and constants (`src/utils/logging.py`)

**Done when:** `truncate_debug_content` and `_PrefixedLogger` debug methods exist; module exports documented in docstrings; existing `get_logger` / `test()` / `log_llm_batch_summary` behavior unchanged.

1. Add module-level constants after imports (before `_DatabaseLogHandler`):

```python
DEBUG_DETAIL_PREFIX = " | "  # two spaces, pipe, two spaces — working-log detail only
DEBUG_LINE_THRESHOLD = 50
DEBUG_HEAD_LINES = 15
DEBUG_TAIL_LINES = 15
```

2. Add pure function `truncate_debug_content(text: str) -> list[str]`:
   - Split `text` on `"\n"` (preserve empty trailing line only if input ended with `\n` — use `text.splitlines()` which drops terminal empty line per Python default; **document** that callers pass normalized text).
   - Let `n = len(lines)`.
   - If `n <= DEBUG_LINE_THRESHOLD`: return `lines` unchanged.
   - Else: `omitted = n - DEBUG_HEAD_LINES - DEBUG_TAIL_LINES`; return `lines[:DEBUG_HEAD_LINES] + [f"<{omitted} lines omitted>"] + lines[-DEBUG_TAIL_LINES:]`.
   - Empty string → `[]`.

3. Add pure function `format_debug_index_header(*, func: str, index: int, total: int, identifier: str, outcome: str) -> str`:
   - Require `1 <= index <= total` and `total >= 1` (raise `ValueError` otherwise — fail fast in dev).
   - Return exactly: `f"{func} index {index}/{total} {identifier} -> {outcome}"` where `func` is the **caller's** dotted context (e.g. `roster.ingest_new_companies` or `module.__name__` suffix — **callers** pass the short context string; plan does not auto-derive from stack).
   - **No** `DEBUG_DETAIL_PREFIX` on header lines.

4. On `_PrefixedLogger`, add three methods (all no-op when `self._debug_flag` is False):

   - `debug_index(self, *, func: str, index: int, total: int, identifier: str, outcome: str) -> None`:
     - Build header via `format_debug_index_header(...)`.
     - Emit with `self._logger.info(header)` (not `debug()` — avoids `[ ~ ]` prefix and matches parent “visually distinct header”).

   - `debug_detail(self, message: str) -> None`:
     - Emit `self._logger.info(f"{DEBUG_DETAIL_PREFIX}{message}")`.

   - `debug_detail_block(self, text: str) -> None`:
     - For each line in `truncate_debug_content(text)`, call `debug_detail(line)`.

5. Do **not** remove or change `test()`, `debug()`, or `log_llm_batch_summary` in this stage.

6. Update the module docstring **Usage** block with a short example showing `get_logger(__name__, debug_flag=debug)` + `set_debug_flag(debug)` at function entry + `debug_index` / `debug_detail` / `debug_detail_block`.

⚠️ **Decision:** Headers and working detail use **INFO** when `debug_flag` is True (same volume class as today’s `[DEBUG]` INFO lines) so Susan’s console and `app_log` capture UAT traces without enabling global DEBUG level. `logger.debug()` / `[ ~ ]` remain for low-level developer noise, not the AST-538 operational contract.

## Stage 2: Code Rules contract (`docs/ASTRAL_CODE_RULES.md`)

**Done when:** §1.5 documents the full backend debug contract; a reader can implement a new batch loop without reading AST-538.

1. After the existing §1.5 bullets (logging.py / data layer / core / UI), add subsection **### 1.5.1 Backend debug logging (AST-538 / AST-554)** with these mandatory points:

   - **Trigger:** Backend functions accept `debug: bool` (default `False`) and pass it through the call chain (including Agent Ad Hoc backend runs). Emit contract lines **only** when `debug=True` via `get_logger(..., debug_flag=debug)` and/or `logger.set_debug_flag(debug)` before calling `debug_index` / `debug_detail` / `debug_detail_block`. **No** new debug-contract lines when `debug=False`.
   - **UI/React:** No debug-logging requirement (backend only).
   - **Helpers:** Use `_PrefixedLogger.debug_index`, `debug_detail`, `debug_detail_block` from `src/utils/logging.py`; use `truncate_debug_content` for long blobs before emission.
   - **Per-index header (style D):** One scannable header per batch item: `format_debug_index_header` shape — function context, universal `index N/M`, primary identifier, ` -> ` outcome. **Not** domain-specific counters in the format string (e.g. avoid `term 3/95`; use `index 3/95`).
   - **Working detail:** Substantive trace lines use prefix ` | ` (`DEBUG_DETAIL_PREFIX`) under the current index header.
   - **Long content:** Strings longer than **50 lines** → first **15**, line `<n lines omitted>` with **exact** `n = total_lines - 30`, then last **15** (implemented by `truncate_debug_content`).
   - **Batch end:** Aggregate `summary={...}` at batch end is allowed but **must not** replace per-index headers + detail for debug runs.
   - **Anti-patterns:** New `logger.info("[DEBUG] …")` in files touched for this epic; debug-contract emission without `debug=True`; logging full prompts/responses without truncation; debug noise in `src/data/` (still no log).
   - **Grandfather:** Existing `logger.info("[DEBUG] …")` in files **not** otherwise edited for AST-538 work may remain until that file is touched.
   - **Coexistence (not debug-gated):** `run_next hop: …` hop boundaries (AST-527/530); `log_llm_batch_summary` when `log_batch_id` is set; normal INFO/WARNING/ERROR for production paths.

2. Cross-link from §1.5 opening bullet (“Use `src/utils/logging.py`”) to §1.5.1.

## Stage 3: Component tests (`tests/component/utils/test_debug_logging.py`)

**Done when:** `pytest tests/component/utils/test_debug_logging.py` passes; tests assert **behavior** (line counts, gating, omit math), not full log copy.

1. Create `tests/component/utils/test_debug_logging.py` importing `truncate_debug_content`, `format_debug_index_header`, `get_logger`, and constants.

2. Class `TestTruncateDebugContent`:
   - `test_short_text_returns_all_lines`: 10 newline-separated lines → list length 10, no omitted marker.
   - `test_exactly_threshold_returns_all_lines`: 50 lines → length 50.
   - `test_over_threshold_inserts_omitted_marker`: 51 lines → length `15 + 1 + 15 = 31`; middle element exactly `"<21 lines omitted>"`.
   - `test_empty_string_returns_empty_list`.

3. Class `TestFormatDebugIndexHeader`:
   - `test_happy_path_shape`: `format_debug_index_header(func="roster.ingest", index=2, total=5, identifier="acme", outcome="passed")` equals `"roster.ingest index 2/5 acme -> passed"`.
   - `test_index_out_of_range_raises`: `index=0` or `index>total` raises `ValueError`.

4. Class `TestPrefixedLoggerDebugGating` (use `caplog` at INFO):
   - `test_debug_index_silent_when_flag_false`: `get_logger("test.ast554", debug_flag=False)` → `debug_index(...)` → zero records containing `index 1/1`.
   - `test_debug_index_emits_when_flag_true`: `debug_flag=True` → one record with substring `index 1/1` and ` -> `.
   - `test_debug_detail_silent_when_flag_false`: `debug_detail("hits=3")` → no record containing `DEBUG_DETAIL_PREFIX` stripped content.
   - `test_debug_detail_emits_with_prefix_when_true`: record message starts with `" | "`.
   - `test_debug_detail_block_respects_truncation`: 60-line string, `debug_flag=True` → count of emitted detail lines is 31 and one record contains `"<30 lines omitted>"`.

5. Do **not** add tests that snapshot entire multi-line Google CSE dumps or LLM payloads.

## Stage 4: Verification and handoff

**Done when:** Full component suite still green; Linear comment lists plan path and self-assessment; status **Plan Ready**.

1. Run `pytest tests/component/utils/test_debug_logging.py` from repo root (venv as Susan uses locally).

2. Run `pytest tests/component/utils/test_logging_batch.py` to confirm no regression on batch LLM logging.

3. Do **not** run dispatcher or roster integration tests for AC 4 spot-check — **AST-557** owns operational verification using this helper.

## Dependencies

| Ticket | Relationship |
|--------|----------------|
| **AST-538** | Parent definition and acceptance criteria source |
| **AST-557** | Blocked by AST-554 (Linear); consumes helper for AC 2 + operational AC 4 |
| **AST-556** | Blocked by AST-554; adds review rubric after contract exists |
| **AST-527 / AST-530** | Done — hop lines stay outside debug contract |

## Self-Assessment

**Scope:** `Single-Component` — Touches `src/utils/logging.py`, one new test module, and a focused §1.5.1 doc addition; no core dispatcher/roster/UI edits.

**Conf:** `high` — Parent AST-538 and dispatch child descriptions fix format, truncation math, and boundaries; implementation follows existing `_PrefixedLogger` / `get_logger(debug_flag=)` patterns.

**Risk:** `Medium` — Wrong gating or truncation would mislead UAT and flood logs, but this ticket does not rewire production batch paths until children adopt the helper.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| **§1.5 / §3.3** | Extends approved `utils` logging module only; no new `utils → data` import. |
| **§1.3 DRY** | Centralizes truncation and index/detail formatting; backfill children call helpers instead of copy-paste. |
| **§2.4 batch** | Contract documents per-index headers inside batch loops; does not change claim/clear semantics. |
| **§3.5 naming** | `debug_index` / `debug_detail` / `debug_detail_block` are verb-led, scoped to debug flag. |

No conflicts requiring `conf-!!-NONE`.

## Betty / test note (in build scope for AST-554)

Parent AC **7** requires new tests for helper gating and truncation on this ticket (not deferred). Betty may extend manifest after Code Complete; no log-string assertions per parent.

## Radia review (2026-06-03)

**Diff:** `origin/dev...origin/sub/AST-538/AST-554-debug-logging-contract-and-helper` @ `6c7a2e24`.

### What's solid

- **Plan fidelity:** Stages 1–3 delivered — constants, pure `truncate_debug_content` / `format_debug_index_header`, `_PrefixedLogger.debug_index` / `debug_detail` / `debug_detail_block`, §1.5.1 contract in `docs/ASTRAL_CODE_RULES.md`, and `tests/component/utils/test_debug_logging.py` (gating + truncation math only, no golden log prose). Matches parent AC 1, 3, 4 (helper gating), 7.
- **Scope boundaries:** No dispatcher/roster/inflow instrumentation, nav rename, or review-astral skill edits — correctly deferred to AST-557 / AST-555 / AST-556.
- **§1.5 / §3.3 (utils layer):** Changes confined to `src/utils/logging.py`; no new `utils → data` import; existing late-import DB handler unchanged.
- **§1.5 Logging (E1):** Emission stays on `_PrefixedLogger` / `get_logger`; contract lines use INFO when `debug_flag=True` as planned (distinct from `[ ~ ]` `debug()` / `test()`).
- **§1.3 DRY:** Truncation and index header formatting centralized for AST-557 adopters.
- **Self-Assessment alignment:** `scope-Single-Component` matches the diff footprint; no `conf-!!-NONE` gap.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **advisory** | `src/utils/logging.py` — `_PrefixedLogger.test()` vs new helpers | `test()` still emits `[ ~ ]`-prefixed INFO when `debug_flag=True`. New contract uses plain INFO headers + `DEBUG_DETAIL_PREFIX` detail. **AST-557** backfill should prefer `debug_index` / `debug_detail` / `debug_detail_block` for batch traces; reserve `test()` for legacy/low-level instrumentation until those call sites are touched. |
| **advisory** | `format_debug_index_header` | Empty-batch callers must skip `debug_index` when `total=0` — helper raises `ValueError` for `total < 1` (fail-fast per plan). Document in backfill loops. |
| **advisory** | Plan §Review (build stub) | Stale note that Stage 3 tests were not landed — superseded by `test-astral` (`test_debug_logging.py` on publish ref). |

No **fix-now** or **discuss** items for this ticket.

### Recommended actions

| Action | Owner | When |
| --- | --- | --- |
| Proceed to `resolve-astral` (no product changes required from review) | Ada | After Review Posted |
| Adopt helpers in `inflow_discovery` / batch paths per §1.5.1 | Hedy (AST-557) | After AST-554 lands on parent ftr |
| Add review-astral rubric rows for insufficient debug | Radia (AST-556) | After contract on parent integration branch |

## Resolution (2026-06-03)

**Review:** Radia @ `6c7a2e24` (product), doc @ `77cb5e9b` — **fix-now:** none; **discuss:** none.

**Actions:** Cherry-picked Radia review doc onto `dev-ada` via merge of `origin/sub/AST-538/AST-554-debug-logging-contract-and-helper`. No product commits — advisory items (`test()` vs new helpers, `total=0` guard) deferred to **AST-557** / backfill docs per review table.

**Publish:** `origin/sub/AST-538/AST-554-debug-logging-contract-and-helper` — resolution doc commit via Joan `store-resolve-commit`.

**Verification:** Betty manifest (§7.13zs) — `pytest tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py` green on `dev-ada`; §9a dry-run clean vs `origin/dev` and `origin/ftr/ast-538-improve-quality-of-debug-logging`.
