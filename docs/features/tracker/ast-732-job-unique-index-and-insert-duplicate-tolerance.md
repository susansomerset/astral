# Job unique index and insert duplicate tolerance (Duplicate jobs ingested)

**Linear issue:** https://linear.app/astralcareermatch/issue/AST-732/job-unique-index-and-insert-duplicate-tolerance-duplicate-jobs

**Publish ref:** `sub/AST-728/AST-732-job-unique-index-and-insert-duplicate-tolerance`

Add a durable unique identity constraint on the `job` table and make **insert-time** unique violations safe for Tracker ingest. Lazy schema migration in `_ensure_job_schema` creates a partial unique index on `(company, job_title, company_job_id)` for rows with a complete identity triple. `database.save_job` returns a duplicate-bounce signal instead of raising when a **new-row INSERT** would violate that index. `ingest_jobs` and `ingest_board_listings` count bounces in `duplicates`. Pre-insert listing dedup (`raw_job_listing_is_duplicate`, board listing keys) stays unchanged.

**Prerequisite:** **AST-729** cleanup must run in any environment that still has duplicate complete triples before this index migration can succeed (SQLite will reject index creation on duplicate keys).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Partial unique index in `_ensure_job_schema`; `save_job` insert duplicate tolerance + bool return | data |
| `src/core/tracker.py` | Wire ingest paths to count `save_job` duplicate bounces; passthrough bool on `save_job` facade | core |

## Stage 1: Partial unique index lazy migration

**Done when:** `_ensure_job_schema` creates index `idx_job_identity_unique` idempotently on every DB open; index exists only for complete identity triples; re-opening DB does not error when index already present.

1. In `src/data/database.py`, add module constant:
   ```python
   _JOB_IDENTITY_UNIQUE_INDEX = "idx_job_identity_unique"
   ```
2. At the end of `_ensure_job_schema` (after existing column migrations, before `_job_schema_ensured = True`), add index ensure block mirroring the company index loop pattern (~lines 695–701):
   - Query `SELECT 1 FROM sqlite_master WHERE type='index' AND name=?` with `_JOB_IDENTITY_UNIQUE_INDEX`.
   - If missing, execute:
     ```sql
     CREATE UNIQUE INDEX idx_job_identity_unique
     ON job (company, job_title, company_job_id)
     WHERE company_job_id IS NOT NULL
       AND job_title IS NOT NULL
       AND TRIM(company_job_id) != ''
       AND TRIM(job_title) != ''
     ```
   - `conn.commit()` after successful create.
   - Do **not** swallow `IntegrityError` / unique-violation failures during index build — let them propagate so operators know **AST-729** cleanup is required.
   - Swallow only benign `OperationalError` for race/idempotent cases if needed (same as other index creates); duplicate-key index build failure must surface.
3. Add a one-line comment in `_ensure_job_schema`: AST-732 partial unique index; incomplete identity rows (NULL/empty `company_job_id` or `job_title`) remain outside the constraint until Consult populates them.

⚠️ **Decision:** Partial unique index (not table-level UNIQUE) so multiple pre-Consult ingest rows with NULL `company_job_id` remain valid, matching TRACKER_DATA_MODEL ingest contract and **AST-729** dedupe scope (complete triples only).

⚠️ **Decision:** Index name `idx_job_identity_unique` is stable for IntegrityError message matching in Stage 2.

## Stage 2: `save_job` insert duplicate tolerance

**Done when:** `database.save_job` returns `True` on successful insert or update, `False` on insert identity duplicate bounce; UPDATE-path unique violations still raise; PK and other IntegrityErrors still raise.

1. Change `save_job` signature in `src/data/database.py` from `-> None` to `-> bool`. Docstring: `True` = row inserted or updated; `False` = new-row insert bounced because `(company, job_title, company_job_id)` already exists (complete triple).
2. Add private helper above `save_job`:
   ```python
   def _is_job_identity_unique_violation(exc: sqlite3.IntegrityError) -> bool:
       msg = str(exc).lower()
       return _JOB_IDENTITY_UNIQUE_INDEX.lower() in msg or (
           "unique constraint failed" in msg
           and "job.company" in msg
           and "job.job_title" in msg
           and "job.company_job_id" in msg
       )
   ```
3. In `_with_conn`, wrap **only** the INSERT `conn.execute(...)` block in try/except:
   - On `sqlite3.IntegrityError as e`:
     - If `_is_job_identity_unique_violation(e)`: `return False` (no commit — insert rolled back with connection or explicit rollback before return).
     - Else: re-raise.
   - On successful INSERT or UPDATE: `conn.commit()` then `return True`.
   - Early return when UPDATE has empty `sets`: `return True` (no-op update, same as today).
4. Update `_with_conn` outer flow so `_run_with_retry(_with_conn)` returns the bool from `_with_conn` and `save_job` returns that value to callers.
5. Do **not** catch IntegrityError on UPDATE — collision when metadata would duplicate another row is **AST-733** scope; must still raise to Consult callers.

⚠️ **Decision:** Duplicate bounce applies to INSERT branch only. Data layer does not log (per ticket notes); callers interpret `False`.

## Stage 3: Tracker ingest wiring

**Done when:** `ingest_jobs` and `ingest_board_listings` increment `duplicates` (not `new`) when `database.save_job` returns `False`; return dict shape unchanged; existing pre-insert dedup checks remain first in the loop.

1. In `src/core/tracker.py` `ingest_jobs`, replace bare `database.save_job(...)` + `new_count += 1` with:
   ```python
   inserted = database.save_job(...)
   if not inserted:
       dup_count += 1
       continue
   new_count += 1
   ```
   Keep existing `raw_job_listing_is_duplicate` and title-filter checks **before** `save_job` (order unchanged).
2. Same pattern in `ingest_board_listings` for its `database.save_job(...)` call (after board listing dedup / title filter).
3. Update `save_job` facade at line ~617:
   ```python
   def save_job(astral_job_id: str, **kwargs: Any) -> bool:
       """Direct job row upsert for admin/API callers. Returns False on identity duplicate insert bounce."""
       return database.save_job(astral_job_id, **kwargs)
   ```
4. Do **not** change `initialize_job`, `transition_job_state`, or `save_job_data` — they update existing rows or rely on raise-on-failure for invalid ids; no ingest count wiring needed.

## Stage 4: Compile gate

**Done when:** `python -m py_compile src/data/database.py src/core/tracker.py` exits 0.

1. Run compile from repo root on both touched files.
2. Fix syntax/import errors before stage commit.

## Self-Assessment

**Scope:** `Single-Component` — two files in data + core Tracker ingest path; no UI, Gazer, or Consult parsing changes.

**Conf:** `high` — `_ensure_job_schema` index pattern and `save_job` upsert shape are established; ticket specifies partial index columns, insert-only bounce, and ingest return dict preservation.

**Risk:** `Medium` — index creation fails on environments with uncleansed duplicate triples (forces **AST-729** first); misclassified IntegrityError could hide real DB faults — mitigated by narrow `_is_job_identity_unique_violation` check and INSERT-only catch.

## ASTRAL_CODE_RULES self-review

- **§1.3 DRY:** Single `_is_job_identity_unique_violation` helper; index name constant reused.
- **§2.1 Config:** No new config keys; ingest initial state unchanged.
- **§2.4 Batch processing:** N/A.
- **§3.3 Imports:** No new cross-layer violations.
- **§3.5 Naming:** `idx_job_identity_unique`, snake_case bool return documented.
- **Data layer no log:** Duplicate bounce returns bool only — no logging added.
- **No conflicts** requiring plan revision.
