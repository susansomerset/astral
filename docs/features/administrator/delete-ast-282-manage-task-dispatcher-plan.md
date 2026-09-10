<!-- linear-archive: AST-282 archived 2026-06-03 -->

## Linear archive (AST-282)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-282/manage-task-dispatcher  
**Status at archive:** Done  
**Project:** Astral Administrator  
**Assignee:** susan  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

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

**Dispatcher Logic (**`src/core/dispatcher.py` — new, per ASTRAL_CODE_RULES 3.3):

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

### Comments

_No comments._

---

# ast-282: Manage Task Dispatcher — Plan

## Overview

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

### Design decisions

**Dispatcher lives in `src/cli/dispatcher.py`** with two documented exceptions to the layer rules:

1. **Data layer access** — Dispatcher reads scheduling config (`dispatch_task`) and writes execution bookkeeping (`dispatch_ledger`, entity counts). This is infrastructure, not business logic.
2. **CLI→CLI imports** — Dispatcher imports `run_batch()` functions from sibling CLI modules. It orchestrates them; it belongs among them.

Both exceptions are single-file, documented in the code rules update.

**Direct invocation, not subprocess:** ASTRAL_CODE_RULES 3.5 originally envisioned shelling out to CLI scripts. This plan calls `run_batch()` functions directly — no subprocess overhead, structured return values, direct ctx/batch_id passing. Section 3.5 to be updated when this ships.

**No manual trigger from UI** — future enhancement issue. This plan covers scheduled dispatch only. The admin screen is CRUD for scheduling configuration.

---

## Sub 1: `dispatch_task` table and database functions

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

---

## Sub 2: Candidate-as-raft — ctx threading through the call stack

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

---

## Sub 3: Candidate-scoped batch claims

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

---

## Sub 4: CLI `run_batch()` extraction + `--batch-id` / `--candidate-id` arguments

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

---

## Sub 5: `DISPATCH_TASKS` config and Dispatcher orchestration

**Scope:** Build the Dispatcher orchestrator and its config-driven task registry.

### Config: `DISPATCH_TASKS` in `config.py`

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

### Dispatcher: `src/cli/dispatcher.py`

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

---

## Sub 6: API endpoints for dispatch_task CRUD and nav enable

**Scope:** Admin endpoints for managing the dispatch schedule, plus core wrappers for layering compliance.

### Core wrappers in `src/core/dispatch.py`

Add write-side wrappers (the docstring already notes these were deferred to ast-282):

- `save_dispatch_task(...)` — wraps `database.save_dispatch_task`
- `update_dispatch_task(task_id, **kwargs)` — wraps `database.update_dispatch_task`
- `list_dispatch_tasks()` — wraps `database.list_dispatch_tasks`
- `get_dispatch_task(task_id)` — wraps `database.get_dispatch_task`

These are for the API layer only. The Dispatcher itself calls database directly (documented exception).

### API endpoints

```
GET    /api/admin/dispatch_tasks        — list all dispatch_task rows
POST   /api/admin/dispatch_tasks        — create (candidate_id, task_key, freq_hrs, min_count)
PUT    /api/admin/dispatch_tasks/:id    — update (freq_hrs, min_count, enabled)
```

All `@require_auth`. All call through `src/core/dispatch.py`. Blueprint in `src/ui/api/admin_dispatch_tasks.py`, registered in `src/ui/server.py`.

### Nav enable

Remove `enabled: False` from "Task Dispatcher" in `NAV_CONFIG`.

**Layer:** `src/core/dispatch.py`, `src/ui/api/admin_dispatch_tasks.py`, `src/ui/server.py`, `src/utils/config.py`

---

## Sub 7: Manage Task Dispatcher screen

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

---

## Dependency Graph

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

---

## Code Rules Updates Required

When this feature ships, update `docs/ASTRAL_CODE_RULES.md`:

1. **Section 2.1** — Add `DISPATCH_TASKS` to the config blocks list
2. **Section 3.1** — Add `dispatcher.py` to cli listing
3. **Section 3.3** — Document the two layer exceptions for `dispatcher.py`: data layer access (scheduling infra) and CLI→CLI imports (`run_batch()`)
4. **Section 3.5 "Scheduled jobs"** — Replace subprocess description with direct `run_batch()` invocation; rename `scheduled_actions` → `dispatch_task`; note Railway cron runs CLI directly (no HTTP endpoint)

---

## Files Changed

| File | Subs | Changes |
|------|------|---------|
| `src/data/database.py` | 1, 3 | dispatch_task table + CRUD, count_entities_in_state, candidate_id on batch claims, docstring update |
| `src/utils/config.py` | 5, 6 | DISPATCH_TASKS registry, nav enable |
| `src/external/anthropic.py` | 2 | ctx parameter on do_task, per-call API key |
| `src/core/consult.py` | 2 | ctx parameter on render_verdict, qualify_job_listings, evaluate_jd |
| `src/core/roster.py` | 2, 3 | ctx parameter on prefilter_company; candidate_id on get_new_company_batch |
| `src/core/tracker.py` | 3 | candidate_id on get_new_job_batch |
| `src/core/dispatch.py` | 6 | Write-side wrappers for dispatch_task CRUD |
| `src/core/candidate.py` | — | No changes (get_candidate already returns decrypted raft) |
| `src/cli/dispatcher.py` | 5 | **New file** — Dispatcher orchestrator |
| `src/cli/*.py` (9 files) | 4 | Extract run_batch(), add --batch-id and --candidate-id |
| `src/ui/api/admin_dispatch_tasks.py` | 6 | **New file** — dispatch_task CRUD endpoints |
| `src/ui/server.py` | 6 | Register new blueprint |
| `src/ui/frontend/src/pages/Admin/ScheduledActions.tsx` | 7 | De-stub into full screen |
| `src/ui/frontend/src/App.css` | 7 | Task Dispatcher styles |
| `docs/ASTRAL_CODE_RULES.md` | — | Post-ship update: sections 2.1, 3.1, 3.3, 3.5 |
