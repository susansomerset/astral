<!-- linear-archive: AST-894 archived 2026-07-29 -->

## Linear archive (AST-894)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-894/default-avail-0-and-expand-all-visible-sections-on-load-default-the  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-888 — Default the scheduled_actions screen to show avail >0 and expand all  
**Blocked by / blocks / related:** parent: AST-888

### Description

## What this implements

On Admin → Scheduled Actions landing, default the existing Avail filter to “> 0” and expand every section that still has rows under the current filters, using the shared Expand All policy from AST-886 — so every section with available entities is visible at once instead of requiring the operator to engage the filter and open sections one by one.

## Acceptance criteria

1. Fresh navigation to Admin → Scheduled Actions engages the Avail filter as “> 0” without the operator touching the control.
2. With that default and matching rows in more than one section, every section that has at least one matching row is expanded at the same time (no actionable section left collapsed solely because another is open).
3. Under that default view with no other narrowing filters, every visible row shows a numeric Avail greater than zero (no em-dash Avail rows).
4. Switching Avail back to All restores zero/empty Avail rows that match the other filters, and empty-section omission continues to follow the filtered set.
5. After landing, the operator can collapse a section without that action being blocked by the default expand behavior.
6. The prior first-section-only auto-open no longer leaves other Avail > 0 sections collapsed on the default landing view when multiple sections have matching rows.

## Boundaries

* Does not change Available calculation, claim, dispatch, or Avail column formatting.
* Does not add new Avail modes or server-side query params.
* Does not change Run / Stop / AUTO / edit-modal / Manage Tasks.
* Does not change other sectioned screens’ default expansion.
* Does not re-implement Expand All — use the shared AST-886 section expand policy already on Scheduled Actions.

## Notes for planning

* Avail > 0 filter control already exists (AST-885 / AST-887); change default only.
* Shared `useSectionExpandPolicy({ expandAll: true })` already on Scheduled Actions (AST-886 / AST-893); replace first-section-only auto-open with expand-all-visible on landing.
* Frontend-only; no API change.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent. Engineers publish to origin sub/ftr refs — never Linear gitBranchName when it disagrees.

### Comments

#### radia — 2026-07-14T01:38:52.609Z
**Diff:** `origin/dev...origin/sub/AST-888/AST-894-sa-default-avail-expand-all` @ `348e9cb`

### What's solid
- Stage 1 matches plan: `availGtZeroFilter` initial `"gt0"`; once-gate + `expandAllSections()`; prune / Expand All policy / Avail options / `filteredRows` predicate untouched.
- Betty revised AST-887 + AST-894 landing/collapse/Avail→All coverage; no product scope creep.
- §1.3 DRY / §2.1 / §3.3 / UI-only OK. Self-Assessment Scope matches footprint.

### Issues
None.

### Recommended actions
| Action | Item |
|--------|------|
| none (ship) | 0 fix-now · 0 discuss · 0 advisory |

**Doc:** `docs/features/interface/ast-894-sa-default-avail-expand-all.md` — `docs(AST-894): Radia review — clean` → `origin/sub/AST-888/AST-894-sa-default-avail-expand-all` @ `348e9cb`

#### betty — 2026-07-14T01:34:44.961Z
## QA test manifest — AST-894

**Publish:** `origin/sub/AST-888/AST-894-sa-default-avail-expand-all` @ `e097f4d` (`merge-tests(AST-894): origin/tests 5f3d93afa8aa4dae53635e73dede28e20398236b`)

**Bible shasum on publish ref:**
- `docs/test-bible/frontend/pages.md` — `ead665f4dc0af4cfa0126c5c380b8ae81cf0d365`

1. **Default Avail `gt0` omits zero/null Avail** (§6c) — `test_AdminScheduledActions.test.tsx` — `AST-887 Avail > 0 filter` (revised) + `AST-894` Avail All restores
2. **Landing expand-all opens every matching section** under default filters (§6c) — `AST-894 default Avail > 0 and expand-all on landing`
3. **Once-gate:** operator collapse after landing stays collapsed — `AST-894`
4. **Regression:** Expand All chrome + filter suites — `--testNamePattern="AST-894|AST-887|AST-893|AST-751|AST-768|AST-785"` (or full file)

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-894|AST-887|AST-893|AST-751|AST-768|AST-785"
```

**Broken / obsolete revised this pass:** AST-887 default-All case; suites needing zero/null Avail rows now call `selectAvailAll()`.

— Betty

#### katherine — 2026-07-14T01:24:22.792Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-888/AST-894-sa-default-avail-expand-all/docs/features/interface/ast-894-sa-default-avail-expand-all.md

`origin/sub/AST-888/AST-894-sa-default-avail-expand-all` @ `f4979ff`

**Scope:** Single-Component — one React page (`AdminScheduledActions.tsx`): Avail initial state → `gt0`, first-section auto-open → one-shot `expandAllSections()`.

**Conf:** high — Avail filter and Expand All policy already shipped; only landing defaults change.

**Risk:** low — client landing UX only; Available math / dispatch / other pages untouched. Once-gate keeps post-landing collapses from being overwritten.

#### katherine — 2026-07-14T01:24:09.436Z
Plan: [`docs/features/interface/ast-894-sa-default-avail-expand-all.md`](https://github.com/susansomerset/astral/blob/sub/AST-888/AST-894-sa-default-avail-expand-all/docs/features/interface/ast-894-sa-default-avail-expand-all.md)
`origin/sub/AST-888/AST-894-sa-default-avail-expand-all` @ `83e9ea16b4361f3d1d54d063b446b4df1e83a988`

**Scope:** Single-Component — one page (`AdminScheduledActions.tsx`): default Avail to `gt0` and one-shot landing `expandAllSections` instead of first-section-only auto-open.
**Conf:** high — Avail filter and Expand All policy already on the page; this only flips the initial filter value and the landing expand effect.
**Risk:** low — client-side defaults on Scheduled Actions only; Available math, dispatch, and other screens untouched.

---

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

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-888/AST-894-sa-default-avail-expand-all` @ `e097f4d`

### What’s solid

- Stage 1 matches plan literally: `availGtZeroFilter` initial `"gt0"`; once-gate `didAutoOpenSectionRef` + `expandAllSections()`; prune effect / `useSectionExpandPolicy` / select options / `filteredRows` predicate untouched.
- Betty side correctly revised AST-887 defaults + AST-894 landing/collapse/Avail→All coverage; no product scope creep.
- §1.3 DRY (reuses hook), §3.3 / §2.1 / UI-only — OK. Self-Assessment Scope matches footprint.

### Issues

None.

### Recommended actions

| Action | Item |
|--------|------|
| none (ship) | 0 fix-now · 0 discuss · 0 advisory |

---

## Resolution

**Date:** 2026-07-14  
**Radia review:** `docs(AST-894): Radia review — clean` @ `348e9cb` — 0 fix-now · 0 discuss · 0 advisory.

No product or plan-doc code changes required. §9a dry-run clean vs `origin/dev` and vs `origin/ftr/AST-888-sa-default-avail-expand-all`.
