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
