<!-- linear-archive: AST-1349 archived 2026-08-31 -->

## Linear archive (AST-1349)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1349/experience-array-contract-schema-prompts-agent-clarify-candidate  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 5  
**Parent:** AST-1345 — Clarify candidate_data.artifacts.base_resume.experience node  
**Blocked by / blocks / related:** parent: AST-1345; blocks: AST-1351; blocks: AST-1350

### Description

## What this implements

Owns the shared experience job-array wire shape in craft/parse/finalize response schemas and candidate + job craft prompts; tightens agent validation to that contract only (no string success path, no needless extra checks). Does **not** own UI toast chrome or HTML emit (siblings). After this child, schemas/prompts/agent agree on one array shape for candidate and job (Base template = job default structure).

## Citations

`pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.agent.do-task-delegation`, `astral.standards.debug-contract-gated`, `astral.standards.no-hardcoded-sets`

## Acceptance criteria

1. After craft/parse (or load of a saved base resume) for a multi-job resume, `artifacts.base_resume.experience` is an ordered array; each element exposes company, title, dates, location, and accomplishments observable in Base Resume Content / parse JSON.
2. Job artifact resume content that carries experience uses the same array element shape as the candidate base resume (same keys/requiredness by default); Base remains the template, not a job-tailored editor.
3. Craft/parse/finalize schemas and the related candidate + job prompts accept and describe experience only as that array — string experience is not a valid success path.
4. Agent handling of experience does not reject a valid job array with leftover string-era validation, and does not require fields beyond the shared contract.
5. When `debug=True` on touched experience-reading hops/persist paths, logs show found/recorded experience shape and per-job detail (Style D), not only summaries.

## Boundaries

Does **not** own UI toast chrome or HTML emit (siblings Unsupported experience shape; Experience array UI + render/print parity).

## Notes for planning

Shared wire shape; Base template = job default structure.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-13T00:12:14.487Z
[code-rubric] PROCEED (Commit: bab06e65) experience array contract locked

#### betty — 2026-08-13T00:08:55.174Z
`origin/sub/AST-1345/AST-1349-experience-array-contract-schema-prompts-agent` @ `bab06e65` · array contract tests ready

#### joan — 2026-08-12T23:59:22.781Z
[plan-rubric] PROCEED (Commit: 2342855c) experience contract locked

#### ada — 2026-08-12T23:56:21.339Z
`origin/sub/AST-1345/AST-1349-experience-array-contract-schema-prompts-agent` @ `2342855c104a1e2109328f78c00bee28077c1dc0` · plan published

---

# Experience array contract — schema, prompts, agent (Clarify candidate_data.artifacts.base_resume.experience node)

