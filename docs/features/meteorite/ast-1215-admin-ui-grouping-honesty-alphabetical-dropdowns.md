# Admin UI grouping honesty + alphabetical dropdowns

**Linear:** [AST-1215](https://linear.app/astralcareermatch/issue/AST-1215/admin-ui-grouping-honesty-alphabetical-dropdowns-ui-groupingssequences)  
**Parent:** [AST-1185](https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven)  
**Publish ref:** `sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns`

After AST-1214’s live alphabetical Admin catalog (`GET /api/admin/dispatch_tasks/task_keys`) and with Gaze/Meteorite grouping + alias catalog keys already live (AST-1183 / AST-1184 at User Testing), this ticket owns the **React** honesty pass: Scheduled Actions and Manage Tasks must render section headers and within-section row order only from `agent_task` grouping metadata (`task_group_order`, `task_group_name`, `task_seq`), every in-scope Admin **task-key** dropdown must list keys alphabetically by **task_key string** (including alias identities when present in the payload), and touched Admin frontend paths must not restate grouping membership or section order in hard-coded React lists. Alias → master resolution stays backend/config — the UI shows the alias key as-is.

### Planner audit (tip stacked on `origin/ftr/AST-1185-…` after AST-1214)

| Surface | Grouping | Task-key dropdown | Hard-coded membership/order lists |
|---------|----------|-------------------|-----------------------------------|
| `AdminScheduledActions.tsx` | Sections keyed by `task_group_order` + `task_group_name` from catalog meta; within-section default sort by `task_seq` then task_key | Add/Edit modal: `Object.keys(allTaskKeys).sort()` from `GET …/dispatch_tasks/task_keys` | None found |
| `AdminTaskPrompts.tsx` (Manage Tasks) | Same composite section key from row fields; within-section by `task_seq` then task_key | run_next options from loaded `tasks` via `localeCompare` | None found |
| `AdminAnthropicAdHoc.tsx` | N/A (no section chrome) | Task Key select + Save As list: `tasks.map` with **no** client sort (array order today follows `list_candidate_tasks` `ORDER BY task_key`, but AC wants an explicit client contract) | None found |
| `AdminVectorFeedback.tsx` | N/A | Rubric-owner subset via `GET …/vector_feedback/task_keys` | **Out of scope** (same exclusion as AST-1214) |
| Jobs / non-Admin | — | — | **Out of scope** (parent Admin-only default) |

This ticket therefore **preserves** existing grouping behavior on Scheduled Actions / Manage Tasks, **unifies** lexicographic task_key sorting behind one helper (match Python/`sorted` / SQLite `ORDER BY task_key` ordinal compare — not locale-sensitive `localeCompare`), and **applies** that helper to Ad Hoc so every in-scope Admin task-key picker has the same explicit contract.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/taskKeySort.ts` | New: `compareTaskKeys` + `sortedTaskKeys` (lexicographic task_key string order) | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Use helper for catalog picker keys + filter task-key option list; leave section/`task_seq` grouping logic intact | ui |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Use helper for `taskKeyOptions` and task_key tie-break after `task_seq`; leave section grouping intact | ui |
| `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Sort Task Key `<select>` and Save As list via helper by `task_key` | ui |

**Out of scope (do not edit):**

| Owner | What |
|-------|------|
| AST-1214 (done / UT) | Admin API catalog membership, write gates, form-meta |
| AST-1183 / AST-1184 | Seed grouping rename; `master_task_key` resolve |
| AST-1182 | `parse_meteorite_email` → `meteorite_email` seed rename |
| Betty | Any `tests/` / bible — engineer does not edit test-tree |
| This ticket explicitly excludes | `AdminVectorFeedback.tsx` task filter; Jobs UI section configs; inventing React alias→master maps; API/config/`src/data` |

## Execution contract

The plan is binding. Execute stages in order. Do not edit API/config/seed/tests. Do not add React alias→master maps. When blocked — comment on **AST-1185** with the Stage N template from plan-child.

---

## Stage 1: Shared lexicographic task_key sort helper

**Done when:** `src/ui/frontend/src/lib/taskKeySort.ts` exports `compareTaskKeys(a, b)` and `sortedTaskKeys(keys)` that order strings by plain lexicographic compare (`a < b` / `a > b`), matching Python `sorted()` / SQLite `ORDER BY task_key` for ASCII snake_case keys. No `localeCompare`. No other files changed yet.

1. Create `src/ui/frontend/src/lib/taskKeySort.ts` with exactly:

```ts
/** Lexicographic task_key order (Python sorted() / SQLite ORDER BY task_key). Not locale-sensitive. */
export function compareTaskKeys(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0
}

export function sortedTaskKeys(keys: Iterable<string>): string[] {
  return [...keys].sort(compareTaskKeys)
}
```

⚠️ **Decision:** One shared helper instead of three slightly different `.sort()` / `localeCompare` call sites, so dropdown order cannot drift from the AST-1214 catalog contract. Rejected: leave Ad Hoc relying only on API array order.

---

## Stage 2: Scheduled Actions + Manage Tasks — wire helper; keep grouping data-driven

**Done when:**

- `AdminScheduledActions.tsx` Add/Edit Task `<select>` options are `sortedTaskKeys(Object.keys(allTaskKeys))` (still driven by `GET /api/admin/dispatch_tasks/task_keys`; still shows alias keys when present in that payload).
- Filter chip / task-key filter option list built from loaded rows also uses `sortedTaskKeys` (or `[...set].sort(compareTaskKeys)`).
- Section headers still come only from catalog/row `task_group_order` + `task_group_name`; default within-section order still `task_seq` then `compareTaskKeys` (replace the existing `localeCompare` / default `.sort()` tie-breaks for **task_key** only).
- `AdminTaskPrompts.tsx` `taskKeyOptions` uses `sortedTaskKeys`; within-section tie-break after `task_seq` uses `compareTaskKeys`.
- No new hard-coded task-key arrays, section-name arrays, or phase/seq inventories added. No edits that invent alias→master mapping.

1. In `AdminScheduledActions.tsx`, import `{ compareTaskKeys, sortedTaskKeys }` from `../lib/taskKeySort`.
2. Replace the Add/Edit modal options line  
   `Object.keys(allTaskKeys).sort().map(...)`  
   with  
   `sortedTaskKeys(Object.keys(allTaskKeys)).map(...)`.
3. Replace `taskKeys` memo  
   `[...new Set(data.map(d => d.task_key))].sort()`  
   with  
   `sortedTaskKeys(new Set(data.map(d => d.task_key)))`.
4. In `sortRowsWithinSection`, when comparing task_key strings, use `compareTaskKeys(a.task_key, b.task_key)` instead of `a.task_key.localeCompare(b.task_key)`.
5. Leave section composite-key sorts (`task_group_order\u0000name`.localeCompare) unchanged — those order **sections**, not the task-key catalog.
6. In `AdminTaskPrompts.tsx`, import the same helpers; set  
   `taskKeyOptions` to `sortedTaskKeys(new Set(tasks.map(t => t.task_key)))`;  
   in within-section sort after `task_seq`, use `compareTaskKeys(a.task_key, b.task_key)`.
7. Do **not** change run_next cycle-filter logic except that it continues to consume `taskKeyOptions` (already alphabetical after step 6). Keep the “prepend current invalid run_next” UI exception in `runNextSelectKeysForUi` — that is edit-state honesty, not catalog order.

⚠️ **Decision:** Sentinel `task_seq ?? 999` for missing seq stays — it is a missing-value fallback, not a membership/order inventory. Do not replace with a hard-coded seq table.

---

## Stage 3: Agent Ad Hoc — explicit alphabetical task_key lists

**Done when:** Agent Ad Hoc Task Key `<select>` options and Save As menu entries appear in lexicographic `task_key` order via `sortedTaskKeys` / `compareTaskKeys`, even if `/api/admin/tasks` order changes later. No alias→master UI. No Vector Feedback / Jobs edits.

1. In `AdminAnthropicAdHoc.tsx`, import `{ compareTaskKeys, sortedTaskKeys }` from `../lib/taskKeySort`.
2. Add a memo (or inline once)  
   `const taskKeysSorted = useMemo(() => [...tasks].sort((a, b) => compareTaskKeys(a.task_key, b.task_key)), [tasks])`  
   — or derive `sortedTaskKeys(tasks.map(t => t.task_key))` and look up rows; prefer sorting the task objects with `compareTaskKeys` so labels stay attached.
3. Replace both `tasks.map(t => …)` option/menu renders (Task Key select ~line 273 and Save As list ~line 358) to iterate the sorted list.
4. Final grep on the four Files Changed paths for hard-coded task-key membership arrays (e.g. string-literal lists of `grade_do`, `fetch_jd`, section title inventories). Expected: **zero** removals beyond the sort wiring. If a hard-coded membership/order list is found in those paths, delete it and keep using API/catalog data — do not leave parallel lists. If a list is found **outside** Files Changed that this ticket’s AC requires, stop and comment on **AST-1185** (do not silently expand Files Changed).

---

## Self-Assessment

**Scope:** `Single-Component` — Admin React pages + one shared `lib/` sort helper; no API/config/seed; Vector Feedback and Jobs excluded.

**Conf:** `high` — planner audit shows grouping already data-driven on the two primary surfaces; remaining work is an explicit alphabetical contract helper plus Ad Hoc wiring against known payloads.

**Risk:** `low` — sort-order / display-only; dispatch, claim, and alias resolve paths untouched. Wrong sort would only affect option order; wrong grouping edit would mis-order Admin chrome but this plan preserves existing grouping formulas.

## Self-review vs ASTRAL_CODE_RULES

- §1.3 DRY — shared `taskKeySort` helper for three call sites.
- §1.4 / `astral.standards.no-hardcoded-sets` — no new membership sets; audit expects none to remove on tip.
- §3.2 / `astral.layers.ui-config-driven-business-logic` — grouping/order from API/`agent_task` metadata; React only renders.
- §3.5 / `astral.ui.frontend-file-placement` — pages stay flat under `pages/`; helper under `lib/`.
- `astral.standards.in-scope-only` — no API, seed, alias resolve, Vector Feedback, or Jobs UI.
- §2.1 / §2.4 / §2.6 / §3.3 — N/A (no config blocks, batch claim, state machine, or Python import-direction changes).

## Review

**Publish ref:** `sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns`  
**Code tip:** `7e6db2fb` (Stage 1 `taskKeySort` → Stage 2 Scheduled Actions + Manage Tasks → Stage 3 Ad Hoc).

Note for Betty: lexicographic vs prior `localeCompare` is contract-hardening — on today’s ASCII catalog the option order is unchanged; assert option order equals API/`sorted` payload order, not a visible reorder.
)
