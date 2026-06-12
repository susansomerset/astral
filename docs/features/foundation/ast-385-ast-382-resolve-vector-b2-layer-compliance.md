# Plan: AST-385 — Resolve Vector B2 (layer compliance)

**Linear:** https://linear.app/astralcareermatch/issue/AST-385/ast-382-resolve-vector-b2-layer-compliance  
**Feature branch:** `betty/ast-385-ast-382-resolve-vector-b2-layer-compliance`

## Summary

Eliminate **B2** violations tracked in `debug/code_review_notes.md`: UI must not import `data`; external must not import `data`; resolve `utils`↔`data` tension in `logging.py` (see **AST-388** for file-local design); fix `server.py` bootstrap data import via **AST-383** when that lands. This ticket owns **integration verification** and any **residual** B2 not covered by **AST-321** / **AST-383**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/anthropic.py` (and any other external→data noted in notes) | If still importing `data` after **AST-321**/**AST-383**, refactor to core-mediated access per ASTRAL_CODE_RULES §2.5 | external |
| `src/ui/server.py` | Defer primary fix to **AST-383** (`core/bootstrap`); this ticket adds only a **guard comment** or removes dead import if 383 completes first | ui |
| `src/utils/logging.py` | Coordinate with **AST-388** — do not land conflicting refactors; if 388 moves DB sink boundary, B2 here is satisfied by that merge | utils |
| Remaining modules per `code_review_notes.md` | Close any B2 row still open after related tickets merge | mixed |

## Stage 1: Triage notes against other tickets

**Done when:** Spreadsheet-style list (in Linear comment or plan table) maps each B2 file in notes to **AST-321**, **AST-383**, **AST-388**, or **this ticket**.

1. Grep `debug/code_review_notes.md` for `**B2 — Layer compliance**`.
2. For each file, read the trailing `**Linear (conversation scope):**` line — if it cites **AST-321** or **AST-383**, mark **defer** until that PR merges.
3. Anything left marked **AST-385** is in-scope for direct code changes on the build branch.

## Stage 2: Implement residual B2 fixes

**Done when:** `rg "from src.data"` from forbidden layers (per rules: `src/ui/` except scripts, `src/external/`) returns zero matches, excluding paths Susan explicitly exempts.

1. For each **AST-385** row, apply the minimal layer-correct pattern: UI → new core facade → data; external → core → data.
2. After **AST-321** merge, re-run grep; fix stragglers (e.g. `anthropic` timesheet paths called out in ticket description).

## Stage 3: Verification

**Done when:** Import-linter or Susan’s manual equivalent: start Flask app + one dispatcher tick path without `ImportError`.

1. Run existing server start command from `docs` or `scripts/start_server.py` as documented for local dev.
2. Document in PR description which deferred tickets were assumed merged.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches multiple layers and depends on sibling tickets landing order.

**Conf:** `LOW` — Sequencing with **AST-321** / **AST-383** / **AST-388** dominates; implementer must rebase frequently.

**Risk:** `HIGH` — Layer mistakes break production imports or create subtle circular dependencies.

## Plan vs ASTRAL_CODE_RULES

Strict §3.3 import table is the acceptance bar; do not weaken `api_admin` exemption without Susan decision (notes already call out **api_admin**).

## Review (stub)

**Branch:** `betty/ast-385-ast-382-resolve-vector-b2-layer-compliance`  
**Publish commit:** latest **Built by Betty** comment on the Linear issue.

## Resolution (2026-05-11 — f-resolve-linear, Betty)

**Radia `e-review-linear`:** fix-now **0**. **Resolve pass:** no additional product changes required.

Advanced to **User Testing** per `docs/ASTRAL_TEAM_WORKFLOW.md`.
