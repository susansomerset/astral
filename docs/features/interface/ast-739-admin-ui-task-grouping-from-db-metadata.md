<!-- linear-archive: AST-739 archived 2026-06-23 -->

## Linear archive (AST-739)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-739/admin-ui-task-grouping-from-db-metadata-organizing-tasks  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-734 — Organizing Tasks  
**Blocked by / blocks / related:** parent: AST-734; blocks: AST-740

### Description

## What this implements

Manage Tasks and Scheduled Actions (and any other admin UI that orders catalog tasks without runtime timestamps) consume the four DB grouping fields from Organizing Tasks. Manage Tasks edit modal exposes all four fields; list views group into collapsible sections by `task_group_order` / `task_group_name`, sort rows by `task_seq`, show `task_name` as the human-readable label, and never display the numeric sequence. Scheduled Actions resolves dispatch alias keys to catalog metadata the same way AST-568 resolved phase/seq, but reads DB fields instead of config.

## Acceptance criteria

4. Manage Tasks list groups tasks into collapsible sections ordered by `task_group_order`; within each section, rows order by `task_seq`; section titles show `task_group_name`; no visible `task_seq` column or number.
5. Scheduled Actions groups and sorts dispatch rows using DB metadata (including alias keys resolving to catalog metadata).
6. Invalid or inconsistent group data can be saved without server-side rejection (Susan verifies manually).
7. Existing component tests for Manage Tasks and Scheduled Actions are updated where grouping/sort expectations change; no regressions to edit-modal prompt save or dispatch row actions.

## Boundaries

* Does not implement AST-735 Scheduled Actions screen edits (AUTO summary, expanded filters, Candidate column layout) — separate parent blocked by this epic.
* Does not remove `phase` / `seq` from TASK_CONFIG — sibling Ada ticket.
* Does not change dispatch run/stop, scheduler, or Stop All / Add Task behaviors beyond grouping/sort source.
* Collapsible sections must still allow zero expanded panels.

## Notes for planning

* Reuse CollapsiblePanel patterns from current Manage Tasks / Scheduled Actions (AST-426, AST-568).
* `GET /api/admin/dispatch_tasks/task_keys` should expose grouping metadata from DB for form defaults.
* Task keys remain read-only from catalog; no add/delete in UI.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-734-organizing-tasks`, child `sub/AST-734/<child-id>-admin-ui-task-grouping-from-db-metadata`. Blocked by metadata storage child until API/DB fields exist.

### Comments

#### radia — 2026-06-18T22:37:47.215Z
## Radia review — AST-739

**Ref:** `origin/dev...origin/sub/AST-734/AST-739-admin-ui-task-grouping-from-db-metadata` @ `c002406` (includes prerequisite AST-738 from ftr merge + Betty tests).

**Verdict:** Clean — no **fix-now** / **discuss**.

### Plan (Stages 1–3)
- `GET /api/admin/dispatch_tasks/task_keys` returns `task_group_*` via `_catalog_task_grouping_meta`; drops `phase`/`seq`; orphan keys get empty defaults.
- Manage Tasks: section bucketing on `task_group_order`+`task_group_name`, within-section `task_seq` sort, `task_name` display, four editable modal fields on PUT.
- Scheduled Actions: same section pattern; Task column still `task_key`; default sort uses `task_seq`.

### ASTRAL_CODE_RULES
- **§3.2 layer:** Frontend pages API-only; `api_admin.py` uses existing `database.get_agent_task` — no new layer violations.
- **§2.1 config:** UI paths no longer read `TASK_CONFIG` `phase`/`seq` for grouping (AST-738 backward-compat `phase`/`seq` on Manage Tasks GET remains until AST-740 — expected).
- **§5f/§5g:** N/A (no debug/LLM external changes).

### Advisory (non-blocking)
- `_dispatch_task_key_form_meta` docstring still mentions "TASK_CONFIG first" — stale after DB grouping (`api_admin.py`).
- Stray `# placeholder removed = "qualify_job_listings"` in `test_agent_tasks.py` header (Betty cleanup).
- Duplicate section-key `useMemo` across two pages — acceptable per plan Self-Review.

