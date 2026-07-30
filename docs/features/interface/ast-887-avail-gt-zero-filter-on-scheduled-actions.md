<!-- linear-archive: AST-887 archived 2026-07-29 -->

## Linear archive (AST-887)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-887/avail-0-filter-on-scheduled-actions-add-filter-flag-to-scheduled  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-885 — Add filter flag to scheduled_actions for Avail > 0  
**Blocked by / blocks / related:** parent: AST-885

### Description

## What this implements

Add an on-page filter control on Admin → Scheduled Actions that, when engaged, shows only rows whose Available count is greater than zero. When not engaged, Available does not constrain visibility. The filter intersects (AND) with existing Candidate, Task, Floor, AUTO, Debug, Freq, Min count, Batch size, and Run-count filters. Zero or empty Available rows are excluded when engaged (same cases the Avail column shows as an em dash). Empty section/group headers are omitted after filtering; section AUTO summaries reflect the filtered set. Default: filter not engaged.

## Acceptance criteria

1. On Admin → Scheduled Actions, a filter control is available that can be engaged to mean “Avail > 0.”
2. With that filter engaged and no other narrowing filters, every visible row shows a numeric Avail greater than zero (no em-dash Avail rows).
3. With that filter engaged together with any other existing filter(s), only rows that satisfy all engaged filters remain visible.
4. With that filter not engaged, rows with Avail zero or empty remain visible when they would otherwise match the other filters.
5. Engaging the filter removes empty section/group headers; clearing it restores sections that again have matching rows.
6. Page load / default view does not engage the Avail > 0 filter.

## Boundaries

* Does not change how Available is calculated, claimed, or dispatched.
* Does not change Avail column formatting.
* Does not add server-side query parameters or alter the dispatch-tasks list API payload.
* Does not change Run / Stop / AUTO / edit-modal / Manage Tasks behavior.
* Does not add Available min/max range filters — greater-than-zero flag only.

## Notes for planning

* Follow the existing client-side filter bar on Scheduled Actions (AST-751 pattern: AUTO/Debug-style controls, AND intersection, omit empty sections after filter).
* Primary surface is the Scheduled Actions admin page; no API payload change expected.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent. Engineers publish to origin sub/ftr refs — never Linear gitBranchName when it disagrees.

### Comments

