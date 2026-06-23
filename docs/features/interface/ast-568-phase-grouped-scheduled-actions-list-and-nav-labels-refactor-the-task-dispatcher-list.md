<!-- linear-archive: AST-568 archived 2026-06-15 -->

## Linear archive (AST-568)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-568/phase-grouped-scheduled-actions-list-and-nav-labels-refactor-the-task  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-567 — Refactor the Task Dispatcher List  
**Blocked by / blocks / related:** parent: AST-567

### Description

## What this implements

Phase-grouped Scheduled Actions list (CollapsiblePanel like Manage Tasks), seq order within phase, phase/seq metadata for task_key, nav and page title **Scheduled Actions**.

## Acceptance criteria

1. Sidebar **Scheduled Actions** → `/admin/scheduled_actions`.
2. Page heading **Scheduled Actions**.
3. Multiple phases → collapsible sections with full table behavior.
4. Rows ordered by catalog **seq** within phase.
5. Zero sections expanded allowed.
6. Filters still work; empty sections handled.
7. Stop All, Add, run/stop, AUTO, Dbg, modals unchanged.

## Boundaries

No dispatcher/scheduler/schema changes beyond phase/seq metadata for UI. No route rename.

## Notes for planning

`AdminScheduledActions.tsx`, `NAV_CONFIG`, `api_admin.py` task_keys if needed. Reuse `CollapsiblePanel` from `AdminTaskPrompts.tsx`.

## Git branch (authoritative)

Parent `ftr/ast-567`; child `sub/AST-567/<child-id>-scheduled-actions-phase-sections`.

### Comments

#### radia — 2026-06-03T14:46:53.396Z
**Doc publish (Joan follow-up):** Review section landed on `origin/sub/AST-567/AST-568-scheduled-actions-phase-sections` @ `c1716843` (cherry-pick of dev-radia `a0067704`; Joan `store-review-commit` reported empty pick because content already matched tip).

#### radia — 2026-06-03T14:45:59.022Z
**Review (Radia)** — `origin/dev...origin/sub/AST-567/AST-568-scheduled-actions-phase-sections` @ `a2298032`

**fix-now:** none

**discuss:** none

**advisory:** Optional later `test_api_admin` assertion that `GET /api/admin/dispatch_tasks/task_keys` returns `phase`/`seq` for a known `TASK_CONFIG` key (Vitest page mocks + bible §7.13zy already cover AST-568).

**Plan / rules:** Stages 1–4 match combined plan — `task_keys` `phase`/`seq`, `NAV_CONFIG` **Scheduled Actions**, `CollapsiblePanel` sections aligned with `AdminTaskPrompts.tsx` (alphabetic phase order, `seq` default sort within section, zero expanded OK). Filters, Stop All, Add, run/stop, AUTO, Dbg, modals, polling unchanged. No §1.5 / §3.2 violations in diff.

**Doc:** `docs/features/interface/ast-568-phase-grouped-scheduled-actions-list-and-nav-labels-refactor-the-task-dispatcher-list.md` — Joan `store-review-commit` @ `a0067704` on publish ref.

**Note:** `AGENTS.md` not present in `astral-radia` worktree; review followed `review-astral` skill + `ASTRAL_CODE_RULES.md`.

#### betty — 2026-06-03T14:41:33.416Z
## QA test manifest (AST-568)

**Publish ref:** `origin/sub/AST-567/AST-568-scheduled-actions-phase-sections` @ `a2298032`

