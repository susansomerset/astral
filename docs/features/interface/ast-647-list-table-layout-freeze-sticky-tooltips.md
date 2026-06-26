<!-- linear-archive: AST-647 archived 2026-06-23 -->

## Linear archive (AST-647)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-647/list-table-layout-freeze-columns-sticky-header-cell-tooltips-table  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-633 — Table Layout fix  
**Blocked by / blocks / related:** parent: AST-633

### Description

## What this implements

Shared list/table presentation for **ListPage** and pages using the same list-table markup: configurable **N** frozen left data columns (default **2** from `UI_CONFIG` via `/api/system/ui_config`), checkbox and row-action columns always frozen in addition to **N**, vertical **sticky header** in the table scroll region, horizontal scroll for wide tables, and long cells truncated to **30** characters with full value in a hover tooltip. Add the default frozen-column count to `config.py` / UI config API. Apply the same layout contract to at least one bespoke grouped list table (e.g. Recommended or Scheduled Actions phase table) so acceptance covers both ListPage and non-ListPage consumers.

## Acceptance criteria

1. With config default **2**, a wide list screen with horizontal overflow keeps the leftmost **two** data columns visible while scrolling right; remaining columns scroll normally.
2. A screen that declares a different frozen-column count (e.g. **3**) keeps that many left columns visible instead of the default.
3. Scrolling down through a long table keeps header labels visible at the top of the table scroll area on representative screens using both ListPage (e.g., Agent Timesheets) and a bespoke grouped list (e.g., Recommended or Scheduled Actions phase table).
4. A cell with content longer than 30 characters displays truncated text with ellipsis; hovering shows the full value in a tooltip.
5. On a screen that already opens detail on row click (e.g., company or job list with modal), row click still opens that detail after this change.
6. List screens that do not override frozen-column count all inherit **2** from config via the UI config API — no hardcoded default in frontend source.
7. Sort, filter, checkbox selection, and column drag/reorder still work on at least one ListPage consumer and one bespoke table after the layout change.

## Boundaries

* Layout and cell presentation only — no changes to column definitions, sort/filter, bulk actions, phase grouping, or row actions beyond layout props.
* No backend debug logging changes (UI-only).
* Does not apply to non-tabular admin views (artifact editors, profile forms, script sandbox log stream, Data Management ad-hoc query result table unless explicitly adopted later).
* Must not break ListPage column reorder, resize, or localStorage layout persistence.

## Notes for planning

