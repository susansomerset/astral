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
