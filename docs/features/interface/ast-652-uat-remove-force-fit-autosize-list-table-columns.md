<!-- linear-archive: AST-652 archived 2026-06-23 -->

## Linear archive (AST-652)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-652/uat-remove-force-fit-autosize-list-table-columns-table-layout-fix  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-633 — Table Layout fix  
**Blocked by / blocks / related:** parent: AST-633

### Description

## What failed

List tables still use `table-layout: fixed` and `width: 100%` on `.list-page-table`, forcing columns to squish to fit the viewport (“force to fit on one screen”) instead of autosizing to content and scrolling horizontally when wide.

Susan UAT (2026-06-14): *“this should also TAKE OUT the 'force to fit on one screen' rule for the component, and autosize the columns.”*

## Expected

Shared list/table presentation (**ListPage** and pages using the same list-table markup/styles) autosizes column widths to content (natural/`auto` layout), drops the force-fit-on-one-screen rule, and relies on horizontal scroll (with existing frozen-column + sticky-header behavior) when the table is wider than the viewport.

## Repro

1. Open a wide **ListPage** consumer (e.g. Agent Timesheets) or **Admin Scheduled Actions** with many columns.
2. Observe columns compressed to fit the container width rather than sizing to header/cell content.
3. Compare to bespoke job phase tables that already use `tableLayout: "auto"`.

## Parent AC (quoted inline)

> **Horizontal scroll where needed:** Wide tables enable horizontal scrolling in the table body rather than squishing columns; frozen-column behavior applies whenever horizontal overflow exists.

## Boundaries

* This bug does **not** change: frozen-column count defaults/overrides, sticky header, 30-char truncation + tooltips, row-click detail flows, sort/filter/checkbox/column reorder/resize persistence, or backend/config keys beyond what layout CSS/JS requires.
* Does **not** redesign Scheduled Actions % width headers beyond aligning them with autosize + scroll (coordinate with existing frozen-column sticky offsets).

### Comments

#### chuckles — 2026-06-15T00:50:33.813Z
[check-linear] User Testing — resolve landed; parent [fix-uat] handoff posted (@susan re-test AST-633).

#### susan — 2026-06-15T00:47:01.920Z
@chuckles Have Katherine run resolve for this ticket, please.

#### radia — 2026-06-14T23:58:14.426Z
**Review** — `origin/dev...origin/sub/AST-633/AST-652-uat-remove-force-fit-autosize-columns` @ `8b2e748c` (+ doc `3159afb8`)

Plan doc: `docs/features/interface/ast-652-uat-remove-force-fit-autosize-list-table-columns.md` (Review section)

### Solid

- Stages 1–2 match plan: `.list-page-table` default is `width: auto` + `table-layout: auto`; removed `max-width: 0`, deleted `--auto` modifier, dropped `horizontalScrollable` prop/gate.
- Consumer cleanup: Agent Timesheets, Cost Reconciliation, job phase pages (inline auto removed), Scheduled Actions `%` widths removed (alignment-only styles kept).
- UAT intent satisfied: force-fit removed; horizontal scroll wrapper unchanged; AST-647 freeze/truncate untouched.
- Test: `AST-652: default list-page-table uses autosize layout` checks computed `table-layout: auto`.
- `grep` clean — no `horizontalScrollable` / `list-page-table--auto` in `src/ui/frontend`.

### advisory

- UAT: column drag-resize under auto layout (pixel widths still applied from ListPage localStorage).
- UAT: Scheduled Actions frozen sticky offsets (120px fallback carryover from AST-647) if not already verified.

**Verdict:** clean — no fix-now or discuss.

#### betty — 2026-06-14T23:56:26.258Z
## QA test manifest (AST-652)