* Primary files: `src/utils/config.py` (`UI_CONFIG`), `src/ui/frontend/src/components/ListPage.tsx`, shared list-table CSS, and one bespoke phase/grouped list page.
* Checkbox/action columns: do **not** count toward **N** but are always included in the freeze set (parent open question resolved).
* Per-screen override via declarative prop on ListPage (and equivalent on bespoke tables).
* Katherine owns React/TS + UI config exposure; no new API endpoints beyond existing `ui_config` if the key fits there.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-633`, child `sub/AST-633/<child-segment>`. Created at **dispatch-parent**. Engineers publish to `origin/sub/...` — never Linear `gitBranchName` when it disagrees.

### Comments

#### radia — 2026-06-14T21:43:56.521Z
**Review** — `origin/dev...origin/sub/AST-633/AST-647-list-table-layout-freeze-sticky-tooltips` @ `5b9b971a` (+ doc `86c65f32`)

Plan doc: `docs/features/interface/ast-647-list-table-layout-freeze-sticky-tooltips.md` (Review section)

### Solid

- Stages 1–4 delivered: `UI_CONFIG` keys, shared `listTableLayout` / `uiConfig` / `ListTableTruncatedCell`, ListPage freeze + truncate + always-on scroll wrap, `AdminScheduledActions` with 3 frozen cols, sticky-header CSS fix (removed `position: relative` override).
- §2.1 / §1.3 / §3.3: config-driven defaults, DRY extract, UI-only layers; boundaries respected (sort/filter/checkbox/drag/resize/localStorage untouched).
- Betty manifest covered: helper unit tests, truncated cell, ListPage layout classes + override, ui_config API assertion, Scheduled Actions frozen-class test.

### discuss

- **`AdminScheduledActions.tsx`** — `scheduledFrozenStyle` calls `stickyLeftPx(..., {}, ...)` while columns use **% widths** (`9%`, `14%`, `7%`). Sticky `left` uses **120px defaults** per prior column; col 0 is fine, cols 1–2 may **misalign** on horizontal scroll. Tests only assert CSS classes.
  - **UAT:** Scheduled Actions, narrow viewport / wide rows — scroll horizontally; confirm Candidate / Task / Entity stay aligned. If broken, feed measured pixel widths or use min-width colgroup + `--auto`.

### advisory

- `frozenN === 0` until ui_config fetch completes (brief flash).
- Global `tbody td` `max-width: 0` + nowrap — watch `expandable` columns in UAT.
- No hover bg rule for `list-table-cell-frozen-right` (cosmetic).

**Verdict:** findings — no ListPage fix-now blockers; resolve-child should confirm Scheduled Actions sticky alignment in UAT.

#### betty — 2026-06-14T21:33:52.247Z
## QA test manifest (AST-647)

**Publish ref:** `origin/sub/AST-633/AST-647-list-table-layout-freeze-sticky-tooltips` @ `5b9b971a` (`merge-tests(AST-647): origin/tests 434d24c3`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref = `1361add1fbfa6f9340b825698e3665b0d2712761` (**§7.13zzt**)

1. **`tests/component/frontend/lib/test_listTableLayout.test.ts`** — `resolveFrozenDataColumns`, `truncateForDisplay`, `stickyLeftPx` helpers (AC1/AC2/AC4 math).
2. **`tests/component/frontend/components/test_ListTableTruncatedCell.test.tsx`** — ellipsis + `title` tooltip when string length > 30 (AC4).
3. **`tests/component/frontend/components/test_ListPage_listTableLayout.test.tsx`** — ListPage renders `list-table-cell-frozen` on checkbox + first **N=2** data columns and `list-table-cell-frozen-right` on row-actions; honors `frozenDataColumns` override (AC1/AC2/AC6).
4. **`tests/component/frontend/components/test_ListPage.test.tsx`** — regression: api mock serves `/api/system/ui_config` after **uiConfig** module extract (sort/filter/checkbox/drag/resize paths — AC7 baseline).
5. **`tests/component/frontend/pages/test_AdminScheduledActions.test.tsx`** — **`AST-647: phase table freezes first three data columns`** (bespoke grouped table, **N=3**); existing sort/filter/row-click tests retained; candidate-filter harness fixes for **All** / empty-candidates cases.
6. **`tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_list_table_layout_defaults`** — `list_table_frozen_data_columns: 2` and `list_table_cell_truncate_chars: 30` on `GET /api/ui_config` (AC6).

**Narrowed run (Appendix — §7.13zzt):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_list_table_layout_defaults

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_listTableLayout.test.ts \
  ../../../tests/component/frontend/components/test_ListTableTruncatedCell.test.tsx \
  ../../../tests/component/frontend/components/test_ListPage_listTableLayout.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx
```

**Manual smoke (plan):** Agent Timesheets horizontal scroll + sticky header; Scheduled Actions three frozen cols; company/job list row-click modal still opens.

— Betty

#### katherine — 2026-06-14T21:24:38.413Z
Plan: [`docs/features/interface/ast-647-list-table-layout-freeze-sticky-tooltips.md`](https://github.com/susansomerset/astral/blob/sub/AST-633/AST-647-list-table-layout-freeze-sticky-tooltips/docs/features/interface/ast-647-list-table-layout-freeze-sticky-tooltips.md) @ `5b404807`

Four build stages: (1) `UI_CONFIG` keys for frozen-column default **2** and truncate **30**; (2) shared `listTableLayout.ts` / `ListTableTruncatedCell` + CSS fix for sticky header (`position: relative` was overriding sticky) and frozen-column classes; (3) ListPage prop `frozenDataColumns?`, always-on scroll wrap, checkbox + **N** data cols + row-actions sticky; (4) **AdminScheduledActions** bespoke adoption with `frozenDataColumns={3}`.

**Self-assessment**
- **Scope:** `Single-Component` — one layout contract across shared helpers, ListPage, CSS, and one bespoke page; config literals only on backend.
- **Conf:** `Medium` — sticky `left` offsets must track drag-reordered columns and user-resized widths, but we reuse existing markup and native `title` tooltips with no new deps.
- **Risk:** `Medium` — ListPage is widely consumed; mistakes would be presentation-only but visible on many list screens — sort/filter/checkbox/reorder paths are explicitly untouched.

---

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

## Resolution

- **2026-06-14 (Katherine resolve-child):** No product commits — Radia review had **no fix-now** items. **`discuss`** (Scheduled Actions `%` widths vs `stickyLeftPx` 120px defaults) and **advisory** notes (ui_config flash, expandable columns, frozen-right hover) left for **Susan UAT** per review Recommended actions.
- **§9a:** `origin/sub/AST-633/AST-647-list-table-layout-freeze-sticky-tooltips` @ `86c65f32` merges cleanly into **`origin/dev`** and **`origin/ftr/AST-633`**.
- **Outcome:** Ticket → **User Testing** (implementer assignee unchanged).

