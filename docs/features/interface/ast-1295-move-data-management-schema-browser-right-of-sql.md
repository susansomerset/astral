<!-- linear-archive: AST-1295 archived 2026-08-19 -->

## Linear archive (AST-1295)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1295/move-data-management-schema-browser-right-of-sql-move-table-lookup-and  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1291 — Move table lookup and field lookup objects on Data Management page  
**Blocked by / blocks / related:** parent: AST-1291

### Description

## What this implements

Relocate the tables + fields lookup grouping from the left of the SQL workbench to the right of the SQL input on Data Management. Preserve selection and display behavior; do not own upsert, SQL execution, or other Admin pages.

## Acceptance criteria

- [X] On Admin → Data Management, the tables lookup panel is visually to the **right** of the SQL input window (not to the left).
- [X] After selecting a table, the fields lookup for that table appears with the tables lookup on the **right** of the SQL input (same grouping as today, mirrored side).
- [X] SQL history controls, Run, result display, Copy Output, and Table Upsert still work as before this change.
- [X] No other Admin page layout changes ship in this epic.

## Boundaries

Does not own upsert, SQL execution, or other Admin pages. Does not change schema discovery or result-grid presentation beyond layout adjacency.

## In scope

- [X] `astral.standards.in-scope-only` — layout adjacency only on Data Management; no feature creep
- [X] `astral.ui.frontend-file-placement` — edit stays in existing `AdminDataManagement.tsx` page placement
- [X] `astral.ui.naming-conventions` — no rename churn
- [X] `astral.layers.ui-config-driven-business-logic` — no new frontend business rules while moving chrome

## Considered but excluded

- [X] `astral.git.engineer-test-tree-ban` — engineers do not edit `tests/` / bible; Betty owns any test updates if DOM-order assertions appear later
- [X] Admin API / SQL execution / upsert paths (`src/ui/api/api_admin.py`) — behavior unchanged; layout-only
- [X] Other Admin pages / nav shell — out of epic boundaries (responsive nav is AST-1284 / AST-1286)
- [X] CSS / `App.css` — this page uses inline flex styles; no shared stylesheet change planned

## Notes for planning

Layout-only slice. Plan: `docs/features/interface/ast-1295-move-data-management-schema-browser-right-of-sql.md`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1291-move-table-lookup-and-field-lookup-objects-on-data`, child `sub/AST-1291/AST-1295-move-data-management-schema-browser-right-of-sql`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-10T02:02:13.610Z
[code-rubric] revision=2
**Overall:** CLEAN
No fix-now, no discuss. Pure sibling JSX reorder; commit provenance clean (src/tests/docs split).
— Radia

#### betty — 2026-08-10T01:57:27.283Z
1. **Existing §6c regression (AC3):** `tests/component/frontend/pages/test_AdminDataManagement.test.tsx` — sql run / copy / schema click → fields / upsert modal + toast / sql-error paths (labels + behavior).
2. **New (AC1–AC2 layout):** same file — `AST-1295: Tables/Fields schema browser follows SQL textarea in DOM (right of workbench)` (document order = visual right under default flex row).

**Broken / obsolete:** none.
**Integration:** none — chrome reorder only.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminDataManagement.test.tsx
```

`origin/sub/AST-1291/AST-1295-move-data-management-schema-browser-right-of-sql` @ `df604923` (`merge-tests(AST-1295): origin/tests 3b99c01d`)

`docs/test-bible/frontend/pages.md` shasum: `8f5fe992c32dfa7d0d5e2df41fd82375fca0600d`

— Betty

