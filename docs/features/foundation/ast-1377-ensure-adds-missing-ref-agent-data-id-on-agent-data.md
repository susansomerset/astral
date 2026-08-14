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

## Joan validate

[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1377
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1376/AST-1377-ensure-adds-missing-ref-agent-data-id-on-agent-data` @ `1065d54d9115007bb3025071278f25fa6bc577ea`

## Traceability

### Parent AC → plan stage(s)

| AC | Plan stage |
|----|------------|
| 1. Legacy `agent_data` missing `ref_agent_data_id` → one ensure adds nullable column | Stage 1 step 2 |
| 2. Second ensure is no-op | Stage 1 step 2 + Done when (idempotent `cols` check / `_agent_data_schema_ensured`) |
| 3. Fresh CREATE still includes `ref_agent_data_id` | Stage 1 step 2 explicit guard + Done when |
| 4. Write/read using `ref_agent_data_id` no longer raises `OperationalError` | Stage 1 (column presence unblocks existing AST-977 paths; Betty verifies) |
| 5. Bootstrap / upsert-registry startup leaves column present | Stage 1 step 3 registry confirmation + ensure entrypoints named in Done when |

### Plan stage → parent definition

| Stage | Parent Purpose / Functional scope / AC |
|-------|----------------------------------------|
| Stage 1 | FS-1 existing-table migration; FS-2 fresh-table parity; FS-3 bootstrap reach; AC 1–5 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| `orch.roles.engineer-assignee-through-resolve` | conforms | Single data-layer stage; engineer-owned build |
| `orch.roles.pre-commit-path-bans` | conforms | Plan excludes `tests/` / bible |
| `orch.roles.chuckles-never-ticket-assignee` | conforms | Joan validation only |
| `orch.roles.betty-owns-test-tree` | conforms | Explicit Betty boundary in Files Changed / Execution contract |
| `orch.pipeline.plan-is-bible` | conforms | Ordered Stage 1 steps; 🛑 escalation on drift |
| `orch.pipeline.project-scoped-queues` | conforms | Astral Foundation child only |
| `orch.pipeline.status-gates-skill-entry` | conforms | Plan Ready gate satisfied |
| `orch.roles.archie-approves-statutes` | conforms | No canon/statute edits |
| `orch.pipeline.call-susan-for-product-decisions` | conforms | Closed gap; no product ambiguity |
| `orch.git.no-dev-agent-branches` | conforms | `sub/AST-1376/...` publish ref |
| `orch.git.commit-vocabulary` | conforms | Standard child publish |
| `orch.git.ftr-sub-topology` | conforms | Parent ftr / child sub topology |
| `orch.git.one-epic-worktree-per-parent` | conforms | `astral-AST-1376` worktree |
| `orch.git.merge-on-checkout` | conforms | No rebase/cherry-pick in plan |
| `orch.git.no-cherry-pick-rebase-force` | conforms | Idempotent ALTER only |
| `orch.git.flow-direction-inviolable` | conforms | Child publishes to `origin/sub/...` |
| `orch.git.three-permanent-branches` | conforms | No new permanent branches |
| `orch.git.betty-merge-tests-one-sha` | conforms | Betty manifest path unchanged |
| `astral.standards.database-header-inventory` | conforms | Stage 1 step 1 updates `agent_data` header bullet |
| `astral.standards.in-scope-only` | conforms | One helper extension; explicit out-of-scope table |
| `astral.standards.dry-and-focused-functions` | conforms | Mirrors `entity_id` ALTER in `_ensure_agent_data_schema`; no parallel migrator |
| `astral.standards.data-raises-caller-logs` | conforms | Execution contract forbids new data-layer logging |
| `astral.layers.import-direction` | conforms | `data` layer only; no new cross-layer imports |
| `astral.standards.no-cross-contamination` | conforms | Touches only `database.py` ensure + inventory |
| `astral.standards.no-hardcoded-sets` | conforms | Nullable `TEXT` DDL; no new config enums |
| `astral.standards.public-then-helpers` | conforms | Extends existing private ensure helper |
| `astral.standards.names-not-ticket-ids` | conforms | Column name is domain term, not ticket id |
| `astral.batch.batch-id-first` | conforms | No batch API signature changes |
| `astral.batch.batch-id-format` | conforms | Untouched |
| `astral.batch.claim-process-release` | conforms | Untouched |
| `astral.batch.entity-agent-responses-latest-only` | conforms | Preserves `entity_id` / latest-ref contract |
| `astral.config.config-source-of-truth` | conforms | No new config keys |
| `astral.git.betty-no-src-or-features` | conforms | Engineer owns `src/`; Betty excluded |
| `astral.seed.boot-only-not-hot-path` | conforms | Schema ensure via existing lazy/startup registry |
| `astral.seed.define-approved` | conforms | No seed catalog work |
| `astral.seed.operator-rows-stay-deleted` | conforms | No seed rows touched |
| `astral.seed.other-via-coverage-join` | conforms | No coverage/seed changes |
| `astral.state.core-decides-transitions` | conforms | No state-transition logic |
| `astral.state.job-prior-states-enforced` | conforms | Untouched |

## Considered and excluded

**Considered:** 36 statutes listed above (18 universal + 18 scoped).

**Excluded (sample — full predicate failures):**

| id | reason |
|----|--------|
| `astral.agent.*` | layers/paths miss (`core` / `src/core/**`) |
| `astral.config.secrets-and-env-specific-from-environ` | layers miss (`utils`, `core`, …) |
| `astral.debug.*` | paths miss (`debug/**`, `artifacts/**`, …) |
| `astral.dispatch.*` | layers/paths miss (`dispatcher`, `config`) |
| `astral.docs.features-single-file-per-ticket` | layers miss (`docs`); plan Files Changed is `src/` only |
| `astral.git.engineer-test-tree-ban` | paths miss (`tests/**`, bible paths) |
| `astral.idioms.*` / `astral.patterns.*` | layers/paths miss (`core`, `ui`) |
| `astral.layers.core-vs-external-bright-line` | layers miss (`core`, `external`) |
| `astral.layers.scripts-exempt-from-layer-rules` | layers miss (`scripts`) |
| `astral.layers.ui-config-driven-business-logic` | layers miss (`ui`, `utils`) |
| `astral.seed.agent-tables-in-repo-json` | paths miss (`bootstrap`, `repo_admin_json`, …) |
| `astral.seed.archie-catalog-wins` | paths miss (`dispatcher`, `data/admin/**`) |
| `astral.standards.debug-contract-gated` | layers miss (no debug-touching layers) |
| `astral.standards.logging-via-utils` | layers miss (no logging changes) |
| `astral.standards.utils-data-late-import-only` | layers miss (`utils`) |
| `astral.state.no-daisy-chain-in-run` | layers miss (`core`) |
| `astral.ui.*` | layers/paths miss (`ui`) |

## Findings

- **acceptable** — No Self-assessment (Scope/Conf/Risk) block; trivial single-file ALTER mirror of shipped `entity_id` idiom; Estimate confirm present.
- **acceptable** — AC4 has no explicit write/read smoke step in Stage 1; column ADD is the product fix and Betty owns verification per boundaries.

## R6 checklist (summary)

Definition fidelity: implements parent FS 1–3 and AC 1–5; respects boundaries (no backfill, no dedupe, no bootstrap rewrite). Layers/config/placement/patterns: data-only; no config; no new files; no catalog pattern cited (parent: none). DRY/scope: extends `_ensure_agent_data_schema` only; siblings AST-978 named out of scope. Publish-tip tree confirms gap: CREATE already has `ref_agent_data_id`; existing-table branch ALTERs `entity_id` only (~5814–5816); `_UPSERT_LAZY_SCHEMA_HANDLERS["agent_data"]` registered.

context_tokens≈52000

[plan-rubric] PROCEED (Commit: 1065d54d) legacy ALTER idempotent

## Review

- **Build:** Stage 1 complete — `_ensure_agent_data_schema` existing-table path ADDs nullable `ref_agent_data_id` when absent; inventory notes the column; registry/bootstrap unchanged.
- **Publish ref:** `origin/sub/AST-1376/AST-1377-ensure-adds-missing-ref-agent-data-id-on-agent-data` @ `d4522b16aee95d4a5c6115a70b2a5906673ea190`
- **PR:** none yet
