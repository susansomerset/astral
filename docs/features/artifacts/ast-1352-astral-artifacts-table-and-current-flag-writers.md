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
