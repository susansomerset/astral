# AST-1377 — Ensure adds missing ref_agent_data_id on agent_data

- **Linear:** [AST-1377](https://linear.app/astralcareermatch/issue/AST-1377/ensure-adds-missing-ref-agent-data-id-on-agent-data-missing-bootstrap)
- **Parent:** [AST-1376 — Missing bootstrap steps for ref_agent_data_id](https://linear.app/astralcareermatch/issue/AST-1376/missing-bootstrap-steps-for-ref-agent-data-id)
- **Publish ref:** `origin/sub/AST-1376/AST-1377-ensure-adds-missing-ref-agent-data-id-on-agent-data`
- **Summary:** Legacy `agent_data` tables created before the self-ref work never gained `ref_agent_data_id` because `_ensure_agent_data_schema` only ALTERs missing `entity_id` on the existing-table path (CREATE already includes `ref_agent_data_id`). Extend that ensure so a missing nullable `ref_agent_data_id` is added idempotently; keep create-path and already-migrated DBs unchanged; rely on the existing `_UPSERT_LAZY_SCHEMA_HANDLERS` / `ensure_all_upsert_registry_schemas_at_startup` registration (no bootstrap rewrite). Does **not** own historical backfill (AST-978) or craft_do_rubric token limits.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Module inventory note for `ref_agent_data_id`; in `_ensure_agent_data_schema` existing-table branch, ADD COLUMN `ref_agent_data_id TEXT` when absent (mirror `entity_id` idiom) | data |

**Out of scope (explicit):**

| Item | Owner |
|------|--------|
| Historical backfill of refs on duplicate rows | **AST-978** |
| craft_do_rubric `max_tokens` / truncated JSON | out of epic |
| Dedupe write/read semantics, match keys, ref resolution | unchanged (AST-974 / AST-977) |
| `bootstrap.py` / `_UPSERT_LAZY_SCHEMA_HANDLERS` registration | already wires `agent_data` — do not fork |
| `tests/` / bible | Betty |

---

## Stage 1: Ensure ALTER for missing `ref_agent_data_id`

**Done when:** On a DB whose `agent_data` table exists without `ref_agent_data_id`, one call to `_ensure_agent_data_schema` (or `ensure_all_upsert_registry_schemas_at_startup` / `ensure_table_schema_for_upsert("agent_data")`) makes `PRAGMA table_info(agent_data)` list nullable `ref_agent_data_id`; a second ensure is a no-op; fresh CREATE still includes the column; header inventory mentions it; `python3 -m py_compile src/data/database.py` passes. No write/read/dedupe behavior changes.

1. In `src/data/database.py` module docstring inventory, update the `agent_data` bullet so it also notes nullable self-ref `ref_agent_data_id` (points at earliest identical content row when set; AST-974 / AST-977). Keep the existing `entity_id` / latest-per-task note (AST-984). Do **not** invent other inventory changes.

2. In `_ensure_agent_data_schema` (existing-table `else` branch, immediately after the `entity_id` ADD COLUMN block — currently ~5814–5816):
   - After building `cols` from `PRAGMA table_info(agent_data)` (same set used for `entity_id`), if `"ref_agent_data_id" not in cols`, run:
     `conn.execute("ALTER TABLE agent_data ADD COLUMN ref_agent_data_id TEXT")`
     then `conn.commit()`.
   - Column type must be nullable `TEXT` with **no** DEFAULT and **no** FK constraint (matches CREATE path and AST-977 Stage 1 decision).
   - Do **not** clear, null, or rewrite any existing `block_data` or `ref_agent_data_id` values.
   - Do **not** change the fresh-table `CREATE TABLE agent_data` shape (it already lists `ref_agent_data_id TEXT`).
   - Do **not** change index creation, `_backfill_agent_data_entity_id_from_entity_columns`, or the `_agent_data_schema_ensured` flag semantics.
   - Do **not** add a parallel migrator, script, or second ensure helper — extend this function only (`astral.standards.dry-and-focused-functions` / `in-scope-only`).

3. Confirm (read-only verification in this stage — no code change unless missing):
   - `"agent_data": _ensure_agent_data_schema` remains in `_UPSERT_LAZY_SCHEMA_HANDLERS`.
   - `ensure_all_upsert_registry_schemas_at_startup` still loops that registry (called from `src/core/bootstrap.py`).
   - If either registration is missing, **stop** and comment on parent AST-1376 with the 🛑 Stage format — do not invent a new bootstrap path.

⚠️ **Decision:** Place the `ref_agent_data_id` ALTER beside the existing `entity_id` ALTER in the same `else` branch (same `cols` PRAGMA), not a new function or startup-only path — matches the ticket Notes and the `entity_id` idiom already in-module. Idempotency is “column present once”; second ensure hits the early `_agent_data_schema_ensured` return or finds the column already in `cols`.

---

## Execution contract

- Execute Stage 1 steps in order; one commit on the epic worktree for this stage, then publish to `origin/sub/AST-1376/AST-1377-ensure-adds-missing-ref-agent-data-id-on-agent-data`.
- Do not touch `tests/`, bible, UI, dispatcher, BLOCK_TYPES, or dedupe helpers.
- Data layer raises; add **no** new data-layer logging (`astral.standards.data-raises-caller-logs`).
- Ambiguity or drift → stop and comment on **parent** AST-1376 with the 🛑 Stage blocked format; do not improvise.

## Estimate

Confirm Chuckles estimate: 2 — agree
