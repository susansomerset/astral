# AST-763 — Cannot change task_key in the scheduled task modal

<!-- linear-archive: AST-763 archived 2026-07-22 -->

## Linear archive (AST-763)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-763/cannot-change-task-key-in-the-scheduled-task-modal  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** susan  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

When Susan edits an existing scheduled action on the Scheduled Actions admin screen, the **Task** field is missing from the modal — only **Add Task** lets her pick a `task_key`. She needs to change which dispatch task a row runs without deleting and re-adding the row (e.g. correcting a mis-picked key or retargeting a schedule). This is a focused admin UX gap on a screen already in UAT ([AST-735](https://linear.app/astralcareermatch/issue/AST-735/scheduled-actions-screen-edits)).

## Functional scope

* **Task selector on Edit Task:** The Add/Edit modal shows the same **Task** dropdown on **Edit Task** as on **Add Task**, populated from the admin dispatch task-key catalog (all keys returned for scheduled-action forms today).
* **Persist task_key on save:** Saving an edited row updates the stored `task_key` for that dispatch row, not only the scheduling fields editable today (freq, min count, batch size, max runs, trigger state, score floor, AUTO, debug).
* **Preserve row values on task_key change:** Changing **Task** in the modal does **not** reset **Input State** or **Score Floor** — Susan's current values stay unless she edits them manually. **Entity Type** still reflects the selected task key (read-only, catalog-derived) so she can see what she picked.
* **Save validation:** On save, validate that the chosen `task_key` is valid for the row's **Input State**; reject with a clear error if not. Do not silently adjust score floor or trigger state to catalog defaults.
* **AUTO rows not editable:** Rows with **AUTO mode** on cannot be edited (including task_key) — Susan must turn AUTO off first or use another path.
* **Running rows editable:** Rows with an active dispatch thread remain editable; changes apply to **future runs only**, not the in-flight run.
* **Duplicate-row guard:** If the combination of candidate, task key, and input state would duplicate another dispatch row, save fails with a clear error and the modal stays open.
* **Regression guard:** All other behaviors (Add Task, run/stop, AUTO/Dbg toggles, filters, grouping, Stop All, polling) remain as on the current Scheduled Actions screen.

## Boundaries

* Does **not** allow changing **candidate** on an existing row — only **task_key** and the fields already editable in the modal.
* Does **not** auto-reset **Input State** or **Score Floor** when **Task** changes (Susan's explicit direction).
* Does **not** change dispatch scheduler tick logic, claim/run behavior, or ledger semantics beyond "future runs pick up saved row values."
* Does **not** bulk-migrate or clone scheduled actions (Apply Scheduled Actions remains out of scope per [AST-735](https://linear.app/astralcareermatch/issue/AST-735/scheduled-actions-screen-edits)).
* Does **not** add, remove, or rename catalog task keys — only lets Susan point an existing row at a different existing key.
* Must not regress [AST-735](https://linear.app/astralcareermatch/issue/AST-735/scheduled-actions-screen-edits) / [AST-751](https://linear.app/astralcareermatch/issue/AST-751/scheduled-actions-filters-auto-summary-and-all-candidate-layout-scheduled-actions-screen-edits) layout, filters, or task grouping.
* No backend debug-logging requirements (admin UI change only).

## Acceptance criteria

1. Open **Edit Task** on a non-AUTO scheduled-action row — the **Task** dropdown is visible with the current task key selected.
2. Choose a different task key, keep or adjust **Input State** / **Score Floor** manually, and **Save** — after reload, the row shows the new task key; **Score Floor** unchanged unless Susan edited it.
3. Save with a `task_key` invalid for the row's **Input State** — explicit validation error; no save.
4. Attempt to save a change that would duplicate `(candidate, task_key, trigger_state)` — explicit error; modal stays open.
5. Row with **AUTO mode** on — **Edit Task** is unavailable or blocked (cannot change task_key while AUTO is on).
6. Row with an active running thread — **Edit Task** and save succeed; in-flight run behavior unchanged; subsequent runs use updated row values.
7. Add Task, run/stop, AUTO/Dbg column toggles, filters, collapsible task groups, and Stop All still behave as before UAT on [AST-735](https://linear.app/astralcareermatch/issue/AST-735/scheduled-actions-screen-edits).
8. Component tests cover Edit Task task-key selection, validation, AUTO-blocked edit, and successful save with an updated key.

## Dependencies and blockers

None — builds on the Scheduled Actions screen and dispatch-task admin API already on `dev` via [AST-734](https://linear.app/astralcareermatch/issue/AST-734/organizing-tasks) / [AST-735](https://linear.app/astralcareermatch/issue/AST-735/scheduled-actions-screen-edits). No wait on Backlog epics.

## Open questions

None.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-763 (parent) | ftr/AST-763-edit-modal-task-key |
| AST-773 | sub/AST-763/AST-773-edit-modal-task-key-and-api |

| AST-781 | sub/AST-763/AST-781-scheduled-actions-500-board-search-entity-type |

**Epic worktree:** `astral-AST-763/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | 1eab4795-e6aa-4edc-9f2a-db547adddc0b |
| Betty | qa | 3cf88329-76d9-4a0c-830f-877aa9cd61a1 |
| Radia | review | 491da84e-eed0-423f-8eba-a569343a0173 |

---

## Original brief

I need to be able to change the selected task_kay for a scheduled action, but it does not appear on the modal.

### Comments

#### chuckles — 2026-06-25T02:00:54.694Z
[check-linear] Done — parent shipped; no Chuckles action unless you want a new Discussion ticket (@susan)

#### chuckles — 2026-06-24T05:48:36.040Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-781** | Scheduled Actions 500 — Unknown entity_type board_search |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-781** — _Scheduled Actions 500 — Unknown entity_type board_search_
- **Issue reported:** Opening **Admin → Scheduled Actions** (`/admin/scheduled_actions`) fails to load the dispatch task list. Browser shows loading/error; server log shows `GET /api/admin/dispatch_tasks` returning **500** with:
- **Should now:** Scheduled Actions page loads all dispatch rows (including any legacy rows) without error; Available counts show **0** or **—** for rows that cannot be counted, not a 500 for the whole page.
- **Quick check (this fix only):**
  1. Log in as admin with at least one `dispatch_task` row whose `entity_type` is `board_search` (legacy boards sunset data).
  2. Navigate to **Scheduled Actions**.
  3. Observe `GET /api/admin/dispatch_tasks` → 500 and page does not render the table.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-24T05:34:40.651Z
@chuckles What needs to happen next for this ticket?  it seems stuck.

#### chuckles — 2026-06-24T02:54:26.400Z
[thread-missing] blocked: Cursor agent transcript for `b6540c34-97de-4750-8d00-7d3659b234c2` is not on this host (petrichor). Run this job from **chuckles server (HP ProDesk)** where that conversation exists.

Do **not** `agent create-chat` or `--resume` here — that forks a new thread the other host cannot use.

Watcher rule `fix` on `AST-763`.

— Chuckles

#### susan — 2026-06-23T21:19:37.241Z
Got this error when I attempted to look at the scheduled actions:

```
127.0.0.1 - - [23/Jun/2026 14:18:54] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [23/Jun/2026 14:18:54] "GET /api/admin/dispatch_tasks/state_options HTTP/1.1" 200 -
127.0.0.1 - - [23/Jun/2026 14:18:54] "GET /api/admin/dispatch_tasks/task_keys HTTP/1.1" 200 -
127.0.0.1 - - [23/Jun/2026 14:18:54] "GET /api/admin/dispatch_tasks HTTP/1.1" 500 -
Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 1478, in __call__
    return self.wsgi_app(environ, start_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 1458, in wsgi_app
    response = self.handle_exception(e)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 1455, in wsgi_app
    response = self.full_dispatch_request()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 869, in full_dispatch_request
    rv = self.handle_user_exception(e)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 867, in full_dispatch_request
    rv = self.dispatch_request()
         ^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 852, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/ui/auth.py", line 83, in decorated
    return f(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/ui/auth.py", line 94, in decorated
    return f(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/ui/api/api_admin.py", line 745, in list_dtasks
    row["available_count"] = database.count_eligible_for_dispatch_task(row) if et and ts and cid else 0
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5790, in count_eligible_for_dispatch_task
    return count_entities_in_state(entity_type, state, candidate_id, states=claim_states)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5854, in count_entities_in_state
    return _run_with_retry(_with_conn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 247, in _run_with_retry
    return fn()
           ^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5850, in _with_conn
    raise ValueError(f"Unknown entity_type: {entity_type}")
ValueError: Unknown entity_type: board_search
127.0.0.1 - - [23/Jun/2026 14:18:54] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [23/Jun/2026 14:18:54] "GET /api/admin/dispatch_tasks/state_options HTTP/1.1" 200 -
127.0.0.1 - - [23/Jun/2026 14:18:54] "GET /api/admin/dispatch_tasks/task_keys HTTP/1.1" 200 -
127.0.0.1 - - [23/Jun/2026 14:18:54] "GET /api/admin/dispatch_tasks HTTP/1.1" 500 -
Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 1478, in __call__
    return self.wsgi_app(environ, start_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 1458, in wsgi_app
    response = self.handle_exception(e)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 1455, in wsgi_app
    response = self.full_dispatch_request()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 869, in full_dispatch_request
    rv = self.handle_user_exception(e)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 867, in full_dispatch_request
    rv = self.dispatch_request()
         ^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/flask/app.py", line 852, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/ui/auth.py", line 83, in decorated
    return f(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/ui/auth.py", line 94, in decorated
    return f(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/ui/api/api_admin.py", line 745, in list_dtasks
    row["available_count"] = database.count_eligible_for_dispatch_task(row) if et and ts and cid else 0
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5790, in count_eligible_for_dispatch_task
    return count_entities_in_state(entity_type, state, candidate_id, states=claim_states)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5854, in count_entities_in_state
    return _run_with_retry(_with_conn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 247, in _run_with_retry
    return fn()
           ^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5850, in _with_conn
    raise ValueError(f"Unknown entity_type: {entity_type}")
ValueError: Unknown entity_type: board_search
127.0.0.1 - - [23/Jun/2026 14:18:59] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
```

#### chuckles — 2026-06-23T19:51:30.336Z
@susan

1. When **task_key** changes on an existing row, should **Input State** and **Score Floor** reset to the new task's catalog defaults (matching Add Task when you pick a key), or stay at the row's current values unless you change them manually?
2. Should **task_key** editing be blocked while that row's dispatch thread is actively running?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
