# AST-652 — UAT: Remove force-fit; autosize list table columns

**Linear:** [AST-652 — UAT: Remove force-fit; autosize list table columns (Table Layout fix)](https://linear.app/astralcareermatch/issue/AST-652/uat-remove-force-fit-autosize-list-table-columns-table-layout-fix)  
**Parent:** [AST-633 — Table Layout fix](https://linear.app/astralcareermatch/issue/AST-633/table-layout-fix) (AC reference only — horizontal scroll, not squish)  
**Publish ref:** `origin/sub/AST-633/AST-652-uat-remove-force-fit-autosize-columns` (origin only)

## Summary

AST-647 shipped frozen columns, sticky headers, and truncation, but shared list tables still default to **`table-layout: fixed`** and **`width: 100%`** on `.list-page-table`, squishing columns to fit the viewport. Only consumers that passed **`horizontalScrollable`** or added **`list-page-table--auto`** / inline **`tableLayout: "auto"`** escaped force-fit. Susan UAT (2026-06-14): remove the force-fit-on-one-screen rule and **autosize columns to content**, relying on existing horizontal scroll (`.list-page-table-wrap--scroll`) and frozen-column behavior when the table is wider than the viewport. This UAT bug is CSS + markup cleanup only — no changes to frozen-column defaults, truncation, sort/filter, resize persistence, or backend.

**Builds on:** [AST-647 plan](ast-647-list-table-layout-freeze-sticky-tooltips.md) — patch delta only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/App.css` | Default `.list-page-table` to `table-layout: auto` + `width: auto`; remove fixed-layout ellipsis hack; drop redundant `.list-page-table--auto` | ui |
| `src/ui/frontend/src/components/ListPage.tsx` | Remove `horizontalScrollable` prop; table always uses autosize base class | ui |
| `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx` | Remove obsolete `horizontalScrollable` prop | ui |
| `src/ui/frontend/src/pages/AdminCostReconciliation.tsx` | Remove redundant `list-page-table--auto` class | ui |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Remove redundant inline `tableLayout: "auto"` | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Remove redundant inline `tableLayout: "auto"` | ui |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | Remove redundant inline `tableLayout: "auto"` | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Remove percentage `width` on `<th>` so columns autosize; keep frozen sticky offsets | ui |

**QA manifest (Betty — not engineer commits):** extend `test_ListPage_listTableLayout.test.tsx` or add assertion that default ListPage table does **not** use fixed layout (e.g. computed `table-layout: auto`); optional smoke that wide Agent Timesheets / Scheduled Actions overflow horizontally instead of compressing column text. Manual: Agent Timesheets + Admin Scheduled Actions with many columns — columns widen to header/content, horizontal scrollbar appears when needed; frozen left columns still stick.

**Out of scope:** frozen-column count, sticky header CSS, truncation/tooltips, row-click flows, column reorder/resize/localStorage, `UI_CONFIG` keys, job phase grouped tables (already inline auto).

---

## Stage 1: Autosize default in shared list-table CSS

**Done when:** `.list-page-table` uses natural column sizing and `width: auto`; tbody cells no longer force equal shrink via `max-width: 0`; `.list-page-table--auto` removed (behavior folded into base).

1. In `src/ui/frontend/src/App.css`, replace the `.list-page-table` block (~lines 381–386):

   ```css
   .list-page-table {
     width: auto;
     border-collapse: collapse;
     table-layout: auto;
     font-size: 13px;
   }
   ```

2. Delete the entire `.list-page-table--auto` rule block (~lines 387–391) — no callers should remain after Stage 2.

3. In `.list-page-table tbody td` (~lines 437–445), remove **`max-width: 0;`** and its comment. Keep `white-space: nowrap`, `overflow: hidden`, and `text-overflow: ellipsis` for cells that rely on CSS ellipsis; primary long-text truncation remains **`ListTableTruncatedCell`** from AST-647.

   ⚠️ **Decision:** `max-width: 0` is the fixed-layout equal-column shrink trick — it conflicts with autosize. User-resized columns still set explicit pixel `width` on th/td via ListPage; those override natural sizing when present.

4. Grep repo for `list-page-table--auto` — expect zero matches after Stage 2; after Stage 1 only `AdminCostReconciliation.tsx` may still reference it (fixed in Stage 2).

**Ritual:** `code(AST-652): default list-page-table to autosize layout`

---

## Stage 2: Remove force-fit gates and Scheduled Actions % widths

**Done when:** ListPage no longer gates autosize behind `horizontalScrollable`; redundant overrides removed from consumers; Scheduled Actions phase tables drop percentage column widths; frozen sticky offsets unchanged.

1. In `src/ui/frontend/src/components/ListPage.tsx`:
   - Remove `horizontalScrollable?: boolean` from `ListPageProps` (~line 41) and its JSDoc.
   - Remove `horizontalScrollable = false` from destructuring (~line 99).
   - Change table class (~line 336) from conditional to:
     ```tsx
     <table className="list-page-table">
     ```

2. In `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx`, remove the `horizontalScrollable` prop from `<ListPage>` (~line 218).

3. In `src/ui/frontend/src/pages/AdminCostReconciliation.tsx`, change (~line 267):
   ```tsx
   <table className="list-page-table">
   ```
   (drop `list-page-table--auto`).

4. In `src/ui/frontend/src/pages/JobsSkipped.tsx`, `JobsRecommended.tsx`, and `JobsInReview.tsx`, remove `style={{ tableLayout: "auto" }}` from each phase `<table className="list-page-table">` — base CSS now provides auto layout.

5. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, on each `<th>` in the phase table (~lines 383–396), remove the **`width: "…%"`** entry from the third argument to `scheduledFrozenStyle(..., { width: "…%" })` — pass `{}` or omit the width object entirely so headers size to label text. Example:
   ```tsx
   <th className={...} style={scheduledFrozenStyle(0, frozenN)} onClick={...}>Candidate{sortIcon("candidate_id")}</th>
   ```
   Do **not** change `scheduledFrozenStyle`, `DATA_COL_KEYS`, sort handlers, row click, or frozen class logic.

   ⚠️ **Decision:** Percent widths were force-fit relative to a 100%-wide table; removing them lets columns grow and triggers horizontal scroll on the existing `list-page-table-wrap--scroll` wrapper. Sticky `left` offsets still use `stickyLeftPx` with 120px fallback per column (AST-647) — acceptable for UAT; do not add resize persistence to Scheduled Actions in this bug pass.

6. In `tests/component/frontend/components/test_ListPage.test.tsx`, remove `horizontalScrollable` from the bulk-actions test props (~line 63).

7. `grep -r "horizontalScrollable\|list-page-table--auto" src/ui/frontend` — must return no matches.

**Ritual:** `code(AST-652): drop horizontalScrollable gate and Scheduled Actions % widths`

---

## Self-Assessment

**Scope:** `minor` — CSS default change plus small prop/class cleanup across known list-table consumers; no new modules or API surface.

**Conf:** `high` — AST-647 already introduced `.list-page-table--auto` as the target behavior; this bug promotes that behavior to the default and deletes the opt-in gate.

**Risk:** `Medium` — every `.list-page-table` screen changes layout width behavior; wrong CSS could break frozen-column overlap or column resize, but scroll wrappers and AST-647 sticky classes remain untouched.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Fold `--auto` into base class; remove duplicate inline `tableLayout: auto` on job pages |
| §2.1 config | No new config keys — layout presentation only |
| §3.3 imports | No new cross-layer imports |
| §3.5 naming | Keep existing `list-page-table*` BEM classes |

No conflicts — plan stays UI-only per parent boundaries.

---

## Execution contract

- Stages 1 → 2 in order; one `code()` commit per stage on epic worktree; publish each to **`origin/sub/AST-633/AST-652-uat-remove-force-fit-autosize-columns`** via `git push origin HEAD:sub/AST-633/AST-652-uat-remove-force-fit-autosize-columns`.
- After Stage 2, run `cd src/ui/frontend && npm run build` before handoff to test-child.
- Deviation → Linear comment on **AST-652** parent thread format from plan-child §6.
