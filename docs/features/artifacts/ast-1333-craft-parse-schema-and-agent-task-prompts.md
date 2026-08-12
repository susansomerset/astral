# AST-1333 — Craft/parse schema and agent_task prompts

**Linear:** https://linear.app/astralcareermatch/issue/AST-1333/craftparse-schema-and-agent-task-prompts  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1326/make-highlights-a-required-resume-section  
**Publish ref:** `sub/AST-1326/AST-1333-craft-parse-schema-and-agent-task-prompts`

Add required `highlights` to the shared craft-base / simple-resume-parse response schema, and update those two `agent_task` seed prompts so Highlights is required and ordered immediately above Experience (field inventory / segment instructions stay consistent with the schema). Does **not** own structure-catalog membership, default order, or normalize mint/coerce (sibling AST-1332). Does **not** change draft_job_resume nested envelope work.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Insert `"highlights": {"type": "str", "required": True}` into `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` immediately before `experience` (shared by `craft_resume_base` and `simple_resume_parse` via object identity). | utils |
| `data/admin/agent_task.json` | Update current `craft_resume_base` and `simple_resume_parse` `cache_prompt` text: segment count / field inventory / segment instructions require Highlights above Experience. | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Keep byte-identical with `data/admin/agent_task.json` after the prompt edits (`cp` after catalog edit). | docs |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `RESUME_STRUCTURE_REQUIRED_SECTION_IDS` / DEFAULT / normalize coerce | AST-1332 (already on epic line) |
| `BUILD_CONFIG["artifact_shapes"]["resume_content"]` | out of scope — not the craft/parse hop schema |
| `draft_job_resume` / nested envelope / deviations | AST-1268 family — do not touch |
| `src/core/candidate.py` / `src/core/builder.py` / `src/core/agent.py` | unchanged — persistence already copies enabled section strings; validation already fails missing `required` keys |
| `tests/`, `docs/test-bible/**` | Betty |

## Traceability (this child's AC only)

Parent ACs 1–3 (catalog / order / coerce) and AC 6 (HTML emit) are AST-1332. This ticket owns parent ACs 4–5 only.

| Child AC | Stage |
|----------|--------|
| 4 — craft-base / simple-resume-parse response schemas require `highlights` string; omitting the key fails schema validation | 1 |
| 5 — `craft_resume_base` and `simple_resume_parse` agent_task prompts state Highlights is required and sits above Experience, consistent with schema field inventory / segment instructions | 2 |

## Stage 1: Shared craft/parse response schema — required `highlights`

**Done when:** `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` has a `highlights` entry `{"type": "str", "required": True}` whose dict-key order places it immediately before `experience`. `TASK_CONFIG["craft_resume_base"]["response_schema"]` and `TASK_CONFIG["simple_resume_parse"]["response_schema"]` are still the **same object** (`is` identity with `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`). Omitting `highlights` from a payload fails `_validate_schema_object_fields` / `_validate_response_schema` with `Missing required field 'highlights'` (empty string `""` still passes — key present). No `agent_task.json` edits in this stage.

1. In `src/utils/config.py`, in `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`, insert this line **immediately before** the `"experience": _EXPERIENCE_JOB_ARRAY_FIELD` entry:

   ```python
   "highlights": {"type": "str", "required": True},
   ```

   Final key order in that dict must be exactly:

   `resume_structure`, `candidate_name`, `candidate_title`, `candidate_contact_detail`, `candidate_tagline`, `professional_summary`, `core_competencies`, `highlights`, `experience`, `prior_experience`, `education_certifications`, `technical_skills`.

2. Do **not** edit `_CRAFT_RESUME_NORMALIZE_TASK_KEYS`, `TASK_CONFIG` wrappers, `BUILD_CONFIG["artifact_shapes"]`, resume-structure catalog tuples, `candidate.py`, or any other `TASK_CONFIG` hop schemas.

3. Do **not** edit `data/admin/agent_task.json` in this stage.

⚠️ **Decision:** One shared schema object stays the single hop contract for both task keys (AST-1037). Empty string is valid when the source has no highlight material — `required: True` means the key must be present, not non-empty (same as other required str fields under `_validate_schema_object_fields`).

⚠️ **Decision:** Do not mirror `highlights` into `BUILD_CONFIG["artifact_shapes"]["resume_content"]` on this ticket — parent AC names craft-base / simple-resume-parse response schemas only.

