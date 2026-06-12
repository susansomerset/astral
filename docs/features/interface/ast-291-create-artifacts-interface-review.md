# ast-291: Create Artifacts Interface — Code Review

**Branch:** `<agent>/ast-291-create-artifacts-interface`
**Commits reviewed:** 3
**Reviewer:** Chuckles

---

## Overall Assessment

**Ship it.** Clean implementation across a wide surface area — new component, 7 page wrappers, ListPage sort/resize enhancements, nav collapse, scrollbar theming. No functional bugs found. A few observations worth tracking.

---

## Commit `7d45e4a` — Plan document

Thorough plan covering data model (base resume dict, rubric arrays), component design (SideTabPanel, ArtifactEditor), nav/route wiring, and token resolution impact. Open questions were resolved in-conversation before implementation began.

---

## Commit `b595630` — Artifacts interface + UI enhancements

### SideTabPanel (`components/SideTabPanel.tsx`)

**Clean component.** Vertical tabs on the left, textarea on the right. Two modes: fixed (labels locked) and editable (rename, reorder, add/remove).

**`genId()` uses module-level counter + `Date.now()`:**

```tsx
let _nextId = 0
function genId() { return `st_${Date.now()}_${_nextId++}` }
```

This is fine for the current single-user model. If the component were ever rendered in SSR or concurrent mode, the module-level counter could cause issues. Not a concern for this app.

**`activeId` initializes from `tabs[0]?.id`** — correct for mount, but if the parent replaces the entire `tabs` array (e.g., on candidate switch), `activeId` would reference a stale ID. The `activeTab` fallback (`?? tabs[0]`) handles this gracefully — the textarea still renders correctly. Minor: the tab list would show nothing highlighted until the user clicks. Low risk given the current usage pattern where candidate switches trigger a full remount via the `key` or route change.

**Double-click to rename** is discoverable for power users but not obvious. Acceptable for the "just need it to work" scope — a future iteration could add a pencil icon or tooltip.

### ArtifactEditor (`pages/Artifacts/ArtifactEditor.tsx`)

**Two-phase loading for fixed-tab mode** (shapes fetch, then candidate fetch) is correctly sequenced — the candidate data effect gates on `fixedFields` being populated.

