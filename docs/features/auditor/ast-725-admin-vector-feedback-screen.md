# AST-725 — Admin Vector Feedback screen (Runtime Rubric Validation)

- **Linear:** [AST-725](https://linear.app/astralcareermatch/issue/AST-725/admin-vector-feedback-screen-runtime-rubric-validation)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation)
- **Publish ref:** `origin/sub/AST-378/AST-725-admin-vector-feedback-screen`
- **Depends on:** [AST-722](https://linear.app/astralcareermatch/issue/AST-722/rubric-storage-schema-backfill-and-feedback-config-runtime-rubric) `vector_feedback` schema + `RUBRIC_FEEDBACK_CONFIG`; [AST-724](https://linear.app/astralcareermatch/issue/AST-724/runtime-vector-feedback-capture-and-lenient-parse-runtime-rubric) runtime writes to `vector_feedback` and raw `FEEDBACK` agent_data blocks on `origin/ftr/AST-378-runtime-rubric-validation`

## Summary

Read-only Admin screen for Susan to inspect **`vector_feedback`** grain before a formal rubric-health UI exists. Lists parsed feedback rows (candidate, run task, vector code, feedback type, value, batch/run identifiers) with URL-backed filters and client-side sort. When candidate + rubric owner `task_key` are selected, shows a per-vector aggregation panel over **current** (`current = 1`) `rubric_vector` rows: row counts and value distributions for relevance / clarity / verdict sufficient to judge strong vs weak vectors (AC #5). Batch links open the existing **`BatchAgentDataModal`** so raw **`FEEDBACK`** blocks from unparseable runs are visible without a separate raw-SQL path (AST-724 fallback). **Does not** capture feedback at runtime, mutate rubrics, or add health indicators on Artifacts rubric pages.

## Out of scope (explicit)

| Item | Owner ticket |
|------|----------------|
| Runtime `vector_reviews` capture / parse | AST-724 |
| Rubric_vector read/write cutover | AST-723 |
| Rubric health badges on Artifacts pages | — |
| Betty test files / test-bible | Betty at Code Complete |
| CSV export | — (v1 read-only table only) |

## Rubric owner `task_key` model (aggregation filter)

Aggregation joins **`rubric_vector`** where **`task_key`** is the **consumer** owner key (same as AST-723 / backfill), not craft task keys or artifact keys:

| Owner `task_key` (filter value) | Rubric artifact (context) |
|---------------------------------|---------------------------|
| `prefilter_company` | company_prefilter |
| `qualify_job_listings` | joblist_rubric |
| `evaluate_jd` | jobdesc_rubric |
| `grade_do` | do_rubric |
| `grade_get` | get_rubric |
| `grade_like` | like_rubric |

**`vector_feedback.task_key`** stores the **run** task key (consumer or craft, e.g. `grade_get` or `craft_get_rubric`). The detail table shows both run `task_key` and joined `vector_code`; aggregation filter **`owner_task_key`** maps to **`rubric_vector.task_key`**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `list_vector_feedback`, `aggregate_vector_feedback_by_rubric` | data |
| `src/core/candidate.py` | Thin list/aggregate wrappers with `value_label` enrichment | core |
| `src/ui/api/api_admin.py` | `GET /vector_feedback`, `/vector_feedback/aggregate`, `/vector_feedback/meta` | ui |
| `src/utils/config.py` | `NAV_CONFIG` Admin nav item | utils |
| `src/ui/frontend/src/routes.tsx` | Route for Vector Feedback page | ui |
| `src/ui/frontend/src/pages/AdminVectorFeedback.tsx` | New read-only admin page | ui |
| `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | Add `FEEDBACK` to block-type tab order | ui |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**.

---

## Stage 1: Data layer — list and aggregate queries

**Done when:** `list_vector_feedback` returns joined rows (code, label) newest-first with optional filters; `aggregate_vector_feedback_by_rubric` returns one summary object per **current** rubric vector for a candidate + owner `task_key`, including vectors with zero feedback rows.

1. In **`src/data/database.py`**, in the **`# ---- rubric_vector / vector_feedback (AST-722) ----`** section (after `insert_vector_feedback_rows`), add **`list_vector_feedback`** with optional kwargs: `candidate_id`, `task_key` (filters `vector_feedback.task_key`), `owner_task_key` (filters joined `rubric_vector.task_key`), `vector_code` (exact match on uppercased `rubric_vector.code`), `feedback_type`, `value`, `batch_id`, `date_from`, `date_to` (inclusive end-of-day on `vector_feedback.created_at`, same `T23:59:59` pattern as `list_timesheets`).

2. SQL shape for list (use parameterized clauses only — no string interpolation of values):

   ```sql
   SELECT vf.*,
          rv.code AS vector_code,
          rv.label AS vector_label,
          rv.task_key AS owner_task_key
   FROM vector_feedback vf
   LEFT JOIN rubric_vector rv ON rv.rubric_vector_uuid = vf.rubric_vector_uuid
   WHERE <dynamic filters>
   ORDER BY vf.created_at DESC
   ```

3. Call **`_ensure_vector_feedback_table(conn)`** and **`_ensure_rubric_vector_table(conn)`** before query.

4. Add **`aggregate_vector_feedback_by_rubric(candidate_id: str, owner_task_key: str) -> List[Dict[str, Any]]`**:
   - Require non-empty `candidate_id` and `owner_task_key`; return `[]` when either blank (caller validates for API).
   - Query **all** `rubric_vector` rows with `candidate_id`, `task_key = owner_task_key`, `current = 1`, ordered by `importance DESC`, `code`.
   - For each vector, aggregate matching `vector_feedback` rows (any run `task_key`) grouped by `feedback_type` + `value` counts.
   - Per vector return dict:

     ```python
     {
         "code": str,
         "label": str,
         "importance": int,
         "rubric_vector_uuid": str,
         "run_count": int,          # COUNT(DISTINCT batch_id) across feedback rows
         "feedback_row_count": int, # total vector_feedback rows for this uuid
         "distributions": {
             "relevance": {"O": 2, "A": 1},  # value code → count
             "clarity": {...},
             "verdict": {...},
         },
     }
     ```

   - Vectors with no feedback: `run_count = 0`, `feedback_row_count = 0`, empty distribution dicts for the three feedback types.

5. Use **`_run_with_retry`** wrappers matching `list_dispatch_ledger` / `list_timesheets` style.

⚠️ **Decision:** Aggregation scopes to **current** rubric vectors only — Susan judges active rubric health, not retired UUID history. Historical feedback for retired vectors still appears in the detail table when not filtered away.

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §1.1 inventory | No new tables; uses existing `vector_feedback` / `rubric_vector` |
| §2.4 batch | `batch_id` exposed on list rows |
| §3.3 imports | data → utils only |

---

## Stage 2: Core wrappers — label enrichment

**Done when:** Core exposes `list_vector_feedback` and `aggregate_vector_feedback_by_rubric` with `value_label` on each row / distribution key; UI imports core only.

1. In **`src/core/candidate.py`** (rubric domain already lives here per AST-723), add:

   ```python
   def _feedback_value_label(feedback_type: str, value: str) -> str:
       labels = RUBRIC_FEEDBACK_CONFIG.get("value_labels", {})
       return labels.get(value, value)
   ```

   Import **`RUBRIC_FEEDBACK_CONFIG`** from `src.utils.config`.

2. Add **`list_vector_feedback(**kwargs) -> List[Dict[str, Any]]`**:
   - Call `database.list_vector_feedback(**kwargs)`.
   - For each row, set `value_label = _feedback_value_label(row["feedback_type"], row["value"])`.
   - Return enriched list (do not mutate DB dicts in place if shared — copy via `dict(row)`).

3. Add **`aggregate_vector_feedback_by_rubric(candidate_id: str, owner_task_key: str) -> List[Dict[str, Any]]`**:
   - Call `database.aggregate_vector_feedback_by_rubric(candidate_id, owner_task_key)`.
   - For each vector summary, add `distribution_labels` parallel to `distributions`: same nesting, values mapped through `_feedback_value_label` (e.g. `"O" → "Often"`).
   - Return enriched list.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §3.2 ui layer | API will call core, not data |
| §2.1 config | Labels from `RUBRIC_FEEDBACK_CONFIG` only |

---

## Stage 3: Admin API endpoints

**Done when:** Admin GET endpoints return JSON; `require_admin` gated; filter query params mirror data-layer kwargs; meta endpoint drives filter dropdowns without hardcoded value sets in React.

1. In **`src/ui/api/api_admin.py`**, import from **`src.core.candidate`**:

   ```python
   from src.core.candidate import list_vector_feedback, aggregate_vector_feedback_by_rubric
   ```

   Import **`RUBRIC_FEEDBACK_CONFIG`** and **`RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`** from `src.utils.config`.

2. Add filter helper **`_vector_feedback_filters() -> dict`** — same pattern as `_timesheet_filters`: pass through only present query args among `candidate_id`, `task_key`, `owner_task_key`, `vector_code`, `feedback_type`, `value`, `batch_id`, `date_from`, `date_to`.

3. Add route **`GET /vector_feedback`** (`@admin_bp.route("/vector_feedback")`, `@require_admin`):

   ```python
   def list_vector_feedback_admin():
       return jsonify(list_vector_feedback(**_vector_feedback_filters()))
   ```

4. Add route **`GET /vector_feedback/aggregate`**:
   - Read `candidate_id` and `owner_task_key` from query args (accept alias `task_key` as `owner_task_key` when `owner_task_key` absent — document in code comment only).
   - If either missing, return `400` with `{"error": "candidate_id and owner_task_key required"}`.
   - Return `jsonify(aggregate_vector_feedback_by_rubric(candidate_id, owner_task_key))`.

5. Add route **`GET /vector_feedback/meta`**:
   - Return:

     ```json
     {
       "owner_task_keys": ["prefilter_company", "qualify_job_listings", ...],
       "feedback_types": [
         {"key": "relevance", "label": "Relevance", "value_codes": ["A","O","S","R","N"]},
         ...
       ],
       "value_labels": { "O": "Often", ... }
     }
     ```

   - `owner_task_keys`: `sorted(set(RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.values()))`.
   - `feedback_types` / `value_labels`: from `RUBRIC_FEEDBACK_CONFIG` (no duplicated literals in TS).

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §2.9 auth | `@require_admin` on all three routes |
| §3.2 ui | Endpoints call core only |
| §1.4 magic numbers | Value codes from config meta endpoint |

---

## Stage 4: React admin page, nav, and FEEDBACK modal tab

**Done when:** Admin nav shows **Vector Feedback**; page loads empty state without error when table has zero rows; filters refetch list + aggregation; sort works on detail table; batch cell opens agent-data modal including FEEDBACK tab when present.

1. In **`src/utils/config.py`**, **`NAV_CONFIG`** Admin group — insert after **Execution History**:

   ```python
   {"label": "Vector Feedback", "path": "/admin/vector_feedback"},
   ```

2. In **`src/ui/frontend/src/routes.tsx`**:
   - Import `AdminVectorFeedback` from `./pages/AdminVectorFeedback`.
   - Add route (with other Admin routes):

     ```tsx
     { path: "admin/vector_feedback", element: <AdminRoute><AdminVectorFeedback /></AdminRoute> },
     ```

3. Create **`src/ui/frontend/src/pages/AdminVectorFeedback.tsx`**:

   **State / URL filters** (mirror `AdminAgentTimesheets.tsx` + `AdminPerformanceMonitor.tsx`):
   - Filter keys: `candidate_id`, `owner_task_key`, `task_key`, `vector_code`, `feedback_type`, `value`, `batch_id`, `date_from`, `date_to`.
   - `useSearchParams` + `useAdminCandidateFilter` with **memoized** `urlBacked` (AST-709 pattern).
   - Default date range when no `batch_id`: `date_from` = today − 7 days, `date_to` = today (ISO `YYYY-MM-DD`), same as Agent Timesheets.

   **Data load:**
   - On mount + filter change: `GET /api/admin/vector_feedback/meta` once (store owner task keys + feedback types).
   - `GET /api/admin/vector_feedback?...` for detail rows.
   - When `candidate_id` and `owner_task_key` both set: `GET /api/admin/vector_feedback/aggregate?candidate_id=...&owner_task_key=...`.

   **Aggregation panel** (above detail table, `className="admin-filters"` sibling section `vector-feedback-aggregate`):
   - Table columns: Code, Label, Importance, Runs (distinct batches), Rows, Relevance dist, Clarity dist, Verdict dist.
   - Format each distribution as compact text: `O×2, A×1` using `distribution_labels` when present, else raw codes.
   - Show message when candidate or rubric task not selected: *"Select candidate and rubric task to see per-vector aggregation."*
   - Empty current rubric: *"No current rubric vectors for this candidate and task."*

   **Detail table** — use **`ListPage`** with columns:

   | key | label | type |
   |-----|-------|------|
   | `created_at` | Created | datetime |
   | `candidate_id` | Candidate | str |
   | `owner_task_key` | Rubric task | str |
   | `task_key` | Run task | str |
   | `vector_code` | Code | str |
   | `vector_label` | Label | str |
   | `feedback_type` | Type | str |
   | `value` | Value | str |
   | `value_label` | Value label | str |
   | `batch_id` | Batch | str |
   | `rubric_vector_uuid` | Vector UUID | str |

   - `ListPage` title: **Vector Feedback**; `loading` / `emptyMessage` when zero rows.
   - **`batch_id` column:** `render` → clickable button/link styling consistent with Execution History batch links; `onClick` sets `agentDataBatchId` state.
   - Wire **`BatchAgentDataModal`** with `batchId={agentDataBatchId}` / `onClose={() => setAgentDataBatchId(null)}`.

   **Filter bar** (`admin-filters`):
   - Rubric task (`owner_task_key`) `<select>` from meta `owner_task_keys`.
   - Run task (`task_key`) `<select>`: options = owner keys + craft keys (`craft_prefilter_rubric`, …) from meta or hardcode craft list matching `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` keys — prefer extending meta response with `run_task_keys` = sorted union of owner + craft keys if not already in meta; **if extending meta**, add to Stage 3 step 5: `run_task_keys` sorted union of `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.values()` and `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.keys()`.
   - Vector code text input; feedback type + value `<select>` from meta; batch_id text input; date_from / date_to inputs.
   - `AdminCandidateFilterControl` for candidate (same as other admin tabs).

4. In **`src/ui/api/api_admin.py`** meta endpoint (Stage 3), add **`run_task_keys`**:

   ```python
   "run_task_keys": sorted(
       set(RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.values())
       | set(CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.keys())
   ),
   ```

   Import **`CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`**.

5. In **`src/ui/frontend/src/components/BatchAgentDataModal.tsx`**, extend **`BLOCK_TYPE_ORDER`**:

   ```ts
   const BLOCK_TYPE_ORDER = ["SYSTEM", "CACHE_A", "CACHE_B", "CACHE_C", "CACHE_D", "NO_CACHE", "TASK", "RESPONSE", "FEEDBACK"]
   ```

   (After RESPONSE — matches `BLOCK_TYPES` in config.)

⚠️ **Decision:** Reuse **`ListPage`** client sort (not server sort) — matches Agent Timesheets / list admin tables; dataset is exploration-scale, not ledger-scale.

⚠️ **Decision:** FEEDBACK fallback is **batch modal** only — no duplicate raw-block table on this page; keeps v1 minimal while satisfying AST-724 inspect path.

### Self-review (Stage 4)

| Rule | OK? |
|------|-----|
| §3.5 NAV sync | `NAV_CONFIG` + `routes.tsx` both updated |
| §3.2 ui config-driven | Filter enums from `/vector_feedback/meta` |
| DRY | Reuse `BatchAgentDataModal`, `useAdminCandidateFilter`, `ListPage` |

---

## Execution contract (build-child)

- Execute stages **1 → 2 → 3 → 4** in order; **one commit per stage** on epic worktree `astral-AST-378`.
- After each stage commit, publish to **`origin/sub/AST-378/AST-725-admin-vector-feedback-screen`** via `git push origin HEAD:sub/AST-378/AST-725-admin-vector-feedback-screen` (session `astral-AST-378`).
- Do **not** edit `tests/` or `docs/test-bible/**`.
- On ambiguity — post **`🛑 Stage N blocked`** on **AST-378** parent per plan-child format; stop.

---

## Self-Assessment

**Scope:** `Single-Component` — One read-only admin vertical slice across data list queries, thin core enrichment, three admin API routes, and a single React page plus nav wiring; no dispatcher, agent capture, or Artifacts rubric UI changes.

**Conf:** `high` — Mirrors established admin list patterns (Execution History, Agent Timesheets), tables and config already exist from AST-722/724, and acceptance criteria are concrete inspect/aggregate requirements.

**Risk:** `low` — Read-only admin paths; mistakes affect Susan's exploration UI only and do not alter runtime grading, capture, or rubric authority.

---

## Self-review vs ASTRAL_CODE_RULES

| Section | Assessment |
|---------|------------|
| §1.3 DRY | Reuses `ListPage`, `BatchAgentDataModal`, `useAdminCandidateFilter`; value labels from `RUBRIC_FEEDBACK_CONFIG` |
| §2.1 config | Nav item in `NAV_CONFIG`; meta endpoint serves owner/run task keys and feedback enums |
| §2.4 batch | `batch_id` on every list row; aggregation counts distinct batches per vector |
| §2.6 state machine | No entity state transitions |
| §3.3 imports | ui → core → data; no ui → data for feedback list |
| §3.5 naming | `AdminVectorFeedback.tsx`, route `/admin/vector_feedback`, API `/api/admin/vector_feedback` |

No unresolved conflicts — plan is implementable as written.