## Stage 2: agent_task seed prompts — Highlights required above Experience

**Done when:** Current `craft_resume_base` and `simple_resume_parse` rows in `data/admin/agent_task.json` instruct that Highlights is a required keyed segment / field sitting immediately above Experience, and their inventory language matches Stage 1's schema (including segment count / required-field list). `craft_resume_base` QUALITY CHECKLIST no longer requires non-empty string values for every key (step 1d). `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to `data/admin/agent_task.json`. No other `task_key` rows change. No `src/` edits in this stage.

1. In `data/admin/agent_task.json`, edit **only** the object with `"task_key": "craft_resume_base"` and `"current": 1`. Change **`cache_prompt` only** (leave `user_prompt`, `nocache_prompt`, agent ids, grouping, `run_next`, uuids, `updated_at` untouched):

   a. In the opening paragraph, change `exactly 9 keyed segments` → `exactly 10 keyed segments`.

   b. In `## SEGMENT INSTRUCTIONS`, insert a new `### highlights` block **immediately before** `### experience`, with this **exact** body:

   ```
   ### highlights
   Required body section. Place Highlights **immediately above Experience** in the resume narrative order (same placement as the product catalog).

   Extract highlight / career-highlight bullets from the resume (and LinkedIn only when they add framing without inventing facts). Present as a single string — one highlight per line, plain text.

   Rules:
   - Resume is source of truth for facts and metrics
   - Do NOT invent highlights that appear in neither resume nor LinkedIn
   - IF the sources have no highlight material, return an empty string (key still required)
   ```

   c. Keep other segment bodies and FORMATTING RULES unchanged. Keep the new `### highlights` block adjacent to `### experience` with no other `###` between them.

   d. In the same `cache_prompt` **QUALITY CHECKLIST**, replace the blanket first bullet so empty `highlights` is allowed (schema + `### highlights` already allow `""`). Change this line:

   ```
   - Every key present with a non-empty string value
   ```

   to **exactly**:

   ```
   - Every required key present (string values may be empty when source material is absent — especially `highlights`)
   ```

   Leave the remaining checklist bullets unchanged.

2. In `data/admin/agent_task.json`, edit **only** the object with `"task_key": "simple_resume_parse"` and `"current": 1`. Change **`cache_prompt` only**:

   a. Replace the Field inventory block with **exactly**:

   ```
   Field inventory (match the schema):
   - required: `resume_structure`, `candidate_name`, `candidate_title`, `candidate_contact_detail`, `professional_summary`, `core_competencies`, `highlights`, `experience` (job array)
   - optional: `candidate_tagline`, `prior_experience`, `education_certifications`, `technical_skills`
   ```

   b. In `### resume_structure`, update the parenthetical known-id list so `highlights` appears **immediately before** `experience`. The list must be:

   ``(`candidate_name`, `candidate_title`, `candidate_tagline`, `candidate_contact_detail`, `professional_summary`, `core_competencies`, `highlights`, `experience`, `prior_experience`, `education_certifications`, `technical_skills`)``

   c. Insert a new `### highlights` block **immediately before** `### experience`, with this **exact** body:

   ```
   ### highlights
   Required. Career-highlight / highlights bullets from the paste only — one highlight per line in a single string.

   - Place Highlights **immediately above Experience** in narrative order (product catalog rule).
   - Preserve `__` / `~~` digraphs when present.
   - Do **not** invent highlights. Empty string when the paste has no highlight material (key still required — do not omit).
   ```

3. After both prompt edits, sync the UAT fixture twin so the two files stay byte-identical:

   ```bash
   cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
   cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
   ```

4. Do **not** change `user_prompt` / `nocache_prompt` / `system_prompt` on either row. Do **not** edit other task keys. Do **not** touch `data/admin/agent.json`.

⚠️ **Decision:** Prompt text is the durable Archie catalog (`astral.seed.agent-tables-in-repo-json` / `astral.seed.archie-catalog-wins`). Live Manage Tasks DB edits alone are not lasting — commit the JSON.

⚠️ **Decision:** Fixture sync via whole-file `cp` (AST-786 / AST-834 pattern) so catalog and expected twin cannot drift on this edit. Surgical dual-edit is unnecessary when the twin must match the full catalog.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Revisions