#### joan — 2026-08-10T01:52:43.556Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1295
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1291/AST-1295-move-data-management-schema-browser-right-of-sql` @ `8b49545ef33cdc15cdaf1b16cae1cd365c9852b7`

## Traceability
AC1→S1; AC2→S1; AC3→S1; AC4→S1

No `fix-now` findings. Self-assessment (minor / high / low) matches a one-file sibling reorder in `AdminDataManagement.tsx`. Parent Purpose/Functional scope/Boundaries respected; statutes cited on the child plus the universal orchestration set scored in-session (R1–R3) with no violations.

— Joan
context_tokens≈52000

#### katherine — 2026-08-10T01:50:46.716Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1291/AST-1295-move-data-management-schema-browser-right-of-sql/docs/features/interface/ast-1295-move-data-management-schema-browser-right-of-sql.md

**Scope:** minor — one React page file; sibling reorder in the existing workbench flex row; no API/config.

**Conf:** high — left-then-right JSX in `AdminDataManagement.tsx` is explicit; flipping Main query panel before Schema browser panel is the whole deliverable.

**Risk:** low — wrong order only misplaces chrome on this Admin page; SQL/upsert/history paths stay untouched if Stage 1 steps 3–4 are followed literally.

---

# AST-1295 — Move Data Management schema browser right of SQL

**Linear:** [AST-1295](https://linear.app/astralcareermatch/issue/AST-1295/move-data-management-schema-browser-right-of-sql-move-table-lookup-and)  
**Parent:** [AST-1291](https://linear.app/astralcareermatch/issue/AST-1291/move-table-lookup-and-field-lookup-objects-on-data-management-page)  
**Publish ref:** `sub/AST-1291/AST-1295-move-data-management-schema-browser-right-of-sql`

On Admin → Data Management, the tables + fields schema browser sits in a flex row to the **left** of the SQL workbench, stealing horizontal space from the query textarea. This ticket is layout-only: keep the same schema-browser grouping (tables list, then fields for the selected table) and move that panel to the **right** of the SQL input (and its history controls / Run / results). Do not change schema discovery SQL, selection behavior, upsert, history, Copy Output, result-grid presentation, or any other Admin page.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminDataManagement.tsx` | In the workbench flex row, place the main query panel before the schema browser panel so the browser renders to the right of SQL | ui |

No API, config, CSS module, routes, upsert modal, or other Admin page files.

## Stage 1: Reorder schema browser to the right of the SQL workbench

**Done when:** On Admin → Data Management, the Tables list (and Fields for the selected table when a table is selected) appear visually to the right of the SQL textarea and history controls; selecting a table still loads that table’s fields in the same right-side grouping; Run, result grid, Copy Output, SQL history ▲/▼, and Table Upsert behave as before this change.

1. In `src/ui/frontend/src/pages/AdminDataManagement.tsx`, locate the workbench flex row that currently wraps two children in this order:
   - Schema browser panel (`{/* Schema browser panel */}` — `width: 200`, Tables list + conditional Fields block)
   - Main query panel (`{/* Main query panel */}` — history buttons, SQL textarea, Run / Copy Output, result table)

2. Reorder those two children so the **Main query panel** comes first and the **Schema browser panel** comes second inside the same parent:
   ```tsx
   <div style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
     {/* Main query panel */}
     <div style={{ flex: 1, minWidth: 0 }}>
       {/* existing history + textarea + Run/Copy + result grid — unchanged */}
     </div>

     {/* Schema browser panel */}
     <div style={{ width: 200, flexShrink: 0, display: "flex", flexDirection: "column", gap: 8 }}>
       {/* existing Tables label/list + Fields — {selectedTable} block — unchanged */}
     </div>
   </div>
   ```
   Because the parent uses default `flex-direction: row`, DOM order is visual left-to-right: SQL workbench left, schema browser right.

3. Do **not** change:
   - Schema browser state (`tables`, `selectedTable`, `fields`) or either `useEffect` that loads `sqlite_master` / `PRAGMA table_info`
   - Click handler that sets `selectedTable`
   - Tables / Fields markup, styles (`width: 200`, scroll maxHeights, PK/type display), or labels
   - SQL history, `handleRun`, result grid, Copy Output, Toast, or Table Upsert block / Modal above the flex row
   - Page `maxWidth: 1200`, outer padding, or heading
   - Any other file under `src/ui/frontend/src/pages/` or Admin routes

4. Do **not** introduce `flex-direction: row-reverse`, CSS order tricks, or a new wrapper component — only sibling reorder in this file.

5. Do **not** edit `tests/`, `docs/test-bible/**`, or `docs/ASTRAL_TEST_BIBLE.md` (engineer test-tree ban). Existing component coverage for schema click / upsert continues to target labels and text, not left/right DOM order.

⚠️ **Decision:** Sibling reorder in the existing flex row is sufficient. No CSS reverse and no extraction of a new component — keeps the change to one file and matches the epic’s “placement only” boundary.

