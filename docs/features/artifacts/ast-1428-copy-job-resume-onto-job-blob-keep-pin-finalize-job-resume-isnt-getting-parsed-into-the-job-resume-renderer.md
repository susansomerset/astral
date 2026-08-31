# AST-1428 — Copy job resume onto job blob, keep pin (Finalize job resume isn't getting parsed into the job_resume renderer)

<!-- linear-archive: AST-1428 archived 2026-08-31 -->

## Linear archive (AST-1428)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1428/copy-job-resume-onto-job-blob-keep-pin-finalize-job-resume-isnt  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1422 — Finalize job resume isn't getting parsed into the job_resume renderer  
**Blocked by / blocks / related:** parent: AST-1422; blocks: AST-1430

### Description

## What this implements

Copy the parsed `finalize_job_resume` RESPONSE onto the job record as an editable blob. Keep `job_data.artifacts.job_resume` as the `agent_data_id` pin. Later edits write the job blob only. Never edit `agent_data`.

Approved ancestor: AST-1099 (Susan). Product contract from her: copy from the original agent_data response; blob lives on the job; pin persists.

## Citations

AST-1099 pin write (stopped terminal body-copy into `resume_content`). AST-551 / AST-552 job-blob persist. AST-1100 hydrate/PUT (do not replace the pin with a dict).

## Acceptance criteria

- [X] 1. After a successful `finalize_job_resume`, the parsed resume (unwrapped `agent_payload.resume`) is stored as an editable blob on the job (sibling of the pin, not stuffed into `artifacts.job_resume`).
- [X] 2. `artifacts.job_resume` remains the RESPONSE `agent_data_id`.
- [X] 3. Recommended-job Job Resume fields show that copied blob; Preview/Print uses it (title and sections, not contact-only).
- [X] 4. Subsequent editor saves write the job blob only. `agent_data` rows are never updated.

## Proposed change

- [X] Copy after pin in `do_task` via `persist_finalize_job_resume_content` (finalize_job_resume only; before run_next).
- [X] Tracker helper writes `artifacts.resume_content` from `_resume_payload_body`; empty skip; pin untouched.
- [X] GET hydrate overlays `resume_content` onto `job_resume` (else unwrap pin `.resume`); no persist-on-GET.
- [X] `PUT …/artifacts/job_resume` writes `resume_content`; never replaces the pin with a dict.
- [X] Print `_resolve_resume_sections` unwraps pin fallback; prefers `resume_content`.

## Boundaries

Does not re-parent under AST-1099 / AST-1091. Does not edit `agent_data`. Does not replace the pin string with a dict on save (AST-1100's shipped PUT). Cover letter / proposed_answers only if the same copy+keep-pin gap is on those slots as part of making resume work — do not expand into unrelated JAR chrome.

## Notes for planning

Patch `docs/features/artifacts/ast-1099-pin-agent-data-id.md` (plan-fix). Seed that doc in the plan-fix prompt.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1422-finalize-job-resume-not-parsed`, child `sub/AST-1422/<this-id>-copy-job-resume-blob-keep-pin`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-19T00:27:20.343Z
[code-rubric] PROCEED (Commit: da1b045b) keep-pin resume blob copy

#### chuckles — 2026-08-19T00:20:26.932Z
[bug-repro]
Sibling AST-1430 @ c5dd7b40 — merged onto this sub. Repro: resume_content copy after finalize pin + PUT keep-pin. Tests on this branch after merge-child(AST-1430).

#### joan — 2026-08-19T00:06:45.594Z
[board-joan] CANON: OK

#### betty — 2026-08-19T00:05:09.271Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_jobs.md — broken test — TestAst1100JobArtifactPinResolveApi::test_put_job_resume_writes_body_dict asserts dict onto pin; docs/test-bible/core/agent.md AST-1099 — missing coverage — no sibling resume_content copy/unwrap after finalize pin

#### ada — 2026-08-19T00:02:07.697Z
`origin/sub/AST-1422/AST-1428-copy-job-resume-blob-keep-pin` @ `acaf0121` · copy blob keep pin

---

_Implementation detail may live in git history on `origin/dev`._
