# AST-731 — Qualify job list metadata collision delete (Duplicate jobs ingested)

<!-- linear-archive: AST-731 archived 2026-06-23 -->

## Linear archive (AST-731)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-731/qualify-job-list-metadata-collision-delete-duplicate-jobs-ingested  
**Status at archive:** Canceled  
**Project:** Astral Tracker  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-728 — Duplicate jobs ingested  
**Blocked by / blocks / related:** parent: AST-728

### Description

## What this implements

When Consult delivers job metadata after `qualify_job_listings` that would populate identity columns on the current row but another row already holds the same `(company, job_title, company_job_id)` triple, delete the current job row by `astral_job_id` instead of updating into a duplicate. The existing row with that triple remains canonical.

## Acceptance criteria

* When `qualify_job_listings` metadata would collide with an existing identity triple on another row, the current job row is deleted and no duplicate triple exists afterward.
* No regression in Consult job initialization paths covered by existing tests.

## Boundaries

* Does not add the unique index or insert tolerance — sibling ticket (coordinate with that work).
* Does not run one-time cleanup migration — sibling ticket.
* Does not re-point orphaned related records when deleting the colliding row.

## Notes for planning

* Enforcement at `initialize_job` / qualify_job_listings outcome path in core (tracker/consult).
* Delete the *new* colliding row, keep the pre-existing canonical row per parent definition.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/duplicate-jobs-ingested`, child `sub/AST-728/AST-731-qualify-joblist-collision-delete`. Created at **dispatch-parent**.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
