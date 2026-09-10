# AST-1547 — Job resume content is not saving to the job record

<!-- linear-archive: AST-1547 archived 2026-09-09 -->

## Linear archive (AST-1547)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1547/job-resume-content-is-not-saving-to-the-job-record  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Job resume content is not saving to the job record

The job_data.artifacts.* elements should ALWAYS begin as a REPLICA of the agent response to the prompt. We are still saving the agent_data reference for job_resume and cover_letter, instead of the actual text content in the job record. The agent_data record remains unchanged.

## As-is

After successful finalize hops (`finalize_job_resume` / `finalize_cover_letter`, and the pin map’s third slot), core writes the RESPONSE `agent_data_id` string into `job_data.artifacts.job_resume` / `cover_letter` (pointer-only). JAR / hydrate / Print paths still resolve those pins through `agent_data` for display. Operator edits therefore either miss a durable job body or risk treating the hop RESPONSE as the editable store. `agent_data` holds the hop body; the job row does not begin as a replica operators read and edit.

## To-be

When those hops succeed, each matching `job_data.artifacts.*` slot **begins as a replica** of the agent response content (parsed hop body written onto the job record). `agent_data` stays the pristine hop RESPONSE and is **not** updated by later human edits.

CRITICAL: Surfaces that already read the job artifact bodies MUST USE THE CONTENT FROM JOB, not agent_data, so that users may edit the job_resume and cover_letter content as needed and the agent_data remains pristine. This should be the same pattern as candidate.base_resume. The response lives in agent_data unaltered, but the edits are persisted on the job (parallel to candidate edits on `artifacts.base_resume`).

## Proposed steps

1. On successful `finalize_job_resume` / `finalize_cover_letter` (same pin-mapped hops), write the parsed hop body onto the job artifact slot(s) as a durable replica — stop leaving pointer-only values as what operators read.
2. Point hydrate / JAR / Print / editor load for those artifacts at the **job** body only (no `resolve_job_artifact_agent_data_body` for operator display/edit), matching how Base Resume Content reads `candidate_data.artifacts.base_resume`.
3. Keep editor Save writing the edited body back onto the job artifact; never write human edits into `agent_data`.
4. Leave `agent_data` RESPONSE rows unchanged after the hop; coat-check empty replicas; keep cancel/clear wiping the job body keys that operators use.

## Component scope

* `src/core/agent.py` — modified: post-`do_task` success path for finalize hops; must drive the job-body replica write (today it pins `agent_data_id` only).
* `src/core/tracker.py` — modified: pin and/or body-persist helpers plus `hydrate_job_artifacts_for_display` (and related save helpers) so the job stores and serves the replica body, not a pin resolve for operator surfaces.
* `src/utils/config.py` — modified only if pin-map / clear-key policy must change so cancel and slot names match body-on-job (not pointer-only) semantics.
* Job artifact PUT / GET paths that currently assume pin strings under `job_resume` / `cover_letter` (tracker + thin API wrappers already used by JAR) — modified so Save/load round-trip the job body the way `base_resume` does on the candidate.

## Technical scope

* `src/core/agent.py` — modified function: `do_task` success hook after RESPONSE store for pin-mapped finalize keys. Why: live production write; must emit a job body replica instead of (or in addition to, if a pin is retained as non-display metadata) pointer-only semantics.
* `src/core/tracker.py` — modified function(s): body persist / save helpers for `job_resume` and `cover_letter` replicas, and hydrate so GET/JAR bind the job dict (not pin→`agent_data`). Why: job artifact merge + display overlay live here; mirrors candidate `base_resume` content-on-entity.
* `src/utils/config.py` — modified config only if `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` / `JOB_BUILD_ARTIFACT_CLEAR_KEYS` must change for body-on-job clear/write policy. Why: slot↔task and cancel keys are config-owned.
* Thin job artifact PUT handlers (existing API → tracker save) — modified function(s) only as needed so editor Save persists body on the job key operators edit, never into `agent_data`. Why: closes the edit loop Susan named.

