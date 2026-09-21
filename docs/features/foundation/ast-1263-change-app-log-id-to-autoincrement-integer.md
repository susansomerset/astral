# AST-1263 — Change app_log_id to autoincrement integer

<!-- linear-archive: AST-1263 archived 2026-08-17 -->

## Linear archive (AST-1263)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1263/change-app-log-id-to-autoincrement-integer  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

`app_log` stores append-only operational log rows. Its primary key is a UUID that nothing else references, so the UUID index is pure overhead on a high-write table. This epic replaces that key with an autoincrement integer so inserts stay cheap and the schema matches how the row is actually used (local identity only, not a cross-table handle).

## Functional scope

* **Integer autoincrement primary key:** `app_log` uses an autoincrement integer primary key (not a UUID/text key). New environments create that shape; existing environments end up on that shape after migration/ensure.
* **Writers stop minting UUIDs:** The append path no longer generates or supplies a client UUID for the primary key; the database assigns the integer id on insert.
* **Read/query continuity:** Listing and filtering `app_log` (including Execution History expanded logs keyed by row id in the UI) continues to work with integer ids — level, batch, and time filters behave as today.
* **Existing databases migrate:** Deployed databases that still have a UUID/text `app_log` primary key are migrated to the integer autoincrement shape without breaking subsequent appends or queries.

## Architectural definition

* **Patterns to reuse** — `pattern.layers.import-discipline` (schema and write ownership stay in the data layer; utils continues to reach `app_log` only via the approved late-import flush path). No approved catalog pattern covers append-only PK type; `dispatch_task`’s integer autoincrement PK is informal precedent only, not a cited pattern id.
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.standards.in-scope-only` (touch only `app_log` PK / write-read path for this change); `astral.standards.database-header-inventory` (header inventory stays accurate if table usage notes change); `astral.standards.no-cross-contamination`; `astral.standards.logging-via-utils`; `astral.standards.utils-data-late-import-only` (preserve late-import utils→data for flush); `astral.standards.data-raises-caller-logs`; `astral.layers.import-direction`.

## Boundaries

* Does **not** rename the column to `app_log_id` — the column remains the table’s primary key field; only the type/generation model changes.
* Does **not** reopen a workspace-wide primary-key consistency program (archived AST-867 / related debt). This is an intentional exception for an append-only log whose id is not a foreign key elsewhere; other UUID-keyed entity tables stay as they are.
* Does **not** change log message content, levels, debug-contract shape (AST-538 / AST-976), or Execution History filter UX beyond accepting integer row ids as React keys / opaque ids.
* Does **not** implement periodic log cleanup (Backlog AST-360 stays out of scope).
* Does **not** add foreign keys to or from `app_log.id`.
* Must preserve the utils→data late-import cycle guard for `app_log` writes.

## Acceptance criteria

1. On a fresh database, `app_log` is created with an integer autoincrement primary key (not UUID/text).
2. After this change is applied to an existing database that previously used a UUID/text `app_log` primary key, the table’s primary key is integer autoincrement and new rows insert successfully without a client-supplied UUID.
3. New log lines from normal application logging appear in `app_log` and are visible in Execution History for the relevant batch with the same level/batch/time filtering behavior as before.
4. No other table’s primary-key type is changed by this epic.
5. The late-import path from the logging handler into the data-layer append function remains the only runtime utils→data import for `app_log` writes.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1: **app_log integer PK schema, migration, and write cutover - Ada**

Owns schema ensure for new DBs, migration of existing UUID/text `app_log` PK to integer autoincrement, and cutover of the append path so inserts no longer mint UUIDs. Verifies list/query and Execution History still work with integer row ids. Does **not** own log cleanup, debug-contract redesign, or other tables’ PKs.
**Citations:** `pattern.layers.import-discipline`; `astral.standards.utils-data-late-import-only`; `astral.standards.in-scope-only`; `astral.standards.database-header-inventory`.

**Monolith check:** Four functional-scope bullets → one child — intentional inseparable vertical slice: schema, migration, and write cutover must ship together or inserts break against the wrong PK type.

**New patterns:** none.

---

## Original brief

There's fat index on app_log for a uuid primary key for app_log, which is silly because that key doesn't map anywhere.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1263 (parent) | ftr/AST-1263-change-app-log-id-to-autoincrement-integer |
| AST-1266 | sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover |

**Epic worktree:** `astral-AST-1263/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/a3845f38022d38bcc3fc3b95403a529d/e28ecc8a-56ac-435b-bd41-b024894336dd/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/2a39e8ca-5a92-4c1d-990f-4ebf02f32de9/store.db` |
| Radia | review | `/home/susan/.cursor/chats/a3845f38022d38bcc3fc3b95403a529d/fdc90e7e-29bd-41e6-ae2a-7f1b57b23188/store.db` |

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
