# AST-2015 — [✅/Somerset] qualify_job_listings COMPLETED: 14 error(s) / 16 processed | qualify_job_listings-67d036c7-5729-4c3e-87e5-96800cea4e45

<!-- linear-archive: AST-2015 archived 2026-10-16 -->

## Linear archive (AST-2015)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2015/somerset-qualify-job-listings-completed-14-errors-16-processed-qualify  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

A Somerset `qualify_job_listings` batch of 16 jobs (batch `qualify_job_listings-67d036c7-…`) came back from the model with `agent_performance.status = "failure"` and `failure_note` "Unable to determine a company job ID for listing 002; required for payload." That status covers the whole response, and `do_task` sees it through the AST-1839 rubric-encoded check in `src/core/agent.py`, so it returns `success: False, agent_failure: True` for the entire batch. `_run_batch_consult` in `src/core/consult.py` then sends **all 16 jobs** to their fail destinations: 2 went to `NEW_RETRY`, and 14 that were already sitting in the retry holding went to the terminal `ERROR_QUALIFY_JOB_LISTINGS`. One listing with no job ID wiped out the whole batch, and it was the 15 good listings that took the damage.

The cause is the prompt, not the schema. The `qualify_job_listings` `response_schema` already marks `company_job_id` as `required: False`. However, the `cache_prompt` STEP 1 ("Deduce the company job ID…") and STEP 5 ("ONLY include the job ID…") present the ID as mandatory, and nothing tells the model what to do when it can't find one. The model therefore escalates to the envelope-level `failure` that `prompt_prefix` reserves for "prevented from performing your task". The row in `data/admin/agent_task.json` shows `updated_at` 2026-10-07 03:51, about three hours before this run, so a recent prompt edit is a possible trigger.

## To-be

A listing whose company job ID can't be found is still graded. `company_job_id` is omitted for that line only, and the rest of the batch goes through to pass/fail normally. A missing per-listing field never becomes an envelope-level `failure`. The 14 jobs stranded in `ERROR_QUALIFY_JOB_LISTINGS` by this run get back into the qualify flow.

## Proposed steps

1. Update the `qualify_job_listings` `cache_prompt` in `data/admin/agent_task.json`. STEP 1, STEP 5, and the COMPANY JOB IDENTIFIER section should say that the job ID is best-effort per listing: if it can't be found, leave `company_job_id` off that line and keep grading. They should also say that a gap in one listing never justifies `agent_performance: failure`. Then sync the row to the DB the way prompt edits normally go out.
2. Check whether the 03:51 edit removed wording that used to cover this, using the git history of `data/admin/agent_task.json`. If it did, restore that wording instead of writing new text.
3. **Open for Susan:** should the code also get a guard, so that an envelope failure whose note names one listing on an encoded batch task fails only that line, the same way AST-1884/AST-1996 isolates a malformed grades line? Or is the prompt fix enough? This is the reason the ticket is parked at Discussion rather than Todo.
4. Reset the 14 jobs in `ERROR_QUALIFY_JOB_LISTINGS` from this batch (ids are in the log above) back to `NEW` with a one-off data fix, not a migration, unless Susan prefers to leave them.

## Component scope

* `data/admin/agent_task.json` (modified): `qualify_job_listings` row, `cache_prompt` text. This is where the instruction that makes the ID mandatory lives.
* `src/core/agent.py` (modified **only if** step 3 is approved): the AST-1839 rubric-encoded envelope-failure branch in `do_task`, which currently turns one listing's note into a whole-batch `agent_failure`.
* `src/core/consult.py` (modified **only if** step 3 is approved): the `do_task`-failed branch of `_run_batch_consult`, which would route only the named listing to its fail destination and process the rest.

## Technical scope

* `data/admin/agent_task.json`: prompt text change only, no schema change. `company_job_id` is already optional in `TASK_CONFIG["qualify_job_listings"]["response_schema"]`.
* `src/core/agent.py` (conditional): modified function. The encoded-batch envelope-failure path would keep the parsed payload, so per-line results survive, instead of returning `parsed_response: None`.
* `src/core/consult.py` (conditional): modified function. `_run_batch_consult` would split the batch, sending the failed line to retry/error and the surviving lines to pass/fail, reusing `_transition_batch_consult_failures` for the subset.

## Ancestor candidates

