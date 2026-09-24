# AST-1588 — Support “job.artifacts.job_resume” and “job.artifacts.cover_letter”as artifacts

<!-- linear-archive: AST-1588 archived 2026-09-24 -->

## Linear archive (AST-1588)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1588/support-jobartifactsjob-resume-and-jobartifactscover-letteras  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Job resume and cover letter are still not real catalog artifacts. They remain bound to the job record (`job_data` pins/blobs and type-specific tracker/API helpers) instead of `ARTIFACT_CONFIG` plus the same generic read/write public surface candidate already uses for `base_resume`. This epic registers `job.artifacts.job_resume` and `job.artifacts.cover_letter`, persists them through the artifacts table via that shared catalog contract, extends the artifacts table so each version can cite **source artifact ids**, and when `job_resume` is written it records the then-current `base_resume` `artifact_id` as a source. It inventories every surface that still reads or writes these bodies on the job record and decommissions those former paths — without coat-check or new body-validation work until more of the catalog exists.

## Functional scope

1. **Catalog registration** — Add `job.artifacts.job_resume` and `job.artifacts.cover_letter` to `ARTIFACT_CONFIG` with the same metadata shape as the candidate pilot (entity, candidate-scoped flag, body shape, ingestion owner). The catalog is the sole authority for what those keys are.
2. **Same public read/write as candidate** — Tracker exposes the same kind of public functions candidate already has for catalog artifacts: a generic write that takes entity id + catalog artifact key + body (and source refs when provided), and a generic current-read that takes entity id + catalog artifact key. No tracker (or jobs API) public surface that is hard-wired to only job_resume or only cover_letter.
3. **Artifacts table source references** — Extend the `artifacts` table so each artifact version can store a list of source `artifact_id`s (the seed bodies that informed that write). Write-operative accepts and persists that list; reads can return it with the row. This is the table support for provenance — not coat-check, not full agent/task lineage beyond source artifact ids unless already present.
   1. THERE IS NO VALIDATION ON THE SOURCE REFERENCES YET.  We are doing an incremental add for artifacts, so until the catalog is more mature, validation will throw false positives.
