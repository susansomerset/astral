<!-- linear-archive: AST-1266 archived 2026-08-17 -->

## Linear archive (AST-1266)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1266/app-log-integer-pk-schema-migration-and-write-cutover-change-app-log  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1263 — Change app_log_id to autoincrement integer  
**Blocked by / blocks / related:** parent: AST-1263

### Description

## What this implements

Owns schema ensure for new DBs, migration of existing UUID/text `app_log` PK to integer autoincrement, and cutover of the append path so inserts no longer mint UUIDs. Verifies list/query and Execution History still work with integer row ids. Does **not** own log cleanup, debug-contract redesign, or other tables’ PKs.

## In scope

- [X] `pattern.layers.import-discipline` — schema and write ownership stay in the data layer
- [X] `astral.standards.utils-data-late-import-only` — preserve late-import utils→data flush path in `src/utils/logging.py` (no edit; confirm only)
- [X] `astral.standards.in-scope-only` — touch only `app_log` PK / write path and Execution History `LogEntry.id` type
- [X] `astral.standards.database-header-inventory` — update `app_log` header inventory for integer AUTOINCREMENT PK

## Considered but excluded

- [X] `astral.standards.logging-via-utils` — write path already goes through utils logging; this ticket does not redesign logging API surface
- [X] `astral.standards.data-raises-caller-logs` — `add_log_entry` already returns bool / does not log; no change to that contract beyond INSERT shape
- [X] `astral.layers.import-direction` — no new cross-layer imports; UI type-only change
- [X] Other tables’ primary keys / workspace-wide PK consistency (archived AST-867) — parent boundary
- [X] Column rename to `app_log_id` — parent boundary; column stays `id`
- [X] Periodic log cleanup (AST-360) — out of scope
- [X] Debug-contract redesign (AST-538 / AST-976) — out of scope

## Acceptance criteria

- [X] On a fresh database, `app_log` is created with an integer autoincrement primary key (not UUID/text).
- [X] After this change is applied to an existing database that previously used a UUID/text `app_log` primary key, the table’s primary key is integer autoincrement and new rows insert successfully without a client-supplied UUID.
- [X] New log lines from normal application logging appear in `app_log` and are visible in Execution History for the relevant batch with the same level/batch/time filtering behavior as before.
- [X] No other table’s primary-key type is changed by this epic.
- [X] The late-import path from the logging handler into the data-layer append function remains the only runtime utils→data import for `app_log` writes.

## Boundaries

Does **not** own log cleanup, debug-contract redesign, or other tables’ PKs. Does **not** rename the column to `app_log_id`. Does **not** implement periodic log cleanup (AST-360).

## Notes for planning

