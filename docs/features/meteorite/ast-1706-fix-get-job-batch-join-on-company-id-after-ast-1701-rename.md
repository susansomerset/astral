# AST-1706 — fix: get_job_batch JOIN on company_id after AST-1701 rename

<!-- linear-archive: AST-1706 archived 2026-09-24 -->

## Linear archive (AST-1706)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1706/fix-get-job-batch-join-on-company-id-after-ast-1701-rename  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1705 — qualify_meteorite is failing  
**Blocked by / blocks / related:** parent: AST-1705

### Description

## Scope

### Component scope

* `src/data/database.py` — **modified** — `get_job_batch` SQL still joins on retired `j.company`; must use `j.company_id` after the AST-1701 table rebuild. No new files expected.

### Technical scope

* `src/data/database.py` / `get_job_batch` — **modified function** — one-line JOIN column rename (`company` → `company_id`) so batch load matches the live job schema; without it every job-batch dispatch (including `qualify_meteorite`) dies before consult runs.

## Context

Orphaned bug AST-1705 — `qualify_meteorite` fails with `no such column: j.company` because `get_job_batch` still joins on retired `job.company` after AST-1701 renamed it to `company_id`. No ancestor checklist box was checked; plan from this Scope + parent Description.

### Comments

#### radia — 2026-09-17T21:03:51.660Z
[code-rubric] PROCEED (Commit: c567462) one-line JOIN fix

Overall: CLEAN. Fix-specific: no [bug-repro] (board TESTS OK); ## What must still hold OK. Canon: patt.entity.batch-criteria X (inherited mis-selection, advisory); stat.logging.debug A. Findings: none. Next: Review Posted → User Testing (no resolve-child).

#### betty — 2026-09-17T20:59:57.398Z
[board-betty] TESTS: OK

#### ada — 2026-09-17T20:57:02.066Z
`origin/sub/AST-1705/AST-1706-fix-get-job-batch-company-id` @ `c8e4fba2b3e8149a11b5ef4a9119b181ddf71ec9` · JOIN company_id plan

---

_Implementation detail may live in git history on `origin/dev`._
