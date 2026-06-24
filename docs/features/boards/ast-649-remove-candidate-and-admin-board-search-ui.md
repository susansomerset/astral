<!-- linear-archive: AST-649 archived 2026-06-23 -->

## Linear archive (AST-649)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-649/remove-candidate-and-admin-board-search-ui-remove-board-searches-and  
**Status at archive:** Done  
**Project:** Astral Boards  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-648 — Remove "Board Searches" and related references  
**Blocked by / blocks / related:** parent: AST-648

### Description

## What this implements

Remove all user-visible board-search product surfaces while leaving backend board infrastructure dormant: drop **Board Searches** from candidate navigation, remove the board-searches management route/page, and hide `gaze_board` from Admin Scheduled Actions (Susan: do not keep admin board dispatch exposed). Retire any remaining frontend copy that still presents board searches as a candidate feature after nav/route removal.

## Acceptance criteria

1. With a logged-in user and any eligible candidate selected, the sidebar **does not** show **Board Searches**.
2. Navigating to the former board-searches URL **does not** render the Board Searches management UI (no list, no create/edit modal, no board picker).
3. All other candidate, company, artifacts, and admin pages load and behave as before this change.
4. Component test suite passes after board-search UI tests are updated or removed to match the new product surface.

## Boundaries

* Does **not** drop `board_search` tables, remove `/api/boards` routes, delete `BOARD_CONFIG`, disable backend `gaze_board` dispatch, or change ingest/tracker behavior.
* Does **not** migrate or delete existing board search data.
* Does **not** change company-centric ingest, roster, consult, or artifacts flows.

## Notes for planning

* Navigation visibility is config-driven via `NAV_CONFIG` / `/api/nav_config` — remove the nav item there, not via hard-coded sidebar exceptions.
* Admin Scheduled Actions: hide `gaze_board` from the UI per parent open-question resolution (Susan: No).
* Bookmarked `/candidate/board_searches`: generic not-found is acceptable (Susan: redirect not necessary).

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/ast-648-remove-board-searches-and-related-references`, child `sub/AST-648/<child-segment>`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-14T22:38:05.608Z
**Review** (`origin/dev...origin/sub/AST-648/ast-649-remove-candidate-and-admin-board-search-ui`)

Plan doc: [ast-649-remove-candidate-and-admin-board-search-ui.md](https://github.com/susansomerset/astral/blob/sub/AST-648/ast-649-remove-candidate-and-admin-board-search-ui/docs/features/boards/ast-649-remove-candidate-and-admin-board-search-ui.md) (doc commit `6b870da1`)

### fix-now
None.

### discuss
None.

### What's solid
- **Plan fidelity:** `NAV_CONFIG` Board Searches removed; `routes.tsx` route + import gone; `CandidateBoardSearches.tsx` deleted; `App.css` section comments removed; `ADMIN_CONFIG.hidden_dispatch_task_keys` + `admin_hidden_dispatch_task_keys()` filter `list_dtasks`, `dispatch_task_keys`, and `scheduler_thread_status`.
- **AC:** No nav item; no board-searches route; admin Scheduled Actions omit `gaze_board`; backend `/api/boards`, core board modules, and `DISPATCH_SCHEDULABLE_TASK_KEYS` unchanged.
- **§2.1 / §1.3 / §3.3:** Config-driven nav + admin hide; DRY helper; no new layer violations.
- **Frontend sweep:** No remaining `board_searches` / `Board Searches` / `gaze_board` under `src/ui/frontend`.

### Advisory
- Branch tip includes Betty test/bible work plus incidental drift fixes (`test_boards.py`, `test_roster.py`, `contemplate_job` assertion) — qa-child scope, not product defects.
- `gaze_board` still exists in backend config; raw API POST could create a row — intentional UI-only hide per plan boundaries.

**→ Katherine:** proceed to `resolve-child` (no product changes required).

#### betty — 2026-06-14T22:29:15.052Z
[check-linear] Cleared `[qa-handoff]` — full component pytest green (1512 passed). Fixed 15 unrelated test-tree failures on `origin/tests`:

- **AST-595:** `test_api_admin` task_keys `contemplate_job.trigger_state` → `cfg.resume_artifact_compound_state("contemplate_job")`
- **AST-459:** `test_boards` deeplink gaze uses stored URL; blank deeplink raises
- **Roster:** `claim_company_batch` expects `states=None` kwarg
- **AST-458 REST:** boards integration uses `test-token` + Stytch auth stub (was 401)

**Publish ref:** `origin/sub/AST-648/ast-649-remove-candidate-and-admin-board-search-ui` @ `51da72b4` (`merge-tests(AST-649): origin/tests cca9f901`)

Narrow manifest unchanged (§7.13zzu). Assignee → Katherine for `test-child`.

#### katherine — 2026-06-14T22:25:29.321Z
[qa-handoff]

@Betty White — narrow manifest **green**; full harness gate **red** with failures **unrelated** to AST-649 product (UI removal + `gaze_board` admin filter).

**Git:** `origin/sub/AST-648/ast-649-remove-candidate-and-admin-board-search-ui` @ `b9f654e0` merged on epic worktree.

### Narrow manifest (all pass)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_omits_board_searches \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_ast649_hides_gaze_board_from_scheduled_actions \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls
# 3 passed

cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/test_routes.test.tsx
# 2 passed
```

