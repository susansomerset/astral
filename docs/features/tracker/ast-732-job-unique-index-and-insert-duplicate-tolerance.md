<!-- linear-archive: AST-732 archived 2026-07-22 -->

## Linear archive (AST-732)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-732/job-unique-index-and-insert-duplicate-tolerance-duplicate-jobs  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-728 — Duplicate jobs ingested  
**Blocked by / blocks / related:** parent: AST-728; blocks: AST-733

### Description

## What this implements

Add a durable unique identity constraint on the job table and make insert-time duplicate violations safe: lazy schema migration adds unique index on `(company, job_title, company_job_id)`; `save_job` (and related insert paths) treat unique-constraint violations as duplicate bounces without raising to Tracker ingest callers.

## Acceptance criteria

* A unique index exists on `(company, job_title, company_job_id)` on the job table.
* Opening the database in a fresh environment applies the index idempotently without manual migration steps.
* Attempting to insert a job row whose triple matches an existing row does not create a second row and does not surface an unhandled error to Tracker ingest callers.
* Re-running ingest on listings whose structured identity already exists does not increase the job count for that triple.
* Existing Tracker ingest return shape (`new`, `duplicates`, `invalid_title`) remains valid; duplicate-key rejections increment or behave as duplicate skips, not hard failures.

## Boundaries

* Does not run one-time historical cleanup — **AST-729** (must run before this migration applies in environments with existing dupes).
* Does not handle post–qualify metadata collision deletes — **AST-733**.
* Does not change Gazer scrape or Consult parsing logic.

## Notes for planning

