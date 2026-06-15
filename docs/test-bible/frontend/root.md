# App and routes

**Test tree:** `tests/component/root/`

## Coverage map

Vitest tests live under **`tests/component/frontend/`** (mirror `components/`, `pages/`, `contexts/`, `lib/`, and higher-level **`test_App`** / **`test_routes`** as needed).

There is **no** per-source-file branch-lock table (**§6b**). Prefer adding or extending tests beside the modules they guard. Coverage artifacts land in **`tests/.coverage/frontend/`** when `./scripts/testing/run_component_tests.sh` runs the Vitest **coverage** target.

---

### AST-649 · AST-648

Retire candidate **Board Searches** nav/route/page and hide **`gaze_board`** from Admin Scheduled Actions APIs (**`ADMIN_CONFIG.hidden_dispatch_task_keys`** + **`admin_hidden_dispatch_task_keys()`**). Backend board tables, **`/api/boards`**, **`DISPATCH_SCHEDULABLE_TASK_KEYS`**, and core dispatch unchanged (**§7.13q**).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-649** | Drop **`NAV_CONFIG`** Board Searches item; delete **`CandidateBoardSearches.tsx`** + route; filter **`gaze_board`** from **`GET /api/admin/dispatch_tasks`**, **`/task_keys`**, **`/scheduler/thread_status`** | `src/utils/config.py`, `src/ui/frontend/src/routes.tsx`, `src/ui/api/api_admin.py` | `tests/component/frontend/test_routes.test.tsx` — **`candidate/board_searches`** route absent; `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_omits_board_searches`; `tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_ast649_hides_gaze_board_from_scheduled_actions`; **delete** `tests/component/frontend/pages/test_CandidateBoardSearches.test.tsx` |

**AST-649** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_omits_board_searches \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_ast649_hides_gaze_board_from_scheduled_actions

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/test_routes.test.tsx
```
