<!-- linear-archive: AST-746 archived 2026-06-23 -->

## Linear archive (AST-746)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-746/fix-scheduled-actions-table-column-gap-remove-column-gap-in-scheduled  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-744 — Remove column gap in scheduled_actions  
**Blocked by / blocks / related:** parent: AST-744

### Description

## What this implements

Fix the whitespace gap between Candidate and Task columns on the Scheduled Actions admin page, and correct Task/Entity column positioning so they no longer overlay the State column.

## Acceptance criteria

* No visible gap between Candidate and Task columns
* Task and Entity columns align correctly without overlapping State column values
* Frozen column sticky layout still works at default and configured frozen column counts

## Boundaries

* CSS/layout fix in scheduled actions table only — no API or backend changes
* No changes to other admin list tables unless shared layout helper fix is required

## Notes for planning

* Primary file: `src/ui/frontend/src/pages/AdminScheduledActions.tsx`
* Uses `useListTableColumnMeasure`, `stickyLeftPx`, `listTableLayout` — compare with other admin list pages that render correctly
* Existing test: `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx`

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-744-remove-column-gap-in-scheduled-actions`, child `sub/AST-744/AST-745-fix-scheduled-actions-table-column-gap`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-23T19:00:43.864Z
### Review (`origin/dev`…`origin/sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap`)

**Tip:** `2477e62` (includes doc commit) · product tip `f869adf`

**Plan fidelity:** Stage 1 matches plan — conditional `ScheduledPhaseTable` mount when section expanded, sort-icon remeasure deps, `scheduledFrozenStyle` width lock + `predecessorsReady` gate before sticky `left`. Scope confined to `AdminScheduledActions.tsx`; shared `listTableLayout` / hook untouched per plan.

**Code rules:** §1.3 DRY and §3.3 UI layer — clean. `predecessorsReady` / `(mergedWidths[k] ?? 0) > 0` is intentional (plan + inline comment); avoids `stickyLeftPx` 120px fallback when hidden-panel measure returned zero widths — not an unbounded D3 swallow.

**Tests:** `AST-746` component case covers mount-on-expand, no erroneous `120px` Task `left`, State column unfrozen; remeasure after mocked header widths aligns with manifest.

**fix-now:** none

**discuss:** none

**advisory:** Susan manual UAT still required — expand **each** phase section on Scheduled Actions and confirm gap/overlap fix + horizontal scroll frozen alignment (test-bible pass criterion).

**Doc:** [ast-746-fix-scheduled-actions-table-column-gap.md](https://github.com/susansomerset/astral/blob/2477e62/docs/features/interface/ast-746-fix-scheduled-actions-table-column-gap.md) § Review (Radia)

**Handoff:** Katherine → **resolve-child** (no code changes from review).

#### betty — 2026-06-18T23:00:31.089Z
## QA test manifest (AST-746)

**Publish:** `origin/sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap` @ `f869adf` (`merge-tests(AST-746): origin/tests 9626bb8`)

### 1. Existing coverage (re-run)
1. **`AST-647: phase table freezes first three data columns`** — frozen class wiring on expanded phase table (regression guard).

### 2. New coverage
1. **`AST-746: phase table mounts on expand; measured sticky left avoids 120px fallback gap`** — collapsed sections render no `<table>`; expanded table defers erroneous `120px` sticky fallback on Task; mocked `offsetWidth` yields cumulative `left` (`88px` / `160px`); State column (index 3) unfrozen with no inline `left`.

### 3. Manual UAT (Susan)
Scheduled Actions, multiple phase sections: expand each — no gap between Candidate/Task; Entity does not overlay State; horizontal scroll keeps three frozen columns aligned.

**Run (test-child):**
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-746|AST-647"
```

**Pass criterion:** Vitest green on narrowed run + Susan manual multi-phase UAT.

**Bible:** `docs/test-bible/frontend/pages.md` shasum `b7d9148726408e8185642d69c4e1fcaa2c047fbc` on publish ref.

**Builds on:** AST-647 / AST-652 / AST-657 list-table layout (`docs/test-bible/frontend/components.md`). No API or shared helper changes in scope.

#### katherine — 2026-06-18T22:48:40.210Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap/docs/features/interface/ast-746-fix-scheduled-actions-table-column-gap.md

**Self-assessment**
- **Scope:** `minor` — One bespoke admin page file; presentation-only layout fix scoped to Scheduled Actions phase tables.
- **Conf:** `high` — Root cause is measurement while `CollapsiblePanel` body is `hidden` (zero `offsetWidth` → 120px sticky fallback); fix mounts table on expand and locks frozen widths to measured values.
- **Risk:** `low` — Isolated to `AdminScheduledActions.tsx`; shared ListPage/helpers unchanged.

**Root cause (for validate-plan):** `useListTableColumnMeasure` runs while phase tables are inside `hidden` collapsed panels, so `mergedWidths` never gets real header widths and `stickyLeftPx` falls back to 120px per column — visible gap between Candidate/Task and Entity overlapping State.

---

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

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap` · tip **`f869adf`**

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stage 1 delivered verbatim: conditional `ScheduledPhaseTable` mount, sort-icon remeasure deps, `scheduledFrozenStyle` width lock + `predecessorsReady` gate before sticky `left`. Scope stays `AdminScheduledActions.tsx` only. |
| Root cause | Correctly targets hidden-panel `offsetWidth === 0` → empty `mergedWidths` → `stickyLeftPx` 120px fallback (`listTableLayout.ts` L75). |
| §1.3 DRY | Reuses `useListTableColumnMeasure` / `stickyLeftPx`; no duplicate measure hook. |
| §3.3 layer | UI-only; no new cross-layer imports. |
| Tests | `AST-746` case asserts no table before expand, no `120px` on Task header, State column unfrozen; remeasure after mocked widths + sort click matches plan manifest. |

### Issues

| Severity | Item | Location |
|----------|------|----------|
| — | **No fix-now or discuss.** | — |

### Recommended actions

| Action | Owner |
|--------|-------|
| **resolve-child** — no code changes required from review. | Katherine |
| Susan manual UAT: expand **each** phase section on Scheduled Actions; confirm gap/overlap fix and horizontal scroll alignment (test bible pass criterion). | Susan |

---

## Resolution (2026-06-23)

**Engineer:** Katherine · **Review ref:** `origin/sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap` @ `2477e62` (Radia doc) · product @ `f869adf`

**Changes vs Radia review:** None required — **fix-now** and **discuss** were empty. Merged publish ref on epic worktree (including Radia **Review (Radia)** section); no additional product edits.

**§9a dry-run:** `origin/sub/…` merges cleanly into `origin/dev` and `origin/ftr/AST-744-remove-column-gap-in-scheduled-actions`.

**Advisory:** Susan manual UAT — expand each phase section on Scheduled Actions; confirm Candidate/Task gap, Entity/State overlap, and horizontal scroll frozen alignment (test-bible pass criterion).
