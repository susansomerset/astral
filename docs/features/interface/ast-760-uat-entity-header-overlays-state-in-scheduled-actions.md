<!-- linear-archive: AST-760 archived 2026-06-23 -->

## Linear archive (AST-760)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-760/uat-entity-header-overlays-state-in-scheduled-actions-table-remove  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-744 — Remove column gap in scheduled_actions  
**Blocked by / blocks / related:** parent: AST-744

### Description

## What failed

After AST-758 local-dev delivery fix, Susan re-tested on local dev (2026-06-23). The Scheduled Actions phase table still mis-renders frozen headers: **Entity** `th` overlays **State** `th` (State appears behind Entity). Screenshots attached on parent comment.

## Expected

Frozen column headers align left-to-right: Candidate, Task, Entity, State — each visible and clickable; Entity must not cover State.

## Repro

1. Local `dev` after pull; `zsh launch.sh --flask`
2. Admin → Scheduled Actions
3. Expand a phase section with rows
4. Observe header row — State th hidden behind Entity th (see parent screenshots)

## Parent AC (quoted inline)

> There is a gap of whitespace between the Candidate and Task columns, and task and entity are shifted to the right, overlaying (and blocking) the State column value.

## Boundaries

* Does not change AST-758 [launch.sh](<http://launch.sh>) stale-dist delivery unless required for verification
* Fix product layout/measure in Scheduled Actions table only

### Comments

#### radia — 2026-06-23T19:32:58.325Z
### Review (`origin/dev`…`origin/sub/AST-744/AST-760-uat-entity-header-overlays-state-in-scheduled-actions`)

**Tip:** `25a000a` (includes doc commit) · product tip `716da64`

**Plan fidelity:** Stage 1 delivered — `scheduledFrozenStyle` reverted to **left-only** sticky (width/`minWidth`/`boxSizing` lock removed); AST-746 mount-on-expand, measure deps, and `predecessorsReady` gate preserved.

**Code rules:** §1.3 aligns with ListPage `frozenCellStyle` (left-only) plus AST-746 predecessor gate — intentional. §3.3 UI-only — clean.

**Product scope:** `AdminScheduledActions.tsx` vs `origin/dev` is an **11-line** hunk (this ticket only).

**Tests:** `AST-760` asserts Entity header has no inline `width`/`minWidth`, State unfrozen with no `left`; remeasure confirms sticky `left` without width lock.

**fix-now:** none

**discuss:** none

**advisory:** Full three-dot diff also includes **AST-751** test-bible/test manifest from `merge-tests` on the ftr/735 lineage — expected rollup noise; product code for AST-760 is isolated. Susan manual UAT still required for Entity/State header visibility and click targets.

**Doc:** [ast-760-uat-entity-header-overlays-state-in-scheduled-actions.md](https://github.com/susansomerset/astral/blob/25a000a/docs/features/interface/ast-760-uat-entity-header-overlays-state-in-scheduled-actions.md) § Review (Radia)

**Handoff:** Katherine → **resolve-child** (no code changes from review).

#### betty — 2026-06-23T19:31:06.354Z
## QA test manifest (AST-760)

**Publish:** `origin/sub/AST-744/AST-760-uat-entity-header-overlays-state-in-scheduled-actions` @ `716da64` (`merge-tests(AST-760): origin/tests 7326956`)

### 1. Existing coverage (re-run)
1. **`AST-647: phase table freezes first three data columns`** — frozen class wiring regression.
2. **`AST-746: phase table mounts on expand; measured sticky left avoids 120px fallback gap`** — mount-on-expand + no 120px fallback (gap regression guard).

### 2. New coverage
1. **`AST-760: frozen headers use left-only sticky; Entity does not width-lock over State`** — Entity header (index 2) has no inline `width`/`minWidth` after measure; State (index 3) unfrozen with no inline `left`; measured `left` on Entity still cumulative (`160px`).

### 3. Manual UAT (Susan — primary)
Local `dev`, `zsh launch.sh --flask` → Scheduled Actions → expand phase: Candidate, Task, Entity, State headers visible and clickable; Entity must not cover State; no Candidate/Task gap; horizontal scroll frozen alignment.

**Run (test-child):**
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-760|AST-746|AST-647"
```

**Pass criterion:** Vitest green on narrowed run + Susan manual header UAT.

**Bible:** `docs/test-bible/frontend/pages.md` shasum `5be81f983524cf5ccbabf2031921fbb3db764930` on publish ref.

**Builds on:** AST-746 product fix; AST-758 delivery unchanged.

#### katherine — 2026-06-23T19:29:15.209Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-744/AST-760-uat-entity-header-overlays-state-in-scheduled-actions/docs/features/interface/ast-760-uat-entity-header-overlays-state-in-scheduled-actions.md

**Self-assessment**
- **Scope:** `minor` — `scheduledFrozenStyle` in `AdminScheduledActions.tsx` only; remove AST-746 width/minWidth lock.
- **Conf:** `high` — ListPage uses left-only sticky; Entity frozen th (`z-index: 3`) + forced `minWidth` over State th (`z-index: 2`) matches Susan overlay screenshot.
- **Risk:** `low` — mount-on-expand + `predecessorsReady` + measured `left` retained; manual UAT catches gap regression.

**Root cause (for validate-plan):** AST-746 width lock on last frozen header expands sticky box over adjacent State column; drop width lock, keep measured `left` only.

---

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

---

## Resolution (2026-06-23)

**Engineer:** Katherine · **Review ref:** `origin/sub/AST-744/AST-760-uat-entity-header-overlays-state-in-scheduled-actions` @ `25a000a` (Radia doc) · product @ `716da64`

**Changes vs Radia review:** None required — **fix-now** and **discuss** were empty. Merged publish ref on epic worktree (including Radia **Review (Radia)** section); no additional product edits.

**§9a dry-run:** `origin/sub/…` merges cleanly into `origin/dev` and `origin/ftr/AST-744-remove-column-gap-in-scheduled-actions`.

**Advisory:** Susan manual UAT — expand phase on Scheduled Actions; confirm Entity does not cover State header, Candidate/Task gap absent, horizontal scroll frozen alignment (test-bible pass criterion).
