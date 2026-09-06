# AST-1597 — Artifact table rename and candidate_id

**Linear:** [AST-1597](https://linear.app/astralcareermatch/issue/AST-1597)
**Parent:** [AST-1594](https://linear.app/astralcareermatch/issue/AST-1594) — Add candidate_id to artifact, app_log, and job
**Publish ref:** `sub/AST-1594/AST-1597-artifact-table-rename-and-candidate-id`

Rename the versioned blob table from plural `artifacts` to singular `artifact`, add required `candidate_id` on every row, update data-layer ensure/CRUD/header inventory accordingly, and put copy-only migration SQL on the parent Linear Description for Susan to run (no seed; she drops `artifacts` after cutover). Does not touch `job` / `app_log` columns or logging (AST-1598).

## Explicit scope gate

This ticket’s **Scope** names only:

- `src/data/database.py` (artifact ensure/CRUD/inventory)
- parent Description migration SQL block

Every Files Changed row and every Stage step stays inside that list. No core/UI/utils call-site rewires, no `job`/`app_log` schema, no logging contextvar, no selected-candidate surface filter.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Header inventory `artifacts` → `artifact` + `candidate_id`; rename ensure globals/helpers; CREATE/SQL/index on `artifact`; require/set `candidate_id` on writes; return it on reads | data |
| Linear parent **AST-1594** Description | Append a runnable `## Migration SQL — artifacts → artifact` block (CREATE + INSERT backfill; no DROP; no seed) | Linear (not a repo file) |

**Do not touch:** `src/core/**`, `src/ui/**`, `src/utils/**`, `src/external/**`, `job` / `app_log` ensure or helpers, `tests/**`, `docs/test-bible/**`, `candidate_data` JSON key `artifacts` (library blob — unrelated to the table name), scripts under `scripts/` except that migration lives on Linear not as a committed seed.

## Stage 1: Header inventory + ensure `artifact` + `candidate_id`

**Done when:** Module docstring inventory names table `artifact` (not `artifacts`) and documents required `candidate_id`; a fresh DB and an existing DB that only had `artifacts` both expose table `artifact` with `candidate_id` after ensure; product ensure no longer creates or writes the plural table name for new work; old `artifacts` rows are copied (not deleted) when adopting.

1. In `src/data/database.py` module docstring **Tables used (inventory)**, replace the existing `artifacts — …` bullet with an `artifact — …` bullet that lists columns:
   - `artifact_uuid TEXT PK`
   - `candidate_id TEXT NOT NULL` (owning candidate; when `entity_type='candidate'`, equals `entity_id`; otherwise separate from `entity_id`)
   - `entity_type`, `entity_id`, `artifact_type`, `artifact_data`
   - `source_artifact_ids` (AST-1591)
   - `current`, `created_at`, `updated_at`
   - Active row: `current=1` for `(entity_type, entity_id, artifact_type)` (unchanged natural key)
   - Note rename from `artifacts` (AST-1597 / parent AST-1594); do **not** document `job.candidate_id` or `app_log.candidate_id` here (sibling AST-1598).

2. Rename module flag `_artifacts_schema_ensured` → `_artifact_schema_ensured` and function `_ensure_artifacts_table` → `_ensure_artifact_table`. Update every internal call site inside `database.py` that invoked `_ensure_artifacts_table` to call `_ensure_artifact_table`.

3. Rewrite `_ensure_artifact_table(conn)` behavior (still idempotent; still no logging — data raises / returns only):

   a. Helpers: keep `_table_exists` / `_column_names` local; index name becomes `idx_artifact_entity_type_current` on `artifact (entity_type, entity_id, artifact_type, current)`. Drop legacy index names when renaming/adopting if they exist (`idx_artifacts_entity_type_current`, `idx_astral_artifacts_entity_type_current`) via `DROP INDEX IF EXISTS` before recreating the new name.

   b. **If `artifact` already exists:** ensure `candidate_id` is present. If the column is missing, rebuild via copy (SQLite cannot add `NOT NULL` cleanly without default): create `artifact__cid_mig` with the full CREATE from (d), `INSERT INTO artifact__cid_mig (…) SELECT …` with backfill expression from step 4, `DROP TABLE artifact`, `ALTER TABLE artifact__cid_mig RENAME TO artifact`, then ensure index. If `candidate_id` already exists, only ensure index + `source_artifact_ids` column (same AST-1591 ADD COLUMN path as today, but against `artifact`). Commit; set flag; return.

   c. **Else if plural `artifacts` exists (and `artifact` does not):** **copy-adopt, do not DROP `artifacts`.** `CREATE TABLE artifact (…)` per (d); `INSERT INTO artifact (…) SELECT … FROM artifacts` with the same `candidate_id` backfill expression as Stage 3 / step 4; ensure index; commit; set flag; return. Leave `artifacts` in place for Susan to drop after verification.

   d. **Else if `astral_artifacts` exists (pre-AST-1364 leftover) and neither `artifact` nor `artifacts` exists:** `ALTER TABLE astral_artifacts RENAME TO artifact`; rename PK column `astral_artifact_uuid` → `artifact_uuid` if needed (same as today’s artifacts path); then apply the missing-`candidate_id` rebuild from (b); drop old astral index name; ensure index; commit; return.

   e. **Else (fresh DB):** `CREATE TABLE artifact` with:

   ```sql
   CREATE TABLE artifact (
       artifact_uuid TEXT PRIMARY KEY,
       candidate_id TEXT NOT NULL,
       entity_type TEXT NOT NULL,
       entity_id TEXT NOT NULL,
       artifact_type TEXT NOT NULL,
       artifact_data TEXT NOT NULL,
       source_artifact_ids TEXT NOT NULL DEFAULT '[]',
       current INTEGER NOT NULL DEFAULT 1,
       created_at TIMESTAMP NOT NULL,
       updated_at TIMESTAMP NOT NULL
   )
   ```

   Then create `idx_artifact_entity_type_current`; commit; set flag; return.

4. **`candidate_id` backfill expression** (shared by ensure copy paths and Linear migration SQL — keep identical):

   - When `entity_type = 'candidate'`: use `entity_id`.
   - When `entity_type = 'job'`: `(SELECT company.candidate_id FROM job JOIN company ON company.short_name = job.company WHERE job.astral_job_id = <source>.entity_id)` (scalar subquery).
   - When `entity_type = 'company'`: `(SELECT company.candidate_id FROM company WHERE company.short_name = <source>.entity_id)`.
   - Any other / NULL result: use empty string only inside a rebuild that still needs a NOT NULL column **is forbidden for the Linear migration** — migration INSERT must use `COALESCE(<subquery>, …)` only where AC allows; for migration SQL require non-null ownership: wrap as `COALESCE(NULLIF(TRIM(<resolved>), ''), CASE WHEN entity_type = 'candidate' THEN entity_id ELSE NULL END)` and **fail the INSERT for orphan job/company rows** by using a WHERE filter that skips rows that would get NULL, **or** document that Susan must fix orphans before cutover. **Concrete choice for this plan:** `INSERT` uses:

   ```sql
   CASE
     WHEN artifacts.entity_type = 'candidate' THEN artifacts.entity_id
     WHEN artifacts.entity_type = 'job' THEN (
       SELECT company.candidate_id FROM job
       JOIN company ON company.short_name = job.company
       WHERE job.astral_job_id = artifacts.entity_id
     )
     WHEN artifacts.entity_type = 'company' THEN (
       SELECT company.candidate_id FROM company
       WHERE company.short_name = artifacts.entity_id
     )
     ELSE NULL
   END
   ```

   as `candidate_id`, and add `WHERE candidate_id IS NOT NULL AND TRIM(candidate_id) != ''` via wrapping the INSERT as `INSERT INTO artifact (…) SELECT … FROM artifacts WHERE (<CASE…>) IS NOT NULL AND TRIM(<CASE…>) != ''` (repeat CASE or use a subquery). Do **not** invent new artifact content; skipped orphans stay only in `artifacts` for Susan to inspect before DROP.

⚠️ **Decision:** Ensure **copy-adopts** when only `artifacts` exists (CREATE `artifact` + INSERT backfill) and does **not** `DROP` or `RENAME` away `artifacts`. That matches parent “copy only; Susan drops manually” and keeps local/Railway DBs usable after code deploy without waiting for the Linear SQL paste — Linear SQL remains the documented operator path and must match this expression exactly.

⚠️ **Decision:** Do **not** keep ensuring or INSERT/UPDATE targeting table name `artifacts` after this stage. Plural table may still exist on disk until Susan drops it; product code paths ignore it.

## Stage 2: CRUD — SQL on `artifact`, require/set `candidate_id` on write

**Done when:** All artifact SELECT/UPDATE/INSERT SQL in `database.py` uses table `artifact`; every successful `save_artifact` insert stores a non-empty `candidate_id`; when `entity_type='candidate'`, stored `candidate_id == entity_id`; missing ownership fails with `ValueError` (no logging in data); read helpers return `candidate_id` in the row dict; natural key retire/get/list behavior unchanged aside from the table name and new column.

1. Extend `_ARTIFACT_SELECT` to include `candidate_id` (place it immediately after `artifact_uuid` to match CREATE column order). Update `_artifact_row_dict` to map the new column into `"candidate_id"` and shift indexes for `artifact_data` / `source_artifact_ids` / `current` / timestamps accordingly (or rebuild the mapper from named columns — prefer minimal diff: keep positional mapping consistent with the new SELECT list).

2. Add a private helper in the artifact section (public-then-helpers: place after the public CRUD block or with other artifact helpers — follow existing file organization near `_normalize_artifact_identity`):

   `_resolve_artifact_candidate_id(conn, entity_type: str, entity_id: str, candidate_id: Optional[str]) -> str`

   Behavior:

   - `cid = (candidate_id or "").strip()`
   - If `entity_type == "candidate"`: if `cid` and `cid != entity_id`, raise `ValueError` explaining they must match; return `entity_id` (so omitted `candidate_id` still sets the column).
   - If `cid` is non-empty: return `cid`.
   - If omitted/empty and `entity_type == "job"`: run the same job→company `candidate_id` lookup as Stage 1 backfill (on `conn`); if missing/blank, raise `ValueError("candidate_id required")`.
   - If omitted/empty and `entity_type == "company"`: `SELECT candidate_id FROM company WHERE short_name = ?`; if missing/blank, raise `ValueError("candidate_id required")`.
   - Otherwise raise `ValueError("candidate_id required")`.

⚠️ **Decision:** Scope is `database.py` only; existing core call sites (`candidate.py`, `tracker.py`) do not pass `candidate_id` today. Resolving omitted `candidate_id` for `candidate` from `entity_id`, and for `job`/`company` via ownership lookup, keeps writers green without inventing core rewires. Explicit wrong `candidate_id` on `entity_type=candidate` still fails loudly; unresolved job/company ownership still fails loudly — matching Notes / AC without expanding Files Changed.

3. Change `save_artifact` signature to add a keyword-only `candidate_id` **after** the existing optional `source_artifact_ids` (do not reorder or rename existing parameters):

   ```python
   def save_artifact(
       entity_type: str,
       entity_id: str,
       artifact_type: str,
       artifact_data: Any,
       source_artifact_ids: Optional[Sequence[str]] = None,
       *,
       candidate_id: Optional[str] = None,
   ) -> str:
   ```

   Keep positional `(entity_type, entity_id, artifact_type, artifact_data[, source_artifact_ids])` so current callers stay valid. Inside `_with_conn`, after `_ensure_artifact_table(conn)`, call `_resolve_artifact_candidate_id(conn, et, eid, candidate_id)` and use the returned value on INSERT.

4. Rewrite retire UPDATE, INSERT, and all SELECTs in `save_artifact`, `retire_current_artifact`, `get_current_artifact`, `get_artifact`, `list_artifacts` to use table name `artifact` (not `artifacts`). INSERT column list must include `candidate_id`. UPDATE retire statements do not require a `candidate_id` predicate (natural key unchanged).

5. Docstrings on these helpers: say table `artifact` / “artifact row”; mention required `candidate_id` on write. Do not add logging.

6. **Do not** rename public function names (`save_artifact`, `list_artifacts`, etc.) — only the SQLite table name changes. **Do not** change `candidate_data` JSON key `artifacts`.

## Stage 3: Parent Description migration SQL (Linear AST-1594)

**Done when:** Parent AST-1594 Description contains a clearly marked migration SQL section Susan can run as-is; SQL copies `artifacts` → `artifact` with the Stage 1 backfill expression; does not INSERT invented rows; does not `DROP TABLE artifacts` (Susan drops manually after verification).

1. Via `linear_proxy.py --as ada get-issue AST-1594`, capture the full current Description.

2. Append (do not delete define/dispatch sections) a new trailing section exactly titled:

   `## Migration SQL — artifacts → artifact (AST-1597)`

   Body must include:

   - Short operator notes: run against the live SQLite file; verify row counts; then `DROP TABLE artifacts;` manually; no seed file in repo.
   - Idempotence guidance: if `artifact` already exists and is populated (ensure already copy-adopted), skip or run only after confirming empty — do not double-insert PKs. Prefer: `CREATE TABLE IF NOT EXISTS` is **not** enough for IF NOT EXISTS + INSERT; document: **only run the INSERT when `artifact` is empty or freshly created**; if ensure already copied, Susan verifies then drops `artifacts` only.
   - Full SQL:

   ```sql
   CREATE TABLE IF NOT EXISTS artifact (
       artifact_uuid TEXT PRIMARY KEY,
       candidate_id TEXT NOT NULL,
       entity_type TEXT NOT NULL,
       entity_id TEXT NOT NULL,
       artifact_type TEXT NOT NULL,
       artifact_data TEXT NOT NULL,
       source_artifact_ids TEXT NOT NULL DEFAULT '[]',
       current INTEGER NOT NULL DEFAULT 1,
       created_at TIMESTAMP NOT NULL,
       updated_at TIMESTAMP NOT NULL
   );

   CREATE INDEX IF NOT EXISTS idx_artifact_entity_type_current
       ON artifact (entity_type, entity_id, artifact_type, current);

   INSERT INTO artifact (
       artifact_uuid, candidate_id, entity_type, entity_id, artifact_type,
       artifact_data, source_artifact_ids, current, created_at, updated_at
   )
   SELECT
       a.artifact_uuid,
       b.candidate_id,
       a.entity_type,
       a.entity_id,
       a.artifact_type,
       a.artifact_data,
       COALESCE(a.source_artifact_ids, '[]'),
       a.current,
       a.created_at,
       a.updated_at
   FROM artifacts AS a
   JOIN (
       SELECT
           src.artifact_uuid AS artifact_uuid,
           CASE
             WHEN src.entity_type = 'candidate' THEN src.entity_id
             WHEN src.entity_type = 'job' THEN (
               SELECT company.candidate_id FROM job
               JOIN company ON company.short_name = job.company
               WHERE job.astral_job_id = src.entity_id
             )
             WHEN src.entity_type = 'company' THEN (
               SELECT company.candidate_id FROM company
               WHERE company.short_name = src.entity_id
             )
             ELSE NULL
           END AS candidate_id
       FROM artifacts AS src
   ) AS b ON b.artifact_uuid = a.artifact_uuid
   WHERE b.candidate_id IS NOT NULL
     AND TRIM(b.candidate_id) != ''
     AND NOT EXISTS (
       SELECT 1 FROM artifact AS existing
       WHERE existing.artifact_uuid = a.artifact_uuid
     );
   ```

   Ensure’s copy-adopt INSERT (Stage 1) must use the same CASE logic (same joins / same skip-when-null rule).

3. Write the full updated Description to a temp file and run:

   `python3 ~/.cursor/skills/rollcall/linear_proxy.py --as ada save-issue AST-1594 --description-file <path>`

   Do **not** change parent state, assignee, or estimate. Do **not** strip existing AC / Proposed children / Architectural sections.

4. On child AST-1597, do **not** duplicate the full SQL in Linear comments (comment discipline) — the plan doc + parent Description hold it. After publish, child comment is SHA + ≤5 words only (plan-child §9).

## Estimate

Confirm Chuckles estimate: 5 — agree

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree during **build-child**, then `git push origin HEAD:sub/AST-1594/AST-1597-artifact-table-rename-and-candidate-id`.
- No silent extra files. If `database.py` has drifted (signatures, ensure shape), stop and comment the **parent** AST-1594 with the Stage blocked template from plan-child.
- Engineers do not edit `tests/**` or `docs/test-bible/**`.

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1597
**Overall:** APPROVED
**Publish ref:** `sub/AST-1594/AST-1597-artifact-table-rename-and-candidate-id` @ `2e0709ed4cbb5508e022eca255be1739fb428ae4`

## Traceability
AC1→Stages 1–2 (ensure `artifact` + CRUD on `artifact`, no product writes to `artifacts`); AC2→Stage 3 (migration SQL on parent AST-1594 Description per child Scope); AC3→Stage 2 (`_resolve_artifact_candidate_id`, `save_artifact` INSERT); AC4→Stage 1 (header inventory bullet)

## Findings

### acceptable
- **Location:** Linear AST-1597 assignee  
  **Finding:** Assignee is Ada, not Joan at spawn time.  
  **Recommendation:** Chuckles restores implementer after posting upshot per validate-plan §8.

### discuss
- **Location:** Child AC #2 vs Scope  
  **Finding:** AC text says “this ticket’s Description includes migration SQL,” but Scope and Stage 3 correctly place SQL on **parent** AST-1594 Description (matches epic partition).  
  **Recommendation:** Optional AC wording cleanup on the child ticket; plan is faithful to Scope and parent functional scope.

- **Location:** Stage 2 — `_resolve_artifact_candidate_id`  
  **Finding:** Omitted `candidate_id` for `candidate`/`job`/`company` entity types is resolved via lookup rather than immediate `ValueError`; column is still always populated on INSERT, and unresolved ownership still fails loudly.  
  **Recommendation:** Accept for database.py-only scope (no core call-site rewires); explicit wrong `candidate_id` on `entity_type=candidate` still raises.

**Considered (in-session):** Universal orch.* statutes — all conform (plan doc + data-layer change only). Scoped: `astral.standards.database-header-inventory`, `astral.standards.in-scope-only`, `astral.standards.data-raises-caller-logs`, `astral.standards.public-then-helpers`, `astral.standards.dry-and-focused-functions`, `astral.standards.no-cross-contamination`, `astral.layers.import-direction` — conform. Pattern `pattern.layers.import-discipline` — conforms (data-only; no layer violations). Remaining scoped astral.* statutes excluded (no matching layer/path/change_type intersection).

context_tokens≈42000
```


## Build complete

**Publish ref:** `sub/AST-1594/AST-1597-artifact-table-rename-and-candidate-id` @ `5daf0ea2e0803f3587bb73434de7efd523aabdf0`

Stages 1–3 delivered: header inventory + `_ensure_artifact_table` copy-adopt; CRUD on `artifact` with required `candidate_id` resolve/insert; migration SQL appended to parent AST-1594 Description.
