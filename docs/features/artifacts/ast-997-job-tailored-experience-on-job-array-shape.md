# Job-tailored experience on job-array shape (Parse resume json output is incomplete)

**Linear:** [AST-997](https://linear.app/astralcareermatch/issue/AST-997/job-tailored-experience-on-job-array-shape-parse-resume-json-output-is)
**Parent:** [AST-994](https://linear.app/astralcareermatch/issue/AST-994/parse-resume-json-output-is-incomplete) — Parse resume json output is incomplete
**Publish ref:** `origin/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape`
**Blocked by:** [AST-996](https://linear.app/astralcareermatch/issue/AST-996/judith-craft-base-experience-job-array-parse-resume-json-output-is) — Plan Approved job-array contract (`_EXPERIENCE_JOB_*`, paste-faithful craft-base). Plan against that contract; do **not** re-own craft-base parse or HTML emit.

Job-tailored resume hops (`draft_job_resume` / `finalize_job_resume`, plus advise/check prompt guidance) accept and emit the same Experience job-array shape as AST-996. Tailoring may change **`accomplishments`** for the target job; **company, title, dates, location** stay the base facts. Does **not** invent a new `highlights` field, rewrite craft-base, or touch builders (AST-998).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Point `TASK_CONFIG["finalize_job_resume"]["response_schema"]["experience"]` at the shared job-array field (required False); do not duplicate item keys — reuse AST-996 `_EXPERIENCE_JOB_ITEM_SCHEMA` / array field | utils |
| `src/core/candidate.py` | Stop string-coercing experience job arrays in draft normalize/validate; accept/validate job-array `experience`; pin factual metadata from base; Style D job detail helper reusable by tailor hops | core |
| `src/core/tracker.py` | Persist path keeps experience job arrays (`_resume_payload_body`, match gates, `_prepare_job_resume_content` typing) | core |
| `src/core/agent.py` | On successful `draft_job_resume` / `finalize_job_resume` when `debug=True`, emit Style D detail for recorded experience jobs (reuse candidate helper) | core |
| `data/admin/agent_task.json` | Update `draft_job_resume`, `finalize_job_resume`, `advise_job_resume`, `check_job_resume` prompts for job-array shape + tailor-accomplishments-only / flag metadata rewrites | repo admin JSON |

**Out of scope (do not touch):** `craft_resume_base` schema/prompt (AST-996); `src/core/builder.py` / HTML emit (AST-998); ArtifactEditor Base Resume Content UI; `contemplate_job` prose hop; `prior_experience` stays `str`; `tests/`, bible.

**Build precondition:** Before Stage 1 product commits, merge `origin/sub/AST-994/AST-996-judith-craft-base-experience-job-array` (or rolled-up `origin/ftr/…` once Chuckles merges 996) so `_EXPERIENCE_JOB_*` and `_is_experience_job_array` / filter preserve helpers exist. If those symbols are missing after merge, **stop** and comment on the parent — do not re-implement craft-base contract here.

## Contract reference (AST-996 — do not redefine)

Each experience job object:

| Field | Type | Tailor policy |
|-------|------|---------------|
| `company` | str | **Pinned** to base facts |
| `title` | str | **Pinned** to base facts |
| `dates` | str (freeform) | **Pinned** to base facts |
| `location` | str (`""` if absent) | **Pinned** to base facts |
| `accomplishments` | str (one block) | **May tailor** for the target job |

⚠️ **Decision:** No new `highlights` field. Parent “accomplishments/highlights” means the single accomplishments text block on the shared job object. Inventing a second body field would violate child boundary “do not invent new experience fields beyond the shared job-array contract.”

## Stage 1: Config — finalize schema uses shared job array

**Done when:** `finalize_job_resume` response_schema `experience` is a `list` with the same `items_schema` as craft-base (required False); `draft_job_resume` stays `resume_section_payload: True` with no static experience:str; no craft-base schema edits.

1. In `src/utils/config.py`, after AST-996’s `_EXPERIENCE_JOB_ARRAY_FIELD` (required True) exists, add or inline for finalize:
   ```python
   _EXPERIENCE_JOB_ARRAY_FIELD_OPTIONAL: Dict[str, Any] = {
       "type": "list",
       "required": False,
       "items_schema": _EXPERIENCE_JOB_ITEM_SCHEMA,
   }
   ```
   ⚠️ **Decision:** Share `items_schema` object identity with craft-base; only `required` differs (finalize sections are optional).
2. Replace `TASK_CONFIG["finalize_job_resume"]["response_schema"]["experience"]` with `_EXPERIENCE_JOB_ARRAY_FIELD_OPTIONAL`.
3. Do **not** change `craft_resume_base`, `BUILD_CONFIG["artifact_shapes"]` (already job-array after AST-996), or other hop schemas that do not emit resume section bodies.

## Stage 2: Draft normalize/validate — accept job array; pin base facts

**Done when:** `normalize_draft_job_resume_agent_payload` no longer turns experience job arrays into prose strings; `validate_draft_job_resume_payload` accepts a non-empty job array (or empty/`""` skip); after successful draft validation, company/title/dates/location on each tailored job are restored from the matching base job when base experience is a job array.

1. In `src/core/candidate.py` `normalize_draft_job_resume_agent_payload`:
   - Before the loop that coerces `isinstance(val, (list, dict))` via `_coerce_resume_section_string`, skip when `key == "experience"` and `_is_experience_job_array(val)`.
   - Same skip when promoting nested content dict values for `experience`.
2. In `validate_draft_job_resume_payload`, for `key == "experience"`:
   - If `_is_experience_job_array(val)`: keep the list; optionally run a light per-item check that each item is a dict with string fields for the five keys (missing location → treat as `""` only if you normalize in place; do not invent other fields). Do **not** require `_coerce_resume_section_string`.
   - Elif `val` is a non-empty str: keep as legacy string (pre-996 base) — do not fail the hop solely for legacy shape.
   - Else if val is list/dict that is not a job array: return a clear error (`Section 'experience' must be a job array or prose string`).
3. Add `pin_experience_job_facts_from_base(payload: dict, candidate_data: dict) -> None` (mutates payload):
   - Read `base = (candidate_data.get("artifacts") or {}).get("base_resume")`; if `experience` on base is not a job array, return (nothing to pin).
   - If payload `experience` is not a job array, return.
   - **Match primarily on role identity**, never index-first:
     1. Build an ordered pool of unused base jobs (base array order).
     2. For each tailored job in tailored order, find the **first unused** base job whose `(company.strip().lower(), title.strip().lower())` equals the tailored job’s pair.
     3. On match: copy that base job’s `company`, `title`, `dates`, `location` onto the tailored job; leave tailored `accomplishments` unchanged; mark that base job used.
     4. If no `(company, title)` match: **do not pin** that tailored job (leave model metadata as returned). Do **not** fall back to same-index overwrite — equal lengths after reorder would attach the wrong role’s dates/location to another employer’s accomplishments.
   - Duplicate company+title stints: consume the next unused base match in base order (first unused with that key), so two Amazon/SPM tours still pin distinct base rows without index-aligning the whole array.
   ⚠️ **Decision (AC6 / Joan round=1):** Pin by `(company, title)` only. Index-first when `len` matches is forbidden — Judith may reorder roles while keeping count. Unmatched / garbled identity jobs stay unpinned for Grace (`check_job_resume`) rather than a wrong-base metadata overwrite.
4. Call `pin_experience_job_facts_from_base` on the inner payload at the end of successful `validate_draft_job_resume_payload` (after shape checks pass), so `do_task` returns the pinned payload downstream.
5. For `finalize_job_resume`: schema validation already runs in `do_task`. After schema success for `finalize_job_resume` only, call the same pin helper on the inner payload (from `agent.py` next to the draft validate block, or a tiny shared hook). Do **not** enable `resume_section_payload` on finalize unless required — prefer one explicit pin call for `task_key == "finalize_job_resume"`.

## Stage 3: Tracker persist — do not drop job arrays

**Done when:** `persist_job_artifact_from_parsed` / `save_job_artifact_resume_content` can store `experience` as a job array; match gates treat a non-empty job array as body content.

1. In `src/core/tracker.py`, change `_resume_payload_body` to return `Dict[str, Any]` and include:
   - string section values (as today), and
   - `experience` when `_is_experience_job_array(v)` (import/reuse `candidate_mod._is_experience_job_array` or a public alias `is_experience_job_array` if you prefer not to use a leading-underscore helper across modules — ⚠️ **Decision:** add public `is_experience_job_array = _is_experience_job_array` in `candidate.py` if tracker should not import a private name).
2. Update `parsed_matches_resume_content_shape` and `parsed_matches_job_resume_content`: a section counts as present when it is a non-empty str **or** (for `experience`) a non-empty job array.
3. Update `job_has_persisted_resume_body` the same way for stored `resume_content["experience"]`.
4. Widen `_prepare_job_resume_content` return type to `Dict[str, Any]`; rely on AST-996’s `filter_content_to_resume_structure` preserving job arrays. Contact snapshot logic stays string-only.
5. Do **not** change cover-letter persist paths.

## Stage 4: Prompts — tailor accomplishments only

**Done when:** Repo `agent_task.json` for the four hops below teaches the job-array wire shape and the tailor-vs-pin policy; bootstrap apply picks it up.

1. **`draft_job_resume` `user_prompt`:** After the existing “same JSON structure as the base resume” / “every claim must trace to base” rules, add an explicit Experience block:
   - `experience` is an ordered **array of job objects** with `company`, `title`, `dates`, `location`, `accomplishments`.
   - You may reframe/reorder/emphasize **`accomplishments`** text for the target role (still every claim must trace to the base resume — no invented metrics/employers).
   - **Do not** change `company`, `title`, `dates`, or `location` from the base resume for that role.
2. **`finalize_job_resume` `user_prompt`:** Same job-array output shape; when correcting Grace findings, restore factual metadata to base; accomplishments may stay tailored if Grace did not flag them as invented.
3. **`advise_job_resume` `user_prompt`:** In the resume-revision instruction list, tell Estelle to brief Judith on accomplishment emphasis/cuts/keyword weave **per role**, and to **forbid** rewriting company/title/dates/location.
4. **`check_job_resume` `user_prompt`:** Extend Grace’s checklist: flag any change to company/title/dates/location vs base; accomplishments may differ in wording/emphasis but must remain traceable (no new employers/metrics). Keep accuracy-only scope (no style critique).
5. Do **not** edit `craft_resume_base` prompts.

## Stage 5: Style D debug on tailor hops

**Done when:** With `debug=True`, successful `draft_job_resume` and `finalize_job_resume` emit Style D detail for each experience job (company/title/dates/location + truncated accomplishments), not only hop pass/fail.

1. Reuse AST-996’s `_debug_experience_jobs` (or extract to a shared name if draft path cannot see a session-only helper). If AST-996 landed the helper only beside session parse, move it to a module-level helper both tickets can call — still in `candidate.py`, no new module.
2. In `src/core/agent.py`, after successful validation for `draft_job_resume` and `finalize_job_resume` when `debug=True`, call that helper on the inner payload (under the existing hop `debug_index` from `_resume_hop_debug_index` — add detail lines, do not replace the hop header).
3. Gate all new lines on `debug=True` only (§1.5.1). Do not add tailor debug to advise/check/contemplate.

## Self-Assessment

**Scope:** `Single-Component` — finalize schema reuse + draft validate/pin + tracker persist + four hop prompts + debug detail; no craft-base ownership, no HTML builder.

**Conf:** `high` — AST-996 contract is Plan Approved; destroyers are known; pin match is now `(company, title)`-first with no index fallback (Joan round=1).

**Risk:** `Medium` — a missed coerce/persist path would flatten tailored experience back to prose or drop it from `job_data.artifacts.resume_content`, breaking the chain before AST-998 can render jobs.

## Code rules check

- §1.3 DRY: reuse AST-996 schema objects and `_is_experience_job_array` / debug helper; one pin function for draft + finalize.
- §2.1: no new hardcoded job field sets in core — config `items_schema` only.
- §2.4 / §2.6: no new batch claim or state machine.
- §3.3: core/utils/repo JSON only; no ui→data; no builder.
- §1.5.1: tailor debug Style D only when `debug=True`.
- §3.6: no repo-root `artifacts/` directory.

## Revisions

### Revision 1 — 2026-07-28
Driven by: Joan `[plan-discuss] round=1 concern` fix-now — Stage 2 pin match preferred same index when lengths equal, which corrupts role metadata after reorder.
Changes: `pin_experience_job_facts_from_base` now matches only on `(company, title)` (consume first unused base with that key); **no index-first / no index fallback**; unmatched jobs stay unpinned for Grace.

## Review (build stub)

**Publish ref:** `origin/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape`
**Plan path:** `docs/features/artifacts/ast-997-job-tailored-experience-on-job-array-shape.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–5 | (see tip) | finalize optional job-array schema, draft pin/validate, tracker persist, prompts, Style D tailor debug |

**Tip:** publish-ref tip after this stub append.

## Review (Radia — code-rubric.v1)

`[code-rubric] revision=1`

**Publish ref tip:** (see Linear / post-push SHA) on `origin/sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape`
**Baseline:** `origin/dev`
**Overall:** DISCUSS

### What’s solid
- Finalize reuses shared `_EXPERIENCE_JOB_ITEM_SCHEMA` via optional array field; draft normalize/validate keeps job arrays; pin by `(company, title)` only (no index fallback).
- Tracker persist/`_resume_section_has_body` keep non-empty job arrays; four hop prompts teach tailor-accomplishments-only.
- Style D `_debug_experience_jobs` on draft/finalize when `debug=True`; Betty `test`/`merge-tests` on test-tree only.

### Issues
**discuss (C4 stragglers):** Joan excluded debug/docs/engineer-test-tree/UI auth+placement/naming statutes that the tip brings in-scope via AST-996 merge + features/tests — all scored **conforms** (no product defect).

**advisory:** `agent.py` imports private `_debug_experience_jobs` (tracker correctly uses public `is_experience_job_array`).

### Recommended actions
No fix-now. Stragglers are process notes — resolve-child may proceed without product edits unless Ada wants a public debug-helper alias.

## Resolution

**Date:** 2026-07-28  
**Review tip:** `7f2720d6` (Radia `docs(AST-997): Radia review — findings`)  
**Overall:** DISCUSS → resolved for User Testing (no fix-now)

### fix-now
(none)

### discuss
C4 stragglers (Joan exclusions vs tip in-scope via AST-996 merge + features/tests) — accepted as process notes; all already **conforms**. No product change.

### advisory
1. Public `debug_experience_jobs` alias added beside `_debug_experience_jobs`; `agent.py` tailor hops import the public name (mirrors `is_experience_job_array` for tracker).
