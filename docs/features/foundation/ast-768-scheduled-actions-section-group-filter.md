# AST-768 — Scheduled Actions section/group filter (Organization of tasks and dispatch task keys)

**Linear:** [AST-768 — Scheduled Actions section/group filter](https://linear.app/astralcareermatch/issue/AST-768/scheduled-actions-sectiongroup-filter-organization-of-tasks-and-dispatch)  
**Parent:** [AST-572 — Organization of tasks and dispatch task keys](https://linear.app/astralcareermatch/issue/AST-572/organization-of-tasks-and-dispatch-task-keys)  
**Publish ref:** `origin/sub/AST-572/AST-768-scheduled-actions-section-group-filter`

Add a **Section/Group** filter control on the Scheduled Actions admin screen so operators can narrow dispatch rows to one task group (`task_group_name`) using the same DB-backed metadata Manage Tasks uses (**AST-734/739**). The filter intersects (AND) with existing Candidate, Task, and operational filters from **AST-751**. Client-side only — `GET /api/admin/dispatch_tasks/task_keys` already returns `task_group_name` and `task_group_order` on every schedulable key.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Section/Group filter state, options memo, `filteredRows` intersection, filter-bar control | ui |

**Out of scope (this ticket):** `src/ui/api/api_admin.py` (group list derivable from existing `task_keys` payload); consult→grade cutover (**AST-736**); retry row behavior (**AST-741/745**); scheduler/dispatch backend; `tests/` (Betty manifest below).

**QA manifest (Betty — not engineer commits):** Extend `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` with a describe block `AST-768 section/group filter` covering: filter control renders with **All** plus distinct group names from `taskKeysConfig` mocks; selecting a group shows only rows whose `task_key` maps to that group's `task_group_name`; combined Section/Group + Task filters intersect (empty when Task is outside group); combined Section/Group + AUTO filter intersect; with **Candidate → All**, section filter narrows visible collapsible sections and default sort within a section still follows `task_seq` then `available_count` desc; section header `{autoOn} / {total} AUTO` counts reflect post-filter rows in that group.

## Prerequisite (build gate — not a commit stage)

**Done when:** Epic worktree includes **AST-751** filter bar and DB grouping on `task_keys` (`task_group_order`, `task_group_name`, `task_seq`).

1. On epic worktree: `git fetch origin && git merge origin/ftr/AST-572-organization-tasks-dispatch-keys`.
2. Open `AdminScheduledActions.tsx` — confirm `allTaskKeys` type includes `task_group_order` / `task_group_name` and `sections` buckets by DB grouping (not config `phase`).
3. Confirm expanded filter bar from **AST-751** is present (`floorMin`, `autoFilter`, etc.).
4. If any check fails, **stop** — comment on AST-768 `@susan`: prerequisite not on ftr yet.

---

## Stage 1: Section/Group filter control and row intersection

**Done when:** Filter bar includes **Section/Group** with **All** plus every distinct task group from `allTaskKeys`, sorted by `task_group_order` then `task_group_name`; selecting a group shows only dispatch rows whose `task_key` belongs to that group; combined with Candidate, Task, Floor, AUTO, Debug, Freq, Min count, Batch size, and Run counts filters, all filters intersect (AND); with **Candidate → All**, one selected group shows a single collapsible section (or empty state) with the same within-section sort as single-candidate view; no API or backend changes.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, add state after `taskKeyFilter` (~line 263):

   ```ts
   const [sectionGroupFilter, setSectionGroupFilter] = useState("")
   ```

2. Add a `sectionGroupOptions` `useMemo` after `taskKeys` (~line 313), derived from **`allTaskKeys`** catalog metadata (not `data` rows — shows all Manage Tasks groups even when no dispatch row exists yet):

   ```ts
   const sectionGroupOptions = useMemo(() => {
     const seen = new Map<string, string>()
     for (const meta of Object.values(allTaskKeys)) {
       const name = meta.task_group_name || "(unassigned)"
       const key = `${meta.task_group_order || ""}\u0000${name}`
       if (!seen.has(key)) seen.set(key, name)
     }
     return [...seen.entries()]
       .sort(([a], [b]) => a.localeCompare(b))
       .map(([key, name]) => ({ key, name }))
   }, [allTaskKeys])
   ```

   ⚠️ **Decision:** Filter value is the same composite key `${task_group_order}\u0000${task_group_name}` the `sections` memo already uses (~line 377) — not display name alone — so grouping stays unambiguous if names ever collide.

3. In the `filteredRows` `useMemo` (~line 347), apply the section filter **after** `candidateFilter` and **before** `taskKeyFilter`:

   ```ts
   if (sectionGroupFilter) {
     filtered = filtered.filter(r => {
       const meta = allTaskKeys[r.task_key]
       const name = meta?.task_group_name || "(unassigned)"
       const key = `${meta?.task_group_order || ""}\u0000${name}`
       return key === sectionGroupFilter
     })
   }
   ```

4. Add `sectionGroupFilter` to the `filteredRows` dependency array.

5. In the `.admin-filters` block (~line 561), insert the new control **immediately after** `AdminCandidateFilterControl` and **before** the Task `<label>`:

   ```tsx
   <label>
     Section/Group
     <select value={sectionGroupFilter} onChange={e => setSectionGroupFilter(e.target.value)}>
       <option value="">All</option>
       {sectionGroupOptions.map(opt => (
         <option key={opt.key} value={opt.key}>{opt.name}</option>
       ))}
     </select>
   </label>
   ```

6. Do **not** change `sections` bucketing, `sortRowsWithinSection`, table columns, modals, run/stop, or polling — existing memos already consume `filteredRows`, so section panels and AUTO header counts automatically reflect the new filter.

7. Manual verification (required before `code()`): local dev, Admin → Scheduled Actions:
   - **All** shows every group panel that has rows (unchanged from today).
   - Pick **D. Job Analysis** (or equivalent) — only that group's panel(s) appear; rows inside match the group.
   - Set **Candidate → All**, same group — rows from multiple candidates appear; within-section order matches single-candidate (`task_seq`, then available desc when default sort).
   - Set **Task** to a key outside the selected group — table empty / "No dispatch tasks configured".
   - Set **AUTO → ON** with a group selected — only AUTO-on rows in that group.

⚠️ **Decision:** No new API endpoint — `task_keys` payload is the single source for group names, matching parent AC #1 and **AST-739** Manage Tasks alignment.

## Execution contract

Binding per **plan-child**: **Stage 1** only; **one commit** on epic worktree during **build-child**, publish to **`origin/sub/AST-572/AST-768-scheduled-actions-section-group-filter`**. Do not edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`. Do not edit `src/ui/api/**`, `src/utils/config.py`, or scheduler/dispatch core. On ambiguity — **`🛑 Stage 1 blocked`** on **AST-572** parent; stop.

## Self-Assessment

**Scope:** `minor` — one filter control and one filter branch in `AdminScheduledActions.tsx`; no API or config layers.

**Conf:** `high` — mirrors **AST-751** filter-bar pattern and reuses the existing `sections` composite key; prerequisites (**AST-751**, **AST-739**) are on ftr.

**Risk:** `low` — client-side display filter only; wrong intersection would mislead triage but cannot affect dispatch execution or claims.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Reuses `sections` composite key formula; one `filteredRows` memo — no duplicate filter passes. |
| §2.1 config | No new config keys; group list from DB-backed `task_keys` payload already loaded. |
| §2.4 batch | Not touched — UI read-only on dispatch rows. |
| §2.6 state machine | Not touched. |
| §3.3 imports | No new cross-layer imports; page stays in `src/ui/frontend`. |
| §3.5 naming | Follow existing `admin-filters` / `*Filter` state naming from **AST-751**. |

No conflicts requiring plan revision.

---

## Review (build)

**Built:** `origin/sub/AST-572/AST-768-scheduled-actions-section-group-filter` @ `4ac09c1`

Stage 1: Section/Group filter control sourced from `allTaskKeys` catalog metadata; `filteredRows` AND intersection after Candidate, before Task; filter bar placement after Candidate filter. Component tests deferred to Betty per build-child test-tree ban.

---

## Review (Radia)

**Ref:** `origin/sub/AST-572/AST-768-scheduled-actions-section-group-filter` @ `ce024eb` (product @ `4ac09c1`) · baseline `origin/dev`

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stage 1 matches plan: `sectionGroupFilter` state, `sectionGroupOptions` from `allTaskKeys`, `filteredRows` AND after Candidate / before Task, control after Candidate filter. |
| Product scope | `4ac09c1` touches only `AdminScheduledActions.tsx` — client-side filter; no API/backend in engineer commit. |
| Group key | Reuses `${task_group_order}\u0000${task_group_name}` composite key aligned with `sections` memo — consistent with plan decision. |
| Layer / rules | §3.3 — frontend-only; no new cross-layer imports. §2.1 — group list from existing `task_keys` payload. |
| Tests | Betty manifest: 6 cases in `AST-768 section/group filter`; narrowed Vitest run green on publish tip. |

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **discuss** | Publish tip vs `origin/dev` (not in `4ac09c1`) | **Sibling bleed — AST-750:** `src/utils/config.py` (`DISPATCH_SCORE_FLOOR_VALUES`), `src/ui/api/api_admin.py` (`/dispatch_tasks/score_floor_options`), and `docs/features/interface/ast-750-*.md` appear on the three-dot diff via `merge-tests`; AST-768 plan explicitly out-of-scopes API/config. UI still hardcodes `scoreFloorOptions` 1.00–10.00 — endpoint is unused on this ref. Confirm at **merge-child** whether to strip from sub or defer to AST-750 rollup. |
| advisory | `AdminScheduledActions.tsx` | Composite section key formula appears in three memos (`sectionGroupOptions`, `filteredRows`, `sections`); plan chose duplication over a helper — acceptable; optional micro-DRY later if Susan wants. |

### Recommended actions

| Owner | Action |
| --- | --- |
| Katherine (`resolve-child`) | No product changes required for AST-768 — implementation is plan-complete. |
| Chuckles / merge-child | Resolve AST-750 backend/doc bleed on publish tip before or during ftr rollup (see **discuss** above). |

---

## Resolution

**Date:** 2026-06-23  
**Review ref:** `origin/sub/AST-572/AST-768-scheduled-actions-section-group-filter` @ `94ebec0` (Radia doc) · product @ `4ac09c1`

No **fix-now** items. Product unchanged from build @ `4ac09c1` + Betty `merge-tests(AST-768)` @ `ce024eb`. **discuss** AST-750 sibling bleed on publish tip deferred to Chuckles at **merge-child** (endpoint unused; UI still hardcodes floor options per plan). Advisory composite-key duplication accepted per plan.

**§9a dry-run:** `origin/sub/AST-572/AST-768-scheduled-actions-section-group-filter` → `origin/dev`: clean · → `origin/ftr/AST-572-organization-tasks-dispatch-keys`: clean
