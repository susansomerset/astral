# Agent Responses (entity JSON column)

**Test module:** `tests/component/data/database/test_agent_responses.py`

**Scope:** Entity-row `agent_responses` JSON columns on company / job / candidate (`append_agent_response` latest-only upsert into `agent_data` refs). The standalone `agent_responses` **table** is **retired** (AST-975 / AST-981 / AST-982). Column retirement is sibling **AST-984**.

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

### AST-983 · AST-975

**Scope:** Docs/bible honesty — mandate + config already split table(retired) vs column(live) by engineer `code(AST-983)`. Bible intro/cross-links match; no new pytest (AST-981/982 already retired table I/O mocks and sunset coverage).

| Area | Source | Verification |
| --- | --- | --- |
| Code Rules + config comment split | `docs/ASTRAL_CODE_RULES.md`, `src/utils/config.py` | `rg -n 'agent_responses' docs/ASTRAL_CODE_RULES.md src/utils/config.py` — every hit column-scoped or table marked retired |
| Bible entity-column scope | this file | Intro + AST-726/981/982 blocks |
| Roster / backfill cross-links | `docs/test-bible/core/roster.md`, `docs/test-bible/dev/backfill_latest_only_rubric_entity_data.md` | Entity-row wording only |
| Table I/O tests already retired | `tests/component/core/test_agent.py`, `tests/component/data/database/test_agent_responses.py` | Reuse AST-981/982 classes below |

**AST-983** narrowed run (reuse + docs gate):

```bash
rg -n 'agent_responses' docs/ASTRAL_CODE_RULES.md src/utils/config.py
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_responses.py::TestAst981StandaloneTableIoRetired \
  tests/component/data/database/test_agent_responses.py::TestAst982StandaloneTableSunset \
  tests/component/data/database/test_agent_responses.py::TestAst726AppendAgentResponseUpsert \
  tests/component/core/test_agent.py::TestAst981StandaloneTableAuditRetired \
  -q
```
