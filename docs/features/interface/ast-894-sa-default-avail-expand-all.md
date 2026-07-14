# Default Avail > 0 and expand all visible sections on load

**Linear:** [AST-894](https://linear.app/astralcareermatch/issue/AST-894/default-avail-0-and-expand-all-visible-sections-on-load-default-the)  
**Parent:** [AST-888](https://linear.app/astralcareermatch/issue/AST-888)  
**Publish ref:** `sub/AST-888/AST-894-sa-default-avail-expand-all`

On Admin → Scheduled Actions landing, default the existing Avail filter to `> 0` and expand every section that still has rows under the current filters (using the shared Expand All policy from AST-886 / AST-893), so every section with available entities is visible at once instead of requiring the operator to engage the filter and open sections one by one.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Default Avail to `gt0`; replace first-section-only landing auto-open with one-shot expand-all-visible via `expandAllSections` | ui |

**Out of scope (this ticket):** Available calculation / claim / dispatch; Avail column formatting (`formatAvailableCount`); new Avail modes or server query params; Run / Stop / AUTO / edit-modal / Manage Tasks; other sectioned screens’ default expansion; re-implementing Expand All (keep `useSectionExpandPolicy({ expandAll: true })`); any edit under `tests/` or `docs/test-bible/**` (Betty owns those after Code Complete).

**QA note (Betty — not engineer commits):** Existing `test_AdminScheduledActions.test.tsx` asserts Avail defaults to All (`AST-887`) and relies on AST-785 first-section auto-open (`expandFirstPhaseSection`). Update those expectations for default `gt0` + all matching sections expanded on load.

---

## Stage 1: Default Avail > 0 and expand-all landing

**Done when:** Fresh load of Scheduled Actions shows Avail as `> 0` without the operator touching the control; with matching rows in more than one section under that filter, every non-empty section is expanded at once; the operator can still collapse a section afterward; switching Avail back to All restores zero/null Avail rows that match other filters. No other files change.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, change the Avail filter initial state from not engaged to engaged:

   ```ts
   const [availGtZeroFilter, setAvailGtZeroFilter] = useState("gt0") // "" | "gt0"
   ```

   Keep the select options exactly as today (`All` = `""`, `> 0` = `"gt0"`). Do not change the `filteredRows` predicate (`(r.available_count ?? 0) > 0` when `gt0`), AND intersection with other filters, or empty-section omission.

2. Replace the AST-785 first-section-only landing auto-open effect (the `useEffect` that currently does `setExpandedKeys(new Set([sections[0].sectionKey]))` behind `didAutoOpenSectionRef`) with a one-shot expand-all of every currently visible section:

   ```ts
   useEffect(() => {
     if (didAutoOpenSectionRef.current || sections.length === 0) return
     didAutoOpenSectionRef.current = true
     expandAllSections()
   }, [sections, expandAllSections])
   ```

   Keep `didAutoOpenSectionRef` (still declared near the other refs) so this runs once when sections first become non-empty after load — not on every filter-driven `sectionKeys` change (operators who collapse a section after landing must not be re-forced open). Keep the existing stale-key cleanup effect that drops keys no longer in `sectionKeys` under Expand All. Do not change `useSectionExpandPolicy({ expandAll: true, sectionKeys })` or `SectionExpandChrome` wiring.

3. Do not edit `useSectionExpandPolicy.ts`, `SectionExpandChrome.tsx`, other pages, API modules, or config.

⚠️ **Decision:** One-shot landing expand (guarded by `didAutoOpenSectionRef`) rather than re-calling `expandAllSections` whenever `sectionKeys` change. AC is about fresh navigation / landing; AC5 requires that collapsing after landing stays possible. Filter changes still omit empty sections via `filteredRows` → `sections`; newly appearing sections after the one-shot stay collapsed until the operator expands them or uses **Expand all**.

⚠️ **Decision:** Call `expandAllSections()` instead of hand-building `new Set(sections.map(...))` so landing uses the same Expand All API as the chrome button (DRY with AST-893).

---

## Self-Assessment

**Scope:** Single-Component — one frontend page (`AdminScheduledActions.tsx`): one default-state change and one landing expand effect; shared expand policy hook already opted in.

**Conf:** high — Avail filter and Expand All policy already exist; this ticket only flips the Avail initial value and replaces first-section auto-open with `expandAllSections` behind the same one-shot ref.

**Risk:** low — change is client-side defaults on one admin screen; Available math, dispatch, and other pages are untouched. Wrong landing expand would at most reopen sections more aggressively than intended (mitigated by the one-shot ref).

## Rules check (ASTRAL_CODE_RULES)

- **§1.3 DRY:** Reuses existing `availGtZeroFilter` / `filteredRows` and `expandAllSections` from `useSectionExpandPolicy` — no forked expand policy.
- **§2.1 config:** No new config keys; Avail mode set is already `""` / `"gt0"` in the page (frontend filter UI, not a backend magic number).
- **§2.4 / §2.6:** N/A (no batch / state machine).
- **§3.3 imports:** No new imports required.
- **§3.5 naming:** Keep `availGtZeroFilter`, `didAutoOpenSectionRef`, `expandAllSections` names as they exist.
)
