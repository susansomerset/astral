# Agent Responses

**Test module:** `tests/component/data/database/test_agent_responses.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-726 (parent AST-717)

**Scope:** `append_agent_response` upserts entity-row refs by `task_key` (latest wins); full run history stays in `agent_data`.

| Area | Source | Component tests |
| --- | --- | --- |
| Upsert by `task_key`; preserve unrelated keys | `src/data/database.py` (`append_agent_response`) | `tests/component/data/database/test_agent_responses.py::TestAst726AppendAgentResponseUpsert` |
| Missing `task_key` raises | same | `TestAst726AppendAgentResponseUpsert::test_rejects_missing_task_key` |

**AST-726** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_responses.py::TestAst726AppendAgentResponseUpsert \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-981 · AST-975

**Scope:** Delete standalone-table I/O (`add_agent_response_entry`, `list_agent_responses`, `_derive_agent_status`, candidate cascade `DELETE FROM agent_responses`). Entity `append_agent_response` kept for siblings; schema ensure retired by **AST-982**.

| Area | Source | Component tests |
| --- | --- | --- |
| Helpers removed; append kept | `src/data/database.py` | `TestAst981StandaloneTableIoRetired::test_add_and_list_helpers_removed` |
| `hard_delete_candidate` counts omit table key | same | `TestAst981StandaloneTableIoRetired::test_hard_delete_candidate_skips_standalone_table_key` |
| Entity latest-only upsert (keep) | same | `TestAst726AppendAgentResponseUpsert` (existing) |

**Obsolete removed:** `TestAddAgentResponseEntry` (table insert/list).

### AST-982 · AST-975

**Scope:** Remove `_ensure_agent_responses_schema` / upsert-registry `"agent_responses"` / header inventory; add `_apply_agent_responses_table_sunset` (`DROP TABLE IF EXISTS`) from `ensure_all_upsert_registry_schemas_at_startup`. Entity JSON columns unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Ensure/registry symbols gone; sunset helper present | `src/data/database.py` | `TestAst982StandaloneTableSunset::test_ensure_and_registry_symbols_removed` |
| Bootstrap drops legacy table; no recreate; entity column remains | same | `TestAst982StandaloneTableSunset::test_bootstrap_drops_legacy_table_and_does_not_recreate` |
| Entity latest-only upsert (keep) | same | `TestAst726AppendAgentResponseUpsert` |

**Obsolete revised:** AST-981 ensure-kept assertion; conftest `_SCHEMA_FLAGS` use `_agent_responses_table_sunset_applied`.

**AST-982** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_responses.py::TestAst981StandaloneTableIoRetired \
  tests/component/data/database/test_agent_responses.py::TestAst982StandaloneTableSunset \
  tests/component/data/database/test_agent_responses.py::TestAst726AppendAgentResponseUpsert \
  -q
```
