# AST-657 — UAT: First two data columns not frozen (only action column)

**Linear:** [AST-657 — UAT: First two data columns not frozen (only action column) (Table Layout fix)](https://linear.app/astralcareermatch/issue/AST-657/uat-first-two-data-columns-not-frozen-only-action-column-table-layout)  
**Parent:** [AST-633 — Table Layout fix](https://linear.app/astralcareermatch/issue/AST-633/table-layout-fix) (AC reference only)  
**Publish ref:** `origin/sub/AST-633/AST-657-uat-freeze-first-n-data-columns` (origin only)

## Summary

Susan UAT (2026-06-15): on wide ListPage tables with horizontal scroll, the **row action** column stays sticky on the right, but the leftmost **N=2 data columns** scroll away. AST-647 wired freeze classes and `stickyLeftPx`; AST-652 switched default layout to **`table-layout: auto`**. Offset math still uses user-resized `colWidths` or a **120px fallback** per column and a **40px** checkbox constant — not the **rendered** widths under autosize. Wrong cumulative `left` values break horizontal stickiness for data columns; `right: 0` on the action column needs no offset chain, so it still appears to work. This UAT bug measures real header cell widths after layout and feeds them into `stickyLeftPx`, for **ListPage** and **AdminScheduledActions**. No change to frozen **N**, autosize default, truncation, sticky header row, or backend config.

**Builds on:** [AST-647 plan](ast-647-list-table-layout-freeze-sticky-tooltips.md), [AST-652 plan](ast-652-uat-remove-force-fit-autosize-list-table-columns.md) — patch delta only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/listTableLayout.ts` | Add width merge + measure helpers; extend `stickyLeftPx` to accept measured checkbox width | ui |
| `src/ui/frontend/src/lib/useListTableColumnMeasure.ts` | Shared `useLayoutEffect` hook: measure `<th>` / checkbox widths after paint | ui |
| `src/ui/frontend/src/components/ListPage.tsx` | Wire measurement hook; pass merged widths into `frozenCellStyle` | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Wire same hook for bespoke phase tables | ui |
| `src/ui/frontend/src/App.css` | Ensure frozen header cells keep horizontal + vertical sticky (explicit `left`/`top` on combined selector) | ui |

**QA manifest (Betty — not engineer commits):** extend `test_ListPage_listTableLayout.test.tsx` to assert frozen data `<th>` at index 1 has inline `style.left` strictly greater than checkbox `<th>` when `list_table_frozen_data_columns: 2`; optional jsdom test that `mergeWidthsForSticky` prefers user-resized width over measured. Manual: Agent Timesheets — scroll right; first two data columns + checkbox stay visible; action column stays on right.

**Out of scope:** frozen-column count default, autosize / remove force-fit (AST-652), sticky header row, 30-char truncation/tooltips, config keys, column reorder/resize/localStorage semantics, job phase grouped tables beyond Scheduled Actions.

---

## Stage 1: Measured-width helpers and shared hook

**Done when:** `listTableLayout.ts` exports merge/measure helpers and updated `stickyLeftPx`; `useListTableColumnMeasure.ts` exists; `cd src/ui/frontend && npx tsc -b --noEmit` passes; no ListPage wiring yet.

1. In `src/ui/frontend/src/lib/listTableLayout.ts`, add:

   ```typescript
   /** User-resized width wins; else measured; stickyLeftPx still uses 120 fallback when both missing. */
   export function mergeWidthsForSticky(
     persisted: Record<string, number>,
     measured: Record<string, number>,
   ): Record<string, number> {
     const out: Record<string, number> = { ...measured }
     for (const [key, w] of Object.entries(persisted)) {
       if (typeof w === "number" && w > 0) out[key] = w
     }
     return out
   }

   export function measureListTableColumnWidths(
     table: HTMLTableElement,
     orderedKeys: string[],
     hasCheckbox: boolean,
   ): { checkboxWidthPx: number; dataWidths: Record<string, number> } {
     const headerRow = table.tHead?.rows[0]
     if (!headerRow) return { checkboxWidthPx: LIST_TABLE_CHECKBOX_WIDTH_PX, dataWidths: {} }
     let colIdx = 0
     let checkboxWidthPx = LIST_TABLE_CHECKBOX_WIDTH_PX
     if (hasCheckbox) {
       checkboxWidthPx = headerRow.cells[colIdx]?.offsetWidth ?? LIST_TABLE_CHECKBOX_WIDTH_PX
       colIdx += 1
     }
     const dataWidths: Record<string, number> = {}
     for (const key of orderedKeys) {
       const cell = headerRow.cells[colIdx]
       if (cell && cell.offsetWidth > 0) dataWidths[key] = cell.offsetWidth
       colIdx += 1
     }
     return { checkboxWidthPx, dataWidths }
   }
   ```

2. Change `stickyLeftPx` signature to accept optional measured checkbox width:

   ```typescript
   export function stickyLeftPx(
     dataColIndex: number,
     colWidths: Record<string, number>,
     orderedKeys: string[],
     hasCheckbox: boolean,
     frozenDataColumns: number,
     checkboxWidthPx: number = LIST_TABLE_CHECKBOX_WIDTH_PX,
   ): number | null {
     if (dataColIndex >= frozenDataColumns) return null
     let left = hasCheckbox ? checkboxWidthPx : 0
     for (let i = 0; i < dataColIndex; i++) {
       const key = orderedKeys[i]
       left += colWidths[key] ?? 120
     }
     return left
   }
   ```

3. Create `src/ui/frontend/src/lib/useListTableColumnMeasure.ts`:

   ```typescript
   import { useLayoutEffect, useState, type RefObject } from "react"
   import { mergeWidthsForSticky, measureListTableColumnWidths } from "./listTableLayout"

   export function useListTableColumnMeasure(
     tableRef: RefObject<HTMLTableElement | null>,
     orderedKeys: string[],
     hasCheckbox: boolean,
     persistedWidths: Record<string, number>,
     deps: unknown[],
   ) {
     const [checkboxWidthPx, setCheckboxWidthPx] = useState(40)
     const [mergedWidths, setMergedWidths] = useState<Record<string, number>>(() =>
       mergeWidthsForSticky(persistedWidths, {}),
     )

     useLayoutEffect(() => {
       const table = tableRef.current
       if (!table) return
       const { checkboxWidthPx: cb, dataWidths } = measureListTableColumnWidths(
         table,
         orderedKeys,
         hasCheckbox,
       )
       setCheckboxWidthPx(cb)
       setMergedWidths(mergeWidthsForSticky(persistedWidths, dataWidths))
     }, [tableRef, orderedKeys, hasCheckbox, persistedWidths, ...deps])

     return { checkboxWidthPx, mergedWidths }
   }
   ```

   ⚠️ **Decision:** Measure from **header row `offsetWidth`** after autosize layout — same source ListPage resize uses (`th.offsetWidth`). Re-run on `deps` (row count, col order, persisted widths) so offsets track content width changes without waiting for user resize.

4. Update existing `test_listTableLayout.test.ts` `stickyLeftPx` call sites to pass explicit checkbox width when asserting checkbox offset (behavior unchanged when default arg used).

**Ritual:** `code(AST-657): measured-width helpers for frozen column sticky offsets`

---

## Stage 2: ListPage and Scheduled Actions wiring + CSS

**Done when:** ListPage and AdminScheduledActions pass measured merged widths into `stickyLeftPx`; horizontal scroll keeps checkbox + first **N** data columns visible on wide tables; action column unchanged; `npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/components/ListPage.tsx`:
   - Import `useListTableColumnMeasure` from `../lib/useListTableColumnMeasure`.
   - Add `const tableRef = useRef<HTMLTableElement>(null)` and attach `ref={tableRef}` on `<table className="list-page-table">`.
   - After `colOrder` / `showCheckboxes` / `colWidths` are defined, call:
     ```typescript
     const { checkboxWidthPx, mergedWidths } = useListTableColumnMeasure(
       tableRef,
       colOrder,
       showCheckboxes,
       colWidths,
       [sorted.length, frozenN, truncateChars],
     )
     ```
   - In `frozenCellStyle`, replace `stickyLeftPx(dataColIndex, colWidths, colOrder, showCheckboxes, frozenN)` with:
     ```typescript
     stickyLeftPx(dataColIndex, mergedWidths, colOrder, showCheckboxes, frozenN, checkboxWidthPx)
     ```
   - Checkbox `<th>` / `<td>`: keep `style={{ left: 0 }}` (unchanged).
   - Do **not** change sort, drag-reorder, resize handlers, or localStorage.

2. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`:
   - Import `useListTableColumnMeasure` and add `tableRef` on each phase `<table>` (one ref per table is fine if only one phase panel expanded — use ref on the table inside the mapped phase block; if multiple tables mount, use a callback ref or measure per-table ref keyed by phase — prefer **one ref on the first rendered phase table** only when tests use single phase; for production, attach ref to **each** phase `<table>` and run measure in that table's parent — simplest: duplicate hook call per phase table with ref inside the `.map` callback using `useRef` map keyed by phase id is **not** allowed in map; instead extract **`PhaseTable`** inner component that owns its own `tableRef` + hook).
   - Extract a small inner component `ScheduledPhaseTable` in the same file (no new file) that receives phase rows + sort props and calls `useListTableColumnMeasure(tableRef, [...DATA_COL_KEYS], false, {}, [rows.length, frozenN])`.
   - Update `scheduledFrozenStyle` to accept `mergedWidths` and `checkboxWidthPx` (always false checkbox → width unused) and call `stickyLeftPx(colIndex, mergedWidths, [...DATA_COL_KEYS], false, frozenN)`.

3. In `src/ui/frontend/src/App.css`, after `.list-page-table thead th.list-table-cell-frozen` block (~line 447), add:

   ```css
   .list-page-table thead th.list-table-cell-frozen {
     position: sticky;
     top: 0;
   }

   .list-page-table tbody td.list-table-cell-frozen {
     position: sticky;
   }
   ```

   ⚠️ **Decision:** Re-declare `position: sticky` on frozen header/body cells so horizontal `left` from inline styles is not lost when combined with the global `thead th { position: sticky; top: 0 }` rule under autosize. Do **not** change `border-collapse` in this bug pass unless UAT still fails after measured offsets.

4. Manual verification: **Admin Agent Timesheets** — wide table, scroll right — checkbox + first two data columns remain visible; action column stays right.

**Ritual:** `code(AST-657): wire measured sticky offsets on ListPage and Scheduled Actions`

---

## Self-Assessment

**Scope:** `minor` — Frontend layout helpers + ListPage + one bespoke adopter + small CSS clarification; no backend or config changes.

**Conf:** `Medium` — Root cause (autosize vs 120px fallback offsets) is clear and matches Susan's repro; `useLayoutEffect` measurement is a standard fix but needs correct re-measure triggers when columns reorder or resize.

**Risk:** `Medium` — ListPage is widely consumed; incorrect measurement timing could misalign frozen columns on first paint, but presentation-only and resize/localStorage paths stay intact.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Shared `useListTableColumnMeasure` + layout helpers avoid duplicating measure logic in ListPage and Scheduled Actions |
| §2.1 config | No new config keys; `frozenN` still from `UI_CONFIG` via existing `resolveFrozenDataColumns` |
| §3.3 imports | New hook under `src/ui/frontend/src/lib/`; no cross-layer violations |
| §3.5 naming | camelCase TS helpers match existing `listTableLayout` style |
| §1.5.1 | No backend debug logging |

No conflicts requiring `conf-!!-NONE`.

---

## Execution contract

- Stages 1 → 2 in order; one `code()` commit per stage on epic worktree; publish each to **`origin/sub/AST-633/AST-657-uat-freeze-first-n-data-columns`** via `git push origin HEAD:sub/AST-633/AST-657-uat-freeze-first-n-data-columns`.
- After Stage 2, run `cd src/ui/frontend && npm run build` before handoff to test-child.
- Deviation → Linear comment on **AST-657** with 🛑 template from plan-child §6.

## Review

- **Branch:** `origin/sub/AST-633/AST-657-uat-freeze-first-n-data-columns`
- **Diff:** `origin/dev...9870490e` (product: `origin/dev` → `9870490e` two-dot for UI files; three-dot reported merge-base ambiguity — bootstrap/AST-654 not in branch delta vs `origin/dev`)
- **Tip:** `9870490e`
- **Radia:** 2026-06-15 — **findings** (discuss only)

### What's solid

| Area | Assessment |
|------|------------|
| Root cause / plan | Autosize (AST-652) broke sticky offsets that relied on 120px / 40px fallbacks; fix measures header `offsetWidth` after layout and merges with user-resized widths — matches plan hypothesis. |
| Stage 1 | `mergeWidthsForSticky`, `measureListTableColumnWidths`, extended `stickyLeftPx(checkboxWidthPx)`, `useListTableColumnMeasure` hook. |
| Stage 2 | ListPage `tableRef` + merged widths in `frozenCellStyle`; `ScheduledPhaseTable` inner component (valid hook-per-table); CSS re-declares `position: sticky` on frozen th/td. |
| §1.3 DRY | Shared measure hook for ListPage and Scheduled Actions. |
| Boundaries | No config/backend/autosize/truncation changes. |
| Tests | Unit tests for merge, measure, checkbox width param; ListPage test asserts cumulative `left` on frozen headers; `9870490e` adds `widthsEqual` guard against measure-hook re-render loop. |

### Issues

| Severity | Location | Note |
|----------|----------|------|
| **discuss** | Manual UAT (Susan repro) | Component tests run in jsdom where `offsetWidth` is **0** — ListPage AST-657 test explicitly falls back to 120px chain, **not** real measured widths. **UAT on Agent Timesheets** (wide table, scroll right) is the gate for this bug: checkbox + first **two data columns** must stay visible; action column stays right. |
| **discuss** | First paint | Before `useLayoutEffect` measure, offsets use 40px checkbox + 120px column fallbacks — brief misalignment possible on first frame until measure runs. Acceptable if UAT passes after paint; flag if Susan sees flash. |

### Advisory

- `9870490e` infinite re-render fix (`widthsEqual`, stable `orderedKeysKey` / `persistedKey` deps) is appropriate — keep.
- Re-measure triggers on resize (`persistedKey`), col order, row count, `frozenN` — aligns with plan.

### Recommended actions

1. **resolve-child:** Confirm Susan UAT repro on Agent Timesheets horizontal scroll (primary AC).
2. No code fix-now from review unless UAT fails.
