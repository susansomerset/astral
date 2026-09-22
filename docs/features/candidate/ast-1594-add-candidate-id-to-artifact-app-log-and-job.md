<!-- linear-archive: AST-1594 archived 2026-09-22 -->

## Linear archive (AST-1594)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1594/add-candidate-id-to-artifact-app-log-and-job  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Multi-candidate data still treats candidate ownership as optional or indirect: versioned rows live in plural `artifacts` with no `candidate_id`, `job` scopes only via `company.candidate_id`, and `app_log` has no candidate column at all. This epic makes ownership first-class — rename to singular `artifact`, add required `candidate_id` on `artifact` and `job`, add nullable `candidate_id` on `app_log` (stamp when known), backfill and migrate, and **fail loudly** when an artifact/job write or scoped job read is missing `candidate_id`. Broad **implicit selected-candidate filtering across product surfaces** is explicitly **out of scope** here (separate ticket). Admin multi-candidate views are unchanged by this epic because this epic does not add surface auto-clamp.

## Functional scope

* Own artifact rows by candidate: table name is singular `artifact`; every row carries a required `candidate_id` (when `entity_type` is `candidate`, `candidate_id` equals `entity_id`; otherwise `candidate_id` is the owning candidate and remains a separate field from `entity_id`).
* Provide ticket-local migration SQL that copies existing `artifacts` rows into `artifact` with backfilled `candidate_id`; no seed of new artifact content; Susan drops the old `artifacts` table manually after cutover.
* Own job rows by candidate: add `job.candidate_id`, backfill from `company.candidate_id`, and use that column as the sole list/claim scope key (replaces the company subquery). There are no jobs without companies. Omit `candidate_id` on those helpers → fail loudly.
* Tag log rows by candidate when known: add **nullable** `app_log.candidate_id`; writers stamp it when a candidate is in scope and leave NULL for host/scheduler/auth/infrastructure paths that have none (Susan).
* **Out of scope:** automatically filtering non-admin product surfaces on the UI-selected/designated candidate across astral data tables — that is a **separate ticket** (Susan). This epic only adds columns, migration, required-`candidate_id` behavior on `artifact`/`job`, and nullable stamp-on-`app_log`.

## Component scope

* `src/data/database.py` — **modified** — rename ensure/CRUD from `artifacts` → `artifact`; add required `candidate_id` on `artifact` and `job`; add nullable `candidate_id` on `app_log`; update module header inventory; switch job list/claim/scope helpers from company subquery to `job.candidate_id`; require `candidate_id` on artifact and job scoped helpers (raise when missing); `add_log_entry` accepts optional `candidate_id`.
* `src/utils/logging.py` — **modified** — stamp `candidate_id` onto DB log entries when a designated-candidate contextvar is set (parallel to `log_batch_id`); omit / pass NULL when unset — do not fail the logging caller.
* Parent Linear Description (this ticket) — **modified** — holds the runnable `artifacts` → `artifact` migration SQL Susan executes; no new seed data file.

## Technical scope

* `database.py` / artifact schema: ensure creates or adopts table `artifact` with existing versioned columns plus required `candidate_id`; stop ensuring plural `artifacts` for new DBs; rewrite SQL and indexes to `artifact`; update header inventory.
* `database.py` / artifact writers (`save_artifact`, retire/get/list helpers): require non-empty `candidate_id` on insert (raise if missing); when `entity_type=candidate`, `candidate_id` must equal `entity_id`; keep natural key `(entity_type, entity_id, artifact_type, current)` otherwise.
* Migration SQL (in this ticket, not a seed): `CREATE TABLE artifact (…)`; `INSERT INTO artifact (…) SELECT … FROM artifacts` with `candidate_id` backfill (`entity_type=candidate` → `entity_id`; job/company entities → owning candidate via job/company); Susan drops `artifacts` after verification.
* `database.py` / job schema: ensure adds `job.candidate_id`; backfill `UPDATE job SET candidate_id = (SELECT company.candidate_id FROM company WHERE company.short_name = job.company)`; save/list/claim/count helpers that today use `company IN (SELECT … WHERE candidate_id=?)` switch to `job.candidate_id = ?` and **require** `candidate_id` (fail loudly if omitted).
* `database.py` / app_log schema: ensure adds nullable `app_log.candidate_id`; `add_log_entry` takes optional `candidate_id` (NULL allowed); `list_log_entries` can filter by it when provided.
* `logging.py`: add a designated-candidate contextvar (same shape as `log_batch_id`); flush path passes it into `add_log_entry` when set, otherwise NULL; never raise into the logging caller for a missing candidate.
* No React/UI auto-filter work in this epic. No React debug-logging requirements.

