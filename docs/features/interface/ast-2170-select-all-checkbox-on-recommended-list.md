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

## Joan validate

[plan-rubric]

**Ticket:** AST-2170  
**Overall:** APPROVED  
**Corpus:** 0d01e20d2b313a4e35cf3d07434b6cd69f615768  
**Publish ref:** `ff5c157bfc1bc575f8cca4cec6ade9c9d653378e` (`origin/sub/AST-2166/AST-2170-select-all`)

## Canon scores

_(empty list — child **Citations:** none; parent **Architectural definition** explicitly records no in-force directives for frontend list pages, same precedent as AST-1968 on this page. Nothing to score; Radia’s column on this ticket is likewise empty.)_

## Traceability

AC1–AC9 → Stage 1 (steps 1–5; plan **AC trace** table); no orphan stages; no unmapped child AC.

## Findings

### discuss

- **Location:** Stage 1 step 5 vs **Execution contract**  
- **Finding:** Step 5 directs creating `debug/spikes/ast-2170-lint/{before,after}.txt`, while the execution contract says not to add files beyond the described product change.  
- **Recommendation:** Treat spike outputs as ephemeral local verification only (do not commit), or reword step 5 to run `npm run lint` and compare to a one-off local baseline without implying repo paths—so build-child does not contradict the contract.

### discuss

- **Location:** Canon Scope (intentional empty)  
- **Finding:** Directives such as `astral.standards.in-scope-only` would apply to any product edit but are not on this child’s frozen list (by parent design).  
- **Recommendation:** No list change required for this pass; Archie may keep empty frontend canon as precedent or add a minimal frontend slice at a parent if mechanical comparability is desired later.

### acceptable

- **Location:** Stage 1 step 5 (lint vs `origin/dev`)  
- **Finding:** AC 9 is satisfied by build + lint delta discipline; the quoted anchor lines (`toggleSelect`, `columnCount`, empty `<th aria-label="Select" />`) still match the epic worktree at review time.  
- **Recommendation:** None—execute as written once spike-path wording is clarified per discuss item above.

### acceptable

- **Location:** Stage 1 decisions (section-scoped uncheck, `aria-label`, no indeterminate)  
- **Finding:** Plan matches parent functional scope, child **Scope**, and boundaries; multi-section behaviour (uncheck clears only that section’s ids) is correctly argued vs `AdminManageEmail` single-table precedent.  
- **Recommendation:** None.

### acceptable

- **Location:** R6 self-assessment  
- **Finding:** Single-stage plan, estimate confirm 1, scope gate explicit; no scope creep into tests, bulk bar, or sibling tickets.  
- **Recommendation:** None.

context_tokens≈14500

## Review

- **Build tip:** `origin/sub/AST-2166/AST-2170-select-all` @ `4ba6be820` — `code(AST-2170): select-all header checkbox on Recommended list`
- **Compile/lint:** `npx tsc -b --noEmit` 0; `npm run build` 0; `npm run lint` problem list identical to pre-edit baseline (29 pre-existing, 0 new). Lint before/after kept local under `debug/spikes/ast-2170-lint/` (gitignored, uncommitted).
- **Canon Scope:** empty — nothing to verify.

## Radia review

[code-rubric]

**Ticket:** AST-2170  
**Publish ref:** `a58e4c8e2ae570a487cd4b3e4bc59afc263a1a36` (`origin/sub/AST-2166/AST-2170-select-all`)  
**Corpus:** `0d01e20d2b313a4e35cf3d07434b6cd69f615768`  
**Overall:** CLEAN  

## Canon scores

Frozen list empty (`## Citations`: none — parent Architectural definition). No directive rows to score; worst-grade roll-up N/A.

## Column diff vs plan stage

(aligned) — Joan’s plan-stage canon table was likewise empty; no id-level column to diff.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** `tests/component/frontend/pages/test_JobsRecommended.test.tsx`, `docs/test-bible/frontend/pages.md`  
- **Finding:** Plan **Files Changed** / **Execution contract** describe product-only work in `JobsRecommended.tsx`; the publish tip also carries Betty’s `test(AST-2170)` + bible block (`a58e4c8e2`, `a23c7ab81`). Expected pipeline ownership (`orch.git.betty-tests-on-sub`), not engineer scope creep on the code commit (`4ba6be820`).

- **Location:** `docs/test-bible/frontend/pages.md` — **Not pinned**  
- **Finding:** Section-scoped uncheck (plan decision vs `AdminManageEmail`) is intentionally untested because AST-1975 renders one section per view; product code still implements multi-section-safe `setSectionSelected`. Documented gap only.

- **Location:** Issue doc `## Review` stub  
- **Finding:** Local stub still cites tip `4ba6be820` (code-only); Chuckles should append this pass at `a58e4c8e2` so the doc matches the reviewed tip (tests + bible).

## What’s solid

- **Plan fidelity:** `JobsRecommended.tsx` matches Stage 1 steps 1–3 — `setSectionSelected`, derived `allSectionSelected` from `sec.jobs`, header checkbox with `aria-label={`All jobs in ${sec.label}`}` (does not match `/^Select /`), `onChange` via `!allSectionSelected`. No bulk bar, row handlers, or sort changes.
- **AC coverage:** Five nested component cases exercise AC1–AC8; AC7 uses `/^Select /` row-only query; Ready/review parametrized for AC8.
- **Footprint:** Estimate **1** still fits (single focused product edit + standard qa manifest).

## Recommended actions (downstream — not executed here)

- Chuckles: append this artifact to `docs/features/interface/ast-2170-select-all-checkbox-on-recommended-list.md`, commit/push docs on `sub/AST-2166/AST-2170-select-all`, post slim upshot `--as radia`, move to **Review Posted**.
- **PROCEED** path: datt may route to **User Testing** without `resolve-child` product work unless Susan wants the unpinned multi-section behavior tested later (product call only if epic layout regains multi-section pages).

## Notes

- **Canon Scope:** Intentionally empty; off-list statutes (e.g. `astral.standards.in-scope-only`) were parent-by-design — not a §5.3 ESCALATE (Joan already flagged for Archie precedent only).
- **Diff baseline:** `origin/dev...origin/sub/AST-2166/AST-2170-select-all` — 4 files, +274/−1; no `src/data/**` or migrations.
- Did not re-run `npm run test:component` / build locally; **Tests Passed** + manifest in bible treated as gate evidence.

context_tokens≈32000