- [X] `docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`: AST-1884/AST-1996 batch blast radius (one bad encoded line fails every entity). Same shape of failure; isolation precedent for step 3.
- [ ] `docs/features/consult/ast-898-new-retry-qualify-holding.md`: `NEW_RETRY` holding for `qualify_job_listings`. Explains why these 14 jobs hit terminal error on a second strike.
- [ ] `docs/features/dispatcher/ast-642-per-entity-retry-vs-error-routing-in-mixed-batch-consult-auto-retry.md`: per-entity retry vs error routing inside a mixed batch.
- [ ] `docs/features/consult/ast-338-refactor-qualify-job-listings.md`: origin of the `qualify_job_listings` STEP-structured prompt and payload.
- [ ] `docs/features/consult/ast-501-encoded-batch-for-qualify-and-evaluate-jd.md`: encoded batch envelope for qualify.
- [ ] `docs/features/tracker/ast-1119-fallback-for-company-job-id.md`: `company_job_id` fallback from a UUID in `job_link` (scoped to `qualify_meteorite` only; explicitly excluded `qualify_job_listings`).

## Original report

```
2026-10-07 06:30:33  [INFO]  somerset | dispatch job starting
qualify_job_listings — 16 available (batch:
qualify_job_listings-67d036c7-5729-4c3e-87e5-96800cea4e45)
2026-10-07 06:30:47  [INFO]  somerset | dispatch job task completed:
qualify_job_listings pass:0 fail:0 error:14 (batch:
qualify_job_listings-67d036c7-5729-4c3e-87e5-96800cea4e45)
2026-10-07 06:30:47  [WARNING]  22f92637-2db7-446f-b38b-ab838e604d02
-> NEW_RETRY [Agent failure: Unable to determine a company job ID for
listing 002; required for payload.]
2026-10-07 06:30:47  [WARNING]  3f17e7a2-dfc8-44f4-ad94-aaa7a72a8abc
-> NEW_RETRY [Agent failure: Unable to determine a company job ID for
listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  62647d8c-aacb-46a3-bbca-a33db6bf5a0e ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  d738c5fe-0981-4b45-81c4-8e491e2d838c ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  a2c4e5ca-4b8c-4464-a81b-588d1ba4a28f ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  af490281-e4e1-46cd-a12e-783272a7de5b ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  4201a9ea-c8fa-44ad-ab87-034fbfa08ebf ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  e7d24126-21e0-4792-998d-a30990d2cf30 ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  5da9b289-5d71-4282-a102-89a15f2602dd ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  85bf4d54-804e-4a05-880a-1490a0725f8c ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  b827c7b9-63c3-4919-beb4-825ac9a26ff9 ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  f1a9ce3a-e807-4621-88be-58d9ed01f448 ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  1c3c05be-40b7-4542-9ee4-0638907716a6 ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  fff2e09d-9417-48d9-bf37-bf51f1be9284 ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  c1e55eb1-863a-49b6-a2d2-8aa672b675c5 ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [ERROR]  df93fed1-0d84-4a91-81f4-575185eec444 ->
ERROR_QUALIFY_JOB_LISTINGS [Agent failure: Unable to determine a
company job ID for listing 002; required for payload.]
2026-10-07 06:30:47  [WARNING]  qualify_job_listings skipped — Agent
failure: Unable to determine a company job ID for listing 002;
required for payload.
  This hop is not persisting a success RESPONSE
2026-10-07 06:30:47  [INFO]  LLM openrouter host=DeepInfra
task=qualify_job_listings 11.6s stop=end_turn tokens in=9365 out=595
```

### Comments

#### chuckles — 2026-10-09T02:31:38.026Z
@susan [PR #276](https://github.com/susansomerset/astral/pull/276) is ready for review. It ships [AST-2089](https://linear.app/astralcareermatch/issue/AST-2089) (prompt: job ID is best-effort per listing; code: on an envelope failure, clean lines are still processed and only the gap listing fails) and [AST-2090](https://linear.app/astralcareermatch/issue/AST-2090) (its tests + bible). Two manual steps after you merge:
- **Prompt goes live** only after Manage Tasks → Revert to file for `agent_task` (the `qualify_job_listings` row).
- **14 stranded jobs** from batch `qualify_job_listings-67d036c7-…` are still in `ERROR_QUALIFY_JOB_LISTINGS`; reset them to `NEW` if you want them requalified (ids in the original report).
Move to PR Ready + assign Chuckles when you want finish-up to land it.

---

_Implementation detail may live in git history on `origin/dev`._
