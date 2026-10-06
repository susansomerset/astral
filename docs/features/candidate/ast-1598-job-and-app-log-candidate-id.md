<!-- linear-archive: AST-1598 archived 2026-09-22 -->

## Linear archive (AST-1598)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1598/job-and-app-log-candidate-id-log-stamp-add-candidate-id-to-artifact  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** hedy  
**Priority / estimate:** None / 5  
**Parent:** AST-1594 — Add candidate_id to artifact, app_log, and job  
**Blocked by / blocks / related:** parent: AST-1594

### Description

## What this implements

Adds required `candidate_id` to `job` and nullable `candidate_id` to `app_log`, backfills jobs from `company.candidate_id`, switches list/claim scope to `job.candidate_id` (fail loud if omitted), and wires logging to stamp `candidate_id` when the contextvar is set (NULL when unset). Does not rename artifact (sibling #1). After #1.

## Citations

`astral.standards.database-header-inventory`, `astral.standards.logging-via-utils`, `astral.standards.utils-data-late-import-only`, `astral.standards.data-raises-caller-logs`

## Scope

`src/data/database.py` (job + app_log schema/helpers); `src/utils/logging.py` (candidate contextvar + nullable stamp on DB flush).

## Acceptance criteria

- [X] `job.candidate_id` exists, is backfilled from `company.candidate_id`, and is the sole list/claim scope key (no company subquery for candidate scope); omitting `candidate_id` on those helpers fails loudly.
- [X] `app_log.candidate_id` exists and is **nullable**; new rows stamp a candidate when the logging context has one and store NULL otherwise; missing candidate does not fail the logging caller.
- [X] `database.py` header inventory documents `candidate_id` on `job` and `app_log` (this child's slice).

## Boundaries

- [X] Does not rename `artifacts` → `artifact` (sibling #1). Does not ship non-admin selected-candidate auto-filtering (separate ticket).

## Notes for planning

After sibling #1. Logging stamp mirrors `log_batch_id` contextvar shape.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1594`, child `sub/AST-1594/<this-id>-job-and-app-log-candidate-id`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-06T03:49:52.065Z
[code-rubric] REVIEW (Commit: 8caa180d) fail-loud list breaks UI; stamp infra only

#### betty — 2026-09-06T03:46:59.107Z
`origin/sub/AST-1594/AST-1598-job-and-app-log-candidate-id` @ `8caa180d` · job cid tests ready

#### hedy — 2026-09-06T03:44:21.684Z
`origin/sub/AST-1594/AST-1598-job-and-app-log-candidate-id` @ `aff5678fac4fea8616c2fb9aed58be69b9cbf297` · job ensure guard

#### betty — 2026-09-06T03:42:59.439Z
Product bug blocking qa-child — `_ensure_job_schema` backfill (Stage 1) always runs:

```sql
UPDATE job SET candidate_id = (SELECT company.candidate_id FROM company …)
WHERE candidate_id IS NULL OR TRIM(candidate_id) = ''
```

SQLite requires table `company` to exist for that subquery. Fresh DB / any caller that hits `_ensure_job_schema` before company DDL fails with `OperationalError: no such table: company` instead of documented paths.

Repro on publish tip:
- `get_job("missing")` → OperationalError (expected None)
- `save_job("job-1", state="NEW")` → OperationalError (expected ValueError company required)
- bare `_ensure_job_schema(conn)` on empty DB → same

Holding **Code Complete**. Fix ensure (ensure company first, or skip/guard backfill when `company` missing / job empty), then re-queue Betty for test revisions (save_job ownership, list/claim fail-loud, app_log stamp). Not papering over in fixtures.

#### joan — 2026-09-06T03:34:25.397Z
[plan-rubric] PROCEED (Commit: d12ef119c0c9e92aeaa8d137698c775223152b7f) job log candidate scope

#### hedy — 2026-09-06T03:23:07.122Z
`origin/sub/AST-1594/AST-1598-job-and-app-log-candidate-id` @ `d12ef119c0c9e92aeaa8d137698c775223152b7f` · plan ready

---

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

## Resolution

**Date:** 2026-09-06  
**Publish tip before resolve:** `a89dcbf5ecb5` (Radia `docs()` intake via sync-child)  
**Radia overall:** DISCUSS — **fix-now:** none

| Finding | Disposition |
|---------|-------------|
| discuss #1 — fail-loud `list_jobs` / `count_jobs` breaks UI callers (`api_jobs` applied repair / absent query cid; `api_admin` adhoc) | **Accept as plan partition.** Stage 2 Decision + Joan APPROVED implement AC literally inside `database.py` only; UI call-site rewires out of Scope. Parent UAT / follow-up UI ticket owns unscoped admin/applied paths. No product change. |
| discuss #2 — `log_candidate_id.set(...)` not wired | **Accept as plan partition.** Stage 3 Decision: define + read only; dispatcher/core/UI set sites out of Scope. Stamp works when a later caller sets the ContextVar. No product change. |
| discuss #3 — explicit job `candidate_id` not ownership-validated | **Carry-forward.** Same resolver pattern as AST-1597 artifact discuss; database.py-only scope. Tighten only if a follow-up asks. No product change. |
| discuss #4 — fresh CREATE NOT NULL vs ALTER nullable | **Accept.** Matches plan Stage 1 Decision (no job-table rebuild). Writers enforce required ownership. No product change. |
| advisory — combined AST-1597 on publish ref | Noted for operator cutover; not this child's resolve work. |
| advisory — Betty surfer harness cid | Already on tip via merge-tests; no engineer action. |

**Product / test-tree:** unchanged this resolve pass.

## Bug: AST-1988 — Stamp batch_id and candidate_id on Railway log lines and app_log

**Mini-parent:** [AST-1987](https://linear.app/astralcareermatch/issue/AST-1987) · **Publish ref:** `sub/AST-1987/AST-1988-stamp-log-batch-candidate-ids` · **Parent ftr:** `ftr/AST-1987-railway-log-batch-candidate-ids`

This is the follow-up Stage 3's ⚠️ Decision above deferred (no `log_candidate_id.set(...)` sites). Scope is AST-1988's own `## Scope` only — nothing from AST-1598's Stages 1–2 is reopened.

### As-is

On Railway, every product log line is `{"level": …, "message": …}` — no `batch_id`, no `candidate_id` — so Log Explorer cannot filter a run by batch or candidate. In `app_log`, `batch_id` is stamped but `candidate_id` is `NULL` on every row, including candidate-owned runs like `check_job_resume`.

### To-be

Railway JSON lines emitted inside a batch carry top-level `batch_id`, and inside a candidate-owned run also `candidate_id`, alongside `level` / `message`. `app_log` rows for those runs have `candidate_id` populated. Lines outside any batch keep today's exact shape; the off-Railway `LEVEL name: message` format is unchanged.

### Repro

Formatter half (run on publish tip `cc256733f`, before fix):

```python
import logging
from src.utils.logging import _RAILWAY_JSON_FORMATTER as f, log_batch_id, log_candidate_id
log_batch_id.set("check_job_resume-0b86"); log_candidate_id.set("somerset")
r = logging.LogRecord("src.core.agent", logging.DEBUG, "x.py", 1, "hello", None, None)
print(f.format(r))
# actual:   {"level": "debug", "message": "src.core.agent: hello"}
# expected: {"level": "debug", "message": "src.core.agent: hello", "batch_id": "check_job_resume-0b86", "candidate_id": "somerset"}
```

Stamp half: `rg 'log_candidate_id\.' src/` returns only the read in `_DatabaseLogHandler.emit` (`src/utils/logging.py`) — zero `.set(...)` calls anywhere, so the flush always writes `candidate_id=None`. Susan's report on AST-1987 (`check_job_resume-0b86c465-…` rows, `candidate_id: null`) is the production shape of the same gap.

### Root cause

1. `_RailwayJsonFormatter.format` (`src/utils/logging.py`, AST-1778) builds its dict from `record.levelno` + `record.getMessage()` only; it never reads `log_batch_id` / `log_candidate_id`, which `_DatabaseLogHandler.emit` already reads.
2. Nothing in `src/` calls `log_candidate_id.set(...)`. Every batch opener that sets `log_batch_id` with a candidate id already in hand skips the candidate contextvar, and every matching teardown clears only the batch.

### Proposed change

**Pairing rule (AC 4) — applies to every core site below:** wherever this plan adds a `log_candidate_id.set(<cid>)`, it sits on the line immediately after the existing `log_batch_id.set(<batch>)`, inside the same conditional (if any). Wherever the matching teardown does `log_batch_id.set(None)`, add `log_candidate_id.set(None)` on the line immediately after. Where the teardown uses `log_batch_id.reset(token)` (meteorite), reset the candidate token in the same `if`. No candidate set without a batch set; no batch clear without a candidate clear. This mirrors the batch contextvar's existing lifecycle exactly, so the candidate cannot outlive the batch on any path where the batch does not.

⚠️ **Decision (AC 2): omit keys when unset, never emit `null`.** Lines outside a batch keep today's byte-identical shape (`{"level","message"}`), which is what AC 2 / AST-1987 To-be ("look exactly as they do today") asks for, and Railway turns every top-level key into a filterable attribute — a `null` attribute on every batch-less line is noise with no filter value. Truthiness test (`if value:`), so an empty-string id is also omitted.

**1. `src/utils/logging.py`**

a. `_RailwayJsonFormatter.format`: build the dict into a local, then add the ids only when set:

```python
payload = {"level": _RAILWAY_LEVEL.get(record.levelno, "error"), "message": msg}
batch_id = log_batch_id.get()
if batch_id:
    payload["batch_id"] = batch_id
candidate_id = log_candidate_id.get()
if candidate_id:
    payload["candidate_id"] = candidate_id
return json.dumps(payload, ensure_ascii=False)
```

Key names `batch_id` / `candidate_id` match the `app_log` column names. Class docstring: "One JSON object per line for Railway severity filters; batch_id / candidate_id added when their contextvars are set."

b. Module docstring:
- Console sentence (currently "each line is JSON with `level` + `message`"): append "plus `batch_id` / `candidate_id` when set".
- `log_candidate_id` paragraph: drop "(dispatcher/UI wiring is out of AST-1598 scope — this module only defines and reads it)". Replace with: "Set alongside `log_batch_id` at each candidate-owned batch start and cleared at the same teardown. Read by the DB handler and the Railway JSON formatter."

c. No change to `_DatabaseLogHandler`, `_CONSOLE_FORMATTER`, `_RAILWAY_LEVEL`, `log_debug`, or `_apply_console_formatter`.

**2. `src/core/dispatcher.py`** — add `log_candidate_id` to the `from src.utils.logging import …` line (L55). In `_dispatch_one_body`:

| Block | Batch set (current) | Add after it | Teardown (current, in `finally`) | Add after it |
|---|---|---|---|---|
| AST-1560 meteorite ingress transition | `log_batch_id.set(entity_batch_id)` ~L1031 | `log_candidate_id.set(ledger_cid)` | `log_batch_id.set(None)` ~L1098 | `log_candidate_id.set(None)` |
| AST-1561 BOT_BLOCKED notify | ~L1131 | `log_candidate_id.set(ledger_cid)` | ~L1200 | `log_candidate_id.set(None)` |
| AST-1134 inbox mailbox | ~L1253 | `log_candidate_id.set(ledger_cid)` | ~L1325 | `log_candidate_id.set(None)` |
| Unified entity run | ~L1379, inside `if not has_run_next_chain:` | `log_candidate_id.set(candidate_id)` inside that same `if` | ~L1505 (unconditional, after monitor alerts) | `log_candidate_id.set(None)` |

`ledger_cid` is already the normalized `str(candidate_id or "").strip() or None` (blocks 1–2) or a non-empty string (block 3). Block 4's `candidate_id` has passed the `database.get_candidate` guard. When block 4 skips the batch set (run_next chain), the agent hop opener (§3a) stamps both instead — same as the batch today.

**3. `src/core/agent.py`** — add `log_candidate_id` to the import (L85).

a. Hop batch: in `_open_run_next_hop_ledger`, after `log_batch_id.set(hop_batch_id)` (~L3097) add `log_candidate_id.set(candidate_id)` (the function's own `candidate_id` param; its only caller passes it only when truthy). In `do_task`'s nested `_close_hop_ledger`, inside `if clear_log:` after `log_batch_id.set(None)` (~L2220) add `log_candidate_id.set(None)`. That clear is already gated on `hop_ledger_batch_id` being opened and not yet closed, so it pairs 1:1 with the open.

b. Workbench batch: in `run_adhoc_workbench_test`, after `log_batch_id.set(batch_id)` (~L3183) add `log_candidate_id.set(candidate_id or None)`; in the outer `finally` after `log_batch_id.set(None)` (~L3348) add `log_candidate_id.set(None)`.

**4. `src/core/candidate.py`** — add `log_candidate_id` to the import (L104).

- `run_candidate_artifact_generation`: after `log_batch_id.set(batch_id)` (~L3914, inside `if not skip_outer_ledger:`) add `log_candidate_id.set(candidate_id)` inside the same `if`; in the outer `finally` after `log_batch_id.set(None)` (~L4124) add `log_candidate_id.set(None)`. `candidate_id` has passed the `database.get_candidate` 404 guard.
- `user-session-parse-resume` "session" sentinel batch (~L3747 / ~L3873): **no change** — no real candidate; `NULL` is correct (AC 3).

**5. `src/core/meteorite.py` — in scope: a candidate id is reachable at every `_hold_log_batch` caller.** `enrich_meteorite_land_packet` and `_classify_stage_blob` both early-return unless `cid` is non-empty; `_review_duplicate_meteorite_hook` has `cid = str(row.get("candidate_id") or "").strip()`. These are reachable outside a dispatcher batch (that is why `_hold_log_batch` exists), so without a stamp here those runs stay `NULL`.

a. Add `log_candidate_id` to the import (L70).

b. Change `_hold_log_batch(batch_id: str)` → `_hold_log_batch(batch_id: str, candidate_id: Optional[str])`:

```python
def _hold_log_batch(batch_id: str, candidate_id: Optional[str]):
    """Stamp log_batch_id + log_candidate_id only when a parent dispatch batch is not already set.

    Returns (batch_token, candidate_token) to reset, or None when the parent batch owns both.
    """
    if log_batch_id.get():
        return None
    return log_batch_id.set(batch_id), log_candidate_id.set(candidate_id or None)
```

When a parent batch is already set, the parent opener (dispatcher / agent / candidate, per §2–4) already stamped its candidate, so the hold stays a no-op for both — same rule as today.

c. Callers pass their `cid`: `_hold_log_batch(batch_id, cid)` at ~L640, ~L762, ~L2000.

d. Reset sites (~L702, ~L828, ~L2016) — the existing `if token is not None:` body becomes:

```python
log_batch_id.reset(token[0])
log_candidate_id.reset(token[1])
```

(`Optional` is already imported in meteorite.py L29.)

**Not changed:** `src/core/intake.py` (see Blast radius), any `src/ui/**`, any table/column, `log_debug` gating, the level map, Telescope / gunicorn console.

### Blast radius

- **Every Railway log line inside a batch** gains one or two top-level keys. Railway Log Explorer surfaces them as attributes (the AST-1987 sample shows `level` landing in `attributes`); no consumer parses the line by position.
- **Existing tests** in `tests/component/utils/test_debug_logging.py` (`test_railway_json_formatter_maps_levels`, `test_on_railway_emit_is_json_with_level`) assert `payload["level"]` / `payload["message"]` by key, not whole-dict equality, and run without contextvars set — expected to stay green. `tests/component/utils/test_logging_batch.py` (AST-1598 flush stamp) sets `log_candidate_id` directly — unaffected. New coverage for the added keys / set-clear pairing is Betty's call at the board (AST-1987 step 5).
- **`_hold_log_batch` signature change** — three in-file callers only; no other `src/` module and no test references `_hold_log_batch`.
- **Hop clear inside `_close_hop_ledger`** now clears the candidate too; it already cleared the batch on the same path, so any dispatcher-scoped line after a hop close already had no batch — it now consistently has neither.
- **⚠️ Known out-of-scope gap — `src/core/intake.py`.** Two more candidate-owned batch openers set `log_batch_id` with `candidate_id` in hand and are not in AST-1988's Scope: preamble validation (~L67 set / ~L135 clear, `preamble-<task_key>-…`) and `_run_intake_task` (~L577 set / ~L623 clear). After this fix their Railway lines will carry `batch_id` (formatter change) but **not** `candidate_id`, and their `app_log.candidate_id` stays `NULL`. The same two-line pairing would close it. Not added here per the explicit scope gate; Susan / fix-board decide whether to amend Scope or file a follow-up.

### What must still hold

- AST-1598 Stage 3: `app_log.candidate_id` stays nullable; unset contextvar → `NULL`; a missing candidate never raises into the logging caller (`_DatabaseLogHandler.emit` / `_flush_buffer` untouched).
- AST-1778: off-Railway console is still `LEVEL name: message`; Railway lines are still one JSON object per line with `level` (Railway vocabulary from `_RAILWAY_LEVEL`) and `message` (`"<name>: <msg>"` plus formatted exception); batch-less Railway lines are byte-identical to today.
- `log_batch_id` lifecycle is unchanged at every site — this fix only shadows it.
- `candidate.py` "session" sentinel batch rows stay `candidate_id = NULL`.
- `_hold_log_batch` still no-ops when a parent dispatch batch is set (AST-1560-era rule), now for both contextvars.
- No new tables, columns, or UI / Execution History filter changes (AST-1988 Boundaries).


### Joan fix-board — AST-1988

```text
[board-joan]  CANON: OK

context_tokens≈14000
```

### Radia review-fix — AST-1988

Review-fix for **AST-1988** (read-only). Diff base per spawn: `origin/ftr/AST-1987-railway-log-batch-candidate-ids...origin/sub/AST-1987/AST-1988-stamp-log-batch-candidate-ids`. Publish tip: `f9b447782bafaa173ce36014ac2cfc9ac786c475`.

---

```
[code-rubric]
**Ticket:** AST-1988
**Publish ref:** f9b447782bafaa173ce36014ac2cfc9ac786c475 (`origin/sub/AST-1987/AST-1988-stamp-log-batch-candidate-ids`)
**Corpus:** bd68954dc854ca80fca1fc391821dff9ff288a7a (no `docs/canon-index.md` on this ref — ids resolved from `canon/` tree at publish tip when needed)
**Overall:** CLEAN

## Canon scores

(frozen Canon Scope list empty on AST-1988 Linear description — no directive ids locked at Plan Approved; nothing to score per id)

## Column diff vs plan stage

no plan-stage scores attached (Joan `[board-joan] CANON: OK` on fix-board only; no `validate-plan` fix-mode score table for AST-1988)

## Frame diff

(none)

## Fix-specific checks

**[bug-repro]** not applicable — clean board opt-out: `qa-fix` did not run on this ticket; fix-board `[board-betty] TESTS: REVISE` coverage split to sibling **AST-1991**. Not scored as missing on this tip (per spawn prompt).

**## What must still hold — OK**

- AST-1598 Stage 3: `_DatabaseLogHandler` / `_flush_buffer` untouched; unset contextvar still → NULL; no new raise paths in logging callers.
- AST-1778: `_CONSOLE_FORMATTER` / `_apply_console_formatter` / `_RAILWAY_LEVEL` unchanged; Railway still one JSON object per line with `level` + `"<name>: <msg>"`; batch-less lines omit keys via truthiness (byte-identical to pre-fix when contextvars unset).
- `log_batch_id` lifecycle at every touched site unchanged; `log_candidate_id` mirrors set/clear pairing only.
- `candidate.py` session sentinel batch: no `log_candidate_id` sets added (only `run_candidate_artifact_generation` path stamped).
- `_hold_log_batch`: still no-ops when `log_batch_id.get()` is already set; when it stamps, returns `(batch_token, candidate_token)` and reset sites use `reset` on both.
- Boundaries: no schema/UI changes in diff.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Board test gap (sibling):** Betty’s `[board-betty] TESTS: REVISE` (Railway JSON keys + set/clear pairing / `_hold_log_batch`) is explicitly deferred to **AST-1991**; this product-only tip has no `tests/**` changes — expected for the split, not a defect of this diff.
- **Intake stamp gap (Susan-flagged out of scope):** `src/core/intake.py` preamble / `_run_intake_task` batch openers still set `log_batch_id` only — after this fix their Railway lines gain `batch_id` from the formatter but `app_log.candidate_id` stays NULL until a follow-up or scope amend. Documented in plan `### Blast radius`; not scored as a defect of this diff (per spawn prompt).
- **Canon intake note:** AST-1988 description has no frozen Canon Scope table; Joan’s board pass was registry-level `CANON: OK` without per-id rows. If Archie wants fix-lane tickets to always carry a frozen list, that is process — not a merge blocker on this tip.

## Plan fidelity

Diff matches `## Bug: AST-1988` **Proposed change** in `docs/features/candidate/ast-1598-job-and-app-log-candidate-id.md`: formatter payload + docstrings; dispatcher four blocks; agent hop + workbench; candidate artifact batch; meteorite `_hold_log_batch(batch_id, candidate_id)` + tuple reset at three callers. `rg 'log_candidate_id\.set'` on tip shows set/clear sites only in those modules (plus meteorite hold), not `intake.py`.

## Chuckles — post-review branching

| Gate | Parent shape |
|------|----------------|
| **PROCEED** (clean, C7 complete) | **Normal mini-parent** (AST-1987 with live `ftr/AST-1987-railway-log-batch-candidate-ids` — not fix-intake “ORPHANED → dev” seed) → **Review Posted** → fix-lane clean-review shortcut → **User Testing** (`resolve-child` skipped). Not straight-to-`dev` orphaned merge. |

## What's solid

Mechanical contextvar pairing follows the plan’s AC 4 rule; AC 2 “omit keys, never null” implemented in `_RailwayJsonFormatter.format` with an inline comment; unified dispatch block 4 keeps both stamps inside `if not has_run_next_chain:` while teardown clears both unconditionally (same shape as pre-fix `log_batch_id` teardown).

context_tokens≈12000
```

```
[code-rubric] PROCEED (Commit: f9b447782) Plan matches stamp pairing
```

### Resolution — AST-1988

docs-acceptance: product-only fix. The repro and set/clear pairing tests (Betty `[board-betty] TESTS: REVISE`) land on gap sibling AST-1991, stacked after this ticket on `ftr/AST-1987-railway-log-batch-candidate-ids`.

## Bug: AST-1991 — Cover Railway log batch_id/candidate_id keys and opener set/clear pairing (test gap for AST-1988)

**Mini-parent:** [AST-1987](https://linear.app/astralcareermatch/issue/AST-1987) · **Publish ref:** `sub/AST-1987/AST-1991-cover-railway-log-id-tests` · **Parent ftr:** `ftr/AST-1987-railway-log-batch-candidate-ids` · **Origin:** Betty `[board-betty] TESTS: REVISE` on AST-1988.

Tests and bible only. The product fix is AST-1988's block above, already on the ftr and on this sub after sync-child. Betty lands the tests (qa-fix lane); this block is her spec. No `src/**` edits.

### As-is

No test exercises AST-1988's repro. Nothing asserts that Railway JSON lines carry `batch_id` / `candidate_id` when the contextvars are set, or that a batch-less line is byte-identical to the pre-fix shape. Nothing asserts that the dispatcher / agent / candidate / meteorite batch openers set and clear `log_candidate_id` together with `log_batch_id`. No test references `_hold_log_batch`.

### To-be

Add-only component tests prove the formatter keys (present when set, omitted when unset or blank) and set + clear pairing at one or more openers per family, including `_hold_log_batch`'s no-op under a parent batch and its two-token reset. The repro tests fail on `origin/dev`'s product files and pass on this tip. Bible rows in `debug_logging.md` and `logging_batch.md` point at them.

### Repro

The coverage gap itself: on this tip,

```bash
rg -n "_hold_log_batch|log_candidate_id" tests/component/utils/test_debug_logging.py tests/component/core/test_dispatcher.py tests/component/core/test_agent.py tests/component/core/test_candidate.py tests/component/core/test_meteorite.py
```

returns nothing (exit 1). The Railway tests in `test_debug_logging.py` read only `payload["level"]` / `payload["message"]`. The only `log_candidate_id` test is `TestAst1598LogCandidateId` in `test_logging_batch.py`, which sets the var directly and never goes through an opener or the Railway formatter.

### Root cause

AST-1988 went product-only through fix-board. Betty's board verdict split the repro and pairing tests onto this gap child instead of qa-fix on AST-1988.

### Proposed change

**Shared rules for every test below**

- **New test functions only.** No edit to an existing test body, fixture, or assertion. New methods may be added inside an existing class when that class owns the fixture they reuse (named per test below).
- **Contextvar hygiene.** Contextvars set in a sync test body persist on the test thread. Each test that sets `log_batch_id` / `log_candidate_id` directly must take tokens and `reset` them in `finally`. Each opener test must start from both vars `None` (set via tokens at the top, reset in `finally`) so a leak from another test can't green it.
- **Red-on-dev mechanism.** Opener tests capture `(log_batch_id.get(), log_candidate_id.get())` *during* the run, from inside the mocked inner call (`_run_dispatch_loop`, `send_to_anthropic`, `run_adhoc`, `asyncio.run`, `do_task`). The in-run candidate equality is the assertion that fails pre-fix (the var is never set on `origin/dev`). The post-run `None` assertions are the leak guard (AC 4 of AST-1988).
- **Harnesses chosen are green in the current component env.** The engineer test-fix run on AST-1988 found 77 failures that already exist on the ftr base. None of the classes reused below are among them.

**1. `tests/component/utils/test_debug_logging.py` — new class `TestAst1988RailwayJsonIds`** (place after `TestAst1778RailwayConsoleTransport`; uses `logging_mod._RailwayJsonFormatter()` and `logging.LogRecord("src.core.agent", logging.INFO, __file__, 0, "hello", (), None)` like `test_railway_json_formatter_maps_levels`)

| # | Test | Setup | Assert |
|---|---|---|---|
| 1 | `test_formatter_adds_batch_and_candidate_when_set` **(bug-repro)** | `log_batch_id` = `"b-1988"`, `log_candidate_id` = `"cand-1988"` | `json.loads(fmt.format(record)) == {"level": "info", "message": "src.core.agent: hello", "batch_id": "b-1988", "candidate_id": "cand-1988"}` (whole-dict equality) |
| 2 | `test_formatter_batch_only_omits_candidate` | batch `"b-1988"`, candidate `None` | payload `== {"level": "info", "message": "src.core.agent: hello", "batch_id": "b-1988"}`; `"candidate_id" not in payload` |
| 3 | `test_formatter_unset_is_byte_identical` | both explicitly `None` | `fmt.format(record) == '{"level": "info", "message": "src.core.agent: hello"}'`: exact **string**, not parsed (AST-1988 AC 2: omit, never null) |
| 4 | `test_formatter_blank_ids_omitted` | both `""` | same exact string as #3 (truthiness decision in AST-1988 Proposed change §1) |
| 5 | `test_on_railway_emit_carries_ids` | `RAILWAY_ENVIRONMENT=1` + the `_StdoutCapture` handler pattern from `test_on_railway_emit_is_json_with_level` (same root-handler swap and `finally` restore of `_apply_console_formatter()`); both vars set; `get_logger("test.ast1988.railway").warning("soft fail")` | parsed line `== {"level": "warn", "message": "test.ast1988.railway: soft fail", "batch_id": "b-1988", "candidate_id": "cand-1988"}` |

#1, #2 and #5 are red on `origin/dev` (keys absent). #3 and #4 are green on both trees (shape regression guard).

**2. `tests/component/core/test_dispatcher.py` — new methods in `TestDispatchOne`** (reuse the `test_completes_click_dispatch` monkeypatch set: `get_candidate`, `save_dispatch_ledger`, `update_dispatch_ledger`, `compute_batch_cost`, `flush_log_buffer`, `_db_update_dispatch_task`, `_check_circuit_breaker`, registry entry)

| # | Test | `_run_dispatch_loop` mock | Assert |
|---|---|---|---|
| 6 | `test_ast1988_unified_run_stamps_candidate_with_batch_and_clears` | `AsyncMock(side_effect=…)` appending `(dispatcher_mod.log_batch_id.get(), dispatcher_mod.log_candidate_id.get())` | one capture; batch `startswith("evaluate_jd-")`; candidate `== "cand-1"`; after `_dispatch_one`: both `.get() is None` |
| 7 | `test_ast1988_failed_run_still_clears_candidate` | same capture, then `raise RuntimeError("boom")` | capture candidate `== "cand-1"`; after: both `None` (clear is in `finally`) |
| 8 | `test_ast1988_run_next_chain_leaves_candidate_unset_like_batch` | reuse `test_run_next_chain_skips_dispatch_level_ledger` setup (`_current_agent_task_run_next` → `"contemplate_job"`, task_key `anticipate_scan`) + capture | capture `== (None, None)`: dispatcher mirrors the batch, hop opener owns the stamp; after: both `None` |

**3. `tests/component/core/test_agent.py` — new methods in the existing classes that own the fixtures**

| # | Class / test | Setup | Assert |
|---|---|---|---|
| 9 | `TestAst531RunNextHopLedger::test_ast1988_hop_open_stamps_candidate_and_close_clears` | copy `test_two_hop_chain_creates_distinct_ledger_rows` setup (`hop_ledger_trackers`, `_resolve_task_prompts`, `_patch_strict_batch_anthropic`, `save_agent_data`); `send_to_anthropic` = `AsyncMock(side_effect=async fn)` that appends `(agent_mod.log_batch_id.get(), agent_mod.log_candidate_id.get())` and returns `_strict_batch_llm_ok(...)` | two captures; each candidate `== "c1"`; each batch `==` the matching `hop_ledger_trackers["saves"][i][0][0]`; after `do_task`: both `None` |
| 10 | `TestAst515AdhocWorkbenchLedger::test_ast1988_workbench_stamps_candidate_and_clears` | `ledger_trackers` fixture; `run_adhoc` = async fn capturing both vars, returns `{"success": True, "parsed_response": {"agent_payload": "ok"}, "timesheet": {}}`; `candidate_id="c1"`, `workbench_task_key="evaluate_jd"` | capture batch `startswith("adhoc-evaluate_jd-")`, candidate `== "c1"`; after: both `None` |
| 11 | `TestAst515AdhocWorkbenchLedger::test_ast1988_workbench_raise_still_clears_candidate` | `run_adhoc` captures then raises `RuntimeError("boom")`; `pytest.raises(RuntimeError)` around the call | capture candidate `== "c1"`; after: both `None` |

**4. `tests/component/core/test_candidate.py` — new methods in the existing classes**

| # | Class / test | Setup | Assert |
|---|---|---|---|
| 12 | `TestRunCandidateArtifactGeneration::test_ast1988_ui_generate_stamps_candidate_and_clears` | copy `test_returns_500_on_failed_task` patches; `candidate_mod.asyncio` = `MagicMock(run=MagicMock(side_effect=fn))`, where `fn(coro)` calls `coro.close()`, appends `(candidate_mod.log_batch_id.get(), candidate_mod.log_candidate_id.get())`, returns `{"success": False, "error": "bad"}` | capture batch `startswith("user-craft_resume_base-")`, candidate `== "somerset"`; after: both `None` |
| 13 | `TestAst986SessionResumeParse::test_ast1988_session_sentinel_batch_stays_unstamped` | `self._patch_ledger(monkeypatch)`; same `asyncio.run` capture fn (return `{"success": False, "error": "bad"}`); `run_session_resume_parse("paste me", candidate_id="somerset")` | capture batch `startswith("user-session-parse-resume-")`, candidate `is None` (AST-1988 AC 3: sentinel stays NULL even though a real candidate id is passed for the key map); after: both `None` |

#13 is green on both trees by design. It guards against a future over-stamp.

**5. `tests/component/core/test_meteorite.py` — new class `TestAst1988HoldLogBatchPairing`**

| # | Test | Setup | Assert |
|---|---|---|---|
| 14 | `test_hold_sets_both_and_returns_token_pair` **(bug-repro)** | both vars `None` | `tok = meteorite_mod._hold_log_batch("b-1988", "cand-1988")`; `isinstance(tok, tuple) and len(tok) == 2`; both `.get()` equal the inputs; then `log_batch_id.reset(tok[0])`, `log_candidate_id.reset(tok[1])` → both `None`. On `origin/dev` this raises `TypeError` (one-arg signature), so it's red |
| 15 | `test_hold_noop_under_parent_batch` | parent batch `"parent-b"`, parent candidate `"parent-c"` (tokens) | `_hold_log_batch("b-1988", "cand-1988") is None`; both vars still `"parent-b"` / `"parent-c"` |
| 16 | `test_hold_blank_candidate_stamps_none` | both `None` | `tok = _hold_log_batch("b-1988", "")`; batch `== "b-1988"`, candidate `is None`; reset both |
| 17 | `test_classify_stage_blob_stamps_and_releases` | `TestAst1879ClassifyKeyMapHandOff._run` pattern: `agent_mod.do_task` patched to an async fn capturing both vars, returning `{"success": False, "error": "stop"}`; `_classify_stage_blob("cand-1988", "blob", source_kind="email", source_id="msg-1988")` | capture batch `startswith(STAGE_METEORITE_CONFIG["task_key"] + "-stage-")`, candidate `== "cand-1988"`; after: both `None` (two-token reset path) |

#14 and #17 are red on `origin/dev`. #15 is green on both trees (existing no-op rule). #16 is red on dev (`TypeError`).

**6. `tests/component/utils/test_logging_batch.py` — no change.** The emit-buffer stamp (contextvar → `app_log.candidate_id`) is already pinned by `TestAst1598LogCandidateId`. Tests #6–#17 prove the contextvar is set during candidate-owned runs. Together they cover AST-1988 AC 3 with no duplicate DB-flush test.

**7. `docs/test-bible/utils/debug_logging.md`**

- Revise the `**Console format:**` paragraph (currently "one JSON object per line with `level` … + `message`") by appending: "plus top-level `batch_id` / `candidate_id` when those contextvars are set (omitted, never null, when unset; AST-1988). **`TestAst1988RailwayJsonIds`**."
- New section `### AST-1988 · AST-1987 (bug-repro — Railway JSON ids)` after `### AST-1778 · AST-1777`: one-paragraph summary + `| Area | Source | Component tests |` rows for #1–#5 (#1 tagged **bug-repro**). **Broken / obsolete:** none, since `TestAst1778RailwayConsoleTransport` asserts by key with vars unset. **Integration:** none.
- `## QA test manifest`: append items for `tests/component/utils/test_debug_logging.py::TestAst1988RailwayJsonIds` and add that node to the pytest command block.

**8. `docs/test-bible/utils/logging_batch.md`**

- New section `### AST-1988 · AST-1987 (bug-repro — log_candidate_id set/clear at batch openers)` after `### AST-1598 · AST-1594`. Note that it supersedes that section's "No dispatcher set sites in this child" line for current behavior, and leave the AST-1598 text as history. Table rows #6–#17 with full node ids (they live in core test files; this page is the `log_candidate_id` home). Tag #14 and #6 **bug-repro**. Add one sentence on AST-1988 AC 3 composition (§6 above). **Broken / obsolete:** none. **Integration:** none.

**Not touched:** `src/**`, `docs/features/**` (beyond this block), any other bible page, `tests/integration/**`, `src/core/intake.py` coverage (out of scope, pending Susan's scope call on AST-1988).

### Blast radius

- Add-only test functions in six files plus two bible pages. No fixture or helper changes, so existing tests are untouched. New methods inside `TestDispatchOne`, `TestAst531RunNextHopLedger`, `TestAst515AdhocWorkbenchLedger`, `TestRunCandidateArtifactGeneration` and `TestAst986SessionResumeParse` reuse those classes' fixtures read-only.
- Contextvar leakage between tests is the main hazard. The shared hygiene rule (tokens + `finally`, start from `None`) prevents both false greens and polluting later tests' `log_batch_id is None` assertions (e.g. `test_completes_click_dispatch`).
- `coro.close()` in the `asyncio.run` mocks (#12, #13) avoids "coroutine never awaited" warnings that the existing `MagicMock(run=…)` tests tolerate.
- If AST-1988's opener lines move in a later refactor, these tests pin behavior (in-run values), not line numbers.

### What must still hold

- AST-1988 AC 1–5 as written in its block above. These tests are the proof, not a re-spec.
- AST-1778: `TestAst1778RailwayConsoleTransport` and `TestConsoleFormat` stay green unchanged. Off-Railway plain format is untouched.
- AST-1598: `TestAst1598LogCandidateId` stays green unchanged. `app_log.candidate_id` stays NULL when unset.
- Engineer test-tree ban: Hedy does not commit under `tests/` or `docs/test-bible/`. Betty lands every item in §1–§8.

### Joan fix-board — AST-1991

```text
[board-joan]  CANON: OK

context_tokens≈22000
```
