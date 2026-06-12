# Plan: AST-386 — Resolve Vector E1 (project logger; no print / bare logging)

**Linear:** https://linear.app/astralcareermatch/issue/AST-386/ast-382-resolve-vector-e1-project-logger-no-print-bare-logging  
**Feature branch:** `betty/ast-386-ast-382-resolve-vector-e1-project-logger-no-print-bare`

## Summary

Replace `print()` and bare `import logging` / `getLogger` with `from src.utils.logging import get_logger` per rubric **E1** and `docs/ASTRAL_CODE_RULES.md` §1.5 / §2.1 logging rules. Primary surface area from notes: `playwright.py`, `anthropic.py`, `agent.py`, `consult.py`, `dispatcher.py`, `config.py`, `roster.py`, `api_system.py`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/playwright.py` | Replace `print(...)` with `logger = get_logger(__name__)` and level-appropriate calls (`debug`/`info`/`warning`); preserve semantics of user-visible diagnostics | external |
| `src/external/anthropic.py` | Remove stdlib-only logging where project logger suffices; keep SDK integration points documented if stdlib is required | external |
| `src/core/agent.py` | Remove parallel `import logging` where `get_logger` covers needs | core |
| `src/core/consult.py` | Same | core |
| `src/core/dispatcher.py` | Same | core |
| `src/core/roster.py` | Same | core |
| `src/utils/config.py` | Replace `getLogger` pattern with `get_logger` unless startup-before-logging-init edge case — if edge case, one comment block at top | utils |
| `src/ui/api/api_system.py` | Replace `_log = logging.getLogger` with `get_logger` | ui |

⚠️ **Decision:** `src/utils/logging.py` itself is exempt from E1 per rubric; do not “fix” that file here (**AST-388** owns its B2/D2).

## Stage 1: `playwright.py` print elimination

**Done when:** `rg "print\\("` on `src/external/playwright.py` returns zero matches (or only inside `if __name__` guard Susan explicitly keeps).

1. Add module-level `logger = get_logger(__name__)` once at top (after imports per ASTRAL rules).
2. Map each `print` to the closest level: cookie noise → `debug`; milestone → `info`.
3. Manually tail logs during one short Playwright smoke if Susan has a script; else rely on code review.

## Stage 2: Core + utils stdlib logging alignment

**Done when:** `rg "^import logging$|logging\\.getLogger"` in listed core/utils files returns no stray usage except documented exceptions.

1. For each file in the table, convert to `get_logger`.
2. In `config.py`, if import order risks circular import with `logging.py`, use **lazy get_logger inside functions** only where needed — **and** add B1-style comment (cross-ticket: **AST-384** owns B1 doc; here prefer top-level if safe).

## Stage 3: `anthropic.py` SDK path

**Done when:** Missing-SDK messages go through project logger; no `print` for user-facing errors.

1. Find the “missing SDK” branch noted in ticket; swap to `logger.error(...)`.

## Stage 4: `api_system.py`

**Done when:** `_log` uses `get_logger(__name__)`.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Many modules across external/core/utils/ui.

**Conf:** `high` — Notes enumerate targets; pattern is uniform.

**Risk:** `Medium` — Log volume or level shifts could obscure ops signals; keep levels faithful to old `print` intent.

## Plan vs ASTRAL_CODE_RULES

§1.5: Use `src/utils/logging.py` only; data layer still does not log.

## Review (stub)

**Branch:** `betty/ast-386-ast-382-resolve-vector-e1-project-logger-no-print-bare`  
**Publish commit:** latest **Built by Betty** comment on the Linear issue.

## Resolution (2026-05-11 — f-resolve-linear, Betty)

**Radia `e-review-linear`:** fix-now **0**. **Resolve pass:** no additional product changes required.

Advanced to **User Testing** per `docs/ASTRAL_TEAM_WORKFLOW.md`.