**Doc:** `docs/features/interface/ast-739-admin-ui-task-grouping-from-db-metadata.md` — Review (Radia) section.

#### betty — 2026-06-18T22:29:52.323Z
## QA test manifest (AST-739)

**Publish:** `origin/sub/AST-734/AST-739-admin-ui-task-grouping-from-db-metadata` @ `3932d03` (`merge-tests(AST-739): origin/tests 328867a`)

**Prerequisite:** **AST-738** data/API grouping on publish tip (sibling `merge-tests` on ftr rollup).

### 1. New coverage
1. **API — `dispatch_task_keys` DB grouping** (`TestAst739DispatchTaskKeysGrouping`): `consult_do` reads `grade_do` agent_task row; orphan keys get empty grouping; no `phase`/`seq` keys.
2. **Vitest — Manage Tasks routed page** (`test_AdminTaskPrompts.test.tsx` **AST-739**): section labels from `task_group_name`; edit modal PUT includes four grouping fields; `task_name` display.
3. **Vitest — Scheduled Actions routed page** (`test_AdminScheduledActions.test.tsx` **AST-739**): section labels driven by `task_keys` grouping metadata.

### 2. Broken / revised tests
1. **`test_ast549_task_keys_config_derivation_authoritative`** — no longer asserts config `phase`/`seq`; expects `task_group_name` key instead.
2. **`test_AdminTaskPrompts.test.tsx`** — fixtures use `task_group_*` not `phase`/`seq`; `vi.mock(api)` preserves `setAuthTokenGetter` / `setUnauthorizedHandler` (partial mock like Scheduled Actions).
3. **`test_AdminScheduledActions.test.tsx`** — `taskKeysConfig` / `keysDefault` mocks use DB grouping shape.
4. **`test_AdminTaskPrompts` AST-513** — `task_name: contemplate_job` so row click matches display label.

### 3. Existing coverage (unchanged)
- **AST-738** data/API tests on publish tip (from `origin/tests` ancestry) — still required green for grouping persistence underlying UI.

