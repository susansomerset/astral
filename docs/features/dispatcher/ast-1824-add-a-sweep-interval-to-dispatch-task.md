# AST-1824 — Add a sweep interval to dispatch_task

<!-- linear-archive: AST-1824 archived 2026-10-07 -->

## Linear archive (AST-1824)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1824/add-a-sweep-interval-to-dispatch-task  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

AUTO dispatch rows only start when Avail reaches `min_count`. Rows tuned for full batches (`min_count` = `batch_size`) can leave a partial remainder sitting forever — today the only way to clear it is an admin clicking **Sweep** on Scheduled Actions. Susan wants each `dispatch_task` row to carry its own sweep interval so the scheduler clears leftovers on a cadence: the same effect as a companion row with a frequency interval and `min_count` 1, without a second row. The manual Sweep button stays.

## Functional scope

1. **Per-row sweep interval.** Each `dispatch_task` row can hold a sweep interval in hours. Empty or 0 means no scheduled sweep; that is the default, so existing rows behave exactly as today until Susan sets a value.
2. **Scheduled sweep.** On each scheduler tick, an AUTO-on row with a sweep interval is due for a sweep when Avail is above 0 but below `min_count`, and at least one sweep interval has passed since the row's last run (`last_run_at` — any run: a normal AUTO batch, a manual Run/Sweep, or an earlier scheduled sweep). Rows that already meet `min_count` run through the normal AUTO path, unchanged.
3. **Sweep behaves like the manual Sweep.** A scheduled sweep runs one batch with no `min_count` gate (up to `batch_size` rows), the same way a manual Sweep click on an AUTO row does today. It uses the normal claim → process → release path, ledger, and `last_run_at` stamp. AUTO-off rows never sweep (unattended runs respect AUTO off, AST-1022).
4. **Both AUTO due paths.** The sweep rule applies to claim-queue rows and to candidate-bound mailbox rows (`stage_email_meteorite`). Every other gate each path has today stays in place (mailbox `freq_hrs` / trigger checks, the `max_auto_threads` slot limit, the running-thread skip, the `empty_render` / API-key AUTO guards).
5. **Admin surface.** On Scheduled Actions, the create/edit modal can set the sweep interval, and the list shows it as a column. The existing edit rule still applies (turn AUTO off before editing). Template copy (AST-875) carries the value like the other schedule fields.
6. **Manual Sweep unchanged.** The Sweep button, its enable/disable rule (`auto_mode && 0 < avail < min_count`), and its one-batch behavior do not change.

## Component scope

* `src/data/database.py` — **modified** — the `dispatch_task` schema gains a sweep-interval column; the insert/update/template-copy column sets include it; the AUTO due selection for claim-queue rows adds the sweep-due rule.
* `src/core/dispatcher.py` — **modified** — the mailbox AUTO due path adds the sweep-due rule; a tick-spawned sweep runs as one batch with the `min_count` gate bypassed.
* `src/ui/api/api_admin.py` — **modified** — dispatch_task create/update accept and validate the sweep interval, and list column metadata exposes it.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — sweep-interval field in the create/edit modal, plus a list column.

No deleted files.

## Technical scope

