# Timesheets

**Test module:** `tests/component/data/database/test_timesheets.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-1878 · AST-1851 (timesheet SKU/server check + per-server backfill)

**Primary manifest:** **`docs/test-bible/data/database/candidates.md`** § AST-1878.

| Area | Source | Component tests |
| --- | --- | --- |
| New — ledger SKU must be catalog-priced on the row's server; backfill unknown server raises; backfill scoped to one server | `_add_timesheet_entry` / `backfill_agent_timesheet_costs` | `TestAst1878TimesheetCatalogValidation` |
| Revised — `backfill_deepseek_agent_timesheet_costs()` → `backfill_agent_timesheet_costs("deepseek")` | `src/data/database.py` | `TestBackfillDeepseekAgentTimesheetCosts::test_recomputes_deepseek_costs_leaves_anthropic_unchanged` |

**AST-1880 (pointer):** `TestBackfillDeepseekAgentTimesheetCosts::test_recomputes_deepseek_costs_leaves_anthropic_unchanged` computes its expectation with `calculate_cost_components_from_counts(..., sku="deepseek-v4-pro", server_id="deepseek")`. The DeepSeek-named wrapper is deleted. Manifest: [`../../ui/api/api_admin.md`](../../ui/api/api_admin.md) § AST-1880.

### AST-1965 · AST-1963 (platform columns + platform-first totals)

`agent_timesheets` gains seven nullable columns appended after `created_at` (`_AGENT_TIMESHEET_PLATFORM_COLUMNS`): `platform_cost` REAL (NULL = not reconciled), `native_tokens_prompt` / `_completion` / `_cached` / `_reasoning` INTEGER, `host` TEXT, `platform_reconciled_at` TIMESTAMP — in `_create_agent_timesheets_table` for new tables, `ALTER TABLE … ADD COLUMN` per missing column in `_ensure_timesheets_schema` for existing ones. `update_timesheet_platform(agent_req_id, platform_cost, native_tokens_prompt, native_tokens_completion, native_tokens_cached, native_tokens_reasoning, host)` sets those columns + stamps `platform_reconciled_at`, returns rowcount (0 = no row). `_add_timesheet_entry` no longer calls `get_sku_pricing` (server id check stays). `sum_cost_by_batch` sums `COALESCE(platform_cost, calc_cost_* sum)` per row. Callers (background reconcile, `llm_compat` unpriced rows) are AST-1966's.

| Area | Source | Component tests |
| --- | --- | --- |
| Revised — AC 3 (database half): unpriced SKU (priced on another server / priced nowhere) returns `True` and the row exists; unknown server still raises (reverses AST-1878's SKU rejection) | `_add_timesheet_entry` | `TestAst1878TimesheetCatalogValidation::test_accepts_unpriced_sku_server_check_stays` (was `test_rejects_sku_not_priced_on_server`) |
| New — new table: seven columns after `created_at` in order, NULL on insert | `_create_agent_timesheets_table` | `TestAst1965PlatformColumns::test_new_table_appends_nullable_platform_columns` |
| New — existing table (columns dropped to pre-AST-1965 shape): ensure adds all seven, old row unchanged with NULL platform values; second ensure idempotent | `_ensure_timesheets_schema` | `…::test_existing_table_gains_columns_and_keeps_rows` |
| New — AC 4 writer sets platform columns + timestamp; every original column (calc_cost_*, tokens) equals the insert; sibling row untouched | `update_timesheet_platform` | `…::test_writer_sets_platform_columns_and_never_touches_originals` |
| New — `None` counts / host stored NULL; unknown `agent_req_id` → 0, nothing written | `update_timesheet_platform` | `…::test_writer_passes_missing_counts_as_null_and_misses_unknown_id` |
| New — error inside the write rolls back and raises | `update_timesheet_platform` | `…::test_writer_error_rolls_back_and_raises` |
| New — AC 5 reconciled (calc 0.01, platform 0.03) + unreconciled (calc 0.02) → 0.05; other batch calc-only; empty list → `{}` | `sum_cost_by_batch` | `…::test_sum_prefers_platform_cost_per_row` |
| New — reconciled `platform_cost = 0.0` counts as 0 (NULL, not falsy, is the fallback trigger) | `sum_cost_by_batch` | `…::test_sum_counts_platform_zero_as_zero` |
| New — boundary: backfill skips unpriced rows and leaves platform columns alone | `backfill_agent_timesheet_costs` | `…::test_backfill_skips_unpriced_rows_and_platform_columns` |
| Kept — insert / list / calc-only sum / per-server backfill | — | `TestAddTimesheetEntry` · `TestListTimesheets` · `TestSumCostByBatch` · `TestBackfillDeepseekAgentTimesheetCosts` · `TestAst1878…` (other 3) |

`--cov-branch` over this file on the publish tip: no missing line or partial branch in any AST-1965 hunk of `database.py` (not in `LOCKED_AT_100`). Negative check: the 8 new/revised nodes fail against `origin/ftr` product without AST-1965.

No other test asserts `agent_timesheets` row shape or patches `database.get_sku_pricing` (import removed). `test_dispatcher.py` / `test_agent.py` stub `sum_cost_by_batch` and are unaffected.

**Integration:** none (no `tests/integration/` scenario touches `agent_timesheets`).

## QA test manifest

1. **Component (narrowed — must be all green, 16 on the publish tip):**

```bash
./scripts/testing/run_component_tests.sh tests/component/data/database/test_timesheets.py
```

2. **Ledger-adjacent regression (informational — no new reds vs `origin/ftr`):**

```bash
.venv/bin/python -m pytest tests/component/ui/api/test_api_admin.py tests/component/core/test_agent_ast1879.py tests/component/core/test_consult.py tests/component/core/test_tracker.py -q --tb=line
```

43 pre-existing reds on `origin/ftr/AST-1963-platform-timesheet-cost` with this test tree (5 `test_api_admin.py`, 21 `test_consult.py`, 17 `test_tracker.py`; none in `test_agent_ast1879.py`) — same set on the publish tip. The `origin/ftr` baseline run also showed `test_tracker.py::TestInitializeJob::test_omits_nested_job_data_when_absent` · `::test_splits_columns_and_metadata` red (green on the publish tip; not timesheet code). Any failure outside that set is real.

**Pass criterion:** item 1 green; item 2 no reds beyond the `origin/ftr` baseline. Not the zero-arg harness.

**Bible shasum (after publish):** `git show origin/sub/AST-1963/AST-1965-timesheet-platform-columns:docs/test-bible/data/database/timesheets.md | shasum`
