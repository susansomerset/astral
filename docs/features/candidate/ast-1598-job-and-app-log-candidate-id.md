# AST-1598 — job and app_log candidate_id + log stamp

**Linear:** [AST-1598](https://linear.app/astralcareermatch/issue/AST-1598)
**Parent:** [AST-1594](https://linear.app/astralcareermatch/issue/AST-1594) — Add candidate_id to artifact, app_log, and job
**Publish ref:** `sub/AST-1594/AST-1598-job-and-app-log-candidate-id`

Add required `candidate_id` on `job` (backfill from `company.candidate_id`, sole list/claim scope key), add nullable `candidate_id` on `app_log`, and stamp it from a logging contextvar when set (NULL when unset). Does not rename `artifact` (AST-1597). Does not ship selected-candidate surface auto-filtering.

## Explicit scope gate

This ticket’s **Scope** names only:

- `src/data/database.py` (job + app_log schema/helpers)
- `src/utils/logging.py` (candidate contextvar + nullable stamp on DB flush)

Every Files Changed row and every Stage step stays inside that list. No artifact rename/CRUD, no core/UI call-site rewires, no dispatcher `log_candidate_id.set(...)` sites, no selected-candidate surface filter, no `tests/**` / bible edits.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Header inventory `job`/`app_log` + `candidate_id`; ensure/backfill `job.candidate_id`; switch candidate-scoped job SQL off company subquery; require `candidate_id` on claim/list/count; resolve/require on `save_job` insert; nullable `app_log.candidate_id` + `add_log_entry` / `list_log_entries` | data |
| `src/utils/logging.py` | Add `log_candidate_id` ContextVar (parallel to `log_batch_id`); emit/flush passes it into `add_log_entry` (NULL when unset); never raise into logging caller for missing candidate | utils |

**Do not touch:** `src/core/**`, `src/ui/**`, `src/external/**`, artifact ensure/CRUD (AST-1597), `tests/**`, `docs/test-bible/**`, parent migration SQL (artifact-only).

## Stage 1: Header inventory + `job.candidate_id` ensure/backfill

**Done when:** Module docstring inventory documents `candidate_id` on `job` and on `app_log`; `_ensure_job_schema` adds `job.candidate_id` on fresh and existing DBs and backfills from `company.candidate_id`; product code can rely on the column existing after ensure.

1. In `src/data/database.py` module docstring **Tables used (inventory)**:

   - Extend the `job — …` bullet to include `candidate_id` (required owning candidate; denormalized from `company.candidate_id`; AST-1598 / parent AST-1594). Keep existing job columns listed as today.
   - Extend the `app_log — …` bullet to include nullable `candidate_id` (stamped when logging context has a candidate; NULL otherwise; AST-1598). Keep existing app_log columns.

   Do **not** restate artifact inventory work from AST-1597 beyond leaving its existing `artifact` bullet alone.

2. In `_ensure_job_schema(conn)`:

   a. After `CREATE TABLE IF NOT EXISTS job (…)`, extend the **fresh** CREATE column list so new databases include `candidate_id TEXT NOT NULL` among the job columns (place it after `company` to match ownership adjacency). Because `CREATE TABLE IF NOT EXISTS` does not alter existing tables, existing DBs still go through (b)–(c).

   b. In the existing `PRAGMA table_info(job)` migration loop (same pattern as `job_link` / `latest_score` / `source`), if `candidate_id` is missing: `ALTER TABLE job ADD COLUMN candidate_id TEXT` then `conn.commit()`. Do **not** attempt SQLite `ADD COLUMN … NOT NULL` without a default.

   c. Immediately after ensuring the column exists, backfill blank/NULL ownership:

   ```sql
   UPDATE job
   SET candidate_id = (
     SELECT company.candidate_id FROM company
     WHERE company.short_name = job.company
   )
   WHERE candidate_id IS NULL OR TRIM(candidate_id) = ''
   ```

   Parent: there are no jobs without companies. Rows whose company has no `candidate_id` remain blank until a later write resolves them; do not invent candidates. Application writers (Stage 2) fail loud on insert when ownership cannot be resolved.

   d. Keep existing identity-index / agent_responses cleanup behavior unchanged.

⚠️ **Decision:** Application-level required `candidate_id` on write/claim (Stage 2), not a post-backfill table rebuild to `NOT NULL`. Matches existing job column migrations (`source`, `latest_score`) and avoids a risky job-table rebuild on live DBs.

## Stage 2: Job writers + scoped helpers — `job.candidate_id` only, fail loud

**Done when:** Every candidate-scoped job SQL path in `database.py` filters on `job.candidate_id = ?` (no `company IN (SELECT short_name FROM company WHERE candidate_id = ?)`); `claim_job_batch` / `list_jobs` / `count_jobs` raise `ValueError` when `candidate_id` is omitted or blank; `save_job` INSERT always stores a non-empty `candidate_id`; read dicts include `candidate_id` via existing `SELECT *` / `_job_row_to_dict`.

1. Add a private helper near the job section (public-then-helpers — place with other job helpers):

   `_resolve_job_candidate_id(conn, company: str, candidate_id: Optional[str]) -> str`

   Behavior:

   - `cid = (candidate_id or "").strip()`
   - If `cid` non-empty: return `cid`.
   - Else look up `SELECT candidate_id FROM company WHERE short_name = ?` for `company`; if missing/blank after strip, raise `ValueError("candidate_id required")`.
   - Return the looked-up stripped value.

⚠️ **Decision:** Scope is `database.py` only; existing core/UI `save_job` callers do not pass `candidate_id` today. Resolving omitted `candidate_id` from `company.candidate_id` on INSERT keeps writers green without inventing core rewires. Explicit blank after strip still fails when lookup fails — matching AC “fail loudly” on required ownership.

2. Update `save_job`:

   - Add optional keyword `candidate_id: Optional[str] = None` to the signature (with the other kwargs).
   - On **INSERT**: after company/state validation, `cid = _resolve_job_candidate_id(conn, company, candidate_id)`; include `candidate_id` in the INSERT column list and values.
   - On **UPDATE**: if `candidate_id` is not None, set `candidate_id` to `_resolve_job_candidate_id(conn, company or <existing company>, candidate_id)` only when the caller passed a non-None `candidate_id` **or** when `company` is being changed (re-resolve from the new company via `_resolve_job_candidate_id(conn, company, None)`). If neither `candidate_id` nor `company` is provided on update, leave the existing column alone.
   - Do not log in data; raise only.

3. Replace every job candidate-scope company subquery in `database.py` with `job.candidate_id = ?` (same bind parameter). Exact sites that today use `company IN (SELECT short_name FROM company WHERE candidate_id = ?)`:

   - `job_link_exists_for_candidate`
   - `text_matches_known_company_job_id_for_candidate`
   - `find_candidate_job_by_company_job_id`
   - `find_candidate_job_by_job_link`
   - `claim_job_batch` (`candidate_filter` fragment)
   - `list_jobs`
   - `count_jobs`
   - `count_jobs_below_dispatch_score_floor`
   - `count_eligible_for_dispatch_task` job+score_floor branch
   - `count_entities_in_state` job branch (update docstring: scope via `job.candidate_id`, not company subquery)

   After the switch, drop the `_ensure_company_schema` / `_ensure_company_candidate_fk` calls that exist **only** to support those job subqueries (keep them if the same function still needs company for another reason — these four find/link helpers currently ensure company solely for the subquery; once filtered on `job.candidate_id`, remove those company ensures from those helpers).

4. Fail loud on scoped list/claim/count:

   - At the start of `claim_job_batch`, if `(candidate_id or "").strip()` is empty: raise `ValueError("candidate_id required")`. Then always apply `AND candidate_id = ?` (no optional filter branch).
   - At the start of `list_jobs`, if `(candidate_id or "").strip()` is empty: raise `ValueError("candidate_id required")`. Always filter `candidate_id = ?`.
   - At the start of `count_jobs`, same raise + always filter.

⚠️ **Decision (admin / applied repair):** Parent AC says omit → fail loud on list/claim helpers. Parent also says admin multi-candidate views are unchanged by this epic. Today `src/ui/api/api_jobs.py` `_list_applied_jobs_for_candidate` calls `list_jobs(..., candidate_id=None)` for a repair pass, and `list_view` can pass query `candidate_id=None`. Those UI call sites are **out of Scope** for this child. This plan implements the AC literally in `database.py` (raise on omit). If that breaks admin/applied until a follow-up UI ticket, that is expected partition — do **not** soften list/count to Optional None inside this plan, and do **not** edit `api_jobs.py` here. If Joan/Archie require unscoped list preserved inside this child, amend Scope before build.

5. Helpers that already require a non-empty `candidate_id` (`job_link_exists_for_candidate`, `find_*`, `count_jobs_below_dispatch_score_floor`, `count_entities_in_state`, `find_meteorite_dedupe_match`) keep their existing empty-cid early returns / raises; only the SQL filter changes per step 3.

## Stage 3: Nullable `app_log.candidate_id` + logging contextvar stamp

**Done when:** `app_log` has nullable `candidate_id`; `add_log_entry` accepts optional `candidate_id` (NULL allowed); `list_log_entries` can filter by it when provided; `logging.py` defines `log_candidate_id` and stamps it on DB flush when set, otherwise NULL; missing candidate never raises into the logging caller.

1. In `_ensure_app_log_schema(conn)`:

   - Add `candidate_id TEXT` (nullable, no NOT NULL) to the fresh `CREATE TABLE app_log` column list (after `batch_id`).
   - Add the same column to the legacy TEXT→INTEGER rebuild `CREATE TABLE app_log_new` and to its `INSERT … SELECT` (select `candidate_id` when present on old table; otherwise omit / NULL).
   - For existing INTEGER-PK `app_log` missing the column: `ALTER TABLE app_log ADD COLUMN candidate_id TEXT` then commit (same idempotent PRAGMA pattern as job). Do **not** backfill historical log rows.

2. Update `add_log_entry(level, logger_name, message, batch_id=None, candidate_id=None) -> bool`:

   - INSERT includes `candidate_id` (bind the argument as-is; None → SQL NULL).
   - Keep existing try/except → False on failure (no raise into logging caller).

3. Update `list_log_entries` to accept optional `candidate_id: Optional[str] = None`. When provided (truthy after strip), add `candidate_id = ?` to the WHERE clauses. When omitted, do not filter on it.

4. In `src/utils/logging.py`:

   a. Immediately after `log_batch_id`, add:

   ```python
   log_candidate_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
       "log_candidate_id", default=None
   )
   ```

   b. Update the module docstring to state that `log_candidate_id` is optional context (parallel to `log_batch_id`); when set, DB log rows are stamped; when unset, `candidate_id` is NULL; callers that want a stamp set the contextvar (dispatcher/UI wiring is **out of this ticket’s Scope** — only define + read here).

   c. In `_DatabaseLogHandler.emit`, add `"candidate_id": log_candidate_id.get()` to the buffered entry dict alongside `batch_id`.

   d. Keep `_flush_buffer` late-import of `add_log_entry` and `add_log_entry(**e)` — kwargs now include optional `candidate_id`. Handler errors stay on stderr; never raise into the logging caller for a missing candidate.

⚠️ **Decision:** This child does **not** add `log_candidate_id.set(...)` in dispatcher/core/UI. Stamp works whenever a future (or out-of-band) caller sets the contextvar; until then, new `app_log` rows store NULL. Matches Scope (`logging.py` only) and Notes (“when the contextvar is set”).

## Estimate

Confirm Chuckles estimate: 5 — agree

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree during **build-child**, then `git push origin HEAD:sub/AST-1594/AST-1598-job-and-app-log-candidate-id`.
- Do not add files, modules, or call-site rewires outside Files Changed.
- On ambiguity, drift, or a step that cannot be executed literally: stop and comment on the **parent** Linear issue with the Stage blocked format from plan-child — do not improvise.
