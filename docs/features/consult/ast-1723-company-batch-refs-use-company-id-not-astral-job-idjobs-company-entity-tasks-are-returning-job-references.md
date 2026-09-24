# AST-1723 — Company batch refs use company_id not astral_job_id/jobs (company-entity tasks are returning job references)

<!-- linear-archive: AST-1723 archived 2026-09-24 -->

## Linear archive (AST-1723)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1723/company-batch-refs-use-company-id-not-astral-job-idjobs-company-entity  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / 5  
**Parent:** AST-1720 — company-entity tasks are returning job references  
**Blocked by / blocks / related:** parent: AST-1720

### Description

## What this implements

Stop company-entity batch encode/decode from stuffing `short_name` into `astral_job_id` and returning a `jobs`/`job` array. Company batches identify companies with `company_id` and a company-labeled result array. Does not change job-entity encode/decode that correctly uses `astral_job_id` / `jobs`.

## Scope

### Component scope

* `src/core/roster.py` — modified — company task ctx currently sets `batch_entities` with `astral_job_id: short_name` and reconciles `parsed["jobs"]` for prefilter / vet (and any sibling company batch using the same trick).
* `src/core/agent.py` — modified — encoded/batch decode maps position → `batch_entities[pos]["astral_job_id"]` and returns `{"jobs": ...}`; company entity_type needs a non-job shaped path.
* `src/core/consult.py` — modified — `_ensure_jobs_astral_ids` / flatten helpers assume job-shaped parsed payloads; company callers that share those helpers need company-aware reconcile (or stop sharing the job path).
* `src/core/dispatcher.py` — modified only if claim/log enrichment still prefers `astral_job_id` over `short_name` for company entities when surfacing refs (light touch if roster/agent already fix the payload).
* `src/utils/config.py` — modified — `TASK_CONFIG` company-task `response_schema` still requires `jobs` / job-shaped item keys; must accept company-labeled arrays and `company_id` so agent decode and schema validation agree.

### Technical scope

* `src/core/roster.py` — modified functions: the company `batch_entities` builders (prefilter single/batch, vet single/batch, and any other `astral_job_id: short_name` sites) plus decode/reconcile that reads `parsed["jobs"]` — switch to company id fields and a company-labeled result list so downstream persistence still keys by `short_name`.
* `src/core/agent.py` — modified function(s): the encoded/batch decode that always emits `{"jobs": result_jobs}` keyed by `astral_job_id` — branch (or parallel helper) for company entity_type so the returned array and id field are company-native.
* `src/core/consult.py` — modified helpers: `_ensure_jobs_astral_ids` and any flatten that assumes `jobs` + `astral_job_id` — either company variants or a shared entity-ref helper that does not force the job vocabulary onto company batches.
* `src/core/dispatcher.py` — modified only if a company-entity log/claim path still reads `ent.get("astral_job_id")` first when printing or returning refs; align preference to `short_name` for company.
* `src/utils/config.py` — modified entries: company-entity task `response_schema` (at least `prefilter_company` and any sibling company encode hop still keyed on `jobs`) — change required top-level array / item id fields to company-native (`companies` + `company_id` or equivalent), without altering job-entity schemas.

## Proposed change

- [X] `config.py` — `prefilter_company` response_schema → `companies` + `company_id`
- [X] `agent.py` — company decode path + grade/segment helpers
- [X] `roster.py` — company `batch_entities` + prefilter reconcile/`_flatten_prefilter_parsed`
- [X] `consult.py` — `_ensure_companies_company_ids` + company normalize branch
- [X] `dispatcher.py` — identity prefer `company_id` then `short_name`

## Notes for planning

Approved ancestor (archived): AST-702 — `docs/features/consult/ast-702-batch-prefilter-evaluate-phase.md` (normalize company rows to `{"astral_job_id": short_name, ...}` + decode via `parsed["jobs"]`). Susan approval note on AST-1720: **USE** `company_id` **for identifiers, not short_name.** Parent mini-epic: AST-1720.

### Comments

#### radia — 2026-09-20T05:02:38.631Z
[code-rubric] REVIEW (Commit: 0402c75e) qa-fix repro bar on sibling gap

Product company_id/companies contract matches plan. fix-now: board TESTS:REVISE bar not on tip — orphaned path spun coverage to sibling gap AST-1724 (in flight). discuss: no frozen Canon Scope on bug ticket. advisory: product diff covers Proposed change; job path gated.

#### joan — 2026-09-20T04:53:06.949Z
[board-joan]  CANON: OK

context_tokens≈28000

#### betty — 2026-09-20T04:53:01.303Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md (AST-702 / AST-880) — broken fixtures assert batch_entities.astral_job_id + parsed_response.jobs for company prefilter/vet; no coverage for company_id/companies to-be — need qa-fix revise + repro

#### hedy — 2026-09-20T04:51:57.037Z
`origin/sub/AST-1720/AST-1723-company-batch-refs-company-id` @ `be357f974c05a3761fd976333ad442e5182a50c3` · company_id companies contract

#### chuckles — 2026-09-20T04:50:31.898Z
Scope expanded: `src/utils/config.py` added to Component + Technical scope (company-task response_schema must accept company-labeled arrays / company_id). Re-spawning plan-fix.

#### hedy — 2026-09-20T04:49:49.657Z
[scope-gate] Proposed change needs `src/utils/config.py` — not in ## Scope.

Company-native decode must return `{"companies": [{company_id, grades, ...}, ...]}` (Susan's company_id / company-labeled array). After `_decode_payload`, `do_task` still runs `_validate_response_schema` against `TASK_CONFIG["prefilter_company"]["response_schema"]`, which today requires the top-level key `jobs`. Without updating that schema (and the item id field), a company-shaped return fails validation and the hop never lands.

Scope lines that don't cover it:
- Component/Technical scope list only `roster.py`, `agent.py`, `consult.py`, `dispatcher.py` — no `config.py`.

Why it can't stay inside those four: agent can branch decode to `companies`/`company_id`, but schema validation will reject the payload until `TASK_CONFIG["prefilter_company"]["response_schema"]` lists `companies` (items keyed by `company_id`) instead of `jobs`. Leaving schema as `jobs` keeps the job-labeled contract Susan rejected.

Ask: amend AST-1723 ## Scope to add `src/utils/config.py` — modified — `TASK_CONFIG["prefilter_company"]["response_schema"]` (and any other company encoded task still declaring `jobs` for this path). Small omission Chuckles can amend; then re-spawn plan-fix.

@chuckles

---

_Implementation detail may live in git history on `origin/dev`._