4. **job_resume cites base_resume** — Whenever an operative `job.artifacts.job_resume` is written, the write records the then-current `candidate.artifacts.base_resume` `artifact_id` (from read-current / current row) as a source reference on the new job_resume version. If base_resume has no current row, record an empty source list rather than inventing an id (no coat-check fetch).
5. **Write with artifacts table** — Every operative persist of these two keys (UI save, finalize/body land, cancel/retire) goes through that generic tracker write → catalog write-operative → artifacts table. No supported write of those bodies as source of truth onto the job record.
6. **Read with artifacts table** — Every live/edit/display consumer that needs the current body for either key goes through that generic tracker current-read (or an equivalent catalog read-current wrapper). No supported read that treats `job_data.artifacts.*` (or type-specific overlay helpers) as source of truth for these keys.
7. **Inventory and decommission** — Inventory every current surface that reads or writes job_resume / cover_letter against the job record or type-specific helpers; rewire each to the generic catalog path or retire it. Remove parallel type-specific tracker/API entry points for these two keys.
8. **Explicit non-goals** — No coat-check registration or retirement. No new data-validation / body-shape gates beyond what the shared catalog write path already does for candidate. No promotion of sibling job blob keys (`notes`, `resume_content`, `proposed_answers`, `application_responses`, etc.). Cover letter source citation is not required this epic beyond storing an empty source list when written (product has not named cover-letter seeds). Full token-catalog / prompt-time auto-harvest of all artifact-typed tokens (Foundation [AST-1579](https://linear.app/astralcareermatch/issue/AST-1579/capture-deduped-source-artifact-id-array-on-derived-artifact-write)) is out of scope — this epic only ships table support plus the explicit job_resume → base_resume citation.

## Component scope

* `src/utils/config.py` — **modified** — register `job.artifacts.job_resume` and `job.artifacts.cover_letter` in `ARTIFACT_CONFIG`; retire or derive any parallel job-only editable-type authority so it cannot diverge; align JAR / body-replica config to cite catalog keys.
* `src/data/database.py` — **modified** — extend `artifacts` DDL/ensure for source-reference storage; `save_artifact` / get-current (and related) accept and return source artifact ids; header inventory updated; no unrelated schema churn.
* `src/core/tracker.py` — **modified** — add candidate-shaped generic public write and current-read for catalog keys on jobs; route these two keys through them; on job_resume write, resolve current base_resume artifact_id and pass it as a source; remove type-specific public save/hydrate helpers for job_resume / cover_letter; stop job-record SoT writes/reads for those keys.
* `src/ui/api/api_jobs.py` — **modified** — GET/PUT for these bodies call the generic tracker functions by catalog key (same pattern as candidate API → `save_candidate_data` / `get_candidate_current`); no new artifact-specific endpoint family.
* `src/core/agent.py` — **modified** — finalize / craft-land persist for these two keys calls the generic tracker write only (job_resume path must still result in base_resume cited as source).
* `src/core/builder.py` — **modified** — live resume/cover resolve uses generic tracker current-read by catalog key.
* `src/core/candidate.py` — **modified** — only if shared catalog resolve/write/read or base_resume current-id lookup must stay DRY with tracker; otherwise untouched.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** — load/save for job resume / cover letter follow the rewired generic API/key contract.
  * Make sure the UI reads CURRENT job_resume, not OPERATIVE job_resume.
* `src/ui/frontend/src/lib/recommendedJobReport.tsx` — **modified** — content checks follow rewired payload / key contract.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — only if tab/artifact_key wiring must cite catalog keys after config change.
* `canon/directives/draft/patt.artifacts.traceability.md` — **modified** — only a one-line alignment note that this epic lands source-artifact-id storage on `artifacts` for job_resume→base_resume; do not promote the draft to approved canon unless Archie asks.

## Technical scope

* `src/utils/config.py` — New `ARTIFACT_CONFIG` entries for both job keys (entity `job`, candidate-scoped true, body shapes into existing `BUILD_CONFIG["artifact_shapes"]`, ingestion owner tracker). Startup asserts include both keys beside the candidate pilot. Parallel job-only type tuples deleted or derived from catalog. JAR / body-replica maps cite catalog keys (or a 1:1 map to them), not bare type strings as authority.
* `src/data/database.py` — Add source-reference column (or equivalent JSON array of artifact_uuid strings) on `artifacts`; migrate/ensure existing DBs. Extend `save_artifact` to persist optional source ids with the new current row; extend get-current / get-by-uuid readers to return them. Update module header inventory. Exact column name is plan-child’s call under statute naming discipline.
* `src/core/tracker.py` — Public write: same calling shape as candidate’s catalog str-path save (job id + artifact key + body → resolve `ARTIFACT_CONFIG` → write-operative), plus optional source ids. Public current-read: same calling shape as `get_candidate_current`. For `job.artifacts.job_resume` writes, resolve the owning candidate’s current `candidate.artifacts.base_resume` row id and pass `[that_id]` (or `[]` if missing) as sources. Callers pass the key; tracker does not branch public API by job_resume vs cover_letter. Retire type-specific public helpers. Cancel/retire currents resolve via catalog key.
* `src/ui/api/api_jobs.py` — Handlers invoke the generic tracker write/read with the catalog key from config/route; do not introduce a second, job-resume-only or cover-letter-only public core API.
* `src/core/agent.py` — Finalize persist hooks call the generic tracker write with the catalog key for that hop (so job_resume land picks up base_resume source citation inside tracker write).
* `src/core/builder.py` — Resolve helpers call generic tracker current-read by catalog key; debug source labels name the catalog/table path, not job-record blob SoT.
* `src/core/candidate.py` — Optional shared helper for catalog resolve / current artifact_id lookup only if required for DRY.
* Frontend ArtifactEditor / recommendedJobReport / JAR modal — Adjust to catalog key + generic API contract; no new editor framework; no requirement to display source ids in UI this epic.
* `canon/directives/draft/patt.artifacts.traceability.md` — Optional one-line note that source-artifact-id persistence on `artifacts` starts with this epic’s job_resume→base_resume case.

## Architectural definition

**Patterns to reuse**

* `patt.artifact.manage-catalog` — register the two job keys; unknown keys fail fast. [draft](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.write-operative` — retire+insert current rows via the generic write; now also persists source artifact ids when provided. [draft](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.read-current` — current=1 body via the generic current-read; used to resolve base_resume id for citation and to serve editors. [draft](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifacts.traceability` — source `artifact_id[]` on derived writes; this epic lands the artifacts-table half for job_resume→base_resume only (not full agent/task lineage). [draft](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifacts.traceability.md>)
* `patt.artifacts.ui-consistency` — editor load/save follows catalog key + read-current / write-operative. [draft](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifacts.ui-consistency.md>)
* `pattern.config.config-block` — config remains SoT for the registry. [approved](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>)

**New patterns proposed**

* none — tracker mirrors the candidate public catalog read/write shape; source refs follow the existing traceability draft.

**Applicable statutes**

* `astral.config.config-source-of-truth` — catalog owns keys/metadata. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — no parallel hardcoded job artifact-type public APIs once catalog owns them. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.dry-and-focused-functions` — tracker public read/write match candidate; no per-artifact twin functions. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)
* `astral.standards.database-header-inventory` — artifacts table + new source column stay inventoried. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>)
* `astral.standards.data-raises-caller-logs` — data raises; tracker/API log. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>)
* `astral.layers.import-direction` — ui → core → data. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.standards.debug-contract-gated` — touched `debug=` surfaces keep Style D found/recorded (including found/recorded source ids on job_resume write when debug). [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>)
* `astral.standards.in-scope-only` — coat-check, validation expansion, non-named keys, and [AST-1579](https://linear.app/astralcareermatch/issue/AST-1579/capture-deduped-source-artifact-id-array-on-derived-artifact-write) token-harvest stay out. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)

**Dependency note:** Candidate pilot helpers (`save_candidate_data` catalog path, `get_candidate_current`) are the template tracker must mirror. If a needed helper shape is not yet on `origin/dev` at plan time, that child stays blockedBy the Foundation ticket that owns it rather than inventing a job-only API.

## Acceptance criteria

 1. `ARTIFACT_CONFIG` contains `job.artifacts.job_resume` and `job.artifacts.cover_letter` with complete metadata alongside the candidate pilot key.
 2. Tracker exposes generic public write and current-read functions with the same calling shape as candidate’s catalog artifact save and `get_candidate_current` (entity id + artifact key; no per-artifact public function).
 3. The `artifacts` table stores source artifact id references on each version; new writes can persist them and current/by-id reads can return them.
 4. After an operative `job.artifacts.job_resume` write, the new row’s source references include the candidate’s then-current `base_resume` `artifact_id` when one exists (empty list when none).
 5. UI save and agent finalize land for both keys persist via that generic write into the artifacts table; no supported path writes those bodies as SoT onto the job record.
 6. UI load, jobs GET, and builder live build for both keys obtain bodies via that generic current-read; they do not treat `job_data.artifacts.job_resume` / `cover_letter` (or type-specific overlay helpers) as SoT.
 7. A written inventory lists every pre-change production surface that read or wrote these keys; each row is marked rewired or retired.
 8. Type-specific public tracker/API entry points for only job_resume or only cover_letter are gone (or thin shims that only forward to the generic functions, removed in the same epic).
 9. Coat-check registration and new body-validation gates are not introduced for these keys.
10. Sibling job blob keys (`notes`, `resume_content`, `proposed_answers`, `application_responses`) remain out of `ARTIFACT_CONFIG`.

## Open questions

none

## Proposed child tickets

#### 1!!: **Register job.artifacts.job_resume and job.artifacts.cover_letter - Ada**

Owns catalog registration only: add both keys to `ARTIFACT_CONFIG`, align JAR / body-replica citations to those keys, and eliminate independent job-only editable-type authority (delete or derive). Does not add tracker public functions, schema, or rewire product call sites beyond config asserts. Blocks #3.
**Citations:** `patt.artifact.manage-catalog`; `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`
**Scope:** `src/utils/config.py` — **modified** — register `job.artifacts.job_resume` and `job.artifacts.cover_letter` in `ARTIFACT_CONFIG`; retire or derive any parallel job-only editable-type authority so it cannot diverge; align JAR / body-replica config to cite catalog keys. `src/utils/config.py` — New `ARTIFACT_CONFIG` entries for both job keys (entity `job`, candidate-scoped true, body shapes into existing `BUILD_CONFIG["artifact_shapes"]`, ingestion owner tracker). Startup asserts include both keys beside the candidate pilot. Parallel job-only type tuples deleted or derived from catalog. JAR / body-replica maps cite catalog keys (or a 1:1 map to them), not bare type strings as authority.
**Estimate: 2**

#### 2!!: **Artifacts table source references - Katherine**

Owns data-layer support for source artifact ids on `artifacts` versions: DDL/ensure migration, `save_artifact` persists optional source id list, get-current / get-by-uuid return it, header inventory updated. Does not register catalog keys (#1) or wire tracker job_resume citation (#3). Blocks #3.
**Citations:** `patt.artifacts.traceability`; `patt.artifact.write-operative`; `astral.standards.database-header-inventory`; `astral.standards.data-raises-caller-logs`
**Scope:** `src/data/database.py` — **modified** — extend `artifacts` DDL/ensure for source-reference storage; `save_artifact` / get-current (and related) accept and return source artifact ids; header inventory updated; no unrelated schema churn. `canon/directives/draft/patt.artifacts.traceability.md` — **modified** — only a one-line alignment note that this epic lands source-artifact-id storage on `artifacts` for job_resume→base_resume; do not promote the draft to approved canon unless Archie asks. `src/data/database.py` — Add source-reference column (or equivalent JSON array of artifact_uuid strings) on `artifacts`; migrate/ensure existing DBs. Extend `save_artifact` to persist optional source ids with the new current row; extend get-current / get-by-uuid readers to return them. Update module header inventory. Exact column name is plan-child’s call under statute naming discipline. `canon/directives/draft/patt.artifacts.traceability.md` — Optional one-line note that source-artifact-id persistence on `artifacts` starts with this epic’s job_resume→base_resume case.
**Estimate: 3**

#### 3!: **Tracker generic catalog write/read + job keys + base_resume citation - Hedy**

After #1 and #2: give tracker the same public catalog write and current-read shape candidate already has (entity id + artifact key; no specificity to which artifact). Route job_resume / cover_letter operative writes and backend reads through those generics into the artifacts table. On every job_resume write, cite the then-current base_resume artifact_id as a source (empty list if none). Remove type-specific public save helpers for these keys. Does not own builder/UI consumer inventory (sibling #4). Blocks #4.
**Citations:** `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifacts.traceability`; `patt.artifact.manage-catalog`; `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`; `astral.layers.import-direction`
**Scope:** `src/core/tracker.py` — **modified** — add candidate-shaped generic public write and current-read for catalog keys on jobs; route these two keys through them; on job_resume write, resolve current base_resume artifact_id and pass it as a source; remove type-specific public save/hydrate helpers for job_resume / cover_letter; stop job-record SoT writes/reads for those keys. `src/ui/api/api_jobs.py` — **modified** — GET/PUT for these bodies call the generic tracker functions by catalog key (same pattern as candidate API → `save_candidate_data` / `get_candidate_current`); no new artifact-specific endpoint family. `src/core/agent.py` — **modified** — finalize / craft-land persist for these two keys calls the generic tracker write only (job_resume path must still result in base_resume cited as source). `src/core/candidate.py` — **modified** — only if shared catalog resolve/write/read or base_resume current-id lookup must stay DRY with tracker; otherwise untouched. `src/core/tracker.py` — Public write: same calling shape as candidate’s catalog str-path save, plus optional source ids. Public current-read: same calling shape as `get_candidate_current`. For `job.artifacts.job_resume` writes, resolve the owning candidate’s current `candidate.artifacts.base_resume` row id and pass `[that_id]` (or `[]` if missing) as sources. Retire type-specific public helpers. `src/ui/api/api_jobs.py` — Handlers invoke the generic tracker write/read with the catalog key from config/route. `src/core/agent.py` — Finalize persist hooks call the generic tracker write with the catalog key for that hop. `src/core/candidate.py` — Optional shared helper for catalog resolve / current artifact_id lookup only if required for DRY.
**Estimate: 5**

#### 4: **Inventory and rewire remaining job artifact consumers - Ada**

After #3: inventory every remaining surface that still reads job_resume / cover_letter via job-record or type-specific paths; rewire builder and ArtifactEditor / JAR / recommended-report onto the generic tracker current-read / API contract; finish decommission of leftover type-specific client assumptions. Does not re-own tracker/API public functions or schema (#2/#3). No coat-check or validation. No requirement to surface source ids in UI.
**Citations:** `patt.artifact.read-current`; `patt.artifacts.ui-consistency`; `astral.standards.debug-contract-gated`; `astral.layers.import-direction`; `astral.standards.in-scope-only`
**Scope:** `src/core/builder.py` — **modified** — live resume/cover resolve uses generic tracker current-read by catalog key. `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** — load/save for job resume / cover letter follow the rewired generic API/key contract. `src/ui/frontend/src/lib/recommendedJobReport.tsx` — **modified** — content checks follow rewired payload / key contract. `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — only if tab/artifact_key wiring must cite catalog keys after config change. `src/core/builder.py` — Resolve helpers call generic tracker current-read by catalog key; debug source labels name the catalog/table path, not job-record blob SoT. Frontend ArtifactEditor / recommendedJobReport / JAR modal — Adjust to catalog key + generic API contract; no new editor framework; no requirement to display source ids in UI this epic.
**Estimate: 3**

---

## Original brief

implementation from end to end:

Config to write and then read with artifacts table, plus full decommission of former reads and rights to the record in job table.

Include an inventory of current surfaces to read job_resume, and centralize on the new read and write patterns under patt.artifacts.*.

We are not considering coat check logic or any data validation until we have more of the artifact catalogue built out.

### Comments

#### chuckles — 2026-09-06T23:56:08.448Z
[check-linear] Discussion — filed AST-1601 related to AST-1588, assignee Susan (@susan)

#### susan — 2026-09-06T23:54:18.844Z
@chuckles We need to rip out this ticket's changes because it was supposed to be an identical pattern to what candidate does, but we are still using functions like JOB_ARTIFACT_AGENT_DATA_PIN or whatever, and that is not just wrong, but ABJECTLY CONTRARY TO THE POINT OF THE NEW PATTERNS TO BEGIN WITH.  Create a new ticket, relate this one, and set it to discussion assigned to me.

#### chuckles — 2026-09-06T16:25:04.356Z
[fix-intake] batch closed — AST-1599 already filed; AST-1600 at Discussion (Susan). Parent stays User Testing.

#### susan — 2026-09-06T16:19:19.315Z
\[bug\]

The base resume and cover letter are not persisting in the artifact table, despite the task successfully completing.  Wasn't this one of the acceptance criteria?

#### susan — 2026-09-06T15:37:00.442Z
\[bug\]

Artifacts generated for a recommended job, all tasks completed successfully.  For some reason, the job modal for that job no longer shows the resume and cover letter, just a (wrong and stupid) message that there was no base resume to reference:

\`**SummaryAnalysisArtifactsDiscussion**

### Source base resume

No pinned base resume for this build\`

There was no request to change UI features or functionally beyond the support of the artifact table as the source for the job resume and cover letter. Do not reference the sources on the job modal.

#### chuckles — 2026-09-04T22:10:24.730Z
AST-1591 REVIEW — merge-child blocked; recalling Katherine for pull-merge commit on sub tip.

#### chuckles — 2026-09-04T22:07:28.200Z
AST-1591 REVIEW — Radia: sibling AST-1590 tests on publish ref need merge-child order before UT.

#### susan — 2026-09-04T21:35:40.474Z
we also need to update the artifacts table to support source references, so that when the job_resume is written, the base_resume artifact_id is cited as a source.

#### chuckles — 2026-09-04T21:21:07.671Z
[check-linear] Todo — definition rewritten: not-yet artifacts + candidate-shaped generic tracker read/write (@susan)

#### susan — 2026-09-04T18:55:10.013Z
I believe that this is almost entirely wrong.

We do not already persist job resume and cover letter in artifacts.  This is the problem.

It also seems like you are planning to build slightly different endpoints in tracker than we made in candidate for base resume. This is incorrect. Tracker and candidate should have the same public job functions for read and write as candidate has, with no specificity to which artifact is being handled. 

@chuckles

---

_Implementation detail may live in git history on `origin/dev`._
