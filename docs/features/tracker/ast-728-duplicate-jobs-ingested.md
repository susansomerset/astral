# AST-728 — Duplicate jobs ingested

<!-- linear-archive: AST-728 archived 2026-07-22 -->

## Linear archive (AST-728)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-728/duplicate-jobs-ingested  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Duplicate job rows are appearing in the Tracker pipeline for the same employer identity (same company, job title, and employer job id). That breaks dedup expectations, inflates job counts, and wastes consult and dispatch work on rows that should have been rejected. This epic adds a durable uniqueness guarantee at the database layer, cleans up existing duplicate and decommissioned board-gaze rows, handles the post–`qualify_job_listings` collision path, and makes new inserts fail safe instead of creating another copy.

## Functional scope

* **One-time duplicate cleanup:** Identify job rows that share the same `(company, job_title, company_job_id)` triple. For each duplicate group, keep the row with the earliest `created_at` and remove the other rows in that group. Related records tied to removed `astral_job_id` values (agent_data, agent_responses, timesheets, dispatch_ledger references, etc.) are left as-is — no re-pointing or collective cleanup.
* **Board-gaze decommission cleanup:** Remove all job rows under board-gaze placeholder companies (`__board__*`). Board-gaze is being decommissioned; these records are deleted entirely rather than deduped.
* **Database uniqueness constraint:** Add a unique index on the job table across `company`, `job_title`, and `company_job_id` so the database rejects duplicate identity triples going forward.
* **Schema migration (all environments):** Apply the unique index via an idempotent lazy migration on database schema ensure — runs automatically when any process opens the SQLite database in each independent environment, same pattern as existing table and index migrations (no separate deploy-only step).
* **Insert-time duplicate tolerance:** When the data layer inserts a new job row and the unique constraint would be violated, treat the row as a duplicate bounce — do not raise through to callers; do not create a second row. Ingest callers continue to count or skip the listing as they do today for intentional dedup.
* **Post–qualify_job_listings collision handling:** When Consult delivers job metadata (after `qualify_job_listings`) that would populate the identity columns on the current row but another row already holds that `(company, job_title, company_job_id)` triple, delete the current job row by `astral_job_id` instead of updating it into a duplicate. The existing row with that triple remains canonical.
* **Preserve existing ingest dedup:** The current pre-insert duplicate check (raw listing vs existing `company_job_id` for the company) remains in place; this epic adds enforcement once structured identity fields are known, not a replacement for ingest-time listing dedup.

## Boundaries

* Does not change job state machine rules, Gazer scrape logic, or Consult parsing behavior beyond duplicate tolerance on insert and the post-metadata collision delete path.
* Does not redesign dedup to use raw HTML hashing or full `raw_job_listing` equality — identity is `(company, job_title, company_job_id)` only, per Susan's brief.
* Does not retain or migrate board-gaze jobs — cleanup removes them.
* Does not re-point or delete related records when removing duplicate or board-gaze job rows.
* Does not add UI for viewing or manually merging duplicates.
* Must not break legitimate jobs that legitimately differ on any of the three identity columns.

## Acceptance criteria

* After cleanup runs, at most one row remains per `(company, job_title, company_job_id)` triple among non–board-gaze company jobs; the survivor is the row with minimum `created_at` within each group.
* No job rows remain under `__board__*` placeholder companies after board-gaze cleanup.
* A unique index exists on `(company, job_title, company_job_id)` on the job table.
* Opening the database in a fresh environment applies the index idempotently without manual migration steps.
* Attempting to insert a job row whose triple matches an existing row does not create a second row and does not surface an unhandled error to Tracker ingest callers.
* When `qualify_job_listings` metadata would collide with an existing identity triple on another row, the current job row is deleted and no duplicate triple exists afterward.
* Re-running ingest on listings whose structured identity already exists does not increase the job count for that triple.
* Existing Tracker ingest return shape (`new`, `duplicates`, `invalid_title`) remains valid; duplicate-key rejections increment or behave as duplicate skips, not hard failures.
* No regression in Consult job initialization paths covered by existing tests.

## Dependencies and blockers

none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-728 (parent) | ftr/AST-728-duplicate-jobs-ingested |
| AST-729 | sub/AST-728/AST-729-duplicate-and-board-gaze-job-cleanup-migration |
| AST-732 | sub/AST-728/AST-732-job-unique-index-and-insert-duplicate-tolerance |
| AST-733 | sub/AST-728/AST-733-post-qualify-identity-collision-delete |

**Epic worktree:** `astral-AST-728/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Radia | review | d6a48d01-9152-40ea-a69e-15c503771138 |
| Betty | qa | 551d1694-17a3-4bd3-9d58-8679cda2fd06 |
| Hedy | engineer | 56475369-20a1-4ce4-aed4-674139503f1c |
| Betty | qa | 5c1b649c-6406-409e-abe6-da464299c025 |
| Radia | review | af35bdbb-76f5-4af2-87ba-a00d6c738401 |

---

## Original brief

Simple solution:
remove the offending records that should have been bounced (keep the min(created_at)).

Create a unique index on job across company, job_title, company_job_id

Update [database.py](<http://database.py>) to ignore duplicate errors when it tries to insert the job record.

### Comments

#### chuckles — 2026-06-18T05:05:55.241Z
@susan Open questions on AST-728:

1. When duplicate job rows are deleted during cleanup, what should happen to related records tied to the removed `astral_job_id` (e.g. agent_data, agent_responses, timesheets, dispatch_ledger references) — delete with the row, re-point to the kept job, or leave as-is?
2. Rows with NULL in one or more of `company_job_id` or `job_title` are common before Consult; should the unique index treat NULLs as distinct (allowing multiple NULL-key rows per company) or should cleanup/constraint scope exclude not-yet-initialized rows?
3. Should board-gaze jobs under placeholder companies (`__board__*`) follow the same `(company, job_title, company_job_id)` uniqueness and cleanup rules as company Gazer ingest?

— Chuckles

#### chuckles — 2026-06-18T05:05:31.906Z
@susan Open questions before dispatch:

1. When deleting duplicate rows, may related records tied to the discarded `astral_job_id` (agent responses, timesheets, state history on the loser row) be dropped with the row, or must anything be re-pointed to the surviving row?
2. Does this apply to board-sourced ingest as well as Gazer company-scan ingest, or company-scan only?
3. Are the duplicates you're seeing ones that already have populated identity columns, and should repeat raw listings at ingest (before Consult) also be in scope if the soft dedupe misses them?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
