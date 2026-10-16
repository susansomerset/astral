# AST-2143 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 36 processed | meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4

<!-- linear-archive: AST-2143 archived 2026-10-16 -->

## Linear archive (AST-2143)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2143/somerset-meteorite-grade-do-completed-1-errors-36-processed-meteorite  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Prior occurrences

* none found (4 searches)
* `meteorite_grade_do · ERROR_METEORITE_GRADE_DO · no live content` (self-heal `Invalid transition: METEORITE_PASSED_JD -> ERROR_FETCH_JD_UNREADABLE`, job has no `job_link`): **novel**, diagnosed below.
* Not failures in this batch, listed for context only: 16 × `AllLiteralXGradeSetError` and 3 × `grade X requires confidence digit 0` (`ADX4`) went to `METEORITE_PASSED_JD_RETRY`. That is the shipped first-strike retry from [AST-2011](https://linear.app/astralcareermatch/issue/AST-2011) and the X-with-nonzero-confidence decode failure that [AST-2045](https://linear.app/astralcareermatch/issue/AST-2045) deliberately kept. Not re-diagnosed here.

## As-is

Somerset `meteorite_grade_do` batch `b93cbaa7` claimed 36 jobs: 16 passed, 1 errored, the rest went to retry. The one error is job `4d9d1c79-…`, which sits at `METEORITE_PASSED_JD`:

1. `_run_batch_consult`'s prep loop (`src/core/consult.py`) calls `_prep_live_content`, which calls `tracker.get_job_data(job, "job_description")`.
2. `get_job_data` (`src/core/tracker.py`) finds the composed JD (`compose_job_description`, which is the stored preamble plus the capture behind `jd_telescope_data_id`) shorter than `jd_min_chars`, so it runs the coat-check self-heal: `fetch_jd_batch(uuid, [job])`.
3. `fetch_jd_batch` (`src/core/gazer.py`) finds no `job_link` and calls `transition_job_state([aid], fetch_jd.fail_state)`, which means `ERROR_FETCH_JD_UNREADABLE`. That move isn't legal from `METEORITE_PASSED_JD`, so it raises `Invalid transition`.
4. `get_job_data` catches the exception, logs `fetch_jd_batch self-heal failed`, and returns `None`. Consult then moves the job to `ERROR_METEORITE_GRADE_DO` with the reason `no live content`.

Two separate problems:

* **The self-heal can't work for this job, and it is unsafe downstream.** With no `job_link` there is nothing to scrape. Even when a link exists, `fetch_jd_batch` writes fetch-stage states (`JD_READY` / `ERROR_FETCH_JD_UNREADABLE` / classified states), and none of those are legal from a later task's state such as `METEORITE_PASSED_JD`. So the self-heal is noisy at best and throws at worst. Today the throw is swallowed, so the job's state isn't corrupted, only mis-logged.
* **Why the job has no usable JD is unconfirmed.** A meteorite job with no `job_link` is what body-mode email ingest produces ([AST-1132](<https://linear.app/astralcareermatch/issue/AST-1132>)), and its JD is the preamble only. The job passed the meteorite JD stage, so it had a JD at that point. Either its preamble is under `jd_min_chars` (and it always would have tripped this), or the composed read from [AST-2133](https://linear.app/astralcareermatch/issue/AST-2133) (shipped Oct 10) now sees less than the old raw `job_description` read did, for example a `jd_telescope_data_id` whose row is gone. The local DB has no jobs table, so the job row needs a look on Railway.

## To-be

* A job whose composed JD is short **and** has no `job_link` doesn't attempt a self-heal. `get_job_data` warns once (`JD short, no job_link — cannot self-heal`) and returns whatever composed text exists, or `None`. There is no `Invalid transition` exception and no misleading `fetch_jd_batch self-heal failed` line.
* The coat-check self-heal never tries to move a job into a fetch-stage state while the job is sitting in a later task's state. It either scrapes and keeps the capture without transitioning, or it leaves state alone when the fetch-stage destination isn't a legal move from the job's current state. Which of these is Susan's call (see Proposed steps).
* A job that truly has no usable JD still lands in its task's `error_state` (here `ERROR_METEORITE_GRADE_DO`), as it does today. Only the noise and the illegal attempt go away.

## Proposed steps

1. Ops first: on Railway, read job `4d9d1c79-fd62-4639-a5d8-885c01d808bd`. Check `job_link`, the length of `job_data.job_description`, `jd_telescope_data_id`, and whether that `telescope_data` row exists. That decides whether this is a short-preamble meteorite job (only the self-heal guard below is needed) or a JD lost by the composed read (a regression of [AST-2133](https://linear.app/astralcareermatch/issue/AST-2133/composed-read-only-job-description-create-a-new-table-telescope-data) that needs its own fix).
2. `get_job_data`: before the self-heal, skip `fetch_jd_batch` when the job has no `job_link`. Warn and return `compose_job_description(job) or None`.
3. Make the self-heal transition-safe. Pick one:
   * **(a)** Add a no-transition single-job mode to `fetch_jd_batch`: scrape, gate, keep the capture and write `jd_telescope_data_id`, but skip every `transition_job_state`. The coat-check uses that mode.
   * **(b)** Keep `fetch_jd_batch` as it is, and have the coat-check skip it when the job's current state isn't one of the fetch-stage destinations' `prior_states`.

   (a) is cleaner. (b) is smaller.
4. Re-run somerset `meteorite_grade_do`. A link-less, short-JD job should land in `ERROR_METEORITE_GRADE_DO` with a single "no job_link" warning and no `Invalid transition` line.

## Component scope

* `src/core/tracker.py`: modified. `get_job_data` gets the no-`job_link` guard, and its self-heal call becomes transition-safe.
* `src/core/gazer.py`: modified, only if option 3(a) is picked. `fetch_jd_batch` gets a mode that keeps the capture without moving the job's state.

## Technical scope

* `src/core/tracker.py`: modified function `get_job_data`. It adds an early return when there is no `job_link` and calls the self-heal in a way that can't produce an illegal state transition. No new table and no new field.
* `src/core/gazer.py` (option 3(a) only): modified function `fetch_jd_batch`, which gains an opt-out of its state transitions. Without that, a downstream coat-check can't reuse the scrape-and-keep path safely.

## Ancestor candidates

- [ ] AST-2133: composed read-only job description. This moved the self-heal trigger to composed length and is the most recent change on this path (`docs/features/foundation/ast-2133-composed-read-only-job-description.md`).
- [X] AST-326: batch scrape JDs. This made the `get_job_data` coat-check delegate to the batch fetch with its fetch-stage transitions (`docs/features/gazer/ast-326-batch-scrape-jds-plan.md`).
- [ ] AST-742: scrape_jd → fetch_jd. This renamed the self-heal caller to `fetch_jd_batch` (`docs/features/roster/ast-742-change-scrape-jd-to-fetch-jd.md`).
- [ ] AST-797: runtime routing / scrape_jd → fetch_jd cutover. This covers the tracker self-heal import and log strings (`docs/features/roster/ast-797-runtime-routing-db-migration-inline-validate-title.md`).
- [ ] AST-1132: meteorite job-link hygiene. Body-mode ingest creates meteorite jobs with no `job_link` (`docs/features/meteorite/ast-1132-job-link-hygiene-non-job-create-skip.md`).

## Original report

```
2026-10-12 17:42:45  [INFO]  somerset | dispatch job starting
meteorite_grade_do — 36 available (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:42:56  [WARNING]  4d9d1c79-fd62-4639-a5d8-885c01d808bd
-> ERROR_METEORITE_GRADE_DO [no live content]
2026-10-12 17:42:56  [WARNING]  get_job_data: fetch_jd_batch self-heal
failed for 4d9d1c79-fd62-4639-a5d8-885c01d808bd: Invalid transition:
METEORITE_PASSED_JD -> ERROR_FETCH_JD_UNREADABLE
2026-10-12 17:42:56  [WARNING]  [4d9d1c79-fd62-4639-a5d8-885c01d808bd]
no job_link, cannot scrape JD
2026-10-12 17:42:56  [WARNING]  [4d9d1c79-fd62-4639-a5d8-885c01d808bd]
coat-check self-heal: JD missing, invoking fetch_jd_batch
2026-10-12 17:43:30  [INFO]  1fea8e7e-33f2-4ffa-be71-94ada9e6ce7d |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [INFO]  2903fb71-4056-4c9b-9d9d-ef4090018ebb |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [INFO]  b173ccb6-65cd-47e5-87ae-777717353381 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [INFO]  2ba2170a-1cc1-4ba7-a780-1e566a3a8cad |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [INFO]  d25ba19f-13bb-4219-b3cb-8573c96e2180 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [INFO]  1397d420-506d-45b9-844f-1f220cde19b0 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [INFO]  6ddd5bf9-e03f-4898-bcc2-72a78b118c82 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [INFO]  9d226642-4969-4423-9f90-1689c5e43e7d |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [INFO]  8f872f1d-9a7e-4581-818a-cddf09f81a62 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [WARNING]  7dace48c-2c00-4445-913d-ed1aa4f9a6c2
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [INFO]  c5840b77-043b-4c11-b7f9-58c0d7afd0c4 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [INFO]  f4bef295-d0fe-42e7-a40d-a85696505861 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [INFO]  fcbc84ca-cc20-4228-98e3-85f23835bb82 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [WARNING]  cfcccdcb-1c07-4b23-9a46-834382f2ef42
-> METEORITE_PASSED_JD_RETRY [decode: [meteorite_grade_do] grade X
requires confidence digit 0, got 4 in segment 'ADX4' (line
'032|ADX4|AOB4|DCB4|HDB4|HTB4|PDB4|RRC3|RWB3|SDA4|SEB4|TPB4')]
2026-10-12 17:43:30  [WARNING]  05d16d1c-78b1-488c-b037-19c5ee83e734
-> METEORITE_PASSED_JD_RETRY [decode: [meteorite_grade_do] grade X
requires confidence digit 0, got 4 in segment 'ADX4' (line
'031|ADX4|AOA5|DCB4|HDB4|HTA5|PDA5|RRA5|RWA4|SDA5|SEA5|TPA5')]
2026-10-12 17:43:30  [WARNING]  a9112ac6-cc97-4e79-be42-327163a10e40
-> METEORITE_PASSED_JD_RETRY [decode: [meteorite_grade_do] grade X
requires confidence digit 0, got 4 in segment 'ADX4' (line
'029|ADX4|AOB4|DCB4|HDB4|HTB4|PDB4|RRC3|RWB4|SDA4|SEB4|TPB4')]
2026-10-12 17:43:30  [INFO]  LLM openrouter host=Nebius
task=meteorite_grade_do 11.9s stop=end_turn tokens in=9145 out=743
2026-10-12 17:43:30  [WARNING]  7028b971-cb43-4c5e-a9fb-0ca32713d235
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [WARNING]  877c162e-24d8-4556-8f8d-f83d54f064ae
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [INFO]  32999a02-ab1f-451e-ae05-39cedcd5aa0c |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [WARNING]  55a6d34a-b8b1-4279-8ec7-e90ea2d40220
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [WARNING]  bfac96c4-dc59-461e-88d9-63cc0d51b2d4
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [WARNING]  ab4ff529-d9e3-4472-8c03-47ac73f3b86b
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [INFO]  c23a7e75-d6dc-41d6-95df-c1c00ad05c78 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [WARNING]  1a2b14f5-f926-428a-9653-35917822f7f1
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [WARNING]  8674e96f-632b-4179-b48b-a048ae78ab89
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [INFO]  1a66955c-50af-4b19-a53c-e9a16442fd91 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [INFO]  b5245474-ac8b-496e-ae90-f6ed47065d0f |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:30  [WARNING]  0f8f1d81-ed8d-4c78-a762-01f7f3f92e7c
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [WARNING]  bf81c81e-15e7-4ef2-b61b-e6181a9b8891
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [WARNING]  e769541b-8984-4497-a888-87108ef7f248
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [WARNING]  69af53bd-5fe2-48f8-b7b2-85924c11a1b2
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [WARNING]  2ec2b685-2ad6-49a7-9ba3-4c85eb909150
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [WARNING]  8b30ec4c-57cb-49ca-9481-3fecaf4539e1
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [WARNING]  924a7d47-c60c-4a86-a0e2-73bdea142053
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [WARNING]  9b03bf0a-4516-4d0a-92f8-5fd555bff812
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (11 vectors)]
2026-10-12 17:43:30  [INFO]  LLM openrouter host=Nebius
task=meteorite_grade_do 14.9s stop=end_turn tokens in=18991 out=926
2026-10-12 17:43:33  [INFO]  somerset | dispatch job task completed:
meteorite_grade_do pass:16 fail:0 error:1 (batch:
meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4)
2026-10-12 17:43:33  [INFO]  somerset | dispatch job stopping
meteorite_grade_do — 19 remaining after 1 run(s)
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
