# Agent Tasks

**Test module:** `tests/component/data/database/test_agent_tasks.py`

## Coverage map

| Area | Source | Component tests |
| --- | --- | --- |
| Seven-segment versioning (**AST-454**) | `src/data/database.py` | `TestAst454SevenSegmentPersistence`, `TestSaveAgentTask` |
| Grouping metadata columns + seed (**AST-738**) | `src/data/database.py`, `scripts/migrations/backfill_task_grouping_metadata.py` | `TestAst738TaskGroupingMetadata` |

### AST-738 · AST-734

Four global-per-`task_key` columns on `agent_task`: `task_group_order`, `task_group_name`, `task_seq`, `task_name`. One-time seed copies `TASK_CONFIG` `phase`/`seq` via `backfill_task_grouping_metadata` (global guard when any `current=1` row has non-empty `task_group_name`). `save_agent_task` seeds new rows, copies grouping on segment version, and metadata-only grouping edits do not retire the row. `list_candidate_tasks` returns all four columns.

| Area | Source | Component tests |
| --- | --- | --- |
| Seed helper + backfill guard | `scripts/migrations/backfill_task_grouping_metadata.py` | `TestAst738TaskGroupingMetadata::test_seed_values_for_task_key_from_config`, `test_backfill_skips_when_operator_already_seeded` |
| Insert defaults, metadata-only update, version copy-forward, list columns | `src/data/database.py` | `TestAst738TaskGroupingMetadata` (remaining methods) |
| Manage Tasks GET/PUT + `_enrich_tasks` backward-compat `phase`/`seq` | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestAst738TaskGroupingApi`; revised `TestTaskRoutes::test_preview_task_and_get_update` |

**AST-738** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_tasks.py::TestAst738TaskGroupingMetadata \
  tests/component/ui/api/test_api_admin.py::TestAst738TaskGroupingApi \
  tests/component/ui/api/test_api_admin.py::TestTaskRoutes::test_preview_task_and_get_update \
  -q
```

**Out of scope (siblings):** React Manage Tasks / Scheduled Actions layout (**AST-739**); `TASK_CONFIG` `phase`/`seq` removal (**AST-740**).

---

### AST-782 · AST-756

**Repo-wins startup upsert for `agent_task`:** retire all `current = 1` rows, then import JSON via `apply_agent_task_copy_upsert` semantics. Keys absent from JSON remain `current = 0` only.

| Area | Source | Component tests |
| --- | --- | --- |
| Retire-all-current + import | `src/data/database.py` | `TestAst782AgentTaskRepoJsonStartup::test_startup_retires_absent_keys_and_imports_json` |
| Export current rows only | `src/data/database.py` | `TestAst782AgentTaskRepoJsonStartup::test_fetch_export_rows_only_current` |

---

### AST-786 · AST-756 (UAT bug)

**Data-only:** Replace skeleton **AST-782** `data/admin/agent_task.json` with normalized **`docs/uat-fixtures/AST-756/expected-agent_task.json`** (37 `current = 1` rows, PRAGMA column order, populated prompts/metadata). No `src/**` changes.

| Area | Source | Component tests |
| --- | --- | --- |
| Fixture/repo parity + 37-key catalog | `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json` | `tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed` |
| Startup import smoke | `src/core/repo_admin_json.py`, `src/data/database.py` | `TestAst786AgentTaskRepoJsonSeed::test_startup_apply_loads_all_37_current_rows` |

**AST-786** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  -q
```

**test-child scope gate (required):** `git show 54ceac3 --name-only` — expect **only** `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` under `code(AST-786)` (no `src/`).

---

### AST-790 · AST-756 (UAT bug)

**Product fix:** `apply_agent_task_copy_upsert` forwards **`task_group_name`**, **`task_group_order`**, **`task_name`**, **`task_seq`** from repo JSON / Copy Output rows; skip guard compares grouping so revert/startup restore metadata when prompts already match. **`src/data/database.py` only** — no repo JSON seed edits.

| Area | Source | Component tests |
| --- | --- | --- |
| Startup import grouping | `src/data/database.py` | `TestAst790AgentTaskGroupingImport::test_startup_import_forwards_grouping_metadata` |
| Grouping-only copy upsert | same | `TestAst790AgentTaskGroupingImport::test_copy_upsert_updates_grouping_when_prompts_unchanged` |
| Revert restores grouping | `src/core/repo_admin_json.py`, `src/data/database.py` | `TestAst790AgentTaskGroupingImport::test_revert_restores_grouping_when_prompts_match` |

**AST-790** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_tasks.py::TestAst790AgentTaskGroupingImport \
  -q
```

**test-child scope gate (required):** `git show cb7ec1f --name-only` — expect **only** `src/data/database.py` and `docs/features/foundation/ast-790-uat-agent-task-grouping-metadata-not-applied-on-revert-startup.md` (no `data/admin/**`).