### Full `./scripts/testing/run_component_tests.sh` — 15 failed (not AST-649 product)

| Area | Tests | Why not product fix here |
|------|-------|--------------------------|
| Board gaze (§7.13q spine) | `test_boards.py::TestRunBoardSearchGazeAst459` (2) | Deeplink URL assertion stale vs current `run_board_search_gaze`; backend unchanged by AST-649 |
| Board REST (§7.13q) | `test_board_search_integration.py::TestBoardSearchRestAst458` (10) | Mostly **401** on POST/PATCH — auth/harness, not nav/UI removal; `/api/boards` untouched |
| Admin task_keys (pre-existing) | `test_api_admin.py::TestApiAdminBranchGaps::test_dispatch_task_keys_includes_task_config_registry`, `test_ast549_task_keys_config_derivation_authoritative` | Expect `BUILD_ARTIFACTS`; product correctly returns `BUILD_ARTIFACTS.contemplate_job` (AST-595 compound states) — unrelated to `hidden_dispatch_task_keys` |
| Roster | `test_roster.py::TestBatchApi::test_get_new_company_batch_claims_and_returns_rows` | Unrelated batch API |

AST-649-specific tests (`test_nav_config_omits_board_searches`, `test_ast649_hides_gaze_board_from_scheduled_actions`, routes, scheduler controls) all pass.

**Ask:** For this UI-only ticket, either (a) scope harness gate to the narrow manifest above, or (b) update/skip the unrelated failing tests on publish ref so full suite is green. Reassign me when ready.

#### betty — 2026-06-14T22:23:57.639Z
## QA test manifest (AST-649)

