# AST-1345 — Clarify candidate_data.artifacts.base_resume.experience node

<!-- linear-archive: AST-1345 archived 2026-08-31 -->

## Linear archive (AST-1345)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1345/clarify-candidate-dataartifactsbase-resumeexperience-node  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators and agents still meet `candidate_data.artifacts.base_resume.experience` (and the matching job-artifact experience node) as either a long prose string or a structured job list. The product needs one wire shape only: an ordered array of experience jobs, honored end-to-end in craft/parse schemas and prompts, agent validation, the Base Resume / job artifact UI, and resume render/print. Base experience is the template; job artifacts use the same structure by default. Legacy string (or other non-array) blobs are not migrated — they fail with a regenerate toast and must not produce a printable resume missing Experience.

## Functional scope

* Candidate `artifacts.base_resume.experience` is an ordered array of job objects (company, title, dates, location, accomplishments) — not a single prose string.
* Base experience is the template for job: job `job_data.artifacts` resume content uses the same experience array structure by default (not a separate job-only shape on Base).
* Craft/parse/finalize response schemas and candidate + job craft prompts describe and require that array shape for experience.
* The agent validates the shared array contract without extra needless checks that reject valid array payloads or re-impose string-era rules.
* The Base Resume Content UI presents and persists experience as that array (the base template); job artifact surfaces that edit experience use the same structure.
* Resume render and print emit each experience job from the array (role metadata + accomplishments), not one merged prose blob.
* When experience is a legacy string or any non-array shape, show toast exactly: `unsupported resume structure, please regenerate` — do not open Print / Open HTML and do not emit a partial resume with Experience omitted. No automatic migration of existing candidates.
* When `debug=True` on touched craft/parse/tailor or persist paths that read experience, debug output records what experience shape was found and what was recorded per job (Style D index + detail), not only pass/fail counts.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — experience wire shape and schema literals stay in config, not scattered across agent/UI/builder.
  * `pattern.layers.import-discipline` — UI renders resolved shapes; core owns validate/persist/emit; no UI→data shortcuts.
* **New patterns proposed** — none (reuse the existing experience job-array contract from the AST-994 epic; this epic closes remaining surfaces and the unsupported-shape operator path).
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — array contract and field defs live in config.
  * `astral.agent.do-task-delegation` — craft/parse/finalize stay on `do_task`; no parallel LLM path.
  * `astral.standards.debug-contract-gated` — experience found/recorded debug only when `debug=True`.
  * `astral.layers.import-direction` — ui → core/utils; core → data/external/utils.
  * `astral.layers.ui-config-driven-business-logic` — UI field type / body_kind for experience comes from config shapes, not hard-coded React rules.
  * `astral.standards.no-hardcoded-sets` — no ad-hoc experience field lists outside config.
  * `astral.standards.in-scope-only` — do not reopen cover-letter, education/skills chrome, or migration tooling.

## Boundaries