Revision 1 — 2026-08-12
Driven by: Joan `[plan-discuss] round=1` fix-now — `craft_resume_base` QUALITY CHECKLIST contradicts empty `highlights` (“Every key present with a non-empty string value” vs Stage 1 / `### highlights` allowing `""`).
Changes: Stage 2 step 1 now has explicit step **1d** replacing that checklist bullet with required-key + empty-string language so the model is not told to invent highlights or omit the key.

## Joan validate

[plan-discuss] round=1 concern
[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1333
**Overall:** REVISE
**Publish ref:** `sub/AST-1326/AST-1333-craft-parse-schema-and-agent-task-prompts` @ `d11875f794f1cb05802d64ddbc4ddeec9012f2fc`

### Traceability
AC4→S1 (`_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` shared object); AC5→S2 (`craft_resume_base` + `simple_resume_parse` `cache_prompt` + fixture `cp`). Parent AC1–3 / AC6 → AST-1332 (explicitly out of scope).

### Findings

#### fix-now — `craft_resume_base` QUALITY CHECKLIST contradicts empty `highlights`
- **Location:** Stage 2 §1 (`craft_resume_base` `cache_prompt`), existing `QUALITY CHECKLIST`
- **Finding:** Live prompt ends with “Every key present with a **non-empty string value**.” Stage 1 ⚠️ Decision and the new `### highlights` body both allow `""` when sources have no highlight material (`required: True` = key present; `_validate_schema_object_fields` only rejects `val is None`). Leaving the checklist unchanged tells the model to violate AC5/schema for a valid empty highlights response.
- **Recommendation:** In Stage 2 step 1, amend QUALITY CHECKLIST (per step 1c “except as needed”): e.g. replace the blanket non-empty rule with “every **required** key present” and explicitly allow `highlights` (and other optional-empty fields as today) to be `""` when source material is absent. Do not ship the `### highlights` block without this reconciliation.

#### discuss — Assignee not Joan at fetch time
- **Location:** Linear ticket state
- **Finding:** Status `Plan Ready` but assignee is Katherine, not Joan — `validate-plan` §1 expects Chuckles to assign Joan before spawn.
- **Recommendation:** Chuckles procedural fix only; does not block plan content once checklist is patched.

#### acceptable — No explicit Self-assessment line
- **Location:** `## Estimate`
- **Finding:** Same hygiene gap as sibling AST-1332; footprint is small and ⚠️ Decision blocks are specific.
- **Recommendation:** Optional `Single-Component / high conf / low risk` before build.

**In-session (R1–R4, not printed):** Considered statutes conform for cited scope — `astral.config.config-source-of-truth`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`, `pattern.config.config-block`. `astral.agent.do-task-delegation` excluded (no `src/core/**` in Files Changed). Layer table respects import discipline (utils + seed JSON + fixture twin only). Sibling boundary vs AST-1332 is explicit and correct. Plan Discuss round count after this pass: would be 1.

context_tokens≈52000

## Joan validate (round 2 — APPROVED)

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1333
**Overall:** APPROVED
**Publish ref:** `sub/AST-1326/AST-1333-craft-parse-schema-and-agent-task-prompts` @ `df4946127a6f449fbe8db704967b657b7d8806f4`

### Traceability
AC4→S1 (`_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` shared object); AC5→S2 (`craft_resume_base` + `simple_resume_parse` `cache_prompt` + fixture `cp`, including step 1d checklist fix). Parent AC1–3 / AC6 → AST-1332 (explicitly out of scope).

### Findings

#### acceptable — No explicit Self-assessment line
- **Location:** `## Estimate`
- **Finding:** Still no `**Self-assessment:**` scope/conf/risk line.
- **Recommendation:** Optional hygiene before build; not blocking given narrow footprint and explicit ⚠️ Decision / `## Revisions` blocks.

**Round 1 resolution:** Prior `fix-now` (QUALITY CHECKLIST vs empty `highlights`) is addressed by Stage 2 step **1d** — replaces the blanket non-empty bullet with required-key + empty-string language consistent with Stage 1 ⚠️ Decision and `### highlights` bodies. Assignee is Joan at fetch time (procedural gap closed).

**In-session (R1–R4, not printed):** Cited statutes/patterns conform (`astral.config.config-source-of-truth`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`, `pattern.config.config-block`). `astral.agent.do-task-delegation` excluded (no `src/core/**`). Layer/import discipline holds. Sibling boundary vs AST-1332 explicit. Plan Discuss completed rounds: 1 (concern + reply).

context_tokens≈58000