## Self-Assessment

**Scope:** `minor` — one React page file; reorder two siblings in an existing flex row; no API or config.

**Conf:** `high` — current layout is explicit left-then-right JSX in `AdminDataManagement.tsx`; flipping sibling order is the entire deliverable.

**Risk:** `low` — wrong order would only misplace chrome on this Admin page; SQL/upsert paths are untouched. Residual risk is accidental edits to handlers while moving JSX — Stage 1 steps 3–4 forbid that.

## Code rules self-review

- **§1.3 DRY:** No new helpers; reuse existing panels as-is.
- **§2.1 config:** No config keys; layout chrome stays inline styles (existing pattern on this page).
- **§2.4 / §2.6:** N/A (no batch / state machine).
- **§3.3 imports:** No import changes.
- **§3.5 naming / frontend-file-placement:** Stay in `src/ui/frontend/src/pages/AdminDataManagement.tsx`; no rename.
- **`astral.layers.ui-config-driven-business-logic`:** No new frontend business rules; selection + discovery SQL unchanged.
- **`astral.standards.in-scope-only`:** Layout adjacency only; upsert / SQL execution / other Admin pages excluded.

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1291/AST-1295-move-data-management-schema-browser-right-of-sql`  
**Product commits:** `d2f2e1a9` (schema browser sibling reorder — right of SQL)

## Radia review

[code-rubric] revision=2

**Rubric:** code-rubric.v2
**Publish ref tip:** `df604923`
**Overall:** CLEAN

**Full-set sweep:** all 64 active statutes scored in-session (18 universal + 46 scoped) against `git diff origin/dev...origin/sub/AST-1291/AST-1295-move-data-management-schema-browser-right-of-sql`. No `violates`, no `needs-discussion`. Scoped statutes outside `ui`/`docs` layers (batch, dispatch, state, seed, config, debug, agent, data) score `not-applicable` — diff touches no matching paths. No plan-rubric verdict attached (Notes, not a block).

**What's solid:** Diff is exactly the planned sibling reorder — Main query panel div moved before the Schema browser panel div inside the same unchanged flex-row parent; no other JSX, styles, handlers, `useEffect`s, or state touched (verified by reading the full surrounding render block). Commit provenance is clean and matches `orch.git.commit-vocabulary` / `astral.git.engineer-test-tree-ban` / `astral.git.betty-no-src-or-features`: `code(AST-1295)` touches only `src/ui/frontend/src/pages/AdminDataManagement.tsx`; `test(AST-1295)` + the single `merge-tests(AST-1295)` SHA touch only `tests/component/**` and `docs/test-bible/**`; the plan/review `docs(AST-1295)` commits touch only this file under `docs/features/`. New component test asserts DOM order via `compareDocumentPosition` against the SQL textarea, matching the plan's "Done when." No API, config, CSS module, or other Admin page files touched, matching the epic's placement-only boundary.

**Findings:** none.

**Pattern conformance:**

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan cites no `pattern.*` id; diff shape (pure sibling JSX reorder) doesn't match any approved catalog `# Problem` (checked `pattern.ui.admin-endpoint` — that pattern governs new admin HTTP surfaces, not layout order; not a match) |

**Plan adherence:** Diff matches the Files Changed table and Stage 1 steps exactly, including the explicit "Decision" to keep a sibling reorder (no `row-reverse`, no new wrapper component). Self-Assessment `Scope: minor` / `Conf: high` / `Risk: low` matches the diff's real footprint — one file, one JSX move.

**Cross-ticket boundary:** Relations: none. No smuggled scope from AST-1291 siblings; schema-browser state/handlers, SQL history, Run, result grid, Copy Output, and Table Upsert are all byte-identical to pre-diff.

## Frame diff

(none — ticket description AC/scope table already accurate)

context_tokens≈45000

— Radia

## Resolution

**Date:** 2026-08-10  
**Review:** `[code-rubric] revision=2` — Overall CLEAN (Radia). No fix-now, no discuss, no advisory product work.

**Actions:** None required beyond intake of Radia’s `docs(AST-1295): Radia review — clean` (`ad9c111b`) via `sync-child` merge of `origin/<publish-ref>`. Product tip remains `d2f2e1a9` (schema browser sibling reorder).