* `src/data/database.py`
  * **Modified table** `dispatch_task`**:** new nullable REAL column for the sweep interval in hours (NULL/0 = off). Add it to the fresh-table `CREATE TABLE` in the schema-ensure function and to that function's missing-column migration map, so existing DBs pick it up via `ALTER TABLE ADD COLUMN`. No backfill: existing rows stay NULL.
  * **Modified function (dispatch_task insert):** accepts an optional sweep interval and persists it.
  * **Modified constants (update whitelist and AST-875 template-copy column set):** include the new column.
  * **New helper (sweep due):** true when the row's sweep interval is > 0 and `last_run_at` is missing, or at least one interval old. Reuse the existing `last_run_at` parser that `dispatch_task_freq_allows` uses; do not write a second parser.
  * **Modified function (AUTO due selection for claim-queue rows):** a row is due when Avail ≥ `min_count` (today's rule), **or** when 0 < Avail < `min_count` and the sweep-due helper is true. Rows due only through the sweep branch are marked as a sweep on the returned dict so the tick can start them as a sweep.
* `src/core/dispatcher.py`
  * **Modified function (mailbox AUTO due):** same OR rule against live bound Avail, and it marks sweep rows the same way. The existing trigger check and `dispatch_task_freq_allows` gate still apply to both branches.
  * **Modified function (tick loop spawn):** passes the sweep mark into the thread spawn.
  * **Modified function (thread spawn entry point):** accepts a scheduled-sweep flag alongside the existing `ui_initiated` flag and carries it on the task dict.
  * **Modified function (dispatch batch loop):** when the scheduled-sweep flag is set on an AUTO row, cap at one batch and use an effective minimum of 1, the same as today's UI-initiated Sweep branch. A non-UI sweep must **not** turn on the local-env debug forcing that `ui_initiated` triggers.
* `src/ui/api/api_admin.py`
  * **Modified route (create dispatch_task):** optional sweep interval, parsed as float, null/empty → NULL; negative values rejected with 400.
  * **Modified route (update dispatch_task):** sweep interval in the allowed-field set with the same parsing/validation; the AUTO-on edit lock is unchanged.
  * **Modified constant (dispatch_task list column metadata):** add the sweep-interval column.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx`
  * **Modified types / form state / list table:** add the sweep interval to the row and form types, the modal (create + edit) as a numeric input, and the list table as a sortable column showing `—` when empty. The Run/Sweep button logic is unchanged.

## Architectural definition

**Patterns to reuse**

* `patt.entity.batch-criteria` — the sweep interval is claim-cadence criteria held as `dispatch_task` row data and edited in the admin UI, never a literal in the caller. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-criteria.md>)
* `patt.entity.batch-processing` — a sweep is one ordinary claim → process → release batch; no second claim or lock. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>)

**New patterns proposed:** none.

**Applicable statutes**

* `astral.batch.claim-process-release` — the sweep batch uses the same pool claim and `batch_id` lock/release as a normal run; no carve-out. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.batch.claim-process-release.md>)
* `astral.dispatch.entity-state-bound` — a sweep claims by the row's own `entity_type` / `trigger_state` / `candidate_id`; the new column does not relax that binding. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.dispatch.entity-state-bound.md>)
* `stat.logging.info.dispatcher` — a sweep run ends with the same `task completed` info line as any dispatch run. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.dispatcher.md>)
* `stat.logging.debug` — sweep-due decisions in the due path log at debug, not info, and the log call itself is not gated. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)

## Acceptance criteria

 1. **Column exists on fresh and existing DBs.** After schema ensure runs, `PRAGMA table_info(dispatch_task)` lists the sweep-interval column as REAL, nullable, with existing rows NULL. Fail: the column is missing, or any pre-existing row has a non-NULL value.
 2. **Sweep due fires.** Take an AUTO row with `min_count=10` and a sweep interval of 1, Avail 3, and `last_run_at` 2 hours ago. The AUTO due selection returns it, marked as a sweep. Fail: not returned, or returned without the sweep mark.
 3. **Sweep not due inside the interval.** Same row with `last_run_at` 10 minutes ago: not returned. Fail: returned.
 4. **No interval, no sweep.** Same row with a NULL or 0 sweep interval and Avail 3: not returned. This is today's behavior. Fail: returned.
 5. **Zero Avail never sweeps.** Same row, due interval, Avail 0: not returned. Fail: returned.
 6. **AUTO off never sweeps.** Same row with `auto_mode=0`: not returned by either due path. Fail: returned.
 7. **Full batches are unaffected.** An AUTO row with Avail ≥ `min_count` is returned without the sweep mark and runs its loop per `max_runs` as today. Fail: marked as a sweep, or capped at one batch.
 8. **One batch, no min gate.** Spawn a sweep-marked row through the tick path with Avail 3 < `min_count` 10 and `max_runs` 0. The dispatch batch loop runs exactly one batch (one `_run_task` call), does not stop on "below min_count", and stamps `last_run_at`. Fail: zero batches, more than one batch, or no `last_run_at` update.
 9. **Mailbox path parity.** A candidate-bound `stage_email_meteorite` AUTO row with bound Avail 2, `min_count` 5, a due sweep interval, and `dispatch_task_freq_allows` true is in the mailbox due list, marked as a sweep. With `freq_allows` false, it is not. Fail: either case inverted.
10. **Debug forcing stays UI-only.** A tick-spawned sweep on a local deploy with row `debug=0` does not set `log_debug` true. Fail: `log_debug` is true for a non-UI sweep.
11. **Admin API round-trip.** `POST /api/admin/dispatch_tasks` with a sweep interval of 2.5 persists 2.5. `PUT` on an AUTO-off row with 4 persists 4, and with null clears it to NULL. A negative value returns 400. The list endpoint's column metadata includes the sweep-interval key. Fail: any value not persisted as stated, a negative accepted, or the key absent from the column metadata.
12. **Template copy.** An AST-875 template copy from a row with a sweep interval of 6 yields target rows with 6. Fail: the target is NULL or differs.
13. **UI.** On Scheduled Actions, the modal shows a sweep-interval numeric input in create and edit, and saving sends it. The list shows the value (or `—`), sortable. `npm run build` in `src/ui/frontend` succeeds. Fail: the field is missing, not sent, or the build fails.
14. **Manual Sweep unchanged.** `grep -n "sweepDisabled" src/ui/frontend/src/pages/AdminScheduledActions.tsx` still shows `!!row.auto_mode && avail >= (row.min_count || 1)`, and a UI-initiated run on an AUTO row still runs one batch with min 1. Fail: the rule changed, or manual Sweep behavior regressed.
15. **No parallel scheduler.** `grep -n "Thread(" src/core/dispatcher.py` returns exactly two matches (the existing per-task thread and the tick thread). The sweep is decided inside the existing due selection and spawned by the existing tick loop. Fail: a new sweep thread, timer, or separate scheduler loop exists.

## Open questions

none

## Proposed child tickets

#### 1!: **Sweep interval data + scheduled sweep - Ada**

Adds the per-row sweep interval (schema, insert, update whitelist, template copy) and the scheduler behavior. Both AUTO due paths start a sweep when 0 < Avail < `min_count` and the interval has elapsed since `last_run_at`. A tick-spawned sweep runs one batch with no `min_count` gate, with no UI debug forcing. Does **not** own the admin API or UI (#2). Ships AC 1–10, 12, and 15.
**Citations:** `patt.entity.batch-criteria`, `patt.entity.batch-processing`, `astral.batch.claim-process-release`, `astral.dispatch.entity-state-bound`, `stat.logging.info.dispatcher`, `stat.logging.debug`.
**Scope:**

* `src/data/database.py` — **modified** — the `dispatch_task` schema gains a sweep-interval column; the insert/update/template-copy column sets include it; the AUTO due selection for claim-queue rows adds the sweep-due rule. Technical: new nullable REAL column in `CREATE TABLE` + missing-column migration map, no backfill; insert accepts an optional sweep interval; update whitelist and AST-875 template-copy column set include the column; new sweep-due helper reusing the existing `last_run_at` parser; AUTO due selection OR's in the sweep branch (0 < Avail < `min_count` and sweep due) and marks sweep rows.
* `src/core/dispatcher.py` — **modified** — the mailbox AUTO due path adds the sweep-due rule; a tick-spawned sweep runs as one batch with the `min_count` gate bypassed. Technical: mailbox due gets the same OR rule and mark, with existing trigger/`freq_allows` gates kept; the tick loop passes the sweep mark into the thread spawn; the thread spawn entry point accepts a scheduled-sweep flag alongside `ui_initiated`; the dispatch batch loop caps at one batch with effective minimum 1 when the flag is set on an AUTO row; no local-env debug forcing for a non-UI sweep.

Estimate: 3

#### 2: **Sweep interval in admin API + Scheduled Actions UI - Hedy**

After #1. Lets Susan set and see the sweep interval: create/update routes accept and validate it, list column metadata exposes it, and the Scheduled Actions modal and list show it. Does **not** own the schema or scheduler (#1), and leaves manual Sweep logic alone. Ships AC 11, 13, and 14.
**Citations:** `patt.entity.batch-criteria` — the value is row data edited through the admin UI.
**Scope:**

* `src/ui/api/api_admin.py` — **modified** — dispatch_task create/update accept and validate the sweep interval, and list column metadata exposes it. Technical: create route takes an optional float, null/empty → NULL, negative → 400; update route adds it to the allowed set with the same parsing, AUTO edit lock unchanged; the dispatch_task list column metadata adds the column.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — sweep-interval field in the create/edit modal, plus a list column. Technical: row/form types, a modal numeric input (create + edit), and a sortable list column showing `—` when empty; Run/Sweep button logic unchanged.

Estimate: 2

**New patterns:** none.

**Monolith check:** 6 functional capabilities, 2 children. The split is backend (data + scheduler) and admin surface (API + UI).

**Scope partition check:** each of the 4 Component scope files is claimed by exactly one child: `database.py` and `dispatcher.py` → #1; `api_admin.py` and `AdminScheduledActions.tsx` → #2.

**Adjacent:** AST-1820 / AST-1821 (recheck_no_openings Avail window) touch Avail counting in `database.py`. This epic reads Avail but does not change how it is counted.

---

## Original brief

Dispatcher polls for tasks with avail counts >= min_count before it executes.  I want to add to each dispatch_task an interval to run a "sweep" where avail > 0.  This the equivalent of a dispatch_task record set to an frequency interval and a min count of 1, as a companion to null frequency min_count = batch_size records.  This does not remove the option to manually sweep from the admin screen, but it should trigger a sweep on the interval set for the dispatch_task.

### Comments

#### chuckles — 2026-09-28T05:55:37.449Z
AST-1829 REVIEW — Joan needs plan discuss: move sweep-due debug log from src/data to core.

#### chuckles — 2026-09-28T05:49:18.102Z
datt only starts on Todo + assignee Chuckles. Define hands back as Todo + assignee Susan (draft ready for your review), so it waited for your assign. Starting now.

#### susan — 2026-09-28T04:57:05.557Z
@chuckles Any reason why this ticket hasn't started datt?

---

_Implementation detail may live in git history on `origin/dev`._