* Extend `_ensure_job_schema` lazy migration pattern (same as other DDL changes).
* Data layer raises no logs; return duplicate signal to core/tracker for counting.
* Hot files: `src/data/database.py`, possibly `src/core/tracker.py` for ingest count wiring.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-728-duplicate-jobs-ingested`, child `sub/AST-728/AST-732-job-unique-index-and-insert-duplicate-tolerance`. Created at dispatch-parent.

### Comments

#### hedy — 2026-06-18T05:43:08.467Z
**Diff:** `origin/dev...origin/sub/AST-728/AST-732-job-unique-index-and-insert-duplicate-tolerance` (product: `src/data/database.py`, `src/core/tracker.py`; Betty tests + bible)

### Plan fidelity
- **Stage 1:** `idx_job_identity_unique` partial unique index on `(company, job_title, company_job_id)` with NULL/empty `job_title` / `company_job_id` excluded; idempotent `sqlite_master` check; index-create failures propagate (no swallow) — operators need **AST-729** first if dupes remain.
- **Stage 2:** `save_job` → `bool`; INSERT-only `IntegrityError` catch with `conn.rollback()` + `False`; UPDATE path unchanged (collision on metadata update still raises — **AST-733** scope).
- **Stage 3:** `ingest_jobs` / `ingest_board_listings` count `save_job` `False` as `duplicates`; pre-insert dedup order preserved; tracker `save_job` facade passthrough.
- Boundaries respected: no cleanup migration script, no post-qualify collision delete in `initialize_job`, no Gazer/Consult changes.

### ASTRAL_CODE_RULES
- **§2.1 / §3.5:** Stable index name constant; partial index matches ingest contract (incomplete triples outside constraint).
- **§3.3:** Data-layer only change + thin tracker wiring; no new cross-layer violations.
- **Data layer no log:** Duplicate bounce is bool return only — correct.
- **D2:** No swallowed exceptions; narrow `_is_job_identity_unique_violation` matcher (index name + column tuple).

### Code quality
- `_run_with_retry` returns bool from `_with_conn`; tests cover index lazy migration, idempotent re-open, insert bounce, incomplete-triple allowance, update still `True`, and ingest duplicate counting.

### Advisory (not blocking)
- **Diff bundle:** Branch also carries **AST-729** test bible + component script tests from `merge-tests` — product diff is only the two `src/` files above.
- **Prerequisite:** Index migration will hard-fail on environments with uncleansed duplicate complete triples — run **AST-729** cleanup before deploying this to prod-shaped DBs.
- **Callers ignoring bool:** `initialize_job`, `transition_job_state`, `save_job_data`, and `api_jobs` bulk_state ignore `save_job` return — acceptable here (UPDATE-only paths; `False` is INSERT-bounce-only).

**Verdict:** No fix-now or discuss items. Ready for `resolve-child`.

#### radia — 2026-06-18T05:42:27.534Z
**Diff:** `origin/dev...origin/sub/AST-728/AST-732-job-unique-index-and-insert-duplicate-tolerance` @ `5559ade`
**Plan doc:** `docs/features/tracker/ast-732-job-unique-index-and-insert-duplicate-tolerance.md` (Review section)

### Plan fidelity
Partial unique index `idx_job_identity_unique` matches spec (complete triple WHERE clause); lazy migration idempotent; index-build IntegrityError not swallowed (AST-729 prerequisite surfaces). `save_job` INSERT-only bounce with `conn.rollback()` + bool return; UPDATE path still raises (AST-733 collisions). Ingest paths wire bounce to `duplicates` after existing pre-insert dedup.

### ASTRAL_CODE_RULES
- **§2.1 / §3.5:** Index name constant; no new config keys.
- **§3.3:** Data + core only; no UI layer changes.
- **Data layer no log:** Duplicate bounce returns bool only — compliant.
- **D2:** INSERT IntegrityError catch is narrow (`_is_job_identity_unique_violation`); other errors re-raise.

### Tests
Component manifest covers index creation/idempotency, insert bounce vs incomplete triple vs update path, ingest duplicate count wiring for both ingest entry points.

### fix-now
None.

### advisory
- Diff vs `origin/dev` includes AST-729 test-bible + component tests via `merge-tests` (sibling not on dev yet) — expected epic stacking, not AST-732 product scope.
- Operator order: AST-729 cleanup before index migration in environments with duplicate complete triples (plan prerequisite).

#### betty — 2026-06-18T05:39:50.349Z
## QA test manifest (AST-732)

**Publish ref:** `origin/sub/AST-728/AST-732-job-unique-index-and-insert-duplicate-tolerance` @ `d469273d` (`merge-tests(AST-732): origin/tests 3e5cf2f5`)

**Prerequisite:** **AST-729** cleanup must have run in any DB that still holds duplicate complete identity triples before the index migration applies.

### 1. Partial unique index lazy migration (required)

`tests/component/data/database/test_jobs.py::TestAst732JobIdentityUniqueIndex`

- `test_ensure_job_schema_creates_partial_unique_index` — `idx_job_identity_unique` exists with partial WHERE on complete triple
- `test_index_ensure_idempotent_on_second_open` — second `_ensure_job_schema` does not duplicate index

### 2. `save_job` insert duplicate bounce (required)

`tests/component/data/database/test_jobs.py::TestAst732SaveJobDuplicateBounce`

- `test_insert_duplicate_complete_triple_returns_false` — second INSERT with same `(company, job_title, company_job_id)` returns `False`, no second row
- `test_incomplete_identity_allows_multiple_inserts` — NULL `company_job_id` rows outside partial index
- `test_update_existing_row_still_returns_true` — UPDATE path unchanged

### 3. Tracker ingest wiring (required)

`tests/component/core/test_tracker.py`

- `TestIngestJobs::test_counts_identity_duplicate_bounce_from_save_job` — `save_job` `False` → `duplicates`, not `new`
- `TestIngestBoardListings::test_counts_identity_duplicate_bounce_from_save_job` — same for board ingest

### 4. Regression (required)

- `tests/component/data/database/test_jobs.py::TestSaveJob` (existing insert/merge)
- `tests/component/core/test_tracker.py::TestIngestJobs::test_counts_new_and_duplicate_rows` (pre-insert dedup unchanged)

**Narrowed run:**

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_jobs.py::TestAst732JobIdentityUniqueIndex \
  tests/component/data/database/test_jobs.py::TestAst732SaveJobDuplicateBounce \
  tests/component/core/test_tracker.py::TestIngestJobs::test_counts_identity_duplicate_bounce_from_save_job \
  tests/component/core/test_tracker.py::TestIngestBoardListings::test_counts_identity_duplicate_bounce_from_save_job \
  tests/component/data/database/test_jobs.py::TestSaveJob \
  tests/component/core/test_tracker.py::TestIngestJobs::test_counts_new_and_duplicate_rows \
  -q
```

**Bible shasums on publish ref:**

