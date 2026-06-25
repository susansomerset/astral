# AST-607 — UAT: BASE_RESUME token must inject JSON not markdown

<!-- linear-archive: AST-607 archived 2026-06-23 -->

## Linear archive (AST-607)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-607/uat-base-resume-token-must-inject-json-not-markdown  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-592 — draft_job_resume dispatch job failed  
**Blocked by / blocks / related:** parent: AST-592

### Description

## What failed

After AST-604 alias fix, Susan retested `draft_job_resume` and reports the hop still misaligns section keys because **base resume content** is injected into the agent prompt as **markdown prose** instead of the **JSON object** whose keys must match the candidate section catalog exactly.

Susan: *"You're parsing the base resume content into markdown instead of rendering it as actual JSON for the agent. It needs to be the JSON structure so that the keys can match exactly."*

## Expected

`{$BASE_RESUME}` (existing token — **no** new `BASE_RESUME_JSON` shim) resolves to `json.dumps` of `artifacts.base_resume` as a **section-id-keyed JSON object** so the model sees the same keys it must echo in `agent_payload` (e.g. `candidate_contact_detail`, not markdown `###` headings).

## Repro

1. Local `dev` with AST-592 + AST-604 fixes; candidate `somerset` with `artifacts.base_resume` populated.
2. Manual **Run** on `draft_job_resume` (or Susan's batch).
3. Inspect resolved prompt / debug logs for `{$BASE_RESUME}` substitution — content appears as markdown sections instead of JSON with catalog section ids as keys.
4. Model may return keys that don't match catalog (e.g. `candidate_contact` vs `candidate_contact_detail`) because the input shape did not show exact JSON keys.

## Parent AC (quoted inline)

> `TASK_CONFIG` for `draft_job_resume` no longer requires `grades` or other consult-only graded fields; validation accepts payloads with only candidate-catalog section keys (all optional per Susan); unknown section keys fail with an explicit error.

> Re-running dispatch batch `draft_job_resume-80308ccb-087e-4100-af38-937ea9c75e01` (or an equivalent manual **Run** on `draft_job_resume` for the same job with the same prompt) succeeds when the model returns resume-section JSON like the payload in the original brief — no `Missing required field 'grades'` error.

## Boundaries

* This bug does **not** change: Manage Tasks prompt text (**AST-313**), consult-path graded tasks, or add a new prompt token name.
* Does **not** change `RESUME_SECTION_CATALOG` line format unless required for this fix.
* Does **not** reopen AST-604 alias normalization (keep; complements JSON input).

### Comments

#### betty — 2026-06-12T00:48:45.086Z
## [fix-uat-qa] tests updated

**Triage:** Dev commit `3071187f` already adds targeted component tests for `format_base_resume_for_token` and `{$BASE_RESUME}` JSON serialization; bible §7.13zv lacked an **AST-607** manifest row.
**Bible:** §7.13zv — added **AST-607** child row
**Tests:** none added by QA (covered in dev commit: `tests/component/core/test_candidate.py::TestAst607BaseResumeToken`, `tests/component/utils/test_config.py::TestResolveTokens::test_base_resume_token_emits_section_json_not_markdown`)
**Publish ref:** `origin/sub/AST-592/ast-607-base-resume-token-must-inject-json-not-markdown` @ `5d83e1cc`

#### ada — 2026-06-12T00:46:40.795Z
## [fix-uat-dev] report

**Summary:** `{$BASE_RESUME}` was routed through `value_to_str`, which renders legacy `{label, content}` arrays as markdown `###` sections. Added `format_base_resume_for_token` so the token always emits section-id-keyed JSON (dict passthrough via `filter_base_resume_to_structure`; legacy arrays mapped by structure title → section id).

**Publish ref:** `origin/sub/AST-592/ast-607-base-resume-token-must-inject-json-not-markdown` @ `3071187f`

**Files:**
- `src/core/candidate.py` — `format_base_resume_for_token`
- `src/utils/config.py` — `BASE_RESUME` `serialize: resume_sections_json` in `resolve_tokens`
- `tests/component/core/test_candidate.py` — AST-607 unit tests
- `tests/component/utils/test_config.py` — `resolve_tokens` integration test

**Verification:** `pytest tests/component/core/test_candidate.py::TestAst607BaseResumeToken tests/component/utils/test_config.py::TestResolveTokens::test_base_resume_token_emits_section_json_not_markdown -q` → 3 passed

**Open questions:** none

---

_Implementation detail may live in git history on `origin/dev`._
