# AST-725 — Admin Vector Feedback screen (Runtime Rubric Validation)

- **Linear:** [AST-725](https://linear.app/astralcareermatch/issue/AST-725/admin-vector-feedback-screen-runtime-rubric-validation)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation)
- **Publish ref:** `origin/sub/AST-378/AST-725-admin-vector-feedback-screen`
- **Depends on:** [AST-722](https://linear.app/astralcareermatch/issue/AST-722/rubric-storage-schema-backfill-and-feedback-config-runtime-rubric) `vector_feedback` schema + `RUBRIC_FEEDBACK_CONFIG`; [AST-724](https://linear.app/astralcareermatch/issue/AST-724/runtime-vector-feedback-capture-and-lenient-parse-runtime-rubric) row writes at runtime (table may be empty until runs land)

## Summary

Read-only Admin screen for Susan to inspect **`vector_feedback`** before formal rubric-health UI on Artifacts. Two views on one page: (1) **per-vector summary** for the **active rubric** (`rubric_vector.current = 1`) scoped by **candidate + owner `task_key`** — run counts and value distributions for relevance, clarity, and verdict; (2) **detail table** of individual feedback rows with sort/filter on candidate, run `task_key`, vector code, feedback type, value, and batch/run identifiers. API lives in **`api_admin`**; React uses **`ListPage`** + **`useAdminCandidateFilter`** following Agent Timesheets patterns.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| Rubric health indicators on Artifacts rubric pages | — |
| Feedback capture / envelope parse | AST-724 |
| Mutating rubrics from verdicts | — |
| Export CSV (optional follow-up) | — |

## Run `task_key` vs rubric owner `task_key`

**AST-724** stores the **dispatch/run `task_key`** on each `vector_feedback` row (consumer grader or `craft_*` rubric task), while **`rubric_vector`** rows are keyed by **owner `task_key`** (`prefilter_company`, `grade_do`, …). Summary aggregation joins **`rubric_vector`** (`current = 1`) on **`rubric_vector_uuid`**. Detail list filters **`vector_feedback.task_key`** with the set `{owner}` plus any **craft** keys that map to that owner via **`CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`** / **`RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`**.

⚠️ **Decision:** UI **task** filter uses **owner `task_key`** labels only (six consumer graders + `prefilter_company`); backend expands to matching run keys so craft-run feedback appears without a second dropdown.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `task_keys_for_rubric_owner(owner)` helper; `NAV_CONFIG` Admin nav item | utils |
| `src/data/database.py` | `list_vector_feedback`, `aggregate_vector_feedback_by_vector` | data |
| `src/ui/api/api_admin.py` | `GET /vector_feedback`, `GET /vector_feedback/summary`; column defs + label enrichment | ui |
| `src/ui/frontend/src/pages/AdminVectorFeedback.tsx` | Summary + detail `ListPage` sections, filters, batch modal | ui |
| `src/ui/frontend/src/routes.tsx` | Route `admin/vector_feedback` | ui |
| `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | Add `FEEDBACK` to block-type tab order (AST-724 raw fallback) | ui |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**.

## Stage 1: Config helper and data-layer queries

**Done when:** `list_vector_feedback` and `aggregate_vector_feedback_by_vector` return dict rows for empty and populated DB; `task_keys_for_rubric_owner` maps owner → run keys; no API or React yet.

1. In **`src/utils/config.py`**, after **`rubric_owner_task_key`**, add:

   ```python
   def task_keys_for_rubric_owner(owner_task_key: str) -> frozenset[str]:
       """Run task_keys that write vector_feedback for this rubric owner (consumer + craft)."""
       if not owner_task_key:
           return frozenset()
       keys = {owner_task_key}
       for craft, artifact in CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.items():
           if RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get(artifact) == owner_task_key:
               keys.add(craft)
       return frozenset(keys)


   def rubric_owner_task_key_choices() -> tuple[str, ...]:
       """Sorted owner task_keys for Admin Vector Feedback task filter."""
       return tuple(sorted(RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.values()))
   ```

2. In **`src/data/database.py`**, add **`list_vector_feedback(**filters) -> List[Dict[str, Any]]`**:
   - Call **`_ensure_vector_feedback_table(conn)`** on first use.
   - Base SQL joins **`vector_feedback vf`** to **`rubric_vector rv`** on **`vf.rubric_vector_uuid = rv.rubric_vector_uuid`** (left join if orphaned FK — still show row with empty code).
   - Optional filters (omit SQL clause when arg empty):
     - **`candidate_id`** — `vf.candidate_id = ?`
     - **`owner_task_key`** — `vf.task_key IN (...)` where IN list is **`task_keys_for_rubric_owner(owner_task_key)`** (import helper from config).
     - **`task_key`** (exact run key) — `vf.task_key = ?` (when caller passes run key directly; mutually exclusive with owner expansion in API layer).
     - **`batch_id`** — `vf.batch_id = ?`
     - **`vector_code`** — `rv.code = ?` (case-insensitive: compare uppercased).
     - **`feedback_type`** — `vf.feedback_type = ?`
     - **`value`** — `vf.value = ?` (uppercase stored values).
     - **`date_from` / `date_to`** — `vf.created_at` date bounds (same string date pattern as timesheet filters: `>= date_from`, `<= date_to` end of day if needed).
   - SELECT columns: `vector_feedback_id`, `vf.candidate_id`, `vf.batch_id`, `vf.task_key`, `vf.feedback_type`, `vf.value`, `vf.agent_data_id`, `vf.created_at`, `vf.rubric_vector_uuid`, `rv.code AS vector_code`, `rv.label AS vector_label`, `rv.current AS rubric_current`.
   - Default order: **`vf.created_at DESC`**, limit none (Admin exploration v1).

3. Add **`aggregate_vector_feedback_by_vector(candidate_id: str, owner_task_key: str) -> List[Dict[str, Any]]`**:
   - Return `[]` when **`candidate_id`** or **`owner_task_key`** blank.
   - Join **`rubric_vector rv`** (`rv.current = 1`, `rv.candidate_id`, `rv.task_key = owner_task_key`) to **`vector_feedback vf`** on UUID.
   - Filter **`vf.candidate_id = ?`** and **`vf.task_key IN (...)`** via **`task_keys_for_rubric_owner(owner_task_key)`**.
   - SQL aggregate:

     ```sql
     SELECT rv.rubric_vector_uuid, rv.code, rv.label, rv.importance,
            vf.feedback_type, vf.value, COUNT(*) AS cnt,
            COUNT(DISTINCT vf.batch_id) AS batch_cnt
     FROM rubric_vector rv
     LEFT JOIN vector_feedback vf ON ...
     GROUP BY rv.rubric_vector_uuid, rv.code, rv.label, rv.importance,
              vf.feedback_type, vf.value
     ```

   - Python post-process: one dict per active rubric vector (all **`current=1`** rows for owner, even zero feedback), keys:
     - `rubric_vector_uuid`, `code`, `label`, `importance`
     - `feedback_row_count` (sum of `cnt` across types; 0 when no vf rows)
     - `batch_count` (max distinct batches across groups; 0 when none)
     - `relevance_dist`, `clarity_dist`, `verdict_dist` — each a string like **`"A:3 O:1"`** built from **`RUBRIC_FEEDBACK_CONFIG`** value order for that type (omit zero counts; empty string when no data).

4. Document **`list_vector_feedback`** / **`aggregate_vector_feedback_by_vector`** in the **`database.py` header inventory** comment block (one line each under **`vector_feedback`**).

### Self-review (Stage 1)

| Rule | Notes |
|------|--------|
| §1.1 inventory | Header updated |
| §2.1 config | Owner/run key mapping in config, not SQL literals |
| §3.3 imports | `database` imports config helper only for owner expansion |

## Stage 2: Admin API endpoints

**Done when:** `GET /api/admin/vector_feedback` and `GET /api/admin/vector_feedback/summary` return JSON under `@require_admin`; value labels enriched; `req_dict=1` returns column metadata for detail list.

1. In **`src/ui/api/api_admin.py`**, add imports: **`list_vector_feedback`**, **`aggregate_vector_feedback_by_vector`** from **`database`**; **`RUBRIC_FEEDBACK_CONFIG`**, **`rubric_owner_task_key_choices`** from **`config`**.

2. Add module-level helpers:

   ```python
   def _feedback_value_label(value: str) -> str:
       return (RUBRIC_FEEDBACK_CONFIG.get("value_labels") or {}).get(value, value)

   def _format_feedback_dist(feedback_type: str, counts: dict[str, int]) -> str:
       codes = (RUBRIC_FEEDBACK_CONFIG.get("feedback_types") or {}).get(feedback_type, {}).get("value_codes") or ()
       parts = [f"{c}:{counts.get(c, 0)}" for c in codes if counts.get(c, 0)]
       return " ".join(parts)
   ```

3. Define **`_VECTOR_FEEDBACK_COLUMNS`** (for `req_dict`):

   | key | label | type |
   |-----|-------|------|
   | `created_at` | Date | datetime |
   | `candidate_id` | Candidate | str |
   | `task_key` | Task | str |
   | `batch_id` | Batch | str |
   | `vector_code` | Vector | str |
   | `vector_label` | Label | str |
   | `feedback_type` | Type | str |
   | `value` | Value | str |
   | `value_label` | Value label | str |
   | `agent_data_id` | Agent data | str |
   | `vector_feedback_id` | Feedback ID | str |

4. Define **`_VECTOR_FEEDBACK_SUMMARY_COLUMNS`**:

   | key | label | type |
   |-----|-------|------|
   | `code` | Vector | str |
   | `label` | Label | str |
   | `importance` | Importance | int |
   | `batch_count` | Batches | int |
   | `feedback_row_count` | Feedback rows | int |
   | `relevance_dist` | Relevance | str |
   | `clarity_dist` | Clarity | str |
   | `verdict_dist` | Verdict | str |

5. Add **`_vector_feedback_filters() -> dict`** reading query args: `candidate_id`, `owner_task_key` (preferred), `task_key` (optional exact run key — if both set, `owner_task_key` wins), `batch_id`, `vector_code`, `feedback_type`, `value`, `date_from`, `date_to`.

6. **`@admin_bp.route("/vector_feedback")`** + **`@require_admin`**:
   - Build rows from **`list_vector_feedback(**_vector_feedback_filters())`**.
   - Enrich each row: **`value_label = _feedback_value_label(row["value"])`**; **`feedback_type`** display = config type label when present.
   - If **`request.args.get("req_dict")`**: return **`jsonify({"columns": _VECTOR_FEEDBACK_COLUMNS, "rows": rows})`**.
   - Else: **`jsonify(rows)`**.

7. **`@admin_bp.route("/vector_feedback/summary")`** + **`@require_admin`**:
   - Require **`candidate_id`** and **`owner_task_key`** query args; if either missing return **`jsonify({"error": "candidate_id and owner_task_key required"})`** with status **400**.
   - Rows from **`aggregate_vector_feedback_by_vector(candidate_id, owner_task_key)`**.
   - If **`req_dict`**: return columns + rows; else rows only.

8. **`@admin_bp.route("/vector_feedback/task_keys")`** + **`@require_admin`**:
   - Return **`jsonify(list(rubric_owner_task_key_choices()))`** for the task dropdown.

### Self-review (Stage 2)

| Rule | Notes |
|------|--------|
| §3.3 imports | `ui` → `data` + `utils` only |
| Auth | `@require_admin` on all three routes |

## Stage 3: React Admin page, route, and nav

**Done when:** `/admin/vector_feedback` loads for admin users; summary table appears when candidate + owner task selected; detail table lists rows with filters; empty states when no data; nav link visible under Admin.

1. Create **`src/ui/frontend/src/pages/AdminVectorFeedback.tsx`**:
   - Mirror **`AdminAgentTimesheets.tsx`** structure: **`useSearchParams`**, **`useAdminCandidateFilter`** with **memoized** `urlBacked` (AST-709 pattern), **`AdminCandidateFilterControl`**, **`ListPage`**.
   - URL filter keys: `candidate_id`, `owner_task_key`, `batch_id`, `vector_code`, `feedback_type`, `value`, `date_from`, `date_to`.
   - On mount, fetch **`/api/admin/vector_feedback/task_keys`** for owner task `<select>` options (consumer owner keys).
   - Fetch **`feedback_type`** options from existing **`/api/system/ui_config`** or hardcode `relevance|clarity|verdict` with labels from config if already exposed; if not on ui_config, use static labels matching **`RUBRIC_FEEDBACK_CONFIG`** in a small local map (read-only, three keys only).
   - **Summary section** (above detail): when **`candidate_id`** and **`owner_task_key`** both set, call **`/api/admin/vector_feedback/summary?...`**, render second **`ListPage`** titled **"Per-vector summary (active rubric)"** with **`_VECTOR_FEEDBACK_SUMMARY_COLUMNS`** keys; empty message **"No active rubric vectors or no feedback yet."**
   - **Detail section:** call **`/api/admin/vector_feedback?...`**, **`ListPage`** titled **"Vector feedback rows"**; empty message **"No vector feedback rows match filters."**
   - **`batch_id` column:** `render` → clickable link (match Execution History); opens **`BatchAgentDataModal`** for raw **`FEEDBACK`** blocks when parse failed (AST-724).
   - Default **`date_from`** to last 7 days when no batch filter (same pattern as timesheets).
   - No row selection / export in v1.

2. In **`src/ui/frontend/src/components/BatchAgentDataModal.tsx`**, extend **`BLOCK_TYPE_ORDER`**:

   ```ts
   const BLOCK_TYPE_ORDER = ["SYSTEM", "CACHE_A", "CACHE_B", "CACHE_C", "CACHE_D", "NO_CACHE", "TASK", "RESPONSE", "FEEDBACK"]
   ```

3. In **`src/ui/frontend/src/routes.tsx`**, import **`AdminVectorFeedback`** and add inside admin routes:

   ```tsx
   { path: "admin/vector_feedback", element: <AdminRoute><AdminVectorFeedback /></AdminRoute> },
   ```

   (Place after **`admin/agent_timesheets`**.)

4. In **`src/utils/config.py`** **`NAV_CONFIG`**, Admin **`items`**, add after **Agent Timesheets**:

   ```python
   {"label": "Vector Feedback", "path": "/admin/vector_feedback"},
   ```

### Self-review (Stage 3)

| Rule | Notes |
|------|--------|
| DRY | Reuse ListPage + admin filter hook |
| Scope | Read-only UI only |

## Self-Assessment

**Scope:** `Single-Component` — One new Admin page, three admin API routes, two database query helpers, and a small config/nav addition; no core agent or Artifacts changes.

**Conf:** `high` — Follows established Admin Timesheets + `list_rubric_vectors` patterns; schema and capture contract documented on AST-722/724; owner vs run `task_key` expansion is the only subtle join rule and is specified above.

**Risk:** `low` — Read-only admin paths; wrong aggregation only affects exploration UI until Susan relies on it for rubric health decisions.

## Self-review (plan vs ASTRAL_CODE_RULES)

| Section | Result |
|---------|--------|
| §1.3 DRY | Reuses ListPage, admin filters, config feedback labels |
| §2.1 config | Nav + owner-key helper in config.py |
| §2.4 batch | N/A (read-only) |
| §2.6 state machine | N/A |
| §3.3 imports | ui → data/utils; no core imports in frontend |
| §3.5 naming | `list_vector_feedback`, `aggregate_vector_feedback_by_vector` match existing `list_*` verbs |

No conflicts requiring `conf-!!-NONE`.

## Revisions

```
Revision 1 — 2026-06-18
Driven by: plan-child re-run on epic worktree; align with AST-724 FEEDBACK fallback inspect path
Changes: Added BatchAgentDataModal FEEDBACK tab order; batch_id → modal on detail table; memoized urlBacked on candidate filter (AST-709 parity).
```

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-378/AST-725-admin-vector-feedback-screen` (code tip `9aa2d71`)  
**Reviewed:** 2026-06-18  
**Note:** Three-dot diff includes sibling **AST-722/723/724** commits not yet on `origin/dev`; review scoped to AST-725 Stages 1–3.

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | `task_keys_for_rubric_owner` + `rubric_owner_task_key_choices`; `list_vector_feedback` + `aggregate_vector_feedback_by_vector`; three admin routes with `@require_admin`; `AdminVectorFeedback` summary + detail tables; memoized `urlBacked`; batch → `BatchAgentDataModal`; FEEDBACK tab order; nav + route. |
| Owner vs run keys | Detail/summary filters expand owner → consumer + craft run keys per plan; summary joins active `rubric_vector` (`current=1`). |
| §1.1 inventory | Header documents new query helpers. |
| §2.1 config | Nav item + owner/run mapping in `config.py`; dist formatting uses `RUBRIC_FEEDBACK_CONFIG` value order. |
| §3.3 layers | `api_admin` → data/utils; React via `/api/admin/*` only; no core imports in frontend. |
| Read-only scope | No mutations; exploration UI only. |
| Tests / bible | Betty manifest covers config helpers, admin API routes, page summary/detail/modal, FEEDBACK tab. |

### Issues

| Sev | Location | Finding |
|-----|----------|---------|
| advisory | `AdminVectorFeedback.tsx` | `FEEDBACK_TYPE_LABELS` / `FEEDBACK_VALUES` hardcoded in React (plan-allowed fallback); drift risk if `RUBRIC_FEEDBACK_CONFIG` changes. |
| advisory | `api_admin._enrich_vector_feedback_row` | Adds `feedback_type_label` but detail column still shows raw `feedback_type` key. |
| advisory | `AdminVectorFeedback.tsx` date inputs | Default 7-day window in `filters` useMemo not written to URL on first load — API calls work; URL bookmark slightly out of sync. |
| advisory | Diff baseline | Full AST-722–724 stack in `origin/dev...` until ftr → dev. |

### Recommended actions

| Priority | Action |
|----------|--------|
| UAT | Smoke `/admin/vector_feedback` with candidate + owner task; batch link → FEEDBACK tab on unparseable runs. |
| follow-up | Optional: show `feedback_type_label` in detail column; expose feedback enums via ui_config. |

**Verdict:** Clean — approve for `resolve-child` / UAT. No fix-now or discuss blockers.
