# AST-982 — Drop agent_responses table from schema and existing DBs

**Linear:** [AST-982 — Drop agent_responses table from schema and existing DBs (Decommission table AGENT_RESPONSES)](https://linear.app/astralcareermatch/issue/AST-982/drop-agent-responses-table-from-schema-and-existing-dbs-decommission)

**Parent:** [AST-975 — Decommission table AGENT_RESPONSES](https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses) (AC reference only)

**Publish ref:** `origin/sub/AST-975/AST-982-drop-agent-responses-table-schema`

Removes the standalone `agent_responses` **table** from the data-layer header inventory, upsert-registry ensure path, and bootstrap so local and Railway DBs drop it on upgrade and never recreate it. Hard-drop of historical standalone-table rows is approved (parent Open question 2). Runtime table I/O stop is sibling AST-981; docs/bible/test prose is sibling AST-983; entity JSON column retirement is sibling AST-984.

## UAT fitness

- **AC restored:** Parent AST-975 AC 1 — “After deploy/bootstrap on a legacy DB that still had the standalone `agent_responses` table, that table is gone and is not recreated on subsequent starts.” Parent AST-975 AC 2 (schema/create half, coordinated with AST-981) — “A repo-wide search of product code under `src/`, `scripts/`, and `tests/` finds no remaining create/read/write of the standalone `agent_responses` **table** (entity-column name collisions are allowed only if Open question 1 keeps the columns).” Child AST-982 AC 1–2 match those sentences for the schema/bootstrap lane.
- **Correct outcome:** After server bootstrap (`ensure_all_upsert_registry_schemas_at_startup`), a legacy DB that still had the standalone table no longer has `agent_responses` in `sqlite_master`, and a second bootstrap does not recreate it. Entity-row `agent_responses` JSON columns on company/job/candidate remain. Durable history stays in `agent_data`.
- **Sibling check:** AST-981 removes `add_agent_response_entry` / `list_agent_responses` / `_store_agent_response` and all executable `INSERT`/`SELECT`/`DELETE` against the table, and **leaves** `_ensure_agent_responses_schema` + upsert-registry `"agent_responses"` keys for this ticket. AST-983 owns mandate/bible/test prose. AST-984 owns entity-column drop. Before Stage 1, merge `origin/ftr/AST-975-decommission-table-agent-responses` and confirm AST-981’s stop-writes commits are ancestors (Linear `blockedBy` AST-981). If ftr still has live table I/O call sites, **stop** and comment on AST-982 — do not drop the table while writers remain.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Deleting entity-column `append_agent_response` / JSON columns, or rewriting §2.4.1 / `astral.batch.entity-agent-responses-latest-only` — that is AST-984. Soft-deleting rows while leaving CREATE/`_ensure_*` live would fail AC 1 (table recreated on next start). Inventing an archive/export before DROP contradicts parent Open question 2 (hard drop approved). Stealing AST-981’s call-site removals into this plan is out of scope.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Remove standalone-table inventory + CREATE/ensure/upsert-registry; add idempotent DROP sunset hooked from bootstrap | data |

**Out of scope (do not touch in this ticket):**

| Item | Owner |
|------|--------|
| `src/core/agent.py` audit call sites; `add_agent_response_entry` / `list_agent_responses` / cascade DELETE I/O; migration script retirement | AST-981 |
| Mandate / Code Rules / Test Bible prose; `tests/**` edits | AST-983 / Betty |
| Entity JSON column DDL, `append_agent_response`, roster expand/dedupe | AST-984 (keep live here) |
| `agent_data` block storage; `_compress_payload` / `_decompress_payload` | unchanged (shared) |
| `docs/ASTRAL_CODE_RULES.md`, `src/utils/config.py` inventory comments | AST-983 |

**Betty note (not engineer commits):** Expect `tests/component/data/database/test_agent_responses.py` cases that call `_ensure_agent_responses_schema` or assert the standalone table exists to be retired or rewritten at qa-child; engineer does not edit `tests/`.

**Build gate:** Linear `blockedBy` AST-981. Before Stage 1 product edits, merge `origin/ftr/AST-975-decommission-table-agent-responses` (and `origin/dev` per merge-clean). Confirm AST-981 commits that remove table I/O are ancestors of `HEAD`. If not, **stop** and comment — do not implement the DROP while writers remain on ftr.

## Stage 1: Idempotent sunset — drop standalone table; never recreate

**Done when:** On a DB that previously had the standalone `agent_responses` table, `_apply_agent_responses_table_sunset(conn)` runs `DROP TABLE IF EXISTS agent_responses` and sets a process flag so the helper is a no-op on later calls in the same process; after `ensure_all_upsert_registry_schemas_at_startup()`, `sqlite_master` has no `agent_responses` table; a second bootstrap does not recreate it. Entity tables still have their `agent_responses` JSON columns.

1. Near the module globals (with the other `_*_schema_ensured` flags), **delete** `_agent_responses_schema_ensured`. Add `_agent_responses_table_sunset_applied = False`.

2. **Delete** the entire `_ensure_agent_responses_schema` function (CREATE TABLE + ALTER COLUMN migration block currently ~lines 2325–2363). Do **not** leave a CREATE path under any name.

3. Immediately after the compress/decompress helpers (or where `_ensure_agent_responses_schema` was), implement **`_apply_agent_responses_table_sunset(conn: sqlite3.Connection) -> None`**:
   - If `_agent_responses_table_sunset_applied` is True, return.
   - `conn.execute("DROP TABLE IF EXISTS agent_responses")`.
   - `conn.commit()`.
   - Set `_agent_responses_table_sunset_applied = True`.
   - Docstring: one-time AST-982 sunset — hard-drop standalone audit table; entity JSON columns unchanged.

   ⚠️ **Decision:** Follow the AST-766 board sunset pattern (DROP inside ensure/bootstrap, not a separate operator CLI). Parent Open question 2 already approved hard drop with no archive/export. SQLite drops indexes with the table — no separate `DROP INDEX` needed.

4. In **`ensure_all_upsert_registry_schemas_at_startup`**, after `_get_connection()` and **before** the `for table in sorted(_UPSERT_LAZY_SCHEMA_HANDLERS)` loop, call `_apply_agent_responses_table_sunset(conn)`. This is the deploy/bootstrap path that satisfies AC 1.

5. In **`_UPSERT_SCHEMA_ENSURE_FLAGS`**, delete the `"agent_responses": ("_agent_responses_schema_ensured",)` entry.

6. In **`_UPSERT_LAZY_SCHEMA_HANDLERS`**, delete the `"agent_responses": _ensure_agent_responses_schema` entry. Do not register the sunset helper as an upsert handler — upsert must not treat `agent_responses` as a live table name.

7. In the module header **Tables used (inventory)**, delete the bullet:
   `- agent_responses — Agent response audit (insert-only from add_agent_response_entry).`
   Leave entity-column mentions on `company` / `job` / `candidate` inventory lines unchanged (those are JSON columns, not this table).

8. Keep `_compress_payload` / `_decompress_payload` (used by `agent_data`). Keep `append_agent_response` and all entity-column parse/update helpers.

9. Confirm by search in `src/data/database.py`:
   - Zero matches for `_ensure_agent_responses_schema`, `_agent_responses_schema_ensured`, `CREATE TABLE agent_responses`.
   - Exactly one `DROP TABLE IF EXISTS agent_responses` (inside the sunset helper).
   - Zero upsert-registry keys named `"agent_responses"` (entity-column SQL strings that mention the column name remain allowed).

⚠️ **Decision:** Do not call sunset from `_ensure_job_schema` / `_ensure_company_schema` / `_ensure_candidate_schema`. Those ensures own entity tables; wiring DROP there would couple unrelated schema paths. Bootstrap (`ensure_all_upsert_registry_schemas_at_startup` via `src/core/bootstrap.py`) is the AC 1 contract path (same family as AST-843).

## Stage 2: Acceptance search (schema lane)

**Done when:** The searches below show no remaining standalone-table CREATE/ensure/registry in `src/` or `scripts/`; DROP exists only in the sunset helper; entity-column identifiers may still appear.

1. From repo root, run:

```bash
rg -n "CREATE TABLE agent_responses|_ensure_agent_responses_schema|_agent_responses_schema_ensured" src scripts --glob '*.py'
rg -n "DROP TABLE IF EXISTS agent_responses" src --glob '*.py'
rg -n '"agent_responses":\s*\(_agent_responses|"agent_responses":\s*_ensure_agent' src/data/database.py
```

2. Expected:
   - Zero matches for CREATE / `_ensure_agent_responses_schema` / `_agent_responses_schema_ensured`.
   - Exactly one `DROP TABLE IF EXISTS agent_responses` in `src/data/database.py`.
   - Zero upsert-registry registrations for the standalone table key.
3. Manually sanity-check that `append_agent_response` and entity-column `agent_responses` handling on company/job/candidate still exist unchanged.
4. `python3 -m py_compile src/data/database.py` passes.

## Self-Assessment

**Scope:** Single-Component — `src/data/database.py` only: inventory, CREATE/ensure removal, upsert-registry deregistration, bootstrap-hooked DROP sunset.

**Conf:** high — AST-981 plan already reserved this exact surface (`_ensure_agent_responses_schema`, registry keys, header inventory); AST-766 establishes the DROP-on-ensure pattern; AC and sibling boundaries are explicit.

**Risk:** Medium — dropping while AST-981 writers still exist would break inserts at runtime; mitigated by Linear `blockedBy` + ftr ancestor gate before Stage 1. Wrongly removing entity-column helpers would break latest-only refs (AST-984 lane) — keep-list and Stage 2 grep mitigate.

## Code Rules check

- §1.1 / `astral.standards.database-header-inventory`: header inventory must drop the retired table (Stage 1 step 7).
- §2.4.1 / `astral.batch.entity-agent-responses-latest-only`: preserved — entity JSON columns and `append_agent_response` stay.
- §2.4 batch / `agent_data`: unchanged — RESPONSE blocks remain the durable store; compress helpers kept.
- §1.3 DRY: one sunset helper + one bootstrap call; no parallel migration script.
- §2.1 config: no new config keys.
- §3.3 imports: no new cross-layer imports; data-layer only.
- Layers: data only; no UI/core edits in this ticket.
- Engineer test-tree ban: Stages forbid engineer commits to `tests/` / bible.
