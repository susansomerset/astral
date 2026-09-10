# AST-464 — Table Data Upsert from JSON: generic upsert — data layer and core

**Linear:** [AST-464 — Table Data Upsert from JSON: generic upsert — data layer and core](https://linear.app/astralcareermatch/issue/AST-464/table-data-upsert-from-json-generic-upsert-data-layer-and-core)  
**Parent:** [AST-373 — Table Data Upsert from JSON](https://linear.app/astralcareermatch/issue/AST-373/table-data-upsert-from-json)  
**Feature ref:** `sub/AST-373/AST-464-table-data-upsert-from-json-generic-upsert-data-layer-and-core` (origin only)

## Summary

Implements the **backend** for admin table JSON merges: parse Copy Output payloads (arrays of objects keyed by column name), refuse tables without a primary key or malformed payloads **before** any mutation, generic upsert by SQLite primary key (single or composite) with **all-or-nothing** transactional semantics when foreign-key enforcement fires, structured counts (`inserted` / `updated` / `skipped`), and an **`agent_task`-specific branch** that preserves Manage Tasks versioning (via refactored `save_agent_task` logic on a shared connection). **AST-465** wires the Flask route and UI; this ticket delivers **only** `src/data/database.py` and a **new core module** — **no** `api_admin` routes and **no** React.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | PK discovery helper; generic upsert-by-PK on an existing connection; refactor `save_agent_task` internals to accept a caller-owned `sqlite3.Connection` (no commit); `agent_task` import path that runs historical rows + current-row versioning **inside the same transaction** | data |
| `src/core/table_copy_upsert.py` | New module: `json.loads`, structural validation, `PRAGMA foreign_keys=ON`, `BEGIN` / `COMMIT` / `ROLLBACK`, dispatch generic vs `agent_task`, map `sqlite3.IntegrityError` to failed result with zero writes | core |

No changes under `src/ui/`, `tests/`, or `src/utils/config.py` unless a hard blocker appears during build (not anticipated).

---

## Stage 1: Primary key discovery and `save_agent_task` connection refactor

**Done when:** `save_agent_task` behavior is unchanged for all existing callers (Manage Tasks / tests); new internal entry point runs the same SQL as today but on a passed-in `conn` without committing or closing it.

1. In `src/data/database.py`, add **`primary_key_column_names(conn: sqlite3.Connection, table: str) -> list[str]`**:
   - Confirm the table exists with the same existence check pattern as **`table_columns`** (`sqlite_master` lookup); if missing, raise **`ValueError`** with a short message.
   - Read **`PRAGMA table_info(`*table*`)`**; collect rows where **`pk != 0`**, ordered by **`pk`** ascending then **`cid`** ascending so composite keys match SQLite’s column order.
   - If the result is **empty**, raise **`ValueError`** naming the table (tables without a PK are rejected — **AST-373** note on **timesheets** stays out of scope).

2. In **`src/data/database.py`**, refactor **`save_agent_task`**:
   - Move the body currently inside its **`_with_conn`** closure (from after **`_ensure_agent_task_schema(conn)`** through the final state before **`conn.commit()`**) into a new **`_save_agent_task_on_connection(conn: sqlite3.Connection, task_key: str, *, agent_id=None, …) -> None`** that **never** calls **`commit`**, **`close`**, or **`_get_connection`**, and does **not** wrap in **`_run_with_retry`** (the outer **`save_agent_task`** keeps **`_run_with_retry`** exactly once around the connection lifecycle).
   - Implement **`save_agent_task`** as: open connection, **`_ensure_agent_task_schema`**, call **`_save_agent_task_on_connection`**, **`commit`**, **`close`**, preserving **`_run_with_retry`** as today.

3. **`python3 -m py_compile`** on **`database.py`**; run existing tests only if Susan or **test-astral** asks (engineer build stage **does not** add tests per workflow).

⚠️ **Decision:** Retry stays at the **`save_agent_task` outer** boundary only — the batch importer (Stage 3) runs on a single long-lived transaction and uses **`BEGIN`/`ROLLBACK`** in core; nested per-row **`_run_with_retry`** would fight all-or-nothing semantics, so the **`agent_task` batch path** calls **`_save_agent_task_on_connection`** directly, not **`save_agent_task`**.

---

## Stage 2: Generic UPSERT primitive (non–`agent_task`) on caller connection

**Done when:** For any non–`agent_task` user table that has a PK, the data layer can apply a list of row dicts and return accurate **`inserted`**, **`updated`**, **`skipped`** counts **without committing**.

1. Add **`apply_generic_table_copy_upsert(conn: sqlite3.Connection, table: str, rows: list[dict[str, Any]]) -> dict[str, int]`** in **`src/data/database.py`**:
   - Compute **`columns_ordered = table_columns(conn, table)`** (existing helper).
   - Compute **`pk_cols = primary_key_column_names(conn, table)`** — must be non-empty or raise (**caller** should already gate; defense in depth here).
   - **Row shape:** Each **`rows[i]`** must have **exactly** the keys **`set(columns_ordered)`** — if an extra or missing key, raise **`ValueError`** naming the row index (1-based in message for Susan readability).
   - **Values:** Bind using SQLite parameters only — **never** interpolate user strings into SQL identifiers beyond table/columns already validated via **`sqlite_master`** + **`PRAGMA`**. Dynamically build one **`INSERT … ON CONFLICT(`*pk_cols joined*`)` `DO UPDATE SET`** statement that assigns every **non-PK** column **`excluded.`*col*** (PK columns only appear in **`INSERT`** column list).
   - **Counts:** Before executing each row’s statement, **`SELECT 1 FROM … WHERE …`** with PK equality parameterized — if row exists **and** all non-PK columns already equal pasted values (**normalize** **`None`** and JSON **`null`** the same), increment **`skipped`** and **do not** execute **`INSERT`; if exists and differs, execute upsert → **`updated`**; if absent, execute → **`inserted`** (use a single parameterized upsert SQL shape for simplicity; **`changes()`** is allowed if you prove count semantics match **inserted vs updated vs skipped** — preferably explicit pre-read for clarity).
   - **Types:** Payload values arrive as JSON scalars (**`None`**, bool, int, float, str). **Reject** **`dict`** / **`list`** cell values with **`ValueError`** (Copy Output rows are flat).
   - Return **`{"inserted": int, "updated": int, "skipped": int}`** only (**no commit**).

2. **`python3 -m py_compile`** on **`database.py`**.

⚠️ **Decision:** **`JSON`/`BLOB`** affinity columns rarely appear in Copy Output; bind Python **`str`** for text and **`int`**/**`float`** for numbers as SQLite accepts. If a cast fails during execute, bubble **`sqlite3.IntegrityError`** or **`OperationalError`** to core for rollback (treated as failure path).

---

## Stage 3: `agent_task` import path + core orchestrator

**Done when:** A single JSON string plus table name yields a result dict (**success or error**) with FK-safe rollback; **`agent_task`** honors versioning for **`current`** rows and no-op semantics for untouched historical rows.

### 3a — Data layer: `agent_task` rows on existing connection

1. Add **`apply_agent_task_copy_upsert(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> dict[str, int]`** in **`src/data/database.py`**:
   - Require **`table_columns(conn, "agent_task")`**; each input dict’s keys must match that set exactly (same rule as Stage 2).
   - Normalize **`current`** from JSON (**`1`/`0`** or **`True`/`False`**) to integer **`0`** or **`1`** for comparisons; reject other values with **`ValueError`**.
   - **Phase A — historical (`current == 0`) rows**, in stable input order:
     - For each row **`r`**, look up **`task_key_uuid`** in **`agent_task`**.
     - If **no row**: **`INSERT`** a full-row insert with columns in **`columns_ordered`** order (all placeholders) → **`inserted += 1`**.
     - If **row exists** and **every column value matches** pasted value (normalized **`None`/null**), **`skipped += 1`** (**no-op** unchanged historical row).
     - If **row exists** and differs: parameterized **`UPDATE … WHERE task_key_uuid = ?`** setting every non-metadata column equal to pasted values (**full replace** for that UUID) → **`updated += 1`**.
   - **Phase B — `current == 1` rows:**
     - Group pasted **`current`** rows by **`task_key`**. If any **`task_key`** has **more than one** pasted **`current=1`** row, raise **`ValueError`** (**invalid Copy Output composite** — zero writes).
     - For each **`task_key`**, extract the single **`current=1`** row into kwargs compatible with **`_save_agent_task_on_connection`** (map column names **`user_prompt`**, **`cache_prompt`**, **`nocache_prompt`**, **`cache_prompt_*`**, **`system_prompt`**, **`run_next`**, **`agent_id`**: **`None`** in Python means **“leave untouched” only when** implementing import you must pass **`None`** for fields that must **overwrite from paste** vs leave — **implement as:** for import row, coerce missing optional columns from dict as **`None`** only if absent; Copy Output rows **include every column**, so **pass explicit values from dict converted to `Optional`**: strings use **`… if col in row else None`** pattern only if nullable; **`agent_task`** INSERT path in **`_save_agent_task_on_connection`** already distinguishes **`None` = leave**.
     - ⚠️ **Decision:** Treat every column present on the pasted **`current=1`** row as authoritative for **`_save_agent_task_on_connection`** (pass **`user_prompt=r["user_prompt"]`**, **`None`/`""`** per existing **`save_agent_task`** semantics). This keeps behavior aligned with Manage Tasks PATCH semantics Susan already trusts.
     - **`_save_agent_task_on_connection`** already increments versioning when segments differ — map outcomes to **`inserted`/`updated`/`skipped`** as follows (**must match AST-373/9 usability**): if call results in **`INSERT`** new **`current`** version row → count as **`updated`** (or **`inserted`** if **`task_key` was absent** entirely — treat **`inserted`**); if **`INSERT`/`UPDATE`** skipped because **no-op** (**content unchanged**, metadata-only **`UPDATE updated_at`** only) → **`skipped`**. (**Implement:** compare **`SELECT`** before/after or instrument **`_save_agent_task_on_connection`** return enum — ⚠️ **Decision:** minimally extend **`_save_agent_task_on_connection`** return **`"inserted"|"updated"|"skipped"|"versioned"`** **or** use pre/post **`SELECT`** in **`apply_agent_task_copy_upsert`** to classify **without changing external `save_agent_task` signature** — prefer **classification inside **`apply_agent_task_copy_upsert`** with pre-flight **`SELECT`** to avoid widening public API.**

2. **Ordering:** Run **Phase A before Phase B** so historical **`task_key_uuid`** rows exist before versioning retires **`current`** rows (reduces orphaned UUID mismatches).

### 3b — Core orchestrator module

Create **`src/core/table_copy_upsert.py`** with:

**`apply_copy_output_table_upsert(*, table_name: str, json_payload: str) -> dict[str, Any]`**

Return shape **always**:

```python
{"ok": bool, "inserted": int, "updated": int, "skipped": int, "error": Optional[str]}
```

Counts are **zeros** whenever **`ok` is False**.

Procedure (single function, procedural steps):

1. **`database._get_connection()`** pattern is **disallowed** inside this flow for the transactional body — acquire **`conn = database._get_connection()`** once (or use a small **context manager** that **does not** auto-commit on exit if the stock connection context commits — **verify existing `sqlite3.Connection` `__exit__`**; if it auto-commits, use explicit **`try`/`finally conn.close()`** without relying on context manager).  
2. **`conn.execute("PRAGMA foreign_keys=ON")`** then **`SELECT foreign_keys`** read to assert **`1`**; if not enforced, raise **`RuntimeError`** with a short message (**fail closed**).
3. **`json.loads(json_payload)`** — if **`JSONDecodeError`**, return **`ok=False`**, **`error="Malformed JSON"`** (no DB writes).
4. If top-level is **not** a **`list`**, return **`ok=False`**, **`error="Payload must be a JSON array"`**.
5. If any element is **not** a **`dict`**, return **`ok=False`**, **`error="Each row must be an object"`** (include first bad index in message).
6. Validate **`table_name`** exists via **`database.table_columns(conn, table_name)`** (**`ValueError` → ok=False**).
7. **`pk_cols = primary_key_column_names`** — **`ValueError` → ok=False** (**“table has no primary key”).
8. If **`table_name == "agent_task"`**: inside **`BEGIN IMMEDIATE`** (or equivalent): call **`database._ensure_agent_task_schema(conn)`** then **`database.apply_agent_task_copy_upsert(conn, parsed_rows)`**; **`COMMIT` on success.
9. **Else**: **`BEGIN IMMEDIATE`** → **`database.apply_generic_table_copy_upsert`** → **`COMMIT`**.
10. **`except sqlite3.IntegrityError`** (FK or unique): **`ROLLBACK`**, **`ok=False`**, **`error=str(e)`** or a Susan-safe short prefix **plus** **`UNIQUE`/FK context** (**no partial writes)**.
11. **`except ValueError` as **`e`**:** **`ROLLBACK`** if in transaction; **`ok=False`**, **`error=str(e)`**.
12. On success **`ok=True`**, merge count dict keys into response.

⚠️ **Decision:** **`BEGIN IMMEDIATE`** reduces lock races for admin tooling; acceptable for SQLite single-writer semantics.

Imports: **`sqlite3`**, **`json`**, **`typing`**, **`src.data.database`** as **`database`** — **no UI imports**.

**Compile:** **`python3 -m py_compile src/core/table_copy_upsert.py`**.

---

## Execution contract

Per **plan-astral**: follow stages in order; one **build-astral** commit per stage on **`dev-ada`**; cherry-pick to **`origin/sub/AST-373/AST-464-table-data-upsert-from-json-generic-upsert-data-layer-and-core`**. **AST-465** imports **`apply_copy_output_table_upsert`** from **`src.core.table_copy_upsert`**.

Questions during build → **`AST-373`** parent comment with **`🛑` template** (**not AST-465** unless the question belongs to sibling only).

---

## Self-Assessment

**Scope:** `Single-Component` — One new **`core`** orchestrator plus focused **`database.py`** primitives and a refactor of **`save_agent_task`** for transaction sharing; **`UI` / API** untouched here.

**Conf:** `Medium` — Clear patterns (**`PRAGMA`**, **`ON CONFLICT`**, existing **`save_agent_task`** versioning); **`agent_task`** import classification needs careful counting but stays within documented semantics.

**Risk:** `HIGH` — Wrong upsert or broken FK rollback could corrupt admin data across tables; transactional discipline and FK pragma are load-bearing.

---

## Plan vs ASTRAL_CODE_RULES

| Section | Alignment |
|---------|-----------|
| §1.3 DRY | Reuse **`table_columns`**; PK helper shared by generic + validation; refactor **`save_agent_task`** rather than duplicate versioning logic. |
| §2.1 Config | No new config block — admin path is explicitly **generic per table**. |
| §2.6 State machine | Dispatch / candidate / company flows untouched. |
| §3.3 Imports | **Core → data** only in new module; **data → utils** unchanged. |
| §3.5 Naming | Python **`snake_case`**; new module name mirrors behavior (`table_copy_upsert`). |

No conflicts requiring **`conf-!!-NONE`**.

---

## Review

**Diff reviewed:** `origin/dev...origin/sub/AST-373/AST-464-table-data-upsert-from-json-generic-upsert-data-layer-and-core` at **`c2672d63e29d42cce7d4ab285253846150cec0e7`** (Radia).

### What’s solid

- **Plan fidelity:** Delivered **`src/core/table_copy_upsert.py`** transactional shell (`PRAGMA foreign_keys`, `BEGIN IMMEDIATE`, rollback on **`IntegrityError` / `OperationalError` / validation), **`primary_key_column_names`**, **`apply_generic_table_copy_upsert`**, **`apply_agent_task_copy_upsert`** (historicals before **`current`**), and **`save_agent_task`** refactor via **`_save_agent_task_on_connection`** with **`import_explicit`** for Copy Output — matches the combined plan and ticket boundaries (no UI / **`api_admin`** here).
- **ASTRAL_CODE_RULES:** New work stays **core → data**; data layer continues to raise / return counts without ad-hoc logging; dynamic SQL uses quoted identifiers for DML; nested JSON cells rejected.
- **Risk controls:** Component tests cover malformed JSON, non-array payload, unknown table, no-PK table, composite PK insert/update/skip, nested cell rejection, FK violation → **zero** net rows, **`agent_task`** duplicate **`current=1`** rejection, idempotent **`agent_task`** reapply skips.

### Issues

None graded **fix-now** from this pass.

### Recommended actions

| Severity | Topic | Recommendation |
| --- | --- | --- |
| discuss | **`ASTRAL_TEST_BIBLE.md` scope vs ticket** | The branch diff inserts bible subsections **`7.13o`–`7.13t`** for other Astral tickets in the same hunks as **`7.13u`** (**AST-464**). Prefer landing bible rows with the owning ticket merges (or splitting commits) so **AST-464** reviews stay narrowly attributable. |
| discuss | Orchestrator vs data-layer row index wording | **`apply_copy_output_table_upsert`** uses **0-based** indices in the “row must be an object” error string; **`apply_*_copy_upsert`** uses **1-based** row numbers for shape errors. Consider aligning (usually 1-based for admin-facing copy/paste). |
| discuss | **`PRAGMA table_info` identifier** | **`primary_key_column_names`** builds `PRAGMA table_info({table})` with an unquoted table token after **`sqlite_master`** validation. Low practical risk for normal names; quoting (e.g. **`"…"`**) would match the care used elsewhere. |
| advisory | Tables whose **non-PK column set is empty** | **`ON CONFLICT … DO UPDATE SET`** with an empty **`non_pk_clause`** would not be valid SQLite if such a table ever appears. No evidence in reviewed tests/products; skip unless admin targets an all-primary-key layout. |

**Linear:** Posted **Review Posted** with summary; assignee unchanged (implementer).

---

## Resolution

**2026-05-23 — Ada (resolve-astral, post-Radia `315abbf3`)**

- **Fix-now:** None required (Radia **0**).
- **Discuss:** No Susan direction to change bible commit attribution (**AST-464** stays product-only on this branch; bible scope is Betty’s lane). **Row index:** orchestrator error for non-object rows now uses **1-based** `row N` wording to match the data layer. **`PRAGMA table_info`** unquoted identifier left as a low-risk tracked note unless we standardize quoting project-wide.
- **Advisory:** Generic upsert now **rejects** tables whose columns are **all primary key** with a clear **`ValueError`** before building SQL.
- **Merge:** **`dev-ada`** rebased onto **`origin/dev`**; publish tip merged with Radia’s review section retained above.