* Does **not** treat Base Resume experience editing as job-specific tailoring — Base is the template; job reuses the same structure.
* Does **not** migrate or rewrite existing string-shaped experience blobs into the array.
* Does **not** invent a second experience schema for job vs candidate.
* Does **not** change cover-letter HTML, signature, or from-block work.
* Does **not** reopen AST-993 golden-fixture education/skills/header chrome beyond what render already does for job-array experience.
* Does **not** add multi-candidate backfill or admin bulk repair tools.
* Does **not** open or emit Print / Open HTML for an unsupported experience shape (toast only — no Experience-omitted resume).
* Must not break Highlights / resume_structure catalog work already landed (experience remains the `experience_detail` / `experience_jobs` body).
* Adjacent in-flight Print chrome ([AST-1314](https://linear.app/astralcareermatch/issue/AST-1314/add-a-print-button-to-base-resume-content) family) stays out of scope except that print must honor the array contract and the unsupported toast (no tab) when experience is unusable.

## Acceptance criteria

1. After craft/parse (or load of a saved base resume) for a multi-job resume, `artifacts.base_resume.experience` is an ordered array; each element exposes company, title, dates, location, and accomplishments observable in Base Resume Content / parse JSON.
2. Job artifact resume content that carries experience uses the same array element shape as the candidate base resume (same keys/requiredness by default); Base remains the template, not a job-tailored editor.
3. Craft/parse/finalize schemas and the related candidate + job prompts accept and describe experience only as that array — string experience is not a valid success path.
4. Agent handling of experience does not reject a valid job array with leftover string-era validation, and does not require fields beyond the shared contract.
5. In the Base Resume Content UI, Susan can view and save experience as the job-array template (not as one undifferentiated prose field that round-trips as a string).
6. Render and Print of a base (and job, where applicable) resume show each experience job with role metadata and accomplishments from the array — not one merged experience string.
7. Opening or printing a resume whose experience is still a string (or other non-array shape) shows toast text `unsupported resume structure, please regenerate`, opens no HTML tab, and does not emit a resume with Experience omitted.
8. When `debug=True` on touched experience-reading hops/persist paths, logs show found/recorded experience shape and per-job detail (Style D), not only summaries.

## Dependencies and blockers

none (prior AST-994 / AST-996–998 job-array work is already on `dev`; this epic closes remaining surfaces and the explicit unsupported-shape toast). Adjacent [AST-1314](https://linear.app/astralcareermatch/issue/AST-1314/add-a-print-button-to-base-resume-content) Print UI is not a blocker.

## Open questions

none

## Proposed child tickets

#### 1!: **Experience array contract — schema, prompts, agent - Ada**

Owns the shared experience job-array wire shape in craft/parse/finalize response schemas and candidate + job craft prompts; tightens agent validation to that contract only (no string success path, no needless extra checks). Does **not** own UI toast chrome or HTML emit (siblings #2–#3). After #1, schemas/prompts/agent agree on one array shape for candidate and job (Base template = job default structure).
**Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.agent.do-task-delegation`, `astral.standards.debug-contract-gated`, `astral.standards.no-hardcoded-sets`
**Estimate: 5**

#### 2!: **Unsupported experience shape — toast, no emit - Hedy**

Owns operator-visible failure when experience is a legacy string or non-array: toast exactly `unsupported resume structure, please regenerate` on Base Resume / Print / Open HTML (and job artifact edit) paths; no HTML tab opens and no Experience-omitted resume is emitted. Does **not** migrate data. Does **not** own schema text or per-job HTML layout (siblings #1, #3). Sequencing: after #1 so “unsupported” matches the same contract.
**Citations:** `pattern.layers.import-discipline`, `astral.layers.ui-config-driven-business-logic`, `astral.layers.import-direction`, `astral.standards.in-scope-only`
**Estimate: 3**

#### 3: **Experience array UI + render/print parity - Katherine**

Owns Base Resume Content presenting/persisting the experience array as the base template, job artifact surfaces using the same structure by default, plus render/print emitting each role from the array. Does **not** own prompt/schema wording or the unsupported toast / no-emit path (siblings #1–#2). After #1; may land in parallel with #2 once the contract is fixed.
**Citations:** `pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.debug-contract-gated`
**Estimate: 5**

Monolith check: Functional scope lists 8 capabilities; 3 children intentionally split contract/agent vs unsupported toast/no-emit vs UI+emit so UAT can verify each failure mode separately.

---

## Original brief

For a long time we just had the experience as a long string, which logically parsed out which one was a job, etc.
Now, we need to support an array of experience elements, in the base_resume element, in the UI, in the response schema and craft candidate and job artifacts prompts content, in the agent component (to make sure it isn't validating needlessly), and in the render/print function for the resume.
We likewise need to support it in the job.job_data.artifacts element with the same structure by default as the candidate's base_resume content.

Do not support the old way, we are not migrating multiple candidates, just fail gracefully with a toast to say "unsupported resume structure, please regenerate".

### Comments

#### chuckles — 2026-08-12T19:13:04.266Z
@susan
1. For Base Resume Content editing, should experience be a structured per-job editor (fields per role), or is a single tab that round-trips valid JSON for the job array acceptable as long as string shapes toast and refuse to save?
2. On unsupported experience shape during Print / Open HTML: refuse the whole print with that toast (nothing opens), or still emit the rest of the resume with Experience omitted plus the toast?

---

_Implementation detail may live in git history on `origin/dev`._
