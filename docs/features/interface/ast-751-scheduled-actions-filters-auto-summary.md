# Scheduled Actions filters, AUTO summary, and All-candidate layout (Scheduled Actions Screen Edits)

**Linear:** [AST-751](https://linear.app/astralcareermatch/issue/AST-751/scheduled-actions-filters-auto-summary-and-all-candidate-layout-scheduled)  
**Parent:** [AST-735](https://linear.app/astralcareermatch/issue/AST-735/scheduled-actions-screen-edits)  
**Publish ref:** `sub/AST-735/AST-751-scheduled-actions-filters-auto-summary`

Refresh the Scheduled Actions admin screen: per-group AUTO-on summaries in collapsible headers; expanded on-page filters (Candidate, Floor range, AUTO, Debug, Freq, Min count, Batch size, Run counts); table layout with Candidate / Available / Last run as the rightmost operational column group (Available shows **—** when zero); **Candidate → All** mode keeps task grouping and sorts rows within each task by available count descending. Client-side filtering only — `GET /api/admin/dispatch_tasks` already returns all candidates' rows with `available_count` per row.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Filters, section AUTO summary, column reorder, All-candidate sort, Available zero display | ui |

**Out of scope (this ticket):** `src/ui/api/api_admin.py` (no API change — list payload sufficient); Manage Tasks edit modal / grouping source (`AST-738`/`AST-739`); Apply Scheduled Actions bulk copy; Candidate Actions matrix; scheduler/dispatch backend; `tests/` (Betty manifest below).

**QA manifest (Betty — not engineer commits):** Extend `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` for: section header `N / M AUTO` after filters; each new filter narrows rows; combined filters intersect; column order (Candidate / Avail / Last run rightmost); Available `0` → `—`; All-candidate default sort by available count desc within task; AUTO-on + All shows cross-candidate AUTO rows only; existing run/stop/modal/polling tests still pass.

## Prerequisite (build gate — not a commit stage)

**Done when:** Epic worktree includes AST-734/739 DB grouping on `task_keys` (`task_group_order`, `task_group_name`, `task_seq`, `task_name` — no `phase`/`seq`).

1. On epic worktree: `git fetch origin && git merge origin/ftr/AST-735-scheduled-actions-screen-edits`.
2. Open `AdminScheduledActions.tsx` — confirm `allTaskKeys` type uses `task_group_*` fields and sections bucket by DB grouping (not `phase`).
3. If still on config `phase`/`seq`, **stop** — comment on AST-751 `@susan`: AST-739 not on ftr yet.

---

## Stage 1: Expanded on-page filters

**Done when:** Filter bar includes Candidate (existing), Floor min/max, AUTO, Debug, Freq, Min count, Batch size, and Run counts; each filter narrows visible rows; combined filters intersect (AND); Task filter (existing) still works; section list omits empty groups after filtering.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, add filter state hooks after `taskKeyFilter` (~line 257):

   ```ts
   const [floorMin, setFloorMin] = useState("")
   const [floorMax, setFloorMax] = useState("")
   const [autoFilter, setAutoFilter] = useState("")       // "" | "on" | "off"
   const [debugFilter, setDebugFilter] = useState("")     // "" | "on" | "off"
   const [freqFilter, setFreqFilter] = useState("")
   const [minCountFilter, setMinCountFilter] = useState("")
   const [batchSizeFilter, setBatchSizeFilter] = useState("")
   const [maxRunsFilter, setMaxRunsFilter] = useState("")
   ```

2. Add a `filterOptionValues` `useMemo` derived from full `data` (not filtered rows) so option lists stay stable when other filters narrow the table:

   ```ts
   const filterOptionValues = useMemo(() => ({
     freq: [...new Set(data.map(r => r.freq_hrs ?? 0))].sort((a, b) => a - b),
     minCount: [...new Set(data.map(r => r.min_count))].sort((a, b) => a - b),
     batchSize: [...new Set(data.map(r => r.batch_size).filter(v => v != null))].sort((a, b) => (a as number) - (b as number)),
     maxRuns: [...new Set(data.map(r => r.max_runs ?? 1))].sort((a, b) => a - b),
   }), [data])
   ```

3. Replace the `filteredRows` `useMemo` (~lines 321–326) with intersection logic (keep existing `candidateFilter` and `taskKeyFilter` first, then apply new filters in order):

   ```ts
   const filteredRows = useMemo(() => {
     let filtered = data
     if (candidateFilter) filtered = filtered.filter(r => r.candidate_id === candidateFilter)
     if (taskKeyFilter) filtered = filtered.filter(r => r.task_key === taskKeyFilter)
     if (autoFilter === "on") filtered = filtered.filter(r => !!r.auto_mode)
     if (autoFilter === "off") filtered = filtered.filter(r => !r.auto_mode)
     if (debugFilter === "on") filtered = filtered.filter(r => !!r.debug)
     if (debugFilter === "off") filtered = filtered.filter(r => !r.debug)
     if (freqFilter !== "") filtered = filtered.filter(r => (r.freq_hrs ?? 0) === Number(freqFilter))
     if (minCountFilter !== "") filtered = filtered.filter(r => r.min_count === Number(minCountFilter))
     if (batchSizeFilter !== "") filtered = filtered.filter(r => r.batch_size === Number(batchSizeFilter))
     if (maxRunsFilter !== "") filtered = filtered.filter(r => (r.max_runs ?? 1) === Number(maxRunsFilter))
     if (floorMin !== "" || floorMax !== "") {
       const lo = floorMin === "" ? -Infinity : parseFloat(floorMin)
       const hi = floorMax === "" ? Infinity : parseFloat(floorMax)
       filtered = filtered.filter(r => {
         const scored = r.is_scored ?? !!allTaskKeys[r.task_key]?.is_scored
         if (!scored) return false
         const floor = r.score_floor ?? 1
         return floor >= lo && floor <= hi
       })
     }
     return filtered
   }, [data, candidateFilter, taskKeyFilter, autoFilter, debugFilter, freqFilter, minCountFilter, batchSizeFilter, maxRunsFilter, floorMin, floorMax, allTaskKeys])
   ```

4. In the `.admin-filters` block (~lines 513–526), keep `AdminCandidateFilterControl` and Task select; append new filter controls (reuse existing `.admin-filters` label/select pattern from Performance Monitor):

   ```tsx
   <label>
     Floor min
     <select value={floorMin} onChange={e => setFloorMin(e.target.value)}>
       <option value="">All</option>
       {scoreFloorOptions.map(v => <option key={v} value={v}>{v}</option>)}
     </select>
   </label>
   <label>
     Floor max
     <select value={floorMax} onChange={e => setFloorMax(e.target.value)}>
       <option value="">All</option>
       {scoreFloorOptions.map(v => <option key={v} value={v}>{v}</option>)}
     </select>
   </label>
   <label>
     AUTO
     <select value={autoFilter} onChange={e => setAutoFilter(e.target.value)}>
       <option value="">All</option>
       <option value="on">ON</option>
       <option value="off">OFF</option>
     </select>
   </label>
   <label>
     Debug
     <select value={debugFilter} onChange={e => setDebugFilter(e.target.value)}>
       <option value="">All</option>
       <option value="on">ON</option>
       <option value="off">OFF</option>
     </select>
   </label>
   <label>
     Freq
     <select value={freqFilter} onChange={e => setFreqFilter(e.target.value)}>
       <option value="">All</option>
       {filterOptionValues.freq.map(v => <option key={v} value={String(v)}>{v}</option>)}
     </select>
   </label>
   <label>
     Min count
     <select value={minCountFilter} onChange={e => setMinCountFilter(e.target.value)}>
       <option value="">All</option>
       {filterOptionValues.minCount.map(v => <option key={v} value={String(v)}>{v}</option>)}
     </select>
   </label>
   <label>
     Batch size
     <select value={batchSizeFilter} onChange={e => setBatchSizeFilter(e.target.value)}>
       <option value="">All</option>
       {filterOptionValues.batchSize.map(v => <option key={v} value={String(v)}>{v}</option>)}
     </select>
   </label>
   <label>
     Run counts
     <select value={maxRunsFilter} onChange={e => setMaxRunsFilter(e.target.value)}>
       <option value="">All</option>
       {filterOptionValues.maxRuns.map(v => (
         <option key={v} value={String(v)}>{v === 0 ? "∞ (0)" : String(v)}</option>
       ))}
     </select>
   </label>
   ```

5. Do not change `sections` bucketing, sort, table, modals, or polling in this stage.

⚠️ **Decision:** All new filters are client-side on the existing full list payload — no query params or API changes. Floor range excludes non-scored rows when either bound is set (no `score_floor` to compare).

---

## Stage 2: Per-group AUTO summary in section headers

**Done when:** Each collapsible section header shows `{groupName} ({autoOn} / {total} AUTO)` where counts reflect **filtered** rows in that group (post Stage 1 filters); zero expanded sections still allowed.

1. In the `sections` `useMemo` (~lines 328–344), extend each mapped section object:

   ```ts
   .map(([sectionKey, rows]) => {
     const autoOnCount = rows.filter(r => !!r.auto_mode).length
     return {
       sectionKey,
       groupName: allTaskKeys[rows[0]?.task_key]?.task_group_name || "(unassigned)",
       autoOnCount,
       rows: sortRowsWithinSection(rows),
     }
   })
   ```

2. Update `CollapsiblePanel` `label` (~line 535) from `{sec.groupName} ({sec.rows.length})` to:

   ```tsx
   label={<>{sec.groupName} ({sec.autoOnCount} / {sec.rows.length} AUTO)</>}
   ```

3. Do not change table columns or sort logic in this stage.

⚠️ **Decision:** Summary uses filtered row counts (not raw `data`) so Susan sees AUTO coverage for the triage view she is actively filtering — matches parent AC #2 "under active filters".

---

## Stage 3: Table column reorder and Available zero display

**Done when:** Column order is Task → Entity → State → Floor → AUTO → Run → Dbg → Freq → Min → Batch → Runs → **Candidate → Avail → Last Run**; Available shows **—** when count is `0` or `null`; first three frozen data columns are Task, Entity, State (AST-647 parity with new order).

1. At module top (~lines 45–49), replace `DATA_COL_KEYS` with:

   ```ts
   const DATA_COL_KEYS = [
     "task_key", "entity_type", "trigger_state", "score_floor",
     "auto_mode", "run", "debug", "freq_hrs", "min_count",
     "batch_size", "max_runs", "candidate_id", "available_count", "last_run_at",
   ] as const
   ```

   Keep `FROZEN_DATA_COLUMNS = 3` — frozen indices 0–2 are now Task, Entity, State.

2. Add a small formatter above `ScheduledPhaseTable`:

   ```ts
   function formatAvailableCount(count: number | null): string {
     if (count == null || count === 0) return "—"
     return count.toLocaleString()
   }
   ```

3. In `ScheduledPhaseTable`, reorder `<thead>` and matching `<tbody>` cells to match the new column sequence. Move Candidate, Available, and Last Run cells to **after** Runs (max_runs) and **before** closing `</tr>`. Remove Candidate from the first column position.

4. Update frozen class/style indices in header and body cells: indices `0`, `1`, `2` = Task, Entity, State; all other columns unfrozen.

5. Replace Available cell content (~lines 183–187) with:

   ```tsx
   <ListTableTruncatedCell text={formatAvailableCount(row.available_count)} maxChars={truncateChars} />
   ```

6. Update `toggleSort` click handlers on column headers to use the new header order; ensure `sortCol` string keys still match `DispatchTask` fields (`candidate_id`, `available_count`, `last_run_at`, etc.).

7. Do not change default sort behavior yet (Stage 4).

⚠️ **Decision:** Candidate moves to the right operational group per parent AC #4; frozen-left trio becomes Task/Entity/State so identity columns stay visible while scrolling. If AST-743 (score floor 0.00) lands on the same screen, reuse `formatAvailableCount` only — do not change Floor column logic here.

---

## Stage 4: All-candidate default sort by available count

**Done when:** With **Candidate → All** (`candidateFilter === ""`) and default sort (`sortCol === "_default"`), rows within each section sort by `task_seq`, then `task_key`, then **`available_count` descending**; single-candidate view keeps existing task_seq sort; explicit column-header sort still overrides default comparator.

1. Pass `candidateFilter` from `ScheduledActions` into `sortRowsWithinSection` (add parameter or close over `candidateFilter` in the `useCallback` deps).

2. In `sortRowsWithinSection`, update the `sortCol === "_default"` branch (~lines 303–309):

   ```ts
   if (sortCol === "_default") {
     const as_ = allTaskKeys[a.task_key]?.task_seq ?? 999
     const bs_ = allTaskKeys[b.task_key]?.task_seq ?? 999
     if (as_ !== bs_) return sortDir === "asc" ? as_ - bs_ : bs_ - as_
     const tk = a.task_key.localeCompare(b.task_key)
     if (tk !== 0) return tk
     if (!candidateFilter) {
       const av = a.available_count ?? 0
       const bv = b.available_count ?? 0
       if (av !== bv) return bv - av  // descending by available — fixed, not sortDir
     }
     return a.id - b.id
   }
   ```

3. Do not change API calls, modals, run/stop, Stop All, Add Task, or thread polling.

⚠️ **Decision:** Available-desc sort applies only in All-candidate default view — when Susan picks one candidate, row order stays catalog task_seq (operational habit from AST-568/739). Column-header sort remains available for manual overrides.

---

## Self-Assessment

**Scope:** `Single-Component` — changes are confined to `AdminScheduledActions.tsx` (filter bar, section labels, table column order, client sort); no API, config, or scheduler layers.

**Conf:** `high` — reuses existing `admin-filters`, `CollapsiblePanel`, `filteredRows`/`sections` memos, and AST-634/739 patterns; AC is explicit and the list API already serves all candidates.

**Risk:** `Medium` — column reorder touches frozen-column indices and Vitest table assertions; wrong sort or filter intersection would mislead operational triage but would not affect dispatch execution.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Filter logic stays in one `filteredRows` memo; `formatAvailableCount` is a single helper — no duplicate filter passes. |
| §2.1 config | No new config keys; filter option sets derived from live row data. |
| §2.4 batch | Not touched — UI read-only on dispatch rows. |
| §2.6 state machine | Not touched. |
| §3.3 imports | No new cross-layer imports; page stays in `src/ui/frontend`. |
| §3.5 naming | Follow existing `admin-filters`, `CollapsiblePanel`, `sortRowsWithinSection` naming. |

No conflicts requiring plan revision.

---

## Review (build-child)

**Built:** `sub/AST-735/AST-751-scheduled-actions-filters-auto-summary` — expanded client-side filters, per-group AUTO summary headers, table column reorder (Candidate/Avail/Last Run rightmost), Available zero → —, All-candidate default sort by available count desc within task.

**Tip:** `bfc26258` (`origin/sub/AST-735/AST-751-scheduled-actions-filters-auto-summary`)