### Run (test-child)
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst739DispatchTaskKeysGrouping \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast549_task_keys_config_derivation_authoritative \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx
```

**Pass criterion:** pytest + Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### Bible shasum (`origin/sub/...`)
- `docs/test-bible/frontend/pages.md` `c0e684ae248779f450c19dd0158688d7a663b4b4758143f445f5d0fb96e67013`
- `docs/test-bible/ui/api/api_admin.md` `658553beaa0139e3db05dabeedfb7128f0d3f4c19f4765f66112ae6e716b1f23`

#### katherine — 2026-06-18T22:17:45.684Z
Plan doc on publish ref:

https://github.com/susansomerset/astral/blob/sub/AST-734/AST-739-admin-ui-task-grouping-from-db-metadata/docs/features/interface/ast-739-admin-ui-task-grouping-from-db-metadata.md

**Scope:** Single-Component — `api_admin.py` dispatch `task_keys` DB grouping + Manage Tasks + Scheduled Actions React section/sort/label swap off config `phase`/`seq`.

**Conf:** Medium — AST-568 CollapsiblePanel pattern is reusable; build blocked until AST-738 merges to ftr (DB columns + task GET/PUT/_enrich_tasks).

**Risk:** Medium — alias resolution (`consult_do` → `grade_do`) must read catalog row grouping or rows land in `(unassigned)`; no pipeline execution impact.

Three stages: (1) `_dispatch_task_key_form_meta` DB fields, (2) Manage Tasks list/modal, (3) Scheduled Actions sections. Prerequisite gate documents AST-738 on ftr before Stage 1.

---

# Admin UI task grouping from DB metadata (Organizing Tasks)

**Linear:** [AST-739](https://linear.app/astralcareermatch/issue/AST-739/admin-ui-task-grouping-from-db-metadata-organizing-tasks)  
**Parent:** [AST-734](https://linear.app/astralcareermatch/issue/AST-734/organizing-tasks)  
**Publish ref:** `sub/AST-734/AST-739-admin-ui-task-grouping-from-db-metadata`

Susan wants task grouping and ordering to be admin-editable in the database, not read from `TASK_CONFIG` `phase` / `seq`. **AST-738** (Hedy) adds the four DB columns, deploy seed, and Manage Tasks API read/write on `GET/PUT /api/admin/tasks` and `_enrich_tasks`. **This ticket** switches the Manage Tasks and Scheduled Actions React screens (plus `GET /api/admin/dispatch_tasks/task_keys`) to consume those DB fields exclusively for sectioning, within-group sort, and human-readable labels — without changing dispatch execution, scheduler behavior, or prompt save semantics.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | `_dispatch_task_key_form_meta` / `dispatch_task_keys` return DB grouping fields via catalog resolution | ui |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Group/sort/label from DB fields; edit modal inputs; remove visible seq | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Group/sort from DB metadata on `task_keys` payload; drop `phase`/`seq` usage | ui |

**Out of scope (sibling tickets):** `src/data/database.py` schema/seed (`AST-738`); `_enrich_tasks` / task `GET`/`PUT` grouping persistence (`AST-738`); `TASK_CONFIG` `phase`/`seq` removal (`AST-740`); Scheduled Actions layout changes (`AST-735`).

**QA manifest (Betty — not engineer commits):** Update mocks/assertions in `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`, `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx`, and `tests/component/ui/api/test_api_admin.py` (`test_ast549_task_keys_config_derivation_authoritative` and any `phase`/`seq` assertions on task list/get).

## Prerequisite (build gate — not a commit stage)

**Done when:** `origin/ftr/AST-734-organizing-tasks` includes merged **AST-738** (`code(AST-738)` or later), and a smoke check confirms DB-backed grouping fields on the Manage Tasks API.

1. On epic worktree, run mandatory merge: `git fetch origin && git merge origin/ftr/AST-734-organizing-tasks`.
2. Confirm `agent_task` current rows expose `task_group_order`, `task_group_name`, `task_seq`, `task_name` (via app DB or `GET /api/admin/tasks/<known_key>` after local boot).
3. Confirm `PUT /api/admin/tasks/<key>` accepts and returns the four grouping fields without altering prompt segments (AST-738 behavior).
4. If any check fails, **stop** — comment on AST-739 `@susan` / parent: AST-738 not on ftr yet; do not implement against config `phase`/`seq`.

⚠️ **Decision:** AST-739 assumes AST-738 is merged to ftr before **Stage 1**. No dual-read fallback from `TASK_CONFIG` — single source is DB per parent epic.

---

## Stage 1: Scheduled Actions `task_keys` — DB grouping metadata

**Done when:** `GET /api/admin/dispatch_tasks/task_keys` returns `task_group_order`, `task_group_name`, `task_seq`, and `task_name` for catalog and schedulable keys (resolved through `resolve_dispatch_task_config_key`), and no longer returns `phase` or `seq`. `consult_do` grouping matches `grade_do` DB row. Orphan dispatch-only keys keep entity/trigger defaults with empty/null grouping.

1. In `src/ui/api/api_admin.py`, add a module-level helper immediately above `_dispatch_task_key_form_meta` (~line 715):

   ```python
   def _catalog_task_grouping_meta(catalog_key: str) -> dict:
       """Grouping fields from current agent_task row; empty defaults when missing."""
       row = database.get_agent_task(catalog_key) or {}
       seq = row.get("task_seq")
       return {
           "task_group_order": (row.get("task_group_order") or ""),
           "task_group_name": (row.get("task_group_name") or ""),
           "task_seq": float(seq) if seq is not None else None,
           "task_name": (row.get("task_name") or ""),
       }
   ```

2. Rewrite `_dispatch_task_key_form_meta(task_key: str)` body to:
   - Keep existing `catalog_key = resolve_dispatch_task_config_key(task_key)` and entity/trigger/`is_scored` derivation unchanged (lines 717–725 today).
   - Replace the return dict keys `"phase"` and `"seq"` with `**_catalog_task_grouping_meta(catalog_key)`.
   - Final return shape:

     ```python
     return {
         "entity_type": entity_type or "",
         "trigger_state": trigger_state,
         "is_scored": dispatch_task_key_is_scored(task_key),
         **_catalog_task_grouping_meta(catalog_key),
     }
     ```

3. In `dispatch_task_keys()`, update the orphan-key fallback branch (~lines 752–758) when `k not in seen`: remove `"phase": None, "seq": None`; use:

   ```python
   "task_group_order": "",
   "task_group_name": "",
   "task_seq": None,
   "task_name": "",
   ```

4. Do **not** change `list_dtasks`, create/update dispatch routes, or schedulable-key entity/trigger derivation.

⚠️ **Decision:** Dispatch wrapper keys (e.g. `consult_do`) resolve catalog key first, then read grouping from that catalog row — same alias rule as AST-568, new field source.

---

## Stage 2: Manage Tasks — list grouping, labels, edit modal

**Done when:** Manage Tasks list renders collapsible sections ordered by `task_group_order`, titled with `task_group_name`, rows sorted by `task_seq` with no visible sequence column; row Task cells show `task_name` (fallback `task_key`); edit modal has four editable grouping fields that persist via PUT and reload on reopen; zero expanded sections still works; prompt save/run-next/preview unchanged.

1. In `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`, update `AgentTask` interface (~lines 11–17): remove `phase` and `seq`; add:

   ```ts
   task_group_order: string
   task_group_name: string
   task_seq: number | null
   task_name: string
   ```

2. Add edit-modal state hooks after existing `editRunNext` (~line 167):

   ```ts
   const [editGroupOrder, setEditGroupOrder] = useState("")
   const [editGroupName, setEditGroupName] = useState("")
   const [editTaskSeq, setEditTaskSeq] = useState("")
   const [editTaskName, setEditTaskName] = useState("")
   ```

3. Replace the `sections` `useMemo` (~lines 208–222) with grouping keyed by `${task_group_order}\u0000${task_group_name || "(unassigned)"}`:

   - Bucket each task into `bySectionKey[key]`.
   - Sort section keys with `localeCompare` on the full composite key (preserves order then name).
   - Within each section, sort rows by `(a.task_seq ?? 999) - (b.task_seq ?? 999)`, tie-break `task_key.localeCompare`.
   - Map to `{ sectionKey, groupName, rows }` where `groupName = rows[0]?.task_group_name || "(unassigned)"`.

4. Rename `openPhase` / `resolvedOpenPhase` to `openSection` / `resolvedOpenSection` (or equivalent) keyed on `sectionKey` instead of `phase`. CollapsiblePanel `label` becomes `{groupName} ({sec.rows.length})`.

5. In the list table `<thead>` (~line 367), **remove** the `Seq` column header and its `<td>` (~line 385).

6. In the Task column body cell (~lines 386–388), display `{row.task_name || row.task_key}`; keep the red `●` not-ready indicator before the label when `!row.task_ready`.

7. In `openEdit` (~lines 270–286), after fetching full task, initialize grouping state:

   ```ts
   setEditGroupOrder(String(full.task_group_order ?? ""))
   setEditGroupName(String(full.task_group_name ?? ""))
   setEditTaskSeq(full.task_seq != null ? String(full.task_seq) : "")
   setEditTaskName(String(full.task_name ?? ""))
   ```

8. In `handleSave` PUT body (~lines 294–304), add:

   ```ts
   task_group_order: editGroupOrder,
   task_group_name: editGroupName,
   task_seq: editTaskSeq.trim() === "" ? null : parseFloat(editTaskSeq),
   task_name: editTaskName,
   ```

   Do not add client-side validation beyond empty-string → `null` for `task_seq`.

9. In the edit modal (~lines 417–422), **remove** read-only Phase/Seq spans. Insert four `dep-field` blocks **above** the Agent field:

   ```tsx
   <div className="dep-field">
     <label className="dep-field-label">Group order</label>
     <input className="dep-input" value={editGroupOrder} onChange={e => setEditGroupOrder(e.target.value)} />
   </div>
   <div className="dep-field">
     <label className="dep-field-label">Group name</label>
     <input className="dep-input" value={editGroupName} onChange={e => setEditGroupName(e.target.value)} />
   </div>
   <div className="dep-field">
     <label className="dep-field-label">Task sequence</label>
     <input className="dep-input" type="number" step="any" value={editTaskSeq} onChange={e => setEditTaskSeq(e.target.value)} />
   </div>
   <div className="dep-field">
     <label className="dep-field-label">Task name</label>
     <input className="dep-input" value={editTaskName} onChange={e => setEditTaskName(e.target.value)} />
   </div>
   ```

   Modal title stays `Edit: ${editTask.task_key}` (key remains authoritative identifier).

10. Do **not** change token textareas, run-next graph logic, preview flow, or `loadAll` URLs.

⚠️ **Decision:** List shows human-readable `task_name` only; `task_key` remains in modal title and is not editable — catalog keys are config-owned per parent epic.

---

## Stage 3: Scheduled Actions — DB-backed sections and sort

**Done when:** Scheduled Actions sections use `task_group_name` / `task_group_order` from `task_keys` payload; within-section default sort uses `task_seq`; Task column still shows dispatch `task_key`; filters, run/stop, modals, and column freeze behavior unchanged; zero expanded sections still works.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, update `ScheduledPhaseTableProps.allTaskKeys` and component state type (~lines 59, 221): replace `phase: string | null; seq: number | null` with:

   ```ts
   task_group_order: string
   task_group_name: string
   task_seq: number | null
   task_name: string
   ```

2. Replace `sortRowsWithinSection` default branch (~lines 303–309): when `sortCol === "_default"`, compare `allTaskKeys[a.task_key]?.task_seq ?? 999` vs same for `b`.

3. Replace `sections` `useMemo` (~lines 328–338) with the same section-key pattern as Stage 2 (`task_group_order` + `task_group_name`, sort sections by composite key, `(unassigned)` fallback).

4. Rename `openPhase` / `resolvedOpenPhase` to section-key tracking (mirror Stage 2).

5. Update CollapsiblePanel labels to `{groupName} ({count})` using `task_group_name`.

6. Leave Task column rendering as `row.task_key` (dispatch identity unchanged).

7. Do **not** change candidate filter, task filter, thread polling, modals, Stop All, or table column set.

⚠️ **Decision:** Scheduled Actions displays dispatch `task_key` in the table; DB `task_name` is available on the payload for future UI but not shown in this ticket (Susan did not request dispatch row relabeling).

---

## Self-Assessment

**Scope:** `Single-Component` — three UI-layer files (one API helper + two React pages); no data layer or config edits.

**Conf:** `Medium` — pattern reuse from AST-568 phase sections is clear, but implementation depends on AST-738 API shape landing on ftr first.

**Risk:** `Medium` — wrong grouping source or broken alias resolution would mis-bucket dispatch rows (e.g. `consult_do` under `(unassigned)`), but would not affect pipeline execution.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Small duplicate section-key logic in two pages is acceptable per parent boundary (no mandatory shared package); optional follow-up only if Susan asks. |
| §2.1 config | No new config keys; explicitly stops reading `TASK_CONFIG` `phase`/`seq` in these UI paths. |
| §2.4 batch | N/A — no batch/dispatch changes. |
| §2.6 state machine | N/A — display-only. |
| §3.3 imports | UI → API only; `api_admin.py` uses existing `database.get_agent_task` (data layer). |
| §3.5 naming | Field names match parent epic: `task_group_order`, `task_group_name`, `task_seq`, `task_name`. |

No conflicts requiring plan revision.

## QA / test manifest hints (Betty)

| File | Expected change |
|------|-----------------|
| `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` | Mock tasks use four grouping fields; section button labels use `task_group_name`; no `Seq` column assertion; PUT body includes grouping fields when edited. |
| `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` | `taskKeysConfig` uses grouping fields; section headers like `/D\. Job Analysis \(1\)/` become group names from mocks; default sort uses `task_seq`. |
| `tests/component/ui/api/test_api_admin.py` | `test_ast549_task_keys_config_derivation_authoritative` asserts `consult_do` grouping matches `grade_do` **DB** fields (monkeypatch `get_agent_task`), not `TASK_CONFIG` phase/seq. |

---

## Review (build)

**Built:** `origin/sub/AST-734/AST-739-admin-ui-task-grouping-from-db-metadata` @ `736c306` (`d9dbdb6` task_keys API, `487e0a2` Manage Tasks UI, `736c306` Scheduled Actions UI).

**Out of build scope (Betty / qa-child):** component/API test updates per plan QA hints; config `phase`/`seq` removal (AST-740).

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-734/AST-739-admin-ui-task-grouping-from-db-metadata` @ `3932d03`  
**Tip includes:** AST-739 UI/API commits + prerequisite AST-738 merge from `origin/ftr/AST-734-organizing-tasks` + Betty `merge-tests(AST-739)`.

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity (Stages 1–3) | `_catalog_task_grouping_meta` / `_dispatch_task_key_form_meta` / orphan fallback match plan; Manage Tasks + Scheduled Actions section-key bucketing, sort, modal fields, and PUT body align with spec. |
| AST-568 alias | `consult_do` grouping resolves via catalog key (`grade_do`) — covered by `TestAst739DispatchTaskKeysGrouping`. |
| Layer compliance (§3.2) | UI pages consume API payloads only; `api_admin.py` uses existing `database.get_agent_task` pattern. No new `src/data` imports in frontend. |
| Prerequisite AST-738 | Data columns, seed, `_enrich_tasks` / GET·PUT grouping on Manage Tasks API present on publish tip — required gate satisfied. |
| Tests / bible | Manifest updates and AST-739/738 component tests match plan QA hints; green per Tests Passed. |

### Issues

None (**fix-now** / **discuss**).

### Recommended actions

| Severity | Item | Location |
| --- | --- | --- |
| Advisory | Stale docstring still says "TASK_CONFIG first" on `_dispatch_task_key_form_meta` — grouping is now DB-backed. | `src/ui/api/api_admin.py` |
| Advisory | Stray `# placeholder removed = "qualify_job_listings"` in test module header (Betty cleanup). | `tests/component/data/database/test_agent_tasks.py` |
| Advisory | Duplicate section-key `useMemo` in two pages — acceptable per plan Self-Review; shared helper only if Susan asks. | `AdminTaskPrompts.tsx`, `AdminScheduledActions.tsx` |

---

## Resolution

**Date:** 2026-06-18  
**Review ref:** Radia comment @ `c002406` — clean, no fix-now / discuss.

No product changes required. §9a dry-run: `origin/sub/AST-734/AST-739-admin-ui-task-grouping-from-db-metadata` merges cleanly into `origin/dev` and `origin/ftr/AST-734-organizing-tasks`.

Advisory items (stale `_dispatch_task_key_form_meta` docstring, Betty test header cleanup, shared section helper) deferred — non-blocking per Radia.