**`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref:** `24d6819ebd6c9efd27f21c6aa9a89d61eebc32ff`

### Run (required)

1. **`tests/component/frontend/pages/test_AdminScheduledActions.test.tsx`** — full file (13 tests): page title **Scheduled Actions**, phase **`CollapsiblePanel`** sections (zero expanded, expand/collapse, filter within section), row edit/run/stop/AUTO/modals, thread polling reload, empty state.

### Regression (same pass if time permits)

2. **§7.13h** — `tests/component/frontend/components/test_CollapsiblePanel.test.tsx` (primitive unchanged; Scheduled Actions reuses pattern).
3. **§7.13k** — Scheduled Actions routed page minimum (covered by item 1).

### Narrowed command

```bash
cd src/ui/frontend && npx vitest run ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx
```

### Notes

- Plan Stage 4 test updates landed via **`test(AST-568):`** @ `126b97a1` and bible **§7.13zy** @ `a2298032`.
- **`task_keys`** mocks use **`phase`** / **`seq`** (no **`group`**). Expand a phase section before table row assertions (collapsed panels hide tbody from a11y tree).

#### katherine — 2026-06-03T14:31:17.568Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-567/AST-568-scheduled-actions-phase-sections/docs/features/interface/ast-568-phase-grouped-scheduled-actions-list-and-nav-labels-refactor-the-task-dispatcher-list.md

**Self-assessment**
- **Scope:** Single-Component — one admin page, NAV_CONFIG label, small `task_keys` API metadata, existing Vitest file.
- **Conf:** high — mirrors `AdminTaskPrompts.tsx` phase/`CollapsiblePanel` pattern; adds `phase`/`seq` to `_dispatch_task_key_form_meta` from `TASK_CONFIG` (replaces unused client-side `group` sort).
- **Risk:** Medium — operational run/stop screen; sectioned layout must preserve filters, modals, and thread polling.

Four stages: (1) API `phase`/`seq` on task_keys, (2) nav label, (3) phased `CollapsiblePanel` UI + title, (4) test updates including collapse/expand case.

---

# Phase-grouped Scheduled Actions list and nav labels (Refactor the Task Dispatcher List)

**Linear:** [AST-568](https://linear.app/astralcareermatch/issue/AST-568/phase-grouped-scheduled-actions-list-and-nav-labels-refactor-the-task)  
**Parent:** [AST-567](https://linear.app/astralcareermatch/issue/AST-567/refactor-the-task-dispatcher-list)  
**Publish ref:** `sub/AST-567/AST-568-scheduled-actions-phase-sections`

Susan asked for the Scheduled Actions admin screen to match Manage Tasks: collapsible phase sections, rows ordered by catalog **seq** within each phase, and user-visible naming **Scheduled Actions** (sidebar + page title) while keeping route `/admin/scheduled_actions` and all existing row/modal behavior.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Add `phase` and `seq` to `/dispatch_tasks/task_keys` payload from `TASK_CONFIG` | ui |
| `src/utils/config.py` | `NAV_CONFIG` label `Task Dispatcher` → `Scheduled Actions` | utils |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Phase sections via `CollapsiblePanel`, title/label text, grouping/sort using `phase`/`seq` | ui |
| `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` | Title expectations, phase-section mocks, collapse/section tests | tests |

## Stage 1: Expose catalog `phase` and `seq` on task_keys API

**Done when:** `GET /api/admin/dispatch_tasks/task_keys` returns `phase` (string or null) and `seq` (number or null) for every key in the response map, sourced from `TASK_CONFIG` the same way Manage Tasks uses catalog metadata; existing keys `entity_type`, `trigger_state`, `is_scored` unchanged.

1. In `src/ui/api/api_admin.py`, update `_dispatch_task_key_form_meta(task_key: str) -> dict` so the returned dict includes:
   - `"phase": cfg.get("phase")` where `cfg = TASK_CONFIG.get(task_key) or {}`
   - `"seq": cfg.get("seq")` from the same `cfg`
   Keep existing `entity_type`, `trigger_state`, `is_scored` logic unchanged (including `DISPATCH_SCHEDULABLE_TASK_KEYS` / `dispatch_task_admin_defaults` branch).
2. In the `dispatch_task_keys()` loop for `list_dispatch_tasks()` rows where `k not in seen`, when building the fallback dict for unknown keys (lines ~600–604), set `"phase": None` and `"seq": None` in addition to existing fields (do not invent phase text server-side for unknown keys).
3. Do not change `GET /api/admin/dispatch_tasks` list payload, scheduler routes, or DB schema.

⚠️ **Decision:** Use string **phase** labels from `TASK_CONFIG` (e.g. `"A. Candidate Context"`), not numeric **group**. The current UI sorts on `group` but the API never returned `group`; this ticket aligns Scheduled Actions with Manage Tasks’ `phase` + `seq` fields.

## Stage 2: Navigation label — Scheduled Actions

**Done when:** Admin sidebar shows **Scheduled Actions** linking to `/admin/scheduled_actions` (path unchanged).

1. In `src/utils/config.py`, inside `NAV_CONFIG`, find the admin item with `"path": "/admin/scheduled_actions"` and change `"label": "Task Dispatcher"` to `"label": "Scheduled Actions"`.
2. Do not change `path`, route registration in `src/ui/frontend/src/routes.tsx`, or any other nav items.

## Stage 3: Phase-grouped UI with CollapsiblePanel

**Done when:** With filtered dispatch rows spanning two phases, the page shows collapsible phase sections (Manage Tasks pattern), each containing the same table columns and interactions as today; page title reads **Scheduled Actions**; zero sections may be expanded; empty phases after filters are omitted.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, add:
   ```ts
   import CollapsiblePanel from "../components/CollapsiblePanel"
   ```
2. Update the `allTaskKeys` state type to:
   ```ts
   Record<string, { entity_type: string; trigger_state: string; phase: string | null; seq: number | null; is_scored?: boolean }>
   ```
   Remove `group` from the type and from all usages.
3. Add phase panel state matching `AdminTaskPrompts.tsx`:
   - `const [openPhase, setOpenPhase] = useState<string | null>(null)`
   - `const resolvedOpenPhase` `useMemo`: if `sections.length === 0` → `null`; if `openPhase != null` and a section exists with that phase → `openPhase`; else `null` (allows zero expanded).
4. Replace the single flat `rows` `useMemo` with two memos:
   - **`filteredRows`:** Same filters as today: `selectedId` → `candidate_id` match; `taskKeyFilter` → `task_key` match. No sort yet.
   - **`sections`:** From `filteredRows`, bucket by `const p = allTaskKeys[row.task_key]?.phase || "(unassigned)"`. Build `Object.entries(byPhase).sort(([a],[b]) => a.localeCompare(b)).map(([phase, rows]) => ({ phase, rows: sortRowsWithinSection(rows) }))` where `sortRowsWithinSection` applies the sort rules in step 5. **Omit** sections where `rows.length === 0` (should not occur if bucketing filtered rows only).
5. **`sortRowsWithinSection(rows: DispatchTask[])`** — copy existing comparator from current `rows` `useMemo` but:
   - When `sortCol === "_default"`: compare `(allTaskKeys[a.task_key]?.seq ?? 999)` vs `(allTaskKeys[b.task_key]?.seq ?? 999)` ascending/descending per `sortDir`; tie-breaker `a.task_key.localeCompare(b.task_key)` then `a.id - b.id`.
   - For any other `sortCol`, keep the existing null-safe field comparison (lines ~129–136 in current file).
   - Remove all `group` references.
6. Change `<h1 className="list-page-title">Task Dispatcher</h1>` to `Scheduled Actions`.
7. Replace the single-table render branch (`loading` / empty / one `list-page-table-wrap`) with:
   - `loading` → existing `Loading…` status.
   - `sections.length === 0` → existing copy `No dispatch tasks configured` (same as today when no rows after filter).
   - Else `sections.map(sec => (...))` each wrapped in `<div key={sec.phase} style={{ marginBottom: 12 }}>` containing:
     ```tsx
     <CollapsiblePanel
       label={<>{sec.phase} ({sec.rows.length})</>}
       expanded={resolvedOpenPhase === sec.phase}
       onExpandedChange={next => { if (next) setOpenPhase(sec.phase); else setOpenPhase(null) }}
     >
       {/* table markup */}
     </CollapsiblePanel>
     ```
8. Move the existing `<table className="list-page-table">` … `</table>` (thead + tbody mapping `sec.rows`, not global `rows`) inside each `CollapsiblePanel` body. Do not change column headers, cell renderers, `toggleSort`, Run/Stop/AUTO/Dbg handlers, or row `onClick` → `openEdit`.
9. Keep **above** the section list unchanged: `list-page-header` (title + Stop All + Add Task), `admin-filters` Task select, modals (`showStopAll`, `showModal`), thread polling, and `loadData` / API URLs.
10. Do not add new CSS files; rely on existing `.collapsible-panel` rules from `App.css` (already used by Manage Tasks).

⚠️ **Decision:** One table per phase section (duplicate thead per section), matching `AdminTaskPrompts.tsx` — not one shared thead across sections.

⚠️ **Decision:** Column-header sort applies **within each section** only (sort the section’s `rows` array via shared `sortCol`/`sortDir` state). Cross-phase global reorder is not required by AST-567.

## Stage 4: Component tests

**Done when:** `npm run test` (or project Vitest command for `test_AdminScheduledActions.test.tsx`) passes with updated title and section behavior covered.

1. In `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx`, replace every `screen.getByText("Task Dispatcher")` / `expect(... "Task Dispatcher")` with `"Scheduled Actions"`.
2. Update `taskKeysConfig` and `keysDefault` mock objects: remove `group`; add `phase` and `seq` (e.g. `scan_jobs: { ..., phase: "D. Job Analysis", seq: 2 }`, `watch_cos: { ..., phase: "C. Company Roster", seq: 1 }`).
3. Add one test **"groups rows into phase sections and allows zero expanded"**:
   - `mockApi` with `tasks: [dispatchTask, sparseRow]` and `taskKeysPayload: taskKeysConfig` (two distinct phases).
   - After load, `expect(screen.getByText(/D\. Job Analysis \(1\)/)).toBeInTheDocument()` and `expect(screen.getByText(/C\. Company Roster \(1\)/)).toBeInTheDocument()`.
   - Assert both phase tables are in the document but row text is **not** visible until expand: query `scan_jobs` / `watch_cos` with `queryByText` → not in document while collapsed.
   - Click chevron or section header for one phase (same interaction as Manage Tasks tests if present; otherwise `getByRole("button", { name: /Expand section/i })` on the first panel).
   - After expand, `getByText("scan_jobs")` (or the row for that phase) is visible.
   - Collapse again; row hidden.
4. In **"sorts columns, filters task key"**, after filter to `scan_jobs`, expect only the section for that task’s phase remains (or single section with one row); do not assert global table row order across phases.
5. Do not add Playwright or new test files beyond this existing spec.

## Self-Assessment

**Scope:** `Single-Component` — Touches one admin page, one nav config entry, one admin API helper, and its existing Vitest file; no dispatcher core or schema changes.

**Conf:** `high` — Manage Tasks already implements phase grouping, `CollapsiblePanel`, and `TASK_CONFIG` phase/seq; this plan mirrors that file’s patterns with explicit line-level steps.

**Risk:** `Medium` — Scheduled Actions is operationally critical (run/stop/AUTO); layout change must not regress modals, polling, or filters; tests gate title and section behavior.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `CollapsiblePanel` and Manage Tasks section logic locally; no new shared package required per AST-567 boundaries. |
| §2.1 config | `phase`/`seq` read from `TASK_CONFIG` in API; nav label in `NAV_CONFIG`. |
| §3.3 imports | Frontend imports only `components/CollapsiblePanel`; API imports existing config symbols. |
| §3.5 naming | Page stays `AdminScheduledActions.tsx` in `pages/`; no new subfolders. |
| §1.5 logging | No new backend debug logging (frontend-only epic per parent). |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Built:** `origin/sub/AST-567/AST-568-scheduled-actions-phase-sections` @ `d92261e7` (product: phase/seq on task_keys API, nav **Scheduled Actions**, `CollapsiblePanel` phase sections on `AdminScheduledActions.tsx`).

**Out of build scope (Betty / qa-astral):** Plan Stage 4 component test updates per `build-astral` test-tree ban.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-567/AST-568-scheduled-actions-phase-sections` @ `a2298032` (6 files: `api_admin.py`, `config.py` NAV_CONFIG, `AdminScheduledActions.tsx`, Vitest, plan doc, bible §7.13zy).

