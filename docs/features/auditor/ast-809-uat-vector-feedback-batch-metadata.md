# AST-809 — UAT: Capture batch id, completion timestamp, and batch size with vector feedback

- **Linear:** [AST-809](https://linear.app/astralcareermatch/issue/AST-809/uat-capture-batch-id-completion-timestamp-and-batch-size-with-vector)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation) — Runtime Rubric Validation
- **Publish ref:** `origin/sub/AST-378/AST-809-uat-vector-feedback-batch-metadata`
- **Shipped baseline:** [AST-724](https://linear.app/astralcareermatch/issue/AST-724/runtime-vector-feedback-capture-and-lenient-parse-runtime-rubric) capture + [AST-725](https://linear.app/astralcareermatch/issue/AST-725/admin-vector-feedback-screen-runtime-rubric-validation) admin list

## Summary

Susan UAT 2026-06-25: **vector_feedback** rows must carry **batch execution metadata** Susan uses to inspect rubric feedback runs — **batch id**, **completion timestamp**, and **batch size (entity count)** — and Admin Vector Feedback must expose all three for sort/filter alongside existing columns.

**Root cause:** AST-724 writes `batch_id` and `created_at` on insert but does not persist **`batch_size`**, does not set an explicit **`completed_at`**, and the SUCCESS capture hook runs even when **`batch_id`** is falsy (non-dispatch / missing `log_batch_id`), producing rows that appear to lack run identifiers in Admin.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| Lenient parse, FEEDBACK fallback, rubric_vector versioning | — (unchanged) |
| Human-readable vector label hydration in Admin | separate UAT bug |
| Dispatch ledger / timesheet schema changes | — |

## Parent AC (quoted inline)

> 3. When vector feedback parses cleanly, **vector_feedback** rows are persisted with correct **rubric_vector** UUID, candidate, task run identifier, and one row per feedback type per vector.

> 6. Admin Vector Feedback page lists **vector_feedback** rows with sort/filter on candidate, task, vector code, feedback type, value, run/batch identifiers.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Lazy-add `batch_size`, `completed_at` on `vector_feedback`; extend insert + list queries | data |
| `src/core/agent.py` | Pass batch metadata into capture; skip insert when `batch_id` falsy | core |
| `src/ui/api/api_admin.py` | Add admin column defs for `batch_size`, `completed_at` | ui |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**.

## Stage 1: Schema and insert path

**Done when:** New installs create `vector_feedback` with `batch_size` + `completed_at`; existing DBs get lazy `ALTER TABLE`; `insert_vector_feedback_rows` persists all three metadata fields on every row.

1. In **`src/data/database.py`**, update the **`vector_feedback`** header inventory line to document **`batch_size INTEGER`**, **`completed_at TIMESTAMP`**, and that **`created_at`** remains row insert time (same instant as capture).

2. In **`_ensure_vector_feedback_table(conn)`**:
   - Extend **`CREATE TABLE`** for greenfield installs:

     ```sql
     batch_size INTEGER,
     completed_at TIMESTAMP NOT NULL,
     ```

     (Keep existing columns including **`batch_id TEXT NOT NULL`**, **`created_at TIMESTAMP NOT NULL`**.)

   - After table exists, lazy migrate with **`PRAGMA table_info`** pattern used elsewhere in this file:

     ```python
     cols = {row[1] for row in conn.execute("PRAGMA table_info(vector_feedback)").fetchall()}
     if "batch_size" not in cols:
         conn.execute("ALTER TABLE vector_feedback ADD COLUMN batch_size INTEGER")
     if "completed_at" not in cols:
         conn.execute("ALTER TABLE vector_feedback ADD COLUMN completed_at TIMESTAMP")
     conn.commit()
     ```

3. Extend **`insert_vector_feedback_rows`** signature:

   ```python
   def insert_vector_feedback_rows(
       vector_rows: List[Dict[str, str]],
       *,
       candidate_id: str,
       batch_id: str,
       task_key: str,
       batch_size: int,
       completed_at: Optional[str] = None,
       agent_data_id: Optional[str] = None,
   ) -> None:
   ```

   - Require truthy **`batch_id`** — if missing/blank, **return immediately** (no insert).
   - Set **`ts = completed_at or _utc_now()`** once per call; use **`ts`** for both **`completed_at`** and **`created_at`** on every inserted row.
   - Set **`bs = int(batch_size) if batch_size and batch_size > 0 else 1`**.
   - Extend **`INSERT`** column list and values tuple:

     ```sql
     ..., batch_size, completed_at, created_at)
     VALUES (..., ?, ?, ?)
     ```

     with **`(bs, ts, ts)`** for the three trailing columns.

4. Re-audit the single **`INSERT INTO vector_feedback`** literal in this change — column names, `?` count, and tuple length must match (**ASTRAL_CODE_RULES** lazy-schema rule).

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §1.1 inventory | Header + `_ensure_*` updated |
| §2.4 batch | `batch_id`, `batch_size`, completion time on row |
| §3.3 imports | data → utils only |

---

## Stage 2: Capture hook — pass batch metadata from `do_task`

**Done when:** Rubric-backed SUCCESS capture writes rows only when `batch_id` is set; each row carries dispatch `batch_size` and a single completion timestamp.

1. In **`src/core/agent.py`**, extend **`_capture_rubric_vector_feedback`** kwargs:

   ```python
   batch_size: int,
   completed_at: Optional[str] = None,
   ```

   - At top of function (after success gate), if not **`(batch_id or "").strip()`**: **return** (no FEEDBACK side effect change — unparseable path unchanged).

2. Pass through to **`insert_vector_feedback_rows`**:

   ```python
   insert_vector_feedback_rows(
       parsed_rows,
       candidate_id=candidate_id,
       batch_id=batch_id,
       task_key=task_key,
       batch_size=batch_size,
       completed_at=completed_at,
   )
   ```

3. At the SUCCESS hook (~line 2128), when calling **`_capture_rubric_vector_feedback`**, add:

   ```python
   batch_size=batch_size,
   completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
   ```

   Use the same **`batch_id`** and **`batch_size`** locals already resolved in **`do_task`** (`ctx.get("batch_size", 1)`).

⚠️ **Decision:** **`completed_at`** is set once at capture time on the SUCCESS path (task completion), not per-vector staggered timestamps.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §2.4 batch | Metadata sourced from dispatch/`do_task` context |
| §3.3 imports | core → data only |

---

## Stage 3: Admin API — expose new columns

**Done when:** `GET /api/admin/vector_feedback?req_dict=1` includes **`batch_size`** and **`completed_at`** columns; list query returns both fields.

1. In **`list_vector_feedback`**, extend **`SELECT`**:

   ```sql
   vf.batch_size, vf.completed_at,
   ```

   (Place after **`vf.batch_id`**.)

2. In **`src/ui/api/api_admin.py`**, extend **`_VECTOR_FEEDBACK_COLUMNS`** after **`batch_id`**:

   ```python
   {"key": "batch_size", "label": "Batch size", "type": "int"},
   {"key": "completed_at", "label": "Completed", "type": "datetime"},
   ```

   Keep existing **`created_at`** column (Date) for backward compatibility; **`completed_at`** is the UAT-facing completion field.

3. **No React file changes** — **`AdminVectorFeedback`** loads columns from **`req_dict=1`**; new keys appear automatically.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §3.3 imports | ui → data |
| Scope | Read-only admin column exposure only |

---

## Self-Assessment

**Scope:** `Single-Component` — `vector_feedback` schema migration, capture insert args, and admin column metadata; no parse or rubric logic changes.

**Conf:** `high` — Follows existing lazy `ALTER TABLE`, `insert_vector_feedback_rows`, and Admin Timesheets `batch_size` column patterns; root cause identified in capture hook + missing columns.

**Risk:** `low` — Nullable legacy rows after migration; new captures populate all fields. Wrong metadata only affects Admin inspection, not task grading.

## Self-Review vs ASTRAL_CODE_RULES

| Section | Assessment |
|---------|------------|
| §1.1 Scope | Extends inventory table only |
| §1.3 DRY | Single insert path; admin columns mirror timesheets |
| §2.4 Batch | Golden-ticket `batch_id` required; `batch_size` from `do_task` ctx |
| §2.6 State machine | No entity state transitions |
| §3.3 Imports | data / core / ui layers respected |
| §3.5 Naming | `completed_at` matches `dispatch_ledger` convention |

No unresolved rule conflicts.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-378/AST-809-uat-vector-feedback-batch-metadata` (code tip `4a9f125`)  
**Reviewed:** 2026-06-18

Focused UAT fix diff (10 files) — sibling epic commits already on `origin/ftr`; this review is AST-809 only.

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity (backend) | Lazy `ALTER TABLE` for `batch_size` + `completed_at`; greenfield CREATE updated; header inventory updated. |
| Insert path | 11 columns / 11 bind params; `ts` shared for `completed_at` + `created_at`; `bs` default 1; truthy `batch_id` gate on insert. |
| Capture hook | `_capture_rubric_vector_feedback` skips when `batch_id` blank; passes `batch_size` + `completed_at` from `do_task` SUCCESS hook. |
| Admin API | `_VECTOR_FEEDBACK_COLUMNS` + `list_vector_feedback` SELECT include new fields; `req_dict=1` tests pass. |
| §2.4 batch | Metadata sourced from dispatch `batch_id` / `ctx.batch_size`; no grading impact. |
| Tests | `TestAst809VectorFeedbackBatchMetadata` (agent + api_admin); database list test in manifest. |

### Issues

| Sev | Location | Finding |
|-----|----------|---------|
| **fix-now** | `AdminVectorFeedback.tsx` | Plan Stage 3 assumes columns appear via `req_dict=1`, but the page uses **hardcoded** `detailColumns` and fetches `/api/admin/vector_feedback` **without** `req_dict`. `batch_size` and `completed_at` are in API JSON but **not rendered** — UAT AC requires Admin exposure of all three metadata fields. Add columns after `batch_id` (mirror `_VECTOR_FEEDBACK_COLUMNS`) or switch detail table to `req_dict=1` pattern. |
| advisory | Plan vs AST-725 | Stage 3 "no React changes" relied on req_dict auto-display; AST-725 shipped static columns — plan assumption stale. |
| advisory | Legacy rows | Post-`ALTER`, existing rows have NULL `completed_at` / `batch_size` until re-capture — expected per Self-Assessment. |

### Recommended actions

| Priority | Action |
|----------|--------|
| **resolve** | Add `batch_size` + `completed_at` to `detailColumns` in `AdminVectorFeedback.tsx` (or req_dict-driven columns); optional frontend test assertion. |
| UAT | Re-run Susan scenario: dispatch rubric task → Admin Vector Feedback shows batch id, size, and completed timestamp on new rows. |

**Verdict:** One fix-now (Admin UI columns). Backend/capture path approve; resolve then UAT.