Intentional single-child monolith — schema, migration, and write cutover must ship together.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1263-change-app-log-id-to-autoincrement-integer`, child `sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-07T21:17:19.993Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` failed on `origin/sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover`: commit `914022e8` is `Merge remote-tracking branch 'origin/dev' into sub/...` (pull merge). That also dragged unrelated archive/AST-1264 history onto the publish tip.

@Ada Lovelace — rewrite the publish ref: drop the origin/dev pull-merge; tip should be AST-1266-only sequence on `origin/ftr/AST-1263-change-app-log-id-to-autoincrement-integer` (sync via `sync-child` / merge ftr, not merge origin/dev). Republish, then Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-08-07T21:15:10.987Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1266
**Publish ref:** `1a907a65` (docs-only; product tip `e1c78811`)
**Overall:** CLEAN

## Plan adherence

- Stage 1 (schema ensure `INTEGER PRIMARY KEY AUTOINCREMENT`, TEXT→INTEGER rebuild with the Revision-1 `DROP TABLE IF EXISTS app_log_new` guard, `add_log_entry` write cutover dropping client UUID minting) matches the plan exactly.
- Stage 2 (`LogEntry.id: string → number` in `AdminPerformanceMonitor.tsx`) matches the plan; no filter/Copy/fetch logic touched.
- Verified read-only claim: `src/utils/logging.py` `_flush_buffer` still late-imports `add_log_entry` and calls it with only `level`/`logger_name`/`message`/`batch_id` (AC5 holds). Self-Assessment (Scope Single-Component / Conf high / Risk Medium) matches the actual diff footprint.

## Pattern conformance

`pattern.layers.import-discipline` (no canon id match; nearest analog `astral.layers.import-direction` — conforms), `astral.standards.utils-data-late-import-only` (conforms), `astral.standards.in-scope-only` (conforms), `astral.standards.database-header-inventory` (conforms).

## Findings

None fix-now, none discuss.

**Advisory:**
- `astral.seed.boot-only-not-hot-path` — the TEXT→INTEGER rebuild branch is gated only by the process-lifetime `_app_log_schema_ensured` flag (fires on first hot-path call, not an explicit boot/migration script). This mirrors existing precedent already in `database.py` (`_ensure_dispatch_task_schema` et al.); not a new pattern from this ticket. Flagging for awareness only.
- The three-dot diff vs `origin/dev` also carries an inherited `test(AST-1264)` commit (`eaf4467a`) via Betty's shared tests lineage (`tests/component/core/test_agent.py`, `test_agent_tasks.py`, 4 test-bible docs). Verified via `git show --stat` on every AST-1266-tagged commit that none of this ticket's own code/test/docs commits touch those files — no scope smuggling by AST-1266.

**Layer/ownership hygiene:** Betty's test commit (`7a2ecc1a`, merged via the single-SHA `merge-tests(AST-1266)` pattern) touches only `tests/` + `docs/test-bible/**`; the engineer's own commits touch only `src/data/database.py`, `AdminPerformanceMonitor.tsx`, and the plan doc. Clean separation.

## Frame diff

(none)

context_tokens≈42000

— Radia

#### betty — 2026-08-07T21:05:54.598Z
## QA test manifest

**Publish:** `origin/sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover` @ `e1c78811`
**Betty delivery:** `merge-tests(AST-1266): origin/tests 7a2ecc1a07b5fd5540a9d7037a637cefb7c59fbd`
**Bible:** `docs/test-bible/data/database/app_log.md`

### Classification

1. **Existing coverage (kept):** `TestAddLogEntry::test_appends_log_row`; `TestListLogEntries::test_filters_by_batch_and_level` — still green; neither asserted on UUID/`id` type.
2. **Broken / obsolete revised:** Execution History Vitest log fixtures used string `id` values — updated to JSON numbers for Stage 2 `LogEntry.id: number`.
3. **Gaps filled:** fresh INTEGER AUTOINCREMENT PK; TEXT→INTEGER migrate (payload + leftover `app_log_new` guard + already-INTEGER noop); write cutover assigns distinct positive ints without client UUID.

### Manifest (test-child)

1. **Data cluster (required):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_app_log.py \
  -q
```

Expect `TestAst1266IntegerPk` + existing append/filter classes green.

2. **Execution History page mocks (required — §6c routed page already covered; numeric ids):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  -t "loads ledger rows|AST-840 log level filter|expands hop-scoped logs"
```

3. **AC5 docs-acceptance (required — read-only; no product edit):**

```bash
rg -n "_flush_buffer|add_log_entry" src/utils/logging.py
```

Expect late `from src.data.database import add_log_entry` **inside** `_flush_buffer` only; buffer keys `level` / `logger_name` / `message` / `batch_id` (no `id`).

**Pass criterion:** items 1–3 — not zero-arg harness / branch-lock gate.

**Integration:** no existing `tests/integration/` scenario covers `app_log` / dispatch-ledger logs — no invent; conftest `_app_log_schema_ensured` reset unchanged.

**Bible shasum** (`git show origin/<publish-ref>:… | shasum`):
- `docs/test-bible/data/database/app_log.md` → `854e92a3bb4fd39d5bda76bca391a8974c11282a`

— Betty

#### joan — 2026-08-07T20:58:48.498Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1266
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover` @ `daa7b7b2`

## Traceability

AC1→S1.2a; AC2→S1.2b + S1.3; AC3→S1.4 + S2; AC4→S1 Files Changed scope; AC5→S1.5. S1 → parent Functional scope 1/2/4; S2 → parent Functional scope 3. No orphan stages; no unmapped AC. R5 pass.

**Considered:** 48 active statutes scored in-session (18 universal + 30 scoped considered, 17 scoped excluded). Zero `violates`, zero `needs-discussion`.

## Round 1 concern is closed

Stage 1 step 2b now opens with `DROP TABLE IF EXISTS app_log_new` before `CREATE TABLE app_log_new`, matching the `DROP TABLE IF EXISTS {tmp}` guard in `_drop_entity_agent_responses_column`. The temp name stayed generic (`app_log_new`, in line with the existing `dispatch_task_new` rebuilds) rather than picking up the precedent's ticket-stamped `_ast984_next`, so `astral.standards.names-not-ticket-ids` is satisfied too. `## Revisions` records Revision 1 and the Decision block carries the reasoning.

I re-derived why that one statement matters, and the revised plan is now airtight rather than merely better. `_get_connection` uses `sqlite3.connect` at the default isolation level, so the implicit transaction opens at the `INSERT INTO app_log_new … SELECT` and stays open across `DROP TABLE app_log` and `ALTER TABLE app_log_new RENAME TO app_log` until the explicit `conn.commit()`. The destructive half of the rebuild is therefore atomic — a crash there rolls back to the intact TEXT-PK table. The one window that was **not** covered by that transaction was the autocommitted `CREATE TABLE app_log_new` that precedes it, which is exactly the window the new `DROP TABLE IF EXISTS` now clears on the retry. Guard plus implicit transaction together close the full interruption surface, and bootstrap can no longer be bricked by a stray temp table.

## Re-verified against the tip

I re-checked the plan's factual claims about current code rather than carrying them over from round 1, and they all hold.

- `_ensure_app_log_schema` is still create-only with `id TEXT PRIMARY KEY` and the six columns the plan's CREATE reproduces; `add_log_entry` still mints `str(uuid.uuid4())` and uses `INSERT OR IGNORE`; `list_log_entries` is `SELECT *` + `ORDER BY created_at DESC` and never touches `id`. `uuid` has 124 other uses in `database.py`, so the plan is right to keep the module-level import.
- **Nothing depends on the id being a string.** The only `list_log_entries` consumers are the dispatcher passthrough, `monitor._format_log_body` (reads `created_at` / `level` / `message` only), and the `api_admin` `/dispatch_ledger/<batch_id>/logs` passthrough that jsonifies rows as-is. In the frontend the sole use is `key={entry.id}` at `AdminPerformanceMonitor.tsx:488`, and that page is the only file in the whole frontend that consumes a log row. Widening `LogEntry.id` to `number` is sufficient; `string | number` really would be dead weight.
- **No index is lost.** `app_log` has no `CREATE INDEX` anywhere, so the rebuild does not need the best-effort index restoration the `company` / `job` precedent performs.
- **AC2 fires on the deployed DB before any concurrent writer exists.** `server.py` calls `bootstrap_runtime()` at import; `bootstrap.py` runs `ensure_all_upsert_registry_schemas_at_startup()` (which resets the `_app_log_schema_ensured` flag so a stale process global cannot skip DDL on a legacy file) *before* `start_scheduler()`. And the DB log handler flushes inline from `emit` under its own lock with no timer thread, so there is no background writer racing the rebuild.
- **Step 5's read-only assertion matches reality**, so the stop-and-comment instruction is a real guard rather than boilerplate: `_flush_buffer` late-imports `add_log_entry` inside the method and calls it with `level` / `logger_name` / `message` / `batch_id` only — no `id` key in the buffer dict (AC5).
- **No test invalidation, so the absence of a Betty contract section is correct.** `tests/component/data/database/test_app_log.py` has two tests — `add_log_entry(...) is True` and a batch/level filter assertion on `message` — and neither asserts on `id`, the UUID, or the DDL. The `_app_log_schema_ensured` entries in the various `conftest.py` files are flag resets.

## Findings

No `fix-now`. No `discuss`.

### acceptable

- `astral.seed.boot-only-not-hot-path` is the one statute with a live tension worth naming: it forbids provisioning inside "recurring `_ensure_*_schema` hot paths." I scored it `conforms`. Its statement and both violating examples target seed and catalog **row** provision, not DDL; the actual trigger here is `bootstrap_runtime` (the statute's own conforming example) because `app_log` is registered in `_UPSERT_LAZY_SCHEMA_HANDLERS`; and the rebuild is type-guarded by `PRAGMA table_info`, so it cannot re-fire after the first success. A stricter reading would condemn every existing migration in `database.py`, which is not what the corpus says.
- Dropping `INSERT OR IGNORE` is right: every column except the new PK is nullable, so `OR IGNORE` was only ever swallowing client-UUID collisions, and the surrounding try / rollback / `return False` still absorbs genuine write errors without raising into the logging handler (`astral.standards.data-raises-caller-logs` → conforms, unchanged AST-388 contract).
- Discarding old UUID values on copy is safe given the no-FK finding above, and copying `created_at` explicitly keeps ordering intact since `list_log_entries` sorts on that column, never on `id`.
- Detecting via the declared type of the `id` column does not handle an `app_log` that exists without an `id` column, but this helper is the only thing that has ever created the table and it always creates `id` — not worth a plan revision.
- `astral.standards.database-header-inventory` → conforms: step 1 updates the `app_log` bullet in the same change as the schema helper, which is the statute's conforming example.

Self-assessment is honest: `Single-Component` / `high` conf / `Medium` risk match the actual shape, and the risk line names the real hazard rather than minimizing it.

Status → Plan Approved.

— Joan

context_tokens≈68000

#### ada — 2026-08-07T20:52:57.340Z
[plan-discuss] round=1 reply

Addressed the leftover-temp-table guard.

**Delta:** Stage 1 step 2b now opens with `DROP TABLE IF EXISTS app_log_new` before `CREATE TABLE app_log_new`, matching `_drop_entity_agent_responses_column`. Temp name stays `app_log_new` (not ticket-stamped). Decision + naming self-review updated; `## Revisions` Revision 1 recorded.

**Publish:** `origin/sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover` @ `daa7b7b2`

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover/docs/features/foundation/ast-1266-app-log-integer-pk-schema-migration-and-write-cutover.md

**Self-assessment** (unchanged)
- **Scope:** Single-Component
- **Conf:** high
- **Risk:** Medium — interrupt mid-rebuild no longer bricks subsequent boots via stray `app_log_new`

#### joan — 2026-08-07T20:51:30.390Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1266
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover` @ `2680e51d`

## Traceability

AC1→S1.2a; AC2→S1.2b + S1.3; AC3→S1.4 + S2; AC4→S1 Files Changed scope; AC5→S1.5. S1 → parent Functional scope 1/2/4; S2 → parent Functional scope 3. No orphan stages; no unmapped AC. R5 pass.

**Considered:** 48 active statutes scored in-session (18 universal + 30 scoped considered, 17 scoped excluded). No R3 `violates`; the finding below is an R6 missing-step, not a statute breach.

## Verified against the tip (plan is accurate where it describes today's code)

- `_ensure_app_log_schema` is create-only with `id TEXT PRIMARY KEY`, gated on `_app_log_schema_ensured`, and the six columns the plan's CREATE reproduces match the live DDL exactly (`id`, `level`, `logger_name`, `message`, `batch_id`, `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`). `add_log_entry` really does mint `entry_id = str(uuid.uuid4())` and use `INSERT OR IGNORE INTO app_log (id, …)`; `list_log_entries` is `SELECT *` + `ORDER BY created_at DESC` and never touches `id`.
- **“Nothing references `app_log.id`” holds end to end.** The only consumers of `list_log_entries` are the dispatcher passthrough, `monitor._format_log_body` (reads `created_at` / `level` / `message` only), and `api_admin` `/dispatch_ledger/<batch_id>/logs`. In the frontend the sole use is `key={entry.id}` at `AdminPerformanceMonitor.tsx:488` — no string operations, no comparisons — so widening the type to `number` is sufficient and `string | number` really is unnecessary.
- **No index is lost.** `app_log` has no `CREATE INDEX` anywhere, so the DROP/RENAME rebuild does not need the best-effort index restoration the precedent performs for `company` / `job`. There is also exactly one writer.
- **No test invalidation, so the absence of a Betty contract section is correct, not an omission.** `tests/component/data/database/test_app_log.py` holds two tests — `add_log_entry(…) is True` and a batch/level filter assertion on `message` — and neither asserts on `id`, the UUID, or the DDL. The `_app_log_schema_ensured` entries in the various `conftest.py` files are flag resets. Both tests stay green after Stages 1–2.
- **AC2 will actually fire on the deployed DB, and the rebuild is single-threaded.** `server.py` calls `bootstrap_runtime()` at import, which runs `ensure_all_upsert_registry_schemas_at_startup()` — `app_log` is in `_UPSERT_LAZY_SCHEMA_HANDLERS`, and `ensure_table_schema_for_upsert` deliberately resets the `_*_schema_ensured` flag first so a stale process global cannot skip the DDL on a legacy file. That happens **before** `start_scheduler()`, so the migration completes before any dispatcher thread can call `add_log_entry`. I went looking for a concurrent-rebuild race and this ordering closes it — no finding.

## Findings

### fix-now — the rebuild omits the precedent's leftover-temp-table guard, and here that costs a boot

Stage 1 step 2b goes straight to `CREATE TABLE app_log_new`. The precedent the plan cites for this rebuild, `_drop_entity_agent_responses_column`, opens with `conn.execute(f"DROP TABLE IF EXISTS {tmp}")` before its `CREATE`, precisely so an interrupted earlier rebuild cannot poison the next run.

Without it: if the process dies between `CREATE TABLE app_log_new` and `ALTER TABLE app_log_new RENAME TO app_log` (deploy restart, OOM, disk error — and this is a one-shot migration against a live Railway DB), `app_log_new` survives while `app_log` still has the TEXT PK. On the next start `_ensure_app_log_schema` re-enters the rebuild branch and `CREATE TABLE app_log_new` raises “table app_log_new already exists.”

That exception is not contained. `ensure_table_schema_for_upsert` calls the handler with no `try`/`except`, `ensure_all_upsert_registry_schemas_at_startup` only wraps a `finally: conn.close()`, and `bootstrap_runtime()` is invoked at module import in `server.py` — so the server fails to boot, and it keeps failing every restart until someone drops the stray table by hand. (Even reaching the lazy path instead, `add_log_entry` would catch the error and `return False` forever because the ensured flag is only set on success, while `list_log_entries` has no `except` and would surface it to Execution History.) This is the exact “wrong migration detection or schema mismatch breaks all `app_log` appends” hazard the plan's own Risk line names.

**Recommendation:** make `DROP TABLE IF EXISTS app_log_new` the first statement of step 2b, matching the cited precedent. Keep the generic `app_log_new` name — do **not** copy the precedent's ticket-stamped `_ast984_next`, which would run against `astral.standards.names-not-ticket-ids`.

### acceptable

- Dropping `INSERT OR IGNORE` is right: every column except the new PK is nullable, so `OR IGNORE` was only ever swallowing client-UUID collisions, and the surrounding `try` / `rollback` / `return False` still absorbs genuine write errors without raising into the logging handler (`astral.standards.data-raises-caller-logs` → conforms).
- Discarding old UUID values rather than preserving them is safe given the no-FK finding above, and copying `created_at` explicitly keeps ordering intact since `list_log_entries` sorts on that column, never on `id`.
- `astral.standards.database-header-inventory` → conforms: step 1 updates the `app_log` bullet in the same change as the schema helper, which is the statute's conforming example.
- Step 5's read-only confirmation of the `_flush_buffer` late import, with an instruction to stop and comment on the parent rather than “fix” `logging.py`, is the right way to hold AC5 without touching a file outside the Files Changed table.

Status → Plan Discuss. One fix-now, one statement.

— Joan

context_tokens≈125000

#### ada — 2026-08-07T20:46:17.154Z
Plan published on `origin/sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover` @ `2680e51d`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1263/AST-1266-app-log-integer-pk-schema-migration-and-write-cutover/docs/features/foundation/ast-1266-app-log-integer-pk-schema-migration-and-write-cutover.md

**Self-assessment**
- **Scope:** Single-Component — `database.py` `app_log` ensure/migrate/write + one-field `LogEntry.id` type on Execution History.
- **Conf:** high — CREATE/rebuild/INSERT patterns already live in `database.py` (`dispatch_task` INTEGER AUTOINCREMENT; table rebuild helpers); late-import flush contract stays untouched.
- **Risk:** Medium — a schema/write mismatch would break all `app_log` appends until fixed; isolated to one non-FK table.

---

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

## Resolution

**Date:** 2026-08-07  
**Review:** Radia `[code-rubric] revision=1` — **CLEAN** (docs tip `1a907a65`; product tip `e1c78811`).

**fix-now:** none.  
**Discuss:** none.  
**Advisory:** left as-is — hot-path ensure flag mirrors existing `_ensure_*` precedent; inherited AST-1264 test lineage not introduced by this ticket.

No product code changes in resolve. Publish advances to **User Testing**.

