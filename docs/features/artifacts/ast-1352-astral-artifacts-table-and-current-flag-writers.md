# AST-1352 — astral_artifacts table and current-flag writers

**Linear:** [AST-1352](https://linear.app/astralcareermatch/issue/AST-1352)
**Parent:** [AST-1340](https://linear.app/astralcareermatch/issue/AST-1340) — Create a table called astral_artifacts
**Publish ref:** `sub/AST-1340/AST-1352-astral-artifacts-table-writers`

Data-layer only: create `astral_artifacts` (ensure/migrate + header inventory) and public save/read helpers that retire the prior `current=1` row and insert a new current row for `(entity_type, entity_id, artifact_type)`, matching agent_task / rubric_vector versioning. Does **not** wire Save Base Resume (AST-1353).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Header inventory bullet; `_astral_artifacts_schema_ensured`; `_ensure_astral_artifacts_table`; `save_astral_artifact`; `get_current_astral_artifact`; `list_astral_artifacts` | data |

**Do not touch:** `src/core/**`, `src/ui/**`, `src/utils/config.py`, `src/external/**`, Save Base Resume call sites, `candidate_data.artifacts.base_resume` writers/readers, `tests/**`, `docs/test-bible/**`, canon pattern catalog files (proposed `pattern.data.versioned-current-row` is flagged for Archie on the parent — do not invent a catalog entry here).

## Stage 1: Table ensure + header inventory

**Done when:** A fresh SQLite file and an existing migrated DB both expose `astral_artifacts` with the columns below after any public helper (or a direct `_ensure_astral_artifacts_table` call) runs; the module docstring inventory lists the table; no core/UI callers exist yet.

1. In `src/data/database.py` module docstring **Tables used (inventory)**, add a bullet **immediately after** the `rubric_vector` bullet (before `vector_feedback`):

   ```
   - astral_artifacts — Versioned entity-scoped artifact blobs (astral_artifact_uuid TEXT PK,
     entity_type TEXT, entity_id TEXT, artifact_type TEXT, artifact_data TEXT, current INTEGER 0|1,
     created_at, updated_at). Active row: current=1 for (entity_type, entity_id, artifact_type).
     Versioning follows agent_task / rubric_vector current=1 retire-and-insert (AST-1340 / AST-1352).
   ```

2. Near the other `_…_schema_ensured` flags (with `_rubric_vector_schema_ensured` / `_vector_feedback_schema_ensured`), add:

   ```python
   _astral_artifacts_schema_ensured = False
   ```

3. Immediately after `_ensure_vector_feedback_table` (same ensure-table region as rubric_vector / vector_feedback), add `_ensure_astral_artifacts_table(conn: sqlite3.Connection) -> None` that:

   - Returns early when `_astral_artifacts_schema_ensured` is True.
   - If `sqlite_master` has no table named `astral_artifacts`, `CREATE TABLE astral_artifacts` with exactly these columns:

     | Column | Type / constraint |
     |--------|-------------------|
     | `astral_artifact_uuid` | `TEXT PRIMARY KEY` |
     | `entity_type` | `TEXT NOT NULL` |
     | `entity_id` | `TEXT NOT NULL` |
     | `artifact_type` | `TEXT NOT NULL` |
     | `artifact_data` | `TEXT NOT NULL` |
     | `current` | `INTEGER NOT NULL DEFAULT 1` |
     | `created_at` | `TIMESTAMP NOT NULL` |
     | `updated_at` | `TIMESTAMP NOT NULL` |

   - Creates index `idx_astral_artifacts_entity_type_current` on `(entity_type, entity_id, artifact_type, current)`.
   - `conn.commit()` after create.
   - Sets `_astral_artifacts_schema_ensured = True`.
   - No `ALTER TABLE` backfill path (table is new; no historical rows to migrate — parent boundary: no backfill of prior `artifacts.base_resume`).

   ⚠️ **Decision:** PK name `astral_artifact_uuid` (not bare `id`) — matches `rubric_vector_uuid` / `task_key_uuid` UUID-TEXT PK style in this module.

   ⚠️ **Decision:** Blob column is `artifact_data TEXT NOT NULL` (JSON text). Callers pass the live artifact payload; the writer normalizes to a JSON string (Stage 2). Do not zlib-compress (that pattern is `agent_data.block_data` only per code rules §3.2).

   ⚠️ **Decision:** Do **not** register `astral_artifacts` in `ALLOWED_CONFIG_TABLES` or `ensure_table_schema_for_upsert` maps — this is not a Copy Output / config upsert table; writers call `_ensure_astral_artifacts_table` themselves.

## Stage 2: Current-flag writers and readers

**Done when:** Calling `save_astral_artifact` twice for the same `(entity_type, entity_id, artifact_type)` leaves exactly one `current=1` row whose `artifact_data` matches the latest payload, prior row(s) remain with `current=0` and are returned by `list_astral_artifacts(..., current_only=False)`; `get_current_astral_artifact` returns only the active row. Data layer raises on bad args; no logging inside these functions (`astral.standards.data-raises-caller-logs`).

1. In `src/data/database.py`, in the same region as the ensure helper (public functions grouped with this table’s helpers — follow the rubric_vector public/`_on_connection` adjacency style already in-file), add:

   **`save_astral_artifact(entity_type: str, entity_id: str, artifact_type: str, artifact_data: Any) -> str`**

   - Strip `entity_type`, `entity_id`, `artifact_type`; if any is empty after strip, `raise ValueError` with a message naming the missing field.
   - Validate `entity_type` against `ENTITY_TYPES` from `src.utils.config` (already imported in this module): if not in that list, `raise ValueError` naming the bad type. Do not hardcode a parallel list.
   - Normalize `artifact_data` to a TEXT payload:

     - If `artifact_data` is `None`, `raise ValueError("artifact_data required")`.
     - If `isinstance(artifact_data, str)`, store that string as-is (caller may already have JSON text).
     - Else `json.dumps(artifact_data)` (same pattern as `candidate_data` / `job_data` writers).

   - Open connection via `_get_connection` + `_run_with_retry` (same wrapper style as `list_rubric_vector_uuid_by_code` / `sync_rubric_vectors_from_criteria`).
   - Call `_ensure_astral_artifacts_table(conn)`.
   - `now = _utc_now()`.
   - Retire prior current row(s) for the natural key:

     ```sql
     UPDATE astral_artifacts
        SET current = 0, updated_at = ?
      WHERE entity_type = ? AND entity_id = ? AND artifact_type = ? AND current = 1
     ```

   - Insert new row: `astral_artifact_uuid = str(uuid.uuid4())`, `current = 1`, `created_at = now`, `updated_at = now`, plus the four identity/payload fields.
   - `conn.commit()` before close (match sibling writers that mutate).
   - Return the new `astral_artifact_uuid` string.

   ⚠️ **Decision:** Retire by natural key `(entity_type, entity_id, artifact_type)` with `UPDATE … WHERE … AND current = 1`, not by looking up a single UUID first. Guarantees at most one current row even if a prior bug left duplicates — same discipline as “exactly one current=1 per key” in the parent AC.

   ⚠️ **Decision:** Always insert a new UUID row on save (even when payload is byte-identical to the prior current). Matches agent_task content-change versioning intent for intentional Save snapshots; no fingerprint short-circuit (unlike rubric_vector). Sibling Save Base Resume is an explicit operator save.

2. Add **`get_current_astral_artifact(entity_type: str, entity_id: str, artifact_type: str) -> Optional[Dict[str, Any]]`**

   - Same strip / empty / `ENTITY_TYPES` validation as save (raise on bad identity args).
   - Ensure table; `SELECT` the single row where `entity_type`, `entity_id`, `artifact_type` match and `current = 1` (`LIMIT 1`).
   - If no row: return `None`.
   - If row: return a dict with keys `astral_artifact_uuid`, `entity_type`, `entity_id`, `artifact_type`, `artifact_data`, `current`, `created_at`, `updated_at`.
   - For `artifact_data`: try `json.loads` on the stored TEXT; on `json.JSONDecodeError`, leave the raw string (callers that stored non-JSON text still round-trip).

3. Add **`list_astral_artifacts(entity_type: str, entity_id: str, artifact_type: str, *, current_only: bool = False) -> List[Dict[str, Any]]`**

   - Same identity validation as above.
   - Ensure table; `SELECT` all matching `(entity_type, entity_id, artifact_type)` rows; if `current_only` is True, add `AND current = 1`.
   - Order by `created_at ASC` (oldest first) so retired history is stable and queryable (parent AC 3).
   - Return list of dicts with the same keys / `artifact_data` parse rule as `get_current_astral_artifact`.

4. Do **not** call these helpers from core, UI, or Save Base Resume in this ticket. AST-1353 owns the Save call site: it will pass `entity_type="candidate"`, `entity_id=<candidate_id>`, `artifact_type="base_resume"`, `artifact_data=<saved artifacts.base_resume value>`.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1352
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1340/AST-1352-astral-artifacts-table-writers` @ `d5137e65`

## Traceability
AC1→Stage 1 (ensure/migrate + header inventory); AC2→Stage 2 writers (`save_astral_artifact` / `get_current_astral_artifact`; end-to-end Save proof deferred to AST-1353 per child boundary); AC3→Stage 2 retire-and-insert semantics + `list_astral_artifacts` history query.

## Findings

### acceptable
- **Location:** Plan structure — no Scope/Conf/Risk self-assessment block
- **Finding:** Only `## Estimate` confirm line; no formal self-assessment axes.
- **Recommendation:** Acceptable for this narrow data-layer-only footprint; complexity matches estimate 5.

### discuss
- **Location:** Parent Architectural definition — `pattern.data.versioned-current-row`
- **Finding:** Proposed catalog entry still undrafted (parent already flags Archie); plan correctly refuses to invent the pattern file here.
- **Recommendation:** No plan change required; Archie approval remains a parent/epic catalog task before downstream reuse.

### acceptable
- **Location:** Stage 2 — retire-by-natural-key vs `agent_task` UUID retire
- **Finding:** Plan deliberately uses `UPDATE … WHERE entity_type/entity_id/artifact_type AND current=1` rather than UUID lookup first.
- **Recommendation:** Documented decision is sound (duplicate-current safety); matches parent “exactly one current=1” intent.

**R6 checklist (summary):** Definition fidelity ✓ — data-only scope, explicit do-not-touch list, no Save/UI/candidate_data wiring. Layer/config/placement ✓ — single `data` file, `ENTITY_TYPES` from config, no magic sets, no logging in data helpers. Pattern ✓ — `pattern.layers.import-discipline` honored; versioning shape aligned with `agent_task` / `rubric_vector` precedents in-file. DRY/scope ✓ — reuses `_get_connection`, `_run_with_retry`, `_utc_now`, existing ensure-table idioms; no sibling creep.

**Statute pass (in-session):** All 18 `tier: universal` orch statutes conform (plan touches no git/test-tree/Linear workflow surfaces). Considered scoped statutes on `src/data/database.py` modify — including `astral.standards.database-header-inventory`, `astral.standards.in-scope-only`, `astral.standards.data-raises-caller-logs`, `astral.layers.import-direction`, `astral.standards.no-hardcoded-sets`, batch/state/seed statutes whose path/layer predicates matched — all `conforms`; no `violates`.

context_tokens≈38000
```

## Review (build stub)

**Publish ref:** `origin/sub/AST-1340/AST-1352-astral-artifacts-table-writers`
**Plan path:** `docs/features/artifacts/ast-1352-astral-artifacts-table-and-current-flag-writers.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `294e76fa` | `astral_artifacts` ensure + inventory; `save_astral_artifact` / `get_current_astral_artifact` / `list_astral_artifacts` retire-and-insert |

**Tip:** `294e76fa` on `origin/sub/AST-1340/AST-1352-astral-artifacts-table-writers`

## Radia review

# Radia review — AST-1352

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1352
**Publish ref:** origin/sub/AST-1340/AST-1352-astral-artifacts-table-writers @ 74712e64b4990c68684541c3cf9aebe15be87288
**Overall:** CLEAN
```

**Diff baseline:** `origin/dev...origin/sub/AST-1340/AST-1352-astral-artifacts-table-writers` (524 lines, 8 files)

**Product commit:** `294e76fa` — `src/data/database.py` only (+175 lines)  
**Tests/docs:** Betty `merge-tests` tip `74712e64` (expected per `orch.git.betty-merge-tests-one-sha`)

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no `src/core` agent paths in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no dispatcher/agent-task changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch-id emission |
| astral.batch.batch-id-format | scoped | not-applicable | no batch-id formatting |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/process/release helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no entity_agent_responses changes |
| astral.config.config-source-of-truth | scoped | not-applicable | no config-block edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug/artifacts dir paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single plan doc for AST-1352 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty-owned test-bible/tests merge; engineer product commit is `database.py` only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code()` commit touches only `src/data/database.py` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | data-only; no external I/O |
| astral.layers.import-direction | scoped | conforms | data uses existing `ENTITY_TYPES` from `utils.config`; no forbidden imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no UI paths |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no render/verdict paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API endpoints |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON changes |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog edits |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot seed paths |
| astral.seed.define-approved | scoped | not-applicable | no define/seed flow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator seed rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join seed |
| astral.standards.data-raises-caller-logs | scoped | conforms | helpers raise `ValueError`; no logging in new data paths |
| astral.standards.database-header-inventory | scoped | conforms | `astral_artifacts` bullet added after `rubric_vector` in module inventory |
| astral.standards.debug-contract-gated | scoped | not-applicable | no `debug=` surfaces |
| astral.standards.dry-and-focused-functions | scoped | conforms | shared `_normalize_astral_artifact_identity` / `_astral_artifact_row_dict`; public API thin |
| astral.standards.in-scope-only | scoped | conforms | data writers only; no Save/UI/candidate_data wiring (AST-1353 boundary held) |
| astral.standards.logging-via-utils | scoped | conforms | no new `print` / `getLogger` in touched product code |
| astral.standards.names-not-ticket-ids | scoped | conforms | public symbols are domain-named, not ticket-prefixed |
| astral.standards.no-cross-contamination | scoped | conforms | artifacts table isolated; not registered in config upsert maps per plan |
| astral.standards.no-hardcoded-sets | scoped | conforms | `entity_type` validated via `ENTITY_TYPES`, not a parallel hardcoded list |
| astral.standards.public-then-helpers | scoped | conforms | public save/get/list precede private normalize/row-dict helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no `src/utils/**` changes |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transition paths |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state paths |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run-chain paths |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend files |
| astral.ui.naming-conventions | scoped | not-applicable | no UI files |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip is `merge-tests(AST-1352): origin/tests 7f7444a7` |
| orch.git.commit-vocabulary | universal | conforms | `code` / `docs` / `test` / `merge-tests` vocabulary correct |
| orch.git.flow-direction-inviolable | universal | conforms | sub-branch publish; no dev bypass |
| orch.git.ftr-sub-topology | universal | conforms | child on `sub/AST-1340/AST-1352-…` |
| orch.git.merge-on-checkout | universal | conforms | no rebase/cherry-pick signals in commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | clean linear child history |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1340` worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` only |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no unresolved product forks in diff |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches staged plan |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child; scoped correctly |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child gate satisfied |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/test-bible via Betty merge, not engineer product commit |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code diff |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee; review does not reassign |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits evident |

**Active corpus swept:** 64 statutes on tree (README claims 65; file count is 64).

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.layers.import-discipline | conforms | data→utils only (`ENTITY_TYPES`); no ui/core/external bends (Joan R6 citation honored) |
| pattern.data.versioned-current-row | not cited | parent-proposed catalog entry still undrafted; plan correctly refuses to invent it here |

---

## Plan adherence

Implementation matches both plan stages:

- **Stage 1:** `_astral_artifacts_schema_ensured`, `_ensure_astral_artifacts_table` with exact column set, index `idx_astral_artifacts_entity_type_current`, header inventory bullet placement, no `ALLOWED_CONFIG_TABLES` registration, no ALTER backfill.
- **Stage 2:** `save_astral_artifact` / `get_current_astral_artifact` / `list_astral_artifacts` with strip/empty/`ENTITY_TYPES` validation, natural-key `UPDATE … current=1` retire, always-insert new UUID, `json.dumps` / string-as-is storage, `json.loads` on read with raw fallback, `ORDER BY created_at ASC`, no logging in data helpers.
- **Boundaries:** No core/UI/Save Base Resume / `candidate_data.artifacts.base_resume` wiring — deferred to AST-1353 as planned.
- **Estimate 5:** Footprint fits (single product file + Betty tests/docs).
- **Joan plan-rubric:** APPROVED @ `d5137e65`; no Excluded-statute stragglers on this diff.

**C6 lenses (§5a):** Imports/layers OK; no silent failure (JSON decode fallback is plan-specified, not a swallow); no `or {}` sentinels on required data; no debug/LLM/external/UI surfaces touched; SQL column/`?` counts consistent on INSERT/UPDATE/SELECT.

---

## Findings

### fix-now

*(none)*

### discuss

*(none blocking)*

### advisory

- **Parent catalog — `pattern.data.versioned-current-row`:** Implementation shape matches the intended versioned-current-row idiom (`rubric_vector` / `agent_task` precedents in-file), but the catalog entry remains undrafted on AST-1340. No change required on this child; Archie/parent owns catalog harvest before downstream reuse citations.
- **Duplicate `current=1` rows:** No partial unique index at DB level; retire `UPDATE` heals on save (plan decision). `get_current_astral_artifact` uses `LIMIT 1` if duplicates exist pre-save — acceptable per plan; optional hardening belongs on a future ticket if desired.

---

## What's solid

- Clean engineer footprint: product code is one file, one commit.
- Retire-by-natural-key semantics match plan decision and parent “exactly one current=1” intent.
- Betty coverage maps 1:1 to plan branches (ensure, round-trip, history, identical-payload new UUID, validation, string/JSON-text edge cases).
- Conftest `_astral_artifacts_schema_ensured` resets in data/core/ui — correct isolation hygiene.

---

## Frame diff

(none)

---

## Notes

- Joan plan-rubric verdict attached; no Excluded-statute straggler.
- Tests/test-bible in three-dot diff ride Betty `merge-tests` SHA — not engineer scope creep.
- C7 complete; recommend Chuckles append to issue doc, commit `docs(AST-1352): Radia review — clean`, post slim upshot, advance to **Review Posted** → **User Testing** (PROCEED path).

context_tokens≈22000

---

**Slim Linear upshot (Chuckles posts via `linear_proxy --as radia`):**

```
[code-rubric] PROCEED (Commit: 74712e64) data-layer writers clean
```

## Bug: AST-1364 — Rename astral_artifacts table to artifacts

### As-is
The versioned artifact store table (and its ensure/helpers/public writers) is named `astral_artifacts` / `*_astral_artifact*`, unlike entity tables such as `job` and `company` which have no `astral_` table-name prefix.

### To-be
The SQLite table is named `artifacts`. Ensure helpers, schema flag, index, PK column, and public/data/core call sites use the same unprefixed naming so Save Base Resume still snapshots into this table with identical current-flag semantics.

### Repro
1. Open any DB that has run AST-1352 ensure (or read `src/data/database.py` header inventory + `_ensure_astral_artifacts_table`).
2. Observe table name `astral_artifacts` (and symbols `save_astral_artifact`, `astral_artifact_uuid`, etc.).
3. Compare to inventory peers `job` / `company` — no `astral_` table prefix.

### Root cause
AST-1352 named the new table `astral_artifacts` (and mirrored that prefix into PK / API / core helper names). Product naming intent was the short table name `artifacts`, consistent with other entity tables.

### Proposed change

Scope is **rename only** — same columns (except PK name), same retire-and-insert behavior, same Save wire. Do **not** change `candidate_data.artifacts.base_resume` (JSON path inside candidate_data — unrelated string). Do **not** invent restore/Print UI. Do **not** edit `tests/**` or `docs/test-bible/**` (Betty).

⚠️ **Decision:** Drop the `astral_` prefix from the **table**, **PK column**, **index**, **schema flag**, **ensure/helper names**, and **public writer/reader names**, and update AST-1353 call sites to match. Keeping `save_astral_artifact` while renaming only the SQL table would leave a permanent mismatch and force dual vocabulary in core/UI comments.

1. In `src/data/database.py` module docstring inventory, replace the `astral_artifacts` bullet with:

   ```
   - artifacts — Versioned entity-scoped artifact blobs (artifact_uuid TEXT PK,
     entity_type TEXT, entity_id TEXT, artifact_type TEXT, artifact_data TEXT, current INTEGER 0|1,
     created_at, updated_at). Active row: current=1 for (entity_type, entity_id, artifact_type).
     Versioning follows agent_task / rubric_vector current=1 retire-and-insert (AST-1340 / AST-1352;
     table rename AST-1364).
   ```

2. Rename module flag `_astral_artifacts_schema_ensured` → `_artifacts_schema_ensured`.

3. Replace `_ensure_astral_artifacts_table` with `_ensure_artifacts_table(conn)` that:
   - Returns early when `_artifacts_schema_ensured` is True.
   - If `sqlite_master` has table `artifacts`: ensure index `idx_artifacts_entity_type_current` exists on `(entity_type, entity_id, artifact_type, current)` (create if missing); if column `astral_artifact_uuid` still exists, `ALTER TABLE artifacts RENAME COLUMN astral_artifact_uuid TO artifact_uuid`; then set flag and return.
   - Elif table `astral_artifacts` exists (pre-rename DBs from AST-1352 UAT):
     - `ALTER TABLE astral_artifacts RENAME TO artifacts`.
     - `ALTER TABLE artifacts RENAME COLUMN astral_artifact_uuid TO artifact_uuid`.
     - `DROP INDEX IF EXISTS idx_astral_artifacts_entity_type_current`.
     - `CREATE INDEX IF NOT EXISTS idx_artifacts_entity_type_current ON artifacts (entity_type, entity_id, artifact_type, current)`.
     - `conn.commit()`; set flag; return.
   - Else `CREATE TABLE artifacts` with columns:

     | Column | Type / constraint |
     |--------|-------------------|
     | `artifact_uuid` | `TEXT PRIMARY KEY` |
     | `entity_type` | `TEXT NOT NULL` |
     | `entity_id` | `TEXT NOT NULL` |
     | `artifact_type` | `TEXT NOT NULL` |
     | `artifact_data` | `TEXT NOT NULL` |
     | `current` | `INTEGER NOT NULL DEFAULT 1` |
     | `created_at` | `TIMESTAMP NOT NULL` |
     | `updated_at` | `TIMESTAMP NOT NULL` |

     plus `CREATE INDEX idx_artifacts_entity_type_current ON artifacts (entity_type, entity_id, artifact_type, current)`; commit; set flag.

4. Rename private helpers and SELECT list:
   - `_normalize_astral_artifact_identity` → `_normalize_artifact_identity`
   - `_astral_artifact_row_dict` → `_artifact_row_dict` (dict key `artifact_uuid` instead of `astral_artifact_uuid`)
   - `_ASTRAL_ARTIFACT_SELECT` → `_ARTIFACT_SELECT` listing `artifact_uuid, …`

5. Rename public API (keep signatures/behavior; swap SQL table/column names):
   - `save_astral_artifact` → `save_artifact` (UPDATE/INSERT against `artifacts`; return new `artifact_uuid`)
   - `get_current_astral_artifact` → `get_current_artifact`
   - `list_astral_artifacts` → `list_artifacts`
   - Delete the old `*_astral_artifact*` names (no dual aliases).

6. In `src/core/candidate.py`:
   - Rename `snapshot_saved_base_resume_astral_artifact` → `snapshot_saved_base_resume_artifact`.
   - Call `database.save_artifact(...)` instead of `database.save_astral_artifact(...)`.
   - Update the docstring to say table `artifacts` / returned `artifact_uuid`.

7. In `src/ui/api/api_candidate.py`:
   - Update the import/call of the core helper to `snapshot_saved_base_resume_artifact`.
   - Update the AST-1353 comment to name table `artifacts` (not `astral_artifacts`).

8. Grep the product tree (`src/**`) for remaining `astral_artifacts` / `save_astral_artifact` / `get_current_astral_artifact` / `list_astral_artifacts` / `astral_artifact_uuid` / `_ensure_astral_artifacts` / `_astral_artifacts_schema` / `snapshot_saved_base_resume_astral_artifact` and clear every hit before Code Complete. Do **not** "fix" hits under `tests/` or `docs/test-bible/` in this ticket — leave those for Betty after fix-board.

### Blast radius
- **AST-1352 writers** (`src/data/database.py`) — primary rename surface (this doc).
- **AST-1353 Save wire** (`src/core/candidate.py` `snapshot_saved_base_resume_*`, `src/ui/api/api_candidate.py` PUT path) — must call the renamed public API / helper or Save snapshots break. Sibling plan `docs/features/artifacts/ast-1353-save-base-resume-writes-base-resume-snapshot.md` still documents the old names; product rename is owned here; do not rewrite that sibling plan’s stages in this patch.
- **Component tests / bible** (Betty): `tests/component/data/database/test_astral_artifacts.py`, confest `_astral_artifacts_schema_ensured` resets, `tests/component/core/test_candidate.py` / `tests/component/ui/api/test_api_candidate.py` AST-1353 cases, `docs/test-bible/data/database/astral_artifacts.md` (+ core/candidate bible rows). Expect fix-board **TESTS: REVISE** → Betty updates symbols/table strings; engineer does not patch the test tree.
- **Existing local/staging DBs** that already created `astral_artifacts` — covered by the RENAME path in `_ensure_artifacts_table`; no data loss of prior current/history rows.
- Unrelated: `candidate_data["artifacts"]` JSON key, ArtifactEditor, Print — **out of scope** (different “artifacts” namespace).

### What must still hold
- Parent AST-1340 / AST-1352 AC: exactly one `current=1` row per `(entity_type, entity_id, artifact_type)` after save; second save retires prior to `current=0` and keeps history listable; UUID PK + timestamps; table listed in data-layer header inventory (now under name `artifacts`).
- AST-1353 AC: successful Save Base Resume PUT still records live `artifacts.base_resume` into the versioned store; craft/Generate/Regenerate still do **not** write that store.
- Data layer still raises (no logging) on bad identity / missing `artifact_data`; `entity_type` still validated against `ENTITY_TYPES`.
- No UI→data import; Save still goes `api_candidate` → core → `database.save_artifact`.
- No backfill of historical `candidate_data.artifacts.base_resume` for candidates who never Save — rename only, same boundary as AST-1352.