**Publish ref:** `origin/sub/AST-648/ast-649-remove-candidate-and-admin-board-search-ui` @ `b9f654e0` (`merge-tests(AST-649): origin/tests da8406f3`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `d5319a92fddc50ff8ba575c285c8325db15c1eb14e93c219e87631c2bd38d5a0` — see §7.13zzu

### 1. Existing coverage (bible-backed — backend unchanged)

- **§7.13q** board_search REST/DDL/dispatch spine — **no rerun required** for this UI-only ticket unless `test-child` full suite flags regressions unrelated to removed UI.

### 2. Broken / obsolete tests (revised this pass)

- **Deleted** `tests/component/frontend/pages/test_CandidateBoardSearches.test.tsx` (page removed).
- **Updated** `tests/component/frontend/test_routes.test.tsx` — `candidate/board_searches` route **absent**.
- **Updated** `tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls` — thread_status empty dict shape (post-filter API).
- **§7.13s** bible table trimmed; cross-ref **§7.13zzu**.

### 3. New / expanded tests

1. `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_omits_board_searches` — no `/candidate/board_searches` in any nav group.
2. `tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_ast649_hides_gaze_board_from_scheduled_actions` — `gaze_board` absent from `task_keys`, list rows, and `scheduler/thread_status`.

### Run (narrowed)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_omits_board_searches \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_ast649_hides_gaze_board_from_scheduled_actions \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/test_routes.test.tsx
```

Then full `./scripts/testing/run_component_tests.sh` (zero args) for harness gate.

— Betty

#### katherine — 2026-06-14T22:19:36.339Z
Plan: [`docs/features/boards/ast-649-remove-candidate-and-admin-board-search-ui.md`](https://github.com/susansomerset/astral/blob/sub/AST-648/ast-649-remove-candidate-and-admin-board-search-ui/docs/features/boards/ast-649-remove-candidate-and-admin-board-search-ui.md) on `origin/sub/AST-648/ast-649-remove-candidate-and-admin-board-search-ui` @ `12447a33`.

Two stages: (1) remove `NAV_CONFIG` Board Searches item, delete `CandidateBoardSearches.tsx` + route + CSS comments; (2) add `ADMIN_CONFIG.hidden_dispatch_task_keys` and filter `gaze_board` from Scheduled Actions list/task_keys/thread_status APIs — backend dispatch untouched.

**Self-Assessment**
- **Scope:** `Single-Component` — UI presentation and admin API filtering only; one React page deleted.
- **Conf:** `high` — Established NAV_CONFIG / routes SYNC and ADMIN_CONFIG extension; no new business logic.
- **Risk:** `low` — Removal-only; board backend, `/api/boards`, and dispatcher paths stay dormant.

---

# Remove candidate and admin board search UI

**Linear:** [AST-649](https://linear.app/astralcareermatch/issue/AST-649/remove-candidate-and-admin-board-search-ui-remove-board-searches-and)  
**Parent:** [AST-648](https://linear.app/astralcareermatch/issue/AST-648/remove-board-searches-and-related-references)  
**Publish ref:** `sub/AST-648/ast-649-remove-candidate-and-admin-board-search-ui`

Retire all user-visible board-search product surfaces while leaving backend board infrastructure dormant: remove **Board Searches** from candidate navigation, delete the board-searches management route and page, and hide `gaze_board` from Admin Scheduled Actions. Bookmarked `/candidate/board_searches` may fall through to the existing catch-all redirect (`/jobs/recommended`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Remove Board Searches nav item; add `hidden_dispatch_task_keys` to `ADMIN_CONFIG` + helper | utils |
| `src/ui/frontend/src/routes.tsx` | Remove board-searches route and import | ui |
| `src/ui/frontend/src/pages/CandidateBoardSearches.tsx` | Delete file | ui |
| `src/ui/frontend/src/App.css` | Remove Board Searches section comments from TOC and stylesheet | ui |
| `src/ui/api/api_admin.py` | Filter hidden dispatch task keys from Scheduled Actions APIs | ui |

**QA manifest (Betty — not engineer commits):** update or remove frontend/component tests that assert board-search UI still exists; add assertions that `gaze_board` is absent from admin Scheduled Actions task-key catalog. Engineer does **not** edit `tests/` or `docs/ASTRAL_TEST_BIBLE.md`.

| Test file | Expected Betty change |
|-----------|----------------------|
| `tests/component/frontend/test_routes.test.tsx` | Assert `candidate/board_searches` route is **not** defined |
| `tests/component/frontend/pages/test_CandidateBoardSearches.test.tsx` | **Delete** entire file |
| `tests/component/ui/api/test_api_system.py` | Add `test_nav_config_omits_board_searches`: no item with path `/candidate/board_searches` in any group |
| `tests/component/ui/api/test_api_admin.py` | Assert `gaze_board` not in `GET /api/admin/dispatch_tasks/task_keys`; if list mocks include a `gaze_board` row, assert it is filtered from `GET /api/admin/dispatch_tasks` |

**Out of scope (do not touch):** `src/ui/api/api_boards.py`, `src/core/boards.py`, `BOARD_CONFIG`, `BOARDS_CONFIG`, `DISPATCH_SCHEDULABLE_TASK_KEYS`, dispatcher/gazer/consult board paths, `tests/component/core/*` board tests, `tests/component/utils/test_config.py` gaze_board config assertions.

## Stage 1: Config-driven nav removal and page deletion

**Done when:** `NAV_CONFIG` no longer lists Board Searches; `routes.tsx` has no board-searches route; `CandidateBoardSearches.tsx` is deleted; `App.css` has no Board Searches section comments; visiting `/candidate/board_searches` does not render the management UI (catch-all redirect only).

1. In `src/utils/config.py`, in `NAV_CONFIG` Candidate group (~line 2311), **delete** the entire line:
   ```python
   {"label": "Board Searches", "path": "/candidate/board_searches"},
   ```
   Do not add hard-coded sidebar exceptions elsewhere.

2. In `src/ui/frontend/src/routes.tsx`:
   - Remove line `import BoardSearches from "./pages/CandidateBoardSearches"`.
   - Remove the route object `{ path: "candidate/board_searches", element: <BoardSearches /> },` (~line 106).
   - Keep the `// SYNC:` header comment at top — it still applies to remaining routes.

3. **Delete** `src/ui/frontend/src/pages/CandidateBoardSearches.tsx`.

4. In `src/ui/frontend/src/App.css`:
   - Remove TOC line `* 14. Board Searches (candidate)` (~line 22).
   - Remove the block at ~lines 1717–1718:
     ```css
     /* === 14. Board Searches — uses ListPage + Modal dep-* fields (CandidateBoardSearches.tsx) === */
     ```
     (No CSS rules exist under this section — comments only.)

⚠️ **Decision:** Delete the page component file rather than leaving a dead stub — route removal + catch-all `*` → `/jobs/recommended` satisfies AC #2 without a dedicated redirect.

## Stage 2: Hide `gaze_board` from Admin Scheduled Actions (UI only)

**Done when:** `ADMIN_CONFIG` declares hidden dispatch task keys; `GET /api/admin/dispatch_tasks/task_keys` omits `gaze_board`; `GET /api/admin/dispatch_tasks` omits rows whose `task_key` is `gaze_board`; `GET /api/admin/scheduler/thread_status` omits entries whose `task_key` is hidden; backend `DISPATCH_SCHEDULABLE_TASK_KEYS` and dispatcher behavior are unchanged.

1. In `src/utils/config.py`, extend `ADMIN_CONFIG` (~line 2197) to include:
   ```python
   ADMIN_CONFIG = {
       "reconciliation": {
           ...
       },
       # AST-649: omit from Scheduled Actions UI; backend dispatch unchanged.
       "hidden_dispatch_task_keys": ("gaze_board",),
   }
   ```

2. In `src/utils/config.py`, immediately after the `ADMIN_CONFIG` block, add:
   ```python
   def admin_hidden_dispatch_task_keys() -> frozenset:
       """task_key values hidden from Scheduled Actions admin UI (dispatch backend unchanged)."""
       raw = ADMIN_CONFIG.get("hidden_dispatch_task_keys") or ()
       return frozenset(raw)
   ```

3. In `src/ui/api/api_admin.py`, add `admin_hidden_dispatch_task_keys` to the existing import from `src.utils.config` (same import line as `ADMIN_CONFIG`, `DISPATCH_SCHEDULABLE_TASK_KEYS`, etc.).

4. In `dispatch_task_keys()` (~line 643), after building `seen`, filter before return:
   ```python
   hidden = admin_hidden_dispatch_task_keys()
   for tk in hidden:
       seen.pop(tk, None)
   return jsonify(seen)
   ```

5. In `list_dtasks()` (~line 602), after enriching rows and before the `req_dict` branch:
   ```python
   hidden = admin_hidden_dispatch_task_keys()
   rows = [r for r in rows if r.get("task_key") not in hidden]
   ```

6. In `scheduler_thread_status()` (~line 1215), filter the payload from `task_status_all()`:
   ```python
   hidden = admin_hidden_dispatch_task_keys()
   status = task_status_all()
   filtered = {k: v for k, v in status.items() if v.get("task_key") not in hidden}
   return jsonify(filtered)
   ```
   (If `task_status_all()` returns a list, filter list items by `task_key` instead — match the actual return shape in code before editing.)

⚠️ **Decision:** Hide via `ADMIN_CONFIG` + API filtering, not by removing `gaze_board` from `DISPATCH_SCHEDULABLE_TASK_KEYS` — preserves dormant backend dispatch per epic boundaries.

## Self-Assessment

**Scope:** `Single-Component` — UI and admin API presentation only (`config.py` nav + admin filter, one deleted React page, routes, CSS comments).

**Conf:** `high` — Straightforward removal following established `NAV_CONFIG` / `routes.tsx` SYNC pattern and `ADMIN_CONFIG` extension; no new business logic.

**Risk:** `low` — Deleting unreachable UI; backend board tables, `/api/boards`, and dispatcher paths stay intact; worst case is a missed frontend string (Betty tests catch nav/route regressions).

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §2.1 Config as source of truth | Nav removal via `NAV_CONFIG` only; admin hide list in `ADMIN_CONFIG` — no hard-coded sidebar or task-key exceptions in React. |
| §1.3 DRY | Reuses single `admin_hidden_dispatch_task_keys()` helper for three admin endpoints. |
| §3.3 Imports | `api_admin.py` imports config helper only; no new cross-layer violations. |
| §2.4 / §2.6 | No batch or state-machine changes. |
| Boundaries | No backend rip-out; `api_boards.py` and core board modules untouched. |

No conflicts — plan is implementable as written.

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-648/ast-649-remove-candidate-and-admin-board-search-ui`  
**Product commits:** `5cbafff0` (nav/route/page removal), `2478ca22` (hide gaze_board from admin Scheduled Actions)

## Review

**Diff:** `origin/dev...origin/sub/AST-648/ast-649-remove-candidate-and-admin-board-search-ui` (51da72b4 tip includes Betty test merges; product commits `5cbafff0`, `2478ca22`).

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stage 1 + 2 match plan: `NAV_CONFIG` item removed, route/import/page deleted, `App.css` TOC comment removed, `ADMIN_CONFIG.hidden_dispatch_task_keys` + `admin_hidden_dispatch_task_keys()` wired into `list_dtasks`, `dispatch_task_keys`, `scheduler_thread_status`. |
| Acceptance criteria | No sidebar Board Searches; no `candidate/board_searches` route; admin Scheduled Actions APIs omit `gaze_board`; backend `/api/boards`, `DISPATCH_SCHEDULABLE_TASK_KEYS`, core board modules untouched. |
| §2.1 Config | Nav and admin hide list are config-driven — no hard-coded React or API task-key exceptions. |
| §1.3 DRY | Single helper reused across three admin endpoints. |
| §3.3 Layers | `api_admin.py` imports config helper only; no new cross-layer violations. |
| Frontend sweep | No remaining `board_searches`, `Board Searches`, or `gaze_board` strings under `src/ui/frontend`. |
| Self-assessment | Scope/risk labels match the diff footprint (Single-Component UI + admin presentation). |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | No **fix-now** or **discuss** items. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None — proceed to `resolve-child` (no product changes required). | Katherine |

### Advisory

- Branch tip includes Betty **`tests/`** + bible updates and incidental drift fixes (`test_boards.py` AST-459 deeplink alignment, `test_roster.py` `states=None`, `contemplate_job` trigger_state assertion) — expected qa-child scope, not AST-649 product defects.
- `gaze_board` remains schedulable in backend config and could still be created via raw API POST; plan explicitly chose UI-only hide — intentional per epic boundaries.

## Resolution (Katherine / resolve)

**Date:** 2026-06-14  
**Review:** Radia — no fix-now, no discuss (doc `6b870da1`).

No product code changes required. Review confirmed plan fidelity and acceptance criteria on publish ref `6b870da1` (product `5cbafff0`, `2478ca22`; Betty tests `51da72b4`).

**§9a:** publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-648-remove-board-searches-and-related-references`.
