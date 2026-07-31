# AST-742 — Change "scrape_jd" to "fetch_jd"

<!-- linear-archive: AST-742 archived 2026-07-22 -->

## Linear archive (AST-742)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-742/change-scrape-jd-to-fetch-jd  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** susan  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** duplicate: AST-794

### Description

## Purpose

The job-description retrieval step is still named `scrape_jd` while newer gazer batch tasks use the `fetch_*` pattern (`fetch_website`, `fetch_job_pages`). That inconsistency makes dispatch config, consult routing, and operator vocabulary harder to follow. This feature renames the JD gazer step to `fetch_jd` so job-pipeline naming matches the established fetch convention — without changing scrape behavior, job states, or pipeline order.

## Functional scope

* Rename the dispatch task key from `scrape_jd` to `fetch_jd` everywhere it is the authoritative task identifier (config registries, consult routing, dispatcher eligibility, admin/scheduling surfaces).
* Rename the `GAZER_CONFIG` entry from `scrape_jd` to `fetch_jd`, preserving all orchestration values (pass/fail states, error_states, fallback batch size).
* Rename the gazer batch entry point from `scrape_jd_batch` to `fetch_jd_batch` and update all callers (consult dispatch, tracker coat-check self-heal, tests).
* Migrate existing `dispatch_tasks` database rows (and any seeded defaults) that reference `scrape_jd` so scheduled dispatch continues without manual admin repair.
* Update product tests and test-bible entries that reference the old task key or batch symbol so the rename is fully wired.

## Boundaries

* Does not change JD scrape mechanics, prune rules, classification, connectivity gate, or concurrency limits.
* Does not rename unrelated symbols that happen to contain "scrape" (e.g. `scrape_one`, homepage scrape helpers, roster prefilter scrape steps).
* Does not rename job states (`JD_READY`, `JD_SCRAPE_FAIL`, typed error substates, `PASSED_JOBLIST` trigger) — only the task key and gazer batch naming.
* Does not alter pipeline order: `validate_title` → `qualify_job_listings` → `fetch_jd` → `evaluate_jd` remains unchanged.
* Does not rename `fetch_website`, `fetch_job_pages`, or any company roster dispatch tasks.

## Acceptance criteria

* No remaining `scrape_jd` task-key references in `src/` or `tests/` (excluding historical feature-plan docs under `docs/features/`).
* `DISPATCH_SCHEDULABLE_TASK_KEYS`, `GAZER_CONFIG`, and consult routing recognize `fetch_jd` and no longer route `scrape_jd`.
* `fetch_jd_batch` is invoked for job entities claimed on the `PASSED_JOBLIST` → `JD_READY` step with the same pass/fail outcomes as before the rename.
* Existing environments with `dispatch_tasks.task_key = 'scrape_jd'` rows dispatch successfully after migration (no orphaned rows).
* Component tests for consult routing, gazer JD batch, tracker self-heal, and board-sourced qualify→evaluate path pass unchanged in behavior.

## Dependencies and blockers

none.

## Open questions

one open question before dispatch:

1. **Historical persistence:** Should rows that already stored `task_key=scrape_jd` in `agent_responses`, `dispatch_ledger`, or Execution History be **backfilled** to `fetch_jd`, or **left grandfathered** for audit continuity while only new runs use `fetch_jd`?
   1. Don't backfill.  If we need to for some reason, we can do it in the database directly, but let's just cut over from here.

---

## Original brief

we are using "fetch" for other gazer-type tasks.

### Comments

#### chuckles — 2026-06-25T05:43:37.941Z
[check-linear] Confirmed — on origin/dev via AST-794 / AST-796 (schedulable cutover) + AST-797 (fetch_jd_batch + dispatch row migration). Marked duplicate of AST-794.

#### susan — 2026-06-25T05:40:04.847Z
@chuckles i think we actually implemented this in a more recent ticket. Can you confirm and mark it as duplicate of that ticket?

#### chuckles — 2026-06-18T22:25:46.190Z
@susan — one open question before dispatch:

1. **Historical persistence:** Should rows that already stored `task_key=scrape_jd` in `agent_responses`, `dispatch_ledger`, or Execution History be **backfilled** to `fetch_jd`, or **left grandfathered** for audit continuity while only new runs use `fetch_jd`?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
