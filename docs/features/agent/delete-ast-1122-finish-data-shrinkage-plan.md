# AST-1122 — Finish data shrinkage plan

<!-- linear-archive: AST-1122 archived 2026-08-07 -->

## Linear archive (AST-1122)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1122/finish-data-shrinkage-plan  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

Rebuild this ticket around an Admin **Scheduled Queries** tool (not one-off shrinkage SQL in the Description).

1. **Storage** — Add a SQLite table (working name `scheduled_query`) with at least: stable id, name/label, `sql_text`, `active` (bool), `last_run_at` (nullable), `last_rows_affected` (nullable int), `created_at` / `updated_at`. Lazy schema-ensure like other admin tables.
2. **Admin UI** — New Admin page **Scheduled Queries** (nav next to Data Management): list rows; create/edit name + SQL; toggle `active`; show last run + records affected. **No Run now** control (manual SQL stays on Data Management).
3. **Admin API** — CRUD endpoints under `/api/admin/…` (`@require_admin`) for list/create/update (incl. active toggle). Reuse the same DB execute path Data Management uses for statement execution when the scheduler fires (capture `cursor.rowcount` for writes; define SELECT semantics for `last_rows_affected`).
4. **Daily runner** — Hook into the existing in-process dispatcher scheduler (or a sibling once-per-day wake): for each `active=1` row due for today, execute `sql_text`, then update `last_run_at` + `last_rows_affected`. Idempotent within a calendar day (do not re-fire the same row after a successful same-day run).
5. **First saved query (operator seed, optional)** — Example only; Susan pastes/edits in UI: cleanup non-RESPONSE `agent_data` older than N days (her example: `DELETE FROM agent_data WHERE created_at < … AND block_type != 'RESPONSE'`). Keep RESPONSE rows; retention window confirmed in open questions.
6. **Out of scope here** — One-shot Description SQL for `ref_agent_data_id` linking (prior plan); Python AST-978 backfill CLI; vacuum/space reclaim; a separate “Run now” button.

## Done when

* Admin can save named SQL rows, toggle `active`, and see last run + records affected.
* Active rows run once per day via the existing scheduler path; inactive rows never run.
* No Run-now UI on this page.
* Data Management ad-hoc SQL remains the manual execute surface.

## Risks / open questions

1. **Retention window** for the first cleanup query: 24 hours (your earlier note) vs 3 days (SQL example in rethink) — which default?
   1. You don't care. I will write the queries and their criteria.  
2. **Day boundary**: UTC midnight vs server-local vs “once every 24h since last_run”?
   1. Set it to hours frequency, so not utc and possible every hour depending on what happens to our data.
3. **SELECT vs DML**: if someone saves a SELECT, is `last_rows_affected` = row count returned, or should active scheduled queries be restricted to write statements?
   1. Don't validate it, but yes obviously these will be action statements not select.
4. **Failure behavior**: on SQL error, leave `last_run_at` unchanged (retry next day) or stamp last_run + store last error?
   1. Depends on the error.  If it's a syntax error, switch the flag to off. If it's a network issue or temporary issue, leave it unchanged.
5. **Safety**: same trust model as Data Management (admin-only, any SQL), or add a denylist (e.g. no `DROP TABLE`)?
   1. Same trust model

---

## Original brief

Finish implementing the reuse of agent data content to avoid massive duplicates.

We need SQL statements to link existing duplicate agent_data to their first occurrence.

For this ticket, please just put the SQL statements in the description of this ticket and I will run them, and as a follow on we will add a new issue to validate runtime data handling for agent_data duplicates.

### Archie rethink (2026-08-07)

The simple answer is to clean up all but the response blocks after 24 hours.

Let's completely rethink this ticket and make it an admin tool called scheduled queries, where I can save a sql statement (e.g. "delete from agent_data where created_at < today() - 3 and block_type ≠ 'RESPONSE'") to a row and have an active flag to run every day, and track the last run and records affected. I don't need a "run now" option because I already have that in data management.

### Comments

#### susan — 2026-08-07T06:17:46.567Z
let's completely rethink this ticket and make it an admin tool called scheduled queries, where I can save a sql statement (e.g. "delete from agent_data where created_at < today() - 3 and block_type ≠ 'RESPONSE'") to a row and have an active flag to run every day, and track the last run and records affected.  I don't need a "run now" option because I already have that in data management.

#### susan — 2026-08-07T06:12:06.922Z
The simple answer is to clean up all but the response blocks after 24 hours.

#### chuckles — 2026-08-02T17:51:58.482Z
[check-linear] Discussion — RESPONSE-only SQL ready to run (@susan)

#### susan — 2026-08-02T17:50:21.560Z
@chuckles Please update these queries to just use one block_type: "RESPONSE" (we will run the others later.)

---

_Implementation detail may live in git history on `origin/dev`._
