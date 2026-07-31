# Bootstrap

**Test module:** `tests/component/core/test_bootstrap.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/bootstrap.py` | `tests/component/core/test_bootstrap.py` | no |

---

### AST-782 · AST-756

**Repo-owned admin JSON:** `bootstrap_runtime()` calls `apply_repo_admin_json_at_startup()` after `_validate_runtime_coupling()` and before `sync_agent_tasks`. Core module loads `data/admin/*.json`, data layer applies repo-wins upsert.

**AST-843 (parent AST-842):** After repo admin JSON, `bootstrap_runtime()` calls `database.ensure_all_upsert_registry_schemas_at_startup()` — idempotent lazy schema ensure for every `_UPSERT_LAZY_SCHEMA_HANDLERS` table before `sync_agent_tasks` / scheduler.

| Area | Source | Component tests |
| --- | --- | --- |
| Bootstrap ordering | `src/core/bootstrap.py` | `tests/component/core/test_bootstrap.py::TestBootstrapRuntime::test_runs_validation_sync_and_scheduler_in_order` |
| Registry-wide startup schema ensure | `src/data/database.py` (`ensure_all_upsert_registry_schemas_at_startup`) | `tests/component/data/test_database.py::TestAst843BootstrapSchemaEnsure::test_ensure_all_upsert_registry_schemas_at_startup_idempotent` |
| File load / export / startup orchestration | `src/core/repo_admin_json.py` | `tests/component/core/test_repo_admin_json.py` (full file) |
| Config paths + apply order | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst782RepoAdminJsonConfig` |
| Agent repo upsert + export | `src/data/database.py` | `tests/component/data/database/test_agents.py::TestAst782AgentRepoJsonStartup` |
| Agent_task repo upsert + export | `src/data/database.py` | `tests/component/data/database/test_agent_tasks.py::TestAst782AgentTaskRepoJsonStartup` |

**Broken / obsolete (this pass):** `TestBootstrapRuntime` call-order assertion — must include `schema_ensure` after `repo_json` and before `sync_agent_tasks`.

**AST-843** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_bootstrap.py \
  tests/component/data/test_database.py::TestAst843BootstrapSchemaEnsure \
  -q
```

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

---

### AST-960 · AST-957

**Scope:** Drop bootstrap inventory over deleted **`DISPATCH_SCHEDULABLE_TASK_KEYS`**. `_validate_runtime_coupling` checks LLM env + `get_task_keys()` ⊆ `TASK_CONFIG` only — gap keys (`fetch_jd`, `prefilter`, …) must not force boot failure.

| Area | Source | Component tests |
| --- | --- | --- |
| Coupling without frozenset | `src/core/bootstrap.py` | `tests/component/core/test_bootstrap.py::TestValidateRuntimeCoupling` (incl. `test_passes_with_live_task_config_without_gap_key_inventory`) |
| Pipeline order unchanged | same | `::TestBootstrapRuntime::test_runs_validation_sync_and_scheduler_in_order` |

**Broken / obsolete (Betty revision this pass):**
- `test_raises_when_dispatch_key_missing_from_task_config` — deleted (inventory loop gone).
- Frozenset monkeypatches on empty/orphan/aligned cases — removed.

**AST-960** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_bootstrap.py \
  tests/component/utils/test_config.py::TestAst960DropSchedulableFrozensetInventory \
  tests/component/utils/test_config.py::TestAst955RegisteredKeyDispatchAdminDefaults \
  tests/component/utils/test_config.py::TestAst796FetchJdSchedulableCutover \
  tests/component/utils/test_config.py::TestAst702PrefilterBatchConfig \
  tests/component/utils/test_config.py::TestAst719FetchJobPagesConfig \
  tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig \
  tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig \
  tests/component/utils/test_config.py::TestAst506InflowResolveConfig \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers \
  tests/component/ui/api/test_api_admin.py::TestAst796FetchJdRetiredDispatchKeys \
  tests/component/ui/api/test_api_admin.py::TestAst960TaskKeysNoFrozensetInventory \
  tests/component/ui/api/test_api_admin.py::TestAst955AlignScheduledActionsSave \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

Config / admin bible: **`docs/test-bible/utils/config.md`** · **`docs/test-bible/ui/api/api_admin.md`** (**AST-960**).