**Linear:** [AST-1349](https://linear.app/astralcareermatch/issue/AST-1349/experience-array-contract-schema-prompts-agent-clarify)
**Parent:** [AST-1345](https://linear.app/astralcareermatch/issue/AST-1345/clarify-candidate-data-artifacts-base-resume-experience-node) — Clarify candidate_data.artifacts.base_resume.experience node
**Publish ref:** `origin/sub/AST-1345/AST-1349-experience-array-contract-schema-prompts-agent`

Closes the remaining schema / prompt / agent gap so candidate craft/parse and job craft/finalize agree on one experience wire shape: an ordered array of job objects (`company`, `title`, `dates`, `location`, `accomplishments`). Config already carries `_EXPERIENCE_JOB_*` from the AST-994 epic; this child locks that contract as the only success path (no prose-string experience), rewrites drifted prompts, and trims agent checks to the shared contract. Does **not** own UI toast chrome (AST-1350) or HTML emit / Base Resume UI (AST-1351).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Audit/lock craft/parse/finalize (+ `BUILD_CONFIG` resume_content) experience fields on the shared `_EXPERIENCE_JOB_*` objects; no parallel string experience schema | utils |
| `data/admin/agent_task.json` | Rewrite `craft_resume_base` `### experience` (and conflicting lines) to job-array only; update job craft `user_prompt`s so experience is array-only (remove “prose string or job array”); keep `simple_resume_parse` array wording consistent | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Whole-file `cp` twin of `data/admin/agent_task.json` after prompt edits | docs |
| `src/core/candidate.py` | Draft normalize/validate: reject non-array experience as failure (no string success path); validate only the shared five keys; drop needless `experience_detail` jargon / extra field requirements; Style D found/recorded on touched experience paths when `debug=True` | core |
| `src/core/agent.py` | Keep finalize/draft pin + Style D hooks on experience-reading hops; do not add string-era coerce for experience; ensure schema validation remains the gate for craft/parse/finalize list+`items_schema` | core |

**Out of scope (do not touch):** `src/core/builder.py` / print HTML (AST-1351); toast / no-emit paths (AST-1350); ArtifactEditor UI chrome beyond what already round-trips arrays; `prior_experience` stays `str`; cover letter; `tests/`, bible; Manage Tasks UI; live DB hand-edits.

**As-is (why this ticket exists):** `TASK_CONFIG` craft/parse/finalize schemas already use `_EXPERIENCE_JOB_ARRAY_FIELD` / `_OPTIONAL`, and `simple_resume_parse` prompt already teaches a job array — but `craft_resume_base` `cache_prompt` `### experience` still teaches blank-line prose roles (`COMPANY NAME` / `Title \| dates \| Location`), and `draft_job_resume` `user_prompt` still says experience may stay “a prose string or job array.” That re-authorizes the string success path parent AC forbids.

## Contract (shared — do not redefine)

Each experience job object (config `_EXPERIENCE_JOB_ITEM_SCHEMA`):

| Field | Type | Notes |
|-------|------|-------|
| `company` | str | required |
| `title` | str | required |
| `dates` | str | required; freeform (year-only or ranges OK) |
| `location` | str | required; `""` when source has none |
| `accomplishments` | str | required; one text block per role |

⚠️ **Decision:** One shared items_schema object identity for candidate craft/parse (required list) and job finalize (optional list). Do not invent a second job-only experience schema. Base template = job default structure.

⚠️ **Decision:** No new `highlights` field on experience jobs. Accomplishments is the single body block (AST-997 pin policy for job hops stays: may tailor `accomplishments`; pin `company`/`title`/`dates`/`location` from base).

## Stage 1: Config — lock shared experience array schemas

**Done when:** `craft_resume_base` / `simple_resume_parse` / `finalize_job_resume` response_schema `experience` entries are the shared list+`items_schema` objects (required True for craft/parse, required False for finalize); `BUILD_CONFIG["artifact_shapes"]["resume_content"]["experience"]` matches the same item contract; `stringify_response_schema` for craft and finalize shows an array of the five keys; no `experience: {type: str}` remains on those schemas.

1. In `src/utils/config.py`, confirm (and fix only if drifted) that:
   - `_EXPERIENCE_JOB_ITEM_SCHEMA` still defines exactly the five keys above as `str` / `required: True`.
   - `_EXPERIENCE_JOB_ARRAY_FIELD` is `type: list`, `required: True`, `items_schema: _EXPERIENCE_JOB_ITEM_SCHEMA`.
   - `_EXPERIENCE_JOB_ARRAY_FIELD_OPTIONAL` is the same items_schema with `required: False`.
2. Confirm `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA["experience"]` is `_EXPERIENCE_JOB_ARRAY_FIELD` and that both `TASK_CONFIG["craft_resume_base"]["response_schema"]` and `TASK_CONFIG["simple_resume_parse"]["response_schema"]` still share that object (`is` identity with `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`).
3. Confirm `TASK_CONFIG["finalize_job_resume"]["response_schema"]["experience"]` is `_EXPERIENCE_JOB_ARRAY_FIELD_OPTIONAL` (same `items_schema` identity).
4. Confirm `BUILD_CONFIG["artifact_shapes"]["resume_content"]["experience"]` is `_EXPERIENCE_JOB_ARRAY_FIELD` (or the same items_schema / list shape — do not introduce a string type).
5. Confirm `DATA_SHAPES` base_resume experience field type remains `experience_jobs` (UI sibling consumes this; do not change UI code here).
6. Do **not** add a static `experience` field to `draft_job_resume` `response_schema` — keep `resume_section_payload: True` + runtime validate (Stage 4). Do **not** change `prior_experience`.
7. If any of steps 1–5 already match tip, leave the literals alone (no drive-by renames). If a string-typed `experience` remains on craft/parse/finalize/resume_content, replace it with the shared field object.

## Stage 2: Candidate prompts — craft_resume_base array-only; keep parse aligned

**Done when:** `craft_resume_base` `cache_prompt` `### experience` instructs an ordered JSON array of the five-key job objects (not prose role blocks); LinkedIn/backstory/strengths are not told to enrich experience accomplishments; quality checklist does not imply experience is a string; `simple_resume_parse` still describes experience as a job array with the same five keys. No other task rows edited in this stage except the two candidate rows named below.

1. In `data/admin/agent_task.json`, edit the object with `"task_key": "craft_resume_base"` and `"current": 1`. Change **`cache_prompt` only** (leave `user_prompt`, `nocache_prompt`, agent ids, grouping, `run_next`, uuids, `updated_at` untouched unless a line in `user_prompt` still teaches string experience — if so, fix that line only).
2. Replace the entire `### experience` segment (currently “Format each role as: COMPANY NAME / Title \| … / blank-line separated prose”) with instructions that match this contract:
   - `experience` is an **ordered JSON array** of job objects (resume order).
   - Each object has exactly: `company`, `title`, `dates`, `location`, `accomplishments` (all strings).
   - `dates` freeform as in the resume source; `location` is the source location or `""`.
   - `accomplishments` is one text block per role from resume/paste facts (paragraph and/or bullets) — organize into the field; do not invent metrics/employers.
   - Resume/paste is the source of truth for all five fields. Do **not** return experience as a single prose string.
3. Neutralize **only** experience-conflicting lines elsewhere in the same `cache_prompt`:
   - Input-source bullet that says LinkedIn “Enriches professional summary and experience sections” → keep professional-summary enrichment; remove experience from that enrichment claim (e.g. enrich professional summary only).
   - Any rule that tells Judith to blend LinkedIn/backstory/strengths into experience role accomplishments → remove or rewrite so experience jobs stay resume/paste-faithful.
   - Leave `### professional_summary` / non-experience synthesis language alone unless it explicitly dumps LinkedIn claims into experience.
4. In QUALITY CHECKLIST, ensure bullets do not require experience to be a non-empty **string**. Prefer wording like: required keys present; `experience` is a job array when roles exist; string sections may be empty when source material is absent (especially `highlights`).
5. In `data/admin/agent_task.json`, edit `"task_key": "simple_resume_parse"` / `"current": 1` **`cache_prompt` only** if needed so `### experience` and the field inventory still say job array with the same five keys (already true on tip — touch only if wording drifted from Stage 1 contract).
6. Do **not** invent a second parse agent; session parse continues to call `do_task("simple_resume_parse")` / craft-base as today.

⚠️ **Decision:** Prompt text is the durable Archie catalog (`astral.seed.agent-tables-in-repo-json`). Commit JSON; do not hand-edit production DB.

## Stage 3: Job craft prompts — array-only (Base template = job structure)

**Done when:** `draft_job_resume`, `finalize_job_resume`, `advise_job_resume`, and `check_job_resume` prompts no longer authorize prose-string experience; draft/finalize output guidance describes experience as the same job-array shape as base; advise/check forbid mutating company/title/dates/location and speak in per-role array terms where they mention experience.

1. In `data/admin/agent_task.json`, edit `"task_key": "draft_job_resume"` / `"current": 1` **`user_prompt` only**:
   - Replace the parenthetical `(experience stays a prose string or job array matching the base)` with language that experience is an **ordered array of job objects** with `company`, `title`, `dates`, `location`, `accomplishments` — same keys/types as the provided base resume.
   - Add a short rule block (after the existing hard rules, before the JSON example if cleaner): you may reframe/reorder/emphasize **`accomplishments`** for the target job (every claim still traces to base materials); **do not** change `company`, `title`, `dates`, or `location` from the base role; **do not** emit experience as a prose string.
2. Edit `"task_key": "finalize_job_resume"` / `"current": 1` **`user_prompt` only**: state that the final `resume` / payload experience must remain that job-array shape; when applying Grace fixes, restore factual metadata to base; do not collapse experience to a string.
3. Edit `"task_key": "advise_job_resume"` / `"current": 1` **`user_prompt` only** if needed: in RESUME BRIEF guidance, direct Estelle to brief Judith per role (accomplishments emphasis/cuts/keyword weave) and to **forbid** rewriting company/title/dates/location. Do not add a second experience schema.
4. Edit `"task_key": "check_job_resume"` / `"current": 1` **`user_prompt` only** if needed: keep mutated-identity flags for company/title/dates; ensure wording does not assume experience is one prose blob (location of discrepancies may be per-role).
5. Leave chain `cache_prompt*` / `{$CALLER_*}` tokens and `run_next` unchanged.

## Stage 4: Agent — contract-only validation; no string success path; Style D

**Done when:** A valid five-key job array passes draft validate + craft/parse/finalize schema; a non-empty string `experience` fails (not soft-accepted); validators do not require fields beyond the shared five keys and do not reject a valid array with leftover string-era rules; when `debug=True` on touched experience-reading hops/persist helpers already wired, Style D shows found/recorded shape and per-job detail.

1. In `src/core/candidate.py` `normalize_draft_job_resume_agent_payload`: keep the skip that leaves `_is_experience_job_array(val)` untouched (do **not** `_coerce_resume_section_string` a job array into prose). If any branch still joins an experience list-of-dicts into a string, remove that path.
2. In `validate_draft_job_resume_payload`, for `key == "experience"`:
   - Empty / `""` / `None`: keep today’s skip/accept behavior for “section omitted.”
   - If `_is_experience_job_array(val)` and non-empty: accept. Optionally normalize missing `location` to `""` in place (already present). Do **not** require extra keys beyond `_EXPERIENCE_JOB_ITEM_SCHEMA`. Do **not** require `experience_detail` body_kind language in the error string — use a contract-facing message such as `Section 'experience' must be a job array` (same meaning as today, without UI body_kind jargon).
   - If `val` is a non-empty `str` **or** any non-array shape: return that error (string is **not** a success path).
3. Keep `pin_experience_job_facts_from_base` match-by-`(company, title)` behavior (AST-997); call sites in draft validate + `agent.py` finalize remain. Do not add index-first pinning.
4. In `src/core/agent.py`:
   - Do **not** add experience to any soft-coerce that would turn a list into a string (`_coerce_schema_str_fields_from_list` already skips non-`str` schema types — leave that invariant).
   - Keep existing post-success Style D `debug_experience_jobs` for `draft_job_resume` / `finalize_job_resume` when `debug=True`.
   - Craft/parse success paths already call `_debug_experience_jobs` from candidate helpers when `debug=True` — do not remove; if a touched hop that reads experience lacks Style D shape/detail, add one call to the existing helper (do not invent a second logger format).
5. Do **not** tighten `_is_experience_job_array` to re-implement full `items_schema` (schema validation owns required keys on craft/parse/finalize). Draft validate may rely on list-of-dicts + shared five-key contract without inventing sixth fields.
6. Do **not** implement toast / no-emit / builder HTML here.

## Stage 5: UAT fixture twin sync

**Done when:** `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to `data/admin/agent_task.json`.

1. After Stages 2–3 prompt edits:

```bash
cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
```

2. Do not surgically dual-edit the twin — whole-file `cp` only (AST-1333 / seed twin pattern).

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

**Rubric:** plan-rubric
**Ticket:** AST-1349
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1345/AST-1349-experience-array-contract-schema-prompts-agent` @ `2342855c104a1e2109328f78c00bee28077c1dc0`

### Traceability

| AC | Plan stage(s) |
|----|----------------|
| 1 | S1 (shared array schemas), S2 (`craft_resume_base` / `simple_resume_parse` prompts), S4 (agent persist/validate on craft paths) |
| 2 | S1 (`items_schema` identity craft vs finalize), S3 (job craft prompts), S4 (`pin_experience_job_facts_from_base`, draft validate) |
| 3 | S1 (lock list+`items_schema` on craft/parse/finalize/`BUILD_CONFIG`), S2–S3 (remove prose-string authorization in prompts) |
| 4 | S4 (`validate_draft_job_resume_payload` contract-only; no string success; drop `experience_detail` jargon) |
| 5 | S4 (reuse `debug_experience_jobs` / existing Style D hooks when `debug=True`) |

Stages S1–S5 map to child scope and parent functional bullets 1–4 + debug (parent AC 5–7 correctly deferred to AST-1350/AST-1351 per child Boundaries).

### Findings

**acceptable** — Ticket assignee is Ada (not Joan); Chuckles spawned this pass explicitly; no review block.

**acceptable** — Stage 1 may be largely confirm-only on tip (`_EXPERIENCE_JOB_*` already wired in `config.py`); plan correctly limits edits to drift-only fixes.

**acceptable** — Component tests asserting `"prose string or job array"` / `experience_detail` error text are out of plan scope (`tests/` ban); Betty manifest expected to flip during qa-child after build.

No `fix-now` or `discuss` findings. Statute sweep (R1–R4) in-session: all universal `orch.*` conform; scoped statutes considered for `utils`/`core`/`data/admin` touch set — all `conforms`. Cited patterns `pattern.config.config-block` and `pattern.layers.import-discipline` match plan shape. As-is diagnosis verified on publish ref: `craft_resume_base` `### experience` still teaches prose blocks; `draft_job_resume` still authorizes `"prose string or job array"`.

context_tokens≈48000

## Review (build stub)

- **Publish ref:** `sub/AST-1345/AST-1349-experience-array-contract-schema-prompts-agent`
- **Tip:** `e8c4066c835d4587f2ab3dc310ee3c9d8397c098`
- **Stages:** S1 confirm-only (`_EXPERIENCE_JOB_*` already locked); S2–S3 candidate + job prompts array-only; S4 draft validate contract message / no string success; S5 AST-756 `agent_task` twin `cp`


## Radia review

# Radia review — AST-1349

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1349  
**Publish ref:** `origin/sub/AST-1345/AST-1349-experience-array-contract-schema-prompts-agent` @ `bab06e6582f4811307e1918050c1e8c47f4b66e3`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | No agent confidence / grading paths in diff |
| `astral.agent.do-task-delegation` | scoped | not-applicable | `src/core/agent.py` untouched |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | No grade-vector / consult schema edits |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch claim/process paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch id emission |
| `astral.batch.claim-process-release` | scoped | not-applicable | No dispatcher/tracker batch helpers |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No entity response persistence |
| `astral.config.config-source-of-truth` | scoped | conforms | Experience schemas remain single `_EXPERIENCE_JOB_*` block in `config.py` (confirm-only; already locked) |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | No secrets/env wiring |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No debug artifact dirs |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No spike files |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | No dispatch seed paths |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No `run_next` / chain edits |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single issue doc for AST-1349 |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Product commit `66a29148` touches only `data/admin/`, `src/core/candidate.py`, UAT twin; test/bible via Betty merge |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer commit excludes `tests/` and `docs/test-bible/` |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | No coat-check paths |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No render/verdict orchestration |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | No API/auth surface |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Core-only product edit; no external I/O |
| `astral.layers.import-direction` | scoped | conforms | `candidate.py` diff adds comment + error strings only; no new imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No `scripts/` changes |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | No `src/ui/` changes |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | Prompt contract committed in `data/admin/agent_task.json` + AST-756 twin |
| `astral.seed.archie-catalog-wins` | scoped | conforms | Catalog JSON is source of truth; whole-file twin `cp` per plan |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | No boot/hot-path seed logic |
| `astral.seed.define-approved` | scoped | not-applicable | Child implementation ticket |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No operator-row resurrection |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No coverage-join seed edits |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No `src/data/` product changes |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No `database.py` / migration edits in product diff |
| `astral.standards.debug-contract-gated` | scoped | conforms | Existing Style D on `validate_draft_job_resume_payload` / `debug_experience_jobs` unchanged; no new ungated debug |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Minimal validate-message change; prompts centralized in catalog |
| `astral.standards.in-scope-only` | scoped | conforms | Product scope matches plan; AST-1352 files arrive via `merge-tests` (see advisory) |
| `astral.standards.logging-via-utils` | scoped | conforms | No new `print()` / raw `logging` imports |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | No ticket-id symbol names in product code |
| `astral.standards.no-cross-contamination` | scoped | conforms | No AST-1350/1351 UI/builder/toast scope; cross-epic test merge is pipeline convention |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Experience keys stay in config block |
| `astral.standards.public-then-helpers` | scoped | conforms | No helper-order regression |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No `utils→data` import changes |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No job state machine edits |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No run-chain edits |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | No frontend files |
| `astral.ui.naming-conventions` | scoped | not-applicable | No UI naming surface |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | No server config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `bab06e65 merge-tests(AST-1349): origin/tests 99ffa38` present |
| `orch.git.commit-vocabulary` | universal | conforms | `code(AST-1349)` / `test(AST-1349)` / `merge-tests(AST-1349)` vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | `sub/AST-1345/...` off `dev`; no reverse flow |
| `orch.git.ftr-sub-topology` | universal | conforms | Child on `sub/AST-1345/AST-1349-...` |
| `orch.git.merge-on-checkout` | universal | conforms | No checkout/merge violations observed |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | Linear history; no force/rebase |
| `orch.git.no-dev-agent-branches` | universal | conforms | Publish ref is `sub/`, not agent branch |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Review in `astral-AST-1345` worktree |
| `orch.git.three-permanent-branches` | universal | conforms | Diff baseline `origin/dev` |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Implements approved plan; no new product forks |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages S1–S5 delivered per plan |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Artifacts child under AST-1345 |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Spawned at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | Joan APPROVED @ `2342855c` |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Tests/bible from `test(AST-1349)` + merge-tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada assignee at Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Engineer commit respects path bans |

**Active-set count scored in-session:** 64 rows (registry table); no `violates` / `needs-discussion` statute rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | S1 confirm-only: `_EXPERIENCE_JOB_*` shared identity for craft/parse/finalize/`BUILD_CONFIG` (unchanged on tip) |
| `pattern.layers.import-discipline` | conforms | Core-only touch; no layer bends or new cross-layer imports |

## Plan adherence

Engineer commit `66a29148` delivers the planned footprint:

- **S1 (config):** Confirm-only — no `config.py` diff; tip still has shared `_EXPERIENCE_JOB_ITEM_SCHEMA` / `_EXPERIENCE_JOB_ARRAY_FIELD` / `_EXPERIENCE_JOB_ARRAY_FIELD_OPTIONAL` wired to craft/parse/finalize/`BUILD_CONFIG`.
- **S2 (candidate prompts):** `craft_resume_base` `cache_prompt` `### experience` is array-only (five keys, no `COMPANY NAME` prose blocks, LinkedIn enrichment line removed from experience, checklist uses job-array wording). `simple_resume_parse` already aligned.
- **S3 (job prompts):** `draft_job_resume` `user_prompt` retires `"prose string or job array"`; `finalize_job_resume` and `advise_job_resume` `user_prompt`s teach job-array + pin policy. `check_job_resume` already speaks per-role job-array metadata (no edit required).
- **S4 (agent):** `validate_draft_job_resume_payload` rejects non-array experience with contract-facing `Section 'experience' must be a job array` (no `experience_detail` jargon); empty/`""`/`None` still skip before experience branch; `pin_experience_job_facts_from_base` and Style D hooks untouched in `agent.py` per plan.
- **S5 (UAT twin):** Whole-file `cp` — `TestAst1349ExperienceArrayContract::test_uat_fixture_twin_matches_catalog_after_prompt_edits` asserts byte identity.

**Estimate 5:** Footprint matches (prompt JSON + small validate + Betty tests); no scope creep into AST-1350/1351.

**C6 lenses (§5a):** Imports/layers/silent-failure/fallbacks/logging/debug/external — no issues on touched product paths. §5f/§5g not triggered (`agent.py` / `src/external/` untouched).

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **merge-tests piggyback (AST-1352):** Three-dot diff also includes `test(AST-1352)` artifacts (`tests/component/data/database/test_astral_artifacts.py`, `docs/test-bible/data/database/astral_artifacts.md`, conftest one-liners) from `origin/tests` merge commit `bab06e65`. Parent is AST-1340, not AST-1345. Pipeline-legal per `orch.git.betty-merge-tests-one-sha`; does not affect AST-1349 ACs. Downstream: when reviewing AST-1349 in isolation, filter product diff to `66a29148` if AST-1352 noise is distracting — no resolve-child action required for AST-1349.

## What's solid

- Closes the documented as-is gap: Judith craft and draft prompts no longer re-authorize prose-string experience.
- Draft validate error text matches plan and Betty's flipped AST-997/AST-1270 assertions.
- Shared five-key schema identity preserved without a parallel job-only schema.
- AST-756 twin discipline (`cp` + `cmp`) enforced in tests.

## Frame diff

`(none)` — Joan APPROVED frame unchanged. Implementation delta since plan validate @ `2342855c`:

| Commit | Delta |
|--------|-------|
| `66a29148` | Product: prompts + validate message |
| `99ffa38c` | Betty: `TestAst1349ExperienceArrayContract` + bible rows |
| `7f7444a7` | Betty: AST-1352 database tests (cross-epic merge artifact) |
| `bab06e65` | `merge-tests(AST-1349)` lands tests on publish ref |

context_tokens≈52000


## Bug: AST-1381 — accomplishments `string[]` contract (craft/parse)

Parent mini-bug: [AST-1362](https://linear.app/astralcareermatch/issue/AST-1362/base-resume-issues) / child [AST-1381](https://linear.app/astralcareermatch/issue/AST-1381/fix-base-resume-issues-craftuiprint). UI/render/print + `|`→`•` + collapsible roles + prior format Save → print live in `ast-1351-experience-array-ui-render-print-parity.md` § Bug: AST-1381. This block owns only the **schema / prompt / validate** half of symptom 1.

### As-is

`craft_resume_base` / `simple_resume_parse` still define each job’s `accomplishments` as one **string** and teach “paragraph and/or bullets” / newline-separated bullet lines. Agents return prose that already carries `•` / `-` markers; emit later wraps each line in `<li>` → double bullets.

### To-be

`accomplishments` is an ordered **`string[]`**: one bare achievement string per element (no leading bullet glyphs). Craft/parse prompts and response schemas request that shape; validation rejects a non-list `accomplishments` the same way non-array `experience` is rejected. Lead lines that must stay non-bulleted keep the existing `<no bullet>` prefix **on that array element** (config `experience_role_layout.lead_line_prefix`).

### Repro

1. Craft or parse a base resume whose role accomplishments come back as a single string with lines like `• Shipped X` / `- Did Y`.
2. Persist as job-array `experience` and Print / Open HTML.
3. Observe `<li>• Shipped X</li>` (glyph + list marker).

Fixture shape (pre-fix wire):

```json
{
  "company": "Acme",
  "title": "PM",
  "dates": "2020 - 2023",
  "location": "Remote",
  "accomplishments": "• Shipped X\n- Did Y"
}
```

Post-fix wire:

```json
{
  "company": "Acme",
  "title": "PM",
  "dates": "2020 - 2023",
  "location": "Remote",
  "accomplishments": ["Shipped X", "Did Y"]
}
```

### Root cause

AST-1349 locked `experience` as a job **array** but left `_EXPERIENCE_JOB_ITEM_SCHEMA["accomplishments"]` as `type: str` and rewrote prompts to “one text block … paragraph and/or bullets.” That re-authorizes embedded bullet markers inside the body field. Render (AST-1351 / `_emit_experience_jobs_html`) always wraps non-lead lines in `<li>` without stripping markers — see sibling bug block on ast-1351.

### Proposed change

1. In `src/utils/config.py`, change `_EXPERIENCE_JOB_ITEM_SCHEMA["accomplishments"]` from `{"type": "str", "required": True}` to a **list of strings** required field (same list+items pattern used elsewhere in TASK_CONFIG — e.g. `type: list`, `items_schema` / item type `str`, `required: True`). Keep the other four keys as required strings. Do **not** invent a sixth job key; do **not** change `prior_experience`.
2. Confirm `stringify_response_schema` / craft+parse+finalize schemas that share `_EXPERIENCE_JOB_ITEM_SCHEMA` now show `accomplishments` as a string array. `BUILD_CONFIG["artifact_shapes"]["resume_content"]["experience"]` and `experience_job_ui_fields` stay keyed on `accomplishments` (UI type change is ast-1351).
3. In `data/admin/agent_task.json` (and whole-file `cp` twin `docs/uat-fixtures/AST-756/expected-agent_task.json`):
   - `craft_resume_base` `cache_prompt` `### experience`: teach `accomplishments` as an **ordered JSON array of strings** — bare achievement text only; **do not** prefix elements with `•`, `-`, `*`, or similar; `<no bullet>…` only when the source has a role-description lead.
   - `simple_resume_parse` `### experience`: same array-of-strings contract; keep the `<no bullet>` lead rule as a **prefix on that array element**, not a reason to stay on a prose string.
   - Job draft/finalize prompts that describe `accomplishments` as one text block: retarget to `string[]` without re-opening a prose-string `experience` path.
4. In `src/core/candidate.py` experience validate/normalize paths that currently require `accomplishments` to be `str`: require `list` whose elements are strings (after strip, drop empty); reject string / dict / mixed. Style D found/recorded may list per-element accomplishments when `debug=True`.
5. Do **not** change `_emit_experience_jobs_html` here — that flip is in the ast-1351 AST-1381 block (consume `list` + strip residual markers).

### Blast radius

- Shared `_EXPERIENCE_JOB_ITEM_SCHEMA` identity: craft, parse, finalize, `resume_content` shape, ArtifactEditor / ExperienceJobsEditor persistence, job draft pin policy (may still tailor accomplishments only).
- Existing stored base resumes with string `accomplishments` become unsupported until regenerate/re-edit (same class of gate as AST-1350 non-array experience — decide in make-fix with the ast-1351 emit/UI path: either coerce newline-split string → list on read for emit/UI only, or refuse with the unsupported message; **prefer one-time coerce on read for string accomplishments so Print does not break mid-migration**, without writing the coerce back unless Save runs).
- Betty tests / bible that assert `accomplishments: str` (AST-1349 / AST-1351 families) will need qa-fix if board flags TESTS: REVISE.

### What must still hold

- `experience` remains an ordered job **array** (no prose-string success path) — AST-1349 AC.
- Job objects still have exactly the five keys; no new `highlights` on jobs.
- Finalize may tailor `accomplishments` only; pin `company` / `title` / `dates` / `location` from base.
- `prior_experience` stays `str`.
- AST-756 `expected-agent_task.json` remains a whole-file twin of `data/admin/agent_task.json`.

### Resolution (2026-08-15, resolve-child)

Product landed on `origin/sub/AST-1362/AST-1381-fix-base-resume-issues` (schema/prompts/validate). Sibling AST-1382 retargeted fixtures/bible. Radia review-fix fix-now: orphan AST-1383 `TestAst1380…` / `docs/test-bible/core/agent.md` additions stripped by Betty (`test(AST-1381):` restore from `origin/ftr/AST-1362-base-resume-issues`) — no matching craft-thinking product on this tip. Discuss (multi-ticket frame / AST-1382 on sub) left as expected sibling ancestry. Advancing to User Testing.


## Bug: AST-1382 — gap: retarget accomplishments `string[]` fixtures + bible (board-betty REVISE)

Parent mini-bug: [AST-1362](https://linear.app/astralcareermatch/issue/AST-1362/base-resume-issues) / gap child [AST-1382](https://linear.app/astralcareermatch/issue/AST-1382/gap-base-resume-issues-testsbible-board-betty-revise). Sibling product tip: [AST-1381](https://linear.app/astralcareermatch/issue/AST-1381/fix-base-resume-issues-craftuiprint) (`origin/sub/AST-1362/AST-1381-fix-base-resume-issues`) already landed schema/prompts/validate + emit/UI. Emit / `|`→`•` / collapsible / format-Save repro coverage lives in `ast-1351-…` § Bug: AST-1382. This block owns the **contract/schema fixture + candidate bible** half.

### As-is

Component fixtures and `docs/test-bible/core/candidate.md` / `utils` rows still treat job `accomplishments` as a required **`str`**. After AST-1381, `_EXPERIENCE_JOB_ITEM_SCHEMA["accomplishments"]` is `type: list`, draft validate rejects string accomplishments, and shared `_SAMPLE_EXPERIENCE_JOBS` (str bodies) fails `TestAst1349ExperienceArrayContract` / config schema asserts. AST-1381 `[qa-handoff]` is blocked on this retarget.

### To-be

Fixtures and bible for the five-key job contract use **`accomplishments: string[]`** (bare achievement strings; optional `<no bullet>` prefix on an element). Config asserts expect `accomplishments` as `{"type": "list", "required": True}` (not `str`). Candidate bible § AST-996 / AST-1349 rows name the list shape. No second product rewrite.

### Repro

On tip that includes AST-1381 product:

```bash
.venv/bin/python -m pytest -q \
  tests/component/core/test_candidate.py::TestAst1349ExperienceArrayContract::test_validate_accepts_five_key_job_array \
  tests/component/utils/test_config.py::TestAst996ExperienceJobArrayConfig::test_craft_resume_base_experience_is_job_array_field
```

Both red: validate error “accomplishments must be a list of strings”; config assert `type str` vs `type list`.

### Root cause

fix-board `[board-betty] TESTS: REVISE` on AST-1381: product widened accomplishments to `string[]`, but AST-996 / AST-1349 / AST-1351 fixture spine and bible still encode the old str contract. Gap was filed as this sibling instead of running `qa-fix` on AST-1381.

### Proposed change

1. **`tests/component/core/test_candidate.py`:** Change module `_SAMPLE_EXPERIENCE_JOBS` so each job’s `accomplishments` is a **`list[str]`** (e.g. `["Shipped widgets"]`, `["Led the team"]`). Fix the type alias (`list[dict[str, str]]` → values may be `str | list[str]`, or use `list[dict[str, Any]]`). Grep the file for other inline `"accomplishments": "<str>"` job literals and retarget the same way. Keep five keys; do not add fields.
2. **`tests/component/utils/test_config.py`:** In `TestAst996ExperienceJobArrayConfig` (and any twin that loops `_JOB_KEYS` expecting every key `type: str`), assert `accomplishments` is `{"type": "list", "required": True}` while the other four keys remain `str`. Update `TestAst997FinalizeExperienceJobArray` / stringify examples if they hardcode str accomplishments. Leave `TestAst1351ExperienceJobUiFields` key order alone (still five keys including `accomplishments`).
3. **`docs/test-bible/core/candidate.md`:** Under AST-996 / AST-1349 experience-array sections, rewrite “accomplishments (string)” / “one text block” wording to **ordered `string[]`**, and note draft validate rejects non-list accomplishments. Point narrowed runs at the same TestAst996 / TestAst1349 classes after fixture retarget.
4. **`docs/test-bible/utils/config.md`:** Where AST-996 / AST-1349 schema rows say accomplishments `str`, retarget to `list`. Keep shared `_EXPERIENCE_JOB_ITEM_SCHEMA` identity callouts.
5. Do **not** change product `src/` on this gap (AST-1381 owns that). Do **not** invent a new plan doc.

### Blast radius

- Shared `_SAMPLE_EXPERIENCE_JOBS` feeds many candidate tests beyond AST-1349 — retargeting it once should green a cluster; re-run `TestAst996ExperienceJobArray`, `TestAst1349ExperienceArrayContract`, and any class that deep-equals sample jobs.
- Agent/schema stringify examples that still say `"<accomplishments item>"` as a string leaf may need a list-shaped example if asserts are structural.
- AST-1381 stays Code Complete until this gap’s fixtures land and Betty clears the `[qa-handoff]`.

### What must still hold

- Experience remains an ordered job **array** (no prose-string success path) — AST-1349.
- Exactly five job keys; `prior_experience` stays `str`.
- Finalize may tailor accomplishments only; pin company/title/dates/location.
- AST-756 `expected-agent_task.json` twin discipline stays a product/prompt concern (already on AST-1381); this gap does not re-open prompt edits unless a fixture asserts the old prompt prose.
