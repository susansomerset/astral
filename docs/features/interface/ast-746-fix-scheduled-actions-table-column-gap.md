# AST-746 — Fix scheduled actions table column gap

**Linear:** [AST-746 — Fix scheduled actions table column gap (Remove column gap in scheduled_actions)](https://linear.app/astralcareermatch/issue/AST-746/fix-scheduled-actions-table-column-gap-remove-column-gap-in-scheduled)  
**Parent:** [AST-744 — Remove column gap in scheduled_actions](https://linear.app/astralcareermatch/issue/AST-744/remove-column-gap-in-scheduled-actions) (AC reference only)  
**Publish ref:** `origin/sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap`

## Summary

Susan UAT on **Scheduled Actions**: visible whitespace between **Candidate** and **Task**, and **Task** / **Entity** shifted right so they overlay **State**. AST-647/657 added measured `stickyLeftPx` via `useListTableColumnMeasure`, but phase tables live inside `CollapsiblePanel` bodies with `hidden={!expanded}`. Width measurement runs once while the table is hidden (`offsetWidth === 0`), so `mergedWidths` stays empty and frozen columns use the **120px fallback** per prior column — wrong cumulative `left` values under `table-layout: auto`. This bug pass remeasures only when the phase table is visible and locks frozen column widths to measured values so sticky offsets match column boundaries. CSS/layout only in `AdminScheduledActions.tsx`; no API, config, or ListPage changes unless build proves a shared helper fix is required.

**Builds on:** [AST-647](ast-647-list-table-layout-freeze-sticky-tooltips.md), [AST-652](ast-652-uat-remove-force-fit-autosize-list-table-columns.md), [AST-657](ast-657-uat-first-two-data-columns-not-frozen-only-action-column-table-layout-fix.md) — patch delta only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Defer phase table mount until section expanded; remeasure deps; lock frozen column widths to `mergedWidths`; apply sticky `left` only when widths are measured | ui |

**QA manifest (Betty — not engineer commits):** extend `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — after `expandFirstPhaseSection()`, assert frozen header at index 1 has `style.left` strictly less than `120px` when jsdom reports measured candidate width (or assert `left` on Task header equals measured Candidate `offsetWidth` after expand); assert State column (index 3) has no `list-table-cell-frozen` and is not overlapped (no inline `left`). Manual: Scheduled Actions with multiple phase sections — expand each, confirm no gap between Candidate/Task, Entity does not cover State, horizontal scroll keeps three frozen columns aligned.

**Out of scope:** `listTableLayout.ts` / `useListTableColumnMeasure.ts` changes unless Stage 1 fails manual UAT; ListPage and other admin tables; frozen-column count default (`FROZEN_DATA_COLUMNS = 3`); truncation, sort, modals, API, `UI_CONFIG`.

---

## Stage 1: Visible-only measurement and frozen width lock

**Done when:** With a phase section expanded, Candidate / Task / Entity columns have no visible gap, Entity does not overlay State, and frozen sticky behavior still works at default `frozenN = 3`; `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, on the `sections.map` block (~lines 532–557), render `ScheduledPhaseTable` **only when** that section is expanded — replace unconditional child with:
   ```tsx
   {resolvedOpenSection === sec.sectionKey ? (
     <ScheduledPhaseTable
       rows={sec.rows}
       frozenN={frozenN}
       truncateChars={truncateChars}
       threadStatus={threadStatus}
       allTaskKeys={allTaskKeys}
       toggleSort={toggleSort}
       sortIcon={sortIcon}
       openEdit={openEdit}
       toggleAutoMode={toggleAutoMode}
       toggleDebug={toggleDebug}
       handleRun={handleRun}
       handleStop={handleStop}
     />
   ) : null}
   ```
   ⚠️ **Decision:** Mounting the table only when the panel is expanded guarantees `useLayoutEffect` in `useListTableColumnMeasure` runs against a visible `<table>` (not `hidden`), so `offsetWidth` reflects real column widths instead of 0 → missing keys → 120px sticky fallback.

2. In `ScheduledPhaseTable`, extend `useListTableColumnMeasure` deps (~line 89) to include sort state so remeasure runs when sort icons change header width:
   ```typescript
   [rows.length, frozenN, sortIcon("candidate_id"), sortIcon("task_key"), sortIcon("entity_type")]
   ```
   Pass `sortIcon` into `ScheduledPhaseTable` props if not already available in scope (it is already passed — use it in the deps array).

3. In `scheduledFrozenStyle` (~lines 92–96), replace the body with width-locked sticky styles:
   ```typescript
   function scheduledFrozenStyle(colIndex: number, base: CSSProperties = {}): CSSProperties {
     const key = DATA_COL_KEYS_ARR[colIndex]
     const w = mergedWidths[key]
     const widthStyle: CSSProperties =
       w && w > 0 ? { width: w, minWidth: w, boxSizing: "border-box" } : {}
     const left = stickyLeftPx(colIndex, mergedWidths, DATA_COL_KEYS_ARR, false, frozenN)
     if (left == null) return { ...base, ...widthStyle }
     // Only apply sticky offset when all prior frozen columns have measured width (avoid 120px fallback gap).
     const predecessorsReady = DATA_COL_KEYS_ARR.slice(0, colIndex).every(
       (k) => (mergedWidths[k] ?? 0) > 0,
     )
     if (!predecessorsReady) return { ...base, ...widthStyle }
     return { ...base, ...widthStyle, left }
   }
   ```

4. Apply `scheduledFrozenStyle` to **both** `<th>` and `<td>` for frozen columns (indices 0–2) — already wired; verify no `width`/`left` is applied to State (index 3) or later columns.

5. Do **not** change `DATA_COL_KEYS`, `FROZEN_DATA_COLUMNS`, phase grouping, `CollapsiblePanel` component, sort handlers, row click, or API calls.

6. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

7. Manual verification (required before `code()`): open Scheduled Actions, select **All** candidates, expand a phase with several rows, confirm:
   - No whitespace gap between Candidate and Task headers/cells
   - Entity column ends before State column begins (no text overlap)
   - Horizontal scroll: three left columns remain frozen and aligned

**Ritual:** `code(AST-746): fix scheduled actions frozen column measure on expand`

---

## Self-Assessment

**Scope:** `minor` — One bespoke admin page file; presentation-only layout fix scoped to Scheduled Actions phase tables.

**Conf:** `high` — Root cause matches Radia AST-647 discuss item and `CollapsiblePanel` `hidden` behavior; fix pattern (mount when visible + width lock) is narrow and testable; reuses existing measure hook without new abstractions.

**Risk:** `low` — Change is isolated to `AdminScheduledActions.tsx`; ListPage and shared helpers untouched; worst case is brief frame without sticky `left` until widths measure (preferable to wrong 120px offsets).

---

## Code Rules self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `useListTableColumnMeasure`, `stickyLeftPx`, and existing `ScheduledPhaseTable` extraction — no duplicate measure logic. |
| §2.1 Config | No config changes; `FROZEN_DATA_COLUMNS = 3` override unchanged. |
| §2.4 / §2.6 | N/A — no batch or state machine changes. |
| §3.3 Imports | UI layer only; no new cross-layer imports. |
| §3.5 Naming | Follows existing `scheduledFrozenStyle` / `DATA_COL_KEYS` conventions. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Branch:** `origin/sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap`  
**Tip:** `36f61c2`  
**Built:** Stage 1 — mount `ScheduledPhaseTable` only when phase section expanded; remeasure deps include sort icons; `scheduledFrozenStyle` locks frozen widths and defers sticky `left` until predecessor columns measured.

**Out of build scope (Betty / qa-child):** component test assertions per build-child test-tree ban; manual UAT on multiple phase sections.
