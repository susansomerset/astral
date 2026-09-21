# AST-1345 — Clarify candidate_data.artifacts.base_resume.experience node
**Component:** artifacts  
**Children:** AST-1349, AST-1350, AST-1351  
**Linear archived:** AST-1345 2026-08-31; AST-1349 2026-08-31; AST-1350 2026-08-31; AST-1351 2026-08-31

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-12 16:56 | AST-1349 | docs | `2342855c1` | docs(AST-1349): plan — experience array contract schema prompts agent |
| 2026-08-12 16:59 | AST-1349 | docs | `e49196d70` | docs(AST-1349): Joan validate — APPROVED experience contract |
| 2026-08-12 17:01 | AST-1349 | docs | `1d7d675f3` | docs(AST-1349): review stub tip after docs push |
| 2026-08-12 17:01 | AST-1349 | code | `66a29148a` | code(AST-1349): experience array prompts and contract-only validate |
| 2026-08-12 17:01 | AST-1349 | docs | `e8c4066c8` | docs(AST-1349): review stub tip SHA |
| 2026-08-12 17:08 | AST-1349 | test | `99ffa38cd` | test(AST-1349): experience array contract prompts and validate coverage |
| 2026-08-12 17:08 | AST-1349 | merge-tests | `bab06e658` | merge-tests(AST-1349): origin/tests 99ffa38cd23e7ee2dacf28391a29a44fba4dbfa8 |
| 2026-08-12 17:12 | AST-1349 | docs | `0b595a38e` | docs(AST-1349): Radia review — CLEAN experience array contract |
| 2026-08-12 17:16 | AST-1350 | docs | `8984d14e0` | docs(AST-1350): plan — unsupported experience shape toast no emit |
| 2026-08-12 17:17 | AST-1350 | docs | `c53f85eee` | docs(AST-1350): Joan validate — APPROVED |
| 2026-08-12 17:19 | AST-1350 | code | `3b30b01bc` | code(AST-1350): toast unsupported shape — no HTML tab |
| 2026-08-12 17:19 | AST-1350 | code | `83ca56198` | code(AST-1350): refuse unsupported experience shape before emit |
| 2026-08-12 17:20 | AST-1350 | docs | `0e5474ead` | docs(AST-1350): review stub after build |
| 2026-08-12 17:23 | AST-1345/1350 | sync | `4d42773c0` | sync(publish-ref): origin/sub/AST-1345/AST-1350-unsupported-experience-shape-toast-no-emit |
| 2026-08-12 17:23 | AST-1350 | test | `22925f507` | test(AST-1350): unsupported experience shape toast and no-emit coverage |
| 2026-08-12 17:23 | AST-1350 | merge-tests | `81463c4c8` | merge-tests(AST-1350): origin/tests 22925f5072c9822a5f60902ae749aa2367139abe |
| 2026-08-12 17:26 | AST-1350 | docs | `5be8ed08c` | docs(AST-1350): Radia review — clean |
| 2026-08-12 17:27 | AST-1350 | resolve | `5550df342` | resolve(AST-1350): — clean |
| 2026-08-12 17:27 | AST-1350 | merge-resume | `6908cdeeb` | merge-resume(AST-1350): origin/ftr into sub for §9a |
| 2026-08-12 17:28 | AST-1350 | resolve | `deff7b984` | resolve(AST-1350): — §9a dry-run note hygiene |
| 2026-08-12 17:32 | AST-1351 | docs | `a6e36b190` | docs(AST-1351): plan — experience array UI + render/print parity |
| 2026-08-12 17:33 | AST-1351 | docs | `c72c40944` | docs(AST-1351): Joan validate — array UI + emit parity APPROVED |
| 2026-08-12 17:35 | AST-1351 | code | `eac6612ab` | code(AST-1351): experience array UI + emit Style D parity |
| 2026-08-12 17:36 | AST-1351 | docs | `977e291d9` | docs(AST-1351): Review stub after build |
| 2026-08-12 17:39 | AST-1351 | merge-tests | `863871fb4` | merge-tests(AST-1351): origin/tests 88ddcc5b70803aef901ced1acde9e5f32089a510 |
| 2026-08-12 17:39 | AST-1351 | test | `88ddcc5b7` | test(AST-1351): experience job UI editor and render/print Style D coverage |
| 2026-08-12 17:42 | AST-1351 | docs | `96caa4a06` | docs(AST-1351): Radia review — experience job UI emit parity CLEAN |
| 2026-08-31 14:13 | AST-1349 | docs | `5f2e0e220` | docs(AST-1349): archive Linear issue content |
| 2026-08-31 14:13 | AST-1350 | docs | `976b83e5b` | docs(AST-1350): archive Linear issue content |
| 2026-08-31 14:13 | AST-1351 | docs | `43589041c` | docs(AST-1351): archive Linear issue content |
| 2026-08-31 14:18 | AST-1345 | docs | `d6a99888c` | docs(AST-1345): archive Linear issue content |

_One row of cross-ticket noise excluded from the table above: `test(AST-1489): bug-repro — print-before-PUT page-break auto-persist` (2026-08-26), a later F29 family commit whose body cites AST-1350 as a related pattern._

