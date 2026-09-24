# AST-1705 — qualify_meteorite is failing

<!-- linear-archive: AST-1705 archived 2026-09-24 -->

## Linear archive (AST-1705)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1705/qualify-meteorite-is-failing  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

`qualify_meteorite` dispatch claims a job batch, then `tracker.get_new_job_batch` → `database.get_job_batch` runs `SELECT j.*, c.job_site FROM job j LEFT JOIN company c ON j.company = c.short_name …`. After [AST-1701](https://linear.app/astralcareermatch/issue/AST-1701/job-source-entity-schema-config-ssot-manual-backfill-sql-job-source) rebuilt the job table (`company` → nullable `company_id`), that column no longer exists, so SQLite raises `OperationalError: no such column: j.company`, the dispatcher truncates the batch, and qualify never runs.

## To-be

`get_job_batch` joins employer on `j.company_id = c.short_name` (nullable real employer per [AST-1701](https://linear.app/astralcareermatch/issue/AST-1701/job-source-entity-schema-config-ssot-manual-backfill-sql-job-source)), returns the same job dicts plus `job_site`, and `qualify_meteorite` batches proceed without a schema OperationalError.

## Proposed steps

1. In `src/data/database.py` `get_job_batch`, change the JOIN predicate from `j.company = c.short_name` to `j.company_id = c.short_name` (only live SQL still referencing `j.company` on origin/dev).
2. Leave `_job_row_to_dict`'s existing `company_id` → `company` compat alias alone unless a caller still breaks — that alias already covers pre-#2 readers.
3. Smoke: claim a small `METEORITE_NEW` batch (or unit-level `get_job_batch` against a migrated DB) and confirm no OperationalError and `job_site` still attaches when `company_id` is set.

## Component scope

* `src/data/database.py` — **modified** — `get_job_batch` SQL still joins on retired `j.company`; must use `j.company_id` after the [AST-1701](https://linear.app/astralcareermatch/issue/AST-1701/job-source-entity-schema-config-ssot-manual-backfill-sql-job-source) table rebuild. No new files expected.

## Technical scope

* `src/data/database.py` / `get_job_batch` — **modified function** — one-line JOIN column rename (`company` → `company_id`) so batch load matches the live job schema; without it every job-batch dispatch (including `qualify_meteorite`) dies before consult runs.

## Ancestor candidates

- [ ] [AST-1701](https://linear.app/astralcareermatch/issue/AST-1701/job-source-entity-schema-config-ssot-manual-backfill-sql-job-source) — Job source_entity schema + config SSOT + manual backfill SQL (renamed `job.company` → `company_id`; missed `get_job_batch` JOIN)
- [ ] [AST-1640](https://linear.app/astralcareermatch/issue/AST-1640/job-source-entity-parent-meteoritecompany-candidate-facing-link) — Job source_entity parent (meteorite|company) + candidate-facing link (live parent epic for [AST-1701](https://linear.app/astralcareermatch/issue/AST-1701/job-source-entity-schema-config-ssot-manual-backfill-sql-job-source))
- [ ] AST-337 — Qualified job URLs (introduced `get_job_batch` company JOIN for `job_site`)
- [ ] [AST-1598](https://linear.app/astralcareermatch/issue/AST-1598/job-and-app-log-candidate-id-log-stamp-add-candidate-id-to-artifact) — Job and app_log candidate_id (recent job-schema ensure work that still assumed `job.company`)

## Original report

```
[2026-09-17 20:46:51] INFO src.core.dispatcher: somerset | dispatch job starting qualify_meteorite — 17 available (batch: qualify_meteorite-3cb6fd14-7596-44bb-897b-87d4879af3d3)
[2026-09-17 20:46:51] ERROR src.data.database: database._with_conn failed: OperationalError('no such column: j.company') | args=() kwargs={}
[2026-09-17 20:46:51] ERROR src.core.dispatcher: somerset | dispatch job qualify_meteorite
  OperationalError: no such column: j.company
  Truncating the batch
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 1374, in _dispatch_one_body
    await _tracked()
  File "/app/src/core/dispatcher.py", line 1360, in _tracked
    await _run_dispatch_loop(ctx, task, task_key, entity_batch_id, accumulated, dispatch_ledger_id)
  File "/app/src/core/dispatcher.py", line 1537, in _run_dispatch_loop
    summary = await _run_task(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 809, in _run_task
    summary = await _run_unified(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 614, in _run_unified
    bid, entities = get_new_job_batch(
                    ^^^^^^^^^^^^^^^^^^
  File "/app/src/core/tracker.py", line 1530, in get_new_job_batch
    jobs = database.get_job_batch(bid)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/data/database.py", line 2233, in get_job_batch
    return _run_with_retry(_with_conn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/data/database.py", line 285, in _run_with_retry
    return fn()
           ^^^^
  File "/app/src/data/database.py", line 2228, in _with_conn
    cursor = conn.execute("SELECT j.*, c.job_site FROM job j LEFT JOIN company c ON j.company = c.short_name WHERE j.batch_id = ?", (batch_id,))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sqlite3.OperationalError: no such column: j.company
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
