# Bootstrap

**Test module:** `tests/component/core/test_bootstrap.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/bootstrap.py` | `tests/component/core/test_bootstrap.py` | no |

---

### AST-782 · AST-756

**Repo-owned admin JSON:** `bootstrap_runtime()` calls `apply_repo_admin_json_at_startup()` after `_validate_runtime_coupling()` and before `sync_agent_tasks`. Core module loads `data/admin/*.json`, data layer applies repo-wins upsert.

| Area | Source | Component tests |
| --- | --- | --- |
| Bootstrap ordering | `src/core/bootstrap.py` | `tests/component/core/test_bootstrap.py::TestBootstrapRuntime::test_runs_validation_sync_and_scheduler_in_order` |
| File load / export / startup orchestration | `src/core/repo_admin_json.py` | `tests/component/core/test_repo_admin_json.py` (full file) |
| Config paths + apply order | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst782RepoAdminJsonConfig` |
| Agent repo upsert + export | `src/data/database.py` | `tests/component/data/database/test_agents.py::TestAst782AgentRepoJsonStartup` |
| Agent_task repo upsert + export | `src/data/database.py` | `tests/component/data/database/test_agent_tasks.py::TestAst782AgentTaskRepoJsonStartup` |

**Broken / obsolete (this pass):** `TestBootstrapRuntime` call-order assertion — must include `apply_repo_admin_json_at_startup` between validation and `sync_agent_tasks`.

**AST-782** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_bootstrap.py \
  tests/component/core/test_repo_admin_json.py \
  tests/component/utils/test_config.py::TestAst782RepoAdminJsonConfig \
  tests/component/data/database/test_agents.py::TestAst782AgentRepoJsonStartup \
  tests/component/data/database/test_agent_tasks.py::TestAst782AgentTaskRepoJsonStartup \
  -q
```

See also **`docs/test-bible/ui/server.md`** (**AST-654** pipeline row — bootstrap entry point unchanged; ordering extended by AST-782).
