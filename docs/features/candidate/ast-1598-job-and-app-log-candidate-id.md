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

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1598
**Overall:** APPROVED
**Publish ref:** `sub/AST-1594/AST-1598-job-and-app-log-candidate-id` @ `d12ef119c0c9e92aeaa8d137698c775223152b7f`

## Traceability
AC1→Stages 1–2 (ensure/backfill `job.candidate_id`, subquery→`job.candidate_id`, fail loud on claim/list/count omit, `save_job` INSERT ownership); AC2→Stage 3 (nullable `app_log.candidate_id`, `add_log_entry`/`list_log_entries`, `log_candidate_id` ContextVar + flush stamp, no raise into caller); AC3→Stage 1 (header inventory `job`/`app_log` bullets)

## Findings

### discuss
- **Location:** Stage 2 step 4 — `list_jobs` / `count_jobs` fail loud on omit  
  **Finding:** Plan implements child AC literally (raise when `candidate_id` blank). On publish ref, `api_jobs.py` calls `list_jobs(..., candidate_id=None)` for applied meteorite repair (line 109) and `list_view` can pass absent query `candidate_id` for admin list endpoints — those paths will raise after build unless a follow-up UI ticket passes explicit scope. Parent epic also says admin multi-candidate views are “unchanged” (no auto-clamp); this is a deliberate partition tradeoff the plan surfaces.  
  **Recommendation:** Susan confirms accepting admin repair/list breakage until out-of-scope UI wiring lands; if unscoped admin list must survive in this child, amend Scope + Stage 2 before build (plan already flags this gate).

- **Location:** Stage 3 — `log_candidate_id.set(...)` omitted  
  **Finding:** ContextVar + flush wiring satisfies infra AC (“stamp when context has one; NULL otherwise”), but no dispatcher/core/UI set sites are in Scope — operational stamping deferred until a caller sets the var (parallel to `log_batch_id`, which dispatcher sets today).  
  **Recommendation:** Accept as child partition unless Susan wants dispatcher set wired in this ticket (would expand Scope beyond Files Changed).

### acceptable
- **Location:** Stage 2 — `_resolve_job_candidate_id` on `save_job` INSERT  
  **Finding:** Omitted `candidate_id` resolves from `company.candidate_id` rather than raising; child AC “fail loud on omit” targets scoped list/claim/count helpers, not INSERT resolution — keeps core call sites green within database.py-only scope.  
  **Recommendation:** None — matches AST-1597 artifact resolver pattern and child Boundaries.

**Considered (in-session):** Universal orch.* — conform. Scoped: `astral.standards.database-header-inventory`, `astral.standards.logging-via-utils`, `astral.standards.utils-data-late-import-only`, `astral.standards.data-raises-caller-logs`, `astral.standards.in-scope-only`, `astral.layers.import-direction`, `astral.standards.public-then-helpers`, `astral.standards.no-cross-contamination` — conform. Remaining scoped astral.* excluded (no layer/path intersection with `database.py` + `logging.py` modify set).

context_tokens≈52000

## Build complete

**Publish ref:** `sub/AST-1594/AST-1598-job-and-app-log-candidate-id` @ `12aa4d288ba1f5c4e4b76c73771b33bef62c6249`

Stages 1–3 delivered: job inventory + `candidate_id` ensure/backfill; scoped helpers on `job.candidate_id` with fail-loud claim/list/count and `save_job` resolve; nullable `app_log.candidate_id` + `log_candidate_id` ContextVar stamp on flush.


## Radia review

# Radia review — AST-1598

**Publish ref:** `origin/sub/AST-1594/AST-1598-job-and-app-log-candidate-id` @ `8caa180d80a99b42b7fd8d0de107b58221e6c7a2`  
**Baseline:** `origin/dev`  
**AST-1598 engineer commits:** `2b275c7d` → `aff5678f` (`database.py` + `logging.py` only)  
**Tests tip (Betty merge):** `8caa180d` merges `93c59c33`  
**Note:** Three-dot diff vs `origin/dev` also includes resolved sibling **AST-1597** (artifact rename + Radia DISCUSS carry-forward). AST-1598 plan adherence scored on AST-1598 commits + cumulative integration shape.

