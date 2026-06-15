# AST-372 — consult: fetch job by ID through tracker, not database

<!-- linear-archive: AST-372 archived 2026-06-15 -->

## Linear archive (AST-372)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-372/consult-fetch-job-by-id-through-tracker-not-database  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Problem

`src/core/consult.py` imports `get_job` from `src.data.database` directly. Job row reads from core should go through `src/core/tracker.py` so tracker stays the single job lifecycle surface for callers outside the data layer.

## Batch APIs vs job-by-ID

`tracker.get_job_batch(batch_id)` and `get_new_job_batch` operate on **dispatch-claimed batches**: many jobs can share one `batch_id` for a run. That path is the wrong abstraction for "load this `astral_job_id` now" (e.g. `render_verdict`, builder HTML).

A dedicated **by-id** read is needed: add something like `tracker.get_job(astral_job_id: str)` that delegates to `database.get_job` (thin wrapper), then switch `consult` to use it.

## Scope

* Add the tracker wrapper (if not already present when this is picked up).
* Replace `consult`'s `from src.data.database import get_job` usage with `tracker.get_job` (or equivalent).
* Quick grep for other core modules importing `get_job` for jobs and align if trivial.

## Context

Noted while planning [AST-294](https://linear.app/astralcareermatch/issue/AST-294/build-builderpy-resume-and-cover-letter-renderer) (builder): product text says builder uses tracker for job data; consult currently bypasses tracker for the initial job fetch.

### Comments

#### chuckles — 2026-05-25T04:47:12.534Z
## Manual test steps

1. On local `dev` (merged): `rg 'src\.data\.database' src/core/consult.py` → no matches.
2. `rg 'from src\.data\.database import .*get_job' src/core` → no matches.
3. Manifest (green on prep-uat):
   ```bash
   pytest tests/component/core/test_consult.py \
     tests/component/core/test_tracker.py::TestTrackerFacades::test_ast486_consult_layer_facades_delegate_to_database -q --tb=short
   ```
   → 121 passed.
4. Optional smoke: run a consult batch / `render_verdict` path you use today; confirm no import errors.

`origin/ftr/AST-372-consult-fetch-job-by-id-through-tracker-not-database` @ `61d58336` · local `dev` @ `0162c8e3`. Sub `AST-486` deleted. Restart app if running.

Reset if needed: `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-05-25T04:22:11.811Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-372 | ftr/AST-372-consult-fetch-job-by-id-through-tracker-not-database |
| AST-486 | sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports |

— Chuckles

#### susan — 2026-05-25T04:19:47.416Z
@chuckles With the introduction of new job states I believe we just removed the need for specific get job calls from anywhere.  They are all scooped in batches the same way.  Now we should address so that consult.py does not call database directly for any reason.

#### chuckles — 2026-05-25T01:34:03.722Z
[check-linear]

**@susan — confirm (code on `origin/dev`):**

**`builder.py`** — Already uses **`tracker.get_job(job_id)`** (`build_resume`). No change needed there for this ticket.

**`consult.py`** — Still imports **`database.get_job`** (3 call sites):

1. **`render_verdict`** (~L334) — **Yes, by-id today.** Public API is `(task_type, astral_job_id)` and loads the row inside the orchestrator. Batch router (`consult_do` / `get` / `like`) passes only the id even though `entities[0]` is already in hand — so this is a **double fetch** from batch, but the orchestrator is also used from tests/CLI with **id only**, so consult does need *a* job load here unless we add an optional `job=` parameter.

2. **`_run_cover_letter_for_job`** / **`_run_craft_job_cover_letter_batch`** (~L746, ~L794) — **`get_job(aid) or job`**. Batch already has `job`; refetch is to pick up **`resume_content`** after the resume chain persisted. Could use the in-memory row if we refreshed it from persist — not a “batch vs by-id” gap, just a freshness read.

**`tracker.get_job`** — **Already exists** (thin delegate to `database.get_job`, comment cites AST-372). Remaining work is **import swap in consult** (+ optional: pass `job` into `render_verdict` from batch to drop redundant fetch).

**Ticket scope suggestion:** Keep AST-372 as consult hygiene (migrate to `tracker.get_job`; optional follow-up to thread `job` from batch). Builder item is **done**. Not cancel — still worth the one-line boundary fix.

— Chuckles

#### susan — 2026-05-25T01:32:48.108Z
@chuckles Can you confirm at the moment that consult.py doesn't actually need to fetch job by id, but builder.py will?  I can't think of an example when consult.py would need to get a single job by id (rather than from a batch passed in).

---

_Implementation detail may live in git history on `origin/dev`._
