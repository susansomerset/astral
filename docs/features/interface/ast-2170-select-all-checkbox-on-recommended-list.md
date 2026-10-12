# Select All checkbox on Recommended list

- **Ticket:** [AST-2170](https://linear.app/astralcareermatch/issue/AST-2170)
- **Parent:** [AST-2166](https://linear.app/astralcareermatch/issue/AST-2166) — Add a Select All checkbox (and unchecking it selects none) to Recommended list
- **Publish ref:** `sub/AST-2166/AST-2170-select-all` (origin only)

Jobs → Review and Jobs → Ready are both rendered by the `Recommended` component in `JobsRecommended.tsx`, which already has per-row checkboxes, a page-level `selected` set, and a bulk bar (Skip / Applied / Generate Artifacts). This ticket puts a checkbox into each section table's currently empty select-column header. Checking it adds every job in that section to `selected`; unchecking removes them. Its checked state is derived from `selected` (no new state), so the bulk bar, `selectedIds`, `generateIds`, and the post-bulk clear all work unchanged.

## Canon Scope

Empty — no in-force directive governs frontend list pages (parent Architectural definition). Code precedent only, not canon: header checkbox in `src/ui/frontend/src/pages/AdminManageEmail.tsx` (`allSelected ? clearSelection() : selectAllVisible()`).

## Scope gate

Ticket `## Scope` names one file, `src/ui/frontend/src/pages/JobsRecommended.tsx`, **modified function** (`Recommended` page component): header checkbox in the empty select `<th>`, derived checked state, check adds the section's `astral_job_id`s, uncheck removes them, accessible name must not match `/^Select /`. Every step below is inside that file and that kind of change. No gap.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Add `setSectionSelected` callback; render header checkbox in each section's select `<th>` | ui (frontend) |

No other file. No CSS, no tests (Betty owns `tests/`), no hooks/lib changes.

## Stage 1: Header Select All / select-none checkbox

**Done when:** On Jobs → Review and Jobs → Ready, each section table's first header cell holds one checkbox that selects every row in its section when checked, clears them when unchecked, shows checked only when every row in the section is selected, and `npm run build` passes with no new lint problems.

1. In `src/ui/frontend/src/pages/JobsRecommended.tsx`, directly after the existing `toggleSelect` `useCallback` (the block ending `}), [])` just before `const sections = useMemo(`), add:

   ```tsx
   // Header Select All (AST-2170): add or remove a whole section's ids; other sections' picks are untouched.
   const setSectionSelected = useCallback((ids: string[], on: boolean) => setSelected(prev => {
     const next = new Set(prev)
     for (const id of ids) { if (on) next.add(id); else next.delete(id) }
     return next
   }), [])
   ```

   ⚠️ **Decision:** Uncheck removes **only this section's** ids, not `new Set()`. The ticket says "unchecking removes them" (the section's ids), and the page can show several sections at once; clearing everything would wipe selections in sibling sections. This differs from the `AdminManageEmail` precedent (single table, so `clearSelection()` is equivalent there).

2. In the same file, inside `sections.map(sec => { ... })`, directly after the existing line `const columnCount = 9 + manifest.jobs.recommended.phase_score_columns.length` (and its preceding comment line), add:

   ```tsx
   const sectionIds = sec.jobs.map(j => j.astral_job_id)
   // Derived, never stored: checked only when every row in this section is selected (sections are never empty).
   const allSectionSelected = sectionIds.every(id => selected.has(id))
   ```

   ⚠️ **Decision:** Derive from `sec.jobs` (the unsorted section list) rather than `sorted` — same id set, and it avoids coupling to sort. `every()` is safe without an empty guard because `sections` already filters out states with zero jobs (`.filter(row => (byState[row.state]?.length ?? 0) > 0)` and `.filter(s => byState[s]?.length)`).

3. In the same file, replace the self-closing header cell

   ```tsx
   <th style={{ width: 1 }} aria-label="Select" />
   ```

   with

   ```tsx
   <th style={{ width: 1 }} aria-label="Select">
     <input
       type="checkbox"
       aria-label={`All jobs in ${sec.label}`}
       checked={allSectionSelected}
       onChange={() => setSectionSelected(sectionIds, !allSectionSelected)}
     />
   </th>
   ```

   ⚠️ **Decision — accessible name:** `All jobs in <section label>`. It does **not** match `/^Select /` (AC 7), so `getAllByRole("checkbox", { name: /^Select / })` keeps counting rows only, and it is distinct per section so tests can target one section's header. Do not use "Select all…" — it matches `/^Select /`.

   ⚠️ **Decision — click semantics:** `!allSectionSelected` gives: none or some selected → select all (AC 2, AC 4); all selected → select none (AC 3). No indeterminate state (ticket Boundaries).

   ⚠️ **Decision — keep `aria-label="Select"` on the `<th>`:** unchanged column-header name; the checkbox's own `aria-label` sets its name, so the `th` label does not leak into it. The header `<tr>`/`<th>` has no click handler, so no `stopPropagation` is needed (unlike row cells).

4. Make no other edits. In particular, do not touch `selectedIds`, `generateIds`, `handleBulkDone`, the bulk bar, row checkboxes, sorting, or the Analysis toggle. AC 5 (header follows manual row ticks) and AC 6 (header clears after bulk action, via the existing `setSelected(new Set())` in `handleBulkDone`) fall out of the derived state with no extra code.

5. Compile and lint, from `src/ui/frontend`:
   - If `node_modules` is missing (it is absent in the epic worktree as of plan time — `eslint` fails with `Cannot find package '@eslint/js'`), run `npm ci` first.
   - **Baseline (do this before Step 1's edit):** `npm run lint > ../../../debug/spikes/ast-2170-lint/before.txt 2>&1` (create the folder first). At plan time `git diff origin/dev HEAD -- src/ui/frontend` is empty, so this pre-edit run *is* the `origin/dev` baseline. If that diff is non-empty when you build, stop and comment — the baseline assumption no longer holds.
   - After the edit: `npm run build` must exit 0.
   - After the edit: `npm run lint > ../../../debug/spikes/ast-2170-lint/after.txt 2>&1`; diff against `before.txt`. Any problem in `after.txt` absent from `before.txt` fails AC 9 → fix before commit.

6. Commit on the epic worktree as `code(AST-2170): select-all header checkbox on Recommended list` and publish per build-child (`git push origin HEAD:sub/AST-2166/AST-2170-select-all`).

## AC trace

| AC | Covered by |
|----|------------|
| 1 Header checkbox exists | Step 3 (one `<input>` in the first `<th>`) |
| 2 Select All | Steps 1–3 (`!allSectionSelected` = true → add all section ids; bulk bar counts from `selectedIds`) |
| 3 Select none | Steps 1–3 (all selected → remove section ids → `selectedIds` empty → bar hidden) |
| 4 Partial → all | Step 3 (`every()` false with one row → click selects all) |
| 5 Manual all → header checked | Step 2 (derived from `selected`) |
| 6 Bulk action clears | Step 4 (existing `handleBulkDone` clears `selected`; header derives unchecked) |
| 7 Row-checkbox queries unaffected | Step 3 name decision |
| 8 Same on Ready | Same component serves both routes (`view` prop) — no route-specific code |
| 9 Build + lint | Step 5 |

## Execution contract

Execute steps in order; do not add files, state, CSS, or helpers beyond the above. If the file has drifted (e.g. `toggleSelect`, `columnCount`, or the `<th aria-label="Select" />` line no longer exists as quoted) — stop and comment on [AST-2166](https://linear.app/astralcareermatch/issue/AST-2166) with the 🛑 format from plan-child. Do not edit `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 1 — agree
