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
