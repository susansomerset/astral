# AST-1548 — fix: job resume/cover letter body replica on job (not agent_data pin)

<!-- linear-archive: AST-1548 archived 2026-09-09 -->

## Linear archive (AST-1548)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1548/fix-job-resumecover-letter-body-replica-on-job-not-agent-data-pin  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1547 — Job resume content is not saving to the job record  
**Blocked by / blocks / related:** parent: AST-1547

### Description

## What this implements

Write job artifact body replicas for finalize hops (`job_resume` / `cover_letter`) so operators read and edit content on the job — same pattern as `candidate.artifacts.base_resume` — while `agent_data` RESPONSE rows stay pristine.

## Scope

### Component scope

* `src/core/agent.py` — modified: post-`do_task` success path for finalize hops; must drive the job-body replica write (today it pins `agent_data_id` only).
* `src/core/tracker.py` — modified: pin and/or body-persist helpers plus `hydrate_job_artifacts_for_display` (and related save helpers) so the job stores and serves the replica body, not a pin resolve for operator surfaces.
* `src/utils/config.py` — modified only if pin-map / clear-key policy must change so cancel and slot names match body-on-job (not pointer-only) semantics.
* Job artifact PUT / GET paths that currently assume pin strings under `job_resume` / `cover_letter` (tracker + thin API wrappers already used by JAR) — modified so Save/load round-trip the job body the way `base_resume` does on the candidate.

### Technical scope

* `src/core/agent.py` — modified function: `do_task` success hook after RESPONSE store for pin-mapped finalize keys. Why: live production write; must emit a job body replica instead of (or in addition to, if a pin is retained as non-display metadata) pointer-only semantics.
* `src/core/tracker.py` — modified function(s): body persist / save helpers for `job_resume` and `cover_letter` replicas, and hydrate so GET/JAR bind the job dict (not pin→`agent_data`). Why: job artifact merge + display overlay live here; mirrors candidate `base_resume` content-on-entity.
* `src/utils/config.py` — modified config only if `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` / `JOB_BUILD_ARTIFACT_CLEAR_KEYS` must change for body-on-job clear/write policy. Why: slot↔task and cancel keys are config-owned.
* Thin job artifact PUT handlers (existing API → tracker save) — modified function(s) only as needed so editor Save persists body on the job key operators edit, never into `agent_data`. Why: closes the edit loop Susan named.

## Proposed change

- [X] Config: `JOB_ARTIFACT_BODY_REPLICA_BY_TASK`; remove finalize keys from pin map
- [X] Agent `do_task`: body replica after RESPONSE store for finalize resume/cover; pin only `proposed_answers`
- [X] Tracker: `persist_finalize_job_resume_content` dual-writes `job_resume`+`resume_content`; `persist_finalize_cover_letter_content`; hydrate job-body only (no pin resolve for those slots)
- [X] PUT `…/artifacts/job_resume` dual-writes body via `save_job_artifact_job_resume_body`

## Notes for planning

Approved ancestor (checked): AST-1099 (Archive). Feature doc: `docs/features/artifacts/ast-1099-pin-agent-data-id.md`. Parent brief is on AST-1547 Description (As-is / To-be / CRITICAL job-body read path).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1547-job-resume-content-not-saving`, child `sub/AST-1547/<this-id>-fix-job-resume-body-replica`. Created at bug-fix.

### Comments

#### betty — 2026-08-31T21:18:08.860Z
`origin/sub/AST-1547/AST-1548-fix-job-resume-body-replica` @ `b4d9a226` · merge-tests landed

#### radia — 2026-08-31T21:08:34.202Z
[code-rubric] REVIEW (Commit: d5113a8b) body replica; tests pending AST-1554

#### joan — 2026-08-31T20:58:12.875Z
[board-joan]  CANON: OK

context_tokens≈12000

#### betty — 2026-08-31T20:57:34.092Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md § AST-1430 + ui/api/api_jobs.md § AST-1430 — broken test — keep-pin nodes (test_finalize_copies_resume_content_keeps_pin; test_put_job_resume_writes_resume_content_keeps_pin) assert pin on job_resume; also missing body-on-slot + cover replica / no-hydrate-pin-resolve for the AST-1548 repro

#### ada — 2026-08-31T20:56:07.038Z
`origin/sub/AST-1547/AST-1548-fix-job-resume-body-replica` @ `b5cb2aeb91b911fdb4a07903d4d55deee16f3604` · body replica on job slots

---

_Implementation detail may live in git history on `origin/dev`._
