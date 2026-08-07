# AST-1266 — app_log integer PK schema, migration, and write cutover

**Linear:** [AST-1266](https://linear.app/astralcareermatch/issue/AST-1266/app-log-integer-pk-schema-migration-and-write-cutover-change-app-log)  
**Parent:** [AST-1263](https://linear.app/astralcareermatch/issue/AST-1263/change-app-log-id-to-autoincrement-integer) — Change app_log_id to autoincrement integer  
**Publish ref:** `sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover`

`app_log` is an append-only operational log whose primary key is a client-minted UUID that nothing else references. This ticket replaces that key with SQLite integer `AUTOINCREMENT`, migrates existing TEXT-PK tables, and cuts over `add_log_entry` so inserts no longer supply an `id`. Execution History continues to list/filter by level/batch/time; row `id` remains an opaque React key (now a JSON number).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Header inventory note for `app_log` integer PK; `_ensure_app_log_schema` creates INTEGER AUTOINCREMENT on fresh DBs and rebuilds TEXT-PK tables; `add_log_entry` stops minting UUIDs and omits `id` from INSERT | data |
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | Widen `LogEntry.id` from `string` to `number` so Execution History types match integer row ids from the API | ui |

**Out of files (do not touch):** `src/utils/logging.py` late-import flush path (must remain the only runtime utils→data import for `app_log` writes); other tables’ schema/ensure helpers; log cleanup (AST-360); debug-contract redesign.

## Stages

### Stage 1: Schema ensure, TEXT→INTEGER migration, write cutover

**Done when:** On a fresh DB, `PRAGMA table_info(app_log)` shows `id` type `INTEGER` with `pk=1`, and `add_log_entry(...)` inserts a row whose `id` is a positive integer without any client-supplied UUID. On a DB that previously had `id TEXT PRIMARY KEY` rows, after `_ensure_app_log_schema` runs once, the table is integer PK, prior rows are still queryable (same level/batch/message/created_at; new integer ids assigned), and a subsequent `add_log_entry` succeeds. Header inventory line for `app_log` documents integer autoincrement PK.

1. In `src/data/database.py` module docstring **Tables used (inventory)**, update the `app_log` bullet to state that the primary key is integer `AUTOINCREMENT` (column name remains `id` — do **not** rename to `app_log_id`), and that writers do not supply `id`. Keep the existing mention of `add_log_entry` / `list_log_entries`.

2. In `_ensure_app_log_schema`, replace the create-only TEXT PK path with this exact control flow (still gated by `_app_log_schema_ensured`; still idempotent):

   a. If `sqlite_master` has no `app_log` table, `CREATE TABLE app_log` with:

   ```sql
   CREATE TABLE app_log (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       level TEXT,
       logger_name TEXT,
       message TEXT,
       batch_id TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
   ```

   then `conn.commit()`.

   b. Else (table exists): read `PRAGMA table_info(app_log)`. Locate the column named `id`. If its declared type (case-insensitive) is not `INTEGER`, rebuild in this order:

   - `DROP TABLE IF EXISTS app_log_new` — clear a leftover temp table from an interrupted prior rebuild so the next `CREATE` cannot raise “table app_log_new already exists” and brick bootstrap (matches `_drop_entity_agent_responses_column`’s `DROP TABLE IF EXISTS {tmp}` guard; keep the name `app_log_new`, do **not** use a ticket-stamped temp name).
   - `CREATE TABLE app_log_new` with the same column list/types as the CREATE in (a).
   - `INSERT INTO app_log_new (level, logger_name, message, batch_id, created_at) SELECT level, logger_name, message, batch_id, created_at FROM app_log` — **omit** `id` so SQLite assigns new integers. Do not preserve old UUID strings as ids (nothing FKs to them).
   - `DROP TABLE app_log`.
   - `ALTER TABLE app_log_new RENAME TO app_log`.
   - `conn.commit()`.

   c. If the existing table’s `id` type is already `INTEGER`, do nothing to the table.

   d. Set `_app_log_schema_ensured = True` and return (same as today after create).

   ⚠️ **Decision:** Detect migration need via `PRAGMA table_info` declared type of `id` (not sampling row values, not parsing `sqlite_master` SQL). Precedent for full-table rebuild under SQLite ALTER limits is `_ensure_dispatch_task_schema` / `_drop_entity_agent_responses_column` in this same module — including the leftover-temp `DROP TABLE IF EXISTS` before `CREATE`. Old UUID primary-key values are discarded on copy because `app_log.id` is not a foreign key anywhere (parent Architectural definition).

3. In `add_log_entry`, remove `entry_id = str(uuid.uuid4())` and change the INSERT to:

   ```sql
   INSERT INTO app_log (level, logger_name, message, batch_id)
   VALUES (?, ?, ?, ?)
   ```

   with bind params `(level, logger_name, message, batch_id)` only. Do **not** use `INSERT OR IGNORE` (that existed for client UUID collision tolerance; AUTOINCREMENT ids do not collide that way). Keep the existing try/except/rollback/`return False` / `return True` / `finally: conn.close()` shape. Keep calling `_ensure_app_log_schema(conn)` before the INSERT. Do **not** remove the module-level `uuid` import (still used elsewhere in `database.py`).

4. Do **not** change `list_log_entries` filter SQL, ordering (`ORDER BY created_at DESC`), or `_row_to_dict` — integer `id` values flow through as Python `int` and JSON numbers automatically.

5. Do **not** edit `src/utils/logging.py`. Confirm by reading only: `_flush_buffer` still late-imports `add_log_entry` inside the method and still calls `add_log_entry(**e)` with keys `level`, `logger_name`, `message`, `batch_id` only (no `id` key in the buffer dict). If that read shows a top-level `from src.data.database import add_log_entry` or an `id` field being passed, **stop** and comment on the parent — do not “fix” the handler in this ticket without plan revision.

### Stage 2: Execution History LogEntry type for integer ids

**Done when:** `LogEntry.id` in `AdminPerformanceMonitor.tsx` is typed as `number`; `key={entry.id}` still keys expanded log rows; level/batch/time filtering and Copy behavior are unchanged in code (no filter logic edits).

1. In `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`, change the `LogEntry` interface field `id: string` to `id: number`. Do not change `LOG_LEVELS`, URL `log_level` filtering, `visibleLogs`, Copy, empty-state messages, or the `/api/admin/dispatch_ledger/<batch_id>/logs` fetch path.

   ⚠️ **Decision:** Type as `number` (not `string | number`) because after Stage 1 every API response for `app_log.id` is a JSON number. React keys accept numbers; no stringification helper is required.

## Self-Assessment

**Scope:** `Single-Component` — data-layer `app_log` ensure/write plus a one-field TypeScript type align on Execution History; no other tables or logging pipeline redesign.

**Conf:** `high` — CREATE/rebuild/INSERT patterns already exist in `database.py` (`dispatch_task` INTEGER AUTOINCREMENT; table rebuild helpers); write path and late-import contract are already documented in Code Rules §1.5.

**Risk:** `Medium` — wrong migration detection or a write/schema mismatch would break all `app_log` appends (and thus Execution History population) until fixed; scope is isolated to one table with no FKs.

## Code Rules self-review

| Rule | Status |
|------|--------|
| §1.1 in-scope-only / no-cross-contamination | Only `app_log` PK/write + EH type; other tables untouched |
| §1.1 database-header-inventory | Header bullet updated for integer AUTOINCREMENT PK |
| §1.5 logging-via-utils / utils-data-late-import-only | Late import in `_flush_buffer` left unchanged; no new utils→data imports |
| §1.5 data-raises-caller-logs | `add_log_entry` keeps bool return / no logging inside data |
| §1.3 DRY | Reuses existing ensure-flag + rebuild style; no parallel migration framework |
| §2.1 config | N/A — no new config keys |
| §2.4 batch | N/A — `app_log` is not a claim queue |
| §2.6 state machine | N/A |
| §3.3 imports | UI stays UI; data stays data; utils not edited |
| §3.5 naming | Column remains `id` (parent boundary: do not rename to `app_log_id`); rebuild temp table is `app_log_new` (not ticket-stamped) |

## Revisions

Revision 1 — 2026-08-07  
Driven by: Joan `[plan-discuss] round=1 concern` — rebuild omits precedent’s leftover-temp-table guard (`DROP TABLE IF EXISTS` before `CREATE TABLE app_log_new`), which can brick bootstrap if a prior rebuild left `app_log_new` behind.  
Changes: Stage 1 step 2b now starts with `DROP TABLE IF EXISTS app_log_new` before `CREATE`; Decision / naming self-review note the guard and keep the generic `app_log_new` name.

## Review

**Publish ref:** `sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover`
**Product tip:** `a0b87bf1` (Stage 2)
**Stage commits:** Stage 1 @ `57ce46bd`; Stage 2 @ `a0b87bf1`.

### Radia review — clean

`[code-rubric] revision=1` — full active-set sweep (63 statutes) scored in-session against `git diff origin/dev...e1c78811` (publish ref tip). **Overall: CLEAN.**

**What's solid:**

- Stage 1 and Stage 2 land exactly per plan: `_ensure_app_log_schema` creates `INTEGER PRIMARY KEY AUTOINCREMENT` on fresh DBs, rebuilds legacy `TEXT` PK tables (with the `DROP TABLE IF EXISTS app_log_new` guard from Revision 1), and `add_log_entry` no longer mints a client UUID. `LogEntry.id` widened `string → number` in `AdminPerformanceMonitor.tsx`; no filter/Copy/fetch logic touched.
- Verified read-only claim: `src/utils/logging.py` `_flush_buffer` still late-imports `add_log_entry` and calls it with only `level`/`logger_name`/`message`/`batch_id` — AC5 holds.
- Betty's test commit (`7a2ecc1a`, merged via the single-SHA `merge-tests(AST-1266)` pattern) touches only `tests/` + `docs/test-bible/**`; the engineer's own commits (`57ce46bd`, `a0b87bf1`, docs) touch only `src/data/database.py`, `AdminPerformanceMonitor.tsx`, and this plan doc — clean layer/ownership separation.

**Notes (advisory, not fix-now):**

- `astral.seed.boot-only-not-hot-path`: the TEXT→INTEGER rebuild branch is gated only by the process-lifetime `_app_log_schema_ensured` flag (first hot-path call, not an explicit boot/migration script). This mirrors existing precedent (`_ensure_dispatch_task_schema` et al.) already in `database.py` and isn't a new pattern introduced by this ticket — flagging for awareness only.
- The three-dot diff vs `origin/dev` also carries an inherited `test(AST-1264)` commit (`eaf4467a`) via Betty's shared tests lineage (`tests/component/core/test_agent.py`, `test_agent_tasks.py`, 4 test-bible docs). Confirmed via `git show --stat` on each AST-1266-tagged commit that none of AST-1266's own code/test/docs commits touch those files — no scope smuggling by this ticket.

**Pattern conformance:** `pattern.layers.import-discipline` (no canon match; nearest analog `astral.layers.import-direction` — conforms, no new imports), `astral.standards.utils-data-late-import-only` (conforms), `astral.standards.in-scope-only` (conforms), `astral.standards.database-header-inventory` (conforms).

— Radia