- `docs/test-bible/data/database/jobs.md` — `010037a23904be57519fd14605fd38f10ec47f6de86da28d5ce3f7598b9adcf7`
- `docs/test-bible/core/tracker.md` — `51f5bcd0ebf70a00bb5a88f698fead0de1d28f384da48a0159b1d69a6d23b328`

— Betty

#### betty — 2026-06-18T05:39:38.884Z
**Bible shasums (publish ref):**

- `docs/test-bible/data/database/jobs.md` — `010037a23904be57519fd14605fd38f10ec47f6de86da28d5ce3f7598b9adcf7`
- `docs/test-bible/core/tracker.md` — `51f5bcd0ebf70a00bb5a88f698fead0de1d28f384da48a0159b1d69a6d23b328`

#### hedy — 2026-06-18T05:31:56.121Z
Plan doc: `docs/features/tracker/ast-732-job-unique-index-and-insert-duplicate-tolerance.md`

GitHub: https://github.com/susansomerset/astral/blob/sub/AST-728/AST-732-job-unique-index-and-insert-duplicate-tolerance/docs/features/tracker/ast-732-job-unique-index-and-insert-duplicate-tolerance.md

**Self-assessment**
- **Scope:** `Single-Component` — `database.py` partial unique index + `save_job` bool return; `tracker.py` ingest dup wiring only.
- **Conf:** `high` — lazy `_ensure_job_schema` index pattern and insert-only IntegrityError bounce are fully specified; pre-insert listing dedup preserved.
- **Risk:** `Medium` — index build fails if **AST-729** cleanup not run on duped DBs; mitigated by partial index (incomplete triples excluded) and narrow error classifier on INSERT only.

Four stages: (1) partial unique index `idx_job_identity_unique`, (2) `save_job` returns `False` on identity duplicate insert, (3) `ingest_jobs` / `ingest_board_listings` count bounces in `duplicates`, (4) compile gate.

---

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

---

## Review

**Branch:** `origin/sub/AST-728/AST-732-job-unique-index-and-insert-duplicate-tolerance`  
**Diff baseline:** `origin/dev`  
**Review tip:** `d469273`

**Built:** Stages 1–4 — partial unique index `idx_job_identity_unique` in `_ensure_job_schema`; `save_job` returns bool with INSERT-only identity duplicate bounce (`conn.rollback()` on bounce); `ingest_jobs` / `ingest_board_listings` count bounces in `duplicates`; tracker `save_job` facade passthrough; Betty manifest + component tests on `origin/tests` merge.

### What's solid

- Plan fidelity: partial unique index SQL matches spec (complete triple only); idempotent lazy migration with no IntegrityError swallow on index build; `_is_job_identity_unique_violation` helper with narrow message match; INSERT-only catch with rollback; UPDATE path still raises for AST-733 collisions.
- Ingest wiring: `ingest_jobs` and `ingest_board_listings` check `save_job` bool after existing pre-insert dedup; return dict shape preserved.
- Layer rules: data layer returns bool, no logging added; core interprets signal; no new cross-layer imports.
- Tests: index creation/idempotency, insert bounce vs incomplete triple vs update path, ingest duplicate count wiring — aligned with test-bible manifest.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| — | — | No fix-now items. |

### Recommended actions

| Severity | Location | Action |
| --- | --- | --- |
| advisory | diff vs `origin/dev` | Diff includes AST-729 test-bible + component tests (sibling not on dev yet) via `merge-tests` — expected epic stacking; not AST-732 product scope. |
| advisory | operator runbook | Environments with duplicate complete triples must run AST-729 cleanup before index migration — already documented in plan prerequisite. |

---

## Resolution

**Date:** 2026-06-18  
**Resolved by:** Hedy (resolve-child)

Radia posted **no fix-now** items. Advisory notes (sibling AST-729 tests stacked via `merge-tests`; AST-729 cleanup prerequisite before index migration) accepted as documented.

**§9a dry-run:** `origin/sub/AST-728/AST-732-job-unique-index-and-insert-duplicate-tolerance` @ `5559ade` merges cleanly into **`origin/dev`** and **`origin/ftr/duplicate-jobs-ingested`**.

**Product changes in resolve:** none — review clean. Manifest re-run: 11 passed.