---

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1598
**Publish ref:** origin/sub/AST-1594/AST-1598-job-and-app-log-candidate-id @ 8caa180d80a99b42b7fd8d0de107b58221e6c7a2
**Overall:** DISCUSS
```

## Statutes checked

Diff change set: layers `data`, `utils`, `docs`; paths `src/data/database.py`, `src/utils/logging.py`, plan/bible/tests (Betty); change_types `add`/`modify`.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent paths |
| astral.agent.do-task-delegation | scoped | not-applicable | no dispatch/agent paths |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch-id format changes |
| astral.batch.batch-id-format | scoped | not-applicable | no batch format changes |
| astral.batch.claim-process-release | scoped | not-applicable | claim helper signature unchanged; still release elsewhere |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no entity-agent-responses paths |
| astral.config.config-source-of-truth | scoped | not-applicable | no config.py |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env paths |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug dir paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spikes |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run-next changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | `docs/features/candidate/ast-1598-…md` present |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | AST-1598 code commits limited to `database.py` + `logging.py` |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | data/utils only in engineer commits |
| astral.layers.import-direction | scoped | conforms | utils→data late import unchanged; no new cross-layer imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no ui src changes |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no render/consult |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API route changes |
| astral.seed.* (6 statutes) | scoped | not-applicable | no seed paths |
| astral.standards.data-raises-caller-logs | scoped | conforms | job paths raise `ValueError`; `add_log_entry` swallows → False |
| astral.standards.database-header-inventory | scoped | conforms | `job` + `app_log` inventory bullets updated |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug= contract surfaces |
| astral.standards.dry-and-focused-functions | scoped | conforms | `_resolve_job_candidate_id` shared; subquery→column filter deduped |
| astral.standards.in-scope-only | scoped | conforms | AST-1598 engineer footprint matches plan Files Changed; 1597 artifact in branch is sibling resolve, not 1598 smuggle |
| astral.standards.logging-via-utils | scoped | conforms | ContextVar + handler emit in `logging.py`; no stray `getLogger` |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain column names only |
| astral.standards.no-cross-contamination | scoped | conforms | job/app_log changes isolated from artifact CRUD logic |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | no new config vocab |
| astral.standards.public-then-helpers | scoped | conforms | `_resolve_job_candidate_id` private; public job/log APIs extended |
| astral.standards.utils-data-late-import-only | scoped | conforms | `add_log_entry` import stays inside `_flush_buffer` |
| astral.state.* (3 statutes) | scoped | not-applicable | no state-machine logic |
| astral.ui.* (3 statutes) | scoped | not-applicable | no ui src |
| orch.git.betty-merge-tests-one-sha | universal | conforms | single `merge-tests(AST-1598)` @ `8caa180d` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`test`/`docs`/`merge-tests`/`resolve` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | sub publish topology |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1594/AST-1598-…` |
| orch.git.merge-on-checkout | universal | conforms | sync/merge commits present |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops |
| orch.git.no-dev-agent-branches | universal | conforms | no agent branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1594 epic pattern |
| orch.git.three-permanent-branches | universal | conforms | review vs origin/dev |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | admin/UI breakage is plan-flagged partition — Susan gate |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 implemented per plan literal |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns test/bible revisions |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Hedy per spawn |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer stayed out of test tree |

**Straggler (C4):** Joan verdict attached. No excluded statute rescored as `violates`. `astral.git.engineer-test-tree-ban` in-scope on combined ref (test paths) but **conforms** (Betty lane).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan has no **Patterns to reuse** block |

## Plan adherence

- **Stage 1:** `job` inventory + `_ensure_job_schema` adds/backfills `candidate_id`; `app_log` inventory bullet added. Backfill guarded when `company` table absent (`aff5678f`) — sensible test-harness fix beyond bare plan text.
- **Stage 2:** All listed company-subquery sites switched to `job.candidate_id = ?`; redundant `_ensure_company_*` removed from four find/link helpers; `claim_job_batch` / `list_jobs` / `count_jobs` fail loud on blank `candidate_id`; `save_job` INSERT resolves via `_resolve_job_candidate_id`; UPDATE re-resolves on `company` or explicit `candidate_id` change. SQL bind ordering on `claim_job_batch` verified.
- **Stage 3:** Nullable `app_log.candidate_id` on fresh CREATE, legacy rebuild, and ALTER path; `add_log_entry` / `list_log_entries` extended; `log_candidate_id` ContextVar + emit buffer + `add_log_entry(**e)` flush — no raise into logging caller.
- **Scope gate:** Engineer commits touch only `database.py` + `logging.py`. No dispatcher/core/UI `log_candidate_id.set(...)` (plan-excluded). No selected-candidate surface filter.
- **Sibling integration:** Branch includes resolved AST-1597 artifact work (expected `blockedBy` chain on shared epic ref).
- **Estimate (5):** Still fits.

