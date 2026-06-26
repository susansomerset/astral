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