### What's solid

- **Plan fidelity:** Stages 1–4 delivered — `task_keys` exposes `phase`/`seq` from `TASK_CONFIG` (unknown/orphan keys get `null` → UI `(unassigned)`); nav label and page title **Scheduled Actions**; phase buckets + `CollapsiblePanel` mirror `AdminTaskPrompts.tsx` (`openPhase` / `resolvedOpenPhase`, zero expanded OK); default sort is `seq` then `task_key` then `id` within section; filters/modals/polling/table cells unchanged.
- **§2.1 / §3:** Catalog metadata from config; no dispatcher/schema edits.
- **§3.3 / imports:** Frontend adds only `CollapsiblePanel`; API uses existing `TASK_CONFIG` import path.
- **Tests:** Title + phase collapse/expand + filter-within-section covered; `expandFirstPhaseSection` helper keeps row-level tests valid with collapsed-by-default panels.

### Issues

| Severity | Item | Location |
| --- | --- | --- |
| — | No **fix-now** or **discuss** items on this pass. | — |

### Recommended actions

| Action | Owner | Notes |
| --- | --- | --- |
| Proceed to **resolve-astral** (happy path) | Katherine | No doc cherry-pick required unless you want the Radia review section in local notes; product SHA on publish ref is sufficient for merge. |
| Optional follow-up | Betty | Dedicated `test_api_admin` assertion that `task_keys["scan_jobs"]` includes `phase`/`seq` (page mocks already gate AST-568). |

## Resolution (2026-06-03)

**Engineer:** Katherine · **Review ref:** `origin/sub/AST-567/AST-568-scheduled-actions-phase-sections` @ `a2298032` (product) · Radia doc @ `c1716843`

**Changes vs Radia review:** None required — **fix-now** and **discuss** were empty on this pass. Merged publish ref on `dev-kath` (including Radia **Review** section); no additional product edits.

**Advisory:** Optional `test_api_admin` `task_keys` phase/seq assertion deferred to Betty (Vitest + bible §7.13zy already cover AST-568).

**Merge readiness:** §9a dry-run clean vs `origin/dev` and `origin/ftr/ast-567` before **User Testing**.
