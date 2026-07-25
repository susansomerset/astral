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

**Scope:** Delete standalone-table I/O (`add_agent_response_entry`, `list_agent_responses`, `_derive_agent_status`, candidate cascade `DELETE FROM agent_responses`). Keep `_ensure_agent_responses_schema` + entity `append_agent_response` for siblings.

| Area | Source | Component tests |
| --- | --- | --- |
| Helpers removed; ensure + append kept | `src/data/database.py` | `TestAst981StandaloneTableIoRetired::test_add_and_list_helpers_removed` |
| `hard_delete_candidate` counts omit table key | same | `TestAst981StandaloneTableIoRetired::test_hard_delete_candidate_skips_standalone_table_key` |
| Entity latest-only upsert (keep) | same | `TestAst726AppendAgentResponseUpsert` (existing) |

**Obsolete removed:** `TestAddAgentResponseEntry` (table insert/list).

