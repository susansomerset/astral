# Code Review: AST-327 — Refactor Task Dispatcher to Run Independent Threads
**Commit:** `b402dfc`
**Branch:** `dev`
**Reviewed:** 2026-03-17

**Resolution (post-review):**
- **Issue 1 (race + return value):** `asyncio_task` now registered at top of `_dispatch_one` before `_tracked()` is defined, closing the startup race window. `cancel_task` now returns distinct `reason` codes: `not_running`, `not_yet_ready`, `already_done`, or `killed: True`.
- **Issue 2 (comment):** Added one-liner to `_tick_loop` noting `tick_secs`/`max_auto` are captured once at thread start.
- **Issue 3 (min_count alignment):** `get_due_tasks` threshold changed from `or 0` to `or 1`, matching the runner, preventing noisy zero-work thread spawns.
- **Issue 4 (freq_hrs semantics):** Confirmed by Susan — `freq_hrs` is an entity-level filter applied at batch claim time, not a task-level cooldown. Added clarifying comment in `_tick_loop`.

---

## Compile / Lint

All modified Python files (`dispatcher.py`, `database.py`, `config.py`, `api_admin.py`, `api_system.py`) compile clean with `python3 -m py_compile`. TypeScript (`AdminScheduledActions.tsx`) passes `tsc --noEmit` with zero errors.

---

## What's Solid

- **Migration** — The `enabled → auto_mode` table-rebuild pattern is correct for SQLite's lack of `ALTER COLUMN RENAME`. The fallback `_migrate_cols` guard includes `auto_mode` so fresh installs that skipped the rename path still get the column.
- **Thread model** — Each task gets its own `asyncio.new_event_loop()`, which correctly avoids cross-loop confusion. Registry cleanup in `_task_thread_target`'s `finally` block is solid — exits whether the dispatch completes, times out, or is cancelled.
- **Cancellation path** — `cancel_task` uses `loop.call_soon_threadsafe(asyncio_task.cancel)` to safely reach the asyncio task from a different thread. The `except asyncio.CancelledError` in `_dispatch_one` writes the ledger with `INTERRUPTED` and clears the batch log context. `asyncio.wait_for` re-raises `CancelledError` correctly when the outer task is cancelled.
- **Tick loop cap** — Counting only `is_auto=True` entries in the registry before spawning is correct; CLICK tasks don't eat AUTO slots. FIFO by `ORDER BY id` in `get_due_tasks` is a sensible default.
- **`start_scheduler` stale-row cleanup** — Carried over from the old model and still correct: any `RUNNING` ledger rows from a crashed/restarted process are marked `INTERRUPTED` before the new tick thread starts.
- **API consolidation** — All scheduler endpoints cleanly moved to `api_admin.py`. `api_system.py` is now infrastructure-only. No orphaned imports remain.
- **Frontend** — The `threadStatus` poll interval dropped from 15s to 5s, appropriate for per-task live status. Stop All modal explicitly lists running threads with AUTO/CLICK badge before confirming. Run/Stop buttons correctly key off `threadStatus[row.id]?.running`. `activeThreads.length === 0` correctly disables the Stop All button.
- **Config keys** — Old `dispatch_interval_minutes` and `auto_run` fully replaced. `dispatch_timeout_seconds` properly read by `_dispatch_one` at task start, not at module load.
- **Docs** — `ASTRAL_CODE_RULES.md` §3.5 accurately reflects the new model.

---

## Issues

### Issue 1 — `cancel_task` can silently miss if called before `asyncio_task` is registered ⚠️

**File:** `src/core/dispatcher.py`, lines 570–578 and 699–701

`_tracked()` sets `entry["asyncio_task"] = asyncio.current_task()` as its very first `await`-adjacent step — but it runs inside `loop.run_until_complete()` in the daemon thread. If `cancel_task()` is called from the API thread in the narrow window between `t.start()` (line 688) and when `_tracked()` executes its first line, `entry["asyncio_task"]` is still `None` and the cancellation is a no-op:

```python
# cancel_task line 700 — asyncio_task is None here if called too early
if loop and asyncio_task and not asyncio_task.done():
```

In practice this window is tiny (milliseconds), but a fast UI double-click or a programmatic race could hit it. The task would then run to completion despite the user pressing Stop immediately after Run.

**Options:**
1. After `loop.call_soon_threadsafe`, spin-wait briefly for `asyncio_task` to populate, then retry the cancel (simple but adds complexity).
2. Register `asyncio_task` immediately when the event loop starts in `_task_thread_target`, before `run_until_complete`, by scheduling a coroutine that sets it synchronously. This avoids the race entirely.
3. Accept the race as negligibly unlikely in practice (the task would just run one cycle and stop naturally). Given this is an admin kill UI, option 3 is defensible.

