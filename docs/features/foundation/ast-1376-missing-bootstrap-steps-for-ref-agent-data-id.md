# AST-1376 — Missing bootstrap steps for ref_agent_data_id

<!-- linear-archive: AST-1376 archived 2026-08-31 -->

## Linear archive (AST-1376)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1376/missing-bootstrap-steps-for-ref-agent-data-id  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Live databases that already had an `agent_data` table before the self-ref work still lack the `ref_agent_data_id` column. Runtime write/read paths already expect that column, so agent storage fails with `OperationalError('no such column: ref_agent_data_id')` (seen while `craft_do_rubric` ran). This epic closes the bootstrap gap so every environment gains the column on normal schema ensure / process start — the same contract AST-974/AST-977 already claimed for new and existing databases.

## Functional scope

1. **Existing-table migration.** When `agent_data` already exists and `ref_agent_data_id` is missing, the idempotent `agent_data` schema-ensure path adds that nullable column (same style as the existing `entity_id` ALTER). Databases that already have the column are unchanged.
2. **Fresh-table parity.** New `agent_data` tables continue to be created with `ref_agent_data_id` present; no change to the create shape beyond keeping that column as the canonical schema.
3. **Bootstrap reach.** After deploy/restart (or any path that already runs the upsert-registry schema ensure, including `agent_data`), the column is present before agent content writes that reference it. No separate one-shot production SQL script is required for the column itself.

## Architectural definition

* **Patterns to reuse** — no established pattern applies (catalog). Follow the existing in-module `_ensure_*_schema` ADD COLUMN idiom and the AST-843 startup ensure via `_UPSERT_LAZY_SCHEMA_HANDLERS` / `ensure_all_upsert_registry_schemas_at_startup` ( `agent_data` is already registered ).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.standards.database-header-inventory` (header stays honest about `agent_data` / `ref_agent_data_id`); `astral.standards.in-scope-only` (only the missing ensure step); `astral.standards.dry-and-focused-functions` (extend the existing ensure helper, do not fork a parallel migrator); `astral.standards.data-raises-caller-logs` (data layer still raises; no new data-layer logging); `astral.layers.import-direction` (data-only change).

## Boundaries

* Does **not** change dedupe write/read semantics, match keys, or ref resolution (already shipped under AST-974 / AST-977 / related follow-ons).
* Does **not** re-run historical duplicate backfill (AST-978); after the column exists, operators may use existing backfill tooling if that environment never had the column when backfill ran.
* Does **not** fix LLM `max_tokens` / truncated JSON failures for `craft_do_rubric` (adjacent noise in the same log snippet).
* Does **not** alter UI, dispatch task config, or BLOCK_TYPES.
* Must not break databases that already have `ref_agent_data_id` (ensure stays idempotent).

## Acceptance criteria

1. On a database whose `agent_data` table exists but has no `ref_agent_data_id` column, running the normal `agent_data` schema-ensure once makes `PRAGMA table_info(agent_data)` include nullable `ref_agent_data_id`.
2. Running that ensure a second time is a no-op (no error, column still present once).
3. On a fresh database, create-path `agent_data` still includes `ref_agent_data_id` as today.
4. After ensure has run, an agent_data write/read path that uses `ref_agent_data_id` no longer fails with `OperationalError('no such column: ref_agent_data_id')`.
5. Process bootstrap that already ensures upsert-registry tables (including `agent_data`) leaves the column present without a manual ALTER.

## Dependencies and blockers

none. Prior art: AST-974 / AST-977 (column + runtime), AST-843 (startup ensure registry), AST-978 (optional operator backfill after column exists).

## Open questions

none.

## Proposed child tickets

#### 1: **Ensure adds missing ref_agent_data_id on agent_data - Ada**

Extend the existing `agent_data` schema-ensure so legacy tables gain nullable `ref_agent_data_id` when absent; keep create-path and already-migrated DBs idempotent; rely on the existing upsert-registry / startup ensure registration for `agent_data`. Does **not** own historical backfill or craft_do_rubric token limits.
**Citations:** `astral.standards.database-header-inventory`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.data-raises-caller-logs`, `astral.layers.import-direction`
**Estimate: 2**

**Monolith check:** Functional scope has 3 capabilities; 1 child — intentional single vertical slice (ALTER + ensure/bootstrap reach must ship together for UAT; no separate UI or backfill child).

**New patterns:** none.

---

## Original brief

```
[2026-08-14 20:53:40] INFO src.external.deepseek: LLM deepseek task=craft_do_rubric 460.6s stop=max_tokens tokens in=15592 out=32000
[2026-08-14 20:53:40] ERROR src.external.deepseek: LLM deepseek task=craft_do_rubric 460.6s error=Generation truncated (max_tokens) before complete JSON
[2026-08-14 20:53:40] ERROR src.core.agent: do_task(craft_do_rubric) provider call failed batch_id=craft_do_rubric-bdf40252-c417-494a-8eb1-d50613e6a0f8 error=Generation truncated (max_tokens) before complete JSON
[2026-08-14 20:53:40] ERROR src.data.database: database._with_conn failed: OperationalError('no such column: ref_agent_data_id') | args=() kwargs={}
[2026-08-14 20:53:40] ERROR src.data.database: database._with_conn failed: OperationalError('no such column: ref_agent_data_id') | args=() kwargs={}
```

### Comments

#### chuckles — 2026-08-14T21:41:19.310Z
AST-1377 REVIEW — Radia: sub tip needs merge origin/dev before merge-child (stale vs AST-1373/1374).

---

_Implementation detail may live in git history on `origin/dev`._
