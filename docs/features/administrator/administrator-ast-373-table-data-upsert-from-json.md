# AST-373 — Table Data Upsert from JSON
**Component:** administrator  
**Children:** AST-464, AST-465  
**Linear archived:** AST-373 2026-06-03  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-05-23 16:32 | AST-464 | test | `c2672d63` | test(AST-464): component tests and bible map for Copy Output table upsert |
| 2026-05-23 16:36 | AST-464 | docs | `315abbf3` | docs(AST-464): Radia review — upsert core + data layer |
| 2026-05-23 16:41 | AST-464 | fix | `3e22dec8` | fix(AST-464): review feedback — advisory guard and orchestrator row numbers |
| 2026-05-23 17:34 | AST-465 | docs | `724310b9` | docs(AST-465): bible sync from dev-betty — §7.13r caveat + §7.13v AST-419 |
| 2026-05-23 17:46 | AST-465 | docs | `c58d18cb` | docs(AST-465): Radia review — table upsert UI + admin API |
| 2026-05-23 17:48 | AST-465 | fix | `92d11069` | fix(AST-465): review feedback — explicit HTTP JSON parse errors |
| 2026-05-23 17:52 | AST-464 | merge | `7191d579` | merge(AST-464): integrate child into AST-373 |
| 2026-05-23 17:52 | AST-465 | merge | `91741763` | merge(AST-465): integrate child into AST-373 — resolve bible §7.13r/u/v |
| 2026-05-23 17:59 | AST-373 | merge | `8c8f581f` | merge(AST-373): prep-uat — ftr rollup into dev for UAT |

_SHAs harvested from the archived docs and verified with `git cat-file`; the `ftr/AST-373` and `sub/*` branches were deleted after landing, so these commits are not reachable from `origin/dev` under these SHAs in this repo. AST-465 build commits are declared in-doc as `b6c69025` (Flask route) and `f4ced60e` (Data Management UI) but do not resolve here. The parent rollup reached `origin/dev` around tip `5ecb689d` per the landing comment._

## Epic — AST-373
_Archived: 2026-06-03 · Linear URL: https://linear.app/astralcareermatch/issue/AST-373/table-data-upsert-from-json · Status at archive: Done · Project: Astral Administrator · Assignee: susan · Priority / estimate: High / —_

### Purpose

Database content drifts between environments — admin prompts, candidate records, and anything else Susan maintains in SQLite. Today she can export query results as JSON from Data Management on one server but has no safe way to apply that payload on another. This feature adds a general-purpose, admin-only table upsert on the existing Data Management screen: pick any table, paste Copy Output JSON from a source environment, validate before write, and merge rows into the target without silent data loss.

### Functional scope

* **Replace the Backfill Culture Links block** on Data Management with a new **Table Upsert** section. The ad-hoc SQL query panel and schema browser remain unchanged.
* **Table selector:** A dropdown listing **every user table** in the database (same table list the schema browser uses). The component is table-agnostic — Susan chooses the target table; the feature does not hard-code an allowlist.
* **Update flow:** An **Update** button opens a modal with a large text area. Susan pastes JSON copied from Data Management’s **Copy Output** (the array produced by a `SELECT` on the source server for that same table).
* **Validate-then-apply:** Before any write, parse the JSON and validate the payload against the selected table’s structure (array of objects; column names must match the table; required key columns present; values compatible enough to attempt insert/update). If validation fails, show a clear error and **change nothing**.
* **Primary key required:** Upsert is only offered for tables that declare a primary key (single- or multi-column). Tables without a PK are rejected up front with a clear message — Susan fixes the schema separately (see note on **timesheets** below).
* **Upsert behavior (general):** For each validated row, insert if the row’s primary key is absent in the target, or update the existing row if the primary key matches. Single-column and **composite** primary keys are both supported — match on the full key.
* **Upsert behavior (agent_task exception):** When the selected table is **agent_task**, apply the versioning rules already used by Manage Tasks: unchanged historical rows in the paste are **no-ops**; new or changed content retires the prior active row and inserts a new current version. This is the one table-specific semantic the generic component must honor.
* **Foreign keys — all-or-nothing:** If any row would violate a foreign-key constraint in the target database, **cancel the entire job** and write **zero rows**. Susan fixes parent data or import order and retries.
* **Non-destructive merge:** Rows present in the target database but **not** included in the pasted JSON are left untouched. No table-wide replace, truncate, or delete-by-omission.
* **Feedback:** After submit, show a clear outcome — success with counts (inserted / updated / skipped no-ops) or a specific validation or constraint error. A failed validation or failed apply must not partially corrupt unrelated rows.

