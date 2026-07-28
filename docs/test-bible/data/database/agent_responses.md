# Agent Responses (latest refs via agent_data.entity_id)

**Test module:** `tests/component/data/database/test_agent_responses.py`

**Scope:** Latest-per-task agent refs for company / job / candidate via `list_entity_latest_agent_refs` (`agent_data.entity_id` on RESPONSE rows). Standalone `agent_responses` **table** retired (AST-975 / AST-981 / AST-982). Entity JSON **columns** retired (**AST-984**).

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-726 (parent AST-717)

**Scope (historical):** `append_agent_response` upserted entity-row refs by `task_key` (latest wins). **Superseded by AST-984** — see `TestAst984EntityColumnRetired`.

| Area | Source | Component tests |
| --- | --- | --- |
| Upsert by `task_key`; preserve unrelated keys | `src/data/database.py` (`append_agent_response`) | `tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired` |
| Missing `task_key` raises | same | `TestAst726AppendAgentResponseUpsert::test_rejects_missing_task_key` |

**AST-726** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-981 · AST-975

**Scope:** Delete standalone-table I/O (`add_agent_response_entry`, `list_agent_responses`, `_derive_agent_status`, candidate cascade `DELETE FROM agent_responses`). Entity `append_agent_response` kept for siblings at the time; schema ensure retired by **AST-982**; columns retired by **AST-984**.

| Area | Source | Component tests |
| --- | --- | --- |
| Helpers removed (append also gone AST-984) | `src/data/database.py` | `TestAst981StandaloneTableIoRetired::test_add_and_list_helpers_removed` |
| `hard_delete_candidate` counts omit table key | same | `TestAst981StandaloneTableIoRetired::test_hard_delete_candidate_skips_standalone_table_key` |
| Entity latest-only upsert | same | retired → `TestAst984EntityColumnRetired` |

**Obsolete removed:** `TestAddAgentResponseEntry` (table insert/list).

### AST-982 · AST-975

**Scope:** Remove `_ensure_agent_responses_schema` / upsert-registry `"agent_responses"` / header inventory; add `_apply_agent_responses_table_sunset` (`DROP TABLE IF EXISTS`) from `ensure_all_upsert_registry_schemas_at_startup`. Entity JSON columns unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Ensure/registry symbols gone; sunset helper present | `src/data/database.py` | `TestAst982StandaloneTableSunset::test_ensure_and_registry_symbols_removed` |
| Bootstrap drops legacy table; no recreate; entity column dropped (AST-984) | same | `TestAst982StandaloneTableSunset::test_bootstrap_drops_legacy_table_and_does_not_recreate` |
| Entity column upsert | same | retired → `TestAst984EntityColumnRetired` |

**Obsolete revised:** AST-981 ensure-kept assertion; conftest `_SCHEMA_FLAGS` use `_agent_responses_table_sunset_applied`.

**AST-982** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_responses.py::TestAst981StandaloneTableIoRetired \
  tests/component/data/database/test_agent_responses.py::TestAst982StandaloneTableSunset \
  tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired \
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
  tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired \
  tests/component/core/test_agent.py::TestAst981StandaloneTableAuditRetired \
  -q
```

### AST-984 · AST-975

**Scope:** Drop entity `agent_responses` JSON columns; remove `append_agent_response` / roster dedupe+normalize; latest-per-task via `list_entity_latest_agent_refs` + `ensure_batch_response_entity_ids`; retire backfill CLI.

| Area | Source | Component tests |
| --- | --- | --- |
| Append gone; list + ensure + drop helpers present | `src/data/database.py` | `TestAst984EntityColumnRetired::test_append_and_column_helpers` |
| Latest-per-task from `agent_data.entity_id` | same | `TestAst984EntityColumnRetired::test_list_latest_per_task_key` |
| Ensure tags RESPONSE copies per entity | same | `TestAst984EntityColumnRetired::test_ensure_batch_response_entity_ids_tags_copies` |
| Seeded schemas lack column | same | `TestAst984EntityColumnRetired::test_seeded_entity_rows_have_no_agent_responses_column` |
| do_task tags RESPONSE `entity_id`; no append | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst984EntityColumnRetired` |
| Story / hop from list API | `src/core/roster.py`, `src/core/agent.py` | `TestEntityAgentStory*`, hop/hydrate tests in `test_agent.py` |
| Backfill CLI exit 2 | `scripts/migrations/backfill_latest_only_rubric_entity_data.py` | `tests/component/scripts/test_backfill_latest_only_rubric_entity_data.py` |

**Obsolete revised:** `TestAst726AppendAgentResponseUpsert`; roster `dedupe_agent_responses_latest` / `normalize_agent_responses_for_backfill`; tracker/consult append mocks; hop fixtures that read `entity["agent_responses"]`.

**AST-984** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_responses.py::TestAst981StandaloneTableIoRetired \
  tests/component/data/database/test_agent_responses.py::TestAst982StandaloneTableSunset \
  tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired \
  tests/component/core/test_agent.py::TestAst981StandaloneTableAuditRetired \
  tests/component/core/test_agent.py::TestAst984EntityColumnRetired \
  tests/component/core/test_roster.py::TestEntityAgentStory \
  tests/component/core/test_roster.py::TestEntityAgentStoryBranches \
  tests/component/core/test_roster.py::TestAst726LatestOnlyRosterStory \
  tests/component/core/test_roster.py::TestAst727NormalizeAgentResponsesForBackfill \
  tests/component/core/test_tracker.py::TestTrackerFacades::test_ast486_consult_layer_facades_delegate_to_database \
  tests/component/core/test_consult.py::TestRunBatchConsultBranches::test_handles_missing_fabricated_and_bad_grades \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions \
  tests/component/core/test_agent.py::TestAst769GeneralCallerHydration \
  tests/component/scripts/test_backfill_latest_only_rubric_entity_data.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.
