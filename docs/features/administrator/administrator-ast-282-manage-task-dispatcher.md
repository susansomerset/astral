# AST-282 — Manage Task Dispatcher
**Component:** administrator  
**Children:** — (single ticket)  
**Linear archived:** AST-282 2026-06-03  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-03-02 18:09 | AST-282 | — | `446eb2db4` | ast-282: Manage Task Dispatcher — full feature |
| 2026-03-02 18:25 | AST-282 | — | `03ce309d2` | ast-282: Address code review feedback |
| 2026-03-02 18:28 | AST-282 | merge | `67d88d150` | Merge pull request #35 from susansomerset/chuckles/ast-282-manage-task-dispatcher |
| 2026-03-02 18:35 | AST-282 | — | `b6be479c9` | ast-282: Use dropdowns for candidate and task selection in add modal |
| 2026-03-02 18:46 | AST-282 | merge | `46b77de74` | Merge pull request #36 from susansomerset/chuckles/ast-282-manage-task-dispatcher |

## Epic — AST-282
_Archived: 2026-06-03 · Linear URL: https://linear.app/astralcareermatch/issue/AST-282/manage-task-dispatcher · Status at archive: Done · Project: Astral Administrator · Assignee: susan · Priority / estimate: High / 8_

### Original brief

Replace the Scheduled Actions stub with a fully operational Task Dispatcher. A thin Railway cron job fires every few minutes and calls the Dispatcher endpoint. All scheduling logic lives in [dispatcher.py](<http://dispatcher.py>) and the dispatch_task table. Introduces the candidate-as-raft pattern, candidate-scoped batch processing, and execution_session record ownership.

**Acceptance Criteria:**

**Candidate as Raft:**

* The candidate record returned by `get_candidate()` serves as the context object (the raft) — no new dataclass needed
* `candidate.get_api_key(candidate)` decrypts and returns `candidate_api_key`, raises `ValueError` if missing — no fallback to system key
* `ctx` (the candidate record dict) passes through the call stack: Dispatcher → [consult.py](<http://consult.py>) → do_task
* `consult.py` accepts `ctx` and forwards to `do_task` — consult does not inspect or use ctx beyond forwarding
* `do_task` accepts `ctx`, uses `ctx['candidate_api_key']` when task `requires_candidate_key=True` per CONFIG_TASKS
* `ctx['candidate_data']` provides all candidate content for token resolution in [anthropic.py](<http://anthropic.py>)

`get_*_batch` Function Updates:

* `claim_job_batch()` and `claim_company_batch()` in [database.py](<http://database.py>) accept optional `candidate_id` filter
* All batch queries filter by `candidate_id` when provided
* `tracker.py` and `roster.py` `get_new_*_batch()` functions accept and pass `candidate_id` from ctx

**CLI** `--batch-id` Argument (all batch CLIs):

* Each CLI accepts an optional `--batch-id` argument
* If provided (Dispatcher-initiated): use the passed batch_id
* If not provided (manual run): generate a new UUID as today
* This is the only change required to existing CLI files

`dispatch_task` Table (new):

* `id` — PK
* `candidate_id` — TEXT, FK to candidate
* `task_key` — TEXT, references CONFIG_TASKS key
* `last_run_at` — TIMESTAMP (nullable)
* `freq_hrs` — FLOAT (how often this task should run)
* `min_count` — INTEGER (minimum records in trigger state required to actually fire)
* `batch_id` — TEXT (nullable — set when claimed by Dispatcher to prevent double-dispatch, cleared on completion)
* `enabled` — BOOL
* `updated_at` — TIMESTAMP

**Example rows (consult_joblist for one candidate):**

* `freq_hrs=24, min_count=1` — daily floor run regardless of volume
* `freq_hrs=6, min_count=90` — high-volume trigger when NEW jobs accumulate quickly

**Dispatcher Logic (**`src/core/dispatcher.py` — new, per ASTRAL_CODE_RULES 3.3): *(plan later moved this to `src/cli/dispatcher.py` — see Design decisions)*

`get_due_tasks()`:

* Query dispatch_task WHERE `now() > last_run_at + freq_hrs` AND `batch_id IS NULL` AND `enabled = TRUE`
* Claim due records by setting `batch_id` on each (prevents cron double-dispatch)
* Return claimed records

`dispatch()` — main entry point called by cron endpoint:

1. Call `get_due_tasks()` to get claimed dispatch_task records
2. For each claimed record:
   a. Get `trigger_state` from CONFIG_TASKS for this task_key
   b. Query count of records in trigger_state for this candidate_id (via database)
   c. If count < `min_count`: skip, clear batch_id on dispatch_task record, continue
   d. Fetch candidate record (the raft) via `candidate.get_candidate(candidate_id)`
   e. Validate `candidate.get_api_key(candidate)` — skip with error log if missing
   f. Write `execution_session` record (status=RUNNING, batch_id, task_key, candidate_id, started_at)
   g. Invoke appropriate batch function directly (not subprocess) passing ctx + batch_id
   h. Await summary response from batch function
   i. Update `execution_session` (status=COMPLETED/FAILED, counts, completed_at, better_stack_url)
   j. Update `dispatch_task`: clear batch_id, set last_run_at=now()

**Manage Task Dispatcher Screen (UI — Admin > Task Dispatcher):**

* ListPage showing all dispatch_task records
* Columns: candidate_id, task_key, enabled toggle, freq_hrs, min_count, last_run_at, next_run_at (computed), currently_running indicator
* Edit row → modal to update freq_hrs, min_count, enabled
* Add row → modal to create new dispatch_task (select candidate, task_key, set freq_hrs and min_count)
* Manual trigger button per row (dispatch immediately regardless of threshold — for testing)

**Cron Setup:**

* Thin Railway cron job (every 2-3 minutes) calls POST /api/dispatcher/run
* Endpoint calls `dispatcher.dispatch()` and returns summary JSON
* No logic in the cron itself — all logic in [dispatcher.py](<http://dispatcher.py>)

**API Endpoints:**

* POST /api/dispatcher/run — called by cron, triggers dispatch cycle
* GET /api/admin/dispatch_tasks — list all dispatch_task records
* POST /api/admin/dispatch_tasks — create new dispatch_task row
* PUT /api/admin/dispatch_tasks/:id — update freq_hrs, min_count, enabled
* POST /api/admin/dispatch_tasks/:id/trigger — manual trigger

**Nav:**

* Enable Task Dispatcher route (remove `enabled: False`) — rename handled in Manage Candidates issue

**Database:**

* dispatch_task table: CREATE TABLE as above
* execution_session table: CREATE TABLE (see View Execution History issue)
* [database.py](<http://database.py>) module docstring updated per ASTRAL_CODE_RULES 1.1

#### Comments

_No comments._

### Plan — ast-282: Manage Task Dispatcher

#### Overview

The Task Dispatcher is the automation heart of ASTRAL. It replaces manual CLI invocations with a database-driven scheduler: a Railway cron job fires the Dispatcher on a fixed interval, the Dispatcher checks which tasks are due, and runs them.

**Already built (from ast-281, ast-285, and prior features):**
- `dispatch_ledger` table + save/update/get/list functions in `database.py`
- `app_log` table + `add_log_entry` / `list_log_entries` in `database.py`
- `DatabaseLogHandler` with buffering + `log_batch_id` contextvar in `logging.py`
- `flush_log_buffer()` for explicit flush at batch end
- Core read-side wrappers in `src/core/dispatch.py`
- API endpoints for dispatch_ledger read + logs in `src/ui/api/admin_dispatch.py`
- Execution History UI screen (`PerformanceMonitor.tsx`)
- Agent Timesheets screen + API
- `candidate_api_key` encryption/decryption — `_parse_candidate_row()` decrypts inline, `get_candidate()` returns the raft with plaintext key
- `TASK_CONFIG` entries already have `requires_candidate_key` and `trigger_state` fields (all `trigger_state: None` currently)
- `do_task()` already accepts `candidate_data` for token resolution

#### Design decisions

**Dispatcher lives in `src/cli/dispatcher.py`** with two documented exceptions to the layer rules:

1. **Data layer access** — Dispatcher reads scheduling config (`dispatch_task`) and writes execution bookkeeping (`dispatch_ledger`, entity counts). This is infrastructure, not business logic.
2. **CLI→CLI imports** — Dispatcher imports `run_batch()` functions from sibling CLI modules. It orchestrates them; it belongs among them.

Both exceptions are single-file, documented in the code rules update.

**Direct invocation, not subprocess:** ASTRAL_CODE_RULES 3.5 originally envisioned shelling out to CLI scripts. This plan calls `run_batch()` functions directly — no subprocess overhead, structured return values, direct ctx/batch_id passing. Section 3.5 to be updated when this ships.

**No manual trigger from UI** — future enhancement issue. This plan covers scheduled dispatch only. The admin screen is CRUD for scheduling configuration.

#### Sub 1: `dispatch_task` table and database functions

**Scope:** Create the scheduling table and its CRUD functions.

**Schema:**

```sql
CREATE TABLE dispatch_task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT NOT NULL,        -- FK to candidate.astral_candidate_id
    task_key TEXT NOT NULL,             -- matches a DISPATCH_TASKS key (see Sub 5)
    last_run_at TIMESTAMP,             -- NULL until first run
    freq_hrs REAL NOT NULL,            -- minimum hours between runs
    min_count INTEGER NOT NULL,        -- skip if fewer than this many entities in trigger_state
    batch_id TEXT,                      -- non-NULL = currently claimed by Dispatcher
    enabled INTEGER NOT NULL DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Database functions:**
- `_ensure_dispatch_task_schema(conn)` — idempotent, standard pattern
- `save_dispatch_task(candidate_id, task_key, freq_hrs, min_count, enabled=True)` — INSERT, returns new id
- `get_dispatch_task(task_id)` — single record by PK
- `list_dispatch_tasks()` — all rows, newest first
- `update_dispatch_task(task_id, **kwargs)` — column-whitelisted update (same pattern as `update_dispatch_ledger`)
- `get_due_tasks()` — returns tasks where scheduling criteria are met:
  ```sql
  WHERE enabled = 1 AND batch_id IS NULL
  AND (last_run_at IS NULL OR last_run_at < datetime('now', '-' || freq_hrs || ' hours'))
  ```
- `claim_dispatch_task(task_id, batch_id)` — SET batch_id WHERE id = ? AND batch_id IS NULL (atomic claim, returns bool)
- `release_dispatch_task(task_id)` — SET batch_id = NULL, last_run_at = now
- `count_entities_in_state(entity_type, state, candidate_id)` — `SELECT COUNT(*)` from job or company table, filtered by state and candidate_id

**Update `database.py` module docstring** per ASTRAL_CODE_RULES 1.1 — add `dispatch_task` to table inventory.

**Layer:** `src/data/database.py`

#### Sub 2: Candidate-as-raft — ctx threading through the call stack

**Scope:** Thread the candidate record dict (`ctx`) through the call stack so every layer has access to candidate data and API key. The candidate dict from `get_candidate()` IS the context object — no new dataclass.

**Key insight:** `_parse_candidate_row()` already decrypts `candidate_api_key` inline. The raft carries plaintext in memory. No separate `get_api_key()` call needed.

**Changes to core functions — add optional `ctx` parameter:**

- `consult.render_verdict(task_type, astral_job_id, ctx=None)` — forwards `ctx` to `do_task`
- `consult.qualify_job_listings(batch_id, jobs, ctx=None)` — forwards `ctx` to `do_task`
- `consult.evaluate_jd(job, ctx=None)` — forwards `ctx` to `do_task`
- `roster.prefilter_company(short_name, company_website, ctx=None)` — forwards `ctx` to `do_task`

Core functions pass ctx to `do_task` but do not inspect it beyond forwarding. Making `ctx` optional preserves backward compatibility — existing CLI scripts continue to work without changes until Sub 4.

**Changes to `do_task` in `anthropic.py`:**

- Add `ctx` parameter (optional, default `None`)
- When `ctx` is provided: extract `candidate_data = ctx.get('candidate_data', {})` for token resolution (replaces the existing `candidate_data` parameter)
- When `requires_candidate_key=True` and `ctx` provides `candidate_api_key`: use it as the Anthropic API key for this call (instantiate a per-call `Anthropic(api_key=...)` client)
- Backward-compatible: existing `candidate_data` parameter still works if `ctx` is not provided

**Signature change:**

```python
async def do_task(
    task_key: str,
    live_content: Optional[str] = None,
    index: Optional[str] = None,
    candidate_data: Optional[Dict[str, Any]] = None,  # kept for backward compat
    ctx: Optional[Dict[str, Any]] = None,              # new: full candidate raft
    debug: bool = False,
) -> Dict[str, Any]:
```

When `ctx` is provided, it takes precedence over `candidate_data` for token resolution.

**Layer:** `src/core/consult.py`, `src/core/roster.py`, `src/external/anthropic.py`

#### Sub 3: Candidate-scoped batch claims

**Scope:** Make `candidate_id` an optional parameter on batch claim functions so Dispatcher-initiated runs are single-candidate scoped.

**Changes to `database.py`:**

- `claim_job_batch(batch_id, state, limit, sort_by, candidate_id=None)` — when provided, adds `AND company IN (SELECT short_name FROM company WHERE candidate_id = ?)` to the WHERE clause
- `set_company_batch(...)` — add optional `candidate_id` parameter; when provided, adds `AND candidate_id = ?` to the WHERE clause
- `claim_company_batch(...)` — pass through `candidate_id`

**Changes to core:**

- `tracker.get_new_job_batch(state, limit, candidate_id=None)` — passes `candidate_id` to `claim_job_batch`
- `roster.get_new_company_batch(state, limit, candidate_id=None)` — passes `candidate_id` to `claim_company_batch`

All parameters optional — existing CLI scripts continue to work unscoped.

**Layer:** `src/data/database.py`, `src/core/tracker.py`, `src/core/roster.py`

#### Sub 4: CLI `run_batch()` extraction + `--batch-id` / `--candidate-id` arguments

**Scope:** Refactor each batch CLI to extract the batch loop into an importable `run_batch()` function, and add optional arguments for Dispatcher-initiated and manual candidate-scoped runs.

**Refactor pattern for each CLI:**

```python
# Before: everything in main()
async def main():
    args = parser.parse_args()
    # ... 40 lines of batch loop ...

# After: batch logic in run_batch(), main() is a thin wrapper
async def run_batch(
    ctx: Optional[Dict] = None,
    batch_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, int]:
    """Importable batch function. Returns summary dict."""
    # ... same batch loop, parameterized ...
    return {"total_processed": ..., "total_passed": ...,
            "total_failed": ..., "total_errors": ...}

async def main():
    args = parser.parse_args()
    ctx = candidate.get_candidate(args.candidate_id) if args.candidate_id else None
    summary = await run_batch(ctx=ctx, batch_id=args.batch_id, limit=args.limit)
    logger.info("Done: %s", summary)
```

**`run_batch()` responsibilities:**
- Accept `ctx` (optional) — pass to core functions for candidate-scoped claims and API key threading
- Accept `batch_id` (optional) — use if provided, generate UUID if not
- Accept `limit` (optional) — use if provided, fall back to config default
- Set `log_batch_id` contextvar when `batch_id` is provided (for automatic log tagging)
- Call `flush_log_buffer()` at end
- Return structured summary dict

**Arguments added to each CLI:**
- `--batch-id` (optional) — If provided, use it; otherwise generate UUID
- `--candidate-id` (optional) — If provided, fetch candidate and pass ctx

**Files:** `prefilter.py`, `locate_job_page.py`, `parse_job_list.py`, `gaze_batch.py`, `qualify_batch.py`, `evaluate_jd_batch.py`, `consult_get_batch.py`, `consult_do_batch.py`, `consult_like_batch.py`

**Layer:** `src/cli/` (all batch CLI scripts)

#### Sub 5: `DISPATCH_TASKS` config and Dispatcher orchestration

**Scope:** Build the Dispatcher orchestrator and its config-driven task registry.

##### Config: `DISPATCH_TASKS` in `config.py`

Maps task keys to execution details. No `batch_size` — resolved from existing config (CONSULT_CONFIG, COMPANY_STATES) to avoid duplication:

```python
DISPATCH_TASKS = {
    "prefilter": {
        "entity_type": "company",
        "trigger_state": "NEW",
        "cli_module": "src.cli.prefilter",
    },
    "locate_job_page": {
        "entity_type": "company",
        "trigger_state": "WATCH",
        "cli_module": "src.cli.locate_job_page",
    },
    "parse_job_list": {
        "entity_type": "company",
        "trigger_state": "JOB_PAGE",
        "cli_module": "src.cli.parse_job_list",
    },
    "gaze": {
        "entity_type": "company",
        "trigger_state": "WATCH",
        "cli_module": "src.cli.gaze_batch",
    },
    "qualify_job_listings": {
        "entity_type": "job",
        "trigger_state": "NEW",
        "cli_module": "src.cli.qualify_batch",
    },
    "evaluate_jd": {
        "entity_type": "job",
        "trigger_state": "PASSED_JOBLIST",
        "cli_module": "src.cli.evaluate_jd_batch",
    },
    "consult_get": {
        "entity_type": "job",
        "trigger_state": "PASSED_JD",
        "cli_module": "src.cli.consult_get_batch",
    },
    "consult_do": {
        "entity_type": "job",
        "trigger_state": "PASSED_GET",
        "cli_module": "src.cli.consult_do_batch",
    },
    "consult_like": {
        "entity_type": "job",
        "trigger_state": "PASSED_DO",
        "cli_module": "src.cli.consult_like_batch",
    },
}
```

##### Dispatcher: `src/cli/dispatcher.py`

**Documented layer exceptions:**
1. Imports `src/data/database` for scheduling infrastructure (dispatch_task, dispatch_ledger, entity counts)
2. Imports sibling CLI modules for `run_batch()` functions

**`dispatch()` — main entry point:**

```python
async def dispatch() -> List[Dict]:
    """Called by Railway cron. Returns list of run summaries."""
    due_tasks = database.get_due_tasks()
    summaries = []

    for task in due_tasks:
        task_key = task["task_key"]
        candidate_id = task["candidate_id"]
        dispatch_cfg = DISPATCH_TASKS.get(task_key)
        if not dispatch_cfg:
            continue

        # Atomic claim — prevents double-dispatch if cron overlaps
        batch_id = str(uuid4())
        if not database.claim_dispatch_task(task["id"], batch_id):
            continue

        # Check trigger_state count meets min_count threshold
        count = database.count_entities_in_state(
            dispatch_cfg["entity_type"], dispatch_cfg["trigger_state"], candidate_id)
        if count < task["min_count"]:
            database.release_dispatch_task(task["id"])
            continue

        # Fetch candidate raft (carries decrypted API key)
        ctx = candidate.get_candidate(candidate_id)
        if not ctx or not ctx.get("candidate_api_key"):
            logger.error("Skipping %s/%s — no candidate or API key", task_key, candidate_id)
            database.release_dispatch_task(task["id"])
            continue

        # Write dispatch_ledger + set log contextvar
        database.save_dispatch_ledger(batch_id, task_key, candidate_id, now_iso(), "RUNNING")
        log_batch_id.set(batch_id)

        try:
            cli_module = importlib.import_module(dispatch_cfg["cli_module"])
            summary = await cli_module.run_batch(ctx=ctx, batch_id=batch_id)
            database.update_dispatch_ledger(batch_id,
                status="COMPLETED", completed_at=now_iso(), **summary)
        except Exception as e:
            logger.error("Dispatch %s failed: %s", task_key, e)
            database.update_dispatch_ledger(batch_id,
                status="FAILED", completed_at=now_iso())
            summary = {"total_processed": 0, "total_passed": 0,
                        "total_failed": 0, "total_errors": 1}
        finally:
            flush_log_buffer()
            log_batch_id.set(None)
            database.release_dispatch_task(task["id"])

        summaries.append({"task_key": task_key, "batch_id": batch_id, **summary})

    return summaries
```

**CLI entry point:**

```python
async def main():
    summaries = await dispatch()
    for s in summaries:
        logger.info("  %s batch=%s processed=%d passed=%d failed=%d errors=%d",
                     s["task_key"], s["batch_id"], s["total_processed"],
                     s["total_passed"], s["total_failed"], s["total_errors"])
    logger.info("Dispatch complete: %d tasks run", len(summaries))
```

Railway cron runs `python -m src.cli.dispatcher` directly. No HTTP endpoint needed.

**Layer:** `src/cli/dispatcher.py`, `src/utils/config.py` (DISPATCH_TASKS)

#### Sub 6: API endpoints for dispatch_task CRUD and nav enable

**Scope:** Admin endpoints for managing the dispatch schedule, plus core wrappers for layering compliance.

##### Core wrappers in `src/core/dispatch.py`

Add write-side wrappers (the docstring already notes these were deferred to ast-282):

- `save_dispatch_task(...)` — wraps `database.save_dispatch_task`
- `update_dispatch_task(task_id, **kwargs)` — wraps `database.update_dispatch_task`
- `list_dispatch_tasks()` — wraps `database.list_dispatch_tasks`
- `get_dispatch_task(task_id)` — wraps `database.get_dispatch_task`

These are for the API layer only. The Dispatcher itself calls database directly (documented exception).

##### API endpoints

```
GET    /api/admin/dispatch_tasks        — list all dispatch_task rows
POST   /api/admin/dispatch_tasks        — create (candidate_id, task_key, freq_hrs, min_count)
PUT    /api/admin/dispatch_tasks/:id    — update (freq_hrs, min_count, enabled)
```

All `@require_auth`. All call through `src/core/dispatch.py`. Blueprint in `src/ui/api/admin_dispatch_tasks.py`, registered in `src/ui/server.py`.

##### Nav enable

Remove `enabled: False` from "Task Dispatcher" in `NAV_CONFIG`.

**Layer:** `src/core/dispatch.py`, `src/ui/api/admin_dispatch_tasks.py`, `src/ui/server.py`, `src/utils/config.py`

#### Sub 7: Manage Task Dispatcher screen

**Scope:** De-stub `ScheduledActions.tsx` into a working Task Dispatcher management screen.

**Layout:**

- ListPage showing all `dispatch_task` records from `GET /api/admin/dispatch_tasks`
- **Columns:** candidate_id, task_key, enabled (toggle), freq_hrs, min_count, last_run_at, next_run_at (computed: `last_run_at + freq_hrs`), currently_running indicator (batch_id not null)
- **Edit row** → modal to update freq_hrs, min_count, enabled
- **Add row** → modal to create new dispatch_task (select candidate, select task_key from `DISPATCH_TASKS` keys, set freq_hrs and min_count)

**URL-driven filters** (consistent with Agent Timesheets and Execution History):
- candidate_id dropdown, task_key dropdown — derived from loaded data

**Styling:** Reuse `.admin-filters`, `.list-page-*` CSS classes.

**Out of scope:** Manual trigger button — future enhancement issue.

**Layer:** `src/ui/frontend/src/pages/Admin/ScheduledActions.tsx`, `src/ui/frontend/src/App.css`

#### Dependency Graph

```
Sub 1 (dispatch_task table)  ─────────────────────┐
Sub 2 (ctx threading)        ─────────────────────┤
Sub 3 (candidate-scoped batch claims)  ───────────┤──► Sub 5 (Dispatcher in CLI)
Sub 4 (CLI run_batch refactor + args)  ───────────┘          │
                                                              ▼
                                                   Sub 6 (API CRUD + nav)
                                                              │
                                                              ▼
                                                   Sub 7 (UI screen)
```

Subs 1–4 are independent of each other and can be built in any order. Sub 5 depends on all four. Subs 6 and 7 are sequential after Sub 5.

#### Code Rules Updates Required

When this feature ships, update `docs/ASTRAL_CODE_RULES.md`: *(historical — `docs/ASTRAL_CODE_RULES.md` was later deleted in `44b7d102b`, 2026-09-10; canon carries the law now)*

1. **Section 2.1** — Add `DISPATCH_TASKS` to the config blocks list
2. **Section 3.1** — Add `dispatcher.py` to cli listing
3. **Section 3.3** — Document the two layer exceptions for `dispatcher.py`: data layer access (scheduling infra) and CLI→CLI imports (`run_batch()`)
4. **Section 3.5 "Scheduled jobs"** — Replace subprocess description with direct `run_batch()` invocation; rename `scheduled_actions` → `dispatch_task`; note Railway cron runs CLI directly (no HTTP endpoint)

### Code review (`446eb2d`)

Seven-subissue feature delivered in a single commit:
1. `dispatch_task` table with CRUD, `get_due_tasks`, atomic `claim/release`, and `count_entities_in_state` in `database.py`
2. `ctx` (candidate raft) threading through `do_task`, `render_verdict`, `qualify_job_listings`, `evaluate_jd`, `prefilter_company` with per-call Anthropic API key override
3. `candidate_id` scoping on `set_company_batch`, `claim_company_batch`, `claim_job_batch`, `get_new_company_batch`, `get_new_job_batch`
4. All 9 batch CLIs refactored: `run_batch()` extracted, `--batch-id` and `--candidate-id` args added, `log_batch_id` + `flush_log_buffer` integration
5. `DISPATCH_TASKS` config registry (9 entries) + `src/cli/dispatcher.py` orchestrator
6. Core wrappers in `dispatch.py`, API blueprint (`admin_dispatch_tasks.py`) with GET/POST/PUT, nav enabled
7. De-stubbed `ScheduledActions.tsx` — full Task Dispatcher screen with filters, sortable table, inline enabled toggle, add/edit modals

#### The Good

1. **Dispatcher orchestration loop is clean and correct.** The `dispatch()` flow — `get_due_tasks` → atomic claim → entity count check → ctx fetch → ledger write → `importlib.import_module` → `run_batch()` → ledger update → release — follows the plan exactly. The `finally` block always releases the task and flushes logs, even on exception. The `summary` dict is pre-initialized before `try`, so the `except` branch can safely override it.
2. **`claim_dispatch_task` is properly atomic.** `UPDATE ... WHERE id = ? AND batch_id IS NULL` with `rowcount > 0` check. If a cron overlap fires two dispatchers simultaneously, only one will claim each task. This is the correct pattern for SQLite advisory locking.
3. **`update_dispatch_task` is column-whitelisted.** Unlike `update_dispatch_ledger` (ast-281 review issue #2), this function validates `kwargs` against `_DISPATCH_TASK_UPDATE_COLS` and raises `ValueError` on unknown keys. Typos caught at call time instead of producing `OperationalError`. Good improvement over the ledger pattern.
4. **`ctx` threading is backward-compatible across all layers.** Every function that gains `ctx` has it as an optional `=None` parameter. The three consult functions, `prefilter_company`, `get_new_company_batch`, `get_new_job_batch`, `claim_job_batch`, `set_company_batch` — all additive. Existing CLI scripts and tests continue to work unchanged.
5. **`do_task` API key override is precise.** Only triggers when both `ctx` is provided AND `requires_candidate_key` is True. Creates a per-call `Anthropic(api_key=...)` client — correctly avoids mutating the shared `_client` singleton. The `cd = (ctx.get("candidate_data") or {}) if ctx else (candidate_data or {})` precedence is clear and the old `candidate_data` param still works.
6. **`candidate_id` scoping on job claims uses the correct indirect pattern.** `claim_job_batch` adds `AND company IN (SELECT short_name FROM company WHERE candidate_id = ?)` because jobs don't have a direct `candidate_id` column — they're scoped via their parent company. Same subquery pattern used in `count_entities_in_state`. Consistent.
7. **`run_batch()` extraction is consistent across all 9 CLIs.** Same signature (`ctx`, `batch_id`, `limit`), same return type (`Dict[str, int]` with `total_processed/passed/failed/errors`), same `log_batch_id.set()` + `flush_log_buffer()` bookend pattern. `main()` is reduced to argparse + delegate.
8. **UI uses `admin-filters` CSS class.** Fixes the hidden coupling issue flagged in the ast-281 review (which used `timesheet-filters`). The Task Dispatcher screen reuses the shared admin filter styling correctly.
9. **API layer is properly hardened.** POST validates required fields and returns 400 with specifics. PUT whitelists exactly `freq_hrs`, `min_count`, `enabled` — cannot change `candidate_id` or `task_key` after creation. Type coercion (`float`, `int`, `int(bool(...))`) is done in the API layer before passing to core.

#### Issues to Address

##### 1. BUG: `ctx` not threaded through `find_job_page`, `parse_job_list`, or gazer-internal AI calls

The plan calls out ctx threading for the full call stack, but three `run_batch()` functions don't pass `ctx` to the core functions that make AI calls:

- **`locate_job_page.py`** → calls `find_job_page(url, short_name, company_website)` — `find_job_page` doesn't accept `ctx`, so `do_task("find_job_site")`, `do_task("vet_job_list")`, and `do_task("select_culture_pages")` all fire without a candidate API key or candidate data for token resolution.
- **`parse_job_list.py`** → calls `roster.parse_job_list(company, context)` — which internally calls `_fetch_parse_job_list` → `do_task("parse_job_list")` without ctx.

All of these tasks have `requires_candidate_key: True` in `TASK_CONFIG`. When dispatched, they'll use the environment API key instead of the candidate's key, and the warning "requires_candidate_key is True but no candidate_data provided — tokens will resolve to empty" will fire.

The tasks that DO thread ctx correctly: `prefilter.py` → `prefilter_company(ctx=ctx)`, `qualify_batch.py` → `qualify_job_listings(ctx=ctx)`, `evaluate_jd_batch.py` → `evaluate_jd(ctx=ctx)`, `consult_*_batch.py` → `render_verdict(ctx=ctx)`.

**Fix:** Add `ctx` parameter to `find_job_page`, `_fetch_parse_job_list`/`parse_job_list` in `roster.py`, and forward it to their `do_task` calls. Update `locate_job_page.py` and `parse_job_list.py` `run_batch()` to pass `ctx` through.

##### 2. No UNIQUE constraint on `(candidate_id, task_key)` — allows duplicate scheduling

The `dispatch_task` schema has no uniqueness constraint. The POST endpoint doesn't check for existing rows with the same `(candidate_id, task_key)` pair. An admin can accidentally create two scheduling entries for the same candidate + task, and `get_due_tasks()` will return both — the dispatcher will run the same task twice per cycle.

**Fix:** Add `UNIQUE(candidate_id, task_key)` to the schema, or add a check-before-insert in `save_dispatch_task` / the API POST handler.

##### 3. `--limiterror` argument accepted but silently ignored in `locate_job_page.py`

The CLI parser still defines `--limiterror`:
```python
parser.add_argument("--limiterror", type=int, metavar="N", help="Stop after N outcomes of ERROR only")
```

But `run_batch()` doesn't implement error-limit logic. The old `main()` tracked `error_limit_count` and broke out of the batch loop on reaching the limit. After refactoring, `main()` delegates entirely to `run_batch()`, which has no awareness of this argument.

Either remove the argument from the parser or add `error_limit` as an optional parameter on `run_batch()`.

##### 4. `run_batch()` double-clears `log_batch_id` and double-flushes when called from dispatcher

Each `run_batch()` ends with `flush_log_buffer()` + `log_batch_id.set(None)`, and the dispatcher's `finally` block does the same. Double-flush and double-clear are harmless (flush is a no-op if buffer is empty, set(None) is idempotent). But it means when called standalone via CLI, `run_batch()` correctly manages its own cleanup, and when called from dispatcher, the dispatcher's cleanup is redundant. This is the right design — each layer is self-sufficient. Just noting it's intentional.

##### 5. `debug` parameter dropped from `gaze_batch` and `locate_job_page` `run_batch()`

The old `main()` in `gaze_batch.py` passed `debug=args.debug` to `process_gazer_batch()`. The new `run_batch()` calls `process_gazer_batch(bid, companies)` without `debug`. Same for `locate_job_page.py`. When invoked from the dispatcher, debug output is never needed. But when invoked from CLI with `--debug`, the flag is parsed but never forwarded. Low priority — debug is a development aid, not a production concern.

**Fix:** Add optional `debug: bool = False` to `run_batch()` and forward it. `main()` passes `debug=args.debug`.

#### Minor Notes

- **`release_dispatch_task` sets `last_run_at` on release, not on claim.** This is correct — the freq_hrs cooldown starts from when the task finished, so the next run is scheduled relative to completion, not start.
- **`get_due_tasks` uses `CAST(freq_hrs AS TEXT)` in the datetime modifier.** The `CAST` ensures `freq_hrs` (REAL) converts to text for string concatenation; handles fractional hours (`datetime('now', '-1.5 hours')` is valid SQLite).
- **`count_entities_in_state` validates `entity_type` with a hard `ValueError`.** Only `"company"` and `"job"` accepted. Acceptable for now since all 9 dispatch tasks are company or job entities.
- **Dispatcher imports `get_candidate` from `database` directly** (not through core) — the documented layer exception.
- **`gaze` and `locate_job_page` share `trigger_state: "WATCH"`.** Both fire on WATCH companies; they run independently and each claims separate batches via the atomic claim. No conflict.
- **Add modal uses free-text inputs for `candidate_id` and `task_key`.** For an admin-only tool this is acceptable, but dropdowns from `list_candidates()` and `DISPATCH_TASKS.keys()` would prevent typos. *(Later addressed by `b6be479c9`.)*
- **`save_dispatch_task` returns `lastrowid`.** The API returns `{"id": task_id}` with 201.

#### Summary

Well-executed 21-file feature that lands the core automation engine. The dispatcher loop, atomic claiming, and ctx/API-key threading design are all solid. The CLI refactoring is impressively consistent across 9 files. **Issue #1** (ctx not threaded through `find_job_page` and `parse_job_list`) is the most important — those tasks will use the wrong API key and get empty token resolution when dispatched. **Issue #2** (missing unique constraint) is a data integrity risk that should be fixed before production use. Everything else is minor.

#### Changes Applied (`03ce309d2`)

**Fix #1 — ctx threading through find_job_page and parse_job_list:**
- Added `ctx` parameter to `find_job_page`, `_fetch_jobsite_page_options`, `_fetch_jobsite_analysis` in `roster.py`
- Forwarded `ctx=ctx` to all `do_task("find_job_site")`, `do_task("vet_job_list")` calls
- Added `ctx` to all 4 recursive `find_job_page` calls
- Added `ctx` parameter to `parse_job_list` and `_fetch_parse_job_list` in `roster.py`, forwarded to `do_task("parse_job_list")`
- Updated `locate_job_page.py` to pass `ctx=ctx` to `find_job_page`
- Updated `parse_job_list.py` to pass `ctx=ctx` to `parse_job_list`

**Fix #2 — UNIQUE constraint:** Added `UNIQUE(candidate_id, task_key)` to `dispatch_task` CREATE TABLE in `database.py`

**Fix #3 — `--limiterror` wired into `run_batch()`:** Added `error_limit` parameter to `locate_job_page.py`'s `run_batch()` with early-break logic matching the original `main()`; `main()` passes `error_limit=args.limiterror`

**Fix #4 — Double-clear:** Intentional, no action needed.

**Fix #5 — `debug` parameter restored:** Added `debug: bool = False` to `locate_job_page.py` and `gaze_batch.py` `run_batch()`, forwarded to `find_job_page(debug=debug)` / `process_gazer_batch(debug=debug)`; both `main()` now pass `debug=args.debug`.

**Follow-up (`b6be479c9`):** Add-modal `candidate_id` / `task_key` fields changed from free-text to dropdowns.

### Files changed (plan vs actual)

Plan "Files Changed" table → actual across `446eb2db4` (full feature), `03ce309d2` (review fixes), `b6be479c9` (dropdowns). Era path convention was `ui/…` (not `src/ui/…`).

| | file | planned (subs) | actual |
|---|---|---|---|
| ✓ | `src/data/database.py` | 1, 3 — dispatch_task table + CRUD, `count_entities_in_state`, candidate_id on batch claims, docstring | `446eb2db4` `03ce309d2` |
| ✓ | `src/utils/config.py` | 5, 6 — `DISPATCH_TASKS` registry, nav enable | `446eb2db4` |
| ✓ | `src/external/anthropic.py` | 2 — `ctx` param on `do_task`, per-call API key | `446eb2db4` |
| ✓ | `src/core/consult.py` | 2 — `ctx` param on `render_verdict`, `qualify_job_listings`, `evaluate_jd` | `446eb2db4` |
| ✓ | `src/core/roster.py` | 2, 3 — `ctx` on `prefilter_company`; `candidate_id` on `get_new_company_batch`; (review) `ctx` on `find_job_page` / `parse_job_list` | `446eb2db4` `03ce309d2` |
| ✓ | `src/core/tracker.py` | 3 — `candidate_id` on `get_new_job_batch` | `446eb2db4` |
| ✓ | `src/core/dispatch.py` | 6 — write-side wrappers for dispatch_task CRUD | `446eb2db4` |
| ⚠ not touched | `src/core/candidate.py` | — plan: "No changes (get_candidate already returns decrypted raft)" | — |
| ✓ | `src/cli/dispatcher.py` (new) | 5 — Dispatcher orchestrator | `446eb2db4` |
| ✓ | `src/cli/*.py` (9 batch CLIs) | 4 — extract `run_batch()`, add `--batch-id` / `--candidate-id` | `446eb2db4` (`consult_{do,get,like}_batch`, `evaluate_jd_batch`, `gaze_batch`, `locate_job_page`, `parse_job_list`, `prefilter`, `qualify_batch`); `03ce309d2` (`gaze_batch`, `locate_job_page`, `parse_job_list`) |
| ✓ | `src/ui/api/admin_dispatch_tasks.py` (new) | 6 — dispatch_task CRUD endpoints | `446eb2db4` (`ui/api/…`) `b6be479c9` |
| ✓ | `src/ui/server.py` | 6 — register blueprint | `446eb2db4` (`ui/server.py`) |
| ✓ | `src/ui/frontend/src/pages/Admin/ScheduledActions.tsx` | 7 — de-stub into full screen | `446eb2db4` `b6be479c9` (`ui/frontend/…`) |
| ✓ | `src/ui/frontend/src/App.css` | 7 — Task Dispatcher styles | *(folded into ScheduledActions commit; no separate App.css hunk recorded)* |
| ✗ do-not-edit | `docs/ASTRAL_CODE_RULES.md` | — plan: post-ship update sections 2.1/3.1/3.3/3.5 | — (not touched in these commits) |
| | _plan/review docs_ | — | `ast-282-manage-task-dispatcher-{plan,review}.md` (`446eb2db4` `03ce309d2`) |

_Implementation detail may live in git history on `origin/dev`._
