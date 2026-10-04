# Timesheets

**Test module:** `tests/component/core/test_timesheets.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/timesheets.py` | `tests/component/core/test_timesheets.py` | yes |

### AST-1966 · AST-1963 (background platform cost reconcile per call)

`record_timesheet_entry` inserts the row, then — when it has an `agent_req_id` and `get_model_routing(provider, model_code)` is `openrouter` — starts a daemon thread running `reconcile_timesheet_platform(agent_req_id, server_id, candidate_id, batch_id)` under `contextvars.copy_context()` and returns. `direct` rows / no generation id return with no thread; an unknown (server, SKU) raises `ValueError` after the insert (plan: config drift; every `record_timesheet` call site in `llm_compat` / `anthropic` wraps it in `try/except`). The reconcile: candidate's key for the server (`get_candidate(...)["candidate_api_keys"][server]`; none → one WARNING, stop) → `time.sleep(TIMESHEET_RECONCILE_INITIAL_WAIT_SECONDS)` then `get_generation_stats` up to `TIMESHEET_RECONCILE_RETRIES` tries, `time.sleep(BASE · 2^(n-1))` before try n+1 → all fail: one WARNING naming req id + batch id → success: `update_timesheet_platform`, then if the batch's `dispatch_ledger` row has `completed_at`, `total_cost = sum_cost_by_batch`, `entity_cost = round(total ÷ total_processed, 7)` (total when processed is 0) → any exception: one `logger.exception`, never raised. Lookup: [`../external/openrouter.md`](../external/openrouter.md) § AST-1964; writer / platform-first sum: [`../data/database/timesheets.md`](../data/database/timesheets.md) § AST-1965; unpriced rows from `llm_compat`: [`../external/llm_compat.md`](../external/llm_compat.md) § AST-1966.

Patch points (module globals, looked up at call time): `get_generation_stats`, `get_candidate`, `time.sleep` (fixture `keyed` records the waits), `reconcile_timesheet_platform`, `get_model_routing`, `get_dispatch_ledger`, `TIMESHEET_RECONCILE_RETRIES` / `…_INITIAL_WAIT_SECONDS` / `…_BACKOFF_BASE_SECONDS`. AC 5 / AC 6 call `reconcile_timesheet_platform` synchronously after `_add_timesheet_entry`; only AC 4 starts the real thread (lookup gated on a `threading.Event`, row polled).

| Area | Source | Component tests |
| --- | --- | --- |
| Revised — delegate test names a direct model (`deepseek-v4-pro` / `deepseek`) — a row with a generation id must name a catalog model; asserts no reconcile started | `record_timesheet_entry` | `TestRecordTimesheetEntry::test_delegates_to_database_add` |
| New — no generation id → no routing lookup (old call shape still valid) | `record_timesheet_entry` | `TestRecordTimesheetEntry::test_row_without_generation_id_skips_routing` |
| New — AC 4 openrouter row: returns < 1 s while the lookup is blocked, row exists with NULL platform cost; thread is daemon, carries `log_batch_id`, gets the candidate's key, writes once released | `record_timesheet_entry` | `TestAst1966RecordNeverWaits::test_openrouter_row_returns_before_blocked_lookup` |
| New — AC 4 direct rows (deepseek / kimi / anthropic): no thread, stub never called | `record_timesheet_entry` | `…::test_direct_row_is_never_looked_up` (3) |
| New — unknown (server, SKU): `ValueError` after the row is written, no thread | `record_timesheet_entry` | `…::test_unknown_model_raises_after_insert_without_thread` |
| New — AC 5 not-ready ×4 then 200 → 5 calls, waits `[30, 2, 4, 8, 16]`, platform columns set, `calc_cost_*` unchanged | `reconcile_timesheet_platform` | `TestAst1966RetryThenGiveUp::test_not_ready_four_times_then_200` |
| New — AC 5 fails every time → 5 calls, waits `[30, 2, 4, 8, 16]`, row unchanged, exactly one WARNING with req id + batch id, no ERROR | `reconcile_timesheet_platform` | `…::test_fails_every_time_gives_up_with_one_warning` |
| New — count + base read from config (3 / 2.0, 4 / 0.5, 1 try → initial wait only); first sleep is the 30 s propagation wait | `reconcile_timesheet_platform` | `…::test_count_and_base_come_from_config` (3) |
| New — no key (no candidate, no keys dict, other server only, empty key) → one WARNING, no lookup | `reconcile_timesheet_platform` | `…::test_no_key_warns_once_and_never_looks_up` (5) |
| New — lookup raises → one ERROR with traceback naming the row, nothing propagates | `reconcile_timesheet_platform` | `…::test_exception_logged_once_never_raised` |
| New — AC 6 closed ledger (processed 2, total 0.02) → total 0.06, entity 0.03 | ledger refresh | `TestAst1966ClosedLedgerRefresh::test_closed_row_is_retotalled` |
| New — closed, processed 0 → entity cost = total (dispatcher rule) | ledger refresh | `…::test_closed_row_with_zero_processed_takes_total_as_entity_cost` |
| New — AC 6 open ledger (`completed_at` NULL) unchanged; platform row still written | ledger refresh | `…::test_open_row_untouched` |
| New — no batch id → no ledger lookup; batch with no ledger row → no refresh, no raise | ledger refresh | `…::test_no_batch_or_no_ledger_row_writes_platform_only` |
| New — second reconcile of the same row → same totals (recomputed from the table) | ledger refresh | `…::test_rerun_is_idempotent` |

`LOCKED_AT_100`: `--cov-branch` over `src/core/timesheets.py` from item 1 reports 100% (46 stmts, 14 branches).

No other test reaches the real reconcile: a throwaway autouse spy on `reconcile_timesheet_platform` across `tests/component/{core,ui,external}` recorded zero starts (callers stub `record_timesheet` or use direct models), so no component test opens a thread or the network.

**Integration:** none (no `tests/integration/` scenario records timesheets or reaches OpenRouter).

## QA test manifest

1. **Component (narrowed — must be all green, 109 on the publish tip):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_timesheets.py \
  tests/component/external/test_llm_compat.py \
  tests/component/external/test_openrouter.py \
  tests/component/data/database/test_timesheets.py
```

2. **Wider regression (informational — no new reds vs `origin/ftr`):**

```bash
.venv/bin/python -m pytest tests/component/core tests/component/ui tests/component/external \
  --ignore=tests/component/core/test_meteorite_email.py --ignore=tests/component/core/test_page_intake.py \
  --ignore=tests/component/core/test_surfer.py -q --tb=no
```

227 failed on both `origin/ftr/AST-1963-platform-timesheet-cost` and the publish tip with this test tree — identical sets (43 of them `test_agent.py`, as the engineer noted). The three ignored files fail collection on both (`src.core.meteorite_email` / `page_intake` / `surfer` absent). Before this pass the only new red was `TestRecordTimesheetEntry::test_delegates_to_database_add`, revised above. Any failure outside the baseline set is real.

**Pass criterion:** item 1 green; item 2 no reds beyond the `origin/ftr` baseline. Not the zero-arg harness.

**Bible shasums (after publish):** `for p in core/timesheets.md external/llm_compat.md; do git show origin/sub/AST-1963/AST-1966-background-reconcile:docs/test-bible/$p | shasum; done`
