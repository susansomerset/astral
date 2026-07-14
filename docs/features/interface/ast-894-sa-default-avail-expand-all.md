# Default Avail > 0 and expand all visible sections on load (Default the scheduled_actions screen to show avail >0 and expand all)

**Linear:** [AST-894](https://linear.app/astralcareermatch/issue/AST-894/default-avail-0-and-expand-all-visible-sections-on-load-default-the)  
**Parent:** [AST-888](https://linear.app/astralcareermatch/issue/AST-888/default-the-scheduled-actions-screen-to-show-avail-0-and-expand-all)  
**Publish ref:** `sub/AST-888/AST-894-sa-default-avail-expand-all`

On Admin → Scheduled Actions landing, default the existing Avail filter to `> 0` and, once sections first appear under the current filters, expand every visible section via the shared Expand All policy already on the page — so every group with available work is open at a glance instead of first-section-only auto-open.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Default `availGtZeroFilter` to `"gt0"`; replace first-section-only auto-open with one-shot `expandAllSections()` | ui |

**Out of scope (this ticket):** Available calculation / claim / dispatch / Avail column formatting; new Avail modes or API query params; Run / Stop / AUTO / edit-modal / Manage Tasks; other sectioned screens’ default expansion; changes to `useSectionExpandPolicy` / `SectionExpandChrome` APIs; continuous re-expand on every filter change after landing; `tests/` and `docs/test-bible/**` (Betty at Code Complete).

**QA note (Betty — not engineer commits):** Existing `test_AdminScheduledActions.test.tsx` asserts Avail defaults to All (`AST-887`) and relies on AST-785 first-section auto-open (`expandFirstPhaseSection`). Update those expectations for default `gt0` + all matching sections expanded on load. Manifest should also cover operator collapse after landing and Avail → All restoring zero/empty Avail rows without breaking empty-section omission.

---

## Stage 1: Landing defaults on Scheduled Actions

**Done when:** Fresh load of Admin → Scheduled Actions shows Avail engaged as `> 0` without touching the control; when more than one section has matching rows under that default, every such section is expanded at once; operator can collapse a section afterward without the page forcing it open again; switching Avail back to All restores zero/empty Avail rows that match other filters. No other page or API behavior changes.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, change the Avail filter initial state from empty-string (All) to `"gt0"`:

   ```ts
   const [availGtZeroFilter, setAvailGtZeroFilter] = useState("gt0") // "" | "gt0"
   ```

   Keep the select options exactly as today (`All` = `""`, `> 0` = `"gt0"`). Do not change the `filteredRows` predicate (`availGtZeroFilter === "gt0"` → `(r.available_count ?? 0) > 0`), AND intersection with other filters, empty-section omission, or any other filter initial values.

2. Replace the first-section-only auto-open effect (the `useEffect` that currently does `setExpandedKeys(new Set([sections[0].sectionKey]))` behind `didAutoOpenSectionRef`) with a one-shot expand-all of every currently visible section:

   ```ts
   useEffect(() => {
     if (didAutoOpenSectionRef.current || sections.length === 0) return
     didAutoOpenSectionRef.current = true
     expandAllSections()
   }, [sections, expandAllSections])
   ```

   Keep `didAutoOpenSectionRef` as the once-gate (do not reset it on filter/candidate changes). Keep the existing stale-key prune effect that drops expanded keys no longer in `sectionKeys` unchanged. Do not change `useSectionExpandPolicy({ expandAll: true, sectionKeys })` or `SectionExpandChrome` wiring.

3. Do not edit `useSectionExpandPolicy.ts`, `SectionExpandChrome.tsx`, other pages, API modules, or config.

⚠️ **Decision:** Default only the Avail control initial state to `"gt0"` — do not remove All / `> 0` options or change the AND intersection with other filters. Operator can still clear back to All (AC4).

⚠️ **Decision:** Landing expand runs **once** when `sections` first becomes non-empty (same once-gate as today). Calling `expandAllSections()` (shared hook: `setExpandedKeys(new Set(sectionKeys))`) replaces first-section-only open so every currently visible section opens together (AC2, AC6). The once-gate ensures operator collapses after landing are not overwritten when `sections` recalculates from poll/filter (AC5). Do **not** re-run expand-all on every filter change; newly appearing sections after the one-shot stay collapsed until the operator expands them or uses **Expand all**.

⚠️ **Decision:** Touch only `AdminScheduledActions.tsx`. Shared Expand All policy + chrome already exist from AST-893; do not fork page-local multi-expand logic.

---

## Execution contract

- Execute steps in order within the stage; do not skip, reorder, combine, or expand.
- Do not add files, modules, configs, or dependencies not listed above.
- On ambiguity, drift, or literal failure: stop, comment on the **parent** Linear issue (AST-888) with the Stage-blocked template, and wait.

## Self-Assessment

**Scope:** Single-Component — one React admin page (`AdminScheduledActions.tsx`); Avail default + one landing expand effect.

**Conf:** high — Avail filter and Expand All policy already shipped; this ticket only flips the Avail initial value and swaps first-section open for `expandAllSections()` behind the same once-gate.

**Risk:** low — additive landing UX only; operator controls remain; no API, dispatch, or Available math changes. Wrong expand timing would annoy operators (re-open after collapse) but the once-gate prevents that if followed literally.

## Rules check (ASTRAL_CODE_RULES)

- §1.3 DRY: reuse `expandAllSections` from `useSectionExpandPolicy`; no duplicate Set/`sectionKeys` expand helper on the page.
- §2.1 config: no new config keys — landing defaults are page UI state, same as other filter defaults.
- §2.4 / §2.6: untouched (no batch or state-machine changes).
- §3.3 imports: no new imports (`expandAllSections` already destructured).
- §3.5 naming: keep `availGtZeroFilter` / `"gt0"` and `didAutoOpenSectionRef`.
- §3.2 “UI logic in API”: N/A — no API work; client-side filter default only (AST-887 precedent).

---

## Review (build)

**Built:** `origin/sub/AST-888/AST-894-sa-default-avail-expand-all` @ `ee974d26bb462ce06316faa3d27d930bd8a3f7b3`

Stage 1: Avail initial state `"gt0"`; landing auto-open uses one-shot `expandAllSections()` behind `didAutoOpenSectionRef`. Tests deferred to Betty.