**Embedded-bug discovery (important — not part of this family, preserved rather than duplicated or lost):** `ast-1349-…md` and `ast-1351-…md` each carried an appended `## Bug: AST-1381` and `## Bug: AST-1382` section. Those two tickets' **real** Linear parent is **AST-1362** ("Base Resume Issues") — a different epic that also lives in this `artifacts/` folder (planned as a later family in this consolidation) — not AST-1345. Each host file explicitly owns only half of each bug (ast-1349 the schema/prompt/agent-validate half; ast-1351 the UI/emit/print half); thin standalone `ast-1381-*.md` / `ast-1382-*.md` files exist separately in this folder with no build narrative. That content has been left untouched in place for the AST-1362 family's own future archive (not reproduced here) — a reconciliation note recording exactly where both halves live has been saved to the session scratchpad so nothing is lost when `ast-1349`/`ast-1351` are flagged for deletion below.

`ast-1350-…md` separately carried an appended `## Bug: AST-1545` and `## Bug: AST-1546` section. Those two tickets' real Linear parent is **AST-1542** ("Erroneous error occurs for print buttons"), which lives in **`docs/features/interface/`** — a different feature folder entirely, out of this session's scope. Thin standalone `interface/ast-1545-*.md` / `interface/ast-1546-*.md` files exist (Description/Scope/AC/Boundaries only — no build/review narrative); the full build+review narrative exists **only** embedded in `ast-1350`. Since AST-1542 will never be built as its own family in this artifacts-folder consolidation, and since deleting `ast-1350` would otherwise permanently lose that narrative, it is preserved in full below (under AST-1350's own section, clearly marked as foreign content) rather than left to vanish. `docs/features/interface/` itself has not been touched.

## Epic — AST-1345
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1345/clarify-candidate-dataartifactsbase-resumeexperience-node · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / 8 · Blocked by / blocks / related: —_

### Purpose

Operators and agents still meet `candidate_data.artifacts.base_resume.experience` (and the matching job-artifact experience node) as either a long prose string or a structured job list. The product needs one wire shape only: an ordered array of experience jobs, honored end-to-end in craft/parse schemas and prompts, agent validation, the Base Resume / job artifact UI, and resume render/print. Base experience is the template; job artifacts use the same structure by default. Legacy string (or other non-array) blobs are not migrated — they fail with a regenerate toast and must not produce a printable resume missing Experience.

### Functional scope

* Candidate `artifacts.base_resume.experience` is an ordered array of job objects (company, title, dates, location, accomplishments) — not a single prose string.
* Base experience is the template for job: job `job_data.artifacts` resume content uses the same experience array structure by default (not a separate job-only shape on Base).
* Craft/parse/finalize response schemas and candidate + job craft prompts describe and require that array shape for experience.
* The agent validates the shared array contract without extra needless checks that reject valid array payloads or re-impose string-era rules.
* The Base Resume Content UI presents and persists experience as that array (the base template); job artifact surfaces that edit experience use the same structure.
* Resume render and print emit each experience job from the array (role metadata + accomplishments), not one merged prose blob.
* When experience is a legacy string or any non-array shape, show toast exactly: `unsupported resume structure, please regenerate` — do not open Print / Open HTML and do not emit a partial resume with Experience omitted. No automatic migration of existing candidates.
* When `debug=True` on touched craft/parse/tailor or persist paths that read experience, debug output records what experience shape was found and what was recorded per job (Style D index + detail), not only pass/fail counts.

### Architectural definition

* **Patterns to reuse** — `pattern.config.config-block` (experience wire shape and schema literals stay in config); `pattern.layers.import-discipline` (UI renders resolved shapes; core owns validate/persist/emit; no UI→data shortcuts).
* **New patterns proposed** — none (reuse the existing experience job-array contract from the AST-994 epic; this epic closes remaining surfaces and the unsupported-shape operator path).
* **Applicable statutes** — `astral.config.config-source-of-truth`; `astral.agent.do-task-delegation`; `astral.standards.debug-contract-gated`; `astral.layers.import-direction`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`.

### Boundaries

* Does **not** treat Base Resume experience editing as job-specific tailoring — Base is the template; job reuses the same structure.
* Does **not** migrate or rewrite existing string-shaped experience blobs into the array.
* Does **not** invent a second experience schema for job vs candidate.
* Does **not** change cover-letter HTML, signature, or from-block work.
* Does **not** reopen AST-993 golden-fixture education/skills/header chrome beyond what render already does for job-array experience.
* Does **not** add multi-candidate backfill or admin bulk repair tools.
* Does **not** open or emit Print / Open HTML for an unsupported experience shape (toast only — no Experience-omitted resume).
* Must not break Highlights / resume_structure catalog work already landed (experience remains the `experience_detail` / `experience_jobs` body).
* Adjacent in-flight Print chrome (AST-1314 family) stays out of scope except that print must honor the array contract and the unsupported toast (no tab) when experience is unusable.

### Acceptance criteria

1. After craft/parse (or load of a saved base resume) for a multi-job resume, `artifacts.base_resume.experience` is an ordered array; each element exposes company, title, dates, location, and accomplishments observable in Base Resume Content / parse JSON.
2. Job artifact resume content that carries experience uses the same array element shape as the candidate base resume (same keys/requiredness by default); Base remains the template, not a job-tailored editor.
3. Craft/parse/finalize schemas and the related candidate + job prompts accept and describe experience only as that array — string experience is not a valid success path.
4. Agent handling of experience does not reject a valid job array with leftover string-era validation, and does not require fields beyond the shared contract.
5. In the Base Resume Content UI, Susan can view and save experience as the job-array template (not as one undifferentiated prose field that round-trips as a string).
6. Render and Print of a base (and job, where applicable) resume show each experience job with role metadata and accomplishments from the array — not one merged experience string.
7. Opening or printing a resume whose experience is still a string (or other non-array shape) shows toast text `unsupported resume structure, please regenerate`, opens no HTML tab, and does not emit a resume with Experience omitted.
8. When `debug=True` on touched experience-reading hops/persist paths, logs show found/recorded experience shape and per-job detail (Style D), not only summaries.

### Dependencies and blockers

none (prior AST-994 / AST-996–998 job-array work is already on `dev`; this epic closes remaining surfaces and the explicit unsupported-shape toast). Adjacent AST-1314 Print UI is not a blocker.

### Open questions

none

### Proposed child tickets

**1!: Experience array contract — schema, prompts, agent — Ada** — Owns the shared experience job-array wire shape in craft/parse/finalize response schemas and candidate + job craft prompts; tightens agent validation to that contract only (no string success path, no needless extra checks). Does **not** own UI toast chrome or HTML emit (siblings #2–#3). After #1, schemas/prompts/agent agree on one array shape for candidate and job (Base template = job default structure).
**Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.agent.do-task-delegation`, `astral.standards.debug-contract-gated`, `astral.standards.no-hardcoded-sets`
**Estimate: 5**

**2!: Unsupported experience shape — toast, no emit — Hedy** — Owns operator-visible failure when experience is a legacy string or non-array: toast exactly `unsupported resume structure, please regenerate` on Base Resume / Print / Open HTML (and job artifact edit) paths; no HTML tab opens and no Experience-omitted resume is emitted. Does **not** migrate data. Does **not** own schema text or per-job HTML layout (siblings #1, #3). Sequencing: after #1 so "unsupported" matches the same contract.
**Citations:** `pattern.layers.import-discipline`, `astral.layers.ui-config-driven-business-logic`, `astral.layers.import-direction`, `astral.standards.in-scope-only`
**Estimate: 3**

**3: Experience array UI + render/print parity — Katherine** — Owns Base Resume Content presenting/persisting the experience array as the base template, job artifact surfaces using the same structure by default, plus render/print emitting each role from the array. Does **not** own prompt/schema wording or the unsupported toast / no-emit path (siblings #1–#2). After #1; may land in parallel with #2 once the contract is fixed.
**Citations:** `pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.debug-contract-gated`
**Estimate: 5**

Monolith check: Functional scope lists 8 capabilities; 3 children intentionally split contract/agent vs unsupported toast/no-emit vs UI+emit so UAT can verify each failure mode separately.

### Original brief

For a long time we just had the experience as a long string, which logically parsed out which one was a job, etc.
Now, we need to support an array of experience elements, in the base_resume element, in the UI, in the response schema and craft candidate and job artifacts prompts content, in the agent component (to make sure it isn't validating needlessly), and in the render/print function for the resume.
We likewise need to support it in the job.job_data.artifacts element with the same structure by default as the candidate's base_resume content.

Do not support the old way, we are not migrating multiple candidates, just fail gracefully with a toast to say "unsupported resume structure, please regenerate".

#### Comments

##### chuckles — 2026-08-12T19:13:04.266Z
@susan
1. For Base Resume Content editing, should experience be a structured per-job editor (fields per role), or is a single tab that round-trips valid JSON for the job array acceptable as long as string shapes toast and refuse to save?
2. On unsupported experience shape during Print / Open HTML: refuse the whole print with that toast (nothing opens), or still emit the rest of the resume with Experience omitted plus the toast?

### Files changed (plan vs actual)

_No direct product commit trail on the parent — the epic worktree carries only the epic-registry / archive commits. Implementation landed entirely via the three sub-issues below._

## Sub-issues

### AST-1349 — Experience array contract — schema, prompts, agent
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1349/experience-array-contract-schema-prompts-agent-clarify-candidate · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / 5 · Blocked by / blocks / related: parent: AST-1345; blocks: AST-1351; blocks: AST-1350_

#### What this implements

Owns the shared experience job-array wire shape in craft/parse/finalize response schemas and candidate + job craft prompts; tightens agent validation to that contract only (no string success path, no needless extra checks). Does **not** own UI toast chrome or HTML emit (siblings). After this child, schemas/prompts/agent agree on one array shape for candidate and job (Base template = job default structure).

#### Acceptance criteria

1. [x] After craft/parse (or load of a saved base resume) for a multi-job resume, `artifacts.base_resume.experience` is an ordered array; each element exposes company, title, dates, location, and accomplishments observable in Base Resume Content / parse JSON.
2. [x] Job artifact resume content that carries experience uses the same array element shape as the candidate base resume (same keys/requiredness by default); Base remains the template, not a job-tailored editor.
3. [x] Craft/parse/finalize schemas and the related candidate + job prompts accept and describe experience only as that array — string experience is not a valid success path.
4. [x] Agent handling of experience does not reject a valid job array with leftover string-era validation, and does not require fields beyond the shared contract.
5. [x] When `debug=True` on touched experience-reading hops/persist paths, logs show found/recorded experience shape and per-job detail (Style D), not only summaries.

#### Boundaries

Does not own UI toast chrome or HTML emit (siblings Unsupported experience shape; Experience array UI + render/print parity).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Audit/lock craft/parse/finalize (+ `BUILD_CONFIG` resume_content) experience fields on the shared `_EXPERIENCE_JOB_*` objects; no parallel string experience schema | utils |
| `data/admin/agent_task.json` | Rewrite `craft_resume_base` `### experience` (and conflicting lines) to job-array only; update job craft `user_prompt`s so experience is array-only (remove "prose string or job array"); keep `simple_resume_parse` array wording consistent | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Whole-file `cp` twin | docs |
| `src/core/candidate.py` | Draft normalize/validate: reject non-array experience as failure (no string success path); validate only the shared five keys; drop needless `experience_detail` jargon; Style D found/recorded when `debug=True` | core |
| `src/core/agent.py` | Keep finalize/draft pin + Style D hooks on experience-reading hops; do not add string-era coerce; schema validation remains the gate for craft/parse/finalize list+`items_schema` | core |

**As-is (why this ticket exists):** `TASK_CONFIG` craft/parse/finalize schemas already used `_EXPERIENCE_JOB_ARRAY_FIELD` / `_OPTIONAL`, and `simple_resume_parse` prompt already taught a job array — but `craft_resume_base` `cache_prompt` `### experience` still taught blank-line prose roles (`COMPANY NAME` / `Title | dates | Location`), and `draft_job_resume` `user_prompt` still said experience may stay "a prose string or job array." That re-authorized the string success path parent AC forbids.

#### Contract (shared — do not redefine)

Each experience job object (config `_EXPERIENCE_JOB_ITEM_SCHEMA`): `company` (str, required), `title` (str, required), `dates` (str, required, freeform), `location` (str, required, `""` when none), `accomplishments` (str, required, one text block per role — later widened to `string[]` by the embedded AST-1381 fix, see the reconciliation note at the top of this archive).

⚠️ **Decision:** One shared items_schema object identity for candidate craft/parse (required list) and job finalize (optional list). Do not invent a second job-only experience schema. Base template = job default structure. ⚠️ **Decision:** No new `highlights` field on experience jobs — accomplishments is the single body block (AST-997 pin policy for job hops stays).

#### Stage 1–5 — Config lock, candidate prompts, job prompts, agent validation, UAT fixture twin

Confirm-only Stage 1 (schema names already wired on tip from prior AST-994 work) plus prompt rewrites: `craft_resume_base` `### experience` replaced with ordered-JSON-array-of-five-keys instructions (no prose blocks), LinkedIn-enrichment line narrowed to professional-summary only, QUALITY CHECKLIST no longer implies experience is a non-empty string; `simple_resume_parse` confirmed already aligned. Job prompts (`draft_job_resume`, `finalize_job_resume`, `advise_job_resume`, `check_job_resume`) retarget any "prose string or job array" language to array-only, with an explicit rule that draft may reframe/reorder `accomplishments` for the target job but must never mutate `company`/`title`/`dates`/`location` from base, and must never emit experience as a prose string. Agent: `validate_draft_job_resume_payload` for `key == "experience"` accepts a non-empty job array, rejects any string/non-array shape as a hard failure (not soft-accepted), and uses a contract-facing error `Section 'experience' must be a job array` instead of UI `experience_detail` jargon; `pin_experience_job_facts_from_base` match-by-`(company, title)` (AST-997) kept unchanged; existing Style D `debug_experience_jobs` hooks kept, not duplicated. AST-756 fixture twin re-synced via whole-file `cp`.

⚠️ **Decision:** Prompt text is the durable Archie catalog — commit the JSON, do not hand-edit production DB.

#### Plan review — Joan (PROCEED)

**acceptable** — assignee is Ada (not Joan); Chuckles spawned this pass explicitly; no review block. **acceptable** — Stage 1 may be largely confirm-only on tip; plan correctly limits edits to drift-only fixes. **acceptable** — component tests asserting the old `"prose string or job array"` / `experience_detail` error text are out of plan scope (tests ban); Betty manifest expected to flip during qa-child after build.

#### Radia review — code-rubric.v1, CLEAN

Full 64-statute sweep (product commit `66a29148`, four planned files): all conforms/not-applicable, no violations. Plan adherence confirmed stage-by-stage: Stage 1 confirm-only (no `config.py` diff — schema already correctly wired); Stage 2 `craft_resume_base` prompt rewritten array-only; Stage 3 job prompts retargeted; Stage 4 draft validate rejects non-array experience with the contract-facing message; Stage 5 fixture twin byte-identity test passes.

**Advisory (not blocking):** the three-dot diff also carries `test(AST-1352)` artifacts (unrelated `astral_artifacts` database tests/bible/conftest lines) from an `origin/tests` merge commit — parent is AST-1340, not AST-1345; pipeline-legal per Betty's one-merge-tests-SHA rule, does not affect AST-1349's own ACs; filter the product diff to the single `66a29148` commit if that noise is distracting.

**What's solid:** closes the documented as-is gap — Judith craft and draft prompts no longer re-authorize prose-string experience; draft validate error text matches plan and Betty's flipped AST-997/AST-1270 assertions; shared five-key schema identity preserved without a parallel job-only schema; AST-756 twin discipline (`cp` + `cmp`) enforced in tests.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `data/admin/agent_task.json` + `docs/uat-fixtures/AST-756/expected-agent_task.json` | Candidate + job craft prompt rewrites, array-only; fixture twin resync | `66a29148a` (with `candidate.py`) — +94/-88 across four files |
| ✓ | `src/core/candidate.py` | Draft validate: non-array experience hard-fails; contract-facing error message | `66a29148a` — see above |
| | _tests_ | experience array contract prompts + validate coverage | `99ffa38cd`; bible per Betty manifest |

### AST-1350 — Unsupported experience shape — toast, no emit
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1350/unsupported-experience-shape-toast-no-emit-clarify-candidate · Status at archive: Archive · Project: Astral Artifacts · Assignee: hedy · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1345_

#### What this implements

Owns the operator-visible failure path when `experience` is still a legacy string or any other non-array shape: toast exactly `unsupported resume structure, please regenerate`, open no HTML tab, and do not emit a printable resume with Experience omitted. Core refuses emit; UI surfaces the core error string. Does **not** migrate data, rewrite schemas/prompts (AST-1349), or own happy-path array UI/render layout (AST-1351).

#### Acceptance criteria

- [X] 7. Opening or printing a resume whose experience is still a string (or other non-array shape) shows toast text `unsupported resume structure, please regenerate`, opens no HTML tab, and does not emit a resume with Experience omitted.

#### Boundaries

Does not migrate data. Does not own schema text or per-job HTML layout (siblings).

#### UAT fitness (plan doc)

**Correct outcome:** operator clicks Print / Open HTML / Print Resume on a resume whose `experience` is a string (or other non-array); they see the exact toast, no new HTML tab (and no printable Experience-omitted document), and must regenerate to get a valid job-array experience before print works. **Wrong fix rejected:** UI-only toast while `builder` still skips leftover prose and returns HTML without Experience — that still emits the forbidden Experience-omitted resume; client-side shape checks alone also fail layer rules and leave direct `/candidate/resume/…` hits uncovered.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add exact operator toast/error string under `BUILD_CONFIG` (single source) | utils |
| `src/core/builder.py` | Shared gate: if `experience` key present and not `is_experience_job_array`, raise `ValueError` with that config string before any HTML emit; remove Experience leftover-prose skip-as-success path | core |
| `src/ui/api/api_resume_html.py` | Map the unsupported `ValueError` to HTTP 400 + `{"error": "<exact message>"}` | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Keep fetch-then-blob Print; toast exact `error` string; no tab on failure | ui |
| `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | Same for Open HTML | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Print Resume: fetch `/candidate/resume/<job_id>` first (like Base Resume); on non-OK toast exact `error`, do not open; on OK open blob/tab | ui |

**As-is:** `_emit_body_sections_html` skipped non-array `experience` as `skipped — leftover prose` and still returned full HTML — Experience omitted. Base Resume / Session Open HTML toasted whatever the API returned; JAR Print Resume `window.open`ed the URL blindly (tab opened even on JSON error).

#### Contract (reuse — do not redefine)

Unsupported when the resume content dict has key `"experience"` and `is_experience_job_array(value)` is false: key absent → allow emit; `[]` or list of dicts → allow; `str` (incl. legacy prose) → refuse; `dict`/list-of-non-dicts/other → refuse. Exact operator text: `unsupported resume structure, please regenerate`.

⚠️ **Decision:** Gate in core builder before HTML assembly (not React-only) — covers every route that calls `build_base_resume` / `build_resume` / `build_session_base_resume`. ⚠️ **Decision:** Check the content dict before filter/emit so a non-array value cannot be dropped then silently omitted.

#### Stage 1 & 2 — Core no-emit gate + API/UI toast

Private helper `_reject_unsupported_experience_shape(content)`: no-op when `experience` absent or a valid job array; else raises `ValueError(BUILD_CONFIG["unsupported_resume_structure_message"])`. Called in `build_base_resume` (on raw `br`, before filter/emit), `build_resume_from_job` (on `_resolve_resume_sections` output), and `build_session_base_resume` (on the in-memory dict) — all before filter/emit. Defense in depth: `_emit_body_sections_html`'s `experience_detail` branch raises the same error instead of silently `continue`-skipping non-array experience. `api_resume_html.py` maps that specific `ValueError` string to 400 JSON (other `ValueError`s keep their existing 404 mapping). Three UI surfaces (Base Resume Print, Session Open HTML, JAR Print Resume) all fetch-then-validate before opening any tab; JAR's `onPrintResume` in particular was rewritten from a blind `window.open` into the same fetch-first pattern Base Resume already used.

#### Plan review — Joan (PROCEED)

**acceptable** — assignee is Hedy (not Joan); Chuckles-spawned pass. **acceptable** — `## UAT fitness` correctly frames AC7 vs symptom-only fixes. **acceptable** — as-is verified on tip: `_emit_body_sections_html` still silently skipped non-array experience; `api_resume_html` mapped all `ValueError` to 404; JAR still blind `window.open`ed. **acceptable** — `MaterialsPreviewModal.tsx` loads via iframe without fetch-first but appears unused; core gate still blocks Experience-omitted emit if wired later (out of this ticket's three named surfaces).

#### Radia review — code-rubric.v1, CLEAN

Full 64-statute sweep (product commits `83ca5619` + `3b30b01b`, four files): all conforms/not-applicable. Contract table verified: key absent → allow; `[]`/list-of-dicts → allow; string/dict/non-array-list → refuse with exact message.

**Advisories (all non-blocking, no action on this ticket):** the three-dot diff vs `origin/dev` is ftr-aggregate noise carrying unrelated sibling epic work — filter to the two product commits for review. `test(AST-1353)` rode along before `merge-tests(AST-1350)` — pipeline-legal, unrelated to AC7. A legacy builder fixture (`TestBuildResumeFromJob::test_renders_job_resume_with_keywords_resume_only_by_default`) still passes a string `experience` and now raises — outside the narrowed manifest, flagged as downstream Betty hygiene, not an AST-1350 product defect. Session Open HTML has no new frontend component test (core coverage only) — acceptable per bible manifest. `MaterialsPreviewModal`'s unused iframe path noted again, out of scope.

**What's solid:** core refuses emit before `filter_content_to_resume_structure`, closing the "drop then omit Experience" hole; defense-in-depth on any `experience_detail` non-array, not only the `experience` key; API maps unsupported `ValueError` → 400 with the exact string, other builder errors stay 404; JAR Print Resume now fetch-then-blob with no blind `window.open` on failure; reuses AST-1349's `is_experience_job_array` without redefining schema or touching prompts.

#### Resolution (2026-08-13)

CLEAN (no fix-now/discuss). Advisories left as-is. §9a: `origin/dev` dry-run clean; an `origin/ftr/AST-1345` merge-tree conflict flag on `candidate.py`/`JobAnalysisReportModal.tsx`/`config.py` was resolved by merging ftr onto the sub (`merge-resume(AST-1350)`), both dry-runs clean after.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` + `src/core/builder.py` | `BUILD_CONFIG` message + `_reject_unsupported_experience_shape` gate in three builders + emit defense-in-depth | `83ca56198` — +18/-4 |
| ✓ | `src/ui/api/api_resume_html.py` + `JobAnalysisReportModal.tsx` | 400 mapping; JAR fetch-then-blob toast | `3b30b01bc` — +55/-10 |
| | _tests_ | unsupported experience shape toast + no-emit coverage | `22925f507`; bible per Betty manifest |

---

**Foreign content preserved from this file's original source (`ast-1350-unsupported-experience-shape-toast-no-emit.md`) — real parent AST-1542, real home `docs/features/interface/`, not part of the AST-1345 epic. Kept here only because it would otherwise be lost when the source file is flagged for deletion; see the reconciliation note at the top of this archive.**

#### AST-1545 — Fix false popup-blocked toast on Print / Open HTML (parent: AST-1542, not AST-1345)

**As-is:** on Recommended JAR Print Resume (and Base Resume Print, Session Open HTML, Session Cover Open HTML), validate-then-blob succeeds and the HTML tab opens, but the UI still toasts `Popup blocked — allow popups to open the HTML tab.` because each handler calls `window.open(blobUrl, "_blank", "noopener,noreferrer")` then checks `if (!win)` — and with those features the browser returns `null` even when the tab opened.

**To-be:** when the HTML tab actually opens, no popup-blocked toast; that toast only appears on a real popup block.

**Root cause:** the four validate-then-blob handlers treated a null return from `window.open(..., "noopener,noreferrer")` as "blocked." Browsers return `null` for opens that include `noopener`/`noreferrer` even when the tab succeeded.

**Proposed change:** ⚠️ Decision — open the blob URL with `window.open(blobUrl, "_blank")`, no features string; if `win` is non-null, set `win.opener = null` immediately (noopener-equivalent isolation without forcing a null return); if `win` is null, toast the existing blocked string. Applied identically at all four call sites (`JobAnalysisReportModal.tsx` `handlePrintResume`, `ArtifactsBaseResumeContent.tsx` `handlePrint`, `AdminSessionResumePaste.tsx` `handleOpenHtml`, `AdminSessionCoverLetter.tsx` `handleOpenHtml`) — no shared util file, four call sites edited directly. Print HTML emit, API error mapping, unsupported-shape toast text, and non-blob `window.open` calls (e.g. Print Cover Letter's URL open) stay untouched.

**What must still hold:** AST-1350's unsupported/non-array experience toast and no-tab behavior stays exactly as shipped; a truly blocked popup still shows the blocked-toast text when no tab opens at all; the new tab stays isolated from its opener.

**Resolution — AST-1545 (2026-08-31):** Radia CLEAN/PROCEED (`fdc47334`). Four-site blob-open fix matched plan. Tests/bible landed on sibling AST-1546 (a docs-acceptance split for this product-only sub). Clean-review shortcut → User Testing (no resolve-child).

#### AST-1546 — gap: align Print blob-open tests with false popup-blocked toast fix (parent: AST-1542, not AST-1345)

**As-is:** frontend component/page tests and bible rows still required the three-arg `window.open(blobUrl, "_blank", "noopener,noreferrer")` call shape on the four validate-then-blob success paths, with `window.open` mocked to return `null` — so nothing proved that a successful tab omits the popup-blocked toast. After AST-1545's open-without-features + `opener = null` fix, those third-arg assertions would break, and a null mock would still show "blocked" on an otherwise-successful print.

**To-be:** bible + tests match AST-1545's blob-open shape (two-arg `window.open`, `opener` cleared on success); at least one repro fails if success still surfaces the popup-blocked toast; non-blob opens (JAR Print Cover Letter) keep their existing three-arg assertions unchanged.

**Root cause:** the original AST-1545 board review (`[board-betty] TESTS: REVISE`) found coverage locked to the old three-arg call shape and never asserted "success ⇒ no popup-blocked toast" — a gap sibling was filed to own the test/bible delta rather than running qa-fix directly on AST-1545.

**Proposed change:** this ticket touches only test/bible files — `docs/test-bible/frontend/{components,pages}.md` and the matching component/page test files under `tests/component/frontend/`. Product UI (`JobAnalysisReportModal.tsx` / Base Resume / Session pages) is explicitly out of scope (AST-1545 owns it), as is any non-blob `window.open` assertion (JAR Print Cover Letter keeps `"noopener,noreferrer"`). Every Print Resume success spy (including sites shared with two later, unrelated tickets AST-1489/1490) gets its blob-open expectation changed to the two-arg form, its `window.open` mock changed from returning `null` to a mutable fake window object, and a new assertion that `fakeWin.opener === null` and that the popup-blocked toast text is absent after success — that no-blocked-toast check is the actual bug-repro. `AST-1337`'s Base Resume Print success case and the Session Open HTML success cases get the identical treatment. Bible rows for AST-1350/AST-987/AST-1025 blob-open behavior are rewritten to drop the `noopener,noreferrer` implication and record the no-blocked-toast + cleared-opener contract.

**What must still hold:** AST-1350's unsupported-experience toast and no-tab behavior; failed/empty HTML paths still never call `window.open`; no product UI edits on this ticket.

**Resolution — AST-1546 (2026-08-31):** Radia discuss finding — product UI code had actually been stacked onto this gap sub (a cherry-pick of AST-1545's four blob-open handlers), which was reverted so this publish tip carries tests/bible (+ the plan-fix doc) only; product stayed on sibling `origin/sub/AST-1542/AST-1545-…`. Betty's `test(AST-1546)`/`merge-tests(AST-1546)` commits retained.

### AST-1351 — Experience array UI + render/print parity
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1351/experience-array-ui-renderprint-parity-clarify-candidate · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / 5 · Blocked by / blocks / related: parent: AST-1345_

#### What this implements

Owns Base Resume Content presenting/persisting the experience array as the base template, job artifact surfaces using the same structure by default, plus render/print emitting each role from the array. Does **not** own prompt/schema wording or the unsupported toast / no-emit path (siblings). After contract sibling; may land in parallel with toast sibling once the contract is fixed.

#### Acceptance criteria

- [X] 5. In the Base Resume Content UI, Susan can view and save experience as the job-array template (not as one undifferentiated prose field that round-trips as a string).
- [X] 6. Render and Print of a base (and job, where applicable) resume show each experience job with role metadata and accomplishments from the array — not one merged experience string.

#### Boundaries

Does not own prompt/schema wording or the unsupported toast / no-emit path (siblings).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `BUILD_CONFIG["experience_job_ui_fields"]` — ordered `{key, label}` list, keys exactly `_EXPERIENCE_JOB_ITEM_SCHEMA` | utils |
| `src/ui/api/api_system.py` | Expose `experience_job_ui_fields` (+ reuse `unsupported_resume_structure_message`) on `GET /api/system/ui_config` | ui |
| `src/ui/frontend/src/components/ExperienceJobsEditor.tsx` | New: per-role editor for the five config fields; add/remove/reorder; emits job objects (not a prose string) | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Render `ExperienceJobsEditor` for experience instead of raw JSON/`LabeledTextArea`; Save payload stays a parsed job array; non-array legacy values read-only with the unsupported message | ui |
| `src/ui/frontend/src/App.css` | Minimal role-card styles under `.experience-jobs-editor` | ui |
| `src/core/builder.py` | Happy-path parity audit; add Style D found/recorded experience shape + per-job detail when `debug=True` on the three build entrypoints; do not change the refuse gate or role HTML layout | core |

**As-is (why this ticket exists):** AST-996 taught ArtifactEditor to round-trip experience as pretty-printed JSON text so Save does not `str()`-corrupt the array, but Base Resume Content and job resume still edited experience as one undifferentiated textarea (JSON blob) — operators could not view/edit the job-array template per role. Render/print already emitted roles via `_emit_experience_jobs_html` and refused non-arrays (AST-1350), but Style D on emit paths still mostly logged summary `render_keys` without per-job found/recorded detail.

#### Contract (reuse — do not redefine)

Same five keys as AST-1349's `_EXPERIENCE_JOB_ITEM_SCHEMA`. UI editor fields must use these keys only, labels from `BUILD_CONFIG["experience_job_ui_fields"]`. Save must persist a JSON array of objects, never a single prose string.

⚠️ **Decision:** Replace the experience JSON textarea with a structured `ExperienceJobsEditor` for valid arrays — no dual JSON+form editing in the happy path. ⚠️ **Decision:** Job resume artifact already uses the same `ArtifactEditor` + `useCandidateResumeStructure` path — fixing ArtifactEditor once covers Base and job; no second job-only editor. ⚠️ **Decision:** legacy string/non-array experience shows read-only with the exact unsupported message inline; do not implement Print/Open-HTML toast or tab withholding here (AST-1350); block Save of that experience tab until regenerate replaces it with an array.

#### Stage 1–4 — Config/ui_config field spine, ExperienceJobsEditor, ArtifactEditor integration, builder Style D

New `BUILD_CONFIG["experience_job_ui_fields"]` (5 `{key, label}` entries in schema order) exposed via `GET /api/system/ui_config` alongside the existing unsupported-message string. New `ExperienceJobsEditor.tsx`: one card per job, per-field inputs (multiline for `accomplishments`), Move up/down/Remove controls, footer "Add role" appending a fully-keyed empty job object — no core/data imports, field keys read only from props. `ArtifactEditor.tsx`: marks the `experience` structureMode field as `type: "experience_jobs"`; loads the ui_config field spine once (module-level, with a same-five-keys Title-Case fallback if the fetch fails); adds `isExperienceTab` / `parseExperienceJobs` helpers; renders `ExperienceJobsEditor` for a parseable array, or a read-only raw textarea + the unsupported message for anything else; `doSave`/`buildPayload` toasts and aborts the whole Save if any experience tab fails to parse (never persists a string). Job resume surfaces need no separate file change since `JobAnalysisReportModal` already mounts `ArtifactEditor` with `useCandidateResumeStructure`. `builder.py`: confirmed the happy path already dispatches through `_emit_experience_jobs_html`; added `candidate_mod.debug_experience_jobs(_log, content_dict)` calls (reusing the existing helper, no new debug format) at all three public build entrypoints when `debug=True`.

#### Plan review — Joan (PROCEED)

**acceptable** — plan assumes AST-1349's contract and AST-1350's gate are already on the ftr tip (explicit `sync-child` merge expectation). **acceptable** — as-is verified: ArtifactEditor still round-tripped experience via pretty-printed JSON textarea; `structureMode` `shapeFields` omitted `type: "experience_jobs"` (Stage 3 fixes); no `debug_experience_jobs` yet on build entrypoints (Stage 4 adds). **acceptable** — `JobAnalysisReportModal` mounting `ArtifactEditor` with `structureSections` confirms the "fix once" approach covers job resume without a separate file.

#### Radia review — code-rubric.v1, CLEAN

Full 64-statute sweep (product commit `eac6612a`, six planned files): all conforms/not-applicable. Plan adherence confirmed across all four stages: field spine matches schema order exactly; `ExperienceJobsEditor` add/remove/reorder all present; `ArtifactEditor` structured editor, legacy read-only + Save abort, and `JobAnalysisReportModal` needing zero changes all delivered; builder debug calls added at all three entrypoints with no change to the refuse gate or role layout.

**Advisories (not blocking):** the three-dot diff is epic-aggregate (includes AST-1349/1350 via the merged epic line) — filter to the six-file product commit for review. Builder Style D test coverage exercises only the session entrypoint directly; `build_base_resume`/`build_resume_from_job` use the identical pattern — optional manifest extension before broader UT. `ArtifactEditor` seeds a hardcoded unsupported-message fallback before the `ui_config` fetch resolves — matches `BUILD_CONFIG` today, and the fetched value wins once loaded. `ExperienceJobsEditor` uses array index as React key — acceptable for MVP reorder, may want stable role ids if drag/reorder bugs appear later.

**What's solid:** replaces the JSON textarea happy path with structured per-role editing while preserving the `SideTab` string model (`JSON.stringify` on change); legacy string experience shows read-only + exact unsupported message + Save abort (component-tested); config field spine validated against the craft schema keys; core emit parity preserved with the refuse gate untouched; Style D reuses the existing `debug_experience_jobs` helper rather than inventing a second format.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` + `src/ui/api/api_system.py` | `experience_job_ui_fields` + `ui_config` exposure | `eac6612ab` (all six files, one commit) — +330/-21 total |
| ✓ | `ExperienceJobsEditor.tsx` | New per-role editor component | see above |
| ✓ | `ArtifactEditor.tsx` | Structured present/persist for experience; legacy read-only path | see above |
| ✓ | `App.css` | `.experience-jobs-editor` styles | see above |
| ✓ | `src/core/builder.py` | `debug_experience_jobs` Style D on three build entrypoints | see above |
| | _tests_ | experience job UI editor + render/print Style D coverage | `88ddcc5b7`; bible per Betty manifest |
