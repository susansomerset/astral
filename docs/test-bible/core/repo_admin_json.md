# Repo Admin JSON

**Test module:** `tests/component/core/test_repo_admin_json.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/repo_admin_json.py` | `tests/component/core/test_repo_admin_json.py` | no |

---

### AST-782 · AST-756

Repo-owned **`data/admin/agent.json`** and **`data/admin/agent_task.json`**: bare Copy Output arrays loaded at startup; export writes current DB rows back to disk. Not invoked from admin save paths.

| Area | Source | Component tests |
| --- | --- | --- |
| Missing / malformed file handling | `src/core/repo_admin_json.py` | `TestLoadRepoAdminJsonFile` |
| Transactional apply order (agent → agent_task) | `src/core/repo_admin_json.py` | `TestApplyRepoAdminJsonAtStartup::test_applies_agent_then_agent_task_on_one_connection` |
| Export UTF-8 round-trip files | `src/core/repo_admin_json.py` | `TestExportRepoAdminJsonToFiles` |

Data-layer SQL: **`docs/test-bible/data/database/agents.md`** and **`agent_tasks.md`**. Bootstrap wire: **`docs/test-bible/core/bootstrap.md`**.

---

### AST-783 · AST-756

**Divergence compare + revert:** normalized export-shape compare of live DB vs checked-in repo JSON; **`revert_repo_admin_json_table`** reuses AST-782 startup apply. Admin **`GET /api/admin/repo_json/status`**, **`POST /api/admin/repo_json/revert/<table_key>`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Scalar normalization + compare/revert | `src/core/repo_admin_json.py` | `tests/component/core/test_repo_admin_json.py::TestAst783RepoAdminJsonDivergence` |
| Admin HTTP routes | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestAst783RepoJsonApi` |
| Shared banner + themed confirm | `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | `tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx` |

Routed pages: **`docs/test-bible/frontend/pages.md`** (**AST-783**).
