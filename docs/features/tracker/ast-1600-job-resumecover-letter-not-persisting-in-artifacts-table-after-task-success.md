# AST-1600 — Job resume/cover letter not persisting in artifacts table after task success

<!-- linear-archive: AST-1600 archived 2026-09-24 -->

## Linear archive (AST-1600)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1600/job-resumecover-letter-not-persisting-in-artifacts-table-after-task  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1588 — Support “job.artifacts.job_resume” and “job.artifacts.cover_letter”as artifacts  
**Blocked by / blocks / related:** parent: AST-1588

### Description

## Susan report (verbatim)

[bug]

The base resume and cover letter are not persisting in the artifact table, despite the task successfully completing.  Wasn't this one of the acceptance criteria?

## As-is

After a recommended-job artifact generation task completes successfully, the job resume and cover letter bodies are not present as current rows in the artifacts table.

## To-be

After that task completes successfully, `job.artifacts.job_resume` and `job.artifacts.cover_letter` persist via the generic catalog write into the artifacts table (AC for this epic).

## Suggested engineer

Hedy Lamarr (sibling AST-1592 — tracker generic catalog write/read + job keys + base_resume citation)

## Proposed change

- [X] 1. `tracker._candidate_id_for_job` prefers denormalized `job.candidate_id`, then company chain.
- [X] 2. `tracker.save_job_artifact` passes `candidate_id=` into `database.save_artifact` (raises if unresolved).
- [X] 3. `database._resolve_artifact_candidate_id` (job) prefers `job.candidate_id`, then company join.
- [X] 4. `agent` body-replica land runs on success+index without requiring `resp_id`; warn on empty prepare/save; pins still need `resp_id`.
- [X] 5. `api_jobs` PUT/detail already on catalog path — verified, no change.

## QA test manifest (AST-1600)

1. **[bug-repro]** `tests/component/core/test_agent.py::TestAst1600DoTaskBodyReplicaLand`
2. **[bug-repro]** `tests/component/core/test_tracker.py::TestAst1600TrackerCandidateIdLand`

### Comments

#### radia — 2026-09-06T16:49:48.190Z
[code-rubric] PROCEED (Commit: 5e40874c) Finalize land + candidate_id fix

#### betty — 2026-09-06T16:44:51.006Z
[bug-repro]
`origin/sub/AST-1588/AST-1600-job-resume-cover-not-persisting` @ `148b4e47` · repro lands red, awaits fix

#### betty — 2026-09-06T16:41:02.818Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md § AST-1099 — `TestAst1099DoTaskArtifactPin::test_debug_skip_replica_when_store_fails` asserts store_failed skips body replica (Blast radius break); missing repro that finalize lands without resp_id + `save_job_artifact`/`_resolve_artifact_candidate_id` prefer job.candidate_id (tracker.md § AST-1592; artifacts.md § AST-1597).

#### joan — 2026-09-06T16:40:31.423Z
[board-joan]  CANON: OK

context_tokens≈72000

#### hedy — 2026-09-06T16:39:10.244Z
`origin/sub/AST-1588/AST-1600-job-resume-cover-not-persisting` @ `435221fa47aa5a03dbd7ccca4ff9a247d821b06f` · plan-fix ready

#### susan — 2026-09-06T16:34:06.661Z
Also the read from artifact must read current and the job modal save uses the same write path.

---

_Implementation detail may live in git history on `origin/dev`._
