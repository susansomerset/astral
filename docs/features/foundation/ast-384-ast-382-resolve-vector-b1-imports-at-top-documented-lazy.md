# Plan: AST-384 — Resolve Vector B1 (imports at top / documented lazy imports)

**Linear:** https://linear.app/astralcareermatch/issue/AST-384/ast-382-resolve-vector-b1-imports-at-top-documented-lazy-imports  
**Feature branch:** `betty/ast-384-ast-382-resolve-vector-b1-imports-at-top-documented-lazy`

## Summary

Close every **B1** finding in `debug/code_review_notes.md`: either move imports to module top **or** keep a function-scoped import with a **one-line comment** citing circular-import / heavy-deps rationale per rubric. Overlap with **AST-321** on `api_system.py` — after **AST-321** lands, re-verify this ticket’s B1 acceptance (no nested `src.core.agent` imports without comment if still lazy).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_system.py` | For `from src.core.agent import ...` at lines ~137 and ~148: either hoist to top if **AST-321** refactor removes cycle, or add adjacent `# lazy: ...` comments documenting the import graph reason | ui |
| `src/core/roster.py` | For `from bs4 import BeautifulSoup` at ~837 and ~877: add `# lazy: bs4` rationale (large dep / optional path) or hoist if no cycle | core |
| `src/utils/formatting.py` | For `BeautifulSoup` / `Tag` imports at ~113 and ~130: same treatment | utils |
| `debug/code_review_notes.md` | Append one-line “Resolved AST-384” note per file **only if** Susan wants audit trail in debug (optional — default: **do not** append marketing text; resolution is git history). Skip unless Susan requests. | debug |

⚠️ **Decision:** Do **not** hoist `bs4` to module top in `formatting.py` if that pulls BeautifulSoup into every import of formatting; prefer documented lazy import with comment referencing optional HTML parse path.

## Stage 1: `api_system.py` B1

**Done when:** No nested `from src.core.agent import` without an explanatory comment, or imports are at file top with successful cold import of Flask app (no circular import on `python -c` smoke test Susan uses).

1. Read current `src/ui/api/api_system.py` after fetching latest `origin/dev` on the build branch.
2. If **AST-321** is merged and moved agent helpers: delete lazy imports entirely if top-level imports are cycle-free.
3. Else: leave imports inside functions but add a single block comment above **each** lazy import: `# B1 lazy import: <one sentence — e.g. avoids circular import ui.api → core.agent → …>`.

## Stage 2: `roster.py` lazy bs4

**Done when:** Both BeautifulSoup import sites have matching `# lazy:` comments or imports moved to top with `rg "from bs4"` showing only top-level in file.

1. Open `src/core/roster.py` at both handler locations (~837, ~877).
2. Add comment tying lazy load to optional HTML parsing in roster path (why top-level would hurt cold start or create cycles — pick accurate reason after reading call graph).

## Stage 3: `formatting.py` lazy bs4

**Done when:** Same as Stage 2 for lines ~113 and ~130; `Tag` import documented if still lazy.

1. Mirror roster pattern; ensure comment distinguishes `Tag` vs `BeautifulSoup` if split across lines.

## Self-Assessment

**Scope:** `Single-Component` — Three Python modules, all import hygiene.

**Conf:** `high` — Notes list exact files/lines; rubric B1 is unambiguous.

**Risk:** `low` — Worst case is import cycle discovered at runtime; smoke import tests catch it before merge.

## Plan vs ASTRAL_CODE_RULES

§1.2 / §3.3: Do not “fix” B2 data imports in `api_system` on this ticket — that belongs to **AST-321** / **AST-385**.

## Resolution (2026-05-11 — f-resolve-linear, Betty)

**Radia `e-review-linear`:** fix-now **0**. **Resolve pass:** no additional product changes required.

Advanced to **User Testing** per `docs/ASTRAL_TEAM_WORKFLOW.md`.
