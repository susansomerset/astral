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

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1377
**Publish ref:** `origin/sub/AST-1376/AST-1377-ensure-adds-missing-ref-agent-data-id-on-agent-data` @ `fc347a37a9c4eaa5579e7be16e6fec4081d9ac74`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | diff layers miss `core` |
| `astral.agent.do-task-delegation` | scoped | not-applicable | diff layers miss `core` |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | diff layers miss `core` |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch/dispatcher path changes |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch path changes |
| `astral.batch.claim-process-release` | scoped | not-applicable | no batch path changes |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no batch/entity-response write-path edits |
| `astral.config.config-source-of-truth` | scoped | not-applicable | no `config.py` / config path changes in diff |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | diff layers miss `utils`/`core` |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss `artifacts/**` |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | paths miss `debug/**` |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | layers miss `dispatcher`/`config` |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | layers miss `dispatcher`/`core` |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single `docs/features/foundation/ast-1377-…md` for this ticket |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty bible/tests; engineer `code(AST-1377)` touches `src/` only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | engineer commit `d4522b16` is `src/data/database.py` only; tests via Betty `merge-tests` |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | diff layers miss `core`/`external` product paths |
| `astral.layers.import-direction` | scoped | conforms | data-layer DDL only; no new cross-layer imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers miss `scripts` |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | layers miss `ui` product paths |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check write-path edits |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | layers miss `core` |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | layers miss `ui` API paths |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | paths miss bootstrap/repo JSON |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | paths miss dispatcher/admin seed |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | uses existing `_UPSERT_LAZY_SCHEMA_HANDLERS` / startup loop |
| `astral.seed.define-approved` | scoped | not-applicable | no seed catalog work |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no seed row edits |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage/seed changes |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | no new data-layer logging in `database.py` diff |
| `astral.standards.database-header-inventory` | scoped | conforms | `agent_data` inventory bullet documents `ref_agent_data_id` |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no debug/logging layer touches |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | mirrors `entity_id` ALTER in `_ensure_agent_data_schema`; no parallel migrator |
| `astral.standards.in-scope-only` | scoped | conforms | product commit scoped to planned ensure + inventory |
| `astral.standards.logging-via-utils` | scoped | not-applicable | no logging changes |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | column name is domain term |
| `astral.standards.no-cross-contamination` | scoped | needs-discussion | three-dot diff carries AST-1374 bible/tests unrelated to AST-1377 plan |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | nullable `TEXT` DDL; no new enums |
| `astral.standards.public-then-helpers` | scoped | conforms | extends existing private ensure helper |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | layers miss `utils` |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state-transition logic |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job state logic |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | layers miss `core` |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | no `src/ui/frontend` product diff |
| `astral.ui.naming-conventions` | scoped | not-applicable | no UI product diff |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no UI/server worker config diff |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1377)` pins `origin/tests` @ `4e17a64c` |
| `orch.git.commit-vocabulary` | universal | conforms | `code`/`test`/`docs`/`merge-tests` vocabulary on publish ref |
| `orch.git.flow-direction-inviolable` | universal | conforms | tests delivered via `merge-tests` onto `sub`, not `dev` |
| `orch.git.ftr-sub-topology` | universal | conforms | child publishes to `sub/AST-1376/…` |
| `orch.git.merge-on-checkout` | universal | needs-discussion | `sync(dev)` at `0598756e` predates 13 commits now on `origin/dev` tip |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no cherry-pick/rebase in AST-1377 commits |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref is `origin/sub/…` |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | worktree `astral-AST-1376` |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | closed schema gap; no product ambiguity |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 product steps implemented in `d4522b16` |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Foundation child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | reviewed from Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | no canon/statute edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty manifest + `merge-tests`; engineer did not author tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Radia review only |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada assignee through Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | engineer path ban respected on product commit |

(64 rows from active registry table; corpus README cites 65 — no additional active id surfaced in registry beyond this set.)

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | parent/plan: no established pattern cited |

## Plan adherence

- **Stage 1 product (`d4522b16`):** matches plan — inventory bullet updated; existing-table branch ADDs nullable `ref_agent_data_id TEXT` beside `entity_id`; CREATE path unchanged; no bootstrap rewrite; no dedupe/backfill scope.
- **Registry (step 3):** `"agent_data": _ensure_agent_data_schema` still in `_UPSERT_LAZY_SCHEMA_HANDLERS`; `ensure_all_upsert_registry_schemas_at_startup` loops registry — confirmed on publish ref.
- **Betty coverage:** `TestAst1377EnsureRefAgentDataId` exercises idempotent legacy ALTER, post-ensure write/read (`ref_existing`), and startup registry path — aligns with parent AC 1–5 and qa manifest.
- **Estimate 2:** footprint still fits (single-helper DDL + docstring).
- **Joan straggler:** `astral.docs.features-single-file-per-ticket` was excluded at plan time but applies on diff — **conforms** (required issue doc), not a violation.

## Findings

### discuss

1. **Publish ref stale vs `origin/dev`** — `origin/dev` tip (`04f3d5c9`) and `origin/sub/…AST-1377` tip (`fc347a37`) are mutually unreachable. Thirteen commits on `origin/dev` are not on the sub tip, including full **AST-1373/AST-1374** product stack (`api_system.py`, `AuthContext.tsx`, `authSessionPolicy.ts`, `sessionExtend.ts`, config/API wiring). Two-dot `origin/dev` → `origin/sub` shows those product files **removed** on sub relative to dev. `sync(dev)` at `0598756e` merged `62769042`, before AST-1373/1374 landed on dev. **Downstream:** merge `origin/dev` into the epic/sub integration line before `merge-child` / ftr rollup (orientation § Merge integration line + § Merge-clean gate). Not a product-code defect in `d4522b16`, but rollup-unsafe today.

2. **Three-dot diff noise (AST-1374 artifacts on AST-1377 publish ref)** — vs merge base `62769042`, the diff includes `docs/test-bible/frontend/lib.md` AST-1374 section and frontend component tests (`test_authSessionPolicy`, `test_sessionExtend`, revised AuthContext/Authenticate/handoff tests) without AST-1374 **product** code on this sub tip. Cross-ticket bible/test carryover from diverged history; confuses ticket-scoped review and risks green tests against missing product code on sub until dev is merged.

### advisory

1. **Hot-reload edge** — `_ensure_agent_data_schema` returns early when `_agent_data_schema_ensured` is True; a long-lived process that ensured before deploy could skip the new ALTER until restart. Single-worker deploy restart likely bounds this; Betty’s idempotency test resets the flag explicitly.

## Frame diff

| Planned (`Files Changed`) | In three-dot diff vs `origin/dev` | Notes |
|---------------------------|-----------------------------------|-------|
| `src/data/database.py` | yes (`+4` inventory, `+3` ALTER) | matches plan |
| `tests/` / bible | yes — `test_agent_data.py`, `docs/test-bible/data/database/agent_data.md` | Betty-owned; expected at Tests Passed |
| `docs/features/…ast-1377…md` | yes (new) | workflow artifact |
| — | `docs/test-bible/frontend/lib.md` + 6 frontend test files | **AST-1374** scope; not in AST-1377 plan |
| — | no `src/ui/**` product changes | AST-1377 product surface correct |

## What’s solid

- ALTER mirrors shipped `entity_id` idiom: nullable `TEXT`, no DEFAULT/FK, idempotent `cols` check.
- Betty tests cover legacy table without `ref_agent_data_id`, second ensure no-op, write/read `ref_existing`, and startup registry — direct AC coverage.
- No new data-layer logging; header inventory updated per `astral.standards.database-header-inventory`.

## Recommended actions (downstream — not executed here)

1. Chuckles / merge lane: merge latest `origin/dev` into `sub/AST-1376/AST-1377-…` (or ftr integration line per workflow), run merge-clean gate, re-publish if needed.
2. Re-run Betty narrowed manifest after sync to confirm agent_data tests still green against integrated tip.
3. No `resolve-child` product edits required for AST-1377 DDL itself.

context_tokens≈52000

---

[code-rubric] REVIEW (Commit: fc347a37) ALTER clean; sync dev

## Resolution

**Date:** 2026-08-14  
**Against:** Radia `[code-rubric]` @ `fc347a37` (Overall: DISCUSS) — `docs(AST-1377): Radia review — DISCUSS sync-dev` @ `c4bf2db4`

### discuss

1. **Publish ref stale vs `origin/dev`** — Closed. `sync-child.sh` merged `origin/dev` (`04f3d5c9`, includes AST-1373/AST-1374 product stack) onto this sub; `origin/dev` is an ancestor of HEAD. Tip after sync: `e63c246f` (`sync(dev): origin/dev`).
2. **Three-dot AST-1374 bible/test noise** — Closed as a consequence of (1): integrated tip carries matching AST-1374 product + Betty test/bible together; ticket-scoped DDL remains `src/data/database.py` only for AST-1377 product.

### advisory

1. **Hot-reload `_agent_data_schema_ensured` early return** — Accepted as-is (no product change). Deploy/restart clears the flag; Betty’s idempotency test resets it explicitly. Matches Radia “no resolve-child product edits required for DDL.”

### Verification

- Betty narrowed manifest re-run after sync: 4 passed  
  `TestAst977…::test_ensure_schema_adds_ref_column_on_fresh_and_legacy` + `TestAst1377EnsureRefAgentDataId`

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/787b68891f40df41ba596392a77018d1/3ddf123d-f420-4b70-ba76-4b44b900c2fa/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/757e0bae-6a07-41c8-9934-9b9aa18cd1f1/store.db` |
| Radia | review | `/home/susan/.cursor/chats/787b68891f40df41ba596392a77018d1/ff8b578e-65db-40ba-9139-493be1a371ab/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1376 (parent) | ftr/AST-1376-missing-bootstrap-steps-for-ref-agent-data-id |
| AST-1377 | sub/AST-1376/AST-1377-ensure-adds-missing-ref-agent-data-id-on-agent-data |

**Epic worktree:** `astral-AST-1376/` — one active sub checked out at a time.
