# AST-2169 — fix: Estelle job reads own meteorite jobs by candidate_id, not null company

<!-- linear-archive: AST-2169 archived 2026-10-16 -->

## Linear archive (AST-2169)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2169/fix-estelle-job-reads-own-meteorite-jobs-by-candidate-id-not-null  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-2167 — /check-status for an explicit job link failed  
**Blocked by / blocks / related:** parent: AST-2167; blocks: AST-2171

### Description

## What this implements

Estelle's job reads decide whether a job belongs to the sender from the job's own `candidate_id`, not from the job's company. Meteorite-sourced jobs (which have `company_id = NULL` since AST-1701) are no longer filtered out of `/check-status`, `get_job_by_pattern`, and `get_job_data`.

## Scope

## Component scope

* `src/core/tracker.py`: modified. `_job_owned_by_candidate` is the one place that rejects company-less jobs, and all three Estelle job reads go through it.

## Technical scope

* `src/core/tracker.py`: modified function `_job_owned_by_candidate`. Ownership comes from the job's own `candidate_id` and no longer depends on the nullable `company_id`. Since AST-1701 that is the only owner field every job row carries. No schema change and no new function.

## Acceptance criteria

* `/check-status <job link>` from a bound sender finds that sender's job when `company_id` is `NULL`. The AST-2167 repro is Somerset's Dice job `6775db61-…` in `CANDIDATE_SKIPPED`, and it returns one match.
* `get_job_by_pattern` and `get_job_data` return the same meteorite job for its owner instead of not-found.
* A job whose `candidate_id` is a different candidate is still invisible to the sender on all three paths.
* Employer-sourced jobs (non-null `company_id`) owned by the sender behave exactly as today.

## Boundaries

Does not change `_match_jobs_by_pattern`, the `list_jobs` scoping, the reply templates, or the Contact command intercept. No schema change and no backfill. Tests and bible are Betty's (fix-board decides whether a gap child is needed).

## Notes for planning

The AST-2167 Description (As-is / To-be / Proposed steps) is authoritative. Susan checked ancestor [AST-2151](https://linear.app/astralcareermatch/issue/AST-2151). Its plan doc `docs/features/contact/ast-2151-check-status-registry-handler.md` records this exact null-`company_id` miss as an inherited, out-of-scope consequence. Patch that doc with a `## Bug: <this id>` block; never create a new doc.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-2167-check-status-ownership-candidate-id`, child `sub/AST-2167/AST-2169-check-status-ownership-candidate-id`. Created at bug-fix.

### Comments

#### radia — 2026-10-12T22:33:51.645Z
[code-rubric] PROCEED (Commit: 74526b8c0) ownership via candidate_id

#### ada — 2026-10-12T22:32:14.571Z
`origin/sub/AST-2167/AST-2169-check-status-ownership-candidate-id` @ `74526b8c0` · lighter check (no qa-fix), no new commits

`py_compile src/core/tracker.py` clean. `pytest tests/component/core/test_tracker.py tests/component/core/test_contact.py`: base (`origin/ftr/AST-2167-…`) 24 failed / 386 passed; tip 33 failed / 377 passed. The 24 base reds are identical at tip (pre-existing, unrelated). New reds = 9, all in the already-routed classes (fixtures have no `candidate_id`), for AST-2171:

- TestAst1518ContactTaskReads (2): `test_contact_task_get_job_by_pattern_happy_and_errors`, `test_contact_task_get_job_data_ownership`
- TestAst2151ContactCommandCheckStatus (7): `test_ac3_one_match_reply_with_clocks_and_encoded_deeplink`, `test_ac4_several_matches_list_both_titles_and_links`, `test_ac5_other_candidates_job_excluded`, `test_ac7_no_origin_replies_without_links_one_warning[unset]`, `[blank]`, `test_unparseable_timestamps_render_dash[none]`, `[garbage]`

No new reds outside those two classes.

#### joan — 2026-10-12T22:30:13.441Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T22:29:42.265Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/tracker.md § AST-1518 / § AST-2151 — broken tests + no null-company repro — `TestAst1518ContactTaskReads._job()` and `TestAst2151ContactCommandCheckStatus._job()/_stub(owners)` build rows without `candidate_id` and drive ownership via `get_company`, so the happy paths in `test_contact_task_get_job_by_pattern_happy_and_errors`, `test_contact_task_get_job_data_ownership`, `test_style_d_debug_on_job_data` and the AST-2151 one/several-match tests go red. The cross-candidate cases must vary `job["candidate_id"]` instead of the company owner, and the repro (meteorite row, `company: None`, `candidate_id` = sender → check-status single match + get_job_data ok; `candidate_id` = other → still refused) has no existing node.

#### ada — 2026-10-12T22:29:02.943Z
`origin/sub/AST-2167/AST-2169-check-status-ownership-candidate-id` @ `c7a57c059` · ownership via job.candidate_id

---

_Implementation detail may live in git history on `origin/dev`._
