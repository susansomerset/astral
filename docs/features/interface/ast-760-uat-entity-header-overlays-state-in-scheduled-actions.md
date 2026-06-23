# AST-760 — UAT: Entity header overlays State in scheduled actions table

**Linear:** [AST-760 — UAT: Entity header overlays State in scheduled actions table (Remove column gap in scheduled_actions)](https://linear.app/astralcareermatch/issue/AST-760/uat-entity-header-overlays-state-in-scheduled-actions-table-remove-column)  
**Parent:** AST-744 (AC reference only — inline in ticket Description)  
**Publish ref:** `origin/sub/AST-744/AST-760-uat-entity-header-overlays-state-in-scheduled-actions`

## Summary

Susan UAT (2026-06-23, after AST-758 local-dev delivery): **Scheduled Actions** phase table headers still misalign — **Entity** `th` paints over **State** `th` (State hidden behind Entity). AST-746 fixed hidden-panel measurement and 120px sticky fallback via mount-on-expand + `predecessorsReady`, but also added inline **`width` / `minWidth` locks** on frozen cells. **ListPage** uses measured `left` only (no width lock). On `table-layout: auto`, forcing `minWidth` on the last frozen sticky header (Entity, `z-index: 3`) while State remains a normal sticky header (`z-index: 2`) lets Entity's box overlap State's column slot in real browsers. This UAT bug removes width locking from `scheduledFrozenStyle` and matches ListPage's **left-only** frozen pattern; keeps AST-746 mount-on-expand and `predecessorsReady` gate. Fix in `AdminScheduledActions.tsx` only.

**Builds on:** [AST-746](ast-746-fix-scheduled-actions-table-column-gap.md), [AST-758](ast-758-uat-local-dev-not-showing-scheduled-actions-ui-fix.md) — header overlay delta only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Remove frozen width/minWidth lock from `scheduledFrozenStyle`; keep measured `left` + `predecessorsReady` | ui |

**QA manifest (Betty — not engineer commits):** extend `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — after `expandFirstPhaseSection()`, assert Entity header (index 2) has **no** inline `minWidth` / `width`; State header (index 3) has no `list-table-cell-frozen` and no inline `left`; optional jsdom `getBoundingClientRect`: Entity `right <= State.left + 1` (tolerance 1px). Manual: Susan repro — expand phase, headers Candidate → Task → Entity → State all visible and clickable; no Entity-over-State overlay; horizontal scroll frozen alignment holds.

**Out of scope:** `launch.sh` / AST-758 stale-dist delivery; `listTableLayout.ts` / `useListTableColumnMeasure.ts`; ListPage; `App.css` z-index changes; frozen-column count; API/config.

---

## Stage 1: Left-only frozen styles (drop width lock)

**Done when:** Expanded phase table shows Entity and State headers side-by-side without overlap; AST-746 gap fix preserved (no 120px fallback gap between Candidate/Task); `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, replace `scheduledFrozenStyle` (~lines 92–105) with ListPage-aligned **left-only** logic:

   ```typescript
   function scheduledFrozenStyle(colIndex: number, base: CSSProperties = {}): CSSProperties {
     const left = stickyLeftPx(colIndex, mergedWidths, DATA_COL_KEYS_ARR, false, frozenN)
     if (left == null) return base
     const predecessorsReady = DATA_COL_KEYS_ARR.slice(0, colIndex).every(
       (k) => (mergedWidths[k] ?? 0) > 0,
     )
     if (!predecessorsReady) return base
     return { ...base, left }
   }
   ```

   Remove entirely:
   - `const key = DATA_COL_KEYS_ARR[colIndex]`
   - `const w = mergedWidths[key]`
   - `widthStyle` / `width` / `minWidth` / `boxSizing` on frozen cells

   ⚠️ **Decision:** Width lock was AST-746's overlay trigger — frozen `th` at `z-index: 3` with forced `minWidth` extends over adjacent State `th` at `z-index: 2`. Measured `left` + table auto-layout column widths (as ListPage does) align boundaries without inline width forcing.

2. Do **not** change: conditional `ScheduledPhaseTable` mount on expand; `useListTableColumnMeasure` deps; `DATA_COL_KEYS`; `FROZEN_DATA_COLUMNS`; sort handlers; tbody/th frozen class wiring for indices 0–2 only.

3. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

4. Manual verification (required before `code()`): local `dev`, `zsh launch.sh --flask`, Admin → Scheduled Actions → expand phase with rows:
   - Headers left-to-right: Candidate, Task, Entity, State — each label visible
   - Entity does **not** cover State header (State sort click works)
   - No whitespace gap between Candidate and Task
   - Horizontal scroll: three frozen columns stay aligned

**Ritual:** `code(AST-760): drop frozen width lock; left-only sticky headers`

---

## Self-Assessment

**Scope:** `minor` — One function in `AdminScheduledActions.tsx`; removes AST-746 width-lock regression.

**Conf:** `high` — ListPage uses identical left-only pattern without overlay; Susan symptom matches z-index + forced minWidth on last frozen header; AST-746 tests already assert State has no inline `left`.

**Risk:** `low` — Worst case is gap regression if width lock was doing real work; mount-on-expand + measured `left` remain; manual UAT catches gap before resolve.

---

## Code Rules self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Aligns `scheduledFrozenStyle` with ListPage `frozenCellStyle` (left-only); removes bespoke width-lock branch. |
| §2.1 Config | No config changes. |
| §3.3 Imports | UI layer only. |
| §3.5 Naming | Keeps existing `scheduledFrozenStyle` name. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Branch:** `origin/sub/AST-744/AST-760-uat-entity-header-overlays-state-in-scheduled-actions`  
**Tip:** `a705c2a`  
**Built:** Stage 1 — removed `width`/`minWidth` lock from `scheduledFrozenStyle`; left-only sticky aligned with ListPage; mount-on-expand and `predecessorsReady` unchanged.

**Out of build scope:** Betty test assertions for no inline minWidth on Entity header; Susan manual UAT for header visibility.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-744/AST-760-uat-entity-header-overlays-state-in-scheduled-actions` · tip **`716da64`**

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stage 1 exact: `scheduledFrozenStyle` reverted to **left-only** sticky; width/`minWidth`/`boxSizing` lock removed; mount-on-expand + `predecessorsReady` + measure deps unchanged. |
| §1.3 DRY | Matches ListPage `frozenCellStyle` (left-only) while keeping AST-746 `predecessorsReady` gate — reasonable delta vs ListPage. |
| §3.3 layer | UI-only; no new imports. |
| Product scope | `AdminScheduledActions.tsx` product diff vs `origin/dev` is **11 lines** (this ticket only). |
| Tests | `AST-760` case asserts Entity header has no inline `width`/`minWidth`, State unfrozen with no `left`; remeasure path confirms `left` without width lock. |

### Issues

| Severity | Item | Location |
|----------|------|----------|
| — | **No fix-now.** | — |

### Recommended actions

| Action | Owner |
|--------|-------|
| **resolve-child** — no code changes required from review. | Katherine |
| **advisory:** Full three-dot diff vs `origin/dev` also carries **AST-751** test-bible + test manifest from `merge-tests` on the ftr/735 lineage — product hunk for AST-760 is isolated; expected rollup noise, not scope smuggling in product code. | — |
| Susan manual UAT: expand phase — Candidate/Task/Entity/State headers visible and clickable; Entity must not cover State; no Candidate/Task gap; horizontal scroll frozen alignment. | Susan |
