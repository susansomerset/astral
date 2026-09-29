# Timesheets

**Test module:** `tests/component/data/database/test_timesheets.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-1878 · AST-1851 (timesheet SKU/server check + per-server backfill)

**Primary manifest:** **`docs/test-bible/data/database/candidates.md`** § AST-1878.

| Area | Source | Component tests |
| --- | --- | --- |
| New — ledger SKU must be catalog-priced on the row's server; backfill unknown server raises; backfill scoped to one server | `_add_timesheet_entry` / `backfill_agent_timesheet_costs` | `TestAst1878TimesheetCatalogValidation` |
| Revised — `backfill_deepseek_agent_timesheet_costs()` → `backfill_agent_timesheet_costs("deepseek")` | `src/data/database.py` | `TestBackfillDeepseekAgentTimesheetCosts::test_recomputes_deepseek_costs_leaves_anthropic_unchanged` |
