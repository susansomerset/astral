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