## Architectural definition

* **Patterns to reuse**
  * [`pattern.layers.import-discipline`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md>) — schema and ownership checks stay in data; utils logging keeps late-import to data.
* **New patterns proposed**
  * none for this epic. (`pattern.data.selected-candidate-scope` / surface auto-clamp belongs on the **separate** implicit-filtering ticket.)
* **Applicable statutes**
  * [`astral.standards.database-header-inventory`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>) — table rename + new columns must update the `database.py` header inventory.
  * [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — only the three tables + logging stamp path; no drive-by multi-table auto-filter.
  * [`astral.standards.no-cross-contamination`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-cross-contamination.md>) — layer boundaries while adding columns.
  * [`astral.standards.data-raises-caller-logs`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>) — data raises on missing artifact/job `candidate_id`; no logging inside data.
  * [`astral.standards.logging-via-utils`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>) + [`astral.standards.utils-data-late-import-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.utils-data-late-import-only.md>) — `app_log` writes stay on the approved late-import path.
  * [`astral.layers.import-direction`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>) — UI/core/data import direction.

## Acceptance criteria

* Fresh and migrated DBs expose table `artifact` (singular) with required `candidate_id`; product code no longer depends on table name `artifacts`.
* This ticket’s Description includes migration SQL that copies `artifacts` → `artifact` with `candidate_id` backfill; running it does not invent new artifact content; after Susan drops `artifacts`, the app runs on `artifact` alone.
* `job.candidate_id` exists, is backfilled from `company.candidate_id`, and is the sole list/claim scope key (no company subquery for candidate scope); omitting `candidate_id` on those helpers fails loudly.
* `app_log.candidate_id` exists and is **nullable**; new rows stamp a candidate when the logging context has one and store NULL otherwise; missing candidate does not fail the logging caller.
* Artifact writes always set `candidate_id`; when `entity_type=candidate`, `candidate_id == entity_id`.
* `database.py` header inventory names `artifact` (not `artifacts`) and documents `candidate_id` on `artifact`, `job`, and `app_log`.
* This epic does **not** ship non-admin selected-candidate auto-filtering across product surfaces (separate ticket).

## Open questions

none

## Proposed child tickets

#### 1!: **Artifact table rename and candidate_id - Ada**

Owns singular `artifact` schema (rename from `artifacts`), required `candidate_id`, data-layer CRUD/ensure/index/header inventory updates, and the ticket-local migration SQL Susan runs (copy only; no seed). Does not own job/app_log columns or logging contextvar (sibling #2).
**Citations:** `astral.standards.database-header-inventory`, `astral.standards.in-scope-only`, `pattern.layers.import-discipline`
**Scope:** `src/data/database.py` (artifact ensure/CRUD/inventory); parent Description migration SQL block.
**Estimate: 5**

#### 2: **job and app_log candidate_id + log stamp - Hedy**

Adds required `candidate_id` to `job` and nullable `candidate_id` to `app_log`, backfills jobs from `company.candidate_id`, switches list/claim scope to `job.candidate_id` (fail loud if omitted), and wires logging to stamp `candidate_id` when the contextvar is set (NULL when unset). Does not rename artifact (sibling #1). After #1.
**Citations:** `astral.standards.database-header-inventory`, `astral.standards.logging-via-utils`, `astral.standards.utils-data-late-import-only`, `astral.standards.data-raises-caller-logs`
**Scope:** `src/data/database.py` (job + app_log schema/helpers); `src/utils/logging.py` (candidate contextvar + nullable stamp on DB flush).
**Estimate: 5**

**New patterns:** none in this epic (surface auto-filter pattern deferred).

**Monolith check:** In-scope capabilities are schema+require on artifact/job plus nullable app_log stamp; two children split artifact rename risk from job/log ownership — intentional. Auto-filter capability removed to a separate ticket per Susan.

**Scope partition check:** Every Component/Technical item is claimed by exactly one child (#1 artifact+SQL, #2 job/app_log/logging).

---

## Original brief

1. Add candidate_id to artifact table
2. Rename artifacts table to artifact (do not seed new data, just add sql statements to this ticket to migrate from artifacts and I will drop the artifacts table manually.
3. Add candidate_id to job table if it's not already there
4. Update the surfaces that call astral data tables to automatically filter on the designated/selected candidate, which means we are implicitly filtering on the relevant candidate, instead of having to explicitly filter by candidate.
5. Exception are all admin api functions and data management . Admin pages can show multiple candidates data in the same set. No restrictions on data management and script runs from the admin pages and APIs.

## Migration SQL — artifacts → artifact (AST-1597)

Operator notes (Susan):

* Run against the live SQLite file (`astral.db`).
* Product ensure may already have **copy-adopted** into `artifact` and left plural `artifacts` in place — if so, **verify row counts** then `DROP TABLE artifacts;` only; do **not** re-run the INSERT (PK collisions / duplicates).
* If `artifact` is empty or freshly created and `artifacts` still holds the rows, run the SQL below, verify, then `DROP TABLE artifacts;` manually.
* No seed file in repo; this block does not invent new artifact content. Orphan job/company rows that cannot resolve `candidate_id` are skipped by the INSERT `WHERE` and remain only in `artifacts` for inspection before DROP.

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

### Comments

#### chuckles — 2026-09-06T03:49:54.581Z
AST-1598 REVIEW — Radia: fail-loud list_jobs breaks UI callers; stamp infra only (discuss).

#### chuckles — 2026-09-06T03:15:35.995Z
AST-1597 REVIEW — Radia discuss: orphan-rebuild asymmetry / dual-table ensure; Ada resolve next.

#### susan — 2026-09-06T02:44:16.063Z
Make candidate_id nullable in app log table.

#### chuckles — 2026-09-06T02:42:15.406Z
@susan

Examples of `app_log` paths that today have **no candidate in scope** (there is only `log_batch_id` today; it defaults to `None` outside a dispatcher batch):

1. **Scheduler / tick noise** — `dispatch.scheduler` warnings/errors around task kill, ledger write failure, and dispatch-task update failure in `src/core/dispatcher.py` (some lines run with a task’s `candidate_id` available in locals, but nothing stamps it onto the log handler).
2. **Outside any batch** — any `get_logger(…).info/warning/error` before `log_batch_id.set(...)` or after the batch ends: auth/session, nav without `candidate_id`, module import, worker boot (`scripts/start_server.py` / gunicorn), host monitor paths in `src/core/monitor.py`.
3. **Infrastructure loggers** — `src/external/playwright.py` and similar shared helpers that log without a candidate argument or contextvar.

**Remaining question:** for those paths, (a) require a candidate contextvar before any DB log emit (fail loud otherwise), (b) one agreed sentinel id for host/scheduler/auth noise, or (c) stdout-only until a candidate is known?

#### chuckles — 2026-09-06T00:14:31.628Z
@susan

1. **Auto-filter breadth:** Does “surfaces that call astral data tables” mean only `artifact` / `app_log` / `job` after they gain `candidate_id`, or should every non-admin product surface that today takes an explicit `candidate_id` (company, meteorite, dispatch_task, rubric_vector, etc.) also switch to implicit selected-candidate filtering in this same epic?
2. **Mechanism:** Should implicit scope be enforced inside the data layer via a request/session designated-candidate context when `candidate_id` is omitted, or should non-admin API routes inject the UI-selected candidate and refuse cross-candidate queries while data helpers still take an explicit `candidate_id` argument?
3. **`app_log` NULLs:** May `candidate_id` be NULL for system/dispatcher logs with no candidate in scope? If yes, do any future non-admin log views hide NULL rows, or is `app_log` remaining admin-only for reads (writes still stamp when known)?
4. **`job.candidate_id` authority:** After denormalize + backfill from `company.candidate_id`, is `job.candidate_id` the sole list/claim scope key (replacing the company subquery), and what should happen for jobs whose company is missing or has NULL `candidate_id`?
5. **`artifact.candidate_id` derivation:** On write, is `entity_type=candidate` always `entity_id`, and for `job`/`company` entities must we resolve the owning candidate and reject saves that cannot resolve — or allow NULL during migration only?

#### chuckles — 2026-09-06T00:09:55.372Z
[check-linear] Discussion — left for owning Chuckles lane (no pipeline from check)

#### susan — 2026-09-05T23:22:24.184Z
@chuckles please work on this.

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/fe4bb924acbca3c2914e2628b1f1224a/d161afd5-00d3-4d75-9a18-6d56c46682b6/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/fe4bb924acbca3c2914e2628b1f1224a/a46666e9-9f9b-4cf6-870b-0c2e71023843/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/71812882-1a6d-4eaf-98d3-98a74af5c72a/store.db` |
| Radia | review | `/home/susan/.cursor/chats/fe4bb924acbca3c2914e2628b1f1224a/f47370f0-a3e3-4cff-933d-f984594f6186/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1594 (parent) | ftr/AST-1594 |
| AST-1597 | sub/AST-1594/AST-1597-artifact-table-rename-and-candidate-id |
| AST-1598 | sub/AST-1594/AST-1598-job-and-app-log-candidate-id |

**Epic worktree:** `astral-AST-1594/` — one active sub checked out at a time.
