# AST-1610 — Job artifacts are not persisting

<!-- linear-archive: AST-1610 archived 2026-09-22 -->

## Linear archive (AST-1610)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1610/job-artifacts-are-not-persisting  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1600

### Description

## As-is

After a successful `finalize_job_resume` hop (LLM returns a full `agent_payload.resume` with section bodies), `do_task` logs `persist_job_artifact_catalog skipped … reason=prepare_empty` and does not call `save_job_artifact`. The artifacts table has zero rows with `entity_type` of `job` — the job_resume body never lands.

## To-be

A successful `finalize_job_resume` (and the same catalog land for `finalize_cover_letter` when it has a landable body) writes an operative row into the artifacts table with `entity_type` `job` for the catalog key (`job.artifacts.job_resume` / `job.artifacts.cover_letter`), so hydrate/`get_job_current` can show it.

## Proposed steps

1. Reproduce on a RECOMMENDED job: run Generate Artifacts through `finalize_job_resume`; confirm the `prepare_empty` warning and that no `entity_type=job` artifact row appears.
2. At the `_prepare_job_replica_body(catalog_key, parsed, astral_job_id=index)` call in `do_task`, inspect why it returns `None` despite a non-empty finalize payload — almost certainly `parsed_matches_job_resume_content` failing (enabled section IDs vs `_resume_payload_body` unwrap of `agent_payload` / `nested_resume_key`, or `_candidate_data_for_job` / resume structure yielding no matchable non-contact sections).
3. Fix the unwrap/match (or the parsed object passed into prepare) so a successful finalize with landable section bodies returns a body and `save_job_artifact` runs.
4. Confirm artifacts table has `entity_type=job` rows for `job_resume` (and cover letter on the same path when applicable); UI hydrate shows them.

## Component scope

* `src/core/tracker.py` — modified — `_prepare_job_replica_body` / `parsed_matches_job_resume_content` / `_resume_payload_body` (and any helper they call for candidate structure) are what turn a successful finalize payload into `None` today (`prepare_empty`).
* `src/core/agent.py` — modified — `do_task` job catalog land (`TASK_CONFIG.artifact_key` → prepare → `save_job_artifact`) is the call site emitting the warning; may need to pass a different parsed shape if unwrap expects something other than the in-memory hop `parsed`.
* `src/data/database.py` — modified only if investigation shows writes reach save but `entity_type` / insert path is wrong; current log says prepare never lands, so this is secondary.

## Technical scope

* `src/core/tracker.py` — modified function(s): `_prepare_job_replica_body` and/or `parsed_matches_job_resume_content` / `_resume_payload_body` so a successful finalize payload with landable non-contact section bodies is recognized and returned instead of `None`.
* `src/core/agent.py` — modified function: `do_task` catalog-land branch only if the bug is the shape of `parsed` handed to prepare (not the match helpers themselves); keep WARNING on true empty, keep land ungated on `resp_id` (AST-1600).
* `src/data/database.py` — modified function only if save path is reached but `entity_type`/`candidate_id` insert is wrong; otherwise untouched.

## Ancestor candidates

- [ ] AST-1603 — Agent + tracker land via TASK_CONFIG.artifact_key (parent AST-1601); owns the current prepare→`save_job_artifact` path and the exact `prepare_empty` warning string
- [X] AST-1600 — Job resume/cover letter not persisting in artifacts table after task success (parent AST-1588); prior fix for the same symptom (removed `resp_id` gate, added prepare/save WARNINGs); still User Testing — this may be a remaining hole or regression after AST-1603
- [ ] AST-1592 — Tracker generic catalog write/read + job keys + base_resume citation (parent AST-1588); introduced `save_job_artifact` / prepare-replica / empty-skip design
- [ ] AST-1601 — Rip out job-specific artifact pin helpers; match candidate catalog pattern (parent of AST-1603; User Testing)
- [ ] AST-1588 — Support job.artifacts.job_resume and job.artifacts.cover_letter as artifacts (parent of AST-1592/AST-1600; User Testing)

## Original report

Job artifacts are not persisting. Live log on `finalize_job_resume` success:

`persist_job_artifact_catalog skipped task=finalize_job_resume … key=job.artifacts.job_resume reason=prepare_empty`

Operator confirmation: still not saving the job_resume response to the artifact table — zero records in artifact with `entity_type` of `job`.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
