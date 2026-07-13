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
