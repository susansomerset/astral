# `timesheets` — fetch_timesheet runner

Component tests: `tests/component/core/test_timesheets.py`.

Platform receipts are fetched by the candidate-bound `fetch_timesheet` dispatch task (**AST-2218**). Daemon reconcile (`reconcile_timesheet_platform`, batch OpenRouter threads) is **retired**. Schema / attribution writers: [`../data/database/timesheets.md`](../data/database/timesheets.md) § AST-2217.

### AST-1966 / AST-2008 (retired — daemon reconcile)

Historical coverage of `reconcile_timesheet_platform` / `TIMESHEET_RECONCILE_ENABLED` thread paths is **obsolete**. Replaced by § AST-2218 runner tests. Do not reinstate daemon nodes.

### AST-2218 · AST-2215 (`run_fetch_timesheet`, search recorder, thread-free record)

Parent AC **1** (no cost threads), **6** (NEW→FETCHING→RECEIPTED/NEW), **7** (stub null cost), **10** (closed-ledger catch-up). OpenRouter billed receipts: [`../external/openrouter.md`](../external/openrouter.md). Provision / due: [`dispatcher.md`](dispatcher.md).

| Area | Source | Component tests |
| --- | --- | --- |
| Revised — `record_timesheet_entry` inserts only (no thread) | `record_timesheet_entry` | `TestRecordTimesheetEntry` |
| New — search-call recorder (`DISPATCH_SEARCH` / `google_cse`) | `record_search_timesheet_entry` | `TestRecordSearchTimesheetEntry::test_writes_dispatch_search_google_cse_row` |
| New — AC 6 walk: A receipted / B not-ready then retry; FETCHING mid-lookup; other candidate never claimed | `run_fetch_timesheet` | `TestAst2218RunFetchTimesheet::test_ac6_walk_receipted_and_retry_not_ready` |
| New — AC 6 exception releases FETCHING → NEW | `run_fetch_timesheet` | `…::test_ac6_exception_releases_fetching_to_new` |
| New — AC 7 stub null cost keeps calc; OpenRouter platform wins | `run_fetch_timesheet` / `sum_cost_by_batch` | `…::test_ac7_stub_null_cost_keeps_calc_openrouter_platform_wins` |
| New — AC 10 closed ledger total/entity catch-up | `_refresh_closed_ledger_totals` | `…::test_ac10_refresh_closed_ledger_totals` |

**Broken / obsolete:** all `TestAst1966*` / `TestAst2008ReconcileSwitch` daemon nodes (product symbols removed).

**Integration:** none — do not invent.

## QA test manifest

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst2218FetchTimesheetAdminDefaults \
  tests/component/external/test_openrouter.py::TestAst2218GetReceipt \
  tests/component/core/test_timesheets.py \
  tests/component/core/test_dispatcher.py::TestAst2218FetchTimesheetProvisionAndDue
```

**Pass criterion:** pytest green on the nodes above. Not the zero-arg harness.

**Bible shasums (after publish):**

```text
git show origin/sub/AST-2215/AST-2218-fetch-timesheet-openrouter-daemon-retire:docs/test-bible/core/timesheets.md | shasum
git show origin/sub/AST-2215/AST-2218-fetch-timesheet-openrouter-daemon-retire:docs/test-bible/external/openrouter.md | shasum
git show origin/sub/AST-2215/AST-2218-fetch-timesheet-openrouter-daemon-retire:docs/test-bible/core/dispatcher.md | shasum
git show origin/sub/AST-2215/AST-2218-fetch-timesheet-openrouter-daemon-retire:docs/test-bible/utils/config.md | shasum
```