#### radia — 2026-07-13T18:40:57.060Z
Review: [https://github.com/susansomerset/astral/blob/sub/AST-885/AST-887-avail-gt-zero-filter/docs/features/interface/ast-887-avail-gt-zero-filter-on-scheduled-actions.md](https://github.com/susansomerset/astral/blob/sub/AST-885/AST-887-avail-gt-zero-filter/docs/features/interface/ast-887-avail-gt-zero-filter-on-scheduled-actions.md)

**Diff:** `origin/dev...origin/sub/AST-885/AST-887-avail-gt-zero-filter` @ `cc9d6e801c2bc4cd8461028da7cff967ca2b7ad5`

**fix-now:** none

**What's solid:** Stage 1 exact (`availGtZeroFilter`, predicate after Debug / before Freq, Avail select). `(available_count ?? 0) > 0` matches `formatAvailableCount` em-dash (`null`/`0`). Client-side triage justified by plan Decision + AST-751/768. Betty covers default / engage / AND AUTO / clear + AST-785 race hardening.

**Advisory:** `DispatchTask.available_count` typed `number` while runtime already allows `null` — pre-existing; filter uses `?? 0`.

**Verdict:** Clean — `resolve-child` may proceed.

#### betty — 2026-07-13T18:38:45.707Z
[check-linear]
Cleared [qa-handoff]: AST-751 auto-open race — `expandFirstPhaseSection` waits for table or Expand; em-dash case clicks Expand only when present. Manifest smoke `AST-887|AST-751|AST-768` green (17).

**Publish:** `origin/sub/AST-885/AST-887-avail-gt-zero-filter` @ `21e461e` (`test(AST-887):` cherry-pick; one `merge-tests` kept)
**Bible:** `docs/test-bible/frontend/pages.md` shasum `bbd319ddb7e95a488a952236f82c3f2a390a31f9`
**Assignee:** Katherine for test-child — stay Tests Ready.

#### katherine — 2026-07-13T18:36:50.279Z
[qa-handoff]
@Betty White

AST-887 product cases green; smoke item 2 is a **test** problem, not product.

**Green**
```
cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx --testNamePattern="AST-887"
```
→ 4 passed.

**Red (manifest item 2)**
```
cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx --testNamePattern="AST-751|AST-768"
```
→ 2 failed | 11 passed:
1. `AST-751 … places Candidate, Avail, and Last Run as rightmost columns` — `expandFirstPhaseSection` waits for `Expand section`, but the sole section is already auto-opened (`Collapse section` + table present). Race/`didAutoOpenSectionRef` vs single-section fixture.
2. `AST-751 … renders em dash for zero or null available count` — after `selectAllCandidatesFilter()`, roster panel auto-opens; test still `getByRole("button", { name: "Expand section" })` inside the panel.

**Why test/manifest (not product):** Avail filter only adds `availGtZeroFilter` state + predicate + filter-bar select. No change to section auto-open, column order, or `formatAvailableCount`. AST-887 describe already tolerates auto-open; these two AST-751 cases need the same (wait for table / Collapse, or skip Expand when already open).

**Publish tip used:** `origin/sub/AST-885/AST-887-avail-gt-zero-filter` @ `1ade3eb` (Betty's merge-tests tip). No product commits from this pass.

#### betty — 2026-07-13T18:34:59.384Z
**QA test manifest — AST-887**

1. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx --testNamePattern="AST-887"`
   - **`AST-887 Avail > 0 filter`** (4 cases): default All still shows zero/null Avail rows; engage `> 0` hides 0/null + omits empty sections; ANDs with AUTO; clear restores sections.
2. Re-run smoke (same file): `--testNamePattern="AST-751|AST-768"` — filter bar + section intersection still green around the new Avail control.

**Publish:** `origin/sub/AST-885/AST-887-avail-gt-zero-filter` @ `1ade3eb` (`merge-tests(AST-887): origin/tests 6dd3586b5a64cb1e7a46604272fc13acd23389d7`)

**Bible:** `docs/test-bible/frontend/pages.md` shasum `95ee64e6c7c1b25d6057423710da5a251bbde72e`

— Betty

#### katherine — 2026-07-13T18:30:35.150Z
Plan: [https://github.com/susansomerset/astral/blob/sub/AST-885/AST-887-avail-gt-zero-filter/docs/features/interface/ast-887-avail-gt-zero-filter-on-scheduled-actions.md](https://github.com/susansomerset/astral/blob/sub/AST-885/AST-887-avail-gt-zero-filter/docs/features/interface/ast-887-avail-gt-zero-filter-on-scheduled-actions.md)

**Scope:** Single-Component — one React admin page (`AdminScheduledActions.tsx`); filter bar + `filteredRows` only.
**Conf:** high — copies the existing AUTO/Debug filter-hook / select / AND-intersection pattern; Avail semantics already defined by `formatAvailableCount`.
**Risk:** low — additive client-side filter; default All leaves current visibility unchanged; no API, dispatch, or Available math changes.

Publish tip: `origin/sub/AST-885/AST-887-avail-gt-zero-filter` @ `03c562d`.

---

# Avail > 0 filter on Scheduled Actions (Add filter flag to scheduled_actions for Avail > 0)

**Linear:** [AST-887](https://linear.app/astralcareermatch/issue/AST-887)  
**Parent:** [AST-885](https://linear.app/astralcareermatch/issue/AST-885)  
**Publish ref:** `sub/AST-885/AST-887-avail-gt-zero-filter`

Add one on-page filter to Admin → Scheduled Actions that, when engaged, keeps only rows whose Available count is greater than zero. When not engaged, Available does not constrain visibility. The filter ANDs with every existing filter (Candidate, Section/Group, Task, Floor, AUTO, Debug, Freq, Min count, Batch size, Run counts). Zero or empty Available rows are excluded when engaged — the same cases `formatAvailableCount` already renders as an em dash. Empty section headers drop out because sections already build from `filteredRows`; section AUTO summaries already use that filtered set. Default: not engaged.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Add Avail > 0 filter state, intersection predicate, and filter-bar select | ui |

**Out of scope (this ticket):** `src/ui/api/api_admin.py` and any dispatch-tasks list payload change; Available calculation / claim / dispatch; Avail column formatting (`formatAvailableCount`); Run / Stop / AUTO / edit-modal / Manage Tasks; Available min/max range filters; `tests/` and `docs/test-bible/**` (Betty owns those after Code Complete).

---

## Stage 1: Avail > 0 client-side filter

**Done when:** The Scheduled Actions filter bar has an Avail control defaulting to All (not engaged). Engaging it to `> 0` hides every row whose `available_count` is `null` or `0` (em-dash Avail). Other filters still AND with it. Clearing back to All restores zero/empty Avail rows that match the other filters. Empty sections disappear while engaged and reappear when cleared if they again have matching rows. Section AUTO summaries continue to reflect the filtered row set with no extra code.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, after the `debugFilter` state (~line 311), add:

   ```ts
   const [availGtZeroFilter, setAvailGtZeroFilter] = useState("") // "" | "gt0"
   ```

2. In the `filteredRows` `useMemo` (~lines 415–446), after the Debug filter predicates and before the Freq predicate, add:

   ```ts
   if (availGtZeroFilter === "gt0") {
     filtered = filtered.filter(r => (r.available_count ?? 0) > 0)
   }
   ```

3. Add `availGtZeroFilter` to that `useMemo` dependency array (same list that already includes `autoFilter`, `debugFilter`, etc.).

4. In the `.admin-filters` block, immediately after the Debug `<label>` / `<select>` (~lines 704–711) and before the Freq label, insert:

   ```tsx
   <label>
     Avail
     <select value={availGtZeroFilter} onChange={e => setAvailGtZeroFilter(e.target.value)}>
       <option value="">All</option>
       <option value="gt0">&gt; 0</option>
     </select>
   </label>
   ```

5. Do not edit `formatAvailableCount`, `sections`, `sortRowsWithinSection`, table columns, modals, polling, Run/Stop/AUTO/Debug toggles, or any API call. Sections already omit empty groups via `for (const row of filteredRows)`; AUTO summary already uses filtered rows — both pick up the new predicate automatically.

⚠️ **Decision:** Binary select (`""` / `"gt0"`), not a ternary All/ON/OFF like AUTO/Debug. Ticket boundaries allow only a greater-than-zero flag — no “Avail = 0 only” mode and no min/max range. Label `Avail` with option `> 0` matches the column name and AC wording.

⚠️ **Decision:** Predicate uses `(r.available_count ?? 0) > 0` so `null` and `0` are both excluded when engaged — identical to the em-dash cases in `formatAvailableCount` (lines 90–93). Do not call `formatAvailableCount` inside the filter; compare the numeric field only.

⚠️ **Decision:** Client-side only on the existing `GET /api/admin/dispatch_tasks` payload — same AST-751 / AST-768 pattern. Ticket Boundaries forbid new query params and payload changes. Admin triage filters on an already-fetched list are an established exception to the general “domain filtering in the API” rule.

---

## Execution contract

- Execute steps in order within the stage; do not skip, reorder, combine, or expand.
- Do not add files, modules, configs, or dependencies not listed above.
- On ambiguity, drift, or literal failure: stop, comment on the **parent** Linear issue (AST-885) with the Stage-blocked template, and wait.

## Self-Assessment

**Scope:** Single-Component — one React admin page file; filter bar + `filteredRows` only.

**Conf:** high — copies the existing AUTO/Debug filter-hook / select / AND-intersection pattern; Avail semantics already defined by `formatAvailableCount`.

**Risk:** low — additive client-side filter; default All leaves current visibility unchanged; no API, dispatch, or Available math changes.

## Rules check (ASTRAL_CODE_RULES)

- §1.3 DRY: reuse existing filter-bar label/select and `filteredRows` intersection; no new helper unless duplication appears (it will not for one predicate).
- §2.1 config: no new config keys — filter is UI triage state, not a behavior-driving system constant.
- §2.4 / §2.6: untouched (no batch or state-machine changes).
- §3.3 imports: no new imports.
- §3.5 naming: `availGtZeroFilter` / `"gt0"` match the ticket’s Avail > 0 flag semantics.
- §3.2 “UI logic in API”: deferred by ticket Boundaries + AST-751 precedent (documented Decision above).

---

## Review (build)

**Built:** `origin/sub/AST-885/AST-887-avail-gt-zero-filter` @ `14c408e7b887c3e31864a3f4ed33ee5087089dd4`

Stage 1: Avail filter control (`All` / `> 0`) on Scheduled Actions; `filteredRows` excludes `available_count` null/0 when engaged; sections and AUTO summaries inherit via existing `filteredRows` bucketing. Tests deferred to Betty.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-885/AST-887-avail-gt-zero-filter` @ product `14c408e` + Betty `6dd3586` / race fix `21e461e`

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stage 1 exact: `availGtZeroFilter` state (`""` \| `"gt0"`), `filteredRows` predicate after Debug / before Freq, dep array, Avail select between Debug and Freq. No API / `formatAvailableCount` / sections / Run-Stop-AUTO edits. |
| AC semantics | `(r.available_count ?? 0) > 0` matches `formatAvailableCount` em-dash cases (`null` / `0`). Default All; AND with existing filters; empty sections drop via existing `filteredRows` bucketing. |
| Self-Assessment | Scope Single-Component matches footprint (one page + Betty tests/bible). Conf high / Risk low still accurate. |
| Rules | §1.3 / §3.5 naming as planned. Client-side triage filter justified by plan Decision + AST-751/768 precedent (§3.2 UI-in-API exception). No new imports; §5f/§5g N/A (frontend only). |
| Tests | Betty: default All, engage hides 0/null + empty sections, AND with AUTO, clear restores; `expandFirstPhaseSection` / AST-751 race hardening for AST-785 auto-open. |

### Issues

None (**fix-now**).

### Recommended actions

| Severity | Item |
| --- | --- |
| **Advisory** | `DispatchTask.available_count` is typed `number` while runtime/`formatAvailableCount` already treat `null` — pre-existing; filter correctly uses `?? 0`. Tighten the type only if a later ticket touches the interface. |

**Verdict:** Clean — `resolve-child` may proceed.

---

## Resolution

**Date:** 2026-07-13  
**Review ref:** `origin/sub/AST-885/AST-887-avail-gt-zero-filter` @ Radia `docs(AST-887): Radia review — clean` (`cc9d6e8`)

No **fix-now** items. Product unchanged from build @ `14c408e` + Betty `merge-tests` / race fix. Advisory (`DispatchTask.available_count` typed `number` while runtime allows `null`) accepted — pre-existing; out of scope for this ticket.

**§9a dry-run:** publish tip merges cleanly into `origin/dev` and `origin/ftr/AST-885-avail-gt-zero-filter` (merge-tree clean @ `866d46840cde55cf36e7a5c1030d4f3c8412938d`).
