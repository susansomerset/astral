# Judith craft-base: experience job array (Parse resume json output is incomplete)

**Linear:** [AST-996](https://linear.app/astralcareermatch/issue/AST-996/judith-craft-base-experience-job-array-parse-resume-json-output-is)
**Parent:** [AST-994](https://linear.app/astralcareermatch/issue/AST-994/parse-resume-json-output-is-incomplete) — Parse resume json output is incomplete
**Publish ref:** `origin/sub/AST-994/AST-996-judith-craft-base-experience-job-array`

Updates Judith’s `craft_resume_base` response contract and prompt so **Experience** is an ordered array of jobs (company, title, dates, location, one accomplishments block) with no fabrication or rewrite of facts. Owns the parse JSON shape on session parse and candidate craft-base paths. Does **not** own HTML emit (AST-998) or job-tailored highlight rewriting (AST-997).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add shared experience-job item schema; set `TASK_CONFIG["craft_resume_base"]["response_schema"]["experience"]` and `BUILD_CONFIG["artifact_shapes"]["resume_content"]["experience"]` to list-of-jobs; mark `DATA_SHAPES` base_resume_structure `experience` as structured list | utils |
| `src/core/candidate.py` | Preserve experience job arrays through flatten / split / filter / token helpers; Style D debug detail for recorded jobs on session + candidate craft-base success paths | core |
| `data/admin/agent_task.json` | Rewrite `craft_resume_base` `cache_prompt` **### experience** segment for job-array contract (facts-faithful; no prose role blocks) | repo admin JSON |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Round-trip non-string section values as JSON text for load / Generate / Save so Base Resume Content does not stringify-corrupt the job array | ui |

**Out of scope (do not touch):** `src/core/builder.py` / HTML emit (AST-998); `draft_job_resume` / `finalize_job_resume` / job-tailored hops (AST-997); `prior_experience` remains `str`; AST-993 chrome; `tests/`, bible.

## Stage 1: Config — experience job-array contract

**Done when:** `TASK_CONFIG["craft_resume_base"]["response_schema"]["experience"]` is a required `list` with `items_schema` for company/title/dates/location/accomplishments; `stringify_response_schema("craft_resume_base")` shows that array shape; `BUILD_CONFIG["artifact_shapes"]["resume_content"]["experience"]` matches; no other task schemas changed.

1. In `src/utils/config.py`, near the other shared schema helpers (`_CRAFT_RUBRIC_*`), add:
   ```python
   _EXPERIENCE_JOB_ITEM_SCHEMA: Dict[str, Dict[str, Any]] = {
       "company": {"type": "str", "required": True},
       "title": {"type": "str", "required": True},
       "dates": {"type": "str", "required": True},
       "location": {"type": "str", "required": True},
       "accomplishments": {"type": "str", "required": True},
   }
   _EXPERIENCE_JOB_ARRAY_FIELD: Dict[str, Any] = {
       "type": "list",
       "required": True,
       "items_schema": _EXPERIENCE_JOB_ITEM_SCHEMA,
   }
   ```
   ⚠️ **Decision:** `location` is required as `str`; when the source has no location for a role, Judith returns `""`. Dates stay a single freeform string (e.g. `2023`, `Jan 2023 to Dec 2023`) — no start/end split. Field name `accomplishments` (not `highlights`) for craft-base; AST-997 may introduce tailored highlights later on the same job-object spine.
2. In `TASK_CONFIG["craft_resume_base"]["response_schema"]`, replace `"experience": {"type": "str", "required": True}` with `"experience": _EXPERIENCE_JOB_ARRAY_FIELD` (same object reference, not a duplicated literal).
3. In `BUILD_CONFIG["artifact_shapes"]["resume_content"]`, set `"experience": _EXPERIENCE_JOB_ARRAY_FIELD` the same way (single source for the wire shape).
4. In `DATA_SHAPES["candidates"]["detail"]["base_resume_structure"]`, change the experience entry from `"type": "str"` to `"type": "experience_jobs"` (label stays `"Experience"`). ArtifactEditor Stage 4 keys off this type for JSON round-trip.
5. Do **not** change `prior_experience`, `finalize_job_resume`, `draft_job_resume`, or `BUILD_CONFIG["supported_sections"]["experience"]["body_kind"]` (HTML sibling owns render recognition).
6. Confirm `_schema_to_example` / `stringify_response_schema` already recurse `items_schema` for lists (they do) — no validator changes required for the new shape; `_coerce_schema_str_fields_from_list` only coerces fields with `type == "str"`, so once experience is `list` it will not be flattened to a newline string.

## Stage 2: Preserve job arrays through craft-base split/filter paths

**Done when:** `split_craft_resume_base_payload` puts a job list on `content["experience"]`; `filter_base_resume_to_structure` / `filter_content_to_resume_structure` / `format_base_resume_for_token` keep that list (no `str(list)`); `_flatten_craft_resume_section_strings` does not coerce a list-of-job-dicts into a prose string.

1. In `src/core/candidate.py`, add a small helper (near the craft flatten helpers):
   ```python
   def _is_experience_job_array(val: Any) -> bool:
       return isinstance(val, list) and all(isinstance(item, dict) for item in val)
   ```
2. Update `_coerce_resume_section_string`: if `_is_experience_job_array(val)`, return `None` (do not join dicts into prose). List-of-strings coercion for other sections stays as today.
3. Update `_flatten_craft_resume_section_strings` `_promote`: if `sid == "experience"` and `_is_experience_job_array(val)` and experience is not already a job array on the payload, set `payload["experience"] = val` and return (do not require string coerce). If top-level `experience` is already a job array, leave it.
4. Update `split_craft_resume_base_payload`:
   - Change `content` typing to `Dict[str, Any]`.
   - For each enabled key in `parsed`: if `key == "experience"` and `_is_experience_job_array(val)`, set `content[key] = val`; elif `isinstance(val, str)`, set `content[key] = val` (existing). Do not drop experience when it is a list.
   ⚠️ **Decision:** Legacy stored string `experience` remains readable as a string until re-parse; this ticket does not migrate old blobs. New craft-base success always emits the job array.
5. Update `filter_base_resume_to_structure`: replace `{k: str(v) for ...}` with: keep job arrays as-is for `experience`; for other keys keep `str(v)` only when value is not a `dict`/`list`, else `json.dumps(v)` is **not** used here — non-experience structured values are out of scope; only experience list + string scalars are expected.
   ```python
   out = {}
   for k, v in content.items():
       if k not in section_ids:
           continue
       if k == "experience" and _is_experience_job_array(v):
           out[k] = v
       elif isinstance(v, str):
           out[k] = v
       # else: drop unexpected shapes (do not str()-corrupt)
   return out
   ```
6. Update `filter_content_to_resume_structure`: when `key == "experience"` and `_is_experience_job_array(val)` and the list is non-empty, copy the list into `out`; keep existing non-empty string handling for other keys. Widen `out` type to `Dict[str, Any]`.
7. `format_base_resume_for_token` already `json.dumps`s the filtered payload — once filter preserves the list, the token JSON carries the job array. No further change unless the filter call path regresses.
8. Do **not** edit `normalize_draft_job_resume_agent_payload` / `validate_draft_job_resume_payload` (AST-997).

## Stage 3: Judith prompt — experience as job array

**Done when:** `data/admin/agent_task.json` row `craft_resume_base` `cache_prompt` **### experience** instructs an ordered JSON array of job objects with the five fields above, facts-faithful rules, and freeform dates; `{$RESPONSE_SCHEMA}` remains the schema insertion point (no hardcoded duplicate schema block).

1. In `data/admin/agent_task.json`, find the `craft_resume_base` row. Replace the **### experience** segment (currently prose “COMPANY NAME / Title | dates | Location” blocks separated by blank lines) with instructions that:
   - `experience` is an **ordered JSON array** of job objects (resume order).
   - Each object has exactly: `company`, `title`, `dates`, `location`, `accomplishments` (all strings).
   - `dates` is freeform as in the source (year-only or ranges OK).
   - `location` is the source location string, or `""` if absent.
   - `accomplishments` is **one** text block for that role (paragraph and/or bullets as in the source), not rewritten or expanded with invented claims.
   - Resume is source of truth for company / title / dates / location / metrics; do not invent employers, titles, dates, locations, or accomplishments; do not paraphrase factual metadata to “improve” it.
   - LinkedIn/backstory may enrich narrative inside `accomplishments` only when grounded in resume facts (same rules as today’s synthesis guidance), never new employers/titles/dates/locations.
2. Leave other segment instructions (`candidate_name`, `professional_summary`, `prior_experience`, etc.) unchanged unless a sentence still says experience is a single prose string — fix only those contradictory lines.
3. Do **not** invent a second parse agent or session-only prompt; session parse continues to call `do_task("craft_resume_base")`.
4. Repo JSON applies at bootstrap (`apply_repo_admin_json_at_startup`); no Manage Tasks UI change in this ticket. If local DB has diverged, note in the Linear stage comment that Railway/startup apply picks up the file — do not hand-edit production DB in this plan.

## Stage 4: Base Resume Content JSON round-trip (no corrupt Save)

**Done when:** ArtifactEditor load / Generate / Save for `craft_resume_base` fixed fields shows experience as pretty-printed JSON and saves it back as a parsed array (not `"[object Object]"` / stringified garbage).

1. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, add helpers:
   ```ts
   function sectionValueToTabContent(val: unknown): string {
     if (typeof val === "string") return val
     if (val == null) return ""
     return JSON.stringify(val, null, 2)
   }
   function tabContentToSectionValue(key: string, content: string, fieldType?: string): unknown {
     if (fieldType === "experience_jobs") {
       const t = content.trim()
       if (!t) return []
       return JSON.parse(t)  // let Save catch path surface parse errors via toast
     }
     return content
   }
   ```
2. Wire `sectionValueToTabContent` into `mapFixedFieldsFromRaw` and the Generate success `fixedFields.map` path (replace `String(...)`).
3. Wire `tabContentToSectionValue` into `buildPayload` for fixed-fields mode: look up each field’s `type` from `fixedFields` / shapes (experience → `experience_jobs`). Widen payload typing from `Record<string, string>` to `Record<string, unknown>`.
4. On Save, if `JSON.parse` throws for experience, show a toast (`Experience must be valid JSON`) and abort the request — do not PUT a broken string.
5. Do **not** redesign the tab into a structured job editor; JSON textarea is sufficient for observability and non-destructive Save.

## Stage 5: Style D debug for experience jobs on craft-base parse hops

**Done when:** With `debug=True`, successful `run_session_resume_parse` and successful `craft_resume_base` path inside `run_candidate_artifact_generation` (and `parse_candidate_resume` when debug is threaded) emit Style D detail lines listing each recorded job’s company/title/dates/location plus truncated accomplishments — not only pass/fail.

1. In `src/core/candidate.py`, add helper `_debug_experience_jobs(logger, content_or_parsed)` that:
   - Reads `experience` from a dict (prefer split `content`, else `parsed`).
   - If job array: for each index `i`, `logger.debug_detail(f"experience[{i}] company=... title=... dates=... location=...")` and one detail line for accomplishments via `truncate_debug_content` when long.
   - If missing/legacy string: one detail line noting shape (`experience_shape=str|missing|other`).
2. Call it after successful split in `run_session_resume_parse` (under the existing `debug_index` success header; keep or trim the full `debug_detail_block(json.dumps(parsed))` — prefer job-focused detail + optional truncated payload, do not remove the index header).
3. Call it on successful `craft_resume_base` persist in `run_candidate_artifact_generation` when `debug=True` (same Style D helpers; gate on `debug` only — §1.5.1).
4. Thread `debug: bool = False` onto `parse_candidate_resume` if it lacks it; when `debug=True`, same job detail after split. Callers that omit `debug` stay quiet.
5. Do **not** add tailor-hop debug here (AST-997).

## Self-Assessment

**Scope:** `Single-Component` — config contract + craft-base preserve/split path + Judith prompt row + thin ArtifactEditor JSON round-trip; no builder HTML and no job-tailored hops.

**Conf:** `high` — schema already supports nested `list`/`items_schema`; the failure modes are known (`str(list)` in filter/split, `_coerce_schema_str_fields_from_list` only on `str` fields, prompt still teaching prose blocks).

**Risk:** `Medium` — wrong flatten/filter would drop or stringify jobs and break session parse observability and Base Resume Content Save; HTML still uses `_format_experience_value` JSON dump until AST-998, so interim print is ugly but not empty.

## Code rules check

- §1.3 DRY: one `_EXPERIENCE_JOB_*` config object shared by TASK_CONFIG and artifact_shapes; one preserve helper used by split/filter.
- §2.1: schema/contract literals only in `config.py`; prompt text in repo `agent_task.json` (existing pattern).
- §2.4: no new batch claim pattern; session ledger unchanged.
- §2.6: no state machine changes.
- §3.3: ui → core only; core edits stay in candidate; no ui→data.
- §1.5.1: debug Style D only when `debug=True`.
- §3.6: no repo-root `artifacts/` directory.