**`buildPayload` references `fixedFields` from the component scope but is called inside `doSave`** which is a `useCallback` with deps `[selectedId, artifactKey, editable]`. Since `fixedFields` is derived from `shapeFields` state, technically `buildPayload` could close over a stale `fixedFields` if shapes were re-fetched. In practice `shapesKey` never changes (it's a static prop), so `shapeFields` is fetched once and stays stable. The eslint-disable comment is justified but should note this reasoning.

**Cancel button uses `window.location.reload()`** — effective but blunt. A more React-idiomatic approach would re-fetch the candidate data and reset state. Acceptable for v1, worth noting as a future refinement.

**Auto-save cleanup (`useEffect` return):** Calls `doSave(tabsRef.current)` on unmount if dirty. This is an async function called during cleanup — React won't await it, so if the component unmounts before the fetch completes, the save might be silently dropped. The `beforeunload` handler provides a second safety net for browser tab closes, but in-app navigation could still lose the final save if the debounce timer just fired and the unmount cleanup races the fetch. In practice, the 2-second debounce means most changes are saved before navigation. Low risk.

### ListPage enhancements

**Multi-column default sort** is clean. `defaultSort` is memoized from columns, `userSort` overrides to single-column when the user clicks a header. The `handleSort` function correctly respects `defaultDesc` when first clicking a column.

**Column resize handle** — the `onMouseDown` → document `mousemove`/`mouseup` pattern is correct. The cleanup effect (`dragRef.current = null` on unmount) prevents orphaned listeners. The `Math.max(40, ...)` minimum width prevents columns from collapsing to zero.

**`table-layout: fixed`** is only applied via the `.resized` class when at least one column has been manually sized. Smart — auto-layout is preserved until the user intentionally resizes.

**Sort indicator only shows for user-clicked column** (`primarySortKey`), not for the default multi-column sort. This is the right UX — showing arrows on every column when using the default sort would be noisy.

### NavigationShell collapse

**`collapsed` state is a `Set<string>` keyed by group label.** Clean. If two groups ever had the same label, they'd toggle together — but nav group labels are unique by convention.

**Chevron rotation via CSS transform** is smooth. The `▾` character rotates to point right when collapsed — correct visual metaphor.

### Scrollbar theming

Global scrollbar styling via `::-webkit-scrollbar` with Firefox fallback (`scrollbar-width: thin; scrollbar-color`). Uses existing design tokens. Clean.

### Config changes

**NAV_CONFIG:** Artifacts group correctly positioned between Companies and Candidate, with `"visible": "CONTEXT_READY"`. Seven items with snake_case paths matching the route definitions.

---

## Commit `6bfcd09` — Code rules alignment + shapes-driven base resume tabs

**`base_resume_structure` in DATA_SHAPES:** Nine entries with `key`, `label`, `type: "str"`. Consistent with how other shape definitions work. The `type: "str"` field is present for future use (when fields might become lists or structured types).

**ArtifactEditor refactored from `fixedTabs` prop to `shapesKey`:** Now fetches tab definitions from the shapes API instead of receiving a hardcoded array. This keeps the frontend consistent with the Profile page's shapes-driven approach. `BaseResumeContent.tsx` went from 16 lines to 4.

**Profile.tsx dynamic halving:** `Math.ceil(fields.length / 2)` replaces hardcoded `slice(0, 4)` / `slice(4, 8)`. Adding a 9th contact field would produce a 5/4 split automatically. Correct.

**ASTRAL_CODE_RULES.md:** Directory layout updated with `Artifacts/`, `SideTabPanel.tsx`, `TabbedTextArea.tsx`, `TokenTextarea.tsx`. Accurate reflection of current state.

---

## Cross-cutting concerns

**No backend changes.** All 7 pages use the existing `PUT /api/candidates/:id/data` endpoint with merge semantics. No new API endpoints, no database schema changes. This is the right call for v1.

**No tests added.** Consistent with codebase conventions.

**Layer rules verified.** Frontend calls API endpoints → core → data. No direct imports from data or external layers. Visibility gating is config-driven via NAV_CONFIG.

---

## Summary of actionable items

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | Low | `ArtifactEditor.tsx` | Cancel button uses `window.location.reload()` — consider re-fetch + state reset |
| 2 | Low | `ArtifactEditor.tsx` | Auto-save on unmount is fire-and-forget async — could race on fast navigation |
| 3 | Note | `SideTabPanel.tsx` | `activeId` could go stale on full tab replacement without remount |
| 4 | Note | `SideTabPanel.tsx` | Double-click to rename is not discoverable — future: add pencil icon or tooltip |
| 5 | Note | `ArtifactEditor.tsx` | eslint-disable on `doSave` deps should document why `buildPayload`/`fixedFields` exclusion is safe |

None are blockers. Items 1–2 are minor robustness improvements for a future iteration. Items 3–5 are informational.

---

## Independent review — Chuckles

**Branch:** `<agent>/ast-291-create-artifacts-interface`
**Commits reviewed:** `b595630`, `6bfcd09`

---

### Overall

Clean, well-scoped feature. The `SideTabPanel` / `ArtifactEditor` split is the right abstraction — 7 page wrappers are each 4 lines and the shared logic lives in one place. The ListPage enhancements (resize, multi-sort, collapse) are genuinely useful additions that don't bloat the component. A handful of real issues worth fixing; nothing that should block merge.

---

### `SideTabPanel.tsx`

**`genId()` uses a module-level counter.** That's fine, but the counter never resets between hot-reloads in dev. IDs like `st_1704000000000_47` are stable enough for React keys, but they make snapshot tests brittle if those are ever added. Low risk in production.

**`activeId` initializes from `tabs[0]?.id` once.** If the parent swaps the full `tabs` array (e.g., candidate switch without unmount), `activeId` holds a stale ID. The `activeTab` fallback `?? tabs[0]` saves the textarea from blowing up, but the tab list shows nothing highlighted — the user would see no active tab until they click. The existing review flags this; confirming it's real and worth a future fix.

**Double-click to rename enters edit mode, but a single click on an already-active tab does not.** This is a reasonable UX choice for the "just need it to work" scope, but worth documenting as intentional so it doesn't get filed as a bug.

**`removeTab` sets `activeId` to `next[0]?.id ?? ""`** — if removing the last tab drops to `minTabs=1`, this is fine. If `next` is empty (which can't happen given the `minTabs` guard), it would set an empty string. The guard makes this safe; just confirm the guard always fires before `setActiveId`.

**`addTab` immediately sets `editingId` to the new tab's ID** — gives auto-focus on the rename input. Good UX.

---

### `ArtifactEditor.tsx`

**`fixedFields` derivation is fragile:**

```tsx
const editable = !shapesKey
const fixedFields = shapeFields && shapeFields.length > 0 ? shapeFields : null
```

`fixedFields` is `null` if `shapeFields` is an empty array. The second `useEffect` gates on `(shapesKey && !fixedFields)` — so if the shapes API returns an empty array for `base_resume_structure`, the data-load effect never runs and the page stays on the loading spinner forever. The shapes API shouldn't return empty for a valid key, but a network error or misconfigured key would produce silent hang rather than an error state.

**`doSave` excludes `buildPayload` and `fixedFields` from its deps via eslint-disable.** `buildPayload` references `fixedFields` which is derived from `shapeFields` state. Since `shapesKey` is a static prop that never changes at runtime, `shapeFields` is fetched once — so `fixedFields` is stable after mount. The exclusion is safe but the comment should say why (as the earlier review also noted).

**Cancel button calls `window.location.reload()`.** For fixed-tab (base resume) mode only. This works but loses all in-tab state, including any scroll position in the sidebar. A re-fetch + state reset would be cleaner. Acceptable for v1; flagging for future.

**Auto-save on unmount fires `doSave(tabsRef.current)` as fire-and-forget.** React doesn't await cleanup functions. If the component unmounts in the middle of a 2-second debounce window (user navigates away quickly), the cleanup fires and starts a fetch that may or may not complete. The 2-second debounce means most typing is already flushed — low risk in practice, but not a guarantee.

**`"All changes saved"` status shows on initial load before any edit.** On first render of a criteria page, `dirty=false` and `saving=false`, so the status reads "All changes saved" even though nothing has been saved in this session. Consider a third state (e.g., `null` / no message) until the first save completes. Minor UX.

---

### `ListPage.tsx` enhancements

**Multi-column default sort is clean.** `defaultSort` memoizes from `columns`, single-column `userSort` overrides. `cmpValues` uses `localeCompare` with `{ numeric: true }` — correct for fields that mix numbers and strings (e.g. "10" sorts after "9").

**Column resize cleanup:** The `dragRef.current = null` assignment in `onUp` clears the ref, and the document listeners remove themselves. No leak. The `useEffect` on unmount isn't actually needed for the listeners (they self-remove on mouseup), but the absence of it is fine since the self-cleanup is correct.

**`table-layout: fixed` only applied via `.resized` class** — smart. Auto-layout preserved until user intentionally resizes. One edge case: if the user resizes, navigates away, and comes back, `colWidths` resets to `{}` (component re-mounts), so the table returns to auto-layout. No persistence. This is the right behavior for v1.

**`primarySortKey` (the user-clicked column) drives the sort indicator; default multi-sort has no indicator.** Correct — showing arrows on all columns during the default sort would be noise.

---

### `NavigationShell.tsx`

**`collapsed` state is a `Set<string>` keyed by group label.** If two nav groups ever share a label, they'd toggle together. Nav group labels are unique by convention; this is fine.

**Collapse state is not persisted.** Each page load starts fully expanded. For a sidebar with many groups (currently not a concern), this could be annoying. `localStorage` persistence would be a one-line addition. Not needed now.

---

### `config.py` / `DATA_SHAPES`

**`base_resume_structure` keys** (`candidate_name`, `candidate_title`, etc.) don't match the keys produced by the existing `parse_resume_text` task (`name`, `email`, `phone`, etc.). This is documented in the plan as a known mismatch — existing parse output won't appear under the new keys. The editor will show empty fields for any candidate whose `base_resume` was written by the old task. **This is a real UX gap that should be tracked as a follow-up ticket** — existing candidate data is invisible in the new UI.

**`DATA_SHAPES` placement in `config.py`** is correct — alongside other candidate shapes. The `type: "str"` field on each entry is forward-looking (for list/structured types later). Good.

---

### `Profile.tsx`

**`Math.ceil(fields.length / 2)` replaces hardcoded `slice(0, 4)` / `slice(4, 8)`.** Correct and more robust. For 9 contact fields: 5 left / 4 right. Clean.

---

### Cross-cutting

**No new API endpoints, no schema changes.** Reuses `PUT /api/candidates/:id/data` merge semantics. Correct call for v1.

**Nav visibility gate `"CONTEXT_READY"`** matches the existing pattern for Candidate section artifacts. Correct.

**The plan acknowledges the base_resume key mismatch** and defers to a future migration. That's fine, but whoever picks up that migration needs to know the new keys are already being written by this editor. If both the old parse task and the new editor run against the same candidate, the `base_resume` dict will contain a mix of old keys (from parse) and new keys (from editor saves). The merge semantics of the PUT endpoint will preserve both sets — no data loss, but potentially confusing prompt output until migration is complete.

---

### Summary of actionable items

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | Medium | `ArtifactEditor.tsx` | If shapes API returns empty array for `shapesKey`, page silently hangs on loading spinner — no error state |
| 2 | Low | `ArtifactEditor.tsx` | "All changes saved" shown on initial load before any save has occurred |
| 3 | Low | `ArtifactEditor.tsx` | Cancel reloads the page; re-fetch + state reset would be cleaner |
| 4 | Low | `ArtifactEditor.tsx` | `doSave` on unmount is fire-and-forget; fast navigation could drop the final save |
| 5 | Low | `SideTabPanel.tsx` | `activeId` goes stale on full tab replacement without remount — tab list shows no active item |
| 6 | Note | `config.py` / `DATA_SHAPES` | `base_resume_structure` keys don't match existing `parse_resume_text` output — existing candidate data won't appear in the editor until a migration runs |
| 7 | Note | `ArtifactEditor.tsx` | `eslint-disable` on `doSave` deps needs an inline comment explaining why the exclusion is safe |

Items 1–2 are the ones worth addressing before this ships to real users. The rest are polish or known deferreds.

