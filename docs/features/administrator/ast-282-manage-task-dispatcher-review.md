# Code Review: `446eb2d` — ast-282: Manage Task Dispatcher

## What it does

Seven-subissue feature delivered in a single commit:
1. `dispatch_task` table with CRUD, `get_due_tasks`, atomic `claim/release`, and `count_entities_in_state` in `database.py`
2. `ctx` (candidate raft) threading through `do_task`, `render_verdict`, `qualify_job_listings`, `evaluate_jd`, `prefilter_company` with per-call Anthropic API key override
3. `candidate_id` scoping on `set_company_batch`, `claim_company_batch`, `claim_job_batch`, `get_new_company_batch`, `get_new_job_batch`
4. All 9 batch CLIs refactored: `run_batch()` extracted, `--batch-id` and `--candidate-id` args added, `log_batch_id` + `flush_log_buffer` integration
5. `DISPATCH_TASKS` config registry (9 entries) + `src/cli/dispatcher.py` orchestrator
6. Core wrappers in `dispatch.py`, API blueprint (`admin_dispatch_tasks.py`) with GET/POST/PUT, nav enabled
7. De-stubbed `ScheduledActions.tsx` — full Task Dispatcher screen with filters, sortable table, inline enabled toggle, add/edit modals

## The Good

1. **Dispatcher orchestration loop is clean and correct.** The `dispatch()` flow — `get_due_tasks` → atomic claim → entity count check → ctx fetch → ledger write → `importlib.import_module` → `run_batch()` → ledger update → release — follows the plan exactly. The `finally` block always releases the task and flushes logs, even on exception. The `summary` dict is pre-initialized before `try`, so the `except` branch can safely override it.

2. **`claim_dispatch_task` is properly atomic.** `UPDATE ... WHERE id = ? AND batch_id IS NULL` with `rowcount > 0` check. If a cron overlap fires two dispatchers simultaneously, only one will claim each task. This is the correct pattern for SQLite advisory locking.