### Boundaries

* **Any table, not any SQL:** Susan selects a table and pastes row JSON. No free-form SQL in the upsert path, no multi-table payloads, no arbitrary-table writes in one operation.
* **No export generation:** Susan continues to produce JSON via the existing SQL panel and Copy Output on the source server. This feature does not add export-to-file or repo-tracked snapshots (see [AST-381](https://linear.app/astralcareermatch/issue/AST-381/pushing-database-content-to-github)).
* **No delete/sync-down:** Omitted rows stay in the target DB. Susan handles cleanup manually if needed.
* **No environment automation:** Nothing runs on deploy, bootstrap, or scheduler tick.
* **No diff/diagnostic UI:** Comparison between environments (see [AST-438](https://linear.app/astralcareermatch/issue/AST-438/production-readiness-admin-prompt-and-rubric-diagnostic), done) is out of scope.
* **No PK schema fixes in this ticket:** Adding a primary key to a table that lacks one (e.g. **timesheets**, which today has `anthropic_req_id UNIQUE` but no PK) is out of scope here — Susan addresses that in a separate schema ticket.
* **Must not break:** Existing Data Management SQL execution, schema browser, Manage Agents, Manage Tasks, and runtime prompt resolution.
* **Admin-only:** Same authorization model as other Data Management operations.
* **Susan accepts operational risk:** Porting entity data (e.g. candidates) between environments is intentional; the tool does not enforce business rules beyond schema validation and database constraints.

### Acceptance criteria

 1. The Backfill Culture Links section is removed from Data Management; the Table Upsert section appears in its place.
 2. The table dropdown lists all user tables in the database (not a fixed allowlist).
 3. Clicking **Update** opens a modal with a large JSON text area and a confirm action to apply the upsert.
 4. Malformed JSON, a non-array payload, column mismatches, rows missing required primary-key fields, or a selected table with **no primary key** produce an error message and **zero rows changed**.
 5. For a generic table with a single-column primary key, pasting valid Copy Output JSON upserts all listed rows by primary key; rows not in the JSON remain unchanged.
 6. For a table with a **composite primary key**, upsert matches on the full key set.
 7. For **agent_task**, pasting Copy Output JSON that includes multiple version rows per **task_key** applies new/changed versions using existing Manage Tasks versioning semantics; unchanged historical rows are no-ops.
 8. If any pasted row would fail a foreign-key constraint, the entire operation is cancelled and **zero rows** are written.
 9. Susan can port a candidate (or any other table’s rows) from dev to prod by selecting that table, pasting Copy Output from the source, and seeing the rows merged in the target.
10. On success, Susan sees how many rows were inserted, updated, and skipped as no-ops.

### Dependencies and blockers

None. Data Management, the admin API, and the database schema browser already exist.

### Open questions

None. _(Resolved during definition — see the decision trail below.)_

### Original brief

Right now, the local database has updated admin-level prompt content (not candidate specific), and I need a way to export those prompts to a file that can then be imported in production and synched there so that agent performance is consistent across environments.

Actually, this is VERY SIMPLE, because I'm talking about the agent table and the agent_tasks tables.  There's no magic.

I want to update the Data Management screen to replace the backfill culture links section with a table select dropdown list and a "Update" button that leads to a popup for a large text input, into which I can paste the contents of "Copy Output" json from a select \* statement results from another server (e.g. local), and click "Update" to upsert the content.  Do not delete extant content not included in the JSON (that's easy cleanup and I'd rather not silently lose content.)

#### Comments — definition decision trail (Chuckles ↔ Susan, 2026-05-23)

- **22:29** — Definition draft: v1 scope limited to **agent** + **agent_task** upsert via pasted Copy Output JSON; Backfill Culture Links replaced; non-destructive merge only (no deletes for omitted rows; separate from AST-381 repo-snapshot work). 2 open questions (agent_task versioning semantics on import; confirm no other tables in v1).
- **22:34** — Per Susan's versioning note: **agent_task** import accepts full Copy Output including old version rows; unchanged historical rows are **no-ops**; new/changed content applies via existing Manage Tasks versioning (retire prior active, new row current); success feedback includes skipped no-op count. One open question: confirm v1 is agent + agent_task only.
- **22:39** — **Scope expanded per Susan's direction:** table dropdown lists **all user tables** — generic upsert, not an allowlist; validate JSON against selected table schema **before any write** (mismatch = error, zero rows changed); **agent_task** keeps versioning/no-op semantics, everything else upserts by discovered primary key; candidate (and any table) porting dev → prod explicitly in scope. Three new open questions: composite PKs, tables with no PK, FK failure handling.
- **22:52** — **All open questions resolved:** Composite PK → upsert on the **full key**. No PK → **reject up front**; schema fix is separate (**timesheets** is the offender — `anthropic_req_id UNIQUE`, no PRIMARY KEY). FK failure → **cancel the entire job**, zero rows written. Ready for approval → dispatch.

_Child assignment (Chuckles dispatch): Ada → AST-464 data layer + core upsert engine, agent_task versioning, transactional FK handling; Katherine → AST-465 AdminDataManagement UI, admin API endpoint, remove Backfill Culture Links (blocked by AST-464)._

### Manual test steps

**Prerequisites:** Admin session; local `dev` checked out; app restarted (`python3 ./src/ui/server.py` or your usual start). Have Copy Output JSON from another env (or run SELECT on local first).

1. Open **Administrator → Data Management**. Confirm **Backfill Culture Links** is gone and **Table Upsert** appears (table dropdown + **Update** button).
2. Confirm the **ad-hoc SQL panel** and **schema browser** still work (unchanged).
3. **Table dropdown:** lists user tables (not a hard-coded allowlist). Pick **`agent`**.
4. On source (or same DB): run `SELECT * FROM agent` in SQL panel → **Copy Output**. Paste into Table Upsert modal → **Update**. Expect success with insert/update counts; rows merge by PK; rows not in JSON remain.
5. Repeat for **`agent_task`** with Copy Output that includes version history. Unchanged historical rows should be **no-ops**; new/changed content should version per Manage Tasks semantics.
6. **Validation — no writes:** paste malformed JSON → error, zero rows changed.
7. **Validation — no PK:** select **`timesheets`** (no PK) → clear rejection message, zero rows changed.
8. **FK all-or-nothing:** paste rows referencing missing parent FKs → entire job cancelled, zero rows written.
9. **Composite PK** (if you have a suitable table): upsert matches on full key set.
10. Success toast/summary shows inserted / updated / skipped no-op counts.

_Also fixed in the UAT prep: duplicate `boards_bp` registration in `src/ui/server.py` (startup crash)._

### Files changed (plan vs actual)

_Per-file detail is in the two sub-issue tables below. Parent-level: `merge(AST-373): prep-uat` (`8c8f581f`) rolled the `ftr/AST-373` branch (Betty rollup `91741763`, ancestry incl. `7191d579`) into `dev` for UAT. Betty resolved a `docs/ASTRAL_TEST_BIBLE.md` conflict on the second child merge (§7.13r/u/v) — Betty's tree, reported not edited here._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-464 — generic upsert — data layer and core
_Linear: https://linear.app/astralcareermatch/issue/AST-464/table-data-upsert-from-json-generic-upsert-data-layer-and-core · Parent: AST-373 · Project: Astral Administrator · Assignee: Ada · Feature ref: `sub/AST-373/AST-464-…` (origin only, since deleted)_

#### What this implements

Implements the **backend** for admin table JSON merges: parse Copy Output payloads (arrays of objects keyed by column name), refuse tables without a primary key or malformed payloads **before** any mutation, generic upsert by SQLite primary key (single or composite) with **all-or-nothing** transactional semantics when foreign-key enforcement fires, structured counts (`inserted` / `updated` / `skipped`), and an **`agent_task`-specific branch** that preserves Manage Tasks versioning (via refactored `save_agent_task` logic on a shared connection). **AST-465** wires the Flask route and UI; this ticket delivers **only** `src/data/database.py` and a **new core module** — **no** `api_admin` routes and **no** React.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/data/database.py` | PK discovery helper; generic upsert-by-PK on an existing connection; refactor `save_agent_task` internals to accept a caller-owned `sqlite3.Connection` (no commit); `agent_task` import path that runs historical rows + current-row versioning **inside the same transaction** | `c2672d63`+ (product SHA not named in doc); `3e22dec8` (review fixes) |
| ✓ | `src/core/table_copy_upsert.py` (new) | `json.loads`, structural validation, `PRAGMA foreign_keys=ON`, `BEGIN` / `COMMIT` / `ROLLBACK`, dispatch generic vs `agent_task`, map `sqlite3.IntegrityError` to failed result with zero writes | `c2672d63`+; `3e22dec8` |
| ⚠ not touched | `src/ui/**`, `src/utils/config.py` | plan: no changes unless a hard blocker appears (none did) | — |
| | _tests + bible_ | — | `c2672d63` — component tests + `docs/test-bible` / `docs/ASTRAL_TEST_BIBLE.md` map (Betty's tree) |

#### Stage 1: Primary key discovery and `save_agent_task` connection refactor

**Done when:** `save_agent_task` behavior is unchanged for all existing callers (Manage Tasks / tests); new internal entry point runs the same SQL as today but on a passed-in `conn` without committing or closing it.

1. In `src/data/database.py`, add **`primary_key_column_names(conn: sqlite3.Connection, table: str) -> list[str]`**:
   - Confirm the table exists with the same existence check pattern as **`table_columns`** (`sqlite_master` lookup); if missing, raise **`ValueError`** with a short message.
   - Read **`PRAGMA table_info(table)`**; collect rows where **`pk != 0`**, ordered by **`pk`** ascending then **`cid`** ascending so composite keys match SQLite’s column order.
   - If the result is **empty**, raise **`ValueError`** naming the table (tables without a PK are rejected — the AST-373 note on **timesheets** stays out of scope).
2. Refactor **`save_agent_task`**: move the body currently inside its **`_with_conn`** closure (from after **`_ensure_agent_task_schema(conn)`** through the final state before **`conn.commit()`**) into a new **`_save_agent_task_on_connection(conn, task_key, *, agent_id=None, …) -> None`** that **never** calls **`commit`**, **`close`**, or **`_get_connection`**, and does **not** wrap in **`_run_with_retry`**. Implement **`save_agent_task`** as: open connection, **`_ensure_agent_task_schema`**, call **`_save_agent_task_on_connection`**, **`commit`**, **`close`**, preserving **`_run_with_retry`** as today.
3. **`python3 -m py_compile`** on **`database.py`**; run existing tests only if Susan or `test-astral` asks.

⚠️ **Decision:** Retry stays at the **`save_agent_task` outer** boundary only — the batch importer (Stage 3) runs on a single long-lived transaction and uses **`BEGIN`/`ROLLBACK`** in core; nested per-row **`_run_with_retry`** would fight all-or-nothing semantics, so the **`agent_task` batch path** calls **`_save_agent_task_on_connection`** directly, not **`save_agent_task`**.

#### Stage 2: Generic UPSERT primitive (non–`agent_task`) on caller connection

**Done when:** For any non–`agent_task` user table that has a PK, the data layer can apply a list of row dicts and return accurate **`inserted`**, **`updated`**, **`skipped`** counts **without committing**.

1. Add **`apply_generic_table_copy_upsert(conn, table, rows) -> dict[str, int]`** in **`src/data/database.py`**:
   - Compute **`columns_ordered = table_columns(conn, table)`** (existing helper).
   - Compute **`pk_cols = primary_key_column_names(conn, table)`** — must be non-empty or raise (caller should already gate; defense in depth here).
   - **Row shape:** Each **`rows[i]`** must have **exactly** the keys **`set(columns_ordered)`** — extra or missing key → raise **`ValueError`** naming the row index (1-based in message for Susan readability).
   - **Values:** Bind using SQLite parameters only — never interpolate user strings into SQL identifiers beyond table/columns already validated via **`sqlite_master`** + **`PRAGMA`**. Build one **`INSERT … ON CONFLICT(pk_cols) DO UPDATE SET`** statement assigning every non-PK column **`excluded.col`** (PK columns only appear in the `INSERT` column list).
   - **Counts:** Before executing each row, **`SELECT 1 FROM … WHERE …`** with PK equality parameterized — if the row exists **and** all non-PK columns already equal pasted values (normalize `None`/JSON `null` the same), increment **`skipped`** and do not execute; if exists and differs → upsert → **`updated`**; if absent → **`inserted`**.
   - **Types:** Payload values arrive as JSON scalars (`None`, bool, int, float, str). **Reject** `dict` / `list` cell values with **`ValueError`** (Copy Output rows are flat).
   - Return **`{"inserted": int, "updated": int, "skipped": int}`** only (no commit).
2. **`python3 -m py_compile`** on **`database.py`**.

⚠️ **Decision:** `JSON`/`BLOB` affinity columns rarely appear in Copy Output; bind Python `str` for text and `int`/`float` for numbers as SQLite accepts. If a cast fails during execute, bubble `sqlite3.IntegrityError` or `OperationalError` to core for rollback (failure path).

#### Stage 3: `agent_task` import path + core orchestrator

**Done when:** A single JSON string plus table name yields a result dict (success or error) with FK-safe rollback; **`agent_task`** honors versioning for **`current`** rows and no-op semantics for untouched historical rows.

##### 3a — Data layer: `agent_task` rows on existing connection

1. Add **`apply_agent_task_copy_upsert(conn, rows) -> dict[str, int]`** in **`src/data/database.py`**:
   - Require **`table_columns(conn, "agent_task")`**; each input dict’s keys must match that set exactly (same rule as Stage 2).
   - Normalize **`current`** from JSON (`1`/`0` or `True`/`False`) to integer `0` or `1` for comparisons; reject other values with **`ValueError`**.
   - Group by `task_key`; apply historical (`current=0`) rows first, then the `current=1` row through the shared `_save_agent_task_on_connection` versioning path; unchanged rows count as `skipped`.

##### 3b — Core orchestrator: `src/core/table_copy_upsert.py`

1. Acquire **`conn = database._get_connection()`** once (or a context manager that does **not** auto-commit on exit — verify `sqlite3.Connection.__exit__`; if it auto-commits, use explicit `try`/`finally conn.close()`).
2. **`conn.execute("PRAGMA foreign_keys=ON")`** then **`SELECT foreign_keys`** read to assert `1`; if not enforced, raise **`RuntimeError`** (fail closed).
3. **`json.loads(json_payload)`** — on `JSONDecodeError` return `ok=False`, `error="Malformed JSON"` (no DB writes).
4. If top-level is not a `list` → `ok=False`, `error="Payload must be a JSON array"`.
5. If any element is not a `dict` → `ok=False`, `error="Each row must be an object"` (include first bad index in message).
6. Validate **`table_name`** exists via **`database.table_columns(conn, table_name)`** (`ValueError` → `ok=False`).
7. **`pk_cols = primary_key_column_names`** — `ValueError` → `ok=False` ("table has no primary key").
8. If **`table_name == "agent_task"`**: inside **`BEGIN IMMEDIATE`**: call `database._ensure_agent_task_schema(conn)` then `database.apply_agent_task_copy_upsert(conn, parsed_rows)`; `COMMIT` on success.
9. **Else**: `BEGIN IMMEDIATE` → `database.apply_generic_table_copy_upsert` → `COMMIT`.
10. **`except sqlite3.IntegrityError`** (FK or unique): `ROLLBACK`, `ok=False`, `error=str(e)` or a Susan-safe short prefix plus UNIQUE/FK context (no partial writes).
11. **`except ValueError as e`:** `ROLLBACK` if in transaction; `ok=False`, `error=str(e)`.
12. On success `ok=True`, merge count dict keys into response.

⚠️ **Decision:** `BEGIN IMMEDIATE` reduces lock races for admin tooling; acceptable for SQLite single-writer semantics.

Imports: `sqlite3`, `json`, `typing`, `src.data.database` as `database` — no UI imports. Compile: `python3 -m py_compile src/core/table_copy_upsert.py`.

#### Self-Assessment

**Scope:** `Single-Component` — one new `core` orchestrator plus focused `database.py` primitives and a refactor of `save_agent_task` for transaction sharing; UI / API untouched here.
**Conf:** `Medium` — clear patterns (`PRAGMA`, `ON CONFLICT`, existing `save_agent_task` versioning); `agent_task` import classification needs careful counting but stays within documented semantics.
**Risk:** `HIGH` — wrong upsert or broken FK rollback could corrupt admin data across tables; transactional discipline and FK pragma are load-bearing.

#### Plan vs ASTRAL_CODE_RULES

| Section | Alignment |
|---------|-----------|
| §1.3 DRY | Reuse `table_columns`; PK helper shared by generic + validation; refactor `save_agent_task` rather than duplicate versioning logic. |
| §2.1 Config | No new config block — admin path is explicitly generic per table. |
| §2.6 State machine | Dispatch / candidate / company flows untouched. |
| §3.3 Imports | Core → data only in new module; data → utils unchanged. |
| §3.5 Naming | Python `snake_case`; new module name mirrors behavior (`table_copy_upsert`). |

#### Review (Radia, diff at `c2672d63e29d42cce7d4ab285253846150cec0e7`)

**What's solid:**
- **Plan fidelity:** delivered `src/core/table_copy_upsert.py` transactional shell (`PRAGMA foreign_keys`, `BEGIN IMMEDIATE`, rollback on `IntegrityError` / `OperationalError` / validation), `primary_key_column_names`, `apply_generic_table_copy_upsert`, `apply_agent_task_copy_upsert` (historicals before `current`), and `save_agent_task` refactor via `_save_agent_task_on_connection` with `import_explicit` for Copy Output — matches the combined plan and ticket boundaries (no UI / `api_admin` here).
- **ASTRAL_CODE_RULES:** new work stays core → data; data layer continues to raise / return counts without ad-hoc logging; dynamic SQL uses quoted identifiers for DML; nested JSON cells rejected.
- **Risk controls:** component tests cover malformed JSON, non-array payload, unknown table, no-PK table, composite PK insert/update/skip, nested cell rejection, FK violation → zero net rows, `agent_task` duplicate `current=1` rejection, idempotent `agent_task` reapply skips.

**Issues:** none graded fix-now.

**Recommended actions:**
| Severity | Topic | Recommendation |
| --- | --- | --- |
| discuss | `ASTRAL_TEST_BIBLE.md` scope vs ticket | The branch diff inserts bible subsections `7.13o`–`7.13t` for other Astral tickets in the same hunks as `7.13u` (AST-464). Prefer landing bible rows with the owning ticket merges (or splitting commits) so AST-464 reviews stay narrowly attributable. |
| discuss | Orchestrator vs data-layer row index wording | `apply_copy_output_table_upsert` uses 0-based indices in the "row must be an object" error string; `apply_*_copy_upsert` uses 1-based row numbers for shape errors. Consider aligning (usually 1-based for admin-facing copy/paste). |
| discuss | `PRAGMA table_info` identifier | `primary_key_column_names` builds `PRAGMA table_info({table})` with an unquoted table token after `sqlite_master` validation. Low practical risk for normal names; quoting would match the care used elsewhere. |
| advisory | Tables whose non-PK column set is empty | `ON CONFLICT … DO UPDATE SET` with an empty `non_pk_clause` would not be valid SQLite if such a table ever appears. No evidence in reviewed tests/products; skip unless admin targets an all-primary-key layout. |

Linear: Review Posted, fix-now 0 · discuss 3 · advisory 1; assignee unchanged (implementer).

#### Resolution

**2026-05-23 — Ada (resolve-astral, post-Radia `315abbf3`):**
- **Fix-now:** none required (Radia 0).
- **Discuss:** no Susan direction to change bible commit attribution (AST-464 stays product-only on this branch; bible scope is Betty's lane). **Row index:** orchestrator error for non-object rows now uses 1-based `row N` wording to match the data layer. **`PRAGMA table_info`** unquoted identifier left as a low-risk tracked note unless quoting is standardized project-wide.
- **Advisory:** generic upsert now **rejects** tables whose columns are all primary key with a clear `ValueError` before building SQL.
- **Merge:** `dev-ada` rebased onto `origin/dev`; publish tip merged with Radia's review section retained (`3e22dec8`).

### AST-465 — Data Management UI and admin API
_Linear: https://linear.app/astralcareermatch/issue/AST-465/table-data-upsert-from-json-data-management-ui-and-admin-api · Parent: AST-373 · Project: Astral Administrator · Assignee: Katherine (built) · Blocked by: AST-464 · Feature ref: `ftr/AST-465` (origin only, since deleted)_

**Sibling contract:** AST-464 — core module `apply_copy_output_table_upsert` (see the AST-464 sub-issue above).

#### What this implements

Replaces **Backfill Culture Links** on the Data Management admin page with **Table Upsert**: a table picker (every user-visible table listing, same discovery query as today’s schema browser), an **Update** button that opens a modal with a large JSON paste field, `window.confirm` before apply, and a new **`POST /api/admin/data/table_copy_upsert`** route that `@require_auth` wraps thinly around `apply_copy_output_table_upsert` from `src.core.table_copy_upsert` so Susan can paste Copy Output rows from another environment and receive **inserted / updated / skipped** counts from the `ok: true` path or actionable `error` text from validation / FK failures with **zero** rows committed on failure (AST-464).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/api/api_admin.py` | Add `POST /api/admin/data/table_copy_upsert`; import `apply_copy_output_table_upsert` from `src.core.table_copy_upsert`; keep `/api/admin/script/backfill_culture_links/*` Flask routes untouched (dead from UI perspective) | `b6c69025` (doc-declared; unresolved here); `92d11069` (review fix) |
| ✓ | `src/ui/frontend/src/pages/AdminDataManagement.tsx` | Remove backfill JSX + hooks + `BackfillCompany`/`api` polling; add Table Upsert card + `Modal` + `runSql`/API wiring for table dropdown + `table_copy_upsert` POST handling + toasts | `f4ced60e` (doc-declared; unresolved here) |
| ⚠ optional | `src/ui/frontend/src/App.css` | TOC + rules only if `Modal`/textarea clipping requires it | — (not needed) |
| ✗ do-not-edit | `tests/component/frontend/pages/test_AdminDataManagement.test.tsx` | Betty-owned (`[qa-handoff]`) — drop mocks/assertions for `/api/admin/script/backfill_culture_links/*` once UI no longer renders Backfill Culture Links | Betty's tree — reported not edited |

#### Preflight blocker (STOP without guessing — build-astral step 4)

`build-astral` must run only when `origin/dev` includes AST-464 (`blockedBy` in Linear; typical order Ada Review Posted → Katherine build). Before Stage 1 code: (1) confirm `python3` can import `from src.core.table_copy_upsert import apply_copy_output_table_upsert` from repo root; (2) confirm signature `apply_copy_output_table_upsert(*, table_name: str, json_payload: str) -> dict[str, Any]` and return mapping `ok`, `inserted`, `updated`, `skipped`, `error` — inspect `table_copy_upsert.py` and match the Flask JSON shape literal-for-literal. If module or signature mismatches the AST-464 plan excerpt → **STOP**: Linear comment `🛑` on AST-373 per execution contract. _(This blocker fired in practice — Katherine posted a `🛑` on 2026-05-23 23:25 because `origin/dev` had no `src/core/table_copy_upsert.py` yet; build resumed once AST-464 was merged onto `dev-kath`.)_

#### Stage 1: Flask admin endpoint

**Done when:** `curl`/browser POST with Bearer token succeeds on happy path (200, counts) and rejects empty table / missing body (400) without touching `require_ip`.

1. **`api_admin.py`:** add `from src.core.table_copy_upsert import apply_copy_output_table_upsert` next to sibling `src.core` imports (do not import `src.data` in UI layer).
2. After `run_sql` in the Data Management section (before `upsert_config_table`, same auth story), declare `@admin_bp.route("/data/table_copy_upsert", methods=["POST"])` / `@require_auth` / `def admin_table_copy_upsert():`.
3. `body = request.get_json(silent=True) or {}`. `table = (body.get("table") or "").strip()`; `json_payload = body.get("json_payload")`.
4. If `not table` → `return jsonify({"ok": False, "error": "table is required"}), 400`.
5. If `json_payload is None` → 400, `{"ok":false,"error":"json_payload is required"}`.
6. If `not isinstance(json_payload, str)` → 400, `{"ok":false,"error":"json_payload must be a JSON text string — paste Copy Output verbatim"}`.
7. `result = apply_copy_output_table_upsert(table_name=table, json_payload=json_payload)`.
8. `jsonify(result)`. HTTP **400 whenever `result["ok"] is False`**; reserve **500** only if `apply_copy_output_table_upsert` raises (Flask handler catches `Exception` → `jsonify({"ok":False,"error":str(e)}), 500`).

⚠️ **Decision:** No duplicated `json.loads` in Flask — all semantics live in `table_copy_upsert` per §3.3 layer separation.

#### Stage 2: Remove Backfill UI + scaffolding

**Done when:** `AdminDataManagement.tsx` renders no Backfill Culture Links, no `/api/admin/script/backfill_culture_links` calls, TypeScript `tsc` clean.

1. Delete `interface BackfillCompany` and all backfill-prefixed `useState` / `useRef` / `useEffect` / `fetchBackfillCompanies` / `handleBackfill` / JSX block.
2. Remove `confirm("Backfill` usage.

⚠️ **Decision:** Leaving `api_admin` backfill routes avoids engineer-owned `tests/component/ui/api` churn; Betty updates the `AdminDataManagement` component test only (`[qa-handoff]`).

#### Stage 3: Table Upsert UX + `Modal` + wire-up

**Done when:** user selects a table → **Update** opens a wide modal (`size="wide"`) with a monospace textarea (rows ≥ 16, width `"100%"`) → **Save** ensures a non-empty paste → `window.confirm("Apply JSON upsert into table \"${table}\"? Unrelated rows remain untouched.")` → `POST /api/admin/data/table_copy_upsert` → success `Toast` (`variant="success"`) lists inserted / updated / skipped counts; `ok: false` or HTTP error → `Toast variant="error"` with `error` text; on success optionally clear `upsertJson` and close modal.

1. State additions: `upsertTable`, `upsertModalOpen`, `upsertJson`, `upsertPosting`.
2. Table dropdown: reuse `tables` from the schema `useEffect` that calls `runSql` with `SELECT name FROM sqlite_master WHERE type='table' ORDER BY name`. Bind a second `<select>` to `upsertTable` only (`selectedTable` stays for sidebar column browsing). ⚠️ **Decision:** single SQL fetch — no duplicate state for names.
3. Placeholder row "— select table —" with `value=""`.
4. **Update:** opens modal; button `disabled` when `!upsertTable.trim() || upsertPosting`.
5. `import Modal` from `../components/Modal`. Pass `title={`Upsert rows — ${upsertTable}`}`, `size="wide"`, `dirty={upsertJson.trim().length > 0}`, `open={upsertModalOpen}`. `onClose` must reset modal state without leaving `upsertPosting` stuck `true`.
6. `onSave`: `if (!upsertJson.trim())` → Toast error "Paste JSON rows first." → return. `if (upsertPosting) return`. `setUpsertPosting(true)`; `try`/`finally`: `window.confirm`; `POST` body `JSON.stringify({ table: upsertTable.trim(), json_payload: upsertJson })` via `api(...)`; `const data = await r.json()`; if `!r.ok || data.ok === false` throw `new Error(data.error)`; otherwise Toast success `Upsert completed: inserted …, updated …, skipped …`; `finally` `setUpsertPosting(false)`.

⚠️ **Decision:** `Modal` does not `await` async handlers — `onSave` must `void`-invoke an `async` IIFE or named `handleApply` that performs the awaits.

7. Errors: same `catch` Toast pattern as `handleRun` (`Toast variant="error"`, message `(e as Error).message`). `App.css` only if QA finds modal overflow clipping.

#### Self-Assessment

**Scope:** `Single-Component` — one Flask route + one-page React refactor (admin Data Management shell only); `core`/`data` authored under AST-464.
**Conf:** `Medium` — written contract (`apply_copy_output_table_upsert` return shape + kwargs) ships on AST-464; preflight on `dev` blocks surprises; `Modal` / `Toast` / `runSql` patterns match other admin screens.
**Risk:** `HIGH` — wrong HTTP/body shaping or swallowed errors could confuse Susan during cross-environment merges; transactional safety stays in AST-464 — this ticket must faithfully surface `ok` and `error` and HTTP status.

#### Self-review vs ASTRAL_CODE_RULES

| Section | Alignment |
|---------|-----------|
| §1.3 DRY | Reuses `runSql`/schema table list; no second table-discovery SQL path unless `tables` state proves insufficient. |
| §2.1 Config | No new config keys — endpoints under existing admin auth. |
| §3.3 Imports | Flask imports `src.core.table_copy_upsert` only — never `src.data` from `api_admin`. |
| §3.5 Naming | `AdminDataManagement.tsx` under flat `pages/`; `snake_case` path `/api/admin/data/table_copy_upsert`; reuse shared `Modal`. |

#### Build record

**Built by Katherine.** Publish ref `sub/AST-373/AST-465-…`. Product commits: `b6c69025` (Flask route), `f4ced60e` (Data Management UI). Preflight: sibling `origin/sub/AST-373/AST-464-…` merged onto `dev-kath` before implementation.

#### Review (Radia, tip `724310b9`)

**What's solid:**
- Flask `POST /api/admin/data/table_copy_upsert` matches the staged plan (body validation for `table` / `json_payload` type string, `apply_copy_output_table_upsert` delegate, 400 when `ok` false, 500 on unexpected raises). Imports stay ui → core only (§3.3 — no `src.data` in `api_admin`).
- `AdminDataManagement`: Backfill Culture Links UI and polling removed; table list reuses `tables` from `sqlite_master` discovery; `Modal` + dirty guard + async `Save` (`void` IIFE) + `window.confirm` + success/error `Toast` align with Stage 3 and HIGH operational risk mitigation.
- Tests: `test_api_admin` covers HTTP validation, mocked core `ok` branches, exception → 500; frontend `AdminDataManagement` covers upsert UX, `ok:false`, SQL error regression without backfill mocks.

**Issues:** none fix-now.

**Recommended actions:** _Advisory_ — optionally distinguish invalid JSON in the Flask body (`silent=True` today becomes empty dict → generic 400) with an explicit parse error — admin-only ergonomics; not required for sign-off.

Linear summary: fix-now 0 · discuss 0 · advisory 1 (optional JSON-parse clarity). Boundary check: no AST-381 export scope; upsert engine stays in sibling AST-464 (import-only).

#### Resolution

**2026-05-24 — Katherine (resolve-astral, parent AST-373):**
1. **Advisory — HTTP envelope JSON malformed:** `admin_table_copy_upsert` no longer folds `request.get_json(silent=True)` parse failures into `{}` when the client sends a non-empty `application/json` body (Flask `request.is_json`). Parse failure → 400, `{"ok": false, "error": "Request body must be valid JSON."}`, instead of a misleading `table is required`. Copy-output row JSON parsing remains only in `src.core.table_copy_upsert` (plan Stage 1).
2. **Defense in depth:** top-level decoded value must be a JSON object; a bare array or scalar → 400 with `Request body must be a JSON object with table and json_payload fields.` so `.get(...)` paths stay safe without touching `tests/` this pass (happy-path resolve → User Testing).
