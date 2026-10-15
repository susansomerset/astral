# `database` — timesheets cluster

Component tests: `tests/component/data/database/test_timesheets.py`.

Table: **`service_timesheet`** (renamed from `agent_timesheets` in **AST-2217**). Anthropic mirror table `anthropic_timesheets` is unchanged.

### AST-392 / AST-1878 (ledger insert, list, sum, catalog server check)

| Area | Source | Component tests |
| --- | --- | --- |
| Insert / list / calc-only sum | `_add_timesheet_entry` / `list_timesheets` / `sum_cost_by_batch` | `TestAddTimesheetEntry` · `TestListTimesheets` · `TestSumCostByBatch` |
| Per-server backfill | `backfill_agent_timesheet_costs` | `TestBackfillDeepseekAgentTimesheetCosts` |
| New — ledger SKU must be catalog-priced on the row's server; backfill unknown server raises; backfill scoped to one server | `_add_timesheet_entry` / `backfill_agent_timesheet_costs` | `TestAst1878TimesheetCatalogValidation` |

### AST-1965 · AST-1963 (platform columns + platform-first totals)

`service_timesheet` gains nullable platform columns (`_AGENT_TIMESHEET_PLATFORM_COLUMNS`): `platform_cost` REAL (NULL = not reconciled / stub), `native_tokens_prompt` / `_completion` / `_cached` / `_reasoning` INTEGER, `host` TEXT, `platform_reconciled_at` TIMESTAMP, `platform_metadata` TEXT — after attribution columns (AST-2217) on new tables; `ALTER TABLE … ADD COLUMN` per missing column in `_ensure_timesheets_schema` for existing ones. `update_timesheet_platform(...)` sets those columns + stamps `platform_reconciled_at`, returns rowcount (0 = no row). `sum_cost_by_batch` sums `COALESCE(platform_cost, calc_cost_* sum)` per row.

| Area | Source | Component tests |
| --- | --- | --- |
| Revised — AC 3 (database half): unpriced SKU returns `True` and the row exists; unknown server still raises | `_add_timesheet_entry` | `TestAst1878TimesheetCatalogValidation::test_accepts_unpriced_sku_server_check_stays` |
| Revised — new table: attribution then platform columns after `created_at`, NULL platform on insert | `_create_service_timesheet_table` | `TestAst1965PlatformColumns::test_new_table_appends_nullable_platform_columns` |
| Revised — existing table (platform columns dropped): ensure adds them; old row kept | `_ensure_timesheets_schema` | `…::test_existing_table_gains_columns_and_keeps_rows` |
| New — AC 4 writer sets platform columns + timestamp; originals untouched | `update_timesheet_platform` | `…::test_writer_sets_platform_columns_and_never_touches_originals` |
| New — `None` counts / host stored NULL; unknown `agent_req_id` → 0 | `update_timesheet_platform` | `…::test_writer_passes_missing_counts_as_null_and_misses_unknown_id` |
| New — error inside the write rolls back and raises | `update_timesheet_platform` | `…::test_writer_error_rolls_back_and_raises` |
| New — AC 5 platform-first sum; empty list → `{}` | `sum_cost_by_batch` | `…::test_sum_prefers_platform_cost_per_row` |
| New — reconciled `platform_cost = 0.0` counts as 0 | `sum_cost_by_batch` | `…::test_sum_counts_platform_zero_as_zero` |
| New — backfill skips unpriced rows and leaves platform columns alone | `backfill_agent_timesheet_costs` | `…::test_backfill_skips_unpriced_rows_and_platform_columns` |

**Integration:** none (no `tests/integration/` scenario touches `service_timesheet` / `agent_timesheets`).

### AST-2217 · AST-2215 (rename, attribution, ledger state, stub null cost)

Parent AC **2** (table rename), AC **5** stub half (null `platform_cost` still stamps receipt), AC **8** data half (attribution columns on insert). Externals/agent call-time coverage: [`../../external/anthropic.md`](../../external/anthropic.md), [`../../external/llm_compat.md`](../../external/llm_compat.md), [`../../core/agent.md`](../../core/agent.md), [`../../utils/config.md`](../../utils/config.md).

| Area | Source | Component tests |
| --- | --- | --- |
| New — `agent_timesheets` → `service_timesheet` in place; rows preserved; attribution + platform cols added | `_ensure_timesheets_schema` | `TestAst2217ServiceTimesheet::test_renames_agent_timesheets_preserving_rows` |
| New — attribution kwargs persist on insert (provider/request/entity/timing/status) | `_add_timesheet_entry` | `…::test_attribution_columns_persist_on_insert` |
| New — `TIMESHEET_SEARCH_SERVER_ID` (`google_cse`) allowed as provider | `_add_timesheet_entry` | `…::test_accepts_search_server_id_provider` |
| New — stub `platform_cost=None` stamps `platform_reconciled_at`; sum falls through to calc | `update_timesheet_platform` / `sum_cost_by_batch` | `…::test_update_platform_null_cost_stamps_reconciled` |
| New — ledger `timesheet_state` count / claim NEW→FETCHING / set / list rows for batches | `count_ledger_timesheet_state` / `claim_ledger_timesheet_fetching` / `set_ledger_timesheet_state` / `list_timesheet_rows_for_batches` | `…::test_ledger_timesheet_state_claim_and_list` |
| Broken / revised — PRAGMA / DROP / column-order asserts retargeted to `service_timesheet` + attribution-before-platform | `TestAst1965PlatformColumns` | (same class; see rows above) |

**Broken / obsolete:** SQL string `agent_timesheets` in `_columns` / DROP COLUMN paths under `TestAst1965PlatformColumns` (collection/runtime red after rename). No silent coverage drop.

**Integration:** none — do not invent. Existing scenarios do not name this table.

## QA test manifest

1. **Config registries:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst2217FetchTimesheetRegistries
```

2. **Data layer (rename / attribution / ledger / revised AST-1965):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_timesheets.py
```

3. **Externals — stub `get_receipt` + call-time attribution (probe included on compat):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_anthropic.py::TestAst2217ReceiptStubAndAttribution \
  tests/component/external/test_llm_compat.py::TestAst2217ReceiptStubAndAttribution
```

4. **Agent — DISPATCH_AGENT attribution; multi-entity empty entity id:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent_ast1879.py::TestAst2217CallTimeAttribution
```

**Pass criterion:** pytest green on items 1–4. Not the zero-arg harness / branch-lock gate.

**Bible shasums (after publish):**

```text
git show origin/sub/AST-2215/AST-2217-timesheet-rename-attribution-stubs:docs/test-bible/data/database/timesheets.md | shasum
git show origin/sub/AST-2215/AST-2217-timesheet-rename-attribution-stubs:docs/test-bible/utils/config.md | shasum
git show origin/sub/AST-2215/AST-2217-timesheet-rename-attribution-stubs:docs/test-bible/external/anthropic.md | shasum
git show origin/sub/AST-2215/AST-2217-timesheet-rename-attribution-stubs:docs/test-bible/external/llm_compat.md | shasum
git show origin/sub/AST-2215/AST-2217-timesheet-rename-attribution-stubs:docs/test-bible/core/agent.md | shasum
```