3. **`update_dispatch_task` is column-whitelisted.** Unlike `update_dispatch_ledger` (ast-281 review issue #2), this function validates `kwargs` against `_DISPATCH_TASK_UPDATE_COLS` and raises `ValueError` on unknown keys. Typos caught at call time instead of producing `OperationalError`. Good improvement over the ledger pattern.

4. **`ctx` threading is backward-compatible across all layers.** Every function that gains `ctx` has it as an optional `=None` parameter. The three consult functions, `prefilter_company`, `get_new_company_batch`, `get_new_job_batch`, `claim_job_batch`, `set_company_batch` — all additive. Existing CLI scripts and tests continue to work unchanged.

5. **`do_task` API key override is precise.** Only triggers when both `ctx` is provided AND `requires_candidate_key` is True. Creates a per-call `Anthropic(api_key=...)` client — correctly avoids mutating the shared `_client` singleton. The `cd = (ctx.get("candidate_data") or {}) if ctx else (candidate_data or {})` precedence is clear and the old `candidate_data` param still works.

6. **`candidate_id` scoping on job claims uses the correct indirect pattern.** `claim_job_batch` adds `AND company IN (SELECT short_name FROM company WHERE candidate_id = ?)` because jobs don't have a direct `candidate_id` column — they're scoped via their parent company. Same subquery pattern used in `count_entities_in_state`. Consistent.

7. **`run_batch()` extraction is consistent across all 9 CLIs.** Same signature (`ctx`, `batch_id`, `limit`), same return type (`Dict[str, int]` with `total_processed/passed/failed/errors`), same `log_batch_id.set()` + `flush_log_buffer()` bookend pattern. `main()` is reduced to argparse + delegate.

8. **UI uses `admin-filters` CSS class.** Fixes the hidden coupling issue flagged in the ast-281 review (which used `timesheet-filters`). The Task Dispatcher screen reuses the shared admin filter styling correctly.

9. **API layer is properly hardened.** POST validates required fields and returns 400 with specifics. PUT whitelists exactly `freq_hrs`, `min_count`, `enabled` — cannot change `candidate_id` or `task_key` after creation. Type coercion (`float`, `int`, `int(bool(...))`) is done in the API layer before passing to core.

---

## Issues to Address

### 1. BUG: `ctx` not threaded through `find_job_page`, `parse_job_list`, or gazer-internal AI calls

The plan calls out ctx threading for the full call stack, but three `run_batch()` functions don't pass `ctx` to the core functions that make AI calls:

- **`locate_job_page.py`** → calls `find_job_page(url, short_name, company_website)` — `find_job_page` doesn't accept `ctx`, so `do_task("find_job_site")`, `do_task("vet_job_list")`, and `do_task("select_culture_pages")` all fire without a candidate API key or candidate data for token resolution.
- **`parse_job_list.py`** → calls `roster.parse_job_list(company, context)` — which internally calls `_fetch_parse_job_list` → `do_task("parse_job_list")` without ctx.

All of these tasks have `requires_candidate_key: True` in `TASK_CONFIG`. When dispatched, they'll use the environment API key instead of the candidate's key, and the warning "requires_candidate_key is True but no candidate_data provided — tokens will resolve to empty" will fire.

The tasks that DO thread ctx correctly: `prefilter.py` → `prefilter_company(ctx=ctx)`, `qualify_batch.py` → `qualify_job_listings(ctx=ctx)`, `evaluate_jd_batch.py` → `evaluate_jd(ctx=ctx)`, `consult_*_batch.py` → `render_verdict(ctx=ctx)`.

**Fix:** Add `ctx` parameter to `find_job_page`, `_fetch_parse_job_list`/`parse_job_list` in `roster.py`, and forward it to their `do_task` calls. Update `locate_job_page.py` and `parse_job_list.py` `run_batch()` to pass `ctx` through.

### 2. No UNIQUE constraint on `(candidate_id, task_key)` — allows duplicate scheduling

The `dispatch_task` schema has no uniqueness constraint. The POST endpoint doesn't check for existing rows with the same `(candidate_id, task_key)` pair. An admin can accidentally create two scheduling entries for the same candidate + task, and `get_due_tasks()` will return both — the dispatcher will run the same task twice per cycle.

**Fix:** Add `UNIQUE(candidate_id, task_key)` to the schema, or add a check-before-insert in `save_dispatch_task` / the API POST handler.

### 3. `--limiterror` argument accepted but silently ignored in `locate_job_page.py`

The CLI parser still defines `--limiterror`:
```python
parser.add_argument("--limiterror", type=int, metavar="N", help="Stop after N outcomes of ERROR only")
```

But `run_batch()` doesn't implement error-limit logic. The old `main()` tracked `error_limit_count` and broke out of the batch loop on reaching the limit. After refactoring, `main()` delegates entirely to `run_batch()`, which has no awareness of this argument.

Either remove the argument from the parser or add `error_limit` as an optional parameter on `run_batch()`.

### 4. `run_batch()` double-clears `log_batch_id` and double-flushes when called from dispatcher

Each `run_batch()` ends with:
```python
flush_log_buffer()
log_batch_id.set(None)
```

And the dispatcher's `finally` block does the same:
```python
flush_log_buffer()
log_batch_id.set(None)
database.release_dispatch_task(task["id"])
```

Double-flush and double-clear are harmless (flush is a no-op if buffer is empty, set(None) is idempotent). But it means when called standalone via CLI, `run_batch()` correctly manages its own cleanup, and when called from dispatcher, the dispatcher's cleanup is redundant. This is the right design — each layer is self-sufficient. Just noting it's intentional.

### 5. `debug` parameter dropped from `gaze_batch` and `locate_job_page` `run_batch()`

The old `main()` in `gaze_batch.py` passed `debug=args.debug` to `process_gazer_batch()`. The new `run_batch()` calls `process_gazer_batch(bid, companies)` without `debug`. Same for `locate_job_page.py` — old code passed `debug=args.debug` to `find_job_page()`, new `run_batch()` omits it.

When invoked from the dispatcher, debug output is never needed. But when invoked from CLI with `--debug`, the flag is parsed but never forwarded to `run_batch()`.

Low priority — debug is a development aid, not a production concern. But if someone runs `python -m src.cli.gaze_batch --debug`, they won't get the debug output they expect.

**Fix:** Add optional `debug: bool = False` to `run_batch()` and forward it. `main()` passes `debug=args.debug`.

---

## Minor Notes

- **`release_dispatch_task` sets `last_run_at` on release, not on claim.** This is correct — the freq_hrs cooldown starts from when the task finished, so the next run is scheduled relative to completion, not start. If a task takes 2 hours and freq_hrs is 4, it runs again 4 hours after finishing (6 hours after the previous start), not 4 hours after starting (2 hours after finishing).

- **`get_due_tasks` uses `CAST(freq_hrs AS TEXT)` in the datetime modifier.** SQLite's `datetime('now', '-X hours')` requires the modifier string to be well-formed. The `CAST` ensures `freq_hrs` (stored as REAL) is converted to text for string concatenation. This handles fractional hours correctly — `datetime('now', '-1.5 hours')` is valid SQLite.

- **`count_entities_in_state` validates `entity_type` with a hard `ValueError`.** Only `"company"` and `"job"` are accepted. If a future task type uses a different entity, this function needs updating. Acceptable for now since all 9 dispatch tasks are company or job entities.

- **Dispatcher imports `get_candidate` from `database` directly** (not through core). This is the documented layer exception — scheduling infrastructure bypasses core. Consistent with the plan's design decision.

- **`gaze` and `locate_job_page` share `trigger_state: "WATCH"`.** Both are company-state tasks that fire on WATCH companies — gaze scans for job listings while locate_job_page finds the careers page. They can run independently and will each claim separate batches via the atomic claim. No conflict.

- **Add modal uses free-text inputs for `candidate_id` and `task_key`.** For an admin-only tool this is acceptable, but dropdowns populated from `list_candidates()` and `DISPATCH_TASKS.keys()` would prevent typos. The skeleton review already noted this — filter dropdowns are data-derived (from loaded dispatch_tasks), but the add-modal inputs are not.

- **`save_dispatch_task` returns `lastrowid`.** The API correctly returns `{"id": task_id}` with 201 status. The frontend doesn't use the returned id (it reloads the full list), but it's available for future use.

---

## Summary

This is a well-executed 21-file feature that lands the core automation engine for the project. The dispatcher loop, atomic claiming, and ctx/API-key threading design are all solid. The CLI refactoring is impressively consistent across 9 files. **Issue #1** (ctx not threaded through `find_job_page` and `parse_job_list`) is the most important — those tasks will use the wrong API key and get empty token resolution when dispatched. **Issue #2** (missing unique constraint) is a data integrity risk that should be fixed before production use. Everything else is minor.

---

## Changes Applied

**Fix #1 — ctx threading through find_job_page and parse_job_list:**
- Added `ctx` parameter to `find_job_page`, `_fetch_jobsite_page_options`, `_fetch_jobsite_analysis` in `roster.py`
- Forwarded `ctx=ctx` to all `do_task("find_job_site")`, `do_task("vet_job_list")` calls
- Added `ctx` to all 4 recursive `find_job_page` calls
- Added `ctx` parameter to `parse_job_list` and `_fetch_parse_job_list` in `roster.py`, forwarded to `do_task("parse_job_list")`
- Updated `locate_job_page.py` to pass `ctx=ctx` to `find_job_page`
- Updated `parse_job_list.py` to pass `ctx=ctx` to `parse_job_list`

**Fix #2 — UNIQUE constraint:**
- Added `UNIQUE(candidate_id, task_key)` to `dispatch_task` CREATE TABLE in `database.py`

**Fix #3 — `--limiterror` wired into `run_batch()`:**
- Added `error_limit` parameter to `locate_job_page.py`'s `run_batch()` with early-break logic matching the original `main()` behavior
- `main()` now passes `error_limit=args.limiterror` to `run_batch()`

**Fix #4 — Double-clear:** Intentional, no action needed.

**Fix #5 — `debug` parameter restored:**
- Added `debug: bool = False` to `locate_job_page.py` `run_batch()`, forwarded to `find_job_page(debug=debug)`
- Added `debug: bool = False` to `gaze_batch.py` `run_batch()`, forwarded to `process_gazer_batch(debug=debug)`
- Both `main()` functions now pass `debug=args.debug` to `run_batch()`
