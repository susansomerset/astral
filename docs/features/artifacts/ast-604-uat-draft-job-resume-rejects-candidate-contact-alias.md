# AST-604 — UAT: draft_job_resume rejects candidate_contact alias

<!-- linear-archive: AST-604 archived 2026-06-23 -->

## Linear archive (AST-604)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-604/uat-draft-job-resume-rejects-candidate-contact-alias  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-592 — draft_job_resume dispatch job failed  
**Blocked by / blocks / related:** parent: AST-592

### Description

## What failed

Manual **Run** on `draft_job_resume` for candidate `somerset` completes the LLM call (~87s) then fails validation:

```
ERROR src.core.agent: do_task validation failed. task_key='draft_job_resume' error=Unknown resume section key 'candidate_contact' (not in candidate catalog: ['candidate_contact_detail', 'candidate_name', ...])
```

The model returned `candidate_contact` but the candidate catalog uses `candidate_contact_detail`.

## Expected

`draft_job_resume` accepts the model's resume-section JSON when keys are valid catalog sections or common aliases for catalog ids (e.g. `candidate_contact` → `candidate_contact_detail`). Hop succeeds and advances the chain when content is otherwise valid.

## Repro

1. Local `dev` with AST-592 fix landed; restart app.
2. Candidate `somerset` with enabled sections including `candidate_contact_detail`.
3. Manual **Run** on `draft_job_resume` for a job (or re-run Susan's batch).
4. Model returns `candidate_contact` in `agent_payload` → hop fails with unknown section key.

## Parent AC (quoted inline)

> Re-running dispatch batch `draft_job_resume-80308ccb-087e-4100-af38-937ea9c75e01` (or an equivalent manual **Run** on `draft_job_resume` for the same job with the same prompt) succeeds when the model returns resume-section JSON like the payload in the original brief — no `Missing required field 'grades'` error.

> `TASK_CONFIG` for `draft_job_resume` no longer requires `grades` or other consult-only graded fields; validation accepts payloads with only candidate-catalog section keys (all optional per Susan); unknown section keys fail with an explicit error.

## Boundaries

* This bug does **not** change: Manage Tasks prompts (**AST-313**), consult-path graded tasks, or inventing acceptance of keys outside catalog/known aliases.
* Does **not** reopen AST-594 scope beyond alias normalization for legitimate section ids.

### Comments

#### betty — 2026-06-12T00:07:16.962Z
## [fix-uat-qa] tests updated

**Triage:** Dev fix adds `candidate_contact` → `candidate_contact_detail` alias normalization; existing `TestAst594DraftJobResumePayload` did not cover that path — added one targeted test.
**Bible:** §7.13zv (AST-604 row added during ftr merge)
**Tests:** `tests/component/core/test_candidate.py::TestAst594DraftJobResumePayload::test_normalize_renames_candidate_contact_alias`
**Publish ref:** `origin/sub/AST-592/ast-604-draft-job-resume-rejects-candidate-contact-alias` @ `a0e0ae41`

#### ada — 2026-06-12T00:05:55.291Z
## [fix-uat-dev] report

**Summary:** `draft_job_resume` validation rejected `candidate_contact` because the candidate catalog uses `candidate_contact_detail`. Added `_DRAFT_JOB_RESUME_SECTION_ALIASES` and `_apply_draft_job_resume_section_aliases()` in `normalize_draft_job_resume_agent_payload` so the alias is renamed to the catalog id before whitelist validation (canonical wins when both keys are present).

**Publish ref:** `origin/sub/AST-592/ast-604-draft-job-resume-rejects-candidate-contact-alias` @ `2333b255`

**Files:**
- `src/core/candidate.py`

**Verification:** `/Users/susan/chuckles/astral/.venv/bin/python` one-liner asserting `candidate_contact` → `candidate_contact_detail`; `pytest tests/component/core/test_candidate.py::TestAst594DraftJobResumePayload -q` (5 passed)

**Open questions:** none

---

_Implementation detail may live in git history on `origin/dev`._
