# AST-1613 — fix: job artifacts prepare_empty skip after finalize success (Job artifacts are not persisting)

<!-- linear-archive: AST-1613 archived 2026-09-22 -->

## Linear archive (AST-1613)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1613/fix-job-artifacts-prepare-empty-skip-after-finalize-success-job  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1610 — Job artifacts are not persisting  
**Blocked by / blocks / related:** parent: AST-1610

### Description

## What this implements

Fix: successful `finalize_job_resume` (and same catalog land for cover letter when landable) must write `entity_type=job` artifact rows instead of skipping with `prepare_empty`.

## Scope

### Component scope

* `src/core/tracker.py` — modified — `_prepare_job_replica_body` / `parsed_matches_job_resume_content` / `_resume_payload_body` (and any helper they call for candidate structure) are what turn a successful finalize payload into `None` today (`prepare_empty`).
* `src/core/agent.py` — modified — `do_task` job catalog land (`TASK_CONFIG.artifact_key` → prepare → `save_job_artifact`) is the call site emitting the warning; may need to pass a different parsed shape if unwrap expects something other than the in-memory hop `parsed`.
* `src/data/database.py` — modified only if investigation shows writes reach save but `entity_type` / insert path is wrong; current log says prepare never lands, so this is secondary.

### Technical scope

* `src/core/tracker.py` — modified function(s): `_prepare_job_replica_body` and/or `parsed_matches_job_resume_content` / `_resume_payload_body` so a successful finalize payload with landable non-contact section bodies is recognized and returned instead of `None`.
* `src/core/agent.py` — modified function: `do_task` catalog-land branch only if the bug is the shape of `parsed` handed to prepare (not the match helpers themselves); keep WARNING on true empty, keep land ungated on `resp_id` (AST-1600).
* `src/data/database.py` — modified function only if save path is reached but `entity_type`/`candidate_id` insert is wrong; otherwise untouched.

## Context

Parent bug AST-1610 (orphaned mini-epic). Approved ancestor: AST-1600 (related). As-is/to-be live on the parent Description.

### Comments

#### radia — 2026-09-09T22:41:52.973Z
[code-rubric] PROCEED (Commit: 42cb9729) String parsed coerce land

#### joan — 2026-09-09T22:36:45.488Z
[board-joan]  CANON: OK

Local string→dict coercion at prepare/land in tracker.py and agent.py aligns with existing artifact write-operative flow and coat-check-never-store-empty; no statute or approved pattern needs updating. Deferring response_format in config.py is a scoped plan decision, not a canon gap.

#### betty — 2026-09-09T22:36:09.245Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/tracker.md + docs/test-bible/core/agent.md — missing coverage — no test feeds finalize-shaped string JSON (agent_payload.resume) through prepare/land; existing suites mock prepare and inject dict parsed_response, so prepare_empty never reproduces.

#### hedy — 2026-09-09T22:33:41.294Z
`origin/sub/AST-1610/AST-1613-fix-job-artifacts-prepare-empty` @ `779eea5ef5b76ab9e0ceb07d9b53dfac11d8b7ca` · coerce string parsed

---

_Implementation detail may live in git history on `origin/dev`._
