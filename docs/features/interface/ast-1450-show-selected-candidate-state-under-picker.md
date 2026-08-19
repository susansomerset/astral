# AST-1450 — Show selected candidate state under picker

**Linear:** [AST-1450](https://linear.app/astralcareermatch/issue/AST-1450/show-selected-candidate-state-under-picker)  
**Parent:** [AST-1444](https://linear.app/astralcareermatch/issue/AST-1444/remove-navigation-filter-for-selected-candidate)  
**Publish ref:** `sub/AST-1444/AST-1450-show-selected-candidate-state-under-picker`

Pinned left-nav chrome shows a candidate picker (wide `<select>`, narrow menu) and no live state name. This ticket adds one read-only text line under that picker, in both layouts, showing the selected candidate’s stored `state` string exactly as `/api/candidates` already returns it. It does not gate nav, does not edit `NAV_CONFIG`, and does not add a state editor.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/NavigationShell.tsx` | Resolve the selected candidate row; render a read-only state line under the wide select and under the narrow picker toggle | ui |
| `src/ui/frontend/src/App.css` | TOC `4d`; style `.sidebar-candidate-state` as muted non-editable text under the picker | ui |

No API modules, no `NAV_CONFIG` / `src/utils/config.py`, no `CandidateContext.tsx` contract change, no new React files, no test-tree edits (Betty owns `tests/`).

## Stage 1: Read-only state line under the picker (wide and narrow)

**Done when:** With a candidate selected, pinned chrome shows that candidate’s exact `state` string immediately under the picker control (wide native select and narrow toggle). Changing the selected candidate updates the line to that row’s `state`. Empty candidate list, or no matching selected row, or a missing/blank `state`, means the line is omitted. The line is not an input. Nav membership and who may switch candidates are unchanged.

1. In `src/ui/frontend/src/components/NavigationShell.tsx`, keep the existing `useCandidate()` usage (`candidates`, `selectedId`, `setSelectedId`). Do **not** add a new fetch. Do **not** import `NAV_CONFIG`. Do **not** compare `state` to resume-ready / active-search (or any other) thresholds.

2. `CandidateContext` sets `selectedId` from `CandidateInfo.astral_candidate_id` (`src/ui/frontend/src/contexts/CandidateContext.tsx`). List payloads and Betty’s `tests/component/frontend/components/test_NavigationShell.test.tsx` fixture also carry `astral_candidate_id`. Immediately after the existing `selectedCandidate` / `selectedLabel` block, add:

   ```tsx
   const selectedRow =
     candidates.find(c => c.astral_candidate_id === selectedId)
     ?? candidates.find(c => c.astral_candidate_id === selectedId)
     ?? selectedCandidate
   const selectedState =
     typeof selectedRow?.state === "string" ? selectedRow.state.trim() : ""
   ```

   Render the stored string as-is after `trim`. Do **not** map it through `CANDIDATE_STATES` families, `progress_rank`, retry/error companion labels, or any display alias table. Companion keys such as retry/error states appear as their stored names when that is what `state` is.

3. Build one element (reuse the same JSX variable in both layouts — do not extract a new file under `components/`):

   ```tsx
   const candidateStateLine = selectedState ? (
     <p className="sidebar-candidate-state">{selectedState}</p>
   ) : null
   ```

   Use a `<p>` (or `<div>`) with **no** `contentEditable`, **no** `<input>` / `<select>` / `<textarea>`, **no** `onChange` that writes state. Do not add a “State” heading or a tooltip that rewrites the name.

4. Insert `candidateStateLine` in **both** chrome branches, still inside `{candidates.length > 0 && (…)}` and still inside `.sidebar-chrome`:

   - **Wide** (`isWide`): inside `.sidebar-candidate-select`, immediately after the existing `<select>…</select>`, before the wrapping `</div>`.
   - **Narrow**: inside `.sidebar-candidate-menu`, immediately after the existing `.sidebar-candidate-menu-toggle` `<button>`, **before** the `{candidateMenuOpen && ( <ul>…` list. The line stays under the toggle when the menu is open; do not put it after the `<ul>`.

   Do not add a second logo, a second picker, or a duplicate state line outside `.sidebar-chrome`. Do not move `.sidebar-chrome` / `.sidebar-scroll` structure (AST-1369). Do not change `isAdmin` / `disabled={!isAdmin}` / `setSelectedId` gating.

5. In `src/ui/frontend/src/App.css` TOC (top comment), after `4c. Pinned left-nav chrome (AST-1369)`, add:

   `*  4d. Selected candidate state under picker (AST-1450)`

   Append `4d`; do not renumber the rest of the TOC.

6. After the existing `.sidebar-candidate-select select:focus` block (still in section 4, before `/* === 4c. Pinned left-nav chrome (AST-1369) === */`), add:

   ```css
   /* === 4d. Selected candidate state under picker (AST-1450) === */
   .sidebar-candidate-state {
     margin: 6px 0 0;
     padding: 0;
     border: none;
     background: none;
     font-family: inherit;
     font-size: 12px;
     line-height: 1.3;
     color: var(--text-secondary);
     word-break: break-word;
   }
   ```

   Do not change `.sidebar` overflow, `.sidebar-chrome` / `.sidebar-scroll` flex rules, hamburger/drawer media queries, or picker control dimensions except this new class. Do not introduce a new color literal; use `--text-secondary`.

7. Do **not** edit `src/ui/api/api_candidate.py`, `src/utils/config.py` (`NAV_CONFIG`), `CandidateContext.tsx` field names, or any page under `src/ui/frontend/src/pages/`. Do **not** add polling; the line follows the in-memory `candidates` list already loaded by `CandidateProvider` (updates when the operator changes `selectedId` or when `refresh()` reloads the list).

⚠️ **Decision:** Dual-key row lookup (`astral_candidate_id` then `astral_candidate_id`) — `selectedId` is typed as `astral_candidate_id` while the shell’s current `selectedCandidate` find and the component test fixture use `astral_candidate_id`. One `??` chain binds the line to whichever key the live list actually carries. Do not “fix” the picker label lookup in this ticket beyond sharing `selectedRow` if you already have it; picker behavior stays as today.

⚠️ **Decision:** No API change — `list_candidates` already JSON-serializes each candidate dict including `state` (`src/ui/api/api_candidate.py` → `core_list_candidates`). Duplicating state on `/api/nav_config` would move business data into the nav payload and is out of scope.

⚠️ **Decision:** Omit the line when `selectedState` is empty rather than rendering a placeholder — parent: no candidate selected or empty list means no state line; a blank stored `state` is the same omission.

## Boundaries (do not do)

- Do not hide, show, enable, or disable nav groups/items from this component (sibling AST-1449 / Ada).
- Do not add candidate state editing in the nav.
- Do not invent display aliases (`ACTIVE` → “Active”, family names, progress ranks).
- Do not change who may switch the selected candidate.
- Do not redesign pinned chrome beyond this one line in existing wrappers.
- Do not edit `tests/` (Betty). If `test_NavigationShell.test.tsx` needs assertions for the new `<p class="sidebar-candidate-state">`, that is a follow-up on `tests`.

## Traceability

| AC | Where |
|----|--------|
| Selected candidate → exact current state name directly below the picker; not editable | Stage 1 steps 2–4 (`<p className="sidebar-candidate-state">`, no inputs) |
| Selecting a different candidate updates the displayed state | Stage 1 step 2 (`selectedId` → `selectedRow.state`); same React render as the picker `onChange` / menu `setSelectedId` |
| Narrow shell: same read-only line below the picker control | Stage 1 step 4 narrow insertion (after toggle, before list) |
| Empty list / no selection → no line | Stage 1 steps 3–4 (`selectedState` falsy → `null`; still inside `candidates.length > 0`) |
| Live stored name including retry/error companions | Stage 1 step 2 (raw `state` string, no alias map) |

## Estimate

Confirm Chuckles estimate: 2 — agree