**Publish ref:** `origin/sub/AST-633/AST-652-uat-remove-force-fit-autosize-columns` @ `8b2e748c` (`merge-tests(AST-652): origin/tests 150b8a39`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `961572ba212b7b10e452f93991388da50dfdf9ff` (§7.13zzt — AST-652 row added)

### 1. New / revised (this pass)

1. `tests/component/frontend/components/test_ListPage_listTableLayout.test.tsx` — **`AST-652: default list-page-table uses autosize layout`** (`table-layout: auto`, no `--auto` class)
2. `tests/component/frontend/components/test_ListPage.test.tsx` — removed obsolete `horizontalScrollable` prop from bulk-actions harness

### 2. Regression (AST-647 unchanged — re-run with AST-652)

3. `tests/component/frontend/lib/test_listTableLayout.test.ts`
4. `tests/component/frontend/components/test_ListTableTruncatedCell.test.tsx`
5. `tests/component/frontend/components/test_ListPage_listTableLayout.test.tsx` (frozen-column + truncate cases)
6. `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-647: phase table freezes first three data columns`**
7. `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_list_table_layout_defaults`

### Narrowed run (AST-652)

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ListPage_listTableLayout.test.tsx \
  ../../../tests/component/frontend/components/test_ListPage.test.tsx
```

### Manual (Susan UAT)

Agent Timesheets + Admin Scheduled Actions with many columns — columns widen to header/content; horizontal scrollbar when needed; frozen left columns still stick.

— Betty

#### katherine — 2026-06-14T23:25:07.573Z
Plan doc: [ast-652-uat-remove-force-fit-autosize-list-table-columns.md](https://github.com/susansomerset/astral/blob/sub/AST-633/AST-652-uat-remove-force-fit-autosize-columns/docs/features/interface/ast-652-uat-remove-force-fit-autosize-list-table-columns.md) @ `508809c4`

**Self-assessment**
- **Scope:** `minor` — CSS default change plus prop/class cleanup on existing list-table consumers; no new modules.
- **Conf:** `high` — AST-647 already defined `.list-page-table--auto`; this promotes that behavior to the default and removes the opt-in gate.
- **Risk:** `Medium` — all `.list-page-table` screens change width behavior; frozen sticky and scroll wrappers from AST-647 stay as-is.

Two stages: (1) fold auto layout into base `.list-page-table` CSS, drop `max-width: 0` shrink hack; (2) remove `horizontalScrollable` prop, redundant `--auto`/inline overrides, and Scheduled Actions `%` column widths.

---

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

## Review

- **Branch:** `origin/sub/AST-633/AST-652-uat-remove-force-fit-autosize-columns`
- **Diff:** `origin/dev...origin/sub/AST-633/AST-652-uat-remove-force-fit-autosize-columns`
- **Tip:** `8b2e748c`
- **Radia:** 2026-06-14 — **clean**

### What's solid

| Area | Assessment |
|------|------------|
| Plan fidelity | Stages 1–2 complete: `.list-page-table` → `width: auto` + `table-layout: auto`; `max-width: 0` removed; `--auto` class deleted; `horizontalScrollable` prop removed; consumer cleanup on Agent Timesheets, Cost Reconciliation, job phase pages, Scheduled Actions `%` widths dropped. |
| UAT intent | Force-fit-on-one-screen removed; autosize is now the default for all shared list tables; scroll wrapper unchanged. |
| §1.3 DRY | Redundant inline `tableLayout: "auto"` and `--auto` class removed; single CSS default. |
| Boundaries | No changes to frozen-column logic, truncation, sort/filter/resize/localStorage, or backend. |
| Tests | `AST-652: default list-page-table uses autosize layout` asserts computed `table-layout: auto` and no `--auto` class; obsolete `horizontalScrollable` test prop removed. |
| Grep gate | Zero matches for `horizontalScrollable` / `list-page-table--auto` under `src/ui/frontend`. |

### Issues

None — fix-now or discuss.

### Advisory

- **Column resize + auto layout:** ListPage still applies pixel `width` from localStorage/resize on th/td; confirm in UAT that drag-resize behavior still feels correct under `table-layout: auto` (plan notes explicit widths override natural sizing).
- **Scheduled Actions frozen offsets:** Still uses `stickyLeftPx` with 120px fallbacks (AST-647 carryover); plan explicitly defers — verify horizontal scroll alignment in UAT if not already done from AST-647 resolve-child.

### Recommended actions

Proceed to resolve-child / parent UAT — no code changes required from this review.

## Resolution

- **2026-06-14 (Katherine resolve-child):** No product commits — Radia review **clean** (no fix-now or discuss). **Advisory** items (column resize under auto layout; Scheduled Actions frozen offsets) left for **Susan UAT**.
- **§9a:** `origin/sub/AST-633/AST-652-uat-remove-force-fit-autosize-columns` @ `3159afb8` merges cleanly into **`origin/dev`** and **`origin/ftr/AST-633`**.
- **Outcome:** Ticket → **User Testing** (implementer assignee unchanged).
