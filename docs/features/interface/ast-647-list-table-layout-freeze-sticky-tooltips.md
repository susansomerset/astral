# List table layout — freeze columns, sticky header, cell tooltips

**Linear:** [AST-647](https://linear.app/astralcareermatch/issue/AST-647/list-table-layout-freeze-columns-sticky-header-cell-tooltips-table)  
**Parent:** [AST-633](https://linear.app/astralcareermatch/issue/AST-633/table-layout-fix)  
**Publish ref:** `sub/AST-633/AST-647-list-table-layout-freeze-sticky-tooltips`

Shared list/table presentation for **ListPage** and pages using the same `list-page-table` markup: configurable **N** frozen left data columns (default **2** from `UI_CONFIG` via `/api/system/ui_config`), checkbox and row-action columns always frozen in addition to **N**, vertical **sticky header** in the table scroll region, horizontal scroll for wide tables, and long cells truncated to **30** characters with full value in a hover tooltip. One bespoke grouped list (**AdminScheduledActions**) adopts the same contract so acceptance covers both ListPage and non-ListPage consumers.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `list_table_frozen_data_columns` and `list_table_cell_truncate_chars` to `UI_CONFIG` | utils |
| `src/ui/frontend/src/lib/listTableLayout.ts` | Shared helpers: resolve frozen count, cumulative `left`/`right` offsets, truncate helper | ui |
| `src/ui/frontend/src/components/ListTableTruncatedCell.tsx` | Truncate + native `title` tooltip for plain cells | ui |
| `src/ui/frontend/src/components/ListPage.tsx` | Load new UI_CONFIG keys; `frozenDataColumns` prop; apply freeze + truncation | ui |
| `src/ui/frontend/src/App.css` | Fix sticky header regression; frozen-column + sticky-corner z-index/background | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Bespoke grouped table: shared layout helpers, `frozenDataColumns={3}`, truncation | ui |

**QA manifest (Betty — not engineer commits):** extend or add frontend tests verifying (a) ListPage renders frozen-column classes when ui_config default is 2; (b) truncated cell shows ellipsis + `title` when string length > 30; (c) AdminScheduledActions phase table keeps sort click handlers after layout classes applied. Manual smoke: Agent Timesheets horizontal scroll + sticky header; Scheduled Actions with 3 frozen cols; company list row-click modal still opens.

## Stage 1: UI config defaults

**Done when:** `UI_CONFIG` exposes `list_table_frozen_data_columns: 2` and `list_table_cell_truncate_chars: 30`; `GET /api/system/ui_config` returns both keys unchanged from config spread; `python -m compileall src/utils/config.py` passes; no frontend changes yet.

1. In `src/utils/config.py`, inside `UI_CONFIG` (after `column_types`, ~line 2244), add:
   ```python
   # AST-647: shared list-table layout — default frozen data columns (N) and cell truncate length.
   "list_table_frozen_data_columns": 2,
   "list_table_cell_truncate_chars": 30,
   ```
2. Update the `UI_CONFIG` header comment (~lines 2231–2234) to mention list-table layout keys alongside `column_types`.
3. Do **not** add a new API route — `api_system.ui_config` already spreads `**UI_CONFIG`.

⚠️ **Decision:** Both frozen count and truncate length live in `UI_CONFIG` (not inline React literals) so display rules stay co-located with `column_types` per Code Rules §2.1. AC6 only mandates config-sourced frozen default; truncate in config prevents a magic `30` in TS.

## Stage 2: Shared layout helpers, truncated cell, and CSS foundation

**Done when:** `listTableLayout.ts` and `ListTableTruncatedCell.tsx` exist; `App.css` sticky header works inside `.list-page-table-wrap--scroll`; frozen-column classes styled; no ListPage wiring yet.

1. Create `src/ui/frontend/src/lib/listTableLayout.ts` with:
   ```typescript
   export interface ListTableUiConfig {
     list_table_frozen_data_columns?: number
     list_table_cell_truncate_chars?: number
   }

   export const LIST_TABLE_CHECKBOX_WIDTH_PX = 40

   export function resolveFrozenDataColumns(
     ui: ListTableUiConfig | null,
     override?: number,
   ): number {
     if (typeof override === "number" && override >= 0) return override
     const n = ui?.list_table_frozen_data_columns
     return typeof n === "number" && n >= 0 ? n : 0
   }

   export function resolveCellTruncateChars(ui: ListTableUiConfig | null): number {
     const n = ui?.list_table_cell_truncate_chars
     return typeof n === "number" && n > 0 ? n : 30
   }

   export function truncateForDisplay(text: string, maxChars: number): { display: string; full: string } {
     const full = text
     if (full.length <= maxChars) return { display: full, full }
     return { display: full.slice(0, maxChars) + "\u2026", full }
   }

   /** Cumulative sticky `left` for a data column index (0-based within ordered data columns). */
   export function stickyLeftPx(
     dataColIndex: number,
     colWidths: Record<string, number>,
     orderedKeys: string[],
     hasCheckbox: boolean,
     frozenDataColumns: number,
   ): number | null {
     if (dataColIndex >= frozenDataColumns) return null
     let left = hasCheckbox ? LIST_TABLE_CHECKBOX_WIDTH_PX : 0
     for (let i = 0; i < dataColIndex; i++) {
       const key = orderedKeys[i]
       left += colWidths[key] ?? 120
     }
     return left
   }
   ```

2. Create `src/ui/frontend/src/components/ListTableTruncatedCell.tsx`:
   ```tsx
   import { truncateForDisplay } from "../lib/listTableLayout"

   export default function ListTableTruncatedCell({
     text,
     maxChars,
   }: {
     text: string
     maxChars: number
   }) {
     const { display, full } = truncateForDisplay(text, maxChars)
     if (full.length <= maxChars) return <>{display}</>
     return <span title={full}>{display}</span>
   }
   ```

3. In `src/ui/frontend/src/App.css`, fix sticky header on `.list-page-table thead th`:
   - Remove the trailing `position: relative;` rule (~line 406) that overrides `position: sticky; top: 0;` (~line 394).
   - Keep resize handle positioning by adding:
     ```css
     .list-page-table thead th {
       position: sticky;
       top: 0;
       z-index: 2;
       /* existing padding, background, border, etc. unchanged */
     }
     .list-page-table thead th .col-resize-handle {
       position: absolute;
       right: 0;
       top: 0;
       bottom: 0;
       width: 5px;
       cursor: col-resize;
     }
     ```
   - Move `.col-resize-handle` block (~lines 409–421) under the nested selector above (same visual rules).

4. Add frozen-column CSS after the ListPage table section (~line 462):
   ```css
   .list-page-table-wrap--scroll {
     overflow: auto;
   }

   .list-table-cell-frozen {
     position: sticky;
     background: var(--bg-card);
     z-index: 1;
   }

   .list-page-table thead th.list-table-cell-frozen {
     z-index: 3;
       background: var(--bg-elevated);
   }

   .list-page-table tbody tr:hover td.list-table-cell-frozen {
     background: var(--bg-elevated);
   }

   .list-table-cell-frozen-right {
     position: sticky;
     right: 0;
     background: var(--bg-card);
     z-index: 1;
   }

   .list-page-table thead th.list-table-cell-frozen-right {
     z-index: 3;
     background: var(--bg-elevated);
   }
   ```

5. Ensure `.list-page-table tbody td` long text does not wrap by default when truncation applies — add to existing tbody td rule:
   ```css
   white-space: nowrap;
   overflow: hidden;
   text-overflow: ellipsis;
   max-width: 0; /* allows ellipsis in table-layout: fixed */
   ```
   ⚠️ **Decision:** `max-width: 0` on all tbody td is the standard fixed-layout ellipsis trick; ListPage already uses `table-layout: fixed` unless `--auto`. For `--auto` tables (horizontal scroll mode), ellipsis still works with explicit col widths.

## Stage 3: ListPage integration

**Done when:** ListPage reads ui_config frozen/truncate defaults; supports `frozenDataColumns?: number` prop; checkbox + first **N** data columns + row-actions column stick; cells truncate at config length with tooltip; sort/filter/checkbox/drag-resize/localStorage unchanged; table wrap always scrollable.

1. In `src/ui/frontend/src/components/ListPage.tsx`, extend `UiConfig` interface (~line 9):
   ```typescript
   interface UiConfig {
     column_types: Record<string, ColumnTypeConfig>
     list_table_frozen_data_columns?: number
     list_table_cell_truncate_chars?: number
   }
   ```

2. Add optional prop to `ListPageProps` (~line 55):
   ```typescript
   frozenDataColumns?: number  // per-screen override; omit → UI_CONFIG default
   ```

3. Destructure `frozenDataColumns` in the component signature with default `undefined`.

4. After `_uiConfig` is loaded, compute:
   ```typescript
   const frozenN = resolveFrozenDataColumns(_uiConfig, frozenDataColumns)
   const truncateChars = resolveCellTruncateChars(_uiConfig)
   ```

5. Change table wrap (~line 322) to **always** include scroll class:
   ```tsx
   <div className="list-page-table-wrap list-page-table-wrap--scroll">
   ```
   Keep `list-page-table--auto` when `horizontalScrollable` is true (unchanged).

6. For header row `<th>` elements:
   - Checkbox `<th>`: add `className="list-page-check-col list-table-cell-frozen"` and `style={{ left: 0 }}`.
   - Each `orderedColumns` entry at index `i`: if `stickyLeftPx(i, colWidths, colOrder, showCheckboxes, frozenN)` returns a number, add class `list-table-cell-frozen` and `style={{ left: `${left}px` }}` merged with existing align/width styles.
   - Trailing row-actions `<th>`: when `rowActions` is set, add `list-table-cell-frozen-right` (no left offset).

7. For body `<td>` elements — mirror the same index logic as headers for checkbox, data columns, and row-actions td.

8. Replace default string cell rendering (~lines 382–386):
   - When `col.expandable`: keep existing `<ExpandableCell>` (unchanged threshold 100 — opt-out for columns that need inline expand).
   - When `col.render`: keep custom render; if render returns a plain string longer than `truncateChars`, wrap with `<ListTableTruncatedCell>` only when the render output is a string (if ReactNode, leave as-is).
   - Else (formatted or plain): wrap display string in `<ListTableTruncatedCell text={String(...)} maxChars={truncateChars} />`.

9. Do **not** change sort handlers, drag-and-drop column reorder, resize handlers, or `saveLayout` / `loadLayout` logic.

10. Manual verification target for AC1/AC3/AC5/AC7: `AdminAgentTimesheets.tsx` already passes `horizontalScrollable` — no prop change required for default **N=2**; confirm sticky header + two left data columns stay visible when scrolling horizontally on a wide viewport.

## Stage 4: Bespoke table — AdminScheduledActions

**Done when:** Scheduled Actions phase tables use the same freeze/truncate/sticky-header behavior; `frozenDataColumns={3}` keeps Candidate, Task, and Entity visible; row click to edit modal still works; sort toggles still work.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`:
   - Import `resolveFrozenDataColumns`, `resolveCellTruncateChars`, `stickyLeftPx`, `LIST_TABLE_CHECKBOX_WIDTH_PX` from `../lib/listTableLayout`.
   - Import `ListTableTruncatedCell` from `../components/ListTableTruncatedCell`.
   - Load ui_config once (same module-level cache pattern as ListPage — **reuse** `loadUiConfig` by exporting it from `ListPage.tsx` **or** duplicate the minimal 10-line fetch in this file; prefer **export `loadUiConfig` and `_uiConfig` getter** from `ListPage.tsx` to avoid a third copy).

   ⚠️ **Decision:** Export a small `src/ui/frontend/src/lib/uiConfig.ts` module with the existing ListPage cache moved there — both ListPage and bespoke pages import it. Refactor ListPage to import from `uiConfig.ts` (same behavior, no duplicate fetch).

2. Create `src/ui/frontend/src/lib/uiConfig.ts` — move `_uiConfig`, `_uiConfigPending`, `loadUiConfig`, and `UiConfig` interface from `ListPage.tsx` into this file; update ListPage imports.

3. At top of `AdminScheduledActions` component, add ui_config load effect (same as ListPage).

4. Set module-level constant for this screen:
   ```typescript
   const FROZEN_DATA_COLUMNS = 3
   ```
   Pass to `resolveFrozenDataColumns(_uiConfig, FROZEN_DATA_COLUMNS)`.

5. On each phase table's wrap div (~line 356), add class `list-page-table-wrap--scroll` if not already present (wrap already has `list-page-table-wrap`).

6. Define ordered data column keys for this table (fixed order matching `<th>` sequence):
   ```typescript
   const DATA_COL_KEYS = [
     "candidate_id", "task_key", "entity_type", "trigger_state", "score_floor",
     "auto_mode", "run", "debug", "available_count", "freq_hrs", "min_count",
     "batch_size", "max_runs", "last_run_at",
   ] as const
   ```
   Map header/body cell index → key for `stickyLeftPx` (no checkbox on this table).

7. Apply `list-table-cell-frozen` + computed `left` to first **3** data columns (`candidate_id`, `task_key`, `entity_type`) in both `<th>` and `<td>`.

8. Wrap plain text cell content (`row.candidate_id`, `row.task_key`, entity type, trigger state, etc.) with `<ListTableTruncatedCell>` using `resolveCellTruncateChars(_uiConfig)`. Do **not** wrap interactive cells (AUTO/Run/Dbg buttons) — only text nodes.

9. Do **not** change phase grouping, CollapsiblePanel, filters, modals, or API calls.

## Self-Assessment

**Scope:** `Single-Component` — All changes serve one layout contract (shared helpers + ListPage + one bespoke adopter + CSS); no backend logic beyond two `UI_CONFIG` literals.

**Conf:** `Medium` — Sticky offset math with user-resized columns and drag-reordered order is well-understood but needs careful index alignment; reusing existing `list-page-table` markup and native `title` tooltips avoids new dependencies.

**Risk:** `Medium` — ListPage is widely consumed; a CSS or sticky-index bug would affect many admin/job/company lists, but behavior is presentation-only and row-click/sort/filter paths are untouched.

## Code Rules self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Shared `listTableLayout.ts`, `uiConfig.ts`, and `ListTableTruncatedCell` avoid duplicating fetch/truncate/freeze logic across ListPage and Scheduled Actions. |
| §2.1 Config | Frozen default and truncate length in `UI_CONFIG`; per-screen override via `frozenDataColumns` prop only. |
| §2.4 / §2.6 | N/A — no batch or state machine changes. |
| §3.3 Imports | New files live under `src/ui/frontend/`; config change in `src/utils/` only. |
| §3.5 Naming | `list_table_*` snake_case in config; camelCase TS helpers match existing frontend style. |
| §1.5.1 | No backend debug logging changes. |

No conflicts requiring `conf-!!-NONE`.

## Review

- **Branch:** `origin/sub/AST-633/AST-647-list-table-layout-freeze-sticky-tooltips`
- **Diff:** `origin/dev...origin/sub/AST-633/AST-647-list-table-layout-freeze-sticky-tooltips`
- **Tip:** `5b9b971a`
- **Radia:** 2026-06-14 — **findings** (one discuss; see below)

### What's solid

| Area | Assessment |
|------|------------|
| Plan fidelity | Stages 1–4 match the combined plan: `UI_CONFIG` keys, `listTableLayout` / `uiConfig` / `ListTableTruncatedCell`, ListPage wiring, `AdminScheduledActions` adopter, sticky-header CSS fix. |
| §2.1 Config | `list_table_frozen_data_columns` / `list_table_cell_truncate_chars` in `UI_CONFIG`; ListPage `frozenDataColumns` override; no new API route. |
| §1.3 DRY | ui_config cache extracted to `uiConfig.ts`; freeze/truncate helpers shared. |
| §3.3 Layers | UI-only frontend + two config literals; no layer violations. |
| Boundaries | Layout/presentation only — sort, filter, checkbox, drag/resize, localStorage, phase grouping untouched. |
| Tests | Betty manifest present: layout helpers, truncated cell, ListPage freeze/truncate, ui_config API defaults, Scheduled Actions frozen-class test. |

### Issues

| Severity | Location | Note |
|----------|----------|------|
| **discuss** | `AdminScheduledActions.tsx` — `scheduledFrozenStyle` / `stickyLeftPx(..., {}, ...)` | Bespoke table uses **percentage** column widths (`9%`, `14%`, `7%`) but sticky `left` offsets assume **pixel** widths (`120` default per prior col). Column 0 (`left: 0`) is correct; columns 1–2 may **misalign** under horizontal scroll. Component tests assert CSS classes only, not pixel alignment. **UAT:** Scheduled Actions with wide content / narrow viewport — scroll horizontally and confirm Candidate / Task / Entity headers and cells stay aligned with their columns. If gaps or overlap appear, pass measured widths (or min-width colgroup + `--auto`) into `stickyLeftPx`. |
| advisory | `resolveFrozenDataColumns(null)` → `0` before ui_config loads | Brief render with no frozen data columns until fetch completes; pre-existing fetch-failure fallback unchanged. |
| advisory | `App.css` — global `tbody td` `max-width: 0` + nowrap | Intended for truncation; watch `expandable` columns in UAT for ellipsis fighting inline expand toggle. |
| advisory | `list-table-cell-frozen-right` | No dedicated hover background rule (left frozen cols have one); row-actions stickies may look slightly flat on hover. |

### Recommended actions

1. **resolve-child:** Run manual UAT on Scheduled Actions horizontal scroll for frozen-column alignment (discuss item above).
2. **Optional:** Add hover background for `tbody tr:hover td.list-table-cell-frozen-right` if cosmetic gap matters.
3. No fix-now blockers for ListPage path — pixel offsets use `colWidths` from resize/localStorage as planned.

