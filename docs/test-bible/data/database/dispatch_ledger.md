# Dispatch Ledger

**Test module:** `tests/component/data/database/test_dispatch_ledger.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-1960 · AST-1954 (served LLM host column)

**Primary manifest:** [`../../core/agent.md`](../../core/agent.md) § AST-1960. `dispatch_ledger` gains `host TEXT` (fresh `CREATE` and the pre-existing-table `ALTER` list; AST-1497 DDL only, old rows stay NULL). `_LEDGER_UPDATE_COLS` includes `host`. Readers are unchanged: `get_dispatch_ledger` / `list_dispatch_ledger` are `SELECT *`, so they return the column.

| Area | Source | Component tests |
| --- | --- | --- |
| New — fresh row `host` NULL; `update_dispatch_ledger(host=)` accepted; `get_` + `list_dispatch_ledger` return it | `_ensure_dispatch_ledger_schema` / `update_dispatch_ledger` / readers | `TestAst1960LedgerHostColumn::test_fresh_table_has_host_and_update_round_trips_through_readers` |
| New — pre-AST-1960 table gains `host` by ALTER; old row stays NULL, new row writable | `_ensure_dispatch_ledger_schema` | `…::test_legacy_table_gains_host_and_old_rows_stay_null` |
| Kept — insert / duplicate / unknown-column reject / allowed update | same | `TestSaveDispatchLedger` · `TestUpdateDispatchLedger` |

**Integration:** none (`tests/integration/conftest.py` only resets `_dispatch_ledger_schema_ensured`).

### AST-2008 · AST-2007 (llm_call_seconds / llm_failure_class columns)

Fresh CREATE + legacy ALTER (old rows NULL, no backfill) + `_LEDGER_UPDATE_COLS`. **New:** `TestAst2008LedgerCallOutcomeColumns::test_fresh_table_has_both_and_update_round_trips`, `…::test_legacy_table_gains_both_and_old_rows_stay_null`. Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-2008.
