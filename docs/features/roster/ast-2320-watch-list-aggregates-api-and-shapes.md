# AST-2320 — Watch List aggregates API and shapes

- **Linear:** [AST-2320](https://linear.app/astralcareermatch/issue/AST-2320)
- **Parent:** [AST-2318](https://linear.app/astralcareermatch/issue/AST-2318)
- **Publish ref:** `sub/AST-2318/AST-2320-watch-list-aggregates-api-and-shapes`

Enrich `GET /api/companies?view=watch_list` so each WATCH company carries Scan Start (first `WATCH` in `state_history`), Best Fit (narrow UI label + that job’s `state_changed_at`), total Jobs, and named count buckets JL / JD / DO / GET / LIKE / ACTIVE / SKIPPED / APPLIED with per-bucket newest dates. Replace `UI_CONFIG` `companies.list.watch_list` columns to match. Add a jobs-for-company-by-bucket route for the count modal (sibling AST-2321). Drop the Watch List retry-to-`WEBSITE_FOUND` bulk destination from the state-UI manifest. Does not own TEST_WATCH producer (AST-2319), React chrome (AST-2321), or add-company / Ignored restore (AST-2322).

**Depends on:** AST-2319 (User Testing) for `WATCH`→`IGNORE` and related transition keys the restore/ignore path already recognizes. Aggregates themselves do not call TEST_WATCH code.

## Explicit scope gate

Ticket **Scope** names exactly these files/kinds:

| File | Allowed kind |
|------|----------------|
| `src/utils/config.py` | Replace `watch_list` shape columns; new config map bucket → state set + Best Fit order; remove Watch List retry-to-`WEBSITE_FOUND` bulk destination |
| `src/data/database.py` | New or modified query function(s) for per-company counts + newest `state_changed_at` for configured state sets |
| `src/core/roster.py` | New Best Fit helper; new/modified bucket aggregate helper; new Scan Start helper |
| `src/ui/api/api_companies.py` | Modify `list_view` watch_list enrichment; new or extended jobs-for-company-by-bucket route |

No `src/ui/frontend/**` in this ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `WATCH_LIST_JOB_BUCKETS` (+ Best Fit ladder order); replace `UI_CONFIG["companies"]["list"]["watch_list"]`; remove `watch_list_ack_to_state` from `build_state_ui_manifest` `bulk_company` | utils |
| `src/data/database.py` | Extend/replace job count query: per-`company_id` counts and `MAX(state_changed_at)` by state; new list-jobs-by-company+states helper | data |
| `src/core/roster.py` | `company_watch_scan_start`, `company_watch_best_fit`, `company_watch_bucket_aggregates` (+ thin facades over new DB helpers); keep `get_company_job_state_counts` working for company detail | core |
| `src/ui/api/api_companies.py` | Enrich `view=watch_list` rows; add `GET /api/companies/<short_name>/jobs` filtered by bucket | ui |

## Stages

### Stage 1: Config — buckets, shapes, drop Watch List retry bulk key

**Done when:** `WATCH_LIST_JOB_BUCKETS` is importable and matches the locked parent map (including `SKIPPED_STATES` / `APPLIED_JOB_STATES` references, not duplicated literals). `UI_CONFIG["companies"]["list"]["watch_list"]` columns are only the named Watch List set with narrow labels (no `FAILED_` substring anywhere in those labels). `build_state_ui_manifest()["company"]["bulk_transitions"]` has `watch_list_ignore_to_state` and does **not** have `watch_list_ack_to_state`.

1. In `src/utils/config.py`, immediately after `APPLIED_JOB_STATES` / `SKIPPED_STATES` are defined (after the `JOBS_PROCESSING_EXCLUDED_STATES` assert is fine — both lists must already exist), add:

   ```python
   # AST-2320: Watch List count columns + Best Fit ladder (UI label keys → job states).
   # best_fit_order: low → high; None = counted on the list but not a Best Fit rung (SKIPPED).
   WATCH_LIST_JOB_BUCKETS = {
       "jl": {"label": "JL", "states": ["FAILED_JOBLIST"], "best_fit_order": 1},
       "jd": {"label": "JD", "states": ["FAILED_JD"], "best_fit_order": 2},
       "do": {"label": "DO", "states": ["FAILED_DO"], "best_fit_order": 3},
       "get": {"label": "GET", "states": ["PASSED_GET"], "best_fit_order": 4},
       "like": {"label": "LIKE", "states": ["PASSED_LIKE"], "best_fit_order": 5},
       "active": {
           "label": "ACTIVE",
           "states": ["RECOMMENDED", "CANDIDATE_REVIEW"],
           "best_fit_order": 6,
       },
       "skipped": {"label": "SKIPPED", "states": list(SKIPPED_STATES), "best_fit_order": None},
       "applied": {
           "label": "APPLIED",
           "states": list(APPLIED_JOB_STATES),
           "best_fit_order": 7,
       },
   }
   ```

   Assert every non-`skipped`/`applied` singleton state is in `JOB_STATES`. Assert every `states` entry for `active` / `applied` / `skipped` is in `JOB_STATES`. Assert Best Fit orders among entries with non-`None` order are unique and exactly `{1,2,3,4,5,6,7}`.

2. Replace the entire `UI_CONFIG["companies"]["list"]["watch_list"]` list with exactly these columns (keys are payload field names Stage 3 writes):

   | key | label | sortable | type / notes |
   |-----|-------|----------|----------------|
   | `company_name` | Company | True | (default str) |
   | `scan_start` | Scan Start | True | `type: "datetime"` |
   | `last_scan_at` | Last Scan | True | `type: "datetime"`, `defaultDesc: True` |
   | `best_fit_label` | Best Fit | True | str — UI label only (never `FAILED_*`) |
   | `best_fit_at` | Best Fit Date | True | `type: "datetime"` — sibling formats with the label |
   | `jobs` | Jobs | True | `type: "int"` |
   | `jl` | JL | True | `type: "int"` |
   | `jd` | JD | True | `type: "int"` |
   | `do` | DO | True | `type: "int"` |
   | `get` | GET | True | `type: "int"` |
   | `like` | LIKE | True | `type: "int"` |
   | `active` | ACTIVE | True | `type: "int"` |
   | `skipped` | SKIPPED | True | `type: "int"` |
   | `applied` | APPLIED | True | `type: "int"` |

   Do **not** put `FAILED_` in any label. Do **not** keep `short_name`, `company_website`, or `state` on this shape (detail modal still loads by row id from `idField="short_name"` on the page — sibling AST-2321 keeps `idField`; payload still includes `short_name` from `list_companies` even if it is not a shape column).

3. In `build_state_ui_manifest`, change `bulk_company` to:

   ```python
   bulk_company = {
       "inactive_list_to_state": "WEBSITE_FOUND",
       "ignored_list_to_state": "TO_WATCH",
       "watch_list_ignore_to_state": "IGNORE",
   }
   ```

   Delete `watch_list_ack_to_state`. Keep the assert that every value is in `COMPANY_STATES`.

⚠️ **Decision:** Bucket keys are lowercase (`jl`, `jd`, …) matching shape `key`s so ListPage sorts numeric ints without a parallel map. Labels are the narrow UI strings. Sibling AST-2321 formats dates from companion `*_newest_at` fields (not shape columns).

⚠️ **Decision:** Removing `watch_list_ack_to_state` is this ticket’s “remove Watch List retry-to-`WEBSITE_FOUND` bulk destination.” Sibling AST-2321 removes the Retry Scrape button; AST-2322 already rejects `WATCH`→`WEBSITE_FOUND` at `bulk_state` because that pair is not in `company_state_transitions`.

⚠️ **Decision:** `skipped` uses full `SKIPPED_STATES` even though that set overlaps `FAILED_JOBLIST` / `FAILED_JD` / `FAILED_DO`. Parent locked map lists both; AC1 checks each bucket independently against `GROUP BY state` for that bucket’s state set — cross-column double-count is correct.

### Stage 2: Database — per-company state counts + newest dates; jobs by company + states

**Done when:** For a known `company_id`, one call returns every job `state` with `count` and `newest_at` (`MAX(state_changed_at)`). A second helper returns job rows for one `company_id` filtered by an explicit state list (and optional `candidate_id`). No new entity columns are added (`astral.entity.required-metadata` — Scan Start stays derived from existing `state_history`).

1. In `src/data/database.py`, immediately after `get_company_job_counts`, add:

   ```python
   def get_company_job_state_stats(
       company_ids: List[str],
   ) -> Dict[str, Dict[str, Dict[str, Any]]]:
   ```

   Behavior:

   - If `company_ids` is empty, return `{}`.
   - Deduplicate / strip blanks; skip empties.
   - One SQL:

     ```sql
     SELECT company_id, state, COUNT(*) AS cnt, MAX(state_changed_at) AS newest_at
     FROM job
     WHERE company_id IN (…)
     GROUP BY company_id, state
     ```

   - Return shape: `{ company_id: { state: {"count": int, "newest_at": str|None}, … }, … }`.
   - Companies with zero jobs appear as `{}` only if the caller looks them up — do not invent empty outer keys unless convenient; Stage 3 treats missing as empty.

2. Keep `get_company_job_counts(short_name)` as a thin wrapper that returns `{state: count}` from `get_company_job_state_stats([short_name]).get(short_name, {})` so company detail (`get_company_job_state_counts`) stays correct without a second SQL shape.

3. Add:

   ```python
   def list_jobs_for_company(
       company_id: str,
       states: Optional[List[str]] = None,
       candidate_id: Optional[str] = None,
       order_by: str = "state_changed_at",
   ) -> List[Dict[str, Any]]:
   ```

   - Require non-blank `company_id`.
   - Filter `job.company_id = ?`.
   - If `states` is non-empty, `state IN (…)`.
   - If `candidate_id` is non-blank after strip, also `candidate_id = ?` (Watch List is candidate-scoped; pass it from the API).
   - Same sortable column allowlist / `ORDER BY … DESC NULLS LAST` pattern as `list_jobs`.
   - Return `_job_row_to_dict` rows.

⚠️ **Decision:** New `list_jobs_for_company` instead of extending `list_jobs` — `list_jobs` requires `candidate_id` and has no employer filter; Scope allows a new query function. Do not change `list_jobs` signature.

⚠️ **Decision:** No schema migration and no new company metadata column for Scan Start — parent / `astral.entity.required-metadata` keep Scan Start as a read of existing `state_history`.

### Stage 3: Core roster helpers — Scan Start, Best Fit, bucket aggregates

**Done when:** Given a company dict (with `state_history`) and optional prefetched per-state stats, helpers return Scan Start, Best Fit label+date with no `FAILED_` in the label, and a flat dict of bucket counts + `*_newest_at` + `jobs` total matching `WATCH_LIST_JOB_BUCKETS`.

1. In `src/core/roster.py`, near the existing entity-page helpers (`get_company_job_state_counts`), add:

   ```python
   def company_watch_scan_start(company: Dict[str, Any]) -> Optional[str]:
   ```

   Walk `company.get("state_history") or []` in list order (oldest→newest as stored). Return the `timestamp` string of the **first** entry whose `to_state` (stripped) equals `"WATCH"`. If none, return `None`. Do **not** fall back to `created_at` or `last_scan_at`.

2. Add:

   ```python
   def company_watch_best_fit(
       state_stats: Dict[str, Dict[str, Any]],
   ) -> Tuple[Optional[str], Optional[str]]:
   ```

   - Build a reverse map from each ladder state → `(best_fit_order, label)` using only `WATCH_LIST_JOB_BUCKETS` entries where `best_fit_order` is not `None`.
   - Among states present in `state_stats` with `count > 0`, pick the maximum `best_fit_order`.
   - Return `(label, newest_at)` for that winning state (`newest_at` from that state’s stats). If no ladder state has count > 0, return `(None, None)`.
   - Label is always the bucket `label` (`JL` / `JD` / `DO` / …), never the raw job state string.

3. Add:

   ```python
   def company_watch_bucket_aggregates(
       state_stats: Dict[str, Dict[str, Any]],
   ) -> Dict[str, Any]:
   ```

   For each key in `WATCH_LIST_JOB_BUCKETS` (iteration order of the dict):

   - `count` = sum of `state_stats[s]["count"]` for each `s` in that bucket’s `states` (missing → 0).
   - `newest_at` = max of non-null `state_stats[s]["newest_at"]` among those states (string compare is OK for the `YYYY-MM-DD HH:MM:SS` stamps this codebase writes; if all null, `None`).
   - Set out[`key`] = count (int).
   - Set out[f"{key}_newest_at"] = newest_at.

   Also set `jobs` = sum of all `count` values across every state in `state_stats` (total jobs for the company, not only bucketed states).

4. Add a small orchestrator used by the API:

   ```python
   def enrich_watch_list_company(company: Dict[str, Any], state_stats: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
   ```

   Mutate/copy: set `scan_start` from `company_watch_scan_start(company)`; set `best_fit_label` / `best_fit_at` from `company_watch_best_fit(state_stats)`; update with `company_watch_bucket_aggregates(state_stats)`; return the company dict.

5. Wire DB imports: import `get_company_job_state_stats` and `list_jobs_for_company` from `src.data.database` (same import block as `get_company_job_counts`). Export thin roster facades if the API should not import `database` (follow existing pattern — `api_companies` imports from `roster` only):

   ```python
   def get_companies_job_state_stats(company_ids: List[str]) -> Dict[str, Dict[str, Dict[str, Any]]]:
       return get_company_job_state_stats(company_ids)

   def list_company_jobs_for_bucket(company_id: str, states: List[str], candidate_id: Optional[str] = None) -> List[Dict[str, Any]]:
       return list_jobs_for_company(company_id, states=states, candidate_id=candidate_id)
   ```

⚠️ **Decision:** Best Fit date is the winning **state’s** `MAX(state_changed_at)` among jobs in that state, which matches “that job’s `state_changed_at`” when one job holds the furthest rung; if multiple jobs share the winning state, the newest timestamp in that state wins (same as the dates-toggle bucket date for that rung).

### Stage 4: API — watch_list enrichment + jobs-by-bucket route

**Done when:** `GET /api/companies?view=watch_list&candidate_id=<id>` returns each WATCH row with `scan_start`, `best_fit_label`, `best_fit_at`, `jobs`, `jl`…`applied`, and `jl_newest_at`…`applied_newest_at`. `GET /api/companies/<short_name>/jobs?bucket=active&candidate_id=<id>` returns only jobs for that company whose state is in the ACTIVE bucket set. Neither GET emits `logger.info` (`stat.logging.info.api` — idempotent GETs are not progress).

1. In `src/ui/api/api_companies.py`, import `WATCH_LIST_JOB_BUCKETS` from config and the Stage 3 roster helpers (`enrich_watch_list_company`, `get_companies_job_state_stats`, `list_company_jobs_for_bucket`).

2. In `list_view`, after loading `rows` for `view == "watch_list"` (and only that view):

   - Collect `short_names = [r["short_name"] for r in rows if r.get("short_name")]`.
   - `stats_by_company = get_companies_job_state_stats(short_names)`.
   - For each row: `enrich_watch_list_company(row, stats_by_company.get(row["short_name"], {}))` then `_flatten_for_view` as today.
   - Other views: unchanged (no aggregate enrichment).

3. Add a route **after** the named `/counts` / `/scan_history` / `/import` band and **compatible with** `/<short_name>` — use path `"/<short_name>/jobs"`:

   ```python
   @companies_bp.route("/<short_name>/jobs")
   @require_auth
   def company_jobs_by_bucket(short_name):
   ```

   Query params: `bucket` (required — one of `WATCH_LIST_JOB_BUCKETS` keys), `candidate_id` (required non-blank).

   - If `bucket` missing/unknown → `400` `{"error": "invalid bucket"}`.
   - If `candidate_id` blank → `400` `{"error": "candidate_id required"}`.
   - If `get_company(short_name)` is missing → `404`.
   - `states = list(WATCH_LIST_JOB_BUCKETS[bucket]["states"])`.
   - `rows = list_company_jobs_for_bucket(short_name, states, candidate_id=candidate_id)`.
   - Return `jsonify(rows)` — full job dicts are fine; sibling modal only needs id/title/state enough to open `JobDetailModal` (do not invent a second DTO unless a field is huge; if `job_data` is routinely large, drop `job_data` and `state_history` from each row the same way `api_jobs` uses `_LIST_ROW_DROP_KEYS` — prefer matching that drop list for list payloads).

4. Do **not** add `logger.info` on `list_view` or `company_jobs_by_bucket`.

⚠️ **Decision:** Bucket query param uses config keys (`active`, `jl`, …), not UI labels, so the modal sibling can pass the shape column key directly.

⚠️ **Decision:** `stat.logging.info.api` is cited for API work; these routes are idempotent GETs, so completion info lines are intentionally omitted per the statute’s “Idempotent GETs … are not progress” clause. Mutating company routes remain AST-2322’s logging surface.

## Estimate

Confirm Chuckles estimate: 5 — agree