## Frame diff

```
src/data/database.py     | +332 net   job/app_log candidate_id + 1597 artifact (sibling)
src/utils/logging.py     | +10        log_candidate_id ContextVar + emit stamp
docs/features/…          | plan + Joan + build + 1597 Radia doc carry-forward
docs/test-bible/…        | AST-1598 manifests (Betty)
tests/component/…        | job/app_log/logging + confest/surfer fixes (Betty)
```

## Findings

### discuss

1. **Fail-loud `list_jobs` / `count_jobs` breaks out-of-scope UI callers (plan-known)**  
   **Location:** `database.list_jobs` / `database.count_jobs`; callers unchanged in `src/ui/`  
   **Issue:** Plan implements AC literally — blank `candidate_id` → `ValueError`. After deploy, these paths will raise unless callers pass scope:
   - `api_jobs.py:109` — applied meteorite repair loop: `list_jobs(..., candidate_id=None)`
   - `api_jobs.py:list_view` — passes query `candidate_id` through; absent param → `None` on **all** views (`in_review`, `skipped`, `recommended`, not only `applied`)
   - `api_admin.py:1360` — `list_jobs(..., candidate_id=candidate_id or None)` when admin adhoc query omits candidate  
   Plan + Joan flag this as deliberate partition (admin/applied repair deferred). **Susan must confirm accepting UT/runtime breakage until a UI follow-up** — not a code-vs-plan defect.

2. **`log_candidate_id.set(...)` not wired anywhere (plan-known)**  
   **Location:** `src/utils/logging.py` only defines/reads ContextVar  
   **Issue:** Infra satisfies AC (stamp when set, NULL otherwise), but operational stamping waits for dispatcher/core/UI wiring — out of Scope. Joan carry-forward: accept partition or expand Scope before expecting stamped rows in production logs.

3. **Explicit `candidate_id` on job INSERT not validated against `company.candidate_id`**  
   **Location:** `_resolve_job_candidate_id` — non-empty explicit `cid` returned without lookup  
   **Issue:** Same resolver pattern as AST-1597 artifact discuss; keeps core call sites green within database.py-only scope. Wrong explicit ownership could persist until a later ticket tightens validation.

4. **Application-level NOT NULL vs migration nullable column (plan-known)**  
   **Location:** `_ensure_job_schema` — fresh CREATE `candidate_id TEXT NOT NULL`; existing DBs get nullable `ALTER` + backfill  
   **Issue:** Matches plan Stage 1 decision (no job-table rebuild). Rows with unresolvable company ownership can remain blank until a writer resolves or fails.

### advisory

- **Combined publish ref:** Reviewers testing UT on this branch get AST-1597 artifact behavior too; AST-1597 Radia DISCUSS items (orphan rebuild asymmetry) remain on branch — not re-scored here but relevant for operator cutover.
- **Betty harness fixes:** `test_surfer.py` now passes `candidate_id` to `claim_job_batch` and seeds company — required by fail-loud claim; good regression signal for dispatch-shaped callers.

### fix-now

*(none)*

## What's solid

- Header inventory documents `job.candidate_id` and nullable `app_log.candidate_id`.
- Subquery elimination is complete on all plan-listed sites; company ensures removed where only subquery-motivated.
- `save_job` INSERT column/bind counts match; UPDATE re-resolve logic matches Stage 2 step 2.
- `app_log` migration paths handle legacy TEXT PK rebuild and incremental ALTER without backfilling history.
- `log_candidate_id` wired through emit → flush → `add_log_entry(**e)` with existing stderr fallback on handler failure.
- Company-absent backfill guard prevents ensure crash on fresh/in-memory DBs before company DDL.
- Betty component coverage for job scope, app_log stamp/filter, and ContextVar flush is aligned with plan AC.

## Recommended actions (downstream — not Radia)

1. Chuckles: append artifact; post slim upshot; → **Review Posted**.
2. **Susan:** Confirm discuss #1 acceptable for UT (applied repair + admin list/adhoc breakage) or amend Scope/UI ticket before UT.
3. If Susan wants stamped logs in staging before dispatcher wiring, spawn follow-up for `log_candidate_id.set(...)` at dispatch entry (out of AST-1598 Scope).

context_tokens≈62000
