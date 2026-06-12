# Plan: AST-388 — Resolve `src/utils/logging.py` review findings (B2 + D2)

**Linear:** https://linear.app/astralcareermatch/issue/AST-388/ast-382-resolve-srcutilsloggingpy-review-findings-b2-d2  
**Feature branch:** `betty/ast-388-ast-382-resolve-srcutilsloggingpy-review-findings-b2-d2`

## Summary

Reach an explicit reviewed design for **B2** (late `database` import from utils) and **D2** (`except Exception: pass` in the DB log handler) per `debug/code_review_notes.md`. Either justify in-module + short architecture note in `docs/ASTRAL_CODE_RULES.md`, **or** refactor sink boundary (e.g. optional handler registration from core after startup) so rubric and runtime align.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/logging.py` | Implement chosen design for `_DatabaseLogHandler.emit` and `_flush_buffer` error paths; adjust late import strategy | utils |
| `src/core/dispatcher.py` (or bootstrap from **AST-383**) | If sink moves: register DB flush hook from core after `database` import safe | core |
| `docs/ASTRAL_CODE_RULES.md` | §1.5 or new subsection documenting approved exception to strict utils-import rule for logging sink, and D2 rationale if swallow remains | docs |

⚠️ **Decision:** Prefer **minimal** change: keep late import but add `docs` paragraph + replace bare `pass` with `sys.stderr` fallback or `logging.lastResort` handler so failure is **visible** without crashing caller — only if Susan agrees noise level.

## Stage 1: Design choice (blocking)

**Done when:** Linear comment on **AST-388** with Susan’s picked option **A** (document + stderr fallback), **B** (move DB writes to core-owned listener), or **C** (hybrid).

1. Draft 2–3 options in PR description referencing rubric D2 severity.
2. If Susan does not reply, implement **A** as default (smallest code movement).

## Stage 2: Code — D2 mitigation

**Done when:** No bare `except Exception: pass` without adjacent comment explaining **and** compensating visibility (stderr line, counter increment, or re-raise on non-logging errors).

1. In `emit`, on failure formatting buffer entry: choose between degrade-to-stderr vs drop-with-counter — **document** in code.
2. In `_flush_buffer`, on `add_log_entry` failure: at minimum log to stderr with record count; never silent empty except.

## Stage 3: Code — B2 alignment

**Done when:** Either `logging.py` has an approved architecture note in `ASTRAL_CODE_RULES.md` **or** utils no longer imports `data` at runtime (sink moved).

1. If moving sink: delete late import from utils; add `register_db_log_handler()` in core called from dispatcher startup path (coordinate **AST-383** if that owns startup ordering).
2. If keeping sink: extend `ASTRAL_CODE_RULES.md` §3.3 with explicit **exception** bullet for `logging.py` only, linking to this ticket.

## Self-Assessment

**Scope:** `minor` — Single production module plus small doc touch (unless sink moves — then Medium).

**Conf:** `Medium` — Architectural tradeoff needs Susan sign-off on observability vs crash safety.

**Risk:** `HIGH` — Logging path touches every batch; regressions hide production incidents.

## Plan vs ASTRAL_CODE_RULES

Must end in a state where rubric D2 and layer story are not in silent contradiction.

## Review (stub)

**Branch:** `betty/ast-388-ast-382-resolve-srcutilsloggingpy-review-findings-b2-d2`  
**Publish commit:** latest **Built by Betty** comment on the Linear issue.
