# AST-704 — UAT: Scheduled Actions dispatch_tasks API 500 on UNIQUE constraint (prefilter as batch process)

<!-- linear-archive: AST-704 archived 2026-06-23 -->

## Linear archive (AST-704)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-704/uat-scheduled-actions-dispatch-tasks-api-500-on-unique-constraint  
**Status at archive:** Duplicate  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-700 — prefilter as batch process  
**Blocked by / blocks / related:** parent: AST-700

### Description

## What failed

Opening **Admin → Scheduled Actions** (Manage Tasks) triggers `GET /api/admin/dispatch_tasks` and `GET /api/admin/dispatch_tasks/task_keys`, both returning **HTTP 500**. Server log:

```
sqlite3.IntegrityError: UNIQUE constraint failed: dispatch_task.candidate_id, dispatch_task.task_key, dispatch_task.trigger_state
```

Stack: `list_dispatch_tasks()` → `_ensure_dispatch_task_schema(conn)` → `conn.execute(...)` insert during schema ensure (`database.py` ~5021).

Susan cannot view or configure dispatch tasks — blocking UAT of **fetch_website** and batch **prefilter** scheduling.

## Expected

Scheduled Actions page loads; dispatch task list and task keys return **200**; new **fetch_website** and batch **prefilter** tasks are visible alongside existing tasks without duplicate-key crashes on schema ensure.

## Repro

1. Run local app on current [AST-700](https://linear.app/astralcareermatch/issue/AST-700/prefilter-as-batch-process) UAT build (`origin/dev` after prep-uat).
2. Log in as admin; open **Scheduled Actions** / Manage Tasks.
3. Observe browser network: `/api/admin/dispatch_tasks` and `/api/admin/dispatch_tasks/task_keys` return **500**; console shows IntegrityError above.

## Parent AC (quoted inline)

> 1. A company in **WEBSITE_FOUND** with a valid **company_website**, when claimed by **fetch_website**, ends in **HOMEPAGE_READY** with homepage content persisted in **company_data** (and redirect normalized if the site moved).

> 3. Multiple companies in **HOMEPAGE_READY** can be claimed in one dispatch batch and evaluated in a **single** agent call; each company receives an independent pass/fail outcome and state transition matching today's prefilter semantics.

*(AC 1 and 3 require working dispatch task admin to schedule and verify the new tasks.)*

## Boundaries

* This bug does **not** change: prefilter rubric, encoded decode, scrape/evaluate business logic, or roster company state transitions beyond fixing dispatch_task seed/schema idempotency.
* Does **not** add new dispatch tasks — only fixes registration/listing so existing **fetch_website** / batch **prefilter** config can be viewed and scheduled.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
