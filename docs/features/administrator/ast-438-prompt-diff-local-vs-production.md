# AST-438 — Prompt diff (local vs production)
Generated: 2026-05-18T18:41:21Z
Prod: astral.up.railway.app
## Executive summary
- Tasks compared: 11
- Agent tasks with any diff: evaluate_jd, grade_do, grade_get, grade_like, qualify_job_listings
- Agents with any diff: college_intern_ruth, job_analyst_grace

## Per-task diffs


### craft_company_prefilter


### craft_do_rubric


### craft_get_rubric


### craft_jobdesc_rubric


### craft_joblist_rubric


### craft_like_rubric


### evaluate_jd

- `user_prompt`: **CONTENT_DIFF** // Done

### grade_do

- `cache_prompt`: **CONTENT_DIFF** // Done

### grade_get

- `user_prompt`: **CONTENT_DIFF** // Done
- `cache_prompt`: **CONTENT_DIFF** // Done

### grade_like

- `user_prompt`: **CONTENT_DIFF** // Done
- `cache_prompt`: **CONTENT_DIFF** // Done

### qualify_job_listings

- `cache_prompt`: **CONTENT_DIFF** // Done

## Per-agent diffs

### ats_expert_atlas


### college_intern_ruth

- `content`: **CONTENT_DIFF** // Done

### job_analyst_grace

- `content`: **CONTENT_DIFF** // Done

### principal_recruiter_estelle


## Follow-ups (out of scope)
- **AST-373** — prompt export/import UI (future sync decision).
- **AST-381** — repo-tracked DB snapshots (longer-term alignment).