## Ancestor candidates

- [X] AST-1099 — Pin agent_data_id on job artifact slots after chain hops (direct cause: pointer-only write; stopped terminal body-copy for finalize hops)
- [ ] AST-1091 — Job resume / cover letter / suggested responses not saved in job_data (parent epic that defined “pointer only / not a second copy of the response body on the job row”)
- [ ] AST-1100 — Resolve artifact bodies from pinned agent_data_id for UAT surfaces (readers/hydrate that pull from `agent_data` via pin — conflicts with CRITICAL “use content from job”)
- [ ] [AST-1430](https://linear.app/astralcareermatch/issue/AST-1430/test-gap-resume-content-copy-put-pin-clobber-ast-1428) — prior resume_content sibling-copy / keep-pin work on the AST-1099 line (partial ancestor if body already lands under `resume_content` but surfaces still pin-resolve or cover_letter is still pointer-only)

### Comments

#### chuckles — 2026-09-01T01:39:19.908Z
Not stuck on intake — nothing new to file this pass.

The `[bug]` from yesterday already became **AST-1556** (artifacts table SoT, not `job_data`). It ran the fix lane end-to-end, hit User Testing, and was **merge-child**'d into `ftr/AST-1547-job-resume-content-not-saving` (`e2be9364`). That tip is still **ahead of `origin/dev`** — UAT-batch `bug-fix` correctly does not run prep-uat itself, so Railway staging never got the land.

Next for you to see the fix live: prep-uat on this parent (all non-canceled children are already rollup-safe: AST-1548 Done, AST-1554 Canceled, AST-1556 User Testing). No fresh `[bug]`/`[fix]` in this batch beyond what AST-1556 already covered.

#### susan — 2026-09-01T01:38:09.238Z
@chuckles why is this stuck?

#### susan — 2026-08-31T21:55:01.706Z
\[bug\]

Please have the job-related artifacts persist in artifacts table, not in the job_data of the job record.

#### chuckles — 2026-08-31T21:54:04.498Z
Got it — thanks for the correction.

AST-1548 put editable job resume/cover **body replicas on `job_data.artifacts.*`**. Per this note that was the misspeak: editable drafts for candidate **and** job should live in the **`artifacts` table** (current row keyed by `entity_type` / `entity_id` / `artifact_type`), and the UI should load/save that by entity id — not bury the editable body inside the job record’s `job_data`.

Next pass needs that extra persist step (finalize/Save → `artifacts` table) + UI read path by entity. Say `[bug]` / `[fix]` on this thread (and reassign Chuckles if you want intake to file it) and I will treat this as the to-be.

#### susan — 2026-08-31T21:52:31.902Z
@chuckles Sorry, I hit return too soon on the earlier comment.  the artifacts table should host EDITABLE CONTENT for entities like candidate and job.  I misspoke (having forgotten this) saying that the content should live in the job record itself.  We need to add the extra step to persist the artifact draft for the job in the artifacts table and let the ui use that based on the entity_id, instead of burying it in the content of job_data in job.

#### chuckles — 2026-08-31T21:50:24.648Z
No — that was the point of the fix that just landed.

`candidate_data.artifacts.base_resume` stays the candidate-side body store (agent RESPONSE pristine in `agent_data`; human edits on the candidate artifact). AST-1548 did the job-side parallel: after finalize hops, `job_data.artifacts.job_resume` / `cover_letter` begin as **body replicas** of the agent response, JAR/hydrate/Print read those job bodies (not pin→`agent_data`), and operator Save writes back onto the job. `agent_data` is unchanged.

If what you are seeing in UAT still looks like a pin-only slot or empty editor after a fresh finalize, mark that with `[bug]` / `[fix]` and the job id / symptom — I will not file from this question alone.

#### susan — 2026-08-31T21:48:25.677Z
@chuckles Did we just forget that artifacts has the base resume and should also host job resumes?

---

_Implementation detail may live in git history on `origin/dev`._
