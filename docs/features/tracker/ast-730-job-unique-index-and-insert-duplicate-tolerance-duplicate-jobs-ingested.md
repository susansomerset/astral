# AST-730 — Job unique index and insert duplicate tolerance (Duplicate jobs ingested)

<!-- linear-archive: AST-730 archived 2026-06-23 -->

## Linear archive (AST-730)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-730/job-unique-index-and-insert-duplicate-tolerance-duplicate-jobs  
**Status at archive:** Canceled  
**Project:** Astral Tracker  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-728 — Duplicate jobs ingested  
**Blocked by / blocks / related:** parent: AST-728; blocks: AST-731

### Description

## What this implements

Add a durable database uniqueness guarantee on job identity and make inserts fail safe. Create a unique index on `(company, job_title, company_job_id)`. Apply via idempotent lazy migration on database schema ensure (runs when any process opens the SQLite DB). When inserting a new job row would violate the unique constraint, treat as duplicate bounce — no unhandled error to callers.

## Acceptance criteria

* A unique index exists on `(company, job_title, company_job_id)` on the job table.
* Opening the database in a fresh environment applies the index idempotently without manual migration steps.
* Attempting to insert a job row whose triple matches an existing row does not create a second row and does not surface an unhandled error to Tracker ingest callers.
* Re-running ingest on listings whose structured identity already exists does not increase the job count for that triple.
* Existing Tracker ingest return shape (`new`, `duplicates`, `invalid_title`) remains valid; duplicate-key rejections increment or behave as duplicate skips, not hard failures.

## Boundaries

* Does not implement qualify_job_listings collision delete — sibling ticket.
* Does not run one-time duplicate cleanup — sibling ticket (must land cleanup before index on DBs that still have dupes).
* Does not change job state machine or Gazer scrape logic.

## Notes for planning

* Data layer only for insert tolerance; preserve existing `raw_job_listing_is_duplicate` ingest check in tracker.
* Follow existing `_ensure_*_schema` migration patterns in [database.py](<http://database.py>).

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/duplicate-jobs-ingested`, child `sub/AST-728/AST-730-job-unique-index-insert-tolerance`. Created at **dispatch-parent**.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