**Recommendation:** At minimum, return `{"killed": False, "reason": "not_yet_ready"}` in this case rather than silently returning `killed: False` with no explanation — so the UI could surface "task is starting, try again" rather than leaving the user thinking the stop worked.

** Susan Note **
If just pushing Stop again would catch any stragglers, no need to belt-and-suspenders here, just allow the possible miss and let the user deal with it.

---

### Issue 2 — `_tick_loop` reads `max_auto` once at thread start — config changes require restart ℹ️

**File:** `src/core/dispatcher.py`, lines 732–733

```python
tick_secs = ASTRAL_CONFIG.get("tick_rate_minutes", 1) * 60
max_auto = ASTRAL_CONFIG.get("max_auto_threads", 3)
```

Both are captured at the top of `_tick_loop()`, before the `while True`. Since `ASTRAL_CONFIG` is a module-level dict and there's no live-reload mechanism, this is fine in practice — changes require a server restart regardless. But worth a comment so future readers don't wonder why a runtime config change has no effect.

**Recommendation:** Add a one-liner comment:
```python
# Captured once; changes require server restart (ASTRAL_CONFIG is read-only at runtime)
```

** Susan Note **
Yes, capture it once and the comment is fine.  There is no issue with requiring a restart to reset that variable.

---

### Issue 3 — `min_count` threshold mismatch between `get_due_tasks` and `_run_dispatch_loop` 🔧

**File:** `src/data/database.py` line 2562 vs `src/core/dispatcher.py` line 620

`get_due_tasks` filters with `avail >= (task.get("min_count") or 0)`, meaning a task with `min_count=0` (or `NULL`) always passes the gate. But `_run_dispatch_loop` checks `available < (task.get("min_count") or 1)`, meaning it would immediately bail on that same task with `0 available`.

This isn't introduced by this PR — it pre-existed — but this refactor is a good moment to align them, since the tick loop now relies on `get_due_tasks` to decide what to spawn (whereas the old `dispatch()` called `count_entities_in_state` inside the same loop anyway). A task that passes the DB gate but immediately bails in the runner spawns a thread, writes a `RUNNING` ledger row, and then immediately writes a `COMPLETED` row with all zeros. Harmless but noisy.

**Recommendation:** Align both to `or 1` (the more conservative threshold), or explicitly document that `min_count=0` means "always eligible, runner decides."

** Susan Note ** 
If I'm reading this right, it's a syntactical difference but logically identical.  Either case, make them both identical syntactically and logically.

---

### Issue 4 — `get_due_tasks` result includes tasks regardless of `freq_hrs` due-time check ℹ️

**File:** `src/data/database.py`, lines 2545–2564

The old `dispatch()` called `get_due_tasks()` and passed the results through — so whatever was there before is unchanged here. But looking at the query:

```sql
SELECT * FROM dispatch_task WHERE auto_mode = 1 ORDER BY id
```

There's no `last_run_at + freq_hrs <= now` filter in the SQL or in the Python loop below it. The tick fires every minute, but a task with `freq_hrs = 24` will be passed to `run_task()` every minute unless it happens to already be in the registry. Since `run_task` guards against duplicate starts (`if task_id in _task_registry: return False`), a *running* task won't double-spawn. But a task that completed 2 minutes ago with `freq_hrs = 24` will be re-spawned on the next tick.

Again, this is a pre-existing behavior — the old scheduler had the same issue (it ran all due tasks every interval). But noting it since the per-task thread model makes the frequency semantics more visible. If `freq_hrs` is supposed to be a minimum cooldown between runs, the tick loop should skip tasks where `last_run_at` is within `freq_hrs` of now.

**Recommendation:** Confirm intended semantics of `freq_hrs`. If it's a cooldown: add the filter. If it's informational-only (the AUTO toggle is the real on/off), document that.

** Susan Note **
freq_hrs is used when fetching the entities related to the task.  entities that have been fetched more recently than freq_hrs hours ago are excluded from the batch claim.  Has nothing to do with loop frequency.

---

## Recommended Actions

| # | Severity | Action |
|---|----------|--------|
| 1 | Discuss | Decide whether the `asyncio_task` registration race is worth fixing; at minimum improve the return value of `cancel_task` in the "not yet ready" case |
| 2 | Fix now | Add a one-line comment in `_tick_loop` explaining that `tick_secs`/`max_auto` are captured once |
| 3 | Discuss | Align `min_count or 0` vs `min_count or 1` between `get_due_tasks` and `_run_dispatch_loop`, or document the intent |
| 4 | Discuss | Confirm `freq_hrs` semantics — cooldown or informational? Add a filter or a doc comment accordingly |
